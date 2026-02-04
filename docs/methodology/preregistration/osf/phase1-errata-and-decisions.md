# Phase 1 Errata and Decisions

**Preregistration**: v4.7 (2026-01-31)
**Phase 1 execution**: 2026-01-31 to 2026-02-04
**Repository**: <https://github.com/saross/map-reader-llm> at commit `5d8c251`

This document summarises all protocol corrections, clarifications, and deviations
identified during Phase 1 (baseline calibration) execution. Full details for each
entry are maintained in the repository files referenced below.

**Detailed source files**:

- Protocol errata: `docs/methodology/preregistration/protocol-errata.md` (entries E1–E16)
- Decisions log: `docs/methodology/preregistration/decisions-log.md` (Decisions 4, 11–14)
- FP/FN register: `outputs/phase1-library/fp-fn-register.md`

---

## Classification Key

- **Correction**: Fix to implementation that brings it into alignment with the
  preregistered protocol (no protocol change)
- **Clarification**: Interpretation of an ambiguous point in the preregistration
- **Deviation**: Substantive change from the preregistered protocol (requires justification)

---

## Protocol Errata

### E1: Stale version/date in OSF companion README — Correction

*2026-01-31.* The `osf/README.md` file contained a stale date that did not match
preregistration v4.7. Updated to align. **No protocol impact** (cosmetic metadata).

### E2: Missing execution fields in Phase 1 config — Correction

*2026-02-01.* The Phase 1 library config file was missing five required execution
fields (model, temperature, instruction file, thinking level, max output tokens).
Without the fix, the pipeline would have crashed or used non-preregistered parameter
values. Fields were added to match the preregistered values in Section 8.9.
**No protocol impact.**

### E3: SDK migration for ThinkingConfig support — Correction

*2026-02-01.* The batch detection script used a deprecated Google SDK that does not
support `ThinkingConfig`. Migrated to `google-genai` SDK (v1.56.0). Additionally,
the preregistered model name `gemini-3-flash` was mapped to the API-available variant
`gemini-3-flash-preview` (same model, Google naming convention). **No protocol impact.**

### E4: Tile bounds generation Y-axis inversion — Correction

*2026-02-01.* The tile bounds generation script misinterpreted the Y-axis origin in
tile metadata, shifting all bounds one tile height south (~2565 m). This caused the
evaluation to scope ground truth references to incorrect spatial areas, producing
near-zero F1. Corrected and bounds regenerated. **No protocol impact.**

### E5: Evaluation pipeline reference path and column name bugs — Correction

*2026-02-01.* Three bugs in the evaluation pipeline: (1) wrong reference file path,
(2) column name mismatch between consensus merge output and evaluator, (3) same path
issue in the effects analysis script. Together these caused silent zero-reference
evaluation. **No protocol impact.**

### E6: Pipeline contract validation (post-Phase 1 hardening) — Correction

*2026-02-01.* Added contract validation assertions and 7 integration tests to prevent
recurrence of the silent cascading failures discovered in E3–E5. Covers reference
loading, bounds metadata interpretation, and stage-boundary contracts.
**No protocol impact** (infrastructure hardening only).

### E7: Evaluation reference scoping hardened against boundary effects — Correction

*2026-02-01.* The evaluation pipeline scoped ground truth references using
`union_all()` of tile polygons rather than testing against individual tiles. With
non-adjacent calibration tiles this was geometrically equivalent (Phase 1 results
unaffected), but with denser tile configurations in Phase 2 it could include references
falling in inter-tile gaps. Replaced with per-tile spatial join. Additionally fixed a
secondary issue where references were buffered before scoping. **No protocol impact**
(Phase 1 results unchanged; prevents latent bug in Phase 2+).

### E8: Hard example crops extracted from full map GeoTIFFs — Clarification

*2026-02-02.* The preregistration specifies hard example selection criteria but not
the spatial extraction method. Hard example crops (128x128 px) were extracted from the
full map GeoTIFFs centred on the target coordinate, rather than from detection tiles.
This ensures the relevant feature is always centred with symmetric real map context,
even when the reference point is near a tile edge. Crops may include a few pixels of
map content from outside the detection (calibration) tile boundary. **Minor protocol impact.**
See `protocol-errata.md` E8 for alternatives considered.

### E9: Centre-pointing language added to detection prompts — Clarification

*2026-02-02.* A single sentence was added uniformly to all 11 detection prompt
variants: "Each reference image is centred on the feature being labelled -- the
target symbol for Positive examples, the confusable feature for Negative examples."
This resolves an ambiguity in 128x128 crops where multiple features may appear in a
single crop. Applied identically across all H5 conditions to preserve factor
orthogonality. **Minor protocol impact.** See Decision 12 below for rationale.

