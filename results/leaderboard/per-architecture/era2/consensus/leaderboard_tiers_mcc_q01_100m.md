# Leaderboard (MCC tiers) — 100m buffer

**Generated**: 2026-04-25T14:30:35.719533+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 29 in 5 tier(s)

## Tier 1 (MCC: 0.676–0.761)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h11-pvd-pro-high-image-n5 | greedy | 2 | image | 5 | 3 | 0.761 | 0.885 | [0.860, 0.909] | 0.851 | 0.922 |
| 2 | scale4-optimal-487 | greedy | 2 | image | 10 | 6 | 0.745 | 0.835 | [0.801, 0.865] | 0.869 | 0.805 |
| 3 | h11-pvd-pro-high-text-n5 | greedy | 2 | text | 10 | 6 | 0.727 | 0.859 | [0.823, 0.890] | 0.952 | 0.782 |
| 4 | p3a-high-image-t0.3 | greedy | 2 | image | 10 | 9 | 0.682 | 0.796 | [0.759, 0.833] | 0.878 | 0.729 |
| 5 | h11-pvd-flash-high-image-n5 | greedy | 2 | image | 10 | 7 | 0.676 | 0.829 | [0.793, 0.858] | 0.859 | 0.800 |

## Tier 2 (MCC: 0.565–0.644)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 6 | p3a-high-image-t1.0 | greedy | 2 | image | 10 | 6 | 0.644 | 0.830 | [0.797, 0.861] | 0.831 | 0.828 |
| 7 | h11-pvd-flash-high-text-n5 | greedy | 2 | text | 30 | 26 | 0.620 | 0.826 | [0.793, 0.858] | 0.846 | 0.807 |
| 8 | p3a-high-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.587 | 0.810 | [0.774, 0.846] | 0.836 | 0.786 |
| 9 | p3a-high-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.587 | 0.810 | [0.774, 0.846] | 0.836 | 0.786 |
| 10 | p3a-high-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.575 | 0.789 | [0.749, 0.825] | 0.809 | 0.770 |
| 11 | p3a-high-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.575 | 0.789 | [0.749, 0.825] | 0.809 | 0.770 |
| 12 | h11-n1-pro-image-high-t0 | greedy | 2 | image | 3 | 3 | 0.565 | 0.670 | [0.619, 0.714] | 0.576 | 0.800 |

## Tier 3 (MCC: 0.395–0.503)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 13 | h11-e47-propose-brief | greedy | 2 | text | 5 | 5 | 0.503 | 0.732 | [0.686, 0.773] | 0.712 | 0.754 |
| 14 | p3a-high-image-t0.0 | greedy | 2 | image | 3 | 1 | 0.484 | 0.602 | [0.552, 0.653] | 0.464 | 0.855 |
| 15 | p3a-high-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.451 | 0.636 | [0.575, 0.694] | 0.503 | 0.862 |
| 16 | p3a-min-image-t1.0 | greedy | 2 | image | 10 | 8 | 0.441 | 0.739 | [0.701, 0.775] | 0.715 | 0.765 |
| 17 | p3a-minimal-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.415 | 0.675 | [0.622, 0.724] | 0.605 | 0.763 |
| 18 | p3a-minimal-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.415 | 0.675 | [0.622, 0.724] | 0.605 | 0.763 |
| 19 | h11-pvd-image-n5 | greedy | 2 | image | 10 | 8 | 0.404 | 0.751 | [0.710, 0.788] | 0.707 | 0.802 |
| 20 | h11-n1-pro-text-high-t0 | greedy | 2 | text | 3 | 3 | 0.395 | 0.608 | [0.552, 0.658] | 0.472 | 0.851 |

## Tier 4 (MCC: 0.311–0.380)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 21 | h11-pvd-flash-minimal-text-n30-t07 | greedy | 2 | text | 30 | 29 | 0.380 | 0.669 | [0.621, 0.715] | 0.609 | 0.743 |
| 22 | h11-n1-image-t03 | greedy | 2 | image | 3 | 3 | 0.348 | 0.760 | [0.722, 0.795] | 0.672 | 0.876 |
| 23 | p3a-min-image-t0.3 | greedy | 2 | image | 10 | 10 | 0.339 | 0.723 | [0.680, 0.762] | 0.665 | 0.791 |
| 24 | h11-pvd-text-n10 | greedy | 2 | text | 10 | 10 | 0.316 | 0.628 | [0.573, 0.681] | 0.536 | 0.759 |
| 25 | p3a-minimal-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.311 | 0.654 | [0.602, 0.700] | 0.561 | 0.784 |
| 26 | p3a-minimal-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.311 | 0.654 | [0.602, 0.700] | 0.561 | 0.784 |

## Tier 5 (MCC: 0.170–0.223)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 27 | p3a-minimal-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.223 | 0.616 | [0.560, 0.671] | 0.476 | 0.874 |
| 28 | h11-n1-image-t0 | greedy | 2 | image | 3 | 2 | 0.214 | 0.728 | [0.688, 0.763] | 0.596 | 0.933 |
| 29 | h11-n1-brief-text-t03 | greedy | 2 | text | 3 | 3 | 0.170 | 0.605 | [0.545, 0.660] | 0.469 | 0.855 |
