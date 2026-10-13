#!/usr/bin/env bash
# Red-sentinel harness for tests/test_w27_origin_route.py (D62 (1), step 3).
# Real copies only (git archive + cp, never symlinks).
#   base  - PR #38's head (origin/d60-w27-fastscorer) with the new test -> red
#   fixed - the branch's working tree                                    -> green
#   m1-m3 - one deliberate breakage each of the fix                      -> red
set -u
CLONE=~/scratch/d60-w27-fastscorer-2026-10-12/repo
MUT=~/scratch/origin-gap-h13-copies-2026-10-13/mut-w27
PY=~/Code/map-reader-llm/.venv/bin/python
export PYTHONPYCACHEPREFIX=~/scratch/origin-gap-h13-copies-2026-10-13/pyc-mut
TEST=tests/test_w27_origin_route.py
W27=reports/w27-replicate-floors-2026-10-06-scripts
FILES="$W27/w27_55map_subset_replicates.py $W27/floors-v2/floors2_lib.py scripts/h13_k_sensitivity.py"
make_tree() {  # $1 = name, $2 = git ref for the base tree
  local d=$MUT/$1; rm -rf "$d"; mkdir -p "$d"
  git -C $CLONE archive "$2" scripts tests pytest.ini config.py $W27 | tar -x -C "$d"
  cp -a "$CLONE/$TEST" "$d/tests/"
  if find "$d" -type l | grep -q .; then echo "SYMLINK FOUND in $d"; exit 9; fi
}
work() { for f in $FILES; do cp -a "$CLONE/$f" "$MUT/$1/$f"; done; }
run() { ( cd $MUT/$1 && $PY -m pytest $TEST -q -p no:cacheprovider 2>&1 | tail -1 ) | sed "s/^/$1: /"; }
mutate() {  # $1 = tree, $2 = file, $3 = old, $4 = new
  $PY - "$MUT/$1/$2" "$3" "$4" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
assert s.count(sys.argv[2]) == 1, sys.argv[2]
p.write_text(s.replace(sys.argv[2], sys.argv[3]))
PYEOF
}
make_tree base origin/d60-w27-fastscorer; run base
make_tree fixed HEAD; work fixed; run fixed
make_tree m1 HEAD; work m1
mutate m1 $W27/w27_55map_subset_replicates.py \
  'gdf["source_tiles"] = pd.Series([list(o) for o in origins], index=gdf.index, dtype=object)' \
  'pass'
run m1
make_tree m2 HEAD; work m2
mutate m2 $W27/floors-v2/floors2_lib.py \
  '        origins.append(sorted({t for m in members.tolist() for t in tiles[m]}))
    LAST_MEMBERS["masks"] = masks
    return np.asarray(cents), np.asarray(votes, dtype=int), origins' \
  '        origins.append([])
    LAST_MEMBERS["masks"] = masks
    return np.asarray(cents), np.asarray(votes, dtype=int), origins'
run m2
make_tree m3 HEAD; work m3
mutate m3 $W27/w27_55map_subset_replicates.py \
  '[parse_tile_list((c.get("properties") or {}).get("source_tiles")) for c in cands]' \
  '[[] for c in cands]'
run m3
