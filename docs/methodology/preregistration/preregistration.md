# Preregistration: VLM-Based Burial Mound Detection

**Title**: Extracting geospatial datasets from historical maps using frontier vision-language models: Evaluating prompting strategies for cartographic symbol detection

**Authors**: Shawn Ross(1), Adela Sobotkova(2), Brian Ballsun-Stanton(1)

**Affiliations**: (1) Macquarie University, Sydney, Australia; (2) Aarhus University, Denmark

**Document version**: 3.0
**Last updated**: 2026-01-01
**Status**: Ready for Registration

---

## 1\. Study Overview

### 1.1 Background

This study evaluates prompting strategies for vision-language model (VLM) based detection of burial mound symbols from Soviet 1:50,000 topographic maps. It builds on Sobotkova et al. (2023), which used participatory GIS for the same extraction task.

During preliminary development, we discovered that several "best practice" prompting strategies derived from the VLM literature did not transfer to this task:

1. **Text minimization had little effect**: Contrary to text-image interference literature (Vo et al., 2025), removing text from prompts didn't improve performance.  
2. **Two-stage proposer-verifier was actively harmful**: This architecture degraded performance rather than improving precision-recall tradeoffs.  
3. **Consensus voting worked well**: n-of-x voting schemes substantially improved F1.

These findings suggest that prompting strategies derived from general VLM benchmarks may not generalise to specialised detection tasks on frontier models', a finding with implications for practitioners.

### 1.2 Research Questions

1. Does text content affect VLM detection performance on novel domain tasks, as opposed to image-only prompting?  
2. Do two-stage proposer-verifier pipelines improve precision-recall tradeoffs for VLM detection?  
3. What voting and ensemble strategies optimize detection F1, precision, and recall?  
4. Do these effects generalise across frontier VLM providers (Gemini, Claude, GPT)?

### 1.3 Two-Stage Trial Framework

This study adopts a **two-stage trial framework** using a 361-tile corpus representing four manually annotated Soviet-era topographic map sheets from Bulgaria (Thracian Plain and surrounding areas).

**Stage 1 (current work)**: Identify promising techniques using modest training (20 tiles) and holdout sets (20 tiles). Given limited statistical power, the goal is to screen for techniques that show directional improvement and warrant further investigation. False Discovery Rate (FDR) correction is used to balance discovery against false positives.

**Stage 2 (future work)**: Techniques that show promise in Stage 1 will be validated on a larger holdout set (additional tiles from the 361-tile corpus or transfer testing on out-of-sample maps) with more stringent significance thresholds.

This framing acknowledges the power limitations of small-sample evaluation while maintaining scientific rigor through preregistration and appropriate multiple comparison correction.

### 1.4 Timeline

**Anticipated data collection**: 30 December 2025 - 31 January 2026

---

## 2\. Data Resources

### 2.1 Map Tile Corpus

| Dataset | Tiles | Purpose | Status |
| :---- | :---- | :---- | :---- |
| Development set (‘training tiles’) | 20 | Prompt engineering, iteration | Used \- contaminated |
| Exploratory test set(‘holdout tiles’) | 20 | Generalization checks (no feedback to prompts) | Used for evaluation only |
| Reserve set | 321 | Confirmatory testing | **Untouched** |

**Total**: 361 tiles from 4 annotated Soviet topographic map sheets. Maps were hand-annotated by students with comprehensive expert review.

**Note**: The 20 exploratory test tiles were used ONLY for final generalisation checks on prompts, with NO feedback into prompt development.

### 2.2 Selection Methodology

See Section 8.6 for full methodology. Key parameters:

| Parameter | Value |
| :--- | :--- |
| Selection date | 2025-12-23 |
| Random seed | 1766464625 |
| Samples per map | 5 |
| Content threshold | ≤75% background |
| Spatial separation | Not adjacent to training |
| Tile size | 448×448 pixels |

### 2.3 Training Tiles (n=20)

Tiles used for prompt development and few-shot examples.

#### K-35-052-4\_32635 (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-052-4\_32635\_x1344\_y2240.png | 2 | sparse |
| K-35-052-4\_32635\_x1792\_y3136.png | 1 | sparse |
| K-35-052-4\_32635\_x3136\_y3584.png | 0 | empty |
| K-35-052-4\_32635\_x3584\_y3584.png | 3 | dense |
| K-35-052-4\_32635\_x896\_y1792.png | 0 | empty |

#### K-35-053-3\_Elenovo (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-053-3\_Elenovo\_x1792\_y1792.png | 3 | dense |
| K-35-053-3\_Elenovo\_x1792\_y896.png | 1 | sparse |
| K-35-053-3\_Elenovo\_x3136\_y2688.png | 3 | dense |
| K-35-053-3\_Elenovo\_x3136\_y3584.png | 2 | sparse |
| K-35-053-3\_Elenovo\_x3584\_y1344.png | 0 | empty |

#### K-35-062-2\_Rakovski (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-062-2\_Rakovski\_x1344\_y1792.png | 2 | sparse |
| K-35-062-2\_Rakovski\_x1792\_y2688.png | 0 | empty |
| K-35-062-2\_Rakovski\_x1792\_y896.png | 3 | dense |
| K-35-062-2\_Rakovski\_x3136\_y1792.png | 2 | sparse |
| K-35-062-2\_Rakovski\_x448\_y2688.png | 3 | dense |

#### K-35-078-1\_Lesovo (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-078-1\_Lesovo\_x1344\_y0.png | 2 | sparse |
| K-35-078-1\_Lesovo\_x1344\_y3136.png | 0 | empty |
| K-35-078-1\_Lesovo\_x2240\_y2688.png | 0 | empty |
| K-35-078-1\_Lesovo\_x2688\_y1344.png | 0 | empty |
| K-35-078-1\_Lesovo\_x448\_y0.png | 0 | empty |

**Training set summary**: 20 tiles, 22 mounds total

---

### 2.4 Holdout Tiles (n=20)

Tiles reserved for final evaluation. Spatially separated from training tiles.

#### K-35-052-4\_32635 (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-052-4\_32635\_x0\_y2688.png | 4 | dense |
| K-35-052-4\_32635\_x1792\_y1344.png | 2 | sparse |
| K-35-052-4\_32635\_x3584\_y0.png | 0 | empty |
| K-35-052-4\_32635\_x3584\_y2240.png | 1 | sparse |
| K-35-052-4\_32635\_x448\_y896.png | 0 | empty |

#### K-35-053-3\_Elenovo (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-053-3\_Elenovo\_x2688\_y1344.png | 0 | empty |
| K-35-053-3\_Elenovo\_x2688\_y896.png | 1 | sparse |
| K-35-053-3\_Elenovo\_x448\_y1792.png | 1 | sparse |
| K-35-053-3\_Elenovo\_x896\_y0.png | 4 | dense |
| K-35-053-3\_Elenovo\_x896\_y2240.png | 3 | dense |

#### K-35-062-2\_Rakovski (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-062-2\_Rakovski\_x3584\_y0.png | 0 | empty |
| K-35-062-2\_Rakovski\_x4032\_y0.png | 2 | sparse |
| K-35-062-2\_Rakovski\_x4032\_y1344.png | 3 | dense |
| K-35-062-2\_Rakovski\_x448\_y1792.png | 2 | sparse |
| K-35-062-2\_Rakovski\_x448\_y448.png | 3 | dense |

