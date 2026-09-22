# MedSynth

MedSynth is a synthetic healthcare data generator written in Python, designed from the ground up for the Nigerian healthcare context.

## HOW TO RUN MEDSYNTH

Currently, MedSynth implements the core simulation engine, Nigerian geography (States, LGAs, Wards), demographic handling, and a deterministic random-seed timeline. Disease modules, clinical histories, and data exporters are in active development.

### 1. Install dependencies
MedSynth currently has no external dependencies beyond the Python standard library.

### 2. Run Tests
To run the automated test suite and edge-case validations:
```bash
$env:PYTHONPATH = "C:\Projects\MedSynth"
python -m unittest discover -s tests -p "test_*.py" -v
```

### 3. Run Static Analysis
To verify syntax integrity across the project:
```bash
python -m compileall medsynth tests
```

### 4. Basic Generation
*(Note: As the CLI entrypoint is not yet finalized, generation is currently executed programmatically via the core engine.)*

```python
import time
from medsynth.simulation.generator import Generator, GeneratorOptions

options = GeneratorOptions()
options.population_size = 100
options.seed = 12345

generator = Generator(options)
population = generator.run()

for person in population:
    print(f"Name: {person.attributes.get('first_name')} {person.attributes.get('last_name')}")
    print(f"Location: {person.attributes.get('lga')}, {person.attributes.get('state')}")
```

### 5. Location Targeting
To generate a population for a specific Nigerian State or LGA:
```python
options.target_state = "Oyo"
options.target_lga = "Ibadan North"
```

### Features Currently Excluded/Incomplete
- **Exporting (CSV/JSON/FHIR)**: Exporters are pending implementation (CSV will be implemented first as per project guidelines; JSON/FHIR are excluded).
- **Disease Selection**: Modules have not been introduced yet.
- **Age/Sex Filtering**: Filtering via configuration is pending the CLI implementation.

