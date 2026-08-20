# Per-stratum leaderboard — Era 3 consensus

**Generated**: 2026-05-06 (Session 79 redesign)
**Era**: 3 (327 tiles, 384 px, h10 test bounds (subset of Era 2))
**Architecture**: consensus — K stochastic passes + greedy-voting consensus at threshold vote_t. No verifier.
**Conditions**: 14
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
| 1 | `h8v2-scale-4` | 0.733 [0.699, 0.760] | +0.772 |
| 2 | `h12v2-r1-hn-heavy` | 0.731 [0.700, 0.753] | +0.725 |
| 3 | `h8v2-scale-8` | 0.730 [0.703, 0.757] | +0.739 |

## Top-3 by MCC (Tier 1)

| # | Condition | MCC | F1@20 m |
|--:|:---|---:|---:|
| 1 | `h8v2-scale-4` | +0.772 | 0.733 |
| 2 | `h8v2-scale-8` | +0.739 | 0.730 |
| 3 | `h12v2-r3-hp-heavy` | +0.733 | 0.701 |

## See also

- Top-level `../README.md` for cross-stratum methodology
- `../headlines.md` for top-3 leaders across all strata
- `../cross-architecture-era*_*m_*.md` for flat cross-arch comparisons within Era
- `../cross-architecture-paired-era*.md` for paired tests (does PV help on this proposer?)
- `../mc-precision-flags.md` for permutation-precision-limited tests

