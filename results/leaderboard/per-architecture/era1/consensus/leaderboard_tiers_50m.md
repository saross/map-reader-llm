# Leaderboard — Era 1, Consensus (no PV), 50 m buffer

**Generated**: 2026-08-20T06:34:06.324490+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 72 in 6 tier(s). Bounds: `inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.809–0.814)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h3-high-track2-text-T1.0 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.809 [0.784, 0.832] | 0.898 | 0.737 | — |
| 2 | h3-high-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.813 [0.794, 0.836] | 0.850 | 0.779 | — |
| 3 | h3-high-track2-text-T0.7 | text | 30 | 22 | gemini-3-flash | detect_brief-text-high | — | — | 0.814 [0.792, 0.834] | 0.866 | 0.768 | — |
| 4 | h3-rep-high | text | 30 | 21 | gemini-3-flash | detect_brief-text-high | — | — | 0.812 [0.791, 0.831] | 0.827 | 0.798 | — |

## Tier 2 (F1: 0.735–0.781)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 5 | h9-track2-text-h9-D-t4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.778 [0.752, 0.800] | 0.786 | 0.770 | — |
| 6 | h9-track2-text-h9-D-t1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.781 [0.760, 0.802] | 0.753 | 0.811 | — |
| 7 | h9-track2-text-h9-A-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.772 [0.750, 0.796] | 0.755 | 0.790 | — |
| 8 | h9-track2-text-h9-A-p1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.778 [0.753, 0.798] | 0.776 | 0.779 | — |
| 9 | h9-track2-text-h9-A-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.778 [0.755, 0.803] | 0.766 | 0.790 | — |
| 10 | h9-track2-text-h9-E-p1 | text | 5 | 5 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.739 [0.714, 0.764] | 0.792 | 0.692 | — |
| 11 | h9-track2-text-h9-D-t2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.770 [0.745, 0.793] | 0.749 | 0.792 | — |
| 12 | h9-track2-text-h9-A-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.752 [0.725, 0.777] | 0.737 | 0.768 | — |
| 13 | h9-track2-text-h9-D-t3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.780 [0.753, 0.804] | 0.765 | 0.796 | — |
| 14 | h9-track2-text-h9-D-t5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.756 [0.731, 0.777] | 0.774 | 0.738 | — |
| 15 | h9-track2-text-h9-A-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.764 [0.740, 0.786] | 0.746 | 0.783 | — |
| 16 | h3-rep-minimal | text | 30 | 25 | gemini-3-flash | detect_brief-text | — | — | 0.735 [0.710, 0.759] | 0.703 | 0.770 | — |

## Tier 3 (F1: 0.707–0.807)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 17 | h9-track2-text-h9-B-v1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.740 [0.712, 0.765] | 0.699 | 0.785 | — |
| 18 | h3-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text | — | — | 0.727 [0.699, 0.753] | 0.658 | 0.813 | — |
| 19 | h3-track2-text-T0.7 | text | 30 | 24 | gemini-3-flash | detect_brief-text | — | — | 0.728 [0.702, 0.753] | 0.683 | 0.779 | — |
| 20 | h3-track1-image-T0.7 | image | 30 | 18 | gemini-3-flash | library_plus-hp | — | — | 0.790 [0.771, 0.809] | 0.792 | 0.787 | — |
| 21 | h9-track1-image-h9-C-img5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img5 | — | — | 0.793 [0.774, 0.817] | 0.824 | 0.764 | — |
| 22 | h7-track2-text-T0.7 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.722 [0.695, 0.746] | 0.681 | 0.768 | — |
| 23 | h3-track2-text-T1.0 | text | 30 | 22 | gemini-3-flash | detect_brief-text | — | — | 0.723 [0.694, 0.749] | 0.685 | 0.764 | — |
| 24 | h7-track2-text-T0.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.729 [0.699, 0.753] | 0.669 | 0.801 | — |
| 25 | h9-track1-image-h9-A-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.802 [0.778, 0.824] | 0.824 | 0.781 | — |
| 26 | h9-track1-image-h9-A-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.806 [0.781, 0.828] | 0.832 | 0.781 | — |
| 27 | h3-track1-image-T1.0 | image | 30 | 19 | gemini-3-flash | library_plus-hp | — | — | 0.762 [0.742, 0.786] | 0.817 | 0.714 | — |
| 28 | h9-track1-image-h9-E-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p2 | — | — | 0.807 [0.790, 0.826] | 0.820 | 0.794 | — |
| 29 | h9-track2-text-h9-B-v2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.707 [0.678, 0.734] | 0.707 | 0.707 | — |
| 30 | h9-track1-image-h9-D-t2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.795 [0.774, 0.815] | 0.797 | 0.794 | — |
| 31 | h9-track1-image-h9-C-img4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img4 | — | — | 0.802 [0.784, 0.823] | 0.815 | 0.790 | — |
| 32 | h9-track1-image-h9-D-t5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.795 [0.774, 0.816] | 0.830 | 0.762 | — |
| 33 | h9-track1-image-h9-D-t1 | image | 5 | 4 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.763 [0.740, 0.785] | 0.887 | 0.670 | — |
| 34 | h9-track2-text-h9-B-v5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.717 [0.692, 0.744] | 0.742 | 0.694 | — |
| 35 | h3-track1-image-T0.3 | image | 30 | 22 | gemini-3-flash | library_plus-hp | — | — | 0.771 [0.753, 0.794] | 0.755 | 0.788 | — |
| 36 | h9-track1-image-h9-A-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.792 [0.770, 0.816] | 0.802 | 0.783 | — |
| 37 | h9-track1-image-h9-A-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.807 [0.790, 0.827] | 0.810 | 0.805 | — |
| 38 | h9-track1-image-h9-B-v1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v1 | — | — | 0.790 [0.772, 0.811] | 0.780 | 0.801 | — |
| 39 | h9-track1-image-h9-C-img3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img3 | — | — | 0.801 [0.779, 0.822] | 0.805 | 0.798 | — |
| 40 | h9-track1-image-h9-D-t3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.793 [0.772, 0.816] | 0.808 | 0.779 | — |
| 41 | h9-track1-image-h9-C-img2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img2 | — | — | 0.796 [0.775, 0.817] | 0.831 | 0.764 | — |
| 42 | h9-track2-text-h9-E-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.718 [0.693, 0.745] | 0.705 | 0.731 | — |
| 43 | h9-track2-text-h9-B-v4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.709 [0.681, 0.734] | 0.722 | 0.698 | — |
| 44 | h9-track2-text-h9-E-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.711 [0.685, 0.738] | 0.722 | 0.699 | — |
| 45 | h9-track1-image-h9-D-t4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.772 [0.750, 0.796] | 0.798 | 0.748 | — |
| 46 | h9-track1-image-h9-E-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p5 | — | — | 0.783 [0.760, 0.803] | 0.812 | 0.755 | — |
| 47 | h9-track1-image-h9-B-v2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v2 | — | — | 0.790 [0.767, 0.809] | 0.810 | 0.770 | — |

## Tier 4 (F1: 0.676–0.788)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 48 | h9-track1-image-h9-E-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p1 | — | — | 0.775 [0.757, 0.797] | 0.738 | 0.816 | — |
| 49 | h9-track2-text-h9-E-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.705 [0.673, 0.730] | 0.748 | 0.666 | — |
| 50 | h9-track1-image-h9-B-v5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v5 | — | — | 0.787 [0.767, 0.805] | 0.789 | 0.785 | — |
| 51 | h1-brief-text | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.693 [0.666, 0.720] | 0.674 | 0.712 | — |
| 52 | h9-track1-image-h9-A-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.779 [0.757, 0.801] | 0.777 | 0.781 | — |
| 53 | h7-track2-text-T0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.696 [0.665, 0.724] | 0.584 | 0.861 | — |
| 54 | h7-track2-text-T1.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.687 [0.661, 0.714] | 0.676 | 0.698 | — |
| 55 | h9-track1-image-h9-E-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p4 | — | — | 0.774 [0.754, 0.798] | 0.799 | 0.751 | — |
| 56 | h9-track1-image-h9-C-img1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img1 | — | — | 0.785 [0.765, 0.809] | 0.794 | 0.777 | — |
| 57 | h7-track2-text-T1.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.682 [0.656, 0.713] | 0.686 | 0.677 | — |
| 58 | h9-track1-image-h9-B-v3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v3 | — | — | 0.785 [0.764, 0.808] | 0.785 | 0.785 | — |
| 59 | h7-track1-image-T1.0 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.760 [0.737, 0.779] | 0.708 | 0.820 | — |
| 60 | h9-track2-text-h9-B-v3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.685 [0.657, 0.711] | 0.682 | 0.688 | — |
| 61 | h7-track1-image-T0.3 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.751 [0.730, 0.773] | 0.736 | 0.766 | — |
| 62 | h9-track1-image-h9-B-v4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v4 | — | — | 0.788 [0.766, 0.809] | 0.790 | 0.787 | — |
| 63 | h9-track1-image-h9-E-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p3 | — | — | 0.773 [0.755, 0.794] | 0.775 | 0.772 | — |
| 64 | h1-verbose-text-image | image | 3 | 2 | gemini-3-flash | detect_verbose-text-image | — | — | 0.763 [0.741, 0.784] | 0.719 | 0.813 | — |
| 65 | h1-brief-text-image | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.758 [0.737, 0.779] | 0.707 | 0.816 | — |
| 66 | h7-track1-image-T0.7 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.756 [0.736, 0.780] | 0.684 | 0.844 | — |
| 67 | h7-track1-image-T0.0 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.737 [0.717, 0.757] | 0.649 | 0.852 | — |
| 68 | h9-track2-text-h9-E-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.676 [0.645, 0.702] | 0.665 | 0.686 | — |

## Tier 5 (F1: 0.674–0.755)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 69 | h7-track1-image-T1.3 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.755 [0.736, 0.776] | 0.721 | 0.794 | — |
| 70 | h1-verbose-text | text | 3 | 2 | gemini-3-flash | detect_verbose-text | — | — | 0.674 [0.642, 0.705] | 0.577 | 0.811 | — |
| 71 | h1-image-only | image | 3 | 2 | gemini-3-flash | detect_image-only | — | — | 0.736 [0.712, 0.760] | 0.684 | 0.796 | — |

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
