# Consolidated Design Updates for Preregistration

**Purpose**: Implement all design decisions from final review session
**Date**: 2026-01-03
**Excludes**: Pro transfer constraints (to be specified separately)

---

## Summary of Changes

| Change | Impact |
|--------|--------|
| Holdout expansion (20 → 60 tiles) | Higher power, MDE ~0.07-0.09 |
| K=10 independent runs | Proper variance estimates, avoids voting circularity |
| Revised factorial design | 100 conditions (5 M/E × 4 H7 × 5 T) |
| H5 partial cross | 6 conditions crossing ordering with 3 M/E levels |
| H3 stopping rule | Must exceed single-stage by ≥0.05 F1 |
| Temperature range | Extended to T=1.3 with escalation trigger |
| Section 3.3 revision | Added directional consistency criterion |
| H6 text diversity | Level 3 specification (content variation, fixed structure) |

---

## 1. Holdout Tile Expansion

**See separate document**: `cc-editing-instructions-expand-holdout.md`

This change is already documented. Key points:
- Expand from 20 to 60 holdout tiles (15 per map)
- Reserve drops from 321 to 281 tiles
- Update power estimates: MDE ≈ 0.07-0.09 for F1

---

## 2. Evaluation Protocol: K=10 Independent Runs

### 2.1 Rationale

Running K=10 independent single-pass runs (rather than N=5 voting) provides:
- Proper variance estimates (mean, SD, CI) for each condition
- Avoids circular application of voting when testing other hypotheses
- Enables post-hoc voting analysis at multiple thresholds (N=5, N=10)
- Answers both "pure effect" and "does voting help?" from same data

### 2.2 Add New Section 3.8 (after Section 3.7 Blinding)

```markdown
### 3.8 Evaluation Protocol

**Independent runs**: Each condition in the main factorial is evaluated using K=10 independent single-pass runs. Results are characterized statistically (mean F1, SD, 95% CI).

**Rationale**: Independent runs provide unbiased estimates of each factor's effect without assuming voting (which is itself under test in H4). This design:
- Avoids circular application of voting when testing other hypotheses
- Enables proper variance-based statistical comparisons
- Allows post-hoc computation of voted results for comparison

**Post-hoc voting analysis**: Voting performance is computed from the same runs:
- N=5 voting: runs 1-5 as one pool, runs 6-10 as another (two independent estimates)
- N=10 voting: all runs as single pool
- Multiple thresholds computed for each N

**H4 integration**: The K=10 protocol directly supports H4 analysis. Additional N=30 runs are conducted at the optimal configuration to extend the voting characterization.
```

### 2.3 Update References Throughout

Search for and update any references to "5 passes" or "N=5" in the main factorial context:

| Section | Find | Replace With |
|---------|------|--------------|
| Various | "5 passes" (factorial context) | "K=10 independent runs" |
| Various | "N=5 voting" (factorial context) | "K=10 independent runs with post-hoc voting analysis" |

**Note**: H6 Diversity retains its own protocol (5 runs × 5 passes for voting diversity testing).

---

## 3. Revised Factorial Design

### 3.1 Update Factor Definitions

The main factorial tests **100 conditions**:

| Factor | Symbol | Levels | Values |
|--------|--------|--------|--------|
| Modality/Elaboration | M/E | 5 | Image-only, Brief-text, Brief-text+image, Verbose-text, Verbose-text+image |
| Hard negatives | H7 | 4 | None, Text-only, Images-only, Text+Images |
| Temperature | T | 5 | 0.0, 0.3, 0.7, 1.0, 1.3 |

**Total**: 5 × 4 × 5 = **100 conditions**

**API calls**: 100 × 10 runs × 60 tiles = **60,000 calls** (~$90 Flash)

### 3.2 Update Section 8.4.6 or Equivalent

Replace current factorial description with:

```markdown
#### Main Factorial Design

**Design**: M/E(5) × H7(4) × T(5) = 100 conditions

| Factor | Levels | Values |
|--------|--------|--------|
| Modality/Elaboration (M/E) | 5 | Image-only, Brief-text, Brief-text+image, Verbose-text, Verbose-text+image |
| Hard negatives (H7) | 4 | None (A), Text-only (B), Images-only (C), Text+Images (D) |
| Temperature (T) | 5 | 0.0, 0.3, 0.7, 1.0, 1.3 |

**Evaluation**: Each condition evaluated with K=10 independent single-pass runs on 60 holdout tiles.

**Modality/Elaboration levels**:
- **Image-only**: Minimal text instruction, visual examples only
- **Brief-text**: Text-only prompt (~200-400 words), no images
- **Brief-text+image**: Brief text combined with visual examples
- **Verbose-text**: Elaborate text-only prompt (~700-1400 words), no images
- **Verbose-text+image**: Elaborate text combined with visual examples

**Hard negative levels** (2×2 decomposition):
- **A (None)**: Positive examples only, no exclusion guidance
- **B (Text-only)**: Explicit exclusion instructions, no visual counter-examples
- **C (Images-only)**: Hard negative images with minimal labels
- **D (Text+Images)**: Hard negative images with explicit explanatory labels

**Temperature levels**: Extended above vendor default to characterize full response curve. See Section H9 for escalation trigger.

**Hypotheses tested**: H1 (text modality), H2 (elaboration), H7 (hard negatives), H9 (temperature), plus all pairwise interactions.
```

