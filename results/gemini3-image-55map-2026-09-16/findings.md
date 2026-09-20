# Gemini 3 image at deployment scale, K = 1, 3 and 5: findings

> **Last revised**: 2026-09-21 (the six `*-mcc-oracle` rows dropped from
> § 2's table under PI ruling 2026-09-21 and moved to
> `results/tile-presence-2026-09-21/`; this also clears rows that had gone
> stale when those cells were re-pointed on 2026-09-20). Prior: 2026-09-20
> (original publication — row B of the image
> proposer × verifier 2×2, registered UNSIGNED for the Principal
> Investigator's (PI) review). See [§ Changelog](#changelog) for revision
> history.

This run is **row B** of the image proposer × verifier 2×2 at deployment
scale. Row A is `gemini37-image-55map-2026-09-13`
(`results/gemini37-image-55map-2026-09-13/findings.md`). The family of tests,
its instruments, and its caveats were declared in
`reports/image-2x2-tests-declaration-2026-09-19.md` before this row's primary
cell existed. There is no controlling card of row A's kind and no P1–P5
predictions: the declaration states contrasts, not directional predictions.

**What the 2×2 varies.** Row A and row B share the tiling (`g384_ov192`,
24,561 tiles), the proposer configuration `detect_brief-text-image`, the
exemplar library, the union builder, the two verifier arms, and the scoring
instrument. They differ in the proposer **model and its thinking level** —
`gemini-3.7-flash` at thinking `low` in row A against
`gemini-3-flash-preview` at thinking `minimal` here. Both rows' proposer metas
record the same `system_instruction_hash`
(`e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12`) and the
same `library_hash`
(`7c9bbcec1c4396db59aca57303fa1d679e0d93ffb0249b526dd5d89fe41dab1c`), so the
payload is identical and the row factor is the model package.

**Instrument.** `scripts/evaluate_detections.py` on the r2 board's own stage-2
recipe — 14 buffers, `inputs/vectors/references/best-available-gt-55maps-r2.geojson`,
`inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` (8,541 tiles),
tile-level bias-corrected and accelerated (BCa) bootstrap at 10,000 draws with
seed 42, `--mcc`, and `--require-clean-inputs`. Every figure below is read from
a committed `evaluation.json` under
`results/gemini3-image-55map-2026-09-16/cells/`, from
`results/gemini3-image-55map-2026-09-16/sweeps.json`, or from
`results/image-2x2-2026-09-19/tests_2x2_K{1,3,5}.json`. The paired tile-swap
permutation tests run at 10,000 draws with seed 42, with Benjamini–Hochberg
(BH) at q = 0.05 applied within each metric. A permutation *p*-value is bounded
below by 1/10,000, so a test with no draw at or beyond the observed statistic
is reported as *p* < 0.0001.

## 1. The primary rung, K = 3

K = 3 is the declared primary rung (declaration § 2). At that rung, on the
carried cells, the proposer swap costs the stack about a tenth of micro-F1 and
about four hundredths of tile-level Matthews correlation coefficient (MCC),
under **either** verifier.

| Test | Contrast | Metric | Row A | Row B | Δ (A − B) | BH *p* | Significant |
|---|---|---|---:|---:|---:|---:|---|
| T1 | proposer effect under arm 2 | tile-MCC | 0.764766 | 0.723426 | **+0.041339** | < 0.0001 | yes |
| T1 | proposer effect under arm 2 | F1 @ 50 m | 0.919904 | 0.812665 | **+0.107238** | < 0.0001 | yes |
| T2 | proposer effect under arm 1 | tile-MCC | 0.748998 | 0.724698 | **+0.024300** | < 0.0001 | yes |
| T2 | proposer effect under arm 1 | F1 @ 50 m | 0.902535 | 0.802387 | **+0.100147** | < 0.0001 | yes |
| T3 | verifier seat within row B (arm 2 − arm 1) | tile-MCC | — | — | −0.001272 | 0.7954 | no |
| T3 | verifier seat within row B (arm 2 − arm 1) | F1 @ 50 m | — | — | **+0.010278** | < 0.0001 | yes |
| T4 | interaction (A2 − A1) − (B2 − B1) | tile-MCC | +0.015767 | −0.001272 | **+0.017039** | 0.005167 | yes |
| T4 | interaction (A2 − A1) − (B2 − B1) | F1 @ 50 m | +0.017369 | +0.010278 | **+0.007091** | 0.01925 | yes |
| T5 | `G3IMG-ARM1-K3-carried` vs `IM-k3` | tile-MCC | — | — | +0.013698 | 0.07225 | no |
| T5 | `G3IMG-ARM1-K3-carried` vs `IM-k3` | F1 @ 50 m | — | — | +0.001604 | 0.7604 | no |

Source: `results/image-2x2-2026-09-19/tests_2x2_K3.json`. T3's and T5's
contrasts are not row-A-versus-row-B, so their Row A and Row B columns are left
empty; T3 is `G3IMG-ARM2-K3-carried` minus `G3IMG-ARM1-K3-carried`, and T5 is
`G3IMG-ARM1-K3-carried` (tile-MCC 0.724698, F1 0.802387) against `IM-k3`
(0.711, 0.800784).

**The reading.** The 2×2's answer at its primary rung is that the **proposer
family carries the advantage, and the verifier seat does not substitute for
it**. T1 and T2 are large and significant on both metrics in the same
direction; T3 — the verifier seat *within* row B — is worth +0.0103 F1 and
**nothing at all** on tile-MCC (−0.0013, *p* = 0.7954), where the same seat
swap in row A was worth +0.0158 MCC (row A `findings.md` § 4). T4 makes that
difference itself significant on both metrics: the 3.7 verifier's gain
**depends on the proposer family beneath it**.

## 2. Both arms × all three rungs

Eighteen cells. The K = 3 and K = 5 carried points were fixed on Gold Standard
(GS) calibration legs over the `image-b-gs-2026-08-28` pool before any 55-map
scoring; the K = 1 points are those legs' K = 3 thresholds with the vote
threshold collapsed to 1, so they are **carried analogues**, not carried points
in the strict sense (§ 8). Both oracles are reported beside the carried cells
so the transfer tax is visible.

| Cell | point | n | F1 @ 50 | F1 95 % CI | tile-MCC | MCC 95 % CI | tp | fp | fn | tn |
|---|---|---:|---:|---|---:|---|---:|---:|---:|---:|
| `G3IMG-ARM1-K1-carried` | (0.15, k1) | 8,529 | 0.6664 | [0.6593, 0.6734] | 0.7144 | [0.6992, 0.7286] | 2,646 | 301 | 883 | 4,711 |
| `G3IMG-ARM1-K1-f1-oracle` | (0.40, k1) | 7,466 | 0.6753 | [0.6676, 0.6825] | 0.7444 | [0.7311, 0.7572] | 2,512 | 83 | 1,017 | 4,929 |
| `G3IMG-ARM1-K3-carried` | (0.15, k3) | 5,538 | 0.8024 | [0.7943, 0.8101] | 0.7247 | [0.7106, 0.7392] | 2,557 | 187 | 972 | 4,825 |
| `G3IMG-ARM1-K3-f1-oracle` | (0.15, k3) | 5,538 | 0.8024 | [0.7943, 0.8101] | 0.7247 | [0.7106, 0.7392] | 2,557 | 187 | 972 | 4,825 |
| `G3IMG-ARM1-K5-carried` | (0.15, k5) | 4,858 | 0.8177 | [0.8089, 0.8259] | 0.7165 | [0.7024, 0.7304] | 2,485 | 158 | 1,044 | 4,854 |
| `G3IMG-ARM1-K5-f1-oracle` | (0.15, k5) | 4,858 | 0.8177 | [0.8089, 0.8259] | 0.7165 | [0.7024, 0.7304] | 2,485 | 158 | 1,044 | 4,854 |
| `G3IMG-ARM2-K1-carried` | (0.88, k1) | 9,172 | 0.6644 | [0.6572, 0.6712] | 0.7063 | [0.6907, 0.7212] | 2,724 | 405 | 805 | 4,607 |
| `G3IMG-ARM2-K1-f1-oracle` | (0.98, k1) | 7,931 | 0.6923 | [0.6851, 0.6992] | 0.7659 | [0.7531, 0.7781] | 2,573 | 56 | 956 | 4,956 |
| **`G3IMG-ARM2-K3-carried`** | (0.88, k3) | 5,941 | **0.8127** | [0.8050, 0.8201] | **0.7234** | [0.7087, 0.7379] | 2,639 | 261 | 890 | 4,751 |
| `G3IMG-ARM2-K3-f1-oracle` | (0.96, k3) | 5,266 | 0.8263 | [0.8185, 0.8336] | 0.7553 | [0.7431, 0.7678] | 2,505 | 41 | 1,024 | 4,971 |
| `G3IMG-ARM2-K5-carried` | (0.95, k5) | 5,155 | 0.8306 | [0.8224, 0.8382] | 0.7253 | [0.7111, 0.7394] | 2,567 | 193 | 962 | 4,819 |
| `G3IMG-ARM2-K5-f1-oracle` | (0.96, k5) | 4,664 | 0.8354 | [0.8271, 0.8432] | 0.7450 | [0.7324, 0.7577] | 2,447 | 33 | 1,082 | 4,979 |

**The tile-MCC optimum is not on this table.** PI ruling 2026-09-21 dropped
it from every board and campaign table under both definitions —
unconstrained, and pinned to the rung's carried vote count — because it is a
vote-threshold choice read as a metric's verdict. It is presented instead,
with its vote count as a column and its verifier pool priced, in
[`results/tile-presence-2026-09-21/`](../tile-presence-2026-09-21/leaderboard.md).
The cells stay on disk with their committed evaluations, re-labelled in
`cells_manifest.json`.

The bolded cell is the run's headline condition: the all-3.7-verifier cell at
the declared primary rung on its carried point, the cell T1 and T3 are stated
about. The `tp`, `fp`, `fn`, and `tn` columns are the **tile** confusion; every
row sums to 8,541.

**The carried ladder** (carried cells only, F1 @ 50 m / tile-MCC):

| Arm | K = 1 | K = 3 | K = 5 |
|---|---|---|---|
| row B arm 1 | 0.6664 / 0.7144 | 0.8024 / 0.7247 | 0.8177 / 0.7165 |
| row B arm 2 | 0.6644 / 0.7063 | 0.8127 / 0.7234 | 0.8306 / 0.7253 |
| row A arm 1 | 0.8477 / 0.7324 | 0.9025 / 0.7490 | 0.9130 / 0.7529 |
| row A arm 2 | 0.8719 / 0.7569 | 0.9199 / 0.7648 | 0.9270 / 0.7659 |

## 3. The gap is precision, and K closes only part of it

At K = 3 arm 2, row B's **recall is within six points of row A's and its
precision is fourteen points below**:

| Cell | n | precision @ 50 m | recall @ 50 m | F1 @ 50 m |
|---|---:|---:|---:|---:|
| `IMG-ARM2-K3-carried` (row A) | 5,357 | 0.8908 | 0.9510 | 0.9199 |
| `G3IMG-ARM2-K3-carried` (row B) | 5,941 | 0.7495 | 0.8874 | 0.8127 |

The mechanism is visible on the proposer side, before any score is taken. Each
Gemini 3 pass emits about **1.7 ×** the 3.7 pool's detections (per-pass totals
34,411 / 34,449 / 34,530 / 34,470 / 34,588 against row A's 20,017 / 20,065 /
20,090 / 20,052 / 20,092), and the passes agree with each other far less, so
the first-N unions balloon:

