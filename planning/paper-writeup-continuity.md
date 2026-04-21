# Paper write-up continuity — handoff for a fresh session

**Created**: 2026-04-21 (late, end of Session 73 equivalent)
**Purpose**: Continuity message for a fresh Claude Code session to
pick up the paper write-up phase without re-reading the entire
project state.

## Executive state

- **Analysis freeze reached**: all LLM extraction runs complete. No
  more API spend planned. If a paper-claim-driven recalculation
  surfaces during write-up, it's a known possibility but not
  blocking.
- **Documentation audit complete and verified** (2026-04-21):
  `results/documentation-audit/` — the authoritative index to every
  run, deliverable, and citation source. 82 / 85 claims verified by
  a fresh-context verifier agent; 0 dead citations.
- **Interim docs are the primary source** for paper mining.
  Working-notes observations (Obs 1–273) and raw results are the
  deep-dive layer when interim docs are insufficient or suspect.
- **v2 verifier work is quarantined** to
  `archive/v2-verifier-contamination/`. Do NOT cite any figure
  traceable to that directory — the v2 prompt was calibrated on
  gold-standard FPs (calibration-on-test).
- **Paper-headline detection F1 = 0.904** at 50 m on the 487-tile
  matrix uses verifier v1 (confirmed during quarantine). Headline is
  clean.

## Write-up strategy (user-approved)

1. Mine interim documentation first (from `results/documentation-audit/`
   and the per-analysis `report.md` files).
2. Mark superseded interim docs as `SUPERSEDED`.
3. Level-up any interim doc below the exemplar's quality bar.
4. Then draft the paper, referencing interim docs as primary sources,
   descending to raw results / working-notes observations only when
   an interim doc is insufficient or contested.

### Exemplar (quality template) — CONFIRMED 2026-04-21

`results/gold-standard-subtype-classification/report.md` — 17
sections, full citation pattern, methods block, paper implications,
relationship to prior Obs, reproducibility section. Any other
interim doc that matches this structural bar is "finished".

User confirmed this nomination on 2026-04-21 end-of-session. Treat
it as the authoritative template for interim-doc quality from here.

### Two suggested refinements on the user's strategy

1. Before quality-levelling, list existing interim docs against the
   exemplar's structure — produces a concrete gap-list instead of a
   subjective "best" moving target.
2. Write one new meta-consolidation: `results/meta-findings-summary.md`
   at the exemplar's quality level, synthesising Obs 264 / 265 / 266
   (failure taxonomies) + Obs 269 (verifier calibration) + Obs 271
   (benchmark→triangulation) + Obs 272 (attractor-pull) + Obs 273
   (D-S inadequacy) into the paper's Discussion-section spine.
   ~2 hours. Front-loads the synthesis and avoids five-way
   cross-referencing during the main writing pass.

## Documentation state — what we have vs what we need

### Have — primary interim docs (citation-ready)

**Per-analysis reports** (use these as first-pass paper content):

- `results/gold-standard-subtype-classification/report.md` (exemplar)
- `results/55maps-image-generalisation/buffer-band-lift/report.md`
- `results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md`
- `results/55maps-image-generalisation/ds-human-crosstab/report.md`
- `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md`
- `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md`
- `results/55maps-image-generalisation/verifier-calibration-crosstab/` (calibration.md)
- `results/55maps-image-generalisation/buffer-100m-diagnostics/` (summary.json + report)
- `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md`
- `results/h8-v2/analysis_summary.md` (per audit, strongest Era 1
  narrative)

**Paper-tables consolidation (paper-ready, with suggested citations)**:

- `results/paper-tables/metrics_master.{json,csv}` — consolidated
  487-tile-matrix F1/P/R
- `results/paper-tables/leaderboard-20m-annotated.md` — tiered
  leaderboard with annotation
- `results/paper-tables/gold-standard-spatial-tolerance.{md,csv}`
  (suggested citation embedded)
- `results/paper-tables/subtype-classification.{md,csv}` (suggested
  citation embedded)
- `results/paper-tables/spatial_tolerance_comparison.md`
- `results/paper-tables/pipeline_progression.{json,csv}`
- `results/paper-tables/n1_leaderboard.csv` (single-pass K=1 cells)

**Working notes (research trajectory / citation source for Discussion)**:

- `docs/notes/reflections/working-notes.md` Obs 1–273. Key Obs for
  the paper:
  - Obs 262 / 263 / 268 — review-UI calibration
  - Obs 264 / 265 / 266 — failure-mode taxonomies (70 figures)
  - Obs 267 — corrected F1 headline
  - Obs 269 — verifier miscalibration
  - Obs 270 — subtype-classification headline
  - Obs 271 — benchmark→triangulation asymmetric confusion
  - Obs 272 — attractor-pull scale ends at ~125 m
  - Obs 273 — D-S aggregate structurally inadequate

