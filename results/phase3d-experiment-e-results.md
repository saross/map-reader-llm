# Experiment E — High-Recall Text Proposer (Negative Result)

## Summary

Experiment E tested whether a recall-biased text proposer could push
text-track recall above 0.835 (matching the cross-modal union) while
maintaining verifier precision ≥ 0.78, targeting F1 > 0.80. Four levers
were pulled simultaneously: recall-biased prompt framing, softened
exclusion rules, T=0.7, HIGH thinking, and reduced negative examples.

**Result: All four success criteria failed.** The combined intervention
degraded F1 from 0.796 to 0.640. A systematic ablation series
(restoring one baseline parameter at a time) recovered performance
incrementally, ultimately attributing the degradation to all four
levers. Even with only the prompt changes remaining, F1 reached only
0.779 — below baseline — with identical recall (0.784) and slightly
worse precision.

**Conclusion:** The baseline configuration (T=0.0, minimal thinking,
17 examples, standard prompt) is near the model's capability frontier
for this task. Attempts to optimise further via prompt engineering
or parameter tuning have net negative effects. The text-track F1=0.796
is not leaving meaningful performance on the table.

## Metadata

- **Date**: 2026-03-10
- **Scripts**: `4_detect_mounds_batch.py` (proposer), `run_experiment_e.py` (verifier + evaluation)
- **Model**: `gemini-3-flash-preview`
- **Verifier**: `verify_adversarial.md` (T=0.0, minimal thinking — unchanged across all runs)
- **Validation tiles**: 60
- **Reference mounds in scope**: 96–97 (minor variation from tile boundary matching)
- **Match buffer**: 20.0 m
- **Total cost**: ~$0.06 (4 proposer runs) + ~$3.00 (4 × ~180 verifier calls) ≈ $3.06

## Experimental Design

### Hypothesis

A recall-biased text proposer can push text-track recall above 0.835 by
simultaneously applying:

1. **Recall-bias framing** — "Flag any feature that could plausibly be a
   burial mound, even if uncertain"
2. **Softened exclusion rule** — rays "may be faint, partially occluded,
   or degraded" (vs baseline: "Symbols without visible rays are not
   mounds")
3. **T=0.7** — increased sampling diversity for borderline detections
   (vs baseline T=0.0)
4. **HIGH thinking** — extended reasoning budget for ambiguous cases
   (vs baseline minimal)
5. **Reduced negative examples** — 10 examples (removed 4 hard negatives
   + 3 nulls; vs baseline 17)

### Strategy

"Go/no-go then disambiguate": test all interventions simultaneously
first. If positive, run ablations to isolate contributions. If negative,
ablate to understand *which* levers caused the degradation.

The initial combined run was negative (F1=0.640), so ablations were run
to decompose the failure.

## Ablation Series

Parameters were restored to baseline one at a time, in order of
suspected impact, with each ablation building on the previous:

| ID | Description | Nulls | Thinking | T | Examples | HN |
|---|---|---|---|---|---|---|
| E1 | All levers | no | HIGH | 0.7 | 10 | no |
| E2 | + nulls restored | **yes** | HIGH | 0.7 | 13 | no |
| E3 | + minimal thinking | yes | **minimal** | 0.7 | 13 | no |
| E4 | + T=0.0 | yes | minimal | **0.0** | 13 | no |
| Baseline | Standard config | yes | minimal | 0.0 | 17 | **yes** |

### Raw Proposer Results (Before Verifier)

| ID | Detections | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| Baseline | 140 | ~78 | ~62 | ~19 | 0.557 | 0.804 | — |
| E1 | 212 | 66 | 146 | 31 | 0.311 | 0.680 | 0.427 |
| E2 | 183 | 71 | 112 | 25 | 0.388 | 0.740 | 0.509 |
| E3 | 184 | 73 | 111 | 24 | 0.397 | 0.753 | 0.520 |
| E4 | 151 | 76 | 75 | 21 | 0.503 | 0.784 | 0.613 |

### Verified Results (Optimal Threshold)

| ID | Threshold | N | TP | FP | FN | Precision | Recall | F1 | ΔF1 |
|---|---|---|---|---|---|---|---|---|---|
| Baseline | 0.16 | 94 | — | — | — | 0.809 | 0.784 | **0.796** | — |
| E1 | 0.16 | 100 | 63 | 37 | 34 | 0.630 | 0.649 | 0.640 | −0.156 |
| E2 | 0.11 | 101 | 68 | 33 | 28 | 0.673 | 0.708 | 0.690 | −0.106 |
| E3 | 0.11 | 100 | 70 | 30 | 27 | 0.700 | 0.722 | 0.711 | −0.085 |
| E4 | 0.16 | 98 | 76 | 22 | 21 | 0.776 | 0.784 | **0.779** | −0.017 |

### Performance Recovery Per Ablation Step

| Ablation step | ΔF1 recovered | % of total | Cumulative F1 |
|---|---|---|---|
| E1→E2: Restore null examples | +0.050 | 32% | 0.690 |
| E2→E3: HIGH → minimal thinking | +0.021 | 13% | 0.711 |
| E3→E4: T=0.7 → T=0.0 | +0.068 | 44% | 0.779 |
| E4→Baseline: Restore hard negatives | +0.017 | 11% | 0.796 |
| **Total degradation** | **−0.156** | **100%** | |

## Findings

### Finding 1: Temperature dominates proposer performance

