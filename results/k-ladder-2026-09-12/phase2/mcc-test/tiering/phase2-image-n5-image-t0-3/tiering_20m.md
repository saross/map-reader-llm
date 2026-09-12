# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-image-n5-image-t0-3-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (0 significant) -> **1 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-image-t0.3-n10-opmax`, `pv-diag-384::pv-min-image-t0.3-n3-opmax`, `pv-diag-384::pv-min-image-t0.3-n5-opmax`, `pv-diag-384::pv-min-image-t0.3-n1-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-image-t0.3-n10-opmax` | verified-PV | 1 | 0.782 | 0.782 | -0.000 | 0.838 | 1 |
| 2 | `pv-min-image-t0.3-n3-opmax` | verified-PV | 1 | 0.777 | 0.777 | -0.000 | 0.818 | 1 |
| 3 | `pv-min-image-t0.3-n5-opmax` | verified-PV | 1 | 0.777 | 0.777 | +0.000 | 0.842 | 1 |
| 4 | `pv-min-image-t0.3-n1-opmax` | verified-PV | 1 | 0.768 | 0.768 | -0.000 | 0.844 | 1 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-image-t0.3-n1-opmax` | `pv-diag-384::pv-min-image-t0.3-n3-opmax` | 0.8443 | 0.8178 | +0.0265 | 0.2034 | 0.4068 | no |
| `pv-diag-384::pv-min-image-t0.3-n1-opmax` | `pv-diag-384::pv-min-image-t0.3-n5-opmax` | 0.8443 | 0.8416 | +0.0026 | 0.9954 | 0.9954 | no |
| `pv-diag-384::pv-min-image-t0.3-n1-opmax` | `pv-diag-384::pv-min-image-t0.3-n10-opmax` | 0.8443 | 0.8377 | +0.0065 | 0.8208 | 0.9954 | no |
| `pv-diag-384::pv-min-image-t0.3-n3-opmax` | `pv-diag-384::pv-min-image-t0.3-n5-opmax` | 0.8178 | 0.8416 | -0.0238 | 0.1018 | 0.4068 | no |
| `pv-diag-384::pv-min-image-t0.3-n3-opmax` | `pv-diag-384::pv-min-image-t0.3-n10-opmax` | 0.8178 | 0.8377 | -0.0199 | 0.1992 | 0.4068 | no |
| `pv-diag-384::pv-min-image-t0.3-n5-opmax` | `pv-diag-384::pv-min-image-t0.3-n10-opmax` | 0.8416 | 0.8377 | +0.0039 | 0.9411 | 0.9954 | no |
