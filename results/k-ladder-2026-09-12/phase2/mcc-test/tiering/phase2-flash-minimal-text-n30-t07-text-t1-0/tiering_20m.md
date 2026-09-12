# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-minimal-text-n30-t07-text-t1-0-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (3 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-text-t1.0-n10-opmax`, `pv-diag-384::pv-min-text-t1.0-n5-opmax`, `pv-diag-384::pv-min-text-t1.0-n3-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-text-t1.0-n10-opmax` | verified-PV | 1 | 0.878 | 0.878 | +0.000 | 0.788 | 1 |
| 2 | `pv-min-text-t1.0-n5-opmax` | verified-PV | 1 | 0.871 | 0.871 | +0.000 | 0.780 | 1 |
| 3 | `pv-min-text-t1.0-n3-opmax` | verified-PV | 1 | 0.865 | 0.865 | -0.000 | 0.804 | 1 |
| 4 | `pv-min-text-t1.0-n1-opmax` | verified-PV | 1 | 0.824 | 0.824 | +0.000 | 0.809 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-text-t1.0-n1-opmax` | `pv-diag-384::pv-min-text-t1.0-n3-opmax` | 0.8095 | 0.8040 | +0.0055 | 0.7762 | 0.7762 | no |
| `pv-diag-384::pv-min-text-t1.0-n1-opmax` | `pv-diag-384::pv-min-text-t1.0-n5-opmax` | 0.8095 | 0.7797 | +0.0298 | 0.1170 | 0.5760 | no |
| `pv-diag-384::pv-min-text-t1.0-n1-opmax` | `pv-diag-384::pv-min-text-t1.0-n10-opmax` | 0.8095 | 0.7881 | +0.0214 | 0.2880 | 0.5760 | no |
| `pv-diag-384::pv-min-text-t1.0-n3-opmax` | `pv-diag-384::pv-min-text-t1.0-n5-opmax` | 0.8040 | 0.7797 | +0.0243 | 0.2134 | 0.5760 | no |
| `pv-diag-384::pv-min-text-t1.0-n3-opmax` | `pv-diag-384::pv-min-text-t1.0-n10-opmax` | 0.8040 | 0.7881 | +0.0159 | 0.4385 | 0.6577 | no |
| `pv-diag-384::pv-min-text-t1.0-n5-opmax` | `pv-diag-384::pv-min-text-t1.0-n10-opmax` | 0.7797 | 0.7881 | -0.0084 | 0.6924 | 0.7762 | no |
