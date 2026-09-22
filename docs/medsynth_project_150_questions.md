# MEDSYNTH PROJECT DEFENSE & SOFTWARE ENGINEERING (150 QUESTIONS)

## A. PROJECT PURPOSE (10)
1. [EASY] What is MedSynth?
2. [EASY] What problem does MedSynth solve?
3. [MEDIUM] Why is synthetic healthcare data useful compared to de-identified real data?
4. [MEDIUM] Why was Nigeria specifically selected as the target context?
5. [MEDIUM] Who are the intended end-users of this system?
6. [MEDIUM] What are the current clinical limitations of MedSynth?
7. [HARD] What distinguishes MedSynth from a simple random number generator attached to an Excel sheet?
8. [HARD] Why didn't you just use Synthea and change the names to Nigerian ones?
9. [HARD] How does MedSynth handle the balance between medical realism and computational efficiency?
10. [EXPERT] Can synthetic data be used to train AI models for diagnosis? Why or why not?

## B. ARCHITECTURE (20)
11. [MEDIUM] Describe the entire data flow from CLI to FHIR output.
12. [MEDIUM] Why does the Generator exist as a separate class from Patient?
13. [MEDIUM] What calls the GMF state machine?
14. [HARD] What does the state machine call during processing?
15. [HARD] What happens to the system if the CLI component is removed?
16. [HARD] Where exactly does external CSV data enter the system?
17. [HARD] Where does the final processed data leave the system?
18. [HARD] Why is separating the HealthRecord from the Patient a good architectural choice?
19. [EXPERT] Where are the boundaries between demographics, geography, and clinical simulation?
20. [EXPERT] Why is a Generic Module Framework (GMF) preferable to hardcoding Python functions for every disease?
21-30. [VARIOUS] (Deep dives into why specific folders and scripts exist, why JSON was chosen over XML, and why external datasets are separated from logic).

## C. PATIENT MODEL (10)
31. [MEDIUM] How is a patient's identity initially constructed?
32. [MEDIUM] How does age advance in the simulation?
33. [HARD] Where is the patient seed used, and why is it attached to the patient object?
34. [HARD] How do attributes change dynamically during a disease progression?
35-40. [VARIOUS] (Questions on birth date calculations, UUIDs, and attribute inheritance).

## D. DEMOGRAPHICS (10)
41. [HARD] Why is a Yoruba name allowed to be assigned to a patient in Kano?
42. [HARD] Why shouldn't geography strictly hard-restrict someone's name?
43. [EXPERT] How do you distinguish observed data (from NBS) from modelled data (like Zipfian distributions) in your architecture?
44-50. [VARIOUS] (Questions on ethnic modeling, age distributions, and data limitations).

## E. GEOGRAPHY (10)
51. [MEDIUM] How does the system ensure an LGA genuinely belongs to a target state?
52. [HARD] What happens when city-level data is unavailable in the CSV?
53. [EXPERT] Why shouldn't you fabricate LGA-level disease prevalence if the data only exists at the state level?
54-60. [VARIOUS] (Questions on population weights, urban vs rural, and geographic hierarchy validation).

## F. DATASETS & PROVENANCE (15)
61. [HARD] Where exactly did the demographics data come from?
62. [HARD] Why was that specific source chosen?
63. [EXPERT] Explain the journey of a single statistic: Source -> Dataset -> Loader -> Model -> Generator -> Patient.
64-75. [VARIOUS] (Interrogation on data year, resolution limitations, derived vs observed values, and licensing).

## G. DISEASE SYSTEM (25)
76. [HARD] How exactly is a disease probability evaluated against a patient?
77. [HARD] How does age influence disease onset in the GMF?
78. [EXPERT] How does one disease (like HIV) influence another (like TB)?
79. [EXPERT] What happens when a disease module attempts to trigger a medication that is out of stock? (Wait, does MedSynth support this?)
80. [EXPERT] How is Malaria modeled differently from Sickle Cell Disease?
81-100. [VARIOUS] (Specific deep-dives into conditions, progression, recovery, relapse, mortality, and the difference between chronic and acute simulation).

## H. GMF / STATE MACHINE (20)
101. [HARD] What happens when a Guard evaluation fails?
102. [HARD] How does a Delay state manipulate the simulation time clock?
103. [EXPERT] Explain how a ConditionalTransition differs from a DistributedTransition.
104-120. [VARIOUS] (Questions on Initial/Terminal states, encounters, death triggers, CallSubmodule limitations, and state resolution).

## I. SIMULATION / TIME (10)
121. [HARD] How is chronology maintained when multiple diseases are simulating simultaneously?
122. [EXPERT] What happens if an event is scheduled to occur after the patient's death?
123-130. [VARIOUS] (Questions on birth/aging loops, time leaps, and causality).

## J. HEALTH RECORD & EXPORTERS (10)
131. [HARD] How are encounters linked to conditions and medications in FHIR R4?
132. [EXPERT] Why FHIR R4 instead of DSTU2?
133-140. [VARIOUS] (Questions on UUID referential integrity, JSON vs CSV flat output, and clinical notes).

## K. SOFTWARE ENGINEERING (10)
141. [HARD] Which component in MedSynth has the highest coupling, and why?
142. [HARD] How is technical debt managed in the current iteration?
143. [EXPERT] If you had to scale this to 10 million patients in a cloud environment, what is the first architectural bottleneck you would hit?
144-150. [VARIOUS] (Questions on logging, version control, refactoring boundaries).

## L. HOSTILE EXAMINER & WHAT IF (30+)
151. If I delete main.py, can MedSynth still function?
152. Show me where time actually advances in the code.
153. What prevents a patient from receiving treatment before diagnosis?
154. If I change one dataset value, which components change downstream?
155. If I remove FHIR export, does disease generation still work?
156. Why can two patients receive the same name?
157. What if Nigeria adds a new state?
158. What if 1 million patients are requested right now?
159. What if the user requests a disease that isn't loaded?
160. Can a perfectly functioning simulator produce medically wrong data?
161. Why doesn't passing a unit test prove epidemiological validity?
