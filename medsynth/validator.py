import json
from typing import List

VALID_STATE_TYPES = {
    "Initial", "Simple", "Terminal", "Delay", "Guard", "Encounter", "EncounterEnd",
    "ConditionOnset", "ConditionEnd", "AllergyOnset", "Symptom", "Observation", 
    "Procedure", "MedicationOrder", "MedicationEnd", "CarePlanStart", "CarePlanEnd", 
    "Death", "SetAttribute", "Counter", "CallSubmodule"
}

def validate_module(filepath: str) -> List[str]:
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Malformed JSON: {e}"]
    except Exception as e:
        return [f"Could not read file: {e}"]
        
    if "states" not in data:
        return ["Missing 'states' object in module."]
        
    states = data["states"]
    
    if "Initial" not in states:
        errors.append("Missing 'Initial' state.")
        
    has_terminal = any(s.get("type") == "Terminal" for s in states.values())
    if not has_terminal:
        errors.append("Missing 'Terminal' state.")
        
    # Build transition map
    transitions = {}
    for state_name, state_def in states.items():
        state_type = state_def.get("type")
        if state_type not in VALID_STATE_TYPES:
            errors.append(f"Invalid state type '{state_type}' in state '{state_name}'.")
            
        trans = []
        if "direct_transition" in state_def:
            trans.append(state_def["direct_transition"])
        
        if "conditional_transition" in state_def:
            for ct in state_def["conditional_transition"]:
                if "transition" in ct:
                    trans.append(ct["transition"])
            if "fallback_transition" in state_def:
                trans.append(state_def["fallback_transition"])
                
        if "distributed_transition" in state_def:
            for dt in state_def["distributed_transition"]:
                if "transition" in dt:
                    trans.append(dt["transition"])
            if "fallback_transition" in state_def:
                trans.append(state_def["fallback_transition"])
                
        if "complex_transition" in state_def:
            for ct in state_def["complex_transition"]:
                for dt in ct.get("distributions", []):
                    if "transition" in dt:
                        trans.append(dt["transition"])
            if "fallback_transition" in state_def:
                trans.append(state_def["fallback_transition"])
                
        transitions[state_name] = trans
        
        # Verify valid transition references
        for t in trans:
            if t not in states:
                errors.append(f"Invalid transition '{t}' from state '{state_name}'.")
                
    # Check reachability
    if "Initial" in states:
        reachable = set()
        queue = ["Initial"]
        while queue:
            curr = queue.pop(0)
            if curr not in reachable:
                reachable.add(curr)
                queue.extend(transitions.get(curr, []))
                
        for state_name in states:
            if state_name not in reachable:
                errors.append(f"Unreachable state: '{state_name}'.")
                
    return errors

