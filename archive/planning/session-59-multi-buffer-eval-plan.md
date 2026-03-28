# Plan: Comprehensive Multi-Buffer Evaluation for Paper Tables

## Context

The project needs a complete set of F1, Precision, and Recall metrics with 95%
bootstrap CIs at four spatial buffer distances (20, 30, 40, 50 m) for all
paper-critical conditions. This serves two purposes:

1. **Headline metrics**: Complete F1/P/R with CIs for the paper results tables
2. **Spatial tolerance decision**: Compare metrics across buffer distances to
   choose the paper's primary spatial tolerance before running pairwise tests
   and FDR correction

**Key decision**: All conditions will be (re-)evaluated on the **full 487-tile
evaluation bounds** (435 reference mounds) for consistency. Existing 240-tile
results become supplementary. This means re-running consensus evaluations that
previously used validation_bounds.

## What Already Exists

- `bootstrap_ci()` in `lib_advanced_metrics.py` already returns CIs for **all
  three metrics** (F1, P, R) — no core library changes needed
- `analyse_consensus_sweep.py` supports `--buffer-metres` and `--bounds`
- `analyse_pv_buffer_sensitivity.py` supports `--batch` mode with YAML spec
  and evaluates at multiple buffers in one invocation
- The JSON outputs from both scripts contain full CIs for F1, P, R
- All proposer data covers 487 tiles (confirmed via meta.json)

## What's Needed

### New files

| File | Purpose |
|------|---------|
| `scripts/sapphire-paper-eval.sh` | Orchestration script for sapphire |
| `scripts/consolidate_paper_metrics.py` | Reads all result JSONs, produces unified paper table |
| `configs/pv-paper-conditions.yaml` | Batch spec for PV buffer sensitivity |

### No modifications to existing scripts

The existing analysis scripts are mature and correct. The gap is orchestration
and consolidation, not computation.

---

## Step 1: Identify Paper-Critical Conditions

### Consensus conditions (via `analyse_consensus_sweep.py`)

Each evaluated at all pool_size x threshold combinations, best config extracted.

| # | Label | Study dir | Temps | Pools |
|---|-------|-----------|-------|-------|
| 1 | Flash HIGH text | `outputs/h11/pv-diag-384/flash-high-text-n5` | text-t0.7 | 5 10 30 |
| 2 | Flash HIGH image | `outputs/h11/pv-diag-384/flash-high-image-n5` | image-t0.7 | 5 10 |
| 3 | Pro HIGH text | `outputs/h11/pv-diag-384/pro-high-text-n5` | text-t0.7 | 5 |
| 4 | Pro HIGH image | `outputs/h11/pv-diag-384/pro-high-image-n5` | image-t0.7 | 5 |
| 5 | Flash MIN text T=0.7 | `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07` | text-t0.7 | 5 10 30 |
| 6 | Flash MIN text T=1.0 | `outputs/h11/consensus-384-UNINTENDED-T1.0` | 384 | 5 10 30 |
| 7 | Flash MIN image | `outputs/h11/pv-diag-384/image-n5` | image-t0.7 | 5 10 |
| 8 | Single-pass T=0.0 | `outputs/retest/h11-single-pass-384-t0` | brief-text-t0 | 5 10 |

**All use `--bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.**

Total: 8 conditions x 4 buffers = 32 consensus sweep runs.

### PV conditions (via `analyse_pv_buffer_sensitivity.py`)

Each evaluated at its optimal threshold at all 4 buffers.

| # | Label | Notes |
|---|-------|-------|
| 1 | Flash HIGH text 4-of-5 + Flash min vf | Best overall PV result |
| 2 | Flash HIGH text 16-of-30 + Flash min vf | Best N=30 PV |
| 3 | Flash HIGH text 9-of-10 + Flash min vf | Best N=10 PV |
| 4 | Pro HIGH text 3-of-5 + Flash min vf | Pro proposer comparison |
| 5 | Text baseline + Flash min vf | Single-pass PV baseline |
| 6 | Image baseline + Flash min vf | Single-pass PV baseline |
| 7 | Flash HIGH text 4-of-5 + Flash medium vf | Verifier thinking comparison |
| 8 | Flash HIGH image 3-of-5 + Flash min vf | Best image PV |

**Exact conditions and thresholds to be confirmed** from the existing
`threshold_sweep.json` optimal results before creating the batch YAML.

Total: ~8 conditions, each at 4 buffers in one invocation.

---

## Step 2: Create Orchestration Script

**File**: `scripts/sapphire-paper-eval.sh`

Pattern follows `scripts/sapphire-overnight-analysis.sh`.

```text
Section A: Consensus sweeps (32 runs)
  For each of 8 conditions x 4 buffers:
    python3 scripts/analyse_consensus_sweep.py \
      --study-dir $STUDY_DIR \
      --output-dir results/paper-eval/${COND_NAME}-${BUFFER}m \
      --temperatures $TEMPS \
      --pool-sizes $POOLS \
      --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
      --buffer-metres $BUFFER \
      --quiet

