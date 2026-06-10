# Make-up plan: the half-coverage "min6" cell (text-n10 lineage)

> **Status**: AWAITING APPROVAL (Shawn, morning 2026-06-11). Prepared
> overnight in Session 111.

## What actually happened (diagnosis, not failure-to-rerun)

The artefact that "failed on half the tiles" is **not a run** — it is a
**stale union**. All ten `text-n10` proposer passes are complete on disk
(487/487 tiles each, 0 failures, verified from every pass meta). But the
committed `outputs/h11/pv-diag-384/consensus/text-1of5.geojson` (974
candidates on only **230/471** candidate-bearing tiles) was built
mid-study, before the resume/retry rounds completed the passes — and its
n=1 verifier probabilities cover only those 974 candidates. Scoring it
gives a meaningless 0.60 F1 (`results/verifier-robustness/min_thinking_pv.log`);
its verifier signal is healthy (vote↔probability r = +0.40), the pool
simply never saw half the map.

So the proposer side needs **no API spend at all**. Only the verifier leg
over a correct first-5 union is missing.

## Options

| | what | cost | yields |
|---|---|---:|---|
| **A (already in train, $0)** | Derive min6 post-hoc from the verified 10-pool (`text-1of10` + committed carry-forward probs) via `contributing_passes` — the method-matched cell the Flash 3.5 analysis uses anyway | $0 | the n=5 reference, method-matched to the 3.5 tranche |
| **B (recommended add-on)** | Regenerate the true first-5 union with current `merge_passes` (~1,600 cands expected), extract crops, one carry-forward n=1 verifier pass | **≈ $1.15 flex** (~1,600 calls) | a clean, directly-verified min6 cell in the text-n10 lineage; replaces the stale artefact for the record |

Recommendation: **do both**. A is free and required for the method-matched
Flash 3.5 comparison; B closes the data-integrity hole properly for ~a
dollar and gives the true-merge cross-check of the derivation in this
lineage too. Either way, the stale `text-1of5` union + its probabilities
should be **archived** (never deleted) to
`archive/superseded-unions/text-1of5-partial-coverage/` with a README
noting the diagnosis.

## If approved (B)

```bash
# on zbook, after the Flash 3.5 tranche completes
.venv/bin/python scripts/merge_passes.py \
    --input-dir outputs/h11/pv-diag-384/text-n10/text-t0.7 \
    --passes 1,2,3,4,5 --threshold 1 \
    --output outputs/h11/pv-diag-384/consensus/text-min-t07-true-1of5.geojson
.venv/bin/python scripts/run_pv.py extract \
    --proposer outputs/h11/pv-diag-384/consensus/text-min-t07-true-1of5.geojson \
    --output-dir outputs/h11/pv-diag-384/crops/text-min-t07-true-1of5 --padding 75
.venv/bin/python scripts/run_pv.py verify \
    --crops-dir outputs/h11/pv-diag-384/crops/text-min-t07-true-1of5 \
    --verifier-config prompts/configs/verify_adversarial-text.json \
    --mode realtime --service-tier flex --iterations 1 --workers 14 \
    --output-dir outputs/h11/pv-diag-384/verified/text-min-t07-true-1of5
# then the standard k x prob_t sweep + 14-buf evaluation, $0
```

Gate before verify: union must cover ~471 tiles (reject if < 460).
API-gate summary: gemini-3-flash (carry-forward verifier), realtime flex,
~1,600 calls, ≈ $1.15.
