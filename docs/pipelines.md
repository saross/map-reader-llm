# Active Pipelines

**Document version**: 1.2
**Last updated**: 2026-01-18

---

This document details the analysis pipelines currently active in the Map Reader LLM project. Pipelines represent different strategies for balancing **Recall** (finding all mounds) vs. **Precision** (avoiding false positives) and **Cost/Speed**.

## Naming Convention

Prompts follow the pattern: `{workflow}_{M/E-level}[_{H5-level}].json`

| Component | Values | Meaning |
|-----------|--------|---------|
| **workflow** | `detect`, `propose`, `verify` | Single-shot, Two-stage S1, Two-stage S2 |
| **M/E-level** | `image-only`, `brief-text`, `brief-text-image`, `verbose-text`, `verbose-text-image` | Modality and elaboration level |
| **H5-level** | `_terse`, `_verbose` | Negative text treatment (omit for minimal) |

---

## Summary Table

| Pipeline | Base Config | H5 Variants | Focus |
|----------|-------------|-------------|-------|
| **Image-Only** | `detect_image-only.json` | `_terse`, `_verbose` | Minimal text, images only |
| **Brief-Text** | `detect_brief-text.json` | N/A (text-only) | Concise text, no images |
| **Brief-Text+Image** | `detect_brief-text-image.json` | `_terse`, `_verbose` | Concise text + images |
| **Verbose-Text** | `detect_verbose-text.json` | N/A (text-only) | Detailed text, no images |
| **Verbose-Text+Image** | `detect_verbose-text-image.json` | `_terse`, `_verbose` | Detailed text + images |
| **Two-Stage** | `propose_brief.json` + `verify_brief.json` | N/A | Exploratory (H2) |

---

## 1. Single-Shot Detection Pipelines

### Image-Only (`detect_image-only`)

- **Config**: `prompts/configs/detect_image-only.json`
- **Instructions**: `prompts/system-instructions/detect_image-only.md`
- **Description**: Minimal text instructions with visual examples. Neutral filenames prevent semantic leakage. H5 variants add exclusion guidance for negative examples.
- **Library**: Scale-8 (17 examples: 4 Canon+, 2 Canon-, 4 HP, 4 HN, 3 null)
- **Usage**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_image-only.json
  ```

### Brief-Text (`detect_brief-text`)

- **Config**: `prompts/configs/detect_brief-text.json`
- **Instructions**: `prompts/system-instructions/detect_brief-text.md`
- **Description**: Concise text descriptions of the target symbols; no example images (the map tile itself is still supplied — this is the *example* modality, not the input modality).
- **Purpose**: The production carry-forward condition — it beat image-only on the registered H1 test (ΔF1 +0.088, p = 0.004) and was selected under §8.4.7's own carry-forward rule. The registration's original "academic baseline" designation was retired 2026-07-30 (see `docs/methodology/preregistration/protocol-errata.md` E68).
- **Usage**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_brief-text.json
  ```

### Brief-Text+Image (`detect_brief-text-image`)

- **Config**: `prompts/configs/detect_brief-text-image.json`
- **Instructions**: `prompts/system-instructions/detect_brief-text-image.md`
- **Description**: Concise text instructions combined with visual examples. H5 variants add exclusion guidance.
- **Library**: Scale-8 (17 examples)
- **Usage**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_brief-text-image.json
  ```

### Verbose-Text (`detect_verbose-text`)

- **Config**: `prompts/configs/detect_verbose-text.json`
- **Instructions**: `prompts/system-instructions/detect_verbose-text.md`
- **Description**: Text-only baseline with detailed symbol descriptions. No visual examples.
- **Purpose**: Academic baseline to test if verbose text compensates for lack of images.
- **Usage**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_verbose-text.json
  ```

### Verbose-Text+Image (`detect_verbose-text-image`)

