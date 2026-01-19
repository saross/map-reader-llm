# Two-Stage Pipeline Prompt Revision Instructions

**Document purpose**: Specification for updating H2 two-stage pipeline prompts and configs to use brief-level text and match the new prompt construction principles.

**Prepared by**: Opus 4.5 in consultation with Shawn Ross
**Date**: 2026-01-20

---

## 1. Context

H2 (Two-Stage Pipelines) is **confirmatory**. The two-stage prompts need updating to:

1. Use brief-level text content (middle ground between minimal and verbose)
2. Apply the same prompt construction principles as the main detection prompts
3. Update filenames to reflect the text level
4. Update config files to reference new instruction files

---

## 2. File Renames

| Current File | New File |
|--------------|----------|
| `prompts/propose_image-only.md` | `prompts/propose_brief.md` |
| `prompts/verify_image-only.md` | `prompts/verify_brief.md` |
| `prompts/propose_image-only.json` | `prompts/propose_brief.json` |
| `prompts/verify_image-only.json` | `prompts/verify_brief.json` |

---

## 3. Instruction File Content

### 3.1 propose_brief.md

```markdown
# Two-Stage Detection: Proposer

Detect all candidate burial mound symbols in this Soviet topographic map tile. This is Stage 1 of a two-stage pipeline; a verifier will filter false positives.

## Target Symbols

All mound symbols share one diagnostic feature: short **rays (hachures) radiating OUTWARD** from a central shape, forming a "sunburst" or "gear" pattern. This indicates elevated terrain.

**Subtypes to detect:**

- **Burial mound (kurgan)**: Orange-brown hollow circle with rays. ~10-20 pixels diameter. Often accompanied by elevation numbers or "кург." label.
- **Settlement mound**: Orange-brown, larger and often oval/irregular. More rays (8-15).
- **Triangulation point on mound**: Black triangle with central dot, surrounded by black rays.
- **Benchmark on mound**: Black square with central dot, surrounded by black rays.

The **rays pointing outward** are essential. Symbols without visible rays are not mounds.

## Guidelines

1. Provide individual bounding boxes for each symbol, even in clusters.
2. Symbols may be partially occluded by roads, contours, or text. Include if rays are partially visible.
3. If reference examples are provided, compare uncertain cases against them.

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

**Notes:**
- This is identical to `detect_brief-text-image.md` except for the opening line which adds pipeline context
- No "err on the side of detection" language (removed per new principles)
- No role preamble
- Action-first structure

---

### 3.2 verify_brief.md

```markdown
# Two-Stage Detection: Verifier

Classify whether the candidate symbol at the centre of this crop is a burial mound.

## Diagnostic Criteria

Mound symbols have **rays (hachures) radiating OUTWARD** from a central shape ("sunburst" pattern). This indicates elevated terrain.

**Key tests:**

1. Are there rays radiating from a central point? No rays → not a mound.
2. Do rays point OUTWARD (mound) or INWARD (quarry/pit)? Inward → not a mound.
3. Check central shape: circle/oval (plain mound), triangle (triangulation on mound), square (benchmark on mound).
4. Check colour: orange-brown (plain mound) or black (survey marker on mound).

If reference examples are provided, compare the candidate against them.

## Output Format

Return JSON:

{
    "reasoning": "Brief description of visual features observed.",
    "mound_probability": 0.0
}

## Scoring Guide

