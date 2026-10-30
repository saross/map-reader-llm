# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-55map-stride-a-r2-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_50m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 8541 evaluation tiles
- **Metric**: micro-average F1 @ 50 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (6 significant) -> **4 tiers**
- **Tie set (Tier 1)**: `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | verified-PV | 1 | 0.842 | 0.842 | -0.000 | 0.695 | 1 |
| 2 | `g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | verified-PV | 1 | 0.838 | 0.838 | -0.000 | 0.691 | 2 |
| 3 | `g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | verified-PV | 1 | 0.832 | 0.832 | -0.000 | 0.702 | 3 |
| 4 | `g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | verified-PV | 1 | 0.823 | 0.823 | -0.000 | 0.701 | 4 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (4 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 3; MCC tie set 2 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | 0.8480 | 1 | 3 | 0.8321 |
| 2 | `g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | 0.8455 | 1 | 4 | 0.8227 |
| 3 | `g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | 0.8390 | 2 | 1 | 0.8419 |
| 4 | `g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | 0.8341 | 3 | 2 | 0.8383 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | 0.8455 | 0.8480 | -0.0024 | 0.3350 | 0.3350 | no |
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | 0.8455 | 0.8341 | +0.0114 | 0.0046 | 0.0138 | yes |
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | 0.8455 | 0.8390 | +0.0066 | 0.1022 | 0.1226 | no |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | 0.8480 | 0.8341 | +0.0139 | 0.0000 | 0.0000 | yes |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | 0.8480 | 0.8390 | +0.0090 | 0.0091 | 0.0182 | yes |
| `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | 0.8341 | 0.8390 | -0.0049 | 0.0155 | 0.0232 | yes |
