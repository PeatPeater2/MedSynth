# How MedSynth Works (Beginner's Guide)

If you are new to synthetic health data, the codebase can look overwhelming. This guide explains MedSynth using simple analogies.

### 1. The Factory (The Generator)
Imagine MedSynth as a massive factory. The `Generator` (`generator.py`) is the factory floor manager. You tell the manager, "Build me 10,000 people." The manager hires workers (Multiprocessing) to start building them.

### 2. The Blueprint (The Datasets)
Before building a person, the manager looks at a blueprint to ensure the person looks like a real Nigerian. 
* **Geography:** Where do they live? (Lagos, Kano, etc.)
* **Demographics:** Are they male or female? How old are they?
* **Facilities:** What is the nearest hospital to their house?

### 3. The Biological Human (The Patient)
The factory builds the `Patient`. Think of this as the physical, biological body. It has a heart rate, a temperature, and an age.

### 4. The Instruction Manuals (Disease Modules)
Once the person is born, the factory assigns them "Instruction Manuals" (the JSON files in `datasets/diseases/`).
These manuals dictate the rules of life. For example, the `malaria.json` manual says:
1. Every month, roll a dice.
2. If you roll a 6, the patient gets a fever.
3. If the patient is poor, wait 4 days.
4. Go to the hospital.

### 5. The Machine (The GMF)
The patient cannot read the instruction manual themselves. A machine called the **GMF** (Generic Module Framework) reads the JSON manual and forces the biological patient to experience those rules.

### 6. The Medical Diary (HealthRecord)
When the patient gets sick and visits the hospital, the doctor writes it down. This is the `HealthRecord`. 
* **Condition:** "You have Malaria."
* **Observation:** "Your temperature is 39°C."
* **Medication:** "Take this ACT."

### 7. The Translators (The Exporters)
Once the patient dies or reaches the present day, they are finished. But computers cannot read our Python objects. 
The **Exporters** (CSV, FHIR) act as translators. They take the Medical Diary, translate it into standard database tables (CSV) or international healthcare formats (FHIR JSON), and save it to the hard drive. 

Then, the factory deletes the patient to save memory and moves on to the next one!

