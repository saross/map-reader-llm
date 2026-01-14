# Consolidated Hypothesis Redesign: H5, H8, and H4

**Date:** January 12, 2026  
**Version:** 1.0  
**Status:** Ready for preregistration update  
**Authors:** Shawn Ross (with Claude assistance)

---

## Executive Summary

This document consolidates a significant redesign of hypotheses H5, H8, and H4 for the VLM-based burial mound detection study. The redesign addresses confounding issues in the original structure and provides cleaner separation of research questions.

### Key Changes

| Hypothesis | Original Design | Revised Design |
|------------|-----------------|----------------|
| **H5** | Tests whether negatives help AND text treatment (confounded) | Tests text treatment only (given negatives are present) |
| **H8** | Tests library size scaling (but confounds component addition) | Sequential addition + scaling (clean contrasts) |
| **H4** | Partial factorial across M/E levels | Single optimal M/E level (with triggered exploratory extension) |

### Budget Summary

| Component | Cells | Cost (~$12/cell) |
|-----------|-------|------------------|
| Confirmatory hypotheses | 18 | $216 |
| Triggered exploratory | 3 | $36 |
| **Maximum total** | **21** | **$252** |

---

## 1. Revised H8: Library Composition and Scaling

### 1.1 Research Questions

H8 now answers two distinct questions through a unified sequential design:

1. **Sequential addition**: What is the marginal value of each library component?
   - Does Canon- help? (given Canon+)
   - Do HP help? (given Canon+ and Canon-)
   - Do HN help? (given Canon+, Canon-, and HP)

2. **Size scaling**: What is the optimal total number of hard examples?
   - Where do diminishing returns set in?
   - What is the library size ceiling?

### 1.2 Design Structure

| ID | Condition | Canon+ | Canon- | HP | HN | Nulls | Total | Hard | Primary Purpose |
|----|-----------|--------|--------|-----|-----|-------|-------|------|-----------------|
| 1 | Pure Positive Canon | 4 | 0 | 0 | 0 | 3 | **7** | 0 | Minimal baseline |
| 2 | Canonical | 4 | 2 | 0 | 0 | 3 | **9** | 0 | +Canon- effect |
| 3 | +HP | 4 | 2 | 4 | 0 | 3 | **13** | 4 | +HP effect |
| 4 | Scale-4 | 4 | 2 | 2 | 2 | 3 | **13** | 4 | 1:1 floor |
| 5 | Scale-8 | 4 | 2 | 4 | 4 | 3 | **17** | 8 | +HN effect / scaling baseline |
| 6 | Scale-16 | 4 | 2 | 8 | 8 | 3 | **25** | 16 | Scaling mid |
| 7 | Scale-32* | 4 | 2 | 16 | 16 | 3 | **41** | 32 | Scaling ceiling |

*Or available maximum maintaining 1:1 HP:HN ratio. If fewer than 16 distinct HP or HN are available from training set mining, Scale-32 is capped at the maximum available while preserving 1:1 ratio.

### 1.3 Planned Contrasts

**Sequential addition contrasts** (tests component value):

| Contrast | Comparison | What It Tests | Controlled Variables |
|----------|------------|---------------|---------------------|
| C1 | Pure Positive Canon → Canonical | Does Canon- help? | Canon+ constant (4), HP=0, HN=0 |
| C2 | Canonical → +HP | Do HP help? | Canon+/- constant, HN=0 |
| C3 | +HP → Scale-8 | Do HN help? | Canon+/- constant, HP constant (4) |

**Scaling contrasts** (tests diminishing returns):

| Contrast | Comparison | Hard Examples | What It Tests |
|----------|------------|---------------|---------------|
| S1 | Scale-4 → Scale-8 | 4 → 8 | Initial scaling value |
| S2 | Scale-8 → Scale-16 | 8 → 16 | Mid-range scaling |
| S3 | Scale-16 → Scale-32 | 16 → 32 | Ceiling/diminishing returns |

**Bonus contrast** (composition vs size):

| Contrast | Comparison | What It Tests |
|----------|------------|---------------|
| B1 | +HP vs Scale-4 | At matched total (13 examples): is 4+0 or 2+2 better? |

