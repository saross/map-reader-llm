# Prompts Appendix Corrections

**Target file**: `preregistration-appendix-prompts.md`
**Reference**: `preregistration.md` v4.2
**Date**: 2026-01-08

---

## Summary

The instruction files are now correct (8 files, no text-only hardneg variants). However, the **config files are missing H5=Images-only variants** required by the preregistration.

---

## Issue: H5=Images-only Configs Missing

### Preregistration Requirement

Preregistration Section 8.7.4 (line 1884) specifies:

> "3 image-using modalities × 3 H5 levels = 9"

The three H5 levels per preregistration lines 594-599:

| H5 Level | Exclusion Text | Hard Neg Images | Image Labels | Instruction File |
|----------|----------------|-----------------|--------------|------------------|
| None | No | No | — | `detect_{modality}.md` |
| Images-only | **No** | **Yes** | Minimal ("Negative") | `detect_{modality}.md` |
| Text+Images | Yes | Yes | Detailed | `detect_{modality}_hardneg.md` |

**Key point**: H5=Images-only uses the **same instruction file** as H5=None (no exclusion text), but a **different config** that includes hard negative images with minimal labels.

### Current State (Appendix)

Lines 798-809 list only 8 base configs:
- 3 image-using modalities × 2 H5 levels (None, Text+Images) = 6
- 2 text-only modalities × 1 H5 level (None only) = 2

**Missing**: 3 configs for H5=Images-only

### Required: Add 3 H5=Images-only Configs

Add these to Section 2.3 (Complete Configuration File List):

| Configuration File | M/E Level | H5 Level | Instruction File |
|--------------------|-----------|----------|------------------|
| `detect_image-only_images.json` | Image-only | Images-only | detect_image-only.md |
| `detect_brief-text-image_images.json` | Brief-text+image | Images-only | detect_brief-text-image.md |
| `detect_verbose-text-image_images.json` | Verbose-text+image | Images-only | detect_verbose-text-image.md |

---

## Required Changes

### 1. Update Line 31 (Config Count)

**Current**:
```
- **23 configuration files**: See Section 2.2 for breakdown
```

**Change to**:
```
- **26 configuration files**: See Section 2.2 for breakdown
```

---

### 2. Update Line 775-780 (Config Breakdown)

**Current**:
```
This yields:

- **8 base detection configs**: 5 M/E levels, but image-using have base + `_hardneg` variants
- **12 H4 ordering variants**: 3 image-using M/E levels × 2 orderings × 2 H5 levels
- **2 pipeline configs**: propose_image-only.json, verify_image-only.json
- **1 pilot config**: pilot_tilesize.json

**Total: 23 configuration files**
```

**Change to**:
```
This yields:

- **11 base detection configs**: 3 image-using M/E levels × 3 H5 levels + 2 text-only M/E levels × 1 H5 level
- **12 H4 ordering variants**: 3 image-using M/E levels × 2 orderings × 2 H5 levels (None and Text+Images only; Images-only uses canonical-first)
- **2 pipeline configs**: propose_image-only.json, verify_image-only.json
- **1 pilot config**: pilot_tilesize.json

**Total: 26 configuration files**
```

---

### 3. Update Lines 784-792 (Config Structure Table)

**Current**:
```markdown
| M/E Level | Base (canonical-first) | With hardneg | canonical-last | canonical-last + hardneg | random-order | random-order + hardneg |
|-----------|------------------------|--------------|----------------|-------------------------|--------------|------------------------|
| Image-only | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Brief-text | ✓ | — | — | — | — | — |
| Brief-text+image | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Verbose-text | ✓ | — | — | — | — | — |
| Verbose-text+image | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
```

**Change to**:
```markdown
| M/E Level | H5=None | H5=Images-only | H5=Text+Images | H4 variants |
|-----------|---------|----------------|----------------|-------------|
| Image-only | ✓ | ✓ | ✓ (`_hardneg`) | 4 (2 orderings × 2 H5) |
| Brief-text | ✓ | — | — | — |
| Brief-text+image | ✓ | ✓ | ✓ (`_hardneg`) | 4 (2 orderings × 2 H5) |
| Verbose-text | ✓ | — | — | — |
| Verbose-text+image | ✓ | ✓ | ✓ (`_hardneg`) | 4 (2 orderings × 2 H5) |

**Note**: H5=Images-only uses the same instruction file as H5=None but includes hard negative images with minimal "Negative" labels in the config.
```

---

### 4. Update Section 2.3 Base Detection Configs (Lines 798-809)

