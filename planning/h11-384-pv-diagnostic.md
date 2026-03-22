# Plan: 384px Diagnostic PV Experiments

## Context

We need to characterise how 384px tiles interact with the Proposer-Verifier (PV) pipeline before committing to expensive N=30 runs. At 512px, the breakthrough insight was that PV F1 tracks **proposer recall** — moderate consensus (3–5 of 10) feeds the verifier a high-recall, moderate-precision candidate set, yielding project-best F1=0.831.

At 384px, single-pass recall is already 0.877 (vs 0.725 at 512px), but precision collapses to 0.272. The previous H11 PV runs used **single-pass proposers only** (F1=0.682). Nobody has tested **consensus + PV at 384px** — the combination that was transformative at 512px.

**Goal**: Run 4 proposer configurations over the **full evaluation area** (matching the 512px production footprint) that yield comprehensive diagnostic analyses across all thresholds, revealing whether 384px + PV can match or exceed 512px + PV, and whether consensus adds value given recall saturation.

### Tile coverage

The 384px tiles already exist: **611 PNGs** across all 4 map sheets (K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1). However, only a 240-tile **validation** manifest exists — a subset covering ~40% of the area. The 512px production runs use 340 tiles (`full_evaluation_manifest.json`). We need to create a full evaluation manifest for 384px listing all 611 tiles, plus corresponding bounds.

### Temperature correction

Consensus runs **must** use T=0.7 (not T=0.0). At T=0.0 the model is near-deterministic, so multiple passes produce near-identical outputs and consensus voting collapses to ~N=1. T=0.7 was the Phase 3a optimum for both tracks. The T=0.0 runs are explicitly deterministic single-pass baselines (N=1).

---

## Proposer Configurations (4 runs)

All use **611-tile** 384px full evaluation manifest (to be created — see Step 0).

| Config | Track | N | Temperature | Proposer calls | Purpose |
|--------|-------|--:|---:|---:|---|
| **A** | Text (`detect_brief-text.json`) | 10 | 0.7 | 6,110 | Full text consensus sweep; subsumes N=5 |
| **B** | Image (`library_plus-hp.json`) | 5 | 0.7 | 3,055 | Modality consensus comparison |
| **C** | Text (`detect_brief-text.json`) | 1 | 0.0 | 611 | Deterministic text single-pass baseline |
| **D** | Image (`library_plus-hp.json`) | 1 | 0.0 | 611 | Deterministic image single-pass baseline |

**Total proposer: 10,387 calls**

---

## Analyses (full threshold sweeps)

All threshold sweeps run in full — no truncation. Local analysis is cheap; run on sapphire for performance.

### Primary analyses (named, with specific diagnostic questions)

| # | Analysis | Source | Candidates (est.) | Diagnostic question |
|---|----------|--------|---:|---|
| 1 | Text N=1, T=0.0 → PV | Config C | ~1,450 | **Text baseline**: deterministic 384px single-pass + PV. Comparison anchor. |
| 2 | Image N=1, T=0.0 → PV | Config D | ~1,450 | **Image baseline**: does text-only advantage hold at 384px single-pass + PV? |
| 3 | Text 1-of-10 → PV | Config A | ~1,450 | **Temperature effect**: does diverse single-pass (T=0.7) beat deterministic (T=0.0) through PV? |
| 4 | Text 5-of-10 → PV | Config A | ~500–750 | **Core experiment**: does the 512px Goldilocks zone work at 384px? Headline comparison to 512px best (F1=0.831). |
| 5 | Text 10-of-10 → PV | Config A | ~250–400 | **Diminishing returns**: does strict consensus over-filter? Go/no-go for N>10. |
| 6 | Image 3-of-5 → PV | Config B | ~750–1,000 | **Modality + consensus**: paired with #4 for text vs image under moderate consensus + PV. |

*Candidate estimates scaled from H11 240-tile baseline (~570 at single-pass) to 611-tile full evaluation (~1,450).*

### Full threshold sweeps (run all, not just the named analyses above)

- **Config A**: 10 PV runs — 1-of-10, 2-of-10, ..., 10-of-10 (full sweep)
- **Config B**: 5 PV runs — 1-of-5, 2-of-5, ..., 5-of-5 (full sweep)
- **Config C**: 1 PV run (single-pass baseline, no consensus)
- **Config D**: 1 PV run (single-pass baseline, no consensus)

**Total: 17 PV verification runs** (10 + 5 + 1 + 1)

**Note**: Several PV runs will exceed 1,000 candidates (the loose thresholds on 611 tiles produce ~1,450). Per project rules, all PV runs use Batch API. The largest single run (~1,450 candidates) is flagged but within reasonable bounds — no separate discussion needed.

### Full evaluation sweep

