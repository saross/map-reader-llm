# Plan: Candidate Review App (Streamlit)

> **⚠️ SUPERSEDED 2026-05-01.** This planning document is preserved
> for historical reference. The app it specifies was built as
> `scripts/review_candidates.py` and has been in active use across
> several downstream review workflows (the GS-FP review and the v2
> burial-mound bet-test app among them). The "Future Extensions"
> list was implemented selectively per design judgement, and the
> design ceiling has been reached. See `scripts/review_candidates.py`
> for the current implementation. Do not act on items in this file
> as if they are pending.

## Purpose

A lightweight Streamlit app for rapid human review of VLM verifier
candidates. The primary use case: review measured FPs from the 55-map
generalisation run to determine how many are "phantom FPs" (real
mounds the students missed) vs genuine model errors. This provides
ground truth for the corrected precision estimate.

Secondary uses:
- QA review of any PV pipeline output
- Building human-labelled training/evaluation sets
- Identifying systematic FP categories for future prompt refinement

## Interface

```
┌──────────────────────────────────────────────┐
│  Candidate Review                            │
│                                              │
│  candidate_04237            p = 0.142        │
│  source_tile: K-35-065-3_x1344_y672.png      │
│                                              │
│  [150×150 crop image, displayed large]       │
│                                              │
│  Progress: 42 / 576  (7.3%)                  │
│  ████░░░░░░░░░░░░░░░░                       │
│                                              │
│  [Yes ✓]    [No ✗]    [Uncertain ?]          │
│                                              │
│  Running totals: 28 yes, 12 no, 2 uncertain  │
│  Estimated corrected P: 0.906                │
│                                              │
│  [Download CSV]    [Undo last]               │
└──────────────────────────────────────────────┘
```

## Candidate selection

The app should support reviewing different candidate subsets:

1. **Measured FPs** — candidates accepted by the pipeline (p ≥ 0.15)
   but unmatched to student GT within 50m. These are the "phantom FP
   or real FP?" question. (~576 candidates at 50m)

2. **All accepted** — all candidates above threshold, including TPs.
   For comprehensive QA.

3. **Custom filter** — by probability range, source map, vote count.

For the initial build, focus on (1) — measured FPs sorted by
descending verifier probability (highest p first, since those are
most likely to be phantom FPs).

## Inputs

- `--crops-dir`: Path to crops directory (with candidate_manifest.json
  and crops/ subdirectory)
- `--probabilities`: Path to probabilities.json
- `--ground-truth`: Path to reference GeoJSON (student mounds)
- `--bounds`: Path to evaluation bounds GeoJSON
- `--buffer-metres`: Matching tolerance (default 50)
- `--threshold`: Verifier probability threshold (default 0.15)
- `--output`: Path to save review results CSV (default: review.csv
  in the working directory)

## Data flow

1. Load manifest, probabilities, GT, bounds
2. Run the matching (same as `calculate_f1_internal`) to identify
   TP/FP/FN sets
3. Filter to the FP set (or user-selected subset)
4. Sort by verifier probability descending
5. Present each candidate's crop image with metadata
6. Record human label (yes/no/uncertain) per candidate
7. Save results incrementally to CSV (resume-safe)
8. Display running statistics (corrected precision estimate)

## State management

Streamlit re-runs the script on every interaction. Use
`st.session_state` to persist:
- Current candidate index
- Review results dict (candidate_id → label)
- Previously loaded data (cached with `@st.cache_data`)

For resume: on startup, load existing CSV if present and skip
already-reviewed candidates.

## Output

CSV with columns:
```
candidate_id,verifier_probability,human_label,source_tile,review_timestamp
candidate_04237,0.142,yes,K-35-065-3_x1344_y672.png,2026-04-11T10:30:00+10:00
candidate_03891,0.131,no,K-35-074-1_x2016_y1008.png,2026-04-11T10:30:15+10:00
```

## Running statistics

After each review, update and display:
- Reviewed: N / total
- Yes (phantom FP — real mound): count and %
- No (genuine FP): count and %
- Uncertain: count
- **Estimated corrected precision**: P_corrected = (TP + phantom_FP_count × total_FP/reviewed_FP) / n_accepted
- **Estimated corrected F1**: from corrected P and unchanged R

## Implementation estimate

- **Streamlit app script**: ~100 lines (`scripts/review_candidates.py`)
- **Dependencies**: `streamlit` (add to requirements.txt)
- **Matching logic**: reuse `calculate_f1_internal` or
  `match_detections_to_references` from `lib_advanced_metrics.py`
- **Total effort**: ~1 hour including testing

## Usage

