# Tier stability (F1) — combined era1

**Metric**: F1
**Stratum**: combined / era1
**Conditions**: 93

## Methodology

For each condition the table records the tier index assigned at each of the 5 buffer tier tables ([20, 30, 40, 50, 100] m). Spearman's rho is computed between the rank vector of tier assignments at 20 m and that at each other buffer. A rho of 1.0 means perfect rank-stability (no condition crosses a tier boundary across that buffer change); lower values surface buffer-dependent tier reorganisations.

**F1 tiers are constructed independently at each buffer.** Per-cell thresholds are fixed at the primary buffer (20 m) via the `--threshold-buffer` flag of `build_tiered_leaderboard.py`; pairwise permutation tests and greedy-clique tier construction then run at each of [20, 30, 40, 50, 100] m using those fixed thresholds (Option A semantics). Spearman rho values reported below are therefore substantive — they surface buffer-dependent tier reorganisations rather than a tautology.

Note: ties (all conditions in one tier) make Spearman's rho undefined; the rho column reports `nan` in that case.

## Spearman rank correlation summary

| vs buffer | Spearman rho | p-value |
|---:|---:|---:|
| 30 m | +0.9633 | 0.0000 |
| 40 m | +0.9657 | 0.0000 |
| 50 m | +0.9657 | 0.0000 |
| 100 m | +0.9655 | 0.0000 |

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
| `h9-track2-text-h9-E-p1` | 0.717 | 2 | 3 | 3 | 3 | 3 | shift |
| `h9-track2-text-h9-D-t2` | 0.712 | 2 | 3 | 3 | 3 | 3 | shift |
| `h9-track2-text-h9-A-p5` | 0.712 | 2 | 3 | 3 | 3 | 3 | shift |
| `h9-track2-text-h9-D-t3` | 0.711 | 2 | 3 | 3 | 3 | 3 | shift |
| `h9-track2-text-h9-D-t5` | 0.710 | 2 | 3 | 3 | 3 | 3 | shift |
| `h9-track2-text-h9-A-p3` | 0.710 | 2 | 3 | 3 | 3 | 3 | shift |
| `h3-rep-minimal` | 0.703 | 2 | 3 | 3 | 4 | 4 | shift |
| `h9-track2-text-h9-B-v1` | 0.698 | 3 | 3 | 3 | 4 | 4 | shift |
| `h3-track2-text-T0.3` | 0.692 | 3 | 3 | 4 | 4 | 4 | shift |
| `h3-track2-text-T0.7` | 0.692 | 3 | 3 | 4 | 4 | 4 | shift |
| `h3-track1-image-T0.7` | 0.691 | 3 | 3 | 5 | 5 | 5 | shift |
| `h9-track1-image-h9-C-img5` | 0.689 | 3 | 3 | 5 | 5 | 5 | shift |
| `h7-track2-text-T0.7` | 0.687 | 3 | 3 | 6 | 6 | 6 | shift |
| `h3-track2-text-T1.0` | 0.686 | 3 | 4 | 6 | 6 | 6 | shift |
| `h7-track2-text-T0.3` | 0.683 | 3 | 4 | 6 | 6 | 6 | shift |
| `h9-track1-image-h9-A-p1` | 0.682 | 3 | 4 | 7 | 7 | 7 | shift |
| `h9-track1-image-h9-A-p5` | 0.679 | 3 | 4 | 7 | 7 | 7 | shift |
| `h3-track1-image-T1.0` | 0.679 | 3 | 4 | 8 | 8 | 8 | shift |
| `h9-track1-image-h9-E-p2` | 0.675 | 3 | 4 | 9 | 9 | 9 | shift |
| `h9-track2-text-h9-B-v2` | 0.673 | 3 | 5 | 10 | 10 | 10 | shift |
| `h9-track1-image-h9-D-t2` | 0.673 | 3 | 6 | 11 | 11 | 11 | shift |
| `h9-track1-image-h9-C-img4` | 0.672 | 3 | 6 | 11 | 11 | 11 | shift |
| `h9-track1-image-h9-D-t5` | 0.669 | 3 | 6 | 11 | 11 | 11 | shift |
| `h9-track1-image-h9-D-t1` | 0.668 | 3 | 6 | 11 | 12 | 12 | shift |
| `h9-track2-text-h9-B-v5` | 0.667 | 3 | 6 | 12 | 13 | 13 | shift |
| `h3-track1-image-T0.3` | 0.666 | 3 | 6 | 13 | 14 | 14 | shift |
| `h9-track1-image-h9-A-p4` | 0.665 | 3 | 6 | 13 | 14 | 14 | shift |
| `h9-track1-image-h9-B-v1` | 0.664 | 3 | 6 | 13 | 15 | 15 | shift |
| `h9-track1-image-h9-A-p2` | 0.664 | 3 | 6 | 13 | 15 | 15 | shift |
| `h9-track1-image-h9-C-img3` | 0.664 | 3 | 6 | 13 | 15 | 15 | shift |
| `h9-track1-image-h9-D-t3` | 0.663 | 3 | 6 | 13 | 15 | 15 | shift |
| `h9-track1-image-h9-C-img2` | 0.663 | 3 | 7 | 13 | 15 | 15 | shift |
| `h9-track2-text-h9-E-p2` | 0.661 | 3 | 7 | 14 | 16 | 16 | shift |
| `h9-track2-text-h9-B-v4` | 0.658 | 3 | 8 | 14 | 16 | 16 | shift |
| `h9-track2-text-h9-E-p4` | 0.658 | 3 | 8 | 14 | 16 | 16 | shift |
| `h9-track1-image-h9-D-t4` | 0.657 | 3 | 8 | 15 | 17 | 17 | shift |
| `h9-track1-image-h9-E-p5` | 0.656 | 3 | 9 | 15 | 17 | 17 | shift |
| `h9-track1-image-h9-B-v2` | 0.655 | 3 | 9 | 15 | 17 | 17 | shift |
| `h9-track1-image-h9-E-p1` | 0.652 | 4 | 9 | 15 | 17 | 17 | shift |
| `h9-track2-text-h9-E-p5` | 0.650 | 4 | 10 | 16 | 18 | 18 | shift |
| `h9-track1-image-h9-B-v5` | 0.649 | 4 | 11 | 17 | 19 | 19 | shift |
| `h9-track1-image-h9-A-p3` | 0.644 | 4 | 12 | 19 | 21 | 21 | shift |
| `h1-brief-text` | 0.644 | 4 | 12 | 18 | 20 | 20 | shift |
| `h7-track2-text-T0.0` | 0.643 | 4 | 12 | 20 | 22 | 22 | shift |
| `h7-track2-text-T1.0` | 0.643 | 4 | 12 | 20 | 22 | 22 | shift |
| `h9-track1-image-h9-E-p4` | 0.642 | 4 | 13 | 21 | 23 | 23 | shift |
| `h9-track1-image-h9-C-img1` | 0.641 | 4 | 13 | 21 | 23 | 23 | shift |
| `h7-track2-text-T1.3` | 0.640 | 4 | 14 | 22 | 24 | 24 | shift |
| `h9-track1-image-h9-B-v3` | 0.640 | 4 | 14 | 23 | 25 | 25 | shift |
| `h7-track1-image-T1.0` | 0.640 | 4 | 14 | 23 | 25 | 25 | shift |
| `h9-track2-text-h9-B-v3` | 0.635 | 4 | 15 | 24 | 26 | 26 | shift |
| `h7-track1-image-T0.3` | 0.634 | 4 | 15 | 25 | 27 | 27 | shift |
| `h9-track1-image-h9-B-v4` | 0.632 | 4 | 16 | 25 | 28 | 28 | shift |
| `h4-canonical-last` | 0.631 | 4 | 16 | 26 | 29 | 29 | shift |
| `h9-track1-image-h9-E-p3` | 0.628 | 4 | 16 | 26 | 30 | 30 | shift |
| `h1-verbose-text-image` | 0.627 | 4 | 16 | 26 | 30 | 30 | shift |
| `h1-brief-text-image` | 0.624 | 4 | 16 | 26 | 30 | 30 | shift |
| `h7-track1-image-T0.7` | 0.620 | 4 | 16 | 26 | 30 | 30 | shift |
| `h7-track1-image-T0.0` | 0.613 | 4 | 17 | 27 | 31 | 30 | shift |
| `h9-track2-text-h9-E-p3` | 0.612 | 4 | 17 | 27 | 32 | 31 | shift |
| `h8-track2-text-scale-4` | 0.609 | 5 | 17 | 28 | 32 | 31 | shift |
| `h8-track2-text-scale-8` | 0.607 | 5 | 17 | 28 | 32 | 31 | shift |
| `h4-config-default` | 0.606 | 5 | 17 | 29 | 33 | 32 | shift |
| `h7-track1-image-T1.3` | 0.606 | 5 | 18 | 29 | 33 | 32 | shift |
| `h5-track1-image-terse` | 0.605 | 5 | 19 | 30 | 34 | 33 | shift |
| `h8-track2-text-pure-positive-canon` | 0.605 | 5 | 19 | 30 | 35 | 34 | shift |
| `h8-track2-text-canonical` | 0.605 | 5 | 19 | 30 | 35 | 34 | shift |
| `h5-track1-image-verbose` | 0.603 | 5 | 19 | 31 | 36 | 35 | shift |
| `h8-track1-image-plus-hp` | 0.599 | 5 | 19 | 31 | 36 | 35 | shift |
| `h8-track1-image-exploratory-pure-positive-4hp` | 0.599 | 5 | 19 | 31 | 36 | 35 | shift |
| `h4-canonical-first` | 0.599 | 5 | 19 | 31 | 36 | 35 | shift |
| `h5-track2-text-terse` | 0.598 | 5 | 19 | 32 | 37 | 36 | shift |
| `h8-track2-text-plus-hp` | 0.597 | 5 | 19 | 32 | 37 | 36 | shift |
| `h1-verbose-text` | 0.596 | 5 | 19 | 32 | 37 | 36 | shift |
| `h8-track1-image-scale-8` | 0.587 | 5 | 19 | 32 | 37 | 37 | shift |
| `h8-track1-image-scale-4` | 0.584 | 5 | 19 | 32 | 37 | 37 | shift |
| `h5-track2-text-verbose` | 0.583 | 5 | 19 | 32 | 37 | 38 | shift |
| `h8-track1-image-canonical` | 0.581 | 5 | 19 | 32 | 37 | 38 | shift |
| `h1-image-only` | 0.575 | 5 | 19 | 33 | 38 | 39 | shift |
| `h8-track1-image-exploratory-pure-positive-2hp` | 0.571 | 5 | 19 | 34 | 39 | 40 | shift |
| `h4-random` | 0.571 | 5 | 19 | 34 | 39 | 40 | shift |
| `h8-track1-image-exploratory-pure-positive-canon` | 0.570 | 5 | 19 | 34 | 39 | 40 | shift |
| `h8-track1-image-pure-positive-canon` | 0.568 | 6 | 19 | 34 | 39 | 40 | shift |
| `h11-bridge-brief-text-t0` | 0.515 | 6 | 20 | 35 | 40 | 41 | shift |

