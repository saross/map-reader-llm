# Leaderboard — Era 3, Consensus (no PV), 40 m buffer

**Generated**: 2026-08-20T06:34:06.387862+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era3/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 14 in 1 tier(s). Bounds: `inputs/vectors/bounds/384/h10_test_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.752–0.824)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h8v2-scale-4 | image | 5 | 4 | gemini-3-flash-preview | detect_h8_scale-4_v2 | — | — | 0.812 [0.788, 0.838] | 0.910 | 0.734 | — |
| 2 | h12v2-r1-hn-heavy | image | 5 | 3 | gemini-3-flash-preview | detect_h12_r1-hn-heavy_v2 | — | — | 0.824 [0.804, 0.842] | 0.814 | 0.834 | — |
| 3 | h8v2-scale-8 | image | 5 | 3 | gemini-3-flash-preview | detect_h8_scale-8_v2 | — | — | 0.808 [0.783, 0.829] | 0.811 | 0.806 | — |
| 4 | h10v2-pool_160_hp4hn4 | image | 5 | 4 | gemini-3-flash-preview | detect_pool_160_hp4hn4_v2 | — | — | 0.786 [0.759, 0.809] | 0.924 | 0.683 | — |
| 5 | h12v2-r2-balanced | image | 5 | 4 | gemini-3-flash | detect_pool_160_hp4hn4_v2 | — | — | 0.786 [0.759, 0.809] | 0.924 | 0.683 | — |
| 6 | h8v2-scale-32 | image | 5 | 4 | gemini-3-flash-preview | detect_h8_scale-32_v2 | — | — | 0.752 [0.721, 0.777] | 0.872 | 0.661 | — |
| 7 | h8v2-scale-16 | image | 5 | 3 | gemini-3-flash-preview | detect_h8_scale-16_v2 | — | — | 0.794 [0.770, 0.816] | 0.778 | 0.812 | — |
| 8 | h8v2-canonical | image | 5 | 4 | gemini-3-flash-preview | detect_h8_canonical_v2 | — | — | 0.776 [0.747, 0.803] | 0.868 | 0.702 | — |
| 9 | h8v2-pure-positive-canon | image | 5 | 3 | gemini-3-flash-preview | detect_h8_pure-positive-canon_v2 | — | — | 0.784 [0.762, 0.804] | 0.730 | 0.846 | — |
| 10 | h8v2-plus-hp | image | 5 | 4 | gemini-3-flash-preview | detect_h8_plus-hp_v2 | — | — | 0.785 [0.760, 0.809] | 0.886 | 0.705 | — |
| 11 | h12v2-r3-hp-heavy | image | 5 | 3 | gemini-3-flash-preview | detect_h12_r3-hp-heavy_v2 | — | — | 0.809 [0.788, 0.830] | 0.801 | 0.818 | — |
| 12 | h10v2-pool_020_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_020_hp4hn4_v2 | — | — | 0.781 [0.754, 0.805] | 0.753 | 0.812 | — |
| 13 | h10v2-pool_040_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_040_hp4hn4_v2 | — | — | 0.781 [0.757, 0.805] | 0.753 | 0.812 | — |
| 14 | h10v2-pool_080_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_080_hp4hn4_v2 | — | — | 0.779 [0.754, 0.803] | 0.754 | 0.806 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
