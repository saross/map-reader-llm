# Leaderboard (MCC tiers) — 20m buffer

**Generated**: 2026-05-06T09:33:38.349602+00:00
**Tiering metric**: MCC
**FDR q**: 0.05
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 29 in 7 tier(s)

## Tier 1 (MCC: 0.727–0.761)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h11-pvd-pro-high-image-n5 | greedy | 2 | image | 5 | 3 | 0.761 | 0.700 | [0.667, 0.732] | 0.673 | 0.729 |
| 2 | scale4-optimal-487 | greedy | 2 | image | 10 | 6 | 0.746 | 0.742 | [0.713, 0.771] | 0.772 | 0.715 |
| 3 | h11-pvd-pro-high-text-n5 | greedy | 2 | text | 10 | 6 | 0.727 | 0.836 | [0.810, 0.859] | 0.927 | 0.761 |

## Tier 2 (MCC: 0.620–0.682)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 4 | p3a-high-image-t0.3 | greedy | 2 | image | 10 | 9 | 0.682 | 0.731 | [0.698, 0.757] | 0.806 | 0.669 |
| 5 | h11-pvd-flash-high-image-n5 | greedy | 2 | image | 10 | 7 | 0.676 | 0.750 | [0.722, 0.781] | 0.778 | 0.724 |
| 6 | p3a-high-image-t1.0 | greedy | 2 | image | 10 | 6 | 0.644 | 0.735 | [0.707, 0.765] | 0.737 | 0.733 |
| 7 | h11-pvd-flash-high-text-n5 | greedy | 2 | text | 30 | 26 | 0.620 | 0.814 | [0.792, 0.839] | 0.834 | 0.795 |

## Tier 3 (MCC: 0.565–0.587)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 8 | p3a-high-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.587 | 0.789 | [0.763, 0.811] | 0.814 | 0.765 |
| 9 | p3a-high-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.587 | 0.789 | [0.763, 0.811] | 0.814 | 0.765 |
| 10 | p3a-high-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.575 | 0.773 | [0.744, 0.800] | 0.792 | 0.754 |
| 11 | p3a-high-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.575 | 0.773 | [0.744, 0.800] | 0.792 | 0.754 |
| 12 | h11-n1-pro-image-high-t0 | greedy | 2 | image | 3 | 3 | 0.565 | 0.552 | [0.517, 0.587] | 0.475 | 0.660 |

## Tier 4 (MCC: 0.415–0.503)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 13 | h11-e47-propose-brief | greedy | 2 | text | 5 | 5 | 0.503 | 0.714 | [0.678, 0.745] | 0.694 | 0.736 |
| 14 | p3a-high-image-t0.0 | greedy | 2 | image | 3 | 1 | 0.484 | 0.488 | [0.457, 0.520] | 0.377 | 0.694 |
| 15 | p3a-high-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.451 | 0.605 | [0.565, 0.642] | 0.479 | 0.821 |
| 16 | p3a-min-image-t1.0 | greedy | 2 | image | 10 | 8 | 0.441 | 0.646 | [0.613, 0.676] | 0.625 | 0.669 |
| 17 | p3a-minimal-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.415 | 0.667 | [0.631, 0.705] | 0.597 | 0.754 |
| 18 | p3a-minimal-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.415 | 0.667 | [0.631, 0.705] | 0.597 | 0.754 |

## Tier 5 (MCC: 0.380–0.404)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 19 | h11-pvd-image-n5 | greedy | 2 | image | 10 | 8 | 0.404 | 0.680 | [0.650, 0.711] | 0.640 | 0.726 |
| 20 | h11-n1-pro-text-high-t0 | greedy | 2 | text | 3 | 3 | 0.395 | 0.567 | [0.530, 0.603] | 0.441 | 0.793 |
| 21 | h11-pvd-flash-minimal-text-n30-t07 | greedy | 2 | text | 30 | 29 | 0.380 | 0.661 | [0.627, 0.694] | 0.602 | 0.733 |

## Tier 6 (MCC: 0.311–0.349)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 22 | h11-n1-image-t03 | greedy | 2 | image | 3 | 3 | 0.349 | 0.677 | [0.648, 0.707] | 0.598 | 0.779 |
| 23 | p3a-min-image-t0.3 | greedy | 2 | image | 10 | 10 | 0.340 | 0.660 | [0.629, 0.690] | 0.607 | 0.722 |
| 24 | h11-pvd-text-n10 | greedy | 2 | text | 10 | 10 | 0.316 | 0.619 | [0.582, 0.659] | 0.528 | 0.747 |
| 25 | p3a-minimal-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.311 | 0.642 | [0.606, 0.679] | 0.551 | 0.770 |
| 26 | p3a-minimal-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.311 | 0.642 | [0.606, 0.679] | 0.551 | 0.770 |

## Tier 7 (MCC: 0.170–0.223)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 27 | p3a-minimal-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.223 | 0.593 | [0.547, 0.631] | 0.458 | 0.841 |
| 28 | h11-n1-image-t0 | greedy | 2 | image | 3 | 2 | 0.214 | 0.629 | [0.600, 0.657] | 0.515 | 0.807 |
| 29 | h11-n1-brief-text-t03 | greedy | 2 | text | 3 | 3 | 0.170 | 0.591 | [0.550, 0.634] | 0.457 | 0.835 |
