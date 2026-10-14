#!/usr/bin/env bash
# W1-4 replay (fault-window re-check, Session 164). D42 class B re-run
# (run_classb.sh of 2026-10-06 06:42Z) in a detached replay tree at
# 7121c969f, the HEAD sapphire had pulled when the original ran (transcript
# 2026-10-06T06:42:14Z; 7121c969f..349eb178c changes one planning file).
# Differences from run_classb.sh, none computational: scratch B is under my
# output directory, not /tmp/regen-b (the wrapper regen_pes_v2.py is copied
# with only that path changed); the eight steps run at most two processes at
# once, and the three pool steps one at a time with --workers 2 instead of
# 8/8/6. PYTHONHASHSEED=0 as in the original. Then the outputs are copied
# into the tree's class-b directory as at 06:47:33Z, and
# scripts/annotate_classb_permutation.py (from e7b32de0b) runs --write.
set -u
T=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-1-to-4-7121c969f
O=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-1-to-4-out/w1-4${RUN_TAG:-}
S=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w1-1-to-4
W=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/d42-implementation-2026-10-05-scripts/wrappers
cd "$T" || exit 1
[ "$(git rev-parse HEAD)" = "$(git rev-parse 7121c969f)" ] || { echo "wrong HEAD"; exit 1; }
source "$HOME/Code/map-reader-llm/.venv/bin/activate"
export PYTHONHASHSEED=0
export PYTHONPATH=$S/netguard
B=$O/regen-b; SC=/home/shawn/cc-scratch/bootstrap-cis
rm -rf "$B"; mkdir -p $B/384-march $B/384-e39 $B/phase3a-high-text $B/eval $B/resweep
: > $B/status.tsv
step() { local n=$1; shift; local t0=$(date +%s); "$@" > "$B/$n.log" 2>&1 < /dev/null; printf '%s\t%s\t%ss\n' "$n" "$?" "$(( $(date +%s)-t0 ))" >> $B/status.tsv; }
slot() { while [ "$(jobs -rp | wc -l)" -ge 2 ]; do wait -n; done; }

# The wrappers as run: regen_384.py and regen_pes_v2.py (01ab11db6), and
# regen_384_e39.py made by the session's own sed (06:41:54Z).
cp "$W/regen_384.py" "$B/regen_384.py"
sed "s|/tmp/regen-b|$B|g" "$W/regen_pes_v2.py" > "$B/regen_pes_v2.py"
sed 's|return json.loads(subprocess.check_output(\["git", "-C", str(REPO), "show", f"e686e695e:{I4_SWEEP}"\]))|return json.loads((REPO / I4_SWEEP).read_text())  # E39 (current) sweep, D44 figure to cite|' "$B/regen_384.py" > "$B/regen_384_e39.py"
diff "$B/regen_384.py" "$B/regen_384_e39.py" > "$B/sed-e39.diff"
diff "$W/regen_pes_v2.py" "$B/regen_pes_v2.py" > "$B/sed-pes.diff"

# B-17/B-18 setup: March-named sweep copies with resolvable paths (moved-inputs § 3)
B="$B" python - <<"PY"
import json, os; from pathlib import Path
R = Path.cwd(); S = Path(os.environ["B"]) / "h11-384-pv-diagnostic"
for t in ("text", "image"):
    for old, new in (("flash", "minimal"), ("pro", "medium")):
        d = json.loads((R / f"results/h11-384-pv-diagnostic/pro-{t}-{new}-verifier/threshold_sweep.json").read_text())
        d["probabilities_file"] = str(R / f"outputs/h11/pv-diag-384/verified/pro-{t}-{new}-verifier/probabilities.json")
        d["manifest_file"] = str(R / f"outputs/h11/pv-diag-384/crops/pro-medium-{t}-baseline/candidate_manifest.json")
        o = S / f"pro-{t}-{old}-verifier"; o.mkdir(parents=True, exist_ok=True)
        (o / "threshold_sweep.json").write_text(json.dumps(d, indent=2))
