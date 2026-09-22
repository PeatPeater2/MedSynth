# MedSynth Master Documentation

**Project:** MedSynth  
**Author:** Peter Aderinto  
**Nickname:** PEAT PEATER  

## 1. Project Overview

**What is MedSynth?**  
MedSynth is a synthetic patient and healthcare data generation engine explicitly contextualised for Nigeria. It produces clinically, demographically, and geographically realistic (but entirely fake) electronic health records (EHRs). 

**What problem does it solve?**  
Medical research, software development, and epidemiological modelling in Africa are severely bottlenecked by a lack of access to structured healthcare data. Real patient records are heavily protected by privacy laws (NDPR/HIPAA), fragmented across paper systems, or siloed in proprietary databases. MedSynth solves this by generating statistically accurate, synthetic datasets that can be freely shared without any privacy risks.

**Why Nigeria?**  
Most existing synthetic data generators (like Synthea) are hardcoded to Western contexts (e.g., Massachusetts demographics, US census data, Medicaid). MedSynth specifically models the Nigerian reality: Local Government Areas (LGAs), real Nigerian primary healthcare facilities (PHCs), Nigerian disease burdens (e.g., Malaria, Sickle Cell), and NDHS-based socioeconomics (wealth quintiles driving care-seeking delays).

**Synthetic Patient vs. Synthetic Population**  
* **Synthetic Patient:** A single computational model of a fake human being. They have a name, birthdate, sex, location, and a continuous biological state. Over their lifetime, they may catch diseases, visit hospitals, and eventually die.
* **Synthetic Population:** A large collection of synthetic patients (e.g., 100,000 people) generated such that their aggregate statistics (age distribution, disease prevalence, facility utilization) match real-world Nigerian population metrics.

## 2. Why MedSynth Exists
MedSynth was built to overcome:
* **Privacy Restrictions:** Synthetic data is 100% fake. There is zero risk of leaking Personally Identifiable Information (PII).
* **Research Data Scarcity:** It provides African data scientists with massive datasets (millions of rows) to train machine learning models, test dashboards, and conduct simulated epidemiological studies.
* **Software Interoperability:** It exports standard HL7 FHIR R4 resources, allowing Nigerian health-tech developers to test their EHR systems with realistic scale.

## 3. The Patient Lifecycle
When MedSynth generates a patient, the system follows a strict computational lifecycle:

1. **Population Request:** The user requests `N` patients via the CLI.
2. **Birth & Demographics:** A `Patient` object is instantiated. They are assigned a sex and an age (extrapolated back to a birth date) based on Nigerian demographic distributions.
3. **Geography & Identity:** The patient is mapped to a specific State and LGA (e.g., Lagos -> Ikeja). They receive a culturally appropriate name based on ethnic prevalence.
4. **Socioeconomics:** They are assigned a wealth quintile (1-5) and insurance status probability (NHIA).
5. **Facility Assignment:** The Generator anchors the patient to a real physical hospital/clinic in their LGA from the HDX dataset.
6. **Disease Simulation:** The patient's life runs from birth to the present day. Disease modules (JSON state machines) evaluate if the patient gets sick.
7. **Care-Seeking:** If sick, their wealth quintile determines if they seek immediate care or suffer a delay.
8. **Clinical Events:** They visit the facility. The `HealthRecord` logs the Encounter, Condition, Observations (Vitals), and Medications.
9. **Export:** The patient falls out of scope, their HealthRecord is streamed directly to disk (CSV/JSON/FHIR), and memory is freed.

## 4. HealthRecord Deep Explanation
The `Patient` object represents the *biological* human. The `HealthRecord` represents their *medical paperwork*.

* **Why the separation?** A patient might biologically have an undiagnosed condition. It is a biological reality, but it shouldn't appear on their EHR until a doctor officially diagnoses it during an `Encounter`.
* **Storage:** The `HealthRecord` maintains distinct arrays of objects: `encounters`, `conditions`, `observations` (vital signs), `medications`, and `procedures`.
* **Interaction:** When a JSON disease module reaches an `Encounter` state, it injects an Encounter object into the patient's `HealthRecord`. All subsequent clinical actions (Medications, Observations) are nested under that specific Encounter until the visit ends.

## 5. Extreme-Scale Generation
MedSynth is an "extreme-scale" architecture. It does not buffer patients in RAM.
Instead of: `Generate 1 Million Patients -> Store in RAM -> Export (CRASH)`
MedSynth does: `Generate Patient 1 -> Export -> Delete -> Generate Patient 2...`
Because it utilizes **Streaming Yields** and **Multiprocessing Chunking**, MedSynth can mathematically generate 50 million patients on a standard laptop (given enough time and hard drive space) while never exceeding ~300MB of RAM.

