# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-high-text-n5-text-t0-3-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (3 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-high-text-t0.3-n5-opmax`, `pv-diag-384::pv-high-text-t0.3-n3-opmax`, `pv-diag-384::pv-high-text-t0.3-n10-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-high-text-t0.3-n5-opmax` | verified-PV | 1 | 0.887 | 0.887 | +0.000 | 0.780 | 1 |
| 2 | `pv-high-text-t0.3-n3-opmax` | verified-PV | 1 | 0.878 | 0.878 | +0.000 | 0.805 | 1 |
| 3 | `pv-high-text-t0.3-n10-opmax` | verified-PV | 1 | 0.872 | 0.872 | -0.000 | 0.787 | 1 |
| 4 | `pv-high-text-t0.3-n1-opmax` | verified-PV | 1 | 0.831 | 0.831 | +0.000 | 0.807 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-text-t0.3-n1-opmax` | `pv-diag-384::pv-high-text-t0.3-n3-opmax` | 0.8068 | 0.8053 | +0.0015 | 0.9703 | 0.9703 | no |
| `pv-diag-384::pv-high-text-t0.3-n1-opmax` | `pv-diag-384::pv-high-text-t0.3-n5-opmax` | 0.8068 | 0.7805 | +0.0263 | 0.2588 | 0.5689 | no |
| `pv-diag-384::pv-high-text-t0.3-n1-opmax` | `pv-diag-384::pv-high-text-t0.3-n10-opmax` | 0.8068 | 0.7872 | +0.0196 | 0.3793 | 0.5689 | no |
| `pv-diag-384::pv-high-text-t0.3-n3-opmax` | `pv-diag-384::pv-high-text-t0.3-n5-opmax` | 0.8053 | 0.7805 | +0.0248 | 0.2279 | 0.5689 | no |
| `pv-diag-384::pv-high-text-t0.3-n3-opmax` | `pv-diag-384::pv-high-text-t0.3-n10-opmax` | 0.8053 | 0.7872 | +0.0181 | 0.3717 | 0.5689 | no |
| `pv-diag-384::pv-high-text-t0.3-n5-opmax` | `pv-diag-384::pv-high-text-t0.3-n10-opmax` | 0.7805 | 0.7872 | -0.0067 | 0.7684 | 0.9221 | no |
