# Dawid-Skene Latent Truth Model — Results

> **Post-recovery 2026-05-03 annotation** — this auto-generated report
> reflects the post-recovery state. Pre-recovery values for the same
> measurement (F1 = 0.7710, D-S F1 = 0.795) are preserved at
> `dawid-skene-results.md.pre-recovery-20260503T023258.backup` in this
> directory. The +0.0035 lift in measured F1 comes from the
> verifier-cleanup pass surfacing 18 pre-existing missing-from-verifier
> candidates plus 1 new consensus candidate; D-S posterior shifted
> from 0.795 to 0.799 (+0.004). See the run-level
> `configs/run-configs/55maps_image_generalisation_post_run_report.md`
> "Recovery 2026-05-03" subsection for the full propagation chain.

## Summary

Joint model of student digitisers and VLM pipeline as noisy
annotators, estimating latent true mound locations via EM.

## Shared Item Set

| Category | Count |
|----------|-------|
| Matched (student=1, vlm=1) | 3,650 |
| Student-only (student=1, vlm=0) | 1,095 |
| VLM-only (student=0, vlm=1) | 1,030 |
| **Total** | **5,775** |

## Corrected Metrics Comparison

| Method | F1 | Precision | Recall | Notes |
|--------|----|-----------|--------|-------|
| Measured (vs student GT) | 0.7745 | 0.7799 | 0.7692 | Baseline |
| Simple correction (5% FN) | 0.7942 | 0.8209 | 0.7692 | Assumes uniform FN |
| **Dawid-Skene posterior** | **0.799** | **0.821** | **0.7782** | Model-based |

## D-S Model Details

- **Converged**: True (11 iterations)
- **Estimated prevalence**: 0.8549 (fraction of items that are true mounds)

### Estimated Annotator Confusion Matrices

**Student digitisers:**

- Sensitivity: 0.9500 (prior: 0.95)
- Specificity: 1.0000 (prior: 1.0, fixed)

**VLM pipeline:**

- Sensitivity: 0.7782
- Specificity: 0.0000

### Reclassification of VLM-Only Items

- Total VLM-only items: 1030
- Per-item posterior P(true=1): 0.1865
- Expected reclassified (soft): 192.1
- Hard-threshold (≥0.5) reclassified: 0
- Total latent positives (expected): 4937.1

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
