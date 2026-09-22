# CLI Command Reference

This document outlines the syntax and options for the MedSynth Command Line Interface.

**Core Command:**
`python -m medsynth generate`

### Valid Options

* `-p`, `--patients`: Number of patients to generate (Default: 1).
* `-s`, `--seed`: Random seed for reproducibility.
* `-o`, `--output`: Output directory (Default: `./output`).
* `-f`, `--format`: Output formats. Comma separated list of `csv`, `json`, `fhir` (Default: `csv,json,fhir`).
* `--state`: Target a specific Nigerian state (e.g., "Lagos").
* `--lga`: Target a specific LGA (e.g., "Ikeja").
* `--sex`: Target a specific sex (`M` or `F`).
* `--stream`: Use streaming generation to remove RAM limits (Highly recommended for N > 10,000).
* `-w`, `--workers`: Number of CPU processes for streaming generation (Default: 1).
* `--checkpoint-every`: How often to save progress to `checkpoint.json` (Default: 10,000).
* `--resume`: Resume generation from a specific `checkpoint.json` file.

---

# Practical Use Cases

### 1. Generate a small test population
```bash
python -m medsynth generate --patients 100
```
*Generates 100 patients to the `./output` folder in all formats.*

### 2. Generate a large population using all CPU cores
```bash
python -m medsynth generate --patients 500000 --stream --workers 8 --output ./my_data
```
*Streams 500k patients to disk using 8 CPU cores.*

### 3. Generate a geographically targeted population
```bash
python -m medsynth generate --patients 5000 --state "Kano" --lga "Kano Municipal"
```
*Forces all 5,000 generated patients to live in Kano Municipal and visit facilities located there.*

### 4. Export only FHIR data (No CSV)
```bash
python -m medsynth generate --patients 1000 --format fhir
```

### 5. Reproducible Scientific Research
```bash
python -m medsynth generate --patients 10000 --seed 9999
```
*Will generate the exact same 10,000 biological trajectories every time it is run.*

### 6. Resuming an Interrupted Run
If you were generating 1,000,000 patients and your laptop battery died at 450,000:
```bash
python -m medsynth generate --patients 1000000 --stream --resume ./output/checkpoint.json
```
*MedSynth will read the checkpoint, skip the first 450,000 indexes, and safely append the remaining 550,000 to the files.*

