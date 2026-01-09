# Preregistration: VLM-Based Burial Mound Detection

**Title**: Extracting geospatial datasets from historical maps using frontier vision-language models: Evaluating prompting strategies for cartographic symbol detection

**Authors**: Shawn Ross

**Affiliations**: Macquarie University, Sydney, Australia

**Document version**: 4.2
**Last updated**: 2026-01-07
**Status**: Ready for Registration

---

## 1. Study Overview

### 1.1 Background

This study evaluates prompting strategies for using frontier vision-language models (VLMs) to detect burial mound symbols from Soviet-era 1:50,000 topographic maps of Bulgaria. It builds on Sobotkova et al. (2023), which used participatory GIS for the same extraction task.

During preliminary development, we discovered that some "best practice" prompting strategies derived from the VLM literature did not seem to transfer to this task, while others did, for example:

1. **Text minimisation had little effect**: Contrary to text-image interference literature (Vo et al., 2025), removing text from prompts didn't improve performance.  
2. **Two-stage proposer-verifier was actively harmful**: This architecture degraded performance rather than improving precision-recall tradeoffs.  
3. **Consensus voting worked well**: n-of-x voting schemes substantially improved performance.

These findings suggest that prompting strategies derived from general VLM benchmarks may not generalise to specialised detection tasks like map symbol extraction using frontier models, a finding with implications for practitioners.

### 1.2 Research Questions

1. Does text + image prompting affect VLM detection performance on novel domain tasks, as opposed to image-only prompting?
2. Does the nature of text (concise, verbose, varied across consensus voting runs) affect detection performance?
3. Do two-stage proposer-verifier pipelines improve precision-recall tradeoffs for VLM detection?  
4. What voting and ensemble strategies optimise detection F1, precision, and recall?  
5. Does model temperature affect VLM performance?
6. Do these factors interact with one another to affect VLM performance?
7. Do effects generalise from low-cost models like Gemini 3 Flash to more capable models like Gemini 3 Pro, and across frontier VLM families (Gemini 3, Claude 4.5, GPT-5.2)?
8. What image library characteristics most improve performance (e.g., library size, inclusion of negatives, diversity of images, etc.)?

### 1.3 Two-Stage Trial Framework

This study adopts a **two-stage trial framework** using a 361-tile corpus including four manually annotated Soviet-era topographic map sheets from Bulgaria (Thracian Plain and surrounding areas). Annotation is comprehensive, with all mound symbols identified.

**Stage 1 (current work)**: Identify promising techniques using a modest training set (20 tiles) and an expanded holdout set (60 tiles). The expanded holdout provides adequate power to detect moderate effects (MDE ≈ 0.07–0.09 for F1). False Discovery Rate (FDR) correction is used to balance discovery against false positives.

**Stage 2 (future work)**: Techniques that show promise in Stage 1 will be validated on a larger holdout set (additional tiles from the 361-tile corpus or transfer testing on out-of-sample maps) with more stringent significance thresholds.

This framing acknowledges the power limitations of small-sample evaluation while maintaining rigor through preregistration and appropriate multiple comparison correction.

**Role of text-only conditions**:

Text-only conditions (Brief-text, Verbose-text) serve primarily as academic baselines to assess VLM capability without visual examples. The primary optimisation target is image-based discovery, as an optimal deployment will almost certainly include visual examples.

Text-only results inform:

- Whether text guidance alone has any value
- Whether modality matters: comparing image-only, text-only, and text+image performance
- Baseline comparison for text+image improvements

Identical text is used across modalities (text-only and text+image) to isolate the effect of adding visual examples. Verbose text additions (edge case guidance) are derived from image-only baseline failures (difficult examples for the image library are selected empirically from false positives and false negatives).

### 1.4 Timeline

**Anticipated data collection**: 30 December 2025 - 31 January 2026

---

## 2. Data Resources

### 2.1 Map Tile Corpus

| Dataset | Tiles | Purpose | Status |
| :---- | :---- | :---- | :---- |
| Development set ('training tiles') | 20 | Prompt engineering, iteration | Used — contaminated |
| Exploratory test set ('holdout tiles') | 60 | Generalisation checks (no feedback to prompts) | Used for evaluation only |
| Reserve set | 281 | Confirmatory testing | **Untouched** |

**Total**: 361 tiles from 4 annotated Soviet topographic map sheets. Maps were hand-annotated by students with comprehensive expert review.

**Note**: The 60 exploratory test tiles were used ONLY for generalisation assessment of prompts, with NO feedback into prompt development.

**Analysis scope**: Training tiles are excluded from all reported performance metrics. F1, precision, recall, and MCC are computed on holdout tiles only.

### 2.2 Selection Methodology

See Section 8.6 for full methodology. Key parameters:

| Parameter | Training | Holdout |
| :--- | :--- | :--- |
| Selection date | 2025-12-23 | 2026-01-03 |
| Random seed | 1766464625 | 1767425239 |
| Samples per map | 5 | 15 |

| Parameter | Value |
| :--- | :--- |
| Content threshold | ≤75% background |
| Spatial separation | Holdout tiles not adjacent to training tiles |
| Tile size | 512×512 pixels (64px overlap, 448px stride) |

*Tile size validated by calibration pilot (2026-01-07) comparing 256px, 512px, and 1024px. 512px retained as optimal precision-recall balance; see Section 12.2 for multi-scale analysis.*

### 2.3 Training Tiles (n=20)

Tiles used for prompt development and few-shot examples.

#### K-35-052-4\_32635 (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-052-4\_32635\_x1344\_y1344.png | 0 | empty |
| K-35-052-4\_32635\_x1344\_y2240.png | 2 | sparse |
| K-35-052-4\_32635\_x2240\_y2240.png | 1 | sparse |
| K-35-052-4\_32635\_x2240\_y3584.png | 3 | dense |
| K-35-052-4\_32635\_x3136\_y896.png | 0 | empty |

#### K-35-053-3\_Elenovo (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-053-3\_Elenovo\_x1792\_y2240.png | 4 | dense |
| K-35-053-3\_Elenovo\_x2240\_y2240.png | 11 | dense |
| K-35-053-3\_Elenovo\_x2240\_y3584.png | 1 | sparse |
| K-35-053-3\_Elenovo\_x3136\_y3136.png | 0 | empty |
| K-35-053-3\_Elenovo\_x896\_y1344.png | 2 | sparse |

#### K-35-062-2\_Rakovski (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-062-2\_Rakovski\_x0\_y1792.png | 2 | sparse |
| K-35-062-2\_Rakovski\_x0\_y3136.png | 0 | empty |
| K-35-062-2\_Rakovski\_x448\_y2688.png | 3 | dense |
| K-35-062-2\_Rakovski\_x896\_y2688.png | 1 | sparse |
| K-35-062-2\_Rakovski\_x896\_y3136.png | 4 | dense |

#### K-35-078-1\_Lesovo (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-078-1\_Lesovo\_x1344\_y0.png | 2 | sparse |
| K-35-078-1\_Lesovo\_x1344\_y896.png | 0 | empty |
| K-35-078-1\_Lesovo\_x3136\_y2688.png | 0 | empty |
| K-35-078-1\_Lesovo\_x3584\_y3136.png | 0 | empty |
| K-35-078-1\_Lesovo\_x896\_y3136.png | 0 | empty |

**Training set summary**: 20 tiles, 36 mounds total

---

### 2.4 Holdout Tiles (n=60)

Tiles reserved for final evaluation. Spatially separated from training tiles.

#### K-35-052-4\_32635 (15 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-052-4\_32635\_x0\_y0.png | 1 | sparse |
| K-35-052-4\_32635\_x0\_y1344.png | 1 | sparse |
| K-35-052-4\_32635\_x0\_y2240.png | 9 | dense |
| K-35-052-4\_32635\_x1344\_y3136.png | 0 | empty |
| K-35-052-4\_32635\_x2240\_y1344.png | 1 | sparse |
| K-35-052-4\_32635\_x2688\_y0.png | 0 | empty |
| K-35-052-4\_32635\_x3136\_y0.png | 0 | empty |
| K-35-052-4\_32635\_x3136\_y2240.png | 1 | sparse |
| K-35-052-4\_32635\_x3136\_y3584.png | 0 | empty |
| K-35-052-4\_32635\_x3584\_y3136.png | 2 | sparse |
| K-35-052-4\_32635\_x3584\_y3584.png | 3 | dense |
| K-35-052-4\_32635\_x448\_y1344.png | 1 | sparse |
| K-35-052-4\_32635\_x448\_y3136.png | 0 | empty |
| K-35-052-4\_32635\_x448\_y896.png | 0 | empty |
| K-35-052-4\_32635\_x896\_y3136.png | 0 | empty |

#### K-35-053-3\_Elenovo (15 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-053-3\_Elenovo\_x0\_y0.png | 0 | empty |
| K-35-053-3\_Elenovo\_x0\_y1344.png | 0 | empty |
| K-35-053-3\_Elenovo\_x0\_y2688.png | 0 | empty |
| K-35-053-3\_Elenovo\_x0\_y3136.png | 0 | empty |
| K-35-053-3\_Elenovo\_x1792\_y448.png | 2 | sparse |
| K-35-053-3\_Elenovo\_x2240\_y448.png | 1 | sparse |
| K-35-053-3\_Elenovo\_x2688\_y1344.png | 0 | empty |
| K-35-053-3\_Elenovo\_x3136\_y1344.png | 0 | empty |
| K-35-053-3\_Elenovo\_x3584\_y2240.png | 3 | dense |
| K-35-053-3\_Elenovo\_x448\_y0.png | 1 | sparse |
| K-35-053-3\_Elenovo\_x448\_y2688.png | 8 | dense |
| K-35-053-3\_Elenovo\_x448\_y3136.png | 3 | dense |
| K-35-053-3\_Elenovo\_x448\_y448.png | 4 | dense |
| K-35-053-3\_Elenovo\_x896\_y2240.png | 3 | dense |
| K-35-053-3\_Elenovo\_x896\_y448.png | 1 | sparse |

#### K-35-062-2\_Rakovski (15 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-062-2\_Rakovski\_x1792\_y0.png | 5 | dense |
| K-35-062-2\_Rakovski\_x1792\_y3584.png | 0 | empty |
| K-35-062-2\_Rakovski\_x2240\_y2240.png | 5 | dense |
| K-35-062-2\_Rakovski\_x2240\_y448.png | 1 | sparse |
| K-35-062-2\_Rakovski\_x2688\_y1344.png | 4 | dense |
| K-35-062-2\_Rakovski\_x2688\_y2240.png | 1 | sparse |
| K-35-062-2\_Rakovski\_x2688\_y2688.png | 0 | empty |
| K-35-062-2\_Rakovski\_x3136\_y1344.png | 2 | sparse |
| K-35-062-2\_Rakovski\_x3136\_y1792.png | 2 | sparse |
| K-35-062-2\_Rakovski\_x3136\_y2240.png | 0 | empty |
| K-35-062-2\_Rakovski\_x3136\_y3136.png | 3 | dense |
| K-35-062-2\_Rakovski\_x3136\_y896.png | 2 | sparse |
| K-35-062-2\_Rakovski\_x3584\_y1344.png | 0 | empty |
| K-35-062-2\_Rakovski\_x3584\_y448.png | 2 | sparse |
| K-35-062-2\_Rakovski\_x448\_y896.png | 4 | dense |

#### K-35-078-1\_Lesovo (15 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-078-1\_Lesovo\_x0\_y2688.png | 0 | empty |
| K-35-078-1\_Lesovo\_x0\_y3136.png | 2 | sparse |
| K-35-078-1\_Lesovo\_x1344\_y2240.png | 0 | empty |
| K-35-078-1\_Lesovo\_x2240\_y1344.png | 0 | empty |
| K-35-078-1\_Lesovo\_x2240\_y3136.png | 0 | empty |
| K-35-078-1\_Lesovo\_x2688\_y1792.png | 0 | empty |
| K-35-078-1\_Lesovo\_x2688\_y896.png | 0 | empty |
| K-35-078-1\_Lesovo\_x3136\_y1344.png | 0 | empty |
| K-35-078-1\_Lesovo\_x3136\_y1792.png | 1 | sparse |
| K-35-078-1\_Lesovo\_x3136\_y448.png | 0 | empty |
| K-35-078-1\_Lesovo\_x3584\_y0.png | 0 | empty |
| K-35-078-1\_Lesovo\_x3584\_y1344.png | 0 | empty |
| K-35-078-1\_Lesovo\_x3584\_y448.png | 0 | empty |
| K-35-078-1\_Lesovo\_x448\_y1792.png | 0 | empty |
| K-35-078-1\_Lesovo\_x896\_y1792.png | 0 | empty |

**Holdout set summary**: 60 tiles, 79 mounds total

---

### 2.5 Density Distribution

Tiles were stratified by mound density (see Section 8.6 for category definitions):

| Density | Training | Holdout |
| :---- | :---- | :---- |
| Empty (0 mounds) | 8 | 30 |
| Sparse (1-2 mounds) | 7 | 18 |
| Dense (3+ mounds) | 5 | 12 |

