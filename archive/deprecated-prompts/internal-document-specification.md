# Internal Project Document Specification

**Purpose**: This document specifies what should be recorded in an internal project document SEPARATE from the OSF preregistration. These items are operational/planning details that support project execution but are not methodological commitments.

**Date**: 2026-01-15 (updated for thinking level calibration)

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

**Estimated date**: 2026-01-09
**Soft budget limit**: $250 (triggers review, not hard cap)

### Summary (from execution-plan.md v3.0)

| Component | Cells | Calls | Cost (~$11/cell) |
|-----------|-------|-------|------------------|
| H1 (M/E) | 5 | 15,000 | ~$55 |
| H7 (Temperature) | 5 | 15,000 | ~$55 |
| H8 (Composition) | 7 | 21,000 | ~$77 |
| H5 (Negative Text) | 6 | 18,000 | ~$66 |
| H4 (Ordering) | 3 | 9,000 | ~$33 |
| **Confirmatory total** | **26** | **78,000** | **~$286** |

**Soft budget limit**: $500 (triggers review, not hard cap)
**Contingency**: 20% buffer → **Budget ceiling: ~$600**

### Budget Reserves Allocation

| Reserve | Amount | Purpose |
|---------|--------|---------|
| Contingency | ~$50 | API failures, retries |
| H6 escalation | ~$50 | If Pro shows superiority warranting full optimisation |
| Unexpected findings | ~$30 | Worth-pursuing discoveries |

**Note**: Sequential OFAT design (26 confirmatory cells), K=10 protocol, and OFAT approach for H6 Pro transfer.
```

### 2.2 Pricing Assumptions

```markdown
## API Pricing Assumptions

**Date recorded**: 2026-01-09
**Note**: Record actual pricing at experiment start; update if pricing changes during study.

### Published Pricing (Gemini 3 Flash verified 2026-01-09)

| Model | Input $/1M tokens | Output $/1M tokens | Per-Call Est. | Calculation Basis |
|-------|-------------------|--------------------| --------------|-------------------|
| Gemini 3 Flash | $0.50 | $3.00 | $0.003 | ~5K input + 200 output tokens |
| Gemini 3 Pro | ~$5.00 | ~$30.00 | ~$0.03 | ~10× Flash (needs verification) |
| Claude 4.5 Sonnet | TBD | TBD | ~$0.02 | Estimate |
| GPT-5.2 Thinking | TBD | TBD | ~$0.025 | Estimate |

**Per-call calculation**: (5,000 input × $0.50/1M) + (200 output × $3.00/1M) = $0.0025 + $0.0006 ≈ $0.003

**Thinking tokens**: Gemini thinking tokens (`thoughts_token_count`) are billed as output tokens. With `thinking_level=minimal`, thinking token overhead is negligible. Higher thinking levels would significantly increase output token costs.

**Source**: [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing)

### Actual Pricing (to be filled at experiment start)

| Model | Actual Input $/1M | Actual Output $/1M | Date Recorded |
|-------|-------------------|--------------------| --------------|
| Gemini 3 Flash | | | |
| Gemini 3 Pro | | | |
| Claude 4.5 Sonnet | | | |
| GPT-5.2 Thinking | | | |

### Pilot vs Projection Discrepancy Note

Initial cost projections assumed $0.0015/call for Flash. Actual pricing ($0.003/call) is ~2× higher.
Pilot exploratory work (Dec 2025) cost A$62.93, which included API learning curve, proactive runs by
Gemini in Antigravity, and some accidental Pro usage. This informed the revised budget estimates.
```

### 2.3 Decision Rationale Log

```markdown
## Key Design Decisions

This section documents the rationale for major design decisions, for internal reference.

### Sequential OFAT Design Scope

**Decision**: Run sequential One-Factor-At-a-Time (OFAT) design with 26 confirmatory cells

**Design**:
- Phase 2a: H1 — Modality/Elaboration (5 levels) = 5 cells
- Phase 2b: H7 — Temperature (5 levels) = 5 cells
- Phase 2c: H8 — Library Composition (7 conditions) = 7 cells
- Phase 2d: H5 — Negative Text (3 M/E × 3 H5, 6 net new) = 6 cells
- Phase 2e: H4 — Ordering (3 conditions) = 3 cells
- Total: 26 cells

