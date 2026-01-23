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

## Directory Structure Strategy
*   **`prompts/configs/`**: Enables "Time Travel". Any past experiment can be reproduced by loading its specific JSON config.
*   **`inputs/manifests/`**: Defines the "Scope" of a run. Instead of running on absolute paths, scripts take a manifest (list of tile IDs) to ensure consistent data subsets (e.g., "Training Set" vs "Test Set").
