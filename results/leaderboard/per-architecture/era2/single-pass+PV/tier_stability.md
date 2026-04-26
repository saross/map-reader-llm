# Tier stability (F1) — era2 single-pass+PV

**Metric**: F1
**Stratum**: era2 / single-pass+PV
**Conditions**: 8

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**F1 tiers are constructed independently at each buffer.** Per-cell thresholds are fixed at the primary buffer (20 m) via the `--threshold-buffer` flag of `build_tiered_leaderboard.py`; pairwise permutation tests and greedy-clique tier construction then run at each of [20, 30, 40, 50, 100] m using those fixed thresholds (Option A semantics). Spearman rho values reported below are therefore substantive — they surface buffer-dependent tier reorganisations rather than a tautology.

Note: ties (all conditions in one tier) make Spearman's rho undefined; the rho column reports `nan` in that case.

## Spearman rank correlation summary

| vs buffer | Spearman rho | p-value |
|---:|---:|---:|
| 30 m | +1.0000 | 1.0000 |
| 40 m | +1.0000 | 1.0000 |
| 50 m | +1.0000 | 1.0000 |
| 100 m | +1.0000 | 1.0000 |

## Per-condition tier assignments

| condition | F1@20m | tier@20m | tier@30m | tier@40m | tier@50m | tier@100m | spearman vs 20m |
|:---|---:| ---: | ---: | ---: | ---: | ---: |---:|
| `pv-checklist-image` | 0.531 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-checklist-text` | 0.521 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-brief-image` | 0.520 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-brief-text` | 0.514 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-cascade-adversarial-checklist` | 0.504 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-cascade-checklist-adversarial` | 0.495 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-adversarial-image` | 0.494 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-adversarial-text` | 0.471 | 1 | 1 | 1 | 1 | 1 | stable |

