import copy
from typing import Any, Dict, Optional, List
from medsynth.patient import Patient
from medsynth.health_record import Encounter, Condition, Observation, Procedure, Medication, CarePlan, Allergy, Immunization
from medsynth.logic import Logic

def convert_time(quantity: float, unit: str) -> int:
    ms_per_unit = {
        "years": 31557600000,
        "months": 2629800000,
        "weeks": 604800000,
        "days": 86400000,
        "hours": 3600000,
        "minutes": 60000,
        "seconds": 1000
    }
    return int(quantity * ms_per_unit.get(unit, 86400000))

class Transition:
    def __init__(self, definition: Dict[str, Any]):
        self.definition = definition
        
    def follow(self, patient: Patient, time: int) -> Optional[str]:
        if "direct_transition" in self.definition:
            return self.definition["direct_transition"]
        elif "conditional_transition" in self.definition:
            for ct in self.definition["conditional_transition"]:
                if Logic(ct.get("condition", {})).test(patient, time):
                    return ct.get("transition")
            return self.definition.get("fallback_transition")
        elif "distributed_transition" in self.definition:
            r = patient.rand()
            cumulative = 0.0
            for dt in self.definition["distributed_transition"]:
                cumulative += dt.get("distribution", 0.0)
                if r <= cumulative:
                    return dt.get("transition")
            return self.definition.get("fallback_transition")
        elif "complex_transition" in self.definition:
            for ct in self.definition["complex_transition"]:
                if Logic(ct.get("condition", {})).test(patient, time):
                    r = patient.rand()
                    cumulative = 0.0
                    for dt in ct.get("distributions", []):
                        cumulative += dt.get("distribution", 0.0)
                        if r <= cumulative:
                            return dt.get("transition")
            return self.definition.get("fallback_transition")
        return None

class State:
    """Base class for GMF states."""
    def __init__(self, name: str, definition: Dict[str, Any]):
        self.name = name
        self.definition = definition
        self.transition_obj = Transition(definition)
        
        self.entered: Optional[int] = None
        self.exited: Optional[int] = None
        self.module_name: Optional[str] = None

    def clone(self) -> 'State':
        cloned = copy.copy(self)
        cloned.entered = None
        cloned.exited = None
        return cloned

    def transition(self, patient: Patient, time: int) -> Optional[str]:
        return self.transition_obj.follow(patient, time)

    def process(self, patient: Patient, time: int) -> bool:
        return True
        
    def run(self, patient: Patient, time: int, terminate_on_death: bool = True) -> bool:
        if terminate_on_death and not patient.is_alive(time):
            return False
            
        if self.entered is None:
            self.entered = time
            
        advance = self.process(patient, time)
        
        if advance:
            if hasattr(self, 'end_of_delay') and self.exited is not None:
                pass
            else:
                self.exited = time
        elif isinstance(self, Terminal):
            self.exited = time
            
        return advance

class Initial(State):
    def process(self, patient: Patient, time: int) -> bool:
        return True

class Simple(State):
    def process(self, patient: Patient, time: int) -> bool:
        return True

class Terminal(State):
    def process(self, patient: Patient, time: int) -> bool:
        return False

class Delay(State):
    def __init__(self, name: str, definition: Dict[str, Any]):
        super().__init__(name, definition)
        self.exact = definition.get("exact")
        self.range = definition.get("range")
        self.unit = definition.get("unit", "days")
        if self.exact:
            self.unit = self.exact.get("unit", self.unit)
        elif self.range:
            self.unit = self.range.get("unit", self.unit)

    def end_of_delay(self, patient: Patient, time: int) -> int:
        if self.exact:
            return time + convert_time(self.exact.get("quantity", 0), self.unit)
        elif self.range:
            low = self.range.get("low", 0)
            high = self.range.get("high", 0)
            val = low + (patient.rand() * (high - low))
            return time + convert_time(val, self.unit)
        return time

    def process(self, patient: Patient, time: int) -> bool:
        if not hasattr(self, 'target_exit_time') or self.target_exit_time is None:
            self.target_exit_time = self.end_of_delay(patient, time)
            
        if time >= self.target_exit_time and patient.is_alive(self.target_exit_time):
            self.exited = self.target_exit_time
            return True
        return False

    def clone(self) -> 'State':
        cloned = super().clone()
        cloned.target_exit_time = None
        return cloned

