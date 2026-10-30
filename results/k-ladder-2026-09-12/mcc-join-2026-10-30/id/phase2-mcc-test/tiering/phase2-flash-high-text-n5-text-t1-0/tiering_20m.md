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

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-high-text-t1.0-n1-opmax` | 0.8162 | 1 | 3 | 0.7810 |
| 2 | `pv-high-text-t1.0-n3-opmax` | 0.7986 | 1 | 2 | 0.8541 |
| 3 | `pv-high-text-t1.0-n10-opmax` | 0.7910 | 1 | 1 | 0.8804 |
| 4 | `pv-high-text-t1.0-n5-opmax` | 0.7857 | 1 | 1 | 0.8688 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-text-t1.0-n1-opmax` | `pv-diag-384::pv-high-text-t1.0-n3-opmax` | 0.8162 | 0.7986 | +0.0176 | 0.4385 | 0.8065 | no |
| `pv-diag-384::pv-high-text-t1.0-n1-opmax` | `pv-diag-384::pv-high-text-t1.0-n5-opmax` | 0.8162 | 0.7857 | +0.0305 | 0.1856 | 0.8065 | no |
| `pv-diag-384::pv-high-text-t1.0-n1-opmax` | `pv-diag-384::pv-high-text-t1.0-n10-opmax` | 0.8162 | 0.7910 | +0.0252 | 0.2708 | 0.8065 | no |
| `pv-diag-384::pv-high-text-t1.0-n3-opmax` | `pv-diag-384::pv-high-text-t1.0-n5-opmax` | 0.7986 | 0.7857 | +0.0129 | 0.5580 | 0.8065 | no |
| `pv-diag-384::pv-high-text-t1.0-n3-opmax` | `pv-diag-384::pv-high-text-t1.0-n10-opmax` | 0.7986 | 0.7910 | +0.0076 | 0.7432 | 0.8065 | no |
| `pv-diag-384::pv-high-text-t1.0-n5-opmax` | `pv-diag-384::pv-high-text-t1.0-n10-opmax` | 0.7857 | 0.7910 | -0.0053 | 0.8065 | 0.8065 | no |
