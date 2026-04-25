# Tier stability (MCC) — era2 consensus

**Generated**: Session 79 redesign (2026-04-25)
**Metric**: MCC
**Stratum**: era2 / consensus
**Conditions**: 29

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**Important caveat**: in the current 12-stratum redesign build, tiers are constructed once per stratum at the primary buffer (20 m); the per-buffer markdown tier tables share the same tier assignments and only differ in the per-row F1 (or MCC) values displayed. Spearman rho across buffers is therefore 1.0 by construction (mathematically degenerate). The `tier@<buf>m` columns and Spearman rows are present for downstream cross-stratum comparison but contain no buffer-stability information beyond the trivial. Per-buffer tier construction would 5x the pairwise computation cost and is deferred.

**Fallback marker**: 4/4 non-primary buffer files fell back to the primary-buffer JSON (the expected behaviour with the current build).

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
| `h11-pvd-pro-high-image-n5` | 0.761 | 1 | 1 | 1 | 1 | 1 | stable |
| `scale4-optimal-487` | 0.745 | 1 | 1 | 1 | 1 | 1 | stable |
| `h11-pvd-pro-high-text-n5` | 0.727 | 1 | 1 | 1 | 1 | 1 | stable |
| `p3a-high-image-t0.3` | 0.682 | 2 | 2 | 2 | 2 | 2 | stable |
| `h11-pvd-flash-high-image-n5` | 0.676 | 2 | 2 | 2 | 2 | 2 | stable |
| `p3a-high-image-t1.0` | 0.644 | 2 | 2 | 2 | 2 | 2 | stable |
| `h11-pvd-flash-high-text-n5` | 0.620 | 2 | 2 | 2 | 2 | 2 | stable |
| `p3a-high-text-t0.3` | 0.587 | 3 | 3 | 3 | 3 | 3 | stable |
| `p3a-high-text-t0.3-n5` | 0.587 | 3 | 3 | 3 | 3 | 3 | stable |
| `p3a-high-text-t1.0-n5` | 0.575 | 3 | 3 | 3 | 3 | 3 | stable |
| `p3a-high-text-t1.0` | 0.575 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-n1-pro-image-high-t0` | 0.565 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-e47-propose-brief` | 0.503 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-high-image-t0.0` | 0.484 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-high-text-t0.0` | 0.451 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-min-image-t1.0` | 0.441 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-minimal-text-t1.0-n5` | 0.415 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-minimal-text-t1.0` | 0.415 | 4 | 4 | 4 | 4 | 4 | stable |
| `h11-pvd-image-n5` | 0.404 | 5 | 5 | 5 | 5 | 5 | stable |
| `h11-n1-pro-text-high-t0` | 0.395 | 5 | 5 | 5 | 5 | 5 | stable |
| `h11-pvd-flash-minimal-text-n30-t07` | 0.380 | 5 | 5 | 5 | 5 | 5 | stable |
| `h11-n1-image-t03` | 0.348 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-min-image-t0.3` | 0.339 | 6 | 6 | 6 | 6 | 6 | stable |
| `h11-pvd-text-n10` | 0.316 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-minimal-text-t0.3-n5` | 0.311 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-minimal-text-t0.3` | 0.311 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-minimal-text-t0.0` | 0.223 | 7 | 7 | 7 | 7 | 7 | stable |
| `h11-n1-image-t0` | 0.214 | 7 | 7 | 7 | 7 | 7 | stable |
| `h11-n1-brief-text-t03` | 0.170 | 7 | 7 | 7 | 7 | 7 | stable |

