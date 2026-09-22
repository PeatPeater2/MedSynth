# Data Provenance

MedSynth is only as realistic as its underlying data. This document outlines the exact sources of the external datasets used to anchor the synthetic population in Nigerian reality.

### 1. Healthcare Facilities (`nigeria_facilities.csv`)
* **Source:** Humanitarian Data Exchange (HDX) / eHealth Africa
* **Year:** ~2019-2022
* **Geographic resolution:** Point coordinates (Lat/Lng), mapped to LGA and State.
* **Population:** 46,146 verified Nigerian healthcare facilities.
* **Purpose:** To anchor patient clinical encounters to real physical buildings (Primary Health Care Centers, General Hospitals, Teaching Hospitals).
* **Observed/Derived/Modelled:** **Observed.** The facility IDs, names, and coordinates are real.

### 2. State Populations (`state_population.csv`)
* **Source:** National Bureau of Statistics (NBS) Nigeria
* **Year:** 2006 (Base census) + Demographic projections.
* **Geographic resolution:** State level.
* **Purpose:** To weight patient generation. MedSynth will generate more patients in Kano and Lagos than in Bayelsa, reflecting actual population density.
* **Observed/Derived/Modelled:** **Modelled.** Based on NBS projections from the last official census.

### 3. Socioeconomics / Wealth Quintiles (`demographics.py`)
* **Source:** Nigeria Demographic and Health Survey (NDHS)
* **Year:** 2018 / 2023-24
* **Purpose:** Assigning a `wealth_quintile` (1-5) to patients to drive care-seeking delays (poverty barriers).
* **Observed/Derived/Modelled:** **Modelled.** The quintiles are distributed evenly across the population mathematically in accordance with NDHS methodology.

### 4. Names (`hausa_names.csv`, `yoruba_names.csv`, etc.)
* **Source:** Compiled from various open-source African name databases and linguistic lists.
* **Purpose:** Providing culturally accurate first and last names based on geographic region (e.g., heavily weighting Hausa names in Northern states).
* **Observed/Derived/Modelled:** **Derived.** The names themselves are real, but their assignments and combinations are entirely synthetic.

### 5. Physiology / Vitals (`physiology.py`)
* **Source:** World Health Organization (WHO) Growth Standards / CDC Growth Charts.
* **Purpose:** Generating baseline Height, Weight, and BMI curves that grow correctly from infancy to adulthood.
* **Observed/Derived/Modelled:** **Modelled.** The trajectories follow mathematically smoothed Z-score approximations of WHO data.

### Unverified / Unavailable Data
* **Provider (Doctor/Nurse) Rosters:** There is no public, up-to-date database of all clinicians working in all 46,000 facilities. Therefore, Practitioner names and IDs will be purely synthetic in future updates.
* **Financial Costs:** Accurate out-of-pocket costs for every medical procedure in Nigeria are highly volatile and largely unavailable in structured formats. Cost modelling is currently omitted.

