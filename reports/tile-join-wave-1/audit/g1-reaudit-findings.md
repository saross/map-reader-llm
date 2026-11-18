# Fresh re-audit of the fix round `f6f5ffe54..0549672ec` (Claude Opus, 2026-11-19)

> Copied from the S169 main session's scratchpad on 2026-11-19, so that `g1-audit.md` and the mail record have a durable source. Unchanged except for this note.

Evidence is on zbook: `~/scratch/wave1/reaudit` (frozen copy),
`reaudit-probe/tests/test_reaudit_probes.py` (probes P1–P9), `reaudit-mut`
(mutants), and `reaudit-run` (real-board replays). Step 1 replayed about 600
real registered cells under (sheet-contains, sheet-primary) with no false
stop except RA-C1. No symbol-level F1/P/R change was found.

## Critical

- **RA-C1 (a false stop on a committed board; executed).**
  `era1_leaderboard_tiering.py:1035` rounds the replay MCC to 6 dp before
  comparing it with the recorded 4-dp value at `MCC_GATE_TOL = 5e-5`
  (`:228`).
  - The cell `retest-phase3a-high::text-high-t0.3-n5-4of5` (confusion
    175/88/48/29, which reproduces) has true MCC 0.5206504316, recorded
    as 0.5207. The validator compares 0.520650 with 0.5207, a difference
    of 5.0000000000105e-05, which is greater than the tolerance.
  - Under (sheet-contains, id) and (geometric-contains, id), the analysis
    `phase3a-high-consensus-calibration` raises `ReproductionDriftError`
    and the whole board stops. Under (id, id) the MCC is withheld, a
    pre-existing false gate.
  - Fix: compare the unrounded value, or `round(mcc, 4) == recorded`.
    Add a regression test with this exact cell.
- **RA-C2.** `tier_e_ladder_tiering.py:282` now passes
  `*LEGACY_JOIN_FLAGS`, so era1 writes `tiering_20m_id_ct-id`
  (`tiering_stem`), but `:297` reads the committed `tiering_20m.json`. The
  launcher therefore summarises a stale file, and `--n-permutations` and
  `--seed` never reach its output. Make the launcher read the stem that
  era1 actually wrote, and add a test that runs it end to end, or asserts
  read path equals write path.
- **RA-C3** is the same as Astra's R2-5 (`stride55_score.py:37` import
  before path setup; `--help` gives `ModuleNotFoundError`). Already in
  your list.

## Medium

- **RA-M1.** `era1_leaderboard_tiering.py:1281-1286`:
  `TILE_JOIN_REFUSAL_CODES` omits `TILE_JOIN_REASON_UNATTRIBUTED_REFERENCE`,
  so `is_tile_join_refusal` (`:1306`) misses it, and a board with a blank
  in-frame reference sheet raises out of `load_cells` (`:1704`) instead of
  withholding (the 2026-09-13 ruling: withhold and list). `refusal_code()`
  returns None, so there is a generic raise at `:1201`, and
  `expected_refusals_from` raises "no refusal code" (probe P1). This is
  latent today: no committed reference has a blank sheet.
- **RA-M2.** `evaluate_detections.py:1268-1279` formats
  `shortfall["n_booked"]` and `["n_inside_union"]` with `%d`, but the
  reference-refusal describer (`lib_advanced_metrics.py:5959-5968`) sets
  them to None. That raises `TypeError` under pytest. In production it
  prints a logging Traceback, which `scripts/wait_for_run.py:69` classifies
  as **crashed** (exit 3) (probe P7). Add an evaluator-level test for the
  reference refusal.
- **RA-M3.** `era1_leaderboard_tiering.py:1673`
  (`if recorded_ct != count_table_join:`): the recorded F1 arm is not
  validated when only the classification join changes (absent treated as
  agreement). A record whose F1 does not reproduce passes under
  (sheet-contains, id) (probe P8). Validate every applicable recorded arm
  always (this overlaps R2-2).
