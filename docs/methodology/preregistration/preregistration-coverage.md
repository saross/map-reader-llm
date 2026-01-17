# Preregistration: Experimental Coverage

**Companion document to**: `preregistration.md`
**Purpose**: Documents factorial coverage, extended tests, and explicit exclusions
**Status**: Ready for Registration

---

## 1. Core Prompt Configuration Factors

These factors control how a single detection prompt is constructed:

| Factor | Symbol | Levels | Hypothesis |
|--------|--------|--------|------------|
| Modality/Elaboration | M/E | 5 (Image-only, Brief-text+image, Verbose-text+image, Brief-text-only, Verbose-text-only) | H1 |
| Negative text treatment | H5 | 3 (Minimal, Terse, Verbose) | H5 |
| Temperature | T | 5 (0.0, 0.3, 0.7, 1.0, 1.3) | H7 |
| Ordering | O | 3 (canonical-first, canonical-last, random) | H4 |

**Note on H5**: H5 tests the text treatment for negative examples (how much exclusion guidance to provide), given negatives are present. The three levels are:
- **Minimal**: "Negative" label only (images speak for themselves)
- **Terse**: Brief exclusion guidance (1-2 sentences)
- **Verbose**: Detailed exclusion explanations

H5 is tested at ALL three image-using M/E levels (Image-only, Brief-text+image, Verbose-text+image) to detect any M/E × H5 interaction.

**Note on Ordering**: Ordering is tested at optimal M/E only (3 conditions), not as a partial cross.

**Fixed parameters (Gemini)**: The following parameters are fixed across all Gemini experiments:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `thinking_level` | `minimal` | Calibrated via pilot; minimal achieves equivalent F1 to high at 1/3 latency (see §8.9) |
| `media_resolution` | default (HIGH) | Sufficient for 512×512 tiles; no benefit from ULTRA_HIGH in pilot |
| `max_output_tokens` | 8192 | Sufficient for detection output |

---

## 2. Factor Coverage in OFAT Design

**OFAT tests main effects sequentially, with limited interaction coverage:**

| Factor Pair | Coverage | Notes |
|-------------|----------|-------|
| M/E × H5 | 3 × 3 = 9 cells | H5 tested at all 3 image-using M/E levels |
| M/E × T | Main effect only | T tested at optimal M/E from H1 |
| M/E × H8 | Main effect only | H8 tested at optimal M/E and T |
| H5 × T | Not tested | H5 tested at optimal T from H7 |
| H5 × H8 | Not tested | Both tested at respective optima |
| M/E × O | Main effect only | O tested at optimal M/E only |

**Interaction detection**: The 3×3 M/E × H5 factorial in Phase 2d allows testing of this interaction. Other interactions are not directly testable but are controlled by sequential optimisation.

---

## 3. Experimental Designs

### 3.1 Sequential OFAT Design (H1, H7, H8, H5, H4)

**Design**: Sequential One-Factor-At-a-Time (OFAT), carrying optimal parameters forward:

| Phase | Factor | Cells | Cumulative |
|-------|--------|-------|------------|
| Phase 2a | H1 — Modality/Elaboration (5 levels) | 5 | 5 |
| Phase 2b | H7 — Temperature (5 levels) | 5 | 10 |
| Phase 2c | H8 — Library Composition (7 conditions) | 7 | 17 |
| Phase 2d | H5 — Negative Text (3 M/E × 3 H5, 6 net new) | 6 | 23 |
| Phase 2e | H4 — Ordering (3 conditions at optimal M/E) | 3 | 26 |
| **Confirmatory total** | | **26** | |

**H5 expanded scope**: H5 is tested at ALL three image-using M/E levels (Image-only, Brief-text+image, Verbose-text+image) to detect M/E × H5 interaction. 3 M/E × 3 H5 = 9 cells total; 3 overlap with H1 baseline (each M/E at H5=Minimal), leaving 6 net new cells.

Each condition evaluated with K=10 independent single-pass runs on 60 holdout tiles.

**Evaluation protocol**: Results characterised statistically (mean F1, SD, 95% CI). Post-hoc voting analysis computed from the same runs (N=5 from runs 1-5 or 6-10; N=10 from all runs).

### 3.2 H2 Analysis (Contrasts within Factorial)

H2 is tested as planned contrasts within the main factorial, not as a separate experiment:

- **Brief-text vs Verbose-text** (text-only comparison)
- **Brief-text+image vs Verbose-text+image** (text+image comparison)

All pairwise elaboration comparisons are available from the M/E factor in the main factorial.

### 3.3 H4 Design (Ordering at Optimal M/E)

**Design**: 3 orderings at optimal M/E only = **3 conditions**

| Ordering | Description |
|----------|-------------|
| Canonical-first | Canonical positives and negatives before hard examples |
| Canonical-last | Hard examples first, canonical last |
| Random | All examples shuffled |

**Triggered exploratory (H4b)**: If H4 significant (p < 0.05), test HP-first vs HN-first ordering within the hard block (+2 cells).

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

Each condition run 5 times to provide symmetric variance estimates. Tested at optimal configuration from sequential OFAT design.

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

*Document version: 2.5*
*Created: 2026-01-02*
*Updated: 2026-01-14*

**Changelog:**

- v2.5: Aligned with preregistration.md v4.6 — replaced stranded factorial design with sequential OFAT design (26 cells); updated H5 terminology from "None/Images-only/Text+Images" to "Minimal/Terse/Verbose"; H5 now tested at all 3 image-using M/E levels (3×3=9 cells, 6 net new); updated H7 temperature levels to 5 (added T=0.3); simplified H4 to optimal M/E only (3 conditions); updated pairwise coverage matrix for OFAT design
- v2.4: Aligned with preregistration.md v4.4 — clarified HP (4 examples) included in ALL H5 conditions (H5 tests negative channel with positive guidance constant); distinguished H5=None (11 examples with HP) from H8 Pure Positive Canon (7 examples, no HP); added note on H5 factor explaining this distinction
- v2.3: Aligned with preregistration.md v4.3 — H5=None is pure-positive baseline (canonical positives + null tiles only; no canonical negatives); canonical negatives included in H5=Images-only and H5=Text+Images only
- v2.2: Corrected main design description — replaced incorrect "60-condition factorial" with stranded design (54 base cells); text-only modalities tested at H5=None only and T=1.0 only per preregistration.md; fixed H9 design from 4 conditions to 5 conditions (added temperature diversity condition D)
- v2.1: Synchronised hypothesis numbering with preregistration.md v4.2 — H5=hard negatives (3 levels), H7=temperature (4 levels), H4=ordering, H3=voting, H9=diversity; updated factorial to 60 conditions (5 M/E × 3 H5 × 4 T)
- v2.0: Major update — revised factorial design; K=10 independent runs; H2 now contrasts within factorial; ordering partial cross design; updated pairwise coverage matrix; voting from K=10 runs (N=5, N=10, N=30)
- v1.0: Initial coverage documentation