#### K-35-078-1\_Lesovo (5 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-078-1\_Lesovo\_x1792\_y1792.png | 0 | empty |
| K-35-078-1\_Lesovo\_x2688\_y448.png | 2 | sparse |
| K-35-078-1\_Lesovo\_x3136\_y3136.png | 0 | empty |
| K-35-078-1\_Lesovo\_x3584\_y448.png | 0 | empty |
| K-35-078-1\_Lesovo\_x896\_y896.png | 0 | empty |

**Holdout set summary**: 20 tiles, 28 mounds total

---

### 2.5 Density Distribution

Tiles were stratified by mound density (see Section 8.6 for category definitions):

| Density | Training | Holdout |
| :---- | :---- | :---- |
| Empty (0 mounds) | 8 | 8 |
| Sparse (1-2 mounds) | 7 | 7 |
| Dense (3+ mounds) | 5 | 5 |

### 2.6 Map Annotation

Soviet-era maps were initially annotated by students using the FAIMS v2.6 mobile data capture application (customised as a participatory GIS). Annotation consisted of identifying all symbols representing:

* Burial mounds  
* Burial mounds with benchmarks  
* Burial mounds with triangulation points  
* Benchmarks (no burial mound)  
* Triangulation points (no burial mound)

These four tiles were later selected for the quality assessment of student work as reported in Sobotkova et al., 2023\. To that end, the author (Shawn Ross) manually assessed these tiles to ensure complete extraction and accuracy, with results then compared to the student work (which also served as a check against missed symbols). 

---

## 3\. Statistical Analysis Plan

### 3.1 Significance Testing

* **Per-hypothesis α**: 0.05  
* **Direction**: One-tailed for directional predictions; two-tailed for equivalence tests (H1)  
* **Multiple comparison correction**: Benjamini-Hochberg FDR at q \= 0.05 across confirmatory hypotheses

### 3.2 Rationale for FDR

With 6 confirmatory hypotheses tested on 20 tiles (28 mound symbols), statistical power is limited. Bonferroni correction (α \= 0.008) would be overly conservative for a screening study. FDR controls the expected proportion of false discoveries among rejected hypotheses, which is appropriate when:

* The goal is identifying promising techniques for further validation  
* Some false positives are acceptable if balanced by discovery of true effects  
* Sample size limits power for detecting moderate effects

### 3.3 Interpretation Guidelines

* **Statistically significant (FDR-corrected p \< 0.05)**: Technique shows promise; advance to Stage 2 validation  
* **Nominally significant (uncorrected p \< 0.05, FDR-corrected p ≥ 0.05)**: Suggestive evidence; consider for Stage 2 with lower priority  
* **Non-significant (uncorrected p ≥ 0.05)**: No evidence of benefit; do not advance unless strong theoretical rationale

### 3.4 Practical Significance Caveat

Results will be interpreted in light of practical significance. A statistically significant but trivially small improvement (e.g., F1 \+0.01) will be reported but not treated as actionable. Techniques advanced to Stage 2 should show both statistical significance and a meaningful effect direction.

### 3.5 Reporting

* All preregistered analyses reported regardless of outcome  
* Report both uncorrected and FDR-corrected p-values  
* Report effect sizes (F1 difference, precision difference, recall difference) with 95% bootstrapped CIs  
* Exploratory analyses clearly labelled and interpreted cautiously

---

## 4\. Outcome Measures

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

* Georeferencing imprecision in historical maps  
* Symbol centroid ambiguity (mound symbols can be 10-20m across at 1:50,000 scale)  
* Ground truth digitisation variation

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

MCC is preferred over accuracy given class imbalance in the holdout set (8 empty tiles, 12 non-empty tiles). MCC ranges from \-1 (perfect inverse classification) through 0 (random) to \+1 (perfect classification), and appropriately penalises both false positives and false negatives.

**Rationale**: A method that simply predicts "mounds present" for every tile would achieve \~60% accuracy but MCC ≈ 0\. Tile-level MCC directly addresses the practical question: "Can this method correctly identify when there is nothing to find?"

We also report tile-level sensitivity (P(detect ≥1 | tile has mounds)) and specificity (P(detect 0 | tile is empty)) for interpretability.

---

## 5\. Confirmatory Hypotheses

### H1: Text Modality Has No Significant Effect

**Background**: The text-image interference literature (Vo et al., 2025\) found VLMs override visual analysis with textual priors. This effect, however, applies to domains where VLMs have strong priors (e.g., "Adidas logos have 3 stripes"). Burial mound symbols are novel domain content with no conflicting prior knowledge.

**Prediction**: Image+text prompts will perform as well as text-only prompts.

**Test**: Compare detection performance with:

- Condition A: Few-shot image library examples only (no text descriptions)  
- Condition B: Few-shot examples \+ text descriptions of symbol characteristics

H1, H2, and H7 will be coordinated to isolate effects of modality vs. elaboration vs. hard negatives.

**Analysis**: Two-tailed test for difference; equivalence supported if 95% CI for F1 difference includes zero and excludes practically significant effects (±0.05).

**Advance to Stage 2 if**: Significant difference detected (suggesting the addition of text *does* matter for this domain, contrary to preliminary findings).

---

### H2: Text Elaboration Does Not Improve Performance

**Background**: Adding lengthy descriptive text instructions does not appear to improve recall over brief text instructions.

**Prediction**: Detailed text instructions will not improve F1 compared to minimal instructions.

**Test**: Compare detection performance with:

* Condition A: Minimal text ("Detect burial mound symbols")
* Condition B: Elaborate text (detailed criteria, explicit inclusion/exclusion rules)

**Analysis**: One-tailed test; H0: elaborate ≤ minimal; H1: elaborate \> minimal. Prediction is that H0 will not be rejected (elaborate does not help).

**Advance to Stage 2 if**: Elaborate text shows significant improvement (would contradict preliminary findings and warrant investigation).

---

### H3: Coarse-to-Fine Two-Stage Pipeline Degrades Performance

**Background**: Two-stage pipelines are recommended in general ML but lack VLM-specific evidence. Preliminary testing found coarse-to-fine (proposer-verifier) degraded performance, likely due to context loss when cropping candidate regions.

**Prediction**: Two-stage coarse-to-fine (proposer-verifier) detection will produce lower F1 than single-stage detection.

**Test**: Compare detection performance with:

* Condition A: Single-stage detection (baseline prompt)  
* Condition B: Two-stage proposer-verifier pipeline (liberal proposer → strict verifier)

**Analysis**: One-tailed test; H0: two-stage ≥ single-stage; H1: two-stage \< single-stage. Prediction is that H0 will be rejected (two-stage performs worse).

**Advance to Stage 2 if**: Two-stage shows equivalent or superior performance (would contradict preliminary findings and suggest the architecture merits further optimisation).

---

### H4: Consensus Voting Improves F1

**Background**: Consensus voting addresses stochastic variation in VLM outputs. Preliminary testing confirmed substantial improvements with 2-of-5, 4-of-10, and 10-of-30 configurations, including for weaker models (e.g., Gemini 3 Flash as well as Gemini 3 Pro).

**Prediction**: Consensus voting (x-of-N) will improve F1 compared to single-pass detection.

**Test**: Full grid search across pool sizes and vote thresholds:

* Condition A: Single-pass detection (N=1, baseline)
* Condition B: N-pass voting with threshold T, for all combinations:
  - N ∈ {5, 10, 30}
  - T ∈ {1, 2, ..., N} for each N

**Model coverage**:

* Full grid (all N × T combinations): Gemini 3 Flash (cost-efficient exploration)
* Representative subset: Claude and GPT models (validate key findings transfer)

**Analysis**: One-tailed test; H0: voting ≤ single-pass; H1: voting > single-pass. Primary comparison uses optimal (N, T) from Flash grid search.

**Secondary analyses**:

