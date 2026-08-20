# Leaderboard — Era 2, Consensus (no PV), 30 m buffer

**Generated**: 2026-08-20T06:34:06.345496+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 29 in 7 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.826–0.851)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h11-pvd-pro-high-text-n5 | text | 10 | 6 | gemini-3-flash | detect_brief-text | — | — | 0.851 [0.828, 0.876] | 0.944 | 0.775 | — |
| 2 | h11-pvd-flash-high-text-n5 | text | 30 | 26 | gemini-3-flash | detect_brief-text | — | — | 0.826 [0.804, 0.848] | 0.846 | 0.807 | — |

## Tier 2 (F1: 0.789–0.810)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 3 | p3a-high-text-t0.3 | text | 10 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.810 [0.787, 0.832] | 0.836 | 0.786 | — |
| 4 | p3a-high-text-t0.3-n5 | text | 5 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.810 [0.787, 0.832] | 0.836 | 0.786 | — |
| 5 | p3a-high-text-t1.0 | text | 10 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.789 [0.763, 0.814] | 0.809 | 0.770 | — |
| 6 | p3a-high-text-t1.0-n5 | text | 5 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.789 [0.763, 0.814] | 0.809 | 0.770 | — |
| 7 | h11-pvd-flash-high-image-n5 | image | 10 | 7 | gemini-3-flash | library_plus-hp | — | — | 0.809 [0.785, 0.835] | 0.840 | 0.782 | — |

## Tier 3 (F1: 0.730–0.821)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 8 | scale4-optimal-487 | image | 10 | 6 | gemini-3-flash | detect_h8_scale-4_v2 | — | — | 0.804 [0.778, 0.831] | 0.836 | 0.775 | — |
| 9 | p3a-high-image-t1.0 | image | 10 | 6 | gemini-3-flash | library_plus-hp | — | — | 0.788 [0.764, 0.814] | 0.790 | 0.786 | — |
| 10 | p3a-high-image-t0.3 | image | 10 | 9 | gemini-3-flash | library_plus-hp | — | — | 0.784 [0.757, 0.806] | 0.864 | 0.717 | — |
| 11 | h11-e47-propose-brief | text | 5 | 5 | gemini-3-flash-preview | propose_brief-text | — | — | 0.730 [0.695, 0.760] | 0.709 | 0.752 | — |
| 12 | h11-pvd-pro-high-image-n5 | image | 5 | 3 | gemini-3-flash | library_plus-hp | — | — | 0.821 [0.798, 0.843] | 0.790 | 0.855 | — |

## Tier 4 (F1: 0.648–0.737)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 13 | h11-pvd-image-n5 | image | 10 | 8 | gemini-3-flash | library_plus-hp | — | — | 0.728 [0.703, 0.757] | 0.684 | 0.777 | — |
| 14 | h11-n1-image-t03 | image | 3 | 3 | gemini-3-flash-preview | library_plus-hp | — | — | 0.737 [0.710, 0.766] | 0.651 | 0.848 | — |
| 15 | p3a-minimal-text-t1.0 | text | 10 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.673 [0.637, 0.711] | 0.603 | 0.761 | — |
| 16 | p3a-minimal-text-t1.0-n5 | text | 5 | 9 | gemini-3-flash | detect_brief-text | — | — | 0.673 [0.637, 0.711] | 0.603 | 0.761 | — |
| 17 | h11-pvd-flash-minimal-text-n30-t07 | text | 30 | 29 | gemini-3-flash | detect_brief-text | — | — | 0.669 [0.637, 0.703] | 0.609 | 0.743 | — |
| 18 | p3a-min-image-t0.3 | image | 10 | 10 | gemini-3-flash | library_plus-hp | — | — | 0.710 [0.680, 0.738] | 0.654 | 0.777 | — |
| 19 | p3a-min-image-t1.0 | image | 10 | 8 | gemini-3-flash | library_plus-hp | — | — | 0.715 [0.689, 0.742] | 0.691 | 0.740 | — |
| 20 | p3a-minimal-text-t0.3 | text | 10 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.648 [0.613, 0.684] | 0.556 | 0.777 | — |
| 21 | p3a-minimal-text-t0.3-n5 | text | 5 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.648 [0.613, 0.684] | 0.556 | 0.777 | — |

## Tier 5 (F1: 0.598–0.692)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 22 | h11-n1-image-t0 | image | 3 | 2 | gemini-3-flash-preview | library_plus-hp | — | — | 0.692 [0.664, 0.719] | 0.567 | 0.887 | — |
| 23 | h11-pvd-text-n10 | text | 10 | 10 | gemini-3-flash | detect_brief-text | — | — | 0.628 [0.594, 0.671] | 0.536 | 0.759 | — |
| 24 | p3a-high-text-t0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.627 [0.584, 0.663] | 0.497 | 0.851 | — |
| 25 | p3a-minimal-text-t0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.598 [0.553, 0.636] | 0.462 | 0.848 | — |
| 26 | h11-n1-brief-text-t03 | text | 3 | 3 | gemini-3-flash-preview | detect_brief-text | — | — | 0.601 [0.559, 0.642] | 0.465 | 0.848 | — |

## Tier 6 (F1: 0.593–0.618)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 27 | h11-n1-pro-text-high-t0 | text | 3 | 3 | gemini-3-flash-preview | detect_brief-text | — | — | 0.593 [0.553, 0.627] | 0.461 | 0.830 | — |
| 28 | h11-n1-pro-image-high-t0 | image | 3 | 3 | gemini-3-flash-preview | library_plus-hp | — | — | 0.618 [0.582, 0.654] | 0.531 | 0.738 | — |

## Tier 7 (F1: 0.550–0.550)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 29 | p3a-high-image-t0.0 | image | 3 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.550 [0.514, 0.583] | 0.424 | 0.782 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
