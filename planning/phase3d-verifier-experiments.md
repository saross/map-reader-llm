# Phase 3d — Verifier Improvement Experiments

Planning document for five follow-up experiments on the two-stage
proposer-verifier pipeline, plus one deferred option.

## Context

The best configurations from Phase 3d so far:

| Pipeline | F1 | P | R | N |
|----------|---:|---:|---:|---:|
| Text-only single-track + adversarial | **0.796** | 0.809 | 0.784 | 94 |
| Cross-modal union + adversarial | 0.768 | 0.711 | **0.835** | 114 |
| Image single-track + adversarial | 0.711 | 0.711 | 0.711 | 97 |

The union pipeline achieves the best recall (0.835) but F1 is held back
by low precision on image-only candidates (P=0.318, 7 TP with 15 FP).
Approaches tested so far (HIGH thinking, provenance-aware thresholding,
multi-verifier ensemble) have all failed to improve this.

All experiments below target the **44 image-only candidates** from the
union experiment unless otherwise stated. The existing verifier
probabilities (`outputs/phase3d-union/verifier_adversarial_probabilities.json`)
serve as the baseline (minimal thinking, text-only mode, T=0.0).

---

## Experiment A: Provenance-Informed Verification

**Priority**: 1 (highest expected value)
**Estimated cost**: ~$1 (44 API calls)
**Status**: COMPLETE (2026-03-10, Session 46)
**Result**: **Best of the three experiments.** ΔF1=+0.011, ΔP=+0.019,
ΔR=0.000. Removed 3 FPs (15→12) with 0 TPs lost. Image-only P
improved from 0.318 to 0.368. Did not reach F1>0.796 target.
**Cost**: ~$0.13 (44 API calls, 0 failures)
**Results**: `results/phase3d-verifier-experiments-abc.md`

### Rationale

Every verifier configuration tested so far sees each candidate crop in
isolation — it has no information about what other pipeline stages
concluded. The text track's *absence* of a detection at a given location
is a meaningful negative signal: image-only candidates have P=0.318
compared to P=0.867 for both-track candidates. Telling the verifier
about this provenance is the only approach that provides genuinely new
information rather than more reasoning time or different prompting on
the same inputs.

### Design

- **Scope**: Re-verify the 44 image-only union candidates
- **Modification**: Add a provenance preamble to the verifier prompt:
  *"Note: This candidate was detected by the image-based analyser ONLY.
  A separate text-based analysis of the same map area did NOT flag this
  location. Consider whether this absence is informative."*
- **Verifier**: Adversarial (`verify_adversarial.md`), with the
  provenance preamble prepended
- **Config**: T=0.0, thinking=minimal, include_examples=False
  (matching the baseline union experiment)
- **Evaluation**: Replace image-only probabilities in the union results
  and recompute F1/P/R at all thresholds. Compare to baseline.

### What we learn

- Whether provenance information improves the verifier's discrimination
  on perceptually ambiguous candidates
- Whether the text track's absence is a strong enough signal to shift
  confidently-wrong FPs (the 9 at p=1.0)
- If positive: the architecture could be extended to a provenance-aware
  verifier for all candidate categories

### Implementation notes

- Adapt from `reverify_image_only_high_thinking.py` — same structure,
  different prompt modification
- Prompt modification is a content preamble (prepended text part), not
  a change to the system instruction, to keep the adversarial framing
  intact
- Reuse the same evaluation code from `run_union_experiment.py`

---

## Experiment B: Visual Reference Examples for Image-Only Candidates

**Priority**: 2
**Estimated cost**: ~$0.50 (44 API calls)
**Status**: COMPLETE (2026-03-10, Session 46)
**Result**: Paradoxical — best image-only P improvement (+0.073) but
*worst* overall F1 (ΔF1=−0.004). Gained 2 TPs but greedy matching
non-additivity caused net negative at whole-pool level. Visual examples
liberalised acceptance on ambiguous candidates.
**Cost**: ~$0.13 (44 API calls, 0 failures)
**Results**: `results/phase3d-verifier-experiments-abc.md`

### Rationale

The union experiment used `include_examples=False` (text-only reference
labels) for all candidates. But the Phase 3d pilot used
`include_examples=True` (visual reference images) for the image track
verifier and achieved F1=0.711. We have not tested whether showing the
verifier *visual* examples of genuine mound symbols (and confusable
features) specifically helps it discriminate on the perceptually
challenging image-only crops.

The hypothesis is that visual comparison might help the model recognise
subtle differences between genuine mound symbols and confusable features
that text descriptions alone cannot convey. This is especially relevant
for the image-only FPs, which are perceptually convincing in isolation.

### Design

- **Scope**: Re-verify the 44 image-only union candidates
- **Modification**: Set `include_examples=True` in the verifier call
- **Verifier**: Adversarial (`verify_adversarial.md`)
- **Config**: T=0.0, thinking=minimal, include_examples=True
- **Reference examples**: The 6 examples already defined in
  `VERIFIER_EXAMPLES` (4 positive, 2 negative) from
  `inputs/examples/neutral-naming/`
- **Evaluation**: Same as Experiment A — replace probabilities, recompute

