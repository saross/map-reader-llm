# Leaderboard — Era 1, Consensus (no PV), 40 m buffer

**Generated**: 2026-05-06T00:25:57.052810+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 72 in 6 tier(s). Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.807–0.812)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h3-high-track2-text-T1.0 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.807 [0.783, 0.829] | 0.896 | 0.735 | — |
| 2 | h3-high-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.811 [0.793, 0.834] | 0.848 | 0.777 | — |
| 3 | h3-high-track2-text-T0.7 | text | 30 | 22 | gemini-3-flash | detect_brief-text-high | — | — | 0.812 [0.790, 0.833] | 0.864 | 0.766 | — |
| 4 | h3-rep-high | text | 30 | 21 | gemini-3-flash | detect_brief-text-high | — | — | 0.810 [0.787, 0.829] | 0.825 | 0.796 | — |

## Tier 2 (F1: 0.732–0.776)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 5 | h9-track2-text-h9-D-t4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.776 [0.752, 0.800] | 0.784 | 0.768 | — |
| 6 | h9-track2-text-h9-D-t1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.776 [0.754, 0.796] | 0.748 | 0.805 | — |
| 7 | h9-track2-text-h9-A-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.767 [0.745, 0.792] | 0.750 | 0.785 | — |
| 8 | h9-track2-text-h9-A-p1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.774 [0.751, 0.797] | 0.773 | 0.775 | — |
| 9 | h9-track2-text-h9-A-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.776 [0.755, 0.801] | 0.764 | 0.788 | — |
| 10 | h9-track2-text-h9-E-p1 | text | 5 | 5 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.739 [0.714, 0.764] | 0.792 | 0.692 | — |
| 11 | h9-track2-text-h9-D-t2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.768 [0.742, 0.791] | 0.747 | 0.790 | — |
| 12 | h9-track2-text-h9-A-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.752 [0.725, 0.777] | 0.737 | 0.768 | — |
| 13 | h9-track2-text-h9-D-t3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.773 [0.745, 0.798] | 0.758 | 0.788 | — |
| 14 | h9-track2-text-h9-D-t5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.754 [0.730, 0.776] | 0.772 | 0.737 | — |
| 15 | h9-track2-text-h9-A-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.757 [0.733, 0.780] | 0.739 | 0.775 | — |
| 16 | h3-rep-minimal | text | 30 | 25 | gemini-3-flash | detect_brief-text | — | — | 0.732 [0.706, 0.756] | 0.700 | 0.766 | — |

## Tier 3 (F1: 0.705–0.790)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 17 | h9-track2-text-h9-B-v1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.736 [0.710, 0.761] | 0.696 | 0.781 | — |
| 18 | h3-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text | — | — | 0.724 [0.696, 0.751] | 0.655 | 0.809 | — |
| 19 | h3-track2-text-T0.7 | text | 30 | 24 | gemini-3-flash | detect_brief-text | — | — | 0.726 [0.699, 0.750] | 0.681 | 0.777 | — |
| 20 | h3-track1-image-T0.7 | image | 30 | 18 | gemini-3-flash | library_plus-hp | — | — | 0.776 [0.758, 0.797] | 0.779 | 0.774 | — |
| 21 | h9-track1-image-h9-C-img5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img5 | — | — | 0.780 [0.758, 0.804] | 0.810 | 0.751 | — |
| 22 | h7-track2-text-T0.7 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.717 [0.691, 0.742] | 0.676 | 0.762 | — |
| 23 | h3-track2-text-T1.0 | text | 30 | 22 | gemini-3-flash | detect_brief-text | — | — | 0.719 [0.690, 0.745] | 0.682 | 0.761 | — |
| 24 | h7-track2-text-T0.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.724 [0.693, 0.747] | 0.664 | 0.796 | — |
| 25 | h9-track1-image-h9-A-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.787 [0.764, 0.811] | 0.808 | 0.766 | — |
| 26 | h9-track1-image-h9-A-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.790 [0.767, 0.815] | 0.816 | 0.766 | — |
| 27 | h3-track1-image-T1.0 | image | 30 | 19 | gemini-3-flash | library_plus-hp | — | — | 0.754 [0.732, 0.777] | 0.809 | 0.707 | — |
| 28 | h9-track1-image-h9-E-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p2 | — | — | 0.788 [0.771, 0.809] | 0.801 | 0.775 | — |
| 29 | h9-track2-text-h9-B-v2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.705 [0.676, 0.732] | 0.705 | 0.705 | — |
| 30 | h9-track1-image-h9-D-t2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.788 [0.767, 0.809] | 0.790 | 0.787 | — |
| 31 | h9-track1-image-h9-C-img4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img4 | — | — | 0.785 [0.766, 0.807] | 0.797 | 0.774 | — |
| 32 | h9-track1-image-h9-D-t5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.776 [0.754, 0.799] | 0.810 | 0.744 | — |
| 33 | h9-track1-image-h9-D-t1 | image | 5 | 4 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.755 [0.731, 0.776] | 0.877 | 0.662 | — |
| 34 | h9-track2-text-h9-B-v5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.711 [0.687, 0.738] | 0.736 | 0.688 | — |
| 35 | h3-track1-image-T0.3 | image | 30 | 22 | gemini-3-flash | library_plus-hp | — | — | 0.759 [0.740, 0.780] | 0.743 | 0.775 | — |
| 36 | h9-track1-image-h9-A-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.783 [0.761, 0.808] | 0.793 | 0.774 | — |
| 37 | h9-track1-image-h9-A-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.787 [0.769, 0.808] | 0.789 | 0.785 | — |
| 38 | h9-track1-image-h9-B-v1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v1 | — | — | 0.774 [0.752, 0.796] | 0.763 | 0.785 | — |
| 39 | h9-track1-image-h9-C-img3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img3 | — | — | 0.775 [0.754, 0.799] | 0.779 | 0.772 | — |
| 40 | h9-track1-image-h9-D-t3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.782 [0.759, 0.807] | 0.796 | 0.768 | — |
| 41 | h9-track1-image-h9-C-img2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img2 | — | — | 0.779 [0.754, 0.803] | 0.812 | 0.748 | — |
| 42 | h9-track2-text-h9-E-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.716 [0.691, 0.744] | 0.703 | 0.729 | — |
| 43 | h9-track2-text-h9-B-v4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.706 [0.677, 0.730] | 0.718 | 0.694 | — |
| 44 | h9-track2-text-h9-E-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.705 [0.677, 0.732] | 0.717 | 0.694 | — |
| 45 | h9-track1-image-h9-D-t4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.760 [0.737, 0.785] | 0.786 | 0.737 | — |
| 46 | h9-track1-image-h9-E-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p5 | — | — | 0.771 [0.747, 0.792] | 0.800 | 0.744 | — |
| 47 | h9-track1-image-h9-B-v2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v2 | — | — | 0.774 [0.752, 0.795] | 0.795 | 0.755 | — |

