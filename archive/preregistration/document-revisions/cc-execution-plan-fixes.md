# Execution Plan Final Review Fixes

**Purpose**: Correct errors, inconsistencies, and outdated content identified in final review
**Date**: 2026-01-04
**Document**: execution-plan.md

---

## Priority: CRITICAL

### 1. Phase 1 Step 4 — H2/H7 Orthogonality Violation

**Location**: Lines 157-167

**Problem**: Shows verbose text including exclusion guidance, which violates the H2/H7 orthogonality fix. Exclusion guidance is controlled by H7, not by brief/verbose distinction.

**Find**:
```markdown
**Step 4: Construct Verbose Text**

Build verbose text by adding targeted guidance for each hard example:

| Component | Source | Content |
|-----------|--------|---------|
| Base | Legend descriptions | Brief text describing canonical mound types |
| Exclusion guidance | Hard negative images | Text describing why each FP is NOT a mound |
| Edge case guidance | Hard positive images | Text describing why each FN IS a mound |

**Alignment requirement**: Each hard example image must have corresponding text guidance. The verbose text directly describes the hard examples in the library.
```

**Replace with**:
```markdown
**Step 4: Construct Verbose Text**

Build verbose text by adding edge case guidance for hard positives:

| Component | Source | Content |
|-----------|--------|---------|
| Base | Legend descriptions | Brief text describing canonical mound types |
| Edge case guidance | Hard positive images | Text describing why each FN IS a mound (e.g., occluded symbols, degraded examples) |

**Note on exclusion guidance**: Text describing hard negatives (FPs) is NOT part of verbose text. Exclusion guidance is controlled by the H7 factor:
- H7 = None or Images-only: No exclusion text
- H7 = Text-only or Text+Images: Exclusion text added via `_hardneg.md` instruction variants

This separation ensures H2 (elaboration) and H7 (hard negatives) remain orthogonal factors.

**Alignment requirement**: Each hard positive image must have corresponding edge case text in verbose prompts.
```

---

### 2. Phase 1 Step 5 — Word Count Estimate

**Location**: Lines 169-175

**Problem**: Word count for verbose text is too high now that exclusion guidance is removed.

**Find**:
```markdown
**Step 5: Construct Brief vs Verbose Text**

| Text Version | Content |
|--------------|---------|
| Brief text | Legend-based descriptions of canonical mound types only (~200-400 words) |
| Verbose text | Brief text + exclusion guidance + edge case guidance (~700-1400 words) |
```

**Replace with**:
```markdown
**Step 5: Construct Brief vs Verbose Text**

| Text Version | Content |
|--------------|---------|
| Brief text | Legend-based descriptions of canonical mound types only (~200-400 words) |
| Verbose text | Brief text + edge case guidance for hard positives (~400-700 words) |

**Note**: Exclusion guidance for hard negatives is added separately via H7 `_hardneg.md` variants, not via the brief/verbose distinction.
```

---

### 3. Phase 4 Cost Estimate — Using Flash Pricing for Pro

**Location**: Lines 448-456

**Problem**: Estimates ~$21-24 for ~1,400-1,600 Pro calls. This uses Flash pricing (~$0.015/call). Pro is ~10× more expensive (~$0.075/call).

**Find**:
```markdown
### Total Phase 4 API Calls

| Sub-phase | API Calls | Est. Cost |
|-----------|-----------|-----------|
| 4a: Baseline | 200 | ~$3 |
| 4b: OFAT | ~1,200 | ~$18 |
| 4c: Voting | (from 4a-4b) | — |
| 4d: Refinement | 0-200 | $0-3 |
| **Total** | **~1,400-1,600** | **~$21-24** |

**Note**: If Pro shows dramatic superiority warranting full optimisation, budget for extended Pro testing (~$40-60 additional).
```

**Replace with**:
```markdown
### Total Phase 4 API Calls

| Sub-phase | API Calls | Est. Cost |
|-----------|-----------|-----------|
| 4a: Baseline | 200 | ~$15 |
| 4b: OFAT | ~1,200 | ~$90 |
| 4c: Voting | (from 4a-4b) | — |
| 4d: Refinement | 0-200 | $0-15 |
| **Total** | **~1,400-1,600** | **~$105-120** |

**Note**: Pro pricing is ~10× Flash (~$0.075/call vs ~$0.0015/call). If Pro shows dramatic superiority warranting full optimisation, budget for extended Pro testing (~$50-80 additional).
```

---

### 4. Budget Summary — Correct All Totals

**Location**: Lines 491-507

