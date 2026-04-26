#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# build_combined_tier_stability.sh
# ---------------------------------------------------------------------------
# Run scripts/build_tier_stability.py over a combined / cross-architecture
# leaderboard directory. The stability script expects per-arch native naming
# (leaderboard_tiers_<B>m.json, leaderboard_tiers_mcc_<B>m.json), but the
# combined dirs use the explicit-metric naming
# (leaderboard_tiers_f1_<B>m.json, leaderboard_tiers_mcc.json).
#
# Strategy: create temporary symlinks in the combined dir mapping the
# stability script's expected names to the actual files, run the stability
# build, then remove the symlinks.
#
# Usage:
#   bash scripts/build_combined_tier_stability.sh <era>
# ---------------------------------------------------------------------------

set -euo pipefail

ERA="${1:?usage: $0 <era>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON="${REPO_ROOT}/.venv/bin/python"
DIR="${REPO_ROOT}/results/leaderboard/combined/era${ERA}"
[[ -d "$DIR" ]] || { echo "missing $DIR" >&2; exit 2; }

BUFFERS=(20 30 40 50 100)

# Track created symlinks so we can clean up (and not delete real files).
created_links=()
trap 'for l in "${created_links[@]}"; do [[ -L "$l" ]] && rm -f "$l"; done' EXIT

# F1: leaderboard_tiers_<B>m.json -> leaderboard_tiers_f1_<B>m.json
for B in "${BUFFERS[@]}" ; do
    src="leaderboard_tiers_f1_${B}m.json"
    link="${DIR}/leaderboard_tiers_${B}m.json"
    if [[ -f "${DIR}/${src}" && ! -e "$link" ]]; then
        ln -s "$src" "$link"
        created_links+=("$link")
    fi
done

# MCC: leaderboard_tiers_mcc_<B>m.json -> leaderboard_tiers_mcc.json (single)
for B in "${BUFFERS[@]}" ; do
    link="${DIR}/leaderboard_tiers_mcc_${B}m.json"
    if [[ -f "${DIR}/leaderboard_tiers_mcc.json" && ! -e "$link" ]]; then
        ln -s "leaderboard_tiers_mcc.json" "$link"
        created_links+=("$link")
    fi
done

echo "Created ${#created_links[@]} temporary symlinks"

"$PYTHON" scripts/build_tier_stability.py --metric f1 --stratum-dir "$DIR"
"$PYTHON" scripts/build_tier_stability.py --metric mcc --stratum-dir "$DIR"

echo "Stability tables built in $DIR"
ls "$DIR" | grep '^tier_stability'
