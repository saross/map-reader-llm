# Tile-join Wave 1: consumer dispositions

> **Last revised**: 2026-11-19 (shell launchers added, RA-M4; earlier, the G1 audit fix round). See [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), the Wave 1 code agent (W1.1 and W1.2), on branch
  `tile-join-wave-1`.
- **Asked for by**: the main session, relaying Astra's static consumer audit
  (GPT, OpenAI Codex, Astra lane; 2026-11-18;
  `~/agent-mail/codex/outbox/claude/20261118T122600Z-astra-tile-join-consumer-audit.md`,
  inventory `~/agent-mail/codex/reviews/tile-join-consumers-2026-11-18/tile-join-consumer-probe.json`,
  129 abstract-syntax-tree (AST) matched calls at `e92d1c5d7`, 116 of them
  outside the metrics library).
- **Rulings**: PI rulings D72 and D73 in `planning/pi-decisions-2026-09-20.md`;
  the specification is `planning/tile-join-wave-1-spec-2026-11-01.md` (W1.1).

## What this document answers

Wave 1 retires `TILE_JOIN_DEFAULT` and makes the library default to the two
sheet-specific joins: `sheet-contains` for tile classification and
`sheet-primary` for the per-tile count tables (D72, D73 (2), D73 (6)).
Retiring the constant makes its importers fail, but most consumers import a
*function* and inherit its default, so they would have changed their numbers
silently on their next run while writing outputs that look like the old ones.
This document gives every call site in Astra's inventory, plus the routes the
inventory could not see, one disposition:

- **fixed in W1** — the script now takes both rules explicitly, documents them
  in its header, and records them in its own output;
- **inherits the corrected default correctly** — and why that is right;
- **historical replay path** — how it is pinned to its recorded rule;
- **deferred to Wave 2/3 regeneration** — and what stops it publishing an
  apparently migrated result meanwhile.

## How the deferred sites are made safe

Every deferred site is **pinned to the legacy rule by an explicit keyword**:
`tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` on a classification call,
`tile_join=` or `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` on a
count-table call (both constants are `"id"`, defined in
`scripts/lib_advanced_metrics.py`). Commit `e34a7e581` inserted them, one per
leaf call, mechanically from Astra's inventory. So:

1. **Nothing it writes can look migrated.** A pinned script computes exactly
   the rule it always computed, so its outputs reproduce its committed
   outputs, numbers and keys alike. It writes no `tile_joins` provenance, and
   any reader going through `recorded_tile_joins` reads it as a legacy
   (`id`) artefact.
2. **The worklist is a grep.** `grep -rn TILE_JOIN_LEGACY_ scripts/` lists
   every pinned site; Wave 2/3 migrates a script by replacing its pin with the
   two options and the provenance its outputs need, as the W1 wrappers do.
3. **Second-order wrappers are covered at the leaf.** A pin sits inside the
   wrapper that holds the leaf call (`n1_baseline_leaderboard_tiering.pass_averaged_per_tile`,
   `final_board_build.per_tile_arrays`, `dedup_tiering_rerun.per_tile_arrays`
   and the like), so every importer of the wrapper is pinned with it.
   `consensus_vs_baseline_tiering.consensus_per_tile` takes a
   `count_table_join` parameter whose default is the legacy rule, which pins
   its four importers (`tier_verifier_matrix`, `permutation_opmax_vs_headline`,
   `permute_flash35_pairs`, `build_pareto_leaderboard`); `build_pareto_v2`
   passes its own rule.

The trade-off, stated plainly: a pinned *continuing generator* (a board
builder, a sweep) that someone runs for a new result before Wave 2/3 migrates
it produces an `id` result, the rule D72 found invalid for merged output. That
is the same number it would have produced before Wave 1, so it cannot be
mistaken for a corrected one, but it is not a corrected one either. Wave 2/3's
specification should list the pinned continuing generators first.

## Routes the AST inventory could not see

