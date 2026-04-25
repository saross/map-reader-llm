# Leaderboard (MCC tiers) — 30m buffer

**Generated**: 2026-04-25T14:30:35.248767+00:00
**Tiering metric**: MCC
**FDR q**: 0.05
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 29 in 7 tier(s)

## Tier 1 (MCC: 0.727–0.761)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h11-pvd-pro-high-image-n5 | greedy | 2 | image | 5 | 3 | 0.761 | 0.821 | [0.787, 0.851] | 0.790 | 0.855 |
| 2 | scale4-optimal-487 | greedy | 2 | image | 10 | 6 | 0.745 | 0.804 | [0.766, 0.838] | 0.836 | 0.775 |
| 3 | h11-pvd-pro-high-text-n5 | greedy | 2 | text | 10 | 6 | 0.727 | 0.851 | [0.813, 0.883] | 0.944 | 0.775 |

## Tier 2 (MCC: 0.620–0.682)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 4 | p3a-high-image-t0.3 | greedy | 2 | image | 10 | 9 | 0.682 | 0.784 | [0.748, 0.818] | 0.864 | 0.717 |
| 5 | h11-pvd-flash-high-image-n5 | greedy | 2 | image | 10 | 7 | 0.676 | 0.809 | [0.773, 0.843] | 0.840 | 0.782 |
| 6 | p3a-high-image-t1.0 | greedy | 2 | image | 10 | 6 | 0.644 | 0.788 | [0.751, 0.822] | 0.790 | 0.786 |
| 7 | h11-pvd-flash-high-text-n5 | greedy | 2 | text | 30 | 26 | 0.620 | 0.826 | [0.793, 0.858] | 0.846 | 0.807 |

## Tier 3 (MCC: 0.565–0.587)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 8 | p3a-high-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.587 | 0.810 | [0.774, 0.846] | 0.836 | 0.786 |
| 9 | p3a-high-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.587 | 0.810 | [0.774, 0.846] | 0.836 | 0.786 |
| 10 | p3a-high-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.575 | 0.789 | [0.749, 0.825] | 0.809 | 0.770 |
| 11 | p3a-high-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.575 | 0.789 | [0.749, 0.825] | 0.809 | 0.770 |
| 12 | h11-n1-pro-image-high-t0 | greedy | 2 | image | 3 | 3 | 0.565 | 0.618 | [0.569, 0.665] | 0.531 | 0.738 |

## Tier 4 (MCC: 0.415–0.503)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 13 | h11-e47-propose-brief | greedy | 2 | text | 5 | 5 | 0.503 | 0.730 | [0.683, 0.772] | 0.709 | 0.752 |
| 14 | p3a-high-image-t0.0 | greedy | 2 | image | 3 | 1 | 0.484 | 0.550 | [0.497, 0.602] | 0.424 | 0.782 |
| 15 | p3a-high-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.451 | 0.627 | [0.565, 0.683] | 0.497 | 0.851 |
| 16 | p3a-min-image-t1.0 | greedy | 2 | image | 10 | 8 | 0.441 | 0.715 | [0.674, 0.751] | 0.691 | 0.740 |
| 17 | p3a-minimal-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.415 | 0.673 | [0.620, 0.722] | 0.603 | 0.761 |
| 18 | p3a-minimal-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.415 | 0.673 | [0.620, 0.722] | 0.603 | 0.761 |

## Tier 5 (MCC: 0.380–0.404)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 19 | h11-pvd-image-n5 | greedy | 2 | image | 10 | 8 | 0.404 | 0.728 | [0.685, 0.765] | 0.684 | 0.777 |
| 20 | h11-n1-pro-text-high-t0 | greedy | 2 | text | 3 | 3 | 0.395 | 0.593 | [0.539, 0.644] | 0.461 | 0.830 |
| 21 | h11-pvd-flash-minimal-text-n30-t07 | greedy | 2 | text | 30 | 29 | 0.380 | 0.669 | [0.621, 0.715] | 0.609 | 0.743 |

## Tier 6 (MCC: 0.311–0.348)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 22 | h11-n1-image-t03 | greedy | 2 | image | 3 | 3 | 0.348 | 0.737 | [0.696, 0.774] | 0.651 | 0.848 |
| 23 | p3a-min-image-t0.3 | greedy | 2 | image | 10 | 10 | 0.339 | 0.710 | [0.667, 0.751] | 0.654 | 0.777 |
| 24 | h11-pvd-text-n10 | greedy | 2 | text | 10 | 10 | 0.316 | 0.628 | [0.573, 0.681] | 0.536 | 0.759 |
| 25 | p3a-minimal-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.311 | 0.648 | [0.596, 0.694] | 0.556 | 0.777 |
| 26 | p3a-minimal-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.311 | 0.648 | [0.596, 0.694] | 0.556 | 0.777 |

## Tier 7 (MCC: 0.170–0.223)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 27 | p3a-minimal-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.223 | 0.598 | [0.542, 0.656] | 0.462 | 0.848 |
| 28 | h11-n1-image-t0 | greedy | 2 | image | 3 | 2 | 0.214 | 0.692 | [0.650, 0.728] | 0.567 | 0.887 |
| 29 | h11-n1-brief-text-t03 | greedy | 2 | text | 3 | 3 | 0.170 | 0.601 | [0.542, 0.655] | 0.465 | 0.848 |
