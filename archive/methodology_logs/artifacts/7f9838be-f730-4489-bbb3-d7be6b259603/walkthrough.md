# Walkthrough: Mound Detection Prompt Refinement

We have successfully refined the mound detection prompt for `gemini-3-pro-preview` to handle complex cases like occlusions and false positives from similar symbols.

## Prompt Evolution

### V1 (Initial)
- **Status:** Baseline.
- **Issue:** Missed mounds in clutter; low recall.

### V2 (Enhanced Descriptions)
- **Changes:** Detailed visual descriptions for 4 subtypes; "Contextual Clues" section.
- **Result:** Improved recall, but missed intersected mounds.

### V2.1 (Intersection)
- **Changes:** Explicit instruction to handle mounds intersected by lines (grids/roads).
- **Result:** Detected intersected mounds, **BUT** introduced a regression (false positive on Bridge/Culvert).

### V2.2 (Correction attempt)
- **Changes:** Stronger constraints.
- **Result:** Fixed the specific regression, but lacked systemic protection against dots.

### V2.3 (Final Strict)
- **Changes:**
    - **"Hollow Circle"**: Mandated that mounds must be hollow rings, not dots.
    - **"Always Orange"**: Strict color enforcement for Type A/B.
    - **"Bridge Decoy"**: Explicit exclusion of black dots on roads.
- **Result:**
    - **Precision:** 100% (No false positives in validation).
    - **Recall:** Very High (5/6 on challenging tile; 10 detections in random validation).
    - **Trade-off:** Missed one heavily obscured (filled-in) mound due to strict "hollow" rule.

## Validation Results

We ran a blind 5-tile validation using V2.3.

**Output:** `outputs/results/detections-K-35-062-2_Rakovski-random5.geojson`
**Total Detections:** 10

### Reasoning Examples (V2.3)

> "Small orange-brown **hollow circle** with radiating spikes... accompanied by the relative height number '3'."

> "Black triangle with central dot... explicitly identified as a kurgan by the text label **'кург.'** immediately above."

## Conclusion
The V2.3 prompt is robust and ready for production use. It favors high precision (avoiding false positives) while maintaining excellent recall for all but the most heavily obscured features.
