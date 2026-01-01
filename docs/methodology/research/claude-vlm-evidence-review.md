# Evidence Review: VLM Prompting Strategy Claims vs. Empirical Findings

**Document created**: 2024-12-22  
**Purpose**: Summary of investigation into the evidence base for common VLM prompting recommendations, prompted by unexpected experimental results on Gemini 3.

---

## Context

A research synthesis document recommended several "best practices" for VLM-based detection tasks:
1. Minimize text in prompts to avoid text-image interference
2. Use two-stage proposer-verifier pipelines to optimise precision-recall
3. Consensus voting to reduce errors

When implementing these on **Gemini 3 Flash and Pro** for cartographic symbol detection (burial mounds on Soviet topographic maps):
- (1) Text minimization had **little effect**
- (2) Two-stage pipelines were **actively harmful** (degraded performance)
- (3) Consensus voting **worked well** (this one held up)

This document traces the actual evidence behind claims (1) and (2).

---

## Claim 1: Text-Image Interference

### What the synthesis claimed

> "State-of-the-art VLMs achieve only **17% accuracy** on visual tasks when images conflict with textual priors, and 'thinking' models like o3 show *worse* degradation (-6.56%) when text cues are present."

> "The solution is counterintuitive: **use less text, not better text**."

### Actual source

**Paper**: "Vision Language Models are Biased" (Vo et al., May 2025)  
**arXiv**: 2505.23941  
**URL**: https://arxiv.org/abs/2505.23941

### Models actually tested

- Gemini-2.5 Pro
- Claude 3.7 Sonnet (Sonnet-3.7)
- GPT-4.1
- o3
- o4-mini

**Note**: This is Gemini **2.5**, not Gemini 3. The research predates current frontier models.

### What the research actually shows

The 17% accuracy figure refers to a very specific phenomenon:

1. **Task**: Counting visual elements in **counterfactual images** - images that have been modified to contradict common knowledge
   - Adidas logos with 4 stripes instead of 3
   - Dogs with 5 legs instead of 4
   - Flags with altered star counts

2. **Finding**: VLMs achieve 100% accuracy on *unmodified* images but only 17% on counterfactual images. They default to memorized knowledge rather than actually analyzing the visual content.

3. **Text interference finding**: Adding **in-image text** (e.g., the word "Adidas" overlaid on a logo) caused accuracy to drop by -4.49 points. This is about text *in the image*, not text in the prompt.

4. **Prompt-based mitigations had minimal effect**:
   - "Rely exclusively on image details" (Debiased prompt): **+1.87** improvement
   - "Double-check your answer" prompt: **+2.70** improvement
   
   The paper itself concludes that helpful prompting strategies "only slightly improve accuracy."

### Why this doesn't apply to cartographic symbol detection

The text-image interference phenomenon requires:
- **Strong prior knowledge** that conflicts with visual evidence
- VLMs "know" Adidas has 3 stripes, dogs have 4 legs, etc.

Burial mound symbols on Soviet topographic maps are **novel domain content**:
- VLMs have no memorized prior about what these symbols look like
- There's no conflicting knowledge to override visual analysis
- The task is pure visual pattern matching, not fighting against priors

**Conclusion**: The finding that text minimization had little effect on Gemini 3 for this task is **consistent with** the underlying mechanism - there's no prior to interfere with.

### Key quotes from the original paper

> "Our study shows that SOTA VLMs fail consistently in counting visual elements (e.g., stripes in a logo) when they are strongly biased towards the subject (e.g., an Adidas logo has three stripes)."

> "Instructing VLMs to rely exclusively on the image details to answer questions (Debiased) or to double-check its answers (Double-Check) only slightly improves accuracy, by +1.87 and +2.70, respectively."

---

## Claim 2: Two-Stage Proposer-Verifier Pipelines

### What the synthesis claimed

> "A two-stage pipeline separates concerns... This architecture prevents restrictive criteria from affecting initial detection. The model sees all potential targets first, then evaluates them individually. Expected improvement: **+5-8% F1** based on comparable studies."

### Evidence search results

**I could not locate any peer-reviewed study showing +5-8% F1 improvement from a VLM→VLM two-stage architecture for object detection.**

### What exists in the literature

1. **DINO-GPT4-V** (Roboflow, Nov 2023)
   - Uses traditional CV model (Grounding DINO) for detection
   - Then GPT-4V for classification of detected regions
   - This is **hybrid VLM+CV**, not VLM→VLM two-stage
   - URL: https://blog.roboflow.com/dino-gpt-4v/

2. **VLM-R1** (March 2025)
   - Found emergent "OD aha moment" where RL-trained models spontaneously developed two-step reasoning
   - This emerged from **reinforcement learning training**, not from prompting
   - Not a recommended prompting strategy

