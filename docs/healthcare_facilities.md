# Nigerian Healthcare Facility Integration

MedSynth integrates official Nigerian health facility data to ensure patients receive care at geographically authentic real-world locations.

## Data Source & Provenance

* **Source**: Humanitarian Data Exchange (HDX) / eHealth Africa
* **Dataset Name**: Nigeria - Healthsites
* **URL**: [HDX Nigeria Health Facilities Dataset](https://data.humdata.org/dataset/nigeria-health-facilities)
* **Access Date**: 2026-08-29
* **Data Scale**: 46,146 verified health facilities

### Data Model & Classification

The facility layer uses an observed and explicit subset of the HDX feature properties:

* **Observed Fields**: `facility_id`, `facility_name`, `facility_type`, `category`, `state`, `lga`, `latitude`, `longitude`.
* **Modelled / Derived Fields**: 
  * `ownership`: Defaulted to `DATA_UNAVAILABLE` unless inferred from explicit facility categories like "Private Hospital" or "Military".

### Schema
```python
class Facility:
    id: str
    name: str
    type: str          # Primary, Secondary, Tertiary
    category: str      # General Hospital, Primary Health Center, etc.
    ownership: str     # Public, Private, DATA_UNAVAILABLE
    state: str
    lga: str
    latitude: float
    longitude: float
```

## Geographic Integration & Assignment

Facilities are natively integrated into MedSynth's `State -> LGA` hierarchical geography.

### Patient Assignment

Patients are dynamically assigned a **Primary Facility** based on their spatial location:
1. **Modelled Assignment**: MedSynth attempts to assign a random facility located in the exact same **LGA** as the patient.
2. **Fallback**: If the specific LGA contains no mapped facilities, MedSynth assigns a random facility within the same **State**.

*Note: Assignment currently uses uniform random LGA mapping rather than distance-based mapping since patients do not yet possess individual physical coordinate properties, only LGA boundaries.*

## Export Implementations

1. **CSV**: Extends `encounters.csv` with `FACILITY_ID` and `FACILITY_NAME` columns.
2. **JSON/JSONL**: Serializes `facility_id` and `facility_name` into `encounter` objects.
3. **FHIR R4**: 
   * `Encounter.location` array is populated with a FHIR `Location` reference.
   * Format: `{"reference": "Location/<uuid>", "display": "<facility_name>"}`

## Limitations & Future Extensions

1. **Provider Data**: Doctors, nurses, and explicit organizational hierarchies are currently `DATA_UNAVAILABLE` and omitted rather than fabricated.
2. **Spatial Routing**: Patient assignment relies on LGA intersection rather than strict Haversine coordinate distances.
3. **Capacity Constraints**: Facilities currently have infinite capacity and do not reject patients based on overcrowding.

