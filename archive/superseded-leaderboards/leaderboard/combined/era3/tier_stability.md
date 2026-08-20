# Tier stability (F1) — era3 consensus

**Metric**: F1
**Stratum**: era3 / consensus
**Conditions**: 14

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**F1 tiers are constructed independently at each buffer.** Per-cell thresholds are fixed at the primary buffer (20 m) via the `--threshold-buffer` flag of `build_tiered_leaderboard.py`; pairwise permutation tests and greedy-clique tier construction then run at each of [20, 30, 40, 50, 100] m using those fixed thresholds (Option A semantics). Spearman rho values reported below are therefore substantive — they surface buffer-dependent tier reorganisations rather than a tautology.

Note: ties (all conditions in one tier) make Spearman's rho undefined; the rho column reports `nan` in that case.

## Spearman rank correlation summary

| vs buffer | Spearman rho | p-value |
|---:|---:|---:|
| 30 m | nan | 1.0000 |
| 40 m | +1.0000 | 1.0000 |
| 50 m | nan | 1.0000 |
| 100 m | nan | 1.0000 |

## Per-condition tier assignments

| condition | F1@20m | tier@20m | tier@30m | tier@40m | tier@50m | tier@100m | spearman vs 20m |
|:---|---:| ---: | ---: | ---: | ---: | ---: |---:|
| `h8v2-scale-4` | 0.733 | 1 | 1 | 1 | 1 | 1 | stable |
| `h12v2-r1-hn-heavy` | 0.731 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-scale-8` | 0.730 | 1 | 1 | 1 | 1 | 1 | stable |
| `h10v2-pool_160_hp4hn4` | 0.717 | 1 | 1 | 1 | 1 | 1 | stable |
| `h12v2-r2-balanced` | 0.717 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-scale-32` | 0.713 | 1 | 2 | 1 | 2 | 2 | shift |
| `h8v2-scale-16` | 0.712 | 1 | 2 | 1 | 2 | 2 | shift |
| `h8v2-canonical` | 0.707 | 1 | 2 | 1 | 2 | 2 | shift |
| `h8v2-pure-positive-canon` | 0.705 | 1 | 2 | 1 | 2 | 2 | shift |
| `h8v2-plus-hp` | 0.705 | 1 | 2 | 1 | 2 | 2 | shift |
| `h12v2-r3-hp-heavy` | 0.701 | 1 | 2 | 1 | 2 | 3 | shift |
| `h10v2-pool_020_hp4hn4` | 0.697 | 1 | 2 | 1 | 2 | 3 | shift |
| `h10v2-pool_040_hp4hn4` | 0.694 | 1 | 2 | 1 | 2 | 3 | shift |
| `h10v2-pool_080_hp4hn4` | 0.688 | 1 | 2 | 1 | 2 | 3 | shift |

