# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-55map-stride-b-r2-2026-09-12`

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
- **Pairs**: 6 (0 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `stride-55map-2026-08-25::g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | 0.7092 | 0.7128 | -0.0035 | 0.2843 | 0.5592 | no |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | 0.7092 | 0.7098 | -0.0006 | 0.8774 | 0.8774 | no |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt` | 0.7092 | 0.7123 | -0.0031 | 0.3728 | 0.5592 | no |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | 0.7128 | 0.7098 | +0.0030 | 0.0687 | 0.4122 | no |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt` | 0.7128 | 0.7123 | +0.0004 | 0.8179 | 0.8774 | no |
| `stride-55map-2026-08-25::g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt` | 0.7098 | 0.7123 | -0.0025 | 0.1465 | 0.4395 | no |
