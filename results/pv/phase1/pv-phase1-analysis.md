# PV Phase 1: Verifier Optimisation (340-Tile Corpus)

**Generated**: 2026-03-21
**Proposer**: Text N=1 T=0.0 minimal (882 candidates, Phase 2b run_1)
**Verifier**: Adversarial-text (baseline), tested against brief-text and checklist-text
**Bootstrap**: 1,000 iterations, seed=42
**Pilot reference**: `results/phase3d-verifier-experiments-abc.md` (60-tile holdout)

## Key Finding

The Proposer-Verifier (PV) pipeline improves F1 from 0.6052 (proposer only) to 0.7669 (with verifier) on the 340-tile corpus, consistent with the pilot result (F1=0.796 on 60 tiles, within CI). Verifier performance is **insensitive to crop size** (75--300 px), **not improved by consensus** (N=5 approximately equals N=1), and **equivalent across strategies** (adversarial approximately equals checklist approximately equals brief).

## Crop Size Sensitivity (Obs 166)

All four crop sizes tested with adversarial-text verifier, N=1, T=0.0.

| Crop Size | F1 | 95% CI | P | R | n |
|----------:|-----:|:------:|------:|------:|----:|
| 40 px | 0.7407 | [0.6947, 0.7841] | 0.7803 | 0.7050 | 487 |
| 75 px | 0.7681 | [0.7227, 0.8080] | 0.7875 | 0.7495 | 513 |
| 150 px | 0.7669 | [0.7323, 0.8095] | 0.7771 | 0.7570 | 525 |
| 300 px | 0.7607 | [0.7133, 0.8026] | 0.7665 | 0.7551 | 531 |

The 40 px crop underperforms (F1=0.7407) due to insufficient context, but 75 px, 150 px, and 300 px are statistically equivalent with broadly overlapping CIs. The 150 px default is retained for consistency with the pilot (see `results/phase3d-verifier-experiments-abc.md`).

## Consensus N=1 vs N=5 (Obs 167)

Adversarial-text verifier at 150 px crop. N=5 uses T=0.7 with mean probability aggregation; N=1 uses T=0.0.

| Config | F1 | 95% CI | P | R | Threshold | n |
|--------|-----:|:------:|------:|------:|----------:|----:|
| N=1, T=0.0 | 0.7669 | [0.7323, 0.8095] | 0.7771 | 0.7570 | 0.20 | 525 |
| N=5, T=0.7 | 0.7737 | [0.7273, 0.8157] | 0.7737 | 0.7737 | 0.20 | 539 |

N=5 consensus provides a marginal F1 improvement (+0.0068) that falls well within the overlap of both CIs. The 5x cost increase is not justified. This mirrors the pilot finding that verifier consensus adds no value, consistent with the Phase 3d temperature experiment (Experiment C) showing verifier errors are systematic perceptual misclassifications rather than sampling noise.

## Verifier Strategy Comparison (Obs 169)

Three verifier instruction strategies tested at 150 px crop, N=1, T=0.0.

| Strategy | F1 | 95% CI | P | R | Threshold | n |
|----------|-----:|:------:|------:|------:|----------:|----:|
| adversarial-text | 0.7669 | [0.7323, 0.8095] | 0.7771 | 0.7570 | 0.20 | 525 |
| checklist-text | 0.7694 | [0.7241, 0.8092] | 0.7478 | 0.7922 | 0.15 | 571 |
| brief-text | 0.7523 | [0.7113, 0.7947] | 0.7609 | 0.7440 | 0.15 | 527 |

All three strategies produce statistically equivalent F1 (overlapping CIs). The checklist strategy yields slightly higher recall (0.7922) at the cost of lower precision (0.7478); adversarial produces the best precision-recall balance. Brief-text slightly underperforms but remains within CI overlap.

## Optimal Configuration

- **Verifier**: adversarial-text (selected for consistency with pilot; any strategy equivalent)
- **Crop size**: 150 px (default; 75--300 px equivalent)
- **Passes**: N=1 (consensus adds no value for verification)
- **Temperature**: T=0.0
- **Optimal threshold**: 0.20

## Proposer-Only Baseline

For reference, the proposer-only performance (no verifier) on the same 882 candidates:

| Metric | Value | 95% CI |
|--------|------:|:------:|
| F1 | 0.6052 | [0.5469, 0.6551] |
| Precision | 0.4875 | [0.4249, 0.5445] |
| Recall | 0.7978 | [0.7425, 0.8458] |

The verifier improves F1 by +0.1617 (0.6052 to 0.7669), primarily by boosting precision from 0.4875 to 0.7771 (+0.2896) while trading modest recall (0.7978 to 0.7570, -0.0408).

## Methodology

1. Proposer detections from Phase 2b T=0.0 run_1 (882 candidates on 340 tiles)
2. Candidate crops extracted from source GeoTIFF rasters (E33 non-truncating path)
3. Each crop submitted to verifier via real-time Application Programming Interface (API) with the specified verifier configuration
4. Probability threshold swept 0.0--1.0 in 0.05 steps
5. F1/P/R computed via Hungarian matching at 20 m tolerance
6. Bootstrap CIs via tile-level resampling (K=1,000, seed=42)
7. Crop sizes tested: 40, 75, 150, 300 px; strategies tested: adversarial-text, brief-text, checklist-text; consensus tested: N=1 T=0.0 vs N=5 T=0.7
