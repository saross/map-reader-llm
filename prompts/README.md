# Prompts & Versioning

This directory contains the configurations and system instructions for LLM inference. We use a **Modular / Data-Driven** architecture to ensure reproducibility.

## Structure

- **`configs/*.json`**: Run configurations. See **[docs/PIPELINES.md](../docs/PIPELINES.md)** for active pipelines.
- **`system-instructions/*.md`**: System instructions (the "Brain" or "Logic").

## File Naming Convention

Instruction files follow the pattern: `{workflow}_{M/E-level}_{H5-level}.md`

This naming reflects two **orthogonal experimental factors**:

1. **M/E level** (Modality/Elaboration) - controls **positive guidance** (what TO detect)
2. **H5 level** (Negative Text Treatment) - controls **negative guidance** (what NOT to detect)

### M/E Levels (Positive Guidance)

| M/E Level | Filename Component | Description |
|-----------|-------------------|-------------|
| Image-only | `image-only` | Minimal text, visual examples only |
| Brief-text | `brief-text` | Concise text descriptions, no images |
| Brief-text+image | `brief-text-image` | Concise text + visual examples |
| Verbose-text | `verbose-text` | Detailed text descriptions, no images |
| Verbose-text+image | `verbose-text-image` | Detailed text + visual examples |

### H5 Levels (Negative Guidance)

| H5 Level | Filename Suffix | Exclusion Text |
|----------|----------------|----------------|
| Minimal | `_minimal` or *(no suffix)* | None - examples labelled "Negative" only |
| Terse | `_terse` | Brief (1-2 sentences) |
| Verbose | `_verbose` | Detailed (full section with subsections) |

### Naming Examples

| Filename | Positive Guidance | Negative Guidance | Interpretation |
|----------|-------------------|-------------------|----------------|
| `detect_image-only.md` | Minimal text, images | None | H1 baseline - image-only with no exclusion text |
| `detect_verbose-text-image.md` | Detailed text + images | None | H1 baseline - verbose positive, no exclusion text |
| `detect_verbose-text-image_terse.md` | Detailed text + images | Brief exclusion text | Verbose positive + terse negative |
| `detect_verbose-text-image_verbose.md` | Detailed text + images | Detailed exclusion text | Both positive and negative guidance are verbose |
| `detect_image-only_terse.md` | Minimal text, images | Brief exclusion text | Minimal positive + terse negative |

### Key Points

- **Orthogonal factors:** Any M/E level can be combined with any H5 level
- **Text-only M/E levels** (brief-text, verbose-text) have no H5 variants because negative guidance requires visual examples
- **All image-using files use Scale-8 library** (17 examples: Canon+ 4, Canon- 2, HP 4, HN 4, null 3)
- **Config files (.json) always use minimal labels** ("Positive"/"Negative"); text elaboration controlled only in instruction files (.md)

### Structural Consistency

Within each M/E level, positive guidance text is **identical** across all H5 variants. Only the exclusion guidance section varies:

- `detect_verbose-text-image.md` - NO exclusion section
- `detect_verbose-text-image_terse.md` - Same positive text + brief exclusion section
- `detect_verbose-text-image_verbose.md` - Same positive text + detailed exclusion section

This ensures that any performance differences between H5 levels can be attributed solely to the negative guidance, not to changes in positive guidance.

### Additional Suffixes

| Suffix | Factor | Description |
|--------|--------|-------------|
| `_canonical-last` | H4 | Ordering: hard examples first, legend last |
| `_random-order` | H4 | Ordering: random permutation (documented seed) |

**Note:** Model selection (Flash vs Pro) and temperature are runtime parameters passed to the script, not encoded in the config.

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

### Detection Instruction Files (11 total)

**Image-using M/E levels × 3 H5 levels = 9 files:**

| M/E Level | Minimal | Terse | Verbose |
|-----------|---------|-------|---------|
| Image-only | `detect_image-only.md` | `detect_image-only_terse.md` | `detect_image-only_verbose.md` |
| Brief-text+image | `detect_brief-text-image.md` | `detect_brief-text-image_terse.md` | `detect_brief-text-image_verbose.md` |
| Verbose-text+image | `detect_verbose-text-image.md` | `detect_verbose-text-image_terse.md` | `detect_verbose-text-image_verbose.md` |

**Text-only M/E levels × 1 H5 level = 2 files:**

| M/E Level | H5=Minimal |
|-----------|------------|
| Brief-text | `detect_brief-text.md` |
| Verbose-text | `detect_verbose-text.md` |

### Detection Config Files

Config files (`.json`) pair with instruction files and specify the few-shot library. See `configs/` directory for full inventory.

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

Available for: image-only, brief-text-image, verbose-text-image (at each H5 level)

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

### H5: Negative Text Treatment

Tests how much exclusion guidance to provide for negative examples.

| H5 Level | Suffix | Description |
|----------|--------|-------------|
| Minimal | `_minimal` or none | "Negative" label only - images speak for themselves |
| Terse | `_terse` | Brief exclusion guidance (1-2 sentences) |
| Verbose | `_verbose` | Detailed exclusion guidance (6 subsections) |

H5 is tested at all 3 image-using M/E levels (9 cells total, 6 net new after H1 overlap).

### H7: Temperature

Temperature is a **runtime parameter**, not a config variant. The OFAT design (preregistration Section 8.4.7) tests T ∈ {0.0, 0.3, 0.7, 1.0, 1.3} at optimal M/E. No separate config files needed.

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

## Migration History

### v4.6 Changes (2026-01-14)

H5 naming updated from binary (`_hardneg`) to three-level system:

| Old Pattern | New Pattern |
|-------------|-------------|
| `*_hardneg.*` | `*_verbose.*` (detailed exclusion) |
| *(no suffix)* | `*_minimal.*` or no suffix (no exclusion text) |
| *(new)* | `*_terse.*` (brief exclusion) |

H5 now tested at all 3 image-using M/E levels (not just optimal).

### v4.2 Changes (2026-01-08)

| Old Pattern | New Pattern |
|-------------|-------------|
| `detect_text-only*` | `detect_brief-text*` |
| `detect_text-image*` | `detect_brief-text-image*` |
| `*_elaborate*` | `*verbose*` |

### Files Removed

| File | Reason |
|------|--------|
| `detect_text-only_hardneg.*` | Text-only tested at H5=Minimal only |
| `detect_text-only_elaborate_hardneg.*` | Text-only tested at H5=Minimal only |
| `detect_text-image.md` | Duplicate of `detect_brief-text-image.md` |

## How to Create a New Version

To test a new hypothesis (e.g., "Does removing hard negatives improve recall?"):

1. Create `configs/propose_image-only_no-negatives.json`
2. Copy content from `propose_image-only.json`
3. Modify the `examples` array
4. Run: `python scripts/4_detect_mounds_batch.py --config prompts/configs/propose_image-only_no-negatives.json`

This preserves the baseline exactly while capturing your experiment as a distinct entity.