3. **"Understand and Detect" pipeline** (ScienceDirect, Jan 2025)
   - Multi-step prompting to generate image-specific prompts
   - Not a precision→recall staging architecture
   - About prompt generation, not detection verification

4. **F-VLM** (Frozen VLM for detection)
   - Uses frozen VLM features with trained detector head
   - Architectural approach, not prompting strategy

### The apparent source of the claim

The "+5-8% F1" figure appears to have been **extrapolated from general machine learning intuitions** about cascaded classifiers, not from VLM-specific empirical work.

In traditional ML, two-stage systems (e.g., region proposal networks followed by classifiers) often improve over single-stage systems. However:
- These involve **trained components** optimized end-to-end
- Prompting a VLM twice is not equivalent to architectural cascading
- Each VLM call introduces its own error modes

### Why two-stage may have hurt performance

Possible explanations for the observed degradation:

1. **Compounding errors**: If Stage 1 (proposer) misses a target, Stage 2 never sees it. Two chances to fail, not two chances to succeed.

2. **Context loss**: The verifier may see cropped regions or highlighted candidates without full map context, losing information that aids detection.

3. **Threshold interaction**: The proposer's "liberal" threshold and verifier's "strict" threshold may interact unpredictably.

4. **Different failure modes**: Single-stage failures may be random/stochastic (fixable by voting); two-stage failures may be systematic (not fixable by voting).

---

## Claim 3: Consensus Voting

### What the synthesis claimed

> "Multi-pass voting offers another precision-recall optimization: run detection 3 times at temperature 0.5... flag regions detected in ≥2/3 passes as positive. Research shows this reduces false positives by 35% while maintaining recall."

### Empirical result

**This one held up.** Consensus voting (2-of-5, 4-of-10, 10-of-30) substantially improved F1 on Gemini 3.

### Why voting works when other strategies don't

Voting addresses **stochastic variation** in VLM outputs - the randomness inherent in sampling from the model's distribution. This is:
- Model-agnostic (works regardless of architecture)
- Task-agnostic (works regardless of domain)
- Doesn't depend on assumptions about priors or text-image interaction

The other strategies made assumptions about VLM behaviour that may be:
- Model-specific (Gemini 2.5 vs 3)
- Task-specific (counterfactual images vs novel domain detection)

---

## Summary Table

| Strategy | Literature Claim | Models Tested | Gemini 3 Result | Assessment |
|----------|------------------|---------------|-----------------|------------|
| Text minimization | Reduces interference, improves accuracy | Gemini 2.5 Pro, GPT-4.1, Claude 3.7, o3, o4-mini | Little effect | Literature finding doesn't generalize to novel domain tasks |
| Two-stage pipeline | +5-8% F1 | **No VLM-specific evidence found** | Actively harmful | Claim appears unsupported by VLM research |
| Consensus voting | Reduces FP by 35% | Various | Works well | Confirmed - most robust strategy |

---

## Implications for Implementation

### What to do

1. **Use consensus voting** - this is the reliably beneficial strategy
2. **Don't assume text hurts** - for novel domain tasks, text+image may work as well as image-only
3. **Test single-stage first** - two-stage adds complexity without demonstrated benefit for VLM prompting

### What to test empirically

The planned preregistered experiment will formally test:
- H1: Text modality has no significant effect (image+text ≈ image-only)
- H2: Text elaboration doesn't help (and may hurt)
- H3: Two-stage degrades performance vs single-stage
- H4: Consensus voting improves F1

### Codebase implications

When implementing the extraction pipeline:
- **Voting is the priority optimization** - ensure robust implementation of n-of-x aggregation
- **Two-stage architecture is not recommended** - adds complexity for negative returns
- **Prompt text content is less critical than expected** - focus effort elsewhere
- **Cross-model testing needed** - strategies may behave differently on Claude/GPT vs Gemini

---

## References

1. Vo, A., Nguyen, K.-N., Taesiri, M.R., Dang, V.T., Nguyen, A.T., & Kim, D. (2025). Vision Language Models are Biased. arXiv:2505.23941. https://arxiv.org/abs/2505.23941

2. Gallagher, J. (2023). DINO-GPT4-V: Use GPT-4V in a Two-Stage Detection Model. Roboflow Blog. https://blog.roboflow.com/dino-gpt-4v/

3. VLM-R1 (2025). Improving Object Detection through Reinforcement Learning with VLM-R1. https://om-ai-lab.github.io/2025_03_20.html

4. Guo, M. et al. (2025). Understand and Detect: Multi-step zero-shot detection with image-level specific prompt. Knowledge-Based Systems. https://www.sciencedirect.com/science/article/abs/pii/S0950705125001303

---

## Document History

- 2024-12-22: Created based on conversation with Claude reviewing evidence for prompting strategy claims
