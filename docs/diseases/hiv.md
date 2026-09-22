# HIV/AIDS Module

## Evidence & Data Sources
- **Source**: UNAIDS 2022 Data & NAIIS 2018 (Nigeria HIV/AIDS Indicator and Impact Survey)
- **URL**: https://www.unaids.org/
- **Nigerian Epidemiology**: ~1.4% prevalence among adults, ~0.034% incidence annually.
- **Classification**: `OBSERVED_SOURCE_DATA` for base incidence rates, `MODELLED_DATA` for exact longitudinal incidence distributions mapping to sex bias (Female > Male > Children).

## Epidemiological Parameters
- **Annual Incidence**: Modelled at 0.04% (F), 0.02% (M), 0.005% (Children) to approximate UNAIDS new infection targets longitudinally over patient lifespan.
- **Geography**: `DATA_UNAVAILABLE` for granular state-level differences natively inside the GMF; uses national demographic averages to distribute cases.

## Clinical Assumptions
- **Transmission**: Partner networks are `DATA_UNAVAILABLE`. Modeled probabilistically as an annual exposure risk.
- **Acute Phase**: Bypassed straight to chronic infection modeling, as acute symptomatic presentation is highly variable and often missed clinically.

## Diagnostics & Care
- **Delay to Diagnosis**: Modeled 1-3 years undiagnosed phase representing real-world lag.
- **Testing**: Ambulatory encounter leading to HIV 1+2 Ab Rapid Test (LOINC 80231-4).
- **Care Entry**: Initiates HIV Care Program (SNOMED 385966005).

## Treatment & Monitoring
- **ART**: Dolutegravir / Lamivudine / Tenofovir (RxNorm 2123111). Standard Nigerian first-line.
- **Monitoring Loop**: Assessed every 6 months via Viral Load (LOINC 25835-1).
- **Suppression**: 89% remain suppressed, 10% failing, 1% progress to AIDS per loop.

## Progression & Mortality
- **AIDS Progression**: ConditionOnset (SNOMED 62479008).
- **AIDS Mortality**: If progressed, mortality occurs within 1-3 years.

## Cross-Disease Interactions
- **Tuberculosis**: HIV acts as a massive risk multiplier for TB. If the patient has the `hiv_positive` attribute set, TB incidence transitions dramatically spike to 5% annually, overriding baseline epidemiological probabilities.

