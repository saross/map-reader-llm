# Prompt Library Alignment: Review and Corrections

**Target document**: `prompt-library-alignment.md`
**Reference**: `preregistration.md` v4.2
**Date**: 2026-01-08

---

## Summary

The alignment plan is well-structured and largely correct. One significant correction: **text-only modalities do not need `_hardneg` variants** per preregistration design.

---

## Key Correction: Text-Only Hardneg Files

### Issue

The alignment plan includes creating/renaming `_hardneg` variants for text-only modalities:
- `detect_brief-text_hardneg.md`
- `detect_verbose-text_hardneg.md`

### Preregistration Says (lines 609, 591)

> "Text-only modalities are tested at H5=None only, since they have no example images and the Text-only H5 condition has been removed."

> "The 'Text-only' condition (exclusion text without hard negative images) was removed as practically implausible — if hard negative examples are important enough to explain in text, they warrant visual demonstration."

### Resolution

**Do NOT create** `detect_brief-text_hardneg.md` or `detect_verbose-text_hardneg.md`.

Text-only modalities (Brief-text, Verbose-text) are only tested at H5=None. The H5 factor (None / Images-only / Text+Images) applies only to image-using modalities.

---

## Updated File Inventory

### Instruction Files Needed (10 total)

| File | Modality | H5 Variant | Action |
|------|----------|------------|--------|
| `detect_image-only.md` | Image-only | None | ✅ Exists |
| `detect_image-only_hardneg.md` | Image-only | Text+Images | ❌ **Create** |
| `detect_brief-text.md` | Brief-text | None | 🔄 Rename from `detect_text-only.md` |
| `detect_brief-text-image.md` | Brief+image | None | ✅ Exists |
| `detect_brief-text-image_hardneg.md` | Brief+image | Text+Images | 🔄 Rename from `detect_text-image_hardneg.md` |
| `detect_verbose-text.md` | Verbose-text | None | 🔄 Rename from `detect_text-only_elaborate.md` |
| `detect_verbose-text-image.md` | Verbose+image | None | 🔄 Rename from `detect_text-image_elaborate.md` |
| `detect_verbose-text-image_hardneg.md` | Verbose+image | Text+Images | 🔄 Rename from `detect_text-image_elaborate_hardneg.md` |
| `propose_image-only.md` | H2 proposer | — | ✅ Exists |
| `verify_image-only.md` | H2 verifier | — | ✅ Exists |

### Files to DELETE (not rename)

| File | Reason |
|------|--------|
| `detect_text-image.md` | Duplicate of `detect_brief-text-image.md` |
| `detect_text-only_hardneg.md` | Text-only at H5=None only; no hardneg variant |
| `detect_text-only_elaborate_hardneg.md` | Text-only at H5=None only; no hardneg variant |

---

## Updated Config File Inventory

### Config Files Needed

**Main detection configs (9 per preregistration Section 8.7.4):**

| Config | Instruction File |
|--------|------------------|
| `detect_image-only.json` | `detect_image-only.md` |
| `detect_image-only_hardneg.json` | `detect_image-only_hardneg.md` |
| `detect_brief-text.json` | `detect_brief-text.md` |
| `detect_brief-text-image.json` | `detect_brief-text-image.md` |
| `detect_brief-text-image_hardneg.json` | `detect_brief-text-image_hardneg.md` |
| `detect_verbose-text.json` | `detect_verbose-text.md` |
| `detect_verbose-text-image.json` | `detect_verbose-text-image.md` |
| `detect_verbose-text-image_hardneg.json` | `detect_verbose-text-image_hardneg.md` |
| (9th is runtime variant, not separate config) | — |

**H4 ordering variants (6 new configs for partial cross):**

| Config | Base |
|--------|------|
| `detect_image-only_canonical-last.json` | image-only |
| `detect_image-only_random-order.json` | image-only |
| `detect_brief-text-image_canonical-last.json` | brief+image |
| `detect_brief-text-image_random-order.json` | brief+image |
| `detect_verbose-text-image_canonical-last.json` | verbose+image |
| `detect_verbose-text-image_random-order.json` | verbose+image |

**Note**: H4 ordering variants may also need `_hardneg` versions depending on whether ordering is tested at H5=None or optimal H5. Check preregistration H4 (line 554): "All H4 conditions tested at optimal H5 and T from main factorial."

If optimal H5 turns out to be Text+Images, you'd need hardneg ordering variants. Recommend creating them for completeness:

