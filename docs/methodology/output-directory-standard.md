# Output Directory Standard

> **Last revised**: 2026-09-13 (three passes the same day. Items 11a and
> 11b of the documentation-foundation checklist: the generated-file
> registry rebuilt over `outputs/` as well as `results/` and `reports/`
> (3,619 files, 0 unattributed) and extended to record the
> generated-projections ruling's three obligations per document, so the
> compliance table's "neither regime" claim is now a query rather than an
> audit note; the **six** generated documents in neither regime are
> **closed to 0** — the five register renderings verified and guarded, and
> the Era-2 board's two tables plus the three generated 55-map boards given
> a banner, a source-commit stamp and a tested `--check`. Earlier the same
> day — items 3–5: the compliance table recounted to
> today on every row and the generated-projections ruling's reach
> recorded — `evaluation.md` reclassified as generated, a denominator note
> on the then-stale generated-file registry. Item 1: post-run reports
> back-filled for all 41 registered runs — 39 as generated projections, 2
> hand-authored — and that row's count and compliance cell corrected.
> Prior 2026-09-11: generated projections carry machine provenance, not a
> hand changelog — PI ruling, Session 153; prior 2026-08-03:
> `docs/methodology/reports/**` split-by-citation rule). See
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

| Path pattern | Class | Count (2026-09-13) | Count (2026-05-26) | Compliance on 2026-09-13 |
|---|---|---:|---:|---|
| `results/**.md` (anchor docs only — see audit plan § 5.2) | Paper-citation working docs | **2,864** files, of which **80** carry a revision banner | ~35–50 (anchor docs) | Compliant on the classes that carry today's results — **17 of 17** `findings.md` and **4 of 4** uplift-supplement documents have banner + changelog. The 2,864 is the whole tree, most of it generated per-cell output, so it is not the denominator; see the registry note below |
| `reports/**.md` | Internal reports authored by Claude Code | **101** files, **62** bannered | varies | Compliant on current work: **18 of 18** reports dated 2026-09-11/12/13 have banner + changelog. The 39 unbannered are older reports under back-fill-on-touch |
| `outputs/**/post_run_report.md` | Per-run post-run reports | **41 + 1** retrospective — one per registered run | 2 + 1 retrospective | Complete. **39** are **generated projections** emitted by `scripts/generate_run_reports.py` and governed by the generated-projections rule below, not by banner-and-changelog; **2** are hand-authored (`55maps-image-generalisation`, `55maps-text-min-generalisation`) and carry the banner + Changelog from 2026-09-13. Back-filled under the standing exception below |
| `outputs/**/experiment_intent.md` | Per-pass / per-run intent files | **432** files, **35** bannered | 139 | Informal; in scope. Grew 139 → 432 since May. **Classified 2026-09-13** (item 11a): **397 generated** — 393 written at launch by `scripts/lib_experiment_intent.py`, 4 by `scripts/run_generalisation.py` — and **35 hand-authored** stage intents for steps with no launcher. The 35 hand-authored are exactly the 35 bannered, so this row's banner count is already complete on the documents that owe one |
| `outputs/**/evaluation.md` | Per-run evaluation summaries | **46** files, **0** bannered; **46 of 46** carry a `**Generated**:` stamp | 11 | **Reclassified**: these are generated projections, so the 2026-09-11 generated-projections ruling below governs them, not the banner rule. Registered as generated 2026-09-13 (rule `gen-outputs-evaluation`, generator `scripts/evaluate_detections.py`); still the ruling's one **open** class — none carries that regime's banner, source commit or drift guard, and closing it is a generator change, not a document edit |
| `outputs/**/pre_launch_audit.md` | audit-config skill outputs | **2** files, **1** bannered | 1 (`55maps-text-high-t0.3-generalisation`) | In scope going forward. Classified hand-written 2026-09-13, so both owe regime 1 |

All 2026-09-13 counts are file counts taken in a worktree at `main` on
that date; the banner counts are files matching `^> **Last revised**`.
The May 2026 counts are retained as history and are **not** restated on
the new basis — the `results/**.md` row's May figure counted anchor docs
per audit plan § 5.2, while its September figure counts the whole tree,
so the two are not comparable and neither is wrong.

**Note on the denominator, and the instrument that sets it.** Only
hand-written documents owe a banner and changelog; generated ones owe the
regime below instead. The project's own classifier is
`reports/verification/generated-file-registry.json`, built by
`scripts/build_generated_file_registry.py`.

