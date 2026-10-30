# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-d51clip-phase2-image-n5-image-t0-3-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

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
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-image-t0.3-n10-opmax-d51clip` | 0.9018 | 1 | 1 | 0.7819 |
| 2 | `pv-min-image-t0.3-n1-opmax-d51clip` | 0.8939 | 1 | 1 | 0.7680 |
| 3 | `pv-min-image-t0.3-n5-opmax-d51clip` | 0.8935 | 1 | 1 | 0.7767 |
| 4 | `pv-min-image-t0.3-n3-opmax-d51clip` | 0.8850 | 1 | 1 | 0.7774 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-image-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n3-opmax-d51clip` | 0.8939 | 0.8850 | +0.0088 | 0.5320 | 0.7980 | no |
| `pv-diag-384::pv-min-image-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n5-opmax-d51clip` | 0.8939 | 0.8935 | +0.0003 | 1.0000 | 1.0000 | no |
| `pv-diag-384::pv-min-image-t0.3-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n10-opmax-d51clip` | 0.8939 | 0.9018 | -0.0079 | 0.7336 | 0.8803 | no |
| `pv-diag-384::pv-min-image-t0.3-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n5-opmax-d51clip` | 0.8850 | 0.8935 | -0.0085 | 0.4061 | 0.7980 | no |
| `pv-diag-384::pv-min-image-t0.3-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n10-opmax-d51clip` | 0.8850 | 0.9018 | -0.0167 | 0.1247 | 0.7482 | no |
| `pv-diag-384::pv-min-image-t0.3-n5-opmax-d51clip` | `pv-diag-384::pv-min-image-t0.3-n10-opmax-d51clip` | 0.8935 | 0.9018 | -0.0082 | 0.5032 | 0.7980 | no |
