# Gemini 3.7 image at deployment scale: the tile-MCC candidate, K = 3

> **Last revised**: 2026-09-13 (later: **API GATE APPROVED by the PI**,
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
   — BLOCKED until `merge_passes.py` includes recovery fragments (B2).
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

### 2026-09-13 (later) — approved, then blocked at the audit for US$0

The PI approved the gate in session (caching confirmed at source). The launch agent's pre-launch audit returned BLOCKED on four points: B1 the approval was not minuted in this card (now is); B2 `merge_passes.py` drops recovery fragments, which would corrupt the GS calibration leg's union (650 vs 674 features on the K = 5 check) — builder fix and reach measurement pending the PI; B3 the stop rule must use the audited basis; B4 the cache gate is pass-scale. Cost basis US$0.00322 per tile-pass reproduced exactly (US$22.5004 over 6,990 GS tile-passes). No API call made.

### 2026-09-13 — Original publication (costed; awaiting the API-gate approval)

Written on the PI's request after the MCC reading of both boards. Every
number anchored to a committed file; the cost basis is the audited
token basis with invoice-derived and runner-estimator bounds.
