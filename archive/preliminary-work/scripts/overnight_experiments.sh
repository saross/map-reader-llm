#!/bin/bash
# Master Overnight Experiment Script
# 1. Job A: Gemini 3 Pro (v3.5 Single Stage) N=5
# 2. Job B: Gemini 3 Flash (v3.5 Swarm) N=30
# 3. Job C: Gemini 3 Pro (v4.6 Two-Stage Verifier) N=1


source venv/bin/activate
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi
export PYTHONPATH=$PYTHONPATH:.

echo "Starting Overnight Experiments..."
echo "API Key Length: ${#GOOGLE_API_KEY}"


# --- JOB A: Gemini 3 Pro | v3.5 (Single Stage) | N=5 ---
echo ">>> Starting Job A: Gemini 3 Pro (v3.5) N=5"
python3 scripts/generate_overnight_configs.py # Ensure configs exist

# Loop 5 times
for i in 5; do
    echo "Job A Run $i/5"
    python3 scripts/4_detect_mounds_batch.py \
        --config prompts/configs/detect_image-only.json \
        --manifest inputs/target_tiles_manifest.json \
        --output "run_${i}" \
        --workers 5
done

echo ">>> Job A Complete."


# --- JOB B: Gemini 3 Flash | v3.5 (Flash Swarm) | N=30 ---
# echo ">>> Starting Job B: Gemini 3 Flash (v3.5) N=30"

# # Loop 30 times
# for i in {1..30}; do
#     echo "Job B Run $i/30"
#     python3 scripts/4_detect_mounds_batch.py \
#         --config prompts/configs/detect_image-only.json \
#         --manifest inputs/target_tiles_manifest.json \
#         --output "run_${i}" \
#         --workers 5
# done

# echo ">>> Job B Complete."


# --- JOB C: Gemini 3 Pro | v4.6 (Verifier) | N=1 ---
echo ">>> Starting Job C: Gemini 3 Pro (v4.6 Verifier) N=1"
mkdir -p outputs/overnight/job_c_pro_verifier

# Input: Standard Candidate Pool (from v4.2 Proposer)
# Script: 5_verify_crops.py
python3 scripts/5_verify_crops.py \
    --candidates outputs/results/v4.2_temp_0_7_train/run_01.geojson \
    --output outputs/overnight/job_c_pro_verifier/verified_v4.6_pro.geojson \
    --config prompts/configs/verify_image-only.json \
    --workers 5 \
    --iterations 1

echo ">>> Job C Complete."

echo "All Overnight Experiments Finished."

