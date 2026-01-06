# Correction: Verbose Text Content

**Purpose**: Correct an error in cc-factorial-restructure.md regarding verbose text content
**Date**: 2026-01-05
**Applies to**: cc-factorial-restructure.md, Part 1 and Part 7

---

## The Error

The restructure document incorrectly stated that verbose text should NOT include hard positive edge case guidance. This was an over-correction.

---

## Correct Definition

### What H2 (Verbosity) Controls

Detail level for describing **canonical symbols AND hard positive edge cases**.

| Level | Canonical Symbols | Hard Positive Edge Cases |
|-------|-------------------|--------------------------|
| Minimal | Task instruction only | None |
| Brief | Terse descriptions | Terse mention of types ("symbols may be occluded") |
| Verbose | Detailed descriptions | Detailed guidance on types AND variants |

### The Brief vs Verbose Distinction

- **Brief**: Describes types tersely, doesn't elaborate on variants
- **Verbose**: Describes types in detail, expands to cover specific variants as they are identified in the library

### Example

**Brief text** (hard positive guidance):
> Symbols may be partially obscured by roads, contours, or text. Include borderline cases.

**Verbose text** (hard positive guidance):
> Symbols are frequently intersected by other map features. Roads (black or red lines) may cross through a mound symbol. Contour lines (brown) at similar colour may partially merge with mound rays. Grid lines (blue) may overlay symbols. Text labels may obscure parts of symbols. In all cases, if you can see rays extending outward from a central point, even partially, mark the detection. Degraded or faded symbols from map scanning should also be included if the ray pattern is discernible.

**Same types** (occlusion, degradation). **Different detail level**.

---

## Orthogonality with H7

The separation between H2 and H7 is:

| Factor | Controls | Content |
|--------|----------|---------|
| H2 (Verbosity) | Detail level for **positives** | Canonical symbols + hard positive (FN) edge cases |
| H7 (Hard negatives) | Presence of **negative** guidance | Exclusion text + hard negative (FP) images |

This is orthogonal:
- Verbose text describes what TO detect (in detail)
- H7 exclusion text describes what NOT to detect
- These are independent dimensions

---

## Text-Library Relationship

**Text describes types; library provides instances.**

As the library grows (H15), the verbose text may expand to describe additional variant types if they represent distinct edge case patterns. But the text doesn't enumerate specific images — it provides conceptual guidance that the images exemplify.

**Example**:
- Library includes HP image: occluded mound crossed by road
- Verbose text describes the occlusion type, not the specific image

---

## Identical Text Across Modalities

This principle remains:
- Brief-text = Brief+image (same text file)
- Verbose-text = Verbose+image (same text file)

Text-only conditions receive the same guidance; they just lack visual examples to anchor it.

---

## Corrections to cc-factorial-restructure.md

### Part 1: Redefine H2 — Replace New Definition Table

**Find**:
```markdown
### New Definition

| Level | Content | Word Count |
|-------|---------|------------|
| Minimal | Task instruction only ("detect burial mound symbols") | ~50 words |
| Brief | Terse descriptions of all symbol types | ~200-300 words |
| Verbose | Detailed descriptions of all symbol types | ~500-700 words |

**Critical change**: All three levels describe the SAME content categories (canonical symbols). The difference is DETAIL LEVEL, not content coverage.
```

**Replace with**:
```markdown
### New Definition

| Level | Content | Word Count |
|-------|---------|------------|
| Minimal | Task instruction only ("detect burial mound symbols") | ~50 words |
| Brief | Terse descriptions of canonical symbols + terse HP edge case guidance | ~200-300 words |
| Verbose | Detailed descriptions of canonical symbols + detailed HP edge case guidance | ~500-700 words |

**Critical change**: All three levels describe the SAME content categories (canonical symbols + hard positive edge cases). The difference is DETAIL LEVEL, not content coverage.

**Verbose text expands with library**: As hard positive variants are identified and added to the library, verbose text expands to describe those variant types in detail. Brief text mentions the types tersely without elaborating on variants.
```

### Part 1: What Each Level Contains — Update Verbose

**Find**:
```markdown
**Verbose text**:
- Task framing
- Detailed description of each canonical type (size, colour, ray count, context, landscape position)
- Detection criteria (ray direction, colour analysis)
- Edge case guidance for canonical symbols (occlusion, degradation, clustering)
- Decision procedure
- Output format

**Note**: Verbose text does NOT include hard negative exclusion guidance — that remains controlled by H7.
```

**Replace with**:
```markdown
**Verbose text**:
- Task framing
- Detailed description of each canonical type (size, colour, ray count, context, landscape position)
- Detection criteria (ray direction, colour analysis)
- Detailed edge case guidance for hard positives:
  - Occluded mounds (roads, contours, grid lines, text crossing symbols)
  - Degraded/faded symbols (scanning artefacts, printing issues)
  - Clustered mounds (separating adjacent symbols)
  - Variant types as identified in library construction
- Decision procedure
- Output format

**Note**: Verbose text does NOT include hard negative exclusion guidance — that remains controlled by H7 via `_hardneg.md` instruction variants.
```

### Part 7: Instruction File Updates — Revise Content Clarification

**Find**:
```markdown
### Content Clarification

**Brief text** should contain:
- Terse descriptions of 4 canonical types
- Basic detection guidance
- ~200-300 words

**Verbose text** should contain:
- Detailed descriptions of 4 canonical types
- Detection criteria (ray direction, colour, count)
- Edge case guidance for **canonical symbols** (occlusion, degradation)
- Decision procedure
- ~500-700 words

**Neither brief nor verbose** should contain:
- Hard positive guidance (symbols that were missed) — this varies by library
- Hard negative exclusion guidance — this is controlled by H7 `_hardneg` variants
```

**Replace with**:
```markdown
### Content Clarification

**Brief text** should contain:
- Terse descriptions of 4 canonical types
- Terse HP edge case guidance (mentions types: occlusion, degradation)
- Basic detection guidance
- ~200-300 words

**Verbose text** should contain:
- Detailed descriptions of 4 canonical types
- Detection criteria (ray direction, colour, count)
- Detailed HP edge case guidance (occlusion types, degradation patterns, clustering)
- Expands to describe HP variant types as they are added to library
- Decision procedure
- ~500-700 words

**Text consistency across modalities**:
- Brief-text = Brief+image (same text file)
- Verbose-text = Verbose+image (same text file)

**Neither brief nor verbose** should contain:
- Hard negative exclusion guidance — this is controlled by H7 `_hardneg` variants
```

---

## Verification

After applying corrections:

- [ ] Verbose text includes HP edge case guidance (occlusion, degradation, clustering)
- [ ] Brief text mentions HP edge case types tersely
- [ ] Verbose expands with library to describe HP variant types
- [ ] H7 still controls exclusion guidance for hard negatives (unchanged)
- [ ] Identical text across text-only and text+image modalities (unchanged)
- [ ] Orthogonality is H2 (positives, detail level) vs H7 (negatives, presence)

---

*Correction prepared 2026-01-05*