| Rung | row A union | row B union | ratio | row B unanimous share |
|---|---:|---:|---:|---:|
| K = 1 | 6,985 | 22,785 | **3.26 ×** | — |
| K = 3 | 8,337 | 36,389 | **4.36 ×** | 12,236 / 36,389 = 33.6 % |
| K = 5 | 9,173 | 45,786 | **4.99 ×** | 10,353 / 45,786 = 22.6 % |

Row A's K = 3 union is 69.9 % unanimous (5,825 of 8,337) and its K = 5 union
61.0 % (5,593 of 9,173); row B's are 33.6 % and 22.6 %. One row A pass supplies
83.8 % of its K = 3 candidate set (6,985 of 8,337); one row B pass supplies
62.6 % (22,785 of 36,389).

So for this pool the vote threshold is doing far more work. It buys a great
deal of precision — arm 2 carried precision rises 0.5140 → 0.7495 → 0.8196
across K = 1, 3, and 5 — but it also discards true positives faster than row
A's does: arm 2 carried recall falls 0.9394 → 0.8874 → 0.8420, and tile false
negatives rise 805 → 890 → 962, while row A's recall holds at 0.9570 → 0.9510
→ 0.9456. Micro-F1 therefore climbs steeply with K in row B (+0.1483 from
K = 1 to K = 3 on arm 2 carried) while tile-MCC barely moves (0.7063 → 0.7234
→ 0.7253): the surplus that unanimity removes sits mostly on tiles that were
already counted.