**Rationale**:
- Sequential design reduces cells from ~54 to 26 while testing each factor at truly optimal parameters
- H5 tested at all 3 image-using M/E levels to detect M/E × H5 interaction
- K=10 independent runs enable proper variance estimation and post-hoc voting analysis
- Budget (~$286) based on ~$11/cell pricing

**Alternatives considered**:
- Full factorial crossing: Rejected — would require ~100 conditions
- H5 at optimal M/E only: Rejected — expanded to all image-using M/E to detect interactions
- N=5 voting in factorial: Rejected — K=10 independent runs enable unbiased testing

### K=10 Independent Runs Protocol

**Decision**: Evaluate each condition with K=10 independent single-pass runs

**Rationale**:
- Avoids circular application of voting when testing main effects
- Enables proper variance-based statistical comparisons
- Allows post-hoc computation of voted results (N=5 from runs 1-5 or 6-10; N=10 from all runs)
- Same data supports both factor testing and H3 voting analysis

### H4 Ordering Design

**Decision**: Test ordering at optimal M/E only (3 conditions), not as partial cross

**Rationale**:
- Simplified from 3×3 partial cross (9 cells) to 3 cells at optimal M/E
- Focuses H4 on primary question: does ordering matter?
- Triggered exploratory (H4b) tests HP-first vs HN-first if H4 significant

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

### Thinking Level Calibration (2026-01-15)

**Decision**: Use `thinking_level=minimal` for all Gemini experiments

**Pilot methodology**:
- Conditions: minimal, low, high (3 levels)
- Tiles: 20 calibration tiles × K=10 replications = 600 API calls
- Library: Canonical-only (9 examples)
- Model: gemini-3-flash-preview

**Results**:
- All three levels have overlapping 95% CIs — no significant differences
- Minimal: F1=0.479 (SD=0.023), latency=34.2s
- High: F1=0.460 (SD=0.044), latency=97.3s
- Minimal is 2.84× faster with lower variance

**Rationale**:
- Visual pattern matching does not benefit from extended reasoning
- Symbol detection is recognition-based, not reasoning-based
- Minimal achieves equivalent accuracy at 1/3 the latency and cost

**Outputs**: `outputs/pilot-thinking/`, `results/pilot-thinking/`
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
| Phase 2 Confirmatory (Flash) | ~$286 | | | |
| Phase 3 Follow-ups (Flash) | ~$70 | | | |
| H6 Pro transfer | ~$42-48 | | | |
| Exploratory | ~$40-60 | | | |
| Contingency used | $0 | | | |
| **TOTAL** | ~$439-465 | | | |
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

*Document version: 1.7*
*Created: 2026-01-02*
*Updated: 2026-01-15*

**Changelog:**

- v1.7: Added thinking level calibration decision rationale (pilot completed 2026-01-15); added thinking tokens billing note to pricing section; aligned with preregistration.md §8.9
- v1.6: Aligned with preregistration.md v4.6 and execution-plan.md v3.0 — replaced stranded factorial design with sequential OFAT design (26 cells); updated budget table (~$286 confirmatory at ~$11/cell); updated H4 design description; soft budget limit $500
- v1.5: Updated reference to execution-plan.md v2.8; aligned with preregistration.md v4.4
- v1.4: Updated pricing based on verified Gemini 3 Flash rates ($0.50/1M input, $3/1M output → $0.003/call); revised budget estimates (~$253-279 vs previous ~$116-149); soft budget limit $250; added pilot discrepancy note; aligned with execution-plan.md v2.7
- v1.3: Aligned with preregistration.md v4.2 and execution-plan.md v2.6 — replaced "60-condition factorial" with stranded design (54 base cells); updated budget tables (~$116-149 vs previous ~$150-183); text-only constraints (H5=None, T=1.0 only); fixed H10 reference (merged into H2)
- v1.2: Synchronised hypothesis numbering with preregistration.md v4.2 — H3=voting, H4=ordering, H5=hard negatives (3 levels), H6=Flash→Pro transfer, H7=temperature (4 levels), H9=diversity; updated factorial to 60 conditions (5 M/E × 3 H5 × 4 T)
- v1.1: Updated cost estimates for 100-condition factorial (~$150-183); added K=10, H4 partial cross, H6 OFAT decision rationale; updated working documents archive with cc-consolidated-design-updates.md and cc-text-image-alignment.md
- v1.0: Initial specification
