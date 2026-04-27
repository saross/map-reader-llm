# `with-mcc/` archived (off-matrix one-offs)

This directory's contents have been archived to
`archive/with-mcc-pre-2026-04-27-off-matrix/text/` because they were off-matrix
one-offs (see Obs 288 in `docs/notes/reflections/working-notes.md`).

The canonical post-Wave-2 phase3a tile-level Matthews Correlation Coefficient
(MCC) source is `results/phase3a-text-matrix/<cell>/evaluation.{json,md,csv}`.

## Why this was archived

The pre-existing `with-mcc/` reference cells were hand-rolled smoke-test
artefacts produced during Session 78 by ad-hoc invocations of
`evaluate_detections.py` against whichever consensus geojson was nearby at the
time, NOT against the canonical matrix consensus sources. Wave 2 of Session 80
(commit `163161a4`, 2026-04-27) replaced these with the matrix-canonical 252-cell
sweep. Cross-checking the with-mcc text reference cell against the new sweep
revealed it had been built against a different consensus pool
(`outputs/retest/phase3a-high/track2-text/T0.7/consensus/consensus_t26.geojson`,
376 features) than the matrix sweep
(`outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/consensus/consensus_t26.geojson`,
415 features).

The off-matrix MCC value in the archived reference (0.7153) is therefore not
canonical truth for the text high-T0.7 K=30 t=26 cell. The canonical matrix
value is **MCC = 0.6198 [0.5489, 0.6906]** at
`results/phase3a-text-matrix/high-t0.7/n30/high-t0-7-26of30/evaluation.json`.

## See also

- Obs 288 (full forensic): `docs/notes/reflections/working-notes.md`.
- Wave 2 sweep: `scripts/run_phase3a_mcc_sweep.sh` + `scripts/build_phase3a_mcc_jobs.py`.