**Rebuilt 2026-09-13** (checklist item 11a; deltas
`reports/generated-file-registry-2026-09-13.md`). It had been built on
`2026-08-20T08:24:18` at `git_head` `06f7b8ea5` and held 2,131 files, and
by charter it enumerated `results/`, `reports/` and part of
`docs/methodology` but **not** `outputs/` — so the three `outputs/` rows
above had no generated-versus-hand-written classification at all. The
charter now extends to `outputs/**.md` and the rebuild holds **3,619**
files — **3,318** generated, **301** hand-written, **0** unattributed:
`results/` 2,864 (2,723 generated), `reports/` 88 of the 104 present (16
under the `reports/d17-inventory/` audit-apparatus exclusion), `outputs/`
638 (595 generated), `docs/` 29 (all hand-written). So the denominator for
this table's `results/**.md` row is **141**, not 2,864: the other 2,723 are
generated per-cell output that owes the regime below.

Each generated row also records that regime's three obligations —
`generated_banner`, `source_commit_stamp`, `check_mode` (read out of the
generator's argparse, not grepped) and `tier1_check_test` with the test
path — so "which generated documents are in neither regime?" is a query
(`--gaps`) rather than a hand audit. The registry is itself generated and
now carries its own guard: `_meta.git_head` is the stamp, `--check` the
drift mode, and `tests/test_build_generated_file_registry.py` runs that
check against the committed file.

One further caution, unchanged by the rebuild: its marker test matches
`**Generated**:` anywhere in a file's
first fifteen lines, and at least six hand-authored `results/**.md`
documents carry such a line as a provenance note rather than a generator
stamp (`results/evaluation-scopes.md`,
`results/retest/retest-production-summary.md`,
`results/paper-tables/gold-standard-spatial-tolerance.md`,
`results/55maps-mcc-v2-summary/report.md`, and
`results/pv/phase{1,2}/pv-phase*-analysis.md`) — the registry's explicit
`hw-*` rules override the marker on all six, so nothing is mis-filed
today, but an audit that reads the marker instead of the registry would
wrongly exempt six documents that already carry a hand revision trail.

**Back-fill rule**: per CLAUDE.md, "back-fill on touch only" — when you
edit one of these documents, attach the banner + Changelog stub. Do not
bulk back-fill unchanged documents.

**One standing exception, discharged 2026-09-13**: the PI asked on
2026-09-13 for the missing per-run post-run reports to be back-filled in
bulk (`planning/documentation-foundation-checklist-2026-09-13.md`, Batch 1
item 1), which supersedes back-fill-on-touch for the
`outputs/**/post_run_report.md` row and for that row only. It was
discharged the same day: every one of the 41 runs in
`results/run-registry.json` now has a report. The 39 that had none are
generated projections — regenerate with
`python3 scripts/generate_run_reports.py --all --write`, drift-check with
`--check` (a tier-1 test in `tests/test_generate_run_reports.py` runs it) —
and the 2 hand-authored narrative reports were left as prose and given the
banner + Changelog instead, because their Dawid-Skene corrections, paired
comparisons and per-map extrema are not re-derivable from the manifests
and a projection would have destroyed them. Their pre-2026-09-13 state
also corrected a claim in the row above: they existed but carried neither
a banner nor a Changelog, so the former "2 compliant" cell described
existence, not banner compliance.

**Out of scope**: `docs/notes/reflections/*.md` (append-only historical
records), `docs/methodology/preregistration/*.md` (governed separately
by the preregistration process), `docs/methodology/research/*.md`
(third-party Deep Research reports), and `archive/**` (frozen state).

**Generated projections — provenance, not a hand changelog (PI ruling
2026-09-11, Session 153)**: a Markdown file under an in-scope path that
is emitted by a generator from registered inputs is OUT of the
banner-and-changelog requirement and IN a stricter one. **Six** families
are governed by this rule as of 2026-09-13 — the table in "Which files this
reaches" below is the authoritative list, recounted from the registry; the
two worked examples that established the rule were:

- `results/hypothesis-outcome-table/hypothesis-outcome-table.md` — a pure
  projection of `results/analyses-manifest.json`
  (`scripts/generate_hypothesis_outcome_table.py --check`).
- the 39 generated `outputs/<run>/post_run_report.md` files
  (`scripts/generate_run_reports.py --check`, added 2026-09-13), projected
  from the run registry, the runs / conditions / passes / analyses
  manifests, `results/run-conditions.json`, `results/run-analyses.json`
  and the errata register. Each names its generator, its version and the
  source commit; a hand edit fails the drift guard and is destroyed on the
  next regeneration.

The principle:
a hand-edited document's history is human, so a human writes it down; a
generated document's history is its inputs' and its generator's git
history, so the file must make that traceable by machine instead. Every
such file must carry (1) a `GENERATED FILE — do not hand-edit` banner
naming the generator script, (2) the source commit of the inputs it was
projected from, and (3) a `--check` drift guard in the generator, run by
a tier-1 test, that fails when the committed file no longer matches a
fresh projection. A hand-added changelog would break (3), which is why
the exemption exists. "Is this current?" is answered by the drift test,
not by a changelog. Before→after notes for a regeneration go in the
commit message and, when the change is paper-relevant, in the session's
report under `reports/`.

**Which files this reaches — recounted from the registry, 2026-09-13**
(checklist item 11b; deltas `reports/generated-file-registry-2026-09-13.md`),
so the ruling is not read as applying only to its worked examples. Every
figure here is a query over
`reports/verification/generated-file-registry.json`, not a reading pass.

**50 documents, six generators, all three obligations met**:

| Documents | Generator | Check mode | Tier-1 test |
|---:|---|---|---|
| 39 `outputs/<run>/post_run_report.md` | `scripts/generate_run_reports.py` | `--check` | `tests/test_generate_run_reports.py` |
| 5 register renderings (`results/{runs,conditions,passes,analyses}-manifest.md`, `results/run-registry.md`) | `scripts/generate_post_run_report.py` | `--check-renderings` | `tests/test_manifest_renderings.py` |
| 3 55-map boards (`results/55map-leaderboard/55map-leaderboard-50m{,-standardised,-r2}.md`) | `scripts/build_55map_leaderboard.py` | `--check` | `tests/test_55map_leaderboard_renderings.py` |
| 1 `results/hypothesis-outcome-table/hypothesis-outcome-table.md` | `scripts/generate_hypothesis_outcome_table.py` | `--check` | `tests/test_generate_hypothesis_outcome_table.py` |
| 1 Era-2 board `tiering_20m.md` | `scripts/era1_leaderboard_tiering.py` | `--check <board dir>` | `tests/test_era2_board_renderings.py` |
| 1 Era-2 board `frame-deltas.md` | `scripts/build_gs_era2_board.py` | `check-renderings` | `tests/test_era2_board_renderings.py` |

**The six documents in neither regime are closed to 0.** The five register
renderings carried the banner but no source commit, and their generator had
no `--check` at all; they now have both. The Era-2 board's two tables and
the three generated 55-map boards were given a banner, a source-commit
stamp and a tested `--check`, each regenerated once with **zero content
drift** — the diff is the banner. The audit's fourth "55-map table",
`results/55map-leaderboard/gs-vs-55map-transfer.md`, is **hand-written**
(no generator, no sidecar JSON; rule `hw-gs-55map-transfer`): it owes
regime 1 and now carries a banner and a Changelog, so the four tables split
across both regimes rather than sitting in one.

**What remains, named**: (a) the **46** `outputs/**/evaluation.md` files —
the ruling's one open class, `scripts/evaluate_detections.py`, still with
no banner, stamp or check mode; (b) **17** further
`tiering_20m.md`-family documents written by
`scripts/era1_leaderboard_tiering.py` for earlier analyses, which are now
one `--render-md <board dir>` away from the regime (the generator carries
the guard; only their committed text predates it) and are deliberately left
for back-fill-on-touch, since re-rendering another analysis's board is that
analysis's business; (c) the remaining generated corpus — 3,268 of 3,318
generated documents carry no `GENERATED FILE` banner, almost all of it
per-cell `results/**` output. (c) is a statement of the tree's shape, not a
backlog: the ruling reaches paper-facing projections, and the standing rule
for the rest is back-fill on touch. Audit trail:
`planning/interim-docs-review.md` § 11.4, and `--gaps` for the live list.

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

### 2026-09-13 — Registry rebuilt over `outputs/`; the "neither regime" count closed to 0 (Session 154, items 11a and 11b)

**Trigger**: items 11a and 11b of `planning/documentation-foundation-checklist-2026-09-13.md`, which the 2026-09-13 re-score (`planning/interim-docs-review.md` § 11.5) had made prerequisites for a second documentation audit pass: the generated-file registry was stale and did not enumerate `outputs/` at all, so the "six generated documents in neither compliance regime" finding rested on a reading pass rather than on the project's own classifier.

| Claim | Before | After |
|---|---|---|
| Registry corpus | 2,131 files at `git_head` `06f7b8ea5` (2026-08-20); `outputs/` not enumerated | **3,619** files — `results/` 2,864, `reports/` 88 of 104 present, `outputs/` 638, `docs/` 29 |
| Registry strata | 1,952 generated / 179 hand-written / 0 unattributed | **3,318** generated / **301** hand-written / **0** unattributed (two files that were marker-carrying-but-unattributed under the old map are now attributed) |
| Generator map | 89 rules, v1.0 | **100** rules, v1.1 — nine `outputs/` rules, two attributions, one widened |
| Denominator for the `results/**.md` row | "2,864 files, 80 bannered" with no classification | **141** hand-written owe a banner; the other 2,723 are generated |
| Generated documents in the 2026-09-11 regime | 45 documents, 3 families, 5 of them unverified on requirements (2) and (3) | **50** documents, **6** generators, all three obligations met and each named with its check mode and tier-1 test |
| Generated documents in **neither** regime (the audit's six) | 6 | **0** |
| `outputs/**/experiment_intent.md` classification | none | 397 generated / 35 hand-authored — and the 35 hand-authored are exactly the 35 bannered |

**What changed in the documents**: ten generated documents were regenerated once so they carry the banner and stamp — the five register renderings, the Era-2 board's `tiering_20m.md` and `frame-deltas.md`, and the three 55-map boards. **Content drift was zero in every case**: the diff is the banner and the stamp, two lines per file. That the 150-cell tiering table and the three 28-pair boards re-render byte-identically from their committed JSON is itself the evidence that they were pure projections. One hand-written document, `results/55map-leaderboard/gs-vs-55map-transfer.md`, gained a Revision-Policy banner and Changelog; no figure in it moved.

**Correction to the audit's framing**: the re-score counted "the four 55-map leaderboard tables" as one generated class. Three are generated boards; the fourth has no generator and no sidecar JSON and was already filed hand-written in the generator map. The four split across both regimes.

**What did NOT change**: the 2026-09-11 ruling itself (this entry applies it), every register row, board cell, rank, tier, tie set, withheld-cell disclosure and signature field, the committed r1 55-map board JSONs (G3/G4 regression-gate targets — `--rebuild-md` is a render-only path), and the May 2026 counts retained as history. The `results/**.md` and `reports/**.md` row counts from this morning's pass were not re-taken.

**Landed in**: `86ba12413` (registry), `acd4ed054` (register renderings), `b16954d4c` (Era-2 board tables), `80e897049` (55-map boards), and this entry's own commit.

### 2026-09-13 — Post-run reports back-filled for all 41 runs (Session 153, Batch 1 item 1)

**Trigger**: the PI's 2026-09-13 request to back-fill the missing per-run post-run reports in bulk (`planning/documentation-foundation-checklist-2026-09-13.md`, Batch 1 item 1), which supersedes back-fill-on-touch for the `outputs/**/post_run_report.md` row only. Taken via the generated-projection route the 2026-09-11 ruling opened, so the reports carry provenance and a tested drift guard instead of 39 hand changelogs that would each have gone stale on the next manifest rebuild.

| Claim | Before | After |
|---|---|---|
| Scope table, `outputs/**/post_run_report.md` count | 2 + 1 retrospective (2026-05-26); "~22" post-audit target | 41 + 1 retrospective — one per registered run |
| Same row, compliance cell | "2 compliant; 15 missing entirely" | Complete: 39 generated projections under the generated-projections rule, 2 hand-authored with banner + Changelog |
| Governed generated-projection families | 1 (the hypothesis-outcome table) | 2 (+ the 39 generated post-run reports) |

**Correction the back-fill surfaced**: the "2 compliant" cell was wrong on its own terms. Both hand-authored reports existed, but neither carried a Revision-Policy banner or a Changelog, so the cell described existence rather than banner compliance. Both were given the pattern on 2026-09-13 (their own Changelogs record it) and the cell is restated.

**What did NOT change**: the run count (41 registered runs, unchanged), any metric, and the 2026-09-11 ruling itself — this entry applies it rather than amending it. The registered counts for `experiment_intent.md` (139), `evaluation.md` (11) and `pre_launch_audit.md` (1) are 2026-05-26 censuses and were **not** re-counted in this pass; they stay as dated figures rather than being refreshed without an audit.

**Landed in**: the commit whose message begins `docs(outputs): back-fill post-run reports for all 41 registered runs`.

### 2026-09-13 — Compliance table recounted; the generated-projections ruling's reach recorded (Session 153)

**Trigger**: item 5(b) of
`planning/documentation-foundation-checklist-2026-09-13.md` — the
compliance table carried 2026-05-26 counts and predated the 2026-09-11
generated-projections ruling, so it described neither today's inventory
nor today's two regimes. Every count below was taken as a file count in a
worktree at `main` on 2026-09-13; banner counts match
`^> **Last revised**`.

**Before → after table for numerical claims that moved** (the May column
is retained in the table as history rather than overwritten):

| Row | Count (2026-05-26) | Count (2026-09-13) |
|---|---|---|
| `results/**.md` | ~35–50 anchor docs | **2,864** files, **80** bannered (17 of 17 `findings.md` and 4 of 4 supplement docs compliant) |
| `reports/**.md` | varies | **101** files, **62** bannered (18 of 18 dated 2026-09-11/12/13 compliant) |
| `outputs/**/post_run_report.md` | 2 + 1 retrospective | measured at **3** files / **2 of the 41** manifest run directories, then **superseded the same day** by item 1's back-fill — the row now carries item 1's **41 + 1** (see the entry below) |
| `outputs/**/experiment_intent.md` | 139 | **432** files, **35** bannered |
| `outputs/**/evaluation.md` | 11 | **46** files, **0** bannered, **46 of 46** generated |
| `outputs/**/pre_launch_audit.md` | 1 | **2** files, **1** bannered |

**One row reclassified.** `outputs/**/evaluation.md` was listed as
"Informal; in scope going forward" under the banner rule. All 46 carry a
`**Generated**:` stamp and are generator output, so the 2026-09-11
generated-projections ruling governs them instead; none yet carries that
regime's banner, source commit or drift guard, and closing that is a
generator change rather than a document edit.

**One note added.** A denominator note
records that only hand-written documents owe a banner, that the project's
own classifier
(`reports/verification/generated-file-registry.json`) was last built
`2026-08-20T08:24:18` at `git_head` `06f7b8ea5` and is stale against this
table by 814 `results/**.md` and 48 `reports/**.md`, that by charter it
does not enumerate `outputs/` so the three `outputs/` rows have no
classification at all, and that its `**Generated**:` marker test matches
six hand-authored documents whose explicit `hw-*` rules currently
override it — so an audit reading the marker rather than the registry
would wrongly exempt six documents that already carry a revision trail.

**The generated-projections section gains a reach paragraph**, naming the
three families that satisfy the ruling — **45 documents** once item 1's 39
generated post-run reports are counted — and the six-plus-46 that satisfy
neither regime, with `planning/interim-docs-review.md` § 11.4 as the audit
trail. It also flags that the five register renderings name a generator
but were **not** checked in this pass for a source commit and a tier-1
drift guard, so they should not be cited as fully compliant until they
are.

**What did NOT change**: the Purpose, Status, Artefact Types, Gitignore
Policy, Proposed Directory Structure, Naming Conventions, Post-Run Report
Schema and Immediate TODOs sections; the six in-scope path patterns
themselves (no class added or removed from scope); the out-of-scope list;
the 2026-09-11 generated-projections rule's three requirements and its
rationale; and the 2026-08-03 `docs/methodology/reports/**`
split-by-citation rule.

**Interaction with the item-1 entry below, recorded so the two do not
disagree.** That entry states that the `experiment_intent.md` (139),
`evaluation.md` (11) and `pre_launch_audit.md` (1) figures are 2026-05-26
censuses left unrefreshed "rather than being refreshed without an audit".
This pass **is** that audit: all three are recounted above (432, 46 and 2),
the May figures are retained beside them as history, and `evaluation.md`
is reclassified on the strength of the recount. The two entries are
sequential passes of the same day, not competing claims.

### 2026-09-11 — Governance: generated projections carry provenance, not a changelog (Session 153)

**Trigger**: regenerating the hypothesis-outcome table after the `verifier-uplift-pairing` row was registered exposed a collision — the Document Revision Policy asks for a hand changelog on `results/**.md`, but the table is a generated projection whose `--check` byte-equality guard (tier-1) would fail on any hand edit. PI ruling: generated projections are exempt from the banner-and-changelog rule and must instead carry a GENERATED banner, a source-commit stamp, and a tested drift guard. Rule added to § "Documents in Revision Policy Scope". Route (b) of `reports/r7-gaps-deltas-2026-09-11.md` § 6.1.

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
