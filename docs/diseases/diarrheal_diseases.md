# Diarrheal Diseases Module

## Scope
- **Definition**: Acute watery diarrhea and severe secretory diarrhea (Cholera).
- **Included conditions**: Acute diarrhea, Mild Dehydration, Severe Dehydration, Cholera.
- **Excluded conditions**: Dysentery (bloody diarrhea) is omitted as a discrete pathway due to overlapping treatment parameters and lack of granular differential prevalence; Chronic diarrhea (like inflammatory bowel disease) is excluded.

## Evidence & Data Sources
- **Source**: NDHS (Nigeria Demographic and Health Survey) 2018. WHO guidelines on diarrheal disease management.
- **URL**: https://www.who.int/
- **Nigerian Epidemiology**: Extremely high incidence in U5 children. Over 10% 2-week prevalence translates to multiple episodes per year per child.
- **Data Classification**: 
  - `OBSERVED_SOURCE_DATA` for demographic age skew (Children >> Adults) and standard ORS+Zinc intervention strategies.
  - `MODELLED_DATA` for exact fractional breakdown of severity (80% mild, 15% moderate, 4% severe, 1% cholera proxy).
  - `DATA_UNAVAILABLE`: Environmental WASH (Water, Sanitation, Hygiene) indicators cannot be modeled dynamically at the household level. Malnutrition z-scores are also unrepresented natively in the patient demographic pool.

## Clinical Pathway
- **Risk Evaluation**: Evaluated annually. Under-5s have an 80% chance per year of an acute episode; everyone else has a 20% chance.
- **Severity Branches**:
  - **Mild (80%)**: Acute diarrhea with no clinical dehydration. Managed ambulatory with Oral Rehydration Therapy (ORT). If U5, Zinc is additionally ordered.
  - **Moderate (15%)**: Acute diarrhea with mild clinical dehydration (SNOMED 2609003). Managed identically to mild, but with slightly longer clinical recovery delay.
  - **Severe (4%)**: Severe dehydration (SNOMED 44142007) prompting Emergency admission. Managed with IV Fluids (RxNorm 1049221). 5% case-fatality rate.
  - **Cholera (1%)**: Epidemic-level secretory diarrhea mimicking severe dehydration. Prompts Emergency admission, IV Fluids, and Doxycycline (antibiotic therapy). 10% case-fatality rate.

## Health Record Integrations
- **Encounters**: Ambulatory (Mild/Mod) vs Emergency (Severe/Cholera).
- **Conditions**: Acute diarrhea, Mild dehydration, Severe dehydration, Cholera.
- **Medications**: Zinc, Intravenous Fluids, Doxycycline.
- **Care Plans**: Oral Rehydration Therapy.

## Limitations
- **Antibiotic Usage**: Arbitrary antibiotic abuse (a massive problem in Nigeria for mild diarrhea) is not explicitly modeled; the engine models the *clinical ideal* (ORT + Zinc for mild cases, Antibiotics strictly reserved for Cholera).
- **WASH / Environment**: Lack of environmental hazard layers means the disease is distributed randomly across demographics without grouping by slum/rural clustering.

