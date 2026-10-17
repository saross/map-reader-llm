#!/bin/bash
# Compare candidate copies A and B (raw, before L1 reduction) with each other
# and copy A with its predictions. Read-only on everything but out/.
set -u
L=~/scratch/s164-restate-2026-10-15/lane-pairwise
A=$L/runs/A/repo; B=$L/runs/B/repo
N=~/scratch/d60-consensus-route-2026-10-12
S3=~/scratch/d57-4-rescore-2026-10-09/phase3-out/new/h3/tiering-champions
P=~/Code/map-reader-llm/.venv/bin/python
C="$P -I -B $L/bin/cmp_dirs.py"
O=$L/out/cand-cmp
mkdir -p "$O"
git -C "$A" status --porcelain --untracked-files=all > "$O/status-A.txt"
git -C "$B" status --porcelain --untracked-files=all > "$O/status-B.txt"
cmp -s "$O/status-A.txt" "$O/status-B.txt" && echo "status lists identical" > "$O/status-AB.txt" || echo "status lists DIFFER" > "$O/status-AB.txt"
awk '{print $2}' "$O/status-A.txt" > "$O/modified-A.txt"
$C "$A" "$B" --files "$O/modified-A.txt" --root "$A" --root "$B" \
  --drop-keys timestamp,generated_at,generated_at_utc > "$O/A-vs-B.txt"
$C "$A/results/pairwise/20m" "$N/out/new1-20m" --root "$A" --root "$N/repo" > "$O/pred-20m.txt"
$C "$A/results/pairwise/30m" "$N/out/new1-30m" --root "$A" --root "$N/repo" > "$O/pred-30m.txt"
$C "$A/results/pairwise/leaderboard-20m" "$L/trial/lb-20m" --root "$A" > "$O/pred-lb20.txt"
$C "$A/results/pairwise/leaderboard-30m" "$L/trial/lb-30m" --root "$A" > "$O/pred-lb30.txt"
$C "$L/trial/factor-20m" "$A/results/pairwise/factor-analysis-20m" --root "$A" \
  --root /home/shawn/scratch/s164-restate-2026-10-15/wt > "$O/pred-factor.txt"
$C "$L/trialtree/results/factor-analysis" "$A/results/factor-analysis" > "$O/pred-collect.txt"
$C "$L/trial/e45-h2-rerun" "$A/results/e45-bootstrap-pairings/h2-rerun" --root "$A" \
  --root /home/shawn/scratch/s164-restate-2026-10-15/wt > "$O/pred-h2rerun.txt"
$C "$S3" "$A/results/diversity-dividend-384/tiering-champions" \
  --drop-keys generated_at_utc,git_commit --show 20 > "$O/pred-h3tier.txt"
$P -I -B "$L/bin/cmp_e45.py" "$A/results/e45-bootstrap-pairings/e45_bootstrap_pairings.json" \
  "$L/out/trial-e45.json" > "$O/pred-e45.txt"
echo done > "$O/done"
