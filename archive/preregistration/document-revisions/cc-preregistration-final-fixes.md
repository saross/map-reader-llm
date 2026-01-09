# Preregistration Final Review Fixes

**Purpose**: Correct errors, inconsistencies, and minor issues identified in final review
**Date**: 2026-01-04
**Document**: preregistration.md

---

## Priority: HIGH

### 1. H2/H7 Orthogonality — Exclusion Guidance Location

**Location**: Section 8.4.1 (around lines 1274-1291)

**Problem**: Current text states verbose text includes both exclusion guidance (for FPs) and edge case guidance (for FNs). But H7 should control exclusion guidance to keep H2 and H7 orthogonal.

**Find** (Step 4, around line 1274):
```markdown
**Step 4: Construct Verbose Text**

Build verbose text by adding targeted guidance for each hard example:

| Component | Source | Content |
|-----------|--------|---------|
| Base | Legend descriptions | Brief text describing canonical mound types |
| Exclusion guidance | Hard negative images | Text describing why each FP is NOT a mound |
| Edge case guidance | Hard positive images | Text describing why each FN IS a mound |

**Alignment requirement**: Each hard example image must have corresponding text guidance.
```

**Replace with**:
```markdown
**Step 4: Construct Verbose Text**

Build verbose text by adding edge case guidance for hard positives:

| Component | Source | Content |
|-----------|--------|---------|
| Base | Legend descriptions | Brief text describing canonical mound types |
| Edge case guidance | Hard positive images | Text describing why each FN IS a mound (e.g., partially occluded symbols, small variants) |

**Note on exclusion guidance**: Exclusion guidance for hard negatives (FPs) is NOT included in verbose text. Instead, it is controlled by the H7 factor:
- H7 Conditions A and C: No exclusion text
- H7 Conditions B and D: Exclusion text added via `_hardneg.md` instruction variants

This separation ensures H2 (elaboration) and H7 (hard negative guidance) remain orthogonal factors.

**Alignment requirement**: Each hard positive image must have corresponding edge case text in verbose prompts. Hard negative text alignment is controlled by H7.
```

**Also update Step 5** (around line 1286):

**Find**:
```markdown
**Step 5: Construct Brief vs Verbose Text**

| Text Version | Content |
|--------------|---------|
| Brief text | Legend-based descriptions only (~200-400 words) |
| Verbose text | Brief text + exclusion guidance + edge case guidance (~700-1400 words) |
```

**Replace with**:
```markdown
**Step 5: Construct Brief vs Verbose Text**

| Text Version | Content |
|--------------|---------|
| Brief text | Legend-based descriptions of canonical mound types only (~200-400 words) |
| Verbose text | Brief text + edge case guidance for hard positives (~400-700 words) |

**Note**: Exclusion guidance for hard negatives is added separately via H7 `_hardneg.md` variants, not via the brief/verbose distinction. This keeps H2 (elaboration) and H7 (hard negatives) as orthogonal factors.
```

---

### 2. Config Naming Pattern — Remove Temperature from Filenames

**Location**: Section 8.7.4 (around lines 1714-1724)

**Problem**: Temperature is a runtime parameter, not part of config files. Current text shows 100 config files; should be 20.

**Find**:
```markdown
**Config naming pattern**: `detect_{modality}_{elaboration}_{hardneg}_{temp}.json`

Example configurations:

| Config Pattern | M/E | H7 | T |
| :--- | :--- | :--- | :--- |
| `detect_image-only_none_t0.0.json` | Image-only | None | 0.0 |
| `detect_brief-text_text-only_t1.0.json` | Brief-text | Text-only | 1.0 |
| `detect_brief-text-image_images-only_t0.7.json` | Brief-text+image | Images-only | 0.7 |
| `detect_verbose-text-image_text-images_t1.3.json` | Verbose-text+image | Text+Images | 1.3 |
```

**Replace with**:
```markdown
**Config naming pattern**: `detect_{modality}_{hardneg}.json`

Temperature is specified at runtime, not in config files. This yields 20 config files (5 M/E × 4 H7).

Example configurations:

| Config Pattern | M/E | H7 |
| :--- | :--- | :--- |
| `detect_image-only_none.json` | Image-only | None |
| `detect_text-brief_hardneg-text.json` | Brief-text | Text-only |
| `detect_text-brief-image_hardneg-images.json` | Brief-text+image | Images-only |
| `detect_text-verbose-image_hardneg-both.json` | Verbose-text+image | Text+Images |

**Runtime parameters** (specified at execution, not in config files):
- Temperature: T ∈ {0.0, 0.3, 0.7, 1.0, 1.3}
- Model: gemini-3-flash, gemini-3-pro, claude-sonnet-4-5, etc.
- Number of passes (K): 10 for main factorial, varies for H4
```

---

## Priority: MEDIUM

### 3. H3 Testing Approach — Remove H4 from Factor List

**Location**: Line 464

**Problem**: H4 (consensus voting) is post-processing, not part of single-stage prompt configuration.

**Find**:
```markdown
**Testing approach**: The two-stage pipeline will be tested using the optimal single-stage configuration identified from H1, H2, H4, H5, H7, H9 (modality, text elaboration, consensus voting, ordering, hard negatives, temperature).
```

