# H6 registered $0 analyses — A-06, A-07, A-09 on the existing genuine-Pro data

> **Last revised**: 2026-09-08 (A-07 and A-09 refreshed on the Flash
> comparator rebuilt from the E71-recovered passes, PI instruction S150;
> no verdict changes, the image fragility flag retired). See
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
(12 pools verified after the verification round extended it to the
pv-diag Pro corners); a comparator gate re-derived all six E57-pool
consensus F1s from disk against the conditions manifest (6/6 at
tolerance 5e-5).

**Scope caveats carried by every result below**: 384 px / 487 tiles
(Era 2), not the registered Phase-4 scope; Pro pools exist only at
N = 3; M/E, H5, and O are unvaried in the existing Pro data; E74
discloses that H6 itself was never executed.

## A-06 — the Phase 2 decision rule

Registered: "If alternative outperforms Flash-optimal by ≥0.03 F1,
flag factor for adjustment"
(`docs/methodology/preregistration/osf/preregistration.md:677`,
registered without a CI condition).

**Revised at the verification round.** The original run reported
only the confounded corner contrast (T = 0.0 + HIGH vs
T = 0.7 + MEDIUM) under the premise that no registered factor was
cleanly evaluable. The blind verifier falsified that premise: the
full genuine-Pro thinking × temperature 2 × 2 exists per modality
(the `n1-pro-rerun-384` corners plus the `pv-diag-384` Pro
baselines, all `gemini-3.1-pro-preview` under the extended
provenance gate, same Era-2 corpus, identical instruction and
library hashes). The registered factor **T** is therefore cleanly
evaluable at matched thinking:

| Modality | Thinking | T=0.7 F1 | T=0.0 F1 | Δ | Rule fires (Δ ≥ 0.03) | Δ CI95 (paired bootstrap, B = 1,000) |
|---|---|---:|---:|---:|---|---|
| Text | HIGH | 0.7450 | 0.8045 | +0.0595 | **yes** | [+0.0340, +0.0846] |
| Text | MEDIUM | 0.7555 | 0.7921 | +0.0366 | **yes** | [+0.0113, +0.0620] |
| Image | HIGH | 0.5908 | 0.6658 | +0.0750 | **yes** | [+0.0421, +0.1076] |
| Image | MEDIUM | 0.5950 | 0.6555 | +0.0605 | **yes** | [+0.0299, +0.0888] |

The thinking contrast at matched temperature (not a registered
Phase-2 factor; decomposition context) reaches 0.03 in none of the
four cells (+0.0124, −0.0105, +0.0103, −0.0042; every CI straddles
zero). **Temperature is the driver**: the registered rule fires for
factor T in all four cells, with delta CIs excluding zero, and the
question the confounded framing left open ("which factor?") is
answered at $0. Consistent with the known Pro single-pass
temperature preference (`n1-baseline-matrix-384`). Replicate-count
caveat: the two HIGH T = 0.7 corners average 10 (text) and 5
(image) passes against 3 everywhere else (same estimator, differing
precision); the two delta estimators (manifest eval vintage vs
pass-averaged micro) are reconciled by an in-script gate and agree
to ≤ 0.0005. The original confounded contrast is retained in the
artefact as a superseded record.

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
| Text | 0.8602 / 0.8558 / 0.8494 | 0.4634 / 0.5203 / 0.5748 | **k = 1** | k = 3 | 67 % | **flagged**; > 20 % ⇒ the registered extended N = 30 test is indicated but cannot execute in a $0 block |
| Image | 0.6909 / 0.7149 / 0.7223 | 0.5614 / 0.5760 / 0.5854 | k = 3 | k = 3 | 0 % | transfers (robust: margin 0.0094 > 0.005 on the recovered sweeps) |

Flash curves refreshed 2026-09-08 on the comparator sweeps rebuilt from
the E71-recovered passes (`185681674`, re-scored `10e933ded`); the
pre-recovery curves were 0.4726 / 0.5199 / 0.5665 (text) and 0.5509 /
0.5499 / 0.5525 (image). Every recovered image cell rises (k = 3 by
+0.033); text moves within ±0.01. Neither optimum nor either verdict
moves.

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

**Fragility (verification round; refreshed 2026-09-08).** On the
pre-recovery comparator both optima sat on near-flat curves — the Flash
image winner (k = 3) led its runner-up by 0.0015 F1 and the Pro text
winner (k = 1) by 0.0045, both under the artefact's 0.005 fragility
threshold — and had the Flash image optimum landed on k = 1 the image
verdict would have flipped from "transfers" to flagged at 200 %
relative. On the sweeps rebuilt from the recovered passes the Flash
image winner leads by 0.0094 F1, above the threshold, so the
image "transfers" verdict is robust to that margin and the S135
MEDIUM-3 flag is retired; the Pro text winner still leads by 0.0045
(fragile), and the text "flagged" verdict remains robust (67 % against
a 10 % rule). The Flash comparator passes are 485–486 of 487 tiles
after recovery — the E71 residue that failed both recovery tiers — and
the curves now consume the post-recovery detections; the earlier
one-sided gap (the pre-recovery scoring at 458–472 tiles, E71 rider
2026-09-07) no longer applies. The image "transfers"
verdict is therefore not robust at these margins; the text
"flagged" verdict is (67 % against a 10 % rule). The matched-N form
is itself post-hoc; the library's "run extended N = 30 test"
message is operational wording, not a registered trigger.

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

