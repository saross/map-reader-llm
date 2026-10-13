#!/usr/bin/env bash
# D63 batches 4 and 5: re-run the fair-384 replays (today's main and the
# fix, refused comparisons recorded) and the fair-384 replay on the MARCH
# library (1ca43283e) under hash seeds 0-7; every job twice. Three workers.
set -u
echo $$ > /tmp/d63-runs/run_impact45.pid
REPO=~/scratch/d61-regenerations-2026-10-12/repo
PY=~/Code/map-reader-llm/.venv/bin/python
S=$REPO/reports/s163-agent-records/bootstrap-hash-order-scripts
R="$PY $S/script_replay.py --repo $REPO --work /tmp/d63-runs --python $PY --copy-from $HOME/Code/map-reader-llm"
PVC=""
for c in text-1of10 text-5of10 text-6of10 image-3of5 image-baseline text-baseline text-10of10 image-1of5 image-5of5; do
  PVC="$PVC outputs/h11/pv-diag-384/verified/$c/probabilities.json outputs/h11/pv-diag-384/crops/$c/candidate_manifest.json"
done
TODAY_ARGS="--archive scripts config.py inputs/vectors archive/outputs-experimental-pilot/pv results/h11-384-pv-diagnostic results/pv/phase2 --copy $PVC"
MARCH_ARGS="--archive scripts config.py inputs/vectors results/h11-384-pv-diagnostic results/pv/phase2 --copy archive/outputs-experimental-pilot/pv/results archive/outputs-experimental-pilot/pv/crops-150 $PVC"
CMD="I4_SWEEP_FILE=/tmp/d63-runs/i4-sweep-e686e695e.json $PY $S/fair384_replay.py out"
OUT="out/fair-384-vs-512.json out/pairwise-384px.json"
{
for run in run1 run2; do
  echo "$R --name fair384 --ref origin/main --tag s01-$run --seeds 0 1 $TODAY_ARGS --cmd '$CMD' --output $OUT"
  echo "$R --name fair384 --ref origin/main --tag s23-$run --seeds 2 3 $TODAY_ARGS --cmd '$CMD' --output $OUT"
  echo "$R --name fair384 --ref bootstrap-hash-order --tag s12-$run --seeds 1 2 $TODAY_ARGS --cmd '$CMD' --output $OUT"
  echo "$R --name fair384-march --ref 1ca43283e --tag s0123-$run --seeds 0 1 2 3 $MARCH_ARGS --cmd '$CMD' --output $OUT"
  echo "$R --name fair384-march --ref 1ca43283e --tag s4567-$run --seeds 4 5 6 7 $MARCH_ARGS --cmd '$CMD' --output $OUT"
done
} > /tmp/d63-runs/jobs45.txt
xargs -P 3 -I{} -d '\n' bash -c '{} > /dev/null 2>&1; echo "rc=$? :: {}" | cut -c1-200 >> /tmp/d63-runs/jobs45-done.txt' < /tmp/d63-runs/jobs45.txt
echo "ALL DONE $(date -u +%FT%TZ)" >> /tmp/d63-runs/jobs45-done.txt
