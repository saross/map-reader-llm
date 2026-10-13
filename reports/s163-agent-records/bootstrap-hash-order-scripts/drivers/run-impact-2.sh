#!/usr/bin/env bash
# D63 impact replays, batch 2 (fair-384 and the B-17/B-18 PV pairwise).
# Waits for batch 1 to exit so that at most three workers run at once.
set -u
echo $$ > /tmp/d63-runs/run_impact2.pid
while kill -0 "$(cat /tmp/d63-runs/run_impact.pid)" 2>/dev/null; do sleep 30; done
REPO=~/scratch/d61-regenerations-2026-10-12/repo
PY=~/Code/map-reader-llm/.venv/bin/python
S=$REPO/reports/s163-agent-records/bootstrap-hash-order-scripts
R="$PY $S/script_replay.py --repo $REPO --work /tmp/d63-runs --python $PY --copy-from $HOME/Code/map-reader-llm"
FAIR_COPY=""
for c in text-1of10 text-5of10 text-6of10 image-3of5 image-baseline text-baseline text-10of10 image-1of5 image-5of5; do
  FAIR_COPY="$FAIR_COPY outputs/h11/pv-diag-384/verified/$c/probabilities.json outputs/h11/pv-diag-384/crops/$c/candidate_manifest.json"
done
FAIR_ARGS="--archive scripts config.py inputs/vectors archive/outputs-experimental-pilot/pv results/h11-384-pv-diagnostic results/pv/phase2 --copy $FAIR_COPY"
FAIR_CMD="I4_SWEEP_FILE=/tmp/d63-runs/i4-sweep-e686e695e.json $PY $S/fair384_replay.py out"
FAIR_OUT="out/fair-384-vs-512.json out/pairwise-384px.json"
PV_COPY=""
for t in text image; do
  for v in minimal medium; do PV_COPY="$PV_COPY outputs/h11/pv-diag-384/verified/pro-$t-$v-verifier/probabilities.json"; done
  PV_COPY="$PV_COPY outputs/h11/pv-diag-384/crops/pro-medium-$t-baseline/candidate_manifest.json"
done
PV_ARGS="--archive scripts config.py inputs/vectors/references inputs/vectors/bounds/384/full_evaluation_bounds.geojson results/h11-384-pv-diagnostic --copy $PV_COPY"
PV_CMD="$PY $S/pv_pairwise_replay.py"
PV_OUT="out/text-asis/comparison.json out/image-asis/comparison.json"
{
for run in run1 run2; do
  echo "$R --name fair384 --ref origin/main --tag s01-$run --seeds 0 1 $FAIR_ARGS --cmd '$FAIR_CMD' --output $FAIR_OUT"
  echo "$R --name fair384 --ref origin/main --tag s23-$run --seeds 2 3 $FAIR_ARGS --cmd '$FAIR_CMD' --output $FAIR_OUT"
  echo "$R --name fair384 --ref bootstrap-hash-order --tag s12-$run --seeds 1 2 $FAIR_ARGS --cmd '$FAIR_CMD' --output $FAIR_OUT"
  echo "$R --name pvpair --ref origin/main --tag $run --seeds 0 1 2 3 $PV_ARGS --cmd '$PV_CMD' --output $PV_OUT"
  echo "$R --name pvpair --ref bootstrap-hash-order --tag $run --seeds 1 2 $PV_ARGS --cmd '$PV_CMD' --output $PV_OUT"
done
} > /tmp/d63-runs/jobs2.txt
xargs -P 3 -I{} -d '\n' bash -c '{} > /dev/null 2>&1; echo "rc=$? :: {}" | cut -c1-200 >> /tmp/d63-runs/jobs2-done.txt' < /tmp/d63-runs/jobs2.txt
echo "ALL DONE $(date -u +%FT%TZ)" >> /tmp/d63-runs/jobs2-done.txt
