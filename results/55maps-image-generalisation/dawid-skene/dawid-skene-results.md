# Dawid-Skene Latent Truth Model — Results

## Summary

Joint model of student digitisers and VLM pipeline as noisy
annotators, estimating latent true mound locations via EM.

## Shared Item Set

| Category | Count |
|----------|-------|
| Matched (student=1, vlm=1) | 3,637 |
| Student-only (student=1, vlm=0) | 1,133 |
| VLM-only (student=0, vlm=1) | 1,028 |
| **Total** | **5,798** |

## Corrected Metrics Comparison

| Method | F1 | Precision | Recall | Notes |
|--------|----|-----------|--------|-------|
| Measured (vs student GT) | 0.771 | 0.7796 | 0.7625 | Baseline |
| Simple correction (5% FN) | 0.7904 | 0.8206 | 0.7624 | Assumes uniform FN |
| **Dawid-Skene posterior** | **0.7954** | **0.8207** | **0.7716** | Model-based |

## D-S Model Details

- **Converged**: True (11 iterations)
- **Estimated prevalence**: 0.8557 (fraction of items that are true mounds)

### Estimated Annotator Confusion Matrices

**Student digitisers:**

- Sensitivity: 0.9500 (prior: 0.95)
- Specificity: 1.0000 (prior: 1.0, fixed)

**VLM pipeline:**

- Sensitivity: 0.7716
- Specificity: 0.0000

### Reclassification of VLM-Only Items

- Total VLM-only items: 1028
- Per-item posterior P(true=1): 0.1862
- Expected reclassified (soft): 191.4
- Hard-threshold (≥0.5) reclassified: 0
- Total latent positives (expected): 4961.4

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
