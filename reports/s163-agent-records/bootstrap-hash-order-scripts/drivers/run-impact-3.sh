#!/usr/bin/env bash
# D63 batch 3: the fair-384 replay on the MARCH library (1ca43283e) under
# hash seeds 0-7, twice; and second runs of the function-level harness on
# main and on the fix. Waits for batch 2 so at most three workers run.
set -u
echo $$ > /tmp/d63-runs/run_impact3.pid
while kill -0 "$(cat /tmp/d63-runs/run_impact2.pid)" 2>/dev/null; do sleep 30; done
REPO=~/scratch/d61-regenerations-2026-10-12/repo
PY=~/Code/map-reader-llm/.venv/bin/python
S=$REPO/reports/s163-agent-records/bootstrap-hash-order-scripts
R="$PY $S/script_replay.py --repo $REPO --work /tmp/d63-runs --python $PY --copy-from $HOME/Code/map-reader-llm"
COPY="archive/outputs-experimental-pilot/pv"
for c in text-1of10 text-5of10 text-6of10 image-3of5 image-baseline text-baseline text-10of10 image-1of5 image-5of5; do
  COPY="$COPY outputs/h11/pv-diag-384/verified/$c/probabilities.json outputs/h11/pv-diag-384/crops/$c/candidate_manifest.json"
done
ARGS="--archive scripts config.py inputs/vectors results/h11-384-pv-diagnostic results/pv/phase2 --copy $COPY"
CMD="I4_SWEEP_FILE=/tmp/d63-runs/i4-sweep-e686e695e.json $PY $S/fair384_replay.py out"
OUT="out/fair-384-vs-512.json out/pairwise-384px.json"
# Main-code harness tree: main's scripts and tests plus the harness file.
mkdir -p /tmp/d63-red/reports/s163-agent-records/bootstrap-hash-order-scripts
cp $S/hash_seed_harness.py /tmp/d63-red/reports/s163-agent-records/bootstrap-hash-order-scripts/
{
for run in run1 run2; do
  echo "$R --name fair384-march --ref 1ca43283e --tag s0123-$run --seeds 0 1 2 3 $ARGS --cmd '$CMD' --output $OUT"
  echo "$R --name fair384-march --ref 1ca43283e --tag s4567-$run --seeds 4 5 6 7 $ARGS --cmd '$CMD' --output $OUT"
done
echo "cd /tmp/d63-red && $PY reports/s163-agent-records/bootstrap-hash-order-scripts/hash_seed_harness.py --out /tmp/d63-runs/harness-main-run2.json"
echo "cd $REPO && $PY reports/s163-agent-records/bootstrap-hash-order-scripts/hash_seed_harness.py --out /tmp/d63-runs/harness-fix-run2.json"
} > /tmp/d63-runs/jobs3.txt
xargs -P 3 -I{} -d '\n' bash -c '{} > /dev/null 2>&1; echo "rc=$? :: {}" | cut -c1-200 >> /tmp/d63-runs/jobs3-done.txt' < /tmp/d63-runs/jobs3.txt
echo "ALL DONE $(date -u +%FT%TZ)" >> /tmp/d63-runs/jobs3-done.txt
