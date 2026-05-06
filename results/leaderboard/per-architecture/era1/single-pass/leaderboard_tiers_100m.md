# Leaderboard — Era 1, Single-pass (raw), 100 m buffer

**Generated**: 2026-05-06T00:25:57.034425+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/single-pass/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 21 in 1 tier(s). Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.655–0.753)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h4-canonical-last | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.730 [0.708, 0.752] | 0.615 | 0.896 | — |
| 2 | h8-track2-text-scale-4 | text | 1 | 1 | gemini-3-flash | library_scale-4-text | — | — | 0.661 [0.629, 0.690] | 0.533 | 0.872 | — |
| 3 | h8-track2-text-scale-8 | text | 1 | 1 | gemini-3-flash | library_scale-8-text | — | — | 0.662 [0.628, 0.691] | 0.533 | 0.872 | — |
| 4 | h4-config-default | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.753 [0.732, 0.772] | 0.646 | 0.902 | — |
| 5 | h5-track1-image-terse | image | 1 | 1 | gemini-3-flash | library_plus-hp_terse | — | — | 0.738 [0.713, 0.759] | 0.626 | 0.898 | — |
| 6 | h8-track2-text-canonical | text | 1 | 1 | gemini-3-flash | library_canonical-text | — | — | 0.655 [0.625, 0.685] | 0.524 | 0.872 | — |
| 7 | h8-track2-text-pure-positive-canon | text | 1 | 1 | gemini-3-flash | library_pure-positive-canon-text | — | — | 0.659 [0.624, 0.687] | 0.530 | 0.872 | — |
| 8 | h5-track1-image-verbose | image | 1 | 1 | gemini-3-flash | library_plus-hp_verbose | — | — | 0.742 [0.719, 0.762] | 0.640 | 0.881 | — |
| 9 | h4-canonical-first | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.739 [0.715, 0.760] | 0.628 | 0.898 | — |
| 10 | h8-track1-image-exploratory-pure-positive-4hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-4hp | — | — | 0.741 [0.721, 0.767] | 0.629 | 0.900 | — |
| 11 | h8-track1-image-plus-hp | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.739 [0.715, 0.760] | 0.628 | 0.898 | — |
| 12 | h5-track2-text-terse | text | 1 | 1 | gemini-3-flash | detect_brief-text_terse | — | — | 0.664 [0.635, 0.699] | 0.538 | 0.866 | — |
| 13 | h8-track2-text-plus-hp | text | 1 | 1 | gemini-3-flash | library_plus-hp-text | — | — | 0.659 [0.627, 0.688] | 0.530 | 0.870 | — |
| 14 | h8-track1-image-scale-8 | image | 1 | 1 | gemini-3-flash | library_scale-8 | — | — | 0.727 [0.704, 0.747] | 0.618 | 0.883 | — |
| 15 | h8-track1-image-scale-4 | image | 1 | 1 | gemini-3-flash | library_scale-4 | — | — | 0.705 [0.674, 0.732] | 0.587 | 0.883 | — |
| 16 | h5-track2-text-verbose | text | 1 | 1 | gemini-3-flash | detect_brief-text_verbose | — | — | 0.681 [0.648, 0.712] | 0.570 | 0.844 | — |
| 17 | h8-track1-image-canonical | image | 1 | 1 | gemini-3-flash | library_canonical | — | — | 0.709 [0.686, 0.729] | 0.619 | 0.828 | — |
| 18 | h8-track1-image-exploratory-pure-positive-2hp | image | 1 | 1 | gemini-3-flash | library_pure-positive-2hp | — | — | 0.696 [0.668, 0.730] | 0.576 | 0.879 | — |
| 19 | h4-random | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.713 [0.685, 0.740] | 0.591 | 0.900 | — |
| 20 | h8-track1-image-exploratory-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.718 [0.694, 0.743] | 0.625 | 0.844 | — |
| 21 | h8-track1-image-pure-positive-canon | image | 1 | 1 | gemini-3-flash | library_pure-positive-canon | — | — | 0.714 [0.689, 0.738] | 0.618 | 0.844 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
