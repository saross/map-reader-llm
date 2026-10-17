#!/usr/bin/env bash
# =============================================================================
# kl_derive_run.sh -- run the patched 3.7 opmax derivation on real data, twice
# =============================================================================
# K-ladder lane, S164 restatement pass, part 1 step 1 (verification of the
# patch). In harness hG (default leg rule: the re-verified rows) and then
# harness hF (MAP_READER_VERIFY_DIRS=fixed: the legs as run): `prepare
# --clip-to-common-area`, the two evaluation jobs it writes, and `collect`.
# One harness at a time (this script plus one interpreter). No API calls.
# =============================================================================
P=$HOME/scratch/s164-restate-2026-10-15/lane-kladder/p1
PY=$HOME/Code/map-reader-llm/.venv/bin/python
echo $$ > "$P/../logs/derive.pid"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
for H in G F; do
  cd "$P/h$H" || exit 9
  if [ "$H" = F ]; then export MAP_READER_VERIFY_DIRS=fixed; else unset MAP_READER_VERIFY_DIRS; fi
  t0=$(date +%s)
  "$PY" scripts/derive_g37_gs_opmax_rungs.py prepare --clip-to-common-area > "$P/derive-$H-prepare.log" 2>&1
  rc=$?
  echo "prepare rc=$rc $(( $(date +%s) - t0 )) s" > "$P/derive-$H-status.txt"
  if [ "$rc" -ne 0 ]; then echo "STOPPED: prepare failed" >> "$P/derive-$H-status.txt"; echo FAILED > "$P/derive-state"; exit 1; fi
  t1=$(date +%s)
  while read -r line; do
    [ -z "$line" ] && continue
    eval "\"$PY\" ${line#python }" >> "$P/derive-$H-jobs.log" 2>&1 || echo "JOB FAILED: $line" >> "$P/derive-$H-status.txt"
  done < results/k-ladder-2026-09-12/phase2/g37-opmax-jobs.txt
  echo "jobs $(( $(date +%s) - t1 )) s" >> "$P/derive-$H-status.txt"
  "$PY" scripts/derive_g37_gs_opmax_rungs.py collect > "$P/derive-$H-collect.log" 2>&1
  echo "collect rc=$?" >> "$P/derive-$H-status.txt"
done
echo DONE > "$P/derive-state"
