# Dawid-Skene Latent Truth Model — v2 (data-driven prior)

## Summary

Identical to v1 except the student false-negative prior, which is 0.7247 (source: empirical_vlm_only_mound_rate).

## Item counts

| Category | Count |
|----------|------:|
| Matched | 3,637 |
| Student-only | 1,133 |
| VLM-only | 1,028 |
| **Total** | **5,798** |

## D-S outputs

- Converged: True (11 iterations)
- Estimated prevalence: 1.0000
- Student sensitivity (fixed): 0.2753
- Student specificity (fixed): 1.0000
- VLM sensitivity: 0.8046
- VLM specificity: 0.0000
- VLM-only posterior: 1.0000

See `comparison.md` for v1 vs v2 side-by-side, and `report.md` for the narrative interpretation and circularity caveat.
