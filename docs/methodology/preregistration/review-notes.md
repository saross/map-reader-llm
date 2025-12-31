# Preregistration Review Notes

**Reviewer**: Claude Code
**Date**: 2025-12-30 (initial), 2025-12-31 (updated)
**Document reviewed**: `preregistration.md` v2.5 → v2.11

**Status**: All methodology and prompt/config composition complete. Document ready for registration pending routine editing.

---

## A. Errors Requiring Correction (RESOLVED)

### A.1 Date/Version Inconsistencies

| Location | Issue | Correction |
|----------|-------|------------|
| Line 10 | Year error: "2024-12-30" | Should be "2025-12-30" |
| Line 928-930 | Footer version "2.0", dates "2024-12-22/23" | Should match header: v2.5, 2025-12-30 |

### A.2 Section Numbering

| Location | Issue | Correction |
|----------|-------|------------|
| Line 232 | "4.2.1 Spatial Tolerance" appears under 4.1 | Should be "4.1.1" |
| Line 255 | "4.2 Secondary Outcome" follows 4.2.1 | Should be renumbered after fixing above |

### A.3 Summary Table (Section 7) Mapping Errors

The Summary Table (lines 701-713) has incorrect hypothesis numbering:

| Table Shows | Should Be | Description |
|-------------|-----------|-------------|
| H8 (fine-to-coarse) | H10 | Exploratory hypothesis |
| H9 (temperature) | H11 | Exploratory hypothesis |
| H10 (cross-model) | H12 | Exploratory hypothesis |

Also missing from summary: H8 (Flash→Pro transfer), H9 (Temperature), H13-H15.

### A.4 H3 Status Contradiction

- Line 705: States "Not tested"
- But H3 is listed as Confirmatory in Section 5
- **Clarification needed**: Is H3 being tested or documented from training data only?

### A.5 Encoding Artefacts

