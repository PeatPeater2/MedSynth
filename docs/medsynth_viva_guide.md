# MEDSYNTH VIVA STUDY GUIDE

## 1. PROJECT OVERVIEW
MedSynth is a Python-based synthetic healthcare population generator targeted at the Nigerian demographic and epidemiological context. It generates highly realistic synthetic patients to bypass data privacy laws and data scarcity, enabling research, software testing, and AI training.

## 2. ARCHITECTURE DEFENSE
You must defend the separation of concerns:
- **`generator.py`**: The overarching engine.
- **`state_machine.py`**: The GMF engine parsing JSON rules.
- **`patient.py`**: The biological entity (Age, Sex, Attributes).
- **`health_record.py`**: The clinical ledger (Encounters, Conditions).
If asked why this structure was chosen, explain that separating Biology (`Patient`) from Clinical History (`HealthRecord`) allows the exporters to cleanly translate the ledger into FHIR without untangling it from the patient's biological state.

## 3. PYTHON CONCEPTS
You will be asked why certain Python constructs were used.
- Be prepared to explain `argparse` in `cli.py`.
- Be prepared to explain how `with open()` handles memory and file locks.
- Be prepared to explain `os.path.join` for cross-platform compatibility.

## 4. DATA PROVENANCE
If an examiner asks "How do you know this is Nigerian?", point to:
- `datasets/demographics/` (NBS age/sex distributions)
- `datasets/geography/` (Nigerian States and LGAs)
Do not claim it is 100% perfectly accurate; acknowledge that where data was missing (like LGA-level disease stats), state-level distributions were used. Honesty about data limitations scores higher than faking it.

## 5. DISEASE ENGINE (GMF)
The Generic Module Framework (GMF) uses JSON files to represent diseases.
Why? Because hardcoding Malaria in Python means only Python developers can update it. JSON modules allow clinicians to update the disease logic without touching the codebase.

## 6. COMMON EXAMINER TRAPS
* **TRAP**: "Why didn't you just write a Python script that randomly assigns diseases based on an Excel sheet?"
  * **DEFENSE**: That produces statistically flat data. It doesn't model chronological progression (getting disease A, which leads to disease B, which leads to death). MedSynth simulates time.
* **TRAP**: "If the unit tests pass, the clinical data is right."
  * **DEFENSE**: No! Software correctness (the JSON parsed correctly) is completely separate from Epidemiological correctness (the JSON incorrectly says 90% of people have stroke). 
* **TRAP**: "Since you have Yoruba names, you restrict them to the South West."
  * **DEFENSE**: No! Internal migration exists. People move. Hard-restricting names destroys the realism of diverse urban hubs like Lagos or Kano.

## 7. WEAKEST AREAS (OWN THEM)
If attacked on these, acknowledge them gracefully and explain how they will be fixed:
1. **Care-Seeking Delay**: We currently assume 100% immediate healthcare access. We need to add Socioeconomic Status (SES) barriers.
2. **Continuous Vitals**: We lack continuous lifetime BMI/BP modeling.
3. **RAM Constraints**: The engine currently holds all generated patients in memory. To scale to 1 million patients, the generator must be refactored to use `yield` (streaming).

