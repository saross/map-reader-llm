# SUPERSEDED — N=1 baseline matrix, 4-buffer / no-MCC evals

**Status**: superseded 2026-06-02 (Session 96).
**Superseded by**: `results/paper-eval/n1/384px-14buf-mcc/` (the same 18 cells,
re-scored at the 14-buffer standard `5…150 m` **plus** tile-level MCC).

## What this directory is

The original N=1 baseline-matrix evaluation: the 18 single-pass 384 px baseline
pools scored at only **4 buffers (20/30/40/50 m) with MCC switched off**
(`configs/n1-eval-384px-all-buffers.yaml`). It predates two project standards
adopted 2026-05-31 — the 14 uniform buffers (all runs) and the MCC-always
preference — and so could not back valid condition rows (the conditions schema
requires non-null `tp/tn/fp/fn`, which only the MCC pass supplies).

## Why it is kept here (not moved to `archive/`)

This exact path is cited as a **reference artefact** by `protocol-errata.md` **E57**
(the Pro-pool model-of-record / `output_dir` investigation traced run identity from
these evals' `_metadata.input_files.detections`) and by several working docs.
Relocating it would orphan those citations, so it is **marked superseded in place**
rather than moved — consistent with "archive, never delete" (it is neither deleted
nor edited), while keeping the E57 citation valid.

## Use the successor for any current work

- **Manifest conditions**: the 18 `baseline-<slug>` conditions in
  `results/run-conditions.json` point at `384px-14buf-mcc/`, not here.
- **Full context**: `docs/methodology/n1-baseline-matrix.md`.
