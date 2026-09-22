# Healthcare Access & Socioeconomic Modelling

MedSynth incorporates an evidence-based socioeconomic and healthcare access layer for synthetic Nigerian populations. Rather than applying flat delays to all patients, care-seeking behaviour is explicitly modelled using actual Nigerian evidence.

## Socioeconomic Representation

Following the methodology of the **Nigeria Demographic and Health Survey (NDHS)** and the **National Bureau of Statistics (NBS)**, socioeconomic status is modelled primarily via **Wealth Quintiles**.

* **Categories**: `Poorest`, `Poorer`, `Middle`, `Richer`, `Richest`
* **Distribution**: Evenly distributed (20% each) on a national scale, reflecting standard NDHS stratification.
* **Property**: `wealth_quintile` attached to `Patient.attributes`.

*Note: Individual income/salary amounts are not fabricated, as they are not reliably captured or representative of the informal economy.*

## Health Insurance Coverage

Nigeria's health insurance penetration (primarily NHIA) is extremely low.
* **Overall Coverage**: ~3-5%
* **Distribution**: Coverage is heavily skewed towards formal sector employment and higher wealth quintiles.
* **MedSynth Model**: Probabilistic assignment based on `wealth_quintile`:
  * `Poorest`: 0.5%
  * `Poorer`: 1%
  * `Middle`: 3%
  * `Richer`: 8%
  * `Richest`: 15%
* **Property**: `insurance` attached to `Patient.attributes` (`NHIA` or `None`).

## Care-Seeking Behaviour & Delays

Evidence demonstrates that poverty and Out-of-Pocket (OOP) expenditure are the primary drivers of healthcare delays in Nigeria. 

**Critical Rule:** Delay is NOT universal across all diseases. Care-seeking is modelled **disease-by-disease** within the GMF (Generic Module Framework) using the `Attribute` condition type.

### Example: Malaria Delay Model
NDHS 2018 indicates that approximately **62.1%** of childhood fever/malaria cases experience delayed formal treatment (>24 hours), often relying on self-medication or PMVs (Patent Medicine Vendors) first.

In the `malaria.json` module, this is modelled via a `Care_Seeking_Decision` node:
* **Richest/Richer**: 60-80% probability of prompt formal care (<24 hours).
* **Middle**: 40% probability of prompt care, 60% probability of a short delay (2-4 days).
* **Poorer/Poorest**: 75-85% probability of a long delay (4-7 days).

### Limitations
1. **Distance/Geographic Delays**: MedSynth patients currently only possess LGA-level geographic resolution, not precise GPS coordinates. Therefore, Haversine distance-based care delays are currently `DATA_UNAVAILABLE` and omitted.
2. **Alternative Providers**: Encounters represent formal facility visits. PMV (pharmacy) visits and traditional healer visits are implicitly captured inside the "delay" timeframe but do not yet generate explicit `Encounter` objects.

