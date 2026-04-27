#!/bin/bash
# Phase 3a MCC re-evaluation sweep driver.
# =========================================
#
# Re-evaluates the 252 phase3a matrix cells (text + image, excluding the
# 2 with-mcc reference cells) with --mcc, now that the bdd61bcc fix
# renders MCC into evaluation.md and evaluation.csv.
#
# Reads jobs.tsv (built by scripts/build_phase3a_mcc_jobs.py) with three
# tab-separated columns: detections_geojson, output_dir, label.
#
# Parallelism via xargs -P (GNU parallel is not installed on sapphire).
# Each line of jobs.tsv is fed to a worker that calls evaluate_detections.py.
#
# Usage:
#   bash scripts/run_phase3a_mcc_sweep.sh <jobs.tsv> <workers> [logfile]
#
# Example (in tmux):
#   bash scripts/run_phase3a_mcc_sweep.sh /tmp/jobs.tsv 8 /tmp/phase3a-mcc.log

set -uo pipefail

if [ $# -lt 2 ]; then
    echo "usage: $0 <jobs.tsv> <workers> [logfile]" >&2
    exit 2
fi

JOBS_TSV="$1"
WORKERS="$2"
LOGFILE="${3:-/tmp/phase3a-mcc.log}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON=".venv/bin/python"
EVAL="scripts/evaluate_detections.py"
BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
GT="inputs/vectors/references/mounds-reference.geojson"

export PYTHONUNBUFFERED=1

run_one() {
    # Reads "geojson<TAB>outdir<TAB>label" via $1 and runs evaluate_detections.
    # Writes one log line per job: "<status>\t<exit>\t<label>\t<elapsed>"
    local line="$1"
    local geojson outdir label
    IFS=$'\t' read -r geojson outdir label <<<"$line"

    local start=$(date +%s)
    mkdir -p "$outdir"

    "$PYTHON" "$EVAL" \
        --detections "$geojson" \
        --buffers 20 30 40 50 \
        --bootstrap 1000 \
        --seed 42 \
        --bounds "$BOUNDS" \
        --ground-truth "$GT" \
        --output-dir "$outdir" \
        --label "$label" \
        --mcc \
        > "$outdir/run.log" 2>&1
    local rc=$?
    local elapsed=$(($(date +%s) - start))

    if [ $rc -eq 0 ]; then
        printf 'OK\t%d\t%s\t%ds\n' "$rc" "$label" "$elapsed"
    else
        printf 'FAIL\t%d\t%s\t%ds\n' "$rc" "$label" "$elapsed"
    fi
}
export -f run_one
export PYTHON EVAL BOUNDS GT

echo "Phase 3a MCC sweep starting"
echo "  jobs:    $(wc -l < "$JOBS_TSV") (from $JOBS_TSV)"
echo "  workers: $WORKERS"
echo "  logfile: $LOGFILE"
echo "  start:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

# Stream stdin (one job per line) into xargs, which dispatches to bash -c
# wrappers running run_one. Output goes to LOGFILE plus stdout (tee).
< "$JOBS_TSV" xargs -d '\n' -P "$WORKERS" -I {} \
    bash -c 'run_one "$@"' _ {} 2>&1 | tee -a "$LOGFILE"

echo
echo "Phase 3a MCC sweep finished"
echo "  end: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
ok=$(grep -c '^OK' "$LOGFILE" || true)
fail=$(grep -c '^FAIL' "$LOGFILE" || true)
echo "  ok=$ok fail=$fail"