**Methodology / reproducibility**:

- `docs/methodology/preregistration/decisions-log.md` — preregistered
  decisions
- `docs/methodology/preregistration/protocol-errata.md` — E1-E54
- `docs/methodology/v2-verifier-contamination-policy.md` — quarantine
  policy
- `results/ci-metadata-registry.md` — every CI's bootstrap metadata

### Need — gaps worth filling before paper write-up starts

1. **Meta-findings summary** (the suggested refinement above) —
   synthesises Obs 262-273 into a paper-Discussion-shaped narrative.
2. **Era-scoped hypothesis summaries**. Era 1 (`h10/h11/h12-v2`) has
   `analysis_summary.md` for h8-v2 but probably not uniform coverage
   across hypotheses. Check during the interim-doc review.
3. **55-map cross-track comparison doc**. The three tracks (image /
   text-HIGH / text-MIN) each have evaluation.json; the pairwise
   permutation tests exist under `paired-vs-*`. A one-page
   consolidation of "image vs text-HIGH vs text-MIN" with the paired
   tests cited would make the Results-section narrative cleaner.
4. **A "limitations" consolidation doc**. Scattered limitations
   (v2 quarantine, 14 % reviewer-promoted in extended GT, student-GT
   positional noise ~25 m, AUC=0.5 D-S, Pro+MINIMAL cell untested).
   Would become the Limitations section directly.

### Mark-as-superseded candidates

Quick scan:

- `planning/*.md` — many are historical planning docs. The
  doc-audit-rerun-plan.md is DONE (keep as record). Others may be
  superseded. Review and append `**Status: SUPERSEDED — <reason>**`
  to stale entries. Don't delete.
- `archive/cc-sessions/` already handled.
- `archive/v2-verifier-contamination/` already has NOTE.md and
  README.md; no action.
- `archive/flawed-audit-2026-04-19/` already has NOTE.md; no action.
- Anything `pre-launch-audit.md` for a run that completed should be
  annotated `**Status: SUPERSEDED — see <run>_post_run_report.md**`
  (optional polish; not load-bearing).

## Canonical numbers (from the verified doc audit)

Paper will cite these. All verified 2026-04-21:

| Claim | Value | Source |
|---|---|---|
| Detection F1 headline (487-tile matrix, K=30 text-HIGH + PV) | **0.904** [0.878, 0.928] @ 50 m | `results/paper-tables/metrics_master.json` |
| Detection F1 K=5 companion (487-tile matrix) | 0.891 [0.863, 0.916] @ 50 m | same |
| Corrected F1 lower bound (55-map, human-reviewed) | ≥ **0.830** @ 50 m | `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.json` |
| Multi-buffer corrected F1 curve | 0.832 → 0.848 → 0.852 → 0.854 → **0.855** across 50-150 m | `results/55maps-image-generalisation/corrected-f1-multi-buffer/corrected-f1.csv` |
| Subtype weighted-F1 (4-map GS, conditional on match) | **0.887** [0.849, 0.922] | `results/gold-standard-subtype-classification/macro_weighted_summary.json` |
| Attractor-pull scale ends at | ~**125 m** (shell lift becomes non-significant at p=0.381 in the 125-150 m shell) | `results/55maps-image-generalisation/buffer-band-lift/shell.csv` |
| Verifier calibration | ECE **0.269**, AUC **0.655** | `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.json` |
| D-S aggregate (VLM-only slice) | Degenerate at any prior; AUC **0.500** regardless | `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/summary.json` |
| Review set size | 1,028 VLM-only candidates (472 @50 m, 556 re-reviewed → 274 mound, 283 confirmed FP) | `results/55maps-image-generalisation/human-review.csv` and `.../human-review-multi-buffer.csv` |
| Cost (55-map image generalisation) | $364.70 | `outputs/55maps-image-generalisation/cost_manifest.json` |
| Cost (55-map text-HIGH re-run) | $69.60 | `outputs/55maps-text-high-generalisation/cost_manifest.json` |
| Cost (55-map text-MIN) | $60.79 | `outputs/55maps-text-min-generalisation/cost_manifest.json` |

## Suggested fresh-session plan

### Step 1 — Context warm-up (~15 min)

Read in this order:

1. This file (`planning/paper-writeup-continuity.md`) — handoff
   context.
