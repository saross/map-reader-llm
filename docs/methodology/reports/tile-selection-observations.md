# Tile Selection: Methodological Observations

> **STALE — predates the holdout expansion.** This document describes the
> pre-expansion 20-tile holdout (28 mounds); the lodged design is 60 holdout
> tiles with 79 mounds (`osf/preregistration.md:234`). Its "preregistered
> estimate (40-60 symbols)" has no source in any lodged document (D17 audit
> FALSE-22). Retained as a historical design note; do not cite against the
> registration. Banner added 2026-07-28.

*Reference notes on design choices and implications*

---

## Context

Four Soviet 1:50,000 topographic maps (Bulgaria) serve as the study corpus. These maps were randomly selected for Sobotkova et al. (2023) to evaluate student digitisation performance, representing a ~5% sample of a larger corpus (~80 maps, ~10,000 mounds total). The current study inherits these maps; they were not cherry-picked for VLM evaluation.

| Map | Mounds | % of sample corpus | Terrain characteristics |
|-----|--------|-------------------|------------------------|
| K-35-053-3_Elenovo | 217 | 38% | — |
| K-35-062-2_Rakovski | 196 | 34% | — |
| K-35-052-4_32635 | 136 | 24% | — |
| K-35-078-1_Lesovo | 20 | 3.5% | Rugged, dense contours |
| **Total** | **569** | **100%** | |

Symbol type distribution (corpus-wide):
- Burial mound: 455 (80%)
- Benchmark on burial mound: 65 (11%)
- Triangulation point on burial mound: 43 (8%)
- Settlement mound: 5 (1%)

---

## Sampling Design: Equal-Per-Map vs. Proportional

### Chosen approach: Equal tiles per map

- 5 training tiles per map (20 total)
- 5 holdout tiles per map (20 total)
- Stratified by within-map mound density (empty / sparse / dense)

### Implication: Overweighting sparse maps

| Map | Corpus mound share | Sampling weight | Relative over/underweight |
|-----|-------------------|-----------------|---------------------------|
| Elenovo | 38% | 25% | 0.66× (underweighted) |
| Rakovski | 34% | 25% | 0.74× (underweighted) |
| K-35-052-4 | 24% | 25% | 1.04× (approximately matched) |
| Lesovo | 3.5% | 25% | 7× (overweighted) |

### Rationale for this design

The design prioritises **generalization testing** over **corpus-representative performance**:

1. **Sparse maps are common**: The broader corpus includes many sparse maps like Lesovo. A method that only works on mound-dense sheets would have limited practical utility.

2. **Different terrain = different confounders**: Lesovo's rugged terrain with dense contour lines presents distinct false positive risks. Testing on visually diverse maps reveals brittleness.

3. **False positive rate matters on sparse maps**: Practical archaeological survey requires methods that don't hallucinate mounds where none exist. Equal sampling ensures adequate empty/sparse tiles for evaluating this.

4. **Empty tiles for calibration**: Including Lesovo helps ensure the few-shot library contains genuine "nothing here" examples, which empirically reduces hallucination rates.

### Alternative not chosen: Proportional sampling

Proportional sampling would concentrate ~72% of holdout tiles on Elenovo and Rakovski, maximising power for corpus-level F1 estimation but:
- Undersampling sparse maps (Lesovo might contribute 1 tile)
- Reducing ability to detect map-specific failure modes
- Potentially overfitting to dense-map characteristics

---

## Power Implications

### Holdout mound count

- 28 mounds in holdout set
- Toward lower end of the drafting-era working estimate (40-60 symbols; not in any lodged document)
- Detectable effect size: F1 ≈ 0.10-0.12 (vs. 0.08 with larger sample)

This is adequate for directional predictions but limits precision on effect size estimates.

### Symbol-type subgroup power

Expected holdout distribution (assuming proportional to corpus):
- Burial mounds: ~22
- Benchmark mounds: ~3
- Triangulation mounds: ~2
- Settlement mounds: ~0

**Limitation**: With only ~3 benchmark mounds in holdout, symbol-type-specific performance cannot be reliably assessed. Preliminary findings (benchmark problematic, triangulation perfect recall) cannot be confirmed at subgroup level.

**Acknowledgement for paper**: "Symbol-type-specific performance is reported descriptively but should be interpreted cautiously due to small subgroup sizes (n < 5 for non-burial-mound types)."

