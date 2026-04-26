# Tier stability (F1) — era1 single-pass

**Metric**: F1
**Stratum**: era1 / single-pass
**Conditions**: 21

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**F1 tiers are constructed independently at each buffer.** Per-cell thresholds are fixed at the primary buffer (20 m) via the `--threshold-buffer` flag of `build_tiered_leaderboard.py`; pairwise permutation tests and greedy-clique tier construction then run at each of [20, 30, 40, 50, 100] m using those fixed thresholds (Option A semantics). Spearman rho values reported below are therefore substantive — they surface buffer-dependent tier reorganisations rather than a tautology.

Note: ties (all conditions in one tier) make Spearman's rho undefined; the rho column reports `nan` in that case.

## Spearman rank correlation summary

| vs buffer | Spearman rho | p-value |
|---:|---:|---:|
| 30 m | +1.0000 | 1.0000 |
| 40 m | nan | 1.0000 |
| 50 m | nan | 1.0000 |
| 100 m | nan | 1.0000 |

## Per-condition tier assignments

| condition | F1@20m | tier@20m | tier@30m | tier@40m | tier@50m | tier@100m | spearman vs 20m |
|:---|---:| ---: | ---: | ---: | ---: | ---: |---:|
| `h4-canonical-last` | 0.631 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8-track2-text-scale-4` | 0.609 | 1 | 1 | 2 | 2 | 2 | shift |
| `h8-track2-text-scale-8` | 0.607 | 1 | 1 | 2 | 2 | 2 | shift |
| `h4-config-default` | 0.606 | 1 | 1 | 3 | 3 | 3 | shift |
| `h5-track1-image-terse` | 0.605 | 1 | 1 | 3 | 3 | 3 | shift |
| `h8-track2-text-canonical` | 0.605 | 1 | 1 | 4 | 4 | 4 | shift |
| `h8-track2-text-pure-positive-canon` | 0.605 | 1 | 1 | 4 | 4 | 4 | shift |
| `h5-track1-image-verbose` | 0.603 | 1 | 1 | 5 | 5 | 5 | shift |
| `h8-track1-image-exploratory-pure-positive-4hp` | 0.599 | 1 | 1 | 5 | 5 | 5 | shift |
| `h4-canonical-first` | 0.599 | 1 | 1 | 5 | 5 | 5 | shift |
| `h8-track1-image-plus-hp` | 0.599 | 1 | 1 | 5 | 5 | 5 | shift |
| `h5-track2-text-terse` | 0.598 | 1 | 1 | 6 | 6 | 6 | shift |
| `h8-track2-text-plus-hp` | 0.597 | 1 | 1 | 6 | 6 | 6 | shift |
| `h8-track1-image-scale-8` | 0.587 | 1 | 1 | 6 | 6 | 7 | shift |
| `h8-track1-image-scale-4` | 0.584 | 1 | 1 | 6 | 6 | 7 | shift |
| `h5-track2-text-verbose` | 0.583 | 1 | 1 | 6 | 6 | 8 | shift |
| `h8-track1-image-canonical` | 0.581 | 1 | 1 | 6 | 6 | 8 | shift |
| `h8-track1-image-exploratory-pure-positive-2hp` | 0.571 | 1 | 1 | 6 | 6 | 8 | shift |
| `h4-random` | 0.571 | 1 | 1 | 6 | 6 | 8 | shift |
| `h8-track1-image-exploratory-pure-positive-canon` | 0.570 | 1 | 1 | 6 | 6 | 8 | shift |
| `h8-track1-image-pure-positive-canon` | 0.568 | 1 | 1 | 6 | 6 | 8 | shift |

