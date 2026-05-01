# VLM-Based Burial Mound Detection: Benchmark Review & Methodological Plan

**Document created**: 2024-12-23  
**Purpose**: Reference document for Claude Code development of burial mound symbol extraction pipeline

---

## Part 1: Critique of Secondary Source Materials

### Overview

Investigation into the methodological rigor of commonly cited traditional CV benchmarks for cartographic symbol detection revealed significant discrepancies between reported/implied performance and actual validated results. This has implications for how VLM-based approaches should be evaluated and compared.

### Benchmark Verification Summary

| Study | Domain | Claimed/Implied | Actual Performance | Validation Method | Assessment |
|-------|--------|-----------------|-------------------|-------------------|------------|
| YOLOv3 + CBAM (MDPI 2022) | Map point symbols | ~98% accuracy | **mAP@0.50 = 98%** | Train/test split undocumented | Real data ✓; validation methodology unclear |
| YOLOv3 + RF (MDPI 2021) | Burial mounds (LiDAR) | "High performance" | **F1 = 0.77** (P=0.97, R=0.64) | Against known burial mounds | Real data ✓; F1 lower than implied |
| Random Forest (MDPI 2020) | Burial mounds (LiDAR) | 93% detection rate | **93% on external dataset** | Separate geographic areas + field validation | **Gold standard methodology** |
| U-Net (ScienceDirect 2022) | Wetland symbols | F1 = 0.908 | **F1 = 0.886** | 10-fold cross-validation | Real data ✓; proper CV; slightly lower than cited |

### Key Findings

#### 1. The ">0.90 F1" Claim Does Not Hold

The synthesis documents implied traditional CV methods routinely achieve F1 > 0.90 for archaeological symbol detection. This is not supported:

- **YOLOv3 burial mounds**: F1 = 0.77 (calculated from reported P=0.97, R=0.64)
- **U-Net wetlands**: F1 = 0.886 (not 0.908)
- **Random Forest burial mounds**: 93% detection rate ≠ F1 (false positive count not incorporated)
- **YOLOv3 map symbols**: mAP ≠ F1 (different metrics, not directly comparable)

#### 2. Metric Confusion is Pervasive

Studies report different metrics (mAP, detection rate, accuracy, F1) that are not directly comparable:

- **mAP@0.50**: Area under precision-recall curve at 50% IoU threshold
- **Detection rate**: Recall only; ignores false positives
- **Accuracy**: Can be inflated by class imbalance (rare symbols in large tiles)
- **F1**: Harmonic mean of precision and recall; the appropriate comparison metric

#### 3. Validation Rigor Varies Dramatically

Only the Romanian Random Forest study (Niculiță, 2020) meets gold-standard validation criteria:
- External geographic test areas (separate 100 km² regions)
- Field-verified ground truth
- Explicit reporting of both false positives and false negatives

Most other studies lack clear documentation of train/test splits or use same-distribution validation only.

#### 4. Training Data Requirements

Traditional CV methods achieving competitive performance required:
- YOLOv3 map symbols: 6,675 annotated images
- YOLOv3 burial mounds: 560 annotated mounds + extensive preprocessing
- U-Net wetlands: Manual annotation + ~8 hours training time

### Implications for VLM Comparison

**Current VLM performance (F1 = 0.75) is more competitive than initially framed:**

- Matches or approaches the best-validated traditional method (YOLOv3 LiDAR at F1 = 0.77)
- Achieves this with 12 few-shot examples vs. hundreds/thousands of training samples
- Zero training time; adaptable through prompt refinement

**The F1 = 0.85 target remains meaningful** but should be compared against:
1. Properly validated CV benchmarks (F1 ≈ 0.77-0.89 range)
2. Human crowdsourcing baseline (~6% error rate ≈ F1 = 0.94)

---

## Part 2: Methodological Plan

### 2.1 Data Resources

#### Ground Truth Dataset
- **4 fully annotated Soviet 1:50,000 topographic maps**
- Annotations created by primary researcher (not model-derived)
- All burial mound symbol types marked
- Each map divided into ~90 tiles at full resolution
- **Total: 361 tiles across 4 maps**

#### Crowdsourcing Baseline (Sobotkova et al. 2023)
- ~80 maps annotated by student volunteers
- 6% error rate (predominantly false negatives; 1 false positive in reviewed sample)
- 241 person-hours for 10,827 features
- Average: 63 seconds per feature

