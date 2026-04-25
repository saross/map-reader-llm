# Tier stability (F1) — era2 pv

**Generated**: Session 79 redesign (2026-04-25)
**Metric**: F1
**Stratum**: era2 / pv
**Conditions**: 44

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
| `pv-flash-high-text-16of30` | 0.890 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t0.3-n5` | 0.886 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-comparative` | 0.885 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-adversarial` | 0.883 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-high-text-t1.0-n10` | 0.880 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-checklist` | 0.878 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t0.3-n5` | 0.878 | 1 | 1 | 1 | 1 | 1 | stable |
| `pv-min-text-t1.0-n10` | 0.877 | 1 | 1 | 1 | 1 | 1 | stable |
| `session-78-text-brief` | 0.876 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t0.7-n10` | 0.874 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.7-n5` | 0.873 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.7-n10` | 0.873 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t0.3-n10` | 0.872 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t1.0-n5` | 0.871 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.3-n10` | 0.868 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t0.7-n5` | 0.863 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-min-text-t0.0-n3` | 0.862 | 2 | 2 | 2 | 2 | 2 | stable |
| `pv-high-text-t1.0-n5` | 0.861 | 2 | 2 | 2 | 2 | 2 | stable |
| `session-78-text-checklist-text` | 0.860 | 3 | 3 | 3 | 3 | 3 | stable |
| `session-78-text-adversarial-text` | 0.858 | 3 | 3 | 3 | 3 | 3 | stable |
| `session-78-text-brief-text` | 0.846 | 3 | 3 | 3 | 3 | 3 | stable |
| `pv-high-text-t0.0-n3` | 0.823 | 3 | 3 | 3 | 3 | 3 | stable |
| `pv-min-image-t0.7-n10` | 0.788 | 4 | 4 | 4 | 4 | 4 | stable |
| `pv-high-image-t0.7-n5` | 0.787 | 4 | 4 | 4 | 4 | 4 | stable |
| `session-78-image-adversarial` | 0.787 | 4 | 4 | 4 | 4 | 4 | stable |
| `session-78-image-comparative` | 0.786 | 4 | 4 | 4 | 4 | 4 | stable |
| `session-78-image-brief` | 0.784 | 4 | 4 | 4 | 4 | 4 | stable |
| `session-78-image-checklist` | 0.783 | 4 | 4 | 4 | 4 | 4 | stable |
| `pv-min-image-t0.3-n10` | 0.782 | 4 | 4 | 4 | 4 | 4 | stable |
| `session-78-image-checklist-text` | 0.780 | 4 | 4 | 4 | 4 | 4 | stable |
| `pv-min-image-t0.3-n5` | 0.777 | 4 | 4 | 4 | 4 | 4 | stable |
| `pv-high-image-t0.7-n10` | 0.776 | 4 | 4 | 4 | 4 | 4 | stable |
| `pv-min-image-t0.7-n5` | 0.773 | 4 | 4 | 4 | 4 | 4 | stable |
| `session-78-image-adversarial-text` | 0.772 | 4 | 4 | 4 | 4 | 4 | stable |
| `pv-high-image-t0.3-n10` | 0.769 | 4 | 4 | 4 | 4 | 4 | stable |
| `pv-scale4-optimal-n10` | 0.768 | 4 | 4 | 4 | 4 | 4 | stable |
| `session-78-image-brief-text` | 0.768 | 5 | 5 | 5 | 5 | 5 | stable |
| `pv-n1-image-t0-n3` | 0.767 | 5 | 5 | 5 | 5 | 5 | stable |
| `pv-high-image-t1.0-n10` | 0.763 | 5 | 5 | 5 | 5 | 5 | stable |
| `pv-scale4-optimal-n5` | 0.763 | 5 | 5 | 5 | 5 | 5 | stable |
| `pv-high-image-t0.3-n5` | 0.746 | 5 | 5 | 5 | 5 | 5 | stable |
| `pv-min-image-t1.0-n10` | 0.741 | 5 | 5 | 5 | 5 | 5 | stable |
| `pv-min-image-t1.0-n5` | 0.738 | 5 | 5 | 5 | 5 | 5 | stable |
| `pv-high-image-t1.0-n5` | 0.734 | 6 | 6 | 6 | 6 | 6 | stable |

