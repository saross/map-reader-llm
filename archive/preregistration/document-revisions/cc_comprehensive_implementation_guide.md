# Implementation Guide: Config Corrections and H5 Scope Finalization

**Date:** January 14, 2026  
**For:** CC (Implementation)  
**Status:** Ready for implementation  
**Priority:** Complete before data collection begins

---

## Executive Summary

**Three main issues resolved:**

1. ✅ Config file errors identified and corrected (17 files affected)
2. ✅ H5 experimental scope finalized (test at all 3 image-based M/E levels)
3. ✅ Cost estimates corrected (~$286 confirmatory, not $1,560)

**Action required:** Update config files, create missing instruction files, update preregistration

---

## Part 1: Config File Corrections

### Issue Summary

**What was wrong:** Config files had wrong hypothesis labels and wrong library size
- Base configs labeled "H4-A" → should be "H1"
- Configs had 11 examples → should be 17 examples (Scale-8)
- Some ordering notes had incorrect counts

**Why it matters:** Preregistration is the authoritative source. Line 1703 explicitly states: "H1 totals: 5 cells (tested at T=1.0, Scale-8 library, canonical-first ordering)"

**Scale-8 library = 17 examples:**
- Canon+ (4) + Canon- (2) + HP (4) + HN (4) + Nulls (3) = **17 total**

### Files Requiring Correction

**Group A: Base H1 configs (5 files) - Wrong hypothesis and library:**
1. `detect_image-only.json`
2. `detect_brief-text.json`
3. `detect_brief-text-image.json`
4. `detect_verbose-text.json`
5. `detect_verbose-text-image.json`

**Current (WRONG):**
```json
{
    "hypothesis": "H4-A",
    "examples": [...] // 11 examples
}
```

**Required (CORRECT):**
```json
{
    "hypothesis": "H1",
    "examples": [...] // 17 examples: Canon+(4) + Canon-(2) + HP(4) + HN(4) + null(3)
}
```

**Group B: H4 ordering configs (6 files) - Wrong library size:**
- `detect_image-only_canonical-last.json`
- `detect_brief-text-image_canonical-last.json`
- `detect_verbose-text-image_canonical-last.json`
- `detect_image-only_random-order.json`
- `detect_brief-text-image_random-order.json`
- `detect_verbose-text-image_random-order.json`

**Required:** Update from 11 to 17 examples (Scale-8)

**Group C: H4+H5 combined configs (6 files) - Counting errors:**
- `detect_*_canonical-last_verbose.json`
- `detect_*_random-order_verbose.json`

**Required:** Fix `ordering_note` to match actual array (17 examples, 4 HN not 3)

**Group D: All configs - Terminology updates:**
- Replace "H5=None" → "H5=Minimal" in ordering notes
- Update descriptions from "Text+Images hard negatives" → "Verbose negative guidance"

---

## Part 2: H5 Experimental Scope - FINALIZED

### Decision Confirmed

**Test H5 at all three image-based M/E levels** (not just at optimal from H1)

**Rationale:**
1. Directly tests whether optimal negative elaboration depends on positive elaboration (M/E × H5 interaction)
2. More generalizable results across M/E choices
3. Only moderate cost increase (+$36 for +3 cells)
4. More defensible to reviewers (no untested assumptions)

### Required Files: 11 Total

**Group 1: H1 Base Conditions (H5=Minimal - no exclusion text)**

| # | Filename | M/E Level | H5 Level | Library | Status |
|---|----------|-----------|----------|---------|--------|
| 1 | `detect_image-only.md` | Image-only | Minimal | Scale-8 (17) | **MISSING** - create |
| 2 | `detect_brief-text.md` | Brief-text | N/A | Scale-8 (17) | ✅ EXISTS |
| 3 | `detect_brief-text-image.md` | Brief+image | Minimal | Scale-8 (17) | ✅ EXISTS |
| 4 | `detect_verbose-text.md` | Verbose-text | N/A | Scale-8 (17) | **MISSING** - create |
| 5 | `detect_verbose-text-image.md` | Verbose+image | Minimal | Scale-8 (17) | ✅ EXISTS |

