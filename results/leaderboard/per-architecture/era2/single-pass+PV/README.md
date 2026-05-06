# Per-stratum leaderboard — Era 2 single-pass+PV

**Generated**: 2026-05-06 (Session 79 redesign)
**Era**: 2 (487 tiles, 384 px, full Era-2 evaluation bounds)
**Architecture**: single-pass+PV — One detection pass + one verifier pass. The detection GeoJSON is post-thresholded by the verifier's binary cut.
**Conditions**: 8
**F1 tiers** (q=0.05): 1
**MCC tiers** (q=0.05): 2

## Files in this directory

**Tier tables (q=0.05 base)**:

- `leaderboard_tiers_20m.md` — F1 at 20 m
- `leaderboard_tiers_30m.md` — F1 at 30 m
- `leaderboard_tiers_40m.md` — F1 at 40 m
- `leaderboard_tiers_50m.md` — F1 at 50 m
- `leaderboard_tiers_100m.md` — F1 at 100 m
- `leaderboard_tiers_mcc_20m.md` — MCC at 20 m
- `leaderboard_tiers_mcc_30m.md` — MCC at 30 m
- `leaderboard_tiers_mcc_40m.md` — MCC at 40 m
- `leaderboard_tiers_mcc_50m.md` — MCC at 50 m
- `leaderboard_tiers_mcc_100m.md` — MCC at 100 m

**Tier tables (q=0.01 sensitivity)**:

- `leaderboard_tiers_q01_20m.md` — F1 at q=0.01
- `leaderboard_tiers_q01_30m.md` — F1 at q=0.01
- `leaderboard_tiers_q01_40m.md` — F1 at q=0.01
- `leaderboard_tiers_q01_50m.md` — F1 at q=0.01
- `leaderboard_tiers_q01_100m.md` — F1 at q=0.01
- `leaderboard_tiers_mcc_q01_20m.md` — MCC at q=0.01
- `leaderboard_tiers_mcc_q01_30m.md` — MCC at q=0.01
- `leaderboard_tiers_mcc_q01_40m.md` — MCC at q=0.01
- `leaderboard_tiers_mcc_q01_50m.md` — MCC at q=0.01
- `leaderboard_tiers_mcc_q01_100m.md` — MCC at q=0.01

**Tier-stability tables**:

- `tier_stability.md` — Spearman rho across buffers (F1)
- `tier_stability_mcc.md` — Spearman rho across buffers (MCC)

**Sweep + JSON sidecars**:

- `leaderboard_all_evaluations.json` — full threshold x buffer evaluation sweep
- `leaderboard_tiers_20m.json` — primary-buffer F1 tier JSON (includes pairwise tests)
- `leaderboard_tiers_mcc_20m.json` — primary-buffer MCC tier JSON

## Top-3 by F1 (Tier 1, 20 m)

| # | Condition | F1 [95% CI] | MCC |
|--:|:---|:---|---:|
| 1 | `pv-checklist-image` | 0.531 [0.473, 0.580] | +0.388 |
| 2 | `pv-checklist-text` | 0.521 [0.463, 0.569] | +0.315 |
| 3 | `pv-brief-image` | 0.520 [0.463, 0.569] | +0.341 |

## Top-3 by MCC (Tier 1)

| # | Condition | MCC | F1@20 m |
|--:|:---|---:|---:|
| 1 | `pv-cascade-adversarial-checklist` | +0.432 | 0.504 |
| 2 | `pv-adversarial-text` | +0.432 | 0.471 |
| 3 | `pv-adversarial-image` | +0.416 | 0.494 |

## See also

- Top-level `../README.md` for cross-stratum methodology
- `../headlines.md` for top-3 leaders across all strata
- `../cross-architecture-era*_*m_*.md` for flat cross-arch comparisons within Era
- `../cross-architecture-paired-era*.md` for paired tests (does PV help on this proposer?)
- `../mc-precision-flags.md` for permutation-precision-limited tests

