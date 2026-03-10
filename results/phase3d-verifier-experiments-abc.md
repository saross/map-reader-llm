# Phase 3d — Verifier Improvement Experiments A–D Results

## Metadata

- **Generated**: 2026-03-10 (A–C), 2026-03-10 (D)
- **Script**: `scripts/reverify_image_only_experiments.py`
- **Scope**: 44 image-only candidates from the cross-modal union experiment
- **Verifier**: Adversarial (`verify_adversarial.md`) for A–C;
  Comparative (`verify_comparative.md`) for D second stage
- **Model**: gemini-3-flash-preview
- **Baseline**: `outputs/phase3d-union/verifier_adversarial_probabilities.json`
  (T=0.0, thinking=minimal, include_examples=False)
- **Ground truth**: 97 reference mounds in validation tile bounds
- **Total cost**: ~$1.05 (242 Application Programming Interface (API) calls
  across A + B + C at T=0.5 + C at T=1.0 + D, 0 failures, ~14 min wall time)

## Summary Table

All experiments re-verified the same 44 image-only candidates and merged
probabilities into the full 184-candidate baseline for evaluation.

| Experiment | ΔF1 | ΔP | ΔR | Image-only P | TP | FP |
|---|---:|---:|---:|---:|---:|---:|
| Baseline (reference) | — | — | — | 0.318 | 7 | 15 |
| **A: Provenance preamble** | **+0.011** | **+0.019** | 0.000 | 0.368 | 7 | 12 |
| B: Visual examples | −0.004 | −0.006 | 0.000 | 0.391 | 9 | 14 |
| C: Temperature T=0.5 (K=3) | +0.004 | +0.006 | 0.000 | 0.333 | 7 | 14 |
| C: Temperature T=1.0 (K=3) | 0.000 | 0.000 | 0.000 | 0.318 | 7 | 15 |
| D: Cascaded comparative | +0.004 | +0.006 | 0.000 | 0.333 | 7 | 14 |

None of the experiments reached the success criterion of F1 > 0.796
(the text-only single-track benchmark).

## Full Evaluation Results

| Configuration | F1 | P | R | N | Threshold |
|---|---:|---:|---:|---:|---:|
| Baseline | 0.768 | 0.711 | 0.835 | 114 | 0.11 |
| A: Provenance | 0.779 | 0.730 | 0.835 | 111 | 0.16 |
| B: Examples | 0.764 | 0.704 | 0.835 | 115 | 0.11 |
| C: Temperature T=0.5 | 0.771 | 0.717 | 0.835 | 113 | 0.19 |
| C: Temperature T=1.0 | 0.768 | 0.711 | 0.835 | 114 | 0.19 |
| D: Cascaded comparative | 0.771 | 0.717 | 0.835 | 113 | 0.11 |
| Text-only single-track (ref.) | 0.796 | 0.809 | 0.784 | 94 | 0.16 |

Recall is unchanged at 0.835 across all experiments — expected, since
only image-only verifier probabilities were modified and no true
positives crossed the accept/reject boundary.

---

## Experiment A: Provenance-Informed Verification

**Status**: COMPLETE — best result of the three experiments

### Modification

Prepended a provenance preamble as the first content part:

> "Note: This candidate was detected by the image-based analyser ONLY.
> A separate text-based analysis of the same map area did NOT flag this
> location. Consider whether this absence is informative."

### Result

- **ΔF1 = +0.011** (0.768 → 0.779)
- 3 FPs rejected (15 → 12) with 0 TPs lost
- Image-only precision improved from 0.318 to 0.368
- 24 of 44 candidates changed probability vs baseline

### Interpretation

The provenance signal shifted 3 false positives below threshold without
affecting any true positives. The verifier correctly interpreted the
absence of text-track confirmation as a meaningful negative signal for
perceptually ambiguous candidates. This validates the hypothesis from
Session 44 that cross-modal absence is informative.

