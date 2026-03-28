# Phase 3c H9 Diversity: Cross-Track Comparison

## Context

Hypothesis H9 predicted that at least one diversity mechanism (text
rephrasing, hard negative image rotation, temperature variation, or their
combination) would improve consensus voting F1 compared to fully identical
passes. Phase 3c tested this across two tracks:

- **Track 1 (Image)**: 5 conditions × 5 sub-conditions × 5 runs = 125 units
- **Track 2 (Text-Only)**: 4 conditions × 5 sub-conditions × 5 runs = 100 units
  (Condition C excluded — image diversity is inapplicable to text-only)

Both tracks used MINIMAL thinking, T=0.7, N=5 pool size, and 20m spatial
tolerance. Analysis via paired permutation test (10,000 iterations,
two-sided, α=0.05).

## Combined Results

### Track 1 (Image) — All conditions at optimal threshold x=3

| Condition | Diversity | F1 | ±SD | ΔF1 vs A | p-value |
|-----------|-----------|-----|------|----------|---------|
| A | None (baseline) | 0.664 | 0.015 | — | — |
| B | Text | 0.668 | 0.013 | +0.004 | 0.689 |
| C | Image (HN rotation) | 0.671 | 0.018 | +0.007 | 0.621 |
| D | Temperature | 0.669 | 0.014 | +0.005 | 0.375 |
| E | Combined | 0.671 | 0.008 | +0.007 | 0.375 |

### Track 2 (Text-Only) — All conditions at optimal threshold x=4

| Condition | Diversity | F1 | ±SD | ΔF1 vs A | p-value |
|-----------|-----------|-----|------|----------|---------|
| A | None (baseline) | 0.716 | 0.012 | — | — |
| B | Text | 0.686 | 0.005 | −0.030 | 0.061 |
| D | Temperature | 0.730 | 0.008 | +0.014 | 0.181 |
| E | Combined (text+temp) | 0.694 | 0.011 | −0.022 | 0.061 |

## Cross-Track Findings

### 1. Consistent null result across modalities

Neither track shows a statistically significant improvement from any
diversity mechanism. H9 is rejected: parametric diversity (rephrasing,
example rotation, temperature variation) does not improve consensus
accuracy beyond identical passes, for either the image-using or text-only
detection pipeline.

### 2. Track 2 trends worse, not better

Track 1 shows uniformly positive (but non-significant) ΔF1 values
(+0.004 to +0.007). Track 2 shows a mixed pattern: text diversity (B)
and combined diversity (E) trend *worse* than baseline (−0.030 and
−0.022), approaching significance at p=0.061. Temperature diversity (D)
trends slightly positive (+0.014, p=0.181).

**Interpretation**: Text rephrasing on Track 2 may introduce semantic
drift that degrades detection quality. The text-only prompt was already
optimised through Phase 2 configuration exploration; paraphrasing
disrupts the calibrated wording without adding complementary information.
The image track may be more robust to text variation because the image
content provides a stable anchor.

### 3. Baseline performance differs between tracks

Track 2 text-only (F1=0.716) outperforms Track 1 image-using (F1=0.664)
at baseline, consistent with the modality findings from the main
consensus analysis (Group 2 pairwise tests). This gap persists across
all diversity conditions, confirming that the text-only pipeline is
inherently more accurate at MINIMAL thinking.

### 4. Variance stabilisation did not replicate at scale

The pilot (60 tiles) found that Condition C on Track 1 had remarkably
low variance (SD=0.008, 5× reduction vs baseline, p=0.010 F-test — see
Obs 148). At full scale (487 tiles), Condition C shows SD=0.018 vs
baseline SD=0.015 — slightly *higher*, not lower. The pilot finding was
an artefact of the small evaluation set (Obs 192).

## Theoretical Interpretation

### Why diversity fails where architecture succeeds

The null H9 result contrasts sharply with the large positive effect of
the proposer-verifier architecture (H2: Group 1 pairwise tests, 7/8
significant, ΔF1 up to +0.278). Both strategies aim to reduce correlated
errors, but through different mechanisms:

- **Parametric diversity (H9)**: Varies input parameters (prompt wording,
  examples, temperature) hoping to produce decorrelated error profiles
  across voting passes. This fails because the VLM's error structure is
  dominated by the task itself (which symbols look like mounds), not by
  prompt phrasing or temperature.

- **Structural diversity (H2)**: Decomposes the task into fundamentally
  different operations — proposing (high recall, low precision) and
  verifying (high specificity). This succeeds because the two stages
  have orthogonal error modes: the proposer flags everything suspicious,
  the verifier rejects non-mound symbols.

This distinction between *parametric* and *structural* diversity is a
key methodological contribution. It implies that for VLM-based detection
tasks, ensemble improvements should come from task decomposition (H2),
not from input perturbation (H9).

### Connection to the diversity dividend (Obs 141)

The "diversity dividend" discovered in Obs 141 — where HIGH thinking
improved consensus despite hurting individual-pass efficiency — operates
through a different mechanism than H9. HIGH thinking increases the
*variance of detection patterns* because the model reasons differently
each time, producing genuinely diverse error profiles. H9's parametric
manipulations (different wording of the same instruction, different
example images, slightly different temperature) do not produce the same
depth of behavioural variation. The VLM's detection behaviour is
fundamentally insensitive to these surface-level perturbations.

## Summary for Paper

H9 is not supported. Across 225 experimental units spanning two tracks
and five diversity conditions, no manipulation significantly improved
consensus voting accuracy. The text-only track showed marginally negative
effects from text rephrasing (p=0.061), suggesting that prompt
optimisation and diversity may be antagonistic. The variance
stabilisation secondary finding from the pilot (Obs 148) did not
replicate at scale (Obs 192).

The null result is informative: it demonstrates that the detection
pipeline's error structure is task-determined, not prompt-determined,
and that meaningful improvement requires structural changes to the
pipeline architecture (H2) rather than parametric perturbation of
inputs (H9).
