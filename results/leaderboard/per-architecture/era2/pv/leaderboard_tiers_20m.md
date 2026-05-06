# Leaderboard — Era 2, Consensus + PV, 20 m buffer

**Generated**: 2026-05-06T00:25:57.083835+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 44 in 6 tier(s). Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.877–0.890)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | pv-flash-high-text-16of30 | text | 30 | 16 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.890 [0.874, 0.910] | 0.915 | 0.867 | 0.789 |
| 2 | pv-high-text-t0.3-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.886 [0.868, 0.905] | 0.914 | 0.860 | 0.776 |
| 3 | session-78-text-comparative | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-comparative | 0.25 | 0.885 [0.863, 0.904] | 0.927 | 0.846 | 0.794 |
| 4 | session-78-text-adversarial | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-adversarial | 0.20 | 0.883 [0.862, 0.901] | 0.927 | 0.844 | 0.793 |
| 5 | pv-high-text-t1.0-n10 | text | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.880 [0.862, 0.901] | 0.890 | 0.871 | 0.790 |
| 6 | session-78-text-checklist | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-checklist | 0.15 | 0.878 [0.856, 0.896] | 0.913 | 0.846 | 0.774 |
| 7 | pv-min-text-t0.3-n5 | text | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.878 [0.860, 0.897] | 0.907 | 0.851 | 0.772 |
| 8 | pv-min-text-t1.0-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.877 [0.860, 0.895] | 0.921 | 0.837 | 0.780 |

## Tier 2 (F1: 0.861–0.876)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 9 | session-78-text-brief | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-brief | 0.15 | 0.876 [0.854, 0.894] | 0.909 | 0.846 | 0.765 |
| 10 | pv-high-text-t0.7-n10 | text | 10 | 8 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.874 [0.857, 0.894] | 0.942 | 0.816 | 0.763 |
| 11 | pv-min-text-t0.7-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.873 [0.854, 0.891] | 0.930 | 0.823 | 0.786 |
| 12 | pv-min-text-t0.7-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.873 [0.853, 0.893] | 0.914 | 0.835 | 0.776 |
| 13 | pv-high-text-t0.3-n10 | text | 10 | 8 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.872 [0.853, 0.892] | 0.908 | 0.839 | 0.787 |
| 14 | pv-min-text-t1.0-n5 | text | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.871 [0.852, 0.890] | 0.904 | 0.841 | 0.779 |
| 15 | pv-min-text-t0.3-n10 | text | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.868 [0.850, 0.886] | 0.916 | 0.825 | 0.772 |
| 16 | session-78-text-checklist-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-checklist-text | 0.15 | 0.864 [0.842, 0.883] | 0.890 | 0.839 | 0.755 |
| 17 | pv-high-text-t0.7-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.863 [0.842, 0.883] | 0.911 | 0.821 | 0.768 |
| 18 | pv-min-text-t0.0-n3 | text | 3 | 2 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.862 [0.842, 0.884] | 0.908 | 0.821 | 0.783 |
| 19 | pv-high-text-t1.0-n5 | text | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.861 [0.841, 0.881] | 0.928 | 0.802 | 0.756 |

## Tier 3 (F1: 0.823–0.860)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 20 | session-78-text-adversarial-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-adversarial-text | 0.15 | 0.860 [0.839, 0.880] | 0.912 | 0.814 | 0.753 |
| 21 | session-78-text-brief-text | text | 5 | 4 | gemini-3-flash | library_plus-hp | session-78-brief-text | 0.15 | 0.852 [0.827, 0.873] | 0.902 | 0.807 | 0.758 |
| 22 | pv-high-text-t0.0-n3 | text | 3 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.823 [0.797, 0.850] | 0.856 | 0.793 | 0.774 |

## Tier 4 (F1: 0.773–0.788)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 23 | pv-min-image-t0.7-n10 | image | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.788 [0.761, 0.811] | 0.817 | 0.761 | 0.821 |
| 24 | pv-high-image-t0.7-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.787 [0.761, 0.814] | 0.807 | 0.768 | 0.836 |
| 25 | session-78-image-adversarial | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-adversarial | 0.15 | 0.787 [0.760, 0.814] | 0.789 | 0.784 | 0.830 |
| 26 | session-78-image-comparative | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-comparative | 0.25 | 0.786 [0.760, 0.813] | 0.787 | 0.784 | 0.830 |
| 27 | session-78-image-checklist-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-checklist-text | 0.15 | 0.785 [0.758, 0.814] | 0.789 | 0.782 | 0.821 |
| 28 | session-78-image-brief | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-brief | 0.15 | 0.784 [0.758, 0.812] | 0.783 | 0.786 | 0.829 |
| 29 | session-78-image-checklist | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-checklist | 0.15 | 0.783 [0.757, 0.812] | 0.782 | 0.784 | 0.816 |
| 30 | pv-min-image-t0.3-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.782 [0.752, 0.805] | 0.812 | 0.754 | 0.837 |
| 31 | session-78-image-brief-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-brief-text | 0.15 | 0.778 [0.753, 0.807] | 0.804 | 0.754 | 0.819 |
| 32 | pv-min-image-t0.3-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.777 [0.750, 0.803] | 0.803 | 0.752 | 0.841 |
| 33 | pv-high-image-t0.7-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.776 [0.748, 0.805] | 0.869 | 0.701 | 0.796 |
| 34 | pv-min-image-t0.7-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.773 [0.747, 0.797] | 0.786 | 0.761 | 0.838 |

## Tier 5 (F1: 0.763–0.772)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 35 | session-78-image-adversarial-text | image | 5 | 3 | gemini-3-flash | library_plus-hp | session-78-adversarial-text | 0.15 | 0.772 [0.748, 0.801] | 0.790 | 0.754 | 0.797 |
| 36 | pv-high-image-t0.3-n10 | image | 10 | 6 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.769 [0.744, 0.796] | 0.802 | 0.738 | 0.815 |
| 37 | pv-scale4-optimal-n10 | image | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.768 [0.744, 0.795] | 0.791 | 0.747 | 0.815 |
| 38 | pv-n1-image-t0-n3 | image | 3 | 2 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.767 [0.743, 0.793] | 0.758 | 0.777 | 0.839 |
| 39 | pv-high-image-t1.0-n10 | image | 10 | 5 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.763 [0.736, 0.789] | 0.783 | 0.745 | 0.800 |
| 40 | pv-scale4-optimal-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.763 [0.733, 0.791] | 0.800 | 0.729 | 0.835 |

## Tier 6 (F1: 0.734–0.746)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 41 | pv-high-image-t0.3-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.746 [0.716, 0.773] | 0.809 | 0.692 | 0.804 |
| 42 | pv-min-image-t1.0-n10 | image | 10 | 7 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.20 | 0.741 [0.713, 0.773] | 0.813 | 0.680 | 0.810 |
| 43 | pv-min-image-t1.0-n5 | image | 5 | 4 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.738 [0.712, 0.770] | 0.810 | 0.678 | 0.802 |
| 44 | pv-high-image-t1.0-n5 | image | 5 | 3 | gemini-3-flash | — | v1 (adversarial-text canonical) | 0.15 | 0.734 [0.698, 0.761] | 0.756 | 0.713 | 0.822 |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
