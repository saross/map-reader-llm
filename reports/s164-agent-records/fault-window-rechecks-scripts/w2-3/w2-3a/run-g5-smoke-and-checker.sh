#!/usr/bin/env bash
# W2-3a group 5: (a) the pre-launch audit's smoke inputs (9a934eaef), and
# (b) today's check_union_provenance.py (origin/main 718d0ee08) as a
# cross-check on the 28 Phase 2 unions and their 28 crop manifests as of
# 326181bcd.
# (a) Original (session transcript, agent-ae87367bcee3e0e5c, sapphire live
# checkout at 2484074fd, whose scripts equal 9a934eaef's):
#   06:15:32Z python -c '... features[:5] ... json.dump(d, open(out, "w"))'
#   06:15:36Z run_pv.py extract --proposer .../union_smoke5.geojson
#             --output-dir outputs/k-ladder-2026-09-12/smoke/crops --padding 75
#   06:15:40Z run_pv.py verify ... (API; NOT replayed)
# (b) today's checker reads, never writes, the 326181bcd replay tree; its JSON
# goes to the out directory. PYTHONDONTWRITEBYTECODE keeps the branch
# worktree free of byte-code caches. One process.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
OUT=$ROOT/w2-3a-out/g5
source "$ROOT/env.sh"
export TMPDIR=$ROOT/w2-3a-out/tmp PYTHONDONTWRITEBYTECODE=1
mkdir -p "$OUT" "$TMPDIR"

stage() { echo; echo "##### $* ($(date -u +%FT%TZ)) #####"; }
status() { echo "##### exit=$1 #####"; }

T=$ROOT/w2-3a-9a934eaef
if [ ! -d "$T" ]; then
    git -C "$HOME/Code/map-reader-llm" worktree add --detach "$T" 9a934eaef 2>&1 | tail -1
fi
cd "$T" || exit 1
git rev-parse HEAD

stage "a1. the five-feature smoke union"
mkdir -p outputs/k-ladder-2026-09-12/smoke
$PY -c "
import json, pathlib
src = pathlib.Path(\"outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/consensus-n1/consensus_t1.geojson\")
d = json.load(open(src))
d[\"features\"] = d[\"features\"][:5]
out = pathlib.Path(\"outputs/k-ladder-2026-09-12/smoke/union_smoke5.geojson\")
json.dump(d, open(out, \"w\"))
print(\"wrote\", out, len(d[\"features\"]), \"features\")
"
status $?

stage "a2. the smoke crops (rasters copied in, read-only source)"
mkdir -p inputs/rasters
cp -p "$HOME"/Code/map-reader-llm/inputs/rasters/K-35-0*.tif \
      "$HOME"/Code/map-reader-llm/inputs/rasters/K-35-0*.tif.aux.xml inputs/rasters/
$PY scripts/run_pv.py extract --proposer outputs/k-ladder-2026-09-12/smoke/union_smoke5.geojson \
    --output-dir outputs/k-ladder-2026-09-12/smoke/crops --padding 75 > "$OUT/smoke-extract.log" 2>&1
status $?
tail -4 "$OUT/smoke-extract.log"

stage "b. today's checker: 28 unions and 28 manifests as of 326181bcd"
T2=$ROOT/w2-3a-326181bcd
mapfile -t args < <(
    cd "$T2" && $PY - <<'PYEOF'
import json, sys
sys.path.insert(0, ".")
from scripts.run_k_ladder_phase2_verifier import resolve_paths
rungs = json.load(open("results/k-ladder-2026-09-12/phase2/unions.json"))["rungs"]
for r in rungs:
    print("--union"); print(f"{r['consensus_dir']}/consensus_t1.geojson")
PYEOF
)
$PY "$ROOT/wt/scripts/check_union_provenance.py" --repo-root "$T2" "${args[@]}" \
    --workers 1 --json-out "$OUT/today-checker-unions.json" > "$OUT/today-checker-unions.log" 2>&1
status $?
grep -v '^\[' "$OUT/today-checker-unions.log" | tail -8
cd "$T2" || exit 1
mapfile -t rows < <(
    $PY - <<'PYEOF'
import json, sys
sys.path.insert(0, ".")
from scripts.run_k_ladder_phase2_verifier import resolve_paths
rungs = json.load(open("results/k-ladder-2026-09-12/phase2/unions.json"))["rungs"]
for r in rungs:
    p = resolve_paths(r)
    print(f"{p['crops_dir']}/candidate_manifest.json\t{r['consensus_dir']}/consensus_t1.geojson")
PYEOF
)
: > "$OUT/today-checker-manifests.log"
for row in "${rows[@]}"; do
    m=${row%%$'\t'*}; u=${row##*$'\t'}
    n=$(echo "$m" | tr '/' '_')
    $PY "$ROOT/wt/scripts/check_union_provenance.py" --repo-root "$T2" --manifest "$m" \
        --manifest-union "$u" --json-out "$OUT/today-checker-manifest-$n.json" \
        >> "$OUT/today-checker-manifests.log" 2>&1
    echo "exit=$? $m" >> "$OUT/today-checker-manifests.log"
done
grep -c "exit=0" "$OUT/today-checker-manifests.log"

echo
echo "##### ALL STAGES ATTEMPTED ($(date -u +%FT%TZ)) #####"
