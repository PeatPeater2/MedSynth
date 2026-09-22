# Configuration & Flexibility Guide

This guide outlines exactly what can be customized or controlled in the current MedSynth architecture.

## Configuration Matrix

| Option | Supported? | How to control it | Example |
| :--- | :--- | :--- | :--- |
| **Population size** | **SUPPORTED NOW** | CLI: `-p` or `--population` | `python medsynth/main.py -p 100` |
| **Random seed** | **SUPPORTED NOW** | CLI: `--seed` | `python medsynth/main.py --seed 42` |
| **State** | **SUPPORTED NOW** | CLI: `-s` or `--state` | `python medsynth/main.py -s Kano` |
| **LGA** | **SUPPORTED NOW** | CLI: `--lga` | `python medsynth/main.py --lga Somolu` |
| **Age bounds** | **SUPPORTED NOW** | CLI: `--min-age` and `--max-age` | `python medsynth/main.py --min-age 10 --max-age 15` |
| **Sex** | **SUPPORTED NOW** | CLI: `--sex` | `python medsynth/main.py --sex M` |
| **Disease selection** | **SUPPORTED NOW** | CLI: `-m` or `--modules` | `python medsynth/main.py -m malaria tuberculosis` |
| **Output format** | **SUPPORTED NOW** | CLI: `-f` or `--format` | `python medsynth/main.py -f fhir json` |
| **Output directory** | **SUPPORTED NOW** | CLI: `-o` or `--output` | `python medsynth/main.py -o ./custom_out` |

