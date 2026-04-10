# Plan: Candidate Review App (Streamlit)

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
