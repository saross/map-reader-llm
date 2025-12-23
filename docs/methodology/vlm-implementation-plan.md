# VLM Hypothesis Testing: Implementation Plan

**Document created**: 2024-12-23  
**Purpose**: Guide for stepwise implementation of hypothesis testing prompts  
**Status**: Draft for refinement with Claude Code

---

## Overview

This document outlines the phased approach to testing preregistered hypotheses about VLM prompting strategies for burial mound detection. The approach builds from the existing best-performing prompt (image + minimal text) and systematically tests modifications.

---

## Existing Prompts

| Prompt ID | Description | Status | Current Performance |
|-----------|-------------|--------|---------------------|
| `text_only` | Text descriptions only, no images | ✅ Have | Decent (below image+text) |
| `image_only` | Few-shot examples, minimal text framing | ✅ Have | Similar to image+text |
| `image_minimal_text` | Few-shot examples + brief text instructions | ✅ Have | **Best performer** (v3.2) |
| `two_stage` | Proposer-verifier architecture | ✅ Have | Poor (documented failure) |

---

## Prompts to Construct

| Prompt ID | Description | Required For | Priority |
|-----------|-------------|--------------|----------|
| `image_elaborate_text` | Few-shot examples + detailed text instructions | H2 | High |
| `image_minimal_text_ordered` | Same as baseline but with best examples in final positions | H5 | High |
| `image_minimal_text_hardneg` | Baseline + 4 hard negative examples | H7 | High |
| `prompt_variant_1` through `prompt_variant_5` | Semantically equivalent task phrasings for diverse voting | H6 | Medium |

---

## Phase 1: Text Effect Baseline (H1, H2)

### Purpose
Establish whether text content affects detection performance on holdout set.

### Conditions

| Condition | Prompt | Passes | Hypotheses |
|-----------|--------|--------|------------|
| 1A | `text_only` | 1 | Context only |
| 1B | `image_only` | 1 | H1 (compare to 1C) |
| 1C | `image_minimal_text` | 1 | Baseline |
| 1D | `image_elaborate_text` | 1 | H2 (compare to 1C) |

### Comparisons
- **H1**: 1B vs 1C — Does adding text to images matter?
- **H2**: 1C vs 1D — Does elaborating text help or hurt?

### Expected Outcomes
- H1: No significant difference (1B ≈ 1C)
- H2: Elaborate text does not help (1D ≤ 1C), may hurt recall

### API Calls
4 conditions × 20 tiles × 1 pass = **80 calls**

---

## Phase 2: Few-Shot Library Optimization (H5, H7)

### Purpose
Test whether example ordering and hard negatives improve detection.

### Conditions

| Condition | Prompt | Modification | Hypotheses |
|-----------|--------|--------------|------------|
| 2A | `image_minimal_text` | Baseline (random ordering, no hard negatives) | Reference |
| 2B | `image_minimal_text_ordered` | Best examples in positions 9-12 | H5 |
| 2C | `image_minimal_text_hardneg` | Add 4 hard negative examples | H7 |
| 2D | `image_minimal_text_ordered_hardneg` | Both modifications combined | Exploratory |

### Comparisons
- **H5**: 2A vs 2B — Does ordering matter?
- **H7**: 2A vs 2C — Do hard negatives improve precision without hurting recall?
- **Exploratory**: 2D vs 2B, 2D vs 2C — Do modifications interact?

### Expected Outcomes
- H5: Best-last ordering improves F1 (2B > 2A)
- H7: Hard negatives improve precision, recall stable (2C precision > 2A precision, 2C recall ≈ 2A recall)

### API Calls
4 conditions × 20 tiles × 1 pass = **80 calls**

### Note
Condition 2A may reuse results from Phase 1 Condition 1C if implementation allows.

---

## Phase 3: Voting Optimization (H4, H6)

### Purpose
Confirm voting benefit and test whether prompt diversity improves ensemble.

