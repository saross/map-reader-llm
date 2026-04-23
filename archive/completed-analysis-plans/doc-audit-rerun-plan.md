# SUPERSEDED 2026-04-24

**Reason**: Re-audit completed 2026-04-21.

**See**: `results/documentation-audit/audit-summary.md` + `verification-2026-04-21.md` (fresh-context audit; 82/85 claims PASS)

This document is preserved for audit / historical reference. Its original content follows below.

---

## Documentation Audit Re-run Plan

**Created**: 2026-04-19
**Purpose**: Produce a corrected replacement for the documentation
audit at `results/documentation-audit/`. The existing audit
(committed 2026-04-19 in commit `8747d726`) contains factual errors
— hallucinated cost figures, conflated runs with similar names,
wrong Observation number attributions. This plan drives a two-agent
workflow (primary + verifier) to catch the class of error that
fluent-looking prose hides.

## Why two agents

The first audit's failure mode was **content hallucination on a
sound structural framework**. A verifier agent in fresh context can
catch this cheaply because its only job is to check citations
against source files — it doesn't need to enumerate runs or decide
what to check.

Workflow:

```text
Primary agent  → produces draft at results/documentation-audit/draft/
                 (every numeric claim cites source path + key)

Verifier agent → reads the draft and cited files in fresh context
                 → emits pass/fail per claim + aggregate report
                 → does NOT read the old audit or any prior context

Primary agent  → incorporates verifier findings, commits final at
                 results/documentation-audit/ (dropping the draft/)
```

## Known-correct canonical values (anchor against these)

As of 2026-04-19 (committed and verified):

| Run | Cost | F1 @ 50 m (measured) | F1 @ 50 m (D-S) | Cache hit | Obs |
|---|---|---|---|---|---|
| 55maps-image-generalisation | $364.70 | 0.771 | 0.795 | 91.0 % | 256 / 257 |
| 55maps-generalisation (retrospective 2026-04-10 text HIGH) | ~$75 estimate, no cost_manifest | 0.790 | 0.814 | unknown | referenced by 258 |
| 55maps-text-min-generalisation | $60.79 | 0.759 | 0.783 | 0.0 % | 258 / 259 |
| 55maps-text-high-generalisation (2026-04-19 re-run) | $69.60 | 0.788 | 0.813 | 0.0 % | 258 / 259 / 260 |

If the new audit produces different numbers, the verifier should
catch it; if it doesn't, flag immediately — the audit is wrong and
should not be committed.

## 2026-04-21 supplement — state changes since plan creation

The audit plan was written on 2026-04-19. Between then and 2026-04-21
the following load-bearing changes landed; the audit must account for
them:

### New observations (Obs 262–273)

Working-notes `docs/notes/reflections/working-notes.md` has added
Obs 262 through Obs 273 since this plan was written. Running list
with their focal artefact:

- **Obs 262–268**: 55-map image human-review findings (review-UI
  tolerance-circle effect, verifier calibration crosstab, three
  failure-mode taxonomies at 70 figures, 472 phantom TPs, corrected
  F1 ≥ 0.830 at 50 m, etc.). Artefacts:
  `results/55maps-image-generalisation/{uncalibrated-vs-calibrated-crosstab,verifier-calibration-crosstab,human-reviewed-corrected}`.
- **Obs 269**: Verifier over-confident, ECE 0.269, AUC 0.65.
  Artefact: `results/55maps-image-generalisation/verifier-calibration-crosstab/`.
- **Obs 270 / 271**: Subtype-classification accuracy on 4-map GS
  (weighted-F1 = 0.887 headline; benchmark → triangulation 57 %
  asymmetric confusion). Artefact:
  `results/gold-standard-subtype-classification/`.
