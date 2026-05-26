# Results

> **Last revised**: 2026-05-26 (full rewrite — the previous version
> described a pre-v2.9-redesign stranded-factorial study scaffold that
> never ran). See [§ Changelog](#changelog) for revision history.

Statistical analysis outputs, derived metrics, and paper-prep artefacts
from the preregistered VLM burial mound detection study.

## Purpose

This directory holds **derived analyses**, not raw experimental
artefacts:

- Raw run outputs (per-pass detections, evaluation JSON, cost manifests)
  live in `outputs/`. See
  `docs/methodology/output-directory-standard.md`.
- This directory holds the statistical analyses, condition rankings,
  cross-cutting investigations, paper-output staging, and narrative
  summary documents that cite those raw artefacts.

The structure is **flat by analysis topic**, not hierarchical by
experimental phase. Sub-directories are named for the analysis they
contain (e.g., `phase3a-image-matrix/`, `55maps-cross-track-comparison/`,
`dawid-skene/`), and may pull from multiple raw runs.

## How to navigate

For the canonical phase → document mapping, start at
`docs/methodology/documentation-index.md`. This README is a
**topic-organised mirror** — it groups the 62 sub-directories by what
they analyse, while the documentation-index orders them by
preregistered phase and hypothesis.

Related references:

- `docs/methodology/output-directory-standard.md` — directory structure
  spec, including the post-run-report schema and the Documents in
  Revision Policy Scope enumeration.
- `planning/documentation-audit-plan.md` — the in-progress
  documentation audit and back-fill plan (Stage Gate 1 approved
  2026-05-26).
- `docs/methodology/preregistration/` — preregistration document,
  execution plan, and decisions / errata logs.
- `docs/notes/reflections/working-notes.md` — running observation
  register (Obs N entries cited from anchor docs).

## Conceptual groupings

The work falls into six categories, presented here in roughly the
order it was carried out. Where the historical "Era 1 / Era 2"
shorthand survives in older docs, treat it as superseded — this
README uses descriptive labels instead.

### 1. Hypothesis-testing OFAT runs

Single-OFAT-axis sweeps testing the preregistered hypotheses on the
original training corpus. The bulk of the project's hypothesis-testing
work lives here.

- `retest/` — Phases 2a–2e under the v2.9 sequential OFAT design
  (paper-citation source for H1, H4, H5, H7, H8 results).
- `phase3a-image-matrix/`, `phase3a-text-matrix/` — Phase 3a consensus
  voting sweep (H3) on image and text tracks.
- `phase3c-diversity/` — Phase 3c diversity exploratory matrix (H9,
  redirected here from the retired Phase 3b).
- `h8-v2/` — H8 library-size analysis (v2 verifier).
- `h10/` — H10 pool-size analysis.
- `h11/`, `h11-384-pv-diagnostic/`, `h11-384-single-pass-t0-rerun/` —
  H11 tile-size and 384-pixel proposer-verifier diagnostics.
- `h12-v2/` — H12 analysis (v2 verifier).
- `verifier-t-pilot/` — verifier temperature pilot study.
- `cross-hypothesis-library/` — cross-hypothesis library-construction
  analyses.
- `e47-propose-brief/` — E47 propose-brief experiment data.
- `pv/` — proposer-verifier umbrella analyses.
- `pairwise/` — pairwise comparison analyses across OFAT conditions.
- `verifier-calibration-audit/`, `verifier-calibration-matrix/`,
  `verifier-calibration-matrix-pairwise/` — verifier-calibration work
  that fed into the OFAT runs.

### 2. Gold-standard (4-map) analyses

Strict-evaluation analyses on the 4-map gold-standard sub-corpus.
These preceded the 55-map generalisation runs and were the bridge
between OFAT hypothesis testing and full-corpus generalisation.

**Methodological sub-division**: gold-standard analyses span two
phases of evaluation methodology:

- **Earlier phase** — used a smaller tile subset for evaluation
  (~60 tiles, to be confirmed empirically). This pool proved to have
  insufficient discriminatory power for some comparisons, prompting
  the move to the full corpus.
- **Later phase** — moved to the full 4-map tileset for evaluation.

In **both** phases, a 20-tile "calibration" set was reserved for
training-style work and excluded from the test pool. The
`feedback_384px_scope_preference.md` project memory note discusses
related tile-pool selection rationale.

Sub-directories carrying an `-era2` suffix (e.g.,
`gold-standard-extended-buffer-sweep-era2`) indicate the later
tile-pool methodology. For analyses without the suffix, **the tile
pool must be confirmed empirically from each analysis's metadata** —
this README does not assert a phase mapping for individual
sub-directories. An empirical mapping pass is a candidate follow-up
edit (lower priority than the audit plan's enumerated remediation).

Sub-directories:

- `gold-standard-attractor-pull/`
- `gold-standard-extended-buffer-sweep/`
- `gold-standard-extended-buffer-sweep-era2/`
- `gold-standard-image-extended-buffer-sweep/`
- `gold-standard-subtype-classification/`
- `gs-125m-fp-side-6-crop-review/`
- `gs-fp-classification/`
- `gt-duplicate-review-gs4/`, `student-gt-fn-rate-analysis-gs4/` —
  GS-specific ground-truth audits.

### 3. 55-map generalisation runs

The final phase of the project — running the OFAT-winning
configurations on the full 55-map corpus to test generalisation.

Primary run analyses:

- `55maps-image-generalisation/` — image-modality generalisation run.
- `55maps-text-min-generalisation/` — text-minimal generalisation run.
- `55maps-text-high-generalisation/` — text-high generalisation run.
- `55maps-text-high-t0.3-generalisation/` — text-high at T=0.3.
- `55maps-generalisation/` — retrospective text run.

Follow-on analyses on the 55-map outputs:

- `55maps-attractor-pull-v2/` — attractor-pull diagnostic.
- `55maps-cleaned-gt-evaluation/` — evaluation against cleaned GT.
- `55maps-cross-track-comparison/` — image vs text track comparison.
- `55maps-ds-summary-v2/` — Dawid–Skene correction summary.
- `55maps-fp-classification/` — false-positive classification.
- `55maps-mcc-v2-summary/` — MCC metrics summary.
- `55maps-pairwise-permutation-v2/` — pairwise permutation tests.
- `55maps-per-map-shell-variance/` — per-map variance analysis.
- `55maps-vs-gs-tp-localisation/` — 55-map vs GS true-positive
  localisation comparison.

### 4. Cross-cutting / secondary analyses

Analyses that pull from multiple runs or that investigate secondary
effects orthogonal to a single hypothesis.

- `dawid-skene/` — Dawid–Skene incompleteness-correction analyses.
- `factor-analysis/` — factor-analytic investigations.
- `inter-pass-agreement/` — pass-to-pass agreement analyses.
- `leaderboard/` — cross-condition rankings (per-architecture and
  combined). The paper's headline ordering lives here.
- `proposer-vote-fraction/` — proposer-vote-fraction diagnostics.
- `secondary-effects/`, `secondary-effects-consensus-sd/`,
  `secondary-effects-token-efficiency/` — secondary-effect
  investigations.
- `fp-failure-mode-closure/` — false-positive failure-mode closure
  analysis.
- `gt-duplicate-review/`, `gt-spacing-analysis/` — ground-truth audits
  (general; GS-specific variants are in § 2).
- `student-gt-fn-rate-analysis/` — student ground-truth false-negative
  rate.
- `temperature-failure-recovery-analysis/` — temperature failure
  recovery investigation.
- `tolerance-sensitivity/` — tolerance-sensitivity sweep.
- `tp-only-localisation-bias-sub-band/` — TP-only localisation bias
  sub-band analysis (Obs 322).
- `wbf-greedy-comparison/` — WBF vs greedy aggregation comparison.

### 5. Paper-output staging

- `paper-eval/` — evaluation data staged for paper consumption.
- `paper-tables/` — paper-table staging directory.
- `figures/` — publication figures.

### 6. Audit / meta

- `documentation-audit/` — prior audit pass (`audit-summary.md`,
  `priority-backfill.md`) referenced by
  `planning/documentation-audit-plan.md`.
- `limitations-consolidation/` — consolidated limitations notes for
  paper Discussion / Limitations sections.

## Top-level documents

The 25 top-level `.md` and JSON files at `results/*` are paper-prep
narrative anchors and machine-readable indices. The most-cited:

- `phase2a-analysis-summary.md`, `phase2c-track1-image-analysis.md`,
  etc. — per-phase paper-citation narrative summaries (note: only the
  image track has a top-level Phase 2c analysis; the text-track
  analysis is under `retest/phase2*/`).
- `phase2*-carry-forward-parameters.md` — per-phase carry-forward
  parameter records (the "winners" from each OFAT axis).
- `h11-tile-size-results.md` — H11 paper-citation summary.
- `phase3d-*.md` — phase 3d experiment results:
  `phase3d-pilot-results.md`, `phase3d-experiment-e-results.md`,
  `phase3d-union-results.md`, `phase3d-high-thinking-results.md`,
  `phase3d-pilot-extensions.md`, `phase3d-verifier-experiments-abc.md`.
- `meta-findings-summary.md` — cross-experiment meta-findings.
- `methods-approach-b-vs-corrected-f1-nuance.md`,
  `methods-curator-gt-incompleteness-limitation.md` — methodological
  notes for paper Methods / Limitations.
- `evaluation-scopes.md`, `k-consensus-heterogeneity-footnote.md` —
  methodological clarifications.
- `ci-metadata-registry.md` — bootstrap CI metadata registry.
- `all-bootstrap-cis.json`, `consensus-build-manifest_*.json`,
  `phase2a-analysis-report.json` — machine-readable indices and
  manifests.
- `55maps-cleanup-report.json`, `phase2c-exploratory-pure-positive-hp.json` —
  cleanup and exploratory artefacts.

For the canonical phase → document mapping, see
`docs/methodology/documentation-index.md` § "Phase → Document
Cross-Reference".

## Conventions

- **Anchor docs** (the paper-cited subset, ~35–50 docs) follow the
  Document Revision Policy in `/CLAUDE.md`. Banner + Changelog
  back-fill on touch only.
- **Machine-generated summaries** (e.g., the ~50
  `threshold_sweep_summary.md` files under
  `h11-384-pv-diagnostic/*/`) are treated as artefacts, not anchor
  docs — they do not require the Revision Policy treatment.
- **Cross-reference / lineage**: anchor docs are expected to end with a
  `## See also` block per `docs/methodology/output-directory-standard.md`
  § "Cross-reference / Lineage Block". Back-fill is in progress as part
  of the audit campaign.
- **JSON sidecars** (e.g., `*.report.json`, `*.metadata.json`) carry
  per-analysis metadata; the corresponding `.md` is the
  human-readable narrative.
- File naming follows the conventions in
  `docs/methodology/output-directory-standard.md` § "Naming
  Conventions".

## Reproducibility

- Raw run outputs live in `outputs/`; this directory contains derived
  analyses only.
- Analysis scripts live in `scripts/` (currently 168 Python scripts,
  May 2026). Per-script reproducibility recipes belong in each run's
  `outputs/<run-id>/post_run_report.md` rather than enumerated here.
  Post-run-report back-fill for Era 1 runs is planned under the audit
  campaign (Phase 3 of `planning/documentation-audit-plan.md`).
- The Dawid–Skene incompleteness correction (`dawid-skene/`,
  `55maps-ds-summary-v2/`) is the project's canonical accounting for
  ground-truth incompleteness; the corrected F1 / P / R appear in the
  paper headline alongside the raw metrics.
- Anti-confabulation: numerical claims in derived docs should anchor
  back to their source `outputs/<run-id>/evaluation/*.json` or
  `cost_manifest.json`. Re-verify before citing.

## Changelog

### 2026-05-26 — Full rewrite

**Refresh trigger**: Stage Gate 1 approval of
`planning/documentation-audit-plan.md`. The previous version of this
README described a pre-v2.9-redesign stranded-factorial study scaffold
(`phase1-library/`, `phase2-factorial/strand1-verbosity/`,
`phase4-transfer/h6-flash-pro/`, etc.) that never ran. None of those
directories exist; the real `results/` is flat with 62 sub-directories
grouped by analysis topic.

**Before → after summary**:

| Aspect | Before (stale) | After (current) |
|---|---|---|
| Directory structure section | Hierarchical 5-phase tree with 20+ sub-paths; **none of those paths exist** | Six conceptual groupings (OFAT / GS / 55-map / cross-cutting / paper-output / audit) covering all 62 real sub-directories |
| Preregistration alignment table | OLD v2.0 stranded factorial: strand1-verbosity, strand2-h5-confirm, strand3-library, strand4-interaction | Replaced by pointer to `docs/methodology/documentation-index.md` § "Phase → Document Cross-Reference" (the canonical mapping, refreshed under v2.9 OFAT) |
| Analysis pipeline section | Enumerated 4 script names (`aggregate_results.py`, `analyse_phase2_results.py`, `generate_figures.py`, `compile_report.py`) of which only one exists today | Replaced by pointer to per-run `post_run_report.md` reproducibility recipes (Phase 3 audit-back-fill target) |
| File conventions | Aspirational patterns (`*-bootstrap.csv`, `metrics-*.csv`) | Replaced with current conventions (anchor docs vs machine artefacts, lineage blocks, JSON sidecars) |
| Document Revision Policy | Not applied | Banner applied; this file is in scope per `results/**.md` |

**What did NOT change**: this README's purpose — to orient newcomers to
the `results/` directory.

**Verification**: pre-rewrite `ls`-based survey confirmed 62
sub-directories, 25 top-level `.md` files, and that none of the
5 stale phase directories in the old structure exist.

### 2026-04-08 — Original publication

The README was originally authored as part of the project's first
attempt to standardise the `results/` layout, alongside the
preregistration's v2.0 stranded-factorial design. It described an
aspirational hierarchical structure (`phase1-library/`,
`phase2-factorial/strand1-verbosity/`, etc.) that anticipated the
analysis pipeline. The v2.9 preregistration redesign (replacing
stranded factorial with sequential OFAT) made the structural
descriptions obsolete; subsequent organic growth of the project
produced a flat, topic-organised directory rather than the hierarchical
one in the original README. The 2026-05-26 rewrite reflects current
reality and is grounded in the present audit campaign.
