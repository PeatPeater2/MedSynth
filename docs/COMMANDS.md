# MedSynth Command Reference

MedSynth is executed via its main entry point: `medsynth/main.py`.

## Core Command
```bash
python medsynth/main.py [options]
```

## Available Arguments

| Argument | Short | Purpose | Valid Values |
| :--- | :--- | :--- | :--- |
| `--population` | `-p` | Number of synthetic patients to generate. | Any positive integer |
| `--state` | `-s` | Target a specific Nigerian state. | e.g., `Kano`, `Lagos` |
| `--lga` | | Target a specific Local Government Area. | e.g., `Somolu` |
| `--seed` | | Fix the random seed for reproducible population generation. | Any integer |
| `--min-age` | | Minimum age limit. | e.g., `10` |
| `--max-age` | | Maximum age limit. | e.g., `15` |
| `--sex` | | Target a specific biological sex. | `M` or `F` |
| `--modules` | `-m` | List of specific disease modules to load. | e.g., `malaria tuberculosis` |
| `--format` | `-f` | Output formats to generate. | e.g., `csv`, `json`, `fhir` |
| `--output` | `-o` | Custom output directory path. | Any valid path |

## Advanced Examples

**Generate 5 Males between ages 10 and 15 in Somolu LGA, running ONLY the Malaria module, exporting ONLY FHIR R4 to a custom directory:**
```bash
python medsynth/main.py -p 5 --min-age 10 --max-age 15 --sex M --lga Somolu --modules malaria -f fhir -o C:/custom/path
```

## PLANNED COMMAND CAPABILITIES

The following commands are reasonable future additions that would improve the utility of the generator but are **not currently implemented**:
- `--year` / `--start-date` / `--end-date`: To constrain the temporal boundaries of the simulation (currently, it simulates up to the exact moment of execution).
- `--facility`: To bind the generated population to a specific healthcare facility or coordinates.
- `--household-size`: To generate linked family graphs instead of isolated individuals.

