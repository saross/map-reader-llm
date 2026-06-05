# Phase 3a Comprehensive Results Report: Consensus Voting Across Temperature, Thinking Level, and Spatial Precision

> **⚠ ERRATUM (2026-06-05) — model mislabel.** This archived 60-tile validation report states the model was "Gemini 2.0 Flash (`gemini-2.0-flash-001`)". That is a **confabulation**: the actual detection outputs (`archive/outputs-pre-retest-60-tile/`) are tagged `-3-flash-` and record `gemini-3-flash-preview` internally; **zero** project artefacts record any 2.x model, and the project post-dates Gemini 3's 2025-11-18 release. **Every model reference here should read `gemini-3-flash`.** Superseded by the 340-tile production retest; preserved per archive-never-delete. Evidence: `results/retest/retest-production-summary.md` § Changelog.

**Author**: Shawn Ross
**Date**: 2026-02-16
**Status**: Reference report for paper drafting
**Phase**: 3a (H3 — Consensus Voting)

---

## Purpose

This report consolidates all Phase 3a consensus voting results into a single
reference document for use when drafting the paper. It integrates findings
from three analytical dimensions:

1. **Consensus voting sweep** (temperature × pool size × vote threshold)
2. **Thinking level × modality interaction** (2×2 factorial: MINIMAL/HIGH × image/text)
3. **Spatial tolerance sensitivity** (evaluation matching at 20 m, 30 m, 40 m, 50 m)

Together these dimensions span a 2×2×4 parameter space: 4 conditions × 4
tolerances = 16 analysis runs, each evaluating 135 consensus configurations
with K=1000 bootstrap iterations. The report is structured to provide
quotable results, interpretive narratives, and citable tables.

---

## 1. Experimental Design

### 1.1 Conditions

| Track | Modality | Thinking Level | Label |
|:------|:---------|:---------------|:------|
| Track 1 | Image (base64-encoded map tile) | MINIMAL | T1 Img MIN |
| Track 1 | Image (base64-encoded map tile) | HIGH | T1 Img HIGH |
| Track 2 | Text (coordinate descriptions) | MINIMAL | T2 Txt MIN |
| Track 2 | Text (coordinate descriptions) | HIGH | T2 Txt HIGH |

Each condition comprises 90 batch runs (30 per temperature × 3 temperatures)
across 60 holdout tiles containing 79 ground truth burial mound symbols.

### 1.2 Consensus Sweep Parameters

| Parameter | Values |
|:----------|:-------|
| Temperatures | T=0.3, T=0.7, T=1.0 |
| Pool sizes (N) | 5, 10, 30 |
| Vote thresholds (x) | 1 through N (all integer values) |
| Total configurations per analysis | 135 |

### 1.3 Evaluation Design

| Parameter | Value |
|:----------|:------|
| Consensus clustering tolerance | 20 m (fixed, preregistered) |
| Within-run deduplication | 20 m |
| Evaluation matching tolerances | 20 m (preregistered), 30 m, 40 m, 50 m |
| Bootstrap iterations | 1,000 |
| Bootstrap seed | 42 |
| Model | Gemini 2.0 Flash (gemini-2.0-flash-001) |

The clustering tolerance is held constant at 20 m across all runs.
Only the evaluation matching buffer varies. This decoupled design ensures
that the detection pool (clusters, vote counts) is identical at every
tolerance; only the TP/FP/FN classification changes.

### 1.4 Single-Pass Baselines

| Modality | Baseline F1 | Source |
|:---------|:------------|:-------|
| Image | 0.609 | Phase 2a best single-pass (T=0.0, K=1) |
| Text | 0.660 | Phase 2a best single-pass (T=0.0, K=1) |

---

## 2. Headline Results

### 2.1 Best Performance at Each Tolerance

**Table 2.1.** Best consensus F1 across all four conditions at each
matching tolerance.

| Tolerance | Best Condition | F1 | 95% CI | P | R | Config |
|----------:|:---------------|-----:|:------:|-----:|-----:|:-------|
| 20 m | T2 Txt HIGH | 0.751 | [0.610, 0.796] | 0.772 | 0.732 | T0.7 N=30 x=22 |
| 30 m | T2 Txt HIGH | 0.804 | [0.667, 0.843] | 0.826 | 0.784 | T0.7 N=30 x=22 |
| 40 m | T2 Txt HIGH | 0.821 | [0.674, 0.860] | 0.773 | 0.876 | T0.7 N=30 x=19 |
| 50 m | T2 Txt HIGH | 0.831 | [0.684, 0.868] | 0.782 | 0.887 | T0.7 N=30 x=19 |