| Config | Notes |
|--------|-------|
| `detect_image-only_canonical-last_hardneg.json` | |
| `detect_image-only_random-order_hardneg.json` | |
| `detect_brief-text-image_canonical-last_hardneg.json` | |
| `detect_brief-text-image_random-order_hardneg.json` | |
| `detect_verbose-text-image_canonical-last_hardneg.json` | |
| `detect_verbose-text-image_random-order_hardneg.json` | |

### Config Files to DELETE

| Config | Reason |
|--------|--------|
| `detect_text-only_hardneg.json` | No text-only hardneg variant |
| `detect_text-only_elaborate_hardneg.json` | No text-only hardneg variant |
| Any `detect_text-image*.json` | Renamed to `detect_brief-text-image*.json` |

---

## Answers to CC's Questions

### Q1: Verbose file content

**Answer**: Copy verbatim from preregistration appendix. The preregistration is the registered source of truth. If current elaborate files differ, flag discrepancies for Shawn's review before deciding whether to update the appendix or discard changes.

### Q2: Config ordering variants

**Answer**: Yes, retain and rename. H4 (ordering) is confirmatory. Create both non-hardneg and hardneg versions for image-using modalities at all 3 M/E levels tested in H4.

### Q3: Propose/verify prompts

**Answer**: Yes, verify content matches preregistration appendix. H2 (two-stage) is confirmatory.

### Q4: JSON output fences

**Answer**: Remove all markdown code fences from output format sections. Preregistration doesn't use them, and they can cause parsing issues.

---

## Content Standardisation

Apply these changes across all instruction files:

| Item | Standard Form |
|------|---------------|
| Ray descriptor | "rays (hachures; spikes)" |
| Emphasis | "extending OUTWARD" (capitalised) |
| Tile size | "512×512 tile" (not 448) |
| Subtypes | `burial_mound`, `settlement_mound`, `triangulation_mound`, `benchmark_mound` |
| JSON output | No markdown code fences |

---

## Updated Execution Checklist

### Phase 1: Create Missing File

- [ ] Create `detect_image-only_hardneg.md` from preregistration appendix

### Phase 2: Rename Instruction Files (5 renames)

- [ ] `detect_text-only.md` → `detect_brief-text.md`
- [ ] `detect_text-image_hardneg.md` → `detect_brief-text-image_hardneg.md`
- [ ] `detect_text-only_elaborate.md` → `detect_verbose-text.md`
- [ ] `detect_text-image_elaborate.md` → `detect_verbose-text-image.md`
- [ ] `detect_text-image_elaborate_hardneg.md` → `detect_verbose-text-image_hardneg.md`

### Phase 3: Delete Redundant Instruction Files (3 deletions)

- [ ] Delete `detect_text-image.md` (duplicate)
- [ ] Delete `detect_text-only_hardneg.md` (text-only at H5=None only)
- [ ] Delete `detect_text-only_elaborate_hardneg.md` (text-only at H5=None only)

### Phase 4: Update Content

- [ ] Update titles in renamed files
- [ ] Update tile size 448 → 512 where needed
- [ ] Remove JSON code fences
- [ ] Verify "rays (hachures; spikes)" terminology
- [ ] Verify verbose content matches preregistration appendix

### Phase 5: Rename Config Files

- [ ] Rename all `detect_text-only*.json` → `detect_brief-text*.json`
- [ ] Rename all `detect_text-image*.json` → `detect_brief-text-image*.json`
- [ ] Rename all `*_elaborate*.json` → `*verbose*.json`
- [ ] Update `instruction_file` references in each config

### Phase 6: Delete Redundant Config Files

- [ ] Delete `detect_text-only_hardneg.json`
- [ ] Delete `detect_text-only_elaborate_hardneg.json`

### Phase 7: Create H4 Ordering Configs (if not existing)

- [ ] Create ordering variants for 3 M/E levels × 2 orderings × 2 H5 = 12 configs
- [ ] Or verify existing ordering configs and rename as needed

### Phase 8: Update Script References

- [ ] Check `scripts/3_detect_tiles.py`
- [ ] Check `scripts/5_verify_crops.py`
- [ ] Check any other scripts importing configs

### Phase 9: Verification

- [ ] 10 detection instruction files exist with correct names
- [ ] Content matches preregistration appendix
- [ ] All config files reference correct instruction files
- [ ] No orphaned files
- [ ] Scripts run without errors

---

## Final File Count

| Category | Count |
|----------|-------|
| Detection instruction files | 8 (5 modalities × ~1.6 H5 variants) |
| H2 pipeline instruction files | 2 (propose + verify) |
| **Total instruction files** | **10** |
| Main detection configs | 8 |
| H4 ordering configs | 12 (3 M/E × 2 orders × 2 H5) |
| H2 pipeline configs | 2 |
| **Total config files** | **~22** |

---

*Ready for implementation.*
