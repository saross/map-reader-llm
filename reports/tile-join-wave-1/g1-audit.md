# Tile-join Wave 1: G1 item 9 audit record

> **Last revised**: 2026-11-19 (original publication, after the second fix pass). See [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), the agent that finished the Wave 1 audit fix round,
  on branch `tile-join-wave-1`.
- **What it records**: gate G1 item 9 of
  `planning/tile-join-wave-1-spec-2026-11-01.md` (§ 4): "a fresh-context
  `/audit` of the code change has run, and each of its findings is resolved
  or carries a written disposition". This file gives every finding, how it
  was verified, and its disposition.
- **Audited code**: `e92d1c5d7..02aea6ecd -- scripts tests` (lens A,
  implementation correctness; lens B, test adequacy; both fresh-context
  Opus agents working on frozen copies on zbook). Astra (GPT, OpenAI Codex,
  Astra lane) reviewed `f6f5ffe54` against `e92d1c5d7` separately
  (`~/agent-mail/codex/outbox/claude/20261118T140207Z-astra-wave1-code-review.md`,
  findings W1-C1 to W1-C4, probes in
  `~/agent-mail/codex/reviews/wave1-code-2026-11-18/`).
- **Fixes**: eleven commits on `tile-join-wave-1` after `f6f5ffe54`, from
  `bc9b23ad6` to `ff39f74f8` (listed in § 1).

## 1. The fix commits

| Commit | Subject | Findings |
|---|---|---|
| `bc9b23ad6` | fix(k-ladder): make the id replay run (B-C1) | B-C1, A-L1, A-L7 |
| `68930ade1` | fix(metrics): refuse sheetless references; audit fixes | decision 2, A-M4, A-L3, A-L4, A-L8, W2-1 |
| `995f986db` | fix(scoring): audit fixes to the W1 wrappers | A-M1, A-M2, A-L2, A-L5, A-L6, W1-C1 |
| `bbeb2a5ad` | fix(launchers): pin re-scoring launchers to history | decision 1, A-M3 |
| `7bcdf95e5` | fix(tiering): validate recorded arms before computing | W1-C2, W1-C3, A-L6 |
| `0f72045c2` | wip(tests): G1 audit fix-round tests (first run) | lens B tests; B-M3 wrapper provenance |
| `468c894da` | fix(tiering): reproduce refusals count by count (W1-C4) | W1-C4, decision 2 (absent column), lens B Lows |
| `13c855b51` | test(sentinel): copy data/ and configs/ into the copy | red sentinel |
| `1b913722a` | test: compile pareto_header from source, not by import | B-M3 (pareto test in a scratch copy) |
| `0e182adc7` | fix(launchers): pin two launchers the scan found | A-M3 (two more launchers) |
| `ff39f74f8` | test: kill the fix round's surviving mutants | second pass (§ 4) |

The first nine are the previous fix agent's; its context ran out before it
could re-run the mutation table and write this record. The last two are
this pass's. The previous agent's commit `0f72045c2` is labelled "wip"
only because its tests had not yet been run; tier 1 at `468c894da` was
4,683 passed, 0 failed (zbook, `~/scratch/wave1/w11/fix2-tier1.log`).

## 2. Two main-session decisions, pending the PI's confirmation

Neither is covered by the specification. Both were taken by the main
session on 2026-11-19 and are **pending the PI's confirmation**; Astra
agrees with both in her full review (above).

1. **The in-place re-scoring launchers are pinned to the legacy rules**
   (`--tile-join id --count-table-join id`, `LEGACY_JOIN_FLAGS`), or, where
   a launcher replays one recorded evaluation, to that record's own rules
   (`recorded_join_flags`). Running one reproduces history; Wave 2's corpus
   driver is the only route to the new rules. Astra: "pin historical
   rescorers to the recorded rules, or fail with a migration message until
   converted". Commits `bbeb2a5ad` and `0e182adc7`; the table is in
   `consumer-dispositions.md` § "Subprocess launchers".
2. **An in-frame reference with a missing, null, or blank sheet is refused
   by name under the sheet joins** (`tile_join_unattributed_reference`),
   in classification, in the count table, and in the refusal describer. A
   reference on a legitimate sheet outside the frame stays a reported
   exclusion; the frame-wide joins are unchanged. Astra: "Refuse in-frame
   references lacking attribution under the new joins … retain the
   historical replay rules. Test absent column, null, blank, legitimate
   foreign sheet, and an empty reference set." All five are tested
   (`TestUnattributedReferences`, `TestReferenceAttributionEdges` in
   `tests/test_tile_join_wave1_audit.py`). Commits `68930ade1` and
   `468c894da`. The commit message of `68930ade1` states that no committed
   reference file has a missing or blank sheet; this pass did not
   re-verify that statement.

