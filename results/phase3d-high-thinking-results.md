# Phase 3d — HIGH-Thinking Verifier Experiment Results

## Metadata

- **Generated**: 2026-03-10
- **Script**: `scripts/reverify_image_only_high_thinking.py`
- **Scope**: 44 image-only candidates from the cross-modal union
- **Verifier**: Adversarial (text-only mode, `include_examples=False`)
- **Verifier config**: T=0.0, thinking=high, model=gemini-3-flash
- **Cost**: ~$0.50 (44 API calls, 0 failures, ~6 minutes)
- **Outputs**:
  `outputs/phase3d-union/verifier_adversarial_high_thinking_probabilities.json`
- **Baseline comparison**:
  `outputs/phase3d-union/verifier_adversarial_probabilities.json`
  (minimal thinking, from the union experiment)

## Hypothesis

Image-only candidates from the cross-modal union have poor precision
(P=0.318 at t=0.11): 7 TPs with 15 FPs. Many of these FPs have
verifier probability 1.0 under minimal thinking — the verifier is
confidently wrong. The hypothesis was that extended reasoning
(`thinking_level="high"`) might help the adversarial verifier catch
subtle differences between genuine mound symbols and confusable map
features, improving precision without sacrificing the 7 TPs.

## Result: HIGH thinking made precision worse

| Config | F1 | P | R | N |
|---|---:|---:|---:|---:|
| Union, all minimal thinking | 0.768 | 0.711 | 0.835 | 114 |
| Union, HIGH for image-only | **0.747** | 0.675 | 0.835 | 120 |
| Text-only single-track (reference) | 0.796 | 0.809 | 0.784 | 94 |

F1 dropped by 0.021. The HIGH-thinking verifier accepted 6 additional
FPs while keeping the same recall. Precision fell from 0.711 to 0.675.

---

## Per-Candidate Comparison

| ID | Minimal | HIGH | Change | Status |
|---:|--------:|-----:|-------:|--------|
| 0 | 1.00 | 0.95 | -0.05 | TP |
| 5 | 0.10 | 0.95 | **+0.85** | FP |
| 6 | 0.00 | 0.00 | 0.00 | FP |
| 7 | 0.90 | 1.00 | +0.10 | FP |
| 14 | 1.00 | 1.00 | 0.00 | FP |
| 15 | 1.00 | 1.00 | 0.00 | FP |
| 25 | 0.00 | 0.00 | 0.00 | FP |
| 28 | 1.00 | 0.95 | -0.05 | TP |
| 30 | 0.05 | 0.95 | **+0.90** | FP |
| 31 | 0.00 | 0.00 | 0.00 | FP |
| 37 | 1.00 | 1.00 | 0.00 | FP |
| 39 | 0.10 | 0.10 | 0.00 | FP |
| 40 | 1.00 | 1.00 | 0.00 | FP |
| 41 | 1.00 | 1.00 | 0.00 | TP |
| 42 | 0.00 | 0.00 | 0.00 | FP |
| 45 | 1.00 | 0.95 | -0.05 | FP |
| 51 | 0.85 | 0.95 | +0.10 | FP |
| 52 | 0.00 | 0.20 | +0.20 | FP |
| 53 | 0.75 | 0.95 | +0.20 | FP |
| 59 | 1.00 | 0.98 | -0.02 | FP |
| 60 | 0.00 | 0.95 | **+0.95** | FP |
| 77 | 0.10 | 0.00 | -0.10 | FP |
| 78 | 0.00 | 0.95 | **+0.95** | FP |
| 87 | 0.95 | 0.95 | 0.00 | FP |
| 90 | 1.00 | 0.95 | -0.05 | FP |
| 96 | 0.00 | 0.00 | 0.00 | FP |
| 102 | 0.40 | 0.95 | **+0.55** | FP |
| 107 | 0.00 | 0.00 | 0.00 | FP |
| 108 | 0.05 | 0.05 | 0.00 | FP |
| 109 | 1.00 | 0.95 | -0.05 | TP |
| 110 | 0.00 | 0.10 | +0.10 | FP |
| 111 | 0.05 | 0.00 | -0.05 | FP |
| 112 | 0.00 | 0.00 | 0.00 | FP |
| 113 | 0.00 | 0.00 | 0.00 | FP |
| 115 | 0.85 | 0.30 | **-0.55** | TP |
| 117 | 1.00 | 0.95 | -0.05 | FP |
| 118 | 1.00 | 0.95 | -0.05 | TP |
| 121 | 0.05 | 0.00 | -0.05 | FP |
| 122 | 0.30 | 0.95 | **+0.65** | FP |
| 124 | 0.00 | 0.00 | 0.00 | FP |
| 126 | 0.00 | 0.00 | 0.00 | FP |
| 127 | 1.00 | 0.95 | -0.05 | FP |
| 128 | 0.05 | 0.95 | **+0.90** | FP |
| 131 | 0.95 | 0.98 | +0.03 | FP |

