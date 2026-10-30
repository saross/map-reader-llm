# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-high-text-n5-text-t0-3-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

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
- **Pairs**: 6 (2 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 2; MCC tie set 3 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-high-text-t0.3-n3-opmax` | 0.9056 | 1 | 1 | 0.8783 |
| 2 | `pv-high-text-t0.3-n10-opmax` | 0.8975 | 1 | 1 | 0.8722 |
| 3 | `pv-high-text-t0.3-n5-opmax` | 0.8847 | 1 | 1 | 0.8873 |
| 4 | `pv-high-text-t0.3-n1-opmax` | 0.8541 | 2 | 2 | 0.8314 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-text-t0.3-n1-opmax` | `pv-diag-384::pv-high-text-t0.3-n3-opmax` | 0.8541 | 0.9056 | -0.0516 | 0.0161 | 0.0483 | yes |
| `pv-diag-384::pv-high-text-t0.3-n1-opmax` | `pv-diag-384::pv-high-text-t0.3-n5-opmax` | 0.8541 | 0.8847 | -0.0306 | 0.0733 | 0.1466 | no |
| `pv-diag-384::pv-high-text-t0.3-n1-opmax` | `pv-diag-384::pv-high-text-t0.3-n10-opmax` | 0.8541 | 0.8975 | -0.0435 | 0.0029 | 0.0174 | yes |
| `pv-diag-384::pv-high-text-t0.3-n3-opmax` | `pv-diag-384::pv-high-text-t0.3-n5-opmax` | 0.9056 | 0.8847 | +0.0209 | 0.1728 | 0.2592 | no |
| `pv-diag-384::pv-high-text-t0.3-n3-opmax` | `pv-diag-384::pv-high-text-t0.3-n10-opmax` | 0.9056 | 0.8975 | +0.0081 | 0.8189 | 0.8189 | no |
| `pv-diag-384::pv-high-text-t0.3-n5-opmax` | `pv-diag-384::pv-high-text-t0.3-n10-opmax` | 0.8847 | 0.8975 | -0.0128 | 0.2191 | 0.2629 | no |