Every PV output gets full bootstrap CI evaluation (F1, precision, recall). The 17 verified GeoJSONs are evaluated against ground truth with pairwise comparisons for the 6 named analyses above plus any interesting patterns from the sweeps.

Run evaluation + bootstrap on **sapphire** for performance. Expect <10 min for the full sweep.

---

## Cost Estimate

### Proposer stage

| | Calls | Batch ($0.0005/call) | Real-time ($0.001/call) |
|---|---:|---:|---:|
| Config A (text N=10) | 6,110 | $3.06 | $6.11 |
| Config B (image N=5) | 3,055 | $1.53 | $3.06 |
| Config C (text N=1) | 611 | $0.31 | $0.61 |
| Config D (image N=1) | 611 | $0.31 | $0.61 |
| **Subtotal** | **10,387** | **$5.19** | **$10.39** |

### PV verification stage

17 verification runs. Candidate counts range from ~250 (strict consensus) to ~1,450 (single-pass/loose). Estimated total: ~14,000 verification calls.

| | Calls | Batch (~$0.000125/call) | Real-time (~$0.00025/call) |
|---|---:|---:|---:|
| All 17 PV runs | ~14,000 | ~$1.75 | ~$3.50 |

### Totals

| Mode | Proposer | PV | **Total** |
|---|---:|---:|---:|
| **Batch** | $5.19 | $1.75 | **~$6.94** |
| Real-time | $10.39 | $3.50 | ~$13.89 |

**Recommendation**: Batch for everything. Shares queue with running Phase 3c processes.

---

## Execution Plan

### Step 0: Create full evaluation manifest and bounds for 384px

The 384px tiles exist (611 PNGs) but only a 240-tile validation manifest exists. Create the production manifest and bounds.

**0a. Create `inputs/tiles_384/full_evaluation_manifest.json`**

List all 611 PNG filenames in `inputs/tiles_384/` as a JSON array (matching the format of `inputs/tiles/full_evaluation_manifest.json`).

```bash
python3 -c "
import json
from pathlib import Path
tiles = sorted(p.name for p in Path('inputs/tiles_384').glob('*.png'))
json.dump(tiles, open('inputs/tiles_384/full_evaluation_manifest.json', 'w'), indent=2)
print(f'Created manifest with {len(tiles)} tiles')
"
```

**0b. Generate `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`**

Use the existing bounds generation script:

```bash
python scripts/generate_tile_bounds.py \
    --manifest inputs/tiles_384/full_evaluation_manifest.json \
    --tiles-dir inputs/tiles_384 \
    --tile-size 384 \
    --output inputs/vectors/bounds/384/full_evaluation_bounds.geojson
```

**0c. Verify**: Confirm manifest has 611 entries, bounds GeoJSON has 611 features, and the geographic extent matches the 512px full evaluation bounds.

### Step 1: Create 4 study YAMLs

Create study YAML files for each proposer config. `run_phase2.py` supports 384px via `inputs.tile_size: 384`.

**Files to create:**

- `studies/h11-384-pv-diag-text-n10.yaml`
- `studies/h11-384-pv-diag-image-n5.yaml`
- `studies/h11-384-pv-diag-text-baseline.yaml`
- `studies/h11-384-pv-diag-image-baseline.yaml`

Key YAML fields (common):

```yaml
inputs:
  manifest: inputs/tiles_384/full_evaluation_manifest.json
  tile_size: 384
  tiles_dir: inputs/tiles_384
  ground_truth: inputs/vectors/references/mounds-reference.geojson
  bounds: inputs/vectors/bounds/384/full_evaluation_bounds.geojson
```

Per-config specifics:

- **Config A** (text N=10): `detect_brief-text.json`, T=0.7, runs=10, thinking=minimal
- **Config B** (image N=5): `library_plus-hp.json`, T=0.7, runs=5, thinking=minimal
- **Config C** (text baseline): `detect_brief-text.json`, T=0.0, runs=1, thinking=minimal
- **Config D** (image baseline): `library_plus-hp.json`, T=0.0, runs=1, thinking=minimal

Output directories:

- `outputs/h11/pv-diag-384/text-n10/`
- `outputs/h11/pv-diag-384/image-n5/`
- `outputs/h11/pv-diag-384/text-baseline/`
- `outputs/h11/pv-diag-384/image-baseline/`

### Step 2: Smoke test — Config C only (text N=1, T=0.0)

Before committing to the full ~24,000 API calls, run Config C as a smoke test. This is the cheapest config (611 calls, ~$0.31 batch) and validates:

1. The new 611-tile manifest works with `run_phase2.py`
2. Tile-size 384 override is handled correctly
3. Detection counts are reasonable (~1,450 expected, scaled from 570/240 tiles)
4. Crop extraction works on the full evaluation area
5. PV verifier processes 384px-sourced crops correctly

