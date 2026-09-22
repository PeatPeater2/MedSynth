# How MedSynth Works Internally (Technical Guide)

This guide explains the deep technical mechanics of MedSynth's engine.

## 1. Object Architecture

### The `Generator` (`generator.py`)
This is the master orchestration class. It is instantiated exactly once per run (or once per worker process). 
* **State Loading:** The `__init__` method loads the bulky CSV files (Facilities, Demographics, Names) into RAM.
* **JSON Parsing:** It reads the `datasets/diseases/*.json` files and converts them into in-memory dictionary trees representing the state machines.

### The `Patient` (`patient.py`)
A lightweight data class representing the biological human.
* It holds `attributes` (dictionary of demography).
* It holds `record`, an instance of `HealthRecord`.
* Crucially, the `Patient` object is **ephemeral**. In streaming mode, as soon as the patient dies or reaches the present day, they are exported and instantly garbage-collected by Python.

### The `HealthRecord` (`health_record.py`)
Contains lists of clinical objects: `Encounter`, `Condition`, `Observation`, `Medication`.
* **Important Distinction:** The `Patient` is biology. The `HealthRecord` is the medical chart.

## 2. The Generic Module Framework (GMF)

The GMF (`state_machine.py`) evaluates JSON files.
* **States:** Nodes in a graph.
* **Transitions:** Edges pointing to the next node.
* **Guards:** Boolean checks (e.g., `if @patient.wealth_quintile == 1`).

When `Generator.generate_person` is called, it iterates over every active disease module. The patient steps through the state machine. If they hit a `Delay` state, the engine calculates the time to wake up, puts the module to sleep, and advances the patient's internal clock.

## 3. The Streaming Yield

To generate 100 million patients without crashing, MedSynth uses Python generator functions (`yield`).

```python
def generate_stream(self, workers=1):
    for i in range(population_size):
        patient = self.generate_person(i, seed)
        yield patient
```

In `cli.py`:
```python
for p in generator.generate_stream(...):
    exporter.export_patient(p)
```
Because the list of patients is never appended to an array like `generated_population.append(p)`, Python reclaims the memory instantly. 

## 4. Multiprocessing & The GIL

Python has a Global Interpreter Lock (GIL) that prevents multiple threads from executing Python bytecode simultaneously. Therefore, `ThreadPoolExecutor` does not speed up CPU-bound tasks like generating patients.

MedSynth uses `ProcessPoolExecutor` to bypass the GIL. It spawns independent Python processes.
* **The IPC Bottleneck:** To send work to a child process, Python must `pickle` (serialize) the arguments. Because `Generator` contains 46,000 facilities in RAM, passing `Generator` to a child process is incredibly slow. 
* MedSynth handles this by chunking tasks (e.g., 100 seeds at a time) to minimize the number of times serialization must occur, but IPC remains the primary performance bottleneck.

## 5. Checkpointing & Random Seeds

* **Reproducibility:** If `seed=42`, patient #1 will *always* receive exactly the same biological outcome. This is because MedSynth generates a massive pre-calculated list of independent seeds: `seeds = [main_rng.randint(...) for _ in range(N)]`. Worker 8 finishing before Worker 1 does not alter the random sequence.
* **Checkpointing:** Every `N` patients, `cli.py` writes `patients_completed=X` to `checkpoint.json`. If power fails, `--resume` reads this file and simply starts the `for` loop at index `X` instead of `0`.