class Guard(State):
    def process(self, patient: Patient, time: int) -> bool:
        return Logic(self.definition.get("allow", {})).test(patient, time)

class SetAttribute(State):
    def process(self, patient: Patient, time: int) -> bool:
        attr = self.definition.get("attribute")
        val = self.definition.get("value")
        if attr:
            patient.attributes[attr] = val
        return True

class Counter(State):
    def process(self, patient: Patient, time: int) -> bool:
        attr = self.definition.get("attribute")
        action = self.definition.get("action", "increment")
        if attr:
            current = patient.attributes.get(attr, 0)
            if action == "increment":
                patient.attributes[attr] = current + 1
            elif action == "decrement":
                patient.attributes[attr] = current - 1
        return True

class Death(State):
    def process(self, patient: Patient, time: int) -> bool:
        cause = None
        if "condition_onset" in self.definition:
            cause = self.definition.get("condition_onset")
        patient.record_death(time, cause)
        return True

class Encounter(State):
    def process(self, patient: Patient, time: int) -> bool:
        encounter_class = self.definition.get("encounter_class", "ambulatory")
        encounter = __import__("medsynth.health_record", fromlist=["Encounter"]).Encounter(time, encounter_class)
        encounter.codes = self.definition.get("codes", [])
        encounter.facility_id = patient.attributes.get("primary_facility_id")
        encounter.facility_name = patient.attributes.get("primary_facility_name")
        patient.record.encounters.append(encounter)
        patient.record.current_encounter = encounter
        return True

class EncounterEnd(State):
    def process(self, patient: Patient, time: int) -> bool:
        if patient.record.current_encounter:
            patient.record.current_encounter.stop = time
            patient.record.current_encounter = None
        return True

class ConditionOnset(State):
    def process(self, patient: Patient, time: int) -> bool:
        target_encounter = patient.record.current_encounter_or_create(time)
        cond = __import__("medsynth.health_record", fromlist=["Condition"]).Condition(time)
        cond.codes = self.definition.get("codes", [])
        patient.record.conditions.append(cond)
        patient.record.present_conditions.append(cond)
        target_encounter.conditions.append(cond)
        
        # Store for reference by other states
        target = self.definition.get("target_encounter")
        if target:
            pass # Advanced Synthea feature
        return True

class ConditionEnd(State):
    def process(self, patient: Patient, time: int) -> bool:
        # Find the active condition
        codes = self.definition.get("codes", [])
        if not codes:
            return True
            
        target_code = codes[0].get("code")
        for cond in patient.record.present_conditions:
            if any(c.get("code") == target_code for c in cond.codes):
                cond.stop = time
                patient.record.present_conditions.remove(cond)
                break
        return True

class AllergyOnset(State):
    def process(self, patient: Patient, time: int) -> bool:
        al = __import__("medsynth.health_record", fromlist=["Allergy"]).Allergy(time)
        al.codes = self.definition.get("codes", [])
        patient.record.allergies.append(al)
        return True

class Symptom(State):
    def process(self, patient: Patient, time: int) -> bool:
        symp = self.definition.get("symptom")
        cause = self.definition.get("cause", self.module_name)
        prob = self.definition.get("probability", 1.0)
        
        if symp and patient.rand() <= prob:
            val = self.definition.get("exact", {}).get("quantity", 0)
            if "range" in self.definition:
                low = self.definition["range"].get("low", 0)
                high = self.definition["range"].get("high", 0)
                val = patient.rand_int(low, high)
                
            patient.set_symptom(cause, symp, val)
        return True