Lines 709, 839-856, 865 contain encoding issues (â†', â€", Î±). These appear to be UTF-8 characters that weren't properly encoded during export.

### A.6 Model ID Issues

The model IDs in Section 8.2 need verification:

| Provider | Listed ID | Status |
|----------|-----------|--------|
| Gemini | `gemini-3-flash-preview` | Codebase uses `gemini-3-flash` |
| Claude | `claude-haiku-4-5-20251001` etc. | Verify these are actual release IDs |
| GPT | `gpt-5.2-*` | Verify availability |

**Action**: Confirm actual model IDs before registration. Use placeholder format if models not yet released.

---

## B. Consistency Issues

### B.1 Answers from Section 12 Not Applied

Several answers in Section 12 are marked but not integrated:

| Question | Answer Given | Integration Status |
|----------|--------------|-------------------|
| 12.1.1 Data collection dates | "30 December 2025 - 31 January 2026" | **Not in main document** - add to Section 1 |
| 12.2.5 Detection matching | "Nearest spatial match(?)" | **Tentative** - needs confirmation and integration |

### B.2 Few-Shot Library Composition

The preregistration says:
- Section 8.4: "Legend-derived symbols (burial mound, settlement mound, triangulation on mound, benchmark on mound)" + "3 null tiles"
- This matches our actual implementation (4 positives + 3 nulls = 7 baseline)

**Current codebase library** (`inputs/references/neutral/MANIFEST.md`):
- 4 positive examples (legend-derived)
- 3 null tiles (from training set)
- 2 hard negatives (benchmark alone, triangulation alone)

This is consistent. However, Section 8.4 mentions "hard positive" examples that don't exist yet - these come from the procedure-derived selection (false negatives from training evaluation).

### B.3 Missing Rakovski Null Tile

The null tile selection (Section 8.4) shows 3 tiles from Lesovo, Elenovo, and 32635. Rakovski is not represented. This matches `null_tiles_manifest.json` but should be noted - was this intentional?

---

## C. Improvements Based on Codebase Knowledge

### C.0 Codebase Consistency Review (2025-12-30)

Full review of all scripts for matching-related code. All now use consistent 20m distance-based approach:

| Script | Matching Approach | Status |
|--------|-------------------|--------|
| `lib_advanced_metrics.py` | Hungarian algorithm, 20m | Reference implementation |
| `benchmark_variability.py` | Centroid distance, 20m | Updated (removed IoU) |
| `generate_union_candidates.py` | Centroid distance, 20m | Updated |
| `analyze_fp_crops.py` | Centroid distance, 20m | Updated (was IoU > 0.5) |
| `6_accuracy_report.py` | Uses lib_advanced_metrics | Consistent |
| `7_analyze_consensus.py` | Uses lib_advanced_metrics | Fixed docstring |
| `7_analyze_consensus_runs.py` | buffer(20) | Consistent |
| `3_georeference_and_visualize.py` | 20m deduplication | Consistent |

**Key change**: Replaced IoU-based clustering (threshold 0.5) with centroid distance-based clustering (threshold 20m) across all voting/consensus code to align with F1 evaluation spatial tolerance.

### C.1 Prompt Config Alignment

Our current prompt structure supports most hypotheses:

| Hypothesis | Required Configs | Current Status |
|------------|------------------|----------------|
| H1 (text modality) | image-only vs text-image | `detect_image-only.json` + `detect_text-image.json` |
| H2 (text elaboration) | minimal vs elaborate | `detect_image-only.md` vs `detect_text-image.md` |
| H3 (two-stage) | single vs propose+verify | `detect_image-only.json` vs `propose_image-only.json` + `verify_image-only.json` |
| H7 (hard negatives) | baseline vs hardneg | All `-hardneg` variants exist |

### C.2 Detection Matching Algorithm Update

Section 4.1.2 now documents **one-to-one matching** via the Hungarian algorithm:
- Implementation: `scripts/lib_advanced_metrics.py` using `scipy.optimize.linear_sum_assignment`
- Each detection matches at most one reference, and vice versa
- A detection spanning two mounds counts as 1 TP + 1 FN (important for mound counting)
- This replaces the previous reference-centric approach

### C.3 Voting Implementation Gap

Section 8.5 says "[To be specified]" for:
- Spatial matching threshold for aggregating detections across runs
- Aggregation algorithm

**From codebase** (`scripts/lib_advanced_metrics.py`):
- We have spatial matching at 20m buffer with Hungarian algorithm
- No multi-run voting aggregation implemented yet

**Recommendation**: Document the voting algorithm:
```
1. Run N passes, collect all detections
2. Cluster detections within [X]m of each other
3. Count votes per cluster
4. Accept clusters with ≥threshold votes
```

### C.4 Example Count Discrepancy

Section 8.4 implies the library will have:
- 4 legend-derived positives
- 4 hard positives (from false negatives)
- 3 hard negatives (from false positives)
- 3 null tiles
- **Total: 14 examples**

But current configs only have 7 baseline / 9 hardneg. The hard positives haven't been selected yet (requires running baseline on training tiles first).

---

## D. Prompts and Configs to Create

### D.1 Existing (Ready)

| Config | Purpose | Status |
|--------|---------|--------|
| `detect_image-only.json` | H1, H2 baseline | Ready |
| `detect_image-only-hardneg.json` | H7 hardneg condition | Ready |
| `detect_text-image.json` | H1, H2 elaborate condition | Ready |
| `detect_text-image-hardneg.json` | H7 with text | Ready |
| `detect_text-only.json` | Text-only baseline | Ready |
| `detect_text-only-hardneg.json` | Text-only with exclusions | Ready |
| `propose_image-only.json` | H3 two-stage proposer | Ready |
| `verify_image-only.json` | H3 two-stage verifier | Ready |

### D.2 New Configs Needed

#### H5: Example Ordering

Need 3 ordering variants:

| Config Name | Ordering | Description |
|-------------|----------|-------------|
| `detect_image-only_canonical-first.json` | Legend → Hard | Canonical examples first |
| `detect_image-only_canonical-last.json` | Hard → Legend | Hard examples first |
| `detect_image-only_random-order.json` | Random | Random permutation (×3 with seeds) |

**Implementation note**: These are config variants only - same instruction file, different example ordering in JSON.

#### H6: Prompt Diversity (Text Variants)

Need 5 instruction file variants with semantically equivalent text:

| File | Variant Text |
|------|--------------|
| `detect_diverse_v1.md` | "Identify burial mound symbols in this map section" |
| `detect_diverse_v2.md` | "Detect tumuli markers on this topographic map" |
| `detect_diverse_v3.md` | "Find kurgan indicators in this image" |
| `detect_diverse_v4.md` | "Locate ancient burial mound cartographic symbols" |
| `detect_diverse_v5.md` | "Mark all mound features shown on this Soviet map" |

Plus corresponding configs pointing to each.

#### H9: Temperature Variants

Need 4 temperature conditions (same prompt, different config):

| Config Name | Temperature |
|-------------|-------------|
| `detect_image-only_temp-0.0.json` | 0.0 |
| `detect_image-only_temp-0.3.json` | 0.3 |
| `detect_image-only_temp-0.7.json` | 0.7 |
| `detect_image-only.json` | 1.0 (existing) |

### D.3 Methodology Specifications Needed (Not Prompts)

These require specifying *how* to construct, not the content itself:

| Item | Current Status | What's Needed |
|------|----------------|---------------|
| Hard positive examples | Procedure documented | Run procedure, document results |
| Hard negative examples (procedure-derived) | Procedure documented | Run procedure, document results |
| Image diversity pool | Procedure in H6 | Run baseline, collect FPs/FNs, document pool |
| Voting aggregation algorithm | Not specified | Document algorithm in Section 8.5 |
| Multi-model prompt adaptation | Not specified | May need format adjustments per provider |

---

## E. Questions Requiring Clarification

### E.1 Critical — RESOLVED

1. ~~**H3 testing status**~~: Confirmed as confirmatory. Will be tested.

2. ~~**Detection matching algorithm**~~: Documented in Section 4.1.2. Reference-centric approach is appropriate.

3. ~~**Cross-model output format**~~: Same JSON schema across all providers confirmed.

### E.2 Important — RESOLVED

4. [x] **Voting threshold for H4**: Resolved (2025-12-31). Full grid search across N ∈ {5, 10, 30} and T ∈ {1..N}. No a priori threshold; optimal found empirically. Full grid on Flash, subset on expensive models. Updated H4 test specification and Section 8.5 parameters.

5. [x] **H6 image resampling**: Resolved (2025-12-31). Each pass has distinct examples (no duplicates within a pass). Same example can appear in different passes, subject to frequency-capped random sampling (floor 20%, cap 60%). Full methodology in Section 8.4.3. Example-level effectiveness analysis added as secondary/tertiary analysis in Section 8.4.4.

6. [x] **Missing Rakovski null tile**: Confirmed intentional per selection protocol (2025-12-30).

7. [x] **Thinking parameters**: Resolved (2025-12-31). No principled equivalence exists across providers. Adopting descriptive approach: test each at provider-recommended "high reasoning" setting, report results with cost-performance analysis. Added Cross-Model Comparability and Cost-Performance Analysis subsections to Section 8.2.

### E.3 Minor — RESOLVED

8. [x] **Tile exclusion criteria**: Resolved (2025-12-30). Added to Section 8.6.

9. [x] **H8 baseline**: Resolved (2025-12-31). Using "Factorial Corners" approach (~14 conditions) as primary analysis, with pre-specified trigger conditions for escalating to secondary (bracketing/targeted expansion) or tertiary (full replication) analysis. Decision tree and success criteria documented in H8 section.

---

## F. Summary of Required Actions

### Before Registration — Document Structure (v2.7, COMPLETE)

- [x] Fix dates and version numbers (A.1) — 2025-12-30
- [x] Fix section numbering (A.2) — 2025-12-30
- [x] Correct Summary Table hypothesis mappings (A.3) — 2025-12-30
- [x] Fix encoding artefacts (A.5) — 2025-12-30
- [x] Update model IDs to match codebase (A.6) — 2025-12-30
- [x] Integrate answers from Section 12 into main text (B.1) — 2025-12-30
- [x] Clarify H3 testing status — confirmed as confirmatory — 2025-12-30
- [x] Specify detection matching algorithm — added Section 4.1.2 (Hungarian algorithm) — 2025-12-30
- [x] Add cross-model JSON schema note to Section 12.2 — 2025-12-30
- [x] Document voting aggregation algorithm in Section 8.5 — 20m distance-based clustering — 2025-12-30
- [x] Specify tile exclusion criteria — added to Section 8.6 — 2025-12-30
- [x] Add tile selection methodology — added Section 8.6 — 2025-12-30

### Before Registration — Methodology Specifications (v2.9, COMPLETE)

- [x] H4 voting: Specify full grid search across N ∈ {5, 10, 30}, T ∈ {1..N} — 2025-12-31
- [x] H6 sampling: Document frequency-capped random sampling methodology — Section 8.4.3 — 2025-12-31
- [x] Library composition: Document four-category structure — Section 8.4.1 — 2025-12-31
- [x] Example-level analysis: Add regression and BIBD framework — Section 8.4.4 — 2025-12-31
- [x] Hypothesis interactions: Add summary table — Section 8.4.5 — 2025-12-31
- [x] Cross-model comparability: Document reasoning parameter non-equivalence — Section 8.2 — 2025-12-31
- [x] Cost-performance analysis: Add framework for efficiency frontier reporting — Section 8.2 — 2025-12-31
- [x] H8 escalation: Add adaptive testing framework with triggers — H8 section — 2025-12-31
- [x] Implement voting aggregation code — `benchmark_variability.py` and `generate_union_candidates.py` — 2025-12-30
- [x] Codebase consistency review — all scripts now use 20m distance-based matching — 2025-12-30
- [x] Pairwise interaction testing: Add Section 8.4.6 with 48-condition factorial design — 2025-12-31
- [x] Text-image ordering constraint: Document aligned ordering, text precedes images — 2025-12-31
- [x] Escalation triggers: Define triggers for 3-way interaction testing — 2025-12-31
- [x] Cost estimation: ~$60-100 total, well under $250 trigger — 2025-12-31

### Before Registration — Prompt/Config Composition (COMPLETE)

- [x] Create ordering variant configs for H5 (3 configs) — skeleton configs created 2025-12-31
- [x] H9 temperature variants — no separate configs needed; temperature is a runtime parameter in the 48-condition factorial (Section 8.4.6) — 2025-12-31
- [x] Document prompt structure and H6 methodology (Section 8.3) — 2025-12-31
- [x] H6 text diversity — methodology documented with examples; final wording deferred to pre-holdout — 2025-12-31

### Before Holdout Evaluation (Post-Registration)

- [ ] Run hard example selection procedure on training tiles
- [ ] Document hard example selection results (which FPs/FNs selected, frequencies)
- [ ] Finalise library composition based on empirical selection
- [ ] Finalise H6 text diversity instruction files (5 variants) and commit to repository
- [ ] Upload finalised library to OSF
- [ ] Record API pricing at experiment start

---

## G. Clarifications from User

1. **Rakovski null tile**: Intentionally excluded. Selection protocol chose 3 tiles with Lesovo required; random selection excluded one map.

2. **H3 status**: Confirmed as confirmatory. Will be tested on holdout to validate preliminary finding that two-stage proposer-verifier degrades performance (contrary to literature recommendations).

3. **Detection matching**: Reference-centric algorithm documented in new Section 4.1.2. Current implementation is rigorous for this use case.

4. **Cross-model format**: Same JSON output schema will be used across all providers. Prompt adaptation only where API constraints require.

---

*Generated by Claude Code reviewing against codebase state as of 2025-12-30*
*Updated after applying corrections to preregistration.md v2.7*