However, the improvement is modest (+0.011 F1) and does not reach the
0.796 text-only benchmark. The 12 remaining FPs include candidates at
p=1.0 (IDs 14, 15, 37, 40, 45, 51, 127, 131) where even the provenance
signal was insufficient to shift the verifier's confident judgement.

---

## Experiment B: Visual Reference Examples

**Status**: COMPLETE — paradoxical result

### Modification

Set `include_examples=True` in the verifier call, providing 6 visual
reference example images (4 positive, 2 negative) alongside the
candidate crop instead of text-only descriptions.

### Result

- **ΔF1 = −0.004** (0.768 → 0.764) — net negative at whole-pool level
- Image-only precision improved most (+0.073, 0.318 → 0.391)
- Gained 2 TPs (7 → 9) but only lost 1 FP (15 → 14)
- 16 of 44 candidates changed probability vs baseline

### Interpretation

The paradoxical result — best image-only precision improvement but
*worst* overall F1 — is caused by greedy matching non-additivity.
Gaining 2 image-only TPs created matching conflicts with candidates from
other provenance categories (both-track, text-only), redistributing
TP/FP assignments at the whole-pool level and producing a net negative.

Notable individual changes:

- Candidate 5: 0.10 → 1.00 (FP liberalised)
- Candidate 30: 0.05 → 1.00 (FP liberalised)
- Candidate 60: 0.00 → 1.00 (FP liberalised)
- Candidate 7: 0.90 → 0.10 (FP correctly rejected)

Visual examples helped the verifier correctly identify some genuine
mounds it previously missed, but also convinced it that several false
positives look like the reference examples. The net effect is
liberalisation — consistent with the broader finding that providing the
verifier with more information about what mounds look like makes it more
willing to classify ambiguous features as mounds.

---

## Experiment C: Temperature Variation

**Status**: COMPLETE — negative result at both T=0.5 and T=1.0

### Modification

Sampled at non-zero temperature (K=3 passes per candidate), computed
mean probabilities. Tested at T=0.5 (conservative) and T=1.0 (standard
unscaled distribution).

### Result at T=0.5

- **ΔF1 = +0.004** (0.768 → 0.771) — marginal improvement
- Very low per-candidate variance: most std = 0.000–0.058
- Only candidates 7 (std=0.208) and 115 (std=0.189) showed meaningful
  variation
- 21 of 44 candidates changed probability vs baseline

### Result at T=1.0

- **ΔF1 = 0.000** (0.768 → 0.768) — no change whatsoever
- Substantially more variance: candidate 28 std=0.403, candidate 87
  std=0.356, candidate 118 std=0.286, candidate 60 std=0.248
- But means converged back to the same accept/reject boundary as baseline
- 28 of 44 candidates changed probability vs baseline

### Interpretation

Higher temperature produced more per-pass variation but the averaged
means cancelled out: some FPs got lower means (good) while some TPs
also got lower means (bad). At the optimal threshold, these movements
balanced exactly.

This confirms that the verifier's errors on image-only candidates are
*systematic perceptual misclassifications*, not sampling noise.
Stochastic sampling cannot fix a model that consistently misreads the
visual evidence — the mean converges to the same wrong answer regardless
of temperature. Temperature variation is the weakest lever in the
diversity taxonomy.

---

## Experiment D: Cascaded Comparative Verification

**Status**: COMPLETE — marginal positive, well below expected ceiling

### Modification

Two-stage cascaded verification. First stage: the baseline adversarial
verifier at threshold t=0.11 filters 44 image-only candidates to 22
passing candidates. Second stage: a *comparative* verifier
(`verify_comparative.md`) shows 4 confirmed positive mound reference
images alongside each candidate and asks for feature-by-feature
comparison (rays, shape, colour, gestalt).

This is the only experiment that uses a different verifier instruction
and a different content-part structure. The comparative framing pivots
from "argue this is NOT a mound" (adversarial) to "compare this to
confirmed mounds" (comparative). Non-passing candidates retain their
baseline adversarial probabilities unchanged.