**Every MCC oracle above K = 1 collapses to a single vote.** At K = 3 and
K = 5, on both arms, the tile-MCC oracle sits at `k1` over a three- or
five-pass union — (0.35, k1), (0.40, k1), (0.98, k1), and (0.98, k1) —
admitting 10,078 to 12,508 detections and scoring micro-F1 @ 50 m of only
0.5205 to 0.5772. At K = 1 the two oracles are ordinary (0.6748 and 0.6923).
These four cells are registered because the board's convention registers both
oracles, but they are not deployable configurations: they buy tile
discrimination by flooding the map. Read them beside the carried cells, not
instead of them.

## 4. The interaction decays with K

T4 asks whether the 3.7 verifier seat's gain depends on the proposer family.
It does at K = 1 and K = 3, and the dependence shrinks monotonically as K
rises, on both metrics:

| Rung | T4 tile-MCC | raw *p* | T4 F1 @ 50 m | raw *p* |
|---|---:|---:|---:|---:|
| K = 1 (exploratory) | **+0.0327** | < 0.0001 | **+0.0262** | < 0.0001 |
| K = 3 (primary) | **+0.0170** | 0.0031 | **+0.0071** | 0.0154 |
| K = 5 (exploratory) | +0.0043 | 0.4221 | +0.0011 | 0.671 |

