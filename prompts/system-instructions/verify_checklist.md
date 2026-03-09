# Two-Stage Detection: Feature Checklist Verifier

A detection system has identified the symbol at the centre of this crop as a
possible burial mound. Evaluate it by checking each diagnostic feature
independently, then make an overall judgement.

## Feature Checklist

Score each feature before making your final judgement:

### 1. Outward-radiating rays

Does the symbol have short lines (rays) radiating **outward** from a central
point? This is the single most important diagnostic feature. Rays must point
AWAY from the centre, not toward it.

- **Present**: Clear rays radiating outward — strong mound indicator
- **Ambiguous**: Some marks near the centre, but direction unclear
- **Absent**: No outward-radiating lines visible — likely NOT a mound

### 2. Central shape and colour (orange-brown symbols)

If the symbol is orange-brown: does it have a central circle or oval shape?

- **Yes**: Orange-brown circle/oval with outward rays — classic burial mound
  or settlement mound pattern
- **No circle but has rays**: Unusual but still possibly a mound
- **Orange-brown marks but no circle and no rays**: NOT a mound — likely a
  contour feature, boundary mark, or other terrain indicator

### 3. Central shape and colour (black symbols)

If the symbol is black: does it have a central triangle or a central square?

- **Black triangle with outward rays**: Triangulation point ON a mound
- **Black square with outward rays**: Benchmark ON a mound
- **Black triangle WITHOUT outward rays**: Triangulation point alone — NOT a mound
- **Black square WITHOUT outward rays**: Benchmark alone — NOT a mound

### 4. Size

Is the symbol size consistent with mound map symbols (roughly 10-20 pixels in
diameter for the central shape, with rays extending slightly beyond)?

- **Consistent**: Appropriate size for a mound symbol
- **Too large**: May be a settlement or other large feature
- **Too small**: May be a dot, noise, or spot height marker

### 5. Confusable symbol check

Could this symbol be one of the following non-mound features?

- A solid black triangle with no outward rays (triangulation point alone)
- A solid black square with no outward rays (benchmark alone)
- Lines pointing inward toward a central point (contour feature, not mound)
- A small dot with a nearby number (spot height marker)
- Part of a text label or elevation number
- Marks along a linear boundary (vegetation or land-use boundary)

## Output Format

Return JSON:

{
    "checklist": {
        "outward_rays": "present | ambiguous | absent",
        "central_shape": "Description of what you observe",
        "colour": "orange-brown | black | other",
        "size": "consistent | too_large | too_small",
        "confusable_match": "none | Description of which confusable it resembles"
    },
    "reasoning": "Overall assessment based on checklist results.",
    "mound_probability": 0.0
}

## Scoring Guide

- **0.9-1.0**: Rays present + correct shape + correct colour + correct size +
  no confusable match
- **0.6-0.8**: Most features present but one is ambiguous
- **0.3-0.5**: Mixed evidence — some features present, some absent or ambiguous
- **0.0-0.2**: Key features absent (especially rays) or strong confusable match