| Route | Disposition |
|---|---|
| `scripts/evaluate-pro-n10.py:333` and `:336` import `calculate_tile_classification` and `bootstrap_tile_classification_ci` through `evaluate_tile_mcc` (a re-export; `:30–36`) | deferred, pinned to legacy at both calls (`e34a7e581`), rows 50 and 51 of the table |
| `describe_tile_join_refusal`, `scripts/evaluate_detections.py` (`evaluate_single_run`) | fixed in W1 (`55737337a`): the probe is asked of the **count-table** join, because what it withholds (intervals, coverage) is read from the count table; the tile block is refused separately by `calculate_tile_classification` under the classification join. Each record names the join it guards |
| `describe_tile_join_refusal`, `scripts/era1_leaderboard_tiering.py` (`refusal_disclosure`) | fixed in W1 (`55737337a`): the disclosure of an F1-arm refusal names the count-table join that refused, not a default |
| The tiering harness's subprocess callers, `scripts/k_ladder_mcc_test.py` and `scripts/k_ladder_mcb.py` (through `selection_aware_intervals.py`) | fixed in W1 (`55737337a`): both joins are passed explicitly on every invocation, and the artefact name is computed by the same rule the harness uses (`era1_leaderboard_tiering.tiering_stem`) |
| `scripts/k_ladder_clipped_cells.py` (writes `evaluate_detections.py` command lines) | fixed in W1 (`55737337a`): both joins are written into every job, never left to the scorer's default |
| `scripts/selection_aware_intervals.py:891–899` (MCC indicators derived from the F1 count arm) | fixed in W1 (`55737337a`): on `--board` the indicators always come from the classification arm; elsewhere the count-arm derivation is allowed only for the explicit historical pair `--tile-join id --count-table-join id` and is labelled `mcc_indicators`; any other pair is refused |
| Evidence scripts outside `scripts/`: about 40 files under `reports/*-scripts/`, `planning/tile-join-resolution-2026-11-01-scripts/` and `archive/` (listed below) | **not changed; outside this agent's write scope.** They are frozen records of past runs. Re-run on Wave 1 code, any that calls a library function without a join inherits the new defaults; to reproduce one, check out the commit its record names. `planning/tile-join-resolution-2026-11-01-scripts/perfect_detector.py` iterates `TILE_JOINS`, which now holds five names, and would raise on `sheet-primary` (a count-table join) as a classification join. **Open item for the main session** |
| The test suite (`tests/`) | tests that restate the legacy rule now ask the library for `id` explicitly; see commit `a7989c47f` |

Evidence scripts found by `grep` for the library's join-bearing functions
under `reports/`, `planning/` and `archive/` at this branch's head (not an
AST census; the main session may want Astra's probe extended to them):

```text
archive/preliminary-work/scripts/compile_stock_taking.py
archive/preliminary-work/scripts/util_advanced_metrics.py
archive/superseded-w27-floors-2026-10-12/floors-v2/floors2_lib.py
planning/tile-join-resolution-2026-11-01-scripts/perfect_detector.py
reports/d42-implementation-2026-10-05-scripts/regen_384_e39.py
reports/d42-implementation-2026-10-05-scripts/wrappers/regen_384.py
reports/d51-ladder-provenance-2026-10-08-scripts/clip_cost.py
reports/d57-4-rescore-2026-10-09-scripts/replay_cell.py
reports/frames-blast-radius-2026-10-07-scripts/blast_lib.py
reports/frames-blast-radius-2026-10-07-scripts/rescore_evaluations.py
reports/input-drift-2026-10-07-scripts/rescore_scored_vintage.py
reports/retest-bootstrap-check-2026-10-05-scripts/b17_retest.py
reports/retest-bootstrap-check-2026-10-05-scripts/fair384_retest.py
reports/retest-bootstrap-check-2026-10-05-scripts/w21_reproduce.py
reports/retest-bootstrap-check-2026-10-05-scripts/w23_score.py
reports/retest-bootstrap-check-2026-10-05-scripts/w23_tests.py
reports/s163-agent-records/bootstrap-hash-order-scripts/fair384_replay.py
reports/s163-agent-records/bootstrap-hash-order-scripts/hash_seed_harness.py
reports/s163-agent-records/bootstrap-hash-order-scripts/pv_pairwise_replay.py
reports/s163-agent-records/origin-gap-h13-copies-scripts/pertile_diversity.py
reports/s164-agent-records/d64-a06-replication-scripts/d64_a06_replication.py
reports/s164-agent-records/d64-a06-replication-scripts/d64_p12_replication.py
reports/s164-agent-records/s9-staleness-sweep-scripts/points_cell.py
reports/s166-agent-records/clipped-tile-mcc-scripts/attribution_check.py
reports/s166-agent-records/k-ladder-mcc-join-scripts/consensus_joins.py
reports/s166-agent-records/k-ladder-mcc-join-scripts/independent_check.py
reports/s166-agent-records/k-ladder-mcc-join-scripts/mechanism.py
reports/s166-agent-records/k-ladder-mcc-join-scripts/render.py
reports/s166-agent-records/mcc-join-tiering-scripts/id_join_mechanism.py
reports/s166-agent-records/mcc-join-tiering-scripts/summarise.py
reports/scorer-frames-d50-d51-2026-10-08-scripts/meas_lib.py
reports/scorer-frames-d50-d51-2026-10-08-scripts/source_tile_gap.py
reports/w27-replicate-floors-2026-10-06-scripts/floors-v2/floors2_55map.py
reports/w27-replicate-floors-2026-10-06-scripts/floors-v2/floors2_lib.py
reports/w27-replicate-floors-2026-10-06-scripts/floors-v2/floors2_scorer_gate.py
reports/w27-replicate-floors-2026-10-06-scripts/runA/runA_score.py
reports/w27-replicate-floors-2026-10-06-scripts/vdate_check.py
reports/w27-replicate-floors-2026-10-06-scripts/vdate_extra.py
reports/w27-replicate-floors-2026-10-06-scripts/vdate_ident.py
reports/w27-replicate-floors-2026-10-06-scripts/w27_55map_subset_replicates.py
```

