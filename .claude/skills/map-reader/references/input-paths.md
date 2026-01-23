# Input Paths Reference

Quick reference for all input files and directories used in detection experiments.

---

## Tile Manifests

| Manifest | Path | Purpose |
|----------|------|---------|
| Calibration | `inputs/tiles/calibration_manifest.json` | 20 tiles for Phase 1-2 |
| Validation | `inputs/tiles/validation_manifest.json` | Reserved for Phase 3 validation |
| Production | `inputs/tiles/production_manifest.json` | Full region coverage |

### Manifest Format

```json
{
  "tiles": [
    {
      "id": "tile_name",
      "path": "inputs/tiles/map_sheet/tile_name.tif",
      "bounds": [minx, miny, maxx, maxy]
    }
  ]
}
```

---

## Ground Truth

| Resource | Path |
|----------|------|
| Mound reference | `inputs/vectors/references/mounds-reference.geojson` |
| Alternative truth | `inputs/vectors/references/mounds-alternative.geojson` |

### Ground Truth Format

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [x, y]},
      "properties": {
        "id": "mound_001",
        "confidence": "high",
        "source": "field_survey"
      }
    }
  ]
}
```

---

## Region Bounds

| Bounds | Path | Purpose |
|--------|------|---------|
| Calibration | `inputs/vectors/bounds/calibration_bounds.geojson` | Phase 1-2 region |
| Validation | `inputs/vectors/bounds/validation_bounds.geojson` | Phase 3 region |
| Full region | `inputs/vectors/bounds/study_region.geojson` | Complete study area |

---

## Example Library

### Directory Structure

```text
inputs/examples/
├── neutral-naming/             # Neutral-named symlinks
│   ├── example_01.png         # Canon+ (burial mound)
│   ├── example_02.png         # Canon+ (settlement mound)
│   ├── example_03.png         # Canon+ (triangulation on mound)
│   ├── example_04.png         # Canon+ (benchmark on mound)
│   ├── example_05.png         # HP (hard positive 1)
│   ├── example_06.png         # HP (hard positive 2)
│   ├── example_07.png         # HP (hard positive 3)
│   ├── example_08.png         # HP (hard positive 4)
│   ├── example_09.png         # Canon- (triangulation alone)
│   ├── example_10.png         # Canon- (benchmark alone)
│   ├── example_11.png         # HN (hard negative 1)
│   ├── example_12.png         # HN (hard negative 2)
│   ├── example_13.png         # HN (hard negative 3)
│   ├── example_14.png         # HN (hard negative 4)
│   ├── example_15.png         # Null (empty tile 1)
│   ├── example_16.png         # Null (empty tile 2)
│   ├── example_17.png         # Null (empty tile 3)
│   └── MANIFEST.md            # Provenance documentation
├── canonical/                  # Original canonical examples
├── hard-positives/            # Extracted HP crops
└── hard-negatives/            # Extracted HN crops
```

### Example Slot Assignments

| Slots | Category | Count | Description |
|-------|----------|-------|-------------|
| 01-04 | Canon+ | 4 | Clear canonical positives |
| 05-08 | HP | 4 | Hard positives (frequently missed) |
| 09-10 | Canon- | 2 | Clear canonical negatives |
| 11-14 | HN | 4 | Hard negatives (frequent FPs) |
| 15-17 | Null | 3 | Empty tiles |

---

## Configuration Files

| Type | Path |
|------|------|
| Prompt configs | `prompts/configs/*.json` |
| System instructions | `prompts/system-instructions/*.md` |

---

## Map Tiles

### Directory Structure

```text
inputs/tiles/
├── map_sheet_1/
│   ├── tile_001.tif
│   ├── tile_002.tif
│   └── ...
├── map_sheet_2/
│   └── ...
└── ...
```

### Tile Format

- Format: GeoTIFF (`.tif`)
- CRS: EPSG:32635 (UTM zone 35N)
- Size: Configurable (default 1024×1024 pixels)
- Resolution: Matches source map scan

---

## Output Directories

| Output | Path |
|--------|------|
| Detection results | `outputs/<experiment>/` |
| Analysis results | `results/<experiment>/` |
| Reports | `reports/` |

### Output Conventions

```text
outputs/
├── phase1-library/
│   ├── pass_01/
│   │   ├── tile_001.geojson
│   │   └── tile_001.meta.json
│   ├── pass_02/
│   └── ...
├── phase2a-h1/
│   ├── image-only/
│   └── brief-text/
└── ...
```

---

## Verification Commands

Check all critical inputs exist:

```bash
# Manifests
ls inputs/tiles/calibration_manifest.json
ls inputs/tiles/validation_manifest.json

# Ground truth
ls inputs/vectors/references/mounds-reference.geojson

# Bounds
ls inputs/vectors/bounds/calibration_bounds.geojson
ls inputs/vectors/bounds/validation_bounds.geojson

# Example library
ls inputs/examples/neutral-naming/example_*.png | wc -l  # Should be 17

# Configs
ls prompts/configs/*.json | wc -l

# System instructions
ls prompts/system-instructions/*.md | wc -l
```