### 1.4 Predictions

1. F1 will increase from Pure Positive Canon → Canonical (Canon- helps distinguish confusable symbols)
2. F1 will increase from Canonical → +HP (hard positives improve recall)
3. F1 will increase from +HP → Scale-8 (hard negatives improve precision)
4. F1 will increase from Scale-4 → Scale-8, with moderate marginal gain
5. F1 will increase from Scale-8 → Scale-16, with smaller marginal gain
6. F1 increase from Scale-16 → Scale-32 will show minimal or no improvement (diminishing returns)

### 1.5 Analysis

- **Primary**: One-way ANOVA across 7 library conditions
- **Planned contrasts**: As specified above (sequential addition + scaling)
- **Secondary**: Characterise diminishing returns curve (F1 vs hard example count)
- **Tertiary**: Cost-efficiency analysis (F1 improvement per input token)

### 1.6 Execution Parameters

- **M/E level**: Optimal from H1
- **H5 level**: Optimal (or Images-only if H5 not yet complete)
- **Temperature**: Optimal from H7 (or T=1.0 default)
- **Ordering**: Canonical-first (default)
- **K**: 10 independent runs per condition

### 1.7 Advance Criteria

Advance to Stage 2 if:
- Significant main effect of library composition (FDR-corrected p < 0.05), OR
- Significant deviation from expected diminishing returns pattern

---

## 2. Revised H5: Negative Text Treatment

### 2.1 Research Question

**Given that hard negatives are included in the library**, what is the optimal level of text support for negative examples?

This is distinct from "should we include negatives at all?" — which is now answered by H8 (contrast C3: +HP → Scale-8).

### 2.2 Design Structure

| Level | Condition | HN Images | Exclusion Text | Description |
|-------|-----------|-----------|----------------|-------------|
| A | Minimal | Yes | "Negative" label only | Images speak for themselves |
| B | Terse | Yes | Brief exclusion guidance | Concise "do not detect" instructions |
| C | Verbose | Yes | Detailed exclusion guidance | Full explanation of why each is not a mound |

**Library composition for all H5 conditions**: Scale-8 (or optimal from H8)
- Canon+: 4
- Canon-: 2
- HP: 4
- HN: 4
- Nulls: 3
- **Total: 17 examples**

### 2.3 Relationship to H1

H1 tests text elaboration for **positive** guidance (image-only → brief → verbose).  
H5 tests text elaboration for **negative** guidance (minimal → terse → verbose).

**Cross-hypothesis comparison**: After both H1 and H5 complete, compare optimal positive vs negative text levels. If they differ (e.g., verbose positives but terse negatives), this indicates asymmetric elaboration requirements.

### 2.4 Predictions

1. Adding terse exclusion text will improve precision vs minimal labels
2. Verbose exclusion text will show minimal additional benefit over terse (diminishing returns)
3. Optimal negative text level may differ from optimal positive text level (H1)

### 2.5 Analysis

- **Primary**: One-way ANOVA across 3 H5 levels on precision
- **Planned contrasts**: Minimal vs Terse; Terse vs Verbose
- **Secondary**: Parallel analysis on recall to confirm no significant harm
- **Tertiary**: Analysis on F1 to assess net benefit
- **Cross-hypothesis**: Compare H1 optimal vs H5 optimal text elaboration

### 2.6 Execution Parameters

- **M/E level**: Optimal from H1
- **Library composition**: Scale-8 (or optimal from H8)
- **Temperature**: Optimal from H7 (or T=1.0 default)
- **Ordering**: Canonical-first (default)
- **K**: 10 independent runs per condition

### 2.7 Advance Criteria

Advance to Stage 2 if:
- Significant H5 effect on precision (FDR-corrected p < 0.05), AND
- Recall does not significantly decrease

---

## 3. Revised H4: Example Ordering

### 3.1 Research Question

Does the positioning of canonical (legend-derived) examples relative to hard (empirically-derived) examples affect detection performance?

### 3.2 Design Structure