**Terrain and mound density representation**: Lesovo represents mountainous terrain with low mound density, consistent with similar regions in mountainous areas. Its inclusion ensures the pipeline is evaluated on terrain representative of sparse-mound contexts, testing both detection in low-density environments and false positive rates in areas where mounds are sparse and geographic sybology (e.g., contour lines) are dense. The expanded holdout set includes 15 tiles from each map, with Lesovo contributing primarily empty tiles (13 of 15) which serve as a rigorous test of false positive rates in challenging terrain.

### 2.6 Map Annotation

Soviet-era maps were initially annotated by students using the FAIMS v2.6 mobile data capture application (customised as a participatory GIS). Annotation consisted of identifying all symbols representing:

- Burial mounds
- Burial mounds with benchmarks
- Burial mounds with triangulation points
- Benchmarks (no burial mound)
- Triangulation points (no burial mound)

The four maps used in the present study were later selected for the quality assessment of student work. To that end, the author (Shawn Ross) manually reviewed these tiles to ensure complete extraction and accuracy, with results then compared to the student work (which also served as a check against missed symbols). For a thorough presentation and discussion of the background, participatory GIS approach used to build the mound dataset, and quality assurance measures, please see Sobotkova et al., 2023.

---

## 3. Statistical Analysis Plan

### 3.1 Significance Testing

- **Per-hypothesis α**: 0.05
- **Direction**: One-tailed for directional predictions; two-tailed for equivalence tests (H1)
- **Multiple comparison correction**: Benjamini-Hochberg FDR at q = 0.05 across confirmatory hypotheses

### 3.2 Rationale for FDR

With 8 confirmatory hypotheses tested on 60 tiles (79 mound symbols), statistical power is adequate for detecting moderate effects. Bonferroni correction (α = 0.006) would remain conservative for a screening study. FDR controls the expected proportion of false discoveries among rejected hypotheses, which is appropriate when:

- The goal is identifying promising techniques for further validation
- Some false positives are acceptable if balanced by discovery of true effects
- The screening study prioritises sensitivity to real effects over strict Type I error control

### 3.3 Interpretation Guidelines

- **Statistically significant (FDR-corrected p < 0.05)**: Technique shows promise; advance to Stage 2 validation
- **Nominally significant (uncorrected p < 0.05, FDR-corrected p ≥ 0.05)**: Suggestive evidence; consider for Stage 2 with lower priority
- **Non-significant (uncorrected p ≥ 0.05)**: No statistical evidence of benefit. However, techniques showing consistent directional improvement (e.g., positive point estimate in ≥75% of conditions where tested) may be flagged for Stage 2 investigation with lowest priority if theoretically motivated. This fallback guards against discarding genuinely useful techniques due to sampling noise.

### 3.4 Practical Significance Caveat

Results will be interpreted in light of practical significance. A statistically significant but trivially small improvement (e.g., F1 +0.01) will be reported but not treated as actionable. Techniques advanced to Stage 2 should show both statistical significance and a meaningful effect.

### 3.5 Reporting

- All preregistered analyses reported **regardless of outcome**
- Report **effect sizes** (F1 difference, precision difference, recall difference) with 95% bootstrapped CIs
- **Spatial tolerance sensitivity**: All primary results reported at 20m; robustness checks at 10m, 30m, and 50m included in supplementary materials
- Report both uncorrected and FDR-corrected p-values
- Exploratory analyses clearly labelled and interpreted cautiously

### 3.6 Power Considerations

With 60 holdout tiles containing 79 mound symbols, statistical power is adequate for detecting moderate effects. Approximate detectable effect sizes (80% power, α = 0.05, two-tailed):

- **Symbol-level F1**: Minimum detectable difference ≈ 0.07-0.09
- **Tile-level MCC**: Minimum detectable difference ≈ 0.20

These estimates are approximate and assume moderate correlation between tiles. The two-stage trial framework treats Stage 1 as a screening study; techniques showing promise will be validated with additional samples in Stage 2.

**Implication**: Effects of F1 ≈ 0.08 or larger should be detectable with reasonable power. Smaller effects (e.g., F1 +0.05) may still fall below the detection threshold and will be flagged for Stage 2 investigation if directionally consistent.

### 3.7 Blinding

All API calls and metric computations are automated via scripts committed before holdout evaluation. The analysis pipeline runs without manual intervention between data collection and statistical output, eliminating opportunities for analyst degrees of freedom during evaluation.

### 3.8 Evaluation Protocol

**Independent runs**: Each condition in the main factorial is evaluated using K=10 independent single-pass runs. Results are characterised statistically (mean F1, SD, 95% CI).

**Rationale**: Independent runs provide unbiased estimates of each factor's effect without assuming voting (which is itself under test in H4). This design:

- Avoids circular application of voting when testing other hypotheses
- Enables proper variance-based statistical comparisons
- Allows post-hoc computation of voted results for comparison

**Post-hoc voting analysis**: Voting performance is computed from the same runs:

- N=5 voting: runs 1-5 as one pool, runs 6-10 as another (two independent estimates)
- N=10 voting: all runs as single pool
- Multiple thresholds computed for each N

**H4 integration**: The K=10 protocol directly supports H4 analysis. Additional N=30 runs are conducted at the optimal configuration to extend the voting characterisation.

---

## 4. Outcome Measures

### 4.1 Primary Outcome: Symbol-level F1

Detection performance is evaluated at the symbol level using precision, recall, and F1 score.

#### 4.1.1 Spatial Tolerance

**Primary matching threshold**: 20 metres. A detection is considered a true positive if it falls within 20m of a ground truth reference point.

**Spatial tolerance curve**: The evaluation also generates a spatial tolerance curve showing how precision, recall, and F1 vary across different buffer distances:

| Buffer (m) | Purpose |
| :---- | :---- |
| 10 | Strict localisation |
| 20 | Default threshold |
| 30 | Moderate tolerance |
| 50 | Lenient tolerance |

The 20m default was chosen as a reasonable balance \- it accounts for:

- Georeferencing imprecision in historical maps
- Symbol centroid ambiguity (mound symbols can be 10-20m across at 1:50,000 scale)
- Variation in map digitisation precision

#### 4.1.2 Detection Matching Algorithm

Detection matching uses **one-to-one matching** via the Hungarian algorithm:

1. Compute pairwise distances between all detection centroids and reference centroids
2. Build a cost matrix where distances exceeding the spatial tolerance (20m) are set to infinity
3. Apply the Hungarian algorithm (scipy.optimize.linear_sum_assignment) to find the optimal assignment minimising total distance
4. Filter assignments to retain only those within the spatial tolerance threshold
5. **True Positive**: Each matched detection-reference pair (counted once per pair)
6. **False Negative**: Each unmatched reference (no detection assigned)
7. **False Positive**: Each unmatched detection (not assigned to any reference)

This approach ensures:

- **Strict one-to-one matching**: Each detection matches at most one reference, and vice versa
- **Accurate mound counting**: A detection spanning two nearby mounds counts as 1 TP + 1 FN (important for answering "how many mounds are here?")
- **Optimal assignment**: The Hungarian algorithm guarantees the globally optimal matching that minimises total distance
- **No double-counting**: A single reference cannot contribute multiple TPs, and a single detection cannot satisfy multiple references

**Note on True Negatives**: At the symbol level, True Negatives are undefined: one cannot count all locations on a map where mounds do not exist. Therefore, metrics requiring True Negatives (accuracy, specificity, MCC) are not applicable at symbol-level, but will be evaluated at tile-level.

### 4.2 Secondary Outcome: Tile-level Discrimination (MCC)

In addition to symbol-level F1, we report tile-level Matthews Correlation Coefficient (MCC) for the binary classification of empty vs. populated tiles. At the tile level, True Negatives are well-defined:

| Tile state | Model output | Classification |
| :---- | :---- | :---- |
| Has mounds | Detected ≥1 mound | True Positive |
| Empty | Detected nothing | True Negative |
| Empty | Detected ≥1 mound | False Positive (hallucination) |
| Has mounds | Detected nothing | False Negative |

MCC is preferred over accuracy given balanced class distribution in the holdout set (30 empty tiles, 30 non-empty tiles). MCC ranges from -1 (perfect inverse classification) through 0 (random) to +1 (perfect classification), and appropriately penalises both false positives and false negatives.

**Rationale**: A method that simply predicts "mounds present" for every tile would achieve 50% accuracy but MCC ≈ 0. Tile-level MCC directly addresses the practical question: "Can this method correctly identify when there is nothing to find?"

We also report tile-level sensitivity (P(detect ≥1 | tile has mounds)) and specificity (P(detect 0 | tile is empty)) for interpretability.

---

## 5. Confirmatory Hypotheses

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

**Orthogonality with H5**: H1 controls detail level for **positives** (canonical symbols + hard positive edge cases). H5 controls presence of **negative** guidance (exclusion text + hard negative images). These are independent dimensions.

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

**Text-only note**: Text-only conditions serve primarily as academic baselines to characterise VLM capability without visual examples. The operationally-relevant comparisons are among image-using conditions.

**Advance to Stage 2 if**: Significant differences detected between levels, suggesting modality/elaboration choices matter for this domain.

*Note: The original H2 (text elaboration) has been merged into H1 and is now addressed via planned contrasts within this hypothesis.*

---

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
3. Stage 2: For each uncertain candidate, extract larger tile (~1024×1024) centred on candidate, re-query with verification prompt

*Pilot note: Calibration testing found 1024px tiles achieve only 37% recall at 2/5 threshold, limiting confirmation value. The fine-to-coarse test remains valid for confirming the prediction that two-stage will not help, but practitioners should note this constraint.*

**Analysis**:

- One-tailed tests: H0: two-stage ≥ single-stage; H1: two-stage < single-stage
- Prediction is that H0 will not be rejected for either architecture

**Stopping rule**: Two-stage architectures will only be pursued further if either demonstrates F1 at least 0.05 higher than single-stage. Given the inherent cost (~2× API calls) and complexity overhead, parity or marginal improvement would not justify adoption.

**Advance to Stage 2 if**: Either two-stage approach shows F1 improvement of at least 0.05 over single-stage (would contradict preliminary findings).

*Note: The original H10 (fine-to-coarse validation) has been merged into H2. Both two-stage directions are now tested together.*

---

### H3: Consensus Voting Improves F1

**Background**: Consensus voting addresses stochastic variation in VLM outputs. Preliminary testing confirmed substantial improvements with various voting configurations.

**Prediction**: Consensus voting will improve F1 compared to single-pass detection.

**Test**:

**Primary data source**: The K=10 independent runs from the main factorial enable voting analysis at multiple pool sizes and thresholds:

| Pool Size | Source | Thresholds |
|-----------|--------|------------|
| N=5 | Runs 1-5 or 6-10 | 1, 2, 3, 4, 5 |
| N=10 | All runs | 1, 2, ..., 10 |

**Extended voting (N=30)**: Additional 20 runs at optimal configuration to enable:

- N=30 threshold sweep (1, 2, ..., 30)
- Cost-benefit characterisation of deeper voting

**Analysis**:

- Compare single-pass mean F1 vs voted F1 at each (N, threshold) combination
- Generate threshold sweep curves (F1, precision, recall vs threshold for each N)
- Identify optimal (N, threshold) balancing performance and cost
- One-tailed test for primary comparison: H0: voting ≤ single-pass; H1: voting > single-pass

**Cost-efficiency analysis**:

- F1 improvement per additional pass
- Identify diminishing returns point
- Report optimal configuration for budget-constrained deployment

**Advance to Stage 2 if**: Significant improvement confirmed. Optimise voting parameters in Stage 2.

---

### H4: Example Ordering Affects Performance (Canonical Placement)

**Background**: VLMs exhibit documented recency bias where attention heads prioritise the final demonstration example. However, prototype theory suggests establishing canonical forms before presenting edge cases may improve schema formation.

**Prediction**: Canonical-last ordering will produce higher F1 than canonical-first ordering.

**Rationale**: Recency bias in VLM attention means final examples have outsized influence on schema formation. Placing clean prototypes (canonical examples) in the final positions should anchor the model's representation more effectively than placing them first.

**Directional hypothesis**: H0: canonical-last ≤ canonical-first; H1: canonical-last > canonical-first

**Test**: Compare detection performance across three ordering conditions:

- Condition A: Canonical-first — Legend entries in initial positions, followed by hard examples
- Condition B: Canonical-last — Hard examples in initial positions, legend entries in final positions
- Condition C: Random ordering (average of 3 random permutations with documented seeds)

**Partial factorial cross**: Ordering is tested at 3 M/E levels to assess M/E × O interaction:

- Image-only (minimal text may increase ordering sensitivity)
- Brief-text+image (probable operational mode)
- Verbose-text+image (extensive text may reduce ordering sensitivity)

**Design**: 3 orderings × 3 M/E levels = 9 total conditions. Since the main factorial uses canonical-first ordering throughout, this adds 6 new conditions (canonical-last and random orderings at each of 3 M/E levels) beyond what the factorial already tests. All H4 conditions tested at optimal H5 and T from main factorial.

**Note**: Canonical-first ordering is used throughout the main factorial. This design adds canonical-last and random orderings at the 3 selected M/E levels.