* Precision-recall tradeoff curves for each N
* Visualise F1, precision, and recall as functions of threshold for each N
* Cost-efficiency analysis: F1 improvement per additional pass
* Identify diminishing returns point (where additional passes yield marginal gains)
* Cross-model consistency: Do optimal thresholds transfer across providers?

**Advance to Stage 2 if**: Significant improvement confirmed. Optimize voting parameters (N, threshold) in Stage 2\.

---

### H5: Example Ordering Affects Performance (Canonical Placement)

**Background**: VLMs exhibit documented recency bias where attention heads prioritize the final demonstration example. UniBias research found models replicate the last demonstration's response pattern 12% of the time regardless of shot count. However, prototype theory suggests establishing canonical forms before presenting edge cases may improve schema formation.

**Prediction**: The relative placement of canonical examples (clear legend symbols) versus hard examples (difficult positives/negatives identified during library construction) will affect detection performance.

**Test**: Compare detection performance across three conditions:

* Condition A: Canonical-first — Legend entries in initial positions, followed by hard examples  
* Condition B: Canonical-last — Hard examples in initial positions, legend entries in final positions  
* Condition C: Random ordering (average of 3 random permutations with documented seeds)

**Analysis**:

* Primary: One-tailed test comparing Condition A (canonical-first) vs Condition C (random)  
* Secondary: One-tailed test comparing Condition B (canonical-last) vs Condition C (random)  
* Exploratory: Direct comparison of Condition A vs Condition B

**Implementation**: Canonical examples are legend-derived symbols (burial mound, settlement mound, triangulation on mound, benchmark on mound). Hard examples are selected via the procedure in Section 2.2 (frequent false positives/negatives from training tile evaluation). Within each block (canonical or hard), internal ordering is randomized with documented seed.

**Advance to Stage 2 if**: Either canonical-first or canonical-last significantly outperforms random. Would establish example ordering as a low-cost optimization strategy.

---

### H6: Prompt and Example Diversity Improves Consensus Voting

**Background**: Voting with identical prompts and examples may produce correlated errors. Two mechanisms could improve ensemble diversity: (1) semantically equivalent but differently phrased prompts produce more independent error patterns; (2) varying the hard examples shown across passes exposes different failure modes to correction. These mechanisms may be additive or interactive.

**Prediction**: Consensus voting with varied prompts and/or varied example images will improve F1 compared to voting with fully identical passes.

**Test**: 2×2 factorial design comparing:

| Condition | Text | Images | Description |
| ----- | ----- | ----- | ----- |
| A | Fixed | Fixed | Baseline: identical prompt and examples across all 5 passes |
| B | Varied | Fixed | Text diversity: 5 prompt variants, same examples |
| C | Fixed | Varied | Image diversity: same prompt, examples resampled each pass |
| D | Varied | Varied | Full diversity: both mechanisms combined |

**Text variants** (semantically equivalent task instructions):

1. "Identify burial mound symbols in this map section"  
2. "Detect tumuli markers on this topographic map"  
3. "Find kurgan indicators in this image"  
4. "Locate ancient burial mound cartographic symbols"  
5. "Mark all mound features shown on this Soviet map"

**Image diversity implementation**:

* Pool construction: All false negatives (≥1 occurrence) and all false positives (≥1 occurrence) during training tile evaluation (per Section 2.2 procedure)
* Hard example count: K hard positives and M hard negatives per pass, where K and M are set based on pool size (preregistered once pool is constructed; target K=4, M=3 if pool allows)
* Fixed conditions (A, B): Sample K hard positives and M hard negatives once from pool; use same selection for all 5 passes
* Varied conditions (C, D): Resample hard examples for each pass using frequency-capped random sampling (see Section 8.4.3 for methodology)
* Canonical examples (legend-derived symbols) and null tiles remain fixed across all conditions and passes
* Condition A runs: To control for specific image selection effects, Condition A is run 5 times with different randomly-sampled fixed libraries (documented seeds); results averaged across runs

**Cross-reference**: Full sampling methodology, constraints, and example-level analysis framework documented in Sections 8.4.3–8.4.4.

**Analysis**:

* Primary: 2×2 factorial ANOVA testing main effects (text diversity, image diversity) and interaction  
* Secondary: Planned contrasts comparing each diversity condition (B, C, D) against baseline (A, averaged across runs)  
* Effect sizes reported for each factor

**Advance to Stage 2 if**: Either main effect is significant, OR the interaction is significant (indicating combined diversity outperforms either alone). Would establish diversity mechanisms as refinements to consensus voting.

---

### H7: Hard Negative Examples Improve Precision

**Background**: Hard negative mining is established in few-shot learning. Two mechanisms could improve precision: (1) explicit text instructions describing what to exclude; (2) visual counter-examples showing confusable symbols. These may operate independently or synergistically — text provides semantic guidance while images provide perceptual anchors for decision boundaries.

**Prediction**: Including hard negative information (text and/or images) will improve precision without significantly harming recall.

**Test**: 2×2 factorial design comparing:

| Condition | Exclusion Text | Hard Neg Images | Description |
| ----- | ----- | ----- | ----- |
| A | No | No | Baseline: positive examples only, no exclusion guidance |
| B | Yes | No | Text-only: explicit exclusion instructions, no visual counter-examples |
| C | No | Yes | Image-only: hard negative images with minimal labels ("Negative") |
| D | Yes | Yes | Combined: hard negative images with explicit explanatory labels |

**Hard negative image sources**:

1. **Legend-derived negatives**: Visually confusable symbols that lack burial mound characteristics. Confirmed: benchmark (standalone), triangulation point (standalone). Additional symbols will be documented if full Soviet topographic map legend is acquired prior to holdout evaluation.  
2. **Procedure-derived negatives**: False positives with ≥1 occurrence during training tile evaluation (per Section 2.2).

**Text implementation**:

* Condition A, C: No exclusion guidance in prompt  
* Condition B: Explicit exclusion instructions without visual examples: "Do NOT mark: benchmarks without radiating rays, isolated triangulation points, or other circular symbols lacking the characteristic mound rays."  
* Condition D: Same exclusion instructions, plus explanatory labels on hard negative images

**Image label implementation**:

* Condition C: Minimal labels only ("Negative" or "Negative: Not a mound")  
* Condition D: Labels with distinguishing features (e.g., "Negative: Benchmark ALONE — triangular symbol without radiating rays. NOT a mound.")

**Analysis**:

* Primary: 2×2 factorial ANOVA testing main effects (exclusion text, hard negative images) and interaction on precision  
* Secondary: Parallel analysis on recall to confirm no significant harm  
* Tertiary: Analysis on F1 to assess net benefit

**Advance to Stage 2 if**: Either main effect significantly improves precision AND recall does not significantly decrease. Would establish whether hard negative guidance works through text, images, or both.

---

### H8: Optimizations Transfer from Gemini 3 Flash to Pro

**Background**: Development and optimization is conducted on Gemini 3 Flash for cost efficiency. For this approach to be valid, effects observed on Flash must replicate on Pro. This hypothesis uses an adaptive testing framework: primary analysis tests boundary conditions efficiently, with pre-specified triggers for more comprehensive secondary analysis if interactions are detected.

**Prediction**: Significant effects identified in H4–H7 on Gemini 3 Flash will replicate directionally on Gemini 3 Pro, with no significant condition × model interactions.

#### Primary Analysis: Factorial Corners

Test boundary conditions for each hypothesis on Pro (~14 conditions total):

