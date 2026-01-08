# Correction: Remove Redundant Minimal+image Level

**Purpose**: Correct M/E factor from 6 levels back to 5 levels
**Date**: 2026-01-05
**Applies to**: cc-factorial-restructure.md

---

## The Error

The restructure document added "Minimal+image" as a separate level from "Image-only". These are the same thing — Image-only already uses minimal text (task instruction + output format).

---

## Correct M/E Factor (5 Levels)

| Level | Text | Images | Purpose |
|-------|------|--------|---------|
| 1. Image-only | Minimal | Yes | Baseline: can model detect with images + minimal instruction? |
| 2. Brief+image | Brief | Yes | Does adding terse descriptions help? |
| 3. Verbose+image | Verbose | Yes | Does adding detailed descriptions help? |
| 4. Brief-text | Brief | No | Text-only baseline (academic) |
| 5. Verbose-text | Verbose | No | Text-only baseline (academic) |

**Image-only IS the minimal+image condition.** No separate level needed.

---

## Corrections to cc-factorial-restructure.md

### Part 2: Revised Modality/Elaboration Factor

**Find**:
```markdown
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
```

**Replace with**:
```markdown
### M/E Factor (5 levels)

| Level | Text | Images | Purpose |
|-------|------|--------|---------|
| 1. Image-only | Minimal | Yes | Baseline: can model detect with images + minimal instruction? |
| 2. Brief+image | Brief | Yes | Does adding terse descriptions help? |
| 3. Verbose+image | Verbose | Yes | Does adding detailed descriptions help? |
| 4. Brief-text | Brief | No | Text-only baseline (academic) |
| 5. Verbose-text | Verbose | No | Text-only baseline (academic) |

**Note**: Image-only already uses minimal text (task instruction + output format). This is the baseline for testing whether adding descriptive text (brief or verbose) improves performance.
```

### Part 3: Strand 1 Totals — Update Cell Count

**Find**:
```markdown
### Total Strand Costs

| Strand | Calls | Cost |
|--------|-------|------|
| 1: Verbosity | 18,000 | ~$27 |
```

This was based on 6 M/E levels. With 5 levels and partial H7 cross:

**Revised Strand 1 calculation**:
- (3 image M/E × 2 H7 × 5 T) + (2 text M/E × 2 H7 × 5 T) = 30 + 20 = **50 cells**
- 50 × K=10 × 60 tiles = **30,000 calls** (~$45)

### Part 8: Configuration File Updates — Update Config Count

**Find**:
```markdown
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
```

**Replace with**:
```markdown
### Config Count

| M/E Level | × H7 Levels | = Configs |
|-----------|-------------|-----------|
| Image-only | 4 | 4 |
| Brief+image | 4 | 4 |
| Verbose+image | 4 | 4 |
| Brief-text | 2 (None, Text-only) | 2 |
| Verbose-text | 2 (None, Text-only) | 2 |
| **Total** | | **16** |

This is the same config count as before the restructure.
```

### Remove References to Minimal+image Instruction Files

**Find and delete**:
```markdown
### New Instruction Files Needed

| Filename | M/E Level | H7 Variant |
|----------|-----------|------------|
| `detect_minimal.md` | Minimal+image | Base |
| `detect_minimal_hardneg.md` | Minimal+image | With exclusion |
```

No new instruction files needed — the existing 10 instruction files remain correct.

---

## Updated Strand 1 Design

### Strand 1 Structure (5 M/E × Partial H7 Cross)

**Image-Using Modalities (3 levels)**:

| M/E | H7=None | H7=Text+Images |
|-----|---------|----------------|
| Image-only | ✓ | ✓ |
| Brief+image | ✓ | ✓ |
| Verbose+image | ✓ | ✓ |

**Text-Only Modalities (2 levels)**:

| M/E | H7=None | H7=Text-only |
|-----|---------|--------------|
| Brief-text | ✓ | ✓ |
| Verbose-text | ✓ | ✓ |

**Strand 1 Totals**:
- (3 image M/E × 2 H7 × 5 T) + (2 text M/E × 2 H7 × 5 T) = 30 + 20 = **50 cells**
- 50 × K=10 × 60 tiles = **30,000 calls** (~$45)

---

## Also Update cc-h7-strand1-integration.md

**Find** (in Part 1):
```markdown
### Image-Using Modalities

| M/E Level | H7=None | H7=Text+Images |
|-----------|---------|----------------|
| Image-only | ✓ | ✓ |
| Minimal+image | ✓ | ✓ |
| Brief+image | ✓ | ✓ |
| Verbose+image | ✓ | ✓ |
```

**Replace with**:
```markdown
### Image-Using Modalities (3 levels)

| M/E Level | H7=None | H7=Text+Images |
|-----------|---------|----------------|
| Image-only | ✓ | ✓ |
| Brief+image | ✓ | ✓ |
| Verbose+image | ✓ | ✓ |
```

**Find** (in Part 1):
```markdown
### Strand 1 Totals

| Component | Cells |
|-----------|-------|
| Image M/E (4) × H7 (2) × T (5) | 40 |
| Text M/E (2) × H7 (2) × T (5) | 20 |
| **Total** | **60 cells** |

**API calls**: 60 × K=10 × 60 tiles = **36,000 calls** (~$54)
```

**Replace with**:
```markdown
### Strand 1 Totals

| Component | Cells |
|-----------|-------|
| Image M/E (3) × H7 (2) × T (5) | 30 |
| Text M/E (2) × H7 (2) × T (5) | 20 |
| **Total** | **50 cells** |

**API calls**: 50 × K=10 × 60 tiles = **30,000 calls** (~$45)
```

**Update Part 6 cost summary accordingly.**

---

## Revised Budget Impact

| Component | Previous | Corrected |
|-----------|----------|-----------|
| Strand 1 | 36,000 calls (~$54) | 30,000 calls (~$45) |
| Savings | — | 6,000 calls (~$9) |

---

## Verification

After applying corrections:

- [ ] M/E factor has 5 levels (not 6)
- [ ] No "Minimal+image" level exists
- [ ] No detect_minimal.md or detect_minimal_hardneg.md instruction files
- [ ] Config count is 16 (not 20)
- [ ] Strand 1 is 50 cells / 30,000 calls / ~$45
- [ ] Image-only described as using minimal text (task instruction + output format)

---

*Correction prepared 2026-01-05*
