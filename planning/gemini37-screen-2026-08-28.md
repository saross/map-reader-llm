# Gemini 3.7 Flash family screen: one cell, K=5, probe-first

> **Last revised**: 2026-08-28 (original publication; PREPARED FOR
> PI GO — nothing runs until it is given). See
> [§ Changelog](#changelog).

**Question**: has the Flash family improved since Gemini 3? (3.5
regressed badly at higher cost — S113: won in no role, bare tie
0.620.) A screening run on the leading configuration, judged against
committed anchors; PI-approved design decisions 2026-08-28: K=5 (the
saturation evidence makes K=10 redundant for screening; passes are
additive if escalation is warranted), explicit `thinking=low` (3.7's
lowest level — see the comparability caveat).

## The cell

| Parameter | Value | Note |
|---|---|---|
| Config | `detect_brief-text` — byte-identical | the leading config |
| Model | `gemini-3.7-flash` via `--model` CLI override | stamped in metas |
| Thinking | `low` via `--thinking-level` CLI override | 3.7 has low/medium/high — no "minimal"; explicit beats alias |
| Geometry | B: 384 px / 50 % (stride 192), GS corpus | `inputs/grid-2026-08-18/grid_384_ov192_manifest.json`, 1,398 tiles |
| Passes | K = 5 (run_1..5), T = 0.7, real-time flex | additive escalation to K=10 possible later |
| Verifier | **carried gemini-3-flash** `verify_adversarial-text` T=0.0 MINIMAL n=1 over the K=5 union | isolates the proposer-model axis (the S113 role-permutation precedent) |
| Anchors | GS ladder g384_ov192 N=5 **0.8934**; K=10 cell 0.8961 (`plateau_analyses.json`) | committed, $0 |

**Comparability caveat (recorded up front)**: Gemini 3 MINIMAL
measured ZERO thinking tokens; if 3.7's `low` emits thinking, the
comparison is "each model at its cheapest thinking level" — the
practitioner-relevant axis, but model-vs-thinking stays confounded in
any 3.7 win until a follow-up. The probe measures 3.7-low's thinking
volume; the finding is reported with this framing either way.

## Registered expectations (committed at PI go)

| # | Bet | Prediction | Grounding |
|---|---|---|---|
| G1 | Verified best @20 m | 3.7 at-or-below the Gemini 3 plateau (≤ 0.8934 + GS resolution) | the 3.5 precedent; no family gain has ever shown |
| G2 | Operating lattice | prob ∈ {0.15, 0.20}, mid-to-high k | the lattice has held across models |
| G3 | Cost | proposer $5.5–16 flex (thinking-volume-dependent; 3.7 rates 1.5×/1.25× Gemini 3) | live pricing 2026-08-28 + measured token profile |
| G4 | Thinking at `low` | nonzero but < HIGH-class volumes (< 1,000 t/tile) | weakly grounded; probe measures |

Pre-named informative outcome: **3.7 ABOVE the plateau** (verified
best > 0.8961 + resolution) — would trigger the escalation path
(passes 6–10, verifier-role swap, deployment consideration) and
reopen the model-version policy.

## Cost

Probe: 5 tiles ≈ **$0.05** (pins thinking volume + the `low`
transmission). Full: proposer 6,990 calls ≈ **$5.5–16** flex
(3.7 flex rates $0.375/M in, $1.875/M out incl. thinking; pricing
page fetched 2026-08-28, valid through 2026-12-31) + carried verifier
~3,000 calls ≈ $2.1 at the measured Gemini 3 rate. **All-in ≈ $8
expected, ~$18 ceiling**; a probe rate implying > $25 pauses.

## Execution once approved

1. 5-tile probe (`--model gemini-3.7-flash --thinking-level low`);
   verify the meta stamps model + thinking, count thinking tokens.
2. `/audit-config` delta (two CLI overrides on the byte-identical
   config).
3. K=5 driver (Phase-B pattern) → union (stride/grid chain) →
   carried verifier (gated) → sweep + free N∈{1,3} rungs → the
   G1–G4 verdicts vs the committed anchors.

## Escalation — PI-APPROVED 2026-08-29

Screen outcome: the G1 informative outcome FIRED (verified best
0.9139 @20 m at (0.10, k5) — above every Gemini 3 cell; (0.15, k5)
0.9026 also above the anchor; union 791 with 59 % unanimous; recall
0.9299; all-in ~$7.4). PI verdict (verbatim in substance): strong
enough to escalate — "it looks like they've done something to vision
that wasn't changed 3→3.5 that has raised the ceiling... worth
working into the paper one way or another."

**Approved next steps (launch detached on sapphire at next session
start, background to the write-up):**

1. **Passes 6–10** (+~$6.5): the SAME invocation as the K=5 run
   (`--model gemini-3.7-flash --thinking-level low`, T=0.7, flex,
   cell g384_ov192_g37), runs 6–10 via the driver loop; then rebuild
   the union at K=10, verify the increment, full sweep + ladders.
2. **Verifier-role swap** (~$0.5–1): re-verify the K=5 union with
   `--model gemini-3.7-flash` on the verifier config (3.7 as
   verifier over its own and/or the text-B proposals — the S113
   role-permutation pattern).
3. **55-map deployment run** — PLAN (card + P-slate + probe first,
   ~$45–55 at measured 3.7 rates, B geometry K=5): the resolving
   test (deployment MDE80 0.013 vs the +0.018 effect). "Too good to
   pass up exploring."

## Changelog

### 2026-08-29 — Screen outcome + escalation approval

G1 informative outcome recorded; PI approved passes 6–10, the
verifier-role swap, and planning the 55-map run.

### 2026-08-28 — Original publication

Drafted in-session (S143) after the PI's K=5 and thinking=low
rulings; pricing fetched live; awaiting PI go for the probe + run.
