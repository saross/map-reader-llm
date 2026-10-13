#!/usr/bin/env bash
# Red-sentinel harness for tests/test_library_copies_origins.py and the
# tier-2 tests/test_h13_origin_route_real.py (D62 (1)). Real copies only
# (git archive + cp). The tier-2 test reads outputs/h13/scoring and the
# reference and bounds vectors, so those are archived too.
set -u
CLONE=~/scratch/d60-1-input-vintage-2026-10-12/repo
MUT=~/scratch/origin-gap-h13-copies-2026-10-13/mut
PY=~/Code/map-reader-llm/.venv/bin/python
TESTS="tests/test_library_copies_origins.py tests/test_h13_origin_route_real.py"
FILES="scripts/lib_consensus.py scripts/analyse_diversity.py scripts/h13_k_sensitivity.py scripts/h13_aggregation_sweep.py"
make_tree() {  # $1 = name, $2 = BASE or WORK
  local d=$MUT/$1; rm -rf "$d"; mkdir -p "$d"
  git -C $CLONE archive origin/main scripts tests pytest.ini config.py \
      outputs/h13/scoring inputs/vectors/references inputs/vectors/bounds | tar -x -C "$d"
  if [ "$2" = WORK ]; then for f in $FILES; do cp -a "$CLONE/$f" "$d/$f"; done; fi
  for t in $TESTS; do cp -a "$CLONE/$t" "$d/tests/"; done
  if find "$d" -type l | grep -q .; then echo "SYMLINK FOUND in $d"; exit 9; fi
}
run() { ( cd $MUT/$1 && $PY -m pytest $TESTS -q -p no:cacheprovider 2>&1 | tail -1 ) | sed "s/^/$1: /"; }
mutate() {  # $1 = tree, $2 = file, $3 = python old, $4 = python new
  $PY - "$MUT/$1/$2" "$3" "$4" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
assert s.count(sys.argv[2]) == 1, sys.argv[2]
p.write_text(s.replace(sys.argv[2], sys.argv[3]))
PYEOF
}
make_tree base2 BASE; run base2
make_tree fixed2 WORK; run fixed2
make_tree m5 WORK
mutate m5 scripts/lib_consensus.py '"source_tiles": parse_tile_list(cluster["source_tiles"]),' '"source_tiles": [],'
run m5
make_tree m6 WORK
mutate m6 scripts/lib_consensus.py '"source_tiles": parse_tile_list(props.get("source_tiles")),' '"source_tiles": [],'
run m6
make_tree m7 WORK
mutate m7 scripts/analyse_diversity.py '[parse_tile_list(value) for value in recorded]' '[[] for value in recorded]'
run m7
make_tree m8 WORK
mutate m8 scripts/h13_aggregation_sweep.py 'assign_primary_tiles(gdf, bounds, origin=origins)' 'assign_primary_tiles(gdf[["geometry"]], bounds)'
run m8
