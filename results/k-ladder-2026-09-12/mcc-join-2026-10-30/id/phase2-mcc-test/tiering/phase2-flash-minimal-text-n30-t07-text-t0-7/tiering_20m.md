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

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-text-t0.7-n5-opmax` | 0.7957 | 1 | 1 | 0.8739 |
| 2 | `pv-min-text-t0.7-n3-opmax` | 0.7910 | 1 | 1 | 0.8725 |
| 3 | `pv-min-text-t0.7-n1-opmax` | 0.7881 | 1 | 1 | 0.8575 |
| 4 | `pv-min-text-t0.7-n10-opmax` | 0.7768 | 1 | 1 | 0.8726 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-text-t0.7-n1-opmax` | `pv-diag-384::pv-min-text-t0.7-n3-opmax` | 0.7881 | 0.7910 | -0.0029 | 0.8125 | 0.8125 | no |
| `pv-diag-384::pv-min-text-t0.7-n1-opmax` | `pv-diag-384::pv-min-text-t0.7-n5-opmax` | 0.7881 | 0.7957 | -0.0077 | 0.6544 | 0.8125 | no |
| `pv-diag-384::pv-min-text-t0.7-n1-opmax` | `pv-diag-384::pv-min-text-t0.7-n10-opmax` | 0.7881 | 0.7768 | +0.0113 | 0.6012 | 0.8125 | no |
| `pv-diag-384::pv-min-text-t0.7-n3-opmax` | `pv-diag-384::pv-min-text-t0.7-n5-opmax` | 0.7910 | 0.7957 | -0.0048 | 0.8077 | 0.8125 | no |
| `pv-diag-384::pv-min-text-t0.7-n3-opmax` | `pv-diag-384::pv-min-text-t0.7-n10-opmax` | 0.7910 | 0.7768 | +0.0142 | 0.4555 | 0.8125 | no |
| `pv-diag-384::pv-min-text-t0.7-n5-opmax` | `pv-diag-384::pv-min-text-t0.7-n10-opmax` | 0.7957 | 0.7768 | +0.0189 | 0.2116 | 0.8125 | no |
