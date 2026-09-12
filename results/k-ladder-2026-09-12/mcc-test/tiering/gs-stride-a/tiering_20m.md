# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-gs-stride-a-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (1 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8`, `stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3`, `stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g384-ov128-k10-verified-p0.15-k8` | verified-PV | 1 | 0.890 | 0.891 | +0.000 | 0.797 | 1 |
| 2 | `g384-ov128-ladder-n3-verified-p0.15-k3` | verified-PV | 1 | 0.883 | 0.883 | +0.000 | 0.776 | 1 |
| 3 | `g384-ov128-ladder-n5-verified-p0.15-k4` | verified-PV | 1 | 0.878 | 0.878 | -0.000 | 0.775 | 1 |
| 4 | `g384-ov128-ladder-n1-verified-p0.15-k1` | verified-PV | 1 | 0.861 | 0.861 | +0.000 | 0.783 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n1-verified-p0.15-k1` | `stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3` | 0.7834 | 0.7762 | +0.0072 | 0.6734 | 0.8081 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n1-verified-p0.15-k1` | `stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4` | 0.7834 | 0.7751 | +0.0083 | 0.6164 | 0.8081 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n1-verified-p0.15-k1` | `stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8` | 0.7834 | 0.7969 | -0.0134 | 0.3839 | 0.7678 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3` | `stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4` | 0.7762 | 0.7751 | +0.0011 | 1.0000 | 1.0000 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3` | `stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8` | 0.7762 | 0.7969 | -0.0206 | 0.0624 | 0.1947 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4` | `stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8` | 0.7751 | 0.7969 | -0.0217 | 0.0649 | 0.1947 | no |