| Hypothesis | Conditions Tested on Pro | Purpose |
| :--- | :--- | :--- |
| H4 (voting) | Single-pass; Flash-optimal (e.g., 3-of-5); Unanimity (5-of-5) | Transfer + directional check |
| H5 (ordering) | Random; Canonical-first; Canonical-last | Full comparison (3 conditions) |
| H6 (diversity) | Full 2×2 factorial (A, B, C, D) | Interaction detection |
| H7 (hard negatives) | Full 2×2 factorial (A, B, C, D) | Interaction detection |

**Analysis**:

* For each hypothesis, test whether the same directional effect appears on Pro
* Test for condition × model interaction using 2×2 ANOVA (condition × model)
* Report both absolute performance and relative effect sizes

#### Trigger Conditions for Secondary Analysis

Escalate to more comprehensive testing if **any** of the following conditions are met:

| Trigger | Definition | Threshold |
| :--- | :--- | :--- |
| Effect reversal | Pro effect is opposite direction to Flash | Sign change in effect |
| Significant interaction | Condition × model interaction | p < 0.10 |
| Large attenuation | Pro effect size substantially smaller than Flash | Cohen's d ratio < 0.50 |
| Rank reversal | Ordering of conditions differs between Flash and Pro | Best condition differs |

#### Secondary Analysis: Targeted Expansion (If Triggered)

**H4 (voting) — Bracketing procedure:**

If Flash optimal = X-of-N and trigger conditions are met:

1. **Bracket**: Test (X−1)-of-N and (X+1)-of-N on Pro
2. **Monotonicity check**: If bracket shows monotonic trend (e.g., higher thresholds consistently better), run full threshold sweep for that N
3. **Scale check**: If N=5 optimal differs from Flash, test same threshold ratio at N=10 to determine if pattern generalises

```
Example decision tree for H4:

PRIMARY: Test single-pass, 3-of-5, 5-of-5 on Pro
    │
    ├─► Same rank order as Flash (3-of-5 best)
    │   └─► STOP: Threshold transfers ✓
    │
    ├─► 5-of-5 > 3-of-5 (Pro prefers stricter)
    │   └─► SECONDARY: Test 4-of-5
    │       ├─► 4-of-5 best → Report Pro optimal = 4-of-5
    │       └─► 5-of-5 still best → Consider 5-of-10 scaling check
    │
    ├─► 3-of-5 ≈ 5-of-5 (no clear preference)
    │   └─► SECONDARY: Run full sweep 1-of-5 through 5-of-5
    │
    └─► Single-pass > voting (voting hurts Pro)
        └─► SECONDARY: Full investigation required
```

**H5 (ordering) — Already comprehensive:**

Primary analysis tests all 3 conditions. If interaction detected, increase replicates for pairwise power.

**H6/H7 (diversity/hard negatives) — Already factorial:**

Primary analysis runs full 2×2. If interaction detected:
- Report which cell(s) drive the interaction
- Test whether Pro requires different combination than Flash
- Increase replicates if effect sizes are small but directionally interesting

#### Tertiary Analysis: Full Replication (If Required)

If secondary analysis reveals complex or multiple interactions (≥2 hypotheses show non-transferability), escalate to full experimental replication on Pro:

> "Due to significant Flash-Pro interactions detected in secondary analysis, full experimental replication was conducted on Pro to establish Pro-specific optimal configuration."

This would include:
- Full H4 grid search (N ∈ {5, 10, 30}, all thresholds)
- All H5, H6, H7 conditions with increased replication

**Cost justification**: Tertiary analysis is only triggered when primary and secondary analyses provide evidence that Pro behaves fundamentally differently from Flash, warranting the additional investment.

#### Success Criteria

| Outcome | Interpretation | Action |
| :--- | :--- | :--- |
| ≥80% effects replicate, no triggers | Flash optimisations transfer to Pro | Report unified recommendations |
| 1 trigger activated, resolved in secondary | Minor model-specific adjustment needed | Report Flash-optimal + Pro adjustment |
| Multiple triggers, tertiary required | Models require separate optimisation | Report model-specific recommendations |

**Advance to Stage 2 if**: Primary analysis shows ≥80% of significant effects replicate directionally without triggering secondary analysis. If triggers are activated, advance after secondary/tertiary analysis resolves the model-specific configuration.

---

### H9: Temperature Effects on Detection Performance

**Background**: Google documentation recommends temperature=1.0 for Gemini 3, warning that values \<1.0 cause "looping or degraded performance." However, lower temperatures conventionally reduce output variance, which may benefit structured detection tasks. This recommendation has not been validated for cartographic symbol detection.

**Prediction**: Temperature=1.0 will perform at least as well as lower temperature settings on Gemini 3 Flash.

**Test**: Compare detection performance across temperature conditions on Gemini 3 Flash (thinking\_level: high):

| Condition | Temperature |
| ----- | ----- |
| A | 0.0 |
| B | 0.3 |
| C | 0.7 |
| D | 1.0 (recommended) |

**Analysis**:

* Primary: One-way ANOVA across temperature conditions  
* Secondary: Planned contrasts comparing each lower temperature against 1.0  
* Monitor for looping/degenerate outputs as qualitative check on Google's warning

**Advance to Stage 2 if**: Any temperature significantly outperforms 1.0, OR if 1.0 confirms as optimal. Either outcome informs parameter selection.

---

## 6\. Exploratory Hypotheses

*These analyses will be conducted and reported but are not confirmatory. Results will be interpreted cautiously and framed as hypothesis-generating. Not included in FDR correction.*

### H10: Fine-to-Coarse Validation Improves Uncertain Detections

**Background**: Coarse-to-fine (H3) failed because cropping removed context. Fine-to-coarse is the inverse: run detection at full resolution first, then re-query uncertain cases with *expanded* context to aid disambiguation.

**Prediction**: For detections with low consensus agreement, re-querying with expanded spatial context will improve classification accuracy compared to accepting/rejecting at a fixed threshold.

**Test**: Compare:

- Condition A: Single-stage detection with fixed 50% consensus threshold  
- Condition B: Single-stage detection \+ context-expanded re-query for 40-60% consensus cases

**Analysis**: Compare F1 on the subset of "uncertain" detections; report computational cost.

**Implementation**:

- Stage 1: Standard detection on original tiles  
- Stage 2: For candidates with 2/5 or 3/5 agreement, generate expanded context crop (2x area) and re-query

**Status**: Exploratory. Novel approach; uncertain whether context expansion helps or introduces new confounders.

---

### H11: Temperature Variation Improves Ensemble Diversity

**Background**: Fixed temperature across voting passes may produce correlated errors. Varying temperature should increase sample diversity.

**Prediction**: Voting with varied temperatures across passes will improve F1 compared to voting with fixed temperature.

**Test**: Compare:

- Condition A: 5-pass voting at T=1.0 (Gemini default)  
- Condition B: 5-pass voting at T=\[0.7, 0.8, 0.9, 1.0, 1.0\]

**Analysis**: Paired comparison; report interaction with H6 (prompt diversity) if both are tested.

**Status**: Exploratory. Effect size likely small; may be confounded with prompt diversity effects.

---

### H12: Cross-Model Consistency

**Background**: Results obtained on Gemini 3 may not generalize to other VLMs. Testing across Claude and GPT-5.2 validates that findings reflect task properties rather than model-specific behaviors.

**Prediction**: Relative ordering of conditions (e.g., voting \> single-pass; hard negatives improve precision) will be consistent across different models, e.g., Gemini, Claude, and GPT-5.2, even if absolute F1 differs.

**Test**: Replicate primary confirmatory tests (H4, H5, H7) on Claude and GPT-5.2 models as per Section 8.1.

**Analysis**:

- Report absolute F1 per model  
- Qualitative assessment of whether significant effects replicate  
- Test for condition × model interaction if sample size permits

**Status**: Exploratory but important for generalizability claims.

---

### H13: Cross-Model Consensus Voting

**Background**: Within-model consensus voting (H4) improves performance by averaging across passes. However, passes from the same model may share systematic biases. Voting across architecturally different models may provide more independent error patterns.

**Question**: Does cross-model voting outperform within-model voting at equivalent total passes?

**Test**: Compare voting strategies at N=6 total passes:

| Condition | Composition | Description |
| ----- | ----- | ----- |
| A | 6× Flash | Within-model baseline (Gemini 3 Flash) |
| B | 6× Sonnet | Within-model baseline (Claude 4.5 Sonnet) |
| C | 6× Thinking | Within-model baseline (GPT-5.2 Thinking, medium) |
| D | 2× Flash \+ 2× Sonnet \+ 2× Thinking | Cross-model ensemble |

**Implementation considerations**:

* Output format standardized across models (coordinate lists)  
* Spatial matching applied uniformly  
* Equal weighting (each pass \= 1 vote, threshold \= 4/6)  
* Cost tracked per condition for efficiency analysis

**Analysis**:

* Compare F1 across conditions  
* Analyze error correlation: do different models make different mistakes?  
* Cost-adjusted comparison: F1 per dollar

**Exploratory extensions**:

* Weighted voting by model confidence (if parseable)  
* Weighted voting by model-specific precision/recall profiles  
* Optimal ensemble composition search

---

### H14: Training Pool Size Effects on Library Quality

**Background**: Few-shot library construction (Section 2.2) identifies hard examples from training tile evaluation. A larger training pool may surface more diverse or representative hard examples, improving the resulting library's effectiveness.

**Question**: How does training pool size affect detection performance on held-out tiles?

**Test**: Construct few-shot libraries from progressively larger training pools:

| Condition | Training Tiles | Holdout Tiles | Notes |
| ----- | ----- | ----- | ----- |
| A | 20 | 20 | Current design |
| B | 40 | 20 | 2× training |
| C | 80 | 20 | 4× training |
| D | 160 | 20 | 8× training |

**Implementation**:

* Training pools are nested (A ⊂ B ⊂ C ⊂ D) for comparability  
* Same holdout set across all conditions  
* Library construction procedure (Section 2.2) applied identically to each pool  
* Document resulting library composition for each condition

**Analysis**:

* F1 on holdout as function of training pool size  
* Characterize diminishing returns curve  
* Compare library composition across conditions (do larger pools find different hard examples?)

**Constraints**:

* Total tiles available: 361  
* Holdout fixed at 20 tiles  
* Maximum training pool: \~340 tiles

---

### H15: Few-Shot Library Size Effects

**Background**: Larger few-shot libraries provide more examples for pattern matching but increase token cost and may introduce inconsistency. The optimal library size for cartographic symbol detection is unknown.

**Question**: How does few-shot library size affect detection performance and cost efficiency?

**Test**: Compare library sizes holding training pool constant:

| Condition | Positives | Hard Positives | Hard Negatives | Null Tiles | Total |
| ----- | ----- | ----- | ----- | ----- | ----- |
| A | 4 (legend) | 2 | 2 | 2 | 10 |
| B | 4 (legend) | 4 | 3 | 3 | 14 |
| C | 4 (legend) | 8 | 6 | 4 | 22 |
| D | 4 (legend) | 16 | 12 | 6 | 38 |

**Implementation**:

* Legend-derived positives fixed across conditions (canonical examples)  
* Hard examples drawn from pool; larger libraries sample more deeply  
* Requires sufficient training pool to source hard examples (pair with E5 Condition C or D)  
* Document which hard examples are added at each tier

**Analysis**:

* F1 as function of library size  
* Token cost as function of library size  
* F1 per dollar (cost-efficiency frontier)  
* Qualitative assessment: does adding examples introduce inconsistency?

---

### **E7: Tile Size Effects on Detection Performance**

**Background**: Larger tiles reduce API calls required for full map coverage but increase symbols per tile and decrease symbol-to-image ratio. VLM attention to small features may degrade as tile size increases.

**Question**: How does tile size affect detection performance and operational efficiency?

**Test**: Compare detection performance across tile sizes (conditional advancement):

| Condition | Tile Size | Area Multiplier | Est. Symbols/Tile |
| ----- | ----- | ----- | ----- |
| A (baseline) | 448×448 | 1× | 0-3 |
| B | 896×896 | 4× | 0-12 |
| C (conditional) | 1792×1792 | 16× | 0-48 |

**Conditional advancement**: Condition C tested only if Condition B achieves F1 within 0.05 of baseline.

**Analysis**:

* F1 as function of tile size  
* Efficiency metric: F1 × coverage rate (symbols evaluated per API call)  
* Qualitative assessment: Are errors concentrated on small/crowded symbols?

**Implementation notes**:

* Tiles generated from same source maps with consistent overlap handling  
* Few-shot library images remain at original resolution (448×448 crops)  
* Ground truth regenerated for larger tile boundaries

---

## 7\. Summary Table

### 7.1 Confirmatory Hypotheses

| Hypothesis | Prediction | Test Type | Advance to Stage 2 if... |
| :---- | :---- | :---- | :---- |
| H1 (text modality) | No effect | Two-tailed equivalence | Significant difference found |
| H2 (text elaboration) | No benefit | One-tailed | Elaboration helps (unexpected) |
| H3 (coarse-to-fine) | Degradation | One-tailed | Two-stage approach warrants optimisation |
| H4 (consensus voting) | Improvement | One-tailed | Significant improvement |
| H5 (example ordering) | Canonical placement matters | One-tailed | Significant improvement |
| H6 (prompt diversity) | Diverse > identical | Factorial ANOVA | Main effect or interaction significant |
| H7 (hard negatives) | Precision ↑, Recall stable | Factorial ANOVA | Precision up, recall stable |
| H8 (Flash→Pro transfer) | Effects replicate | Replication | ≥80% effects replicate directionally |
| H9 (temperature) | T=1.0 optimal | One-way ANOVA | Any temperature outperforms 1.0 |

### 7.2 Exploratory Hypotheses

| Hypothesis | Question | Analysis |
| :---- | :---- | :---- |
| H10 (fine-to-coarse) | Does context expansion help uncertain cases? | Compare F1 on uncertain subset |
| H11 (temperature variation) | Does varied temperature improve ensembles? | Paired comparison |
| H12 (cross-model consistency) | Do effects generalise across providers? | Qualitative replication |
| H13 (cross-model voting) | Does cross-model voting beat within-model? | Compare F1 at N=6 |
| H14 (training pool size) | How does pool size affect library quality? | F1 vs pool size curve |
| H15 (library size) | What is optimal few-shot library size? | F1 vs library size curve |
| E7 (tile size) | How does tile size affect performance? | F1 vs tile size |

---

## 8\. Implementation Details

### 8.1 Models

**Primary**: Gemini 3 Flash, Gemini 3 Pro

**Secondary (for H10)**: Claude 4.5 Haiku, Sonnet, Opus; GPT-5.2 Thinking, Pro

### 8.2 API Parameters

All models tested at maximum capability configuration. Parameters

**Gemini 3 (Google):**

| Model | Model ID | thinking\_level |
| ----- | ----- | ----- |
| Flash | `gemini-3-flash` | `high` |
| Pro | `gemini-3-pro` | `high` |

Fixed parameters:

* `temperature`: 1.0 (required; values \<1.0 cause degraded performance)  
* `mediaResolution`: `default (media_resolution_medium)`  
* `max_output_tokens`: 8192

