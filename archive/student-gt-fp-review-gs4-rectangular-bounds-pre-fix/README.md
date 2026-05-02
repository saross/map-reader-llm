# Student GT FP Review — 4 GS Maps (Rectangular Bounds, Pre-Fix)

Forensic provenance for the manual false-positive review pass run under
the rectangular TIFF-bounds protocol on the four gold-standard (GS) map
sheets, before the trapezoidal-graticule active-area correction at
commit `0bb7c448` superseded the rectangular analysis.

## Contents

- `fp-candidates.csv` — the 17 unmatched student features identified by
  `scripts/review_student_fp_candidates.py` (Hungarian one-to-one match
  at 50 m radius) under the rectangular-bounds inputs.
- `fp-decisions.csv` — the manual-review decisions captured via the
  Streamlit reviewer (`scripts/launch_gs4maps_fp_review.sh`). All 17
  candidates were marked "uncertain" — the review never resolved them
  to a category because, on inspection in-app, every candidate sat in
  the black corners of the rectangular TIFFs, outside the true active
  map area.

## Why preserved

The rectangular-bounds analysis was the trigger that surfaced the
artefact: a 3.06 % student FP rate inconsistent with both Shawn's prior
expert recall (~1 genuine non-mound) and Sobotkova et al. (2023)'s
0.1 % published figure. The follow-up — clipping the active map area
to the trapezoidal graticule rather than the rectangular raster — drove
the FP count from 17 to 0 and reconciled the analysis with the
published baseline (see Obs 316 and Obs 317 in
`docs/notes/reflections/working-notes.md`).

These CSVs are kept as the audit trail of the review pass that ran
before the correction: they document the candidates inspected and the
"uncertain" pattern that prompted the deeper investigation. Deleting
them would erase the methodological breadcrumbs that explain why the
trapezoidal correction was made, even though both files are now
operationally obsolete.

## Pointers

- **Trapezoidal correction commit**: `0bb7c448`
  (`analysis(gs-4maps): correct FP via trapezoidal graticule bounds`).
- **Analogous archived analysis**:
  `archive/student-gt-fn-rate-analysis-gs4-rectangular-bounds-pre-fix/`
  (the per-sheet FN/FP confusion-matrix outputs from the same
  rectangular-bounds run).
- **Working-notes context**: Obs 316 (trapezoidal correction
  vindicates Sobotkova 2023) and Obs 317 (4-GS-vs-55-map gap explained
  by variance) in `docs/notes/reflections/working-notes.md`.
- **Producing scripts**: `scripts/launch_gs4maps_fp_review.sh` and
  `scripts/review_student_fp_candidates.py` (now flagged as
  historical / superseded in their header docstrings).

Per project policy: archive, never delete. These artefacts are forensic
provenance, not active outputs.
