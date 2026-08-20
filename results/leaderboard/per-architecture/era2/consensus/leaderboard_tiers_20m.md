# Leaderboard — Era 2, Consensus (no PV), 20 m buffer

**Generated**: 2026-08-20T06:34:06.342568+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 29 in 7 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.814–0.836)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h11-pvd-pro-high-text-n5 | text | 10 | 6 | gemini-3-flash | detect_brief-text | — | — | 0.836 [0.810, 0.859] | 0.927 | 0.761 | — |
| 2 | h11-pvd-flash-high-text-n5 | text | 30 | 26 | gemini-3-flash | detect_brief-text | — | — | 0.814 [0.792, 0.839] | 0.834 | 0.795 | — |

## Tier 2 (F1: 0.750–0.789)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 3 | p3a-high-text-t0.3 | text | 10 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.789 [0.763, 0.811] | 0.814 | 0.765 | — |
| 4 | p3a-high-text-t0.3-n5 | text | 5 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.789 [0.763, 0.811] | 0.814 | 0.765 | — |
| 5 | p3a-high-text-t1.0 | text | 10 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.773 [0.744, 0.800] | 0.792 | 0.754 | — |
| 6 | p3a-high-text-t1.0-n5 | text | 5 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.773 [0.744, 0.800] | 0.792 | 0.754 | — |
| 7 | h11-pvd-flash-high-image-n5 | image | 10 | 7 | gemini-3-flash | library_plus-hp | — | — | 0.750 [0.722, 0.781] | 0.778 | 0.724 | — |

## Tier 3 (F1: 0.700–0.742)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 8 | scale4-optimal-487 | image | 10 | 6 | gemini-3-flash | detect_h8_scale-4_v2 | — | — | 0.742 [0.713, 0.771] | 0.772 | 0.715 | — |
| 9 | p3a-high-image-t1.0 | image | 10 | 6 | gemini-3-flash | library_plus-hp | — | — | 0.735 [0.707, 0.765] | 0.737 | 0.733 | — |
| 10 | p3a-high-image-t0.3 | image | 10 | 9 | gemini-3-flash | library_plus-hp | — | — | 0.731 [0.698, 0.757] | 0.806 | 0.669 | — |
| 11 | h11-e47-propose-brief | text | 5 | 5 | gemini-3-flash-preview | propose_brief-text | — | — | 0.714 [0.678, 0.745] | 0.694 | 0.736 | — |
| 12 | h11-pvd-pro-high-image-n5 | image | 5 | 3 | gemini-3-flash | library_plus-hp | — | — | 0.700 [0.667, 0.732] | 0.673 | 0.729 | — |

## Tier 4 (F1: 0.642–0.680)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 13 | h11-pvd-image-n5 | image | 10 | 8 | gemini-3-flash | library_plus-hp | — | — | 0.680 [0.650, 0.711] | 0.640 | 0.726 | — |
| 14 | h11-n1-image-t03 | image | 3 | 3 | gemini-3-flash-preview | library_plus-hp | — | — | 0.677 [0.648, 0.707] | 0.598 | 0.779 | — |
| 15 | p3a-minimal-text-t1.0 | text | 10 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.667 [0.631, 0.705] | 0.597 | 0.754 | — |
| 16 | p3a-minimal-text-t1.0-n5 | text | 5 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.667 [0.631, 0.705] | 0.597 | 0.754 | — |
| 17 | h11-pvd-flash-minimal-text-n30-t07 | text | 30 | 29 | gemini-3-flash | detect_brief-text | — | — | 0.661 [0.627, 0.694] | 0.602 | 0.733 | — |
| 18 | p3a-min-image-t0.3 | image | 10 | 10 | gemini-3-flash | library_plus-hp | — | — | 0.660 [0.629, 0.690] | 0.607 | 0.722 | — |
| 19 | p3a-min-image-t1.0 | image | 10 | 8 | gemini-3-flash | library_plus-hp | — | — | 0.646 [0.613, 0.676] | 0.625 | 0.669 | — |
| 20 | p3a-minimal-text-t0.3 | text | 10 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.642 [0.606, 0.679] | 0.551 | 0.770 | — |
| 21 | p3a-minimal-text-t0.3-n5 | text | 5 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.642 [0.606, 0.679] | 0.551 | 0.770 | — |

## Tier 5 (F1: 0.591–0.629)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 22 | h11-n1-image-t0 | image | 3 | 2 | gemini-3-flash-preview | library_plus-hp | — | — | 0.629 [0.600, 0.657] | 0.515 | 0.807 | — |
| 23 | h11-pvd-text-n10 | text | 10 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.619 [0.582, 0.659] | 0.528 | 0.747 | — |
| 24 | p3a-high-text-t0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.605 [0.565, 0.642] | 0.479 | 0.821 | — |
| 25 | p3a-minimal-text-t0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.593 [0.547, 0.631] | 0.458 | 0.841 | — |
| 26 | h11-n1-brief-text-t03 | text | 3 | 3 | gemini-3-flash-preview | detect_brief-text | — | — | 0.591 [0.550, 0.634] | 0.457 | 0.835 | — |

## Tier 6 (F1: 0.552–0.567)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 27 | h11-n1-pro-text-high-t0 | text | 3 | 3 | gemini-3-flash-preview | detect_brief-text | — | — | 0.567 [0.530, 0.603] | 0.441 | 0.793 | — |
| 28 | h11-n1-pro-image-high-t0 | image | 3 | 3 | gemini-3-flash-preview | library_plus-hp | — | — | 0.552 [0.517, 0.587] | 0.475 | 0.660 | — |

## Tier 7 (F1: 0.488–0.488)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 29 | p3a-high-image-t0.0 | image | 3 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.488 [0.457, 0.520] | 0.377 | 0.694 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
