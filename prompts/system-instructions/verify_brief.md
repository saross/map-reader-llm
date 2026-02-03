# Two-Stage Detection: Verifier

Classify whether the candidate symbol at the centre of this crop is a burial mound.

## Diagnostic Criteria

Mound symbols have **rays (hachures) radiating OUTWARD** from a central shape ("sunburst" pattern). This indicates elevated terrain.

**Key tests:**

1. Are there rays radiating from a central point? No rays → not a mound.
2. Do rays point OUTWARD (mound) or are there marks pointing INWARD (not a mound)? Inward marks may appear in orange-brown, the same colour family as mound symbols.
3. Check central shape: circle/oval (plain mound), triangle (triangulation on mound), square (benchmark on mound).
4. Check colour: orange-brown (plain mound) or black (survey marker on mound).
5. Is the shape round or ovoid in mound-like colours but without outward-radiating rays? Dark marks within the shape rather than extending outward → not a mound.
6. Does nearby Cyrillic text (e.g., "могила", "кург.") appear to confirm the candidate? Text does not confirm or deny — the ray pattern is the sole criterion.

If reference examples are provided, compare the candidate against them. Each reference image is centred on the feature being labelled.

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
