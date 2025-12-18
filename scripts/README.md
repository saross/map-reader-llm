# Scripts

This directory contains the Python code for the map processing pipeline.

## Core Pipeline

### 1. `preprocess_tiling.py`
*   **Purpose**: Splits large GeoTIFF maps into small tiles (e.g., 512x512) for the LLM.
*   **Key Feature**: Generates geospatial sidecar files (`.pgw`, `.aux.xml`) so each little tile knows exactly where it belongs on Earth.
*   **Output**: `inputs/tiles/`

### 2. `4_detect_mounds_batch.py`
*   **Purpose**: The main inference engine.
*   **Key Feature**: Reads a **Versioned Config** (from `prompts/versions/`), builds a multimodal prompt (System Text + Example Images + Target Map Tile), and queries Gemini.
*   **Output**: `outputs/results/vX.X/detections-*.geojson` (Raw boxes) + `.meta.json`

### 3. `3_georeference_and_visualize.py`
*   **Purpose**: Post-processing and cleanup.
*   **Key Feature**: Deduplicates overlapping detections (merges nearby points) and ensures the final file is a valid, clean GeoJSON layer for GIS usage.
*   **Output**: `outputs/results/mounds-*.geojson` (Final points)

*Note: Older scripts and utilities have been moved to `archive/scripts/`.*
