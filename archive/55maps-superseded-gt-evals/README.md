# Superseded 55-map GT-evaluation variants

**Archived**: 2026-06-07 (Session 105). **Why**: superseded by the two-reference
(Track 1 / Track 2) consolidation — see
`planning/55maps-gt-consolidation-spec-2026-06-07.md` and
`docs/methodology/55maps-generalisation-runs.md` § "Two evaluation references".

These were the earlier, ad-hoc 55-map ground-truth evaluation variants. The
Session-105 consolidation settled on **two references only**:

- **Track 1** — the reviewed student GT (`results/rescore-2026-05-31/`), already
  spec-complete (14-buffer + MCC).
- **Track 2** — the canonical adjudicated extended GT
  (`results/55maps-extended-gt-2026-06-07/`), the paper reference. Its 773-mound
  phantom set **already unions** the per-run manual corrections that the
  `human-reviewed-corrected/` and `cleaned-gt-evaluation/` variants represented,
  so those are folded in and retired rather than reported as a third column.

Nothing in `results/run-conditions.json` or the generated manifests references
these paths (verified before the move). Archived, not deleted, per project
policy; git history is preserved (moved with `git mv`).

## Contents

- `55maps-cleaned-gt-evaluation/` — "cleaned GT" evals (buffers [20,30,40,50]).
- `per-run/<run>/mcc/` — per-run MCC-only evals (buffers [50..150]).
- `per-run/55maps-image-generalisation/human-reviewed-corrected/` — the image
  run's at-the-time human-reviewed corrected-F1 (F1-only).
- `condition-scoring-backfill-2026-05-30/55maps-*` — the two 55-map
  condition-scoring backfill evals (the `gs-v2-*` siblings stay live in
  `results/`).
