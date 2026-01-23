# Visualisation Guide

How to view detection results and create publication-quality maps using QGIS.

## Prerequisites

- [QGIS](https://qgis.org/) 3.x or later
- Completed detection run with outputs in `outputs/` directory
- Reference data in `inputs/vectors/`

## Quick Start: Loading Results in QGIS

### 1. Load Base Map Tiles

1. Open QGIS
2. **Layer → Add Layer → Add Raster Layer**
3. Navigate to `inputs/tiles/{map_name}/`
4. Select any `.png` file — QGIS will auto-detect the `.pgw` world file and `.aux.xml` CRS

Alternatively, load the original GeoTIFF:

1. **Layer → Add Layer → Add Raster Layer**
2. Select `inputs/rasters/{map_name}.tif`

### 2. Load Detection Results

1. **Layer → Add Layer → Add Vector Layer**
2. Navigate to `outputs/`
3. Select the detection GeoJSON file (e.g., `run_01_detections.geojson`)
4. Ensure CRS is EPSG:32635 (UTM zone 35N)

### 3. Load Reference Data

1. **Layer → Add Layer → Add Vector Layer**
2. Navigate to `inputs/vectors/`
3. Select reference file (e.g., `reference_K-35-052-4_32635.geojson`)

### 4. Load Tile Bounds (Optional)

Useful for understanding tile coverage:

1. **Layer → Add Layer → Add Vector Layer**
2. Select `inputs/vectors/bounds/calibration_bounds.geojson` or `validation_bounds.geojson`

## Styling Recommendations

### Detection Polygons

1. Right-click detection layer → **Properties → Symbology**
2. Select **Simple Fill**
3. Settings:
   - Fill colour: Transparent or light yellow (#FFFF00, 30% opacity)
   - Stroke colour: Red (#FF0000)
   - Stroke width: 1.0 mm

### Reference Points

1. Right-click reference layer → **Properties → Symbology**
2. Select **Simple Marker**
3. Settings:
   - Symbol: Circle
   - Size: 3.0 mm
   - Fill colour: Green (#00FF00)
   - Stroke colour: Dark green (#006600)

### Tile Bounds

1. Right-click bounds layer → **Properties → Symbology**
2. Select **Simple Fill**
3. Settings:
   - Fill colour: Transparent
   - Stroke colour: Blue (#0000FF)
   - Stroke width: 0.5 mm
   - Stroke style: Dashed

## Comparing Detections to Ground Truth

### Visual Inspection

Layer order (bottom to top):

1. Base map (tiles or GeoTIFF)
2. Tile bounds (optional)
3. Reference points
4. Detection polygons

### True/False Positive Analysis

Load the evaluation outputs:

- `run_01_tp.geojson` — True positives (correct detections)
- `run_01_fp.geojson` — False positives (incorrect detections)
- `run_01_fn.geojson` — False negatives (missed ground truth)

Style each differently:

| Layer | Fill | Stroke |
|-------|------|--------|
| True Positives | Green (#00FF00, 40%) | Dark green |
| False Positives | Red (#FF0000, 40%) | Dark red |
| False Negatives | Orange (#FFA500, 40%) | Dark orange |

## Creating Publication Maps

### Basic Export

1. **Project → New Print Layout**
2. Add map item: **Add Item → Add Map**
3. Set scale and extent
4. Add legend, scale bar, north arrow as needed
5. **Layout → Export as Image** (PNG/JPEG) or **Export as PDF**

### Recommended Settings

- Resolution: 300 DPI for print, 150 DPI for web
- Format: PNG for raster quality, PDF for vector preservation
- Page size: A4 or letter for single-map figures

### Multi-Panel Figures

For comparing conditions:

1. Create multiple map items in the same layout
2. Lock each to the same extent for comparison
3. Add condition labels as text items

## Batch Visualisation

For systematic review of multiple tiles:

### QGIS Atlas Generation

1. **Project → New Print Layout**
2. Enable **Atlas** panel
3. Set coverage layer to tile bounds
4. Configure map item to be "Controlled by Atlas"
5. **Atlas → Export Atlas as Images**

This generates one image per tile, useful for systematic FP/FN review.

## Colour-Blind Friendly Palettes

Alternative colour schemes for accessibility:

| Category | Standard | Colour-blind Safe |
|----------|----------|-------------------|
| True Positive | Green | Blue (#0072B2) |
| False Positive | Red | Orange (#D55E00) |
| False Negative | Orange | Yellow (#F0E442) |
| Reference | Green | Cyan (#56B4E9) |

## Tips

### Performance

- For large tile sets, work with bounds layers rather than loading all tiles
- Use spatial indexes: **Vector → Data Management Tools → Create Spatial Index**

### Coordinate Reference System (CRS)

- Project CRS: EPSG:32635 (WGS 84 / UTM zone 35N)
- All outputs use this CRS
- If layers don't align, check **Layer Properties → Source → CRS**

### Exporting Figures for Papers

1. Set white background: **Project → Properties → General → Background colour**
2. Disable anti-aliasing for crisp vector export
3. Include scale bar with metric units
4. Add CRS notation in figure caption (not on map)

## Example QGIS Project Structure

```text
project.qgz
├── Base Maps (Group)
│   ├── K-35-052-4_32635.tif
│   └── K-35-053-3_Elenovo.tif
├── Reference Data (Group)
│   ├── reference_K-35-052-4_32635.geojson
│   └── reference_K-35-053-3_Elenovo.geojson
├── Detections (Group)
│   ├── run_01_detections.geojson
│   ├── run_01_tp.geojson
│   ├── run_01_fp.geojson
│   └── run_01_fn.geojson
└── Bounds (Group)
    ├── calibration_bounds.geojson
    └── validation_bounds.geojson
```

## Further Resources

- [QGIS Documentation](https://docs.qgis.org/)
- [Making Maps with QGIS](https://docs.qgis.org/latest/en/docs/training_manual/map_composer/)
- [Cartography Guide](https://www.axismaps.com/guide)
