# K-35-075-3 outlier diagnostic

**Map**: K-35-075-3 (Soviet topographic sheet)
**Context**: Persistent low-outlier in the 55-map image generalisation
heterogeneity analysis. F1 = 0.286 across all four buffers (20/30/40/50 m)
— buffer loosening does not help, which means the 10 FPs are not
"almost-matches" that a wider tolerance would rescue.

## The raw numbers

| Quantity | Value |
|----------|------:|
| Tiles in manifest | 156 |
| Reference mounds (student-annotated) | **2** |
| Final detections (vote ≥ 3 & prob ≥ 0.15) | 12 |
| Hungarian match @ 50 m | TP=2, FP=10, FN=0 |
| Precision | 0.167 |
| Recall | 1.000 |
| F1 | 0.286 |

Recall is perfect — both ground-truth mounds were found, at excellent
spatial precision (matched detections are ~11 m and ~12 m from the
reference points). The score is dragged down entirely by the 10
detections that have no matching ground-truth.

## Why this isn't a pipeline failure

### The two TP detections are high-confidence

| Candidate | vote_count | probability | Match distance |
|-----------|:----------:|:-----------:|:--------------:|
| 5560 | 5 / 5 | 1.00 | ~11 m |
| 5601 | 4 / 5 | 1.00 | ~12 m |

### Among the 10 "FPs", two are also very high confidence

| Candidate | vote_count | probability | Nearest GT |
|-----------|:----------:|:-----------:|:-----------:|
| 5556 | 3 / 5 | **1.00** | >3 km away |
| 5616 | 5 / 5 | **0.95** | ~2 km away |

These two are well outside the 50 m buffer of both reference mounds,
so they score as FPs. But they carry verifier probability ≥ 0.95 —
the same confidence the pipeline assigned to the two confirmed TPs.
Either the pipeline is hallucinating with perfect confidence (which
would be inconsistent with its behaviour on every other map), or they
are real mounds that the student annotators missed.

### The map's reference count is anomalously low

Adjacent same-row maps:

| Map | Reference mounds |
|-----|-----------------:|
| K-35-075-1 | 73 |
| K-35-075-2 | 142 |
| **K-35-075-3** | **2** |
| K-35-075-4 | 58 |

Distribution across all 55 maps:

| Quantile | Reference mounds per map |
|----------|-------------------------:|
| Min | 2 (this map) |
| Q1 | 56 |
| Median | 82 |
| Q3 | 115 |
| Max | 246 |

K-35-075-3 is 28× below the median and 29× below the mean of its
adjacent row-075 sheets. No other map in the set has fewer than 10
reference mounds.

## Conclusion: under-annotation, not a pipeline problem

The student ground truth for this single map is almost certainly
incomplete. The pipeline found 12 candidates, of which:

- 2 match the (probably incomplete) ground truth with high confidence
  at tight spatial tolerance
- 2 more are flagged at verifier confidence ≥ 0.95 in areas where no
  ground truth exists — almost certainly real mounds the annotators
  missed
- 8 are lower-confidence candidates (verifier p = 0.20–0.40) that may
  or may not be real

If the map had been annotated with typical completeness (~80–100
mounds based on adjacent sheets), the pipeline's 12 candidates would
fall inside the normal over-detection pattern and F1 would track the
55-map average.

## Sensitivity analysis

Excluding K-35-075-3 tightens the 55-map F1 distribution considerably:

| Metric | With K-35-075-3 (n=55) | Without K-35-075-3 (n=54) | Δ |
|--------|:----------------------:|:-------------------------:|:--:|
| Mean F1 @ 50 m | 0.750 | 0.759 | +0.009 |
| SD @ 50 m | 0.093 | **0.069** | **−26%** |
| Min F1 @ 50 m | 0.286 | 0.587 | +0.301 |

The 4-map calibration SD @ 50 m is 0.021; the 55-map SD is 4.4× that
with K-35-075-3 included, or 3.3× without. Either way the
distribution widens meaningfully at generalisation, but K-35-075-3
alone accounts for a quarter of the measured spread.

## Recommendation for the paper

1. **Report the single-outlier finding explicitly** rather than
   hiding it. It illustrates a real limitation of student-annotated
   ground truth at scale: completeness varies, and missed mounds
   appear in the metric as pipeline errors.

2. **Report both distributions** (with and without K-35-075-3) in
   supplementary material so readers can judge the completeness issue
   on its own terms.

3. **Headline F1 = 0.771** is an aggregate (tile-level Hungarian) and
   therefore already less affected by this issue — the per-map mean of
   0.750 drifts further from the aggregate partly because of this one
   outlier.

4. **Future annotation improvements** on K-35-075-3 specifically would
   narrow the reported distribution and raise the minimum. This is a
   cheap improvement for a paper revision round if requested.

## Artefacts

- Source: `outputs/55maps-image-generalisation/verified/verified_detections.geojson`
  (subset: 12 detections where source_tile startswith `K-35-075-3`)
- Reference: `inputs/vectors/references/student-mounds-55maps.geojson`
  (subset: 2 features with source_map == `K-35-075-3`)
- Diagnostic: this file
