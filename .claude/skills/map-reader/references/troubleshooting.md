# Troubleshooting Guide

Common issues and solutions for VLM detection experiments.

---

## API Issues

### Rate Limiting

**Symptom**: `429 Too Many Requests` errors or exponential backoff messages.

**Solutions**:

1. Reduce worker count:

   ```bash
   python scripts/4_detect_mounds_batch.py --workers 1 ...
   ```

2. Add delay between requests (built into script, but can be extended)

3. Check API quota in Google Cloud Console

4. For large batches, run overnight or split across multiple sessions

### Authentication Errors

**Symptom**: `401 Unauthorized` or `Invalid API key` errors.

**Solutions**:

1. Verify API key is set:

   ```bash
   echo $GOOGLE_API_KEY | head -c 10  # Should show AIza...
   ```

2. Check key is valid in Google AI Studio

3. Ensure key has Gemini API access enabled

4. If using `config.py`, verify the key is correctly loaded

### Timeout Errors

**Symptom**: Requests timing out, especially on large tiles.

**Solutions**:

1. Check network connectivity

2. Reduce `max_output_tokens` if response is very long

3. Try a smaller tile size if processing large images

4. Retry the specific tile:

   ```bash
   python scripts/4_detect_mounds_batch.py --continue-from <tile_name> ...
   ```

---

## Input File Issues

### Missing Manifest

**Symptom**: `FileNotFoundError: inputs/tiles/calibration_manifest.json`

**Solutions**:

1. Verify the manifest exists:

   ```bash
   ls inputs/tiles/*.json
   ```

2. Generate manifest if missing:

   ```bash
   python scripts/preprocess_tiling.py --generate-manifest
   ```

3. Check path spelling in command

### Missing Tiles

**Symptom**: `FileNotFoundError` for specific tile paths.

**Solutions**:

1. Verify tiles exist:

   ```bash
   ls inputs/tiles/*/
   ```

2. Check manifest paths match actual file locations

3. Regenerate manifest if tile structure changed

### Missing Ground Truth

**Symptom**: `FileNotFoundError: inputs/vectors/references/mounds-reference.geojson`

**Solutions**:

1. Verify ground truth exists:

   ```bash
   ls inputs/vectors/references/
   ```

2. Check if file is in alternative location

3. Ensure file wasn't accidentally deleted or moved

### Missing Example Images

**Symptom**: Config validation fails due to missing example images.

**Solutions**:

1. Verify symlinks exist:

   ```bash
   ls -la inputs/examples/neutral/
   ```

2. Check symlinks point to valid targets:

   ```bash
   file inputs/examples/neutral/example_01.png
   ```

3. Recreate broken symlinks:

   ```bash
   cd inputs/examples/neutral/
   rm example_01.png
   ln -s ../canonical/burial_mound_01.png example_01.png
   ```

---

## Configuration Issues

### Invalid Config JSON

**Symptom**: `JSONDecodeError` when loading config.

**Solutions**:

1. Validate JSON syntax:

   ```bash
   python -m json.tool prompts/configs/<config>.json
   ```

2. Check for trailing commas (not allowed in JSON)

3. Ensure all strings are properly quoted

### Missing System Instruction

**Symptom**: `FileNotFoundError` for instruction file.

**Solutions**:

1. Verify instruction file exists:

   ```bash
   ls prompts/system-instructions/
   ```

2. Check `instruction_file` field in config matches actual filename

3. Ensure file extension is `.md`

### Example Path Mismatch

**Symptom**: Config loads but examples not found.

**Solutions**:

1. Check example paths in config use correct prefix (usually `neutral/`)

2. Verify `EXAMPLES_DIR` in `config.py` points to correct location

3. Test with dry-run:

   ```bash
   python scripts/4_detect_mounds_batch.py --dry-run ...
   ```

---

## Output Issues

### Empty Detection Results

**Symptom**: GeoJSON files contain no features.

**Possible causes**:

1. Model not detecting any features (legitimate result for empty tiles)

2. System instruction may be too restrictive

3. Example library may not include similar features

**Solutions**:

1. Check a few tiles manually in QGIS to verify ground truth

2. Try with a different config (e.g., more examples)

3. Check model response in `.meta.json` for clues

### Malformed GeoJSON

**Symptom**: `JSONDecodeError` when reading detection results.

**Solutions**:

1. Check if file was partially written (interrupted run)

2. Delete corrupted file and re-run:

   ```bash
   rm outputs/<experiment>/pass_01/<tile>.geojson
   python scripts/4_detect_mounds_batch.py --continue-from <tile> ...
   ```

3. Check disk space

### Coordinate Misalignment

**Symptom**: Detections appear offset from ground truth.

**Solutions**:

1. Verify CRS consistency (should be EPSG:32635)

2. Check tile georeferencing

3. Verify ground truth CRS matches

---

## Analysis Issues

### Accuracy Report Fails

**Symptom**: `6_accuracy_report.py` crashes or produces no output.

**Solutions**:

1. Verify all input files exist and are valid GeoJSON

2. Check CRS consistency across all inputs

3. Ensure bounds file covers the detection area

4. Check for empty feature collections

### Consensus Analysis Fails

**Symptom**: `7_analyse_consensus.py` fails to merge passes.

**Solutions**:

1. Verify all pass directories exist:

   ```bash
   ls outputs/<experiment>/pass_*/
   ```

2. Ensure consistent tile naming across passes

3. Check that each pass completed successfully

---

## Performance Issues

### Slow Processing

**Symptom**: Detection takes longer than expected.

**Solutions**:

1. Check API latency (may be server-side issue)

2. Reduce tile count for testing

3. Use `--limit` flag for quick tests:

   ```bash
   python scripts/4_detect_mounds_batch.py --limit 5 ...
   ```

### High Memory Usage

**Symptom**: Script crashes with `MemoryError`.

**Solutions**:

1. Reduce worker count

2. Process fewer tiles per batch

3. Check for memory leaks in custom modifications

---

## Getting Help

If issues persist:

1. Check recent changes to configs or scripts

2. Review error messages in full

3. Test with minimal config (single tile, simple config)

4. Document the exact command, error message, and context
