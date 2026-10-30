#!/usr/bin/env bash
# =============================================================================
# kl_p2_run.sh -- K-ladder lane, part 2, in two independent clones (A then B)
# =============================================================================
# S164 restatement pass (reports/s164-agent-records/restatement-pass.md § 1.4,
# steps 2-4, 6-7 and the 3.7 opmax derivation of step 3). Each clone is a
# sparse git clone of 64382beea. One clone at a time, one interpreter at a
# time (this script plus one child). Every step's log and wall seconds are
# kept under p2/<R>/; a failing step stops that clone. The leg rule is the
# default (the re-verified rows); MAP_READER_VERIFY_DIRS is unset. No API.
#
# Usage: kl_p2_run.sh [inventory]   (the argument resumes both clones at the
# inventory refresh, restoring the inventory files to HEAD first)
# =============================================================================
FROM=${1:-start}
L=$HOME/scratch/s164-restate-2026-10-15/lane-kladder
P=$L/p2
PY=$HOME/Code/map-reader-llm/.venv/bin/python
echo $$ > "$L/logs/p2run.pid"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
unset MAP_READER_VERIFY_DIRS
K=results/k-ladder-2026-09-12
echo "before $(journalctl -k -b 2>/dev/null | grep -c 'Bad page state')" > "$P/bad-page.txt"

step() {  # step <name> <command...>: run in the clone, log, time, stop on failure
  local name=$1; shift
  local t0; t0=$(date +%s.%N)
  ( cd "$C" && "$@" ) > "$O/$name.log" 2>&1
  local rc=$?
  printf '%s\t%s\t%s\n' "$name" "$rc" "$(echo "$(date +%s.%N) - $t0" | bc)" >> "$O/times.tsv"
  if [ "$rc" -ne 0 ]; then echo "FAILED $name" > "$O/state"; return 1; fi
}

head_steps() {
  # 1. The five board-frame cells, each with its recorded arguments.
  "$PY" "$P/tools/kl_p2_cmds.py" "$C" > "$O/cmds.tsv" || { echo "FAILED cmds" > "$O/state"; return 1; }
  ok=1
  while IFS=$'\t' read -r cell argv; do
    mapfile -t ARGS < <(printf '%s' "$argv" | "$PY" -c 'import json,sys; print("\n".join(json.load(sys.stdin)))')
    step "eval-$(basename "$cell")" "$PY" scripts/evaluate_detections.py "${ARGS[@]}" || { ok=0; break; }
  done < "$O/cmds.tsv"
  [ "$ok" = 1 ] || return 1
  step tier-e-collect "$PY" scripts/run_k_ladder_tier_e.py collect || return 1
  step tier-e-tiering "$PY" scripts/tier_e_ladder_tiering.py || return 1
  step phase2-collect "$PY" scripts/score_k_ladder_phase2_rungs.py collect || return 1
  # 2. The 3.7 opmax derivation (fixed script, 1608a7604), REPAIRED reading.
  step g37-prepare "$PY" scripts/derive_g37_gs_opmax_rungs.py prepare --clip-to-common-area || return 1
  ok=1; n=0
  while read -r line; do
    [ -z "$line" ] && continue; n=$((n+1))
    mapfile -t ARGS < <(printf '%s' "${line#python scripts/evaluate_detections.py }" | tr ' ' '\n')
    step "g37-job-$n" "$PY" scripts/evaluate_detections.py "${ARGS[@]}" || { ok=0; break; }
  done < "$C/$K/phase2/g37-opmax-jobs.txt"
  [ "$ok" = 1 ] || return 1
  step g37-collect "$PY" scripts/derive_g37_gs_opmax_rungs.py collect || return 1
}

tail_steps() {
  # 3. The inventory's values (membership kept), then the Phase 1 tables.
  git -C "$C" show "HEAD:$K/inventory.json" > "$O/inventory-committed.json"
  step inventory-refresh "$PY" "$L/p1/tools/kl_inventory_refresh.py" --code . --data . \
      --inventory "$O/inventory-committed.json" --out-dir "$O/inventory" || return 1
  cp "$O/inventory/inventory.json" "$O/inventory/inventory-tables.md" "$C/$K/"
  step phase1-tables "$PY" scripts/build_k_ladder_tables.py || return 1
  # 4. GS stride A: the findings § 6.1 tiering, then the MCC test (spliced).
  step gs-tiering-61 "$PY" scripts/era1_leaderboard_tiering.py \
      --analysis-id k-ladder-gs-stride-a-2026-09-12 \
      --conditions "$K/tiering-input/gs-stride-a/run-conditions.json" \
      --analyses "$K/tiering-input/gs-stride-a/run-analyses.json" \
      --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \
      --permute-mcc --output-dir "$K/mcc-test/tiering/gs-stride-a" || return 1
  rm -rf "$O/gs-tiering-61"; cp -r "$C/$K/mcc-test/tiering/gs-stride-a" "$O/gs-tiering-61"
  git -C "$C" show "HEAD:$K/mcc-test/summary.json" > "$O/mcc-summary-committed.json"
  step mcc-test "$PY" scripts/k_ladder_mcc_test.py --only gs-stride-a || return 1
  cp "$C/$K/mcc-test/summary.json" "$O/mcc-summary-rerun.json"
  step mcc-splice "$PY" "$P/tools/kl_splice.py" mcc . "$O/mcc-summary-committed.json" \
      "$O/mcc-summary-rerun.json" "$K/mcc-test/summary.json" || return 1
  # 5. The two-ladder MCB (spliced).
  git -C "$C" show "HEAD:$K/mcb/summary.json" > "$O/mcb-summary-committed.json"
  step mcb "$PY" scripts/k_ladder_mcb.py --only gs-stride-a --only tier-e || return 1
  cp "$C/$K/mcb/summary.json" "$O/mcb-summary-rerun.json"
  cp "$C/$K/mcb/table.md" "$O/mcb-table-rerun.md"
  step mcb-splice "$PY" "$P/tools/kl_splice.py" mcb . "$O/mcb-summary-committed.json" \
      "$O/mcb-summary-rerun.json" "$K/mcb" || return 1
  # 6. The tension analyses that read moved inputs.
  step tension "$PY" scripts/k_ladder_tension_analyses.py --grid-overlap --effect-sizes || return 1
}

for R in A B; do
  C=$P/c$R; O=$P/$R; mkdir -p "$O"; echo RUNNING > "$O/state"
  if [ "$FROM" = inventory ]; then
    git -C "$C" checkout -- "$K/inventory.json" "$K/inventory-tables.md"
  else
    : > "$O/times.tsv"
    head_steps || continue
  fi
  tail_steps || continue
  echo DONE > "$O/state"
done
echo "after $(journalctl -k -b 2>/dev/null | grep -c 'Bad page state')" >> "$P/bad-page.txt"
echo DONE > "$P/state"