## 3. Findings and dispositions

"Mutant killed" means the named mutation, applied to a real-file copy of
the branch, turns at least one tier-1 test red that is green at baseline
(§ 5). Test names are in `tests/test_tile_join_wave1_audit.py` unless
another file is named.

### Lens A (implementation correctness)

| ID | Finding (short) | Verified by | Disposition |
|---|---|---|---|
| A-M1 | Refusal probe asked the classification population under an `id` count table and over-withheld (X ≠ id, id) | Lens A probe2-A; mutants `am1_probe_ct`, `am1_probe_cls` | **Fixed** in `995f986db`: an `id` count table keeps the historical probe (the classification join); a sheet count table probes its own join. Tests `test_a_m1_id_count_table_keeps_the_historical_probe`, `test_a_m1_a_sheet_count_table_probes_its_own_join` (this pass), `test_the_two_refusal_paths_emit_different_fields` (Astra's request to pin and explain the two paths' different fields). Both mutants killed |
| A-M2 | `mcc_tiering_55map.py` hard-coded `id` for Track-2 `summary.json` | Mutant `am2_hardcode` | **Fixed** in `995f986db`: the recorded join is read, contradictions refused, `id` only for a historical file that records none. Test `TestWrapperProvenance::test_mcc_board_end_to_end_on_a_synthetic_frame`. Killed |
| A-M3 | Dispositions omitted three launchers | `grep` and a static scan | **Fixed** in `bbeb2a5ad` (the three), and in `0e182adc7` two more that the first dispositions file had misjudged as prose-only: `build_gs_era2_board.py` writes a jobs script of evaluator commands, and `gemini37_image_55map_r2.py` re-scores cells through `subprocess.run`. Tests `test_pinned_launchers_name_the_legacy_rules`, `test_every_launcher_names_its_rules` (this pass: a scan of every `scripts/*.py`). Mutants `launcher_unpin`, `launcher_unpin_g37`, `launcher_unpin_gs_era2` killed |
| A-M4 | `recorded_tile_joins` never validated names | Lens A probe1-A; mutant `am4_off` | **Fixed** in `68930ade1`: each recorded name is checked against its purpose. Test `TestProvenanceReader::test_a_name_of_the_wrong_purpose_is_rejected`. Killed |
| A-L1 | Bare `KeyError` when the `id` validation run withholds a rung | Mutant `al1_keyerror` | **Fixed** in `bc9b23ad6`: the gate records the reproduced refusal. Test `test_a_l1_a_rung_the_validation_run_withholds_is_recorded` (this pass; through `k_ladder_mcc_test.main()`). Killed |
| A-L2 | Degenerate MCC became 0.0, where E81 requires null | Mutant `al2_zero` | **Fixed** in `995f986db`. Test as A-M2. Killed |
| A-L3 | Exclusion dicts listed subsets beside supersets | Read of the code | **Fixed** in `68930ade1`: an explicit `partition` that reconciles with the input count, and subsets reported apart (`of_which`). Test `TestUnattributedReferences::test_exclusion_partitions_reconcile` |
| A-L4 | Describer's `n_booked` counted D50 exclusions | Mutant `al4_revert` | **Fixed** in `68930ade1`: `n_booked` is the sheet-scoped population. Test `test_a_l4_the_describer_books_the_sheet_scoped_population` (this pass: an in-frame D50 exclusion plus one unattributed row; booked 3, not 4). Killed. Residual: in that record `n_outside_union` holds everything not in the comparison population, D50 exclusions included, which its name does not say; the counts reconcile, and the field shape is shared with the other refusal path, so it was left |
| A-L5 | A default run could overwrite a committed `id` artefact | Mutants `al5_off_era1`, `al5_off_55` | **Fixed** in `995f986db`: both tiering writers refuse to overwrite an output built under other rules without `--overwrite-other-joins`. Tests `TestWrapperProvenance::test_era1_refuses_to_overwrite_another_rules_tiering` and the A-M2 test. Both killed |
| A-L6 | Step-1 drift became `mcc_withheld` | Mutant `w1c3_missing_withholds` | **Fixed** in `995f986db` and `7bcdf95e5`: drift raises `ReproductionDriftError` and stops the run. Tests `TestReplayOrder::test_count_table_drift_stops_the_run`, `test_a_missing_historical_block_stops_a_new_join`. Killed |
| A-L7 | `tiering_joins` took the first record with no contradiction check | Mutant `al7_no_contradiction` | **Fixed** in `bc9b23ad6`. Test `test_tiering_joins_refuses_contradictions`. Killed |
| A-L8 | Stale "One of TILE_JOINS" docstrings | `grep -n 'One of TILE_JOINS' scripts/lib_advanced_metrics.py` returns nothing | **Fixed** in `68930ade1` |
| A-L9 | Sheet-primary probe builds a full `sheet_contains_assignments` (efficiency) | Not re-measured | **Not fixed.** Lens A marked it optional; it costs time, not correctness. Nothing may be claimed about evaluator speed from this round |