- **Config**: `prompts/configs/detect_verbose-text-image.json`
- **Instructions**: `prompts/system-instructions/detect_verbose-text-image.md`
- **Description**: Detailed text instructions combined with visual examples. H5 variants add exclusion guidance.
- **Library**: Scale-8 (17 examples)
- **Usage**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_verbose-text-image.json
  ```

---

## 2. Two-Stage Pipeline (Propose + Verify)

> **Note**: Two-stage pipelines are tested as **exploratory (H2)** based on preliminary evidence suggesting they do not outperform single-stage detection with voting. The pipeline is retained to formally test the null hypothesis.

This pipeline mimics a "Proposer-Reviewer" human workflow.

### Stage 1: Proposer (`propose_brief`)

- **Config**: `prompts/configs/propose_brief.json`
- **Instructions**: `prompts/system-instructions/propose_brief.md`
- **Goal**: **Recall at all costs.** Flag anything that *might* be a mound.
- **Strategy**: Liberal detection threshold; classify subtypes for diagnostics.
- **Output**: GeoJSON with many candidates (including False Positives).
- **Command**:

  ```bash
  python scripts/4_detect_mounds_batch.py --config prompts/configs/propose_brief.json
  ```

### Stage 2: Verifier (`verify_brief`)

- **Config**: `prompts/configs/verify_brief.json`
- **Instructions**: `prompts/system-instructions/verify_brief.md`
- **Script**: `scripts/5_verify_crops.py`
- **Goal**: **Precision filter.** Crop each candidate, perform detailed visual inspection, assign confidence score.
- **Mechanism**:
  - Visual Chain of Thought: Scan → Discriminate → Calibrate → Verify
  - Confidence scoring rubric (0.0–1.0)
  - Filters out False Positives from Stage 1
- **Command**:

  ```bash
  python scripts/5_verify_crops.py \
    --candidates outputs/propose_brief/candidates.geojson \
    --output outputs/propose_brief/verified.geojson \
    --config prompts/configs/verify_brief.json
  ```

### Known Limitations

Preliminary testing found two-stage pipelines underperformed single-stage with voting:

| Issue | Impact |
|-------|--------|
| **Compounding errors** | If Stage 1 misses a target, Stage 2 never sees it |
| **Context loss** | Verifier sees cropped regions without full map context |
| **Systematic failures** | Two-stage failures are unfixable by voting; single-stage failures are stochastic |

See `decisions-log.md` for full rationale on H2 exploratory status.

---

## Configuration Details

All pipeline configurations are stored in `prompts/configs/`. These JSON files control:

| Field | Description |
|-------|-------------|
| `model` | Which model to use (e.g., `gemini-3-flash`) |
| `temperature` | Sampling temperature (1.0 for experiments) |
| `max_output_tokens` | Maximum output tokens (8192) |
| `thinking_level` | Gemini reasoning depth (`minimal` by default) |
| `examples` | Reference images loaded into context window |
| `instruction_file` | Path to system instruction markdown |

System instructions are stored in `prompts/system-instructions/`.

See `prompts/README.md` for full schema documentation including library configs and internal documentation fields.

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
    "system_instruction_hash": "sha256-of-system-instruction",
    "system_instruction_text": "You are an expert analyst...",
    "library_hash": "sha256-of-example-library-composition",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "thinking_level": "minimal",
    "include_example_images": true,
    "example_count": 9,
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
| `system_instruction_hash` | SHA-256 hash of system instruction text (for reproducibility) |
| `system_instruction_text` | Full system instruction text sent to the model |
| `library_hash` | SHA-256 hash of example library (paths + labels + categories) |
| `temperature` | Sampling temperature (0.0 = near-deterministic) |
| `max_output_tokens` | Maximum output tokens per API call |
| `thinking_level` | Model reasoning level (e.g., `minimal`, `medium`, `high`; Gemini ThinkingConfig) |
| `include_example_images` | Whether example images were sent (`true` for image tracks, `false` for text-only) |
| `example_count` | Number of examples in the library (from config, before image loading) |
| `git_commit` | Repository state at execution time |
| `finish_reason_counts` | Distribution of API completion statuses |
| `retries_*` | Breakdown by error category (rate limit, server, timeout) |
| `cost_estimate` | Calculated from token usage and current pricing |
| `per_item_metadata` | Detailed per-tile/per-candidate response data |

### Reconstructing the Full API Prompt

The meta.json captures all components needed to reconstruct the exact prompt sent to the
Gemini API. The prompt is not stored verbatim because it includes binary image data, but it
can be reconstructed deterministically from the metadata.

The API call structure (see `scripts/4_detect_mounds_batch.py`, lines 274–318) is:

```text
generate_content(
    model=<configuration.model>,
    contents=<content>,
    config=GenerateContentConfig(
        temperature=<configuration.temperature>,
        max_output_tokens=<configuration.max_output_tokens>,
        response_mime_type="application/json",
        thinking_config=ThinkingConfig(thinking_level=<configuration.thinking_level>),
        system_instruction=<configuration.system_instruction_text>,
        safety_settings=[all categories set to OFF],
    ),
)
```

The `contents` parameter is assembled as follows:

1. **Preamble text**: `"Here are the Reference Symbols you must find:"`
2. **Example pairs** (for each example in `full_config_snapshot.examples`, in order):
   - Text part: the `label` field (e.g., `"Positive"` or `"Negative"`)
   - Image part: the image file at `prompts/examples/<path>` (PNG bytes)
   - If `include_example_images` is `false`, this step is skipped entirely
3. **Transition text**: `"Now, find detection instances that visually match ANY of the above Reference Examples in the Target Map Tile below:"`
4. **Target tile image**: the tile being analysed (PNG bytes from `inputs/tiles/`)

To verify a specific run's prompt:

- The system instruction is in `configuration.system_instruction_text`
- The example images are at `prompts/examples/<full_config_snapshot.examples[N].path>`
- The example order matches the config order (unless `ordering_override` is set in the
  snapshot, in which case the reordered sequence was used)
- The target tile is identified by `per_item_metadata[N].item_id`

**Not captured in metadata** (hardcoded in the script):

- `response_mime_type` is always `"application/json"` (JSON mode)
- All four safety categories (`HARASSMENT`, `HATE_SPEECH`, `SEXUALLY_EXPLICIT`,
  `DANGEROUS_CONTENT`) are set to `OFF`
- The preamble and transition text strings shown above

### Shared Metadata Module

The metadata tracking logic is centralised in `scripts/lib_llm_metadata.py`, which provides:

- **`LLMMetadataTracker`**: Thread-safe aggregation class
- **`extract_gemini_metadata()`**: Gemini API response parser
- **`extract_claude_metadata()`**: Claude API response parser (for future use)
- **`extract_openai_metadata()`**: OpenAI API response parser (for future use)
- **`estimate_cost()`**: Cost calculation from token usage

This design ensures consistent metadata capture across all scripts and supports future multi-provider experiments.

---

## H5: Negative Text Treatment Variants

Each image-using pipeline has three H5 variants controlling how negative examples are described:

| H5 Level | Suffix | Exclusion Text | Purpose |
|----------|--------|----------------|---------|
| Minimal | *(none)* | "Negative" label only | Images speak for themselves |
| Terse | `_terse` | Brief (1-2 sentences) | Concise exclusion guidance |
| Verbose | `_verbose` | Detailed (6 subsections) | Full explanation of confusables |

**Example configs for Image-Only**:

- `detect_image-only.json` — H5=Minimal
- `detect_image-only_terse.json` — H5=Terse
- `detect_image-only_verbose.json` — H5=Verbose

Text-only pipelines (Brief-Text, Verbose-Text) have no H5 variants because negative guidance requires visual examples.

---

## Execution Modes

All detection pipelines can be executed via `run_phase2.py` in one of two modes:

| Mode | Flag | Engine | Rate Limiting | Cost |
|------|------|--------|---------------|------|
| **Concurrent** | `--mode concurrent` (default) | Per-tile API calls via `4_detect_mounds_batch.py` subprocess | Token-bucket governor (`lib_token_bucket.py`) | Standard pricing |
| **Batch** | `--mode batch` | Single JSONL file per unit via Gemini Batch API (`lib_batch_api.py`) | Server-side (separate, higher limits) | 50% discount |

Both modes produce identical output files (GeoJSON, `.meta.json`, `.tiles.json`), so downstream analysis scripts work without modification regardless of execution mode.

### When to use batch mode

- Large studies where cost matters (50% savings)
- Studies that can tolerate multi-hour latency per unit (batch jobs run asynchronously)
- Runs that don't need real-time progress monitoring
- **Crash-safe recovery**: If the process crashes during polling, re-run with `--resume` — pending batch jobs are recovered from the checkpoint and polled to completion instead of being resubmitted

### When to use concurrent mode

- Iterative development and debugging (immediate per-tile feedback)
- Small studies or sanity checks (faster turnaround for few tiles)
- When fine-grained retry control is needed (per-tile retries with backoff)

---

## Related Documents

- **Config schema**: `prompts/README.md` — Full configuration documentation
- **Hypothesis tracking**: `docs/methodology/preregistration/hypothesis-tracking.md` — Condition mappings
- **Decisions log**: `docs/methodology/preregistration/decisions-log.md` — Rationale for key decisions
