# Software Fixes Needed

Issues identified during Session 2026-04-08 that require code changes
before the 55-map production run.

## 1. Tile-size auto-detection in `4_detect_mounds_batch.py`

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

## 2. Batch API support in `4_detect_mounds_batch.py`

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
