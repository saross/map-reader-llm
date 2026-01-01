# Active Pipelines

**Document version**: 1.1
**Last updated**: 2026-01-02

---

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

---

## Metadata Tracking

All pipeline scripts capture comprehensive metadata for reproducibility and cost analysis. Each run produces a `.meta.json` file alongside the output GeoJSON.

### Metadata Output Structure

```json
{
  "run_id": "uuid-v4-identifier",
  "timestamp": {
    "start": "2026-01-02T10:30:00+00:00",
    "end": "2026-01-02T10:45:23+00:00",
    "duration_seconds": 923.4
  },
  "environment": {
    "git_commit": "f6b88c0abc123...",
    "script": "4_detect_mounds_batch.py",
    "script_version": "4.2.0"
  },
  "configuration": {
    "version": "detect_image-only",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only.md",
    "prompt_hash": "sha256-of-system-instruction",
    "temperature": 1.0,
    "full_config_snapshot": { ... }
  },
  "execution_stats": {
    "items_processed": 20,
    "items_failed": 0,
    "retries_total": 2,
    "retries_rate_limit": 1,
    "retries_server_error": 1,
    "retries_timeout": 0,
    "safety_blocks": 0,
    "parse_failures": 0,
    "finish_reason_counts": { "success": 20 }
  },
  "usage_stats": {
    "total_input_tokens": 125000,
    "total_output_tokens": 4500,
    "total_cached_tokens": 0,
    "total_tokens": 129500,
    "by_provider": {
      "google_gemini": {
        "input_tokens": 125000,
        "output_tokens": 4500,
        "request_count": 20
      }
    }
  },
  "results_summary": {
    "total_detections": 47,
    "class_counts": { "burial_mound": 35, "settlement_mound": 12 }
  },
  "cost_estimate": {
    "input_cost_usd": 0.0125,
    "output_cost_usd": 0.0018,
    "total_cost_usd": 0.0143,
    "pricing_used": {
      "model": "gemini-3-flash",
      "input_per_1m": 0.10,
      "output_per_1m": 0.40
    }
  },
  "per_item_metadata": [
    {
      "item_id": "tile_0001.png",
      "provider": "google_gemini",
      "model_requested": "gemini-3-flash",
      "tokens": { "input_tokens": 6250, "output_tokens": 225 },
      "finish_reason": "success",
      "latency_ms": 2340,
      "attempt_number": 1,
      "parse_success": true
    }
  ]
}
```

### Key Metadata Fields

| Field | Description |
|-------|-------------|
| `run_id` | Unique identifier for this execution |
| `prompt_hash` | SHA-256 hash of system instruction (for reproducibility) |
| `git_commit` | Repository state at execution time |
| `finish_reason_counts` | Distribution of API completion statuses |
| `retries_*` | Breakdown by error category (rate limit, server, timeout) |
| `cost_estimate` | Calculated from token usage and current pricing |
| `per_item_metadata` | Detailed per-tile/per-candidate response data |

### Shared Metadata Module

The metadata tracking logic is centralised in `scripts/lib_llm_metadata.py`, which provides:

- **`LLMMetadataTracker`**: Thread-safe aggregation class
- **`extract_gemini_metadata()`**: Gemini API response parser
- **`extract_claude_metadata()`**: Claude API response parser (for future use)
- **`extract_openai_metadata()`**: OpenAI API response parser (for future use)
- **`estimate_cost()`**: Cost calculation from token usage

This design ensures consistent metadata capture across all scripts and supports future multi-provider experiments.

## Baseline vs Hard Negative Variants

Each single-shot pipeline has two variants:

| Variant | Examples | Instruction | Purpose |
|---------|----------|-------------|---------|
| Baseline | Positives + null tiles | What to find | Measure baseline performance |
| `-hardneg` | + hard negatives | + exclusion guidance | Test if hard negatives improve precision |

Two-stage pipelines include hard negatives by default (no baseline variant).