### 3.3 Update H1 Description

Find current H1 and update to reflect 5-level M/E factor:

```markdown
### H1: Text Modality Effects

**Background**: The text-image interference literature (Vo et al., 2025) found VLMs override visual analysis with textual priors. This effect may not apply to novel domain content with no conflicting prior knowledge.

**Prediction**: Text modality will not significantly affect detection performance for this novel domain task.

**Test**: Compare detection performance across modality/elaboration levels:

| Level | Text | Images | Description |
|-------|------|--------|-------------|
| Image-only | Minimal | Yes | Few-shot visual examples with minimal task instruction |
| Brief-text | Brief | No | Text-only with concise symbol descriptions |
| Brief-text+image | Brief | Yes | Brief text combined with visual examples |
| Verbose-text | Elaborate | No | Text-only with comprehensive descriptions |
| Verbose-text+image | Elaborate | Yes | Elaborate text combined with visual examples |

**Analysis**: 
- One-way ANOVA across 5 M/E levels
- Planned contrasts: Image-only vs Brief-text+image; Brief vs Verbose within each image condition
- Two-tailed tests; equivalence supported if 95% CI for pairwise F1 differences includes zero and excludes ±0.05

**Advance to Stage 2 if**: Significant differences detected between levels, suggesting modality/elaboration choices matter for this domain.
```

### 3.4 Update H2 Description

H2 becomes a focused contrast within the factorial rather than separate experiment:

```markdown
### H2: Text Elaboration Does Not Improve Performance

**Background**: Adding lengthy descriptive text instructions does not appear to improve recall over brief text instructions.

**Prediction**: Elaborate text instructions will not improve F1 compared to brief instructions.

**Test**: Planned contrasts within the main factorial:
- Brief-text vs Verbose-text (text-only comparison)
- Brief-text+image vs Verbose-text+image (text+image comparison)

**Analysis**: One-tailed tests; H0: elaborate ≤ brief; H1: elaborate > brief. Prediction is that H0 will not be rejected.

**Advance to Stage 2 if**: Elaborate text shows significant improvement in either comparison (would contradict preliminary findings).
```

---

## 4. H5 Ordering: Partial Cross with Mitigation

### 4.1 Update H5 Description

```markdown
### H5: Example Ordering Affects Performance (Canonical Placement)

**Background**: VLMs exhibit documented recency bias where attention heads prioritize the final demonstration example. However, prototype theory suggests establishing canonical forms before presenting edge cases may improve schema formation.

**Prediction**: The relative placement of canonical examples versus hard examples will affect detection performance.

**Test**: Compare detection performance across three ordering conditions:

* Condition A: Canonical-first — Legend entries in initial positions, followed by hard examples  
* Condition B: Canonical-last — Hard examples in initial positions, legend entries in final positions  
* Condition C: Random ordering (average of 3 random permutations with documented seeds)

**Partial factorial cross**: Ordering is tested at 3 M/E levels to assess M/E × O interaction:
- Image-only (minimal text may increase ordering sensitivity)
- Brief-text+image (probable operational mode)
- Verbose-text+image (extensive text may reduce ordering sensitivity)

**Design**: 3 orderings × 3 M/E levels = 9 conditions, tested at optimal H7 and T from main factorial.

**Note**: Canonical-first ordering is used throughout the main factorial. This design adds canonical-last and random orderings at the 3 selected M/E levels.

**Mitigation trigger**: If H5 shows significant O × M/E interaction (p < 0.10), extend ordering tests to remaining 2 M/E levels (Brief-text, Verbose-text) to complete the factorial.

**Analysis**:
- Primary: 3 × 3 ANOVA (Ordering × M/E subset)
- Test for O × M/E interaction
- If no interaction: report main effect of ordering pooled across M/E levels

**Advance to Stage 2 if**: Significant ordering effect or O × M/E interaction detected.
```

---

## 5. H9 Temperature: Extended Range with Trigger

### 5.1 Update H9 Description

