# G1 item 9 audit findings: Wave 1 code at `02aea6ecd` (both lenses, fresh context, Opus)

> Copied from the S169 main session's scratchpad on 2026-11-19, so that `g1-audit.md` and the mail record have a durable source. Unchanged except for this note.

Audited: `e92d1c5d7..02aea6ecd -- scripts tests` (96 files). The reviewers
worked on frozen `git archive` copies on zbook; evidence is in
`~/scratch/wave1/audit-A/` (probe*.py, callcheck-A.py, sigdiff-A.py) and in
`~/scratch/wave1/audit-B-harness/` (mutate.py, muts*.json, results*.txt).

## Lens A (implementation correctness): no Critical

Confirmed clean:

- symbol matching is unchanged;
- all 612 join-taking calls bind correctly (AST simulation), and no
  positional shifts occur;
- count tables sum to the symbol totals on real data;
- the sheet-primary tie-break is order-independent (20 shuffles);
- the version-1.5 rule and the contradiction check hold for the
  classification purpose;
- era1's two-computation code carries no committed MCC beside new arrays.

### Medium

- **A-M1.** `evaluate_detections.py:1253-1257`: the refusal probe, under
  `count_table_join="id"`, asks the classification-population question
  (`describe_tile_join_refusal` counts all in-frame `scope.retained`,
  `lib_advanced_metrics.py:5716-5725`), whereas the `id` count table books
  only attributed, in-scope rows (`:3602`, `:3646`). For (X != id, id)
  pairs it over-withholds. Confirmed by probe2-A.py: base
  geometric-contains gives ci_lower 1.0, new (geometric-contains, id) gives
  ci None, withheld. No committed file is affected (all record id or
  nothing). Fix: probe the count table's own population, or state the
  limitation.
- **A-M2.** `mcc_tiering_55map.py:301-303` hard-codes
  `"recorded_tile_join": TILE_JOIN_LEGACY_CLASSIFICATION` for Track-2
  `summary.json`, ignoring the `tile_classification.tile_join` and
  `metadata.tile_joins` that `compute_corrected_f1_multi_buffer.py` now
  writes. After Wave 2 this gives a false GATE FAIL or a wrong label. Fix:
  read the recorded joins (`recorded_tile_joins`-style), falling back to
  `id` for historical files only.
- **A-M3.** `consumer-dispositions.md` omits three launchers of W1-fixed
  tools that pass no join flag:
  - `scripts/run_bootstrap_10k.py:64-85` (re-scores in place);
  - `scripts/score-unscored-conditions-2026-05-30.sh:43` (`.sh`, so missed
    by a `.py`-only search);
  - `scripts/stride55_score.py:181-194` (runs
    `compute_corrected_f1_multi_buffer.py`).
- **A-M4.** `lib_advanced_metrics.py:528` (`recorded_tile_joins`) never
  validates names. A purpose-swapped record (classification
  "sheet-primary", count_table "sheet-contains") or `"bogus"` is returned
  as recorded (probe1-A.py). Fix: run `check_tile_joins` on the result.

### Low

- **A-L1.** `k_ladder_mcc_test.py:596-598, :616`: a bare `KeyError` when the
  `id` validation run withholds a rung that the requested run admits.
  Record an "expected refusal reproduced" instead.
- **A-L2.** `mcc_tiering_55map.py:557`: a degenerate MCC under a
  non-recorded join becomes 0.0. E81 requires null.
- **A-L3.** `lib_advanced_metrics.py:3443-3450` and booking at about
  `:3880-3892`: the exclusion dicts list subset counts beside their
  supersets (`n_out_of_frame_cross_sheet` within `n_out_of_frame`;
  `n_unattributed_in_frame` within `n_unattributed`), so summing them
  double-counts. Make the partition explicit and assert the
  reconciliation.
- **A-L4.** `lib_advanced_metrics.py:5807`: `n_booked = n_in_frame -
  n_unattributed`, where `n_in_frame` includes D50 exclusions. The
  diagnostic misstates the counts.
- **A-L5.** `era1_leaderboard_tiering.py:235` (`tiering_stem`) and
  `mcc_tiering_55map.py:460`: a default run writes under published plain
  names, so it can overwrite a committed `id` artefact (for example
  `55map-mcc-tiering-r2.json`). Consider refusing to overwrite an existing
  output whose recorded joins differ.
- **A-L6.** `era1_leaderboard_tiering.py:1323-1376`: a step-1 reproduction
  drift (`ConfusionGateError`) is caught and becomes `mcc_withheld`. Under
  the spec's § 5, drift should stop. Distinguish drift (stop) from a join
  refusal (withhold).
- **A-L7.** `k_ladder_mcb.py` `tiering_joins`: an "or" chain over three
  records with no contradiction check.
- **A-L8.** Stale docstrings saying "One of TILE_JOINS":
  `lib_advanced_metrics.py:3939` (`compute_per_tile_classification`),
  `:5375` (`assign_points_to_tiles`), and `:6296`
  (`bootstrap_tile_effect_size_ci`).
- **A-L9.** Efficiency: the sheet-primary probe in `evaluate_single_run`
  builds a full `sheet_contains_assignments`, about 220 sjoins per 55-map
  evaluation, to check an invariant that holds by construction.
  Optional.

## Lens B (test adequacy)

