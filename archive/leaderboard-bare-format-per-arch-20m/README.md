# Superseded bare-format per-architecture 20 m boards

Archived 2026-08-20 during the Phase 6 remediation of defect **D35** (audit
finding F11, `reports/session-137-audit-report-2026-08-20.md`).

## What these files are

The seven `results/leaderboard/per-architecture/<era>/<architecture>/leaderboard_tiers_20m.md`
boards as they stood at commit `8ff376919`, in the *bare* format written by
`scripts/build_tiered_leaderboard.py`.

## Why they were replaced

Two generators wrote the same seven paths and the last one to run won:

- `scripts/enrich_per_arch_markdown.py` — the richer, later, deliberate writer
  (provenance header naming the source tier JSON, git commit, and evaluation
  bounds; proposer / config / verifier / threshold metadata columns). It wrote
  all 35 per-architecture F1 boards at 2026-05-06T00:25:57 UTC and left its
  machine-readable `leaderboard_rows_20m.json` siblings behind as evidence.
- `scripts/build_tiered_leaderboard.py` — the bare writer. A later pass at
  2026-05-06T09:33:34 UTC overwrote only the seven 20 m boards, so the primary
  board of every stratum was left in the wrong format while its four siblings
  (30 / 40 / 50 / 100 m) kept the owner's format.

Phase 6 assigned ownership of `results/leaderboard/per-architecture/**`
`leaderboard_tiers_<buffer>m.md` to `enrich_per_arch_markdown.py`, added a
refusal guard to the bare writer, and re-emitted the seven boards in the
owner's format.

## What is preserved here that the active boards no longer show

The bare format carries an **MCC** column populated from the condition-level
`tile_mcc` field; the enriched format populates its MCC column from the
per-buffer `evaluations[<buffer>]["mcc"]` field, which these tier JSONs no
longer carry, so the re-emitted boards print `—` there. No value is lost from
the repository — the same numbers remain in each stratum's committed
`leaderboard_tiers_20m.json` (`tiers[].conditions[].tile_mcc`) and in the
sibling `leaderboard_tiers_mcc_20m.md` boards — but these copies keep the
superseded rendering browsable in the working tree, per the project's
"archive, never delete" policy.

Every F1, confidence interval, precision, recall, tier assignment, and
condition ordering in these files is identical to the re-emitted enriched
boards; the migration was verified per file with
`scripts/compare_leaderboard_board_content.py`.
