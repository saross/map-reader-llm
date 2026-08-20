# Leaderboard — Era 2, Single-pass (raw), 40 m buffer

**Generated**: 2026-08-20T06:34:06.338136+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/single-pass/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 6 in 4 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.795–0.795)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h11-pvd-pro-medium-text-baseline | text | 1 | 1 | gemini-3-flash | detect_brief-text | — | — | 0.795 [0.764, 0.823] | 0.800 | 0.791 | — |

## Tier 2 (F1: 0.674–0.763)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 2 | h11-pvd-pro-medium-image-baseline | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.763 [0.737, 0.789] | 0.701 | 0.837 | — |
| 3 | h11-pvd-image-baseline | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.674 [0.651, 0.703] | 0.533 | 0.915 | — |

## Tier 3 (F1: 0.536–0.536)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 4 | h11-pvd-text-baseline | text | 1 | 1 | gemini-3-flash | detect_brief-text | — | — | 0.536 [0.490, 0.571] | 0.379 | 0.913 | — |

## Tier 4 (F1: 0.430–0.567)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 5 | h11-n1-pro-image-medium-t07 | image | 1 | 1 | gemini-3-flash-preview | library_plus-hp | — | — | 0.567 [0.533, 0.602] | 0.414 | 0.897 | — |
| 6 | h11-n1-pro-text-medium-t07 | text | 1 | 1 | gemini-3-flash-preview | detect_brief-text | — | — | 0.430 [0.397, 0.472] | 0.280 | 0.929 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
