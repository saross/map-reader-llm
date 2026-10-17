# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-tier-e-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `64382beea` and rendered at commit `64382beea`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

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

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `g384-ov192-k1-verified-opmax` | 0.8211 | 1 | 2 | 0.8680 |
| 2 | `g384-ov192-k3-verified-opmax` | 0.8167 | 1 | 1 | 0.8979 |
| 3 | `g384-ov192-k5-verified-opmax` | 0.8139 | 1 | 1 | 0.9046 |
| 4 | `g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.7973 | 1 | 1 | 0.8942 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `grid-2026-08-18::g384-ov192-k1-verified-opmax` | `grid-2026-08-18::g384-ov192-k3-verified-opmax` | 0.8211 | 0.8167 | +0.0044 | 0.8794 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k1-verified-opmax` | `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 0.8211 | 0.8139 | +0.0071 | 0.7765 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k1-verified-opmax` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.8211 | 0.7973 | +0.0238 | 0.2619 | 0.8094 | no |
| `grid-2026-08-18::g384-ov192-k3-verified-opmax` | `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 0.8167 | 0.8139 | +0.0027 | 1.0000 | 1.0000 | no |
| `grid-2026-08-18::g384-ov192-k3-verified-opmax` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.8167 | 0.7973 | +0.0194 | 0.3568 | 0.8094 | no |
| `grid-2026-08-18::g384-ov192-k5-verified-opmax` | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | 0.8139 | 0.7973 | +0.0167 | 0.4047 | 0.8094 | no |
