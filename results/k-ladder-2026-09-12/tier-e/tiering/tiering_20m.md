# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-tier-e-2026-09-12`

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (3 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `grid-2026-08-18::g384-ov192-k5-verified-opmax`, `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe`, `grid-2026-08-18::g384-ov192-k3-verified-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g384-ov192-k5-verified-opmax` | verified-PV | 1 | 0.890 | 0.890 | -0.000 | 0.814 | 1 |
| 2 | `g384-ov192-k10-verified-p0.15-k10-boardframe` | verified-PV | 1 | 0.889 | 0.889 | +0.000 | 0.790 | 1 |
| 3 | `g384-ov192-k3-verified-opmax` | verified-PV | 1 | 0.884 | 0.884 | -0.000 | 0.817 | 1 |
| 4 | `g384-ov192-k1-verified-opmax` | verified-PV | 1 | 0.855 | 0.855 | -0.000 | 0.821 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `grid-2026-08-18::g384-ov192-k1-verified-opmax` | `grid-2026-08-18::g384-ov192-k3-verified-opmax` | 0.8211 | 0.8167 | +0.0044 | 0.8794 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k1-verified-opmax` | `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 0.8211 | 0.8139 | +0.0071 | 0.7765 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k1-verified-opmax` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.8211 | 0.7903 | +0.0308 | 0.0970 | 0.3960 | no |
| `grid-2026-08-18::g384-ov192-k3-verified-opmax` | `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 0.8167 | 0.8139 | +0.0027 | 1.0000 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k3-verified-opmax` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.8167 | 0.7903 | +0.0264 | 0.1386 | 0.3960 | no |
| `grid-2026-08-18::g384-ov192-k5-verified-opmax` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.8139 | 0.7903 | +0.0237 | 0.1980 | 0.3960 | no |
