# H6 registered $0 analyses — A-06, A-07, A-09 on the existing genuine-Pro data

> **Last revised**: 2026-10-17 (A-06 gains a dated note on the D64
> same-day replication, PI rulings D64, D66, and D67: temperature is the
> driver in text and image on same-day data, and the first day's image
> thinking contrast at T = 0.0 was not confirmed the next day; nothing
> registered changes). 2026-10-14: A-07 regenerated under the D50
> scorer, PI rulings D62 (5) and D65: the Flash comparator curves rise
> by 0.0012–0.0018 F1 and the Pro text curve by 0.0024, with no optimal
> k, fragility flag, or verdict changing; the row awaited re-signing
> (re-signed 2026-10-14). 2026-10-12: A-09 re-derived on the audited
> cost basis with the not-like-for-like caveat, PI ruling D61 (4): the
> registered gate stays CLOSED, the matched-configuration text limb no
> longer fires, and the row awaited re-signing (re-signed 2026-10-13);
> earlier the same day, A-06 regenerated with the D42 permutation p and
> Benjamini–Hochberg, D61 (3), and the finding that the Pro HIGH T = 0.0
> passes did not think recorded against A-06's HIGH-cell reading.
> 2026-09-08: A-07 and A-09 refreshed on the Flash comparator rebuilt
> from the E71-recovered passes. See [§ Changelog](#changelog) for
> revision history.

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

**Note, 2026-10-12 (PI rulings D61 (3) and D61 (4)).** Two additions;
the table above, the four rule verdicts, and the registered outcome
text are unchanged.

*p-values (D61 (3)).* The artefact now carries the paired tile-swap
permutation p that PI ruling D42 adopted (10,000 permutations, seed 42,
through the shared helper `e45_bootstrap_pairings.paired_bootstrap`,
`3c3023f51`), in place of the retired bootstrap p, which sat at its
floor of 0.001 in all four cells. Benjamini–Hochberg (BH) is applied
across the four registered factor-T contrasts as one family. The
registered rule has no p condition, so BH is reported beside it and
decides nothing:

| Contrast (T = 0.0 − T = 0.7) | Bootstrap p (retired) | Permutation p | BH-adjusted p | Discordant tiles |
|---|---:|---:|---:|---:|
| Text, HIGH | 0.001 (floor) | 0 (< 0.0001) | 0 | 175 |
| Text, MEDIUM | 0.001 (floor) | 0.0019 | 0.0019 | 147 |
| Image, HIGH | 0.001 (floor) | 0 (< 0.0001) | 0 | 218 |
| Image, MEDIUM | 0.001 (floor) | 0.0002 | 0.00027 | 192 |

All four reject at q = 0.05. Deltas, intervals, and the four flags are
unchanged.

*Pro HIGH did not think (D61 (4)).* The Pro HIGH T = 0.0 passes
(`n1-pro-rerun-384`, `pro-{text,image}-high-t0`) delivered no thinking:
they record zero thought tokens, and the June 2026 invoice confirms it
(`reports/manipulation-check-2026-10-05.md` § D; Obs 509). Whether the
T = 0.7 Pro HIGH comparators (`pv-diag-384`,
`pro-high-{text,image}-n5`) thought is unknown: they carry no recorded
usage and no matching invoice line. At HIGH, therefore, the factor-T
contrast compares T = 0.0 without thinking against T = 0.7 with
thinking unknown, and the reading "temperature is the driver" is open
there: the gap is temperature, or thinking delivered at T = 0.7 and not
at T = 0.0. The thinking context at T = 0.0 (HIGH − MEDIUM) likewise
compares Pro without thinking against MEDIUM thinking. Nothing is
re-labelled here; the register row's outcome text is the PI's to
revise.

**Note, 2026-10-15 (PI rulings D64, D66, and D67): the same-day
genuine-Pro replication.** The table above, the four rule verdicts, the
artefact, and the registered outcome text are unchanged. D64 re-ran the
2 × 2 on one date, in one mode, with thinking booked per pass
(`outputs/pro-2x2-replication-2026-10-13/`): five passes per text corner
and three per image corner on 2026-10-13, then three more per image
corner on 2026-10-14. Those three were a confirmatory test of the two
image contrasts that were borderline on the first day, with criteria
fixed before any of their F1 values were computed (the first day's sign,
BH-adjusted p < 0.05 across the two, |Δ| ≥ 0.03, and |Δ| above the
replicate floor of the new passes). The replicate floor is the 95th
percentile of the F1 differences between repeat passes of the same
corner: ordinary run-to-run variation. Record:
`reports/s164-agent-records/d64-a06-replication.md` (PR #48).

**Text** (five passes per corner, all on 2026-10-13):

| Contrast | Committed (table above) | D64 |
|---|---:|---:|
| T = 0.0 − T = 0.7 at HIGH | +0.0595 | +0.0500 |
| T = 0.0 − T = 0.7 at MEDIUM | +0.0366 | +0.0464 |
| HIGH − MEDIUM at T = 0.0 | +0.0124 | +0.0026 |
| HIGH − MEDIUM at T = 0.7 | −0.0105 | −0.0010 |

**Image** (three passes per corner on each of two days):

| Contrast | Committed (table above) | 2026-10-13 (passes 1–3) | 2026-10-14 (passes 4–6, the confirmatory test) | All six passes (secondary) |
|---|---:|---:|---:|---:|
| T = 0.0 − T = 0.7 at HIGH | +0.0750 | +0.0690 | +0.0786 | +0.0738 |
| **T = 0.0 − T = 0.7 at MEDIUM** | +0.0605 | +0.0336 | **+0.0653, replicates** | +0.0494 |
| **HIGH − MEDIUM at T = 0.0** | +0.0103 | +0.0374 | **+0.0202, partly** | +0.0288 |
| HIGH − MEDIUM at T = 0.7 | −0.0042 | +0.0020 | +0.0069 | +0.0044 |

The two bold rows were borderline on the first day and were the subject
of the confirmatory test. The six-pass column is reported for
completeness but does not decide replication. Passes 4–6 were added
because the first day's results looked borderline, so pooling them with
the first day would overstate the evidence.

In text, "temperature is the driver" holds with the date, mode, and
thinking confounds removed. Both temperature contrasts fire the rule,
reject after BH, and exceed the same-day replicate floor (0.0116), and
the thinking contrasts are near zero. In image, the temperature contrast
fires and exceeds the floor at both thinking levels on both days. At
MEDIUM, borderline on the first day (BH-adjusted p 0.032, 0.0036 above
the rule), it was confirmed on three independent passes run the next day
(BH-adjusted p 0.0002). On the first day the image thinking contrast at
T = 0.0 reached 0.03 and rejected after BH (BH-adjusted p 0.043),
against this section's reading that the thinking contrast "reaches 0.03
in none of the four cells". On the next day it was +0.0202 (BH-adjusted
p 0.138, below 0.03 and below that day's floor of 0.0205): same
direction on three further passes but not confirmed; the check had
roughly even odds of passing even if the effect were as large as first
seen. Across the six image passes it is +0.0288, below 0.03 (secondary).
The thinking level was requested rather than delivered (image HIGH
delivered under one thought token per request at T = 0.0, and MEDIUM
about 11), so the contrast cannot test thinking. Between the two days
three image corners fell by 0.011–0.026 F1 and one rose by 0.006, the
largest move (0.0259) just above the within-day replicate floor
(0.0254); that change moved the two confirmatory contrasts in opposite
directions. Under the mapping the PI fixed before the confirmatory test
(D67), A-06's headline stays "temperature is the driver"; and the
register row's outcome carries the same reading in a dated paragraph.

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
| Text | 0.8626 / 0.8582 / 0.8519 | 0.4647 / 0.5217 / 0.5764 | **k = 1** | k = 3 | 67 % | **flagged**; > 20 % ⇒ the registered extended N = 30 test is indicated but cannot execute in a $0 block |
| Image | 0.6909 / 0.7149 / 0.7223 | 0.5631 / 0.5778 / 0.5873 | k = 3 | k = 3 | 0 % | transfers (robust: margin 0.0095 > 0.005 on the recovered sweeps) |

Flash curves refreshed 2026-09-08 on the comparator sweeps rebuilt from
the E71-recovered passes (`185681674`, re-scored `10e933ded`); the
pre-recovery curves were 0.4726 / 0.5199 / 0.5665 (text) and 0.5509 /
0.5499 / 0.5525 (image). Every recovered image cell rises (k = 3 by
+0.033); text moves within ±0.01. Neither optimum nor either verdict
moves.

All curves rescored 2026-10-14 under the D50 scorer (detections
scoped per sheet, never re-keyed across sheets; PI rulings D62 (5)
and D65): the Flash comparator curves rise by 0.0012–0.0016 F1 (text)
and 0.0017–0.0018 (image), the Pro text curve by 0.0024 at every k,
and the Pro image curve does not move. Before D50 the table read
0.8602 / 0.8558 / 0.8494 (Pro text), 0.4634 / 0.5203 / 0.5748 (Flash
text), and 0.5614 / 0.5760 / 0.5854 (Flash image). Again neither
optimum nor either verdict moves.

Descriptive fraction-form only (no registered verdict attaches): the
Flash production optimum is 26/30 = 0.867 of the pool; Pro text's
optimum is 1/3 = 0.333.

Two observations worth carrying forward. First, the text-track
optimal threshold **reverses between models at matched N** (Pro
prefers the permissive union, the Flash comparator the strict
intersection), so the vote threshold again behaves as a property of
the pipeline–corpus–model encounter rather than of the
configuration (cf. Obs 358's threshold-transfer lesson). Second, the
Pro text N = 3 union (0.8626) clearly beats Pro single-pass
(0.8045) — a +0.058 gain from three passes at k = 1, so consensus
volume helps Pro text even at tiny N; both are small-N observations
on 487 tiles and neither carries a registered verdict.

**Fragility (verification round; refreshed 2026-09-08 and, under
D50, 2026-10-14).** On the pre-recovery comparator both optima sat
on near-flat curves — the Flash image winner (k = 3) led its runner-up by 0.0015 F1 and the Pro text
winner (k = 1) by 0.0045, both under the artefact's 0.005 fragility
threshold — and had the Flash image optimum landed on k = 1 the image
verdict would have flipped from "transfers" to flagged at 200 %
relative. On the sweeps rebuilt from the recovered passes the Flash
image winner leads by 0.0095 F1 (0.0094 before D50), above the
threshold, so the image "transfers" verdict is robust to that margin
and the S135 MEDIUM-3 flag is retired; the Pro text winner still leads
by 0.0044 (0.0045 before D50; fragile), and the text "flagged" verdict
remains robust (67 % against a 10 % rule). The Flash comparator passes are 485–486 of 487 tiles
after recovery — the E71 residue that failed both recovery tiers — and
the curves now consume the post-recovery detections; the earlier
one-sided gap (the pre-recovery scoring at 458–472 tiles, E71 rider
2026-09-07) no longer applies. The matched-N form
is itself post-hoc; the library's "run extended N = 30 test"
message is operational wording, not a registered trigger.

## A-09 — the scope-limitation gate

Registered: "Full per-model optimisation only if Pro demonstrates
substantially superior cost-effectiveness (≥20% higher F1 at
comparable cost, OR comparable F1 at ≤50% cost)"
(`…/preregistration.md:691`). Cost basis: the register's audited
per-pass `cost_usd` from `results/passes-manifest.json` (PI ruling D11;
re-derived on it 2026-10-12 under D16 and D61 (4)) on both sides of the
matched-configuration comparison; the audited all-Flash Pareto v2
frontier (`results/verifier-robustness/pareto/pareto_v2.json`,
token-load audit basis, same corpus and buffer) as the Flash-optimal
yardstick. Comparability windows below are operational choices, not
registered. F1s are on today's scorer (D50), which raised the Flash
comparator's N = 3 curves by about 0.002 and Pro's text union to
0.8626; the A-07 table above shows the same D50 values since A-07 was
regenerated on 2026-10-14.

**Matched-configuration basis (model swap at the Pro corners;
re-derived on audited costs 2026-10-12):**

| Modality | Pro single pass | Flash same-config N = 3 best | F1 ratio | Cost ratio | Limb 1 |
|---|---|---|---:|---:|---|
| Text | 0.8045 @ $0.93/pass (flex; no thinking delivered) | 0.5764 @ $19.85 (3 × $6.62; standard, about 2.0 M thought tokens per pass) | 1.40 | 0.05 | **does not fire**: Pro is 95 % cheaper, which is not "comparable cost" |
| Image | 0.6658 @ $2.98/pass (standard; no thinking delivered) | 0.5873 @ $13.48 (3 × $4.49; standard, about 1.2 M thought tokens per pass) | 1.13 | 0.22 | **does not fire** on either count: the F1 ratio is under 1.20 and the cost is not comparable |

Limb 2 fires in neither modality (the F1s are not within 0.02). At its
own corner Pro is better and, on audited costs, far cheaper: a case
neither registered limb is worded for.

**Not like-for-like (PI ruling D61 (4); stated here, beside the cost
figures, before the row is re-signed).** The audited matched-configuration
costs compare different service tiers and different thinking. The Flash
comparator's audited $6.62 per text pass (mean of three) is
standard-tier pricing that includes about 2.0 million thought tokens per
pass ($0.60 without them), while Pro's $0.93 is the flex rate (its
standard-tier price is $1.85) with no thinking delivered. Pro's image
passes asked for flex but were served at standard, because the cached
path drops the service tier; they too delivered no thinking. Re-priced
on one tier with no thinking on either side, from the same recorded
tokens and the same rate card (`a09_cost_gate.json`,
`like_for_like_cost` under each modality and `cost_comparability_caveat`):

| Standard tier, no thinking on either side | Text | Image |
|---|---:|---:|
| Pro, one pass | $1.85 | $2.98 |
| Flash comparator, one pass | $0.60 | $0.78 |
| One Pro pass ÷ the comparator's three-pass consensus | 1.03 | 1.27 |
| One Pro pass ÷ one comparator pass | 3.1 | 3.8 |

The text ratio of 1.03 is the figure the 2026-09-08 artefact carried
on the estimate basis. The audited gap therefore reflects Pro's
undelivered thinking (Obs 509; `reports/manipulation-check-2026-10-05.md`
§ D) and the tier difference, not a cheaper model. (The image figures
are this re-derivation's; the ruling states the text case.)

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
points are single-pass **0.8045 at $0.93** and the text N = 3 union
at **0.8626 for $2.78** (3 × $0.93); on image, single-pass 0.6658 at
$2.98. Both limbs are computed in code against both rungs (the
artefact carries `registered_gate_verdict` so machine readers and
prose cannot diverge). Limb 1 never fires: Pro's F1 is below every
frontier F1 (2 to 25 % lower), so no ≥ 20 % advantage exists at any
cost. Limb 2 never fires: the one Pro point within 0.02 F1 of a
frontier point, the text union against min6 (0.8626 against 0.8784),
costs 1.14 times min6; and the Pro points at or under half a frontier
cost, single-pass text at 38 % of min6's cost and 23 % of min11's,
give up 0.0739 and 0.0790 F1, far outside "comparable". One
arithmetic correction from the verification round stands: Pro
single-pass text is *cheaper* than min6 in absolute and per-F1-point
terms, so the original "dearer per unit of F1 throughout" wording was
wrong; the verdict rests on the limbs as registered, not on
dominance. Cost-basis note: the frontier's dollars are modelled
token-load-audit flex rates, while Pro's are audited: text at flex,
image at standard. Pro image is therefore over-costed against the
frontier's flex basis, which is conservative for CLOSED. All Pro
figures here are Pro without thinking (D61 (4)); what Pro with
thinking delivered would score or cost is not measured.

**Verdict: the registered gate is CLOSED**
(`registered_gate_verdict` in `a09_cost_gate.json`) on the basis it
was written for — Pro versus Flash as actually optimised. On audited
costs neither matched-configuration limb fires; the matched
comparison measures something real but different: the pure model
effect at Pro's preferred corner, where Flash was never optimised
(E57's own narrative), on a cost gap that is not like-for-like.
Reporting both bases keeps the gate honest without letting a
strawman comparison open it.

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
   (reaches 0.03 nowhere). Open at HIGH since 2026-10-12: the Pro
   HIGH T = 0.0 passes did not think (see the A-06 note). What a
   ~US$48 re-run would still add:
   the three unvaried registered factors (M/E, H5, O), the
   registered scope, and an N = 30 Pro voting curve to settle
   A-07's text reversal (currently a fragile small-N result).
3. The E40 constraint (Pro cannot run MINIMAL thinking) **persists
   by construction** — a re-run cannot remove it, which was the
   unexecuted register's caution when pricing the re-run at
   ~US$48 (`studies/phase4-transfer.yaml:165` estimate vintage).

## Changelog

### 2026-10-17 — A-06: the D64 same-day replication noted (PI rulings D64, D66, and D67)

A dated note is added under A-06. It records the D64 same-day
replication and its confirmatory test on image passes 4–6
(`reports/s164-agent-records/d64-a06-replication.md`, PR #48). Nothing
above it changes: the table, the four rule verdicts,
`a06_decision_rule.json`, and the registered outcome text. Commit: the
one that applies it.

### 2026-10-14 — A-07 regenerated under the D50 scorer (PI rulings D62 (5) and D65)

**Refresh trigger**: PI ruling D50 (2026-10-07) made the shared scorer
scope detections per sheet by tile geometry and never re-key a
detection across sheets. `a07_voting_thresholds.json` had not been
regenerated since 2026-09-08; the D57 (4) Phase 3 re-score and the S164
re-score (`reports/s164-agent-records/rescore-repaired-gs.md` § 3.4, on
branch `rescore-repaired-gs`) both found 25 of its leaves moving under
today's scorer. PI ruling D62 (5), "now", recorded in D65: regenerate
A-07 as its own small PR. `scripts/h6_registered_analyses.py`
(unchanged) was run on sapphire at `90294a283` in two independent runs
(separate worktrees, new processes); they agree byte for byte apart
from `generated_at`. The artefact landed in `468ada2fc`.
`a06_decision_rule.json` and `a09_cost_gate.json`, which the same
script writes, came out byte-identical to the committed files apart
from `generated_at` and were not committed.

**Before → after** (`a07_voting_thresholds.json`, the 25 leaves; F1 @
20 m):

| Quantity | Before (2026-09-08) | After (D50 scorer) |
|---|---|---|
| Pro text curve, k = 1 / 2 / 3 | 0.8602 / 0.8558 / 0.8494 | 0.8626 / 0.8582 / 0.8519 |
| Flash comparator text curve | 0.4634 / 0.5203 / 0.5748 | 0.4647 / 0.5217 / 0.5764 |
| Flash comparator image curve | 0.5614 / 0.5760 / 0.5854 | 0.5631 / 0.5778 / 0.5873 |
| Pro text margin over runner-up | 0.004457 | 0.004423 |
| Flash text margin over runner-up | 0.054448 | 0.054612 |
| Flash image margin over runner-up | 0.009411 | 0.00948 |
| Image fragility caveat (`scope_caveats`) | "leads its runner-up by 0.0094 F1" | "… by 0.0095 F1" |
| Comparator gate, `committed` and `recomputed` (six cells each) | the pre-D50 values | the D50 values above; 6/6 still pass at 5e-5 |

In this document: the A-07 table, a dated note under it, the union
gain (0.8602 → 0.8626 against the unchanged single-pass 0.8045, so
+0.056 → +0.058), the fragility paragraph (0.0094 → 0.0095 and
0.0045 → 0.0044, the earlier values kept in brackets), and the A-09
section's pointer to the A-07 table.

**What did NOT change**: every optimal k (text: Pro k = 1, Flash
k = 3; image: both k = 3); both matched-N verdicts (text flagged at
67 % relative, image transfers at 0 %); the fragility flags (the Pro
text margin stays under 0.005, so text stays fragile; the Flash image
margin stays above it, so the retired image flag stays retired); the
Pro image curve (0.6909 / 0.7149 / 0.7223); the fraction-form
descriptives; the model-provenance gate (12 pools); the Pro N = 3
consensus files under `outputs/h11/n1-pro-rerun-384/`, rewritten
byte-identical. The register row `h6-a07-voting-thresholds` quotes
nine of the moved values and the derived union gain in its outcome
text, so its signature of 2026-09-10T06:56:15Z lapses: the row is set
to `re-sign-pending` with a dated D9-pattern note (the prior signature
kept in `history`), and its outcome text is unchanged. A redraft with
only those numbers updated is in `reports/s164-agent-records/a07-d50.md`,
for the PI.

**Removed at the PI's direction (Session 164)**: the fragility
paragraph's closing sentence, "The image "transfers" verdict is
therefore not robust at these margins; the text "flagged" verdict is
(67 % against a 10 % rule).", contradicted the same paragraph and the
register row from the 2026-09-08 refresh, which retired the image
flag. The paragraph's earlier sentences already state both verdicts'
robustness, so nothing replaces it. The register row's outcome text was
updated with the PI-approved draft and re-signed.

### 2026-10-12 (later) — A-09 re-derived on the audited cost basis (PI rulings D16 and D61 (4))

**Refresh trigger**: PI ruling D11 made the register's `cost_usd` the
audited basis, and D16 (WP7 of
`planning/cost-accounting-fix-plan-2026-09-21.md`, open since
2026-09-21) required the signed A-09 to be re-derived on it; the D57 (4)
Phase 3 re-score found 18 cost fields that no longer reproduce
(`reports/s163-agent-records/d57-4-rescore-s3-deltas.md` § Stopped
lines). PI ruling D61 (4): re-derive, keep the registered verdict, report
the matched-configuration comparison as it stands, and state beside the
cost figures, before re-signing, that the cost gap is not like-for-like.
`scripts/h6_registered_analyses.py` gained `like_for_like_costs` (it
re-prices each pass's recorded tokens at the served tier, halting unless
that reproduces the audited `cost_usd`, then at the standard tier with
and without thought tokens) and `cost_caveat_statement`, with tier-1
tests. The artefact was regenerated on sapphire in two independent
runs, byte-identical apart from `generated_at`.

**Before → after** (`a09_cost_gate.json`: the 18 cost leaves, the 6 F1
leaves D50 moves, and the new caveat blocks):

| Quantity | Before (2026-09-08, estimate basis) | After (audited, D11; F1 on the D50 scorer) |
|---|---|---|
| Pro cost per pass, text / image | $1.85 / $15.74 | $0.93 (flex) / $2.98 (standard) |
| Flash comparator cost per pass, text / image | $0.60 / $3.97 | $6.62 / $4.49 (standard, with thinking) |
| Flash N = 3 best F1, text / image | 0.5748 / 0.5854 | 0.5764 / 0.5873 |
| Matched text: F1 ratio, cost ratio, limb 1 | 1.40, 1.03, fires | 1.40, 0.05, does not fire |
| Matched image: F1 ratio, cost ratio, limb 1 | 1.14, 1.32, does not fire | 1.13, 0.22, does not fire |
| Frontier, Pro single-pass text: cost ratio vs min6 / min11 | 0.76 / 0.46 | 0.38 / 0.23 |
| Frontier, Pro text union: cost ratio vs min6 / min11 | 2.29 / 1.39 | 1.14 / 0.69 |
| Frontier, Pro text union: F1 ratio vs min6 / min11 | 0.979 / 0.974 | 0.982 / 0.976 |
| Frontier, Pro image single pass: cost ratio vs min6 / min11 | 6.48 / 3.93 | 1.23 / 0.75 |
| Frontier, Pro image union: cost ratio vs min6 / min11 | 19.43 / 11.80 | 3.68 / 2.24 |

**Correction found on re-derivation**: the frontier paragraph said that
no Pro point was within 0.02 F1 of a frontier point and none reached
50 % of a frontier cost. Both were already untrue of the 2026-09-08
artefact: the text union was 0.0182 F1 from min6 (its
`f1_comparable_within_0.02` was true), and single-pass text was at 46 %
of min11's cost. Neither moved a limb, because the union cost 2.29
times min6 and single-pass text gave up 0.0790 F1. The paragraph now
gives the limbs' actual reasons. The register row's outcome text
repeats the "76 % of min6's cost" case and is left for the PI.

**What did NOT change**: the registered verdict (CLOSED); limbs 1 and 2
never fire against the frontier; Pro's F1s (0.8045 text, 0.6658
image); the frontier rungs; the image matched-configuration limb; the
coverage disclosure. The register row `h6-a09-cost-gate` is set to
`re-sign-pending` with a dated signature note in the D9 pattern; its
outcome text (which quotes cost ratio 1.03, a firing text limb, and
1.32) is unchanged, for the PI's wording. The re-run section's item 2
gains a pointer to the A-06 note.

### 2026-10-12 — A-06 regenerated: permutation p with BH; the thinking finding recorded (PI ruling D61 (3) and (4))

**Refresh trigger**: the shared helper `paired_bootstrap` took the D42
permutation p on 2026-10-05 (`3c3023f51`), and `a06_decision_rule.json`
(2026-09-08) was never regenerated, so the D57 (4) Phase 3 re-score found
it still carrying the bootstrap p fields
(`reports/s163-agent-records/d57-4-rescore-s3-deltas.md` § Stopped lines).
PI ruling D61 (3), which records it as the only file under `results/`
still carrying `p_at_floor`: regenerate on today's script and add BH
across the four registered contrasts. PI ruling D61 (4) adds the thinking finding.
`scripts/h6_registered_analyses.py` gained `apply_bh_to_factor_t` with
tier-1 tests; the artefact was regenerated on sapphire in two
independent runs, byte-identical apart from `generated_at`.

**Before → after** (`a06_decision_rule.json`, the 28 leaves the Phase 3
diff predicted, plus the BH fields):

| Field, per contrast (text HIGH / text MEDIUM / image HIGH / image MEDIUM) | Before | After |
|---|---|---|
| `p_value` | 0.001 / 0.001 / 0.001 / 0.001 (bootstrap floor) | 0 / 0.0019 / 0 / 0.0002 (permutation) |
| `p_at_floor`, `prop_gt_zero`, `prop_le_zero` | present | removed (bootstrap p retired) |
| `p_method`, `n_permutations`, `n_discordant_tiles` | absent | permutation test, 10,000, 175 / 147 / 218 / 192 |
| `p_bh_adjusted` (new) | absent | 0 / 0.0019 / 0 / 0.000267 |

**What did NOT change**: every F1, delta, and delta interval; all four
rule verdicts (fires); the thinking-context deltas and intervals; the
estimator-reconciliation gate. The register row `h6-a06-decision-rule`
quotes no p-value, so none of its numbers moved and its signature is
not lapsed by this regeneration; whether the D61 (4) finding bears on
its outcome text ("TEMPERATURE IS THE DRIVER") is for the PI.
`a07_voting_thresholds.json`, which the same script writes, was not
committed: under today's scorer (D50) it moves 25 leaves, a separate
Phase 5 item. The two consensus `voting_summary.json` files under
`outputs/h11/n1-pro-rerun-384/` gain only the `pass_provenance_schema`
tag `merge_passes` has written since `ac7d393c7`; their counts and the
consensus GeoJSON files are unchanged.

### 2026-09-08 (later, S151) — A-07's retired-flag prose corrected: 0.0015, not 0.0016

**Trigger**: PI instruction (2026-09-08). The A-07 artefact's retired-flag
sentence gave the pre-recovery image margin as 0.0016 where the archived
pre-recovery artefact's field (0.001545) and this document say 0.0015. The
literal lived in `scripts/h6_registered_analyses.py`; corrected there and the
three artefacts regenerated on sapphire from the committed script. **Before →
after**: the one word; the three `generated_at` stamps. **What did not
change**: every figure, verdict, and gate in A-06, A-07, and A-09; the
register rows and their 2026-09-08T01:53:31Z signatures (the PI may wish to
re-sign A-07, since its artefact post-dates the signature by this prose
correction).

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