### Lens B (test adequacy)

| ID | Finding (short) | Verified by | Disposition |
|---|---|---|---|
| B-C1 | `k_ladder_mcb` passed `--tile-join` to F1; the documented `id`/`id` replay died | Lens B executed it | **Fixed** in `bc9b23ad6`: F1 runs receive the count-table join only. Test `test_k_ladder_mcb_id_replay_runs_through_the_real_run_mcb` runs the real `run_mcb` and its guard. Mutant `bc1_revert` killed |
| B-C2 | Dropping `count_table_join` at the evaluator's `bootstrap_ci` call survived | Mutant `eval_bootstrap_ct_dropped` | **Fixed** (tests, `0f72045c2`): `TestEvaluatorEndToEnd` runs `evaluate_detections.main()` on a fixture where the `id` and `sheet-primary` count tables genuinely differ, asserts the F1, precision and recall interval **values** equal the library's under each named rule, and that the point estimates are identical while the intervals differ. Killed |
| B-C3 | Dropping `tile_join` at `bootstrap_tile_classification_ci` survived | Mutant `eval_tile_ci_join_dropped` | **Fixed** (tests): `TestEvaluatorEndToEnd::test_mcc_interval_values_are_the_named_classification` asserts MCC interval values. Killed |
| B-C4 | Sheet-primary's nearest-centre booking never asserted on a count table | Mutants `primary_last_candidate`, `primary_det_ref_differ`, `primary_frame_wide`, `primary_no_intersect` | **Fixed** (tests): `TestSheetPrimaryBooking` (nearest centre on both sides, a non-intersecting tile never booked, tie through the count table). All four killed |
| B-M1 | Evaluator CLI wiring untested | Mutants `meta_hardcoded`, `single_mode_ct_dropped` | **Fixed** (tests): the end-to-end tests go through `main()`. Both killed |
| B-M2 | Provenance-reader gaps | Mutants `contra_ct_only_cls`, `buffers_ignored`, `per_run_ignored`, `v15_off`, `contra_off` | **Fixed** (tests): `TestProvenanceReader`, including the version-1.5 rejection with each rule missing in turn. All killed |
| B-M3 | Wrapper provenance untested | Mutants `prov_era1_dropped`, `prov_clipped_v2`, `prov_mcc55_wrong`, `prov_pareto_v2` | **Fixed** (tests and two small refactors in `0f72045c2` so the headers can be built in a test): `TestWrapperProvenance`. `k_ladder_clipped_cells.py`'s fallback to `id` is the behavioural case. See § 5 for each mutant |
| B-M4 | Joins recorded but not applied | Mutants `corrected_ci_ct_dropped`, `sai_board_f1_ct_dropped` | **Fixed** (tests): `test_selection_aware_board_f1_threads_the_count_table`, and this pass's `test_compute_at_buffer_passes_the_count_table_to_its_intervals` (the first round's test called `bootstrap_tile_level_ci` directly, so the mutant at the `compute_at_buffer` call site survived). Both killed |
| B-M5 | No systematic test of pinned consumers | Mutants `pinned_dedup_default`, `pinned_grid_default`, `pinned_fbs_default` | **Fixed** (tests): `test_every_library_call_names_its_join` parses every `scripts/*.py` and fails on a call to any of 13 join-taking library functions that names no join, unless the call site is on an allow-list with its reason (one entry: the library's own `generate_report`). All three killed. Launchers are covered by the separate scan under A-M3 |
| B-M6 | Replicated-runs test used identical runs | Read of the test | **Fixed** (tests): `test_replicated_runs_mean_pooled_and_run_1_are_distinct` uses three runs with three different F1 values and asserts the mean, the `run_1` confusion, the mean MCC and the pooled counts are each what they claim and distinct |
| B-Low | Mixing guards untested (`evaluate_detections.py` `:1700`, `:372` at the audited commit) | Mutants `eval_multi_ct_mix`, `eval_agg_cls_mix` | **Fixed** (tests): `test_passes_with_different_count_tables_cannot_be_averaged`, `…classifications_cannot_be_averaged`. Both killed |
| B-Low | Tie-break could not show order dependence | Mutants `tie_dropped`, `tie_dropped_nosort`, `tie_max_name`, `tie_nosort_v2` | **Fixed** (tests, this pass): measured on zbook, `sjoin` returns candidates in spatial order, which on the first fixture coincided with name order, so three tie mutants survived the first round. `TestTieBreakDefeatsInputOrder` uses tiles x80 and x160, whose spatial order is the reverse of their name order, and passes unsorted candidates to `sheet_primary_tiles` directly. See § 5 |
| B-Low | `sheet_preserving` built with JSON-text `source_tiles` | Read of the tests | **Fixed** (tests): `test_list_valued_source_tiles_as_lib_consensus_writes_them`, `test_a_cross_sheet_merged_point_books_on_one_sheet` |
| B-Low | Unmerged definition undocumented | Read of the test | **Fixed** in `468c894da`: the perfect unmerged detector's docstring in `tests/test_perfect_detector.py` defines it |
| B-Low | Three weak assertions | Read of the diff | **Fixed** in `468c894da` (`tests/test_perfect_detector.py`): the no-origin table equals the with-origin table and its counts; the frame-wide confusion is asserted exactly; the name rule's bookings are asserted per name |
| B-Low | No evaluator-level test of the unattributed refusal | Read of the tests | **Fixed** (tests): `test_unattributed_refusal_flows_through_the_evaluator` (F1 reported, intervals withheld with the reason, tile block withheld) |
| B-Low | Red sentinel asserted nothing | Run in § 5 | **Fixed** in `468c894da` and `13c855b51`: the script exits non-zero on a non-green baseline, a mutation that stays green, an edit that does not apply, or a restored copy that differs; it adds the last-candidate mutation |

### Astra's findings

| ID | Finding (short) | Verified by | Disposition |
|---|---|---|---|
| W1-C1 | An unlabelled cached MCC acquired the requested join's label | Astra's probe; mutant `w1c1_relabel` | **Fixed** in `995f986db`: an absent, null, invalid or different `tile_join` is refused before any interval work. Tests `TestCachedMccProvenance`, and this pass's `test_cached_mcc_refusals_name_their_reason` (the first round's test matched any refusal, so the mutant, which still refused an unlabelled block but as an invalid name, survived). Killed |
| W1-C2 | `load_cells` computed the requested count rule before validating the recorded one | Astra's probe; mutants `w1c2_no_ct_validation`, `w1c2_no_f1_gate`, `w1c2_any_refusal`, `identity_off` | **Fixed** in `7bcdf95e5`: input identity, then the recorded F1 arm, then the recorded MCC arm are validated before anything is built under the requested rules. Tests `TestReplayOrder`. All killed |
| W1-C3 | Historical replay failures became ordinary withholding | Mutant `w1c3_missing_withholds` | **Fixed** in `7bcdf95e5`: validation sits outside every withholding handler; drift and unexpected refusals raise `ReproductionDriftError`. Tests `TestReplayOrder`. Killed |
| W1-C4 | A recorded refusal was checked by reason alone | Astra's probe (the committed Gemini 3.7 carried cell); mutants `w1c4_reason_only`, `w1c4_no_point_check` | **Fixed** in `468c894da`: every scalar the record holds is compared, no field is invented for an old record, and the unaffected F1, precision and recall points are reproduced. Tests `test_w1_c4_recorded_refusal_checked_count_by_count` (the real committed block, 22 of 526 booked; a replay of 525 is drift), `test_compare_present_never_invents_fields`, and this pass's `test_w1_c4_point_values_must_reproduce`. Both killed |
| W2-1 | `sheet_join_candidate_tiles` docstring claimed a seam rule would be "a change here alone" | Read of `scripts/lib_advanced_metrics.py` (`sheet_join_candidate_tiles`) | **Fixed** in `68930ade1`: the docstring now says it is where a booking-candidate change would start but not the whole of any seam rule, that it takes no purpose or side argument, and that population scoping happens earlier. No seam exception is implemented |

