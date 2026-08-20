# Leaderboard — Era 1, Single-pass (raw), 40 m buffer

**Generated**: 2026-08-20T06:34:06.282459+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/single-pass/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 21 in 1 tier(s). Bounds: `inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.644–0.718)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h4-canonical-last | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.718 [0.696, 0.742] | 0.605 | 0.881 | — |
| 2 | h8-track2-text-scale-4 | text | 1 | 1 | gemini-3-flash | library_scale-4-text | — | — | 0.649 [0.615, 0.678] | 0.523 | 0.855 | — |
| 3 | h8-track2-text-scale-8 | text | 1 | 1 | gemini-3-flash | library_scale-8-text | — | — | 0.652 [0.618, 0.681] | 0.525 | 0.859 | — |
| 4 | h4-config-default | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.713 [0.693, 0.732] | 0.612 | 0.853 | — |
| 5 | h5-track1-image-terse | image | 1 | 1 | gemini-3-flash | library_plus-hp_terse | — | — | 0.695 [0.672, 0.718] | 0.590 | 0.846 | — |
| 6 | h8-track2-text-canonical | text | 1 | 1 | gemini-3-flash | library_canonical-text | — | — | 0.646 [0.615, 0.676] | 0.517 | 0.861 | — |
| 7 | h8-track2-text-pure-positive-canon | text | 1 | 1 | gemini-3-flash | library_pure-positive-canon-text | — | — | 0.651 [0.616, 0.680] | 0.523 | 0.861 | — |
| 8 | h5-track1-image-verbose | image | 1 | 1 | gemini-3-flash | library_plus-hp_verbose | — | — | 0.710 [0.687, 0.732] | 0.613 | 0.844 | — |
| 9 | h4-canonical-first | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.715 [0.692, 0.737] | 0.607 | 0.868 | — |
| 10 | h8-track1-image-exploratory-pure-positive-4hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-4hp | — | — | 0.699 [0.678, 0.728] | 0.594 | 0.850 | — |
| 11 | h8-track1-image-plus-hp | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.715 [0.692, 0.737] | 0.607 | 0.868 | — |
| 12 | h5-track2-text-terse | text | 1 | 1 | gemini-3-flash | detect_brief-text_terse | — | — | 0.644 [0.613, 0.678] | 0.522 | 0.840 | — |
| 13 | h8-track2-text-plus-hp | text | 1 | 1 | gemini-3-flash | library_plus-hp-text | — | — | 0.649 [0.617, 0.678] | 0.522 | 0.857 | — |
| 14 | h8-track1-image-scale-8 | image | 1 | 1 | gemini-3-flash | library_scale-8 | — | — | 0.688 [0.666, 0.709] | 0.584 | 0.835 | — |
| 15 | h8-track1-image-scale-4 | image | 1 | 1 | gemini-3-flash | library_scale-4 | — | — | 0.670 [0.639, 0.694] | 0.557 | 0.839 | — |
| 16 | h5-track2-text-verbose | text | 1 | 1 | gemini-3-flash | detect_brief-text_verbose | — | — | 0.655 [0.625, 0.689] | 0.549 | 0.813 | — |
| 17 | h8-track1-image-canonical | image | 1 | 1 | gemini-3-flash | library_canonical | — | — | 0.680 [0.654, 0.702] | 0.594 | 0.794 | — |
| 18 | h8-track1-image-exploratory-pure-positive-2hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-2hp | — | — | 0.665 [0.636, 0.697] | 0.550 | 0.840 | — |
| 19 | h4-random | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.673 [0.645, 0.702] | 0.558 | 0.850 | — |
| 20 | h8-track1-image-exploratory-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.680 [0.658, 0.708] | 0.592 | 0.800 | — |
| 21 | h8-track1-image-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.676 [0.651, 0.703] | 0.586 | 0.800 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
