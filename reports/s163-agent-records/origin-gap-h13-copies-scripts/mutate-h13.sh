#!/usr/bin/env bash
# Red-sentinel harness for tests/test_h13_origin_route.py (D62 (1)).
# Builds REAL copies (git archive + cp, never symlinks) of the clone's
# scripts/ and tests/, then:
#   base   - origin/main's scripts with the new test file  -> expect red
#   fixed  - the branch's working tree                       -> expect green
#   m1..m4 - one deliberate breakage each of the fixed code  -> expect red
set -u
CLONE=~/scratch/d60-1-input-vintage-2026-10-12/repo
MUT=~/scratch/origin-gap-h13-copies-2026-10-13/mut
PY=~/Code/map-reader-llm/.venv/bin/python
TEST=tests/test_h13_origin_route.py
make_tree() {  # $1 = name, $2 = git ref for scripts (or WORK for working tree)
  local d=$MUT/$1; rm -rf "$d"; mkdir -p "$d"
  git -C $CLONE archive origin/main scripts tests pytest.ini config.py | tar -x -C "$d"
  if [ "$2" = WORK ]; then
    cp -a $CLONE/scripts/h13_k_sensitivity.py $CLONE/scripts/h13_aggregation_sweep.py "$d/scripts/"
  fi
  cp -a $CLONE/$TEST "$d/tests/"
  find "$d" -type l | grep . && { echo "SYMLINK FOUND in $d"; exit 9; }
}
run() {  # $1 = name
  ( cd $MUT/$1 && $PY -m pytest $TEST -q -p no:cacheprovider 2>&1 | tail -1 ) | sed "s/^/$1: /"
}
make_tree base origin/main; run base
make_tree fixed WORK; run fixed
# m1: score ignores the origins (legacy tiling, no column)
make_tree m1 WORK
$PY - "$MUT/m1/scripts/h13_k_sensitivity.py" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
a = 'gdf["source_tiles"] = pd.Series(kept, index=gdf.index, dtype=object)\n'
b = 'gdf["source_tile"] = assign_primary_tiles(gdf, bounds, origin=kept)'
assert s.count(a) == 1 and s.count(b) == 1
s = s.replace(a, 'pass\n').replace(b, 'gdf["source_tile"] = assign_primary_tiles(gdf, bounds)')
p.write_text(s)
PYEOF
run m1
# m2: cluster_votes_with_origins records no tiles
make_tree m2 WORK
$PY - "$MUT/m2/scripts/h13_k_sensitivity.py" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
a = 'origins.append(sorted({t for m in members.tolist() for t in tiles[m]}))'
assert s.count(a) == 1
p.write_text(s.replace(a, 'origins.append([])'))
PYEOF
run m2
# m3: write_cell tiles without the origin (keeps the column)
make_tree m3 WORK
$PY - "$MUT/m3/scripts/h13_aggregation_sweep.py" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
a = 'assign_primary_tiles(gdf, bounds, origin=origins)'
assert s.count(a) == 1
p.write_text(s.replace(a, 'assign_primary_tiles(gdf[["geometry"]], bounds, origin=None)'))
PYEOF
run m3
# m4: write_cell drops the origin column from the file
make_tree m4 WORK
$PY - "$MUT/m4/scripts/h13_aggregation_sweep.py" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
a = '                    "origin_tiles": row["origin_tiles"],\n'
assert s.count(a) == 1
p.write_text(s.replace(a, ''))
PYEOF
run m4