### Base Prompt
Use best configuration from Phase 2. Likely `image_minimal_text_ordered_hardneg` or best-performing variant. Denote as `optimized_prompt`.

### Conditions

| Condition | Prompt | Passes | Voting | Hypotheses |
|-----------|--------|--------|--------|------------|
| 3A | `optimized_prompt` | 1 | None | Baseline |
| 3B | `optimized_prompt` | 5 | ≥3/5 identical | H4 |
| 3C | `prompt_variants_1-5` | 5 | ≥3/5 diverse | H6 (compare to 3B) |

### Comparisons
- **H4**: 3A vs 3B — Does voting improve F1?
- **H6**: 3B vs 3C — Does prompt diversity improve voting?

### Expected Outcomes
- H4: Voting significantly improves F1 (3B > 3A)
- H6: Diverse prompts further improve F1 (3C > 3B), or at minimum don't hurt

### API Calls
- 3A: 20 tiles × 1 pass = 20 calls
- 3B: 20 tiles × 5 passes = 100 calls
- 3C: 20 tiles × 5 passes = 100 calls
- **Total: 220 calls**

---

## Prompt Construction Specifications

### `image_elaborate_text`

Take existing `image_minimal_text` and add:

```
[Existing few-shot examples]

[ADD THE FOLLOWING TEXT:]

## Detection Criteria

Burial mound symbols on Soviet 1:50,000 topographic maps appear as:
- Small circular or oval shapes, typically 2-4mm diameter at map scale
- Often with radiating hachure lines indicating elevated terrain
- May appear individually or in clusters
- Located on elevated terrain, ridges, or prominent landscape positions

## Exclusion Criteria

Do NOT mark the following as burial mounds:
- Spot heights: small dots accompanied by elevation numbers (e.g., "185")
- Triangulation points: triangles with central dots
- Quarry symbols: similar circular shapes but with distinct internal markings
- Well symbols: circles with specific well notation
- Benchmark symbols: circles with crosshairs or specific survey notation

## Decision Procedure

When uncertain whether a feature is a burial mound:
1. Check for accompanying text or numbers (suggests spot height, not mound)
2. Look for the characteristic hachure pattern indicating elevation
3. Consider landscape context (mounds typically on elevated ground)
4. If still uncertain, err on the side of detection

[Target tile]
```

Adjust specific details based on actual symbol characteristics in your maps.

---

### `image_minimal_text_ordered`

Same few-shot library as baseline, but reorder examples:

**Current order** (assumed random): Examples 1-12 in arbitrary sequence

**New order**:
- Positions 1-8: Less clear examples, edge cases, partial views
- Positions 9-12: Clearest, most unambiguous burial mound examples

**Implementation**:
1. Rank existing positive examples by clarity (researcher judgment)
2. Document ranking criteria before testing
3. Place top 4 in final positions

---

### `image_minimal_text_hardneg`

Add 4 hard negative examples to existing few-shot library:

**Hard negative 1: Spot height**
```
[Image of spot height symbol]
"This is NOT a burial mound. Note the elevation number (e.g., '247') adjacent to the dot, indicating a spot height measurement point."
```

**Hard negative 2: Quarry/pit symbol**
```
[Image of quarry symbol]
"This is NOT a burial mound. This circular shape represents a quarry or excavation pit. Note [distinguishing feature]."
```

**Hard negative 3: Well symbol**
```
[Image of well symbol]
"This is NOT a burial mound. This is a well symbol, indicated by [distinguishing feature]."
```

**Hard negative 4: Other confusable feature**
```
[Image of commonly confused symbol from your false positive analysis]
"This is NOT a burial mound. This represents [feature type]. Note [distinguishing characteristic]."
```

**Placement**: Hard negatives should appear after positive examples but before the target tile.

---

### Prompt Variants for H6 (Diverse Voting)

All variants use identical few-shot examples; only the task instruction text changes.

**Variant 1** (baseline phrasing):
```
"Identify burial mound symbols in this map section"
```

