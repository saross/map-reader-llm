# Leaderboard — Era 3, Consensus (no PV), 50 m buffer

**Generated**: 2026-08-20T06:34:06.389266+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era3/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 14 in 1 tier(s). Bounds: `inputs/vectors/bounds/384/h10_test_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.759–0.833)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h8v2-scale-4 | image | 5 | 4 | gemini-3-flash-preview | detect_h8_scale-4_v2 | — | — | 0.816 [0.790, 0.840] | 0.914 | 0.737 | — |
| 2 | h12v2-r1-hn-heavy | image | 5 | 3 | gemini-3-flash-preview | detect_h12_r1-hn-heavy_v2 | — | — | 0.833 [0.816, 0.850] | 0.823 | 0.843 | — |
| 3 | h8v2-scale-8 | image | 5 | 3 | gemini-3-flash-preview | detect_h8_scale-8_v2 | — | — | 0.815 [0.791, 0.835] | 0.817 | 0.812 | — |
| 4 | h10v2-pool_160_hp4hn4 | image | 5 | 4 | gemini-3-flash-preview | detect_pool_160_hp4hn4_v2 | — | — | 0.786 [0.759, 0.809] | 0.924 | 0.683 | — |
| 5 | h12v2-r2-balanced | image | 5 | 4 | gemini-3-flash | detect_pool_160_hp4hn4_v2 | — | — | 0.786 [0.759, 0.809] | 0.924 | 0.683 | — |
| 6 | h8v2-scale-32 | image | 5 | 4 | gemini-3-flash-preview | detect_h8_scale-32_v2 | — | — | 0.759 [0.731, 0.784] | 0.880 | 0.668 | — |
| 7 | h8v2-scale-16 | image | 5 | 3 | gemini-3-flash-preview | detect_h8_scale-16_v2 | — | — | 0.807 [0.782, 0.830] | 0.790 | 0.825 | — |
| 8 | h8v2-canonical | image | 5 | 4 | gemini-3-flash-preview | detect_h8_canonical_v2 | — | — | 0.780 [0.749, 0.806] | 0.872 | 0.705 | — |
| 9 | h8v2-pure-positive-canon | image | 5 | 3 | gemini-3-flash-preview | detect_h8_pure-positive-canon_v2 | — | — | 0.787 [0.763, 0.806] | 0.732 | 0.850 | — |
| 10 | h8v2-plus-hp | image | 5 | 4 | gemini-3-flash-preview | detect_h8_plus-hp_v2 | — | — | 0.789 [0.763, 0.812] | 0.890 | 0.709 | — |
| 11 | h12v2-r3-hp-heavy | image | 5 | 3 | gemini-3-flash-preview | detect_h12_r3-hp-heavy_v2 | — | — | 0.819 [0.796, 0.840] | 0.810 | 0.828 | — |
| 12 | h10v2-pool_020_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_020_hp4hn4_v2 | — | — | 0.796 [0.772, 0.818] | 0.767 | 0.828 | — |
| 13 | h10v2-pool_040_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_040_hp4hn4_v2 | — | — | 0.793 [0.771, 0.814] | 0.764 | 0.825 | — |
| 14 | h10v2-pool_080_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_080_hp4hn4_v2 | — | — | 0.794 [0.772, 0.818] | 0.768 | 0.821 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
