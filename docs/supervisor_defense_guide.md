# Supervisor Defense Guide (Viva Prep)

This document is designed to prepare Peter Aderinto (PEAT PEATER) to verbally defend the architecture, decisions, and capabilities of MedSynth during a university defense or technical assessment.

---

### Q: What is MedSynth?
**Short answer:** It is a synthetic patient generator explicitly contextualised for Nigeria.
**Technical answer:** It is a stochastic, state-machine driven simulation engine written in Python that generates mathematically realistic but completely synthetic electronic health records (EHRs) in CSV and HL7 FHIR formats.
**Why it matters:** It solves the data scarcity and privacy bottlenecks in African health-tech.

### Q: Why use JSON for disease modules instead of writing them in Python?
**Short answer:** It separates medical logic from computer science.
**Technical answer:** Using the Generic Module Framework (GMF), diseases are represented as declarative JSON state machines. This allows a doctor or epidemiologist to write or modify a disease's clinical progression (e.g., adding a new symptom) without needing to understand Python or touch the core engine code.

### Q: Why are `Patient` and `HealthRecord` separate objects in the code?
**Short answer:** Biology is different from paperwork.
**Technical answer:** The `Patient` object tracks the biological ground-truth (e.g., the patient was just infected with Malaria). The `HealthRecord` tracks clinical discovery. The disease is not added to the `HealthRecord` until the patient physically travels to a hospital and a doctor logs an `Encounter` state.

### Q: How does Streaming reduce RAM usage?
**Short answer:** It processes one person at a time instead of holding a million people in memory.
**Technical answer:** Standard generation appends patients to a massive array (`list.append(patient)`), which crashes the RAM at around 1-2 million patients. MedSynth uses Python generator functions (`yield`). The CLI consumes the patient, writes them to disk, and allows the Python Garbage Collector to immediately destroy the object. Memory usage remains a flat ~250MB regardless of scale.

### Q: If Python is single-threaded due to the GIL, how did you make MedSynth use multiple CPU cores?
**Short answer:** By using distinct processes instead of threads.
**Technical answer:** The Global Interpreter Lock (GIL) prevents threads from executing simultaneously. I bypassed this by using `concurrent.futures.ProcessPoolExecutor`, which spawns entirely separate OS-level Python processes, allowing true parallel CPU execution for massive populations.

### Q: How do you guarantee the data is reproducible?
**Short answer:** I pre-generate a master list of random seeds before generation starts.
**Technical answer:** I don't share one random number generator across multiple processes (which would cause race conditions). Instead, the master process generates an array of N unique deterministic seeds (`seeds[i]`). Each patient is instantiated with their specific seed. Whether Patient #500 is generated on CPU core 1 or CPU core 8, their biological outcome is identical every time.

### Q: How do you prevent the JSON/FHIR file from crashing the system when it gets too large?
**Short answer:** Chunking.
**Technical answer:** A standard JSON file must be fully parsed into memory to be valid. A 20GB FHIR file would crash any text editor or database loader. MedSynth's `FHIRExporter` automatically tracks resource limits and chunks the output into multiple sequential files (`bundle_00000.json`, `bundle_00001.json`).

### Q: How does your socioeconomic care-seeking model work?
**Short answer:** Poor patients wait longer to go to the hospital.
**Technical answer:** The `demographics.py` engine assigns an NDHS Wealth Quintile (1-5). In the `malaria.json` state machine, I implemented a `Guard` state. If `@patient.wealth_quintile == 1` (poorest), the state machine routes them to a 2-4 day `Delay` node before triggering the `Encounter`. This accurately models the out-of-pocket financial barrier to healthcare in Nigeria.

### Q: How would you generate 50 million patients?
**Short answer:** I wouldn't do it on my laptop.
**Technical answer:** Architecturally, MedSynth can generate 50 million patients on a laptop because the streaming pipeline bounds the RAM to 250MB. However, due to Python IPC (Inter-Process Communication) overhead, it would take ~17 days of continuous CPU time. To generate 50M efficiently, I would containerize the generator in Docker and deploy it across a distributed Kubernetes cluster or Apache Spark infrastructure.

