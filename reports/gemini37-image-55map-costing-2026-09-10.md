# Costing a Gemini 3.7 image run at 55-map scale (costing only; nothing run)

> **Last revised**: 2026-09-10 (original publication; S152, scheduled item 4). See [§ Changelog](#changelog).

The PI asked (continuity, "NEXT SESSION", item 4) for the cost of extending
the Gemini 3.7 image track from the 4-map gold standard (GS) to the 55-map
corpus, with both verifier arms, presented against the 55-map instrument's
resolution. This is a costing from committed run metadata. No Application
Programming Interface (API) call was made; the PI "may" fund the run in a
later session.

## Inputs (every figure re-read from the named file)

| Quantity | Value | Source |
|---|---:|---|
| 55-map B-geometry tiles (384 px / 50 %) per pass | 24,561 | `outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/run_5/*.meta.json` (`items_processed` 24,560 + recovery 1) |
| GS B-geometry tiles per pass | 1,398 | `results/gemini37-image-gs-2026-09-01/findings.md` |
| 3.7 image GS proposer, 5 passes, all-in | US$22.50 token-basis | `results/gemini37-image-gs-2026-09-01/findings.md` § Operational notes |
| 3.7 image GS proposer, runner estimator, all metas summed | US$35.82 "billed" (list US$71.64) | `outputs/gemini37-image-gs-2026-09-01/g384_ov192_g37img/run_*/*.meta.json` (ten metas incl. fd-storm attempts and recoveries) |
| Caching achieved at scale (image) | 79.5 % of input | findings I5 |
| 3.7 text 55-map proposer, 5 passes | US$51.94 "billed" (list US$103.89) | `outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/run_*/*.meta.json` (no caching) |
| 55-map text K = 5 union (verifier input) | 12,715 candidates | `outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/union_k5.geojson` |
| GS text K = 5 union / GS image K = 5 union | 791 / 674 candidates | the two `union_k5.geojson` under `outputs/gemini37-screen-2026-08-28/verifier/…` and `outputs/gemini37-image-gs-2026-09-01/verifier/…` |
| Gemini 3 verifier (carried), list | US$0.956 for 674 (GS image); US$17.78 for 12,715 (55-map text) | `verify_arm1/run.meta.json` under the two runs |
| Gemini 3.7 verifier, list | US$0.852 for 674 (GS image); US$16.22 for 12,715 (55-map text) | `verify_arm2/run.meta.json` under the two runs |
| Gemini 3.8 verifier | ≈ US$0.9–1.3 token basis for the 791-candidate Arm V (2,023 tokens per candidate) | `planning/gemini38-screen-2026-09-04.md` § Arm V (projection; the production run's meta is not on disk); the single probe call in `…/verify_swap38/run.meta.json` cost US$0.0039 with 530 thinking tokens, an upper bound |
| 55-map instrument resolution | MDE80 ≈ 0.013 F1 | continuity (S146 block: "55-map 0.013") |
| GS image gain the run would test at scale | +0.084 to +0.090 F1 over the Gemini 3 image anchor | findings I1 |

## Arithmetic

**Proposer, per tile-pass.** Token-basis: 22.50 / (5 × 1,398) =
US$0.00322. Runner-estimator basis: 35.82 / (5 × 1,398) = US$0.00512
(the token-load audit of 2026-06-12 found the runner over-records
cached-heavy runs, so the token basis is the better central figure and
the runner figure a ceiling). For comparison, 3.7 text at 55-map scale
cost US$0.000423 per tile-pass, so image is 7.6× text per tile-pass.

**Proposer at 55-map scale.** 24,561 tiles × N passes:

| Passes | Token basis | Runner-estimator ceiling |
|---:|---:|---:|
| K = 5 | US$395 | US$629 |
| K = 10 | US$791 | US$1,258 |

**Verifier input at 55-map scale.** Text yields 0.518 candidates per
tile on 55 maps and 0.566 on GS; image yields 0.482 on GS. Scaling the
55-map text union by the GS image/text ratio (674 / 791 = 0.852) gives
about 10,800 candidates; scaling image's GS rate directly gives 11,840.
Take 11,300 ± 500 for K = 5 (K = 10 unions run larger; the 3.7 text
K = 10 GS union was 3,319 against 791 at K = 5, a 4.2× step, so a K = 10
verifier bill should be budgeted at up to 4× the K = 5 figure).

**Verifier arms at 55-map scale (K = 5, list basis).**

| Arm | Per candidate | 11,300 candidates |
|---|---:|---:|
| Gemini 3 (carried) | US$0.00140–0.00142 | ≈ US$16 |
| Gemini 3.7 | US$0.00126–0.00128 | ≈ US$14–15 |
| Gemini 3.8 (card projection; probe upper bound US$0.0039) | US$0.0011–0.0016 | ≈ US$13–18 (upper bound ≈ US$44) |

## The estimate

| Configuration | Token basis | Runner ceiling |
|---|---:|---:|
| K = 5, proposer + Gemini 3 and 3.7 verifier arms | ≈ US$425 | ≈ US$660 |
| … plus the 3.8 arm | ≈ US$440 (upper bound US$470) | ≈ US$675 (upper bound US$705) |
| K = 10, proposer + Gemini 3 and 3.7 arms (verifier ×4) | ≈ US$910 | ≈ US$1,380 |

The verifier arms are a rounding error beside the proposer; the decision
is the proposer's US$400–650 at K = 5.

**Against the instrument.** The 55-map corrected-F1 instrument resolves
about 0.013 F1 at 80 % power. The GS image gain the run would test is
+0.084 to +0.090 over the Gemini 3 image anchor, six to seven times that
resolution, so the run is not under-powered for the transfer question;
what it would buy is whether the GS parity of 3.7 image with 3.7 text
(0.9308 versus 0.9265 on GS, not significant) survives at deployment
scale, and the image track's deployment-scale transfer tax, which the
text track measured at about −0.05 to −0.09 (S111–S112 transfer table).
The PI's pre-agreed trigger for the extension (a resolvable new F1 high
on GS) was NOT met (findings § The escalation question), so this costing
is for the record, not a recommendation.

**Operational caveats.** The GS image run lost two pass attempts to
file-descriptor storms and the daily flex-storm window before the
storm-resilient recovery driver (`scripts/gemini37-image-gs-driver.sh`,
150-worker image cap, `ulimit 8192`) cleared the residue; at 17.6× the
tile count the same profile means several recovery rounds and a
multi-day wall clock. Caching at 79.5 % was below the 90 % projection;
the token-basis figure above already reflects the achieved rate.

## Changelog

### 2026-09-10 — Original publication

Costing only, from committed run metadata (S152, scheduled item 4). No
API spend.
