# CC Instructions: Preregistration Simplifications and Additions

## Document
`preregistration.md`

## Overview

This document implements the simplifications and additions discussed to streamline the experimental design while maintaining scientific rigor. Changes include:

1. Merge H1+H2 into single M/E hypothesis
2. Update H5 with directional prediction (canonical-last > canonical-first)
3. Simplify H7 from 4 levels to 3 levels
4. Reduce H9 from 5 temperatures to 4
5. Merge H3+H10 into single two-stage hypothesis
6. Merge H6+H11 into diversity mechanisms hypothesis
7. Reduce text-only temperature testing to T=1.0 only
8. Add H18 (overlap/stride) as Tier B exploratory
9. Reorganize exploratory hypotheses into tiers
10. Add Section 12: Future Directions
11. Update budget calculations throughout

---

## Change 1: Merge H1 and H2 into Single M/E Hypothesis

### Rationale
H1 (text modality) and H2 (text elaboration) are testing the same underlying factor — the 5-level M/E factor. Presenting them as one hypothesis with planned contrasts is cleaner.

### Location
Section 5, replace H1 and H2 with merged hypothesis

### Replace H1 (lines ~398-421) and H2 (lines ~423-459) with:

```markdown
### H1: Modality and Elaboration Level Affects Detection Performance

**Background**: The text-image interference literature (Vo et al., 2025) found VLMs override visual analysis with textual priors. This effect may not apply to novel domain content. Additionally, preliminary testing suggested verbose instructions do not improve over brief instructions.

**Predictions**:
1. Text modality will not significantly affect detection performance for this novel domain task
2. Verbose text will not significantly improve F1 compared to brief text
3. Image-based conditions will outperform text-only conditions

**Test**: Compare detection performance across 5 modality/elaboration levels:

| Level | Text | Images | Description |
|-------|------|--------|-------------|
| Image-only | Minimal | Yes | Few-shot visual examples with minimal task instruction |
| Brief-text | Brief | No | Text-only with concise symbol descriptions |
| Brief-text+image | Brief | Yes | Brief text combined with visual examples |
| Verbose-text | Verbose | No | Text-only with comprehensive descriptions |
| Verbose-text+image | Verbose | Yes | Verbose text combined with visual examples |

**Text elaboration levels**:

All levels describe the same content categories (canonical symbols + hard positive edge cases) at different levels of detail:

| Level | Canonical Symbols | HP Edge Cases | Word Count |
|-------|-------------------|---------------|------------|
| Minimal | Task instruction only | None | ~50 |
| Brief | Terse descriptions | Terse mention ("symbols may be occluded") | ~200-300 |
| Verbose | Detailed descriptions | Detailed guidance on types + variants | ~500-700 |

**Orthogonality with H7**: H1 controls detail level for **positives** (canonical symbols + hard positive edge cases). H7 controls presence of **negative** guidance (exclusion text + hard negative images). These are independent dimensions.

**Text-modality consistency**: Identical text is used across modalities (Brief-text = Brief+image text; Verbose-text = Verbose+image text). This isolates the effect of adding visual examples.

**Analysis**:

- Primary: One-way ANOVA across 5 M/E levels
- Planned contrasts:
  - Image-only vs Brief+image (does adding text help?)
  - Brief+image vs Verbose+image (does more detail help?)
  - Brief-text vs Brief+image (do images help?)
  - Text-only conditions vs Image-using conditions (modality effect)
- Two-tailed tests for modality comparisons
- One-tailed for elaboration: H0: verbose ≤ brief; H1: verbose > brief

**Text-only note**: Text-only conditions serve primarily as academic baselines to characterize VLM capability without visual examples. The operationally-relevant comparisons are among image-using conditions.

**Advance to Stage 2 if**: Significant differences detected between levels, suggesting modality/elaboration choices matter for this domain.

---
```

### Update subsequent hypothesis numbers

H3 becomes H2, H4 becomes H3, etc. **OR** keep original numbers for traceability and note the merger in the changelog. I recommend keeping original numbers with a note.

**Add after the merged H1**:

```markdown
*Note: H2 has been merged into H1. The original H2 (text elaboration) is now addressed via planned contrasts within H1.*

---
```

---

## Change 2: Update H5 with Directional Prediction

### Location
Section 5, H5 (Example Ordering)

### Current prediction (line ~528):
```markdown
**Prediction**: The relative placement of canonical examples versus hard examples will affect detection performance.
```

