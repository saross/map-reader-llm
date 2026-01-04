# VLM Burial Mounds Detection: Internal Operations Document

**Purpose**: Operational planning details that support project execution. This document complements but is SEPARATE from the OSF preregistration.

**Audience**: Research team internal use; may be shared in supplementary materials post-publication

**Date**: 2026-01-02

---

## 1. Cost Estimates

**Estimated date**: 2026-01-02
**Soft budget limit**: $250 (self-funded threshold)

### 1.1 Confirmatory Testing (Flash)

| Component | Conditions | API Calls | Est. Cost |
|-----------|------------|-----------|-----------|
| Main factorial (M×O×H×T) | 48 | 4,800 | $7 |
| H2 core (M×E×H) | 8 | 800 | $1 |
| H2 pairwise (E×O, E×T) | 14 | 1,400 | $2 |
| H3 two-stage | 2 | 400 | $1 |
| H4 voting grid | ~45 | 900 | $1 |
| H6 diversity (4 cond × 5 runs) | 20 runs | 2,000 | $3 |
| **Flash confirmatory subtotal** | | ~10,300 | **$15** |

### 1.2 Transfer & Cross-Model

| Component | Conditions | API Calls | Est. Cost |
|-----------|------------|-----------|-----------|
| H8 Pro transfer (corners) | ~14 | 1,400 | $21 |
| **Confirmatory total** | | ~11,700 | **$36** |

### 1.3 Exploratory (H10-H16)

| Component | API Calls | Est. Cost |
|-----------|-----------|-----------|
| H10 Fine-to-coarse | ~500 | $1 |
| H11 Temperature variation | 200 | $0.30 |
| H12 Cross-model (Claude, GPT) | 2,000 | $45 |
| H13 Cross-model voting | 480 | $8 |
| H14 Training pool size | ~2,500 | $4 |
| H15 Library size | 400 | $1 |
| H16 Tile size | 300 | $3 |
| **Exploratory subtotal** | ~6,400 | **$62** |

### 1.4 Extended Coverage (Tiers 1-3)

| Test | Calls | Est. Cost |
|------|-------|-----------|
| TD×H, ID×H | 800 | $1 |
| N×H, N×M (grids) | 1,800 | $2 |
| TD×M, ID×M | 800 | $1 |
| Pro voting grid | 900 | $9 |
| N×T (4 grids) | 3,600 | $5 |
| Extended cross-model | 2,000 | $15 |
| **Extended subtotal** | ~9,900 | **$33** |

### 1.5 Summary

| Category | Est. Cost |
|----------|-----------|
| Confirmatory (Flash + Pro) | $36 |
| Exploratory | $62 |
| Extended coverage | $33 |
| **GRAND TOTAL** | **~$131** |
| **Remaining from $250** | **~$119** |

### 1.6 Budget Reserves Allocation

| Reserve | Amount | Purpose |
|---------|--------|---------|
| Contingency | ~$20 | API failures, retries |
| H8 escalation | ~$30 | If transfer triggers activate |
| Unexpected findings | ~$30 | Worth-pursuing discoveries |
| Stage 2 seed | ~$39 | Initial Stage 2 planning |

---

## 2. API Pricing Assumptions

**Date recorded**: 2026-01-02

**Note**: Record actual pricing at experiment start; update if pricing changes during study.

| Model | Per-Call Estimate | Calculation Basis |
|-------|-------------------|-------------------|
| Gemini 3 Flash | $0.0015 | ~5K input + 200 output tokens |
| Gemini 3 Pro | $0.015 | ~10× Flash |
| Claude 4.5 Sonnet | $0.02 | Estimate |
| GPT-5.2 Thinking | $0.025 | Estimate |

### 2.1 Actual Pricing (to be filled at experiment start)

| Model | Actual Input $/1K | Actual Output $/1K | Date Recorded |
|-------|-------------------|--------------------| --------------|
| Gemini 3 Flash | | | |
| Gemini 3 Pro | | | |
| Claude 4.5 Sonnet | | | |
| GPT-5.2 Thinking | | | |

---

## 3. Key Design Decisions

This section documents the rationale for major design decisions, for internal reference.

### 3.1 Factorial Design Scope

**Decision**: Run full 48-condition factorial plus extended coverage (Tiers 1-3)

**Rationale**:
- Total cost (~$131) well under $250 soft budget
- Comprehensive pairwise coverage enables strong claims about interactions
- Extended coverage tests plausible mechanisms (diversity × hard negatives, voting × modality)

**Alternatives considered**:
- Sequential determination (test M and T independently first): Rejected — budget allows full testing
- Fractional factorial: Rejected — would lose information on intermediate levels
- Reduced temperature levels: Rejected — want full characterisation

### 3.2 Diversity and Voting Single-Config Testing

**Decision**: Test H6 (diversity) and H4 (voting threshold) at optimal base configuration only

**Rationale**:
- Diversity mechanism (error decorrelation) is general; should generalise across configs
- Preliminary voting results showed consistent ~30-40% optimum
- Full factorial crossing would add ~$50+ for low expected information gain

**Caveats documented in preregistration**: Yes

### 3.3 Two-Stage Stopping Rule

**Decision**: -0.10 F1 threshold; test at optimal single-stage config only

**Rationale**:
- Preliminary testing showed 0.2-0.4 F1 deficit
- Two-stage has ~2× cost overhead; must demonstrate near-parity to justify
- Architecture problem (context loss) unlikely fixable by configuration tuning

### 3.4 Stage 2 Pilot Deferral

**Decision**: Do not run Stage 2 pilot during Stage 1

**Rationale**:
- Need Stage 1 effect sizes to properly power Stage 2
- Using reserve tiles now would contaminate them
- Clean separation supports two-stage trial framework

**Pre-specified**: Test top 3-5 configurations (not just winner) in Stage 2

---

## 4. Working Documents Archive

The following internal working documents informed the preregistration:

| Document | Purpose | Status |
|----------|---------|--------|
| preregistration-review-final.md | Comprehensive review and action items | Incorporated into preregistration |
| factorial-coverage-synopsis.md | Coverage analysis | Key content moved to preregistration-coverage.md |
| internal-document-specification.md | This document's specification | Implemented |
| h2-text-elaboration-comparison.md | H2 prompt specifications | Referenced in preregistration |
| execution-plan.md | Operational sequencing | Active planning document |

These documents are retained for project archive but are not part of the formal preregistration.

---

## 5. Post-Study Additions

After study completion, add the following sections:

### 5.1 Actual Costs Incurred

| Component | Estimated | Actual | Variance | Notes |
|-----------|-----------|--------|----------|-------|
| Confirmatory (Flash) | $15 | | | |
| H8 Pro transfer | $21 | | | |
| Exploratory | $62 | | | |
| Extended coverage | $33 | | | |
| Contingency used | $0 | | | |
| **TOTAL** | $131 | | | |

### 5.2 Model Versions Used

| Model | Version ID | Date First Used | Date Last Used |
|-------|------------|-----------------|----------------|
| Gemini 3 Flash | | | |
| Gemini 3 Pro | | | |
| Claude 4.5 Sonnet | | | |
| GPT-5.2 Thinking | | | |

**Note**: If model versions changed during study, document both and stratify results if sample sizes permit.

### 5.3 Operational Issues Log

| Date | Issue | Resolution | Impact |
|------|-------|------------|--------|
| | | | |

---

## 6. Relationship to Preregistration

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

*Created: 2026-01-02*