**Bold** changes exceed +/-0.3 in magnitude.

### Summary of changes

- **12 increased** (>+0.05): almost all FPs rising from low to high
  probability. Candidates 5, 30, 60, 78, 128 went from correctly
  rejected (p <= 0.10) to confidently accepted (p = 0.95).
- **2 decreased** (>-0.05): candidate 115 (TP, 0.85 -> 0.30) and
  candidate 77 (FP, 0.10 -> 0.00). The only TP that changed went in
  the wrong direction.
- **30 stable** (within +/-0.05): most candidates retained similar
  probabilities regardless of thinking level.

---

## Interpretation

### Extended reasoning acts as a liberaliser, not a regulariser

The adversarial verifier prompt asks the model to "argue this is NOT a
mound" and then assess the probability it is one. With minimal thinking,
this produces quick, heuristic rejections that are well-calibrated for
the image-only candidates. With HIGH thinking, the model generates more
elaborate arguments both for and against — and the extended reasoning
appears to produce more ways to *justify* acceptance rather than more
rigorous grounds for rejection.

This is consistent with a known failure mode of chain-of-thought
reasoning: longer reasoning chains can produce more sophisticated
rationalisations rather than better decisions. When the visual evidence
is genuinely ambiguous (these crops do look mound-like), more reasoning
generates more ways to interpret the visual features favourably.

### The image-only FP problem is perceptual, not reasoning-limited

The 15 FPs that pass the minimal-thinking verifier are not cases where
the model would change its mind with more thought. They are locations
where the map crop genuinely contains features that visually resemble
burial mound symbols — contour patterns, vegetation markers, or other
circular/semicircular features. No amount of reasoning at the verifier
stage can overcome this, because the crop image is genuinely ambiguous.

The discriminating information — that the text-based proposer did NOT
flag this location — is not available to the verifier. Adding this
provenance signal as input (provenance-informed verification) would be
a qualitatively different experiment that provides genuinely new
information rather than more reasoning time.

### Minimal thinking may act as beneficial regularisation

The observation that minimal thinking outperforms HIGH thinking on this
task suggests that the thinking budget constraint acts as a form of
regularisation. Forced to make a quick decision, the model relies on
the most salient visual features, which happen to correlate well with
ground truth. Given more reasoning budget, the model over-analyses
ambiguous cases and generates false confidence.

This pattern may be task-specific: for more complex verification tasks
(e.g., distinguishing between closely related symbol types), HIGH
thinking might still help. But for this binary mound/not-mound task
on pre-selected candidate crops, the minimal-thinking verifier is
already well-calibrated.

---

## Implications

1. **HIGH-thinking verification is not a path to F1 > 0.8.** The
   experiment directly refutes the hypothesis that extended reasoning
   improves precision on image-only candidates.

2. **The text-only single-track pipeline (F1=0.796) remains the best
   F1 configuration.** No post-hoc processing of union results matches
   it.

3. **The union pipeline's value is recall (0.835), not F1.** For
   applications where recall is paramount, the union is preferred; for
   balanced F1, text-only is preferred.

4. **Remaining precision improvement options** are limited to approaches
   that add genuinely new information (provenance-informed verification,
   better proposer) rather than more reasoning on the same information.