The red sentinel reproduced exactly: 68 / 30 failed / 14 failed /
IDENTICAL, 68.

### Critical

- **B-C1 (real bug).** `k_ladder_mcb.py:704` raises when `tile_join !=
  TILE_JOIN_CLASSIFICATION_DEFAULT and metric != "mcc"`, but `main()`
  (`:930-931`) passes `args.tile_join` to every metric (default metrics
  `["f1","mcc"]`, `:865`). So the documented replay `--tile-join id
  --count-table-join id` (header `:116-118`) dies on F1. It was executed:
  `ValueError tile join 'id' applies to the MCC metric only, not 'f1'`.
  `tests/test_k_ladder_mcb.py:457-467` stubs `run_mcb` (`:410-432`), so the
  guard never runs. The old parser guard, and its test
  `test_mcb_main_refuses_a_join_where_it_cannot_apply`, were removed in
  `a7989c47f`.
- **B-C2.** The mutant that deletes `count_table_join=count_table_join` from
  the `bootstrap_ci` call (`evaluate_detections.py:1310`) survives. An
  id/id replay would compute sheet-primary intervals labelled `id`. The
  golden replay's fixture tables coincide. Nothing in tier 1 tests G1
  item 2 through the evaluator.
- **B-C3.** The mutant that deletes `tile_join=tile_join` at
  `evaluate_detections.py:1534` (`bootstrap_tile_classification_ci`)
  survives: the MCC interval comes from the wrong join.
  `test_evaluator_replay_under_id_records_id` checks labels only.
- **B-C4.** sheet-primary's nearest-centre booking is never asserted on a
  count table. Three mutants survive:
  - book the last candidate (`lib_advanced_metrics.py:3841-3846`);
  - change the reference side only;
  - use all sheet tiles, intersecting or not.

  The count-table tests assert only overall and per-sheet sums. The
  tie-break and non-intersecting tests call only the `sheet_primary_tiles`
  helper.

### Medium

- **B-M1.** Evaluator CLI wiring is untested. The mutant that makes
  `_build_metadata` ignore args (`:881-882`) survives, as does the mutant
  where `_run_single_mode` drops `count_table_join` (`:2926`). The
  "emitted evaluation.json" test builds `_metadata` by hand and never
  calls `main()`.
- **B-M2.** Gaps in the provenance reader. These mutants survive:
  - contradiction checked for classification only
    (`lib_advanced_metrics.py:522`);
  - buffer-row records ignored (`:508`);
  - per_run ignored (`:445`).

  The version-1.5 rejection is tested only with both rules missing.
- **B-M3.** Wrapper provenance is untested. These mutants survive:
  - `era1:1610` deleting `tile_joins`;
  - `k_ladder_clipped_cells.py:805`, which has a behavioural consequence
    because `:1056` falls back to `id`;
  - `mcc_tiering_55map.py:605` hard-coding `id`;
  - `build_pareto_v2.py:459`.
- **B-M4.** Joins recorded but never applied: these mutants survive in
  `compute_corrected_f1_multi_buffer.py:820` (`bootstrap_tile_level_ci`)
  and `selection_aware_intervals.py:968` (the board F1 branch). The stub
  in `tests/test_selection_aware_intervals.py:185-186` never records the
  argument.
- **B-M5.** No systematic test of the pinned legacy consumers. Mutants
  survive in `dedup_metric_impact.py:368` and `grid_analysis.py:411`.
  Suggest a static (AST) tier-1 test that every library call site passes
  an explicit join, or is on an allow-list.
- **B-M6.** The replicated-runs test uses identical runs, so the per-run
  mean, the `run_1` confusion, and pooled counts cannot be told apart, and
  "pooled" is a sum the test computes itself. The spec requires distinct
  quantities, each tested.

### Low

- Mixing guards untested: mutants survive at
  `evaluate_detections.py:1700` and `:372`.
- The tie-break cannot show any order dependence, because sjoin returns
  candidates in name order. Test with a bounds order that defeats the
  sort.
- `sheet_preserving` is built by a test helper that stores `source_tiles`
  as JSON text, where `lib_consensus` writes a list. Cross-sheet merged
  points are not exercised under the sheet joins.
- The unmerged definition (own-sheet tiles only) is undocumented in the
  test.
- Weak assertions:
  - `test_explicit_historical_calls_keep_historical_behaviour` (`tp >= 1`
    only);
  - `test_missing_origins_keep_d50_attribution` (no-raise only);
  - `test_no_origin_columns_keep_historical_behaviour` (no-raise only).
- No evaluator-level test that the unattributed refusal flows through
  `evaluate_single_run` (F1 reported, intervals withheld with that
  reason, tile block withheld).
- The red sentinel script asserts nothing (`set -u` only). Make it fail
  on wrong counts, and add a sheet-primary nearest-centre mutation.

## Astra, Wave 2 review W2-1 (affects the code docstring)

`sheet_join_candidate_tiles` (`lib_advanced_metrics.py:3202`) is called
for references and detections in classification (`:3429`) and for
count-table booking (`:3841-3846`), and takes no purpose or side
argument. `iter_sheet_scopes` (`:2723`) filters populations first. Its
docstring claim that a seam decision is "a change here alone" is wrong:
narrow it, and do NOT implement any seam exception.
