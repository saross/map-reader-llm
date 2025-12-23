# Scripts

This directory contains the Python code for the map processing pipeline.

## Core Pipeline

### 1. `preprocess_tiling.py`
*   **Purpose**: Splits large GeoTIFF maps into small tiles (e.g., 512x512) for the LLM.
*   **Key Feature**: Generates geospatial sidecar files (`.pgw`, `.aux.xml`) so each little tile knows exactly where it belongs on Earth.
*   **Output**: `inputs/tiles/`

### 2. `4_detect_mounds_batch.py`
*   **Purpose**: The main **Stage 1** inference engine.
*   **Key Feature**: Reads a **Run Config** (from `prompts/configs/`), builds a multimodal prompt (System Text + Example Images + Target Map Tile), and queries Gemini.
*   **Output**: `outputs/results/vX.X/detections-*.geojson` (Raw boxes) + `.meta.json`

### 3. `5_verify_crops.py`
*   **Purpose**: The **Stage 2** Verification engine.
*   **Key Feature**: Extracts high-res crops of candidates found in Stage 1 and asks a powerful model to double-check them using Visual Chain-of-Thought.
*   **Output**: `outputs/results/vX.X/verified-*.geojson`

### 4. `7_analyze_consensus.py`
*   **Purpose**: Analysis and scoring.
*   **Key Feature**: Calculates F1/Precision/Recall against Ground Truth and performs grid-search simulation for Proposer/Verifier voting thresholds.

*Note: Older scripts and utilities have been moved to `archive/scripts/`.*
