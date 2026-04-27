# `with-mcc/` archived (off-matrix one-offs)

This directory's contents have been archived to
`archive/with-mcc-pre-2026-04-27-off-matrix/image/` because they were off-matrix
one-offs (see Obs 288 in `docs/notes/reflections/working-notes.md`).

The canonical post-Wave-2 phase3a tile-level Matthews Correlation Coefficient
(MCC) source is `results/phase3a-image-matrix/<cell>/evaluation.{json,md,csv}`.

## Why this was archived

The pre-existing `with-mcc/` reference cells were hand-rolled smoke-test
artefacts produced during Session 78 by ad-hoc invocations of
`evaluate_detections.py` against whichever consensus geojson was nearby at the
time, NOT against the canonical matrix consensus sources. Wave 2 of Session 80
(commit `163161a4`, 2026-04-27) replaced these with the matrix-canonical 252-cell
sweep. Cross-checking the with-mcc image reference cell against the new sweep
revealed it had been built against the **MINIMAL track's consensus pool by
mistake** — a stratum mis-assignment, not just a source-asymmetry.

The off-matrix MCC value in the archived reference (0.3831) is therefore not
canonical truth for the image high-T0.7 K=10 t=7 cell. The canonical matrix
value is **MCC = 0.6765 [0.6083, 0.7400]** at
`results/phase3a-image-matrix/high-t0.7/n10/high-t0-7-7of10/evaluation.json`.

This is a +0.29 absolute MCC correction (0.3831 → 0.6765) — any prior framing
that "the image high-T0.7 cell is MCC-poor" was an artefact of the wrong
consensus source and should be redirected to the canonical matrix value.

## See also

- Obs 288 (full forensic): `docs/notes/reflections/working-notes.md`.
- Wave 2 sweep: `scripts/run_phase3a_mcc_sweep.sh` + `scripts/build_phase3a_mcc_jobs.py`.
