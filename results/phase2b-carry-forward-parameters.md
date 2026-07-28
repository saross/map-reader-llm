# Phase 2b Carry-Forward Parameters (Retest-Era)

**Created**: 2026-04-24 (Session 75, Step 4 item 3 — Option B residual)
**Source**: Phase 2b retest (340-tile K=3; Track 1 image + Track 2 text)
**Primary analysis**: `results/retest/phase2b/analysis_summary.md`
**Raw evaluation JSONs**:
  `results/retest/phase2b-track1-evaluation.json` +
  `results/retest/phase2b-track2-evaluation.json`
**Retest-production-summary narrative embedding**: `results/retest/retest-production-summary.md` §Phase 2b
**Carries forward to**: Phase 2c (H8 Library Composition), Phase 2d (H5 Negation Text), Phase 2e (H4 Example Ordering)
**Supersedes**: pre-retest 60-tile K=10 pilot (archived at `archive/outputs-pre-retest-60-tile/phase2b/carry-forward-parameters.md` + `...carry-forward-parameters-with-retention-banner.md`)

## Context

Phase 2b retest tested H7 (Temperature) across 5 levels (T=0.0, T=0.3,
T=0.7, T=1.0, T=1.3) with K=3 independent runs each, using the dual-track
carry-forward from Phase 2a (Decision 16, E27). Analysis used bootstrapped
95 % CIs (n=1,000, seed=42, tile-level-multi-run resampling) with
Benjamini–Hochberg FDR correction at q=0.05, applied within each track
independently (the tracks represent independent OFAT chains).

The retest replaces a 60-tile K=10 pilot (archived 2026-04-23 + 2026-04-24)
whose headline finding was qualitatively identical (T=0.0 optimal on both
tracks, T=1.0 / T=1.3 worse) but with less statistical power. The retest
at 340 tiles × K=3 sharpens the pairwise significance pattern (6/10 Track 1
and 5/10 Track 2 pairwise contrasts FDR-significant, vs 6/10 and 4/10 in
the pilot).

## Results summary

### Track 1: Image-Using (brief-text-image)

| Temperature | F1 | 95 % CI | Precision | Recall |
|-------------|---:|:-------:|----------:|-------:|
| **T=0.0** | **0.587** | **[0.541, 0.633]** | **0.499** | **0.713** |
| T=0.3 | 0.575 | [0.528, 0.612] | 0.488 | 0.699 |
| T=0.7 | 0.537 | [0.489, 0.580] | 0.452 | 0.660 |
| T=1.0 | 0.527 | [0.474, 0.561] | 0.440 | 0.657 |
| T=1.3 | 0.490 | [0.459, 0.540] | 0.406 | 0.618 |

**FDR-significant comparisons**: 6/10. T=0.0 significantly better than
T=0.7 (ΔF1 = +0.050, p = 0.002), T=1.0 (+0.064, p = 0.001), and T=1.3
(+0.085, p = 0.001). T=0.3 also significantly better than T=1.0 and T=1.3.
T=0.7 significantly better than T=1.3. T=0.0 vs T=0.3 not significant
(ΔF1 = +0.015, p = 0.30).

### Track 2: Text-Only (brief-text)

| Temperature | F1 | 95 % CI | Precision | Recall |
|-------------|---:|:-------:|----------:|-------:|
| **T=0.3** | **0.606** | **[0.553, 0.654]** | **0.491** | **0.793** |
| T=0.0 | 0.605 | [0.547, 0.655] | 0.487 | 0.798 |
| T=0.7 | 0.584 | [0.521, 0.636] | 0.461 | 0.798 |
| T=1.3 | 0.544 | [0.487, 0.603] | 0.425 | 0.756 |
| T=1.0 | 0.533 | [0.432, 0.583] | 0.415 | 0.748 |

**FDR-significant comparisons**: 5/10. T=0.0 significantly better than
T=1.0 (ΔF1 = +0.093, p = 0.001) and T=1.3 (+0.057, p = 0.004). T=0.3
also significantly better than T=1.0 and T=1.3. T=0.7 significantly
better than T=1.0 (+0.072, p = 0.004). T=0.0 vs T=0.3 not significant
(ΔF1 = −0.002, p = 0.862, essentially tied).

## Carry-forward decision

**T=0.0 (deterministic decoding) selected for both tracks.**

### Decision rule applied

The decision rule declared in the Phase 2b study YAML
(`studies/phase2b-h7-temperature.yaml:125`): *"If T=1.0 (default) is
within 0.02 F1 of best, prefer T=1.0 for simplicity."* This is an
operational tie-break adopted at execution time — the preregistration
specifies **no** carry-forward tie-break rule (corrected 2026-07-28, D17
audit FALSE-3). T=1.0 is NOT within 0.02 of best in either track:

