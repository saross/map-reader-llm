# H6 registered $0 analyses — A-06, A-07, A-09 on the existing genuine-Pro data

> **Last revised**: 2026-08-17 (original publication). See
> [§ Changelog](#changelog) for revision history.

**What this is.** The S134 walk (Group E) ruled that H6's three
registered analysis components run first, on the Pro data that
exists, before the ~US$48 Phase-4 re-run decision. This document
reports all three, plus the explicit A-08 non-computability
statement. Machine-readable sources:
`a06_decision_rule.json`, `a07_voting_thresholds.json`,
`a09_cost_gate.json` (this directory); script
`scripts/h6_registered_analyses.py`.

**Data provenance (the S135 audit's headline catch).** The block
plan originally anchored these analyses on
`n1-outstanding-384::pro-*` — which is the **E57 mis-dispatch**:
those pools were dispatched and billed as `gemini-3-flash-preview`.
The genuine Pro data is `outputs/h11/n1-pro-rerun-384`
(`gemini-3.1-pro-preview`, four corners × three runs), and the
mis-dispatch pools serve instead as a **matched-N,
matched-configuration Flash comparator** (the project's
preserve-and-compare heuristic). A model-provenance gate asserts
both facts from `results/passes-manifest.json` before anything runs
(8 pools verified); a comparator gate re-derived all six E57-pool
consensus F1s from disk against the conditions manifest (6/6 at
tolerance 5e-5).

**Scope caveats carried by every result below**: 384 px / 487 tiles
(Era 2), not the registered Phase-4 scope; Pro pools exist only at
N = 3; the contrast available to A-06 moves temperature and thinking
level together (E40-class confound); E74 discloses that H6 itself
was never executed.

## A-06 — the Phase 2 decision rule

Registered: "If alternative outperforms Flash-optimal by ≥0.03 F1,
flag factor for adjustment"
(`docs/methodology/preregistration/osf/preregistration.md:677`,
registered without a CI condition). None of the four registered
factors (M/E, H5, T, O) is cleanly evaluable; the nearest available
contrast is the corner pair (carried T = 0.7 + MEDIUM vs alternative
T = 0.0 + HIGH), per modality:

| Modality | Carried (T0.7, MEDIUM) | Alternative (T0.0, HIGH) | Δ | Rule fires (Δ ≥ 0.03) | Δ CI95 (paired bootstrap, B = 1,000) |
|---|---:|---:|---:|---|---|
| Text | 0.7555 | 0.8045 | +0.0490 | **yes** | [+0.0267, +0.0703] |
| Image | 0.5950 | 0.6658 | +0.0708 | **yes** | [+0.0369, +0.1016] |

The registered rule fires in both modalities: on Pro, the
T = 0.0 + HIGH corner beats the carried T = 0.7 + MEDIUM corner by
more than the registered threshold, with delta CIs excluding zero
(the CI is the operational augmentation documented in
`lib_phase4_transfer.py`; the registered rule is the delta alone).
Because temperature and thinking move together, this flags "a factor"
without identifying which — consistent with H6's registered
prediction of "at most minor factor adjustments", and consistent
with the known Pro single-pass temperature preference
(`n1-baseline-matrix-384`: T = 0.0 > T = 0.7). It does not
constitute a clean registered Phase-2 verdict for any single factor.

## A-07 — the Phase 3 voting-threshold comparison

Registered: "Compare Pro optimal threshold to Flash optimal
threshold; Note any differences >10% relative"
(`…/preregistration.md:679-683`). **The registered form is
not-computable-as-registered**: the Flash production optimum is
26-of-30 (an N = 30 pool) while Pro pools exist only at N = 3, and a
raw vote-count comparison across those pool sizes is
data-independent (every k ∈ {1, 2, 3} differs from 26 by > 88 %
relative — a tier1 test documents this). The computable form is
**matched-N**: genuine-Pro N = 3 voting curves against the E57
Flash-comparator N = 3 curves at the same configuration and corpus.

| Modality | Pro curve (k = 1/2/3, F1@20 m) | Flash curve (E57 pools) | Pro optimal | Flash optimal | Relative diff | Verdict |
|---|---|---|---|---|---|---|
| Text | 0.8602 / 0.8558 / 0.8494 | 0.4726 / 0.5199 / 0.5665 | **k = 1** | k = 3 | 67 % | **flagged**; > 20 % ⇒ the registered extended N = 30 test is indicated but cannot execute in a $0 block |
| Image | 0.6909 / 0.7149 / 0.7223 | 0.5509 / 0.5499 / 0.5525 | k = 3 | k = 3 | 0 % | transfers |

Descriptive fraction-form only (no registered verdict attaches): the
Flash production optimum is 26/30 = 0.867 of the pool; Pro text's
optimum is 1/3 = 0.333.

Two observations worth carrying forward. First, the text-track
optimal threshold **reverses between models at matched N** (Pro
prefers the permissive union, the Flash comparator the strict
intersection), so the vote threshold again behaves as a property of
the pipeline–corpus–model encounter rather than of the
configuration (cf. Obs 358's threshold-transfer lesson). Second, the
Pro text N = 3 union (0.8602) clearly beats Pro single-pass
(0.8045) — a +0.056 gain from three passes at k = 1, so consensus
volume helps Pro text even at tiny N; both are small-N observations
on 487 tiles and neither carries a registered verdict.

## A-09 — the scope-limitation gate

Registered: "Full per-model optimisation only if Pro demonstrates
substantially superior cost-effectiveness (≥20% higher F1 at
comparable cost, OR comparable F1 at ≤50% cost)"
(`…/preregistration.md:691`). Cost basis per the audit adjudication:
audited per-pass `cost_usd` from `results/passes-manifest.json` on
both sides for the matched-configuration comparison; the audited
all-Flash Pareto v2 frontier
(`results/verifier-robustness/pareto/pareto_v2.json`, token-load
audit basis, same corpus and buffer) as the Flash-optimal yardstick.
Comparability windows below are operational choices, not registered.

**Matched-configuration basis (model swap at the Pro corners):**

| Modality | Pro single pass | Flash same-config N = 3 best | F1 ratio | Limb 1 (≥ 1.20 at comparable cost) |
|---|---|---|---:|---|
| Text | 0.8045 @ $1.85/pass | 0.5665 @ $1.79 (3 × $0.60) | 1.42 | fires |
| Image | 0.6658 @ $15.74/pass | 0.5525 @ $11.92 (3 × $3.97) | 1.21 | fires |

**Flash-optimal frontier basis (the registered gate's yardstick):**
the audited frontier offers min6 **F1 0.8784 at $2.43** and min11
**0.8835 at $4.00** (487-tile corpus, F1@20 m). Pro's best cell in
this block is the text N = 3 union at **0.8602 for $5.56**
(3 × $1.85), and Pro single-pass is **0.8045 at $1.85**. Pro
therefore offers **lower F1 at higher cost than the Flash frontier
at every available operating point**: neither registered limb fires
(no ≥20 % F1 advantage at comparable cost; no comparable F1 at
≤50 % cost — Pro is dearer per unit of F1 throughout).

**Verdict: the registered gate is CLOSED** on the basis it was
written for — Pro versus Flash as actually optimised. The
matched-configuration limb-1 firings measure something real but
different: the pure model effect at Pro's preferred corner, where
Flash was never optimised (E57's own narrative). Reporting both
bases keeps the gate honest without letting a strawman comparison
open it.

## A-08 — explicitly not computed

A-08 (the registered three-way transfer verdict,
`…/preregistration.md:693-699`) is not computed: the registered
Phase 2 varies four factors one at a time on Pro, and the existing
Pro data vary none of them cleanly — the only available contrast is
the confounded corner pair, so "all factors within 0.03 of
Flash-optimal" is unevaluable. Computing a verdict from one
confounded factor would misrepresent the registered criterion. The
honest disposition is not-computable-as-registered (block-plan
hardening 7 converts this silence into a statement).

## What this means for the ~US$48 re-run decision (PI's call)

Report, not decision. Inputs the walk asked for:

1. **A-09 is CLOSED** against the Flash frontier — the registered
   scope limitation does not license full per-model Pro
   optimisation on the existing evidence.
2. **A-06 flags the confounded corner factor both ways with clear
   CIs**, and **A-07's text threshold reverses at matched N** —
   both are exactly the kind of question the registered Phase-4
   design (four factors, OFAT, matched scope) would resolve
   cleanly, and neither can be settled further at $0.
3. The E40 confound (Pro cannot run MINIMAL thinking) **persists by
   construction** — a re-run cannot fully remove it, which was the
   unexecuted register's caution when pricing the re-run at
   ~US$48 (`studies/phase4-transfer.yaml:165` estimate vintage).

## Changelog

### 2026-08-17 — Original publication

S135 analysis block items 4–6, executed on sapphire ($0 API) after
the clean-context audit re-anchored the inputs onto genuine-Pro
data (BLOCKER-1). Register rows `h6-a06-decision-rule`,
`h6-a07-voting-thresholds`, `h6-a09-cost-gate` authored with
PROPOSED post-hoc classification (discharge principle, Obs 413);
PI ratification queued.
