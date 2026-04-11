# Plan: Dawid-Skene Latent Truth Model for Corrected Metrics

## Motivation

The 55-map generalisation study evaluates the VLM pipeline against
student-digitised ground truth (4,770 mounds). The student GT has a
documented error profile (Sobotkova et al. 2023): ~5% false negative
rate (missed real mounds), ~0% false positive rate (no invented
mounds). This means measured precision is artificially low — some VLM
detections scored as FP are actually correct detections of mounds the
students missed.

A simple correction (multiply-adjust for the 5% FN rate) yields
corrected F1=0.809 (from 0.790). But a Dawid-Skene (D-S) latent
class model can do better: it jointly estimates the true mound
locations by modelling both the students and the VLM as noisy
annotators with learnable error rates.

## The Dawid-Skene Model

### Core idea

Given K annotators who each label N items as positive/negative, D-S
estimates:
- The **true label** for each item (latent variable)
- Each annotator's **confusion matrix** (sensitivity and specificity)

The model uses EM (Expectation-Maximisation) to iteratively:
1. **E-step**: Estimate P(true label | all annotations) using
   current annotator confusion matrices
2. **M-step**: Re-estimate annotator confusion matrices using
   current true label estimates

### Annotators in our setup

1. **Student digitisers**: Binary label per spatial location
   (mound present / absent). Known priors from QA: sensitivity ≈0.95,
   specificity ≈1.0.
2. **VLM pipeline**: Produces a probability per candidate. Can be
   binarised at threshold (e.g., 0.15) or used as soft labels.

### Spatial alignment challenge

D-S operates on a shared item set. Our two annotators don't label the
same items — students digitised point locations, the VLM produces
bounding boxes. Alignment options:

**Option A: Point-based matching (recommended)**

Use the existing Hungarian algorithm matching (50m tolerance) to
create the shared item set:

- **Matched pairs** (TP): Both student and VLM agree → strong
  evidence of a mound
- **Student-only points** (VLM FN): Student says mound, VLM says
  nothing → real mound the VLM missed, OR student error
- **VLM-only points** (VLM FP): VLM says mound, no student point
  nearby → phantom FP (real mound student missed), OR VLM error

This gives us a natural item set of ~5,500 spatial locations
(~3,500 matched + ~1,300 student-only + ~600 VLM-only).

**Option B: Grid-based (more complex)**

Discretise the map into 20m grid cells, assign binary labels from
each annotator to each cell. More principled but creates ~millions
of mostly-empty cells, requiring sparse representation.

### Prior information

We can initialise D-S with strong priors from known error rates:

```python
# Student confusion matrix (from Sobotkova et al. 2023 QA)
student_sensitivity = 0.95  # P(student=1 | true=1) — catches 95%
student_specificity = 1.00  # P(student=0 | true=0) — no false positives

# VLM confusion matrix (from gold standard evaluation)
vlm_sensitivity = 0.73     # P(vlm=1 | true=1) — recall at 50m
vlm_specificity = 0.86     # P(vlm=0 | true=0) — 1 - FPR (approximate)
```

With strong priors, D-S converges quickly (typically 3-5 EM iterations).

## Implementation Plan

### Dependencies