**Mitigation trigger**: If H4 shows significant O × M/E interaction (p < 0.10), extend ordering tests to remaining 2 M/E levels (Brief-text, Verbose-text) to complete the factorial.

**Analysis**:

- Primary: 3 × 3 ANOVA (Ordering × M/E subset)
- Planned contrast: canonical-last vs canonical-first (one-tailed)
- Test for O × M/E interaction
- If no interaction: report main effect of ordering pooled across M/E levels
- Random ordering provides baseline for comparison

**Implementation**: Canonical examples are legend-derived symbols (burial mound, settlement mound, triangulation on mound, benchmark on mound). Hard examples are selected via the procedure in Section 8.4.2. Within each block (canonical or hard), internal ordering is randomised with documented seed.

**Advance to Stage 2 if**: Significant ordering effect or O × M/E interaction detected.

---

### H5: Hard Negative Examples Improve Precision

**Background**: Hard negative mining is established in few-shot learning. Two channels could improve precision: (1) explicit text instructions describing what to exclude; (2) visual counter-examples showing confusable symbols. These may operate independently or synergistically.

**Prediction**: Including hard negative information (text and/or images) will improve precision without significantly harming recall.

**H5 Testing Structure**:

H5 uses a staged testing approach to balance detection of M/E × H5 interactions with budget efficiency:

1. **Strand 1 (partial cross)**: H5=None vs H5=Text+Images tested across all image-based M/E levels to detect overall H5 effect and M/E × H5 interaction
2. **H5 Confirmatory (full 3 levels)**: All 3 H5 levels tested at optimal M/E to decompose the mechanism

*Note: The original 4-level design (None, Text-only, Images-only, Text+Images) has been simplified to 3 levels. The "Text-only" condition (exclusion text without hard negative images) was removed as practically implausible — if hard negative examples are important enough to explain in text, they warrant visual demonstration.*

**Test**: 3-level design comparing:

| Condition | Exclusion Text | Hard Neg Images | Description |
| --------- | -------------- | --------------- | ----------- |
| A (None) | No | No | Baseline: positive examples only, no exclusion guidance |
| B (Images-only) | No | Yes | Hard negative images with minimal labels ("Negative") |
| C (Text+Images) | Yes | Yes | Hard negative images with explicit explanatory labels |

**Strand 1 partial cross**:

| M/E Level | H5=None | H5=Text+Images |
| --------- | ------- | -------------- |
| Image-only | ✓ | ✓ |
| Brief+image | ✓ | ✓ |
| Verbose+image | ✓ | ✓ |

**Note**: Text-only modalities are tested at H5=None only, since they have no example images and the Text-only H5 condition has been removed.

**H5 Confirmatory design**:

After Strand 1 identifies optimal M/E level, test all 3 H5 levels at that M/E:

| H5 Level | Exclusion Text | HN Images | Image Labels |
| -------- | -------------- | --------- | ------------ |
| None | No | No | — |
| Images-only | No | Yes | Minimal ("Negative") |
| Text+Images | Yes | Yes | Detailed (with explanation) |

**Library composition by H5 level**:

| H5 Level | Canon+ | Canon- | HP | Emp-HN | Nulls | Total |
| -------- | ------ | ------ | -- | ------ | ----- | ----- |
| None | 4 | 2 | 4 | 0 | 3 | 13 |
| Images-only | 4 | 2 | 4 | 3 | 3 | 16 |
| Text+Images | 4 | 2 | 4 | 3 | 3 | 16 |

**Note**: Canon- (legend-derived negatives) are always included in H5 to provide baseline visual context for distinguishing "marker on mound" from "standalone marker". Only H8 Pure tests without Canon-.

**Hard negative sources**:

1. **Canon-** (legend-derived negatives): Standalone triangulation point, standalone benchmark — always included in H5 to provide baseline context
2. **Emp-HN** (empirically-derived hard negatives): False positives with ≥3/5 occurrence during image-only baseline on training tiles — presence/modality controlled by H5 factor

**Note**: H5 tests Emp-HN presence and labelling (images-only vs text+images vs none). Canon- is always present as baseline visual vocabulary. Only H8 Pure tests without Canon-.

**What H5 tests**:

- Do hard negatives help when shown visually with minimal labels (B)?
- Does adding explanatory text improve further (C vs B)?
- Does the H5 effect vary by verbosity level (M/E × H5 interaction)?

**Analysis**:

- Primary: One-way ANOVA across 3 H5 levels on precision
- Planned contrasts: None vs Images-only; Images-only vs Text+Images
- Secondary: Parallel analysis on recall to confirm no significant harm
- Tertiary: Analysis on F1 to assess net benefit
- Strand 1: Test for M/E × H5 interaction

**Advance to Stage 2 if**: Significant H5 effect on precision AND recall does not significantly decrease.

---

### H6: Optimisations Transfer from Gemini 3 Flash to Pro

**Background**: Development and optimisation is conducted on Gemini 3 Flash for cost efficiency. For this approach to be valid, effects observed on Flash should replicate on Pro without requiring complete re-optimisation.

**Prediction**: The Flash-optimal configuration will perform well on Pro, with at most minor factor adjustments needed.

**Transfer testing approach**: Stepwise adjustment from Flash-optimal using one-factor-at-a-time (OFAT) sensitivity testing, rather than independent full optimisation.

#### Phase 1: Baseline Comparison

Run Flash-optimal configuration on Pro:
- K=10 runs on 20 stratified holdout tiles (subset of 60, preserving density distribution)
- Compare Pro vs Flash performance at matched configuration
- Establish baseline for factor sensitivity testing

#### Phase 2: OFAT Factor Sensitivity

For each core factor, test 1-2 alternatives while holding others at Flash-optimal:

| Factor | Tests | Purpose |
| ------ | ----- | ------- |
| M/E | 2 adjacent levels | Does Pro prefer more/less text? |
| H5 | 2 alternatives | Does Pro need different hard negative approach? |
| T | 2 adjacent temperatures | Does Pro prefer different temperature? |
| O | 2 alternative orderings | Does ordering effect transfer? |

**Decision rule**: If alternative outperforms Flash-optimal by ≥0.03 F1, flag factor for adjustment.

#### Phase 3: Voting Analysis

Compute voting curves from Phase 1-2 runs (no additional API calls):
- Compare Pro optimal threshold to Flash optimal threshold
- Note any differences >10% relative

#### Phase 4: Refinement (Conditional)

If Phase 2 identifies factors needing adjustment:
- Test one additional level in the indicated direction
- For voting: if threshold differs >20%, run N=30 at Pro-adjusted config

**Scope limitation**: Full per-model optimisation only if Pro demonstrates substantially superior cost-effectiveness (≥20% higher F1 at comparable cost, OR comparable F1 at ≤50% cost).

#### Success Criteria

| Outcome | Interpretation |
|---------|----------------|
| All factors within 0.03 of Flash-optimal | Full transfer; report unified recommendation |
| 1-2 factors need adjustment | Partial transfer; report Flash-optimal with Pro adjustments |
| ≥3 factors need adjustment | Poor transfer; consider Pro-specific optimisation (out of scope) |

**Advance to Stage 2 if**: Transfer confirmed (full or partial). Pro-specific adjustments, if any, documented for deployment guidance.

---

### H7: Temperature Affects Detection Performance

**Background**: Gemini documentation recommends T=1.0 for reasoning tasks. Preliminary testing found T<1.0 degraded performance. Higher temperatures may increase output diversity, potentially benefiting voting ensembles.

**Prediction**: T=1.0 (vendor recommended) will yield optimal or near-optimal performance. Lower temperatures will degrade performance; higher temperatures may increase variance without improving mean F1.

*Note: The original 5-level design has been reduced to 4 levels. T=0.3 was removed as preliminary testing showed no meaningful difference between T=0.0 and T=0.3, and the sparse region below T=0.7 is less theoretically interesting than the region around and above the vendor default.*

**Test**: Compare detection performance across 4 temperature levels:

| Level | Temperature | Rationale |
| ----- | ----------- | --------- |
| 1 | 0.0 | Minimum (deterministic) |
| 2 | 0.7 | Moderate variance |
| 3 | 1.0 | Vendor default |
| 4 | 1.3 | Above default (conservative extension) |

**Analysis**:

- One-way ANOVA across 4 temperature levels
- Planned contrasts: T=1.0 vs each other level
- Examine temperature × voting interaction via post-hoc analysis

**Temperature escalation trigger**: If T=1.3 yields higher F1 than T=1.0 (point estimate, same M/E and H5 condition), exploratory testing at T=1.6 and T=2.0 will be conducted at the optimal configuration to characterise the upper bound of the temperature-performance curve.

**Advance to Stage 2 if**: Any temperature significantly outperforms T=1.0, or if escalation trigger activates and higher temperatures show continued improvement.

---

### H8: Few-Shot Library Size Affects Detection Performance

**Status**: Confirmatory (Strand 2)

**Background**: Few-shot library size affects both the information available to the model and the token cost of each query. Preliminary exploration suggested performance improves with additional examples, but the optimal size and diminishing returns curve are unknown.

**Terminology**:

| Term | Definition |
|------|------------|
| Canon+ | Legend-derived positive examples (burial mound, settlement mound, trig point on mound, bench mark on mound) — always present |
| Canon- | Legend-derived negative examples (standalone triangulation point, standalone bench mark) — distinguishes "marker on mound" from "marker alone" |
| HP | Empirically-derived hard positives (false negatives from Phase 1 image-only baseline) |
| Emp-HN | Empirically-derived hard negatives (false positives from Phase 1 image-only baseline) |
| Hard Examples | HP + Emp-HN combined |

**Predictions**:

1. F1 will increase from Pure (7 examples) to Canonical (9 examples) — legend-derived negatives help distinguish similar symbols
2. F1 will increase from Canonical to Library A (9 → 13) — empirical hard examples help
3. F1 will increase from A to B (13 → 17), with moderate marginal gain
4. F1 will increase from B to C (17 → 25), with smaller marginal gain
5. F1 increase from C to D (25 → 41) will show minimal or no improvement (diminishing returns plateau)

**Test**: Compare detection performance across 6 library conditions:

| Condition | Canon+ | Canon- | HP | Emp-HN | Nulls | Total | Hard Examples |
|-----------|--------|--------|-----|--------|-------|-------|---------------|
| Pure      | 4      | 0      | 0   | 0      | 3     | 7     | 0             |
| Canonical | 4      | 2      | 0   | 0      | 3     | 9     | 0             |
| A         | 4      | 2      | 2   | 2      | 3     | 13    | 4             |
| B         | 4      | 2      | 4   | 4      | 3     | 17    | 8             |
| C         | 4      | 2      | 8   | 8      | 3     | 25    | 16            |
| D         | 4      | 2      | 16  | 16     | 3     | 41    | 32            |

**Baselines**:

- **Pure**: Positive examples only — tests whether VLM can detect mounds with no negative guidance at all
- **Canonical**: Adds legend-derived negatives — tests whether distinguishing similar symbols helps

**H5 constraint**: Pure and Canonical conditions run at H5=None by necessity (no empirical HNs to include). Conditions A-D run at optimal H5 from Strand 1.

**Ratio**: Conditions A-D use 1:1 HP:Emp-HN ratio. This avoids majority label bias and is the most defensible default given limited guidance in the literature. Ratio exploration is addressed in H12 (exploratory).

**Progression**: Enables three key contrasts:

- Pure → Canonical: Do legend-derived negatives help?
- Canonical → A: Do empirical hard examples help?
- A → B → C → D: Diminishing returns curve (0 → 4 → 8 → 16 → 32 hard examples)

**Fixed parameters**: Optimal verbosity (from Strand 1), optimal H5 from Strand 1, optimal temperature.

**Confound note**: Pure and Canonical conditions run at H5=None by design constraint (no empirical HNs available to include). Conditions A-D run at optimal H5 from Strand 1. The Canonical → A contrast therefore tests the combined effect of (1) adding empirical hard examples and (2) applying optimal H5 setting.

Interpretation depends on Strand 1 results:

- If Strand 1 finds H5=None is optimal → confound is moot; A-D also run at H5=None
- If Strand 1 finds H5≠None is optimal → interpret Canonical → A as a bundled treatment

**Adjustment option**: If the confound complicates interpretation, Strand 1 data can be used to estimate and adjust for the H5 effect. Specifically:

1. From Strand 1, estimate the H5 effect size (F1 difference between H5=None and H5=Optimal) at a comparable library composition
2. Subtract this estimated H5 effect from the observed Canonical → A difference
3. The residual approximates the "pure" effect of adding empirical hard examples

This adjustment is imperfect (library compositions differ slightly), but provides inferential leverage if needed. Document any such adjustment as post-hoc sensitivity analysis.

**Analysis**:

- Primary: One-way ANOVA across 6 library conditions
- Planned contrasts:
  - Pure vs Canonical (legend negatives help?)
  - Canonical vs A (empirical hard examples help?)
  - A vs B, B vs C, C vs D (diminishing returns)
- Secondary: Characterise diminishing returns curve (F1 vs total example count)
- Tertiary: Cost-efficiency analysis (F1 per input token)