### E10: 50 m recognition/localisation threshold determined — Clarification

*2026-02-02.* The preregistration specifies that hard positives are drawn from
recognition failures rather than localisation errors, but leaves the specific distance
threshold to empirical determination. Analysis of the Phase 1 FN distance distribution
revealed a distributional cliff between 30 m and 50 m. A 50 m threshold was adopted,
yielding 9 recognition failures (>50 m) and 15 localisation failures
(20–50 m) from 24 total FNs. **No protocol impact** (empirical
determination within preregistered latitude).
See Decision 11 below.

### E11: Scale-16 and Scale-32 library conditions capped — Clarification

*2026-02-02.* The hard positive pool is structurally exhausted at 4 recognition
failures. Scale-16 (requires 8 HP) and Scale-32 (requires 16 HP) are both capped at
Scale-8 under the preregistered 1:1 HP:HN constraint. This activates the contingency
anticipated at preregistration line 815. Both config files are marked "deferred".
H8 contrasts C1–C3, S1, and B1 remain fully testable; scaling contrasts S2 and S3 are
deferred to post-H10. **No protocol impact** (preregistered contingency activation).

### E12: H9 image diversity runs as HN-diversity-only — Clarification

*2026-02-02.* Due to HP pool exhaustion (E11), the HP channel is frozen for H9-C
(image diversity): 4 slots, 4 examples, every HP appears in every pass. Only HN
examples rotate across passes. HP diversity is untestable with the current pool and
is therefore deferred to post-H10. **Minor protocol impact** (H9-C tests
a subset of intended image diversity factor).

### E13: H12 (HP:HN ratio) deferred to post-H10 — Deviation

*2026-02-02.* H12 tests the effect of varying the HP:HN ratio within hard example
libraries. With HP capped at 4, the only testable ratios confound ratio with total
library size. Deferring to post-H10 (when calibration tile expansion may yield
additional recognition failures) preserves the possibility of an informative, symmetric
test. **Moderate protocol impact** — H12 is a Tier B exploratory hypothesis and its
deferral does not affect confirmatory hypotheses H1–H8.

### E14: Verbose instruction word count exceeds preregistered range — Clarification

*2026-02-04.* Iterative prompt refinement (decision procedure restructuring,
centre-pointing language, exclusion criteria updates) has grown the verbose-level
instruction text to 779 words. The brief-to-verbose ratio is now approximately 1:3.7
(213:779), exceeding the preregistered range by ~80 words. The additional content
consists of structural improvements documented in prior errata. This is a conservative
deviation: it may amplify the H1 M/E effect, working in favour of detecting a
difference. **Minor protocol impact.**

### E15: Inconsistent pass count references in preregistration appendix — Correction

*2026-02-04.* The preregistration appendix contains inconsistent Phase 1 baseline
pass count references. The operative procedure (appendix lines 98–99) specifies K=5
passes with a ≥3/5 threshold, consistent with the execution simulation and the v2.1
changelog. However, two other locations (appendix lines 115 and 1694) retain stale
"≥3/10" references from an earlier draft. Phase 1 was executed with K=5 as intended.
The threshold is moot: all 24 FNs were complete misses (0/5) and all selected FPs
occurred at ≥3/5 votes. **No protocol impact.**

### E16: Prompt text shifted from cartographic naming to visual descriptions — Clarification

