import json
from typing import Dict, Any, List
from medsynth.patient import Patient
from medsynth.state_machine import build_state, State, Terminal

class Module:
    """
    Represents a Synthea generic module containing a state machine.
    """
    def __init__(self, definition: Dict[str, Any]):
        self.name: str = definition.get("name", "Unknown Module")
        self.states: Dict[str, State] = {}
        
        for state_name, state_def in definition.get("states", {}).items():
            state = build_state(state_name, state_def)
            state.module_name = self.name
            self.states[state_name] = state

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Module':
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls(json.load(f))

    def process(self, patient: Patient, time: int) -> bool:
        """
        Executes the module for the patient at the current timestep.
        Returns True if the module has reached a Terminal state.
        """
        if not patient.is_alive(time):
            return True
            
        history_key = self.name
        
        # Initialize if not present
        if history_key not in patient.history:
            if "Initial" not in self.states:
                return True
            patient.history[history_key] = [self.states["Initial"].clone()]
            
        history = patient.history[history_key]
        current_state = history[0]
        
        while current_state.run(patient, time, terminate_on_death=True):
            next_state_name = current_state.transition(patient, time)
            
            if not next_state_name or next_state_name not in self.states:
                return True 
                
            current_state = self.states[next_state_name].clone()
            history.insert(0, current_state)
            
            # Synthea quirk: If the state we just exited was a delay that completed in the past,
            # we recursively evaluate from that exact past time.
            exited_time = history[1].exited
            if exited_time is not None and exited_time < time:
                if not patient.is_alive(exited_time):
                    return True
                
                if self.process(patient, exited_time):
                    return True
                        
                current_state = patient.history[history_key][0]
                
        return isinstance(current_state, Terminal)

