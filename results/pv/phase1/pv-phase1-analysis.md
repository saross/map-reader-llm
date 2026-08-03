# PV Phase 1: Verifier Optimisation (340-Tile Corpus)

> **Last revised**: 2026-08-03 (E39 — regenerated the adversarial-text-150 arm
> on the sibling arms' fine threshold grid; corrected the three tables that
> carried its figures and the selected operating point).
> See [§ Changelog](#changelog) for revision history.

**Generated**: 2026-03-21
**Proposer**: Text N=1 T=0.0 minimal (882 candidates, Phase 2b run_1)
**Verifier**: Adversarial-text (baseline), tested against brief-text and checklist-text
**Bootstrap**: 1,000 iterations, seed=42
**Pilot reference**: `results/phase3d-verifier-experiments-abc.md` (60-tile holdout)

## Key Finding

The Proposer-Verifier (PV) pipeline improves F1 from 0.6052 (proposer only) to 0.7701 (with verifier) on the 340-tile corpus, consistent with the pilot result (F1=0.796 on 60 tiles, within CI). Verifier performance is **insensitive to crop size** (75--300 px), **not improved by consensus** (N=5 approximately equals N=1), and **equivalent across strategies** (adversarial approximately equals checklist approximately equals brief).

### Confidence-interval comparability (†)

Rows marked † are the adversarial-text 150 px, N=1, T=0.0 arm, regenerated on
2026-08-03 (see [§ Changelog](#changelog)). Their confidence intervals (CIs) use
the bias-corrected and accelerated (BCa) bootstrap; every unmarked row in this
document retains a percentile-method CI computed in March 2026. The switch
landed in `scripts/lib_advanced_metrics.py` at commit `2026999ad` (2026-04-30).

Point estimates are unaffected by the method change and remain directly
comparable across all rows. **CI widths are not**: BCa intervals here are
appreciably narrower than the percentile intervals beside them, so the marked
and unmarked CIs must not be compared against each other as if they were
like-for-like. Every equivalence claim below was re-checked after the
regeneration and still holds on the intervals as shown, but the CI column is
method-mixed by construction and should be read with that caveat.

## Crop Size Sensitivity (Obs 166)

All four crop sizes tested with adversarial-text verifier, N=1, T=0.0.

| Crop Size | F1 | 95% CI | P | R | n |
|----------:|-----:|:------:|------:|------:|----:|
| 40 px | 0.7407 | [0.6947, 0.7841] | 0.7803 | 0.7050 | 487 |
| 75 px | 0.7681 | [0.7227, 0.8080] | 0.7875 | 0.7495 | 513 |
| 150 px | 0.7701 | [0.7466, 0.7943]† | 0.7759 | 0.7644 | 531 |
| 300 px | 0.7607 | [0.7133, 0.8026] | 0.7665 | 0.7551 | 531 |

The 40 px crop underperforms (F1=0.7407) due to insufficient context, but 75 px, 150 px, and 300 px are statistically equivalent with broadly overlapping CIs. The 150 px default is retained for consistency with the pilot (see `results/phase3d-verifier-experiments-abc.md`); on the common 0.05 threshold grid it is now also the nominal best of the four, but its margin over 75 px (+0.0020) is far inside the CI overlap and carries no inferential weight.

## Consensus N=1 vs N=5 (Obs 167)

Adversarial-text verifier at 150 px crop. N=5 uses T=0.7 with mean probability aggregation; N=1 uses T=0.0.

| Config | F1 | 95% CI | P | R | Threshold | n |
|--------|-----:|:------:|------:|------:|----------:|----:|
| N=1, T=0.0 | 0.7701 | [0.7466, 0.7943]† | 0.7759 | 0.7644 | 0.15 | 531 |
| N=5, T=0.7 | 0.7737 | [0.7273, 0.8157] | 0.7737 | 0.7737 | 0.20 | 539 |

N=5 consensus provides a marginal F1 improvement (+0.0036) that falls well within the overlap of both CIs. The 5x cost increase is not justified. This mirrors the pilot finding that verifier consensus adds no value, consistent with the Phase 3d temperature experiment (Experiment C) showing verifier errors are systematic perceptual misclassifications rather than sampling noise.

## Verifier Strategy Comparison (Obs 169)

Three verifier instruction strategies tested at 150 px crop, N=1, T=0.0.

| Strategy | F1 | 95% CI | P | R | Threshold | n |
|----------|-----:|:------:|------:|------:|----------:|----:|
| adversarial-text | 0.7701 | [0.7466, 0.7943]† | 0.7759 | 0.7644 | 0.15 | 531 |
| checklist-text | 0.7694 | [0.7241, 0.8092] | 0.7478 | 0.7922 | 0.15 | 571 |
| brief-text | 0.7523 | [0.7113, 0.7947] | 0.7609 | 0.7440 | 0.15 | 527 |

All three strategies produce statistically equivalent F1 (overlapping CIs). On the common 0.05 threshold grid, adversarial-text is now the nominal leader (0.7701) rather than checklist-text (0.7694) — an ordering reversal relative to the figures published before the 2026-08-03 grid correction. The margin is 0.0007, which is inferentially meaningless, and the substantive conclusion of cross-strategy equivalence is unchanged. The checklist strategy yields slightly higher recall (0.7922) at the cost of lower precision (0.7478); adversarial produces the best precision-recall balance. Brief-text slightly underperforms but remains within CI overlap.

## Optimal Configuration

- **Verifier**: adversarial-text (selected for consistency with pilot; any strategy equivalent — and, on the corrected grid, nominally the best of the three)
- **Crop size**: 150 px (default; 75--300 px equivalent)
- **Passes**: N=1 (consensus adds no value for verification)
- **Temperature**: T=0.0
- **Optimal threshold**: 0.15

The optimal threshold moved from 0.20 to 0.15 in the 2026-08-03 correction. This is a genuine change to the selected operating point, not a restatement: the previously published 0.20 was an artefact of sweeping this arm on a 0.1 grid that contained no 0.15 row. Every other selection above is unchanged. Downstream work that inherited threshold 0.20 from this document should be re-checked against 0.15.

## Proposer-Only Baseline

For reference, the proposer-only performance (no verifier) on the same 882 candidates:

| Metric | Value | 95% CI |
|--------|------:|:------:|
| F1 | 0.6052 | [0.5469, 0.6551] |
| Precision | 0.4875 | [0.4249, 0.5445] |
| Recall | 0.7978 | [0.7425, 0.8458] |

This baseline is the threshold-0.0 row, at which all 882 proposer candidates are accepted. It is identical across all seven Phase 1 arms by construction and is therefore unaffected by the 2026-08-03 grid correction; the CI shown is the percentile-era value.

The verifier improves F1 by +0.1649 (0.6052 to 0.7701), primarily by boosting precision from 0.4875 to 0.7759 (+0.2884) while trading modest recall (0.7978 to 0.7644, -0.0334).

## Methodology

1. Proposer detections from Phase 2b T=0.0 run_1 (882 candidates on 340 tiles)
2. Candidate crops extracted from source GeoTIFF rasters (E33 non-truncating path)
3. Each crop submitted to verifier via real-time Application Programming Interface (API) with the specified verifier configuration
4. Probability threshold swept 0.0--1.0 in 0.05 steps (the adversarial-text 150 px N=1 arm was originally swept in 0.1 steps and was regenerated to this grid on 2026-08-03; see [§ Changelog](#changelog))
5. F1/P/R computed via Hungarian matching at 20 m tolerance
6. Bootstrap CIs via tile-level resampling (K=1,000, seed=42)
7. Crop sizes tested: 40, 75, 150, 300 px; strategies tested: adversarial-text, brief-text, checklist-text; consensus tested: N=1 T=0.0 vs N=5 T=0.7

## Changelog

### 2026-08-03 — E39 fine-grid regeneration of the adversarial-text-150 arm

**Refresh trigger**: wave-4 verification triage family
`w4-e39-superseded-sweep-instrument` (row `017#52[2]`) in
`reports/verification/c4-triage/mismatch-triage-2026-08-02-wave4.json` found
that the committed sweep for `adversarial-text-150 / text-n1-t0.0-minimal` was a
step-0.1 / 100-bootstrap artefact, while all six sibling arms were step-0.05 /
1000-bootstrap. This document published that coarse-grid optimum beside
fine-grid sibling figures as a like-for-like comparison.

**Mechanism**: a 0.1 threshold grid contains no 0.15 row, so the adversarial
arm's optimum was pinned to threshold 0.20 (F1 0.7669) when its optimum on the
common grid is threshold 0.15 (F1 0.7701). The defect was incommensurable grids,
not arithmetic — the regenerated fine-grid sweep's threshold-0.20 row reproduces
the old optimum exactly (F1 0.7669, P 0.7771, R 0.7570, n 525). Regenerated on
sapphire with the same generator (`scripts/evaluate_pv_results.py sweep`,
`--step 0.05 --bootstrap 1000 --seed 42`) from the archived probabilities and
candidate manifest; zero API calls. The superseded artefact is retained at
`archive/superseded-sweeps/pv-phase1-adversarial-text-150/`.

**Before → after** (adversarial-text-150, N=1, T=0.0 — the row that appears in
all three tables above):

| Quantity | Before | After |
|---|---|---|
| Optimal threshold | 0.20 | 0.15 |
| F1 | 0.7669 | 0.7701 |
| Precision | 0.7771 | 0.7759 |
| Recall | 0.7570 | 0.7644 |
| n accepted | 525 | 531 |
| F1 95% CI | [0.7323, 0.8095] | [0.7466, 0.7943] |
| Verifier F1 gain over proposer | +0.1617 | +0.1649 |
| N=5 minus N=1 F1 | +0.0068 | +0.0036 |

**Ranking changes** — two nominal reversals, both far inside CI overlap, neither
altering a decision or a substantive conclusion:

- **Verifier strategy**: adversarial-text (0.7701) now edges ahead of
  checklist-text (0.7694), reversing the previously published ordering. The
  selected verifier was already adversarial-text.
- **Crop size**: 150 px (0.7701) now edges ahead of 75 px (0.7681) as the
  nominal best. The selected crop size was already 150 px.

**Selected operating point changed**: the optimal threshold moves from 0.20 to
0.15. This is the one consequential change in this revision.

**What did NOT change**: the proposer-only baseline (the threshold-0.0 row is
identical across all seven arms by construction); every "statistically
equivalent / overlapping CIs" conclusion, each re-checked against the
regenerated interval; the selected verifier strategy, crop size, pass count, and
temperature; and all sibling-arm figures.

**Method note on confidence intervals**: `scripts/lib_advanced_metrics.py`
switched the bootstrap from the percentile method to bias-corrected and
accelerated (BCa) at commit `2026999ad` (2026-04-30). The regenerated
adversarial row therefore carries a BCa CI while every other row here retains a
percentile-era CI, as flagged by the † marker and the note under
[§ Key Finding](#key-finding). Point estimates reproduce exactly across the
method change; CIs do not and cannot. Era CIs were deliberately not
reconstructed — a CI mismatch against any pre-May-2026 sweep is expected and
should not be read as a defect.

**Cross-references**: erratum E39
(`docs/methodology/preregistration/protocol-errata.md`, entry dated 2026-03-21),
whose published figure of 0.770 for adversarial-text was correct all along —
the disposition is "erratum right, committed artefact and published table
wrong"; triage family `w4-e39-superseded-sweep-instrument`.

**Landed in**: this document's revision commit (`fix(results): E39 —
regenerate adversarial fine-grid sweep, correct pv-phase1 comparison table`) —
see `git log` for this file.

### 2026-03-21 — Original publication

Published in commit `9a1b9e1d5` ("feat(pv): validate verifier strategy choice +
add phase-gate process"), alongside the checklist-text and brief-text sweeps
that the strategy comparison was built to test. Reported the PV pipeline lifting
F1 from 0.6052 (proposer only) to 0.7669, with verifier performance insensitive
to crop size, not improved by consensus, and equivalent across the three
instruction strategies; optimal threshold 0.20. The adversarial-text-150 N=1
T=0.0 figures came from a step-0.1 / 100-bootstrap sweep; every other arm used
step-0.05 / 1000-bootstrap.
