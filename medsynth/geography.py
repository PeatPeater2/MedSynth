import os
import csv
import random
from typing import Dict, List, Optional
from medsynth.patient import Patient

class Geography:
    """
    Handles Nigerian geographical boundaries (States, LGAs) for patient allocation,
    weighted by actual demographic population figures.
    """
    def __init__(self):
        self.states: List[str] = []
        self.state_weights: List[float] = []
        self.lgas_by_state: Dict[str, List[str]] = {}
        self._load_data()

    def _load_data(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        state_file = os.path.join(base_dir, 'datasets', 'geography', 'nigeria_states.csv')
        lga_file = os.path.join(base_dir, 'datasets', 'geography', 'nigeria_lgas.csv')
        pop_file = os.path.join(base_dir, 'datasets', 'demographics', 'state_population.csv')
        
        # Load state populations
        populations = {}
        if os.path.exists(pop_file):
            with open(pop_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    populations[row['state']] = float(row['population'])
                    
        if os.path.exists(state_file) and os.path.getsize(state_file) > 0:
            with open(state_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state = row['state']
                    self.states.append(state)
                    self.lgas_by_state[state] = []
                    # Default to 1 if missing in population file
                    self.state_weights.append(populations.get(state, 1.0))
        else:
            raise FileNotFoundError("nigeria_states.csv dataset is missing. Data foundation is required.")

        if os.path.exists(lga_file) and os.path.getsize(lga_file) > 0:
            with open(lga_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state = row.get('state')
                    lga = row.get('lga')
                    if state in self.lgas_by_state and lga:
                        self.lgas_by_state[state].append(lga)
        else:
            raise FileNotFoundError("nigeria_lgas.csv dataset is missing.")

    def assign_point(self, patient: Patient, options):
        target_state = options.target_state
        target_lga = options.target_lga

        if target_lga:
            # Find the state for this LGA to keep them consistent
            found_state = None
            for state_name, lgas in self.lgas_by_state.items():
                if target_lga in lgas:
                    found_state = state_name
                    break
            
            if found_state:
                patient.attributes["state"] = found_state
                patient.attributes["lga"] = target_lga
                return
            else:
                # Fallback if LGA not found, but we should assign the requested LGA string anyway
                patient.attributes["state"] = target_state if isinstance(target_state, str) else (target_state[0] if isinstance(target_state, list) else "Unknown State")
                patient.attributes["lga"] = target_lga
                return

        if target_state:
            if isinstance(target_state, str) and target_state in self.states:
                state = target_state
            elif isinstance(target_state, list):
                # Pick uniformly from the requested states
                state = patient.rand_choice(target_state)
            else:
                state = patient.rand_choices(self.states, weights=self.state_weights, k=1)[0]
        else:
            state = patient.rand_choices(self.states, weights=self.state_weights, k=1)[0]
        
        lgas = self.lgas_by_state.get(state, [])
        lga = patient.rand_choice(lgas) if lgas else "Unknown LGA"
        
        patient.attributes["state"] = state
        patient.attributes["lga"] = lga
