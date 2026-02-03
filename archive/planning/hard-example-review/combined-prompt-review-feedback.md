# Combined Prompt Review Feedback for CC

**Date**: 2026-02-03
**Source**: Opus strategic review of all 11 detection prompts, 2 two-stage prompts, review synopsis, and all 8 hard example images.

**Overall assessment**: Changes 1-4 are well-designed, well-motivated by the hard examples, and the two governing principles (descriptive language, VLM-resolution calibration) are sound. The hard example images confirm the changes address real failure modes. The following items need attention before finalising.

---

## Priority 1: Apply Changes 1-4 and centre-pointing to the two-stage prompts

`propose_brief.md` and `verify_brief.md` are still in their pre-hard-example state. Both are in scope for Stage 1-2 experiments.

**propose_brief.md** — treat as a variant of `detect_brief-text-image.md`:
- Add the standard centre-pointing sentence
- Update Guideline 2: "lines, shapes, or text" and "sunburst pattern remains discernible"
- Apply any terse-level exclusion additions if the proposer receives H5 content
- Keep the distinctive "a verifier will filter false positives" framing

**verify_brief.md** — different priorities given it receives a crop centred on a single candidate:
- Add the reference-example centre-pointing sentence for few-shot exemplars (the verifier already has "candidate symbol at the centre" for the target crop, but needs the same language for reference images)
- Add inward-marks distinction (Change 2A) and non-mound-round-shapes (Change 3) to the diagnostic criteria — these are core verifier discriminators
- Occlusion/clustering guidance (Changes 1, 4) is lower priority here since the verifier receives a pre-cropped candidate, but consider a brief mention

---

## Priority 2: Extend descriptive principle to remaining H5 exclusion sections

The existing verbose exclusion content in `_verbose` files still uses interpretive feature names that predate the descriptive principle. For consistency with Changes 1-4:

- **"Infrastructure Markers"** section: "Dots positioned on roads, bridges, rivers, or canals" → something like "dots positioned along linear features." The title could become "Dots on Linear Features" or similar.
- **"Contour Line Artefacts"** title: interprets what the features are. The body text is already fairly descriptive ("closed... lines on hilltops forming roughly circular patterns"). Consider retitling to "Closed Curved Line Patterns" or similar. Body text can stay.

Mixing descriptive and interpretive registers within the same prompt may subtly signal that the interpretive labels carry weight, encouraging the model to identify feature types rather than match visual patterns.

---

## Priority 3: Strengthen Change 2B (Cyrillic text confound)

HN 13 is the most dangerous hard negative in the library. The combination of "могила" (literally "burial mound" in Cyrillic) plus an orange-brown shape with marks creates a double-trigger — visual *and* textual false evidence. A VLM that can read Cyrillic may use the text as confirmation.

The current Change 2B framing ("text characters alone do not indicate a mound") treats this as one exclusion item among many. Two enhancements:

**a)** In the verbose exclusion subsection for Change 2B, explicitly state that map text near a candidate does not confirm or deny the visual diagnostic. The ray pattern is the sole criterion. The model should be actively discounting text as evidence, not merely noting that text "alone" is insufficient.

**b)** Consider adding a brief general principle to the verbose guidelines section (not buried in a specific exclusion category): something like "Base all detections on the visual sunburst diagnostic only. Map text, labels, and abbreviations near a candidate do not confirm or deny the presence of a mound." This covers the HN 13 case but also generalises to any future text-based confusion. For brief variants, the existing "the rays pointing outward are essential" may be sufficient — this addition is verbose-only.

---

## Priority 4: Verify Change 4A anti-satisficing language

The "if you find one, look carefully nearby" guidance for clustered mounds addresses a real VLM failure mode (confirmed by HP 06 and HP 08). But overly directive language could bias the model toward inventing additional detections near real ones, trading recall improvement for precision loss.

Frame as descriptive rather than directive: "Mounds commonly appear in groups where individual symbols vary in prominence — apply the ray diagnostic independently to each candidate" is better than "if you find one mound, look carefully for others nearby." The key is that every detection must independently satisfy the sunburst diagnostic, regardless of proximity to other detections.

---

## Priority 5: Keep "marks" vs "rays" distinction as-is

The open wording item in the synopsis — whether to use "inward-pointing rays or other marks" — should be resolved in favour of keeping "marks" for inward/non-radiating features and reserving "rays" exclusively for the positive outward-radiating diagnostic. This creates a semantic shortcut throughout the prompt: "rays" = positive signal, "marks" = not what you're looking for. Using "inward-pointing rays" would reuse the positive term for a negative feature, weakening the distinction.

---

## Priority 6 (lower, can be deferred): Decision Procedure step ordering

The verbose Decision Procedure (steps 1-6) instructs the model to check for rays (step 1) and classify subtypes (steps 3-4) *before* considering occlusion and degradation (steps 5-6). A VLM following this literally might reject an occluded symbol at step 1 for having no visible rays, before reaching the step 5 guidance that says to account for occlusion.

Restructuring so that occlusion/degradation caveats are integrated earlier — or framing as "check for sunburst pattern accounting for occlusion and degradation, then classify" — would be more robust. This is a non-trivial structural change, so it can be deferred to a subsequent review round if the current change set is already complex enough.

---

## Not requiring action

- **Brief:verbose ratio** is tracking well after Change 1 consolidation (1:2.9). Changes 2-4 will push verbose proportionally more, which should bring it to ~1:3.
- **"кург." in positive guidance vs exclusion text**: the synopsis wording handles this correctly (text alone is insufficient, not text is misleading). Just verify the implementation preserves this framing.
- **Text-only files with conditional reference-example language**: harmless, required by the text-modality consistency principle in the preregistration. Small token cost, no action needed.
- **HP crops are confirmed centred on target mound** per Shawn's correction. Additional mounds visible in HP 05, 06, 08 crops are non-target neighbours, which reinforces the value of centre-pointing language.
