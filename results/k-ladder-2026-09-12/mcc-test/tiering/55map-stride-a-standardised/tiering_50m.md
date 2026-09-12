# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-55map-stride-a-standardised-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 8541 evaluation tiles
- **Metric**: micro-average F1 @ 50 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (6 significant) -> **4 tiers**
- **Tie set (Tier 1)**: `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-standardised-gt`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g384-ov128-55map-n10-oracle-p0.15-k7-standardised-gt` | verified-PV | 1 | 0.842 | 0.842 | -0.000 | 0.696 | 1 |
| 2 | `g384-ov128-55map-n5-oracle-p0.15-k4-standardised-gt` | verified-PV | 1 | 0.838 | 0.838 | +0.000 | 0.691 | 2 |
| 3 | `g384-ov128-55map-n3-oracle-p0.20-k2-standardised-gt` | verified-PV | 1 | 0.833 | 0.833 | -0.000 | 0.702 | 3 |
| 4 | `g384-ov128-55map-n1-oracle-p0.20-k1-standardised-gt` | verified-PV | 1 | 0.823 | 0.823 | +0.000 | 0.701 | 4 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (3 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-standardised-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-standardised-gt` | 0.7010 | 0.7022 | -0.0012 | 0.6391 | 0.6391 | no |
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-standardised-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-standardised-gt` | 0.7010 | 0.6911 | +0.0099 | 0.0087 | 0.0261 | yes |
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-standardised-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-standardised-gt` | 0.7010 | 0.6958 | +0.0052 | 0.1653 | 0.1984 | no |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-standardised-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-standardised-gt` | 0.7022 | 0.6911 | +0.0111 | 0.0011 | 0.0066 | yes |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-standardised-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-standardised-gt` | 0.7022 | 0.6958 | +0.0064 | 0.0636 | 0.0954 | no |
| `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-standardised-gt` | `stride-55map-2026-08-25::g384-ov128-55map-n10-oracle-p0.15-k7-standardised-gt` | 0.6911 | 0.6958 | -0.0047 | 0.0150 | 0.0300 | yes |