```markdown
### H9: Temperature Affects Detection Performance

**Background**: Gemini documentation recommends T=1.0 for reasoning tasks. Preliminary testing found T<1.0 degraded performance. Higher temperatures may increase output diversity, potentially benefiting voting ensembles.

**Prediction**: T=1.0 (vendor recommended) will yield optimal or near-optimal performance. Lower temperatures will degrade performance; higher temperatures may increase variance without improving mean F1.

**Test**: Compare detection performance across 5 temperature levels:

| Level | Temperature | Rationale |
|-------|-------------|-----------|
| 1 | 0.0 | Minimum (deterministic) |
| 2 | 0.3 | Low variance |
| 3 | 0.7 | Moderate variance |
| 4 | 1.0 | Vendor default |
| 5 | 1.3 | Above default (conservative extension) |

**Analysis**: 
- One-way ANOVA across 5 temperature levels
- Planned contrasts: T=1.0 vs each other level
- Examine temperature × voting interaction via post-hoc analysis

**Temperature escalation trigger**: If T=1.3 yields higher F1 than T=1.0 (point estimate, same M/E and H7 condition), exploratory testing at T=1.6 and T=2.0 will be conducted at the optimal configuration to characterize the upper bound of the temperature-performance curve.

**Advance to Stage 2 if**: Any temperature significantly outperforms T=1.0, or if escalation trigger activates and higher temperatures show continued improvement.
```

---

## 6. H3 Stopping Rule Revision

### 6.1 Replace H3 Section

Already provided in previous response. Key change:

**Old**: Stop if two-stage is ≥0.10 *lower* than single-stage
**New**: Continue only if two-stage is ≥0.05 *higher* than single-stage

```markdown
### H3: Coarse-to-Fine Two-Stage Pipeline Degrades Performance

**Background**: Two-stage pipelines are recommended in general ML but lack VLM-specific evidence. Preliminary testing found coarse-to-fine (proposer-verifier) degraded performance, likely due to context loss when cropping candidate regions.

**Prediction**: Two-stage coarse-to-fine (proposer-verifier) detection will produce lower F1 than single-stage detection.

**Test**: Compare detection performance with:

* Condition A: Single-stage detection (baseline prompt)
* Condition B: Two-stage proposer-verifier pipeline (liberal proposer → strict verifier)

**Testing approach**: The two-stage pipeline will be tested using the optimal single-stage configuration identified from the main factorial (M/E, H7, T). This approach ensures a fair comparison where any performance difference reflects architectural rather than configurational factors.

**Stopping rule**: Two-stage architecture will only be pursued further if it demonstrates F1 at least 0.05 higher than single-stage at the same configuration. Given the inherent cost (~2× API calls) and complexity overhead, parity or marginal improvement would not justify the additional operational burden when deeper single-stage voting is available as an alternative.

**Scope limitation**: Exhaustive optimisation of proposer-verifier configurations (e.g., varying proposer/verifier thresholds, prompt variants for each stage) is beyond the scope of this study. Such investigation would be warranted only if initial testing shows the architecture exceeds single-stage performance by at least 0.05 F1.

**Applicability to other two-stage approaches**: The same stopping rule (must exceed single-stage by ≥0.05 F1) applies to H10 (fine-to-coarse validation) and any other multi-stage architecture tested. Two-stage approaches must demonstrate clear improvement to justify their overhead.

**Analysis**: One-tailed test; H0: two-stage ≥ single-stage; H1: two-stage < single-stage. Prediction is that H0 will be rejected (two-stage performs worse).

**Advance to Stage 2 if**: Two-stage shows F1 improvement of at least 0.05 over single-stage (would contradict preliminary findings and suggest the architecture merits further optimisation).
```

---

## 7. Section 3.3 Revision: Directional Consistency

### 7.1 Update Section 3.3

```markdown
### 3.3 Interpretation Guidelines

* **Statistically significant (FDR-corrected p < 0.05)**: Technique shows promise; advance to Stage 2 validation
* **Nominally significant (uncorrected p < 0.05, FDR-corrected p ≥ 0.05)**: Suggestive evidence; consider for Stage 2 with lower priority
* **Non-significant (uncorrected p ≥ 0.05)**: No statistical evidence of benefit. However, techniques showing consistent directional improvement (e.g., positive point estimate in ≥75% of conditions where tested) may be flagged for Stage 2 investigation with lowest priority if theoretically motivated. This guards against discarding genuinely useful techniques due to sampling noise.
```

---

## 8. H6 Text Diversity Specification

### 8.1 Add Section 8.3.3

**See separate document**: `cc-editing-instructions-h6-diversity.md`

Key points:
- Level 3 variation (content diversity, fixed structure)
- Task framing, instruction phrasing, and guideline wording vary
- Section headers, output format, number of guidelines stay constant
- Prompts constructed after optimal base config determined