```bash
nohup .venv/bin/python3 scripts/run_phase2.py \
  studies/h11-384-pv-diag-text-baseline.yaml \
  --mode batch --max-batch-jobs 5 \
  > outputs/h11/pv-diag-384/text-baseline.log 2>&1 &
```

**Gate**: After Config C completes, verify:

- 611 tiles processed per run (check meta file)
- Detection count ~1,450 (±30% is acceptable; major deviation signals a problem)
- Crop extraction succeeds with 0 tile fallbacks
- PV verification runs and produces bimodal probability distribution
- F1 is in the expected range (≥0.60, based on H11 384px PV baseline of 0.682 on 240 tiles)

**If smoke test passes** → launch remaining 3 configs in parallel.
**If smoke test fails** → diagnose before spending further.

### Step 3: Launch remaining proposer runs (Batch API)

After smoke test passes, launch Configs A, B, D in parallel.

```bash
# Config D (image baseline — cheap, gives early image-track signal)
nohup .venv/bin/python3 scripts/run_phase2.py \
  studies/h11-384-pv-diag-image-baseline.yaml \
  --mode batch --max-batch-jobs 3 \
  > outputs/h11/pv-diag-384/image-baseline.log 2>&1 &

# Config A (largest — text N=10)
nohup .venv/bin/python3 scripts/run_phase2.py \
  studies/h11-384-pv-diag-text-n10.yaml \
  --mode batch --max-batch-jobs 5 \
  > outputs/h11/pv-diag-384/text-n10.log 2>&1 &

# Config B (image N=5)
nohup .venv/bin/python3 scripts/run_phase2.py \
  studies/h11-384-pv-diag-image-n5.yaml \
  --mode batch --max-batch-jobs 5 \
  > outputs/h11/pv-diag-384/image-n5.log 2>&1 &
```

**Quota check** (concurrent with Phase 3c Track 1 + Track 2):

- Phase 3c T1: --max-batch-jobs 5
- Phase 3c T2: --max-batch-jobs 5
- Diagnostic (Step 3): 3 + 5 + 5 = 13
- **Total: 23 concurrent jobs** (well within 100 limit)
- **Storage**: text JSONL ~13 MB × 10 jobs + image JSONL ~460 MB × 5 jobs = ~2.4 GB (well within 20 GB after sweep)

*JSONL sizes scaled from 240-tile baseline: text ~5 MB → ~13 MB, image ~180 MB → ~460 MB for 611 tiles.*

### Step 4: Compute consensus GeoJSON (post-proposer)

For each multi-run config, merge per-run GeoJSON files into consensus GeoJSON at **every** vote threshold. Full sweeps only.

**Required**: A consensus-merging script that:

1. Reads N per-run GeoJSON files (proposer outputs)
2. Spatially clusters detections within a merge radius
3. Counts votes per cluster
4. Outputs filtered GeoJSON at each threshold (1-of-N through N-of-N)

**Check first**: `scripts/analyse_consensus_sweep.py` may already produce consensus GeoJSON output, or `scripts/merge_consensus.py` / similar may exist. If not, we need a small script.

The consensus merge should use the same spatial matching parameters as the evaluation pipeline (likely 15m merge radius based on mound symbol size).

**Output**: One GeoJSON per (config, threshold) combination:

- Config A: 10 files (text_1of10.geojson through text_10of10.geojson)
- Config B: 5 files (image_1of5.geojson through image_5of5.geojson)
- Config C: 1 file (text_baseline.geojson) — no consensus needed
- Config D: 1 file (image_baseline.geojson) — no consensus needed

**Total: 17 consensus GeoJSON files**

### Step 5: Extract crops for each of the 17 GeoJSON files

For each consensus GeoJSON (and the baselines), extract 150×150 crops from source rasters.

```bash
python scripts/extract_candidates.py \
    --proposer <consensus_geojson> \
    --rasters-dir inputs/rasters \
    --output-dir outputs/h11/pv-diag-384/crops/<threshold_name> \
    --padding 75
```

This produces `candidate_manifest.json` + crop PNGs for each threshold.

Crop extraction is tile-size-agnostic (always 150×150 from source GeoTIFF rasters — the E33 fix).

**Check for fallback**: If any extraction summary shows "From tiles (fallback)" > 0, flag immediately.

### Step 6: Run PV verifier on all 17 crop sets (Batch API)

For each crop set, run the adversarial text-only verifier.