| Condition | Canonical Position | Hard Position | Rationale |
|-----------|-------------------|---------------|-----------|
| Canonical-first | Positions 1-6 | Final positions | Tests primacy effect |
| Canonical-last | Final positions | Positions 1-N | Tests recency effect |
| Random | Shuffled | Shuffled | Neutral baseline |

**Note**: Within the hard example block, HP and HN are interleaved randomly (documented seed). HP/HN ordering is tested separately in exploratory H4b if H4 main effect is significant.

### 3.3 Simplification Rationale

The original design tested ordering across multiple M/E levels to detect O × M/E interaction. This interaction is theoretically speculative (the hypothesis that text verbosity would moderate ordering effects lacks strong prior support). 

Testing at optimal M/E only:
- Answers the primary question (does ordering matter?)
- Saves 6 cells ($72)
- Avoids underpowered interaction tests

If H4 shows a strong main effect and interaction is suspected, OFAT sensitivity testing at a contrasting M/E level can be conducted as exploratory follow-up.

### 3.4 Predictions

Canonical-last will outperform canonical-first due to recency bias in VLM attention mechanisms. Random ordering will perform between the two.

### 3.5 Analysis

- **Primary**: One-way ANOVA across 3 ordering conditions
- **Planned contrasts**: Canonical-first vs Canonical-last; Optimal vs Random
- **Secondary**: Effect size estimation for ordering benefit

### 3.6 Execution Parameters

- **M/E level**: Optimal from H1
- **H5 level**: Optimal (or default)
- **Library**: Optimal from H8 (or Scale-8 default)
- **Temperature**: Optimal from H7 (or T=1.0 default)
- **K**: 10 independent runs per condition

### 3.7 Advance Criteria

Advance to Stage 2 if significant ordering effect detected (FDR-corrected p < 0.05).

---

## 4. Triggered Exploratory Hypotheses

### 4.1 H4b: HP/HN Ordering Within Hard Block

**Trigger**: Significant H4 main effect (p < 0.05)

**Question**: Given that ordering matters, does the position of HP relative to HN within the hard example block affect performance?

**Design** (at optimal canonical placement from H4):

| Condition | HP Position | HN Position |
|-----------|-------------|-------------|
| HP-first | Before HN | After HP |
| HN-first | After HN | Before HP |

**Cells**: 2  
**Cost**: $24

**Analysis**: Paired comparison; report effect size and direction.

### 4.2 HN-Only Condition

**Trigger**: Example-level regression (Section 8.4.5) shows |β_hardneg| > 2×|β_hardpos| AND both coefficients significant (p < 0.05)

**Question**: If HN are disproportionately valuable, can we achieve good performance with Canon + HN only (no HP)?

**Design**:

| Condition | Canon+ | Canon- | HP | HN | Nulls | Total |
|-----------|--------|--------|-----|-----|-------|-------|
| HN-only | 4 | 2 | 0 | 4 | 3 | **13** |

**Comparison**: HN-only (13) vs +HP (13) — matched size, different composition

**Cells**: 1  
**Cost**: $12

**Analysis**: Direct comparison; assess whether HP can be omitted without performance loss.

---

## 5. Complete Hypothesis Dependency Structure

```
H1 (M/E: 5 cells)
    ↓ optimal M/E
    ├── H8 (Composition + Scaling: 7 cells)
    │       ↓ optimal composition
    │       └── H5 (Negative Text: 3 cells)
    │               ↓ optimal text treatment
    │               └── H4 (Ordering: 3 cells)
    │                       ↓ if significant
    │                       └── [H4b: HP/HN Order: 2 cells] (exploratory)
    │
    └── [Cross-comparison: H1 optimal vs H5 optimal text]
    
H8 example-level analysis
    ↓ if β_hardneg >> β_hardpos
    └── [HN-only: 1 cell] (exploratory)
```

### 5.1 Parallelisation Options

To reduce timeline, some hypotheses can run in parallel with acknowledged risk:

- **H8 at default M/E**: If confident image+verbose will be optimal, H8 can start before H1 completes
- **H5 at Scale-8**: If confident Scale-8 is near-optimal, H5 can start before H8 completes

