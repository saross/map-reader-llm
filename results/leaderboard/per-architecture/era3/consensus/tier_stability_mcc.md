# Tier stability (MCC) — era3 consensus

**Metric**: MCC
**Stratum**: era3 / consensus
**Conditions**: 14

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
| `h8v2-scale-4` | 0.772 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-scale-8` | 0.739 | 1 | 1 | 1 | 1 | 1 | stable |
| `h12v2-r3-hp-heavy` | 0.733 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-plus-hp` | 0.732 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-scale-16` | 0.726 | 1 | 1 | 1 | 1 | 1 | stable |
| `h12v2-r1-hn-heavy` | 0.725 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-scale-32` | 0.718 | 1 | 1 | 1 | 1 | 1 | stable |
| `h10v2-pool_160_hp4hn4` | 0.718 | 1 | 1 | 1 | 1 | 1 | stable |
| `h12v2-r2-balanced` | 0.718 | 1 | 1 | 1 | 1 | 1 | stable |
| `h10v2-pool_080_hp4hn4` | 0.691 | 1 | 1 | 1 | 1 | 1 | stable |
| `h10v2-pool_020_hp4hn4` | 0.686 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-canonical` | 0.680 | 1 | 1 | 1 | 1 | 1 | stable |
| `h10v2-pool_040_hp4hn4` | 0.640 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8v2-pure-positive-canon` | 0.599 | 2 | 2 | 2 | 2 | 2 | stable |

