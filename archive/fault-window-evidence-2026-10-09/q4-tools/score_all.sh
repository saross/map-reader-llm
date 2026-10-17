#!/bin/bash
# Scratch re-score for D55 Q4 (throwaway): scores in the scratch clone only.
echo $$ > /home/shawn/scratch/q4-tools/score.pid
cd /home/shawn/scratch/q4-rescore-2026-10-08 || exit 9
CELLS=G3IMG-ARM2-K1-carried,G3IMG-ARM2-K1-f1-oracle,G3IMG-ARM2-K1-mcc-oracle,G3IMG-ARM2-K3-carried,G3IMG-ARM2-K3-f1-oracle,G3IMG-ARM2-K3-mcc-oracle,G3IMG-ARM2-K3-mcc-oracle-unconstrained,G3IMG-ARM2-K5-carried,G3IMG-ARM2-K5-f1-oracle,G3IMG-ARM2-K5-mcc-oracle,G3IMG-ARM2-K5-mcc-oracle-unconstrained
.venv/bin/python scripts/gemini37_image_55map_r2.py --campaign g3 --stage score --workers 6 --jobs 4 --cells "$CELLS"
echo "STEP g3-score exit=$?"
.venv/bin/python results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/inheritance_ladder.py --campaign g3 --stage score --workers 6 --jobs 4
echo "STEP inheritance-score exit=$?"
.venv/bin/python results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/replicate_k5_arm1.py --arm arm1 --stage tests
echo "STEP replicate-tests exit=$?"
echo "SCORE JOB FINISHED"
