Here is a comprehensive Markdown summary of our discussion, methodology, and findings. You can copy-paste this directly into your new session to immediately restore context and begin coding.

***

# Project Context: Archaeological Feature Extraction from Soviet Maps

**Objective:**
To automate the extraction of burial mound symbols (tumuli) from historical Soviet military topographic maps (1:50,000 scale GeoTIFFs) using Multimodal LLMs (Gemini), replacing a previous crowdsourcing workflow.

**Background Resources:**
1.  **Sobotkova et al. (2023):** "Creating large, high-quality geospatial datasets from historical maps using novice volunteers." (Established the "ground truth" dataset and visual definitions).
2.  **Kardos (2024):** Student paper on using YOLO for satellite imagery. (Provided the inspiration for a Python pipeline, though we are shifting from YOLO/Satellite to Gemini/Maps).

## 1. The Challenge
*   **Source:** 1:50,000 Soviet GeoTIFFs (approx 400 sq km per sheet).
*   **Target:** Specific map symbols for burial mounds:
    *   **Sunburst:** Orange circle with radiating spikes.
    *   **Circle-dot:** Simple orange circle with a central dot.
    *   **Triangulation:** Sunburst with a triangle/geometry inside.
*   **Noise:** The maps contain heavy clutter: contour lines (same color as mounds), text, grid lines, and vegetation patterns (blue hatching).

## 2. The Methodology (The "VLM-Pipeline")
We rejected a pure YOLO approach (requires training data) and a raw "whole map" upload (resolution loss). We agreed on a **Sliding Window** approach with **Geospatial Post-Processing**.

### Step A: Pre-processing (Tiling)
*   **Library:** `rasterio` (Python).
*   **Logic:** Slice the massive GeoTIFF into small, overlapping tiles (e.g., **512x512 pixels**).
*   **Reasoning:** At this scale, mound symbols appear as **20-30 pixels** wide, which is the "sweet spot" for VLM detection. A full map resize would shrink them to sub-pixel noise.
*   **Crucial:** We must save the **Affine Transform** (geospatial coordinates) of each specific tile top-left corner to map pixels back to the real world later.

### Step B: Inference (Gemini VLM)
*   **Model:** Gemini 1.5 Pro or Flash.
*   **Prompt Strategy:** Object Detection (Bounding Boxes).
*   **Prompt Logic:** "Identify the bounding boxes of all 'Burial Mound' symbols. Ignore contour lines. Return JSON: `{'box_2d': [ymin, xmin, ymax, xmax]}`."
*   **Detection Type:** Standard Bounding Box (HBB). We rejected Oriented Bounding Boxes (OBB) because the symbols are radially symmetrical.

### Step C: Post-Processing
*   **Centroid Calculation:** Calculate the center pixel of the returned bounding box.
*   **Georeferencing:** Use the saved Affine Transform from Step A to convert `(Pixel_X, Pixel_Y)` into `(Longitude, Latitude)` or Projected CRS.
*   **Deduplication:** Since tiles overlap, merge points that are within $N$ meters of each other.

## 3. Proof of Concept Results
*   **Test Image:** A crop of a map tile with heavy "blue hatching" (marshland) and contour lines was tested.
*   **Result:** Gemini successfully visually identified:
    *   Isolated mound markers.
    *   "Sunburst" symbols on contour lines.
    *   A complex cluster of 3 symbols ("Glavchova Mogila") partially obscured by blue hash lines.
*   **Conclusion:** The signal-to-noise ratio is sufficient for a Zero-Shot approach without fine-tuning, provided the tiling resolution is correct.

## 4. Current Task: Code Generation
**The user needs a complete Python repository structure to run locally in VS Code.**

**Requirements:**
1.  **`requirements.txt`**: Must include `rasterio`, `google-generativeai`, `geopandas`, `shapely`, `Pillow`, `tqdm`.
2.  **`config.py`**: To hold API keys and file paths.
3.  **`1_preprocess_tiling.py`**:
    *   Input: A raw GeoTIFF.
    *   Output: A directory of PNG tiles + a metadata JSON file mapping filenames to their Affine Transforms.
4.  **`2_detect_mounds.py`**:
    *   Input: The directory of PNG tiles.
    *   Process: Send to Gemini API in batches.
    *   Output: A raw JSON log of detections (pixel coordinates).
5.  **`3_georeference_and_visualize.py`**:
    *   Process: Convert pixel logs to geospatial points using the metadata.
    *   Output: A `.gpkg` or `.shp` file for viewing in QGIS.