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
- **Tile join**: `geometric-primary` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-primary', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-image-t0.7-n5-opmax-d51clip` | 0.9405 | 1 | 1 | 0.7705 |
| 2 | `pv-min-image-t0.7-n3-opmax-d51clip` | 0.9320 | 1 | 2 | 0.7570 |
| 3 | `pv-min-image-t0.7-n1-opmax-d51clip` | 0.9245 | 1 | 3 | 0.7252 |
| 4 | `pv-min-image-t0.7-n10-opmax-d51clip` | 0.9106 | 1 | 1 | 0.7852 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-image-t0.7-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n3-opmax-d51clip` | 0.9245 | 0.9320 | -0.0075 | 0.7561 | 0.7561 | no |
| `pv-diag-384::pv-min-image-t0.7-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n5-opmax-d51clip` | 0.9245 | 0.9405 | -0.0159 | 0.4216 | 0.6324 | no |
| `pv-diag-384::pv-min-image-t0.7-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n10-opmax-d51clip` | 0.9245 | 0.9106 | +0.0139 | 0.3384 | 0.6324 | no |
| `pv-diag-384::pv-min-image-t0.7-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n5-opmax-d51clip` | 0.9320 | 0.9405 | -0.0084 | 0.7120 | 0.7561 | no |
| `pv-diag-384::pv-min-image-t0.7-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n10-opmax-d51clip` | 0.9320 | 0.9106 | +0.0214 | 0.2002 | 0.6006 | no |
| `pv-diag-384::pv-min-image-t0.7-n5-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.7-n10-opmax-d51clip` | 0.9405 | 0.9106 | +0.0298 | 0.0422 | 0.2532 | no |