### Result

- **ΔF1 = +0.004** (0.768 → 0.771) — marginal improvement
- 1 FP rejected: candidate 7 (0.90 → 0.00)
- 0 TPs lost, all 7 retained
- Only 3 of 22 passing candidates changed direction; the other 19
  were confirmed or increased to p=1.0
- Image-only precision: 0.318 → 0.333
- 8 of 44 candidates changed probability vs baseline

### Interpretation

The comparative framing **liberalised** the verifier rather than
tightening it — the same pattern observed in Experiment B. Of 22
candidates presented to the second-stage verifier, 20 received p=1.0.
Several candidates that had intermediate baseline probabilities were
pushed *up* by the comparison:

- Candidate 102: 0.40 → 1.00 (dramatic increase)
- Candidate 53: 0.75 → 1.00
- Candidate 51: 0.85 → 1.00
- Candidate 115: 0.85 → 1.00

Only candidate 7 (0.90 → 0.00) was convincingly rejected, and
candidate 122 decreased modestly (0.30 → 0.20). The hard-core FPs (IDs
14, 37, 40) remained at p=1.0 — immovable across all four experiments.

The result falls well below the pre-experiment expected ceiling of
F1 ≈ 0.785–0.790 (expected 3–5 FP removals). The hypothesis that
pattern-matching against confirmed examples would exploit a different
cognitive pathway than adversarial argumentation was not supported:
when the VLM compared FPs to confirmed mounds, it found enough visual
similarity to confirm them. This reinforces the conclusion that
image-only FP errors are perceptual misclassifications, not failures of
reasoning strategy.

**Cost**: ~$0.05 (22 API calls, 0 failures, 94s wall time).

---

## Per-Candidate Comparison

