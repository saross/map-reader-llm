# Output Directory Standard

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
The schema is lifted from the four 55-map generalisation reports (Exemplar
A: `outputs/55maps-image-generalisation/post_run_report.md`), which were
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