### What we learn

- Whether visual examples improve perceptual discrimination on the
  specific crops that fool the text-only verifier
- Whether the include_examples=True setting that worked in the pilot
  (image track) transfers to the union context
- Direction of effect: do examples help reject FPs, or do they provide
  the model with more ways to rationalise acceptance?

### Implementation notes

- Trivial modification: flip `INCLUDE_EXAMPLES = True` in the re-verify
  script
- May want to run as a separate script to keep results cleanly separated
- The 6 example images add ~150 KB per API call; cost increase is
  minimal at 44 calls

---

## Experiment C: Temperature Variation with Majority Vote

**Priority**: 3
**Estimated cost**: ~$1.50 (3 × 44 = 132 API calls)
**Status**: COMPLETE (2026-03-10, Session 46)
**Result**: Negative at both T=0.5 (ΔF1=+0.004) and T=1.0 (ΔF1=0.000).
Higher temperature increased per-pass variance but means converged to
baseline. Confirms errors are systematic perceptual misclassifications,
not sampling noise. Temperature variation is the weakest diversity lever.
**Cost**: ~$0.80 (264 API calls total: 132 at T=0.5 + 132 at T=1.0)
**Results**: `results/phase3d-verifier-experiments-abc.md`
**Note**: T=0.5 output was overwritten by T=1.0 run; T=0.5 results
documented from session output only.

### Rationale

All verifier experiments have used T=0.0 (deterministic, greedy
decoding). This gives a single probability per candidate with no
uncertainty estimate. At T>0, the model samples from its output
distribution, which means repeated calls may produce different
probabilities. The pattern of variation is informative:

- If a candidate's probability is *stable* across samples (e.g.,
  always 0.95 or always 0.05), the model is genuinely confident
- If it *varies widely* (e.g., 0.2, 0.8, 0.95), the T=0 answer is
  an arbitrary pick from an uncertain distribution

For the 9 image-only FPs that score p=1.0 at T=0, temperature variation
tests whether these are genuinely confident or artificially decisive.
If they become unstable at T>0, averaging could shift them below
threshold.

### Design

- **Scope**: Re-verify the 44 image-only union candidates, 3 times each
- **Modification**: T=0.5 (moderate sampling temperature)
- **Verifier**: Adversarial (`verify_adversarial.md`)
- **Config**: T=0.5, thinking=minimal, include_examples=False
- **Aggregation**: For each candidate, compute mean, median, min, max,
  and standard deviation across the 3 samples
- **Evaluation**: Use mean probability as the aggregated score; compare
  threshold sweep to T=0 baseline

### What we learn

- Whether the T=0 verifier's confident FP scores (p=1.0) are stable
  or collapse under stochastic sampling
- Whether averaging reduces the bimodal distribution and creates a
  more graded probability landscape
- Whether any TP/FP separation emerges from variance (high-variance
  candidates might be systematically different from low-variance ones)

### Implementation notes

- Could run all 3 passes sequentially (simpler) or investigate whether
  the API supports batch/concurrent calls
- Need to store all 3 probability vectors, not just the aggregate
- Consider whether K=5 samples would be more informative than K=3 (cost
  ~$2.50 vs ~$1.50). K=3 is likely sufficient to detect instability
- Temperature choice: T=0.5 is moderate. T=1.0 might be too noisy;
  T=0.3 might not produce enough variation. Can always re-run at a
  different T if results are inconclusive

---

## Experiment D: Cascaded Verification

**Priority**: 4
**Estimated cost**: ~$0.50 (≤22 API calls for second stage)
**Status**: PLANNED

### Rationale

The current verifier runs a single pass with a single prompt. A cascaded
approach runs two verifiers in series: the first (existing adversarial)
filters the candidate pool, and the second applies a *different*
verification strategy only to candidates that passed the first stage.

At t=0.11, 22 of the 44 image-only candidates pass the adversarial
verifier (7 TP, 15 FP). A second-stage verifier targeting only these 22
candidates could use a fundamentally different prompt — for instance,
explicit comparison against reference examples rather than adversarial
reasoning.

### Design

- **Scope**: The ~22 image-only candidates that pass the first-stage
  adversarial verifier at t=0.11
- **First stage**: Existing adversarial verifier results (already
  computed) — no new API calls
- **Second stage**: A new verifier prompt focused on *comparative*
  classification:
  - Show 3–4 reference crops of genuine mound symbols alongside the
    candidate crop
  - Ask: *"Compare the candidate to these confirmed mound symbols.
    Does the candidate share the same diagnostic features (outward rays,
    central shape, colour)? Or does it resemble these symbols only
    superficially?"*
  - The comparative framing forces feature-by-feature visual comparison
    rather than isolated judgement
- **Config**: T=0.0, thinking=minimal, include_examples=True
  (the reference images ARE the examples here)
- **Evaluation**: Combine first-stage and second-stage probabilities
  (e.g., product, or use second-stage as a gate)

### What we learn

- Whether a comparative framing (candidate vs. known positives)
  improves discrimination where adversarial reasoning alone fails
- Whether two structurally different verification strategies in series
  produce better precision than either alone
