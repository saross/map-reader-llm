# Verifier stage — K = 3, rebuilt union (recovery-fragment fix)

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

This stage **extends** `../verify_k3/`, it does not replace it. The committed
stage's `probabilities.json` was not touched.

## Why this stage exists

The recovery-fragment fix (`75d7c8d4cd55b6ec8d2a40abff70a31f62b67725`) rebuilt
`outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n3/consensus_t1.geojson`
from **757** candidates to **759**. The committed stage's results are keyed
against the old numbering, so they must be re-keyed before they can be read
against the new crops manifest; and three of the new candidates are not covered
by the committed stage at all.

| field | value |
|---|---|
| extends | `../verify_k3/probabilities.json` (757 results) |
| proposer union | `../../../g384_ov192_g37/consensus-n3/consensus_t1.geojson` (759 candidates) |
| crops | `../crops_k3_recovery-fixed/` (759 crops, 150 × 150 px, padding 75, all from rasters, 0 tile fallbacks) |
| carried | **756** results, matched by projected centroid within 2 m |
| newly verified | **3** candidates |
| API calls | **3** |
| audited flex cost | **US$0.002027** (list basis US$0.004053) |

## The three calls

| candidate | source tile | votes | new `mound_probability` |
|---|---|---:|---:|
| `candidate_00523` | `K-35-062-2_Rakovski_x3648_y192.png` | 2 | **0.0** |
| `candidate_00706` | `K-35-062-2_Rakovski_x192_y576.png` | 1 | **1.0** |
| `candidate_00707` | `K-35-062-2_Rakovski_x2688_y1152.png` | 1 | **0.0** |

`candidate_00523` is the same mound as the committed stage's candidate at
(24.986184, 42.311546), displaced **9.551 m** — 1.90 px, so genuinely a different
crop — and promoted from 1 vote to 2 by the fragment. `candidate_00706` and
`candidate_00707` are genuinely new candidates the fragment introduced.

**None of the three enters this rung's scored detection set.** The operating
point is vote ≥ 3, and all three sit at 1 or 2 votes. The one candidate that
*does* newly enter is `candidate_00049` — carried, not called — promoted from 2
votes to 3 with a committed probability of 1.0.

## A residue the approved spend does not cover, flagged not smoothed

Of the 756 carried results, **751 have a byte-identical crop window** and are
therefore exactly valid. **Five do not**: their centroids moved sub-metre, but
enough to cross a pixel boundary, so `rasterio.DatasetReader.index` floors them
into a window offset by 1 px in one axis.

| candidate | displacement | window before → after | carried probability |
|---|---:|---|---:|
| `candidate_00049` | 0.999 m | (1886, 1236) → (1886, 1237) | 1.0 |
| `candidate_00272` | 0.829 m | (3716, 2337) → (3717, 2337) | 1.0 |
| `candidate_00348` | 0.579 m | (821, 2340) → (820, 2340) | 1.0 |
| `candidate_00047` | 0.247 m | (2121, 1048) → (2122, 1048) | 0.95 |
| `candidate_00027` | 0.237 m | (281, 2451) → (281, 2452) | 1.0 |

Re-verifying these five would cost about US$0.0035 and **is not approved** — the
PI's ruling approved 4 calls and nothing else. Carrying them is defensible on
the numbers: every one sits at 0.95 or 1.0, the operating point is 0.10, and a
1 px shift on a 150 px crop with the mound still centred cannot plausibly drive
a 1.0 to below 0.10. The one direct piece of evidence in this job supports that
— `../verify_k1_recovery-fixed/`'s single call returned the identical 0.95 on a
crop whose window did not move at all, which tests reproducibility but not
shift-tolerance. So this is an argument from magnitude, not a measurement, and it
is named here so the PI can overrule it for US$0.0035.

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
    --proposer outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n3/consensus_t1.geojson \
    --output-dir outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops_k3_recovery-fixed \
    --padding 75 --rasters-dir inputs/rasters --tiles-dir inputs/tiles_384_ov192

python carry_probabilities.py --old-manifest ../crops_k3/candidate_manifest.json \
    --old-probs ../verify_k3/probabilities.json \
    --new-manifest ../crops_k3_recovery-fixed/candidate_manifest.json \
    --out-dir . --rasters-dir inputs/rasters --label k3

python scripts/run_pv.py verify \
    --crops-dir outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops_k3_recovery-fixed \
    --verifier-config prompts/configs/verify_adversarial-text.json \
    --output-dir outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k3_recovery-fixed \
    --mode realtime --iterations 1 --workers 3 --service-tier flex
```

`run.meta.json` describes **only the three calls**. The 756 carried results, with
each one's old key, new key, displacement and crop window, are in
`carry_provenance.json`.

## Changelog

### 2026-09-13 — Original publication

Created under the PI's "fix properly" ruling of 2026-09-13, which approved 4
verifier calls (≈ US$0.003) across this stage and
`../verify_k1_recovery-fixed/` and nothing further. 756 results carried from
`../verify_k3/` (751 with a byte-identical crop window, 5 shifted by 1 px and
flagged above); 3 calls made. The cell this stage feeds,
`gemini37-screen-2026-08-28::g37-text-k3-verified-opmax`, re-scores to F1@20
**0.8870 → 0.8860** (−0.0010) on 494 → 495 detections — the extra detection is a
false positive, so precision falls (0.8340 → 0.8323) while recall holds at
0.9471. The operating point does not move: the board-frame argmax is still
(vote 3, prob 0.10), with 0 ties, and the two frames still agree.
