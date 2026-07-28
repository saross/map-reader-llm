# Phase 2d Carry-Forward Parameters

**Created**: 2026-02-12
**Source**: Phase 2d analysis (Track 1: `results/phase2d-track1-image-analysis.md`,
Track 2: `results/phase2d-track2-text-analysis.md`)
**Carries forward to**: Phase 2e (H4 Example Ordering)

## Context

Phase 2d tested H5 (Negative Text Treatment) across 3 conditions (minimal,
terse, verbose) with K=10 independent runs each, using the carry-forward
parameters from Phase 2c (plus-hp library, T=0.0). Analysis used bootstrapped
95% CIs (n=1000) with Benjamini-Hochberg FDR correction at q=0.05.

Both tracks were executed in a dual-track OFAT design (Decision 17):

- Track 1 (image-using): brief-text-image M/E, plus-hp library, T=0.0
- Track 2 (text-only): brief-text M/E, T=0.0 (library N/A — text-only)

## Results Summary

### Track 1: Image-Using (brief-text-image, T=0.0, plus-hp)

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| **minimal** | **0.609** | [0.485, 0.701] | 0.524 | 0.726 |
| verbose | 0.578 | [0.443, 0.669] | 0.508 | 0.670 |
| terse | 0.571 | [0.484, 0.658] | 0.493 | 0.680 |

**FDR-significant comparisons**: 0/3. No pairwise differences significant.

### Track 2: Text-Only (brief-text, T=0.0)

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| **minimal** | **0.660** | [0.533, 0.759] | 0.559 | 0.807 |
| terse | 0.602 | [0.450, 0.729] | 0.506 | 0.742 |
| verbose | 0.548 | [0.431, 0.646] | 0.480 | 0.639 |

**FDR-significant comparisons**: 1/3 (minimal vs verbose: ΔF1 = +0.114,
p < 0.05 after FDR correction).

## Carry-Forward Decision

**H5 = minimal (no exclusion guidance) selected for both tracks.**

### Decision Rule Applied

The decision rule declared in the Phase 2d study YAML
(`studies/phase2d-h5-negtext.yaml:133-139`): select the level with
highest mean F1 only if terse or verbose *significantly* improves on
minimal; "If no significant differences: Use Minimal (simplest) as
default — Occam's razor." This is an operational rule adopted at
execution time — the preregistration specifies no carry-forward
selection rule, and an earlier version of this section quoted a
"Select condition with highest F1" rule that exists in no document
(corrected 2026-07-28, D17 audit FALSE-5). Applied here: Track 1 has
0/3 significant comparisons, so minimal is selected under the
no-significant-difference Occam's-razor branch; Track 2's single
significant comparison favours minimal (+0.114 vs verbose), so no
alternative significantly improves on it. Minimal also happens to hold
the highest point estimate in both tracks:

- Track 1: minimal (0.609) > verbose (0.578) > terse (0.571)
- Track 2: minimal (0.660) > terse (0.602) > verbose (0.548)

The minimal condition's superiority is consistent across both modalities.

### Mechanism

Exclusion guidance (terse and verbose) reduces both precision and recall
relative to the baseline. The model becomes overly conservative when given
explicit exclusion criteria, increasing false negatives without meaningfully
reducing false positives. In Track 2 (text-only), the effect is larger and
statistically significant for the verbose condition, consistent with the
hypothesis that image examples partially buffer against harmful effects of
exclusion guidance.

### Cross-Track Insight

Image examples buffer approximately 70% of the exclusion guidance effect:

- Track 2 (text-only): minimal → verbose ΔF1 = −0.112 (significant)
- Track 1 (image-using): minimal → verbose ΔF1 = −0.031 (non-significant)

This suggests visual anchors provide robustness against degradation from
exclusion instructions, but the baseline (no exclusion text) remains optimal
in both modalities.

### Practical Implication for Phase 2e

The minimal condition uses the instruction file `detect_brief-text-image.md`,
which contains full two-sentence Guideline 3 and no exclusion section. This
is the same instruction file used throughout Phases 2a-2c, so Phase 2e
requires no instruction file changes.

## Fixed Parameters for Phase 2e

| Parameter | Value | Source |
|-----------|-------|--------|
| M/E | brief-text-image | Phase 2a |
| Temperature | 0.0 | Phase 2b |
| Library | plus-hp (13 examples) | Phase 2c |
| H5 Treatment | minimal (no exclusion text) | Phase 2d |
| Ordering | Under test | Phase 2e (H4) |
| Config file | `prompts/configs/library_plus-hp.json` | Phases 2a-2d |
| Instruction file | `prompts/system-instructions/detect_brief-text-image.md` | Phases 2a-2d |

## Phase 2e Design (H4 Example Ordering)

Phase 2e tests 3 ordering conditions (image-using track only):

| Condition | Description | Ordering |
|-----------|-------------|----------|
| canonical-first | Default config order (baseline) | [C+, HP, C−, null] |
| canonical-last | All canonical examples moved to end | [HP, null, C+, C−] |
| random | Reproducibly shuffled (per-run seeds) | Varies per run |

Phase 2e is single-track (image-using only). Text-only prompts do not include
in-context example images, so there is nothing to reorder.

## Key Observations

- **Exclusion guidance hurts, not helps.** Both modalities perform best with
  no exclusion text. More guidance makes the model more conservative without
  improving discrimination.

- **Image examples provide robustness.** The text-only modality is more
  sensitive to exclusion guidance degradation (~3.5× larger effect than
  image-using), suggesting visual anchors stabilise performance.

- **Near-determinism at T=0.0 continues.** Track 1 terse and verbose
  produced identical F1 across all 10 runs; Track 2 showed minimal variance
  (2-3 distinct values across runs).

## References

- Track 1 analysis: `results/phase2d-track1-image-analysis.md`
- Track 2 analysis: `results/phase2d-track2-text-analysis.md`
- Track 1 JSON: `results/phase2d-track1-image-analysis.json`
- Track 2 JSON: `results/phase2d-track2-text-analysis.json`
- Phase 2c carry-forward: `results/phase2c-carry-forward-parameters.md`
- Decision 17 (Phase 2d design): `docs/methodology/preregistration/decisions-log.md`