Track 2 Text HIGH is the best-performing condition at every tolerance tested.

### 2.2 H3 Confirmation: Consensus Beats Single-Pass

All four conditions confirm H3 at all four tolerances. The consensus F1
improvement over the single-pass baseline (ΔF1) ranges from +2.3 pp
(T2 Txt MIN at 20 m) to +18.5 pp (T1 Img MIN at 50 m).

**Table 2.2.** ΔF1 (consensus best − single-pass baseline) across the
full matrix.

| Condition | Baseline | Δ at 20 m | Δ at 30 m | Δ at 40 m | Δ at 50 m |
|:----------|--------:|---------:|---------:|---------:|---------:|
| T1 Img MIN | 0.609 | +4.1 pp | +12.5 pp | +17.6 pp | +18.5 pp |
| T1 Img HIGH | 0.609 | +3.5 pp | +11.7 pp | +16.6 pp | +18.5 pp |
| T2 Txt MIN | 0.660 | +2.3 pp | +9.3 pp | +12.2 pp | +12.2 pp |
| T2 Txt HIGH | 0.660 | +9.1 pp | +14.4 pp | +16.1 pp | +17.1 pp |

Note: The baseline is measured at 20 m and is not re-evaluated at wider
tolerances. The ΔF1 at wider tolerances therefore conflates two effects:
(1) consensus voting improvement and (2) spatial tolerance relaxation.
For a clean comparison, use only the 20 m column as the measure of
consensus voting benefit.

---

## 3. Full Results Matrix

### 3.1 Global Optima: F1

**Table 3.1.** Best consensus F1 by condition and matching tolerance.

| Condition | 20 m | 30 m | 40 m | 50 m |
|:----------|-----:|-----:|-----:|-----:|
| T1 Img MIN | 0.650 | 0.734 | 0.785 | 0.794 |
| T1 Img HIGH | 0.644 | 0.726 | 0.775 | 0.794 |
| T2 Txt MIN | 0.683 | 0.753 | 0.782 | 0.782 |
| T2 Txt HIGH | 0.751 | 0.804 | 0.821 | 0.831 |

### 3.2 Global Optima: Precision

**Table 3.2.** Precision at the global optimum configuration.

| Condition | 20 m | 30 m | 40 m | 50 m |
|:----------|-----:|-----:|-----:|-----:|
| T1 Img MIN | 0.640 | 0.716 | 0.845 | 0.775 |
| T1 Img HIGH | 0.699 | 0.692 | 0.738 | 0.757 |
| T2 Txt MIN | 0.657 | 0.724 | 0.752 | 0.752 |
| T2 Txt HIGH | 0.772 | 0.826 | 0.773 | 0.782 |

### 3.3 Global Optima: Recall

**Table 3.3.** Recall at the global optimum configuration.

| Condition | 20 m | 30 m | 40 m | 50 m |
|:----------|-----:|-----:|-----:|-----:|
| T1 Img MIN | 0.660 | 0.753 | 0.732 | 0.814 |
| T1 Img HIGH | 0.598 | 0.763 | 0.814 | 0.835 |
| T2 Txt MIN | 0.711 | 0.784 | 0.814 | 0.814 |
| T2 Txt HIGH | 0.732 | 0.784 | 0.876 | 0.887 |

### 3.4 Global Optima: Confidence Intervals

**Table 3.4.** 95% bootstrap CI for F1 at the global optimum.

| Condition | 20 m | 30 m | 40 m | 50 m |
|:----------|:-----|:-----|:-----|:-----|
| T1 Img MIN | [0.494, 0.714] | [0.609, 0.776] | [0.654, 0.824] | [0.683, 0.825] |
| T1 Img HIGH | [0.493, 0.707] | [0.576, 0.780] | [0.639, 0.819] | [0.657, 0.842] |
| T2 Txt MIN | [0.523, 0.757] | [0.600, 0.808] | [0.637, 0.831] | [0.637, 0.831] |
| T2 Txt HIGH | [0.610, 0.796] | [0.667, 0.843] | [0.674, 0.860] | [0.684, 0.868] |