**Group 2: H5=Terse Variants (brief exclusion guidance - 1-2 sentences)**

| # | Filename | M/E Level | Exclusion Text | Status |
|---|----------|-----------|----------------|--------|
| 6 | `detect_image-only_terse.md` | Image-only | Brief (1-2 sentences) | **MISSING** - create |
| 7 | `detect_brief-text-image_terse.md` | Brief+image | Brief (1-2 sentences) | **MISSING** - create |
| 8 | `detect_verbose-text-image_terse.md` | Verbose+image | Brief (1-2 sentences) | **MISSING** - create |

**Group 3: H5=Verbose Variants (detailed exclusion guidance)**

| # | Filename | M/E Level | Exclusion Text | Status |
|---|----------|-----------|----------------|--------|
| 9 | `detect_image-only_verbose.md` | Image-only | Detailed section | **RENAME** from `_hardneg.md` |
| 10 | `detect_brief-text-image_verbose.md` | Brief+image | Detailed section | **RENAME** from `_hardneg.md` |
| 11 | `detect_verbose-text-image_verbose.md` | Verbose+image | Detailed section | **RENAME** from `_hardneg.md` |

**Note:** Text-only M/E levels (Brief-text, Verbose-text) have no H5 variants because they cannot show "Images-only" negative guidance.

### Naming Convention

- **No suffix** = H5=Minimal (base/H1 condition, no exclusion text)
- **`_terse` suffix** = H5=Terse (brief exclusion guidance)
- **`_verbose` suffix** = H5=Verbose (detailed exclusion guidance)

**OLD naming (incorrect):**
- `_hardneg` suffix was ambiguous

**NEW naming (correct):**
- `_terse.md` for brief exclusion text
- `_verbose.md` for detailed exclusion text

### Key Structural Rules

**1. Library composition (ALL files use Scale-8):**
```json
{
    "examples": [
        // Canon+ (4) - legend-derived positives
        {...}, {...}, {...}, {...},
        
        // Canon- (2) - legend-derived negatives
        {...}, {...},
        
        // HP (4) - empirical hard positives
        {...}, {...}, {...}, {...},
        
        // HN (4) - empirical hard negatives
        {...}, {...}, {...}, {...},
        
        // Nulls (3) - tiles with no mounds
        {...}, {...}, {...}
    ]
}
```

**2. Labels (ALL configs use minimal labels):**
- Positive examples: `"label": "Positive"`
- Negative examples: `"label": "Negative"`
- NO elaborated labels in JSON configs

**3. Text variation (controlled via instruction files only):**
- Positive guidance text: varies by M/E level (Image-only/Brief/Verbose)
- Negative guidance text: varies by H5 level (None/Terse/Verbose)
- Both controlled in .md instruction files, NOT in .json configs

**4. Consistency within M/E level:**

Positive guidance text must be identical across H5 levels for same M/E:
- `detect_image-only.md` base text = `detect_image-only_terse.md` = `detect_image-only_verbose.md`
- Only difference: presence/detail of exclusion guidance section

### Exclusion Text Templates

**Terse Template (1-2 sentences):**
```markdown
## Exclusion Guidance

Rays are key: Shapes without visible radiating rays are not mounds. Consider occlusion or degradation before excluding.

**DO NOT mark:**
- Standalone triangulation points (black triangle, NO rays)
- Standalone benchmarks (black square/circle, NO rays)
- Spot heights, bridge markers, or other simple dots
```

**Verbose Template (full section):**
Use the detailed "Exclusion Criteria (CRITICAL)" section from current `_hardneg.md` files with subsections for:
1. Spot Heights
2. Standalone Triangulation Points
3. Standalone Benchmarks
4. Quarry/Pit Symbols
5. Contour Line Artifacts
6. Infrastructure Markers

---

## Part 3: Corrected Cost Estimates

### Previous Calculation Error

**My original estimate:** $1,560 confirmatory (WRONG - off by 5×)  
**CC's report:** $250 for 23 cells (CORRECT)  
**Implied cost per cell:** $250 / 23 = ~$11 per cell