## Why the nine unpinned sites inherit correctly

Nine `score_detection_set` calls pass `compute_mcc=False` as a literal. With
that flag the function computes the buffer-matched F1, precision and recall
point estimates only: it builds no tile classification and reads no count
table, so no join reaches the number it returns, and its result records
`tile_join: null` and `count_table_join: null` (Wave 1, C3). Symbol matching is
unchanged by Wave 1, so these sites produce exactly what they produced before.

## Per-site table

All 129 calls of Astra's inventory and the two re-exported calls it could not
see. Line numbers are those of `e92d1c5d7`, where the inventory was taken;
lines in the fixed files have since moved. Counts: 36 fixed in W1, 85 deferred
and pinned to the legacy rule, 9 inheriting correctly, 1 historical replay
path.

| # | Call site (line at `e92d1c5d7`) | Enclosing function | Callee | Disposition | Commit | How |
|---:|---|---|---|---|---|---|
| 1 | `scripts/6_accuracy_report.py:165` | `validate_file` | `calculate_tile_classification` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 2 | `scripts/6_accuracy_report.py:168` | `validate_file` | `bootstrap_tile_classification_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 3 | `scripts/analyse_consensus_sweep.py:303` | `evaluate_single_config` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 4 | `scripts/analyse_diversity.py:421` | `evaluate_condition_replication` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 5 | `scripts/analyse_flash35_2x2.py:136` | `sweep` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 6 | `scripts/analyse_phase2_results.py:360` | `analyse_phase_results` | `bootstrap_multi_run_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 7 | `scripts/analyse_phase2_results.py:404` | `analyse_phase_results` | `bootstrap_multi_run_effect_size_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 8 | `scripts/analyse_pv_buffer_sensitivity.py:152` | `evaluate_condition_at_buffers` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 9 | `scripts/analyse_secondary_effects.py:374` | `analyse_tile_mcc` | `calculate_tile_classification` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 10 | `scripts/analyse_secondary_effects.py:375` | `analyse_tile_mcc` | `bootstrap_tile_classification_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 11 | `scripts/analyse_secondary_effects.py:596` | `analyse_thinking_temp_interaction` | `bootstrap_interaction_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 12 | `scripts/analyse_secondary_effects.py:755` | `analyse_spatial_clustering` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 13 | `scripts/analyse_secondary_effects_text.py:376` | `analyse_tile_mcc` | `calculate_tile_classification` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 14 | `scripts/analyse_secondary_effects_text.py:377` | `analyse_tile_mcc` | `bootstrap_tile_classification_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 15 | `scripts/analyse_secondary_effects_text.py:598` | `analyse_thinking_temp_interaction` | `bootstrap_interaction_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 16 | `scripts/analyse_secondary_effects_text.py:757` | `analyse_spatial_clustering` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 17 | `scripts/analyse_study_effects.py:222` | `compare_conditions` | `bootstrap_effect_size_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 18 | `scripts/analyse_study_effects.py:233` | `compare_conditions` | `bootstrap_tile_effect_size_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 19 | `scripts/analyse_verifier_robustness.py:179` | `score_cids` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 20 | `scripts/audit_tile_join_variants.py:265` | `audit_job` | `calculate_tile_classification` | historical replay path | — | already passes an explicit join (an S166 audit of the frame-wide joins) |
| 21 | `scripts/augment_per_arch_with_mcc.py:102` | `compute_mcc_for_condition` | `calculate_tile_classification` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 22 | `scripts/augment_per_arch_with_mcc.py:105` | `compute_mcc_for_condition` | `bootstrap_tile_classification_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 23 | `scripts/build_55map_leaderboard.py:492` | `main` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 24 | `scripts/build_pareto_leaderboard.py:152` | `_score_cids` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 25 | `scripts/build_pareto_leaderboard.py:256` | `main` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 26 | `scripts/build_pareto_v2.py:220` | `rung_tile_classification` | `compute_per_tile_classification` | fixed in W1 | `55737337a` | C4: two computations; both options; stamped names |
| 27 | `scripts/compare-384-vs-512.py:304` | `main` | `bootstrap_effect_size_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 28 | `scripts/compare_wbf_vs_greedy.py:130` | `main` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 29 | `scripts/compare_wbf_vs_greedy.py:142` | `main` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 30 | `scripts/compare_wbf_vs_greedy_canonical.py:252` | `main` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 31 | `scripts/compare_wbf_vs_greedy_canonical.py:256` | `main` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 32 | `scripts/compare_wbf_vs_greedy_production.py:238` | `main` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 33 | `scripts/compare_wbf_vs_greedy_production.py:242` | `main` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 34 | `scripts/compute-pairwise-effect-sizes.py:563` | `run_one_comparison` | `bootstrap_effect_size_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 35 | `scripts/compute_corrected_f1_multi_buffer.py:587` | `bootstrap_tile_level_ci` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `55737337a` | C3: both rules threaded and written to summary.json |
| 36 | `scripts/compute_corrected_f1_multi_buffer.py:655` | `compute_mcc_block` | `calculate_tile_classification` | fixed in W1 | `55737337a` | C3: both rules threaded and written to summary.json |
| 37 | `scripts/compute_corrected_f1_multi_buffer.py:656` | `compute_mcc_block` | `bootstrap_tile_classification_ci` | fixed in W1 | `55737337a` | C3: both rules threaded and written to summary.json |
| 38 | `scripts/compute_family_fdr.py:228` | `build_count_matrices` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 39 | `scripts/compute_pool_recall_ceilings.py:81` | `main` | `score_detection_set` | inherits correctly | — | compute_mcc=False: point estimates only, no table read |
| 40 | `scripts/consensus-sweep-phase3a-high-text.py:170` | `compute_single_consensus` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 41 | `scripts/consensus-sweep-phase3a-high-text.py:272` | `compute_pairwise` | `bootstrap_effect_size_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 42 | `scripts/consensus_vs_baseline_tiering.py:190` | `consensus_per_tile` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `e34a7e581` | count_table_join parameter, defaulting to the legacy rule for its importers |
| 43 | `scripts/dedup_metric_impact.py:366` | `gate_tile_confusion` | `calculate_tile_classification` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 44 | `scripts/dedup_tiering_rerun.py:154` | `per_tile_arrays` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 45 | `scripts/era1_leaderboard_tiering.py:316` | `_per_tile_one_set` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `55737337a` | two computations per cell; both options; stamped names |
| 46 | `scripts/era1_leaderboard_tiering.py:530` | `cell_per_tile_classification` | `calculate_tile_classification` | fixed in W1 | `55737337a` | two computations per cell; both options; stamped names |
| 47 | `scripts/era1_leaderboard_tiering.py:539` | `cell_per_tile_classification` | `compute_per_tile_classification` | fixed in W1 | `55737337a` | two computations per cell; both options; stamped names |
| 48 | `scripts/era1_leaderboard_tiering.py:692` | `join_sensitivity_gate` | `calculate_tile_classification` | fixed in W1 | `55737337a` | two computations per cell; both options; stamped names |
| 49 | `scripts/evaluate-pro-n10.py:284` | `main` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 50 | `scripts/evaluate-pro-n10.py:333` | `main` | `calculate_tile_classification (via evaluate_tile_mcc)` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 51 | `scripts/evaluate-pro-n10.py:336` | `main` | `bootstrap_tile_classification_ci (via evaluate_tile_mcc)` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 52 | `scripts/evaluate_detections.py:1234` | `evaluate_single_run` | `bootstrap_ci` | fixed in W1 | `55737337a` | --tile-join / --count-table-join; provenance in rows, tile block and _metadata |
| 53 | `scripts/evaluate_detections.py:1424` | `evaluate_single_run` | `calculate_tile_classification` | fixed in W1 | `55737337a` | --tile-join / --count-table-join; provenance in rows, tile block and _metadata |
| 54 | `scripts/evaluate_detections.py:1453` | `evaluate_single_run` | `bootstrap_tile_classification_ci` | fixed in W1 | `55737337a` | --tile-join / --count-table-join; provenance in rows, tile block and _metadata |
| 55 | `scripts/evaluate_pilot.py:139` | `evaluate_on_bounds` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 56 | `scripts/evaluate_pilot.py:166` | `evaluate_on_bounds` | `calculate_tile_classification` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 57 | `scripts/evaluate_pilot.py:169` | `evaluate_on_bounds` | `bootstrap_tile_classification_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 58 | `scripts/evaluate_pv_results.py:357` | `cmd_sweep` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 59 | `scripts/evaluate_pv_results.py:552` | `cmd_compare` | `bootstrap_effect_size_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 60 | `scripts/evaluate_retest_all.py:105` | `evaluate_condition` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 61 | `scripts/evaluate_retest_all.py:156` | `evaluate_multi_run_condition` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 62 | `scripts/evaluate_retest_all.py:234` | `pairwise_effect_sizes` | `bootstrap_effect_size_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 63 | `scripts/evaluate_tile_mcc.py:281` | `evaluate_mcc` | `calculate_tile_classification` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 64 | `scripts/evaluate_tile_mcc.py:286` | `evaluate_mcc` | `bootstrap_tile_classification_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 65 | `scripts/final_board_build.py:528` | `per_tile_arrays` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 66 | `scripts/final_board_posthoc_cells.py:407` | `confusion_gate` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 67 | `scripts/final_board_sweeps.py:422` | `_score` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 68 | `scripts/final_board_sweeps.py:813` | `main` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 69 | `scripts/final_board_sweeps.py:855` | `main` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 70 | `scripts/gemini37_image_55map_r2.py:476` | `per_tile_arrays` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 71 | `scripts/gemini37_image_55map_r2.py:510` | `tile_vectors` | `calculate_tile_classification` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 72 | `scripts/grid_analysis.py:254` | `score` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 73 | `scripts/grid_analysis.py:291` | `single_pass_table` | `calculate_tile_classification` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 74 | `scripts/grid_analysis.py:404` | `build_per_tile` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 75 | `scripts/grid_incumbent_rescore.py:156` | `rescore_incumbent` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 76 | `scripts/grid_verifier_analysis.py:442` | `per_tile_counts` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 77 | `scripts/h13_aggregation_sweep.py:283` | `main` | `bootstrap_ci` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 78 | `scripts/h13_overlap_analysis.py:161` | `build_per_tile` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 79 | `scripts/h6_registered_analyses.py:599` | `f1_at_20m` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 80 | `scripts/k_ladder_tension_analyses.py:239` | `per_tile_table` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 81 | `scripts/lib_advanced_metrics.py:3170` | `compute_per_tile_classification` | `calculate_tile_classification` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 82 | `scripts/lib_advanced_metrics.py:3305` | `score_detection_set` | `calculate_tile_classification` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 83 | `scripts/lib_advanced_metrics.py:3563` | `bootstrap_ci` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 84 | `scripts/lib_advanced_metrics.py:3819` | `bootstrap_effect_size_ci` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 85 | `scripts/lib_advanced_metrics.py:3823` | `bootstrap_effect_size_ci` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 86 | `scripts/lib_advanced_metrics.py:4004` | `bootstrap_multi_run_ci` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 87 | `scripts/lib_advanced_metrics.py:4117` | `bootstrap_multi_run_effect_size_ci` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 88 | `scripts/lib_advanced_metrics.py:4124` | `bootstrap_multi_run_effect_size_ci` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 89 | `scripts/lib_advanced_metrics.py:4339` | `bootstrap_interaction_ci` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 90 | `scripts/lib_advanced_metrics.py:5172` | `bootstrap_tile_classification_ci` | `calculate_tile_classification` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 91 | `scripts/lib_advanced_metrics.py:5351` | `bootstrap_tile_effect_size_ci` | `calculate_tile_classification` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 92 | `scripts/lib_advanced_metrics.py:5355` | `bootstrap_tile_effect_size_ci` | `calculate_tile_classification` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 93 | `scripts/lib_advanced_metrics.py:5612` | `generate_report` | `bootstrap_ci` | fixed in W1 | `bf7186b71` | library: the join is a parameter threaded to every leaf, recorded in each output |
| 94 | `scripts/materialise_vr_condition_sets.py:125` | `f1_of` | `score_detection_set` | inherits correctly | — | compute_mcc=False: point estimates only, no table read |
| 95 | `scripts/mcc_tiering_55map.py:183` | `tile_vectors` | `calculate_tile_classification` | fixed in W1 | `55737337a` | --tile-join; record validated under its own join first |
| 96 | `scripts/n1_baseline_leaderboard_tiering.py:296` | `pass_averaged_per_tile` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 97 | `scripts/paired_mcc_permutation.py:296` | `aggregate_confusion` | `compute_per_tile_classification` | fixed in W1 | `55737337a` | C4: references validated under their own join, then requested |
| 98 | `scripts/paired_permutation_consensus.py:298` | `run_comparison` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 99 | `scripts/paired_permutation_consensus.py:302` | `run_comparison` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 100 | `scripts/paired_permutation_corrected_55maps.py:212` | `get_per_tile_counts` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 101 | `scripts/pairwise_permutation_test.py:348` | `run_permutation_test` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `55737337a` | C4: tile_join / count_table_join parameters, recorded; CLI option |
| 102 | `scripts/pairwise_permutation_test.py:351` | `run_permutation_test` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `55737337a` | C4: tile_join / count_table_join parameters, recorded; CLI option |
| 103 | `scripts/pairwise_permutation_test.py:715` | `run_permutation_test_mcc` | `compute_per_tile_classification` | fixed in W1 | `55737337a` | C4: tile_join / count_table_join parameters, recorded; CLI option |
| 104 | `scripts/pairwise_permutation_test.py:716` | `run_permutation_test_mcc` | `compute_per_tile_classification` | fixed in W1 | `55737337a` | C4: tile_join / count_table_join parameters, recorded; CLI option |
| 105 | `scripts/permutation_opmax_vs_headline.py:115` | `materialise_opmax` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 106 | `scripts/permutation_opmax_vs_headline.py:147` | `verify_headline` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 107 | `scripts/repair_bootstrap_cis.py:178` | `bootstrap_ci_percentile` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 108 | `scripts/rescore_tile_mcc_e81.py:310` | `recompute_cell` | `calculate_tile_classification` | fixed in W1 | `55737337a` | C2: each record's own join passed to both calls |
| 109 | `scripts/rescore_tile_mcc_e81.py:311` | `recompute_cell` | `bootstrap_tile_classification_ci` | fixed in W1 | `55737337a` | C2: each record's own join passed to both calls |
| 110 | `scripts/score_high_thinking_prior.py:79` | `score` | `score_detection_set` | inherits correctly | — | compute_mcc=False: point estimates only, no table read |
| 111 | `scripts/score_min11_uplift.py:62` | `per_tile` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 112 | `scripts/score_min11_uplift.py:97` | `main` | `score_detection_set` | inherits correctly | — | compute_mcc=False: point estimates only, no table read |
| 113 | `scripts/score_min11_uplift.py:108` | `main` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 114 | `scripts/score_min_thinking_pv.py:109` | `sweep` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 115 | `scripts/score_nof10_comparison.py:62` | `score` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 116 | `scripts/score_pro_pv.py:87` | `score` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 117 | `scripts/score_zero_diversity_anchor.py:107` | `main` | `score_detection_set` | inherits correctly | — | compute_mcc=False: point estimates only, no table read |
| 118 | `scripts/score_zero_diversity_anchor.py:125` | `main` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 119 | `scripts/selection_aware_intervals.py:159` | `build_candidate_tile_counts` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `55737337a` | both options; board MCC from the classification arm |
| 120 | `scripts/selection_aware_intervals.py:174` | `build_candidate_tile_counts` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `55737337a` | both options; board MCC from the classification arm |
| 121 | `scripts/selection_aware_intervals.py:744` | `build_sweep_tile_counts` | `compute_per_tile_tp_fp_fn` | fixed in W1 | `55737337a` | both options; board MCC from the classification arm |
| 122 | `scripts/stride_verifier_analysis.py:226` | `score_at` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 123 | `scripts/student_ranking_significance.py:93` | `per_tile` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 124 | `scripts/sweep_unswept_pools.py:418` | `sweep_cell` | `score_detection_set` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 125 | `scripts/sweep_unswept_pools.py:436` | `sweep_cell` | `score_detection_set` | inherits correctly | — | compute_mcc=False: point estimates only, no table read |
| 126 | `scripts/test-prompt-engineering-effects.py:71` | `run_permutation_test` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 127 | `scripts/test-prompt-engineering-effects.py:74` | `run_permutation_test` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 128 | `scripts/test_gtfree_selection.py:183` | `main` | `score_detection_set` | inherits correctly | — | compute_mcc=False: point estimates only, no table read |
| 129 | `scripts/tier_verifier_matrix.py:88` | `_score` | `score_detection_set` | inherits correctly | — | compute_mcc=False: point estimates only, no table read |
| 130 | `scripts/validate_first5_of10_derivation.py:131` | `sweep` | `score_detection_set` | inherits correctly | — | compute_mcc=False: point estimates only, no table read |
| 131 | `scripts/verify_phase2a_metrics.py:349` | `per_tile_decomposition` | `compute_per_tile_tp_fp_fn` | deferred to Wave 2/3, pinned to legacy | `e34a7e581` | `tile_join=TILE_JOIN_LEGACY_COUNT_TABLE` |

## Second-order consumers (wrappers in W1-fixed modules)

Tier 1 found a route the AST inventory could not see:
`final_board_sweeps.tile_confusion` calls `mcc_tiering_55map.tile_vectors`,
a wrapper whose default moved with the library's. An AST scan of `scripts/`
for calls to every W1-fixed wrapper whose default moved found 23 calls in
15 files, none passing a join. Each is pinned to the legacy
rule exactly as the direct consumers are (commit `da589eb27`).

| # | Call site (line before the pin) | Wrapper called | Disposition | Commit | Keywords added |
|---:|---|---|---|---|---|
| 1 | `scripts/analyse_null_exemplar_sensitivity.py:743` | `era1_leaderboard_tiering.cell_per_tile` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 2 | `scripts/analyse_null_exemplar_sensitivity.py:748` | `era1_leaderboard_tiering.cell_per_tile_classification` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 3 | `scripts/build_cross_architecture_tables.py:389` | `pairwise_permutation_test.run_permutation_test_mcc` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 4 | `scripts/build_cross_architecture_tables.py:397` | `pairwise_permutation_test.run_permutation_test` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 5 | `scripts/build_tiered_leaderboard.py:730` | `evaluate_detections.evaluate_single_run` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION, count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 6 | `scripts/build_tiered_leaderboard.py:1240` | `pairwise_permutation_test.run_permutation_test_mcc` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 7 | `scripts/build_tiered_leaderboard.py:1260` | `pairwise_permutation_test.run_permutation_test` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 8 | `scripts/build_tiered_leaderboard.py:1444` | `pairwise_permutation_test.run_permutation_test_mcc` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 9 | `scripts/build_tiered_leaderboard.py:1471` | `pairwise_permutation_test.run_permutation_test` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 10 | `scripts/compare_wbf_greedy_pv_permutation.py:187` | `pairwise_permutation_test.run_permutation_test` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 11 | `scripts/compare_wbf_vs_greedy.py:166` | `pairwise_permutation_test.run_permutation_test` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 12 | `scripts/compare_wbf_vs_greedy_canonical.py:270` | `pairwise_permutation_test.run_permutation_test` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 13 | `scripts/compare_wbf_vs_greedy_production.py:265` | `pairwise_permutation_test.run_permutation_test` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 14 | `scripts/dedup_tiering_rerun.py:437` | `mcc_tiering_55map.tile_vectors` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 15 | `scripts/dedup_tiering_rerun.py:462` | `mcc_tiering_55map.tile_vectors` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 16 | `scripts/dedup_tiering_rerun.py:600` | `era1_leaderboard_tiering.load_cells` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION, count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 17 | `scripts/final_board_sweeps.py:409` | `mcc_tiering_55map.tile_vectors` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |
| 18 | `scripts/resweep_pv_on_h10.py:132` | `evaluate_detections.evaluate_single_run` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION, count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 19 | `scripts/run_pairwise_tests.py:857` | `pairwise_permutation_test.run_permutation_test` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 20 | `scripts/run_verifier_t_stage_b.py:199` | `evaluate_detections._evaluate_condition` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION, count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 21 | `scripts/score_55maps_extended_gt_canonical.py:161` | `compute_corrected_f1_multi_buffer.run` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION, count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 22 | `scripts/score_55maps_standardised_reference.py:331` | `compute_corrected_f1_multi_buffer.run` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION, count_table_join=TILE_JOIN_LEGACY_COUNT_TABLE` |
| 23 | `scripts/stride55_sweep_oracle.py:212` | `mcc_tiering_55map.tile_vectors` | deferred to Wave 2/3, pinned to legacy | `da589eb27` | `tile_join=TILE_JOIN_LEGACY_CLASSIFICATION` |

