# Cost-Performance Tradeoffs: Consensus Depth vs. Model Capacity

*Section draft for methods/results*

---

## Overview

Preliminary experiments revealed a substitutability relationship between model capacity and consensus voting depth: smaller models with deeper consensus pools can match the performance of larger models with shallow voting, often at lower cost. This section documents the observed tradeoffs and their implications for practical deployment.

---

## Observed Tradeoffs

Development used Gemini 3 Flash (cost-optimized) with validation on Gemini 3 Pro (capacity-optimized). Single-run performance differences were consistent:

| Model | Single-pass F1 | Relative cost per call |
|-------|---------------|------------------------|
| Gemini 3 Flash | baseline | 1× |
| Gemini 3 Pro | baseline + 0.05–0.10 | ~10–20× |

However, consensus voting depth modulated this relationship:

| Configuration | Total relative cost | Approximate F1 |
|--------------|---------------------|----------------|
| Flash 1-of-1 | 1× | baseline |
| Pro 1-of-1 | 10–20× | baseline + 0.05–0.10 |
| Flash 5-of-5 (3/5 threshold) | 5× | baseline + ~0.08 |
| Flash 10-of-30 (majority) | 30× | ≈ Pro 2-of-5 |
| Pro 2-of-5 (majority) | 50–100× | near-peak |

**Key finding**: Flash with 10-of-30 voting achieved comparable F1 to Pro with 2-of-5 voting, at roughly one-third to one-half the cost.

---

## Interpretation

### Consensus depth and model capacity are partially substitutable

Both larger models and deeper consensus pools appear to address the same underlying source of error: stochastic variation in VLM outputs. A larger model produces more reliable single-pass predictions; deeper voting averages out unreliable predictions from a smaller model. The mechanisms differ, but the effect on F1 is similar.

This suggests a **cost-performance frontier** where practitioners can choose their position based on constraints:

- **Latency-constrained**: Prefer Pro with shallow voting (fewer API calls, faster turnaround)
- **Cost-constrained**: Prefer Flash with deep voting (more calls, but cheaper per call)
- **Quality-ceiling**: At some point, deeper voting on Flash may plateau while Pro continues to benefit — this ceiling was not reached in preliminary testing but should be investigated

### Diminishing returns at both ends

- Adding consensus depth shows diminishing returns: the jump from 1-of-1 to 5-of-5 is larger than from 5-of-5 to 10-of-30
- Similarly, Pro's single-pass advantage (~0.05–0.10 F1) doesn't scale linearly with cost

The optimal configuration depends on where you are on the curve and what marginal improvement is worth.

---

## Implications

### For practical deployment

1. **Default recommendation**: For cost-sensitive production use, Flash + moderate voting depth (e.g., 5-of-10 or 10-of-30) may be optimal. Pro is justified when latency matters or when operating near Flash's quality ceiling.

2. **Adaptive strategies**: Consider a tiered approach — run Flash with shallow voting first; escalate uncertain cases (low consensus agreement) to Pro or deeper voting. This concentrates expensive compute on hard cases.

3. **Budget planning**: Total cost = (tiles × voting depth × cost per call). Deep voting on Flash can still be expensive at scale; the substitutability finding helps optimise, not eliminate, costs.

### For the research community

Few VLM papers report cost-performance tradeoffs explicitly. Documenting this relationship contributes practical guidance that pure accuracy comparisons miss.

### For cross-vendor testing

An open question: does this substitutability hold across model families? Specifically:
- Can Claude Haiku + deep voting match Claude Sonnet/Opus + shallow voting?
- Can GPT-4o-mini + deep voting match GPT-5.2 + shallow voting?

If the pattern generalises, it suggests a fundamental property of VLM few-shot performance rather than a Gemini-specific artefact. This would be a notable finding.

---

## Methodological Note

These observations emerged from preliminary (training-phase) experiments with inconsistent tile sets, so exact figures should be treated as indicative rather than confirmatory. The substitutability relationship was consistent across multiple runs, but precise cost-performance curves should be validated on the holdout set with controlled configurations.

Confirmatory testing will include:
- Flash vs. Pro at matched voting depths (isolating model capacity effect)
- Flash at varied voting depths (characterising consensus returns curve)
- Cross-vendor replication (testing generalisability)

---

## Draft Text for Paper

### Methods (brief)

"Development prioritised Gemini 3 Flash for cost efficiency, with periodic validation on Gemini 3 Pro. Preliminary experiments suggested that consensus voting depth and model capacity are partially substitutable: Flash with deep voting (10-of-30) achieved comparable F1 to Pro with shallow voting (2-of-5) at lower total cost. This informed our decision to optimise voting strategies on Flash before cross-model validation."

### Results (if confirmed on holdout)

"We observed a substitutability relationship between model capacity and consensus depth. Gemini 3 Flash with 10-of-30 majority voting achieved F1 = [X], comparable to Gemini 3 Pro with 2-of-5 voting (F1 = [Y]), despite Pro's ~0.05–0.10 advantage in single-pass performance. At current API pricing, the Flash configuration cost approximately [Z]% of the Pro configuration for equivalent performance. This suggests practitioners can trade latency for cost by using smaller models with deeper consensus pools."

### Discussion

"The substitutability of model capacity and consensus depth has practical implications for VLM deployment. When latency is not critical, smaller models with deeper voting may offer a cost-effective alternative to larger models. This finding aligns with the theoretical framing of consensus voting as variance reduction: both larger models and deeper voting reduce prediction variance, through different mechanisms. An open question is whether this relationship holds across model families; our cross-vendor tests provide preliminary evidence that [it does / it is architecture-specific]."

---

*Document created: 2024-12-23*
*To be refined with holdout results*
