# `results/leaderboard/era2/` — superseded leaderboard build

**Build date**: 2026-04-17 with partial markdown rebuilds 2026-04-24
(pre-Phase-C, pre-Session-79 redesign).

**Status**: Superseded by the per-architecture and combined-leaderboard
trees built 2026-04-26 (Session 79 redesign).

## Why this directory is preserved

This bare-era leaderboard predates two major refactors:

1. **Per-architecture stratification** (Session 79, 2026-04-26): the
   leaderboard was redesigned to stratify conditions by (Era × Architecture)
   matrix rather than pooling all conditions together at the Era level. This
   eliminates between-architecture confounds that the bare-era pooled
   leaderboard cannot disentangle.
2. **Phase C verifier-calibration regeneration** (commit `fc7843158b04cbdd`,
   2026-04-25): the verifier-calibration matrix was re-evaluated on canonical
   shared crops, refreshing 14-cell verifier-calibration-matrix evaluations.
   The bare-era leaderboard does not incorporate Phase C updates.

Per project archive-don't-delete policy, this directory is preserved for
historical reference. The data files (`leaderboard_all_evaluations.json`,
`leaderboard_tiers_*.{md,json}`) reflect the 2026-04-17 build state and are
**not the current canonical leaderboard**. The `pv-materialised/`
subdirectory stores Session 78 PV materialisations and is still in use.

## Where to look instead

For current canonical Era 2 leaderboards:

- **Per-architecture leaderboard**: `results/leaderboard/per-architecture/era2/<arch>/`
  with `<arch>` ∈ {`single-pass`, `consensus`, `single-pass+PV`, `pv`} (Era 2
  has all four populated). Files: `leaderboard_tiers_<B>m.{md,json}` for F1 at
  buffer `<B>` ∈ {20, 30, 40, 50, 100} m, plus `leaderboard_tiers_mcc_<B>m.md`.
- **Combined cross-architecture leaderboard**: `results/leaderboard/combined/era2/`
  with files `leaderboard_tiers_f1_<B>m.{md,json}`,
  `leaderboard_tiers_f1_q01_<B>m.{md,json}`, `leaderboard_tiers_mcc.{md,json}`,
  `leaderboard_tiers_mcc_q01.{md,json}`.
- **Headlines**: `results/leaderboard/per-architecture/headlines.md` (top-3 per
  populated stratum at q=0.05).

## See also

- `results/leaderboard/per-architecture/README.md` — full methodology of the
  Session 79 redesign.
- `scripts/run_per_arch_leaderboards.sh` — orchestrator for the per-architecture
  build (≈2-3 hours sapphire wall-clock).
- `scripts/build_combined_leaderboard.sh` — orchestrator for the combined
  build (reuses per-arch caches).
- Wave 3 of Session 80 (Theme 7) — staleness audit that flagged this build.
