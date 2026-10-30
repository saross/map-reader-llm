#!/usr/bin/env bash
# Re-run the fast jobs at the fix commit and compare with the chain outputs.
S=$HOME/scratch/kladder-mcc-join-2026-10-30; V=$S/verify; L=$S/logs/verify
mkdir -p $L; echo $$ > $L/verify.pid; echo RUNNING > $L/verify.state
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
cd $V || exit 9
K=results/k-ladder-2026-09-12; CLIP=$K/clipped-mcc-2026-10-30; R=$K/mcc-join-2026-10-30; OUT=$V/$R
BB=inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson
for J in id geometric-primary geometric-contains; do
  F=(); [ $J = id ] || F=(--tile-join $J)
  $PY scripts/k_ladder_mcc_test.py "${F[@]}" --ladders $R/inputs/phase2-ladders-compat-326181bcd.json --bounds $BB --output-dir $OUT/$J/phase2-mcc-test > $L/p2_$J.log 2>&1 < /dev/null &
  $PY scripts/k_ladder_mcc_test.py "${F[@]}" --ladders $CLIP/ladders-clipped.json --conditions $CLIP/tiering-input/run-conditions.json --bounds $BB --output-dir $OUT/$J/clipped-mcc-test > $L/cl_$J.log 2>&1 < /dev/null &
  $PY scripts/era1_leaderboard_tiering.py --analysis-id k-ladder-tier-e-2026-09-12 --conditions $K/tier-e/tiering-input/run-conditions.json --analyses $K/tier-e/tiering-input/run-analyses.json --bounds $BB --output-dir $OUT/$J/tier-e --buffer 20 --n-permutations 10000 --seed 42 --permute-mcc "${F[@]}" > $L/te_$J.log 2>&1 < /dev/null &
done
wait
$PY $S/wt/reports/s166-agent-records/k-ladder-mcc-join-scripts/make_registries.py $V $R/inputs/phase2-ladders-compat-326181bcd.json $R $OUT/registries > $L/reg.log 2>&1
$PY scripts/k_ladder_mcb.py --registry $CLIP/mcb-registry.json --output-dir $OUT/id/clipped-mcb > $L/mcbc_id.log 2>&1 < /dev/null &
for J in geometric-primary geometric-contains; do
  $PY scripts/k_ladder_mcb.py --tile-join $J --metrics mcc --registry $OUT/registries/$J-clipped-registry.json --output-dir $OUT/$J/clipped-mcb > $L/mcbc_$J.log 2>&1 < /dev/null &
done
wait
python3 - > $L/compare.txt 2>&1 <<PYEOF
import json, pathlib
a = pathlib.Path("$S/wt/$R"); b = pathlib.Path("$OUT")
skip = {"generated_at_utc", "git_commit"}
def strip(x):
    if isinstance(x, dict): return {k: strip(v) for k, v in x.items() if k not in skip}
    if isinstance(x, list): return [strip(v) for v in x]
    return x
n = bad = 0
for f in sorted(b.rglob("*.json")):
    if "registries" in f.parts: continue
    g = a / f.relative_to(b); n += 1
    if not g.exists() or strip(json.loads(f.read_text())) != strip(json.loads(g.read_text())):
        bad += 1; print("DIFF", f.relative_to(b))
print(f"compared {n} json files; {bad} differ")
PYEOF
grep -q " 0 differ" $L/compare.txt && echo DONE > $L/verify.state || echo FAILED > $L/verify.state
