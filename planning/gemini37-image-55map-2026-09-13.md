# Gemini 3.7 image at deployment scale: the tile-MCC candidate, K = 3

> **Last revised**: 2026-09-13 (**PROPOSER COMPLETE** — all three passes at
> 24,561 / 24,561, audited US$245.6307 at a flat US$0.00333 per tile-pass, and
> both unions built (K = 1 6,985, K = 3 8,337; § 3.2). The four verifier arms
> are in flight and the campaign projects to ≈ US$274–288, inside the US$420
> hard stop. Earlier: **PASS 1 COMPLETE, both gates PASS** — audited
> US$81.9283 against the US$110 gate, cached share 0.808 against the 0.70
> gate (§ 3.1). Earlier: **RELAUNCHED** — B1–B4 all discharged, the GS
> calibration leg run and the carried operating points fixed in § 2, the
> mechanism smoke passed, and the 55-map proposer's pass 1 launched;
> P1–P5 remain
> UNTESTED because passes 2–3 and everything downstream are unbuilt — launch
> state and resume path in
> `outputs/gemini37-image-55map-2026-09-13/post_run_report.md`. Earlier:
> **API GATE APPROVED by the PI**,
> 2026-09-13 morning, in session, on the condition that caching is in
> effect — confirmed at source: the GS 3.7 image run's full passes show
> 79–80 % of input tokens cached via Gemini's implicit prefix caching,
> billed under the image caching SKU; launch then **BLOCKED at the
> pre-launch audit at US$0** by `reports/gemini37-image-55map-deltas-2026-09-13.md`
> — blocker B2, `merge_passes.py` silently drops `run_N_recovery`
> fragments, so the GS calibration leg cannot be built until the builder
> is fixed (PI ruling pending; reach being measured); B1 was the missing
> minute of this approval, now supplied; B3 (stop rule on the audited
> basis, `scripts/audit_proposer_cost.py`) and B4 (the cache gate is a
> pass-scale gate, not a smoke gate) are corrections to § 5. Earlier:
> COSTED). See
> [§ Changelog](#changelog).

**Question**: can a configuration chosen for tile-level discrimination
(Matthews correlation coefficient, MCC, on the presence-or-absence of a
mound per tile) significantly outperform every configuration deployed so
far on the 55-map corpus? Presence-or-absence is the unit of survey
triage, so MCC has research uses that F1 does not.

## 1. Why this configuration

Every figure below was re-read from the file cited on 2026-09-13.

| Evidence | Value | Anchor |
|---|---|---|
| Gold Standard (GS) Era-2 board: the top nine cells by tile-MCC are all image cells; the top three are single-pass image under a Pro or medium-thinking verifier | 0.877–0.889 | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md` table |
| The only GS cell leading on BOTH metrics: 3.7 image proposer K = 5, 3.7 verifier | F1 0.9233 (Tier 1), MCC 0.8264 | same table, rank 1 |
| The all-3.7 text stack (the paper's F1 headline) | F1 0.9190, MCC 0.7937 | same table, rank 2 |
| 55-map r2 board: sole MCC Tier 1 is the Gemini 3 image campaign, significantly above every text cell | IM-k3 0.7110; +0.032 to +0.071 over the text cells, all BH-significant | `results/metric-leaderboards/55map-mcc-tiering-r2.md` |
| 55-map MCC leader today: the fourth cell at K = 1 (Gemini 3 pool, 3.7 verifier) | 0.7471 (F1 0.8352) | `results/55map-final-board-r2-2026-09-06/final_board_50m.json`, `FOURTH-N1-oracle` |
| Deployed all-3.7 text stack | MCC 0.7147 (F1 0.8871) | same file, `ARM2-N5-oracle` |
| Tile-MCC never rises with K and falls significantly on three deployment ladders | § 4.1 | `results/k-ladder-2026-09-12/findings.md` |
| 55-map instrument resolves ΔMCC of about 0.01 | arm 1 K = 1 → 5 −0.0099, p = 0.017 | `reports/k-ladder-mcc-test-2026-09-12.md` |

Reading: MCC lives in the verifier and the modality, not in the pass
count. The image-over-text MCC gap is +0.03 on the GS at 3.7 and +0.03
to +0.07 at deployment for Gemini 3, and the instrument at 8,541 tiles
resolves a third of that. A 3.7 image run at K = 3 with the 3.7
verifier is therefore the candidate most likely to beat 0.7471
significantly, and its K = 1 rung is read from the same passes at the
cost of one more verifier pass.

## 2. The cells

| Parameter | Value | Note |
|---|---|---|
| Proposer | `gemini-3.7-flash`, `detect_brief-text-image` (the image config the GS 3.7 image run used), thinking `low`, T = 0.7 | byte-identical to `outputs/gemini37-image-gs-2026-09-01` |
| Geometry | B: 384 px / 50 % overlap (stride 192), the 55-map tiling `g384_ov192_55map`, 24,561 tiles per pass | the deployed geometry of stride B and the 3.7 text arms |
| Passes | K = 3 (run_1..3); K = 1 read from run_1 | first-N rule |
| Verifier arms | arm 1: carried `gemini-3-flash` (`verify_adversarial-text`, T = 0.0, MINIMAL, n = 1); arm 2: `gemini-3.7-flash` low, same config | mirrors the 3.7 text 2×2 (`gemini37-55map-grid-2026-08-31`) so the modality difference-in-differences exists at deployment |
| Operating points | CARRIED from a GS K = 3 calibration leg (below), not an argmax; oracle reported beside it | the fourth-cell precedent |

**Carried operating points — FIXED 2026-09-13, before any 55-map scoring.**
The GS calibration leg ran as § 5 step 1 specifies: the K = 3 first-N union
of the committed GS 3.7 image passes (622 candidates, votes
{1: 105, 2: 57, 3: 460}), both verifier arms at 622/622 with zero failures,
swept on the grid-common frame at the GS-primary 20 m buffer.

| Arm | Verifier | Carried (prob_t, k) | GS F1@20 | P | R |
|---|---|---|---:|---:|---:|
| arm 1 | `gemini-3-flash-preview`, `verify_adversarial-text`, T = 0.0, MINIMAL | **(0.10, k3)** | 0.9197 | 0.9032 | 0.9369 |
| arm 2 | `gemini-3.7-flash`, same config, thinking `low` | **(0.88, k3)** | 0.9245 | 0.9192 | 0.9299 |

Anchor gate passed (text-B rescored 0.89614 against the registered 0.8961).
Both arms select unanimity, so the K = 1 rung carries `prob_t` only and k
collapses to 1. Artefacts: `outputs/gemini37-image-gs-2026-09-01/verifier/g384_ov192_g37img/union_k3.geojson`,
`verify_k3_arm{1,2}/`, `results/gemini37-image-55map-2026-09-13/gs-calibration/`.
Audited cost of the leg US$1.12 (arm 1 US$0.4417 + arm 2 US$0.6804, flex,
3.7 rate card) against the card's US$1.2 — the union came in at 622 rather
than the estimated ≈ 450.
| Reference, buffer | r2, 50 m; tile-MCC on the 8,541-tile corpus | the board's instrument |
| Cost basis | token-basis flex, audited per `reports/token-load-audit-2026-06-12.md` § 2; billed reconciliation within 2 % on the August 3.7 leg | `reports/billing-reconciliation-2026-09-11.md` § 3 |

## 3. Cost

| Leg | Calls | Basis | USD |
|---|---:|---|---:|
| GS calibration leg: K = 3 first-N union of the committed GS 3.7 image passes, verified by both arms | ≈ 2 × 450 | 3.7 GS image K = 5 union was 674 candidates (`results/gemini37-image-gs-2026-09-01/`); K = 3 ≈ 450; $0.0013 per candidate | 1.2 |
| 55-map proposer, 3 passes × 24,561 tiles | 73,683 | US$0.00322 per tile-pass, 3.7 image with caching (`reports/gemini37-image-55map-costing-2026-09-10.md` line 33; K = 5 costed there at US$395) | 237 |
| 55-map K = 3 union, two verifier arms | ≈ 2 × 8,500 | image proposes tightly: 674 per 1,398 GS tiles at K = 5 → ≈ 8,500 at K = 3 over 24,561; $0.00140 (Gemini 3) / $0.00127 (3.7) per candidate (costing lines 58–59) | 22.7 |
| 55-map K = 1 union, two verifier arms | ≈ 2 × 5,500 | same rates | 14.7 |
| Scoring, sweeps, tiering | — | sapphire, $0 | 0 |
| **Total** | ≈ 102,000 calls | | **≈ US$276** |

Lower bound if caching runs as it did on the GS image run (invoice-derived
US$0.00245 per tile-pass, `reports/billing-reconciliation-2026-09-11.md`
§ 3.2): proposer ≈ US$180, total ≈ US$220. Upper bound at the runner
estimator's basis (US$0.00512): proposer ≈ US$377, total ≈ US$415.
**Stop rule**: abort the proposer if pass 1 exceeds US$110 on the
audited basis — computed with `scripts/audit_proposer_cost.py` (3.7 rate
card, cache reads at the cache rate, thinking at the output rate), NOT
the figure `run.meta.json` prints, which uses Gemini 3 rates and would
read US$126 for a US$79 pass (blocker B3). The verifier legs in § 3 are
on the list basis; `run_pv.py verify` defaults to flex, so the envelope
is ≈ US$261 (B3).

**Audited actuals, 2026-09-13** (running; the campaign is in flight):

| Leg | Card | Audited actual |
|---|---:|---:|
| GS calibration leg | 1.2 | **1.1221** (arm 1 0.4417 + arm 2 0.6804; union 622, not ≈ 450) |
| 5-tile mechanism smoke | — | **≈ 0.025** |
| 55-map proposer, pass 1 | ≈ 79 | **81.9283** — both gates PASS (§ 3.1 below) |
| 55-map proposer, pass 2 | ≈ 79 | **81.8712** — cache 0.810, within 0.07 % of pass 1 |
| 55-map proposer, pass 3 | ≈ 79 | **81.8313** — cache 0.811 |
| **Proposer, all three passes** | 237 | **245.6307** — 73,683 tile-passes, US$0.00333 each |
| Four verifier arms, scoring | 37.4 | in flight; projected **27.6–40.9** (§ 3.2) |
| **Running total** | | **≈ 246.78** of a ≈ US$274–288 envelope |

### 3.2 Union sizes and the four-arm projection

Both unions built by `stride55_prepare_and_union.py` (the ruled builder) after
the coverage gate passed at 24,561 / 24,561 on every pass:

| Rung | Candidates | Card estimate | Deltas' revised estimate |
|---|---:|---:|---:|
| K = 1 | **6,985** | ≈ 5,500 | — |
| K = 3 | **8,337** | ≈ 8,500 | ≈ 9,000–10,900 |

**The card's original K = 3 estimate was the better one.** The deltas report's
upward revision to ≈ 9,000–10,900 — built from the measured K = 5 → K = 3
candidate ratio of 0.923 and pass 1's 0.823 detection density — **overshot**:
the actual union is 8,337, within 1.9 % of the card's ≈ 8,500 and 7–23 % below
the revision. The K = 1 estimate, by contrast, was 27 % low.

The reason is visible in the per-pass dedup counts — **7,123 / 7,103 / 7,125**,
and a three-pass union of only 8,337. A single image pass already contributes
84 % of the K = 3 union's candidates, so the three passes agree with each other
far more than the text campaign's did (where the card's assumed K = 1 : K = 3
ratio of 0.647 came from). The measured ratio here is **0.838**. This is a
substantive result, not just a costing correction: extra image passes add
little new geometry and mostly raise vote counts on candidates pass 1 already
found, which is the mechanism P2 predicts will keep tile-MCC from rising with K.

Four-arm projection on the two available bases, over 2 × 15,322 = 30,644 calls:

| Basis | arm 1 | arm 2 | Four arms |
|---|---:|---:|---:|
| Card list rates (US$0.00140 / US$0.00127 per candidate) | 21.45 | 19.46 | **40.91** |
| GS calibration leg measured (622 candidates: 0.4417 / 0.6804) | 10.88 | 16.76 | **27.64** |

So the campaign lands at **≈ US$274–288**, against the US$420 hard stop —
US$132 of headroom even on the pessimistic basis.

### 3.1 Pass-1 gates — both PASS, read 2026-09-13 10:36 UTC

`scripts/audit_proposer_cost.py` on
`outputs/gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img`, re-read at
source, gives:

| Fragment | Tiles | Cached share | Audited USD |
|---|---:|---:|---:|
| `run_1` | 24,559 | **0.808** | 81.9212 |
| `run_1_recovery_rd1` | 2 | 0.813 | 0.0071 |
| **Total** | **24,561 / 24,561** | | **81.9283** |

Per tile-pass **US$0.00334**, against the card's basis of US$0.00322 — **+3.7 %**.
The pass completed at 10:32:36 UTC after one recovery round
(`driver.log:1119`, "PASS 1 COMPLETE").

- **Cost gate** (≤ US$110): **PASS** at US$81.93, with US$28 of headroom.
- **Cache gate** (≥ 0.70): **PASS** at 0.808, consistent with the GS image
  run's 0.79–0.80.

The meta's printed `cost_estimate` of **US$201.0662** is the Gemini-3-rate
artefact blocker B3 identified; it is never the gate basis.

**Revised projection.** At pass 1's audited rate the proposer's three passes
come to **≈ US$245.8** (card ≈ US$237), and the whole campaign to
**≈ US$285** — GS leg 1.12 + smoke 0.03 + proposer 245.8 + four verifier
arms and scoring ≈ 37.4. That is **above** the card's ≈ US$261–276 and well
inside the US$420 running hard stop, which remains the operative
abort rule. Passes 2–3 are therefore **GO**: the go/no-go the card's
"abort the proposer" rule becomes in practice (§ 3.1 of the deltas report)
is discharged in favour of proceeding. A pass whose audited cost exceeds
**1.5 × pass 1** (US$122.9) is a stop-and-report.

Two corrections the run has already established. First, the K = 5 → K = 3
candidate ratio is **0.923** (674 → 622), not the ≈ 0.67 the card's ≈ 450
implied, so on the measured density the 55-map K = 3 union is nearer ≈ 10,900
than ≈ 8,500 and the four verifier arms nearer US$32 than US$23 — the envelope
moves to ≈ US$270, still well inside the US$420 running stop. Second, **both
pass-1 gates are post-pass, not in-flight**: `4_detect_mounds_batch.py` writes
`*.meta.json` once at the end, so the audited cost and the cached share are
computable only when a pass finishes, and the "abort the proposer" rule above
operates as a go/no-go on passes 2–3. Detail in
`reports/gemini37-image-55map-deltas-2026-09-13.md` §§ 1 and 3.1.

## 4. Predictions, stated before the run

- **P1 (primary, MCC)**: the all-3.7 image K = 3 carried cell's tile-MCC
  exceeds the current 55-map leader (fourth cell K = 1, 0.7471) by
  ≥ +0.02, BH-significant on the paired tile-swap over 8,541 tiles.
  Informative failure: ≤ +0.01 (the GS image advantage does not transfer).
- **P2 (MCC, K)**: the K = 1 rung's MCC is ≥ the K = 3 rung's (the ladder
  result); F1 is lower.
- **P3 (F1, modality)**: corrected-F1 @ 50 m at K = 3 is within ± 0.02 of
  the 3.7 text arm 2 at N = 3 (0.8848): parity, per Obs 447 at deployment
  scale. Informative failure in either direction.
- **P4 (verifier seat)**: arm 2 (3.7 verifier) beats arm 1 on MCC by
  ≥ +0.01, as on the GS (0.8264 vs 0.8133).
- **P5 (transfer)**: the carried point's tax against the rung oracle is
  ≤ 0.01 F1 and ≤ 0.01 MCC.

## 5. Run order and gates

1. `/audit-config` on the proposer and both verifier configs; a 5-tile
   smoke (its cached share is by construction low — 16 % at 5 tiles,
   54 % at 15 — so the ≥ 70 % cache gate is judged on PASS 1, not the
   smoke; B4); the GS calibration leg (≈ US$1.2) → carried points fixed
   — **DONE 2026-09-13**, points in § 2; B2 discharged at the artefact
   (the rebuilt K = 5 first-N union reproduces the committed 674
   byte-identically, so the K = 3 union beside it is trustworthy).
2. Pass 1 on sapphire; audited cost check against the stop rule.
3. Passes 2–3; union; K = 1 and K = 3 unions with `pass_provenance`.
4. Both verifier arms on both unions; sweep; score at carried and oracle
   points; paired tile-swap on MCC and F1 against the fourth cell K = 1,
   arm 2 N = 3 and N = 5, and IM-k3; BH within the five-test family.
5. Register; findings document; analysis row for the PI; "ladder, then
   board": the rungs join the 55-map board and the ladder findings.

## 6. What this does not do

It does not extend the K ladder beyond 3 (the K = 5 → 10 step is the
worst buy on every ladder), does not swap the proposer config, and does
not touch the GS boards. If P1 fails informatively the result still
settles the modality question at deployment scale, which the paper
currently states on the GS only.

## Changelog

### 2026-09-13 (proposer complete) — three passes, both unions, arms in flight

**Trigger**: passes 2 and 3 ran to completion under the same driver and
invocation as pass 1, the coverage gate passed on all three, and both unions
were built by the ruled builder. Every figure audited at source.

| Claim | Before | After |
|---|---:|---:|
| Pass 2 | unlaunched | **COMPLETE**, US$81.8712, cache 0.810, 2 h 07 m |
| Pass 3 | unlaunched | **COMPLETE**, US$81.8313, cache 0.811, 2 h 16 m |
| Proposer total | projected ≈ 245.8 | **US$245.6307** over 73,683 tile-passes |
| Per tile-pass | US$0.00334 (pass 1) | **US$0.00333** across all three |
| K = 1 union | ≈ 5,500 estimated | **6,985** |
| K = 3 union | ≈ 8,500 card / ≈ 9,000–10,900 deltas | **8,337** |
| Campaign envelope | ≈ US$285 | **≈ US$274–288** |
| Running audited total | ≈ US$83.08 | **≈ US$246.78** |

Cost per pass was remarkably flat — US$81.9283, US$81.8712, US$81.8313, a
spread of 0.12 % — and the cached share held at 0.808 / 0.810 / 0.811 across
the flex congestion window. Each pass needed exactly one recovery round, of
2, 3 and 1 tiles.

**Two corrections to the deltas report's sizing, recorded in § 3.2.** Its
upward revision of the K = 3 union to ≈ 9,000–10,900 overshot; the card's
original ≈ 8,500 was the better estimate, and the actual 8,337 sits 1.9 %
under it. The K = 1 estimate of ≈ 5,500 was 27 % low. The cause is high
inter-pass agreement in the image proposer — per-pass dedup counts of
7,123 / 7,103 / 7,125 against a three-pass union of 8,337, so one pass supplies
84 % of the K = 3 candidates and the measured K = 1 : K = 3 ratio is 0.838, not
the text campaign's 0.647.

**What did NOT change**: the carried operating points, the cells, the scoring
instrument, the five-test family, the US$420 hard stop, and predictions P1–P5
(all still **UNTESTED**). No verifier arm has finished, no score exists, and no
board, tiering, signed row or analysis row was touched.

### 2026-09-13 (pass-1 gate) — both gates PASS, the projection revised upward

**Trigger**: pass 1 of the 55-map proposer completed at 10:32:36 UTC
(`outputs/gemini37-image-55map-2026-09-13/driver.log:1119`), which is the
moment both pass-1 gates become computable (§ 3.1 of the deltas report: the
runner writes `*.meta.json` once, at the end). Numbers re-read at source with
`scripts/audit_proposer_cost.py` at 10:36 UTC by the second steward.

| Claim | Before | After |
|---|---:|---:|
| Pass-1 tiles | in flight | **24,561 / 24,561** (24,559 main + 2 recovered, one round) |
| Pass-1 audited cost | pending | **US$81.9283** vs the US$110 gate — **PASS** |
| Pass-1 cached share | pending | **0.808** vs the 0.70 gate — **PASS** |
| Per tile-pass | US$0.00322 (card basis) | **US$0.00334**, +3.7 % |
| Proposer, three passes | ≈ US$237 | **≈ US$245.8** |
| Whole envelope | ≈ US$261–276 | **≈ US$285**, inside the US$420 hard stop |
| Running audited total | ≈ US$1.15 | **≈ US$83.08** |
| Passes 2–3 | unlaunched, go/no-go pending | **GO** |

The meta's printed `cost_estimate` reads **US$201.0662** for this pass — the
Gemini-3-rate artefact blocker B3 identified, 2.45 × the audited figure. It was
not used at the gate, and the discrepancy is the second confirmation of B3 at
pass scale.

**What did NOT change**: the carried operating points in § 2, the GS
calibration leg's US$1.1221, the 622-candidate GS union, the cells, the
predictions P1–P5 (all still **UNTESTED**), and the US$420 hard stop. No
union, verifier arm, score or analysis row exists yet. No board, no tiering
and no signed row was touched.

### 2026-09-13 (relaunch) — blockers cleared, calibration leg run, pass 1 in flight

B1–B4 all discharged and the run relaunched on branch
`gemini37-image-55map-2026-09-13`. B2's discharge carries a correction: the GS
calibration leg never ran through `merge_passes.resolve_pass_files`, because
`image_b_prepare_and_union.py` resolves passes through the
always-fragment-inclusive `stride_prepare_and_union.resolve_pass_paths` — so the
leg was blocked on a defect that did not reach it. The verification demanded
before trusting the K = 3 union passed decisively anyway: the rebuilt K = 5
first-N union reproduces the committed 674-candidate `union_k5.geojson`
**byte-identically**, all five passes gated at 1,398/1,398 after the recovery
fold. `merge_passes.py` still matters downstream, as the only source of
`pass_provenance`.

Carried operating points fixed in § 2 — arm 1 (0.10, k3) at GS F1@20 0.9197,
arm 2 (0.88, k3) at 0.9245, from a 622-candidate K = 3 union with the anchor
gate at 0.89614. Mechanism smoke passed on the GS payload fingerprint
`e169b723…`; pass 1 launched ≈ 07:28 UTC under
`scripts/gemini37-image-55map-driver.sh`. ≈ US$1.15 audited committed. P1–P5
remain UNTESTED; no board or tiering re-tiered, no signed row touched, no
analysis row authored. Launch state and resume path:
`outputs/gemini37-image-55map-2026-09-13/post_run_report.md`. Open with the PI:
who owns passes 2–3 onward, which builder produces the 55-map unions, and
whether the contradictory S152 "DECLINED" record is annotated.

### 2026-09-13 (later) — approved, then blocked at the audit for US$0

The PI approved the gate in session (caching confirmed at source). The launch agent's pre-launch audit returned BLOCKED on four points: B1 the approval was not minuted in this card (now is); B2 `merge_passes.py` drops recovery fragments, which would corrupt the GS calibration leg's union (650 vs 674 features on the K = 5 check) — builder fix and reach measurement pending the PI; B3 the stop rule must use the audited basis; B4 the cache gate is pass-scale. Cost basis US$0.00322 per tile-pass reproduced exactly (US$22.5004 over 6,990 GS tile-passes). No API call made.

### 2026-09-13 — Original publication (costed; awaiting the API-gate approval)

Written on the PI's request after the MCC reading of both boards. Every
number anchored to a committed file; the cost basis is the audited
token basis with invoice-derived and runner-estimator bounds.
