# Fault-window evidence (preserved 2026-10-16)

Small files the S163 and S164 records cite that existed only in sapphire
scratch directories written during the memory-fault window (2026-10-08 to
2026-10-09): `~/scratch/d57-4-rescore-2026-10-09/`,
`~/scratch/q4-repaired-readers-2026-10-09/`, and `~/scratch/q4-tools/`.
Copied byte for byte before any clean-up of those directories (PI ruling
D65 (8)); the fault-window re-checks (PRs #49 and #53) verified every
claim-bearing output they bear on.

- `census-old/`: the D57 (4) census outputs (`census_cells.csv`,
  `census_summary.json`, `compare.csv`) that "census-verified" in
  `reports/s164-agent-records/fault-window-rechecks.md` rests on.
- `phase3-out-diffs/`: the D57 (4) Phase 3 diffs.
- `q4/`: the D55 Q4 re-verification comparisons; the 62 MB `q4/before/` is
  kept on sapphire as `~/scratch/archived-evidence/q4-before-2026-10-09.tgz`.
- `q4-tools/`: the Q4 drivers (not otherwise in the repository).
- `phase3-new-uncommitted.patch`: the nine uncommitted Phase 3 NEW outputs
  (the W1-14 values), as a diff against the worktree's commit `e1e8f444a`.

These are evidence of what was computed, not current results; values
computed in the fault window are superseded by the regenerations and
re-checks named above.
