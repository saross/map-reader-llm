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

### 1.4 K-ladder lane (sub-agent; inventory pending)

### 1.5 Pairwise lane: PR #37's moved artefacts (sub-agent; inventory pending)

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

### 1.7 Modality bridge lane (sub-agent; inventory pending)

### 1.8 Register, manifests, and documents (this agent, last)

## Changelog

### 2026-10-15 — Original publication

First version, in progress: the plan's design decisions, the GS chain lane,
and the Era-2 board lane, committed before any regeneration.
