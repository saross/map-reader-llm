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
