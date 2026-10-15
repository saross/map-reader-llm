#!/usr/bin/env bash
# Replays of two register-transform files in this group that were written on
# amd-tower, not sapphire (transcripts, agents a51feb87262e915a2 and
# a771172bf2954c784); replayed on sapphire for completeness.
#  (a) f31e7470e: build_k_ladder_tiering_input.py, the command recorded at
#      2026-09-12T01:19:55Z, at f31e7470e;
#  (b) 3d9c64807: author_k_ladder_board_membership.py --write, recorded at
#      2026-09-13T00:21:39Z, at 3d9c64807.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
source "$ROOT/env.sh"
echo "start $(date -u +%FT%TZ) PYTHONHASHSEED=${PYTHONHASHSEED:-unset}"
cd "$ROOT/w2-3b-f31e7470e" || exit 1
echo "(a) head $(git rev-parse --short HEAD)"
rm -rf results/k-ladder-2026-09-12/tiering-input/gs-stride-a
$PY scripts/build_k_ladder_tiering_input.py --analysis-id k-ladder-gs-stride-a-2026-09-12 \
  --note "The gold-standard stride-A (g384 ov128) K ladder, K = 1/3/5/10 at prob_t 0.15 with an exact re-verification per rung, re-scored on the Era-2 board frame." \
  --rung 'stride-phaseb-2026-08-25::g384-ov128-ladder-n1-verified-p0.15-k1=results/k-ladder-2026-09-12/board-frame/stride-phaseb__g384-ov128-ladder-n1/evaluation.json' \
  --rung 'stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3=results/k-ladder-2026-09-12/board-frame/stride-phaseb__g384-ov128-ladder-n3/evaluation.json' \
  --rung 'stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4=results/k-ladder-2026-09-12/board-frame/stride-phaseb__g384-ov128-ladder-n5/evaluation.json' \
  --rung 'stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8=results/k-ladder-2026-09-12/board-frame/stride-phaseb__g384-ov128-k10/evaluation.json' \
  --out-dir results/k-ladder-2026-09-12/tiering-input/gs-stride-a
echo "(a) exit=$?"
cd "$ROOT/w2-3b-3d9c64807" || exit 1
echo "(b) head $(git rev-parse --short HEAD)"
rm -f results/leaderboard/era2/gs-era2-verified-board-2026-09-10/k-ladder/membership.json
$PY scripts/author_k_ladder_board_membership.py --write
echo "(b) exit=$? end $(date -u +%FT%TZ)"