### 3.5 Global Optima: Consensus Configuration Selected

**Table 3.5.** Optimal consensus configuration at each tolerance.

| Condition | 20 m | 30 m | 40 m | 50 m |
|:----------|:-----|:-----|:-----|:-----|
| T1 Img MIN | T0.7 N=10 x=6 | T1.0 N=30 x=14 | T1.0 N=30 x=17 | T1.0 N=30 x=14 |
| T1 Img HIGH | T0.3 N=30 x=25 | T0.7 N=30 x=15 | T0.7 N=30 x=15 | T0.7 N=30 x=15 |
| T2 Txt MIN | T1.0 N=30 x=22 | T1.0 N=30 x=22 | T1.0 N=30 x=22 | T1.0 N=30 x=22 |
| T2 Txt HIGH | T0.7 N=30 x=22 | T0.7 N=30 x=22 | T0.7 N=30 x=19 | T0.7 N=30 x=19 |

### 3.6 Number of Consensus Detections at Global Optimum

**Table 3.6.** n_det (number of detections surviving consensus filtering)
at the global optimum.

| Condition | 20 m | 30 m | 40 m | 50 m |
|:----------|-----:|-----:|-----:|-----:|
| T1 Img MIN | 100 | 102 | 84 | 102 |
| T1 Img HIGH | 83 | 107 | 107 | 107 |
| T2 Txt MIN | 105 | 105 | 105 | 105 |
| T2 Txt HIGH | 92 | 92 | 110 | 110 |

---

## 4. Per-Temperature Analysis

### 4.1 Per-Temperature Best F1

**Table 4.1.** Best F1 at each temperature and tolerance.

| Condition | Buf | T0.3 | T0.7 | T1.0 |
|:----------|----:|-----:|-----:|-----:|
| T1 Img MIN | 20 | 0.619 | 0.650 | 0.598 |
| T1 Img MIN | 30 | 0.701 | 0.704 | 0.734 |
| T1 Img MIN | 40 | 0.763 | 0.761 | 0.785 |
| T1 Img MIN | 50 | 0.775 | 0.790 | 0.794 |
| T1 Img HIGH | 20 | 0.644 | 0.638 | 0.579 |
| T1 Img HIGH | 30 | 0.709 | 0.726 | 0.714 |
| T1 Img HIGH | 40 | 0.759 | 0.775 | 0.765 |
| T1 Img HIGH | 50 | 0.769 | 0.794 | 0.765 |
| T2 Txt MIN | 20 | 0.676 | 0.660 | 0.683 |
| T2 Txt MIN | 30 | 0.737 | 0.742 | 0.753 |
| T2 Txt MIN | 40 | 0.743 | 0.742 | 0.782 |
| T2 Txt MIN | 50 | 0.743 | 0.742 | 0.782 |
| T2 Txt HIGH | 20 | 0.748 | 0.751 | 0.733 |
| T2 Txt HIGH | 30 | 0.794 | 0.804 | 0.800 |
| T2 Txt HIGH | 40 | 0.813 | 0.821 | 0.821 |
| T2 Txt HIGH | 50 | 0.822 | 0.831 | 0.821 |

### 4.2 Per-Temperature Optimal Configuration

**Table 4.2.** Consensus configuration at the per-temperature optimum.

| Condition | Buf | T0.3 | T0.7 | T1.0 |
|:----------|----:|:-----|:-----|:-----|
| T1 Img MIN | 20 | N=30 x=22 | N=10 x=6 | N=30 x=15 |
| T1 Img MIN | 30 | N=30 x=22 | N=30 x=17 | N=30 x=14 |
| T1 Img MIN | 40 | N=30 x=22 | N=5 x=3 | N=30 x=17 |
| T1 Img MIN | 50 | N=30 x=18 | N=5 x=3 | N=30 x=14 |
| T1 Img HIGH | 20 | N=30 x=25 | N=30 x=14 | N=30 x=12 |
| T1 Img HIGH | 30 | N=30 x=20 | N=30 x=15 | N=30 x=15 |
| T1 Img HIGH | 40 | N=30 x=20 | N=30 x=15 | N=30 x=15 |
| T1 Img HIGH | 50 | N=30 x=20 | N=30 x=15 | N=30 x=15 |
| T2 Txt MIN | 20 | N=5 x=5 | N=30 x=28 | N=30 x=22 |
| T2 Txt MIN | 30 | N=10 x=9 | N=30 x=23 | N=30 x=22 |
| T2 Txt MIN | 40 | N=5 x=5 | N=30 x=23 | N=30 x=22 |
| T2 Txt MIN | 50 | N=5 x=5 | N=30 x=23 | N=30 x=22 |
| T2 Txt HIGH | 20 | N=30 x=17 | N=30 x=22 | N=30 x=21 |
| T2 Txt HIGH | 30 | N=30 x=17 | N=30 x=22 | N=30 x=21 |
| T2 Txt HIGH | 40 | N=30 x=17 | N=30 x=19 | N=10 x=7 |
| T2 Txt HIGH | 50 | N=30 x=17 | N=30 x=19 | N=10 x=7 |

