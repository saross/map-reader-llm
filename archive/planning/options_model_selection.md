# Architecture Options: Model Selection & Orchestration

**Objective**: Allow flexible switching between models (Flash/Pro) without degrading reproducibility or creating "Config Hell".

## Option 1: CLI Overrides (The "Ad-Hoc" Approach)
Add a `--model` flag to your scripts. This overrides the value in the JSON config at runtime.

*   **Usage**: `python run_benchmark.py --model gemini-1.5-flash`
*   **Pros**: 
    *   Extremely fast to use and implement.
    *   Great for "What if?" testing during development.
    *   No new files to manage.
*   **Cons**:
    *   **Reproducibility Risk**: The resulting metadata *must* record the override, or you lose track of what really ran. (Our `MetadataTracker` already handles this).
    *   **Manual**: You have to run commands one by one.

## Option 2: Config Inheritance (The "FAIR4RS" Approach)
Create new JSON configs that explicitly reference a "parent" config but override specific fields.

*   **Structure**: 
    *   `v3.3_flash.json`: `{ "parent": "v3.1_baseline.json", "model": "gemini-1.5-flash" }`
*   **Usage**: `python run_benchmark.py --config v3.3_flash.json`
*   **Pros**:
    *   **Perfect Reproducibility**: The exact configuration is saved in a file under version control.
    *   **Explicitness**: You know exactly what "v3.3" means (it means v3.1 + Flash).
*   **Cons**:
    *   **File Proliferation**: You get many small files.
    *   **Eng Impact**: Requires updating the config loader to handle "inheritance".

## Option 3: The "Job Queue" (The "Ops" Approach)
Use a YAML file to define a "Batch" of multiple runs.

*   **Structure**: `queue.yaml`
    ```yaml
    - name: "Flash Baseline"
      run: "v3.1_baseline"
      model: "gemini-1.5-flash"
    - name: "Pro Production"
      run: "v3.1_baseline"
      model: "gemini-3-pro"
    ```
*   **Usage**: `python run_queue.py queue.yaml`
*   **Pros**:
    *   **Automation**: "Set and Forget". Run 5 experiments overnight perfectly.
    *   **Organisation**: logical grouping of related runs.
*   **Cons**:
    *   **Complexity**: Requires building a new `run_queue.py` orchestrator.

## Recommendation

**Start with Option 1 (CLI)** for immediate interactive development ("Develop on Flash"), but **adopt Option 3 (Job Queue)** for your overnight/production benchmarking runs.

**Why?**
1.  **CLI** solves your *immediate* pain ("I just want to try Flash *now*").
2.  **Job Queue** solves your *process* pain ("I want to run a robust set of tests without babysitting").

I can implement Option 1 in ~10 mins. Option 3 would take ~30-45 mins.