- `crowd-kit` (Toloka's crowdsourcing library) has a D-S implementation
  that accepts soft labels: `pip install crowd-kit`
- Alternatively, implement the 2-annotator D-S directly (~50 lines)
  since we only have 2 annotators and strong priors

### Steps

1. **Build the shared item set** (~30 min)
   - Run Hungarian matching at 50m between VLM detections and student GT
   - Create a DataFrame with columns: `item_id`, `student_label`,
     `vlm_label`, `vlm_probability`, `geometry`
   - Matched pairs: student=1, vlm=1
   - Student-only: student=1, vlm=0
   - VLM-only: student=0, vlm=1

2. **Run D-S with priors** (~30 min)
   - Initialise annotator confusion matrices from known error rates
   - Run EM until convergence
   - Extract posterior P(true=1) for each item

3. **Compute corrected metrics** (~15 min)
   - Threshold posteriors at 0.5 to get latent truth labels
   - Recalculate P, R, F1 of the VLM against latent truth
   - Compare with simple correction and measured values

4. **Sensitivity analysis** (~30 min)
   - Vary student FN rate (3%–7%) and see how corrected metrics change
   - Vary the matching tolerance (20–50m)
   - Report the range of plausible corrected F1

### Expected output

A table like:

| Method | F1 | P | R | Notes |
|--------|------|------|------|-------|
| Measured (vs student GT) | 0.790 | 0.858 | 0.732 | Baseline |
| Simple correction (5% FN) | 0.809 | 0.904 | 0.732 | Assumes uniform FN |
| Dawid-Skene posterior | ~0.81 | ~0.90 | ~0.73 | Model-based |
| Human-reviewed FPs | TBD | TBD | TBD | Ground truth |

Plus: D-S posterior probabilities per item, which can be mapped
spatially to identify where the student GT is most likely wrong.

### Interesting side outputs

- **Estimated student error rate** (model-derived vs documented):
  does D-S recover the ~5% FN rate from the data alone?
- **Spatial distribution of disagreements**: do phantom FPs cluster
  in specific maps or regions? (This would indicate systematic
  student omissions vs random errors.)
- **VLM as QA tool**: the VLM detections could identify which maps
  need re-digitisation, turning the model comparison into a QA
  workflow.

## Timeline

- **Effort**: ~2 hours total (steps 1-4 above)
- **Dependencies**: None beyond existing data + crowd-kit install
- **When**: After the quick-review app provides human-verified FP
  labels (which serve as ground truth for validating the D-S output)
- **Compute**: Local (no API calls, no sapphire needed)

## Status: COMPLETE (2026-04-11)

Implemented as `scripts/analyse_dawid_skene.py` with 26 tier1 tests.

### Key Results

| Method | F1 | Precision | Recall |
|--------|----|-----------|--------|
| Measured (vs student GT) | 0.7898 | 0.8579 | 0.7317 |
| Simple correction (5% FN) | 0.8084 | 0.9031 | 0.7317 |
| Dawid-Skene posterior | 0.8144 | 0.9031 | 0.7416 |

### Key Findings

1. **D-S validates the simple correction**: Both agree on corrected
   precision (0.903) and expected reclassification count (~184 of 578
   VLM-only items).
2. **2-annotator identifiability limitation**: With only 2 binary
   annotators, D-S assigns a uniform posterior (0.318) to all VLM-only
   items. It correctly estimates the aggregate fraction but cannot
   discriminate individual items. Student sensitivity must be fixed at
   the documented prior (0.95) — if free, EM converges to 1.0.
3. **Verifier probability provides individual discrimination**: The 578
   VLM-only items split bimodally: 348 with p≥0.8 (likely real mounds)
   and 162 with p<0.3 (likely FPs). This is the primary input for the
   candidate review app.
4. **Recall difference between methods**: D-S gives slightly higher
   recall (0.742 vs 0.732) because it operates on the observed item set
   and does not count mounds missed by BOTH annotators. The simple
   correction's estimate (R=0.732) is more conservative.
5. **Consensus GeoJSON CRS bug found**: The consensus GeoJSON declares
   EPSG:4326 but stores EPSG:32635 coordinates — requires `set_crs`
   override rather than `to_crs` reprojection.

### Output Files

- `results/dawid-skene/dawid-skene-results.md` — Full report
- `results/dawid-skene/dawid-skene-results.json` — Machine-readable
- `results/dawid-skene/item-posteriors.csv` — Per-item data for review app

## References

- Dawid, A.P. and Skene, A.M. (1979). "Maximum likelihood estimation
  of observer error-rates using the EM algorithm." Applied Statistics.
- Sobotkova, A. et al. (2023). "Creating large, high-quality
  geospatial datasets from historical maps using novice volunteers."
- `crowd-kit` library: https://github.com/Toloka/crowd-kit
