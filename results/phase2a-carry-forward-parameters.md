# Phase 2a Carry-Forward Parameters

**Created**: 2026-02-08
**Source**: Phase 2a analysis (`outputs/phase2a/analysis_summary.md`)
**Carries forward to**: Phase 2b (H7 Temperature)

## Context

Phase 2a tested H1 (Modality/Elaboration Level) across 5 conditions with
K=10 independent runs each, at T=1.0 (vendor default), canonical-first
ordering, and Scale-8 library. Analysis used bootstrapped 95% confidence
intervals (CIs) with Benjamini-Hochberg False Discovery Rate (FDR)
correction at q=0.05.

## Results Summary

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| brief-text | 0.5425 | [0.424, 0.650] | 0.4338 | 0.7247 |
| verbose-text | 0.4710 | [0.355, 0.569] | 0.3644 | 0.6660 |
| brief-text-image | 0.4617 | [0.371, 0.541] | 0.3934 | 0.5588 |
| verbose-text-image | 0.4369 | [0.358, 0.507] | 0.3675 | 0.5392 |
| image-only | 0.4252 | [0.340, 0.500] | 0.3492 | 0.5454 |

**FDR-significant comparisons**: 0/10 (3/10 initially significant before
correction). The lack of FDR significance motivated the dual-track
carry-forward decision.

## Carry-Forward Decision

**Decision 16 / Erratum E27**: Dual-track carry-forward.

The preregistered OFAT design specified carrying forward the single best
M/E level. However, the best overall condition (brief-text, F1=0.5425) was
text-only, which cannot participate in Phases 2d (H5 negative text
treatment, requires images) or Phase 3c (H9 diversity testing, requires
images). No pairwise differences survived FDR correction, so there is no
statistical basis for declaring a single winner.

**Resolution**: Two independent tracks carried forward:

### Track 1: Image-Using (Preregistered OFAT Chain)

- **Condition**: brief-text-image
- **F1**: 0.4617 [0.371, 0.541]
- **Config**: `prompts/configs/detect_brief-text-image.json`
- **Rationale**: Best image-using M/E level; required for H5 and H9 testing
- **Status**: Confirmatory (preregistered OFAT sequence continues)

### Track 2: Text-Only (Exploratory)

- **Condition**: brief-text
- **F1**: 0.5425 [0.424, 0.650]
- **Config**: `prompts/configs/detect_brief-text.json`
- **Rationale**: Best overall performer; tests whether text-only advantage
  persists across subsequent parameter optimisations
- **Status**: Exploratory (deviation from preregistered single-winner design)

## Fixed Parameters for Phase 2b

| Parameter | Value | Source |
|-----------|-------|--------|
| Library | Scale-8 (17 examples) | Preregistered default |
| Ordering | Canonical-first | Preregistered default |
| M/E (Track 1) | brief-text-image | Phase 2a optimal image-using |
| M/E (Track 2) | brief-text | Phase 2a optimal overall |

## Key Observations

- Text-only (brief-text) outperformed all image-using conditions, contrary
  to H1's prediction that images would improve detection
- The modality gap (~+0.08 F1 for text-only vs best image-using) is
  consistent but not statistically significant after FDR correction
- Brief elaboration outperformed verbose elaboration in both modalities

## References

- Analysis summary: `outputs/phase2a/analysis_summary.md`
- Decision 16: `docs/methodology/preregistration/decisions-log.md`
- Erratum E27: `docs/methodology/preregistration/protocol-errata.md`
- Phase 2b Track 1 YAML: `studies/phase2b-h7-temperature.yaml`
- Phase 2b Track 2 YAML: `studies/phase2b-h7-temperature-text-only.yaml`