```bash
pip install streamlit  # one-time
streamlit run scripts/review_candidates.py -- \
    --crops-dir outputs/55maps-generalisation/crops \
    --probabilities outputs/55maps-generalisation/verified/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson
```

## Future extensions

- Show the source tile alongside the crop (wider context)
- Show nearest student GT point distance and location
- Keyboard shortcuts (y/n/u without clicking)
- Batch mode: show 4-6 crops at once for faster screening
- Export reviewed labels as a GeoJSON for spatial analysis

## Backlog — next-generation expert review / digitisation app (future work)

Added 2026-04-20 after a session reviewing 55-map-image-generalisation
VLM-only candidates surfaced the limits of the current per-crop workflow.
Motivating observations: see `docs/notes/reflections/working-notes.md` Obs
263 (crop-based review has an ~10–15% irreducible ambiguity floor) and the
adjacent Obs 260 / 261 on annotation noise layers.

### Problem statement

The current 150×150 crop-per-candidate workflow has two structural
limitations:

1. **Spatial-matching ambiguity**: a symbol offset from crop centre forces a
   reviewer into an uncalibrated "is this close enough?" judgement, with
   drift on the fuzzy boundary.
2. **Multi-symbol disambiguation**: when a crop contains multiple candidate
   mounds (common in Thracian cluster landscapes), the reviewer cannot tell
   which one the pipeline actually detected.

The alternative — full-map manual digitisation à la
`outputs/h11/gold-standard-v2/` — is more accurate but slower, and historically
has not had a dedicated tool; it's been done in QGIS with some scripting
around.

### Design space to explore

An app optimised for accuracy AND speed would likely combine elements of
both workflows:

- **Whole-map canvas** (tile or raster viewer, not cropped per-candidate),
  with pan/zoom, keyboard nav.
- **All pipeline candidates overlaid** as transient markers with their
  verifier probabilities colour-coded.
- **All existing GT points overlaid**, distinguishable (e.g. by shape or
  colour) so the reviewer knows what's already been catalogued.
- **Review actions at the symbol level, not the candidate level**: click a
  real symbol → record it as a mound regardless of whether the pipeline
  detected it; click a spurious candidate → record it as FP. Disambiguation
  by direct spatial pointing.
- **Automatic crosshair / distance readout** to nearest candidate centroid
  and nearest GT point — gives the reviewer a calibrated sense of proximity
  rather than a visual guess.
- **Batch advance**: when the visible window is fully reviewed, pan to
  the next un-reviewed area automatically. Keyboard-driven.
- **Session-resumable**: same as current app, with per-map or per-tile
  progress state.
- **Output = reviewed GeoJSON** (matching the gold-standard-v2 format), not
  a per-candidate CSV. The F1 calculation happens downstream by recomputing
  matches against the human-reviewed mound set.

### Why this is better than the current app

- Eliminates the centre-offset ambiguity (reviewer points at the symbol
  directly).
- Handles multi-symbol crops correctly (review each symbol on its merits).
- Makes "did the pipeline miss this?" visible — reviewer can mark real
  mounds the pipeline didn't detect, producing the full recall picture
  rather than just a phantom-FP rescue.
- Produces a single artefact (reviewed GeoJSON) that is reusable as an
  upgraded gold standard for any future pipeline evaluation, not just the
  current run.

### Why this is *not* urgent

- The current Streamlit app is what's running the 55-map review now; the
  results will produce a defensible human-corrected F1 with the known
  ~10–15% ambiguity caveat documented in Obs 263.
- Building the next-gen app is a multi-day project (map rendering stack,
  overlay logic, session/state model, GeoJSON I/O) — not justifiable
  pre-publication for the current paper.
- Post-publication, if the research programme continues and further
  corpora need review, this is the right investment to queue.

### Open questions for when the time comes

- **Stack**: Streamlit-with-Folium? Pure web (Leaflet + FastAPI)? Desktop
  (QGIS plugin)? Each has trade-offs for deployment, collaborator access,
  and performance at raster scales.
- **Collaboration**: multi-reviewer workflow? Conflict resolution when two
  reviewers disagree on the same map area?
- **Provenance**: how to record reviewer identity, timestamp, and decision
  confidence per point in the output GeoJSON.
- **Generalisation to other archaeological symbol classes**: could the same
  tool support review of tells, enclosures, field boundaries, not just
  burial mounds? If yes, the symbol-classification infrastructure should
  be generic from the start.

### Pointer

When revisiting this, also review whether the `outputs/h11/gold-standard-v2/`
workflow (however it was produced) has tooling that can be lifted rather
than built fresh.
