# Phase 0.3 — the 256 px premise on a common footprint

> **Last revised**: 2026-08-19 (original publication). See [§ Changelog](#changelog)
> for revision history.

**Classification**: POST-HOC (E41-class). This re-scores committed detections on
a corrected evaluation footprint. It is not a registered test and must not be
reported under a registered hypothesis.

## The question

The recall-levers programme records a premise that 256 px tiling "swamps the
verifier", and that premise currently constrains the design: it is the reason
for caution about pushing the proposer towards higher recall. The premise rests
on a cross-scope comparison. `pv-diag-256::verified-adv-text-consensus-5of5`
publishes F1@20 m = 0.8558 on scope `px256-1032`, while
`pv-diag-384::verified-adv-text-min-6of10` publishes 0.8835 on `era-2-487`.
Different footprints, different ground-truth denominators, and a published gap
of only 0.0277. Session 136 corrected this class of confound four separate
times; it had not been corrected here.

## What was done

The two evaluation-bounds footprints were intersected, each carrier tile grid
was clipped to the intersection, and both committed detection sets were clipped
to it and re-scored with one scorer at a 20 m buffer. Detections were booked to
a carrier tile by nearest tile centroid, the rule E79 settled and the same rule
the evaluator applies to references.

Two robustness axes were varied rather than assumed:

- **Carrier grid.** Scoring on the 256 px grid and again on the 384 px grid,
  because the carrier determines which reference mounds fall in scope. A
  conclusion that flips with the carrier is not a conclusion.
- **Deduplication.** With and without a uniform 20 m within-set pass, because
  E80 records two coexisting scoring paths and a cross-architecture comparison
  has to say which it used.

| Footprint | Area | Carrier tiles | Reference mounds |
|---|---:|---:|---:|
| 256 px corpus | 1,324.8 km² | 1,032 | 431 |
| 384 px corpus | 1,415.8 km² | 487 | 435 |
| **Intersection** | **1,274.8 km²** | 1,032 (256 px) / 481 (384 px) | **420 under both carriers** |

The intersection is 96.2 % of the 256 px footprint and 90.0 % of the 384 px one.
The asymmetry matters: the 384 px corpus covers 141.0 km² that the 256 px corpus
never sees, against 50.0 km² the other way. Both carriers scope the same 420
reference mounds, so the ground-truth denominator is genuinely common.

## Result: the gap survives, and widens slightly

| Cell | Carrier | Dedup | Precision | Recall | **F1@20 m** |
|---|---:|---|---:|---:|---:|
| 256 px, PV consensus 5-of-5 | 256 px | no | 0.8831 | 0.8095 | **0.8447** |
| 256 px, PV consensus 5-of-5 | 384 px | no | 0.8727 | 0.8000 | **0.8348** |
| 384 px, PV min 6-of-10 | 256 px | no | 0.9257 | 0.8310 | **0.8758** |
| 384 px, PV min 6-of-10 | 384 px | no | 0.9204 | 0.8262 | **0.8708** |

| Comparison | Gap (384 px − 256 px) |
|---|---:|
| Published, cross-scope | +0.0277 |
| Common footprint, 256 px carrier | **+0.0311** |
| Common footprint, 384 px carrier | **+0.0360** |
| Common footprint, 256 px carrier, deduplicated | +0.0322 |
| Common footprint, 384 px carrier, deduplicated | +0.0371 |

Correcting the footprint does not erase the gap. It moves it from 0.028 to
between 0.031 and 0.037 depending on carrier, and the direction is stable across
both carriers and both deduplication settings. Uniform deduplication is
immaterial here, removing one detection from the 384 px set and none from the
256 px set, so E80's confound does not bear on this comparison.

## The mechanism the premise names is not supported

This is the part that matters for the design, and it runs against the premise.

"Swamping the verifier" predicts a specific signature: the smaller tile produces
more candidates than the verifier can discriminate, so it should buy **recall**
at the cost of **precision**. The measured pattern is not that. The 256 px cell
is worse on *both* margins under both carriers — precision 0.8831 against 0.9257,
recall 0.8095 against 0.8310 on the 256 px carrier. It also emits slightly *more*
surviving detections (385 against 377). A cell that is simultaneously less
precise and less complete is not trading one for the other; it is simply weaker
on this contrast.

So the caution the premise licences — that pushing towards higher recall will
overwhelm the precision stage — does not follow from this evidence. The 256 px
deficit is real, modest, and unexplained by swamping.

## The boundary: this is not a clean tile-size contrast

The two cells differ in more than tile size, and the difference is not small:

| | 256 px cell | 384 px cell |
|---|---|---|
| Proposer pool | `text-consensus-5of5` | `text-1of10` |
| Passes | 5 | 10 |
| Vote threshold | 5 of 5 | 6 of 10 |
| Verifier | v1, `verify_adversarial.md`, `gemini-3-flash-preview`, MINIMAL, T = 0.0 | identical |

The verifier stage is identical, but pass count and vote threshold are not. The
384 px cell draws on twice the passes at a proportionally more permissive
threshold, which is exactly the diversity dividend this project has measured
elsewhere. Attributing the surviving 0.031–0.037 to tile size alone is therefore
not warranted by these two cells.

What the re-score does establish is narrower and still useful: **the published
comparison is not an artefact of mismatched scope**, and the deficit does not
have the shape "swamping" predicts. Isolating tile size needs the iso-stride
design in Phase 2, which holds stride and pass count constant and varies only
tile size.

## What this means for the programme

- The premise should be restated. "256 px is modestly weaker on a mixed
  tile-size-and-pass-count contrast, by about 0.03 F1, on both precision and
  recall" is what the evidence supports. "256 px swamps the verifier" is not.
- Because the deficit is not a precision failure, it is weak grounds for
  constraining the high-recall direction, and option (c) should be treated as
  open rather than disfavoured.
- The verifier stage on the grid (Phase 1, $6.33) remains the thing that settles
  whether a precision stage changes tile-size rankings. This re-score used
  already-verified sets and so cannot speak to it.

## Reproducing this

```bash
python scripts/phase0_3_tilesize_common_footprint.py \
    --output-dir results/phase0-recall-levers/tilesize-premise
```

Run on sapphire. Inputs are the committed detection sets named in each
condition's source-evaluation `cli_args`, the two committed bounds files, and
`inputs/vectors/references/mounds-reference.geojson`. Outputs are
`tilesize_premise.json` and the two clipped carrier grids under `bounds/`.

## See also

- `planning/recall-levers-programme-2026-08-19.md` § 0.3 (the specification)
- `scripts/h13_tilesize_overlap_grid.py` (`build_common_scope`, the pattern followed)
- Errata E79 (tile assignment) and E80 (deduplication paths)

## Changelog

### 2026-08-19 — Original publication

First execution of Phase 0.3. Establishes that the published 256 px versus
384 px gap survives footprint correction at +0.031 to +0.037 F1, that it is
stable across both carrier grids and both deduplication settings, that the
"swamping" mechanism is not supported because the 256 px cell loses on precision
and recall together, and that the contrast confounds tile size with pass count
and vote threshold. Committed with the Phase 0.3 script.
