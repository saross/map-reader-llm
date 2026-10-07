# Scorer frames: rulings D50 and D51 implemented and measured, 2026-10-08

> **Last revised**: 2026-10-08 (original publication, Session 163). See [§ Changelog](#changelog) for revision history.

**Status: FOR THE PI.** Implementation of two PI rulings of 2026-10-07
(`planning/pi-decisions-2026-09-20.md`, entries D50 and D51) on branch
`scorer-frames-d50-d51`, delivered as a pull request for review. Nothing on `main`
was changed, and no committed result, evaluation, register row, sweep, ladder file
or paper draft was rewritten. Every re-score below ran on sapphire in scratch
(`~/scratch/scorer-frames-d50-d51-2026-10-08/`), importing the scorer from a
disposable worktree of the branch at `bddbee0a1` (`4fd64e8a8` on the pushed
branch, § 7 item 3) and reading data from the `main` checkout. No API call was
made. Scripts and their small outputs are beside this file in
`scorer-frames-d50-d51-2026-10-08-scripts/` (outputs under `out/`); the per-cell row
file (`new_evaluations.jsonl`, 2,800 rows) stays on sapphire in that scratch
directory, beside the superseded runs § 7 describes.

Abbreviations, first use: PI is the principal investigator; F1 is the point-matched
F1 score, and P and R are precision and recall; MCC is the tile-level Matthews
correlation coefficient; GS is the four-sheet gold standard; K is the number of
proposer passes a candidate pool unions; opmax is a sweep-optimal operating point.
OFF is the scorer on `main`, ON is the frames blast-radius report's geometric wrapper
(`reports/frames-blast-radius-2026-10-07.md` § 3, "the frames report" below), and NEW
is this branch's scorer. D50 and D51 are PI rulings, not entries in the defect
register.

## 1. Headline

| Count | Value | Source (`out/`) |
|---|---:|---|
| Committed evaluations re-scored with NEW (every cell the frames report scored) | 2,727 | `summary/summary_new.json` → `classes` |
| … unchanged to 1e-9 (F1, P, R at every scored buffer; MCC) | 1,950 | same |
| … equal to the frames report's predicted ON values to 1e-9 | 70 | same (`as-predicted`) |
| … moved by origin-sheet restoration, which the frames report did not measure | 707 | same (`origin-restored`) |
| … other, or errors | 0 | same |
| Cells moving by ≥ 0.001 in any metric | 762 (55 predicted + 707) | `n_moved_ge_0.001` |
| … of which registered conditions | **68** | `registered_moved` |
| 3.7 GS K-ladder under D51 (K = 1/3/5/10, opmax F1@20) | **0.8682 / 0.9073 / 0.9066 / 0.9068** | `ladders_new.json` |
| Tier E K-ladder under D51 (K = 1/3/5/10) | 0.8604 / 0.8902 / 0.8968 / 0.8886 | same |
| Sweeps re-run whose argmax moves | 0 of 12 | `sweeps_new.json`, `stride55_new.json` |
| Phase 2 ladders the D51 gate passes as they stand | 0 of 14 (5 refused, 9 undetermined) | `ladders_new.json` → `phase2_gate_survey` |
| Tier-1 suite at the final head `9a3c7b038` | 4,024 passed, 0 failed | `tier1_summary.txt` |

1. **D50 reproduces the frames report exactly where it predicted.** All 70 cells with
   out-of-frame detections read the report's ON values to 1e-9, MCC included, and all
   ten gold-standard sweeps and both 55-map stride sweeps agree row for row with its
   ON sweeps (§ 4).
2. **Surprising: the origin rule reaches 707 more cells, and every one rises.**
   Consensus files carry `source_tiles` but no `source_tile`, so the evaluator
   synthesises one by a spatial join, taking the first frame tile in join order. In
   the overlap of two sheets' padded tiles that can be the neighbouring sheet's tile,
   though every member of the cluster was seen on the other sheet. That is the
   re-key ruling D50 forbids, made by the evaluator itself. Restoring the origin
   moves 696 cells at 20 m, **all upward** (median +0.0018, largest +0.0245; 680 of
   the 696 have a synthesised `source_tile`). The frames report's census could not see this,
   because its parser turns a NumPy array of names, which is how geopandas reads a
   JSON-array property, into one unparseable string (§ 5.2).
3. **The ruled ladder numbers hold.** The 3.7 GS ladder reads 0.8682 / 0.9073 /
   0.9066 / 0.9068 clipped to the area every rung searched (gain +0.0386), and the
   sweep re-run on that matched area keeps every rung's operating point. Tier E,
   re-scored on its origin sheets as D50 rules, reads 0.8680 / 0.8979 / 0.9046 /
   0.8886 as the frames report predicted, and 0.8604 / 0.8902 / 0.8968 / 0.8886 on
   its matched area, where it peaks at K = 5 (§§ 5.3–5.4).
4. **Surprising: the D51 gate passes none of the 14 Phase 2 ladders as they stand.**
   Besides the 3.7 ladder, four `pv-diag-384` ladders are refused because their K = 1
   pass never processed one to three tiles its K = 3 sibling did; two of those gaps
   hold reference mounds (3 and 2), which those K = 1 evaluations book as false
   negatives no coverage check could see. Nine more are undetermined, because their
   older K = 5 and K = 10 pools record no pass provenance and, in four T 0.7
   families, no pass records its tile manifest (§ 5.6).

## 2. What D50 changed

### 2.1 The rule

`scripts/lib_advanced_metrics.py` gains `scope_detections_to_frame`, the detection
scope of option (A) in the frames report's § 6. Each detection is attributed to one
map sheet and kept only if it intersects one of that sheet's frame tiles, by the
`intersects` predicate `scope_references_to_tiles` applies to references.

- **Origin sheets.** Where a file records the tile(s) a detection was seen on
  (`origin_source_tile`, `origin_tiles` or `source_tiles`, the first with a value),
  those tiles' frame sheets are its origin sheets. A `source_tile` on one of them
  stands. A `source_tile` on a sheet the detection was never seen on is a re-key
  across a sheet edge; the detection is scored on an origin sheet instead (the one
  whose tiles hold it, sorted first on a tie) and counted. With no origin recorded,
  `source_tile` decides by the scorers' long-standing prefix rule. Every
  serialisation in the corpus is parsed, including a NumPy-array `repr` stored as a
  string, which geopandas hands back wrapped in a one-element array (tier E's
  materialised cells).
- **No member tile is privileged.** `merge_passes.py` stores `source_tiles` sorted
  (`sorted(set(...))`, lines 254 and 350), so its first entry is the alphabetically
  first member, not the first seen. A cluster seen on two sheets may be scored on
  either.
- **What the rule removes.** Only detections attributed to a frame sheet and outside
  its tiles. A detection on no frame sheet (a null or foreign name) is not scored by
  the per-sheet matcher, as before, and the tile confusion keeps it, as before.
- **Unaffected cells are untouched.** A cell with no out-of-frame detection and no
  re-keyed one receives the same rows in the same order; 1,950 cells reproduce to
  1e-9 (§ 4.1).

### 2.2 Where it applies

| Entry point (frames report § 2) | Change |
|---|---|
| `calculate_f1_internal` | Per-sheet loop is now `iter_sheet_scopes`: references and detections scoped by one rule |
| `compute_per_tile_tp_fp_fn` (bootstrap intervals, tile-swap permutations) | Same loop; out-of-frame rows no longer join the matching unbooked |
| `calculate_tile_classification`, `describe_tile_join_refusal` | Drop exactly the out-of-frame rows before booking |
| `compute_counts_at_r` (corrected-F1 engine) | Its copy of the rule replaced by `iter_sheet_scopes` |
| `analyse_dawid_skene.py`, `review_candidates.py`, `discover_hard_cases.py`, `h13_overlap_analysis.py`, `analyse_55maps_heterogeneity.py` | Their copies replaced by the library's loop or scope |
| `evaluate_detections.py` | Every evaluation records a `detection_scope` block, per pass and summed |
| `sweep_f1_greedy_pv.py` | Inherits the scope; prints the universe's scope counts |
| `prepare_h13_scoring.assign_primary_tiles` (twelve call sites), tier E's `reassign_carrier_tiles` | `assign_primary_tiles_on_origin_sheet`: the nearest tile on an origin sheet, or none; tier E also writes `origin_source_tile` before overwriting |

The `detection_scope` block holds `n_detections`, `n_in_scope`, `n_out_of_frame`,
`n_out_of_frame_cross_sheet` (out of frame but inside another sheet's tiles),
`n_origin_restored`, `n_origin_only`, `n_origin_unrecognised`, `n_unattributed` and
`n_unattributed_in_frame`, with the rule's name and the ruling's text. The cell's own
`n_detections` beside it stays the file's feature count.

**Left as they are, deliberately.** `score_leaderboard_cells.py` and
`evaluate_pilot.py` filter candidates to a list of tile names before scoring. The
lists define a candidate universe (for example the 327-tile H10 test set), not a
scoring scope, so they stay, and the library's geometric scope applies on top. The
evaluator still synthesises a missing `source_tile` by spatial join; the scorer now
overrides it wherever the file records an origin. Callers that hand
`assign_primary_tiles` bare cluster centroids with no origin
(`grid_analysis.as_gdf`, `materialise_grid_unions.union_with_votes`, image-B and
stride analyses) keep the legacy nearest-centroid rule (§ 7, item 6).

## 3. What D51 changed

### 3.1 The area a pool assessed

`scripts/lib_assessed_area.py` determines a candidate pool's assessed area from
provenance alone, in this order:

1. a **record** its builder wrote beside the union (`union_k5.assessed-area.json`),
   naming the tiling's polygons, the manifest the passes covered, and any clip;
2. a **declaration** for a legacy pool in
   `inputs/provenance/assessed-area-declarations.json`, citing its evidence;
3. the consensus step's **pass provenance** (`voting_summary.json` →
   `pass_provenance`): each pass's own `processed_tiles` on its tiling's polygons,
   recovery fragments resolved through their subset manifests. `merge_passes.py`
   applies no clip.

Anything else is **undetermined**, with the reason; the function never infers an area
from a path or a naming convention. Five tilings are registered with their polygon
files in `KNOWN_TILINGS` (the 487-tile 384 px frame and the four grid tilings), each
checked tile for tile against its manifest at use. As a consistency check, every
candidate of the pool must lie inside the area its provenance claims (1 m tolerance),
or the area carries a warning.

Three legacy pools are declared: the 3.7 GS K = 5 and K = 10 unions
(`image_b_prepare_and_union.py`) and the grid K = 10 union tier E carries
(`materialise_grid_unions.py`). Each declaration cites the builder's coverage gate,
the clip lines and the committing commit; all 791, 913 and 3,319 of their candidates
lie inside the declared areas.

### 3.2 The check

`compare_assessed_areas` intersects each pool's area with the scoring frame and
compares it with the area common to every pool. A pool whose effective area exceeds
the common area by more than the tolerance is a mismatch. The comparison **refuses**
(exit 3) unless the caller asks to clip to the common area; then the output names the
clip (`clip-to-common-assessed-area`) and the area each pool loses. An undetermined
pool **refuses** (exit 4) unless the caller explicitly allows it, and even then the
status reads `undetermined`, never `same`. Because the common area is the
intersection, two areas of equal size in different places are refused too.

**Tolerance.** 0.01 km² (`DEFAULT_TOLERANCE_KM2`) is a 100 m square, far below the
smallest real gap § 5.6 finds (2.0819 km², one tile's unshared part) and far above
floating-point noise on polygon unions.

### 3.3 Where it is wired

| Code | Gate | On a clip |
|---|---|---|
| `build_k_ladder_phase2_tables.py` (writes `phase2/ladders.json`) | every ladder, before anything is written | each reported point re-scored with its detections clipped and the frame's references kept, under `clipped_to_common_area` |
| `score_k_ladder_phase2_rungs.py prepare` (K = 1, 3 sweeps) | per family, against its committed K = 5 and K = 10 | sweeps get `--clip-area`; materialised cells clipped |
| `derive_g37_gs_opmax_rungs.py prepare` (3.7 K = 5, 10 sweeps) | against the family's K = 1 and K = 3 | same |
| `run_k_ladder_tier_e.py prepare` (tier E sweeps) | K = 1, 3, 5 against the committed K = 10 | same |
| `sweep_f1_greedy_pv.py --clip-area` | — | every output row names the clip and the candidates removed |
| `check_assessed_areas.py` | any set of pools, from the command line | writes the common area as GeoJSON |

Every gated driver takes the same three options, `--area-tolerance-km2`,
`--clip-to-common-area` and `--allow-undetermined-area`. Going forward,
`image_b_prepare_and_union.py` and
`materialise_grid_unions.py` write their record with each union, recomputed before it
is written, so an unresolvable record fails at build time. The Phase 1 builder
(`build_k_ladder_tables.py`), `build_k_ladder_inventory.py`,
`tier_e_ladder_tiering.py` and the K-ladder consumer analyses are not wired (§ 7,
item 8).

## 4. Validation

### 4.1 Cells

`rescore_new.py` re-scored every one of the frames report's 2,727 scored cells with
NEW, at that report's own buffers, and `summarise_new.py` classified each against its
OFF and ON values (`summary/summary_new.json`). 1,950 reproduce OFF to 1e-9 with
nothing fired; all 70 cells with out-of-frame detections reproduce ON to 1e-9, MCC
included, and 55 of them move by ≥ 0.001, the frames report's count; no cell is
unexplained, and none errored. The 24
corrected-F1 adapter cells and the 49 the frames report could not score were
diagnosed or skipped as there.

The scope fired on 82 cells for out-of-frame rows, the 70 and 12 more (ten tier E cells
and copies, two archived artefacts) whose null-`source_tile` rows are now attributed
through their recorded origin and dropped as out of frame instead of as unattributed.
They were not scored before either.

### 4.2 Sweeps

| Sweep (frame) | Out of frame | Rows moving vs committed | Argmax committed → NEW | Equal to frames-report ON |
|---|---:|---:|---|---|
| 3.7 K = 1 (board) | 38 | 80 of 80 | (1, 0.15) 0.8495 → 0.8747 | yes |
| 3.7 K = 1 (Era-2) | 38 | 80 of 80 | (1, 0.15) 0.8495 → 0.8747 | yes |
| 3.7 K = 3 (board) | 45 | 240 of 240 | (3, 0.10) 0.8870 → 0.9135 | yes |
| 3.7 K = 1, recovery-fixed (board) | 38 | 80 of 80 | (1, 0.15) 0.8495 → 0.8747 | yes |
| 3.7 K = 3, recovery-fixed (board) | 45 | 240 of 240 | (3, 0.10) 0.8860 → 0.9135 | yes |
| 3.7 K = 5, control (board) | 0 | 0 of 400 | (5, 0.10) 0.9066 → 0.9066 | yes |
| Tier E K = 1 (board) | 96 | 80 of 80 | (1, 0.20) 0.8462 → 0.8680 | yes |
| Tier E K = 3 (board) | 125 | 240 of 240 | (3, 0.15) 0.8746 → 0.8979 | yes |
| Tier E K = 5 (board) | 148 | 400 of 400 | (5, 0.15) 0.8828 → 0.9046 | yes |
| Tier E K = 5, recovery-fixed (board) | 148 | 400 of 400 | (5, 0.15) 0.8828 → 0.9046 | yes |
| 55-map stride A `g384_ov128` (50 m) | — | 2 of 200 | (k7, 0.15) 0.8362, unchanged | 200 of 200 rows |
| 55-map stride B `g384_ov192` (50 m) | — | 3 of 200 | (k9, 0.20) 0.8503, unchanged | 200 of 200 rows |

Sources: `sweeps_new.json` (the frames report's own jobs, swept with the worktree's
`sweep_f1_greedy_pv.run_sweep`, no wrapper) and `stride55_new.json` (the corrected-F1
engine, now scoped, no wrapper). "Equal" means the argmax point, its F1, the F1 at the
committed argmax and the count of moving rows all match the frames report's ON sweep.

### 4.3 Tests and red sentinels

Two new tier-1 modules hold 54 tests, `tests/test_detection_scope.py` for D50 and
`tests/test_assessed_area.py` for D51 (refusal, clip, undetermined pools, pass
provenance, recovery fragments, declarations, the builder's gate and the sweep's
clip). The
golden test in `tests/test_tile_join_withheld.py` now asserts that `detection_scope`
is the only addition to its pre-change golden, and that it recorded nothing removed.

`red_sentinel.sh` builds a real copy of the branch head, `bddbee0a1` (`git archive`,
0 symlinks),
runs the two modules green, then breaks each rule once in the copy
(`red_sentinel.txt`):

| Break | Tests red | Restored |
|---|---:|---|
| D50 geometric scope disabled (every attributed detection kept) | 8 of 52 | 52 green |
| D51 refusal disabled (no comparison mismatches) | 6 of 52 | 52 green |

The two ladder-builder wiring tests are deselected in the copy, because importing the
builder computes the whole passes register, which reads artefacts across `outputs/`. They pass
in the full worktree.

The tier-1 suite on sapphire at the final head, `9a3c7b038` (the branch rebased onto
`main` at `d76be2814`), reads **4,024 passed, 0 failed**, 5 skipped, 3 xfailed and
54 deselected (`tier1_summary.txt`). At the measurement head, `bddbee0a1`, it read
4,016 passed and 1 failed. That failure,
`test_lib_detection_paths.py::test_no_bare_convention_a_glob_outside_this_module`,
named `delete_landed_caches.py` and `modality_bridge_union.py`, the concurrent Run B
session's new files; it failed identically on a clean copy of `origin/main` at
`2956c4250`, and `main` has since fixed it (`01bdbc53d`).

### 4.4 Union builders and cost

`modality_bridge_union.py --validate-originals`, run with the branch's code at
`bddbee0a1`, rebuilds all four original clipped unions in both layouts and finds all
eight equal to the committed files, byte for byte (`runb_validation.json`). The
origin-restricted primary-tile rule changes no union, because a union's carrier tiles
come from bare centroids. The scope adds about 5 ms to a `calculate_f1_internal` call
that takes about 283–342 ms on a 3.7 universe (`time_scope.txt`).

## 5. Impact

### 5.1 Out-of-frame detections: the frames report's 70 cells

NEW equals the frames report's ON for all 70, so its § 4.1 table (55 cells moving by
≥ 0.001) and its §§ 5.1–5.3 consequences stand as written for those cells. They
include the 3.7 rungs (K = 1 0.8495 → 0.8747, K = 3 0.8860 → 0.9135, carried K = 1
0.8338 → 0.8616) and the 512 px cells on the 384 px frame (+0.060 to +0.069). The
rest of this section is what that report did not measure.

### 5.2 Origin restoration: 707 cells the frames report did not see (surprising)

`origin_restored_analysis.py` (`origin_restored_analysis.json`):

| Measure | Value |
|---|---|
| Cells moving by ≥ 0.001 at 20 m through origin restoration | 696 |
| … F1@20 rises / falls | 696 / 0 |
| … median and largest rise | +0.0018 and +0.0245 |
| … rising by ≥ 0.01 | 50 |
| … whose `source_tile` the evaluator synthesised by spatial join | 680 |
| … whose origin is `source_tiles` / `origin_tiles` | 690 / 6 |
| Cells where the scope restored at least one detection | 1,090 |

**Mechanism.** A consensus file records each cluster's member tiles but no
`source_tile`, so `evaluate_detections.py` assigns one by a left spatial join to the
frame, keeping the first tile in join order (`_evaluate_condition`). In the band where
two sheets' padded tiles overlap, that first tile can belong to the neighbouring
sheet, though the cluster was seen only on its own sheet's tiles; the per-sheet matcher
then cannot match it to its own sheet's reference, and one true positive becomes a
false positive and a false negative. That every one of the 696 moves is upward is what
that mechanism predicts. The join's first-tile choice also depends on the frame file's
row order, which § 5.5 shows matters.

**Why the frames report missed it.** Its census
(`frames-blast-radius-2026-10-07-scripts/sheet_attribution_census.py`, `as_list`)
handles lists, tuples and strings. geopandas returns a JSON-array property as a NumPy
array, which `as_list` turns into a single unparseable string, so every such file
counted zero cross-sheet detections by construction (the analysis feeds it a
two-name array and gets one string back). Its finding that "the only cross-sheet cells
among them are the six h13 cells" held only for h13's `;`-joined `origin_tiles`.

**Which cells.** Of the 707, 637 are GS Era-2 cells and 42 Era-1 null-exemplar
twins; the rest are 9 55-map, 5 board, 4 board null-exemplar twins, 6 h13 and 4
archived cells (`summary/moved_new.csv`). By signed analysis, from the frames
report's register columns:

| Analysis | Moved cells (all registered) | Largest change, any metric | F1@20 change |
|---|---:|---:|---|
| `uplift-supplement-flatten` | 61 | 0.0204 | +0.0004 to +0.0155 |
| `pv-diag-384-consensus-calibration` | 27 | 0.0028 | +0.0016 to +0.0025 |
| `tile-size-sweep` | 8 | 0.0028 | +0.0019 to +0.0025 |
| `k-ladder-2026-09-12` | 7 | 0.0509 | +0.0133 to +0.0278 |
| `null-exemplar-sensitivity-2026-09-13` | 7 | 0.0509 | +0.0133 to +0.0278 |
| `e43-matched-temperature` | 7 | 0.0023 | +0.0016 to +0.0021 |
| `h6-a07-voting-thresholds` | 6 | 0.0023 | +0.0012 to +0.0018 |
| `diversity-dividend-384` | 4 | 0.0025 | +0.0021 to +0.0024 |
| `h13-overlap-2026-08-18` | 3 | 0.0204 | +0.0092 to +0.0155 |
| `e45-bootstrap-pairings` | 1 | 0.0024 | +0.0024 |
| `family-bh-fdr-confirmatory` | 1 | 0.0024 | +0.0024 |

A cell can serve several analyses; the k-ladder and null-exemplar rows include the
three 3.7 rungs of § 5.1. Outside h13, tier E and the 3.7 rungs, no registered cell
moves by more than 0.0034.

### 5.3 The 3.7 GS ladder

| K | Committed F1@20 | D50 | D51, clipped at the rung's point | D51, matched-area sweep argmax | Removed by the clip |
|---|---:|---:|---:|---|---:|
| 1 (opmax) | 0.8495 | 0.8747 | **0.8682** | (1, 0.15) 0.8682, n 468 | 34 |
| 1 (carried, p 0.10) | 0.8338 | 0.8616 | 0.8553 | — | 39 |
| 3 | 0.8860 (`ladders.json` 0.8870) | 0.9135 | **0.9073** | (3, 0.10) 0.9073, n 460 | 35 |
| 5 | 0.9066 | 0.9066 | **0.9066** | (5, 0.10) 0.9066, n 443 | 0 |
| 10 | 0.9068 | 0.9068 | **0.9068** | (10, 0.10) 0.9068, n 423 | 0 |

`ladders_new.json` → `g37_gs`. The gate finds K = 1 and K = 3 assessing 1,402.4067 km²
of the board frame and K = 5 and K = 10 1,364.4713 km², a 37.9354 km² excess holding 7
board reference mounds (`area_gaps.json`). Clipped, the ladder reads exactly the
ruling's figures. The K = 1 → K = 10 gain is +0.0386 (committed +0.0573), and K = 3
sits above K = 5 and K = 10. Re-sweeping each rung on the matched area keeps every
operating point, so the frames report's open question ("opmax points might also move
under a matched sweep") is answered, and they do not.

### 5.4 Tier E

| K | Committed F1@20 | D50 (origin restored) | D51, clipped | D51, matched-area sweep argmax |
|---|---:|---:|---:|---|
| 1 (opmax) | 0.8546 | 0.8680 | 0.8604 | (1, 0.20) 0.8604, n 453 |
| 1 (carried, p 0.15) | 0.8540 | 0.8673 | 0.8597 | — |
| 3 | 0.8840 | 0.8979 | 0.8902 | (3, 0.15) 0.8902, n 421 |
| 5 | 0.8905 | 0.9046 | 0.8968 | (5, 0.15) 0.8968, n 408 |
| 10 (grid union, clipped upstream) | 0.8886 | 0.8886 | 0.8886 | (10, 0.15) 0.8886, n 400 |

`ladders_new.json` → `tier_e`; restored rows per cell 7, 7, 6 and 7
(`tier_e_origin_probe_k*.json`; every one was seen only on Elenovo and re-keyed to
K-35-052-4). D50 reproduces the frames report's § 5.4 values. Under D51 the ladder
peaks at K = 5, and its K = 1 → K = 10 gain is +0.0282 (committed +0.0340; both on
four-decimal values). The frames report's "absorbs 40.6 %" claim
(`findings.md:1410`) would read 50.7 % against the unchanged consensus-only +0.0572,
but that side comes from `grid_analysis.as_gdf`, whose bare centroids carry no origin
for the new rule to use, and nobody has measured it (§ 7, item 6).

### 5.5 h13 and the null-exemplar twins

The six h13 cells read common arm A 0.5579 → 0.5734, B 0.5198 → 0.5300, C 0.4024 →
0.4116, and native arm A 0.5575 → 0.5730, B 0.5221 → 0.5276, C 0.4066 → 0.4129
(16 to 64 restored detections per three-pass cell). The registered common-scope
contrast A − B therefore widens from +0.0382 to +0.0434 at these point estimates
(the register records +0.0380); the bootstraps were not re-run.

**Surprising: 42 Era-1 null-exemplar twins move, by +0.0061 to +0.0183, while no
full-frame Era-1 cell moves.** For the matched pair checked,
`retest-phase3a-high::text-high-t0.3-n10-8of10`, the full-frame parent
(`results/rescore-2026-06-07/phase3/phase3a-high__track2-text__T0.3__n10__t8`) has no
re-keyed detection and stays at 0.7595, while its reduced-frame twin had 7 detections
joined to a sheet they were never seen on and moves 0.7350 → 0.7453. Removing the
overlap tiles changed which tile the spatial join met first. The analysis's committed
reduced-minus-full change for that cell, −0.0245, is −0.0142 under D50, so part of the
Era-1 null-exemplar effect is this attribution artefact. The seven board twins move
too (the three 3.7 rungs as the frames report predicted, and four tier E twins).

### 5.6 The D51 gate over every Phase 2 ladder (surprising)

Run unclipped and allowing undetermined pools (`ladders_new.json` →
`phase2_gate_survey`):

| Ladder (proposer pool) | Gate | Why |
|---|---|---|
| `g384_ov192_g37` (3.7 GS) | refused, 37.9354 km² | K = 5, 10 clipped upstream (§ 5.3) |
| `flash-minimal-text-n30-t07-text-t0.3` | refused, 2.0819 km² | K = 1 never processed `K-35-053-3_Elenovo_x336_y2016.png`; 0 mounds in the gap |
| `flash-minimal-text-n30-t07-text-t1.0` | refused, 2.0893 km² | K = 1 never processed `K-35-062-2_Rakovski_x3360_y2688.png`; 0 mounds |
| `flash-high-text-n5-text-t1.0` | refused, 4.7609 km² | K = 1 never processed three tiles; **3 mounds** in the gap |
| `image-n5-image-t1.0` | refused, 2.4289 km² | K = 1 never processed `K-35-053-3_Elenovo_x1344_y672.png`; **2 mounds** |
| four `pv-diag-384` ladders and `scale-4-optimal-487` | undetermined | K = 5 and K = 10 pools' `voting_summary.json` records no pass provenance; K = 1 and K = 3 agree with each other |
| four T 0.7 ladders | undetermined | additionally, their passes have no meta file recording a tile manifest |

`area_gaps.py` (`area_gaps.json`) names the tiles and counts the board reference
mounds inside each gap. A missing tile in a single pass is the E72 failure mode, but
these K = 1 rungs are scored from consensus files that carry no `processed_tiles`, so
the coverage guard could not see it; the gate sees it from the pass provenance.

## 6. What the PI would approve next (nothing below has been changed)

**Code.** Merging the branch changes the scorer every script imports. From then on, a
regenerated artefact will differ from its committed copy wherever § 5 measures a move,
and every new evaluation carries `detection_scope`.

**Registered conditions (68 move by ≥ 0.001).** The three 3.7 rungs (§ 5.1), the six
h13 arms, four tier E cells, and 55 consensus and pass cells across the analyses of
§ 5.2's table, none of which moves by more than 0.0034. `summary/moved_new.csv` lists
each with its OFF and NEW F1 at 20 m and 50 m. Re-registering them is a regeneration of
`results/conditions-manifest.json` from re-run evaluations.

**Sweeps.** The ten gold-standard sweeps of § 4.2 move on every row but keep their
argmaxes; the two 55-map stride sweeps move on 2 and 3 rows.

**Ladder files.** `results/k-ladder-2026-09-12/phase2/ladders.json` (and its tables and
figure) for the 3.7 family; `tier-e/` (`ladder.json`, `scores.json`, cells); and
`recovery-fix-2026-09-13/`. Under D51 the phase-2 builder will refuse to regenerate
until the PI rules on the 13 other ladders (below).

**Documents.** The citing sites of the frames report's § 5, of which these were
re-read at this head, `results/k-ladder-2026-09-12/findings.md:602` and `:1573`
(+0.0573), `:1295`, `:1317`, `:1408` and `:1410` (tier E's +0.0340 and 40.6 %), and
`:1338` ("like for like"); `phase2/ladder-tables.md:156–157`, `:178`, `:199`;
`reports/k-ladder-phase2-deltas-2026-09-12.md:120` and `:178`;
`recovery-fix-2026-09-13/README.md:25–27`;
`results/null-exemplar-sensitivity-2026-09-13/findings.md:24`, `:166` and `:183`;
`docs/paper/results-claims-inventory-2026-09-12.md:461` (R3-13). The frames report's
other sites (register outcomes in `results/run-analyses.json`, the signed board's
README and tiering, `results/conditions-manifest.md`, the uplift CSVs) were not
re-read here. Beyond them, the h13 findings and register outcome (A − B) and the
null-exemplar analysis's Era-1 statistics change (§ 5.5).

**The PI is asked to rule on four questions.**

1. **Accept the origin-restoration scale.** D50 was ruled on a measured 70 cells; the
   rule as ruled ("never re-key") also restores 707 cells the frames report could not
   see, every one upward. Accept, or narrow the rule (for example to files with a
   recorded `source_tile` only), which would leave the evaluator's spatial-join
   re-key in place.
2. **The four refused `pv-diag-384` ladders.** Clip their larger rungs to the K = 1
   rung's area (option 1 of D51, applied to them), or accept the gap (two of the four
   gaps hold no reference mound).
3. **The nine undetermined ladders.** Declare their pools' provenance (the passes
   may be recoverable from the pools' directory layout, which the gate deliberately
   does not infer), or have the builder run with `--allow-undetermined-area`, which
   records them as undetermined.
