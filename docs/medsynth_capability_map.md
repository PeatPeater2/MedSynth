# MEDSYNTH CAPABILITY MAP

## 1. POPULATION & DEMOGRAPHICS
* **Base Generation**: CURRENTLY IMPLEMENTED. Probabilistic based on NBS data.
* **Exact Targeting**: CURRENTLY IMPLEMENTED via CLI constraints.
* **Ethnic/Name Modelling**: CURRENTLY IMPLEMENTED. Zipfian distribution, handles migration appropriately (names are not hard-locked to states).
* **Family/Household Graph**: MISSING (RECOMMENDED). Patients are isolated singletons. To model infectious disease spread (like TB or COVID) or genetics (like Sickle Cell), patients must be generated in household units. Requires a new graph-generation architecture.
* **Internal Migration**: MISSING (OPTIONAL). Geography is currently static from birth.

## 2. LIFE COURSE
* **Birth & Death**: CURRENTLY IMPLEMENTED. Standard lifespan simulated.
* **Aging Engine**: CURRENTLY IMPLEMENTED.
* **Pregnancy & Childbirth**: MISSING (RECOMMENDED). Essential for modeling maternal health issues (Preeclampsia, Hemorrhage) which are major contributors to Nigerian mortality. Requires injecting a "pregnancy status" attribute dynamically.

## 3. PHYSIOLOGY & BIOMETRICS
* **Discrete Observations**: CURRENTLY IMPLEMENTED. (e.g. A module explicitly fires an observation).
* **Continuous Physiological Tracking (Growth, BMI, BP)**: MISSING (RECOMMENDED). Currently, if a patient gets hypertension, it's a random chance based on age. A mature engine continuously calculates BP/BMI curves over a lifetime, allowing diseases to trigger deterministically when thresholds are crossed.

## 4. CLINICAL & DISEASE ENGINE
* **Chronological State Machine (GMF)**: CURRENTLY IMPLEMENTED.
* **Comorbidities & Disease Interactions**: PARTIALLY IMPLEMENTED. Diseases can interact via shared attributes (e.g. HIV reduces immunity attribute, TB triggers faster).
* **Direct Module-to-Module Triggers (CallSubmodule)**: MISSING (RECOMMENDED).
* **Treatment Response & Recovery**: CURRENTLY IMPLEMENTED.
* **Disease Progression**: CURRENTLY IMPLEMENTED.

## 5. HEALTHCARE WORLD (FACILITIES & PROVIDERS)
* **Real Facility Mapping**: MISSING (ESSENTIAL). Encounters currently happen in a void. A mature engine loads the Nigeria Health Facility Registry (NHFR) and routes patients to actual PHCs or General Hospitals based on GPS proximity to their LGA.
* **Provider Assignment**: MISSING (OPTIONAL).

## 6. CARE-SEEKING & SOCIOECONOMICS
* **Socioeconomic Status (SES) / Poverty Modeling**: MISSING (ESSENTIAL). Needs NBS poverty metrics.
* **Care-Seeking Delays**: MISSING (ESSENTIAL). Currently, diseases trigger encounters immediately. In reality (especially in Nigeria), care is often delayed due to cost or distance. 
* **Insurance & Financial Modeling**: MISSING (RECOMMENDED). Out-of-pocket tracking vs NHIA coverage.

## 7. DATA ARCHITECTURE & OUTPUTS
* **CSV/JSON/FHIR R4**: CURRENTLY IMPLEMENTED.
* **CLI Flexibility**: CURRENTLY IMPLEMENTED (Highly flexible targeting, grouping, isolation).
* **Streaming Generation**: MISSING (RECOMMENDED). The engine currently holds all patients in RAM until export. To generate 10M+ patients, it must yield and flush to disk continuously.
* **Clinical Notes Exporter (Text)**: MISSING (OPTIONAL).

## 8. VALIDATION
* **Internal Demographic Consistency**: CURRENTLY IMPLEMENTED.
* **FHIR Referential Integrity**: CURRENTLY IMPLEMENTED.

