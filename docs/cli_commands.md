# MedSynth Command Reference

This is the complete command reference for the `medsynth` CLI.

## Basic Commands

**Generate the default population:**
```powershell
medsynth generate
```

**Get help on the CLI:**
```powershell
medsynth --help
```

**Get help on generation options:**
```powershell
medsynth generate --help
```

## Generation Options

### `-p` / `--patients`
- **Purpose:** Specifies the number of synthetic patients to generate.
- **Syntax:** `-p 100` or `--patients 100`
- **Default:** `10`
- **Valid values:** Any integer > 0
- **Examples:** `medsynth generate -p 500`

### `--state`
- **Purpose:** Restricts the geographic assignment to a specific state.
- **Syntax:** `--state Osun`
- **Default:** `Osun`
- **Valid values:** Any valid Nigerian state (e.g. `Lagos`, `Oyo`, `Kano`). Cannot be combined with conflicting `--lga`.

### `--lga`
- **Purpose:** Restricts the geographic assignment to a specific Local Government Area (LGA).
- **Syntax:** `--lga Somolu`
- **Default:** None (Randomly assigned based on state).
- **Interactions:** Automatically assigns the correct parent state if one is not provided. Fails if `--state` is provided but doesn't match the LGA's actual state.

### `--city`
- **Purpose:** Target specific city.
- **Syntax:** `--city Osogbo`
- **Default:** None
- **Note:** *Not Currently Supported* (No city-level datasets exist). Passing this will currently result in a validation error. 

### `--sex`
- **Purpose:** Restrict the generated population to a specific biological sex.
- **Syntax:** `--sex male` or `--sex female`
- **Default:** `all` (Probabilistically weighted based on Nigerian demographic datasets).
- **Valid values:** `male`, `female`, `m`, `f`, `all`.

### `--age`
- **Purpose:** Restricts the generation to an exact age or age range.
- **Syntax:** `--age 25` or `--age 20-40` or `--age newborn`
- **Default:** `all` (Probabilistically weighted based on the Nigerian population pyramid).
- **Valid values:** Exact integers, `min-max` ranges, or demographic categories (`newborn`, `child`, `adolescent`, `adult`, `elderly`).

### `--disease`
- **Purpose:** Load specific clinical disease modules instead of all enabled modules.
- **Syntax:** `--disease malaria` or `--disease malaria,tb,hiv`
- **Default:** `all` (Loads every `.json` file in `datasets/diseases/`).
- **Valid values:** Any basename of an existing disease JSON file.

### `-f` / `--format`
- **Purpose:** Restricts the exporter to only output specific data formats, reducing clutter and file IO time.
- **Syntax:** `-f csv` or `-f fhir,json`
- **Default:** `csv,json,fhir`
- **Valid values:** Comma-separated list of `csv`, `json`, `fhir`, or `all`.

### `--seed`
- **Purpose:** Fixes the internal Random Number Generator state to produce exactly reproducible populations.
- **Syntax:** `--seed 12345`
- **Default:** Random (System timestamp).

### `--group`
- **Purpose:** A powerful tool to generate multiple disparate cohorts in a single run.
- **Syntax:** `--group "sex:count:location"` or `--group "sex:count:location:age"`
- **Default:** None
- **Examples:** `medsynth generate --group "male:500:Ibadan" --group "female:500:Lagos"`
- **Interactions:** Bypasses the base generation defaults to inject the cohort directly into the aggregate population. Multiple groups can be defined.

