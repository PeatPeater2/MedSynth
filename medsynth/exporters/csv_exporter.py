import os
import csv
from typing import List
from medsynth.patient import Patient

class CSVExporter:
    def __init__(self, output_dir: str):
        self.output_dir = os.path.join(output_dir, 'csv')
        os.makedirs(self.output_dir, exist_ok=True)
        self.files = {}
        self.writers = {}

    def begin(self, resume=False):
        mode = 'a' if resume else 'w'
        
        self.files['patients'] = open(os.path.join(self.output_dir, 'patients.csv'), mode, newline='', encoding='utf-8')
        self.writers['patients'] = csv.writer(self.files['patients'])
        if not resume:
            self.writers['patients'].writerow(['Id', 'BIRTHDATE', 'DEATHDATE', 'FIRST', 'LAST', 'GENDER', 'ETHNICITY', 'STATE', 'LGA'])
        
        self.files['encounters'] = open(os.path.join(self.output_dir, 'encounters.csv'), mode, newline='', encoding='utf-8')
        self.writers['encounters'] = csv.writer(self.files['encounters'])
        if not resume:
            self.writers['encounters'].writerow(['Id', 'START', 'STOP', 'PATIENT', 'ENCOUNTERCLASS', 'CODE', 'DESCRIPTION', 'FACILITY_ID', 'FACILITY_NAME'])
        
        self.files['observations'] = open(os.path.join(self.output_dir, 'observations.csv'), mode, newline='', encoding='utf-8')
        self.writers['observations'] = csv.writer(self.files['observations'])
        if not resume:
            self.writers['observations'].writerow(['DATE', 'PATIENT', 'ENCOUNTER', 'CODE', 'DESCRIPTION', 'VALUE', 'CATEGORY'])
            
        self.files['conditions'] = open(os.path.join(self.output_dir, 'conditions.csv'), mode, newline='', encoding='utf-8')
        self.writers['conditions'] = csv.writer(self.files['conditions'])
        if not resume:
            self.writers['conditions'].writerow(['START', 'STOP', 'PATIENT', 'ENCOUNTER', 'CODE', 'DESCRIPTION'])
        
        self.files['medications'] = open(os.path.join(self.output_dir, 'medications.csv'), mode, newline='', encoding='utf-8')
        self.writers['medications'] = csv.writer(self.files['medications'])
        if not resume:
            self.writers['medications'].writerow(['START', 'STOP', 'PATIENT', 'PAYER', 'ENCOUNTER', 'CODE', 'DESCRIPTION', 'REASONCODE', 'REASONDESCRIPTION'])

    def export_patient(self, p: Patient):
        pid = p.attributes.get('id', str(id(p)))
        self.writers['patients'].writerow([
            pid,
            p.attributes.get('birthdate', ''),
            p.attributes.get('deathdate', ''),
            p.attributes.get('first_name', ''),
            p.attributes.get('last_name', ''),
            p.attributes.get('gender', ''),
            p.attributes.get('ethnicity', ''),
            p.attributes.get('state', ''),
            p.attributes.get('lga', '')
        ])
        
        for enc in p.record.encounters:
            code = enc.codes[0].get('code', '') if enc.codes else ''
            desc = enc.codes[0].get('display', '') if enc.codes else ''
            self.writers['encounters'].writerow([
                enc.id, enc.start, enc.stop or '', pid, getattr(enc, 'encounter_class', ''), code, desc,
                getattr(enc, 'facility_id', ''), getattr(enc, 'facility_name', '')
            ])
            
        for obs in p.record.observations:
            code = obs.codes[0].get('code', '') if obs.codes else ''
            desc = obs.codes[0].get('display', '') if obs.codes else ''
            val = getattr(obs, 'value', '')
            cat = getattr(obs, 'category', '')
            self.writers['observations'].writerow([obs.start, pid, '', code, desc, val, cat])
            
        for cond in p.record.conditions:
            code = cond.codes[0].get('code', '') if cond.codes else ''
            desc = cond.codes[0].get('display', '') if cond.codes else ''
            self.writers['conditions'].writerow([
                cond.start, cond.stop or '', pid, '', code, desc
            ])
            
        for med in p.record.medications:
            code = med.codes[0].get('code', '') if med.codes else ''
            desc = med.codes[0].get('display', '') if med.codes else ''
            self.writers['medications'].writerow([
                med.start, med.stop or '', pid, '', '', code, desc, '', ''
            ])

    def end(self):
        for f in self.files.values():
            f.close()

    def export(self, population: List[Patient]):
        self.begin()
        for p in population:
            self.export_patient(p)
        self.end()