**Replace with**:
```markdown
**Testing approach**: The two-stage pipeline will be tested using the optimal single-stage configuration identified from H1, H2, H5, H7, H9 (modality, text elaboration, ordering, hard negatives, temperature). Consensus voting (H4) is applied as post-processing to both single-stage and two-stage outputs for fair comparison.
```

---

### 4. Temperature "Required" Statement

**Location**: Line 1072

**Problem**: Says T=1.0 is "required" but factorial tests lower values.

**Find**:
```markdown
- `temperature`: 1.0 (required; values <1.0 cause degraded performance)
```

**Replace with**:
```markdown
- `temperature`: 1.0 (vendor recommended; preliminary testing suggested lower values may degrade performance — tested explicitly in H9)
```

---

### 5. Section 8.3.3 — Incorrect Factor Reference

**Location**: Line 1221

**Problem**: References O (ordering) which is not in main factorial.

**Find**:
```markdown
1. Identify optimal base configuration from main factorial (M, O, H, T) and H2 (E)
```

**Replace with**:
```markdown
1. Identify optimal base configuration from main factorial (M/E, H7, T)
```

---

### 6. Section 8.3.4 — Missing Temperature Level

**Location**: Line 1231

**Problem**: Missing T=1.3.

**Find**:
```markdown
- **Temperature**: T ∈ {0.0, 0.3, 0.7, 1.0} as per factorial design (Section 8.4.6)
```

**Replace with**:
```markdown
- **Temperature**: T ∈ {0.0, 0.3, 0.7, 1.0, 1.3} as per factorial design (Section 8.4.7)
```

---

## Priority: LOW

### 7. Typos

**Line 32**:
- Find: "consise"
- Replace: "concise"

**Line 258**:
- Find: "The four mapss used"
- Replace: "The four maps used"

**Line 282**:
- Find: "due to sampling noise"
- Replace: "due to sampling noise."

---

### 8. Terminology: "Elaborate" → "Verbose" in Section 8.7.2

**Location**: Line 1680

**Find**:
```markdown
| H2 | `detect_*_elaborate*.json` variants | `detect_*_elaborate*.md` variants |
```

**Replace with**:
```markdown
| H2 | `detect_*_verbose*.json` variants | `detect_*_verbose*.md` variants |
```

---

### 9. H5 Condition Count Clarification

**Location**: Around line 533

**Find**:
```markdown
**Design**: 3 orderings × 3 M/E levels = 9 conditions, tested at optimal H7 and T from main factorial.
```

**Replace with**:
```markdown
**Design**: 3 orderings × 3 M/E levels = 9 total conditions. Since the main factorial uses canonical-first ordering throughout, this adds 6 new conditions (canonical-last and random orderings at each of 3 M/E levels) beyond what the factorial already tests. All H5 conditions tested at optimal H7 and T from main factorial.
```

---

### 10. H13 Missing Status Line

**Location**: After line 898 (end of H13 section, before the `---` separator)

**Add before the separator**:
```markdown

**Status**: Exploratory. Tests whether architectural diversity in ensembles provides benefits beyond single-model voting.
```

---

### 11. H1 Table — "Elaborate" in Description

**Location**: Lines 411-412

**Find**:
```markdown
| Verbose-text | Elaborate | No | Text-only with comprehensive descriptions |
| Verbose-text+image | Elaborate | Yes | Elaborate text combined with visual examples |
```

**Replace with**:
```markdown
| Verbose-text | Verbose | No | Text-only with comprehensive descriptions |
| Verbose-text+image | Verbose | Yes | Verbose text combined with visual examples |
```

---

### 12. Document Version Number

**Location**: Line 9

**Find**:
```markdown
**Document version**: 3.1
```

**Replace with**:
```markdown
**Document version**: 3.4
```

**Also update line 1882**:

**Find**:
```markdown
*Document version: 3.3*
```

**Replace with**:
```markdown
*Document version: 3.4*
```

**And add to changelog** (after line 1888):
```markdown
- v3.4: Final review fixes — H2/H7 orthogonality clarification (exclusion guidance controlled by H7 only); config naming corrected (temperature is runtime parameter); H3 factor list corrected; temperature "required" → "recommended"; Section 8.3.3/8.3.4 factor references fixed; typos corrected; terminology standardised (elaborate → verbose)
```

---

## Verification Checklist

After implementing all changes:

- [ ] Section 8.4.1 Step 4: Exclusion guidance NOT in verbose text
- [ ] Section 8.4.1 Step 5: Verbose text = brief + edge case guidance only
- [ ] Section 8.7.4: Config pattern has no temperature; 20 configs not 100
- [ ] Line 464: H4 removed from H3 factor list
- [ ] Line 1072: Temperature is "recommended" not "required"
- [ ] Line 1221: Factors are M/E, H7, T (no O)
- [ ] Line 1231: Temperature list includes T=1.3
- [ ] Line 1680: Uses "verbose" not "elaborate"
- [ ] Lines 411-412: Table uses "Verbose" not "Elaborate"
- [ ] Typos fixed (lines 32, 258, 282)
- [ ] H13 has Status line
- [ ] H5 clarifies 6 new conditions beyond factorial
- [ ] Version number updated to 3.4 in both locations
- [ ] Changelog updated

---

*Instructions prepared 2026-01-04*
