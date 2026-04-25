# Tier stability (F1) — era2 consensus

**Generated**: Session 79 redesign (2026-04-25)
**Metric**: F1
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

| condition | F1@20m | tier@20m | tier@30m | tier@40m | tier@50m | tier@100m | spearman vs 20m |
|:---|---:| ---: | ---: | ---: | ---: | ---: |---:|
| `h11-pvd-pro-high-text-n5` | 0.836 | 1 | 1 | 1 | 1 | 1 | stable |
| `h11-pvd-flash-high-text-n5` | 0.814 | 1 | 1 | 1 | 1 | 1 | stable |
| `p3a-high-text-t0.3` | 0.789 | 2 | 2 | 2 | 2 | 2 | stable |
| `p3a-high-text-t0.3-n5` | 0.789 | 2 | 2 | 2 | 2 | 2 | stable |
| `p3a-high-text-t1.0` | 0.773 | 2 | 2 | 2 | 2 | 2 | stable |
| `p3a-high-text-t1.0-n5` | 0.773 | 2 | 2 | 2 | 2 | 2 | stable |
| `h11-pvd-flash-high-image-n5` | 0.750 | 2 | 2 | 2 | 2 | 2 | stable |
| `scale4-optimal-487` | 0.742 | 3 | 3 | 3 | 3 | 3 | stable |
| `p3a-high-image-t1.0` | 0.735 | 3 | 3 | 3 | 3 | 3 | stable |
| `p3a-high-image-t0.3` | 0.731 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-e47-propose-brief` | 0.714 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-pvd-pro-high-image-n5` | 0.700 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-pvd-image-n5` | 0.680 | 4 | 4 | 4 | 4 | 4 | stable |
| `h11-n1-image-t03` | 0.677 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-minimal-text-t1.0-n5` | 0.667 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-minimal-text-t1.0` | 0.667 | 4 | 4 | 4 | 4 | 4 | stable |
| `h11-pvd-flash-minimal-text-n30-t07` | 0.661 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-min-image-t0.3` | 0.660 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-min-image-t1.0` | 0.646 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-minimal-text-t0.3-n5` | 0.642 | 4 | 4 | 4 | 4 | 4 | stable |
| `p3a-minimal-text-t0.3` | 0.642 | 4 | 4 | 4 | 4 | 4 | stable |
| `h11-n1-image-t0` | 0.629 | 5 | 5 | 5 | 5 | 5 | stable |
| `h11-pvd-text-n10` | 0.619 | 5 | 5 | 5 | 5 | 5 | stable |
| `p3a-high-text-t0.0` | 0.605 | 5 | 5 | 5 | 5 | 5 | stable |
| `p3a-minimal-text-t0.0` | 0.593 | 5 | 5 | 5 | 5 | 5 | stable |
| `h11-n1-brief-text-t03` | 0.591 | 5 | 5 | 5 | 5 | 5 | stable |
| `h11-n1-pro-text-high-t0` | 0.567 | 6 | 6 | 6 | 6 | 6 | stable |
| `h11-n1-pro-image-high-t0` | 0.552 | 6 | 6 | 6 | 6 | 6 | stable |
| `p3a-high-image-t0.0` | 0.488 | 7 | 7 | 7 | 7 | 7 | stable |