### Corrected Estimates

**Using ~$11 per cell:**

| Design Component | Cells | Calls (K=10, N=5) | Cost (~$11/cell) |
|-----------------|-------|-------------------|------------------|
| H1 (M/E) | 5 | 15,000 | ~$55 |
| H7 (Temperature) | 5 | 15,000 | ~$55 |
| H8 (Library) | 7 | 21,000 | ~$77 |
| **H5 (Negative text)** | **6*** | **18,000** | **~$66** |
| H4 (Ordering) | 3 | 9,000 | ~$33 |
| **Confirmatory total** | **26** | **78,000** | **~$286** |

*H5 tests 3 M/E × 3 H5 = 9 conditions, but 3 overlap with H1 → 6 net new cells

**With triggered exploratory:**

| Component | Cells | Cost |
|-----------|-------|------|
| Confirmatory | 26 | ~$286 |
| M/E-sensitivity (if H8 ≠ Scale-8) | 3 | ~$33 |
| H4b (if H4 significant) | 2 | ~$22 |
| HN-only (if HN >> HP) | 1 | ~$11 |
| **Maximum total** | **32** | **~$352** |

### Cost Comparison

| Version | Confirmatory Cells | Confirmatory Cost | Change |
|---------|-------------------|------------------|--------|
| Previous (H5 at one M/E) | 23 | ~$253 | Baseline |
| **Current (H5 at all M/E)** | **26** | **~$286** | **+$33 (+13%)** |
| Maximum with all triggers | 32 | ~$352 | +$99 (+39%) |

**Impact:** Only +$33 for substantially more robust experimental design. This is very reasonable.

---

## Part 4: Preregistration Updates Required

### Section 5.5: H5 Hypothesis

**Line 619 - Change:**

Current:
```markdown
- **M/E level**: Optimal from H1
```

Updated:
```markdown
- **M/E level**: All image-based conditions (Image-only, Brief-text+image, Verbose-text+image)
- **Rationale**: Tests whether optimal negative text level depends on positive elaboration (M/E × H5 interaction)
- **Text-only exclusion**: Brief-text and Verbose-text M/E levels cannot have "Images-only" negative guidance and serve only as H1 baselines
```

**After Line 625 - Add new subsection:**

```markdown
**M/E × H5 Interaction Analysis**:

Beyond the primary one-way ANOVA for each M/E level separately, exploratory analysis will examine whether optimal H5 level varies by M/E condition:

- **Two-way ANOVA**: M/E (3 levels) × H5 (3 levels) on precision and F1
- **Interaction test**: Does the H5 effect (Minimal → Terse → Verbose) differ across M/E levels?
- **Practical implication**: If interaction exists, optimal recommendations become conditional: "For M/E level X, use H5 level Y"

This addresses the theoretical concern that positive and negative guidance may have asymmetric elaboration requirements.
```

**Line 611-615 - Add fourth prediction:**

```markdown
4. **NEW:** The M/E × H5 interaction will be non-significant, indicating that optimal negative text level is consistent across positive elaboration levels
```

### Section 7.1: Confirmatory Summary Table

**Line 1142 - Update H5 row:**

Current:
```markdown
| H5 (negative text) | Terse helps, verbose diminishing returns | One-way ANOVA (3 levels) | Significant text treatment effect, recall stable |
```

Updated:
```markdown
| H5 (negative text) | Terse helps, verbose diminishing returns; effect consistent across M/E | Two-way ANOVA (3 M/E × 3 H5) | Significant H5 main effect, recall stable, M/E × H5 interaction non-significant |
```

### Section 8.3: Add New Subsection

**After Section 8.3.1, add:**

