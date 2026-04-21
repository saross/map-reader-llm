# Results Documentation Audit — Corrected Draft

**Draft Date**: 2026-04-22
**Status**: DRAFT — awaiting verifier pass before committing
**Supersedes**: the 2026-04-19 audit at `results/documentation-audit/`
(committed in `8747d726`), which contained hallucinated cost figures,
conflated run names, and mis-attributed Observation numbers. See
`planning/doc-audit-rerun-plan.md` for the driver document and the
two-agent workflow.

## Why this draft exists

The prior audit applied a sound structural framework but wrote several
numeric claims from inference rather than file reads. Specifically:

- `55maps-text-min-generalisation` was stated to cost **$165.74** with a
  90.2 % cache-hit rate; the `cost_manifest.json` actually records
  **$60.79** with a 0.0 % cache-hit rate.
- `55maps-text-high-generalisation` was written up as a single run
  costing **$359.53**; there are in fact two distinct runs — the 2026-04-10
  retrospective run at `outputs/55maps-generalisation/` (no cost manifest;
  ~$75 estimate in the retrospective post-run report) and the 2026-04-19
  re-run at `outputs/55maps-text-high-generalisation/` (cost manifest
  records $69.60).
- All four 55-map runs were attributed to "Obs 255"; the correct
  working-notes anchors span Obs 256–273.

The draft in this folder re-runs the audit with every numeric claim
cited to its source file and key path. A separate verifier agent (fresh
context) checks each cited claim against the actual source file before
the draft is promoted into the permanent `results/documentation-audit/`
directory.

## Files in this draft

1. **`audit-summary.md`** — executive summary of coverage patterns and
   gold-standard versus gap-heavy runs. Every numeric cell in the
   summary cites its source file.
2. **`results-audit-2026-04-21.md`** — full run-by-run table. All
   numeric claims (F1, precision, recall, cost, cache-hit, Observation
   numbers) cite the file and JSON key or Markdown line where the value
   can be verified.
3. **`priority-backfill.md`** — updated gap analysis and backfill
   priority list, acknowledging the analytical work landed between the
   prior audit and this one (multi-buffer corrected F1, Dawid-Skene v1
   + v2 cross-tabs, subtype classification, buffer-band lift, verifier
   calibration, CI-metadata registry, errata E54).

## Scope notes (unchanged from prior audit)

- **Active runs**: anything under `outputs/` or `results/` that is NOT
  inside `outputs/archive/`, `archive/`, or
  `archive/v2-verifier-contamination/`.
- **Quarantine**: `archive/v2-verifier-contamination/` holds 100 files
  moved on 2026-04-21 because the v2 verifier prompt was derived by
  analysing false positives on the 4-map gold-standard set (calibration-
  on-test). These are NOT audited as active runs. Policy document:
  `docs/methodology/v2-verifier-contamination-policy.md`.
- **Working-notes observations**: the audit anchors observation cites to
  the `## Observation N:` heading line in
  `docs/notes/reflections/working-notes.md`. Post-matrix range (Obs 256–
  273) covers every 55-map generalisation finding plus the 2026-04-20/21
  human-review day analyses.

## Relationship to the prior audit

- **Structure preserved**: the two-tier / era split, the deliverable
  checklist, and the tiered backfill framing all carry over. The prior
  audit's narrative arc (Era 1 rigorous but under-documented → Era 2
  publication-ready) is correct.
- **Numbers replaced**: every cost, F1, and Observation-number citation
  has been re-derived from the committed files in the repository.
- **Additions**: coverage for the 2026-04-20 and 2026-04-21 analyses
  (Obs 262–273, corrected-F1 multi-buffer, D-S v1/v2 cross-tabs,
  subtype classification, buffer-band lift, verifier calibration,
  human-review multi-buffer CSV, paper-tables consolidation). The
  2026-04-18 audit predated all of this work.

## How a reviewer should read this draft

1. Skim `audit-summary.md` for the overall coverage picture (a six-page
   executive view).
2. Use `results-audit-2026-04-21.md` to look up any run cited in the
   manuscript; the status column cites the authoritative source for
   the number quoted.
3. Consult `priority-backfill.md` only if a gap needs action; most
   publication-blocking gaps have already been closed by the work that
   landed between 2026-04-18 and 2026-04-22.

## Verifier checklist

The verifier agent should confirm, at minimum:

- Every cost figure resolves to `totals.cost_usd` in the cited
  `cost_manifest.json` (to 2 decimal places).
- Every F1 / precision / recall resolves to
  `summary.buffers[i].{f1,precision,recall}` in the cited
  `evaluation.json`.
- Every cache-hit figure resolves to `totals.cache_hit_rate` in the
  cited `cost_manifest.json`.
- Every Observation citation resolves to a `## Observation N:` heading
  at the cited line number in `docs/notes/reflections/working-notes.md`.
- Every commit citation resolves via `git log`.

If the verifier finds a dead citation or a numeric mismatch, the
primary agent will correct the draft and the draft only — the
canonical `results/documentation-audit/` files are NOT modified until
verification passes.
