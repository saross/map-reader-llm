# Hard Example Library: Decisions and Path Forward

**Date**: 2026-02-02
**Context**: Synopsis of decisions made during strategic review (Shawn + Opus) for CC to incorporate into implementation. All decisions are consistent with the submitted preregistration (v4.6).

---

## 1. Hard Example Crop Sizing

**Decision**: Use **128×128 pixel crops** as the starting default for both hard positives (HPs) and hard negatives (HNs).

**Rationale**:
- At 128×128, a 15-20px symbol occupies ~1-2.5% of crop area — visually prominent as an exemplar while providing ~6-8× diameter of surrounding context (terrain, adjacent symbols, contour lines).
- The 300×300 figure from the literature review is driven by VLM *minimum input size* specifications, but those apply to *target images being analysed*, not reference exemplars. VLMs will upscale 128×128 reference images internally; this is acceptable since the model isn't detecting *within* the exemplar — it's learning *from* it.
- Maintains visual distinctiveness across the three exemplar tiers: tight canonical crops (~64px) < hard examples (128px) < null tiles (512×512).
- Canonical legend crops are already tight and working. Hard examples need more context than canonicals (to show real-world difficulty) but not dramatically more.

**Negative examples**: Use **identical 128×128 crops**, centred on the confusable feature that triggered the false positive. Negative difficulty should come from visual similarity, not size differences. This is consensus across metric learning and contrastive learning literature.

