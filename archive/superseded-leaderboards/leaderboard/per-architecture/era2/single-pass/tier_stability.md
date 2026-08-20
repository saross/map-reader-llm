# Tier stability (F1) — era2 single-pass

**Metric**: F1
**Stratum**: era2 / single-pass
**Conditions**: 6

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**F1 tiers are constructed independently at each buffer.** Per-cell thresholds are fixed at the primary buffer (20 m) via the `--threshold-buffer` flag of `build_tiered_leaderboard.py`; pairwise permutation tests and greedy-clique tier construction then run at each of [20, 30, 40, 50, 100] m using those fixed thresholds (Option A semantics). Spearman rho values reported below are therefore substantive — they surface buffer-dependent tier reorganisations rather than a tautology.

Note: ties (all conditions in one tier) make Spearman's rho undefined; the rho column reports `nan` in that case.

## Spearman rank correlation summary

| vs buffer | Spearman rho | p-value |
|---:|---:|---:|
| 30 m | +0.9091 | 0.0120 |
| 40 m | +0.9091 | 0.0120 |
| 50 m | +0.9091 | 0.0120 |
| 100 m | +0.9091 | 0.0120 |

## Per-condition tier assignments

| condition | F1@20m | tier@20m | tier@30m | tier@40m | tier@50m | tier@100m | spearman vs 20m |
|:---|---:| ---: | ---: | ---: | ---: | ---: |---:|
| `h11-pvd-pro-medium-text-baseline` | 0.763 | 1 | 1 | 1 | 1 | 1 | stable |
| `h11-pvd-pro-medium-image-baseline` | 0.606 | 2 | 1 | 1 | 1 | 1 | shift |
| `h11-pvd-image-baseline` | 0.600 | 2 | 2 | 2 | 2 | 2 | stable |
| `h11-pvd-text-baseline` | 0.520 | 3 | 3 | 3 | 3 | 3 | stable |
| `h11-n1-pro-image-medium-t07` | 0.452 | 4 | 3 | 3 | 3 | 3 | shift |
| `h11-n1-pro-text-medium-t07` | 0.416 | 4 | 4 | 4 | 4 | 4 | stable |

