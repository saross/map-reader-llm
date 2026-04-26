#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# build_combined_leaderboard.sh
# ---------------------------------------------------------------------------
# Build the combined / cross-architecture leaderboard for one Era. Pools all
# conditions from every architecture (single-pass, consensus, single-pass+PV,
# pv) into a single greedy-clique BH-FDR-tiered ranking, separately at each
# (buffer, metric, q-level) combination.
#
# Cache reuse: hardlinks the per-architecture .cache/{evaluations,pairwise_*}
# directories from results/leaderboard/per-architecture/era<N>/<arch>/.cache/
# into the combined cache dir at results/leaderboard/combined/era<N>/.cache/.
# Within-architecture pairs are hit from cache; only cross-architecture pairs
# are computed fresh.
#
# Output convention (combined): leaderboard_tiers_f1_<B>m.{md,json},
# leaderboard_tiers_f1_q01_<B>m.{md,json}, leaderboard_tiers_mcc.{md,json},
# leaderboard_tiers_mcc_q01.{md,json}. Files are renamed after generation
# from the script's native naming (leaderboard_tiers_<B>m.md, etc.) to add
# the explicit `_f1_` infix and to collapse the per-buffer MCC copies.
#
# Usage:
#   bash scripts/build_combined_leaderboard.sh <era>
#
# Requires: cache dirs already populated at
#   results/leaderboard/per-architecture/era<N>/<arch>/.cache/
# (run scripts/run_per_arch_leaderboards.sh first, plus the per-buffer F1
# rebuild for non-20m buffers).
#
# Run on sapphire. Estimated wall-clock per Era: 30-60 minutes (Era 1 = 1,512
# new cross-arch pairs x 5 buffers + 1 MCC; Era 2 = 2,346 new pairs x same).
# ---------------------------------------------------------------------------

set -euo pipefail

ERA="${1:?usage: $0 <era>}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON="${REPO_ROOT}/.venv/bin/python"
INVENTORY="${REPO_ROOT}/planning/condition-inventory-with-s78.json"
SCRIPT="${REPO_ROOT}/scripts/build_tiered_leaderboard.py"
PER_ARCH_ROOT="${REPO_ROOT}/results/leaderboard/per-architecture/era${ERA}"
OUT_DIR="${REPO_ROOT}/results/leaderboard/combined/era${ERA}"
CACHE_DIR="${OUT_DIR}/.cache"
LOG_DIR="${REPO_ROOT}/logs/combined-leaderboard/era${ERA}"

mkdir -p "$OUT_DIR" "$CACHE_DIR/evaluations" "$LOG_DIR"
mkdir -p "$CACHE_DIR/pairwise" "$CACHE_DIR/pairwise_mcc"
for B in 20 30 40 50 100 ; do
    mkdir -p "$CACHE_DIR/pairwise_f1_${B}m"
done

# Per-Era settings
case "$ERA" in
    1)
        BOUNDS="${REPO_ROOT}/inputs/vectors/bounds/full_evaluation_bounds.geojson"
        STATUS_ARGS=(--status READY SINGLE_PASS_ONLY)
        ARCHS=(consensus single-pass)
        ;;
    2)
        BOUNDS="${REPO_ROOT}/inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
        STATUS_ARGS=(--status READY SINGLE_PASS_ONLY PV_READY)
        ARCHS=(consensus single-pass single-pass+PV pv)
        ;;
    *)
        echo "Era $ERA not supported by this driver (Era 3 handled by symlink/copy)" >&2
        exit 2
        ;;
esac

BUFFERS="20 30 40 50 100"
BUFFER_LIST=(20 30 40 50 100)
WORKERS=8
BOOTSTRAP=1000
N_PERM=10000
SEED=42

