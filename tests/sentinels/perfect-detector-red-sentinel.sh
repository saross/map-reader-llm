#!/usr/bin/env bash
# ============================================================================
# perfect-detector-red-sentinel.sh
# ----------------------------------------------------------------------------
# Red sentinel for tests/test_perfect_detector.py and
# tests/test_tile_join_wave1_audit.py (tile-join Wave 1, W1.2;
# planning/tile-join-wave-1-spec-2026-11-01.md). In a REAL-FILE copy (cp -r,
# never symlinks: docs/agent-guidance.md, "Mutation harnesses") of scripts/
# and tests/, with the inputs the real-frame fixtures read:
#   1. set the classification default back to id;
#   2. remove the sheet restriction (frame-wide candidates in
#      sheet_join_candidate_tiles);
#   3. book sheet-primary to the LAST candidate instead of the nearest
#      centre (G1 audit, lens B);
# each mutation must turn at least one test red. The copy is then restored,
# its sources must diff identical to the branch, and the tests must be as
# green as at baseline. The script FAILS (non-zero exit) on any deviation:
# a baseline that is not all-pass, a mutation that leaves everything green,
# an edit that does not apply, or a restored copy that differs.
#
# Not a pytest module: run it by hand, in a scratch directory, never in a
# checkout.
#
# Usage: bash tests/sentinels/perfect-detector-red-sentinel.sh SRC DEST
#   SRC  a checkout of the branch; DEST  a scratch directory (replaced).
# ============================================================================
set -euo pipefail
SRC=$1; DEST=$2; PY=$HOME/Code/map-reader-llm/.venv/bin/python
TESTS="tests/test_perfect_detector.py tests/test_tile_join_wave1_audit.py"
fail() { echo "SENTINEL FAILED: $*"; exit 1; }

rm -rf "$DEST"; mkdir -p "$DEST/inputs"
cp -r "$SRC/scripts" "$SRC/tests" "$SRC/results" "$SRC/data" "$SRC/configs" "$DEST/"
cp -r "$SRC/inputs/vectors" "$DEST/inputs/"
cp "$SRC/pytest.ini" "$SRC/ruff.toml" "$SRC/config.py" "$DEST/"
[ "$(find "$DEST" -type l | wc -l)" -eq 0 ] || fail "symlinks in the copy"
LIB="$DEST/scripts/lib_advanced_metrics.py"
cp "$LIB" "$DEST/lib.orig"

# Prints "<passed> <failed>" for one run of the tests in the copy.
counts() {
    local out
    out=$(cd "$DEST" && $PY -m pytest $TESTS -q -p no:cacheprovider 2>&1 | tail -n 1) || true
    echo "$out" >&2
    local p f
    p=$(echo "$out" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo 0)
    f=$(echo "$out" | grep -oE '[0-9]+ (failed|error)' | grep -oE '[0-9]+' | paste -sd+ | bc || echo 0)
    echo "$p ${f:-0}"
}
mutate() {  # file, old, new: the edit must apply exactly once
    "$PY" - "$1" "$2" "$3" <<'PYEOF'
import sys
path, old, new = sys.argv[1:]
text = open(path).read()
if text.count(old) != 1:
    sys.exit(f"edit applies {text.count(old)} times: {old[:60]!r}")
open(path, "w").write(text.replace(old, new))
PYEOF
}

echo "== baseline in copy"
read -r BASE_P BASE_F < <(counts)
[ "$BASE_F" -eq 0 ] && [ "$BASE_P" -gt 0 ] || fail "baseline not all-pass ($BASE_P/$BASE_F)"

run_mutation() {  # name, old, new
    echo "== mutation: $1"
    mutate "$LIB" "$2" "$3" || fail "$1: edit did not apply"
    read -r P F < <(counts)
    [ "$F" -gt 0 ] || fail "$1 left every test green ($P passed)"
    echo "   red: $F failed, $P passed"
    cp "$DEST/lib.orig" "$LIB"
}
run_mutation "classification default back to id" \
    "TILE_JOIN_CLASSIFICATION_DEFAULT: str = TILE_JOIN_SHEET_CONTAINS" \
    "TILE_JOIN_CLASSIFICATION_DEFAULT: str = TILE_JOIN_ID"
run_mutation "sheet restriction removed" \
    "    del sheet, gdf_bounds  # unused by the D73 (2) rule; see the docstring
    return _candidate_tiles(points, sheet_bounds)" \
    "    del sheet
    return _candidate_tiles(points, gdf_bounds)"
run_mutation "sheet-primary books the last candidate" \
    "out.append(min(names, key=lambda t: (geom.distance(centroids[t]), t)))" \
    "out.append(names[-1])"

rm "$DEST/lib.orig"
echo "== restored"
diff -r "$SRC/scripts" "$DEST/scripts" -x __pycache__ >/dev/null || fail "scripts differ"
diff -r "$SRC/tests" "$DEST/tests" -x __pycache__ >/dev/null || fail "tests differ"
read -r P F < <(counts)
[ "$P" -eq "$BASE_P" ] && [ "$F" -eq 0 ] || fail "restored copy gives $P/$F, baseline $BASE_P/0"
echo "SENTINEL PASSED: baseline $BASE_P passed; every mutation red; restored identical"
