# Inputs

Place your source Soviet Topographic Maps (GeoTIFFs) here.

## Requirements
*   **Format**: GeoTIFF (`.tif`)
*   **Projection**: Must be projected (e.g., EPSG:32635 UTM Zone 35N), not raw Lat/Lon, for accurate tiling results.
*   **Resolution**: Tested on standard 1:50,000 scans (approx 200-300 DPI).

The pipeline will scan this directory for `*.tif` files during the tiling phase.