- **Obs 272**: Attractor-pull scale ends at ~125 m on VLM-only
  candidates (shell permutation lift + Ripley's cross-L). Artefact:
  `results/55maps-image-generalisation/buffer-band-lift/`.
- **Obs 273**: D-S aggregate is structurally inadequate on the
  VLM-only slice at any prior (2-annotator identifiability
  degeneracy). Artefacts: `results/55maps-image-generalisation/ds-human-crosstab/`
  (v1) and `.../dawid-skene-v2-data-driven-prior/` (v2).

### New analyses and their artefacts

- **Multi-buffer corrected F1** (F1 0.832 → 0.855 across R =
  50/75/100/125/150): `results/55maps-image-generalisation/corrected-f1-multi-buffer/`.
- **Buffer-100m diagnostics** (GT clustering + pair-drift):
  `results/55maps-image-generalisation/buffer-100m-diagnostics/`.
- **Human re-review**: `results/55maps-image-generalisation/human-review-multi-buffer.csv`
  (557 rows re-reviewing yesterday's not_mound candidates at five
  tolerance bands).
- **Subtype classification**: `results/gold-standard-subtype-classification/`.
- **Paper-tables consolidation** (new):
  `results/paper-tables/gold-standard-spatial-tolerance.{md,csv}` and
  `results/paper-tables/subtype-classification.{md,csv}`.

### v2 verifier quarantine (2026-04-21)

100 files moved to `archive/v2-verifier-contamination/` because the
v2 verifier prompt was derived by analysing FPs from the 4-map GS
set (calibration-on-test). Affected:

- `results/leaderboard/cells/gold-standard-v2-greedy-v2-327tile.json`
  (moved to archive)
- `results/e47-v1-vs-v2/` (entire directory moved to archive)
- Seven raw-output subdirectories under `outputs/h11/` (moved)

Audit scope impact: any audit row that would have cited a file now in
`archive/v2-verifier-contamination/` is EXCLUDED. The audit should
not treat these as active runs. Policy doc at
`docs/methodology/v2-verifier-contamination-policy.md`. Paper
headline F1 = 0.904 was verified to use verifier v1 (run date
2026-03-25, before v2 existed) — headline is clean.

### CI-metadata registry + sidecars

48 metadata sidecars (41 per-file + 7 directory-level) now exist
across `outputs/`, `results/`, `results/leaderboard/`; master registry
at `results/ci-metadata-registry.md`. The audit should treat any
`<name>.metadata.json` sidecar as the authoritative companion for its
parent file's bootstrap metadata (iterations, seed, resampling unit,
generating script, commit, timestamp). CI-metadata gaps = 0 after
this work.

### Protocol errata additions

- **E54**: Clarification documenting the preregistered 1,000-iteration
  primary-F1 bootstrap vs the 10,000-iteration post-hoc analyses
  (corrected F1, subtype classification, review-UI crosstabs).
  Suggested paper-methods wording included in the errata entry.

### Commit range since 2026-04-19 plan creation

Rough commit range for the audit to review: `8747d726` (the original
flawed audit that triggered this plan) through `1ce5399e` (2026-04-21
paper-tables integration). Spans ~40+ commits of analytical work.
`git log --oneline 8747d726..1ce5399e` is the canonical list.

### Anchor values unchanged

The F1 anchor values in the 2026-04-19 table above are STILL VALID
for those runs — no re-runs happened. Today's additions are scope
expansion, not revision of prior. The audit can treat the 2026-04-19
table as load-bearing.

## Known errors in the existing audit

- Text MIN run: audit claims cost $165.74 with 90.2% cache hit rate
  → **wrong**. Actual: $60.79, 0.0% cache hit (per the committed
  post-run report and cost_manifest.json).
- "55maps-text-high-generalisation (2026-04-10)" with cost "$359.53"
  near-complete at 7/8 → **wrong**. Conflates two distinct runs:
    (a) 2026-04-10 retrospective run at `outputs/55maps-generalisation/`
        with no committed cost manifest (~$75 estimate only);
    (b) 2026-04-19 re-run at `outputs/55maps-text-high-generalisation/`
        with measured cost $69.60.
- Obs 255 attributed to all three 55-map runs → **wrong**. Actual:
  Obs 256 = image; Obs 258/259 = text HIGH paired test + thinking
  tokens; Obs 260 = student jitter; Obs 261 = 50 m bimodal.

## Primary agent prompt

Copy-paste this into a fresh Claude Code session in
`/home/shawn/Code/map-reader-llm/`:

````markdown
I have a prior documentation audit at `results/documentation-audit/`
(4 files) that contains factual errors — hallucinated cost figures,
conflated runs with similar names, wrong Observation number
attributions. I need you to produce a corrected replacement.

