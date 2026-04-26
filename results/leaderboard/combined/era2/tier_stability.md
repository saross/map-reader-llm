# Tier stability (F1) — combined era2

**Metric**: F1
**Stratum**: combined / era2
**Conditions**: 87

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**F1 tiers are constructed independently at each buffer.** Per-cell thresholds are fixed at the primary buffer (20 m) via the `--threshold-buffer` flag of `build_tiered_leaderboard.py`; pairwise permutation tests and greedy-clique tier construction then run at each of [20, 30, 40, 50, 100] m using those fixed thresholds (Option A semantics). Spearman rho values reported below are therefore substantive — they surface buffer-dependent tier reorganisations rather than a tautology.

Note: ties (all conditions in one tier) make Spearman's rho undefined; the rho column reports `nan` in that case.

## Spearman rank correlation summary

| vs buffer | Spearman rho | p-value |
|---:|---:|---:|
| 30 m | +0.9939 | 0.0000 |
| 40 m | +0.9950 | 0.0000 |
| 50 m | +0.9943 | 0.0000 |
| 100 m | +0.9944 | 0.0000 |

## Per-condition tier assignments

| condition | F1@20m | tier@20m | tier@30m | tier@40m | tier@50m | tier@100m | spearman vs 20m |
|:---|---:| ---: | ---: | ---: | ---: | ---: |---:|
| `pv-flash-high-text-16of30` | 0.890 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t0.3-n5` | 0.886 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-comparative` | 0.885 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-adversarial` | 0.883 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t1.0-n10` | 0.880 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-checklist` | 0.878 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t0.3-n5` | 0.878 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t1.0-n10` | 0.877 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-brief` | 0.876 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t0.7-n10` | 0.874 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.7-n5` | 0.873 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.7-n10` | 0.873 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t0.3-n10` | 0.872 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t1.0-n5` | 0.871 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.3-n10` | 0.868 | 2 | 3 | 2 | 2 | 2 | shift |
| `pv-high-text-t0.7-n5` | 0.863 | 2 | 3 | 2 | 2 | 2 | shift |
| `pv-min-text-t0.0-n3` | 0.862 | 2 | 3 | 2 | 2 | 2 | shift |
| `pv-high-text-t1.0-n5` | 0.861 | 2 | 3 | 2 | 3 | 3 | shift |
| `session-78-text-checklist-text` | 0.860 | 3 | 3 | 3 | 3 | 3 | stable |
| `session-78-text-adversarial-text` | 0.858 | 3 | 3 | 3 | 3 | 3 | stable |
| `session-78-text-brief-text` | 0.846 | 3 | 4 | 3 | 3 | 3 | shift |
| `h11-pvd-pro-high-text-n5` | 0.836 | 3 | 4 | 3 | 3 | 3 | shift |
| `pv-high-text-t0.0-n3` | 0.823 | 3 | 4 | 3 | 3 | 3 | shift |
| `h11-pvd-flash-high-text-n5` | 0.814 | 4 | 5 | 4 | 4 | 4 | shift |
| `p3a-high-text-t0.3-n5` | 0.789 | 4 | 5 | 4 | 4 | 4 | shift |
| `p3a-high-text-t0.3` | 0.789 | 4 | 5 | 4 | 4 | 4 | shift |
| `pv-min-image-t0.7-n10` | 0.788 | 4 | 6 | 5 | 5 | 5 | shift |
| `pv-high-image-t0.7-n5` | 0.787 | 4 | 6 | 5 | 5 | 5 | shift |
| `session-78-image-adversarial` | 0.787 | 4 | 6 | 5 | 6 | 5 | shift |
| `session-78-image-comparative` | 0.786 | 4 | 6 | 5 | 6 | 5 | shift |
| `session-78-image-brief` | 0.784 | 4 | 6 | 5 | 6 | 5 | shift |
| `session-78-image-checklist` | 0.783 | 4 | 6 | 5 | 6 | 5 | shift |
| `pv-min-image-t0.3-n10` | 0.782 | 4 | 6 | 5 | 6 | 5 | shift |
| `session-78-image-checklist-text` | 0.780 | 4 | 6 | 5 | 6 | 6 | shift |
| `pv-min-image-t0.3-n5` | 0.777 | 4 | 6 | 5 | 7 | 6 | shift |
| `pv-high-image-t0.7-n10` | 0.776 | 4 | 7 | 6 | 7 | 7 | shift |
| `pv-min-image-t0.7-n5` | 0.773 | 4 | 7 | 6 | 8 | 8 | shift |
| `p3a-high-text-t1.0-n5` | 0.773 | 5 | 8 | 7 | 9 | 9 | shift |
| `p3a-high-text-t1.0` | 0.773 | 5 | 8 | 7 | 9 | 9 | shift |
| `session-78-image-adversarial-text` | 0.772 | 5 | 9 | 8 | 10 | 10 | shift |
| `pv-high-image-t0.3-n10` | 0.769 | 5 | 9 | 8 | 10 | 10 | shift |
| `pv-scale4-optimal-n10` | 0.768 | 5 | 9 | 8 | 10 | 10 | shift |
| `session-78-image-brief-text` | 0.768 | 5 | 9 | 8 | 10 | 10 | shift |
| `pv-n1-image-t0-n3` | 0.767 | 5 | 9 | 8 | 10 | 10 | shift |
| `pv-high-image-t1.0-n10` | 0.763 | 5 | 9 | 8 | 10 | 10 | shift |
| `h11-pvd-pro-medium-text-baseline` | 0.763 | 5 | 10 | 9 | 11 | 11 | shift |
| `pv-scale4-optimal-n5` | 0.763 | 5 | 10 | 9 | 12 | 12 | shift |
| `h11-pvd-flash-high-image-n5` | 0.750 | 5 | 10 | 9 | 12 | 12 | shift |
| `pv-high-image-t0.3-n5` | 0.746 | 6 | 10 | 9 | 12 | 12 | shift |
| `scale4-optimal-487` | 0.742 | 6 | 10 | 9 | 12 | 12 | shift |
| `pv-min-image-t1.0-n10` | 0.741 | 6 | 10 | 9 | 12 | 12 | shift |
| `pv-min-image-t1.0-n5` | 0.738 | 6 | 10 | 9 | 12 | 12 | shift |
| `p3a-high-image-t1.0` | 0.735 | 6 | 11 | 10 | 12 | 12 | shift |
| `pv-high-image-t1.0-n5` | 0.734 | 6 | 11 | 11 | 13 | 13 | shift |
| `p3a-high-image-t0.3` | 0.731 | 6 | 11 | 12 | 14 | 14 | shift |
| `h11-e47-propose-brief` | 0.714 | 6 | 12 | 13 | 15 | 15 | shift |
| `h11-pvd-pro-high-image-n5` | 0.700 | 6 | 13 | 14 | 16 | 16 | shift |
| `h11-pvd-image-n5` | 0.680 | 7 | 14 | 15 | 17 | 17 | shift |
| `h11-n1-image-t03` | 0.677 | 7 | 14 | 15 | 17 | 17 | shift |
| `p3a-minimal-text-t1.0` | 0.667 | 7 | 15 | 16 | 18 | 18 | shift |
| `p3a-minimal-text-t1.0-n5` | 0.667 | 7 | 15 | 16 | 18 | 18 | shift |
| `h11-pvd-flash-minimal-text-n30-t07` | 0.661 | 7 | 15 | 16 | 18 | 18 | shift |
| `p3a-min-image-t0.3` | 0.660 | 7 | 15 | 17 | 19 | 19 | shift |
| `p3a-min-image-t1.0` | 0.646 | 7 | 15 | 17 | 19 | 19 | shift |
| `p3a-minimal-text-t0.3` | 0.642 | 7 | 16 | 18 | 20 | 20 | shift |
| `p3a-minimal-text-t0.3-n5` | 0.642 | 7 | 16 | 18 | 20 | 20 | shift |
| `h11-n1-image-t0` | 0.629 | 8 | 17 | 19 | 21 | 21 | shift |
| `h11-pvd-text-n10` | 0.619 | 8 | 18 | 20 | 22 | 22 | shift |
| `h11-pvd-pro-medium-image-baseline` | 0.606 | 8 | 19 | 21 | 23 | 23 | shift |
| `p3a-high-text-t0.0` | 0.605 | 8 | 20 | 22 | 24 | 24 | shift |
| `h11-pvd-image-baseline` | 0.600 | 9 | 20 | 22 | 24 | 24 | shift |
| `p3a-minimal-text-t0.0` | 0.593 | 9 | 21 | 23 | 25 | 25 | shift |
| `h11-n1-brief-text-t03` | 0.591 | 9 | 21 | 23 | 25 | 25 | shift |
| `h11-n1-pro-text-high-t0` | 0.567 | 9 | 21 | 23 | 25 | 25 | shift |
| `h11-n1-pro-image-high-t0` | 0.552 | 9 | 21 | 23 | 25 | 26 | shift |
| `pv-checklist-image` | 0.531 | 9 | 21 | 24 | 26 | 27 | shift |
| `pv-checklist-text` | 0.521 | 10 | 21 | 24 | 26 | 27 | shift |
| `pv-brief-image` | 0.520 | 10 | 21 | 24 | 26 | 27 | shift |
| `h11-pvd-text-baseline` | 0.520 | 10 | 22 | 24 | 26 | 27 | shift |
| `pv-brief-text` | 0.514 | 10 | 22 | 24 | 26 | 27 | shift |
| `pv-cascade-adversarial-checklist` | 0.504 | 10 | 22 | 24 | 26 | 27 | shift |
| `pv-cascade-checklist-adversarial` | 0.495 | 10 | 22 | 25 | 27 | 28 | shift |
| `pv-adversarial-image` | 0.494 | 10 | 22 | 25 | 27 | 28 | shift |
| `p3a-high-image-t0.0` | 0.488 | 10 | 22 | 25 | 27 | 28 | shift |
| `pv-adversarial-text` | 0.471 | 11 | 23 | 26 | 28 | 29 | shift |
| `h11-n1-pro-image-medium-t07` | 0.452 | 11 | 23 | 26 | 29 | 30 | shift |
| `h11-n1-pro-text-medium-t07` | 0.416 | 11 | 24 | 27 | 30 | 31 | shift |

