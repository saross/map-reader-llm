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

**Estimated date**: 2026-01-03
**Soft budget limit**: $250 (may be exceeded given expanded holdout)

### Summary (from execution-plan.md)

| Phase | API Calls | Estimated Cost |
|-------|-----------|----------------|
| Phase 1: Library | ~100 | $1-2 |
| Phase 2: Factorial (48 cond × 5 passes × 60 tiles) | ~14,400 | $18-30 |
| Phase 3a: H4 Voting | ~2,400 | $75-120 |
| Phase 3b: H6 Diversity | ~2,400 | $15-24 |
| Phase 3c: H3 Two-Stage | ~1,200 | $9-15 |
| Phase 3d: H2 Elaboration | ~2,400 | $9-15 |
| Phase 4: H8 Transfer | ~1,400 | $40-70 |
| **Confirmatory Total** | **~24,300** | **$167-276** |
| Phase 5: Exploratory | ~2,000-5,000 | $20-50 |
| **Grand Total** | **~26,300-29,300** | **$187-326** |

**Contingency**: 20% buffer → **Budget ceiling: ~$390**

### Budget Reserves Allocation

| Reserve | Amount | Purpose |
|---------|--------|---------|
| Contingency | ~$40 | API failures, retries |
| H8 escalation | ~$50 | If transfer triggers activate |
| Unexpected findings | ~$50 | Worth-pursuing discoveries |

**Note**: Budget increased due to expanded holdout set (60 tiles vs original 20).
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

**Decision**: Run full 48-condition factorial plus extended coverage (Tiers 1-3)

**Rationale**:
- Expanded holdout (60 tiles) provides improved statistical power (MDE ≈ 0.07-0.09 for F1)
- Comprehensive pairwise coverage enables strong claims about interactions
- Extended coverage tests plausible mechanisms (diversity × hard negatives, voting × modality)

**Note**: Budget (~$187-326) exceeds original $250 soft limit due to holdout expansion; approved given power benefits.

**Alternatives considered**:
- Sequential determination (test M and T independently first): Rejected — budget allows full testing
- Fractional factorial: Rejected — would lose information on intermediate levels
- Reduced temperature levels: Rejected — want full characterization

### Diversity and Voting Single-Config Testing

**Decision**: Test H6 (diversity) and H4 (voting threshold) at optimal base configuration only

**Rationale**:
- Diversity mechanism (error decorrelation) is general; should generalize across configs
- Preliminary voting results showed consistent ~30-40% optimum
- Full factorial crossing would add ~$50+ for low expected information gain

**Caveats documented in preregistration**: Yes

### Two-Stage Stopping Rule

**Decision**: -0.10 F1 threshold; test at optimal single-stage config only

**Rationale**:
- Preliminary testing showed 0.2-0.4 F1 deficit
- Two-stage has ~2× cost overhead; must demonstrate near-parity to justify
- Architecture problem (context loss) unlikely fixable by configuration tuning

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
| h2-text-elaboration-comparison.md | H2 prompt specifications | Referenced in preregistration |

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
| Confirmatory (Flash) | $127-201 | | | |
| H8 Pro transfer | $40-70 | | | |
| Exploratory | $20-50 | | | |
| Contingency used | $0 | | | |
| **TOTAL** | $187-326 | | | |
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

*Created 2026-01-02*
