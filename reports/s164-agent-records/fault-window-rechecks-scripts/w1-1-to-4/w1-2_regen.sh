#!/usr/bin/env bash
# W1-2 replay (fault-window re-check, Session 164). Re-runs the nine retest
# phase evaluations (d42_regen.sh group 2) in place in the replay tree at
# 7aef6d2ff, two processes at a time, then the annotator (w1-2_annotate.py,
# a copy of retest_annotate.py whose only change is the summary path). The
# annotator reads the regenerated working-tree files and the committed HEAD
# (7aef6d2ff) versions, exactly as on 2026-10-05 07:15Z. PYTHONHASHSEED is
# left unset, as in the original runner.
set -u
T=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-1-to-4-7aef6d2ff
O=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-1-to-4-out/w1-2${RUN_TAG:-}
S=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w1-1-to-4
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export PYTHONPATH=$S/netguard
cd "$T" || exit 1
[ "$(git rev-parse HEAD)" = 7aef6d2ffde8a287d55a18b1dbfc28eb2361b6da ] || { echo "wrong HEAD"; exit 1; }
mkdir -p "$O"; : > "$O/status.tsv"
step() {  # step <name> <command...>
    local name=$1; shift
    local t0=$(date +%s)
    "$@" > "$O/${name}.log" 2>&1 < /dev/null
    local rc=$?
    printf '%s\t%s\t%ss\n' "$name" "$rc" "$(( $(date +%s) - t0 ))" >> "$O/status.tsv"
}
declare -A RETEST=(
  [phase2a]=phase2a-evaluation.json
  [phase2b-track1-image]=phase2b-track1-evaluation.json
  [phase2b-track2-text]=phase2b-track2-evaluation.json
  [phase2c-track1-image-exploratory]=phase2c-exploratory-evaluation.json
  [phase2c-track1-image]=phase2c-track1-evaluation.json
  [phase2c-track2-text]=phase2c-track2-evaluation.json
  [phase2d-track1-image]=phase2d-track1-evaluation.json
  [phase2d-track2-text]=phase2d-track2-evaluation.json
  [phase2e]=phase2e-evaluation.json
)
for key in "${!RETEST[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge 2 ]; do wait -n; done
  step "retest-${key}" "$PY" scripts/evaluate_retest_all.py --phase "$key" \
      --output "results/retest/${RETEST[$key]}" &
done
wait
# Keep the regenerated (pre-annotation) files for the record.
mkdir -p "$O/regenerated"; cp results/retest/phase2*-evaluation.json "$O/regenerated/"
step annotate "$PY" "$S/w1-2_annotate.py" "$O/retest_annotation_summary.json"
echo ALL-DONE >> "$O/status.tsv"
