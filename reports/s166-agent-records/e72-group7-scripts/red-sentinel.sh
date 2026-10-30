#!/usr/bin/env bash
# ============================================================================
# red-sentinel.sh — run the E72 regeneration tests against a chosen script
# ----------------------------------------------------------------------------
# Copies scripts/, the two regen_e43_board test modules, tests/conftest.py,
# config.py and pytest.ini into a fresh harness as REAL files (never links: the
# tests resolve sys.path through Path(__file__).resolve(), which would follow a
# link back into the checkout), swaps in the script under test, and runs the
# tier-1 tests. Run it once with the 2026-08-02 script (expect the new tests
# red) and once with the adapted one (expect green).
#
# Usage (from a checkout of the branch):
#   git show 2f3ef020a:scripts/regen_e43_board.py > /tmp/old.py
#   reports/s166-agent-records/e72-group7-scripts/red-sentinel.sh <harness> /tmp/old.py <python>
# ============================================================================
set -euo pipefail
repo=$(git rev-parse --show-toplevel)
harness=$1
script=$2
python=${3:-python}

rm -rf "$harness"
mkdir -p "$harness/tests"
cp -r "$repo/scripts" "$harness/scripts"
cp "$script" "$harness/scripts/regen_e43_board.py"
cp "$repo/config.py" "$repo/pytest.ini" "$harness/"
cp "$repo/tests/__init__.py" "$repo/tests/conftest.py" \
    "$repo/tests/test_regen_e43_board.py" \
    "$repo/tests/test_regen_e43_board_restated_layout.py" "$harness/tests/"
test "$(find "$harness" -type l | wc -l)" -eq 0
cd "$harness"
"$python" -m pytest -m tier1 -q -p no:cacheprovider --tb=line \
    tests/test_regen_e43_board_restated_layout.py tests/test_regen_e43_board.py
