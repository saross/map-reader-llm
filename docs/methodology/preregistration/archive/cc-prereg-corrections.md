# CC Instructions: Preregistration Corrections

## Document
`preregistration.md`

## Overview
Four corrections needed following review:
1. H7 library table — add Canon- column, update totals
2. H15 implementation status — change from exploratory to confirmatory
3. H5 test type — change from "One-tailed" to "Factorial ANOVA"
4. Terminology consistency — ensure Canon+/Canon-/HP/Emp-HN used throughout

---

## Correction 1: H7 Library Composition Table

### Location
Section 5, H7 hypothesis, lines ~661-668

### Current Text
```markdown
**Library composition by H7 level**:

| H7 Level | Canonical | Hard Pos | Hard Neg | Nulls | Total |
|----------|-----------|----------|----------|-------|-------|
| None | 4 | 4 | 0 | 3 | 11 |
| Text-only | 4 | 4 | 0 | 3 | 11 |
| Images-only | 4 | 4 | 3 | 3 | 14 |
| Text+Images | 4 | 4 | 3 | 3 | 14 |
```

### Replace With
```markdown
**Library composition by H7 level**:

| H7 Level | Canon+ | Canon- | HP | Emp-HN | Nulls | Total |
|----------|--------|--------|-----|--------|-------|-------|
| None | 4 | 2 | 4 | 0 | 3 | 13 |
| Text-only | 4 | 2 | 4 | 0 | 3 | 13 |
| Images-only | 4 | 2 | 4 | 3 | 3 | 16 |
| Text+Images | 4 | 2 | 4 | 3 | 3 | 16 |

**Note**: Canon- (legend-derived negatives) are always included in H7 to provide baseline visual context for distinguishing "marker on mound" from "standalone marker". Only H15 Pure tests without Canon-.
```

### Rationale
- Aligns terminology with H15 (Canon+, Canon-, HP, Emp-HN)
- Makes explicit that Canon- is always present in H7
- Clarifies that H7 tests Emp-HN modality, not Canon- inclusion
- Corrects totals (was missing Canon- count)

---

## Correction 2: H15 Implementation Status

### Location
Section 8.7.1 Implementation Status table, line ~1856

### Current Text
```markdown
| H15 | Few-shot library size effects | 📋 Exploratory | Library size parameter |
```

### Replace With
```markdown
| H15 | Few-shot library size effects | ✅ Ready | Strand 2 core (confirmatory) |
```

### Rationale
H15 was promoted to confirmatory status in the factorial restructure.

---

## Correction 3: H5 Test Type in Summary Table

### Location
Section 7.1 Confirmatory Hypotheses summary table, line ~1139

### Current Text
```markdown
| H5 (example ordering) | Canonical placement matters | One-tailed | Significant improvement |
```

### Replace With
```markdown
| H5 (example ordering) | Canonical placement matters | Factorial ANOVA | Significant ordering effect or interaction |
```

### Rationale
H5 uses a 3×3 factorial ANOVA (Ordering × M/E), not a one-tailed test. The "Advance to Stage 2 if" column should also reflect the actual analysis (detecting ordering effect or O × M/E interaction).

---

## Correction 4: Terminology Consistency

### 4a. Section 8.4.2 Library Composition Table

#### Location
Lines ~1425-1431

#### Current Text
```markdown
| Category | Source | Purpose | Selection |
| :--- | :--- | :--- | :--- |
| Canonical positive | Map legend | Establish clear positive prototypes | 4 legend-derived symbols |
| Hard positive | FN mining | Cover difficult positive cases | Top K by frequency (target K=4) |
| Hard negative | FP mining | Prevent common false positives | Top M by frequency (target M=3) |
| Null tile | Training set | Establish "no mounds" baseline | Stratified sample (n=3) |
```

