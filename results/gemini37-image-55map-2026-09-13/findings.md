# Gemini 3.7 image at deployment scale, K = 3: findings

> **Last revised**: 2026-09-16 (permutation p-values reported as *p* < 0.0001
> rather than *p* = 0.0000; the P1 threshold gap named; `IM-k3`'s tile-join
> provenance re-diagnosed). Prior: 2026-09-14 (original publication — the
> campaign's P1–P5 verdicts, both arms × both rungs, the deployment-scale
> modality difference-in-differences, and the audited costs per leg). See
> [§ Changelog](#changelog) for revision history.

Card: `planning/gemini37-image-55map-2026-09-13.md` (§ 2 the cells, § 4 the
predictions, committed before any 55-map scoring). Deltas, rulings and the
pre-specified readings: `reports/gemini37-image-55map-deltas-2026-09-13.md`
§ 10. Launch state, gates and recovery narrative:
`outputs/gemini37-image-55map-2026-09-13/post_run_report.md`.

**Instrument.** `scripts/evaluate_detections.py` on the r2 board's own stage-2
recipe — 14 buffers, `best-available-gt-55maps-r2.geojson` (5,018 references),
`55maps_evaluation_bounds.geojson` (8,541 tiles), tile-level BCa bootstrap
10,000 / seed 42, `--mcc`, `--require-clean-inputs`. Every figure below is
read from a committed `evaluation.json` under
`results/gemini37-image-55map-2026-09-13/cells/`, and the paired tile-swap
runs at 10,000 draws, seed 42, with Benjamini–Hochberg at q = 0.05 applied
across the declared five-test family, separately on each metric. **A
permutation p-value is bounded below by 1/10,000**, so a test with no draw
at or beyond the observed statistic is reported as *p* < 0.0001, never as
*p* = 0; the raw zeros are in `tests_IMG-ARM2-K3-carried.json`.

## 1. P1–P5, with the numbers

| | Prediction | Result | Verdict |
|---|---|---|---|
| **P1** | image K = 3 carried tile-MCC beats `FOURTH-N1-oracle` (0.7471) by **≥ +0.02**, BH-significant | **0.7648** vs 0.7471 = **+0.0177**, BH *p* < 0.0001; **+0.0185** at the rung's MCC oracle | **NEAR MISS** — significant and in the predicted direction, but short of the +0.02 threshold and above the ≤ +0.01 informative-failure band. The card defined no verdict for the interval between the two, so +0.0177 falls in a GAP in the prediction's design; the threshold was not met |
| **P2** | K = 1 MCC **≥** K = 3 MCC; F1 lower at K = 1 | MCC **rises** with K on both arms: arm 2 0.7569 → **0.7648** (+0.0078, BH p **0.0022**); arm 1 0.7324 → 0.7490. F1 lower at K = 1 on both (0.8719 < 0.9199; 0.8477 < 0.9025) | **INFORMATIVE FAIL** on the MCC claim, significantly reversed; the F1 half holds |
| **P3** | F1 @ 50 m at K = 3 within **± 0.02** of the 3.7 text arm 2 at N = 3 (0.8848) | **0.9199** vs 0.8848 = **+0.0351**, BH *p* < 0.0001 | **INFORMATIVE FAIL**, in the image modality's favour — not parity |
| **P4** | arm 2 beats arm 1 on MCC by **≥ +0.01** | K = 3: **+0.0158** (0.7648 − 0.7490). K = 1: **+0.0245** (0.7569 − 0.7324) | **HOLDS** at both rungs |
| **P5** | carried-vs-oracle tax **≤ 0.01** on both metrics, per rung | `IMG-ARM2-K3` F1 **+0.0007** / MCC **+0.0008**; `IMG-ARM2-K1` +0.0023 / +0.0045; `IMG-ARM1-K3` +0.0000 / +0.0087; `IMG-ARM1-K1` **+0.0129 / +0.0199** | **HOLDS on 3 rungs of 4**; fails only on `IMG-ARM1-K1` |

**The headline the predictions do not capture.** The all-3.7 image K = 3 cell
at its carried point leads the 55-map corpus on **both** metrics, and every one
of the ten tests is BH-significant:

| Comparator | its MCC | Δ MCC | BH p | its F1 | Δ F1 | BH p |
|---|---:|---:|---:|---:|---:|---:|
| `FOURTH-N1-oracle` | 0.7471 | **+0.0177** | < 0.0001 | 0.8352 | **+0.0848** | < 0.0001 |
| `ARM2-N3-oracle` | 0.7163 | **+0.0484** | < 0.0001 | 0.8848 | **+0.0351** | < 0.0001 |
| `ARM2-N5-oracle` | 0.7147 | **+0.0501** | < 0.0001 | 0.8871 | **+0.0328** | < 0.0001 |
| `IM-k3` | 0.7110 | **+0.0538** | < 0.0001 | 0.8008 | **+0.1191** | < 0.0001 |
| `IMG-ARM2-K1-carried` | 0.7569 | **+0.0078** | 0.0022 | 0.8719 | **+0.0480** | < 0.0001 |

So the campaign's substantive question — does the image modality's tile-MCC
advantage transfer from the Gold Standard to deployment? — is answered **yes**,
significantly, even though P1's particular threshold was not met. The
`IM-k3` comparison carries a caveat: that cell's own `source_tile` reproduces
this chain's tile-assignment writer at only 83.65 %, because the tile-MCC
tiering scored the original verified file in place (deltas § 10.7).

## 2. Both arms × both rungs

Twelve cells; the carried points were fixed on a Gold Standard K = 3
calibration leg before any 55-map scoring, and both oracles are reported
beside them so the transfer tax is visible.

| Cell | point | n | F1 @ 50 | tile-MCC | MCC 95 % CI | tp | fp | fn | tn | sens | spec |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `IMG-ARM1-K1-carried` | (0.10, k1) | 6,250 | 0.8477 | 0.7324 | [0.7175, 0.7463] | 2,693 | 275 | 836 | 4,737 | 0.7631 | 0.9451 |
| `IMG-ARM1-K1-f1-oracle` | (0.15, k1) | 5,582 | 0.8606 | 0.7523 | [0.7388, 0.7652] | 2,585 | 112 | 944 | 4,900 | 0.7325 | 0.9777 |
| `IMG-ARM1-K1-mcc-oracle` | (0.15, k1) | 5,582 | 0.8606 | 0.7523 | [0.7388, 0.7652] | 2,585 | 112 | 944 | 4,900 | 0.7325 | 0.9777 |
| `IMG-ARM1-K3-carried` | (0.10, k3) | 5,437 | 0.9025 | 0.7490 | [0.7351, 0.7625] | 2,658 | 183 | 871 | 4,829 | 0.7532 | 0.9635 |
| `IMG-ARM1-K3-f1-oracle` | (0.10, k3) | 5,437 | 0.9025 | 0.7490 | [0.7351, 0.7625] | 2,658 | 183 | 871 | 4,829 | 0.7532 | 0.9635 |
| `IMG-ARM1-K3-mcc-oracle` | (0.15, k3) | 4,977 | 0.8992 | 0.7577 | [0.7444, 0.7702] | 2,568 | 80 | 961 | 4,932 | 0.7277 | 0.9840 |
| `IMG-ARM2-K1-carried` | (0.88, k1) | 5,997 | 0.8719 | 0.7569 | [0.7432, 0.7702] | 2,671 | 165 | 858 | 4,847 | 0.7569 | 0.9671 |
| `IMG-ARM2-K1-f1-oracle` | (0.95, k1) | 5,938 | 0.8742 | 0.7594 | [0.7459, 0.7725] | 2,661 | 148 | 868 | 4,864 | 0.7540 | 0.9705 |
| `IMG-ARM2-K1-mcc-oracle` | (0.98, k1) | 5,322 | 0.8721 | 0.7614 | [0.7491, 0.7737] | 2,519 | 31 | 1,010 | 4,981 | 0.7138 | 0.9938 |
| **`IMG-ARM2-K3-carried`** | (0.88, k3) | 5,357 | **0.9199** | **0.7648** | [0.7516, 0.7776] | 2,659 | 127 | 870 | 4,885 | 0.7535 | 0.9747 |
| `IMG-ARM2-K3-f1-oracle` | (0.90, k3) | 5,343 | 0.9206 | 0.7654 | [0.7524, 0.7784] | 2,657 | 123 | 872 | 4,889 | 0.7529 | 0.9755 |
| `IMG-ARM2-K3-mcc-oracle` | (0.96, k2) | 5,167 | 0.8882 | 0.7656 | [0.7534, 0.7780] | 2,534 | 28 | 995 | 4,984 | 0.7181 | 0.9944 |

## 3. Why MCC rises with K here, and falls everywhere else

P2 was called low-risk: tile-MCC falls monotonically with K on all three
committed deployment ladders. It rose on both image arms instead, and the
mechanism is visible on the proposer side before any score is taken.

| Ladder | MCC at K/N = 1 | 3 | 5 |
|---|---:|---:|---:|
| text arm 1 | 0.7246 | 0.7179 | 0.7147 |
| text arm 2 | 0.7422 | 0.7163 | 0.7147 |
| **image arm 1** | 0.7324 | **0.7490** | — |
| **image arm 2** | 0.7569 | **0.7648** | — |

The three image passes deduplicate to **7,123 / 7,103 / 7,125** candidates, and
their three-pass first-N union is only **8,337**. One pass therefore supplies
**84 %** of the K = 3 candidate set, and the measured K = 1 : K = 3 ratio is
**0.838** where the text campaign's was 0.647. Extra image passes add very
little new geometry; what they add is **corroboration**. So at unanimity the
vote threshold acts as a **precision filter** rather than a recall lever, and
that is what the confusion matrices show: false-positive tiles fall
275 → 183 on arm 1 and 165 → 127 on arm 2 as K goes 1 → 3, while true positives
barely move (2,693 → 2,658 and 2,671 → 2,659).

This sharpens deltas § 10.5, which read the 55-map MCC ceiling as a
**specificity** target — `FOURTH-N1-oracle` leads on 45 false-positive tiles
despite having the field's *lowest* sensitivity. The image K = 3 cell reaches
0.7648 by the same route: 127 FP tiles at sensitivity 0.7535. Pushed further,
its MCC oracle reaches 28 FP tiles — fewer than the incumbent leader's 45 —
at MCC 0.7656.

**The generalisation.** For a **text** pool, K buys recall and costs
specificity, so tile-MCC falls while F1 rises. For an **image** pool, whose
passes largely agree, K buys specificity at almost no cost in recall, so
tile-MCC and F1 rise together. Pass count is not a single lever with a single
sign; its sign depends on how much the passes disagree.

## 4. The deployment-scale modality difference-in-differences

Pre-specified in deltas § 10.6 as (image arm 2 − arm 1) − (text arm 2 − arm 1)
at matched K, on the same 8,541-tile frame.

| Rung | Metric | Image effect | Text effect | Difference-in-differences |
|---|---|---:|---:|---:|
| K = 3 | tile-MCC | **+0.0158** | **−0.0016** | **+0.0174** |
| K = 3 | F1 @ 50 m | +0.0174 | +0.0143 | +0.0031 |
| K = 1 | tile-MCC | +0.0245 | +0.0176 | +0.0069 |
| K = 1 | F1 @ 50 m | +0.0242 | +0.0197 | +0.0045 |

The K = 3 MCC row is the result worth carrying: **the 3.7 verifier seat buys
tile-MCC for an image pool and nothing at all for a text pool.** On text at
this rung the verifier upgrade is worth +0.0143 F1 and −0.0016 MCC — it buys
localisation and no discrimination. On image it is worth +0.0174 F1 *and*
+0.0158 MCC. The modality and the verifier seat interact; they are not two
independent increments.

## 5. Audited costs, per leg, against the card

Audited basis throughout — cache-aware, thinking-inclusive, at the tier
actually used, per `reports/token-load-audit-2026-06-12.md` § 2. The metas'
own `cost_estimate` is never used: on the proposer it reads US$603.8936
against US$245.6307 audited (the Gemini-3-rate artefact of blocker B3), and on
every verifier arm it reads exactly **2 ×** audited, which is the flex
correction.

| Leg | Card | Audited | Note |
|---|---:|---:|---|
| GS K = 3 calibration leg, both arms | 1.2 | **1.1221** | union 622, not ≈ 450 |
| 5-tile mechanism smoke | — | **≈ 0.025** | |
| Proposer pass 1 | ≈ 79 | **81.9283** | cache 0.808 |
| Proposer pass 2 | ≈ 79 | **81.8712** | cache 0.810 |
| Proposer pass 3 | ≈ 79 | **81.8313** | cache 0.811 |
| **Proposer, 73,683 tile-passes** | **237** | **245.6307** | US$0.00333 per tile-pass |
| K = 1 arm 1 (`gemini-3-flash`) | — | **4.9626** | 6,985 cands, 0 retries |
| K = 1 arm 2 (`gemini-3.7-flash`) | — | **7.7028** | main 7.6875 + cleanup 0.0153; 12,247 retries |
| K = 3 arm 1 | — | **5.9058** | 8,337 cands, 9 retries |
| K = 3 arm 2 | — | **9.2650** | main 9.2638 + cleanup 0.0012; 9,045 retries |
| **Four verifier arms** | **37.4** | **27.8361** | US$0.000710 / 0.001103 per candidate |
| **Campaign total** | **≈ 261–276** | **274.6139** | US$145.39 clear of the US$420 hard stop |

Per-pass proposer cost was flat to **0.12 %** (81.9283 / 81.8712 / 81.8313) and
the cached share held at 0.808 / 0.810 / 0.811 straight through the flex
congestion window. The verifier arms take **no** caching at all (cache share
0.000): every crop is a distinct image. Each arm 2 leg's audited cost is the
**sum of two metas**, because `run_pv.py cleanup` rewrites `run.meta.json` with
the retry pass's usage only — an audit reading one file understates those legs
by three orders of magnitude (post-run report § 3.1).

The card's four-arm estimate of US$37.4 was **26 % high**; its K = 3 union
estimate of ≈ 8,500 was within 1.9 % of the actual 8,337, while the deltas
report's upward revision to ≈ 9,000–10,900 overshot. The K = 1 estimate of
≈ 5,500 was 27 % low, for the inter-pass-agreement reason in § 3.

## 6. What did NOT change

- **No board and no tiering was re-tiered**, and **no signed row was touched.**
  `results/55map-final-board-r2-2026-09-06/` and
  `results/metric-leaderboards/55map-mcc-tiering-r2.md` are untouched; this
  campaign's cells live only in its own results tree.
- **The analysis row is UNSIGNED** — `manually_verified_at` is null, per the
  card.
- **No prompt or input configuration changed.** The proposer invocation is
  byte-identical to the Gold Standard 3.7 image run's, on the payload
  fingerprint `e169b723…`; the verifier config is `verify_adversarial-text` at
  T = 0.0 for both arms.
- **The carried operating points are as fixed on 2026-09-13**, before any
  55-map scoring: arm 1 (0.10, k3), arm 2 (0.88, k3), with `k` collapsing to 1
  at the K = 1 rung.
- **The geometric tile-join question remains open with the PI.** It moves 146
  committed cells by roughly a tenth of an MCC and was not touched. What this
  campaign changed is only that its *own* detections are booked on the
  vocabulary the published `id` join already requires — the same writer, and
  the same rule, as the comparators (deltas § 10.7).
- **Nothing on sapphire's main checkout was written.**

## 7. Limitations

- **P1's threshold is the card's, and it was not met.** +0.0177 is significant
  and the leader is displaced, but a reader who wants the prediction honoured
  as written should record it as a miss, not round it up.
- **The K ladder stops at 3.** Whether image tile-MCC keeps rising at K = 5 or
  turns over is untested, and § 3's mechanism predicts it should saturate once
  unanimity stops removing false positives.
- **`IM-k3`'s tile assignment is not this chain's** (83.65 % idempotent), so
  that one comparison of the five mixes assignment rules. The other four do
  not.
- **One MCC oracle sits at k2, not unanimity** (`IMG-ARM2-K3-mcc-oracle`, at
  (0.96, k2)), so the "unanimity is the precision lever" reading of § 3 is a
  statement about the carried points and the ladder, not about every point on
  the grid.
- **The two verifier arms differ in model *and* thinking level** (Gemini 3
  MINIMAL against 3.7 low), as the mirrored text 2×2 did, so P4's "verifier
  seat" effect is the seat as a package, not the model alone.

## Changelog

### 2026-09-16 — p-value rendering, the P1 gap, and IM-k3's join

PI review of the campaign before signature. Three corrections, none of which
moves a measurement:

| Claim | Before | After |
|---|---|---|
| Permutation p-values | `BH p 0.0000` | **BH *p* < 0.0001** |
| P1's verdict band | "near miss", band unstated | the card's **gap** named: success ≥ +0.02, informative failure ≤ +0.01, and +0.0177 falls between them |
| `IM-k3` tile join | "83.65 % idempotent — scored in place" | **not a defect**: its `source_tile` vocabulary is 100 % inside the scoring frame (2,664 of 2,664 names; 4,680 of 4,680 features). The 83.65 % is a CONVENTION difference, not an invalid join |

**p-values.** A permutation p-value over 10,000 draws is bounded below by
1/10,000. Reporting `0.0000` reads as *p* = 0, which no permutation test can
produce. The raw zeros remain in `tests_IMG-ARM2-K3-carried.json`; only the
rendering changed. Propagated to the card § 4a and the register row's outcome.

**P1's gap.** The card specified success at ≥ +0.02 and informative failure at
≤ +0.01, and said nothing about the interval between. The observed +0.0177
falls in it. The verdict "near miss" stands and the threshold was genuinely
not met — but it is a gap in the prediction's design, not a property of the
result, and is now stated as such rather than glossed.

**`IM-k3`.** Re-checked against `55maps_evaluation_bounds.geojson` directly:
all 2,664 of its distinct `source_tile` names are frame tiles and all 4,680 of
its features book onto one, so its confusion matrix (summing to 8,541) is
sound and the five-test family is not compromised. What the 83.65 % figure
measures is that re-applying `assign_standard_tile` would MOVE 16.35 % of its
detections to a different frame tile — the origin-tile convention against the
nearest-standard-centroid convention. Both are well defined. The other three
comparators are 100 % idempotent because they were produced BY that writer.
Reconciling them is a $0 on-disk re-score, but it would move `IM-k3`'s
published MCC and therefore the eight-cell tiering where it is sole Tier 1, so
it is the PI's call and is not done here.

### 2026-09-14 — Original publication

First publication, at campaign completion. Written from the twelve committed
`evaluation.json` files and
`results/gemini37-image-55map-2026-09-13/tests_IMG-ARM2-K3-carried.json`, with
the comparators read from
`results/55map-final-board-r2-2026-09-06/final_board_50m.json` and the audited
costs recomputed from each leg's metas rather than carried from any prior note.

Upstream commits this document rests on: `e0f9a4d03` (the 179-point sweep and
the twelve materialised cells), `392a06933` (the engine scores and the
five-test family), `9fd928af3` (registration, one UNSIGNED analysis row), and
`7ed157a32` (the tile-assignment fix and its two new gates, without which no
figure here would exist).

State at publication: P1 NEAR MISS, P2 and P3 INFORMATIVE FAIL, P4 HOLDS, P5
holds on three rungs of four; audited spend US$274.6139 of a US$420 hard stop;
no board re-tiered, no signed row touched, and the analysis row unsigned.