- The failure mode: does the comparative verifier agree with the
  adversarial one (redundant), or does it disagree on specific FP types?

### Implementation notes

- Requires drafting a new verifier prompt (`verify_comparative.md`)
- Input: candidate crop + 3–4 reference crops in the same API call
- The second stage only runs on ~22 candidates, making it cheap
- Combining scores: simplest approach is to multiply probabilities
  (both must be high), but could also use the second stage as a binary
  gate (p > 0.5 required)
- Should select reference crops carefully — use crops of known TPs from
  the validation set that show clear, unambiguous mound symbols

---

## Experiment E: High-Recall Text Proposer

**Priority**: 5
**Estimated cost**: ~$3.50 via Batch API (50% discount; ~$7 synchronous)
**Status**: PLANNED

### Rationale

This targets the *proposer* side of the pipeline rather than the
verifier. The text-only single-track achieves F1=0.796 with recall
0.784. If a recall-biased text proposer could push recall to ~0.85
(matching the union's 0.835) while maintaining text-track-level
precision through adversarial verification, the result could be
F1 > 0.8 without needing cross-modal fusion at all.

The text track's proposer (Phase 2d, brief-text-image, T=0.0) was
optimised for balanced detection, not maximum recall. A recall-biased
variant would use different prompting and generation parameters to
flag anything plausible, accepting lower proposer precision in exchange
for higher recall — relying on the verifier to clean up the additional
FPs.

### Design

- **Scope**: Full validation tile set (60 tiles), single proposer pass
- **Proposer modifications** (all targeting higher recall):
  - Temperature: T=0.7 (vs T=0.0 baseline) for broader sampling
  - Thinking: HIGH (vs minimal) for more thorough map examination
  - Prompt: Recall-biased framing — *"Flag any feature that could
    plausibly be a burial mound, even if uncertain. It is better to
    include a doubtful candidate than to miss a real one."*
  - Negative examples: Removed or reduced (they may anchor the model
    toward rejection)
  - Positive examples: Retained (anchor toward detection)
- **Verifier**: Adversarial (`verify_adversarial.md`), T=0.0,
  thinking=minimal, include_examples=False (the proven best config)
- **Evaluation**: Standard greedy matching, threshold sweep, compared
  to text-only baseline and union results

### What we learn

- The recall ceiling for a single text-track pass with recall-biased
  parameters
- Whether the verifier can maintain precision on a larger, noisier
  candidate pool generated by the recall-biased proposer
- Whether this approach can match or exceed the union's recall (0.835)
  without needing the image track at all
- The precision-recall trade-off shape for the text track as proposer
  aggressiveness varies

### Implementation notes

- **Use the Batch API** via `4_detect_mounds_batch.py` +
  `lib_batch_api.py` for the proposer pass — 50% cost reduction,
  proven infrastructure from Phase 2 runs
- Needs a new proposer prompt/config (recall-biased version of
  brief-text-image). Draft in `prompts/configs/`
- The batch module already supports all required parameters:
  `temperature` (T=0.7), `thinking_level` ("HIGH"), and
  `include_example_images` (False for text-only)
- Create a study YAML entry or run directly with the batch script
  using `--config` pointing to the new prompt config
- After the proposer batch completes, pipe output through
  `extract_candidates.py` → adversarial verifier (synchronous,
  ~$1 for ~100 candidates) → evaluation
- If recall doesn't improve meaningfully, consider multi-pass union
  (K=3–5 proposer passes, union all detections) at ~$10–18 via batch

---

## Deferred: Wider Crop Context

**Status**: DEFERRED
**Estimated cost**: ~$1–2 (re-extraction + re-verification)

Crops currently use 75px padding (150×150 px). Widening to 150px
(300×300 px) would give the verifier more surrounding context to
identify contour patterns, boundary lines, or other features that
explain away "mound-like" appearances at the current scale. Deferred
because it requires re-extracting all crops (more engineering work)
and the other experiments are faster to execute and evaluate first.
If Experiments A–D all fail to improve precision on image-only
candidates, wider context becomes the next logical step.

---

## Experiment Order and Dependencies

```text
A (provenance-informed)  ─┐
B (visual examples)      ─┤── Independent, can run in any order
C (temperature variation) ─┘
         │
         ▼
D (cascaded verification) ── May benefit from A/B/C findings
                              to inform second-stage prompt design
         │
         ▼
E (high-recall proposer)  ── Independent of A–D; different lever
                              (proposer vs verifier)
```

Experiments A, B, and C are independent and could potentially run in
the same session. Each produces a set of 44 probabilities that can be
evaluated against the same baseline. Experiment D benefits from knowing
which approaches (if any) shifted the image-only FPs, informing the
design of the second-stage prompt. Experiment E is fully independent
and targets a different part of the pipeline.

## Success Criteria

Any experiment that pushes the union pipeline's F1 above **0.796**
(the current text-only single-track benchmark) would represent a
genuine improvement. The stretch target is F1 > **0.80**.

For Experiment E specifically, the target is text-only recall > **0.835**
(matching the union) with precision maintained above **0.78** (for
F1 > 0.80).
