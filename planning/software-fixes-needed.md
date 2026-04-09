# Software Fixes Needed

Issues identified during Sessions 2026-04-08/09 that require code
changes before the 55-map production run.

## 1. ~~Tile-size auto-detection in `4_detect_mounds_batch.py`~~ — DONE (2026-04-08)

**Problem**: The `--tile-size` parameter defaults to `TILE_SIZE=512`
from `config.py`. When processing 384px tiles via `--tiles-dir
inputs/tiles_384`, forgetting to pass `--tile-size 384` silently
corrupts coordinates by a factor of 512/384 = 1.33, producing
300–500m systematic offsets. This was discovered when a v2 proposer
run produced zero TPs.

**Fix options** (in order of preference):
1. Auto-detect tile size from the first tile image in the manifest
2. Make `--tile-size` mandatory when `--tiles-dir` differs from
   the default `TILES_DIR`
3. Add a validation check comparing tile image dimensions against
   the configured tile size, erroring on mismatch

**Files**: `scripts/4_detect_mounds_batch.py` (lines 603–606, 730),
`scripts/lib_batch_api.py` (lines 1013–1016, 1451)

**Reference**: Observation 214, working-notes.md

## 2. ~~Batch API support in `4_detect_mounds_batch.py`~~ — DONE (2026-04-08)

**Problem**: The proposer detection script (`4_detect_mounds_batch.py`)
only supports real-time API calls. The Batch API (50% cost discount)
is implemented in `lib_batch_api.py` and accessible via `run_phase2.py`,
but `run_phase2.py` requires a study YAML and has a more complex
interface. For production runs of 2,400+ proposer calls, batch mode
should be available directly from the simpler detection script.

**Fix**: Add `--mode {realtime,batch}` flag to
`4_detect_mounds_batch.py`, mirroring the interface in `run_pv.py
verify`. When `--mode batch`, use `lib_batch_api.run_batch_unit()`
instead of the real-time `process_single_tile()` path.

**Files**: `scripts/4_detect_mounds_batch.py`, `scripts/lib_batch_api.py`

**Motivation**: The 55-map production run requires 5 × 7,833 = 39,165
proposer calls. At real-time pricing this is ~$51; at batch pricing
~$26. The cost difference justifies the engineering effort.

## 3. ~~Recursive tile directory scanning in `4_detect_mounds_batch.py`~~ — DONE (2026-04-09)

**Problem**: The manifest tile-matching logic
(`4_detect_mounds_batch.py`, lines 976–979) only scans one level of
subdirectories (`map_dir.glob("*.png")`). When tiles are double-nested
(e.g., `tiles_dir/K-35-042-3/K-35-042-3/*.png`), the script silently
finds zero tiles and exits. This was caught by the 55-map smoke test
(2026-04-08) and worked around by flattening the directory structure.

**Fix**: Change `map_dir.glob("*.png")` to `map_dir.glob("**/*.png")`
or `map_dir.rglob("*.png")` in the manifest matching block (line 978)
and the scan-all fallback (line 1008). This makes the script robust to
both single-nested and double-nested tile directory structures.

**Files**: `scripts/4_detect_mounds_batch.py` (lines 978, 1008)

**Reference**: 55-map generalisation run smoke test, 2026-04-08

## 4. ~~Recursive raster path resolution in `extract_candidates.py`~~ — DONE (2026-04-09)

**Problem**: `resolve_raster_path()` (line 84–105) only looks in the
immediate `rasters_dir` for `{map_name}.tif`. When rasters are in
subdirectories (e.g., `inputs/rasters/Russian1981_32635/K-35-042-3.tif`),
passing `--rasters-dir inputs/rasters` silently falls back to tile PNGs,
potentially truncating edge crops. The workaround is to pass the exact
subdirectory path (`--rasters-dir inputs/rasters/Russian1981_32635`).

**Fix**: Add recursive search or a configurable search depth to
`resolve_raster_path()`. One approach: try `rasters_dir.rglob(pattern)`
after the direct match fails.

**Files**: `scripts/extract_candidates.py` (lines 84–105)

## 5. ~~Scale `MAX_ACCEPTABLE_TILE_FAILURES` with chunk size in `lib_batch_api.py`~~ — ALREADY RESOLVED

Code already uses rate-based threshold: `MAX_ACCEPTABLE_TILE_FAILURE_RATE
= 0.20` with `MIN_ACCEPTABLE_TILE_FAILURES = 10` floor. For 4,000
tiles, `max(10, 4000 × 0.20) = 800`, which accommodates the ~560
HIGH-thinking truncation failures. The fix described below was the
original issue; the code was updated before this document was written.

**Original problem**: `MAX_ACCEPTABLE_TILE_FAILURES = 10` is a hardcoded
threshold calibrated for 60-tile batch units (10/60 = 17% tolerance).
When using larger chunks (e.g., 4,000 tiles via `--max-batch-tiles`),
even a modest ~14% HIGH-thinking truncation rate produces ~560
failures, exceeding the threshold by 56×. This causes `complete_batch_unit()`
to reject the chunk as failed despite having 86% valid results, and
triggers expensive sync retries on all 560 tiles before giving up.

**Fix**: Replace the hardcoded threshold with a percentage of the
submitted tile count:

```python
max_failures = max(10, int(len(ctx.submitted_keys) * 0.15))
```

This preserves the original 10-tile minimum for small units while
scaling to ~600 for 4,000-tile chunks. The sync retry loop should
also respect this scaled threshold.

**Files**: `scripts/lib_batch_api.py` (line 86, and the check at
line 1769)

**Reference**: 55-map generalisation run, 2026-04-09

## 6. ~~Flex mode (`--service-tier`) support~~ — DONE (2026-04-09)


Added `--service-tier {standard,flex}` to `4_detect_mounds_batch.py`,
`run_pv.py verify`, and `lib_verifier.py`. Flex gives 50% discount
with synchronous 1–15 min latency, avoiding batch API queue congestion.
Requires SDK ≥v1.69.0 (upgraded to v1.71.0).

## 7. ~~Pin SDK version in requirements~~ — DONE (2026-04-09)

`google-genai` upgraded from 1.56.0 to 1.71.0. Should be pinned in
`requirements.txt` or `pyproject.toml` to prevent drift.

## 8. ~~Test failure from SDK upgrade~~ — DONE (2026-04-09)

`test_batch_api.py::TestCompleteBatchUnit::test_parse_failure_retried_successfully`
fails after the 1.56→1.71 upgrade. The sync retry mock is no longer
called. Low priority — the retry logic works in production, the test
may need updating for SDK internal changes.

## 9. ~~Update token bucket governor for Tier 3 limits~~ — DONE (2026-04-09)

The `TokenBucketGovernor` defaults are calibrated for Tier 1
(RPM=1,440, TPM=720,000). Tier 3 allows RPM=20,000, TPM=20M. With
current settings we use 7% of RPM capacity. Updating defaults would
allow ~60 workers instead of 10–12, cutting the 55-map proposer run
from hours to ~20 minutes.
