# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-d51clip-phase2-image-n5-image-t1-0-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (0 significant) -> **1 tiers**
- **Tie set (Tier 1)**: `pv-diag-384::pv-min-image-t1.0-n10-opmax-d51clip`, `pv-diag-384::pv-min-image-t1.0-n5-opmax-d51clip`, `pv-diag-384::pv-min-image-t1.0-n3-opmax-d51clip`, `pv-diag-384::pv-min-image-t1.0-n1-opmax-d51clip`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `pv-min-image-t1.0-n10-opmax-d51clip` | verified-PV | 1 | 0.743 | 0.743 | -0.000 | 0.808 | 1 |
| 2 | `pv-min-image-t1.0-n5-opmax-d51clip` | verified-PV | 1 | 0.738 | 0.738 | +0.000 | 0.802 | 1 |
| 3 | `pv-min-image-t1.0-n3-opmax-d51clip` | verified-PV | 1 | 0.729 | 0.729 | -0.000 | 0.818 | 1 |
| 4 | `pv-min-image-t1.0-n1-opmax-d51clip` | verified-PV | 1 | 0.704 | 0.704 | +0.000 | 0.836 | 1 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `pv-min-image-t1.0-n5-opmax-d51clip` | 0.8888 | 1 | 1 | 0.7384 |
| 2 | `pv-min-image-t1.0-n10-opmax-d51clip` | 0.8847 | 1 | 1 | 0.7428 |
| 3 | `pv-min-image-t1.0-n1-opmax-d51clip` | 0.8739 | 1 | 1 | 0.7044 |
| 4 | `pv-min-image-t1.0-n3-opmax-d51clip` | 0.8686 | 1 | 1 | 0.7288 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `pv-diag-384::pv-min-image-t1.0-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t1.0-n3-opmax-d51clip` | 0.8739 | 0.8686 | +0.0053 | 0.7242 | 0.8690 | no |
| `pv-diag-384::pv-min-image-t1.0-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t1.0-n5-opmax-d51clip` | 0.8739 | 0.8888 | -0.0149 | 0.5572 | 0.8690 | no |
| `pv-diag-384::pv-min-image-t1.0-n1-opmax-d51clip` | `pv-diag-384::pv-min-image-t1.0-n10-opmax-d51clip` | 0.8739 | 0.8847 | -0.0108 | 0.6898 | 0.8690 | no |
| `pv-diag-384::pv-min-image-t1.0-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t1.0-n5-opmax-d51clip` | 0.8686 | 0.8888 | -0.0202 | 0.3977 | 0.8690 | no |
| `pv-diag-384::pv-min-image-t1.0-n3-opmax-d51clip` | `pv-diag-384::pv-min-image-t1.0-n10-opmax-d51clip` | 0.8686 | 0.8847 | -0.0161 | 0.4329 | 0.8690 | no |
| `pv-diag-384::pv-min-image-t1.0-n5-opmax-d51clip` | `pv-diag-384::pv-min-image-t1.0-n10-opmax-d51clip` | 0.8888 | 0.8847 | +0.0041 | 1.0000 | 1.0000 | no |
