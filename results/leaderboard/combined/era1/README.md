# Combined / cross-architecture leaderboard — Era 1

This directory holds the **combined / cross-architecture tier tables for Era 1**: all 93 conditions across the 2 populated architectures (single-pass and consensus) pitted against each other in a single greedy-clique BH-FDR-tiered ranking, separately at each (buffer, metric, q-level) combination.

Era 1 has no Provider–Verifier (PV) or single-pass + PV cells; the 4-architecture matrix collapses to 2.

## Condition pool

| Architecture | N | Source per-architecture leaderboard |
|---|---:|---|
| single-pass | 21 | `../../per-architecture/era1/single-pass/` |
| consensus | 72 | `../../per-architecture/era1/consensus/` |
| single-pass + PV | 0 | (no Era 1 cells) |
| pv | 0 | (no Era 1 cells) |
| **Total** | **93** | |

C(93, 2) = 4,278 within-Era pairwise comparisons. Of those, **2,766** are within-architecture (pre-computed in the per-architecture caches and reused) and **1,512** are cross-architecture (computed fresh in this build).

## Files

| Pattern | Description |
|---|---|
| `leaderboard_tiers_f1_<B>m.{md,json}` | Per-buffer F1 tier table at q = 0.05 (B in {20, 30, 40, 50, 100} m) |
| `leaderboard_tiers_f1_q01_<B>m.{md,json}` | Per-buffer F1 tier table at q = 0.01 (sensitivity) |
| `leaderboard_tiers_mcc.{md,json}` | MCC tier table at q = 0.05 (single file — MCC is buffer-independent) |
| `leaderboard_tiers_mcc_q01.{md,json}` | MCC tier table at q = 0.01 (sensitivity) |
| `leaderboard_all_evaluations.json` | Resolved metric registry for all 93 conditions |
| `leaderboard_all_evaluations.metadata.json` | Bootstrap-CI sidecar |
| `tier_stability.md`, `tier_stability_mcc.md` | Spearman rho across buffers |

## Methodology

Identical to the per-architecture build (see `../../per-architecture/era1/<arch>/README.md`):

- **Bounds**: 340-tile 512 px scope (`inputs/vectors/bounds/full_evaluation_bounds.geojson`)
- **Per-cell threshold selection**: F1-maximising at 20 m primary buffer (Option A)
- **Per-buffer F1 tier construction**: 5 separate runs, one per primary buffer
- **MCC tier construction**: single buffer-independent run
- **Pairwise permutation tests**: 10,000 iterations, seed 42
- **BH-FDR family scope**: all C(93, 2) = 4,278 pairs within one (buffer, metric, q-level) combination
- **Greedy-clique tiering**

## See also

- Top-level combined README: `../README.md`
- Within-architecture stratified tables: `../../per-architecture/era1/`
- 4-row "best per architecture" Era 1 summary: `../../per-architecture/cross-architecture-era1_<B>m_<metric>.md`