**Claude 4.5 (Anthropic):**

| Model | Model ID | effort | thinking.budget\_tokens |
| ----- | ----- | ----- | ----- |
| Haiku | `claude-haiku-4-5-20251001` | — | 8192 |
| Sonnet | `claude-sonnet-4-5-20250929` | — | 8192 |
| Opus | `claude-opus-4-5-20251101` | `high` | 16384 |

Fixed parameters:

* `temperature`: 1.0  
* `max_tokens`: 16384 (must exceed budget\_tokens)

Notes: Extended thinking enabled for all variants. Effort parameter (beta) applied to Opus only.

**GPT-5.2 (OpenAI):**

| Model | Model ID | reasoning.effort | Notes |
| ----- | ----- | ----- | ----- |
| Instant | `gpt-5.2-chat-latest` | N/A | Speed-optimized variant; 128k context |
| Thinking | `gpt-5.2` | `xhigh` | Maximum single-path reasoning |
| Pro | `gpt-5.2-pro` | `xhigh` | Parallel reasoning threads |

Fixed parameters:

* `temperature`: 1.0 (fixed; cannot be modified)  
* `verbosity`: `low`  
* `max_output_tokens`: 8192

All other parameters left at provider defaults.

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

#### 8.3.2 H6 Text Diversity Methodology

For H6 Conditions B and D (varied text), we use 5 semantically equivalent instruction variants. Each variant:

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

#### 8.3.3 Runtime Parameters

The following parameters are specified at runtime, not in config files:

- **Temperature**: T ∈ {0.0, 0.3, 0.7, 1.0} as per factorial design (Section 8.4.6)
- **Model**: Flash vs Pro specified via command-line argument
- **Number of passes (N)**: For voting experiments

### 8.4 Few-Shot Library Construction

The few-shot library will be constructed empirically using training tiles only, following this procedure.

#### 8.4.1 Library Composition

The library comprises four example categories:

| Category | Source | Purpose | Selection |
| :--- | :--- | :--- | :--- |
| Canonical positive | Map legend | Establish clear positive prototypes | 4 legend-derived symbols |
| Hard positive | FN mining | Cover difficult positive cases | Top K by frequency (target K=4) |
| Hard negative | FP mining | Prevent common false positives | Top M by frequency (target M=3) |
| Null tile | Training set | Establish "no mounds" baseline | Stratified sample (n=3) |

**Category ratios**: The baseline library uses approximately 4:K:M:3 (canonical:hard-pos:hard-neg:null). For H7 conditions without hard negatives, the ratio becomes 4:K:0:3.

**Library size variations**: Total library size varies by condition:
- Minimal: 7 examples (4 canonical + 3 null; no hard examples)
- Baseline: 7 + K + M examples (with hard positives and negatives)
- Extended: May include additional hard examples if pool allows (documented)

#### 8.4.2 Baseline Library

**Canonical positives** (legend-derived):
* Burial mound, settlement mound, triangulation on mound, benchmark on mound

**Null tiles** (3 tiles selected via stratified sampling):

* Pool: Training tiles with density=empty (mound\_count=0)
* Content threshold: ≤75% background pixels (ensures meaningful map content)
* Stratification: One tile per map, with Lesovo required
* Random seed: 20251223

**Selected tiles** (n=3):

| Tile | Map | Background % | Note |
| :---- | :---- | :---- | :---- |
| K-35-078-1\_Lesovo\_x2240\_y2688.png | Lesovo | 10% | Required for distinct terrain |
| K-35-053-3\_Elenovo\_x3584\_y1344.png | Elenovo | 30% | Stratified random |
| K-35-052-4\_32635\_x896\_y1792.png | 32635 | 10% | Stratified random |

**Rationale**:

* Lesovo was required because it has visually distinct terrain (forested, different symbol density) compared to the other maps  
* Stratified selection ensures geographic diversity  
* Low background percentage ensures tiles contain meaningful cartographic content rather than being mostly blank margins

**Hard example selection procedure:**

1. Run baseline library on all 20 training tiles with 5-pass consensus voting  
2. Identify False Negatives (ground truth mounds missed in ≥3/5 passes)  
3. Rank FNs by frequency; select top 4 as hard positive examples  
4. Identify False Positives (detections in ≥3/5 passes with no matching ground truth)  
5. Rank FPs by frequency; select top 3 as hard negative examples  
6. If ties occur, select randomly (document seed)

**Ordering (for H5):**

* "Best-last" condition: Hard positives placed in final positions  
* "Random" condition: Shuffled with documented seed

**Documentation:** The resulting library will be uploaded to OSF as a supplement before any holdout evaluation. The supplement will include:

* Image filenames and labels
* Selection rationale (frequency counts)
* Exact ordering for each condition

#### 8.4.3 Cross-Pass Sampling Methodology (for H6 Image Diversity)

For conditions requiring varied examples across passes (H6 Conditions C and D), we use frequency-capped random sampling to ensure diversity while maintaining statistical power for example-level analysis.

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

#### 8.4.4 Example-Level Effectiveness Analysis

Understanding which specific examples drive library effectiveness enables future library optimisation and provides insight into VLM few-shot learning mechanisms.

**Primary analysis (post-hoc regression):**

After completing H6 experiments, fit a linear model predicting pass-level F1 from example presence:

```
F1_pass ~ β₀ + Σᵢ βᵢ(exampleᵢ_present) + ε
```

Where:
- `exampleᵢ_present` = 1 if example i appeared in that pass, 0 otherwise
- βᵢ estimates the marginal contribution of example i to F1
- Model fitted using ordinary least squares with robust standard errors

**Reporting:**
- Coefficient estimates (βᵢ) with 95% confidence intervals
- Flag examples where |βᵢ| > 0.02 F1 as "high-impact"
- Rank examples by absolute effect size within each category

**Secondary analysis (category-level effects):**

Aggregate example-level effects by category:

```
F1_pass ~ β₀ + β_canon(n_canonical) + β_hardpos(n_hard_positive)
        + β_hardneg(n_hard_negative) + β_null(n_null) + ε
```

This estimates the marginal value of adding one more example of each type.

**Tertiary analysis (BIBD, if feasible):**

If library size k ≤ 10 and N ≥ 20, construct a Balanced Incomplete Block Design where:
- Each example appears in exactly r passes (r ≈ N/2)
- Each pair of examples co-occurs in exactly λ passes

This enables ANOVA decomposition:

```
F1 = μ + Σᵢ(main effect of exampleᵢ) + Σᵢⱼ(interaction of exampleᵢ × exampleⱼ) + ε
```

BIBD parameters will be determined post-library-construction and documented before holdout evaluation.

**Documentation commitment:**

The following will be published as supplementary data:
- Exact example assignment matrix (passes × examples)
- Achieved frequency distribution per example
- Regression coefficients and diagnostics
- Random seeds used for all sampling

#### 8.4.5 Hypothesis Interaction Summary

The following table summarises how library-related hypotheses interact and which experimental parameters vary:

| Hypothesis | What Varies | Fixed Elements | Library Size | Passes |
| :--- | :--- | :--- | :--- | :--- |
| H4 (voting) | N, T (vote threshold) | Library composition, ordering | Baseline | 5, 10, 30 |
| H5 (ordering) | Example order within pass | Library composition, which examples | Baseline | 5 |
| H6 (diversity) | Which hard examples per pass; prompt text | Canonical + null (always present) | Baseline | 5 |
| H7 (hard negatives) | Presence/absence of hard negative category | Canonical, hard positive, null | Varies | 5 |

