#!/usr/bin/env bash
# D42 class B regeneration (D43, D44), Session 161. Scratch outputs only.
set -u
cd ~/Code/map-reader-llm || exit 1
source .venv/bin/activate
export PYTHONHASHSEED=0
B=/tmp/regen-b; SC=/home/shawn/cc-scratch/bootstrap-cis
mkdir -p $B/384-march $B/384-e39 $B/phase3a-high-text $B/eval $B/resweep
: > $B/status.tsv
step() { local n=$1; shift; local t0=$(date +%s); "$@" > "$B/$n.log" 2>&1 < /dev/null; printf '%s\t%s\t%ss\n' "$n" "$?" "$(( $(date +%s)-t0 ))" >> $B/status.tsv; }

# B-17/B-18 setup: March-named sweep copies with resolvable paths (moved-inputs § 3)
python - <<"PY"
import json; from pathlib import Path
R = Path.cwd(); S = Path("/tmp/regen-b/h11-384-pv-diagnostic")
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
step b17-asis python scripts/evaluate_pv_results.py --bounds $BND compare --sweep-dirs $H/pro-text-flash-verifier $H/pro-text-pro-verifier --output-dir $B/eval/text-asis --pairwise --bootstrap 1000 --seed 42 &
step b18-asis python scripts/evaluate_pv_results.py --bounds $BND compare --sweep-dirs $H/pro-image-flash-verifier $H/pro-image-pro-verifier --output-dir $B/eval/image-asis --pairwise --bootstrap 1000 --seed 42 &
step b17-resweep python scripts/evaluate_pv_results.py --bounds $BND sweep --probabilities outputs/h11/pv-diag-384/verified/pro-text-minimal-verifier/probabilities.json --manifest outputs/h11/pv-diag-384/crops/pro-medium-text-baseline/candidate_manifest.json --output-dir $B/resweep/pro-text-flash-verifier --step 0.05 --bootstrap 1000 --seed 42 &
step 384-march python $B/regen_384.py $B/384-march &
step 384-e39 python $B/regen_384_e39.py $B/384-e39 &
step pes-v1 python scripts/compute-pairwise-effect-sizes.py --data-dir $SC/data --pv-dir $SC/pv-data --output $B/pairwise-effect-sizes-v1inputs.json --workers 8 &
step pes-v2 python $B/regen_pes_v2.py --data-dir outputs/ --pv-dir archive/outputs-experimental-pilot/pv --output $B/pairwise-effect-sizes-v2.json --workers 8 &
step p3a-high python scripts/consensus-sweep-phase3a-high-text.py --data-dir $SC/data --pv-dir $SC/pv-data --output-dir $B/phase3a-high-text --workers 6 &
wait
# B-17 re-sweep sensitivity: compare the re-swept minimal arm against medium
python - <<"PY"
import json; from pathlib import Path
R = Path.cwd(); src = Path("/tmp/regen-b/resweep/pro-text-flash-verifier/threshold_sweep.json")
d = json.loads(src.read_text())
d["probabilities_file"] = str(R / "outputs/h11/pv-diag-384/verified/pro-text-minimal-verifier/probabilities.json")
d["manifest_file"] = str(R / "outputs/h11/pv-diag-384/crops/pro-medium-text-baseline/candidate_manifest.json")
src.write_text(json.dumps(d, indent=2))
PY
cp -r $H/pro-text-pro-verifier $B/resweep/
step b17-resweep-compare python scripts/evaluate_pv_results.py --bounds $BND compare --sweep-dirs $B/resweep/pro-text-flash-verifier $B/resweep/pro-text-pro-verifier --output-dir $B/eval/text-resweep --pairwise --bootstrap 1000 --seed 42
echo ALL-DONE >> $B/status.tsv
