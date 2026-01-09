# Prompt Library Alignment Plan

**Created**: 2026-01-08
**Purpose**: Align actual `prompts/` directory with preregistration specifications
**For review by**: Opus

---

## Executive Summary

The current prompt library uses **legacy naming conventions** that differ from the preregistration document. The content is largely aligned, but file names and some structural details need updating.

**Key changes required:**
1. Rename 8 instruction files to match preregistration naming
2. Create 1 missing instruction file (`detect_image-only_hardneg.md`)
3. Delete 2 redundant files
4. Update all config files to reference new names
5. Minor content standardisation

---

## Part 1: Naming Convention Changes

### Current vs Preregistration Naming

| Current File | Preregistration Name | Status |
|--------------|---------------------|--------|
| `detect_image-only.md` | `detect_image-only.md` | ✅ Matches |
| — | `detect_image-only_hardneg.md` | ❌ **Missing** |
| `detect_text-only.md` | `detect_brief-text.md` | 🔄 Rename |
| `detect_text-only_hardneg.md` | `detect_brief-text_hardneg.md` | 🔄 Rename |
| `detect_brief-text-image.md` | `detect_brief-text-image.md` | ✅ Matches |
| `detect_text-image.md` | — | 🗑️ Delete (duplicate) |
| `detect_text-image_hardneg.md` | `detect_brief-text-image_hardneg.md` | 🔄 Rename |
| `detect_text-only_elaborate.md` | `detect_verbose-text.md` | 🔄 Rename |
| `detect_text-only_elaborate_hardneg.md` | `detect_verbose-text_hardneg.md` | 🔄 Rename |
| `detect_text-image_elaborate.md` | `detect_verbose-text-image.md` | 🔄 Rename |
| `detect_text-image_elaborate_hardneg.md` | `detect_verbose-text-image_hardneg.md` | 🔄 Rename |
| `propose_image-only.md` | `propose_image-only.md` | ✅ Matches |
| `verify_image-only.md` | `verify_image-only.md` | ✅ Matches |

### Rationale for New Naming

The preregistration uses a clearer naming convention:

```text
detect_{modality}[_hardneg].md

Modalities:
- image-only         (no text instructions)
- brief-text         (text only, concise)
- brief-text-image   (text + images, concise)
- verbose-text       (text only, detailed)
- verbose-text-image (text + images, detailed)

Suffix:
- _hardneg           (includes exclusion guidance for H5)
```

This replaces the old `_elaborate` suffix with explicit `verbose-` prefix, making the M/E factor levels clear.

---

## Part 2: Content Alignment

### 2.1 File to Create: `detect_image-only_hardneg.md`

**Source**: Preregistration appendix Section 1.1.2

```markdown
# Mound Detection (Image-Only)

Scan the Target Image. Mark all symbols that look like the Positive examples.

## Exclusion Guidance

The key diagnostic feature is **radiating rays** (hachures; spikes) extending OUTWARD from a central shape.

**DO NOT mark symbols without visible rays**, including:

- Standalone triangulation points (black triangle, NO rays)
- Standalone benchmarks (black square/circle, NO rays)
- Spot heights (simple dots with elevation numbers)
- Bridge/culvert markers (dots on roads/rivers)

Consider occlusion or degradation before excluding — partial rays still indicate a mound.

## Output Format

Return JSON with normalised coordinates (0-1000):

{
    "detections": [
        {
            "box_2d": [ymin, xmin, ymax, xmax],
            "label": "mound",
            "subtype": "burial_mound" | "settlement_mound" | "triangulation_mound" | "benchmark_mound"
        }
    ]
}
```

### 2.2 Content Comparison: Brief Text Files

**Current `detect_text-only.md`** vs **Preregistration `detect_brief-text.md`**:

| Aspect | Current | Preregistration | Action |
|--------|---------|-----------------|--------|
| Title | "Text-Only Baseline" | "Brief Text" | Update title |
| Symbol descriptions | ✅ Matches | — | None |
| Section structure | Separate sections (Handling Occlusion, Separating Clusters, When Uncertain) | Combined "Guidelines" section | Restructure |
| Output format | ✅ Matches | — | None |

**Proposed change**: Restructure to match preregistration's simpler "Guidelines" format.

### 2.3 Content Comparison: Brief Text+Image Files

**Current `detect_brief-text-image.md`** vs **Preregistration**:

| Aspect | Current | Preregistration | Action |
|--------|---------|-----------------|--------|
| Content | ✅ Matches | — | None |
| JSON fence | Has ` ```json ` fence | No fence | Remove fence |

**Proposed change**: Remove markdown code fence around JSON output (preregistration doesn't use it).

### 2.4 Content Comparison: Verbose Files

**Current `detect_text-only_elaborate.md`** vs **Preregistration `detect_verbose-text.md`**:

Both are extensive (~700+ words). Key differences:

| Aspect | Current | Preregistration | Action |
|--------|---------|-----------------|--------|
| Title | "Text-Only Elaborate" | "Verbose Text" | Update title |
| Tile size reference | "448×448 tile" | "512×512 tile" | Update to 512 |
| Structure | ✅ Similar | — | Verify alignment |

**Note**: The verbose prompts in preregistration appear to be derived from the `h2-text-elaboration-comparison.md` master document.

### 2.5 Terminology Consistency

All files should use:
- "rays (hachures; spikes)" — consistent three-term descriptor
- "extending OUTWARD" — capitalised for emphasis
- Subtype values: `burial_mound`, `settlement_mound`, `triangulation_mound`, `benchmark_mound`

---

## Part 3: Config File Updates

### Current Config Files

| Config File | Current Instruction | New Instruction |
|-------------|---------------------|-----------------|
| `detect_image-only.json` | `detect_image-only.md` | ✅ No change |
| `detect_image-only_hardneg.json` | `detect_image-only.md` | `detect_image-only_hardneg.md` |
| `detect_text-only.json` | `detect_text-only.md` | `detect_brief-text.md` |
| `detect_text-only_hardneg.json` | `detect_text-only_hardneg.md` | `detect_brief-text_hardneg.md` |
| `detect_text-only_elaborate.json` | `detect_text-only_elaborate.md` | `detect_verbose-text.md` |
| `detect_text-only_elaborate_hardneg.json` | `detect_text-only_elaborate_hardneg.md` | `detect_verbose-text_hardneg.md` |
| `detect_text-image.json` | `detect_text-image.md` | `detect_brief-text-image.md` |
| `detect_text-image_hardneg.json` | `detect_text-image_hardneg.md` | `detect_brief-text-image_hardneg.md` |
| `detect_text-image_elaborate.json` | `detect_text-image_elaborate.md` | `detect_verbose-text-image.md` |
| `detect_text-image_elaborate_hardneg.json` | `detect_text-image_elaborate_hardneg.md` | `detect_verbose-text-image_hardneg.md` |
| Ordering variants (`*_canonical-last*.json`, `*_random-order*.json`) | Various | Update instruction references |

### Config Files to Rename

To maintain consistency, config files should also be renamed:

| Current Config | New Config |
|----------------|------------|
| `detect_text-only.json` | `detect_brief-text.json` |
| `detect_text-only_hardneg.json` | `detect_brief-text_hardneg.json` |
| `detect_text-only_elaborate.json` | `detect_verbose-text.json` |
| `detect_text-only_elaborate_hardneg.json` | `detect_verbose-text_hardneg.json` |
| `detect_text-image.json` | `detect_brief-text-image.json` |
| `detect_text-image_hardneg.json` | `detect_brief-text-image_hardneg.json` |
| `detect_text-image_elaborate.json` | `detect_verbose-text-image.json` |
| `detect_text-image_elaborate_hardneg.json` | `detect_verbose-text-image_hardneg.json` |
| `detect_text-image_canonical-last.json` | `detect_brief-text-image_canonical-last.json` |
| `detect_text-image_canonical-last_hardneg.json` | `detect_brief-text-image_canonical-last_hardneg.json` |
| `detect_text-image_random-order.json` | `detect_brief-text-image_random-order.json` |
| `detect_text-image_random-order_hardneg.json` | `detect_brief-text-image_random-order_hardneg.json` |
| `detect_image-only_canonical-last.json` | ✅ Keep |
| `detect_image-only_canonical-last_hardneg.json` | ✅ Keep |
| `detect_image-only_random-order.json` | ✅ Keep |
| `detect_image-only_random-order_hardneg.json` | ✅ Keep |

---

## Part 4: Files to Delete

These files are redundant after alignment:

| File | Reason |
|------|--------|
| `detect_text-image.md` | Duplicate of `detect_brief-text-image.md` |

---

## Part 5: Execution Checklist

### Phase 1: Create Missing File

- [ ] Create `prompts/system-instructions/detect_image-only_hardneg.md` from preregistration content

### Phase 2: Rename Instruction Files

- [ ] `detect_text-only.md` → `detect_brief-text.md`
- [ ] `detect_text-only_hardneg.md` → `detect_brief-text_hardneg.md`
- [ ] `detect_text-image_hardneg.md` → `detect_brief-text-image_hardneg.md`
- [ ] `detect_text-only_elaborate.md` → `detect_verbose-text.md`
- [ ] `detect_text-only_elaborate_hardneg.md` → `detect_verbose-text_hardneg.md`
- [ ] `detect_text-image_elaborate.md` → `detect_verbose-text-image.md`
- [ ] `detect_text-image_elaborate_hardneg.md` → `detect_verbose-text-image_hardneg.md`

### Phase 3: Update Content

- [ ] Update titles in all renamed files to match preregistration
- [ ] Update tile size reference from 448 to 512 where applicable
- [ ] Restructure brief text files to use "Guidelines" section format
- [ ] Remove JSON code fences from output format sections
- [ ] Verify "rays (hachures; spikes)" terminology throughout

### Phase 4: Delete Redundant Files

- [ ] Delete `detect_text-image.md` (duplicate)

### Phase 5: Rename Config Files

- [ ] Rename all config files per table in Part 3
- [ ] Update `instruction_file` references in each config

### Phase 6: Update Script References

Check and update any scripts that reference old filenames:

- [ ] `scripts/3_detect_tiles.py`
- [ ] `scripts/5_verify_crops.py`
- [ ] Any other scripts importing configs

### Phase 7: Verification

- [ ] All 10 detection instruction files exist with correct names
- [ ] All instruction file content matches preregistration appendix
- [ ] All config files reference correct instruction files
- [ ] No orphaned files in `prompts/system-instructions/`
- [ ] Scripts run without file-not-found errors

---

## Questions for Review

1. **Verbose file content**: Should we copy verbose content verbatim from preregistration appendix, or verify the current elaborate files are equivalent? The elaborate files were created from `h2-text-elaboration-comparison.md`.

2. **Config ordering variants**: The current library has ordering variants (`canonical-last`, `random-order`) for text-image configs. These are for H4 (ordering hypothesis). Should these be retained and renamed, or are they handled differently in the preregistration?

3. **Propose/verify prompts**: The two-stage pipeline prompts exist and match names. Should their content be verified against preregistration Section 1.7?

4. **JSON output fences**: Preregistration doesn't use markdown code fences around JSON output format. Current files are inconsistent. Recommend removing all fences for consistency.

---

## Impact Assessment

| Area | Impact | Risk |
|------|--------|------|
| Scripts | Config file references need updating | Medium |
| Documentation | Already aligned (preregistration is source of truth) | Low |
| Reproducibility | Old config names in any existing results | Low (no holdout runs yet) |
| Git history | File renames tracked by git | None |

---

*Document ready for Opus review.*