At the primary rung the BH-adjusted values over the declared five-member family
are **0.005167** (tile-MCC) and **0.01925** (F1 @ 50 m), both significant at
q = 0.05 — the values quoted in § 1.

Sources: `results/image-2x2-2026-09-19/tests_2x2_K1.json`,
`tests_2x2_K3.json`, and `tests_2x2_K5.json`. **This table deliberately quotes
raw, unadjusted *p*-values at K = 1 and K = 5.** Those two files are
exploratory replicates and were being regenerated under the four-member BH
family the PI ruled on 2026-09-20 (declaration § 3); a change of family size
moves the *adjusted* values only, so the observed differences and raw
*p*-values above are stable across the rebuild while the K = 1 and K = 5
adjusted values are not. Read those two rows as a **direction**, not as a
tested result.

The direction is coherent with § 3: the verifier seat matters most where the
candidate set is dirtiest. Unanimity over more passes does the filtering that
the better verifier would otherwise do, so by K = 5 the two seats are hard to
tell apart on a Gemini 3 pool.

## 5. Audited costs, per leg, against the provisional

Audited basis throughout — cache-aware, thinking-inclusive, and at the tier
actually used, per `reports/token-load-audit-2026-06-12.md` § 2. The metas'
own `cost_estimate` is never used: on every leg of this row it reads exactly
**2 ×** the audited figure, which is the half-of-list correction, and on the
proposer pool it reads US$633.1201 against US$233.6295 audited.

### 5.1 The proposer pool

Command:

```bash
.venv/bin/python scripts/audit_proposer_cost.py \
    outputs/gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img \
    --model gemini-3-flash-preview
```

