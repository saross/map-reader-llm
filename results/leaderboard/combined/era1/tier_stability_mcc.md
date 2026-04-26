# Tier stability (MCC) — combined era1

**Metric**: MCC
**Stratum**: combined / era1
**Conditions**: 93

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
| `h9-track1-image-h9-B-v4` | 0.714 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-A-p5` | 0.694 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-A-p3` | 0.691 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-D-t1` | 0.685 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-A-p4` | 0.685 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-C-img2` | 0.678 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-C-img3` | 0.672 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-C-img1` | 0.670 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-D-t3` | 0.669 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-B-v1` | 0.661 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-A-p1` | 0.661 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-C-img5` | 0.657 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-B-v5` | 0.657 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-E-p2` | 0.654 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-E-p3` | 0.654 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-A-p2` | 0.645 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-E-p1` | 0.643 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-E-p4` | 0.642 | 1 | 1 | 1 | 1 | 1 | stable |
| `h3-high-track2-text-T1.0` | 0.641 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-D-t2` | 0.638 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-B-v3` | 0.638 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track1-image-h9-D-t5` | 0.632 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track1-image-h9-D-t4` | 0.631 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track1-image-h9-B-v2` | 0.630 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track1-image-h9-E-p5` | 0.605 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track1-image-h9-C-img4` | 0.580 | 2 | 2 | 2 | 2 | 2 | stable |
| `h3-high-track2-text-T0.3` | 0.576 | 2 | 2 | 2 | 2 | 2 | stable |
| `h3-high-track2-text-T0.7` | 0.571 | 2 | 2 | 2 | 2 | 2 | stable |
| `h3-rep-high` | 0.545 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-A-p1` | 0.501 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-B-v3` | 0.499 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-A-p4` | 0.495 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-A-p2` | 0.487 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-D-t1` | 0.476 | 3 | 3 | 3 | 3 | 3 | stable |
| `h3-track1-image-T1.0` | 0.475 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-E-p1` | 0.475 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-D-t2` | 0.473 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-E-p3` | 0.469 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-D-t3` | 0.444 | 3 | 3 | 3 | 3 | 3 | stable |
| `h3-track1-image-T0.7` | 0.443 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-A-p5` | 0.440 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-D-t5` | 0.440 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-B-v2` | 0.437 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-B-v5` | 0.435 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-D-t4` | 0.431 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-E-p2` | 0.426 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-E-p5` | 0.423 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-A-p3` | 0.410 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-E-p4` | 0.404 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-B-v1` | 0.403 | 4 | 4 | 4 | 4 | 4 | stable |
| `h1-verbose-text-image` | 0.395 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track2-text-T1.3` | 0.379 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track1-image-T1.3` | 0.367 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track2-text-h9-B-v4` | 0.353 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track1-image-T1.0` | 0.332 | 4 | 4 | 4 | 4 | 4 | stable |
| `h3-track2-text-T1.0` | 0.331 | 4 | 4 | 4 | 4 | 4 | stable |
| `h3-rep-minimal` | 0.312 | 4 | 4 | 4 | 4 | 4 | stable |
| `h1-brief-text-image` | 0.302 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track2-text-T1.0` | 0.284 | 5 | 5 | 5 | 5 | 5 | stable |
| `h7-track2-text-T0.7` | 0.283 | 5 | 5 | 5 | 5 | 5 | stable |
| `h5-track1-image-verbose` | 0.281 | 5 | 5 | 5 | 5 | 5 | stable |
| `h3-track1-image-T0.3` | 0.271 | 5 | 5 | 5 | 5 | 5 | stable |
| `h7-track1-image-T0.3` | 0.270 | 5 | 5 | 5 | 5 | 5 | stable |
| `h3-track2-text-T0.7` | 0.267 | 5 | 5 | 5 | 5 | 5 | stable |
| `h1-brief-text` | 0.258 | 5 | 5 | 5 | 5 | 5 | stable |
| `h1-image-only` | 0.251 | 5 | 5 | 5 | 5 | 5 | stable |
| `h7-track1-image-T0.7` | 0.229 | 5 | 5 | 5 | 5 | 5 | stable |
| `h5-track1-image-terse` | 0.223 | 5 | 5 | 5 | 5 | 5 | stable |
| `h7-track2-text-T0.3` | 0.214 | 5 | 5 | 5 | 5 | 5 | stable |
| `h4-config-default` | 0.214 | 5 | 5 | 5 | 5 | 5 | stable |
| `h4-canonical-last` | 0.212 | 5 | 5 | 5 | 5 | 5 | stable |
| `h1-verbose-text` | 0.203 | 5 | 5 | 5 | 5 | 5 | stable |
| `h3-track2-text-T0.3` | 0.180 | 5 | 5 | 5 | 5 | 5 | stable |
| `h8-track1-image-exploratory-pure-positive-4hp` | 0.162 | 6 | 6 | 6 | 6 | 6 | stable |
| `h8-track1-image-scale-8` | 0.147 | 6 | 6 | 6 | 6 | 6 | stable |
| `h8-track1-image-scale-4` | 0.133 | 6 | 6 | 6 | 6 | 6 | stable |
| `h7-track1-image-T0.0` | 0.118 | 6 | 6 | 6 | 6 | 6 | stable |
| `h8-track1-image-plus-hp` | 0.098 | 6 | 6 | 6 | 6 | 6 | stable |
| `h4-canonical-first` | 0.098 | 6 | 6 | 6 | 6 | 6 | stable |
| `h8-track1-image-canonical` | 0.098 | 6 | 6 | 6 | 6 | 6 | stable |
| `h8-track1-image-exploratory-pure-positive-canon` | 0.097 | 6 | 6 | 6 | 6 | 6 | stable |
| `h8-track1-image-pure-positive-canon` | 0.097 | 6 | 6 | 6 | 6 | 6 | stable |
| `h11-bridge-brief-text-t0` | 0.095 | 6 | 6 | 6 | 6 | 6 | stable |
| `h7-track2-text-T0.0` | 0.088 | 6 | 6 | 6 | 6 | 6 | stable |
| `h4-random` | 0.084 | 6 | 6 | 6 | 6 | 6 | stable |
| `h5-track2-text-verbose` | 0.081 | 6 | 6 | 6 | 6 | 6 | stable |
| `h8-track2-text-canonical` | 0.000 | 7 | 7 | 7 | 7 | 7 | stable |
| `h8-track1-image-exploratory-pure-positive-2hp` | 0.000 | 7 | 7 | 7 | 7 | 7 | stable |
| `h8-track2-text-scale-8` | 0.000 | 7 | 7 | 7 | 7 | 7 | stable |
| `h8-track2-text-scale-4` | 0.000 | 7 | 7 | 7 | 7 | 7 | stable |
| `h8-track2-text-pure-positive-canon` | 0.000 | 7 | 7 | 7 | 7 | 7 | stable |
| `h5-track2-text-terse` | 0.000 | 7 | 7 | 7 | 7 | 7 | stable |
| `h8-track2-text-plus-hp` | 0.000 | 7 | 7 | 7 | 7 | 7 | stable |

