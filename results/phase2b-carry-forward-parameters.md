# Phase 2b Carry-Forward Parameters

**Created**: 2026-02-08
**Source**: Phase 2b analysis (Track 1: `results/phase2b-track1-image-summary.md`,
Track 2: `results/phase2b-track2-text-summary.md`)
**Carries forward to**: Phase 2c (H8 Library Composition)

## Context

Phase 2b tested H7 (Temperature) across 5 levels (T=0.0, T=0.3, T=0.7,
T=1.0, T=1.3) with K=10 independent runs each, using the dual-track
carry-forward from Phase 2a (Decision 16, E27). Analysis used bootstrapped
95% CIs (n=1000) with Benjamini-Hochberg FDR correction at q=0.05.
FDR correction was applied within each track independently, as the tracks
represent independent OFAT chains.

## Results Summary

### Track 1: Image-Using (brief-text-image)

| Temperature | F1 | 95% CI | Precision | Recall |
|-------------|---:|:------:|----------:|-------:|
| T0.0 | 0.5574 | [0.453, 0.643] | 0.4761 | 0.6722 |
| T0.3 | 0.5492 | [0.457, 0.631] | 0.4645 | 0.6722 |
| T0.7 | 0.4814 | [0.403, 0.557] | 0.4060 | 0.5918 |
| T1.0 | 0.4578 | [0.369, 0.532] | 0.3830 | 0.5691 |
| T1.3 | 0.4387 | [0.349, 0.506] | 0.3640 | 0.5526 |

**FDR-significant comparisons**: 6/10. Clear separation between
{T0.0, T0.3} and {T0.7, T1.0, T1.3}. T0.0 vs T0.3 not significant.

### Track 2: Text-Only (brief-text)

| Temperature | F1 | 95% CI | Precision | Recall |
|-------------|---:|:------:|----------:|-------:|
| T0.0 | 0.6602 | [0.533, 0.759] | 0.5585 | 0.8072 |
| T0.3 | 0.6212 | [0.484, 0.731] | 0.5068 | 0.8031 |
| T0.7 | 0.5672 | [0.436, 0.685] | 0.4510 | 0.7660 |
| T1.0 | 0.5687 | [0.432, 0.677] | 0.4559 | 0.7567 |
| T1.3 | 0.5258 | [0.402, 0.633] | 0.4113 | 0.7299 |

**FDR-significant comparisons**: 4/10. T0.0 significantly better than
T0.7, T1.0, and T1.3. T0.0 vs T0.3 not significant.

## Carry-Forward Decision

**T=0.0 (deterministic decoding) selected for both tracks.**

### Decision Rule Applied

The preregistered decision rule states: "If T=1.0 (default) is within
0.02 F1 of best, prefer T=1.0 for simplicity." T=1.0 is NOT within 0.02
of T=0.0 in either track:

- Track 1: T0.0 − T1.0 = +0.0992 (well outside 0.02 threshold)
- Track 2: T0.0 − T1.0 = +0.0961 (well outside 0.02 threshold)

T=0.0 is unambiguously optimal. Both tracks show clean monotonic
degradation with increasing temperature.

### Mechanism

Higher temperatures increase detection count (more false positives) while
recall drops modestly. The precision-recall tradeoff is strongly
asymmetric — precision degrades faster than recall improves, driving the
F1 decrease. This is consistent with findings from the handwriting
recognition project.

### Cross-Track Consistency

The optimal temperature (T=0.0) is the same in both tracks. The text-only
advantage from Phase 2a persists at every temperature level (~+0.10 F1),
confirming that temperature and modality effects are additive rather than
interactive.

## Fixed Parameters for Phase 2c

| Parameter | Track 1 (image) | Track 2 (text) | Source |
|-----------|-----------------|----------------|--------|
| M/E | brief-text-image | brief-text | Phase 2a |
| Temperature | 0.0 | 0.0 | Phase 2b |
| Ordering | Canonical-first | Canonical-first | Preregistered default |

## Phase 2c Design (H8 Library Composition)

Phase 2c tests 5 library conditions (of 7 preregistered; Scale-16 and
Scale-32 deferred per E11):

| Condition | Canon+ | Canon- | HP | HN | Null | Total |
|-----------|--------|--------|----|----|------|-------|
| Pure Positive Canon | 4 | 0 | 0 | 0 | 3 | 7 |
| Canonical | 4 | 2 | 0 | 0 | 3 | 9 |
| +HP | 4 | 2 | 4 | 0 | 3 | 13 |
| Scale-4 | 4 | 2 | 2 | 2 | 3 | 13 |
| Scale-8 | 4 | 2 | 4 | 4 | 3 | 17 |

Planned contrasts:

- C1: Pure Positive Canon vs Canonical (effect of canonical negatives)
- C2: Canonical vs +HP (effect of hard positives)
- C3: +HP vs Scale-4 (HP-only vs balanced HP+HN at matched size)
- S1: Scale-4 vs Scale-8 (scaling effect)

Each track runs independently with its own library configs:

- Track 1: `prompts/configs/library_*.json` (image-using)
- Track 2: `prompts/configs/library_*-text.json` (text-only)

## Key Observations

- Temperature is a critical hyperparameter, not a minor tuning knob:
  +0.10-0.12 F1 improvement from T=1.0 to T=0.0
- Near-deterministic plateau: T0.0 and T0.3 are not statistically
  distinguishable in either track
- The modality gap (~+0.10 F1 for text-only) is stable across all
  temperature levels, confirming additive rather than interactive effects
- These findings are consistent with the handwriting recognition project's
  temperature results

## References

- Track 1 analysis: `results/phase2b-track1-image-summary.md`
- Track 2 analysis: `results/phase2b-track2-text-summary.md`
- Track 1 per-run metrics: `outputs/phase2b/track1-image/per_run_metrics.csv`
- Track 2 per-run metrics: `outputs/phase2b/track2-text/per_run_metrics.csv`
- Phase 2c Track 1 YAML: `studies/phase2c-h8-library.yaml`
- Phase 2c Track 2 YAML: `studies/phase2c-h8-library-text-only.yaml`
- Decision 16 / E27: `docs/methodology/preregistration/decisions-log.md`
- E11 (Scale-16/32 deferral): `docs/methodology/preregistration/protocol-errata.md`
