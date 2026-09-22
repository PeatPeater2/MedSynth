# Synthea Component Map

| Synthea Component | Source Class/File | MedSynth Equivalent | Decision | Reason | Dependencies | Status |
| ----------------- | ----------------- | ------------------- | -------- | ------ | ------------ | ------ |
| **GMF States** | | | | | | |
| Initial | `State.java` | `Initial` (`state.py`) | PORT FAITHFULLY | Required entry point for generic modules. | None | Pending |
| Terminal | `State.java` | `Terminal` (`state.py`) | PORT FAITHFULLY | Required exit point for generic modules. | None | Pending |
| Simple | `State.java` | `Simple` (`state.py`) | PORT FAITHFULLY | Basic pass-through state. | None | Pending |
| Delay | `State.java` | `Delay` (`state.py`) | PORT FAITHFULLY | Simulation time advancement. | None | Pending |
| Guard | `State.java` | `Guard` (`state.py`) | PORT FAITHFULLY | Blocking state until logic met. | Logic | Pending |
| SetAttribute | `State.java` | `SetAttribute` (`state.py`) | PORT FAITHFULLY | Storing variables on patient. | None | Pending |
| Counter | `State.java` | `Counter` (`state.py`) | PORT FAITHFULLY | Tracking counts (e.g. # of treatments). | None | Pending |
| CallSubmodule | `State.java` | `CallSubmodule` (`state.py`) | PORT FAITHFULLY | Module composition and reusability. | Module | Pending |
| Encounter / End | `State.java` | `Encounter` (`state.py`) | PORT FAITHFULLY | Generates health record encounters. | HealthRecord | Pending |
| Condition / End | `State.java` | `ConditionOnset` (`state.py`) | PORT FAITHFULLY | Disease generation. | HealthRecord | Pending |
| Allergy / End | `State.java` | `AllergyOnset` (`state.py`) | PORT FAITHFULLY | Allergy generation. | HealthRecord | Pending |
| Symptom | `State.java` | `Symptom` (`state.py`) | PORT FAITHFULLY | Disease presentation tracking. | HealthRecord | Pending |
| Observation | `State.java` | `Observation` (`state.py`) | PORT FAITHFULLY | Lab values and vitals tracking. | HealthRecord | Pending |
| Procedure | `State.java` | `Procedure` (`state.py`) | PORT FAITHFULLY | Surgeries and interventions. | HealthRecord | Pending |
| Medication / End | `State.java` | `MedicationOrder` (`state.py`) | PORT FAITHFULLY | Treatment tracking. | HealthRecord | Pending |
| CarePlan / End | `State.java` | `CarePlanStart` (`state.py`) | PORT FAITHFULLY | Care management tracking. | HealthRecord | Pending |
| Death | `State.java` | `Death` (`state.py`) | PORT FAITHFULLY | Patient mortality. | HealthRecord, Person | Pending |
| **GMF Transitions** | | | | | | |
| Direct | `Transition.java` | `DirectTransition` | PORT FAITHFULLY | Simple direct edge. | None | Pending |
| Conditional | `Transition.java` | `ConditionalTransition` | PORT FAITHFULLY | Branching based on logic. | Logic | Pending |
| Distributed | `Transition.java` | `DistributedTransition` | PORT FAITHFULLY | Probability-based branching. | None | Pending |
| Complex | `Transition.java` | `ComplexTransition` | PORT FAITHFULLY | Logic + Probability. | Logic | Pending |
| **Core Engine** | | | | | | |
| Generator | `Generator.java` | `Generator` (`generator.py`) | PORT FAITHFULLY | Orchestrates population simulation. | Person, Module | Pending |
| Logic | `Logic.java` | `Logic` (`logic.py`) | PORT FAITHFULLY | Evaluates conditions (Age, Sex, etc). | Person | Pending |
| Person | `Person.java` | `Person` (`patient.py`) | ADAPT FOR NIGERIA | Core identity (stripped of US Census logic). | None | Pending |
| HealthRecord | `HealthRecord.java` | `HealthRecord` (`health_record.py`) | PORT FAITHFULLY | Structured clinical event log. | Person | Pending |
| Location | `Location.java` | `geography.py` | ADAPT FOR NIGERIA | Use Nigeria States, LGAs, Wards. | None | Pending |
| Demographics | `Demographics.java`| `demographics.py` | ADAPT FOR NIGERIA | Use Nigerian names, distributions. | None | Pending |
| **Exporters** | | | | | | |
| CSV Exporter | `CSVExporter.java` | `csv_exporter.py` | PORT FAITHFULLY | Data dump of HealthRecord. | HealthRecord | Pending |
| JSON Exporter | (Custom) | `json_exporter.py` | PORT FAITHFULLY | Direct serialization of internal record. | HealthRecord | Pending |
| FHIR Exporter | `FHIRExporter.java`| `fhir_exporter.py` | PORT FAITHFULLY | Basic R4 representation of clinical history.| HealthRecord | Pending |
| **Removed Features**| | | | | | |
| Physiology | `PhysiologySimulator.java`| None | CUT ENTIRELY | Highly specific bio-simulation; out of scope. | None | Cut |
| US Claims/Billing | `Payer.java` | None | CUT ENTIRELY | US Medicare/Medicaid logic irrelevant. | None | Cut |
| CPT/HCPCS | `Cost.java` | None | CUT ENTIRELY | US billing machinery not requested. | None | Cut |
| CCDA Exporter | `CDAExporter.java` | None | CUT ENTIRELY | Legacy US regulatory format. | None | Cut |
| CMS Reporting | `Quality.java` | None | CUT ENTIRELY | CMS logic irrelevant. | None | Cut |

## Architecture Decisions
1. **State Machine**: The core interpreter (GMF) will be a faithful representation of Synthea's state and transition logic to ensure compatibility with existing generic module configurations, but written idiomatically in Python (e.g., duck-typing instead of heavy Java inheritance trees where appropriate).
2. **Clinical Record**: The `HealthRecord` will maintain relational integrity (an `Encounter` holds a reference or ID connecting it to `Conditions`, `Observations`, etc.), rather than flat lists.
3. **Data Boundary**: Nigerian specific values (Providers, Names, Demographics) will explicitly state if they are `MODELLED_DATA` vs `OBSERVED_SOURCE_DATA`.
4. **Behavioral Quirks**: Synthea's time-travel behavior (where Delays rewind execution to exact times) will be preserved in the `Generator` to ensure precise onset dates.

