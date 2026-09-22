# Lower Respiratory Infections (LRI) Module

## Evidence & Data Sources
- **Source**: WHO Global Health Observatory & UNICEF (2022)
- **URL**: https://data.unicef.org/topic/child-health/pneumonia/
- **Nigerian Epidemiology**: LRI is the leading infectious cause of U5 mortality. Incidence is highly skewed toward neonates and children under 5.
- **Classification**: `OBSERVED_SOURCE_DATA` for incidence distribution weighting toward U5. `MODELLED_DATA` for precise annual fractions tracking longitudinal lifespan risk.

## Definition
- **Represents**: Acute lower respiratory tract infections, primarily clinical pneumonia (viral and bacterial) and bronchiolitis.
- **Does Not Represent**: Upper respiratory infections (common cold), asthma, or chronic COPD.

## Epidemiological Parameters
- **Annual Incidence**: 
  - U5s (<5): 20%
  - Older Children (<15): 5%
  - Elderly (>=65): 10%
  - Adults (15-64): 3%
- **Geography**: `DATA_UNAVAILABLE` for granular state-level differences natively inside the GMF; uses national demographic averages.
- **Sex**: Uniform. No explicit biological sex difference applied as evidence points more heavily to environmental (indoor pollution) and nutritional factors than inherent sex traits.

## Clinical Assumptions
- **Acute Phase**: LRI is an acute episode lasting 1-2 weeks. It evaluates annually over the lifespan, meaning patients can have dozens of mild episodes throughout their life.

## Severity & Pathway
- **Mild (80%)**: 
  - Represents viral pneumonia or bronchiolitis. 
  - Symptom: Cough.
  - Encounter: Ambulatory.
  - Treatment: Supportive care.
  - Outcome: 100% recovery.
- **Severe (20%)**:
  - Represents bacterial pneumonia.
  - Symptom: Difficulty breathing (Danger sign).
  - Encounter: Emergency room admission.
  - Diagnosis: Chest X-ray.
  - Treatment: Amoxicillin (Standard first-line antibiotic, RxNorm 723).
  - Outcome: 95% recovery, 5% mortality.

## Cross-Disease Interactions
- **HIV**: HIV+ patients have compromised immune systems, making them highly susceptible to opportunistic bacterial pneumonias. If `hiv_positive == true`, the annual LRI incidence overrides demographic defaults and spikes to 25%.
- **Tuberculosis differentiation**: TB is chronic (months of prolonged cough), while LRI is acute (weeks of cough/fever). Both operate independently and do not conflict within the HealthRecord timeline.

## Limitations
- State-by-state geographic gradients are unavailable without demographic remodeling.
- Antibiotic resistance (e.g., to Amoxicillin) is not modeled due to a lack of precise longitudinal resistance probability matrices for the general outpatient Nigerian population.

