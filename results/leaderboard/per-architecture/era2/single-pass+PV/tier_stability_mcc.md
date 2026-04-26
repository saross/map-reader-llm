# Tier stability (MCC) — era2 single-pass+PV

**Metric**: MCC
**Stratum**: era2 / single-pass+PV
**Conditions**: 8

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
| `pv-cascade-adversarial-checklist` | 0.432 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-adversarial-text` | 0.431 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-adversarial-image` | 0.416 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-cascade-checklist-adversarial` | 0.412 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-brief-text` | 0.396 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-checklist-image` | 0.388 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-brief-image` | 0.340 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-checklist-text` | 0.315 | 2 | 2 | 2 | 2 | 2 | stable |

