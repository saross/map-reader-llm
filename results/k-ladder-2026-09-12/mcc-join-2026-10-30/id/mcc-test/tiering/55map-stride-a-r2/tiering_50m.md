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
- **Pairs**: 6 (3 significant)

- **MCC tiers**: 2; MCC tie set 3 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | 0.7018 | 1 | 3 | 0.8321 |
| 2 | `g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | 0.7006 | 1 | 4 | 0.8227 |
| 3 | `g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | 0.6954 | 1 | 1 | 0.8419 |
| 4 | `g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | 0.6907 | 2 | 2 | 0.8383 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | 0.7006 | 0.7018 | -0.0012 | 0.6391 | 0.6391 | no |
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | 0.7006 | 0.6907 | +0.0099 | 0.0087 | 0.0261 | yes |
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | 0.7006 | 0.6954 | +0.0052 | 0.1653 | 0.1984 | no |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | 0.7018 | 0.6907 | +0.0111 | 0.0011 | 0.0066 | yes |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | 0.7018 | 0.6954 | +0.0064 | 0.0636 | 0.0954 | no |
| `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | 0.6907 | 0.6954 | -0.0047 | 0.0150 | 0.0300 | yes |
