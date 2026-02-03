# Hard Example Prompt Text: Review Synopsis

**Purpose**: Brief for Opus (claude.ai) to review proposed prompt text changes derived
from the hard example library. Provides reasoning and principles so Opus can assess
whether the text is well-calibrated.

**Date**: 2026-02-03 (Session 11)

---

## Governing Principles

Two principles govern all changes:

1. **Describe visual appearance, not map symbology identity.** Prompt text should
   describe what the VLM will see (colours, shapes, spatial relationships) rather than
   interpreting what map features are (grid lines, buildings, canals). The VLM may not
   interpret feature identities the same way a human cartographer would, but visual
   descriptions are robust. This matches the register used for the target symbol itself
   ("sunburst with outward-radiating rays").

2. **Use only diagnostics reliable at VLM exemplar resolution (128×128px).** A human
   examining the full-resolution map can see fine detail (solid vs hollow fill, precise
   outlines, half-coloured patterns). A VLM processing 128px crops cannot reliably
   resolve these. Prompt diagnostics should be calibrated for VLM perception, not
   cartographic accuracy. See Decision 13 in `decisions-log.md` for the full diagnostic
   reliability table.

## Brief:Verbose Ratio Target

The preregistration specifies brief prompts at ~200-300 words and verbose at ~500-700.
Target ratio is ~1:3 measured at the H5-minimal pair. The H5 factor (exclusion guidance
depth) is orthogonal to text-detail — terse/verbose H5 variants add shared exclusion
content to both brief and verbose files, which compresses the apparent ratio at those
levels but doesn't affect the text-detail ratio.

---

## Change 1: Occlusion Guidance

**Source**: HP 07 (mound with diagonal blue line crossing through it, splitting rays)

**What changed**: Updated occlusion guidance across all prompt levels to describe
interference from overlapping features without assuming feature identity. Added
reconstruction guidance (look for rays on either side of interfering features).

**Brief** (Guideline 2): Replaced "roads, contours, or text" with "lines, shapes, or
text". Replaced "rays are partially visible" with "sunburst pattern remains discernible".

**Verbose** (3 edits):
- Decision Procedure step 5: Replaced feature names with colour descriptions
- Partially Occluded Symbols subsection: Replaced interpretive list items with
  colour/shape descriptions; added interference range (partial clip to full split) and
  reconstruction guidance
- Pre-existing "Coordinate grid lines (blue)" and "grid lines (blue)" updated to
  descriptive language for consistency

---

## Change 2: Inward-Pointing Marks + Text Confusion

**Source**: HN 13 (orange-brown round shape with inward marks + "могила" text)

**Two components**:

**2A — Updated existing quarry/pit exclusion** (terse bullet + verbose subsection):
Rewritten with descriptive language. Added colour note — these may appear in orange-brown,
same colour family as mound symbols. Title changed from "Quarry and Pit Symbols" to
"Inward-Pointing Marks". Removed interpretive "(inward = excavation, outward = elevation)"
from key difference.

**2B — New Cyrillic text items** (terse bullet + verbose subsection): Flags Cyrillic
characters ('могила', 'кург.') as a secondary confound. Key difference: "Text characters
alone do not indicate a mound — the sunburst pattern with outward-radiating rays is
required."

**Open wording item**: The distinction between "marks" (inward) and "rays" (outward) is
intentional but under review. Shawn is checking whether "inward-pointing rays or other
marks" better covers the range of inward-pointing features.

---

## Change 3: Non-Mound Round Shapes

**Source**: HN 11 (orange-brown ovoid with dark marks, no rays), HN 14 (round feature
near rectangular outlines and brown curves, no rays)

**VLM calibration note**: The researcher identified detailed human-visible diagnostics
(solid fill, black outline, two black dots, mixed black-brown, half-black-half-white
circle). CC's VLM-perspective review found most of these unreliable at 128px. The prompt
text uses only resolution-robust diagnostics: ray absence, mark location (within shape vs
radiating outward), overall colour composition.

**Terse bullet**: "Round or ovoid shapes in mound-like colours without outward-radiating
rays — dark marks may sit within the shape rather than extending outward"

**Verbose subsection**: "Other Round Shapes in Mound-Like Colours" — catch-all for
confusable round shapes not covered by specific exclusion categories. Diagnostic: no
discrete marks extending outward from the shape.

---

## Change 4: Enhanced Clustering + Dense Features

**Source**: HP 05 (mound abutting symbol + crossed by blue line), HP 06 (subtle mound
next to prominent mound-on-benchmark), HP 08 (four mounds in a line, second missed)

**Two components**:

**4A — Enhanced Clustered Mounds** (verbose-text files only): Added "if you find one,
look carefully nearby" guidance. Addresses VLM-specific satisficing behaviour — the model
may find the most prominent detection in a cluster and stop scanning. Also notes that
neighbouring symbols vary in prominence.

**4B — Symbols Amid Dense Features** (verbose-text files only, new subsection): Mounds
may appear amid visually complex surroundings. Apply radiating ray diagnostic regardless
of context.

---

## File Locations

- **Consolidated prompt text**: Proposed in CC Session 11 conversation (not yet on disk)
- **Decision log**: `docs/methodology/preregistration/decisions-log.md` — Decision 13
- **Working notes**: `docs/notes/working_notes.md` — Observation 87
- **Hard example library decisions**: `planning/hard-example-library-decisions.md`
- **Crop analysis**: `inputs/examples/neutral-naming/MANIFEST.md`
- **Cross-reference table**: In CC Session 11 conversation (prompt text ↔ image path)
