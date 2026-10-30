# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-high-text-n5-text-t0-7-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (4 significant) -> **3 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-high-text-t0.7-n10-opmax`, `pv-diag-384::pv-high-text-t0.7-n5-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-high-text-t0.7-n10-opmax` | verified-PV | 1 | 0.874 | 0.874 | -0.000 | 0.764 | 1 |
| 2 | `pv-high-text-t0.7-n5-opmax` | verified-PV | 1 | 0.863 | 0.863 | -0.000 | 0.768 | 1 |
| 3 | `pv-high-text-t0.7-n3-opmax` | verified-PV | 1 | 0.849 | 0.849 | -0.000 | 0.798 | 2 |
| 4 | `pv-high-text-t0.7-n1-opmax` | verified-PV | 1 | 0.801 | 0.801 | -0.000 | 0.774 | 3 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)
- **Tile join**: `geometric-primary` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-primary', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-high-text-t0.7-n3-opmax` | 0.9237 | 1 | 2 | 0.8492 |
| 2 | `pv-high-text-t0.7-n10-opmax` | 0.9024 | 1 | 1 | 0.8744 |
| 3 | `pv-high-text-t0.7-n5-opmax` | 0.8978 | 1 | 1 | 0.8634 |
| 4 | `pv-high-text-t0.7-n1-opmax` | 0.8748 | 1 | 3 | 0.8009 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-text-t0.7-n1-opmax` | `pv-diag-384::pv-high-text-t0.7-n3-opmax` | 0.8748 | 0.9237 | -0.0488 | 0.0244 | 0.1464 | no |
| `pv-diag-384::pv-high-text-t0.7-n1-opmax` | `pv-diag-384::pv-high-text-t0.7-n5-opmax` | 0.8748 | 0.8978 | -0.0230 | 0.3775 | 0.4699 | no |
| `pv-diag-384::pv-high-text-t0.7-n1-opmax` | `pv-diag-384::pv-high-text-t0.7-n10-opmax` | 0.8748 | 0.9024 | -0.0276 | 0.2978 | 0.4699 | no |
| `pv-diag-384::pv-high-text-t0.7-n3-opmax` | `pv-diag-384::pv-high-text-t0.7-n5-opmax` | 0.9237 | 0.8978 | +0.0258 | 0.0997 | 0.2991 | no |
| `pv-diag-384::pv-high-text-t0.7-n3-opmax` | `pv-diag-384::pv-high-text-t0.7-n10-opmax` | 0.9237 | 0.9024 | +0.0212 | 0.3916 | 0.4699 | no |
| `pv-diag-384::pv-high-text-t0.7-n5-opmax` | `pv-diag-384::pv-high-text-t0.7-n10-opmax` | 0.8978 | 0.9024 | -0.0046 | 0.6443 | 0.6443 | no |
