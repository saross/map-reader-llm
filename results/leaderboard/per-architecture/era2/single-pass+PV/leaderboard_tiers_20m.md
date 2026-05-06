# Leaderboard — Era 2, Single-pass + PV, 20 m buffer

**Generated**: 2026-05-06T00:25:57.078306+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/single-pass+PV/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 8 in 1 tier(s). Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.471–0.531)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | pv-checklist-image | image | 1 | 1 | gemini-3-flash | verified-checklist-image | checklist-image | — | 0.531 [0.473, 0.580] | 0.620 | 0.464 | 0.031 |
| 2 | pv-checklist-text | text | 1 | 1 | gemini-3-flash | verified-checklist-text | checklist-text | — | 0.521 [0.463, 0.569] | 0.598 | 0.462 | 0.031 |
| 3 | pv-brief-image | image | 1 | 1 | gemini-3-flash | verified-brief-image | brief-image | — | 0.520 [0.463, 0.569] | 0.607 | 0.455 | 0.031 |
| 4 | pv-brief-text | text | 1 | 1 | gemini-3-flash | verified-brief-text | brief-text | — | 0.514 [0.456, 0.560] | 0.673 | 0.416 | 0.031 |
| 5 | pv-cascade-adversarial-checklist | text | 1 | 1 | gemini-3-flash | verified-cascade-adversarial-checklist | cascade-adversarial-checklist | — | 0.504 [0.446, 0.549] | 0.667 | 0.405 | 0.419 |
| 6 | pv-cascade-checklist-adversarial | text | 1 | 1 | gemini-3-flash | verified-cascade-checklist-adversarial | cascade-checklist-adversarial | — | 0.495 [0.435, 0.540] | 0.661 | 0.395 | 0.388 |
| 7 | pv-adversarial-image | image | 1 | 1 | gemini-3-flash | verified-adversarial-image | adversarial-image | — | 0.494 [0.434, 0.539] | 0.659 | 0.395 | 0.031 |
| 8 | pv-adversarial-text | text | 1 | 1 | gemini-3-flash | verified-adversarial-text | adversarial-text | — | 0.471 [0.408, 0.517] | 0.712 | 0.352 | 0.031 |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
