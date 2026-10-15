#!/usr/bin/env bash
# W2-3a: compare every regenerated file of groups 2 to 5 with its committed
# blob at the generating commit (compare_files.py; crops by compare_crops.py;
# API outputs by check_api_outputs.py). Set-aside keys are named on each call.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
O=$ROOT/w2-3a-out
D=$ROOT/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w2-3/w2-3a
PY=$HOME/Code/map-reader-llm/.venv/bin/python
T2=$ROOT/w2-3a-326181bcd
TODAY=718d0ee08
R=results/k-ladder-2026-09-12/recovery-fix-2026-09-13

echo "== group 2: in-tree regenerations at 326181bcd"
$PY "$D/compare_files.py" --repo "$T2" --pairs "$O/g2/pairs-g2.tsv" --out "$D/cmp-g2-326181bcd.json" \
    --today $TODAY --ignore-key generated_at_utc --ignore-key updated_at_utc
echo "== group 2: were all 173 compared files rewritten by the replay (mtime after the marker)?"
$PY - "$O/g2/pairs-g2.tsv" "$O/g2/start-marker" <<'PYEOF'
import os, sys
marker = os.stat(sys.argv[2]).st_mtime
stale = [l.split("\t")[0] for l in open(sys.argv[1]) if l.strip()
         and os.stat(l.split("\t")[0]).st_mtime < marker]
print(len(stale), "not rewritten:", [s.split("/w2-3a-326181bcd/")[1] for s in stale])
PYEOF
echo "== group 2: crop manifests and PNGs"
$PY "$D/compare_crops.py" --repo "$T2" --commit 326181bcd --extract-root "$O/g2/extract" \
    --live-root "$HOME/Code/map-reader-llm" --out "$D/cmp-g2-crops.json"
echo "== group 2: API outputs, offline consistency"
$PY "$D/check_api_outputs.py" --tree "$T2" --smoke-tree "$ROOT/w2-3a-9a934eaef" \
    --out "$D/chk-api-outputs.json"

echo "== group 3"
G3=$O/g3
{
  for k in k1-carried k1-opmax k3-opmax k5; do
    printf "%s\t20c0a053f\t%s\n" "$G3/rescore/$k.geojson" "$R/materialised/$k.geojson"
  done
  for k in k1-carried k1-opmax k3-opmax; do
    printf "%s\t20c0a053f\t%s\n" "$G3/f1only-$k.json" "$R/f1-only/$k.json"
  done
  printf "%s\t20c0a053f\t%s\n" "$G3/rescore/operating-points.json" "$R/operating-points.json"
  printf "%s\t5166ddeda\t%s\n" "$G3/fixed-from-committed.json" "$R/operating-points.json"
  printf "%s\t5166ddeda\t%s\n" "$G3/fixed-from-regen.json" "$R/operating-points.json"
  printf "%s\t987534c03\t%s\n" "$G3/rescore-987534c03/k3-opmax.geojson" \
      "results/k-ladder-2026-09-12/phase2/materialised/g37-text-k3-verified-opmax.geojson"
  printf "%s\t987534c03\t%s\n" "$G3/rescore/k3-opmax.geojson" \
      "results/k-ladder-2026-09-12/phase2/materialised/g37-text-k3-verified-opmax.geojson"
  for f in evaluation.json evaluation.csv evaluation.md; do
    printf "%s\t20c0a053f\t%s\n" "$G3/rescore/grid-2026-08-18__g384-ov192-k5-verified-opmax/$f" \
        "$R/reproduced-k5-evaluation/$f"
  done
} > "$G3/pairs-g3.tsv"
$PY "$D/compare_files.py" --repo "$T2" --pairs "$G3/pairs-g3.tsv" --out "$D/cmp-g3.json" \
    --today $TODAY --ignore-key materialised --ignore-key cell_dir --ignore-key path \
    --ignore-key generated_at_utc --ignore-key timestamp
echo "== group 3: in-tree sweeps of the recovery-fixed stages (by-products)"
cat "$G3/git-status-63f4cac1c.txt" "$G3/git-status-987534c03.txt"

echo "== group 4"
G4=$O/g4
{
  printf "%s\tb949d5644\t%s\n" "$ROOT/w2-3a-b949d5644/results/k-ladder-2026-09-12/subpool-coverage-probe.json" \
      results/k-ladder-2026-09-12/subpool-coverage-probe.json
  printf "%s\t3013171cd\t%s\n" "$ROOT/w2-3a-3013171cd/results/k-ladder-2026-09-12/first-n-union-sizes.json" \
      results/k-ladder-2026-09-12/first-n-union-sizes.json
  for f in inventory.json inventory-tables.md; do
    printf "%s\tf4a1011a8\t%s\n" "$ROOT/w2-3a-f4a1011a8/results/k-ladder-2026-09-12/$f" \
        "results/k-ladder-2026-09-12/$f"
  done
} > "$G4/pairs-g4.tsv"
$PY "$D/compare_files.py" --repo "$T2" --pairs "$G4/pairs-g4.tsv" --out "$D/cmp-g4.json" \
    --today $TODAY --ignore-key generated_at_utc --ignore-line '^Generated 20[0-9T:+-]+ from '

echo "== group 5: smoke inputs"
T5=$ROOT/w2-3a-9a934eaef
{
  for p in outputs/k-ladder-2026-09-12/smoke/union_smoke5.geojson \
           outputs/k-ladder-2026-09-12/smoke/crops/candidate_manifest.json; do
    printf "%s\t9a934eaef\t%s\n" "$T5/$p" "$p"
  done
} > "$O/g5/pairs-g5.tsv"
$PY "$D/compare_files.py" --repo "$T2" --pairs "$O/g5/pairs-g5.tsv" --out "$D/cmp-g5-smoke.json" \
    --today $TODAY --ignore-key rasters_dir --ignore-key tiles_dir
