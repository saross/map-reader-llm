# Addendum: H15 Promoted to Confirmatory

**Purpose**: Promote H15 (Library Size) from exploratory to confirmatory status
**Date**: 2026-01-05
**Applies to**: cc-factorial-restructure.md and all affected documents

---

## Change Summary

H15 (Library Size) is elevated from exploratory to **confirmatory** status. It is now part of Strand 2 of the core experimental design and subject to FDR correction.

---

## Part 1: Revised Confirmatory Hypothesis List

### Previous (6 confirmatory)

H1, H2, H4, H5, H7, H9

### Updated (7 confirmatory)

H1, H2, H4, H5, H7, H9, **H15**

---

## Part 2: H15 Specification (Confirmatory)

### H15: Library Size Affects Detection Performance

**Background**: Few-shot library size affects both the information available to the model and the token cost of each query. Preliminary exploration suggested performance improves with additional examples, but the optimal size and diminishing returns curve are unknown.

**Predictions**:

1. F1 will increase from Library A (11 examples) to Library B (14 examples)
2. F1 will increase from Library B to Library C (21 examples), with smaller marginal gain
3. F1 increase from Library C to Library D (35 examples) will show minimal or no improvement (diminishing returns plateau)

**Test**: Compare detection performance across 4 library sizes:

| Condition | Canonical | Hard Positives | Hard Negatives | Null Tiles | Total |
|-----------|-----------|----------------|----------------|------------|-------|
| A | 4 | 2 | 2 | 3 | 11 |
| B | 4 | 4 | 3 | 3 | 14 |
| C | 4 | 8 | 6 | 3 | 21 |
| D | 4 | 16 | 12 | 3 | 35 |

**Fixed parameters**: Optimal verbosity (from Strand 1), H7=Text+Images, optimal temperature.

**Analysis**:

- Primary: One-way ANOVA across 4 library sizes
- Planned contrasts: A vs B, B vs C, C vs D (adjacent pairs)
- Secondary: Characterise diminishing returns curve (F1 vs library size)
- Tertiary: Cost-efficiency analysis (F1 per input token)

**Advance to Stage 2 if**: 

- Significant main effect of library size (FDR-corrected p < 0.05), OR
- Significant deviation from expected diminishing returns pattern (e.g., D substantially outperforms C)

---

## Part 3: FDR Correction Updates

### Scope

FDR correction at q = 0.05 now applies to **7 confirmatory hypotheses**:

| # | Hypothesis | Primary Test |
|---|------------|--------------|
| 1 | H1 (Modality) | ANOVA across 6 M/E levels |
| 2 | H2 (Verbosity) | Planned contrasts: Minimal vs Brief vs Verbose |
| 3 | H4 (Voting) | Voting vs single-pass comparison |
| 4 | H5 (Ordering) | 3×3 ANOVA (ordering × M/E) |
| 5 | H7 (Hard negatives) | 2×2 ANOVA (text × images) on precision |
| 6 | H9 (Temperature) | ANOVA across 5 temperatures |
| 7 | H15 (Library size) | ANOVA across 4 library sizes |

### Procedure

1. Compute p-values for all 7 primary tests
2. Rank p-values smallest to largest
3. Apply Benjamini-Hochberg: compare p(i) to (i/7) × 0.05
4. Reject hypotheses where p(i) ≤ (i/7) × 0.05

### Critical Values (for reference)

| Rank | BH threshold (q=0.05, m=7) |
|------|----------------------------|
| 1 | 0.0071 |
| 2 | 0.0143 |
| 3 | 0.0214 |
| 4 | 0.0286 |
| 5 | 0.0357 |
| 6 | 0.0429 |
| 7 | 0.0500 |

---

## Part 4: Updated Summary Tables

### Section 7.1 Confirmatory Hypotheses (preregistration.md)

**Find and replace the confirmatory hypotheses table with:**

```markdown
### 7.1 Confirmatory Hypotheses

| Hypothesis | Prediction | Test Type | Advance to Stage 2 if... |
| :---- | :---- | :---- | :---- |
| H1 (modality) | Performance differs by modality | One-way ANOVA | Significant differences found |
| H2 (verbosity) | More detail does not help | Planned contrasts | Elaboration helps (unexpected) |
| H4 (consensus voting) | Improvement | One-tailed | Significant improvement |
| H5 (example ordering) | Canonical placement matters | Factorial ANOVA | Significant effect or interaction |
| H7 (hard negatives) | Precision ↑, Recall stable | Factorial ANOVA | Precision up, recall stable |
| H9 (temperature) | T=1.0 optimal | One-way ANOVA | Any temperature outperforms 1.0 |
| H15 (library size) | Diminishing returns curve | One-way ANOVA | Significant main effect |
```