**Find**:
```markdown
## Budget Summary

| Phase | API Calls | Estimated Cost |
|-------|-----------|----------------|
| Phase 1: Library + Text | ~100 | $1-2 |
| Phase 2: Factorial (100 × K=10) | ~60,000 | ~$90 |
| Phase 3a: H4 N=30 Extension | ~1,200 | ~$2 |
| Phase 3b: H5 Ordering | ~3,600 | ~$5 |
| Phase 3c: H6 Diversity | ~6,000 | ~$9 |
| Phase 3d: H3 Two-Stage | ~1,200 | ~$2 |
| **Flash Subtotal** | **~72,100** | **~$109** |
| Phase 4: H8 Pro Transfer | ~1,400-1,600 | ~$21-24 |
| **Confirmatory Total** | **~73,500-73,700** | **~$130-133** |
| Phase 5: Exploratory | ~2,000-5,000 | ~$20-50 |
| **Grand Total** | **~75,500-78,700** | **~$150-183** |

**Contingency**: 20% buffer → **Budget ceiling: ~$220**

**Note**: This is significantly lower than the previous design (~$187-326) due to:

1. K=10 independent runs replace N=5 voting in factorial (same data, different framing)
2. H2 integrated into main factorial (no separate Phase 3d)
3. H8 uses OFAT on 20-tile subset rather than full replication
```

**Replace with**:
```markdown
## Budget Summary

| Phase | API Calls | Estimated Cost |
|-------|-----------|----------------|
| Phase 1: Library + Text | ~100 | $1-2 |
| Phase 2: Factorial (100 × K=10) | ~60,000 | ~$90 |
| Phase 3a: H4 N=30 Extension | ~1,200 | ~$2 |
| Phase 3b: H5 Ordering | ~3,600 | ~$5 |
| Phase 3c: H6 Diversity | ~6,000 | ~$9 |
| Phase 3d: H3 Two-Stage | ~1,200 | ~$2 |
| **Flash Subtotal** | **~72,100** | **~$109** |
| Phase 4: H8 Pro Transfer | ~1,400-1,600 | ~$105-120 |
| **Confirmatory Total** | **~73,500-73,700** | **~$214-229** |
| Phase 5: Exploratory | ~2,000-5,000 | ~$30-60 |
| **Grand Total** | **~75,500-78,700** | **~$244-289** |

**Contingency**: 20% buffer → **Budget ceiling: ~$350**

**Note**: The majority of cost comes from Pro model testing (Phase 4) at ~10× Flash pricing. Flash-only confirmatory testing would cost ~$109.
```

---

### 5. Phase 0 Checklist — Wrong File Names

**Location**: Lines 47-53

**Problem**: Uses old file naming that doesn't match the 10-instruction-file structure.

**Find**:
```markdown
- [x] **Prompts**: Finalise all instruction files (2026-01-01)
  - [x] `detect_image-only.md` (baseline, also used by hardneg configs)
  - [x] `detect_text-image.md` and `detect_text-image_hardneg.md`
  - [x] `detect_text-only.md` and `detect_text-only_hardneg.md`
  - [x] `detect_*_elaborate.md` and `detect_*_elaborate_hardneg.md` (H2)
  - [ ] H6 text variants (5 semantically equivalent instructions)
  - [x] `propose_image-only.md` and `verify_image-only.md` (H3)
```

**Replace with**:
```markdown
- [x] **Prompts**: Finalise all instruction files (2026-01-01)
  - [x] `detect_image-only.md` and `detect_image-only_hardneg.md`
  - [x] `detect_brief-text.md` and `detect_brief-text_hardneg.md`
  - [x] `detect_brief-text-image.md` and `detect_brief-text-image_hardneg.md`
  - [x] `detect_verbose-text.md` and `detect_verbose-text_hardneg.md`
  - [x] `detect_verbose-text-image.md` and `detect_verbose-text-image_hardneg.md`
  - [ ] H6 text variants (5 semantically equivalent instructions, constructed after Phase 2)
  - [x] `propose_image-only.md` and `verify_image-only.md` (H3)
```

---

## Priority: HIGH

### 6. H5 Condition Count — Internal Contradiction

**Location**: Line 320

**Problem**: Says "9 conditions total" but canonical-first is already in the main factorial.

**Find**:
```markdown
#### Design

Test 3 orderings × 3 M/E levels = 9 conditions total (partial cross):
```

**Replace with**:
```markdown
#### Design

Test 3 orderings × 3 M/E levels, but canonical-first is already in the main factorial. This adds **6 new conditions** (2 orderings × 3 M/E levels):
```

---

### 7. Output Directory Structure — Remove Stale H2 Directory

**Location**: Line 96

**Problem**: Shows `h2-elaboration/` directory, but H2 is integrated into the main factorial.

**Find**:
```markdown
├── phase3-followup/
│   ├── h4-voting/
│   ├── h6-diversity/
│   ├── h3-twostage/
│   │   ├── candidates.geojson        # Proposer output
│   │   ├── candidates.meta.json
│   │   ├── verified.geojson          # Verifier output
│   │   └── verified.meta.json
│   └── h2-elaboration/
```

**Replace with**:
```markdown
├── phase3-followup/
│   ├── h4-voting/
│   ├── h5-ordering/
│   ├── h6-diversity/
│   └── h3-twostage/
│       ├── candidates.geojson        # Proposer output
│       ├── candidates.meta.json
│       ├── verified.geojson          # Verifier output
│       └── verified.meta.json
```

---

### 8. Phase 5 H12 Description

**Location**: Lines 475-477

**Problem**: Incorrectly describes H12 as "replicating H4, H5, H7" rather than OFAT transfer testing.

