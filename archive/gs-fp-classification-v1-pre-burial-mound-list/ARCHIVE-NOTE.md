# Archive note — GS FP-classification v1 (pre-burial-mound closed list)

## Why this directory was archived

This directory holds the v1 outputs of the gold-standard (GS) FP-class
classification driver (commits `6037b390` + `ee4f18cb`, 2026-04-29). It was
superseded the same day by v2, which expanded the closed-list categories to
include burial-mound classes — see the v2 commit referenced below.

## What changed between v1 and v2

The v1 closed-list — copied verbatim from the 55-map sibling driver
(`scripts/55maps-fp-classify.py`) — was designed for FP-only
classification. It contained: `number, benchmark, water-feature,
contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid,
none, other`. There is no `burial-mound` category.

When the same script was repurposed to classify all 371 GS detections
(true positives (TPs) and false positives (FPs) together — see
`archive/planning-completed-session-81-82/gs-fp-classification-plan-2026-04-29.md` §6.5 for the TP-side
reliability rationale), real mounds had no proper category to assign. The
v1 TP-side fell back to visual-similarity proxies: `contour-ring` 60.0 %
and `number` 15.2 %, failing the > 10 % vocabulary-leakage warning the
script itself raised. This was a script-design issue (closed list scoped
for FP-only on the 55-map corpus), not a classifier hallucination.

Soviet 1:50,000 topographic-map legends DO have burial-mound symbols:
`burial-mound`, `benchmark-on-burial-mound`,
`triangulation-point-on-burial-mound`, `settlement-mound`. Omitting them
forced misclassification of correctly-detected mounds. v2 adds these four
categories so the closed list correctly covers TP+FP scope.

## v2 location and reference

- v2 outputs: `results/gs-fp-classification/`
- v2 commit: see `data(gs-fp-classification): re-run with burial-mound
  categories added to closed list` (2026-04-29)
- Planning context: `archive/planning-completed-session-81-82/gs-fp-classification-plan-2026-04-29.md`
  §2 (framing), §6.5 (TP-side reporting expectation)

## v1 result snapshot (preserved here for cross-version comparison)

- Total classified: 371 / 371
- TP-side `contour-ring`: 213 / 355 = 60.0 % (vocabulary leakage)
- TP-side `number`: 54 / 355 = 15.2 %
- TP-side `none` + `other`: 0.8 % (calibration sanity check failed under
  v1's closed list — but the v1 list could not produce the correct
  answer; the failure is the closed list, not the classifier)
- FP-side at the >50 m primary threshold (n = 16): `number` 25.0 %,
  `benchmark` 25.0 %, `water-feature` 12.5 %, `contour-ring` 12.5 %,
  `settlement` 12.5 %
- Cross-corpus chi-square (Monte Carlo) p-value at >50 m: 0.0107

The v1 FP-side numbers are still informative as a sensitivity check on
the FP-only profile, since the burial-mound categories should rarely be
chosen for FPs on the FP-side anyway. The v2 FP-side row is the
authoritative one for the paper.
