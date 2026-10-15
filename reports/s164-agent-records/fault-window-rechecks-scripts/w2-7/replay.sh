#!/usr/bin/env bash
# W2-7 replay: the modality-track audit recomputation.
#
# Step 1, d5eaeb1ee (2026-09-13T23:48:10Z), replayed at its parent
# c1b151bce, which the original worktree (~/worktrees/map-reader-llm/
# claude-track on sapphire) had just pulled. Original commands (session
# archive 2026-09-11T04-35, sub-agent a9b65f3759cd18e1b, 23:46:10Z and
# 23:46:18Z), with R=results/modality-track-audit-2026-09-14/recomputed:
#   characterise_gs_plateau.py --legacy-modality --out-dir $R/working-precision-legacy
#   characterise_gs_plateau.py --out-dir $R/working-precision
#   tile_size_sweep.py --legacy-modality --output-dir $R/tile-size-sweep-legacy
#   tile_size_sweep.py --output-dir $R/tile-size-sweep
#   compare_modality_recomputation.py
# Step 2, aa1d9bd5b (23:59:17Z, "re-render recomputation.md with blanks
# collapsed"), replayed at its parent 6dfe7cbeb: compare_modality_recomputation.py.
# The replay trees start without the committed outputs (removed before the
# run), so every file compared is written by the replay.
# Usage: replay.sh <tree at c1b151bce> <tree at 6dfe7cbeb> <out dir>
set -u
T1=$1; T2=$2; O=$3
A=results/modality-track-audit-2026-09-14
R=$A/recomputed
source "$HOME/scratch/s164-fw-recheck2-2026-10-15/env.sh"
canary() { git -C "$HOME/Code/map-reader-llm" status --porcelain=v1 | sha256sum | cut -c1-16; }
echo "=== $(date -u +%FT%TZ) live-checkout canary $(canary)"
cd "$T1" || exit 9
echo "=== step 1 at $(git rev-parse --short HEAD)"
rm -rf "$R" "$A/recomputation.json" "$A/recomputation.md"
"$PY" scripts/characterise_gs_plateau.py --legacy-modality --out-dir "$R/working-precision-legacy" > "$O/s1-plateau-legacy.log" 2>&1; echo "plateau legacy rc=$?"
"$PY" scripts/characterise_gs_plateau.py --out-dir "$R/working-precision" > "$O/s1-plateau.log" 2>&1; echo "plateau rc=$?"
"$PY" scripts/tile_size_sweep.py --legacy-modality --output-dir "$R/tile-size-sweep-legacy" > "$O/s1-sweep-legacy.log" 2>&1; echo "sweep legacy rc=$?"
"$PY" scripts/tile_size_sweep.py --output-dir "$R/tile-size-sweep" > "$O/s1-sweep.log" 2>&1; echo "sweep rc=$?"
"$PY" scripts/compare_modality_recomputation.py > "$O/s1-compare.log" 2>&1; echo "compare rc=$?"
rm -rf "$O/step1"; mkdir -p "$O/step1"; cp -r "$A/." "$O/step1/"
cd "$T2" || exit 9
echo "=== step 2 at $(git rev-parse --short HEAD)"
rm -f "$A/recomputation.json" "$A/recomputation.md"
"$PY" scripts/compare_modality_recomputation.py > "$O/s2-compare.log" 2>&1; echo "compare rc=$?"
rm -rf "$O/step2"; mkdir -p "$O/step2"; cp "$A/recomputation.json" "$A/recomputation.md" "$O/step2/"
echo "=== $(date -u +%FT%TZ) DONE; live-checkout canary $(canary)"
