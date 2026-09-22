# MEDSYNTH DEVELOPMENT ROADMAP

This roadmap organizes the development of new MedSynth capabilities based on architectural dependencies. 

## PHASE 1: FOUNDATION & OPTIMIZATION
*These must be implemented before complex simulation expansions to ensure the engine doesn't collapse under scale.*
1. **Streaming Generation Engine**: Modify `generator.py` to yield and export patients incrementally to disk, bypassing RAM limits for populations >1,000,000.
2. **GMF Submodule Support**: Implement `CallSubmodule` so diseases can cleanly branch into other diseases.

## PHASE 2: PHYSIOLOGY & DEMOGRAPHICS
*Building biological realism.*
3. **Continuous Vitals Engine**: Implement lifetime background tracking of BMI, Hemoglobin, and Blood Pressure curves.
4. **Maternal Tracking**: Inject pregnancy cycles and fertility rates as core demographic attributes.

## PHASE 3: THE HEALTHCARE WORLD
*Anchoring the simulation in physical reality.*
5. **Facility Mapping**: Ingest the Nigeria Health Facility Registry (NHFR) and map facilities (PHCs, GHs, THs) to specific LGAs and coordinates.
6. **Provider Generation**: Generate synthetic doctors/nurses attached to those facilities.

## PHASE 4: SOCIOECONOMICS & CARE SEEKING
*This depends on Phase 3, because a patient must have a facility to travel to in order to calculate distance/cost.*
7. **Socioeconomic Status (SES)**: Assign poverty brackets based on NBS data.
8. **Care-Seeking Behavior Engine**: Intercept all encounter triggers and apply a "delay probability" based on the patient's SES, distance to the facility, and insurance coverage.
9. **Financials/Insurance**: Model Out-Of-Pocket payments vs NHIA coverage.

## PHASE 5: ADVANCED SIMULATION
10. **Household/Graph Modelling**: Group patients into families to simulate genetic inheritance (Sickle Cell) and localized transmission (Tuberculosis, COVID-19).

