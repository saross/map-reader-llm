# D65 (2): the restatement pass (S164)

> **Last revised**: 2026-10-15 (original publication, in progress). See
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
re-verified on 2026-10-13, in one batch job. Both scripts gain a
`reverification` record beside it (date, record path, rows per leg), and the
findings say it where the dates are used (§§ 1, 7, 7a).

The trial changes readings, not only numbers, and they are reported as
surprises (§ 5): § 7's "none clears its upper bound" fails (the two
K-matched gap changes clear theirs, 1.09 and 1.01), the Gemini 3 T 1.0 text
advantage falls inside its upper bound (1.03 → 0.98), § 7a's three
sub-unit "each cell at its upper" readings become one, and the 3.7 image
carried original's § 6 "oracle" is its registered point, not its new best.

### 1.8 Register, manifests, and documents (this agent, last)

## Changelog

### 2026-10-15 — Original publication

First version, in progress: the plan's design decisions, the GS chain lane,
and the Era-2 board lane, committed before any regeneration.