**Current** (8 files):
```markdown
#### Base Detection Configs (8 files)

| Configuration File | M/E Level | H5 Level | Instruction File |
|--------------------|-----------|----------|------------------|
| `detect_image-only.json` | Image-only | None | detect_image-only.md |
| `detect_image-only_hardneg.json` | Image-only | Text+Images | detect_image-only_hardneg.md |
| `detect_brief-text.json` | Brief-text | None | detect_brief-text.md |
| `detect_brief-text-image.json` | Brief-text+image | None | detect_brief-text-image.md |
| `detect_brief-text-image_hardneg.json` | Brief-text+image | Text+Images | detect_brief-text-image_hardneg.md |
| `detect_verbose-text.json` | Verbose-text | None | detect_verbose-text.md |
| `detect_verbose-text-image.json` | Verbose-text+image | None | detect_verbose-text-image.md |
| `detect_verbose-text-image_hardneg.json` | Verbose-text+image | Text+Images | detect_verbose-text-image_hardneg.md |
```

**Change to** (11 files):
```markdown
#### Base Detection Configs (11 files)

| Configuration File | M/E Level | H5 Level | Instruction File |
|--------------------|-----------|----------|------------------|
| `detect_image-only.json` | Image-only | None | detect_image-only.md |
| `detect_image-only_images.json` | Image-only | Images-only | detect_image-only.md |
| `detect_image-only_hardneg.json` | Image-only | Text+Images | detect_image-only_hardneg.md |
| `detect_brief-text.json` | Brief-text | None | detect_brief-text.md |
| `detect_brief-text-image.json` | Brief-text+image | None | detect_brief-text-image.md |
| `detect_brief-text-image_images.json` | Brief-text+image | Images-only | detect_brief-text-image.md |
| `detect_brief-text-image_hardneg.json` | Brief-text+image | Text+Images | detect_brief-text-image_hardneg.md |
| `detect_verbose-text.json` | Verbose-text | None | detect_verbose-text.md |
| `detect_verbose-text-image.json` | Verbose-text+image | None | detect_verbose-text-image.md |
| `detect_verbose-text-image_images.json` | Verbose-text+image | Images-only | detect_verbose-text-image.md |
| `detect_verbose-text-image_hardneg.json` | Verbose-text+image | Text+Images | detect_verbose-text-image_hardneg.md |

**Note**: H5=Images-only configs (`_images.json`) use the same instruction file as H5=None but include hard negative images with minimal "Negative" labels.
```

---

### 5. Add Example Config for H5=Images-only

Add new section after Section 2.5 (or wherever appropriate):

```markdown
### 2.X Example Configuration: Image-Only, Images-Only Hard Negatives

#### detect_image-only_images.json

**M/E**: Image-only | **H5**: Images-only

```json
{
    "version": "detect_image-only_images",
    "description": "Image-only with hard negative images (minimal labels). Tests H5=Images-only.",
    "hypothesis": "H5-B",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "examples/canonical_burial_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_settlement_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_triangulation_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_benchmark_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/null_tile_01.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_02.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_03.png", "label": "Negative", "category": "null"},
        {"path": "examples/hardneg_standalone_benchmark.png", "label": "Negative", "category": "hard_negative"},
        {"path": "examples/hardneg_standalone_triangulation.png", "label": "Negative", "category": "hard_negative"}
    ],
    "ordering_note": "Canonical-first ordering. Hard negatives included with minimal labels (no explanation)."
}
```

**Key difference from H5=Text+Images**: Hard negative images are present but use minimal "Negative" labels rather than detailed explanatory labels. The instruction file has NO exclusion guidance text.
```

---

### 6. Update Changelog

Add v2.6 entry:

```markdown
- v2.6: Added missing H5=Images-only configs — 3 new base configs (`_images.json` variants) for image-using modalities; updated config count from 23 to 26; clarified H5=Images-only uses same instruction file as H5=None but includes hard negative images with minimal labels; added example config for H5=Images-only
```

---

## Verification Checklist

After applying fixes:

- [ ] Config count updated to 26 (line 31)
- [ ] Base detection configs = 11 (not 8)
- [ ] H4 ordering variants = 12 (unchanged)
- [ ] Pipeline configs = 2 (unchanged)
- [ ] Pilot config = 1 (unchanged)
- [ ] H5=Images-only configs added for all 3 image-using modalities
- [ ] Example config for H5=Images-only included
- [ ] Note clarifies H5=Images-only uses same instruction file as H5=None
- [ ] Changelog updated to v2.6

---

## Summary

| Change | Location | Description |
|--------|----------|-------------|
| Config count | Line 31 | 23 → 26 |
| Config breakdown | Lines 775-780 | Update counts and add H5=Images-only note |
| Structure table | Lines 784-792 | Restructure to show H5 levels clearly |
| Base configs table | Lines 798-809 | Add 3 H5=Images-only configs |
| New section | After 2.5 | Example config for H5=Images-only |
| Changelog | End | Add v2.6 entry |

---

*Ready for implementation.*
