# Dawid-Skene Latent Truth Model — Results

> **Post-recovery 2026-05-03 annotation** — this auto-generated
> report was re-run after the text-MIN recovery (commits
> `a9bc85b2..6e077005`). The recovery was a proposer-level no-op
> (per-pass geojsons bit-identical), but the consensus rebuild +
> dedup added +39 features (10,131 → 10,170) and +4 verified
> detections (3,861 → 3,865). Measured F1 lifted +0.0004 (0.7591 →
> 0.7595 vs un-reviewed GT) — well within the auto-proceed gate.
> See the run-level
> `configs/run-configs/55maps_text_min_generalisation_post_run_report.md`
> "Recovery 2026-05-03" subsection for the full propagation chain.

## Summary

Joint model of student digitisers and VLM pipeline as noisy
annotators, estimating latent true mound locations via EM.

## Shared Item Set

| Category | Count |
|----------|-------|
| Matched (student=1, vlm=1) | 3,276 |
| Student-only (student=1, vlm=0) | 1,494 |
| VLM-only (student=0, vlm=1) | 585 |
| **Total** | **5,355** |

## Corrected Metrics Comparison

| Method | F1 | Precision | Recall | Notes |
|--------|----|-----------|--------|-------|
| Measured (vs student GT) | 0.7591 | 0.8485 | 0.6868 | Baseline |
| Simple correction (5% FN) | 0.7764 | 0.893 | 0.6867 | Assumes uniform FN |
| **Dawid-Skene posterior** | **0.7834** | **0.8931** | **0.6977** | Model-based |

## D-S Model Details

- **Converged**: True (14 iterations)
- **Estimated prevalence**: 0.9230 (fraction of items that are true mounds)

### Estimated Annotator Confusion Matrices

**Student digitisers:**

- Sensitivity: 0.9500 (prior: 0.95)
- Specificity: 1.0000 (prior: 1.0, fixed)

**VLM pipeline:**

- Sensitivity: 0.6977
- Specificity: 0.0000

### Reclassification of VLM-Only Items

- Total VLM-only items: 585
- Per-item posterior P(true=1): 0.2947
- Expected reclassified (soft): 172.4
- Hard-threshold (≥0.5) reclassified: 0
- Total latent positives (expected): 4942.4

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
