# Tier stability (F1) — era2 single-pass+PV

**Generated**: Session 79 redesign (2026-04-25)
**Metric**: F1
**Stratum**: era2 / single-pass+PV
**Conditions**: 8

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**Important caveat**: in the current 12-stratum redesign build, tiers are constructed once per stratum at the primary buffer (20 m); the per-buffer markdown tier tables share the same tier assignments and only differ in the per-row F1 (or MCC) values displayed. Spearman rho across buffers is therefore 1.0 by construction (mathematically degenerate). The `tier@<buf>m` columns and Spearman rows are present for downstream cross-stratum comparison but contain no buffer-stability information beyond the trivial. Per-buffer tier construction would 5x the pairwise computation cost and is deferred.

**Fallback marker**: 4/4 non-primary buffer files fell back to the primary-buffer JSON (the expected behaviour with the current build).

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

