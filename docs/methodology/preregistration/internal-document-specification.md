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
**Soft budget limit**: $180 (with 20% contingency buffer)

### Summary (from execution-plan.md v2.6)

| Phase | API Calls | Estimated Cost |
|-------|-----------|----------------|
| Phase 1: Library + Text | ~100 | ~$1-2 |
| Phase 2a: Strand 1 (M/E × partial H5) | ~15,600 | ~$23 |
| Phase 2b: H5 Confirmatory | ~2,400 | ~$4 |
| Phase 2c: Strand 2 (Library Size H8) | ~14,400 | ~$22 |
| Phase 2d: Strand 3 (conditional) | ~4,800 | ~$7 |
| Phase 3a: H3 N=30 Extension | ~1,200 | ~$2 |
| Phase 3b: H4 Ordering | ~3,600 | ~$5 |
| Phase 3c: H9 Diversity | ~6,000 | ~$9 |
| Phase 3d: H2 Two-Stage | ~1,200 | ~$2 |
| **Flash Subtotal** | **~49,300** | **~$75** |
| Phase 4: H6 Pro Transfer (OFAT) | ~1,400-1,600 | ~$21-24 |
| **Confirmatory Total** | **~50,700-50,900** | **~$96-99** |
| Phase 5: Exploratory | ~2,000-5,000 | ~$20-50 |
| **Grand Total** | **~52,700-55,900** | **~$116-149** |

**Contingency**: 20% buffer → **Budget ceiling: ~$180**

### Budget Reserves Allocation

| Reserve | Amount | Purpose |
|---------|--------|---------|
| Contingency | ~$25 | API failures, retries |
| H6 escalation | ~$40 | If Pro shows superiority warranting full optimisation |
| Unexpected findings | ~$25 | Worth-pursuing discoveries |

**Note**: Budget significantly lower than previous designs due to stranded factorial (54 base cells vs full 60-cell factorial), text-only constraints (H5=None and T=1.0 only), K=10 protocol, and OFAT approach for H6.
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

### Stranded Factorial Design Scope

**Decision**: Run stranded factorial design with 54 base cells (not full 60-condition factorial)

**Design**:
- Strand 1: (3 image M/E × 2 H5 × 4 T) + (2 text M/E × 1 H5 × 1 T) = 26 cells
- H5 Confirmatory: 1 optimal M/E × 1 H5 (Images-only) × 4 T = 4 cells
- Strand 2: 6 library conditions × 4 T = 24 cells
- Base total: 54 cells

**Rationale**:
- Expanded holdout (60 tiles) provides improved statistical power (MDE ≈ 0.07-0.09 for F1)
- 5-level M/E factor integrates modality and elaboration testing (H1) in unified design
- Text-only modalities tested at H5=None only (no example images) and T=1.0 only (budget efficiency)
- K=10 independent runs enable proper variance estimation and post-hoc voting analysis

**Note**: Budget (~$116-149) is lower than previous designs due to stranded structure and text-only constraints.

**Alternatives considered**:
- Full 60-condition factorial: Rejected — text-only cannot use H5=Images-only or H5=Text+Images
- Full O crossing: Rejected — H4 partial cross sufficient with mitigation trigger
- N=5 voting in factorial: Rejected — K=10 independent runs enable unbiased testing

### K=10 Independent Runs Protocol

**Decision**: Evaluate each condition with K=10 independent single-pass runs

**Rationale**:
- Avoids circular application of voting when testing main effects
- Enables proper variance-based statistical comparisons
- Allows post-hoc computation of voted results (N=5 from runs 1-5 or 6-10; N=10 from all runs)
- Same data supports both factor testing and H3 voting analysis

### H4 Partial Cross Design

**Decision**: Test ordering as 3 × 3 partial cross (3 orderings × 3 M/E levels) instead of full factorial crossing

**Rationale**:
- Full O × M/E × H5 × T crossing would add 200 conditions
- Partial cross tests key interaction (O × M/E) at fixed H5 and T
- Mitigation trigger (p < 0.10) extends to remaining M/E levels if interaction detected

### H6 OFAT Transfer Approach

**Decision**: Use One-Factor-At-a-Time (OFAT) approach for Pro transfer validation on 20-tile subset

**Rationale**:
- Goal is transfer validation, not full Pro optimisation
- OFAT tests 1-2 alternatives per factor to check if optimal differs
- 20-tile stratified subset preserves statistical power for key comparisons
- Full Pro optimisation only if superiority warrants

### Diversity and Voting Single-Config Testing

**Decision**: Test H9 (diversity) and H3 (extended voting N=30) at optimal base configuration only

**Rationale**:
- Diversity mechanism (error decorrelation) is general; should generalise across configs
- H3 voting at N=5 and N=10 comes from K=10 factorial runs (no additional cost)
- N=30 extension requires only 20 additional runs at optimal config

**Caveats documented in preregistration**: Yes

### Two-Stage Stopping Rule

**Decision**: +0.05 F1 improvement threshold; test at optimal single-stage config only

**Rationale**:
- Preliminary testing showed 0.2-0.4 F1 deficit for coarse-to-fine
- Two-stage has ~2× cost overhead; must demonstrate clear improvement (≥0.05 F1) to justify
- Parity or marginal improvement insufficient when deeper single-stage voting is available
- Same threshold applies to both two-stage directions tested in H2 (coarse-to-fine and fine-to-coarse)

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
| cc-editing-instructions-h9-diversity.md | H9 diversity implementation notes | Archived |

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
| Phase 2 Stranded Factorial (Flash) | ~$56 | | | |
| Phase 3 Follow-ups (Flash) | ~$18 | | | |
| H6 Pro transfer | ~$21-24 | | | |
| Exploratory | ~$20-50 | | | |
| Contingency used | $0 | | | |
| **TOTAL** | ~$116-149 | | | |
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

*Document version: 1.3*
*Created: 2026-01-02*
*Updated: 2026-01-09*

**Changelog:**

- v1.3: Aligned with preregistration.md v4.2 and execution-plan.md v2.6 — replaced "60-condition factorial" with stranded design (54 base cells); updated budget tables (~$116-149 vs previous ~$150-183); text-only constraints (H5=None, T=1.0 only); fixed H10 reference (merged into H2)
- v1.2: Synchronised hypothesis numbering with preregistration.md v4.2 — H3=voting, H4=ordering, H5=hard negatives (3 levels), H6=Flash→Pro transfer, H7=temperature (4 levels), H9=diversity; updated factorial to 60 conditions (5 M/E × 3 H5 × 4 T)
- v1.1: Updated cost estimates for 100-condition factorial (~$150-183); added K=10, H4 partial cross, H6 OFAT decision rationale; updated working documents archive with cc-consolidated-design-updates.md and cc-text-image-alignment.md
- v1.0: Initial specification
