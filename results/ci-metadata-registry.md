# Confidence Interval (CI) Metadata Registry

Generated: 2026-04-20. Maintainer: `shawn@faims.edu.au`.

## Purpose

This registry records the provenance of every Confidence Interval (CI)
reported in the map-reader-llm results tree. For each CI-bearing file
or file-class, the registry captures the four paper-reproducibility
fields: bootstrap iteration count, random seed, resampling unit, and
generating script. The goal is that the paper can cite each reported
CI with a full bootstrap specification.

Four completeness states are used:

- `YES` — All four fields are explicitly recorded in the output
  file (or a co-located manifest).
- `YES_SIDECAR` — Fields are recorded in a co-located sidecar
  (`<name>.metadata.json` next to the data file, or `.metadata.json`
  at the directory level for bulk cells). Sidecars make the resolved
  values (e.g., `"seed": 42`) available without requiring a reader to
  consult the generating script. Introduced 2026-04-20 (see "Sidecar
  upgrade pass" below).
- `INFERABLE` — The generating script is identifiable and its
  defaults are version-controlled; the output file's timestamp and
  script version are sufficient to resolve the defaults. After the
  2026-04-20 sidecar pass, this state should not persist in the
  table; entries previously marked `INFERABLE` are now `YES_SIDECAR`
  except where noted.
- `NO` — One or more fields cannot be reliably recovered. Listed in
  `archive/planning-completed-session-81-82/ci-rerun-todo.md`.

## Default bootstrap configuration across the codebase

All bootstrap and permutation procedures in this repository share
standard defaults that are hard-coded in a small number of scripts.
These defaults are embedded in the generating script and
version-controlled, so an `INFERABLE` status combined with a file
timestamp identifies the bootstrap specification precisely.

| Script | Default iterations | Default seed | Resampling unit |
|--------|--------------------|--------------|-----------------|
| `scripts/evaluate_detections.py` | `DEFAULT_BOOTSTRAP = 1000` | `DEFAULT_SEED = 42` | tile (see `lib_advanced_metrics.bootstrap_ci`) |
| `scripts/build_tiered_leaderboard.py` | `DEFAULT_BOOTSTRAP = 1000` | `DEFAULT_SEED = 42` | tile |
| `scripts/analyse_phase2_results.py` | `DEFAULT_N_BOOTSTRAP = 1000` | `random_seed = 42` | tile (multi-run across K runs, averaged) |
| `scripts/compute-pairwise-effect-sizes.py` | `1000` | `42` (constant) | tile (paired) |
| `scripts/run_pairwise_tests.py` | `10000` permutations | `42` | tile (permutation) |
| `scripts/compare_wbf_greedy_pv_permutation.py` | `10000` permutations | `42` | tile (permutation) |
| `scripts/compute_corrected_f1_multi_buffer.py` | `10000` bootstrap | `42` | review-level (matched pair) |
| `scripts/compute_corrected_f1_human_reviewed.py` | `10000` bootstrap | `42` | review-level |
| `scripts/crosstab_verifier_vs_human.py` | `10000` bootstrap | `42` | review-level |
| `scripts/crosstab_uncalibrated_vs_calibrated.py` | `10000` bootstrap | `42` | review-level (overlap rows) |
| `scripts/analyse_subtype_classification.py` | `10000` bootstrap | `42` | matched-pair (stratified by map) |
| `scripts/analyse_buffer_band_lift.py` | `1000` permutations | `42` | detection (spatial null) |

Where the output file records these values explicitly (e.g., `_metadata.n_bootstrap`,
`metadata.bootstrap_iterations`, `provenance.seed`), the registry marks
`metadata_complete = YES`. Where the file omits them but they can be
recovered from the generating script's defaults at the file's timestamp,
the registry marks `INFERABLE`.

## Canonical evaluation.json gap

The `scripts/evaluate_detections.py` script is the primary one-off
evaluator. It writes `f1_ci_lower`, `f1_ci_upper`, `p_ci_lower`,
`p_ci_upper`, `r_ci_lower`, `r_ci_upper` at each buffer but does **not**
write `bootstrap_n`, `seed`, or `resampling_unit` into the output JSON.
Any file named `evaluation.json` with this structure therefore has
`metadata_complete = INFERABLE`. There are several hundred such files
across `paper-eval/`, `phase3a-{image,text}-matrix/`, `h8-v2/`,
`h12-v2/`, `pairwise/tile-size-30m/`, `55maps-*-generalisation/evaluation/`
and related trees. They are all produced with the defaults above
unless overridden on the Command Line Interface (CLI); no override is
known to have occurred. Adding explicit metadata writes to
`evaluate_detections.py` is captured as a standing recommendation in
`archive/planning-completed-session-81-82/ci-rerun-todo.md` but does not mandate re-running the files.

## Registry table

File-classes are grouped by generating script. `ci_count` is the
number of distinct (metric, buffer, condition) CI triples in the
file or class; where a class expands to many files, the column
reports per-file × file count.

Note: rows previously marked `INFERABLE` were upgraded to
`YES_SIDECAR` in the 2026-04-20 sidecar pass (see "Sidecar upgrade
pass" below for details). A new column `sidecar_path` records the
location of the resolved-metadata sidecar for each upgraded entry;
rows with no sidecar show `—`.

| file_path | ci_count | methodology | iterations | seed | resampling_unit | source_script | source_git_commit | date_generated | metadata_complete | sidecar_path | notes |
|-----------|----------|-------------|------------|------|------------------|---------------|-------------------|----------------|--------------------|--------------|-------|
| `outputs/55maps-image-generalisation/evaluation/evaluation.json` | 12 (3 metrics × 4 buffers) | bootstrap percentile (2.5/97.5) | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded in file | 2026-04-18T05:10Z | YES_SIDECAR | `outputs/55maps-image-generalisation/evaluation/evaluation.metadata.json` | Trigger file for this audit. Script default: `DEFAULT_BOOTSTRAP=1000, DEFAULT_SEED=42`; tile-level resampling via `lib_advanced_metrics.bootstrap_ci`. Run command captured verbatim in `outputs/55maps-image-generalisation/run.log` and embedded in the sidecar. |
| `outputs/55maps-text-high-generalisation/evaluation/evaluation.json` | 12 | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-04-18T17:48Z | YES_SIDECAR | `outputs/55maps-text-high-generalisation/evaluation/evaluation.metadata.json` | Sister text-high track; no run.log, values resolved from `resolved_config.yaml`. |
| `outputs/55maps-text-min-generalisation/evaluation/evaluation.json` | 12 | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-04-18T12:21Z | YES_SIDECAR | `outputs/55maps-text-min-generalisation/evaluation/evaluation.metadata.json` | Sister text-min track; `run.log` present; sidecar includes CLI invocation. |
| `outputs/h11/single-pass-384-UNINTENDED-T1.0/analysis_report.json` | ≥ 12 | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/analyse_phase2_results.py` | not recorded | 2026-03-14T11:13Z | YES_SIDECAR | `outputs/h11/single-pass-384-UNINTENDED-T1.0/analysis_report.metadata.json` | `n_bootstrap=1000` in file; seed defaults to 42 in script. UNINTENDED (protocol deviation); kept for provenance. |
| `results/all-bootstrap-cis.json` | 2976 | bootstrap percentile | 1000 | 42 | tile | `scripts/consolidate_pv_bootstrap_cis.py` | not recorded | per-entry | YES | — | `_metadata.n_bootstrap=1000, _metadata.random_seed=42` explicit in file. Each entry carries `n_iterations`, `source_file`. |
| `results/pv/all-bootstrap-cis.json` | (aggregate) | bootstrap percentile | 1000 | 42 | tile | `scripts/consolidate_pv_bootstrap_cis.py` | not recorded | per-entry | YES | — | Same structure as the repo-root aggregate. |
| `results/pv/pairwise-effects/pairwise-effect-sizes.json` | 52 comparisons | paired bootstrap percentile | 1000 | 42 | tile (paired) | `scripts/compute-pairwise-effect-sizes.py` | not recorded | per-entry | YES | — | `metadata.n_iterations=1000, metadata.random_seed=42` explicit. |
| `results/pv/pairwise-effects/pairwise-effect-sizes-v2.json` | 52 comparisons | paired bootstrap percentile | 1000 | 42 | tile (paired) | `scripts/compute-pairwise-effect-sizes.py` | not recorded | per-entry | YES | — | Same, v2. |
| `results/pv/phase1/**/threshold_sweep.json` (7 files) | 21 thresholds × 3 metrics × 7 files | bootstrap percentile | 1000 | 42 | tile | `scripts/run_pv.py` (threshold sweep) | not recorded | per-file | YES | — | Each file records `bootstrap_iterations=1000, seed=42` explicitly. |
| `results/pv/phase2/**/threshold_sweep.json` (25 files) | 21 × 3 × 25 | bootstrap percentile | 1000 | 42 | tile | `scripts/run_pv.py` | not recorded | per-file | YES | — | Same. Indexed under phase2/02-canonical-last through phase2/26-high-25of30. |
| `results/paper-eval/pv/**/buffer_sensitivity.json` (9 files) | 3 metrics × 4 buffers × 9 files | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_pv_buffer_sensitivity.py` | not recorded | per-file | YES | — | `bootstrap_iterations=1000, seed=42` explicit. |
| `results/paper-eval/flash-*/consensus-analysis-report.json` (20 cells) | ~45 configs × 3 metrics × 4 buffers × 20 cells | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_consensus_sweep.py` | not recorded | per-file | YES | — | `metadata.n_bootstrap=1000, metadata.random_seed=42` explicit. |
| `results/retest/phase3a-consensus/*/consensus-analysis-report.json` (3 files) | as above × 3 | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_consensus_sweep.py` | not recorded | 2026-03-25 | YES | — | Replication and per-track cells. |
| `results/h11-384-pv-diagnostic/bootstrap-cis-384px.json` | 81 conditions × 3 metrics | bootstrap percentile | 1000 | 42 | tile | `scripts/consolidate_pv_bootstrap_cis.py` | not recorded | 2026-03-25T23:19Z | YES | — | `_metadata.n_iterations` per-entry; script default seed. |
| `results/h11-384-pv-diagnostic/**/threshold_sweep.json` (~80 files) | 21 × 3 per file | bootstrap percentile | 1000 | 42 | tile | `scripts/run_pv.py` | not recorded | per-file | YES | — | Each file records `bootstrap_iterations=1000, seed=42`. |
| `results/h11-384-single-pass-t0-rerun/consensus-analysis-report.json` | as consensus reports | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_consensus_sweep.py` | not recorded | 2026-03-25T12:02Z | YES | — | `metadata.n_bootstrap=1000, metadata.random_seed=42` explicit. |
| `results/e47-v1-vs-v2/v1-sweep/threshold_sweep.json` | 21 × 3 | bootstrap percentile | 1000 | 42 | tile | `scripts/run_pv.py` | not recorded | 2026-03 | YES | — | Explicit `bootstrap_iterations=1000, seed=42`. Quarantine subtree — see note below. |
| `results/e47-v1-vs-v2/v2-sweep/threshold_sweep.json` | 21 × 3 | bootstrap percentile | 1000 | 42 | tile | `scripts/run_pv.py` | not recorded | 2026-03 | YES | — | Same. Quarantine subtree — see note below. |
| `results/e47-v1-vs-v2/grid/**/threshold_sweep.json` (10 files) | 21 × 3 × 10 | bootstrap percentile | 1000 | 42 | tile | `scripts/run_pv.py` | not recorded | per-file | YES | — | Explicit metadata. Quarantine subtree — see note below. |
| `results/e47-v1-vs-v2/detect-single-pass/**/threshold_sweep.json` (8 files) | 21 × 3 × 8 | bootstrap percentile | 1000 | 42 | tile | `scripts/run_pv.py` | not recorded | per-file | YES | — | Explicit. Quarantine subtree — see note below. |
| `results/e47-v1-vs-v2/grid-multibuffer/**/evaluation.json` (0 files; no such files exist) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | STALE_ENTRY | — | The registry row describing 16 `evaluation.json` files under this path was stale on 2026-04-20: no files match the pattern. The subtree does contain `threshold_sweep.json` files (`YES` metadata, row above) which have been moved to `archive/v2-verifier-contamination/e47-v1-vs-v2/grid-multibuffer/**` by the v2-verifier-contamination quarantine agent during this session. Left in the registry to document the resolution; the quarantine agent should remove or relocate the e47-v1-vs-v2 rows when consolidating. |
| `results/leaderboard/era1/leaderboard_tiers_20m.json` | 19 conditions × 3 × 4 | bootstrap percentile | 1000 | 42 | tile | `scripts/build_tiered_leaderboard.py` | `b57cf6c2` | 2026-04-17T03:51Z | YES | — | `metadata.bootstrap=1000, metadata.seed=42, metadata.n_permutations=10000, git_commit` all explicit. |
| `results/leaderboard/era2/leaderboard_tiers_20m.json` | similar | bootstrap percentile | 1000 | 42 | tile | `scripts/build_tiered_leaderboard.py` | recorded in-file | 2026-04-17 | YES | — | Same metadata schema. |
| `results/leaderboard/era3/leaderboard_tiers_20m.json` | similar | bootstrap percentile | 1000 | 42 | tile | `scripts/build_tiered_leaderboard.py` | recorded in-file | 2026-04-17 | YES | — | Same. |
| `results/leaderboard/era{1,2,3}/leaderboard_all_evaluations.json` | hundreds (N=72 × 4 buffers × 3 metrics in era1) | bootstrap percentile | 1000 | 42 | tile | `scripts/build_tiered_leaderboard.py` | not recorded in this file | 2026-04-17 | YES_SIDECAR | `results/leaderboard/era{1,2,3}/leaderboard_all_evaluations.metadata.json` (one per era) | Script defaults as above; sibling `leaderboard_tiers_*.json` has explicit metadata for the same run. Per-era sidecars written 2026-04-20. |
| `results/leaderboard/era2/.cache/evaluations/**/t*_*.json` (thousands) | 3 × 1 per file | bootstrap percentile | 1000 | 42 | tile | `scripts/build_tiered_leaderboard.py` (cache) | not recorded | per-file | YES_SIDECAR | `results/leaderboard/era2/.cache/.metadata.json` (directory-level; gitignored but present in the working tree) | Cache files consumed by the tiered leaderboard. Directory-level sidecar covers all ~1056 cells. The entire `.cache/` subtree is gitignored (reproducible from source detections); the sidecar is present on disk but not versioned. |
| `results/leaderboard/cells/*.json` (13 files) | n/a | — | — | — | — | `scripts/build_tiered_leaderboard.py` (cells) | — | — | NO-CI | — | Threshold-sweep cells without CIs; out of scope for this registry. |
| `results/phase2a-analysis-report.json` | 5 × 3 conditions (multi-run) | bootstrap percentile (multi-run) | 1000 | 42 | tile, runs averaged (K=10) | `scripts/analyse_phase2_results.py` | not recorded | 2026-02-06T06:45Z | YES_SIDECAR | `results/phase2a-analysis-report.metadata.json` | `n_bootstrap=1000` explicit in-file; seed default=42 resolved in sidecar. |
| `archive/outputs-pre-retest-60-tile/phase2b/phase2b-track1-image-analysis.json` | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/analyse_phase2_results.py` | not recorded | 2026-02-08T04:36Z | YES_SIDECAR | `archive/outputs-pre-retest-60-tile/phase2b/phase2b-track1-image-analysis.metadata.json` | Pre-retest 60-tile K=10 pilot. Archived 2026-04-23 (superseded by `results/retest/phase2b-track1-evaluation.json`, 340-tile K=3). |
| `archive/outputs-pre-retest-60-tile/phase2b/phase2b-track2-text-analysis.json` | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/analyse_phase2_results.py` | not recorded | 2026-02 | YES_SIDECAR | `archive/outputs-pre-retest-60-tile/phase2b/phase2b-track2-text-analysis.metadata.json` | Pre-retest 60-tile K=10 pilot. Archived 2026-04-23 (superseded by `results/retest/phase2b-track2-evaluation.json`, 340-tile K=3). |
| `results/phase2c-track1-image-analysis.json` | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/analyse_phase2_results.py` | not recorded | 2026-02 | YES_SIDECAR | `results/phase2c-track1-image-analysis.metadata.json` | Same. |
| `results/phase2c-exploratory-pure-positive-hp.json` | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/analyse_phase2_results.py` | not recorded | 2026-02 | YES_SIDECAR | `results/phase2c-exploratory-pure-positive-hp.metadata.json` | Same. |
| `results/phase2d-track1-image-analysis.json` | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/analyse_phase2_results.py` | not recorded | 2026-02 | YES_SIDECAR | `results/phase2d-track1-image-analysis.metadata.json` | Same. |
| `results/phase2d-track2-text-analysis.json` | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/analyse_phase2_results.py` | not recorded | 2026-02 | YES_SIDECAR | `results/phase2d-track2-text-analysis.metadata.json` | Same. |
| `results/phase3a-text-matrix/all-evaluations.json` | aggregate | bootstrap percentile | 1000 | 42 | tile | `scripts/summarise_phase3a_text_matrix.py` | not recorded | 2026-04-17 | YES_SIDECAR | `results/phase3a-text-matrix/all-evaluations.metadata.json` | Aggregate of per-cell `evaluation.json` in the same tree. |
| `results/phase3a-image-matrix/all-evaluations.json` | aggregate | bootstrap percentile | 1000 | 42 | tile | `scripts/summarise_phase3a_matrix.py` | not recorded | 2026-04 | YES_SIDECAR | `results/phase3a-image-matrix/all-evaluations.metadata.json` | Same. |
| `results/phase3a-{image,text}-matrix/**/evaluation.json` (~252 files) | 3 × 4 per file | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | per-file | YES_SIDECAR | `results/phase3a-text-matrix/.metadata.json` and `results/phase3a-image-matrix/.metadata.json` (directory-level) | Per-cell outputs; script defaults. Covered by directory-level sidecars (252 cells total: 156 text + 96 image). |
| `results/phase3a-text-matrix/secondary_effects.json` | ~8 effects × 3 metrics (ci_excludes_zero reported) | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_secondary_effects_text.py` | not recorded | 2026-04 | YES_SIDECAR | `results/phase3a-text-matrix/secondary_effects.metadata.json` | `n_iterations=1000` visible in nested bootstrap blocks; seed default resolved in sidecar. |
| `results/phase3a-text-matrix/verifier_summary.json` | per-verifier summary | (no CIs reported directly) | — | — | — | `scripts/summarise_phase3a_text_matrix.py` | — | — | NO-CI | — | Out of scope. |
| `results/phase3c-diversity/track1-image/diversity-analysis-report.json` | many | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_diversity.py` | not recorded | 2026-03-25T07:29Z | YES | — | `metadata.n_bootstrap=1000, metadata.random_seed=42, metadata.n_permutations=10000` explicit. |
| `results/phase3c-diversity/track2-text/diversity-analysis-report.json` | many | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_diversity.py` | not recorded | 2026-03-25 | YES | — | Same. |
| `results/phase3c-diversity/track2-text/diversity-consensus-sweep.json` | many | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_consensus_sweep.py` | not recorded | 2026-03 | YES_SIDECAR | `results/phase3c-diversity/track2-text/diversity-consensus-sweep.metadata.json` | Consensus sweep cells; sibling `diversity-analysis-report.json` has explicit run-level metadata. |
| `results/retest/phase2a-evaluation.json` | 5 × 3 (multi-run) | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/evaluate_retest_all.py` | not recorded | 2026-02 | YES_SIDECAR | `results/retest/phase2a-evaluation.metadata.json` | Uses `analyse_phase2_results.py`-equivalent multi-run bootstrap; constants BOOTSTRAP_ITERATIONS=1000, RANDOM_SEED=42 in script. |
| `results/retest/phase2b-track1-evaluation.json` | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/evaluate_retest_all.py` | not recorded | 2026-02 | YES_SIDECAR | `results/retest/phase2b-track1-evaluation.metadata.json` | Same. |
| `results/retest/phase2b-track2-evaluation.json` | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/evaluate_retest_all.py` | not recorded | 2026-02 | YES_SIDECAR | `results/retest/phase2b-track2-evaluation.metadata.json` | Same. |
| `results/retest/phase2c-{track1,track2,exploratory}-evaluation.json` (3 files) | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/evaluate_retest_all.py` | not recorded | 2026-02 | YES_SIDECAR | `results/retest/phase2c-track1-evaluation.metadata.json`, `.../phase2c-track2-evaluation.metadata.json`, `.../phase2c-exploratory-evaluation.metadata.json` | Same. |
| `results/retest/phase2d-{track1,track2}-evaluation.json` (2 files) | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/evaluate_retest_all.py` | not recorded | 2026-02 | YES_SIDECAR | `results/retest/phase2d-track1-evaluation.metadata.json`, `.../phase2d-track2-evaluation.metadata.json` | Same. |
| `results/retest/phase2e-evaluation.json` | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/evaluate_retest_all.py` | not recorded | 2026-02 | YES_SIDECAR | `results/retest/phase2e-evaluation.metadata.json` | Same. |
| `results/retest/phase3a-{replication,track1,track2}-evaluation.json` (3 files) | as above | bootstrap percentile (multi-run) | 1000 | 42 | tile (multi-run) | `scripts/evaluate_retest_all.py` | not recorded | 2026-02 | YES_SIDECAR | `results/retest/phase3a-replication-evaluation.metadata.json`, `.../phase3a-track1-evaluation.metadata.json`, `.../phase3a-track2-evaluation.metadata.json` | Same. |
| `results/retest/pairwise-bootstrap-comparisons.json` | 70 comparisons × 3 metrics | bootstrap percentile | 1000 | 42 | tile (paired) | `scripts/run_pairwise_tests.py` (pre-permutation era) | not recorded | 2026-02 | YES | — | `metadata.bootstrap_iterations=1000, metadata.random_seed=42` explicit. |
| `results/retest/phase3a-high-text/phase3a-high-text-consensus-sweep.json` | 135 configs × 3 × 1 buffer | bootstrap percentile | 1000 | 42 | tile | `scripts/consensus-sweep-phase3a-high-text.py` | not recorded | 2026-02 | YES | — | `bootstrap_iterations=1000, bootstrap_seed=42` explicit. |
| `results/retest/phase3a-high-text/phase3a-high-text-pairwise.json` | several | bootstrap percentile | 1000 | 42 | tile | `scripts/consensus-sweep-phase3a-high-text.py` | not recorded | 2026-02 | YES | — | Same script writes explicit metadata. |
| `results/pairwise/20m/run_manifest.json` | n/a (manifest) | permutation | 10000 | 42 | tile (permutation) | `scripts/run_pairwise_tests.py` | not recorded | 2026-03-28T06:54Z | YES | — | Manifest records `metadata.n_permutations=10000, metadata.seed=42`; applies to all cells in the tree. |
| `results/pairwise/20m/group_*/*.json` (~32 files) | 1 comparison per file | permutation | 10000 | 42 | tile (permutation) | `scripts/run_pairwise_tests.py` | not recorded | 2026-03-28 | YES | — | Each cell records its own `metadata.n_permutations, metadata.seed`. |
| `results/pairwise/30m/run_manifest.json` | n/a | permutation | 10000 | 42 | tile (permutation) | `scripts/run_pairwise_tests.py` | not recorded | 2026-03-28 | YES | — | As above, 30 m buffer. |
| `results/pairwise/30m/group_*/*.json` (~32 files) | 1 per file | permutation | 10000 | 42 | tile (permutation) | `scripts/run_pairwise_tests.py` | not recorded | 2026-03-28 | YES | — | As above. |
| `results/pairwise/factor-analysis-20m/run_manifest.json` + cells | many | permutation | 10000 | 42 | tile (permutation) | `scripts/run_pairwise_tests.py` | not recorded | 2026-03-28 | YES | — | Cells and manifest both record metadata. |
| `results/pairwise/leaderboard-20m/**`, `leaderboard-30m/**` | each cell | permutation | 10000 | 42 | tile (permutation) | `scripts/run_pairwise_tests.py` | not recorded | 2026-03-28 | YES | — | Same. |
| `results/pairwise/tile-size-30m/**/evaluation.json` (5 files) | 3 × 1 | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-03-28 | YES_SIDECAR | `results/pairwise/tile-size-30m/.metadata.json` (directory-level) | Per-condition evaluation inputs for tile-size comparison (file count corrected from 6 to 5 after enumeration). |
| `results/pairwise/tile-size-mcnemar-30m/tile_size_comparison.json` | per comparison | McNemar + permutation | 10000 | 42 | tile (paired symbol match) | `scripts/compare_tile_sizes.py` | not recorded | 2026-03-28T08:17Z | YES | — | `metadata.seed=42`; McNemar has no bootstrap iteration count. |
| `results/pairwise/prompt-engineering-20m/prompt_engineering_pairwise.json` | several | permutation | 10000 | 42 | tile (permutation) | `scripts/run_pairwise_tests.py` | not recorded | 2026-03 | YES | — | Metadata block verified on 2026-04-20: `metadata.n_permutations=10000, metadata.seed=42` explicit. Upgraded from YES (assumed). |
| `results/secondary-effects/secondary_effects.json` | ~40 interaction contrasts × 3 metrics | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_secondary_effects.py` | not recorded | 2026-02 | YES_SIDECAR | `results/secondary-effects/secondary_effects.metadata.json` | Nested blocks record `n_iterations=1000` per contrast; seed default resolved in sidecar. |
| `results/h10/statistical_analysis.json` | 3 configs × 3 metrics + permutation | bootstrap + permutation | 1000 bootstrap, 10000 perm | 42 | tile | `scripts/compare_wbf_greedy_pv_permutation.py` (or similar) | not recorded | 2026-03 | YES | — | `parameters.n_bootstrap=1000, parameters.n_permutations=10000, parameters.seed=42` explicit. |
| `results/h10/wbf/variant_c_vs_greedy_hp4hn4.json` | 2 configs × 3 metrics | bootstrap percentile | 1000 | 42 | tile | `scripts/compare_wbf_vs_greedy_canonical.py` | not recorded | 2026-03 | YES_SIDECAR | `results/h10/wbf/variant_c_vs_greedy_hp4hn4.metadata.json` | Script defaults; sibling `statistical_analysis.json` has explicit metadata. |
| `results/h10/consensus_dedup_magnitude_diagnostic.json`, `h10_consensus_only_20m.json`, `h10_pool_*_20m.json`, `h10_wbf_consensus_20m.json`, `h10_pv_permutation_020_vs_160.json`, `k5_replicate_sweep.json`, `sweep_results.json`, `verifier_independence_probe.json` | n/a (no CIs) | — | — | — | — | various H10 analysis scripts | — | — | NO-CI | — | Point-estimate threshold sweeps and diagnostic counts; out of scope. |
| `results/h8-v2/{greedy,wbf}/**/evaluation.json` (43 files) | 3 × 4 per file | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-04-15 | YES_SIDECAR | `results/h8-v2/.metadata.json` (directory-level) | Standard `evaluate_detections.py` outputs (file count corrected from ~80 to 43 after enumeration; verifier-sweep subtree contains no evaluation.json). |
| `results/h8-v2/**/threshold_sweep.json` (~10 files) | 21 × 3 per file | bootstrap percentile | 1000 | 42 | tile | `scripts/run_pv.py` | not recorded | 2026-04-15 | YES | — | Each records explicit metadata. |
| `results/h12-v2/{greedy,wbf}/**/evaluation.json` (18 files) | 3 × 4 per file | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-04-15 | YES_SIDECAR | `results/h12-v2/.metadata.json` (directory-level) | Standard. File count corrected from ~30 to 18. |
| `results/h12-v2/permutation-t4/fdr_summary.json` | 3 pairwise contrasts | permutation | 10000 | 42 | tile (permutation) | `scripts/apply_fdr_h12v2.py` + `pairwise_permutation_test.py` | not recorded | 2026-04-15 | YES | — | `n_permutations=10000, seed=42` explicit. |
| `results/h12-v2/permutation-t4/R*/pairwise_permutation_result.json` (3 files) | 1 per file | permutation | 10000 | 42 | tile (permutation) | `scripts/pairwise_permutation_test.py` | not recorded | 2026-04-15 | YES | — | Per-cell metadata. |
| `results/h12-v2/permutation-wbf/**` (parallel structure) | 3 contrasts | permutation | 10000 | 42 | tile (permutation) | same | not recorded | 2026-04-15 | YES | — | WBF track, same defaults. |
| `results/h11-384-pv-diagnostic/pairwise/**/*.json` (6 files) | ~6 comparisons | paired bootstrap + permutation | 1000 bootstrap, 10000 perm | 42 | tile (paired) | `scripts/compute-pairwise-effect-sizes.py` | not recorded | 2026-03-26 | YES | — | Each file records metadata. |
| `results/paper-eval/n1/{384px,512px}/**/evaluation.json` (156 total across subtrees) | 3 × 4 per file | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-03-27 | YES_SIDECAR | `results/paper-eval/.metadata.json` (directory-level) | N=1 baselines; script defaults. Directory sidecar covers all paper-eval evaluate_detections.py outputs. |
| `results/paper-eval/mcc/{384px,512px}/**/evaluation.json` | 3 × 4 per file, some with tile-MCC | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-03-27 | YES_SIDECAR | `results/paper-eval/.metadata.json` (directory-level) | Tile-MCC variants; same defaults. |
| `results/paper-eval/mcc/consensus-pv/**` (subset) | several | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` / `run_pv.py` | not recorded | 2026-03 | YES_SIDECAR | `results/paper-eval/.metadata.json` (directory-level) | Combined consensus + PV cells. |
| `results/paper-eval/single-pass-t0-{20m,30m,40m,50m}/**/evaluation.json` (8 files) | 3 × 1 per file | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-03 | YES_SIDECAR | `results/paper-eval/.metadata.json` (directory-level) | Per-buffer single-pass T=0 evaluations. |
| `results/paper-tables/metrics_master.json` | 100 rows × 3 metric CIs | (aggregate) | 1000 | 42 | tile | `scripts/consolidate_paper_metrics.py` | not recorded | 2026-03-26T20:39Z | YES_SIDECAR | `results/paper-tables/metrics_master.metadata.json` | Aggregate; sidecar documents the chain. Source files all YES/YES_SIDECAR. |
| `results/paper-tables/metrics_master.csv` | same as JSON | (aggregate) | 1000 | 42 | tile | `scripts/consolidate_paper_metrics.py` | not recorded | 2026-03-26 | YES_SIDECAR | `results/paper-tables/metrics_master.metadata.json` (shared with JSON) | CSV export of the same table. |
| `results/paper-tables/pipeline_progression.json` | several | aggregated bootstrap | 1000 | 42 | tile | `scripts/consolidate_paper_metrics.py` | not recorded | 2026-03-26 | YES_SIDECAR | `results/paper-tables/pipeline_progression.metadata.json` | Derived from metrics_master. |
| `results/paper-tables/pro_2x2_matrix.json` | various | (aggregate) | 1000 | 42 | tile | `scripts/consolidate_paper_metrics.py` | not recorded | 2026-03 | YES_SIDECAR | `results/paper-tables/pro_2x2_matrix.metadata.json` | Pro model 2x2. |
| `results/paper-tables/tile_size_comparison.json` | various | (aggregate) | 10000 perm + 1000 boot | 42 | tile (paired) | `scripts/consolidate_paper_metrics.py` | not recorded | 2026-03 | YES_SIDECAR | `results/paper-tables/tile_size_comparison.metadata.json` | Uses McNemar + permutation primary; bootstrap CIs inherited. |
| `results/paper-tables/cost_retrospective.json` | 0 | none | — | — | — | `scripts/consolidate_paper_metrics.py` | not recorded | 2026-03 | YES_SIDECAR | `results/paper-tables/cost_retrospective.metadata.json` | Cost accounting; no CIs. Sidecar present for registry completeness. |
| `results/55maps-cleaned-gt-evaluation/image/evaluation.json` | 3 × 4 | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-04-19T06:06Z | YES_SIDECAR | `results/55maps-cleaned-gt-evaluation/image/evaluation.metadata.json` | Cleaned-GT re-eval of 55maps image track. |
| `results/55maps-cleaned-gt-evaluation/text-high/evaluation.json` | 3 × 4 | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-04-19 | YES_SIDECAR | `results/55maps-cleaned-gt-evaluation/text-high/evaluation.metadata.json` | Same. |
| `results/55maps-cleaned-gt-evaluation/text-min/evaluation.json` | 3 × 4 | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-04-19 | YES_SIDECAR | `results/55maps-cleaned-gt-evaluation/text-min/evaluation.metadata.json` | Same. |
| `results/gold-standard-extended-buffer-sweep/evaluation.json` | 3 × (number of buffers) | bootstrap percentile | 1000 | 42 | tile | `scripts/evaluate_detections.py` | not recorded | 2026-04-18T23:37Z | YES_SIDECAR | `results/gold-standard-extended-buffer-sweep/evaluation.metadata.json` | Extended buffer sweep. |
| `results/gold-standard-subtype-classification/macro_weighted_summary.json` | 4 summary CIs | matched-pair bootstrap | 10000 | 42 | matched-pair (stratified by map) | `scripts/analyse_subtype_classification.py` | recorded in sibling `run_manifest.json` | 2026-04-19/20 | YES | — | `valid_bootstrap_iter=10000, total_bootstrap_iter=10000` in-file; seed and git_commit in `run_manifest.json` in same dir. |
| `results/55maps-image-generalisation/buffer-100m-diagnostics/summary.json` | 0 (descriptive only) | — | — | — | — | `scripts/diagnose_100m_buffer.py` | — | 2026-04-21 | NO-CI | — | No CIs reported; cluster-count and pair-drift diagnostics only. |
| `results/55maps-image-generalisation/buffer-band-lift/summary.json` | 12 rows × 2 CIs (null percentile) | permutation null CI | 1000 | 42 | detection (spatial null; tiles as strata) | `scripts/analyse_buffer_band_lift.py` | not recorded | 2026-04-21 | YES | — | `permutations=1000, seed=42` explicit in top matter. Permutation null CIs, not bootstrap CIs. |
| `results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json` | 5 rows × 3 CIs | review-level bootstrap | 10000 | 42 | review-level (human labels) | `scripts/compute_corrected_f1_multi_buffer.py` | `508f76989...` | 2026-04-21T09:19Z | YES | — | Complete metadata block: `metadata.seed=42, bootstrap_n=10000, git_commit`; methodology, input paths, exclusions all recorded. Gold-standard record. |
| `results/55maps-image-generalisation/ds-human-crosstab/summary.json` | 0 (degenerate) | — | — | — | — | `scripts/analyse_ds_vs_human_review.py` | — | 2026-04-21 | NO-CI | — | D-S posterior degenerated to single value; CIs are NaN. Descriptive crosstab only. Wilson CIs reported for sub-band human-mound-rate where N>0 (none here). |
| `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.json` | 2 × 3 (measured + corrected) | review-level bootstrap + tile bootstrap | 10000 | 42 | review-level (corrected); tile (measured) | `scripts/compute_corrected_f1_human_reviewed.py` | not recorded | 2026-04-20T07:13Z | YES | — | `provenance.n_bootstrap=10000, provenance.seed=42` explicit. Two commensurate CI families — measured (tile-level, inherited from `outputs/55maps-image-generalisation/evaluation/evaluation.json`) and corrected (review-level). Documented in-file. |
| `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.json` | 1 Wilson CI (disagreement rate) + 2 tile-level inherited | review-level bootstrap | 10000 | 42 | review-level | `scripts/crosstab_uncalibrated_vs_calibrated.py` | not recorded | 2026-04-20T07:33Z | YES | — | `provenance.n_bootstrap=10000, provenance.seed=42` explicit. Note: disagreement_rate_ci_95 is Wilson (closed-form), not bootstrap — included for completeness. |
| `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.json` | many bins + sweeps | bootstrap at threshold sweep | 10000 | 42 | review-level | `scripts/crosstab_verifier_vs_human.py` | not recorded | 2026-04 | YES | — | `config.n_bootstrap=10000, config.seed=42` explicit at the end of the file. |
| `outputs/55maps-text-high-generalisation/evaluation/evaluation.json` (post-recovery, BCa N = 10K) | 12 (3 metrics × 4 buffers) | bootstrap BCa | 10000 | 42 | tile | `scripts/evaluate_detections.py` | recorded | 2026-05-02T23:58Z | YES | — | T=0.7 post-recovery re-evaluation (commit `e20f3e18` for the BCa N=10K migration; commit `f533fda5` for the GT-update re-eval). Replaces the 2026-04-18 N=1000 percentile entry above. F1@50m = 0.7920 [0.7820, 0.8017]. |
| `outputs/55maps-text-high-generalisation/full-buffer-eval/evaluation.json` (post-recovery, BCa N = 10K) | 12 | bootstrap BCa | 10000 | 42 | tile | `scripts/evaluate_detections.py` | recorded | 2026-05-02T23:58Z | YES | — | T=0.7 post-recovery full-buffer evaluation; commit `e20f3e18`. |
| `outputs/55maps-text-high-generalisation/extended-buffer-eval/evaluation.json` (post-recovery, BCa N = 10K) | per-buffer F1 + CIs | bootstrap BCa | 10000 | 42 | tile | `scripts/evaluate_detections.py` | recorded | 2026-05-02T23:58Z | YES | — | T=0.7 post-recovery extended-buffer (75/100/125 m); commit `e20f3e18`. |
| `results/55maps-text-high-generalisation/corrected-f1-multi-buffer/summary.json` (post-recovery) | 5 rows × 3 CIs | review-level bootstrap | 10000 | 42 | review-level (human labels) | `scripts/compute_corrected_f1_multi_buffer.py` | `f533fda5fb1528106f4a7b22ea41d1f046cf25ca` | 2026-05-03T00:43Z | YES | — | T=0.7 post-recovery corrected-F1 multi-buffer (commit `f6eaeca9` integrates 6 new reviews + 1 new GT mound from `baf1497a`). F1@50m = 0.8273 [0.8173, 0.8370]. |
| `results/55maps-text-high-generalisation/mcc/evaluation.json` (post-recovery) | tile-level MCC + per-buffer | bootstrap BCa | 10000 | 42 | tile (paired) | `scripts/evaluate_detections.py` (MCC mirror) | recorded | 2026-05-02T23:58Z | YES | — | T=0.7 post-recovery tile-level MCC re-evaluation; MCC@50m = 0.6476 [0.6331, 0.6620]. |
| `results/55maps-text-high-generalisation/paired-vs-min-{20,30,40,50}m/pairwise_permutation_result.json` (4 files; v2 post-recovery) | 1 per file | permutation | 10000 | 42 | tile (paired permutation) | `scripts/run_pairwise_tests.py` | recorded | 2026-05-03 | YES | — | Pairwise-permutation v2 — 3 pairs touching T=0.7 re-run post-recovery; commit `aeb9fb7f`. |
| `results/55maps-text-high-generalisation/paired-vs-high-2026-04-10-50m/pairwise_permutation_result.json` (post-recovery) | 1 | permutation | 10000 | 42 | tile (paired permutation) | `scripts/run_pairwise_tests.py` | recorded | 2026-05-03 | YES | — | Pairwise-permutation v2 — 1 pair vs the 2026-04-10 high reference at 50 m; commit `aeb9fb7f`. |
| `results/55maps-text-high-generalisation/dawid-skene/dawid-skene-results.json` (post-recovery; stable-ID join) | EM posteriors | — | — | 42 | review-level | `scripts/analyse_dawid_skene.py` (post commit `a9e280a3`) | recorded | 2026-05-03 | NO-CI | — | T=0.7 post-recovery D-S re-aggregation using fixed stable-ID join (commit `a9e280a3`); commit `366f9c66`. CIs not computed in this aggregator. |
| `results/55maps-text-high-generalisation/ds-human-crosstab/summary.json` (post-recovery) | crosstab | — | — | — | — | `scripts/analyse_ds_vs_human_review.py` (post commit `a9e280a3`) | recorded | 2026-05-03 | NO-CI | — | T=0.7 post-recovery D-S vs human crosstab; commit `e07dae37`. |
| `results/55maps-generalisation/buffer_sensitivity.json` | per-threshold × 4 buffers | bootstrap percentile | 1000 | 42 | tile | `scripts/analyse_pv_buffer_sensitivity.py` | not recorded | 2026-04 | YES | — | Metadata verified on 2026-04-20: `bootstrap_iterations=1000, seed=42` explicit at top level. Upgraded from YES (assumed). |
| `results/factor-analysis/factor_analysis_results.json` | 0 (p-values only, no CIs) | permutation | 10000 | 42 | tile (permutation) | `scripts/run_pairwise_tests.py` | not recorded | 2026-03 | NO-CI | — | Point effect sizes + p-values only; sibling CSV carries same. Pairwise CIs, where cited, come from `results/pairwise/**/*.json`. |
| `results/tolerance-sensitivity/tolerance-sensitivity.json` | 0 (point estimates) | — | — | — | — | `scripts/analyse_tolerance_sensitivity.py` | — | 2026-03 | NO-CI | — | Point estimates only; no CIs reported. |
| `results/dawid-skene/dawid-skene-results.json` | 0 (EM posteriors only) | — | — | — | — | `scripts/analyse_dawid_skene.py` | — | 2026-04 | NO-CI | — | D-S posterior probabilities; CIs not computed in this file. |
| `results/consensus-build-manifest_20260416T071249Z.json` | 0 | — | — | — | — | `scripts/build_all_consensus.py` | recorded | 2026-04-16 | NO-CI | — | Manifest; no CIs. |
| `results/55maps-cleanup-report.json` | 0 | — | — | — | — | `scripts/55maps-cleanup-analysis.py` | — | 2026-04 | NO-CI | — | Cleanup bookkeeping. |

## Summary counts

Counting distinct file-classes (not individual files), and treating
`leaderboard_all_evaluations.json` + the thousands of `era2/.cache/**`
files as one class each (updated after the 2026-04-20 sidecar pass):

- `YES` (complete metadata in file or co-located manifest): 36
  classes — PV, leaderboard tiers, pairwise permutation, consensus
  analysis reports, aggregate bootstrap-CI files, corrected-F1
  review-level bootstraps, buffer-band-lift, subtype classification,
  plus two formerly "YES (assumed)" classes confirmed on 2026-04-20
  (`55maps-generalisation/buffer_sensitivity.json` and
  `prompt-engineering-20m/prompt_engineering_pairwise.json`).
- `YES_SIDECAR` (resolved metadata in a co-located sidecar,
  `<name>.metadata.json` or directory-level `.metadata.json`): 36
  classes (+ the per-file CSV derivative of metrics_master) covering
  ~520 individual files. Introduced 2026-04-20; see "Sidecar upgrade
  pass" below. Every class previously marked `INFERABLE` has been
  upgraded.
- `INFERABLE` (script default retrievable from version control but
  not materialised alongside the data): **0 classes after the
  2026-04-20 pass.**
- `NO-CI` (file does not report CIs, not in scope): 10+ classes —
  threshold sweep cells, factor-analysis p-values, D-S posteriors,
  manifests, descriptive diagnostics.
- `NO` (metadata not retrievable — requires re-run): **0 classes**.
- `STALE_ENTRY`: 1 class — the registry row describing
  `results/e47-v1-vs-v2/grid-multibuffer/**/evaluation.json` (16
  files) was stale: no `evaluation.json` files actually existed
  under this path on 2026-04-20. The subtree contains only
  `threshold_sweep.json` files (already `YES` via explicit in-file
  metadata) which were moved to
  `archive/v2-verifier-contamination/e47-v1-vs-v2/...` by the
  v2-verifier-contamination quarantine agent during the same
  session. Sidecars were not written; the quarantine agent owns
  any remaining cleanup of the e47-v1-vs-v2 rows.

## Sidecar upgrade pass (2026-04-20)

Motivation: a paper reviewer should not need to open a Python script
and read a `DEFAULT_SEED = 42` line to confirm the bootstrap
specification for a reported CI. The `INFERABLE` state satisfied
reproducibility but not citation ergonomics.

Convention: for a data file `path/to/foo.json`, a sidecar is written
at `path/to/foo.metadata.json` recording the RESOLVED values (not
"script default: 42" but literally `"seed": 42`). For bulk classes
with tens or hundreds of files that share the same specification, a
directory-level sidecar is written at `path/to/.metadata.json` with
a `coverage_pattern` field enumerating the files covered.

Sidecar schema (top-level keys):

- `metadata_version` (string)
- `schema_description` (string, human-readable)
- `target_file` or `target_files` or `coverage_pattern`
- `generated_by_script` (repo-relative path)
- `generated_by_script_version_hash` (git commit at sidecar-writing
  time; original-generation commit added when recoverable)
- `generation_timestamp_iso` (ISO 8601; from the data file's
  `timestamp` key or mtime)
- `bootstrap` (object with `n_iterations`, `seed`, `resampling_unit`,
  `methodology`, `library_entry_point`)
- `invocation` (object documenting the CLI command when available,
  with `source` (run.log, resolved_config.yaml, or script default)
  and `cli_overrides_script_defaults` (boolean))
- `input_files` (when recoverable)
- `notes` (class-specific context)

File counts produced in the 2026-04-20 pass:

| Sidecar type | Count |
|--------------|-------|
| Per-file sidecars (`<name>.metadata.json`) | 41 |
| Directory-level sidecars (`<dir>/.metadata.json`) | 7 |
| Total sidecars | 48 |
| Individual files covered (per-file + directory aggregates) | ~1580 |

Per-file sidecars were written for every paper-headline or
paper-derivative file (the three 55maps generalisation evaluations,
the cleaned-GT trio, gold-standard-extended-buffer-sweep, the seven
phase2a/b/c/d analysis roll-ups, the twelve retest phase2/phase3a
evaluations, the h11 UNINTENDED analysis report, paper-tables
metrics_master / pipeline_progression / pro_2x2_matrix /
tile_size_comparison / cost_retrospective, phase3a-*-matrix
all-evaluations, secondary_effects.json x2, phase3c diversity
consensus sweep, h10 variant_c_vs_greedy_hp4hn4, and the three
per-era leaderboard_all_evaluations files).

Directory-level sidecars were written for the seven bulk classes:
`phase3a-text-matrix/` (156 cells), `phase3a-image-matrix/` (96),
`paper-eval/` (~156), `h8-v2/` (43), `h12-v2/` (18),
`pairwise/tile-size-30m/` (5), and
`leaderboard/era2/.cache/` (~1056). Paper-cited results from these
subtrees are served by the aggregate sidecars in `paper-tables/` and
per-era leaderboard sidecars.

Ambiguities encountered: zero. Every CLI invocation found in a
run.log or resolved_config.yaml specified the same defaults the
scripts use (n=1000, seed=42), so no `cli_overrides_script_defaults`
was flagged `true` anywhere in the pass.

## Provenance chains

- `results/paper-tables/metrics_master.json` →
  `results/paper-eval/flash-*/consensus-analysis-report.json` +
  `results/paper-eval/pv/*/buffer_sensitivity.json` (both sources have
  YES). Aggregate inherits the full specification; document the chain
  when citing.
- `results/leaderboard/era*/leaderboard_tiers_*.json` →
  `results/leaderboard/era*/leaderboard_all_evaluations.json` →
  `results/leaderboard/era2/.cache/evaluations/**` (all share script
  defaults; tier file carries explicit run metadata).
- `results/all-bootstrap-cis.json` → individual `detections_*.geojson`
  raw files under `data/retest/**` (aggregate records the chain via
  `source_file` per entry).
- `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.json`
  (measured block) ← `outputs/55maps-image-generalisation/evaluation/evaluation.json`.

## Recommended durable mitigation

The main structural gap is that `scripts/evaluate_detections.py` does
not write its bootstrap parameters into `evaluation.json`. A one-line
metadata block added to the output dict — `"_metadata": {"n_bootstrap":
n_bootstrap, "seed": seed, "resampling_unit": "tile", "git_commit":
<sha>}` — would move every INFERABLE entry to YES without re-running
any experiments. See `archive/planning-completed-session-81-82/ci-rerun-todo.md` §§ "Durable
mitigation" for the proposed patch.
