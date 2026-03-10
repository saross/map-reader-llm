# Two-Stage Detection: Comparative Verifier

A first-stage verifier has already assessed this candidate as a possible burial
mound. Your task is to **compare it feature-by-feature** against confirmed
burial mound examples shown below. Only confirm it as a mound if it shares the
key diagnostic features.

## Reference examples

You have been shown four confirmed burial mound images. Study them carefully.
The diagnostic features shared by all confirmed mounds are:

- **Rays**: Short lines radiating OUTWARD from the central shape, forming a
  "sunburst" or "gear" pattern
- **Central shape**: A small circle or oval (orange-brown), or a triangle or
  square (black) when a survey marker sits on the mound
- **Colour**: Typically orange-brown for the mound symbol itself; black for
  overlaid survey markers
- **Gestalt**: The overall visual impression — a compact, radially symmetric
  symbol distinct from surrounding map clutter

## Important warning

The presence of nearby text such as "кург." (abbreviation for kurgan/mound)
does NOT confirm a mound. Only the **visual symbol pattern** matters. Text
labels can appear near non-mound features or refer to features outside the crop
area.

## Your task

Compare the candidate (the last image) against the four confirmed mound
examples. For each diagnostic feature, state whether the candidate matches:

1. **Ray comparison**: Does the candidate have outward-radiating rays like the
   confirmed examples? Are the rays similar in length, density, and direction?
2. **Shape comparison**: Does the central shape match — small circle/oval, or
   triangle/square with marker?
3. **Colour comparison**: Is the colour consistent with confirmed mound symbols?
4. **Gestalt match**: Does the overall visual impression match a confirmed mound,
   or does it resemble something else (contour lines, text, boundary marks)?

## Output format

Return JSON:

```json
{
    "ray_comparison": "Description of how the candidate's rays compare to confirmed examples.",
    "shape_comparison": "Description of how the central shape compares.",
    "colour_comparison": "Description of how the colour compares.",
    "gestalt_match": "Overall visual similarity assessment.",
    "reasoning": "Synthesis of the four comparisons into a final judgement.",
    "mound_probability": 0.0
}
```

## Scoring guide

- **0.9–1.0**: Strong match on all four features — looks like the confirmed examples
- **0.6–0.8**: Matches most features but one is weak or ambiguous
- **0.3–0.5**: Mixed — some features match, others clearly differ
- **0.0–0.2**: Poor match — candidate lacks key diagnostic features of confirmed mounds
