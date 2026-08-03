# Output Directory Standard

> **Last revised**: 2026-08-03 (governance: `docs/methodology/reports/**`
> split-by-citation rule added to the Revision-Policy scope section —
> PI ruling closing the gap that directory sat in). See
> [§ Changelog](#changelog) for revision history.

## Purpose

This document defines the standard structure for experimental outputs.
Every directory under `outputs/` must be immediately legible to someone
browsing the repository on GitHub — no tribal knowledge required.

## Status

- **Current state**: The directory structure reflects organic growth
  across 10+ experimental phases. A documentation audit and remediation
  campaign is in progress (see
  `planning/documentation-audit-plan.md`) to align existing artefacts
  to this spec. The Post-Run Report Schema and Cross-reference / Lineage
  Block sections below were codified as part of that campaign; Era 1
  back-fill of `outputs/<run-id>/post_run_report.md` and lineage blocks
  is staged work (audit plan § 6).
- **Target**: standardised layout with consistent naming, the schemas
  defined below applied across all run directories, and explicit
  gitignore policy.
- **Tracking state for `outputs/h11/pv-diag-384/`**: structurally
  important artefacts (geojsons, JSON metadata, manifests) are tracked
  in git; bulk log files (`**/*.log`) are gitignored. The directory
  exists on both zbook and sapphire. The earlier "only exists on
  sapphire" status is obsolete.

## Artefact Types

Every pipeline in this project produces a subset of these artefact types:

| Artefact | Extension | Typical size | Track in git? | Description |
|----------|-----------|-------------|---------------|-------------|
| Detections | `.geojson` | 300–600 KB | **Yes** | GeoJSON FeatureCollection of detected symbols |
| Execution metadata | `.meta.json` | 450 KB–1 MB | **Yes** | Model, config, cost, usage stats, per-tile telemetry |
| Tile status | `.tiles.json` | 20 KB | **Yes** | Per-tile processing success/failure |
| Candidate manifest | `candidate_manifest.json` | ~290 KB | **Yes** | Maps candidate IDs to precise coordinates |
| Probabilities | `probabilities.json` | ~50 KB | **Yes** | Aggregated verification probabilities per candidate |
| Verified detections | `verified-*.geojson` | 500–600 KB | **Yes** | Detections enriched with verifier scores and reasoning |
| Threshold sweep | `threshold_sweep.json` | ~20 KB | **Yes** | Optimal threshold analysis with bootstrap CIs |
| Crop images | `crops/*.png` | ~24 MB total | **No** | Raster crops around candidates — regenerable |
| Batch working files | `batch_working/*.jsonl` | 50–80 MB/run | **No** | Raw API request/response payloads — regenerable |
| Logs | `*.log` | Varies | **No** | Runtime logs — ephemeral |

## Gitignore Policy

The following patterns must be gitignored globally (not per-directory):

```text
# Large regenerable artefacts
outputs/**/batch_working/
outputs/**/crops/
outputs/**/*.log
outputs/.active_files.*
```

Everything else under `outputs/` should be tracked. If a directory is
temporarily too large to commit, add a **specific** gitignore entry with
a comment explaining why, and create a TODO to resolve it.

## Proposed Directory Structure

```text
outputs/
├── README.md                              # This file (high-level map)
│
├── phase2a/                               # Phase 2a: calibration runs
│   ├── {condition}/                       # e.g., "brief-text", "image-only"
│   │   └── run_{N}/
│   │       ├── detections_*.geojson
│   │       ├── detections_*.meta.json
│   │       └── detections_*.tiles.json
│
├── h11/                                   # H11: tile size comparison + PV
│   ├── n1-outstanding-384/                # Single-pass proposer (N=1)
│   │   └── {condition}/run_{N}/           # e.g., "pro-text-high-t0"
│   │
│   ├── consensus-384/                     # 30-pass consensus proposer
│   │   └── 384/run_{N}/
│   │
│   ├── proposer-verifier-384/             # PV pipeline (N=1 proposer)
│   │   ├── proposer/                      # Raw proposer detections
│   │   ├── candidates/                    # Manifest + crops
│   │   │   ├── candidate_manifest.json
│   │   │   └── crops/                     # GITIGNORED
│   │   └── verified-{variant}.geojson     # Verifier outputs
│   │
│   └── pv-diag-384/                       # PV pipeline (consensus proposer)
│       └── verified/
│           └── {architecture}/            # e.g., "flash-high-text-4of5"
│               ├── candidate_manifest.json
│               ├── probabilities.json
│               └── crops/                 # GITIGNORED
│
├── production/                            # NEW: 55-map production run
│   ├── README.md                          # Describes run config and purpose
│   ├── proposer/
│   │   └── run_{N}/
│   │       ├── detections.geojson
│   │       ├── detections.meta.json
│   │       └── detections.tiles.json
│   ├── consensus/
│   │   └── voting-results.geojson
│   ├── verified/
│   │   ├── candidate_manifest.json
│   │   ├── probabilities.json
│   │   └── verified.geojson
│   └── evaluation/
│       ├── threshold_sweep.json
│       └── per-map-metrics.json
│
├── qgis-sanity-check/                     # QGIS inspection layers
│   ├── qgis_tp.geojson
│   ├── qgis_fp.geojson
│   ├── qgis_fn.geojson
│   └── sanity_check_summary.json
│
└── figures/                               # Generated figures
```

## Naming Conventions

- **Directories**: lowercase with hyphens (`proposer-verifier-384`,
  not `ProposerVerifier384`)
- **Run directories**: `run_{N}` with zero-padded numbers where
  practical (`run_01`, `run_02`)
- **Condition names**: `{model}-{thinking}-{modality}-{temperature}`
  (e.g., `flash-high-text-t0`, `pro-minimal-image-t07`)
- **Verified files**: `verified-{verifier-variant}.geojson`
  (e.g., `verified-adversarial-text.geojson`)

## Post-Run Report Schema

Every `outputs/<run-id>/` directory representing a completed experimental
run must contain a `post_run_report.md` conforming to the schema below.
The schema is lifted from the four 55-map generalisation reports (two
under `outputs/`, one config-side only, one retrospective with a divergent
filename suffix — see § Dual-location convention; Exemplar A:
`outputs/55maps-image-generalisation/post_run_report.md`), which were
the first to instantiate this template and remain the canonical reference
for new authors.

**Applies to**: experimental runs (proposer / verifier / consensus
pipelines, scaling studies, threshold sweeps where the sweep itself was
the experiment).

**Does not apply to**: QGIS inspection layers (`qgis-dedup-check`,
`qgis-sanity-check`, `qgis-wbf-check`), generated figure directories
(`figures/`), or exploratory directories explicitly archived under
`archive/`.

### Required sections, in order

1. **Front-matter block** (REQUIRED) — run name; completed timestamp
   (UTC); host; launcher commit (40-char SHA); launcher version; config
   path; pre-launch audit path (if applicable).
2. **Top-line result** (REQUIRED) — F1 / P / R at the project's
   standard buffer radii (20/30/40/50 m) with bootstrap 95% CIs (1,000
   iterations, seed 42, tile-level resampling). Bolded operating point
   `(vote_t, prob_t)`.
3. **Corrected-for-incompleteness result** (REQUIRED if Dawid–Skene
   applicable) — method × F1 / P / R table; explicit Δ F1 attribution.
4. **Cost accounting** (REQUIRED) — overall total + budget-band check;
   by stage (proposer / verifier / consensus / extract / evaluate); per
   pass (workers, wall-clock, tiles OK/failed, retries, thinking tokens);
   token breakdown (input billed, input cached, output, thinking, total);
   unit costs (per tile, per map, per detection, per reference mound).
5. **Per-map extrema** (REQUIRED if multi-map run) — top-5 / bottom-5 by
   cost; mean cost-per-tile dispersion comment.
6. **Scope** (REQUIRED) — map count; tile count; API call counts
   (success / fail); reference mound count; candidate count; final-
   detection count.
7. **Timeline** (REQUIRED if material) — launch → per-stage → complete
   (UTC).
8. **Operational issues and recoveries** (CONDITIONAL — include only if
   there were any).
9. **Reproducibility recipe** (REQUIRED) — literal bash block; expected
   cost ± tolerance; expected runtime.
10. **Artefacts for the paper** (REQUIRED) — file → purpose table for
    tracked artefacts; list of large intermediate artefacts available in
    the companion data release.
11. **See also / lineage block** (REQUIRED — see "Cross-reference /
    lineage block" section below).
12. **Changelog** (REQUIRED on revision — see the Document Revision
    Policy in `/CLAUDE.md`).

### Worked exemplar

Authors back-filling a post-run report for an Era 1 run should open
`outputs/55maps-image-generalisation/post_run_report.md` alongside their
draft and mirror its section structure. Numeric formatting, table
conventions, and prose register are all canonical there.

### Dual-location convention

Some runs have a post-run report at **two** paths:

- `outputs/<run-id>/post_run_report.md` — alongside the run artefacts
  (model outputs, evaluation JSON, cost manifests).
- `configs/run-configs/<run-id>_post_run_report.md` — alongside the
  YAML run config.

When this duplication exists, the two copies drift inevitably unless one
is canonical. The convention is:

- The **`outputs/<run-id>/post_run_report.md` copy is canonical**. All
  edits land there.
- The `configs/run-configs/<run-id>_post_run_report.md` copy, when
  present, must be replaced with a **one-line stub**:

  ```markdown
  # <run-name> — post-run report

  Canonical version: [`outputs/<run-id>/post_run_report.md`](../../outputs/<run-id>/post_run_report.md)
  ```

- New runs must not author both copies. Author the canonical at
  `outputs/...` and (optionally) create the stub at `configs/...` only
  if a config-side breadcrumb is wanted.

**Current state (2026-05-26)**: 2 of the 4 55-map runs are dual-located
(`55maps-image-generalisation`, `55maps-text-min-generalisation`). The
others are asymmetric — `55maps-text-high-generalisation` exists only at
`configs/...`; `55maps-text-high-t0.3-generalisation` exists at neither;
the retrospective text run uses divergent filename suffixes across sides
(`post_run_report_retrospective.md` at `outputs/...`,
`..._retrospective_post_run_report.md` at `configs/...`). Aligning these
to the convention is back-fill work tracked in
`planning/documentation-audit-plan.md` § 5.1 and § 6.3 (Bucket iii); it
is **not** a spec violation in the present moment, but the spec is the
target state once back-fill lands.

### Templated generator

A generator script (`scripts/generate_post_run_report.py`) is the
recommended starting point for Era 1 back-fills: it auto-populates the
deterministic sections (front-matter, cost accounting, scope, timeline)
from `*.meta.json` and `evaluation/*.json`, leaving narrative sections
(operational issues, lineage prose) marked with `<!-- TODO: human-author -->`
for completion. See the documentation audit plan, § 7, for the
templating-vs-hand-authoring rationale.

## Cross-reference / Lineage Block

Every results document (`results/**.md` anchor docs — see "anchor doc"
definition in `planning/documentation-audit-plan.md` § 5.2) and every
post-run report (`outputs/<run-id>/post_run_report.md`) must end with a
`## See also` block in the structured format below.

This codifies a new canonical format. Current best-in-class docs have
inconsistent inline pointers (a `**Cross-reference**` bold tag in
`results/phase3a-image-matrix/consensus-analysis-summary.md`; mixed
inline prose and a numbered `## 13. Observation cross-references` H2 in
`results/retest/retest-production-summary.md`; nothing at all in the
55-map post-run reports). The structured `## See also` format replaces
these patterns going forward.

### Required format

```markdown
## See also

- **Preceding experiment(s)**: `results/<phase-X>/<doc>.md` — one-line
  gloss of what carried forward into this run.
- **Follow-up experiment(s)**: `results/<phase-Y>/<doc>.md` — one-line
  gloss of what this run handed off.
- **Run output directory**: `outputs/<run-id>/` (link the directory; or
  list specific artefact paths if the run is fragmented across
  subdirectories).
- **Working-notes Observations**: Obs N — short title (one bullet per
  Obs; omit line numbers, they drift).
- **Decisions / Errata**: D N or E N — one-line gloss (refer to
  `docs/methodology/preregistration/decisions-log.md` and
  `protocol-errata.md`).
```

### Conventions

- **Heading**: always `## See also`. One canonical form; agents and
  grep tools depend on it. Do not use `## Lineage`, `## Cross-reference`,
  or other variants.
- **Position**: last section of the document, immediately before
  `## Changelog` (when present per the Document Revision Policy).
- **Affirmative `None`**: every bullet must be present. If a category
  genuinely does not apply (e.g., the first run in a phase has no
  preceding experiment), write `**Preceding experiment(s)**: None.`
  rather than omitting the bullet. Affirmative `None` distinguishes
  "no preceding experiment exists" from "author forgot to record one";
  the omission-is-signal alternative loses that distinction.
- **Working-notes Observations**: anchor by `Obs N — title` only. Line
  numbers drift as the working notes grow.
- **Multiple entries**: when more than one preceding or follow-up
  experiment exists, repeat the bullet:

  ```markdown
  - **Preceding experiment(s)**: `results/phase2a-...md` — gloss.
  - **Preceding experiment(s)**: `results/phase2c-...md` — gloss.
  ```

### Rationale

Once this format is propagated across the anchor-doc set (Phase 4 of
the audit remediation), the project gets a machine-greppable lineage
graph "for free". A validator script can parse the `## See also` blocks
to produce `results/lineage-graph.json`, supporting paper-writing
cross-reference workflows and consistency checks.

## Documents in Revision Policy Scope

The Document Revision Policy (defined in `/CLAUDE.md` § "Document
Revision Policy") applies to the document classes enumerated below. The
CLAUDE.md wording covers these via "analogous post-run summary docs
under `outputs/`"; this section is the authoritative enumeration —
CLAUDE.md cross-references back here for the canonical path list.

| Path pattern | Class | Count (2026-05-26) | Count (post-audit target) | Compliance |
|---|---|---:|---:|---|
| `results/**.md` (anchor docs only — see audit plan § 5.2) | Paper-citation working docs | ~35–50 | ~35–50 | Mostly non-compliant; back-fill on touch |
| `reports/**.md` | Internal reports authored by Claude Code | varies | varies | Mostly compliant |
| `outputs/**/post_run_report.md` | Per-run post-run reports | 2 + 1 retrospective | ~22 | 2 compliant; 15 missing entirely; back-fill in audit Phase 3 |
| `outputs/**/experiment_intent.md` | Per-pass / per-run intent files | 139 | 139 | Informal; in scope going forward |
| `outputs/**/evaluation.md` | Per-run evaluation summaries | 11 | 11 | Informal; in scope going forward |
| `outputs/**/pre_launch_audit.md` | audit-config skill outputs | 1 (`55maps-text-high-t0.3-generalisation`) | varies | In scope going forward |

**Back-fill rule**: per CLAUDE.md, "back-fill on touch only" — when you
edit one of these documents, attach the banner + Changelog stub. Do not
bulk back-fill unchanged documents. The "Count (post-audit target)"
column is the expected file count once Phase 3 authoring lands, not a
compliance target; banner compliance follows the back-fill-on-touch
rule.

**Out of scope**: `docs/notes/reflections/*.md` (append-only historical
records), `docs/methodology/preregistration/*.md` (governed separately
by the preregistration process), `docs/methodology/research/*.md`
(third-party Deep Research reports), and `archive/**` (frozen state).

**`docs/methodology/reports/**` — split by citation (PI ruling
2026-08-03, closing the governance gap this directory sat in)**: scope
follows CONSUMPTION, not location. A file in this directory that the
lodged registration (or, in future, paper text) cites as authoritative
is IN full Revision-Policy scope — currently exactly one,
`docs/methodology/reports/tile-selection-methodology.md`
(`preregistration.md` § 8.6), whose header flags this status. The
remaining files are frozen planning-stage records and are explicitly
OUT of scope, under the lighter convention practised 2026-08-02: never
rewrite their bodies to current truth (that falsifies the planning
record); on supersession, add a dated `**STALE — …**` banner under the
H1 naming the superseding design with a line-anchored citation, an
explicit do-not-cite directive, and a `Banner added <date>` line. A
new citation of any file here moves it into full scope; the C4 fleet's
extraction of registration citations is the drift check.

## Immediate TODOs

### 1. Track pv-diag-384 in git (requires sapphire access)

The top-tier results (F1=0.89) live in `outputs/h11/pv-diag-384/` on
sapphire. This directory is currently gitignored.

Steps:

1. Remove `outputs/h11/pv-diag-384/` from `.gitignore`
2. Ensure global patterns cover regenerable artefacts:

   ```text
   outputs/**/batch_working/
   outputs/**/crops/
   ```

3. Commit the lightweight outputs (verified GeoJSONs, probabilities,
   manifests, meta files)
4. Verify total committed size is reasonable (~5–15 MB expected)

### 2. Extract consensus-384 detections

The `outputs/h11/consensus-384/` directory has 30 runs of
`batch_working/` JSONL (2.3 GB) but no extracted detection GeoJSONs.
The extraction was done directly into `pv-diag-384/` on sapphire.

Either:

- Parse the JSONL files to extract GeoJSONs (preserves full provenance)
- Or accept that `pv-diag-384/` is the canonical processed output

### 3. Standardise gitignore

Replace the current per-directory gitignore entries with global
patterns. Current `.gitignore` has:

```text
outputs/h11/pv-diag-256/
outputs/h11/pv-diag-384/
outputs/pv/
outputs/retest/
```

These should become:

```text
# Large regenerable artefacts (global)
outputs/**/batch_working/
outputs/**/crops/
outputs/**/*.log
```

Plus any remaining specific entries with explanatory comments.

### 4. Production run output structure

Before running the 55-map production run, create the `outputs/production/`
directory with a README documenting the run configuration, cost, and
the ground truth filtering applied (hairy-only symbols from student data).

## Changelog

### 2026-08-03 — Governance: reports-directory split-by-citation rule (Session 125, D3)

**Trigger**: the C4 wave-4 triage bannered/corrected three
`docs/methodology/reports/` files and found the directory in neither
the scope list nor the out-of-scope list (escalation item 5 of
`reports/verification/c4-triage/mismatch-triage-2026-08-02-wave4.json`).
PI ruling after a grounded cost-benefit pass (6 files, one
prereg-cited, zero paper/results references): scope follows
consumption. The prereg-cited `tile-selection-methodology.md` enters
full scope; the five frozen planning records are explicitly out of
scope with the dated-STALE-banner-on-supersession convention; a new
citation moves a file into scope, with the C4 registration-citation
extraction as the drift check. No figures changed.

### 2026-08-02 — C4 wave-3 triage corrections (Session 125)

**Trigger**: the Phase-3 C4 wave-3 recompute over this document's dated
censuses (`reports/verification/c4-triage/mismatch-triage-2026-08-02.json`,
families `006-outdir-doc-defect-at-era`, `006-outdir-cross-location-census`,
and `006-outdir-pv-diag-machine-scope`), each adjudication confirmed by a
ruling-11 blind re-derivation before any edit.

| Claim | Before | After |
|---|---|---|
| Revision-Policy-scope table, `outputs/**/post_run_report.md` count (2026-05-26) | 4 + 1 retrospective | 2 + 1 retrospective |
| Same row, compliance cell | 4 compliant; 14 missing entirely | 2 compliant; 15 missing entirely |
| 2026-05-26 changelog, Status "After" cell | quoted census figures as if they were doc text | quotes the actual qualitative wording; census marked as working measurement |

The "4" was never true: the tracked count was 2 at the 2026-05-26 era
commit (`c30ce58aa3`) and only three `post_run_report*.md` files have ever
existed under `outputs/` in the entire history. The figure traces to
`planning/documentation-audit-plan.md` § 3.2's over-generalisation ("all
four runs dual-located"), recorded as an erratum the same session (plan
line 965) but never back-propagated here — the document's own
§ Dual-location convention, committed 22 minutes earlier, carries the
correct enumeration. The compliance tally now matches audit plan § 5.1
(2 Compliant, 15 Missing). The 2026-05-26 changelog "After" cell had
attributed the 1,497 / 48,666 census to the Status body text, which was
always qualitative (`git show d9cc2501`) — the figures were the author's
working census. The dated experiment_intent.md (139) and evaluation.md
(11) censuses were verified era-exact and are deliberately unchanged
(snapshot statements; current tracked counts 174 / 46 reflect monotonic
post-era growth). The "Count (post-audit target)" cells are flagged as
stale in a stronger sense and left for a deliberate rework of that
column's semantics. Corrected in commit noted in git history for this
date.

### 2026-05-26 — Phase 0 of documentation audit

**Refresh trigger**: Stage Gate 1 approval of
`planning/documentation-audit-plan.md` (2026-05-26). Codified four
previously unwritten conventions and refreshed one stale status note.

**Changes**:

| Section | Change | Commit |
|---|---|---|
| `## Post-Run Report Schema` (new) | Codified the 12-section post-run-report template lifted from Exemplar A (`outputs/55maps-image-generalisation/post_run_report.md`); added applicability carve-out, worked-exemplar pointer, templated-generator forward reference. Bootstrap CI params verified against Exemplar A lines 19, 26 pre-commit. | `c611c573` |
| `## Post-Run Report Schema → ### Dual-location convention` (new) | Codified outputs/-canonical, configs/-stub rule for runs with duplicated reports; added dated snapshot of asymmetric reality (2/4 dual-located, 1 configs-only, 1 neither, 1 retrospective with divergent suffixes). | `1aaece11` |
| `## Cross-reference / Lineage Block` (new) | New canonical `## See also` format for results docs and post-run reports; affirmative `None` required for inapplicable categories; no line-number anchors for working-notes Obs (drift-prone). | `593d60f3` |
| `## Status` (refreshed) | Replaced stale "outputs/h11/pv-diag-384/ is gitignored and only on sapphire" with a qualitative verified-against-filesystem replacement (working census at the time, not doc text: 1,497 of 48,666 files tracked). Dropped stale "F1=0.89" parenthetical. | `d9cc2501` |
| `## Documents in Revision Policy Scope` (new) | Authoritative enumeration of the six in-scope path patterns with 2026-05-26 file counts (139 experiment_intent, 11 evaluation, 1 pre_launch_audit, etc.) + post-audit target counts + compliance notes. CLAUDE.md cross-references back. | `c30ce58a` |

**Before → after table for numerical claims that moved**:

| Claim | Before | After |
|---|---|---|
| `outputs/h11/pv-diag-384/` tracking state | "gitignored, only exists on sapphire" | "structurally important artefacts (geojsons, JSON metadata, manifests) are tracked in git; bulk log files (`**/*.log`) are gitignored. The directory exists on both zbook and sapphire." (supporting working census, never doc text: 1,497 of 48,666 files tracked) |
| Stale F1 reference | "top-tier F1=0.89 results" | Parenthetical dropped (spec docs shouldn't carry canonical headline numbers) |

**What did NOT change**:

- The doc's purpose ("standard structure for experimental outputs").
- The Artefact Types table.
- The Gitignore Policy section.
- The Proposed Directory Structure tree.
- The Naming Conventions section.
- The Immediate TODOs section (items 1–4 still pending).

**Open items flagged during this revision** (to be addressed in
`planning/documentation-audit-plan.md` Changelog after Phase 0 lands —
TaskList #13):

- § 3.2 of the audit plan assumed all four 55-map runs were
  dual-located; actually 2 are.
- § 3.3 vs § 6.1 internal contradiction about which file Edit 5 touches
  (resolved: both, per § 3.3's reasoning).
- `experiment_intent.md` count: plan said ~50; actual 139.

### 2026-04-08 — Original publication

Spec doc authored at commit `287123ca` as part of the project's first
attempt to standardise the `outputs/` directory layout. Defined the
directory structure, artefact types, gitignore policy, naming
conventions, and immediate-TODO list for further alignment work.
Schema and convention sections that codify implicit templates
(Post-Run Report Schema, Dual-location convention, Cross-reference /
Lineage Block, Documents in Revision Policy Scope) were not present in
the original publication; they were added in the 2026-05-26 revision
above.
