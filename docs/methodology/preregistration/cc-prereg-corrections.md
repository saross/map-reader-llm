# CC Instructions: Preregistration Corrections

## Document
`preregistration.md`

## Overview

This document addresses errors, inconsistencies, and minor issues identified during review of the v4.0 preregistration. These are targeted fixes, not structural changes.

---

## Fix 1: Version Number Mismatch

### Location
Line 9 (document header)

### Current
```markdown
**Document version**: 3.7
```

### Replace with
```markdown
**Document version**: 4.0
```

### Rationale
The changelog shows v4.0 as the latest entry, but the header still says 3.7.

---

## Fix 2: Wrong Hypothesis Reference in Voting Section

### Location
Section 8.5 (Voting Implementation), around line 1708

### Current
```markdown
#### Parameters for H4 Test
```

### Replace with
```markdown
#### Parameters for H3 Test
```

### Rationale
H4 is example ordering. H3 is consensus voting. This section describes voting parameters.

---

## Fix 3: Model Name Typo

### Location
Section 12.1 (Cross-Model Generalisation), around line 1981

### Current
```markdown
**Rationale**: Paper 1 focuses on Gemini 2.5 Flash for cost-efficiency.
```

### Replace with
```markdown
**Rationale**: Paper 1 focuses on Gemini 3 Flash for cost-efficiency.
```

### Rationale
The document uses "Gemini 3 Flash" throughout. This is the only instance of "Gemini 2.5".

---

## Fix 4: H5 Confirmatory Wording Clarification

### Location
Section 8.4.7 (Stranded Factorial Design), around line 1855

### Current
```markdown
- H5 Confirmatory: 4 cells (Images-only M/E × Images-only H5 × T)
```

### Replace with
```markdown
- H5 Confirmatory: 4 cells (1 optimal M/E × H5=Images-only × 4 T)
```

### Rationale
The original wording is confusing — it sounds like M/E level is "Images-only". The fix clarifies that we're testing the Images-only level of H5 (not M/E) at the optimal M/E from Strand 1.

---

## Fix 5: Ordering Section Label

### Location
Section 8.4.3 (Baseline Library), around line 1418

### Current
```markdown
**Ordering (for H5)**:
```

### Replace with
```markdown
**Ordering (for H4)**:
```

### Rationale
H4 is example ordering. H5 is hard negatives. The section describes ordering conventions.

---

## Fix 6: H9 Temperature Diversity Clarification (Optional)

### Location
Section 6, H9 (Diversity Mechanisms), around lines 869-870

### Current
```markdown
- 5-pass sequence: T=[0.7, 0.85, 1.0, 1.15, 1.3]
- Spans tested range from H7, excluding T=0.0 (deterministic, no diversity contribution)
```

### Replace with
```markdown
- 5-pass sequence: T=[0.7, 0.85, 1.0, 1.15, 1.3]
- Spans the range tested in H7 (temperature hypothesis), excluding T=0.0 (deterministic, no diversity contribution)
```

### Rationale
Minor clarification — makes explicit that H7 is the temperature hypothesis.

---

## Verification Checklist

After making changes, verify:

- [ ] Line 9: Version says "4.0"
- [ ] Section 8.5: Says "Parameters for H3 Test"
- [ ] Section 12.1: Says "Gemini 3 Flash"
- [ ] Section 8.4.7: H5 Confirmatory wording clarified
- [ ] Section 8.4.3: Says "Ordering (for H4)"
- [ ] (Optional) H9: Temperature diversity reference clarified

---

## Note: Budget Calculations Are Correct

The preregistration correctly calculates:

| Component | Cells | Calls | Cost |
|-----------|-------|-------|------|
| Strand 1 | 26 | 15,600 | ~$23 |
| H5 Confirmatory (new cells only) | 4 | 2,400 | ~$4 |
| Strand 2 | 24 | 14,400 | ~$22 |
| **Base total** | **54** | **32,400** | **~$49** |

This is correct because H5 Confirmatory only adds the Images-only level — the None and Text+Images levels were already tested in Strand 1.

No changes needed to budget calculations.
