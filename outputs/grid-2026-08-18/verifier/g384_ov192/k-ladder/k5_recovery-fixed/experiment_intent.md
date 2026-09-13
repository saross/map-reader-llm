# Verifier stage — tier E K = 5, rebuilt union (recovery-fragment fix)

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

This stage **extends** `../k5/`, it does not replace it. The committed stage's
`probabilities.json` was not touched.

## Why this stage exists, and why it cost nothing

The recovery-fragment fix (`75d7c8d4cd55b6ec8d2a40abff70a31f62b67725`) rebuilt
`outputs/grid-2026-08-18/g384_ov192/consensus-n5/`. At vote ≥ 1 the union is the
same **2,932** candidates; the whole effect of the pool's 14 dropped features is
one cluster promoted from 4 votes to 5, which is why `consensus_t5.geojson` went
from 1,168 to 1,169.

A rebuild re-numbers candidates, so the committed results had to be re-keyed
before they could be read against the new crops manifest. **Every one of the
2,932 was covered**, so no API call was made and **US$0.00 was spent** — exactly
as `reports/recovery-fragment-drop-2026-09-13.md` § 4.2 predicted.

| field | value |
|---|---|
| extends | `../k5/probabilities.json` (2,932 results) |
| proposer union | `../../../../g384_ov192/consensus-n5/consensus_t1.geojson` (2,932 candidates) |
| crops | `crops/` (2,932 crops, 150 × 150 px, padding 75, all from rasters, 0 tile fallbacks) |
| carried | **2,932** — all of them |
| uncovered | **0** |
| API calls | **0** |
| cost | **US$0.00** |

There is deliberately **no `run.meta.json`** in this directory: no API call was
made, so there is no run to describe. `carry_provenance.json` is the whole
provenance record.

## The promoted candidate, and the one sensitivity in the zero-delta claim

The single changed candidate is `candidate_01335` at (26.513551, 41.879916),
source tile `K-35-078-1_Lesovo_x192_y2496.png`, carried
`mound_probability` **0.10**, promoted from 4 votes to 5.

The rung's operating point is vote ≥ 5, **prob ≥ 0.15**. A probability of 0.10
does not clear it, so the candidate does not enter the scored detection set and
the cell's F1 and tile-MCC are unchanged — measured, not argued: see the
changelog below.

**The sensitivity, stated plainly.** `candidate_01335` is the one carried result
in this stage whose crop window moved — 1.410 m of centroid shift, enough to
cross a pixel boundary, so its crop is offset by 1 px from the one the committed
0.10 was measured on. Its carried probability is 0.10 against a 0.15 threshold,
which is below but not far below. Re-verifying it would cost about US$0.0007 and
**is not approved** — the PI's ruling approved 4 calls, all of them in the
`gemini37-screen-2026-08-28` tree. So the zero delta reported for this cell is
exact **conditional on** carrying that 0.10. Named here so the PI can settle it
for well under a cent.

## Instrument — the carried verifier, unchanged

No call was made, so nothing was configured; the carried results were produced by
the committed stage under `prompts/configs/verify_adversarial-text.json`
(`gemini-3-flash-preview`, temperature 0.0, thinking MINIMAL, 1 iteration,
real-time flex).

## How it was built

```bash
python scripts/run_pv.py extract \
    --proposer outputs/grid-2026-08-18/g384_ov192/consensus-n5/consensus_t1.geojson \
    --output-dir outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k5_recovery-fixed/crops \
    --padding 75 --rasters-dir inputs/rasters --tiles-dir inputs/tiles_384_ov192

python carry_probabilities.py --old-manifest ../k5/crops/candidate_manifest.json \
    --old-probs ../k5/probabilities.json \
    --new-manifest crops/candidate_manifest.json \
    --out-dir . --rasters-dir inputs/rasters --label k5-tier-e
# -> carried 2932, uncovered 0; no verify step needed
```

## Changelog

### 2026-09-13 — Original publication

Created under the PI's "fix properly" ruling of 2026-09-13. All 2,932 committed
results carried, 0 uncovered, 0 API calls, US$0.00.

The cell this stage feeds,
`grid-2026-08-18::g384-ov192-k5-verified-opmax`, re-scores **identically on every
arm** — F1@20 0.8905 → 0.8905, precision 0.9130, recall 0.8690, BCa CI
[0.8595, 0.9149], tile-MCC 0.8139, confusion tp 193 / tn 248 / fp 10 / fn 36,
435 detections — with the board-frame argmax still at (vote 5, prob 0.15), 0
ties, and the two frames still agreeing. The report's predicted zero delta is
therefore a measurement, not an inference. This is the one of the four cells that
re-scored through the full recorded recipe: `scripts/evaluate_detections.py` with
the curator reference, the `era2_b_intersection_bounds.geojson` frame, 14
buffers, 10,000 BCa draws, seed 42 and `--mcc`, preceded by the tier-E carrier
re-key (`run_k_ladder_tier_e.reassign_carrier_tiles`) without which the tile-join
invariant refuses the cell.
