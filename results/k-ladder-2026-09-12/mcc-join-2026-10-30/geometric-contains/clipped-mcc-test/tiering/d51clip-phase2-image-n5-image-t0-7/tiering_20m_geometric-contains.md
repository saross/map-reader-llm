# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-d51clip-phase2-image-n5-image-t0-7-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (4 significant) -> **3 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-image-t0.7-n10-opmax-d51clip`, `pv-diag-384::pv-min-image-t0.7-n5-opmax-d51clip`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-image-t0.7-n10-opmax-d51clip` | verified-PV | 1 | 0.785 | 0.785 | +0.000 | 0.819 | 1 |
| 2 | `pv-min-image-t0.7-n5-opmax-d51clip` | verified-PV | 1 | 0.770 | 0.770 | -0.000 | 0.835 | 1 |
| 3 | `pv-min-image-t0.7-n3-opmax-d51clip` | verified-PV | 1 | 0.757 | 0.757 | +0.000 | 0.834 | 2 |
| 4 | `pv-min-image-t0.7-n1-opmax-d51clip` | verified-PV | 1 | 0.725 | 0.725 | +0.000 | 0.844 | 3 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-image-t0.7-n5-opmax-d51clip` | 0.8931 | 1 | 1 | 0.7705 |
| 2 | `pv-min-image-t0.7-n1-opmax-d51clip` | 0.8908 | 1 | 3 | 0.7252 |
| 3 | `pv-min-image-t0.7-n3-opmax-d51clip` | 0.8893 | 1 | 2 | 0.7570 |
| 4 | `pv-min-image-t0.7-n10-opmax-d51clip` | 0.8768 | 1 | 1 | 0.7852 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-image-t0.7-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n3-opmax-d51clip` | 0.8908 | 0.8893 | +0.0015 | 0.7973 | 1.0000 | no |
| `pv-diag-384::pv-min-image-t0.7-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n5-opmax-d51clip` | 0.8908 | 0.8931 | -0.0022 | 1.0000 | 1.0000 | no |
| `pv-diag-384::pv-min-image-t0.7-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n10-opmax-d51clip` | 0.8908 | 0.8768 | +0.0140 | 0.4163 | 0.9874 | no |
| `pv-diag-384::pv-min-image-t0.7-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n5-opmax-d51clip` | 0.8893 | 0.8931 | -0.0038 | 0.9694 | 1.0000 | no |
| `pv-diag-384::pv-min-image-t0.7-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n10-opmax-d51clip` | 0.8893 | 0.8768 | +0.0125 | 0.4937 | 0.9874 | no |
| `pv-diag-384::pv-min-image-t0.7-n5-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n10-opmax-d51clip` | 0.8931 | 0.8768 | +0.0163 | 0.2940 | 0.9874 | no |
