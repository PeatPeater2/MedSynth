# Ischemic Heart Disease (IHD) Module

## Scope
- **Definition**: Stable Coronary Heart Disease and Acute Myocardial Infarction.
- **Included conditions**: Ischemic heart disease (stable), Myocardial infarction (acute).
- **Excluded conditions**: Heart failure (as a downstream chronic entity), arrhythmias. 

## Evidence & Data Sources
- **Source**: AHA RACE-Nigeria Registry (Acute Coronary Syndrome in Nigeria, 2020), IHME Global Burden of Disease.
- **URL**: https://www.ahajournals.org/
- **Nigerian Epidemiology**: IHD was historically rare in Nigeria but is rapidly increasing due to epidemiological transition. ACS (Acute Coronary Syndrome) incidence is roughly 59.1 per 100,000 hospitalized adults.
- **Data Classification**: 
  - `OBSERVED_SOURCE_DATA` for Case Fatality: In-hospital mortality for MI in Nigeria is ~8.1%.
  - `MODELLED_DATA` for base prevalence building. Age is heavily weighted to force incidence strictly into the >40 and >65 brackets. The chronic loop contains a 3% annual risk of suffering a severe acute MI.
  - `DATA_UNAVAILABLE`: Hypertension, Diabetes, and Dyslipidemia are unmodeled in the baseline MedSynth demographic architecture, meaning cardiovascular risk is purely age-proxied.

## Clinical Pathway
- **Onset (Stable)**: Upon reaching the risk bracket, patients may develop stable IHD (SNOMED 414545008). 
- **Stable Management**: Addressed via an ambulatory check-up and generic secondary prevention (Aspirin + Atorvastatin). 
- **Acute Myocardial Infarction (AMI)**:
  - Stable IHD patients face a recurring 3% annual risk of experiencing a myocardial infarction.
  - **Symptoms**: Chest pain.
  - **Encounter**: Emergency room admission.
  - **Diagnostics**: Electrocardiogram (ECG) and Troponin laboratory observation.
  - **Mortality**: 8.1% case fatality from the AMI.
  - **Recovery**: Patients surviving the acute 7-day AMI window resolve the acute condition and re-enter the chronic IHD loop.

## Health Record Integrations
- **Encounters**: Ambulatory (Stable), Emergency (AMI).
- **Conditions**: Ischemic heart disease, Myocardial infarction.
- **Observations**: Troponin I (LOINC 10839-9).
- **Procedures**: Electrocardiogram.
- **Medications**: Aspirin, Atorvastatin.
- **Timeline**: Stable IHD is persistent; AMI is acute and recurring.

## Limitations
- **Risk Factors**: Completely lacks the "Big 3" NCD drivers (Hypertension, Diabetes, Smoking) natively, relying on mathematical abstraction of age to generate population density.
- **Revascularization**: Surgical interventions (PCI, CABG) are excluded due to extremely limited availability in typical Nigerian settings, modeling the reality of medical-only management for the vast majority of cases.

