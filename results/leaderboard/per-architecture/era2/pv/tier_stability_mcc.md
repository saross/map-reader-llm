# Tier stability (MCC) — era2 pv

**Metric**: MCC
**Stratum**: era2 / pv
**Conditions**: 44

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
| `session-78-image-checklist-text` | 0.821 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-image-brief-text` | 0.819 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-image-checklist` | 0.816 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-scale4-optimal-n10` | 0.815 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t0.3-n10` | 0.815 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-image-t1.0-n10` | 0.810 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t0.3-n5` | 0.804 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-image-t1.0-n5` | 0.802 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t1.0-n10` | 0.800 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-image-adversarial-text` | 0.797 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-image-t0.7-n10` | 0.796 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-comparative` | 0.793 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-adversarial` | 0.793 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t1.0-n10` | 0.790 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-flash-high-text-16of30` | 0.789 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t0.3-n10` | 0.787 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t0.7-n5` | 0.786 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t0.0-n3` | 0.783 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t1.0-n10` | 0.780 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t1.0-n5` | 0.778 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t0.7-n10` | 0.776 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t0.3-n5` | 0.776 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t0.0-n3` | 0.774 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-checklist` | 0.774 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t0.3-n10` | 0.772 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t0.3-n5` | 0.772 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t0.7-n5` | 0.767 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-brief` | 0.765 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t0.7-n10` | 0.763 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-brief-text` | 0.758 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t1.0-n5` | 0.756 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-checklist-text` | 0.755 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-adversarial-text` | 0.752 | 2 | 2 | 2 | 2 | 2 | stable |

