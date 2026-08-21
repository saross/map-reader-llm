# Tile-level precision, recall, and F1: a protocol-matched comparison with the only published VLM archaeological detection study

> **Last revised**: 2026-08-21 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Date**: 2026-08-21
**Author**: Claude Code (Opus 5), amd-tower — trivial arithmetic over committed
JavaScript Object Notation (JSON) artefacts, run locally
**Application Programming Interface (API) spend**: US$0.00 — no scoring pipeline
was re-run; every count below is read verbatim from a committed
`evaluation.json`
**Generator**: `scripts/derive_tile_level_f1.py` (JSON artefact
[`tile_level_f1.json`](tile_level_f1.json)); this prose document is
hand-authored around that artefact's numbers
**Tests**: `tests/test_derive_tile_level_f1.py` (17 tier-1 tests)

---

## 1. Why this document exists

The project's registered tile-level discrimination metric is the Matthews
Correlation Coefficient (MCC) over a 2 × 2 tile confusion matrix
(preregistration § 4.2). The only published zero-shot Vision Language Model (VLM)
archaeological detection study — Landauer & Klassen (2025),
[10.3390/geomatics5040052](https://doi.org/10.3390/geomatics5040052) — abandoned
localisation scoring because its models' bounding boxes were "relatively
inaccurate", and fell back to **per-tile binary classification** reported as
precision, recall, and F1. Its headline numbers (F1 0.41–0.67) are therefore not
on the same axis as this project's headline object-level, buffer-matched F1, and
they are not directly comparable to our MCC either.

This document closes that gap in the only way that costs nothing and risks
nothing: it re-expresses **the same committed tile confusion matrices** that back
our published MCC values as precision, recall, and F1, so that our tile-level
discrimination can be set beside theirs on a like protocol.

The metric is **supplemental**. It does not replace the registered MCC, and it
does not replace the object-level F1 that carries the study's primary claim. It
exists to answer one question a reviewer of the VLM literature will ask: *on the
task Landauer & Klassen actually scored, how does this pipeline do?*

## 2. Method, and the three traps it respects

The derivation is deliberately thin. It reads
`summary.tile_classification.confusion` from each committed evaluation artefact
and does arithmetic on those four integers. Nothing is re-scored, no geometry is
touched, and no matrix is reconstructed.

That thinness is the point. `docs/methodology/tile-mcc-explained.md` documents
three traps in this machinery, and the design honours each:

1. **The two axes book features to tiles by different rules** (trap 1).
   Detections are booked to exactly one tile under the erratum E79
   nearest-centroid rule; references are booked to *every* tile they intersect.
   Reference occupancy therefore cannot be recovered from the detection-level
   false-negative column — attempting it produced 0.898 against a committed
   0.790 on the very cell that heads our table. Because this derivation reuses
   the committed matrix rather than rebuilding it, the booking rules are
   inherited unchanged and the trap cannot fire.
2. **An undefined statistic is not a zero** (trap 2, erratum E81). Precision is
   undefined when `TP + FP = 0`; recall is undefined when `TP + FN = 0`; F1 is
   undefined when either is. Those cases emit JSON `null` with a named vanishing
   marginal, never `0.0`. A genuine `0.0` — model flagged tiles, none of them
   populated, both marginals non-zero — is distinguished from a missing value
   and is reported as a zero. No cell in this table is degenerate, but the
   discipline is enforced in code and in the tests.
3. **Tile-level numbers are carrier-specific** (trap 3). Every cell carries its
   tiling scope. The two carriers here are *not* interchangeable, and neither is
   interchangeable with Landauer & Klassen's.

### 2.1 The validation gate

Before any F1 is published from a matrix, MCC is recomputed from that same
matrix and required to reproduce the committed point estimate to at least four
decimal places. A cell that fails is withheld, not published with a caveat.

**All ten registered cells passed** (`n_passed: 10 / 10`). Agreement is exact to
floating-point precision for the eight 55-map cells, whose committed MCC is
stored at full precision; the two gold-standard cells store MCC rounded to four
decimal places, so their residuals are 4.76 × 10⁻⁵ and 2.69 × 10⁻⁶ — rounding
residue, not disagreement.

### 2.2 Carriers

| Carrier | Tile size | Sheets | Tiles | Bounds | Reference | Reference-positive tile share |
|---|---:|---:|---:|---|---|---:|
| Era-2 gold standard | 384 px (336 px stride) | 4 | 487 | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | `inputs/vectors/references/mounds-reference.geojson` — expert-digitised; 435 mounds in Era-2 scope | **0.4702** (229 / 487) |
| 55-map generalisation | 384 px, Era-2-style bounds | 55 | 8,541 | `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` | `inputs/vectors/references/canonical-gt-55maps-r50.geojson` — per-buffer gated composite over student-digitised records | **0.4126** (3,524 / 8,541) |

Bounds and reference paths are read from each evaluation artefact's own
`_metadata.input_files` / `cli_args`; scope sizes from
`results/evaluation-scopes.md` §§ 2 and 11.

Both prevalences are **natural**: they are what the tiling of these map sheets
produces, not a constructed positives-to-negatives ratio.

## 3. Derived tile-level metrics

Prevalence is the reference-positive tile share, `(TP + FN) / N`. "Committed MCC"
is `summary.tile_classification.mcc.point` (gold standard) or the bare-float
point estimate written by the Track-2 adapter (55-map). "Recomputed MCC" is
derived here from the same four counts.

### 3.1 Gold-standard cells (Era-2 carrier, 487 tiles)

| Cell | N | TP | FP | FN | TN | Prevalence | tile-P | tile-R | tile-F1 | Committed MCC | Recomputed MCC | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:--:|
| `verified-adv-text-consensus-16of30` (headline) | 487 | 188 | 11 | 41 | 247 | 0.4702 | 0.9447 | 0.8210 | **0.8785** | 0.7903 | 0.790252 | PASS |
| `verified-adv-image-baseline-pro-vf` (MCC crown) | 487 | 215 | 13 | 14 | 245 | 0.4702 | 0.9430 | 0.9389 | **0.9409** | 0.8887 | 0.888703 | PASS |

For orientation, the object-level (buffer-matched) F1 of these two cells at 20 m
is 0.8902 and 0.7309 respectively. The ordering **inverts** between the two
axes: the headline cell wins on locating individual mounds, the MCC crown wins
on telling a populated tile from an empty one. That is the documented
high-F1/low-MCC versus lower-F1/higher-MCC contrast, and it is a finding rather
than an inconsistency.

### 3.2 The 55-map canonical board (55-map carrier, 8,541 tiles)

Board: `55map-canonical-leaderboard-50m` and its MCC sibling
`55map-canonical-leaderboard-mcc-50m`; committed matrices in
`results/55maps-extended-gt-2026-06-07/<cell>/evaluation.json`.

| Cell | N | TP | FP | FN | TN | Prevalence | tile-P | tile-R | tile-F1 | Committed MCC | Recomputed MCC | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:--:|
| IM-k3 | 8541 | 2483 | 181 | 1041 | 4836 | 0.4126 | 0.9321 | 0.7046 | **0.8025** | 0.710410 | 0.710410 | PASS |
| T03-k3 (oracle) | 8541 | 2462 | 235 | 1062 | 4782 | 0.4126 | 0.9129 | 0.6986 | **0.7915** | 0.690330 | 0.690330 | PASS |
| TH7-k3 | 8541 | 2423 | 241 | 1101 | 4776 | 0.4126 | 0.9095 | 0.6876 | **0.7831** | 0.679609 | 0.679609 | PASS |
| TM-n10-k5 (uplift) | 8541 | 2309 | 175 | 1215 | 4842 | 0.4126 | 0.9295 | 0.6552 | **0.7686** | 0.672458 | 0.672458 | PASS |
| T03-k4 | 8541 | 2299 | 172 | 1225 | 4845 | 0.4126 | 0.9304 | 0.6524 | **0.7670** | 0.671071 | 0.671071 | PASS |
| TH7-k4 (carry-forward) | 8541 | 2261 | 158 | 1263 | 4859 | 0.4126 | 0.9347 | 0.6416 | **0.7609** | 0.666625 | 0.666625 | PASS |
| TM-k3 | 8541 | 2274 | 197 | 1250 | 4820 | 0.4126 | 0.9203 | 0.6453 | **0.7586** | 0.657958 | 0.657958 | PASS |
| TM-k4 | 8541 | 2150 | 159 | 1374 | 4858 | 0.4126 | 0.9311 | 0.6101 | **0.7372** | 0.641136 | 0.641136 | PASS |

Rows are ordered by tile-F1, which reproduces the MCC ordering of the board
exactly — all eight cells, no inversions. That is expected rather than
impressive: the eight matrices sit on one carrier with one reference, so their
prevalence and their reference-positive marginal are identical and only the
predicted column varies. The MCC-versus-F1 inversion that the board records
(IM-k3 is the sole MCC Tier-1 cell while ranking seventh of eight on
object-level F1) is a contrast between **tile-level** and **object-level**
scoring, not between two tile-level statistics.

### 3.3 Coverage

No cell was withheld. All ten listed cells exposed a tile confusion matrix in
their committed artefact and all ten passed the MCC reproduction gate, so no
matrix had to be reconstructed by re-scoring and none is reported as missing.

## 4. Comparison with Landauer & Klassen (2025)

Their per-experiment confusion cells are quoted in
`docs/methodology/research/lit-scout-detection-baselines-2026-08-21.md` (strand 3
table). P, R, F1, and MCC below are recomputed here from those counts; the
authors' own F1, as reported, is given in the final column for cross-checking.

| Study cell | Sensor / domain | Tile footprint | N | TP | FP | FN | TN | Prevalence | tile-P | tile-R | tile-F1 | tile-MCC | F1 as published |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GPT-4.1 — Bavarian castles | Bing satellite imagery | 150 × 150 m | 1379 | 244 | 101 | 135 | 899 | 0.2748 | 0.7072 | 0.6438 | **0.6740** | 0.5595 | 0.67 |
| Gemini 2.0 Flash — Bavarian castles | Bing satellite imagery | 150 × 150 m | 1379 | 144 | 2 | 235 | 998 | 0.2748 | 0.9863 | 0.3799 | **0.5486** | 0.5484 | 0.55 |
| GPT-4.1 — Angkorian temples | Satellite imagery | 140 × 140 m | 1100 | 57 | 98 | 43 | 902 | 0.0909 | 0.3677 | 0.5700 | **0.4471** | 0.3900 | 0.45 |
| Gemini 2.0 Flash — Angkorian temples | Satellite imagery | 140 × 140 m | 1100 | 32 | 23 | 68 | 977 | 0.0909 | 0.5818 | 0.3200 | **0.4129** | 0.3918 | 0.41 |
| GPT-4.1 — English hillforts | LiDAR hillshade | 768 × 768 m | 1300 | 286 | 813 | 14 | 187 | 0.2308 | 0.2602 | 0.9533 | **0.4089** | 0.1635 | 0.42 |
| Gemini 2.0 Flash — English hillforts | LiDAR hillshade | 768 × 768 m | 1300 | 149 | 66 | 151 | 934 | 0.2308 | 0.6930 | 0.4967 | **0.5786** | 0.4884 | 0.58 |

Five of the six recomputed F1 values reproduce the published figure to the
printed precision. The sixth — GPT-4.1 on hillforts — gives 0.4089 from the
authors' own counts against a published 0.42; the discrepancy is one percentage
point and its cause is not recoverable from the quoted cells. The count-derived
value is the one tabulated, with the published value beside it.

### 4.1 The two caveats that govern this table

**Caveat 1 — prevalence.** Landauer & Klassen's class balance is **constructed**:
each experiment pairs a fixed set of positive tiles with 1,000 randomly drawn
negatives, giving roughly 1:3 to 1:10 positives-to-negatives (0.2748, 0.0909, and
0.2308 positive share for castles, temples, and hillforts respectively). Ours is
the **natural** prevalence of the tiling — 0.4702 on the 4-sheet gold standard,
0.4126 on the 55-sheet generalisation corpus. Prevalence moves precision and F1
directly and moves MCC differently again, so the two sets of numbers are not on a
common scale even though both are "tile-level F1". A higher-prevalence corpus
makes tile-level precision easier to achieve, which is the direction that
flatters us; a corpus of drawn-at-random negatives makes the negative class
easier, which is the direction that flatters them. Neither correction can be
applied post hoc from the published counts.

**Caveat 2 — task domain.** Their three experiments are satellite imagery
(castles, temples) and LiDAR hillshade (hillforts); ours is scanned 1:25,000
Soviet-series topographic map sheets. Detecting a symbol a surveyor deliberately
drew is a materially different perceptual problem from detecting an eroded
earthwork in a digital elevation model or an overgrown site in optical imagery,
and their feature classes are large sites rather than small discrete symbols.
Their tile footprints (150 m to 768 m on a side) also differ from ours, so the
classification unit is not the same size of ground.

**Consequence.** This is a **discrimination-grain comparison**, not a
leaderboard. It establishes that the same *kind* of question — can the model
separate a tile that contains the target class from one that does not? — has been
posed of both pipelines, and reports what each answered on its own corpus. It
does not license a claim that one model is better than another, because the
corpora differ in class balance, sensor, feature class, and tile size
simultaneously.

## 5. Where our tile-level discrimination sits

Read conservatively, and with both caveats in force: on the tile-level binary
classification protocol that Landauer & Klassen adopted, this project's cells
score above the range they report. Their six model-by-experiment cells span
tile-F1 0.41 to 0.67, with the best (GPT-4.1 on Bavarian castles, 0.674) resting
on a constructed 27 % positive share. Our eight 55-map generalisation cells span
0.7372 to 0.8025 on 8,541 tiles at a natural 41 % positive share, and our two
gold-standard cells reach 0.8785 and 0.9409 on 487 tiles at a natural 47 %
positive share. Expressed as MCC — which is less sensitive to class balance than
F1, though not immune to it — the gap is of the same sign and similar size: 0.16
to 0.56 for their cells against 0.64 to 0.89 for ours. The consistent shape of
our advantage is on the **precision** side: our tile precision sits between 0.91
and 0.94 in every one of the ten cells, whereas theirs ranges from 0.26 to 0.99
and is bought, in the one case where it is high, at a recall of 0.38. The honest
summary is therefore that our pipeline discriminates populated from empty tiles
more reliably and far more stably than the published zero-shot VLM baseline does
on its corpora — while noting that a higher natural prevalence makes tile-level
precision easier for us than for them, that map symbols are an easier perceptual
target than eroded earthworks, and that this comparison is one of protocol grain
rather than of head-to-head performance.

## 6. Registration status

**Not registered.** Neither these derived metrics nor the derivation itself has
been entered in `results/analyses-manifest.md` or
`results/conditions-manifest.md`. First-class registration of tile-level
precision/recall/F1 as a project metric is a decision for the Principal
Investigator: it would add a third axis to the boards, would need its own
confidence intervals and tiering instrument to be usable for comparison rather
than description, and would need an explicit position on how it relates to the
registered § 4.2 MCC. Until that decision is taken, this directory is a
supplemental artefact cited by path, not a registered analysis.

## 7. Reproducing

```bash
# Dry run — prints the table, writes nothing
python scripts/derive_tile_level_f1.py

# Emit results/tile-level-f1/tile_level_f1.json
python scripts/derive_tile_level_f1.py --write

# Tier-1 tests
python -m pytest tests/test_derive_tile_level_f1.py -q
```

The script exits non-zero if any registered cell fails the MCC reproduction gate.

## 8. Sources

| Artefact | Role |
|---|---|
| `docs/methodology/tile-mcc-explained.md` | The three traps; definition of the tile confusion matrix |
| `results/analyses-manifest.md` / `.json` | Board membership for `55map-canonical-leaderboard-50m` and its MCC sibling |
| `results/conditions-manifest.json` | Condition identifiers and provenance pointers to the committed evaluations |
| `results/metric-leaderboards/55map-canonical-50m.{md,json}` | The published MCC-led 55-map board |
| `results/era1-pv-stage-d/384-consensus-text-high/evaluation.json` | Gold-standard headline matrix |
| `results/verifier-robustness/evals/verified-adv-image-baseline-pro-vf/evaluation.json` | Gold-standard MCC crown matrix |
| `results/55maps-extended-gt-2026-06-07/<cell>/evaluation.json` | The eight 55-map matrices |
| `results/evaluation-scopes.md` §§ 2, 11 | Carrier definitions and corpus sizes |
| `docs/methodology/research/lit-scout-detection-baselines-2026-08-21.md` | Landauer & Klassen confusion cells, as quoted and verified |
| `scripts/lib_advanced_metrics.py` (`calculate_tile_classification`) | Canonical tile-classification and MCC implementation |

## Changelog

### 2026-08-21 — Original publication

Derived tile-level precision, recall, and F1 for ten cells — the gold-standard
headline `pv-diag-384::verified-adv-text-consensus-16of30`, the gold-standard MCC
crown `verified-adv-image-baseline-pro-vf`, and the eight cells of the 55-map
canonical board — from the committed tile confusion matrices that back their
published MCC values. No scoring pipeline was re-run and no API spend was
incurred. All ten cells passed the MCC reproduction gate (agreement exact for the
eight full-precision 55-map values; residuals of 4.76 × 10⁻⁵ and 2.69 × 10⁻⁶ for
the two gold-standard values stored at four decimal places, consistent with
rounding). No cell was degenerate, so the undefined-cell discipline did not fire
in the data, though it is enforced in `scripts/derive_tile_level_f1.py` and
covered by `tests/test_derive_tile_level_f1.py`. Landauer & Klassen (2025) are
tabulated alongside, with their constructed prevalence and differing task domains
stated as caveats and the comparison framed as one of discrimination grain rather
than a leaderboard. Registration in the analyses and conditions manifests is
deliberately deferred to a Principal Investigator decision (§ 6).