**Interaction constraints:**

| Interaction | Resolution |
| :--- | :--- |
| H5 × H6 | H5 ordering applies to the examples selected for each pass; in H6 "Varied" conditions, ordering is applied after sampling |
| H5 × H7 | H7 conditions without hard negatives use ordering over reduced library (canonical + hard positive + null only) |
| H6 × H7 | H6 image diversity varies hard positives and hard negatives (when present); H7 Conditions A/B have no hard negatives to vary |
| H4 × H6 | H4 vote threshold optimisation uses H6 Condition A (fixed library) as baseline; diversity effects tested at fixed N=5 |

**Execution order:**

1. **H7 first**: Determines whether hard negatives are included (establishes library composition)
2. **H5 second**: Tests ordering effects on the established library
3. **H6 third**: Tests diversity effects (requires H5 baseline for comparison)
4. **H4 throughout**: Vote threshold grid search runs in parallel across conditions

**Cross-hypothesis analysis:**

After individual hypothesis tests, exploratory analyses will examine:
- Whether optimal voting threshold (H4) differs by library composition (H7)
- Whether ordering effects (H5) interact with diversity (H6)
- Whether example-level effects (Section 8.4.4) explain hypothesis-level results

#### 8.4.6 Pairwise Interaction Testing Methodology

**Rationale**: Individual hypothesis tests (H1, H5, H7, H9) examine main effects in isolation. However, factor effects may not be additive — a technique that improves performance in one condition may degrade it in another. To detect such positive or negative interactions, we test all two-way (pairwise) combinations of experimental factors. This enables us to identify synergistic effects (e.g., hard negatives help more with text+image than image-only) or antagonistic effects (e.g., low temperature helps with canonical-first but hurts with random ordering).

To systematically detect two-way interactions between experimental factors, we employ a full factorial design on core factors, with pre-specified escalation triggers for higher-order interactions.

**Core experimental factors:**

| Factor | Symbol | Levels | Description |
| :--- | :--- | :--- | :--- |
| Modality | M | 2 | image-only, text+image |
| Example ordering | O | 3 | canonical-first, canonical-last, random |
| Hard negatives | H | 2 | without, with |
| Temperature | T | 4 | 0.0, 0.3, 0.7, 1.0 |

**Design:**

- Full factorial: 2 × 3 × 2 × 4 = 48 conditions
- Each condition tested at N=5 voting (5 passes per tile)
- Total runs: 48 × 5 × 20 tiles = 4,800 API calls on Flash
- Estimated cost: ~$6-10 (well under $250 budget trigger)

This design provides full power to detect all two-way interactions without confounding. Three-way and four-way interactions are estimable but with reduced power.

**Text-image ordering constraint:**

For text+image conditions (M = text+image), text ordering corresponds with image ordering:

- If example images are ordered [burial_mound, settlement_mound, triangulation_mound, ...], the text descriptions follow the same sequence
- Text always precedes images in the prompt structure (fixed position)
- This constraint reduces the design from a potential 2 × 3 × 2 × 4 × 2 = 96 conditions to 48 conditions

Rationale: If ordering effects exist, they should manifest consistently across modalities when text and image orderings are aligned. Misaligned orderings (e.g., images in one order, text in another) are not tested; this is noted as a design constraint.

**Escalation triggers for higher-order interactions:**

If pairwise analysis reveals unexpected patterns, we escalate to three-way interaction testing:

| Trigger | Definition | Action |
| :--- | :--- | :--- |
| Crossover interaction | Effect direction reverses across levels of another factor | Test 3-way: A × B × C where C is the moderating factor |
| Large attenuation | Effect size reduces by >50% at different level of another factor | Spot-check 3-way interaction |
| Transfer failure | M × O interaction shows ordering matters for image-only but not text+image | Test text-position factor |

**Escalation procedure:**

1. **Primary analysis**: Full factorial ANOVA on 48 conditions, testing all main effects and two-way interactions
2. **IF any trigger condition is met**:
   - Identify the three factors involved
   - Test the specific 3-way interaction term
   - Report effect size and confidence interval
3. **IF 3-way interaction is significant (α = 0.05)**:
   - Document the interaction pattern
   - Consider additional spot-check conditions (e.g., text-position variants)
   - Flag for Stage 2 validation with larger sample
4. **IF no triggers are met**:
   - Conclude that pairwise interactions adequately characterise the factor relationships
   - Report this as a positive finding (interpretable, additive effects)

**Cost containment:**

Escalation beyond the primary 48-condition factorial is budgeted at $50 additional (allowing ~3,800 additional Flash calls or ~380 Pro calls). If escalation costs approach $250 cumulative, we pause for cost-benefit review before proceeding.

### 8.5 Voting Implementation

Consensus voting aggregates detections from multiple passes into a single prediction set.

#### Spatial Clustering Algorithm

1. **Pool all detections** from N independent passes into a single collection
2. **Compute pairwise distances** between detection centroids
3. **Cluster detections** using distance threshold matching the F1 evaluation tolerance (20m):
   - Detections within 20m of each other are candidates for the same cluster
   - Greedy clustering: for each unclustered detection, find all others within 20m and matching label; group as cluster
4. **Count votes per cluster**: number of distinct passes contributing at least one detection to the cluster
5. **Apply vote threshold**: retain clusters with ≥ T votes (e.g., ≥2/5 for 5-pass voting)
6. **Output geometry**: centroid of cluster members' centroids

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

#### Parameters for H4 Test

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
- **Tiles**: 448×448 pixel tiles at native resolution (~90 tiles per map, ~360 total)
- **Ground Truth**: 569 annotated mound symbols across all maps

#### Selection Criteria

| Criterion | Value | Rationale |
| :--- | :--- | :--- |
| **Content threshold** | ≤75% background (black) | Excludes predominantly empty edge tiles |
| **Training set** | 20 tiles (5 per map) | Sufficient for few-shot library development |
| **Holdout set** | 20 tiles (5 per map) | Matched sample for evaluation |
| **Stratification** | Empty/Sparse/Dense | Balanced density representation |
| **Spatial separation** | Holdout tiles not adjacent to training tiles | Prevents spatial autocorrelation |

#### Tile Density Categories

| Category | Mound Count | Purpose |
| :--- | :--- | :--- |
| Empty | 0 | Tests false positive rate (hallucinations) |
| Sparse | 1-2 | Tests detection in low-density contexts |
| Dense | 3+ | Tests detection in high-density contexts |

#### Randomisation

- **Random seed**: 1766464625 (documented in `inputs/tile_selection_metadata.json`)
- **Stratified random sampling**: Within each map, sample proportionally from density strata
- **Reproducibility**: Re-running with same seed produces identical selection

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

| Hypothesis | Description | Status | Implementation |
| :--- | :--- | :--- | :--- |
| H1 | Text modality effect | ✅ Ready | Factorial factor (modality) |
| H2 | Text elaboration | ✅ Ready | Factorial factor (elaboration) |
| H3 | Coarse-to-fine two-stage | ✅ Ready | Separate pipeline (propose→verify) |
| H4 | Consensus voting | ✅ Ready | Voting grid search |
| H5 | Example ordering | ✅ Ready | Factorial factor (ordering) |
| H6 | Prompt/example diversity | 📋 Deferred | Methodology specified; files created before holdout |
| H7 | Hard negatives | ✅ Ready | Factorial factor (hard_negatives) |
| H8 | Flash→Pro transfer | ✅ Ready | Runtime model parameter |
| H9 | Temperature | ✅ Ready | Factorial factor (temperature) |

#### 8.7.2 Configuration File Mapping

