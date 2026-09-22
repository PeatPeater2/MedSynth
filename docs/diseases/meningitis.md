# Meningitis Clinical Module

## Overview
This module represents **Bacterial Meningitis** in the Nigerian context. It aligns with the epidemiology of the African "Meningitis Belt," which encompasses the northern states of Nigeria.

## Clinical Scope
- **Included Types:** Bacterial meningitis, specifically acute epidemic presentations (historically Neisseria meningitidis).
- **Excluded Types:** Aseptic (viral) meningitis, fungal meningitis (e.g. Cryptococcal), and chronic tuberculous meningitis are out of scope for this specific pathway, though they may be addressed in other modules (like HIV or TB).

## Epidemiology & Geographic Distribution
Meningitis risk in Nigeria is strongly geographically delineated.
- **Meningitis Belt:** Northern states (Sokoto, Kano, Zamfara, Katsina, Kebbi, Jigawa, Yobe, Borno, Bauchi, Gombe, Adamawa, Taraba, Niger, FCT).
- **Age:** The highest risk is among children under 5, followed by older children and young adults (up to age 25).
- **Seasonality:** The disease is heavily seasonal (dry/harmattan season, Dec-June). *Limitation:* Precise monthly incidence is not supported by the underlying MedSynth core engine, so this is modelled probabilistically on an annual loop instead of forcing seasonal event triggers.
- **Data Provenance:** Incidence and CFR data (~8.5%) are derived from 2024/2025 NCDC outbreak surveillance reports.

## Clinical Pathway
- **Risk Evaluation:** Evaluated annually, with incidence rates vastly higher for patients living in the Meningitis Belt states, especially for those aged <5.
- **Onset:** Presents acutely.
- **Symptoms:** Fever, Headache, Neck stiffness, Photophobia.
- **Encounter:** Emergency room admission.
- **Investigation:** Lumbar puncture (Procedure) and Cerebrospinal fluid analysis (Observation).
- **Treatment:** Empiric Ceftriaxone 1g injection.
- **Outcomes:** 
  - Recovery (81.5%)
  - Sensorineural hearing loss (10%)
  - Death (8.5% Case Fatality Rate).

## Data Types
- **OBSERVED_SOURCE_DATA:** Overall CFR (8.5%) from NCDC.
- **MODELLED_DATA:** State-level distribution logic (approximating the Meningitis Belt vs Non-Belt states).
- **DATA_UNAVAILABLE:** Precise serogroup fractions (MenC vs MenW vs MenX) and monthly environmental multipliers.