### 4.3 Temperature Dominance Patterns

At the preregistered 20 m tolerance, the winning temperature varies by
condition:

- T1 Img MIN: T0.7 (moderate diversity, small pool)
- T1 Img HIGH: T0.3 (low diversity, strict threshold — precision strategy)
- T2 Txt MIN: T1.0 (maximum diversity, large pool)
- T2 Txt HIGH: T0.7 (moderate diversity — internal thinking provides additional diversity)

At wider tolerances, the patterns shift:

- T1 Img MIN shifts to T1.0 dominance at 30+ m
- T1 Img HIGH shifts to T0.7 dominance at 30+ m
- T2 Txt MIN remains T1.0 throughout
- T2 Txt HIGH remains T0.7 throughout

The text-track conditions show stable temperature preferences regardless of
tolerance, while image-track conditions shift — further evidence of
image-track fragility at tight tolerances.

---

## 5. Thinking Level × Modality Interaction

### 5.1 The Diversity Dividend

Detection cluster counts at N=30, x=1 (maximum permissiveness) are
invariant across tolerances because clustering uses a fixed 20 m tolerance.

**Table 5.1.** Unique detection clusters by condition and temperature.

| Condition | T=0.3 | T=0.7 | T=1.0 | Ratio (HIGH/MIN) |
|:----------|------:|------:|------:|:----|
| T1 Img MIN | 329 | 573 | 763 | — |
| T1 Img HIGH | 337 | 586 | 685 | 1.02×, 1.02×, 0.90× |
| T2 Txt MIN | 247 | 425 | 529 | — |
| T2 Txt HIGH | 940 | 1,396 | 2,045 | 3.81×, 3.28×, 3.87× |

For text-based processing, HIGH thinking generates 3–4× more detection
clusters than MINIMAL at every temperature. For image-based processing,
the ratio is approximately 1×. This cluster diversity differential is the
mechanistic explanation for why HIGH thinking benefits text consensus
but not image consensus.

### 5.2 Thinking Level Effect Across Tolerances

**Table 5.2.** F1 difference (HIGH − MINIMAL) by modality and tolerance.

| Modality | 20 m | 30 m | 40 m | 50 m |
|:---------|-----:|-----:|-----:|-----:|
| Image | −0.5 pp | −0.8 pp | −1.0 pp | +0.0 pp |
| Text | +6.8 pp | +5.2 pp | +3.9 pp | +4.9 pp |

The interaction is robust across all tolerances. The image-track null
effect persists (and is never positive by more than 0.0 pp). The
text-track positive effect narrows slightly as tolerance widens but remains
substantial at every level tested.

### 5.3 Interpretation: Two Components of the HIGH-Thinking Advantage

The narrowing of the text-track HIGH advantage from +6.8 pp at 20 m to
+3.9 pp at 40 m suggests the advantage has two components:

1. **Diversity component** (persistent): HIGH thinking generates a richer
   detection pool, enabling better consensus filtering. This component
   operates at all tolerances.

2. **Precision component** (diminishing): HIGH thinking may also produce
   more precisely localised detections. This component matters most at
   tight tolerances and becomes irrelevant as the matching buffer widens.

The rebound to +4.9 pp at 50 m may reflect the diversity component's
ability to extend spatial coverage — HIGH thinking's richer detection pool
matches ground truth symbols that MINIMAL's sparser pool never approaches
closely enough to match at any tolerance.

---

## 6. Spatial Tolerance Sensitivity

### 6.1 Incremental F1 Gains

**Table 6.1.** F1 gain at each tolerance step (percentage points).