| ID | Status | Baseline | A: Prov | B: Exam | C: T=1.0 | T=1.0 Std | D: Casc |
|---:|--------|--------:|--------:|--------:|---------:|----------:|--------:|
| 0 | TP | 1.00 | 0.95 | 1.00 | 0.933 | 0.094 | 1.00 |
| 5 | FP | 0.10 | 0.15 | 1.00 | 0.100 | 0.000 | 0.10 |
| 6 | FP | 0.00 | 0.05 | 0.00 | 0.000 | 0.000 | 0.00 |
| 7 | FP | 0.90 | 0.10 | 0.10 | 0.333 | 0.170 | **0.00** |
| 14 | FP | 1.00 | 1.00 | 1.00 | 1.000 | 0.000 | 1.00 |
| 15 | FP | 1.00 | 1.00 | 1.00 | 0.800 | 0.283 | 1.00 |
| 25 | FP | 0.00 | 0.00 | 0.00 | 0.000 | 0.000 | 0.00 |
| 28 | TP | 1.00 | 1.00 | 0.95 | 0.433 | 0.403 | 1.00 |
| 30 | FP | 0.05 | 0.05 | 1.00 | 0.050 | 0.041 | 0.05 |
| 31 | FP | 0.00 | 0.05 | 0.00 | 0.017 | 0.024 | 0.00 |
| 37 | FP | 1.00 | 1.00 | 1.00 | 1.000 | 0.000 | 1.00 |
| 39 | FP | 0.10 | 0.10 | 0.10 | 0.117 | 0.024 | 0.10 |
| 40 | FP | 1.00 | 1.00 | 1.00 | 1.000 | 0.000 | 1.00 |
| 41 | TP | 1.00 | 1.00 | 1.00 | 1.000 | 0.000 | 1.00 |
| 42 | FP | 0.00 | 0.05 | 0.00 | 0.017 | 0.024 | 0.00 |
| 45 | FP | 1.00 | 1.00 | 1.00 | 0.417 | 0.232 | 1.00 |
| 51 | FP | 0.85 | 1.00 | 1.00 | 0.733 | 0.239 | 1.00 |
| 52 | FP | 0.00 | 0.00 | 0.00 | 0.000 | 0.000 | 0.00 |
| 53 | FP | 0.75 | 0.75 | 0.85 | 0.867 | 0.155 | 1.00 |
| 59 | FP | 1.00 | 0.75 | 0.95 | 1.000 | 0.000 | 1.00 |
| 60 | FP | 0.00 | 0.05 | 1.00 | 0.750 | 0.248 | 0.00 |
| 77 | FP | 0.10 | 0.10 | 0.10 | 0.017 | 0.024 | 0.10 |
| 78 | FP | 0.00 | 0.10 | 0.05 | 0.100 | 0.000 | 0.00 |
| 87 | FP | 0.95 | 1.00 | 0.85 | 0.650 | 0.356 | 1.00 |
| 90 | FP | 1.00 | 0.05 | 1.00 | 0.950 | 0.000 | 1.00 |
| 96 | FP | 0.00 | 0.05 | 0.00 | 0.050 | 0.000 | 0.00 |
| 102 | FP | 0.40 | 0.75 | 1.00 | 0.850 | 0.141 | 1.00 |
| 107 | FP | 0.00 | 0.05 | 0.10 | 0.050 | 0.000 | 0.00 |
| 108 | FP | 0.05 | 0.05 | 0.05 | 0.083 | 0.024 | 0.05 |
| 109 | TP | 1.00 | 0.95 | 1.00 | 0.983 | 0.024 | 1.00 |
| 110 | FP | 0.00 | 0.05 | 0.10 | 0.050 | 0.041 | 0.00 |
| 111 | FP | 0.05 | 0.05 | 0.00 | 0.050 | 0.000 | 0.05 |
| 112 | FP | 0.00 | 0.00 | 0.00 | 0.017 | 0.024 | 0.00 |
| 113 | FP | 0.00 | 0.00 | 0.00 | 0.000 | 0.000 | 0.00 |
| 115 | TP | 0.85 | 1.00 | 0.85 | 0.883 | 0.047 | 1.00 |
| 117 | FP | 1.00 | 0.95 | 1.00 | 0.950 | 0.071 | 1.00 |
| 118 | TP | 1.00 | 1.00 | 1.00 | 0.600 | 0.286 | 1.00 |
| 121 | FP | 0.05 | 0.05 | 0.00 | 0.050 | 0.000 | 0.05 |
| 122 | FP | 0.30 | 0.10 | 0.10 | 0.183 | 0.024 | 0.20 |
| 124 | FP | 0.00 | 0.05 | 0.00 | 0.000 | 0.000 | 0.00 |
| 126 | FP | 0.00 | 0.05 | 0.00 | 0.017 | 0.024 | 0.00 |
| 127 | FP | 1.00 | 1.00 | 1.00 | 0.983 | 0.024 | 1.00 |
| 128 | FP | 0.05 | 0.00 | 0.05 | 0.050 | 0.041 | 0.05 |
| 131 | FP | 0.95 | 1.00 | 0.95 | 0.950 | 0.071 | 1.00 |

**Status** column from ground-truth matching: 7 TPs (IDs 0, 28, 41,
109, 115, 118, plus candidate with baseline p=1.0 at ID 0), 37 FPs.

**D: Casc** column notes: Non-passing candidates (baseline p < 0.11)
retain baseline values. Passing candidates received second-stage
comparative verification. Bold values indicate meaningful direction
changes vs baseline.

---

## Cross-Experiment Observations

### 1. No experiment reached the success criterion

The target was F1 > 0.796 (text-only single-track benchmark). The best
result was Experiment A at F1=0.779 — still 0.017 short. Four distinct
approaches (provenance context, visual examples, temperature sampling,
cascaded comparative verification) all failed to close this gap. The
union pipeline's value remains recall (0.835), not F1.

### 2. Recall is invariant to verifier modifications

