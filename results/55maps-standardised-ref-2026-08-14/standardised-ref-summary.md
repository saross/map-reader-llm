# 55-map board on the standardised reference — queue items 2–3

> **Last revised**: 2026-08-14 (initial publication). See
> [§ Changelog](#changelog) for revision history.

**What this is.** The eight 55-map board cells re-scored ONCE against
the ruling-21 **standardised reference**
(`results/deployment-oracle-2026-06-06/canonical-gt/standardised/`:
student layer 4,731 + extension layer 279 at marked centres), closing
queue items 2 and 3 of
`reports/verification/reference-standardisation-queue.md` under its
§ Execution contract. Corrected F1 and tile-level MCC now share one
reference (item 3); the T=0.3 run has a full-buffer evaluation on the
correct reference (item 2), registered under both items from this
single scoring.

**Execution**: `scripts/score_55maps_standardised_reference.py`
(engine commit `6e38c0e5f`), legs A/B/C on sapphire, US$0.00 API.
Per-cell artefacts in this directory (`<cell>/summary.json`,
`corrected-f1.csv`, `report_autogen.md`, `score.log`); consolidated
sweep in `consolidated-standardised.csv`; decomposition in
`abc-decomposition-50m.json`; gate evidence in
`validation-gate.json`.

## Reference-consumption semantics (the item-2/3 design decision)

The legacy extended GT ring-gated phantoms (`buffer_metres <= R`,
`build_phantom_gdf`) because ring-censored phantom records were only
localised to within their review ring — the Obs 371 defect, which
collapsed sub-50 m Track-2 figures onto the student layer. The
standardised extension layer carries **marked centres (±2.5 m)**, so
the localisation gate is dissolved: all 279 extension mounds enter the
extended GT **whole at every buffer radius**, and the Hungarian
matching radius alone decides matches
(`compute_corrected_f1_multi_buffer.load_standardised_extension`).
Consequences, both verified in the artefacts:

- **Sub-50 m Track-2 is now genuine**: e.g. T03-k3 at R = 20 m rises
  0.6296 → 0.6719 (old
  `results/55maps-extended-gt-2026-06-07/T03-k3/summary.json` vs
  `T03-k3/summary.json` here) — correct detections of student-missed
  mounds are no longer booked as false positives below 50 m.
- **Tile MCC is buffer-invariant by construction** (tile
  classification never uses the matching radius and the extended GT no
  longer varies with R), so each cell carries ONE MCC against the same
  reference its F1 uses.
- The extended reference is **5,010 records everywhere** (4,731 +
  279; `n_ref_extended` in every row), versus 5,160 ring-admitted at
  R = 50 m under the legacy pairing — the marking campaign removed
  ~135 net phantom records at the 50 m shell that were duplicates of
  student mounds or not mounds.

## The board at 50 m (leg C — publication)

Source: `consolidated-standardised.csv` (R_m = 50 rows); 95 %
percentile bootstrap CIs, tile-level resampling, 10,000 iterations,
seed 42.

| cell | config | k | P | R | F1 [95 % CI] | MCC [95 % CI] |
|------|--------|---|-----|-----|--------------|---------------|
| T03-k3 | text-high-T0.3 | 3 | 0.8483 | 0.8305 | **0.8393** [0.8304, 0.8479] | 0.6888 [0.6749, 0.7022] |
| TH7-k3 | text-high-T0.7 | 3 | 0.8583 | 0.8200 | 0.8387 [0.8297, 0.8475] | 0.6796 [0.6657, 0.6933] |
| T03-k4 | text-high-T0.3 | 4 | 0.8933 | 0.7756 | 0.8303 [0.8210, 0.8394] | 0.6690 [0.6550, 0.6822] |
| TM-n10-k5 | text-min-n10 | 5 | 0.8895 | 0.7743 | 0.8279 [0.8181, 0.8374] | 0.6709 [0.6573, 0.6844] |
| TH7-k4 | text-high-T0.7 | 4 | 0.8999 | 0.7479 | 0.8169 [0.8066, 0.8268] | 0.6650 [0.6513, 0.6786] |
| TM-k3 | text-min | 3 | 0.8801 | 0.7517 | 0.8109 [0.8006, 0.8210] | 0.6569 [0.6435, 0.6710] |
| IM-k3 | image | 3 | 0.8293 | 0.7747 | 0.8010 [0.7911, 0.8105] | **0.7120** [0.6987, 0.7248] |
| TM-k4 | text-min | 4 | 0.8994 | 0.6938 | 0.7833 [0.7722, 0.7943] | 0.6401 [0.6265, 0.6539] |

Headline observations (point estimates; significance and tiering are
queue item 5, not claimed here):

1. **The F1 rank order is identical to the legacy-reference order** —
   all eight cells keep their positions (`abc-decomposition-50m.json`,
   A1 vs C columns).
2. **The oracle's margin collapses**: T03-k3 leads TH7-k3 by +0.0006
   on the standardised reference, down from +0.0051 on the legacy
   reference (0.84769 − 0.84255) — an ~8× narrowing. Whether T03-k3's
   sole-leader status survives the paired permutation re-tiering is
   item 5's question.
3. **The F1-vs-MCC divergence pattern survives unification at the
   point-estimate level**: image tops MCC (0.7120) while text tops F1,
   now with both metrics on the SAME reference. The formal Obs 280
   re-measurement is queue item 4.

## Why the numbers moved — the A0/A1/B/C decomposition at 50 m

Source: `abc-decomposition-50m.json`. A0 = legacy reference exactly as
committed (de-duplication disabled); A1 = legacy reference on the
current engine; B = standardised student layer + legacy phantoms
(diagnostic, uncommitted per the item-1 precedent); C = standardised
reference (this board).

| cell | A0 | A1 | B | C | A1−A0 (W6-E9) | B−A1 (student layer) | C−B (extension layer) | C−A1 (net) |
|------|-----|-----|-----|-----|---------------|----------------------|------------------------|------------|
| TH7-k4 | 0.81523 | 0.81532 | 0.81530 | 0.81687 | +0.00009 | −0.00002 | +0.00157 | +0.00156 |
| TH7-k3 | 0.84247 | 0.84255 | 0.84218 | 0.83871 | +0.00008 | −0.00037 | −0.00347 | −0.00384 |
| T03-k4 | 0.83587 | 0.83596 | 0.83556 | 0.83034 | +0.00009 | −0.00040 | −0.00522 | −0.00562 |
| T03-k3 | 0.84761 | 0.84769 | 0.84674 | 0.83933 | +0.00008 | −0.00095 | −0.00740 | −0.00836 |
| TM-k4 | 0.78307 | 0.78316 | 0.78308 | 0.78332 | +0.00009 | −0.00008 | +0.00024 | +0.00017 |
| TM-k3 | 0.81271 | 0.81280 | 0.81257 | 0.81085 | +0.00009 | −0.00023 | −0.00171 | −0.00195 |
| IM-k3 | 0.79870 | 0.79878 | 0.80057 | 0.80103 | +0.00008 | +0.00179 | +0.00046 | +0.00225 |
| TM-n10-k5 | 0.82903 | 0.82911 | 0.82870 | 0.82787 | +0.00009 | −0.00041 | −0.00083 | −0.00124 |

Readings:

- **A1−A0 is uniform (+0.00008/9 on every cell)** — the W6-E9
  channel-duplicate fix: the canonical review's one 0.98 m twin
  (ruling 20c) stops double-counting, removing exactly one spurious FN
  per cell (`a1_drops = 1` for all eight, `validation-gate.json`).
- **The extension-layer overhaul (C−B) is the dominant mover and
  runs against the k3 text cells** (T03-k3 −0.0074 … TM-k3 −0.0017)
  while slightly favouring the k4 and image cells. Mechanism
  (consistent with, not proven by, these data): the legacy layer
  placed phantoms AT detection coordinates — a guaranteed 0 m match
  for the generating detection — and admitted ~135 net records at the
  50 m shell that the marking campaign adjudicated away as duplicates
  or non-mounds. Higher-recall (k3) cells harvested more of those
  free matches, so they lose more when the reference shrinks to 279
  distinct mounds at true centres.
- **The student-layer standardisation (B−A1) is small and mostly
  slightly negative, except image (+0.0018)** — the marked/deduplicated
  student positions sit closer to where the image config detects.
- **Every net move (C−A1, max |−0.0084|) is well inside the Obs 396
  net-bias scale (≈ −0.017)** — no contract stop state was triggered.

## Verification stack applied

- **Feature-count crosscheck** (Session 77 class): 8/8 detection
  GeoJSONs match their documented counts before any scoring
  (`validation-gate.json → feature_count_crosscheck`).
- **A0 reproduction gate**: 8/8 cells reproduce the committed legacy
  values (`results/55maps-extended-gt-2026-06-07/<cell>/summary.json`)
  at **delta +0.00e+00 exactly** under the committed configuration
  (de-duplication disabled), tolerance 1e-6
  (`validation-gate.json → gate_rows`). "Reproduce before you vary"
  discharged.
- **Extension census**: 279 admitted / 0 duplicate drops at every
  buffer of every cell (`c_leg_extension_census`); the layer's minimum
  `nearest_student_m` (10.32 m) exceeds the 5 m dedup tolerance.
- **Code verification**: engine + driver under two fresh-context audit
  lenses plus a fix-round re-audit (commits `c951aa749` →
  `b34f90925` → `6e38c0e5f`); tier-1 suite 1,462 passing; the legacy
  scoring path verified byte-identical against the pre-change engine.
- **Blind verifier pass** over this document: see Changelog.

## Known reference biases (carried, not new)

Obs 396 (both directions travel together): ~370 estimated residual
long-range duplicates among out-of-scope student records deflate F1
≈ −0.03 at a balanced operating point; absent joint student+model
false negatives inflate it ≈ +0.011–0.012; net ≈ −0.017 at point
estimates, rank-preserving to first order. This board inherits those
properties from the reference
(`canonical-gt/standardised/README.md § Known biases`).

## Registration

Manifest conditions (`results/run-conditions.json`, commit
`fab017085`): one `-standardised-gt` condition per cell under its run
family (`verified-k4/k3-standardised-gt` × 4 text/image runs;
`verified-5of10-standardised-gt` under `55maps-text-min-n10-uplift`),
each pointing at the generator-shape `<cell>/evaluation.json` here.
Manifest 330 conditions ALL VALID; drift check 0 fail (the uplift
run's `n_passes=10 vs 5 run dirs` WARN is pre-existing on its
canonical sibling). The two t0.3 conditions are that run's full-buffer
evaluation on the correct reference — item 2's gap closed by the same
scoring registered under item 3.

## Changelog

### 2026-08-14 — Original publication

Session 132: queue items 2–3 executed under the reference-
standardisation execution contract (PI go 2026-08-14, US$0.00).
Blind fresh-context verifier pass applied before the queue tick;
corrections (if any) recorded here.
