#!/usr/bin/env bash
# D42 regeneration on sapphire (Session 161). Runs every producer whose code
# now takes a permutation p, in place in the clone (git is the scratch: the
# committed versions stay in HEAD and every change is reviewed by diff before
# anything is committed). The February 60-tile re-test writes to /tmp/d42/feb
# only; the archive is never touched. Each step logs to /tmp/d42/<step>.log
# and records its exit code in /tmp/d42/status.tsv.
set -u
cd ~/Code/map-reader-llm || exit 1
source .venv/bin/activate
mkdir -p /tmp/d42/feb
: > /tmp/d42/status.tsv

step() {  # step <name> <command...>
    local name=$1; shift
    local t0=$(date +%s)
    "$@" > "/tmp/d42/${name}.log" 2>&1 < /dev/null
    local rc=$?
    printf '%s\t%s\t%ss\n' "$name" "$rc" "$(( $(date +%s) - t0 ))" >> /tmp/d42/status.tsv
}

# Group 1: the C1/C2 analyses, in parallel (independent outputs).
step family python scripts/compute_family_fdr.py &
step e45 python scripts/e45_bootstrap_pairings.py --h2-rerun-json results/e45-bootstrap-pairings/h2-rerun/group_1_architecture/pv-vs-consensus-flash-high-text-16-of-30-pv-vs-flash-high-text-26-of-30.json &
step h13 python scripts/h13_overlap_analysis.py &
step grid python scripts/grid_analysis.py --bootstrap 10000 &
step incumbents python scripts/grid_incumbent_rescore.py &
step stride python scripts/stride_verifier_analysis.py &
wait
# grid_verifier_analysis reads grid_analysis.json, so it runs after grid.
step grid_verifier python scripts/grid_verifier_analysis.py

# Group 2: the retest phase evaluations, one process per phase.
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
  step "retest-${key}" python scripts/evaluate_retest_all.py --phase "$key" --output "results/retest/${RETEST[$key]}" &
done
wait

# Group 3: the February 60-tile instrument, re-run on a COPY in /tmp (the
# script writes per_run_metrics.csv into its study directory, and the archive
# is never written). Outputs go to /tmp/d42/feb only.
rm -rf /tmp/d42/febdata && mkdir -p /tmp/d42/febdata
cp -r archive/outputs-pre-retest-60-tile/phase2a archive/outputs-pre-retest-60-tile/phase2b \
      archive/outputs-pre-retest-60-tile/phase2c archive/outputs-pre-retest-60-tile/phase2d \
      archive/outputs-pre-retest-60-tile/phase2e /tmp/d42/febdata/
F=/tmp/d42/febdata
feb() {  # feb <name> <study-dir> <conditions...>
    local name=$1 dir=$2; shift 2
    step "feb-${name}" python scripts/analyse_phase2_results.py --study-dir "$dir" \
        --conditions "$@" --output "/tmp/d42/feb/${name}.json" --quiet
}
feb phase2a $F/phase2a image-only brief-text brief-text-image verbose-text verbose-text-image &
feb phase2b-track1 $F/phase2b/track1-image T0.0 T0.3 T0.7 T1.0 T1.3 &
feb phase2b-track2 $F/phase2b/track2-text T0.0 T0.3 T0.7 T1.0 T1.3 &
feb phase2c-track1 $F/phase2c/track1-image canonical scale-4 scale-8 plus-hp pure-positive-canon &
feb phase2c-exploratory $F/phase2c/track1-image-exploratory pure-positive-canon pure-positive-2hp pure-positive-4hp &
feb phase2d-track1 $F/phase2d/track1-image minimal terse verbose &
feb phase2d-track2 $F/phase2d/track2-text minimal terse verbose &
feb phase2e $F/phase2e config-default canonical-first canonical-last random &
wait
echo ALL-DONE >> /tmp/d42/status.tsv
