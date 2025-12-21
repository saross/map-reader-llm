# System Architecture

## Data Flow Diagram

```mermaid
graph TD
    A[Raw GeoTIFF Maps] -->|preprocess_tiling.py| B[Map Tiles (PNG + WorldFiles)]
    B -->|4_detect_mounds_batch.py| C{Inference Engine}
    D[Prompt Config (.json)] --> C
    E[Reference Library (Images)] --> C
    C -->|Stage 1 Output| F[Candidates GeoJSON]
    F -->|5_verify_crops.py| G{Verification Engine}
    H[Verifier Config] --> G
    G -->|Stage 2 Output| I[Verified GeoJSON]
    I -->|7_analyze_consensus.py| J[Analysis & Reports]
```

## Core Components

### 1. Preprocessing (Tiling)
*   **Script**: `scripts/preprocess_tiling.py`
*   **Input**: `inputs/rasters/*.tif`
*   **Function**: Slices large GeoTIFFs into manageable 1024x1024 pixel chunks. Crucially, it generates `.pgw` (World Files) and `.aux.xml` files for each tile to preserve geospatial metadata (EPSG:32635).
*   **Output**: `inputs/tiles/{map_name}/*.png`

### 2. Inference Engine (Stage 1)
*   **Script**: `scripts/4_detect_mounds_batch.py`
*   **Input**: PNG Tiles + Configuration JSON + Few-Shot Examples.
*   **Function**: Sends tile images to the Gemini API with a system prompt. The model returns a list of bounding boxes for suspected features.
*   **Georeferencing**: The script uses `rasterio` to read the tile's transform and converts pixel coordinates (0-1024) back into projected map coordinates (meters) for the final GeoJSON.

### 3. Verification Engine (Stage 2)
*   **Script**: `scripts/5_verify_crops.py`
*   **Input**: Candidates GeoJSON from Stage 1.
*   **Function**: "Crops" the original high-resolution map data around each candidate. It then performs a focused "Visual Chain of Thought" analysis on just that specific feature to confirm or reject it.
*   **Output**: A filtered GeoJSON file with confidence scores and reasoning.

### 4. Analysis & Reporting
*   **Scripts**: `scripts/7_analyze_consensus.py`, `scripts/benchmark_variability.py`.
*   **Function**: Calculates Intersection over Union (IoU) against "Gold Standard" human labels (if available) or computes consensus between multiple AI runs to determine stability.

## Directory Structure Strategy
*   **`prompts/versions/`**: Enables "Time Travel". Any past experiment can be reproduced by loading its specific JSON config.
*   **`inputs/manifests/`**: Defines the "Scope" of a run. Instead of running on absolute paths, scripts take a manifest (list of tile IDs) to ensure consistent data subsets (e.g., "Training Set" vs "Test Set").