PY
BND=inputs/vectors/bounds/384/full_evaluation_bounds.geojson
H=$B/h11-384-pv-diagnostic
slot; step b17-asis python scripts/evaluate_pv_results.py --bounds $BND compare --sweep-dirs $H/pro-text-flash-verifier $H/pro-text-pro-verifier --output-dir $B/eval/text-asis --pairwise --bootstrap 1000 --seed 42 &
slot; step b18-asis python scripts/evaluate_pv_results.py --bounds $BND compare --sweep-dirs $H/pro-image-flash-verifier $H/pro-image-pro-verifier --output-dir $B/eval/image-asis --pairwise --bootstrap 1000 --seed 42 &
slot; step b17-resweep python scripts/evaluate_pv_results.py --bounds $BND sweep --probabilities outputs/h11/pv-diag-384/verified/pro-text-minimal-verifier/probabilities.json --manifest outputs/h11/pv-diag-384/crops/pro-medium-text-baseline/candidate_manifest.json --output-dir $B/resweep/pro-text-flash-verifier --step 0.05 --bootstrap 1000 --seed 42 &
slot; step 384-march python $B/regen_384.py $B/384-march &
slot; step 384-e39 python $B/regen_384_e39.py $B/384-e39 &
wait
step pes-v1 python scripts/compute-pairwise-effect-sizes.py --data-dir $SC/data --pv-dir $SC/pv-data --output $B/pairwise-effect-sizes-v1inputs.json --workers 2
step pes-v2 python $B/regen_pes_v2.py --data-dir outputs/ --pv-dir archive/outputs-experimental-pilot/pv --output $B/pairwise-effect-sizes-v2.json --workers 2
step p3a-high python scripts/consensus-sweep-phase3a-high-text.py --data-dir $SC/data --pv-dir $SC/pv-data --output-dir $B/phase3a-high-text --workers 2
# B-17 re-sweep sensitivity: compare the re-swept minimal arm against medium
B="$B" python - <<"PY"
import json, os; from pathlib import Path
R = Path.cwd(); src = Path(os.environ["B"]) / "resweep/pro-text-flash-verifier/threshold_sweep.json"
d = json.loads(src.read_text())
d["probabilities_file"] = str(R / "outputs/h11/pv-diag-384/verified/pro-text-minimal-verifier/probabilities.json")
d["manifest_file"] = str(R / "outputs/h11/pv-diag-384/crops/pro-medium-text-baseline/candidate_manifest.json")
src.write_text(json.dumps(d, indent=2))
PY
cp -r $H/pro-text-pro-verifier $B/resweep/
step b17-resweep-compare python scripts/evaluate_pv_results.py --bounds $BND compare --sweep-dirs $B/resweep/pro-text-flash-verifier $B/resweep/pro-text-pro-verifier --output-dir $B/eval/text-resweep --pairwise --bootstrap 1000 --seed 42
echo ALL-DONE >> $B/status.tsv

# Copy into the tree's class-b directory exactly as at 2026-10-06T06:47:33Z
D=results/d42-retest-2026-10-05/class-b
mkdir -p $D
cp $B/384-march/fair-384-vs-512.json $D/fair-384-vs-512-march-sweep.json
cp $B/384-e39/fair-384-vs-512.json $D/fair-384-vs-512-e39-sweep.json
cp $B/pairwise-effect-sizes-v1inputs.json $D/pairwise-effect-sizes-v1-inputs.json
cp $B/pairwise-effect-sizes-v2.json $D/pairwise-effect-sizes-v2.json
cp $B/phase3a-high-text/phase3a-high-text-pairwise.json $D/
cp $B/eval/text-asis/comparison.json $D/b17-text-as-is-comparison.json
cp $B/eval/image-asis/comparison.json $D/b18-image-as-is-comparison.json
cp $B/eval/text-resweep/comparison.json $D/b17-text-resweep-comparison.json
cp $B/resweep/pro-text-flash-verifier/threshold_sweep.json $D/b17-minimal-resweep-threshold-sweep.json
cp $B/status.tsv $D/regen-status.tsv
# The annotator as committed in e7b32de0b, run --write in this tree
git show e7b32de0b:scripts/annotate_classb_permutation.py > scripts/annotate_classb_permutation.py
python scripts/annotate_classb_permutation.py --write > $O/annotate.log 2>&1; echo "annotate rc=$?" >> $O/annotate.log
echo ANNOTATED >> $B/status.tsv