## Scope

Audit every **unarchived** run in:
- `outputs/` (anything not under `outputs/archive/` or deeper
  `archive/` dirs)
- `results/` (same exclusion)

For each run, verify the presence and correctness of:
1. F1 / Precision / Recall at buffers 20 / 30 / 40 / 50 m
2. Bootstrap 95% CIs (1000 iterations, seed 42 per Decision 10 +
   E52)
3. Paired permutation tests vs a comparator (where relevant)
4. Dawid-Skene latent-truth correction (55-map runs only)
5. Cost manifest (runs produced via
   `scripts/run_generalisation.py`)
6. Pre-launch audit at
   `configs/run-configs/<run>_pre_launch_audit.md`
7. Post-run report at
   `configs/run-configs/<run>_post_run_report.md`
8. Working-notes observation referencing the run

## Anti-hallucination rules (non-negotiable)

**Every factual claim must cite a specific file path + the line
number (or JSON key path) where the claim can be verified.** If a
number appears in your report, it must match a number in a file
you've read. No paraphrasing numbers from memory or inference.

Specifically:
- Cost figures: cite `outputs/<run>/cost_manifest.json`'s
  `totals.cost_usd` key, to 2 decimal places matching the source.
- F1 / P / R figures: cite
  `outputs/<run>/evaluation/evaluation.json`'s
  `summary.buffers[N].f1`, etc.
- Cache-hit figures: cite
  `outputs/<run>/cost_manifest.json`'s `totals.cache_hit_rate`.
- Observation numbers: cite
  `docs/notes/reflections/working-notes.md` line numbers where
  the `## Observation N:` heading appears.
- Git commits: cite with `gh` or `git log`, not from memory.
- If a run's cost_manifest doesn't exist, say so explicitly —
  don't invent a figure.

## Canonical facts to anchor against

These are committed and verified as of 2026-04-19:

| Run | Cost | F1 @ 50 m (measured) | F1 @ 50 m (D-S) | Cache hit | Obs |
|---|---|---|---|---|---|
| 55maps-image-generalisation | $364.70 | 0.771 | 0.795 | 91.0 % | 256 / 257 |
| 55maps-generalisation (retrospective 2026-04-10 text HIGH) | ~$75 estimate, no cost_manifest | 0.790 | 0.814 | unknown | referenced by 258 |
| 55maps-text-min-generalisation | $60.79 | 0.759 | 0.783 | 0.0 % | 258 / 259 |
| 55maps-text-high-generalisation (2026-04-19 re-run) | $69.60 | 0.788 | 0.813 | 0.0 % | 258 / 259 / 260 |

If your audit produces different numbers than these, YOU ARE
WRONG — don't commit, ask the user.

## Process

1. Read the existing `results/documentation-audit/` files to
   understand the framework (it's OK) and failure modes (content-
   factual errors).
2. Use the Explore agent (subagent_type=Explore) for the broad
   scan — very thorough thoroughness. Brief the agent with the
   same anti-hallucination rules above.
3. Produce replacement files at `results/documentation-audit/draft/`
   (NOT `results/documentation-audit/` directly — the verifier
   agent checks the draft before replacement):
   - `audit-summary.md` — executive summary with cited figures
     only
   - `priority-backfill.md` — what runs lack what deliverables,
     ordered by paper importance
   - `results-audit-<date>.md` — full table, every numeric cell
     citing source file:key
   - `README.md` — short pointer to the three above
4. After the draft is in place, a separate verifier agent (fresh
   context) will check each cited claim. Wait for the verifier
   report before committing.
5. Incorporate verifier findings, move `draft/` contents to
   `results/documentation-audit/` (replacing the old files), and
   commit with a message noting the replacement + the prior
   audit's shortcomings.
6. Before final commit, spot-check at least 5 numeric claims
   yourself by directly reading the cited files — print each
   (source, claimed value, actual value) so the user can verify.

## Important context

- Project root: `/home/shawn/Code/map-reader-llm/`
- Relevant CLAUDE.md files at `~/.claude/CLAUDE.md`,
  `/home/shawn/Code/CLAUDE.md`, and
  `/home/shawn/Code/map-reader-llm/CLAUDE.md` — read them.
