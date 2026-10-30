# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-mcc-d51clip-tier-e-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (3 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `grid-2026-08-18::g384-ov192-k5-verified-opmax-d51clip`, `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe-d51clip`, `grid-2026-08-18::g384-ov192-k3-verified-opmax-d51clip`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g384-ov192-k5-verified-opmax-d51clip` | verified-PV | 1 | 0.897 | 0.897 | -0.000 | 0.806 | 1 |
| 2 | `g384-ov192-k10-verified-p0.15-k10-boardframe-d51clip` | verified-PV | 1 | 0.894 | 0.894 | -0.000 | 0.797 | 1 |
| 3 | `g384-ov192-k3-verified-opmax-d51clip` | verified-PV | 1 | 0.890 | 0.890 | -0.000 | 0.809 | 1 |
| 4 | `g384-ov192-k1-verified-opmax-d51clip` | verified-PV | 1 | 0.860 | 0.860 | -0.000 | 0.813 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `g384-ov192-k1-verified-opmax-d51clip` | 0.8133 | 1 | 2 | 0.8604 |
| 2 | `g384-ov192-k3-verified-opmax-d51clip` | 0.8089 | 1 | 1 | 0.8902 |
| 3 | `g384-ov192-k5-verified-opmax-d51clip` | 0.8063 | 1 | 1 | 0.8968 |
| 4 | `g384-ov192-k10-verified-p0.15-k10-boardframe-d51clip` | 0.7973 | 1 | 1 | 0.8942 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `grid-2026-08-18::g384-ov192-k1-verified-opmax-d51clip` | `grid-2026-08-18::g384-ov192-k3-verified-opmax-d51clip` | 0.8133 | 0.8089 | +0.0044 | 0.8794 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k1-verified-opmax-d51clip` | `grid-2026-08-18::g384-ov192-k5-verified-opmax-d51clip` | 0.8133 | 0.8063 | +0.0071 | 0.7765 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k1-verified-opmax-d51clip` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe-d51clip` | 0.8133 | 0.7973 | +0.0161 | 0.4476 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k3-verified-opmax-d51clip` | `grid-2026-08-18::g384-ov192-k5-verified-opmax-d51clip` | 0.8089 | 0.8063 | +0.0026 | 1.0000 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k3-verified-opmax-d51clip` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe-d51clip` | 0.8089 | 0.7973 | +0.0116 | 0.5990 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k5-verified-opmax-d51clip` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe-d51clip` | 0.8063 | 0.7973 | +0.0090 | 0.6316 | 1.0000 | no |
