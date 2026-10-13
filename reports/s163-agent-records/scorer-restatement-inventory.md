# Phase 5: scorer-restatement inventory, and `per_map_counts()` on the shared attribution

> **Last revised**: 2026-10-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), an overnight subagent of the main Session 163
  session (workstream `scorer-restatement-sweep`). Four read-only Opus 5.5
  reading agents classified the candidate files. Every line, commit, date,
  and register entry cited below was re-read at source by the workstream
  agent on 2026-10-13 before it was written here.
- **Date**: 2026-10-12 to 2026-10-13 (UTC).
- **Repository**: `map-reader-llm`, branch `scorer-restatement-sweep` from
  `main` at `c546f6901`.
- **Ruling**: PI ruling D60 (3) and (4) (`planning/pi-decisions-2026-09-20.md`)
  name Phase 5's sweep for scorer restatements, `per_map_counts()` in
  `scripts/stride55_sweep_oracle.py` among them
  (`planning/paper-writeup-continuity.md`, the D50 item, "Related, confirmed
  on `main`"). The rule being enforced is D50 (2026-10-07).
- **Where the runs are**: `~/scratch/scorer-restatement-sweep-2026-10-12/` on
  sapphire (`repo/` the branch clone, `old/` a sparse worktree at
  `c546f6901`, `spy/` a sparse worktree at the fix commit, `logs/`,
  `spy-out/`, `out/`, `tools/`).
- **Guarantees**: no model Application Programming Interface (API) call;
  nothing merged; no file of the two other Phase 5 agents edited (the
  consensus route of D60 (3) and W2.7's `FastScorer` of D60 (4)); sapphire's
  shared checkout untouched; at most four, then (from about 12:50 UTC, on the
  main session's instruction) at most two, processes on sapphire.

## Bottom line

1. **`per_map_counts()` is fixed and moves nothing today.** It now iterates
   the shared scorer's per-sheet loop, so its counts sum to the F1 the same
   scripts report. Every output it feeds reproduces its committed bytes with
   the fix: the stride sweep's paired A-versus-B tests, the stride ladder's
   P7 tests and rung pairs, the A5-versus-B5 test, and the Gemini 3.7 sweep
   family and grid board. At every one of its call points no detection lies
   out of frame and no origin is recorded, so the old and new rules agree
   exactly (§ 2). No verdict changes, no signature lapses, and no committed
   output is regenerated.
2. **The largest open item is not a copy of the scorer but a gap in front of
   it.** The gold-standard (GS) grid, H13, plateau, and Image-B chains build
   bare cluster centroids and tile them with no origin, so D50's
   never-re-key rule falls back to the legacy cross-sheet choice
   (`scripts/prepare_h13_scoring.py:307-318`). It feeds signed,
   paper-cited boards (claims R1b-05, R1b-08, R1b-15 to R1b-18). Measured on
   the plateau board's four incumbents, the re-key costs **0.007 to 0.017
   F1 at 20 m** against the same files scored on their recorded sheets
   (§ 3, § 9.3). This is flagged, not fixed.
3. **Two paper-cited diagnostics keep their own matching**: the GS miss
   correlation (one Hungarian across all four sheets; claims R8-03 and
   R8-04) and the GS false-positive classification (nearest-curator split).
   The first gives the identical table when re-run per sheet on today's data
   (§ 9.2). The second differs from the scorer by design (§ 4).
4. **Most other restatements are category (e) readers on 55-map data, where
   they cannot move a number** (at most 4 rows per manifest have members on
   two sheets). § 4 to § 8 list them all, with the deliberate replicas and
   the cleared files.
5. **Side finding, not a restatement**: several signed outputs were last
   written before D50 and have never been re-scored under it, among them the
   Gemini 3.7 fourth-cell sweep, whose 8 rows at `prob_t` 0.0 move today
   under OLD and NEW alike (§ 10).

## 1. What was searched, and what counts as a restatement

The sweep covered every Python file under `scripts/` (452 at the top level
and 13 one level down), every report-side script under
`reports/*-scripts/` (101), and every script under `results/` (18), as of
`c546f6901`. A grep pass selected the candidates: own matching
(`linear_sum_assignment`, `cKDTree`, `sjoin_nearest`, buffer tests) beside
TP/FP/FN counting; `startswith` on tile or sheet names; private per-tile or
per-map counters; and scorer callers that build detection frames themselves.
Four read-only reading agents then classified about 150 files against five
categories, taken from the brief:

- **(a)** own TP/FP/FN counting or matching loops (Hungarian, nearest
  neighbour, buffer) instead of the library's;
- **(b)** detection-to-sheet or detection-to-tile assignment by `source_tile`
  prefix without origins;
- **(c)** bare `startswith` sheet matching of detections;
- **(d)** private copies of `compute_per_tile_tp_fp_fn`;
- **(e)** readers that drop origin fields (`source_tiles`, `origin_tiles`,
  `origin_source_tile`) or re-key `source_tile` before the shared scorer
  sees the rows.

The shared attribution is `scripts/lib_advanced_metrics.py`
`scope_detections_to_frame` and `iter_sheet_scopes` (D50). Each detection is
put on its origin sheet, resolved by the longest matching sheet prefix, and
kept only if it intersects one of that sheet's frame tiles, as references
are. A restatement of the old rule differs from it only where a detection
lies outside its sheet's tiles, was re-keyed across a sheet edge, or carries
a sheet name that prefixes another. A restatement of the matcher can differ
wherever detections compete for a mound.

Matching that is not detection-versus-reference scoring was cleared. That
covers consensus clustering, probability inheritance by nearest candidate,
ground-truth deduplication, spacing statistics, and union-to-union
comparison.

## 2. `per_map_counts()`: the fix and what it moves

### 2.1 What it restated

`per_map_counts()` (`scripts/stride55_sweep_oracle.py:123-146` at
`c546f6901`) returns each sheet's (TP, FP, FN) at 50 m. Those counts are
the pairing input of the per-map sign-swap permutation. It kept its own
per-sheet loop. References and the matcher were the library's, but
detections were selected by `gdf_det["source_tile"].str.startswith(m)`
wherever they lay, and origin columns were ignored: the pre-D50 rule. The
F1 that the same scripts report comes from `compute_counts_at_r`, which has
used the shared scope since D50. So the permutation statistic and the
reported F1 could, in principle, describe different detection sets. The old
function also raised on an empty detection frame (an empty column has no
string dtype), which the new tests found.

### 2.2 The fix

`per_map_counts()` now iterates `iter_sheet_scopes(..., ref_map_col=REF_MAP_COL)`,
the loop `compute_counts_at_r` runs, and keeps the shared matcher, the
reference scoping, and the keys (`frame_sheets`). Its per-sheet counts
therefore sum to the engine's totals. Commit `c42ebd06a`, with eight tier-1
tests in `tests/test_stride55_per_map_counts.py` on the two-sheet synthetic
frame of `tests/test_detection_scope.py`:

- out of frame;
- cross-sheet;
- re-keyed with an origin;
- one sheet name prefixing another;
- per-sheet totals equal to `compute_counts_at_r`;
- keys including empty sheets;
- a fully in-frame set keeping its legacy counts;
- a buffer check.

Red sentinel first: against the unfixed function, 6 of the 8 failed (the
buffer check and the legacy-invariant test passed, as they should). With the
fix, the new tests, `tests/test_k_ladder_mcc_instruments.py`, and
`tests/test_detection_scope.py` gave 70 passed.

`load_candidates()` in the same file was not changed. It replaces each
candidate's `source_tile` with the nearest standard tile on the same map and
keeps no origin column. The stride manifests record no member list, and the
re-key cannot leave the sheet, so the attribution is unchanged by
construction. Carrying an `origin_source_tile` column would be principled
but would change the bytes of every GeoJSON its importers materialise (§ 11).

### 2.3 What it feeds, re-run

Each consumer was re-run in two trees on sapphire: OLD (a sparse worktree at
`c546f6901`) and NEW (the branch clone at `c42ebd06a`). A third, the "spy",
ran each consumer in-process with every `per_map_counts` binding replaced.
At every call, the spy computed both the verbatim old function and the fixed
one, recorded the shared scope's diagnostics, and returned the fixed counts.
Outputs were compared with the committed bytes.

| Consumer | Output (last commit) | NEW against committed | OLD against committed | `per_map_counts` call points (spy) |
|---|---|---|---|---|
| `scripts/stride55_sweep_oracle.py` | `results/stride55-2026-08-27/sweep_oracle.json` (`35ed545ef`, 2026-08-27); `*/sweep_50m.csv` (`85ec1e086`, 2026-10-09) | byte-identical | byte-identical | 4: primaries and oracles, A and B |
| `scripts/stride55_ladder.py` (full sweep) | `results/stride55-2026-08-27/ladder.json` (`996937e1a`, 2026-08-27); `*/ladder_sweep_50m.csv` (`85ec1e086`) | byte-identical | not re-run (stopped when the process budget fell to two): the sweep CSVs never touch `per_map_counts`, and the spy measured its P7 call points | 12: N = 10 carried, N = 5 carried, the N = 1, 3, 5, 10 rung oracles, A and B |
| `scripts/stride55_ladder.py --reuse-oracles --pairs-output-dir` | `results/k-ladder-2026-09-12/mcc-test/sign-swap/ladder_pairs.json` and `rebuild/ladder.json` (`d900ed1d5`, 2026-09-12) | byte-identical (NEW and spy runs) | not re-run | the same 12 |
| `scripts/stride55_a5_vs_b5.py` | `results/stride55-2026-08-27/a5_vs_b5.json` (`e51b5738f`, 2026-08-27) | byte-identical (NEW and spy runs) | not re-run | 2: N = 5 carried, A and B |
| `scripts/gemini37_sweep_oracle.py` | `results/gemini37-55map-2026-08-31/sweeps/` (`a73d64346`, 2026-09-01) | `sweep_oracle.json`, `sweep_arm1_50m.csv`, `sweep_arm2_50m.csv` byte-identical; `sweep_fourth_50m.csv` moves 8 rows (§ 10) | the same 8 rows, the file byte-identical to NEW's | 5: incumbents BN5 and BN10, carried arm 1, arm 2, fourth (the same sets as five of the board's) |
| `scripts/gemini37_grid_board.py` | `results/gemini37-55map-2026-08-31/grid-board/grid_board.json`, `pairwise.csv` (`a73d64346`) | byte-identical | byte-identical | 16: the board's cells |

At all 34 measured call points the old and new functions return the same
counts on every sheet. In every one, no detection lies out of frame, none is
attributed by origin (restored or switched), none is unattributed, and the
inputs carry no origin column. The stride and 3.7 manifests record none, and
`load_candidates` and `cluster_first_n` keep each candidate on its own map.
The out-of-frame candidates D50 removes from these universes sit at
`prob_t` 0.00 to 0.05 (the S2 record's stride moves, and § 10), below every
operating point these scripts test.

**No output moves, no verdict changes, and no signature lapses.** The
signed rows `stride55-sweep-oracle-2026-08-27`, `stride55-ladder-2026-08-27`,
`stride55-a5-vs-b5-2026-08-27`, `gemini37-55map-grid-2026-08-31`,
`gemini37-55map-gridboard-2026-08-31`, and `k-ladder-2026-09-12` keep their
numbers. Nothing was regenerated, so no committed output on this branch comes
from sapphire. The byte-identity results rest on independent runs that agree:
OLD and NEW trees, and the NEW chain and the spy. Sapphire has no
error-correcting memory. Its kernel log showed no `Bad page state` report
since boot, before the runs or after them.

## 3. The re-key gap: chains that pass no origin

This is the largest open item, and it is not a copy of the scorer. D50 stopped
re-keying a detection across a sheet edge by restricting the primary-tile
choice to the detection's origin sheet
(`lib_advanced_metrics.assign_primary_tiles_on_origin_sheet`). The origin is
read from the rows' origin columns. A row with no origin keeps the legacy rule,
which picks the nearest tile centroid among ALL frame tiles
(`scripts/prepare_h13_scoring.py:307-318`, docstring of
`assign_primary_tiles`). The chains below build bare cluster centroids, so no
origin reaches that function. A centroid in the overlap of two sheets' padded
tiles can therefore still be booked to the neighbouring sheet and matched
against that sheet's references, which is the § 5.4 defect of
`reports/frames-blast-radius-2026-10-07.md`.

The shared scorer cannot catch these rows, because the re-keyed tile holds the
point, so the row is in frame on the sheet it was given. Every gold-standard
(GS) frame with more than 60 tiles has cross-sheet tile overlap (measured
2026-10-13 by spatial join of each bounds file; pairs of tiles on different
sheets overlapping by more than 1 m²):

| Frame | Tiles | Cross-sheet pairs | Largest overlap |
|---|---|---|---|
| `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` (and `era2_b_intersection_bounds`, `grid_common_bounds`) | 487 | 23 | 2.525 km² |
| `inputs/vectors/bounds/full_evaluation_bounds.geojson` | 340 | 25 | 4.976 km² |
| `inputs/vectors/bounds/256/full_evaluation_bounds.geojson` | 1,032 | 33 | 0.897 km² |
| `inputs/vectors/bounds/384/validation_bounds.geojson` | 240 | 14 | 2.525 km² |
| `inputs/vectors/bounds/384/h10_test_bounds.geojson` | 327 | 10 | 2.524 km² |
| `inputs/vectors/bounds/validation_bounds.geojson` | 60 | 0 | — |
| `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` | 8,541 | 5,143 | 3.688 km² |

| Site | What drops the origin | Feeds (last commit) | Signed, registered, or cited |
|---|---|---|---|
| `scripts/grid_analysis.py:169-184` (`as_gdf`) | The passes are loaded with their `origin_tiles` (`:161`), clustered by `h13_k_sensitivity.cluster_votes` (centroids and votes only), then tiled by `assign_primary_tiles` with no origin (`:183`) | `results/grid-2026-08-18/grid_analysis.json` (`5986316b5`, 2026-10-05), `sweep.csv` and `per_tile_counts.json` (`f31992b7d`, 2026-08-18) | `grid-tilesize-overlap-2026-08-18`, signed 2026-09-12; paper claim R1b-05 (`docs/paper/results-outline.md:340`) |
| `scripts/materialise_grid_unions.py:89-97` | Same path, writing the K = 10 unions the grid verifier scored | `outputs/grid-2026-08-18/verifier/*/union_k10.geojson`, then `scripts/grid_verifier_analysis.py` → `results/grid-2026-08-18/verifier_analysis.json` (`5986316b5`, 2026-10-05), `verifier_sweep.csv` (`8d4ab3fd8`, 2026-08-24), `conditions-verified/` | `grid-postverifier-2026-08-18`, signed 2026-09-12; paper claim R1b-08 (`results-outline.md:343`); the registered verified grid conditions |
| `scripts/stride_plateau_analyses.py:251` (rungs) and `:308-309` (incumbents) | Rungs via `as_gdf`. The four incumbents are rebuilt from bare coordinates, discarding the `source_tile` their own files record | `results/stride-2026-08-25/plateau_analyses.json` (`346694beb`, 2026-08-25) | `stride-plateau-2026-08-25` and `stride-winner-ladder-exact-2026-08-25`, both signed 2026-09-17; paper claims R1b-15 to R1b-18 |
| `scripts/selection_aware_intervals.py:143` (`--cell` path) | Via `as_gdf` | `results/selection-aware/*` (`46e1edc2e`, 2026-08-20) | `results-draft.md:1374` cites `results/selection-aware/findings.md` |
| `scripts/h13_k_sensitivity.py:169-170` (`score`) | Bare centroids tiled with no origin | `results/h13-overlap-2026-08-18/k-sensitivity/k_sensitivity.json` (`0a32ea3ad`, 2026-08-18) | In the signed `h13-overlap-2026-08-18` directory but not in its findings; cited in `docs/methodology/preregistration/protocol-errata.md` |
| `scripts/h13_aggregation_sweep.py:176` (`write_cell`) | Drops the clusters' `source_tiles` | `results/h13-overlap-2026-08-18/tier0-aggregation/` (`dccee3362`, 2026-08-18) | Not cited in the paper. **PI ruling D61 (1) regenerates this file on today's code; today's code still carries this rule.** |
| `scripts/h13_tilesize_overlap_grid.py:221-222` | Inherits `write_cell` | `tilesize-grid/` (`cd3cc9d20`, 2026-08-18) | Not registered or cited |
| `scripts/phase0_3_tilesize_common_footprint.py:161-168, :205` | Dedup arm rebuilds a geometry-only frame | `results/phase0-recall-levers/tilesize-premise/tilesize_premise.json` (`fe7f6d648`, 2026-08-19) | Not registered or cited |
| `scripts/image_b_analysis.py:334-340` | Ladder rungs re-clustered by `cluster_votes`, tiled with no origin | `results/image-b-gs-2026-08-28/` (`8e4331645`, 2026-08-28); `results/modality-bridge-2026-10-07/` (2026-10-07/08) | `image-b-modality-2026-08-28`, signed 2026-09-17 |
| `scripts/modality_bridge_floors.py:648-653` | `load_passes` keeps `origin_tiles` (`:612`); `cluster_votes` drops it | `results/modality-bridge-2026-10-07/floors/` (`3d3cfe18e`, 2026-10-08) | Not registered |

The origins are recoverable: every prepared `detections_dedup.geojson` carries
`origin_tiles`, and the first-N rungs could pass each cluster's members. The
fix is upstream of the scorer (pass `origin=` to `assign_primary_tiles`, or
carry a member list through `cluster_votes`), so it belongs to whoever owns
these chains. `scripts/h13_k_sensitivity.py`'s own decomposition note records
10 of 549 detections changing sheet on a tie-break alone (ΔF1 0.0102), which
shows the size such re-keying can reach on GS frames. Measured tonight for the
plateau incumbents: § 9.3, where it costs 0.007 to 0.017 F1 at 20 m.

## 4. Other live restatements that feed a signed or paper-cited output

| Site | Cat | What it restates | Feeds (last commit) | Signed, registered, or cited | Can it differ today? |
|---|---|---|---|---|---|
| `scripts/measure_miss_correlation_gs.py:68-76, 78-84` | (a) | Detections versus curator mounds through ONE Hungarian across all four GS sheets; the system set is not scoped; the curator set is clipped to the frame's union | `results/working-precision/gs-miss-correlation.json` (`c9c25e273`, 2026-06-11) | Paper: `results-draft.md` § R8 (lines 943-956), claims R8-03 and R8-04 | No, on today's data: per sheet with the shared scope gives the identical table (§ 9.2) |
| `scripts/gs-fp-classify.py:604-606, 640-652` | (a) | TP versus FP by distance to the nearest curator mound (many-to-one; no sheet or frame scope), so a second detection beside a found mound counts as TP-side | `results/gs-fp-classification/*` (`c8f92781c`, 2026-05-29) | Paper exhibit: `results-outline.md:874` | Yes, by design. Its "FP" set is a subset of the scorer's FPs. Re-bucketing needs no model call: the committed classifications hold the distance and category per detection |
| `scripts/stride55_ladder.py:188-203` (`cluster_first_n`) and its copies `scripts/gemini37_arm_ladder.py:124-140`, `reports/w27-replicate-floors-2026-10-06-scripts/w27_55map_subset_replicates.py:214-231` | (e) | Each rung cluster takes ONE origin, the nearest pooled detection's first member tile, and drops the other members | Stride ladder, A5 versus B5, `ladder_pairs.json`, the 3.7 arm ladder and grid board, W2.7 § 6 | Signed: `stride55-ladder-2026-08-27`, `stride55-a5-vs-b5-2026-08-27`, `gemini37-55map-grid-2026-08-31`, `gemini37-55map-gridboard-2026-08-31`, `k-ladder-2026-09-12`; paper § R7.2, § R7.3 | Only for a cluster seen on two sheets, named on one, and lying outside that sheet's tiles: such a row is dropped where its members would switch it. Measured at every `per_map_counts` call point: no such row at any of them (§ 9.1) |
| `scripts/final_board_sweeps.py:248-271` (`load_manifest_probs`) and the cells `materialise()` writes; also `scripts/score_min11_uplift.py:94-107`, `scripts/materialise_pairing_twin.py:164-182`, `scripts/stride55_score.py:90-160` (`materialise_primary`), `scripts/register_pass1_materialise.py:124-133`, `scripts/final_board_n3_carried.py:106-125`, `scripts/final_board_posthoc_cells.py:529, 560`, `scripts/run_generalisation.py:864`, `scripts/55maps-t0.3-rebuild-verified-geojson.py:112`, `scripts/materialise_second_wave_sets.py:84-86` | (e) | 55-map readers and materialisers that keep one `source_tile` and drop `properties.source_tiles` | Both 55-map final boards, their cells, the verifier-pairing twins, the stride primaries | Signed: `55map-final-board-2026-08-27`, `55map-final-board-r2-2026-09-06`, `verifier-uplift-pairing`; registered 55-map conditions; paper § R7 | Unlikely. Rows whose members span two sheets, per tracked 55-map manifest (counted 2026-10-13): 1 of 8,942, 1 of 7,878, 1 of 9,205, 1 of 9,910, 1 of 10,170, 4 of 16,482 (uplift 3-of-10), and 2, 1, and 0 in the three vote-3 increments; no row's `source_tile` lies off its own members. The stride and 3.7 manifests record no member list at all |
| `scripts/analyse_dawid_skene.py:192-211` | (e) | Keeps one `source_tile`, drops `source_tiles`, then scores through `iter_sheet_scopes` | `results/55maps-*/dawid-skene-standardised/` (2026-08-14) and older | Paper: `methods-draft.md:265-269` (Dawid-Skene converges within 0.004 F1) | Origin drop unlikely (one two-sheet cluster per 55-map manifest). The outputs predate D50, so the out-of-frame rule may move them |
| `scripts/analyse_diversity.py:233-300` (its own `consensus_to_gdf`) | (e) | First-intersecting tile by spatial join; `source_tiles` dropped | `results/phase3c-diversity/` (2026-03-26 to 2026-06-05) | Claims inventory R3-07 (`results-claims-inventory-2026-09-12.md:455`) | Likely, small: 340-tile frame with cross-sheet overlap |
| `scripts/analyse_flash35_2x2.py:135, 207-216` | (e) | Scored frame carries geometry and `source_tile` only; bare rows take the first member | `results/flash35-2x2/analysis-full.json` (`f04063513`, 2026-06-11) | `flash35-model-roles` (unsigned); paper `results-draft.md:470-474` | Unlikely |
| `scripts/run_h2_pilot.py:194-245, 430-439`; inherited by `scripts/run_experiment_e.py` | (a) | Greedy one-to-one matcher; no sheet split; references scoped to the tiles that produced a detection, so a mound in a tile with no detection drops out of the recall denominator | `results/phase3d-pilot-results.md` (2026-03-09) | `docs/paper/discussion-seeds.md:501` (text 0.796 against image 0.711) | Likely (the reference scope), on the 60-tile frame that has no cross-sheet overlap |
| `scripts/test_gtfree_selection.py:86, 130` | (e), inherited | `pairwise_permutation_test.assign_source_tiles` (owned elsewhere) | `results/gtfree-selection/*` (2026-06-13) | `discussion-seeds.md:91` | Unlikely |

## 5. Live restatements, not registered and not cited

| Site | Cat | Note |
|---|---|---|
| `scripts/lib_consensus.py:336-342` (`generate_consensus_gdf`), `:425-437` (`build_pv_gdf`) | (e) | Shared builders shaped like `consensus_to_gdf`: sorted-first member or the manifest's `source_tile`, member list dropped. Callers: `scripts/compute-pairwise-effect-sizes.py` (→ `results/pv/pairwise-effects/`, `results/d42-retest-2026-10-05/class-b/`, 2026-10-06) and `scripts/consensus-sweep-phase3a-high-text.py`. The D60 (3) route fix should cover these too, or name them |
| `scripts/dedup_metric_impact.py:447, 462` and its private tile confusion at `:302` (gated against the library on the first pass only, `:600`); `scripts/dedup_tiering_rerun.py:133, 457-460` | (e), (d) | `results/dedup-metric-impact-2026-08-18/` (2026-08-18) |
| `scripts/analyse_consensus_sd_shrinkage_v2.py:404, 411`; `scripts/compare_wbf_greedy_all_conditions.py:402-418` | (e) | `source_tiles[0]`; can differ only where a row would be switched (`n_origin_switched`) |
| `scripts/analyse_subtype_classification.py:346, 359-360, 442` | (b) | Sheet from the first member, no frame scope; references not tile-scoped (`del gdf_bounds`, `:1099`), so out-of-frame curator mounds count as unmatched in the 5 × 5 matrix. `results/gold-standard-subtype-classification/`, `results/paper-tables/subtype-classification.*` |
| `scripts/student_perstudent_gs4.py:100-115, 203, 215` | (a), own scope | Scores inside audit polygon ∩ footprint by `within` on both sides, by design |
| `scripts/student_ranking_significance.py:73-86` | (e) | Replaces every contender's tile with the nearest footprint tile; the tile universe is restricted to the zone's own sheet (`:120-128`), so no row can cross a sheet. `results/student-baseline-2026-09-01/per-student-gs4/significance.json` (2026-09-01) |
| `scripts/scoring_sensitivity_probe.py:249, 401-405` | (e) | `results/scoring-sensitivity-2026-08-18/` describes the retired rule |
| `scripts/compare_tile_sizes.py:118, 204-262, 414` | (a), (b), (e) | Own per-sheet loop: a detection in a cross-sheet overlap counts on both sheets. `results/pairwise/tile-size-mcnemar-30m/` (2026-03-28), superseded era |
| `reports/w27-replicate-floors-2026-10-06-scripts/` outside `floors-v2/`: `w27_55map_subset_replicates.py` (above, and `load_upl_frame` `:258-273`), `w27_gs_consensus_floors.py:130-131`, `vdate_check.py`, `vdate_extra.py`, `vdate_ident.py`, `runA/runA_score.py` | (e) | W2.7 § 2, § 3, § 4, § 6, § 6a, § 6c; every output committed 2026-10-05 to 2026-10-07, before D50 merged. The W2.7 rebuild agent owns these; listed so the regeneration covers them |

## 6. Dead, one-off, or diagnostic

`scripts/verify_h13_overlap.py:151-170` (own `linear_sum_assignment`, first
intersecting tile; a gate that writes nothing), `scripts/diagnose_100m_buffer.py:71, 114`,
`scripts/export_qgis_sanity_check.py:142-180, 258` (outputs only under
`archive/`), `scripts/6_accuracy_report.py:208-224` (outputs only under
`archive/`), `scripts/verify_phase2a_metrics.py:523-599` (stdout),
`scripts/evaluate_pilot.py:112-113`, `scripts/compute_session78_calibration_matrix.py:134-149`
(labels for AUC, Brier, and ECE, not F1), `scripts/analyse_tp_localisation_55maps_vs_gs.py:323-325`,
`scripts/analyse_inter_pass_agreement.py:628-644`,
`scripts/validate_first5_of10_derivation.py:128-130`, `scripts/discover_hard_cases.py:318-320`,
`scripts/review_candidates.py:429` (sets a review queue, not a score),
`results/verifier-calibration-matrix-pairwise/scripts/run_pairwise_matrix.py:224-300`
(private percentile bootstrap over the library's per-tile counts; outputs
2026-04-25), and the D42 wrappers under `reports/d42-implementation-2026-10-05-scripts/`
(inherit `scripts/compare-384-vs-512.py` and `scripts/compute-pairwise-effect-sizes.py`).

## 7. Deliberate replicas of the old rule

Expected, not defects: `reports/frames-blast-radius-2026-10-07-scripts/blast_lib.py:132-223`
(the D50 blast-radius measurement; it would give different numbers if re-run
at today's library), `reports/retest-bootstrap-check-2026-10-05-scripts/w21_reproduce.py`
and `w23_score.py` `score_old` (historical replays), and
`reports/d51-ladder-provenance-2026-10-08-scripts/clip_cost.py:78-112`, a
private loop built from `iter_sheet_scopes` and the shared matcher that raises
if its counts disagree with `calculate_f1_internal` (`:129-132`).

## 8. Owned elsewhere tonight, and the library itself

- **Owned by other agents (not analysed):** `scripts/analyse_consensus_sweep.py`
  `consensus_to_gdf` and the loaders in `scripts/pairwise_permutation_test.py`
  (D60 (3)); `reports/w27-replicate-floors-2026-10-06-scripts/floors-v2/`
  `FastScorer` (D60 (4)). Files that only import those are marked "inherited".
  One note for the pairwise-loader owner, from the inventory: its
  `assign_source_tiles` and `scripts/compare_tile_sizes.py:118` call
  `drop_duplicates` on geometry, so two distinct detections at identical
  coordinates can collapse into one when tiles are filled.
- **The library's own bare prefix:** `scripts/lib_advanced_metrics.py:1702`
  selects a sheet's bounds by `tile_name.str.startswith(sheet)` for the
  reference side of `iter_sheet_scopes`. The detection side resolves sheets
  longest-first. No tiled frame under `inputs/vectors/bounds/` has a sheet
  name that prefixes another (all 11 files with a `tile_name` checked
  2026-10-13), so this is harmless today and is recorded only.

## 9. Measurements

All on sapphire, 2026-10-12, with the scripts and records in
`reports/s163-agent-records/scorer-restatement-inventory-scripts/`:
`chain.sh` (the consumer lanes of § 2.3), `spy_run.py` driven by
`spy-chain.sh` (the call-point spy), `measure_misc.py` (§ 9.2 and § 9.3), and
`out/` (the spy records and the measurement JSON). § 9.2 and
§ 9.3 were run twice, and the two outputs were byte-identical. § 9.1's
records are corroborated by the independent OLD and NEW consumer runs
(§ 2.3).

### 9.1 `per_map_counts` at every call point

34 call points. The spy measured 16 in the grid board, 12 in the
ladder, 2 in A5 versus B5, and 4 in the sweep; the Gemini 3.7 sweep's 5 are
the same detection sets as five of the board's. At every one, the old and new
functions agree on every sheet, and the shared scope reports 0 out of frame,
0 origin-restored, 0 origin-switched, and 0 unattributed (`out/spy-*.json`).
Section 2.3 gives the consequences.

### 9.2 GS miss correlation, global against per sheet

`measure_misc.py` recomputed the 2 × 2 found/miss table of
`scripts/measure_miss_correlation_gs.py` both ways. The committed global rule
is reproduced exactly: at 20 m, 361 both found, 54 students only, 16 system
only, 4 both missed, ratio 1.5; at 30 m and at 50 m, 367 / 48 / 16 / 4, ratio
1.67. Per sheet, with the system set scoped by the shared rule, the numbers
are identical at all three radii: no mound's flag changes for the system or
for the students. All 412 system detections are in scope on their own sheet.
**The restatement cannot move claims R8-03 or R8-04 on today's data.** It
remains a global matcher that could differ on another detection set.

### 9.3 Plateau incumbents: the re-key costs 0.007 to 0.017 F1

`scripts/stride_plateau_analyses.py` rebuilds each of its four incumbents from
bare coordinates through `as_gdf`. Re-scoring those rebuilt sets reproduces
the committed board's F1 exactly (`board_13cell.f1` in
`results/stride-2026-08-25/plateau_analyses.json`). Scoring the same files
with their own recorded `source_tile` through the shared scorer, on the same
carrier at 20 m, gives:

| Incumbent | Rows on the carrier | Rows `as_gdf` puts on another sheet | F1 @ 20 m committed (`as_gdf`) | F1 @ 20 m on the recorded sheet | Difference |
|---|---|---|---|---|---|
| `opmax` | 418 of 423 | 7 | 0.8842 | 0.8960 | +0.0118 |
| `headline` | 407 of 412 | 5 | 0.8838 | 0.8910 | +0.0072 |
| `min11` | 384 of 389 | 7 | 0.8719 | 0.8842 | +0.0123 |
| `min6` | 407 of 412 | 10 | 0.8623 | 0.8790 | +0.0168 |

The five rows each set loses are off the carrier under both rules. Their
recorded attribution keeps every carrier row on the sheet that holds it (0
out of frame across sheets). The difference is therefore the § 5.4 mechanism
of `reports/frames-blast-radius-2026-10-07.md`: a detection moved to the
neighbouring sheet's overlapping tile cannot match its own sheet's mound, so
one TP becomes an FP and an FN. **This is a surprising, material result for
a signed, paper-cited analysis** (`stride-plateau-2026-08-25`, claims R1b-15
to R1b-18). It was not corrected here. The board's other nine cells (grid and
stride K = 10 unions) are built by the same origin-less path and were not
measured: their unions record no members, and recovering origins needs the
passes. So the board's ranking and its "6 of 78 pairs significant" may move
either way.

## 10. Side findings (not restatements)

- **The Gemini 3.7 fourth-cell sweep moves under today's scorer.**
  `results/gemini37-55map-2026-08-31/sweeps/sweep_fourth_50m.csv`, committed
  `a73d64346` (2026-09-01, before D50), gains 8 changed rows when
  `scripts/gemini37_sweep_oracle.py` is re-run. They are `prob_t` 0.0 at
  k = 1 to 8, with FP falling as D50 drops out-of-frame candidates. OLD and
  NEW produce byte-identical files, so this is D50, not this fix:

  | k | FP before → after | F1 before → after |
  |---|---|---|
  | 1 | 52,594 → 50,402 | 0.1561 → 0.1617 |
  | 2 | 30,041 → 29,935 | 0.2412 → 0.2419 |
  | 3 | 23,914 → 23,843 | 0.2826 → 0.2832 |
  | 4 | 20,338 → 20,293 | 0.3142 → 0.3146 |
  | 5 | 17,873 → 17,852 | 0.3403 → 0.3406 |
  | 6 | 15,834 → 15,823 | 0.3651 → 0.3652 |
  | 7 | 14,079 → 14,075 | 0.3880 → 0.3880 |
  | 8 | 12,562 → 12,561 | 0.4113 → 0.4113 |

  No carried or oracle point moves: `sweep_oracle.json` is byte-identical.
  The file was not regenerated here, because its generator is not
  `stride55_sweep_oracle.py` and the change is not this fix. The moved file is
  kept at `~/scratch/scorer-restatement-sweep-2026-10-12/out/laneA-new/`.
- **Outputs last written before D50 and never re-scored under it** (from the
  inventory, not re-run here):
  - the 3.7 arm ladder and fourth-cell ladder (2026-08-31 and 2026-09-01);
  - the r1 and r2 final-board sweeps and cell evaluations (2026-08-27 to
    2026-09-20) and `final_board_50m.json` (2026-10-05);
  - the Dawid-Skene standardised runs (2026-08-14);
  - every W2.7 table (2026-10-05 to 2026-10-07).

  Their replication gates compare against pre-D50 primaries.
- **`scripts/build_tiered_leaderboard.py` serves its cache unless `--force` is
  passed** (`:782`, `:1374`, `:1430`). The cache is not keyed to the scorer.
  On amd-tower, `results/leaderboard/era{1,2,3}/.cache/` holds 4,669 untracked
  files, none modified after 2026-10-07, so a re-run without `--force` returns
  pre-D50 numbers.
- **`results/uplift-supplement/verifier-uplift.csv`** (signed
  `verifier-uplift-pairing`; last commit `d23596c78`, 2026-09-12) is older than
  the uplift cells re-scored under D50 on 2026-10-09 (`c2eb1e6bc`).
- **Stale docstrings** describe the pre-D50 prefix rule:
  `scripts/materialise_pairing_twin.py:4-7`, and
  `scripts/build_verifier_pairing_worklist.py:1153` and `:1559`.

## 11. For the PI

1. **The re-key gap (§ 3, measured in § 9.3).** Decide whether Phase 5's
   sweep extends to the chains that tile bare centroids with no origin. The
   fix would pass `origin=` to `assign_primary_tiles`, or carry each
   cluster's members through `cluster_votes`, then re-score. It reaches
   signed, paper-cited outputs (claims R1b-05, R1b-08, R1b-15 to R1b-18, the
   Image-B board). Note that D61 (1)'s regeneration of the tier-0 sweep runs
   today's code, which still carries this rule.
2. **`lib_consensus.generate_consensus_gdf` and `build_pv_gdf`** drop member
   lists exactly as `consensus_to_gdf` does. Hand them to the D60 (3)
   consensus-route work, or name them as a follow-up.
3. **W2.7's non-floor scripts** (§ 5) are pre-D50 vintage and drop or re-key
   origins. They belong with the D60 (4) regeneration of § 6 and § 6b.
4. **`gs-fp-classify.py`'s FP definition** (beyond the threshold from every
   curator mound) differs from the scorer's FP by design. Decide whether the
   exhibit at `results-outline.md:874` needs to say so.
5. **`stride55_sweep_oracle.load_candidates`** keeps no origin column. That
   is harmless today and was left unchanged, because carrying one would
   change the bytes of every GeoJSON its importers materialise. Say if the
   principle should win.

## Changelog

### 2026-10-13 — Original publication

First version: the inventory of scorer restatements across `scripts/`,
`reports/*-scripts/`, and `results/` at `c546f6901`; the `per_map_counts()`
fix (`c42ebd06a`) and its re-runs; and the measurements in § 9. No number in
any committed output changed.
