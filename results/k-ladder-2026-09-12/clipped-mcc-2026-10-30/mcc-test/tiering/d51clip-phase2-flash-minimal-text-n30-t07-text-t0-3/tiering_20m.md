# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-d51clip-phase2-flash-minimal-text-n30-t07-text-t0-3-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `unknown` and rendered at commit `unknown`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

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
- **Pairs**: 6 (0 significant)

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-text-t0.3-n3-opmax-d51clip` | 0.8040 | 1 | 1 | 0.8708 |
| 2 | `pv-min-text-t0.3-n1-opmax-d51clip` | 0.7986 | 1 | 1 | 0.8555 |
| 3 | `pv-min-text-t0.3-n10-opmax-d51clip` | 0.7910 | 1 | 1 | 0.8730 |
| 4 | `pv-min-text-t0.3-n5-opmax-d51clip` | 0.7735 | 1 | 1 | 0.8778 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-text-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n3-opmax-d51clip` | 0.7986 | 0.8040 | -0.0054 | 0.7546 | 0.7631 | no |
| `pv-diag-384::pv-min-text-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n5-opmax-d51clip` | 0.7986 | 0.7735 | +0.0251 | 0.2368 | 0.6044 | no |
| `pv-diag-384::pv-min-text-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n10-opmax-d51clip` | 0.7986 | 0.7910 | +0.0076 | 0.7631 | 0.7631 | no |
| `pv-diag-384::pv-min-text-t0.3-n3-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n5-opmax-d51clip` | 0.8040 | 0.7735 | +0.0305 | 0.0181 | 0.1086 | no |
| `pv-diag-384::pv-min-text-t0.3-n3-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n10-opmax-d51clip` | 0.8040 | 0.7910 | +0.0130 | 0.4465 | 0.6697 | no |
| `pv-diag-384::pv-min-text-t0.3-n5-opmax-d51clip` | `pv-diag-384::pv-min-text-t0.3-n10-opmax-d51clip` | 0.7735 | 0.7910 | -0.0175 | 0.3022 | 0.6044 | no |
