# Phase 1 Execution Simulation

> **NOT PART OF THE OSF LODGEMENT.** The registration comprises exactly three
> documents, all in `osf/` (`osf/README.md:3,9-11`); this file is not one of
> them. It is a working document: pre-lodgement content here fed into writing
> the registration but does not license a "the preregistration says" claim,
> and post-lodgement content is operational, not registered. Cite
> `osf/preregistration.md` for registered content. Banner added 2026-07-28
> (D17 audit, structural fix).

**Purpose**: Detailed walkthrough of Phase 1 (Library and Text Construction) to identify operational requirements and potential scaffolding needs.

**Status**: Simulation only — not actual execution

---

## Phase 1 Overview

Phase 1 constructs the hard example library by running baseline detection on training tiles and analysing systematic failures.

**Goal**: Identify hard positives (FNs) and hard negatives (FPs) for the few-shot library.

**Inputs required**:
- 20 training tiles (from `calibration_manifest.json`)
- Ground truth annotations
- Baseline config (`library_pure-positive-canon.json` or `detect_image-only.json`)
- System instruction (`detect_image-only.md`)

**Outputs**:
- Detection results for 5 passes × 20 tiles
- FN/FP frequency analysis
- Hard example image crops
- Updated library configs with example_05-08 (HP) and example_11-14 (HN)

---

## Step-by-Step Execution Checklist

### Pre-Flight Checks

- [ ] Verify API key is set (`GOOGLE_API_KEY` in environment or config.py)
- [ ] Verify training tiles exist: `inputs/tiles/*/` (check all 4 map directories)
- [ ] Verify ground truth exists: `inputs/vectors/references/mounds-reference.geojson`
- [ ] Verify calibration bounds exist: `inputs/vectors/bounds/calibration_bounds.geojson`
- [ ] Verify baseline config exists: `prompts/configs/library_pure-positive-canon.json`
- [ ] Verify neutral example symlinks exist: `inputs/examples/neutral-naming/example_01-04.png`
- [ ] Verify null tile symlinks exist: `inputs/examples/neutral-naming/example_15-17.png`

### Step 1: Run Baseline Detection (5 passes)

**Command pattern** (for each pass i=1..5):

```bash
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/library_pure-positive-canon.json \
    --manifest inputs/tiles/calibration_manifest.json \
    --output-dir outputs/phase1-library/pass_0${i} \
    --workers 1
```

**Expected**:
- 20 tiles × 5 passes = 100 API calls
- Cost estimate: ~$0.30 (100 calls × ~$0.003/call for Flash)
- Time estimate: ~10-20 minutes (depends on rate limiting)

**Outputs per pass**:
- `outputs/phase1-library/pass_0X/{tile_name}.geojson` — detection results
- `outputs/phase1-library/pass_0X/{tile_name}.meta.json` — API metadata

### Step 2: Merge Detection Results

**Purpose**: Combine all passes into a single GeoJSON with vote counts per detection.

**Script needed**: `scripts/merge_passes.py` (or manual merge)

**Logic**:
1. Load all 5 passes' GeoJSONs
2. Cluster detections within 20m tolerance
3. Count occurrences across passes
4. Output merged GeoJSON with `vote_count` property

**Output**: `outputs/phase1-library/merged_detections.geojson`

### Step 3: Match Against Ground Truth

**Command**:

```bash
python scripts/6_accuracy_report.py \
    --pred outputs/phase1-library/merged_detections.geojson \
    --bounds inputs/vectors/bounds/calibration_bounds.geojson \
    --template inputs/vectors/references/mounds-reference.geojson
```

**Purpose**: Identify which ground truth mounds were detected (TPs) vs missed (FNs), and which detections have no ground truth match (FPs).

### Step 4: Failure Analysis

**FN Analysis** (Hard Positives):
- Filter ground truth mounds missed in ≥3/5 passes
- Rank by miss frequency (most frequently missed first)
- Select top K=4 for hard positive library

**FP Analysis** (Hard Negatives):
- Filter detections with no ground truth match in ≥3/5 passes
- Rank by detection frequency (most frequently detected first)
- Select top M=4 for hard negative library