- Use UK/Australian English throughout (analyse, behaviour,
  colour, etc.).
- Don't invent run names: if a directory exists under `outputs/`
  or `results/` and it's not under an `archive/` path, it's in
  scope; otherwise not.
- Recent key commits: `4e5c5e5a` (text HIGH re-run), `dea1155f`
  (cleaned-GT eval + Obs 261), `2120741b` (latest as of
  2026-04-19).

## Start by

Read the existing audit summary, then `git log --oneline -30` and
the last three post-run reports
(`55maps_text_high_generalisation_post_run_report.md`,
`55maps_text_min_generalisation_post_run_report.md`,
`55maps_image_generalisation_post_run_report.md`) so you have the
authoritative values before you even look at the old audit.
````

## Verifier agent prompt

Copy-paste this into a fresh Claude Code session AFTER the primary
draft is ready at `results/documentation-audit/draft/`:

````markdown
You are a fact-check verifier. A primary agent has produced a
documentation audit at `results/documentation-audit/draft/` with
three main files: `audit-summary.md`, `results-audit-<date>.md`,
`priority-backfill.md`. Every numeric or specific factual claim is
supposed to cite its source — e.g. a path like
`outputs/55maps-text-min-generalisation/cost_manifest.json` and a
JSON key path like `totals.cost_usd`, or a working-notes line
number for Observation attributions.

Your ONE job: verify each cited claim by reading the actual source
file and confirming the number matches. Produce a pass/fail report.
Do not re-do the audit. Do not add new claims. Do not evaluate
structure, tone, or completeness — only the accuracy of what's
written.

## Process

1. Parse each of the three draft files and extract every (claim,
   source path, key/line) triple.
2. For each triple, read the source file and check whether the
   claimed value matches (to the stated precision — if the draft
   says "$60.79", the source's `totals.cost_usd` must round to the
   same value; if the draft says "0.759", the source's F1 field
   must round to 0.759).
3. If a claim has no citation, flag it as "uncited" — don't
   attempt to verify from context.
4. If a source path doesn't exist, flag it as "dead citation".
5. If a value is wrong, flag it with (claim, cited value, actual
   value, source path).

## Output

Write a verification report to
`results/documentation-audit/verification-<date>.md` with:

- Summary: N claims checked, N passed, N failed, N uncited, N dead
- Full table of every checked claim with PASS / FAIL / UNCITED /
  DEAD
- For failures: the claim text, cited source, claimed vs actual
  value

Do not fix the draft. Do not commit. The primary agent will
incorporate findings.

## Anti-collusion rules

- Do NOT read the existing (pre-draft)
  `results/documentation-audit/` files (i.e. anything outside
  `draft/`). They contain the very errors you're verifying
  against.
- Do NOT use CLAUDE.md or working-notes as a ground-truth crutch
  unless the draft claim explicitly cites them.
- Do NOT accept "approximately equals" as a pass. If the draft
  says $60.79 and the source says $60.7917, check the rounding:
  0.79 is the correct 2-decimal rounding of 0.7917, so PASS. If
  draft says $60.80, FAIL.

## Sample uncited claims too

Pick 5–10 random claims WITHOUT citations from the draft and check
whichever look like they should have citations against the
filesystem. This catches the case where the primary hallucinated a
plausible-but-wrong figure without bothering to add a citation at
all.

## Fresh context requirement

You are running in a fresh Claude Code context. You have NOT seen
the primary audit's process. Your only input is the draft files
and the actual source-of-truth filesystem.

## Start by

Read `results/documentation-audit/draft/audit-summary.md`. List
every numeric claim you see. Then proceed through the other two
draft files similarly.
````

## Why this shape of verifier works

- **Narrowly scoped**: just fact-check, nothing else. Hard to
  drift.
- **Fresh context**: can't inherit the primary's errors via shared
  reasoning.
- **Adversarial framing**: its job is to FAIL claims, not rubber-
  stamp them.
- **Deterministic output**: the verification report is a pass/fail
  table per cell — easy to skim before committing.

## Estimated time

- Primary agent pass: 30-60 min
- Verifier agent pass: 15-30 min
- User spot-check + commit: 10-15 min

Total: ~1–2 hours in the fresh session.
