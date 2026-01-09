# Prompts & Versioning

This directory contains the configurations and system instructions for LLM inference. We use a **Modular / Data-Driven** architecture to ensure reproducibility.

## Structure

- **`configs/*.json`**: Run configurations. See **[docs/PIPELINES.md](../docs/PIPELINES.md)** for active pipelines.
- **`system-instructions/*.md`**: System instructions (the "Brain" or "Logic").

## Naming Convention

Prompts follow this pattern: `{workflow}_{modality}[_ordering][_hardneg].json`

| Component | Values | Meaning |
|-----------|--------|---------|
| **workflow** | `detect`, `propose`, `verify` | Single-shot, Two-stage S1, Two-stage S2 |
| **modality** | `image-only`, `brief-text`, `brief-text-image`, `verbose-text`, `verbose-text-image` | What drives the prompt |

Optional variant suffixes:

- `_hardneg`: Includes hard negative examples and exclusion guidance (H5)
- `_canonical-last`: H4-B ordering (hard examples first, legend last)
- `_random-order`: H4-C ordering (random permutation with documented seed)

**Note:** Model selection (Flash vs Pro) is a runtime parameter passed to the script, not encoded in the prompt config.

## Config Schema

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Unique identifier for this config |
| `description` | string | Human-readable description |
| `hypothesis` | string | (Optional) Hypothesis condition this config tests (e.g., "H5-A") |
| `model` | string | Default model (e.g., `gemini-3-flash`) |
| `instruction_file` | string | System instruction filename |
| `temperature` | float | Sampling temperature (default: 1.0) |
| `max_output_tokens` | int | Maximum output tokens (default: 8192) |
| `examples` | array | Few-shot examples with `path`, `label`, and optional `category` |
| `random_seed` | int | (Optional) Seed used for random ordering (H5-C) |
| `ordering_note` | string | (Optional) Documents the ordering logic for this config |

## Active Configs

### Main Detection Configs

| Config | Instruction | Modality | H5 |
|--------|-------------|----------|-----|
| `detect_image-only.json` | `detect_image-only.md` | Image-only | None |
| `detect_image-only_hardneg.json` | `detect_image-only_hardneg.md` | Image-only | Text+Images |
| `detect_brief-text.json` | `detect_brief-text.md` | Brief-text | None |
| `detect_brief-text-image.json` | `detect_brief-text-image.md` | Brief-text+image | None |
| `detect_brief-text-image_hardneg.json` | `detect_brief-text-image_hardneg.md` | Brief-text+image | Text+Images |
| `detect_verbose-text.json` | `detect_verbose-text.md` | Verbose-text | None |
| `detect_verbose-text-image.json` | `detect_verbose-text-image.md` | Verbose-text+image | None |
| `detect_verbose-text-image_hardneg.json` | `detect_verbose-text-image_hardneg.md` | Verbose-text+image | Text+Images |

### Two-Stage Pipeline Configs

| Config | Instruction | Stage | Description |
|--------|-------------|-------|-------------|
| `propose_image-only.json` | `propose_image-only.md` | S1 Proposer | High-recall detection |
| `verify_image-only.json` | `verify_image-only.md` | S2 Verifier | Precision-focused verification |

### H4 Ordering Variants

| Config | Ordering | Description |
|--------|----------|-------------|
| `detect_*_canonical-last.json` | H4-B | Hard examples first, legend last |
| `detect_*_random-order.json` | H4-C | Random permutation (seed 42) |

Available for: image-only, brief-text-image, verbose-text-image (± hardneg)

## Hypothesis-Specific Configs

### H4: Example Ordering

Tests whether the order of few-shot examples affects detection performance.

| Config Pattern | Hypothesis | Ordering | Description |
|--------|------------|----------|-------------|
| `detect_*.json` (base) | H4-A | Canonical-first | Legend positives → nulls (baseline) |
| `detect_*_canonical-last.json` | H4-B | Canonical-last | Hard examples first → legend last |
| `detect_*_random-order.json` | H4-C | Random | Random permutation (seed 42; seeds 43, 44 also tested) |

**Example categories:**

- `canonical`: Legend-derived symbol examples (burial mound, settlement mound, etc.)
- `hard_positive`: False negatives from training evaluation (added post-selection)
- `hard_negative`: False positives from training evaluation (added post-selection)
- `null`: Tiles with no mounds (always included)

**Current status**: Skeleton configs with canonical + null examples only. Hard examples to be added after training tile evaluation.

### H5: Hard Negative Guidance

Tested via `_hardneg` config suffix and corresponding instruction files with exclusion guidance.

### H7: Temperature

Temperature is a **runtime parameter**, not a config variant. The factorial design (preregistration Section 8.4.6) tests T ∈ {0.0, 0.7, 1.0, 1.3} across all config combinations. No separate config files needed.

### H9: Prompt Diversity (Exploratory)

Methodology documented in preregistration Section 8.3.2. Five semantically equivalent instruction variants will be created before holdout evaluation:

| Variant | Example Task Framing |
|---------|---------------------|
| V1 | "Identify burial mound symbols in this map section" |
| V2 | "Detect tumuli markers on this topographic map" |
| V3 | "Find kurgan indicators in this image" |
| V4 | "Locate ancient burial mound cartographic symbols" |
| V5 | "Mark all mound features shown on this Soviet map" |

**Status**: Methodology specified; final instruction files to be created before holdout evaluation.

---

## Migration from Old Names (2026-01-08)

The prompts were reorganised to align with preregistration v4.2 naming conventions.

### Naming Convention Changes

| Old Pattern | New Pattern |
|-------------|-------------|
| `detect_text-only*` | `detect_brief-text*` |
| `detect_text-image*` | `detect_brief-text-image*` |
| `*_elaborate*` | `*verbose*` |

### Files Removed

| File | Reason |
|------|--------|
| `detect_text-only_hardneg.*` | Text-only tested at H5=None only |
| `detect_text-only_elaborate_hardneg.*` | Text-only tested at H5=None only |
| `detect_text-image.md` | Duplicate of `detect_brief-text-image.md` |

## How to Create a New Version

To test a new hypothesis (e.g., "Does removing hard negatives improve recall?"):

1. Create `configs/propose_image-only_no-negatives.json`
2. Copy content from `propose_image-only.json`
3. Modify the `examples` array
4. Run: `python scripts/4_detect_mounds_batch.py --config prompts/configs/propose_image-only_no-negatives.json`

This preserves the baseline exactly while capturing your experiment as a distinct entity.
