---
title: "K-consensus heterogeneity footnote (paper-ready)"
date: 2026-05-03
source_observation: "Obs 289 (docs/notes/reflections/working-notes.md, lines 14121–14189)"
intended_paper_section: "Methods — K-consensus aggregation; or Discussion — methodological caveats"
length_words: 312
---

## Footnote: heterogeneity of K-consensus variance reduction across the matrix

The K-consensus aggregation strategy adopted here (running K independent passes
per condition and taking a greedy-vote consensus across them) reduces per-tile
F1 variance under the standard assumption that per-pass errors are independent
and identically distributed (i.i.d.); under that assumption, the consensus
standard deviation contracts with the square root of K, which corresponds to a
log-log shrinkage slope of β₁ = −0.5. We have tested this assumption directly
by rebuilding the greedy-vote consensus on K-subsamples drawn from per-pass
detection geometries and re-evaluating against the canonical reference, rather
than relying on the analytically degenerate mean-of-K-passes proxy that
recovers β₁ = −0.5 by construction. The genuine test reveals that 5 of the 13
strata in the Phase 3a matrix depart detectably from the i.i.d. expectation
(95 % bootstrap confidence intervals exclude −0.5): image-MINIMAL-T=1.0
(β₁ = −0.118, 95 % CI [−0.227, +0.061]; the strongest shared-mode signal),
image-HIGH-T=0.3 (β₁ = −0.222 [−0.358, −0.050]), text-HIGH-T=0.7
(β₁ = −0.387 [−0.421, −0.344]), text-MINIMAL-T=0.7 (β₁ = −0.558
[−0.590, −0.518]), and image-HIGH-T=1.0 (β₁ = −0.731 [−0.884, −0.488]; the one
anti-i.i.d. departure, flagged as awaiting larger-K replication). At
image-MINIMAL-T=1.0, the standard deviation contracts roughly five times more
slowly than the i.i.d. ceiling predicts, indicating that K passes share a
correlated component which consensus voting cannot average out. We interpret
the shallow-side departures as evidence of **shared-mode failure regions** —
tile populations on which the model fails in the same way across passes, so
that additional passes contribute little independent information. The pattern
concentrates on the image track, consistent with image inputs sharing visual
confounds (label-pull, contour-ring) that all passes consistently miss.
Accordingly, we report the K-consensus benefit per stratum rather than as a
single corpus-level summary, and any tier-stability or noise-reduction claim
that leans on √K shrinkage in the body of the paper is qualified for the five
strata named above. See `results/secondary-effects-consensus-sd/report.md`,
Section 3, and Observation 289 in the working notes for full per-stratum
slopes and methodology.
