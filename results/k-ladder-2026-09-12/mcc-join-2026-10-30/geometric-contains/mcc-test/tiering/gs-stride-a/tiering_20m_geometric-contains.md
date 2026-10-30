# Era-1 leaderboard — statistical tiering (20 m) — `k-ladder-gs-stride-a-2026-09-12`

> **GENERATED FILE — do not hand-edit.** Rendered from `tiering_20m.json` by `scripts/era1_leaderboard_tiering.py`, computed at commit `463257349` and rendered at commit `463257349`. Per the PI ruling of 2026-09-11 (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope") this projection carries provenance instead of a hand changelog: "is this current?" is answered by `--check <board dir>` and its tier-1 test, and `--render-md <board dir>` re-renders it from the committed JSON without re-running the permutation.

- **Cells**: 4 (0 single-pass + 0 consensus + 4 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 6 (1 significant) -> **2 tiers**
- **Tie set (Tier 1)**: `stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8`, `stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3`, `stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g384-ov128-k10-verified-p0.15-k8` | verified-PV | 1 | 0.900 | 0.900 | -0.000 | 0.808 | 1 |
| 2 | `g384-ov128-ladder-n3-verified-p0.15-k3` | verified-PV | 1 | 0.892 | 0.892 | -0.000 | 0.787 | 1 |
| 3 | `g384-ov128-ladder-n5-verified-p0.15-k4` | verified-PV | 1 | 0.886 | 0.886 | +0.000 | 0.786 | 1 |
| 4 | `g384-ov128-ladder-n1-verified-p0.15-k1` | verified-PV | 1 | 0.867 | 0.867 | +0.000 | 0.795 | 2 |

## Tile-level MCC — the same permutation, a second statistic

- **Test**: tile-swap permutation on tile-level MCC, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05 within this board; swap masks identical to the F1 test's
- **Pairs**: 6 (0 significant)
- **Tile join**: `geometric-contains` — SENSITIVITY reading: the MCC arm books points to tiles under 'geometric-contains', not the published 'id' join (S153 ruling 6). The F1 arm, its tiering and its withheld cells are unchanged. Gates compare each cell's per-tile labels with the scorer's aggregate under the same join; no committed record exists to reproduce.

- **MCC tiers**: 1; MCC tie set 4 cell(s). Reported beside the F1 tiering, which remains the board's tiering (ruling 7).

| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |
|---:|---|---:|---:|---:|---:|
| 1 | `g384-ov128-k10-verified-p0.15-k8` | 0.8936 | 1 | 1 | 0.8999 |
| 2 | `g384-ov128-ladder-n3-verified-p0.15-k3` | 0.8728 | 1 | 1 | 0.8916 |
| 3 | `g384-ov128-ladder-n5-verified-p0.15-k4` | 0.8724 | 1 | 1 | 0.8862 |
| 4 | `g384-ov128-ladder-n1-verified-p0.15-k1` | 0.8722 | 1 | 2 | 0.8665 |

| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |
|---|---|---:|---:|---:|---:|---:|:--:|
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n1-verified-p0.15-k1` | `stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3` | 0.8722 | 0.8728 | -0.0006 | 0.8154 | 0.9053 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n1-verified-p0.15-k1` | `stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4` | 0.8722 | 0.8724 | -0.0002 | 0.8605 | 0.9053 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n1-verified-p0.15-k1` | `stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8` | 0.8722 | 0.8936 | -0.0214 | 0.1230 | 0.2460 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3` | `stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4` | 0.8728 | 0.8724 | +0.0004 | 0.9053 | 0.9053 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3` | `stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8` | 0.8728 | 0.8936 | -0.0208 | 0.0616 | 0.1848 | no |
| `stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4` | `stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8` | 0.8724 | 0.8936 | -0.0212 | 0.0512 | 0.1848 | no |