---

## Density Distribution Matching

The selection algorithm force-matched density distributions between training and holdout:

| Density category | Training | Holdout |
|-----------------|----------|---------|
| Empty (0 mounds) | 8 | 8 |
| Sparse (1-2 mounds) | 7 | 7 |
| Dense (3+ mounds) | 5 | 5 |

This is a **matched sample design**, not independent stratified random sampling. The purpose is ensuring equivalent difficulty profiles across sets.

**Methodological note for paper**: "Holdout tiles were selected to match the training set's density distribution, ensuring equivalent representation of empty, sparse, and dense tiles across both sets."

---

## Spatial Separation

Holdout tiles exclude tiles adjacent to training tiles (Manhattan distance ≤ 1 tile = 448 pixels). This prevents:
- Spatial autocorrelation leakage (nearby tiles may share mound clusters)
- Edge-overlap where a mound straddles tile boundaries

The constraint was not relaxed during selection (verified in metadata).

---

## Empty Tiles for Anti-Hallucination

Empty training tiles (0 mounds) serve a distinct function from hard negative examples:

| Example type | Purpose | Source |
|--------------|---------|--------|
| Empty tiles | Calibrate base rate expectations; establish that null output is valid | Training tiles (complete) |
| Hard negative crops | Teach discrimination between confusable symbols | Training tiles (cropped regions) |

**Empirical finding**: Early experiments without empty tiles showed elevated false positive rates. The model appeared to infer that every tile should contain detections. Including empty tiles calibrates expectations and reduces hallucination.

**Suggested text for paper**: "Empty training tiles (containing no mound symbols) were included in the few-shot library to establish that null outputs are valid. Preliminary experiments without such examples showed elevated false positive rates, suggesting VLMs may infer an implicit expectation that every image should contain target objects. Empty tiles calibrate base rate expectations; hard negative crops (visually confusable non-mound symbols) address discrimination separately."

---

## Reporting Recommendations

### Primary analysis

Report aggregate F1, precision, recall with bootstrapped 95% CIs on the full holdout set (28 mounds, 20 tiles).

### Secondary analyses

1. **Per-map performance**: Report F1 per map sheet. If performance varies substantially (e.g., F1=0.90 on Elenovo, F1=0.60 on Lesovo), this reveals generalization limits the aggregate would obscure.

2. **Symbol-type performance**: Report descriptively but caveat small subgroup sizes.

3. **Empty-tile false positive rate**: Report false positives specifically on empty holdout tiles (8 tiles, 0 mounds). This is a direct test of hallucination control.

---

## Summary: Design Trade-offs

| Design choice | Optimises for | Sacrifices |
|---------------|---------------|------------|
| Equal tiles per map | Generalization across diverse maps | Corpus-representative F1 estimation |
| Force-matched density distribution | Equivalent difficulty in train/holdout | Independence of sampling |
| Spatial separation | Prevents autocorrelation leakage | Slightly constrains eligible tiles |
| Including sparse Lesovo | Tests false positive rate on hard cases | Raw power (fewer mounds per tile) |

These are defensible choices for a methods-development study focused on generalization. A subsequent deployment study might use proportional sampling to estimate real-world performance on the full corpus.

---

## Draft Text for Paper

### Methods

"Tiles were selected using stratified random sampling with documented provenance. Each of the four maps contributed five training and five holdout tiles, ensuring equal representation across visually and geographically diverse sheets. Within each map, tiles were stratified by mound density (empty, sparse, dense) and sampled to match distributions across training and holdout sets. Holdout tiles were spatially separated from training tiles (minimum 448-pixel gap) to prevent autocorrelation leakage. This design prioritises generalization testing across varying mound densities and terrain types rather than corpus-proportional sampling. The four maps were originally selected randomly for Sobotkova et al. (2023) and were not chosen specifically for this study."

### Limitations

"The holdout set contains 28 mound symbols, providing adequate power for detecting directional effects (F1 differences ≥ 0.10) but limiting precision on effect size estimates. Symbol-type subgroups (benchmark, triangulation, settlement mounds) are too small for reliable subgroup analysis. Equal-per-map sampling overweights sparse sheets relative to their corpus prevalence; reported F1 reflects generalization performance rather than expected corpus-wide accuracy."

---

*Document created: 2024-12-23*
*For reference during analysis and write-up*
