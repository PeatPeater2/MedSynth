# MedSynth Architecture

This document outlines the technical flow and component hierarchy of the MedSynth engine.

## ASCII Architecture Diagram

```text
                       [ USER CLI ]
                            |
                 medsynth.cli (Entrypoint)
                            |
                     [ Configuration ]
                    (GeneratorOptions)
                            |
                      [ GENERATOR ] <=======================+
                      (Process Pool)                        |
                            |                               |
       +--------------------+--------------------+          | (Modules loaded once)
       |                    |                    |          |
 [ Demographics ]     [ Geography ]       [ Facilities ]    |
  (Age/Sex/SES)      (States/LGAs)      (46k HDX dataset)   |
       |                    |                    |          |
       +--------------------+--------------------+          |
                            |                               |
                       [ PATIENT ]                          |
                   (Biological State)                       |
                            |                               |
          +-----------------+-----------------+             |
          |                                   |             |
   [ Physiology ]                      [ GMF Engine ] <=====+
(Continuous Vitals)                (Generic Module Framework)
          |                                   |
          |                          (Executes JSON Diseases)
          |                                   |
          +-----------------+-----------------+
                            |
                     [ HealthRecord ]
                   (Clinical Paperwork)
                            |
         +------------------+------------------+
         |                  |                  |
      [ CSV ]            [ JSON ]          [ FHIR R4 ]
     Exporter            Exporter           Exporter
         |                  |                  |
         +------------------+------------------+
                            |
                         [ DISK ]
                 (Streamed & Chunked output)
```

## Core Components

### 1. CLI (medsynth.cli)
**Purpose:** The entry point. Parses user arguments, sets up logging, configures the generator, and manages the execution loop.
**Responsibilities:** Handling `--stream`, `--workers`, `--checkpoint-every`. It orchestrates the streaming loop that yields patients and feeds them to the Exporters.

### 2. Generator (`medsynth/generator.py`)
**Purpose:** The factory that orchestrates patient creation.
**Responsibilities:** It loads all geographic, demographic, and facility datasets into memory exactly once. If multiprocessing is enabled, it distributes chunks of patient generation seeds to the `ProcessPoolExecutor`.

### 3. Patient (`medsynth/patient.py`)
**Purpose:** The biological representation of a person.
**Responsibilities:** Holds attributes (age, sex, wealth quintile) and the current biological state of any active diseases. It contains the `HealthRecord`.

### 4. GMF (`medsynth/state_machine.py`)
**Purpose:** The Generic Module Framework engine.
**Responsibilities:** It reads disease models (JSON files) and translates them into executable Python states. It advances the patient through States (Initial, Delay, Guard, Encounter, Terminal) based on clinical logic and probabilities.

### 5. Exporters (`medsynth/exporters/`)
**Purpose:** Translating the internal `HealthRecord` into standard data formats.
**Responsibilities:** 
* **CSV:** Writes flat relational tables.
* **FHIR:** Translates internal objects into HL7 FHIR R4 compliant JSON resources (`Patient`, `Encounter`, `Condition`, `Observation`). Handles chunking (`bundle_0000.json`) to prevent memory crashes on massive files.

