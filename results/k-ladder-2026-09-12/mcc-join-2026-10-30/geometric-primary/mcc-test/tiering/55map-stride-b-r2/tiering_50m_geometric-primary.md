# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-55map-stride-b-r2-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_50m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 8541 evaluation tiles
- **Metric**: micro-average F1 @ 50 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (5 significant) -> **3 tiers**
- **Tie set (Tier 1)**: `stride-55map-2026-08-25::g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt` | verified-PV | 1 | 0.856 | 0.856 | -0.000 | 0.712 | 1 |
| 2 | `g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | verified-PV | 1 | 0.852 | 0.852 | +0.000 | 0.710 | 2 |
| 3 | `g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | verified-PV | 1 | 0.851 | 0.851 | -0.000 | 0.713 | 2 |
| 4 | `g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | verified-PV | 1 | 0.801 | 0.801 | -0.000 | 0.709 | 3 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (2 significant)
- **Tile join**: `geometric-primary` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-primary', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 2; MCC tie set 3 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | 0.8705 | 1 | 2 | 0.8507 |
| 2 | `g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt` | 0.8702 | 1 | 1 | 0.8560 |
| 3 | `g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | 0.8671 | 1 | 2 | 0.8516 |
| 4 | `g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | 0.8591 | 2 | 3 | 0.8013 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `stride-55map-2026-08-25::g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | 0.8591 | 0.8705 | -0.0114 | 0.0012 | 0.0072 | yes |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | 0.8591 | 0.8671 | -0.0080 | 0.0384 | 0.0768 | no |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt` | 0.8591 | 0.8702 | -0.0111 | 0.0025 | 0.0075 | yes |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | 0.8705 | 0.8671 | +0.0034 | 0.0538 | 0.0807 | no |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt` | 0.8705 | 0.8702 | +0.0004 | 0.8046 | 0.8046 | no |
| `stride-55map-2026-08-25::g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt` | 0.8671 | 0.8702 | -0.0031 | 0.1056 | 0.1267 | no |
