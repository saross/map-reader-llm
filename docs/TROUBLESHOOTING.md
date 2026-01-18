# Troubleshooting Guide

Common issues and solutions for the VLM Burial Mound Detection pipeline.

## API Issues

### Rate Limiting

**Symptom**: API calls fail with 429 errors or "rate limit exceeded" messages.

**Solutions**:

1. Reduce batch size with `--batch-size` parameter
2. Increase delay between calls (configure in `config.py`)
3. Use exponential backoff (built into the pipeline)
4. Check your API quota and consider upgrading your plan

### Authentication Errors

**Symptom**: "Invalid API key" or authentication failures.

**Solutions**:

1. Verify `.env` file exists in project root
2. Check API key format matches expected pattern
3. Ensure no trailing whitespace in API key
4. Regenerate API key if expired

```bash
# Check if .env exists and has content
cat .env | head -1
```

### Timeout Errors

**Symptom**: Requests fail with timeout errors on large tiles or complex prompts.

**Solutions**:

1. Reduce tile complexity (fewer examples in few-shot prompt)
2. Check network connectivity
3. Retry failed tiles with `--retry-failed` flag

## Tile Processing Issues

### Black Borders on Edge Tiles

**Symptom**: Tiles at image edges have black/empty borders.

**Explanation**: This is expected behaviour. The tiling script uses `boundless=True` which pads out-of-bounds regions with black pixels (value 0). Edge tiles may have partial coverage.

**Impact**: Minimal. The VLM handles partial tiles well. Edge tiles are included for completeness.

### Missing Geospatial Metadata

**Symptom**: Tiles don't load correctly in QGIS or lack CRS information.

**Solutions**:

1. Verify `.pgw` and `.png.aux.xml` sidecar files exist alongside each tile
2. Re-run `preprocess_tiling.py` to regenerate metadata
3. Check source GeoTIFF has valid CRS

```bash
# Check if sidecar files exist
ls inputs/tiles/K-35-052-4_32635/*.pgw | head -5
ls inputs/tiles/K-35-052-4_32635/*.aux.xml | head -5
```

### Tile Not Found Errors

**Symptom**: Detection script reports "tile not found" for certain tiles.

**Solutions**:

1. Verify manifest file matches actual tile files
2. Check tile filename format: `{map_name}_x{col}_y{row}.png`
3. Regenerate manifests with `generate_tile_bounds.py`

## Detection Issues

### Zero Detections

**Symptom**: Detection script completes but finds no mounds.

**Possible Causes**:

1. Empty tiles (no mounds present) — check with reference data
2. Prompt configuration issue — verify config JSON is valid
3. API response parsing error — check raw responses in outputs

**Diagnostic Steps**:

```bash
# Check raw API responses
ls outputs/raw_responses/

# Verify config loads correctly
python -c "import json; print(json.load(open('prompts/configs/detect_image-only.json')))"
```

### Coordinate Misalignment

**Symptom**: Detections don't align with reference points in QGIS.

**Solutions**:

1. Verify CRS consistency (project uses EPSG:32635)
2. Check tile bounds calculation in `generate_tile_bounds.py`
3. Ensure reference data uses same CRS

```bash
# Check detection CRS
python -c "import geopandas as gpd; print(gpd.read_file('outputs/detections.geojson').crs)"
```

### Duplicate Detections

**Symptom**: Same location detected multiple times.

**Explanation**: Expected with overlapping tiles (STRIDE < TILE_SIZE). The evaluation script handles deduplication using 20m clustering.

## Evaluation Issues

### F1 Score Calculation Errors

**Symptom**: Evaluation script fails or produces unexpected metrics.

**Solutions**:

1. Verify reference data exists in `inputs/vectors/`
2. Check detection GeoJSON format is valid
3. Ensure bounds file matches detection file

### Missing Reference Data

**Symptom**: "No reference vectors found" error.

**Solutions**:

1. Place reference GeoJSON files in `inputs/vectors/`
2. Use naming convention: `reference_{map_name}.geojson`
3. Verify CRS matches project (EPSG:32635)

## Environment Issues

### Import Errors

**Symptom**: `ModuleNotFoundError` when running scripts.

**Solutions**:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import geopandas; import rasterio; print('OK')"
```

### Path Resolution Errors

**Symptom**: Scripts fail to find config files or directories.

**Solutions**:

1. Run scripts from project root directory
2. Use absolute paths where supported
3. Check `config.py` paths match your setup

## Memory Issues

### Out of Memory During Tiling

**Symptom**: Tiling script crashes with memory errors.

**Solutions**:

1. Process one map at a time
2. Reduce TILE_SIZE in `config.py` (increases tile count)
3. Close other applications

### Large Output Files

**Symptom**: Output directory grows very large.

**Explanation**: Raw API responses and detection files can be substantial.

**Solutions**:

1. Archive completed runs to external storage
2. Use `--skip-raw-save` flag if raw responses not needed
3. Compress outputs: `tar -czvf run_backup.tar.gz outputs/`

## Getting Help

If issues persist:

1. Check [GitHub Issues](https://github.com/your-repo/issues) for known problems
2. Review execution logs in `outputs/logs/`
3. Enable verbose logging with `--verbose` flag
4. Open a new issue with:
   - Error message (full traceback)
   - Command that caused the error
   - Python version (`python --version`)
   - Operating system
