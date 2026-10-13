#!/usr/bin/env bash
# stage1013.sh -- copy run 1's regenerated W2.7 outputs (and the logs of
# runs 1 and 2 and the integrity re-check) into the clone at the paths the
# 2026-10-12 run committed, plus the drivers and comparisons into
# floors-v2/regen-2026-10-13/. Files whose content equals the committed
# file are copied too, so git shows only what changed. The gzipped
# sim_cells.csv.gz and gs_slice_cells.csv.gz are left alone: their
# decompressed contents were compared with run 1's CSVs and are identical.
set -euo pipefail
S=/home/shawn/scratch/d60-w27-fastscorer-2026-10-12
W=$S/repo/reports/w27-replicate-floors-2026-10-06-scripts
F=$W/floors-v2
R1=$S/out/1013-r1
L1=$S/logs/1013-r1
L2=$S/logs/1013-r2
RG=$F/regen-2026-10-13
PAT="Assigned source_tile to .* detections via spatial join"

filter_gs() {
  # filter_gs <raw gs log> <dest>: drop the per-frame INFO lines, as on 2026-10-12.
  local n
  n=$(grep -c "$PAT" "$1" || true)
  {
    echo "[filtered: $n INFO lines 'Assigned source_tile to N/N detections via spatial join' removed]"
    grep -v "$PAT" "$1" || true
  } > "$2"
}

# § 6 (byte-identical to the committed files; logs replaced)
cp "$R1"/w27/{subset_cells.json,subset_pairs.csv,gates.json,verifier_provenance.json} "$W/"
cp "$L1/s6.log" "$W/map55_run.log"
cp "$L2/s6.log" "$W/map55_run2.log"

# floors-v2 results
cp "$R1/gate/scorer_gate.json" "$R1/gate/scorer_gate_cells.csv" "$F/results/"
cp "$R1/out55/subset_cells_all.csv" "$F/results/subset_cells_all.csv"
cp "$R1/out55/gates.json" "$F/results/gates55.json"
cp "$R1/outgs/gates.json" "$F/results/gates_gs.json"
for n in cell_sds.csv extrapolation55.csv floors55_all.csv gs_k10_check.csv gs_k10_summary.csv \
         gs_validation.csv gs_validation_summary.csv nested_rung55.csv nested_threshold55.csv \
         propensity55.csv rescreen.csv results.json tables.md; do
  cp "$R1/results/$n" "$F/results/$n"
done
cp "$S/out/1013-recheck/integrity_recheck.json" "$F/results/integrity_recheck.json"

# floors-v2 logs
cp "$L1/gate.log" "$F/logs/scorer_gate.log"
cp "$L1/s6b.log" "$F/logs/run55.log"
filter_gs "$L1/gs.log" "$F/logs/gs_run.log"
cp "$L1/analysis.log" "$F/logs/analysis.log"
cp "$R1/rescreen.out" "$F/logs/rescreen.out"
cp "$S/logs/1013-recheck/recheck.log" "$F/logs/integrity_recheck.log"

# drivers, comparisons and run 2's own stage logs
mkdir -p "$RG/logs-r2"
cp "$S/tools/regen1013.sh" "$S/tools/run-recheck.sh" "$S/tools/cmp1013.py" \
   "$S/tools/floors_moved.py" "$S/tools/import_closure.py" "$S/tools/stage1013.sh" "$RG/"
cp "$S/out/1013-cmp/r1-vs-committed.json" "$RG/r1-vs-pr38-committed.json"
cp "$S/out/1013-cmp/r1-vs-pr44r1.json" "$RG/r1-vs-pr44-r1.json"
cp "$S/out/1013-cmp/r1-vs-r2.json" "$RG/r1-vs-r2.json"
cp "$S/out/1013-cmp/floors-moved.txt" "$S/out/1013-cmp/import-closure.txt" \
   "$S/out/1013-cmp/kernel-bad-page.txt" "$RG/"
cp "$L2/gate.log" "$L2/s6b.log" "$L2/analysis.log" "$RG/logs-r2/"
filter_gs "$L2/gs.log" "$RG/logs-r2/gs.log"
echo staged