## Subprocess launchers of the W1-fixed command-line tools

**Disposition: pinned to history.** A **main-session decision (2026-11-19,
pending the PI's confirmation)**, with which Astra agrees in her interim
review (`~/agent-mail/codex/outbox/claude/20261118T134744Z-astra-wave1-interim-provenance.md`:
historical launchers "should be pinned to their recorded rules, or refuse
until explicitly migrated"; restated in her full review). Every launcher
that re-scores or replays committed artefacts now names its rules on the
command line, so running one reproduces history and cannot re-score under
the new defaults outside Wave 2's gates. Wave 2's corpus driver is the only
sanctioned route to the new rules. Commit `bbeb2a5ad`; the tier-1 test
`tests/test_tile_join_wave1_audit.py` (`test_pinned_launchers_name_the_legacy_rules`
and its two siblings) fails if a pin is removed.

| Launcher | Tool it launches | Pin |
|---|---|---|
| `scripts/build_gs_era2_board_opmax.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` (`id`/`id`) |
| `scripts/build_k1_gapfill_worklist.py` | `evaluate_detections.py`, `compute_corrected_f1_multi_buffer.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/build_verifier_pairing_worklist.py` | both, as above | `*LEGACY_JOIN_FLAGS` |
| `scripts/grid_materialise_conditions.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/grid_verifier_analysis.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/r2_score_cells.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/recovery_reeval.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/register_pass1_materialise.py` | both | `*LEGACY_JOIN_FLAGS` |
| `scripts/rescore_conditions.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/run_era1_pv_stage_d.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/run_generalisation.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/run_k_ladder_tier_e.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/score_k_ladder_phase2_rungs.py` | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/tier_e_ladder_tiering.py` | `era1_leaderboard_tiering.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/rerun_bca_corpus.py` | `evaluate_detections.py` (replays a record) | `*recorded_join_flags(doc)`: the record's own rules |
| `scripts/rerun_evals_at_10k.py` | `evaluate_detections.py` (replays a record) | `*recorded_join_flags(doc)` |
| `scripts/analyse_null_exemplar_sensitivity.py` | `evaluate_detections.py` | `--tile-join id --count-table-join id` (`06fd89ffb`) |
| `scripts/run_bootstrap_10k.py` (audit A-M3) | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/stride55_score.py` (audit A-M3) | `compute_corrected_f1_multi_buffer.py` | `*LEGACY_JOIN_FLAGS` |
| `scripts/score-unscored-conditions-2026-05-30.sh` (audit A-M3; a shell script, missed by the `.py`-only search) | `evaluate_detections.py` | `--tile-join id --count-table-join id` in `EVAL` |
| `scripts/build_gs_era2_board.py` (writes a jobs script; found by the fix round's static scan) | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` in `_eval_command` |
| `scripts/gemini37_image_55map_r2.py` (re-scores cells in place; found by the fix round's static scan) | `evaluate_detections.py` | `*LEGACY_JOIN_FLAGS` in `engine_command` |

`LEGACY_JOIN_FLAGS` and `recorded_join_flags` are defined in
`scripts/lib_advanced_metrics.py`. The first version of this section judged
two scripts to "mention a tool only in prose"; one of them,
`gemini37_image_55map_r2.py`, in fact launches `evaluate_detections.py`
through `subprocess.run` and overwrites the evaluations on disk, and
`build_gs_era2_board.py` writes a jobs script of evaluator commands. Both
are now pinned. A tier-1 scan (`test_every_launcher_names_its_rules` in
`tests/test_tile_join_wave1_audit.py`) parses every `scripts/*.py` and
fails if a string literal naming a W1-fixed tool sits in a file with no
pin, unless the file is on an allow-list with its reason:
`dedup_tiering_rerun.py` and `register_pass1_adapt.py` record a tool's
path as provenance metadata and launch nothing. `migrate_ci_flag_basis.py`
runs only `git` and names the evaluator in prose.
Frozen evidence scripts outside `scripts/` stay tied to the revision their
records name (above); they are not edited.

A launcher that produces NEW work (not a re-score of a committed artefact)
may select the corrected rules explicitly once Wave 2's specification says
so, with its own disposition. None is changed to do so in Wave 1.

### Shell launchers (re-audit RA-M4)

The `*.py`-only launcher scan missed thirteen shell scripts that run
`scripts/evaluate_detections.py` without a join flag, so each would have
re-scored under the sheet joins. Commit `e44cfaf2d` pins every one to the
legacy rules (`--tile-join id --count-table-join id`), and the tier-1
launcher scan now covers `*.sh` as well:

- `55maps-image-recovery.sh`, `55maps-t0.3-recovery.sh`,
  `55maps-t0.7-recovery.sh`, `55maps-text-min-recovery.sh`;
- `gs-v2-t0.7-recovery.sh`;
- `run_phase3a_image_analysis.sh`, `run_phase3a_mcc_sweep.sh`,
  `run_phase3a_text_analysis.sh`;
- `run_second_wave_evals.sh`, `run_sweep_promotion_evals.sh`,
  `run_vr_registration_evals.sh`;
- `session-78-matrix-overnight.sh`, `session-78-matrix-rerun-phases-bcd.sh`.

Disposition: historical replay path, pinned (the same main-session
decision as the other launchers, pending the PI). The audit record is
`g1-audit.md` § 8.1.

## Changelog

### 2026-11-19 — Shell launchers added (re-audit RA-M4)

The thirteen shell launchers pinned in `e44cfaf2d` are listed under the
subprocess-launcher section. No earlier disposition changed.

### 2026-11-19 — G1 audit fix round

Trigger: the G1 item 9 audit (lens A finding A-M3: three launchers missing
from this file) and the main session's decision, with Astra's agreement, to
pin every in-place re-scoring launcher to its recorded rules. Changes: the
launcher section is rewritten from "inherits the corrected default; open
item" to "pinned to history" (commit `bbeb2a5ad`), adding
`run_bootstrap_10k.py`, `stride55_score.py` and
`score-unscored-conditions-2026-05-30.sh`, and two launchers the first
version had misjudged as prose-only mentions, `build_gs_era2_board.py` and
`gemini37_image_55map_r2.py` (both pinned in this round), with a tier-1
static scan for any further one. The per-site tables (direct and second-order) are
unchanged. The full audit record is `g1-audit.md` beside this file.

### 2026-11-18 — Original publication

First version, written by the Wave 1 code agent after commit `a7989c47f` on
`tile-join-wave-1`. Covers Astra's 129-call inventory at `e92d1c5d7` and the
two re-exported calls in `scripts/evaluate-pro-n10.py`; the 23
second-order calls to W1-fixed wrappers pinned in `da589eb27`; the
subprocess launchers; and lists the evidence scripts outside `scripts/`
without changing them.