| Pass | tiles | cached share | audited USD |
|---|---:|---:|---:|
| `run_1` + one recovery round | 24,561 | 0.812 | 46.7033 |
| `run_2` + one recovery round | 24,561 | 0.812 | 46.6927 |
| `run_3` + two recovery rounds | 24,561 | 0.812 | 46.7196 |
| `run_4` + one recovery round | 24,561 | 0.812 | 46.7307 |
| `run_5` + two recovery rounds | 24,561 | 0.812 | 46.7831 |
| **Pool, 122,805 tile-passes** | | | **233.6295** |

US$0.00190 per tile-pass, against row A's US$0.00301 over the same 122,805
tile-passes. Per-pass cost was flat to **0.19 %** across the five passes.

**The rate-card trap.** `audit_proposer_cost.py` does *not* read the model from
the meta: it prices at `--model`, which defaults to `gemini-3.7-flash`. Run
without the flag, this pool audits at US$345.9024 — a 48 % overstatement.
`--model gemini-3-flash-preview` is required for this pool, and the figure it
returns (US$233.6295) is the one to quote.

### 5.2 The six verifier legs

`scripts/audit_verifier_cost.py <leg> --tier flex`, STAGE TOTAL (audited):

| Leg | route | candidates | audited USD | USD/candidate |
|---|---|---:|---:|---:|
| K = 1 arm 1 (`gemini-3-flash-preview`, minimal) | realtime flex | 22,785 | **15.7559** | 0.000692 |
| K = 3 arm 1 | realtime flex | 36,389 | **25.1020** | 0.000690 |
| K = 5 arm 1 | realtime flex | 45,786 | **31.5422** | 0.000689 |
| **Arm 1, three rungs** | | 104,960 | **72.4001** | |
| K = 1 arm 2 (`gemini-3.7-flash`, low) | Batch API | 22,785 | **25.3978** | 0.001115 |
| K = 3 arm 2 | Batch API | 36,389 | **40.5813** | 0.001115 |
| K = 5 arm 2 | Batch API | 45,786 | **51.0925** | 0.001116 |
| **Arm 2, three rungs** | | 104,960 | **117.0716** | |
| **Six legs** | | **209,920** | **189.4717** | |

The row spent **US$189.4717 of the PI's US$200 provisional** for its legs
(`planning/paper-writeup-continuity.md`, S156 progress block). Every leg booked
its full union — 22,785, 36,389, and 45,786 — with zero failed items, and the
per-candidate rate is stable to the fourth significant figure within an arm,
which is the evidence that no leg is silently short.

### 5.3 The Gold Standard calibration legs

Run over the `image-b-gs-2026-08-28` pool on 2026-09-17/18, before any 55-map
scoring, and the source of every carried point in § 2:

| Leg | candidates | audited USD |
|---|---:|---:|
| GS K = 3 arm 1 | 2,227 | 1.5383 |
| GS K = 3 arm 2 | 2,227 | 2.4629 |
| GS K = 5 arm 1 | 2,788 | 1.9219 |
| GS K = 5 arm 2 | 2,788 | 3.0878 |
| **Four GS legs** | | **9.0109** |

### 5.4 The row, in total

Proposer US$233.6295 plus six verifier legs US$189.4717 plus four GS
calibration legs US$9.0109 equals **US$432.1121**, against row A's US$415.3174
as extended to K = 5 (row A `findings.md` § 5).

## 6. What the Gold Standard calibration predicted

The carried points came from a GS calibration leg over the
`image-b-gs-2026-08-28` pool (`results/gemini3-image-55map-2026-09-16/gs-calibration/`),
whose anchor gate re-scores the registered text-B cell at 0.8961352657 against
the registered 0.8961. At matched rung and arm, against row A's own GS legs
(`results/gemini37-image-55map-2026-09-13/gs-calibration/` for K = 3 and the
registered GS K = 5 cells `g37-image-k5-verified-carried-p0.10-k5` and
`g37-image-k5-verified-swap37-p0.90-k5` for K = 5):

