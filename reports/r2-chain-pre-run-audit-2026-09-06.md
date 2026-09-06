# Fresh-context audit of the r2 recompute block

> **Last revised**: 2026-09-06 (original publication).

Audit of `planning/reference-revision-2026-09-06.md` §§ 4/4a against the code.
No step of the block was run; zero API spend.

## Denominator

**Opened** (18 scripts; lines, P = in part): contract 490;
`build_55map_leaderboard.py` 316; `final_board_sweeps.py` 385; `final_board_build.py` 632 P;
`final_board_n3_carried.py` 117; `stride55_score.py` 274;
`register_standardised_gt_conditions.py` 267; `materialise_best_available_gt.py` 316;
`score_55maps_standardised_reference.py` 816 P; `lib_uplift_supplement.py` 1737 P;
`build_tiered_leaderboard.py` 2345 P; `evaluate_detections.py` 2488 (help);
`derive_audit_revision_instructions.py` 166 P; `empty_tile_adjudicate.py` 578 P;
`stride55_ladder.py`, both `gemini37_*_ladder.py`, `compute_corrected_f1_multi_buffer.py` P.
**Data** (8): `ladder.json`, `final_board_50m.json`, `cells_manifest.json`, IM-k4
`evaluation.json`, a stride55 `summary.json`, `audit-revision-instructions.csv`,
`condition-inventory.json`, the manifest schemas.
**Claims checked**: 21. **Probes**: 6 (a–f).

**NOT checked**: the § 2/§ 2b estimator arithmetic and intervals;
`tests/test_reference_revision_r2.py`; `marking_campaign_gates.py`;
`verify_run_conditions.py` and the manifest generators; whether the 3.7/3.8 GS
evaluations exist; `planning/55map-final-board-2026-08-27.md`; any scoring run.

## Findings

**BLOCKER 1 — step 3's cell count is wrong by seven; the 29/29 gate passes on a
mixed-vintage board.** The contract says "the 16 final-board cells" and
"16 + 3 + 3 + 6 + 1 = 29". `results/55map-final-board-2026-08-27/final_board_50m.json`
tiers **23** cells, `cells_manifest.json` lists 23, `cells/` holds 19 directories (the four
carried incumbents' detections sit outside it). The true total is 36. *Failure*: step 3
stops at 29, § 5's "step 4 never starts before 29/29" reads green, and step 4 tiers seven
cells still on r1 — the mixed-vintage board the count gate exists to prevent.

**BLOCKER 2 — step 4 depends on step 7; the declared order (4 → {5,6} → 7) is inverted.**
`build_55map_leaderboard.py:63` reads `results/run-conditions.json`; `:228–234` resolves
each cell by `label` and takes F1, CI, MCC and `n_detections` from its `eval_path`. The
`-r2-gt` labels are written by `register_standardised_gt_conditions.register_one`
(`run-conditions.json`, `:242`) — step 7. *Failure*: `StopIteration` on the label lookup,
or a board silently built from r1 eval paths if the clone is careless.

**BLOCKER 3 — the § 4a companion command cannot run, and would score the wrong set.**
`stride55_score.py` has no `--compute-mcc` (probe d; MCC is unconditional at `:197`).
`materialise_primary:105` gates the crop manifest's count, which is the **K=10** union
57,482, so `--union-n 43909` (ladder B N=5) aborts. `--min-votes 5` filters that K=10
union, whereas 0.843775 comes from `cluster_first_n(passes, 5)` with inherited
probabilities. No path in the script materialises a first-N rung.

**BLOCKER 4 — the r1 regression gates halt any r2 run, and G4's bound is tighter than the
contract's band.** `final_board_build.py:317–345` (G3) demands the eight legacy cells
reproduce the committed r1 board to **1e-9** on F1, every pairwise p-value and tier
membership, reading evals from hard-wired `STD_REF_DIR` (`:79`).
`final_board_sweeps.py:236–252` (G4) checks the same board at `MECHANISM_BOUND = 0.003`
(`:99`) — below the contract's own 0.005 drift band. With `standardised_gt()` on r2 both
fail by design, and "G4 red → stop" makes that unrecoverable.

**MAJOR 5 — H1 contradicts the IM-k4 template.** IM-k4's
`_metadata.cli_args.ground_truth` is `best-available-gt-55maps.geojson` — the merged file,
passed to `evaluate_detections.py --ground-truth`, which takes one path (probe a). That is
why the merged artefact exists. H1 forbids it and requires "the r2 layers (student,
extension, audit) via `build_extended_gt`" — but that function takes **two** frames
(`compute_corrected_f1_multi_buffer.py:386–389`) and `--vintage r2` emits **only** the
merged geojson/csv. No r2 layer files exist.

