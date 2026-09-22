from .csv_exporter import CSVExporter
from .json_exporter import JSONExporter
from .fhir_exporter import FHIRExporter

class Exporter:
    """Orchestrates all export formats."""
    def __init__(self, output_dir: str, formats: list = None):
        if formats is None:
            formats = ['csv', 'json', 'fhir']
        
        self.formats = [f.lower() for f in formats]
        self.csv = CSVExporter(output_dir) if 'csv' in self.formats else None
        self.json = JSONExporter(output_dir) if 'json' in self.formats else None
        self.fhir = FHIRExporter(output_dir) if 'fhir' in self.formats else None

    def begin(self, resume=False):
        if self.csv: self.csv.begin(resume=resume)
        if self.json: self.json.begin(resume=resume)
        if self.fhir: self.fhir.begin(resume=resume)

    def export_patient(self, p):
        if self.csv: self.csv.export_patient(p)
        if self.json: self.json.export_patient(p)
        if self.fhir: self.fhir.export_patient(p)

    def flush(self):
        # CSV and JSON files are usually line-buffered, but we can call flush on them if we stored the file handles.
        # But we only strictly need it for FHIR chunks right now.
        if self.csv: 
            for f in self.csv.files.values(): f.flush()
        if self.json and self.json.jsonl_file:
            self.json.jsonl_file.flush()
        if self.fhir: self.fhir.flush()

    def end(self):
        if self.csv: self.csv.end()
        if self.json: self.json.end()
        if self.fhir: self.fhir.end()

    def export(self, population):
        self.begin()
        for p in population:
            self.export_patient(p)
        self.end()

