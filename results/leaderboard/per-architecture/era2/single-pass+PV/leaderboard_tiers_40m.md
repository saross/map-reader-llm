# Leaderboard — Era 2, Single-pass + PV, 40 m buffer

**Generated**: 2026-05-06T00:25:57.079557+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/single-pass+PV/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 8 in 1 tier(s). Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.480–0.544)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | pv-checklist-image | image | 1 | 1 | gemini-3-flash | verified-checklist-image | checklist-image | — | 0.544 [0.486, 0.591] | 0.635 | 0.476 | — |
| 2 | pv-checklist-text | text | 1 | 1 | gemini-3-flash | verified-checklist-text | checklist-text | — | 0.534 [0.478, 0.583] | 0.613 | 0.474 | — |
| 3 | pv-brief-image | image | 1 | 1 | gemini-3-flash | verified-brief-image | brief-image | — | 0.533 [0.476, 0.582] | 0.623 | 0.467 | — |
| 4 | pv-brief-text | text | 1 | 1 | gemini-3-flash | verified-brief-text | brief-text | — | 0.526 [0.472, 0.575] | 0.688 | 0.425 | — |
| 5 | pv-cascade-adversarial-checklist | text | 1 | 1 | gemini-3-flash | verified-cascade-adversarial-checklist | cascade-adversarial-checklist | — | 0.518 [0.464, 0.568] | 0.686 | 0.416 | — |
| 6 | pv-cascade-checklist-adversarial | text | 1 | 1 | gemini-3-flash | verified-cascade-checklist-adversarial | cascade-checklist-adversarial | — | 0.509 [0.452, 0.558] | 0.681 | 0.407 | — |
| 7 | pv-adversarial-image | image | 1 | 1 | gemini-3-flash | verified-adversarial-image | adversarial-image | — | 0.509 [0.451, 0.557] | 0.678 | 0.407 | — |
| 8 | pv-adversarial-text | text | 1 | 1 | gemini-3-flash | verified-adversarial-text | adversarial-text | — | 0.480 [0.422, 0.527] | 0.726 | 0.359 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
