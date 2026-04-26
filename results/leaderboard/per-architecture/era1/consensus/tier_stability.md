# Tier stability (F1) — era1 consensus

**Metric**: F1
**Stratum**: era1 / consensus
**Conditions**: 72

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**F1 tiers are constructed independently at each buffer.** Per-cell thresholds are fixed at the primary buffer (20 m) via the `--threshold-buffer` flag of `build_tiered_leaderboard.py`; pairwise permutation tests and greedy-clique tier construction then run at each of [20, 30, 40, 50, 100] m using those fixed thresholds (Option A semantics). Spearman rho values reported below are therefore substantive — they surface buffer-dependent tier reorganisations rather than a tautology.

Note: ties (all conditions in one tier) make Spearman's rho undefined; the rho column reports `nan` in that case.

## Spearman rank correlation summary

| vs buffer | Spearman rho | p-value |
|---:|---:|---:|
| 30 m | +0.9490 | 0.0000 |
| 40 m | +0.9440 | 0.0000 |
| 50 m | +0.9424 | 0.0000 |
| 100 m | +0.9424 | 0.0000 |

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
| `h9-track2-text-h9-E-p1` | 0.717 | 2 | 2 | 2 | 3 | 3 | shift |
| `h9-track2-text-h9-D-t2` | 0.712 | 2 | 2 | 2 | 3 | 3 | shift |
| `h9-track2-text-h9-A-p5` | 0.712 | 2 | 2 | 2 | 3 | 3 | shift |
| `h9-track2-text-h9-D-t3` | 0.711 | 2 | 2 | 2 | 3 | 3 | shift |
| `h9-track2-text-h9-D-t5` | 0.710 | 2 | 2 | 2 | 3 | 3 | shift |
| `h9-track2-text-h9-A-p3` | 0.710 | 2 | 2 | 2 | 3 | 3 | shift |
| `h3-rep-minimal` | 0.703 | 2 | 2 | 3 | 4 | 4 | shift |
| `h9-track2-text-h9-B-v1` | 0.698 | 3 | 3 | 3 | 4 | 4 | shift |
| `h3-track2-text-T0.3` | 0.692 | 3 | 3 | 3 | 4 | 4 | shift |
| `h3-track2-text-T0.7` | 0.692 | 3 | 3 | 3 | 4 | 4 | shift |
| `h3-track1-image-T0.7` | 0.691 | 3 | 3 | 4 | 5 | 5 | shift |
| `h9-track1-image-h9-C-img5` | 0.689 | 3 | 3 | 4 | 5 | 5 | shift |
| `h7-track2-text-T0.7` | 0.687 | 3 | 3 | 5 | 6 | 6 | shift |
| `h3-track2-text-T1.0` | 0.686 | 3 | 3 | 5 | 6 | 6 | shift |
| `h7-track2-text-T0.3` | 0.683 | 3 | 3 | 5 | 6 | 6 | shift |
| `h9-track1-image-h9-A-p1` | 0.682 | 3 | 3 | 6 | 7 | 7 | shift |
| `h9-track1-image-h9-A-p5` | 0.679 | 3 | 3 | 6 | 7 | 7 | shift |
| `h3-track1-image-T1.0` | 0.679 | 3 | 3 | 7 | 8 | 8 | shift |
| `h9-track1-image-h9-E-p2` | 0.675 | 3 | 3 | 7 | 9 | 9 | shift |
| `h9-track2-text-h9-B-v2` | 0.673 | 3 | 4 | 8 | 10 | 10 | shift |
| `h9-track1-image-h9-D-t2` | 0.673 | 3 | 5 | 9 | 11 | 11 | shift |
| `h9-track1-image-h9-C-img4` | 0.672 | 3 | 5 | 9 | 11 | 11 | shift |
| `h9-track1-image-h9-D-t5` | 0.669 | 3 | 5 | 9 | 11 | 11 | shift |
| `h9-track1-image-h9-D-t1` | 0.668 | 3 | 5 | 9 | 12 | 12 | shift |
| `h9-track2-text-h9-B-v5` | 0.667 | 3 | 5 | 10 | 13 | 13 | shift |
| `h3-track1-image-T0.3` | 0.666 | 3 | 5 | 10 | 14 | 14 | shift |
| `h9-track1-image-h9-A-p4` | 0.665 | 3 | 5 | 11 | 14 | 14 | shift |
| `h9-track1-image-h9-A-p2` | 0.664 | 3 | 5 | 11 | 15 | 15 | shift |
| `h9-track1-image-h9-B-v1` | 0.664 | 3 | 5 | 11 | 15 | 15 | shift |
| `h9-track1-image-h9-C-img3` | 0.664 | 3 | 5 | 11 | 15 | 15 | shift |
| `h9-track1-image-h9-D-t3` | 0.663 | 3 | 5 | 11 | 15 | 15 | shift |
| `h9-track1-image-h9-C-img2` | 0.663 | 3 | 5 | 11 | 15 | 15 | shift |
| `h9-track2-text-h9-E-p2` | 0.661 | 3 | 5 | 12 | 16 | 16 | shift |
| `h9-track2-text-h9-B-v4` | 0.658 | 3 | 6 | 12 | 16 | 16 | shift |
| `h9-track2-text-h9-E-p4` | 0.658 | 3 | 6 | 12 | 16 | 16 | shift |
| `h9-track1-image-h9-D-t4` | 0.657 | 3 | 6 | 13 | 17 | 17 | shift |
| `h9-track1-image-h9-E-p5` | 0.656 | 3 | 6 | 13 | 17 | 17 | shift |
| `h9-track1-image-h9-B-v2` | 0.655 | 3 | 6 | 13 | 17 | 17 | shift |
| `h9-track1-image-h9-E-p1` | 0.652 | 4 | 6 | 13 | 17 | 17 | shift |
| `h9-track2-text-h9-E-p5` | 0.650 | 4 | 7 | 14 | 18 | 18 | shift |
| `h9-track1-image-h9-B-v5` | 0.649 | 4 | 8 | 15 | 19 | 19 | shift |
| `h9-track1-image-h9-A-p3` | 0.644 | 4 | 9 | 17 | 21 | 21 | shift |
| `h1-brief-text` | 0.644 | 4 | 9 | 16 | 20 | 20 | shift |
| `h7-track2-text-T0.0` | 0.643 | 4 | 9 | 18 | 22 | 22 | shift |
| `h7-track2-text-T1.0` | 0.643 | 4 | 9 | 18 | 22 | 22 | shift |
| `h9-track1-image-h9-E-p4` | 0.642 | 4 | 10 | 19 | 23 | 23 | shift |
| `h9-track1-image-h9-C-img1` | 0.641 | 4 | 10 | 19 | 23 | 23 | shift |
| `h7-track2-text-T1.3` | 0.640 | 4 | 11 | 20 | 24 | 24 | shift |
| `h9-track1-image-h9-B-v3` | 0.640 | 4 | 11 | 21 | 25 | 25 | shift |
| `h7-track1-image-T1.0` | 0.640 | 4 | 11 | 21 | 25 | 25 | shift |
| `h9-track2-text-h9-B-v3` | 0.635 | 4 | 12 | 22 | 26 | 26 | shift |
| `h7-track1-image-T0.3` | 0.634 | 4 | 12 | 23 | 27 | 27 | shift |
| `h9-track1-image-h9-B-v4` | 0.632 | 4 | 13 | 23 | 28 | 28 | shift |
| `h9-track1-image-h9-E-p3` | 0.628 | 4 | 13 | 23 | 28 | 28 | shift |
| `h1-verbose-text-image` | 0.627 | 4 | 13 | 23 | 28 | 28 | shift |
| `h1-brief-text-image` | 0.624 | 4 | 13 | 23 | 28 | 28 | shift |
| `h7-track1-image-T0.7` | 0.620 | 4 | 13 | 23 | 28 | 28 | shift |
| `h7-track1-image-T0.0` | 0.613 | 4 | 14 | 24 | 29 | 29 | shift |
| `h9-track2-text-h9-E-p3` | 0.612 | 4 | 14 | 24 | 30 | 30 | shift |
| `h7-track1-image-T1.3` | 0.606 | 5 | 14 | 25 | 31 | 31 | shift |
| `h1-verbose-text` | 0.596 | 5 | 15 | 26 | 32 | 32 | shift |
| `h1-image-only` | 0.575 | 5 | 15 | 27 | 33 | 33 | shift |
| `h11-bridge-brief-text-t0` | 0.515 | 6 | 16 | 28 | 34 | 34 | shift |

