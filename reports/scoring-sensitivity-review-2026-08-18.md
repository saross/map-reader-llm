# Scoring-path sensitivity review: missing within-pass deduplication and order-dependent tile assignment

> **Last revised**: 2026-08-18 (original publication — S136 review of the two
> scoring-path findings surfaced while building the H13 overlap chain). See
> [§ Changelog](#changelog) for revision history.

**Date**: 2026-08-18 (Session 136)
**Author**: Claude Code (Opus 5), amd-tower; all measurement executed on sapphire
**API spend**: US$0.00 — every number below is recomputed from committed artefacts
**Scope**: `scripts/evaluate_detections.py`, `scripts/lib_advanced_metrics.py`,
`scripts/merge_passes.py`, `scripts/extract_candidates.py`, and all 333
conditions in `results/conditions-manifest.json`
**Artefacts**: `results/scoring-sensitivity-2026-08-18/` (exposure register,
five probe batches with their specs); erratum
[E79](../docs/methodology/preregistration/protocol-errata.md)

---

## TL;DR

1. **Both mechanisms are real and are verified at source.** The scorer has no
   deduplication step, and it books ambiguous detections to a tile by row order.
2. **The two exposures are almost disjoint.** Missing deduplication touches
   **155 of 333 conditions**; the tile-assignment tie-break touches **123**; only
   **6** conditions sit in both.
3. **The deduplication exposure is larger and more consequential than the brief
   assumed, and it is NOT confined to single-pass conditions.** Twenty-six
   **proposer-verifier** conditions carry 15–25 % duplicate load, including
   **twelve rows of the `gs-era2-pv-family-30m` leaderboard**. Architecture
   labels are the wrong discriminator; the artefact must be measured.
4. **The effect is roughly three times larger in F1 than the ~6 % count
   inflation suggests.** Across 48 measured cells, deduplication moves F1@20
   by **+0.009 to +0.058**, with recall *exactly* unchanged in almost every
   cell — decisive evidence that the removed features are pure duplicates
   scoring as false positives.
5. **Two paper-cited claims are materially at risk**, both because they compare
   an exposed cell against an unexposed one:
   - the `diversity-dividend-384` **Tier-1 three-member tie** — the "cheap Flash
     consensus reaches the expensive Pro single-pass tier" headline — where the
     two Pro single-pass members rise past the consensus champion; and
   - the § R5 **zero-diversity anchor** (`verified-adv-text-baseline`,
     F1@30 0.8320 → **0.8905**), which on its face moves that cell from 29th to
     13th of the 39 rows on `gs-era2-pv-family-30m`.
6. **The study's two headline numbers are safe.** The GS headline
   (`verified-adv-text-consensus-16of30`) and the 55-map deployment headline are
   both unexposed or negligibly exposed; the measured 55-map movement is
   **+0.0004 F1@20**.
7. **Recommendation: a targeted re-scoring campaign is warranted; a blanket one
   is not.** About 70 cells across four boards need re-scoring with confidence
   intervals, not all 155 conditions. Detail in
   [§ 6](#6-recommendation).

---

## 1. Mechanism 1 — no within-pass deduplication

### 1.1 Verified at source

`scripts/evaluate_detections.py` contains no clustering or deduplication step
anywhere in its scoring path. Its per-buffer point estimate comes straight from
`lib_advanced_metrics.calculate_f1_internal`
(`scripts/evaluate_detections.py:430-432`), which runs Hungarian matching over
whatever features it is handed.

The preregistered within-pass deduplication — § 8.5 Step 1, 20 m tolerance —
lives elsewhere, in `scripts/merge_passes.py:137-218`
(`deduplicate_within_pass`, greedy star clustering at
`DISTANCE_THRESHOLD_METRES = 20.0`, `merge_passes.py:71`). Whether a scored set
has been through it is a property of the *path the artefact took*, not of its
architecture label.

The study tiles at **12.5 % overlap** in both axes. Confirmed from the bounds
themselves: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` has 487
tiles of median width 1927.23 m at a 1686.33 m stride (384 px at 5.02 m/px →
336 px stride → 48 px overlap); the 256 px bounds have 1032 tiles of 1284.82 m
at a 1124.22 m stride (224 px stride → 32 px overlap). A mound in an overlap
band is therefore seen and emitted twice, and the second copy scores as a false
positive.

### 1.2 The path that was missed

`merge_passes` is reached by the multi-pass consensus and weighted-box-fusion
paths. It is **not** reached by a proposer-verifier cell whose proposer pool is
a single raw pass: `scripts/extract_candidates.py` crops one candidate per input
feature with no clustering (its only nod to the issue is normalising
`source_tiles` → `source_tile` at `:273-276`), so duplicate proposals become
duplicate crops, are verified independently, and — where both copies clear the
probability threshold — land in the scored accepted set as two detections.

This is why the exposed set had to be established by measurement rather than by
reading `architecture`.

### 1.3 Exposure, measured

`scripts/scoring_sensitivity_survey.py` resolves the scored detection files
behind every condition in `results/conditions-manifest.json` (via each
`evaluation.json`'s `_metadata.input_files`, expanding directory-mode inputs
with the recorded glob), reprojects each to EPSG:32635, and counts the features
lying within 20 m of another feature in the same artefact. Register:
`results/scoring-sensitivity-2026-08-18/exposure-survey.json`.

| Architecture | conditions | duplicate-exposed (>1 %) | median duplicate fraction |
|---|--:|--:|--:|
| single-pass | 125 | 123 | 0.128 |
| consensus | 125 | 6 | 0.000 |
| proposer-verifier | 83 | 26 | 0.0005 |
| **total** | **333** | **155** | — |

All 333 conditions resolved; none was unreadable.

**Reading the 123 single-pass figure.** The genuinely un-deduplicated
single-pass set is **122**: all 125 minus the three `h13::arm-*` conditions,
whose inputs are the `detections_dedup.geojson` files built by
`scripts/prepare_h13_scoring.py`. The register lists 123 because H13 arm C
(50 % overlap) retains a 3.20 % pair fraction after deduplication. That residual
was measured, not assumed: re-running deduplication on arm C removes a further
1.6 % with **recall exactly unchanged** and F1@30 moving 0.4196 → 0.4249, while
arm A removes **zero** further features and does not move at all
(`probe-batch4.json`). Greedy star clustering is therefore not quite idempotent
at 50 % overlap — cluster mean centroids can drift back within 20 m of one
another — but the effect is an order of magnitude below the raw-pass profile.

**The 26 proposer-verifier conditions** are the finding the brief did not
anticipate. They are exactly the cells whose proposer pool was a single raw
pass: every `pv-diag-384::verified-adv-*-baseline*` cell (20–25 % pair
involvement), the whole `proposer-verifier-384` / `proposer-verifier-512`
prompt-variant family (8–16 %), `retest-phase2b::verified-adv-{text,image}-t0.0`
(the `era1-pv-stage-d` `512-single-*-t0.0` corners, 18–21 %), and the three
`55maps-image-generalisation` deployment cells at 1.05 %.

**The 6 consensus conditions** are all low-vote-threshold cells
(`consensus-1of30`, `consensus-2of30`, `consensus-1of5`, `consensus-2of5`,
`brief-text-t03-consensus-1of3`, `image-t03-consensus-1of3`) at 1.6–6.9 %. These
*did* pass through cross-pass clustering, so by analogy with H13 arm C the
residual is most likely the same non-idempotency. **I did not measure it** — see
[§ 5](#5-what-i-could-not-determine).

### 1.4 Effect on F1, measured on 48 cells

`scripts/scoring_sensitivity_probe.py --mode dedup` scores each cell twice from
the same bounds and ground truth: once exactly as committed, once after applying
`deduplicate_within_pass`. The as-committed column **reproduces the committed
`evaluation.json` F1 to four decimal places in every one of the 48 cells**,
which validates the harness.

Single-pass cells (batches 1–2, 34 cells, 158 passes) — selected for paper
relevance and for proximity to a tier or tie boundary:

| Condition | K | raw | dedup | removed | F1@20 | dedup | Δ | F1@30 | dedup | Δ |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `n1-pro-rerun-384::baseline-pro-text-high-t-0-0` | 3 | 443 | 392 | 11.6 % | 0.8045 | 0.8545 | +0.0499 | 0.8266 | 0.8779 | +0.0513 |
| `n1-pro-rerun-384::baseline-pro-text-medium-t-0-7` | 3 | 465 | 415 | 10.8 % | 0.7555 | 0.7984 | +0.0429 | 0.8074 | 0.8549 | +0.0475 |
| `pv-diag-384::baseline-pro-text-medium-t-0-0` | 1 | 446 | 398 | 10.8 % | 0.7764 | 0.8211 | +0.0447 | 0.7968 | 0.8427 | +0.0459 |
| `n1-pro-rerun-384::baseline-pro-image-high-t-0-0` | 3 | 548 | 484 | 11.7 % | 0.6658 | 0.7041 | +0.0384 | 0.7959 | 0.8492 | +0.0532 |
| `pv-diag-384::baseline-pro-text-high-t-0-7` | 10 | 438 | 390 | 11.0 % | 0.7450 | 0.7879 | +0.0429 | 0.7886 | 0.8345 | +0.0459 |
| `retest-phase2e::canonical-last` | 1 | 785 | 723 | 7.9 % | 0.6314 | 0.6593 | +0.0279 | 0.6858 | 0.7195 | +0.0337 |
| `retest-phase2e::config-default` | 1 | 752 | 694 | 7.7 % | 0.6057 | 0.6342 | +0.0285 | 0.6708 | 0.7024 | +0.0316 |
| `retest-phase2d::image-verbose` | 1 | 742 | 692 | 6.7 % | 0.6027 | 0.6271 | +0.0245 | 0.6682 | 0.6954 | +0.0271 |
| `retest-phase2c::image-plus-hp` | 1 | 771 | 723 | 6.2 % | 0.5985 | 0.6212 | +0.0228 | 0.6641 | 0.6894 | +0.0253 |
| `retest-phase2e::canonical-first` | 1 | 771 | 723 | 6.2 % | 0.5985 | 0.6212 | +0.0228 | 0.6641 | 0.6894 | +0.0253 |
| `retest-phase2b::image-t0.0` | 3 | 772 | 721 | 6.7 % | 0.5862 | 0.6086 | +0.0225 | 0.6538 | 0.6806 | +0.0268 |
| `retest-phase2c::image-canonical` | 1 | 720 | 676 | 6.1 % | 0.5814 | 0.6025 | +0.0211 | 0.6529 | 0.6749 | +0.0220 |
| `retest-phase2b::image-t0.3` | 3 | 772 | 722 | 6.5 % | 0.5750 | 0.5948 | +0.0198 | 0.6512 | 0.6772 | +0.0260 |
| `retest-phase2d::image-terse` | 1 | 773 | 725 | 6.2 % | 0.6052 | 0.6234 | +0.0182 | 0.6494 | 0.6741 | +0.0247 |
| `retest-phase2b::text-t0.0` | 3 | 885 | 814 | 8.0 % | 0.6055 | 0.6371 | +0.0316 | 0.6434 | 0.6770 | +0.0336 |
| `retest-phase2c::text-scale-4` | 1 | 882 | 812 | 7.9 % | 0.6094 | 0.6410 | +0.0316 | 0.6404 | 0.6736 | +0.0332 |
| `retest-phase2b::text-t0.3` | 3 | 871 | 804 | 7.8 % | 0.6065 | 0.6351 | +0.0286 | 0.6348 | 0.6659 | +0.0310 |
| `retest-phase2a::brief-text-image` | 3 | 789 | 750 | 4.9 % | 0.5220 | 0.5362 | +0.0142 | 0.6304 | 0.6484 | +0.0180 |
| `pv-diag-384::baseline-flash-image-minimal-t-0-7` | 10 | 758 | 697 | 8.0 % | 0.5534 | 0.5797 | +0.0263 | 0.6302 | 0.6634 | +0.0332 |
| `retest-phase2d::text-verbose` | 1 | 798 | 747 | 6.4 % | 0.5834 | 0.6050 | +0.0216 | 0.6298 | 0.6547 | +0.0250 |
| `retest-phase2a::verbose-text-image` | 3 | 793 | 754 | 5.0 % | 0.5170 | 0.5318 | +0.0148 | 0.6131 | 0.6308 | +0.0178 |
| `retest-phase2b::text-t0.7` | 3 | 934 | 874 | 6.4 % | 0.5842 | 0.6066 | +0.0224 | 0.6122 | 0.6382 | +0.0260 |
| `retest-phase2a::brief-text` | 3 | 944 | 885 | 6.2 % | 0.5518 | 0.5730 | +0.0212 | 0.5958 | 0.6193 | +0.0235 |
| `retest-phase2b::text-t1.3` | 3 | 958 | 899 | 6.2 % | 0.5442 | 0.5625 | +0.0183 | 0.5905 | 0.6140 | +0.0234 |
| `pv-diag-384::baseline-flash-image-high-t-0-7` | 10 | 855 | 797 | 6.9 % | 0.4986 | 0.5199 | +0.0213 | 0.5779 | 0.6050 | +0.0271 |
| `retest-phase2b::text-t1.0` | 3 | 974 | 916 | 6.0 % | 0.5335 | 0.5529 | +0.0194 | 0.5775 | 0.5991 | +0.0216 |
| `retest-phase2a::image-only` | 3 | 854 | 812 | 4.9 % | 0.4697 | 0.4787 | +0.0090 | 0.5740 | 0.5903 | +0.0162 |
| `retest-phase2a::verbose-text` | 3 | 952 | 902 | 5.3 % | 0.5016 | 0.5181 | +0.0165 | 0.5552 | 0.5740 | +0.0188 |
| `pv-diag-384::baseline-flash-text-minimal-t-0-0-pv-baseline` | 1 | 1047 | 974 | 7.0 % | 0.5196 | 0.5465 | +0.0269 | 0.5304 | 0.5578 | +0.0275 |
| `retest-h11-single-pass-384-t0::baseline-flash-text-minimal-t-0-0` | 10 | 1096 | 1019 | 7.1 % | 0.5031 | 0.5299 | +0.0268 | 0.5147 | 0.5422 | +0.0275 |
| `pv-diag-384::baseline-flash-text-minimal-t-0-7` | 30 | 1104 | 1028 | 6.9 % | 0.4883 | 0.5135 | +0.0252 | 0.5058 | 0.5320 | +0.0262 |
| `e47-propose-brief::baseline-single-pass` | 1 | 1180 | 1092 | 7.5 % | 0.4706 | 0.4977 | +0.0271 | 0.4879 | 0.5160 | +0.0281 |
| `pv-diag-384::baseline-flash-text-high-t-0-7` | 30 | 1520 | 1434 | 5.7 % | 0.3871 | 0.4040 | +0.0169 | 0.4063 | 0.4251 | +0.0188 |
| `pv-diag-256::text-baseline` | 1 | 1828 | 1722 | 5.8 % | 0.3417 | 0.3586 | +0.0168 | 0.3453 | 0.3623 | +0.0170 |

Proposer-verifier cells (batch 3, 11 cells):

| Condition | raw | dedup | removed | F1@20 | dedup | Δ | F1@30 | dedup | Δ | P@30 | → | R@30 | → |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `pv-diag-384::verified-adv-text-baseline-pro-vf` | 463 | 405 | 12.5 % | 0.8263 | 0.8833 | +0.0571 | 0.8419 | 0.9000 | +0.0581 | 0.8164 | 0.9333 | 0.8690 | 0.8690 |
| `pv-diag-384::verified-adv-text-baseline-medium-vf` | 465 | 406 | 12.7 % | 0.8244 | 0.8823 | +0.0578 | 0.8400 | 0.8989 | +0.0589 | 0.8129 | 0.9310 | 0.8690 | 0.8690 |
| `pv-diag-384::verified-adv-text-baseline` | 464 | 405 | 12.7 % | 0.8142 | 0.8714 | +0.0572 | 0.8320 | 0.8905 | +0.0584 | 0.8060 | 0.9235 | 0.8598 | 0.8598 |
| `retest-phase2b::verified-adv-text-t0.0` | 525 | 469 | 10.6 % | 0.7703 | 0.8128 | +0.0425 | 0.8110 | 0.8558 | +0.0448 | 0.8221 | 0.9197 | 0.8002 | 0.8002 |
| `pv-diag-384::verified-adv-image-baseline-pro-vf` | 509 | 452 | 11.2 % | 0.7309 | 0.7734 | +0.0425 | 0.7966 | 0.8478 | +0.0512 | 0.7387 | 0.8319 | 0.8644 | 0.8644 |
| `pv-diag-384::verified-adv-pro-text-baseline` | 394 | 350 | 11.2 % | 0.7696 | 0.8127 | +0.0431 | 0.7889 | 0.8331 | +0.0442 | 0.8299 | 0.9343 | 0.7517 | 0.7517 |
| `pv-diag-384::verified-adv-image-baseline` | 511 | 453 | 11.4 % | 0.7167 | 0.7590 | +0.0423 | 0.7822 | 0.8333 | +0.0511 | 0.7241 | 0.8168 | 0.8506 | 0.8506 |
| `pv-diag-384::verified-adv-pro-image-baseline` | 485 | 433 | 10.7 % | 0.6196 | 0.6452 | +0.0256 | 0.7522 | 0.7972 | +0.0451 | 0.7134 | 0.7991 | 0.7954 | 0.7954 |
| `retest-phase2b::verified-adv-image-t0.0` | 561 | 512 | 8.8 % | 0.6739 | 0.7037 | +0.0297 | 0.7467 | 0.7817 | +0.0351 | 0.7320 | 0.8026 | 0.7619 | 0.7619 |
| `proposer-verifier-384::verified-checklist-text` | 336 | 308 | 8.3 % | 0.5214 | 0.5411 | +0.0196 | 0.5318 | 0.5518 | +0.0200 | 0.6101 | 0.6656 | 0.4713 | 0.4713 |
| `proposer-verifier-384::verified-adversarial-text` | 215 | 198 | 7.9 % | 0.4708 | 0.4834 | +0.0126 | 0.4769 | 0.4897 | +0.0128 | 0.7209 | 0.7828 | 0.3563 | 0.3563 |

**Recall is bit-identical before and after at 30 m in all eleven
proposer-verifier cells**, and unchanged in 33 of the 68 single-pass
cell–buffer pairs; where it moves at all it drops by at most 0.0115
(deduplication occasionally merges detections of two genuinely distinct mounds
lying under 20 m apart, which is why the movement concentrates at the tighter
20 m buffer). Precision does all the work — 0.8060 → 0.9235 at 30 m on the
zero-diversity anchor. That pattern is exactly what the duplicate hypothesis
predicts and is the strongest single piece of evidence that these are artefacts
rather than detections.

**Magnitude scales with detection density, not uniformly.** Removal fractions
span 4.9 % (`retest-phase2a::image-only`) to 12.7 %
(`verified-adv-text-baseline`). Paired contrasts therefore do **not** cancel.

Deployment corpus (batch 5): `55maps-image-generalisation::verified` removes 24
of 4680 features (0.5 %) and moves **F1@20 0.5082 → 0.5086 (+0.0004)**,
F1@50 0.7747 → 0.7764. Negligible.

---

## 2. Mechanism 2 — order-dependent tile assignment

Fully documented in **erratum E79**
(`docs/methodology/preregistration/protocol-errata.md`), which this review
drafted; only the summary is repeated here.

`calculate_f1_internal` (`scripts/lib_advanced_metrics.py:1106-1184`) matches
**per map sheet**, scoping detections by `source_tile` string prefix at `:1159`.
When an artefact carries no `source_tile` — true of every `merge_passes`
consensus output, which writes `source_tiles` plural —
`scripts/evaluate_detections.py:1431-1444` derives one as the **first
intersecting bounds tile in row order**. The principled alternative,
nearest tile centroid, is already applied to references at
`lib_advanced_metrics.py:746-801` and to detections in the H13 chain at
`scripts/prepare_h13_scoring.py:287-334`.

Measured on 14 consensus cells (`probe-batch1.json`, `probe-batch4.json`); the
committed rule reproduces every committed value exactly:

| Condition | n | >1 tile | Δtile | Δ**sheet** | F1@20 first | nearest | Δ |
|---|--:|--:|--:|--:|--:|--:|--:|
| `pv-diag-384::flash-minimal-text-n30-t07-text-t1.0-consensus-9of10` | 549 | 195 | 90 | 10 | 0.6667 | 0.6565 | −0.0102 |
| `pv-diag-384::flash-high-text-n5-text-t0.7-consensus-26of30` | 415 | 150 | 63 | 7 | 0.8141 | 0.8047 | −0.0094 |
| `pv-diag-384::flash-high-text-n5-text-t0.7-consensus-n10-9of10` | 431 | 153 | 59 | 6 | 0.7968 | 0.7875 | −0.0092 |
| `pv-diag-384::flash-high-text-n5-text-t0.3-consensus-10of10` | 409 | 142 | 56 | 6 | 0.7891 | 0.7773 | −0.0118 |
| `pv-diag-384::flash-high-image-n5-image-t0.7-consensus-7of10` | 405 | 156 | 63 | 7 | 0.7500 | 0.7405 | −0.0095 |
| `retest-phase3a-high::text-high-t0.7-n30-22of30` | 478 | 143 | 67 | 7 | 0.7729 | 0.7591 | −0.0138 |
| `retest-phase3a-high::text-high-t1.0-n30-23of30` | 442 | 127 | 61 | 6 | 0.7747 | 0.7625 | −0.0122 |
| `retest-phase3a-replication::text-high-t0.7-n30-21of30` | 520 | 158 | 72 | 7 | 0.7705 | 0.7573 | −0.0132 |
| `retest-phase3a::image-t0.7-n30-18of30` | 535 | 170 | 77 | 9 | 0.6909 | 0.6834 | −0.0074 |
| `gold-standard-v2::consensus-5of5` | 420 | 152 | 62 | 8 | 0.7649 | 0.7556 | −0.0094 |
| `consensus-384-t1-0::consensus-1of30` (@30 m) | 974 | — | 189 | 17 | 0.3109 | 0.3052 | −0.0057 |
| `consensus-384-t1-0::consensus-2of30` (@30 m) | 616 | — | 117 | 11 | 0.4091 | 0.4015 | −0.0076 |
| `e47-propose-brief::consensus-1of5` (@30 m) | 4491 | — | 952 | 40 | 0.1721 | 0.1693 | −0.0028 |
| `n1-outstanding-384::image-t03-consensus-1of3` (@30 m) | 812 | — | 171 | 18 | 0.6399 | 0.6303 | −0.0096 |

The reproduced value for the cell named in the brief — 0.6667 → 0.6565,
Δ −0.0102, 90 tile changes, 10 sheet changes on 549 detections — matches
`results/h13-overlap-2026-08-18/k-sensitivity/k_sensitivity.json` exactly.

Exposure: **123 of 333 conditions**, all `consensus`. Every single-pass and
every proposer-verifier artefact carries an upstream `source_tile`, so the
tie-break is never reached for them. Overlap with the deduplication exposure:
**6 conditions**.

Magnitude is small (−0.0028 to −0.0138), the direction is systematic (the
committed rule is the optimistic one in all 14 cells), and internal validity is
preserved because one rule is applied throughout any single analysis. The costs
are cross-chain comparability and reproducibility under row reordering.

---

## 3. Exposure of paper-cited numbers

Established by a full read of `docs/paper/{results,methods}-draft.md`,
`results-outline.md`, `discussion-outline.md`, `discussion-seeds.md`, the four
boards in `results/metric-leaderboards/`,
`results/hypothesis-outcome-table/`, and `results/analyses-manifest.json`,
cross-referenced against the measured exposure register.

### 3.1 Safe — verified unexposed

| Claim | Source | Why safe |
|---|---|---|
| GS headline F1@20 0.890 / MCC 0.790 | `results-draft.md:241-242` | `pv-diag-384::verified-adv-text-consensus-16of30` — multi-pass PV, duplicate fraction 0 |
| Deployment headline corrected-F1@50 0.8169 | `results-draft.md:404` | 55-map TH7-k4; `55maps-text-high-generalisation::*` duplicate fraction 0.00 % |
| H2 (adjusted p = 0.00035, ΔF1 +0.076) | `results-draft.md:209-212` | PV 16-of-30 vs consensus 26-of-30, both unexposed to deduplication |
| H8 (Simes p = 0.8344) | `results-draft.md:143-144` | `h8-v2` consensus cells, duplicate fraction 0 |
| H13 (arms A/B/C) | `hypothesis-outcome-table.md:36` | the only conditions scored on explicitly deduplicated inputs |
| Entire § R5 verifier-robustness matrix, § R6 Pareto, §§ R7–R9 | `results-draft.md:260-542` | multi-pass PV and 55-map deployment cells throughout |
| 55-map MCC boards (IM-k3 sole Tier 1) | `results-draft.md:398-437` | 1.05 % duplicate load; measured F1 movement +0.0004 |

Three of the four boards in `results/metric-leaderboards/`
(`55map-canonical-50m`, `55map-mcc-tiering`, `55map-mcc-tiering-standardised`)
carry no exposed rows at all.

### 3.2 Exposed but robust — measured, ordering survives

| Claim | Committed | After deduplication | Verdict |
|---|---|---|---|
| H11 single-pass tile-size monotonicity: 256 < 384 < 512 (`results-draft.md:231-232`) | 0.3417 / 0.5196 / 0.6055 | 0.3586 / 0.5465 / 0.6371 | **Holds.** All three legs exposed; the ordering and the argument survive |
| `era1-single-pass-baseline-matrix` T1→T2 boundary | `text-verbose` 0.5834 vs `image-canonical` 0.5814, margin 0.0020 | 0.6050 vs 0.6025, margin 0.0025 | **Holds**, margin slightly widens |
| Board leader vs runner-up | `canonical-last` 0.6314 vs `text-scale-4` 0.6094 | 0.6593 vs 0.6410 | **Holds** |
| `n1-baseline-matrix-384` T1→T2 boundary | 0.7921 vs 0.7555, margin 0.0366 | 0.8211 vs 0.7984, margin 0.0227 | **Ordering holds**; margin narrows 38 %, so tie membership (permutation-based) is not guaranteed |
| `n1-baseline-matrix-384` T5→T6 boundary | 0.5196 vs 0.5031, margin 0.0165 | 0.5465 vs 0.5299, margin 0.0166 | **Holds** |
| H3 "every consensus champion beats its matched single-pass baseline, +0.13 to +0.43" | comparator `baseline-flash-text-high-t-0-7` 0.3871 | 0.4040 → span becomes ≈ +0.10 to +0.41 | **Holds**; the rejection has an enormous margin |
| H7 primary contrast (text T0.3 vs T1.0) | ΔF1 +0.0958, p ≤ 0.001 | +0.0822 | **Holds**; direction and rejection preserved |

Two lower-order orderings *do* flip on the point estimate, both inside
already-non-significant comparisons:

- **H7 temperature ordering at 20 m**: committed T0.3 (0.6065) > T0.0 (0.6055);
  deduplicated T0.0 (0.6371) > T0.3 (0.6351). The registered contrast is
  T0.3 vs T1.0, which is unaffected, but any prose that names T0.3 as the
  single best temperature should be checked.
- **H5 verbosity (F1 leg)**: committed `image-terse` 0.6052 > `image-verbose`
  0.6027; deduplicated 0.6234 < 0.6271. H5's registered test is on precision
  and its adjusted p is 0.834, so no outcome changes, but the F1 direction
  reverses.

**H1 arithmetic, reproduced exactly.** `h1-cmt0106-pooled-modality` compares a
text-only group mean against an image-using group mean. Committed:
text-only (`brief-text` 0.5518, `verbose-text` 0.5016) = **0.5267**;
image-using (`image-only` 0.4697, `brief-text-image` 0.5220,
`verbose-text-image` 0.5170) = **0.5029**; Δ = **+0.0238** — matching
`results/family-fdr/h1_cmt0106_pooled_modality.json` to four decimals, which
confirms these are the right five cells. After deduplication: text-only
(0.5730, 0.5181) = **0.5456**; image-using (0.4787, 0.5362, 0.5318) =
**0.5156**; Δ = **+0.0300**, a 26 % increase. The committed 95 % CI is
[−0.0104, +0.0585] (half-width ≈ 0.034), so a Δ of +0.0300 would still be
expected to include zero, and H1 would still fail the family BH correction —
but this is arithmetic on point estimates, not a re-run bootstrap.

### 3.3 Materially at risk

**(a) `diversity-dividend-384` Tier-1 tie — the cross-architecture headline.**
Verified at `results/diversity-dividend-384/tiering-champions/tiering_20m.json`,
whose `tie_set` is exactly three cells:

| Rank | Cell | Committed F1@20 | Exposure | Measured/expected |
|--:|---|--:|---|---|
| 1 | `consensus-flash-high-text-26of30` | 0.8141 | tie-break only | 0.8047 under the alternative tile rule |
| 2 | `n1-pro-rerun-384::baseline-pro-text-high-t-0-0` | 0.8045 | **dedup, 11.6 %** | **0.8545** |
| 3 | `pv-diag-384::baseline-pro-text-medium-t-0-0` | 0.7921 | **dedup, 10.8 %** | **0.8211** |

The registered outcome text reads "Tier 1 (the tie_set) is a THREE-member
statistical tie: the best Flash HIGH-text consensus (F1 0.814) and the two
genuine-Gemini-3-Pro single-pass baselines". On deduplicated numbers the
consensus champion is no longer at the top of that tie but **0.040 below the
better Pro baseline** (0.8141 vs 0.8545), and 0.050 below if the tile-assignment
rule is also unified. The tie may well survive as a *statistical* tie — the
permutation test was not re-run — but the framing "cheap Flash consensus reaches
the tier of expensive Pro single-pass" is no longer supported by the point
estimates, and the narrative direction reverses.

**(b) § R5 zero-diversity anchor and 12 rows of `gs-era2-pv-family-30m`.**
`pv-diag-384::verified-adv-text-baseline` (board F1@30 **0.8320**) is the
single-proposer-pass anchor against which the paper measures how much of the PV
result comes from pass diversity. Deduplicated it is **0.8905**. For scale, the
board's own values: `opmax35` 0.9161, `verified-adv-text-pro-vf-4of5` 0.9058,
`headline31` 0.9044, `min11` 0.9005, `min6-true` 0.8902. The deduplicated anchor
would sit **level with `min6-true`** — 13th of 39 rather than 29th — and its
Pro-verifier sibling (`verified-adv-text-baseline-pro-vf`, 0.8419 → **0.9000**)
would sit level with `min11`, 8th rather than 25th. (Those ranks are against the
other 27 rows' committed values, which is the right comparison: every one of
them is a multi-pass cell and unexposed.)
All twelve `*-baseline*` rows on that board are exposed at 20–25 %; seven were
measured, moving +0.0442 to +0.0589 at 30 m.

The consequence is not that any committed number is wrong. It is that **the
measured size of the diversity dividend depends on a comparison between a
deduplicated multi-pass cell and an un-deduplicated single-pass cell**, and
correcting the asymmetry shrinks the dividend substantially.

**Caveat on (b), stated plainly.** Deduplicating an *accepted* PV set post hoc
is not identical to what the preregistered pipeline would have produced. Had
deduplication run before crop extraction, the verifier would have seen ~405
crops rather than 464, and the accepted set could differ in composition, not
just in count. The measurement is the best available at $0; it is an
approximation, and the erratum/paper text must say so.

---

## 4. Are the committed numbers wrong?

No, with one distinction worth drawing.

- **The tile-assignment tie-break is a sensitivity, not an error** (E79). Neither
  rule is prescribed; the registration specifies the matching algorithm in full
  at § 4.1.2 (`osf/preregistration.md:358-372`) but never states that matching
  is partitioned by map sheet, let alone how an overlap-band detection is booked
  to one. Every committed analysis applies one rule uniformly across its arms.
- **The missing deduplication is closer to a protocol gap than a sensitivity.**
  Preregistration § 8.5 Step 1 prescribes within-pass 20 m deduplication as a
  property of a *pass*. Conditions whose scored artefact never reached
  `merge_passes` did not receive it. The committed values are correctly computed
  from the artefacts they were given, and are internally consistent within any
  analysis whose arms are all exposed — but a comparison that puts an exposed
  cell against an unexposed one is not measuring only what it claims to measure.
  That is the situation in § 3.3, and it is why **this issue warrants its own
  erratum (E80), which this review recommends but has not drafted.**

---

## 5. What I could not determine

1. **No confidence intervals or permutation tests were re-run.** Every
   deduplicated and reassigned figure here is a *point estimate*. Tier
   membership, tie-set membership, and every p-value in the study are computed
   by 10,000-iteration BCa bootstrap or round-robin tile-swap permutation. I can
   say that the `diversity-dividend-384` Tier-1 point estimates reorder; I
   **cannot** say whether the tie survives. That requires re-running the
   permutation tiering, which is $0 but was outside this review's scope.
2. **Post-hoc deduplication of PV accepted sets is an approximation** of
   pre-verification deduplication (§ 3.3 caveat).
3. **The 6 exposed consensus conditions were not measured.** They carry no
   `source_tile`, so the deduplication probe cannot run on them without first
   choosing a tile-assignment rule — which would confound the two mechanisms.
   By analogy with H13 arm C the expected movement is ≤ +0.006 F1, but that is
   an inference, not a measurement.
4. **MCC movement was not measured anywhere.** Tile-level MCC is *not*
   automatically invariant to deduplication: collapsing two copies emitted from
   two overlapping tiles into one cluster centroid can empty one of those tiles,
   flipping its predicted class. Every MCC figure in the paper that comes from
   an exposed cell is therefore unquantified. The 55-map MCC boards are the
   headline MCC artefacts and are only 1.05 % exposed, so the risk is
   concentrated in the GS single-pass boards.
5. **108 of the 155 exposed conditions were not individually re-scored.** They
   were prioritised out because they are per-pass lineage rows that no paper
   draft cites; the survey register records their duplicate fractions so the
   selection can be audited.
6. **Nothing was re-run against the API.** Whether a properly deduplicated
   proposer pool would have changed the *detections* (as opposed to the score)
   cannot be answered without spend, and is not needed for any claim above.

---

## 6. Recommendation

**A targeted re-scoring campaign is warranted. A blanket 155-condition campaign
is not.**

The argument against blanket re-scoring: 109 of the exposed conditions are
per-pass lineage rows cited nowhere; re-scoring them would move numbers that no
reader ever sees, at the cost of invalidating every cross-reference into the
conditions manifest. The argument for targeted re-scoring: two paper-cited
claims currently rest on an asymmetric comparison, and one of them
(§ 3.3(a)) reverses direction when the asymmetry is removed.

Proposed scope, in priority order — all $0, all sapphire:

1. **Re-score with CIs the 22 cells of `diversity-dividend-384` and re-run its
   permutation tiering.** This is the only way to answer whether the Tier-1 tie
   survives. Highest value per unit of work.
2. **Re-score the 12 `*-baseline*` rows of `gs-era2-pv-family-30m` plus the
   § R5 anchor**, and rebuild that board. Then decide whether the paper reports
   the deduplicated anchor (recommended) or the committed one with a stated
   caveat.
3. **Re-score the 18 cells of `n1-baseline-matrix-384` and the 36 cells of
   `era1-single-pass-baseline-matrix`, and re-run both tierings.** Point
   estimates say the orderings hold; the tier *memberships* need the permutation
   test to confirm.
4. **Re-run the five-cell H1 pooled-modality bootstrap** on deduplicated inputs.
   Point-estimate arithmetic says H1 stays null; confirm it rather than assume
   it.
5. **Leave H2, H8, H13, §§ R5 (non-baseline cells), R6, R7, R8, R9 and both
   headline numbers alone.** Measured or verified unexposed.

Two decisions belong to the PI and are deliberately not taken here:

- **Whether to fix `evaluate_detections.py`.** Adding the § 8.5 Step 1
  deduplication to the scoring path would prevent recurrence but would silently
  move 155 committed conditions. The safer pattern is a `--deduplicate` flag,
  defaulting off, with the campaign above run explicitly under it. Unifying the
  tile-assignment rule (E79) is a separate one-line change with its own
  ~0.01 F1 cost, and the two should not be bundled: bundling makes the resulting
  deltas impossible to attribute.
- **Whether to draft erratum E80** for the deduplication gap. E79 (tile
  assignment) is drafted and appended. The deduplication gap is currently
  documented only inside E75's H13 disposition and in the H13 findings, which is
  not adequate given that it touches 155 conditions and a leaderboard.

---

## 7. Reproduction

All measurement ran on **sapphire** (`ssh sapphire`,
`~/Code/map-reader-llm`, `source .venv/bin/activate`). Total wall clock ≈ 6
minutes; zero API calls.

```bash
# Exposure register (~5 s)
python scripts/scoring_sensitivity_survey.py \
    --output results/scoring-sensitivity-2026-08-18/exposure-survey.json

# Probe batches (specs committed alongside the outputs)
for i in 1 2 3 4; do
  python scripts/scoring_sensitivity_probe.py \
      --spec results/scoring-sensitivity-2026-08-18/probe-spec-batch$i.json \
      --output results/scoring-sensitivity-2026-08-18/probe-batch$i.json
done

# Batch 5 uses the 55-map ground truth
python scripts/scoring_sensitivity_probe.py \
    --spec results/scoring-sensitivity-2026-08-18/probe-spec-batch5.json \
    --output results/scoring-sensitivity-2026-08-18/probe-batch5.json \
    --mode dedup \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson
```

The probe specs embed a `_committed_reference` block recording each cell's
committed F1 at 20 m and 30 m, so the "as-committed reproduces the committed
value" check can be re-verified without consulting the manifest.

---

## See also

- `docs/methodology/preregistration/protocol-errata.md` — **E79** (tile
  assignment, drafted by this review), E75 (H13 execution, whose disposition
  first recorded the deduplication gap), E72 (coverage confound — the same
  family of scoring-path property mistaken for a result)
- `results/h13-overlap-2026-08-18/findings.md` — the H13 overlap results, the
  first analysis scored under uniform deduplication, and the source of the
  973 → 916 arm-A anchor
- `results/h13-overlap-2026-08-18/k-sensitivity/k_sensitivity.json` — the
  original decomposition of the committed-versus-rebuilt F1 gap
- `results/scoring-sensitivity-2026-08-18/` — exposure register and five probe
  batches with their specs
- `scripts/scoring_sensitivity_survey.py`, `scripts/scoring_sensitivity_probe.py`
  — the two tools; both $0, both documented for re-run
- `results/conditions-manifest.json`, `results/analyses-manifest.json`,
  `results/metric-leaderboards/`, `results/hypothesis-outcome-table/` — the
  registers whose numbers were audited

---

## Changelog

### 2026-08-18 — Original publication

First review of the two scoring-path findings surfaced in Session 136 while
building the H13 overlap scoring chain. Verified both mechanisms at source;
established exposure by direct measurement of every committed detection artefact
(155 duplicate-exposed, 123 tie-break-exposed, 6 both, of 333 conditions);
re-scored 62 distinct cells across five probe batches (48 under deduplication,
14 under both tile-assignment rules) with the committed values reproduced
exactly as a harness check; audited the paper drafts, four
leaderboards, the hypothesis-outcome table, and the analyses manifest for
exposure. Principal finding, and a correction to the working assumption the
review started from: duplicate exposure is **not** confined to
`architecture: single-pass` — 26 proposer-verifier conditions, including twelve
rows of `gs-era2-pv-family-30m`, carry 15–25 % duplicate load because a
single-pass proposer pool never reaches `merge_passes`. Two paper-cited claims
assessed as materially at risk (`diversity-dividend-384` Tier-1 tie; the § R5
zero-diversity anchor); both study headlines verified safe. Recommended a
targeted ~40-cell re-scoring campaign with confidence intervals rather than a
blanket one, and recommended a second erratum (E80) for the deduplication gap.
Erratum E79 drafted and appended to `protocol-errata.md` in the same commit.
