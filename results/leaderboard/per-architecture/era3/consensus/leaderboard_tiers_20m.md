# Leaderboard — Era 3, Consensus (no PV), 20 m buffer

**Generated**: 2026-05-06T00:25:57.098184+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era3/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 14 in 1 tier(s). Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/h10_test_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.688–0.733)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h8v2-scale-4 | image | 5 | 4 | gemini-3-flash-preview | detect_h8_scale-4_v2 | — | — | 0.733 [0.699, 0.760] | 0.821 | 0.661 | 0.772 |
| 2 | h12v2-r1-hn-heavy | image | 5 | 3 | gemini-3-flash-preview | detect_h12_r1-hn-heavy_v2 | — | — | 0.731 [0.700, 0.753] | 0.722 | 0.740 | 0.725 |
| 3 | h8v2-scale-8 | image | 5 | 3 | gemini-3-flash-preview | detect_h8_scale-8_v2 | — | — | 0.730 [0.703, 0.757] | 0.732 | 0.727 | 0.739 |
| 4 | h10v2-pool_160_hp4hn4 | image | 5 | 4 | gemini-3-flash-preview | detect_pool_160_hp4hn4_v2 | — | — | 0.717 [0.690, 0.750] | 0.843 | 0.624 | 0.718 |
| 5 | h12v2-r2-balanced | image | 5 | 4 | gemini-3-flash | detect_pool_160_hp4hn4_v2 | — | — | 0.717 [0.690, 0.750] | 0.843 | 0.624 | 0.718 |
| 6 | h8v2-scale-32 | image | 5 | 4 | gemini-3-flash-preview | detect_h8_scale-32_v2 | — | — | 0.713 [0.680, 0.737] | 0.826 | 0.627 | 0.718 |
| 7 | h8v2-scale-16 | image | 5 | 3 | gemini-3-flash-preview | detect_h8_scale-16_v2 | — | — | 0.712 [0.680, 0.741] | 0.697 | 0.727 | 0.726 |
| 8 | h8v2-canonical | image | 5 | 4 | gemini-3-flash-preview | detect_h8_canonical_v2 | — | — | 0.707 [0.675, 0.737] | 0.791 | 0.639 | 0.681 |
| 9 | h8v2-pure-positive-canon | image | 5 | 3 | gemini-3-flash-preview | detect_h8_pure-positive-canon_v2 | — | — | 0.705 [0.675, 0.737] | 0.657 | 0.762 | 0.598 |
| 10 | h8v2-plus-hp | image | 5 | 4 | gemini-3-flash-preview | detect_h8_plus-hp_v2 | — | — | 0.705 [0.668, 0.730] | 0.795 | 0.633 | 0.732 |
| 11 | h12v2-r3-hp-heavy | image | 5 | 3 | gemini-3-flash-preview | detect_h12_r3-hp-heavy_v2 | — | — | 0.701 [0.673, 0.728] | 0.693 | 0.709 | 0.733 |
| 12 | h10v2-pool_020_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_020_hp4hn4_v2 | — | — | 0.697 [0.666, 0.726] | 0.671 | 0.724 | 0.686 |
| 13 | h10v2-pool_040_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_040_hp4hn4_v2 | — | — | 0.694 [0.658, 0.723] | 0.669 | 0.721 | 0.640 |
| 14 | h10v2-pool_080_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_080_hp4hn4_v2 | — | — | 0.688 [0.656, 0.719] | 0.666 | 0.712 | 0.691 |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