*2026-02-03.* The preregistered prompt text describes non-mound map features using
cartographic identity names (e.g., "Contour Line Artefacts", "Infrastructure Markers",
"Roads (black/red lines), contour lines (brown), grid lines (blue)"). These were
systematically revised to visual appearance descriptions (e.g., "Closed Curved Line
Patterns", "Dots on Linear Features", "Lines in various colours (black, red, brown,
blue)"). Interpretive glosses such as "(inward = excavation, outward = elevation)" were
removed. The prompt structure, factor design, and example library are unchanged.
**Minor protocol impact.** See Decision 14 below for rationale.

---

## Post-Preregistration Decisions

Decisions 1–3 and 5–10 were made before preregistration submission and are reflected
in the preregistered protocol (v4.7). The following five decisions were made during
Phase 1 execution and constitute new methodological content.

### Decision 4: Hard Example Selection Criteria

*2026-02-01.* Hard positives and hard negatives were selected from Phase 1 baseline
evaluation (K=5 passes as preregistered; see E15 regarding stale appendix references
to K=10). FNs were categorised by proximity to the nearest detection: recognition
failures (>50 m, no detection anywhere nearby) and localisation failures (20–50 m,
detected but misplaced). All 9 recognition failures were complete misses (0/5);
localisation failures had nearby detections but per-pass miss rates were not
individually verified. Frequency alone provided no differentiation among recognition
failures, so proximity-based ranking was applied, prioritising recognition failures
for HP selection.

During selection, 3 of the initial 4 HP candidates were discovered to be boundary
artefacts and were excluded — their reference coordinates fell outside
all calibration tile polygons. The evaluation scoping bug (E7) had
allowed these out-of-scope references to appear
in the FN list. Final selection: 4 HPs (fids 399, 99, 15, 105) from recognition
failures; 4 HNs (one per map sheet) from vote-5/5 hallucinations (>500 m from any
reference). The one-per-sheet diversity constraint was relaxed for HPs because two
sheets had zero recognition failures among calibration FNs.

Full details including selection tables and alternatives considered:
`decisions-log.md` Decision 4, `fp-fn-register.md`.

### Decision 11: 50 m Recognition/Localisation Threshold and HP Pool Exhaustion

*2026-02-02.* A 50 m distance threshold was adopted to distinguish recognition
failures from localisation failures, based on the distribution of FN distances to
nearest detection: 15 of 24 FNs cluster tightly in the 20–50 m band (localisation
errors), while the remaining 9 are thinly scattered from 50 m to 2450 m (recognition
failures). The sharp drop-off in FN density above 50 m provides a
natural boundary. This threshold exhausts the HP pool at exactly 4
usable examples, triggering the preregistered contingency for Scale-16/32
library capping. The structural asymmetry between HP and HN pools (4 vs ~46 available)
is itself a reportable finding: the model's primary baseline weakness is precision
(excess false alarms) rather than recall (missed mounds).

Full distributional evidence: `decisions-log.md` Decision 11.

### Decision 12: Centre-Pointing Language in Prompts

*2026-02-02.* A descriptive centre-pointing statement was added to all 11 detection
prompt variants: "Each reference image is centred on the feature being labelled -- the
target symbol for Positive examples, the confusable feature for Negative examples."
This addresses ambiguity in 128x128 crops containing multiple features. The statement
is applied uniformly across all H5 conditions (Minimal, Terse, Verbose) to preserve
factor orthogonality — centre-pointing is spatial orientation, distinct from H5's
diagnostic text treatment. Framed as descriptive rather than imperative to avoid
biasing spatial scanning during detection.

Rationale and watch-for criteria: `decisions-log.md` Decision 12.

### Decision 13: VLM-Calibrated Prompt Diagnostics

*2026-02-03.* Prompt text describing hard example features uses only diagnostics that
are reliably resolved by VLMs at 128x128 pixel exemplar resolution, not all
diagnostics that are cartographically valid at higher resolution. Human–VLM cross-
checking during Session 11 found that fine internal structure (solid vs hollow fill,
specific fill patterns) is unreliable at exemplar resolution due to pixel size and
internal model resampling, while features extending into surrounding space (outward-
radiating rays, overall colour composition) remain robust.

Diagnostic reliability table and resolution arithmetic: `decisions-log.md` Decision 13.

### Decision 14: Visual Appearance over Cartographic Identity in Prompts

*2026-02-03.* Prompt text describing non-mound map features was shifted from
cartographic identity names to visual appearance descriptions. The VLM may not map
cartographic labels (e.g., "grid line", "contour line") to the correct visual
patterns, but visual descriptions (e.g., "vertical blue line", "brown curved line")
describe what the model actually sees and are robust. This matches the register
already used for the target symbol ("sunburst with outward-radiating rays"). Distinct
from Decision 13 (which asks *which diagnostics are reliable at 128px*), this decision
asks *what register of description to use* — a conceptual framing question rather than
a resolution-dependent one.

Specific changes and governing principles: `decisions-log.md` Decision 14.

---

## Summary of Protocol Impact

| Entry | Type | Protocol Impact |
|-------|------|-----------------|
| E1 | Correction | None (cosmetic) |
| E2 | Correction | None |
| E3 | Correction | None |
| E4 | Correction | None |
| E5 | Correction | None |
| E6 | Correction | None (infrastructure) |
| E7 | Correction | None (preventive) |
| E8 | Clarification | Minor |
| E9 | Clarification | Minor |
| E10 | Clarification | None |
| E11 | Clarification | None (contingency) |
| E12 | Clarification | Minor |
| E13 | Deviation | Moderate (Tier B exploratory) |
| E14 | Clarification | Minor |
| E15 | Correction | None |
| E16 | Clarification | Minor |
| Decision 4 | — | Selection criteria operationalised |
| Decision 11 | — | Threshold determined; contingency activated |
| Decision 12 | — | Uniform prompt addition |
| Decision 13 | — | Diagnostic filtering principle adopted |
| Decision 14 | — | Visual description register adopted |

**No confirmatory hypotheses (H1–H8) were affected.** The single deviation (E13,
deferral of exploratory H12) preserves the possibility of an informative test after
H10 expands the calibration tile pool.
