# Leaderboard — Era 2, Single-pass (raw), 20 m buffer

**Generated**: 2026-08-20T06:34:06.336562+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/single-pass/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 6 in 4 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.763–0.763)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h11-pvd-pro-medium-text-baseline | text | 1 | 1 | gemini-3-flash | detect_brief-text | — | — | 0.763 [0.732, 0.797] | 0.767 | 0.759 | — |

## Tier 2 (F1: 0.600–0.606)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 2 | h11-pvd-pro-medium-image-baseline | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.606 [0.575, 0.636] | 0.557 | 0.664 | — |
| 3 | h11-pvd-image-baseline | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.600 [0.575, 0.629] | 0.474 | 0.814 | — |

## Tier 3 (F1: 0.520–0.520)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 4 | h11-pvd-text-baseline | text | 1 | 1 | gemini-3-flash | detect_brief-text | — | — | 0.520 [0.475, 0.555] | 0.368 | 0.885 | — |

## Tier 4 (F1: 0.416–0.452)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 5 | h11-n1-pro-image-medium-t07 | image | 1 | 1 | gemini-3-flash-preview | library_plus-hp | — | — | 0.452 [0.418, 0.485] | 0.331 | 0.715 | — |
| 6 | h11-n1-pro-text-medium-t07 | text | 1 | 1 | gemini-3-flash-preview | detect_brief-text | — | — | 0.416 [0.385, 0.459] | 0.271 | 0.899 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
