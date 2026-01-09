# Preregistration: Experimental Coverage

**Companion document to**: `preregistration.md`
**Purpose**: Documents factorial coverage, extended tests, and explicit exclusions
**Status**: Ready for Registration

---

## 1. Core Prompt Configuration Factors

These factors control how a single detection prompt is constructed:

| Factor | Symbol | Levels | Hypothesis |
|--------|--------|--------|------------|
| Modality/Elaboration | M/E | 5 (Image-only, Brief-text, Brief-text+image, Verbose-text, Verbose-text+image) | H1, H2 |
| Hard negatives | H5 | 3 (None, Images-only, Text+Images) | H5 |
| Temperature | T | 4 (0.0, 0.7, 1.0, 1.3) | H7 |
| Ordering | O | 3 (canonical-first, canonical-last, random) | H4 (partial cross) |

**Note**: Ordering is tested via a partial cross (3 orderings × 3 M/E levels = 9 conditions), not in the main factorial. The main factorial uses canonical-first throughout.

---

## 2. Pairwise Coverage Matrix

**All pairwise combinations of core factors are covered:**

| Pair | Covered By | Conditions |
|------|------------|------------|
| M/E × H5 | Main factorial | 5 × 3 = 15 |
| M/E × T | Main factorial | 5 × 4 = 20 |
| H5 × T | Main factorial | 3 × 4 = 12 |
| M/E × O | H4 partial cross | 3 × 3 = 9 |
| H5 × O | (not in scope) | — |
| T × O | (not in scope) | — |

**Note**: H5 × O and T × O interactions are not tested. Ordering is tested at fixed H5 and T levels (optimal from main factorial). If H4 partial cross reveals O × M/E interaction (p < 0.10), extended coverage may be triggered.

---

## 3. Experimental Designs

### 3.1 Stranded Factorial Design (H1, H5, H7, H8)

**Design**: Stranded structure with text-only constraints:

| Strand | Design | Cells |
|--------|--------|-------|
| Strand 1 | (3 image M/E × 2 H5 × 4 T) + (2 text M/E × 1 H5 × 1 T) | 26 |
| H5 Confirmatory | 1 optimal M/E × 1 H5 (Images-only) × 4 T | 4 |
| Strand 2 | 6 library conditions × 4 T | 24 |
| **Base total** | | **54** |
| Strand 3 (conditional) | Interaction check if triggered | ~8 |
| **Maximum total** | | **~62** |

**Note**: Text-only modalities tested at H5=None only (no example images) and T=1.0 only (budget efficiency). This is not a full 60-condition factorial.

Each condition evaluated with K=10 independent single-pass runs on 60 holdout tiles.

**Evaluation protocol**: Results characterised statistically (mean F1, SD, 95% CI). Post-hoc voting analysis computed from the same runs (N=5 from runs 1-5 or 6-10; N=10 from all runs).

### 3.2 H2 Analysis (Contrasts within Factorial)

H2 is tested as planned contrasts within the main factorial, not as a separate experiment:

- **Brief-text vs Verbose-text** (text-only comparison)
- **Brief-text+image vs Verbose-text+image** (text+image comparison)

All pairwise elaboration comparisons are available from the M/E factor in the main factorial.

### 3.3 H4 Design (Ordering Partial Cross)

**Design**: O(3) × M/E(3) = **9 conditions**

| Ordering | M/E Levels |
|----------|------------|
| Canonical-first | (covered in main factorial) |
| Canonical-last | Image-only, Brief-text+image, Verbose-text+image |
| Random | Image-only, Brief-text+image, Verbose-text+image |

**New conditions**: 6 (2 orderings × 3 M/E levels). Canonical-first data from main factorial.

**Mitigation trigger**: If O × M/E interaction (p < 0.10), extend to remaining 2 M/E levels (Brief-text, Verbose-text).

### 3.4 H3 Design (Voting)

**Primary data**: K=10 runs from main factorial enable voting analysis at:

- N=5: runs 1-5 or 6-10 (two independent estimates)
- N=10: all runs as single pool

**Extended voting**: Additional 20 runs at optimal configuration for N=30 analysis.

### 3.5 H9 Design (Diversity)

**Design**: **5 conditions** comparing diversity mechanisms:

| Condition | Text | Images | Temperature | Description |
|-----------|------|--------|-------------|-------------|
| A | Fixed | Fixed | Fixed | Baseline: identical across all passes |
| B | Varied | Fixed | Fixed | Text diversity only |
| C | Fixed | Varied | Fixed | Image diversity only |
| D | Fixed | Fixed | Varied | Temperature diversity only |
| E | Varied | Varied | Varied | Full diversity |

Each condition run 5 times to provide symmetric variance estimates. Tested at optimal configuration from stranded factorial.

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
| Text diversity | TD | 2 (fixed, varied) | H9 |
| Image diversity | ID | 2 (fixed, varied) | H9 |
| Voting pool size | N | 3 (5, 10, 30) | H3 |
| Pipeline architecture | P | 2 (single-stage, two-stage) | H2 |
| Model tier | MT | 4+ (Flash, Pro, Claude, GPT) | H6, H14 |

**Note on voting**: N=5 and N=10 are derived from K=10 factorial runs. N=30 requires 20 additional runs at optimal config.

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
| H9 Diversity | Tested at optimal base config | Mechanism (error decorrelation) is general; should generalise | "Generalisation to other configurations assumed" |
| H3 Voting optimal | Grid at optimal base config | Preliminary shows ~30-40% consistent | "Contingent follow-up if interactions detected" |

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

*Document version: 2.2*
*Created: 2026-01-02*
*Updated: 2026-01-09*

**Changelog:**

- v2.2: Corrected main design description — replaced incorrect "60-condition factorial" with stranded design (54 base cells); text-only modalities tested at H5=None only and T=1.0 only per preregistration.md; fixed H9 design from 4 conditions to 5 conditions (added temperature diversity condition D)
- v2.1: Synchronised hypothesis numbering with preregistration.md v4.2 — H5=hard negatives (3 levels), H7=temperature (4 levels), H4=ordering, H3=voting, H9=diversity; updated factorial to 60 conditions (5 M/E × 3 H5 × 4 T)
- v2.0: Major update — revised factorial design; K=10 independent runs; H2 now contrasts within factorial; ordering partial cross design; updated pairwise coverage matrix; voting from K=10 runs (N=5, N=10, N=30)
- v1.0: Initial coverage documentation
