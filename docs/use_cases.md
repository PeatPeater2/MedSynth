# Practical Use Cases

This document outlines practical scenarios for running the MedSynth engine.

### 1. The Standard Generation
You want to test the system quickly.
```bash
python -m medsynth generate --patients 100
```

### 2. The Extreme-Scale Run
You need 1 million patients for a Machine Learning training set. You must use `--stream` to prevent your RAM from crashing.
```bash
python -m medsynth generate --patients 1000000 --stream --workers 8 --output ./big_data
```

### 3. Epidemiological Targeting (Geographic)
You are simulating an outbreak in a specific Nigerian state.
```bash
python -m medsynth generate --patients 10000 --state "Lagos"
```

### 4. Demographic Targeting (Maternal Health Prep)
You only want to generate female patients for a specific study.
```bash
python -m medsynth generate --patients 5000 --sex F
```

### 5. FHIR Integration Testing
You are building an EMR software and need to test your FHIR database ingestion script, but you don't need CSV files.
```bash
python -m medsynth generate --patients 10000 --format fhir
```

### 6. Disaster Recovery
Your 50 Million patient run crashed after 3 days due to a Windows Update restart.
```bash
python -m medsynth generate --patients 50000000 --stream --resume ./big_data/checkpoint.json
```