```markdown
#### 8.3.1a H5 × M/E Factorial Structure

H5 tests negative text elaboration at three image-based M/E levels, creating a 3×3 design:

| M/E Level | H5=Minimal | H5=Terse | H5=Verbose | Total |
|-----------|------------|----------|------------|-------|
| Image-only | ✓ (H1) | ✓ | ✓ | 3 |
| Brief-text+image | ✓ (H1) | ✓ | ✓ | 3 |
| Verbose-text+image | ✓ (H1) | ✓ | ✓ | 3 |
| **Total** | **3** | **3** | **3** | **9** |

**Overlap with H1:** The H5=Minimal column represents the same conditions as H1 baselines for these three M/E levels (all using Scale-8 library with no exclusion text).

**Instruction file count:** 11 total
- 5 base files for H1 (all 5 M/E levels at H5=Minimal)
- 3 H5=Terse variants (image-based M/E only)
- 3 H5=Verbose variants (image-based M/E only)

**Text-only M/E levels:** Brief-text and Verbose-text serve as academic baselines in H1 only. They cannot have H5 variants because "Images-only" negative guidance requires images to show.

**Orthogonality maintenance:** 
- M/E factor controls positive guidance elaboration (via instruction file text)
- H5 factor controls negative guidance elaboration (via exclusion text presence/detail)
- Both factors vary instruction files only; config files maintain minimal labels throughout
```

### Section 8.4.7: Budget Table

**Line 1769-1779 - Update:**

Current:
```markdown
| Component | Cells | Calls | Cost (~$3/cell) |
| --------- | ----- | ----- | --------------- |
| H1 (M/E) | 5 | 3,000 | ~$11 |
| H7 (Temperature) | 5 | 3,000 | ~$11 |
| H8 (Composition) | 7 | 4,200 | ~$21 |
| H5 (Negative Text) | 3 | 1,800 | ~$8 |
| H4 (Ordering) | 3 | 1,800 | ~$8 |
| **Confirmatory total** | **23** | **13,800** | **~$59** |
```

Updated:
```markdown
| Component | Cells | Calls | Cost (~$11/cell) |
| --------- | ----- | ----- | ---------------- |
| H1 (M/E) | 5 | 15,000 | ~$55 |
| H7 (Temperature) | 5 | 15,000 | ~$55 |
| H8 (Composition) | 7 | 21,000 | ~$77 |
| H5 (Negative Text) | 6* | 18,000 | ~$66 |
| H4 (Ordering) | 3 | 9,000 | ~$33 |
| **Confirmatory total** | **26** | **78,000** | **~$286** |
| M/E-sensitivity (triggered) | 3 | 9,000 | ~$33 |
| H4b (triggered) | 2 | 6,000 | ~$22 |
| HN-only (triggered) | 1 | 3,000 | ~$11 |
| **Maximum total** | **32** | **96,000** | **~$352** |

*H5 tests 3 M/E × 3 H5 = 9 conditions total, but 3 overlap with H1 baselines → 6 net new cells
```

### Execution Order Section

**Update execution order (around line 1632-1640):**

Current:
```markdown
4. **H5 fourth**: Tests text treatment for negatives at optimal library
```

Updated:
```markdown
4. **H5 fourth**: Tests negative text treatment at all image-based M/E levels × optimal library
   - Tests 3 M/E × 3 H5 = 9 conditions (but 3 overlap with H1)
   - Enables M/E × H5 interaction analysis
```

### Changelog Entry

Add to Section 15 (Changelog):

```markdown
- v4.5: H5 scope expansion and cost correction — H5 now tests at all three image-based M/E levels (Image-only, Brief-text+image, Verbose-text+image) rather than optimal M/E only; adds 6 net new cells enabling direct test of M/E × H5 interaction; cost estimates corrected to ~$11/cell based on actual Gemini 3 Flash pricing (~$286 confirmatory vs incorrect previous estimate); Section 5.5 updated (execution parameters, interaction analysis, predictions); Section 7.1 updated (H5 test type); Section 8.3.1a added (H5 × M/E factorial structure); Section 8.4.7 updated (execution order, budget table with corrected costs)
```

---

## Part 5: Implementation Checklist

### Immediate Actions (Before Data Collection)