### Replace with:
```markdown
**Prediction**: Canonical-last ordering will produce higher F1 than canonical-first ordering.

**Rationale**: Recency bias in VLM attention means final examples have outsized influence on schema formation. Placing clean prototypes (canonical examples) in the final positions should anchor the model's representation more effectively than placing them first.

**Directional hypothesis**: H0: canonical-last ≤ canonical-first; H1: canonical-last > canonical-first
```

### Update analysis section (line ~548):
Current:
```markdown
**Analysis**:

- Primary: 3 × 3 ANOVA (Ordering × M/E subset)
- Test for O × M/E interaction
- If no interaction: report main effect of ordering pooled across M/E levels
```

Replace with:
```markdown
**Analysis**:

- Primary: 3 × 3 ANOVA (Ordering × M/E subset)
- Planned contrast: canonical-last vs canonical-first (one-tailed)
- Test for O × M/E interaction
- If no interaction: report main effect of ordering pooled across M/E levels
- Random ordering provides baseline for comparison
```

---

## Change 3: Simplify Hard Negatives Hypothesis to 3 Levels (Now H5)

### Rationale
The Text-only H5 condition (exclusion text without hard negative images) is practically odd — who would describe hard negatives without showing them? Dropping this gives a cleaner design focused on practical questions.

### Location
Section 5, H5 (Hard Negatives) — formerly H7

### Replace the 2×2 table (lines ~629-637) with:

```markdown
**Test**: Compare 3 hard negative conditions:

| Condition | Exclusion Text | Emp-HN Images | Description |
|-----------|----------------|---------------|-------------|
| None | No | No | Baseline: positive examples only, no exclusion guidance |
| Images-only | No | Yes | Hard negative images with minimal labels ("Negative") |
| Text+Images | Yes | Yes | Hard negative images with explicit explanatory labels |

**What H5 tests**:

- Does showing Emp-HN images help? (None vs Images-only)
- Does adding explanatory text to Emp-HN images help? (Images-only vs Text+Images)

**Note**: The Text-only condition (exclusion text without images) was excluded as practically implausible — deployment would not describe hard negatives without showing them.
```

### Replace the 2×2 H7 Confirmatory design (lines ~650-660) with:

```markdown
**H5 Confirmatory design**:

After Strand 1 identifies optimal M/E level, test all 3 H5 levels at that M/E:

| H5 Level | Exclusion Text | Emp-HN Images | Image Labels |
|----------|----------------|---------------|--------------|
| None | No | No | — |
| Images-only | No | Yes | Minimal ("Negative") |
| Text+Images | Yes | Yes | Detailed (with explanation) |
```

### Update library composition table (after our earlier corrections):

```markdown
**Library composition by H5 level**:

| H5 Level | Canon+ | Canon- | HP | Emp-HN | Nulls | Total |
|----------|--------|--------|-----|--------|-------|-------|
| None | 4 | 2 | 4 | 0 | 3 | 13 |
| Images-only | 4 | 2 | 4 | 3 | 3 | 16 |
| Text+Images | 4 | 2 | 4 | 3 | 3 | 16 |

**Note**: Canon- (legend-derived negatives) are always included to provide baseline visual context. Only H8 Pure tests without Canon-.
```

### Update analysis (lines ~681-687):

```markdown
**Analysis**:

- Primary: One-way ANOVA across 3 H5 levels
- Planned contrasts:
  - None vs Images-only (do Emp-HN images help precision?)
  - Images-only vs Text+Images (does explanatory text add value?)
- Secondary: Parallel analysis on recall to confirm no significant harm
- Tertiary: Analysis on F1 to assess net benefit
```

### Update H5 Confirmatory totals (lines ~1662-1665):

```markdown
**H5 Confirmatory totals:**

- 1 M/E × 3 H5 × 4 T = **12 cells**
- **API calls**: 12 × K=10 × 60 tiles = **7,200 calls** (~$11)
```

---

## Change 4: Reduce Temperature Hypothesis to 4 Levels (Now H7)

### Location
Section 5, H7 (Temperature) — formerly H9

### Replace temperature table (lines ~753-761):

```markdown
**Test**: Compare detection performance across 4 temperature levels:

| Level | Temperature | Rationale |
|-------|-------------|-----------|
| 1 | 0.0 | Minimum (deterministic) |
| 2 | 0.7 | Moderate variance |
| 3 | 1.0 | Vendor default |
| 4 | 1.3 | Above default (conservative extension) |

**Rationale for level selection**: Preliminary testing found T<1.0 degraded performance. This design brackets the likely optimal range (0.7–1.3) while including the deterministic baseline (0.0) for comparison. The 0.3 level was dropped as unlikely to be optimal.
```

