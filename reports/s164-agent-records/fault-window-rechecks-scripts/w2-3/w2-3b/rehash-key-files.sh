#!/usr/bin/env bash
# Re-hash one key regenerated file per group against its git blob, by hand
# (sha256 prefixes), independently of compare_files.py. Run from
# ~/scratch/s164-fw-recheck2-2026-10-15. Paths with a machine root are
# compared after the documented root substitution.
R=w2-3b-out/regen
chk() { a=$(sha256sum < "$3" | cut -c1-16); b=$(git -C wt show "$1:$2" | sha256sum | cut -c1-16)
        echo "$1 $a $b $([ "$a" = "$b" ] && echo MATCH || echo DIFF) $2"; }
chk d10137595 results/k-ladder-2026-09-12/mcc-test/tiering/gs-stride-a/tiering_20m.md $R/d10137595/mcc-test/tiering/gs-stride-a/tiering_20m.md
chk 326181bcd results/k-ladder-2026-09-12/phase2/mcc-test/tiering/phase2-scale-4-optimal-487/tiering_20m.md $R/326181bcd/mcc-test/tiering/phase2-scale-4-optimal-487/tiering_20m.md
chk b7e2821ba results/k-ladder-2026-09-12/mcb/table.md $R/b7e2821ba/mcb/table.md
SUB=$(mktemp -p w2-3b-out)
sed "s#$HOME/scratch/s164-fw-recheck2-2026-10-15/w2-3b-cebae7868#/home/shawn/worktrees/map-reader-llm/claude-mcb#g" $R/b7e2821ba/mcb/tier-e/k-ladder-tier-e-2026-09-12_b20_m1.json > "$SUB"
chk b7e2821ba results/k-ladder-2026-09-12/mcb/tier-e/k-ladder-tier-e-2026-09-12_b20_m1.json "$SUB"
rm -f "$SUB"
chk 98e54baf6 outputs/grid-2026-08-18/g384_ov192/consensus-n3/consensus_t1.geojson $R/98e54baf6/outputs/grid-2026-08-18/g384_ov192/consensus-n3/consensus_t1.geojson
chk 5167b9a5c outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k1/sweep_board.json $R/5167b9a5c/outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k1/sweep_board.json
chk 5167b9a5c results/k-ladder-2026-09-12/tier-e/materialised/grid-2026-08-18__g384-ov192-k1-verified-opmax/detections.geojson $R/5167b9a5c/results/k-ladder-2026-09-12/tier-e/materialised/grid-2026-08-18__g384-ov192-k1-verified-opmax/detections.geojson
chk 5167b9a5c outputs/h10/evaluation-v2/pool_160_hp4hn4/consensus/consensus_t1.geojson $R/5167b9a5c/outputs/h10/evaluation-v2/pool_160_hp4hn4/consensus/consensus_t1.geojson
chk 9457b2689 results/k-ladder-2026-09-12/phase2/committed-carried/materialised/pv-scale4-optimal-n10-carried-p0.15-k10.geojson $R/9457b2689/materialised/pv-scale4-optimal-n10-carried-p0.15-k10.geojson
if [ -f $R/d900ed1d5/sign-swap/ladder_pairs.json ]; then
  chk d900ed1d5 results/k-ladder-2026-09-12/mcc-test/sign-swap/ladder_pairs.json $R/d900ed1d5/sign-swap/ladder_pairs.json
fi
