# Leaderboard (MCC tiers) — 50m buffer

**Generated**: 2026-04-26T07:18:22.527884+00:00
**Tiering metric**: MCC
**FDR q**: 0.05
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 29 in 7 tier(s)

## Tier 1 (MCC: 0.727–0.761)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h11-pvd-pro-high-image-n5 | greedy | 2 | image | 5 | 3 | 0.761 | 0.865 | [0.839, 0.893] | 0.832 | 0.901 |
| 2 | scale4-optimal-487 | greedy | 2 | image | 10 | 6 | 0.745 | 0.831 | [0.796, 0.861] | 0.864 | 0.800 |
| 3 | h11-pvd-pro-high-text-n5 | greedy | 2 | text | 10 | 6 | 0.727 | 0.854 | [0.817, 0.885] | 0.947 | 0.777 |

## Tier 2 (MCC: 0.620–0.682)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 4 | p3a-high-image-t0.3 | greedy | 2 | image | 10 | 9 | 0.682 | 0.794 | [0.758, 0.829] | 0.875 | 0.726 |
| 5 | h11-pvd-flash-high-image-n5 | greedy | 2 | image | 10 | 7 | 0.676 | 0.824 | [0.788, 0.857] | 0.854 | 0.795 |
| 6 | p3a-high-image-t1.0 | greedy | 2 | image | 10 | 6 | 0.644 | 0.818 | [0.784, 0.849] | 0.820 | 0.816 |
| 7 | h11-pvd-flash-high-text-n5 | greedy | 2 | text | 30 | 26 | 0.620 | 0.826 | [0.793, 0.858] | 0.846 | 0.807 |

## Tier 3 (MCC: 0.565–0.587)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 8 | p3a-high-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.587 | 0.810 | [0.774, 0.846] | 0.836 | 0.786 |
| 9 | p3a-high-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.587 | 0.810 | [0.774, 0.846] | 0.836 | 0.786 |
| 10 | p3a-high-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.575 | 0.789 | [0.749, 0.825] | 0.809 | 0.770 |
| 11 | p3a-high-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.575 | 0.789 | [0.749, 0.825] | 0.809 | 0.770 |
| 12 | h11-n1-pro-image-high-t0 | greedy | 2 | image | 3 | 3 | 0.565 | 0.660 | [0.609, 0.703] | 0.568 | 0.788 |

## Tier 4 (MCC: 0.415–0.503)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 13 | h11-e47-propose-brief | greedy | 2 | text | 5 | 5 | 0.503 | 0.730 | [0.683, 0.772] | 0.709 | 0.752 |
| 14 | p3a-high-image-t0.0 | greedy | 2 | image | 3 | 1 | 0.484 | 0.593 | [0.546, 0.645] | 0.458 | 0.844 |
| 15 | p3a-high-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.451 | 0.632 | [0.571, 0.688] | 0.501 | 0.858 |
| 16 | p3a-min-image-t1.0 | greedy | 2 | image | 10 | 8 | 0.441 | 0.735 | [0.696, 0.770] | 0.710 | 0.761 |
| 17 | p3a-minimal-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.415 | 0.675 | [0.622, 0.724] | 0.605 | 0.763 |
| 18 | p3a-minimal-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.415 | 0.675 | [0.622, 0.724] | 0.605 | 0.763 |

## Tier 5 (MCC: 0.380–0.404)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 19 | h11-pvd-image-n5 | greedy | 2 | image | 10 | 8 | 0.404 | 0.747 | [0.706, 0.784] | 0.702 | 0.798 |
| 20 | h11-n1-pro-text-high-t0 | greedy | 2 | text | 3 | 3 | 0.395 | 0.603 | [0.548, 0.655] | 0.469 | 0.844 |
| 21 | h11-pvd-flash-minimal-text-n30-t07 | greedy | 2 | text | 30 | 29 | 0.380 | 0.669 | [0.621, 0.715] | 0.609 | 0.743 |

## Tier 6 (MCC: 0.311–0.348)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 22 | h11-n1-image-t03 | greedy | 2 | image | 3 | 3 | 0.348 | 0.752 | [0.715, 0.788] | 0.665 | 0.867 |
| 23 | p3a-min-image-t0.3 | greedy | 2 | image | 10 | 10 | 0.339 | 0.719 | [0.674, 0.759] | 0.661 | 0.786 |
| 24 | h11-pvd-text-n10 | greedy | 2 | text | 10 | 10 | 0.316 | 0.628 | [0.573, 0.681] | 0.536 | 0.759 |
| 25 | p3a-minimal-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.311 | 0.654 | [0.602, 0.700] | 0.561 | 0.784 |
| 26 | p3a-minimal-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.311 | 0.654 | [0.602, 0.700] | 0.561 | 0.784 |

## Tier 7 (MCC: 0.170–0.223)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 27 | p3a-minimal-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.223 | 0.613 | [0.556, 0.669] | 0.473 | 0.869 |
| 28 | h11-n1-image-t0 | greedy | 2 | image | 3 | 2 | 0.214 | 0.719 | [0.678, 0.754] | 0.589 | 0.922 |
| 29 | h11-n1-brief-text-t03 | greedy | 2 | text | 3 | 3 | 0.170 | 0.605 | [0.545, 0.660] | 0.469 | 0.855 |
