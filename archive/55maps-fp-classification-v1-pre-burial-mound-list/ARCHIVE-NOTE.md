# Archive note — 55-map FP-classification v1 (pre-burial-mound closed list)

## Why this directory was archived

This directory holds the v1 outputs of the 55-map FP-class classification
driver (commits prior to 2026-04-29). It was superseded on 2026-04-29 by
v2, which expanded the closed-list categories to include burial-mound
classes for cross-corpus consistency with the parallel gold-standard (GS)
re-run — see the v2 commit referenced below.

## What changed between v1 and v2

The v1 closed list was scoped for FP-only classification and contained:
`number, benchmark, water-feature, contour-ring, vegetation, settlement,
road-or-track, scale-bar-or-grid, none, other`. There was no
`burial-mound` category.

The 55-map classification analysis is, strictly, FP-only by design — its
input is rows in the four corrected review CSVs filtered by
`human_label == "not_mound"`, i.e., human-confirmed non-mounds. The v1
list was therefore defensible for this corpus alone.

However, the parallel GS re-run on 2026-04-29 expanded its closed list
to include the four Soviet 1980s burial-mound symbols
(`burial-mound`, `benchmark-on-burial-mound`,
`triangulation-point-on-burial-mound`, `settlement-mound`) so the GS
true-positive (TP) side could classify real mounds. v2 mirrors that
closed list verbatim on the 55-map side so cross-corpus comparisons in
the paper draw on identical category sets.

If any FPs reclassify as `burial-mound` under v2, that itself is
informative — it would indicate review-pass false-FP labels (real
mounds accidentally clicked "not_mound") rather than a flaw in v1's
scoping decision. The v2 report includes a v1-vs-v2 comparison row
specifically for this finding.

## v2 location and reference

- v2 outputs: `results/55maps-fp-classification/`
- v2 commit: see `data(55maps-fp-classification): re-run with
  burial-mound categories added to closed list` (2026-04-29)
- Parallel GS context: `archive/gs-fp-classification-v1-pre-burial-mound-list/ARCHIVE-NOTE.md`

## v1 result snapshot (preserved here for cross-version comparison)

- Total classified: 1,119 / 1,119 (no failures)
- Wall-clock: 653.6 s (~10.9 min); estimated cost: $0.5071 USD (flex tier)
- Aggregate top-3 categories: `contour-ring` 40.9 %, `number` 19.1 %,
  `settlement` 14.0 %
- Distractor-pull (`number` + `benchmark`) shares: text-track aggregate
  22.7 %, image 27.6 %
- Chi-square (image vs text-track) p = 0.1474 (n.s.); v1 verdict on
  Shawn's hypothesis: NOT SUPPORTED

The v1 distribution is the FP-only baseline against which v2 is
compared in the v2 report's "Methodology change" and v1-vs-v2
comparison sections.
