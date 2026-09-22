# MEDSYNTH VIVA ANSWER GUIDE

*This guide provides technically accurate answers based purely on the actual MedSynth implementation.*

## PYTHON ANSWERS
* **Dictionaries vs Lists**: Dictionaries provide O(1) lookup which is critical for state-machine transition lookups (e.g., finding state 'Onset' by name). Lists are O(N).
* **Pathlib / OS**: Paths are constructed using `os.path.join` to handle Windows (\\) and Linux (/) slash differences automatically.
* **Classes (Patient, Generator)**: Classes encapsulate state. A `Patient` maintains its own history and attributes without polluting global scope, allowing thousands of patients to exist independently in memory.
* **Argparse**: Used in `cli.py` over `sys.argv` because it automatically handles help menus, defaults, and type enforcement (`--patients 20` automatically casts to int).
* **Yield / Streaming**: Currently, MedSynth uses lists (`all_patients.extend(cohort)`). To fix OOM errors at 1M patients, we must transition to `yield` (generators) to flush to disk incrementally.
* **Seed Manipulation**: In `cli.py`, the seed is shifted (`args.seed += count`) when grouping because if we run two identical groups with the exact same seed, we get identical twins.

## ARCHITECTURE & GMF ANSWERS
* **GMF**: Generic Module Framework. It separates clinical logic (JSON) from execution logic (Python). This allows doctors to write disease modules in JSON without knowing Python.
* **Time Advancement**: Time advances linearly. The main loop steps through time. If a module hits a `Delay` state, it calculates the target timestamp and goes to sleep until the global clock reaches that time.
* **Decoupling**: `HealthRecord` is decoupled from `Patient` so that clinical events (FHIR generation) do not clutter the biological simulation (age, sex, genetics).

## DEMOGRAPHICS & GEOGRAPHY ANSWERS
* **Yoruba in Kano**: People migrate. Hard-restricting names to geography prevents modeling urban hubs (like Lagos or Kano) which contain diverse populations.
* **Geographic Hierarchy**: `nigeria_lgas.csv` maps LGAs to States. The CLI validates this in `cli.py` to prevent generating a patient in "Ikeja, Kano" (Ikeja belongs to Lagos).
* **Missing Data**: If LGA-level disease prevalence is missing, we fall back to state-level. We do **not** fabricate missing data, as that destroys statistical provenance.

## CLINICAL & FHIR ANSWERS
* **Care-Seeking Delay Limitation**: A major weakness. Currently, disease onset immediately triggers an encounter. We do not model the days a patient might wait due to poverty before visiting a clinic.
* **Continuous Vitals Limitation**: Another weakness. Vitals are currently discrete `Observation` states in JSON. A mature engine needs continuous background tracking.
* **FHIR Referential Integrity**: `Condition.subject` maps directly to `Patient.id` (UUID). This guarantees that relational graphs are perfectly maintained in the FHIR Bundle exporter.

## TESTING & VALIDATION
* **Test Validity**: Passing software tests (unit tests) only proves the code doesn't crash and the state machine follows its logic. It does **not** prove epidemiological validity. A module could be perfectly coded to give 100% of the population HIV. Software correctness != Clinical correctness.

## HOUSE BUILDING ANALOGY
* **Foundation**: Python environment, CLI, Random Number generation.
* **Structure / Plumbing**: The Architecture (Generator, Patient, HealthRecord).
* **Blueprint**: The JSON disease modules dictating how the house is built.
* **Building Materials**: The NBS Demographics and Geography CSV datasets.
* **Building Inspection**: Unit tests and FHIR Validation.
* **The Final House**: The exported synthetic population (CSV/JSON/FHIR).

