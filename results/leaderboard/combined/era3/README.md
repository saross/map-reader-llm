# Combined / cross-architecture leaderboard — Era 3

This directory holds the **combined / cross-architecture tier tables for Era 3**: all conditions across all architectures pitted against each other in one greedy-clique BH-FDR-tiered ranking, separately at each (buffer, metric, q-level) combination.

## Equivalence note

Era 3 (327-tile, pool_160-excluded scope) contains conditions from a **single architecture** — `consensus` (N = 14). All H10 conditions in Era 3 are K-pass consensus runs; no single-pass, single-pass + Provider–Verifier (PV), or PV-only architectures contribute Era 3 cells.

Because there is only one architecture, the **combined leaderboard is identical to the within-architecture consensus leaderboard**. The files in this directory are copies (not symlinks, for git-tracking convenience) of the canonical per-architecture consensus tables at:

```
results/leaderboard/per-architecture/era3/consensus/
```

## Files

| Output | Source (per-architecture consensus) | Notes |
|---|---|---|
| `leaderboard_tiers_f1_<B>m.{md,json}` | `leaderboard_tiers_<B>m.{md,json}` | Per-buffer F1 tier tables, q = 0.05 |
| `leaderboard_tiers_f1_q01_<B>m.{md,json}` | `leaderboard_tiers_q01_<B>m.{md,json}` | Per-buffer F1 tier tables, q = 0.01 (sensitivity) |
| `leaderboard_tiers_mcc.{md,json}` | `leaderboard_tiers_mcc_20m.{md,json}` | MCC tier table (buffer-independent; all 5 source per-buffer copies are identical) |
| `leaderboard_tiers_mcc_q01.{md,json}` | `leaderboard_tiers_mcc_q01_20m.{md,json}` | MCC tier table, q = 0.01 |
| `leaderboard_all_evaluations.json` | identical | Bootstrap-CI metric registry for all 14 conditions |
| `leaderboard_all_evaluations.metadata.json` | regenerated | Sidecar describing the combined view |
| `tier_stability{,_mcc}.{md,json}` | identical | Spearman rho stability across buffers |

## Methodology

Identical to the per-architecture consensus build (see `results/leaderboard/per-architecture/era3/consensus/README.md`):

- Paired permutation tests: 10,000 iterations, seed 42
- Threshold selection: 20 m primary buffer (Option A: per-cell threshold fixed at 20 m, retained across buffers)
- Per-buffer F1: separate pairwise tests at each of {20, 30, 40, 50, 100} m
- MCC: tile-level Matthews Correlation Coefficient, buffer-independent
- Greedy-clique tiering after BH-FDR correction within each (Era × buffer × metric × q-level) family

## See also

- Top-level combined README: `../README.md`
- Within-architecture stratified tables: `../../per-architecture/era3/`
- 4-row "best per architecture" cross-architecture summary: `../../per-architecture/cross-architecture-era3_*.md`
