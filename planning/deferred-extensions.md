# Deferred Extensions Backlog

**Status**: Deferred. Items recorded for future consideration.

**Purpose**: Centralised list of feature, tooling, and methodology
extensions that were spec'd or sketched but intentionally not built —
typically because they were lower priority than what shipped, lower
return on investment than alternatives, or scoped explicitly as
post-publication work. Captures the design-space context so that a
future revisit does not have to re-derive the rationale.

**How to use**:

- Before starting a new feature or tool, check here for prior analysis.
- Items here are NOT active session work. Do not treat them as pending
  to-dos.
- Re-evaluation at any point is welcome — if a deferred item becomes
  worth pursuing, move it to the appropriate active planning doc and
  add a back-link from here.
- Add new entries when intentionally deferring something with non-trivial
  context worth preserving. Use the section pattern below.

---

## Candidate review app (`scripts/review_candidates.py`)

**Source**: Originally specified in
`archive/planning-completed-session-81-82/candidate-review-app.md`
(superseded 2026-05-01). The core app shipped and is in active use across
multiple 55-map and gold-standard review campaigns. The items below are
extensions intentionally not built.

**Empirical-design-ceiling note**: Obs 263 predicted ~10–15 % irreducible
crop-based ambiguity; Obs 272 measured 11.8 % flip in the (50, 75] m
shell — exact match. The crop-review tool has reached its design ceiling.
Any next iteration is a different tool (see "Next-generation expert review"
below), not an enhancement to `review_candidates.py`.

### Selectively-deferred extensions to the current app

These were listed as "Future extensions" in the original spec; deemed
lower-ROI than the multi-buffer-tolerance-rings + re-verification-toggle
work that did ship.

- **Source tile context alongside the crop** — wider-context view to
  help disambiguate crops near tile boundaries. Not built; current crops
  are presented in isolation.
- **Nearest student GT point distance + location overlay** — currently
  computed internally during Hungarian matching but only surfaced via
  CSV. Not rendered on the image. Would be a small UI addition.
- **Batch mode** — show 4–6 crops at once for faster screening. Not
  built; single-candidate-at-a-time UI remains.
- **GeoJSON export** — current output is CSV only. Adding a GeoJSON
  variant would make spatial-analysis downstream easier.

### Next-generation expert review / digitisation app (whole-map editor)

Larger backlog item, spec'd 2026-04-20 in the original planning doc
after a session reviewing 55-map-image-generalisation candidates surfaced
the limits of the current per-crop workflow. Motivating observations:
working-notes Obs 263 (crop-based review has an ~10–15 % irreducible
ambiguity floor) and the adjacent Obs 260 / 261 on annotation noise.

#### Problem statement

The current 150 × 150 crop-per-candidate workflow has two structural
limitations:

1. **Spatial-matching ambiguity**: a symbol offset from crop centre forces
   a reviewer into an uncalibrated "is this close enough?" judgement,
   with drift on the fuzzy boundary.
2. **Multi-symbol disambiguation**: when a crop contains multiple
   candidate mounds (common in Thracian cluster landscapes), the reviewer
   cannot tell which one the pipeline actually detected.

The alternative — full-map manual digitisation à la
`outputs/h11/gold-standard-v2/` — is more accurate but slower, and
historically has not had a dedicated tool; it has been done in QGIS with
some scripting around.

#### Design space to explore

An app optimised for accuracy AND speed would likely combine elements of
both workflows:

- **Whole-map canvas** (tile or raster viewer, not cropped per-candidate),
  with pan / zoom, keyboard nav.
- **All pipeline candidates overlaid** as transient markers with their
  verifier probabilities colour-coded.
- **All existing GT points overlaid**, distinguishable (e.g. by shape or
  colour) so the reviewer knows what is already catalogued.
- **Review actions at the symbol level, not the candidate level**: click
  a real symbol → record it as a mound regardless of whether the pipeline
  detected it; click a spurious candidate → record it as FP. Disambiguation
  by direct spatial pointing.
- **Automatic crosshair / distance readout** to nearest candidate centroid
  and nearest GT point — gives the reviewer a calibrated sense of
  proximity rather than a visual guess.
- **Batch advance**: when the visible window is fully reviewed, pan to
  the next un-reviewed area automatically. Keyboard-driven.
- **Session-resumable**: same as current app, with per-map or per-tile
  progress state.
- **Output = reviewed GeoJSON** (matching the gold-standard-v2 format),
  not a per-candidate CSV. The F1 calculation happens downstream by
  recomputing matches against the human-reviewed mound set.

#### Why this would be better than the current app

- Eliminates the centre-offset ambiguity (reviewer points at the symbol
  directly).
- Handles multi-symbol crops correctly (review each symbol on its merits).
- Makes "did the pipeline miss this?" visible — reviewer can mark real
  mounds the pipeline did not detect, producing the full recall picture
  rather than just a phantom-FP rescue.
- Produces a single artefact (reviewed GeoJSON) that is reusable as an
  upgraded gold standard for any future pipeline evaluation, not just
  the current run.

#### Why this is *not* urgent

- The current Streamlit app shipped, in active use, and the results
  produce a defensible human-corrected F1 with the known ~10–15 %
  ambiguity caveat documented in Obs 263.
- Building the next-generation app is a multi-day project (map-rendering
  stack, overlay logic, session / state model, GeoJSON I/O) — not
  justifiable pre-publication for the current paper.
- Post-publication, if the research programme continues and further
  corpora need review, this is the right investment to queue.

#### Open questions for when the time comes

- **Stack**: Streamlit + Folium? Pure web (Leaflet + FastAPI)? Desktop
  (QGIS plugin)? Each has trade-offs for deployment, collaborator access,
  and performance at raster scales.
- **Collaboration**: multi-reviewer workflow? Conflict resolution when
  two reviewers disagree on the same map area?
- **Provenance**: how to record reviewer identity, timestamp, and
  decision confidence per point in the output GeoJSON.
- **Generalisation to other archaeological symbol classes**: could the
  same tool support review of tells, enclosures, field boundaries, not
  just burial mounds? If yes, the symbol-classification infrastructure
  should be generic from the start.

#### Pointer

When revisiting this, also review whether the
`outputs/h11/gold-standard-v2/` workflow (however it was produced) has
tooling that can be lifted rather than built fresh.

---

<!-- New deferred-extensions sections go below. Use the same template:
     ## <topic>

     **Source**: <where this came from>

     ### <subsection per item>
     ...
-->
