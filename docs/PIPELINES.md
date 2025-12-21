# Active Pipelines

This document details the three primary analysis pipelines currently active in the Map Reader LLM project. These pipelines represent different strategies for balancing **Recall** (finding all mounds) vs. **Precision** (avoiding false positives) and **Cost/Speed**.

## Summary Table

| Pipeline | Scripts Used | Config Versions | Focus | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Legacy (v3.2)** | `4_detect_mounds_batch.py` | `v3.2_experimental.json` | Baseline Testing | Active / Legacy |
| **Clean / Fast (v3.5)** | `4_detect_mounds_batch.py` | `v3.5_clean.json` | Balanced Speed/Accuracy | **Recommended** |
| **Two-Stage (v4.X)** | `4_detect_mounds_batch.py`<br>`5_verify_crops.py` | Stage 1: `v4.1_recall_augmented.json`<br>Stage 2: `v4.6_verifier.json` | Maximum Rigor & Accuracy | Active / Advanced |

---

## 1. v3.2 Legacy Pipeline (Experimental)
* **Config**: `prompts/versions/v3.2_experimental.json`
* **Description**: The original "Standard" pipeline. It relies on a balanced set of instructions and examples. It is maintained primarily for backwards compatibility and regression testing against newer methods.
* **Usage**:
  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/versions/v3.2_experimental.json
  ```

## 2. v3.5 "Clean" Pipeline
* **Config**: `prompts/versions/v3.5_clean.json` (also `v3.5_clean_pro.json` for Gemini Pro)
* **Description**: A streamlined, visual-first pipeline.
    *   **Visual-First**: Many complex text constraints were removed in favor of a curated "Reference Library" of images.
    *   **Model**: Gemini 1.5 Flash (default) for high speed and low cost.
    *   **Goal**: To serve as a high-performance baseline for "Single Shot" detection.
* **Usage**:
  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/versions/v3.5_clean.json
  ```

## 3. v4.1 + v4.6 Two-Stage Pipeline (High Recall + Verification)
This is the most advanced and rigorous pipeline, designed to mimic a "Proposer-Reviewer" human workflow.

### Stage 1: The "Proposer" (High Recall)
* **Config**: `prompts/versions/v4.1_recall_augmented.json` (or `v4.2_recall_high_temp.json`)
* **Goal**: **Recall at all costs.** The prompt is tuned to be "trigger happy," flagging anything that *might* be a mound. It explicitly targets "Hard Negatives" and "Hard Positives" mined from previous errors.
* **Output**: A GeoJSON file containing many candidates (including False Positives).
* **Command**:
  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/versions/v4.1_recall_augmented.json
  ```

### Stage 2: The "Verifier" (High Precision)
* **Config**: `prompts/versions/v4.6_verifier.json`
* **Script**: `scripts/5_verify_crops.py`
* **Goal**: **Detailed Inspection.** This script takes the candidates from Stage 1, crops high-resolution images of each candidate, and asks a more powerful model (or a specific "Verifier" prompt) to make a final judgment.
* **Mechanism**:
    *   It performs a "Visual Chain of Thought" (Scan -> Discriminate -> Factors -> Score).
    *   It uses a specific rubric to assign a confidence score (0.0 - 1.0).
    *   It filters out the "Hard Negatives" caught by the Proposer.
* **Command**:
  ```bash
  # Input comes from Stage 1 output
  python scripts/5_verify_crops.py --candidates outputs/results/v4.1_recall_augmented/candidates.geojson --output outputs/results/v4.1_recall_augmented/verified.geojson --config prompts/versions/v4.6_verifier.json
  ```

---

## Configuration Details
All pipeline configurations are stored in `prompts/versions/`. These JSON files control:
*   **Model**: Which Gemini model to use.
*   **Temperature**: Stochasticity of the output (0.0 for precision, 1.0 for diversity/recall).
*   **Examples**: The specific set of few-shot images loaded into the context window.