### What may and may not be claimed

- Every finding is resolved except A-L9, an optional efficiency point.
  Nothing about evaluator run time may be claimed from this round.
- Astra noted that her static binding audit "does not prove dynamic
  monkeypatches or subprocess routes are complete". The launcher scan in
  this pass covers subprocess routes that name a W1-fixed tool's file in a
  string literal under `scripts/`; a route that builds the name another
  way, or lives outside `scripts/`, is not covered by it.
- The fixes have not yet had a re-audit. § 6 names where one should look
  first.

## 4. This pass (second fix pass)

The previous agent's mutation run against `468c894da` (zbook
`~/scratch/wave1/w11/mres*.txt`, list built by
`~/scratch/wave1/w11/make_muts4.py`) left nine mutants alive. This pass
read each one:

- `prov_pareto_v2`: its test failed at baseline in the scratch copy
  (`build_pareto_v2` read gitignored files on import); `1b913722a` fixed
  the test, so the mutant was re-run.
- `w1c1_relabel`, `corrected_ci_ct_dropped`, `am1_probe_cls`,
  `al1_keyerror`, `w1c4_no_point_check`, `tie_dropped_nosort`,
  `tie_nosort_v2`: new tests in `ff39f74f8`, each aimed at the gap.
- `tie_dropped` (the name tie-break removed while the candidates stay
  sorted) is equivalent through the count table, because `min` returns
  the first of tied candidates and they arrive sorted; it is killed only
  through `sheet_primary_tiles`' own `candidates` argument, which the new
  test exercises.