| Leg | row A GS F1 @ 20 m | row B GS F1 @ 20 m | gap | row B carried point |
|---|---:|---:|---:|---|
| K = 3 arm 1 | 0.9197 | 0.8200 | **0.0997** | (0.15, k3) |
| K = 3 arm 2 | 0.9245 | 0.8408 | **0.0837** | (0.88, k3) |
| K = 5 arm 1 | 0.9254 | 0.8431 | **0.0823** | (0.15, k5) |
| K = 5 arm 2 | 0.9308 | 0.8551 | **0.0757** | (0.95, k5) |

The deployment-scale gaps at K = 3 (T1 +0.1072 F1, T2 +0.1001 F1) are close to
the matched Gold Standard gaps at the same rung (0.0837 and 0.0997), so the
Gold Standard predicted the size of this row's shortfall before any 55-map
candidate was verified. It did **not** predict the K = 1 collapse: at K = 1 the
deployment gap is +0.2075 F1 (arm 2) and +0.1813 (arm 1), roughly twice the
Gold Standard gap, because a single Gemini 3 pass over 55 maps over-generates
in a way a 487-tile Gold Standard leg cannot show.

## 7. What did NOT change

- **No board and no tiering was re-tiered**, and **no signed row was touched.**
  `results/55map-final-board-r2-2026-09-06/` and
  `results/metric-leaderboards/55map-mcc-tiering-r2.md` are untouched; this
  run's cells live only in its own results tree.
- **The analysis row is UNSIGNED.** `manually_verified_at` is null,
  `signature.status` is `unsigned`, and `outcome` is deliberately null pending
  the PI's reading.
- **No prompt or input configuration changed.** The proposer payload is
  byte-identical to row A's on `system_instruction_hash` and `library_hash`;
  the verifier configuration is `verify_adversarial-text` at T = 0.0 on both
  arms.
- **Row A's eighteen cells are untouched.** This run adds eighteen cells
  beside them and re-scores none of them.
- **The carried points are as fixed on 2026-09-17/18**, before any 55-map
  scoring.

## 8. Limitations

- **The K = 1 points are carried *analogues*, not carried points.** No K = 1
  Gold Standard leg was run; the K = 1 cells take the K = 3 leg's threshold
  with the vote threshold collapsed to 1. The registration records
  `basis: "carried-analogue"` on those six rows to keep the distinction
  visible. Row A did the same thing without the distinct label.
- **The K = 1 and K = 5 test JSONs were being regenerated when this document
  was written**, under the four-member BH family the PI ruled on 2026-09-20
  (declaration § 3). Only the K = 3 reading in § 1 is a primary result; § 4's
  K = 1 and K = 5 rows are qualitative until those files land.
- **The two rows differ in thinking level as well as model** (`low` against
  `minimal`), so "proposer family" is a package, exactly as "verifier seat" is
  in row A's P4.
- **The operating points differ by row by design** (declaration § 5.3). T1 and
  T2 compare the rows as deployed, not at a common threshold. The oracles in
  § 2 show what a common-threshold reading would change: row B's arm 2 K = 3
  F1 oracle is 0.8263, still 0.094 below row A's carried cell.
- **The routes differ between the rows' arm 2.** Row A's arm 2 ran on realtime
  flex; row B's ran on the Google async Batch Application Programming
  Interface (API) (PI ruling 2026-09-18). The 2026-09-19 batch-versus-flex
  probe found no route effect beyond same-route re-invocation drift
  (declaration § 5.2), so this is a recorded caveat, not a measured effect.
- **The E89 drift floor applies.** Independent re-invocations of these
  verifiers at T = 0 flip 3.5–5.3 % of decisions at the operating point
  (declaration § 5.1). T3's MCC null (−0.0013) and T4's K = 5 values (+0.0043
  MCC, +0.0011 F1) are all inside that floor and are uninformative about small
  effects.
