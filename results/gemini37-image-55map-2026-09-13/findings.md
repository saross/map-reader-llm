# Gemini 3.7 image at deployment scale, K = 3 and K = 5: findings

> **Last revised**: 2026-09-19 (the **K = 5 rung added** — six further cells on
> the two image arms, swept, materialised and scored on the same r2 engine,
> after proposer passes 4 and 5 were run through the Batch API. The rung is
> declared **EXPLORATORY**: it was not in the card, no permutation test was run
> at K = 5, and it changes no P1–P5 verdict). Prior: 2026-09-16 (permutation
> p-values reported as *p* < 0.0001
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

## 2. Both arms × all three rungs

Eighteen cells; the carried points were fixed on Gold Standard calibration legs
before any 55-map scoring, and both oracles are reported beside them so the
transfer tax is visible. The twelve K = 1 and K = 3 cells are the ladder the
card specified; the six K = 5 cells were added on 2026-09-17/19 and are
**exploratory** (§ 7). Their carried points are the registered Gold Standard
K = 5 cells' — `g37-image-k5-verified-carried-p0.10-k5` and
`g37-image-k5-verified-swap37-p0.90-k5` in `results/run-conditions.json` — so
arm 2 carries **0.90** at this rung, not the K = 3 leg's 0.88.

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
| `IMG-ARM1-K5-carried` | (0.10, k5) | 5,297 | 0.9130 | 0.7529 | [0.7394, 0.7662] | 2,652 | 164 | 877 | 4,848 | 0.7515 | 0.9673 |
| `IMG-ARM1-K5-f1-oracle` | (0.10, k5) | 5,297 | 0.9130 | 0.7529 | [0.7394, 0.7662] | 2,652 | 164 | 877 | 4,848 | 0.7515 | 0.9673 |
| `IMG-ARM1-K5-mcc-oracle` | (0.15, k5) | 4,885 | 0.9060 | 0.7542 | [0.7409, 0.7670] | 2,564 | 89 | 965 | 4,923 | 0.7266 | 0.9822 |
| `IMG-ARM2-K5-carried` | (0.90, k5) | 5,219 | 0.9270 | 0.7659 | [0.7528, 0.7790] | 2,648 | 114 | 881 | 4,898 | 0.7504 | 0.9773 |
| `IMG-ARM2-K5-f1-oracle` | (0.95, k5) | 5,197 | 0.9280 | 0.7681 | [0.7552, 0.7811] | 2,644 | 103 | 885 | 4,909 | 0.7492 | 0.9794 |
| `IMG-ARM2-K5-mcc-oracle` | (0.95, k5) | 5,197 | 0.9280 | 0.7681 | [0.7552, 0.7811] | 2,644 | 103 | 885 | 4,909 | 0.7492 | 0.9794 |

The exploratory `IMG-ARM2-K5-carried` cell scores above the K = 3 headline cell
on both metrics (0.9270 against 0.9199 F1; 0.7659 against 0.7648 tile-MCC), and
its F1 oracle and MCC oracle coincide at (0.95, k5). No test was run at this
rung, so § 1's headline — which is the reading of the declared five-test family
— stands on the K = 3 cell, and the K = 5 numbers are reported as a direction
(§ 7).

## 3. Why MCC rises with K here, and falls everywhere else

P2 was called low-risk: tile-MCC falls monotonically with K on all three
committed deployment ladders. It rose on both image arms instead, and the
mechanism is visible on the proposer side before any score is taken.

| Ladder | MCC at K/N = 1 | 3 | 5 |
|---|---:|---:|---:|
| text arm 1 | 0.7246 | 0.7179 | 0.7147 |
| text arm 2 | 0.7422 | 0.7163 | 0.7147 |
| **image arm 1** | 0.7324 | **0.7490** | **0.7529** |
| **image arm 2** | 0.7569 | **0.7648** | **0.7659** |

The text rows' K/N = 5 entries are that campaign's committed N = 5 oracle cells;
the image rows' are this document's exploratory K = 5 carried cells, added
2026-09-17/19 and never tested (§ 7).

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

**K = 5 extends the mechanism and puts the knee at 3.** Two further passes
deduplicate to **7,142** and **7,122** candidates — the same per-pass yield as
the first three (7,123 / 7,103 / 7,125) — and the five-pass first-N union is
**9,173** against 8,337 at K = 3 and 6,985 at K = 1. So a fourth and fifth pass
add 836 candidates between them, 10 % on the K = 3 union, and **5,593 of the
9,173 (61 %)** carry all five votes: the votes split
{1: 1,887, 2: 802, 3: 453, 4: 438, 5: 5,593}. Unanimity therefore keeps acting
as a precision filter, and with a longer lever: on arm 2, false-positive
*detections* fall **1,195 → 585 → 474** and false-positive *tiles*
**165 → 127 → 114** as K goes 1 → 3 → 5, while recall slips only
**0.957 → 0.951 → 0.946** and true-positive tiles **2,671 → 2,659 → 2,648**. On
arm 1 the same three steps read 275 → 183 → **164** FP tiles against
2,693 → 2,658 → **2,652** TP tiles. But the returns are sharply diminishing:
tile-MCC gains **+0.0166** (arm 1) and **+0.0079** (arm 2) from K = 1 to K = 3,
then only **+0.0039** and **+0.0011** from K = 3 to K = 5, with F1 gaining
**+0.0105** and **+0.0071** across that second step. The mechanism does not turn
over by K = 5 — it saturates, as the account above predicts — and **K = 3 is
the knee**, which is the rung at which the card stopped the ladder
(`planning/gemini37-image-55map-2026-09-13.md:279`).

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
| **Campaign total, at the K = 3 close** | **≈ 261–276** | **274.6139** | US$145.39 clear of the US$420 hard stop |
| Proposer pass 4 (batch) | — | **61.8648** | cache 0.945; 7 jobs of ≤ 4,000 tiles |
| Proposer pass 5 (batch) | — | **61.9455** | cache 0.945; 7 jobs of ≤ 4,000 tiles |
| **Proposer pool, 122,805 tile-passes** | — | **369.4409** | US$0.00301 per tile-pass |
| K = 5 union and crops | — | **0.00** | 9,173 candidates, 9,173 / 9,173 cropped |
| K = 5 arm 1 (`gemini-3-flash`) | — | **6.4896** | 9,173 cands, 52 server-error retries |
| K = 5 arm 2 (`gemini-3.7-flash`) | — | **10.1788** | main 8.5430 + cleanups 1.5995 + 0.0364; 48,616 retries |
| Batch-vs-flex probe, 200 candidates | — | **0.2248** | `probe-batch-vs-flex-2026-09-19/` |
| **Six verifier arms** | — | **44.5045** | US$0.000707 / 0.001110 per candidate at K = 5 |
| **Campaign total, as extended to K = 5** | — | **415.3174** | 274.6139 + 140.7035 |

Per-pass proposer cost was flat to **0.12 %** (81.9283 / 81.8712 / 81.8313) and
the cached share held at 0.808 / 0.810 / 0.811 straight through the flex
congestion window. The verifier arms take **no** caching at all (cache share
0.000): every crop is a distinct image. Each arm 2 leg's audited cost is the
**sum of two metas**, because `run_pv.py cleanup` rewrites `run.meta.json` with
the retry pass's usage only — an audit reading one file understates those legs
by three orders of magnitude (post-run report § 3.1).

**The K = 5 extension, and the batch route.** Passes 4 and 5 were run through
the **Batch API** in seven chunks of at most 4,000 tiles each
(`outputs/gemini37-image-55map-2026-09-13/batch_run4.log:14`), because
`gemini-3.7-flash` on flex returned 503 for more than twelve hours on
2026-09-16/17 while batch served the same model in minutes
(`reports/flex-tier-503-2026-09-16.md`); the batch-layout passes were then
folded into the pool by `scripts/normalise_pass_layout.py`. Explicit context
caching on that path held a cached share of **0.945**, against 0.808–0.813 on
flex with implicit caching, so each batch pass cost **US$61.9** against
**US$81.9** on flex — **24 % less** for an identical payload, and the pool's
per-tile-pass cost falls from US$0.00333 to **US$0.00301**. The pool meta's own
`cost_estimate` now reads US$1,006.3582 against US$369.4409 audited, the
same blocker-B3 artefact at a larger scale.

**Where this leaves the envelope.** The campaign closed at K = 3 on
US$274.6139 against the card's US$420 hard stop. The K = 5 extension added
**US$140.7035** — 61.8648 + 61.9455 (passes 4–5) + 6.4896 + 10.1788 (both
arms) + 0.2248 (the probe), the union and crops being free — so the campaign as
extended stands at **US$415.3174**, inside the original hard stop by
**US$4.68**. That headroom is incidental rather than planned: passes 4 and 5
were approved separately, under the image-campaign envelope (S154), not against
this card's stop.

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
  at the K = 1 rung. The K = 5 rung carries the registered Gold Standard K = 5
  cells' points instead — arm 1 (0.10, k5) and arm 2 (**0.90**, k5) — which is
  a different probability on arm 2, not a re-tuning of the K = 3 one.
- **The K = 1 and K = 3 cells are untouched.** All twelve evaluations, the
  P1–P5 verdicts, the declared five-test family and its ten BH-significant
  results stand exactly as published on 2026-09-14. The K = 5 rung adds six
  cells beside them and re-scores none of them; the board is likewise
  untouched.
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
- **The K = 5 rung is EXPLORATORY, and untested.** The ladder now reaches 5,
  and § 3's prediction is borne out — tile-MCC still rises, by +0.0039 (arm 1)
  and +0.0011 (arm 2), roughly a quarter and an eighth of the K = 1 → 3 gains —
  but the K = 3 → K = 5 contrast was **not preregistered** (the card ends the
  ladder at 3), was declared exploratory by the PI on 2026-09-19, and **no
  permutation test has been run at K = 5**: `--stage tests` is K = 3-primary and
  the declared five-test family is closed.
- **The K = 5 increments are inside the drift band.** Arm 2's +0.007 F1 is
  smaller than the movement that re-invoking the verifier can produce on its
  own. Erratum E89 records that independent T = 0.0 re-invocations are not
  reproducible, and a batch-vs-flex probe over 200 K = 5 candidates on
  2026-09-19 measured **5.3 %** of decisions flipping at the 0.90 threshold
  against a same-route twin baseline of **3.5 %**, with about 40 % of
  probabilities differing in both comparisons
  (`outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/probe-batch-vs-flex-2026-09-19/README.md`).
  Read the K = 5 rung as a direction, not as a measured increment.
- **The K = 5 step moves the operating point as well as K.** Arm 2 carries 0.90
  at K = 5 against 0.88 at K = 3, because each rung carries its own registered
  Gold Standard cell, so that arm's K = 3 → K = 5 difference is not a clean
  single-factor contrast.
- **The K = 5 pool mixes serving routes.** Passes 1–3 ran on flex realtime with
  implicit caching, passes 4–5 on the Batch API with explicit caching. The
  probe above found the batch route's drift indistinguishable from the route's
  own re-invocation drift, so this is a recorded caveat rather than a measured
  effect.
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

### 2026-09-19 — the K = 5 rung, added and declared exploratory

**Trigger**: the image proposer × verifier 2×2 acquired a K = 5 cell per row.
Proposer passes 4 and 5 were run on 2026-09-17 through the Batch API — flex
having returned 503 on `gemini-3.7-flash` for more than twelve hours
(`reports/flex-tier-503-2026-09-16.md`) — the five-pass union was built, both
verifier arms run, and six further cells swept, materialised and scored on the
same r2 engine with all six selftest gates passing. The contrast was **not**
preregistered: the card ends the ladder at 3
(`planning/gemini37-image-55map-2026-09-13.md:279`), and the PI declared the
rung EXPLORATORY on 2026-09-19.

| Claim | Before | After |
|---|---:|---:|
| Cells in this document | 12 | **18** |
| Ladder, image arm 1 tile-MCC at K = 5 | — | **0.7529** |
| Ladder, image arm 2 tile-MCC at K = 5 | — | **0.7659** |
| Best arm 2 carried F1 @ 50 m | 0.9199 (K = 3) | **0.9270** (K = 5, exploratory) |
| Proposer pool | 73,683 tile-passes, US$245.6307 | **122,805 tile-passes, US$369.4409** |
| Proposer, per tile-pass | US$0.00333 | **US$0.00301** (cache 0.945 on batch) |
| Verifier arms | four, US$27.8361 | **six, US$44.5045** |
| Campaign audited total | US$274.6139 | **US$415.3174** |

**The mechanism holds, and the knee is at 3.** The five-pass union is 9,173
against 8,337 at K = 3, 61 % of it unanimous; false-positive tiles fall on to
164 (arm 1) and 114 (arm 2) while true positives barely move. But tile-MCC
gains only +0.0039 and +0.0011 across K = 3 → K = 5, against +0.0166 and
+0.0079 across K = 1 → K = 3 (§ 3).

**No test was run at K = 5.** `--stage tests` is K = 3-primary and the declared
five-test family is closed, so the rung carries no p-value. Arm 2's +0.007 F1
increment also sits inside the verifier's own re-invocation drift band (E89;
the 2026-09-19 batch-vs-flex probe measured 5.3 % decision flips at 0.90
against a 3.5 % same-route baseline), and arm 2's carried probability differs
between the rungs (0.88 at K = 3, 0.90 at K = 5). All three caveats are in § 7.

**What did NOT change**: every K = 1 and K = 3 cell and its evaluation, the
P1–P5 verdicts, the declared five-test family and its ten BH-significant
results, the scoring instrument, the carried points for K = 1 and K = 3, the
55-map board and the tile-MCC tiering (neither re-tiered), every signed row,
and the analysis row's UNSIGNED status. The six K = 5 cells' standing in the
registry, and any decision to test the contrast, are with the PI.

Landed in `3a9a39836`.

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
