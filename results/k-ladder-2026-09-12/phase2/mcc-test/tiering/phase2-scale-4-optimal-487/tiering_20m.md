# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-scale-4-optimal-487-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (5 significant) -> **3 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-scale4-optimal-n10-opmax`, `pv-diag-384::pv-scale4-optimal-n5-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-scale4-optimal-n10-opmax` | verified-PV | 1 | 0.768 | 0.768 | +0.000 | 0.815 | 1 |
| 2 | `pv-scale4-optimal-n5-opmax` | verified-PV | 1 | 0.763 | 0.764 | +0.000 | 0.831 | 1 |
| 3 | `pv-scale4-optimal-n3-opmax` | verified-PV | 1 | 0.730 | 0.730 | +0.000 | 0.844 | 2 |
| 4 | `pv-scale4-optimal-n1-opmax` | verified-PV | 1 | 0.638 | 0.638 | +0.000 | 0.873 | 3 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-scale4-optimal-n1-opmax` | `pv-diag-384::pv-scale4-optimal-n3-opmax` | 0.8726 | 0.8443 | +0.0283 | 0.1800 | 0.2700 | no |
| `pv-diag-384::pv-scale4-optimal-n1-opmax` | `pv-diag-384::pv-scale4-optimal-n5-opmax` | 0.8726 | 0.8306 | +0.0419 | 0.0618 | 0.1854 | no |
| `pv-diag-384::pv-scale4-optimal-n1-opmax` | `pv-diag-384::pv-scale4-optimal-n10-opmax` | 0.8726 | 0.8154 | +0.0572 | 0.0127 | 0.0762 | no |
| `pv-diag-384::pv-scale4-optimal-n3-opmax` | `pv-diag-384::pv-scale4-optimal-n5-opmax` | 0.8443 | 0.8306 | +0.0136 | 0.4157 | 0.4157 | no |
| `pv-diag-384::pv-scale4-optimal-n3-opmax` | `pv-diag-384::pv-scale4-optimal-n10-opmax` | 0.8443 | 0.8154 | +0.0289 | 0.1405 | 0.2700 | no |
| `pv-diag-384::pv-scale4-optimal-n5-opmax` | `pv-diag-384::pv-scale4-optimal-n10-opmax` | 0.8306 | 0.8154 | +0.0153 | 0.2970 | 0.3564 | no |