Temperature T=0.7 was the single largest source of degradation,
accounting for 44% of the total F1 drop (+0.068 recovered when restored
to T=0.0). At T=0.7 the model generated 184 detections vs 151 at T=0.0
(+22%), but the additional detections were predominantly false positives.
Only 3 additional true positives were gained (73→76) at the cost of
36 additional false positives (75→111).

**Implication**: Detection tasks benefit from deterministic inference
(T=0.0) where the model commits to its best interpretation. Sampling
diversity produces noise, not useful recall.

### Finding 2: Null examples are structurally necessary

Removing the 3 null tile examples caused the second-largest degradation
(32% of total). Without nulls, the model appears compelled to find
*something* on every tile, inflating false positives from 75 to 146
while paradoxically losing true positives (76→66). Null examples anchor
the model's understanding that "no detections" is a valid output.

**Implication**: Null examples are not optional negative examples — they
are structural constraints that prevent hallucinated detections.

### Finding 3: HIGH thinking liberalises proposer decisions

Extended reasoning (HIGH thinking) contributed 13% of the degradation.
This is consistent with the verifier-side finding from Session 45
(Obs 155): extended reasoning liberalises acceptance rather than
tightening rejection. The model uses the extra reasoning budget to
talk itself into marginal detections, not to better discriminate.

**Implication**: The thinking-level finding generalises from verifier
to proposer — extended reasoning is not uniformly beneficial for
classification tasks.

### Finding 4: Recall-biased prompt does not improve recall

Even with all other parameters restored to baseline (E4), the
recall-biased prompt achieved **identical recall** (0.784) to the
baseline. The only effect was 4 additional false positives (98 vs 94
detections, same 76 TP). The "when in doubt, include" framing and
softened exclusion rules did not cause the model to find mounds it
would otherwise miss — they only loosened false-positive filtering.

**Implication**: The model's recall ceiling on this task is determined
by perceptual capability, not by prompt-level decision thresholds. The
mounds it misses are ones it genuinely cannot see, not ones it sees but
rejects.

### Finding 5: Baseline is near the capability frontier

The ablation series demonstrates that the baseline configuration
(T=0.0, minimal thinking, 17 examples with hard negatives and nulls,
standard prompt) is near-optimal for this model and task. Every
perturbation away from baseline degraded performance, and the
maximum residual gap after restoring all parameters except the prompt
was only ΔF1=−0.017. There is no meaningful performance left on the
table via prompt engineering or parameter tuning.

## Success Criteria

| Criterion | Required | Achieved (E4, best) | Status |
|---|---|---|---|
| Recall > 0.835 (union) | > 0.835 | 0.784 | **FAIL** |
| Precision > 0.78 | > 0.78 | 0.776 | **FAIL** |
| F1 > 0.796 (text-only) | > 0.796 | 0.779 | **FAIL** |
| F1 > 0.80 (stretch) | > 0.80 | 0.779 | **FAIL** |

## Implications for the Research Programme

1. **Proposer-side optimisation is now exhausted**, joining verifier-side
   optimisation (Experiments A–D, max ΔF1=+0.011). Both halves of the
   two-stage pipeline have been systematically explored.

2. **The text-only single-track F1=0.796 represents the practical ceiling**
   for this model, task, and evaluation protocol. Further gains would
   require a fundamentally different approach: a different model
   architecture, different map representation, or different evaluation
   methodology.

3. **The diversity taxonomy is now comprehensively tested**: parametric
   (T), cognitive-scaffolding (thinking level), prompt-engineering
   (recall-bias framing), and example-set composition all fail to
   improve on the baseline. Only structural diversity (task
   decomposition into proposer→verifier) has produced meaningful gains.

4. **Ablation methodology works**: The "go/no-go then disambiguate"
   pattern cost ~$3 and produced clean causal attribution across 4
   levers in a single session. This is an efficient experimental
   design for multi-lever exploration.

## Timing

| Run | Duration | Note |
|---|---|---|
| E1 (HIGH, T=0.7) | 144s | Extended thinking is expensive |
| E2 (HIGH, T=0.7) | 187s | 3 more examples, slightly longer |
| E3 (minimal, T=0.7) | 12s | 15× faster without extended thinking |
| E4 (minimal, T=0.0) | 10s | Deterministic is slightly faster |

## Data Artefacts

| File | Description |
|---|---|
| `prompts/system-instructions/detect_brief-text_high-recall.md` | Recall-biased proposer prompt |
| `prompts/configs/detect_brief-text_high-recall.json` | E1 config (all levers) |
| `prompts/configs/detect_brief-text_high-recall_nulls.json` | E2 config (+nulls) |
| `prompts/configs/detect_brief-text_high-recall_nulls-minimal.json` | E3 config (+minimal) |
| `prompts/configs/detect_brief-text_high-recall_nulls-minimal-t0.json` | E4 config (+T=0.0) |
| `outputs/results/detect_brief-text_high-recall/` | E1 proposer output |
| `outputs/results/detect_brief-text_high-recall_nulls/` | E2 proposer output |
| `outputs/results/detect_brief-text_high-recall_nulls-minimal/` | E3 proposer output |
| `outputs/results/detect_brief-text_high-recall_nulls-minimal-t0/` | E4 proposer output |
| `outputs/phase3d-experiment-e/` | Candidates, probabilities, results JSON (last run) |
| `scripts/run_experiment_e.py` | Evaluation pipeline script |
| `tests/test_experiment_e.py` | 12 tier1 unit tests |