#### Replace With
```markdown
| Category | Abbreviation | Source | Purpose | Selection |
| :--- | :--- | :--- | :--- | :--- |
| Canonical positive | Canon+ | Map legend | Establish clear positive prototypes | 4 legend-derived mound types |
| Canonical negative | Canon- | Map legend | Distinguish markers on mounds from standalone markers | 2 legend-derived non-mound symbols |
| Hard positive | HP | FN mining | Cover difficult positive cases | Top K by frequency (target K=4) |
| Empirical hard negative | Emp-HN | FP mining | Prevent common false positives | Top M by frequency (target M=3) |
| Null tile | — | Training set | Establish "no mounds" baseline | Stratified sample (n=3) |
```

#### Rationale
- Adds Canon- row (was missing)
- Adds abbreviation column for consistency with H15/H7 tables
- Uses consistent terminology throughout

---

### 4b. Section 8.4.3 Baseline Library — Add Canon- Section

#### Location
After "Canonical positives (legend-derived):" section, lines ~1442-1445

#### Current Text
```markdown
**Canonical positives** (legend-derived):

- Burial mound, settlement mound, triangulation on mound, benchmark on mound
```

#### Replace With
```markdown
**Canonical positives (Canon+)** — legend-derived mound types:

- Burial mound, settlement mound, triangulation on mound, benchmark on mound

**Canonical negatives (Canon-)** — legend-derived non-mound markers:

- Standalone triangulation point, standalone benchmark
- **Purpose**: Distinguish "marker on mound" from "marker alone" — prevents confusion between composite symbols and their components
```

---

### 4c. Category Ratios Paragraph

#### Location
Lines ~1432-1433

#### Current Text
```markdown
**Category ratios**: The baseline library uses approximately 4:K:M:3 (canonical:hard-pos:hard-neg:null). For H7 conditions without hard negatives, the ratio becomes 4:K:0:3.
```

#### Replace With
```markdown
**Category ratios**: The baseline library uses 4:2:K:M:3 (Canon+:Canon-:HP:Emp-HN:null). For H7 conditions without empirical hard negatives, the ratio becomes 4:2:K:0:3. Only H15 Pure omits Canon-.
```

---

### 4d. H7 Hard Negative Sources

#### Location
Lines ~670-673

#### Current Text
```markdown
**Hard negative sources**:

1. **Legend-derived negatives (Canon-)**: Visually confusable symbols from Soviet topographic legend (benchmark standalone, triangulation point standalone)
2. **Empirically-derived negatives (Emp-HN)**: False positives with ≥3/5 occurrence during image-only baseline on training tiles
```

#### Replace With
```markdown
**Hard negative sources**:

1. **Canon-** (legend-derived negatives): Standalone triangulation point, standalone benchmark — always included in H7 to provide baseline context
2. **Emp-HN** (empirically-derived hard negatives): False positives with ≥3/5 occurrence during image-only baseline on training tiles — presence/modality controlled by H7 factor

**Note**: H7 tests Emp-HN modality (text/images/both/none). Canon- is always present as baseline visual vocabulary. Only H15 Pure tests without Canon-.
```

---

## Verification Checklist

After making changes, verify:

- [ ] H7 table shows Canon+ (4) + Canon- (2) = 6 legend examples in all conditions
- [ ] H7 totals are 13/13/16/16 (not 11/11/14/14)
- [ ] H7 note explains Canon- always present, only H15 Pure omits
- [ ] H15 marked as confirmatory in Section 8.7.1
- [ ] H5 test type is "Factorial ANOVA" in Section 7.1
- [ ] Section 8.4.2 has 5-row table including Canon-
- [ ] Section 8.4.3 documents Canon- symbols
- [ ] All tables use consistent terminology: Canon+, Canon-, HP, Emp-HN
- [ ] No orphaned references to old terminology ("Canonical" alone, "Hard negative" without Emp- prefix)

---

## Summary of Key Points

| Term | Meaning | Count |
|------|---------|-------|
| Canon+ | Legend-derived mound types | 4 |
| Canon- | Legend-derived non-mound markers | 2 |
| HP | Empirically-derived hard positives (FNs) | Varies by condition |
| Emp-HN | Empirically-derived hard negatives (FPs) | Varies by condition |
| Nulls | Empty tiles | 3 |

**Key principle**: Canon- is always present except in H15 Pure. H7 varies Emp-HN modality, not Canon- inclusion.
