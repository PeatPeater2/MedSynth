from typing import List, Dict, Any, Optional
import uuid

class Entry:
    """Base class for all entries in the Health Record."""
    def __init__(self, start: int, entry_type: str):
        self.id: str = str(uuid.uuid4())
        self.start: int = start
        self.stop: Optional[int] = None
        self.type: str = entry_type
        # Codes are typically dictionaries like {"system": "SNOMED-CT", "code": "123", "display": "Name"}
        self.codes: List[Dict[str, str]] = []

class Encounter(Entry):
    def __init__(self, start: int, encounter_class: str):
        super().__init__(start, "encounter")
        self.encounter_class = encounter_class
        self.facility_id: Optional[str] = None
        self.facility_name: Optional[str] = None
        self.conditions: List[Condition] = []
        self.observations: List[Observation] = []
        self.procedures: List[Procedure] = []
        self.medications: List[Medication] = []
        self.careplans: List[CarePlan] = []
        self.immunizations: List[Immunization] = []
        # Facility could be assigned here

class Condition(Entry):
    def __init__(self, start: int):
        super().__init__(start, "condition")
        
class Observation(Entry):
    def __init__(self, start: int, value: Any, category: str = "vital-signs"):
        super().__init__(start, "observation")
        self.value = value
        self.category = category

class Procedure(Entry):
    def __init__(self, start: int):
        super().__init__(start, "procedure")
        self.reasons: List[Condition] = []

class Medication(Entry):
    def __init__(self, start: int):
        super().__init__(start, "medication")
        self.reasons: List[Condition] = []
        self.prescription_details: Dict[str, Any] = {}

class CarePlan(Entry):
    def __init__(self, start: int):
        super().__init__(start, "careplan")
        self.reasons: List[Condition] = []
        self.activities: List[Dict[str, Any]] = []

class Immunization(Entry):
    def __init__(self, start: int):
        super().__init__(start, "immunization")

class Allergy(Entry):
    def __init__(self, start: int):
        super().__init__(start, "allergy")

class HealthRecord:
    """
    A relational clinical record for a synthetic patient.
    Maintains chronological lists of entries and their relationships.
    """
    def __init__(self, patient):
        self.patient = patient
        self.encounters: List[Encounter] = []
        self.conditions: List[Condition] = []
        self.observations: List[Observation] = []
        self.procedures: List[Procedure] = []
        self.medications: List[Medication] = []
        self.careplans: List[CarePlan] = []
        self.immunizations: List[Immunization] = []
        self.allergies: List[Allergy] = []
        
        # Ongoing active encounters/conditions for the state machine to reference
        self.current_encounter: Optional[Encounter] = None
        self.present_conditions: List[Condition] = []

    def record_death(self, time: int):
        self.patient.attributes["deathdate"] = time

    def current_encounter_or_create(self, time: int) -> Encounter:
        """
        Returns the current active encounter. If none exists, creates a virtual/dummy encounter.
        This mirrors Synthea's behavior where some states require an encounter context.
        """
        if self.current_encounter:
            return self.current_encounter
        
        # Create a dummy wellness encounter to house this event
        dummy = Encounter(time, "ambulatory")
        dummy.codes = [{"system": "SNOMED-CT", "code": "162673000", "display": "General examination of patient (procedure)"}]
        dummy.facility_id = self.patient.attributes.get("primary_facility_id")
        dummy.facility_name = self.patient.attributes.get("primary_facility_name")
        self.encounters.append(dummy)
        self.current_encounter = dummy
        return dummy