---

## 9. H4 Integration with K=10 Protocol

### 9.1 Update H4 Description

```markdown
### H4: Consensus Voting Improves F1

**Background**: Consensus voting addresses stochastic variation in VLM outputs. Preliminary testing confirmed substantial improvements with various voting configurations.

**Prediction**: Consensus voting will improve F1 compared to single-pass detection.

**Test**: 

**Primary data source**: The K=10 independent runs from the main factorial enable voting analysis at multiple pool sizes and thresholds:

| Pool Size | Source | Thresholds |
|-----------|--------|------------|
| N=5 | Runs 1-5 or 6-10 | 1, 2, 3, 4, 5 |
| N=10 | All runs | 1, 2, ..., 10 |

**Extended voting (N=30)**: Additional 20 runs at optimal configuration to enable:
- N=30 threshold sweep (1, 2, ..., 30)
- Cost-benefit characterization of deeper voting

**Analysis**:
- Compare single-pass mean F1 vs voted F1 at each (N, threshold) combination
- Generate threshold sweep curves (F1, precision, recall vs threshold for each N)
- Identify optimal (N, threshold) balancing performance and cost
- One-tailed test for primary comparison: H0: voting ≤ single-pass; H1: voting > single-pass

**Cost-efficiency analysis**:
- F1 improvement per additional pass
- Identify diminishing returns point
- Report optimal configuration for budget-constrained deployment

**Advance to Stage 2 if**: Significant improvement confirmed. Optimize voting parameters in Stage 2.
```

---

## 10. Update Cost Summary

### 10.1 Add or Update Cost Section

```markdown
## Estimated Costs

### Tier 1: Main Factorial

| Component | Conditions | Runs | Tiles | API Calls | Est. Cost |
|-----------|------------|------|-------|-----------|-----------|
| M/E × H7 × T factorial | 100 | 10 | 60 | 60,000 | $90 |

### Tier 2: Follow-up Tests (at optimal config)

| Component | Conditions | Runs | Tiles | API Calls | Est. Cost |
|-----------|------------|------|-------|-----------|-----------|
| H5 Ordering (partial cross) | 6 | 10 | 60 | 3,600 | $5 |
| H5 Mitigation (if triggered) | 4 | 10 | 60 | 2,400 | $4 |
| H6 Diversity | 4 × 5 runs | 5 passes | 60 | 6,000 | $9 |
| H4 N=30 extension | 1 | 20 | 60 | 1,200 | $2 |
| H3 Two-stage | 1 | ~10 | 60 | ~1,200 | $2 |
| **Tier 2 subtotal** | | | | **14,400** | **$22** |

### Flash Total

| Category | API Calls | Est. Cost |
|----------|-----------|-----------|
| Tier 1 (factorial) | 60,000 | $90 |
| Tier 2 (follow-ups) | 14,400 | $22 |
| **Flash total** | **74,400** | **$112** |

### Tier 3: Pro Transfer

*To be specified separately*

### Tier 4: Exploratory

Budget permitting, after confirmatory tests complete.
```

---

## 11. Update Execution Plan

The execution-plan.md should be updated to reflect:

1. **Phase 2 design**: 100 conditions (not 48)
2. **Evaluation protocol**: K=10 independent runs
3. **H5 sequencing**: After Phase 2, partial cross
4. **Temperature levels**: 5 levels including T=1.3
5. **Cost estimates**: Updated throughout

---

## 12. Verification Checklist

After implementing all changes:

- [ ] Section 2.1, 2.4, 2.5: Holdout = 60 tiles, Reserve = 281 tiles
- [ ] Section 3.3: Includes directional consistency criterion
- [ ] Section 3.6: Power estimates updated (~0.07-0.09 F1, ~0.20 MCC)
- [ ] Section 3.8: New evaluation protocol section (K=10)
- [ ] Section 5 H1: 5-level M/E factor
- [ ] Section 5 H2: Contrasts within factorial
- [ ] Section 5 H3: Stopping rule = must exceed by ≥0.05
- [ ] Section 5 H4: Integrated with K=10 protocol
- [ ] Section 5 H5: Partial cross (3 M/E levels) with mitigation trigger
- [ ] Section 5 H9: 5 temperature levels, escalation trigger
- [ ] Section 8.3.3: H6 Level 3 diversity specification
- [ ] Section 8.4.6 (or equivalent): Updated factorial design (100 conditions)
- [ ] Cost summary: Updated throughout
- [ ] No stale references to "48 conditions", "20 holdout", "N=5 voting" in factorial context

---

*Document version: 1.0*
*Created: 2026-01-03*