**Advance to Stage 2 if**:

- Significant main effect of library size (FDR-corrected p < 0.05), OR
- Significant deviation from expected diminishing returns pattern (e.g., D substantially outperforms C)

---

## 6. Exploratory Hypotheses

*These analyses will be conducted and reported but are not confirmatory. Results will be interpreted cautiously and framed as hypothesis-generating. Not included in FDR correction.*

*Note: The original H10 (fine-to-coarse validation) has been merged into confirmatory H2. The original H6 (prompt diversity) and H11 (temperature diversity) have been merged into exploratory H9.*

### Tier A: Essential Exploratory

*Tests that address fundamental questions about ensemble diversity mechanisms.*

### H9: Diversity Mechanisms Improve Consensus Voting

**Status**: Exploratory (Tier A)

**Background**: Voting with identical prompts, examples, and temperature across passes may produce correlated errors. Three mechanisms could improve ensemble diversity:

1. **Text diversity**: Semantically equivalent but differently phrased prompts
2. **Image diversity**: Varying hard examples across passes
3. **Temperature diversity**: Varying temperature across passes

These mechanisms may operate independently, redundantly, or synergistically.

**Prediction**: At least one diversity mechanism will improve F1 compared to fully identical passes.

**Test**: 5-condition design comparing diversity mechanisms:

| Condition | Text | Images | Temperature | Description |
| --------- | ---- | ------ | ----------- | ----------- |
| A | Fixed | Fixed | Fixed | Baseline: identical across all passes |
| B | Varied | Fixed | Fixed | Text diversity only |
| C | Fixed | Varied | Fixed | Image diversity only |
| D | Fixed | Fixed | Varied | Temperature diversity only |
| E | Varied | Varied | Varied | Full diversity |

**Text diversity implementation**: Content diversity with fixed structure. All variants maintain identical prompt structure while varying task framing, instruction phrasing, and guideline wording. Examples:

1. "Identify burial mound symbols in this map section"
2. "Detect tumuli markers on this topographic map"
3. "Find kurgan indicators in this image"
4. "Locate ancient burial mound cartographic symbols"
5. "Mark all mound features shown on this Soviet map"

**Image diversity implementation**:

- Hard examples resampled for each pass using frequency-capped random sampling
- Canonical examples (legend-derived symbols) and null tiles remain fixed
- See Section 8.4.3 for methodology

**Temperature diversity implementation**:

- 5-pass sequence: T=[0.7, 0.85, 1.0, 1.15, 1.3]
- Spans the range tested in H7 (temperature hypothesis), excluding T=0.0 (deterministic, no diversity contribution)

**Analysis**:

- Compare F1 across all 5 conditions
- Test whether effects are additive (E ≈ sum of B, C, D effects) or synergistic (E > sum)
- Examine whether mechanisms are redundant (multiple mechanisms produce similar gains)

**Replication**: Each condition run 5 times to provide symmetric variance estimates.

**Advance to further exploration if**: Any diversity mechanism significantly improves F1 over baseline.

---

### Tier B: Budget-Dependent Exploratory

*Tests conducted if budget permits and triggered by Stage 1-2 results.*

### H10: Training Pool Size Effects on Library Quality

**Status**: Exploratory (Tier B)

**Background**: Few-shot library construction (Section 8.4.1) identifies hard examples from training tile evaluation. A larger training pool may surface more diverse or representative hard examples, improving the resulting library's effectiveness.

**Question**: How does training pool size affect detection performance on held-out tiles?

**Test**: Construct few-shot libraries from progressively larger training pools:

| Condition | Training Tiles | Holdout Tiles | Notes |
| --------- | -------------- | ------------- | ----- |
| A | 20 | 60 | Current design |
| B | 40 | 60 | 2× training |
| C | 80 | 60 | 4× training |
| D | 160 | 60 | 8× training |

**Implementation**:

- Training pools are nested (A ⊂ B ⊂ C ⊂ D) for comparability
- Same holdout set across all conditions
- Library construction procedure (Section 8.4.1) applied identically to each pool
- Document resulting library composition for each condition

**Analysis**:

- F1 on holdout as function of training pool size
- Characterise diminishing returns curve
- Compare library composition across conditions (do larger pools find different hard examples?)

**Constraints**:

- Total tiles available: 361
- Holdout fixed at 60 tiles
- Maximum training pool: ~301 tiles (361 − 60 holdout)

**Sequencing**: Conducted after Stage 2 completion but before generalisation to out-of-sample maps. Training pool expansion draws from the reserve set, which is permissible after Stage 2 evaluation is complete.

---

### H11: Tile Size Effects on Detection Performance

**Status**: Exploratory (Tier B)

**Trigger**: Run if detection performance on 512×512 tiles shows room for improvement (F1 < 0.85) or if processing speed is a concern for deployment.

**Background**: Recent research suggests smaller tiles may improve VLM detection of small map symbols (Qiao et al., 2024). While larger tiles reduce API calls, smaller tiles increase the symbol-to-pixel ratio and may improve attention to fine details.

**Question**: Does reducing tile size from 512×512 improve detection performance?

**Test**: Apply optimal configuration from Stages 1-2 across tile sizes:

| Condition | Tile Size | Area Multiplier | API Calls (×) | Symbol:Pixel Ratio |
| --------- | --------- | --------------- | ------------- | ------------------ |
| A | 512×512 | 1× (baseline) | 1× | Lower |
| B | 384×384 | 0.56× | ~1.8× | Higher |

**Rationale for 384×384**: Maintains reasonable coverage per tile while increasing symbol visibility. Smaller sizes (256×256) would require >4× API calls, exceeding budget constraints.

*Note: The original hypothesis tested larger tiles (1024×1024, 2048×2048). This has been revised based on literature suggesting VLM attention to small features degrades with larger tiles. Pilot testing at 256px confirmed high recall (0.90) but very low precision (0.10) at 2/5 threshold, suggesting smaller tiles may over-detect. The 384×384 test size balances improved symbol visibility with practical precision constraints.*

**Implementation**:

- Uses optimal configuration (M/E, H5, T, voting) from Stages 1-2
- Tiles generated from source maps with 64px overlap
- Few-shot library images regenerated at 384×384 for Condition B
- Ground truth regenerated for smaller tile boundaries

**Analysis**:

- F1 as function of tile size
- Cost-efficiency analysis: F1 improvement vs API call increase
- Qualitative assessment: Does smaller size help with crowded areas?

---

### H12: Hard Positive to Hard Negative Ratio

**Status**: Exploratory (Tier B)

**Prerequisite**: H8 (library size) complete; optimal library size determined

**Background**: The main factorial (H8) uses a 1:1 ratio of hard positives to hard negatives across all library sizes. However, optimal ratio may differ:

- Higher HP:Emp-HN ratio may improve recall (more positive guidance)
- Lower HP:Emp-HN ratio may improve precision (more exclusion examples)
- Optimal ratio may depend on library size or baseline error profile

**Research question**: Does the ratio of hard positives to hard negatives affect detection performance, holding total hard example count constant?

**Test**: At optimal library size from H8 (selecting from A-D only; Pure/Canonical excluded as they have no empirical hard examples), compare ratios while holding total hard example count constant:

| Condition | HP | Emp-HN | Total Hard | Ratio |
| --------- | -- | ------ | ---------- | ----- |
| R1 | 2 | 6 | 8 | 1:3 (HN-heavy) |
| R2 | 4 | 4 | 8 | 1:1 (balanced) |
| R3 | 6 | 2 | 8 | 3:1 (HP-heavy) |

**Note**: Exact counts depend on optimal library size from H8.

**Analysis**:

- Compare F1, precision, and recall across ratio conditions
- Test whether ratio affects precision vs recall differentially
- Identify whether ratio interacts with baseline error profile (FP-heavy vs FN-heavy tiles)

**Trigger**: Run if H8 shows library size matters AND budget permits (~$9 additional)

---

### H13: Overlap/Stride Effects on Detection Performance

**Status**: Exploratory (Tier B)

**Background**: Current tiling uses 64px overlap (12.5% of 512px tile, 448px stride). Higher overlap increases redundant coverage, potentially catching symbols near tile edges that might be missed or poorly detected. However, it also increases API costs proportionally.

**Question**: Does increasing tile overlap improve detection performance, and is the cost justified?

**Test**: Compare detection performance across overlap conditions:

| Condition | Overlap | Stride | Overlap % | Tiles (×) | API Cost (×) |
| --------- | ------- | ------ | --------- | --------- | ------------ |
| A | 64px | 448px | 12.5% | 1× | 1× |
| B | 128px | 384px | 25% | ~1.4× | ~1.4× |
| C | 256px | 256px | 50% | ~2× | ~2× |

**Rationale**: Higher overlap provides:

1. Redundant coverage of tile-edge regions where symbols may be truncated
2. Multiple perspectives on the same location for improved voting
3. Potential for post-processing deduplication to improve confidence

**Implementation**:

- Uses optimal configuration from Stages 1-2
- Spatial deduplication applied to handle redundant detections
- Ground truth matching accounts for symbols detected in multiple overlapping tiles

**Analysis**:

- F1 as function of overlap
- Cost-efficiency: F1 improvement per additional API dollar
- Edge-detection analysis: Does overlap specifically help symbols near original tile boundaries?

**Trigger**: Run if significant edge-effect errors observed in Stage 2 holdout evaluation.

---

### Tier C: Deferred to Paper 2

*Tests requiring cross-provider API access, deferred to subsequent publication.*

### H14: Cross-Model Consistency

**Status**: Exploratory (Tier C — deferred)

**Background**: Results obtained on Gemini 3 Flash may not generalise to other VLM architectures. Testing across Claude and GPT validates that findings reflect task properties rather than Gemini-specific behaviours.

**Prediction**: The Flash-optimal configuration will perform reasonably on Claude and GPT models, with at most minor factor adjustments needed.

**Scope**: This hypothesis is deferred to Paper 2 due to:

1. Budget constraints for cross-provider API costs
2. Need to first establish robust findings on single provider
3. Complexity of managing multiple API integrations

**Brief protocol**: Stepwise adjustment from Flash-optimal using OFAT sensitivity testing, mirroring H6 protocol. Each model tested independently on same holdout set.

---

### H15: Cross-Model Consensus Voting

**Status**: Exploratory (Tier C — deferred)

**Background**: Within-model consensus voting (H3) improves performance by averaging across passes. Voting across architecturally different models may provide more independent error patterns.

**Question**: Does cross-model voting outperform within-model voting at equivalent total passes?

**Scope**: This hypothesis is deferred to Paper 2 due to:

1. Dependency on H14 results (need to know if models perform comparably)
2. Cross-provider API coordination complexity
3. Budget constraints

**Brief protocol**: Compare N=6 pass voting: 6× single model vs 2× each of three models.

---

## 7. Summary Table

### 7.1 Confirmatory Hypotheses (H1-H8)

| Hypothesis | Prediction | Test Type | Advance to Stage 2 if... |
| :--------- | :--------- | :-------- | :------------------------ |
| H1 (M/E level) | Text modality no effect; verbose no benefit | Planned contrasts | Significant M/E effect or interaction |
| H2 (two-stage) | Neither architecture improves over single-stage | Compare F1 | Either direction shows ≥0.05 F1 improvement |
| H3 (consensus voting) | Voting improves over single-pass | One-tailed | Significant improvement |
| H4 (example ordering) | Canonical-last > canonical-first | One-tailed | Significant ordering effect |
| H5 (hard negatives) | Precision ↑, recall stable | One-way ANOVA (3 levels) | Precision up, recall stable |
| H6 (Flash→Pro transfer) | Effects replicate on Pro | OFAT sensitivity | Transfer confirmed |
| H7 (temperature) | T=1.0 optimal | One-way ANOVA (4 levels) | Any temperature outperforms 1.0 |
| H8 (library size) | Diminishing returns | One-way ANOVA (6 levels) | Optimal library size identified |

### 7.2 Exploratory Hypotheses (H9-H15)

| Hypothesis | Tier | Question | Analysis |
| :--------- | :--- | :------- | :------- |
| H9 (diversity) | A | Do text/image/temperature diversity mechanisms help voting? | 5-condition comparison |
| H10 (training pool) | B | How does pool size affect library quality? | F1 vs pool size curve |
| H11 (tile size) | B | Does smaller (384×384) tile size improve detection? | Compare F1, cost-efficiency |
| H12 (HP:HN ratio) | B | Does hard example ratio affect performance? | Compare ratios at fixed total |
| H13 (overlap/stride) | B | Does increased overlap improve edge detection? | F1 vs overlap, cost analysis |
| H14 (cross-model) | C | Do effects generalise across providers? | Deferred to Paper 2 |
| H15 (cross-model voting) | C | Does cross-model voting outperform within-model? | Deferred to Paper 2 |

---

## 8. Implementation Details

### 8.1 Models

**Primary**: Gemini 3 Flash, Gemini 3 Pro

**Secondary (for H14)**: Claude 4.5 Haiku, Sonnet, Opus; GPT-5.2 Thinking, Pro

### 8.2 API Parameters

All models tested at maximum capability configuration. Parameters

