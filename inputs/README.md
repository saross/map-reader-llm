# Inputs

Place your source Soviet Topographic Maps and vector data here.

## Directory Structure
*   `rasters/`: Place source GeoTIFFs (`.tif`) here.
*   `vectors/`: Place vector overlays (e.g., GeoJSON, Shapefiles) here.
*   `manifests/`: JSON tile lists (e.g. `training_manifest.json`) for defining batch jobs.
*   `tiles/`: Pre-processed PNG map tiles.
*   `references/`: Few-shot example images for prompts.

## Requirements (Rasters)
*   **Format**: GeoTIFF (`.tif`)
*   **Projection**: Must be projected (e.g., EPSG:32635 UTM Zone 35N), not raw Lat/Lon, for accurate tiling results.
*   **Resolution**: Tested on standard 1:50,000 scans (approx 200-300 DPI).

The pipeline will scan `inputs/rasters/` for `*.tif` files during the tiling phase.