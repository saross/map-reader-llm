# Verifier stage — K = 1, rebuilt union (recovery-fragment fix)

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

This stage **extends** `../verify_k1/`, it does not replace it. The committed
stage's `probabilities.json` was not touched.

## Why this stage exists

The recovery-fragment fix (`75d7c8d4cd55b6ec8d2a40abff70a31f62b67725`) rebuilt
`outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n1/consensus_t1.geojson`.
The rebuilt union holds the same **640** candidates, but a rebuild re-numbers
them, so the committed stage's results — keyed `candidate_NNNNN` against the old
numbering — cannot be read against the new crops manifest. This stage carries
them across, and covers the one candidate the committed stage does not.

| field | value |
|---|---|
| extends | `../verify_k1/probabilities.json` (640 results) |
| proposer union | `../../../g384_ov192_g37/consensus-n1/consensus_t1.geojson` (640 candidates) |
| crops | `../crops_k1_recovery-fixed/` (640 crops, 150 × 150 px, padding 75, all from rasters, 0 tile fallbacks) |
| carried unchanged | **639** results, matched by projected centroid within 2 m |
| newly verified | **1** candidate — `candidate_00092` |
| API calls | **1** |
| audited flex cost | **US$0.000757** (list basis US$0.001514) |

## The one call

`candidate_00092`, source tile `K-35-052-4_32635_x2880_y3072.png`, vote count 1.
The measuring report classified it as uncovered because its centroid moved
**3.026 m** — beyond the 2 m positional tolerance — when a recovery fragment
contributed a co-located detection that shifted the cluster centroid.

**It returned `mound_probability` 0.95, exactly the committed stage's value for
the same mound.** That is not a coincidence and it is worth recording: at the
sheets' ~5.02 m/px ground resolution a 3.026 m shift is **0.60 px**, and
`extract_candidates._crop_from_raster` floors the centroid to whole pixels via
`rasterio.DatasetReader.index`, so the crop window is byte-identical —
`(col_off, row_off) = (3177, 3192)` before and after. The verifier was asked the
same question about the same image and gave the same answer.

**So this call was confirmatory, not necessary.** A coverage test on the integer
crop window rather than on metric distance would have carried this candidate at
US$0. Recorded for the PI in `reports/recovery-drop-fix-2026-09-13.md`.

## Instrument — the carried verifier, unchanged

Read from the committed stage's `run.meta.json` and re-applied without override:

| parameter | value |
|---|---|
| config | `prompts/configs/verify_adversarial-text.json` |
| model | `gemini-3-flash` → `gemini-3-flash-preview` |
| system instruction | `verify_adversarial.md`, hash `2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d` |
| temperature | 0.0 (from the config; never overridden) |
| thinking | MINIMAL (from the config; never overridden) |
| iterations | 1 |
| examples | none (`library_hash: no_examples`) |
| tier | real-time **flex** |

## How it was built

```bash
python scripts/run_pv.py extract \
    --proposer outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n1/consensus_t1.geojson \
    --output-dir outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops_k1_recovery-fixed \
    --padding 75 --rasters-dir inputs/rasters --tiles-dir inputs/tiles_384_ov192

# re-key the committed results onto the rebuilt numbering and seed this stage
python carry_probabilities.py --old-manifest ../crops_k1/candidate_manifest.json \
    --old-probs ../verify_k1/probabilities.json \
    --new-manifest ../crops_k1_recovery-fixed/candidate_manifest.json \
    --out-dir . --rasters-dir inputs/rasters --label k1

# run_pv.py's resume filter then calls the API for the uncovered candidate ONLY
python scripts/run_pv.py verify \
    --crops-dir outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops_k1_recovery-fixed \
    --verifier-config prompts/configs/verify_adversarial-text.json \
    --output-dir outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k1_recovery-fixed \
    --mode realtime --iterations 1 --workers 2 --service-tier flex
```

`run.meta.json` in this directory describes **only the one call** — that is what
makes the cost auditable. The 639 carried results are accounted for in
`carry_provenance.json`, which records each one's old key, new key, displacement
and crop window.

## Changelog

### 2026-09-13 — Original publication

Created under the PI's "fix properly" ruling of 2026-09-13, which approved 4
verifier calls (≈ US$0.003) across this stage and `../verify_k3_recovery-fixed/`
and nothing further. 639 results carried from `../verify_k1/`, all 639 with a
byte-identical crop window; 1 call made, returning 0.95 against the committed
0.95. The cell this stage feeds,
`gemini37-screen-2026-08-28::g37-text-k1-verified-opmax`, re-scores to F1@20
**0.8495 → 0.8495** — no change at the headline buffer; it moves only at 5 m
(0.4781 → 0.4760), where a 3 m centroid shift can cross the match radius.