**Matched-configuration basis (model swap at the Pro corners;
corrected at the verification round):**

| Modality | Pro single pass | Flash same-config N = 3 best | F1 ratio | Cost ratio | Limb 1 |
|---|---|---|---:|---:|---|
| Text | 0.8045 @ $1.85/pass | 0.5748 @ $1.79 (3 × $0.60) | 1.40 | 1.03 | fires (cost within the declared 10 % window) |
| Image | 0.6658 @ $15.74/pass | 0.5854 @ $11.92 (3 × $3.97) | 1.14 | 1.32 | **does not fire** on either count — the F1 ratio is under 1.20 on the recovered comparator (1.21 on the pre-recovery sweeps) and a 32 % cost premium is not "comparable cost" (the original run mislabelled this "within ~5 %") |

Comparator basis (refreshed 2026-09-08): the Flash same-configuration
single-pass aggregates are the `-post-e71` rows (text F1
0.4919, image 0.5446, scored at 484–486 of 487 tiles) and the
N = 3 curves the rebuilt sweeps; the 2026-08-17 artefact had consumed
values scored at 458–472 tiles (E71 rider 2026-09-07). The artefact's
`coverage_disclosure` now renders both sides' ranges from the passes
manifest. The gate verdict does not rest on this basis.

**Flash-optimal frontier basis (the registered gate's yardstick):**
the audited frontier offers min6 **F1 0.8784 at $2.43** and min11
**0.8835 at $4.00** (487-tile corpus, F1@20 m). Pro's candidate
points are single-pass **0.8045 at $1.85** and the text N = 3 union
at **0.8602 for $5.56** (3 × $1.85). Both limbs are now computed in
code against both rungs (the artefact carries
`registered_gate_verdict` so machine readers and prose cannot
diverge). Limb 1 never fires: Pro's F1 is below every frontier F1,
so no ≥ 20 % advantage exists at any cost. Limb 2 never fires: no
Pro point is within 0.02 F1 of a frontier point, and no Pro point
reaches ≤ 50 % of a frontier cost (the nearest case, Pro
single-pass at 76 % of min6's cost, gives up 0.0739 F1 — far
outside "comparable"). One arithmetic correction from the
verification round: Pro single-pass text is *cheaper* than min6 in
absolute and per-F1-point terms, so the original "dearer per unit
of F1 throughout" wording was wrong; the verdict rests on the limbs
as registered, not on dominance. Cost-basis note: the frontier's
dollars are modelled token-load-audit flex rates while the Pro
side is the per-pass extractor's `cost_usd`; if Pro was billed
above flex, the Pro side is over-costed and the verdict is
conservative.

**Verdict: the registered gate is CLOSED**
(`registered_gate_verdict` in `a09_cost_gate.json`) on the basis it
was written for — Pro versus Flash as actually optimised. The
matched-configuration text limb-1 firing measures something real
but different: the pure model effect at Pro's preferred corner,
where Flash was never optimised (E57's own narrative). Reporting
both bases keeps the gate honest without letting a strawman
comparison open it.

## A-08 — explicitly not computed

A-08 (the registered three-way transfer verdict,
`…/preregistration.md:693-699`) is not computed: the registered
Phase 2 varies four factors one at a time on Pro, and the existing
Pro data cleanly vary exactly **one** of them (T, via the completed
2 × 2 — the verification round superseded the earlier "none
cleanly" premise). M/E, H5, and O remain unvaried, so "all factors
within 0.03 of Flash-optimal" is unevaluable, and a three-way
verdict from one factor would misrepresent the registered
criterion. The honest disposition is not-computable-as-registered
(block-plan hardening 7 converts this silence into a statement).

## What this means for the ~US$48 re-run decision (PI's call)

Report, not decision. Inputs the walk asked for:

1. **A-09 is CLOSED** against the Flash frontier — the registered
   scope limitation does not license full per-model Pro
   optimisation on the existing evidence.
2. **The factor question is now answered at $0** (verification
   round): temperature is the driver (fires in all four 2 × 2
   cells with CIs excluding zero), thinking level is not
   (reaches 0.03 nowhere). What a ~US$48 re-run would still add:
   the three unvaried registered factors (M/E, H5, O), the
   registered scope, and an N = 30 Pro voting curve to settle
   A-07's text reversal (currently a fragile small-N result).
3. The E40 constraint (Pro cannot run MINIMAL thinking) **persists
   by construction** — a re-run cannot remove it, which was the
   unexecuted register's caution when pricing the re-run at
   ~US$48 (`studies/phase4-transfer.yaml:165` estimate vintage).

## Changelog

### 2026-09-08 — A-07 and A-09 refreshed on the recovered comparator (S150, PI instruction)

**Refresh trigger**: the recovery-consistency audit
(`reports/recovery-consistency-audit-2026-09-08.md`) found the Flash
comparator's consensus sweeps still voting over the pre-recovery
detections; the PI instructed the refresh. Sweeps rebuilt
(`scripts/rebuild_recovered_consensus.py`, `185681674`; pre-recovery
sweeps archived under `archive/pre-recovery-2026-09-08/`), the six
cells re-scored at their committed protocol (`10e933ded`), the rows
re-pointed, and `scripts/h6_registered_analyses.py` re-run on sapphire
with the comparator aggregates taken from the `-post-e71` rows. A
control rebuild of the archived pre-recovery passes with today's
builder reproduces the April sweeps exactly (665/627/604; 1118/946/783),
so every delta below is a recovery effect. Pre-refresh artefacts:
`archive/pre-recovery-2026-09-08/h6-registered-analyses/`.

**Before → after**:

| Claim | Before | After |
|---|---|---|
| A-07 Flash text curve (k = 1/2/3) | 0.4726 / 0.5199 / 0.5665 | 0.4634 / 0.5203 / 0.5748 |
| A-07 Flash image curve | 0.5509 / 0.5499 / 0.5525 | 0.5614 / 0.5760 / 0.5854 |
| A-07 image optimum margin | 0.0015 (fragile) | 0.0094 (robust; S135 MEDIUM-3 retired) |
| A-09 Flash same-config single pass (text / image) | 0.4942 / 0.5276 (scored at 458–472 tiles) | 0.4919 / 0.5446 (484–486 tiles) |
| A-09 matched-config F1 ratio (text / image) | 1.42 / 1.21 | 1.40 / 1.14 |
| A-09 image matched-config limb | not fired (cost) | not fired (F1 ratio and cost) |

**What did NOT change**: the A-09 CLOSED verdict (decided by the
frontier); both A-07 verdicts (text flagged at 67 %, image transfers);
every Pro-side number; A-06 (its artefact carries only a new
`generated_at`); the text-track optimum reversal.

### 2026-09-07 — The Flash comparator's coverage as scored (E71 rider)

**Refresh trigger**: ruling 3a's re-score of the nine pre-recovery
scorings (`results/rescore-2026-09-07/`, `26cc430ad`) showed that the
A-07/A-09 comparator evaluations were scored at the pre-recovery
vintage, while this document and the A-09 artefact's
`coverage_disclosure` quoted the post-recovery manifest count.

**Before → after**:

| Claim | Before | After |
|---|---|---|
| Flash comparator coverage as scored | 485–486 of 487 tiles (1–2 short) | 458–472 of 487 (15–29 short per pass); the 485–486 is the post-recovery count |
| Size of the one-sided gap | "slightly depresses the Flash curve" | 15–29 tiles per pass; not measured on the consensus curves (never rebuilt) |

**What did NOT change**: every number in every table; the A-09
CLOSED verdict (decided by the frontier); the A-07 verdicts and their
fragility flags; the A-08 disposition. The `a09_cost_gate.json`
artefact is left as generated (its note is corrected here, not
edited in place); both register rows gain `E71` in `deviations`.
Commit: the one landing this entry with the `-post-e71` rows.

### 2026-08-17 (later) — Verification round: A-06 rebuilt on the full 2×2

Blind fresh-context verifier (~60 claims re-derived, ~54
computations; all quotes, F1s, deltas, CIs, and costs reproduced) +
adversarial code audit (3 HIGH, 9 MEDIUM, 10 LOW). Headline
correction (verifier HIGH-1): the full genuine-Pro thinking ×
temperature 2 × 2 exists in committed data, falsifying the
"confound cannot be resolved at $0" premise — A-06 rebuilt, with
**temperature identified as the driver** (before → after: "flags a
factor without identifying which" → "factor T fires in all four
cells; thinking reaches 0.03 nowhere"). A-09: limbs now computed in
code with declared windows and an in-artefact
`registered_gate_verdict` (audit H-1); the image matched-config
limb no longer fires (32 % cost premium mislabelled "within ~5 %",
audit/verifier MEDIUM); the false "dearer per unit of F1
throughout" dominance wording replaced by the limb arithmetic
(verifier MEDIUM-1). A-07: margin/fragility fields (both optima
< 0.005 over runner-up), one-sided partial-coverage disclosure,
registration-status note. Materialisation gates + voting summaries
added (audit H-2/M-1/L-9). What did NOT change: every headline
number of the original run; the A-09 CLOSED verdict; the A-07
verdicts; the not-computable A-08 disposition (its reason
corrected).

### 2026-08-17 — Original publication

S135 analysis block items 4–6, executed on sapphire ($0 API) after
the clean-context audit re-anchored the inputs onto genuine-Pro
data (BLOCKER-1). Register rows `h6-a06-decision-rule`,
`h6-a07-voting-thresholds`, `h6-a09-cost-gate` authored with
PROPOSED post-hoc classification (discharge principle, Obs 413);
PI ratification queued.
