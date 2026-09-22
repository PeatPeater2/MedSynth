# Current Capabilities

This document outlines everything MedSynth can currently do, explicitly distinguishing between what is verified and working versus what is under development.

## 1. IMPLEMENTED & VALIDATED

### Extreme-Scale Architecture
* **Streaming Generation:** MedSynth can stream patients to disk endlessly without running out of RAM. Tested and verified.
* **Multiprocessing:** Supports executing on multiple CPU cores (`--workers`) for significant speedups.
* **Checkpoint & Resume:** Safely interrupts and resumes generation runs without corrupting data or generating duplicate IDs.
* **Deterministic Seeding:** `--seed X` guarantees perfectly reproducible outputs across different machines.

### Demographics & Geography
* **Nigerian Geography:** Fully supports 36 States and 774 LGAs.
* **Culturally Accurate Names:** Assigns Yoruba, Hausa, Igbo, and other names based on geographic probability.
* **Socioeconomic Status:** Assigns NDHS Wealth Quintiles (1-5).
* **Insurance Probability:** Assigns NHIA / Private insurance status based on wealth correlations.

### Clinical & Healthcare World
* **Real Facility Anchoring:** Over 46,146 real HDX Nigerian healthcare facilities are fully integrated.
* **Care-Seeking Delays:** Diseases route through poverty checks to simulate delayed hospital visits for poorer patients.
* **Continuous Physiology:** Height, Weight, BMI, Blood Pressure, Hemoglobin, and Temperature scale analytically with age and disease state.

### Export Formats
* **CSV:** Flat-file relational tables (Patients, Encounters, Conditions, Observations).
* **JSONL:** Raw internal JSON representation.
* **FHIR R4:** Fully compliant HL7 FHIR chunked bundles (`bundle_0000.json`) to support integration with EMRs.

## 2. PARTIALLY IMPLEMENTED

* **Disease Library:** The engine is perfect, but the actual JSON library is small. Currently contains: Malaria, Sickle Cell Disease, LRI (Lower Respiratory Infection), and an Annual Checkup module.

## 3. NOT IMPLEMENTED / FUTURE EXTENSIONS

* **Maternal Tracking & Pregnancy:** The system does not currently model gestation, birth events, or maternal mortality.
* **Household Modelling:** Patients cannot currently be grouped into families (e.g. tracking parents and children living in the same house).
* **Synthetic Providers:** Patients go to real Facilities, but there are no synthetic Doctors or Nurses attached to those facilities yet.
* **Financial Billing:** The engine does not simulate the Naira cost of treatments or process insurance claims.

