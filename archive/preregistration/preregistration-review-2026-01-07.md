# Preregistration Review: v4.1

**Review Date**: 2026-01-07
**Document Reviewed**: preregistration.md v4.1
**Context**: Post-tile-size pilot, post-multiscale analysis

---

## Summary

The preregistration document is in good shape. Core methodology is correctly specified, and multi-scale pilot findings are accurately documented. The items below are refinements rather than corrections of fundamental errors.

| Category | Count |
|----------|-------|
| Correctly documented | 4 major items |
| Potential issues | 5 items |
| Omissions to consider | 3 items |

---

## ✅ Correctly Documented

### 1. Section 8.5 Voting Implementation (lines 1677-1727)

Region-level pooling with within-pass deduplication is correctly specified. The two-stage clustering approach is accurately described:

- Within-pass deduplication before cross-pass voting ✓
- 20m spatial tolerance matching F1 evaluation ✓
- Rationale for region-level vs tile-level pooling ✓

### 2. Section 12.2 Multi-Scale Fusion (lines 2000-2024)

Pilot results are accurately reported:

- F1=0.61 multi-scale vs F1=0.49 single-scale ✓
- Scale characteristics (256px: P=0.10, R=0.90; 1024px: P=0.28, R=0.37) ✓
- Error correlations (small-medium: r=−0.18; small-large: r=−0.09; medium-large: r=+0.13) ✓
- Disposition as exploratory for Paper 2 ✓
- Archived file references ✓

### 3. Tile Size Specification (Section 2.2, line 98)

512×512 with 64px overlap (448px stride) correctly documented.

### 4. Changelog (line 2142)

v4.1 updates correctly reflect:
- Region-level pooling methodology
- Multi-scale pilot results addition

---

## ⚠️ Potential Issues to Address

### 1. H2 Fine-to-Coarse: Pilot Provides Cautionary Data

**Location**: Lines 476-480

**Current text**:
> Stage 2: For each uncertain candidate, extract larger tile (~1024×1024) centred on candidate, re-query with verification prompt

**Issue**: H2 specifies Stage 2 uses ~1024×1024 tiles for context expansion, but the pilot found 1024px has only **37% recall** — most uncertain TPs would be missed by the context scale.

**Recommendation**: Add a note after the fine-to-coarse implementation:

```markdown
*Pilot note: Calibration testing found 1024px tiles achieve only 37% recall, 
limiting confirmation value. The fine-to-coarse test remains valid for 
confirming the prediction that two-stage won't help, but practitioners 
should note this constraint.*
```

**Rationale**: This doesn't change the hypothesis (we predict it won't help), but provides important context for interpretation.

---

### 2. H11 Tile Size: Could Reference Pilot Findings

**Location**: Lines 930-961

**Current text**:
> *Note: The original hypothesis tested larger tiles (1024×1024, 2048×2048). This has been revised based on literature suggesting VLM attention to small features degrades with larger tiles, making smaller tiles more promising.*

**Issue**: H11 proposes testing 384×384 as smaller alternative. The pilot tested 256px, which showed very high recall (0.90) but terrible precision (0.10). This is relevant context.

**Recommendation**: Expand the note:

```markdown
*Note: The original hypothesis tested larger tiles (1024×1024, 2048×2048). 
This has been revised based on literature suggesting VLM attention to small 
features degrades with larger tiles. Pilot testing at 256px confirmed high 
recall (0.90) but very low precision (0.10) at 2/5 threshold, suggesting 
smaller tiles may over-detect. The 384×384 test size balances improved 
symbol visibility with practical precision constraints.*
```

---

### 3. Section 12.2: Threshold Context Missing

**Location**: Lines 2012-2014

**Current text**:
> - Small tiles (256px): High recall (0.90) but low precision (0.10) — detects most mounds but generates many false positives

**Issue**: Scale characteristics cite precision/recall values without specifying the voting threshold. These are at 2/5 threshold.

**Recommendation**: Clarify:

```markdown
- Small tiles (256px): High recall (0.90) but low precision (0.10) at 2/5 
  voting threshold — detects most mounds but generates many false positives
```

---

