#!/usr/bin/env bash
# W2-3a group 1: rebuild the 28 K-ladder Phase 2 first-N unions at their
# generating commits, in disposable detached worktrees, and re-run the
# union-provenance check. Original commands (session transcript,
# agent-ae87367bcee3e0e5c, sapphire live checkout):
#   06:13:37Z  build_k_ladder_phase2_unions.py              (-> e3232d65b)
#   07:14:58Z  build_k_ladder_phase2_unions.py              (rebuild, -> 19e56ed80)
#   07:16:05Z  build_k_ladder_phase2_unions.py --check-only (-> 19e56ed80 unions.json)
#   07:16:27Z  check_unions.sh: check_union_provenance.py --union x28 --workers 4
#              --json-out results/k-ladder-2026-09-12/phase2/union-provenance.json
#   2026-10-05T04:03Z  --check-only                         (-> eb6d797e0 unions.json)
# Here the checker runs with --workers 1 (its results are sorted by union
# path, so the worker count cannot change the output). One process at a time.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
OUT=$ROOT/w2-3a-out/g1
source "$ROOT/env.sh"
export TMPDIR=$ROOT/w2-3a-out/tmp
mkdir -p "$OUT" "$TMPDIR"

stage() { echo; echo "##### $* ($(date -u +%FT%TZ)) #####"; }
status() { echo "##### exit=$1 #####"; }

for c in e3232d65b 19e56ed80 eb6d797e0; do
    t=$ROOT/w2-3a-$c
    if [ ! -d "$t" ]; then
        git -C "$HOME/Code/map-reader-llm" worktree add --detach "$t" "$c" 2>&1 | tail -1
    fi
done

stage "1. e3232d65b: full build"
cd "$ROOT/w2-3a-e3232d65b" || exit 1
git rev-parse HEAD
$PY scripts/build_k_ladder_phase2_unions.py > "$OUT/build-e3232d65b.log" 2>&1; status $?
tail -4 "$OUT/build-e3232d65b.log"

stage "2. 19e56ed80: full rebuild, then --check-only, then the provenance check"
cd "$ROOT/w2-3a-19e56ed80" || exit 1
git rev-parse HEAD
$PY scripts/build_k_ladder_phase2_unions.py > "$OUT/build-19e56ed80.log" 2>&1; status $?
tail -4 "$OUT/build-19e56ed80.log"
$PY scripts/build_k_ladder_phase2_unions.py --check-only > "$OUT/checkonly-19e56ed80.log" 2>&1
status $?
tail -3 "$OUT/checkonly-19e56ed80.log"
mapfile -t unions < <(
    $PY - <<'PYEOF'
import json
rungs = json.load(open("results/k-ladder-2026-09-12/phase2/unions.json"))["rungs"]
for r in rungs:
    print(f"{r['consensus_dir']}/consensus_t1.geojson")
PYEOF
)
args=()
for u in "${unions[@]}"; do args+=(--union "$u"); done
echo "unions: ${#unions[@]}"
$PY scripts/check_union_provenance.py "${args[@]}" --workers 1 \
    --json-out results/k-ladder-2026-09-12/phase2/union-provenance.json \
    > "$OUT/provenance-19e56ed80.log" 2>&1
status $?
grep -v '^\[' "$OUT/provenance-19e56ed80.log" | tail -12

stage "3. eb6d797e0: --check-only"
cd "$ROOT/w2-3a-eb6d797e0" || exit 1
git rev-parse HEAD
$PY scripts/build_k_ladder_phase2_unions.py --check-only > "$OUT/checkonly-eb6d797e0.log" 2>&1
status $?
tail -3 "$OUT/checkonly-eb6d797e0.log"

echo
echo "##### ALL STAGES ATTEMPTED ($(date -u +%FT%TZ)) #####"