However, strictly sequential execution ensures each hypothesis runs at truly optimal parameters.

---

## 6. Summary Tables

### 6.1 Confirmatory Hypothesis Overview

| Hypothesis | Question | Cells | Cost | Dependencies |
|------------|----------|-------|------|--------------|
| H1 | Optimal M/E level? | 5 | $60 | None |
| H8 | Library composition + scaling? | 7 | $84 | H1 (optimal M/E) |
| H5 | Negative text treatment? | 3 | $36 | H1, H8 |
| H4 | Example ordering? | 3 | $36 | H1, H8, H5 |
| **Total** | | **18** | **$216** | |

### 6.2 Exploratory Hypothesis Overview

| Hypothesis | Trigger | Cells | Cost |
|------------|---------|-------|------|
| H4b | H4 significant | 2 | $24 |
| HN-only | β_hardneg >> β_hardpos | 1 | $12 |
| **Maximum** | | **3** | **$36** |

### 6.3 Budget Summary

| Scenario | Cells | Cost |
|----------|-------|------|
| Confirmatory only | 18 | $216 |
| + H4b triggered | 20 | $240 |
| + HN-only triggered | 21 | $252 |
| **Maximum** | **21** | **$252** |

---

## 7. Changes from Original Preregistration

### 7.1 H5 Changes

| Aspect | Original | Revised |
|--------|----------|---------|
| **Scope** | Tests negative presence AND text treatment | Tests text treatment only |
| **Levels** | None / Images-only / Text+Images | Minimal / Terse / Verbose |
| **Baseline** | H5=None (no negatives) | Negatives always present |
| **"Do negatives help?"** | Answered by H5 | Answered by H8 (C3 contrast) |
| **M/E interaction** | Partial cross tested | Run at optimal M/E only |

### 7.2 H8 Changes

| Aspect | Original | Revised |
|--------|----------|---------|
| **Structure** | Size scaling only | Sequential addition + scaling |
| **Contrasts** | Size jumps (7→9→13→...) | Component addition + 1:1 scaling |
| **HP/HN introduction** | Bundled | Separated (+HP then +HN) |
| **Scale-4** | Implicit in A (2+2) | Explicit condition for 1:1 floor |
| **Key question** | "What size library?" | "What components?" + "What size?" |

### 7.3 H4 Changes

| Aspect | Original | Revised |
|--------|----------|---------|
| **M/E coverage** | Partial factorial (3 M/E × 3 ordering) | Optimal M/E only |
| **Cells** | 9 (3 new beyond factorial) | 3 |
| **Interaction testing** | O × M/E tested | Deferred (speculative) |
| **HP/HN ordering** | Not addressed | Exploratory H4b (triggered) |

---

## 8. Implementation Checklist

### 8.1 Preregistration Updates Required

- [ ] Rewrite H5 section (Section 5.5 / lines 574-651)
- [ ] Rewrite H8 section (Section 5.8 / lines 743-831)
- [ ] Update H4 section to remove partial factorial (Section 5.4 / lines 538-571)
- [ ] Add H4b exploratory hypothesis (new section under Exploratory)
- [ ] Add HN-only trigger condition (Section 8.4.5 or new)
- [ ] Update hypothesis count and budget estimates throughout
- [ ] Update Strand 1/Strand 2 descriptions (Section 8.4.7)
- [ ] Update factorial coverage tables

### 8.2 Prompt File Updates Required

- [ ] Verify H5 instruction files match new levels (minimal/terse/verbose)
- [ ] Create/verify configs for all 7 H8 conditions
- [ ] Verify H4 configs use optimal M/E only
- [ ] Document HP/HN randomisation within hard block

### 8.3 Analysis Pipeline Updates

- [ ] Update H5 analysis to new 3-level structure
- [ ] Add H8 sequential contrasts to analysis plan
- [ ] Add H1/H5 cross-comparison analysis
- [ ] Add trigger logic for H4b and HN-only

---

## 9. Approval and Version History

| Version | Date | Changes | Approved |
|---------|------|---------|----------|
| 1.0 | 2026-01-12 | Initial consolidated design | Pending |

---

*End of document*
