# Scripts

Python scripts for the preregistered VLM burial mound detection study. Scripts are organised by function within the experimental pipeline.

## Data Preparation

### `preprocess_tiling.py`

Splits large GeoTIFF maps into tiles (default 512×512) for VLM processing. Generates geospatial sidecar files (`.pgw`, `.aux.xml`) preserving coordinate reference system (CRS) information.

**Output**: `inputs/tiles/<map_name>/*.{png,pgw,png.aux.xml}`

### `select_tiles_phase2.py`

Selects calibration and validation tile sets with documented provenance and spatial separation. Implements stratified sampling by mound density.

**Output**: `inputs/tiles/{calibration,validation}_manifest.json`, `tile_selection_metadata.json`

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

**Usage**: `python scripts/5_verify_crops.py --candidates <input.geojson> --config prompts/configs/verify_brief.json`

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

**CRS contract** (see [`docs/methodology/spatial-reference.md`](../docs/methodology/spatial-reference.md) § consensus voting path): clustering runs in the **analysis CRS (EPSG:32635, metres)** — the 20 m tolerance assumes UTM input — but `apply_threshold()` **reprojects centroids to EPSG:4326** on output (RFC 7946). Any in-memory consumer of `apply_threshold` (e.g. `analyse_diversity.consensus_to_gdf`) must reproject **back to the analysis CRS** before metric work; do not relabel without reprojecting. A 2026-04-11 change to this output CRS silently broke `consensus_to_gdf` (F1=0) until 2026-06-08 — the contract is now pinned by `tests/test_analyse_diversity_crs.py`.

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

### `run_phase2.py`

Study runner for Phase 2/3 One-Factor-At-a-Time (OFAT) experiments. Parses study YAML definitions, generates execution units (condition × run), and dispatches them via one of two execution modes:

- **Concurrent** (default): Spawns `4_detect_mounds_batch.py` as a subprocess per unit, with per-tile API calls governed by the token-bucket rate limiter.
- **Batch**: Submits all tiles per unit as a single JSONL file to the Gemini Batch API (50% cost reduction, separate rate limits). Uses `lib_batch_api.py` for the batch lifecycle.

Supports checkpoint-based resumption, parallel unit execution, cost monitoring, and condition filtering. Batch mode polling is configurable via `--poll-interval` and `--max-poll-hours` for long-running overnight jobs.

**Usage**:

```bash
# Concurrent mode (default)
python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml

# Batch mode (Gemini Batch API)
python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml --mode batch

# Resume from checkpoint
python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml --resume

# Batch mode: overnight monitoring with hourly polls
python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml \
    --mode batch --resume --poll-interval 3600

# Batch mode: quick status check (poll once, then exit)
python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml \
    --mode batch --resume --max-poll-hours 0.01
```

**Output**: Per-run results in `{output_dir}/{condition_name}/run_{K}/`, checkpoint JSON

### `batch-monitor.py`

Standalone monitoring tool for Gemini Batch API jobs. Reads checkpoint state and queries the Batch API to report job progress without running the full pipeline. This script is read-only — it never modifies the checkpoint.

**Usage**:

```bash
# One-shot status check
python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml

# Continuous monitoring (default: hourly checks)
python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml --watch

# Watch with custom interval (30 minutes)
python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml \
    --watch --interval 1800

# Auto-trigger pipeline when all jobs complete
python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml \
    --watch --auto-resume

# Machine-readable JSON output
python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml --json
```

**Output**: Status report (text or JSON) showing completed/pending/failed units, per-condition breakdown, and submission timing

---

## Support Libraries

### `lib_llm_metadata.py`

Standardised metadata capture for LLM API responses across multiple providers (Gemini, Claude, OpenAI). Tracks tokens, costs, timing, and response quality metrics.

### `lib_token_bucket.py`

Proactive token-bucket rate limiter with dual Requests Per Minute (RPM) + Tokens Per Minute (TPM) constraints for the Google Gemini API. Uses continuous capacity replenishment matching how APIs enforce rolling limits. Workers block in `acquire()` until both RPM and TPM budgets allow dispatch. Used by `4_detect_mounds_batch.py` in concurrent mode.

### `lib_batch_api.py`

Standalone module for the Google Gemini Batch API. Encapsulates the full batch lifecycle: JSONL construction, file upload, job submission, polling, result retrieval, validation, and output writing. Produces output files (GeoJSON, `.meta.json`, `.tiles.json`) identical to the concurrent pipeline for downstream compatibility. Used by `run_phase2.py` in `--mode batch`.

**Key functions**:

- `build_jsonl_file()` — Serialise tile requests to Batch API JSONL format
- `submit_batch_job()` — Upload JSONL and create a batch job
- `poll_batch_job()` — Poll until terminal state (SUCCEEDED/FAILED/CANCELLED/EXPIRED)
- `validate_batch_results()` — Verify every submitted tile has a response (detects silent data loss)
- `run_batch_unit()` — Orchestrate the full lifecycle for one execution unit

---

## Archived Scripts

Scripts from earlier development phases have been archived:

- **`archive/pilot-tile-size/scripts/`** — Tile size pilot experiment (H10)
- **`archive/preliminary-work/scripts/`** — Pre-preregistration experimental work (v3.x/v4.x)
- **`archive/deprecated-scripts/`** — One-off utilities and superseded scripts
