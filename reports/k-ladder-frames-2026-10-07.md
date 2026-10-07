# The K-ladder frames: why the two 487-tile sweeps are identical, 2026-10-07

> **Last revised**: 2026-10-07 (original publication, Session 162). See
> [§ Changelog](#changelog) for revision history.

**Status: FOR THE PI.** The record of a read-only investigation (PI
request, 2026-10-07) of a surprise the stale-register-notes pass found
(`reports/stale-register-notes-2026-10-07.md`). Written by the agent that
did the work; added here unchanged below this header. Scripts and raw
outputs: `k-ladder-frames-2026-10-07-scripts/`. Nothing it names has been
edited yet; the corrections and the K-ladder question in its items 8 to
10 await the PI.

Read-only, 2026-10-07; no API calls, no repository edits. Scripts and raw outputs beside
this file (`frames_geometry`, `strip_detections`, `outframe_37`, `universe_counterfactual`;
`.py` and `.out`).

## 1. The explanation

This is explanation (b) and (c) together, and the agreement is guaranteed by construction.

1. **The scorer never uses frame geometry to scope detections.** `calculate_f1_internal`
   (`scripts/lib_advanced_metrics.py:1595-1673`) takes the frame's maps from its
   `tile_name` values (l.1622). It then keeps every detection whose `source_tile`
   *starts with the map name* (l.1648). Only references are scoped geometrically
   (`scope_references_to_tiles`, l.1039-1065, per-tile `intersects`). The sweep
   (`scripts/sweep_f1_greedy_pv.py:97`) and the cell evaluator
   (`scripts/evaluate_detections.py:1115`) both call this function. Neither function
   changed between the producing commit and HEAD (diffed).
2. **The two frames have the same maps and the same references.**
   `era2_b_intersection_bounds.geojson` and `full_evaluation_bounds.geojson` hold the same
   487 `tile_name` values and four maps, and `scope_references_to_tiles` keeps the same
   435 reference indices in both. For ANY detection set, point F1, precision and recall
   are therefore identical under the two frames: the check has no power and could not
   have failed on any rung, past or future.
3. **The 13.4 km² difference is empty tile padding**, so even a geometry-clipping scorer
   would have found nothing there.
   - **Area:** I measured the union areas at 1,415.823 and 1,402.407 km² (EPSG:32635).
     The difference is 13.416 km² (0.95 %), and the board frame is a strict subset.
   - **Where:** 34 tiles are clipped (the sidecar `era2_b_intersection_bounds.provenance.json`
     agrees: `n_clipped` 34, `area_km2_era2_outside_b` 13.42). 33 lose the bottom 240 m
     (about 48 px) of the last row `y3696`: 13 on Rakovski, 10 on K-35-052-4, 10 on
     Elenovo, 0.463–0.464 km² each (the K-35-052-4 corner tile `x4032` loses 0.095). The
     34th is Lesovo `x1680_y3360` (0.117 km²).
   - **Beyond the raster:** the Era-2 tile `K-35-052-4_32635_x0_y3696` reaches 1,663 m
     below the raster's bottom edge (raster 3,748 px tall; the tile row ends at
     4,080 px). The board tile reaches 1,423 m below it. So 13.36 of the 13.42 km² lie
     outside the rasters; only 0.058 km² (on Lesovo) is inside one.
   - **Nothing in it:** 0 reference mounds; the nearest is 1,550.6 m away. 0 candidates
     from any of the 28 rungs, at any threshold (`strip_detections.out`).
4. **Explanation (a), a wiring bug, is ruled out.** At the producing commit `326181bcd`
   (2026-09-12, which added all 56 files), `BOARD_BOUNDS` goes to `sweep_2d_era2b.json`
   and `ERA2_BOUNDS` to `sweep_2d.json` (`score_k_ladder_phase2_rungs.py:88-90, 330-332`).
   - Direct recompute with the project's scorer under each bounds file, at the opmax
     point and at (1, 0.00): row 1 gives 0.8555 and 0.5419, row 27 gives 0.8495 and
     0.7777, under both frames. Every committed row is reproduced to four decimals.
   - The sweep JSONs are bare row lists and record no bounds metadata.

