#!/usr/bin/env bash
# =============================================================================
# red_sentinel.sh — prove the D50 and D51 tests bite (2026-10-08, Session 163)
# -----------------------------------------------------------------------------
# Builds a REAL copy of the branch head (git archive; no symlinks, so no test
# module can resolve its imports back into the worktree — the failure mode of
# the 2026-09-20 mutation harness), runs the D50/D51 tests green, then breaks
# each rule once in the copy and confirms tests turn red, restoring the file
# after each break:
#
#   1. D50: the geometric scope disabled (every attributed detection kept,
#      i.e. the pre-ruling name-prefix behaviour);
#   2. D51: the area refusal disabled (no comparison ever mismatches).
#
# The two ladder-builder wiring tests are deselected in the copy because the
# builder module computes the whole passes register at import, which reads
# per-pass artefacts across outputs/; they pass in the full worktree.
#
# Usage (on sapphire):
#   bash red_sentinel.sh ~/worktrees/map-reader-llm/claude-scorer-d50 SCRATCH_DIR
# =============================================================================
set -euo pipefail

WORKTREE="$1"
COPY="$2/sentinel"
PY="$HOME/Code/map-reader-llm/.venv/bin/python"
TESTS=(tests/test_detection_scope.py tests/test_assessed_area.py)

rm -rf "$COPY" && mkdir -p "$COPY"
git -C "$WORKTREE" archive HEAD scripts tests pytest.ini data config.py \
    results/passes-manifest.json | tar -x -C "$COPY"
git -C "$WORKTREE" archive HEAD -- ":(glob)outputs/**/*.meta.json" \
    ":(glob)outputs/**/*.cost_audit.json" ":(glob)outputs/**/run.meta.json" \
    | tar -x -C "$COPY"
echo "head $(git -C "$WORKTREE" rev-parse --short HEAD); symlinks in copy: $(find "$COPY" -type l | wc -l)"
cd "$COPY"

run() {
    PYTHONDONTWRITEBYTECODE=1 "$PY" -m pytest -p no:cacheprovider -q \
        -k "not ladder_builder" "${TESTS[@]}" 2>&1 | grep -E "^FAILED|passed|failed" \
        | sed "s/ - .*//" || true
}

echo "== green control"; run

echo "== sentinel 1: D50 scope disabled"
cp scripts/lib_advanced_metrics.py /tmp/lam_ok.py
sed -i "s/^        if sheet in sheets_hit\[pos\]:/        if True:  # RED SENTINEL/" \
    scripts/lib_advanced_metrics.py
grep -n "RED SENTINEL" scripts/lib_advanced_metrics.py
run
cp /tmp/lam_ok.py scripts/lib_advanced_metrics.py && rm /tmp/lam_ok.py
echo "== restored"; run

echo "== sentinel 2: D51 refusal disabled"
cp scripts/lib_assessed_area.py /tmp/laa_ok.py
sed -i "s/^    mismatch = worst > tolerance_km2/    mismatch = False  # RED SENTINEL/" \
    scripts/lib_assessed_area.py
grep -n "RED SENTINEL" scripts/lib_assessed_area.py
run
cp /tmp/laa_ok.py scripts/lib_assessed_area.py && rm /tmp/laa_ok.py
echo "== restored"; run
