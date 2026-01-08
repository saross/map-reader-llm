# Major Design Restructure: Separating Verbosity from Library Content

**Purpose**: Restructure factorial design to cleanly separate text elaboration (detail level) from library content (hard example count)
**Date**: 2026-01-05
**Affects**: preregistration.md, preregistration-appendix-prompts.md, preregistration-coverage.md, execution-plan.md

---

## Summary of Change

The original design conflated two questions:
- **Elaboration**: Does more detailed text description help?
- **Library content**: Does adding hard examples help?

Brief text contained only canonical symbol descriptions; verbose text added hard positive guidance. This meant we couldn't tell if verbose helped because of *detail* or because of *content*.

**New design**: Separate these into independent strands:
- **H2 (Verbosity)**: Tests detail level at fixed library content
- **H15 (Library Size)**: Tests hard example count at optimal verbosity

---

## Part 1: Redefine H2 (Text Elaboration)

### Old Definition

| Level | Content |
|-------|---------|
| Brief | Legend descriptions of canonical symbols only |
| Verbose | Brief + edge case guidance for hard positives |

### New Definition

| Level | Content | Word Count |
|-------|---------|------------|
| Minimal | Task instruction only ("detect burial mound symbols") | ~50 words |
| Brief | Terse descriptions of all symbol types | ~200-300 words |
| Verbose | Detailed descriptions of all symbol types | ~500-700 words |

**Critical change**: All three levels describe the SAME content categories (canonical symbols). The difference is DETAIL LEVEL, not content coverage.

### What Each Level Contains

**Minimal text**:
- Task framing ("Identify burial mound symbols")
- Output format specification (JSON schema)
- No symbol descriptions

**Brief text**:
- Task framing
- Terse description of each canonical type:
  - Burial mound: "Small circle with radiating rays (hachures; spikes). Orange-brown."
  - Settlement mound: "Larger, irregular shape with radiating rays. Orange-brown."
  - Triangulation on mound: "Black triangle surrounded by radiating rays."
  - Benchmark on mound: "Black square surrounded by radiating rays."
- Basic guidance: "Focus on the sunburst pattern."
- Output format

**Verbose text**:
- Task framing
- Detailed description of each canonical type (size, colour, ray count, context, landscape position)
- Detection criteria (ray direction, colour analysis)
- Edge case guidance for canonical symbols (occlusion, degradation, clustering)
- Decision procedure
- Output format

**Note**: Verbose text does NOT include hard negative exclusion guidance — that remains controlled by H7.

---

## Part 2: Revised Modality/Elaboration Factor

### Old M/E Factor (5 levels)

1. Image-only
2. Brief-text (text only)
3. Brief-text+image
4. Verbose-text (text only)
5. Verbose-text+image

### New M/E Factor (6 levels)

| Level | Text | Images | Purpose |
|-------|------|--------|---------|
| 1. Image-only | Minimal | Yes | Baseline: can model detect with images alone? |
| 2. Minimal+image | Minimal | Yes | Does adding any text to images help/hurt? |
| 3. Brief+image | Brief | Yes | Does terse text + images help? |
| 4. Verbose+image | Verbose | Yes | Does detailed text + images help? |
| 5. Brief-text | Brief | No | Text-only baseline (academic) |
| 6. Verbose-text | Verbose | No | Text-only baseline (academic) |

**Rationale for adding Minimal+image**: This isolates whether adding text to images helps at all, before asking how much detail helps.

---

## Part 3: Staged Experimental Design

### Strand 1: Verbosity Testing

**Purpose**: Determine optimal text detail level
**Library**: Fixed at Condition B (14 examples: 4 canonical + 4 HP + 3 HN + 3 null)
**H7**: Fixed at optimal from preliminary or run as partial cross

| Conditions | Description |
|------------|-------------|
| 6 M/E levels × 5 temperatures | Full verbosity × temperature cross |

**API calls**: 6 × 5 × K=10 × 60 tiles = **18,000 calls** (~$27 Flash)

**Outputs**:
- Optimal verbosity level for image conditions
- Whether text-only has any value
- Whether mixing text+image helps or hurts
- Temperature × verbosity interaction

### Strand 2: Library Size Testing

**Purpose**: Determine optimal hard example count
**Verbosity**: Fixed at optimal from Strand 1
**H7**: Fixed at Text+Images (D) to include both hard positive and hard negative content

