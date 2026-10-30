# Era-1 leaderboard — statistical tiering (50 m) — `k-ladder-mcc-37arm2-r2-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_50m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

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
- **Pairs**: 3 (3 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 3; MCC tie set 1 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `arm2-n1-oracle-p0.98-k1-r2-gt` | 0.9017 | 1 | 2 | 0.8610 |
| 2 | `arm2-n3-oracle-p0.95-k3-r2-gt` | 0.8729 | 2 | 1 | 0.8848 |
| 3 | `arm2-n5-oracle-p0.95-k5-r2-gt` | 0.8677 | 3 | 1 | 0.8871 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `gemini37-55map-2026-08-29::arm2-n1-oracle-p0.98-k1-r2-gt` | `gemini37-55map-2026-08-29::arm2-n3-oracle-p0.95-k3-r2-gt` | 0.9017 | 0.8729 | +0.0288 | 0.0000 | 0.0000 | yes |
| `gemini37-55map-2026-08-29::arm2-n1-oracle-p0.98-k1-r2-gt` | `gemini37-55map-2026-08-29::arm2-n5-oracle-p0.95-k5-r2-gt` | 0.9017 | 0.8677 | +0.0339 | 0.0000 | 0.0000 | yes |
| `gemini37-55map-2026-08-29::arm2-n3-oracle-p0.95-k3-r2-gt` | `gemini37-55map-2026-08-29::arm2-n5-oracle-p0.95-k5-r2-gt` | 0.8729 | 0.8677 | +0.0052 | 0.0094 | 0.0094 | yes |
