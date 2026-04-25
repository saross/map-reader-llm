# Tier stability (MCC) — era3 consensus

**Generated**: Session 79 redesign (2026-04-25)
**Metric**: MCC
**Stratum**: era3 / consensus
**Conditions**: 14

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
| `h8v2-scale-4` | 0.772 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-scale-8` | 0.739 | 1 | 1 | 1 | 1 | 1 | stable |
| `h12v2-r3-hp-heavy` | 0.733 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-plus-hp` | 0.732 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-scale-16` | 0.726 | 1 | 1 | 1 | 1 | 1 | stable |
| `h12v2-r1-hn-heavy` | 0.725 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-scale-32` | 0.718 | 1 | 1 | 1 | 1 | 1 | stable |
| `h12v2-r2-balanced` | 0.718 | 1 | 1 | 1 | 1 | 1 | stable |
| `h10v2-pool_160_hp4hn4` | 0.718 | 1 | 1 | 1 | 1 | 1 | stable |
| `h10v2-pool_080_hp4hn4` | 0.691 | 1 | 1 | 1 | 1 | 1 | stable |
| `h10v2-pool_020_hp4hn4` | 0.686 | 1 | 1 | 1 | 1 | 1 | stable |
| `h8v2-canonical` | 0.680 | 1 | 1 | 1 | 1 | 1 | stable |
| `h10v2-pool_040_hp4hn4` | 0.640 | 2 | 2 | 2 | 2 | 2 | stable |
| `h8v2-pure-positive-canon` | 0.599 | 2 | 2 | 2 | 2 | 2 | stable |

