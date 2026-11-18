#!/usr/bin/env bash
# ============================================================================
# perfect-detector-red-sentinel.sh
# ----------------------------------------------------------------------------
# Red sentinel for tests/test_perfect_detector.py (tile-join Wave 1, W1.2;
# planning/tile-join-wave-1-spec-2026-11-01.md). In a REAL-FILE copy (cp -r,
# never symlinks: docs/agent-guidance.md, "Mutation harnesses") of scripts/
# and tests/, with the inputs the real-frame fixtures read:
#   1. set the classification default back to id;
#   2. separately, remove the sheet restriction (frame-wide candidates in
#      sheet_join_candidate_tiles);
# the new tests must turn red for each. Then restore, confirm the copy's
# sources diff equal to the branch, and confirm the tests go green again.
# Not a pytest module: run it by hand, in a scratch directory, never in a
# checkout. Run on 2026-11-18 at 06fd89ffb (zbook): baseline 68 passed;
# mutation 1, 30 failed / 38 passed; mutation 2, 14 failed / 54 passed;
# restored copy IDENTICAL to the branch, 68 passed.
#
# Usage: bash tests/sentinels/perfect-detector-red-sentinel.sh SRC DEST
#   SRC  a checkout of the branch; DEST  a scratch directory (replaced).
# ============================================================================
set -u
SRC=$1; DEST=$2; PY=$HOME/Code/map-reader-llm/.venv/bin/python
rm -rf "$DEST"; mkdir -p "$DEST/inputs"
cp -r "$SRC/scripts" "$SRC/tests" "$DEST/"
cp -r "$SRC/inputs/vectors" "$DEST/inputs/"
cp "$SRC/pytest.ini" "$SRC/ruff.toml" "$SRC/config.py" "$DEST/"
echo "symlinks in copy: $(find "$DEST" -type l | wc -l)"
LIB="$DEST/scripts/lib_advanced_metrics.py"
cp "$LIB" "$DEST/lib.orig"
run() { (cd "$DEST" && $PY -m pytest tests/test_perfect_detector.py -q -p no:cacheprovider 2>&1 | tail -n 1); }
echo "== baseline in copy"; run
echo "== mutation 1: classification default back to id"
sed -i 's/^TILE_JOIN_CLASSIFICATION_DEFAULT: str = TILE_JOIN_SHEET_CONTAINS$/TILE_JOIN_CLASSIFICATION_DEFAULT: str = TILE_JOIN_ID/' "$LIB"
grep -n '^TILE_JOIN_CLASSIFICATION_DEFAULT' "$LIB"
run
cp "$DEST/lib.orig" "$LIB"
echo "== mutation 2: sheet restriction removed (frame-wide candidates)"
sed -i -e 's/^    return _candidate_tiles(points, sheet_bounds)$/    return _candidate_tiles(points, gdf_bounds)/' -e 's/^    del sheet, gdf_bounds  # unused by the D73 (2) rule; see the docstring$/    del sheet/' "$LIB"
grep -n '^    del sheet$' "$LIB"
grep -n '^    return _candidate_tiles(points, gdf_bounds)$' "$LIB"
run
cp "$DEST/lib.orig" "$LIB"; rm "$DEST/lib.orig"
echo "== restored: diff against the branch"
diff -r "$SRC/scripts" "$DEST/scripts" -x __pycache__ && diff -r "$SRC/tests" "$DEST/tests" -x __pycache__ && echo "IDENTICAL"
run
