# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-tier-e-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (3 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `grid-2026-08-18::g384-ov192-k5-verified-opmax`, `grid-2026-08-18::g384-ov192-k3-verified-opmax`, `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g384-ov192-k5-verified-opmax` | verified-PV | 1 | 0.905 | 0.905 | -0.000 | 0.814 | 1 |
| 2 | `g384-ov192-k3-verified-opmax` | verified-PV | 1 | 0.898 | 0.898 | +0.000 | 0.817 | 1 |
| 3 | `g384-ov192-k10-verified-p0.15-k10-boardframe` | verified-PV | 1 | 0.894 | 0.894 | -0.000 | 0.797 | 1 |
| 4 | `g384-ov192-k1-verified-opmax` | verified-PV | 1 | 0.868 | 0.868 | +0.000 | 0.821 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `g384-ov192-k3-verified-opmax` | 0.9064 | 1 | 1 | 0.8979 |
| 2 | `g384-ov192-k1-verified-opmax` | 0.8935 | 1 | 2 | 0.8680 |
| 3 | `g384-ov192-k5-verified-opmax` | 0.8933 | 1 | 1 | 0.9046 |
| 4 | `g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.8813 | 1 | 1 | 0.8942 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `grid-2026-08-18::g384-ov192-k1-verified-opmax` | `grid-2026-08-18::g384-ov192-k3-verified-opmax` | 0.8935 | 0.9064 | -0.0129 | 0.3799 | 0.6490 | no |
| `grid-2026-08-18::g384-ov192-k1-verified-opmax` | `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 0.8935 | 0.8933 | +0.0003 | 1.0000 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k1-verified-opmax` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.8935 | 0.8813 | +0.0122 | 0.5408 | 0.6490 | no |
| `grid-2026-08-18::g384-ov192-k3-verified-opmax` | `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 0.9064 | 0.8933 | +0.0131 | 0.2984 | 0.6490 | no |
| `grid-2026-08-18::g384-ov192-k3-verified-opmax` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.9064 | 0.8813 | +0.0250 | 0.1017 | 0.6102 | no |
| `grid-2026-08-18::g384-ov192-k5-verified-opmax` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.8933 | 0.8813 | +0.0119 | 0.5277 | 0.6490 | no |
