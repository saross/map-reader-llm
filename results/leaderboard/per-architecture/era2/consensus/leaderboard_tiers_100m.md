# Leaderboard — Era 2, Consensus (no PV), 100 m buffer

**Generated**: 2026-08-20T06:34:06.354418+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 29 in 7 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.826–0.859)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h11-pvd-pro-high-text-n5 | text | 10 | 6 | gemini-3-flash | detect_brief-text | — | — | 0.859 [0.835, 0.883] | 0.952 | 0.782 | — |
| 2 | h11-pvd-flash-high-text-n5 | text | 30 | 26 | gemini-3-flash | detect_brief-text | — | — | 0.826 [0.804, 0.848] | 0.846 | 0.807 | — |

## Tier 2 (F1: 0.789–0.829)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 3 | p3a-high-text-t0.3 | text | 10 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.810 [0.787, 0.832] | 0.836 | 0.786 | — |
| 4 | p3a-high-text-t0.3-n5 | text | 5 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.810 [0.787, 0.832] | 0.836 | 0.786 | — |
| 5 | p3a-high-text-t1.0 | text | 10 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.789 [0.763, 0.814] | 0.809 | 0.770 | — |
| 6 | p3a-high-text-t1.0-n5 | text | 5 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.789 [0.763, 0.814] | 0.809 | 0.770 | — |
| 7 | h11-pvd-flash-high-image-n5 | image | 10 | 7 | gemini-3-flash | library_plus-hp | — | — | 0.829 [0.808, 0.853] | 0.859 | 0.800 | — |

## Tier 3 (F1: 0.732–0.885)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 8 | scale4-optimal-487 | image | 10 | 6 | gemini-3-flash | detect_h8_scale-4_v2 | — | — | 0.835 [0.815, 0.857] | 0.869 | 0.805 | — |
| 9 | p3a-high-image-t1.0 | image | 10 | 6 | gemini-3-flash | library_plus-hp | — | — | 0.830 [0.807, 0.851] | 0.831 | 0.828 | — |
| 10 | p3a-high-image-t0.3 | image | 10 | 9 | gemini-3-flash | library_plus-hp | — | — | 0.796 [0.772, 0.820] | 0.878 | 0.729 | — |
| 11 | h11-e47-propose-brief | text | 5 | 5 | gemini-3-flash-preview | propose_brief-text | — | — | 0.732 [0.698, 0.762] | 0.712 | 0.754 | — |
| 12 | h11-pvd-pro-high-image-n5 | image | 5 | 3 | gemini-3-flash | library_plus-hp | — | — | 0.885 [0.869, 0.902] | 0.851 | 0.922 | — |

## Tier 4 (F1: 0.654–0.760)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 13 | h11-pvd-image-n5 | image | 10 | 8 | gemini-3-flash | library_plus-hp | — | — | 0.751 [0.728, 0.781] | 0.707 | 0.802 | — |
| 14 | h11-n1-image-t03 | image | 3 | 3 | gemini-3-flash-preview | library_plus-hp | — | — | 0.760 [0.735, 0.786] | 0.672 | 0.876 | — |
| 15 | p3a-minimal-text-t1.0 | text | 10 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.675 [0.640, 0.714] | 0.605 | 0.763 | — |
| 16 | p3a-minimal-text-t1.0-n5 | text | 5 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.675 [0.640, 0.714] | 0.605 | 0.763 | — |
| 17 | h11-pvd-flash-minimal-text-n30-t07 | text | 30 | 29 | gemini-3-flash | detect_brief-text | — | — | 0.669 [0.637, 0.703] | 0.609 | 0.743 | — |
| 18 | p3a-min-image-t0.3 | image | 10 | 10 | gemini-3-flash | library_plus-hp | — | — | 0.723 [0.695, 0.749] | 0.665 | 0.791 | — |
| 19 | p3a-min-image-t1.0 | image | 10 | 8 | gemini-3-flash | library_plus-hp | — | — | 0.739 [0.717, 0.766] | 0.715 | 0.765 | — |
| 20 | p3a-minimal-text-t0.3 | text | 10 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.654 [0.618, 0.689] | 0.561 | 0.784 | — |
| 21 | p3a-minimal-text-t0.3-n5 | text | 5 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.654 [0.618, 0.689] | 0.561 | 0.784 | — |

## Tier 5 (F1: 0.605–0.728)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 22 | h11-n1-image-t0 | image | 3 | 2 | gemini-3-flash-preview | library_plus-hp | — | — | 0.728 [0.698, 0.754] | 0.596 | 0.933 | — |
| 23 | h11-pvd-text-n10 | text | 10 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.628 [0.594, 0.671] | 0.536 | 0.759 | — |
| 24 | p3a-high-text-t0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.636 [0.594, 0.674] | 0.503 | 0.862 | — |
| 25 | p3a-minimal-text-t0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.616 [0.576, 0.655] | 0.476 | 0.874 | — |
| 26 | h11-n1-brief-text-t03 | text | 3 | 3 | gemini-3-flash-preview | detect_brief-text | — | — | 0.605 [0.564, 0.646] | 0.469 | 0.855 | — |

## Tier 6 (F1: 0.608–0.670)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 27 | h11-n1-pro-text-high-t0 | text | 3 | 3 | gemini-3-flash-preview | detect_brief-text | — | — | 0.608 [0.566, 0.643] | 0.472 | 0.851 | — |
| 28 | h11-n1-pro-image-high-t0 | image | 3 | 3 | gemini-3-flash-preview | library_plus-hp | — | — | 0.670 [0.634, 0.701] | 0.576 | 0.800 | — |

## Tier 7 (F1: 0.602–0.602)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 29 | p3a-high-image-t0.0 | image | 3 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.602 [0.567, 0.637] | 0.464 | 0.855 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
