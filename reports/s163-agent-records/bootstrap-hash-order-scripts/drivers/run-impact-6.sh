#!/usr/bin/env bash
# D63 batch 6, after PR #33 merged into main: the fix on the merged branch
# (d63-merge-tmp) for every replay family (seed 1, twice); the harness on
# merged main and on the merged fix (twice each); the red sentinel on merged
# main. Waits for batches 4-5. Three workers.
set -u
echo $$ > /tmp/d63-runs/run_impact6.pid
while kill -0 "$(cat /tmp/d63-runs/run_impact45.pid)" 2>/dev/null; do sleep 30; done
REPO=~/scratch/d61-regenerations-2026-10-12/repo
PY=~/Code/map-reader-llm/.venv/bin/python
S=$REPO/reports/s163-agent-records/bootstrap-hash-order-scripts
R="$PY $S/script_replay.py --repo $REPO --work /tmp/d63-runs --python $PY --copy-from $HOME/Code/map-reader-llm"
REF=d63-merge-tmp
# --- argument sets, as in batches 1, 2 and 4 ---
RETEST_CMD=""; RETEST_OUT=""
for pair in phase2a:phase2a phase2b-track1-image:phase2b-track1 phase2b-track2-text:phase2b-track2 \
            phase2c-track1-image-exploratory:phase2c-exploratory phase2c-track1-image:phase2c-track1 \
            phase2c-track2-text:phase2c-track2 phase2d-track1-image:phase2d-track1 \
            phase2d-track2-text:phase2d-track2 phase2e:phase2e; do
  key=${pair%%:*}; out=${pair##*:}
  RETEST_CMD="$RETEST_CMD $PY scripts/evaluate_retest_all.py --phase $key --output out/$out-evaluation.json;"
  RETEST_OUT="$RETEST_OUT out/$out-evaluation.json"
done
RETEST_ARGS="--archive scripts config.py inputs/vectors/references inputs/vectors/bounds/full_evaluation_bounds.geojson --copy outputs/retest/phase2a outputs/retest/phase2b outputs/retest/phase2c outputs/retest/phase2d outputs/retest/phase2e"
CONS=$(cd ~/Code/map-reader-llm && grep -ho '"consensus_dir": "[^"]*"' scripts/analyse_secondary_effects.py scripts/analyse_secondary_effects_text.py | sed 's/"consensus_dir": "//; s/"$//' | sort -u | tr '\n' ' ')
INT_CMD="$PY $S/interaction_replay.py --module analyse_secondary_effects --out out/image.json; $PY $S/interaction_replay.py --module analyse_secondary_effects_text --out out/text.json"
INT_ARGS="--archive scripts config.py inputs/vectors/references inputs/vectors/bounds/384/full_evaluation_bounds.geojson --copy $CONS"
SD_ARGS="--archive scripts config.py results/phase3a-text-matrix/secondary_effects.json results/secondary-effects/secondary_effects.json"
SD_OUT="results/secondary-effects-consensus-sd/sd_shrinkage.json results/secondary-effects-consensus-sd/report.md"
PVC=""
for c in text-1of10 text-5of10 text-6of10 image-3of5 image-baseline text-baseline text-10of10 image-1of5 image-5of5; do
  PVC="$PVC outputs/h11/pv-diag-384/verified/$c/probabilities.json outputs/h11/pv-diag-384/crops/$c/candidate_manifest.json"
done
FAIR_ARGS="--archive scripts config.py inputs/vectors archive/outputs-experimental-pilot/pv results/h11-384-pv-diagnostic results/pv/phase2 --copy $PVC"
FAIR_CMD="I4_SWEEP_FILE=/tmp/d63-runs/i4-sweep-e686e695e.json $PY $S/fair384_replay.py out"
PV_COPY=""
for t in text image; do
  for v in minimal medium; do PV_COPY="$PV_COPY outputs/h11/pv-diag-384/verified/pro-$t-$v-verifier/probabilities.json"; done
  PV_COPY="$PV_COPY outputs/h11/pv-diag-384/crops/pro-medium-$t-baseline/candidate_manifest.json"
done
PV_ARGS="--archive scripts config.py inputs/vectors/references inputs/vectors/bounds/384/full_evaluation_bounds.geojson results/h11-384-pv-diagnostic --copy $PV_COPY"
# --- merged-main tree for the harness and the red sentinel ---
rm -rf /tmp/d63-red-merged && mkdir -p /tmp/d63-red-merged
git -C $REPO archive origin/main scripts tests config.py pytest.ini | tar -x -C /tmp/d63-red-merged
mkdir -p /tmp/d63-red-merged/reports/s163-agent-records/bootstrap-hash-order-scripts
cp $S/hash_seed_harness.py /tmp/d63-red-merged/reports/s163-agent-records/bootstrap-hash-order-scripts/
git -C $REPO show $REF:tests/test_hash_seed_determinism.py > /tmp/d63-red-merged/tests/test_hash_seed_determinism.py
{
echo "$R --name retest --ref $REF --tag s1-run1 --seeds 1 $RETEST_ARGS --cmd '$RETEST_CMD' --output $RETEST_OUT"
echo "$R --name retest --ref $REF --tag s1-run2 --seeds 1 $RETEST_ARGS --cmd '$RETEST_CMD' --output $RETEST_OUT"
for run in run1 run2; do
  echo "$R --name interaction --ref $REF --tag $run --seeds 1 $INT_ARGS --cmd '$INT_CMD' --output out/image.json out/text.json"
  echo "$R --name sd-v1 --ref $REF --tag $run --seeds 1 $SD_ARGS --cmd '$PY scripts/analyse_consensus_sd_shrinkage.py' --output $SD_OUT"
  echo "$R --name fair384 --ref $REF --tag s1-$run --seeds 1 $FAIR_ARGS --cmd '$FAIR_CMD' --output out/fair-384-vs-512.json out/pairwise-384px.json"
  echo "$R --name pvpair --ref $REF --tag $run --seeds 1 $PV_ARGS --cmd '$PY $S/pv_pairwise_replay.py' --output out/text-asis/comparison.json out/image-asis/comparison.json"
  echo "cd /tmp/d63-red-merged && $PY reports/s163-agent-records/bootstrap-hash-order-scripts/hash_seed_harness.py --out /tmp/d63-runs/harness-mergedmain-$run.json"
  echo "cd $REPO && $PY reports/s163-agent-records/bootstrap-hash-order-scripts/hash_seed_harness.py --out /tmp/d63-runs/harness-mergedfix-$run.json"
done
echo "cd /tmp/d63-red-merged && $PY -m pytest -q -p no:cacheprovider tests/test_hash_seed_determinism.py > /tmp/d63-runs/red-mergedmain.txt 2>&1"
echo "cd $REPO && $PY -m pytest -q -p no:cacheprovider tests/test_hash_seed_determinism.py > /tmp/d63-runs/green-mergedfix.txt 2>&1"
} > /tmp/d63-runs/jobs6.txt
xargs -P 3 -I{} -d '\n' bash -c '{} > /dev/null 2>&1; echo "rc=$? :: {}" | cut -c1-200 >> /tmp/d63-runs/jobs6-done.txt' < /tmp/d63-runs/jobs6.txt
echo "ALL DONE $(date -u +%FT%TZ)" >> /tmp/d63-runs/jobs6-done.txt
