# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-high-image-n5-image-t0-7-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (3 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-high-image-t0.7-n5-opmax`, `pv-diag-384::pv-high-image-t0.7-n10-opmax`, `pv-diag-384::pv-high-image-t0.7-n3-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-high-image-t0.7-n5-opmax` | verified-PV | 1 | 0.787 | 0.787 | +0.000 | 0.836 | 1 |
| 2 | `pv-high-image-t0.7-n10-opmax` | verified-PV | 1 | 0.776 | 0.777 | +0.000 | 0.798 | 1 |
| 3 | `pv-high-image-t0.7-n3-opmax` | verified-PV | 1 | 0.767 | 0.767 | -0.000 | 0.844 | 1 |
| 4 | `pv-high-image-t0.7-n1-opmax` | verified-PV | 1 | 0.691 | 0.691 | -0.000 | 0.844 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-image-t0.7-n1-opmax` | `pv-diag-384::pv-high-image-t0.7-n3-opmax` | 0.8435 | 0.8435 | +0.0000 | 1.0000 | 1.0000 | no |
| `pv-diag-384::pv-high-image-t0.7-n1-opmax` | `pv-diag-384::pv-high-image-t0.7-n5-opmax` | 0.8435 | 0.8359 | +0.0076 | 0.6859 | 0.8746 | no |
| `pv-diag-384::pv-high-image-t0.7-n1-opmax` | `pv-diag-384::pv-high-image-t0.7-n10-opmax` | 0.8435 | 0.7980 | +0.0455 | 0.0781 | 0.1562 | no |
| `pv-diag-384::pv-high-image-t0.7-n3-opmax` | `pv-diag-384::pv-high-image-t0.7-n5-opmax` | 0.8435 | 0.8359 | +0.0076 | 0.7288 | 0.8746 | no |
| `pv-diag-384::pv-high-image-t0.7-n3-opmax` | `pv-diag-384::pv-high-image-t0.7-n10-opmax` | 0.8435 | 0.7980 | +0.0455 | 0.0110 | 0.0660 | no |
| `pv-diag-384::pv-high-image-t0.7-n5-opmax` | `pv-diag-384::pv-high-image-t0.7-n10-opmax` | 0.8359 | 0.7980 | +0.0378 | 0.0347 | 0.1041 | no |