2. `results/documentation-audit/audit-summary.md` — authoritative
   inventory.
3. `results/documentation-audit/results-audit-2026-04-21.md` §A (the
   four 55-map runs) — detailed run-level citations.
4. The exemplar: `results/gold-standard-subtype-classification/report.md`.

### Step 2 — Interim-doc review pass (~1 hour)

For each per-analysis `report.md` under `results/`, score against
the exemplar's 17-section structure:

- ✓ Complete (matches exemplar quality)
- ~ Partial (identify specific gaps)
- ✗ Missing / stub

Output: `planning/interim-docs-review.md` with the scorecard.

### Step 3 — Write the meta-findings consolidation (~2 hours)

`results/meta-findings-summary.md` — synthesises Obs 262-273 into
paper-Discussion-shaped narrative. Uses the exemplar's structural
pattern. Cites each source Obs + analytical artefact. Output must
pass markdownlint and have "Suggested paper text" block for each
major finding.

### Step 4 — Fill identified gaps (variable — 2-6 hours)

Based on Step 2's scorecard, bring sub-exemplar docs up to quality.
Focus on the four "Need" items above:

1. Meta-findings consolidation (Step 3)
2. Era-scoped hypothesis summaries where lacking
3. 55-map cross-track comparison doc
4. Limitations consolidation

### Step 5 — Mark superseded (~30 min)

Append `**Status: SUPERSEDED — <reason>**` to stale planning /
pre-launch-audit / early-analysis docs. Don't delete.

### Step 6 — Hand to paper outline (next session or same session)

With interim docs at uniform quality, draft a paper outline mapping
each section to 1-3 interim docs. Proceed to write-up.

## User decisions (2026-04-21 end-of-session)

Explicit user confirmations recorded here so the next session doesn't
relitigate them:

1. **Exemplar nominated**: gold-standard-subtype-classification
   report (see above).
2. **Meta-findings consolidation IS next**: synthesise Obs 262-273
   into a single paper-Discussion-shaped doc per Step 3 in the plan.
3. **Parsimonious deep-dives**: trust the interim-doc citations by
   default. Descend to raw results / working-notes ONLY when (a) an
   interim doc citation is missing, (b) a causal / mechanism claim
   needs scrutiny, or (c) a paper-headline number is being drafted
   for the final manuscript. Do NOT re-verify 82/85 doc-audit PASS
   claims — they've been verified.
4. **Fact-check-agent for the paper draft (deferred)**: when the
   paper is near complete, build a dedicated adversarial fact-check
   agent that reads ONLY the paper draft + source-of-truth files
   and pass/fails each numeric claim. Modelled on the
   documentation-audit verifier pattern already committed
   (`verification-2026-04-21.md`), but scoped to the paper text
   rather than the interim audit. NOT a task for the opening of the
   next session — a later-stage QA step.

## Critical guardrails for the next session

1. **Do NOT cite figures from `archive/v2-verifier-contamination/`
   or `archive/flawed-audit-2026-04-19/`**. They're preserved for
   methodology transparency, NOT as authoritative sources.
2. **Do NOT re-run the LLM extraction pipeline**. No more API spend.
   If a paper claim requires a number we don't have, flag as a
   potential-recalculation item; do not add to a batch without
   user approval.
3. **Do NOT trust a "fluent prose" interim doc claim without a
   citation**. The flawed-audit-2026-04-19 taught us this. Spot-check
   a claim any time it matters for a paper-headline number.
4. **Distinguish the two "E47" entries**: `protocol-errata.md` line
   1233 is "Primary spatial matching buffer reverted to preregistered
   20 m"; `working-notes.md` line 6553 is "Erratum E47: Proposer
   Prompt Substitution". Shared ID from historical re-numbering —
   clearly cite which file when referencing.
5. **Use UK / Australian English throughout**: analyse (not
   analyze), behaviour, colour, etc.

## Context-budget note

This session used ~75 % of context across a very broad scope (today's
analyses + v2 quarantine + CI metadata + paper-tables integration +
documentation audit). A fresh session starts clean. For the paper
write-up phase, budget context carefully:

- Step 1-2 alone: ~15 % context
- Step 3 (meta-findings): ~25 % context
- Steps 4-5: ~20 % context
- Retains ~40 % headroom for the paper-outline and first section
  drafts.

If any step runs long, checkpoint by committing and start another
fresh session rather than pushing context past 90 %.

## Commit state at handoff

Working tree clean as of commit `c48f639e` (doc-audit replacement).
Eight commits pushed today (`edfc27f5` through `c48f639e`). Full log:
`git log --oneline e038bfe8..HEAD`.
