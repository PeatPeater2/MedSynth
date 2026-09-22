# Physiology and Vitals

MedSynth incorporates an evidence-based physiology engine designed for massive scalability. It separates *background physiological trajectories* from *clinical observations* to prevent combinatorial explosions of unnecessary data during 50M+ patient runs.

## Core Variables Implemented

* **Height** (cm)
* **Weight** (kg)
* **BMI** (kg/m^2)
* **Blood Pressure** (Systolic/Diastolic mmHg)
* **Heart Rate** (Not fully parameterized yet, reserved for future expansion)
* **Temperature** (°C)
* **Hemoglobin** (g/dL)

## Data Sources & Classification

| Variable | Source / Evidence | Classification |
|----------|-------------------|----------------|
| **Height/Weight** | WHO Child Growth Standards (Under 5), CDC/UK (Older). Correlates with NDHS stunting data. | `MODELLED_DATA` |
| **BMI** | Computed dynamically from Height and Weight | `DERIVED_DATA` |
| **Blood Pressure** | Age-based progression + 30-40% Nigerian adult hypertension prevalence models (Systematic reviews 2018-2023) | `MODELLED_DATA` |
| **Temperature** | Basal + acute disease-driven variations | `MODELLED_DATA` |
| **Hemoglobin** | Baseline WHO anaemia thresholds + SCD/Malaria impacts | `MODELLED_DATA` |

*Note: All physiological profiles are synthetic `MODELLED_DATA` and `DERIVED_DATA`. We do not label these as `OBSERVED_SOURCE_DATA` as they are statistical composites rather than raw anonymized patient EHRs.*

## Age and Sex Modelling

The engine inherently checks `patient.age_in_years` and `patient.age_in_months`.
* **Growth:** Height and weight trajectories scale correctly from neonate (50cm, 3.5kg) through adolescence to adulthood.
* **Sex Differences:** Adult height and weight baselines differ between males and females (e.g., adult male ~170cm, female ~160cm). Hemoglobin baselines also adapt (males 14.5 g/dL vs females 13.0 g/dL).
* **Newborn Safety:** The engine explicitly prevents physiological generation for unborn patients (age < 0).

## Disease Effects on Physiology

The engine dynamically cross-references `patient.record.present_conditions` and `patient.attributes` at the exact moment an observation is required:
* **Malaria:** Acutely raises body temperature by 1-2.5 °C. Acutely lowers hemoglobin.
* **Sickle Cell Disease (SCD):** `HbSS` and `HbSC` genotypes chronically depress baseline hemoglobin by 5.0 and 2.5 g/dL, respectively.

## Performance Strategy

**Architecture:** *On-Demand Observation Generation via Analytical Trajectories*

MedSynth **does not** run a daily simulation loop computing BP and weight for millions of people (which would make 50M-patient targets impossible). 
Instead, the `Physiology` class acts as a continuous mathematical function: `f(age, sex, diseases) = vital_sign`.

The value is ONLY computed and committed to the EHR as an `Observation` when a clinical encounter explicitly requests it (e.g., via the `vital_sign` key in the GMF `Observation` state). 

This guarantees:
1. Valid, age-appropriate vitals at any given second.
2. Zero overhead when the patient is not interacting with the healthcare system.

## Known Limitations

1. **Heart Rate / Respiratory Rate / SpO2:** These require more complex baseline circadian rhythms and exertion models to be useful, and are currently omitted until a specific disease (like LRI) strictly demands them.
2. **Longitudinal smoothing:** Because the RNG is sampled per-encounter, a patient's BP might fluctuate 10 points between two encounters on the same day. True deterministic smoothing (via seeded procedural noise) is not yet implemented.

