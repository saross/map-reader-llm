# Frames blast radius: detections scoped like references, every committed cell re-scored, 2026-10-07

> **Last revised**: 2026-10-07 (the input-drift flag of § 3.1 withdrawn after its trace; Session 163). See [§ Changelog](#changelog) for revision history.

**Status: FOR THE PI.** Read-only measurement commissioned by the PI's ruling of
2026-10-07 on `reports/k-ladder-frames-2026-10-07.md` § 4: "measure the blast
radius first, then decide". No API calls, no library edits, no repository writes.
All computation ran on sapphire in `~/scratch/frames-blast-radius-2026-10-07/`
against the checkout at `f01ac3043`. (Another session advanced it to `c526b089f`
mid-run; the three intervening commits touch only the temperature-probe plan,
report, script and test, so no scorer and no committed evaluation differs.) Scripts
and raw outputs are beside this file in `frames-blast-radius-2026-10-07-scripts/`
(outputs under `out/`). The three per-cell row files (7.6 MB together) stay on
sapphire under `~/scratch/frames-blast-radius-2026-10-07/out/`
(`evaluations.jsonl`, `evaluations_rerun.jsonl`, `evaluations_nx.jsonl`), and
`out/summary/cells.csv` is their per-cell summary.

Abbreviations, first use: PI is the principal investigator; F1 is the
point-matched F1 score; P and R are precision and recall; MCC is the tile-level
Matthews correlation coefficient; GS is the four-sheet gold standard; PV is
proposer–verifier; K is the number of proposer passes; opmax is a sweep-optimal
operating point; CI is a confidence interval; OFF is the project's scorer unchanged;
ON is the same scorer with detections scoped geometrically exactly as references are
(§ 3).

## 1. Headline

| Count | Value | Source |
|---|---:|---|
| Committed `evaluation.json` files at `f01ac3043` | 2,800 | `out/summary/final.json` → `evaluations_committed` |
| Re-scored OFF and ON (F1, P, R per buffer; MCC where committed) | 2,727 | `final.json` → `cells_scored_off_and_on` |
| Further cells with out-of-frame diagnostics only (corrected-F1 engine) | 24, all with 0 out-of-frame detections | `final.json` → `status`; § 4.3 |
| Not scoreable (13 missing gitignored inputs, 36 with no input metadata) | 49 | `final.json` → `status` |
| Cells with any out-of-frame detection | **70** of 2,751 | `final.json` → `cells_with_any_out_of_frame` |
| … of which registered conditions (`results/conditions-manifest.json`) | **3** of 634 scored | `final.json` → `registered_cells_with_out_of_frame` |
| Cells moving ≥ 0.001 in any metric at any buffer | **55** | `final.json` → `moved` |
| … moving ≥ 0.005 | **23** | same |
| … moving ≥ 0.01 | **22** | same |
| Committed (vote, probability) sweeps re-run OFF and ON | 12 | `out/sweeps.json`, `out/stride55_sweep.json` |
| … whose argmax moves | **0** | same |

1. **The defect is real but narrow.** Only 70 cells carry a detection the name-prefix
   scope books and the reference rule would drop. In every one of the 55 that moves,
   **recall is unchanged and only precision rises** (ΔR@20 = 0.0000 in all 55 rows of
   § 4): the out-of-frame detections are pure false positives.
2. **Three registered cells move, all on one ladder**: the Gemini 3.7 GS K-ladder's
   K = 1 and K = 3 rungs (0.8495 → 0.8747, 0.8860 → 0.9135, carried K = 1 0.8338 →
   0.8616 at 20 m). With them corrected the ladder is **no longer monotone**: K = 3
   (0.9135) beats K = 10 (0.9068), and the K = 1 → K = 10 gain falls from +0.0573 to
   **+0.0320** (§ 5.1).
3. **One signed headline rests on the defect.** The null-exemplar analysis's "largest
   movement of any Era-2 cell is 0.0074" is the 3.7 K = 1 rung's artefact; scoped, that
   cell moves −0.0007 and the largest movement becomes **0.0068** (§ 5.2).
4. **Everything else that moves is unregistered**: 41 waived cells (the five 512 px
   cells scored on the 384 px frame move **+0.060 to +0.069**; the K = 1 gap-fill
   anchors move +0.001 to +0.021) and eight supplement inputs (+0.0024 to +0.0033 on
   the uplift pairing twins; the 3.7 rungs' three null-exemplar twins).
5. **Surprising, and adjacent rather than in scope: sheet re-keying.** Assigning a
   detection's tile geometrically across *all* sheets (tier E's
   `reassign_carrier_tiles`, h13's `assign_primary_tiles`) moves 6 or 7 detections per
   tier E cell onto a neighbouring sheet, where they cannot match their own sheet's
   reference. That **depresses tier E's K = 1, 3 and 5 cells by 0.013 to 0.014 F1**
   and the six h13 cells by 0.005 to 0.016 (§ 5.4). It is a separate defect, and it
   bears on how any fix must be written.

## 2. Scorer entry points

The inventory below was built by a read-only subagent sweep of `scripts/` and checked
here at the anchors cited (re-read at `f01ac3043`). Verdicts: **S** shares the
asymmetry (references geometric, detections by sheet name); **N** is symmetric; **P**
is partial.

### 2.1 The primitives

| Primitive | References | Detections | Verdict |
|---|---|---|---|
| `calculate_f1_internal` (`scripts/lib_advanced_metrics.py:1595`) | per sheet, `Map`/`source_map` equal, then `scope_references_to_tiles` (`:1646`; `sjoin … predicate='intersects'` at `:1061`) | `source_tile.str.startswith(map)` (`:1648`), no geometry | **S** |
| `compute_per_tile_tp_fp_fn` (`:1126`) — feeds `bootstrap_ci` and every tile-swap permutation test | same per-sheet rule | same name prefix for matching (`:1290`); TP/FP then booked only where `source_tile` is a frame tile name (`:1237`) | **S**, plus a second inconsistency: an out-of-frame detection still takes part in matching but is booked to no tile |
| `bootstrap_ci` | interval from the per-tile table (`:1750`), point from `calculate_f1_internal` (`:1800`) | as above | **S**; interval and point can use different detection scopes |
| `calculate_tile_classification` (`:2986`), default `id` join (`:132`) | geometric, every containing tile | exact `source_tile` equal to a frame tile name (`:2669`) | name-based; an out-of-frame detection is booked only if its name collides with a frame tile |
| `compute_counts_at_r`, the corrected-F1 engine (`scripts/compute_corrected_f1_multi_buffer.py:505`) | per sheet, then `scope_references_to_tiles` | `str.startswith` (`:540`) | **S** (a copy of the library rule) |

Other copies of the name-prefix detection scope: `scripts/analyse_dawid_skene.py:302`,
`scripts/review_candidates.py:488`, `scripts/discover_hard_cases.py:192`,
`scripts/h13_overlap_analysis.py:336` (and a count at
`scripts/analyse_55maps_heterogeneity.py:228`).

### 2.2 Entry points

| Entry point | How detections reach the scorer | Verdict |
|---|---|---|
| `scripts/evaluate_detections.py` (`calculate_f1_internal` at `:1115`) | file `source_tile` if present; if the column is absent, `_evaluate_condition` assigns it by a left `intersects` join to the frame (`:2617-2628`), so out-of-frame detections get a null and drop out | **P**: S for inputs carrying `source_tile` (per-pass, PV and materialised sets), N for consensus files without it |
| `scripts/sweep_f1_greedy_pv.py` (`:96`), `scripts/sweep_f1_wbf.py` | crop-manifest `source_tile` (the proposer's tile) | **S** — every K-ladder and tier E sweep goes through it |
| Corrected-F1 path: `compute_corrected_f1_multi_buffer.py`, `score_55maps_extended_gt_canonical.py`, `stride55_sweep_oracle.py`, the gemini37 55-map ladders | `compute_counts_at_r`; stride and 3.7 55-map sets re-keyed by `assign_standard_tile` (nearest standard tile **within the origin sheet**, never null; `scripts/stride55_score.py:81-87`) | **S** |
| Tile-swap permutation tests (`pairwise_permutation_test.py:410-419`, `lib_permutation.py:223-228`, and the board scripts `era1_leaderboard_tiering.py`, `n1_baseline_leaderboard_tiering.py`, `final_board_build.py`, `build_55map_leaderboard.py`, `k_ladder_tension_analyses.py`) | observed statistic from the per-tile table, ranking by the evaluation's F1 (e.g. `era1_leaderboard_tiering.py:1203`); `final_board_build.py:117` and `build_55map_leaderboard.py:104` gate the gap at 0.003 | **S** |
| K-ladder: `score_k_ladder_phase2_rungs.py`, `derive_g37_gs_opmax_rungs.py` | sweep by manifest name; cells materialised with `source_tiles[0]` (proposer vocabulary) | **S** — realised on the three 3.7 rungs |
| Tier E: `run_k_ladder_tier_e.py` | sweep by manifest name (S); cells re-keyed by `assign_primary_tiles` across all frame tiles (`:989`), out-of-frame set null | **P** — selected under one scope, scored under the other; and re-keying crosses sheets (§ 5.4) |
| Grid, stride and image-B analyses (`grid_analysis.as_gdf`, `:169-184`), h13 (`prepare_h13_scoring.py:375-377` clips) | geometric carrier assignment; off-carrier rows dropped | **N** for frame scope; exposed to sheet re-keying |
| `score_leaderboard_cells.py`, `evaluate_pilot.py` | pre-filtered to frame tile names (`score_leaderboard_cells.py:93-94`) | **P** (names, not geometry) |

The subagent's full grouping of the remaining ~90 scorer-calling scripts (all
library callers inherit the primitive's verdict) is not reproduced here; none
introduces a third scoping rule.

## 3. Validation gates

**The wrapper.** `blast_lib.geometric_detection_scope` keeps a detection whose
`source_tile` begins with frame sheet M only if it intersects one of M's tile
polygons, by calling the library's own `scope_references_to_tiles` on the
detections, so tiles, predicate and coordinate reference system (CRS) handling are
the reference side's by construction. Detections the library ignores anyway (null
or foreign names) are left untouched. ON passes the scoped frame to the unmodified
`calculate_f1_internal` and `calculate_tile_classification`. When a cell drops
nothing, ON receives the same rows as OFF and is identical by construction. For
sweeps, `blast_lib.patched_scorers` monkeypatches the three library functions in
every loaded module and restores them on exit.

### 3.1 Gate (i): the wrapper OFF reproduces the committed values

Every scored cell was compared at its 20 m and 50 m buffers (all 14 buffers where
anything drops), tolerance 1e-4 against the four-decimal committed values
(`out/summary/final.json` → `gate_i_totals`, `gate_i_by_family`; causes from
`classify_reproduction.py`, `out/summary/reproduction_failures.csv`).

| Family (frame) | Scored | F1, P, R and MCC reproduced | F1, P, R reproduced; committed MCC now refused | Not reproduced, input drift | Not reproduced, unexplained |
|---|---:|---:|---:|---:|---:|
| GS-487 Era-2 (`full_evaluation_bounds`) | 1,076 | 1,034 | 0 | 42 | 0 |
| GS-487 board (`era2_b_intersection_bounds`) | 213 | 211 | 2 | 0 | 0 |
| GS-487 grid-common | 63 | 55 | 8 | 0 | 0 |
| GS-327 Era-3 (`h10_test_bounds`) | 40 | 40 | 0 | 0 | 0 |
| GS-340 Era-1 (512 px) | 739 | 739 | 0 | 0 | 0 |
| GS-1032 (256 px) | 16 | 16 | 0 | 0 | 0 |
| GS h13 (four frames) | 6 | 6 | 0 | 0 | 0 |
| 55-map | 285 | 226 | 50 | 0 | 9 |
| Null-exemplar reduced frames (Era-2, Era-1) | 235 | 235 | 0 | 0 | 0 |
| **All live** | **2,673** | **2,562** | **60** | **42** | **9** |
| Archive (`archive/**`) | 54 | 37 | 2 | 12 | 3 |

- **F1, P and R reproduce on 2,622 of 2,673 live cells**, every family represented.
- **The named rows reproduce exactly**: 3.7 GS K = 1 F1@20 0.8495, K = 3 0.8860, carried
  K = 1 0.8338, K = 5 0.9066 / MCC 0.7651, K = 10 0.9068 / MCC 0.7675
  (`final.json` → `gate_i_named_cells`).
- **"MCC now refused" (60)** are artefacts written before the tile-join invariant
  (2026-09-13) that print an MCC today's library refuses; K = 1's committed 0.1337 and
  the carried rung's 0.1422 are two of them. Their F1, P and R reproduce.
- **Input drift (42)**: the detection files on sapphire no longer match the committed
  feature counts. Nine are registered conditions (`n1-outstanding-384` Pro HIGH T 0
  cells, and `e47-propose-brief::single-pass-run_4`). None has an out-of-frame
  detection in its current input. **Traced, and the flag withdrawn**
  (`reports/input-drift-2026-10-07.md`): every drifted cell, live and archived, was
  rewritten by a recorded recovery campaign after the version it scored (mostly the
  E71 dead-tile rerun of 2026-07-30 and the consensus rebuilds after it). 29 of the
  42 live cells are pinned to their scored inputs by `_metadata.e82_input_vintage`,
  which this report's classifier did not read. Rebuilt at the scored inputs, 53 of the
  54 drifted cells reproduce F1, P, R and MCC to 1e-4; the 54th reproduces F1, P and R
  (its old MCC is refused under the tile-join rule). The nine registered cells are kept
  as historical records under ruling 3a, each with a `-post-e71` twin. They drifted
  under E71, not E57: E57 concerns which model they ran on.
- **Unexplained (9)**: older 55-map evaluations under `outputs/55maps-*-generalisation/`,
  off by at most 0.0004 in F1, P, R or MCC, with 0 out-of-frame detections.
- **Sweeps reproduce row for row**: 80/80, 240/240 or 400/400 rows on all ten GS sweeps,
  and 10/10 gate rows on each 55-map stride sweep (`out/sweeps.json` →
  `n_rows_reproduced`; `out/stride55_sweep.json` → `gate_reproduced`).

### 3.2 Gate (ii): the wrapper ON reproduces the frames report's clipped numbers

`out/gates.json` → `gate_ii` (`gates.py`), against
`reports/k-ladder-frames-2026-10-07.md` § 4 and its `universe_counterfactual.out`:

| 3.7 GS rung | OFF | ON, board (expected 0.8747 / 0.9135) | Clipped to grid-common, scored on board (expected 0.8682 / 0.9073) | ON by monkeypatch | Verdict |
|---|---:|---:|---:|---:|---|
| K = 1 (row 27) | 0.8495 | 0.8747 | 0.8682 | 0.8747 | PASS |
| K = 3 (row 28) | 0.8860 | 0.9135 | 0.9073 | 0.9135 | PASS |

The per-sheet rule and the frames report's union clip agree here because none of
these out-of-frame detections lies inside another sheet's tiles
(`n_out_cross_map` 0). They diverge on the 55-map cells (§ 4.2).

### 3.3 Gate (iii): red sentinel

With the wrapper deliberately broken (every prefix-matched detection scoped to an
empty tile set), F1@20 fell to 0.0000 on both rungs and on a control cell with no
out-of-frame detection (`pv-min-text-t1.0-n3-opmax`, ON 0.8647), by both the direct
and the monkeypatch path. After the context manager exited, the library returned
0.8495 again (`out/gates.json` → `gate_iii`, `restored_after_patch`). **PASS**: the
wrapper is in the scoring path.

## 4. What moves

### 4.1 Every moved cell

All 55 cells with |ON − OFF| ≥ 0.001 in any of F1, P, R or MCC at any scored buffer,
generated from `out/summary/moved_grouped.csv` by `render_moved_table.py` (no
number below is transcribed by hand). *Cell* is the directory holding the cell's
`evaluation.json`. *Register*: `registered` (a condition's source file), `waived`
(listed in a run's `_ignored_evals` in `results/run-conditions.json`), `archive`,
or `other`. Δ is ON − OFF. 55-map cells headline at 50 m.

| # | Group | Cell (evaluation directory) | Register | Detections | Out of frame | F1@20 OFF → ON | ΔP@20 | ΔR@20 | ΔF1@50 | MCC OFF / ON |
|---:|---|---|---|---:|---:|---|---:|---:|---:|---|
| 1 | 3.7 GS K-ladder rungs | `gemini37-screen-2026-08-28__g37-text-k1-verified-carried-p0_10-k1` | registered | 558 | 32 | 0.8338 → 0.8616 | +0.0451 | +0.0000 | +0.0284 | refused / refused |
| 2 | 3.7 GS K-ladder rungs | `gemini37-screen-2026-08-28__g37-text-k1-verified-opmax` | registered | 502 | 27 | 0.8495 → 0.8747 | +0.0451 | +0.0000 | +0.0258 | refused / refused |
| 3 | 3.7 GS K-ladder rungs | `gemini37-screen-2026-08-28__g37-text-k3-verified-opmax` | registered | 495 | 28 | 0.8860 → 0.9135 | +0.0499 | +0.0000 | +0.0280 | refused / refused |
| 4 | null-exemplar reduced-frame re-scores | `gemini37-screen-2026-08-28__g37-text-k1-verified-carried-p0.10-k1` | other | 558 | 40 | 0.8267 → 0.8617 | +0.0565 | +0.0000 | +0.0357 | refused / refused |
| 5 | null-exemplar reduced-frame re-scores | `gemini37-screen-2026-08-28__g37-text-k1-verified-opmax` | other | 502 | 34 | 0.8421 → 0.8740 | +0.0567 | +0.0000 | +0.0327 | refused / refused |
| 6 | null-exemplar reduced-frame re-scores | `gemini37-screen-2026-08-28__g37-text-k3-verified-opmax` | other | 495 | 35 | 0.8788 → 0.9134 | +0.0624 | +0.0000 | +0.0352 | refused / refused |
| 7 | 512 px cells scored on the 384 px Era-2 frame | `512px-image-t0` | waived | 777 | 137 | 0.5132 → 0.5786 | +0.0857 | +0.0000 | — | — |
| 8 | 512 px cells scored on the 384 px Era-2 frame | `512px-image-t07` | waived | 783 | 138 | 0.4713 → 0.5315 | +0.0784 | +0.0000 | — | — |
| 9 | 512 px cells scored on the 384 px Era-2 frame | `512px-text-t0` | waived | 884 | 150 | 0.5368 → 0.6056 | +0.0818 | +0.0000 | — | — |
| 10 | 512 px cells scored on the 384 px Era-2 frame | `512px-text-t07` | waived | 924 | 154 | 0.5254 → 0.5925 | +0.0773 | +0.0000 | — | — |
| 11 | 512 px cells scored on the 384 px Era-2 frame | `eval-512-on-384-image-t0` | waived | 777 + 770 + 770 | 409 | 0.5141 → 0.5795 | +0.0861 | +0.0000 | — | — |
| 12 | GS grid-common K = 1 gap-fill | `image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8` | waived | 2792 | 163 | 0.2472 → 0.2604 | +0.0088 | +0.0000 | +0.0139 | refused / refused |
| 13 | GS grid-common K = 1 gap-fill | `image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9` | waived | 2428 | 112 | 0.2738 → 0.2850 | +0.0078 | +0.0000 | +0.0119 | refused / refused |
| 14 | GS grid-common K = 1 gap-fill | `stride-phaseb-2026-08-25__g256-ov064-k10-verified-p0_15-k8` | waived | 2594 | 117 | 0.2654 → 0.2761 | +0.0073 | +0.0000 | — | refused / refused |
| 15 | GS grid-common K = 1 gap-fill | `stride-phaseb-2026-08-25__g384-ov128-k10-verified-p0_15-k8` | waived | 1893 | 99 | 0.3395 → 0.3546 | +0.0115 | +0.0000 | — | refused / refused |
| 16 | GS grid-common K = 1 gap-fill | `stride-phaseb-2026-08-25__g384-ov128-ladder-n3-verified-p0_15-k3` | waived | 1893 | 99 | 0.3395 → 0.3546 | +0.0115 | +0.0000 | — | refused / refused |
| 17 | GS grid-common K = 1 gap-fill | `stride-phaseb-2026-08-25__g384-ov128-ladder-n5-verified-p0_15-k4` | waived | 1893 | 99 | 0.3395 → 0.3546 | +0.0115 | +0.0000 | — | refused / refused |
| 18 | GS grid-common K = 1 gap-fill | `stride-phaseb-2026-08-25__g512-ov176-k10-verified-p0_15-k6` | waived | 1406 | 88 | 0.4122 → 0.4330 | +0.0180 | +0.0000 | — | 0.0843 / refused |
| 19 | GS grid-common K = 1 gap-fill | `stride-phaseb-2026-08-25__g512-ov320-k10-verified-p0_15-k10` | waived | 3926 | 305 | 0.1874 → 0.2015 | +0.0088 | +0.0000 | — | refused / refused |
| 20 | GS grid-common K = 1 gap-fill | `stride-phasec-2026-08-25__g384-ov240-k10-verified-p0_15-k10` | waived | 5698 | 337 | 0.1355 → 0.1434 | +0.0046 | +0.0000 | — | refused / refused |
| 21 | 55-map stride pairing twins | `stride-55map-2026-08-25__g384-ov128-55map-n1-oracle-p0_20-k1-r2-gt` | other | 18162 | 145 | 0.3083 → 0.3102 | +0.0016 | +0.0000 | +0.0024 | 0.1216 / 0.1214 |
| 22 | 55-map stride pairing twins | `stride-55map-2026-08-25__g384-ov128-55map-n1-oracle-p0_20-k1-standardised-gt` | other | 18162 | 145 | 0.3081 → 0.3101 | +0.0016 | +0.0000 | +0.0024 | 0.1218 / 0.1216 |
| 23 | 55-map stride pairing twins | `stride-55map-2026-08-25__g384-ov192-55map-n1-oracle-p0_20-k1-r2-gt` | other | 24923 | 317 | 0.2582 → 0.2610 | +0.0020 | +0.0000 | +0.0033 | 0.0895 / 0.0898 |
| 24 | 55-map stride pairing twins | `stride-55map-2026-08-25__g384-ov192-55map-n1-oracle-p0_20-k1-standardised-gt` | other | 24923 | 317 | 0.2580 → 0.2608 | +0.0020 | +0.0000 | +0.0033 | 0.0891 / 0.0894 |
| 25 | 55-map stride pairing twins | `stride-55map-2026-08-25__g384-ov192-55map-n1-verified37-oracle-p0_96-k1-r2-gt` | other | 24923 | 317 | 0.2582 → 0.2610 | +0.0020 | +0.0000 | +0.0033 | 0.0895 / 0.0898 |
| 26 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n10-carried-p0_15-k8-r2-gt` | waived | 23743 | 138 | 0.2581 → 0.2594 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 27 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n10-carried-p0_15-k8-standardised-gt` | waived | 23743 | 138 | 0.2579 → 0.2592 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 28 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n10-oracle-p0_15-k7-r2-gt` | waived | 23743 | 138 | 0.2581 → 0.2594 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 29 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n10-oracle-p0_15-k7-standardised-gt` | waived | 23743 | 138 | 0.2579 → 0.2592 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 30 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n3-carried-posthoc-p0_15-k3-r2-gt` | waived | 23743 | 138 | 0.2581 → 0.2594 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 31 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n3-carried-posthoc-p0_15-k3-standardised-gt` | waived | 23743 | 138 | 0.2579 → 0.2592 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 32 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n3-oracle-p0_20-k2-r2-gt` | waived | 23743 | 138 | 0.2581 → 0.2594 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 33 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n3-oracle-p0_20-k2-standardised-gt` | waived | 23743 | 138 | 0.2579 → 0.2592 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 34 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n5-carried-p0_15-k4-r2-gt` | waived | 23743 | 138 | 0.2581 → 0.2594 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 35 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n5-carried-p0_15-k4-standardised-gt` | waived | 23743 | 138 | 0.2579 → 0.2592 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 36 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n5-oracle-p0_15-k4-r2-gt` | waived | 23743 | 138 | 0.2581 → 0.2594 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 37 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov128-55map-n5-oracle-p0_15-k4-standardised-gt` | waived | 23743 | 138 | 0.2579 → 0.2592 | +0.0009 | +0.0000 | +0.0015 | refused / refused |
| 38 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n10-carried-p0_15-k10-r2-gt` | waived | 40746 | 252 | 0.1797 → 0.1807 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 39 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n10-carried-p0_15-k10-standardised-gt` | waived | 40746 | 252 | 0.1796 → 0.1806 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 40 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n10-oracle-p0_20-k9-r2-gt` | waived | 40746 | 252 | 0.1797 → 0.1807 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 41 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n10-oracle-p0_20-k9-standardised-gt` | waived | 40746 | 252 | 0.1796 → 0.1806 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 42 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n10-verified37-carried-p0_98-k10-r2-gt` | waived | 40746 | 252 | 0.1797 → 0.1807 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 43 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n10-verified37-oracle-p0_96-k9-r2-gt` | waived | 40746 | 252 | 0.1797 → 0.1807 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 44 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n3-carried-posthoc-p0_15-k3-r2-gt` | waived | 40746 | 252 | 0.1797 → 0.1807 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 45 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n3-carried-posthoc-p0_15-k3-standardised-gt` | waived | 40746 | 252 | 0.1796 → 0.1806 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 46 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n3-oracle-p0_20-k3-r2-gt` | waived | 40746 | 252 | 0.1797 → 0.1807 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 47 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n3-oracle-p0_20-k3-standardised-gt` | waived | 40746 | 252 | 0.1796 → 0.1806 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 48 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n3-verified37-oracle-p0_96-k3-r2-gt` | waived | 40746 | 252 | 0.1797 → 0.1807 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 49 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n5-carried-p0_15-k5-r2-gt` | waived | 40746 | 252 | 0.1797 → 0.1807 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 50 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n5-carried-p0_15-k5-standardised-gt` | waived | 40746 | 252 | 0.1796 → 0.1806 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 51 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n5-oracle-p0_20-k5-r2-gt` | waived | 40746 | 252 | 0.1797 → 0.1807 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 52 | 55-map stride K = 1 gap-fill | `stride-55map-2026-08-25__g384-ov192-55map-n5-oracle-p0_20-k5-standardised-gt` | waived | 40746 | 252 | 0.1796 → 0.1806 | +0.0006 | +0.0000 | +0.0011 | refused / refused |
| 53 | archived copies | `gemini37-screen-2026-08-28__g37-text-k1-verified-carried-p0_10-k1` | archive | 558 | 32 | 0.8338 → 0.8616 | +0.0451 | +0.0000 | +0.0284 | refused / refused |
| 54 | archived copies | `gemini37-screen-2026-08-28__g37-text-k1-verified-opmax` | archive | 502 | 27 | 0.8495 → 0.8747 | +0.0451 | +0.0000 | +0.0258 | refused / refused |
| 55 | archived copies | `gemini37-screen-2026-08-28__g37-text-k3-verified-opmax` | archive | 495 | 28 | 0.8860 → 0.9135 | +0.0499 | +0.0000 | +0.0280 | refused / refused |

### 4.2 By group

| Group | Moved | Register | Largest Δ (any metric) | Out-of-frame detections per cell | Where they lie |
|---|---:|---|---:|---|---|
| 3.7 GS K-ladder rungs | 3 | registered | 0.0509 | 27–32 | outside the board frame's union |
| Their null-exemplar reduced-frame twins | 3 | supplement input | 0.0636 | 34–40 | outside the reduced frame |
| 512 px cells on the 384 px Era-2 frame | 5 | waived | 0.0962 | 137–409 | outside the frame |
| GS grid-common K = 1 gap-fill | 9 | waived | 0.0208 | 88–337 | outside the frame |
| 55-map stride pairing twins | 5 | supplement input | 0.0033 | 145–317 | inside a **neighbouring** sheet's tiles |
| 55-map stride K = 1 gap-fill | 27 | waived | 0.0015 | 138–252 | inside a neighbouring sheet's tiles |
| Archived copies of the 3.7 rungs | 3 | archive | 0.0509 | 27–32 | outside the frame |

Source: `final.json` → `moved_groups`. The "where" column is from each row's
`diag_runs` (`n_out_cross_map`): all 87 + 109 + 988 + 1,419 out-of-frame GS detections
lie outside the frame union; all 6,740 of the 55-map ones lie inside another sheet's
tiles. **A union-geometry clip would therefore leave the 55-map rows unchanged**;
the per-sheet rule (identical to references) moves them.

Fifteen further cells (55-map pairing twins) carry 1 to 13 out-of-frame detections
and move by less than 0.001. Twelve cells carry null `source_tile` values (tier E's
re-keyed cells, their copies, and two archived artefacts); **none of those nulls lies
inside the frame** (`final.json` → `cells_with_null_in_frame` 0), so the null drop is
benign throughout.

### 4.3 Families that cannot move

- **The corrected-F1 (55-map extended-reference) cells**: all 24 adapter evaluations
  have 0 out-of-frame detections, so they are identical under the fix
  (`out/summary/cells.csv`, status `diagnostics-only`).
- **The Era-2 board's 150 tiered cells, every Era-1, Era-3, 256 px and h13 cell**:
  0 out-of-frame.
- **Candidate universes**: of 283 crop manifests (`out/universes.jsonl`), those with
  candidates outside the frame of a committed name-scoped sweep are the 3.7 K = 1 and
  K = 3 crops, tier E's K = 1, 3 and 5 crops, and the two 55-map stride universes
  (1,018 and 2,192, 97 % and 95 % of them single-vote); all were re-run (§ 4.4). A few
  `pv-diag-384` pools hold 1 to 6 candidates in the board frame's clipped strip, but
  their committed opmax sweeps ran on the Era-2 frame, where they have none
  (`scripts/build_gs_era2_board_opmax.py:133`).

### 4.4 Sweeps: the argmax never moves

| Sweep (frame) | Universe | Out of frame | Rows reproduced | Argmax OFF | Argmax ON | Rows moving ≥ 0.001 |
|---|---:|---:|---|---|---|---:|
| 3.7 K = 1 (board) | 640 | 38 | 80/80 | (1, 0.15) 0.8495 | (1, 0.15) 0.8747 | 80 |
| 3.7 K = 1 (Era-2) | 640 | 38 | 80/80 | (1, 0.15) 0.8495 | (1, 0.15) 0.8747 | 80 |
| 3.7 K = 3 (board) | 757 | 45 | 240/240 | (3, 0.10) 0.8870 | (3, 0.10) 0.9135 | 240 |
| 3.7 K = 1, recovery-fixed (board) | 640 | 38 | 80/80 | (1, 0.15) 0.8495 | (1, 0.15) 0.8747 | 80 |
| 3.7 K = 3, recovery-fixed (board) | 759 | 45 | 240/240 | (3, 0.10) 0.8860 | (3, 0.10) 0.9135 | 240 |
| 3.7 K = 5, control (board) | 791 | 0 | 400/400 | (5, 0.10) 0.9066 | (5, 0.10) 0.9066 | 0 |
| Tier E K = 1 (board) | 1,826 | 96 | 80/80 | (1, 0.20) 0.8462 | (1, 0.20) 0.8680 | 80 |
| Tier E K = 3 (board) | 2,481 | 125 | 240/240 | (3, 0.15) 0.8746 | (3, 0.15) 0.8979 | 240 |
| Tier E K = 5 (board) | 2,932 | 148 | 400/400 | (5, 0.15) 0.8828 | (5, 0.15) 0.9046 | 400 |
| Tier E K = 5, recovery-fixed (board) | 2,932 | 148 | 400/400 | (5, 0.15) 0.8828 | (5, 0.15) 0.9046 | 400 |
| 55-map stride A `g384_ov128` (50 m) | 38,713 | 1,018 | 10/10 gate | (k7, 0.15) 0.8362 | (k7, 0.15) 0.8362 | 2 of 200 |
| 55-map stride B `g384_ov192` (50 m) | 57,482 | 2,192 | 10/10 gate | (k9, 0.20) 0.8503 | (k9, 0.20) 0.8503 | 3 of 200 |

Sources: `out/sweeps.json` (`rerun_sweeps.py`, sweep buffers 20, 30, 40 and 50 m as
committed; argmax at 20 m with the K-ladder tie-break), `out/stride55_sweep.json`
(`rerun_stride55_sweep.py`). Argmaxes are (vote, probability) for GS and (min votes,
probability) for 55-map. The tier E rows also show **why tier E's sweep and its
evaluations disagree**: the sweep books the out-of-frame candidates (0.8462) and the
evaluation drops them through the re-key, but the evaluation (0.8546) is *still* below
the scoped sweep (0.8680) on the same 459 points. The remaining gap is sheet re-keying
(§ 5.4).

## 5. Downstream claims and boards

### 5.1 The 3.7 GS K-ladder (registered conditions; `k-ladder-2026-09-12`, signed)

| Rung | Committed F1@20 (`phase2/ladders.json`) | ON | Out of frame |
|---|---:|---:|---:|
| K = 1 | 0.8495 | 0.8747 | 27 |
| K = 3 | 0.8870 (the evaluation reads 0.8860) | 0.9135 | 28 |
| K = 5 | 0.9066 | 0.9066 | 0 |
| K = 10 | 0.9068 | 0.9068 | 0 |

`out/downstream.json` → `ladder_37_gs`. **Surprising (flag):** `ladders.json` carries
K = 3 at 0.887 with 494 detections, while the evaluation it points to reads 0.8860 on
495 (the recovery-fix re-materialisation); the ladder file was not refreshed.

- **The gain.** K = 1 → K = 10 falls from **+0.0573 to +0.0320**. The best rung becomes
  K = 3 (+0.0388 over K = 1). On the frames report's matched-universe clip it is +0.0386.
- **The shape stops being monotone.** K = 3 sits above K = 5 and K = 10, so for this
  family K = 5 and K = 10 leave the efficient set (lower F1 at higher cost).
- **Statements that change** (citing sites):
  - `results/k-ladder-2026-09-12/findings.md:602` (§ 4.3, "+0.0573") and `:1571-1573`;
  - § 7.4 (`:1053-1075`): its "K = 3 takes 37 % to 91 % of each ladder's total F1 gain"
    no longer holds here, where K = 3 takes more than all of it; its US$43-per-0.001
    last step is unchanged but now lies between two dominated rungs;
  - `phase2/ladder-tables.md:156, :178`;
  - `reports/k-ladder-phase2-deltas-2026-09-12.md:120, :178`;
  - `recovery-fix-2026-09-13/README.md:25-26, :222-223`.
- **"Their F1 is unaffected" is wrong.** The claim stands at
  `reports/tile-mcc-geometric-join-2026-09-12.md:316-319`,
  `scripts/build_k_ladder_phase2_tables.py:222-227` (comment), and
  `docs/paper/results-claims-inventory-2026-09-12.md:461` (R3-13). The rungs are
  0.025 to 0.028 low.
- **Not affected.** The K-ladder Hsu multiple-comparisons-with-the-best (MCB) analysis
  and the tile-MCC claims: both arms withhold these rungs because the per-tile table is
  refused, and the refusal stands ON (§ 4.1, MCC column).
- **The Era-2 board (`gs-era2-verified-board-2026-09-10`, signed).** The three rungs are
  withheld from tiering under both scopes, so **no tier changes**. But the quoted F1s
  change, at `run-analyses.json:3138` (outcome),
  `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md:164-165, :407,
  :555, :636-637`, `tiering_20m.md:13-14`, and `frame-deltas.md:52, :61`. By point
  estimate, K = 3 at 0.9135 would rank **5th of 153**: only four tiered cells exceed it
  (`tiering_20m.json` → `ranking`), and it would sit above the Tier 1 member
  `g37-text-k10-verified-carried-p0.10-k10-era2b` (0.9068).
- `results/conditions-manifest.md:595-597` and `reports/modality-rulings-deltas-2026-09-14.md:301`
  quote the same F1s. **Flag:** the manifest still prints the pre-invariant MCC 0.1337
  and 0.1422 for two rungs the board withholds.

### 5.2 Null-exemplar sensitivity (`null-exemplar-sensitivity-2026-09-13`, signed)

The 3.7 rungs' reduced-frame twins carry 34 to 40 out-of-frame detections: their
detections keep the proposer's tile names, so the leak filter, which drops by
frame tile name, removed none of them. Those detections are then booked as false
positives on the reduced frame. Scoped, all three movements nearly vanish
(`out/downstream.json` → `null_exemplar_era2`):

| Cell | Committed Δ F1@20 | ON Δ F1@20 |
|---|---:|---:|
| `g37-text-k1-verified-opmax` | −0.0074 | −0.0007 |
| `g37-text-k3-verified-opmax` | −0.0072 | −0.0001 |
| `g37-text-k1-verified-carried-p0.10-k1` | −0.0071 | +0.0001 |

The Era-2 text group then reads mean −0.00253 (was −0.00275) and median −0.00235
(was −0.00245). Its largest movement is −0.0068, tied by three text cells
(`grid-2026-08-18::g384-ov192-k10-verified37-p0.98-k10-era2b`,
`proposer-verifier-384::verified-adversarial-image-era2b` and
`proposer-verifier-384::verified-cascade-checklist-adversarial-era2b`) and one image
cell (`image-b-gs-2026-08-28::g384-ov192-image-high-k10-verified-p0.20-k8-era2b`). The
image-minus-text mean gap narrows from +0.00062 to +0.00040. **The finding's
direction stands** (image cells still lose less). The quoted maximum 0.0074 becomes
**0.0068** at `results/null-exemplar-sensitivity-2026-09-13/findings.md:24, :166,
:183, :313` and in the register outcome (`run-analyses.json:4204`). The reduced-frame
tiering was not re-run (the 3.7 rungs are withheld there too).

### 5.3 Verifier-uplift supplement (`verifier-uplift-pairing`, signed, Appendix)

Forty rows (20 F1, 20 MCC) of `results/uplift-supplement/verifier-uplift.csv` and
`verifier-uplift-mcc.csv` read an unverified 55-map stride twin that has an
out-of-frame detection (`out/downstream.json` → `verifier_uplift`). The largest
F1@50 uplift change is −0.0033, on the three `g384-ov192-55map-n1` pairs (for
example `…n1-oracle-p0.20-k1-r2-gt`, 0.4926 → 0.4893). MCC uplifts move by at most
0.0003. No sign or ordering claim of the supplement rests on a difference that
small. The 41 waived gap-fill anchors feed
no committed table (no consumer found under `results/`, `reports/`, `docs/` or
`planning/`); the 512 px cells on the 384 px frame are waived, uncited by the paper,
and named only in Obs 309 (`docs/notes/working-notes.md:15349-15353`).

**Flag:** Obs 309 diagnosed those cells' point-outside-interval bootstrap as
sparse-coverage asymmetry. Their point estimates also book 137 to 409 out-of-frame
false positives that the per-tile table does not see. This was not re-tested; the
earlier diagnosis may be incomplete.

### 5.4 Adjacent and surprising: sheet re-keying (tier E and h13)

`calculate_f1_internal` matches per sheet. A re-key that picks the nearest frame tile
among *all* sheets moves detections near a sheet boundary onto the neighbouring
sheet, whose padded tiles overlap. There the detection cannot match its own sheet's
reference, so one true positive becomes a false positive plus a false negative.
`tier_e_sheet_rekey.py` matched every tier E cell detection to its crop-manifest
candidate (identical coordinates) and restored the origin sheet:

| Tier E cell | Re-keyed to another sheet | Committed F1@20 (R) | Origin sheet + geometric scope F1@20 (R) |
|---|---:|---|---|
| K = 1 opmax | 7 | 0.8546 (0.8782) | 0.8680 (0.8920) |
| K = 1 carried | 7 | 0.8540 (0.8874) | 0.8673 (0.9011) |
| K = 3 (opmax = carried) | 6 | 0.8840 (0.8759) | 0.8979 (0.8897) |
| K = 5 (opmax = carried) | 7 | 0.8905 (0.8690) | 0.9046 (0.8828) |
| K = 10 rung (grid union, `materialise_grid_unions`) | 0 | 0.8886 (0.8529) | 0.8886 (0.8529) |

`out/tier_e_sheet_rekey.json`. The opmax origin-sheet values equal the ON sweep
argmax rows of § 4.4 (0.8680, 0.8979, 0.9046).

- **§ 8.6's claim moves on its verified side.** `findings.md:1395-1410`, the k-ladder
  outcome (`run-analyses.json:3931`) and claims inventory R3-14 (`:462`) say the
  verifier "absorbs 40.6 %" of K's F1 return, from verified +0.0340
  (0.8546 → 0.8886). Under consistent origin-sheet attribution the verified gain is
  **+0.0206**, and on the unchanged consensus-only +0.0572 the verifier would absorb
  **64.0 %**. The consensus-only side comes from `grid_analysis.as_gdf`, which re-keys
  the same way and **was not measured**, so this arithmetic is provisional.
- **The tier E ladder then peaks at K = 5** (0.9046 against K = 10's 0.8886). The
  frames report's "like for like" (`findings.md:1337`,
  `reports/k-ladder-closeout-deltas-2026-09-12.md:541-542`) fails on this axis too.
- **h13 (`h13-overlap-2026-08-18`, signed, Results).** The census
  (`sheet_attribution_census.py`, `out/sheet_census.jsonl`) found cross-sheet
  detections in all six h13 cells (16 to 64 per three-pass cell). Restoring the origin
  sheet raises F1@20: common-scope arm A 0.5580 → 0.5734, arm B 0.5198 → 0.5300,
  arm C 0.4025 → 0.4116; native arms A 0.5576 → 0.5730, B 0.5222 → 0.5277, C 0.4067 →
  0.4130. The registered contrast A − B (+0.0380, CI lower bound +0.0009,
  "marginal") would widen to about +0.043. No sign changes. The bootstraps were not
  re-run.
- **Coverage of the census.** It covers the 1,680 cells whose files record the
  proposer's tile (`source_tiles`, `origin_source_tile` or `origin_tiles`); the only
  cross-sheet cells among them are the six h13 cells. The 1,047 cells that do not
  record it cannot be checked from the file. Tier E was checked by the manifest join
  above.

## 6. Options for the PI

**(A) Scorer fix.** Change the detection scope in the shared code so that detections
are scoped exactly as references are: per sheet, by the detection's own (origin)
sheet, kept only if they intersect one of that sheet's frame tiles. This is
`geometric_detection_scope`, applied in `calculate_f1_internal` (`:1648`) and
`compute_per_tile_tp_fp_fn` (`:1290`), and in the engine copy
`compute_counts_at_r` (`compute_corrected_f1_multi_buffer.py:540`). The four script
copies in § 2.1 follow.

- *What it touches.* Measured: **70 evaluations change input, 55 by ≥ 0.001**. All
  other 2,681 diagnosed cells receive identical rows and reproduce bit for bit, so
  "re-run everything" reduces to re-running those 70 plus the 12 sweeps (no argmax
  moves). Registers: three condition rows (the 3.7 rungs, via
  regenerated `conditions-manifest.json`) and the outcomes of four signed analyses
  (`k-ladder-2026-09-12`, `gs-era2-verified-board-2026-09-10`,
  `null-exemplar-sensitivity-2026-09-13`, `verifier-uplift-pairing`). Documents: about
  fifteen, listed in §§ 5.1–5.3. Tests: tier-1 cases for an out-of-frame detection,
  a null `source_tile`, and a cross-sheet point.
- *Risks.*
  - It touches the library every scorer imports, so a regression would be corpus-wide.
    Gates (i) to (iii) are the template for a pre-merge check.
  - The per-tile table and the point estimate become consistent for these cells,
    which shifts their per-tile tables too. For the three 3.7 rungs that table stays
    refused.
  - One MCC flips from printed to refused. The gap-fill anchor
    `stride-phaseb … g512-ov176 … k6` prints 0.0843 OFF because out-of-frame detections
    whose names collide with frame tiles padded the tile-join invariant's booked count.
    Scoped, the invariant refuses (`moved_grouped.csv`).
- *Design choice to rule on.* Per-sheet (identical to references, recommended)
  against union-geometry. They differ only on the 55-map rows, where every dropped
  detection lies inside a neighbouring sheet's tiles (§ 4.2).

**(B) Per-analysis clipping.** Leave the scorer; re-materialise clipped detection
sets for the affected analyses only. That is the three 3.7 rungs and their three
null-exemplar twins (re-evaluated), the uplift pairing twins (the CSV rows
re-derived), and, optionally, annotations on the 41 waived cells.

- *What it touches.* The same register rows and documents as (A), minus the library,
  engine and test changes.
- *Risks.* The latent defect stays in every scorer. Any future cell whose universe
  extends beyond its frame is silently biased again: a native-grid union on the
  board, a cross-tile-size comparison, or a sub-frame like the 327-tile Era-3 set.
  (Universe scan: the 3.7 K = 1 crop universe, 640 candidates, would carry 193
  out-of-frame candidates on the 327-tile frame; `out/universes.jsonl`, frame
  `era3-h10-327`.) Two conventions would coexist. And **the obvious clipping route, re-keying, is itself
  biased**: tier E's re-key clip cost 0.013 to 0.014 F1 per rung through sheet
  re-keying (§ 5.4). A clip must drop by origin-sheet geometry, never re-assign.

**Recommendation: (A), per-sheet, origin-sheet attribution, with a recorded
diagnostic.** The measured cost of (A) is the same 70 cells (B) would touch, because
every other cell is provably unchanged. (A) also closes the hazard for every future
frame and makes the F1 point and the per-tile table describe the same detections.
Write the out-of-frame and cross-sheet counts into each `evaluation.json`, as the
tile-join diagnostics already are, so a reader can see that a scope rule fired.
Rule separately, and before either option is executed, on:

1. **Sheet attribution.** Never re-key a detection across sheets; tier E's six cells
   and h13's six need re-scoring under whichever rule is chosen.
2. **The universe question that neither option settles.** The 3.7 K = 5 and K = 10
   unions were filtered to the grid-common footprint upstream, so they cannot reach
   the 7 board mounds in the 37.94 km² band that the native K = 1 and K = 3 unions can
   (frames report § 4). Tier E's K = 10 rung likewise. Under (A) the 3.7 ladder reads
   0.8747 / 0.9135 / 0.9066 / 0.9068 on mixed universes. Matched by clipping K = 1 and
   K = 3 to grid-common, it reads 0.8682 / 0.9073 / 0.9066 / 0.9068. Matched the other
   way, the K = 5 and K = 10 unions would have to be rebuilt natively: US$0 to rebuild,
   but a new verifier pass, which is an API decision. Either way the ladder is no longer
   monotone at K = 3 → 5, and the +0.0573 headline should not be cited until this is
   ruled.

## 7. Limits

- **Point estimates only.** No bootstrap intervals, tile-swap permutations, tier
  assignments or Hsu MCB sets were recomputed. The three registered movers are
  withheld from every per-tile instrument under both scopes, so no committed tier can
  change through them. Tiers for the waived and supplement cells were never published.
- **MCC is reported where committed**, under the cell's recorded tile join (`id`
  throughout). Where an MCC is defined both OFF and ON it moves by at most 0.0003.
- **Not scored: 49 evaluations.** Twelve `results/deployment-oracle-2026-06-06/preverifier-eval`
  cells (their gitignored consensus files are absent on sapphire), one e47 pass, and 36
  pre-metadata evaluations (`results/retest/*-evaluation.json`,
  `results/verifier-t-pilot/**`). They are unmeasured. The twelve 55-map cells come
  from the standard grid, whose universes show no out-of-frame candidates in the scan.
- **Sweeps were re-run where a universe has out-of-frame candidates**: ten GS and two
  55-map stride. Not re-run: the 55-map final board's ladder-twin sweeps
  (`final_board_sweeps.py`) and the gemini37 55-map sweeps. The latter's universes
  have 0 out-of-frame candidates, so they cannot move; the former were not scanned.
- **The null-exemplar reduced-frame inputs are gitignored.** They were rebuilt in
  scratch by re-implementing `filter_one`; all 305 files match the committed kept
  counts (`rebuild_null_exemplar.py`).
- **The sheet-attribution census sees only files that record origin tiles** (§ 5.4).
  The 64.0 % figure in § 5.4 is provisional until the consensus-only side is measured.
- **The input-drift cells (§ 3.1) are measured on today's inputs**, not the ones their
  committed numbers came from.
- **Entry-point inventory.** The scorer-script inventory is a subagent's read; the
  anchors cited here were re-read, the remaining grouping was not.

## Changelog

### 2026-10-07 — Input-drift flag withdrawn (Session 163)

§ 3.1's "flagged as surprising" input drift was traced
(`reports/input-drift-2026-10-07.md`, `abe87128f`): documented recoveries, inputs
pinned by `e82_input_vintage`, 53 of 54 cells reproduced at their scored inputs. The
bullet is rewritten and "superseded under E57" corrected to E71. No number in this
report changed; the gate table's counts stand (they compare against today's files).

### 2026-10-07 — Original publication (Session 163)

First publication: the blast-radius measurement the PI asked for on 2026-10-07,
against checkout `f01ac3043`, with scripts and outputs in
`frames-blast-radius-2026-10-07-scripts/`.
