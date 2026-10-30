# D65 (2): the restatement pass (S164)

> **Last revised**: 2026-10-20 (§ 5 item 14 corrected: the plateau
> characterisation drops no row). 2026-10-18 (§ 1.3 and § 5 item 9 corrected: the board's
> membership does not drift; the 98 was an artefact of a partial copy).
> 2026-10-15 (the results half: lanes, verdicts, drafted
> outcomes, claim rows, surprises; the pass complete apart from § 11). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), the lead background agent of the main Session 164
  session (workstream `restatement-pass-s164`), with Opus sub-agents for
  four lanes (each named below). Only this agent writes commits, the
  register, and this record.
- **Date**: 2026-10-15 (UTC).
- **Repository**: `map-reader-llm`, branch `restatement-pass-s164` from
  `origin/main` at `718d0ee08`; worktree
  `~/scratch/s164-restate-2026-10-15/wt` on sapphire.
- **Rulings executed**: `planning/pi-decisions-2026-09-20.md` D65 (2)–(4),
  (6), D62 (2) and (6), D67 (5) and (6); under D50, D51, D55 Q1, D58 (Q2,
  Q4, Q6), D60 (3), D9, D42, D45–D48 and D63.
- **Measurements published**: `reports/s164-agent-records/rescore-repaired-gs.md`
  (PR #46; the REPAIRED column is the prediction for every GS value),
  `reports/s164-agent-records/s9-staleness-sweep.md` (PR #50; the eight
  K-ladder cells and the eight 55-map extended-reference cells),
  `reports/s163-agent-records/d60-3-consensus-route.md` (PR #37),
  `reports/s163-agent-records/origin-gap-grid-plateau.md`,
  `origin-gap-h13-copies.md`, `scorer-restatement-inventory.md`.
- **Guarantees**: no model Application Programming Interface (API) call;
  no register `outcome` text changed (each new wording is drafted below for
  the PI); nothing re-signed or merged; the null-exemplar analysis, A-06 and
  the D64 data are out of scope.
- **Drivers**: [`restatement-pass-scripts/`](restatement-pass-scripts/).

**Conventions.** COMMITTED is the file at `origin/main` `718d0ee08`.
PREDICTED is the value the measurement recorded: for the gold-standard (GS)
chain, the REPAIRED copy of the 2026-10-13 re-score
(`~/scratch/s164-rescore-2026-10-13/copies/repairedA` on sapphire, code and
data at `9c843b980`); between `9c843b980` and `718d0ee08` no script the GS
chain runs and no input it reads changed (`git diff --stat` over the
chain's inputs and `scripts/` shows only `h6_registered_analyses.py`, the
D64 scripts, and signature fields of `results/run-analyses.json`), so that
copy is a file-level prediction for every GS chain output.
REGENERATED is this pass's output. F1 is at 20 m on the 487-tile common
footprint unless stated.

## Bottom line

The pass regenerated, once and on today's `main`, every committed output
the S164 re-score, the S9 staleness sweep and PR #37 measured moving, in
seven lanes, each in two independent runs that agree apart from
timestamps, run roots and wall-clock timings (§ 7). Every lane matches its
prediction on every value the prediction covers. The mismatches are
explained and none changes a test or a tier boundary the prediction
named: the Era-2 board displays tier E's S9 re-scores, which the
prediction predated (three tier labels move, every one of 11,175 pair
decisions is as predicted); the fourth cell's board-frame argmax moved
off its registered point, so one optimism run failed the anchor gate the
plan expected it to pass; the extended-reference cells' MCC intervals
moved; and the K-ladder's tension step had run before the Phase 2 tables
it reads, so it was re-run (§ 2).

The restated numbers change readings, and the failures are stated as
failures: the overlap reversal at 384 px no longer clears (−0.0256
[−0.0517, +0.0001], p 0.0541); I3 fails on the 3.7 image carried arm;
R1b-15's 30 m sentence and R1b-16's shared 30 m shelf fail; the grid
findings' Phase A reading fails (the winner leads at 20 m only and no
longer clears min6: +0.0339, p 0.020 → +0.0226, p 0.111); the K ladders'
"about 40 %" verifier
share is now 60.3 %; the 3.7 ladder's last step is no longer the
corpus's dearest; and four modality-bridge readings change (§ 5).

Fifteen signed register rows quote numbers the pass moved: their
signatures lapse (ten in `ed91d2df8`, five in `92a66089d`) and their
redrafted outcomes, with word-level diffs, are in § 4 for the PI. No
`outcome` text was changed and nothing was re-signed. Thirty-nine claim
rows of the frozen inventory are affected (28 restate, 3 fail, 8 were
already stale); the inventory is not edited (D55 Q1; § 6). Two analyses
the pass did not re-run now rest on moved inputs (the null-exemplar
sensitivity and the per-student GS baseline), and six Phase 2 ladders'
MCB and MCC test rest on unclipped cells the D51 inventory now withholds;
these, and thirteen other questions, are in § 10.

## 1. Plan

The plan is committed in stages, each lane's part before that lane
regenerates. Each artefact is produced in two independent runs (fresh
processes, separate output trees) and compared byte for byte apart from
timestamps and run roots, then against its prediction; only then is it
copied into the worktree. Kernel bad-page count
(`journalctl -k -b | grep -c "Bad page state"`) is read before the first
run and after the last.

### 1.1 Design decisions taken before any run

1. **Registered conditions keep their points; analyses keep re-selecting
   their argmax (D65 (3)).** The 2026-10-13 re-score materialised three
   registered conditions at their moved argmax. Under D65 (3) a registered
   (carried) condition keeps its registered operating point, with the new
   argmax reported beside it, so this pass materialises:
   - `grid-2026-08-18::g384-ov048-k10-verified-p0.20-k7` at (0.20, k7)
     (predicted F1 0.8752, 365 detections; argmax (0.15, k7), 0.8761);
   - `stride-phaseb-2026-08-25::g512-ov176-k10-verified-p0.15-k6` at
     (0.15, k6) (predicted 0.8714, 396; argmax (0.15, k7), 0.8718);
   - `gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5`
     at (0.10, k5) (predicted 0.9353, 438; argmax (0.05, k5), 0.9381).

   The predictions are the sweep rows at the registered points
   (`rescore-repaired-gs-scripts/records/extract/repairedA.json`,
   `regpoint/*`). The analyses themselves (grid post-verifier board, stride
   board, plateau, the 3.7 image gap test) re-select each cell's best point,
   as the re-score's § 8 question 3 put to the PI, so their values stay the
   REPAIRED predictions. One analysis read a registered condition's file as a
   "best point": the stride board takes its four grid cells from
   `results/grid-2026-08-18/conditions-verified/<cell>/`. So that it keeps
   reading each grid cell's best point (as its five stride cells do),
   `grid_verifier_analysis.py` also writes each cell's argmax set to
   `results/grid-2026-08-18/verified-best/<cell>/detections.geojson`, and
   `stride_verifier_analysis.py` reads those. The alternative reading (the
   stride board takes the registered set, 0.8752 for 384/12.5) is reported
   beside it in § 4 for the PI.
2. **Opmax cells move to the new argmax (D65 (3))**: the `-opmax` cells of
   tier E and of the Gemini 3.7 GS text ladder (K-ladder lane, § 1.4).
3. **Hand-typed constants that pin a moved value get a dated update**
   (D58 Q6), never a silent one: the text-B anchor
   `image_b_analysis.ANCHOR_F1_20` 0.8961 → 0.9017; the 3.7 image gap test's
   `PAIRS` (0.9139 / 0.9254 / 0.9265 / 0.9308 → 0.9238 / 0.9381 / 0.9364 /
   0.9408) and `G3_GAP` (+0.0549 → +0.0559, p 0.001); the Arm V pair test's
   `INCUMBENTS` (0.9265 / 0.9139 → 0.9364 / 0.9238). The tier-1 guard
   `tests/test_gemini38_armv_pair_test.py` pins `INCUMBENTS` to the
   regenerated analyses. Instrument gates that check against values
   registered on the legs as run keep reading the legs as run (the bridge's
   six-cell anchor gate, `modality_bridge_anchors.GATE_POLICY = "fixed"`).
4. **Regenerate in place or keep beside (D58 Q2, Q4).** An artefact whose
   inputs are unchanged and whose instrument (or verifier rows) changed is
   regenerated in place. An artefact whose inputs drifted before tracking,
   so that its as-scored inputs cannot be recovered, stays as a historical
   record and today's run goes beside it, labelled (PR #37's single-pass
   arms, D61 (2); pairwise lane, § 1.5).
5. **Which documents are restated.** Every `results/**.md` and
   `reports/**.md` that presents a moved number as an analysis's current
   finding (findings, board READMEs, generated renders) is edited in place
   under the Document Revision Policy. Dated measurement records and deltas
   reports (for example the S163/S164 agent records, whose tables are
   COMMITTED → … by construction) are records of what was measured when, and
   are left; § 9 lists them. `docs/paper/` drafts and the frozen claims
   inventory (D55 Q1) are not edited; § 6 lists the claim rows.

### 1.2 GS chain lane (this agent)

**Code changes, committed before the runs** (each with a tier-1 test and a
red sentinel in a copied, not linked, harness):

| File | Change |
|---|---|
| `scripts/grid_verifier_analysis.py` | `REGISTERED_POINTS` (the register's four grid verified conditions); `--materialise-conditions` writes each condition at its registered point, gated on the sweep row at that point, and records the argmax point, F1 and count beside it; writes each cell's argmax set to `verified-best/<cell>/detections.geojson` |
| `scripts/stride_verifier_analysis.py` | `GRID_CELLS` read the grid cells' argmax sets (decision 1) |
| `scripts/image_b_analysis.py` | `ANCHOR_F1_20` 0.8961 → 0.9017, dated |
| `scripts/gemini37_image_gap_test.py` | `PAIRS`, `G3_GAP`, docstring, dated |
| `scripts/gemini38_armv_pair_test.py` | `INCUMBENTS`, docstring, dated |

**Driver** `restatement-pass-scripts/gs_chain.sh` (the re-score's
`chain.sh` with four changes: the copy is this branch's head; the 3.7 image
carried arm runs with `--operating-point 0.10,5`, writing its registered set
`verified_op_20m.geojson`; the gap and Arm V tests run their own scripts with
the dated constants rather than a wrapper; `--anchor-f1` is left to the
dated default), then `gs_conditions.py` (the re-score's `conditions.py`,
with the stride K = 10 conditions at their REGISTERED points read from
`results/run-conditions.json`, the winner-ladder rungs, the nine `best-eval/`
evaluations with their committed arguments, and the 3.7 image carried arm's
`op-eval/`), then the grid selection-aware pilots and `sensitivity_mde.py`.

| Artefact (under `results/`) | Generator | Prediction |
|---|---|---|
| `grid-2026-08-18/{grid_analysis.json, sweep.csv, per_tile_counts.json}`, `conditions/` (4 cells and `grid_conditions.json`) | `grid_analysis.py --bootstrap 10000`, `grid_materialise_conditions.py` | REPAIRED copy (PR #42's origin route; ORIGIN = REPAIRED here) |
| `grid-2026-08-18/{verifier_analysis.json, verifier_sweep.csv}`, `conditions-verified/` (4 cells, `grid_verified_conditions.json`), `verified-best/` (new) | `grid_verifier_analysis.py --materialise-conditions` | REPAIRED copy, except 384/12.5's condition at (0.20, k7): `regpoint/grid/g384_ov048` |
| `grid-2026-08-18/incumbents_common_footprint.json` | `grid_incumbent_rescore.py` | REPAIRED copy |
| `stride-2026-08-25/{stride_verifier_analysis.json, stride_verifier_sweep.csv}` | `stride_verifier_analysis.py` | REPAIRED copy |
| `stride-2026-08-25/plateau_analyses.json` | `stride_plateau_analyses.py` | REPAIRED copy |
| `stride-2026-08-25/conditions-verified/` (5 K = 10 cells, 3 ladder rungs) | `gs_conditions.py` | REPAIRED copy, except 512/34.4 at (0.15, k6): `regpoint/stride/g512_ov176` |
| `image-b-gs-2026-08-28/` and `high/` (analysis, sweep, best set, `best-eval/`), `high/pair_verdicts.json` | `image_b_analysis.py` (×2), `image_b_pair.py`, `gs_conditions.py` | REPAIRED copy (anchor `registered` 0.9017 for the unrounded value) |
| `gemini37-screen-2026-08-28/` (K = 5, `k10/`, `swap37/`), `gemini38-screen-2026-09-04/armV/` (+ `pair_test.json`), `gemini37-fourth-cell/gs-leg/` | `image_b_analysis.py`, `gemini38_armv_pair_test.py`, `gs_conditions.py` | REPAIRED copy |
| `gemini37-image-gs-2026-09-01/arm1/`, `arm2/`, `gap_test.json` | `image_b_analysis.py` (arm 1 with `--operating-point 0.10,5`), `gemini37_image_gap_test.py`, `gs_conditions.py` | REPAIRED copy; arm 1's registered set and `op-eval/`: `regpoint/g37img/arm1` |
| `selection-aware/g{384_ov048,384_ov192,512_ov064,512_ov256}_K10_b20_m*.json` (7) | `selection_aware_intervals.py --cell <cell> --K 10 --bootstrap 10000 [--m-frac]` | `apparent_f1` = the regenerated consensus best (0.6574, 0.7293, 0.6845, 0.7611); optimism, intervals and sets: **no prediction** (not re-run by any record) |
| `sensitivity-mde-2026-08-28/` | `sensitivity_mde.py` (fed by Image-B's null SDs) | **no prediction** (not re-run by any record) |

`results/verifier-robustness/` is read, not written (every file equals the
committed one in the REPAIRED copy).

### 1.3 Era-2 board lane (this agent, after §§ 1.2 and 1.4)

`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/`
(`scripts/build_gs_era2_board.py`; card
`planning/gs-era2-verified-board-2026-09-08.md`): the ten members downstream
of the re-verified legs re-scored on the board frame (`cells/`) and on their
own frames (`g2/`, 200 draws) with their committed arguments, the 3.7 image
carried arm's member scoring its registered set; `gates` (G2–G6,
`gates.json`, `frame-deltas.md`); `era1_leaderboard_tiering.py
--permute-mcc` (`tiering_20m.json`); `selection_aware_intervals.py --board`
for F1 and tile-MCC (`mcb/`); `finalise --no-analysis-row` (`README.md`,
`provenance.json`; the proposed outcome goes to provenance, never to the
register). The seven board members that are S9 K-ladder cells are re-scored
in § 1.4 first. Prediction: re-score § 3.1, REPAIRED column (8,075 of
11,175 pairs significant; 14 tiers; the same five-cell Tier 1 in the same
order; F1 MCB set 52; tile-MCC 3,001 / 6 / 34 / 60; leaders 0.9332, 0.9289,
0.9282, 0.9278, 0.9169).

Three details, settled before the board runs (drivers `mkcopy_board.sh`,
`board_chain.sh`, `board_membership.py`, `board_optimism_runs.tsv`):

- **The membership is kept, its snapshot fields refreshed.** Re-deriving
  `membership.json` today changes the membership itself (the derivation now
  reads later register edits: 98 members instead of 110), a board change this
  pass does not make. So each member's `committed_f1_20` is re-read from its
  evaluation and the 3.7 image carried arm's paths follow its register row,
  recorded in a `_restated` block; the drift of the derivation rule is for the
  PI (§ 10).

  **Corrected 2026-10-18 (Session 165):** the 98 is not a drift in the
  rule. Re-derived read-only on the full branch checkout
  (`build_gs_era2_board.derive_membership()` at `26deb34a3`), the
  membership is the same 110 members, none dropped or added. The 98 came
  from running the derivation inside the board's partial copy
  (`mkcopy_board.sh`), where exactly 12 members' detection files lie
  outside the copied directories (eight `proposer-verifier-384` cells,
  three `verifier-t-pilot` cells, and
  `pv-diag-384::verified-adv-text-consensus-16of30`), so the derivation
  skipped them as missing on disk; all 110 files are tracked. The match
  is by count, since the 98-member list was not recorded. The PI
  accepted keeping the membership (D69).

- **The board's sweep-optimism tables** (`optimism/`, ten screen cells on two
  frames; `selection_aware_intervals.py --sweep-union`) read the same legs and
  are regenerated too. Their builder was off the origin route (fixed in
  `92889e0e5`); no record predicted them. The 3.7 image carried arm's
  board-frame run takes no anchor gate: the gate checks that the sweep's
  argmax is the board cell, and under D65 (3) the board cell is now the
  registered point. `summarise_sweep_optimism.py` rewrites the README's
  changelog, which is restored by hand.
- **`finalise --no-analysis-row`** writes the README and provenance and puts
  its proposed outcome into `provenance.json`; the register row is not
  touched. The README's banner and changelog are restored by hand.

### 1.4 K-ladder lane (sub-agent)

Inventory by an Opus sub-agent (`~/scratch/s164-restate-2026-10-15/lane-kladder/`;
its per-sweep records are `out/kladder-lane-summary.json`). Four of its
findings change the plan:

- **The 3.7 opmax derivation is not on the origin route.**
  `derive_g37_gs_opmax_rungs.py` sweeps and materialises from
  `union_k{5,10}.geojson`, which records only a legacy `source_tile`, so the
  re-verified wrong-sheet rows score on the wrong sheet: run as it stands it
  gives 0.8984 at (0.10, k5) and (0.10, k10), against the origin-routed board
  cells' 0.9165 and 0.9169 at the same points. It is fixed first (the union
  through `image_b_analysis.load_image_union` and the origin step, with a
  tier-1 test and a red sentinel), and its committed-count cross-check
  (`CARRIED_CROSSCHECK`, K = 5, 443 features) gets a dated update to 451, the
  restated `verified_best_20m.geojson`'s count.
- **No opmax argmax moves** on the REPAIRED reading (decision 2 has nothing
  to move): tier E K = 1 (0.20, k1), K = 3 (0.15, k3), K = 5 (0.15, k5); the
  3.7 ladder's K = 1 (0.15, k1), K = 3 (0.10, k3), K = 5 (0.10, k5) and
  K = 10 (0.10, k10), each on the board frame, clipped and unclipped.
- **Today's Phase 2 builder refuses seven ladders on the D51 area gate**
  (`build_k_ladder_phase2_tables.py` v1.4.0; the committed tables are
  v1.2.1, before the gate): the 3.7 ladder and six Gemini 3 `pv-diag-384`
  ladders. Their clip is ruled (D57 (2) and (3) for the six, D67 (5) for the
  3.7 ladder) and was deferred to a ladder step that never ran, so the
  builder runs with `--clip-to-common-area --allow-undetermined-area`: the
  3.7 ladder reads 0.8682 / 0.9073 / 0.9165 / 0.9169 clipped (unclipped
  0.8747 / 0.9135 / 0.9165 / 0.9169 beside), two Gemini 3 ladders' F1 move
  by about 0.003–0.004 (HIGH text T 1.0, MINIMAL image T 0.7; within D57
  (2)'s severity estimate), and the builder withholds tile-MCC on the seven
  clipped ladders. These values were measured by the sub-agent's trial, not
  by the S9 or re-score records, and are flagged as such. The Phase 2
  tile-MCC test (`phase2/mcc-test/`) is not re-run: its cells do not move,
  and against the clipped compatibility inventory it would drop six
  ladders; that is for the PI (§ 10).
- **Tier E fails the same gate** (its area is the 3.7 ladder's), and D51's
  text says tier E "takes the same rule", while D67 (5) and this pass's
  brief restate tier E on today's scorer. This pass follows the brief
  (unclipped: K = 1 / 3 / 5 / 10 0.8680 / 0.8979 / 0.9046 / 0.8942, the
  S9 and re-score values) and reports the clipped reading beside it
  (0.8604 / 0.8902 / 0.8968 / 0.8942; § 8.6's share 48.8 % clipped against
  60.3 % unclipped) for the PI. `run_k_ladder_tier_e.py prepare`, which now
  refuses without the clip and would rewrite the registered tier E cells,
  is not re-run; the cells are re-scored in place and `collect` rebuilds
  the scores.

Generators, in order (after the GS lane; part 2 after the board lane):

| Step | Artefact (under `results/k-ladder-2026-09-12/`) | Generator | Prediction |
|---|---|---|---|
| 1 | the eight S9 cells (`tier-e/cells/` ×4, `phase2/cells/` 3.7 ×3, `recovery-fix-2026-09-13/reproduced-k5-evaluation/`) | `evaluate_detections.py` with each cell's recorded arguments (the recovery-fix copy's detections from its committed `materialised/k5.geojson`) | S9 § 3.1 |
| 2 | `tier-e/cells/…-k10-verified-p0_15-k10-boardframe/`, `board-frame/stride-phaseb__g384-ov128-{ladder-n1,n3,n5,k10}/` | the same, on the GS lane's regenerated sets | re-score § 3.2 |
| 3 | `tier-e/scores.json`, `tier-e/ladder.json`, `tier-e/tiering/`; `phase2/scores.json`; `phase2/g37-opmax/` | `run_k_ladder_tier_e.py collect`; `tier_e_ladder_tiering.py`; `score_k_ladder_phase2_rungs.py collect`; the fixed `derive_g37_gs_opmax_rungs.py prepare --clip-to-common-area`, its jobs, `collect` | re-score § 3.2; the sub-agent's trial for the 3.7 opmax rungs |
| 4 | `mcc-test/tiering/gs-stride-a/`, `mcc-test/gs-stride-a.json`, `mcc-test/summary.json`; `mcb/gs-stride-a/`, `mcb/tier-e/`, `mcb/summary.json`, `mcb/table.md` | `era1_leaderboard_tiering.py … --permute-mcc` (findings § 6.1); `k_ladder_mcc_test.py`; `k_ladder_mcb.py` | re-score § 3.2 (GS stride A +0.0131, BH p 0.7633; tier E MCC set adds K = 10) |
| 5 (after the board) | `phase2/{ladders.json, ladder-tables.md, ladders-compat.json}`, `figures/k-ladder-pareto-phase2.png` | `build_k_ladder_phase2_tables.py --clip-to-common-area --allow-undetermined-area` | as above |
| 6 | `ladders.json`, `figures/k-ladder-pareto.png`; `inventory.json` values | `build_k_ladder_tables.py`; the inventory's values refreshed for its existing membership only (regenerating it would add every ladder registered since, a structural change this pass does not make) | re-score § 3.2 |
| 7 | `tension/grid-overlap.json`, `tension/effect-sizes.json` | `k_ladder_tension_analyses.py --grid-overlap --effect-sizes` | re-score § 3.2 (§ 8.6: 60.3 %, swing 0.0682); § 8.3's grid table from the GS lane's `sweep.csv` |

One stale input gets a dated fix first: `phase2/operating-points.json` row
28 (the 3.7 K = 3 rung) still records 494 detections from before the
recovery fix; the cell holds 495.

### 1.5 Pairwise lane: PR #37's moved artefacts (sub-agent)

Inventory by an Opus sub-agent (`~/scratch/s164-restate-2026-10-15/lane-pairwise/`),
including a trial of every generator; its 1,260 arm instances equal PR #37's
`sources-new.json`, and the per-directory move counts equal #37's (280 of
325, 264 of 300, 5 of 12, 1 of 1). Generators (10,000 permutations, seed
42), each replicating the committed run's flags exactly:

| Artefact | Generator | Prediction |
|---|---|---|
| `results/pairwise/20m/`, `30m/` (32 each, manifest, `fdr/`) | `run_pairwise_tests.py --config configs/pairwise-comparisons.yaml --buffer-metres {20,30} --quiet`, then `apply_fdr_correction.py` | PR #37's NEW run (`d60-3-consensus-route.md` § 3; H2 at 20 m: arm B 0.816471, ΔF1 0.073730) |
| `results/pairwise/leaderboard-20m/` (325, manifest, `fdr/`) | `run_pairwise_tests.py --leaderboard configs/condition-registry.yaml --metrics results/paper-tables/metrics_master.csv --top-n 26 --buffer-metres 20`, then FDR | #37's arms; trial: 265 of 325 significant before and after (two pairs flip in opposite directions), tiers unchanged |
| `results/pairwise/leaderboard-30m/` (300) | as above at 30 m with `--top-n 25 --quiet` and `--metrics` pinned to the March file (`71d81cd5e`), because `metrics_master.csv` gained rows after that board ran | trial: 243 → 240 significant, tiers unchanged |
| `results/pairwise/factor-analysis-20m/` (12), then `results/factor-analysis/factor_analysis_results.{json,csv}` and `_autogen.md` | `run_pairwise_tests.py --config configs/factor-analysis-comparisons.yaml --buffer-metres 20`; `collect-factor-analysis.py` | trial: 23 of 61 rows change, no BH status flips |
| `results/e45-bootstrap-pairings/h2-rerun/`, `e45_bootstrap_pairings.json` | the rerun's `comparison.yaml`; `e45_bootstrap_pairings.py` | trial: H2 ΔF1 +0.073730, B = 10,000 CI [+0.048250, +0.101597]; H3 +0.429693 (the S3 record's) |

