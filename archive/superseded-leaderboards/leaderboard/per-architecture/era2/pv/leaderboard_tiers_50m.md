# Leaderboard — Era 2, Consensus + PV, 50 m buffer

**Generated**: 2026-08-20T06:34:06.377702+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 44 in 6 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.896–0.911)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | pv-flash-high-text-16of30 | text | 30 | 16 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.904 [0.887, 0.922] | 0.930 | 0.880 | — |
| 2 | pv-high-text-t0.3-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.908 [0.892, 0.924] | 0.936 | 0.880 | — |
| 3 | session-78-text-comparative | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-comparative | 0.25 | 0.911 [0.894, 0.928] | 0.955 | 0.871 | — |
| 4 | session-78-text-adversarial | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-adversarial | 0.20 | 0.910 [0.893, 0.927] | 0.955 | 0.869 | — |
| 5 | pv-high-text-t1.0-n10 | text | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.906 [0.891, 0.922] | 0.915 | 0.897 | — |
| 6 | session-78-text-checklist | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-checklist | 0.15 | 0.904 [0.886, 0.922] | 0.940 | 0.871 | — |
| 7 | pv-min-text-t0.3-n5 | text | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.899 [0.884, 0.917] | 0.929 | 0.871 | — |
| 8 | pv-min-text-t1.0-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.896 [0.880, 0.913] | 0.942 | 0.855 | — |

## Tier 2 (F1: 0.880–0.903)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 9 | session-78-text-brief | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-brief | 0.15 | 0.902 [0.883, 0.920] | 0.936 | 0.871 | — |
| 10 | pv-high-text-t0.7-n10 | text | 10 | 8 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.889 [0.871, 0.907] | 0.958 | 0.830 | — |
| 11 | pv-min-text-t0.7-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.890 [0.873, 0.906] | 0.948 | 0.839 | — |
| 12 | pv-min-text-t0.7-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.889 [0.871, 0.908] | 0.932 | 0.851 | — |
| 13 | pv-high-text-t0.3-n10 | text | 10 | 8 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.903 [0.887, 0.919] | 0.940 | 0.869 | — |
| 14 | pv-min-text-t1.0-n5 | text | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.898 [0.882, 0.914] | 0.931 | 0.867 | — |
| 15 | pv-min-text-t0.3-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.890 [0.873, 0.907] | 0.939 | 0.846 | — |
| 16 | session-78-text-checklist-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-checklist-text | 0.15 | 0.890 [0.871, 0.909] | 0.917 | 0.864 | — |
| 17 | pv-high-text-t0.7-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.887 [0.868, 0.906] | 0.936 | 0.844 | — |
| 18 | pv-min-text-t0.0-n3 | text | 3 | 2 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.891 [0.875, 0.908] | 0.939 | 0.848 | — |
| 19 | pv-high-text-t1.0-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.880 [0.861, 0.899] | 0.950 | 0.821 | — |

## Tier 3 (F1: 0.857–0.887)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 20 | session-78-text-adversarial-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-adversarial-text | 0.15 | 0.887 [0.869, 0.907] | 0.941 | 0.839 | — |
| 21 | session-78-text-brief-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-brief-text | 0.15 | 0.879 [0.858, 0.899] | 0.931 | 0.832 | — |
| 22 | pv-high-text-t0.0-n3 | text | 3 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.857 [0.832, 0.881] | 0.891 | 0.825 | — |

## Tier 4 (F1: 0.845–0.895)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 23 | pv-min-image-t0.7-n10 | image | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.876 [0.856, 0.892] | 0.909 | 0.846 | — |
| 24 | pv-high-image-t0.7-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.881 [0.863, 0.899] | 0.903 | 0.860 | — |
| 25 | session-78-image-adversarial | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-adversarial | 0.15 | 0.895 [0.877, 0.909] | 0.898 | 0.892 | — |
| 26 | session-78-image-comparative | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-comparative | 0.25 | 0.894 [0.877, 0.910] | 0.896 | 0.892 | — |
| 27 | session-78-image-checklist-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-checklist-text | 0.15 | 0.894 [0.876, 0.908] | 0.898 | 0.890 | — |
| 28 | session-78-image-brief | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-brief | 0.15 | 0.892 [0.875, 0.908] | 0.890 | 0.894 | — |
| 29 | session-78-image-checklist | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-checklist | 0.15 | 0.891 [0.874, 0.906] | 0.890 | 0.892 | — |
| 30 | pv-min-image-t0.3-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.868 [0.847, 0.886] | 0.901 | 0.837 | — |
| 31 | session-78-image-brief-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-brief-text | 0.15 | 0.873 [0.854, 0.894] | 0.902 | 0.846 | — |
| 32 | pv-min-image-t0.3-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.862 [0.841, 0.883] | 0.892 | 0.835 | — |
| 33 | pv-high-image-t0.7-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.845 [0.823, 0.865] | 0.946 | 0.763 | — |
| 34 | pv-min-image-t0.7-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.881 [0.860, 0.896] | 0.895 | 0.867 | — |

## Tier 5 (F1: 0.852–0.874)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 35 | session-78-image-adversarial-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-adversarial-text | 0.15 | 0.868 [0.850, 0.886] | 0.889 | 0.848 | — |
| 36 | pv-high-image-t0.3-n10 | image | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.874 [0.855, 0.894] | 0.912 | 0.839 | — |
| 37 | pv-scale4-optimal-n10 | image | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.858 [0.839, 0.878] | 0.883 | 0.835 | — |
| 38 | pv-n1-image-t0-n3 | image | 3 | 2 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.872 [0.852, 0.889] | 0.861 | 0.883 | — |
| 39 | pv-high-image-t1.0-n10 | image | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.858 [0.839, 0.876] | 0.879 | 0.837 | — |
| 40 | pv-scale4-optimal-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.852 [0.828, 0.873] | 0.894 | 0.814 | — |

## Tier 6 (F1: 0.839–0.862)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 41 | pv-high-image-t0.3-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.848 [0.825, 0.872] | 0.919 | 0.786 | — |
| 42 | pv-min-image-t1.0-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.841 [0.821, 0.863] | 0.923 | 0.772 | — |
| 43 | pv-min-image-t1.0-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.839 [0.818, 0.862] | 0.920 | 0.770 | — |
| 44 | pv-high-image-t1.0-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.862 [0.839, 0.880] | 0.888 | 0.837 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
