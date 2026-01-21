# Scripts

Python scripts for the preregistered VLM burial mound detection study. Scripts are organised by function within the experimental pipeline.

## Data Preparation

### `preprocess_tiling.py`

Splits large GeoTIFF maps into tiles (default 512×512) for VLM processing. Generates geospatial sidecar files (`.pgw`, `.aux.xml`) preserving coordinate reference system (CRS) information.

**Output**: `inputs/tiles/<map_name>/*.{png,pgw,png.aux.xml}`

### `select_tiles_phase2.py`

Selects calibration and holdout tile sets with documented provenance and spatial separation. Implements stratified sampling by mound density.

**Output**: `inputs/tiles/{calibration,holdout}_manifest.json`, `tile_selection_metadata.json`

### `generate_tile_bounds.py`

Generates GeoJSON polygon bounds for tile sets, useful for visualisation and spatial filtering during evaluation.

**Output**: `inputs/vectors/bounds/*.geojson`

---

## Detection Pipeline

### `4_detect_mounds_batch.py`

Core **Stage 1** detection engine. Reads a prompt configuration, builds multimodal prompts (system text + example images + target tile), and queries the VLM API.

**Usage**: `python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_image-only.json`

**Output**: `outputs/phase*/raw-responses/detections-*.geojson` + `.meta.json`

### `5_verify_crops.py`

**Stage 2** verification engine for the two-stage pipeline (H2). Extracts high-resolution crops of Stage 1 candidates and submits them to a verifier prompt using visual chain-of-thought.

**Usage**: `python scripts/5_verify_crops.py --candidates <input.geojson> --config prompts/configs/verify_image-only.json`

**Output**: `outputs/phase*/h2-twostage/verified-*.geojson`

### `run_study.py`

Study runner for factorial experiments. Executes multi-condition studies defined in YAML configuration files, manages checkpointing, and provides resumption capability.

**Usage**: `python scripts/run_study.py studies/phase2-factorial.yaml [--dry-run] [--resume]`

**Output**: Per-condition results in study output directory

---

## Phase 1: Library Construction

### `analyse_fp_crops.py`

Analyses false positives/negatives from baseline runs and extracts image crops for the hard example library. Clusters errors using 20m distance matching.

**Usage**: `python scripts/analyse_fp_crops.py --input <detections.geojson> --mode fn`

**Output**: `outputs/hard-examples/`

### `mine_hard_cases.py`

Extracts candidate crops from detection results for manual review and hard example selection.

---

## Voting & Consensus

### `merge_passes.py`

Implements the consensus voting algorithm from preregistration Section 8.5. Merges K detection passes into consensus predictions with configurable vote thresholds.

**Algorithm**:

1. Within-pass deduplication (20m tolerance) — handles overlapping tiles
2. Cross-pass clustering (20m tolerance)
3. Count votes per cluster (distinct passes contributing)
4. Apply vote threshold
5. Output: centroid, majority label, confidence (votes/N), source passes

**Usage**:

```bash
# Merge all passes with threshold ≥3
python scripts/merge_passes.py \
    --input-dir outputs/phase1-library \
    --output outputs/phase1-library/merged_t3.geojson \
    --threshold 3

# Split K=10 into N=5 pool A (passes 1-5)
python scripts/merge_passes.py \
    --input-dir outputs/experiment \
    --output outputs/experiment/pool_a.geojson \
    --passes 1,2,3,4,5 \
    --threshold 3

# Generate outputs for all thresholds
python scripts/merge_passes.py \
    --input-dir outputs/experiment \
    --output-dir outputs/experiment/voting \
    --sweep
```

**Output**: Consensus GeoJSON with vote counts, confidence, contributing passes.

---

## Evaluation & Analysis

### `lib_advanced_metrics.py`

Core metrics library providing F1, precision, recall calculations with one-to-one matching using the Hungarian algorithm. Includes bootstrapped confidence interval functions aligned with preregistration Section 3.5.

**Key functions**:
- `calculate_f1_internal()` — Symbol-level F1 with 20m spatial tolerance
- `bootstrap_ci()` — 95% CIs for absolute metrics
- `bootstrap_effect_size_ci()` — 95% CIs for condition differences
- `calculate_tile_classification()` — Binary tile classification (H4.2)

### `6_accuracy_report.py`

Generates accuracy reports comparing detections against ground truth.

### `7_analyse_consensus.py`

Analysis engine for the two-stage pipeline. Calculates performance metrics and performs grid-search simulation for optimal voting thresholds.

### `8_analyse_proposer_consensus.py`

Analyses proposer-stage consensus for the two-stage pipeline.

### `generate_union_candidates.py`

Clusters detections from multiple runs using 20m distance matching for voting aggregation.

### `generate_metrics_for_consensus.py`

Generates per-run metrics files for consensus/voting analysis.

### `analyse_study_effects.py`

Computes bootstrapped 95% CIs for effect sizes between experimental conditions, as specified in preregistration Sections 3.5 and 4.2.

---

## Support Libraries

### `lib_llm_metadata.py`

Standardised metadata capture for LLM API responses across multiple providers (Gemini, Claude, OpenAI). Tracks tokens, costs, timing, and response quality metrics.

---

## Archived Scripts

Scripts from earlier development phases have been archived:

- **`archive/pilot-tile-size/scripts/`** — Tile size pilot experiment (H10)
- **`archive/preliminary-work/scripts/`** — Pre-preregistration experimental work (v3.x/v4.x)
- **`archive/deprecated-scripts/`** — One-off utilities and superseded scripts
