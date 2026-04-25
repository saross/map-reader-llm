# Tier stability (F1) — era1 consensus

**Generated**: Session 79 redesign (2026-04-25)
**Metric**: F1
**Stratum**: era1 / consensus
**Conditions**: 72

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
| `h3-high-track2-text-T1.0` | 0.775 | 1 | 1 | 1 | 1 | 1 | stable |
| `h3-high-track2-text-T0.3` | 0.774 | 1 | 1 | 1 | 1 | 1 | stable |
| `h3-high-track2-text-T0.7` | 0.773 | 1 | 1 | 1 | 1 | 1 | stable |
| `h3-rep-high` | 0.770 | 1 | 1 | 1 | 1 | 1 | stable |
| `h9-track2-text-h9-D-t4` | 0.739 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-D-t1` | 0.735 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-A-p4` | 0.731 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-A-p1` | 0.726 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-A-p2` | 0.723 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-E-p1` | 0.717 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-D-t2` | 0.712 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-A-p5` | 0.712 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-D-t3` | 0.711 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-D-t5` | 0.710 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-A-p3` | 0.710 | 2 | 2 | 2 | 2 | 2 | stable |
| `h3-rep-minimal` | 0.703 | 2 | 2 | 2 | 2 | 2 | stable |
| `h9-track2-text-h9-B-v1` | 0.698 | 3 | 3 | 3 | 3 | 3 | stable |
| `h3-track2-text-T0.3` | 0.692 | 3 | 3 | 3 | 3 | 3 | stable |
| `h3-track2-text-T0.7` | 0.692 | 3 | 3 | 3 | 3 | 3 | stable |
| `h3-track1-image-T0.7` | 0.691 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-C-img5` | 0.689 | 3 | 3 | 3 | 3 | 3 | stable |
| `h7-track2-text-T0.7` | 0.687 | 3 | 3 | 3 | 3 | 3 | stable |
| `h3-track2-text-T1.0` | 0.686 | 3 | 3 | 3 | 3 | 3 | stable |
| `h7-track2-text-T0.3` | 0.683 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-A-p1` | 0.682 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-A-p5` | 0.679 | 3 | 3 | 3 | 3 | 3 | stable |
| `h3-track1-image-T1.0` | 0.679 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-E-p2` | 0.675 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-B-v2` | 0.673 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-D-t2` | 0.673 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-C-img4` | 0.672 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-D-t5` | 0.669 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-D-t1` | 0.668 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-B-v5` | 0.667 | 3 | 3 | 3 | 3 | 3 | stable |
| `h3-track1-image-T0.3` | 0.666 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-A-p4` | 0.665 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-B-v1` | 0.664 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-A-p2` | 0.664 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-C-img3` | 0.664 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-D-t3` | 0.663 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-C-img2` | 0.663 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-E-p2` | 0.661 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-B-v4` | 0.658 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track2-text-h9-E-p4` | 0.658 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-D-t4` | 0.657 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-E-p5` | 0.656 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-B-v2` | 0.655 | 3 | 3 | 3 | 3 | 3 | stable |
| `h9-track1-image-h9-E-p1` | 0.652 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track2-text-h9-E-p5` | 0.650 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track1-image-h9-B-v5` | 0.649 | 4 | 4 | 4 | 4 | 4 | stable |
| `h1-brief-text` | 0.644 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track1-image-h9-A-p3` | 0.644 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track2-text-T0.0` | 0.643 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track2-text-T1.0` | 0.643 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track1-image-h9-E-p4` | 0.642 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track1-image-h9-C-img1` | 0.641 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track2-text-T1.3` | 0.640 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track1-image-h9-B-v3` | 0.640 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track1-image-T1.0` | 0.640 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track2-text-h9-B-v3` | 0.635 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track1-image-T0.3` | 0.634 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track1-image-h9-B-v4` | 0.632 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track1-image-h9-E-p3` | 0.628 | 4 | 4 | 4 | 4 | 4 | stable |
| `h1-verbose-text-image` | 0.627 | 4 | 4 | 4 | 4 | 4 | stable |
| `h1-brief-text-image` | 0.624 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track1-image-T0.7` | 0.620 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track1-image-T0.0` | 0.613 | 4 | 4 | 4 | 4 | 4 | stable |
| `h9-track2-text-h9-E-p3` | 0.612 | 4 | 4 | 4 | 4 | 4 | stable |
| `h7-track1-image-T1.3` | 0.606 | 5 | 5 | 5 | 5 | 5 | stable |
| `h1-verbose-text` | 0.596 | 5 | 5 | 5 | 5 | 5 | stable |
| `h1-image-only` | 0.575 | 5 | 5 | 5 | 5 | 5 | stable |
| `h11-bridge-brief-text-t0` | 0.515 | 6 | 6 | 6 | 6 | 6 | stable |

