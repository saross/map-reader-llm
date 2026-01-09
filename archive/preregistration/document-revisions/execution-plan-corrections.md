# Execution Plan Corrections

**Target file**: `execution-plan.md`
**Reference**: `preregistration.md` v4.2
**Date**: 2026-01-08

---

## Critical Fixes Required

### 1. Fix H15 → H8 (Line 24)

**Current**:
```
Phase 2c: Strand 2 (Library Size H15) ──────────────────────┤
```

**Change to**:
```
Phase 2c: Strand 2 (Library Size H8) ───────────────────────┤
```

---

### 2. Fix Exploratory Status Claims (Line 45)

**Current**:
```
**Note**: The stranded design separates text elaboration (Strand 1) from library content (Strand 2). H2, H6, and H9 are now exploratory hypotheses.
```

**Change to**:
```
**Note**: The stranded design separates text elaboration (Strand 1) from library content (Strand 2). H9 is exploratory; H2 and H6 remain confirmatory.
```

---

### 3. Fix Cell Count in Dependency Graph (Line 19)

**Current**:
```
Phase 2a: Strand 1 (Verbosity × Partial H5) ◄───────────────┤
    │    50 cells × K=10 runs                               │
```

**Change to**:
```
Phase 2a: Strand 1 (Verbosity × Partial H5) ◄───────────────┤
    │    26 cells × K=10 runs                               │
```

---

### 4. Fix H5 Confirmatory Cell Count (Line 21-22)

**Current**:
```
Phase 2b: H5 Confirmatory (Full 3-level at Optimal M/E)     │
    │    15 cells × K=10 runs                               │
```

**Change to**:
```
Phase 2b: H5 Confirmatory (Full 3-level at Optimal M/E)     │
    │    4 cells × K=10 runs                                │
```

---

### 5. Fix H10 Description (Lines 632-634)

**Current**:
```
3. **H10 (fine-to-coarse)**: Novel architecture
   - Context-expanded re-query for uncertain detections
   - ~$5-10
```

**Change to**:
```
3. **H10 (training pool size)**: Library quality assessment
   - Test libraries constructed from larger training pools
   - ~$5-10
```

---

### 6. Fix Budget Table - Strand 1 (Line 651)

**Current**:
```
| Phase 2a: Strand 1 (Verbosity × partial H5) | ~24,000 | ~$36 |
```

**Change to**:
```
| Phase 2a: Strand 1 (Verbosity × partial H5) | ~15,600 | ~$23 |
```

---

### 7. Fix Budget Table - H5 Confirmatory (Line 652)

**Current**:
```
| Phase 2b: H5 Confirmatory (full 3-level) | ~7,200 | ~$11 |
```

**Change to**:
```
| Phase 2b: H5 Confirmatory (full 3-level) | ~2,400 | ~$4 |
```

---

### 8. Fix Exploratory Note (Line 672)

**Current**:
```
- H2, H6, and H9 are now exploratory (moved from confirmatory)
```

**Change to**:
```
- H9 is exploratory; H2 and H6 remain confirmatory
```

---

### 9. Update Budget Totals

After fixing lines 651-652, recalculate:

**Flash Subtotal** should be approximately:
- Previous: ~$94-101
- Adjustment: -$13 (Strand 1) -$7 (H5 Confirmatory) = -$20
- New: ~$74-81

Update line 660:
```
| **Flash Subtotal** | **~42,500-47,300** | **~$74-81** |
```

And line 662 (Confirmatory Total):
```
| **Confirmatory Total** | **~43,900-48,900** | **~$179-201** |
```

And line 664 (Grand Total):
```
| **Grand Total** | **~50,900-60,900** | **~$219-261** |
```

And line 666 (Contingency):
```
**Contingency**: 20% buffer → **Budget ceiling: ~$313**
```

---

### 10. Update Changelog

Add v2.5 entry:

```
- v2.5: Consistency fixes with preregistration.md v4.2 — corrected H8 label (was H15); fixed H2/H6 status (confirmatory, not exploratory); corrected cell counts (Strand 1: 26, H5 Confirmatory: 4); fixed H10 description (training pool size, not fine-to-coarse); recalculated budget totals
```

---

## Verification Checklist

After applying fixes, verify:

- [ ] H8 appears consistently (not H15)
- [ ] H2 and H6 are listed as confirmatory
- [ ] H9 is listed as exploratory
- [ ] Strand 1 = 26 cells
- [ ] H5 Confirmatory = 4 cells
- [ ] H10 = training pool size
- [ ] Budget totals are internally consistent
- [ ] Version updated to 2.5
