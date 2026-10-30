# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-high-image-n5-image-t0-7-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (3 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-high-image-t0.7-n5-opmax`, `pv-diag-384::pv-high-image-t0.7-n10-opmax`, `pv-diag-384::pv-high-image-t0.7-n3-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-high-image-t0.7-n5-opmax` | verified-PV | 1 | 0.787 | 0.787 | +0.000 | 0.836 | 1 |
| 2 | `pv-high-image-t0.7-n10-opmax` | verified-PV | 1 | 0.776 | 0.777 | +0.000 | 0.798 | 1 |
| 3 | `pv-high-image-t0.7-n3-opmax` | verified-PV | 1 | 0.767 | 0.767 | -0.000 | 0.844 | 1 |
| 4 | `pv-high-image-t0.7-n1-opmax` | verified-PV | 1 | 0.691 | 0.691 | -0.000 | 0.844 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)
- **Tile join**: `geometric-primary` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-primary', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-high-image-t0.7-n5-opmax` | 0.9405 | 1 | 1 | 0.7868 |
| 2 | `pv-high-image-t0.7-n3-opmax` | 0.9320 | 1 | 1 | 0.7666 |
| 3 | `pv-high-image-t0.7-n1-opmax` | 0.9170 | 1 | 2 | 0.6909 |
| 4 | `pv-high-image-t0.7-n10-opmax` | 0.9154 | 1 | 1 | 0.7765 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-image-t0.7-n1-opmax` | `pv-diag-384::pv-high-image-t0.7-n3-opmax` | 0.9170 | 0.9320 | -0.0150 | 0.5009 | 0.7513 | no |
| `pv-diag-384::pv-high-image-t0.7-n1-opmax` | `pv-diag-384::pv-high-image-t0.7-n5-opmax` | 0.9170 | 0.9405 | -0.0235 | 0.2356 | 0.7068 | no |
| `pv-diag-384::pv-high-image-t0.7-n1-opmax` | `pv-diag-384::pv-high-image-t0.7-n10-opmax` | 0.9170 | 0.9154 | +0.0015 | 0.8549 | 0.8549 | no |
| `pv-diag-384::pv-high-image-t0.7-n3-opmax` | `pv-diag-384::pv-high-image-t0.7-n5-opmax` | 0.9320 | 0.9405 | -0.0085 | 0.7571 | 0.8549 | no |
| `pv-diag-384::pv-high-image-t0.7-n3-opmax` | `pv-diag-384::pv-high-image-t0.7-n10-opmax` | 0.9320 | 0.9154 | +0.0166 | 0.4460 | 0.7513 | no |
| `pv-diag-384::pv-high-image-t0.7-n5-opmax` | `pv-diag-384::pv-high-image-t0.7-n10-opmax` | 0.9405 | 0.9154 | +0.0250 | 0.1417 | 0.7068 | no |