**In place and beside (decision 4).** The single-pass 5-of-5 and 10-of-10
arms' inputs changed before tracking (D61 (2): 951 → 954 and 898 → 901
detections), so every committed per-pair file that reads one stays at its
path as a March historical record: #7 and #8 in `20m/` and `30m/`
(`group_1_architecture/`), and 49 and 47 files in the two leaderboards'
`group_8/`. Today's runs of those pairs go beside them, labelled, under
`results/rescore-2026-10-15/pairwise/` (outside `results/pairwise/`, which
`regen_e43_board.py` scans), with a README naming the vintage. Every other
per-pair file is regenerated in place. A run's manifest and its BH family
belong to one run, so each directory's `run_manifest.json` and `fdr/` are
today's complete run; for #7 and #8 nothing in them moves (p 0.0 before and
after).

**Not regenerated in this pass, for the PI**:
`results/e43-board-regen/` (the E72 board, `regen_e43_board.py`). Under the
in-place-and-beside layout its gates A and C refuse a `group_8/` that mixes
vintages, its gate B pins the March 30 m count (243), and its renderers
rewrite a 2026-08-02 banner over any revision trail; each needs a ruling or
a code change this pass does not make. The trial's values are reported in
§ 5 (the committed 20 m confirmatory family's status change for #30 no
longer happens).

**e45's other prerequisite.** `e45_bootstrap_pairings.py` also gates H3
against `results/diversity-dividend-384/tiering-champions/tiering_20m.json`,
committed 2026-06-06 and still reading the 26-of-30 arm's pre-D50 0.814118.
e45 is regenerated only if that file's regeneration is a committed
command whose moved values are all predicted (the S3 record); otherwise e45
and its rerun are left, and the reason recorded.

### 1.6 Uplift supplement and extended-reference lane (sub-agent, then this agent)

Inventory by an Opus sub-agent (`~/scratch/s164-restate-2026-10-15/lane-uplift/`
on sapphire); every path and count below was re-read by this agent before
it was written here.

**A. The eight 55-map extended-reference cells** (D67 (6);
`results/55maps-extended-gt-2026-06-07/`). Generators, in order:
`score_55maps_extended_gt_canonical.py --output-base
results/55maps-extended-gt-2026-06-07 --workers 7` (IM-k3, T03-k3, T03-k4,
TH7-k3, TH7-k4, TM-k3, TM-k4: each `summary.json`, `corrected-f1.csv`,
`report_autogen.md`, and the top-level `validation-gate.json`,
`consolidated-track2.csv`, `TRACK2-SUMMARY.md`); `score_uplift_canonical_gt.py`
(TM-n10-k5); `adapt_track2_evals_for_manifest.py` (the eight
`evaluation.json`; on the committed summaries it reproduces all eight
byte for byte). Prediction: S9 § 4.3 and
`s9-staleness-sweep-scripts/records/engine-A.json` (one reviewer-promoted
phantom fewer at every R ≥ 50 m; F1 at 50 m, for example IM-k3 0.798699 →
0.798780). The engine's MCC intervals have **no prediction** (the
sub-agent saw them move at every buffer in one 10,000-resample run; the
adapter does not carry them into `evaluation.json`).

**B. The uplift supplement** (`results/uplift-supplement/`; D62 (6),
D65 (4)), last in the pass:

1. **Replay of the flatten at `741a4eaff`** (D62 (6), closing W2-5): run
   twice by the sub-agent on that commit's code and data. `conditions.csv`,
   `conditions-by-buffer.csv`, `strata.csv` and `transfer-pairs.csv` are
   byte-identical across both runs, to `741a4eaff`, and to `main`;
   `column-spec.json` differs only in `generated_at`, and
   `notation-extension-proposal.md` and `build-report.md` only in their
   dated banner lines (`main`'s `build-report.md` adds 13 hand-written
   lines, the 2026-09-20 IM-k4 note). This agent re-checks the replay's
   records before the record states it as done.
2. **The 21 grid-common verifier-uplift twins on the origin route**
   (D65 (4)): 19 are union twins (16 cells' unions at their condition's
   vote threshold, and the three winner-ladder rungs), made by
   `materialise_pairing_twin.py --union` from unions that hold only a
   legacy `source_tile`; 2 read the registered 384/50 K = 10 consensus
   condition, which the GS chain regenerates. No committed generator has an
   origin mode, so a pass driver re-materialises each union twin through
   its cell's own origin-route loader at probability 0 and vote ≥ k and
   scores it with its committed recipe, in place (D58 Q4). Prediction: the
   re-score's `twins.py` (16 twins) and the sub-agent's probe (the three
   ladder twins: 0.4459 → 0.4552, 0.5436 → 0.5553, 0.5256 → 0.5367).
3. **The pairing statistics** (`compute_verifier_uplift.py --metric F1`
   and `--metric MCC`) on the committed 170-pair worklist (not rebuilt:
   rebuilding would add 66 pairs, a membership change this pass does not
   make), with the 21 verified conditions at their registered points.
4. **The flatten, regenerated once** (`build_uplift_supplement.py`, after
   the manifests are regenerated), with the 2026-09-20 note moved into
   `REVISION_ENTRIES` so the build keeps it.

Two findings of the inventory change what this lane can predict, and are
reported as surprises (§ 5) rather than absorbed:

- the committed pairing CSVs are stale against their own committed twin
  evaluations (D57 (4) re-scored 33 pairing twins and 36 gap-fill cells on
  2026-10-09 without re-running `compute_verifier_uplift.py`), so the
  re-score's "+0.2631 median unchanged", computed by substituting into the
  committed CSV, is not the prediction; the sub-agent's recomputation is
  (F1 median +0.2562, range −0.0366 to +0.5232, 3 negative; tile-MCC 167 of
  170 computed, median +0.4936, range −0.0038 to +0.8410, 1 negative);
- the flatten's signed counts were stale before this pass (the outcome's
  441 conditions and 79 board-frame exclusions match the 2026-09-10 build;
  the committed artefact has 439 and 153), and today's generator adds the
  66 conditions registered since (505 conditions, 130 strata, 153
  excluded). It also empties `cost_usd` on 126 rows, which is not yet
  attributed: **the flatten is not regenerated until that is attributed**.

### 1.7 Modality bridge lane (sub-agent)

Inventory by an Opus sub-agent (`~/scratch/s164-restate-2026-10-15/lane-bridge/`),
with a trial of every generator on the re-verified rows. The bridge
(`results/modality-bridge-2026-10-07/`, unregistered; claim rows R7.3-22 and
R7.3-23) has three generators:

| Artefact | Generator | Prediction |
|---|---|---|
| the ten cells (44 files), `gap_test.json`, `k5/`, `additions/`, 13 logs | `scripts/modality-bridge-2026-10-07-score.sh` (ten `image_b_analysis.py --six-cell-gate` calls, three `gemini37_image_gap_test.py --six-cell-gate` calls; the text-B anchor is the dated default 0.9017) | re-score § 3.3 REPAIRED; file level the REPAIRED copy's bridge directory, except `g3_gap_committed` (now the dated +0.0559) |
| `floors/` (§§ 5–7: gap changes, date components, floors) | `modality_bridge_floors.py --scoring-root outputs/modality-bridge-2026-10-07 --out-dir …/floors` | the sub-agent's trial (no record measured them) |
| `verifier-sd/` (§ 7a) | `modality_bridge_verifier_sd.py --floors-dir …/floors --out-dir …/verifier-sd` | the sub-agent's trial |

**The floors and verifier-SD scripts are off the origin route** (as
`scorer-restatement-inventory.md` listed for the bridge): they rebuild the
cells' sets from unions with a legacy `source_tile` and cluster their rungs
without members, so on the re-verified rows their gate 1 refuses (replicate 1
scores 0.010–0.018 below the restated cells), and the rows they re-key to the
neighbouring sheet are exactly the re-verified rows (17, 34, 12, 8, 10, 16
and 35 per arm). They are fixed before they run: each union through
`union_on_origin` after `load_image_union`, and each rung clustered with its
members and booked on its origin sheet (`image_b_analysis.py`'s own ladder
mechanism), with a tier-1 test and a red sentinel. The six-cell anchor gate
keeps reading the legs as run. Under D58 Q6 the fixed scripts must first
reproduce the committed floors and verifier SD on the bridge's data as run
(data at `be252e57b`); the sub-agent's quick check reproduced all 20 sets.

**D65 (6)'s date caveat.** The only date field in the bridge's outputs is the
verifier-SD script's `replicate_dates` (2026-10-07 and 2026-10-08); the 486
re-verified rows of the 30 bridge legs (162 per replicate; US$0.383286) were
re-verified on 2026-10-13, in one batch job per verifier (396 Gemini 3
rows and 90 Gemini 3.7 rows; `outputs/wrong-sheet-reverify-2026-10-13/record.json`,
`rows[].job`; "one batch job" corrected 2026-10-15, § Changelog). Both scripts gain a
`reverification` record beside it (date, record path, rows per leg), and the
findings say it where the dates are used (§§ 1, 7, 7a).

The trial changes readings, not only numbers, and they are reported as
surprises (§ 5): § 7's "none clears its upper bound" fails (the two
K-matched gap changes clear theirs, 1.09 and 1.01), the Gemini 3 T 1.0 text
advantage falls inside its upper bound (1.03 → 0.98), § 7a's three
sub-unit "each cell at its upper" readings become one, and the 3.7 image
carried original's § 6 "oracle" is its registered point, not its new best.

### 1.8 Register, manifests, and documents (this agent, last)

Executed last, by this agent, after every lane had committed:

1. **Register.** Every signed row was audited against the artefacts at
   the branch point and at the head (an Opus sub-agent, read only;
   § 3). Fifteen rows quote numbers or verdicts the pass moved; their
   signatures lapse through `lapse_signatures.py` (status
   `re-sign-pending`, `signed_at` null, the prior signature in
   `history`, a dated D9-pattern note drafted by Claude and NOT YET
   APPROVED appended to `attests`). The drafted notes are in
   `restatement-pass-scripts/records/register/` (`lapse-notes-gs.json`,
   `lapse-notes-extra.json`); the drafted outcomes are
   `drafted-outcomes-final.json`, rendered in § 4.
2. **Documents** restated in place under the Document Revision Policy
   (§ 9), each with a dated banner and changelog entry.
