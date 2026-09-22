# Nigerian Data Foundation Sources

This document describes the provenance of the core datasets used in the MedSynth generator to model the Nigerian population accurately without fabricating statistical data.

## 1. Geography
*   **Dataset Title:** Local Government Areas of Nigeria
*   **Organization:** National Bureau of Statistics (NBS) / Open Source Geography datasets
*   **Source:** [Nigerian LGAs JSON](https://raw.githubusercontent.com/xosasx/nigerian-local-government-areas/master/lgas.json)
*   **Classification:** `OBSERVED_SOURCE_DATA`
*   **Geographic Resolution:** State and LGA level
*   **Purpose:** Assigns realistic State and LGA origin to each patient.

## 2. Demographics
*   **Dataset Title:** Nigeria Demographics (Age and Sex Pyramids)
*   **Organization:** CIA World Factbook / World Bank estimates
*   **Source:** [CIA World Factbook Nigeria](https://www.cia.gov/the-world-factbook/countries/nigeria/)
*   **Classification:** `OBSERVED_SOURCE_DATA`
*   **Age/Sex Resolution:** 5-year age bands and binary sex ratios
*   **Purpose:** Ensures the generated population mimics Nigeria's heavy youth tilt.

## 3. Names
*   **Dataset Title:** Nigerian Names Dataset
*   **Organization:** Various cultural dictionaries
*   **Source:** Aggregated common Nigerian names
*   **Classification:** `MODELLED_DATA`
*   **Purpose:** Provides cultural naming conventions spanning major ethnic groups (Hausa, Igbo, Yoruba).
*   **Limitations:** Not a complete exhaustive national census of names.

## 4. Disease Prevalences (Top 10 Catalog)
*   **Dataset Title:** Nigeria Disease Prevalences
*   **Organization:** WHO, IHME, NCDC, NDHS
*   **Classification:** `OBSERVED_SOURCE_DATA`
*   **Purpose:** Outlines the incidence/prevalence metrics used to gate disease onset in clinical modules.

For complete tabular metadata, see `datasets/metadata/data_sources.csv`.

