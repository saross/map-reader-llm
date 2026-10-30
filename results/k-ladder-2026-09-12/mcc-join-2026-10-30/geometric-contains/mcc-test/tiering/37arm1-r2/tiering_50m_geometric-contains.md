# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-37arm1-r2-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_50m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 3 (0 single-pass + 0 consensus + 3 verified-PV), 8541 evaluation tiles
- **Metric**: micro-average F1 @ 50 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 3 (2 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `gemini37-55map-2026-08-29::arm1-n5-oracle-p0.15-k5-r2-gt`, `gemini37-55map-2026-08-29::arm1-n3-oracle-p0.15-k3-r2-gt`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `arm1-n5-oracle-p0.15-k5-r2-gt` | verified-PV | 1 | 0.873 | 0.873 | +0.000 | 0.715 | 1 |
| 2 | `arm1-n3-oracle-p0.15-k3-r2-gt` | verified-PV | 1 | 0.871 | 0.870 | -0.000 | 0.718 | 1 |
| 3 | `arm1-n1-oracle-p0.20-k1-r2-gt` | verified-PV | 1 | 0.841 | 0.841 | -0.000 | 0.725 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 3 (2 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 2; MCC tie set 2 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `arm1-n1-oracle-p0.20-k1-r2-gt` | 0.8768 | 1 | 2 | 0.8413 |
| 2 | `arm1-n3-oracle-p0.15-k3-r2-gt` | 0.8727 | 1 | 1 | 0.8705 |
| 3 | `arm1-n5-oracle-p0.15-k5-r2-gt` | 0.8673 | 2 | 1 | 0.8727 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `gemini37-55map-2026-08-29::arm1-n1-oracle-p0.20-k1-r2-gt` | `gemini37-55map-2026-08-29::arm1-n3-oracle-p0.15-k3-r2-gt` | 0.8768 | 0.8727 | +0.0041 | 0.2888 | 0.2888 | no |
| `gemini37-55map-2026-08-29::arm1-n1-oracle-p0.20-k1-r2-gt` | `gemini37-55map-2026-08-29::arm1-n5-oracle-p0.15-k5-r2-gt` | 0.8768 | 0.8673 | +0.0096 | 0.0160 | 0.0240 | yes |
| `gemini37-55map-2026-08-29::arm1-n3-oracle-p0.15-k3-r2-gt` | `gemini37-55map-2026-08-29::arm1-n5-oracle-p0.15-k5-r2-gt` | 0.8727 | 0.8673 | +0.0055 | 0.0015 | 0.0045 | yes |
