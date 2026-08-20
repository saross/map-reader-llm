# Leaderboard — Era 2, Consensus + PV, 30 m buffer

**Generated**: 2026-08-20T06:34:06.368253+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 44 in 6 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.890–0.911)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | pv-flash-high-text-16of30 | text | 30 | 16 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.904 [0.887, 0.922] | 0.930 | 0.880 | — |
| 2 | pv-high-text-t0.3-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.903 [0.885, 0.919] | 0.931 | 0.876 | — |
| 3 | session-78-text-comparative | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-comparative | 0.25 | 0.911 [0.894, 0.928] | 0.955 | 0.871 | — |
| 4 | session-78-text-adversarial | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-adversarial | 0.20 | 0.910 [0.893, 0.927] | 0.955 | 0.869 | — |
| 5 | pv-high-text-t1.0-n10 | text | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.904 [0.888, 0.921] | 0.913 | 0.894 | — |
| 6 | session-78-text-checklist | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-checklist | 0.15 | 0.904 [0.886, 0.922] | 0.940 | 0.871 | — |
| 7 | pv-min-text-t0.3-n5 | text | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.890 [0.872, 0.908] | 0.919 | 0.862 | — |
| 8 | pv-min-text-t1.0-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.892 [0.874, 0.909] | 0.937 | 0.851 | — |

## Tier 2 (F1: 0.870–0.902)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 9 | session-78-text-brief | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-brief | 0.15 | 0.902 [0.883, 0.920] | 0.936 | 0.871 | — |
| 10 | pv-high-text-t0.7-n10 | text | 10 | 8 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.889 [0.871, 0.907] | 0.958 | 0.830 | — |
| 11 | pv-min-text-t0.7-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.885 [0.867, 0.902] | 0.943 | 0.835 | — |
| 12 | pv-min-text-t0.7-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.887 [0.869, 0.905] | 0.929 | 0.848 | — |
| 13 | pv-high-text-t0.3-n10 | text | 10 | 8 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.901 [0.884, 0.918] | 0.938 | 0.867 | — |
| 14 | pv-min-text-t1.0-n5 | text | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.888 [0.871, 0.906] | 0.921 | 0.858 | — |
| 15 | pv-min-text-t0.3-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.873 [0.854, 0.891] | 0.921 | 0.830 | — |
| 16 | session-78-text-checklist-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-checklist-text | 0.15 | 0.890 [0.871, 0.909] | 0.917 | 0.864 | — |
| 17 | pv-high-text-t0.7-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.887 [0.868, 0.906] | 0.936 | 0.844 | — |
| 18 | pv-min-text-t0.0-n3 | text | 3 | 2 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.870 [0.851, 0.889] | 0.916 | 0.828 | — |
| 19 | pv-high-text-t1.0-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.880 [0.861, 0.899] | 0.950 | 0.821 | — |

## Tier 3 (F1: 0.854–0.887)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 20 | session-78-text-adversarial-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-adversarial-text | 0.15 | 0.887 [0.869, 0.907] | 0.941 | 0.839 | — |
| 21 | session-78-text-brief-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-brief-text | 0.15 | 0.879 [0.858, 0.899] | 0.931 | 0.832 | — |
| 22 | pv-high-text-t0.0-n3 | text | 3 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.854 [0.830, 0.878] | 0.888 | 0.823 | — |

## Tier 4 (F1: 0.832–0.865)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 23 | pv-min-image-t0.7-n10 | image | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.852 [0.827, 0.871] | 0.884 | 0.823 | — |
| 24 | pv-high-image-t0.7-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.858 [0.836, 0.879] | 0.879 | 0.837 | — |
| 25 | session-78-image-adversarial | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-adversarial | 0.15 | 0.865 [0.843, 0.884] | 0.868 | 0.862 | — |
| 26 | session-78-image-comparative | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-comparative | 0.25 | 0.864 [0.841, 0.884] | 0.866 | 0.862 | — |
| 27 | session-78-image-checklist-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-checklist-text | 0.15 | 0.864 [0.841, 0.884] | 0.868 | 0.860 | — |
| 28 | session-78-image-brief | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-brief | 0.15 | 0.862 [0.840, 0.881] | 0.860 | 0.864 | — |
| 29 | session-78-image-checklist | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-checklist | 0.15 | 0.861 [0.840, 0.882] | 0.860 | 0.862 | — |
| 30 | pv-min-image-t0.3-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.853 [0.830, 0.872] | 0.886 | 0.823 | — |
| 31 | session-78-image-brief-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-brief-text | 0.15 | 0.849 [0.829, 0.872] | 0.877 | 0.823 | — |
| 32 | pv-min-image-t0.3-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.843 [0.817, 0.864] | 0.872 | 0.816 | — |
| 33 | pv-high-image-t0.7-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.832 [0.809, 0.853] | 0.932 | 0.752 | — |
| 34 | pv-min-image-t0.7-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.846 [0.821, 0.864] | 0.860 | 0.832 | — |

## Tier 5 (F1: 0.821–0.845)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 35 | session-78-image-adversarial-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-adversarial-text | 0.15 | 0.845 [0.824, 0.868] | 0.865 | 0.825 | — |
| 36 | pv-high-image-t0.3-n10 | image | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.836 [0.813, 0.856] | 0.873 | 0.802 | — |
| 37 | pv-scale4-optimal-n10 | image | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.832 [0.811, 0.856] | 0.856 | 0.809 | — |
| 38 | pv-n1-image-t0-n3 | image | 3 | 2 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.842 [0.822, 0.865] | 0.832 | 0.853 | — |
| 39 | pv-high-image-t1.0-n10 | image | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.834 [0.814, 0.853] | 0.855 | 0.814 | — |
| 40 | pv-scale4-optimal-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.821 [0.791, 0.846] | 0.861 | 0.784 | — |

## Tier 6 (F1: 0.806–0.825)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 41 | pv-high-image-t0.3-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.825 [0.801, 0.849] | 0.895 | 0.765 | — |
| 42 | pv-min-image-t1.0-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.819 [0.795, 0.843] | 0.898 | 0.752 | — |
| 43 | pv-min-image-t1.0-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.806 [0.780, 0.832] | 0.885 | 0.740 | — |
| 44 | pv-high-image-t1.0-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.812 [0.787, 0.836] | 0.837 | 0.788 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