**Gemini 3 (Google):**

| Model | Model ID | thinking\_level |
| ----- | ----- | ----- |
| Flash | `gemini-3-flash` | `high` |
| Pro | `gemini-3-pro` | `high` |

Fixed parameters:

- `temperature`: 1.0 (vendor recommended; preliminary testing suggested lower values may degrade performance — tested explicitly in H7)
- `mediaResolution`: `default (media_resolution_medium)`
- `max_output_tokens`: 8192

**Claude 4.5 (Anthropic):**

| Model | Model ID | effort | thinking.budget\_tokens |
| ----- | ----- | ----- | ----- |
| Haiku | `claude-haiku-4-5-20251001` | — | 8192 |
| Sonnet | `claude-sonnet-4-5-20250929` | — | 8192 |
| Opus | `claude-opus-4-5-20251101` | `high` | 16384 |

Fixed parameters:

- `temperature`: 1.0
- `max_tokens`: 16384 (must exceed budget\_tokens)

Notes: Extended thinking enabled for all variants. Effort parameter (beta) applied to Opus only.

**GPT-5.2 (OpenAI):**

| Model | Model ID | reasoning.effort | Notes |
| ----- | ----- | ----- | ----- |
| Instant | `gpt-5.2-chat-latest` | N/A | Speed-optimised variant; 128k context |
| Thinking | `gpt-5.2` | `xhigh` | Maximum single-path reasoning |
| Pro | `gpt-5.2-pro` | `xhigh` | Parallel reasoning threads |

Fixed parameters:

- `temperature`: 1.0 (fixed; cannot be modified)
- `verbosity`: `low`
- `max_output_tokens`: 8192

All other parameters left at provider defaults.

**Large tile handling (Gemini)**: For tiles ≥1024px (used in H2 fine-to-coarse testing), the Gemini API requires `media_resolution="high"` to process the full image at native resolution. Without this parameter, Gemini internally tiles large images into 768×768 patches, potentially losing spatial context at patch boundaries.

#### Cross-Model Comparability

**Reasoning parameters are not directly comparable across providers.** Each provider implements reasoning/thinking capabilities differently:

- **Gemini**: `thinking_level` controls internal deliberation depth
- **Claude**: `extended_thinking` produces visible chain-of-thought; `effort` (beta) scales reasoning
- **GPT**: `reasoning.effort` controls search depth for reasoning models

