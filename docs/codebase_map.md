# Codebase Map

This document explains the purpose of every critical file in the MedSynth repository.

```text
C:\Projects\MedSynth\
├── medsynth/                     # The core Python package
│   ├── __main__.py               # Package entrypoint (routes `python -m medsynth` to cli.py)
│   ├── cli.py                    # The Command Line Interface. Parses arguments, sets up streaming & multiprocessing.
│   ├── generator.py              # The Factory. Holds datasets in memory and orchestrates `generate_person`.
│   ├── patient.py                # Defines the `Patient` class (biology, attributes, and HealthRecord reference).
│   ├── health_record.py          # Defines `HealthRecord`, `Encounter`, `Condition`, `Observation` classes.
│   ├── state_machine.py          # The GMF Engine. Parses JSON modules into executable python States.
│   ├── module.py                 # Loads and manages the disease JSON files.
│   ├── physiology.py             # Analytic continuous vitals engine (Height, Weight, BMI, BP, Hemoglobin).
│   ├── demographics.py           # Evaluates age, sex, and socioeconomic status based on NDHS data.
│   ├── geography.py              # Handles LGA/State assignment and weighting based on NBS population.
│   ├── facilities.py             # Loads the HDX dataset and assigns patients to their nearest hospitals.
│   │
│   └── exporters/                # The Translation Layer
│       ├── __init__.py           # Exporter wrapper.
│       ├── csv_exporter.py       # Writes flat relational tables.
│       ├── json_exporter.py      # Writes raw internal JSON dictionaries.
│       └── fhir_exporter.py      # Translates internal objects to HL7 FHIR R4 and manages bundle chunking.
│
├── datasets/                     # The Ground Truth Data
│   ├── demographics/
│   │   └── state_population.csv  # NBS state weights.
│   ├── facilities/
│   │   └── nigeria_facilities.csv# HDX list of 46,146 verified Nigerian clinics/hospitals.
│   ├── geography/
│   │   ├── nigeria_states.csv    # List of 36 States + FCT.
│   │   └── nigeria_lgas.csv      # List of 774 Local Government Areas mapped to states.
│   ├── names/
│   │   └── *_names.csv           # Regional name distributions (Hausa, Yoruba, Igbo, etc.).
│   └── diseases/                 # The Clinical Instruction Manuals
│       ├── malaria.json          # GMF model for Malaria.
│       ├── lower_respiratory_infection.json # GMF model for LRI.
│       ├── sickle_cell.json      # GMF model for SCD.
│       └── annual_checkup.json   # Routine vitals collection.
│
├── docs/                         # The Knowledge Base (You are here)
└── tests/                        # Automated validation scripts (if applicable)
```

## Critical Call Flows

**Standard Generation Flow:**
`cli.py` -> `Generator.generate_stream()` -> `Generator.generate_person()` -> `Patient()` -> `Geography` -> `Demographics` -> `Facilities` -> `state_machine.py (execute modules)` -> `HealthRecord` -> `exporter.export_patient()`.