**MAJOR 6 — the r1 homes are not read-only by construction.** `final_board_sweeps.py:359`
writes `OUT/cells/<label>/detections.geojson` and `:376–378` rewrites `sweeps.json` and
`cells_manifest.json`; `final_board_n3_carried.py:98,111` writes the same tree;
`register_standardised_gt_conditions.adapt_one` overwrites each
`results/55maps-standardised-ref-2026-08-14/<cell>/evaluation.json` in place. All are
module constants with no override flag: an r2 run before H2 destroys what the regression
gate reads.

**MAJOR 7 — the 3.7 rungs cannot be materialised by the derivation the contract names.**
`final_board_sweeps.build_families` covers A/B plus TH7/T03/TM/IM/UPL only, and
`stride55_ladder.load_deduped_passes:122` hard-codes `range(1, 11)`. The real 3.7
derivations (`gemini37_arm_ladder.py`, K_TOTAL=5, arms 1/2; `gemini37_fourth_cell_ladder.py`,
`verify_37`) inherit the right probabilities but score against the **canonical** extended
GT and write **only** `ladder.json`. H5's "no rung registered from sweep numbers alone"
describes exactly what today's code produces.

**MAJOR 8 — H8's GS rank-change tripwire is false by construction, and the boards it names
do not exist.** `build_tiered_leaderboard.py:1512` applies BH across the whole pair family
and `:1040` a top-N=20 inclusion filter, so adding seven cells moves adjusted p-values and
tiers legitimately — a rank change is not evidence of a mechanism error. Also
`results/leaderboard/era2/` is empty and git-tracks zero files; no leaderboard spec YAML
exists in the repo; `planning/condition-inventory.json` (190 entries, 80 era-2) has zero
3.7/3.8 entries. The GS reference is unaffected (`DEFAULT_GROUND_TRUTH:114` is
`mounds-reference.geojson`), so these are new builds, not rebuilds.

**MAJOR 9 — r2 references resolve to "unresolved" silently.**
`lib_uplift_supplement.py:733` looks up by **basename**; `…-r2.geojson` is absent from
`REFERENCE_BY_FILENAME:130`, the fallbacks at `:742–749` know only
`-standardised-gt`/`-canonical-gt`, and `:757` returns
`ReferenceResolution(None, None, "unresolved")` without raising. `REFERENCE_N_MOUNDS:141`
is a separate literal H3's one-line fix would not populate.

**MINOR 10** — `score_55maps_standardised_reference.py:111–112` hard-gates 4731/279; r2 is
4,726 / 278 / 14. **MINOR 11** — `empty_tile_adjudicate.py:82` has no r2 entry, so step 7's
closure check has no reference. **MINOR 12** — both r2 scripts crash on an out-of-repo
`--out-dir` (`materialise_best_available_gt.py:284`,
`derive_audit_revision_instructions.py:161`), the first *before* writing the geojson.
**MINOR 13** — the engine gate's target was built at `4ac0eeedf`, `script_git_status:
"dirty"`. **MINOR 14** — pass order is committed only by `run_<i>` naming; the N=5 union
gate constrains the set, not the order. **MINOR 15** — `runs-manifest.schema.json:65`
enumerates `gt_reference` as `["curator","student","combined"]`.

## Clean probes

- **(a)** Every flag in IM-k4's `cli_args` exists today; the one new flag
  (`--require-clean-inputs`) defaults off, so replay is unaffected.
- **(b)** `--vintage r2` (run out-of-tree, per MINOR 12): all three outputs
  **byte-identical**; 5,018 = 4,726 + 278 + 14. § 3b's counts check out.
- **(c)** `derive_audit_revision_instructions.py`: both outputs **byte-identical**;
  6 removes, 14 adds.
- **(e)** `--spec`, `--inventory`, `--era`, `--track`, `--ground-truth`, `--top-n`,
  `--metric` all present.
- **(f)** `--reference r2` rejected (`invalid choice: 'r2'`) — H3 is a real gap.
- `summary.json` **does** carry a per-buffer tile confusion matrix and MCC with CIs
  (stride55 B, R=50: mcc, mcc_CI, tp/tn/fp/fn), so "companion deferred for want of a tile
  matrix" no longer holds. The ladder's B N=5 carried value is 0.8437752627324171 — the
  contract's 0.843775 is accurate.

## Changelog

### 2026-09-06 — Original publication

Fresh-context audit of the nine-step r2 recompute queue and hardenings H1–H9, run before
any step of the block. Four BLOCKER, five MAJOR and six MINOR claims with file:line
evidence; six probes, five clean.