### Section 7.2 Exploratory Hypotheses (preregistration.md)

**Remove H15 from exploratory table. Updated table:**

```markdown
### 7.2 Exploratory Hypotheses

| Hypothesis | Question | Analysis |
| :---- | :---- | :---- |
| H3 (two-stage) | Does proposer-verifier help? | Compare F1 at matched config |
| H6 (diversity) | Does variation improve voting? | 2×2 factorial ANOVA |
| H8 (Flash→Pro transfer) | Do effects replicate on Pro? | OFAT sensitivity |
| H10 (fine-to-coarse) | Does context expansion help uncertain cases? | Compare F1 on uncertain subset |
| H11 (temperature variation) | Does varied temperature improve ensembles? | Paired comparison |
| H12 (cross-model consistency) | Do effects generalise across providers? | Qualitative replication |
| H13 (cross-model voting) | Does cross-model voting beat within-model? | Compare F1 at N=6 |
| H14 (training pool size) | How does pool size affect library quality? | F1 vs pool size curve |
| H16 (tile size) | How does tile size affect performance? | F1 vs tile size |
```

---

## Part 5: Updates to cc-factorial-restructure.md

### Section: Part 6 Revised Hypothesis Structure

**Replace the confirmatory table with:**

```markdown
### Confirmatory Hypotheses

| Hypothesis | Question | Test |
|------------|----------|------|
| H1 | Does modality affect performance? | Compare across 6 M/E levels |
| H2 | Does text detail level affect performance? | Minimal vs Brief vs Verbose (within image conditions) |
| H4 | Does consensus voting improve F1? | Voting analysis from K=10 runs |
| H5 | Does example ordering affect performance? | Partial cross at optimal config |
| H7 | Do hard negatives improve precision? | 2×2 (text × images) at optimal verbosity |
| H9 | Does temperature affect performance? | 5 temperatures throughout |
| H15 | Does library size affect performance? | **Strand 2** (4 library sizes) |
```

**Replace the exploratory table with:**

```markdown
### Exploratory Hypotheses

| Hypothesis | Question | Test |
|------------|----------|------|
| H3 | Does two-stage pipeline help? | Proposer-verifier at optimal config |
| H6 | Does diversity improve voting? | 2×2 (text × image diversity) |
| H8 | Do Flash optimisations transfer to Pro? | OFAT at optimal config |
| H10-H14 | Various | As previously specified (excluding H15) |
| H16 | What is optimal tile size? | As previously specified |
```

---

## Part 6: Statistical Analysis Plan Update

### Section 3.2 (preregistration.md)

**Update the confirmatory hypothesis count:**

**Find**:
```markdown
With 9 confirmatory hypotheses tested on 60 tiles
```

**Replace with**:
```markdown
With 7 confirmatory hypotheses tested on 60 tiles
```

**Note**: The previous count of 9 appears to have been stale. The current design has 7 confirmatory hypotheses after this update.

---

## Part 7: Implementation Priority Update

### Section 9 (preregistration.md)

**Add H15 to Tier 1:**

```markdown
### Tier 1: Must Test (Core Confirmatory)

- **H4** (consensus voting) — highest practical impact; foundational
- **H7** (hard negatives) — directly addresses precision issues
- **H15** (library size) — Strand 2 core; determines deployment parameters

### Tier 2: Should Test (Secondary Confirmatory)

- **H1** (modality) — Strand 1 core
- **H2** (verbosity) — Strand 1 core
- **H5** (example ordering) — low implementation cost, clear theoretical basis
- **H9** (temperature) — validates vendor recommendation

### Tier 3: Should Test (Tertiary Confirmatory)

- **H8** (Flash→Pro transfer) — validates development approach
```

---

## Part 8: Power Analysis Note

### Addition to Section 3.6 (preregistration.md)

**Add after existing power considerations:**

```markdown
**H15 power note**: With 4 library size conditions tested at K=10 runs each on 60 tiles, the design provides adequate power to detect moderate main effects. For pairwise adjacent comparisons (A vs B, B vs C, C vs D), minimum detectable differences are approximately 0.08-0.10 F1. This is sufficient to detect practically meaningful differences in library effectiveness.
```

---

## Verification Checklist

After implementing all changes:

- [ ] H15 listed in confirmatory hypotheses (Section 5 and Section 7.1)
- [ ] H15 removed from exploratory hypotheses (Section 6 and Section 7.2)
- [ ] Confirmatory count updated to 7 throughout
- [ ] FDR correction scope stated as 7 hypotheses
- [ ] H15 full specification added (predictions, test, analysis, advance criteria)
- [ ] Implementation priority updated (H15 in Tier 1)
- [ ] Power analysis note added for H15
- [ ] cc-factorial-restructure.md tables updated

---

*Addendum prepared 2026-01-05*
