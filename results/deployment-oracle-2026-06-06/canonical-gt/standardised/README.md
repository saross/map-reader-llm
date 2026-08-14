# Standardised 55-map reference — ruling-21 application

> **Last revised**: 2026-08-14 (initial materialisation). See
> [§ Changelog](#changelog) for revision history.

**This is a best-possible reference, NOT a gold standard** (ruling
21b). Mounds that both the students and every model missed are not
economically recoverable without a fresh survey of the map sheets, so
they are absent from this reference entirely. Treat every recall and
F1 computed against it accordingly (see § Known biases).

Produced by `scripts/materialise_standardised_reference.py` from the
PI-ratified instruction set
(`../ruling21-instructions.csv`, spec
`planning/ruling21-application-spec.md`). The source campaign layers
are unchanged; regenerate by re-running the script.

## Layers

| File | Records | What it is |
|------|---------|------------|
| `student-mounds-55maps-standardised.geojson` | 4731 | Student digitisation, standardised: 4,746 − 4 FP − 1 contradicted merge − 12 duplicates + 2 restored pre-merge originals |
| `extension-mounds-standardised.csv` | 279 | Confirmed mounds the students missed: 278 model-detected survivors (of 773 reviewed) + 1 marking-pass extra, all at marked centres |

## Confidence grades (student layer)

| Grade | Records | Meaning | Positional quality |
|-------|---------|---------|--------------------|
| `directly_reviewed` | 527 | Opened as a queue item and adjudicated | marked centre, ±2.5 m |
| `proxy_confirmed` | 114 | Confirmed as a claimed partner from a reviewed mark; position inherited from the claimant's mark | marked centre, ±2.5 m |
| `out_of_scope` | 4090 | Never examined (ruling 21c boundary) | as digitised: median 8.6 m, p90 18.3 m, max 30.0 m from the true centre (measured on the 89-item jitter sample) |

Every extension record is `directly_reviewed`.

## Known biases (Obs 396; both directions must travel together)

- **Deflation**: an estimated ~370 residual long-range duplicates
  (95% CI ≈ 200–660, hard ceiling 549) remain among the out-of-scope
  records — attractor-displaced second records of mounds 72–100 m
  away. They deflate measured recall ~7% and measured F1 by ≈ 0.03
  at a balanced ~0.85 operating point, rank-preserving to first
  order. A displaced detection can match a displaced ghost record,
  which differentially favours attractor-susceptible configurations.
- **Inflation**: joint student+model false negatives are absent from
  the reference (Obs 361): measured recall is inflated ≈ +2.4–2.7%,
  F1 ≈ +0.011–0.012 absolute.
- **Net at point estimates ≈ −0.017**: measured F1 modestly
  understates true performance; the intervals span near-zero.

## Mixed provenance (a documented property, not an oversight)

Ruling 21(c) scoped marking to the reviewed subset. Positions are
therefore mixed: 641
student records and all 279 extension records carry marked
centres (±2.5 m); the 4090 out-of-scope
student records keep their as-digitised positions (jitter figures
above). The `std_position_source` field states each record's source.

## Replaces

The pre-standardisation pairing of
`inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
(4,746) with `../canonical-review.csv` (773, ring-gated
`buffer_metres` — the Obs 371 defect). The extension layer's
`nearest_student_m` is computed against the standardised student
layer, so per-buffer gating can be done exactly (ruling 20d step 3).

## Changelog

### 2026-08-14 — Initial materialisation

All seven spec decisions resolved (2026-08-10 and 2026-08-14); the
six-claim walk landed at `b2692f188`. Census cross-checked against
`../ruling21-summary.json` at build time.
