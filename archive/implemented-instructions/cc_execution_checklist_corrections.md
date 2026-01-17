# Execution Checklist Corrections

**Document:** `execution-checklist.md`  
**Issue:** Execution Log section uses outdated "stranded factorial" terminology  
**Required:** Update to sequential OFAT design (matches preregistration v4.6)

---

## Corrections Needed

### Section: Execution Log (Lines 80-92)

**Current (INCORRECT):**
```markdown
| Phase | Start Date | End Date | Notes |
|-------|------------|----------|-------|
| Phase 1: Library + Text | | | |
| Phase 2a: Strand 1 | | | |
| Phase 2b: H5 Confirmatory | | | |
| Phase 2c: Strand 2 | | | |
| Phase 2d: Strand 3 (if triggered) | | | |
| Phase 3a: H3 N=30 Extension | | | |
| Phase 3b: H4 Ordering | | | |
| Phase 3c: H9 Diversity | | | |
| Phase 3d: H2 Two-Stage | | | |
| Phase 4: H6 Pro Transfer | | | |
| Phase 5: Exploratory | | | |
```

**Corrected (SEQUENTIAL OFAT):**
```markdown
| Phase | Start Date | End Date | Notes |
|-------|------------|----------|-------|
| Phase 1: Library + Text | | | |
| Phase 2a: H1 M/E Level | | | |
| Phase 2b: H7 Temperature | | | |
| Phase 2c: H8 Library Composition | | | |
| Phase 2d: H5 Negative Text | | | |
| Phase 2e: H4 Ordering | | | |
| Phase 3a: H3 N=30 Extension | | | |
| Phase 3b: H9 Diversity | | | |
| Phase 3c: H2 Two-Stage | | | |
| Phase 3d: Triggered Exploratory (H4b, M/E-sensitivity, HN-only) | | | |
| Phase 4: H6 Pro Transfer | | | |
| Phase 5: Exploratory (H10-H15) | | | |
```

---

## Explanation of Changes

### Phase 2 (Main Sequential Design)

**Old terminology:** "Strand 1", "Strand 2", "Strand 3"  
**New terminology:** Sequential OFAT with explicit hypothesis names

**Correct sequence:**
1. **Phase 2a: H1** — Test 5 M/E levels → determine optimal
2. **Phase 2b: H7** — Test 5 temperatures at optimal M/E → determine optimal T
3. **Phase 2c: H8** — Test 7 library compositions at optimal M/E + T → determine optimal library
4. **Phase 2d: H5** — Test 3 M/E × 3 H5 negative text at optimal T + library → determine optimal negative text
5. **Phase 2e: H4** — Test 3 orderings at optimal M/E + T + library + H5 → determine optimal ordering

**Rationale:** Sequential OFAT design replaced stranded factorial in preregistration v4.5/v4.6.

### Phase 3 (Exploratory Tests)

**Phase 3a:** H3 N=30 Extension ✅ (no change)  
**Phase 3b:** Changed from "H4 Ordering" to "H9 Diversity"
- H4 moved to Phase 2e (confirmatory)
- H9 is exploratory, tested after optimal config determined

**Phase 3c:** H2 Two-Stage ✅ (no change)

**Phase 3d:** Added "Triggered Exploratory" to capture:
- H4b: HP/HN ordering (if H4 significant)
- M/E-sensitivity: Test M/E at H8-optimal library (if H8 ≠ Scale-8)
- HN-only: Hard negatives only condition (exploratory)

### Phase 4-5

No changes needed - already correct.

---

## Summary of Phase Structure

| Phase | Type | Hypotheses | Cells |
|-------|------|------------|-------|
| Phase 1 | Preparation | — | 0 |
| Phase 2a | Confirmatory | H1 (M/E) | 5 |
| Phase 2b | Confirmatory | H7 (Temperature) | 5 |
| Phase 2c | Confirmatory | H8 (Library) | 7 |
| Phase 2d | Confirmatory | H5 (Negative Text) | 6 |
| Phase 2e | Confirmatory | H4 (Ordering) | 3 |
| **Phase 2 Total** | | | **26** |
| Phase 3a | Exploratory | H3 (Voting N=30) | — |
| Phase 3b | Exploratory | H9 (Diversity) | — |
| Phase 3c | Exploratory | H2 (Two-Stage) | — |
| Phase 3d | Triggered | H4b, M/E-sens, HN-only | 2-6 |
| Phase 4 | Exploratory | H6 (Pro Transfer) | — |
| Phase 5 | Exploratory | H10-H15 | — |

---

## Cross-Reference

This structure matches:
- **preregistration.md** Section 8.4.7 (Sequential Design)
- **execution-plan.md** Section "Phase 2: Sequential Hypothesis Testing"
- **preregistration-coverage.md** Section 3.1 (Sequential OFAT Design)

All three documents describe the same 26-cell sequential OFAT design with identical phase names.

---

## Implementation for CC

Replace lines 80-92 in `execution-checklist.md` with the corrected table shown above.

**Verification:** After making this change, ensure the phase names match execution-plan.md exactly.
