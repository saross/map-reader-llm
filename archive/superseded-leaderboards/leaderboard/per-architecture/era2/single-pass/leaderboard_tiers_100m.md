# Leaderboard — Era 2, Single-pass (raw), 100 m buffer

**Generated**: 2026-08-20T06:34:06.339600+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/single-pass/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 6 in 4 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.807–0.807)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h11-pvd-pro-medium-text-baseline | text | 1 | 1 | gemini-3-flash | detect_brief-text | — | — | 0.807 [0.773, 0.834] | 0.812 | 0.802 | — |

## Tier 2 (F1: 0.689–0.794)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 2 | h11-pvd-pro-medium-image-baseline | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.794 [0.771, 0.817] | 0.730 | 0.871 | — |
| 3 | h11-pvd-image-baseline | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.689 [0.665, 0.720] | 0.546 | 0.936 | — |

## Tier 3 (F1: 0.538–0.538)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 4 | h11-pvd-text-baseline | text | 1 | 1 | gemini-3-flash | detect_brief-text | — | — | 0.538 [0.492, 0.572] | 0.381 | 0.917 | — |

## Tier 4 (F1: 0.432–0.593)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 5 | h11-n1-pro-image-medium-t07 | image | 1 | 1 | gemini-3-flash-preview | library_plus-hp | — | — | 0.593 [0.560, 0.630] | 0.434 | 0.938 | — |
| 6 | h11-n1-pro-text-medium-t07 | text | 1 | 1 | gemini-3-flash-preview | detect_brief-text | — | — | 0.432 [0.398, 0.474] | 0.281 | 0.933 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
