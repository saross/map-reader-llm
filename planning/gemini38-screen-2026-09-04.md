# Gemini 3.8 Flash text-only screen: proposer seat and verifier seat, probe-first

> **Last revised**: 2026-09-04 (CLOSED — probe and Arm V executed under
> PI approval; Arm V ties the all-3.7 stack, E1 as predicted; PI ruled
> STOP, Arms P and S not run). See [§ Changelog](#changelog).

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

## Results — probe and Arm V (2026-09-04, PI-approved 2026-09-04)

**Pricing source confirmed** by the PI's pointer
(`blog.google/.../3-8-flash-and-3-8-flash-cyber/`): $0.75 / $3.75 per
million tokens through 2026-12-31, then $1.50 / $7.50 — matches the API
pricing page used above; the blog carries no Flex or thinking-billing
detail, which the API page supplies.

**Pre-launch fixes landed first**: `scripts/lib_llm_metadata.py` gained
`gemini-3.7-flash` and `gemini-3.8-flash` pricing keys and now bills
Gemini thinking tokens at the output rate (commit `73658c579`, two
tier-1 tests); dry-run on sapphire passed (5/5 tiles, 384 px measured,
text-only, both overrides applied); `/audit-config` delta: READY.

**Probe** (`outputs/gemini38-screen-2026-09-04/probe-gate-1/`): 5/5
success, model and thinking stamped `gemini-3.8-flash` / `low`,
instruction hash `e169b723…` and library hash `8580ecb2…` identical to
the 3.7 run_1 meta; per tile input 1,502 / output 81 / thinking 307
tokens (3.7-low: 1,497 / 76 / 275); one tile emitted zero thinking.
Implied proposer K=5 ≈ $9.0 token-basis; gate passed; the PI's
condition for Arm V (no surprises, < $25) met.

**Arm V** (`outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap38/`,
scored to `results/gemini38-screen-2026-09-04/armV/`): 790/791 in the
main run (39 min at 30 workers; 803 server-error retries, 0 rate-limit),
one 503 recovered by `run_pv.py cleanup` at standard tier. Tokens
1,415,680 in / 107,091 out / 60,434 thinking — **76 thinking tokens per
candidate against the 3.7 verifier's 106**; ≈ $0.85 flex token-basis.
Scorer: anchor gate 0.8961 OK, union 791 joined.

| Cell (same 791-candidate union) | F1@20 | P | R | MCC | point |
|---|---:|---:|---:|---:|---|
| **3.8 verifier (Arm V)** | **0.9258** | 0.9335 | 0.9182 | 0.8218 | (0.88, k5) |
| all-3.7 stack (swap37) | 0.9265 | 0.9254 | 0.9276 | 0.8078 | (0.80/0.85 tie, k5) |
| carried Gemini 3 verifier (screen) | 0.9139 | — | — | — | (0.10, k5) |

Ladder: N=1 0.8874 (0.92, k1), N=3 0.9173 (0.88, k3), N=5 0.9258.
Pair tests (`pair_test.json`; round-robin tile-swap, 10,000, seed 42,
487 tiles): 3.8 vs all-3.7 **dF1 −0.0007, p = 0.78**; 3.8 vs carried-G3
+0.0119, p = 0.097.

**Verdicts**: E1 tie — AS PREDICTED. E3 FALSIFIED in the opposite
direction in the verifier seat (3.8 thinks less at `low`) and only 1.1×
in the proposer probe. E4 partly: the argmax sits at 0.88, not at 3.7's
0.80/0.85 or G3's 0.15/0.20, but the surface is flat — every k=5 point
from prob_t 0.20 to 0.92 lies within 0.0022 of the best (0.9251 at
0.20; 0.9236 at 3.7's 0.85). **Correction (same day, from the Obs 448
source check)**: the 3.7 verifier is equally flat on this union (k=5,
prob_t 0.20–0.92: 0.9243–0.9265, spread 0.0022, `swap37/sweep_20m.csv`);
the sharply peaked surface belongs to the carried Gemini 3 verifier
(0.8446–0.8942 over the same band, spread 0.0497,
`results/gemini37-screen-2026-08-28/sweep_20m.csv`). Threshold
insensitivity is therefore a 3.7/3.8-generation property, not a 3.8
novelty; the earlier "where the 3.7 verifier's optimum was sharp" was
wrong. E2 untested (Arm P not run).

**Gotchas recorded**: (1) `run_pv.py verify` stamps `cost_basis: list`
with `discount 1.0` even under `--service-tier flex` — the verify path
does not apply the flex discount that the proposer path does; the
$1.69 in the meta is list, ≈ $0.85 billed. (2) The verify meta's
`parse_failures` (803) equals `retries_total`: the verify path counts
each retried server error as a parse failure. (3) `cleanup` overwrote
`run.meta.json` again; the runner now writes `.pre-cleanup-*.backup`
copies, and the main-run meta is also kept as
`run.meta.main-2026-09-04.json`. (4) 503 "high demand" storms hit at
~04:00 UTC, outside the assumed 13:00–19:00 window.

**PI ruling 2026-09-04: STOP after Arm V.** Arm P (+ ≈ $9.6 with its
carried verifier) and Arm S (≈ $1) are not run: on this evidence both
are expected ties, and the paper's 3.7 arc already carries the
verifier-seat finding. The screen closes as a tie in the verifier seat
with two recorded findings (thinking volume; the flat sweep surface).
Total spend: probe + Arm V ≈ $0.85 flex token-basis.

## Escalation (not approved; for the record)

If E1/E2 informative outcomes fire: passes 6–10 (+$8.5 expected) and a
55-map deployment plan on its own card (3.7 precedent ≈ $45–55 at these
rates, K=5 B geometry, carried points committed before scoring).

## Changelog

### 2026-09-04 (later still) — Finding B corrected

The obs-writer's source check for Obs 448 (`463c931b3`) caught two
errors in Finding B as first written: the 3.8 sweep spread over prob_t
0.20–0.92 is 0.0022, not 0.001, and the 3.7 verifier is equally flat
(0.0022) — the sharp surface is the carried Gemini 3 verifier's
(0.0497). Verdict text corrected in place; the finding now reads as a
generation property refining Obs 441, not a 3.8 novelty. Obs 448 also
records that tile-MCC ranks the arms the other way (3.8 +0.0140 on
MCC while −0.0007 on F1) and that Arm V's ladder MCC falls as N rises
(0.8331 → 0.8293 → 0.8218).

### 2026-09-04 (later) — Probe and Arm V executed

PI approved the probe and, conditional on no surprises under $25,
Arm V (same day). Pricing source confirmed from the Google blog. Cost
estimator fixed first (`73658c579`). Probe passed the gate; Arm V ran
(790/791 + one cleanup), scored and pair-tested: a tie with the all-3.7
stack (dF1 −0.0007, p = 0.78). Data commit `f04eb6f58`; pair-test
script `21a34339f`. PI ruled STOP the same day: Arms P and S not run;
the screen is closed as a verifier-seat tie.

### 2026-09-04 — Original publication

Scoped and costed in Session 148 at the PI's request while the
empty-tile audit continued; pricing, model status, and thinking levels
fetched live from the Gemini API documentation (last updated
2026-09-03); token profile from the 3.7 K=5 metas. Awaiting PI go for
the probe; the API-call review gate applies to every arm separately.
