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

### `analyze_fp_crops.py`

Analyses false positives/negatives from baseline runs and extracts image crops for the hard example library. Clusters errors using 20m distance matching.

**Usage**: `python scripts/analyze_fp_crops.py --input <detections.geojson> --mode fn`

**Output**: `outputs/hard-examples/`

### `mine_hard_cases.py`

Extracts candidate crops from detection results for manual review and hard example selection.

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

### `7_analyze_consensus.py`

Analysis engine for the two-stage pipeline. Calculates performance metrics and performs grid-search simulation for optimal voting thresholds.

### `7_analyze_consensus_runs.py`

Analyses consensus across multiple independent runs for voting threshold optimisation (H3).

### `8_analyze_proposer_consensus.py`

Analyses proposer-stage consensus for the two-stage pipeline.

### `generate_union_candidates.py`

Clusters detections from multiple runs using 20m distance matching for voting aggregation.

### `generate_metrics_for_consensus.py`

Generates per-run metrics files for consensus/voting analysis.

### `analyze_study_effects.py`

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