- **T5's comparator is not protocol-matched.** `IM-k3`
  (`55maps-image-generalisation::verified-k3-r2-gt`) is registered with
  `n_passes` 5 and `vote_threshold` 3 — five passes at 3-of-5 — while
  `G3IMG-ARM1-K3-carried` is three passes at 3-of-3. The protocol-matched
  point on this row's own K = 5 arm 1 pool, the best 3-of-5 point in
  `results/gemini3-image-55map-2026-09-16/sweep_G3IMG-ARM1-K5.csv`, scores
  micro-F1 @ 50 m of **0.7357** at prob_t 0.20, against `IM-k3`'s 0.8008. So
  T5's null at K = 3 rests on a comparison of unlike vote protocols, and the
  matched comparison is less favourable to this row than the registered one.
  `IM-k3`'s tile join is also not this chain's (83.65 % idempotent; row A
  `findings.md` § 7).
- **The MCC oracles above K = 1 are not deployable** (§ 3). They are registered
  for completeness under the board's both-oracles convention.
- **No permutation test compares rungs within this row.** The K = 1 → K = 3 →
  K = 5 ladder in § 2 is descriptive.

## Changelog

### 2026-09-21 — The tile-MCC optimum moved off this table

**Refresh trigger**: PI ruling 2026-09-21, superseding ruling 6c of
2026-09-20. The "MCC oracle" is dropped from the main boards and campaign
tables under **both** definitions — the unconstrained tile-MCC argmax, and
the argmax pinned to each configuration's carried vote count. Tile-MCC stays
reported beside micro-F1 at the carried and F1-oracle points, where both
metrics describe the same configuration; the F1 oracle stays free over both
dimensions; and the tile-MCC optimum moves to a separate presentation,
`results/tile-presence-2026-09-21/`, where its vote count is a column and
the verifier pool it would need is priced.

**What changed on this document**: the six
`G3IMG-ARM{1,2}-K{1,3,5}-mcc-oracle` rows are removed from § 2's table and
replaced by one pointer line.

**This also corrects a staleness.** Those rows were published on 2026-09-20
against the UNCONSTRAINED optima — `G3IMG-ARM1-K3-mcc-oracle` at (0.35,
**k1**) with 10,078 detections, and so on. Later the same day ruling 6c
re-pointed every `*-mcc-oracle` cell to its carried-k optimum and moved the
unconstrained cells to `cells/<label>-mcc-oracle-unconstrained/`, and this
document was not refreshed. Its six rows therefore carried the right
numbers under the wrong labels for a day. Removing them resolves that;
the numbers themselves are in
`results/tile-presence-2026-09-21/leaderboard.md`, which reads the sweep
record directly.

| | before | after |
|---|---:|---:|
| § 2 table rows | 18 | **12** |
| cells on disk | 24 | **24** (none deleted) |

**Numbers that moved**: none on this document. The six rows removed were
label-stale, not value-wrong.

### 2026-09-20 — Original publication

Written in response to
`reports/comparability-inventory-37-runs-2026-09-20.md` § 6 item 4, which
asked for this row to be registered and documented before the 2×2 is signed.

First publication, on the row's completion: five proposer passes at
24,561 / 24,561 each, three first-N unions (22,785 / 36,389 / 45,786), six
verifier legs booking their full unions with zero failures, eighteen scored
cells at K = 1, 3, and 5, and the declared family run at all three rungs. The
run was registered on the same day — one registry entry, one facts entry,
eighteen conditions, six verifier passes, and one analysis row — with
`verify_run_conditions.py --run gemini3-image-55map-2026-09-16` reporting
`1 run(s): 1 pass, 0 partial, 0 fail` and `generate_post_run_report.py --all`
reporting ALL VALID with no registry-versus-facts drift block. **Everything is
UNSIGNED and presented for the PI's review**: `manually_verified_at` is null,
`signature.status` is `unsigned`, and the analysis row's `outcome` is null.

State at publication: the K = 3 rung is the only primary reading; the K = 1 and
K = 5 test JSONs are being regenerated under the four-member BH family ruled on
2026-09-20 and are cited here qualitatively. Row spend US$189.4717 of the
US$200 provisional on the six verifier legs; US$432.1121 including the proposer
pool and the four Gold Standard calibration legs.
