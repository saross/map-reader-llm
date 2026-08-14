# Dawid-Skene Latent Truth Model — Results

## Summary

Joint model of student digitisers and VLM pipeline as noisy
annotators, estimating latent true mound locations via EM.

## Shared Item Set

| Category | Count |
|----------|-------|
| Matched (student=1, vlm=1) | 3,279 |
| Student-only (student=1, vlm=0) | 1,452 |
| VLM-only (student=0, vlm=1) | 586 |
| **Total** | **5,317** |

## Corrected Metrics Comparison

| Method | F1 | Precision | Recall | Notes |
|--------|----|-----------|--------|-------|
| Measured (vs student GT) | 0.7629 | 0.8484 | 0.6931 | Baseline |
| Simple correction (5% FN) | 0.7806 | 0.8931 | 0.6932 | Assumes uniform FN |
| **Dawid-Skene posterior** | **0.7873** | **0.893** | **0.7039** | Model-based |

## D-S Model Details

- **Converged**: True (14 iterations)
- **Estimated prevalence**: 0.9222 (fraction of items that are true mounds)

### Estimated Annotator Confusion Matrices

**Student digitisers:**

- Sensitivity: 0.9500 (prior: 0.95)
- Specificity: 1.0000 (prior: 1.0, fixed)

**VLM pipeline:**

- Sensitivity: 0.7039
- Specificity: 0.0000

### Reclassification of VLM-Only Items

- Total VLM-only items: 586
- Per-item posterior P(true=1): 0.2945
- Expected reclassified (soft): 172.6
- Hard-threshold (≥0.5) reclassified: 0
- Total latent positives (expected): 4903.6

**Note on 2-annotator identifiability:** With only two binary
annotators, D-S assigns the same posterior to all VLM-only
items because they share identical labels (s=0, v=1). The
model correctly estimates the aggregate fraction of real mounds
but cannot discriminate individual items. Hard thresholding at
0.5 reclassifies none; expected counts capture the aggregate.
The verifier probability provides per-item discrimination for
human review (see item-posteriors.csv).

## References

- Dawid, A.P. & Skene, A.M. (1979). Maximum likelihood estimation of observer error-rates using the EM algorithm. *Applied Statistics*, 28(1), 20-28.
- Sobotkova, A. et al. (2023). Creating large, high-quality geospatial datasets from historical maps using novice volunteers.