class Observation(State):
    def process(self, patient: Patient, time: int) -> bool:
        target_encounter = patient.record.current_encounter_or_create(time)
        category = self.definition.get("category", "vital-signs")
        
        val = 0
        if "exact" in self.definition:
            val = self.definition["exact"].get("quantity", 0)
        elif "range" in self.definition:
            low = self.definition["range"].get("low", 0)
            high = self.definition["range"].get("high", 0)
            val = low + patient.rand() * (high - low)
        elif "vital_sign" in self.definition:
            from medsynth.physiology import Physiology
            val = Physiology.get_vital_sign(patient, time, self.definition["vital_sign"])

        obs = __import__("medsynth.health_record", fromlist=["Observation"]).Observation(time, val, category)
        obs.codes = self.definition.get("codes", [])
        patient.record.observations.append(obs)
        target_encounter.observations.append(obs)
        return True

class Procedure(State):
    def process(self, patient: Patient, time: int) -> bool:
        target_encounter = patient.record.current_encounter_or_create(time)
        proc = __import__("medsynth.health_record", fromlist=["Procedure"]).Procedure(time)
        proc.codes = self.definition.get("codes", [])
        
        duration = self.definition.get("duration")
        if duration:
            proc.stop = time + convert_time(duration.get("quantity", 0), duration.get("unit", "minutes"))
        else:
            proc.stop = time
            
        patient.record.procedures.append(proc)
        target_encounter.procedures.append(proc)
        return True

class MedicationOrder(State):
    def process(self, patient: Patient, time: int) -> bool:
        target_encounter = patient.record.current_encounter_or_create(time)
        med = __import__("medsynth.health_record", fromlist=["Medication"]).Medication(time)
        med.codes = self.definition.get("codes", [])
        med.prescription_details = self.definition.get("prescription", {})
        patient.record.medications.append(med)
        target_encounter.medications.append(med)
        return True

class MedicationEnd(State):
    def process(self, patient: Patient, time: int) -> bool:
        codes = self.definition.get("codes", [])
        if not codes:
            return True
            
        target_code = codes[0].get("code")
        for med in patient.record.medications:
            if med.stop is None and any(c.get("code") == target_code for c in med.codes):
                med.stop = time
                break
        return True

class CarePlanStart(State):
    def process(self, patient: Patient, time: int) -> bool:
        target_encounter = patient.record.current_encounter_or_create(time)
        cp = __import__("medsynth.health_record", fromlist=["CarePlan"]).CarePlan(time)
        cp.codes = self.definition.get("codes", [])
        patient.record.careplans.append(cp)
        target_encounter.careplans.append(cp)
        return True

class CarePlanEnd(State):
    def process(self, patient: Patient, time: int) -> bool:
        codes = self.definition.get("codes", [])
        if not codes:
            return True
            
        target_code = codes[0].get("code")
        for cp in patient.record.careplans:
            if cp.stop is None and any(c.get("code") == target_code for c in cp.codes):
                cp.stop = time
                break
        return True

class CallSubmodule(State):
    def process(self, patient: Patient, time: int) -> bool:
        # Complex to implement natively without engine orchestrator. 
        # Typically the generator orchestrates this. We will return True to advance.
        return True

def build_state(name: str, definition: Dict[str, Any]) -> State:
    state_type = definition.get("type", "Simple")
    mapping = {
        "Initial": Initial,
        "Simple": Simple,
        "Terminal": Terminal,
        "Delay": Delay,
        "Guard": Guard,
        "Encounter": Encounter,
        "EncounterEnd": EncounterEnd,
        "ConditionOnset": ConditionOnset,
        "ConditionEnd": ConditionEnd,
        "AllergyOnset": AllergyOnset,
        "Symptom": Symptom,
        "Observation": Observation,
        "Procedure": Procedure,
        "MedicationOrder": MedicationOrder,
        "MedicationEnd": MedicationEnd,
        "CarePlanStart": CarePlanStart,
        "CarePlanEnd": CarePlanEnd,
        "Death": Death,
        "SetAttribute": SetAttribute,
        "Counter": Counter,
        "CallSubmodule": CallSubmodule
    }
    cls = mapping.get(state_type, Simple)
    return cls(name, definition)

