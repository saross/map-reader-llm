# Preregistration: Experimental Coverage

**Companion document to**: `preregistration.md`
**Purpose**: Documents factorial coverage, extended tests, and explicit exclusions
**Status**: Ready for Registration

---

## 1. Core Prompt Configuration Factors

These factors control how a single detection prompt is constructed:

| Factor | Symbol | Levels | Hypothesis |
|--------|--------|--------|------------|
| Modality | M | 2 (image-only, text+image) | H1 |
| Elaboration | E | 2 (brief, elaborate) | H2 |
| Hard negatives | H | 2 (without, with) | H7 |
| Ordering | O | 3 (canonical-first, canonical-last, random) | H5 |
| Temperature | T | 4 (0.0, 0.3, 0.7, 1.0) | H9 |

---

## 2. Pairwise Coverage Matrix

**All 10 pairwise combinations of core factors are covered:**

| Pair | Covered By | Conditions |
|------|------------|------------|
| M × H | Main factorial | 2 × 2 = 4 |
| M × O | Main factorial | 2 × 3 = 6 |
| M × T | Main factorial | 2 × 4 = 8 |
| H × O | Main factorial | 2 × 3 = 6 |
| H × T | Main factorial | 2 × 4 = 8 |
| O × T | Main factorial | 3 × 4 = 12 |
| M × E | H2 design | 2 × 2 = 4 |
| E × H | H2 design | 2 × 2 = 4 |
| E × O | Added coverage | 2 × 3 = 6 |
| E × T | Added coverage | 2 × 4 = 8 |

---

## 3. Experimental Designs

### 3.1 Main Factorial (H1, H5, H7, H9)

**Design**: M(2) × O(3) × H(2) × T(4) = **48 conditions**

Each condition run with 5 passes on 60 holdout tiles.

### 3.2 H2 Design (Elaboration)

H2 is tested via a separate focused design rather than integration into the main factorial. This approach allows direct comparison of brief vs elaborate text at matched conditions.

**Core H2 design** (documented in `planning/h2-text-elaboration-comparison.md`):

- 2 × 2 × 2: Modality (text-only, text+image) × Elaboration (brief, elaborate) × Hard negatives (without, with)
- 8 conditions at T=1.0, canonical-first ordering

**Pairwise coverage extensions**:

- E × O: 2 × 3 = 6 conditions (elaboration × ordering)
- E × T: 2 × 4 = 8 conditions (elaboration × temperature)

**Total H2-related**: 8 + 6 + 8 = **22 conditions**

### 3.3 H6 Design (Diversity)

**Design**: TD(2) × ID(2) = **4 conditions** × 5 runs each = **20 runs**

Where:

- TD = Text Diversity (fixed, varied)
- ID = Image Diversity (fixed, varied)

---

## 4. Extended Interaction Coverage (Tiers 1-3)

Beyond the core factorial and H2 pairwise coverage, additional tests are conducted for interactions with plausible mechanisms.

### Tier 1: Diversity × Hard Negatives

| Test | Design | Rationale |
|------|--------|-----------|
| TD × H | 2 × 2 | Does text diversity help more when hard negatives present? |
| ID × H | 2 × 2 | Does image diversity help more when hard negatives present? |

### Tier 2: Voting/Diversity × Modality

| Test | Design | Rationale |
|------|--------|-----------|
| N × H | Grid × 2 | Does optimal voting threshold change with hard negatives? |
| N × M | Grid × 2 | Does optimal voting threshold differ by modality? |
| TD × M | 2 × 2 | Does text diversity help more with image-only? |
| ID × M | 2 × 2 | Does image diversity help more with image-only? |
| Pro voting grid | Full grid | Validate Flash threshold transfers to Pro |

### Tier 3: Temperature × Voting, Extended Cross-Model

| Test | Design | Rationale |
|------|--------|-----------|
| N × T | Grid × 4 | Does temperature affect optimal threshold? (variance → voting) |
| Extended Claude/GPT | +conditions | Strengthen generalisability claims |

---

## 5. Ensemble/Meta Factors

These factors operate "on top of" the base prompt configuration:

| Factor | Symbol | Levels | Hypothesis |
|--------|--------|--------|------------|
| Text diversity | TD | 2 (fixed, varied) | H6 |
| Image diversity | ID | 2 (fixed, varied) | H6 |
| Voting pool size | N | 4 (1, 5, 10, 30) | H4 |
| Pipeline architecture | P | 2 (single-stage, two-stage) | H3 |
| Model tier | MT | 4+ (Flash, Pro, Claude, GPT) | H8, H12 |

---

## 6. Coverage Exclusions and Rationale

The following interactions are explicitly NOT tested, with rationale:

### 6.1 Weak Mechanism (Tier 4 — Excluded)

| Interaction | Reason for Exclusion |
|-------------|---------------------|
| TD × O (text diversity × ordering) | No plausible mechanism for interaction; diversity operates independently of example ordering |
| TD × T (text diversity × temperature) | Weak mechanism; temperature affects output variance, not prompt diversity effects |
| ID × O (image diversity × ordering) | Same as TD × O |
| ID × T (image diversity × temperature) | Same as TD × T |
| Full TD × ID × H × M (16-cond factorial) | Diminishing returns; core diversity question answered by TD × ID |

### 6.2 Gated by Stopping Rules

| Interaction | Reason for Exclusion |
|-------------|---------------------|
| P × {anything} (pipeline × other factors) | Two-stage architecture must exceed single-stage by ≥0.05 F1 to justify ~2× cost overhead; exhaustive optimisation only if this threshold is met |

### 6.3 Deferred to Stage 2 or Model-Specific Studies

| Interaction | Reason for Exclusion |
|-------------|---------------------|
| Full MT × {everything} (model × all factors) | Goal is transfer validation, not per-model optimisation; full optimisation only if model shows dramatically superior cost-effectiveness |
| Stage 2 pilot | Stage 1 results needed to inform Stage 2 design; premature piloting would contaminate reserve pool |

---

## 7. Single-Configuration Testing Rationale

Some factors are tested at a single optimal configuration with documented rationale:

| Factor | Approach | Rationale | Caveat |
|--------|----------|-----------|--------|
| H6 Diversity | Tested at optimal base config | Mechanism (error decorrelation) is general; should generalise | "Generalisation to other configurations assumed" |
| H4 Voting optimal | Grid at optimal base config | Preliminary shows ~30-40% consistent | "Contingent follow-up if interactions detected" |

---

## 8. Claims Supported by This Design

### Strong Claims (Full Factorial Coverage)

- "The optimal prompt configuration is X"
- "Factors A and B do/don't interact" (for all core factor pairs)
- "Hard negatives affect diversity effectiveness" (TD×H, ID×H tested)
- "Voting threshold varies by modality/hard negatives" (N×M, N×H tested)

### Supported with Caveats

- "Optimal voting threshold is X" — "at optimal base configuration; consistent in preliminary testing"
- "Diversity helps/doesn't help" — "tested at one configuration; generalisation assumed based on mechanism"
- "Effects transfer to Pro/Claude/GPT" — "at tested configurations; stepwise adjustment if needed"

### Not Supported (Explicitly Out of Scope)

- "Diversity effect varies by ordering" — not tested (weak mechanism)
- "Two-stage architecture can be optimised to match single-stage" — only tested if competitive
- "Per-model optimisation improves on Flash-optimal" — only if cost-effective

---

## 9. Stage 2 Design Principles

**Deferred to post-Stage-1, but pre-specified:**

1. Test **top 3-5 configurations**, not just winner
2. Use **80-160 reserve tiles** (from 321 available)
3. Design based on **observed effect sizes** from Stage 1
4. **Separately preregistered** after Stage 1 completion

### Contingent Designs

| Stage 1 Outcome | Stage 2 Design |
|-----------------|----------------|
| Clear winner, no interactions | Validate top 3-5 configs on 80-160 reserve tiles |
| Significant interactions | Factorial on key interacting factors, larger N |
| Transfer failures (H8) | Model-specific optimisation |
| Marginal effects | Larger sample to resolve ambiguity |

---

*Document version: 1.0*
*Created: 2026-01-02*