**Variant 2** (alternative terminology):
```
"Detect tumuli markers on this topographic map"
```

**Variant 3** (regional terminology):
```
"Find kurgan indicators in this image"
```

**Variant 4** (formal phrasing):
```
"Locate ancient burial mound cartographic symbols"
```

**Variant 5** (contextual phrasing):
```
"Mark all mound features shown on this Soviet military topographic map"
```

---

## Voting Implementation Requirements

### Spatial Matching Across Passes

When aggregating detections across voting passes, detections at slightly different coordinates must be matched. Specification needed:

- **Matching threshold**: Detections within [X] pixels/meters are considered the same feature
- **Aggregation method**: Centroid of matched detections? First detection coordinates?
- **Tie-breaking**: If detection appears in exactly 2/5 passes at default 3/5 threshold, how is it handled?

### Output Format

Each condition should output:
- Per-tile detection list (coordinates, confidence if available)
- Per-tile TP/FP/FN counts (against ground truth)
- Aggregate precision, recall, F1
- For voting conditions: per-detection agreement count (how many passes detected this feature)

---

## Run Order Summary

| Batch | Phase | Conditions | API Calls | Cumulative |
|-------|-------|------------|-----------|------------|
| 1 | Phase 1 | 1A, 1B, 1C, 1D | 80 | 80 |
| 2 | Phase 2 | 2A*, 2B, 2C, 2D | 60-80 | 140-160 |
| 3 | Phase 3 | 3A, 3B, 3C | 220 | 360-380 |

*2A may reuse 1C results

**Total estimated API calls**: 360-380 (single-model testing)

For H10 (cross-model), multiply by number of models tested.

---

## Decision Points

### After Phase 1
- If H1 shows significant difference (image+text ≠ image-only), investigate further before proceeding
- If H2 shows elaborate text helps (unexpected), reconsider Phase 2 base prompt
- Otherwise, proceed with `image_minimal_text` as base

### After Phase 2
- Select best-performing configuration for Phase 3
- If neither H5 nor H7 show improvement, use baseline for Phase 3
- If both show improvement, test combined version (2D) in Phase 3

### After Phase 3
- Document final optimized pipeline configuration
- Identify techniques for Stage 2 validation

---

## Files to Create/Modify

**Note**: The current codebase uses JSON configs in `prompts/configs/` with markdown system instructions in `prompts/system-instructions/`. The table below maps plan concepts to actual files.

| Plan Concept | Current File | Purpose | Phase |
|--------------|--------------|---------|-------|
| `text_only` | `prompts/configs/detect_text-only.json` | Existing | 1 |
| `image_only` | `prompts/configs/detect_image-only.json` | Existing | 1 |
| `image_minimal_text` | `prompts/configs/detect_text-image.json` | Existing | 1, 2 |
| `image_elaborate_text` | **Create** variant config | H2 elaborated text | 1 |
| `image_minimal_text_ordered` | **Create** variant config | Ordered examples | 2 |
| `image_minimal_text_hardneg` | **Create** variant config | Hard negatives | 2 |
| `prompt_variants` | **Create** 5 variant configs | Diverse voting | 3 |
| Voting logic | `scripts/7_analyze_consensus.py` | Existing | 3 |
| Spatial matching | `scripts/lib_advanced_metrics.py` | Existing | 3 |
| Metrics | `scripts/lib_advanced_metrics.py` | Existing | All |

---

## Next Steps

1. [ ] Confirm hard negative categories from false positive analysis
2. [ ] Rank existing positive examples for ordering experiment
3. [ ] Construct `image_elaborate_text` prompt
4. [ ] Specify spatial matching threshold for voting
5. [ ] Implement voting aggregation logic
6. [ ] Run Phase 1 on holdout set
7. [ ] Analyze Phase 1 results before proceeding to Phase 2

---

*Document version: 1.0*  
*To be refined during implementation*
