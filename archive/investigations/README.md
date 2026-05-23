# Archived investigations

This directory holds **completed** diagnostic / analytical investigations — typically read-only reports produced by Claude Code subagents or sessions that analysed project state, surfaced findings, and made recommendations without executing changes themselves.

## Convention

- `planning/` is reserved for *active* plans. Once an investigation's recommendations have been acted on (or explicitly retired), the investigation moves here.
- Each investigation keeps its original filename; the file's own header preserves authorship and date provenance.
- No date-prefix on filenames — the file's metadata header is authoritative for provenance.
- Investigations belong here regardless of which campaign or topic they covered — this is a type-categorised archive, not a campaign-categorised one. Group by campaign if needed via `archive/<campaign>-*/` siblings instead.

## Contents

| File | Date | Topic | Outcome |
|---|---|---|---|
| `tier23-sapphire-state-investigation.md` | 2026-05-04/06 | Tier-2/3 cells in the Phase 3a recovery campaign — what sapphire actually did during the off-network overnight | Predicted (correctly) that all 11 cells were zbook-recoverable via crop-regen; recommended path executed in Sessions 86–87 with $1.89 cumulative cost. Parallel-run data later preserved at `archive/phase3a-recovery-sapphire-parallel-run/` with comparative analysis at `results/sapphire-zbook-cleanup-comparison.md` (Obs 325). |
| `three-skipped-cells-investigation.md` | 2026-05-04 | Three Tier-1/2/3 cells skipped during the Phase 3a recovery overnight (e47-flash-high-text-1of5, 55maps-gen-verified-v2, proposer-verifier-384-adversarial-text-v1-prompt) — why they were skipped and how to recover them on zbook | Diagnosed "missing crops" as a path-argument bug + gitignored crop directories never reaching sapphire; all three cells recoverable on zbook for ~$0.09 total. Recommended actions executed in Sessions 86–88, closing all three cells (Obs 324). |
| `session-86-tier-regression-investigation.md` | 2026-05-05 | Per-architecture tier regression: why the post-recovery rebuild thinned era1/consensus, era2/consensus, and era2/pv leaderboards relative to commit `b4c28d5b` | Root cause was a wrong-driver script choice (`run_per_arch_leaderboards.sh` with default `--top-n 20` vs `build_per_arch_redesign.sh` with `--top-n 0`), not a code change. Recommended `--top-n 0` rebuild on existing cache; fixes landed at commits `baa271bf` (runner default) and `ef3ec4fe` (runbook). Referenced from Obs 324. |
