# Session 78 — Verifier Calibration Matrix Summary

Generated: 2026-04-24T16:01:18.642939Z

## Scope

* 2 candidate pools: image-T=0.7 (2 017 candidates), text-T=0.7 (3 736 candidates)
* 6 verifier prompt variants each = 12 total verifier runs
* Scope: 487-tile Era 2 full evaluation bounds

## Results table — F1 @ 20 m at per-buffer optimum

| Pool | Variant | vote_t | prob_t | F1 @ 20 m | Precision | Recall | MCC |
|------|---------|-------:|-------:|----------:|----------:|-------:|----:|
| image | adversarial | 3 | 0.15 | — | — | — | — |
| image | brief | 3 | 0.15 | — | — | — | — |
| image | brief-text | 3 | 0.15 | — | — | — | — |
| image | checklist | 3 | 0.15 | — | — | — | — |
| image | checklist-text | 3 | 0.15 | — | — | — | — |
| image | comparative | 3 | 0.25 | — | — | — | — |
| text | adversarial | 4 | 0.2 | — | — | — | — |
| text | brief | 4 | 0.15 | — | — | — | — |
| text | brief-text | 4 | 0.15 | — | — | — | — |
| text | checklist | 4 | 0.15 | — | — | — | — |
| text | checklist-text | 4 | 0.15 | — | — | — | — |
| text | comparative | 4 | 0.25 | — | — | — | — |

## Artefact locations

* Leaderboard cell sweeps: `results/leaderboard/cells/session-78-*.json`
* Deep evaluations: `results/verifier-calibration-matrix/<pool>-<variant>/`
* Materialised GeoJSONs at optima: `results/verifier-calibration-matrix/<pool>-<variant>-opt-20m.geojson`
* Logs: `logs/session-78-matrix/`

## Canonical baseline (not re-run)

`verify_adversarial-text` is the canonical verifier; its probabilities and downstream evaluations are preserved from prior sessions and remain the reference for cross-prompt comparison.