3. **Manifests, registry, renderings** regenerated and checked (§ 8),
   after merging `origin/main` (no file overlapped the branch's).
4. **Tier-1** at the head, one process; `ruff check` on the touched
   Python and `markdownlint-cli2` on the touched Markdown (§ 7).

## 2. Per lane: COMMITTED → PREDICTED → REGENERATED

Each lane ran twice in independent disposable copies; § 7 gives the
two-run comparisons. "= prediction" means every compared value equals the
prediction named in the lane's plan section; each mismatch is flagged
**MISMATCH** and explained.

### 2.1 GS chain (§ 1.2; `f6f10d605`)

Grid, stride, plateau, Image-B, Gemini 3.7 / 3.8 screen, fourth-cell and
3.7 image chains, their registered conditions, the grid selection-aware
pilots, and the sensitivity table. Run A equals the 2026-10-13 re-score's
REPAIRED copy file for file, except where this pass meant it to differ:

| Where it differs from the REPAIRED copy (by design) | REGENERATED |
|---|---|
| Grid 384/12.5 registered condition, kept at its point (D65 (3)) | (0.20, k7) F1 0.8752, 365 detections (argmax (0.15, k7), 0.8761) |
| Stride 512/34.4 registered condition | (0.15, k6) 0.8714, 396 (argmax (0.15, k7), 0.8718) |
| 3.7 image carried arm's registered set (`op-eval/`) | (0.10, k5) 0.9353, 438 (argmax (0.05, k5), 0.9381) |
| Grid best-point sets (`verified-best/`, new) | byte-equal to the re-score's argmax condition sets |
| Text-B anchor `ANCHOR_F1_20` (dated, D58 Q6) | 0.8961 → 0.9017 |
| `stride_verified_conditions.json` | new |

Each registered point equals its predicted sweep row. The selection-aware
pilots and the sensitivity table had no prediction; their apparent F1
equals the restated consensus best. The headline values are the REPAIRED
column of the re-score's § 3 table (`rescore-repaired-gs.md`), for example
the post-verifier grid board 0.8961 / 0.8815 / 0.8677 / 0.8311 →
0.9017 / 0.8870 / 0.8761 / 0.8368, and Image-B's text − image gap
+0.0549 (p 0.0010) → +0.0559 (p 0.0005). **No mismatch.** The eleven
findings documents restated from these outputs (`d6e2f40e8`) carry the
full before → after tables in their changelogs.

### 2.2 Era-2 board (§ 1.3; `8412f34bb`)

| Quantity | COMMITTED | PREDICTED (re-score § 3.1, REPAIRED) | REGENERATED |
|---|---|---|---|
| Cells admitted / tiered / withheld | 153 / 150 / 3 | = | = |
| Significant pairs of 11,175 | 7,961 | 8,075 | 8,075 |
| F1 tiers | 14 | 14 | 14 |
| Tier 1 | the five 3.7 cells | the same five, same order | the same five, same order |
| F1 MCB admissible set | 65 | 52 | 52 |
| Ranks 1–5 | 0.9233, 0.9190, 0.9182, 0.9179, 0.9068 | 0.9332, 0.9289, 0.9282, 0.9278, 0.9169 | = prediction |
| Tile-MCC family (pairs, tiers, tie set, MCB) | 2,982, 6, 33, 59 | 3,001, 6, 34, 60 | = prediction |
| Grid 384/50 verified (F1, rank, tier) | 0.8886, 11, 2 | 0.8942, 9, 3 | 0.8942, **11**, 3 |
| Pair rows (difference, p, BH p, decision) | — | 11,175 rows | all 11,175 identical to the prediction |

**MISMATCH (display only).** The board's ranking column shows each
member's evaluation F1. The S9 re-score of tier E's four cells
(`64382beea`, § 2.3) came after the prediction, which still showed their
committed evaluations, so in the regenerated board they display 0.8680,
0.8673, 0.8979 and 0.9046 (K = 1 opmax, K = 1 carried, K = 3, K = 5),
rise to ranks 43, 44, 9 and 8, and three take a new tier label (K = 1 both
5 → 4, K = 3 3 → 2; K = 5 keeps 2); 18 other members shift one or two
ranks. Every pairwise test is identical to the prediction; tier labels
follow the ranking order. Against the committed board nine tier labels
change (the board's changelog lists them). Record:
`restatement-pass-scripts/records/board/runA-vs-prediction.txt`.

**Sweep optimism** (`optimism/`, no prediction): regenerated on the fixed
builder (`92889e0e5`). The first runs stopped at the **fourth cell's**
board-frame anchor gate, which § 1.3 did not foresee: on the board frame
its sweep argmax moved from the registered (0.98, k10), 0.9141, to
(0.95, k10), 0.9144 (its own GS frame's argmax stays (0.98, k10)). That
run resumed without the gate, as the 3.7 image carried arm's was planned
to (driver change committed with the board). The first run's per-step log
was overwritten by the resume; its `rc=1` survives in `chain.first.out`,
and the argmax is read from the resumed run's log (`selected: p0.95-k10`,
`apparent f1 0.9144`).

**Membership**: kept; `committed_f1_20` refreshed for 17 members (the ten
above and the seven S9 cells) and the 3.7 image carried arm re-pointed to
its registered set, in `membership.json`'s `_restated` block.

### 2.3 K-ladder lane (§ 1.4; `1608a7604`, `a9eb8ff83`, `64382beea`, `f53f6e97c`, `0fc2d6389`)

| Step | COMMITTED → REGENERATED | Against the prediction |
|---|---|---|
| 1. Eight S9 cells | tier E K = 1 0.8546 → 0.8680, K = 3 0.8840 → 0.8979, K = 5 0.8905 → 0.9046; 3.7 K = 1 0.8495 → 0.8747, K = 3 0.8860 → 0.9135 (unclipped) | = S9 replay on every summary and per-run leaf |
| 2–4. GS stride A board frame; tier E K = 10; tier E tiering; MCB; MCC test | GS stride A 0.8665 / 0.8916 / 0.8862 / 0.8999; tier E K = 1 / 3 / 5 / 10 0.8680 / 0.8979 / 0.9046 / 0.8942, 3 of 6 pairs significant; tier E tile-MCC MCB set now the whole ladder (12 → 13 ladders) | = re-score § 3.2 |
| 3. 3.7 opmax rungs (fixed derivation) | (0.10, k5) 0.9165, (0.10, k10) 0.9169; no argmax moved; carried cross-check 443 → 451 (dated) | = the lane's trial |
| 5. Phase 2 tables (clipped basis) | seven ladders reported clipped, tile-MCC withheld on them; 3.7 GS ladder K = 1 0.8495 → 0.8682, best 0.9068 → 0.9169 (K = 10), share of the gain at K = 3 0.6545 → 0.8029; Gemini 3 HIGH text T 1.0 best 0.8804 → 0.8765; MINIMAL image T 0.7 0.7881 → 0.7852 | = the values § 1.4 quotes; **MISMATCH** with the trial's own file, explained below |
| 6–7. Phase 1 tables, inventory values, tension | § 8.6's share about 60 % (60.3 %), swing 0.0682 | = re-score § 3.2 |
| 7 again, after step 5 (`62050794d`) | `tension/effect-sizes.json` on the clipped Phase 2 tables: MINIMAL image T 0.7 gain 0.0629 → 0.0600; unclipped-basis fields withheld on five rows; `grid-overlap.json` unchanged | **MISMATCH (order)**: part 2 had run step 7 before step 5, against the plan's order |

**Step 5.** The trial's clipped build (`lane-kladder/out/builder/clip/`)
predates the S9 re-score, row 28's fix and the restated 3.7 cells, so 118
leaves of its `ladders.json`, all in the 3.7 GS ladder and its summary,
differ from the regenerated file; the plan's quoted values, which already
carried those changes, match. Four earlier pairs of step 5 runs failed or
were discarded: three on missing inputs in a partial copy, and the fourth
because the partial copy left every ladder's assessed area UNDETERMINED,
which `--allow-undetermined-area` let through unclipped (0 ladders clipped
where the trial clipped 7). The runs used are whole-tree copies
(`kl_phase2_run.sh`, `2012ff6a8`). Record:
`restatement-pass-scripts/records/kladder/phase2-compare.txt`.

### 2.4 Pairwise lane (§ 1.5; `08af04cf3`)

The 32 comparisons at 20 m and 30 m, both leaderboards, the factor
analysis, and e45 with its H2 rerun and H3 tiering: every value equals its
prediction (PR #37's NEW 20 m and 30 m runs, 36 of 36 each; its 1,260 arm
values; the S3 record's H3 tiering; the inventory's trial for the rest).
H2's e45 interval moves to +0.073730 [+0.048250, +0.101597] at
B = 10,000; no BH decision changes among the 32 comparisons; the
leaderboards keep their tiers (20 m 265 of 325 significant; 30 m 243 →
240). The 100 per-pair files that read the drifted single-pass arms stay
as March records with today's runs beside them under
`results/rescore-2026-10-15/pairwise/` (D61 (2)). **No mismatch.**

### 2.5 Uplift supplement and extended-reference lane (§ 1.6; `ad6380c63`, `e66eb0243`, `645c6e4b0`)

| Artefact | COMMITTED → REGENERATED | Against the prediction |
|---|---|---|
| 19 grid-common union twins (origin route) | F1 at 20 m rises on all 19, by +0.0067 to +0.0183; 154 rows re-booked; none dropped | = the re-score's `twins.py` and the inventory's probe |
| Eight 55-map extended-reference cells | one reviewer-promoted phantom fewer at R ≥ 50 m: F1 at 50 m +8e-05 to +9e-05 (IM-k3 0.798699 → 0.798780); precision, tile confusion and MCC unchanged | = the S9 engine replay on every point; **MISMATCH (unpredicted)**: the engine's MCC intervals in `summary.json` and `consolidated-track2.csv` move too |
| Flatten | conditions 439 → 505, 130 strata, 153 board-frame rows excluded | = the uplift inventory |
| Pairing (F1, tile MCC) | F1 median +0.2631 → +0.2562, range −0.0366 to +0.5232, 3 negative; tile MCC 167 of 170 computed, median +0.4936, range −0.0038 to +0.8410, 1 negative | = the uplift inventory |

The 3.7 image carried arm's uplift is negative (−0.0017 F1), which D65 (4)
asked to report.

### 2.6 Modality bridge lane (§ 1.7; `02339bd98`, `d6111dafb`)

| Artefact | COMMITTED → REGENERATED | Against the prediction |
|---|---|---|
| Ten cells (44 files), 13 logs | restated, for example the Gemini 3 K = 10 gap +0.0536 (p 0.0018) | = the re-score's REPAIRED copy, 44 of 44 byte-identical |
| `gap_test.json`, `k5/`, `additions/` | restated | = REPAIRED apart from `g3_gap_committed`, now the dated {+0.0559, 0.0005} (by design, `fc45ed53c`) |
| `floors/` | gate 1 passes on the origin route; two K-matched gap changes clear their upper floors (1.09, 1.01) | = the lane's trial apart from `meta` |
| `verifier-sd/` | one sub-unit "each cell at its upper" reading instead of three | = the lane's trial apart from `meta` |

D58 Q6: the fixed scripts reproduce the committed `floors/` and
`verifier-sd/` on the bridge's data as run (code `d083d3c99` plus the fix,
data `be252e57b`) apart from `meta` and added provenance fields; no value
changes (`records/bridge/q6-compare-*.json`). The tier-1 tests (seven in
`tests/test_modality_bridge_origin.py`) all fail in a real-file copy of
the previous scripts (`records/bridge/origin-fix-sentinel.txt`). The four
changed readings are surprises (§ 5). A review of the drafted findings
against the artefacts (about 400 changed numbers) found three slips and a
rounding, corrected before the commit: § 6's 9.5 % is 9.4 % (0.094456),
the 486 rows went in two batch jobs (396 Gemini 3 rows, 90 Gemini 3.7
rows) and not one, § 8 lists four changed readings and not five, and the
restated all-3.7 gap prints −0.0044 (unrounded −0.0043504), which also
corrected the 3.7 image findings (`94d5815b3`). "US$94.52" → "US$94.53"
is in (`w1-8-cost-audit-summary.json`, `totals.all` 94.526841875).

## 3. Per signed analysis: verdicts and signatures

A signature attests a row's text, so it lapses when a number or verdict
that text quotes moves. Every row signed at the branch point was audited
against its artefacts at `718d0ee08` and at the head (Opus sub-agents,
read only); the re-score's § 3 table was the starting prediction and is
confirmed except where noted.

| Row (lapsed) | What moved, COMMITTED → REGENERATED | Verdict | § 4 |
|---|---|---|---|
| `grid-tilesize-overlap-2026-08-18` | the consensus-only board on the origin route, as PR #42 reported (K = 10 0.7611 / 0.7293 / 0.6845 / 0.6574) | survives (512 px wins at every K); numbers restate | 4.1 |
| `grid-postverifier-2026-08-18` | board 0.8961 / 0.8815 / 0.8677 / 0.8311 → 0.9017 / 0.8870 / 0.8761 / 0.8368; tile size at 12.5 % +0.0366 → +0.0393 (p 0.0266); overlap at 384 px −0.0285 [−0.0530, −0.0045], p 0.0235 → −0.0256 [−0.0517, +0.0001], p 0.0541 | **the overlap reversal at 384 px FAILS** (it holds at 512 px, −0.0502, p 0.0003) | 4.2 |
| `stride-winner-ladder-exact-2026-08-25` | N = 1, 3, 5 against K = 10: 0.8677, 0.8911, 0.8856 against 0.8982 → 0.8737, 0.8993, 0.8937 against 0.9075 | survives (N = 3 − K = 10 −0.0083, p 0.2275) | 4.3 |
| `image-b-modality-2026-08-28` | IP1 +0.0549 (p 0.0010) → +0.0559 (p 0.0005); IP3 MCC 0.7985 against 0.7965 → 0.8139 against 0.8037 | survives | 4.4 |
| `image-b-thinking-pair-2026-08-28` | HP1 −0.0079 (p 0.62) → −0.0068 (p 0.668); HP3 MCC +0.0008 → −0.0031 | HP1–HP4 survive; HP5 a narrow miss, as before | 4.5 |
| `gemini37-screen-2026-08-28` | carried K = 5 0.9139, +0.0178 (p 0.1697) → 0.9238, +0.0221 (p 0.0971); K = 10 0.9142 → 0.9243 | survives | 4.6 |
| `gemini37-image-gs-2026-09-01` | carried-pair gap −0.0115 (p 0.2533) → −0.0143 (p 0.158); all-3.7 gap −0.0043 → −0.0044 (p 0.677) | **I3 FAILS on the carried arm**: its optimum is (0.05, k5), 0.9381, not the registered (0.10, k5), 0.9353 | 4.7 |
| `gemini37-fourth-cell-gs-leg-2026-08-31` | 0.9140 → 0.9220; head-to-head +0.0179 (p 0.0563) → +0.0203 (p 0.0311) | survives; the p crosses 0.05, and the text claims no significance | 4.8 |
| `gemini38-screen-armv-2026-09-04` | 0.9258 → 0.9358 (n 421 → 429); against carried +0.0119 (p 0.0969) → +0.0120 (p 0.0764) | survives | 4.9 |
| `e45-bootstrap-pairings` | H2's interval → +0.073730 [+0.048250, +0.101597] (B = 10,000) | survives; "reproduced bit-for-bit by a blind verifier" now dated to the 2026-08-17 values | 4.10 |
| `gs-era2-verified-board-2026-09-10` | § 2.2; G6 0.0078 → 0.0079; withheld cells 0.8338 / 0.8495 / 0.8860 → 0.8616 / 0.8747 / 0.9135 | structure survives; numbers restate; F1 MCB 65 → 52 | 4.11 |
| `k-ladder-2026-09-12` | GS ladder MCC +0.0135 (BH p 0.7678) → +0.0131 (0.7633); § 8.6 40.6 % → 60.3 %, swing 0.0752 → 0.0682; tile-MCC counts on the clipped basis (21 / 16 → 15 / 10); whole-ladder MCC sets 12 → 13 | shape and MCC readings survive; **§ 7.4's "dearest last step" fails** (the 3.7 step is about US$22 per 0.001 F1; the 55-map 3.7 arm 1's K = 3 → 5 is about US$27) | 4.12 |
| `verifier-uplift-pairing` | MCC pairs 169 → 167; F1 median +0.2631 → +0.2562, maximum +0.5265 → +0.5232, negatives 2 → 3; MCC median +0.4975 → +0.4936, minimum −0.0230 → −0.0038, negatives 3 → 1 | restates | 4.13 |
| `uplift-supplement-flatten` | conditions 439 → 505 (the text's "441 … 79 board-frame rows" was already stale at the branch point: 439 and 153) | restates | 4.14 |
| `null-exemplar-sensitivity-2026-09-13` | its quoted full-frame figures are the board's (7961, 2982, 33, 65, 59), which moved; its own analysis was not re-run | the redraft qualifies those figures rather than replacing them | 4.15 |

**Holding (30 rows).** Twenty-seven signed rows rest on artefacts the pass
did not change. Three rest on changed artefacts but quote nothing that
moved: `tile-level-f1` (its tile matrices are unchanged),
`stride-plateau-2026-08-25` (its outcome quotes the tier structure, which
survives verbatim; a claim-row check suggested it lapse, but it quotes no
30 m reading) and `sensitivity-mde-2026-08-28`. No signed row quotes the
eight 55-map extended-reference cells.

## 4. Drafted outcomes for the PI (not applied)

For each of the fifteen lapsed rows: the drafted new `outcome`, then a
word-level diff against the register's current text in
`[-removed-]{+added+}` form (`git diff --word-diff=plain`'s convention).
Interval brackets inside the text, as in `[-0.0517, +0.0001]`, are content
and can sit next to the diff markers; read the fenced text for the
clean wording. Rendered by `restatement-pass-scripts/outcome_diffs.py`
from `records/register/drafted-outcomes-final.json`. Nothing here is in
the register: each row's `outcome` is unchanged and its signature is
pending.

**Checks.** The ten rows of `ed91d2df8` were verified number by number
against the regenerated artefacts by a separate Opus sub-agent: eight
passed; two carried stale wording, corrected here — the grid
post-verifier row's dated `[REVISED 2026-08-24]` block kept old figures
and "the overlap conclusion is unchanged", so a dated
`[RESTATED 2026-10-15 …]` clause now follows it, and e45's "reproduced
bit-for-bit by a blind verifier" is dated to the 2026-08-17 values (the
regenerated values were not blind-verified). The five rows of
`92a66089d` were drafted from the artefacts at the head and revised once
the Phase 2 tables were committed; the K-ladder draft writes the last-step
price in the correct unit (about US$22 per 0.001 F1) and its lapse note
says the signed "US$1,100 to US$43,000" carries the 1,000× slip recorded
on 2026-10-04.

**The alternative reading of § 1.1 item 1.** The stride board reads each
grid cell's best point (384 px at 12.5 % overlap: (0.15, k7), 0.8761); the
alternative, taking the registered set at (0.20, k7), would read 0.8752
for that cell. It was not run.

### 4.1 `grid-tilesize-overlap-2026-08-18`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
Post-hoc (E41-class) 2x2 tile-size x overlap grid, proposer stage only,
consensus-only aggregation, 10 passes per cell, one configuration
throughout (detect_brief-text, gemini-3-flash-preview, MINIMAL, T=0.7;
30,130 calls, $18.53 billed). Scored on the four-way tile-union
intersection carried on the era-2-487 grid (487 carrier tiles, 20 m
buffer), with the preregistered 20 m within-pass deduplication applied
to every pass so denser tilings are not penalised for cross-tile
duplicates. Best cell per configuration at K=10: 512 px / 12.5 % F1
0.6845 [0.6336,0.7313] MCC 0.5431; 512 px / 50 % F1 0.7611
[0.7126,0.8023] MCC 0.5853; 384 px / 12.5 % F1 0.6574 [0.6038,0.7056]
MCC 0.3066; 384 px / 50 % F1 0.7293 [0.6841,0.7686] MCC 0.4909. TWO
STANDING PRIORS OVERTURNED. (1) 512 px wins at every overlap and every
K, so the 384 px sweet spot does NOT reproduce under one footprint at
T=0.7: tile-size effect -0.0803 at 12.5 % [-0.1236,-0.0394] and -0.0976
at 50 % [-0.1206,-0.0752], both excluding zero. (2) Passes do NOT
substitute for overlap: 384 px / 12.5 % at K=10 loses to 512 px / 50 %
at K=3 by 0.0304 union recall and 0.0926 best F1, at lower cost. NOTE
THE SIGN ON OVERLAP: the paired contrasts are computed on run-averaged
single-pass per-tile counts with NO consensus filter, so (12.5 % - 50 %)
= +0.1207 at 512 px and +0.1381 at 384 px means 50 % overlap COSTS about
0.12-0.14 F1 at a single pass. Overlap reverses and becomes the most
valuable factor in the grid only once the corroboration filter it
creates is switched on -- which is why the best cell is a 50 % one. Tile
size never reverses. The interaction is UNRESOLVED:
difference-of-differences -0.0173 [-0.0580,+0.0248], p=0.4033, spanning
zero. ALL OF THIS IS CONDITIONAL ON THE ABSENCE OF A PRECISION STAGE: no
verifier has run over any grid cell, so whether the tile-size ranking
and the overlap effect survive verification is untested (recall-levers
programme Phase 1, $6.33). Bootstrap intervals here are at B=10,000 per
the 2026-08-19 PI ruling (erratum E82), not the 1,000 Decision 10
pre-specified; the paired contrasts use the analysis script's own
resampler, which was never on the D15 defective path, so re-running them
at 10,000 moved every delta by 0.00000, every CI width by under 5 %, and
no significance verdict. Two of 228 swept cells have an undefined tile
MCC, reported as null and never as 0.0 (E81). Artefacts:
results/grid-2026-08-18/{grid_analysis.json,sweep.csv,findings.md} and
the four per-cell evaluations under results/grid-2026-08-18/conditions/;
scripts grid_prepare_scoring.py, grid_analysis.py,
grid_materialise_conditions.py.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
Post-hoc (E41-class) 2x2 tile-size x overlap grid, proposer stage only,
consensus-only aggregation, 10 passes per cell, one configuration
throughout (detect_brief-text, gemini-3-flash-preview, MINIMAL, T=0.7;
30,130 calls, $18.53 billed). Scored on the four-way tile-union
intersection carried on the era-2-487 grid (487 carrier tiles, 20 m
buffer), with the preregistered 20 m within-pass deduplication applied
to every pass so denser tilings are not penalised for cross-tile
duplicates. Best cell per configuration at K=10: 512 px / 12.5 % F1
[-0.6759 [0.6239,0.7237]-] {+0.6845 [0.6336,0.7313]+} MCC [-0.5383;-]
{+0.5431;+} 512 px / 50 % F1 [-0.7518 [0.7026,0.7938]-] {+0.7611
[0.7126,0.8023]+} MCC [-0.5897;-] {+0.5853;+} 384 px / 12.5 % F1
[-0.6475 [0.5935,0.6966]-] {+0.6574 [0.6038,0.7056]+} MCC [-0.3137;-]
{+0.3066;+} 384 px / 50 % F1 [-0.7205 [0.6749,0.7618]-] {+0.7293
[0.6841,0.7686]+} MCC 0.4909. TWO STANDING PRIORS OVERTURNED. (1) 512 px
wins at every overlap and every K, so the 384 px sweet spot does NOT
reproduce under one footprint at T=0.7: tile-size effect [--0.0824-]
{+-0.0803+} at 12.5 % [-[-0.1243,-0.0429]-] {+[-0.1236,-0.0394]+} and
[--0.0972-] {+-0.0976+} at 50 % [-[-0.1196,-0.0753],-]
{+[-0.1206,-0.0752],+} both excluding zero. (2) Passes do NOT substitute
for overlap: 384 px / 12.5 % at K=10 loses to 512 px / 50 % at K=3 by
0.0304 union recall and [-0.0953-] {+0.0926+} best F1, at lower cost.
NOTE THE SIGN ON OVERLAP: the paired contrasts are computed on
run-averaged single-pass per-tile counts with NO consensus filter, so
(12.5 % - 50 %) = [-+0.1200-] {++0.1207+} at 512 px and [-+0.1348-]
{++0.1381+} at 384 px means 50 % overlap COSTS about [-0.12-0.13-]
{+0.12-0.14+} F1 at a single pass. Overlap reverses and becomes the most
valuable factor in the grid only once the corroboration filter it
creates is switched on -- which is why the best cell is a 50 % one. Tile
size never reverses. The interaction is UNRESOLVED:
difference-of-differences [--0.0148 [-0.0552,+0.0268], p=0.4902,-]
{+-0.0173 [-0.0580,+0.0248], p=0.4033,+} spanning zero. ALL OF THIS IS
CONDITIONAL ON THE ABSENCE OF A PRECISION STAGE: no verifier has run
over any grid cell, so whether the tile-size ranking and the overlap
effect survive verification is untested (recall-levers programme Phase
1, $6.33). Bootstrap intervals here are at B=10,000 per the 2026-08-19
PI ruling (erratum E82), not the 1,000 Decision 10 pre-specified; the
paired contrasts use the analysis script's own resampler, which was
never on the D15 defective path, so re-running them at 10,000 moved
every delta by 0.00000, every CI width by under 5 %, and no significance
verdict. Two of 228 swept cells have an undefined tile MCC, reported as
null and never as 0.0 (E81). Artefacts:
results/grid-2026-08-18/{grid_analysis.json,sweep.csv,findings.md} and
the four per-cell evaluations under results/grid-2026-08-18/conditions/;
scripts grid_prepare_scoring.py, grid_analysis.py,
grid_materialise_conditions.py.
```

### 4.2 `grid-postverifier-2026-08-18`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
Post-hoc (E41-class) proposer-verifier board for the tile-size x overlap
grid: the four committed K=10 unions (c>=1, k>=1;
1,402/2,585/1,827/3,319 candidates, documented counts reproduced EXACTLY
at materialisation) verified by the study's carry-forward adversarial
text verifier (gemini-3-flash-preview, T=0.0, MINIMAL, n=1; 9,133/9,133
verified, ZERO failures; metas $12.5428 list -> $6.2714 expected flex
billed vs $6.33 costed, -$0.06), then thresholded on (mound_probability,
vote_count) and scored for $0 with the grid's own machinery on the
common 487-tile footprint at 20 m (580-row prob_t x k sweep). Best per
cell (best-F1@20m; BCa CI95 at B=10,000): 384/50 p>=0.15 k>=10 F1 0.9017
[0.8727,0.9244] MCC 0.8037; 512/50 p>=0.15 k>=9 F1 0.8870
[0.8583,0.9118] MCC 0.8087; 384/12.5 p>=0.15 k>=7 F1 0.8761 MCC 0.7852
(the registered condition keeps p>=0.20 k>=7: F1 0.8752 [0.8424,0.9017]
MCC 0.7852); 512/12.5 p>=0.15 k>=5 F1 0.8368 [0.7995,0.8676] MCC 0.8011.
BOTH QUESTIONS THE CONSENSUS-ONLY BOARD LEFT OPEN ARE SETTLED, THE
SECOND AT 512 PX ONLY. (1) The tile-size ranking REVERSES under the full
pipeline: (384-512) = +0.0393 [+0.0052,+0.0741] p=0.0266 at 12.5%
overlap — excluding zero on the OPPOSITE side of the consensus-only
-0.0803 — and +0.0147 [-0.0095,+0.0394] p=0.2454 at 50% (sign reversed,
unresolved). The consensus-only '512 px challenge' to the study's 384 px
preference was a truncated-pipeline artefact: the verifier recovers the
precision 384 px lacked, while the 384 px cells' higher union-recall
ceilings (0.9112/0.9696 vs 0.8879/0.9603) are the resource a verifier
cannot create — the Obs 352 rescue mechanism at a new tile-size pair.
(2) The overlap reversal SURVIVES the verifier at 512 px but FAILS at
384 px: 50% wins significantly at 512 px ((12.5-50) = -0.0502
[-0.0778,-0.0224] p=0.0003) but not at 384 px (-0.0256 [-0.0517,+0.0001]
p=0.0541, the interval reaching +0.0001), at roughly HALF the
consensus-only margin — the corroboration filter and the verifier are
partially redundant, and the surviving advantage tracks the
recall-ceiling edge, as the findings doc predicted. Interaction
unresolved (-0.0246 [-0.0613,+0.0114], p=0.1831). CONSENSUS AND VERIFIER
ARE COMPLEMENTS, NOT SUBSTITUTES: every cell's best operating point
retains a vote threshold (k>=5..10) atop the probability threshold; the
pure-verifier k=1 board tops out at 0.8187 (384/12.5) and trails the
stacked optimum in every cell by 0.057-0.207. The 384 px tile-MCC
saturation pathology dissolves post-verifier (all four cells MCC
0.785-0.809; F1 and MCC rankings broadly agree). Verifier gain over the
consensus-only board +0.126..+0.219 best-F1, largest where
consensus-only was worst (the 384 px cells). GATES, all passed: exact
union-count reproduction at materialisation (stop rule); contiguous
candidate-key join; carrier-tile reassignment after the CRS round-trip;
each unthresholded union re-scores to its committed sweep row (<=1e-6);
each materialised condition reproduces its sweep F1 to <=5e-5 at
B=10,000. The paired tile-bootstrap contrasts are the significance
instrument (Decision 10 resampler, B=10,000 per E82, seed 42, integer
per-tile counts of each single verified set); per-cell CIs are register
metadata. Best-F1 operating points are selected on the same ground truth
they are scored on, as on the consensus board (E41-class calibration
caveat). Artefacts:
results/grid-2026-08-18/{verifier_analysis.json,verifier_sweep.csv} and
findings.md section 'The verifier stage, run'; the four evaluations
under results/grid-2026-08-18/conditions-verified/; verifier inputs and
raw outputs under outputs/grid-2026-08-18/verifier/ (committed
8eda1e3a3); scripts materialise_grid_unions.py,
grid_verifier_analysis.py. [REVISED 2026-08-24, same-day audit (commits
57b7ad7ad/0a6bde47f): the pre/post tile-size framing above cites the
single-pass contrasts (-0.0824/-0.0972, both significant), which
run-average ten passes and are not the like-for-like baseline for a
single aggregated operating point. The proper pre-verifier arm — the
registered K=10 best consensus-only operating points on the same
instrument, now published as bootstrap_contrasts_consensus_k10_baseline
— gives (384-512) = -0.0284 [-0.0813,+0.0233] p=0.281 at 12.5% and
-0.0312 [-0.0695,+0.0052] p=0.089 at 50%: BOTH NON-SIGNIFICANT. The
correct statement of the reversal is therefore: aggregation alone erodes
512px's significant single-pass advantage to non-significance, and the
verifier then flips the sign, significantly at 12.5% (+0.0366 p=0.034).
The overlap baseline is -0.0758 p=0.0004 / -0.0730 p=0.0026, so the
overlap conclusion is unchanged. Every board value, post-verifier
contrast, and registered condition is unchanged by the audit; the join
was additionally verified at source over all 9,133 candidates against
the now-committed candidate manifests (ids contiguous in feature order,
centroids within 0.069 m against 5.6-8.0 m minimum spacing).
Selection-space caveat added to the findings doc: operating points are
F1-selected on the scored tiles, and the post-verifier sweep offers
~4-5x the consensus sweep's selection space.] [RESTATED 2026-10-15, S164
restatement pass: the block's figures are as of 2026-08-24. On the
restated sets the single-pass contrasts are -0.0803/-0.0976; the K=10
baseline gives (384-512) = -0.0271 [-0.0809,+0.0254] p=0.3081 at 12.5%
and -0.0319 [-0.0704,+0.0048] p=0.0862 at 50%, both still
non-significant; the verifier flips the sign significantly at 12.5%
(+0.0393 p=0.0266); the overlap baseline is -0.0766 p=0.0006 / -0.0718
p=0.0037, and the overlap conclusion now holds at 512 px only (see (2)
above).]
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
Post-hoc (E41-class) proposer-verifier board for the tile-size x overlap
grid: the four committed K=10 unions (c>=1, k>=1;
1,402/2,585/1,827/3,319 candidates, documented counts reproduced EXACTLY
at materialisation) verified by the study's carry-forward adversarial
text verifier (gemini-3-flash-preview, T=0.0, MINIMAL, n=1; 9,133/9,133
verified, ZERO failures; metas $12.5428 list -> $6.2714 expected flex
billed vs $6.33 costed, -$0.06), then thresholded on (mound_probability,
vote_count) and scored for $0 with the grid's own machinery on the
common 487-tile footprint at 20 m (580-row prob_t x k sweep). Best per
cell (best-F1@20m; BCa CI95 at B=10,000): 384/50 p>=0.15 k>=10 F1
[-0.8961 [0.8657,0.9198]-] {+0.9017 [0.8727,0.9244]+} MCC [-0.7965;-]
{+0.8037;+} 512/50 p>=0.15 k>=9 F1 [-0.8815 [0.8518,0.9073]-] {+0.8870
[0.8583,0.9118]+} MCC [-0.8011;-] {+0.8087;+} 384/12.5 [-p>=0.20-]
{+p>=0.15+} k>=7 F1 [-0.8677 [0.8335,0.8957]-] {+0.8761+} MCC
[-0.7751;-] {+0.7852 (the registered condition keeps p>=0.20 k>=7: F1
0.8752 [0.8424,0.9017] MCC 0.7852);+} 512/12.5 p>=0.15 k>=5 F1 [-0.8311
[0.7938,0.8624]-] {+0.8368 [0.7995,0.8676]+} MCC [-0.7937.-] {+0.8011.+}
BOTH QUESTIONS THE CONSENSUS-ONLY BOARD LEFT OPEN ARE [-SETTLED.-]
{+SETTLED, THE SECOND AT 512 PX ONLY.+} (1) The tile-size ranking
REVERSES under the full pipeline: (384-512) = [-+0.0366
[+0.0026,+0.0717] p=0.034-] {++0.0393 [+0.0052,+0.0741] p=0.0266+} at
12.5% overlap — excluding zero on the OPPOSITE side of the
consensus-only [--0.0824-] {+-0.0803+} — and +0.0147 [-[-0.0093,+0.0393]
p=0.231-] {+[-0.0095,+0.0394] p=0.2454+} at 50% (sign reversed,
unresolved). The consensus-only '512 px challenge' to the study's 384 px
preference was a truncated-pipeline artefact: the verifier recovers the
precision 384 px lacked, while the 384 px cells' higher union-recall
ceilings [-(0.8925/0.9509-] {+(0.9112/0.9696+} vs [-0.8715/0.9416)-]
{+0.8879/0.9603)+} are the resource a verifier cannot create — the Obs
352 rescue mechanism at a new tile-size pair. (2) The overlap reversal
SURVIVES the [-verifier:-] {+verifier at 512 px but FAILS at 384 px:+}
50% wins {+significantly+} at [-both sizes-] {+512 px+} ((12.5-50) =
[--0.0504 [-0.0781,-0.0224] p=0.0004 at 512 px; -0.0285
[-0.0530,-0.0045] p=0.0208-] {+-0.0502 [-0.0778,-0.0224] p=0.0003) but
not+} at 384 [-px),-] {+px (-0.0256 [-0.0517,+0.0001] p=0.0541, the
interval reaching +0.0001),+} at roughly HALF the consensus-only margin
— the corroboration filter and the verifier are partially redundant, and
the surviving advantage tracks the recall-ceiling edge, as the findings
doc predicted. Interaction unresolved [-(-0.0220 [-0.0581,+0.0141],
p=0.234).-] {+(-0.0246 [-0.0613,+0.0114], p=0.1831).+} CONSENSUS AND
VERIFIER ARE COMPLEMENTS, NOT SUBSTITUTES: every cell's best operating
point retains a vote threshold (k>=5..10) atop the probability
threshold; the pure-verifier k=1 board tops out at [-0.8153-] {+0.8187+}
(384/12.5) and trails the stacked optimum in every cell by
[-0.052-0.203.-] {+0.057-0.207.+} The 384 px tile-MCC saturation
pathology dissolves post-verifier (all four cells MCC [-0.775-0.801;-]
{+0.785-0.809;+} F1 and MCC rankings broadly agree). Verifier gain over
the consensus-only board [-+0.130..+0.220-] {++0.126..+0.219+} best-F1,
largest where consensus-only was worst (the 384 px cells). GATES, all
passed: exact union-count reproduction at materialisation (stop rule);
contiguous candidate-key join; carrier-tile reassignment after the CRS
round-trip; each unthresholded union re-scores to its committed sweep
row (<=1e-6); each materialised condition reproduces its sweep F1 to
<=5e-5 at B=10,000. The paired tile-bootstrap contrasts are the
significance instrument (Decision 10 resampler, B=10,000 per E82, seed
42, integer per-tile counts of each single verified set); per-cell CIs
are register metadata. Best-F1 operating points are selected on the same
ground truth they are scored on, as on the consensus board (E41-class
calibration caveat). Artefacts:
results/grid-2026-08-18/{verifier_analysis.json,verifier_sweep.csv} and
findings.md section 'The verifier stage, run'; the four evaluations
under results/grid-2026-08-18/conditions-verified/; verifier inputs and
raw outputs under outputs/grid-2026-08-18/verifier/ (committed
8eda1e3a3); scripts materialise_grid_unions.py,
grid_verifier_analysis.py. [REVISED 2026-08-24, same-day audit (commits
57b7ad7ad/0a6bde47f): the pre/post tile-size framing above cites the
single-pass contrasts (-0.0824/-0.0972, both significant), which
run-average ten passes and are not the like-for-like baseline for a
single aggregated operating point. The proper pre-verifier arm — the
registered K=10 best consensus-only operating points on the same
instrument, now published as bootstrap_contrasts_consensus_k10_baseline
— gives (384-512) = -0.0284 [-0.0813,+0.0233] p=0.281 at 12.5% and
-0.0312 [-0.0695,+0.0052] p=0.089 at 50%: BOTH NON-SIGNIFICANT. The
correct statement of the reversal is therefore: aggregation alone erodes
512px's significant single-pass advantage to non-significance, and the
verifier then flips the sign, significantly at 12.5% (+0.0366 p=0.034).
The overlap baseline is -0.0758 p=0.0004 / -0.0730 p=0.0026, so the
overlap conclusion is unchanged. Every board value, post-verifier
contrast, and registered condition is unchanged by the audit; the join
was additionally verified at source over all 9,133 candidates against
the now-committed candidate manifests (ids contiguous in feature order,
centroids within 0.069 m against 5.6-8.0 m minimum spacing).
Selection-space caveat added to the findings doc: operating points are
F1-selected on the scored tiles, and the post-verifier sweep offers
~4-5x the consensus sweep's selection space.] {+[RESTATED 2026-10-15,
S164 restatement pass: the block's figures are as of 2026-08-24. On the
restated sets the single-pass contrasts are -0.0803/-0.0976; the K=10
baseline gives (384-512) = -0.0271 [-0.0809,+0.0254] p=0.3081 at 12.5%
and -0.0319 [-0.0704,+0.0048] p=0.0862 at 50%, both still
non-significant; the verifier flips the sign significantly at 12.5%
(+0.0393 p=0.0266); the overlap baseline is -0.0766 p=0.0006 / -0.0718
p=0.0037, and the overlap conclusion now holds at 512 px only (see (2)
above).]+}
```

### 4.3 `stride-winner-ladder-exact-2026-08-25`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
Exact rungs: N=1 0.8737; N=3 0.8993 (~$2.64 all-in); N=5 0.8937. N=3
within noise of K=10 (0.9075) at GS scale — the pass-count saturation
the 55-map ladders later confirmed at deployment. Obs 436.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
Exact rungs: N=1 [-0.8677;-] {+0.8737;+} N=3 [-0.8911-] {+0.8993+}
(~$2.64 all-in); N=5 [-0.8856.-] {+0.8937.+} N=3 within noise of K=10
[-(0.8982)-] {+(0.9075)+} at GS scale — the pass-count saturation the
55-map ladders later confirmed at deployment. Obs 436.
```

### 4.4 `image-b-modality-2026-08-28`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
IP1-IP4 CONFIRMED (text +0.0559 @20m p=0.0005; gap 0.0559->0.0245; MCC
0.8139 vs 0.8037; prob 0.15). IP5 indeterminate at GS power (N3-N10
-0.0136 p=0.1189 — the GS indeterminate zone per the sensitivity
appendix). Image N=1 collapses (0.6998); needs near-unanimity consensus.
Obs 439.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
IP1-IP4 CONFIRMED (text [-+0.0549-] {++0.0559+} @20m [-p=0.0010;-]
{+p=0.0005;+} gap [-0.0549->0.0258;-] {+0.0559->0.0245;+} MCC [-0.7985-]
{+0.8139+} vs [-0.7965;-] {+0.8037;+} prob 0.15). IP5 indeterminate at
GS power (N3-N10 [--0.0159 p=0.069-] {+-0.0136 p=0.1189+} — the GS
indeterminate zone per the sensitivity appendix). Image N=1 collapses
[-(0.6974);-] {+(0.6998);+} needs near-unanimity consensus. Obs 439.
```

### 4.5 `image-b-thinking-pair-2026-08-28`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
HP1-HP4 CONFIRMED (HIGH -0.0068 p=0.668; union +126%; MCC -0.0031;
(0.20,k8)); HP5 narrow miss (2.91x). The verifier absorbs the thinking
dividend — the S111/Obs 359 recall-ceiling mechanism reproduced on the
image track. Obs 439.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
HP1-HP4 CONFIRMED (HIGH [--0.0079 p=0.62;-] {+-0.0068 p=0.668;+} union
+126%; MCC [-+0.0008;-] {+-0.0031;+} (0.20,k8)); HP5 narrow miss
(2.91x). The verifier absorbs the thinking dividend — the S111/Obs 359
recall-ceiling mechanism reproduced on the image track. Obs 439.
```

### 4.6 `gemini37-screen-2026-08-28`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
G1's pre-named informative outcome FIRED and G2 is falsified. The
carried-verifier K=5 cell reaches 0.9238 @20 m at (0.10, k5) on a
791-candidate union, nominally above every Gemini-3 cell on this corpus,
but the paired tile-swap permutation (10,000 draws, 487 tiles) returns
+0.0221 at p = 0.0971 against a null SD of 0.0134 — below the GS
instrument's resolution, so the screen can name the direction and not
the size. K=10 adds +0.0006 (0.9243, p = 0.1231) and the ladder's own
N5-N10 contrast is -0.0013 at p = 0.7921: saturated by N = 5, the
Gemini-3 shape exactly (0.8652 / 0.9118 / 0.9231 / 0.9243 at N =
1/3/5/10). The headline is the role swap: re-verifying the SAME 791
candidates with gemini-3.7-flash reaches 0.9364 @20 m at (0.80, k5), P
0.9268 / R 0.9463 / tile-MCC 0.8192 — +0.0347 vs the anchor, p = 0.0065,
the study's first GS-resolvable model-swap margin and the only cell in
the arc beating the anchor on F1 and MCC together. The mechanism is
calibration, not judgement: the 3.7 verifier's mean mound_probability is
0.699 against the carried verifier's 0.594 on identical candidates
(0.687 / 0.587 before the re-verified rows,
planning/gemini37-screen-2026-08-28.md:110), so its optimum migrates
four rungs up a lattice that has sat at 0.10-0.20 across every model the
study has run — G2 falsified, and the portable claim is that a
verifier's operating threshold does not transfer across verifier models.
Cost ordering is the practitioner lesson: five extra passes cost ~$5.4
and bought +0.0006; the role swap cost ~$0.9 token-basis and bought
+0.0126 over the same union. Caveats: both sides of every contrast are
sweep-selected argmaxes scored on the same reference; this is a single
comparison with no family correction across four GS sheets; and
3.7-`low` emits ~276 thinking tokens per tile against Gemini-3 MINIMAL's
zero, so model and thinking stay confounded. The K=10 escalation
re-verified the full union rather than increment-stitching — disclosed
on the card, cheaper than the matching-error risk, and it gives
single-vintage probabilities. The ladder rungs are re-derived;
registration pending materialisation. Obs 441.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
G1's pre-named informative outcome FIRED and G2 is falsified. The
carried-verifier K=5 cell reaches [-0.9139-] {+0.9238+} @20 m at (0.10,
k5) on a 791-candidate union, nominally above every Gemini-3 cell on
this corpus, but the paired tile-swap permutation (10,000 draws, 487
tiles) returns [-+0.0178-] {++0.0221+} at p = [-0.1697-] {+0.0971+}
against a null SD of [-0.0129-] {+0.0134+} — below the GS instrument's
resolution, so the screen can name the direction and not the size. K=10
adds [-+0.0003 (0.9142,-] {++0.0006 (0.9243,+} p = [-0.2076)-]
{+0.1231)+} and the ladder's own N5-N10 contrast is [--0.0011-]
{+-0.0013+} at p = [-0.7928:-] {+0.7921:+} saturated by N = 5, the
Gemini-3 shape exactly [-(0.8588-] {+(0.8652+} / [-0.9018-] {+0.9118+} /
[-0.9131-] {+0.9231+} / [-0.9142-] {+0.9243+} at N = 1/3/5/10). The
headline is the role swap: re-verifying the SAME 791 candidates with
gemini-3.7-flash reaches [-0.9265-] {+0.9364+} @20 m at (0.80, k5), P
[-0.9254-] {+0.9268+} / R [-0.9276-] {+0.9463+} / tile-MCC [-0.8078-]
{+0.8192+} — [-+0.0304-] {++0.0347+} vs the anchor, p = [-0.0105,-]
{+0.0065,+} the study's first GS-resolvable model-swap margin and the
only cell in the arc beating the anchor on F1 and MCC together. The
mechanism is calibration, not judgement: the 3.7 verifier's mean
mound_probability is [-0.687-] {+0.699+} against the carried verifier's
[-0.587-] {+0.594+} on identical candidates
[-(planning/gemini37-screen-2026-08-28.md:110),-] {+(0.687 / 0.587
before the re-verified rows,
planning/gemini37-screen-2026-08-28.md:110),+} so its optimum migrates
four rungs up a lattice that has sat at 0.10-0.20 across every model the
study has run — G2 falsified, and the portable claim is that a
verifier's operating threshold does not transfer across verifier models.
Cost ordering is the practitioner lesson: five extra passes cost ~$5.4
and bought [-+0.0003;-] {++0.0006;+} the role swap cost ~$0.9
token-basis and bought +0.0126 over the same union. Caveats: both sides
of every contrast are sweep-selected argmaxes scored on the same
reference; this is a single comparison with no family correction across
four GS sheets; and 3.7-`low` emits ~276 thinking tokens per tile
against Gemini-3 MINIMAL's zero, so model and thinking stay confounded.
The K=10 escalation re-verified the full union rather than
increment-stitching — disclosed on the card, cheaper than the
matching-error risk, and it gives single-vintage probabilities. The
ladder rungs are re-derived; registration pending materialisation. Obs
441.
```

### 4.7 `gemini37-image-gs-2026-09-01`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
The modality gap is eliminated at Gemini 3.7. A
difference-in-differences on one geometry and one reference: (text -
image) within Gemini 3 was +0.0559 at p = 0.0005; within 3.7 it is
-0.0143 (p = 0.158) on the carried-verifier pair and -0.0043 (p =
0.6767) on the all-3.7 pair — a gap change of -0.060 to -0.070, roughly
2.5x the GS verified-set resolution (MDE80 ~ 0.025), so a resolved
change and not instrument noise. The honest claim is PARITY, not
inversion: image leads nominally in both pairs and neither sign flip is
close to significant. I2 predicted the gap would land below ~0.031 and
the outcome overshot to zero. I1 is confirmed at about four times the
text-side family gain — 3.7-image reaches 0.9381 (carried verifier, at
(0.05, k5); 0.9353 at its registered (0.10, k5)) and 0.9408 (3.7
verifier) against the 0.8458 Gemini-3 image anchor, gains of +0.0923 /
+0.0950 where the same family step on text was +0.022 — so the gap
closed because image caught up, not because text regressed, and the
3-to-3.7 step delivers most of its value where pixels are read. I3 FAILS
on the carried-verifier arm, whose optimum moved to (0.05, k5), below
the predicted 0.10-0.20, and is confirmed on the 3.7-verifier arm at
(0.90, k5): the 3.7 verifier's high-probability calibration shift
replicates on image candidates, a second instrument for the
non-transferring-threshold claim. I4 is confirmed and lighter than
predicted (88-157 t/call). I5 is an informative failure — implicit
caching engaged at 79.5 % of input against a registered >= 90 % bar,
with the probe warm-up-confounded (16 % cold-parallel, 54 % sequential),
yet the proposer side cost $22.50 token-basis against a $32-36
projection. The escalation trigger is NOT met: all-3.7 image 0.9408
against the all-3.7 text swap 0.9364 is +0.0043 at p = 0.677, far inside
MDE80, no resolvable new high, so the 55-map image extension does not
proceed — a registered negative decision, not an absence. Obliges the
paper: the study's 'text examples beat image examples' claim must be
reframed as Gemini-3-specific. Obs 447.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
The modality gap is eliminated at Gemini 3.7. A
difference-in-differences on one geometry and one reference: (text -
image) within Gemini 3 was [-+0.0549-] {++0.0559+} at p = [-0.001;-]
{+0.0005;+} within 3.7 it is [--0.0115-] {+-0.0143+} (p = [-0.2533)-]
{+0.158)+} on the carried-verifier pair and -0.0043 (p = 0.6767) on the
all-3.7 pair — a gap change of [--0.059-] {+-0.060+} to [--0.066,-]
{+-0.070,+} roughly 2.5x the GS verified-set resolution (MDE80 ~
[-0.024),-] {+0.025),+} so a resolved change and not instrument noise.
The honest claim is PARITY, not inversion: image leads nominally in both
pairs and neither sign flip is close to significant. I2 predicted the
gap would land below ~0.031 and the outcome overshot to zero. I1 is
confirmed at about [-five-] {+four+} times the text-side family gain —
3.7-image reaches [-0.9254-] {+0.9381+} (carried [-verifier)-]
{+verifier, at (0.05, k5); 0.9353 at its registered (0.10, k5))+} and
[-0.9308-] {+0.9408+} (3.7 verifier) against the [-0.8412-] {+0.8458+}
Gemini-3 image anchor, gains of [-+0.0842-] {++0.0923+} / [-+0.0896-]
{++0.0950+} where the same family step on text was [-+0.018-] {++0.022+}
— so the gap closed because image caught up, not because text regressed,
and the 3-to-3.7 step delivers most of its value where pixels are read.
I3 {+FAILS on the carried-verifier arm, whose optimum moved to (0.05,
k5), below the predicted 0.10-0.20, and+} is confirmed [-exactly-] {+on
the 3.7-verifier arm+} at [-(0.10, k5) and-] (0.90, k5): the 3.7
verifier's high-probability calibration shift replicates on image
candidates, a second instrument for the non-transferring-threshold
claim. I4 is confirmed and lighter than predicted (88-157 t/call). I5 is
an informative failure — implicit caching engaged at 79.5 % of input
against a registered >= 90 % bar, with the probe warm-up-confounded (16
% cold-parallel, 54 % sequential), yet the proposer side cost $22.50
token-basis against a $32-36 projection. The escalation trigger is NOT
met: all-3.7 image [-0.9308-] {+0.9408+} against the all-3.7 text swap
[-0.9265-] {+0.9364+} is +0.0043 at p = 0.677, far inside MDE80, no
resolvable new high, so the 55-map image extension does not proceed — a
registered negative decision, not an absence. Obliges the paper: the
study's 'text examples beat image examples' claim must be reframed as
Gemini-3-specific. Obs 447.
```

### 4.8 `gemini37-fourth-cell-gs-leg-2026-08-31`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
A ~$3 GS calibration leg: the Gemini-3 grid g384_ov192 K=10 union (3,319
candidates) re-verified with the 3.7 verifier reaches 0.9220 @20 m at
(0.98, k10), P 0.9643 / R 0.8832 / tile-MCC 0.8350 against the 0.9017
text-B anchor (+0.0203, p = 0.0311 on 10,000 permutations over 487
tiles). The lattice moves the whole way to the top of the scale: the 3.7
verifier's mean probability is 0.214 on the noisy Gemini-3 pool against
0.699 on its own union (0.209 / 0.687 before the re-verified rows,
planning/gemini37-55map-2026-08-29.md:200), so the same verifier
calibrates DIFFERENTLY AGAINST DIFFERENT CANDIDATE POOLS — the
threshold-transfer claim extended from model to pool. (0.98, k10) was
committed as the 55-map fourth cell's carried point at
planning/gemini37-55map-2026-08-29.md:201 before any deployment scoring.
Obs 444 § (e).
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
A ~$3 GS calibration leg: the Gemini-3 grid g384_ov192 K=10 union (3,319
candidates) re-verified with the 3.7 verifier reaches [-0.9140-]
{+0.9220+} @20 m at (0.98, k10), P [-0.9637-] {+0.9643+} / R [-0.8692-]
{+0.8832+} / tile-MCC [-0.8239-] {+0.8350+} against the [-0.8961-]
{+0.9017+} text-B anchor [-(+0.0179,-] {+(+0.0203,+} p = [-0.0563-]
{+0.0311+} on 10,000 permutations over 487 tiles). The lattice moves the
whole way to the top of the scale: the 3.7 verifier's mean probability
is [-0.209-] {+0.214+} on the noisy Gemini-3 pool against [-0.687-]
{+0.699+} on its own union
[-(planning/gemini37-55map-2026-08-29.md:200),-] {+(0.209 / 0.687 before
the re-verified rows, planning/gemini37-55map-2026-08-29.md:200),+} so
the same verifier calibrates DIFFERENTLY AGAINST DIFFERENT CANDIDATE
POOLS — the threshold-transfer claim extended from model to pool. (0.98,
k10) was committed as the 55-map fourth cell's carried point at
planning/gemini37-55map-2026-08-29.md:201 before any deployment scoring.
Obs 444 § (e).
```

