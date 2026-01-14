# Prompt for CC: Add Naming Convention Section to README

**Task:** Add the following section to the prompt library README to explain the file naming convention.

---

## Section to Add to README

### File Naming Convention

Instruction files follow the pattern: `detect_{M/E-level}_{H5-level}.md`

This naming reflects two **orthogonal experimental factors**:

1. **M/E level** (Modality/Elaboration) - controls **positive guidance** (what TO detect)
2. **H5 level** (Hard Negatives) - controls **negative guidance** (what NOT to detect)

#### M/E Levels (Positive Guidance)

| M/E Level | Filename Component | Description |
|-----------|-------------------|-------------|
| Image-only | `image-only` | Minimal text, visual examples only |
| Brief-text | `brief-text` | Concise text descriptions, no images |
| Brief-text+image | `brief-text-image` | Concise text + visual examples |
| Verbose-text | `verbose-text` | Detailed text descriptions, no images |
| Verbose-text+image | `verbose-text-image` | Detailed text + visual examples |

#### H5 Levels (Negative Guidance)

| H5 Level | Filename Suffix | Exclusion Text |
|----------|----------------|----------------|
| Minimal | *(no suffix)* | None - examples labeled "Negative" only |
| Terse | `_terse` | Brief (1-2 sentences) |
| Verbose | `_verbose` | Detailed (full section with subsections) |

#### Examples

| Filename | Positive Guidance | Negative Guidance | Interpretation |
|----------|-------------------|-------------------|----------------|
| `detect_image-only.md` | Minimal text, images | None | H1 baseline - image-only with no exclusion text |
| `detect_verbose-text-image.md` | Detailed text + images | None | H1 baseline - verbose positive, no exclusion text |
| `detect_verbose-text-image_terse.md` | Detailed text + images | Brief exclusion text | Verbose positive + terse negative |
| `detect_verbose-text-image_verbose.md` | Detailed text + images | Detailed exclusion text | Both positive and negative guidance are verbose |
| `detect_image-only_terse.md` | Minimal text, images | Brief exclusion text | Minimal positive + terse negative |

#### Key Points

- **Orthogonal factors:** Any M/E level can be combined with any H5 level
- **Text-only M/E levels** (brief-text, verbose-text) have no H5 variants because "images-only" negative guidance requires visual examples
- **All files use Scale-8 library** (17 examples: Canon+ 4, Canon- 2, HP 4, HN 4, null 3)
- **Config files (.json) always use minimal labels** ("Positive"/"Negative"); text elaboration controlled only in instruction files (.md)

#### Structural Consistency

Within each M/E level, positive guidance text is **identical** across all H5 variants. Only the exclusion guidance section varies:

- `detect_verbose-text-image.md` - NO exclusion section
- `detect_verbose-text-image_terse.md` - Same positive text + brief exclusion section
- `detect_verbose-text-image_verbose.md` - Same positive text + detailed exclusion section

This ensures that any performance differences between H5 levels can be attributed solely to the negative guidance, not to changes in positive guidance.

---

## Suggested Placement

Add this section after any existing "Overview" or "Introduction" section and before detailed file descriptions. If the README already has a table of contents, add an entry for "File Naming Convention".

## Additional Notes for CC

- Feel free to adjust formatting to match existing README style
- If there are conflicting naming conventions already documented, flag for Shawn's review
- Consider adding a visual diagram if it helps clarify the two-factor structure
