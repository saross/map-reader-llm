# Instructions: Aligning H2 Two-Stage Configs with Preregistration

**Date**: 2026-01-18
**Purpose**: Align `propose_image-only.json`, `verify_image-only.json`, and associated .md files with preregistration v4.6
**Priority**: Must complete before OSF submission

---

## Issue 1: Library Composition (CRITICAL)

**Problem:** Both `propose_image-only.json` and `verify_image-only.json` currently use the Canonical library (9 examples: 4 Canon+, 2 Canon-, 3 nulls).

**Preregistration requirement:** H2 must be tested "at optimal single-stage configuration" (preregistration §H2, line 463).

### Action Required

1. Update both configs to use a **placeholder for H8-optimal library**:
   ```json
   "library": "TBD_H8_OPTIMAL",
   "examples": "// Will be populated with optimal library from H8 (Phase 2c)"
   ```

2. Add a note in both config files:
   ```json
   "_NOTE": "This config will be finalized after Phase 2c (H8) determines optimal library composition. The Canonical library shown here is a placeholder from early development."
   ```

3. Document in `execution-plan.md` that H2 testing occurs **after Phase 2c completes** and uses whatever library proves optimal (likely Scale-8, Scale-16, or Scale-32).

---

## Issue 2: Undocumented Parameters

**Problem:** `verify_image-only.json` contains two parameters not mentioned in preregistration:
- `verification_threshold: 0.51`
- `majority_vote_fraction: 0.5`

### Action Required

Choose one option:

**Option A** (if these are implementation details for your pipeline code):
- Keep the parameters but add explanatory comments:
  ```json
  "verification_threshold": 0.51,  // Pipeline threshold for binary classification from probability
  "majority_vote_fraction": 0.5,   // Pipeline parameter for consensus across multiple verifier passes
  "_NOTE": "These are pipeline implementation parameters, not experimental factors"
  ```

**Option B** (if these aren't actually used):
- Remove them entirely

**Option C** (if these ARE experimental design parameters):
- Document them in preregistration §H2 implementation details

**Question for SR:** Which option applies?

---

## Issue 3: Subtype Classification

**Problem:** `propose_image-only.md` outputs 4 subtypes (burial_mound, settlement_mound, triangulation_mound, benchmark_mound), but this isn't mentioned in preregistration §H2.

### Action Required

Add a note to preregistration §H2 (around line 474) after "Stage 2: Crop candidate regions, verify with focused prompt":

```markdown
*Implementation note: The proposer classifies detections into subtypes (burial mound, settlement mound, triangulation point on mound, benchmark on mound) based on visual characteristics. This classification is for diagnostic purposes and quality assessment; all subtypes are treated as positive detections for F1 calculation.*
```

---

## Issue 4: Missing Appendix Documentation

**Problem:** Preregistration checklist (line 2226) says "Document prompt text for all conditions (Appendix)" but there's no appendix with H2 prompts.

### Action Required

Choose one approach:

**Option A: Add to existing appendix document**

If `preregistration-appendix-prompts.md` exists, add:

```markdown
### A.X: H2 Two-Stage Prompt Specifications

#### H2 Condition B: Coarse-to-Fine (Proposer-Verifier)

**Stage 1 - Proposer (propose_image-only.md):**

[paste full propose_image-only.md content]

**Stage 2 - Verifier (verify_image-only.md):**

[paste full verify_image-only.md content]

**Configuration Files:**
- propose_image-only.json
- verify_image-only.json

**Implementation notes:**
- Library composition: Will use H8-optimal library (TBD after Phase 2c)
- Temperature: Will use H7-optimal temperature (TBD after Phase 2b, or 1.0 default)
- Thinking level: minimal (based on calibration pilot 2026-01-15)
- Proposer instruction: "err on the side of detection" for high recall
- Verifier uses probability scoring (0.0-1.0) with threshold at 0.51
```

**Option B: Reference in preregistration**

Add to preregistration §8.3:

```markdown
Complete H2 prompt specifications are documented in `preregistration-appendix-prompts.md` Section X.
```

---

## Issue 5: Temperature Alignment

**Problem:** Both configs specify `temperature: 1.0`, but this should be the optimal temperature from H7 (Phase 2b).

### Action Required

Update both configs:
```json
"temperature": "TBD_H7_OPTIMAL",  // Will use optimal from Phase 2b, or 1.0 if T=1.0 proves optimal
```

**Alternative:** If you prefer to keep numeric values, add a comment:
```json
"temperature": 1.0,  // Placeholder - will use H7-optimal (Phase 2b result)
```

---

## Issue 6: Thinking Level (NO CHANGE NEEDED)

**Status:** Both configs specify `thinking_level: minimal`, which is correct based on the calibration pilot.

### Action Required

Add a clarifying comment:
```json
"thinking_level": "minimal",  // Based on thinking level calibration pilot (2026-01-15)
```

---

## Issue 7: Execution Sequencing

**Problem:** H2 depends on parameters from earlier phases but this dependency isn't clearly documented.

### Action Required

Update `execution-plan.md` Phase 3c (H2 Two-Stage) to include:

```markdown
**Prerequisites:**
- Phase 2b (H7) complete → optimal temperature known
- Phase 2c (H8) complete → optimal library composition known
- Phase 2d (H5) complete → optimal negative text treatment known

**Configuration:**
- Uses optimal M/E level from Phase 2a (H1)
- Uses optimal temperature from Phase 2b (H7)
- Uses optimal library from Phase 2c (H8)
- Uses optimal negative text from Phase 2d (H5)

**Note:** The propose and verify config files are templates that will be instantiated with these optimal parameters before H2 testing begins.
```

---

## Summary Checklist

Complete before OSF submission:

- [ ] Update library in both configs to placeholder "TBD_H8_OPTIMAL" with explanatory note
- [ ] Resolve verification_threshold and majority_vote_fraction parameters (Option A/B/C - needs SR input)
- [ ] Add subtype classification note to preregistration §H2
- [ ] Add H2 prompts to appendix (or create appendix reference in preregistration)
- [ ] Update temperature to "TBD_H7_OPTIMAL" placeholder (or add clarifying comment)
- [ ] Add thinking_level comment referencing calibration pilot
- [ ] Update execution-plan.md to document H2 prerequisites and parameter dependencies
- [ ] Check preregistration checklist item "Document prompt text for all conditions" and mark complete

---

## Key Principle

These configs are **templates** that will be finalized with parameters from earlier phases:

| Parameter | Source | Status |
|-----------|--------|--------|
| thinking_level | Calibration pilot | ✓ Fixed (minimal) |
| temperature | H7 (Phase 2b) | ⏳ TBD |
| library composition | H8 (Phase 2c) | ⏳ TBD |
| M/E level | H1 (Phase 2a) | ⏳ TBD |
| negative text | H5 (Phase 2d) | ⏳ TBD |

The configs should clearly distinguish:
- **Infrastructure parameters** (thinking_level=minimal) - already determined
- **Experimental parameters** (library, temperature) - determined by earlier phases

---

## Questions for SR

1. **verification_threshold and majority_vote_fraction**: Which option (A/B/C) applies?
2. **Appendix location**: Add to existing appendix doc or create new section in preregistration?
3. **Temperature placeholder**: Use "TBD_H7_OPTIMAL" string or numeric 1.0 with comment?

---

*Document version: 1.0*
*Created: 2026-01-18*
