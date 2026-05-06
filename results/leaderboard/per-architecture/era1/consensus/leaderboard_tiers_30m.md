# Leaderboard — Era 1, Consensus (no PV), 30 m buffer

**Generated**: 2026-05-06T00:25:57.046351+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 72 in 6 tier(s). Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.793–0.804)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h3-high-track2-text-T1.0 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.799 [0.775, 0.820] | 0.887 | 0.727 | — |
| 2 | h3-high-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.798 [0.779, 0.823] | 0.834 | 0.764 | — |
| 3 | h3-high-track2-text-T0.7 | text | 30 | 22 | gemini-3-flash | detect_brief-text-high | — | — | 0.804 [0.783, 0.825] | 0.856 | 0.759 | — |
| 4 | h3-rep-high | text | 30 | 21 | gemini-3-flash | detect_brief-text-high | — | — | 0.793 [0.769, 0.813] | 0.808 | 0.779 | — |

## Tier 2 (F1: 0.728–0.770)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 5 | h9-track2-text-h9-D-t4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.765 [0.738, 0.789] | 0.773 | 0.757 | — |
| 6 | h9-track2-text-h9-D-t1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.770 [0.748, 0.791] | 0.743 | 0.800 | — |
| 7 | h9-track2-text-h9-A-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.760 [0.738, 0.784] | 0.743 | 0.777 | — |
| 8 | h9-track2-text-h9-A-p1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.759 [0.735, 0.781] | 0.758 | 0.761 | — |
| 9 | h9-track2-text-h9-A-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.754 [0.729, 0.779] | 0.743 | 0.766 | — |
| 10 | h9-track2-text-h9-E-p1 | text | 5 | 5 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.731 [0.706, 0.756] | 0.783 | 0.685 | — |
| 11 | h9-track2-text-h9-D-t2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.752 [0.725, 0.775] | 0.732 | 0.774 | — |
| 12 | h9-track2-text-h9-A-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.743 [0.717, 0.770] | 0.728 | 0.759 | — |
| 13 | h9-track2-text-h9-D-t3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.756 [0.727, 0.781] | 0.742 | 0.772 | — |
| 14 | h9-track2-text-h9-D-t5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.746 [0.722, 0.767] | 0.765 | 0.729 | — |
| 15 | h9-track2-text-h9-A-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.746 [0.719, 0.768] | 0.728 | 0.764 | — |
| 16 | h3-rep-minimal | text | 30 | 25 | gemini-3-flash | detect_brief-text | — | — | 0.728 [0.704, 0.754] | 0.697 | 0.762 | — |

## Tier 3 (F1: 0.692–0.756)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 17 | h9-track2-text-h9-B-v1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.727 [0.699, 0.755] | 0.688 | 0.772 | — |
| 18 | h3-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text | — | — | 0.719 [0.691, 0.744] | 0.650 | 0.803 | — |
| 19 | h3-track2-text-T0.7 | text | 30 | 24 | gemini-3-flash | detect_brief-text | — | — | 0.719 [0.693, 0.744] | 0.675 | 0.770 | — |
| 20 | h3-track1-image-T0.7 | image | 30 | 18 | gemini-3-flash | library_plus-hp | — | — | 0.750 [0.729, 0.773] | 0.753 | 0.748 | — |
| 21 | h9-track1-image-h9-C-img5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img5 | — | — | 0.749 [0.726, 0.770] | 0.778 | 0.722 | — |
| 22 | h7-track2-text-T0.7 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.711 [0.686, 0.738] | 0.671 | 0.757 | — |
| 23 | h3-track2-text-T1.0 | text | 30 | 22 | gemini-3-flash | detect_brief-text | — | — | 0.711 [0.682, 0.737] | 0.674 | 0.751 | — |
| 24 | h7-track2-text-T0.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.714 [0.685, 0.738] | 0.655 | 0.785 | — |
| 25 | h9-track1-image-h9-A-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.756 [0.733, 0.782] | 0.777 | 0.737 | — |
| 26 | h9-track1-image-h9-A-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.752 [0.726, 0.778] | 0.777 | 0.729 | — |
| 27 | h3-track1-image-T1.0 | image | 30 | 19 | gemini-3-flash | library_plus-hp | — | — | 0.731 [0.706, 0.756] | 0.783 | 0.685 | — |
| 28 | h9-track1-image-h9-E-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p2 | — | — | 0.745 [0.722, 0.767] | 0.757 | 0.733 | — |
| 29 | h9-track2-text-h9-B-v2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.694 [0.663, 0.721] | 0.694 | 0.694 | — |
| 30 | h9-track1-image-h9-D-t2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.745 [0.722, 0.769] | 0.747 | 0.744 | — |
| 31 | h9-track1-image-h9-C-img4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img4 | — | — | 0.736 [0.714, 0.761] | 0.748 | 0.725 | — |
| 32 | h9-track1-image-h9-D-t5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.747 [0.723, 0.772] | 0.780 | 0.716 | — |
| 33 | h9-track1-image-h9-D-t1 | image | 5 | 4 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.725 [0.701, 0.749] | 0.843 | 0.636 | — |
| 34 | h9-track2-text-h9-B-v5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.702 [0.676, 0.728] | 0.726 | 0.679 | — |
| 35 | h3-track1-image-T0.3 | image | 30 | 22 | gemini-3-flash | library_plus-hp | — | — | 0.724 [0.703, 0.746] | 0.709 | 0.740 | — |
| 36 | h9-track1-image-h9-A-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.732 [0.709, 0.756] | 0.741 | 0.724 | — |
| 37 | h9-track1-image-h9-A-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.735 [0.712, 0.756] | 0.737 | 0.733 | — |
| 38 | h9-track1-image-h9-B-v1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v1 | — | — | 0.745 [0.719, 0.766] | 0.735 | 0.755 | — |
| 39 | h9-track1-image-h9-C-img3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img3 | — | — | 0.740 [0.716, 0.765] | 0.743 | 0.737 | — |
| 40 | h9-track1-image-h9-D-t3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.742 [0.717, 0.767] | 0.756 | 0.729 | — |
| 41 | h9-track1-image-h9-C-img2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img2 | — | — | 0.746 [0.719, 0.772] | 0.778 | 0.716 | — |
| 42 | h9-track2-text-h9-E-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.707 [0.682, 0.735] | 0.694 | 0.720 | — |
| 43 | h9-track2-text-h9-B-v4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.694 [0.666, 0.720] | 0.706 | 0.683 | — |
| 44 | h9-track2-text-h9-E-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.692 [0.664, 0.719] | 0.703 | 0.681 | — |
| 45 | h9-track1-image-h9-D-t4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.726 [0.700, 0.751] | 0.750 | 0.703 | — |
| 46 | h9-track1-image-h9-E-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p5 | — | — | 0.739 [0.713, 0.764] | 0.766 | 0.712 | — |
| 47 | h9-track1-image-h9-B-v2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v2 | — | — | 0.738 [0.715, 0.763] | 0.758 | 0.720 | — |

