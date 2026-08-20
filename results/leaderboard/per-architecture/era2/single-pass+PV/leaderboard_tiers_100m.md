# Leaderboard — Era 2, Single-pass + PV, 100 m buffer

**Generated**: 2026-08-20T06:34:06.359530+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/single-pass+PV/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 8 in 1 tier(s). Bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.486–0.552)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | pv-checklist-image | image | 1 | 1 | gemini-3-flash | verified-checklist-image | checklist-image | — | 0.552 [0.494, 0.599] | 0.644 | 0.483 | — |
| 2 | pv-checklist-text | text | 1 | 1 | gemini-3-flash | verified-checklist-text | checklist-text | — | 0.542 [0.487, 0.591] | 0.622 | 0.480 | — |
| 3 | pv-brief-image | image | 1 | 1 | gemini-3-flash | verified-brief-image | brief-image | — | 0.541 [0.485, 0.589] | 0.632 | 0.474 | — |
| 4 | pv-brief-text | text | 1 | 1 | gemini-3-flash | verified-brief-text | brief-text | — | 0.534 [0.483, 0.584] | 0.699 | 0.432 | — |
| 5 | pv-cascade-adversarial-checklist | text | 1 | 1 | gemini-3-flash | verified-cascade-adversarial-checklist | cascade-adversarial-checklist | — | 0.526 [0.474, 0.575] | 0.697 | 0.423 | — |
| 6 | pv-cascade-checklist-adversarial | text | 1 | 1 | gemini-3-flash | verified-cascade-checklist-adversarial | cascade-checklist-adversarial | — | 0.518 [0.462, 0.566] | 0.692 | 0.414 | — |
| 7 | pv-adversarial-image | image | 1 | 1 | gemini-3-flash | verified-adversarial-image | adversarial-image | — | 0.517 [0.460, 0.564] | 0.690 | 0.414 | — |
| 8 | pv-adversarial-text | text | 1 | 1 | gemini-3-flash | verified-adversarial-text | adversarial-text | — | 0.486 [0.431, 0.533] | 0.735 | 0.363 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
