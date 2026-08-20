# Leaderboard — Era 2, Consensus + PV, 100 m buffer

**Generated**: 2026-08-20T06:34:06.382434+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 44 in 6 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.899–0.916)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | pv-flash-high-text-16of30 | text | 30 | 16 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.909 [0.893, 0.927] | 0.934 | 0.885 | — |
| 2 | pv-high-text-t0.3-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.912 [0.897, 0.928] | 0.941 | 0.885 | — |
| 3 | session-78-text-comparative | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-comparative | 0.25 | 0.916 [0.898, 0.932] | 0.960 | 0.876 | — |
| 4 | session-78-text-adversarial | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-adversarial | 0.20 | 0.915 [0.898, 0.931] | 0.960 | 0.874 | — |
| 5 | pv-high-text-t1.0-n10 | text | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.908 [0.894, 0.924] | 0.918 | 0.899 | — |
| 6 | session-78-text-checklist | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-checklist | 0.15 | 0.909 [0.891, 0.925] | 0.945 | 0.876 | — |
| 7 | pv-min-text-t0.3-n5 | text | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.906 [0.891, 0.924] | 0.936 | 0.878 | — |
| 8 | pv-min-text-t1.0-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.899 [0.883, 0.916] | 0.944 | 0.858 | — |

## Tier 2 (F1: 0.880–0.908)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 9 | session-78-text-brief | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-brief | 0.15 | 0.907 [0.888, 0.923] | 0.941 | 0.876 | — |
| 10 | pv-high-text-t0.7-n10 | text | 10 | 8 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.892 [0.874, 0.910] | 0.960 | 0.832 | — |
| 11 | pv-min-text-t0.7-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.893 [0.877, 0.907] | 0.951 | 0.841 | — |
| 12 | pv-min-text-t0.7-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.894 [0.876, 0.909] | 0.937 | 0.855 | — |
| 13 | pv-high-text-t0.3-n10 | text | 10 | 8 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.908 [0.893, 0.925] | 0.945 | 0.874 | — |
| 14 | pv-min-text-t1.0-n5 | text | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.902 [0.886, 0.919] | 0.936 | 0.871 | — |
| 15 | pv-min-text-t0.3-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.895 [0.878, 0.910] | 0.944 | 0.851 | — |
| 16 | session-78-text-checklist-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-checklist-text | 0.15 | 0.895 [0.875, 0.912] | 0.922 | 0.869 | — |
| 17 | pv-high-text-t0.7-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.892 [0.872, 0.911] | 0.941 | 0.848 | — |
| 18 | pv-min-text-t0.0-n3 | text | 3 | 2 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.896 [0.881, 0.913] | 0.944 | 0.853 | — |
| 19 | pv-high-text-t1.0-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.880 [0.861, 0.899] | 0.950 | 0.821 | — |

## Tier 3 (F1: 0.864–0.892)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 20 | session-78-text-adversarial-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-adversarial-text | 0.15 | 0.892 [0.872, 0.910] | 0.946 | 0.844 | — |
| 21 | session-78-text-brief-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-brief-text | 0.15 | 0.883 [0.863, 0.902] | 0.936 | 0.837 | — |
| 22 | pv-high-text-t0.0-n3 | text | 3 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.864 [0.838, 0.887] | 0.898 | 0.832 | — |

## Tier 4 (F1: 0.850–0.897)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 23 | pv-min-image-t0.7-n10 | image | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.883 [0.864, 0.900] | 0.916 | 0.853 | — |
| 24 | pv-high-image-t0.7-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.886 [0.868, 0.904] | 0.908 | 0.864 | — |
| 25 | session-78-image-adversarial | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-adversarial | 0.15 | 0.897 [0.880, 0.911] | 0.900 | 0.894 | — |
| 26 | session-78-image-comparative | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-comparative | 0.25 | 0.896 [0.880, 0.912] | 0.898 | 0.894 | — |
| 27 | session-78-image-checklist-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-checklist-text | 0.15 | 0.894 [0.876, 0.908] | 0.898 | 0.890 | — |
| 28 | session-78-image-brief | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-brief | 0.15 | 0.894 [0.877, 0.911] | 0.892 | 0.897 | — |
| 29 | session-78-image-checklist | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-checklist | 0.15 | 0.893 [0.877, 0.908] | 0.892 | 0.894 | — |
| 30 | pv-min-image-t0.3-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.870 [0.850, 0.888] | 0.903 | 0.839 | — |
| 31 | session-78-image-brief-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-brief-text | 0.15 | 0.873 [0.854, 0.894] | 0.902 | 0.846 | — |
| 32 | pv-min-image-t0.3-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.869 [0.847, 0.890] | 0.899 | 0.841 | — |
| 33 | pv-high-image-t0.7-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.850 [0.829, 0.869] | 0.952 | 0.768 | — |
| 34 | pv-min-image-t0.7-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.888 [0.869, 0.904] | 0.903 | 0.874 | — |

## Tier 5 (F1: 0.859–0.886)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 35 | session-78-image-adversarial-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-adversarial-text | 0.15 | 0.868 [0.850, 0.886] | 0.889 | 0.848 | — |
| 36 | pv-high-image-t0.3-n10 | image | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.886 [0.868, 0.904] | 0.925 | 0.851 | — |
| 37 | pv-scale4-optimal-n10 | image | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.865 [0.846, 0.884] | 0.890 | 0.841 | — |
| 38 | pv-n1-image-t0-n3 | image | 3 | 2 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.881 [0.864, 0.896] | 0.870 | 0.892 | — |
| 39 | pv-high-image-t1.0-n10 | image | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.876 [0.861, 0.894] | 0.899 | 0.855 | — |
| 40 | pv-scale4-optimal-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.859 [0.837, 0.879] | 0.901 | 0.821 | — |

## Tier 6 (F1: 0.846–0.876)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 41 | pv-high-image-t0.3-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.858 [0.836, 0.880] | 0.930 | 0.795 | — |
| 42 | pv-min-image-t1.0-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.846 [0.826, 0.867] | 0.929 | 0.777 | — |
| 43 | pv-min-image-t1.0-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.849 [0.829, 0.871] | 0.931 | 0.779 | — |
| 44 | pv-high-image-t1.0-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.876 [0.856, 0.893] | 0.902 | 0.851 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