# ---------------------------------------------------------------------------
# Stage A: seed cache via hardlinks from per-architecture caches.
# Hardlinks (not symlinks) so the combined .cache directory is self-contained
# and survives if the per-arch caches are later moved. Hardlinks share inodes,
# so disk usage is unchanged.
# ---------------------------------------------------------------------------
echo "[$(date -u +%H:%M:%S)] Era ${ERA}: seeding cache from per-architecture caches"
for arch in "${ARCHS[@]}"; do
    src_cache="${PER_ARCH_ROOT}/${arch}/.cache"
    if [[ ! -d "$src_cache" ]]; then
        echo "  WARNING: missing per-arch cache: $src_cache" >&2
        continue
    fi
    # Evaluations: per-condition subdirs (label/<t>_<B>m.json).
    for cond_dir in "$src_cache/evaluations"/*/; do
        [[ -d "$cond_dir" ]] || continue
        label="$(basename "$cond_dir")"
        dst="${CACHE_DIR}/evaluations/${label}"
        mkdir -p "$dst"
        for f in "$cond_dir"/*.json ; do
            [[ -f "$f" ]] || continue
            ln -f "$f" "$dst/$(basename "$f")" 2>/dev/null || cp -f "$f" "$dst/$(basename "$f")"
        done
    done
    # Pairwise: legacy 20m layout (pairwise/<a>_vs_<b>.json),
    # per-buffer F1 layout (pairwise_f1_<B>m/<a>_vs_<b>.json),
    # MCC layout (pairwise_mcc/<a>_vs_<b>.json).
    for sub in pairwise pairwise_mcc pairwise_f1_20m pairwise_f1_30m \
                 pairwise_f1_40m pairwise_f1_50m pairwise_f1_100m ; do
        src_sub="${src_cache}/${sub}"
        [[ -d "$src_sub" ]] || continue
        for f in "$src_sub"/*.json ; do
            [[ -f "$f" ]] || continue
            ln -f "$f" "${CACHE_DIR}/${sub}/$(basename "$f")" 2>/dev/null || cp -f "$f" "${CACHE_DIR}/${sub}/$(basename "$f")"
        done
    done
done
echo "  cache seeded: $(find "$CACHE_DIR" -name '*.json' | wc -l) files"

# ---------------------------------------------------------------------------
# Stage B: F1 runs, one per primary buffer, q=0.05 then q=0.01.
#
# Each invocation passes --buffers "20 <primary>" — 20 m is needed for
# threshold selection (--threshold-buffer 20, Option A); the primary is
# needed for tier construction + display. The script writes one .md per
# buffer in --buffers, so up to 2 .md files are written: a stale 20m.md
# (showing primary-buffer tiering with 20m metric values) and a correct
# <primary>m.md. We immediately archive the correct file under the final
# combined name before the next pass overwrites it.
#
# The primary=20 case is special: --buffers 20 --primary-buffer 20 writes
# only the 20m.md file, which IS the correct primary=20 tiering.
# ---------------------------------------------------------------------------
run_f1_pass() {
    local buffer="$1"
    local fdr_q="$2"
    local extra=("${@:3}")

    local tag="era${ERA}-combined-f1-q$(echo "$fdr_q" | tr -d '.')-buf${buffer}m"
    local log_file="${LOG_DIR}/${tag}.log"

    # Buffer set: just the primary if primary=20 (no separate threshold
    # buffer needed), else "20 <primary>" so threshold selection has data.
    local buffers_arg
    if [[ "$buffer" == "20" ]]; then
        buffers_arg=("--buffers" "20")
    else
        buffers_arg=("--buffers" "20" "$buffer")
    fi

    echo "[$(date -u +%H:%M:%S)] $tag"
    "$PYTHON" "$SCRIPT" \
        --inventory "$INVENTORY" \
        --era "$ERA" \
        --bounds "$BOUNDS" \
        "${STATUS_ARGS[@]}" \
        "${buffers_arg[@]}" \
        --primary-buffer "$buffer" \
        --threshold-buffer 20 \
        --metric f1 \
        --fdr-q "$fdr_q" \
        --workers "$WORKERS" \
        --bootstrap "$BOOTSTRAP" \
        --n-permutations "$N_PERM" \
        --seed "$SEED" \
        --top-n 0 \
        --skip-evaluation \
        "${extra[@]}" \
        --output-dir "$OUT_DIR" \
        > "$log_file" 2>&1
    local rc=$?
    if [[ $rc -ne 0 ]]; then
        echo "    FAILED (rc=$rc, see $log_file)"
        return $rc
    fi

    # Preserve the correct .md (matching primary buffer) under the final
    # combined name. The 20m.md from a non-20m primary run is stale and
    # gets discarded on the next 20m primary run anyway.
    local q_suffix=""
    if [[ "$fdr_q" == "0.01" ]]; then
        q_suffix="_q01"
    fi
    local src_md="${OUT_DIR}/leaderboard_tiers${q_suffix}_${buffer}m.md"
    local src_json="${OUT_DIR}/leaderboard_tiers${q_suffix}_${buffer}m.json"
    local dst_md="${OUT_DIR}/leaderboard_tiers_f1${q_suffix}_${buffer}m.md"
    local dst_json="${OUT_DIR}/leaderboard_tiers_f1${q_suffix}_${buffer}m.json"
    if [[ -f "$src_md" ]]; then
        cp -f "$src_md" "$dst_md"
    fi
    if [[ -f "$src_json" ]]; then
        cp -f "$src_json" "$dst_json"
    fi

    echo "    OK -> $(basename "$dst_md")"
}

for B in "${BUFFER_LIST[@]}" ; do
    # Pass 1: q=0.05, computes pairwise at this buffer.
    run_f1_pass "$B" "0.05"
    # Pass 2: q=0.01, reuses pairwise cache.
    run_f1_pass "$B" "0.01" --skip-pairwise
done

# ---------------------------------------------------------------------------
# Stage C: MCC runs (buffer-independent — single primary buffer only).
# We use primary-buffer 20 by convention.
# ---------------------------------------------------------------------------
run_mcc_pass() {
    local fdr_q="$1"
    local extra=("${@:2}")
    local tag="era${ERA}-combined-mcc-q$(echo "$fdr_q" | tr -d '.')"
    local log_file="${LOG_DIR}/${tag}.log"

    echo "[$(date -u +%H:%M:%S)] $tag"
    "$PYTHON" "$SCRIPT" \
        --inventory "$INVENTORY" \
        --era "$ERA" \
        --bounds "$BOUNDS" \
        "${STATUS_ARGS[@]}" \
        --buffers 20 \
        --primary-buffer 20 \
        --threshold-buffer 20 \
        --metric mcc \
        --fdr-q "$fdr_q" \
        --workers "$WORKERS" \
        --bootstrap "$BOOTSTRAP" \
        --n-permutations "$N_PERM" \
        --seed "$SEED" \
        --top-n 0 \
        --skip-evaluation \
        "${extra[@]}" \
        --output-dir "$OUT_DIR" \
        > "$log_file" 2>&1
    local rc=$?
    if [[ $rc -eq 0 ]]; then
        echo "    OK"
    else
        echo "    FAILED (rc=$rc, see $log_file)"
        return $rc
    fi
}

run_mcc_pass "0.05"
run_mcc_pass "0.01" --skip-pairwise

# ---------------------------------------------------------------------------
# Stage D: clean up script-native filenames and finalise MCC names.
#
# F1: each pass already preserved its primary-buffer .md and .json under
# the combined name (leaderboard_tiers_f1_<B>m.{md,json}). The native-named
# files (leaderboard_tiers_<B>m.{md,json}) left behind are stale (they
# reflect the LAST primary's tiering rendered at each buffer) and must be
# removed to avoid confusion.
#
# MCC: the script's native filename is leaderboard_tiers_mcc_20m.{md,json}.
# Rename to the buffer-independent leaderboard_tiers_mcc.{md,json}.
# ---------------------------------------------------------------------------
echo "[$(date -u +%H:%M:%S)] Cleaning up native-named files and finalising MCC"
for B in "${BUFFER_LIST[@]}" ; do
    for ext in md json ; do
        rm -f "${OUT_DIR}/leaderboard_tiers_${B}m.${ext}" \
              "${OUT_DIR}/leaderboard_tiers_q01_${B}m.${ext}"
    done
done
for ext in md json ; do
    if [[ -f "${OUT_DIR}/leaderboard_tiers_mcc_20m.${ext}" ]]; then
        mv -f "${OUT_DIR}/leaderboard_tiers_mcc_20m.${ext}" \
              "${OUT_DIR}/leaderboard_tiers_mcc.${ext}"
    fi
    if [[ -f "${OUT_DIR}/leaderboard_tiers_mcc_q01_20m.${ext}" ]]; then
        mv -f "${OUT_DIR}/leaderboard_tiers_mcc_q01_20m.${ext}" \
              "${OUT_DIR}/leaderboard_tiers_mcc_q01.${ext}"
    fi
done

echo "[$(date -u +%H:%M:%S)] Era ${ERA} combined leaderboard build complete"
ls -la "$OUT_DIR" | grep -v '^total\|\.cache' | head -40
