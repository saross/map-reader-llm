# Whole-file own-sheet padding audit (55-map r2 reference)

> **Last revised**: 2026-11-19 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **What**: every reference in `best-available-gt-55maps-r2.geojson` (5,018
  references, 55 sheets) measured on its own labelled sheet's source scan. A
  reference is flagged when its 9 × 9 pixel window there is entirely near-black
  (RGB ≤ 8). This extends the seam check (`../dry-run.md` §§ 2–2.4), which
  measured only references that touch another sheet's tile.
- **Script**: `inspect-reference-padding.py`, written by Astra (GPT, OpenAI
  Codex) and copied here unchanged. It was run on zbook on 2026-11-19 at the
  PI's approval with one change, the hard CPU ceiling raised from 25 s to 900 s
  for the zbook run (12.1 CPU-seconds used). It is read-only, uses the
  containing-pixel convention (`rasterio` `index`), and does not score,
  adjudicate symbols, or change references.
- **Output**: `padding-audit-summary.json` lists the flagged references with
  provenance anchors (reference commit `ef18e4e76`, file and script hashes).
  The full per-reference output is regenerable in about 10 s.

## Result

- **33 references** have an entirely near-black 9 × 9 window on their own
  sheet: 24 graded `directly_reviewed` and 9 `out_of_scope`.
- **27 of them are already in the seam-contact set** (24 directly reviewed, 3
  out of scope).
- **6 are new, all graded `out_of_scope`**, in pairs on three sheets that the
  seam check did not reach: `student:02861` and `02862` (Radetski),
  `student:01823` and `01824` (Asenovgrad), and `student:02684` and `02685`
  (Radnevo).
- Whether those six enter scoring depends on the pipeline's scope selection,
  not on the confidence label; that has not been checked. As in the seam
  audit, padding at the coordinate is a pixel fact, not evidence of a sheet
  label error, a displaced counterpart, or any score change.

## Changelog

### 2026-11-19 — Original publication

The PI approved running Astra's prepared audit. Results recorded as above.
