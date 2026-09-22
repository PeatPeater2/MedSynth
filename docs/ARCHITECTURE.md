# MedSynth Architecture

## Core Engine Flow

`	ext
User
 ↓
medsynth.bat / CLI
 ↓
Configuration (GeneratorOptions)
 ↓
Population Generator (medsynth/generator.py)
 ↓
Demographics & Geography (medsynth/demographics.py, medsynth/geography.py)
 ↓
Disease / Clinical Modules (JSON files -> medsynth/gmf/)
 ↓
State Machine (Chronological Timeline Simulation)
 ↓
Health Record (medsynth/health_record.py)
 ↓
Export Layer (medsynth/exporters/)
 ↓
CSV / JSON / FHIR R4
`

## Description
MedSynth operates on a modified version of the Generic Module Framework (GMF). Patients are simulated chronologically from birth to death (or present day). During simulation, independent disease modules execute their JSON-defined state machines concurrently, emitting events to the unified HealthRecord which is finally exported.
