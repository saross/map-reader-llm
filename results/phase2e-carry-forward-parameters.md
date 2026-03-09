# Phase 2e Carry-Forward Parameters

**Created**: 2026-03-09 (retrospective; experiment executed 2026-02-12)
**Source**: Phase 2e analysis (`outputs/phase2e/analysis_summary.md`,
`outputs/phase2e/analysis_report.json`)
**Session**: Session 33 (commits `8f34ed4`, `de6ac2e`, `8118eb5`, `7a038b6`)
**Carries forward to**: Phase 3 (all hypotheses)

## Context

Phase 2e tested H4 (Example Ordering) across 4 conditions with K=10 independent
runs each, using carry-forward parameters from Phases 2a–2d. Analysis used
bootstrapped 95% Confidence Intervals (CIs) (n=1,000) with Benjamini-Hochberg
False Discovery Rate (FDR) correction at q=0.05.

Phase 2e is single-track (image-using only). Text-only prompts do not include
in-context example images, so there is nothing to reorder.

### Errata Affecting Design

- **E29**: `reorder_examples()` canonical-first was a no-op in prior phases.
  All Phases 2a–2d used config-file order, not true canonical-first.
- **E30**: Phase 2e tests 4 ordering conditions instead of preregistered 3,
  adding config-default as a distinct condition (zero additional API cost via
  symlinks to Phase 2c data).
- **E31**: Fixed-ordering conditions at T=0.0 produce identical outputs across
  all K=10 runs. Four of 9 remaining deterministic units copied from existing
  runs rather than re-executed.

## Results Summary

### Track 1: Image-Using (brief-text-image, T=0.0, plus-hp, minimal)

| Condition | Ordering | F1 | 95% CI | Precision | Recall |
|-----------|----------|---:|:------:|----------:|-------:|
| **config-default** | [C+, HP, C−, null] | **0.609** | [0.485, 0.701] | 0.524 | 0.726 |
| canonical-last | [HP, null, C+, C−] | 0.609 | [0.529, 0.722] | 0.526 | 0.722 |
| canonical-first | [C+, C−, HP, null] | 0.579 | [0.463, 0.671] | 0.497 | 0.693 |
| random | shuffled per-run | 0.529 | [0.440, 0.616] | 0.453 | 0.634 |

**FDR-significant comparisons**: 0/6. Two comparisons initially significant at
α=0.05 (config-default vs random, canonical-last vs random) did not survive FDR
correction across 6 comparisons.

### Track 2: Text-Only

Not applicable — text-only prompts do not include example images. Text-only
carries forward unchanged from Phase 2d.

## Carry-Forward Decision

**H4 = config-default ordering selected (no change from prior phases).**

### Decision Rule Applied

The preregistered decision rule states: "Select ordering with highest mean F1."
Config-default and canonical-last are tied at F1=0.609. Protocol guidance
specifies: if config-default is within 0.02 F1 of the best, prefer
config-default for consistency with prior phases. Config-default meets this
criterion (ΔF1 = −0.003 vs canonical-last bootstrap mean).

### Mechanism

Fixed orderings outperform random (ΔF1 ≈ 0.07–0.08), but among fixed
orderings, specific arrangement has minimal effect. The random condition's lower
performance may reflect per-run shuffling introducing inconsistency rather than
ordering per se — each run sees a different example sequence, preventing the
model from developing stable associations.

## Fixed Parameters for Phase 3

| Parameter | Value | Source |
|-----------|-------|--------|
| M/E | brief-text-image / brief-text | Phase 2a |
| Temperature | 0.0 | Phase 2b |
| Library | plus-hp (13 examples) | Phase 2c |
| H5 Treatment | minimal (no exclusion text) | Phase 2d |
| H4 Ordering | config-default [C+, HP, C−, null] | Phase 2e |
| Config file | `prompts/configs/library_plus-hp.json` | Phases 2a–2e |
| Instruction file | `prompts/system-instructions/detect_brief-text-image.md` | Phases 2a–2e |

## Key Observations

- **T=0.0 determinism paradox.** Fixed-ordering conditions produce identical
  outputs across K=10 runs. This means K=10 serves as verification of
  reproducibility rather than variance estimation (Observation 128).

- **Fixed orderings outperform random.** The ~0.07 F1 gap between fixed and
  random orderings suggests consistency matters more than specific arrangement.

- **No ordering sensitivity among fixed conditions.** Config-default,
  canonical-first, and canonical-last produce very similar results, suggesting
  the model is robust to example order within fixed sequences.

## References

- Analysis summary: `outputs/phase2e/analysis_summary.md`
- Analysis report: `outputs/phase2e/analysis_report.json`
- Per-run metrics: `outputs/phase2e/per_run_metrics.csv`
- Phase 2d carry-forward: `results/phase2d-carry-forward-parameters.md`
- Session 33 log: `docs/notes/reflections/session-log.md`
- Protocol errata: E29, E30, E31 in `docs/methodology/preregistration/protocol-errata.md`
- Decision 18: `docs/methodology/preregistration/decisions-log.md`
