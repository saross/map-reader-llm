# Leaderboard — Era 1, Single-pass (raw), 30 m buffer

**Generated**: 2026-08-20T06:34:06.280274+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/single-pass/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 21 in 1 tier(s). Bounds: `inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.627–0.686)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h4-canonical-last | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.686 [0.662, 0.711] | 0.578 | 0.842 | — |
| 2 | h8-track2-text-scale-4 | text | 1 | 1 | gemini-3-flash | library_scale-4-text | — | — | 0.640 [0.609, 0.669] | 0.516 | 0.844 | — |
| 3 | h8-track2-text-scale-8 | text | 1 | 1 | gemini-3-flash | library_scale-8-text | — | — | 0.645 [0.612, 0.675] | 0.520 | 0.850 | — |
| 4 | h4-config-default | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.671 [0.649, 0.693] | 0.576 | 0.803 | — |
| 5 | h5-track1-image-terse | image | 1 | 1 | gemini-3-flash | library_plus-hp_terse | — | — | 0.649 [0.626, 0.672] | 0.551 | 0.790 | — |
| 6 | h8-track2-text-canonical | text | 1 | 1 | gemini-3-flash | library_canonical-text | — | — | 0.636 [0.605, 0.666] | 0.509 | 0.848 | — |
| 7 | h8-track2-text-pure-positive-canon | text | 1 | 1 | gemini-3-flash | library_pure-positive-canon-text | — | — | 0.641 [0.606, 0.670] | 0.515 | 0.848 | — |
| 8 | h5-track1-image-verbose | image | 1 | 1 | gemini-3-flash | library_plus-hp_verbose | — | — | 0.668 [0.644, 0.695] | 0.577 | 0.794 | — |
| 9 | h4-canonical-first | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.664 [0.639, 0.687] | 0.564 | 0.807 | — |
| 10 | h8-track1-image-exploratory-pure-positive-4hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-4hp | — | — | 0.656 [0.633, 0.685] | 0.558 | 0.798 | — |
| 11 | h8-track1-image-plus-hp | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.664 [0.639, 0.687] | 0.564 | 0.807 | — |
| 12 | h5-track2-text-terse | text | 1 | 1 | gemini-3-flash | detect_brief-text_terse | — | — | 0.627 [0.597, 0.662] | 0.508 | 0.818 | — |
| 13 | h8-track2-text-plus-hp | text | 1 | 1 | gemini-3-flash | library_plus-hp-text | — | — | 0.638 [0.607, 0.666] | 0.513 | 0.842 | — |
| 14 | h8-track1-image-scale-8 | image | 1 | 1 | gemini-3-flash | library_scale-8 | — | — | 0.655 [0.632, 0.679] | 0.557 | 0.796 | — |
| 15 | h8-track1-image-scale-4 | image | 1 | 1 | gemini-3-flash | library_scale-4 | — | — | 0.637 [0.608, 0.662] | 0.530 | 0.798 | — |
| 16 | h5-track2-text-verbose | text | 1 | 1 | gemini-3-flash | detect_brief-text_verbose | — | — | 0.630 [0.597, 0.662] | 0.528 | 0.781 | — |
| 17 | h8-track1-image-canonical | image | 1 | 1 | gemini-3-flash | library_canonical | — | — | 0.653 [0.628, 0.677] | 0.571 | 0.762 | — |
| 18 | h8-track1-image-exploratory-pure-positive-2hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-2hp | — | — | 0.631 [0.604, 0.661] | 0.522 | 0.798 | — |
| 19 | h4-random | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.644 [0.616, 0.671] | 0.533 | 0.813 | — |
| 20 | h8-track1-image-exploratory-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.649 [0.621, 0.676] | 0.565 | 0.762 | — |
| 21 | h8-track1-image-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.646 [0.619, 0.674] | 0.560 | 0.764 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