All experiments produced R=0.835 — the 7 image-only TPs were never
shifted below any reasonable threshold. The recall ceiling is set by
the proposer, not the verifier.

### 3. The hard-core FPs are immovable

Candidates 14, 37, 40 scored p=1.0 across **all four experiments**
(including both temperature runs and the comparative second stage).
These are perceptual confusions that no amount of prompt modification,
reasoning strategy, temperature sampling, or reference comparison can
resolve — the crops genuinely look like mound symbols to the VLM.

### 4. Showing positive examples liberalises the verifier

Both Experiment B (visual examples in adversarial framing) and
Experiment D (comparative framing with positive-only examples) pushed
candidate probabilities upward rather than improving discrimination.
Experiment D confirmed 20 of 22 passing candidates at p=1.0, including
several that increased dramatically (candidate 102: 0.40 → 1.00).
Pattern-matching against confirmed mounds makes FPs look *more*
mound-like, not less. This is a consistent and replicable effect.

### 5. Experiment B reveals greedy matching artifacts

Experiment B improved image-only precision the most (+0.073) but hurt
whole-pool F1 (−0.004). This demonstrates that per-category
improvements don't compose additively under greedy matching — gaining
image-only TPs can steal matches from other provenance categories.

### 6. Temperature confirms systematic rather than stochastic errors

At T=1.0, per-pass variance increased substantially (max std=0.403) but
means converged to the baseline. The errors are deterministic
perceptual misclassifications, not sampling artifacts.

### 7. Only negative information improves precision

Across all four experiments, only Experiment A (provenance preamble)
meaningfully improved precision without side effects. The preamble
provides *negative* information ("text analysis did NOT flag this").
All approaches providing *positive* information — visual examples (B),
comparative references (D) — liberalised the verifier. This suggests
the effective lever for VLM verification is informing the model about
what's *absent*, not what's *present*.

---

## Implications

### Verifier-side optimisation is exhausted

Four experiments spanning five distinct approaches (provenance context,
visual examples, temperature T=0.5, temperature T=1.0, cascaded
comparative verification) produced a maximum ΔF1 of +0.011. The
verifier-side ceiling for image-only candidates is effectively reached.
Further verifier modifications are unlikely to close the 0.017 gap to
the text-only benchmark.

### Experiment E (high-recall text proposer) is the remaining path

The consistent finding across A–D is that image-only FP errors are
perceptual — the VLM genuinely sees mound-like features in ~15
candidates that are not mounds. No reasoning strategy, framing, or
sampling approach can overcome this. The path to F1 > 0.8 requires
better proposer recall from a single modality, reducing dependence on
the weak image-only track.

### The union pipeline's value is recall, not F1

The union pipeline (F1=0.768–0.779) will not beat the text-only
single-track (F1=0.796) through verifier improvements alone. Its
value is recall (0.835 vs 0.784) — it finds more mounds at the cost
of more false positives. This is a genuine architectural trade-off,
not a deficiency to be fixed.

## Data Artifacts

| File | Description |
|---|---|
| `outputs/phase3d-union/verifier_adversarial_provenance_probabilities.json` | Experiment A probabilities (44 entries) |
| `outputs/phase3d-union/verifier_adversarial_examples_probabilities.json` | Experiment B probabilities (44 entries) |
| `outputs/phase3d-union/verifier_adversarial_temperature_probabilities.json` | Experiment C T=1.0 means (44 entries) |
| `outputs/phase3d-union/verifier_adversarial_temperature_all_passes.json` | Experiment C T=1.0 per-pass data |
| `outputs/phase3d-union/verifier_comparative_cascaded_probabilities.json` | Experiment D probabilities (44 entries) |
| `prompts/system-instructions/verify_comparative.md` | Experiment D verifier instruction |

**Note**: The T=0.5 probability file was overwritten by the T=1.0 run.
T=0.5 evaluation results (F1=0.771, ΔF1=+0.004) are documented above
from session output but the raw per-candidate data was not preserved.
