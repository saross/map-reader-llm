# Preregistration CC Instructions — Addendum

**Purpose**: Align config naming pattern with prompts appendix
**Date**: 2026-01-04
**Applies to**: cc-preregistration-final-fixes.md, Section 2

---

## Config Naming Alignment

The original preregistration fix (Section 2) used naming that differs from the prompts appendix. This addendum corrects the alignment.

### Update Section 2 Examples

**Find** (in cc-preregistration-final-fixes.md, the replacement text for Section 8.7.4):

```markdown
Example configurations:

| Config Pattern | M/E | H7 |
| :--- | :--- | :--- |
| `detect_image-only_none.json` | Image-only | None |
| `detect_text-brief_hardneg-text.json` | Brief-text | Text-only |
| `detect_text-brief-image_hardneg-images.json` | Brief-text+image | Images-only |
| `detect_text-verbose-image_hardneg-both.json` | Verbose-text+image | Text+Images |
```

**Replace with**:

```markdown
Example configurations:

| Config Pattern | M/E | H7 |
| :--- | :--- | :--- |
| `detect_image-only_none.json` | Image-only | None |
| `detect_brief-text_text.json` | Brief-text | Text-only |
| `detect_brief-text-image_images.json` | Brief-text+image | Images-only |
| `detect_verbose-text-image_both.json` | Verbose-text+image | Text+Images |
```

### Naming Convention Summary

Both preregistration.md and preregistration-appendix-prompts.md should use:

**Pattern**: `detect_{modality}_{hardneg}.json`

| Component | Values |
|-----------|--------|
| `{modality}` | `image-only`, `brief-text`, `brief-text-image`, `verbose-text`, `verbose-text-image` |
| `{hardneg}` | `none`, `text`, `images`, `both` |

### Also Update Config Count

The preregistration fix stated "20 config files" but should be "16" given text-only constraints.

**Find** (in the replacement text):
```markdown
Temperature is specified at runtime, not in config files. This yields 20 config files (5 M/E × 4 H7).
```

**Replace with**:
```markdown
Temperature is specified at runtime, not in config files. This yields 16 config files (see note below).

**Config count**: Text-only modalities (Brief-text, Verbose-text) cannot use H7=Images-only or H7=Both:
- 3 image-using modalities × 4 H7 levels = 12
- 2 text-only modalities × 2 H7 levels = 4
- **Total: 16 configurations**
```

---

*Addendum prepared 2026-01-04*
