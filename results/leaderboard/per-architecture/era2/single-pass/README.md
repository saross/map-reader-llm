# Per-stratum leaderboard — Era 2 single-pass

**Generated**: 2026-04-26 (Session 79 redesign)
**Era**: 2 (487 tiles, 384 px, full Era-2 evaluation bounds)
**Architecture**: single-pass — One stochastic detection pass per tile (K=1). No consensus, no verifier.
**Conditions**: 6
**F1 tiers** (q=0.05): 4
**MCC tiers** (q=0.05): 4

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
| 1 | `h11-pvd-pro-medium-text-baseline` | 0.763 [0.713, 0.806] | +0.752 |

## Top-3 by MCC (Tier 1)

| # | Condition | MCC | F1@20 m |
|--:|:---|---:|---:|
| 1 | `h11-pvd-pro-medium-text-baseline` | +0.752 | 0.763 |
| 2 | `h11-pvd-pro-medium-image-baseline` | +0.734 | 0.606 |

## See also

- Top-level `../README.md` for cross-stratum methodology
- `../headlines.md` for top-3 leaders across all strata
- `../cross-architecture-era*_*m_*.md` for flat cross-arch comparisons within Era
- `../cross-architecture-paired-era*.md` for paired tests (does PV help on this proposer?)
- `../mc-precision-flags.md` for permutation-precision-limited tests

