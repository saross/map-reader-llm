# Phase 2c Carry-Forward Parameters

**Created**: 2026-02-09
**Source**: Phase 2c analysis (Track 1: `results/phase2c-track1-image-analysis.md`)
**Carries forward to**: Phase 2d (H5 Negative Text Treatment)

## Context

Phase 2c tested H8 (Library Composition) across 5 conditions with K=10
independent runs each, using the carry-forward parameters from Phase 2b
(T=0.0, brief-text-image). Analysis used bootstrapped 95% CIs (n=1000)
with Benjamini-Hochberg FDR correction at q=0.05.

**Track 2 (text-only) was not executed.** Library composition is an
inherently visual factor — the library examples contain annotated map
images. Text-only prompts receive only example labels, not the images
themselves, so all library conditions collapse to functionally identical
prompts. This was confirmed during pre-flight when a diagnostic check
showed text-only configs produced identical detection counts across all
conditions. Phase 2c therefore ran Track 1 (image-using) only.

## Results Summary

### Track 1: Image-Using (brief-text-image, T=0.0)

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| canonical | 0.528 | [0.403, 0.628] | 0.474 | 0.596 |
| scale-4 | 0.564 | [0.446, 0.658] | 0.479 | 0.684 |
| scale-8 | 0.570 | [0.460, 0.663] | 0.490 | 0.681 |
| pure-positive-canon | 0.603 | [0.490, 0.695] | 0.530 | 0.699 |
| **plus-hp** | **0.609** | [0.485, 0.701] | 0.524 | 0.726 |

**FDR-significant comparisons**: 0/10. One comparison (canonical vs
pure-positive-canon) was initially significant (p<0.05) but did not
survive FDR correction.

### Planned Contrasts

| Contrast | Comparison | ΔF1 | 95% CI | Interpretation |
|----------|-----------|----:|:------:|----------------|
| C1 | pure-positive-canon → canonical | −0.075 | [−0.149, −0.011] | Removing negatives helps (trend) |
| C2 | canonical → +HP | +0.081 | [−0.001, +0.169] | Hard positives help (trend) |
| B1 | +HP vs scale-4 | +0.045 | [−0.026, +0.114] | HP-only ≈ balanced HP+HN |
| S1 | scale-4 → scale-8 | +0.006 | [−0.051, +0.066] | No scaling effect |

## Carry-Forward Decision

**plus-hp (4 Canon+, 2 Canon−, 4 HP, 0 HN, 3 Null = 13 examples)
selected as the optimal library for subsequent phases.**

### Decision Rule Applied

The preregistered decision rule states: "Rank by F1; if best differs from
canonical by < 0.02, prefer canonical for simplicity." The difference
between plus-hp (0.609) and canonical (0.528) is +0.081 — well outside
the 0.02 simplicity threshold. plus-hp is therefore selected.

### Mechanism

The improvement from canonical to plus-hp is driven primarily by recall
(+0.130, from 0.596 to 0.726) with modest precision improvement (+0.050,
from 0.474 to 0.524). Adding hard positive examples helps the model
recognise more mounds without proportionally increasing false positives.
The canonical negatives in the library appear to have a weak negative
effect (pure-positive-canon outperforms canonical), suggesting the model
may be over-attending to negative examples.

### Caveats

No pairwise differences are statistically significant after FDR correction.
The near-determinism at T=0.0 means most runs within a condition produce
identical outputs (e.g., canonical had 9/10 runs with F1=0.5297). The
between-run variance is near zero, so bootstrap CIs are driven entirely by
between-tile variance, making it difficult to achieve significance. The
carry-forward decision is based on the point estimate ranking, which is
consistent across all planned contrasts and aligns with domain expectations
(more positive examples = better performance).

## Fixed Parameters for Phase 2d

| Parameter | Track 1 (image) | Source |
|-----------|-----------------|--------|
| M/E | brief-text-image | Phase 2a |
| Temperature | 0.0 | Phase 2b |
| Library | plus-hp | Phase 2c |
| Ordering | Canonical-first | Preregistered default |

## Key Observations

- **Library composition shows a directional effect but not a significant
  one.** The gradient is consistent: more positive examples = better
  performance. But the effect size (ΔF1 ≈ 0.08) is smaller than the
  temperature effect (ΔF1 ≈ 0.10-0.12 from Phase 2b).

- **Negative examples may hurt.** Pure-positive-canon outperforms
  canonical by 0.075 F1, driven by +0.103 recall. This suggests the 2
  canonical negative examples may distract the model from detection.

- **Hard positives are more valuable than hard negatives.** plus-hp
  (4 HP, 0 HN) outperforms scale-4 (2 HP, 2 HN) despite identical
  library size (13 examples each), suggesting that at matched size,
  hard positive examples contribute more than hard negatives.

- **Scaling shows diminishing returns.** scale-4 and scale-8 are nearly
  identical (ΔF1 = 0.006), indicating that adding more balanced hard
  examples beyond 4+4 does not improve performance.

- **Near-determinism at T=0.0 limits statistical power.** Future phases
  may benefit from running at T=0.3 for variance estimation, even if
  T=0.0 remains the operational setting.

## Text-Only Track Status

Track 2 (text-only) was not executed for Phase 2c because library
composition is inherently visual. The text-only carry-forward from
Phase 2b (T=0.0, brief-text) remains unchanged. The text-only track
will resume in Phase 2d (H5 Negative Text Treatment), where the factor
being tested (negative text elaboration) applies to text-based prompts.

## References

- Track 1 analysis: `results/phase2c-track1-image-analysis.md`
- Track 1 per-run metrics: `outputs/phase2c/track1-image/per_run_metrics.csv`
- Phase 2c Track 1 YAML: `studies/phase2c-h8-library.yaml`
- Phase 2b carry-forward: `results/phase2b-carry-forward-parameters.md` (retest-era, 340-tile K=3; supersedes the archived pre-retest pilot at `archive/outputs-pre-retest-60-tile/phase2b/`)
- Decision 11 (Scale-16/32 deferral): `docs/methodology/preregistration/protocol-errata.md`
