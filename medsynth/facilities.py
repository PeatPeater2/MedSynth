import os
import csv
from typing import Dict, List, Optional
from medsynth.patient import Patient

class Facility:
    def __init__(self, f_id: str, name: str, f_type: str, category: str, ownership: str, state: str, lga: str, lat: float, lon: float):
        self.id = f_id
        self.name = name
        self.type = f_type
        self.category = category
        self.ownership = ownership
        self.state = state
        self.lga = lga
        self.latitude = lat
        self.longitude = lon

class FacilityManager:
    """
    Manages loading and querying of the Nigerian Healthcare Facility Registry data.
    """
    def __init__(self):
        self.facilities: List[Facility] = []
        self.by_state: Dict[str, List[Facility]] = {}
        self.by_lga: Dict[str, Dict[str, List[Facility]]] = {}
        self._load_data()

    def _load_data(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        facility_file = os.path.join(base_dir, 'datasets', 'facilities', 'nigeria_facilities.csv')
        
        if not os.path.exists(facility_file):
            return
            
        with open(facility_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat = float(row['latitude'])
                    lon = float(row['longitude'])
                except (ValueError, TypeError):
                    continue
                    
                fac = Facility(
                    f_id=row['facility_id'],
                    name=row['facility_name'],
                    f_type=row['facility_type'],
                    category=row['category'],
                    ownership=row['ownership'],
                    state=row['state'],
                    lga=row['lga'],
                    lat=lat,
                    lon=lon
                )
                self.facilities.append(fac)
                
                # Group by state
                if fac.state not in self.by_state:
                    self.by_state[fac.state] = []
                self.by_state[fac.state].append(fac)
                
                # Group by LGA
                if fac.state not in self.by_lga:
                    self.by_lga[fac.state] = {}
                if fac.lga not in self.by_lga[fac.state]:
                    self.by_lga[fac.state][fac.lga] = []
                self.by_lga[fac.state][fac.lga].append(fac)

    def assign_facility(self, patient: Patient) -> Optional[Facility]:
        """
        Assigns a primary care facility to a patient based on their location.
        Currently uses a modelled assignment: picking a random facility in their LGA.
        If the LGA has no facilities, picks a random facility in their State.
        """
        state = patient.attributes.get("state")
        lga = patient.attributes.get("lga")
        
        if not state:
            return None
            
        # Try LGA first
        lga_facilities = self.by_lga.get(state, {}).get(lga, [])
        if lga_facilities:
            return patient.rand_choice(lga_facilities)
            
        # Fallback to state
        state_facilities = self.by_state.get(state, [])
        if state_facilities:
            return patient.rand_choice(state_facilities)
            
        return None