### Update analysis (lines ~762-767):

```markdown
**Analysis**:

- One-way ANOVA across 4 temperature levels
- Planned contrasts: T=1.0 vs each other level
- Examine temperature × voting interaction via post-hoc analysis
```

---

## Change 5: Merge Two-Stage Hypotheses into Single Hypothesis (Now H2)

### Location
Section 5, replace old H3 (Coarse-to-Fine) with new H2 that includes both directions

### Replace old H3 entirely with:

```markdown
### H2: Two-Stage Pipelines Do Not Improve Detection

**Status**: Confirmatory (architectural)

**Background**: Two-stage pipelines are recommended in general ML but lack VLM-specific evidence. Two directions are possible:

1. **Coarse-to-fine (proposer-verifier)**: Liberal first pass identifies candidates; strict second pass verifies. Preliminary testing found this degraded performance, likely due to context loss when cropping candidate regions.

2. **Fine-to-coarse (context expansion)**: Standard detection first; uncertain cases re-queried with larger tile for additional context.

**Prediction**: Neither two-stage architecture will improve F1 over single-stage detection with voting.

**Test**: Compare at optimal single-stage configuration:

| Condition | Architecture | Description |
|-----------|--------------|-------------|
| A (baseline) | Single-stage | Optimal config with consensus voting |
| B | Coarse-to-fine | Liberal proposer → strict verifier |
| C | Fine-to-coarse | Standard detection → context-expanded re-query for uncertain cases |

**Coarse-to-fine implementation (Condition B)**:
- Stage 1: Detection with lower confidence threshold
- Stage 2: Crop candidate regions, verify with focused prompt

**Fine-to-coarse implementation (Condition C)**:
1. Stage 1: Standard detection on 512×512 tiles with 5-pass voting
2. Identify uncertain candidates: Detections with 2/5 or 3/5 agreement
3. Stage 2: For each uncertain candidate, extract larger tile (~1024×1024) centered on candidate, re-query with verification prompt

**Analysis**: 
- One-tailed tests: H0: two-stage ≥ single-stage; H1: two-stage < single-stage
- Prediction is that H0 will not be rejected for either architecture

**Stopping rule**: Two-stage architectures will only be pursued further if either demonstrates F1 at least 0.05 higher than single-stage. Given the inherent cost (~2× API calls) and complexity overhead, parity or marginal improvement would not justify adoption.

**Advance to Stage 2 if**: Either two-stage approach shows F1 improvement of at least 0.05 over single-stage (would contradict preliminary findings).

---
```

