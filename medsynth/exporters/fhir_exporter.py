import os
import json
import datetime
from typing import List
from medsynth.patient import Patient

class FHIRExporter:
    def __init__(self, output_dir: str, chunk_size: int = 1000):
        self.output_dir = os.path.join(output_dir, 'fhir')
        os.makedirs(self.output_dir, exist_ok=True)
        self.chunk_size = chunk_size
        self.current_entries = []
        self.chunk_index = 0
        self.patient_count = 0

    def _ms_to_date_str(self, ms: int) -> str:
        if not ms:
            return ""
        dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=ms / 1000.0)
        return dt.strftime('%Y-%m-%d')

    def begin(self, resume=False):
        self.current_entries = []
        self.patient_count = 0
        if resume:
            # Find the highest bundle index
            existing = [f for f in os.listdir(self.output_dir) if f.startswith('bundle_') and f.endswith('.json')]
            if existing:
                highest = max([int(f.replace('bundle_', '').replace('.json', '')) for f in existing])
                self.chunk_index = highest + 1
            else:
                self.chunk_index = 0
        else:
            self.chunk_index = 0

    def flush(self):
        self._write_chunk()

    def _write_chunk(self):
        if not self.current_entries:
            return
        path = os.path.join(self.output_dir, f"bundle_{self.chunk_index:06d}.json")
        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": self.current_entries
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, indent=2)
        self.chunk_index += 1
        self.current_entries = []
        self.patient_count = 0

    def export_patient(self, p: Patient):
        pid = p.attributes.get('id', str(id(p)))
        
        # Patient Resource
        patient_resource = {
            "resourceType": "Patient",
            "id": pid,
            "name": [
                {
                    "use": "official",
                    "family": p.attributes.get("last_name", ""),
                    "given": [p.attributes.get("first_name", "")]
                }
            ],
            "gender": "male" if p.attributes.get("gender") == "M" else "female",
            "birthDate": self._ms_to_date_str(p.attributes.get("birthdate", 0)),
            "address": [
                {
                    "state": p.attributes.get("state", ""),
                    "city": p.attributes.get("lga", ""),
                    "country": "NG"
                }
            ]
        }
        
        self.current_entries.append({
            "fullUrl": f"urn:uuid:{pid}",
            "resource": patient_resource,
            "request": {"method": "POST", "url": "Patient"}
        })
        
        # Conditions
        for cond in p.record.conditions:
            cond_res = {
                "resourceType": "Condition",
                "subject": {"reference": f"urn:uuid:{pid}"},
                "clinicalStatus": {
                    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active" if not cond.stop else "resolved"}]
                },
                "onsetDateTime": self._ms_to_date_str(cond.start)
            }
            if cond.stop:
                cond_res["abatementDateTime"] = self._ms_to_date_str(cond.stop)
                
            if cond.codes:
                cond_res["code"] = {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": cond.codes[0].get("code"),
                            "display": cond.codes[0].get("display")
                        }
                    ]
                }
                
            self.current_entries.append({
                "resource": cond_res,
                "request": {"method": "POST", "url": "Condition"}
            })

        # Encounters
        for enc in p.record.encounters:
            enc_res = {
                "resourceType": "Encounter",
                "id": enc.id,
                "status": "finished",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": getattr(enc, 'encounter_class', 'AMB')
                },
                "subject": {"reference": f"urn:uuid:{pid}"},
                "period": {
                    "start": self._ms_to_date_str(enc.start)
                }
            }
            if enc.stop:
                enc_res["period"]["end"] = self._ms_to_date_str(enc.stop)
                
            if enc.codes:
                enc_res["type"] = [{
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": enc.codes[0].get("code"),
                            "display": enc.codes[0].get("display")
                        }
                    ]
                }]
                
            if getattr(enc, 'facility_id', None):
                enc_res["location"] = [{
                    "location": {
                        "reference": f"Location/{enc.facility_id}",
                        "display": getattr(enc, 'facility_name', 'Unknown Facility')
                    }
                }]
                
            self.current_entries.append({
                "fullUrl": f"urn:uuid:{enc.id}",
                "resource": enc_res,
                "request": {"method": "POST", "url": "Encounter"}
            })

        # Observations
        for obs in p.record.observations:
            obs_res = {
                "resourceType": "Observation",
                "status": "final",
                "subject": {"reference": f"urn:uuid:{pid}"},
                "effectiveDateTime": self._ms_to_date_str(obs.start)
            }
            if obs.codes:
                obs_res["code"] = {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": obs.codes[0].get("code"),
                            "display": obs.codes[0].get("display")
                        }
                    ]
                }
            if hasattr(obs, 'value'):
                obs_res["valueQuantity"] = {
                    "value": obs.value
                }
            
            self.current_entries.append({
                "resource": obs_res,
                "request": {"method": "POST", "url": "Observation"}
            })
            
        self.patient_count += 1
        if self.patient_count >= self.chunk_size:
            self._write_chunk()

    def end(self):
        self._write_chunk()

    def export(self, population: List[Patient]):
        self.begin()
        for p in population:
            self.export_patient(p)
        self.end()

