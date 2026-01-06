# Addendum: H7 Integration with Strand 1

**Purpose**: Specify how H7 (Hard Negatives) integrates with the Strand 1 verbosity testing
**Date**: 2026-01-05
**Applies to**: cc-factorial-restructure.md

---

## Decision Summary

**Approach**: Partial H7 cross in Strand 1 + Full H7 confirmatory test at optimal verbosity + Strengthened trigger

This balances:
- Detecting verbosity × H7 interactions
- Full decomposition of H7 mechanism (text vs images)
- Budget efficiency
- Insurance against missed interactions

---

## Part 1: Strand 1 Structure (Verbosity × Partial H7 Cross)

### Image-Using Modalities

| M/E Level | H7=None | H7=Text+Images |
|-----------|---------|----------------|
| Image-only | ✓ | ✓ |
| Minimal+image | ✓ | ✓ |
| Brief+image | ✓ | ✓ |
| Verbose+image | ✓ | ✓ |

**At H7=None**:
- Instruction file: `detect_{modality}.md` (no exclusion text)
- Library: Canonical (4) + Hard Positives (4) + Nulls (3) = **11 images**

**At H7=Text+Images**:
- Instruction file: `detect_{modality}_hardneg.md` (with exclusion text)
- Library: Canonical (4) + Hard Positives (4) + Hard Negatives (3, detailed labels) + Nulls (3) = **14 images**

### Text-Only Modalities

| M/E Level | H7=None | H7=Text-only |
|-----------|---------|--------------|
| Brief-text | ✓ | ✓ |
| Verbose-text | ✓ | ✓ |

**At H7=None**:
- Instruction file: `detect_{modality}.md` (no exclusion text)
- Library: None (text-only)

**At H7=Text-only**:
- Instruction file: `detect_{modality}_hardneg.md` (with exclusion text)
- Library: None (text-only)

**Note**: Text-only modalities cannot have H7=Images-only or H7=Text+Images since they have no example images.

### Strand 1 Totals

| Component | Cells |
|-----------|-------|
| Image M/E (4) × H7 (2) × T (5) | 40 |
| Text M/E (2) × H7 (2) × T (5) | 20 |
| **Total** | **60 cells** |

**API calls**: 60 × K=10 × 60 tiles = **36,000 calls** (~$54)

---

## Part 2: H7 Confirmatory Test (Full 2×2 Decomposition)

After Strand 1 identifies optimal M/E level, test all 4 H7 levels at that M/E:

| H7 Level | Exclusion Text | HN Images | Image Labels |
|----------|----------------|-----------|--------------|
| None | No | No | — |
| Text-only | Yes | No | — |
| Images-only | No | Yes | Minimal ("Negative") |
| Text+Images | Yes | Yes | Detailed (with explanation) |

### Library Composition by H7 Level

| H7 Level | Canonical | Hard Pos | Hard Neg | Nulls | Total |
|----------|-----------|----------|----------|-------|-------|
| None | 4 | 4 | 0 | 3 | 11 |
| Text-only | 4 | 4 | 0 | 3 | 11 |
| Images-only | 4 | 4 | 3 | 3 | 14 |
| Text+Images | 4 | 4 | 3 | 3 | 14 |

### H7 Confirmatory Totals

| Component | Cells |
|-----------|-------|
| M/E (1, optimal) × H7 (4) × T (5) | 20 |

**API calls**: 20 × K=10 × 60 tiles = **12,000 calls** (~$18)

### Analysis

- Primary: 2×2 ANOVA (Exclusion Text × HN Images) on precision
- Secondary: Same analysis on F1 and recall
- Test for interaction: Are text and images redundant or additive?

---

## Part 3: Strengthened Trigger for Expansion

### Trigger Conditions

Run H7 middle levels (Text-only, Images-only) at a **second M/E level** if EITHER:

1. **Interaction detected**: Strand 1 shows significant M/E × H7 interaction (p < 0.10), OR
2. **Large H7 effect**: H7 main effect (None vs Text+Images) exceeds 0.08 F1

### Rationale for Condition 2

A large H7 effect without detected interaction could still mask decomposition differences. If hard negatives matter a lot, it's worth checking whether the mechanism differs by verbosity.

### Expansion Design