- **0.9-1.0**: Clear sunburst pattern with outward-radiating rays
- **0.6-0.8**: Likely mound, some ambiguity or occlusion
- **0.3-0.5**: Uncertain, could be mound or similar feature
- **0.0-0.2**: Not a mound (no rays, wrong direction, noise, isolated marker)
```

**Notes:**
- Action-first structure
- No role preamble
- Includes diagnostic criteria (not just "compare to examples")
- Conditional reference framing

---

## 4. Config File Updates

### 4.1 propose_brief.json

Update the following fields:

```json
{
    "version": "propose_brief",
    "description": "Two-Stage Proposer (Stage 1). High-recall detection using brief text, use with verify_brief.",
    "hypothesis": "H2",
    "instruction_file": "propose_brief.md",
    ...
}
```

**Changes from current:**
- `version`: `"propose_image-only"` → `"propose_brief"`
- `description`: Update to mention "brief text"
- `instruction_file`: `"propose_image-only.md"` → `"propose_brief.md"`

**Keep unchanged:**
- `model`, `temperature`, `max_output_tokens`, `thinking_level`
- `examples` array
- `_config_notes` (update `proposer_strategy` to remove "err on the side of detection" reference)

### 4.2 verify_brief.json

Update the following fields:

```json
{
    "version": "verify_brief",
    "description": "Two-Stage Verifier (Stage 2). Precision-focused verification using brief text.",
    "hypothesis": "H2",
    "instruction_file": "verify_brief.md",
    ...
}
```

**Changes from current:**
- `version`: `"verify_image-only"` → `"verify_brief"`
- `description`: Update to mention "brief text"
- `instruction_file`: `"verify_image-only.md"` → `"verify_brief.md"`

**Keep unchanged:**
- `model`, `temperature`, `max_output_tokens`, `thinking_level`
- `examples` array
- `_config_notes` (no changes needed)

---

## 5. Full Updated Config Files

### 5.1 propose_brief.json (complete)

```json
{
    "version": "propose_brief",
    "description": "Two-Stage Proposer (Stage 1). High-recall detection using brief text, use with verify_brief.",
    "hypothesis": "H2",
    "model": "gemini-3-flash",
    "instruction_file": "propose_brief.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "thinking_level": "minimal",
    "_config_notes": {
        "template_status": "This config is a template. Parameters will be finalised after earlier phases complete.",
        "temperature": "Placeholder - will use H7-optimal from Phase 2b (or 1.0 if T=1.0 proves optimal)",
        "library": "Placeholder - will use H8-optimal from Phase 2c (likely Scale-8, Scale-16, or Scale-32)",
        "thinking_level": "Fixed at minimal based on calibration pilot (2026-01-15)",
        "proposer_strategy": "Uses brief-level diagnostic text. Subtypes (burial_mound, settlement_mound, triangulation_mound, benchmark_mound) are for diagnostics; all count as positive detections for F1."
    },
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive: Burial Mound (Kurgan)", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive: Settlement Mound", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive: Triangulation Point ON Mound", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive: Benchmark ON Mound", "category": "canonical_positive"},
        {"path": "neutral/example_05.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_06.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_07.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_08.png", "label": "Negative: Benchmark ALONE (no mound)", "category": "canonical_negative"},
        {"path": "neutral/example_09.png", "label": "Negative: Triangulation Point ALONE (no mound)", "category": "canonical_negative"}
    ],
    "_library_note": "Current examples are Canonical library (placeholder). Will be updated to H8-optimal composition after Phase 2c."
}
```

### 5.2 verify_brief.json (complete)

```json
{
    "version": "verify_brief",
    "description": "Two-Stage Verifier (Stage 2). Precision-focused verification using brief text.",
    "hypothesis": "H2",
    "model": "gemini-3-flash",
    "instruction_file": "verify_brief.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "thinking_level": "minimal",
    "_config_notes": {
        "template_status": "This config is a template. Parameters will be finalised after earlier phases complete.",
        "temperature": "Placeholder - will use H7-optimal from Phase 2b (or 1.0 if T=1.0 proves optimal)",
        "library": "Placeholder - will use H8-optimal from Phase 2c (likely Scale-8, Scale-16, or Scale-32)",
        "thinking_level": "Fixed at minimal based on calibration pilot (2026-01-15)",
        "usage": "Run with --iterations 1 for H2 testing. Each K=10 run is independent (one proposer pass, one verifier pass). Raw mound_probability scores used for evaluation, no binary thresholding."
    },
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive: Burial Mound (Kurgan)", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive: Settlement Mound", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive: Triangulation Point ON Mound", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive: Benchmark ON Mound", "category": "canonical_positive"},
        {"path": "neutral/example_05.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_06.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_07.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_08.png", "label": "Negative: Benchmark ALONE (no mound)", "category": "canonical_negative"},
        {"path": "neutral/example_09.png", "label": "Negative: Triangulation Point ALONE (no mound)", "category": "canonical_negative"}
    ],
    "_library_note": "Current examples are Canonical library (placeholder). Will be updated to H8-optimal composition after Phase 2c."
}
```

---

## 6. Preregistration Updates Required

The following references in `preregistration.md` need updating:

### Section 8.7.2 Configuration File Mapping

Update the H2 row:

**Current:**
```
| H2 | `propose_*.json` + `verify_*.json` (coarse-to-fine); `detect_*.json` + `expand_*.json` (fine-to-coarse) | Corresponding `.md` files |
```

**Updated:**
```
| H2 | `propose_brief.json` + `verify_brief.json` (coarse-to-fine); `detect_*.json` + `expand_*.json` (fine-to-coarse) | `propose_brief.md`, `verify_brief.md` |
```

### Appendix (preregistration-appendix-prompts.md)

If the appendix documents the two-stage prompts, update the content to reflect the new `propose_brief.md` and `verify_brief.md` content.

---

## 7. Verification Checklist

After implementation, verify:

- [ ] `propose_image-only.md` renamed to `propose_brief.md` with new content
- [ ] `verify_image-only.md` renamed to `verify_brief.md` with new content
- [ ] `propose_image-only.json` renamed to `propose_brief.json` with updated references
- [ ] `verify_image-only.json` renamed to `verify_brief.json` with updated references
- [ ] Old `*_image-only.*` files removed (or moved to archive)
- [ ] No "err on the side of detection" language in proposer
- [ ] No role preambles ("You are an expert...")
- [ ] Action-first opening in both prompts
- [ ] Diagnostic criteria included in both prompts
- [ ] Conditional reference framing present
- [ ] `instruction_file` field in configs points to correct `.md` files
- [ ] `version` field in configs matches filename

---

## 8. Rationale

**Why brief instead of image-only?**

The image-only level (~50 words) provides minimal diagnostic criteria, relying almost entirely on visual examples. For a two-stage pipeline where:

1. The proposer needs to identify candidates reliably
2. The verifier needs to make binary decisions on cropped regions

...having explicit diagnostic criteria (the sunburst pattern, ray direction, subtypes) provides a consistent decision framework across both stages. Brief (~185 words) is the pragmatic middle ground: enough guidance to be effective, not so much as to be unwieldy.

**Why not verbose?**

The verifier operates on small cropped regions with a single centered candidate. The extensive edge case handling in verbose (occlusion, clustering, degradation) is less relevant when the model is examining one isolated symbol. Brief provides the core diagnostic without unnecessary content.

---

*End of specification*
