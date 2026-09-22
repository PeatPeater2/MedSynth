# Neonatal Disorders Module

## Scope
- **Definition**: Conditions occurring strictly within the first 28 days of life (the neonatal period).
- **Included conditions**: Prematurity (complications of preterm birth), Neonatal Sepsis, and Birth Asphyxia. These three represent the vast majority of infectious and intrapartum-related mortality for Nigerian neonates.
- **Excluded conditions**: LRI (handled by the LRI module explicitly), Congenital anomalies (unsupported data density natively without fabricating complex maternal linkages), and Jaundice (often benign or overlapping with prematurity without intensive data representation).

## Evidence & Data Sources
- **Source**: NDHS (Nigeria Demographic and Health Survey) 2018 & UNICEF Neonatal Mortality Data 2021.
- **URL**: https://data.unicef.org/
- **Nigerian Epidemiology**: Neonatal Mortality Rate (NMR) is ~34 per 1,000 live births (3.4%).
- **Data Classification**: 
  - `OBSERVED_SOURCE_DATA` for incidence vectors: Prematurity (~12%), Sepsis (~1.5%), Asphyxia (~1.5%).
  - `MODELLED_DATA` for case-fatality rates mapped dynamically to hit the 3.4% NMR target across the generated cohort.
  - `DATA_UNAVAILABLE`: Maternal-dependent risk factors (e.g., mother's HIV status or antenatal care frequency) cannot be modeled because the generator does not spawn parent/child linked graphs. Gestational age weeks are also excluded; prematurity is modeled purely as an acute categorical event.

## Clinical Pathway
- **Birth Integration**: Evaluated exactly at birth (`Initial` state) and hard-locked by a strict `< 28 days` age validation gate to guarantee chronological accuracy. 
- **Risk Factors**: Implicitly handled via population incidence (15% overall morbidity split across the three branches). 

### Prematurity
- **Diagnosis**: Premature birth of newborn.
- **Treatment/Care**: NICU inpatient admission. Followed for 28 days.
- **Mortality**: 10% case fatality (highest volume cause of death).

### Neonatal Sepsis
- **Diagnosis**: Neonatal sepsis (via Blood Culture observation).
- **Treatment/Care**: Ampicillin (RxNorm 733).
- **Mortality**: 15% case fatality (highest intensity cause of death).

### Birth Asphyxia
- **Diagnosis**: Birth Asphyxia.
- **Treatment/Care**: Neonatal Resuscitation Care Plan (SNOMED 3130004).
- **Mortality**: 30% case fatality (highest severity cause of death).

## Limitations
1. Maternal Dependency is unsupported by the current patient model architecture.
2. Only tracks discrete conditions; long-term cognitive delays resulting from Asphyxia are bypassed to keep the timeline focused on the acute 28-day window.

