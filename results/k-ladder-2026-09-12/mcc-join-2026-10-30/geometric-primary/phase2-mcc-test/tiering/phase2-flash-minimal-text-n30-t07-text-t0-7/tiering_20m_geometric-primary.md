# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-minimal-text-n30-t07-text-t0-7-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (0 significant) -> **1 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-text-t0.7-n5-opmax`, `pv-diag-384::pv-min-text-t0.7-n10-opmax`, `pv-diag-384::pv-min-text-t0.7-n3-opmax`, `pv-diag-384::pv-min-text-t0.7-n1-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-text-t0.7-n5-opmax` | verified-PV | 1 | 0.874 | 0.874 | +0.000 | 0.796 | 1 |
| 2 | `pv-min-text-t0.7-n10-opmax` | verified-PV | 1 | 0.873 | 0.873 | -0.000 | 0.777 | 1 |
| 3 | `pv-min-text-t0.7-n3-opmax` | verified-PV | 1 | 0.873 | 0.872 | -0.000 | 0.791 | 1 |
| 4 | `pv-min-text-t0.7-n1-opmax` | verified-PV | 1 | 0.858 | 0.857 | -0.000 | 0.788 | 1 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)
- **Tile join**: `geometric-primary` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-primary', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-text-t0.7-n3-opmax` | 0.9149 | 1 | 1 | 0.8725 |
| 2 | `pv-min-text-t0.7-n1-opmax` | 0.9064 | 1 | 1 | 0.8575 |
| 3 | `pv-min-text-t0.7-n5-opmax` | 0.9064 | 1 | 1 | 0.8739 |
| 4 | `pv-min-text-t0.7-n10-opmax` | 0.8936 | 1 | 1 | 0.8726 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-text-t0.7-n1-opmax` | `pv-diag-384::pv-min-text-t0.7-n3-opmax` | 0.9064 | 0.9149 | -0.0086 | 0.4060 | 0.7813 | no |
| `pv-diag-384::pv-min-text-t0.7-n1-opmax` | `pv-diag-384::pv-min-text-t0.7-n5-opmax` | 0.9064 | 0.9064 | -0.0000 | 1.0000 | 1.0000 | no |
| `pv-diag-384::pv-min-text-t0.7-n1-opmax` | `pv-diag-384::pv-min-text-t0.7-n10-opmax` | 0.9064 | 0.8936 | +0.0128 | 0.5081 | 0.7813 | no |
| `pv-diag-384::pv-min-text-t0.7-n3-opmax` | `pv-diag-384::pv-min-text-t0.7-n5-opmax` | 0.9149 | 0.9064 | +0.0085 | 0.6774 | 0.8129 | no |
| `pv-diag-384::pv-min-text-t0.7-n3-opmax` | `pv-diag-384::pv-min-text-t0.7-n10-opmax` | 0.9149 | 0.8936 | +0.0213 | 0.3069 | 0.7813 | no |
| `pv-diag-384::pv-min-text-t0.7-n5-opmax` | `pv-diag-384::pv-min-text-t0.7-n10-opmax` | 0.9064 | 0.8936 | +0.0128 | 0.5209 | 0.7813 | no |
