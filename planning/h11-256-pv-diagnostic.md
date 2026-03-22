# Plan: 256px Tile Size Diagnostic — Does F1 Continue to Rise?

## Context

384px tiles achieved a new project-best F1=0.883 (text 6-of-10 + PV), significantly beating 512px (F1=0.831, p=0.002). The mechanism is higher recall from increased mound-to-tile area ratio, rescued by consensus + PV filtering.

The question: does this trend continue at 256px, or has it peaked? The early H11 pilot showed 256px at P=0.10, R=0.90 — terrible precision but the highest recall. With consensus + PV, that precision penalty might be recoverable.

**Approach**: Two targeted configs as a diagnostic, not a full sweep. N=1 smoke test first, then N=5 for a consensus sweep.

## Tile counts and costs

| Metric | 256px | 384px | 512px |
|--------|------:|------:|------:|
| Total tiles (raw) | 1,152 | 611 | 360 |
| Clean tiles (est., excl. calibration) | ~918 | 487 | 340 |
| Tiles per raster | 288 | ~130 | ~85 |
| Stride | 224 | 336 | 448 |
| Mound-to-tile ratio | 8–20% | 5–13% | 4–10% |

### Cost estimate

| Config | Proposer calls | PV verification (est.) | Batch cost |
|--------|---:|---:|---:|
| N=1, T=0.0 (smoke test) | 918 | ~2,000 | ~$0.71 |
| N=5, T=0.7 (consensus) | 4,590 | ~1,500 × 5 thresholds | ~$3.20 |
| **Total** | **5,508** | **~9,500** | **~$3.91** |

---

## Execution plan

### Step 0: Generate 256px tiles

```bash
python scripts/preprocess_tiling.py \
    --tile-size 256 --overlap 32 --output-dir inputs/tiles_256
```

### Step 1: Create full evaluation manifest (excluding calibration overlap)

Same approach as 384px:
1. List all PNGs → full manifest
2. Load calibration bounds, spatial-join to find overlapping tiles
3. Exclude overlapping tiles from manifest
4. Generate 256px evaluation bounds GeoJSON

### Step 2: Create study YAMLs

Two files:
- `studies/h11-256-pv-diag-text-baseline.yaml` — N=1, T=0.0, text-only
- `studies/h11-256-pv-diag-text-n5.yaml` — N=5, T=0.7, text-only

Text-only track only (image track is consistently worse — confirmed at both 384px and 512px).

Key fields:
```yaml
inputs:
  manifest: inputs/tiles_256/full_evaluation_manifest.json
  tile_size: 256
  tiles_dir: inputs/tiles_256
  ground_truth: inputs/vectors/references/mounds-reference.geojson
  bounds: inputs/vectors/bounds/256/full_evaluation_bounds.geojson
```

### Step 3: Smoke test — N=1 baseline

Launch Config A (text N=1, T=0.0, 918 tiles) via Batch API.

```bash
nohup .venv/bin/python3 scripts/run_phase2.py \
  studies/h11-256-pv-diag-text-baseline.yaml \
  --mode batch --max-batch-jobs 5 \
  > outputs/h11/pv-diag-256/text-baseline.log 2>&1 &
```

**Gate checks** (after completion):
- 918 tiles processed (or close — some edge tiles may fail)
- Detection count sanity: expect ~2,000–3,000 (higher FP density at 256px)
- Detections/tile: expect ~2.5 (similar per-tile rate)

### Step 4: Smoke test PV pipeline

Run the full PV pipeline on the N=1 output:
1. Extract 150×150 crops from rasters
2. Verify via Batch API (adversarial text verifier)
3. Threshold sweep with bootstrap CIs

**Decision gate**: If 256px N=1 + PV F1 < 0.75, the 256px pathway is unlikely to beat 384px best (0.883) and we can stop. If F1 ≥ 0.75, proceed to N=5.

### Step 5: N=5 consensus run (if gate passes)

Launch Config B (text N=5, T=0.7) via Batch API.

```bash
nohup .venv/bin/python3 scripts/run_phase2.py \
  studies/h11-256-pv-diag-text-n5.yaml \
  --mode batch --max-batch-jobs 5 \
  > outputs/h11/pv-diag-256/text-n5.log 2>&1 &
```

### Step 6: Full PV pipeline on N=5 consensus

1. Compute consensus GeoJSON at all 5 thresholds (1-of-5 through 5-of-5)
2. Extract crops for each threshold
3. PV verify each crop set (6 total: 5 thresholds + N=1 baseline)
4. Threshold sweep with bootstrap CIs for all 6

### Step 7: Fair paired comparison

Use `compare-384-vs-512.py` approach (spatial-join to common tile grid).

Compare against both 384px and 512px:
- 256px text 3-of-5 + PV vs 384px text 6-of-10 + PV (current best)
- 256px text 3-of-5 + PV vs 512px text 5-of-10 + PV
- 256px text N=1 + PV vs 384px text N=1 + PV vs 512px text N=1 + PV

Use the **256px tile grid** as the common footprint (smallest, so both 384px and 512px detections can be clipped to it).

---

## Files to create

- `inputs/tiles_256/` — generated tiles (~918 clean after exclusion)
- `inputs/tiles_256/full_evaluation_manifest.json`
- `inputs/vectors/bounds/256/full_evaluation_bounds.geojson`
- `studies/h11-256-pv-diag-text-baseline.yaml`
- `studies/h11-256-pv-diag-text-n5.yaml`
- `outputs/h11/pv-diag-256/` — results directory

## Existing infrastructure to reuse

- `scripts/preprocess_tiling.py` — tile generation
- `scripts/generate_tile_bounds.py` — bounds generation
- `scripts/run_phase2.py` — batch proposer execution
- `scripts/lib_consensus.py` — consensus merging
- `scripts/extract_candidates.py` — crop extraction
- `scripts/run_pv.py` — PV verification
- `scripts/evaluate_pv_results.py` — threshold sweep evaluation
- `scripts/compare-384-vs-512.py` — fair paired comparison (adapt for 3-way)

## Verification

1. **Lint**: `ruff check` on any new/modified scripts
2. **Tests**: `pytest tests/ -m tier1`
3. **Code audit**: `/audit` on any new scripts
4. **Sanity checks**: tile count ~918, detection density ~2.5/tile, per-tile rate consistent with 384px and 512px
5. **Smoke test gate**: N=1 + PV F1 ≥ 0.75 before proceeding to N=5