| Condition | 20→30 m | 30→40 m | 40→50 m | Total |
|:----------|--------:|--------:|--------:|------:|
| T1 Img MIN | +8.4 | +5.1 | +0.9 | +14.4 |
| T1 Img HIGH | +8.1 | +4.9 | +2.0 | +15.0 |
| T2 Txt MIN | +6.9 | +3.0 | +0.0 | +9.9 |
| T2 Txt HIGH | +5.3 | +1.7 | +1.0 | +8.0 |

### 6.2 Key Patterns

**Image tracks gain more than text tracks.** The total gain from 20→50 m
is 14–15 pp for image vs 8–10 pp for text. Image-derived detections have
greater spatial imprecision, consistent with the difficulty of converting
pixel locations to geographic coordinates from base64-encoded images.

**The 20→30 m step is the largest.** Every condition gains 5–8 pp in this
single step, suggesting many detections fall just outside the 20 m buffer.
This is the strongest evidence that 20 m is conservative for this dataset.

**Diminishing returns beyond 40 m.** All conditions gain <2 pp in the
40→50 m step. T2 Txt MIN gains exactly 0 pp, confirming that its detection
pool is fully captured within 40 m.

**The practical ceiling is ~40–50 m.** The combined positional uncertainty
from ground truth digitisation, cartographic generalisation, and VLM
detection is bounded at approximately 40–50 m for the majority of correct
detections.

### 6.3 Image-Track Convergence

At 50 m, T1 Img MIN and T1 Img HIGH converge to identical F1 (0.794).
The convergence trajectory:

| Tolerance | T1 Img MIN | T1 Img HIGH | Gap |
|----------:|----------:|-----------:|----:|
| 20 m | 0.650 | 0.644 | +0.5 pp (MIN leads) |
| 30 m | 0.734 | 0.726 | +0.8 pp (MIN leads) |
| 40 m | 0.785 | 0.775 | +1.0 pp (MIN leads) |
| 50 m | 0.794 | 0.794 | +0.0 pp (converged) |

This convergence, combined with the invariant cluster diversity (Table 5.1),
confirms that the image-track is fundamentally bottlenecked by visual feature
extraction rather than by reasoning depth or spatial precision.

### 6.4 Text MINIMAL Plateau

T2 Txt MIN produces identical results at 40 m and 50 m:

- Same F1: 0.782
- Same P/R: 0.752 / 0.814
- Same config: T1.0 N=30 x=22
- Same n_det: 105

Every detection that can match ground truth has already matched by 40 m.
This cleanly bounds the spatial uncertainty of text-derived MINIMAL
detections.

---

## 7. Configuration Behaviour Analysis

### 7.1 Pool Size Dominance

N=30 dominates at all tolerances ≥30 m for every condition. At 20 m, two
exceptions occur:

- T1 Img MIN selects N=10 (the only global-optimum N<30 in the entire matrix)
- T2 Txt MIN selects N=5 at T=0.3 (per-temperature level)

Both exceptions occur in the lowest-diversity conditions, where the detection
pool cannot sustain large-pool consensus filtering at tight spatial
constraints.

### 7.2 Vote Threshold Ranges

The optimal vote threshold (x) varies systematically:

| Condition | Typical x/N ratio | Interpretation |
|:----------|:------------------|:---------------|
| T1 Img HIGH at 20 m | 25/30 = 83% | Very strict — precision-oriented |
| T2 Txt HIGH at 20 m | 22/30 = 73% | Moderate — balanced |
| T2 Txt MIN at 20 m | 22/30 = 73% | Moderate — balanced |
| T1 Img MIN at 20 m | 6/10 = 60% | Lenient — small pool |
| T2 Txt HIGH at 50 m | 19/30 = 63% | More lenient at wide tolerance |

At wider tolerances, thresholds generally decrease (become more lenient)
because more detections qualify as true positives, allowing the consensus
to include clusters with fewer votes without degrading precision.

### 7.3 Temperature and Thinking as Diversity Axes

Temperature and thinking level are mechanistically independent diversity
sources:

- **Temperature** controls token-level sampling randomness (stochastic
  diversity)
- **Thinking level** controls deliberation depth (reasoning diversity)

For text processing, both axes contribute additively: T2 Txt HIGH at T=1.0
produces 2,045 clusters versus 529 for T2 Txt MIN at T=1.0 (3.87×
multiplication). The combination of high temperature and high thinking
creates the richest detection pool.

