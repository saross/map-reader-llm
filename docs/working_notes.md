# Research Notes: LLM-based Map Extraction

## Observation 1: "Going with the Grain"
Sometimes the model exhibits strong "impulses" to identify features that correlate with the target (e.g., elevation numbers, related symbols) even if not explicitly asked. Rather than suppressing these impulses to "simplify" the task, it is more effective to identify this "basin of attraction" and guide the model to exploit it.
- **Example**: Gemini strongly associates elevation numbers with burial mounds. Using this text as a confirmation signal ("scan for isolated elevation numbers") improves detection in cluttered areas where the visual symbol is obscured.

## Future Work / Paper Ideas
- **Target Journal**: Archaeological Prospection
- **Prompt Engineering**: Moving from "suppression of noise" to "exploitation of correlation".

## Observation 2: The "Grid Line" & "Proximity" Blindspots
Visual models often fail when a symbol is:
1.  **Bisected**: A strong linear feature (grid line, road) crossing the *center* of the symbol can break the "gestalt" of the circle, causing the model to see it as two halves or disparate noise.
2.  **Clustered**: Two symbols in very close proximity (touching or overlapping) are often aggregated into a single detection or skipped entirely if the "crowding" confuses the object detector's NMS (Non-Maximum Suppression) intuition.

**Recommendation**: Explicitly instruct the model to "separate" close neighbors and to "reconstruct" symbols bisected by lines.

## Observation 3: The "Bridge Decoy"
The model sometimes confuses black dots on roads (bridges/culverts) for "Benchmark on Mound" symbols, especially when they are near valid orange mounds. The linear feature (road) intersects it, which we encouraged in V2.2, but the key distinction is missing: **Bridges lack the "sunburst/spikes" and are strictly on the road axis.**

**Recommendation**: Add a specific negative constraint for "Black dots on roads or stream crossings (bridges/culverts) that lack radiating spikes."

## Observation 4: The Strictness Trade-off (False Negatives)
In V2.3, we added strict "Hollow Circle" and "Always Orange" constraints to eliminate black dots (bridges). This successfully killed the false positives.
**The Cost:** We missed one small, heavily obscured mound.
**Hypothesis:** Heavily intersected mounds (covered by black grid/road lines) or very small mounds may appear "filled" or "broken" to the model, failing the strict "hollow circle" check.
**Strategy:** Do not relax the constraint yet. Proceed to larger validation. If this is a rare outlier (~1/100), we accept the loss to maintain high precision. If systematic, we will need to soften "Hollow" to "Usually hollow".

## Observation 5: Pareidolia & The "Unrolled Mound"
The V2.3 prompt is highly sensitive to "spikes". This has created two new classes of False Positives:
1.  **The "Unrolled Mound" (Embankments/Scarps)**: Linear black lines with hachures (ticks) look like "straight mounds" to the model. It sees the spikes and triggers, ignoring the "circular" requirement.
2.  **Pareidolia on Numbers**: The curly shapes of numbers (especially '2', '3', '6', '8', '9', '0') are sometimes hallucinated as "hollow circles".

**Recommendation**:
- Explicitly exclude "Linear features with spikes (embankments/cliffs)".
- Explicitly exclude "Numbers and Text characters".
- Reinforce that the symbol must be a *CLOSED* circle.

## Observation 6: Label Confusion (The "Number" Decoy)
Despite the "Anti-Number" rule in V2.4, the model continues to box numbers (e.g., "2", "3") as mounds.
**Root Cause:** The model is confusing the *label* (which correlates with the mound) for the *object itself*, especially when the actual mound is small or obscured. It sees the number, knows it's related to a mound, and boxes the number.
**Fix (V2.5):** We must explicitly teach the model the **spatial relationship**: "The number is a LABEL. The mound is the SYMBOL NEXT TO IT. Do not box the number."

## Observation 7: The "Blob" Decoy
V2.4 introduced a false positive on a "black blob" (likely a building) intersected by a contour.
**Fix (V2.5):** Strengthen the "Geometric Regularity" constraint. "Mounds are distinct geometric symbols (circles/triangles/squares), not irregular blobs."

## Observation 8: The "Anti-Number" Paradox (V2.6 Regression)
Attempting to explicitly separate "numbers" from "mounds" in Prompt V2.6 (by listing digits as false positives and enforcing "No Spikes = No Mound") paradoxically **increased** the rate of false positive number detections.
**Hypothesis:** By repeatedly mentioning "numbers" and "digits" in the negative constraints, we may be priming the model's attention towards them. The model sees the number, recognizes it is "salient" (because the prompt talks about it), and then fails to apply the negation logic correctly, boxing the salient object.
**Conclusion:** V2.5 remains the most robust prompt so far. It seems better to rely on the positive definition of the mound (Sunburst) and a lighter touch on labels, rather than an aggressive negative focus on numbers. Numbers are "sticky" false positives.

## Observation 9: The Visual Prompt Breakthrough (Phase 3)
Switching to a "Visual Few-Shot" approach (Prompt V3 + Reference Images) yielded a significant breakthrough in handling "Label Confusion".
- **Result:** on the challenging tile, the model produced **ZERO false positive numbers**. The visual examples effectively communicated "Mounds have spikes, numbers do not" in a way that text constraints (V2.6) failed to do.
- **Trade-off:** We observed a drop in recall for simple "Burial Mounds" (simple orange circles) while complex "Triangulation Mounds" (matching the legend reference perfectly) were detected.
- **Hypothesis:** The model is now over-fitting to the *exact visual style* of the Legend crop.
- **Next Step:** To recover recall, we need to supply "Real World" reference crops (valid detections from previous runs) alongside the idealized Legend crop.

## Observation 10: The Few-Shot Success (Phase 4)
Building on the visual breakthrough, we moved from "One-Shot" (Legend only) to "Few-Shot" by adding just **two** real-world positive examples (one simple mound, one benchmark variant).
- **Result:** Dramatic restoration of recall. The model went from finding ~50% of mounds (mostly complex ones) to **100% recall** across 5 random tiles (18 detections vs 10 previously).
- **Efficiency:** The correction was extremely efficient. We didn't need hundreds of examples; just providing *one* alternative view for each sub-class was enough to bridge the "Legend-to-Reality" gap.
- **Precision (Phase 5):** To handle the single remaining false positive type (degraded labels resembling mounds), we introduced a "Negative Example" class. Instead of describing "don't detect noise," we simply showed the model an image of said noise with the instruction "IGNORE". This proved far more effective than text constraints.
- **Conclusion:** Visual Few-Shot Prompting is definitively superior to Text-Only prompting for this task. It bypasses the difficulty of describing "sunburst shape" in words and robustly ignores numbers without "anti-number" paradoxes.
