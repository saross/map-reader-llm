# Gemini 3.8 Flash text-only screen: proposer seat and verifier seat, probe-first

> **Last revised**: 2026-09-04 (original publication — scoped and costed,
> NOT approved; no API call has been made). See
> [§ Changelog](#changelog).

**Question**: does Gemini 3.8 Flash (released 2 September 2026, model id
`gemini-3.8-flash`) move the Gold Standard (GS) text-only optimum above
the Gemini 3.7 stack? The 3.7 screen (`planning/gemini37-screen-2026-08-28.md`)
found the first family gain, and the 55-map 2×2 (Obs 444) located it in
the **verifier seat**, not the proposer seat. A 3.8 screen therefore
tests both seats from the start, cheapest first.

**What is known about 3.8 Flash** (fetched 2026-09-04 from
`ai.google.dev/gemini-api/docs/pricing`, `/docs/models`, `/docs/thinking`,
all "last updated 2026-09-03"): status "New Stable"; 3.7 Flash remains
"Stable". Thinking levels `low, medium, high`, default medium, no
`minimal`, cannot be disabled — identical to 3.7. Pricing identical to
3.7: standard $0.75 in / $3.75 out per million tokens, thinking billed as
output; Flex and Batch $0.375 / $1.875; valid through 2026-12-31, then
doubles. Launch coverage describes it as built on 3.7 and tuned to
"work harder" (more thinking tokens) for coding and agents — the cost
risk this card's probe measures, and the reason to expect no vision
change a priori.

## The cells

| Parameter | Value | Note |
|---|---|---|
| Config | `detect_brief-text` — byte-identical | the leading config, as for 3.7 |
| Model | `gemini-3.8-flash` via `--model` | stamped in metas; `--thinking-level low` (3.8's lowest, matching 3.7-low) |
| Geometry | B: 384 px / 50 % (stride 192), GS corpus | `inputs/grid-2026-08-18/grid_384_ov192_manifest.json`, 1,398 tiles |
| Passes | K = 5 (run_1..5), T = 0.7, real-time flex | K=10 added +0.0003 for 3.7 (saturated by N=5) |
| Verifier configs | `verify_adversarial-text`, T = 0.0, n = 1 | carried `gemini-3-flash` MINIMAL for the proposer-axis cell; `gemini-3.8-flash` low for the swap cells |
| Anchors ($0, committed) | 3.7 text K=5 carried-vf **0.9139** @20 m (0.10, k5); K=10 0.9142; all-3.7 stack **0.9265** (0.80/0.85 tie, k5), MCC 0.808; G3 plateau 0.8934 / 0.8961 | `results/gemini37-screen-2026-08-28/{analysis,k10/analysis,swap37/analysis}.json` |

**Comparability**: both models run at their lowest thinking level
(`low`), so the level confound that clouded 3→3.7 (MINIMAL vs low)
does not recur. Thinking *volume* may still differ; the probe measures
it and the finding is framed "each model at its cheapest level" either
way.

## Arms, in run order (each gated; stop rules in § Stop)

1. **Probe** — 5 tiles, `--model gemini-3.8-flash --thinking-level low`.
   Verify the meta stamps model and thinking; count thinking tokens per
   tile against 3.7-low's measured 275 t/tile. ≈ $0.05.
2. **Arm V — verifier seat at $0 proposer cost.** Re-verify the EXISTING
   3.7 K=5 union (791 candidates, `outputs/gemini37-screen-2026-08-28/`)
   with 3.8 as verifier. Direct comparison with the all-3.7 stack
   (0.9265) on the same candidates. ≈ 791 calls; 3.7's verifier profile
   was 2,023 tokens per candidate → token-basis ≈ $0.9, ≈ $1.3 if
   thinking doubles.
3. **Arm P — proposer seat.** K=5 passes at 3.8-low on B geometry
   (6,990 calls), union, carried G3 verifier over the union (≈ 800–900
   calls, 3.7 precedent $0.56 flex). Comparable with 3.7's 0.9139.
4. **Arm S — the all-3.8 stack.** 3.8 verifier over the 3.8 K=5 union.
   Comparable with 0.9265. ≈ $0.9–1.3.

Arm V runs before Arm P because it is the cheapest resolving test of the
seat where the 3.7 gain lived. If Arm V ties and the probe shows no
vision-relevant change, Arm P can still run for completeness of the
family record, but the PI may reasonably stop there.

## Registered expectations (commit at PI go)

| # | Bet | Prediction | Grounding |
|---|---|---|---|
| E1 | Arm V, verified best @20 m | tie with 0.9265 (within GS resolution) | 3.8 is built on 3.7 with more thinking; launch benchmarks are coding/agents, none vision |
| E2 | Arm P, carried-vf best @20 m | tie with 0.9139 | same |
| E3 | Thinking volume at `low` | above 3.7's 275 t/tile, 1.5–3× | the "works harder" launch framing; weakly grounded, probe measures |
| E4 | Verifier operating point | 3.8's prob_t optimum differs from 3.7's 0.80/0.85 and G3's 0.15/0.20 | verifier calibration is model-dependent (S144); report the sweep, carry no threshold |

Pre-named informative outcome: **Arm V or Arm S above 0.9265 plus GS
resolution**, which would be the second family gain in the verifier
seat and would reopen the verifier-model policy for the 55-map board.
Resolution caveat: GS screening MDE80 ≈ 0.065 (sensitivity appendix,
S143); the 3.7 swap's +0.0304 resolved only through paired permutation
(p = 0.0105). Expect a tie to be indistinguishable from a small gain.

## Cost (token basis, flex, 3.8 rates verified 2026-09-04)

Measured 3.7-low per pass on this cell (metas run_1..5): input
2,092,586 tokens, output 106,193, thinking 383,973, ≈ 1,393 tiles
processed (2–9 failures per pass, recovered).

| Arm | Calls | Expected | Ceiling (thinking ×3) |
|---|---:|---:|---:|
| Probe | 5 | $0.05 | $0.10 |
| V (3.8 vf over 3.7 union) | 791 | $0.9 | $1.5 |
| P proposer K=5 | 6,990 | $8.5 | $15.7 |
| P carried verifier | ≈ 850 | $0.6 | $0.6 |
| S (3.8 vf over 3.8 union) | ≈ 850 | $1.0 | $1.6 |
| **All-in** | **≈ 9,500** | **≈ $11** | **≈ $20** |

Per-pass sensitivity at 3.8 rates: thinking ×1 $1.70, ×1.5 $2.06,
×2 $2.42, ×3 $3.14. **Pause rule**: a probe implying > $25 all-in
pauses for a PI ruling. Billing reconciliation note: the 3.7 card
recorded passes 6–10 as "≈ $5.4 expected" against a $8.5 token-basis
figure for five passes; whether thinking was billed at output rate on
the posted SKUs is part of the unfinished D5 billing reconciliation —
treat the token basis as the ceiling, the 3.7 billed figure as the
floor.

Wall-clock at the 3.7 defaults (WORKERS 12, sapphire): passes took 72,
60, 53, 43, and 46 minutes (metas), ≈ 4.5 h for K=5; each pass logged
1,300–3,000 server-error retries, so more workers may not shorten it.
Schedule around the flex-storm window (~13:00–19:00 UTC).

## Stop rules

- Probe thinking > 3× 3.7-low (> 825 t/tile) → pause; consider
  `medium` only if `low` is degenerate, and record the level change as a
  design deviation.
- Any pass with > 1 % unrecovered tile failures → recovery pass before
  the union (K=5 precedent `run_*_recovery`).
- Arm V ties E1 AND probe shows no vision-relevant change → PI decides
  whether Arm P runs.

## Before launch (mechanics)

1. **Pricing table**: `scripts/lib_llm_metadata.py` `PRICING["google_gemini"]`
   has no `gemini-3.7-flash` or `gemini-3.8-flash` entry, so metas fall
   to the `default` 0.50/3.00 and exclude thinking (the 3.7 metas'
   `pricing_used` shows this). Add both at standard 0.75/3.75 with
   thinking counted as output before any 3.8 run, or every 3.8
   `cost_estimate` is an underestimate.
2. `/audit-config` delta: two CLI overrides on the byte-identical
   config (3.7 precedent, step 2).
3. Driver: clone `scripts/gemini37-escalation.sh` with
   `MODEL_ARGS="--model gemini-3.8-flash --thinking-level low"`,
   `OUTROOT=outputs/gemini38-screen-2026-09-04`, cell `g384_ov192_g38`,
   runs 1–5, `.done` markers, detached on sapphire.
4. Verifier launches via `run_pv.py verify` with `--model
   gemini-3.8-flash` (the swap37 precedent), each reconciled against
   pass metas first. Stamp `service_tier` and protect `run.meta.json`
   from the cleanup overwrite (queued runner fixes; the swap37 meta was
   lost to it).
5. Data commits per arm from sapphire; register rows after the
   verdicts, PI-signed, alongside the 3.7 rows still pending in
   `planning/gemini37-register-rows-proposal-2026-09-03.md`.

## Escalation (not approved; for the record)

If E1/E2 informative outcomes fire: passes 6–10 (+$8.5 expected) and a
55-map deployment plan on its own card (3.7 precedent ≈ $45–55 at these
rates, K=5 B geometry, carried points committed before scoring).

## Changelog

### 2026-09-04 — Original publication

Scoped and costed in Session 148 at the PI's request while the
empty-tile audit continued; pricing, model status, and thinking levels
fetched live from the Gemini API documentation (last updated
2026-09-03); token profile from the 3.7 K=5 metas. Awaiting PI go for
the probe; the API-call review gate applies to every arm separately.