| Condition | Positives | Hard Positives | Hard Negatives | Null Tiles | Total |
|-----------|-----------|----------------|----------------|------------|-------|
| A | 4 (canonical) | 2 | 2 | 3 | 11 |
| B | 4 (canonical) | 4 | 3 | 3 | 14 |
| C | 4 (canonical) | 8 | 6 | 3 | 21 |
| D | 4 (canonical) | 16 | 12 | 3 | 35 |

**API calls**: 4 × 5 × K=10 × 60 tiles = **12,000 calls** (~$18 Flash)

**Outputs**:
- Optimal library size
- Diminishing returns curve
- Cost-efficiency frontier (F1 per token)

### Strand 3: Interaction Check (Conditional)

**Trigger**: Run only if BOTH Strand 1 and Strand 2 show significant effects

**Purpose**: Check if optimal verbosity depends on library size

| Check | Condition |
|-------|-----------|
| 1 | Non-optimal verbosity × Library D (largest) |
| 2 | Non-optimal verbosity × Library A (smallest) |

**API calls**: 2 × 5 × K=10 × 60 tiles = **6,000 calls** (~$9 Flash)

**Decision rule**: If interaction detected (effect direction reverses or attenuates by >50%), document and expand testing. If no interaction, conclude factors are independent.

### Total Strand Costs

| Strand | Calls | Cost |
|--------|-------|------|
| 1: Verbosity | 18,000 | ~$27 |
| 2: Library Size | 12,000 | ~$18 |
| 3: Interaction | 6,000 | ~$9 |
| **Total** | **36,000** | **~$54** |

---

## Part 4: H7 Integration

H7 (Hard Negatives) still operates as a 2×2 factor on exclusion guidance:

| H7 Level | Exclusion Text | Hard Neg Images |
|----------|----------------|-----------------|
| None | No | No |
| Text-only | Yes | No |
| Images-only | No | Yes (minimal labels) |
| Text+Images | Yes | Yes (detailed labels) |

**Integration with strands**:

- **Strand 1**: Can run as partial H7 cross (e.g., None vs Text+Images) or fix H7 and test separately
- **Strand 2**: Uses H7=Text+Images to include full hard negative content in library
- **H7 main test**: Run at optimal verbosity and library size B

**Recommended approach**: 
1. Run Strand 1 at H7=Text+Images (assumes hard negatives help — test separately if needed)
2. Run H7 as confirmatory test at optimal verbosity before Strand 2

---

## Part 5: H6 Diversity and Example-Level Analysis

H6 (Diversity) enables example-level effectiveness analysis via regression.

**Dependency**: Requires variation in which examples appear across passes. Only works with resampled examples (H6 Conditions C and D), not fixed libraries.

**Design**:
- Run at optimal verbosity (from Strand 1)
- Use large library pool (Library C or D) to enable resampling
- Each pass samples subset of hard examples
- Variation enables regression: F1_pass ~ Σ βᵢ(exampleᵢ_present)

**Analysis outputs**:
- βᵢ for each example (marginal contribution to F1)
- High-impact examples identified (|βᵢ| > 0.02)
- Category-level effects (canonical vs hard positive vs hard negative)

**Sequencing**: H6 runs after Strand 1 and Strand 2, using optimal parameters from both.

---

## Part 6: Revised Hypothesis Structure

### Confirmatory Hypotheses

| Hypothesis | Question | Test |
|------------|----------|------|
| H1 | Does modality affect performance? | Compare across 6 M/E levels |
| H2 | Does text detail level affect performance? | Minimal vs Brief vs Verbose (within image conditions) |
| H4 | Does consensus voting improve F1? | Voting analysis from K=10 runs |
| H5 | Does example ordering affect performance? | Partial cross at optimal config |
| H7 | Do hard negatives improve precision? | 2×2 (text × images) at optimal verbosity |
| H9 | Does temperature affect performance? | 5 temperatures throughout |

### Exploratory Hypotheses

| Hypothesis | Question | Test |
|------------|----------|------|
| H3 | Does two-stage pipeline help? | Proposer-verifier at optimal config |
| H6 | Does diversity improve voting? | 2×2 (text × image diversity) |
| H8 | Do Flash optimisations transfer to Pro? | OFAT at optimal config |
| H10-H14 | Various | As previously specified |
| H15 | What is optimal library size? | **Strand 2** (4 library sizes) |
| H16 | What is optimal tile size? | As previously specified |

**Note**: H15 (Library Size) moves from low-priority exploratory to **core Strand 2** of the main design.

---

## Part 7: Instruction File Updates

### New Instruction Files Needed

