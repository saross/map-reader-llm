# Correction: Library Size Ratio and Ratio Exploration Hypothesis

**Purpose**: Update H15 library conditions to 1:1 HP:HN ratio; add exploratory hypothesis for ratio testing
**Date**: 2026-01-05
**Applies to**: cc-factorial-restructure.md, cc-h15-confirmatory-addendum.md, preregistration.md

---

## Part 1: Update Library Size Conditions to 1:1 Ratio

### Rationale

No clear consensus exists in the literature on optimal HP:HN ratios for few-shot VLM prompting. Research on in-context learning suggests:
- Majority label bias can skew predictions toward over-represented categories
- Too many negative examples can cause semantic drift
- Balance (1:1) is the most defensible default

### Updated H15 Library Conditions

**Find** (in cc-factorial-restructure.md and cc-h15-confirmatory-addendum.md):

```markdown
| Condition | Canonical | HP  | HN  | Nulls | Total |
|-----------|-----------|-----|-----|-------|-------|
| A         | 4         | 2   | 2   | 3     | 11    |
| B         | 4         | 4   | 3   | 3     | 14    |
| C         | 4         | 8   | 6   | 3     | 21    |
| D         | 4         | 16  | 12  | 3     | 35    |
```

**Replace with**:

```markdown
| Condition | Canon+ | Canon- | HP | Emp-HN | Nulls | Total | Hard Examples |
|-----------|--------|--------|-----|--------|-------|-------|---------------|
| Pure      | 4      | 0      | 0   | 0      | 3     | 7     | 0             |
| Canonical | 4      | 2      | 0   | 0      | 3     | 9     | 0             |
| A         | 4      | 2      | 2   | 2      | 3     | 13    | 4             |
| B         | 4      | 2      | 4   | 4      | 3     | 17    | 8             |
| C         | 4      | 2      | 8   | 8      | 3     | 25    | 16            |
| D         | 4      | 2      | 16  | 16     | 3     | 41    | 32            |

**Terminology**:
- **Canon+**: Legend-derived positive examples (burial mound, settlement mound, trig point on mound, bench mark on mound) — always present
- **Canon-**: Legend-derived negative examples (standalone triangulation point, standalone bench mark) — distinguishes "marker on mound" from "marker alone"
- **HP**: Empirically-derived hard positives (false negatives from Phase 1)
- **Emp-HN**: Empirically-derived hard negatives (false positives from Phase 1)
- **Hard Examples**: HP + Emp-HN combined

**Baselines**:
- **Pure**: Positive examples only — tests whether VLM can detect mounds with no negative guidance at all
- **Canonical**: Adds legend-derived negatives — tests whether distinguishing similar symbols helps

**H7 Constraint**: Pure and Canonical conditions run at **H7=None** by necessity (no empirical HNs to include). Conditions A-D run at optimal H7 from Strand 1.

**Ratio**: Conditions A-D use 1:1 HP:Emp-HN ratio. This avoids majority label bias and is the most defensible default given limited guidance in the literature. Ratio exploration is addressed in H17 (exploratory).

**Progression**: Enables three key contrasts:
- Pure → Canonical: Do legend-derived negatives help?
- Canonical → A: Do empirical hard examples help?
- A → B → C → D: Diminishing returns curve (0 → 4 → 8 → 16 → 32 hard examples)
```

### Update H15 Hypothesis Specification

**In preregistration.md Section 5 (H15)**, update:

- "4 library sizes" → "6 library conditions (Pure, Canonical, A-D)"
- Add terminology section distinguishing Canon+, Canon-, HP, Emp-HN
- Note H7 constraint for Pure/Canonical conditions

**In cc-h15-confirmatory-addendum.md**, update the test description:

```markdown
**Test**: Compare detection performance across 6 library conditions:

| Condition | Canon+ | Canon- | HP | Emp-HN | Nulls | Total |
|-----------|--------|--------|-----|--------|-------|-------|
| Pure      | 4      | 0      | 0   | 0      | 3     | 7     |
| Canonical | 4      | 2      | 0   | 0      | 3     | 9     |
| A         | 4      | 2      | 2   | 2      | 3     | 13    |
| B         | 4      | 2      | 4   | 4      | 3     | 17    |
| C         | 4      | 2      | 8   | 8      | 3     | 25    |
| D         | 4      | 2      | 16  | 16     | 3     | 41    |

**Note**: Pure and Canonical run at H7=None (no empirical HNs available). Conditions A-D run at optimal H7 from Strand 1.
```

**Update predictions**:

```markdown
**Predictions**:

1. F1 will increase from Pure (7 examples) to Canonical (9 examples) — legend-derived negatives help distinguish similar symbols
2. F1 will increase from Canonical to Library A (9 → 13) — empirical hard examples help
3. F1 will increase from A to B (13 → 17), with moderate marginal gain
4. F1 will increase from B to C (17 → 25), with smaller marginal gain
5. F1 increase from C to D (25 → 41) will show minimal or no improvement (diminishing returns plateau)
```

**Update analysis**:

```markdown
**Analysis**:

- Primary: One-way ANOVA across 6 library conditions
- Planned contrasts: 
  - Pure vs Canonical (legend negatives help?)
  - Canonical vs A (empirical hard examples help?)
  - A vs B, B vs C, C vs D (diminishing returns)
- Secondary: Characterise diminishing returns curve (F1 vs total example count)
- Tertiary: Cost-efficiency analysis (F1 per input token)

**Confound note**: Pure and Canonical conditions run at H7=None by design constraint (no empirical HNs available to include). Conditions A-D run at optimal H7 from Strand 1. The Canonical → A contrast therefore tests the combined effect of (1) adding empirical hard examples and (2) applying optimal H7 setting. 

Interpretation depends on Strand 1 results:
- If Strand 1 finds H7=None is optimal → confound is moot; A-D also run at H7=None
- If Strand 1 finds H7≠None is optimal → interpret Canonical → A as a bundled treatment

**Adjustment option**: If the confound complicates interpretation, Strand 1 data can be used to estimate and adjust for the H7 effect. Specifically:
1. From Strand 1, estimate the H7 effect size (F1 difference between H7=None and H7=Optimal) at a comparable library composition
2. Subtract this estimated H7 effect from the observed Canonical → A difference
3. The residual approximates the "pure" effect of adding empirical hard examples
This adjustment is imperfect (library compositions differ slightly), but provides inferential leverage if needed. Document any such adjustment as post-hoc sensitivity analysis.
```

---

## Part 2: Add H17 (HP:HN Ratio Exploration) as Exploratory Hypothesis

### New Hypothesis: H17 (HP:HN Ratio)

**Add to Section 6 (Exploratory Hypotheses) in preregistration.md:**

```markdown
### H17: Hard Positive to Hard Negative Ratio

**Status**: Exploratory
**Prerequisite**: H15 (library size) complete; optimal library size determined

**Background**: The main factorial (H15) uses a 1:1 ratio of hard positives to hard negatives across all library sizes. However, optimal ratio may differ:
- Higher HP:HN ratio may improve recall (more positive guidance)
- Lower HP:HN ratio may improve precision (more exclusion examples)
- Optimal ratio may depend on library size or baseline error profile

**Research question**: Does the ratio of hard positives to hard negatives affect detection performance, holding total hard example count constant?

**Test**: At optimal library size from H15 (selecting from A-D only; Pure/Canonical excluded as they have no empirical hard examples), compare ratios while holding total hard example count constant:

| Condition | HP | HN | Total Hard | Ratio |
|-----------|-----|-----|------------|-------|
| R1 | 2 | 6 | 8 | 1:3 (HN-heavy) |
| R2 | 4 | 4 | 8 | 1:1 (balanced) |
| R3 | 6 | 2 | 8 | 3:1 (HP-heavy) |

**Note**: Exact counts depend on optimal library size from H15. If optimal is Library C (8 HP, 8 HN), the above applies. If optimal is Library B (4 HP, 4 HN), scale accordingly.

**Analysis**:
- Compare F1, precision, and recall across ratio conditions
- Test whether ratio affects precision vs recall differentially
- Identify whether ratio interacts with baseline error profile (FP-heavy vs FN-heavy tiles)

**Trigger**: Run if H15 shows library size matters AND budget permits (~$5-10 additional)

**Practical implication**: If ratio matters, deployment recommendations should specify not just "how many" but "what balance" of hard examples.
```

---

## Part 3: Update Exploratory Hypothesis List

### Section 7.2 (preregistration.md)

**Add H17 to the exploratory hypotheses table:**

```markdown
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
| **H17 (HP:HN ratio)** | **Does hard example ratio affect performance?** | **Compare ratios at fixed total count** |
```

---

## Part 4: Update Budget

### Strand 2 (H15) Budget Update

H15 now has 6 library conditions (Pure, Canonical, A-D):

**Updated**: 6 conditions × 5 T × K=10 × 60 tiles = **18,000 calls (~$27)**

### Exploratory Budget Note

H17 adds approximately:
- 3 ratio conditions × 5 T × K=10 × 60 tiles = 9,000 calls (~$13)
- But R2 (1:1) is already tested in H15, so incremental cost is ~6,000 calls (~$9)

**Update exploratory budget line** to reflect H17:

```markdown
| Phase 5: Exploratory (H10-H14, H16, H17) | ~7,000-12,000 | ~$40-60 |
```

---

## Part 5: Sequencing Note

H17 runs **after** H15 because:
1. H15 determines optimal library size
2. H17 tests ratio at that optimal size
3. No point testing ratio at suboptimal library size

Add to execution plan after Strand 2:

```markdown
### H17: Ratio Exploration (Conditional)

**Trigger**: H15 shows significant library size effect AND budget permits
**Prerequisite**: Optimal library size determined from H15
**Design**: 3 ratio conditions at optimal library size
**API calls**: ~6,000 (~$9)
```

---

## Verification Checklist

After implementing:

- [ ] H15 has 6 conditions: Pure, Canonical, A, B, C, D
- [ ] Terminology defined: Canon+, Canon-, HP, Emp-HN
- [ ] Pure = Canon+ (4) + Nulls (3) = 7 total
- [ ] Canonical = Canon+ (4) + Canon- (2) + Nulls (3) = 9 total
- [ ] Library A = 13 total (4 HP + 4 Emp-HN)
- [ ] Library B = 17 total (8 HP + 8 Emp-HN)
- [ ] Library C = 25 total (16 HP + 16 Emp-HN)
- [ ] Library D = 41 total (32 HP + 32 Emp-HN)
- [ ] Conditions A-D use 1:1 HP:Emp-HN ratio
- [ ] H7 constraint documented: Pure/Canonical run at H7=None
- [ ] Strand 2 budget updated to 6 conditions (~$27)
- [ ] H17 added to exploratory hypotheses (Section 6)
- [ ] H17 added to Section 7.2 table
- [ ] H17 sequencing noted (after H15, uses A-D only)
- [ ] Analysis notes confound between Pure/Canonical and A-D (H7 setting differs)
- [ ] Strand 1 adjustment option documented for post-hoc sensitivity analysis

---

*Correction prepared 2026-01-05*
