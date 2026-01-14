# Interaction Triggers for Follow-up Testing

**Date:** January 12, 2026  
**Context:** Post-cascade analysis of VLM burial mound detection experiments  
**Purpose:** Guide decisions about whether to conduct OFAT interaction probes after main experiment

---

## Overview

The main experiment uses a sequential/cascading design:

```
H1 (M/E) → H8 (Composition) → H5 (Text treatment) → H4 (Ordering)
```

This efficiently answers main effect questions but doesn't directly test interactions. This document identifies signals that would warrant follow-up OFAT interaction testing.

---

## Potential Interactions to Monitor

### 1. M/E × H5 (Positive vs Negative Text Elaboration)

**Why it might matter:** Optimal text elaboration for describing what TO detect (positives) might differ from optimal text for what NOT to detect (negatives). Verbose positive guidance might pair best with terse negative guidance, or vice versa.

**Signal to trigger follow-up:**
- H1 optimal (e.g., Brief+image) ≠ H5 optimal (e.g., Verbose)
- Large effect size in one but not the other

**Follow-up design (OFAT):**
- Test H5 levels at a contrasting M/E level (e.g., if H1 optimal = Verbose, test H5 at Brief)
- 3 cells, ~$9

**What it would tell us:** Whether text elaboration recommendations are symmetric or asymmetric for positive vs negative guidance.

---

### 2. M/E × H8 (Text Elaboration × Library Size)

**Why it might matter:** Verbose text descriptions might partially substitute for hard examples (both provide disambiguation information). If so, optimal library size might be smaller at Verbose M/E than at Image-only M/E.

**Signal to trigger follow-up:**
- Performance gap between library sizes (e.g., Scale-8 vs Scale-16) is noticeably different across M/E levels in any incidental data
- Diminishing returns curve shape differs by M/E (if any cross-M/E data exists)

**Follow-up design (OFAT):**
- Test 2-3 H8 library sizes at a contrasting M/E level
- 2-3 cells, ~$6-9

**What it would tell us:** Whether verbose text reduces the need for large example libraries (cost optimisation insight).

---

### 3. Temperature × Voting Effectiveness

**Why it might matter:** Low temperatures produce more deterministic outputs, reducing diversity across runs. If T=0.3 is optimal for single-pass, it might underperform with voting because there's less variance to aggregate.

**Signal to trigger follow-up:**
- Optimal T differs for single-pass vs voted results (can assess post-hoc from K=10 data)
- Voting improvement (voted F1 − single-pass F1) correlates negatively with temperature in post-hoc analysis

**Follow-up design:**
- Already testable post-hoc from existing data (no new runs needed)
- If signal is strong, consider ensemble with mixed temperatures (H9 diversity mechanism)

**What it would tell us:** Whether temperature and voting interact, informing deployment strategy.

---

### 4. H8 × H5 (Library Composition × Text Treatment)

**Why it might matter:** Hard negatives with verbose text might be redundant — if you're explaining what not to detect in detail, showing examples might add less value. Conversely, at Minimal text, hard negative images might be essential.

**Signal to trigger follow-up:**
- H5 effect size (Minimal → Verbose improvement) differs dramatically depending on library composition
- Example-level regression shows HN contribution varies by text condition (if data allows)

**Follow-up design (OFAT):**
- Test H5 at a different H8 library size (e.g., if tested at Scale-8, probe at Scale-4 or +HP)
- 3 cells, ~$9

**What it would tell us:** Whether text and image guidance for negatives are substitutes or complements.

---

### 5. Ordering × Library Size

**Why it might matter:** With small libraries, every example is seen; ordering effects might be pronounced. With large libraries (Scale-32), recency effects might be diluted.

**Signal to trigger follow-up:**
- Strong H4 ordering effect at current library size
- Any theoretical reason to believe ordering matters more/less with library size

**Follow-up design (OFAT):**
- Test ordering at a contrasting library size
- 3 cells, ~$9

**What it would tell us:** Whether ordering recommendations generalise across library sizes.

---

## Signals from Example-Level Analysis (Section 8.4.5)

The post-hoc regression on example effectiveness may reveal interaction signals:

| Finding | Implication | Potential Follow-up |
|---------|-------------|---------------------|
| β_hardneg >> β_hardpos | HN disproportionately valuable | HN-only condition (already planned as triggered exploratory) |
| Specific HP/HN examples dominate | Library composition is sparse (few examples drive results) | Investigate what makes those examples effective |
| Category effects vary by M/E | M/E × example type interaction | Test example composition at different M/E |
| High variance in example coefficients | Some examples help, others hurt | Consider curated subset libraries |

---

## Decision Framework

After cascade results are complete, use this checklist:

### Step 1: Check for Obvious Signals

- [ ] Does H1 optimal differ from H5 optimal? → Consider M/E × H5 probe
- [ ] Does voting improvement vary by temperature? → Note for deployment; may not need new runs
- [ ] Do example-level coefficients show surprises? → Consider composition follow-ups

### Step 2: Assess Practical Value

For each potential interaction:
- Would knowing this change deployment recommendations?
- Is the effect size large enough to matter practically?
- Is there enough budget remaining?

### Step 3: Prioritise by Cost-Effectiveness

| Probe | Cells | Cost | Practical Value |
|-------|-------|------|-----------------|
| Temperature × Voting | 0 (post-hoc) | $0 | High (deployment) |
| M/E × H5 | 3 | ~$9 | Medium (text guidance) |
| M/E × H8 | 2-3 | ~$6-9 | Medium (cost optimisation) |
| H8 × H5 | 3 | ~$9 | Medium (redundancy) |
| Ordering × Library | 3 | ~$9 | Low (unless H4 effect is strong) |

---

## When NOT to Probe Interactions

- Main effects are small or non-significant (interactions of null effects are rarely meaningful)
- Budget is exhausted and Stage 2 validation is higher priority
- Results are already clear enough for deployment recommendations
- Interaction is theoretically unmotivated (fishing)

---

## Notes

- This document is for guidance after results are in, not a commitment to run these probes
- All follow-up testing would be exploratory (not confirmatory)
- Document any probes conducted and their rationale in the final paper's supplementary materials

---

*Created: 2026-01-12*
*Review after: Cascade experiment completion*
