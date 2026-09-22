# Sickle Cell Disease Clinical Module

## Overview
This module models **Sickle Cell Disease (SCD)** in Nigeria, which carries the highest global burden of the disease. The module accurately distinguishes between the sickle cell trait (HbAS) and the disease states (HbSS, HbSC).

## Genetics & Inheritance
Since MedSynth currently generates patients independently without a multi-generational family structure, explicit parental inheritance is not modelled directly. Instead, genotypes are probabilistically assigned at birth based on Nigerian population distributions:
- **HbAA (Normal):** ~68.0%
- **HbAS (Trait/Carrier):** ~25.0%
- **HbSS (SCD):** ~2.5%
- **HbSC (SCD):** ~0.5%
- **HbAC (Trait):** ~4.0%

This accurately replicates a birth prevalence of roughly 2.5% to 3.0% for SCD in Nigeria without fabricating a family tree.

## Epidemiology
- **Disease Prevalence:** ~2.5-3.0% of the population.
- **Trait Prevalence:** ~25%.
- **Mortality:** Very high in children under 5 (approximating historical estimates that 50-90% may die before their 5th birthday if unmanaged). This is modelled via an elevated annual mortality risk (`SCD_Death` transition) in the `<5` age branch.
- **Sex:** Inherited autosomal recessively; affects males and females equally.
- **Geography:** Widespread nationally; no specific regional constraint implemented.

## Trait vs Disease
- **HbAS (Sickle Cell Trait):** These patients receive the genotype attribute but **do not** enter the SCD clinical pathway. They will not experience vaso-occlusive crises or acute chest syndrome from this module.
- **HbSS & HbSC:** These patients enter the SCD clinical pathway at birth.

## Clinical Pathway
- **Chronic Disease:** A `ConditionOnset` of "Sickle cell disease (disorder)" is recorded.
- **Treatment (Hydroxyurea):** Due to known access and cost barriers in Nigeria, Hydroxyurea uptake is modelled at ~15% (`MODELLED_DATA` derived from SPARCO registry estimates).
- **Vaso-occlusive Crises (VOC):** Pain crises occur probabilistically and result in an emergency encounter, analgesia, and a ~15% rate of blood transfusion.
- **Infection Interactions:** The module explicitly listens for the presence of the `Fever` symptom (which could be triggered by the existing Malaria or Meningitis modules). If an infection-driven fever is present, it dramatically increases the probability of a VOC crisis, accurately reflecting how malaria and other infections precipitate SCD crises in Nigeria.
- **Acute Chest Syndrome:** Evaluated as a potential severe complication in patients >5 years, leading to inpatient admission, antibiotics, transfusion, and a high risk of mortality.

## Data Limitations
- **Newborn Screening:** Universal newborn screening is not modelled as it is currently limited to specific pilots in Nigeria.
- **Stroke Interaction:** The existing Stroke module primarily triggers on age and cardiovascular risk factors. Due to engine limitations, a direct programmatic link forcing a stroke specifically from the SCD module without duplicating logic wasn't implemented, though SCD patients can independently suffer strokes if they meet the general module's criteria.

## Data Provenance
- Genotype prevalences and HU coverage are `OBSERVED_SOURCE_DATA` from WHO, NCDC, and SPARCO.
- The infection-triggered crisis mechanism is `CLINICAL_KNOWLEDGE`.