#### Expansion Potential
- Several hundred additional maps covering Bulgaria
- Available for transfer testing or expanded training

### 2.2 Experimental Design

#### Training Set
- **20 tiles**: 5 randomly selected from each of 4 annotated maps
- Used for iterative prompt development and few-shot library construction
- Source of positive examples, hard negatives, edge cases

#### Holdout Test Set
- **20 tiles**: 5 different tiles from each of 4 maps (stratified)
- Completely held out from prompt development
- Used only for final evaluation

#### Expansion Protocol
- Additional training tiles (up to 180) available for ablation studies
- Incremental increases: 20 → 40 → 80 → 120 → 180 tiles
- Assess diminishing returns on few-shot library size

### 2.3 Models Under Evaluation

| Model | Role | Notes |
|-------|------|-------|
| Gemini Flash | Development/testing | Lower cost for iteration |
| Gemini Pro | Production evaluation | Primary results |
| Claude (Sonnet/Opus) | Cross-model comparison | Validates generalizability |
| GPT-4V | Cross-model comparison | Validates generalizability |

### 2.4 Primary Metrics

#### Detection Metrics
- **F1 Score** (primary): Overall and per symbol type
- **Precision**: False positive rate critical for practical deployment
- **Recall**: False negative rate; comparison to crowdsourcing baseline
- **Precision-Recall Curve**: Performance across confidence thresholds

#### Spatial Metrics
- **Spatial Tolerance Curve**: F1 at varying match distances (10m, 20m, 30m, 50m)
- Accounts for localization uncertainty in both predictions and annotations

#### Tile-Level Metrics
- **Tile classification accuracy**: Correct identification of empty vs. populated tiles
- **Per-tile detection rate**: Useful for practical deployment messaging

#### Uncertainty Quantification
- **Bootstrapped 95% CIs**: For all point estimates
- **Per-symbol-type sample sizes**: Reported alongside class-specific metrics

#### Cost Metrics
- **API cost per tile**: For reproducibility and adoption decisions
- **Time per tile**: End-to-end processing time

### 2.5 Methodological Enhancements

#### Preregistration (CRITICAL)

Before any model evaluation on test tiles, preregister:
1. Exact test tile IDs (20 tiles, identified by map + tile number)
2. Primary outcome metric: Overall F1 at 25m spatial tolerance
3. Success threshold: F1 ≥ 0.85
4. Secondary outcomes: Per-symbol F1, precision-recall curves
5. Analysis plan: Bootstrap procedure, CI calculation method

