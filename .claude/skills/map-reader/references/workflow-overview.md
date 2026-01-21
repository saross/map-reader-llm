# Workflow Overview

Generic detect-evaluate-analyse pipeline documentation for VLM cartographic symbol detection.

---

## Detection Script (`4_detect_mounds_batch.py`)

The core inference engine that processes map tiles through the VLM API.

### Full Parameter Reference

```bash
python scripts/4_detect_mounds_batch.py \
    --config <config.json>        # Required: Prompt configuration
    --manifest <manifest.json>    # Required: Tile manifest
    --output-dir <path>           # Required: Output directory
    --workers <n>                 # Optional: Parallel workers (default: 1)
    --dry-run                     # Optional: Validate without API calls
    --continue-from <tile>        # Optional: Resume from specific tile
    --limit <n>                   # Optional: Process only first N tiles
```

### Configuration File Structure

Configs in `prompts/configs/` control detection behaviour:

```json
{
  "version": "config_name",
  "description": "Human-readable description",
  "hypothesis": "H1",
  "model": "gemini-3-flash",
  "instruction_file": "system_instruction.md",
  "temperature": 1.0,
  "max_output_tokens": 8192,
  "thinking_level": "minimal",
  "examples": [
    {"path": "neutral-naming/example_01.png", "label": "Positive", "category": "canonical_positive"}
  ]
}
```

**Key fields:**

- `model` — VLM model identifier
- `instruction_file` — System instruction filename (in `prompts/system-instructions/`)
- `temperature` — Sampling temperature (0.0–2.0)
- `thinking_level` — Model reasoning level (`minimal`, `low`, `medium`, `high`)
- `examples` — Few-shot example library with labels and categories

### Output Files

For each processed tile:

- `{tile_name}.geojson` — Detection results
- `{tile_name}.meta.json` — API metadata

**GeoJSON detection format:**

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [x, y]},
      "properties": {
        "confidence": 0.85,
        "subtype": "burial_mound",
        "tile_id": "tile_name"
      }
    }
  ]
}
```

### Multi-Pass Execution

For experiments requiring multiple passes (K runs):

```bash
for i in $(seq -w 1 5); do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/<config>.json \
        --manifest inputs/tiles/<manifest>.json \
        --output-dir outputs/<experiment>/pass_${i}
done
```

---

## Accuracy Evaluation (`6_accuracy_report.py`)

Compares detections against ground truth to calculate performance metrics.

### Usage

```bash
python scripts/6_accuracy_report.py \
    --pred <detections.geojson>   # Required: Predicted detections
    --bounds <bounds.geojson>     # Required: Region bounds
    --template <truth.geojson>    # Required: Ground truth reference
```

### Metrics Calculated

**Symbol-level metrics:**

- **Precision** — TP / (TP + FP) — How many detections are correct
- **Recall** — TP / (TP + FN) — How many ground truth mounds were found
- **F1** — Harmonic mean of precision and recall
- **95% CI** — Bootstrap confidence intervals

**Tile-level classification:**

- **MCC** — Matthews Correlation Coefficient (balanced accuracy measure)
- **Sensitivity** — True positive rate for tiles
- **Specificity** — True negative rate for tiles

### Matching Logic

- Detections within tolerance distance (default: 20m) of ground truth are matches
- Unmatched detections are false positives (FP)
- Unmatched ground truth points are false negatives (FN)

---

## Consensus Analysis (`7_analyse_consensus.py`)

Analyses detection stability across multiple independent passes.

### Usage

```bash
python scripts/7_analyse_consensus.py \
    --input-dir <experiment_dir>  # Directory containing pass_01, pass_02, etc.
    --output <output.json>        # Output analysis file
    --passes <n>                  # Number of passes to analyse
    --tolerance <m>               # Spatial clustering tolerance (default: 20m)
```

### Output Metrics

- **Vote counts** — How many passes detected each location
- **Consensus threshold** — Minimum votes to consider a detection stable
- **Stability analysis** — Distribution of detections by vote count
- **Systematic failures** — Locations consistently missed or falsely detected

### Interpretation Guide

| Vote Count | Interpretation |
|------------|----------------|
| K/K | Highly stable detection, likely true positive |
| (K-1)/K | Stable with occasional miss |
| ~K/2 | Marginal, sensitive to stochastic variation |
| 1/K | Unstable, likely false positive or edge case |

---

## Two-Stage Analysis (`8_analyse_proposer_consensus.py`)

For two-stage (proposer-verifier) workflows where a high-recall proposer generates candidates and a precision-focused verifier filters them.

### Usage

```bash
python scripts/8_analyse_proposer_consensus.py \
    --proposer-dir <proposer_outputs>   # Proposer detection results
    --verifier-dir <verifier_outputs>   # Verifier filtered results
    --output <analysis.json>            # Combined analysis output
```

### Analysis Output

- Proposer recall (candidates generated)
- Verifier precision (candidates retained)
- Combined F1 of the two-stage pipeline
- Candidate attrition analysis

---

## Output Directory Conventions

Organise experiment outputs consistently:

```text
outputs/
├── phase1-library/           # Phase 1 library construction
│   ├── pass_01/
│   ├── pass_02/
│   ├── ...
│   ├── merged_detections.geojson
│   └── consensus_analysis.json
├── phase2a-h1-baseline/      # Hypothesis testing
│   ├── pass_01/
│   ├── ...
│   └── accuracy_report.json
└── production/               # Final deployment runs
    └── full_region/
```

**Naming conventions:**

- `pass_XX` — Individual detection passes (zero-padded)
- `merged_detections.geojson` — Combined multi-pass results
- `consensus_analysis.json` — Vote count analysis
- `accuracy_report.json` — Evaluation metrics

---

## Cost Estimation

API costs depend on model and tile count:

| Model | Cost/Call | 100 Tiles | 1000 Tiles |
|-------|-----------|-----------|------------|
| Gemini Flash | ~$0.003 | ~$0.30 | ~$3.00 |
| Gemini Pro | ~$0.02 | ~$2.00 | ~$20.00 |

**Multi-pass cost:**

- 5 passes × 20 tiles = 100 calls ≈ $0.30 (Flash)
- 10 passes × 100 tiles = 1000 calls ≈ $3.00 (Flash)
