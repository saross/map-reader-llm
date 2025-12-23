#!/bin/bash
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.

echo ">>> Starting Re-run of Job A Run 4 (Temp 0.3)"
python3 scripts/4_detect_mounds_batch.py \
    --config prompts/configs/detect_image-only.json \
    --manifest inputs/target_tiles_manifest.json \
    --output "run_4" \
    --workers 5

echo ">>> Starting Re-run of Job A Run 5 (Temp 0.3)"
python3 scripts/4_detect_mounds_batch.py \
    --config prompts/configs/detect_image-only.json \
    --manifest inputs/target_tiles_manifest.json \
    --output "run_5" \
    --workers 5

echo ">>> Re-runs Complete."
