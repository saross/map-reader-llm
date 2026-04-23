# Paper write-up continuity — handoff for a fresh session

**Created**: 2026-04-21 (late, end of Session 73 equivalent)
**Last updated**: 2026-04-23 (end of Session 74 — Steps 1–3 complete)
**Purpose**: Continuity message for a fresh Claude Code session to
pick up the paper write-up phase without re-reading the entire
project state.

---

## ⚡ Start here (Session 75+ entry point)

**You are on: Step 4** — fill identified gaps (Era 1 consolidations,
cross-track doc, Limitations doc, level-up the partial reports, and
a few small new reports). Est. 11–15 hours comprehensive (user has
confirmed the comprehensive pass, NOT minimum-viable).

**Tree state at handoff**: commit `c1170229`, main-only, working
tree clean. amd-tower and zbook in sync. 10 session-74 commits
pushed: `eb2cf23c` → `c1170229`. Use `git log --oneline 4a866d33..HEAD`
for the full log.

**Reading order (in sequence, don't skim)**:

1. This file — the current orientation layer (you are reading it).
2. `planning/interim-docs-review.md` **§6 Step 4 sequencing** — this
   is the canonical Step 4 work-plan and supersedes the §"Need" list
   below. Start here for the work-item order.
3. `docs/notes/reflections/session-reflection.md` §"Session 74
   Reflection — 2026-04-23" — the agent-verdict-verification lesson.
   Load-bearing for Step 4 because Step 4 will dispatch multiple
   background agents for h-series synthesis.
4. `docs/notes/reflections/llm-observations.md` §"Session 74
   Observations (2026-04-23, map-reader-llm)" — the "sub-agent
   outputs are drafts not verdicts" framing and the 3-of-7 wrong-
   verdict rate context.
5. `results/meta-findings-summary.md` — Step 3's output. Read this
   to ground yourself in the Obs 262–273 synthesis before any Step 4
   item that references failure modes, verifier calibration, or the
   attractor-pull scale.
6. `results/gold-standard-subtype-classification/report.md` — still
   the exemplar for per-analysis report structure. Step 4 analysis-
   summary synthesis tasks should match this 17-section bar (trimmed
   per applicable-sections matrix in `interim-docs-review.md` §2.3).
7. Now begin Step 4 item 1 (synthesise `results/h8-v2/analysis_summary.md`).

**Canonical numbers table for paper claims** — see §"Canonical numbers"
below. Verified 2026-04-21 by a fresh-context verifier agent; do not
re-verify.

**Five load-bearing guardrails** (details in §"Critical guardrails"):

1. Sub-agent verdicts are **drafts, not verdicts** — verify any
   load-bearing agent claim against the filesystem before acting.
2. No citations from `archive/v2-verifier-contamination/` or
   `archive/flawed-audit-2026-04-19/`.
3. UK / Australian English throughout (analyse, behaviour, prioritise,
   synthesise, finalise, recognise).
4. E47 disambiguation required whenever referenced: `protocol-errata.md:1233`
   (buffer revert) vs `working-notes.md:6553` (proposer prompt
   substitution).
5. Step 4 item 3 (Phase 2b analysis_summary.md synthesis) has a
   **MANDATORY Option B residual** sub-task (create retest-era
   `phase2b-carry-forward-parameters.md`, repoint `phase2c-carry-
   forward-parameters.md:126`, archive pre-retest carry-forward). See
   `planning/interim-docs-review.md` §3.15 + §6 item 3 for details.

---

## Session 74 status (2026-04-23) — what's new since the original handoff

### Steps completed (DONE 2026-04-23)

- **Step 1 — Context warm-up** (✅ DONE 2026-04-23).
- **Step 2 — Interim-doc review pass** (✅ DONE 2026-04-23) →
  `planning/interim-docs-review.md` (1,281 lines, 21 rows, 9
  directory groups in §10 "known out-of-scope", markdownlint-clean).
  **Note**: §6 Step 4 sequencing in that file is now the canonical
  Step 4 plan and supersedes the "Need" list in this file's
  §"Documentation state — what we have vs what we need" section
  below.
- **Step 3 — Meta-findings consolidation** (✅ DONE 2026-04-23) →
  `results/meta-findings-summary.md` (1,158 lines, 5 themes, each
  with a "Suggested paper text" block + full Trace; all 9 headline
  canonical numbers spot-checked present; markdownlint-clean).

### New artefacts from Session 74

- **Obs 274** in `docs/notes/reflections/working-notes.md` — Phase
  2b tile-level MCC inverts the F1 ordering (image 0.089 → 0.368
  monotonic across T=0.0 → T=1.3; mechanism is flat sensitivity +
  climbing specificity). Reconciles (does not contradict) Obs 116 /
  177 / 209. Ready to cite in Discussion if the paper addresses
  metric-choice tradeoffs; not required for any Step 3 theme.
- **Phase 2b tile-level MCC** at `results/paper-eval/mcc/phase2b/`
  (10 conditions × K=3 × 340 tiles, patched pipeline).
- **CRS bugfix** (commit `eb2cf23c`): `scripts/analyse_consensus_sweep.py::consensus_to_gdf`
  now constructs the GeoDataFrame in EPSG:4326 then `to_crs(TARGET_CRS)`.
  Contamination scope verified narrow — Phase 2b MCC was the only
  post-2026-04-11 consumer that hit the bug. **No active artefacts
  required re-compute.** `load_geojson` consumers dodge the bug via
  GeoPandas' default 4326 auto-assignment for CRS-less GeoJSON; the
  `ensure_utm_crs` helper in `lib_consensus` is immune by construction.
- **Option A pre-retest phase2b archive pass** (commit `16ee3ae5`):
  six orphan 60-tile K=10 pilot docs moved from `results/` to
  `archive/outputs-pre-retest-60-tile/phase2b/`. Ci-metadata-registry
  updated. `phase2b-carry-forward-parameters.md` **retained** with a
  retention banner because `phase2c-carry-forward-parameters.md:126`
  depends on it — **Option B residual MANDATORY for Step 4** (see
  §"Critical guardrails" item 5 above).
- **UNINTENDED-T1.0 disposition** (commit `5ae94041`): both
  `outputs/h11/{consensus,single-pass}-384-UNINTENDED-T1.0/README.md`
  banners rewritten to reflect dual role (origin = E43 deviation;
  retention = serendipitous Era 2 / 487-tile T=1.0 coverage for 157
  downstream references where Phase 2b at 340 tiles cannot extend).

### Scorecard coverage gap caveat

The original §"Documentation state — what we have vs what we need"
list in this file was a strict subset of the actual `results/`
tree. Session 74's re-inventory discovered ~10 directories that
belong in-scope and added 6 of them as scorecard rows (phase3a-image-
matrix, secondary-effects, factor-analysis, retest-production-summary,
evaluation-scopes, uncalibrated-vs-calibrated-crosstab; plus Phase 2b
retest as row 15). 9 directory groups remain in scorecard §10 "known
out-of-scope". **Use `planning/interim-docs-review.md` §6 as the
authoritative Step 4 plan**; this file's §"Need" list is
superseded-but-preserved-for-reference (see DONE-annotations below).

---

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

> **⚠️ Superseded 2026-04-23 by `planning/interim-docs-review.md` §6
> Step 4 sequencing**, which is the authoritative ordered 10-item
> Step 4 work-plan. Items below retained for historical context and
> annotated DONE / see-§6 where applicable.

1. **Meta-findings summary** (the suggested refinement above) —
   synthesises Obs 262-273 into a paper-Discussion-shaped narrative.
   **✅ DONE 2026-04-23** → `results/meta-findings-summary.md`
   (1,158 lines, 5 themes, markdownlint-clean, commit `0fccf455`).
2. **Era-scoped hypothesis summaries**. Era 1 (`h10/h11/h12-v2`) has
   `analysis_summary.md` for h8-v2 but probably not uniform coverage
   across hypotheses. Check during the interim-doc review.
   **→ see scorecard §6 items 1, 2, 3, 4**: h8-v2 synthesise (L,
   ~90 min); h10 synthesise (L, ~90 min); Phase 2b retest synthesise
   (L, ~90 min, with Option B residual sub-task); h11 consolidate
   (M, 60–75 min). The "Era 1 has analysis_summary.md for h8-v2" line
   was wrong — scorecard row 10 confirms h8-v2 has NO dedicated
   summary; narrative is in working-notes Obs 238.
3. **55-map cross-track comparison doc**. The three tracks (image /
   text-HIGH / text-MIN) each have evaluation.json; the pairwise
   permutation tests exist under `paired-vs-*`. A one-page
   consolidation of "image vs text-HIGH vs text-MIN" with the paired
   tests cited would make the Results-section narrative cleaner.
   **→ see scorecard §6 item (cross-track)**: not in the current
   §6 top-10 (which is scoped to interim-doc level-ups rather than
   new synthesis docs). This item is still open; consider slotting
   after item 4 in Step 4 or as a late-Step-4 / early-Step-6 task.
4. **A "limitations" consolidation doc**. Scattered limitations
   (v2 quarantine, 14 % reviewer-promoted in extended GT, student-GT
   positional noise ~25 m, AUC=0.5 D-S, Pro+MINIMAL cell untested).
   Would become the Limitations section directly.
   **→ still open**. Like item 3, not explicitly in §6 top-10 but
   needed before paper outline. Suggested slot: after §6 items 1–6
   (i.e., after the Era 1 consolidations and the two new reports),
   so the Limitations doc can cite them directly.

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

### Step 1 — Context warm-up (~15 min) — ✅ DONE 2026-04-23

Read in this order:

1. This file (`planning/paper-writeup-continuity.md`) — handoff
   context.
2. `results/documentation-audit/audit-summary.md` — authoritative
   inventory.
3. `results/documentation-audit/results-audit-2026-04-21.md` §A (the
   four 55-map runs) — detailed run-level citations.
4. The exemplar: `results/gold-standard-subtype-classification/report.md`.

### Step 2 — Interim-doc review pass (~1 hour) — ✅ DONE 2026-04-23

For each per-analysis `report.md` under `results/`, score against
the exemplar's 17-section structure:

- ✓ Complete (matches exemplar quality)
- ~ Partial (identify specific gaps)
- ✗ Missing / stub

Output: `planning/interim-docs-review.md` with the scorecard.

**Actually produced**: 21-row scorecard covering the continuity doc's
"Have" list + 6 re-inventory additions + 1 Phase 2b retest row, plus
a §10 "known out-of-scope" section covering 9 directory groups. Final
tier breakdown: 0 ✓ / 13 ~ / 2 ✗ stub / 4 ✗ missing. Commit `f0287747`.

### Step 3 — Write the meta-findings consolidation (~2 hours) — ✅ DONE 2026-04-23

`results/meta-findings-summary.md` — synthesises Obs 262-273 into
paper-Discussion-shaped narrative. Uses the exemplar's structural
pattern. Cites each source Obs + analytical artefact. Output must
pass markdownlint and have "Suggested paper text" block for each
major finding.

**Actually produced**: 1,158-line synthesis with 13 sections covering
5 themes (T1 human-review calibration / T2 failure taxonomies / T3
verifier miscalibration / T4 subtype asymmetry / T5 attractor-pull +
D-S inadequacy). Each theme has a "Suggested paper text" block with
full Trace (≥ 1 Obs anchor + ≥ 1 artefact path). All 9 headline
canonical numbers spot-checked present. Commit `0fccf455`.

### Step 4 — Fill identified gaps (variable — 11–15 hours comprehensive) — ⏸ PENDING

**Authoritative plan**: `planning/interim-docs-review.md` §6 Step 4
sequencing — 10 ordered items with effort estimates. User has
confirmed the comprehensive pass (NOT minimum-viable). Supersedes the
four original "Need" items above; see the DONE annotations in that
section for mapping.

Short summary (see scorecard §6 for full detail):

1. `results/h8-v2/analysis_summary.md` synthesise (L, ~90 min)
2. `results/h10/analysis_summary.md` synthesise (L, ~90 min)
3. `results/retest/phase2b/analysis_summary.md` synthesise (L, ~90 min)
   **+ MANDATORY Option B residual** (retest-era carry-forward doc,
   repoint phase2c line 126, archive pre-retest carry-forward)
4. `results/h11/analysis_summary.md` consolidate (M, 60–75 min)
5. `buffer-100m-diagnostics/report.md` write (M, 45–60 min)
6. `results/paper-eval/mcc/report.md` write (M, 45–60 min)
7. `factor-analysis/factor_analysis_results.md` level-up (M, ~45–60
   min; includes fixing blank Temperature rows 42–43)
8. `uncalibrated-vs-calibrated-crosstab/crosstab.md` level-up (S, 25–35 min)
9. `results/evaluation-scopes.md` level-up (S, 20–30 min)
10. Batch-level-up the eight partial per-analysis reports (~3.5–4.5 h)

Items 3 and 4 from the original "Need" list (55-map cross-track
comparison doc; Limitations consolidation) are NOT in scorecard §6's
top 10 but remain open. Suggested slot: after §6 items 1–6, so the
Limitations doc can cite the newly-written Era 1 summaries and small
reports directly.

### Step 5 — Mark superseded (~30 min) — ⏸ PENDING

Append `**Status: SUPERSEDED — <reason>**` to stale planning /
pre-launch-audit / early-analysis docs. Don't delete.

**Session 74 note**: Option A of the phase2b archive pass (six orphan
pre-retest docs moved to `archive/outputs-pre-retest-60-tile/phase2b/`,
commit `16ee3ae5`) was the Session-74 equivalent of an ad-hoc
"SUPERSEDED" pass. Step 5 should cover remaining stale planning and
pre-launch-audit docs; scorecard §5 mark-as-superseded candidates
list is still valid.

### Step 6 — Hand to paper outline (next session or same session) — ⏸ PENDING

With interim docs at uniform quality, draft a paper outline mapping
each section to 1-3 interim docs. Proceed to write-up.

#### Step 6 polish-pass backlog

Items surfaced during Step 4 that are not load-bearing for the current
item's claim but warrant a polish pass before paper finalisation:

- **50 m TP count discrepancy (buffer-100m-diagnostics vs corrected-F1
  multi-buffer, noted 2026-04-24 during Session 75 Item 5
  verification)** — **RESOLVED 2026-04-24 (Session 75 close-out)**:
  investigated by an Explore agent as part of the end-of-session
  clearance pass. Root cause is **not** a matching-algorithm
  difference; both pipelines use the same Hungarian one-to-one
  matcher. The 2-pair gap arises from different ground-truth inputs:
  the diagnostic consumes `human-review.csv` (472 mounds at 50 m
  from yesterday's single-buffer review) while corrected-F1 consumes
  `human-review.csv` + `human-review-multi-buffer.csv` (474 at 50 m,
  adding candidate IDs 5641 and 5777 from today's multi-buffer
  re-review). Both pipelines are internally correct. Reconciliation
  notes added to both reports in commit `783f37c2`; paper-citation
  rule: use 4,110 (corrected-F1) for headline claims; 4,108
  (diagnostic) is descriptive-only for the 50 → 100 m recall-gain
  decomposition. No code/data fix needed.

- **metrics_master.csv vs metrics_master.json row-count drift (noted
  2026-04-24 during the consolidate_paper_metrics.py dry-run)**:
  committed `results/paper-tables/metrics_master.csv` has 104 rows;
  `metrics_master.json` has 100 rows. The two output files were
  generated at different times and are out of sync at HEAD. A
  deliberate re-run of `scripts/consolidate_paper_metrics.py` during
  paper finalisation will bring them back to parity (100 rows each).
  Not urgent — the JSON is the authoritative source; the 4 extra
  rows in the CSV are stale pro-high-text pool_size=10 entries from
  an earlier run. Not addressed in the Session-75 close-out because
  the plan's non-goal explicitly deprioritises output regeneration.

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

### Added 2026-04-23 (Session 74)

The following five items extend the original five guardrails above
and are specific to Step 4 work.

1. **Sub-agent outputs are drafts, not verdicts**. Session 74
   dispatched seven background Explore / general-purpose agents;
   three returned wrong or mis-calibrated verdicts that would have
   caused wasted compute or mis-cited papers if acted on unchecked
   (Phase 2b tile count wrong by a factor of 22; Phase 3a
   contamination verdict completely reversed on direct sjoin test;
   subtype-MCC contamination flagged where `ensure_utm_crs` helper
   makes it immune). For any load-bearing claim from a background
   agent, run a direct-evidence check against the filesystem or
   actual code execution BEFORE relaying it to the user or acting on
   it. See `docs/notes/reflections/session-reflection.md` §Session 74
   and `docs/notes/reflections/llm-observations.md` §Session 74 for
   the full framing.
2. **Phase 2b carry-forward Option B residual is MANDATORY for Step
   4 item 3**. When synthesising
   `results/retest/phase2b/analysis_summary.md` you must ALSO
   (a) create a retest-era
   `results/phase2b-carry-forward-parameters.md` equivalent based on
   the 340-tile K=3 retest data, (b) repoint
   `results/phase2c-carry-forward-parameters.md:126` to the new
   retest-era doc, (c) archive the pre-retest
   `results/phase2b-carry-forward-parameters.md` to
   `archive/outputs-pre-retest-60-tile/phase2b/` alongside the six
   files already archived 2026-04-23 (commit `16ee3ae5`). Tracked
   redundantly in four places: retention banner in the file itself;
   scorecard §3.15 "Superseded pre-retest artefacts"; scorecard §3.15
   level-up notes sub-task; scorecard §6 sequencing item 3.
3. **CRS patch is prophylactic; no active re-compute needed**. The
   `scripts/analyse_consensus_sweep.py::consensus_to_gdf` fix (commit
   `eb2cf23c`) protects against future consensus-path computes but
   was only hit by today's Phase 2b MCC. Other consumers
   (`evaluate_detections.py::load_geojson`,
   `lib_consensus.ensure_utm_crs`) use different paths that dodge the
   bug. Contamination scope verified narrow by three background
   agents; do not re-check unless a new consensus-rebuild-path
   compute is added. A future hardening (refactor `consensus_to_gdf`
   to use `ensure_utm_crs`) is a Step 4 nice-to-have, not a blocker.
4. **UNINTENDED-T1.0 retention is by design**. The two
   `outputs/h11/{consensus,single-pass}-384-UNINTENDED-T1.0/`
   directories are retained with dual-role framing: origin = E43
   deviation; retention = serendipitous Era 2 / 487-tile T=1.0
   coverage for 157 downstream references where preregistered Phase 2b
   (340 tiles) cannot extend. Do NOT archive; the READMEs
   (commit `5ae94041`) document the framing. Scientific T=1.0
   evidence rests on Phase 2b (Obs 116 / 177 / 209), not E43 data.
5. **Scorecard §6 is the Step 4 work-plan**; this file's §"Need"
   list is superseded-but-preserved. If §6 and this file disagree
   about Step 4 order, §6 wins.

## Context-budget note

> **⚠️ Superseded 2026-04-23** — Steps 1-3 used more context than this
> estimate anticipated (Session 74 spent most of its budget on the
> Step 2 re-inventory cascade and the CRS-bugfix / contamination-
> investigation thread). Updated estimates below.

Original Session 73 estimate, preserved for reference:

- Step 1-2 alone: ~15 % context
- Step 3 (meta-findings): ~25 % context
- Steps 4-5: ~20 % context
- Retains ~40 % headroom for the paper-outline and first section
  drafts.

Revised estimates after Session 74 actuals:

- Steps 1-3 actual: ~60-70 % context (one session, though the session
  had several tangential threads — CRS bugfix, UNINTENDED disposition,
  phase2b archive — that a more disciplined Step-3-focused session
  might avoid).
- Step 4 comprehensive (10 items, 11-15 h): probably 2-3 sessions, not
  one. The four L-effort synthesis items (h8-v2, h10, phase2b, h11) are
  each context-heavy because they span many JSON files. Consider doing
  one or two per session with commit + sync between.
- Step 5 (~30 min) and Step 6 (paper outline) can probably share a
  single session after Step 4 completes.

Rule of thumb that held across Sessions 73 and 74: checkpoint-commit
at natural boundaries and start a new session rather than pushing
past ~75 % context. Session 74 pushed close to that ceiling by the
end (several agent dispatches, several file-read cycles); next session
should aim for fewer concurrent threads.

## Commit state at handoff

**Session 74 handoff (2026-04-23)**: working tree clean at commit
`c1170229`, `main` only (no stray branches), amd-tower and zbook in
sync. Session 74 pushed 11 commits: `eb2cf23c` → `c1170229`. Full log:
`git log --oneline 4a866d33..HEAD`.

Session 74 commit sequence (bottom-up on `git log`):

- `eb2cf23c` fix(crs): reproject consensus centroids in consensus_to_gdf
- `de5b1214` feat(mcc): compute Phase 2b tile-level MCC for H7 temperature sweep
- `5ae94041` docs(unintended): clarify dual-role disposition for UNINTENDED-T1.0 dirs
- `f0287747` docs(scorecard): Step 2 interim-doc review — 21 rows + known-out-of-scope
- `44990e97` obs(mcc): Obs 274 — Phase 2b tile-level MCC orthogonal to F1 headline
- `b323f045` obs(mcc): tighten Obs 274 cross-references — cite Obs 116 as F1 root
- `16ee3ae5` chore(archive): Option A — archive pre-retest phase2b pilot docs
- `0fccf455` docs(meta-findings): synthesise Obs 262–273 into paper-Discussion spine
- `c1170229` reflect(session-74): end-of-session reflection for 2026-04-23
- (this commit, whichever hash it lands on): docs(continuity): Session 74
  handoff update + Step 4 reading order

### Session 73 handoff (preserved for reference)

Working tree clean as of commit `c48f639e` (doc-audit replacement).
Eight commits pushed 2026-04-21 (`edfc27f5` through `c48f639e`). Full
log: `git log --oneline e038bfe8..c48f639e`.
