# Leaderboard — Era 1, Single-pass (raw), 50 m buffer

**Generated**: 2026-05-06T00:25:57.033000+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/single-pass/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 21 in 1 tier(s). Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.650–0.734)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h4-canonical-last | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.724 [0.701, 0.748] | 0.610 | 0.889 | — |
| 2 | h8-track2-text-scale-4 | text | 1 | 1 | gemini-3-flash | library_scale-4-text | — | — | 0.654 [0.620, 0.682] | 0.527 | 0.863 | — |
| 3 | h8-track2-text-scale-8 | text | 1 | 1 | gemini-3-flash | library_scale-8-text | — | — | 0.658 [0.624, 0.686] | 0.530 | 0.866 | — |
| 4 | h4-config-default | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.734 [0.713, 0.753] | 0.630 | 0.879 | — |
| 5 | h5-track1-image-terse | image | 1 | 1 | gemini-3-flash | library_plus-hp_terse | — | — | 0.717 [0.693, 0.739] | 0.608 | 0.872 | — |
| 6 | h8-track2-text-canonical | text | 1 | 1 | gemini-3-flash | library_canonical-text | — | — | 0.650 [0.620, 0.681] | 0.521 | 0.866 | — |
| 7 | h8-track2-text-pure-positive-canon | text | 1 | 1 | gemini-3-flash | library_pure-positive-canon-text | — | — | 0.655 [0.619, 0.682] | 0.526 | 0.866 | — |
| 8 | h5-track1-image-verbose | image | 1 | 1 | gemini-3-flash | library_plus-hp_verbose | — | — | 0.726 [0.702, 0.746] | 0.627 | 0.863 | — |
| 9 | h4-canonical-first | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.730 [0.708, 0.754] | 0.620 | 0.887 | — |
| 10 | h8-track1-image-exploratory-pure-positive-4hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-4hp | — | — | 0.724 [0.702, 0.751] | 0.615 | 0.879 | — |
| 11 | h8-track1-image-plus-hp | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.730 [0.708, 0.754] | 0.620 | 0.887 | — |
| 12 | h5-track2-text-terse | text | 1 | 1 | gemini-3-flash | detect_brief-text_terse | — | — | 0.654 [0.626, 0.689] | 0.530 | 0.853 | — |
| 13 | h8-track2-text-plus-hp | text | 1 | 1 | gemini-3-flash | library_plus-hp-text | — | — | 0.654 [0.623, 0.684] | 0.527 | 0.865 | — |
| 14 | h8-track1-image-scale-8 | image | 1 | 1 | gemini-3-flash | library_scale-8 | — | — | 0.704 [0.682, 0.725] | 0.599 | 0.855 | — |
| 15 | h8-track1-image-scale-4 | image | 1 | 1 | gemini-3-flash | library_scale-4 | — | — | 0.690 [0.659, 0.717] | 0.575 | 0.865 | — |
| 16 | h5-track2-text-verbose | text | 1 | 1 | gemini-3-flash | detect_brief-text_verbose | — | — | 0.667 [0.634, 0.699] | 0.559 | 0.828 | — |
| 17 | h8-track1-image-canonical | image | 1 | 1 | gemini-3-flash | library_canonical | — | — | 0.689 [0.666, 0.712] | 0.603 | 0.805 | — |
| 18 | h8-track1-image-exploratory-pure-positive-2hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-2hp | — | — | 0.678 [0.649, 0.710] | 0.561 | 0.857 | — |
| 19 | h4-random | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.697 [0.668, 0.722] | 0.577 | 0.879 | — |
| 20 | h8-track1-image-exploratory-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.699 [0.676, 0.726] | 0.609 | 0.822 | — |
| 21 | h8-track1-image-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.695 [0.671, 0.719] | 0.602 | 0.822 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
