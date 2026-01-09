# Inputs

Place your source Soviet Topographic Maps and vector data here.

## Directory Structure

*   `rasters/`: Place source GeoTIFFs (`.tif`) and associated metadata (`.aux.xml`) here.
*   `vectors/`: Vector data organised into:
    *   `bounds/`: GeoJSON bounds files for tile sets (calibration, holdout)
    *   `references/`: Ground truth and reference GeoJSON files
*   `tiles/`: Pre-processed PNG map tiles, with manifest and metadata files:
    *   `calibration_manifest.json`: Tiles for few-shot library development
    *   `holdout_manifest.json`: Tiles for evaluation
    *   `tile_selection_metadata.json`: Full selection provenance (seeds, mound counts, etc.)
*   `examples/`: Few-shot example images for prompts.

## Requirements (Rasters)
*   **Format**: GeoTIFF (`.tif`)
*   **Projection**: Must be projected (e.g., EPSG:32635 UTM Zone 35N), not raw Lat/Lon, for accurate tiling results.
*   **Resolution**: Tested on standard 1:50,000 scans (approx 200-300 DPI).

The pipeline will scan `inputs/rasters/` for `*.tif` files during the tiling phase.