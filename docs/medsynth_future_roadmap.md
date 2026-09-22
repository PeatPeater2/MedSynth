# MedSynth Future Roadmap

This roadmap organizes future development based on strict architectural dependencies. Features cannot be added randomly; they must respect the underlying engine capabilities.

## Phase 1: The Clinical Workforce (Next Immediate Step)
* **Provider Generation:** Anchor synthetic practitioners (Doctors, Nurses, CHEWs) to the 46k HDX facilities.
* **Specialty Modelling:** Ensure tertiary hospitals receive specialists (Surgeons, OBGYNs) while rural PHCs receive CHEWs.
* **Why it matters:** Allows researchers to analyse Nigerian healthcare workforce density and patient-to-doctor ratios.

## Phase 2: Demographics & Families
* **Maternal Tracking & Pregnancy:** Introduce gestation states, fertility rates, and simulate childbirth/neonatal records.
* **Household/Graph Modelling:** Group independent synthetic patients into localized families sharing a geographic coordinate.
* **Why it matters:** Required to simulate genetic inheritance (Sickle Cell passing from parents) and infectious disease spread (Tuberculosis clusters within a home).

## Phase 3: The Clinical Library Expansion
* **GMF Submodule Support (`CallSubmodule`):** Allow diseases to "call" other diseases to reduce JSON duplication.
* **Non-Communicable Diseases (NCDs):** Build out Hypertension, Diabetes, and Cardiovascular models using Nigerian prevalence data.
* **Maternal Mortality & Sepsis:** Build out complications of pregnancy.

## Phase 4: Extreme-Scale Distribution (Long-Term)
* **Cloud-Scale Generation:** Port the multiprocessing architecture to support distributed generation across Kubernetes clusters or Apache Spark.
* **Why it matters:** A single laptop can theoretically generate 50 Million patients, but it would take ~17 days. Distributed generation is required to compress that to a few hours.

## Phase 5: Financials
* **Out-Of-Pocket Cost Simulation:** Attach synthetic Naira costs to medications and procedures.
* **Catastrophic Health Expenditure:** Model when patients abandon treatment due to poverty.

