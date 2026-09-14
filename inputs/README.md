# Inputs

Place your source Soviet Topographic Maps and vector data here.

## Directory Structure

*   `rasters/`: Place source GeoTIFFs (`.tif`) and associated metadata (`.aux.xml`) here.
*   `vectors/`: Vector data organised into:
    *   `bounds/`: GeoJSON bounds files for tile sets (calibration, holdout)
    *   `references/`: Ground truth and reference GeoJSON files
*   `tiles/`: Pre-processed PNG map tiles at 512 x 512 px on a 448 px stride
    (Era 1), with manifest and metadata files:
    *   `calibration_manifest.json`: Tiles for few-shot library development (20)
    *   `validation_manifest.json`: Tiles for evaluation (60)
    *   `full_evaluation_manifest.json`: The Era-1 evaluation frame — the 360
        physical tiles minus the 20 calibration tiles (340)
    *   `tile_selection_metadata.json`: Full selection provenance (seeds, mound
        counts, etc.). Two fields carry errata annotations: `parameters.tile_size`
        is the 448 px **stride**, not the tile size, and the per-tile
        `mound_count` values are superseded (erratum **E87**; corrected counts
        in `docs/methodology/preregistration/osf/tile-mound-counts-recomputed-2026-09-13.md`)
*   `tiles_384/`: The same sheets re-tiled at 384 x 384 px on a 336 px step
    (Era 2), with `full_evaluation_manifest.json` (487),
    `validation_manifest.json` (240) and `tile_selection_metadata.json`.
    `calibration_manifest.json` here is the literal `[]` **by design, not by
    omission**: the 384 px grid has no calibration set of its own — the
    exclusion geometry is derived from the 512 px calibration tiles' footprint —
    but `scripts/generate_tile_bounds.py` requires the file to exist in its
    default mode (`--tiles-dir inputs/tiles_384`) and exits if it is missing, so
    the empty array is a required placeholder that yields a zero-feature
    `calibration_bounds.geojson`.
*   `calibration/h10-384/`: The H10 nested calibration pools (20 ⊂ 40 ⊂ 80 ⊂ 160,
    seed 42) and the 327-tile test manifest, selected over the 384 px frame.
*   `provenance/`: `manifest-dependencies.json` — the registry of manifests that
    declare provenance from another set, with each source's blob hash at
    declaration time. Checked by `scripts/check_manifest_provenance.py`
    (erratum **E86**).
*   `examples/`: Few-shot example images for prompts.
    *   `neutral-naming/MANIFEST.md`: the neutral-filename mapping and the
        provenance of every example crop
    *   `null-tiles/`: the three empty exemplars, plus
        `null_overlap_by_frame.json` — which evaluation tiles overlap their
        pixels (erratum **E86**)

## Requirements (Rasters)

*   **Format**: GeoTIFF (`.tif`)
*   **Projection**: Must be projected (e.g., EPSG:32635 UTM Zone 35N), not raw Lat/Lon, for accurate tiling results.
*   **Resolution**: Tested on standard 1:50,000 scans (approx 200-300 DPI).

The pipeline will scan `inputs/rasters/` for `*.tif` files during the tiling phase.