### 4. Encoding Artifacts in Changelog

**Location**: Lines 2143-2159

**Issue**: Some changelog entries may show encoding artifacts (e.g., "×" displaying incorrectly) depending on editor/viewer. Worth checking the source file renders correctly in target environments (OSF, GitHub, PDF export).

**Action**: Verify rendering in intended publication formats.

---

### 5. Minor Precision in Multi-Scale Pilot Numbers

**Location**: Line 2014

**Current text**:
> Higher precision (0.28) but unacceptably low recall (0.37)

**Issue**: The pilot results show 1024px precision at 2/5 threshold is actually 0.284 (rounds to 0.28), but for consistency with other reported values, consider using 0.29 or stating "~0.28".

**Recommendation**: Minor — acceptable as-is, but could standardise rounding.

---

## 🔍 Omissions to Consider

### 1. Pilot Decision Rationale for 512px Not Cross-Referenced

**Location**: Section 2.2 (lines 94-98)

**Issue**: The detailed pilot decision (pilot_decision.md) explains why 512px was retained, but the preregistration doesn't explicitly state that tile size was validated by pilot testing.

**Recommendation**: Add to Section 2.2:

```markdown
| Tile size | 512×512 pixels (64px overlap, 448px stride) |

*Tile size validated by calibration pilot (2026-01-07) comparing 256px, 
512px, and 1024px. 512px retained as optimal precision-recall balance; 
see Section 12.2 for multi-scale analysis.*
```

---

### 2. No Reference to Archived Pilot Files in Section 8

**Issue**: Section 12.2 references archived pilot data files, but Section 8 (Implementation) doesn't mention the pilot outputs or their role in calibration.

**Recommendation**: Add new subsection after 8.7:

```markdown
### 8.8 Calibration Pilot Outputs

Tile size and voting methodology were calibrated via pilot studies before 
holdout evaluation. Archived outputs:

| File | Description |
|------|-------------|
| `outputs/pilot/pilot_results.json` | Single-scale results with bootstrap CIs |
| `outputs/pilot/pilot_summary.md` | Human-readable summary |
| `outputs/pilot/pilot_decision.md` | Decision rationale |
| `outputs/pilot/multiscale_analysis.json` | Multi-scale voting analysis |
| `outputs/pilot/multiscale_full_sweep.csv` | Full parameter sweep |

These files document calibration decisions made before holdout evaluation 
and are archived for reproducibility.
```

---

### 3. media_resolution=HIGH Not Documented for Large Tiles

**Location**: Section 8.2 (API Parameters)

**Issue**: The pilot required `media_resolution=HIGH` for 1024px tiles to prevent Gemini's internal tiling (which splits large images into 768px patches). If 1024px tiles are used in H2 (fine-to-coarse), this API parameter should be documented.

**Recommendation**: Add to Section 8.2:

```markdown
**Large tile handling (Gemini)**: For tiles ≥1024px, the Gemini API requires 
`media_resolution="HIGH"` to process the full image at native resolution. 
Without this parameter, Gemini internally tiles large images into 768×768 
patches, potentially losing spatial context at patch boundaries.
```

---

## Required Changes Summary

| Priority | Section | Change | Lines |
|----------|---------|--------|-------|
| Medium | H2 | Add pilot note about 1024px recall limitation | 480-481 |
| Low | H11 | Add pilot context about 256px precision issues | 947 |
| Low | 12.2 | Specify "at 2/5 threshold" for scale characteristics | 2012-2014 |
| Low | 2.2 | Add reference to pilot validation of 512px | 98 |
| Low | 8.2 | Document `media_resolution=HIGH` for large tiles | ~1550 |
| Low | 8.8 (new) | Add calibration pilot outputs reference | after 8.7 |

---

## Verification Checklist

Before final registration:

- [ ] Apply medium-priority change (H2 pilot note)
- [ ] Consider low-priority changes based on space/clarity tradeoffs
- [ ] Verify encoding renders correctly in OSF/GitHub
- [ ] Confirm all pilot output files exist at documented paths
- [ ] Update document version to 4.2 if changes made

---

*Review prepared by Claude, 2026-01-07*