4. **The re-score itself**, as a separate step after merging, deciding which of
   § 6's artefacts to regenerate and in what order.

## 7. Implementation notes and surprises

1. **The attribution rule went through three versions; the third is the one
   measured.** The first ("any member's sheet") was right but missed tier E through a
   parse bug (item 4). The second privileged the first recorded member tile, on the
   belief that `source_tiles[0]` is the candidate's own tile. It is not:
   `merge_passes.py` sorts the list, so the first entry is alphabetical. The third
   restores the first rule with the parse fixed. Compared cell by cell, the second
   and third runs differ by ≥ 0.001 on only 10 cells (`origin_restored_analysis.json`
   → `first_origin_vs_any_member_cells_differing_ge_0.001`), all tier E cells and
   copies whose origins the second run could not parse (371 to 397 unrecognised
   each). Everywhere both runs read the origin, the two rules agree to 0.001, so the
   choice rests on the sorted list, not on effect size. **Correction:** the message
   of commit `4fd64e8a8` attributes the 701 cells the second rule moved to its privileging the
   first member; those moves come from the evaluator's spatial-join re-key (§ 5.2),
   which both rules restore. The rejected rule's summary is kept in
   `out/rejected-first-origin/`.
2. **The tile confusion briefly dropped unattributed rows.** The first full tier-1
   run failed 28 tests: 26 tile-confusion tests, the golden test of § 4.3 and the
   inherited one (commit `fe32793ca`'s message says 27). D50 removes exactly the
   out-of-frame rows, so `DetectionScope.retained` keeps everything else for the
   confusion; this was fixed before any number here was produced.
3. **Superseded runs are preserved, not deleted**, on sapphire under
   `out/first-run-any-member-origin/`, `out/superseded-pre-retained-fix/`,
   `out/superseded-6b25cb9cf-array-parse/` and
   `out/superseded-c9c3d5035-first-origin-partial/`. The branch was rebased onto
   `main` while the work ran, so runs carry the hash they ran at. On the pushed
   branch, measurement head `bddbee0a1` is `4fd64e8a8` (the scorer and every other
   file the branch changes are identical, apart from the comment corrected in
   `a84451667`); `6b25cb9cf`, also `b935cdb0e` before an earlier rebase, is
   `fe32793ca`; `c9c3d5035` is `31706629a`; `c4867e7a2` is `30d871371`; and the
   rejected first-origin commit `6b642faaf` is `6e858c0cb`.
4. **Tier E stores `source_tiles` as the `repr` of a NumPy array**
   (`"['K-35-…' 'K-35-…'\n …]"`), a string geopandas reads back wrapped in a
   one-element array. `parse_tile_list` now expands it; a test writes and reads a real
   GeoJSON to keep it so.
5. **Run B's per-pass dedup files would change on rebuild.** Its union validation
   shows `write_dedup_geojson` now keeping 8 to 17 points per pass (60 passes
   rebuilt) on their origin sheet where the legacy rule re-keyed them (`runb.log` on
   sapphire). The unions are unaffected (§ 4.4).
6. **Bare-centroid callers still re-key.** `grid_analysis.as_gdf` and the union
   builders assign carrier tiles to cluster centroids that record no origin, by the
   legacy nearest-centroid rule. Carrying member tiles through `cluster_votes` would
   let them restrict to origin sheets; the consensus-only side of tier E's 40.6 %
   claim depends on it. This was neither done nor measured here.
7. **No union records its clip, and the gate is only as good as its registry.** The
   three declared pools are reconstructions from code and commit history. Run B's new
   builder (`modality_bridge_union.py`, the concurrent session's) writes a
   `union_k<K>.build.json` with its manifest and clip, but no assessed-area record;
   one `write_area_record` call there would make its pools determinable.
8. **Not wired to the gate:** the Phase 1 builder, the ladder inventory, tier E's
   tiering step and the K-ladder consumer analyses. They read finished rungs; the gate
   sits where rungs are swept and assembled.
9. **The test that failed on `main` during the work** (now fixed there) is in § 4.3.

## 8. Limits

- **Point estimates only.** No bootstrap interval, tile-swap permutation, tier or Hsu
  MCB set was recomputed; § 5's contrasts are point-estimate arithmetic.
- **The frames report's 49 unscored cells stay unscored**, and the 24 corrected-F1
  adapter cells were diagnosed only (none has an out-of-frame or re-keyed detection).
- **The null-exemplar twins are scored on the frames report's scratch rebuilds** of
  their gitignored inputs (`rebuild_null_exemplar.py`), which reproduce every committed
  twin; only one Era-1 parent–twin pair was checked directly.
- **The gate survey runs the gate as the builder would**, unclipped; the four refused
  `pv-diag-384` ladders were not re-scored clipped.
- **Data from the `main` checkout on sapphire**, code from the branch worktree; the
  scorer on that checkout equals `origin/main`'s.

## Changelog

### 2026-10-08 — Original publication (Session 163)

First publication of the implementation of rulings D50 and D51 on branch
`scorer-frames-d50-d51` and its impact measurement at `bddbee0a1`, with scripts and
outputs in `scorer-frames-d50-d51-2026-10-08-scripts/`.
