# Archive Manifest

**Date**: 2026-04-16
**Reason**: Production scope consolidation — locking in three test tile sets
(Era 1: 340×512, Era 2: 487×384, Era 3: 327×384) plus the 55-map
generalisation set. All non-production-scope results and superseded outputs
archived to prevent confusion during the write-up and leaderboard work.

**Reference**: `results/evaluation-scopes.md` documents the three production
scopes and their nesting relationships.

## Archive categories

### `results-60-tile-validation/` (19 directories + 6 empty placeholders)

Results computed against the old 60-tile `validation_bounds.geojson` scope,
which lacked statistical power to distinguish performance across conditions.
All preregistered hypotheses were subsequently retested at production scale
(340×512 or 487×384).

**Moved from `results/`:**

- `h11-384-consensus-flash-high-image-n10/`
- `h11-384-consensus-flash-high-image-n5/`
- `h11-384-consensus-flash-high-text-n10/`
- `h11-384-consensus-flash-high-text-n30/`
- `h11-384-consensus-flash-high-text-n5/`
- `h11-384-consensus-flash-minimal-image/`
- `h11-384-consensus-flash-minimal-text-t07/`
- `h11-384-consensus-flash-minimal-text-t10/`
- `h11-384-consensus-n10-image/`
- `h11-384-consensus-n5/`
- `h11-384-consensus-pro-high-image-n5/`
- `h11-384-consensus-pro-high-text-n5/`
- `h11-384-pairwise-n5/`
- `h11-384-buffer-sensitivity/`
- `phase3a-consensus/`
- `phase3a-replication/`
- `phase2b-consensus/`
- `h11/` (validation-scope consensus-sweep-384 and wbf)
- `phase2-factorial/`
- `final-report/` (empty placeholder)
- `phase1-library/` (empty placeholder)
- `phase3-followup/` (empty placeholder)
- `phase4-transfer/` (empty placeholder)
- `phase5-exploratory/` (empty placeholder)
- `tables/` (empty placeholder)

**Evidence**: `meta.bounds = inputs/vectors/bounds/384/validation_bounds.geojson`
or `inputs/vectors/bounds/validation_bounds.geojson` confirmed in JSON metadata
for all non-empty directories.

### `results-non-production-tile-sizes/` (1 directory)

Results from tile sizes not included in the three production scopes.

**Moved from `results/`:**

- `h11-256-pv-diagnostic/` — 256px tile variant from H11 tile-size exploration.
  The exclusion of 256px from production scopes is documented in the H11 tile-size
  results narrative (`results/h11-tile-size-results.md`). Source data preserved
  here for the write-up's justification of tile-size choices.

### `outputs-pre-retest-60-tile/` (16 directories + 2 log files + 1 subdir)

Raw detection outputs from the original pre-retest H1–H9 experiments at 60-tile
scope. All have been superseded by the 340-tile retest at `outputs/retest/`.

**Moved from `outputs/`:**

- `phase1-library/` → superseded by `retest/phase2a`
- `phase2a/` → superseded by `retest/phase2a`
- `phase2b/` → superseded by `retest/phase2b`
- `phase2c/` → superseded by `retest/phase2c`
- `phase2d/` → superseded by `retest/phase2d`
- `phase2e/` → superseded by `retest/phase2e`
- `phase2-factorial/` → superseded by `retest/phase2*`
- `phase3a/` → superseded by `retest/phase3a`
- `phase3a-replication/` → superseded by `retest/phase3a-replication`
- `phase3c/` → superseded by `retest/phase3c`
- `phase3d-pilot/` → superseded by H11 PV pipeline
- `phase3d-union/` → superseded by H11 PV pipeline
- `phase3d-experiment-e/` → superseded by H11 PV pipeline
- `phase3-followup/` (empty placeholder)
- `phase4-transfer/` (empty placeholder)
- `phase5-exploratory/` (empty placeholder)
- `phase3a-replication-batch.log`
- `phase3a-replication.log`
- `preliminary-results/` (old 55/60-tile detections from `outputs/results/`)

### `outputs-experimental-pilot/` (7 directories)

Experimental, pilot, or superseded pipeline outputs not associated with any
production evaluation scope.

**Moved from `outputs/`:**

- `flash-lite-pilot/` — Flash Lite model pilot (model discontinued)
- `pv/` (~1.9 GB) — legacy proposer-verifier pipeline, superseded by
  `outputs/h11/proposer-verifier-384/` and related H11 PV work
- `test-phase2b/` — single test run artefact
- `verification/` — early verification attempt
- `standalone-verification/` — batch 1
- `standalone-verification-batch2/` — batch 2
- `standalone-verification-batch3/` — batch 3

