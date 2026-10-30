# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-phase2-flash-high-image-n5-image-t0-3-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (3 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-high-image-t0.3-n10-opmax`, `pv-diag-384::pv-high-image-t0.3-n5-opmax`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-high-image-t0.3-n10-opmax` | verified-PV | 1 | 0.770 | 0.770 | -0.000 | 0.829 | 1 |
| 2 | `pv-high-image-t0.3-n5-opmax` | verified-PV | 1 | 0.748 | 0.748 | +0.000 | 0.805 | 1 |
| 3 | `pv-high-image-t0.3-n3-opmax` | verified-PV | 1 | 0.722 | 0.721 | -0.000 | 0.824 | 2 |
| 4 | `pv-high-image-t0.3-n1-opmax` | verified-PV | 1 | 0.693 | 0.692 | -0.000 | 0.827 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-high-image-t0.3-n10-opmax` | 0.8294 | 1 | 1 | 0.7705 |
| 2 | `pv-high-image-t0.3-n1-opmax` | 0.8270 | 1 | 2 | 0.6925 |
| 3 | `pv-high-image-t0.3-n3-opmax` | 0.8237 | 1 | 2 | 0.7215 |
| 4 | `pv-high-image-t0.3-n5-opmax` | 0.8049 | 1 | 1 | 0.7475 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-high-image-t0.3-n1-opmax` | `pv-diag-384::pv-high-image-t0.3-n3-opmax` | 0.8270 | 0.8237 | +0.0033 | 0.9886 | 0.9886 | no |
| `pv-diag-384::pv-high-image-t0.3-n1-opmax` | `pv-diag-384::pv-high-image-t0.3-n5-opmax` | 0.8270 | 0.8049 | +0.0221 | 0.3197 | 0.7090 | no |
| `pv-diag-384::pv-high-image-t0.3-n1-opmax` | `pv-diag-384::pv-high-image-t0.3-n10-opmax` | 0.8270 | 0.8294 | -0.0024 | 0.8562 | 0.9886 | no |
| `pv-diag-384::pv-high-image-t0.3-n3-opmax` | `pv-diag-384::pv-high-image-t0.3-n5-opmax` | 0.8237 | 0.8049 | +0.0188 | 0.3545 | 0.7090 | no |
| `pv-diag-384::pv-high-image-t0.3-n3-opmax` | `pv-diag-384::pv-high-image-t0.3-n10-opmax` | 0.8237 | 0.8294 | -0.0057 | 0.6657 | 0.9886 | no |
| `pv-diag-384::pv-high-image-t0.3-n5-opmax` | `pv-diag-384::pv-high-image-t0.3-n10-opmax` | 0.8049 | 0.8294 | -0.0245 | 0.1869 | 0.7090 | no |