If triggered, run at one additional M/E level (the most different from optimal that's still image-using):

| Optimal M/E | Expansion M/E |
|-------------|---------------|
| Verbose+image | Brief+image or Minimal+image |
| Brief+image | Verbose+image |
| Minimal+image | Verbose+image |
| Image-only | Brief+image |

**Expansion cells**: 1 M/E × 2 H7 (Text-only, Images-only) × 5 T = **10 cells**
**API calls**: 10 × K=10 × 60 tiles = **6,000 calls** (~$9)

---

## Part 4: What Gets Tested

| Question | Where Tested |
|----------|--------------|
| Does verbosity matter? | Strand 1 (Minimal → Brief → Verbose within image conditions) |
| Does adding text to images help/hurt? | Strand 1 (Image-only vs Minimal+image vs Brief/Verbose+image) |
| Do hard negatives help overall? | Strand 1 (H7=None vs H7=Text+Images, pooled across M/E) |
| Is there verbosity × H7 interaction? | Strand 1 (compare H7 effect across M/E levels) |
| Is H7 benefit from text, images, or both? | H7 Confirmatory (2×2 at optimal M/E) |
| Are text and images redundant or additive? | H7 Confirmatory (interaction term) |
| Does H7 decomposition differ by verbosity? | Expansion (if triggered) |

---

## Part 5: What Does NOT Get Tested (Accepted Gaps)

| Gap | Rationale for Accepting |
|-----|-------------------------|
| H7 middle levels at all verbosity levels | Covered at optimal; trigger catches important differences |
| 3-way interaction (Verbosity × H7-text × H7-images) | Unlikely to matter; Text+Images is safe default |
| Full H7 cross in text-only modalities | Logically constrained (can't have images in text-only) |

### Limitation to Document

> "H7 decomposition (text vs images) was tested at optimal verbosity only. If the decomposition differs at other verbosity levels, this would be detected only if the combined H7 effect showed interaction or was large (>0.08 F1). We accept this limitation because (1) deployment will use optimal verbosity, and (2) Text+Images is never worse than single-channel H7, only potentially suboptimal for token efficiency."

---

## Part 6: Cost Summary

| Component | Cells | Calls | Cost |
|-----------|-------|-------|------|
| Strand 1 (Verbosity × partial H7) | 60 | 36,000 | ~$54 |
| H7 Confirmatory (full 2×2) | 20 | 12,000 | ~$18 |
| **Base total** | **80** | **48,000** | **~$72** |
| Expansion (if triggered) | 10 | 6,000 | ~$9 |
| **Maximum total** | **90** | **54,000** | **~$81** |

---

## Part 7: Document Updates

### preregistration.md

**Section 5 (H7)**: Update to reflect:
- Partial cross in Strand 1 (None vs Text+Images)
- Full 2×2 at optimal M/E
- Strengthened trigger conditions

**Add to H7 specification**:

```markdown
**H7 Testing Structure**:

1. **Strand 1 (partial cross)**: H7=None vs H7=Text+Images tested across all M/E levels to detect overall H7 effect and M/E × H7 interaction

2. **H7 Confirmatory (full 2×2)**: All 4 H7 levels tested at optimal M/E to decompose the mechanism (exclusion text × hard negative images)

3. **Expansion trigger**: H7 middle levels (Text-only, Images-only) tested at a second M/E level if:
   - M/E × H7 interaction detected (p < 0.10), OR
   - H7 main effect > 0.08 F1
```

### execution-plan.md

Update Phase 2 structure to show:
- Strand 1 includes partial H7 cross (60 cells, not 30)
- H7 Confirmatory as distinct step after Strand 1 analysis
- Expansion trigger decision point

### preregistration-coverage.md

Update factorial matrix to show:
- Which M/E × H7 combinations are tested in Strand 1
- Which are tested in H7 Confirmatory
- Which are conditional on trigger

---

## Verification Checklist

After implementing:

- [ ] Strand 1 specified as 60 cells (6 M/E × 2 H7 × 5 T, with text-only H7 constraint)
- [ ] H7 Confirmatory specified as 20 cells (1 M/E × 4 H7 × 5 T)
- [ ] Expansion trigger documented (interaction p < 0.10 OR effect > 0.08)
- [ ] Expansion design specified (10 cells at second M/E)
- [ ] Library composition correct for each H7 level
- [ ] Label convention documented (minimal for Images-only, detailed for Text+Images)
- [ ] Accepted gaps documented as limitation
- [ ] Cost updated (~$72 base, ~$81 maximum for Strand 1 + H7)

---

*Addendum prepared 2026-01-05*
