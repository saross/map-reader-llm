# Leaderboard — Era 2, Single-pass + PV, 30 m buffer

**Generated**: 2026-08-20T06:34:06.356775+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/single-pass+PV/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 8 in 1 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.477–0.541)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | pv-checklist-image | image | 1 | 1 | gemini-3-flash | verified-checklist-image | checklist-image | — | 0.541 [0.482, 0.590] | 0.632 | 0.474 | — |
| 2 | pv-checklist-text | text | 1 | 1 | gemini-3-flash | verified-checklist-text | checklist-text | — | 0.532 [0.475, 0.580] | 0.610 | 0.471 | — |
| 3 | pv-brief-image | image | 1 | 1 | gemini-3-flash | verified-brief-image | brief-image | — | 0.531 [0.473, 0.578] | 0.620 | 0.464 | — |
| 4 | pv-brief-text | text | 1 | 1 | gemini-3-flash | verified-brief-text | brief-text | — | 0.523 [0.465, 0.573] | 0.684 | 0.423 | — |
| 5 | pv-cascade-adversarial-checklist | text | 1 | 1 | gemini-3-flash | verified-cascade-adversarial-checklist | cascade-adversarial-checklist | — | 0.515 [0.460, 0.563] | 0.682 | 0.414 | — |
| 6 | pv-cascade-checklist-adversarial | text | 1 | 1 | gemini-3-flash | verified-cascade-checklist-adversarial | cascade-checklist-adversarial | — | 0.506 [0.451, 0.557] | 0.677 | 0.405 | — |
| 7 | pv-adversarial-image | image | 1 | 1 | gemini-3-flash | verified-adversarial-image | adversarial-image | — | 0.506 [0.450, 0.556] | 0.674 | 0.405 | — |
| 8 | pv-adversarial-text | text | 1 | 1 | gemini-3-flash | verified-adversarial-text | adversarial-text | — | 0.477 [0.417, 0.524] | 0.721 | 0.356 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
