import random
from typing import Dict, Any, List, Optional
from medsynth.health_record import HealthRecord

class Patient:
    """
    Represents a synthetic patient in MedSynth, incorporating demographic 
    identity and the clinical HealthRecord.
    """
    def __init__(self, seed: int):
        self.random = random.Random(seed)
        self.seed = seed
        self.attributes: Dict[str, Any] = {}
        
        # The relational clinical record
        self.record = HealthRecord(self)
        
        # Clinical state tracking for the Generic Module Framework
        self.history: Dict[str, List[Any]] = {}  # Tracks module state histories
        self.symptoms: Dict[str, int] = {}       # Tracks current symptoms (1-100 severity)
        self.vital_signs: Dict[str, Any] = {}    # Tracks continuous vital signs
        
        self.last_updated: int = 0

    def rand(self) -> float:
        return self.random.random()

    def rand_int(self, a: int, b: int) -> int:
        return self.random.randint(a, b)

    def rand_choice(self, seq):
        return self.random.choice(seq)

    def rand_choices(self, seq, weights=None, k=1):
        return self.random.choices(seq, weights=weights, k=k)

    def age_in_years(self, current_time_ms: int) -> int:
        if "birthdate" not in self.attributes:
            return 0
        diff = current_time_ms - self.attributes["birthdate"]
        return max(0, int(diff / (1000 * 60 * 60 * 24 * 365.25)))

    def age_in_months(self, current_time_ms: int) -> int:
        if "birthdate" not in self.attributes:
            return 0
        diff = current_time_ms - self.attributes["birthdate"]
        return max(0, int(diff / (1000 * 60 * 60 * 24 * 30.44)))

    def is_alive(self, current_time_ms: int) -> bool:
        born = "birthdate" in self.attributes and self.attributes["birthdate"] <= current_time_ms
        died_time = self.attributes.get("deathdate")
        not_dead = (died_time is None) or (died_time > current_time_ms)
        return born and not_dead

    def record_death(self, time: int, cause: Optional[str] = None):
        if self.is_alive(time):
            self.attributes["deathdate"] = time
            if cause:
                self.attributes["cause_of_death"] = cause
            self.record.record_death(time)

    def set_symptom(self, cause: str, symptom_name: str, severity: int):
        """
        Synthea handles symptoms by taking the maximum value across all causes.
        Here we simplify slightly but preserve the concept.
        """
        # A more robust system would track symptoms by cause. 
        # For MedSynth's current spec, we take the max value.
        current = self.symptoms.get(symptom_name, 0)
        if severity > current:
            self.symptoms[symptom_name] = severity

    def get_symptom(self, symptom_name: str) -> int:
        return self.symptoms.get(symptom_name, 0)

    def set_vital_sign(self, name: str, value: Any):
        self.vital_signs[name] = value

    def get_vital_sign(self, name: str) -> Any:
        return self.vital_signs.get(name)

