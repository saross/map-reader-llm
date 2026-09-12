# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-37arm2-r2-2026-09-12`

- **Cells**: 3 (0 single-pass + 0 consensus + 3 verified-PV), 8541 evaluation tiles
- **Metric**: micro-average F1 @ 50 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 3 (2 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `gemini37-55map-2026-08-29::arm2-n5-oracle-p0.95-k5-r2-gt`, `gemini37-55map-2026-08-29::arm2-n3-oracle-p0.95-k3-r2-gt`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `arm2-n5-oracle-p0.95-k5-r2-gt` | verified-PV | 1 | 0.887 | 0.887 | +0.000 | 0.715 | 1 |
| 2 | `arm2-n3-oracle-p0.95-k3-r2-gt` | verified-PV | 1 | 0.885 | 0.885 | +0.000 | 0.716 | 1 |
| 3 | `arm2-n1-oracle-p0.98-k1-r2-gt` | verified-PV | 1 | 0.861 | 0.861 | +0.000 | 0.742 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 3 (2 significant)

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `gemini37-55map-2026-08-29::arm2-n1-oracle-p0.98-k1-r2-gt` | `gemini37-55map-2026-08-29::arm2-n3-oracle-p0.95-k3-r2-gt` | 0.7422 | 0.7163 | +0.0258 | 0.0000 | 0.0000 | yes |
| `gemini37-55map-2026-08-29::arm2-n1-oracle-p0.98-k1-r2-gt` | `gemini37-55map-2026-08-29::arm2-n5-oracle-p0.95-k5-r2-gt` | 0.7422 | 0.7147 | +0.0275 | 0.0000 | 0.0000 | yes |
| `gemini37-55map-2026-08-29::arm2-n3-oracle-p0.95-k3-r2-gt` | `gemini37-55map-2026-08-29::arm2-n5-oracle-p0.95-k5-r2-gt` | 0.7163 | 0.7147 | +0.0017 | 0.3580 | 0.3580 | no |
