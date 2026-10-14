#!/usr/bin/env bash
# W1-3 replay (fault-window re-check, Session 164). The February 60-tile
# re-test (d42_regen.sh group 3 plus the in-session repair and re-run of
# 2026-10-05 07:04:47Z / 07:05:33Z) at 7aef6d2ff, on a fresh copy of
# archive/outputs-pre-retest-60-tile from the replay tree. Sequence as run:
# (1) all eight analyses on the unrepaired copy; (2) repair the copy only:
# suffix-free Phase 2b detection files get ".geojson", Phase 2e
# config-default run_* symlinks re-pointed at the copy's phase2c plus-hp
# runs; (3) re-run 2b-track1, 2b-track2, 2d-track2, 2e; (4) feb_compare.
# Two processes at a time. PYTHONHASHSEED is left unset, as originally.
set -u
T=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-1-to-4-7aef6d2ff
O=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-1-to-4-out/w1-3${RUN_TAG:-}
S=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w1-1-to-4
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export PYTHONPATH=$S/netguard
cd "$T" || exit 1
[ "$(git rev-parse HEAD)" = 7aef6d2ffde8a287d55a18b1dbfc28eb2361b6da ] || { echo "wrong HEAD"; exit 1; }
mkdir -p "$O/feb"; : > "$O/status.tsv"
step() {  # step <name> <command...>
    local name=$1; shift
    local t0=$(date +%s)
    "$@" > "$O/${name}.log" 2>&1 < /dev/null
    local rc=$?
    printf '%s\t%s\t%ss\n' "$name" "$rc" "$(( $(date +%s) - t0 ))" >> "$O/status.tsv"
}
F=$O/febdata
rm -rf "$F" && mkdir -p "$F"
cp -r archive/outputs-pre-retest-60-tile/phase2a archive/outputs-pre-retest-60-tile/phase2b \
      archive/outputs-pre-retest-60-tile/phase2c archive/outputs-pre-retest-60-tile/phase2d \
      archive/outputs-pre-retest-60-tile/phase2e "$F/"
feb() {  # feb <name> <study-dir> <conditions...>
    local name=$1 dir=$2; shift 2
    while [ "$(jobs -rp | wc -l)" -ge 2 ]; do wait -n; done
    step "feb-${name}" "$PY" scripts/analyse_phase2_results.py --study-dir "$dir" \
        --conditions "$@" --output "$O/feb/${name}.json" --quiet &
}
# (1) first pass, unrepaired copy
feb phase2a $F/phase2a image-only brief-text brief-text-image verbose-text verbose-text-image
feb phase2b-track1 $F/phase2b/track1-image T0.0 T0.3 T0.7 T1.0 T1.3
feb phase2b-track2 $F/phase2b/track2-text T0.0 T0.3 T0.7 T1.0 T1.3
feb phase2c-track1 $F/phase2c/track1-image canonical scale-4 scale-8 plus-hp pure-positive-canon
feb phase2c-exploratory $F/phase2c/track1-image-exploratory pure-positive-canon pure-positive-2hp pure-positive-4hp
feb phase2d-track1 $F/phase2d/track1-image minimal terse verbose
feb phase2d-track2 $F/phase2d/track2-text minimal terse verbose
feb phase2e $F/phase2e config-default canonical-first canonical-last random
wait
mkdir -p "$O/feb-first-pass" && cp "$O"/feb/*.json "$O/feb-first-pass/"
echo "first-pass-done" >> "$O/status.tsv"
# (2) repair the copy, as at 07:04:47Z
( cd "$F" && find phase2b -type f -regex ".*/detections_T[0-9.]*_run[0-9][0-9]" | while read f; do mv "$f" "$f.geojson"; done
  echo "phase2b geojson count: $(find phase2b -name '*.geojson' | wc -l)"
  cd phase2e/config-default && for l in run_*; do rm "$l"; ln -s "$F/phase2c/track1-image/plus-hp/$l" "$l"; done
  ls -la ) > "$O/repair.log" 2>&1
# (3) re-run the four affected analyses, as at 07:05:33Z
feb phase2b-track1 $F/phase2b/track1-image T0.0 T0.3 T0.7 T1.0 T1.3
feb phase2b-track2 $F/phase2b/track2-text T0.0 T0.3 T0.7 T1.0 T1.3
feb phase2d-track2 $F/phase2d/track2-text minimal terse verbose
feb phase2e $F/phase2e config-default canonical-first canonical-last random
wait
# (4) the comparison (feb_compare.py with its archive and output paths re-pointed)
step feb_compare "$PY" "$S/w1-3_feb_compare.py" "$T/archive/outputs-pre-retest-60-tile" "$O/feb" "$O/feb_compare.json"
echo ALL-DONE >> "$O/status.tsv"
