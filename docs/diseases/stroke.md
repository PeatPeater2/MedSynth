# Stroke Module

## Scope
- **Definition**: Cerebrovascular accidents encompassing acute neurological deficits.
- **Included conditions**: Ischemic Stroke (75%) and Hemorrhagic Stroke (25%).
- **Excluded conditions**: TIA (Transient Ischemic Attack) is not explicitly modeled as a discrete precursor in this iteration to keep the acute pathway focused on major stroke events.

## Evidence & Data Sources
- **Source**: IHME Global Burden of Disease (Nigeria, 2019), WHO Global Health Observatory, and Nigerian hospital-based registries.
- **URL**: https://www.healthdata.org/
- **Nigerian Epidemiology**: Stroke incidence in Nigeria is approx. 70 per 100,000 person-years, with a stark skew toward adults >40 and skyrocketing in populations >65.
- **Data Classification**: 
  - `OBSERVED_SOURCE_DATA` for subtype distribution (Ischemic ~75%, Hemorrhagic ~25%).
  - `MODELLED_DATA` for exact age-gated annual probabilities to approximate the 70/100k target across a simulated lifecycle pool (e.g., heavily weighting patients >65).
  - `DATA_UNAVAILABLE`: Hypertension and Diabetes, while the largest known risk factors in Nigeria, are currently unrepresented in MedSynth's demographic attributes as standalone chronic conditions. Thus, risk is strictly approximated via Age. State-by-state geographic variations in stroke incidence are also unavailable.

## Clinical Pathway
- **Risk Evaluation**: Evaluated annually. <40 years: practically 0. 40-65 years: moderate risk. >65 years: high risk.
- **Onset**: Acute symptom presentation (Sudden weakness) prompting an Emergency Room encounter.
- **Diagnosis**: Patients undergo a CT scan of the head (SNOMED 418196008) which determines the subtype.
- **Ischemic Stroke (75%)**:
  - **Treatment**: Aspirin (RxNorm 1191).
  - **Mortality**: 30% 30-day case fatality rate (reflecting high acute mortality in Nigerian settings).
  - **Recovery**: Survivors receive a physical therapy CarePlan.
- **Hemorrhagic Stroke (25%)**:
  - **Treatment**: General stroke management (supportive/surgical proxy).
  - **Mortality**: 45% 30-day case fatality rate (hemorrhagic strokes carry significantly worse prognosis).
  - **Recovery**: Survivors receive a physical therapy CarePlan.

## Health Record Integrations
- **Encounters**: Emergency admission.
- **Conditions**: Cerebrovascular accident (parent code), Ischemic stroke, Hemorrhagic stroke.
- **Procedures**: Computed tomography of head.
- **Medications**: Aspirin.
- **Care Plans**: Stroke management, Physical therapy procedure.
- **Timeline**: Stroke operates as an acute 30-day episode. Upon surviving the 30-day window, the acute condition ends, and the patient re-enters the annual exposure loop (representing risk of recurrent strokes).

## Limitations
- **Hypertension & Diabetes**: Not modeled. Risk relies solely on Age.
- **Rehabilitation Nuance**: Physical therapy is applied generically as a single CarePlan; precise modified Rankin Scale (mRS) disability scoring is not dynamically mapped.

