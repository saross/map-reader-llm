# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-55map-stride-b-g37vf-r2-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_50m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 3 (0 single-pass + 0 consensus + 3 verified-PV), 8541 evaluation tiles
- **Metric**: micro-average F1 @ 50 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 3 (3 significant) -> **3 tiers**
- **Tie set (Tier 1)**: `stride-55map-2026-08-25::g384-ov192-55map-n10-verified37-oracle-p0.96-k9-r2-gt`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g384-ov192-55map-n10-verified37-oracle-p0.96-k9-r2-gt` | verified-PV | 1 | 0.881 | 0.881 | +0.000 | 0.736 | 1 |
| 2 | `g384-ov192-55map-n3-verified37-oracle-p0.96-k3-r2-gt` | verified-PV | 1 | 0.875 | 0.875 | +0.000 | 0.738 | 2 |
| 3 | `g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt` | verified-PV | 1 | 0.835 | 0.835 | -0.000 | 0.747 | 3 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 3 (2 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 2; MCC tie set 1 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt` | 0.9048 | 1 | 3 | 0.8352 |
| 2 | `g384-ov192-55map-n3-verified37-oracle-p0.96-k3-r2-gt` | 0.8954 | 2 | 2 | 0.8747 |
| 3 | `g384-ov192-55map-n10-verified37-oracle-p0.96-k9-r2-gt` | 0.8936 | 2 | 1 | 0.8813 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `stride-55map-2026-08-25::g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n3-verified37-oracle-p0.96-k3-r2-gt` | 0.9048 | 0.8954 | +0.0094 | 0.0001 | 0.0001 | yes |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-verified37-oracle-p0.96-k9-r2-gt` | 0.9048 | 0.8936 | +0.0112 | 0.0000 | 0.0000 | yes |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-verified37-oracle-p0.96-k3-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-verified37-oracle-p0.96-k9-r2-gt` | 0.8954 | 0.8936 | +0.0018 | 0.3323 | 0.3323 | no |
