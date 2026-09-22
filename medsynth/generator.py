import time
import logging
from typing import List, Optional, Union
import random
import concurrent.futures

from medsynth.patient import Patient
from medsynth.geography import Geography
from medsynth.demographics import Demographics
from medsynth.facilities import FacilityManager
from medsynth.health_record import Encounter, Condition, Observation
from medsynth.module import Module

def _mp_worker_chunk(args):
    gen, tasks = args
    results = []
    for index, seed in tasks:
        results.append(gen.generate_person(index, seed))
    return results

import uuid

class GeneratorOptions:
# ... Wait, I should just edit generate_person method directly.
    def __init__(self):
        self.population_size: int = 1
        self.seed: int = int(time.time() * 1000)
        self.reference_time: int = int(time.time() * 1000)
        self.end_time: int = self.reference_time
        self.timestep: int = 7 * 24 * 60 * 60 * 1000 
        self.target_state: Optional[Union[str, list]] = None
        self.target_lga: Optional[str] = None
        self.target_sex: Optional[str] = None
        self.min_age: Optional[int] = None
        self.max_age: Optional[int] = None
        self.thread_pool_size: int = 1

class Generator:
    """
    Core generator loop for MedSynth.
    Orchestrates the FSM modules across the timeline.
    """
    def __init__(self, options: GeneratorOptions):
        self.options = options
        self.geography = Geography()
        self.demographics = Demographics()
        self.facility_manager = FacilityManager()
        self.main_rng = random.Random(self.options.seed)
        self.modules: List[Module] = []

    def load_module(self, filepath: str):
        self.modules.append(Module.load_from_file(filepath))

    def generate_stream(self, workers: int = 1, start_index: int = 0):
        """Yields patients sequentially. If workers > 1, uses multiprocessing."""
        seeds = [self.main_rng.randint(0, 2**63 - 1) for _ in range(self.options.population_size)]
        
        if workers <= 1:
            for i in range(start_index, self.options.population_size):
                yield self.generate_person(i, seeds[i])
        else:
            chunk_size = 100
            chunks = []
            for i in range(start_index, self.options.population_size, chunk_size):
                tasks = [(j, seeds[j]) for j in range(i, min(i + chunk_size, self.options.population_size))]
                chunks.append((self, tasks))
            
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
                for results in executor.map(_mp_worker_chunk, chunks):
                    for patient in results:
                        yield patient

    def run(self) -> List[Patient]:
        """Legacy batch run method."""
        generated_population = []
        seeds = [self.main_rng.randint(0, 2**63 - 1) for _ in range(self.options.population_size)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.options.thread_pool_size) as executor:
            futures = [executor.submit(self.generate_person, i, seeds[i]) for i in range(self.options.population_size)]
            for future in concurrent.futures.as_completed(futures):
                generated_population.append(future.result())
            
        logging.info(f"Generated {len(generated_population)} patients.")
        return generated_population

    def generate_person(self, index: int, person_seed: int) -> Patient:
        patient = Patient(seed=person_seed)
        
        self.geography.assign_point(patient, self.options)
        self.demographics.assign_demographics(patient, self.options)
        
        primary_facility = self.facility_manager.assign_facility(patient)
        if primary_facility:
            patient.attributes["primary_facility_id"] = primary_facility.id
            patient.attributes["primary_facility_name"] = primary_facility.name
        
        self.update_patient(patient)
        
        # Post-process: Make all UUIDs deterministic based on the patient's seed
        uuid_rng = random.Random(person_seed)
        patient.attributes["id"] = str(uuid.UUID(int=uuid_rng.getrandbits(128)))
        
        for enc in patient.record.encounters:
            enc.id = str(uuid.UUID(int=uuid_rng.getrandbits(128)))
        for cond in patient.record.conditions:
            cond.id = str(uuid.UUID(int=uuid_rng.getrandbits(128)))
        for obs in patient.record.observations:
            obs.id = str(uuid.UUID(int=uuid_rng.getrandbits(128)))
        for proc in patient.record.procedures:
            proc.id = str(uuid.UUID(int=uuid_rng.getrandbits(128)))
        for med in patient.record.medications:
            med.id = str(uuid.UUID(int=uuid_rng.getrandbits(128)))
        for cp in patient.record.careplans:
            cp.id = str(uuid.UUID(int=uuid_rng.getrandbits(128)))
        for imm in patient.record.immunizations:
            imm.id = str(uuid.UUID(int=uuid_rng.getrandbits(128)))
        for alg in patient.record.allergies:
            alg.id = str(uuid.UUID(int=uuid_rng.getrandbits(128)))
            
        return patient

    def update_patient(self, patient: Patient):
        """
        Advances the patient's life sequentially by the timestep until the simulation end time
        or until the person dies.
        """
        patient.last_updated = patient.attributes.get("birthdate", self.options.reference_time)
        current_time = patient.last_updated
        
        while patient.is_alive(current_time) and current_time < self.options.end_time:
            for mod in self.modules:
                mod.process(patient, current_time)
            
            patient.last_updated = current_time
            current_time += self.options.timestep

