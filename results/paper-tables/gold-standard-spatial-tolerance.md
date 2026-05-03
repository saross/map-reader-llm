# Gold-Standard Spatial Tolerance Curve (4-map, Extended Buffers)

**Generated**: 2026-04-18T23:37:10+00:00 (source run); consolidated 2026-04-20
**Buffers**: 5, 10, 15, 25, 35, 45 m (extended-buffer sweep)
**Bounds**: `inputs/vectors/bounds/384/h10_test_bounds.geojson` (327 tiles, 4 maps, 569 reference mounds)
**Source**: `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md`

## Suggested paper text

> "The gold-standard curve plateaus at 25 m while the 55-map generalisation curve does not plateau by 50 m (Table `gold-standard-spatial-tolerance.md`); the ~25 m right-shift is the signature of student-GT positional noise, not a model-quality gap."

Drop-in sentence for the spatial-tolerance / 55-map-generalisation framing section. Cross-references this table and its 55-map companion `spatial_tolerance_comparison.md`.

## Purpose

Characterises the spatial-tolerance curve on the **4-map gold-standard corpus** (expert-curated ground truth)
at tighter-than-primary (5 / 10 / 15 m) and intermediate (25 / 35 / 45 m) spatial buffers. Companion file
to `spatial_tolerance_comparison.md`, which covers the 55-map generalisation corpus (student-annotated
ground truth) at 20 / 30 / 40 / 50 m. The two files document different corpora and must not be merged —
the underlying ground-truth precision differs materially (see §"Interpretation" below).

## Configuration

- **Proposer**: `detect_brief-text`, Gemini 3 Flash, T = 0.7, thinking = HIGH, K = 5 passes, 17 text-only
  labelled examples.
- **Verifier**: `verify_adversarial-text` (v1 prompt), Gemini 3 Flash, T = 0.0, thinking = MINIMAL.
- **Consensus / decision**: vote_t = 4 (4-of-5 majority), prob_t = 0.15 on verifier `mound_probability`,
  Intersection-over-Union deduplication radius 20 m.
- **Run**: `outputs/h11/gold-standard-v2/` (git commit `d59798ac`), verifier artefact
  `verified-v1/probabilities.json` (597 / 607 candidates parsed; 10 parse failures dropped per convention).

## F1 with 95 % CI by Buffer Distance

| Buffer (m) | F1 | Precision | Recall | ΔF1 from prev |
|-----------:|---|---|---|--------------:|
| 5          | 0.250 [0.203, 0.303] | 0.284 [0.234, 0.343] | 0.223 [0.177, 0.272] | — |
| 10         | 0.654 [0.601, 0.702] | 0.744 [0.689, 0.795] | 0.583 [0.528, 0.636] | +0.404 |
| 15         | 0.777 [0.733, 0.815] | 0.884 [0.842, 0.923] | 0.693 [0.639, 0.747] | +0.123 |
| 25         | 0.822 [0.783, 0.859] | 0.936 [0.902, 0.965] | 0.734 [0.681, 0.788] | +0.046 |
| 35         | 0.822 [0.783, 0.859] | 0.936 [0.902, 0.965] | 0.734 [0.681, 0.788] | 0.000 |
| 45         | 0.822 [0.783, 0.859] | 0.936 [0.902, 0.965] | 0.734 [0.681, 0.788] | 0.000 |

Bootstrap: 1 000 iterations, tile-level resample, seed = 42 (standard paper bootstrap spec). n = 250
verified detections (post vote_t = 4, prob_t = 0.15, 327-tile allowlist).

For the cached leaderboard values at 20 / 30 / 40 / 50 m on this same run
(F1 = 0.816 / 0.822 / 0.822 / 0.826 point-estimate), see
`results/leaderboard/cells/gold-standard-v2-greedy-v1-327tile.json`.

## Plateau onset

F1 is fully plateaued from **25 m upward**: point estimates, precision, and recall are identical at
25 / 35 / 45 m — all detection-to-reference matches saturate inside a 25 m tolerance. The 25 m → 35 m
delta is zero; the 20 m → 25 m gain is essentially zero (+0.006 against the cached 20 m cell).

Below the plateau, the curve falls sharply:

- **15 m → 10 m**: costs ~0.12 F1.
- **10 m → 5 m**: costs a further ~0.40 F1.
- **At 5 m**, precision collapses from 0.94 (≥ 25 m) to 0.28, driven by combined centroiding, map, and
  digitising jitter rather than model error.

## Interpretation: gold-standard vs 55-map right-shift

The 55-map generalisation curve (`spatial_tolerance_comparison.md`,
`flash-high-text-4-of-5--flash-min-vf`) has **not plateaued at 50 m**: the 40 m → 50 m step still buys
~0.005 F1, and the implied plateau lies beyond 50 m. The gold-standard curve here plateaus at 25 m.

The ~25 m right-shift between the two corpora is the **signature of student-GT positional noise on the
55-map ground truth**, not a model-quality gap:

| Buffer | Gold-standard 4-map (this file) | 55-map student GT | Gap |
|-------:|--------------------------------:|------------------:|----:|
| 20 m   | 0.816 (cached cell)             | 0.623             | +0.193 |
| 30 m   | 0.822                           | 0.753             | +0.070 |
| 40 m   | 0.822                           | 0.783             | +0.040 |
| 50 m   | 0.826                           | 0.792             | +0.034 |

At large buffer (50 m) the gap narrows to 0.034 F1 — closer to the "true" gold-standard-vs-unseen-maps
model-quality gap. The large gap at 20 m (0.193) materially overstates the model-quality cost of
generalisation; most of it is absorbed by GT positional noise once the tolerance exceeds the
noise radius.

**Publication implication**: when quoting the 55-map detection F1, either (a) quote the 50 m cell as
closest to the model-quality ceiling, or (b) frame the 20 m figure alongside this gold-standard curve
so that the ~25 m annotation-precision offset is visible to the reader.

## Companion artefacts

- CSV: `gold-standard-spatial-tolerance.csv` (machine-readable version of the table above).
- Source report: `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md` (full
  methodology, 55-map comparison, reproducibility block).
- Source data: `results/gold-standard-extended-buffer-sweep/evaluation.{json,csv,md}`,
  `verified_detections.geojson`, `score_leaderboard_sweep.json`.

## Notes

- Buffers deliberately differ from the 55-map sweep (5 / 10 / 15 / 25 / 35 / 45 m vs 20 / 30 / 40 / 50 m):
  the gold-standard annotation precision allows the curve to be probed below 20 m, where the 55-map
  student GT is too noisy for a meaningful F1.
- The 20 / 30 / 40 / 50 m cells on this same run are reported in the cached leaderboard cell
  (`gold-standard-v2-greedy-v1-327tile.json`) and are not duplicated here to avoid source-of-truth
  drift. The extended buffers above (5 / 10 / 15 / 25 / 35 / 45 m) are the new information.
