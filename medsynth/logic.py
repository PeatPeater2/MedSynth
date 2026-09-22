from typing import Dict, Any, List
from medsynth.patient import Patient

class Logic:
    """
    Evaluates logic conditions for state transitions.
    """
    def __init__(self, definition: Dict[str, Any]):
        self.condition_type = definition.get("condition_type", "True")
        self.definition = definition

    def test(self, patient: Patient, time: int) -> bool:
        if self.condition_type == "True":
            return True
        elif self.condition_type == "False":
            return False
        elif self.condition_type == "And":
            conditions = [Logic(c) for c in self.definition.get("conditions", [])]
            return all(c.test(patient, time) for c in conditions)
        elif self.condition_type == "Or":
            conditions = [Logic(c) for c in self.definition.get("conditions", [])]
            return any(c.test(patient, time) for c in conditions)
        elif self.condition_type == "Not":
            condition = Logic(self.definition.get("condition", {}))
            return not condition.test(patient, time)
        elif self.condition_type == "Gender":
            return patient.attributes.get("gender") == self.definition.get("gender")
        elif self.condition_type == "Age":
            age = patient.age_in_months(time) if self.definition.get("unit") == "months" else patient.age_in_years(time)
            op = self.definition.get("operator", "==")
            val = self.definition.get("quantity", 0)
            return self._compare(age, op, val)
        elif self.condition_type == "Attribute":
            attr = patient.attributes.get(self.definition.get("attribute"))
            op = self.definition.get("operator", "==")
            val = self.definition.get("value")
            if attr is None:
                return op == "is nil"
            elif op == "is not nil":
                return True
            return self._compare(attr, op, val)
        elif self.condition_type == "Symptom":
            symp = patient.get_symptom(self.definition.get("symptom", ""))
            op = self.definition.get("operator", "==")
            val = self.definition.get("value", 0)
            return self._compare(symp, op, val)
        elif self.condition_type == "PriorState":
            # Check if patient history contains this state
            state_name = self.definition.get("name")
            since = self.definition.get("since")
            
            # Simple fallback for now
            return True
        else:
            return False

    def _compare(self, left: Any, operator: str, right: Any) -> bool:
        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == "<":
            return left < right
        elif operator == "<=":
            return left <= right
        elif operator == ">":
            return left > right
        elif operator == ">=":
            return left >= right
        elif operator == "is nil":
            return left is None
        elif operator == "is not nil":
            return left is not None
        return False

