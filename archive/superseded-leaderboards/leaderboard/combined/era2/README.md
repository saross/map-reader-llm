# Combined / cross-architecture leaderboard — Era 2

This directory holds the **combined / cross-architecture tier tables for Era 2**: all 87 conditions across all 4 architectures (single-pass, consensus, single-pass + Provider–Verifier (PV), PV-only) pitted against each other in a single greedy-clique BH-FDR-tiered ranking, separately at each (buffer, metric, q-level) combination.

## Condition pool

| Architecture | N | Source per-architecture leaderboard |
|---|---:|---|
| single-pass | 6 | `../../per-architecture/era2/single-pass/` |
| consensus | 29 | `../../per-architecture/era2/consensus/` |
| single-pass + PV | 8 | `../../per-architecture/era2/single-pass+PV/` |
| pv | 44 | `../../per-architecture/era2/pv/` |
| **Total** | **87** | |

C(87, 2) = 3,741 within-Era pairwise comparisons. Of those, **1,395** are within-architecture (pre-computed in the per-architecture caches and reused) and **2,346** are cross-architecture (computed fresh in this build).

## Files

| Pattern | Description |
|---|---|
| `leaderboard_tiers_f1_<B>m.{md,json}` | Per-buffer F1 tier table at q = 0.05 (B in {20, 30, 40, 50, 100} m) |
| `leaderboard_tiers_f1_q01_<B>m.{md,json}` | Per-buffer F1 tier table at q = 0.01 (sensitivity) |
| `leaderboard_tiers_mcc.{md,json}` | MCC tier table at q = 0.05 (single file — MCC is buffer-independent) |
| `leaderboard_tiers_mcc_q01.{md,json}` | MCC tier table at q = 0.01 (sensitivity) |
| `leaderboard_all_evaluations.json` | Resolved metric registry for all 87 conditions |
| `leaderboard_all_evaluations.metadata.json` | Bootstrap-CI sidecar |
| `tier_stability.md`, `tier_stability_mcc.md` | Spearman rho across buffers |

## Methodology

Identical to the per-architecture build (see `../../per-architecture/era2/<arch>/README.md`):

- **Bounds**: 487-tile 384 px scope (`inputs/vectors/bounds/384/full_evaluation_bounds.geojson`)
- **Per-cell threshold selection**: F1-maximising at 20 m primary buffer (Option A)
- **Per-buffer F1 tier construction**: 5 separate runs, one per primary buffer (20, 30, 40, 50, 100 m); each run fixes thresholds at 20 m via `--threshold-buffer 20` and runs pairwise + tiering at the chosen primary buffer
- **MCC tier construction**: single buffer-independent run (the tile-level MCC permutation test does not take a buffer argument)
- **Pairwise permutation tests**: 10,000 iterations, seed 42, paired tile-swap (F1) or per-tile (TP, TN, FP, FN) classification swap (MCC)
- **BH-FDR family scope**: all C(87, 2) = 3,741 pairs within one (buffer, metric, q-level) combination
- **Greedy-clique tiering**: conditions sorted by metric descending; appended to current tier if BH-adjusted p ≥ q against every current member, else start new tier

## Driver

`scripts/build_combined_leaderboard.sh 2`. The driver:

1. Hardlinks per-architecture caches (`pairwise/`, `pairwise_f1_<B>m/`, `pairwise_mcc/`, `evaluations/`) from the 4 per-arch dirs into the combined cache dir
2. Runs the F1 builder once per primary buffer × q-level (10 invocations); each invocation passes `--buffers "20 <primary>" --primary-buffer <primary> --threshold-buffer 20` and immediately preserves the primary's `.md`/`.json` under the final combined name before the next pass overwrites it
3. Runs the MCC builder twice (q=0.05, q=0.01)
4. Cleans up stale native-named files

## See also

- Top-level combined README: `../README.md`
- Within-architecture stratified tables: `../../per-architecture/era2/`
- 4-row "best per architecture" Era 2 summary: `../../per-architecture/cross-architecture-era2_<B>m_<metric>.md`