**Verifier config**: `prompts/configs/verify_adversarial-text.json` (the project's best verifier — 71% FP rejection rate, 97.4% TP preservation at 512px).

```bash
# For each of the 17 threshold directories:
python scripts/run_pv.py verify \
    --crops-dir outputs/h11/pv-diag-384/crops/<threshold_name> \
    --config prompts/configs/verify_adversarial-text.json \
    --output-dir outputs/h11/pv-diag-384/verified/<threshold_name> \
    --mode batch
```

**Flag**: Some threshold/config combinations will produce >500 candidates. Per project rules, these should use Batch API (which we're already planning). The largest sets (~570 candidates) are well within the 1,000-candidate discussion threshold.

### Step 7: Evaluate — full sweep with bootstrap CIs (on sapphire)

Run evaluation against ground truth for **all 17 verified GeoJSONs**. Full bootstrap CIs, no truncation.

```bash
# On sapphire:
python scripts/evaluate_pv_results.py \
    --verified-dir outputs/h11/pv-diag-384/verified/ \
    --ground-truth inputs/vectors/references/mounds-reference.geojson \
    --bounds inputs/vectors/bounds/validation_bounds.geojson \
    --output results/h11-384-pv-diagnostic/ \
    --bootstrap 10000
```

**Pairwise comparisons** (all 6 named analyses):

1. Analysis 1 vs 2: text vs image at single-pass T=0.0
2. Analysis 1 vs 3: T=0.0 vs T=0.7 single-pass (text)
3. Analysis 1 vs 4: single-pass vs moderate consensus (text)
4. Analysis 4 vs 5: moderate vs strict consensus (Goldilocks test)
5. Analysis 4 vs 512px best (F1=0.831): **the headline comparison**
6. Analysis 4 vs 6: text vs image at moderate consensus

Plus: full threshold-vs-F1 curves for both text (10 points) and image (5 points) sweeps, plotted against 512px equivalents.

---

## Key Files

### Existing (reuse)

- `scripts/run_phase2.py` — proposer batch execution
- `scripts/extract_candidates.py` — crop extraction from rasters
- `scripts/5_verify_crops.py` / `scripts/run_pv.py` — PV verification
- `scripts/evaluate_pv_results.py` — evaluation with bootstrap CIs
- `scripts/analyse_consensus_sweep.py` — consensus analysis utilities
- `scripts/lib_advanced_metrics.py` — pairwise bootstrap infrastructure
- `prompts/configs/detect_brief-text.json` — text-only proposer config
- `prompts/configs/library_plus-hp.json` — image-track proposer config
- `prompts/configs/verify_adversarial-text.json` — PV verifier config
- `inputs/tiles_384/` — 611 pre-generated 384px tile PNGs
- `scripts/generate_tile_bounds.py` — bounds generation from manifest
- `scripts/preprocess_tiling.py` — tile generation (if additional tiles needed)
- `inputs/vectors/references/mounds-reference.geojson` — ground truth

### To create

- `inputs/tiles_384/full_evaluation_manifest.json` — 611-tile manifest (Step 0a)
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` — bounds for 611 tiles (Step 0b)
- `studies/h11-384-pv-diag-text-n10.yaml`
- `studies/h11-384-pv-diag-image-n5.yaml`
- `studies/h11-384-pv-diag-text-baseline.yaml`
- `studies/h11-384-pv-diag-image-baseline.yaml`
- Consensus-merging script (if not already available — check first)

---

## Verification

1. **Pre-flight**: Confirm 384px tiles exist (611 PNGs in `inputs/tiles_384/`), full evaluation manifest has 611 tiles, bounds GeoJSON has matching extent to 512px full evaluation
2. **Proposer check**: After each config completes, verify tile count in output (611 per run), spot-check detection counts (expect ~1,450 for single-pass text, scaled from 570/240 tiles)
3. **Consensus check**: Verify vote counts decrease monotonically with threshold (1-of-N has most detections, N-of-N has fewest)
4. **Crop check**: Verify crop count matches consensus detection count, no "From tiles (fallback)" in extraction summary
5. **PV check**: Verify all candidates processed (0 failures), spot-check mound_probability distribution is bimodal
6. **Evaluation**: Full bootstrap CIs on all 17 verified outputs, pairwise comparisons for named analyses, threshold-vs-F1 curves

## Decision Points

After results are in:

- If Analysis 4 (text 5-of-10 + PV) matches 512px best → 384px is viable, proceed to full evaluation
- If Analysis 1 ≈ Analysis 4 → consensus adds no value at 384px (recall saturated), use N=1 + PV (massive cost saving: 2 calls/tile)
- If Analysis 5 << Analysis 4 → strict consensus over-filters, skip N>10
- If Analysis 2 ≈ Analysis 1 → modality doesn't matter at 384px single-pass + PV
- If Analysis 6 ≈ Analysis 4 → modality doesn't matter at 384px consensus + PV (consistent with H11 finding without PV)
- Threshold-vs-F1 curves reveal the optimal operating point and whether the 384px Goldilocks zone differs from 512px
