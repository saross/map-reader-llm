# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-high-image-n5-image-t1-0-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (5 significant) -> **3 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-high-image-t1.0-n10-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-high-image-t1.0-n10-opmax` | verified-PV | 1 | 0.763 | 0.763 | -0.000 | 0.800 | 1 |
| 2 | `pv-high-image-t1.0-n5-opmax` | verified-PV | 1 | 0.734 | 0.734 | +0.000 | 0.823 | 2 |
| 3 | `pv-high-image-t1.0-n3-opmax` | verified-PV | 1 | 0.725 | 0.725 | +0.000 | 0.829 | 2 |
| 4 | `pv-high-image-t1.0-n1-opmax` | verified-PV | 1 | 0.612 | 0.612 | -0.000 | 0.864 | 3 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (1 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-image-t1.0-n1-opmax` | `pv-diag-384::pv-high-image-t1.0-n3-opmax` | 0.8640 | 0.8294 | +0.0346 | 0.1084 | 0.1725 | no |
| `pv-diag-384::pv-high-image-t1.0-n1-opmax` | `pv-diag-384::pv-high-image-t1.0-n5-opmax` | 0.8640 | 0.8230 | +0.0410 | 0.0945 | 0.1725 | no |
| `pv-diag-384::pv-high-image-t1.0-n1-opmax` | `pv-diag-384::pv-high-image-t1.0-n10-opmax` | 0.8640 | 0.8002 | +0.0637 | 0.0070 | 0.0420 | yes |
| `pv-diag-384::pv-high-image-t1.0-n3-opmax` | `pv-diag-384::pv-high-image-t1.0-n5-opmax` | 0.8294 | 0.8230 | +0.0064 | 0.8054 | 0.8054 | no |
| `pv-diag-384::pv-high-image-t1.0-n3-opmax` | `pv-diag-384::pv-high-image-t1.0-n10-opmax` | 0.8294 | 0.8002 | +0.0292 | 0.1150 | 0.1725 | no |
| `pv-diag-384::pv-high-image-t1.0-n5-opmax` | `pv-diag-384::pv-high-image-t1.0-n10-opmax` | 0.8230 | 0.8002 | +0.0228 | 0.2086 | 0.2503 | no |
