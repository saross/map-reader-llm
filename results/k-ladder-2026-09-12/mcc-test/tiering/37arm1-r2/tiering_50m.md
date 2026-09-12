# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-37arm1-r2-2026-09-12`

- **Cells**: 3 (0 single-pass + 0 consensus + 3 verified-PV), 8541 evaluation tiles
- **Metric**: micro-average F1 @ 50 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 3 (2 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `gemini37-55map-2026-08-29::arm1-n5-oracle-p0.15-k5-r2-gt`, `gemini37-55map-2026-08-29::arm1-n3-oracle-p0.15-k3-r2-gt`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `arm1-n5-oracle-p0.15-k5-r2-gt` | verified-PV | 1 | 0.873 | 0.873 | +0.000 | 0.715 | 1 |
| 2 | `arm1-n3-oracle-p0.15-k3-r2-gt` | verified-PV | 1 | 0.871 | 0.870 | -0.000 | 0.718 | 1 |
| 3 | `arm1-n1-oracle-p0.20-k1-r2-gt` | verified-PV | 1 | 0.841 | 0.841 | -0.000 | 0.725 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 3 (3 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `gemini37-55map-2026-08-29::arm1-n1-oracle-p0.20-k1-r2-gt` | `gemini37-55map-2026-08-29::arm1-n3-oracle-p0.15-k3-r2-gt` | 0.7246 | 0.7179 | +0.0067 | 0.0498 | 0.0498 | yes |
| `gemini37-55map-2026-08-29::arm1-n1-oracle-p0.20-k1-r2-gt` | `gemini37-55map-2026-08-29::arm1-n5-oracle-p0.15-k5-r2-gt` | 0.7246 | 0.7147 | +0.0099 | 0.0056 | 0.0168 | yes |
| `gemini37-55map-2026-08-29::arm1-n3-oracle-p0.15-k3-r2-gt` | `gemini37-55map-2026-08-29::arm1-n5-oracle-p0.15-k5-r2-gt` | 0.7179 | 0.7147 | +0.0032 | 0.0455 | 0.0498 | yes |