### 4.9 `gemini38-screen-armv-2026-09-04`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
The family ladder stops at 3.7. On the identical 791-candidate union,
the 3.8 verifier reaches 0.9358 @20 m at (0.88, k5), P 0.9347 / R 0.9369
/ tile-MCC 0.8331 on 429 detections: against the all-3.7 stack that is
dF1 -0.0006 at p = 0.7769, and against the carried Gemini-3 verifier
+0.0120 at p = 0.0764. E1 CONFIRMED — a tie, and the pre-named
informative outcome did not fire, so the verifier-model policy stays
shut and the 55-map board is untouched. The tie is not flat on every
axis: 3.8 buys +0.0139 of tile-MCC over 3.7 (0.8331 vs 0.8192) while
losing 0.0006 of F1, precision-led as its point implies. E3 is FALSIFIED
in the opposite direction — 76 thinking tokens per candidate in the
verifier seat against the 3.7 verifier's 106, and only 1.1x in the
proposer probe (307 vs 275 t/tile), so 'newer' bought LESS thinking, not
more. E4 is only partly confirmed, and the check that settles it also
corrects the campaign's first reading: the argmax does sit at 0.88
rather than at 3.7's 0.80/0.85 or Gemini-3's 0.15/0.20, but the surface
is flat — every k=5 point from prob_t 0.20 to 0.92 lies within 0.0022 of
the best — AND the 3.7 verifier is equally flat on the same union
(0.9343-0.9364 over that band, spread 0.0022, swap37/sweep_20m.csv),
whereas the carried Gemini-3 verifier is sharply peaked (0.8520-0.9021,
spread 0.0502). Threshold insensitivity is therefore a
3.7/3.8-generation property, not a 3.8 novelty. E2 is untested: the PI
ruled STOP after Arm V, so Arm P (~$9.6) and Arm S (~$1) were not run;
total spend was ~$0.85 flex token-basis. Gotchas recorded on the card:
run_pv.py verify stamps cost_basis 'list' with discount 1.0 even under
--service-tier flex; the verify path counts each retried server error as
a parse failure (803 = retries_total); and cleanup overwrote
run.meta.json again, the main-run meta surviving as
run.meta.main-2026-09-04.json. Obs 448.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
The family ladder stops at 3.7. On the identical 791-candidate union,
the 3.8 verifier reaches [-0.9258-] {+0.9358+} @20 m at (0.88, k5), P
[-0.9335-] {+0.9347+} / R [-0.9182-] {+0.9369+} / tile-MCC [-0.8218-]
{+0.8331+} on [-421-] {+429+} detections: against the all-3.7 stack that
is dF1 [--0.0007-] {+-0.0006+} at p = 0.7769, and against the carried
Gemini-3 verifier [-+0.0119-] {++0.0120+} at p = [-0.0969.-] {+0.0764.+}
E1 CONFIRMED — a tie, and the pre-named informative outcome did not
fire, so the verifier-model policy stays shut and the 55-map board is
untouched. The tie is not flat on every axis: 3.8 buys [-+0.0140-]
{++0.0139+} of tile-MCC over 3.7 [-(0.8218-] {+(0.8331+} vs [-0.8078)-]
{+0.8192)+} while losing [-0.0007-] {+0.0006+} of F1, precision-led as
its point implies. E3 is FALSIFIED in the opposite direction — 76
thinking tokens per candidate in the verifier seat against the 3.7
verifier's 106, and only 1.1x in the proposer probe (307 vs 275 t/tile),
so 'newer' bought LESS thinking, not more. E4 is only partly confirmed,
and the check that settles it also corrects the campaign's first
reading: the argmax does sit at 0.88 rather than at 3.7's 0.80/0.85 or
Gemini-3's 0.15/0.20, but the surface is flat — every k=5 point from
prob_t 0.20 to 0.92 lies within 0.0022 of the best — AND the 3.7
verifier is equally flat on the same union [-(0.9243-0.9265-]
{+(0.9343-0.9364+} over that band, spread 0.0022, swap37/sweep_20m.csv),
whereas the carried Gemini-3 verifier is sharply peaked
[-(0.8446-0.8942,-] {+(0.8520-0.9021,+} spread [-0.0497).-] {+0.0502).+}
Threshold insensitivity is therefore a 3.7/3.8-generation property, not
a 3.8 novelty. E2 is untested: the PI ruled STOP after Arm V, so Arm P
(~$9.6) and Arm S (~$1) were not run; total spend was ~$0.85 flex
token-basis. Gotchas recorded on the card: run_pv.py verify stamps
cost_basis 'list' with discount 1.0 even under --service-tier flex; the
verify path counts each retried server error as a parse failure (803 =
retries_total); and cleanup overwrote run.meta.json again, the main-run
meta surviving as run.meta.main-2026-09-04.json. Obs 448.
```

### 4.10 `e45-bootstrap-pairings`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
AS PREDICTED - both registered-instrument CIs exclude zero in the
permutation direction. H2 (PV 16-of-30 vs consensus 26-of-30): dF1
+0.073730, B=1,000 CI95 [+0.049520, +0.101772]; E54 B=10,000 [+0.048250,
+0.101597]. H3 (consensus 26-of-30 vs matched single-pass): dF1
+0.429693, CI95 [+0.392114, +0.470439]; B=10,000 [+0.388060, +0.472072].
Reproduction gates passed 7/7 (H2, vs the committed quiet artefact
through the same code path, incl. the wins/losses permutation
fingerprint) and 4/4 (H3, vs the tiering pairwise micro-F1 vintage) at
1e-6 before any bootstrap. Registered quantities = CI95 +
CI-excludes-zero (Decision 10, decisions-log.md:335-345); the 2*min-tail
p is convention-borrowed from the family H1 leg, not registered.
Scoping: H2 and H3 are the two permutation-floor family inputs; H8's
family input is also permutation-sourced (a Simes minimum, not pairable)
and stays disclosed under E45. The permutation p-values remain the
family inputs; this artefact is the E45 paired disclosure. Verification
round (on the 2026-08-17 values): both bootstrap legs reproduced
bit-for-bit by a blind verifier from independently written code; the
values above, regenerated 2026-10-15 (S164 restatement pass), have not
been blind-verified. Artefact:
results/e45-bootstrap-pairings/e45_bootstrap_pairings.json (sapphire,
seed 42, $0).
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
AS PREDICTED - both registered-instrument CIs exclude zero in the
permutation direction. H2 (PV 16-of-30 vs consensus 26-of-30): dF1
[-+0.076083,-] {++0.073730,+} B=1,000 CI95 [-[+0.051787, +0.104642];-]
{+[+0.049520, +0.101772];+} E54 B=10,000 [-[+0.050771, +0.103945].-]
{+[+0.048250, +0.101597].+} H3 (consensus 26-of-30 vs matched
single-pass): dF1 [-+0.427340,-] {++0.429693,+} CI95 [-[+0.389640,
+0.468082];-] {+[+0.392114, +0.470439];+} B=10,000 [-[+0.385608,
+0.469544].-] {+[+0.388060, +0.472072].+} Reproduction gates passed 7/7
(H2, vs the committed quiet artefact through the same code path, incl.
the wins/losses permutation fingerprint) and 4/4 (H3, vs the tiering
pairwise micro-F1 vintage) at 1e-6 before any bootstrap. Registered
quantities = CI95 + CI-excludes-zero (Decision 10,
decisions-log.md:335-345); the 2*min-tail p is convention-borrowed from
the family H1 leg, not registered. Scoping: H2 and H3 are the two
permutation-floor family inputs; H8's family input is also
permutation-sourced (a Simes minimum, not pairable) and stays disclosed
under E45. The permutation p-values remain the family inputs; this
artefact is the E45 paired disclosure. Verification [-round:-] {+round
(on the 2026-08-17 values):+} both bootstrap legs reproduced bit-for-bit
by a blind verifier from independently written [-code.-] {+code; the
values above, regenerated 2026-10-15 (S164 restatement pass), have not
been blind-verified.+} Artefact:
results/e45-bootstrap-pairings/e45_bootstrap_pairings.json (sapphire,
seed 42, $0).
```

### 4.11 `gs-era2-verified-board-2026-09-10`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
150 of 153 admitted cells tiered; 3 WITHHELD (the tile-join invariant
refuses their per-tile table on this frame, so they are ranked and
tested nowhere and only their whole-frame F1 is quoted:
g37-text-k1-verified-carried-p0.10-k1 F1@20 0.8616;
g37-text-k1-verified-opmax F1@20 0.8747; g37-text-k3-verified-opmax
F1@20 0.9135). 8075/11175 pairs significant at BH q = 0.05, 14 tiers on
the era2-b-487 frame (487 tiles, 435 reference mounds). Tier 1 (greedy
clique) = 5 cell(s); MCB admissible set = 52. Top:
g37-image-k5-verified-swap37-p0.90-k5-era2b F1@20 0.9332.
g37-text-k5-verified-swap37-p0.80-k5-era2b 0.9289 (T1);
g37-text-k5-verified-swap38-p0.88-k5-era2b 0.9282 (T1);
g37-image-k5-verified-carried-p0.10-k5-era2b 0.9278 (T1);
g37-text-k10-verified-carried-p0.10-k10-era2b 0.9169 (T1). Gates: G1 see
provenance, G2 0 failures, G3 0 failures, G4 110/110; G6 max |delta|
0.0079. REPORTED BESIDE, not replacing, the preregistered F1 tiering (PI
ruling 2026-09-13, S153 ruling 7): a tile-MCC permutation family on the
SAME swap masks (same seed, same tile order), BH q = 0.05 within its own
family — 3001/11175 pairs significant, 6 MCC tiers over 150 cells; MCC
Tier 1 = 34 cell(s) (verified-adv-image-baseline-pro-vf-era2b MCC
0.8887; verified-adv-image-baseline-medium-vf-era2b MCC 0.8848;
verified-adv-image-baseline-era2b MCC 0.8766; pv-scale4-optimal-n1-opmax
MCC 0.8726; pv-high-image-t1.0-n1-opmax MCC 0.8640; and 29 more — full
list in tiering_20m.json -> mcc_permutation.tie_set); MCC MCB admissible
set = 60, of which 9 also in the F1 admissible set. The board's tiering
remains the F1 one.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
150 of 153 admitted cells tiered; 3 WITHHELD (the tile-join invariant
refuses their per-tile table on this frame, so they are ranked and
tested nowhere and only their whole-frame F1 is quoted:
g37-text-k1-verified-carried-p0.10-k1 F1@20 [-0.8338;-] {+0.8616;+}
g37-text-k1-verified-opmax F1@20 [-0.8495;-] {+0.8747;+}
g37-text-k3-verified-opmax F1@20 [-0.8860). 7961/11175-] {+0.9135).
8075/11175+} pairs significant at BH q = 0.05, 14 tiers on the
era2-b-487 frame (487 tiles, 435 reference mounds). Tier 1 (greedy
clique) = 5 cell(s); MCB admissible set = [-65.-] {+52.+} Top:
g37-image-k5-verified-swap37-p0.90-k5-era2b F1@20 [-0.9233.-]
{+0.9332.+} g37-text-k5-verified-swap37-p0.80-k5-era2b [-0.9190-]
{+0.9289+} (T1); g37-text-k5-verified-swap38-p0.88-k5-era2b [-0.9182-]
{+0.9282+} (T1); g37-image-k5-verified-carried-p0.10-k5-era2b [-0.9179-]
{+0.9278+} (T1); g37-text-k10-verified-carried-p0.10-k10-era2b
[-0.9068-] {+0.9169+} (T1). Gates: G1 see provenance, G2 0 failures, G3
0 failures, G4 110/110; G6 max |delta| [-0.0078.-] {+0.0079.+} REPORTED
BESIDE, not replacing, the preregistered F1 tiering (PI ruling
2026-09-13, S153 ruling 7): a tile-MCC permutation family on the SAME
swap masks (same seed, same tile order), BH q = 0.05 within its own
family — [-2982/11175-] {+3001/11175+} pairs significant, 6 MCC tiers
over 150 cells; MCC Tier 1 = [-33-] {+34+} cell(s)
(verified-adv-image-baseline-pro-vf-era2b MCC 0.8887;
verified-adv-image-baseline-medium-vf-era2b MCC 0.8848;
verified-adv-image-baseline-era2b MCC 0.8766; pv-scale4-optimal-n1-opmax
MCC 0.8726; pv-high-image-t1.0-n1-opmax MCC 0.8640; and [-28-] {+29+}
more — full list in tiering_20m.json -> mcc_permutation.tie_set); MCC
MCB admissible set = [-59,-] {+60,+} of which 9 also in the F1
admissible set. The board's tiering remains the F1 one.
```

### 4.12 `k-ladder-2026-09-12`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
The pass-count ladder K at otherwise fixed parameters, on 23 ladders:
the gold-standard stride A ladder (the only one whose every rung is an
exact re-verification of its own first-N union), the thirteen Gemini 3
pv-diag-384 families and the 3.7 gold-standard text screen that Phase 2
completed to four rungs for US$24.8065, the grid 384 px / 50 % MINIMAL
text ladder tier E completed for US$4.9595, and the seven 55-map
deployment ladders. SHAPE: the return is FRONT-LOADED and K = 3 is on
the efficient set of every ladder in the corpus — 37 % to 93 % of a
ladder's total F1 gain for 31 % to 64 % of its top rung's cost — while
the last step is the worst buy on every ladder, at about US$0.20 to
US$27 per 0.001 F1 (the 3.7 family's K = 5 -> K = 10 step buys +0.0004
F1@20 for US$8.68, about US$22 per 0.001 F1). WHAT GOVERNS THE RETURN:
the proposer's thinking level, and within a level its temperature. The K
= 1 -> best-rung F1 gain is significant on 7 of 7 HIGH-thinking ladders
and 2 of 6 MINIMAL ones; four ladders, every one of them MINIMAL,
greedy-clique into a SINGLE tier in which K buys nothing detectable; and
on both HIGH tracks the gain rises monotonically with temperature (text
+0.0559 -> +0.0735 -> +0.0955, image +0.0780 -> +0.0959 -> +0.1514
across T 0.3 -> 0.7 -> 1.0). Read as the diversity dividend (Obs 141)
measured on a K ladder: K buys sampling diversity, and pays in
proportion to how much the configuration already generates. TILE-MCC
DOES NOT FOLLOW F1. Across the 15 verified ladders with an interpretable
tile-MCC, F1 rises on all 15 and tile-MCC falls on 10, and NO ladder
shows a significant tile-MCC RISE; the gold-standard ladder's +0.0131, §
4 of the findings' one apparent counter-example, tests at BH p = 0.7633.
Significant FALLS are found on four ladders — the 3.7-verifier stride B
(-0.0112), 3.7 arm 1 (-0.0099), 3.7 arm 2 (-0.0275) and HIGH image T 1.0
(-0.0637, BH p = 0.0420, the family with the largest F1 gain). More
passes buy localisation inside already-positive tiles, not tile-level
discrimination, which matters for any application whose unit is the tile
rather than the mound. CAVEAT on the MCC column: tile-MCC is computed by
a string join on source_tile, and three cells of the 3.7 gold-standard
text family are scored on a frame whose tile vocabulary is not their
proposer's, so their tile-MCC is WITHHELD with a named reason rather
than reported (g37-text-k1-verified-opmax,
g37-text-k1-verified-carried-p0.10-k1, g37-text-k3-verified-opmax; no
raw value is now recorded). The corpus-wide exposure is measured at 3 of
149 committed cells the Era-2 board reads, no published board MCC is
affected, and the repair is a corpus-wide decision with the PI because
the 384 px frames overlap
(reports/tile-mcc-geometric-join-2026-09-12.md). Their F1 is sound and
is reported in full. INSTRUMENT (PI ruling): the board's round-robin
tile-swap micro-F1 permutation is THE instrument — 10,000 permutations,
seed 42, BH q = 0.05 within each ladder's own round-robin, tile-MCC
swapped on byte-identical masks so a ΔF1 and a ΔMCC are two statistics
of one permutation — and the registered per-map paired sign-swap is the
CROSS-CHECK. Where both cover a pair (8 pairs, 2 ladders) all eight
tile-MCC significance calls AGREE, with ΔMCC estimates within 0.0006;
one marginal F1 call differs (stride A's K = 3 -> 5, BH p 0.0079 against
0.0655), so the instrument choice is live for marginal F1 claims and
immaterial to the MCC conclusion. THE TWO CORPORA AGREE once resolution
is accounted for. The deployment MINIMAL ladders' own cells, scored on
random 487-tile subsets of their own 8,541 tiles (200 draws, seed 42,
same instrument), keep BH significance in 197 of 200 draws at ΔF1
+0.0547 and in only 39 of 200 at +0.0192 — a subsampling standard
deviation of ~0.0114 either way — so 487 tiles resolve a ΔF1 of about
0.03 and above and not below. The nine MINIMAL ladders sort by effect
size rather than by corpus (every one at or above +0.0546 separates,
every one at or below +0.0223 does not), and the deployment range
+0.0192..+0.0547 sits INSIDE the gold-standard range +0.0139..+0.0600.
So 'K buys nothing detectable' on four MINIMAL configurations is a
statement about 487 tiles, not about K. PARETO MCC SET: on tile-MCC no
rung above K = 1 is ever the admissible choice — K = 1 holds the highest
tile-MCC on 8 of the 15 interpretable ladders and is never significantly
beaten on it — so the MCC-efficient rung is K = 1 wherever tile-level
discrimination is the objective, while the F1-efficient rung is K = 3.
The two objectives select different rungs, and that is the review's
practical finding. A GEOMETRY EFFECT, consensus-only: at fixed MINIMAL
text T 0.7 the grid study's K = 1 -> 10 gain is about 2.2x larger at
12.5 % overlap than at 50 % (+0.1441 against +0.0660 at 384 px; +0.0947
against +0.0425 at 512 px), and tile-MCC RISES with K on all four
consensus-only cells (+0.029..+0.132) — the opposite of the verified
ladders, consistent with the same mechanism. Overlap and pass count buy
the same redundancy. The pattern does not survive to the verified
deployment ladders, which order the other way. THE VERIFIER STAGE
REVERSES tile-MCC's RESPONSE TO K, and absorbs about 60 % of K's F1
return (§ 8.6, added on the PI's ruling 2026-09-13). On ONE pool and ONE
geometry — the grid study's 384 px / 50 % B-geometry MINIMAL text pool,
which is the deployment stride-B tiling at gold-standard scale — K = 1
-> 10 raises F1@20 by +0.0660 with tile-MCC RISING +0.0444
consensus-only (results/grid-2026-08-18/sweep.csv, cell g384_ov192, best
F1@20 per K over the corroboration x vote grid: 0.6633/0.4465 at K = 1,
0.7293/0.4909 at K = 10), and raises F1@20 by only +0.0262 with tile-MCC
FALLING -0.0238 once the same pool is verified (tier-e/ladder.json and
each rung's evaluation: 0.8680/0.8211 at K = 1, 0.8942/0.7973 at K =
10). So the verifier takes 60.3 % of what extra passes buy on F1 —
because it was already removing much of what extra passes remove — and
turns a tile-level GAIN into a tile-level LOSS, a swing of 0.0682 MCC.
This is the mechanism of the TILE-MCC DOES NOT FOLLOW F1 finding above
measured directly rather than inferred: tile-MCC's response to K is a
property of the PIPELINE STAGE, not of K. Its limits are stated with it:
one geometry, one thinking level, one temperature, one modality, one
corpus, and the ladder's own DMCC steps are not individually significant
(tile-MCC separates on none of its six pairs), so the claim is about the
sign and size of the shift BETWEEN stages. NOT CLAIMED: no MCC RANKING
of rungs, tiering stays on the preregistered F1; and the five
non-separating ladders' MCC moves are not shown to be zero. HSU MCB
ADMISSIBLE SETS (PI ruling 2026-09-13, 'wait for the sets'): the
review's last outstanding run-card requirement is supplied for all 22
tiered ladders, on F1 at each ladder's own headline buffer and on
tile-MCC, with the Era-2 board's own MCB step verbatim
(scripts/selection_aware_intervals.py --board; Hsu's constrained
one-sided form on theta_i = stat_i - max_{j != i} stat_j, critical value
bootstrapped over 10,000 tile resamples, seed 42, m-out-of-n 1.0,
simultaneous 95 %), each ladder on its own frame and reference, driven
by scripts/k_ladder_mcb.py and gated on all 44 runs against the
committed tiering ranking (170 candidate rows, max abs delta 4.958e-05,
results/k-ladder-2026-09-12/mcb/summary.json). ON THE SHAPE FINDING: K =
3 is admissible on 12 of the 22 ladders and is the CHEAPEST admissible
rung on 10 of them, so the front-loaded Pareto reading is endorsed by
the simultaneous instrument on roughly half the corpus and declined on
the other half — on nine ladders nothing below K = 5 is admissible even
though K = 3 remains the efficient buy, which makes 'K = 3 is on the
efficient set' a cost claim rather than a statistical one. ON THE LAST
STEP: NO ladder's F1-admissible set excludes K = 10 — all twenty ladders
that have a K = 10 rung admit it — so the top rung is never
statistically ruled out, only never worth its price, which is the formal
counterpart of the US$1,100-to-US$43,000 per 0.001 F1 figures above. ON
THE TWO OBJECTIVES: K = 1 is ruled out on F1 on 20 of 22 ladders and is
admissible on tile-MCC on 22 of 22, holding the highest tile-MCC on 13
of them, so the PARETO MCC SET claim above now rests on the canonical
simultaneous instrument rather than on a pairwise count. ON TILE-MCC'S
RESOLUTION: the MCC-admissible set is the WHOLE ladder on 13 of 22
against 2 of 22 on F1 — the same weak resolution the permutation arm
found — but where it resolves it resolves against K: six of the twenty
ladders with a K = 10 rung exclude it on tile-MCC, and on two (55-map
stride B under the 3.7 verifier, and 3.7 arm 2) the MCC-admissible set
is {K = 1} alone. ON RESOLUTION GENERALLY: the simultaneous F1 width
w_upper is 0.0159-0.0326 on the 487-tile gold standard and 0.0047-0.0056
on the 8,541-tile deployment corpus, three to six times narrower, which
is the tension analysis's resolution result in the MCB's own units.
INSTRUMENT DISAGREEMENT, FLAGGED: the admissible set and the committed
greedy-clique tie set differ in BOTH directions (F1 set smaller than the
tie set on two ladders, larger on six), exactly as erratum E83 and
defect D20 warn; of the four MINIMAL ladders that greedy-clique into a
SINGLE tier, only two are admissible whole, since MINIMAL text T 0.3 and
MINIMAL image T 1.0 both rule K = 1 out as best. The single-tier
statement stands as a within-ladder pairwise BH result and is not
withdrawn, but 'one tier' is not 'every rung could be the best one'.
WITHHELD: the 3.7 gold-standard text screen has NO admissible set on
either metric, because the tile-join invariant refuses the per-tile
table of three of its four rungs on this frame and the refusal falls on
the F1 arm as well as the MCC arm, leaving two sound rungs of four; its
whole-frame F1 is unaffected and reported in full. CARRIED CONVENTION
(PI ruling 2026-09-13): the gold-standard stride ladder's own vote shell
(k = 1/3/4/8 at K = 1/3/5/10) is THE carried point and ruling R2's
literal k = K stays as a disclosed column; no number was recomputed, the
two readings coincide at K <= 3, and both stay committed in
phase2/committed-carried/scores.json. Reading that ruling back against
the 55-map tables disclosed something nothing had recorded: stride A's
committed carried cells are the stride shell (k = 3/4/8) while stride
B's, stride B's 3.7-verifier cell and both 3.7 arms' are k = K, so the
transfer taxes of findings sections 3.2, 3.3 and 3.4 are k = K taxes and
are an UPPER BOUND on the transfer cost (each cell's vote_threshold in
results/run-conditions.json; findings section 3's disclosure table). MCB
artefacts: results/k-ladder-2026-09-12/mcb/; deltas
reports/k-ladder-mcb-deltas-2026-09-13.md. Findings:
results/k-ladder-2026-09-12/findings.md (all sections); tension analyses
results/k-ladder-2026-09-12/tension/; spend
reports/k-ladder-phase2-deltas-2026-09-12.md and
results/k-ladder-2026-09-12/tier-e/.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
The pass-count ladder K at otherwise fixed parameters, on 23 ladders:
the gold-standard stride A ladder (the only one whose every rung is an
exact re-verification of its own first-N union), the thirteen Gemini 3
pv-diag-384 families and the 3.7 gold-standard text screen that Phase 2
completed to four rungs for US$24.8065, the grid 384 px / 50 % MINIMAL
text ladder tier E completed for US$4.9595, and the seven 55-map
deployment ladders. SHAPE: the return is FRONT-LOADED and K = 3 is on
the efficient set of every ladder in the corpus — 37 % to 93 % of a
ladder's total F1 gain for 31 % to 64 % of its top rung's cost — while
the last step is the worst buy on every ladder, at [-US$1,100-] {+about
US$0.20+} to [-US$43,000-] {+US$27+} per 0.001 F1 (the 3.7 family's K =
5 -> K = 10 step buys [-+0.0002-] {++0.0004+} F1@20 for [-US$8.65).-]
{+US$8.68, about US$22 per 0.001 F1).+} WHAT GOVERNS THE RETURN: the
proposer's thinking level, and within a level its temperature. The K = 1
-> best-rung F1 gain is significant on 7 of 7 HIGH-thinking ladders and
2 of 6 MINIMAL ones; four ladders, every one of them MINIMAL,
greedy-clique into a SINGLE tier in which K buys nothing detectable; and
on both HIGH tracks the gain rises monotonically with temperature (text
+0.0559 -> +0.0735 -> [-+0.0994,-] {++0.0955,+} image +0.0780 -> +0.0959
-> +0.1514 across T 0.3 -> 0.7 -> 1.0). Read as the diversity dividend
(Obs 141) measured on a K ladder: K buys sampling diversity, and pays in
proportion to how much the configuration already generates. TILE-MCC
DOES NOT FOLLOW F1. Across the [-21-] {+15+} verified ladders with an
interpretable tile-MCC, F1 rises on all [-21-] {+15+} and tile-MCC falls
on [-16,-] {+10,+} and NO ladder shows a significant tile-MCC RISE; the
gold-standard ladder's [-+0.0135,-] {++0.0131,+} § 4 of the findings'
one apparent counter-example, tests at BH p = [-0.7678.-] {+0.7633.+}
Significant FALLS are found on four ladders — the 3.7-verifier stride B
(-0.0112), 3.7 arm 1 (-0.0099), 3.7 arm 2 (-0.0275) and HIGH image T 1.0
(-0.0637, BH p = 0.0420, the family with the largest F1 gain). More
passes buy localisation inside already-positive tiles, not tile-level
discrimination, which matters for any application whose unit is the tile
rather than the mound. CAVEAT on the MCC column: tile-MCC is computed by
a string join on source_tile, and three cells of the 3.7 gold-standard
text family are scored on a frame whose tile vocabulary is not their
proposer's, so their tile-MCC is WITHHELD with a named reason rather
than reported (g37-text-k1-verified-opmax,
g37-text-k1-verified-carried-p0.10-k1, g37-text-k3-verified-opmax;
{+no+} raw [-0.1337 / 0.1422 / 0.1337).-] {+value is now recorded).+}
The corpus-wide exposure is measured at 3 of 149 committed cells the
Era-2 board reads, no published board MCC is affected, and the repair is
a corpus-wide decision with the PI because the 384 px frames overlap
(reports/tile-mcc-geometric-join-2026-09-12.md). Their F1 is sound and
is reported in full. INSTRUMENT (PI ruling): the board's round-robin
tile-swap micro-F1 permutation is THE instrument — 10,000 permutations,
seed 42, BH q = 0.05 within each ladder's own round-robin, tile-MCC
swapped on byte-identical masks so a ΔF1 and a ΔMCC are two statistics
of one permutation — and the registered per-map paired sign-swap is the
CROSS-CHECK. Where both cover a pair (8 pairs, 2 ladders) all eight
tile-MCC significance calls AGREE, with ΔMCC estimates within 0.0006;
one marginal F1 call differs (stride A's K = 3 -> 5, BH p 0.0079 against
0.0655), so the instrument choice is live for marginal F1 claims and
immaterial to the MCC conclusion. THE TWO CORPORA AGREE once resolution
is accounted for. The deployment MINIMAL ladders' own cells, scored on
random 487-tile subsets of their own 8,541 tiles (200 draws, seed 42,
same instrument), keep BH significance in 197 of 200 draws at ΔF1
+0.0547 and in only 39 of 200 at +0.0192 — a subsampling standard
deviation of ~0.0114 either way — so 487 tiles resolve a ΔF1 of about
0.03 and above and not below. The nine MINIMAL ladders sort by effect
size rather than by corpus (every one at or above +0.0546 separates,
every one at or below +0.0223 does not), and the deployment range
+0.0192..+0.0547 sits INSIDE the gold-standard range
[-+0.0139..+0.0629.-] {++0.0139..+0.0600.+} So 'K buys nothing
detectable' on four MINIMAL configurations is a statement about 487
tiles, not about K. PARETO MCC SET: on tile-MCC no rung above K = 1 is
ever the admissible choice — K = 1 holds the highest tile-MCC on [-13-]
{+8+} of the [-21-] {+15+} interpretable ladders and is never
significantly beaten on it — so the MCC-efficient rung is K = 1 wherever
tile-level discrimination is the objective, while the F1-efficient rung
is K = 3. The two objectives select different rungs, and that is the
review's practical finding. A GEOMETRY EFFECT, consensus-only: at fixed
MINIMAL text T 0.7 the grid study's K = 1 -> 10 gain is about [-2.4x-]
{+2.2x+} larger at 12.5 % overlap than at 50 % [-(+0.1454-] {+(+0.1441+}
against [-+0.0572-] {++0.0660+} at 384 px; [-+0.0914-] {++0.0947+}
against [-+0.0396-] {++0.0425+} at 512 px), and tile-MCC RISES with K on
all four consensus-only cells [-(+0.038..+0.154)-] {+(+0.029..+0.132)+}
— the opposite of the verified ladders, consistent with the same
mechanism. Overlap and pass count buy the same redundancy. The pattern
does not survive to the verified deployment ladders, which order the
other way. THE VERIFIER STAGE REVERSES tile-MCC's RESPONSE TO K, and
absorbs about [-40-] {+60+} % of K's F1 return (§ 8.6, added on the PI's
ruling 2026-09-13). On ONE pool and ONE geometry — the grid study's 384
px / 50 % B-geometry MINIMAL text pool, which is the deployment stride-B
tiling at gold-standard scale — K = 1 -> 10 raises F1@20 by [-+0.0572-]
{++0.0660+} with tile-MCC RISING +0.0444 consensus-only
(results/grid-2026-08-18/sweep.csv, cell g384_ov192, best F1@20 per K
over the corroboration x vote grid: 0.6633/0.4465 at K = 1,
[-0.7205/0.4909-] {+0.7293/0.4909+} at K = 10), and raises F1@20 by only
[-+0.0340-] {++0.0262+} with tile-MCC FALLING [--0.0308-] {+-0.0238+}
once the same pool is verified (tier-e/ladder.json and each rung's
evaluation: [-0.8546/0.8211-] {+0.8680/0.8211+} at K = 1,
[-0.8886/0.7903-] {+0.8942/0.7973+} at K = 10). So the verifier takes
[-40.6-] {+60.3+} % of what extra passes buy on F1 — because it was
already removing much of what extra passes remove — and turns a
tile-level GAIN into a tile-level LOSS, a swing of [-0.0752-] {+0.0682+}
MCC. This is the mechanism of the TILE-MCC DOES NOT FOLLOW F1 finding
above measured directly rather than inferred: tile-MCC's response to K
is a property of the PIPELINE STAGE, not of K. Its limits are stated
with it: one geometry, one thinking level, one temperature, one
modality, one corpus, and the ladder's own DMCC steps are not
individually significant (tile-MCC separates on none of its six pairs),
so the claim is about the sign and size of the shift BETWEEN stages. NOT
CLAIMED: no MCC RANKING of rungs, tiering stays on the preregistered F1;
and the five non-separating ladders' MCC moves are not shown to be zero.
HSU MCB ADMISSIBLE SETS (PI ruling 2026-09-13, 'wait for the sets'): the
review's last outstanding run-card requirement is supplied for all 22
tiered ladders, on F1 at each ladder's own headline buffer and on
tile-MCC, with the Era-2 board's own MCB step verbatim
(scripts/selection_aware_intervals.py --board; Hsu's constrained
one-sided form on theta_i = stat_i - max_{j != i} stat_j, critical value
bootstrapped over 10,000 tile resamples, seed 42, m-out-of-n 1.0,
simultaneous 95 %), each ladder on its own frame and reference, driven
by scripts/k_ladder_mcb.py and gated on all 44 runs against the
committed tiering ranking (170 candidate rows, max abs delta 4.958e-05,
results/k-ladder-2026-09-12/mcb/summary.json). ON THE SHAPE FINDING: K =
3 is admissible on 12 of the 22 ladders and is the CHEAPEST admissible
rung on 10 of them, so the front-loaded Pareto reading is endorsed by
the simultaneous instrument on roughly half the corpus and declined on
the other half — on nine ladders nothing below K = 5 is admissible even
though K = 3 remains the efficient buy, which makes 'K = 3 is on the
efficient set' a cost claim rather than a statistical one. ON THE LAST
STEP: NO ladder's F1-admissible set excludes K = 10 — all twenty ladders
that have a K = 10 rung admit it — so the top rung is never
statistically ruled out, only never worth its price, which is the formal
counterpart of the US$1,100-to-US$43,000 per 0.001 F1 figures above. ON
THE TWO OBJECTIVES: K = 1 is ruled out on F1 on 20 of 22 ladders and is
admissible on tile-MCC on 22 of 22, holding the highest tile-MCC on 13
of them, so the PARETO MCC SET claim above now rests on the canonical
simultaneous instrument rather than on a pairwise count. ON TILE-MCC'S
RESOLUTION: the MCC-admissible set is the WHOLE ladder on [-12-] {+13+}
of 22 against 2 of 22 on F1 — the same weak resolution the permutation
arm found — but where it resolves it resolves against K: [-seven-]
{+six+} of the twenty ladders with a K = 10 rung exclude it on tile-MCC,
and on two (55-map stride B under the 3.7 verifier, and 3.7 arm 2) the
MCC-admissible set is {K = 1} alone. ON RESOLUTION GENERALLY: the
simultaneous F1 width w_upper is [-0.0151-0.0326-] {+0.0159-0.0326+} on
the 487-tile gold standard and 0.0047-0.0056 on the 8,541-tile
deployment corpus, three to six times narrower, which is the tension
analysis's resolution result in the MCB's own units. INSTRUMENT
DISAGREEMENT, FLAGGED: the admissible set and the committed
greedy-clique tie set differ in BOTH directions (F1 set smaller than the
tie set on two ladders, larger on six), exactly as erratum E83 and
defect D20 warn; of the four MINIMAL ladders that greedy-clique into a
SINGLE tier, only two are admissible whole, since MINIMAL text T 0.3 and
MINIMAL image T 1.0 both rule K = 1 out as best. The single-tier
statement stands as a within-ladder pairwise BH result and is not
withdrawn, but 'one tier' is not 'every rung could be the best one'.
WITHHELD: the 3.7 gold-standard text screen has NO admissible set on
either metric, because the tile-join invariant refuses the per-tile
table of three of its four rungs on this frame and the refusal falls on
the F1 arm as well as the MCC arm, leaving two sound rungs of four; its
whole-frame F1 is unaffected and reported in full. CARRIED CONVENTION
(PI ruling 2026-09-13): the gold-standard stride ladder's own vote shell
(k = 1/3/4/8 at K = 1/3/5/10) is THE carried point and ruling R2's
literal k = K stays as a disclosed column; no number was recomputed, the
two readings coincide at K <= 3, and both stay committed in
phase2/committed-carried/scores.json. Reading that ruling back against
the 55-map tables disclosed something nothing had recorded: stride A's
committed carried cells are the stride shell (k = 3/4/8) while stride
B's, stride B's 3.7-verifier cell and both 3.7 arms' are k = K, so the
transfer taxes of findings sections 3.2, 3.3 and 3.4 are k = K taxes and
are an UPPER BOUND on the transfer cost (each cell's vote_threshold in
results/run-conditions.json; findings section 3's disclosure table). MCB
artefacts: results/k-ladder-2026-09-12/mcb/; deltas
reports/k-ladder-mcb-deltas-2026-09-13.md. Findings:
results/k-ladder-2026-09-12/findings.md (all sections); tension analyses
results/k-ladder-2026-09-12/tension/; spend
reports/k-ladder-phase2-deltas-2026-09-12.md and
results/k-ladder-2026-09-12/tier-e/.
```

