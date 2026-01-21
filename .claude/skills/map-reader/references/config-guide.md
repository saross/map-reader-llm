# Configuration Guide

Complete reference for prompt configuration files used in VLM detection experiments.

---

## Config Selection Table

| Purpose | Config File | Hypothesis | Notes |
|---------|-------------|------------|-------|
| **Library Construction** ||||
| Phase 1 baseline | `library_pure-positive-canon.json` | — | Canon+ (4) and null (3) only |
| Canonical library | `library_canonical.json` | — | Canon+ (4), Canon- (2), null (3) |
| With hard positives | `library_plus-hp.json` | — | Adds HP (4) to canonical |
| **Hypothesis Testing** ||||
| H1 image-only | `detect_image-only.json` | H1 | No text labels on examples |
| H1 brief text | `detect_brief-text-image.json` | H1 | Brief diagnostic labels |
| H1 verbose text | `detect_verbose-text-image.json` | H1 | Full diagnostic text |
| **Text Verbosity (H5)** ||||
| Minimal instruction | `detect_verbose-text-image.json` | H5 | Baseline instruction |
| Terse instruction | `detect_verbose-text-image_terse.json` | H5 | Reduced instruction detail |
| Verbose instruction | `detect_verbose-text-image_verbose.json` | H5 | Extended instruction detail |
| **Library Scale (H8)** ||||
| Scale-4 | `library_scale-4.json` | H8-1 | Minimal: 7 examples |
| Scale-8 | `library_scale-8.json` | H8-2 | Standard: 17 examples |
| Scale-16 | `library_scale-16.json` | H8-3 | Extended: 17+ examples |
| Scale-32 | `library_scale-32.json` | H8-4 | Maximum: 17+ examples |
| **Two-Stage (H2)** ||||
| Proposer | `propose_brief.json` | H2 | High-recall candidate generation |
| Verifier | `verify_brief.json` | H2 | Precision-focused filtering |

---

## Config File Structure

### Required Fields

```json
{
  "version": "config_name",
  "description": "Human-readable description of this configuration",
  "hypothesis": "H1",
  "model": "gemini-3-flash",
  "instruction_file": "detect_image-only.md",
  "temperature": 1.0,
  "max_output_tokens": 8192,
  "examples": []
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Unique config identifier (matches filename) |
| `description` | string | Human-readable purpose description |
| `hypothesis` | string | Preregistered hypothesis being tested (H1-H15) |
| `model` | string | VLM model identifier |
| `instruction_file` | string | System instruction filename |
| `temperature` | float | Sampling temperature (0.0–2.0) |
| `max_output_tokens` | int | Maximum response length |
| `thinking_level` | string | Reasoning depth: minimal, low, medium, high |
| `examples` | array | Few-shot example library |

### Example Library Format

```json
"examples": [
  {
    "path": "neutral-naming/example_01.png",
    "label": "Positive",
    "category": "canonical_positive"
  },
  {
    "path": "neutral-naming/example_09.png",
    "label": "Negative: Triangulation Point ALONE (no mound)",
    "category": "canonical_negative"
  }
]
```

**Categories:**

- `canonical_positive` — Clear positive examples (example_01-04)
- `hard_positive` — Difficult positives, often missed (example_05-08)
- `canonical_negative` — Clear negative examples (example_09-10)
- `hard_negative` — Confusing negatives, often false-alarmed (example_11-14)
- `null` — Empty tiles with no features (example_15-17)

---

## System Instructions

System instructions in `prompts/system-instructions/` define the detection task:

| Instruction File | Purpose |
|------------------|---------|
| `detect_image-only.md` | H1 baseline: image-only detection |
| `detect_brief-text.md` | Brief diagnostic text labels |
| `detect_verbose-text.md` | Verbose diagnostic text |
| `propose_brief.md` | Two-stage proposer (high recall) |
| `verify_brief.md` | Two-stage verifier (high precision) |

---

## Creating New Configs

### 1. Copy an Existing Config

```bash
cp prompts/configs/detect_image-only.json prompts/configs/my_new_config.json
```

### 2. Update Required Fields

- Set unique `version` matching filename
- Update `description` to explain purpose
- Set appropriate `hypothesis` reference
- Modify `examples` array as needed

### 3. Validate Config

```bash
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/my_new_config.json \
    --manifest inputs/tiles/calibration_manifest.json \
    --dry-run
```

---

## Example Library Composition

### Canonical Library (9 examples)

| Slot | Category | Description |
|------|----------|-------------|
| 01-04 | Canon+ | Clear burial mounds |
| 09-10 | Canon- | Triangulation/benchmark alone |
| 15-17 | Null | Empty tiles |

### Scale-8 Library (17 examples)

| Slot | Category | Description |
|------|----------|-------------|
| 01-04 | Canon+ | Clear burial mounds |
| 05-08 | HP | Frequently missed mounds |
| 09-10 | Canon- | Triangulation/benchmark alone |
| 11-14 | HN | Frequent false alarms |
| 15-17 | Null | Empty tiles |

---

## Temperature Guidelines

| Temperature | Behaviour | Use Case |
|-------------|-----------|----------|
| 0.0 | Deterministic | Reproducibility testing |
| 0.5 | Low variance | Conservative detection |
| 1.0 | Standard | Default for most experiments |
| 1.5 | High variance | Exploration, diversity |
| 2.0 | Maximum variance | Not recommended |

---

## Thinking Level Guidelines

| Level | Description | Token Cost | Use Case |
|-------|-------------|------------|----------|
| `minimal` | No extended reasoning | Lowest | Production, cost-sensitive |
| `low` | Brief reasoning | Low | Standard detection |
| `medium` | Moderate reasoning | Medium | Complex cases |
| `high` | Extensive reasoning | Highest | Debugging, analysis |

Based on calibration pilot (2026-01-15), `minimal` is the default for all hypothesis testing.