### Remove old H10 from Section 6
Delete old H10 entirely from exploratory hypotheses (it's now part of confirmatory H2).

---

## Change 6: Merge Diversity Hypotheses into Single Hypothesis (Now H9)

### Location
Section 6, replace old H6 and old H11 with new H9 (merged hypothesis)

### Replace old H6 (lines ~560-610) and old H11 (lines ~892-914) with:

```markdown
### H9: Diversity Mechanisms Improve Consensus Voting

**Status**: Exploratory (Tier A)

**Background**: Consensus voting with identical passes may produce correlated errors. Three mechanisms could improve ensemble diversity:

1. **Text diversity**: Semantically equivalent but differently phrased prompts
2. **Image diversity**: Different hard examples sampled per pass
3. **Temperature diversity**: Different temperatures per pass

These may be redundant (all just increase output variance) or complementary (each breaks different correlation patterns).

**Test**: Compare each mechanism against a fixed baseline, plus combined condition:

| Condition | Text | Images | Temperature | Description |
|-----------|------|--------|-------------|-------------|
| A (baseline) | Fixed | Fixed | Fixed (T=1.0) | Identical passes |
| B | Varied | Fixed | Fixed | Text diversity only |
| C | Fixed | Varied | Fixed | Image diversity only |
| D | Fixed | Fixed | Varied | Temperature diversity only |
| E | Varied | Varied | Varied | Full diversity |

**Implementation details**:

*Text variation (Conditions B, E)*:
- 5 semantically equivalent prompt variants
- Each pass uses a different variant
- Same structure, varied vocabulary (identify/detect/find/locate/mark)
- See Section 8.3.3 for specification

*Image variation (Conditions C, E)*:
- Hard examples (HP and Emp-HN) resampled per pass
- Canonical examples (Canon+, Canon-) and null tiles remain fixed
- Frequency-capped sampling per Section 8.4.4

*Temperature variation (Conditions D, E)*:
- 5 temperatures across passes: T = [0.7, 0.85, 1.0, 1.15, 1.3]
- Spans range around optimal, excludes 0.0 (deterministic, no diversity value)

**Analysis**:

- Primary: Compare each diversity condition (B, C, D) to baseline (A)
  - One-tailed tests: H0: diversity ≤ baseline; H1: diversity > baseline
- Secondary: Compare full diversity (E) to best single mechanism
- Tertiary: Error correlation analysis across passes within each condition

**Predictions**: No strong directional predictions (exploratory). Possible outcomes:
1. One dominant mechanism (e.g., image diversity helps, others don't)
2. Additive benefits (each helps; E is best)
3. Redundancy (all help equally; E ≈ B ≈ C ≈ D)
4. No benefit (baseline voting is sufficient)

**Cost**: 5 conditions × K=5 passes × 60 tiles = 1,500 API calls (~$2.25)

**Trigger**: Run after optimal configuration identified from main factorial.

---
```

### Remove H11 from Section 6
Delete H11 entirely (now merged into H6).

---

## Change 7: Text-Only at T=1.0 Only

### Rationale
Text-only conditions are academic baselines; optimizing their temperature is unnecessary.

### Location
Section 8.4.7 (Stranded Factorial Design), update Strand 1 design

### Replace the text-only portion of Strand 1 (lines ~1632-1638):

```markdown
*Text-only modalities (2 levels) — tested at T=1.0 only:*

| M/E Level | H5=None |
|-----------|---------|
| Brief-text | ✓ |
| Verbose-text | ✓ |

**Note**: Text-only modalities are tested at T=1.0 only (vendor default) and H5=None only (no hard negative images available). Temperature optimization is reserved for image-using conditions. This reduces text-only cells from 20 to 2.
```

### Update Strand 1 totals:

```markdown
**Strand 1 totals:**

| Component | Cells |
|-----------|-------|
| Image M/E (3) × H7 (2) × T (4) | 24 |
| Text M/E (2) × T=1.0 × H7=None | 2 |
| **Total** | **26** |

**API calls**: 26 × K=10 × 60 tiles = **15,600 calls** (~$23)
```

---

## Change 8: Add Overlap/Stride Hypothesis as Tier B Exploratory (Now H13)

### Location
Section 6 (Exploratory Hypotheses), Tier B, add new H13

### Add new hypothesis:

```markdown
### H13: Tile Overlap Affects Detection Performance

**Status**: Exploratory (Tier B)

**Background**: Current tile generation uses 64-pixel overlap (12.5%), which literature suggests is the minimum for statistically significant improvement. Higher overlap may improve edge detection at the cost of more API calls.

**Research question**: Does increasing tile overlap improve detection performance, and what is the optimal overlap percentage?

**Test**: Compare detection performance across 3 overlap conditions:

| Condition | Overlap | % of Tile | Stride | Tiles per Map | API Multiplier |
|-----------|---------|-----------|--------|---------------|----------------|
| Current | 64px | 12.5% | 448px | ~90 | 1.0× |
| Medium | 128px | 25% | 384px | ~110 | ~1.2× |
| High | 256px | 50% | 256px | ~180 | ~2.0× |

**Implementation notes**:

- Ground truth (symbol locations) remains unchanged
- Tile boundaries change, requiring regeneration of tile sets
- Same holdout *region* evaluated, but tile count differs
- All conditions tested at optimal configuration from main factorial

**Analysis**:

- Primary: One-way ANOVA across 3 overlap conditions
- Secondary: Cost-efficiency analysis (F1 improvement per additional API call)
- Tertiary: Edge-effect analysis (do symbols near tile boundaries show greater improvement?)

**Predictions**: Based on literature, expect:
- Medium (25%) to show improvement over Current (12.5%)
- High (50%) to show diminishing returns over Medium
- Optimal likely in 25-50% range

**Trigger**: Run after main factorial if budget allows (~$8 additional)

**Cost**: 3 conditions × K=10 × variable tiles ≈ 3,800 calls average (~$6)

---
```

---

## Change 9: Reorganize Exploratory Hypotheses into Tiers

### Location
Section 6 header and structure

### Replace Section 6 header and add tier structure:

```markdown
## 6. Exploratory Hypotheses

*These analyses will be conducted and reported but are not confirmatory. Results will be interpreted cautiously and framed as hypothesis-generating. Not included in FDR correction.*

### Tier A: Run in Stage 1 (Essential)

These exploratory hypotheses are essential for the paper's contribution and will be run regardless of budget constraints.

---

### H9: Diversity Mechanisms Improve Consensus Voting
[merged diversity content as above]

---

### Tier B: Run If Budget Allows

These hypotheses address important practical questions but can be deferred if budget is constrained.

---

### H10: Training Pool Size Effects on Library Quality
[old H14 content]

---

### H11: Tile Size Effects on Detection Performance

**Status**: Exploratory (Tier B, conditional)

**Trigger**: Run only if optimal configuration from main factorial achieves F1 < 0.85

[Update existing content to reflect 512 vs 384 comparison, not larger tiles]

**Updated test design**:

| Condition | Tile Size | Symbol Ratio | API Multiplier |
|-----------|-----------|--------------|----------------|
| Current | 512×512 | 3.9-9.8% | 1.0× |
| Smaller | 384×384 | 5.2-13% | ~1.8× |

**Rationale**: Literature suggests current tile size places symbols at the upper edge of acceptable ratio. If we plateau below F1=0.85, smaller tiles (better symbol:tile ratio) are more likely to help than larger tiles.

---

### H12: Hard Positive to Hard Negative Ratio
[old H17 content]

---

### H13: Tile Overlap Affects Detection Performance
[new overlap content as above]

---

### Tier C: Deferred to Future Work

These hypotheses are beyond the scope of the current study. See Section 12 for discussion.

- **H14**: Cross-model consistency (Claude, GPT)
- **H15**: Cross-model voting

---
```

---

## Change 10: Add Section 12 (Future Directions)

### Location
After Section 11 (Preregistration Checklist), before Section 12 (Outstanding Questions — renumber to 13)

### Add new section:

```markdown
## 12. Future Directions

*The following techniques were considered but are beyond the scope of this study. They are documented here for transparency and as potential directions for follow-on research.*

### 12.1 Cross-Model Generalization (H12, H13)

**Cross-architecture validation**: Testing whether optimizations transfer across VLM providers (Gemini → Claude, GPT) would strengthen generalizability claims but requires substantial additional budget and navigating different API constraints.

**Cross-model ensemble voting**: Voting across architecturally different models may provide more diverse error patterns than within-model voting. However, this requires standardized output formats and multiplies cost by the number of models.

*Deferred to potential Paper 2: "Do VLM symbol extraction strategies generalize across architectures?"*

### 12.2 Multi-Scale Fusion

Processing tiles at multiple sizes (e.g., 256×256 and 512×512) and merging detections could leverage the strengths of each scale:
- Smaller tiles: Better symbol resolution and recognition
- Larger tiles: Better contextual information for disambiguation

Fusion strategies (confidence-weighted, cascaded, learned) require separate investigation.

*Deferred pending single-scale optimization.*

### 12.3 Tile Size × Stride Interaction

Optimal tile size and stride may be interdependent. A full factorial (multiple sizes × multiple strides) would be expensive but could reveal interactions missed by testing each factor independently.

*Sequential testing specified in H16/H18; full interaction analysis deferred.*

### 12.4 Automated Library Construction

If the optimized pipeline achieves stable F1 ≥ 0.85, automated library construction becomes feasible:
1. Run initial detection with canonical examples only
2. Identify systematic false positives and false negatives
3. Automatically select hard examples for library
4. Iterate until performance stabilizes

This would enable deployment on new maps with only legend input required.

*Stretch goal if primary optimization succeeds.*

### 12.5 Symbol-Specific Optimization

Different symbol types (burial mound, settlement mound, composite symbols) may benefit from different detection parameters or prompting strategies. Per-class optimization requires sufficient examples of each type and would multiply the experimental conditions.

*Deferred pending aggregate optimization.*

### 12.6 Transfer to Other Map Series and Imagery Types

The ultimate goal is a generalizable approach applicable to:
- Other Soviet topographic map series and scales
- Historical maps from other sources (Austro-Hungarian, Ottoman, etc.)
- High-resolution satellite imagery for archaeological feature detection

Transfer testing requires validated baseline performance on the current task.

*Planned as follow-on research program.*

---
```

### Renumber subsequent sections
- Current Section 12 (Outstanding Questions) → Section 13
- Current Section 13 (Conflict of Interest) → Section 14
- etc.

---

## Change 11: Update Summary Tables

### Note
The summary tables below use the **new hypothesis numbers** from Change 14. See Change 14 for the complete mapping.

### Location
Section 7.1 and 7.2

### Replace Section 7.1 table:

```markdown
### 7.1 Confirmatory Hypotheses

| Hypothesis | Prediction | Test Type | Advance to Stage 2 if... |
|------------|------------|-----------|--------------------------|
| H1 (M/E level) | Affects performance; verbose ≤ brief | ANOVA + contrasts | Significant differences found |
| H2 (two-stage) | Neither architecture helps | One-tailed | Either shows ≥0.05 improvement |
| H3 (consensus voting) | Improvement | One-tailed | Significant improvement |
| H4 (example ordering) | Canonical-last > canonical-first | One-tailed | Significant ordering effect |
| H5 (hard negatives) | Precision ↑, Recall stable | One-way ANOVA (3 levels) | Precision up, recall stable |
| H6 (Flash→Pro transfer) | Transfer works | OFAT sensitivity | Transfer confirmed |
| H7 (temperature) | T=1.0 optimal | One-way ANOVA (4 levels) | Any temperature outperforms 1.0 |
| H8 (library size) | Diminishing returns | One-way ANOVA | Optimal library size identified |
```

### Replace Section 7.2 table:

```markdown
### 7.2 Exploratory Hypotheses

| Hypothesis | Tier | Question | Analysis |
|------------|------|----------|----------|
| H9 (diversity mechanisms) | A | Does variation improve voting? | 5-condition comparison |
| H10 (training pool size) | B | How does pool size affect library? | F1 vs pool size curve |
| H11 (tile size) | B | Does smaller tile size help? | Conditional (F1 < 0.85 trigger) |
| H12 (HP:HN ratio) | B | Does ratio affect performance? | Compare at fixed total |
| H13 (overlap/stride) | B | Does more overlap help? | 3-level comparison |
| H14 (cross-model) | C | Do effects generalize? | Deferred to Paper 2 |
| H15 (cross-model voting) | C | Does cross-model voting help? | Deferred to Paper 2 |
```

---

## Change 12: Update Budget Calculations

### Note
Uses **new hypothesis numbers** from Change 14.

### Location
Section 8.4.7 (Stranded Factorial Design totals)

### Update Strand 1 totals (already covered in Change 7)

### Update H5 Confirmatory totals (already covered in Change 3)

### Update total stranded design table:

```markdown
**Total stranded design:**

| Component | Cells | Calls | Cost |
|-----------|-------|-------|------|
| Strand 1 (M/E × partial H5 × T) | 26 | 15,600 | ~$23 |
| H5 Confirmatory (full 3-level) | 12 | 7,200 | ~$11 |
| Strand 2 (Library size, H8) | 24 | 14,400 | ~$22 |
| **Base total** | **62** | **37,200** | **~$56** |
| Strand 3 (conditional) | 8 | 4,800 | ~$7 |
| H5 Expansion (if triggered) | 6 | 3,600 | ~$5 |
| **Maximum total** | **76** | **45,600** | **~$68** |

**Note**: Strand 2 uses 4 temperatures (not 5) consistent with H7. 6 library conditions × 4 T = 24 cells.
```

---

## Change 13: Update Changelog

### Location
End of document, changelog section

### Add new entry at top:

```markdown
- v3.6: Major simplification and renumbering — Hypotheses renumbered H1-H15 in clean sequence (H1-H8 confirmatory, H9-H15 exploratory); old H1+H2 merged into new H1 (M/E level with contrasts); old H3+H10 merged into new H2 (two-stage pipelines); old H6+H11 merged into new H9 (diversity mechanisms); old H7 simplified to 3 levels as new H5; old H9 reduced to 4 temperatures as new H7; old H5 updated with directional prediction as new H4; old H15 becomes new H8; text-only conditions tested at T=1.0 only; new H13 added (overlap/stride); exploratory hypotheses reorganized into Tiers A/B/C; Section 12 added (Future Directions); confirmatory count now 8; budget reduced from ~$90 to ~$56 base
```

---

## Change 14: Renumber All Hypotheses

### Rationale
After merging and reorganizing, hypothesis numbers are no longer sequential (H1, H3, H4, H5, H7, H8, H9, H15 confirmatory; H6, H14, H16, H17, H18 exploratory). This is confusing for readers. Renumber to clean sequential order.

### Mapping Table

| Old # | New # | Status | Hypothesis |
|-------|-------|--------|------------|
| H1 (merged H2) | **H1** | Confirmatory | M/E level |
| H3 (merged H10) | **H2** | Confirmatory | Two-stage pipelines |
| H4 | **H3** | Confirmatory | Consensus voting |
| H5 | **H4** | Confirmatory | Example ordering |
| H7 | **H5** | Confirmatory | Hard negatives |
| H8 | **H6** | Confirmatory | Flash→Pro transfer |
| H9 | **H7** | Confirmatory | Temperature |
| H15 | **H8** | Confirmatory | Library size |
| H6 (merged H11) | **H9** | Exploratory (Tier A) | Diversity mechanisms |
| H14 | **H10** | Exploratory (Tier B) | Training pool size |
| H16 | **H11** | Exploratory (Tier B) | Tile size |
| H17 | **H12** | Exploratory (Tier B) | HP:HN ratio |
| H18 | **H13** | Exploratory (Tier B) | Overlap/stride |
| H12 | **H14** | Exploratory (Tier C) | Cross-model consistency (deferred) |
| H13 | **H15** | Exploratory (Tier C) | Cross-model voting (deferred) |

### Section 5 Structure (Confirmatory)

```markdown
## 5. Confirmatory Hypotheses

### H1: Modality and Elaboration Level Affects Detection Performance
[merged H1+H2 content]

### H2: Two-Stage Pipelines Do Not Improve Detection
[merged H3+H10 content]

### H3: Consensus Voting Improves F1
[old H4 content]

### H4: Example Ordering Affects Performance
[old H5 content, with directional prediction]

### H5: Hard Negative Examples Improve Precision
[old H7 content, 3 levels]

### H6: Optimizations Transfer from Gemini Flash to Pro
[old H8 content]

### H7: Temperature Affects Detection Performance
[old H9 content, 4 levels]

### H8: Few-Shot Library Size Affects Detection Performance
[old H15 content]
```

### Section 6 Structure (Exploratory)

```markdown
## 6. Exploratory Hypotheses

*These analyses will be conducted and reported but are not confirmatory. Results will be interpreted cautiously and framed as hypothesis-generating. Not included in FDR correction.*

### Tier A: Run in Stage 1 (Essential)

### H9: Diversity Mechanisms Improve Consensus Voting
[merged H6+H11 content]

---

### Tier B: Run If Budget Allows

### H10: Training Pool Size Effects on Library Quality
[old H14 content]

### H11: Tile Size Effects on Detection Performance
[old H16 content, updated for smaller tiles]

### H12: Hard Positive to Hard Negative Ratio
[old H17 content]

### H13: Tile Overlap Affects Detection Performance
[new H18 content]

---

### Tier C: Deferred to Future Work

### H14: Cross-Model Consistency
[old H12 content — brief note that this is deferred to Paper 2]

### H15: Cross-Model Consensus Voting
[old H13 content — brief note that this is deferred to Paper 2]
```

### Updated Summary Tables (Section 7)

#### 7.1 Confirmatory Hypotheses

```markdown
| Hypothesis | Prediction | Test Type | Advance to Stage 2 if... |
|------------|------------|-----------|--------------------------|
| H1 (M/E level) | Affects performance; verbose ≤ brief | ANOVA + contrasts | Significant differences found |
| H2 (two-stage) | Neither architecture helps | One-tailed | Either shows ≥0.05 improvement |
| H3 (consensus voting) | Improvement | One-tailed | Significant improvement |
| H4 (example ordering) | Canonical-last > canonical-first | One-tailed | Significant ordering effect |
| H5 (hard negatives) | Precision ↑, Recall stable | One-way ANOVA (3 levels) | Precision up, recall stable |
| H6 (Flash→Pro transfer) | Transfer works | OFAT sensitivity | Transfer confirmed |
| H7 (temperature) | T=1.0 optimal | One-way ANOVA (4 levels) | Any temperature outperforms 1.0 |
| H8 (library size) | Diminishing returns | One-way ANOVA | Optimal library size identified |
```

#### 7.2 Exploratory Hypotheses

```markdown
| Hypothesis | Tier | Question | Analysis |
|------------|------|----------|----------|
| H9 (diversity mechanisms) | A | Does variation improve voting? | 5-condition comparison |
| H10 (training pool size) | B | How does pool size affect library? | F1 vs pool size curve |
| H11 (tile size) | B | Does smaller tile size help? | Conditional (F1 < 0.85 trigger) |
| H12 (HP:HN ratio) | B | Does ratio affect performance? | Compare at fixed total |
| H13 (overlap/stride) | B | Does more overlap help? | 3-level comparison |
| H14 (cross-model) | C | Do effects generalize? | Deferred to Paper 2 |
| H15 (cross-model voting) | C | Does cross-model voting help? | Deferred to Paper 2 |
```

### Cross-Reference Updates Required

Search and replace all hypothesis references throughout the document:

| Context | Old Reference | New Reference |
|---------|---------------|---------------|
| H7 conditions mention | "H7=None" | "H5=None" |
| Library size references | "H15" | "H8" |
| Diversity references | "H6" | "H9" |
| Two-stage references | "H3" or "H10" | "H2" |
| Temperature references | "H9" | "H7" |
| Transfer references | "H8" | "H6" |
| Ordering references | "H5" | "H4" |
| Voting references | "H4" | "H3" |
| Tile size references | "H16" | "H11" |
| Ratio references | "H17" | "H12" |
| Overlap references | "H18" | "H13" |
| Cross-model references | "H12" | "H14" |
| Cross-model voting refs | "H13" | "H15" |

**Key sections requiring cross-reference updates:**
- Section 3.2 (FDR rationale — "7 confirmatory" → "8 confirmatory")
- Section 8.4.6 (Hypothesis Interaction Summary)
- Section 8.4.7 (Stranded Factorial Design)
- Section 8.7 (Hypothesis-to-Implementation Mapping)
- Section 9 (Implementation Priority)
- All "see Hx" references throughout

### Update Changelog Entry

Replace the v3.6 changelog entry with:

```markdown
- v3.6: Major simplification and renumbering — Hypotheses renumbered H1-H15 in clean sequence (H1-H8 confirmatory, H9-H15 exploratory); H1+H2 merged into new H1 (M/E level with contrasts); old H3+H10 merged into new H2 (two-stage pipelines); old H6+H11 merged into new H9 (diversity mechanisms); old H7 simplified to 3 levels as new H5; old H9 reduced to 4 temperatures as new H7; old H5 updated with directional prediction as new H4; text-only conditions tested at T=1.0 only; new H13 added (overlap/stride); exploratory hypotheses reorganized into Tiers A/B/C; Section 12 added (Future Directions); confirmatory count now 8; budget reduced from ~$90 to ~$56 base
```

---

## Verification Checklist

After making changes, verify:

### Hypothesis Structure
- [ ] H1 = M/E level (merged old H1+H2) with planned contrasts
- [ ] H2 = Two-stage pipelines (merged old H3+H10)
- [ ] H3 = Consensus voting (old H4)
- [ ] H4 = Example ordering (old H5) with directional prediction (canonical-last > canonical-first)
- [ ] H5 = Hard negatives (old H7) with 3 levels (None, Images-only, Text+Images)
- [ ] H6 = Flash→Pro transfer (old H8)
- [ ] H7 = Temperature (old H9) with 4 levels (0.0, 0.7, 1.0, 1.3)
- [ ] H8 = Library size (old H15)
- [ ] H9 = Diversity mechanisms (merged old H6+H11) — Tier A exploratory
- [ ] H10 = Training pool size (old H14) — Tier B exploratory
- [ ] H11 = Tile size (old H16) — Tier B exploratory
- [ ] H12 = HP:HN ratio (old H17) — Tier B exploratory
- [ ] H13 = Overlap/stride (new) — Tier B exploratory
- [ ] H14 = Cross-model consistency (old H12) — Tier C (deferred)
- [ ] H15 = Cross-model voting (old H13) — Tier C (deferred)

### Document Structure
- [ ] Section 5 contains H1-H8 (confirmatory)
- [ ] Section 6 contains H9-H15 (exploratory) organized into Tiers A, B, C
- [ ] Section 7 summary tables use new numbering
- [ ] Section 12 (Future Directions) added
- [ ] Subsequent sections renumbered (old 12→13, 13→14, etc.)

### Cross-References Updated
- [ ] All "H7=None" etc. references updated to "H5=None"
- [ ] Section 3.2 says "8 confirmatory hypotheses"
- [ ] Section 8.4.6 (Hypothesis Interaction Summary) uses new numbers
- [ ] Section 8.4.7 (Stranded Factorial Design) uses new numbers
- [ ] Section 8.7 (Hypothesis-to-Implementation Mapping) uses new numbers
- [ ] Section 9 (Implementation Priority) uses new numbers
- [ ] All "see Hx" cross-references updated

### Budget and Totals
- [ ] Strand 1 totals: 26 cells, 15,600 calls, ~$23
- [ ] H5 Confirmatory totals: 12 cells, 7,200 calls, ~$11 (formerly "H7 Confirmatory")
- [ ] Strand 2 totals: 24 cells, 14,400 calls, ~$22
- [ ] Total budget: ~$56 base, ~$68 maximum
- [ ] Changelog updated with v3.6 entry including renumbering note
