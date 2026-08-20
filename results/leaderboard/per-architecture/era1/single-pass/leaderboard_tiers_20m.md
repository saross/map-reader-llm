# Leaderboard — Era 1, Single-pass (raw), 20 m buffer

**Generated**: 2026-08-20T06:34:06.277901+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/single-pass/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 21 in 1 tier(s). Bounds: `inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.568–0.631)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h4-canonical-last | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.631 [0.609, 0.657] | 0.532 | 0.775 | — |
| 2 | h8-track2-text-scale-4 | text | 1 | 1 | gemini-3-flash | library_scale-4-text | — | — | 0.609 [0.577, 0.641] | 0.491 | 0.803 | — |
| 3 | h8-track2-text-scale-8 | text | 1 | 1 | gemini-3-flash | library_scale-8-text | — | — | 0.607 [0.574, 0.638] | 0.489 | 0.800 | — |
| 4 | h4-config-default | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.606 [0.576, 0.628] | 0.520 | 0.725 | — |
| 5 | h5-track1-image-terse | image | 1 | 1 | gemini-3-flash | library_plus-hp_terse | — | — | 0.605 [0.581, 0.631] | 0.514 | 0.737 | — |
| 6 | h8-track2-text-canonical | text | 1 | 1 | gemini-3-flash | library_canonical-text | — | — | 0.605 [0.569, 0.633] | 0.484 | 0.805 | — |
| 7 | h8-track2-text-pure-positive-canon | text | 1 | 1 | gemini-3-flash | library_pure-positive-canon-text | — | — | 0.605 [0.572, 0.636] | 0.486 | 0.800 | — |
| 8 | h5-track1-image-verbose | image | 1 | 1 | gemini-3-flash | library_plus-hp_verbose | — | — | 0.603 [0.573, 0.630] | 0.520 | 0.716 | — |
| 9 | h4-canonical-first | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.599 [0.572, 0.627] | 0.508 | 0.727 | — |
| 10 | h8-track1-image-exploratory-pure-positive-4hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-4hp | — | — | 0.599 [0.574, 0.625] | 0.508 | 0.727 | — |
| 11 | h8-track1-image-plus-hp | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.599 [0.572, 0.627] | 0.508 | 0.727 | — |
| 12 | h5-track2-text-terse | text | 1 | 1 | gemini-3-flash | detect_brief-text_terse | — | — | 0.598 [0.570, 0.634] | 0.485 | 0.781 | — |
| 13 | h8-track2-text-plus-hp | text | 1 | 1 | gemini-3-flash | library_plus-hp-text | — | — | 0.597 [0.565, 0.630] | 0.480 | 0.788 | — |
| 14 | h8-track1-image-scale-8 | image | 1 | 1 | gemini-3-flash | library_scale-8 | — | — | 0.587 [0.562, 0.612] | 0.499 | 0.712 | — |
| 15 | h8-track1-image-scale-4 | image | 1 | 1 | gemini-3-flash | library_scale-4 | — | — | 0.584 [0.554, 0.609] | 0.486 | 0.731 | — |
| 16 | h5-track2-text-verbose | text | 1 | 1 | gemini-3-flash | detect_brief-text_verbose | — | — | 0.583 [0.549, 0.616] | 0.489 | 0.724 | — |
| 17 | h8-track1-image-canonical | image | 1 | 1 | gemini-3-flash | library_canonical | — | — | 0.581 [0.555, 0.610] | 0.508 | 0.679 | — |
| 18 | h8-track1-image-exploratory-pure-positive-2hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-2hp | — | — | 0.571 [0.543, 0.603] | 0.473 | 0.722 | — |
| 19 | h4-random | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.571 [0.539, 0.601] | 0.473 | 0.720 | — |
| 20 | h8-track1-image-exploratory-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.570 [0.541, 0.601] | 0.496 | 0.670 | — |
| 21 | h8-track1-image-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.568 [0.542, 0.599] | 0.492 | 0.672 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
