# Tier stability (MCC) — era1 single-pass

**Metric**: MCC
**Stratum**: era1 / single-pass
**Conditions**: 21

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
| `h5-track1-image-verbose` | 0.281 | 1 | 1 | 1 | 1 | 1 | stable |
| `h5-track1-image-terse` | 0.223 | 1 | 1 | 1 | 1 | 1 | stable |
| `h4-config-default` | 0.214 | 1 | 1 | 1 | 1 | 1 | stable |
| `h4-canonical-last` | 0.212 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8-track1-image-exploratory-pure-positive-4hp` | 0.162 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track1-image-scale-8` | 0.147 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track1-image-scale-4` | 0.133 | 2 | 2 | 2 | 2 | 2 | stable |
| `h4-canonical-first` | 0.098 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track1-image-plus-hp` | 0.098 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track1-image-canonical` | 0.098 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track1-image-exploratory-pure-positive-canon` | 0.097 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track1-image-pure-positive-canon` | 0.097 | 2 | 2 | 2 | 2 | 2 | stable |
| `h4-random` | 0.084 | 2 | 2 | 2 | 2 | 2 | stable |
| `h5-track2-text-verbose` | 0.081 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track2-text-pure-positive-canon` | 0.000 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track2-text-scale-8` | 0.000 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track2-text-scale-4` | 0.000 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track1-image-exploratory-pure-positive-2hp` | 0.000 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track2-text-canonical` | 0.000 | 2 | 2 | 2 | 2 | 2 | stable |
| `h5-track2-text-terse` | 0.000 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8-track2-text-plus-hp` | 0.000 | 2 | 2 | 2 | 2 | 2 | stable |

