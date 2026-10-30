# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-high-text-n5-text-t1-0-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (4 significant) -> **3 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-high-text-t1.0-n10-opmax`, `pv-diag-384::pv-high-text-t1.0-n5-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-high-text-t1.0-n10-opmax` | verified-PV | 1 | 0.880 | 0.880 | -0.000 | 0.791 | 1 |
| 2 | `pv-high-text-t1.0-n5-opmax` | verified-PV | 1 | 0.869 | 0.869 | -0.000 | 0.786 | 1 |
| 3 | `pv-high-text-t1.0-n3-opmax` | verified-PV | 1 | 0.854 | 0.854 | +0.000 | 0.799 | 2 |
| 4 | `pv-high-text-t1.0-n1-opmax` | verified-PV | 1 | 0.781 | 0.781 | +0.000 | 0.816 | 3 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)
- **Tile join**: `geometric-primary` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-primary', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-high-text-t1.0-n3-opmax` | 0.9405 | 1 | 2 | 0.8541 |
| 2 | `pv-high-text-t1.0-n10-opmax` | 0.9237 | 1 | 1 | 0.8804 |
| 3 | `pv-high-text-t1.0-n5-opmax` | 0.9195 | 1 | 1 | 0.8688 |
| 4 | `pv-high-text-t1.0-n1-opmax` | 0.9073 | 1 | 3 | 0.7810 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-text-t1.0-n1-opmax` | `pv-diag-384::pv-high-text-t1.0-n3-opmax` | 0.9073 | 0.9405 | -0.0332 | 0.1104 | 0.6624 | no |
| `pv-diag-384::pv-high-text-t1.0-n1-opmax` | `pv-diag-384::pv-high-text-t1.0-n5-opmax` | 0.9073 | 0.9195 | -0.0123 | 0.6181 | 0.7417 | no |
| `pv-diag-384::pv-high-text-t1.0-n1-opmax` | `pv-diag-384::pv-high-text-t1.0-n10-opmax` | 0.9073 | 0.9237 | -0.0164 | 0.4744 | 0.7116 | no |
| `pv-diag-384::pv-high-text-t1.0-n3-opmax` | `pv-diag-384::pv-high-text-t1.0-n5-opmax` | 0.9405 | 0.9195 | +0.0209 | 0.2875 | 0.6650 | no |
| `pv-diag-384::pv-high-text-t1.0-n3-opmax` | `pv-diag-384::pv-high-text-t1.0-n10-opmax` | 0.9405 | 0.9237 | +0.0168 | 0.3325 | 0.6650 | no |
| `pv-diag-384::pv-high-text-t1.0-n5-opmax` | `pv-diag-384::pv-high-text-t1.0-n10-opmax` | 0.9195 | 0.9237 | -0.0041 | 0.9185 | 0.9185 | no |
