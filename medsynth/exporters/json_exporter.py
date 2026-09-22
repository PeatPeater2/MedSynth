import os
import json
from typing import List
from medsynth.patient import Patient

class JSONExporter:
    def __init__(self, output_dir: str, mode: str = 'jsonl'):
        self.output_dir = os.path.join(output_dir, 'json')
        os.makedirs(self.output_dir, exist_ok=True)
        self.mode = mode
        self.jsonl_file = None

    def begin(self, resume=False):
        if self.mode == 'jsonl':
            mode = 'a' if resume else 'w'
            self.jsonl_file = open(os.path.join(self.output_dir, 'patients.jsonl'), mode, encoding='utf-8')

    def export_patient(self, p: Patient):
        pid = p.attributes.get('id', str(id(p)))
        data = {
            "id": pid,
            "attributes": p.attributes,
            "record": {
                "encounters": [self._serialize(e) for e in p.record.encounters],
                "conditions": [self._serialize(c) for c in p.record.conditions],
                "observations": [self._serialize(o) for o in p.record.observations],
                "procedures": [self._serialize(pr) for pr in p.record.procedures],
                "medications": [self._serialize(m) for m in p.record.medications],
                "immunizations": [self._serialize(i) for i in p.record.immunizations],
                "allergies": [self._serialize(a) for a in p.record.allergies],
                "careplans": [self._serialize(cp) for cp in p.record.careplans]
            }
        }
        
        if self.mode == 'jsonl':
            json.dump(data, self.jsonl_file)
            self.jsonl_file.write('\n')
        else:
            path = os.path.join(self.output_dir, f"{pid}.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

    def end(self):
        if self.jsonl_file:
            self.jsonl_file.close()

    def export(self, population: List[Patient]):
        self.begin()
        for p in population:
            self.export_patient(p)
        self.end()

    def _serialize(self, obj):
        data = {
            "start": obj.start,
            "stop": obj.stop,
            "codes": obj.codes
        }
        if hasattr(obj, 'value'):
            data["value"] = obj.value
        if getattr(obj, 'type', '') == 'encounter':
            if getattr(obj, 'facility_id', None):
                data["facility_id"] = obj.facility_id
            if getattr(obj, 'facility_name', None):
                data["facility_name"] = obj.facility_name
            data["encounter_class"] = getattr(obj, 'encounter_class', '')
        return data