Section B: PV buffer sensitivity (~8 conditions)
    python3 scripts/analyse_pv_buffer_sensitivity.py \
      --batch configs/pv-paper-conditions.yaml \
      --output-dir results/paper-eval/pv \
      --buffers 20 30 40 50 \
      --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
      --bootstrap 1000 --seed 42
```

**Output dir**: `results/paper-eval/` (new, clean directory for this evaluation).

**Estimated runtime on sapphire**: ~20-30 minutes total (32 consensus runs at
~30s each parallelised internally + 8 PV conditions at ~6s per buffer).

---

## Step 3: Create PV Batch YAML

**File**: `configs/pv-paper-conditions.yaml`

Before writing this, read the optimal thresholds from existing
`results/h11-384-pv-diagnostic/*/threshold_sweep.json` files. Each entry needs:
- `label`: human-readable name
- `probabilities`: path to probabilities.json
- `manifest`: path to candidate_manifest.json
- `threshold`: optimal probability threshold from the existing sweep

---

## Step 4: Create Consolidation Script

**File**: `scripts/consolidate_paper_metrics.py`

**Purpose**: Read all result JSONs, extract paper-relevant metrics, produce a
unified master table.

**Inputs**:

1. Consensus results: `results/paper-eval/*/consensus-analysis-report.json`
   - Extract `global_optimum` from each report (best config at that buffer)
   - Also extract specific configs for named comparisons (e.g., N=5 best,
     N=10 best, N=30 best)

2. PV results: `results/paper-eval/pv/*/buffer_sensitivity.json`
   - Each file has results at all 4 buffers

**Outputs**:

1. `results/paper-tables/metrics_master.json` — full structured data
2. `results/paper-tables/metrics_master.csv` — flat table with columns:

   ```text
   condition_type, condition_label, buffer_metres,
   f1, f1_ci_lower, f1_ci_upper,
   precision, p_ci_lower, p_ci_upper,
   recall, r_ci_lower, r_ci_upper,
   n_detections, config_details
   ```

3. `results/paper-tables/spatial_tolerance_comparison.md` — pivoted Markdown
   table: conditions as rows, buffer distances as column groups, showing
   F1 [CI] at each. This is the decision-support table for choosing headline
   spatial tolerance.

**Design principles**:
- Reusable: CLI with `--input-dir` and `--output-dir` args
- Extensible: condition registry as YAML or embedded dict, easy to add conditions
- Publication-ready: CSV suitable for LaTeX import, Markdown for quick review
- Include `delta_from_20m` column showing metric change at relaxed buffers

---

## Step 5: Run on Sapphire and Consolidate

```bash
# On sapphire:
ssh sapphire
cd ~/Code/map-reader-llm && git pull && source .venv/bin/activate
nohup bash scripts/sapphire-paper-eval.sh \
    > results/paper-eval/sapphire-eval.log 2>&1 &

# After completion, consolidate (can run locally or on sapphire):
python3 scripts/consolidate_paper_metrics.py \
    --input-dir results/paper-eval \
    --output-dir results/paper-tables
```

---

## Step 6: Pause — Spatial Tolerance Decision

Review `results/paper-tables/spatial_tolerance_comparison.md`. Key questions:

- Does the ranking of conditions change between buffers?
- How much does F1 improve from 20m to 30m? Is it a ceiling effect or
  genuine spatial mismatch being resolved?
- What buffer distance best reflects the practical use case (a human
  surveyor checking flagged locations)?
- Is there a natural inflection point?

**This decision gates all downstream pairwise tests and FDR correction.**

---

## Verification

1. **Spot-check**: Compare a few 20m results from the new full-bounds
   evaluation against existing 240-tile results. F1 values will differ
   (different ground truth set) but directions should be consistent.
2. **Completeness**: The consolidation script should report any missing
   condition x buffer combinations.
3. **CI sanity**: All CIs should be narrower at full bounds (larger sample)
   than at validation bounds.
4. **Lint**: `ruff check` on new Python script, `markdownlint` on any new .md.

---

## Critical Files

| File | Role |
|------|------|
| `scripts/analyse_consensus_sweep.py` | Consensus evaluation engine (invoke, don't modify) |
| `scripts/analyse_pv_buffer_sensitivity.py` | PV evaluation engine (invoke, don't modify) |
| `scripts/lib_advanced_metrics.py` | Core bootstrap_ci(), calculate_f1_internal() |
| `scripts/sapphire-overnight-analysis.sh` | Template for the new orchestration script |
| `scripts/consolidate_pv_bootstrap_cis.py` | Pattern for consolidation script design |
| `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | 487-tile bounds for all evaluations |
| `inputs/vectors/references/mounds-reference.geojson` | Ground truth (435 mounds in full bounds) |