**Future exploratory**: Note as a potential exploratory variable to test 64, 128, 256, and 512 crop sizes for exemplars. Not for confirmatory trials. Mixed sizes within a single library are not recommended at this stage (the theoretical motivation from SimCLR doesn't transfer to frozen VLMs).

**Watch for during early runs**:
- If the model consistently misidentifies HPs in context-heavy areas → signal to increase crop size.
- If it struggles to distinguish HPs from HNs → signal that crops may be too similar, try tighter.

---

## 2. Centre-Pointing Language in Prompts

**Decision**: Add a descriptive centre-pointing statement to all detection prompt preambles, applied uniformly across all H5 conditions.

**Implemented language** (identical in all 11 prompt files):

> Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples.

**Revision note**: The initial recommendation ("centred on the relevant feature") was revised because "relevant feature" is ambiguous for negatives — the model might interpret it as a nearby mound rather than the confusable non-mound at the crop centre. The revised wording explicitly ties the label to the centred feature. Uniform application across H5 levels preserves factor orthogonality (centre-pointing is spatial orientation, not diagnostic text).

**Rationale**:
- At 128×128, crops may contain 2-3 mound symbols if they cluster. Without centre-pointing, the model may latch onto an easy neighbouring mound instead of the difficult target HP.
- For HNs, a crop centred on a confusable symbol may also contain a real mound at the periphery. Labelling the whole image "Negative" without centre-pointing sends a contradictory signal.
- The Stage 2 verifier prompt already uses "candidate symbol in the centre" language, so this is consistent with existing design.
- Frame as *descriptive* ("each image is centred on...") rather than *imperative* ("look at the centre of...") to avoid biasing spatial scanning during detection.

**Watch for**: Spatial bias in detections clustering toward tile centres. This would suggest the centering instruction is bleeding from exemplar interpretation into detection behaviour. Low risk given that detection prompts explicitly say "scan the target image," but worth monitoring.

---

## 3. Localisation vs Recognition Error Classification

**Decision**: Use a **50m distance threshold** to separate localisation errors from recognition failures. Exclude localisation errors (< 50m) from hard example libraries.

**Empirical basis**: CC's analysis shows a distributional cliff between 30m and 50m in the FN distance distribution. Below 30m: clear localisation territory. 30-50m: ambiguous. Above 50m: almost certainly genuine recognition failures. The cliff itself is the evidence for the threshold.

**Rationale for excluding localisation errors**:
- Few-shot libraries teach the model *what to look for*. A recognition FN is a mound the model couldn't identify — showing it as an HP directly addresses that gap.
- A localisation FN is a mound the model *did* recognise but placed incorrectly. Showing more examples of already-recognised mounds won't fix coordinate prediction — that's an architectural limitation, not a pattern-matching failure.
- Similarly, "phantom" FPs from localisation errors aren't genuine confusable symbols. Including them as HNs would teach the model to avoid random map patches, which is uninformative and potentially confusing.
- Excluding localisation errors is consistent with the design principle of building libraries empirically from detection results, minimising manual judgment calls.

**Resulting pool sizes** (at 50m threshold):

| Category | Available | Selected for Scale-8 | Available for expansion |
|----------|-----------|---------------------|------------------------|
| HP       | 4         | 4                   | 0                      |
| HN       | 46+       | 4                   | 42+                    |

---

## 4. Implications for H8 Library Scaling

The HP pool is **structurally exhausted at 4**. This has specific consequences for H8 conditions:

| H8 Condition | HP | HN | Status |
|---|---|---|---|
| Pure Positive Canon | 0 | 0 | ✅ Runs as designed |
| Canonical | 0 | 0 | ✅ Runs as designed |
| +HP | 4 | 0 | ✅ Runs as designed |
| Scale-4 | 2 | 2 | ✅ Runs as designed |
| Scale-8 | 4 | 4 | ✅ Runs as designed |
| Scale-16 | 8 | 8 | ❌ Capped — collapses to Scale-8 under 1:1 constraint |
| Scale-32 | 16 | 16 | ❌ Capped — collapses to Scale-8 under 1:1 constraint |

**Testable contrasts**:
- ✅ C1: Pure Positive Canon → Canonical (does Canon- help?)
- ✅ C2: Canonical → +HP (do HP help?)
- ✅ C3: +HP → Scale-8 (do HN help?)
- ✅ S1: Scale-4 → Scale-8 (initial scaling value)
- ✅ B1: +HP vs Scale-4 (composition vs size at matched total)
- ❌ S2: Scale-8 → Scale-16 (deferred to post-H10)
- ❌ S3: Scale-16 → Scale-32 (deferred to post-H10)

This is explicitly anticipated by the preregistration (line 815): "If fewer than 16 distinct HPs or HNs are available, Scale-32 (and possibly Scale-16) will be capped at the maximum available while preserving 1:1 ratio."

---

## 5. Experimental Sequencing

### Run now (Stage 1, current HP/HN pools):

1. **H1-H8 confirmatory hypotheses** — using the available pools. H8 scaling tests S1 through Scale-8; S2/S3 deferred.
2. **H9 (diversity)** — run as HN-diversity-only test. HP is frozen (4 slots, 4 examples, every HP appears in every pass). HN rotation is the more important diversity dimension given that FPs are the larger problem. Document that HP diversity is untestable due to pool exhaustion.

### Defer until after H10:

3. **H12 (HP:HN ratio)** — with HP capped at 4, the only testable ratios are HP-constant with varying HN (4:4, 4:8, etc.), which confounds ratio with total count. Alternatively, reducing HP below 4 discards known-useful information. Defer until H10 expands the HP pool so the full symmetric design can run.

### Run after Stage 2 completion:

4. **H10 (training pool expansion)** — expand calibration tile set using reserve tiles (permissible after Stage 2 evaluation). Rebuild libraries from larger pool. This should unlock Scale-16/32 for H8 scaling, the full H12 ratio test, and HP diversity for H9.

### Sequencing rationale:
- H9 before H10: the HN diversity result is immediately actionable for voting configuration in all subsequent experiments.
- H12 after H10: deferring produces a more informative, symmetric test.
- The composition question (H8 C1-C3) is arguably more important for practitioners than the extended scaling curve (S2-S3), and is fully testable now.

---

## 6. Key Finding to Document

The structural asymmetry between HP and HN pools is itself a reportable finding. It indicates the model's primary weakness at baseline is **precision** (too many false alarms, hence abundant HN candidates) rather than **recall** (missing mounds, hence few HP candidates). If this holds through confirmatory trials, it has practical implications: a model that over-detects but needs human filtering is operationally different from one that silently misses features.

---

## 7. Open Items

- [x] Extract 128×128 HP crops centred on the 4 recognition-failure FNs (>50m threshold) — Done (Session 7)
- [x] Extract 128×128 HN crops centred on the confusable feature for each selected FP — Done (Session 8)
- [x] Add centre-pointing language to detection prompt preamble — Done (Session 8, all 11 detect_*.md files)
- [x] Document the 50m threshold decision and distributional cliff evidence — Done (Session 8, Decision 11 in decisions-log.md)
- [x] Update H8 implementation to reflect Scale-16/32 capping — Done (Session 8, library_scale-16.json and library_scale-32.json marked deferred)
- [x] Document HP/HN asymmetry finding — Done (Session 8, Observation 85 in working_notes.md, Decision 11 in decisions-log.md)
- [x] Confirm H9 implementation handles frozen HP channel — Done (Session 8, noted in hypothesis-tracking.md H9 section)
- [x] Flag H12 as deferred in execution tracking — Done (Session 8, hypothesis-tracking.md updated)
