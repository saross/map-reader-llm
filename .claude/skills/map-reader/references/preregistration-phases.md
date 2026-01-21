# Preregistration Phases

Execution procedures for the preregistered VLM burial mound detection study. This document covers Phase 1 through Phase 4.

---

## Phase Overview

| Phase | Purpose | Tiles | Key Outputs |
|-------|---------|-------|-------------|
| Phase 1 | Library Construction | 20 calibration | Hard example library |
| Phase 2a | H1 Baseline Testing | 20 calibration | Image-only vs text performance |
| Phase 2b | H5-H7 Parameter Tuning | 20 calibration | Optimal text level, temperature |
| Phase 2c | H8 Library Scale | 20 calibration | Optimal library composition |
| Phase 3 | Holdout Validation | Holdout set | Final performance estimates |
| Phase 4 | Production Deployment | Full region | Complete detection coverage |

---

## Phase 1: Library Construction

**Goal**: Build the hard example library by identifying systematic detection failures.

### Pre-Flight Checklist

- [ ] API key configured (`GOOGLE_API_KEY` environment variable)
- [ ] Calibration tiles present: `inputs/tiles/*/` (all map directories)
- [ ] Ground truth exists: `inputs/vectors/references/mounds-reference.geojson`
- [ ] Calibration bounds exist: `inputs/vectors/bounds/calibration_bounds.geojson`
- [ ] Baseline config exists: `prompts/configs/library_pure-positive-canon.json`
- [ ] Canon example symlinks exist: `inputs/examples/neutral/example_01-04.png`
- [ ] Null tile symlinks exist: `inputs/examples/neutral/example_15-17.png`

### Step 1: Run Baseline Detection (5 passes)

```bash
for i in $(seq -w 1 5); do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/library_pure-positive-canon.json \
        --manifest inputs/tiles/calibration_manifest.json \
        --output-dir outputs/phase1-library/pass_${i} \
        --workers 1
done
```

**Expected:**

- 20 tiles × 5 passes = 100 API calls
- Cost estimate: ~$0.30 (Flash)

### Step 2: Merge Detection Results

Combine all passes into a single GeoJSON with vote counts:

```bash
python scripts/7_analyse_consensus.py \
    --input-dir outputs/phase1-library/ \
    --output outputs/phase1-library/consensus_analysis.json \
    --passes 5
```

### Step 3: Match Against Ground Truth

```bash
python scripts/6_accuracy_report.py \
    --pred outputs/phase1-library/merged_detections.geojson \
    --bounds inputs/vectors/bounds/calibration_bounds.geojson \
    --template inputs/vectors/references/mounds-reference.geojson
```

### Step 4: Failure Analysis

**Hard Positives (FNs)** — mounds missed in ≥3/5 passes:

```bash
python scripts/mine_hard_cases.py \
    --input outputs/phase1-library/fn_analysis.geojson \
    --output-dir outputs/phase1-library/hard-positives \
    --mode fn \
    --manifest inputs/tiles/calibration_manifest.json \
    --limit 4
```

**Hard Negatives (FPs)** — false detections in ≥3/5 passes:

```bash
python scripts/mine_hard_cases.py \
    --input outputs/phase1-library/fp_analysis.geojson \
    --output-dir outputs/phase1-library/hard-negatives \
    --mode fp \
    --manifest inputs/tiles/calibration_manifest.json \
    --limit 4
```

### Step 5: Create Hard Example Symlinks

```bash
cd inputs/examples/neutral/

# Hard positives (example_05-08)
ln -s ../hard-positives/hp_001.png example_05.png
ln -s ../hard-positives/hp_002.png example_06.png
ln -s ../hard-positives/hp_003.png example_07.png
ln -s ../hard-positives/hp_004.png example_08.png

# Hard negatives (example_11-14)
ln -s ../hard-negatives/hn_001.png example_11.png
ln -s ../hard-negatives/hn_002.png example_12.png
ln -s ../hard-negatives/hn_013.png example_13.png
ln -s ../hard-negatives/hn_004.png example_14.png
```

### Step 6: Update Documentation

1. Update `inputs/examples/neutral/MANIFEST.md` with actual file mappings
2. Record in `docs/methodology/preregistration/decisions-log.md`:
   - Date of Phase 1 execution
   - Baseline performance metrics
   - Hard example selection rationale
   - Any deviations from preregistered procedure

### Step 7: Verify Library Configs

```bash
# Dry run to verify config loads correctly
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/library_scale-8.json \
    --manifest inputs/tiles/calibration_manifest.json \
    --dry-run
```

---

## Phase 2a: H1 Baseline Testing

**Goal**: Establish baseline performance for image-only vs text-augmented detection.

### Pre-Flight Checklist

