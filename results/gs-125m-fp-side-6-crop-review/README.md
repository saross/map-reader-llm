# GS strict (>125 m) FP-side burial-mound 6-crop review

## What this is

Staging artefacts for a manual visual inspection task: the user reviews
six Gold Standard (GS)-side false positives (FPs) that the v2 burial-mound
FP-classifier (`scripts/gs-fp-classify.py`) labelled as `burial-mound` or
`triangulation-point-on-burial-mound` at the strictest distance stratum
(> 125 m from any curator ground-truth (GT) mound).

This is the headline "6 / 14 = 42.9 %" cell from
`results/gs-fp-classification/report.md` (line 25). The review answers
whether each of the six is a genuine missed mound (curator GT incomplete)
or a v2 prompt over-claim — relevant to the Limitations narrative around
curator-GT incompleteness and to Obs 307's prompt-bias caveat.

## Contents

- `index.md` — review interface. One section per candidate with the
  embedded crop, pre-filled context (sheet, coordinates, v2 label,
  v2 classifier confidence + rationale, distance to nearest curator GT
  mound), and a blank verdict block.
- `crops/cand_NNNNN_<sheet>.png` — six 768 × 768 px crop images, each a
  150 m × 150 m metric window upscaled via LANCZOS (matches the exact
  view the v2 classifier saw).
- `README.md` — this file.

## Cohort summary (the 6)

| # | candidate ID | sheet | v2 label | dist to curator GT (m) | confidence |
|---|---:|---|---|---:|---:|
| 1 | 54  | K-35-052-4_32635   | triangulation-point-on-burial-mound | 2 921.7 | 0.95 |
| 2 | 125 | K-35-052-4_32635   | triangulation-point-on-burial-mound | 1 721.2 | 0.95 |
| 3 | 168 | K-35-053-3_Elenovo | burial-mound                        |   192.0 | 0.95 |
| 4 | 349 | K-35-053-3_Elenovo | burial-mound                        |   427.7 | 0.85 |
| 5 | 531 | K-35-078-1_Lesovo  | triangulation-point-on-burial-mound | 3 385.0 | 0.95 |
| 6 | 562 | K-35-078-1_Lesovo  | burial-mound                        | 2 481.8 | 0.90 |

Spread across three of the four GS sheets (K-35-062-2_Rakovski had zero
FPs at this stratum). Two candidates per sheet on K-35-052-4_32635,
K-35-053-3_Elenovo, and K-35-078-1_Lesovo.

## Reviewer instructions

1. Open `index.md` in a Markdown viewer that renders relative-path image
   links (e.g. VS Code preview, GitHub web view, `glow`, `mdcat`).
2. For each of the six sections, inspect the crop and write one of three
   verdicts in the `Verdict` block:
   - `real_mound_curator_omission` — the symbol IS a burial mound; the
     curator GT is incomplete here. Strengthens the GT-incompleteness
     narrative (cf. today's two confirmed additions on the 55-map
     corpus).
   - `v2_overclaim` — v2 is wrong; the symbol is not a mound. Strengthens
     Obs 307's prompt-bias caveat.
   - `edge_case_ambiguous` — reasonable people could disagree. Document
     why in the `note:` line.
3. Optionally add a free-text `note:` to flag anything noteworthy
   (e.g. "real mound but the symbol is partly clipped by the tile
   boundary").

## Reproducibility

To re-render the six crops from scratch:

```bash
.venv/bin/python scripts/stage_gs_125m_fp_review.py
```

The script is idempotent (skips re-rendering crops that already exist)
and deterministic (no API calls; renders directly from
`inputs/rasters/*.tif` via the same `render_crop` function the v2
classifier used). Source of truth for the cohort selection is
`results/gs-fp-classification/fp_classifications.json` (filter:
`dist_to_nearest_curator_GT_m > 125` AND `category in
{"burial-mound", "triangulation-point-on-burial-mound"}`).

## Cross-references

- v2 FP-classification driver: `scripts/gs-fp-classify.py`
- v2 FP-classification results: `results/gs-fp-classification/`
- Working notes: `docs/notes/reflections/working-notes.md` — search for
  "Obs 307" (cross-corpus chi-square at v2) and "Obs 306" (TP-side
  closed-list expansion).
- Sibling 55-map review interface (Streamlit, larger 177-row cohort):
  `scripts/v2_burial_mound_bet_test_app.py`. Not used here — the GS
  cohort is small enough (6 items) that a static Markdown index is
  faster end-to-end.
