# Two-Stage Detection: Adversarial Verifier

A detection system has identified the symbol at the centre of this crop as a
possible burial mound. Your task is to **find reasons it is NOT a burial mound**.

Assume the detection system made an error. Argue for the strongest non-mound
interpretation of this symbol. Only confirm it as a burial mound if you cannot
find a plausible alternative explanation.

## What burial mounds look like

Burial mound symbols have **short lines (rays) radiating OUTWARD** from a
central shape, forming a "sunburst" or "gear" pattern. The rays point away
from the centre, indicating elevated terrain. The central shape is typically
a small circle or oval in orange-brown, or a triangle or square in black
(when a survey marker sits on a mound).

## Common false alarms — argue for these first

Before confirming a mound, check whether the symbol could instead be:

- **A triangulation point without a mound**: A solid black triangle, possibly
  with a central dot — but with NO outward-radiating rays around it. These
  are extremely common on Soviet maps and frequently confused with mounds.
- **A benchmark without a mound**: A solid black square, possibly with a
  central dot — but with NO outward-radiating rays around it.
- **A contour feature**: Lines that approach or converge on a point, but the
  lines point INWARD (downhill flow) rather than radiating OUTWARD. These
  can appear in the same orange-brown colour family as mound symbols.
- **A vegetation or land-use boundary**: Small marks along a boundary line
  that may resemble rays but are actually boundary indicators.
- **Text or numbering artefact**: Partial Cyrillic characters or elevation
  numbers that coincidentally resemble radiating lines.
- **A spot height marker**: A small black dot (~5-7 pixels diameter) with a
  nearby elevation number. These are roughly half the size of the smallest
  mound symbol (≥12 pixels). If the symbol is smaller than ~10 pixels
  diameter, it is a spot height, not a mound.
- **A well or spring**: A blue circle, sometimes with concentric blue rings.
  Mound symbols are only orange-brown or black — never blue. Any blue
  circular symbol is a water feature.

## Decision process

1. Identify the strongest non-mound interpretation of the symbol.
2. Describe the specific visual evidence supporting that interpretation.
3. Only if NO non-mound interpretation is plausible, confirm as a mound.

## Output Format

Return JSON:

{
    "best_alternative": "The strongest non-mound interpretation of this symbol.",
    "alternative_evidence": "Specific visual features supporting the non-mound interpretation.",
    "reasoning": "Why you accept or reject the non-mound interpretation.",
    "mound_probability": 0.0
}

## Scoring Guide

- **0.9-1.0**: No plausible alternative — clear sunburst with outward rays
- **0.6-0.8**: The non-mound interpretation is weak but not impossible
- **0.3-0.5**: Genuinely ambiguous — mound and non-mound are equally plausible
- **0.0-0.2**: Strong non-mound interpretation — symbol is most likely something else
