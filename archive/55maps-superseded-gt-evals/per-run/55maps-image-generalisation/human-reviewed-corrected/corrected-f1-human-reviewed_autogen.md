# Corrected F1/P/R at 50 m — human-reviewed

**Timestamp**: 2026-04-20T07:13:19.416828+00:00
**Review CSV**: `results/55maps-image-generalisation/human-review.csv`
**Buffer**: 50 m (the ONLY buffer at which this correction is valid)

## Headline numbers

| Metric | Measured | Measured 95% CI | Corrected | Corrected 95% CI (review-only) |
|--------|---------:|:---------------:|----------:|:------------------------------:|
| F1 | 0.7710 | [0.7604, 0.7817] | **0.8295** | [0.8257, 0.8333] |
| Precision | 0.7796 | [0.7658, 0.7924] | **0.8808** | [0.8739, 0.8876] |
| Recall | 0.7625 | [0.7491, 0.7759] | **0.7839** | [0.7826, 0.7852] |

**Delta from measured**: F1 +0.0585, P +0.1012, R +0.0214.

## Caveats

- **50 m only**: this correction is valid only at the 50 m buffer. Reviewers
  judged each candidate against the 50 m tolerance circle and did not record
  symbol positions within the circle; tighter-buffer corrections are not
  derivable from this output. See Obs 263 in
  `docs/notes/reflections/working-notes.md`.
- **Conservative bias**: the reviewer's decision policy is asymmetric —
  ambiguous cases default to not-mound (Obs 263 follow-up). The corrected F1
  is therefore a **lower bound**, not a point estimate. The Dawid-Skene
  aggregate-posterior F1 (0.795, see `results/55maps-image-generalisation/dawid-skene/`)
  is the complementary weighted-average estimate and represents a tentative
  upper-bound for the comparison.
- **CI incompatibility**: the measured CI and the corrected CI capture
  different uncertainty sources. Measured CI bootstraps over pipeline
  matching variability; corrected CI bootstraps over human-review labels.
  They are not commensurable — do not compute a single "combined" CI by
  intersection or union without a joint bootstrap.

## Counts

### Measured (at 50 m)
- TP: 3637
- FP: 1028
- FN: 1133
- n_detections: 4665
- n_ref: 4770

### Human review
- Reviewed: 1028 VLM-only candidates
- Phantom TP (marked as real mound): **472** (45.9%)
- Confirmed FP (marked not-mound): 556 (54.1%)

### Corrected (at 50 m)
- TP_corrected: 4109 (measured + 472 phantom)
- FP_corrected: 556 (measured − 472 reassigned)
- FN_corrected: 1133 (unchanged — phantom TPs weren't in student GT)
- n_ref_extended: 5242 (student GT + 472 newly-discovered mounds)

## Dawid-Skene comparison

| Method | Phantom-TP estimate | Corrected F1 |
|--------|--------------------:|-------------:|
| Measured (no correction) | 0 | 0.7710 |
| Dawid-Skene aggregate posterior | ~186 (18.1%) | 0.7950 |
| **Human review (per-item)** | **472 (45.9%)** | **0.8295** |

The human-reviewed estimate is +27.8 percentage
points higher than the D-S aggregate posterior. Consistent with Obs 263: crop
review catches more than aggregate posterior methods because it can identify
individual phantom mounds rather than only estimating their aggregate rate.

## Reproducibility

- Bootstrap: 10,000 iterations, seed 42
- Inputs: `results/55maps-image-generalisation/human-review.csv`, `outputs/55maps-image-generalisation/evaluation/evaluation.json`
- Script: `scripts/compute_corrected_f1_human_reviewed.py`
