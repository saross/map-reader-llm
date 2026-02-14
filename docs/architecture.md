# System Architecture

## Data Flow Diagram

```mermaid
graph TD
    A[Raw GeoTIFF Maps] -->|preprocess_tiling.py| B[Map Tiles (PNG + WorldFiles)]
    B -->|4_detect_mounds_batch.py| C{Inference Engine}
    D[Prompt Config (.json)] --> C
    E[Reference Library (Images)] --> C
    C -->|Stage 1 Output| F[Candidates GeoJSON]
    C -->|Metadata| M1[Detection .meta.json]
    F -->|5_verify_crops.py| G{Verification Engine}
    H[Verifier Config] --> G
    G -->|Stage 2 Output| I[Verified GeoJSON]
    G -->|Metadata| M2[Verification .meta.json]
    I -->|7_analyze_consensus.py| J[Analysis & Reports]
    M1 --> J
    M2 --> J
```

## Core Components

### 1. Preprocessing (Tiling)

- **Script**: `scripts/preprocess_tiling.py`
- **Input**: `inputs/rasters/*.tif`
- **Function**: Slices large GeoTIFFs into manageable 1024x1024 pixel chunks. Crucially, it generates `.pgw` (World Files) and `.aux.xml` files for each tile to preserve geospatial metadata (EPSG:32635).
- **Output**: `inputs/tiles/{map_name}/*.png`

### 2. Inference Engine (Stage 1)

- **Script**: `scripts/4_detect_mounds_batch.py` (v4.2.0)
- **Input**: PNG Tiles + Configuration JSON + Few-Shot Examples.
- **Function**: Sends tile images to the Gemini API with a system prompt. The model returns a list of bounding boxes for suspected features.
- **Georeferencing**: The script uses `rasterio` to read the tile's transform and converts pixel coordinates (0-1024) back into projected map coordinates (metres) for the final GeoJSON.
- **Output**:
  - `detections-{version}-{model}-{date}.geojson` - Detection results
  - `detections-{version}-{model}-{date}.meta.json` - Comprehensive run metadata

### 3. Verification Engine (Stage 2)

- **Script**: `scripts/5_verify_crops.py` (v5.1.0)
- **Input**: Candidates GeoJSON from Stage 1.
- **Function**: "Crops" the original high-resolution map data around each candidate. It then performs a focused "Visual Chain of Thought" analysis on just that specific feature to confirm or reject it.
- **Output**:
  - Filtered GeoJSON file with confidence scores and reasoning
  - `.meta.json` file with per-iteration voting metadata

### 4. Analysis & Reporting

- **Scripts**: `scripts/7_analyze_consensus.py`, `scripts/benchmark_variability.py`.
- **Function**: Calculates Intersection over Union (IoU) against "Gold Standard" human labels (if available) or computes consensus between multiple AI runs to determine stability.

### 5. Metadata Tracking Module

- **Module**: `scripts/lib_llm_metadata.py`
- **Function**: Provides standardised metadata capture for all LLM API interactions across providers (Gemini, Claude, OpenAI).
- **Key Classes**:
  - `LLMMetadataTracker`: Thread-safe aggregation of API response metadata
  - `LLMResponseMetadata`: Per-response data (tokens, latency, finish reason)
  - `TokenUsage`: Detailed token breakdown (input, output, cached, reasoning)
- **Features**:
  - Automatic git commit tracking
  - Prompt hash for reproducibility verification
  - Cost estimation with configurable pricing tables
  - Categorised retry tracking (rate limit, server error, timeout)

### 6. Rate Limiting (Token Bucket)

- **Module**: `scripts/lib_token_bucket.py`
- **Function**: Proactive token-bucket rate limiter with dual RPM + TPM constraints and continuous capacity replenishment. Workers block in `acquire()` until both budgets allow dispatch.
- **Used by**: `4_detect_mounds_batch.py` in concurrent mode (multi-worker runs).
- **Not used by**: Batch mode — the Batch API has separate (higher) rate limits and handles throttling server-side.

### 7. Batch API Module

- **Module**: `scripts/lib_batch_api.py`
- **Function**: Standalone module for the Google Gemini Batch API. Provides an alternative execution mode (`--mode batch` on `run_phase2.py`) that submits all tiles per execution unit as a single JSONL file, offering 50% cost reduction over synchronous requests.
- **Lifecycle**: Build JSONL → upload via Files API → create batch job → poll `batches.get()` → download results → parse and validate → write output files.
- **Output contract**: Produces GeoJSON, `.meta.json`, and `.tiles.json` files identical to the concurrent pipeline, ensuring downstream analysis scripts work without modification.
- **Key safety mechanism**: Response validation matches every submitted tile key against response keys, detecting silent data loss that would otherwise appear as zero-detection tiles.
- **Crash recovery**: Write-ahead checkpoint persistence records the batch job name to the checkpoint file immediately after submission (before the hours-long polling phase). On resume, pending jobs are recovered and polled to completion instead of being resubmitted.

## Directory Structure Strategy

- **`prompts/configs/`**: Enables "Time Travel". Any past experiment can be reproduced by loading its specific JSON config.
- **`inputs/manifests/`**: Defines the "Scope" of a run. Instead of running on absolute paths, scripts take a manifest (list of tile IDs) to ensure consistent data subsets (e.g., "Training Set" vs "Test Set").