- Track 1 image: T=0.0 − T=1.0 = +0.060 (well outside 0.02 threshold)
- Track 2 text: T=0.3 − T=1.0 = +0.073 (well outside 0.02 threshold)

T=0.0 is unambiguously optimal. Both tracks show monotonic (Track 1) or
near-monotonic (Track 2, with T=0.0 / T=0.3 tied at the top) degradation
with increasing temperature.

### Note on Track 2 T=0.0 vs T=0.3 tie

On the text track, T=0.0 and T=0.3 are statistically indistinguishable
(p = 0.862). The carry-forward selects T=0.0 because ΔF1 is effectively
zero and T=0.0 is the simpler default (deterministic decoding). A reader
wishing to argue for T=0.3 on the text track has no statistical objection
from this data, only the convention that deterministic decoding is the
preferred default when the best-T is statistically indistinguishable from
the next-best-T.

### Mechanism

Higher temperatures increase detection count (more false positives) while
recall drops modestly. The precision-recall trade-off is strongly
asymmetric — precision degrades faster than recall improves, driving the
F1 decrease. Pattern is consistent across both tracks and across both the
pre-retest pilot and this retest.

## Cross-reference to the consensus-stage temperature finding

**T=0.0 is the single-pass Phase 2b optimum; it is NOT the consensus-stage
optimum.** Phase 3a and the 55-map generalisation work found T=0.7 to be
optimal for K=5 consensus aggregation. The two findings are compatible:
at higher K, consensus voting averages out some of the T>0 noise, so a
modest T>0 benefits aggregation.

The Phase 2b carry-forward (T=0.0) applies to downstream Era 1 Phases
2c–2e which are single-pass evaluations. Production consensus runs (Era
2 / 3, 55-map) use the consensus-stage optimum T=0.7. See:

- `docs/notes/reflections/working-notes.md` Obs 116, 177, 209 (consensus-
  stage temperature story)
- `results/retest/phase2b/analysis_summary.md` §Caveat 3 (full discussion
  of the single-pass ≠ consensus-stage crossover)
- Protocol errata E49, E51, E52 (library-axis retests use T=0.7, the
  production operating point, not the Phase-2b-optimal T=0.0)

## T=1.0 distinction — preregistered vs E43 UNINTENDED

T=1.0 requires careful language in the paper. Two separate things
happened:

1. **T=1.0 as a preregistered test condition (this carry-forward's
   Phase 2b).** The preregistration specified testing T=0.0, 0.3, 0.7,
   1.0, 1.3 to characterise the temperature response surface. The
   finding that T=1.0 performs poorly is a legitimate, preregistered
   result and is the scientific basis for the paper's practitioner
   claim that users should change the Gemini API default.
2. **T=1.0 as an accidental deployment (E43).** Separately, production
   consensus runs at 384 px were inadvertently run at T=1.0 when T=0.7
   was intended. This was a configuration error documented in errata
   E43, producing the `outputs/h11/consensus-384-UNINTENDED-T1.0/` and
   `outputs/h11/single-pass-384-UNINTENDED-T1.0/` directories. The
   error was detected and the correct condition re-run; the UNINTENDED
   directories are retained with dual-role READMEs (commit `5ae94041`)
   as serendipitous Era 2 / 487-tile T=1.0 scope coverage.

The paper cites (1) as the evidence that T=1.0 is suboptimal. The
accidental deployment (2) is an honest-reporting detail for the errata
section and may be referenced for Era 2 scope where Phase 2b's 340-tile
corpus cannot extend, but it is not the scientific basis for the
temperature finding.

## References

- Primary analysis: `results/retest/phase2b/analysis_summary.md`
- Evaluation JSONs: `results/retest/phase2b-track{1,2}-evaluation.json`
- Metadata sidecars: `results/retest/phase2b-track{1,2}-evaluation.metadata.json`
- Aggregated embedding: `results/retest/retest-production-summary.md` §Phase 2b
- Raw detections: `outputs/retest/phase2b/track{1-image,2-text}/T{0.0,0.3,0.7,1.0,1.3}/run_{1,2,3}/`
- Study YAMLs: `studies/retest/phase2b-h7-temperature.yaml`, `studies/retest/phase2b-h7-temperature-text-only.yaml`
- Pre-retest pilot (archived): `archive/outputs-pre-retest-60-tile/phase2b/`
- E43 UNINTENDED distinction: `docs/methodology/preregistration/protocol-errata.md` §E43
- Dual-track carry-forward decision (from Phase 2a): `docs/methodology/preregistration/protocol-errata.md` §E27
