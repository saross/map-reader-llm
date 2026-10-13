#!/usr/bin/env bash
# D63 impact replays on sapphire: three workers, each job one script_replay
# invocation. Writes its own pid file; every job logs under /tmp/d63-runs.
set -u
echo $$ > /tmp/d63-runs/run_impact.pid
REPO=~/scratch/d61-regenerations-2026-10-12/repo
PY=~/Code/map-reader-llm/.venv/bin/python
S=$REPO/reports/s163-agent-records/bootstrap-hash-order-scripts
R="$PY $S/script_replay.py --repo $REPO --work /tmp/d63-runs --python $PY --copy-from $HOME/Code/map-reader-llm"
RETEST_CMD=""
for pair in phase2a:phase2a phase2b-track1-image:phase2b-track1 phase2b-track2-text:phase2b-track2 \
            phase2c-track1-image-exploratory:phase2c-exploratory phase2c-track1-image:phase2c-track1 \
            phase2c-track2-text:phase2c-track2 phase2d-track1-image:phase2d-track1 \
            phase2d-track2-text:phase2d-track2 phase2e:phase2e; do
  key=${pair%%:*}; out=${pair##*:}
  RETEST_CMD="$RETEST_CMD $PY scripts/evaluate_retest_all.py --phase $key --output out/$out-evaluation.json;"
  RETEST_OUT="${RETEST_OUT:-} out/$out-evaluation.json"
done
RETEST_ARGS="--archive scripts config.py inputs/vectors/references inputs/vectors/bounds/full_evaluation_bounds.geojson --copy outputs/retest/phase2a outputs/retest/phase2b outputs/retest/phase2c outputs/retest/phase2d outputs/retest/phase2e"
CONS=$(cd ~/Code/map-reader-llm && grep -ho '"consensus_dir": "[^"]*"' scripts/analyse_secondary_effects.py scripts/analyse_secondary_effects_text.py | sed 's/"consensus_dir": "//; s/"$//' | sort -u | tr '\n' ' ')
INT_CMD="$PY $S/interaction_replay.py --module analyse_secondary_effects --out out/image.json; $PY $S/interaction_replay.py --module analyse_secondary_effects_text --out out/text.json"
INT_ARGS="--archive scripts config.py inputs/vectors/references inputs/vectors/bounds/384/full_evaluation_bounds.geojson --copy $CONS"
SD_ARGS="--archive scripts config.py results/phase3a-text-matrix/secondary_effects.json results/secondary-effects/secondary_effects.json"
SD_CMD="$PY scripts/analyse_consensus_sd_shrinkage.py"
SD_OUT="results/secondary-effects-consensus-sd/sd_shrinkage.json results/secondary-effects-consensus-sd/report.md"
{
for run in run1 run2; do
  echo "$R --name retest --ref origin/main --tag s01-$run --seeds 0 1 $RETEST_ARGS --cmd '$RETEST_CMD' --output $RETEST_OUT"
  echo "$R --name retest --ref origin/main --tag s23-$run --seeds 2 3 $RETEST_ARGS --cmd '$RETEST_CMD' --output $RETEST_OUT"
  echo "$R --name retest --ref bootstrap-hash-order --tag s12-$run --seeds 1 2 $RETEST_ARGS --cmd '$RETEST_CMD' --output $RETEST_OUT"
  echo "$R --name interaction --ref origin/main --tag $run --seeds 0 1 2 3 $INT_ARGS --cmd '$INT_CMD' --output out/image.json out/text.json"
  echo "$R --name interaction --ref bootstrap-hash-order --tag $run --seeds 1 2 $INT_ARGS --cmd '$INT_CMD' --output out/image.json out/text.json"
  echo "$R --name sd-v1 --ref origin/main --tag $run --seeds 0 1 2 3 $SD_ARGS --cmd '$SD_CMD' --output $SD_OUT"
  echo "$R --name sd-v1 --ref bootstrap-hash-order --tag $run --seeds 1 2 $SD_ARGS --cmd '$SD_CMD' --output $SD_OUT"
done
} > /tmp/d63-runs/jobs.txt
xargs -P 3 -I{} -d '\n' bash -c '{} > /dev/null 2>&1; echo "rc=$? :: {}" | cut -c1-200 >> /tmp/d63-runs/jobs-done.txt' < /tmp/d63-runs/jobs.txt
echo "ALL DONE $(date -u +%FT%TZ)" >> /tmp/d63-runs/jobs-done.txt