**Find**:
```markdown
1. **H12 (cross-model consistency)**: Most important for generalisability
   - Replicate H4, H5, H7 on Claude 4.5 Sonnet and GPT-5.2
   - ~$30-50
```

**Replace with**:
```markdown
1. **H12 (cross-model consistency)**: Most important for generalisability
   - Test Flash-optimal configuration on Claude 4.5 Sonnet and GPT-5.2 Thinking
   - OFAT sensitivity testing per factor (same protocol as H8)
   - ~$40-60 (depends on provider pricing)
```

---

## Priority: MEDIUM

### 9. Config Naming in Checklist

**Location**: Lines 55-58

**Find**:
```markdown
- [x] **Configs**: Create all JSON config files (2026-01-01)
  - [x] H1/H5/H7 baseline and ordering variants (`detect_image-only*.json`, `detect_text-image*.json`)
  - [x] H2 elaboration variants (`detect_*_elaborate*.json`)
  - [ ] H9 temperature (runtime parameter, no separate configs needed)
  - [ ] H6 diversity configs
```

**Replace with**:
```markdown
- [x] **Configs**: Create all JSON config files (2026-01-01)
  - [x] 16 main factorial configs: 5 M/E × 4 H7 (minus 4 invalid text-only × image-H7 combos)
  - [x] Naming pattern: `detect_{modality}_{hardneg}.json`
  - [ ] H5 ordering variants (6 configs: 2 orderings × 3 M/E levels)
  - [ ] H9 temperature: runtime parameter, no separate configs needed
  - [ ] H6 diversity configs: constructed after Phase 2 optimal determined
```

---

### 10. Phase 3b — Add "at optimal H7 and T"

**Location**: After line 330

**Add after the API calls line**:
```markdown
**Fixed parameters**: All H5 conditions tested at optimal H7 and T from Phase 2 results.
```

---

### 11. Phase 2 — Add Config/Temperature Clarification

**Location**: After line 220 (after the 60,000 API calls line)

**Add**:
```markdown
**Implementation note**: The 100 conditions are implemented using 16 config files × 5 temperature values (runtime parameter). Text-only modalities (Brief-text, Verbose-text) only have 2 valid H7 levels each (None, Text-only), yielding 16 rather than 20 configs.
```

---

## Priority: LOW

### 12. Update Document Version and Changelog

**Location**: Lines 571-581

**Find**:
```markdown
*Document version: 2.1*
*Created: 2025-12-31*
*Updated: 2026-01-04*

**Changelog:**

- v2.1: Fixed stale E7 reference → H16 in dependency graph and Phase 5 priority list
```

**Replace with**:
```markdown
*Document version: 2.2*
*Created: 2025-12-31*
*Updated: 2026-01-04*

**Changelog:**

- v2.2: Final review fixes — H2/H7 orthogonality in Phase 1 (exclusion guidance controlled by H7 only); corrected Pro cost estimates (~$105-120, not ~$21-24); fixed budget summary totals; updated file naming to match 10-instruction structure; fixed H5 condition count (6 new, not 9); removed stale h2-elaboration directory; corrected H12 description
- v2.1: Fixed stale E7 reference → H16 in dependency graph and Phase 5 priority list
```

---

## Verification Checklist

After implementing all changes:

- [ ] Phase 1 Step 4: Exclusion guidance NOT in verbose text
- [ ] Phase 1 Step 5: Verbose text word count is ~400-700 (not ~700-1400)
- [ ] Phase 4 costs: ~$105-120 (not ~$21-24)
- [ ] Budget summary: Confirmatory total ~$214-229; Grand total ~$244-289
- [ ] Budget ceiling: ~$350 (not ~$220)
- [ ] Phase 0 file names: Use correct 10-instruction naming
- [ ] H5 condition count: "6 new conditions" (not "9 conditions total")
- [ ] Directory structure: No h2-elaboration/; has h5-ordering/
- [ ] H12 description: OFAT transfer testing (not "replicate H4, H5, H7")
- [ ] Config checklist: Describes 16-config structure
- [ ] Phase 3b: Notes "at optimal H7 and T"
- [ ] Phase 2: Notes config/temperature implementation
- [ ] Version updated to 2.2 with changelog

---

## Cross-Document Alignment Check

Ensure these values match across all documents:

| Item | Preregistration | Prompts Appendix | Execution Plan |
|------|-----------------|------------------|----------------|
| Config count | 16 | 16 | 16 |
| Instruction files | 10 (+2 H3) | 10 (+2 H3) | 10 (+2 H3) |
| Phase 1 passes | 5 | 5 | 5 |
| FP/FN threshold | ≥3/5 | ≥3/5 | ≥3/5 |
| Verbose text content | Edge case guidance only | Edge case guidance only | Edge case guidance only |
| H8 Pro cost | $126-170 | N/A | ~$105-120 |

**Note on H8 cost discrepancy**: Preregistration estimates 2,600-3,400 calls at Pro pricing. Execution plan estimates 1,400-1,600 calls. The execution plan uses a more streamlined OFAT approach. Either update preregistration to match, or note this as a refinement in execution plan.

---

*Instructions prepared 2026-01-04*
