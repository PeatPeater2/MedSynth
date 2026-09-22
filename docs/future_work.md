# Future Work & Research Extensions

MedSynth is a highly extensible platform. While the core extreme-scale engine is complete, the following areas represent ambitious research and engineering extensions for future development.

### 1. Maternal Tracking & Pregnancy
* **Concept:** Implementing gestation states, fertility rates, and simulating childbirth to generate linked maternal-neonatal records.
* **Why it matters:** Maternal and infant mortality are critical public health metrics in Africa. Generating realistic maternal complications (e.g., postpartum haemorrhage, pre-eclampsia) is essential for maternal health-tech development.

### 2. Household & Graph Modelling
* **Concept:** Currently, MedSynth generates 1 million independent islands (patients). Graph modelling would link them into households (Parents, Children, Grandparents) sharing a geographic coordinate.
* **Why it matters:** Necessary for simulating genetic inheritance (Sickle Cell passing from parents to children) and localized infectious disease transmission (Tuberculosis, COVID-19 within a home).

### 3. Provider Generation
* **Concept:** Synthesizing a realistic healthcare workforce (Doctors, Nurses, CHEWs) anchored to the 46k physical facilities, complete with MDCN/NMCN synthetic licenses.
* **Why it matters:** Enables health-systems research on patient-to-doctor ratios, workforce deployment, and clinic wait-time simulations.

### 4. Advanced Clinical & Disease Modelling
* **Non-Communicable Diseases (NCDs):** Building complex JSON modules for Hypertension, Diabetes, and Ischaemic Heart Disease (IHD) tailored to Nigerian incidence rates.
* **Clinical Notes / NLP:** Using Generative AI or templates to write unstructured synthetic doctor's notes for every encounter to train medical NLP models.
* **Comorbid Interactions:** Allowing diseases to heavily influence one another (e.g., HIV accelerating Tuberculosis progression).

### 5. Healthcare Financing & Claims
* **Concept:** Moving beyond a boolean "has insurance" check. Attaching synthetic Naira costs to every medication and procedure, generating claims, and tracking Out-of-Pocket (OOP) catastrophic health expenditure.
* **Why it matters:** Essential for health economists modelling Universal Health Coverage (UHC) viability in Nigeria.

### 6. Distributed Cloud Generation
* **Concept:** Refactoring the `ProcessPoolExecutor` to support distributed streaming across a Kubernetes cluster or Apache Spark.
* **Why it matters:** While MedSynth can mathematically generate 50 million patients on a single machine without crashing RAM, the CPU time required (~17 days) makes it impractical locally. Distributed generation would compress this to a few hours.