**Platform**: OSF Registries (https://osf.io/registries)  
**Timing**: After training set analysis, before any test set evaluation

#### Ablation Studies

Document the impact of key methodological choices:

1. **Few-shot library size**: Performance at 4, 8, 12, 16, 20 examples
2. **Hard negative inclusion**: With vs. without explicit counter-examples
3. **Example ordering**: Recency bias effects (best examples last vs. random)
4. **Prompt text content**: Minimal vs. detailed symbol descriptions
5. **Consensus voting**: 1-of-1, 2-of-3, 3-of-5, majority-of-N configurations
6. **Temperature variation**: Fixed vs. varied across voting passes

#### Error Analysis

Systematic categorization of failure modes:

**False Negatives (missed symbols)**:
- By symbol type (burial mound, triangulation point on mound, benchmark on mound)
- By visual quality (degraded, partial, overlapping)
- By spatial context (isolated, clustered, edge-of-tile)
- By map region (systematic geographic patterns)

**False Positives (incorrect detections)**:
- Confuser category (spot heights, quarries, wells, elevation markers)
- Visual similarity to target symbols
- Systematic patterns (certain terrain types, map conditions)

#### Explicit Baseline Comparisons

Frame all results against:

1. **Crowdsourcing baseline** (Sobotkova et al. 2023):
   - F1 ≈ 0.94 (6% error rate, predominantly FN)
   - Cost: 63 seconds human time per feature
   - Does VLM match? Exceed? At what cost trade-off?

2. **Best-validated CV benchmark**:
   - YOLOv3 burial mounds: F1 = 0.77 with 560 training mounds
   - Random Forest LiDAR: 93% detection on external validation
   - Does VLM match with dramatically less training data?

3. **Null baselines**:
   - Random detection at varying densities
   - Simple template matching (if feasible)

### 2.6 Generalization Testing

#### Within-Distribution (Primary)
- Test tiles from same 4 maps as training tiles
- Different spatial regions, same cartographic conventions

#### Transfer Testing (Secondary)
- Small sample of tiles from maps outside the 4 annotated sheets
- Manual spot-checking if full annotation not feasible
- Addresses reviewer question: "Does this generalize?"
- Explicitly acknowledge as limitation if not fully validated

### 2.7 Reporting Standards

#### Required Elements
- Full few-shot prompt (appendix or supplementary material)
- Example images from few-shot library (with annotations)
- Complete results tables with CIs
- Precision-recall curves for all models
- Spatial tolerance curves
- Error analysis with representative examples
- API costs and processing times
- Code availability statement

#### Reproducibility
- Exact model versions (e.g., `gemini-1.5-pro-002`)
- Temperature and generation parameters
- Random seeds where applicable
- Tile selection procedure (random seed)

---

## Part 3: Implementation Checklist

### Phase 1: Setup
- [ ] Finalize tile extraction at full resolution (361 tiles confirmed)
- [ ] Random selection of training tiles (20) with documented seed
- [ ] Random selection of test tiles (20) with documented seed
- [ ] Verify no overlap between training and test sets
- [ ] Document tile IDs for both sets

### Phase 2: Prompt Development (Training Set Only)
- [ ] Initial few-shot library construction from training tiles
- [ ] Iterative refinement based on training tile performance
- [ ] Hard negative mining from training tile false positives
- [ ] Ablation studies on training set
- [ ] Consensus voting optimization on training set
- [ ] Cross-model testing on training set (Gemini, Claude, GPT-4V)

### Phase 3: Preregistration
- [ ] Freeze prompt and methodology
- [ ] Document exact test tile IDs
- [ ] Specify primary outcome (F1 at 25m tolerance)
- [ ] Specify success criterion (F1 ≥ 0.85)
- [ ] Submit preregistration to OSF
- [ ] Wait for timestamp confirmation before proceeding

### Phase 4: Test Evaluation
- [ ] Run all models on test set (single evaluation per model)
- [ ] Calculate all preregistered metrics
- [ ] Perform error analysis
- [ ] Generate visualizations

### Phase 5: Extended Analysis
- [ ] Training set size ablation (if time permits)
- [ ] Transfer testing on out-of-sample maps (if feasible)
- [ ] Cost-benefit analysis vs. crowdsourcing baseline

### Phase 6: Reporting
- [ ] Draft results with all preregistered analyses
- [ ] Prepare supplementary materials (prompts, code, examples)
- [ ] Acknowledge limitations explicitly
- [ ] Submit to target venue (Journal of Computer Applications in Archaeology)

---

## Part 4: Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Inadvertent test set contamination | Preregistration; physical separation of tile sets; documented analysis pipeline |
| Low statistical power for rare symbol types | Report sample sizes; frame per-class results as exploratory; consider pooled analysis |
| Overfitting to 4-map idiosyncrasies | Stratified sampling; transfer testing; explicit generalization limitations |
| Cross-model comparison confounds | Same test set, same prompts (adapted minimally for API format), same evaluation code |
| Reviewer skepticism of VLM reliability | Comprehensive error analysis; explicit failure mode documentation; confidence intervals |

---

## Part 5: Key References

### Primary Baseline
- Sobotkova, A., Ross, S.A., Nassif-Haynes, C., & Ballsun-Stanton, B. (2023). Creating large, high-quality geospatial datasets from historical maps using novice volunteers. *Applied Geography*, 155, 102967.

### CV Benchmarks (Verified)
- YOLOv3 map symbols: MDPI 2022, mAP=98%, validation unclear
- YOLOv3 burial mounds (LiDAR): MDPI 2021, F1=0.77 (calculated), against known mounds
- Niculiță, M. (2020). "Geomorphometric Methods for Burial Mound Recognition and Extraction from High-Resolution LiDAR DEMs". *Sensors* 20(4): 1192. doi:10.3390/s20041192
- U-Net wetlands: ScienceDirect 2022, F1=0.886, 10-fold CV

### VLM Methodology (from prior evidence review)
- Text-image interference: Vo et al. (2025), arXiv:2505.23941 — minimal effect for novel domains
- Two-stage pipelines: No VLM-specific evidence found for +5-8% F1 claim
- Consensus voting: Confirmed effective; 3-5% accuracy gains typical

---

*Document version: 1.0*  
*Last updated: 2024-12-23*
