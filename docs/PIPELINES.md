# Active Pipelines

This document details the analysis pipelines currently active in the Map Reader LLM project. Pipelines represent different strategies for balancing **Recall** (finding all mounds) vs. **Precision** (avoiding false positives) and **Cost/Speed**.

## Naming Convention

Prompts follow this pattern: `{workflow}_{modality}[_{variant}].json`

| Component | Values | Meaning |
|-----------|--------|---------|
| **workflow** | `detect`, `propose`, `verify` | Single-shot, Two-stage S1, Two-stage S2 |
| **modality** | `text-only`, `text-image`, `image-only` | What drives the prompt |
| **variant** | `-hardneg`, `_liberal` | Hard negatives, parameter variants |

---

## Summary Table

| Pipeline | Config | Hard Neg Variant | Focus |
|----------|--------|------------------|-------|
| **Text-Only** | `detect_text-only.json` | `detect_text-only-hardneg.json` | Baseline (no images) |
| **Text + Image** | `detect_text-image.json` | `detect_text-image-hardneg.json` | Text + images |
| **Image-Only** | `detect_image-only.json` | `detect_image-only-hardneg.json` | Minimal text |
| **Two-Stage** | `propose_image-only.json` + `verify_image-only.json` | *(includes hard neg)* | Maximum rigour |

---

## 1. Single-Shot Detection Pipelines

### Text-Only (`detect_text-only`)

- **Config**: `prompts/configs/detect_text-only.json`
- **Instructions**: `prompts/system-instructions/detect_text-only.md`
- **Description**: Pure text instructions with no reference images. V2.3 revival from preliminary work. Use as baseline to measure image contribution.
- **Usage**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_text-only.json
  ```

### Text + Image (`detect_text-image`)

- **Config**: `prompts/configs/detect_text-image.json`
- **Instructions**: `prompts/system-instructions/detect_text-image.md`
- **Description**: Descriptive text instructions combined with 7 reference images (4 positive, 3 null). Use `-hardneg` variant to add hard negative examples.
- **Usage**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_text-image.json
  ```

### Image-Only (`detect_image-only`)

- **Config**: `prompts/configs/detect_image-only.json`
- **Instructions**: `prompts/system-instructions/detect_image-only.md`
- **Description**: Minimal text instructions with 7 reference images (4 positive, 3 null). Neutral filenames to prevent semantic leakage. Use `-hardneg` variant to add hard negative examples.
- **Usage**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_image-only.json
  ```

---

## 2. Two-Stage Pipeline (Propose + Verify)

This is the most rigorous pipeline, designed to mimic a "Proposer-Reviewer" human workflow.

### Stage 1: Proposer (`propose_image-only`)

- **Config**: `prompts/configs/propose_image-only.json`
- **Instructions**: `prompts/system-instructions/propose_image-only.md`
- **Goal**: **Recall at all costs.** Flag anything that *might* be a mound.
- **Strategy**: 9 reference images (4 positive, 3 null, 2 hard negatives).
- **Output**: GeoJSON with many candidates (including False Positives).
- **Command**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/propose_image-only.json
  ```

### Stage 2: Verifier (`verify_image-only`)

- **Config**: `prompts/configs/verify_image-only.json`
- **Instructions**: `prompts/system-instructions/verify_image-only.md`
- **Script**: `scripts/5_verify_crops.py`
- **Goal**: **Precision filter.** Crop each candidate, perform detailed visual inspection, assign confidence score.
- **Mechanism**:
  - Visual Chain of Thought: Scan → Discriminate → Calibrate → Verify
  - Confidence scoring rubric (0.0–1.0)
  - Filters out False Positives from Stage 1
- **Command**:

  ```bash
  python scripts/5_verify_crops.py \
    --candidates outputs/results/propose_image-only/candidates.geojson \
    --output outputs/results/propose_image-only/verified.geojson \
    --config prompts/configs/verify_image-only.json
  ```

---

## Configuration Details

All pipeline configurations are stored in `prompts/configs/`. These JSON files control:

- **model**: Which model to use (e.g., `gemini-3-flash`)
- **temperature**: Sampling temperature (1.0 for experiments)
- **max_output_tokens**: Maximum output tokens (8192)
- **examples**: Reference images loaded into context window
- **instruction_file**: Path to system instruction markdown

System instructions are stored in `prompts/system-instructions/`.

## Baseline vs Hard Negative Variants

Each single-shot pipeline has two variants:

| Variant | Examples | Instruction | Purpose |
|---------|----------|-------------|---------|
| Baseline | Positives + null tiles | What to find | Measure baseline performance |
| `-hardneg` | + hard negatives | + exclusion guidance | Test if hard negatives improve precision |

Two-stage pipelines include hard negatives by default (no baseline variant).