## 2. The same pattern elsewhere (step 5)

- **All 32 `sweep_2d_era2b.json` / `sweep_2d.json` pairs under `outputs/` are
  byte-identical:** 28 from Phase 2; 2 from g37-opmax (`verify/`, `verify_k10/`, via
  `scripts/derive_g37_gs_opmax_rungs.py:198-201`); 2 recovery-fixed
  (`verify_k{1,3}_recovery-fixed/`).
- **All 4 tier E `sweep_board.json` / `sweep_era2.json` pairs are byte-identical**
  (`scripts/run_k_ladder_tier_e.py:1043-1047`; `k1`, `k3`, `k5`, `k5_recovery-fixed`).
- **GS Era-2 board G6** (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/`
  `frame-deltas.md`): all 50 cells committed on `full_evaluation_bounds` show Δ +0.0000
  on the board frame, so G6 is uninformative by construction for Era-2 → board. Only the
  grid-common → board rows (Δ about −0.007) measure anything (428 mounds against 435).
- **Not this pattern:** optimism (grid-common vs board) and the card's 327-vs-487 test.

## 3. Claims that lean on frame agreement (step 4)

**A. True but vacuous.** These sites present agreement as an empirical result. The
conclusion stands, and is stronger than stated: the two frames are scoring-equivalent
for every point estimate. The wording ("never disagree", "found", "28 of 28", "still
agree") should become "agree by construction":

- `reports/k-ladder-phase2-deltas-2026-09-12.md:134-139` ("never disagree … not
  load-bearing"); `planning/k-ladder-review-2026-09-11.md:300` ("28 of 28");
  `reports/k-ladder-closeout-deltas-2026-09-12.md:149`;
  `reports/recovery-drop-fix-2026-09-13.md:181-182, 327`;
  `results/k-ladder-2026-09-12/findings.md:1582` ("still agree").
- The 31 opmax condition notes ("the two frames agree on the argmax for this rung") in
  `results/run-conditions.json` and `results/conditions-manifest.json`. They are
  generated by `scripts/register_k_ladder_phase2_conditions.py:171-180` and
  `scripts/register_k_ladder_tier_e_conditions.py:130-136`, and echoed in
  `outputs/h11/pv-diag-384/post_run_report.md`,
  `outputs/gemini37-screen-2026-08-28/post_run_report.md:140,142`, and
  `outputs/grid-2026-08-18/post_run_report.md:164-168`.
- JSON fields `frames_agree_on_argmax` / `frames_agree` / `opmax_on_era2_frame` in
  `phase2/{operating-points,scores,ladders}.json`, `phase2/g37-opmax/*.json`,
  `tier-e/*.json`, and `recovery-fix-2026-09-13/operating-points.json`.
- `docs/paper/results-draft.md`, `docs/paper/results-claims-inventory-2026-09-12.md`, and
  the K-ladder analysis rows of `results/run-analyses.json`: **no claim leans on frame
  agreement.**

**B. Mis-citations that need correcting.**

- `scripts/score_k_ladder_phase2_rungs.py:15-17` (docstring) and
  `reports/k-ladder-phase2-deltas-2026-09-12.md:138-139` cite "the board's note" that
  the frames' optima agree "for twenty of the twenty-one committed pv cells".
  The only such note (`planning/gs-era2-verified-board-2026-09-08.md:546`;
  `docs/notes/working-notes.md:33847`) compares the **327-tile Era-3 frame** with the
  487-tile frame and records **twenty of twenty-nine** free-sweep cells (nine differed):
  a different frame pair, and a real comparison. "Twenty of twenty-one" appears nowhere
  else in the repository.
- `results/k-ladder-2026-09-12/tier-e/pre_launch_audit.md:232-238` (Warning 3) cites
  § 6's measurement (l.169-175), which is of **grid-common against the board frame**
  (2.7 %, 37.9 km²), as the difference between "the two 487-tile frames" that tier E
  sweeps (board vs `full_evaluation_bounds`, really 0.95 %). Its reasoning ("a candidate
  can be inside one frame's union and outside the other's") does not hold for this scorer.
- `planning/gs-era2-verified-board-2026-09-08.md:115-121` (option (a)) expected change
  "only through false positives in that mound-free strip"; there are none, and the scorer
  would not drop them. Its conclusion holds exactly (G6 50/50 at +0.0000); annotation optional.

## 4. Adjacent finding (surprising): out-of-frame detections are scored inconsistently

The same mechanism (map-name scoping) means the board frame does **not** exclude
out-of-frame detections. Whether they count depends on how each cell was built:

| Ladder rung (GS, board frame, opmax) | Universe | Outside board frame | F1@20 committed | clipped to board | clipped to grid-common |
|---|---|---:|---:|---:|---:|
| 3.7 K = 1 (Phase 2, `merge_passes`) | native B | 27 (24 within 20 m of a reference mound outside the frame) | 0.8495 | 0.8747 | 0.8682 |
| 3.7 K = 3 (Phase 2) | native B | 28 (26 within 20 m) | 0.8860 | 0.9135 | 0.9073 |
| 3.7 K = 5 / K = 10 (committed) | grid-common filtered | 0 | 0.9066 / 0.9068 | same | same |
| tier E K = 1 / 3 / 5 (eval) | native, re-keyed | 23 / 23 / 21 (null `source_tile` → dropped) | 0.8546 / 0.8840 / 0.8905 | same | 0.8468 / 0.8762 / 0.8826 |

Point estimates, project scorer, committed operating points held fixed.

- **3.7 GS ladder** (`findings.md:602`, "0.8495 → 0.9068 (+0.0573)"): the K = 1 and
  K = 3 rungs book 27 and 28 out-of-frame detections as false positives, nearly all
  within 20 m of a reference mound the frame excludes. The committed K = 5 and K = 10
  unions (`union_k5.geojson`, `union_k10.geojson`) have 0 candidates outside grid-common, so
  they cannot reach the 7 board-frame mounds in the 37.94 km² band. With matched
  universes the gain becomes **+0.0386**, and K = 3 (0.9073) would sit level with or
  above K = 5 (0.9066) and K = 10 (0.9068), changing the ladder's shape (opmax points
  might also move under a matched sweep; untested).
- **Tier E:** `findings.md:1337` and `reports/k-ladder-closeout-deltas-2026-09-12.md:541-542`
  say "scoring every rung on the board frame excludes the out-of-frame candidates either
  way, so … like for like". That is only half true. The *evaluations* drop those
  candidates, through the null re-keyed `source_tile`, not through frame geometry. The
  *sweeps* that chose each argmax count them: sweep F1 0.8462 / 0.8746 / 0.8828 against
  evaluation F1 0.8546 / 0.8840 / 0.8905. The native rungs also reach the band mounds
  that the filtered K = 10 rung cannot (clip-to-grid-common costs them 0.008).
- **The 26 Gemini 3 `pv-diag-384` rungs are unaffected:** 0 out-of-frame detections.
Needs a PI ruling on the universe rule; matched-universe sweeps cost US$0. Until then the
3.7 GS ladder's +0.0573 and its monotone shape should not be treated as settled.

## 5. What to correct (no edits made)

1. Reword the § 3A claims to "agree by construction (identical tile names and in-scope
   references; the scorer scopes detections by map name)". Consider replacing the second
   sweep with an equivalence assertion (same tile names, same in-scope reference IDs).
2. Correct the "twenty of twenty-one" mis-citation at its two sites (§ 3B).
3. Correct tier E `pre_launch_audit.md` Warning 3: wrong frame pair, wrong percentage,
   and reasoning that does not apply to this scorer.
4. Put § 4 to the PI before anything cites the 3.7 GS K-gain or tier E's "like for like".
5. Optional: annotate G6 that the Era-2 → board deltas are zero by construction.

## Changelog

### 2026-10-07 — Original publication (Session 162)

The agent record, with this header added.
