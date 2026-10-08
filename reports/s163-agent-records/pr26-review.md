# Review of PR #26: D50 detection scope and D51 same-area gate

> **Last revised**: 2026-10-08 (original publication). See [§ Changelog](#changelog)
> for revision history.

The review below is recorded as returned to the main session. The text from the
reviewer's metadata to the end of "What I could not check" is unchanged; this note,
the banner and the changelog are additions. The fixes were applied on branch
`scorer-frames-d50-d51` on 2026-10-08 by a subagent of the main session (Claude,
Opus 5.5). Each finding was re-verified at source before it was fixed, and each
held. No model call was made.

| Finding | Applied | How |
|---|---|---|
| 1. Both D51 options pass different areas unclipped | `16a49438f` | With `--clip-to-common-area` and `--allow-undetermined-area`, a mismatch among the determined rungs now clips **every** rung, undetermined ones included, to the area common to the determined rungs, and keeps the frame's reference set. The status is `clipped-to-common-area-with-undetermined`, and the record names the undetermined rungs. With no rung determined, or with the determined rungs agreeing, behaviour is unchanged: the nine undetermined ladders stay `undetermined`, unclipped. Of the review's two remedies, clipping was chosen over refusing, because report § 6 Q2 and Q3 can be answered together. |
| Recommended direct test (M7) | `ef37504a3` | `test_a_clip_never_removes_references` calls `rescore_clipped_evaluation` directly. It is red under M7. |
| 2. `parse_tile_list` never fails loudly | `b904ff936` | `None`, NaN, `pd.NA` and `pd.NaT` count as missing, so the search moves on to the next column, and missing list elements are dropped. Other types raise `TypeError`. A `[`-string that is neither JSON nor holds a quoted name, and a JSON list of non-names, raise `ValueError`. Errors name the column and the row. Old and new parsers agree on all 110,334 checks: every distinct origin and `source_tile` value in the 2,043 tracked GeoJSON files that carry an origin column, each in every form geopandas can return. The six values the review recomputed are unchanged. |
| 3. Tier E regeneration privileges the first member | `fd50cd133` | The review's first remedy, applied row by row: `reassign_carrier_tiles` writes `origin_source_tile` only for a row whose member list records nothing. The committed tier E cells, rebuilt as the materialiser writes them and passed through the fixed function, read 0.8680 / 0.8979 / 0.9046. |
| 4. Registry conflict on merge | `7a7a40e36` | `origin/main` was merged at `e29baf0f5`, by then 50 commits ahead (the review saw 38). The one conflict, the registry, was rebuilt with `scripts/build_generated_file_registry.py`; `--check` and `--strict` pass. The code `main` changed after the review imports nothing the branch changed. |
| 5. Informational | report changelog | The § 5.2 wording now says which count it gives: 696 cells by the largest of the F1, precision and recall changes, 629 by F1@20 alone. The other items need no change before merging and were not changed. |

The red sentinels are as follows. For finding 1, restoring the old branch order, the
old `run_area_gate` check or the old builder check each turns the new tests red; the
builder tests were mutated in place, because the builder reads `outputs/`. For finding
2, 13 of the 16 new cases fail on the old parser. For finding 3, restoring the old
copy turns the new test red.

**Residual, found while fixing finding 3, not changed.** In a materialised cell that
is not re-keyed, the scorer keeps a `source_tile` that names one of the detection's
origin sheets. `materialise_pv_geojson.py` writes the first, alphabetical, member
there. A cluster seen on two sheets but lying only in the second sheet's frame tiles
is therefore still dropped as out of frame for such a cell, as a synthetic probe
confirms. This behaviour predates the branch, and how often it occurs in committed
cells was not measured.

**Remaining:** the full tier-1 suite on the merged head, to be run on sapphire.

- **Reviewer lane:** Claude, Opus 5.5, read-only subagent
- **Date:** 2026-10-08
- **Repository:** `saross/map-reader-llm`
- **Pull request:** #26, branch `scorer-frames-d50-d51`, "feat(metrics): D50 detection scope and D51 same-area gate"
- **Commit reviewed:** `981f39afe` (10 commits ahead of `main`, 38 behind; merge base `d76be2814`; `origin/main` at `7e0ee2757`)

Nothing was edited, committed, pushed, or posted. Probes and mutation runs were done in a
scratch directory (`.../scratchpad/review_probes/`, plus a `git archive` copy with no
symlinks). No model API calls were made.

## Verdict: MERGE AFTER FIXES

D50 (Ruling D50) is implemented correctly and reproduces the report's numbers wherever I
checked. Origin restoration works the same way in both directions: I built a case where it
lowers F1, and the code handled it. The report's "707 cells, all upward" result comes from
the data, not from a bug that can only add matches. D51 (Ruling D51) has one real gap.
When `--clip-to-common-area` and `--allow-undetermined-area` are both set, a ladder whose
determined rungs searched different areas passes as "undetermined" and nothing is clipped.
These are the two options § 6 of the report puts to the Principal Investigator (PI) for
the four refused `pv-diag-384` ladders and the nine undetermined ones. Fix finding 1
before either option is used. Findings 2 and 3 are small hardenings. The merge itself has
one conflict, in a generated file that needs rebuilding.

## Findings, ranked by severity

### 1. Medium-high: with both flags set, the D51 gate passes rungs of different areas and never clips them

- **Where:** `scripts/lib_assessed_area.py:810-840`. When `mismatch` is true,
  `clip_to_common` is true, and any pool is undetermined, the `if undetermined:` branch
  (826) runs instead of `elif mismatch:` (834). No `clip` block is written and the status
  is `undetermined`. `run_area_gate` writes the common-area GeoJSON only when the status
  is `STATUS_CLIPPED` (961-963), and so does the builder (`build_k_ladder_phase2_tables.py:782`).
  The drivers read `record.get("clip_geojson")`, which is `None`
  (`derive_g37_gs_opmax_rungs.py:194`, `run_k_ladder_tier_e.py:1092`,
  `score_k_ladder_phase2_rungs.py:411`, `:470`), so they sweep and materialise unclipped.
- **Failure scenario:** in `out/ladders_new.json` → `phase2_gate_survey`, all four refused
  `pv-diag-384` ladders have K = 1 and K = 3 determined but different (+2.08 to +4.76 km²),
  and K = 5 and K = 10 undetermined. Suppose the PI answers § 6 Q2 "clip" and Q3 "allow
  undetermined" (report lines 457-463), and the builder runs with both flags. The
  ladders then publish unclipped with status `undetermined`. The K = 1 rung still books
  the 3 and 2 reference mounds in its missed tiles as false negatives. Nothing refuses
  and nothing records a clip. The record keeps only `max_excess_km2`.
- **Reproduced:** in `d51_probe.py`, two determined areas of 2 km² and 1 km² plus one
  undetermined pool, with both flags, give `status undetermined`, `max_excess 1.0`, and no
  `clip` key.
- **Fix:** clip the determined pools even when some pools are undetermined. Record both
  facts, for example status `undetermined` with a `clip` block, and have `run_area_gate`
  and the builder clip whenever a clip block exists. The alternative is to refuse this
  combination. Add a tier-1 test for it.

### 2. Medium-low: `parse_tile_list` never fails loudly, and some values are dropped or mask other columns without notice

- **Where:** `scripts/lib_advanced_metrics.py:1141-1204`, used by the origin loop at
  1463-1469, where the first column that yields any name wins.
- **What it does with unexpected values** (`test_pr26_probes.py`):
  - A set, a dict, or an int becomes one bogus name. It is counted as
    `n_origin_unrecognised`, and `source_tile` decides.
  - A string starting with `[` that is neither JSON nor quoted (for example
    `"[A_x0.png, B_x0.png]"`) becomes `[]` with no counter. The origin is ignored without
    any trace.
  - `pd.NA` becomes `['<NA>']`. That counts as a parsed value, so a later origin column
    (`source_tiles`) is never consulted. The probe gives `n_origin_unrecognised 1` where a
    restoration was due.
  - A `NaN` element inside a list becomes the name `'nan'`.
- **Scope:** none of these serialisations occurs in the corpus the report measured. All
  the forms it names are handled and tested: list, ndarray, JSON, the NumPy-repr string,
  the repr wrapped in a one-element array, `;`-joined, and bare. This is hardening, not
  a wrong number.
- **Fix:** treat `pd.isna` scalars as missing. Raise `TypeError` on unsupported container
  types and `ValueError` on a `[`-string that yields no tokens. Add these cases to
  `test_parse_tile_list_reads_every_serialisation`.

### 3. Low (latent): regenerating tier E brings back the rejected "first member" rule

- **Where:** `scripts/materialise_pv_geojson.py:221` promotes `source_tiles[0]`, which is
  the alphabetically first member (`merge_passes.py:254`, `:350` sort the list). Then
  `run_k_ladder_tier_e.py:1021-1022` copies it into `origin_source_tile`.
  `ORIGIN_TILE_COLUMNS` (`lib_advanced_metrics.py:1131-1135`) consults `origin_source_tile`
  first, both at assignment (`origin_tiles_of`) and at scoring. A regenerated tier E cell
  is therefore attributed to one member's sheet, not to every sheet it was seen on.
  That is the rule § 7 item 1 rejected.
- **Failure scenario:** a cluster seen on sheets A and B, lying only in B's frame tiles,
  with A sorting first. `reassign_carrier_tiles` gives it `source_tile = None`, and the
  scope then drops it as out of frame. Under the measured rule it would be kept on B.
- **Measured impact today: none.** `tier_e_regen_probe.py` emulates regeneration for the
  committed K = 1, 3, and 5 cells. They contain no two-sheet clusters, and F1@20 m is
  0.8680, 0.8979, and 0.9046 both as committed and as regenerated.
- **Fix:** do not write `origin_source_tile` when `source_tiles` is present. Or make the
  scope take the union of all origin columns instead of the first non-empty one.

### 4. Low: merge conflict in the generated-file registry

`git merge-tree origin/main 981f39afe` finds exactly one conflict:
`reports/verification/generated-file-registry.json`. Both sides regenerated it. Rebuild it
after the merge with `scripts/build_generated_file_registry.py`, and do not take either
side as it stands. Otherwise
`tests/test_build_generated_file_registry.py::test_committed_registry_matches_a_rebuild`
fails.

### 5. Informational and nits (no change required to merge)

- **The per-tile `id` join books a restored detection to the re-keyed tile.** A
  restoration moves the detection to sheet A for matching, but `_book` still credits the
  TP (true positive) to `det_row["source_tile"]`, which is B's overlap tile
  (`lib_advanced_metrics.py:1967`, `:1986`, `:1995`; probe output shows TP on
  `B_x0_y0.png`). The point lies inside that tile, so tile resampling stays geometrically
  sound. The report's tables do not cover this.
- **A null-`source_tile` row with a recorded origin, inside the frame, now makes the
  per-tile table refuse under the default `id` join.** F1 scores the row, but `_book`
  credits it to no tile, which gives a `TileJoinRefusalError` shortfall (probe). Before
  D50 the row was unattributed and skipped. No such row exists in the corpus: tier E's
  23 or 21 per cell are out of frame on both the board and the 487-tile frame
  (`origin_only_probe.py`). Two further edges: an input with origin columns but no
  `source_tile` column passes `calculate_f1_internal` but raises `KeyError` in
  `compute_per_tile_tp_fp_fn` (`det_row["source_tile"]`). The evaluator always
  synthesises `source_tile`, so this cannot happen in the evaluator.
- **`analyse_55maps_heterogeneity.count_per_map`** (`:248`, called at `:274-276` with one
  sheet's tiles as the frame) cannot restore an origin on a neighbouring sheet, because
  that sheet is not in the frame. Its docstring says the count is "the one
  `calculate_f1_internal` matches", which does not hold for re-keyed rows. It is a
  reporting count, and 55-map cells carry no re-key.
- **Report wording, § 5.2 line 292.** "Cells moving by ≥ 0.001 at 20 m … 696" uses
  max(|ΔF1|, |ΔP|, |ΔR|) (`origin_restored_analysis.py`). By F1@20 alone the count is 629
  (`moved_new.csv`). The smallest F1 rise among the 696 is +0.00016. "All upward" holds for
  F1@20 (696 up, 0 down) and F1@50 (684 up, 0 down, 23 n/a).
- **The D51 area is the union of the passes' processed tiles**
  (`lib_assessed_area.py:360-415`). At a vote threshold above 1, a tile one pass missed
  is searched less thoroughly, and the gate cannot see that. This matches the ruling,
  which is about candidate pools, but it is worth stating as a limit.
- **Paths in records.** `materialise_grid_unions.py` writes `clip_bounds` and `passes`
  from `args.scoring_dir`, which may be absolute. The record then depends on the machine
  it was written on.

## On the "707 all upward" question (check 2)

- **The code is symmetric.** Attribution never looks at references.
  `test_restoration_can_lower_f1` places a detection seen only on A, re-keyed to B, with
  the nearby reference on Map B. F1 falls from 1.0 without the origin to 0.5 with it. A
  restoration can also drop an in-frame TP: if the origin sheet's frame tiles do not hold
  the point, it is out of frame for its own sheet (`test_restoration_can_drop_an_in_frame_tp`).
  That is D50 parity with references, but it moves F1 down, not up.
- **Upward-only is a property of the data.** In the three cells I recomputed, every
  restored detection with a reference within 20 m had that reference on its origin
  sheet (9.3 m and 4.9 m on Elenovo). Restored false positives had their nearest
  reference more than 1.2 km away, so moving them changes nothing. This is the expected
  geometry. A padded tile beyond a sheet's neat line shows that sheet's collar, not the
  neighbour's map content, so a mound seen only on A is digitised with Map A. A
  misregistered sheet edge, or a mound digitised on both sheets, could reverse the
  direction. "What the mechanism predicts" (report line 306) is a domain expectation,
  not a guarantee from the code.

## What I verified, and how

1. **The D50 scorer, by reading** `scope_detections_to_frame`, `iter_sheet_scopes`,
   `parse_tile_list`, `assign_primary_tiles_on_origin_sheet`, `compute_per_tile_tp_fp_fn`,
   the two tile-confusion entry points, `evaluate_detections.describe_detection_scope`,
   and the call sites the PR rewrote.
   - Detections are scoped by the same `intersects` predicate on the same per-sheet tiles
     as references.
   - Rows are kept in input order, positionally (non-unique index safe).
   - Cells with nothing out of frame and nothing re-keyed reach the matcher unchanged.
     The code from `4fd64e8a8` (measurement head) to `981f39afe` differs only in a
     comment.
2. **Recomputing moved cells from committed detections with the branch scorer**
   (`moved_cell_probe.py`):

   | Cell | F1@20 m | F1@50 m | Matches `moved_new.csv`? |
   |---|---:|---:|---|
   | `flash-high-text-n5__text-t0.7__consensus__t26` (registered) | 0.816471 | 0.828235 | yes (0.81647 / 0.82824) |
   | `gs-v2-consensus-5of5` | 0.767251 | 0.783626 | yes |
   | `h11 consensus-384-UNINTENDED-T1.0 eval-t1` | 0.305181 | 0.315117 | yes |
   | Tier E K = 1 | 0.8680 | — | yes |
   | Tier E K = 3 | 0.8979 | — | yes |
   | Tier E K = 5 | 0.9046 | — | yes |

   The tier E values also match report § 5.4 (D50 column).
3. **Rerunning the D51 gate for the 3.7 GS ladder** (`d51_probe.py`): frame 1,402.4067 km²,
   common area 1,364.4713 km², excess 37.9354 km². The K = 1 opmax cell clipped reads F1
   0.8682 with 468 detections and 34 removed, the same as `ladders_new.json` and § 5.3.
4. **Spot-checking the report against its committed outputs:**
   - `summary_new.json` classes: 1,950 / 707 / 70 / 24 / 49; 762 moved; 68 registered.
   - `origin_restored_analysis.json`: 696 / 696 up / 0 down, median +0.00175, largest
     +0.02447, 50 cells ≥ 0.01, 680 synthesised, origin columns 690 / 6, 10 cells
     differing under first-origin.
   - `ladders_new.json` gate survey: 5 refused, 9 undetermined, all areas as in § 5.6.
   - `sweeps_new.json`: out-of-frame counts of 38, 45, 96, 125, and 148.
5. **Tests.** I ran 52 tier-1 modules that import the changed code, in my detached
   worktree with the project `.venv`: 1,004 passed, 1 skipped, 2 xfailed, 0 failed. The
   new modules include the two ladder-builder wiring tests. `ruff check` passes on the
   changed scripts and tests.
6. **Mutation sentinels on a real `git archive` copy** (0 symlinks; `mutate.py`). Counts
   exclude the two ladder-builder tests, which cannot import without the full `outputs/`
   tree. In the copy they are red in the control too, and the PR's own sentinel deselects
   them.

   | Mutation | Tests turned red | Bites? |
   |---|---:|---|
   | M1: origin restoration disabled | 5 | yes |
   | M2: NumPy-repr parsing disabled | 3 | yes |
   | M3: first member privileged | 1 | yes (`test_a_cluster_seen_on_both_sheets…`) |
   | M5: tile confusion drops unattributed rows | 1 | yes |
   | M6: pass area from the manifest instead of `processed_tiles` | 1 | yes |
   | M8: tolerance ×10⁴ | 6 | yes |
   | M4: per-tile booking reads unscoped rows | 0 | equivalent mutant: matching reads `scope.detections` anyway |
   | M7: clip also clips references (D51 "keep the frame's reference set") | 0 in the copy | see below |

   M7 is pinned only by `test_the_ladder_builder_refuses_and_clips` (recall 0.5), which
   needs the full data tree. A 20-line test that calls `rescore_clipped_evaluation`
   directly (`test_clip_keeps_refs.py`) turns red under M7. Worth adding to the suite.
7. **Merge risk with `main`** (check 5).
   - **Conflicts:** `git merge-tree` reports one, the registry (finding 4).
   - **Overlapping files:** none in `scripts/` or `tests/`. Main changed
     `modality_bridge_floors.py` (new), `modality_bridge_stage2_checks.py`,
     `verifier_dryrun_harness.py`, three Run B shell scripts, and four test modules.
     `modality_bridge_union.py` has not changed on `main` since the branch point, so § 4.4's
     byte-for-byte union validation still applies.
   - **Floors subset rungs will not move.** `load_passes`
     (`modality_bridge_floors.py:591-615`) reads only centroid, label, `origin_tiles`, and
     `cluster_size` from `detections_dedup.geojson`. Rebuilt dedup files change only
     `source_tile`, which it never reads. `build_rung` (`:632-655`) assigns carriers to
     bare centroids, so the branch's `assign_primary_tiles` falls back to its legacy rule.
     Scoring goes through `per_tile_counts` → `compute_per_tile_tp_fp_fn` with
     `source_tile`-only attribution, and each carrier tile contains its point. Two
     measurements back this:
     - `reassign_probe.py`: the branch's `assign_primary_tiles` reproduces the stored
       `source_tile` of all four anchor unions (3,319 + 4,065 + 791 + 674 points, 0
       mismatches). The `reassign_gate` in the six-cell gate and in `image_b_analysis`
       therefore still passes.
     - `runb_scope_probe.py`: the D50 scope fires on 0 of main's 24 committed Run B
       verified sets, so floors gates 2 and 3 reproduce.
   - **Tests on `main`:** the new floors tests import only pure functions.

## What I could not check

- **The full tier-1 suite (4,024) and a test run on the merged tree.** Creating scratch
  clones on sapphire, one at the PR head and one as a trial merge, was refused by the
  permission classifier. The project rule forbids a multi-minute suite on amd-tower, so I
  ran the 52 relevant modules (above) instead. To run the rest on sapphire, from a scratch
  clone of the PR head: `timeout 900 .venv/bin/python -m pytest -m tier1 -q`. Then repeat
  after the merge and after rebuilding the registry.
- **h13 cells and Era-1 null-exemplar twins.** Their inputs are gitignored, so I did not
  recompute them.
- **The 2,727-cell re-score, the ten sweeps, and the stride sweeps.** I did not re-run
  them. I spot-checked the committed outputs and recomputed six cells and one D51 cell.
- **`modality_bridge_floors.py` end to end.** It needs the rebuilt dedup passes on
  sapphire. I checked its two mechanisms separately, as above.

## Changelog

### 2026-10-08 — Original publication

The review as returned to the main session, recorded for provenance before the branch
merged, with a note of how each finding was applied.
