# Prompts & Versioning

This directory contains the configurations and system instructions for LLM inference. We use a **Modular / Data-Driven** architecture to ensure reproducibility.

## Structure

- **`configs/*.json`**: Run configurations. See **[docs/PIPELINES.md](../docs/PIPELINES.md)** for active pipelines.
- **`system-instructions/*.md`**: System instructions (the "Brain" or "Logic").

## Naming Convention

Prompts follow this pattern: `{workflow}_{modality}.json`

| Component | Values | Meaning |
|-----------|--------|---------|
| **workflow** | `detect`, `propose`, `verify` | Single-shot, Two-stage S1, Two-stage S2 |
| **modality** | `text-only`, `text-image`, `image-only` | What drives the prompt |

Optional variant suffixes:

- `-hardneg`: Includes hard negative examples and exclusion guidance
- `_canonical-last`: H5-B ordering (hard examples first, legend last)
- `_random-order`: H5-C ordering (random permutation with documented seed)
- `_temp-X.X`: Temperature variant for H9 testing

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

| Config | Instruction | Workflow | Modality | Hard Neg |
|--------|-------------|----------|----------|----------|
| `detect_text-only.json` | `detect_text-only.md` | Single-shot | Text only | ✗ |
| `detect_text-only-hardneg.json` | `detect_text-only-hardneg.md` | Single-shot | Text only | ✓ |
| `detect_text-image.json` | `detect_text-image.md` | Single-shot | Text + Image | ✗ |
| `detect_text-image-hardneg.json` | `detect_text-image-hardneg.md` | Single-shot | Text + Image | ✓ |
| `detect_image-only.json` | `detect_image-only.md` | Single-shot | Image only | ✗ |
| `detect_image-only_canonical-last.json` | `detect_image-only.md` | Single-shot | Image only | ✗ |
| `detect_image-only_random-order.json` | `detect_image-only.md` | Single-shot | Image only | ✗ |
| `detect_image-only-hardneg.json` | `detect_image-only.md` | Single-shot | Image only | ✓ |
| `propose_image-only.json` | `propose_image-only.md` | Two-stage S1 | Image only | ✓ |
| `verify_image-only.json` | `verify_image-only.md` | Two-stage S2 | Image only | ✓ |

## Hypothesis-Specific Configs

### H5: Example Ordering

Tests whether the order of few-shot examples affects detection performance.

| Config | Hypothesis | Ordering | Description |
|--------|------------|----------|-------------|
| `detect_image-only.json` | H5-A | Canonical-first | Legend positives → nulls (baseline) |
| `detect_image-only_canonical-last.json` | H5-B | Canonical-last | Hard examples first → legend last |
| `detect_image-only_random-order.json` | H5-C | Random | Random permutation (seed 42; seeds 43, 44 also tested) |

**Example categories:**

- `canonical`: Legend-derived symbol examples (burial mound, settlement mound, etc.)
- `hard_positive`: False negatives from training evaluation (added post-selection)
- `hard_negative`: False positives from training evaluation (added post-selection)
- `null`: Tiles with no mounds (always included)

**Current status**: Skeleton configs with canonical + null examples only. Hard examples to be added after training tile evaluation.

### H9: Temperature

Temperature is a **runtime parameter**, not a config variant. The 48-condition factorial design (preregistration Section 8.4.6) tests T ∈ {0.0, 0.3, 0.7, 1.0} across all config combinations. No separate config files needed.

### H6: Prompt Diversity

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

## Migration from Old Names (2025-12-23)

The prompts were reorganised for clarity. Old versions archived at `archive/prompts-pre-reorganisation/`.

### Config Files

| Old Name | New Name |
|----------|----------|
| *(V2.3 resurrected)* | `detect_text-only.json` |
| `v3.2_experimental.json` | `detect_text-image.json` |
| `v3.5_clean.json` | `detect_image-only.json` |
| `v3.5_clean_pro.json` | *(deleted — model is runtime param)* |
| `v4.1_recall_augmented.json` | *(deleted — v4.2 performed better)* |
| `v4.2_recall_high_temp.json` | `propose_image-only.json` |
| `v4.6_verifier.json` | `verify_image-only.json` |
| `v4.6_verifier_pro.json` | *(deleted — model is runtime param)* |

### Instruction Files

| Old Name | New Name |
|----------|----------|
| *(V2.3 extracted)* | `detect_text-only.md` |
| `v3.0_system_instruction.md` | `detect_text-image.md` |
| `v3.5_clean_instruction.md` | `detect_image-only.md` |
| `v3.7_visual_instruction.md` | `propose_image-only.md` |
| `v4.6_verifier_instructions.md` | `verify_image-only.md` |

## How to Create a New Version

To test a new hypothesis (e.g., "Does removing hard negatives improve recall?"):

1. Create `configs/propose_image-only_no-negatives.json`
2. Copy content from `propose_image-only.json`
3. Modify the `examples` array
4. Run: `python scripts/4_detect_mounds_batch.py --config prompts/configs/propose_image-only_no-negatives.json`

This preserves the baseline exactly while capturing your experiment as a distinct entity.
