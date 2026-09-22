# EXTREME SCALE ARCHITECTURE AUDIT (50 MILLION PATIENTS)

## 1. PIPELINE & MEMORY AUDIT
The current MedSynth generation pipeline is fundamentally **batch-bound**.
The flow is:
Generator -> Patient[] (stored in RAM) -> Exporters -> Disk

Every single generated patient is appended to a global ll_patients list. Memory is never released until the entire generation and export process completes.

**Measurements (from physical tracemalloc benchmarks):**
- **RAM per patient**: ~6,013 bytes.
- **10,000 patients**: ~57.34 MB Peak RAM.
- **Estimated 50 Million patients**: ~300 GB Peak RAM.

**Conclusion**: A 50M patient run is impossible on standard hardware without true streaming execution.

## 2. EXPORTER STREAMING AUDIT
If we refactor the Generator to yield patients (streaming), the exporters must also support incremental writes.

* **CSV Exporter**: Currently loops over the entire population. It can easily be refactored to append rows incrementally and flush to disk.
* **JSON Exporter**: Currently serializes the entire array. To stream, it must be rewritten to output **Newline-Delimited JSON (NDJSON)**, allowing it to write one patient per line without holding the array structure in memory.
* **FHIR R4 Exporter**: Currently creates one massive Bundle object. A 35GB FHIR Bundle is technically invalid/unusable. We must implement **Chunked Output** (e.g., writing one Bundle per 10,000 patients) or output raw NDJSON FHIR resources.

## 3. STORAGE ESTIMATES
Storage requirements scale linearly and are well within the capacity of a modern SSD.
*(Based on empirical disk footprints from 10,000 patients)*

| Format | Bytes/Patient | 1 Million | 10 Million | 50 Million |
|--------|---------------|-----------|------------|------------|
| CSV    | 67            | 67 MB     | 670 MB     | 3.35 GB    |
| JSON   | 470           | 470 MB    | 4.7 GB     | 23.5 GB    |
| FHIR   | 719           | 719 MB    | 7.19 GB    | 35.95 GB   |

## 4. CONCURRENCY & REPRODUCIBILITY
Currently, concurrency is handled via concurrent.futures.ThreadPoolExecutor. However, Python's GIL means this does not provide true parallel CPU bound acceleration. 
For 50M patients, the architecture must transition to a **Producer/Consumer Worker Pool** using multiprocessing (process pools). 

**Reproducibility Issue**: If multiple processes generate patients simultaneously, global seed manipulation fails. We must assign a deterministic seed derived from the Patient ID or Index at creation time, rather than relying on sequential state.

## 5. FAILURE RECOVERY
Currently, a crash at patient 999,999 destroys all progress.
A streaming architecture inherently solves this by saving data instantly. However, we must implement **Checkpointing** so that a failed run can resume from Patient N.

## 6. REQUIRED ARCHITECTURE FOR 50M
To achieve 50,000,000 patients:
1. **Streaming Generator**: Change 
un() to yield patient.
2. **Streaming Exporters**: Exporters process the generator stream one patient at a time.
3. **Multiprocessing**: Use process pools rather than thread pools to bypass the GIL.
4. **Chunked FHIR**: Never create a 35GB FHIR Bundle. Output thousands of 50MB Bundles.
5. **Deterministic Seeding**: Seed Random per patient using hash(patient_id + global_seed).