- **RA-M4.** Thirteen shell launchers run `evaluate_detections.py`
  unpinned:
  - `55maps-image-recovery.sh:147`
  - `55maps-t0.3-recovery.sh:143`
  - `55maps-t0.7-recovery.sh:140`
  - `55maps-text-min-recovery.sh:148`
  - `gs-v2-t0.7-recovery.sh:171`
  - `run_phase3a_image_analysis.sh:24`
  - `run_phase3a_mcc_sweep.sh:36`
  - `run_phase3a_text_analysis.sh:23`
  - `run_second_wave_evals.sh:34`
  - `run_sweep_promotion_evals.sh:45`
  - `run_vr_registration_evals.sh:45`
  - `session-78-matrix-overnight.sh:360`
  - `session-78-matrix-rerun-phases-bcd.sh:261`

  `test_every_launcher_names_its_rules` scans `*.py` only. Pin them (pass
  `--tile-join id --count-table-join id`), extend the scan to `*.sh`, and
  update `consumer-dispositions.md`.
- **RA-M5.** `expected_refusals_from` (`:1049-1072`) accepts any
  `{ref: code}` or any tiering's `withheld_cells`, without checking the
  tiering's `analysis_id`, its `tile_joins`, or each entry's
  `count_table_join` (probe P2). Check them, and test it: the mutants
  `cls_expected_any` and `ct_expected_any` survive.
- **RA-M6.** The AST scan covers 13 library functions but not
  `evaluate_single_run`, `run_permutation_test*`, or `compute_at_buffer`,
  so the 23 second-order pins are unguarded (for example
  `resweep_pv_on_h10.py:136-140`; mutant `resweep_unpin` survives). Extend
  the scan.

## Low (the absent-as-agreement class)

- **`verify_input_identity`** (`:1112-1123`) returns `verified` when the
  hashed file is not the one the harness reads (P3), and `verified` with
  `n_files` 0 when every hash is null (P3b). Assert that the detections
  read are among the hashed inputs, and that `n_files` > 0.
- **`recorded_output_joins`** (`:253`) takes the first non-empty field and
  never checks for contradictions (P4; mutant `output_joins_ignore_mcc`
  survives). Mirror `k_ladder_mcb.tiering_joins` after A-L7.
- **`_reproduce_refused_cell`** (`:1251`) compares nothing and records no
  marker when no buffer row exists at the requested buffer. It returns
  `{}` (P5). The caller route has no refusal-count check. Make the absence
  explicit, or fatal.
- **`mcc_tiering_55map._track2_recorded_join`** (`:309`) defaults to
  `id` with no new-writer gate, and `compute_corrected_f1_multi_buffer`
  still writes `"version": "1.0.0"`. Bump the version and gate on it. The
  overwrite guard at `:514` also treats absent as `id`.
- **`k_ladder_mcc_test.py:616-632`** is the same as Astra's R2-4. Already
  in your list.
- **Replicate-mean cells** are checked on refusal status only. The same
  as R2-3; already in your list.
- **A stale allow-list entry** at `tests/test_tile_join_wave1_audit.py:537`
  (`generate_report` inside `lib_advanced_metrics.py`) matches no call.
  Remove it.
- **`rerun_evals_at_10k.py:54`** imports before `sys.path.insert` (`:57`).
  The same class as R2-5; fix it, and include it in the standalone-launch
  check.
- **(sheet-\*, id) over-withholds** at `evaluate_detections.py:1258`
  (`probe_join`). It is a pair that never existed historically. Document
  it, or fix it.
- **Pre-existing, not from this fix (for the PI; do not change symbol
  matching):** symbol-level matching silently drops a blank-sheet
  reference. With one null `Map`, the perfect detector gives F1 0.8889
  (P7). Record it in `g1-audit.md` as a pre-existing observation. No
  committed reference has a blank sheet.

## Surviving mutants to kill

- `scope_check_off` (era1 `:919`)
- `refused_shortfall_off` (`:1261`)
- `refused_shortfall_ignored` (`:1268`)
- `cls_expected_any` (`:1011`)
- `ct_expected_any` (`:1190`)
- `output_joins_ignore_mcc` (`:253`)
- `ref_partition_double` (lib `:3576`: the partition values are wrong, but
  the assert still holds)
- `mcc55_none_first` (`mcc_tiering_55map` `:652`)
- `resweep_unpin`

The harness and mutant definitions are in `~/scratch/wave1/reaudit-mut`.
