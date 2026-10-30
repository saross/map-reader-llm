# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-image-n5-image-t0-7-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (4 significant) -> **3 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-image-t0.7-n10-opmax`, `pv-diag-384::pv-min-image-t0.7-n5-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-image-t0.7-n10-opmax` | verified-PV | 1 | 0.788 | 0.788 | -0.000 | 0.822 | 1 |
| 2 | `pv-min-image-t0.7-n5-opmax` | verified-PV | 1 | 0.773 | 0.773 | -0.000 | 0.838 | 1 |
| 3 | `pv-min-image-t0.7-n3-opmax` | verified-PV | 1 | 0.760 | 0.760 | +0.000 | 0.838 | 2 |
| 4 | `pv-min-image-t0.7-n1-opmax` | verified-PV | 1 | 0.725 | 0.725 | +0.000 | 0.844 | 3 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-image-t0.7-n1-opmax` | 0.8437 | 1 | 3 | 0.7252 |
| 2 | `pv-min-image-t0.7-n5-opmax` | 0.8383 | 1 | 1 | 0.7734 |
| 3 | `pv-min-image-t0.7-n3-opmax` | 0.8377 | 1 | 2 | 0.7599 |
| 4 | `pv-min-image-t0.7-n10-opmax` | 0.8223 | 1 | 1 | 0.7881 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-image-t0.7-n1-opmax` | `pv-diag-384::pv-min-image-t0.7-n3-opmax` | 0.8437 | 0.8377 | +0.0060 | 0.8145 | 1.0000 | no |
| `pv-diag-384::pv-min-image-t0.7-n1-opmax` | `pv-diag-384::pv-min-image-t0.7-n5-opmax` | 0.8437 | 0.8383 | +0.0054 | 0.8375 | 1.0000 | no |
| `pv-diag-384::pv-min-image-t0.7-n1-opmax` | `pv-diag-384::pv-min-image-t0.7-n10-opmax` | 0.8437 | 0.8223 | +0.0214 | 0.3670 | 0.9768 | no |
| `pv-diag-384::pv-min-image-t0.7-n3-opmax` | `pv-diag-384::pv-min-image-t0.7-n5-opmax` | 0.8377 | 0.8383 | -0.0006 | 1.0000 | 1.0000 | no |
| `pv-diag-384::pv-min-image-t0.7-n3-opmax` | `pv-diag-384::pv-min-image-t0.7-n10-opmax` | 0.8377 | 0.8223 | +0.0154 | 0.4884 | 0.9768 | no |
| `pv-diag-384::pv-min-image-t0.7-n5-opmax` | `pv-diag-384::pv-min-image-t0.7-n10-opmax` | 0.8383 | 0.8223 | +0.0160 | 0.3420 | 0.9768 | no |