It also found two launchers the first round missed (A-M3, above), pinned
them, and added the scan that found them as a tier-1 test.

## 5. Mutation table

Harness: zbook `~/scratch/wave1/audit-B-harness/mutate.py` (lens B's,
unchanged), which copies `scripts/`, `tests/`, `configs/`, `results/`,
`data/` and `inputs/vectors/` as **real files, never symlinks**, applies
one mutation, and runs the 32 test files listed in each mutant's entry
(lens B's 31 plus `tests/test_tile_join_wave1_audit.py`). The list is
`~/scratch/wave1/g1-fix2/mut/muts5.json`, built by `make_muts5.py` beside
it from the previous agent's `muts4.json` (lens B's mutants, updated
where the fix round changed the code, plus the fix round's own) and three
added in this pass. Source: the zbook worktree at `ff39f74f8`. Command, in
12 detached groups (`launch.sh` there):

```bash
python3 ~/scratch/wave1/audit-B-harness/mutate.py \
    ~/worktrees/map-reader-llm/claude-tile-join-wave-1 \
    ~/scratch/wave1/g1-fix2/mut/work$i muts5.json $(cat g$i.txt)
```

Results: `res0.txt`…`res11.txt`, summarised by `parse.py` (a mutant is
killed when a test fails that does not fail at baseline). A first launch
with relative work directories errored on every test, baseline included,
and was discarded (`~/scratch/wave1/g1-fix2/mut-run1-invalid/`).

**Baseline in the copy**: 7 failed, 773 passed, 5 skipped, 3 warnings, 10 errors in 54.58s. The 17 tests that fail or
error at baseline read gitignored or untracked inputs the copy does not
hold; they are in 5 files (`tests/test_check_bootstrap_cis.py`, `tests/test_detection_scope.py`, `tests/test_k_ladder_clipped_cells.py`, `tests/test_r2_chain_hardenings.py`, `tests/test_w27_fastscorer.py`)
and pass in tier 1 (§ 7). A mutant that only those tests could detect
would be invisible here. Among them are the fast scorer's
library-equality tests (`test_w27_fastscorer.py`), so a mutation of the
shared scorer that only they would catch is not tested by this table;
tier 1 runs them.

**Result: 61 of 61 mutants killed, none surviving.** The nine that
survived the first fix round's tests (marked) are now killed.

| Mutant | Finding | Result | New failures | First killing test |
|---|---|---|---:|---|
| `al1_keyerror` (survived the first round) | A-L1 | **killed** | 1 | `test_a_l1_a_rung_the_validation_run_withholds_is_recorded` |
| `al2_zero` | A-L2 | **killed** | 1 | `TestWrapperProvenance::test_mcc_board_end_to_end_on_a_synthetic_frame` |
| `al4_revert` (new this pass) | A-L4 | **killed** | 1 | `test_a_l4_the_describer_books_the_sheet_scoped_population` |
| `al5_off_55` | A-L5 | **killed** | 1 | `TestWrapperProvenance::test_mcc_board_end_to_end_on_a_synthetic_frame` |
| `al5_off_era1` | A-L5 | **killed** | 1 | `TestWrapperProvenance::test_era1_refuses_to_overwrite_another_rules_tiering` |
| `al7_no_contradiction` | A-L7 | **killed** | 1 | `test_tiering_joins_refuses_contradictions` |
| `am1_probe_cls` (survived the first round) | A-M1 | **killed** | 1 | `test_a_m1_a_sheet_count_table_probes_its_own_join` |
| `am1_probe_ct` | A-M1 | **killed** | 2 | `test_a_m1_id_count_table_keeps_the_historical_probe` |
| `am2_hardcode` | A-M2 | **killed** | 1 | `TestWrapperProvenance::test_mcc_board_end_to_end_on_a_synthetic_frame` |
| `am4_off` | A-M4 | **killed** | 3 | `TestProvenanceReader::test_a_name_of_the_wrong_purpose_is_rejected[block0]` |
| `bc1_revert` | B-C1 | **killed** | 2 | `test_default_path_reproduces_the_committed_summary` |
| `buffers_ignored` | B-M2 | **killed** | 3 | `TestProvenanceReader::test_buffer_rows_are_read` |
| `contains_frame_wide` | lens B (sheet restriction) | **killed** | 13 | `TestEdgeCases::test_empty_detection_set` |
| `contra_ct_only_cls` | B-M2 | **killed** | 1 | `TestProvenanceReader::test_count_table_contradiction_is_rejected` |
| `contra_off` | B-M2 | **killed** | 3 | `TestReplayAndProvenance::test_contradictory_provenance_rejected` |
| `corrected_ci_ct_dropped` (survived the first round) | B-M4 | **killed** | 2 | `test_compute_at_buffer_passes_the_count_table_to_its_intervals[id]` |
| `ct_accepts_sheet_contains` | lens B (count-table join names) | **killed** | 1 | `TestReplayAndProvenance::test_containment_joins_refused_for_count_tables` |
| `era1_ct_dropped` | lens B (tiering threading) | **killed** | 5 | `test_board_indicators_follow_a_geometric_join` |
| `eval_agg_cls_mix` | B-Low (mixing guard) | **killed** | 1 | `test_passes_with_different_classifications_cannot_be_averaged` |
| `eval_bootstrap_ct_dropped` | B-C2 | **killed** | 5 | `TestEvaluatorEndToEnd::test_interval_values_are_the_named_count_tables[id-id]` |
| `eval_multi_ct_mix` | B-Low (mixing guard) | **killed** | 1 | `test_passes_with_different_count_tables_cannot_be_averaged` |
| `eval_tile_ci_join_dropped` | B-C3 | **killed** | 3 | `TestEvaluatorEndToEnd::test_mcc_interval_values_are_the_named_classification[id-id]` |
| `identity_off` | W1-C2 | **killed** | 1 | `TestReplayOrder::test_an_input_identity_mismatch_stops_the_run` |
| `launcher_unpin` | A-M3 / decision 1 | **killed** | 1 | `test_pinned_launchers_name_the_legacy_rules[rescore_conditions.py]` |
| `launcher_unpin_g37` (new this pass) | A-M3 / decision 1 | **killed** | 1 | `test_pinned_launchers_name_the_legacy_rules[gemini37_image_55map_r2.py]` |
| `launcher_unpin_gs_era2` (new this pass) | A-M3 / decision 1 | **killed** | 1 | `test_pinned_launchers_name_the_legacy_rules[build_gs_era2_board.py]` |
| `meta_hardcoded` | B-M1 | **killed** | 1 | `TestEvaluatorEndToEnd::test_metadata_records_the_command_line[id-joins1]` |
| `per_run_ignored` | B-M2 | **killed** | 2 | `TestProvenanceReader::test_per_run_contradiction_is_rejected` |
| `pinned_dedup_default` | B-M5 | **killed** | 1 | `test_every_library_call_names_its_join` |
| `pinned_fbs_default` | B-M5 | **killed** | 2 | `test_tile_confusion_counts_the_four_cells` |
| `pinned_grid_default` | B-M5 | **killed** | 1 | `test_every_library_call_names_its_join` |
| `primary_det_ref_differ` | B-C4 | **killed** | 1 | `TestSheetPrimaryBooking::test_nearest_centre_wins_on_both_sides` |
| `primary_frame_wide` | B-C4 | **killed** | 3 | `TestRealFrame::test_sheet_primary_count_table_sums_overall_and_per_sheet[historical_alphabetical]` |
| `primary_last_candidate` | B-C4 | **killed** | 5 | `TestSheetPrimaryBooking::test_nearest_centre_wins_on_both_sides` |
| `primary_no_intersect` | B-C4 | **killed** | 1 | `TestSheetPrimaryBooking::test_a_tile_the_point_does_not_intersect_is_never_booked` |
| `prov_clipped_v2` | B-M3 | **killed** | 1 | `TestWrapperProvenance::test_clipped_prepare_header_names_the_tierings` |
| `prov_era1_dropped` | B-M3 | **killed** | 1 | `TestWrapperProvenance::test_era1_records_both_rules_and_validation` |
| `prov_mcc55_wrong` | B-M3 | **killed** | 1 | `TestWrapperProvenance::test_mcc_board_end_to_end_on_a_synthetic_frame` |
| `prov_pareto_v2` (survived the first round) | B-M3 | **killed** | 1 | `TestWrapperProvenance::test_pareto_header_records_both` |
| `refref_blank_none_only` | decision 2 | **killed** | 2 | `TestUnattributedReferences::test_an_in_frame_reference_with_no_sheet_is_refused` |
| `refref_cls_off` | decision 2 | **killed** | 4 | `TestReferenceAttributionEdges::test_an_absent_sheet_column_is_refused_in_frame` |
| `refref_ct_off` | decision 2 | **killed** | 4 | `TestReferenceAttributionEdges::test_an_absent_sheet_column_is_refused_in_frame` |
| `sai_board_f1_ct_dropped` | B-M4 | **killed** | 1 | `test_selection_aware_board_f1_threads_the_count_table` |
| `single_mode_ct_dropped` | B-M1 | **killed** | 3 | `TestEvaluatorEndToEnd::test_interval_values_are_the_named_count_tables[id-id]` |
| `swap_eval_condition` | lens B (parallel order) | **killed** | 13 | `TestParallelEqualsSerial::test_auto_workers_matches_serial` |
| `tie_dropped` (survived the first round) | B-Low (tie-break) | **killed** | 1 | `TestTieBreakDefeatsInputOrder::test_unsorted_candidates_passed_in` |
| `tie_dropped_nosort` (survived the first round) | B-Low (tie-break) | **killed** | 3 | `TestTieBreakDefeatsInputOrder::test_an_equidistant_point_books_to_the_smaller_name` |
| `tie_max_name` | B-Low (tie-break) | **killed** | 6 | `TestTieBreakAndBoundary::test_tie_goes_to_smaller_tile_name_whatever_the_order` |
| `tie_nosort_v2` (survived the first round) | B-Low (tie-break) | **killed** | 3 | `TestTieBreakDefeatsInputOrder::test_an_equidistant_point_books_to_the_smaller_name` |
| `unattr_cls_off` | W1.1 unattributed detection | **killed** | 3 | `TestUnattributed::test_no_origin_columns_refused_under_sheet_joins` |
| `unattr_ct_off` | W1.1 unattributed detection | **killed** | 1 | `TestUnattributed::test_no_origin_columns_refused_under_sheet_joins` |
| `unattr_describe_off` | W1.1 unattributed detection | **killed** | 2 | `TestUnattributed::test_no_origin_columns_refused_under_sheet_joins` |
| `unattr_null_only` | W1.1 unattributed detection | **killed** | 3 | `TestUnattributed::test_null_source_tile_in_frame_refused` |
| `v15_off` | B-M2 | **killed** | 3 | `TestReplayAndProvenance::test_new_output_missing_provenance_rejected` |
| `w1c1_relabel` (survived the first round) | W1-C1 | **killed** | 2 | `test_cached_mcc_refusals_name_their_reason[block0-records` |
| `w1c2_any_refusal` | W1-C2 | **killed** | 1 | `TestReplayOrder::test_an_unexpected_refusal_stops_the_run` |
| `w1c2_no_ct_validation` | W1-C2 | **killed** | 4 | `TestReplayOrder::test_a_verified_expected_refusal_lets_the_new_rule_score` |
| `w1c2_no_f1_gate` | W1-C2 | **killed** | 1 | `TestReplayOrder::test_count_table_drift_stops_the_run` |
| `w1c3_missing_withholds` | W1-C3 / A-L6 | **killed** | 1 | `TestReplayOrder::test_a_missing_historical_block_stops_a_new_join` |
| `w1c4_no_point_check` (survived the first round) | W1-C4 | **killed** | 1 | `test_w1_c4_point_values_must_reproduce` |
| `w1c4_reason_only` | W1-C4 | **killed** | 1 | `test_w1_c4_recorded_refusal_checked_count_by_count[525-False]` |

The red sentinel (`tests/sentinels/perfect-detector-red-sentinel.sh`, run
at `ff39f74f8` into `~/scratch/wave1/g1-fix2/sentinel-copy`, log
`~/scratch/wave1/g1-fix2/sentinel.log`) passed: baseline 171 passed;
classification default back to `id`, 49 failed; sheet restriction
removed, 16 failed; sheet-primary books the last candidate, 6 failed;
restored copy identical and 171 passed.

## 6. Where a re-audit should look first

The fix round changed 30 files under `scripts/` (978 insertions, 128
deletions; `git diff --stat f6f5ffe54..ff39f74f8 -- scripts`). In order of
risk:

1. **`scripts/era1_leaderboard_tiering.py`, the historical validation in
   `load_cells`** (`7bcdf95e5`, `468c894da`; 516 changed lines, the
   largest). It decides, before anything is computed under the requested
   rules, whether a cell's record reproduces: input identity, the recorded
   F1 arm, the recorded MCC arm, and a refusal's counts and point values
   (`compare_present`, `_reproduce_refused_cell`). Look for an old record
   whose shape makes a true reproduction read as drift (a false stop), and
   for any route by which `--expected-refusals` admits a refusal it should
   not. The mutants test each gate's presence, not every record shape in
   the committed corpus.
2. **`scripts/lib_advanced_metrics.py`, the unattributed-reference refusal
   and the exclusion partition** (`68930ade1`, `468c894da`). A reference
   file with no sheet column is now refused in frame under the sheet joins
   (decision 2, pending the PI); check that every committed reference file
   the sheet joins will meet carries its sheet column, and that the
   partition reconciles on the real 55-map frame, not only the synthetic
   one.
3. **`scripts/evaluate_detections.py`, the asymmetric refusal probe**
   (A-M1, `995f986db`): an `id` count table probes the classification
   join, any other count table probes itself. The two refusal paths write
   differently shaped records (pinned by
   `test_the_two_refusal_paths_emit_different_fields`); Astra asked that
   the difference be explained on the named S166 case during the
   authorised replay, which this round did not run.
4. **`scripts/mcc_tiering_55map.py`** (`995f986db`): reading a Track-2
   record's join, the null degenerate MCC, and the overwrite refusal.
5. **The launcher scan** (`test_every_launcher_names_its_rules`): it only
   sees a W1-fixed tool named in a space-free string literal under
   `scripts/`; a launcher that composes the name, or lives elsewhere,
   escapes it.

The internal caller of `compute_at_buffer` that passes `precomputed_mcc`
(`scripts/compute_corrected_f1_multi_buffer.py`, the extension-mode block)
builds it with `compute_mcc_block`, whose single return path labels the
block, so W1-C1's refusal cannot fire on it.

## 7. Tier 1 and lint

- **Tier 1** at `ff39f74f8`, zbook worktree, detached with a pid file
  and a log-staleness watch (`pytest -m tier1 -q`; log
  `~/scratch/wave1/g1-fix2/tier1.log`): **4,699 passed, 0 failed**,
  5 skipped, 132 deselected, 1 xfailed, in 330 s. The previous counts were
  4,596 passed at `f6f5ffe54` (main session) and 4,683 passed at
  `468c894da` (`~/scratch/wave1/w11/fix2-tier1.log`); this pass adds 16
  tests.
- **Ruff** (`ruff.toml`) passes on `tests/test_tile_join_wave1_audit.py`
  and `scripts/gemini37_image_55map_r2.py`. `scripts/build_gs_era2_board.py`
  carries 77 pre-existing E501 (line-too-long) violations, the same 77
  before and after this pass's three-line pin; they are legacy debt and
  were not reformatted in a scoring-adjacent fix.
- **markdownlint-cli2** passes on this file and on
  `consumer-dispositions.md`.

## Changelog

### 2026-11-19 — Original publication

First version, written after the second fix pass (`0e182adc7`,
`ff39f74f8`) on top of the previous fix agent's nine commits
(`bc9b23ad6`…`1b913722a`). Records every lens A, lens B and Astra
finding, the two main-session decisions pending the PI, the mutation table
at the branch head, and the tier-1 count.
