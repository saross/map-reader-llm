# Leaderboard — Era 3, Consensus (no PV), 30 m buffer

**Generated**: 2026-05-06T00:25:57.099150+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era3/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 14 in 1 tier(s). Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/h10_test_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.734–0.805)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h8v2-scale-4 | image | 5 | 4 | gemini-3-flash-preview | detect_h8_scale-4_v2 | — | — | 0.799 [0.773, 0.823] | 0.895 | 0.721 | — |
| 2 | h12v2-r1-hn-heavy | image | 5 | 3 | gemini-3-flash-preview | detect_h12_r1-hn-heavy_v2 | — | — | 0.805 [0.783, 0.826] | 0.795 | 0.815 | — |
| 3 | h8v2-scale-8 | image | 5 | 3 | gemini-3-flash-preview | detect_h8_scale-8_v2 | — | — | 0.792 [0.767, 0.811] | 0.795 | 0.790 | — |
| 4 | h10v2-pool_160_hp4hn4 | image | 5 | 4 | gemini-3-flash-preview | detect_pool_160_hp4hn4_v2 | — | — | 0.760 [0.734, 0.783] | 0.894 | 0.661 | — |
| 5 | h12v2-r2-balanced | image | 5 | 4 | gemini-3-flash | detect_pool_160_hp4hn4_v2 | — | — | 0.760 [0.734, 0.783] | 0.894 | 0.661 | — |
| 6 | h8v2-scale-32 | image | 5 | 4 | gemini-3-flash-preview | detect_h8_scale-32_v2 | — | — | 0.734 [0.705, 0.758] | 0.851 | 0.646 | — |
| 7 | h8v2-scale-16 | image | 5 | 3 | gemini-3-flash-preview | detect_h8_scale-16_v2 | — | — | 0.764 [0.736, 0.789] | 0.748 | 0.781 | — |
| 8 | h8v2-canonical | image | 5 | 4 | gemini-3-flash-preview | detect_h8_canonical_v2 | — | — | 0.759 [0.725, 0.786] | 0.849 | 0.686 | — |
| 9 | h8v2-pure-positive-canon | image | 5 | 3 | gemini-3-flash-preview | detect_h8_pure-positive-canon_v2 | — | — | 0.755 [0.729, 0.778] | 0.703 | 0.815 | — |
| 10 | h8v2-plus-hp | image | 5 | 4 | gemini-3-flash-preview | detect_h8_plus-hp_v2 | — | — | 0.775 [0.749, 0.799] | 0.874 | 0.696 | — |
| 11 | h12v2-r3-hp-heavy | image | 5 | 3 | gemini-3-flash-preview | detect_h12_r3-hp-heavy_v2 | — | — | 0.788 [0.762, 0.808] | 0.779 | 0.796 | — |
| 12 | h10v2-pool_020_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_020_hp4hn4_v2 | — | — | 0.757 [0.727, 0.784] | 0.730 | 0.787 | — |
| 13 | h10v2-pool_040_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_040_hp4hn4_v2 | — | — | 0.769 [0.745, 0.794] | 0.741 | 0.799 | — |
| 14 | h10v2-pool_080_hp4hn4 | image | 5 | 3 | gemini-3-flash-preview | detect_pool_080_hp4hn4_v2 | — | — | 0.758 [0.732, 0.782] | 0.733 | 0.784 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
