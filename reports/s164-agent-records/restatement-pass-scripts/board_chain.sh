#!/usr/bin/env bash
# =============================================================================
# board_chain.sh — the Era-2 board lane of the restatement pass in one copy
# =============================================================================
# Part of the S164 restatement pass (reports/s164-agent-records/
# restatement-pass.md § 1.3). In a copy made by mkcopy_board.sh from a branch
# head that already holds the restated GS sets and the re-scored S9 K-ladder
# cells:
#   1. board_membership.py: the membership snapshot's F1 and the 3.7 image
#      carried arm's paths refreshed, membership kept;
#   2. build_gs_era2_board.py jobs, then the G2 and board-frame jobs of the
#      ten members downstream of the re-verified legs only (the other 93
#      reproduce; S9 sweep § 6);
#   3. build_gs_era2_board.py gates (gates.json, frame-deltas.md);
#   4. era1_leaderboard_tiering.py --permute-mcc (tiering_20m.json and .md);
#   5. selection_aware_intervals.py --board, F1 and tile-MCC (mcb/);
#   6. the twenty sweep-optimism runs (optimism/), then
#      summarise_sweep_optimism.py; the 3.7 image carried arm's board-frame
#      run takes no anchor gate, because under PI ruling D65 (3) its board
#      cell is its registered point, not the sweep's argmax;
#   7. build_gs_era2_board.py finalise --no-analysis-row (README.md,
#      provenance.json; the proposed outcome goes to provenance only).
# Single-threaded, one process at a time. Legs under the default rule.
#
# Usage: board_chain.sh <copy_dir> <log_dir>
# =============================================================================
set -uo pipefail
COPY=$1; LOGDIR=$2
PY=$HOME/Code/map-reader-llm/.venv/bin/python
TOOLS=$(cd "$(dirname "$0")" && pwd)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
unset MAP_READER_VERIFY_DIRS
mkdir -p "$LOGDIR"; echo $$ > "$LOGDIR/chain.pid"; echo RUNNING > "$LOGDIR/chain.state"
cd "$COPY" || exit 9
B=results/leaderboard/era2/gs-era2-verified-board-2026-09-10
ID=gs-era2-verified-board-2026-09-10
step() {
  local name=$1; shift
  echo "=== $(date -u +%FT%TZ) START $name"
  "$@" > "$LOGDIR/$name.log" 2>&1 < /dev/null
  local rc=$?
  echo "=== $(date -u +%FT%TZ) END $name rc=$rc"
  if [ $rc -ne 0 ]; then echo "CHAIN FAILED at $name"; echo "FAILED $name" > "$LOGDIR/chain.state"; exit $rc; fi
}
#: The ten members downstream of the re-verified legs (slugs).
MOVED="gemini37-image-gs-2026-09-01__g37-image-k5-verified-carried-p0_10-k5
gemini37-image-gs-2026-09-01__g37-image-k5-verified-swap37-p0_90-k5
gemini37-screen-2026-08-28__g37-text-k10-verified-carried-p0_10-k10
gemini37-screen-2026-08-28__g37-text-k5-verified-carried-p0_10-k5
gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5
gemini37-screen-2026-08-28__g37-text-k5-verified-swap38-p0_88-k5
grid-2026-08-18__g384-ov192-k10-verified37-p0_98-k10
grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10
image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8
image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9"
step membership "$PY" "$TOOLS/board_membership.py" "$COPY"
step jobs "$PY" scripts/build_gs_era2_board.py jobs
: > "$LOGDIR/moved-jobs.sh"
for s in $MOVED; do
  grep -E "^run python scripts/evaluate_detections.py .*--output-dir $B/(g2|cells)/$s( |$)" "$B/score-commands.sh" \
    | sed "s#^run python #\"$PY\" #" >> "$LOGDIR/moved-jobs.sh"
done
n=$(grep -c . "$LOGDIR/moved-jobs.sh"); echo "moved jobs: $n"
[ "$n" -eq 20 ] || { echo "expected 20 jobs, found $n"; echo "FAILED jobs-count" > "$LOGDIR/chain.state"; exit 3; }
step score bash "$LOGDIR/moved-jobs.sh"
step gates "$PY" scripts/build_gs_era2_board.py gates
step tiering "$PY" scripts/era1_leaderboard_tiering.py --analysis-id $ID \
  --analyses $B/tiering-input/run-analyses.json --permute-mcc --output-dir $B
for m in f1 mcc; do
  step "mcb_$m" "$PY" scripts/selection_aware_intervals.py --board $ID \
    --analyses $B/tiering-input/run-analyses.json --metric $m --bootstrap 10000 \
    --m-frac 1.0 --out $B/mcb
done
while IFS=$'\t' read -r stem union verify k bounds csv anchor; do
  extra=()
  # The committed-frame runs used the default bounds (grid-common), so they
  # are run the same way; the board-frame runs name the board frame.
  [ "$bounds" != DEFAULT ] && extra+=(--bounds "$bounds")
  [ "$csv" != None ] && extra+=(--sweep-csv "$csv")
  [ "$anchor" != None ] && extra+=(--sweep-anchor-eval "$anchor")
  step "opt_$stem" "$PY" scripts/selection_aware_intervals.py --sweep-union "$union" \
    --sweep-verify "$verify" --sweep-k "$k" --tag "$stem" \
    --bootstrap 10000 --m-frac 1.0 --out $B/optimism "${extra[@]}"
done < "$TOOLS/board_optimism_runs.tsv"
step opt_summary "$PY" scripts/summarise_sweep_optimism.py
step finalise "$PY" scripts/build_gs_era2_board.py finalise --no-analysis-row \
  --re-sign-reason "restatement pass 2026-10-15 (D65 (2)): ten members re-scored with the D62 (1) re-verified rows on PR #42's origin route, the S9 K-ladder cells re-scored under D50, and the 3.7 image carried arm kept at its registered point (D65 (3))"
echo "=== $(date -u +%FT%TZ) CHAIN DONE"; echo DONE > "$LOGDIR/chain.state"