**Command** (using analyse_fp_crops.py):

```bash
# For FNs (hard positives)
python scripts/analyse_fp_crops.py \
    --input outputs/phase1-library/fn_analysis.geojson \
    --output_dir outputs/phase1-library/hard-positives \
    --mode fn \
    --manifest inputs/tiles/calibration_manifest.json \
    --limit 4

# For FPs (hard negatives)
python scripts/analyse_fp_crops.py \
    --input outputs/phase1-library/fp_analysis.geojson \
    --output_dir outputs/phase1-library/hard-negatives \
    --mode fp \
    --manifest inputs/tiles/calibration_manifest.json \
    --limit 4
```

### Step 5: Create Hard Example Symlinks

**After cropping hard examples, create neutral-named symlinks**:

```bash
cd inputs/examples/neutral-naming/

# Hard positives (example_05-08)
ln -s ../hard-positives/hp_001.png example_05.png
ln -s ../hard-positives/hp_002.png example_06.png
ln -s ../hard-positives/hp_003.png example_07.png
ln -s ../hard-positives/hp_004.png example_08.png

# Hard negatives (example_11-14)
ln -s ../hard-negatives/hn_001.png example_11.png
ln -s ../hard-negatives/hn_002.png example_12.png
ln -s ../hard-negatives/hn_003.png example_13.png
ln -s ../hard-negatives/hn_004.png example_14.png
```

### Step 6: Update MANIFEST.md

Update `inputs/examples/neutral-naming/MANIFEST.md`:
- Fill in actual file mappings for examples 05-08 and 11-14
- Document provenance (source tile, coordinates, selection metric)
- Update symlink status table

### Step 7: Document in Decisions Log

Record in `docs/methodology/preregistration/decisions-log.md`:
- Date of Phase 1 execution
- Baseline performance metrics (F1, P, R on training set)
- Hard example selection rationale
- Any deviations from preregistered procedure

### Step 8: Verify Library Configs

Confirm these configs work with the new hard examples:
- `library_scale-8.json` — should reference example_05-08 and example_11-14
- `library_scale-16.json` — extended pool
- `library_scale-32.json` — extended pool

**Test command**:

```bash
# Dry run to verify config loads correctly
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/library_scale-8.json \
    --manifest inputs/tiles/calibration_manifest.json \
    --dry-run
```

---

## Gaps Identified

### Missing Scripts/Functionality

1. **Pass merger script**: Need to merge multiple passes into single GeoJSON with vote counts
2. **FN/FP separator**: Need to separate matched/unmatched detections after accuracy report
3. **Batch pass runner**: Running 5 passes manually is tedious; could automate

### Missing Documentation

1. **Phase 1 study YAML**: No `studies/phase1-library.yaml` exists for run_study.py
2. **Hard example directory**: `inputs/examples/hard-positives/` and `hard-negatives/` don't exist yet

### Operational Knowledge Needed

1. **Config file structure**: Understanding which config to use for baseline
2. **Manifest file locations**: Where are calibration vs holdout manifests
3. **Output directory conventions**: How to organise phase outputs
4. **Ground truth paths**: Where are reference annotations
5. **Bounds file purpose**: Understanding calibration_bounds vs validation_bounds

---

## Time and Cost Estimates

| Step | API Calls | Est. Cost | Est. Time |
|------|-----------|-----------|-----------|
| Step 1 (5 passes) | 100 | $0.30 | 15 min |
| Step 2-4 (analysis) | 0 | $0 | 10 min |
| Step 5-8 (setup) | 0 | $0 | 20 min |
| **Total** | 100 | ~$0.30 | ~45 min |

---

## Scaffolding Recommendations

Based on this simulation, the following would help:

### CLAUDE.md Additions

1. **Quick reference paths** for key files (manifests, bounds, ground truth)
2. **Config selection guide** — which config for which purpose
3. **Output directory conventions**
4. **Phase workflow overview** with script sequence

### Potential Skill Value

A skill could bundle:
- Phase execution checklists
- Common command patterns
- Troubleshooting guidance for API errors
- Output verification procedures

---

*Simulation created: 2026-01-20*
