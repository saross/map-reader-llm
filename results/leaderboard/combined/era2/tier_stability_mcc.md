# Tier stability (MCC) — combined era2

**Metric**: MCC
**Stratum**: combined / era2
**Conditions**: 87

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**MCC tiers are buffer-independent by methodology.** The MCC permutation test (`run_permutation_test_mcc`) operates on tile-level binary classifications which do not depend on the buffer used for spatial matching during F1 evaluation. The greedy-clique tiering also sorts by a single buffer-independent MCC value per condition. Therefore the tier assignments at 20 / 30 / 40 / 50 / 100 m are identical, and Spearman rho across buffers is 1.0 by construction. This is not a degenerate output; it correctly reflects that MCC at the tile level summarises the entire confusion matrix without buffer-dependent matching geometry.

Note: ties (all conditions in one tier) make Spearman's rho undefined; the rho column reports `nan` in that case.

## Spearman rank correlation summary

| vs buffer | Spearman rho | p-value |
|---:|---:|---:|
| 30 m | +1.0000 | 0.0000 |
| 40 m | +1.0000 | 0.0000 |
| 50 m | +1.0000 | 0.0000 |
| 100 m | +1.0000 | 0.0000 |

## Per-condition tier assignments

| condition | MCC@20m | tier@20m | tier@30m | tier@40m | tier@50m | tier@100m | spearman vs 20m |
|:---|---:| ---: | ---: | ---: | ---: | ---: |---:|
| `pv-min-image-t0.3-n5` | 0.841 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-n1-image-t0-n3` | 0.839 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-image-t0.7-n5` | 0.838 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-image-t0.3-n10` | 0.837 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t0.7-n5` | 0.836 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-scale4-optimal-n5` | 0.835 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-image-adversarial` | 0.831 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-image-comparative` | 0.830 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-image-brief` | 0.829 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t1.0-n5` | 0.822 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-image-t0.7-n10` | 0.821 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-image-brief-text` | 0.819 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-image-checklist-text` | 0.817 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-image-checklist` | 0.816 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-scale4-optimal-n10` | 0.815 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t0.3-n10` | 0.815 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-image-t1.0-n10` | 0.810 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t0.3-n5` | 0.804 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-image-t1.0-n5` | 0.802 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t1.0-n10` | 0.800 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t0.7-n10` | 0.796 | 2 | 2 | 2 | 2 | 2 | stable |
| `session-78-text-comparative` | 0.793 | 2 | 2 | 2 | 2 | 2 | stable |
| `session-78-text-adversarial` | 0.793 | 2 | 2 | 2 | 2 | 2 | stable |
| `session-78-image-adversarial-text` | 0.793 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t1.0-n10` | 0.790 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-flash-high-text-16of30` | 0.789 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t0.3-n10` | 0.787 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.7-n5` | 0.786 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.0-n3` | 0.783 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t1.0-n10` | 0.780 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t1.0-n5` | 0.778 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.7-n10` | 0.776 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t0.3-n5` | 0.776 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t0.0-n3` | 0.774 | 2 | 2 | 2 | 2 | 2 | stable |
| `session-78-text-checklist` | 0.774 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.3-n10` | 0.772 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.3-n5` | 0.772 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t0.7-n5` | 0.767 | 2 | 2 | 2 | 2 | 2 | stable |
| `session-78-text-brief` | 0.765 | 3 | 3 | 3 | 3 | 3 | stable |
| `pv-high-text-t0.7-n10` | 0.763 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-pvd-pro-high-image-n5` | 0.761 | 3 | 3 | 3 | 3 | 3 | stable |
| `session-78-text-brief-text` | 0.758 | 3 | 3 | 3 | 3 | 3 | stable |
| `pv-high-text-t1.0-n5` | 0.756 | 3 | 3 | 3 | 3 | 3 | stable |
| `session-78-text-checklist-text` | 0.755 | 3 | 3 | 3 | 3 | 3 | stable |
| `session-78-text-adversarial-text` | 0.752 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-pvd-pro-medium-text-baseline` | 0.752 | 3 | 3 | 3 | 3 | 3 | stable |
| `scale4-optimal-487` | 0.745 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-pvd-pro-medium-image-baseline` | 0.734 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-pvd-pro-high-text-n5` | 0.727 | 3 | 3 | 3 | 3 | 3 | stable |
| `p3a-high-image-t0.3` | 0.682 | 4 | 4 | 4 | 4 | 4 | stable |
| `h11-pvd-flash-high-image-n5` | 0.676 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-high-image-t1.0` | 0.644 | 4 | 4 | 4 | 4 | 4 | stable |
| `h11-pvd-flash-high-text-n5` | 0.620 | 4 | 4 | 4 | 4 | 4 | stable |
| `h11-n1-pro-image-medium-t07` | 0.597 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-high-text-t0.3-n5` | 0.587 | 5 | 5 | 5 | 5 | 5 | stable |
| `p3a-high-text-t0.3` | 0.587 | 5 | 5 | 5 | 5 | 5 | stable |
| `p3a-high-text-t1.0-n5` | 0.575 | 5 | 5 | 5 | 5 | 5 | stable |
| `p3a-high-text-t1.0` | 0.575 | 5 | 5 | 5 | 5 | 5 | stable |
| `h11-n1-pro-image-high-t0` | 0.565 | 5 | 5 | 5 | 5 | 5 | stable |
| `h11-e47-propose-brief` | 0.503 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-high-image-t0.0` | 0.484 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-high-text-t0.0` | 0.451 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-min-image-t1.0` | 0.441 | 6 | 6 | 6 | 6 | 6 | stable |
| `pv-cascade-adversarial-checklist` | 0.432 | 6 | 6 | 6 | 6 | 6 | stable |
| `pv-adversarial-text` | 0.431 | 6 | 6 | 6 | 6 | 6 | stable |
| `pv-adversarial-image` | 0.416 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-minimal-text-t1.0` | 0.415 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-minimal-text-t1.0-n5` | 0.415 | 6 | 6 | 6 | 6 | 6 | stable |
| `pv-cascade-checklist-adversarial` | 0.412 | 6 | 6 | 6 | 6 | 6 | stable |
| `h11-pvd-image-n5` | 0.404 | 6 | 6 | 6 | 6 | 6 | stable |
| `pv-brief-text` | 0.396 | 6 | 6 | 6 | 6 | 6 | stable |
| `h11-n1-pro-text-high-t0` | 0.395 | 7 | 7 | 7 | 7 | 7 | stable |
| `pv-checklist-image` | 0.388 | 7 | 7 | 7 | 7 | 7 | stable |
| `h11-pvd-flash-minimal-text-n30-t07` | 0.380 | 7 | 7 | 7 | 7 | 7 | stable |
| `h11-n1-image-t03` | 0.348 | 7 | 7 | 7 | 7 | 7 | stable |
| `pv-brief-image` | 0.340 | 7 | 7 | 7 | 7 | 7 | stable |
| `p3a-min-image-t0.3` | 0.339 | 7 | 7 | 7 | 7 | 7 | stable |
| `h11-pvd-text-n10` | 0.316 | 8 | 8 | 8 | 8 | 8 | stable |
| `pv-checklist-text` | 0.315 | 8 | 8 | 8 | 8 | 8 | stable |
| `p3a-minimal-text-t0.3-n5` | 0.311 | 8 | 8 | 8 | 8 | 8 | stable |
| `p3a-minimal-text-t0.3` | 0.311 | 8 | 8 | 8 | 8 | 8 | stable |
| `h11-pvd-image-baseline` | 0.311 | 8 | 8 | 8 | 8 | 8 | stable |
| `h11-n1-pro-text-medium-t07` | 0.309 | 8 | 8 | 8 | 8 | 8 | stable |
| `p3a-minimal-text-t0.0` | 0.223 | 9 | 9 | 9 | 9 | 9 | stable |
| `h11-n1-image-t0` | 0.214 | 9 | 9 | 9 | 9 | 9 | stable |
| `h11-n1-brief-text-t03` | 0.170 | 9 | 9 | 9 | 9 | 9 | stable |
| `h11-pvd-text-baseline` | -0.001 | 10 | 10 | 10 | 10 | 10 | stable |

