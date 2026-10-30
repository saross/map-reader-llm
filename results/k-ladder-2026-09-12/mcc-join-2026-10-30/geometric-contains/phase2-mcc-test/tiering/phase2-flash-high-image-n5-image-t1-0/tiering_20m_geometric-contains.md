# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-high-image-n5-image-t1-0-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (5 significant) -> **3 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-high-image-t1.0-n10-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-high-image-t1.0-n10-opmax` | verified-PV | 1 | 0.763 | 0.763 | -0.000 | 0.800 | 1 |
| 2 | `pv-high-image-t1.0-n5-opmax` | verified-PV | 1 | 0.734 | 0.734 | +0.000 | 0.823 | 2 |
| 3 | `pv-high-image-t1.0-n3-opmax` | verified-PV | 1 | 0.725 | 0.725 | +0.000 | 0.829 | 2 |
| 4 | `pv-high-image-t1.0-n1-opmax` | verified-PV | 1 | 0.612 | 0.612 | -0.000 | 0.864 | 3 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-high-image-t1.0-n1-opmax` | 0.8875 | 1 | 3 | 0.6119 |
| 2 | `pv-high-image-t1.0-n3-opmax` | 0.8806 | 1 | 2 | 0.7245 |
| 3 | `pv-high-image-t1.0-n5-opmax` | 0.8805 | 1 | 2 | 0.7337 |
| 4 | `pv-high-image-t1.0-n10-opmax` | 0.8640 | 1 | 1 | 0.7633 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-image-t1.0-n1-opmax` | `pv-diag-384::pv-high-image-t1.0-n3-opmax` | 0.8875 | 0.8806 | +0.0069 | 0.6234 | 0.8222 | no |
| `pv-diag-384::pv-high-image-t1.0-n1-opmax` | `pv-diag-384::pv-high-image-t1.0-n5-opmax` | 0.8875 | 0.8805 | +0.0070 | 0.6852 | 0.8222 | no |
| `pv-diag-384::pv-high-image-t1.0-n1-opmax` | `pv-diag-384::pv-high-image-t1.0-n10-opmax` | 0.8875 | 0.8640 | +0.0236 | 0.2265 | 0.6214 | no |
| `pv-diag-384::pv-high-image-t1.0-n3-opmax` | `pv-diag-384::pv-high-image-t1.0-n5-opmax` | 0.8806 | 0.8805 | +0.0001 | 1.0000 | 1.0000 | no |
| `pv-diag-384::pv-high-image-t1.0-n3-opmax` | `pv-diag-384::pv-high-image-t1.0-n10-opmax` | 0.8806 | 0.8640 | +0.0167 | 0.3107 | 0.6214 | no |
| `pv-diag-384::pv-high-image-t1.0-n5-opmax` | `pv-diag-384::pv-high-image-t1.0-n10-opmax` | 0.8805 | 0.8640 | +0.0165 | 0.3032 | 0.6214 | no |