- [ ] Phase 1 completed (hard example library built)
- [ ] Hard example symlinks verified (example_05-08, example_11-14)
- [ ] H1 configs exist:
  - `detect_image-only.json`
  - `detect_brief-text-image.json`
  - `detect_verbose-text-image.json`

### Execution

Run K=10 passes for each condition:

```bash
# Image-only (H1 baseline)
for i in $(seq -w 1 10); do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/detect_image-only.json \
        --manifest inputs/tiles/calibration_manifest.json \
        --output-dir outputs/phase2a-h1/image-only/pass_${i}
done

# Brief text + image
for i in $(seq -w 1 10); do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/detect_brief-text-image.json \
        --manifest inputs/tiles/calibration_manifest.json \
        --output-dir outputs/phase2a-h1/brief-text/pass_${i}
done
```

### Analysis

```bash
# Evaluate each condition
python scripts/6_accuracy_report.py \
    --pred outputs/phase2a-h1/image-only/merged_detections.geojson \
    --bounds inputs/vectors/bounds/calibration_bounds.geojson \
    --template inputs/vectors/references/mounds-reference.geojson

# Compare conditions
python scripts/analyse_study_effects.py \
    --study phase2a-h1 \
    --output results/phase2a-h1-comparison.json
```

---

## Phase 2b: H5-H7 Parameter Tuning

**Goal**: Determine optimal text verbosity level (H5) and temperature (H7).

### H5: Text Verbosity Levels

Test minimal, terse, and verbose system instructions:

```bash
# Configs: detect_verbose-text-image_minimal.json
#          detect_verbose-text-image_terse.json
#          detect_verbose-text-image_verbose.json

for level in minimal terse verbose; do
    for i in $(seq -w 1 10); do
        python scripts/4_detect_mounds_batch.py \
            --config prompts/configs/detect_verbose-text-image_${level}.json \
            --manifest inputs/tiles/calibration_manifest.json \
            --output-dir outputs/phase2b-h5/${level}/pass_${i}
    done
done
```

### H7: Temperature Variation

Test temperatures 0.5, 1.0, 1.5 with optimal text level:

```bash
# Requires temperature-specific configs or runtime override
for temp in 0.5 1.0 1.5; do
    for i in $(seq -w 1 10); do
        python scripts/4_detect_mounds_batch.py \
            --config prompts/configs/detect_optimal-text_temp-${temp}.json \
            --manifest inputs/tiles/calibration_manifest.json \
            --output-dir outputs/phase2b-h7/temp-${temp}/pass_${i}
    done
done
```

---

## Phase 2c: H8 Library Scale

**Goal**: Determine optimal few-shot library size.

### Library Scale Conditions

| Scale | Canon+ | HP | Canon- | HN | Null | Total |
|-------|--------|-----|--------|-----|------|-------|
| Scale-4 | 4 | 0 | 0 | 0 | 3 | 7 |
| Scale-8 | 4 | 4 | 2 | 4 | 3 | 17 |
| Scale-16 | 4 | 4 | 2 | 4 | 3 | 17 |
| Scale-32 | 4 | 4 | 2 | 4 | 3 | 17 |

```bash
for scale in 4 8 16 32; do
    for i in $(seq -w 1 10); do
        python scripts/4_detect_mounds_batch.py \
            --config prompts/configs/library_scale-${scale}.json \
            --manifest inputs/tiles/calibration_manifest.json \
            --output-dir outputs/phase2c-h8/scale-${scale}/pass_${i}
    done
done
```

---

## Phase 3: Holdout Validation

**Goal**: Validate optimal configuration on held-out tiles.

### Pre-Flight Checklist

- [ ] Phase 2 completed (optimal parameters determined)
- [ ] Holdout manifest exists: `inputs/tiles/holdout_manifest.json`
- [ ] Holdout bounds exist: `inputs/vectors/bounds/holdout_bounds.geojson`
- [ ] Optimal config created based on Phase 2 results

### Execution

```bash
for i in $(seq -w 1 10); do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/optimal_final.json \
        --manifest inputs/tiles/holdout_manifest.json \
        --output-dir outputs/phase3-holdout/pass_${i}
done
```

### Analysis

```bash
python scripts/6_accuracy_report.py \
    --pred outputs/phase3-holdout/merged_detections.geojson \
    --bounds inputs/vectors/bounds/holdout_bounds.geojson \
    --template inputs/vectors/references/mounds-reference.geojson
```

---

## Phase 4: Production Deployment

**Goal**: Deploy optimal configuration across full study region.

### Execution

```bash
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/optimal_final.json \
    --manifest inputs/tiles/production_manifest.json \
    --output-dir outputs/phase4-production/ \
    --workers 4
```

### Documentation

1. Archive all outputs to permanent storage
2. Document final performance metrics in preregistration report
3. Create reproducibility package with configs and code versions
