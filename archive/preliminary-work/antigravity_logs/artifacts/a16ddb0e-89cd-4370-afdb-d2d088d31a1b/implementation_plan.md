# Implementation Plan - Map Reader LLM

This project aims to automate the extraction of burial mounds from Soviet 1:50k topographic maps using Gemini 1.5.

## User Review Required
> [!IMPORTANT]
> **API Key**: You will need a valid Google Gemini API key exported as `GOOGLE_API_KEY` or stored in a `.env` file (we will use `python-dotenv`).

## Proposed Changes

### Phase 1: Foundations & Tiling (Current Focus)

#### [NEW] [requirements.txt](file:///home/shawn/Code/map-reader-llm/requirements.txt)
- `rasterio`: For reading GeoTIFFs and handling geospatial transforms.
- `google-generativeai`: For Gemini API access.
- `geopandas` & `shapely`: For geospatial data manipulation and export.
- `Pillow`: For image manipulation (saving tiles).
- `tqdm`: For progress bars.
- `python-dotenv`: For managing environment variables (API keys).

#### [NEW] [config.py](file:///home/shawn/Code/map-reader-llm/config.py)
- Central configuration for:
    - Input/Output directories.
    - Tile size (512x512).
    - Overlap (e.g., 64 or 128 pixels).
    - Model names.

#### [NEW] [1_preprocess_tiling.py](file:///home/shawn/Code/map-reader-llm/src/1_preprocess_tiling.py)
- **Goal**: Slice the map into small images for the LLM.
- **Logic**:
    1.  Iterate through `inputs/*.tif`.
    2.  Use `rasterio` to read the file.
    3.  Create a sliding window of 512x512 with a defined overlap.
    4.  Save each window as a `.png` in `outputs/tiles/<map_name>/`.
    5.  Save a corresponding `metadata.json` in `outputs/tiles/<map_name>/` that maps `tile_filename -> [transform matrix]`. This is crucial for reconstructing the location later.

### Phase 2: Inference (In Progress)
#### [NEW] [test_gemini_inference.py](file:///home/shawn/Code/map-reader-llm/src/test_gemini_inference.py)
- **Goal**: Run a localized test on 5 random tiles to verify prompt and model performance.
- **Output**: `outputs/test_detections.json`.

#### [NEW] [convert_to_geojson.py](file:///home/shawn/Code/map-reader-llm/src/convert_to_geojson.py)
- **Goal**: Convert individual tile detections (pixel coords) to a single geospatial file (GeoJSON).
- **Process**: 
    1. Read `test_detections.json`.
    2. Read `metadata.json` for each tile.
    3. Un-normalize coordinates (0-1000 -> 0-512).
    4. Apply Affine/Lower-Left shift to get CRS coordinates.
    5. Save as `FeatureCollection`.

#### [NEW] [2_detect_mounds.py](file:///home/shawn/Code/map-reader-llm/src/2_detect_mounds.py)
- **Goal**: Full-scale inference on all tiles.
- **Refined Prompt Strategy**:
    - **Role**: Expert Soviet Topographic Map Analyst.
    - **Context**: 1:50,000 scale.
    - **Symbols**: Sunburst (Tumulus), Circle-dot (Mound), Triangulation Mound.
    - **Negative Constraints**: Distinctly ignore contour lines, elevation points, and vegetation.
    - **Output Format**: JSON with `box_2d` (0-1000), `label`, and `reasoning`.
- **Process**:
    1. Iterate all tiles in `outputs/tiles/`.
    2. Check `metadata.json` to ensure tile is valid.
    3. Send to Gemini (Rate Limit handled).
    4. Append results to `outputs/all_detections.json`.

### Phase 3: Post-processing (Future)
#### [NEW] [3_georeference_and_visualize.py](file:///home/shawn/Code/map-reader-llm/src/3_georeference_and_visualize.py)
- Convert pixel boxes to lat/lon, deduplicate, export to GeoPackage.

## Verification Plan - Phase 1
### Automated Tests
- None planned for this research script phase.

### Manual Verification
1.  **Dependencies**: Run `pip install -r requirements.txt` and ensure no errors.
2.  **Tiling**: Run `python src/1_preprocess_tiling.py`.
3.  **Output Check**:
    - Verify `outputs/tiles/` contains PNG images.
    - Check image quality (readable map features).
    - Verify `metadata.json` exists and contains valid transform data.