## Tier 4 (F1: 0.659–0.752)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 48 | h9-track1-image-h9-E-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p1 | — | — | 0.724 [0.702, 0.750] | 0.690 | 0.762 | — |
| 49 | h9-track2-text-h9-E-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.689 [0.660, 0.717] | 0.731 | 0.651 | — |
| 50 | h9-track1-image-h9-B-v5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v5 | — | — | 0.752 [0.728, 0.775] | 0.754 | 0.750 | — |
| 51 | h1-brief-text | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.676 [0.649, 0.706] | 0.658 | 0.696 | — |
| 52 | h9-track1-image-h9-A-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.716 [0.693, 0.742] | 0.714 | 0.718 | — |
| 53 | h7-track2-text-T0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.682 [0.651, 0.711] | 0.572 | 0.844 | — |
| 54 | h7-track2-text-T1.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.674 [0.648, 0.701] | 0.664 | 0.685 | — |
| 55 | h9-track1-image-h9-E-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p4 | — | — | 0.729 [0.705, 0.755] | 0.751 | 0.707 | — |
| 56 | h9-track1-image-h9-C-img1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img1 | — | — | 0.735 [0.714, 0.762] | 0.742 | 0.727 | — |
| 57 | h7-track2-text-T1.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.676 [0.649, 0.708] | 0.680 | 0.672 | — |
| 58 | h9-track1-image-h9-B-v3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v3 | — | — | 0.725 [0.703, 0.751] | 0.725 | 0.725 | — |
| 59 | h7-track1-image-T1.0 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.717 [0.695, 0.740] | 0.668 | 0.774 | — |
| 60 | h9-track2-text-h9-B-v3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.674 [0.645, 0.700] | 0.671 | 0.677 | — |
| 61 | h7-track1-image-T0.3 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.713 [0.690, 0.737] | 0.699 | 0.727 | — |
| 62 | h9-track1-image-h9-B-v4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v4 | — | — | 0.725 [0.701, 0.749] | 0.726 | 0.724 | — |
| 63 | h9-track1-image-h9-E-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p3 | — | — | 0.731 [0.708, 0.752] | 0.732 | 0.729 | — |
| 64 | h1-verbose-text-image | image | 3 | 2 | gemini-3-flash | detect_verbose-text-image | — | — | 0.700 [0.677, 0.724] | 0.660 | 0.746 | — |
| 65 | h1-brief-text-image | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.720 [0.699, 0.741] | 0.672 | 0.775 | — |
| 66 | h7-track1-image-T0.7 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.711 [0.690, 0.737] | 0.644 | 0.794 | — |
| 67 | h7-track1-image-T0.0 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.687 [0.667, 0.713] | 0.605 | 0.794 | — |
| 68 | h9-track2-text-h9-E-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.659 [0.631, 0.687] | 0.649 | 0.670 | — |

## Tier 5 (F1: 0.633–0.708)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 69 | h7-track1-image-T1.3 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.708 [0.687, 0.732] | 0.675 | 0.744 | — |
| 70 | h1-verbose-text | text | 3 | 2 | gemini-3-flash | detect_verbose-text | — | — | 0.633 [0.600, 0.661] | 0.542 | 0.761 | — |
| 71 | h1-image-only | image | 3 | 2 | gemini-3-flash | detect_image-only | — | — | 0.671 [0.646, 0.697] | 0.624 | 0.725 | — |

## Tier 6 (F1: 0.525–0.525)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 72 | h11-bridge-brief-text-t0 | text | 10 | 10 | gemini-3-flash-preview | detect_brief-text | — | — | 0.525 [0.482, 0.559] | 0.419 | 0.701 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
