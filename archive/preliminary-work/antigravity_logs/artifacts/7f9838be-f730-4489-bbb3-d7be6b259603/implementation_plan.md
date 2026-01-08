# Visualization of Tile Bounding Boxes

## Goal
1.  Generate a one-off GeoJSON containing the bounding boxes of the 5 tiles recently processed (`detections-K-35-062-2_Rakovski-robust-random5.geojson`).
2.  Refactor `2_detect_mounds.py` to optionally output a separate GeoJSON file containing the bounding boxes of all processed tiles.

## User Review Required
> [!NOTE]
> The ad-hoc GeoJSON will be saved to `outputs/results/tile_bboxes-rakovski-random5.geojson`.
> Future runs can use `--export_bounds` (or similar) to generate this automatically.

## Proposed Changes

### Configuration
None.

### Scripts
#### [NEW] [generate_adhoc_bboxes.py](file:///home/shawn/Code/map-reader-llm/scripts/generate_adhoc_bboxes.py)
- Reads the existing `detections-K-35-062-2_Rakovski-robust-random5.geojson` to find which tiles were processed.
- For each unique tile, opens the source GeoTIFF/PNG using `rasterio`.
- Extracts the bounds and CRS.
- Saves a new GeoJSON `tile_bboxes-rakovski-random5.geojson`.

#### [MODIFY] [2_detect_mounds.py](file:///home/shawn/Code/map-reader-llm/scripts/2_detect_mounds.py)
- Update `system_instruction` / `prompt` with the text from `prompts/V2_mound_detection_prompt.md`.
- Update parsing logic to extract `subtype` from JSON and save to GeoJSON properties.
- Ensure `gemini-3-pro-preview` is used with the new prompt.
- Update `detect_mounds` signature to accept `export_bounds=False`.
- If true, maintain a list of tile geometries during processing.
- Save `[output_filename]_bounds.geojson` at the end.

#### [NEW] [test_detection_v2.py](file:///home/shawn/Code/map-reader-llm/scripts/test_detection_v2.py)
- A focused script to run the V2 prompt on the single "busy" tile `K-35-062-2_Rakovski_x2688_y1344.png`.
- Output: `outputs/results/test_v2_x2688_y1344.geojson`.

#### [MODIFY] [run_random_extraction.py](file:///home/shawn/Code/map-reader-llm/scripts/run_random_extraction.py)
- Add `--export_bounds` argument to the CLI.
- Pass this flag to `detect_mounds`.

## Verification Plan
### Automated Tests
- Run `python scripts/test_detection_v2.py`.
- Verify output contains detections with `subtype`.
- Manually check performance on the known difficult tile (user review).
- Run a dry-run or small test of `run_random_extraction.py` with `--export_bounds` to verify the second file is created.
