# Analysis Summary

**Purpose**: Plain-language overview of the statistical analysis plan for non-specialist readers.

**Last updated**: 2026-01-18

---

## What We Test

This study evaluates whether Vision Language Models (VLMs) can detect burial mound symbols on Soviet topographic maps. We test **15 hypotheses** about factors that might affect detection performance:

| Category | Hypotheses | Questions |
|----------|------------|-----------|
| **Prompt design** | H1, H5 | Does text detail level matter? How should negatives be described? |
| **Model parameters** | H7 | What temperature setting works best? |
| **Few-shot examples** | H4, H8 | Does example ordering matter? How many hard examples are needed? |
| **Voting** | H3, H9 | Does running multiple passes help? Does diversity between passes help? |
| **Architecture** | H2 | Does a two-stage pipeline outperform single-stage? |
| **Transfer** | H6 | Do Flash-optimal settings work on Pro? |
| **Exploratory** | H10-H15 | Tile size, HP:HN ratio, overlap, cross-model effects |

---

## How We Measure Success

### Primary Outcome: F1 Score at 20m

The **F1 score** balances precision and recall:

- **Precision**: Of the mounds we detected, how many were real?
- **Recall**: Of the real mounds, how many did we detect?
- **F1**: The harmonic mean of precision and recall (higher is better)

A detection counts as correct if it falls within **20 metres** of a ground truth mound. This tolerance accounts for georeferencing imprecision and symbol size.

### Secondary Outcome: Tile-Level MCC

The **Matthews Correlation Coefficient (MCC)** measures whether we correctly classify tiles as "has mounds" vs "empty". This addresses the practical question: *Can the method identify when there's nothing to find?*

---

## What We Report

For each hypothesis, we report:

| Metric | Description |
|--------|-------------|
| **Mean F1** | Average performance across 10 independent runs |
| **95% CI** | Confidence interval showing uncertainty |
| **Effect size** | How much better/worse compared to baseline |
| **p-value** | Statistical significance (both raw and FDR-corrected) |

---

## How We Handle Multiple Comparisons

With 8 confirmatory hypotheses, we use **False Discovery Rate (FDR) correction** at q = 0.05:

| Result | Interpretation |
|--------|----------------|
| FDR-corrected p < 0.05 | **Significant** — technique shows promise |
| Raw p < 0.05, FDR p ≥ 0.05 | **Suggestive** — consider for follow-up |
| Raw p ≥ 0.05 | **No evidence** — null hypothesis retained |

FDR is appropriate for a screening study where the goal is identifying promising techniques for further validation.

---

## How Each Hypothesis is Analysed

### H1: Modality/Elaboration Level

- **Design**: 5 conditions (image-only, brief-text, brief+image, verbose-text, verbose+image)
- **Analysis**: One-way ANOVA across 5 levels
- **Planned contrasts**: Image-only vs Brief+image; Brief+image vs Verbose+image; Text-only vs Image-using

### H2: Two-Stage Pipeline

- **Design**: 3 conditions (single-stage baseline, coarse-to-fine, fine-to-coarse)
- **Analysis**: One-tailed tests predicting two-stage ≤ single-stage
- **Note**: Treated as exploratory due to preliminary evidence of no benefit

### H3: Consensus Voting

- **Design**: Multiple pool sizes (N=5, 10, 30) and thresholds
- **Analysis**: Compare voted F1 vs single-pass mean F1
- **Output**: Threshold sweep curves showing optimal (N, threshold) combinations

### H4: Example Ordering

- **Design**: 3 conditions (canonical-first, canonical-last, random)
- **Analysis**: One-way ANOVA; planned contrast canonical-first vs canonical-last
- **Prediction**: Canonical-last > canonical-first (recency effect)

### H5: Negative Text Treatment

- **Design**: 3 levels (minimal, terse, verbose) × 3 M/E levels
- **Analysis**: Two-way ANOVA testing H5 main effect and M/E × H5 interaction
- **Primary metric**: Precision (with recall as safety check)

### H6: Flash→Pro Transfer

- **Design**: OFAT sensitivity testing of each factor
- **Analysis**: Compare Pro performance at Flash-optimal vs adjusted settings
- **Decision rule**: Adjust factor if Δ ≥ 0.03 F1

### H7: Temperature

- **Design**: 5 levels (0.0, 0.3, 0.7, 1.0, 1.3)
- **Analysis**: One-way ANOVA; planned contrasts T=1.0 vs each other level
- **Trigger**: Extend to T=1.6, 2.0 if T=1.3 outperforms T=1.0

### H8: Library Composition

- **Design**: 7 library conditions (Pure Positive Canon → Scale-32)
- **Analysis**: One-way ANOVA; sequential addition and scaling contrasts
- **Output**: Diminishing returns curve (F1 vs hard example count)

### H9-H15: Exploratory

- Reported but not included in FDR correction
- Interpreted cautiously as hypothesis-generating
- See preregistration for full specifications

---

## Statistical Power

With 60 holdout tiles containing 79 mound symbols:

| Metric | Minimum Detectable Effect |
|--------|---------------------------|
| Symbol-level F1 | ≈ 0.07–0.09 |
| Tile-level MCC | ≈ 0.20 |

Effects smaller than this may not reach statistical significance but will be flagged for Stage 2 investigation if directionally consistent.

---

## Practical Significance

Statistical significance is necessary but not sufficient. A technique must show:

1. **Statistical significance**: FDR-corrected p < 0.05
2. **Meaningful effect size**: More than trivial improvement (e.g., F1 > +0.03)
3. **Practical benefit**: Worth the added cost/complexity

A significant but tiny effect (F1 +0.01) will be reported but not treated as actionable.

---

## Blinding and Automation

All analyses are automated via precommitted scripts:

- API calls run without manual intervention
- Metrics computed automatically
- Statistical tests run on predetermined conditions

This eliminates analyst degrees of freedom during evaluation.

---

## Related Documents

- **Preregistration**: `preregistration.md` — Full statistical analysis plan (Section 3)
- **Hypothesis tracking**: `hypothesis-tracking.md` — Condition mappings
- **Execution plan**: `execution-plan.md` — Operational sequencing
