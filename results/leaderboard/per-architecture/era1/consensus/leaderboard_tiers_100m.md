# Leaderboard — Era 1, Consensus (no PV), 100 m buffer

**Generated**: 2026-08-20T06:34:06.333645+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 72 in 6 tier(s). Bounds: `inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.811–0.816)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h3-high-track2-text-T1.0 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.811 [0.787, 0.833] | 0.900 | 0.738 | — |
| 2 | h3-high-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.815 [0.796, 0.838] | 0.852 | 0.781 | — |
| 3 | h3-high-track2-text-T0.7 | text | 30 | 22 | gemini-3-flash | detect_brief-text-high | — | — | 0.816 [0.795, 0.836] | 0.868 | 0.770 | — |
| 4 | h3-rep-high | text | 30 | 21 | gemini-3-flash | detect_brief-text-high | — | — | 0.814 [0.792, 0.833] | 0.829 | 0.800 | — |

## Tier 2 (F1: 0.735–0.784)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 5 | h9-track2-text-h9-D-t4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.780 [0.755, 0.801] | 0.788 | 0.772 | — |
| 6 | h9-track2-text-h9-D-t1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.781 [0.760, 0.802] | 0.753 | 0.811 | — |
| 7 | h9-track2-text-h9-A-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.772 [0.750, 0.796] | 0.755 | 0.790 | — |
| 8 | h9-track2-text-h9-A-p1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.780 [0.757, 0.800] | 0.778 | 0.781 | — |
| 9 | h9-track2-text-h9-A-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.784 [0.762, 0.809] | 0.772 | 0.796 | — |
| 10 | h9-track2-text-h9-E-p1 | text | 5 | 5 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.745 [0.720, 0.768] | 0.798 | 0.698 | — |
| 11 | h9-track2-text-h9-D-t2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.774 [0.749, 0.797] | 0.753 | 0.796 | — |
| 12 | h9-track2-text-h9-A-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.756 [0.729, 0.780] | 0.740 | 0.772 | — |
| 13 | h9-track2-text-h9-D-t3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.780 [0.753, 0.804] | 0.765 | 0.796 | — |
| 14 | h9-track2-text-h9-D-t5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.758 [0.734, 0.780] | 0.776 | 0.740 | — |
| 15 | h9-track2-text-h9-A-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.767 [0.744, 0.790] | 0.749 | 0.787 | — |
| 16 | h3-rep-minimal | text | 30 | 25 | gemini-3-flash | detect_brief-text | — | — | 0.735 [0.710, 0.759] | 0.703 | 0.770 | — |

## Tier 3 (F1: 0.711–0.825)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 17 | h9-track2-text-h9-B-v1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.747 [0.721, 0.773] | 0.706 | 0.792 | — |
| 18 | h3-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text | — | — | 0.730 [0.700, 0.755] | 0.661 | 0.816 | — |
| 19 | h3-track2-text-T0.7 | text | 30 | 24 | gemini-3-flash | detect_brief-text | — | — | 0.728 [0.702, 0.753] | 0.683 | 0.779 | — |
| 20 | h3-track1-image-T0.7 | image | 30 | 18 | gemini-3-flash | library_plus-hp | — | — | 0.803 [0.784, 0.822] | 0.806 | 0.800 | — |
| 21 | h9-track1-image-h9-C-img5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img5 | — | — | 0.808 [0.790, 0.830] | 0.840 | 0.779 | — |
| 22 | h7-track2-text-T0.7 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.722 [0.695, 0.746] | 0.681 | 0.768 | — |
| 23 | h3-track2-text-T1.0 | text | 30 | 22 | gemini-3-flash | detect_brief-text | — | — | 0.723 [0.694, 0.749] | 0.685 | 0.764 | — |
| 24 | h7-track2-text-T0.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.733 [0.701, 0.756] | 0.672 | 0.805 | — |
| 25 | h9-track1-image-h9-A-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.811 [0.790, 0.834] | 0.834 | 0.790 | — |
| 26 | h9-track1-image-h9-A-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.825 [0.803, 0.844] | 0.852 | 0.800 | — |
| 27 | h3-track1-image-T1.0 | image | 30 | 19 | gemini-3-flash | library_plus-hp | — | — | 0.766 [0.746, 0.789] | 0.822 | 0.718 | — |
| 28 | h9-track1-image-h9-E-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p2 | — | — | 0.818 [0.803, 0.835] | 0.831 | 0.805 | — |
| 29 | h9-track2-text-h9-B-v2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.711 [0.682, 0.737] | 0.711 | 0.711 | — |
| 30 | h9-track1-image-h9-D-t2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.807 [0.787, 0.825] | 0.808 | 0.805 | — |
| 31 | h9-track1-image-h9-C-img4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img4 | — | — | 0.808 [0.789, 0.829] | 0.820 | 0.796 | — |
| 32 | h9-track1-image-h9-D-t5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.810 [0.791, 0.832] | 0.847 | 0.777 | — |
| 33 | h9-track1-image-h9-D-t1 | image | 5 | 4 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.774 [0.750, 0.795] | 0.899 | 0.679 | — |
| 34 | h9-track2-text-h9-B-v5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.721 [0.696, 0.745] | 0.746 | 0.698 | — |
| 35 | h3-track1-image-T0.3 | image | 30 | 22 | gemini-3-flash | library_plus-hp | — | — | 0.780 [0.759, 0.802] | 0.764 | 0.798 | — |
| 36 | h9-track1-image-h9-A-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.802 [0.777, 0.824] | 0.812 | 0.792 | — |
| 37 | h9-track1-image-h9-A-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.822 [0.805, 0.840] | 0.825 | 0.820 | — |
| 38 | h9-track1-image-h9-B-v1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v1 | — | — | 0.807 [0.788, 0.828] | 0.796 | 0.818 | — |
| 39 | h9-track1-image-h9-C-img3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img3 | — | — | 0.811 [0.791, 0.834] | 0.815 | 0.807 | — |
| 40 | h9-track1-image-h9-D-t3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.806 [0.786, 0.828] | 0.821 | 0.792 | — |
| 41 | h9-track1-image-h9-C-img2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img2 | — | — | 0.814 [0.792, 0.835] | 0.849 | 0.781 | — |
| 42 | h9-track2-text-h9-E-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.721 [0.697, 0.748] | 0.708 | 0.735 | — |
| 43 | h9-track2-text-h9-B-v4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.715 [0.685, 0.737] | 0.727 | 0.703 | — |
| 44 | h9-track2-text-h9-E-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.713 [0.687, 0.742] | 0.724 | 0.701 | — |
| 45 | h9-track1-image-h9-D-t4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.791 [0.768, 0.813] | 0.818 | 0.766 | — |
| 46 | h9-track1-image-h9-E-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p5 | — | — | 0.794 [0.771, 0.813] | 0.824 | 0.766 | — |
| 47 | h9-track1-image-h9-B-v2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v2 | — | — | 0.801 [0.778, 0.820] | 0.822 | 0.781 | — |

## Tier 4 (F1: 0.681–0.807)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 48 | h9-track1-image-h9-E-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p1 | — | — | 0.796 [0.779, 0.817] | 0.758 | 0.839 | — |
| 49 | h9-track2-text-h9-E-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.707 [0.676, 0.732] | 0.750 | 0.668 | — |
| 50 | h9-track1-image-h9-B-v5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v5 | — | — | 0.806 [0.787, 0.824] | 0.808 | 0.803 | — |
| 51 | h1-brief-text | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.693 [0.666, 0.720] | 0.674 | 0.712 | — |
| 52 | h9-track1-image-h9-A-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.790 [0.771, 0.811] | 0.788 | 0.792 | — |
| 53 | h7-track2-text-T0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.699 [0.666, 0.727] | 0.586 | 0.865 | — |
| 54 | h7-track2-text-T1.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.689 [0.663, 0.716] | 0.678 | 0.699 | — |
| 55 | h9-track1-image-h9-E-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p4 | — | — | 0.790 [0.767, 0.812] | 0.815 | 0.766 | — |
| 56 | h9-track1-image-h9-C-img1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img1 | — | — | 0.806 [0.786, 0.827] | 0.814 | 0.798 | — |
| 57 | h7-track2-text-T1.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.682 [0.656, 0.713] | 0.686 | 0.677 | — |
| 58 | h9-track1-image-h9-B-v3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v3 | — | — | 0.801 [0.781, 0.823] | 0.801 | 0.801 | — |
| 59 | h7-track1-image-T1.0 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.779 [0.758, 0.798] | 0.726 | 0.840 | — |
| 60 | h9-track2-text-h9-B-v3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.689 [0.661, 0.715] | 0.686 | 0.692 | — |
| 61 | h7-track1-image-T0.3 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.764 [0.742, 0.784] | 0.749 | 0.779 | — |
| 62 | h9-track1-image-h9-B-v4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v4 | — | — | 0.807 [0.785, 0.828] | 0.808 | 0.805 | — |
| 63 | h9-track1-image-h9-E-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p3 | — | — | 0.786 [0.765, 0.806] | 0.788 | 0.785 | — |
| 64 | h1-verbose-text-image | image | 3 | 2 | gemini-3-flash | detect_verbose-text-image | — | — | 0.786 [0.763, 0.805] | 0.741 | 0.837 | — |
| 65 | h1-brief-text-image | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.779 [0.758, 0.796] | 0.727 | 0.839 | — |
| 66 | h7-track1-image-T0.7 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.769 [0.750, 0.791] | 0.696 | 0.859 | — |
| 67 | h7-track1-image-T0.0 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.759 [0.737, 0.779] | 0.669 | 0.878 | — |
| 68 | h9-track2-text-h9-E-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.681 [0.651, 0.707] | 0.671 | 0.692 | — |

## Tier 5 (F1: 0.687–0.778)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 69 | h7-track1-image-T1.3 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.778 [0.759, 0.798] | 0.742 | 0.818 | — |
| 70 | h1-verbose-text | text | 3 | 2 | gemini-3-flash | detect_verbose-text | — | — | 0.687 [0.654, 0.717] | 0.588 | 0.826 | — |
| 71 | h1-image-only | image | 3 | 2 | gemini-3-flash | detect_image-only | — | — | 0.748 [0.725, 0.770] | 0.695 | 0.809 | — |

## Tier 6 (F1: 0.531–0.531)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 72 | h11-bridge-brief-text-t0 | text | 10 | 10 | gemini-3-flash-preview | detect_brief-text | — | — | 0.531 [0.488, 0.564] | 0.424 | 0.709 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