**1. Fix config files (17 files):**
- [ ] Update 5 base H1 configs: `hypothesis="H1"`, 17 examples (Scale-8)
- [ ] Update 6 H4 ordering configs: 17 examples (Scale-8)
- [ ] Fix 6 H4+H5 combined configs: correct counts in `ordering_note`
- [ ] Update all descriptions to current terminology
- [ ] Remove/update old H5 terminology references

**2. Create missing instruction files (5 files):**
- [ ] Create `detect_image-only.md` (base, no exclusion text)
- [ ] Create `detect_verbose-text.md` (base, no exclusion text)
- [ ] Create `detect_image-only_terse.md` (brief exclusion guidance)
- [ ] Create `detect_brief-text-image_terse.md` (brief exclusion guidance)
- [ ] Create `detect_verbose-text-image_terse.md` (brief exclusion guidance)

**3. Rename existing files (3 files):**
- [ ] `detect_image-only_hardneg.md` → `detect_image-only_verbose.md`
- [ ] `detect_brief-text-image_hardneg.md` → `detect_brief-text-image_verbose.md`
- [ ] `detect_verbose-text-image_hardneg.md` → `detect_verbose-text-image_verbose.md`

**4. Verify structure:**
- [ ] All Scale-8 configs have Canon+(4) + Canon-(2) + HP(4) + HN(4) + null(3) = 17
- [ ] All configs use minimal labels ("Positive"/"Negative")
- [ ] Positive guidance text identical across H5 variants within each M/E
- [ ] Exclusion text present only in `_terse` and `_verbose` variants

**5. Create matching config files:**
- [ ] 11 detection configs (one per instruction file)
- [ ] Plus H4 ordering variants as needed
- [ ] Plus H8 library variants as needed

### Preregistration Updates

**6. Update sections:**
- [ ] Section 5.5: Line 619 + new interaction analysis subsection
- [ ] Section 7.1: H5 row updated to two-way ANOVA
- [ ] Section 8.3.1a: Add new factorial structure explanation
- [ ] Section 8.4.7: Budget table and execution order
- [ ] Section 15: Add changelog entry

**7. Review and validate:**
- [ ] Cross-check all cell counts and costs
- [ ] Verify no inconsistencies between sections
- [ ] Confirm alignment with actual implementation

### Before Registration

**8. Final checks:**
- [ ] All 11 instruction files committed to repository
- [ ] All configs validated against instruction files
- [ ] Library composition verified (Scale-8 = 17 examples)
- [ ] Cost estimates match actual pricing
- [ ] Preregistration ready for OSF upload

---

## Part 6: Quick Reference

### File Inventory

**Total required instruction files: 11**
- H1 base: 5 files (all M/E levels at H5=Minimal)
- H5 Terse: 3 files (image-based M/E only)
- H5 Verbose: 3 files (image-based M/E only)

**Total required config files: 11 minimum**
- Plus H4 ordering variants
- Plus H8 library variants

### Cell Count Summary

| Hypothesis | Cells | Overlaps | Net New |
|------------|-------|----------|---------|
| H1 | 5 | — | 5 |
| H7 | 5 | — | 5 |
| H8 | 7 | — | 7 |
| H5 | 9 | 3 (with H1) | 6 |
| H4 | 3 | — | 3 |
| **Total** | **29** | **3** | **26** |

### Cost Summary

- **Confirmatory:** 26 cells × $11/cell = **~$286**
- **With triggers:** Up to 32 cells = **~$352**
- **Change from previous:** +3 cells = **+$33** (+13%)

### Key Design Principles

1. **All configs use Scale-8 (17 examples)**
2. **All configs use minimal labels** ("Positive"/"Negative")
3. **Text variation controlled via instruction files only**
4. **Positive and negative guidance are orthogonal factors**
5. **M/E factor = positive elaboration**
6. **H5 factor = negative elaboration**

---

## Questions or Issues?

If any questions arise during implementation:

1. Check this document first
2. Verify against preregistration (authoritative source)
3. Flag inconsistencies to Shawn immediately
4. Do not proceed if uncertain - better to clarify than implement incorrectly

**Critical:** All changes must be complete before data collection begins. No modifications allowed after first API call on holdout tiles.
