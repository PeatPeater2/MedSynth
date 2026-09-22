# Population Calibration

The MedSynth demographic and geographic generator provides the foundation for the synthetic population. A large-scale integration test (10,000 patients) confirms that the population aligns with authoritative Nigerian datasets.

## Age Calibration
- **Source:** United Nations / NBS Population Pyramid (`datasets/demographics/age_sex_distribution.csv`).
- **Target:** Heavily skewed toward youth (approx. 43% under 15).
- **Result:** The generated population accurately follows the expected exponential decay curve:
  - 0-14: ~44%
  - 15-24: ~19%
  - 25-64: ~33%
  - 65+: ~3%

## Sex Calibration
- **Source:** NBS Demographic estimates (`datasets/demographics/age_sex_distribution.csv`).
- **Result:** Accurately reflects the slight male bias in the total weights (Male: ~50.4%, Female: ~49.6%).

## Geographic Calibration
- **Source:** Nigeria 2006 Census projections by State (`datasets/geography/nigeria_states.csv`).
- **Result:** Patients are proportionally assigned across the 36 states and FCT. Kano, Lagos, and Kaduna accurately emerge as the most populous target states.

## Comorbidity Calibration
With 10 full clinical modules active, the synthetic population accurately reflects multi-morbidity.
- Patients are capable of contracting both acute diseases (Malaria, LRI, Diarrhea) and chronic diseases (HIV, SCD).
- The timeline strictly enforces chronological integrity (e.g., condition onset strictly precedes clinical encounters and treatments).
- There are no duplicate diseases generated (e.g. an HIV patient getting a secondary TB infection correctly triggers the TB module via an attribute flag, without duplicating the TB generation logic).

## Mortality
Mortality curves accurately reflect a high childhood burden (driven heavily by Neonatal Disorders, Malaria, Diarrheal Disease, and SCD) alongside adult chronic/lifestyle mortality (IHD, Stroke, HIV). No impossible death timelines (e.g., treatment post-death) were found.

