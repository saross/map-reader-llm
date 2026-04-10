#!/bin/bash
# 55-Map Generalisation — Iterative Straggler Cleanup
# ====================================================
# Recovers stragglers from each of the 5 proposer runs via multiple
# escalating cleanup passes:
#
#   Pass A: Standard config, 5 retries, base-wait 10s
#   Pass B: Standard config, 10 retries, base-wait 20s (longer backoff)
#   Pass C: Safe-mode config (max_output_tokens=2048), 5 retries
#
# All passes resume on the existing GeoJSON file via --output.
# Before/after coverage snapshots are written for each pass so failure
# patterns can be characterised post-hoc (which pass recovered each tile).
#
# Usage:
#   nohup bash scripts/55maps-cleanup-stragglers.sh \
#     > outputs/55maps-generalisation/cleanup.log 2>&1 &

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate
export PYTHONUNBUFFERED=1

OUTDIR="outputs/55maps-generalisation"
TILES_DIR="inputs/tiles_384_55maps"
MANIFEST="$TILES_DIR/full_evaluation_manifest.json"
CONFIG_STD="prompts/configs/detect_brief-text.json"
CONFIG_SAFE="prompts/configs/detect_brief-text-safemode.json"
RECORDS_DIR="$OUTDIR/cleanup-records"

mkdir -p "$RECORDS_DIR"

echo "============================================="
echo "55-Map Iterative Straggler Cleanup"
echo "Started: $(date)"
echo "============================================="
echo ""

# Helper: snapshot current coverage for a run
snapshot() {
    local run=$1
    local tag=$2
    local run_dir="$OUTDIR/proposer/detect_brief-text/run_$run"
    python3 - <<PYEOF
import json, glob, os
files = sorted(glob.glob("$run_dir/detections-detect_brief-text-3-flash-*.geojson"))
if not files:
    print(f"run_$run ($tag): no geojson")
else:
    data = json.load(open(files[-1]))
    tiles = data.get("processed_tiles", [])
    snap = {
        "run": $run,
        "tag": "$tag",
        "file": files[-1],
        "n_processed": len(tiles),
        "n_features": len(data.get("features", [])),
        "processed_tiles": sorted(tiles),
    }
    os.makedirs("$RECORDS_DIR/run_$run", exist_ok=True)
    with open(f"$RECORDS_DIR/run_$run/$tag.json", "w") as f:
        json.dump(snap, f)
    print(f"run_$run ($tag): {len(tiles)}/8541 tiles, {len(data.get('features', []))} features")
PYEOF
}

# Find the existing GeoJSON filename for a run (so --output can target it)
get_existing_filename() {
    local run=$1
    local run_dir="$OUTDIR/proposer/detect_brief-text/run_$run"
    ls "$run_dir"/detections-detect_brief-text-3-flash-*.geojson 2>/dev/null | head -1 | xargs -I{} basename {}
}

# Run one cleanup pass
cleanup_pass() {
    local run=$1
    local pass_name=$2
    local config=$3
    local max_retries=$4
    local base_wait=$5
    local workers=$6

    local run_dir="$OUTDIR/proposer/detect_brief-text/run_$run"
    local existing_filename=$(get_existing_filename "$run")

    if [ -z "$existing_filename" ]; then
        echo "ERROR: No existing geojson found for run $run — skipping"
        return 1
    fi

    echo ""
    echo "--- Run $run / Pass $pass_name ---"
    echo "Config: $config"
    echo "Retries: $max_retries, base-wait: ${base_wait}s, workers: $workers"
    echo "Resume target: $run_dir/$existing_filename"
    echo "Started: $(date)"

    snapshot "$run" "before-$pass_name"

    # Pass --output with the existing filename so resume logic finds it.
    # The --output flag accepts a filename; the script prepends output-dir.
    python3 scripts/4_detect_mounds_batch.py \
        --config "$config" \
        --manifest "$MANIFEST" \
        --tiles-dir "$TILES_DIR" \
        --tile-size 384 \
        --temperature 0.7 \
        --thinking-level high \
        --mode realtime \
        --service-tier flex \
        --workers "$workers" \
        --max-retries "$max_retries" \
        --base-wait "$base_wait" \
        --output-dir "$run_dir" \
        --output "$existing_filename" \
        2>&1 \
        | tee -a "$RECORDS_DIR/run_$run/$pass_name.log" \
        || echo "WARNING: Pass $pass_name exited non-zero (stragglers expected)"

    snapshot "$run" "after-$pass_name"
    echo "Completed: $(date)"
}

# Main loop: 3 passes per run × 5 runs
for run in 1 2 3 4 5; do
    echo ""
    echo "============================================="
    echo "=== RUN $run / 5 ==="
    echo "============================================="
    snapshot "$run" "initial"

    # Pass A: standard, moderate retries
    cleanup_pass "$run" "A-standard" "$CONFIG_STD" 5 10 30

    # Pass B: standard, longer backoff for persistent 503s
    cleanup_pass "$run" "B-longer-backoff" "$CONFIG_STD" 10 20 20

    # Pass C: safe-mode, targets thinking-token-exhaustion parse failures
    cleanup_pass "$run" "C-safemode" "$CONFIG_SAFE" 5 10 20

    snapshot "$run" "final"
done

echo ""
echo "============================================="
echo "All cleanup passes complete: $(date)"
echo "Records: $RECORDS_DIR"
echo "============================================="
