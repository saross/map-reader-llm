# Documentation Audit and Remediation Plan — Intermediate Run Documentation

> **Last revised**: 2026-05-28 (Phase 0 execution complete; Stage Gate 1
> approved 2026-05-26; corrections noted for § 3.2 framing, § 3.3/§ 6.1
> internal contradiction, and `experiment_intent.md` count undercount).
> See [§ Changelog](#changelog) for revision history.

**Author**: Claude Code (research-agent run, Session 87+1)
**Status**: Stage Gate 1 approved 2026-05-26; Phase 0 (spec edits)
complete 2026-05-26; Phase 1 (templated generator) next.
**Scope**: `results/**.md`, `outputs/**/post_run_report.md` (plus analogous
post-run summary docs under `outputs/`), and the canonical specs at
`docs/methodology/output-directory-standard.md`,
`docs/methodology/documentation-protocol.md`, and the
"Document Revision Policy" section of `/home/shawn/Code/map-reader-llm/CLAUDE.md`.
**Out of scope**: `docs/notes/reflections/working-notes.md`,
`docs/methodology/preregistration/`, `reports/**.md`,
`docs/methodology/research/`.

---

## 1. Executive summary

The repository contains 472 markdown documents under `results/` and 69 under
`outputs/`. A previous audit pass (`results/documentation-audit/audit-summary.md`,
2026-04-22) already mapped Era 1 (`h8`–`h12`, `retest`) versus Era 2 (the four
55-map generalisation runs), and the Era 2 runs already implement a strong
post-run-report template. Two reported "phantom" gaps — Phase 2b summary
missing, Phase 3b absent — are not real gaps: Phase 2b has a dedicated
`results/retest/phase2b/analysis_summary.md` (Session 75 closure), and
Phase 3b was officially absorbed into Phase 2e under the v2.9 preregistration
redesign.

The real gaps cluster in three buckets:

1. **Specification drift**: the canonical `output-directory-standard.md`
   describes a directory tree but does **not** specify a post-run-report
   schema, even though the project has produced four exemplar post-run
   reports following an unwritten template. The Document Revision Policy in
   `CLAUDE.md` is in force but is followed by **zero** of the 472 results
   docs sampled.
2. **Era 1 post-run-report deficit**: 24 of 26 `outputs/` subdirectories
   lack a `post_run_report.md`. Eleven of those are Era 1 runs (`h8-v2`,
   `h10`, `h11/*`, `h12-v2`, `phase2*`, `phase3*`, `verifier-t-pilot`,
   `retest`); these are the highest-value targets for paper-writing.
3. **Cross-reference drought**: results docs name-check sibling runs
   inconsistently. There is no machine-readable lineage graph mapping
   experiment → preceding experiment → follow-up → working-notes
   observation cluster.

**Recommended staging**: a single Stage Gate after § 3 (spec upgrade
approval). Once the upgraded spec is approved, the propagation work
divides into a one-shot generator script for templated post-run reports
(~6–10 hours, mostly script authoring) and an opportunistic
revision-banner back-fill (CLAUDE.md says "back-fill on touch only", so
this is incidental, not bulk). **Total estimated effort across all
remediation: 24–38 hours**, of which 8–12 hours is hand-authoring of
narrative material that no script can generate.

This is the user's paper-writing-readiness audit. The plan is intentionally
exhaustive in one pass, since the user has been burned before by audits
that "kept finding more holes". When the two audiences (paper-source
priority, newcomer-orientation) conflict, the plan favours
**citation-ready findings first, narrative scaffolding second**, per the
brief.

---

## 2. Findings from steps 1 and 2

### 2.1 What the canonical spec actually requires

#### `docs/methodology/output-directory-standard.md` (158 lines, last touched during Phase 2e era)

- Defines artefact types (detections, meta, tile-status, candidate manifest,
  probabilities, verified detections, threshold sweeps).
- Defines a **gitignore policy** (regenerable artefacts: `crops/`,
  `batch_working/`, `*.log`).
- Defines a **directory structure** (proposed, with a worked example for
  `outputs/h11/` and `outputs/production/`).
- Defines **naming conventions**: lowercase-hyphen directories, `run_{N}`
  with zero-padded integers, condition names of the form
  `{model}-{thinking}-{modality}-{temperature}`, verified files as
  `verified-{verifier-variant}.geojson`.
- Lists four explicit TODOs (track `pv-diag-384` in git, extract
  `consensus-384` detections, standardise gitignore, create `production/`).

The spec **does not** mandate:

- A `post_run_report.md` per `outputs/<run>/`.
- A `pre_launch_audit.md` companion.
- A `cost_manifest.json` schema.
- Cross-references between results docs and `working-notes.md` Observations.
- Revision banners on results docs.
- A schema for the post-run report itself (front-matter, top-line table,
  cost accounting, etc.).

#### `docs/methodology/documentation-protocol.md`

- Working notes, decisions log, errata, results files, session log — each
  has a "when to write / trigger / format / cadence" entry.
- Results files entry (lines 81–90) is the only mention of
  `results/`-tree docs, and prescribes only "Phase-specific. Must
  include a status line (Status: Complete / In Progress / Draft)".
- No prescription for `outputs/<run>/post_run_report.md` at all — the
  exemplar template is not codified anywhere.

#### `CLAUDE.md` — Document Revision Policy

Three-step pattern (Last revised banner immediately below H1; `## Changelog`
section at the bottom with newest-first dated entries; in-place body edits
each time). Scope explicitly named as "any document under `results/**.md`,
`reports/**.md`, or `outputs/**/post_run_report.md` (and analogous post-run
summary docs under `outputs/`)". Back-fill on touch only.

### 2.2 Best-in-class existing docs (proposed canonical exemplars)

I read several candidates and propose three best-in-class exemplars. Each
is a different **kind** of doc and the spec upgrade should generalise
across all three.

#### Exemplar A — Run-level post-run report

`outputs/55maps-image-generalisation/post_run_report.md` (281 lines)
and its sibling `configs/run-configs/55maps_image_generalisation_post_run_report.md`
(dual-location convention; see § 9.2 below).

What makes it strong (paper-source priority):

- Front-matter block: run name, completed timestamp, host, launcher
  commit, launcher version, config path, pre-launch audit path. Every
  field needed to reproduce the run is one click away.
- Top-line F1 / P / R at four buffer radii with bootstrap CIs in a
  single table, bolded operating point.
- Dawid-Skene corrected metrics table immediately below, with an
  explicit ΔF1 attribution.
- Cost accounting at three resolutions: overall (one number), per-stage
  (proposer / verifier / consensus / extract / evaluate), per-pass
  (worker count, wall-clock, tiles OK, retries, thinking tokens), token
  breakdown (input, cached, output, thinking, totals), and unit costs
  (cost-per-tile, cost-per-map, cost-per-detection, cost-per-mound).
- Operational issues and recoveries section (each issue with task
  reference and fix proposal).
- Reproducibility recipe (literal `bash` block).
- Artefacts table with file → purpose mapping.

Quoting the most useful fragment:

```text
| Field | Tokens | Share |
|-------|-------:|------:|
| Input (billed, non-cached) | 61.5 M | 7.8% |
| Input (cached) | **621.3 M** | **79.1%** |
| Output | 7.8 M | 1.0% |
| Thinking | 95.2 M | 12.1% |
| **Total** | **785.7 M** | 100% |

**Cache hit rate: 91.0%** — Gemini context caching saved ~79% of
billable input tokens across the run.
```

That is exactly what the paper's cost table will need; the doc is
already paper-citation-ready.

#### Exemplar B — Multi-phase narrative

`results/retest/retest-production-summary.md` (level-up 2026-04-24,
Session 76).

What makes it strong (newcomer-orientation):

- Front-matter cites every cross-referenced sibling doc, including the
  Phase 2b dedicated analysis summary (with a "see dedicated narrative"
  pointer in § 4 itself).
- Headline statistical findings precede methodology (consistent with
  paper-source priority).
- Each phase section pairs a per-condition table with a "Key finding"
  paragraph that states which contrasts are FDR-significant, with
  exact p-values inline.
- Includes the cross-era model-comparability caveat (Gemini 2.0 Flash
  vs Gemini 3 Flash) explicitly in the front-matter.
- Has a paper-facing headline claim sentence at the end of § 1.

#### Exemplar C — Era 2 phase-specific level-up

`results/phase3a-image-matrix/consensus-analysis-summary.md`.

What makes it strong:

- Distinguishes paper-citation source from companion auto-generated file
  (`consensus-analysis-summary_autogen.md`), with explicit script-hardening
  note ("re-running the script does NOT overwrite it").
- Cross-references siblings (`phase3a-text-matrix/secondary_effects.md`,
  `secondary-effects/secondary_effects.md`).
- Headline numbers under explicit `## 1. Executive summary` heading.
- "One-line paper claim" paragraph for direct paper-text reuse.
- Bootstrap protocol (n iter, seed, resampling unit) cited verbatim
  from the metadata sidecar.

### 2.3 Era 1 vs Era 2 documentation pattern (confirmed)

The 2026-04-22 audit (`results/documentation-audit/audit-summary.md`)
already characterises this split. I confirmed the basic shape:

- Era 1 (h8 → h12, retest, phase2*, phase3*) has rigorous statistics in
  per-phase results docs; what it lacks is the **run-level** post-run
  report (cost manifest, pre-launch audit, post-run report). The
  statistical content is there; the operational scaffolding is not.
- Era 2 (the four 55-map generalisation runs) has both. The four runs
  are documented to a uniform standard.

The deliverable-coverage table in `audit-summary.md` (eight columns × four
runs) is the existing scoring framework. The plan below extends that
framework rather than re-inventing it.

---

## 3. Proposed spec upgrades (Stage Gate)

> **STAGE GATE**: the user must approve § 3 in full before any
> propagation work begins (§ 6 onwards). The upgrades below are
> diff-level proposals; the actual edits are remediation work, not
> planning work.

The canonical spec needs three additions and one minor tightening.

### 3.1 Addition — codify the post-run-report schema

**Where**: a new section in `docs/methodology/output-directory-standard.md`
titled "## Post-Run Report Schema", inserted between the existing
"## Naming Conventions" and "## Immediate TODOs" sections.

**Content**: lift the structure of Exemplar A directly into the spec. The
schema (in spec form) becomes:

```text
Every outputs/<run-id>/ that represents a completed experimental run
must contain a post_run_report.md with the following sections, in order:

1. Front-matter block (REQUIRED):
   - Run name, completed timestamp (UTC), host, launcher commit (40-char SHA),
     launcher version, config path, pre-launch audit path.
2. Top-line result (REQUIRED):
   - F1 / P / R at the project's standard buffer radii (20/30/40/50 m)
     with bootstrap 95% CIs (1,000 iterations, seed 42, tile-level resampling).
   - Bolded operating point (vote_t, prob_t).
3. Corrected-for-incompleteness result (REQUIRED if D-S applicable):
   - Method × F1 / P / R table; explicit Δ F1 attribution.
4. Cost accounting (REQUIRED):
   - Overall total + budget-band check.
   - By stage (proposer / verifier / consensus / extract / evaluate).
   - Per pass (workers, wall-clock, tiles OK/failed, retries, thinking tokens).
   - Token breakdown (input billed, input cached, output, thinking, total).
   - Unit costs (per tile, per map, per detection, per reference mound).
5. Per-map extrema (REQUIRED if multi-map run):
   - Top-5 / bottom-5 by cost; mean cost-per-tile dispersion comment.
6. Scope (REQUIRED): map count, tile count, API call counts (success/fail),
   reference mound count, candidate count, final-detection count.
7. Timeline (REQUIRED if material): launch → per-stage → complete (UTC).
8. Operational issues and recoveries (CONDITIONAL): only if there were any.
9. Reproducibility recipe (REQUIRED): literal bash block, expected cost
   ± tolerance, expected runtime.
10. Artefacts for the paper (REQUIRED): file → purpose table for tracked
    artefacts; list of large intermediate artefacts available in
    companion data release.
11. See also / lineage block (REQUIRED — see § 3.4 below).
12. Changelog (REQUIRED on revision; see Document Revision Policy).
```

**Rationale**: this section codifies the unwritten template that produced
Exemplar A. Once it is canonical, the templated generator (§ 7) has a
schema to target, and Era 1 back-fills have a checklist to follow.

### 3.2 Addition — codify the dual-location convention

The four 55-map runs each have a post-run report at **two** paths:

- `outputs/<run-id>/post_run_report.md` — the "operational" copy, lives
  beside the artefacts.
- `configs/run-configs/<run-id>_post_run_report.md` — the "config-side"
  copy, lives beside the YAML.

The two are byte-for-byte equivalent for the active runs but **drift
inevitably** unless one is canonical and the other is a symlink-or-stub.
The 2026-05-03 recovery annotation in `audit-summary.md` already had to
disambiguate "the original launch state" from "post-recovery state"
because of this duplication.

**Proposed convention** (to add to the spec):

- The `outputs/<run-id>/post_run_report.md` is **canonical**.
- The `configs/run-configs/<run-id>_post_run_report.md` becomes a
  one-line stub: `# <run-name> — post-run report\n\nMoved to outputs/<run-id>/post_run_report.md`.
- Or, alternatively, kept identical with an explicit "synced from
  outputs/..." banner and a CI lint that errors if the two diverge.

The user should choose between "stub" and "synced" at the Stage Gate.
The plan below assumes "stub" since it removes the drift risk entirely
(recommended).

### 3.3 Tightening — extend Document Revision Policy scope

The CLAUDE.md Revision Policy currently names `results/**.md`,
`reports/**.md`, `outputs/**/post_run_report.md`. It should explicitly
include:

- `outputs/**/experiment_intent.md` — the per-pass intent files (~50 of
  these exist) — currently informal, should be in scope.
- `outputs/**/evaluation/evaluation.md` — the per-run evaluation
  summaries (~12 of these) — currently informal, should be in scope.
- `outputs/**/pre_launch_audit.md` — the audit-config skill output;
  one exists at `outputs/55maps-text-high-t0.3-generalisation/pre_launch_audit.md`.

**No content change needed** to CLAUDE.md; the existing wording
"and analogous post-run summary docs under `outputs/`" is broad
enough — but the spec should enumerate the candidate paths explicitly so
the back-fill rule is unambiguous.

### 3.4 Addition — cross-reference / lineage block

Every results doc and every post-run report must include a
`## See also` (or `## Lineage`) block. Format:

```markdown
## See also

- **Preceding experiment**: `results/<phase-X>/<doc>.md` — what carried
  forward into this run.
- **Follow-up experiment**: `results/<phase-Y>/<doc>.md` — what this
  run carried forward.
- **Run output directory**: `outputs/<run-id>/` (or list specific
  artefact paths).
- **Working-notes Observations**: Obs N (line LLLL) — short title.
- **Decisions / Errata**: D N, E N (with one-line gloss).
```

**Rationale**: the existing best-in-class docs do this informally
(Exemplar B has it as prose; Exemplar C has it as a "Cross-reference"
header). Codifying as a structured block makes it (a) machine-greppable,
(b) useful for the templated generator, (c) a clear forcing function for
authors to surface the lineage when writing.

### 3.5 Minor — spec status section refresh

The `## Status` section in `output-directory-standard.md` currently lists
`outputs/h11/pv-diag-384/` as gitignored and "only on sapphire". This is
out-of-date as of the prior audit; the spec should be refreshed to reflect
current state (or the status section dropped in favour of a "last
reviewed" date plus the Revision Policy banner).

---

## 4. Verifying the reported gaps

Before the previous survey's claim of "Phase 2b summary missing, Phase 3b
absent entirely" gets propagated as a remediation target, the actual
filenames need re-reading.

### 4.1 Phase 2b — labelling artefact, not a gap

**Reported**: "Phase 2b summary missing".

**Actual state**:

- `results/phase2b-carry-forward-parameters.md` — exists (the carry-forward
  parameters file).
- `results/retest/phase2b/analysis_summary.md` — exists; this is the
  paper-citation source for Phase 2b (Session 75 closure, commit
  `e8c46809`). Lines 1–28 read like a paper extract.
- `results/retest/retest-production-summary.md` § 4 — covers Phase 2b
  numbers for cross-reference, with an explicit "See dedicated analysis
  summary" pointer in § 4.

The pre-retest Phase 2b summary may have been archived under
`archive/outputs-pre-retest-60-tile/phase2b/` (the carry-forward doc
references it). What the previous survey saw as a "missing" file is the
**absence of a top-level `results/phase2b-analysis-summary.md`**. That is
a labelling inconsistency (other phases have a top-level
`phase2N-analysis-summary.md`; Phase 2b has it under `retest/`), not a
content gap.

**Action** (in the gap inventory below): treat as a Tier-3 cosmetic
labelling issue — add a stub at `results/phase2b-analysis-summary.md`
that points to the retest doc, OR add a cross-reference in the
`documentation-index.md` so newcomers can find it. Effort: 15 minutes.

### 4.2 Phase 3b — never existed; not a gap

**Reported**: "Phase 3b absent entirely".

**Actual state** (from
`docs/methodology/preregistration/execution-plan.md`):

> v2.9: Major redesign aligned with preregistration.md v4.5 — replaced
> stranded factorial with sequential OFAT design; ... Phase 2 restructured
> to sequential phases 2a-2e; **Phase 3b absorbed into Phase 2e**

And from `execution-checklist.md`:

> Phase 3b: H9 Diversity (exploratory) — Implicit testing via Phase 3a
> parameter variation; confirmed null result — prompt/parameter diversity
> does not improve consensus

**Phase 3b is not a real phase**. The label refers to H9 Diversity work
that was redirected into Phase 2e (and later into the Phase 3c
exploratory diversity matrix at `results/phase3c-diversity/`).

**Action**: zero. Phase 3b should not be in the gap inventory at all.
A one-line clarification in `documentation-index.md` would help future
auditors not re-discover this phantom gap. Effort: 5 minutes.

### 4.3 Other reported gaps — confirmed real

The 2026-04-22 audit identified five real gaps that remain:

1. Era 1 multi-buffer curves missing for `h8-v2`, `h10`, `h12-v2`
   (only 20 m reported).
2. `h11` proposer-vs-verifier paired test never computed; two
   `UNINTENDED-T1.0` runs never formally archived.
3. No formal cost manifest for h-series or retest runs.
4. Retrospective text run (2026-04-10) has no retrospective pre-launch
   audit.
5. The 2026-05-03 parser-fix recovery surfaced 3 outstanding tile
   recoveries that have not yet been actioned (image-HIGH, text-MIN,
   GS-v2).

These are inherited from the prior audit and are tracked in
`results/documentation-audit/priority-backfill.md`. The plan below
includes them as Tier 1–2 remediation items but does not re-derive them.

---

## 5. Gap inventory against the upgraded spec

This section scores every in-scope doc against the upgraded spec
(§ 3.1 schema for post-run reports; § 3.4 lineage block for results docs;
Document Revision Policy applied to both). Categories:

- **Compliant**: ≥ 90% of required schema sections present, lineage
  block present, Revision Policy banner present.
- **Minor gaps**: 1–2 schema sections missing OR lineage block weak OR
  Revision Policy banner absent.
- **Major gaps**: 3+ schema sections missing, OR no lineage block, OR
  no statistical analysis at all.
- **Missing entirely**: doc does not exist where the schema says it
  should.

### 5.1 `outputs/<run-id>/post_run_report.md` files (26 directories in scope)

| Run directory | post_run_report present? | Compliance | Notes |
|---|:--:|---|---|
| `55maps-image-generalisation` | yes | **Compliant** | Exemplar A; lineage block weak (no explicit Obs cites); banner missing |
| `55maps-text-min-generalisation` | yes | **Compliant** | Same template as A; lineage block weak |
| `55maps-text-high-generalisation` | no (lives at `configs/run-configs/`) | **Minor** | Canonical post-run report at `configs/...`; needs symlink/stub at `outputs/...` per § 3.2 |
| `55maps-text-high-t0.3-generalisation` | no | **Major** | Has `pre_launch_audit.md` but no post-run report at all |
| `55maps-image-generalisation` (image variant) | duplicate of above row | — | — |
| `55maps-generalisation` (retrospective text) | `post_run_report_retrospective.md` exists | **Minor** | Retrospective; flagged as "estimate-only" per audit-summary; needs lineage-block alignment |
| `phase2a` | no | **Missing** | Era 1; statistics live in `results/phase2a-analysis-summary.md` |
| `phase2c` | no | **Missing** | Era 1; statistics in `results/phase2c-track1-image-analysis.md` etc. |
| `phase3a` | no | **Missing** | Era 1; statistics in `results/phase3a-image-matrix/`, `phase3a-text-matrix/` |
| `phase3a-replication` | no | **Missing** | Era 1; statistics in working-notes Obs 140-141 |
| `phase3c` | no | **Missing** | Era 1; statistics in `results/phase3c-diversity/` |
| `phase3d-experiment-e` | no | **Missing** | Era 1; statistics in `results/phase3d-experiment-e-results.md` |
| `phase3d-pilot` | no | **Missing** | Era 1; statistics in `results/phase3d-pilot-results.md` |
| `phase3d-union` | no | **Missing** | Era 1; statistics in `results/phase3d-union-results.md` |
| `h8-v2` | no | **Missing** | Era 1; statistics in `results/h8-v2/analysis_summary.md` (per prior audit) |
| `h10` | no | **Missing** | Era 1; statistics in `results/h10/analysis_summary.md` |
| `h11` | no | **Missing** | Era 1; statistics fragmented across `results/h11-tile-size-results.md`, `results/h11-384-pv-diagnostic/`, `results/h11-384-single-pass-t0-rerun/` |
| `h11/consensus-384-UNINTENDED-T1.0` | no (has README.md only) | **Major** | Per prior audit, never formally archived/excluded |
| `h11/single-pass-384-UNINTENDED-T1.0` | no (has README.md + analysis_summary.md) | **Major** | Same |
| `h12-v2` | no | **Missing** | Era 1; statistics in `results/h12-v2/analysis_summary.md` |
| `retest` | no | **Missing** | Era 1; statistics in `results/retest/retest-production-summary.md` (Exemplar B), per-phase summaries in `results/retest/phase2*/` |
| `test-phase2b` | no | **Missing** | Likely an exploratory dir; possibly archive-eligible |
| `verifier-t-pilot` | no | **Missing** | Statistics in `results/verifier-t-pilot/` (need to confirm) |
| `qgis-dedup-check`, `qgis-sanity-check`, `qgis-wbf-check` | no | **N/A** | QGIS inspection layers, not experimental runs — out of scope for post-run reports |
| `figures` | n/a | **N/A** | Generated figures, not a run |
| `results` | n/a | **N/A** | Empty directory per prior audit |

**Summary**: 4 compliant, 2 minor, 3 major, 14 missing entirely (excluding 5
N/A). Coverage **15%** (4/26) before remediation; ~73% achievable
(19/26) with the templated generator + selective hand-authoring.

### 5.2 `results/**/*.md` paper-citation docs

Sampling 472 docs is impractical; instead score the **anchor docs** that
the paper will cite. Anchor docs are identified by:

- Direct mention in `audit-summary.md`'s deliverable-coverage table
  (the four 55-map runs).
- Cross-references from `documentation-index.md` § "Phase → Document
  Cross-Reference".
- Top-level docs at `results/*.md` (not in subdirectories).
- README files inside `results/<topic>/` directories.

The anchor list (estimated 35–50 docs):

| Doc class | Count | Compliance | Notes |
|---|---:|---|---|
| Top-level `results/phase2*-analysis-*.md` (8 files) | 8 | **Minor** | Statistics present, lineage informal, no Revision banner |
| Top-level `results/phase2*-carry-forward-parameters.md` (5 files) | 5 | **Minor** | Carry-forward purpose is narrow; lineage block would benefit from § 3.4 format |
| `results/phase3a-image-matrix/consensus-analysis-summary.md` | 1 | **Compliant** | Exemplar C; only Revision banner missing |
| `results/phase3a-text-matrix/secondary_effects.md` | 1 | **Compliant** | Sister to C; same standard |
| `results/phase3c-diversity/phase3c-comprehensive-results-report.md` | 1 | **Minor** | Need to confirm compliance |
| `results/phase3d-pilot-results.md` | 1 | **Minor** | Strong content; lineage informal |
| `results/phase3d-experiment-e-results.md` | 1 | **Minor** | Same |
| `results/phase3d-union-results.md` | 1 | **Minor** | Same |
| `results/phase3d-pilot-extensions.md` | 1 | **Minor** | Same |
| `results/phase3d-verifier-experiments-abc.md` | 1 | **Minor** | Same |
| `results/phase3d-high-thinking-results.md` | 1 | **Minor** | Same |
| `results/h11-tile-size-results.md` | 1 | **Minor** | Strong content; lineage informal |
| `results/h11-384-pv-diagnostic/*/threshold_sweep_summary.md` (~50 files) | 50 | **Minor** | Auto-generated per-cell summaries; treat as machine artefacts, not paper-cite docs |
| `results/h10/analysis_summary.md` | 1 | **Minor** | Era 1; multi-buffer curves missing per prior audit |
| `results/retest/retest-production-summary.md` | 1 | **Compliant** | Exemplar B |
| `results/retest/phase2b/analysis_summary.md` | 1 | **Compliant** | Strong; lineage block weak |
| `results/55maps-image-generalisation/**/*.md` (~30 docs) | ~30 | **Mixed** | Detailed statistical sub-analyses; many `_autogen.md` siblings; spot-check needed |
| `results/55maps-text-*/**/*.md` (~12 docs) | ~12 | **Mixed** | Same pattern |
| `results/leaderboard/per-architecture/*.md` (~15 docs) | 15 | **Compliant** (mostly) | Recently authored; structurally consistent |
| `results/paper-tables/*.md` | 4 | **Minor** | Paper-output staging; lineage block would help downstream cite-checking |
| `results/documentation-audit/*.md` (4 docs) | 4 | **Compliant** | Self-aware; banner present |
| `results/README.md` | 1 | **Major** | **Stale** — describes pre-OFAT phase structure that does not exist (factorial strands, phase4-transfer/h6-flash-pro, etc.); needs full rewrite |
| `results/CLAUDE.md`, errata, etc. | — | — | Out of scope (not run docs) |

**Summary** (anchor docs): 0 of ~35–50 anchor docs have a Revision Policy
banner; ~10 are spec-compliant on content; ~25 have minor gaps (mostly
lineage block); 1 is a major gap (`results/README.md` stale). The
50 auto-generated `threshold_sweep_summary.md` files are not anchor docs
and should be excluded from the back-fill scope.

### 5.3 Out-of-scope but worth flagging

- `outputs/h10/evaluation-v2/pool_*/run_*/experiment_intent.md` (~20 files)
  and `outputs/h12-v2/<bucket>/run_*/experiment_intent.md` (~20 files)
  are per-pass intent stubs. They are spec-relevant under the § 3.3
  scope extension but are sub-run artefacts rather than paper-citation
  docs. Treat as **bulk-templated**, not hand-authored.

---

## 6. Remediation tasks (ordered, with effort estimates)

The remediation triage from the brief:

- **Bucket (i)**: spec reconciliation — implement § 3 once approved.
- **Bucket (ii)**: revision-banner back-fill — incidental, on touch.
- **Bucket (iii)**: post-run-report authoring/regeneration — the big
  unknown; templating decision in § 7.

### 6.1 Bucket (i) — spec reconciliation

**Total: 2.5–4 hours**, post-Stage-Gate.

| Task | Effort | Files touched | Type |
|---|--:|---|---|
| Edit `output-directory-standard.md` to add post-run-report schema (§ 3.1) | 1 h | 1 | Trivial back-fill (lift Exemplar A) |
| Add dual-location convention (§ 3.2) | 0.5 h | 1 | Trivial back-fill |
| Add lineage-block format (§ 3.4) | 0.5 h | 1 | Trivial back-fill |
| Refresh `## Status` section (§ 3.5) | 0.25 h | 1 | Trivial back-fill |
| Tighten Document Revision Policy scope in `CLAUDE.md` (§ 3.3) | 0.25 h | 1 | Trivial back-fill |
| Apply Revision Policy banner to `output-directory-standard.md` itself | 0.25 h | 1 | Trivial back-fill |
| Add Phase 2b / 3b clarification to `documentation-index.md` (§ 4.1, § 4.2) | 0.25 h | 1 | Trivial back-fill |
| Rewrite `results/README.md` (§ 5.2) to reflect actual directory state | 1 h | 1 | Needs domain reasoning |

### 6.2 Bucket (ii) — revision-banner back-fill (incidental)

**Total effort scales with downstream work**, not independently estimated.
The CLAUDE.md rule is "back-fill on touch only", so this is not a
dedicated remediation task. Each results-doc edit done as part of
Bucket (iii) carries a 5–10 minute overhead to add the Last revised
banner and Changelog stub. At ~25 anchor docs likely to be touched
during paper writing, that is **2–4 hours** spread across the rest of
the work — not a separate work-stream.

### 6.3 Bucket (iii) — post-run-report authoring / regeneration

This is where the work concentrates. The 14 "missing entirely" rows in
§ 5.1 are the targets. The templated generator approach (§ 7) is the
recommended path; estimates assume it is built.

| Task | Effort | Files touched | Type |
|---|--:|---|---|
| Author `scripts/generate_post_run_report.py` template generator (§ 7) | 4–6 h | 1 new script | Needs domain reasoning (deciding what's auto-extractable vs human-authored) |
| Generate post-run reports for Era 1 runs (14 directories × ~15 min each = ~3.5 h, of which ~2.5 h is human-narrative completion) | 3–5 h | ~14 markdown files | Mixed: trivial extraction + paragraph-level reasoning per run |
| Resolve `outputs/h11/*UNINTENDED-T1.0` (formally archive or formally exclude per prior audit Tier-3 item) | 1 h | ~2 directories moved | Trivial + decision-needed |
| Stub the dual-location post-run reports per § 3.2 | 0.5 h | 4 files | Trivial back-fill |
| Author retrospective pre-launch audit for 2026-04-10 text run (per priority-backfill N3) | 1.5 h | 1 new file | Needs domain reasoning |
| Hand-author cross-reference / lineage block on each Era 1 results-doc anchor (~25 docs × 5–10 min) | 2–4 h | ~25 files | Trivial back-fill once template exists |
| Hand-author `outputs/h11/post_run_report.md` covering the H11 multi-pathway structure (this run is fragmented and resists pure templating) | 2–3 h | 1 file | Needs domain reasoning |
| Spot-check the 50 auto-generated `threshold_sweep_summary.md` files — confirm they should remain as machine artefacts, OR fold a single index-md per directory | 0.5 h | 1 audit doc | Trivial |

**Bucket (iii) total: 14.5–21 hours**, of which ~6–9 hours is domain-reasoning
hand-authoring and ~8.5–12 hours is trivial extraction or templated
back-fill.

### 6.4 Cross-reference graph — incremental

Once the lineage-block format from § 3.4 is canonical and applied to the
anchor docs, the project gets a machine-greppable cross-reference graph
"for free". A one-shot validator script (effort: 1–2 hours) could parse
the lineage blocks and produce a `results/lineage-graph.json` for paper
text-generation work.

**Total Bucket (iii) including lineage validator: 16–23 hours.**

### 6.5 Grand total

| Bucket | Hours |
|---|--:|
| (i) Spec reconciliation | 2.5–4 |
| (ii) Banner back-fill (incidental) | 2–4 |
| (iii) Post-run reports + lineage | 16–23 |
| Phase 2b / 3b labelling clean-up | 0.3 |
| Carryover from prior `priority-backfill.md` Tier 1–2 (multi-buffer curves, h11 paired test, retrospective audit) | 4–7 |
| **Total** | **24.8–38.3 hours** |

The wide band reflects the templating-decision uncertainty resolved in § 7.

---

## 7. Templating-vs-hand-authoring decision

### 7.1 What the existing artefacts can supply

Each Era 1 run directory (`outputs/<run-id>/`) is expected to contain:

- `*.meta.json` (per-pass metadata: model, config, tokens, cost,
  retries, wall-clock, git commit).
- `*.tiles.json` (per-tile success/failure).
- `evaluation/*.json` (F1 / P / R / CIs at multi-buffer).
- Sometimes `cost_manifest.json` (Era 2 only; Era 1 pre-launcher era
  does **not** have these — confirmed by prior audit § "Known gaps").
- The corresponding `results/<phase>/*.md` already contains the
  statistical narrative.

### 7.2 What a generator script can populate

I propose `scripts/generate_post_run_report.py <run-id>` that:

1. Reads `outputs/<run-id>/*.meta.json` (one or more) and aggregates:
   - Front-matter block (run name, completed timestamp, host, launcher
     commit, launcher version, config path).
   - Cost accounting (per-stage, per-pass, token breakdown, unit
     costs) — for Era 2 reads `cost_manifest.json` directly; for Era 1
     reconstructs from `meta["cost_estimate"]["total_cost_usd"]` + token
     fields per pass.
   - Scope (map count, tile count, API call counts).
   - Timeline (UTC events from `meta["execution_timeline"]` if present).
2. Reads `outputs/<run-id>/evaluation/*.json` (or
   `results/<run-id>/evaluation.json`) and aggregates:
   - Top-line F1 / P / R table with bootstrap CIs.
   - D-S corrected metrics if `dawid-skene-results.json` exists.
3. Reads the corresponding `results/<phase>/*.md` and:
   - Extracts the "Headline" or "Executive summary" paragraph as
     candidate copy for the post-run report's headline section.
   - Cross-references the doc path back into the "See also" block.
4. Reads `docs/methodology/preregistration/decisions-log.md` and
   `protocol-errata.md` and:
   - Surfaces any D N or E N entry whose `Affected results` field
     mentions this run-id.
5. Reads `docs/notes/reflections/working-notes.md` and:
   - Greps for `outputs/<run-id>/` mentions; extracts the Obs N IDs and
     line numbers; populates the lineage block.
6. **Marks unfilled fields with explicit `<!-- TODO: domain reasoning -->`
   comments**, so the human author can scan for them. Fields that need
   human authorship:
   - "Operational issues and recoveries" — only the human knows what
     went weird.
   - The narrative "what does this run mean" paragraphs.
   - The reproducibility recipe (the literal bash invocation).
   - The lineage block's preceding/follow-up experiment cells
     (require knowing the experimental graph).

### 7.3 Recommended approach — templating with human completion

**Recommended**: build the generator. Its yield ratio is high (~70% of
each report is auto-extractable), and the template forces structural
consistency across the 14 missing reports, which is exactly what the
spec upgrade aims to enforce.

The alternative — hand-authoring 14 reports from raw artefacts —
would burn ~30 minutes per report on auto-extractable boilerplate
(~7 hours of pure boilerplate work, error-prone), versus the generator's
4–6 hour upfront cost amortised across all 14 + future runs.

The generator should land **after** the spec upgrade is approved, so the
schema it targets is canonical.

### 7.4 What the generator must NOT do

- It must **not** invent statistics. If a metric is not in the JSON, the
  field is left as `<!-- TODO: human-author or N/A -->`.
- It must **not** infer cost when `cost_manifest.json` is absent. It
  reports "no cost manifest" and leaves the section as a stub.
- It must **not** overwrite a hand-authored post-run report if one
  already exists. Add `--check` and `--force` flags; default to safe.
- It must **not** generate `_autogen.md` siblings of paper-citation
  docs. The pattern in `results/phase3a-image-matrix/` (separate
  `consensus-analysis-summary_autogen.md` + hand-authored
  `consensus-analysis-summary.md`) is the right model: the generator
  writes to `post_run_report.md` only when the file does not exist; the
  paper-citation versions in `configs/run-configs/` are stubs per § 3.2.

---

## 8. Cross-reference graph requirement

Per § 3.4, every results doc and every post-run report carries a
`## See also` block in the standard format. Once propagated, this gives:

- **Forward edges**: doc → preceding doc, doc → follow-up doc.
- **Lateral edges**: doc → run output directory, doc → working-notes Obs.
- **Backward edges**: derivable by greping for the doc's own path.

A **lineage-graph.json** can be assembled by a one-pass validator script:

```python
# scripts/validate_lineage_blocks.py
# Reads every results/**.md and outputs/**/post_run_report.md,
# parses the ## See also block, emits results/lineage-graph.json.
# Errors if any anchor doc is missing the block.
```

The validator's emit is the input the paper-writing workflow needs:
"give me every doc that cites Phase 2b" or "give me the lineage from
Phase 2a → Phase 3a-replication", answerable in one query.

**Validator effort**: 1–2 hours, included in Bucket (iii) totals above.

---

## 9. Meta-gap check — what intermediate docs are missing entirely

### 9.1 Programme-level experiments index

**Status**: partially exists, but spread across three documents that
none of them is canonical.

- `docs/methodology/documentation-index.md` § "Phase → Document
  Cross-Reference" is the closest existing table, but it is
  hypothesis-organised (H1 → Phase 2a, etc.), not run-organised.
- `docs/methodology/preregistration/execution-checklist.md` lists
  phase status (started, complete) but not the lead findings.
- `docs/methodology/preregistration/hypothesis-tracking.md` (per the
  index) tracks H1–H15.

**Recommendation**: author a **new** `docs/methodology/experiments-index.md`
(or extend `documentation-index.md`) with a single canonical table:

| Run-id | Phase | Hypothesis | Status | Lead finding (1 line) | post_run_report path | results doc path |
|---|---|---|---|---|---|---|

This is a one-shot table-build (~2 hours) once the post-run reports
exist. It provides the paper-writing workflow with a single
"experiments cited in the paper" master list.

### 9.2 Configs README

`configs/run-configs/README.md` exists (per file listing). Spot-check
that it documents the dual-location convention from § 3.2. If not:
add a one-paragraph stub explaining the canonical-vs-stub pattern.
Effort: 15 minutes.

### 9.3 Results-tree README (currently stale)

`results/README.md` (currently describes pre-OFAT factorial structure
that does not exist) is **the** highest-priority newcomer-orientation
doc and is currently misleading. **Rewrite** is included as a Bucket (i)
task above.

### 9.4 Paper-tables index

`results/paper-tables/` contains 26 files (per prior audit) including
metrics-master CSV/JSON and per-cell breakdowns. There is no `README.md`
indexing them. **Recommendation**: add `results/paper-tables/README.md`
indexing each table with its target paper section. Effort: 1 hour;
included as a discretionary Bucket (iii) item.

### 9.5 Lineage-graph artefact

Already covered in § 8. Listed here for completeness.

### 9.6 New doc types — recommended summary

| New doc | Effort | Priority |
|---|--:|---|
| `docs/methodology/experiments-index.md` | 2 h | High (paper-prep) |
| `results/paper-tables/README.md` | 1 h | Medium |
| `results/lineage-graph.json` (auto-generated) | 1.5 h | Medium |
| Configs dual-location README stub | 0.25 h | Low |

**Meta-gap total: ~4.75 hours**, all of it new authoring.

---

## 10. Stage gates

Two stage gates only — the user has been burned by audits that "kept
finding more holes", so the plan minimises hand-offs.

### Stage Gate 1 — Spec upgrade approval (after § 3)

**Trigger**: user reads § 3 and approves (or amends) the four spec
upgrades.

**Decisions needed at this gate**:

- Approve the post-run-report schema as proposed (§ 3.1)?
- Approve the dual-location stub convention (§ 3.2), or prefer the
  CI-synced alternative?
- Approve the Document Revision Policy scope extension (§ 3.3)?
- Approve the lineage-block format (§ 3.4)?
- Approve the Status section refresh (§ 3.5)?

**Output**: a one-line user response on each of the five. Plan revises if
amendments are made; otherwise propagation work begins.

### Stage Gate 2 — Generator output review (after § 6.3 task 1)

**Trigger**: the generator script lands and produces a sample
`outputs/phase2a/post_run_report.md` (smallest Era 1 run, lowest cost
to iterate on).

**Decisions needed at this gate**:

- Does the generator output meet the schema?
- Are the human-completion `<!-- TODO -->` markers in the right places?
- Are there any structural changes to the schema in light of what the
  generator can/cannot do?

**Output**: green-light to run the generator across the remaining 13 Era 1
directories, OR amend the generator and re-iterate.

**No further stage gates**: the remaining work is mechanical
(template-fill + lineage blocks). User can interrupt at any time but
the plan does not require their pre-approval again.

---

## 11. Risks

### 11.1 Phantom-gap risk (real)

The previous survey claimed "Phase 2b summary missing" and "Phase 3b
absent entirely". Both were wrong: Phase 2b lives at
`results/retest/phase2b/analysis_summary.md`, and Phase 3b was officially
absorbed into Phase 2e. Discovering this took ~5 minutes of file-reading.

**Mitigation**: § 4 of this plan re-verifies every gap claim against
actual filenames and prereg redesign history before scheduling
remediation. Going forward: any new claim of "X is missing" must cite
the absent path explicitly so it can be re-verified in one grep.

### 11.2 Churn risk from over-eager back-fill (real)

The Document Revision Policy says "back-fill on touch only". A bulk
back-fill of Last revised banners across all 472 results docs would
violate this rule, generate hundreds of trivial commits, and
desensitise the user to the banner's signalling value (the banner is
useful precisely because most docs don't have one until they get
revised).

**Mitigation**: Bucket (ii) is explicitly scoped as incidental work, not
a dedicated work-stream. The plan does not budget hours for "go through
results/ and add banners".

### 11.3 Scope creep (real)

Once the upgraded spec is canonical, every `outputs/**/experiment_intent.md`
file (~50 of them) becomes "in scope" for the Revision Policy. The
50 auto-generated `threshold_sweep_summary.md` files arguably become
in scope too. If treated as anchor docs, the back-fill scope balloons
from ~25 files to ~100+.

**Mitigation**: § 5.1 explicitly classifies QGIS, figures, empty-`results`,
and `outputs/<run-id>/proposer/<config>/run_N/experiment_intent.md` as
out-of-scope-for-anchor-doc-treatment. They are spec-relevant
(they have to follow the file naming convention) but they are
**not** required to carry a Revision Policy banner unless touched.

### 11.4 Generator overreach (medium)

A templated generator that infers too much (e.g., guesses cost from a
single .meta.json when there are five passes) will produce
plausible-but-wrong reports. Era 1 runs are exactly the population most
at risk because they predate `cost_manifest.json`.

**Mitigation**: § 7.4 is explicit — the generator must leave a stub,
not invent a number. The user reviews the first generator output at
Stage Gate 2 specifically to catch this class of failure.

### 11.5 Prior-audit drift (medium)

`results/documentation-audit/audit-summary.md` (2026-04-22) and
`priority-backfill.md` (with 2026-05-03 annotations) capture the prior
state. The 2026-05-02/03 recovery campaign and the 3 outstanding
parser-fix recoveries (image-HIGH, text-MIN, GS-v2) postdate the
priority-backfill plan. Some Tier 1–2 items may have been silently
closed by intervening work.

**Mitigation**: before starting Bucket (iii), re-read
`priority-backfill.md` and confirm each Tier 1–2 item is still open.
The recovery campaign closure documents (`commits 731466d8 → e07dae37`)
should be the diff-target.

### 11.6 Two-audience tension (low — already resolved)

The brief is explicit: paper-source priority wins when it conflicts with
newcomer-orientation. The schema in § 3.1 puts citation-ready findings
first (top-line F1, cost, scope) and narrative scaffolding second
(timeline, operational issues, see-also). No mitigation needed; the
ordering is already correct.

---

## 12. Open questions for the user (to resolve at Stage Gate 1)

1. Is the dual-location stub convention (§ 3.2) acceptable, or do you
   prefer a CI-synced alternative? Stub is recommended because it
   removes the drift risk; the CI-sync alternative requires writing
   and maintaining a lint hook.
2. Is the lineage-block format (§ 3.4) at the right level of detail, or
   would you prefer a tighter / looser schema?
3. Should the templated generator (§ 7) target **all 14** missing Era 1
   reports, or only the **paper-cited** subset (likely 8–10)? The
   answer affects Bucket (iii) total by ~3–5 hours.
4. The Phase 2b labelling clean-up (§ 4.1) and Phase 3b clarification
   (§ 4.2) are 20-minute tasks. Schedule them in this remediation
   pass, or defer them as docstring touch-ups for a later session?
5. Is the recommended timing of meta-gap work (§ 9.1 experiments-index)
   "after generator + lineage propagation" correct, or is it more
   urgent than that for paper-prep?

---

## Changelog

### 2026-05-28 — Phase 0 execution complete; corrections to original framing

**Refresh trigger**: Phase 0 of the audit (Bucket (i) — spec
reconciliation) was executed 2026-05-26 across 8 sequential edits under
the cadence "propose / approve / commit / push, one at a time". Stage
Gate 1 was approved by the user 2026-05-26 with the answers in § 12
locked. Three internal-contradiction / accuracy issues with the
original plan were caught during execution and are recorded here so
future readers do not re-derive them.

**Phase 0 commit ledger** (in order):

| Edit | Section | Commit | Touched |
|---|---|---|---|
| 1 | `## Post-Run Report Schema` codified | `c611c573` | `output-directory-standard.md` |
| 2 | Dual-location convention codified | `1aaece11` | `output-directory-standard.md` |
| 3 | `## Cross-reference / Lineage Block` codified (one canonical heading `## See also`; affirmative `None`; no line-number anchors) | `593d60f3` | `output-directory-standard.md` |
| 4 | `## Status` refreshed (verified-against-filesystem) | `d9cc2501` | `output-directory-standard.md` |
| 5 | `## Documents in Revision Policy Scope` codified | `c30ce58a` | `output-directory-standard.md`, `CLAUDE.md` |
| 6 | Revision Policy banner + Changelog applied to spec doc | `ee0d7aa1` | `output-directory-standard.md` |
| 7 | Phase 2b / 3b clarifications | `0e697c77` | `documentation-index.md` |
| 8 | `results/README.md` full rewrite | `2ef592c8` | `results/README.md` |

**Corrections to the original plan** (issues caught during execution):

| Issue | Original plan claim | Verified reality | Resolution |
|---|---|---|---|
| § 3.2 framing | "The four 55-map runs each have a post-run report at two paths." | Only 2 of 4 are dual-located: `55maps-image-generalisation` and `55maps-text-min-generalisation`. `55maps-text-high-generalisation` exists only at `configs/run-configs/...`; `55maps-text-high-t0.3-generalisation` exists at neither (has `pre_launch_audit.md` + `experiment_intent.md` only). The retrospective text run uses divergent filename suffixes across sides. § 5.1 of this plan actually knew about the asymmetry (it flagged `55maps-text-high-generalisation` as "Minor" and `55maps-text-high-t0.3-` as "Major") — § 3.2 just oversold the universality of dual-location. | The spec wording in commit `1aaece11` says "when this duplication exists" rather than asserting universality. The asymmetric runs are now back-fill scope tracked under Bucket (iii) / § 6.3. |
| § 3.3 vs § 6.1 row 5 internal contradiction | § 3.3 said: "No content change needed to CLAUDE.md... but the spec should enumerate the candidate paths explicitly." § 6.1 row 5 said: "Tighten Document Revision Policy scope in CLAUDE.md (§ 3.3) \| 0.25 h \| **1 file** \| Trivial back-fill" — implying the edit IS to CLAUDE.md. | The two statements contradict on which file the edit lands in. | Resolved in commit `c30ce58a` (Edit 5) by touching both files: the authoritative enumeration is in the spec doc (per § 3.3's clearer reasoning); CLAUDE.md cross-references the spec and lists the paths inline so Claude doesn't need to fetch the spec for routine revision checks. |
| `experiment_intent.md` count | § 3.3 said "~50 of these exist". | 139 files exist (verified via `find outputs -name experiment_intent.md \| wc -l` pre-commit on 2026-05-26). | The spec doc's Documents in Revision Policy Scope table records the correct count (139). The back-fill cost estimate in Bucket (iii) is conservatively under-counted; if the project chooses to back-fill experiment_intent banners en masse the effort doubles vs. the original plan's estimate. The back-fill-on-touch rule means this does not become a separate work stream. |

**Additional discoveries during execution** (not corrections — additive
findings):

- The Document Revision Policy as originally written did not include
  `docs/methodology/*.md` spec docs in scope. The audit plan's § 6.1
  row 6 asked for the banner to be applied to
  `output-directory-standard.md` anyway. Resolved as a voluntary
  application (commit `ee0d7aa1`) rather than extending canonical
  scope to all methodology spec docs — keeps the policy commitment
  narrow.
- Edit 3 (`## Cross-reference / Lineage Block`) made three deliberate
  deviations from § 3.4's literal wording, all of which strengthen
  the convention: (a) one canonical heading instead of "or `## Lineage`"
  to keep grep tooling unambiguous; (b) affirmative `None` required
  for inapplicable categories (distinguishes "no preceding experiment
  exists" from "author forgot"); (c) no line-number anchors on
  working-notes Obs references (working-notes.md grows daily; line
  numbers drift).
- Edit 8 (results/README.md rewrite) retired "Era 1 / Era 2 / Era 3"
  terminology entirely. The shorthand was overloaded between
  OFAT-vs-generalisation and tile-pool senses. Descriptive labels are
  used in the new README. Empirical mapping of gold-standard
  sub-directories to their evaluation tile pool (~60-tile subset vs.
  full 4-map minus 20-tile calibration) is deferred — tracked as
  TaskList follow-up.

**What did NOT change in this revision**: the plan's substantive
recommendations, effort estimates, and Bucket (i)-(iii) structure are
unchanged. The Stage Gate 1 approval covered the plan as written; the
corrections above are accuracy notes, not scope shifts.

### 2026-05-06 — Original publication

Plan authored by Claude Code in response to user request for a
paper-writing-readiness documentation audit. Drew on:

- Canonical specs at `docs/methodology/output-directory-standard.md`,
  `docs/methodology/documentation-protocol.md`, and the Document
  Revision Policy section of `/home/shawn/Code/map-reader-llm/CLAUDE.md`.
- Prior audit pass at `results/documentation-audit/audit-summary.md`
  (2026-04-22) and `priority-backfill.md` (2026-05-03 revision).
- Direct file inspection of the four 55-map post-run reports
  (Exemplar A), `retest-production-summary.md` (Exemplar B), and
  `phase3a-image-matrix/consensus-analysis-summary.md` (Exemplar C).
- Verification that Phase 2b is documented at
  `results/retest/phase2b/analysis_summary.md` and Phase 3b was
  officially absorbed into Phase 2e (`execution-plan.md` v2.9 redesign).

No prior version to diff against (this is the original publication).
Future revisions will record the trigger, before/after numerical
deltas where applicable, and the commit hash that lands the change.
