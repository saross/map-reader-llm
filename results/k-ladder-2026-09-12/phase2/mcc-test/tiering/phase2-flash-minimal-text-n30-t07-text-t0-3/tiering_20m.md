# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-minimal-text-n30-t07-text-t0-3-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (0 significant) -> **1 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-text-t0.3-n5-opmax`, `pv-diag-384::pv-min-text-t0.3-n10-opmax`, `pv-diag-384::pv-min-text-t0.3-n3-opmax`, `pv-diag-384::pv-min-text-t0.3-n1-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-text-t0.3-n5-opmax` | verified-PV | 1 | 0.878 | 0.878 | +0.000 | 0.773 | 1 |
| 2 | `pv-min-text-t0.3-n10-opmax` | verified-PV | 1 | 0.873 | 0.873 | -0.000 | 0.791 | 1 |
| 3 | `pv-min-text-t0.3-n3-opmax` | verified-PV | 1 | 0.871 | 0.871 | +0.000 | 0.804 | 1 |
| 4 | `pv-min-text-t0.3-n1-opmax` | verified-PV | 1 | 0.856 | 0.855 | -0.000 | 0.799 | 1 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-text-t0.3-n1-opmax` | `pv-diag-384::pv-min-text-t0.3-n3-opmax` | 0.7986 | 0.8040 | -0.0054 | 0.7546 | 0.7631 | no |
| `pv-diag-384::pv-min-text-t0.3-n1-opmax` | `pv-diag-384::pv-min-text-t0.3-n5-opmax` | 0.7986 | 0.7735 | +0.0251 | 0.2368 | 0.6044 | no |
| `pv-diag-384::pv-min-text-t0.3-n1-opmax` | `pv-diag-384::pv-min-text-t0.3-n10-opmax` | 0.7986 | 0.7910 | +0.0076 | 0.7631 | 0.7631 | no |
| `pv-diag-384::pv-min-text-t0.3-n3-opmax` | `pv-diag-384::pv-min-text-t0.3-n5-opmax` | 0.8040 | 0.7735 | +0.0305 | 0.0181 | 0.1086 | no |
| `pv-diag-384::pv-min-text-t0.3-n3-opmax` | `pv-diag-384::pv-min-text-t0.3-n10-opmax` | 0.8040 | 0.7910 | +0.0130 | 0.4465 | 0.6697 | no |
| `pv-diag-384::pv-min-text-t0.3-n5-opmax` | `pv-diag-384::pv-min-text-t0.3-n10-opmax` | 0.7735 | 0.7910 | -0.0175 | 0.3022 | 0.6044 | no |
