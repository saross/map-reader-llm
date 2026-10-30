# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-image-n5-image-t1-0-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (0 significant) -> **1 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-image-t1.0-n10-opmax`, `pv-diag-384::pv-min-image-t1.0-n5-opmax`, `pv-diag-384::pv-min-image-t1.0-n3-opmax`, `pv-diag-384::pv-min-image-t1.0-n1-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-image-t1.0-n10-opmax` | verified-PV | 1 | 0.743 | 0.743 | -0.000 | 0.808 | 1 |
| 2 | `pv-min-image-t1.0-n5-opmax` | verified-PV | 1 | 0.738 | 0.738 | +0.000 | 0.802 | 1 |
| 3 | `pv-min-image-t1.0-n3-opmax` | verified-PV | 1 | 0.729 | 0.729 | -0.000 | 0.818 | 1 |
| 4 | `pv-min-image-t1.0-n1-opmax` | verified-PV | 1 | 0.704 | 0.704 | +0.000 | 0.836 | 1 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-image-t1.0-n1-opmax` | 0.8360 | 1 | 1 | 0.7044 |
| 2 | `pv-min-image-t1.0-n3-opmax` | 0.8178 | 1 | 1 | 0.7288 |
| 3 | `pv-min-image-t1.0-n10-opmax` | 0.8078 | 1 | 1 | 0.7428 |
| 4 | `pv-min-image-t1.0-n5-opmax` | 0.8021 | 1 | 1 | 0.7384 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-image-t1.0-n1-opmax` | `pv-diag-384::pv-min-image-t1.0-n3-opmax` | 0.8360 | 0.8178 | +0.0182 | 0.4359 | 0.6539 | no |
| `pv-diag-384::pv-min-image-t1.0-n1-opmax` | `pv-diag-384::pv-min-image-t1.0-n5-opmax` | 0.8360 | 0.8021 | +0.0339 | 0.1526 | 0.6072 | no |
| `pv-diag-384::pv-min-image-t1.0-n1-opmax` | `pv-diag-384::pv-min-image-t1.0-n10-opmax` | 0.8360 | 0.8078 | +0.0282 | 0.2024 | 0.6072 | no |
| `pv-diag-384::pv-min-image-t1.0-n3-opmax` | `pv-diag-384::pv-min-image-t1.0-n5-opmax` | 0.8178 | 0.8021 | +0.0157 | 0.4314 | 0.6539 | no |
| `pv-diag-384::pv-min-image-t1.0-n3-opmax` | `pv-diag-384::pv-min-image-t1.0-n10-opmax` | 0.8178 | 0.8078 | +0.0100 | 0.6323 | 0.7588 | no |
| `pv-diag-384::pv-min-image-t1.0-n5-opmax` | `pv-diag-384::pv-min-image-t1.0-n10-opmax` | 0.8021 | 0.8078 | -0.0057 | 0.7823 | 0.7823 | no |