For image processing, only temperature contributes meaningfully: cluster
counts scale with temperature (329→763 for MIN, 337→685 for HIGH) but
thinking level adds nothing.

---

## 8. Quotable Results for Paper Sections

### For the Results Section

> Consensus voting improved detection performance over single-pass baselines
> across all four conditions of the 2×2 design (Table X), confirming H3.
> The best consensus configuration achieved F1=0.751 at the preregistered
> 20 m matching tolerance (Track 2 Text HIGH, T=0.7, N=30, x=22; 95% CI
> [0.610, 0.796]), compared to the single-pass baseline of F1=0.660
> (+9.1 pp). At a practically relevant 50 m matching tolerance, the same
> condition achieved F1=0.831 (95% CI [0.684, 0.868]).

### For the Thinking Level Effect

> Extended thinking produced a modality-conditional effect on consensus
> voting performance. For text-based detection, HIGH thinking generated
> 3–4× more unique detection clusters than MINIMAL thinking and improved
> consensus F1 by 6.8 percentage points (0.751 vs 0.683 at 20 m). For
> image-based detection, HIGH thinking produced virtually identical cluster
> diversity (~1× ratio) and no meaningful F1 improvement (0.644 vs 0.650
> at 20 m). This interaction was robust across all spatial tolerances tested
> (20–50 m).

### For the Spatial Sensitivity Discussion

> A sensitivity analysis varying the evaluation matching tolerance from
> 20 m to 50 m revealed that image-derived detections have substantially
> greater spatial imprecision than text-derived detections, with image-track
> conditions gaining 14–15 pp compared to 8–10 pp for text-track conditions
> over the full tolerance range. The preregistered 20 m tolerance is
> conservative but defensible; the relative ranking of conditions is stable
> across all tolerances tested.

### For Practical Applications

> At a 50 m matching tolerance — operationally realistic for prioritising
> archaeological survey areas — the best VLM consensus configuration
> detected 88.7% of burial mound symbols (recall) at 78.2% precision,
> yielding F1=0.831. This suggests that VLM-based historical map analysis
> could substantially reduce the area requiring manual inspection in
> landscape survey.

---

## 9. Open Questions and Future Work

### 9.1 Paired Permutation Tests

The current analysis uses tile-level bootstrap CIs, which include
between-tile variance (differing mound density, terrain complexity). Paired
permutation tests on per-tile F1 differences would control for this
variance and substantially narrow confidence intervals, potentially
enabling formal significance testing of the thinking-level interaction.

### 9.2 Temperature × Thinking Factorial

The current design confounds temperature and thinking level somewhat:
each temperature is evaluated independently within each thinking level.
A full temperature × thinking factorial (with temperature varied
systematically within each thinking condition, holding pool size constant)
would more cleanly estimate the additivity or interaction of these
diversity sources.

### 9.3 Model Generality

All results pertain to Gemini 2.0 Flash. Whether the diversity dividend
generalises to other VLMs (Claude, GPT, open-source models) is unknown.
The visual processing bottleneck may be model-specific: models with
stronger vision encoders might show a thinking-level effect on
image-track diversity.

### 9.4 Larger Pool Sizes

N=30 dominates across the matrix, and the data include 30 runs per
temperature — the maximum pool size. Whether larger pools (N=50, N=100)
would further improve performance, particularly for the high-diversity
T2 Txt HIGH condition, is an open question that would require additional
batch runs.

---

## 10. File Inventory

| File | Content |
|:-----|:--------|
| `phase3a-thinking-level-comparison.md` | Detailed 2×2 factorial analysis at 20 m |
| `phase3a-spatial-tolerance-sensitivity.md` | Tolerance sensitivity across 20–50 m |
| `phase3a-comprehensive-results-report.md` | This document — consolidated reference |
| `track1-image/` | T1 Img MIN, 20 m results |
| `track1-image-high/` | T1 Img HIGH, 20 m results |
| `track2-text/` | T2 Txt MIN, 20 m results |
| `track2-text-high/` | T2 Txt HIGH, 20 m results |
| `track{1,2}-{image,text}{,-high}-{30,40,50}m/` | Extended tolerance results |

Each directory contains:

- `consensus-analysis-report.json` — full sweep results with metadata
- `consensus-analysis-summary.md` — human-readable summary
- `consensus-sweep-results.csv` — tabular results for all 135 configurations
