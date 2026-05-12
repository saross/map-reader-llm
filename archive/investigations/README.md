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
