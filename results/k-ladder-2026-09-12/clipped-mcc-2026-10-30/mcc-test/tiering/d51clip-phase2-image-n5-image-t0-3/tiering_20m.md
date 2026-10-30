# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-d51clip-phase2-image-n5-image-t0-3-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `unknown` and rendered at commit `unknown`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (0 significant) -> **1 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-image-t0.3-n10-opmax-d51clip`, `pv-diag-384::pv-min-image-t0.3-n3-opmax-d51clip`, `pv-diag-384::pv-min-image-t0.3-n5-opmax-d51clip`, `pv-diag-384::pv-min-image-t0.3-n1-opmax-d51clip`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-image-t0.3-n10-opmax-d51clip` | verified-PV | 1 | 0.782 | 0.782 | -0.000 | 0.838 | 1 |
| 2 | `pv-min-image-t0.3-n3-opmax-d51clip` | verified-PV | 1 | 0.777 | 0.777 | -0.000 | 0.818 | 1 |
| 3 | `pv-min-image-t0.3-n5-opmax-d51clip` | verified-PV | 1 | 0.777 | 0.777 | +0.000 | 0.842 | 1 |
| 4 | `pv-min-image-t0.3-n1-opmax-d51clip` | verified-PV | 1 | 0.768 | 0.768 | -0.000 | 0.844 | 1 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-image-t0.3-n1-opmax-d51clip` | 0.8443 | 1 | 1 | 0.7680 |
| 2 | `pv-min-image-t0.3-n5-opmax-d51clip` | 0.8416 | 1 | 1 | 0.7767 |
| 3 | `pv-min-image-t0.3-n10-opmax-d51clip` | 0.8377 | 1 | 1 | 0.7819 |
| 4 | `pv-min-image-t0.3-n3-opmax-d51clip` | 0.8178 | 1 | 1 | 0.7774 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-image-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n3-opmax-d51clip` | 0.8443 | 0.8178 | +0.0265 | 0.2034 | 0.4068 | no |
| `pv-diag-384::pv-min-image-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n5-opmax-d51clip` | 0.8443 | 0.8416 | +0.0026 | 0.9954 | 0.9954 | no |
| `pv-diag-384::pv-min-image-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n10-opmax-d51clip` | 0.8443 | 0.8377 | +0.0065 | 0.8208 | 0.9954 | no |
| `pv-diag-384::pv-min-image-t0.3-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n5-opmax-d51clip` | 0.8178 | 0.8416 | -0.0238 | 0.1018 | 0.4068 | no |
| `pv-diag-384::pv-min-image-t0.3-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n10-opmax-d51clip` | 0.8178 | 0.8377 | -0.0199 | 0.1992 | 0.4068 | no |
| `pv-diag-384::pv-min-image-t0.3-n5-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n10-opmax-d51clip` | 0.8416 | 0.8377 | +0.0039 | 0.9411 | 0.9954 | no |