These mechanisms differ in architecture, compute allocation, and output characteristics. No principled method exists to establish "equivalent" reasoning effort across providers (cf. [Sys2Bench](https://arxiv.org/abs/2502.12521) finding that inference-time techniques are not consistently comparable).

**Our approach**: Descriptive comparison at provider-recommended settings.

| Provider | Setting Used | Interpretation |
| :--- | :--- | :--- |
| Gemini | `thinking_level=high` | Provider's maximum reasoning mode |
| Claude | Extended thinking + `effort=high` (Opus) | Provider's maximum reasoning mode |
| GPT | `reasoning.effort=xhigh` | Provider's maximum reasoning mode |

Cross-model comparisons should be interpreted as "performance at provider-recommended high-reasoning configuration" rather than matched computational effort.

#### Cost-Performance Analysis

The primary value of cross-model comparison is enabling practitioners to make informed cost-performance tradeoffs. We will report:

1. **Performance metrics**: F1, precision, recall at 20m tolerance for each model
2. **Cost metrics**: USD per tile (input + output tokens × provider pricing at time of experiment)
3. **Efficiency frontier**: Pareto-optimal models (no other model achieves higher F1 at lower cost)
4. **Cost-normalised comparison**: F1 per dollar, allowing selection based on budget constraints

**Pricing documentation**: API pricing will be recorded at experiment start and included in supplementary materials. If pricing changes during the study, both prices will be documented.

**Recommendation format**: Results will include guidance such as:
> "For budget-constrained applications, Model X achieves Y% of maximum F1 at Z% of the cost. For maximum performance regardless of cost, Model W is recommended."

**Version documentation**: Model version identifiers are automatically captured from API response metadata and will be reported in supplementary materials.

### 8.3 Prompt Variants

This section documents the prompt structure and text diversity methodology.

#### 8.3.1 Base Instruction Structure

All detection prompts share a common structure:

1. **Task framing**: Brief statement of the detection goal
2. **Output format**: JSON schema specification with normalised coordinates (0-1000)
3. **Few-shot examples**: Provided via the config file's `examples` array

The base image-only instruction is intentionally minimal:

```markdown
# Mound Detection (Image-Only)

Scan the Target Image. Mark all symbols that look like the Positive examples.

Return JSON with normalised coordinates (0-1000):
{"detections": [{"box_2d": [ymin, xmin, ymax, xmax], "label": "mound"}]}
```

The text+image variant adds domain context and explicit guidance (see `detect_text-image.md`).

#### 8.3.2 H9 Text Diversity Methodology

For H9 Conditions B and E (varied text), we use 5 semantically equivalent instruction variants. Each variant:

- Conveys the same detection task
- Uses different vocabulary and phrasing
- Maintains identical output format specification
- Is assigned to one pass in the 5-pass voting scheme

**Example variant texts** (illustrative; final wording to be documented before holdout evaluation):

| Variant | Task Framing |
| :--- | :--- |
| V1 | "Identify burial mound symbols in this map section" |
| V2 | "Detect tumuli markers on this topographic map" |
| V3 | "Find kurgan indicators in this image" |
| V4 | "Locate ancient burial mound cartographic symbols" |
| V5 | "Mark all mound features shown on this Soviet map" |

**Constraints:**

- All variants use the same output JSON schema
- Vocabulary diversity targets: archaeological terminology (burial mound, tumulus, kurgan), cartographic terminology (symbol, marker, indicator), action verbs (identify, detect, find, locate, mark)
- Final instruction files will be committed to the repository before holdout evaluation

#### 8.3.3 H9 Text Diversity Specification

**Variation level**: Level 3 (Content variation, fixed structure)

All 5 prompt variants maintain identical structure (same sections, same order, same output format) while varying:

1. **Task framing**: The opening instruction line using varied terminology:
   - Action verbs: identify, detect, find, locate, mark
   - Domain vocabulary: burial mound, tumuli, kurgan, mound features, cartographic symbols

2. **Instruction phrasing**: The task elaboration sentence following reference examples (semantically equivalent, differently worded)

3. **Guideline wording**: Semantically equivalent guidelines with varied phrasing (e.g., "focus on sunburst shape" vs "look for gear/ship's wheel pattern"; "include borderline cases" vs "favour inclusion over omission")

**Elements held constant across all variants:**

- Section headers and order
- Output format specification (JSON schema)
- Number and type of guidelines (3 guidelines in all variants)
- Reference example labelling convention
- Exclusion guidance text (if hard negatives in base config)

**Rationale**: This isolates content diversity from structural diversity, enabling clean attribution of any observed effect to semantic variation rather than prompt organisation.

**Potential extension**: If content diversity shows significant benefit, structural diversity (varied section headers, reorganised flow) may be explored as a follow-on investigation in Stage 2.

**Construction procedure**:

1. Identify optimal base configuration from main factorial (M/E, H5, T)
2. Use the winning prompt template as the structural base
3. Create V1–V5 by varying task framing, instruction phrasing, and guideline wording
4. Verify semantic equivalence across all 5 variants
5. Document final prompt text in pre-holdout specifications

#### 8.3.4 Runtime Parameters

The following parameters are specified at runtime, not in config files:

- **Temperature**: T ∈ {0.0, 0.7, 1.0, 1.3} as per factorial design (Section 8.4.7)
- **Model**: Flash vs Pro specified via command-line argument
- **Number of passes (N)**: For voting experiments

### 8.4 Few-Shot Library and Verbose Text Construction

The few-shot library AND verbose text additions will be constructed empirically using training tiles only, following this procedure. Hard examples (images) and verbose text additions are derived from the same source — image-only baseline failures on training tiles. This ensures text descriptions align with the visual examples shown to the model.

**Rationale for aligned construction**:

- Image-based discovery is the primary optimisation target
- Text-only conditions serve as academic baseline comparisons
- Aligned text and images reinforce rather than contradict
- Avoids potential confusion from text describing failures not shown in images

#### 8.4.1 Library and Text Construction Procedure

**Step 1: Image-Only Baseline**

Run baseline detection on training tiles:

- Prompt: Image-only (4 canonical positives + 3 null tiles, minimal text instruction)
- Passes: 5 × 20 training tiles = 100 API calls
- Temperature: T=1.0

**Step 2: Failure Analysis**

Identify systematic failures:

- **False Negatives (FNs)**: Ground truth mounds missed in ≥3/5 passes
- **False Positives (FPs)**: Detections in ≥3/5 passes with no matching ground truth

Rank by frequency and categorise by failure type.

**Step 3: Construct Hard Example Library**

Select hard examples based on frequency ranking:

- **Hard positives**: Top K FNs (target K=4)
- **Hard negatives**: Top M FPs (target M=3)

Document for each selected example: source tile, frequency, failure category.

**Step 4: Construct Brief Text**

Build brief text with terse descriptions:

| Component | Source | Content |
| --------- | ------ | ------- |
| Canonical descriptions | Legend | Terse descriptions of 4 canonical mound types |
| HP edge case guidance | Hard positive images | Terse mention of edge case types ("symbols may be partially occluded by roads or contours") |

Word count: ~200-300 words.

**Step 5: Construct Verbose Text**

Expand brief text with detailed guidance:

| Component | Source | Content |
| --------- | ------ | ------- |
| Canonical descriptions | Legend | Detailed descriptions of 4 canonical types (size, colour, ray count, context) |
| HP edge case guidance | Hard positive images | Detailed guidance on occlusion types, degradation patterns, clustering, variant types as identified in library |

Word count: ~500-700 words.

**Brief vs Verbose distinction**: Both include the same content categories (canonical symbols + HP edge cases). The difference is detail level, not content coverage.

**Note on exclusion guidance**: Exclusion guidance for hard negatives (FPs) is NOT included in either brief or verbose text. Instead, it is controlled by the H5 factor via `_hardneg.md` instruction variants:

- H5=None: No exclusion text
- H5=Images-only: Hard negative images with minimal labels
- H5=Text+Images: Hard negative images with explanatory exclusion text

This separation ensures H1 (M/E level) and H5 (hard negative guidance) remain orthogonal factors.

**Text-modality consistency**: Identical text is used across modalities (text-only brief = text+image brief; text-only verbose = text+image verbose). Text-only conditions receive the same guidance; they just lack visual examples to anchor it.

**Step 6: Document and Upload**

Before any holdout evaluation, upload to OSF: library manifest, brief text, verbose text, mapping table (hard example image ↔ corresponding text guidance).

#### 8.4.2 Library Composition

The library comprises five example categories:

| Category | Abbreviation | Source | Purpose | Selection |
| :--- | :--- | :--- | :--- | :--- |
| Canonical positive | Canon+ | Map legend | Establish clear positive prototypes | 4 legend-derived mound types |
| Canonical negative | Canon- | Map legend | Distinguish markers on mounds from standalone markers | 2 legend-derived non-mound symbols |
| Hard positive | HP | FN mining | Cover difficult positive cases | Top K by frequency (target K=4) |
| Empirical hard negative | Emp-HN | FP mining | Prevent common false positives | Top M by frequency (target M=3) |
| Null tile | — | Training set | Establish "no mounds" baseline | Stratified sample (n=3) |

**Category ratios**: The baseline library uses 4:2:K:M:3 (Canon+:Canon-:HP:Emp-HN:null). For H5 conditions without empirical hard negatives, the ratio becomes 4:2:K:0:3. Only H8 Pure omits Canon-.

**Library size variations**: Total library size varies by condition:

- Minimal: 7 examples (4 canonical + 3 null; no hard examples)
- Baseline: 7 + K + M examples (with hard positives and negatives)
- Extended: May include additional hard examples if pool allows (documented)

#### 8.4.3 Baseline Library

**Canonical positives (Canon+)** — legend-derived mound types:

- Burial mound, settlement mound, triangulation on mound, benchmark on mound

**Canonical negatives (Canon-)** — legend-derived non-mound markers:

- Standalone triangulation point, standalone benchmark
- **Purpose**: Distinguish "marker on mound" from "marker alone" — prevents confusion between composite symbols and their components

**Null tiles** (3 tiles selected via stratified sampling):

- Pool: Training tiles with density=empty (mound\_count=0)
- Content threshold: ≤75% background pixels (ensures meaningful map content)
- Stratification: One tile per map, with Lesovo required
- Random seed: 20251223

**Selected tiles** (n=3):

| Tile | Map | Background % | Note |
| :---- | :---- | :---- | :---- |
| K-35-078-1\_Lesovo\_x2240\_y2688.png | Lesovo | 10% | Required for distinct terrain |
| K-35-053-3\_Elenovo\_x3584\_y1344.png | Elenovo | 30% | Stratified random |
| K-35-052-4\_32635\_x896\_y1792.png | 32635 | 10% | Stratified random |

**Rationale**:

- Lesovo was required because it has visually distinct terrain (forested, different symbol density) compared to the other maps
- Stratified selection ensures geographic diversity
- Low background percentage ensures tiles contain meaningful cartographic content rather than being mostly blank margins

**Ordering (for H4)**:

- "Canonical-first" condition: Legend-derived symbols in initial positions, hard examples last
- "Canonical-last" condition: Hard examples in initial positions, legend-derived symbols last
- "Random" condition: Shuffled with documented seed

#### 8.4.4 Cross-Pass Sampling Methodology (for H9 Image Diversity)

For conditions requiring varied examples across passes (H9 Conditions C and E), we use frequency-capped random sampling to ensure diversity while maintaining statistical power for example-level analysis.

**Sampling constraints:**

| Constraint | Rule | Rationale |
| :--- | :--- | :--- |
| Within-pass uniqueness | No duplicate examples within a single pass | Each example contributes independently |
| Frequency floor | Each example appears in ≥ floor(N × 0.2) passes | Ensures sufficient data for regression |
| Frequency cap | Each example appears in ≤ ceil(N × 0.6) passes | Guarantees meaningful diversity |
| Category minimums | Each pass includes ≥1 canonical, ≥1 hard positive, ≥1 null | Maintains category representation |

**Decision rule for cap**: The exact frequency cap will be determined by library size once known:

- If library size k ≤ examples_per_pass × 2: No cap needed (natural diversity from sampling)
- If library size k > examples_per_pass × 2: Cap = ceil(N × 0.6)

**Sampling procedure:**

1. Initialise example frequency counters to zero
2. For each pass p in 1..N:
   a. Sample required category minimums (1 canonical, 1 hard positive, 1 hard negative if applicable, 1 null)
   b. Fill remaining slots by sampling from eligible examples (those below frequency cap)
   c. If insufficient eligible examples, relax cap for lowest-frequency examples
   d. Increment frequency counters for selected examples
   e. Record exact example assignment for pass p
3. Document random seed used for reproducibility

**Fixed elements across all passes:**

- Canonical positive examples (legend-derived) — always included in every pass
- Null tiles — always included in every pass
- Only hard positives and hard negatives vary across passes in "Varied" conditions

#### 8.4.5 Example-Level Effectiveness Analysis

Understanding which specific examples drive library effectiveness enables future library optimisation and provides insight into VLM few-shot learning mechanisms.

**Primary analysis (post-hoc regression):**

After completing H6 experiments, fit a linear model predicting pass-level F1 from example presence:

```text
F1_pass ~ β₀ + Σᵢ βᵢ(exampleᵢ_present) + ε
```

Where:

- `exampleᵢ_present` = 1 if example i appeared in that pass, 0 otherwise
- βᵢ estimates the marginal contribution of example i to F1
- Model fitted using ordinary least squares with robust standard errors

**Reporting:**

- Coefficient estimates (βᵢ) with 95% bootstrapped confidence intervals
- Flag examples where |βᵢ| > 0.02 F1 as "high-impact"
- Rank examples by absolute effect size within each category

**Secondary analysis (category-level effects):**

Aggregate example-level effects by category:

```text
F1_pass ~ β₀ + β_canon(n_canonical) + β_hardpos(n_hard_positive)
        + β_hardneg(n_hard_negative) + β_null(n_null) + ε
```

This estimates the marginal value of adding one more example of each type.

**Tertiary analysis (BIBD, if feasible):**

If library size k ≤ 10 and N ≥ 20, construct a Balanced Incomplete Block Design where:

- Each example appears in exactly r passes (r ≈ N/2)
- Each pair of examples co-occurs in exactly λ passes

This enables ANOVA decomposition:

```text
F1 = μ + Σᵢ(main effect of exampleᵢ) + Σᵢⱼ(interaction of exampleᵢ × exampleⱼ) + ε
```

BIBD parameters will be determined post-library-construction and documented before holdout evaluation.

**Documentation commitment:**

The following will be published as supplementary data:

- Exact example assignment matrix (passes × examples)
- Achieved frequency distribution per example
- Regression coefficients and diagnostics
- Random seeds used for all sampling

#### 8.4.6 Hypothesis Interaction Summary

The following table summarises how library-related hypotheses interact and which experimental parameters vary:

| Hypothesis | What Varies | Fixed Elements | Library Size | Passes |
| :--------- | :---------- | :------------- | :----------- | :----- |
| H3 (voting) | N, T (vote threshold) | Library composition, ordering | Baseline | 5, 10, 30 |
| H4 (ordering) | Example order within pass | Library composition, which examples | Baseline | 5 |
| H5 (hard negatives) | Presence/modality of hard negative category | Canonical, hard positive, null | Varies | 5 |
| H9 (diversity) | Which hard examples per pass; prompt text; temperature | Canonical + null (always present) | Baseline | 5 |

**Interaction constraints:**

| Interaction | Resolution |
| :---------- | :--------- |
| H4 × H9 | H4 ordering applies to the examples selected for each pass; in H9 "Varied" conditions, ordering is applied after sampling |
| H4 × H5 | H5 conditions without hard negatives use ordering over reduced library (canonical + hard positive + null only) |
| H9 × H5 | H9 image diversity varies hard positives and hard negatives (when present); H5=None has no hard negatives to vary |
| H3 × H9 | H3 vote threshold optimisation uses H9 Condition A (fixed library) as baseline; diversity effects tested at fixed N=5 |

**Execution order:**

1. **H5 first**: Determines whether hard negatives are included (establishes library composition)
2. **H4 second**: Tests ordering effects on the established library
3. **H9 third**: Tests diversity effects (requires H4 baseline for comparison)
4. **H3 throughout**: Vote threshold grid search runs in parallel across conditions

**Cross-hypothesis analysis:**

After individual hypothesis tests, exploratory analyses will examine:

- Whether optimal voting threshold (H3) differs by library composition (H5)
- Whether ordering effects (H4) interact with diversity (H9)
- Whether example-level effects (Section 8.4.4) explain hypothesis-level results

#### 8.4.7 Stranded Factorial Design

**Rationale**: The factorial cleanly separates text elaboration (how much detail) from library content (how many hard examples). This is achieved via a stranded design:

- **Strand 1**: M/E × partial H5 cross — tests H1, H5, H7
- **H5 Confirmatory**: Full 3-level decomposition at optimal M/E — decomposes H5 mechanism
- **Strand 2**: Library size (H8) — tests diminishing returns of hard examples
- **Strand 3**: Interaction check (conditional) — tests M/E × library interaction

*Note: Text-only modalities are tested at T=1.0 only to reduce budget, as preliminary testing showed temperature effects are minimal for text-only conditions.*

**Core experimental factors:**

| Factor | Symbol | Levels | Description |
| :----- | :----- | :----- | :---------- |
| Modality/Elaboration | M/E | 5 | Image-only, Brief+image, Verbose+image, Brief-text, Verbose-text |
| Hard negatives | H5 | 3 | None, Images-only, Text+Images |
| Temperature | T | 4 | 0.0, 0.7, 1.0, 1.3 |
| Library size | L | 6 | Pure (7), Canonical (9), A (13), B (17), C (25), D (41) |

**Strand 1: M/E × Partial H5 Cross**

Test M/E and H5 with temperature, but only test H5 extremes (None vs Text+Images) to detect interaction without full cross:

*Image-using modalities (3 levels):*

| M/E Level | H5=None | H5=Text+Images |
| --------- | ------- | -------------- |
| Image-only | ✓ (4T) | ✓ (4T) |
| Brief+image | ✓ (4T) | ✓ (4T) |
| Verbose+image | ✓ (4T) | ✓ (4T) |

*Text-only modalities (2 levels):*

| M/E Level | H5=None |
| --------- | ------- |
| Brief-text | ✓ (T=1.0 only) |
| Verbose-text | ✓ (T=1.0 only) |

**Note**: Text-only modalities are tested at H5=None only (no example images) and T=1.0 only (budget efficiency).

**Strand 1 totals:**

| Component | Cells |
| --------- | ----- |
| Image M/E (3) × H5 (2) × T (4) | 24 |
| Text M/E (2) × H5=None × T=1.0 | 2 |
| **Total** | **26** |

**API calls**: 26 × K=10 × 60 tiles = **15,600 calls** (~$23)

**H5 Confirmatory: Full 3-Level Decomposition**

After Strand 1 identifies optimal M/E level, test all 3 H5 levels at that M/E to decompose the mechanism:

| H5 Level | Exclusion Text | HN Images | Image Labels |
| -------- | -------------- | --------- | ------------ |
| None | No | No | — |
| Images-only | No | Yes | Minimal ("Negative") |
| Text+Images | Yes | Yes | Detailed (with explanation) |

**H5 Confirmatory totals:**

- 1 M/E × 3 H5 × 4 T = **12 cells** (but 8 already run in Strand 1)
- New cells: 1 M/E × 1 H5 (Images-only) × 4 T = **4 cells**
- **API calls**: 4 × K=10 × 60 tiles = **2,400 calls** (~$4)

**Strand 2: Library Size (H8)**

Test 6 library conditions at optimal M/E and H5 from Strand 1:

| Condition | Canon+ | Canon- | HP | Emp-HN | Nulls | Total |
| --------- | ------ | ------ | -- | ------ | ----- | ----- |
| Pure | 4 | 0 | 0 | 0 | 3 | 7 |
| Canonical | 4 | 2 | 0 | 0 | 3 | 9 |
| A | 4 | 2 | 2 | 2 | 3 | 13 |
| B | 4 | 2 | 4 | 4 | 3 | 17 |
| C | 4 | 2 | 8 | 8 | 3 | 25 |
| D | 4 | 2 | 16 | 16 | 3 | 41 |

**H5 Constraint**: Pure and Canonical run at H5=None (no empirical HNs available). Conditions A-D run at optimal H5 from Strand 1.

**Strand 2 totals:**

- 6 conditions × 4 T = **24 cells**
- **API calls**: 24 × K=10 × 60 tiles = **14,400 calls** (~$22)

**Strand 3: Interaction Check (Conditional)**

If Strand 1 AND Strand 2 show significant effects, check whether optimal M/E depends on library size by testing a second M/E level across library conditions.

**Trigger**: Run if BOTH:

1. Strand 1 shows significant M/E effect (p < 0.05), AND
2. Strand 2 shows significant library size effect (p < 0.05)

**Strand 3 totals:**

- 1 additional M/E × 6 conditions × 4 T = **24 cells** (but ~8 already run in Strand 1)
- **API calls**: ~8 × K=10 × 60 tiles = **4,800 calls** (~$7)

**Total stranded design:**

| Component | Cells | Calls | Cost |
| --------- | ----- | ----- | ---- |
| Strand 1 (M/E × partial H5) | 26 | 15,600 | ~$23 |
| H5 Confirmatory (Images-only level) | 4 | 2,400 | ~$4 |
| Strand 2 (Library size) | 24 | 14,400 | ~$22 |
| **Base total** | **54** | **32,400** | **~$49** |
| Strand 3 (conditional) | 8 | 4,800 | ~$7 |
| H5 Expansion (2nd M/E, if triggered) | 4 | 2,400 | ~$4 |
| **Maximum total** | **66** | **39,600** | **~$60** |

*Note: Budget reduced from v3.x (~$90 base) due to simplifications: H5 reduced from 4 to 3 levels, temperature reduced from 5 to 4 levels, text-only modalities tested at T=1.0 only.*

**Note on ordering (H4)**: Example ordering is tested as a partial cross (see H4), not in the main strands. All strand conditions use canonical-first ordering. The H4 partial cross adds canonical-last and random ordering at 3 selected M/E levels.

**Text-image ordering constraint:**

For text+image conditions, text ordering corresponds with image ordering:

- If example images are ordered [burial_mound, settlement_mound, ...], the text descriptions follow the same sequence
- Text always precedes images in the prompt structure (fixed position)

### 8.5 Voting Implementation

Consensus voting aggregates detections from multiple passes into a single prediction set.

#### Pooling Scope

Voting operates at the **region level** (geographic evaluation unit), not at the individual tile level. This distinction matters when tiles overlap or when multiple tiles cover the same geographic area:

1. **Within-pass deduplication**: Before voting, detections from overlapping tiles within the same pass are deduplicated using the 20m spatial tolerance. This prevents a single pass from contributing multiple votes for the same physical location detected in adjacent tiles.

2. **Cross-pass voting**: After within-pass deduplication, detections are pooled across all N passes and clustered to count distinct pass contributions.

This region-level approach ensures that tile boundaries (which are arbitrary processing artefacts) do not affect vote counts. A detection near a tile boundary that appears in multiple overlapping tiles within the same pass contributes only one vote from that pass.

#### Spatial Clustering Algorithm

1. **Deduplicate within each pass**: For each of N passes, cluster detections from all tiles using 20m tolerance; retain one centroid per cluster
2. **Pool deduplicated detections** from all N passes into a single collection
3. **Compute pairwise distances** between detection centroids
4. **Cluster detections** using distance threshold matching the F1 evaluation tolerance (20m):
   - Detections within 20m of each other are candidates for the same cluster
   - Greedy clustering: for each unclustered detection, find all others within 20m and matching label; group as cluster
5. **Count votes per cluster**: number of distinct passes contributing at least one detection to the cluster
6. **Apply vote threshold**: retain clusters with ≥ T votes (e.g., ≥2/5 for 5-pass voting)
7. **Output geometry**: centroid of cluster members' centroids

#### Consensus Detection Output

For each cluster meeting the vote threshold:

- **Geometry**: Mean centroid of constituent detections
- **Label**: Majority vote among constituent detection subtypes
- **Confidence**: Vote count / total passes (e.g., 4/5 = 0.8)
- **Source**: List of contributing pass IDs

#### Alignment with F1 Evaluation

The 20m clustering threshold deliberately matches the spatial tolerance used in F1 calculation (Section 4.1.1). This ensures that:

- Detections considered "the same" during voting are also treated as matching the same reference during evaluation
- No artificial precision loss from threshold misalignment

#### Parameters for H3 Test

| Parameter | Values | Rationale |
| :--- | :--- | :--- |
| N (passes) | 5, 10, 30 | Explore cost-performance tradeoff |
| T (threshold) | 1 to N | Full grid search; no a priori threshold selection |
| Distance threshold | 20m | Matches F1 evaluation tolerance |
| Primary model | Gemini 3 Flash | Cost-efficient for full grid exploration |
| Validation models | Claude 4.5, GPT-5.2 | Confirm transferability of optimal parameters |

### 8.6 Tile Selection Methodology

Full methodology documented in `docs/methodology/tile-selection-methodology.md`. Summary below.

#### Data Sources

- **Maps**: 4 Soviet 1:50,000 topographic maps (Bulgaria)
  - K-35-052-4_32635, K-35-053-3_Elenovo, K-35-062-2_Rakovski, K-35-078-1_Lesovo
- **Tiles**: 512×512 pixel tiles at native resolution (~90 tiles per map, ~360 total)
- **Ground Truth**: 569 annotated mound symbols across all maps

#### Selection Criteria

| Criterion | Value | Rationale |
| :--- | :--- | :--- |
| **Content threshold** | ≤75% background (black) | Excludes predominantly empty edge tiles |
| **Training set** | 20 tiles (5 per map) | Sufficient for few-shot library development |
| **Holdout set** | 60 tiles (15 per map) | Expanded sample for improved statistical power |
| **Stratification** | Empty/Sparse/Dense | Balanced density representation |
| **Spatial separation** | Holdout tiles not adjacent to training tiles | Prevents spatial autocorrelation |

#### Tile Density Categories

| Category | Mound Count | Purpose |
| :--- | :--- | :--- |
| Empty | 0 | Tests false positive rate (hallucinations) |
| Sparse | 1-2 | Tests detection in low-density contexts |
| Dense | 3+ | Tests detection in high-density contexts |

#### Randomisation

- **Random seeds**: Training selection seed 1766464625 (2025-12-23), holdout selection seed 1767425239 (2026-01-03). Both documented in `inputs/tile_selection_metadata.json`
- **Stratified random sampling**: Within each map, sample proportionally from density strata
- **Reproducibility**: Re-running with same seeds produces identical selection

#### Output Artefacts

- `inputs/training_manifest.json` — list of training tile filenames
- `inputs/holdout_manifest.json` — list of holdout tile filenames
- `inputs/tile_selection_metadata.json` — full metadata (seed, mound counts, density strata)
- `outputs/results/training_bounds.geojson` — spatial extent of training tiles
- `outputs/results/holdout_bounds.geojson` — spatial extent of holdout tiles

#### Tile Exclusion Criteria

Tiles are excluded from the eligible pool (before random selection) if:

1. **Background threshold exceeded**: >75% background pixels (black [0,0,0])
2. **Off-map content**: Tile predominantly contains border/margin rather than map content

Tiles are excluded from analysis (after selection) if:

1. **API failure**: Request fails after 3 retries with exponential backoff
2. **Malformed response**: Response cannot be parsed as valid JSON
3. **Timeout**: Request exceeds 120 seconds
4. **Empty response**: Model returns no detections AND no explanation (indicates processing failure rather than genuine empty tile)

**Documentation requirement**: Any tile excluded after selection must be documented with:

- Tile filename
- Exclusion reason
- Number of retry attempts (if applicable)
- Whether the exclusion affected training or holdout set

---

### 8.7 Hypothesis-to-Implementation Mapping

This section maps each hypothesis to the specific configuration files, system instructions, and scripts that implement it.

#### 8.7.1 Implementation Status

**Confirmatory Hypotheses (H1-H8)**:

| Hypothesis | Description | Status | Implementation |
| :--- | :--- | :--- | :--- |
| H1 | M/E level (modality + elaboration) | ✅ Ready | Factorial factor (m_e_level) |
| H2 | Two-stage pipelines | ✅ Ready | Separate pipelines (coarse-to-fine, fine-to-coarse) |
| H3 | Consensus voting | ✅ Ready | Voting grid search |
| H4 | Example ordering | ✅ Ready | Factorial factor (ordering) |
| H5 | Hard negatives | ✅ Ready | Factorial factor (hard_negatives) |
| H6 | Flash→Pro transfer | ✅ Ready | Runtime model parameter |
| H7 | Temperature | ✅ Ready | Factorial factor (temperature) |
| H8 | Library size | ✅ Ready | Strand 2 core |

**Exploratory Hypotheses (H9-H15)**:

| Hypothesis | Description | Tier | Status | Implementation |
| :--- | :--- | :--- | :--- | :--- |
| H9 | Diversity mechanisms | A | 📋 Planned | Multi-pass variation (text/images/temperature) |
| H10 | Training pool size | B | 📋 Planned | Varied training pool sampling |
| H11 | Tile size | B | 📋 Planned | Tile dimension parameter (384×384) |
| H12 | HP:HN ratio | B | 📋 Planned | Varied positive/negative balance |
| H13 | Overlap/stride | B | 📋 Planned | Tile overlap parameter |
| H14 | Cross-model consistency | C | 📋 Deferred | Runtime model parameter (Claude, GPT) |
| H15 | Cross-model voting | C | 📋 Deferred | Multi-model ensemble voting |

#### 8.7.2 Configuration File Mapping

| Hypothesis | Config Files | System Instructions |
| :--- | :--- | :--- |
| H1 | `detect_{modality}_{elaboration}.json` variants | `detect_{modality}_{elaboration}.md` variants |
| H2 | `propose_*.json` + `verify_*.json` (coarse-to-fine); `detect_*.json` + `expand_*.json` (fine-to-coarse) | Corresponding `.md` files |
| H3 | Any detect config (passes parameter) | Any detect instruction |
| H4 | `*_canonical-last.json`, `*_random-order.json` | Same instruction file per modality |
| H5 | `*_hardneg.json` variants | `*_hardneg.md` variants |
| H6 | All configs (model runtime override) | All instructions |
| H7 | All configs (temperature runtime override) | All instructions |
| H8 | Strand 2 library configs | All instructions |

#### 8.7.3 Script Mapping

| Hypothesis | Primary Scripts | Analysis Scripts |
| :--- | :--- | :--- |
| H1, H4, H5, H7 | `run_study.py`, `4_detect_mounds_batch.py` | `lib_advanced_metrics.py` |
| H2 | `4_detect_mounds_batch.py` (2× sequential) | `7_analyze_consensus.py`, `8_analyze_proposer_consensus.py` |
| H3 | `run_study.py` (passes parameter) | `7_analyze_consensus.py` |
| H6 | `run_study.py` (model parameter) | `lib_advanced_metrics.py` |
| H8 | Strand 2 library configuration | `lib_advanced_metrics.py` |
| H9 | `run_study.py` (extended for diversity) | `lib_advanced_metrics.py` |

#### 8.7.4 Stranded Factorial Design Coverage (Phase 2)

The stranded factorial design tests H1, H5, H7, and H8 across multiple strands:

**Factor summary:**

| Factor | Levels | Values |
| :--- | :--- | :--- |
| M/E (Modality/Elaboration) | 5 | Image-only, Brief+image, Verbose+image, Brief-text, Verbose-text |
| H5 (Hard negatives) | 3 | None, Images-only, Text+Images |
| T (Temperature) | 4 | 0.0, 0.7, 1.0, 1.3 |
| L (Library size) | 6 | Pure, Canonical, A, B, C, D |

**Design**: Stranded structure (see Section 8.4.7):

- Strand 1: 26 cells (M/E × partial H5 × T; text-only at T=1.0 only)
- H5 Confirmatory: 4 cells (1 optimal M/E × H5=Images-only × 4 T)
- Strand 2: 24 cells (6 library conditions × T)
- Strand 3: ~10 cells (conditional interaction check)

**Config naming pattern**: `detect_{modality}_{hardneg}.json`

Temperature and library composition are specified at runtime, not in config files. This yields 9 config files.

**Config count**: Text-only modalities cannot use H5=Images-only or H5=Text+Images:

- 3 image-using modalities × 3 H5 levels = 9
- 2 text-only modalities × H5=None only = 2 (but runtime variants, not separate configs)
- **Total: 9 configurations** (text-only tested at T=1.0 only)

Example configurations:

| Config Pattern | M/E | H5 |
| :--- | :--- | :--- |
| `detect_image-only_none.json` | Image-only | None |
| `detect_brief-image_images.json` | Brief+image | Images-only |
| `detect_verbose-image_both.json` | Verbose+image | Text+Images |

**Runtime parameters** (specified at execution, not in config files):

- Temperature: T ∈ {0.0, 0.7, 1.0, 1.3}
- Model: gemini-3-flash, gemini-3-pro, claude-sonnet-4-5, etc.
- Number of passes (K): 10 for main factorial, varies for H3
- Library composition: Varies by strand (see Section 8.4.7)

**Note**: H4 (ordering) is tested as a partial cross, not in the main strands. All strand conditions use canonical-first ordering. See H4 for the 9-condition partial cross design (3 orderings × 3 M/E levels).

### 8.8 Calibration Pilot Outputs

Tile size and voting methodology were calibrated via pilot studies before holdout evaluation. Archived outputs:

| File | Description |
|------|-------------|
| `outputs/pilot/pilot_results.json` | Single-scale results with bootstrap CIs |
| `outputs/pilot/pilot_summary.md` | Human-readable summary |
| `outputs/pilot/pilot_decision.md` | Decision rationale for 512px retention |
| `outputs/pilot/multiscale_analysis.json` | Multi-scale voting analysis |
| `outputs/pilot/multiscale_full_sweep.csv` | Full parameter sweep (97 configurations) |
| `outputs/pilot/multiscale_summary.md` | Multi-scale summary |

These files document calibration decisions made before holdout evaluation and are archived for reproducibility. See Section 12.2 for multi-scale pilot findings.

---

## 9. Implementation Priority

### Tier 1: Must Test (Core Confirmatory)

- **H3** (consensus voting) — highest practical impact; foundational
- **H5** (hard negatives) — directly addresses precision issues
- **H8** (library size) — determines optimal hard example count

### Tier 2: Should Test (Secondary Confirmatory)

- **H4** (example ordering) — low implementation cost, clear theoretical basis
- **H7** (temperature) — validates vendor recommendation

### Tier 3: Lower Priority (Confirmatory)

- **H1** (M/E level) — already informally tested; confirmatory test validates preliminary findings
- **H2** (two-stage) — preliminary evidence suggests degradation
- **H6** (Flash→Pro transfer) — validates development approach

### Tier 4: If Resources Allow (Exploratory)

- **H9** (diversity) — refines H3; Tier A exploratory
- **H10** (training pool size) — Tier B exploratory
- **H11** (tile size) — Tier B exploratory
- **H12** (HP:HN ratio) — Tier B (conditional on H8)
- **H13** (overlap/stride) — Tier B exploratory
- **H14, H15** (cross-model) — Tier C, deferred to Paper 2

---

## 10. Stage 2 Planning (Contingent on Stage 1 Results)

Techniques that pass Stage 1 screening will be validated in Stage 2 with:

- **Larger sample**: 80-160 additional tiles from the 281-tile reserve set
- **Stricter correction**: Bonferroni or Holm-Bonferroni at α = 0.05
- **Transfer testing**: Tiles from maps outside the 4 annotated sheets (if feasible)
- **Optimised parameters**: For techniques that show promise, optimise hyperparameters (e.g., voting threshold, number of hard negatives)

### 10.1 Configuration Selection Strategy

Stage 2 will test the **top 3-5 configurations** from Stage 1 rather than only the single best performer. This approach:

- Guards against overfitting to Stage 1 sample
- Allows detection of configurations that generalise better despite slightly lower Stage 1 performance
- Provides robustness if top configuration has high variance

**Selection criteria**:

1. Include the highest-F1 configuration
2. Include configurations within 0.05 F1 of the best (if any)
3. Include configurations representing distinct factor combinations (e.g., if best uses image-only, include best text+image)
4. Maximum 5 configurations to maintain statistical power

### 10.2 Stage 2 Preregistration

Stage 2 will be separately preregistered after Stage 1 completion. The Stage 2 preregistration will specify:

- Exact configurations to test (based on Stage 1 results)
- Sample size and tile selection methodology
- Power analysis based on observed Stage 1 effect sizes
- Analysis plan with appropriate multiple comparison correction

This separation ensures Stage 2 design is informed by Stage 1 data without compromising preregistration integrity.

---

## 11. Preregistration Checklist

Before any test set evaluation:

- [ ] Finalise hypothesis list and predictions
- [ ] Specify exact test tile IDs (60 tiles, identified by map + tile number)
- [x] Specify primary outcome: Overall F1 at 20m spatial tolerance  
- [ ] Specify success threshold: F1 ≥ 0.85 for pipeline as a whole  
- [ ] Document few-shot library composition (examples, ordering)  
- [ ] Document prompt text for all conditions  
- [ ] Document hard negative examples (for H5)
- [ ] Document prompt variants (for H9)  
- [ ] Specify random seeds for any stochastic elements  
- [ ] Commit analysis code to repository  
- [ ] Submit to OSF Registries  
- [ ] Obtain timestamp confirmation  
- [ ] **Then** proceed to test evaluation

---

## 12. Future Directions

This section outlines promising research directions beyond the scope of Paper 1. These items are documented for transparency and to guide future work, but are explicitly **not part of the current preregistered study**.

### 12.1 Cross-Model Generalisation (Paper 2)

**Rationale**: Paper 1 focuses on Gemini 3 Flash for cost-efficiency. Future work should validate whether optimal configurations transfer across model families.

**Planned scope**:

- Test top 3-5 configurations from Paper 1 on Claude 4.5 Haiku/Sonnet and GPT-5.2 variants
- Compare within-family vs cross-family voting ensembles
- Assess whether model-specific tuning is necessary or whether universal configurations exist

### 12.2 Multi-Scale Fusion

**Rationale**: Burial mounds may be detected at multiple scales, and combining detections across tile sizes could improve both precision and recall by exploiting independent error patterns across scales.

**Calibration pilot results**: A pilot study (n=19 ground truth mounds, 10 regions) tested whether combining detections from multiple tile sizes improves performance. Three scales were tested on identical geographic coverage: 256px (160 tiles), 512px (40 tiles), and 1024px (10 tiles), each with K=5 detection passes.

- **Best multi-scale strategy**: Scale confirmation requiring agreement across all three scales achieved F1=0.61 [95% CI: 0.28–0.91]
- **Best single-scale baseline**: 512px at 4/5 voting threshold achieved F1=0.49 [95% CI: 0.14–0.73]
- **Improvement**: +0.12 F1, though confidence intervals overlap substantially due to limited ground truth

**Scale characteristics** (at 2/5 voting threshold):

- Small tiles (256px): High recall (0.90) but low precision (0.10) — detects most mounds but generates many false positives
- Medium tiles (512px): Balanced precision-recall trade-off
- Large tiles (1024px): Higher precision (0.28) but unacceptably low recall (0.37) — misses ~63% of mounds

**Error correlation**: Correlation of false negative patterns across scales was low to negative (small-medium: r=−0.18; small-large: r=−0.09; medium-large: r=+0.13), indicating independent error patterns that support the theoretical basis for multi-scale fusion.

**Disposition**: Multi-scale fusion is designated as **exploratory analysis** for Paper 2, contingent on validation with a larger ground truth set (target: 50+ mounds). The current preregistration retains 512px single-scale detection as the confirmatory methodology.

**Archived pilot data**:

- `outputs/pilot/multiscale_analysis.json` — structured results with bootstrap confidence intervals
- `outputs/pilot/multiscale_full_sweep.csv` — full parameter sweep (97 configurations)
- `outputs/pilot/multiscale_summary.md` — human-readable summary

### 12.3 Tile Size × Stride Interaction

**Rationale**: H11 (tile size) and H13 (overlap/stride) may interact—smaller tiles may require different overlap ratios than larger tiles.

**Planned scope**:

- Full factorial of 3 tile sizes × 3 overlap ratios (9 conditions)
- Identify optimal size/stride combinations for different terrain types
- Develop adaptive tiling strategies

### 12.4 Automated Library Construction

**Rationale**: Manual curation of few-shot libraries is time-consuming. Automated selection of informative examples could improve scalability.

**Planned scope**:

- Explore embedding-based example selection
- Test uncertainty-guided example sampling
- Compare automated vs manual library performance

### 12.5 Symbol-Specific Optimisation

**Rationale**: Different mound symbol types (burial mound, triangulation mound, settlement mound) may require different detection strategies.

**Planned scope**:

- Analyse per-symbol-type performance from Paper 1
- Develop symbol-specific prompts or libraries if needed
- Assess whether a unified approach or specialised pipelines are optimal

### 12.6 Transfer to Other Map Series

**Rationale**: This study uses Soviet 1:50,000 topographic maps of Bulgaria. Generalisation to other cartographic traditions is an open question.

**Planned scope**:

- Test on maps from other Eastern European countries (similar Soviet-era cartography)
- Test on Western European topographic series (different symbol conventions)
- Assess domain adaptation requirements

---

## 13. Outstanding Questions

The following items need to be specified before preregistration can be finalised:

### 13.1 Resolved

- [x] Anticipated data collection dates (Section 1.4)
- [x] Author affiliations (Section header)
- [x] Ground truth protocol (Section 2.6)
- [x] Spatial tolerance (Section 4.1.1)
- [x] Detection matching algorithm (Section 4.1.2)
- [x] API parameters (Section 8.2)
- [x] Tile IDs (Sections 2.3, 2.4)
- [x] Voting spatial matching (Section 8.5) — 20m distance-based clustering
- [x] Tile selection methodology (Section 8.6) — stratified random with spatial separation
- [x] Tile exclusion criteria (Section 8.6) — >75% background, API failures, malformed responses
- [x] Cross-model output format — identical JSON schema across all providers

### 13.2 Pending

*All critical items resolved. Minor items may be added during final review.*

---

## 14. Conflict of Interest

The authors declare no competing interests. This research received no external funding from AI model providers.

---

## 15. Ethics Statement

This study analyses historical map imagery and involves no human participants. No ethics approval was required.

---

## 16. Registration Statement

This preregistration will be submitted to OSF Registries using the OSF Preregistration format.

---

## 17. Data and Code Availability

- **Code**: All analysis scripts will be released via GitHub/OSF upon publication
- **API responses**: Raw API response logs will be archived (with timestamps)
- **Ground truth**: [Pending confirmation of Bulgarian data sharing requirements]
- **Map tiles**: [Pending confirmation of Bulgarian data sharing requirements]
- **Prompts**: All prompt text and configuration files documented in `preregistration-appendix-prompts.md`

### 17.1 Companion Documents

This preregistration is accompanied by the following supplementary documents:

| Document | Purpose |
|----------|---------|
| `preregistration-coverage.md` | Factorial coverage matrix, extended tests, explicit exclusions |
| `preregistration-appendix-prompts.md` | Complete prompt text for all system instructions and configurations |

---

## References

- Sobotkova, A., Ross, S.A., Nassif-Haynes, C., & Ballsun-Stanton, B. (2023). Creating large, high-quality geospatial datasets from historical maps using novice volunteers. *Applied Geography*, 155, 102967.
- Vo, A., et al. (2025). Vision Language Models are Biased. arXiv:2505.23941.

---

*Document version: 4.2*
*Created: 2025-12-22*
*Updated: 2026-01-07*

**Changelog:**

- v4.2: Pilot context additions — H2 fine-to-coarse note (1024px 37% recall limitation); H11 note expanded (256px precision issues); Section 12.2 scale characteristics threshold specified (2/5); Section 2.2 pilot validation cross-reference; Section 8.2 `media_resolution=high` documentation for large tiles; Section 8.8 added (calibration pilot outputs table)
- v4.1: Section 8.5 updated with region-level pooling methodology (within-pass deduplication before cross-pass voting; corrects for tile boundary artefacts); Section 12.2 expanded with multi-scale fusion pilot results (n=19 mounds, F1=0.61 multi-scale vs F1=0.49 single-scale, designated exploratory for Paper 2)
- v4.0: Major simplification — Hypotheses renumbered H1-H15 (8 confirmatory, 7 exploratory); H1+H2 merged (M/E level with planned contrasts); H3+H10 merged (two-stage pipelines, both directions); H6+H11 merged into exploratory H9 (diversity mechanisms with 5 conditions); old H7 simplified to 3 levels (now H5, removed Text-only condition); old H9 reduced to 4 temperatures (now H7, removed T=0.3); old H5 updated with directional prediction (now H4); new H13 added (overlap/stride); text-only modalities tested at T=1.0 only; exploratory hypotheses organised into Tiers A/B/C; Section 12 added (Future Directions for Paper 2); budget reduced from ~$90 to ~$49 base
- v3.6: Terminology consistency corrections — H7 library table updated to use Canon+/Canon-/HP/Emp-HN columns with corrected totals (13/13/16/16); Canon- always included note added; H15 implementation status updated to confirmatory; H5 test type corrected to Factorial ANOVA; Section 8.4.2 library composition table expanded to 5 categories with abbreviation column; Section 8.4.3 Canon- section added
- v3.5: Major factorial restructure separating text elaboration from library content — H2 redefined as 3 detail levels (Minimal/Brief/Verbose) with HP edge cases in both brief and verbose at different detail levels; stranded design (Strand 1: 50 cells for verbosity × partial H7; H7 Confirmatory: 20 cells full 2×2 at optimal M/E; Strand 2: 30 cells for H15 library size with 6 conditions); H15 promoted to confirmatory with Pure/Canonical/A-D library conditions using 1:1 HP:Emp-HN ratio and Canon+/Canon-/HP/Emp-HN terminology; H17 added as exploratory ratio hypothesis; H3/H6/H8 moved to exploratory; confirmatory count reduced to 7 (H1, H2, H4, H5, H7, H9, H15); M/E factor remains 5 levels (Image-only uses minimal text, no separate level); H7 constraint documented (Pure/Canonical run at H7=None); Section 8.4.1 updated (brief includes terse HP guidance, verbose includes detailed HP guidance); Section 8.4.7 rewritten for stranded design; Section 8.7.4 updated for stranded coverage
- v3.4: Final review fixes — H2/H7 orthogonality clarification (exclusion guidance controlled by H7 only); config naming corrected (temperature is runtime parameter, 16 configs not 20 due to text-only constraints); H3 factor list corrected; temperature "required" → "recommended"; Section 8.3.3/8.3.4 factor references fixed; typos corrected; terminology standardised (elaborate → verbose)
- v3.3: Exploratory hypotheses H10-H16 comprehensive rewrite with detailed test designs; fixed H11 implementation table description ("prompts" → "passes"); markdown linting (asterisk lists → dashes throughout)
- v3.2: Major factorial design update — revised to 100-condition design (5 M/E × 4 H7 × 5 T levels); added Section 3.8 K=10 Evaluation Protocol; updated H1 to 5-level M/E factor; H2 now contrasts within factorial; H4 integrated with K=10 runs; H5 partial cross design (3 × 3) with p < 0.10 mitigation; H9 extended to 5 temperatures with escalation trigger; H7 alignment clarification (text describes same failures as images); Section 1.3 text-only role clarification; Section 8.4.1 library and verbose text construction procedure with alignment requirements; updated Section 8.4.7 and Section 8.7.4 for 100-condition factorial
- v3.1: Comprehensive review updates — fixed errors (hypothesis count, H1 prediction, H10→H12 reference, ordering terminology, escaped characters, E7→H16); added new sections (power analysis, blinding, analysis scope, Lesovo terrain, spatial tolerance sensitivity, model version documentation, Stage 2 expansion); updated hypothesis descriptions (H3 stopping rule, H4 primary/exploratory clarification, H6 symmetric replication, H8 transfer approach); added administrative sections (COI, ethics, registration, data availability); added H10-H16 to implementation table; created companion documents (preregistration-coverage.md for factorial coverage, preregistration-appendix-prompts.md for complete prompt documentation); added Section 16.1 Companion Documents reference table
- v3.0: Added Section 8.7 hypothesis-to-implementation mapping; status set to Ready for Registration
- v2.11: Section 8.3 prompt variants documentation; H6 text diversity methodology with example variants; runtime parameters specification
- v2.10: Section 8.4.7 pairwise interaction testing methodology; text-image ordering constraint; escalation triggers for 3-way interactions
- v2.9: H4 full grid search specification (N ∈ {5, 10, 30}); Sections 8.4.1-8.4.5 (library composition, cross-pass sampling methodology, example-level effectiveness analysis, hypothesis interactions); Section 8.2 cross-model comparability and cost-performance analysis; H8 adaptive testing framework with trigger conditions
- v2.8: De-duplicated document; consolidated tile selection methodology references; removed redundant spatial tolerance text
- v2.7: Added voting implementation algorithm (8.5), tile selection methodology (8.6), tile exclusion criteria, updated detection matching to Hungarian algorithm (4.1.2)
- v2.6: Fixed section numbering, added detection matching algorithm (4.1.2), corrected summary table, integrated answers, added timeline
- v2.5: Added API parameters, null tile selection, preliminary findings
- v2.0: Merged hypotheses document; added two-stage trial framework, FDR rationale, tile-level MCC, H5-H10, implementation priority, checklist  
