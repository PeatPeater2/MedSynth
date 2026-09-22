# Tuberculosis Module

## Evidence & Data Sources
- **Source**: WHO Global Tuberculosis Report (2022)
- **URL**: https://www.who.int/teams/global-tuberculosis-programme/tb-reports
- **Nigerian Epidemiology**: ~219 per 100,000 population incidence annually.
- **Data Year**: 2022
- **Classification**: `OBSERVED_SOURCE_DATA` for incidence and treatment success (85%). `MODELLED_DATA` for precise age/sex probability splits.

## Epidemiological Parameters
- **Annual Incidence**: ~0.219% (national average).
- **Sex Breakdown**: Male incidence is higher than female incidence, which is higher than childhood incidence. Modeled as:
  - Adult Male (>=15): 0.30%
  - Adult Female (>=15): 0.18%
  - Children (<15): 0.10%

## Clinical Assumptions
- Simulated as an annual stochastic check (Delay 1 year loop).
- Active TB onset is evaluated directly; Latent TB Infection (LTBI) is currently `DATA_UNAVAILABLE` to represent cleanly in the engine without inflating conditions, so it is bypassed to model only active, symptomatic progression.

## Risk Factors
- **Age**: Yes (stratified <15 and >= 15).
- **Sex**: Yes (stratified M/F for adults).
- **HIV**: `DATA_UNAVAILABLE` (HIV module not yet functional to act as a prereq dependency).

## Symptoms & Diagnosis
- **Symptom**: Prolonged cough (100% chance for active TB cases).
- **Encounter**: Ambulatory checkup.
- **Diagnosis**: Microscopic observation of Sputum by Acid fast stain (LOINC 11545-1).

## Treatment & Outcomes
- **Medication**: Rifampin / Isoniazid / Pyrazinamide / Ethambutol (RxNorm 1147220).
- **Delay**: 6 months (standard short-course therapy).
- **Outcomes**: 85% Treatment Success/Cured (`ConditionEnd`), 10% Persistent/Loss to Follow-up, 5% Death.

## Limitations
1. HIV status is a major risk factor globally and in Nigeria, but HIV/AIDS is not yet a functional MedSynth module, so the HIV interaction cannot be explicitly modeled as a condition prerequisite yet.
2. Latent TB is not represented.
3. TB prevalence gradient across LGAs/States is modeled uniformly across the nation due to unavailable deep spatial data.