| Filename | M/E Level | H7 Variant |
|----------|-----------|------------|
| `detect_minimal.md` | Minimal+image | Base |
| `detect_minimal_hardneg.md` | Minimal+image | With exclusion |

### Revised Instruction Files

| Filename | Change Required |
|----------|-----------------|
| `detect_brief-text.md` | Ensure describes canonical symbols only (no hard positive edge cases) |
| `detect_brief-text-image.md` | Same content as brief-text |
| `detect_verbose-text.md` | Detailed canonical descriptions + edge case guidance for canonicals (NOT hard positives) |
| `detect_verbose-text-image.md` | Same content as verbose-text |

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

---

## Part 8: Configuration File Updates

### New Config Count

| M/E Level | × H7 Levels | = Configs |
|-----------|-------------|-----------|
| Image-only | 4 | 4 |
| Minimal+image | 4 | 4 |
| Brief+image | 4 | 4 |
| Verbose+image | 4 | 4 |
| Brief-text | 2 (None, Text-only) | 2 |
| Verbose-text | 2 (None, Text-only) | 2 |
| **Total** | | **20** |

### New Config Files Needed

- `detect_minimal_none.json`
- `detect_minimal_text.json`
- `detect_minimal_images.json`
- `detect_minimal_both.json`

---

## Part 9: Budget Impact

### Revised Budget Summary

| Component | Calls | Cost |
|-----------|-------|------|
| Strand 1: Verbosity (6 M/E × 5 T × H7 partial) | ~18,000-27,000 | ~$27-40 |
| H7 Confirmatory (at optimal verbosity) | ~12,000 | ~$18 |
| Strand 2: Library Size (4 sizes × 5 T) | ~12,000 | ~$18 |
| Strand 3: Interaction (conditional) | ~6,000 | ~$9 |
| H4 N=30 Extension | ~1,200 | ~$2 |
| H5 Ordering | ~3,600 | ~$5 |
| H6 Diversity | ~6,000 | ~$9 |
| H3 Two-Stage | ~1,200 | ~$2 |
| **Flash Subtotal** | **~60,000-69,000** | **~$90-103** |
| H8 Pro Transfer | ~1,400-1,600 | ~$105-120 |
| **Confirmatory Total** | | **~$195-223** |
| Exploratory (H10-H14, H16) | ~5,000 | ~$30-50 |
| **Grand Total** | | **~$225-273** |
| **Contingency (20%)** | | **~$330** |

---

## Part 10: Document-Specific Updates

### preregistration.md

1. **Section 1.3**: Update "Role of text-only conditions" — already fixed
2. **Section 5 (H2)**: Rewrite to define verbosity as detail level, not content
3. **Section 8.3**: Update prompt variant descriptions
4. **Section 8.4.1**: Remove "Construct Verbose Text" step that adds hard positive guidance
5. **Section 8.4.7**: Revise factorial design to show stranded approach
6. **Add new section**: Strand 1/2/3 experimental structure
7. **Update H15**: Elevate from exploratory to Strand 2 core

### preregistration-appendix-prompts.md

1. **Section 1.0**: Add Minimal+image instruction files
2. **Section 1.2-1.5**: Revise brief/verbose content descriptions
3. **Part 2**: Add minimal config files
4. **Update config count**: 16 → 20

### execution-plan.md

1. **Phase 2**: Restructure as Strand 1 (verbosity) + H7 test
2. **Add Phase 2b**: Strand 2 (library size)
3. **Add Phase 2c**: Strand 3 (interaction check, conditional)
4. **Update budget summary**
5. **Update dependency graph**

### preregistration-coverage.md

1. Update factorial matrix to show stranded design
2. Document what's tested together vs sequentially
3. Update exclusion rationale if any combinations are now excluded

---

## Verification Checklist

After implementing all changes:

- [ ] H2 defined as detail level (Minimal → Brief → Verbose), not content
- [ ] All verbosity levels describe same content categories (canonical symbols)
- [ ] Hard positive edge case guidance removed from verbose text definition
- [ ] Minimal+image level added (6 M/E levels total)
- [ ] Strand 1/2/3 structure documented
- [ ] H15 elevated to Strand 2 core design
- [ ] H6 dependency on resampling noted for example-level analysis
- [ ] New instruction files specified (detect_minimal.md, detect_minimal_hardneg.md)
- [ ] New config files specified (4 minimal configs)
- [ ] Config count updated (20 total)
- [ ] Budget updated (~$225-273 confirmatory)
- [ ] All documents aligned on new structure

---

*Instructions prepared 2026-01-05*
