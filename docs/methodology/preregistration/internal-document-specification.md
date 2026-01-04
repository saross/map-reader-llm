# Internal Project Document Specification

**Purpose**: This document specifies what should be recorded in an internal project document SEPARATE from the OSF preregistration. These items are operational/planning details that support project execution but are not methodological commitments.

**Date**: 2026-01-03 (updated for holdout expansion)

---

## 1. Document Details

**Filename**: `vlm-burial-mounds-internal-operations.md`

**Location**: Project repository (not OSF preregistration)

**Audience**: Research team internal use; may be shared in supplementary materials post-publication

---

## 2. Content to Include

### 2.1 Cost Estimates and Budget

**Note**: Detailed cost estimates are maintained in `execution-plan.md`. Summary figures below.

```markdown
## Cost Estimates

**Estimated date**: 2026-01-04
**Soft budget limit**: $220 (with 20% contingency buffer)

### Summary (from execution-plan.md v2.0)

| Phase | API Calls | Estimated Cost |
|-------|-----------|----------------|
| Phase 1: Library + Text | ~100 | $1-2 |
| Phase 2: Factorial (100 cond × K=10 runs × 60 tiles) | ~60,000 | ~$90 |
| Phase 3a: H4 N=30 Extension | ~1,200 | ~$2 |
| Phase 3b: H5 Ordering | ~3,600 | ~$5 |
| Phase 3c: H6 Diversity | ~6,000 | ~$9 |
| Phase 3d: H3 Two-Stage | ~1,200 | ~$2 |
| **Flash Subtotal** | **~72,100** | **~$109** |
| Phase 4: H8 Pro Transfer (OFAT) | ~1,400-1,600 | ~$21-24 |
| **Confirmatory Total** | **~73,500-73,700** | **~$130-133** |
| Phase 5: Exploratory | ~2,000-5,000 | ~$20-50 |
| **Grand Total** | **~75,500-78,700** | **~$150-183** |

**Contingency**: 20% buffer → **Budget ceiling: ~$220**

### Budget Reserves Allocation

| Reserve | Amount | Purpose |
|---------|--------|---------|
| Contingency | ~$25 | API failures, retries |
| H8 escalation | ~$40 | If Pro shows superiority warranting full optimisation |
| Unexpected findings | ~$25 | Worth-pursuing discoveries |

**Note**: Budget significantly lower than previous design (~$187-326) due to K=10 protocol, H2 integration, and OFAT approach for H8.
```

### 2.2 Pricing Assumptions

```markdown
## API Pricing Assumptions

**Date recorded**: 2026-01-02
**Note**: Record actual pricing at experiment start; update if pricing changes during study.

| Model | Per-Call Estimate | Calculation Basis |
|-------|-------------------|-------------------|
| Gemini 3 Flash | $0.0015 | ~5K input + 200 output tokens |
| Gemini 3 Pro | $0.015 | ~10× Flash |
| Claude 4.5 Sonnet | $0.02 | Estimate |
| GPT-5.2 Thinking | $0.025 | Estimate |

### Actual Pricing (to be filled at experiment start)

| Model | Actual Input $/1K | Actual Output $/1K | Date Recorded |
|-------|-------------------|--------------------| --------------|
| Gemini 3 Flash | | | |
| Gemini 3 Pro | | | |
| Claude 4.5 Sonnet | | | |
| GPT-5.2 Thinking | | | |
```

### 2.3 Decision Rationale Log

