# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-d51clip-phase2-flash-minimal-text-n30-t07-text-t0-3-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (0 significant) -> **1 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-text-t0.3-n5-opmax-d51clip`, `pv-diag-384::pv-min-text-t0.3-n10-opmax-d51clip`, `pv-diag-384::pv-min-text-t0.3-n3-opmax-d51clip`, `pv-diag-384::pv-min-text-t0.3-n1-opmax-d51clip`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-text-t0.3-n5-opmax-d51clip` | verified-PV | 1 | 0.878 | 0.878 | +0.000 | 0.773 | 1 |
| 2 | `pv-min-text-t0.3-n10-opmax-d51clip` | verified-PV | 1 | 0.873 | 0.873 | -0.000 | 0.791 | 1 |
| 3 | `pv-min-text-t0.3-n3-opmax-d51clip` | verified-PV | 1 | 0.871 | 0.871 | +0.000 | 0.804 | 1 |
| 4 | `pv-min-text-t0.3-n1-opmax-d51clip` | verified-PV | 1 | 0.856 | 0.855 | -0.000 | 0.799 | 1 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (1 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 2; MCC tie set 3 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-text-t0.3-n3-opmax-d51clip` | 0.8853 | 1 | 1 | 0.8708 |
| 2 | `pv-min-text-t0.3-n1-opmax-d51clip` | 0.8728 | 1 | 1 | 0.8555 |
| 3 | `pv-min-text-t0.3-n10-opmax-d51clip` | 0.8728 | 1 | 1 | 0.8730 |
| 4 | `pv-min-text-t0.3-n5-opmax-d51clip` | 0.8410 | 2 | 1 | 0.8778 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-text-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n3-opmax-d51clip` | 0.8728 | 0.8853 | -0.0125 | 0.3857 | 0.4628 | no |
| `pv-diag-384::pv-min-text-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n5-opmax-d51clip` | 0.8728 | 0.8410 | +0.0318 | 0.1017 | 0.2034 | no |
| `pv-diag-384::pv-min-text-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n10-opmax-d51clip` | 0.8728 | 0.8728 | +0.0000 | 1.0000 | 1.0000 | no |
| `pv-diag-384::pv-min-text-t0.3-n3-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n5-opmax-d51clip` | 0.8853 | 0.8410 | +0.0443 | 0.0018 | 0.0108 | yes |
| `pv-diag-384::pv-min-text-t0.3-n3-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n10-opmax-d51clip` | 0.8853 | 0.8728 | +0.0125 | 0.3501 | 0.4628 | no |
| `pv-diag-384::pv-min-text-t0.3-n5-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n10-opmax-d51clip` | 0.8410 | 0.8728 | -0.0318 | 0.0543 | 0.1629 | no |
