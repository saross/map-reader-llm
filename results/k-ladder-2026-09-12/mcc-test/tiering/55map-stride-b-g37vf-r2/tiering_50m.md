# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-55map-stride-b-g37vf-r2-2026-09-12`

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

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `stride-55map-2026-08-25::g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n3-verified37-oracle-p0.96-k3-r2-gt` | 0.7471 | 0.7376 | +0.0095 | 0.0000 | 0.0000 | yes |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-verified37-oracle-p0.96-k9-r2-gt` | 0.7471 | 0.7359 | +0.0112 | 0.0000 | 0.0000 | yes |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-verified37-oracle-p0.96-k3-r2-gt` | `stride-55map-2026-08-25::g384-ov192-55map-n10-verified37-oracle-p0.96-k9-r2-gt` | 0.7376 | 0.7359 | +0.0017 | 0.2644 | 0.2644 | no |