```markdown
## Key Design Decisions

This section documents the rationale for major design decisions, for internal reference.

### Factorial Design Scope

**Decision**: Run full 100-condition factorial (5 M/E × 4 H7 × 5 T) with K=10 independent runs

**Rationale**:
- Expanded holdout (60 tiles) provides improved statistical power (MDE ≈ 0.07-0.09 for F1)
- 5-level M/E factor integrates modality and elaboration testing (H1 + H2) in unified design
- 4-level H7 factor enables orthogonal testing of text and image hard negatives
- K=10 independent runs enable proper variance estimation and post-hoc voting analysis

**Note**: Budget (~$150-183) is lower than previous design despite expanded factorial, due to K=10 protocol efficiency and H2 integration.

**Alternatives considered**:
- Separate H2 phase: Rejected — M/E factor provides full coverage within main factorial
- Full O crossing: Rejected — H5 partial cross sufficient with mitigation trigger
- N=5 voting in factorial: Rejected — K=10 independent runs enable unbiased testing

### K=10 Independent Runs Protocol

**Decision**: Evaluate each condition with K=10 independent single-pass runs

**Rationale**:
- Avoids circular application of voting when testing main effects
- Enables proper variance-based statistical comparisons
- Allows post-hoc computation of voted results (N=5 from runs 1-5 or 6-10; N=10 from all runs)
- Same data supports both factor testing and H4 voting analysis

### H5 Partial Cross Design

**Decision**: Test ordering as 3 × 3 partial cross (3 orderings × 3 M/E levels) instead of full factorial crossing

**Rationale**:
- Full O × M/E × H7 × T crossing would add 200 conditions
- Partial cross tests key interaction (O × M/E) at fixed H7 and T
- Mitigation trigger (p < 0.10) extends to remaining M/E levels if interaction detected

### H8 OFAT Transfer Approach

**Decision**: Use One-Factor-At-a-Time (OFAT) approach for Pro transfer validation on 20-tile subset

**Rationale**:
- Goal is transfer validation, not full Pro optimisation
- OFAT tests 1-2 alternatives per factor to check if optimal differs
- 20-tile stratified subset preserves statistical power for key comparisons
- Full Pro optimisation only if superiority warrants

### Diversity and Voting Single-Config Testing

**Decision**: Test H6 (diversity) and H4 (extended voting N=30) at optimal base configuration only

**Rationale**:
- Diversity mechanism (error decorrelation) is general; should generalise across configs
- H4 voting at N=5 and N=10 comes from K=10 factorial runs (no additional cost)
- N=30 extension requires only 20 additional runs at optimal config

**Caveats documented in preregistration**: Yes

### Two-Stage Stopping Rule

**Decision**: +0.05 F1 improvement threshold; test at optimal single-stage config only

**Rationale**:
- Preliminary testing showed 0.2-0.4 F1 deficit for coarse-to-fine
- Two-stage has ~2× cost overhead; must demonstrate clear improvement (≥0.05 F1) to justify
- Parity or marginal improvement insufficient when deeper single-stage voting is available
- Same threshold applies to H10 (fine-to-coarse) and any other multi-stage architecture

### Stage 2 Pilot Deferral

**Decision**: Do not run Stage 2 pilot during Stage 1

**Rationale**:
- Need Stage 1 effect sizes to properly power Stage 2
- Using reserve tiles now would contaminate them
- Clean separation supports two-stage trial framework

**Pre-specified**: Test top 3-5 configurations (not just winner) in Stage 2
```

### 2.4 Working Documents Archive

```markdown
## Working Documents

The following internal working documents informed the preregistration:

| Document | Purpose | Status |
|----------|---------|--------|
| preregistration-review-final.md | Comprehensive review and action items | Incorporated into preregistration |
| factorial-coverage-synopsis.md | Coverage analysis | Key content moved to preregistration-coverage.md |
| experimental-factor-inventory.md | Factor-by-factor analysis | Archived; decisions captured |
| h2-text-elaboration-comparison.md | H2 prompt specifications | Superseded by M/E factor |
| cc-consolidated-design-updates.md | 100-condition factorial, K=10 protocol | Incorporated into preregistration v3.2 |
| cc-text-image-alignment.md | Text-image alignment for library/verbose text | Incorporated into preregistration v3.2 |
| cc-editing-instructions-h6-diversity.md | H6 diversity implementation notes | Archived |

These documents are retained for project archive but are not part of the formal preregistration.
```

---

## 3. Post-Study Additions

After study completion, add the following sections:

### 3.1 Actual Costs Incurred

```markdown
## Actual Costs (Post-Study)

| Component | Estimated | Actual | Variance | Notes |
|-----------|-----------|--------|----------|-------|
| Phase 2 Factorial (Flash) | ~$90 | | | |
| Phase 3 Follow-ups (Flash) | ~$18 | | | |
| H8 Pro transfer | ~$21-24 | | | |
| Exploratory | ~$20-50 | | | |
| Contingency used | $0 | | | |
| **TOTAL** | ~$150-183 | | | |
```

### 3.2 Model Versions Used

```markdown
## Model Versions

| Model | Version ID | Date First Used | Date Last Used |
|-------|------------|-----------------|----------------|
| Gemini 3 Flash | | | |
| Gemini 3 Pro | | | |
| Claude 4.5 Sonnet | | | |
| GPT-5.2 Thinking | | | |

**Note**: If model versions changed during study, document both and stratify results if sample sizes permit.
```

### 3.3 Operational Issues

```markdown
## Operational Issues Log

| Date | Issue | Resolution | Impact |
|------|-------|------------|--------|
| | | | |
```

---

## 4. Relationship to Preregistration

This internal document **complements** but is **separate from** the OSF preregistration.

| Preregistration Contains | Internal Document Contains |
|--------------------------|---------------------------|
| Methodological commitments | Operational planning |
| What we will test | How much it will cost |
| Stopping rules and thresholds | Budget allocation |
| Analysis plan | Decision rationale |
| Exclusions with scientific rationale | Exclusions with resource rationale |

The preregistration is the **public commitment**. This document is the **project management record**.

---

## 5. Action Items for Claude Code

1. Create `vlm-burial-mounds-internal-operations.md` in project repository
2. Populate cost estimates section from Section 6 of preregistration-review-final.md
3. Add pricing assumptions table
4. Add decision rationale summaries
5. Create placeholder sections for post-study additions
6. Do NOT include any of this content in the OSF preregistration files

---

*Document version: 1.1*
*Created: 2026-01-02*
*Updated: 2026-01-04*

**Changelog:**

- v1.1: Updated cost estimates for 100-condition factorial (~$150-183); added K=10, H5 partial cross, H8 OFAT decision rationale; updated working documents archive with cc-consolidated-design-updates.md and cc-text-image-alignment.md
- v1.0: Initial specification