**Note**: `results/pv/` (kept in production results) cross-references some
paths under the archived `outputs/pv/`. Those references are historical and
should be updated if `results/pv/` analysis is refreshed.

### `intermediate-calibration/` (6 items)

Intermediate artefacts from within production-scope directories. These are
threshold-tuning and dry-run outputs that informed pipeline development but
are not needed for final leaderboard analysis.

**Moved from within `outputs/`:**

- `h10-calibration-runs/` (from `outputs/h10/calibration-runs/`)
- `h10-calibration-runs-v2/` (from `outputs/h10/calibration-runs-v2/`)
- `dry-run-pool/` (from `outputs/h8-v2/dry-run-pool/`)
- `dry-run-ppc/` (from `outputs/h8-v2/dry-run-ppc/`)
- `dry-run-scale-32/` (from `outputs/h8-v2/dry-run-scale-32/`)
- `dry-run-scale-32-post-fix/` (from `outputs/h8-v2/dry-run-scale-32-post-fix/`)

## Items flagged for user review

The following items were **kept** in production directories but flagged for
scope verification during the leaderboard rebuild:

1. `results/paper-eval/` — mixed 384px/512px, minimal metadata
2. `results/pv/` — PV bootstrap CI aggregation, may reference mixed scopes
3. `results/wbf-greedy-comparison/` — scope to verify
4. `results/tolerance-sensitivity/` — method reference, scope-independent
5. `results/dawid-skene/` — annotation agreement, scope-independent
6. `results/phase3c-diversity/` — scope to verify (likely Era 1 or Era 2)

## Total impact

- **~2.1 GB archived** (dominated by `outputs/pv/` at ~1.9 GB)
- **~43 items moved** across 5 archive categories
- Production directories now contain only Era 1/2/3 + 55-map + reference data

## 2026-04-20 addition: `human-review-sessions/`

**Moved**: `results/55maps-image-generalisation/human-review.csv` →
`archive/human-review-sessions/human-review-55maps-image-uncalibrated-2026-04-20.csv`

**Reason**: 327 reviews completed using the Streamlit app before the 50 m
matching-tolerance circle was added (see `scripts/review_candidates.py`
change the same day). Reviewer was making uncalibrated "close enough?"
judgements on symbol-to-centre proximity; Obs 263 in
`docs/notes/reflections/working-notes.md` documents the ~10-15% per-item
noise this introduced. User restarted the review from scratch with the
calibrated tolerance-circle UI for defensible accuracy.

The archived CSV is preserved for comparison analysis: cross-tabulating the
uncalibrated vs calibrated decisions on the same candidate ids will quantify
how much the tolerance circle shifted the accept/reject boundary, which is
itself a methodology finding.

## 2026-04-24 addition: `h10-h12-v1-retracted-probe/`

**Moved from**:

- `outputs/h10/{consensus, evaluation, verified, verifier-crops, wbf}/` (7,977 tracked files)
- `results/h10/{sweep_results.json, statistical_analysis.json, verifier_independence_probe.{json,md}, k5_replicate_sweep.json, consensus_dedup_magnitude_diagnostic.json}` (6 tracked files)
- `results/h10/wbf/{sweep_results_pool_160_hp4hn4_variant_c.json, variant_c_vs_greedy_hp4hn4.json, variant_c_vs_greedy_hp4hn4.metadata.json}` (3 tracked files)

**Reason**: The H10/H12 v1 library-composition probe (5 pool_160 HP:HN
variants at K=10, launched 2026-04-11) was formally retracted by Obs 235
on 2026-04-14 because the proposer config (`detect_brief-text_pool_160_*`)
has `include_example_images: false` — the library was never transmitted
to the API. Obs 235 declared the "library effect" physically impossible.
The retracted data had remained in the working directories for seven
months; Session 75's Step-4 h10 synthesis re-discovered the retraction
context and physically separated the retracted probe data from the
clean v2 primary-experiment data (which remains in place at
`outputs/h10/evaluation-v2/pool_{020,040,080,160}_hp4hn4/`).

**Preservation rationale**: `CLAUDE.md` §"Unexpected Data as Discovery
Opportunities" + archive-never-delete directive. Obs 235 §"PARTIAL
CORRECTION" retains one valid use of this data (Obs 230 WBF vs greedy
aggregation-method test at hp4hn4 K=10); see archive README for details.

**Authoritative paper-citation summary**: `results/h10/analysis_summary.md`
— scoped to the clean primary experiment only. Cross-hypothesis coverage
of the HP:HN variants is at `results/h8-v2/analysis_summary.md` (Scale-8
/ 16 / 32) and `results/h12-v2/analysis_summary.md` (R1 / R2 / R3).

**Full retraction context**: `archive/h10-h12-v1-retracted-probe/README.md`.