| Hypothesis | Config Files | System Instructions |
| :--- | :--- | :--- |
| H1 | `detect_image-only*.json` vs `detect_text-image*.json` | `detect_image-only.md` vs `detect_text-image.md` |
| H2 | `detect_*_elaborate*.json` variants | `detect_*_elaborate*.md` variants |
| H3 | `propose_image-only.json` + `verify_image-only.json` | `propose_image-only.md`, `verify_image-only.md` |
| H4 | Any detect config (passes parameter) | Any detect instruction |
| H5 | `*_canonical-last.json`, `*_random-order.json` | Same instruction file per modality |
| H6 | 5 text variants (to create before holdout) | 5 instruction variants |
| H7 | `*_hardneg.json` variants | `*_hardneg.md` variants |
| H8 | All configs (model runtime override) | All instructions |
| H9 | All configs (temperature runtime override) | All instructions |

#### 8.7.3 Script Mapping

| Hypothesis | Primary Scripts | Analysis Scripts |
| :--- | :--- | :--- |
| H1, H5, H7, H9 | `run_study.py`, `4_detect_mounds_batch.py` | `lib_advanced_metrics.py` |
| H2 | `4_detect_mounds_batch.py` | `lib_advanced_metrics.py` |
| H3 | `4_detect_mounds_batch.py` (2× sequential) | `7_analyze_consensus.py`, `8_analyze_proposer_consensus.py` |
| H4 | `run_study.py` (passes parameter) | `7_analyze_consensus.py` |
| H6 | `run_study.py` (extended for diversity) | `lib_advanced_metrics.py` |
| H8 | `run_study.py` (model parameter) | `lib_advanced_metrics.py` |

#### 8.7.4 Factorial Design Coverage (Phase 2)

The 48-condition factorial experiment (`studies/phase2-factorial.yaml`) tests H1, H5, H7, and H9 simultaneously:

| Config Pattern | H1 (Modality) | H5 (Ordering) | H7 (Hard Neg) |
| :--- | :--- | :--- | :--- |
| `detect_image-only.json` | image-only | canonical-first | baseline |
| `detect_image-only_canonical-last.json` | image-only | canonical-last | baseline |
| `detect_image-only_random-order.json` | image-only | random | baseline |
| `detect_image-only_hardneg.json` | image-only | canonical-first | hardneg |
| `detect_image-only_canonical-last_hardneg.json` | image-only | canonical-last | hardneg |
| `detect_image-only_random-order_hardneg.json` | image-only | random | hardneg |
| `detect_text-image.json` | text+image | canonical-first | baseline |
| `detect_text-image_canonical-last.json` | text+image | canonical-last | baseline |
| `detect_text-image_random-order.json` | text+image | random | baseline |
| `detect_text-image_hardneg.json` | text+image | canonical-first | hardneg |
| `detect_text-image_canonical-last_hardneg.json` | text+image | canonical-last | hardneg |
| `detect_text-image_random-order_hardneg.json` | text+image | random | hardneg |

Each of the 12 configs is tested at 4 temperatures (0.0, 0.3, 0.7, 1.0) for H9, yielding 48 total conditions.

---

## 9\. Implementation Priority

### Tier 1: Must Test (Core Confirmatory)

- **H4** (consensus voting) — highest practical impact; foundational
- **H7** (hard negatives) — directly addresses precision issues

### Tier 2: Should Test (Secondary Confirmatory)

- **H5** (example ordering) — low implementation cost, clear theoretical basis
- **H6** (prompt diversity) — moderate confidence, refines H4
- **H8** (Flash→Pro transfer) — validates development approach
- **H9** (temperature) — validates vendor recommendation

### Tier 3: Lower Priority (Confirmatory)

- **H1, H2** (text effects) — already informally tested; confirmatory test validates preliminary findings
- **H3** (coarse-to-fine) — preliminary evidence suggests degradation; confirmatory test validates this unexpected result against literature recommendations

### Tier 4: If Resources Allow (Exploratory)

- **H10** (fine-to-coarse) — novel, worth exploring
- **H11** (temperature variation) — likely small effect
- **H12** (cross-model) — important for generalizability
- **H13–H15, E7** — additional exploratory questions

---

## 10\. Stage 2 Planning (Contingent on Stage 1 Results)

Techniques that pass Stage 1 screening will be validated in Stage 2 with:

- **Larger sample**: Additional tiles from the 361-tile corpus (e.g., 40-80 tiles)  
- **Stricter correction**: Bonferroni or Holm-Bonferroni at α = 0.05  
- **Transfer testing**: Tiles from maps outside the 4 annotated sheets (if feasible)  
- **Optimized parameters**: For techniques that show promise, optimize hyperparameters (e.g., voting threshold, number of hard negatives)

Stage 2 will be separately preregistered based on Stage 1 findings.

---

## 11\. Preregistration Checklist

Before any test set evaluation:

- [ ] Finalize hypothesis list and predictions  
- [ ] Specify exact test tile IDs (20 tiles, identified by map \+ tile number)  
- [x] Specify primary outcome: Overall F1 at \[X\]m spatial tolerance  
- [ ] Specify success threshold: F1 ≥ 0.85 for pipeline as a whole  
- [ ] Document few-shot library composition (examples, ordering)  
- [ ] Document prompt text for all conditions  
- [ ] Document hard negative examples (for H7)  
- [ ] Document prompt variants (for H6)  
- [ ] Specify random seeds for any stochastic elements  
- [ ] Commit analysis code to repository  
- [ ] Submit to OSF Registries  
- [ ] Obtain timestamp confirmation  
- [ ] **Then** proceed to test evaluation

---

## 12\. Outstanding Questions

The following items need to be specified before preregistration can be finalised:

### 12.1 Resolved

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

### 12.2 Pending

*All critical items resolved. Minor items may be added during final review.*

---

## References

- Sobotkova, A., Ross, S.A., Nassif-Haynes, C., & Ballsun-Stanton, B. (2023). Creating large, high-quality geospatial datasets from historical maps using novice volunteers. *Applied Geography*, 155, 102967\.  
    
- Vo, A., et al. (2025). Vision Language Models are Biased. arXiv:2505.23941.

---

*Document version: 3.0*
*Created: 2025-12-22*
*Updated: 2026-01-01*

**Changelog:**
- v3.0: Added Section 8.7 hypothesis-to-implementation mapping; status set to Ready for Registration
- v2.11: Section 8.3 prompt variants documentation; H6 text diversity methodology with example variants; runtime parameters specification
- v2.10: Section 8.4.6 pairwise interaction testing methodology; full 48-condition factorial design; text-image ordering constraint; escalation triggers for 3-way interactions; cost estimation (~$60-100 total)
- v2.9: H4 full grid search specification (N ∈ {5, 10, 30}); Sections 8.4.1-8.4.5 (library composition, cross-pass sampling methodology, example-level effectiveness analysis, hypothesis interactions); Section 8.2 cross-model comparability and cost-performance analysis; H8 adaptive testing framework with trigger conditions
- v2.8: De-duplicated document; consolidated tile selection methodology references; removed redundant spatial tolerance text
- v2.7: Added voting implementation algorithm (8.5), tile selection methodology (8.6), tile exclusion criteria, updated detection matching to Hungarian algorithm (4.1.2)
- v2.6: Fixed section numbering, added detection matching algorithm (4.1.2), corrected summary table, integrated answers, added timeline
- v2.5: Added API parameters, null tile selection, preliminary findings
- v2.0: Merged hypotheses document; added two-stage trial framework, FDR rationale, tile-level MCC, H5-H10, implementation priority, checklist  