## Tier 4 (F1: 0.674–0.778)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 48 | h9-track1-image-h9-E-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p1 | — | — | 0.763 [0.743, 0.786] | 0.727 | 0.803 | — |
| 49 | h9-track2-text-h9-E-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.697 [0.667, 0.723] | 0.740 | 0.659 | — |
| 50 | h9-track1-image-h9-B-v5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v5 | — | — | 0.778 [0.759, 0.800] | 0.780 | 0.775 | — |
| 51 | h1-brief-text | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.687 [0.660, 0.714] | 0.668 | 0.707 | — |
| 52 | h9-track1-image-h9-A-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.762 [0.739, 0.784] | 0.760 | 0.764 | — |
| 53 | h7-track2-text-T0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.691 [0.662, 0.720] | 0.580 | 0.855 | — |
| 54 | h7-track2-text-T1.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.683 [0.656, 0.709] | 0.673 | 0.694 | — |
| 55 | h9-track1-image-h9-E-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p4 | — | — | 0.757 [0.733, 0.781] | 0.781 | 0.735 | — |
| 56 | h9-track1-image-h9-C-img1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img1 | — | — | 0.770 [0.749, 0.793] | 0.778 | 0.762 | — |
| 57 | h7-track2-text-T1.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.680 [0.654, 0.711] | 0.684 | 0.675 | — |
| 58 | h9-track1-image-h9-B-v3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v3 | — | — | 0.768 [0.748, 0.793] | 0.768 | 0.768 | — |
| 59 | h7-track1-image-T1.0 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.755 [0.732, 0.775] | 0.704 | 0.815 | — |
| 60 | h9-track2-text-h9-B-v3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.680 [0.650, 0.705] | 0.676 | 0.683 | — |
| 61 | h7-track1-image-T0.3 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.738 [0.717, 0.760] | 0.724 | 0.753 | — |
| 62 | h9-track1-image-h9-B-v4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v4 | — | — | 0.771 [0.751, 0.797] | 0.773 | 0.770 | — |
| 63 | h9-track1-image-h9-E-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p3 | — | — | 0.758 [0.737, 0.780] | 0.760 | 0.757 | — |
| 64 | h1-verbose-text-image | image | 3 | 2 | gemini-3-flash | detect_verbose-text-image | — | — | 0.749 [0.728, 0.769] | 0.706 | 0.798 | — |
| 65 | h1-brief-text-image | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.744 [0.723, 0.766] | 0.695 | 0.801 | — |
| 66 | h7-track1-image-T0.7 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.738 [0.718, 0.764] | 0.668 | 0.824 | — |
| 67 | h7-track1-image-T0.0 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.719 [0.702, 0.743] | 0.634 | 0.831 | — |
| 68 | h9-track2-text-h9-E-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.674 [0.645, 0.702] | 0.664 | 0.685 | — |

## Tier 5 (F1: 0.659–0.738)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 69 | h7-track1-image-T1.3 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.738 [0.717, 0.758] | 0.704 | 0.775 | — |
| 70 | h1-verbose-text | text | 3 | 2 | gemini-3-flash | detect_verbose-text | — | — | 0.659 [0.625, 0.687] | 0.564 | 0.792 | — |
| 71 | h1-image-only | image | 3 | 2 | gemini-3-flash | detect_image-only | — | — | 0.717 [0.691, 0.738] | 0.667 | 0.775 | — |

## Tier 6 (F1: 0.529–0.529)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 72 | h11-bridge-brief-text-t0 | text | 10 | 10 | gemini-3-flash-preview | detect_brief-text | — | — | 0.529 [0.486, 0.563] | 0.423 | 0.707 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