### 4.13 `verifier-uplift-pairing`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
170 of 170 pairs computed on F1 and 167 of 170 on tile MCC (0 blocked;
three MCC pairs pending: one has an undefined twin MCC, and the two
55-map stride A K = 10 twins' own evaluations withhold their tile MCC).
F1 uplift median +0.2562, range -0.0366 to +0.5232, 3 negative; MCC
uplift median +0.4936, range -0.0038 to +0.8410, 1 negative. By frame
(F1 n, median): 55maps-8541 86, +0.369; era-2-487 51, +0.132;
grid-common-487 21, +0.193; era-1-340 5, +0.037; era-3-327 4, +0.005;
px256-1032 3, +0.398. The 27 first-N ladder-rung twins were derived
inside the K-ladder job (PI ruling B3, 2026-09-12) and are all positive.
Total 170 not 172: three K = 3 archived sweep optima became Era-2 board
members (excluded by the board-frame rule) and the September recovery
pair joined. [AMENDED 2026-09-12, S153, second amendment: 145 -> 170.
Signed text at 2026-09-11: '145 of 172 pairs computed on F1 and 144 on
tile MCC (27 blocked, disclosed with reasons: all first-N ladder rungs
whose universe was never committed; one further MCC pair undefined
because its twin's MCC is undefined). F1 uplift median +0.201, range
-0.0366 to +0.486, 2 negative (h8-v2::verified-wbf-scale-4 -0.0003;
proposer-verifier-512::verified-adversarial-text -0.0366, the run
sidelined in S107, whose verifier cut recall on an already-precise
twin); MCC uplift median +0.427, range -0.023 to +0.841, 3 negative. By
frame (F1 n, median): 55-map strata 59, +0.353; GS Era-2 53, +0.138;
grid-common 21, +0.194; Era-1 5, +0.037; Era-3 4, +0.005; px256 3,
+0.398. The paper headline
pv-diag-384::verified-adv-text-consensus-16of30 (0.8902) gains +0.2132
F1 / +0.3928 MCC over its 16-of-30 consensus. [AMENDED 2026-09-11, S153:
85 -> 128 by the four absence-refusal rules of 2026-09-10, -> 129 by the
44th ready twin, -> 145 by two null-vote-threshold rules (single-pass
cells route to the single-pass rule at k = 1; k-of-N pool names are
parsed). Signed text at 2026-09-10: '85 of 172 pairs computed on F1 and
MCC (86 blocked, disclosed with reasons). F1 uplift median +0.212, range
-0.0003 to +0.486, 1 negative; GS Era-2 frame 19 pairs (median +0.138),
55-map strata 41 pairs (median +0.300).']']
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
170 of 170 pairs computed on F1 and [-169-] {+167+} of 170 on tile MCC
(0 blocked; [-the-] {+three MCC pairs pending:+} one [-MCC pair
pending-] has an undefined twin {+MCC, and the two 55-map stride A K =
10 twins' own evaluations withhold their tile+} MCC). F1 uplift median
[-+0.2631,-] {++0.2562,+} range -0.0366 to [-+0.5265, 2-] {++0.5232, 3+}
negative; MCC uplift median [-+0.4975,-] {++0.4936,+} range [--0.0230-]
{+-0.0038+} to +0.8410, [-3-] {+1+} negative. By frame (F1 n, median):
55maps-8541 86, [-+0.368;-] {++0.369;+} era-2-487 51, +0.132;
grid-common-487 21, [-+0.194;-] {++0.193;+} era-1-340 5, +0.037;
era-3-327 4, +0.005; px256-1032 3, +0.398. The 27 first-N ladder-rung
twins were derived inside the K-ladder job (PI ruling B3, 2026-09-12)
and are all positive. Total 170 not 172: three K = 3 archived sweep
optima became Era-2 board members (excluded by the board-frame rule) and
the September recovery pair joined. [AMENDED 2026-09-12, S153, second
amendment: 145 -> 170. Signed text at 2026-09-11: '145 of 172 pairs
computed on F1 and 144 on tile MCC (27 blocked, disclosed with reasons:
all first-N ladder rungs whose universe was never committed; one further
MCC pair undefined because its twin's MCC is undefined). F1 uplift
median +0.201, range -0.0366 to +0.486, 2 negative
(h8-v2::verified-wbf-scale-4 -0.0003;
proposer-verifier-512::verified-adversarial-text -0.0366, the run
sidelined in S107, whose verifier cut recall on an already-precise
twin); MCC uplift median +0.427, range -0.023 to +0.841, 3 negative. By
frame (F1 n, median): 55-map strata 59, +0.353; GS Era-2 53, +0.138;
grid-common 21, +0.194; Era-1 5, +0.037; Era-3 4, +0.005; px256 3,
+0.398. The paper headline
pv-diag-384::verified-adv-text-consensus-16of30 (0.8902) gains +0.2132
F1 / +0.3928 MCC over its 16-of-30 consensus. [AMENDED 2026-09-11, S153:
85 -> 128 by the four absence-refusal rules of 2026-09-10, -> 129 by the
44th ready twin, -> 145 by two null-vote-threshold rules (single-pass
cells route to the single-pass rule at k = 1; k-of-N pool names are
parsed). Signed text at 2026-09-10: '85 of 172 pairs computed on F1 and
MCC (86 blocked, disclosed with reasons). F1 uplift median +0.212, range
-0.0003 to +0.486, 1 negative; GS Era-2 frame 19 pairs (median +0.138),
55-map strata 41 pairs (median +0.300).']']
```

### 4.14 `uplift-supplement-flatten`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
505 registered conditions flattened into 130 strata (corpus x reference
x buffer x frame); 505 carry a headline-buffer F1; 153 board-frame rows
excluded by rule; headline references r2 (55-map) and curator (GS).
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
[-441-] {+505+} registered conditions flattened into 130 strata (corpus
x reference x buffer x frame); [-441-] {+505+} carry a headline-buffer
F1; [-79-] {+153+} board-frame rows excluded by rule; headline
references r2 (55-map) and curator (GS).
```

### 4.15 `null-exemplar-sensitivity-2026-09-13`

Signature: **re-sign-pending**. Drafted outcome, for the PI's approval (not applied):

```text
SPLIT — the leak signature is real and the boards barely move. (1)
SIGNATURE, on the full frames: on the Era-2 board an image-bearing
cell's false-positive rate on the 20 exposed tiles is 0.561x its rate on
the other 467, against 0.685x for a text control (mean log ratio -0.1433
vs -0.0552; difference -0.0881, p < 1e-4 by 10,000-draw label
permutation, seed 42). It is not a between-run confound: restricted to
pv-diag-384, which supplies 54 image and 61 text cells from one
pipeline, the difference is -0.0773, p < 1e-4. The three Era-1 boards
are null unstratified (p 0.25-0.45); stratifying by run lifts
era1-leaderboard to -0.0705 (p 0.021) but heterogeneously
(retest-phase3a -0.235, retest-phase2c +0.139). (2) PER-CELL: on the
Era-2 board no cell's F1@20 moves more than 0.0074 and no cell's
tile-MCC more than 0.0120; mean deltas -0.00213 (image) vs -0.00275
(text) for F1 and -0.00126 vs -0.00286 for MCC — the reduction costs the
image cells LESS, not more, because the exposed tiles hold 12 of the
frame's 435 references as well as the quiet ground. The Era-1 boards
move an order of magnitude more (mean delta F1 -0.015 to -0.021) because
their reduction removes 9.6% of the positives against 2.8%; that frame
effect is shared by every cell, which is why the text controls and not
zero are the reference. (3) THE BOARD REBUILT (against the Era-2 board
as committed before the S164 restatement, whose full-frame figures stand
on the left of each arrow; the restated board has 8075 significant F1
pairs, 14 tiers, a Tier 1 of 5 cells, 3001 significant tile-MCC pairs, 6
MCC tiers, an MCC Tier 1 of 34, and Hsu MCB admissible sets of 52 (F1)
and 60 (tile-MCC), and the reduced-frame rebuild has not been re-run on
it): tie-set EDGES do move. F1 7961 -> 7905 significant pairs of 11,175,
14 -> 13 tiers, Tier 1 5 -> 4 cells — and the cell it loses is the TEXT
cell g37-text-k10-verified-carried-p0.10-k10, both image cells staying.
tile-MCC 2982 -> 3118 significant, 6 -> 7 tiers, Tier 1 33 -> 28 (7
leave, 2 join, all image, none of them a leader). Hsu MCB admissible: F1
65 -> 66, tile-MCC 59 -> 57. UNCHANGED: F1 ranks 1-4 and tile-MCC ranks
1-7 in the same order, the selection-aware argmax winner under both
metrics, the three cells the tile-join invariant withholds, Spearman
0.9989 between the rankings with a largest rank shift of 8 and only 2
cells moving by more than one tier. Paired tile-swap (10,000 draws, seed
42) between each image cell and its nearest full-frame-F1 text
comparator: 6 of 118 Era-2 verdicts cross alpha = 0.05, every one from
just above to just below with the pair difference growing, none
reversing sign; zero flips on any Era-1 board. (4) VERDICT on the two
exposed claims: Obs 482's 'image leads tile-MCC' and the Gemini 3.7
image cell's F1 Tier-1 placement BOTH STAND and need a disclosure rather
than a qualifier — across the 59 paired comparisons the image-over-text
tile-MCC advantage is +0.0848 on the full frame and +0.0852 on the
reduced one (a change of +0.0004), the tile-MCC leaders shed at most one
false positive each across all 20 leaked tiles, and the 3.7 image cell
keeps rank 1 while its lead over the 3.7 text cells narrows by 0.0010.
Any text quoting a tie-set SIZE is frame-specific and should say so.
Incidental: 7 Era-2 cells' exposure differs from the board's own 'track'
field — three proposer-verifier '-image' cells are text-proposer (track
names the verifier) and the four pv-scale4-optimal cells are
image-bearing (detect_h8_scale-4_v2, include_example_images true), two
of them in tile-MCC Tier 1. The board was not changed. NOT RE-RUN AFTER
THE S164 RESTATEMENT: 14 of the 150 Era-2 cells (4 image-bearing, 10
text) were re-scored, so every Era-2 figure in (1) to (4) except the
pv-diag-384 restriction predates them; the Era-1 figures are unaffected.
Artefacts: results/null-exemplar-sensitivity-2026-09-13/.
```

Word-level diff against the current outcome (`[-removed-]{+added+}`):

```text
SPLIT — the leak signature is real and the boards barely move. (1)
SIGNATURE, on the full frames: on the Era-2 board an image-bearing
cell's false-positive rate on the 20 exposed tiles is 0.561x its rate on
the other 467, against 0.685x for a text control (mean log ratio -0.1433
vs -0.0552; difference -0.0881, p < 1e-4 by 10,000-draw label
permutation, seed 42). It is not a between-run confound: restricted to
pv-diag-384, which supplies 54 image and 61 text cells from one
pipeline, the difference is -0.0773, p < 1e-4. The three Era-1 boards
are null unstratified (p 0.25-0.45); stratifying by run lifts
era1-leaderboard to -0.0705 (p 0.021) but heterogeneously
(retest-phase3a -0.235, retest-phase2c +0.139). (2) PER-CELL: on the
Era-2 board no cell's F1@20 moves more than 0.0074 and no cell's
tile-MCC more than 0.0120; mean deltas -0.00213 (image) vs -0.00275
(text) for F1 and -0.00126 vs -0.00286 for MCC — the reduction costs the
image cells LESS, not more, because the exposed tiles hold 12 of the
frame's 435 references as well as the quiet ground. The Era-1 boards
move an order of magnitude more (mean delta F1 -0.015 to -0.021) because
their reduction removes 9.6% of the positives against 2.8%; that frame
effect is shared by every cell, which is why the text controls and not
zero are the reference. (3) THE BOARD [-REBUILT:-] {+REBUILT (against
the Era-2 board as committed before the S164 restatement, whose
full-frame figures stand on the left of each arrow; the restated board
has 8075 significant F1 pairs, 14 tiers, a Tier 1 of 5 cells, 3001
significant tile-MCC pairs, 6 MCC tiers, an MCC Tier 1 of 34, and Hsu
MCB admissible sets of 52 (F1) and 60 (tile-MCC), and the reduced-frame
rebuild has not been re-run on it):+} tie-set EDGES do move. F1 7961 ->
7905 significant pairs of 11,175, 14 -> 13 tiers, Tier 1 5 -> 4 cells —
and the cell it loses is the TEXT cell
g37-text-k10-verified-carried-p0.10-k10, both image cells staying.
tile-MCC 2982 -> 3118 significant, 6 -> 7 tiers, Tier 1 33 -> 28 (7
leave, 2 join, all image, none of them a leader). Hsu MCB admissible: F1
65 -> 66, tile-MCC 59 -> 57. UNCHANGED: F1 ranks 1-4 and tile-MCC ranks
1-7 in the same order, the selection-aware argmax winner under both
metrics, the three cells the tile-join invariant withholds, Spearman
0.9989 between the rankings with a largest rank shift of 8 and only 2
cells moving by more than one tier. Paired tile-swap (10,000 draws, seed
42) between each image cell and its nearest full-frame-F1 text
comparator: 6 of 118 Era-2 verdicts cross alpha = 0.05, every one from
just above to just below with the pair difference growing, none
reversing sign; zero flips on any Era-1 board. (4) VERDICT on the two
exposed claims: Obs 482's 'image leads tile-MCC' and the Gemini 3.7
image cell's F1 Tier-1 placement BOTH STAND and need a disclosure rather
than a qualifier — across the 59 paired comparisons the image-over-text
tile-MCC advantage is +0.0848 on the full frame and +0.0852 on the
reduced one (a change of +0.0004), the tile-MCC leaders shed at most one
false positive each across all 20 leaked tiles, and the 3.7 image cell
keeps rank 1 while its lead over the 3.7 text cells narrows by 0.0010.
Any text quoting a tie-set SIZE is frame-specific and should say so.
Incidental: 7 Era-2 cells' exposure differs from the board's own 'track'
field — three proposer-verifier '-image' cells are text-proposer (track
names the verifier) and the four pv-scale4-optimal cells are
image-bearing (detect_h8_scale-4_v2, include_example_images true), two
of them in tile-MCC Tier 1. The board was not changed. {+NOT RE-RUN
AFTER THE S164 RESTATEMENT: 14 of the 150 Era-2 cells (4 image-bearing,
10 text) were re-scored, so every Era-2 figure in (1) to (4) except the
pv-diag-384 restriction predates them; the Era-1 figures are
unaffected.+} Artefacts: results/null-exemplar-sensitivity-2026-09-13/.
```

## 5. Surprises

Flagged under the project's research-finding calibration rule; none is
explained away.

1. **Four bridge readings change, not only numbers** (§ 1.7, § 2.6;
   `results/modality-bridge-2026-10-07/findings.md` §§ 6–8): two K-matched
   gap changes now clear their upper floors (1.0942 and 1.0146 of them), so
   § 7's "none clears its upper bound" fails; the Gemini 3 T 1.0 text
   advantage falls inside its upper bound (1.03 → 0.98; 0.9956 with the
   measured verifier noise); § 7a's three sub-unit "each cell at its upper"
   readings become one (0.9561); and the 3.7 image carried original's § 6
   "oracle" is its registered point (0.9353 at (0.10, k5)), not its new best
   (0.9381 at (0.05, k5)).
2. **The overlap reversal at 384 px no longer clears** (−0.0256
   [−0.0517, +0.0001], p 0.0541; it holds at 512 px), and **I3 fails on
   the 3.7 image carried arm** (its optimum is (0.05, k5), not the
   registered (0.10, k5)); both are stated as failures in the restated
   findings (`d6e2f40e8`) and in the drafted outcomes (§ 4).
3. **The fourth cell's head-to-head crosses 0.05** (p 0.0563 → 0.0311,
   +0.0203). Its outcome claims no significance, so the drafted text
   reports the new p without a new claim.
4. **The fourth cell's board-frame argmax moved** off its registered point
   ((0.98, k10), 0.9141 → (0.95, k10), 0.9144), so its sweep-optimism run
   on the board frame failed the anchor gate the plan expected it to pass
   (§ 2.2). Its own GS frame's argmax does not move.
5. **The board's display moved where the prediction did not**: tier E's
   four cells now show their S9 re-scored evaluations, which changes three
   tier labels with every pairwise test identical (§ 2.2).
6. **The 3.7 image carried arm loses to its own union twin** on F1 (0.9353
   against 0.9370) and on tile-MCC; its uplift is −0.0017 F1, the negative
   D65 (4) asked to have reported.
7. **The Phase 2 builder now withholds six Gemini 3 `pv-diag-384` ladders
   from its compatibility inventory** on the D51 clipped basis ("until the
   clipped cells exist"), so the committed MCB sets and the Phase 2 tile-MCC
   test for those ladders rest on as-evaluated (unclipped) rungs the
   inventory no longer lists. A tier-1 join test now pins that gap
   (`8df0522ff`); the question is for the PI (§ 10).
8. **`--allow-undetermined-area` is a silent hazard.** In a partial copy
   every ladder's assessed area was UNDETERMINED and the flag let all 14
   through unclipped, logging ERROR lines but exiting 0 (§ 2.3, step 5).
   The runs used are whole-tree copies, where the gate determined all
   areas and clipped seven.
9. **§ 1.3's membership-derivation drift.** Re-deriving the board's
   `membership.json` today gives 98 members instead of 110, because the
   derivation reads register edits made since 2026-09-14. The pass kept
   the membership and refreshed only its snapshot fields; the drift of the
   rule is for the PI (§ 10).

   **Corrected 2026-10-18 (Session 165):** the 98 is not a drift in the
   rule. Re-derived read-only on the full branch checkout
   (`build_gs_era2_board.derive_membership()` at `26deb34a3`), the
   membership is the same 110 members, none dropped or added. The 98
   came from running the derivation inside the board's partial copy
   (`mkcopy_board.sh`), where exactly 12 members' detection files lie
   outside the copied directories (eight `proposer-verifier-384` cells,
   three `verifier-t-pilot` cells, and
   `pv-diag-384::verified-adv-text-consensus-16of30`), so the derivation
   skipped them as missing on disk; all 110 files are tracked. The match
   is by count, since the 98-member list was not recorded. The PI
   accepted keeping the membership (D69).

10. **Two stalenesses older than the pass** surfaced in the uplift lane:
    the committed pairing CSV predated D57 (4)'s twin re-scores (it
    disagreed with its own twin evaluations on 28 F1 and 20 MCC rows), and
    the flatten's outcome ("441 … 79 board-frame rows excluded") was
    already stale at the branch point (439 and 153).
11. **The engine's MCC intervals for the eight 55-map extended-reference
    cells move**, which the S9 replay did not predict (§ 2.5).
12. **Five more signed rows lapse than the ten of `ed91d2df8`** (§ 3):
    the Era-2 board, the K ladders, the uplift pairing and flatten, and the
    null-exemplar sensitivity, whose quoted full-frame "before" figures are
    the board's.
13. **E72's flip may no longer hold.** Recomputing the BH adjustment on
    the regenerated pairwise p values gives E72's 23-member Group 7 a q of
    0.0483, where the branch point reproduces 0.050735. This is a
    sub-agent's own computation (`records/docs/docs2-notes.md`), not the
    E72 generator's, whose regeneration is held for a ruling (§ 1.5); it is
    not in any committed document.
14. **The GS plateau characterisation is stale beyond the pass.** Its
    generator (`scripts/characterise_gs_plateau.py`), run twice on the
    final manifests (identical), moves rows no lane touched
    (`n1-outstanding-384` and `pv-diag-384` cells by about +0.0015 to
    +0.0023, from re-scores before the pass), counts 65 more non-GS
    conditions skipped, and drops `g37-text-k1-verified-opmax` (0.8495,
    which the pass restates to 0.8747) from the analysed set without an
    explanation found. It was not committed; § 10 item 16.

    **Corrected 2026-10-20 (Session 165):** nothing is dropped.
    Regenerated on the full branch checkout, the characterisation
    analyses the same 459 conditions as the committed file,
    `g37-text-k1-verified-opmax` among them; that cell only leaves the
    late-plateau table (onset at 50 m or later), because its restated
    curve plateaus earlier. The 65 extra skipped conditions are the
    non-GS registrations since the file was built. The PI ruled to
    regenerate it in this PR (D69, § 10 Q16).

## 6. Claim rows affected (the inventory is not edited)

The Results claims inventory
(`docs/paper/results-claims-inventory-2026-09-12.md`) is frozen as the
2026-09-12 snapshot under PI ruling D55 Q1, "with dated notes, until the
Results re-draft; no reclassification or recount now". The pass does not
edit it; this table is for the PI and the re-draft. Built by a read-only
Opus sub-agent from the files at `718d0ee08` and `0fc2d6389` (the bridge
from its candidate outputs, which `d6111dafb` committed unchanged apart
from the findings text); the re-score's § 4 and the S163
`scorer-restatement-inventory.md` were the starting prediction. Rows found
by (a) every row whose anchor names a changed artefact and (b) a search of
every claim's text for every value that moved; rows on artefacts the pass
did not touch (55-map boards, Pareto v2, the Era-1 board, H13, Phase 3)
were not re-read one by one. F1 at 20 m on the 487-tile frame unless
stated; "already stale" means the branch-point file already differed from
the inventory's quote (the board rebuilds of 2026-09-13 and 2026-09-14,
the D42 p-value regeneration of 2026-10-05, or the S9 drift), and those
cells read quote → branch point → regenerated.

**Counts**: 39 rows in the table. **28 restate** (the verdict survives and
numbers move); three of them, and two of the failures, carried p values
already stale under D42, and two (R3-14, R6-17) carried the S9 drift. **3 fail**: R1b-09 at 384 px, R1b-15's 30 m
sentence, and R1b-16's shared 30 m shelf. **8 were already stale before
the pass** (R4-17, R4-18, R4-20 to R4-24, and R4-28); the pass moves seven
of them again and leaves R4-17 alone. **30 checked rows hold**: 27
verbatim, and three whose claim text holds while a number in their note
or anchor moved.

### 6.1 Table

| Row | Quoted (inventory, short) | Committed → regenerated (source) | Verdict | Proposed wording |
|---|---|---|---|---|
| R1b-02 | 50 % overlap costs +0.1200 (512 px) and +0.1348 (384 px); 384 px costs −0.0824 (12.5 %) and −0.0972 (50 %); all four exclude zero | +0.1200 → +0.1207; +0.1348 → +0.1381; −0.0824 → −0.0803; −0.0972 → −0.0976; all four intervals still exclude zero (`results/grid-2026-08-18/grid_analysis.json`; `findings.md` contrast table) | Restates | "… 50 % overlap costs +0.1207 F1 at 512 px and +0.1381 at 384 px; 384 px costs −0.0803 at 12.5 % overlap and −0.0976 at 50 %. All four exclude zero …" |
| R1b-03 | Interaction −0.0148 [−0.0552, +0.0268], p = 0.4902 | Quote → BASE p 0.4681 (D42) → −0.0173 [−0.0580, +0.0248], p 0.4033 (same files) | Restates (p already stale, D42) | "The interaction is unresolved: difference-of-differences −0.0173 [−0.0580, +0.0248], p = 0.4033 …" |
| R1b-04 | At 50 % the filter keeps recall near 0.87–0.89 and lifts precision 0.156 → 0.531 (512 px) | Corroborated shares 7.0 / 7.7 / 40.8 / 41.7 % unchanged; recall 0.87–0.89 → 0.88–0.91; precision 0.156 → 0.531 becomes 0.159 → 0.536 (384 px: 0.123 → 0.367 becomes 0.125 → 0.374) (grid `findings.md`) | Restates | "… while at 50 % it keeps recall near 0.88–0.91 and lifts precision 0.159 → 0.536 (512 px)." |
| R1b-05 | K = 10 consensus board 512/50 % 0.7518, 384/50 % 0.7205, 512/12.5 % 0.6759, 384/12.5 % 0.6475 | → 0.7611 / 0.7293 / 0.6845 / 0.6574; ranking unchanged (`grid_analysis.json`; `findings.md` consensus-only board) | Restates | "… 512/50 % **0.7611**, 384/50 % 0.7293, 512/12.5 % 0.6845, 384/12.5 % 0.6574." |
| R1b-06 | 384/12.5 % K = 10 (union recall 0.8925, F1 0.6475, $2.91) loses to 512/50 % K = 3 (0.9229, 0.7429, $1.60) | Recall 0.8925 → 0.9112, F1 0.6475 → 0.6574; 0.9229 → 0.9416, 0.7429 → 0.7500; ΔF1 −0.0953 → −0.0926; Δrecall −0.0304 and costs unchanged (grid `findings.md` head-to-head) | Restates | "… 384/12.5 % at K = 10 (union recall 0.9112, best F1 0.6574, $2.91) loses to 512/50 % at K = 3 (0.9416, 0.7500, $1.60) …" |
| R1b-07 | One pass of 512/50 % (0.7121, $0.53) beats ten of either 12.5 % cell (0.6759; 0.6475) | 0.7121 → 0.7186; 0.6759 → 0.6845; 0.6475 → 0.6574; costs unchanged (same) | Restates | "… one single pass of 512/50 % (F1 0.7186, $0.53) beats ten passes of either 12.5 % cell (0.6845 at $1.90; 0.6574 at $2.91)." |
| R1b-08 | Post-verifier board 384/50 % 0.8961, 512/50 % 0.8815, 384/12.5 % 0.8677, 512/12.5 % 0.8311 | → 0.9017 / 0.8870 / 0.8761 / 0.8368; ranking unchanged. 384/12.5 %'s best point moved (0.20, k7) → (0.15, k7); its registered condition keeps (0.20, k7) at 0.8752 (D65 (3)) (`verifier_analysis.json`; `conditions-verified/`; `findings.md`) | Restates | "… 384/50 % **0.9017**, 512/50 % 0.8870, 384/12.5 % 0.8761 (its registered condition, at (0.20, k7), 0.8752), 512/12.5 % 0.8368." |
| R1b-09 | Overlap reversal survives the verifier at about half the margin: −0.0504, p 0.0004 (512 px); −0.0285, p 0.0208 (384 px); baselines −0.0758, p 0.0004 and −0.0730, p 0.0026 | Quote → BASE (D42) −0.0504, p 0.0003; −0.0285 [−0.0530, −0.0045], p 0.0235; −0.0758, p 0.0008; −0.0730, p 0.0032 → 512 px −0.0502, p 0.0003; **384 px −0.0256 [−0.0517, +0.0001], p 0.0541**; baselines −0.0766, p 0.0006 and −0.0718, p 0.0037 (`verifier_analysis.json` contrasts; `findings.md` Question 2) | **Fails at 384 px**; holds at 512 px (p already stale, D42) | "**The overlap reversal survives the verifier at 512 px but not at 384 px**: (12.5 − 50) = −0.0502, p = 0.0003 at 512 px; at 384 px the point estimate still favours 50 % (−0.0256 [−0.0517, +0.0001]) but p = 0.0541, so the reversal is no longer significant there; against a K = 10 consensus baseline of −0.0766, p = 0.0006 and −0.0718, p = 0.0037." ("About half the margin" goes: at 512 px the ratio is 0.66.) |
| R1b-10 | Baseline (384 − 512) −0.0284, p 0.281 and −0.0312, p 0.089; the verifier flips the sign, significantly at 12.5 % (+0.0366, p 0.034), unresolved at 50 % (+0.0147, p 0.231) | Quote → BASE p 0.298 / 0.094 / 0.037 / 0.235 (D42) → −0.0271, p 0.308; −0.0319, p 0.086; +0.0393, p 0.027; +0.0147, p 0.245 (same) | Restates (p already stale, D42) | "… (384 − 512) = −0.0271, p = 0.308 at 12.5 % and −0.0319, p = 0.086 at 50 % … significantly at 12.5 % (+0.0393, p = 0.027) and unresolved at 50 % (+0.0147, p = 0.245)." |
| R1b-11 | Verifier gain +0.130 to +0.220, 384 px +0.220 and +0.176; ceilings 0.8925 / 0.9509 against 0.8715 / 0.9416 | → +0.126 to +0.219; 384 px +0.219 and +0.172 (still the largest); ceilings 0.9112 / 0.9696 against 0.8879 / 0.9603 (grid `findings.md`) | Restates | "… **+0.126 to +0.219**, largest … (the two 384 px cells, +0.219 and +0.172) … ceilings (0.9112 / 0.9696 against 0.8879 / 0.9603) …" |
| R1b-12 | Best points keep k ≥ 5..10; pure verifier tops out at 0.8153, trailing by 0.052–0.203 | k ≥ 5..10 unchanged; 0.8153 → 0.8187; 0.052–0.203 → 0.057–0.207 (`verifier_sweep.csv`; `findings.md`) | Restates | "… the pure-verifier k = 1 board tops out at 0.8187, trailing the stacked optimum in every cell by 0.057–0.207." |
| R1b-14 | 384 px ladder 0.8677 → 0.8982 → 0.8961 → 0.8860; +0.0305 [+0.0052, +0.0564], p 0.020; 256 vs 192 +0.0020, p 0.862; 144 rung p 0.297 / 0.360 | Quote → BASE p 0.022 / 0.866 / 0.284 / 0.352 (D42) → 0.8761 → 0.9075 → 0.9017 → 0.8938; +0.0314 [+0.0057, +0.0577], p 0.020; +0.0059, p 0.640; 144 vs 256 −0.0137, p 0.223; vs 192 −0.0079, p 0.481 (`results/stride-2026-08-25/stride_verifier_analysis.json`; `findings.md`) | Restates (p already stale, D42) | "The 384 px ladder reads 0.8761 (stride 336) → **0.9075** (256) → 0.9017 (192) → 0.8938 (144): 336 → 256 is significant (+0.0314 [+0.0057, +0.0577], p = 0.020), the top is flat (256 vs 192: +0.0059, p = 0.640), and the 144 rung falls away (p = 0.223 / 0.481)." |
| R1b-15 | 6 of 78 pairs significant, all with 512/12.5 %; Tier 1 the other twelve; best new cell ties the grid winner (+0.0020, p 0.862); at 30 m the top three indistinguishable to the third decimal; no new GS F1 high from geometry; shelf ~0.896–0.898 @ 20 m, ~0.903 @ 30 m | 6 of 78 → 6 of 78, **the same six pairs**; tiers 12 + 1 unchanged; +0.0020, p 0.866 → +0.0059, p 0.640; **30 m 0.9031 / 0.9034 / opmax 0.9031 → 0.9124 / 0.9089 / opmax 0.9173**; best geometry cell against opmax at 20 m +0.0140, p 0.291 → +0.0116, p 0.380 (now above every incumbent; opmax 0.8842 → 0.8960); shelf ~0.896–0.898 → ~0.902–0.908 @ 20 m, no common 30 m shelf (`plateau_analyses.json` → `board_13cell`; stride `findings.md` Question 3) | **Fails in part**: "6 of 78" and the tiers survive verbatim; the 30 m sentence fails; "no new high" holds statistically only | "… **6 of 78 pairs significant, all involving 512/12.5 %**, Tier 1 holding the other twelve cells including all four incumbents; the best new cell ties the grid winner (+0.0059, p = 0.640). At 20 m the best geometry cell's point estimate (0.9075) sits above every incumbent's (+0.0116 over opmax, p = 0.380) without leaving their tier, so geometry gives no statistically new GS F1 high; the 20 m shelf is ~0.902–0.908. At 30 m the three no longer agree: opmax 0.9173 against 0.9124 (384/33.3 %) and 0.9089 (384/50 %), point estimates with no paired test." |
| R1b-16 | ≈ $6.6 against ≈ $10.7 (384/50 %) and ~$50-class for the HIGH-thinking incumbents **that share the 30 m shelf** | Tiles (820 against 1,398) and costs unchanged; at 30 m opmax 0.9031 → 0.9173, registered headline 0.8958 → 0.9054, best geometry cell 0.9031 → 0.9124 (`plateau_analyses.json`; stride `findings.md` Question 3 and changelog) | **Fails in part**: the cost claim survives; "share the 30 m shelf" fails | "… for ≈ $6.6 all-in against ≈ $10.7 (384/50 %) and ~$50-class for the HIGH-thinking incumbents, which share its 20 m tier but not a 30 m shelf (opmax 0.9173 above the best geometry cell's 0.9124, the registered headline 0.9054 below it; point estimates, no 30 m test)." |
| R1b-17 | Exact ladder 0.8677 / 0.8911 / 0.8856 / 0.8982; N = 3 within 0.007 of K = 10 at 40 % of its cost (note: board frame 0.8605 / 0.8834 / 0.8782 / 0.8905) | → 0.8737 / 0.8993 / 0.8937 / 0.9075; gap 0.0071 → 0.0083; costs and the ~19× unchanged; board frame → 0.8665 / 0.8916 / 0.8862 / 0.8999, frame tax still −0.0072 to −0.0077 (`plateau_analyses.json` → `winner_ladder_exact`; `results/k-ladder-2026-09-12/ladders.json`; `board-frame/stride-phaseb__g384-ov128-*`) | Restates | "… F1@20 m 0.8737 / **0.8993** / 0.8937 / 0.9075 … N = 3 reaches 0.8993 for $2.64 — within 0.008 of the full K = 10 winner at 40 % of its cost …" |
| R3-11 | K = 3 takes 37–93 % of the gain for 31–62 % of the cost; last step dearest on 17 of 23, at about US$0.21 to US$43 per 0.001 F1 | 3.7 GS ladder K = 5 → 10: 0.9066 → 0.9068 (+0.0002 for US$8.68, about US$43) becomes 0.9165 → 0.9169 (+0.0004, about US$21.7; clipped and as evaluated alike); K = 3 shares stay inside 37–93 % (3.7 ladder 65 % → 80 % clipped; GS stride A 77 % → 76 %); efficient sets and the 17-of-23 count unchanged; the next dearest last step is unchanged (55-map stride B, about US$17) (`phase2/ladders.json`; `ladders.json`) | Restates | "… the last step is the dearest per 0.001 F1 on 17 of the 23 ladders, at **about US$0.21 to about US$22 per 0.001 F1** where it gains F1." |
| R3-13 | The GS ladder's +0.0135 tests at BH p = 0.7678 | → +0.0130 (0.013043), BH p 0.7633 (`mcc-test/summary.json`, `gs-stride-a`) | Restates (the 21 / 16 counts: note 5) | "… the gold-standard ladder's +0.0130 — tests at BH p = 0.7633." |
| R3-14 | K = 1 → 10: +0.0572 (MCC +0.0444) consensus-only; +0.0340 (MCC −0.0308) verified; the verifier absorbs 40.6 %; swing 0.0752 | Consensus-only 0.6633 → 0.7205 becomes 0.6633 → 0.7293 (+0.0660), MCC +0.0444 unchanged; verified (tier E) 0.8546 → 0.8886 becomes 0.8680 → 0.8942 (+0.0262), MCC 0.8211 → 0.7903 becomes 0.8211 → 0.7973 (−0.0238); 40.6 % → 60.3 %; swing 0.0752 → 0.0682 (`tension/grid-overlap.json`; `tier-e/ladder.json`) | Restates; the sign reversal survives (partly stale before the pass: S9's drift alone gives 68.8 %) | "… raises F1@20 by +0.0660 with tile-MCC **rising** +0.0444 consensus-only, and by only +0.0262 with tile-MCC **falling** −0.0238 once the same pool is verified: the verifier absorbs **60.3 %** of K's F1 return and reverses the sign of its tile-MCC effect, a swing of 0.0682." |
| R3-15 | Deployment range +0.0192..+0.0547 sits inside the GS range +0.0139..+0.0629 | GS top (MINIMAL image T 0.7) +0.0629 → +0.0600 on the clipped basis (D51; +0.0629 kept as the as-evaluated history); GS stride A +0.0305 → +0.0338 (BH p 0.0072 → 0.0024); deployment ladders unchanged (`phase2/ladders.json` summary; `ladders.json`; `mcc-test/summary.json`) | Restates; survives | "… and the deployment range +0.0192..+0.0547 sits **inside** the gold-standard range +0.0139..+0.0600." |
| R6-16 | About US$17 (55-map stride B) and about US$43 (3.7 family) per 0.001 F1, against about US$1.05 (HIGH text T 1.0); last step dearest on 17 of 23 | 3.7: about US$43 → about US$22 (+0.0004 for US$8.68); HIGH text T 1.0 +0.0116 → +0.0117 for the same US$12.23, still about US$1.05 (clipped); the rest unchanged (`phase2/ladders.json`) | Restates | "… about US$17 per 0.001 F1 for 55-map stride B's K = 5 → K = 10, and **about US$22** per 0.001 F1 for the 3.7 family's, against about US$1.05 …" |
| R6-17 | The verifier absorbs 40.6 % (+0.0572 against +0.0340); tile-MCC +0.0444 against −0.0308 | As R3-14: 60.3 % (+0.0660 against +0.0262); +0.0444 against −0.0238 | Restates; "the verifier takes the larger share" survives (partly stale, S9) | "… the verifier absorbs **60.3 %** of K's F1 return (+0.0660 consensus-only against +0.0262 verified) and reverses the sign of its tile-MCC effect (+0.0444 against −0.0238)." |
| R4-04 | Verified 384 px margin over the best consensus-only configuration (0.890 against 0.814) exceeds the bar | Consensus champion (HIGH text 26-of-30) 0.8141 → 0.8165; H2 rider +0.076 → +0.074, still ≥ 0.05 (pairwise lane, PR #37 route: `results/family-fdr/family_fdr.md` § 2 and changelog 2026-10-15; `results/diversity-dividend-384/tiering-champions/tiering_20m.json`) | Restates | "… (0.890 against 0.817) exceeds the registered adoption bar." |
| R4-17 | 79 verified cells (39 register + 40 sweep optima) on one frame, 487 tiles, 435 mounds | Quote → BASE 153 admitted, 150 tiered, 3 withheld → NEW unchanged (membership kept, pass § 1.3) (board `README.md`) | **Already stale**; not moved by the pass | "The GS Era-2 verified board admits 153 cells (150 tiered, 3 withheld) on one frame … (487 tiles, 435 reference mounds)." |
| R4-18 | 3,081 pairs, 1,845 significant, seven tiers | Quote → BASE 11,175 / 7,961 / 14 → 11,175 / **8,075** / 14 (`tiering_20m.json`; `README.md`) | **Already stale**; moved again | "Of 11,175 pairs, 8,075 are significant at BH q = 0.05, giving 14 tiers." |
| R4-19 | Tier 1: 0.9233, 0.9190, 0.9182, 0.9179, 0.9068 | → 0.9332, 0.9289, 0.9282, 0.9278, 0.9169; the same five cells in the same order (the image carried cell scores its registered (0.10, k5) set) (`README.md` rows 1–5) | Restates | "… image under the 3.7 verifier 0.9332, text under 3.7 0.9289, text under 3.8 0.9282, image under the carried Gemini 3 verifier 0.9278, text at K = 10 under the carried verifier 0.9169." |
| R4-20 | MCB admissible set 28 of 79 | Quote → BASE 65 of 150 → **52** of 150 (`README.md`) | **Already stale**; moved again | "The Hsu MCB admissible set holds 52 of the 150 tiered cells." |
| R4-21 | Every Gemini 3 cell Tier 2 or below: best committed incumbent 16-of-30 0.8951 (rank 8); best sweep optimum HIGH text T0.3 K = 5 0.8873 (rank 11) | BASE: tier E's K = 5 optimum 0.8905 (rank 9) already outranked 0.8873 (rank 12) → NEW: tier E K = 5 0.9046 (rank 8, Tier 2); 16-of-30 0.8951 (rank 10, Tier 2); HIGH text T0.3 K = 5 0.8873 (rank 13, **Tier 3**) (`README.md`) | **Already stale** (named cells); "Tier 2 or below" holds | "Every Gemini 3 cell sits in Tier 2 or below: the best is tier E's K = 5 sweep optimum at 0.9046 (rank 8, Tier 2), then the 16-of-30 incumbent at 0.8951 (rank 10, Tier 2)." |
| R4-22 | 30 of 40 sweep optima significantly below the lowest Tier-1 cell; all 40 below the top | The 40 cannot be told apart by id (the inventory's own note). Board-wide `-opmax` ids, BH q 0.05: BASE 59 of 74 and 73 of 74 → 70 of 74 and 74 of 74 (`tiering_20m.json` pairwise; counted here) | **Already stale**; moved again | "Of the board's 74 `-opmax` cells, 70 are significantly below the lowest Tier-1 cell and all 74 below the top one." |
| R4-23 | Lowest Tier-1 cell against the best sweep optimum (HIGH text T0.3 K = 5): +0.020, p = 0.16, not significant | Quote (anchor p 0.1783, BH 0.2438) → BASE +0.0195, p 0.1783, BH 0.2198 → **+0.0296, p 0.0381, BH 0.0525**; against tier E's K = 5 cell (the best since 2026-09-13): +0.0163, p 0.2505 → +0.0123, p 0.3931, BH 0.4495 (`tiering_20m.json` pairwise) | **Already stale**; restates; raw p now below 0.05 (note 2) | "The lowest Tier-1 cell against the best sweep optimum (tier E's K = 5 cell, 0.9046): +0.012, p = 0.39, not significant; against the HIGH text T0.3 K = 5 cell: +0.030, p = 0.038, BH-adjusted 0.053, not significant after correction." |
| R4-24 | Top cell against it: +0.037, p = 0.011, BH 0.021 | Quote → BASE +0.0359, p 0.0158, BH 0.0234 → +0.0459, p 0.0016, BH 0.0027; against tier E's K = 5 cell: +0.0328, p 0.0112, BH 0.0170 → +0.0286, p 0.0304, BH 0.0425 (same) | **Already stale**; restates | "The top cell against the HIGH text T0.3 K = 5 cell: +0.046, p = 0.0016, BH-adjusted 0.0027; against tier E's K = 5 cell: +0.029, p = 0.030, BH-adjusted 0.042." |
| R4-25 | Optimism costs the 3.7 and 3.8 cells 0.0006 to 0.0035; corrected board-frame F1 0.9027 to 0.9215 | → +0.0008 (text K = 5 carried) to +0.0039 (grid verified37); corrected 0.9104 to 0.9314 (`optimism/README.md`, board-frame rows) | Restates (note 6) | "… costs the 3.7 and 3.8 cells 0.0008 to 0.0039, leaving corrected board-frame F1 of 0.9104 to 0.9314." |
| R4-28 | The analysis row was SIGNED by the PI on 2026-09-10 | Quote → BASE re-signed 2026-09-16T02:58:00Z (`results/run-analyses.json`) → NEW: the register still reads signed, but the restated README says the 2026-09-16 signature "attests the earlier numbers" | **Already stale**; needs re-signing | "The analysis row was re-signed by the PI on 2026-09-16 over the rebuilt board; the 2026-10-15 restatement moved its numbers, and it awaits re-signature." |
| R7.3-01 | 3.7 screen 0.9139 at (0.10, k5), 791-candidate union, ~$7.4 | → **0.9238** at (0.10, k5); union, unanimity, and cost unchanged (`results/gemini37-screen-2026-08-28/analysis.json` → `image_best`) | Restates | "… reached 0.9238 F1 at 20 m at (0.10, k5) …" |
| R7.3-04 | "the GS proposer gain of +0.018 did not transfer" | 0.9139 − 0.8961 = +0.0178 (p 0.17) → 0.9238 − 0.9017 = +0.0221 (p 0.097; not significant either way); the deployment numbers unchanged (same, `head_to_head_20m`) | Restates | "… the GS proposer gain of +0.022 did not transfer as a resolvable deployment win." |
| R7.3-11 | 3.8 0.9258 against 0.9265, −0.0007, p = 0.78; the instrument resolves about 0.011 (null SD 0.00379) | → 0.9358 against 0.9364, −0.0006, p 0.7769; null SD 0.00379 → 0.003745 (2.8 σ 0.0106 → 0.0105) (`results/gemini38-screen-2026-09-04/armV/pair_test.json`) | Restates | "It reached 0.9358 F1 at 20 m against the all-3.7 stack's 0.9364, a difference of −0.0006 at p = 0.78; … the paired instrument resolves about 0.010 …" |
| R7.3-12 | 3.8 joins Era-2 Tier 1 at 0.9182, third of five | → 0.9282, Tier 1, third of five; tokens and cost unchanged (board `README.md` row 3) | Restates | "… the 3.8 cell joins Tier 1 at 0.9282, third of the five …" |
| R7.3-21 | 3.7 image 0.9254 (G3 verifier) and 0.9308 (3.7 verifier), +0.084 / +0.090 over 0.8412 (I1); about five times the text-side gain | Arm 1 best moved (0.10, k5) 0.9254 → **(0.05, k5) 0.9381**, registered point kept at 0.9353 (D65 (3)); arm 2 0.9308 → 0.9408; anchor 0.8412 → 0.8458; +0.092 / +0.095; text-side gain +0.0221, so about four times (`results/gemini37-image-gs-2026-09-01/findings.md`; `arm1/`, `arm2/`; `results/image-b-gs-2026-08-28/analysis.json`) | Restates ("five" becomes "four"); I3 fails on this arm (note 1) | "The 3.7 image proposer scored 0.9381 at 20 m under the Gemini 3 verifier (at (0.05, k5); 0.9353 at its registered (0.10, k5)) and 0.9408 under the 3.7 verifier, +0.092 and +0.095 over the Gemini 3 image anchor of 0.8458 (I1), about four times the text-side gain." |
| R7.3-22 | Gap +0.0549 (p 0.001) in Gemini 3 → −0.0115 (p 0.25) and −0.0043 (p 0.68) in 3.7: parity | Register artefact: +0.0549 (p 0.001) → +0.0559 (p 0.0005); −0.0115 (p 0.25) → −0.0143 (p 0.16); −0.0043 (p 0.68) → −0.0043 (−0.00435, p 0.68) (`gemini37-image-gs-2026-09-01/gap_test.json`). Bridge, committed → candidate: Gemini 3 +0.0523 (p 0.0029) → +0.0536 (p 0.0018); 3.7 −0.0006 (p 0.95) → −0.0026 (p 0.77), −0.0023 (p 0.75) unchanged; gap changes −0.0529 / −0.0547 → −0.0562 / −0.0559 (p 0.0060 / 0.0031) (`gap_test.json`, `floors/gap_change.json`, `findings.md` changelog 2026-10-15) | Restates; parity survives in both | "The within-family text − image gap moved from +0.0559 (p = 0.0005) in Gemini 3 to −0.0143 (p = 0.16) and −0.0043 (p = 0.68) in 3.7, supporting parity rather than inversion (I2 overshot its prediction to zero)." If the bridge is cited: "the bridging replicate reads +0.0536 (p = 0.0018) against −0.0026 (p = 0.77) and −0.0023 (p = 0.75)." |
| R7.3-24 | All-3.7 image 0.9308 against text swap 0.9265, +0.0043, not significant, under MDE80 ≈ 0.024 | → 0.9408 against 0.9364, +0.0043 (p 0.68); MDE80 0.024 → 0.025 (`gap_test.json` → `all-3.7`; `results/sensitivity-mde-2026-08-28/sensitivity-mde.md`) | Restates; the decision holds | "… (all-3.7 image 0.9408 against the all-3.7 text swap's 0.9364, +0.0043, not significant and under MDE80 ≈ 0.025) …" |

### 6.2 Rows that hold

Re-read against the regenerated artefact. Each holds verbatim unless noted.

- **Instrument and frame**: R0-05 (10,000 permutations, seed 42, q 0.05), R0-07 and R1-11 (487 tiles, 20 m).
- **Grid and stride**: R1b-01 (design and costs). R1b-13: every
  iso-stride contrast stays non-significant (smallest p 0.084) and 384 px
  stays at or above at every stride. R1b-18: `k_curves.g384_ov128` best
  k 8, flat top [6, 7, 8, 9]; `g384_ov192` best k 10, [10]. R1b-22
  (selection space). R1b-19 to R1b-21 (H13, not re-run; PR #41 found it
  unmoved). R1b-23 (stride55).
- **Family false discovery rate (FDR)**: R2-09, R2-10, R2-11, R3-01, and
  R4-03. No p value and no rejection moves; only H2's rider moves
  (R4-04).
- **Consensus**: R3-02. The champions' lifts are now +0.129 to +0.429,
  which still rounds to the register's "+0.13 to +0.43". R4-12's claim
  text holds; its anchor's 0.814 is now 0.816.
- **K ladder**: R3-10 (the Phase 2 tiering was not re-run; note 5).
  R3-12: the F1 admissible sets are unchanged, tier E's tile-MCC set gains
  K = 10, K = 1 is still admissible on tile-MCC on 22 of 22 and highest on
  13. R6-11 and R6-14 (55-map and cost; unaffected). R6-18: its note's
  Obs 482 counts (65 and 59) now read 52 and 60, and the overlap was not
  recomputed here.
- **Era-2 board**: R4-26 (inference). R4-27: the claim's "0.007 to 0.008"
  holds (now 0.0070 to 0.0079), while the anchor's G6 maximum is 0.0078 →
  0.0079.
- **Model generation**: R7.3-02 (G1 fired; note 7), R7.3-03 (all three
  points unchanged: the fourth cell is still best at (0.98, k10), 0.9140 →
  0.9220), R7.3-20 (all five Tier-1 cells are 3.7 or 3.8 and every
  Gemini 3 cell is in Tier 2 or below), R7.3-23 (text beats image only in
  Gemini 3; the bridge agrees), and R7.3-29.

### 6.3 Notes

1. **Failures with no claim row.**
   - **I3 on the 3.7 image carried arm**: the arm's optimum moved to
     (0.05, k5), 0.9381 against 0.9353 at the registered (0.10, k5),
     outside the predicted 0.10–0.20. The 3.7-verifier limb holds at
     (0.90, k5) (`results/gemini37-image-gs-2026-09-01/findings.md`, I3
     row).
   - **The grid findings' Phase A paragraph**: the grid winner leads at
     20 m only, and it no longer clears min6 (+0.0339, p 0.020 → +0.0226,
     p 0.111).
   - **Two bridge readings in the candidate**: § 7's "none clears its upper
     bound" fails, because the two K-matched gap changes reach 1.09 and
     1.01. The Gemini 3 T 1.0 text advantage now falls inside its upper
     floor (1.03 → 0.98). R7.3-22 and R7.3-23 do not quote either reading.
2. **Surprise (flagged, not explained away)**: in R4-23 the raw p
   crosses 0.05 (0.1783 → 0.0381), so "not significant" now rests on BH
   (0.0525). S7 is the same pattern (the fourth cell's GS leg against the
   text-B anchor, p 0.0563 → 0.0311), but no claim row quotes it.
3. **Stale before the pass, on p values only**: R1b-03, R1b-09, R1b-10,
   R1b-14, and R1b-15 quote p values from before the D42 regeneration of
   2026-10-05. The table gives the BASE file's values.
4. **R3-14 and R6-17 carry the S9 drift**: today's scorer alone moves tier
   E's evaluations (K = 1 0.8546 → 0.8680), giving 68.8 % before any
   re-verified row enters. The pass reports 60.3 % unclipped, with the
   clipped reading of 48.8 % beside it for the PI (pass § 1.4).
5. **The Phase 2 clip (D51)**: the regenerated Phase 2 tables withhold
   tile-MCC on seven clipped ladders, and the Phase 2 tile-MCC test and
   tiering were not re-run (pass § 1.4). R3-10's "7 of 7 HIGH, 2 of 6
   MINIMAL", R3-12's MCC counts, and R3-13's "21 ladders, falls on 16"
   therefore still read the committed unclipped tests. That is for the
   PI. The two GS ladders' simultaneous F1 widths also move (GS stride A
   0.0160 → 0.0168, tier E 0.0151 → 0.0159). R3-15 and R6-11 cite the
   range in their notes.
6. **Registered point against argmax (D65 (3))**: 384/12.5 % is best at
   (0.15, k7) 0.8761, against 0.8752 at its registered point. 512/34.4 %
   is best at (0.15, k7) 0.8718, against 0.8714. The 3.7 image carried arm
   is best at (0.05, k5) 0.9381, against 0.9353. The Era-2 board scores the
   carried arm's registered set (0.9278), but its optimism row reads the
   argmax (0.9306 on the board frame). A wording that quotes "the arm's
   F1" must say which.
7. **R7.3-02**: G1's threshold is the planning card's pinned 0.8934. The
   restated Gemini 3 plateau at 20 m is ~0.902–0.908, and the 3.7 screen's
   lead over the text-B anchor (+0.0221, p 0.097) is not significant,
   before or after the pass. G1 fired as registered, so the row holds; a
   re-draft should not describe the screen as clear of the restated
   plateau.
8. **Signatures**: the status labels "SIGNED" on R1b-05, R1b-08, R1b-17,
   and the R7.3 screen rows now point at register rows the pass lapsed to
   `re-sign-pending` (`ed91d2df8`, ten rows). At NEW three rows whose
   quoted numbers moved are still recorded as signed. The k-ladder row's
   outcome quotes 40.6 %, 0.0752, and US$43,000. The gs-era2 board row's
   outcome quotes 7961/11175, "MCB admissible set = 65", and 0.9233. The
   stride-plateau row is the third, although its outcome does not quote
   the 30 m reading. Whether these lapse is § 1.8's work.

## 7. Integrity

**Two independent runs per artefact** (fresh processes, separate output
trees; records under `restatement-pass-scripts/records/`):

| Lane | Files | Run A against run B |
|---|---:|---|
| GS chain | 416 | 359 byte-identical, 57 identical after timestamps and run roots, 0 mismatched (`gs/runA-vs-runB.txt`) |
| Pairwise | 726 | all equal after normalising, 12 byte-identical (`pairwise/A-vs-B.txt`) |
| K-ladder, S9 cells and part 2 | 53 changed | equal apart from timestamps, one generation timestamp in part 2 (`kladder/s9-cells-compare.json`, `part2-compare.json`) |
| K-ladder step 5 (Phase 2 tables) | 4 | equal apart from generation timestamps; figure byte-identical (`kladder/phase2-compare.txt`) |
| Uplift twins; extended-reference cells | 81; 35 | equal (`uplift/twins-compare.json`, `extref-compare.json`) |
| Flatten and pairing | 10 | 10 byte-identical (`uplift/flatten-pairing-AB.txt`) |
| Era-2 board | 712 | 648 byte-identical, 63 after normalising, `frame-deltas.md` differing only in a gate timestamp (`board/runA-vs-runB.txt`) |
| Modality bridge | 73 | 67 byte-identical, 5 differing only in `meta.wall_seconds`, `logs/floors.log` only in timings (`bridge/cmp-all-A-vs-B.json`) |

**Kernel bad-page count** (`journalctl -k -b | grep -c "Bad page state"`,
boot of 2026-10-10 05:09 on sapphire): 0 before any run (2026-10-15
10:16Z), 0 before and after each K-ladder part (`lane-kladder/p1/s9/`,
`p2/bad-page.txt`), and 0 after the last run (2026-10-15T14:21:58Z).

**Red sentinels.** Every fix that changes how an analysis reads its
inputs has a tier-1 test that fails in a real-file copy of the previous
code: the registered points (`385877de0`, four tests), the sweep optimism
on origin (`92889e0e5`), the 3.7 opmax derivation (`1608a7604`), the
bridge floors and verifier SD (`02339bd98`, seven tests), and the Phase 2
table tests rewritten for the builder's new columns (`f743421a4`).

**Tier-1 at the head** (`ae62f6174` plus this record and the rebuilt
registry; one process, `pytest -m tier1`): 4,433 passed, 5 skipped,
3 xfailed, 0 failed. An earlier run in this session failed six tests,
each traced and resolved: the registry and run-report drift guards
(rebuilt; nine stale run reports regenerated in `ae62f6174`), two
Phase 2 table tests that read columns by position (`f743421a4`), and
two MCB tests, one pinning values `f53f6e97c` had moved and one
meeting the six withheld ladders (`8df0522ff`).

**Launch hygiene.** One early tier-1 launch on sapphire chained
`cd … &&` before `nohup`, so its ssh session stayed open until pytest
ended; it ran to completion and nothing followed it on the line.

## 8. Manifests, registry, and renderings

After every regeneration, the five further lapses, and the merge of
`origin/main` at `376eb1d50` (19 commits; no file overlapped the
branch's):

- `generate_post_run_report.py --all --write` (`3b5279634`): **ALL
  VALID** (44 runs, 658 conditions, 1,455 passes, 71 analyses against the
  schemas); signature status **15 re-sign-pending, 30 signed, 25
  unsigned, 1 unsigned-by-design**. Its 209 warnings are the previous
  run's, line for line.
- `generate_post_run_report.py --check-renderings`: five register
  renderings current.
- `verify_run_conditions.py`: 41 pass, 3 partial
  (`55maps-text-min-n10-uplift`, `e47-propose-brief`,
  `n1-outstanding-384`, runs no lane of the pass touched), 0 fail.
- `generate_run_reports.py --check`: nine of 40 generated run reports
  were stale; regenerated (`ae62f6174`), all 40 current (four
  hand-authored reports skipped by design).
- `build_generated_file_registry.py`, then `--check`: registry current,
  4,113 files (3,721 generated, 392 hand-written).

## 9. Documents restated, and documents left

**Restated in place** under the Document Revision Policy, each with a
2026-10-15 banner and changelog entry:

| Commit | Documents |
|---|---|
| `d6e2f40e8` | eleven findings: the grid (consensus-only and post-verifier), stride, Image-B, 3.7 image GS, selection-aware (grid pilots), sensitivity MDE, e45, the family FDR, the factor analysis, the diversity dividend, and the annotated 20 m leaderboard |
| `94d5815b3` | the 3.7 image GS findings: the all-3.7 gap rounded to −0.0044 (unrounded −0.0043504), with a same-day note |
| `8412f34bb` | the Era-2 board README: banner, changelog and the E86 disclosure restored by hand after `finalise`, with a dated note on the disclosure's figures |
| `d6111dafb` | the modality bridge findings (§ 2.6) |
| `de998a94d` | the K-ladder findings (§ 2.3; § 10 item 13 lists a pre-existing inconsistency left as it was) |
| `3a9ec2815` | the 55-map Gemini 3 image findings § 6; the K-ladder inventory's stride rows; the three hand-written paper tables (`results/paper-tables/`), which take the D60 (3) restated banner |

**Rewritten by their generators** with the regenerations: the cells'
`evaluation.md`, the tiering and MCB renders, `ladder-tables.md`,
`inventory-tables.md`, the uplift build report, the extended-reference
`report_autogen.md`, and the manifests' renders.

**Not restated**, because each needs an analysis re-run rather than a
text edit (§ 10, § 11): `results/null-exemplar-sensitivity-2026-09-13/findings.md`
(about eight stale full-frame values, and reduced-frame readings computed
on the pre-pass cells) and `results/student-baseline-2026-09-01/per-student-gs4/findings.md`
(about 14 values). `results/working-precision/gs-plateau-characterisation.md`
is generated from the conditions manifest; regenerating it was tried in
two runs (identical) and not committed (§ 5 item 14).

**Left as dated records** (§ 1.1 item 5): the S163 and S164 agent records,
the deltas reports, and about 28 reports, 8 results-side records and 15
planning cards that quote moved values as of their dates; the list is
`restatement-pass-scripts/records/docs/doc-sweep.md`, section (b).

## 10. For the PI

1. **The fifteen drafted outcomes** (§ 4): approve, redraft, or reject
   each; re-signature follows approval of the text.
2. **The stride board's reading of the grid cells** (§ 1.1 item 1, § 4):
   each cell's best point (as run; 384/12.5 0.8761) or its registered set
   (0.8752).
3. **Tier E's basis** (§ 1.4): restated unclipped, as the brief directed
   (K = 1 / 3 / 5 / 10 0.8680 / 0.8979 / 0.9046 / 0.8942), with the D51
   clipped reading beside it (0.8604 / 0.8902 / 0.8968 / 0.8942; § 8.6's
   share 48.8 % against 60.3 %). D51's text says tier E "takes the same
   rule". The clipped K = 10 value is the lane's trial's; no committed
   artefact holds it.
4. **The six Phase 2 ladders the D51 inventory now withholds** (§ 5 item
   7): their committed MCB sets and Phase 2 tile-MCC test rest on unclipped
   cells. Build clipped cells and re-run both, or keep them with a
   disclosure. Until then a tier-1 test pins the gap (`8df0522ff`), and the
   K-ladder findings give the tile-MCC counts on both bases.
5. **The Era-2 board's membership rule** (§ 1.3, § 5 item 9): re-deriving
   it today gives 98 members, not 110. Keep the frozen membership or
   re-derive.
6. **The fourth cell's board cell** (§ 2.2): it stays the registered
   (0.98, k10) on the board, 0.9141, while the board-frame argmax is now
   (0.95, k10), 0.9144; this pass applied D65 (3) to it as to the 3.7 image
   carried arm. Confirm.
7. **The null-exemplar sensitivity** (§ 11): its signature lapsed because
   it quotes the board's moved figures, and its reduced-frame readings
   (Tier 1 five → four; the 0.0074 and 0.0120 bounds) rest on the
   pre-pass cells. Re-run `scripts/analyse_null_exemplar_sensitivity.py`
   or keep it as a dated record.
8. **The per-student GS baseline**
   (`results/student-baseline-2026-09-01/per-student-gs4/findings.md`):
   its model rows equal the Era-2 board's cells (for example 0.9190 /
   0.9066 → 0.9289 / 0.9165), and its per-zone values and tests need
   re-scoring; its rankings hold. Re-score or keep as dated.
9. **The two Gemini screens have no restated narrative home**: their
   analyses and pair tests were regenerated (all-3.7 swap against the
   anchor p 0.0105 → 0.0065; K = 5 carried p 0.1697 → 0.0971; Arm V
   against carried p 0.0969 → 0.0764; every verdict holds), but their
   findings live only in closed planning cards and the lapsed register
   rows. Revision notes on the cards, or the register rows alone?
10. **Dated notes on the claims inventory** (§ 6): D55 Q1 allows them;
    none was added.
11. **R4-23**: the raw p crosses 0.05 (0.1783 → 0.0381); "not
    significant" now rests on the BH correction alone (0.0525).
12. **`--allow-undetermined-area`** (§ 5 item 8): should the Phase 2
    builder refuse when every ladder's area is undetermined, rather than
    exit 0 with all fourteen unclipped?
13. **The K-ladder findings' pre-existing inconsistency**, noticed and not
    edited: §§ 1, 4.3 and 7.2 say § 4.1 found no significant tile-MCC
    change, while § 4.1 found three significant falls.
14. **The 55-map seam** (D67 (6)): the extended-reference cells moved by
    about 8e-05, which changes the fourth decimal on six cells, so
    `TRACK2-SUMMARY.md` now disagrees with the 55-map leaderboard and five
    other documents that quote the unregenerated registered conditions.

15. **E72's Group 7** (§ 5 item 13): the held E72 regeneration would
    settle whether its flip survives (q 0.0483 against 0.050735).
16. **The GS plateau characterisation** (§ 5 item 14): regenerate it in a
    separate change with its own review of the dropped row, or leave it
    dated.

## 11. Not done

- **No register `outcome` text changed and nothing re-signed or merged**
  (the guarantees); the draft PR stays a draft.
- **Out of scope by the plan**: the null-exemplar analysis, A-06 and the
  D64 data; the E72 board regeneration, held for a ruling (§ 1.5); the
  claims inventory and `docs/paper/` drafts (D55 Q1).
- **Not re-run, for the PI** (§ 10): the null-exemplar sensitivity; the
  per-student GS baseline's per-zone values and tests; the Phase 2 tile-MCC
  test (`phase2/mcc-test/`) and the six withheld ladders' MCB sets on the
  clipped basis.
- **Not checked**: whether the two 55-map GS calibration legs read the
  same wrong-sheet crops the D62 (1) re-verification repaired (flagged by
  the document sweep; outside this pass's measured scope).
- **Planning documents** that quote moved values as current state (for
  example the continuity file's open item quoting 0.9265 as the 3.7 text
  headline) are the main session's to update; the sweep's list of dated
  records is in `restatement-pass-scripts/records/docs/doc-sweep.md`.

- **Not committed**: the regenerated GS plateau characterisation (§ 5
  item 14), kept on sapphire at `lead2/plateauA/`.

## Changelog

### 2026-10-30 — § 6 walked by the PI; one figure corrected (Session 166)

The PI walked § 6's claim rows one at a time with the independent
verification (`reports/s165-agent-records/restatement-claims-verify.md`) and
ruled each (D69). The approved wordings are the dated notes in the claims
inventory (`docs/paper/results-claims-inventory-2026-09-12.md`, `ce52570c6`),
which supersede § 6.1's proposals; the table is left as drafted. Nine
proposals changed in the walk, among them R3-11's range (about US$27 at the
top, not US$22), R7.3-22 and R7.3-24's −0.0044 / +0.0044, R3-14 and R6-17's
lead (48.7 %, the clipped reading) and cause attribution, and R4-04's
0.816. R6-18, listed in § 6.2 as holding, has a board-grain note that partly
fails (Obs 513). § 6.2's R4-12 figure is corrected here: 0.817 → 0.816
(0.816471, rounded twice before).

### 2026-10-20 — The plateau characterisation's "dropped" row corrected (Session 165)

§ 5 item 14 said the GS plateau characterisation drops
`g37-text-k1-verified-opmax` from its analysed set without an
explanation. Regenerated on the full checkout, it analyses the same 459
conditions; the cell only leaves the late-plateau table because its
restated curve plateaus earlier. § 5 item 14 gains a dated correction,
and the characterisation is regenerated in this PR on the PI's ruling
(D69, § 10 Q16). Commit: the one that applies this entry.

### 2026-10-18 — The membership drift corrected (Session 165)

§ 1.3 and § 5 item 9 said that re-deriving the Era-2 board's membership
today gives 98 members instead of 110 because the derivation reads later
register edits. A read-only re-derivation on the full checkout gives the
same 110; the 98 came from the board lane's partial copy, which lacked
12 members' detection files. Both passages gain a dated correction;
nothing else in the record changes. The PI accepted keeping the
membership, a record correction, and a to-do for the builder to refuse
rather than skip a frozen member whose file is missing (D69, § 10 Q5).
Commit: the one that applies this entry.

### 2026-10-15 (later) — Results half; the pass complete apart from § 11

The lead agent's second session on the pass (its predecessor stopped when
its context grew too long) wrote the results half: the Bottom line, § 1.8,
and §§ 2–11. It committed the Era-2 board lane (`8412f34bb`), the bridge
lane (`02339bd98`, `d6111dafb`), K-ladder step 5 (`0fc2d6389`, after four
discarded pairs of runs) and step 7 again (`62050794d`), the K-ladder
findings (`de998a94d`), the remaining documents (§ 9), two K-ladder test
updates (`f743421a4`, `8df0522ff`), five further signature lapses
(`92a66089d`), the merge of `origin/main` (`376eb1d50`), and the
manifests (`3b5279634`). Corrected in the plan: § 1.7's "in one batch
job" is one batch job per verifier (396 Gemini 3 rows and 90 Gemini 3.7
rows).

### 2026-10-15 — Original publication

First version, in progress: the plan's design decisions, the GS chain lane,
and the Era-2 board lane, committed before any regeneration.
