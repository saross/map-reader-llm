# Discussion — seed paragraphs

> **Last revised**: 2026-08-16 (Seeds 6–7 added — the plateau rule
> and its decision tree; the preregistration retrospective from the
> D16 rider). See [§ Changelog](#changelog) for revision history.

**Status**: seed paragraphs only — draft prose for the Discussion
section, capturing the three argument lines that fell out of Session
113's closing chain (Obs 366–368) plus one Session-114 addendum. Not a
Discussion outline; ordering and integration with the conventional
Discussion moves (relation to prior literature, limitations,
implications) come later. Companion: `docs/paper/results-draft.md`
(§§ R8–R9 carry the measured results these seeds interpret).

---

## Seed 1. Instrument resolution is about representativeness before size

The study's central methodological lesson is easily misread as "the
calibration corpus was too small". The power arithmetic does say that —
resolving the decisions the Gold-Standard (GS) instrument got wrong
would have needed ~10–20 sheets (~900–1,900 mounds) per decision axis at
80 % power, versus the four sheets used (Obs 366 § 2) — but the
arithmetic is the *less* important half of the lesson. Two of the
calibration failures were not power failures at all: the vote-threshold
direction genuinely *reversed* between the curated GS sheets and the
deployment corpus, and the minimal-vs-HIGH thinking tie was genuinely
real on the GS sheets. A larger sample of the *same* sheets would have
converged, with growing confidence, on the wrong answer. The binding
constraint was that the curated sheets were not drawn from the
deployment population — representativeness, then size. This inverts the
usual instinct for reference-data investment: before buying more
annotation, buy *sampling* — and if representative sampling is
unaffordable (it usually is, since here it meant curating up to roughly
a third of the deployment corpus in advance), accept that
characterisation-instrument ties are bounded ignorance at the
instrument's resolution (±0.03 F1 here), and plan deployment-side
mitigation rather than calibration-side certainty. The mitigation
heuristics are cheap: deploy recall-permissive on plateaus, and budget
for a deployment-side threshold sweep (Obs 358; §§ R6–R7).

## Seed 2. Deploy-and-evaluate is cheaper than the reference data it replaces

The economics of the previous point are stark enough to be the
recommendation. A calibration reference able to ground the configuration
decisions would have cost weeks of expert or student curation; the
deploy-and-evaluate alternative — carry the entire end-of-calibration
tie-set to deployment and let the deployment corpus itself resolve the
ties — prices at ~$733 audited flex for the 8,541-tile corpus (Obs 367).
Two structural properties of the architecture make this affordable: the
threshold axis is free post hoc (verify one permissive band, sweep vote
and probability thresholds on recorded verifier probabilities), and
pass-count variants nest (a 10-pass campaign contains its 5-pass rung),
so the tie-set collapses to four proposer pools (~25 passes). The study
itself is the existence proof: its five deployment campaigns, run
incrementally without a covering design in mind, summed to ≈ $722
(token-load audit § 6) — the minimal covering design, discovered
retrospectively. For a funded survey project the resolution campaign is
a line item, not a work package; the expensive thing it replaces is not
compute but human annotation. A prospective version would simply specify
the four pools up front and run them in parallel. This also reframes
what "calibration" buys: not the deployment decision itself, but the
short-list of configurations worth deploying — the tie-set *is* the
calibration product.

## Seed 3. The GT-free protocol is a falsifiable proposal, not a validated method

Section R9's leave-one-family-out result (ρ = +0.881; top pick a true
Tier-1 cell) completes the production protocol — deploy, rank GT-free,
tie-break by cost — and converts the study's contribution from
"architecture and configuration trade-space characterised against ground
truth" to "plus a serviceable selection diagnostic usable on production
discovery runs lacking it". The Discussion should claim exactly that
much and no more. The validation is a retrodiction: one corpus, one
symbol type, eight cells, four configuration families; the Spearman
rests on eight points; and the method's two known failure modes are
characterised but not stress-tested (the consensus must be permissive —
unanimity inverts the ranking; and the family structure must be
genuinely diverse — T03 and TH7 share a recipe and flatter each other's
pseudo-reference, while the image family contributes the most
independent signal, so a less diverse tie-set would weaken the
evaluator). The honest framing is a falsifiable proposal with a
pre-specified test: apply the four-step protocol, preregistered, to the
next discovery corpus, and report whether the GT-free pick lands in the
true top tier once reference data eventually exists. That framing is
also the stronger rhetorical position — the protocol's value does not
depend on this paper claiming generality it cannot yet have
(`results/gtfree-selection/gtfree-selection-findings.md` § 6).

## Seed 4 (S114 addendum). The tile-MCC counter-board now replicates across instruments

Flagged for consideration; not in the S113 plan. The Session-114 refresh
of the metric-led boards (`results/metric-leaderboards/`, membership
extended to the cells promoted to first-class on 2026-06-12) moved the
GS MCC crown from min11 (0.807) to a *single image pass plus Pro
verifier* (`verified-adv-image-baseline-pro-vf`, tile-MCC 0.889, F1@30
only 0.797), with image + verifier cells sweeping the MCC top ranks.
This replicates the pattern already on the Era-1 512 px board
(`era1-leaderboard`: verified-adv-image-t0.0 MCC 0.889, board-best,
mid F1) and at 55-map deployment (IM-k3: best tile-MCC 0.710, seventh
F1). The mechanism is now legible across all three instruments:
tile-level MCC is localisation-free, and the image modality's weakness
is localisation (75 m plateau, § R1), not tile-level detection — while
verification, not consensus volume, is what controls its false-positive
tiles. If the Discussion engages with metric choice for survey
applications (it should: § R7 lesson iii), this is the strongest
single piece of evidence that *the right pipeline depends on whether
the survey consumes coordinates or tiles* — a cheap two-call-per-tile
image + verifier stack is the best tile-prioritisation instrument in
the study while being nowhere near the F1 frontier.

**Statistical upgrade (same day)**: the deployment-scale leg of this
claim now carries permutation backing
(`results/metric-leaderboards/55map-mcc-tiering.{md,json}`, 10k
tile-swap on the MCC statistic + BH-FDR, gate 8/8 exact): **IM-k3 is
the sole Tier-1 cell on the MCC axis** — all seven of its pairwise
comparisons are significant, including against the F1 oracle T03-k3
(ΔMCC +0.020, BH p = 0.0056), and the BCa CIs are now on the board.
The image cell's MCC lead is a resolved statistical fact at 8,541
tiles, not a numerical ordering. Note the tile-level inversion of the
F1 board's tier structure: the F1 oracle drops to MCC Tier 2, and the
carry-forward sits in MCC Tier 3 with the uplift.

---

## Seed 5 (S125 addendum). Tile-MCC as the basis for semi-automated extraction — and temperature/pool-size cost equivalences

Flagged for consideration (PI-raised, 2026-08-03; grew out of the
E72-remediation matched-temperature analysis,
`results/e43-matched-temperature/findings.md`). Two connected points:

1. **Tile-level MCC is the natural metric for a semi-supervised
   workflow** — "show me the tiles with mounds and I'll pinpoint the
   mounds manually." Object-level F1 rewards precise localisation; the
   tile-MCC counter-board (Seed 4) rewards reliable tile
   discrimination, which is exactly what a human-in-the-loop
   pinpointing pass consumes. The paired-MCC ladder shows temperature
   trades sensitivity for specificity at tile level (higher T → fewer
   false-positive tiles at flat sensitivity, replicating Obs 274 on a
   second era/tile size/model), so configuration choice differs by
   intended workflow: fully-automated extraction optimises object-F1;
   semi-automated triage optimises tile-MCC. A follow-on paper could
   compare direct feature detection against tile-triage-plus-human
   pinpointing — the planned pinpoint-correction app for the student
   map set's flawed positions could be repurposed as the instrument.
2. **Cost-equivalent configurations belong in the Pareto story**: the
   matched ladder suggests T=1.0 at N=5 meets or beats T=0.7 at N=10
   on both F1 and tile-MCC at half the proposer passes (landed:
   `results/e43-matched-temperature/findings.md` § 13 — vs T=0.7/N=30
   an F1 dead heat at 5.5× the spend; non-inferiority framing, ±0.038
   null intervals). If it holds, practitioners choosing
   configurations under budget constraints need the
   temperature-vs-pool-size trade made explicit, not just the
   per-configuration Pareto frontier.

## Seed 6 (S133 addendum). The plateau rule: what transfers from a small calibration corpus, what does not, and the decision tree that falls out

Drafted from the Session-133 D13 settlement dialogue (PI-endorsed
framing, 2026-08-16); complements Seed 1 (representativeness before
size) with the post-standardisation decomposition and a practitioner
recipe. Anchors: the S132 standardised boards
(`results/55maps-standardised-ref-2026-08-14/consolidated-standardised.csv`),
Obs 347 (GS-plateau heuristics), Obs 358 (threshold-transfer
failure), Obs 362 (resolving power / the reversal), Obs 368 + Seed 3
(GT-free selection), Obs 409 (the oracle-margin collapse), E56.

**The optimistic half, stated precisely.** Everything *structural*
that the calibration corpus resolved with significance transferred to
deployment intact: architecture, model, modality, thinking level at
single pass, and — sharpest of all — temperature, where post-hoc
re-selection on the deployment board buys +0.0006 at p = 0.857. On
the standardised reference the entire measured deployment gap
(carry-forward TH7-k4 0.8169 → Tier-1 set ≈ 0.839, +0.0224) is
recovered almost wholly by moving one scalar dial on the *carried*
configuration: relaxing the vote threshold from 4-of-5 to 3-of-5
recovers +0.0218 of it. The gap is threshold-transfer failure, not a
better configuration the calibration missed.

**Why the dial moves.** The F1-optimal vote threshold is not a
property of the configuration; it is a property of the encounter
between pipeline and corpus — specifically the prevalence of marginal
mounds that only a minority of passes propose. A single-region
calibration corpus has one difficulty mix; 55 diverse sheets have a
longer marginal tail, so the permissive setting wins more, and the
verifier (which exists to absorb precision costs) was being under-fed
at 4-of-5.

**The failure was flagged in advance by its own instrument.** The GS
did not confidently choose 4-of-5 and get overturned; it reported a
3-of-5 ≈ 4-of-5 plateau — i.e. it announced that it could not resolve
the choice — and the carried value was a peak-pick on noise. Both
deployment surprises this project recorded are instances of one rule:
**nothing the calibration corpus confidently concluded was
overturned; its ties and plateaus are the entire risk surface** (the
threshold plateau, reversed at +0.022; the min-vs-HIGH tie inside
±0.03, reversed at −0.030, Obs 362).

**The decision tree (preliminary).** For calibrate-small,
deploy-large workflows:

1. **Where the calibration corpus resolves a choice with
   significance → carry it.** Nothing in this project's record
   contradicts that move.
2. **Where it shows a tie or plateau → treat the choice as
   unresolved.** Do not peak-pick. Tie-break toward the **cheaper**
   option (the Obs 357 meta-rule) or the **more permissive** one
   (which keeps recall available for the verifier to refine) — PI
   tie-breakers, 2026-08-16.
3. **Budget a dial re-tune at deployment — it is cheap by
   construction.** Re-thresholding needs no new proposer passes: the
   existing passes re-merge at the new threshold (a $0 recalculation)
   and only the changed candidate pool needs a single verifier run.
   The expensive layer (proposer passes) is untouched.
4. **Where no reference data exists at deployment → the GT-free
   protocol is the preliminary branch.** LOFO permissive-consensus
   ranking reproduced the true board at ρ = +0.881 over cells that
   mix thresholds (Obs 368), so GT-free dial re-selection is at least
   demonstrated in retrodiction — advanced here as a falsifiable
   proposal per Seed 3's framing, not a validated method.

**The caution that keeps the optimism honest.** Relative choices
transfer; absolute performance does not — every configuration's F1
degrades on transfer, unequally (the R6/R7 transfer table). The
calibration corpus predicts *which* configuration, not *how well* it
will do. And per Seed 1, a larger sample of the same unrepresentative
sheets would have converged confidently on the wrong dial setting —
the plateau rule is about resolving power, which representativeness
gates before size does.

## Seed 7 (S133 addendum). Preregistration retrospective: what worked, what over-baked, and the micro-registration alternative

Planned Discussion space per the D16 settlement rider (PI,
2026-08-16). The PI's thesis: LLM support makes routine
preregistration feasible, but may also invite
over-planning/over-registration — and this project somewhat
over-baked its prereg, requiring many amendments.

**The PI's fuller articulation (2026-08-17, session close)** — this
was his first AI-assisted preregistration *and*, because of that
assistance, his first **comprehensive** one: the comprehensiveness
that enabled the over-bake was itself an affordance of the tooling.
Two claims to keep distinct in drafting: (i) **the process was
valuable even where the artefact failed** — going through the
registration and articulating the plan in detail genuinely clarified
his thinking about the project ("plans are worthless, planning is
everything"); (ii) **the artefact was too prescriptive, front-loaded,
'waterfall'-like, and complex** — it (a) contained omissions,
contradictions, and errors (receipts in the D17 inventory: the
exploratory-label propagation, the unregistered inference method,
the unexecuted strands), and (b) did not survive contact with
reality. Overall verdict: preregistration was worth it, and the
paper should say both halves plainly. The waterfall framing also
gives the micro-registration recipe below its natural name: it is
the *iterative/incremental* counterpart — register less up front,
register better at each analysis boundary — so the retrospective's
arc is waterfall → agile, told from the project's own record.

The S133 dialogue's assessment, for drafting:

**The over-bake is real, with receipts.** Fifteen registered
hypotheses, of which roughly a third never executed (H6, H13, H14,
H15, plus H2 Condition C) — each now a disclosure obligation a
reviewer checking the OSF record will look for; an errata register
in the seventies; conditional escalation triggers registered at an
operational specificity the project outgrew (E60: the trigger fired
only on an unregistered corpus, within noise); a registered
inference recipe that did not survive contact with the analysis
(E45: the permutation machinery used everywhere was never
registered).

**Two counterweights keep the retrospective honest.** First, the
amendment count is a biased measure of over-registration: an
unregistered project would have drifted identically, invisibly. The
counterfactual is not "fewer deviations" but "the same deviations,
unrecorded" — much of the errata volume is the honesty discipline
*working*, and the register is itself a contribution. Second, the
registration delivered exactly the goods it promises: {H2, H3, H7}
survive the registered family FDR as confirmatory claims; H2's
*falsified directional prediction* is more credible because it was
registered; CMT-0106's outcome-blind execution resolved an
outcome-material fork to the conservative branch.

**The sharper diagnosis is grain, not volume.** What aged badly was
registration of specific operational bindings — fixed corpora,
enumerated escalation temperatures, fifteen hypotheses including
speculative strands, a specific bootstrap recipe. What aged well was
design-level and procedural commitment — the factorial structure,
hypothesis directions, the FDR family rule. The transferable lesson:
register decision *rules* and *procedures* plus a handful of sharp
confirmatory hypotheses; leave operational parameters to disclosed,
rule-governed selection (cf. Seed 6's plateau rule, which is such a
rule).

**The LLM-support point cuts both ways — and that is the Discussion
claim.** LLM assistance collapsed the drafting cost of registration,
which is precisely what enabled the fifteen-hypothesis over-bake
(ambition became cheap to enumerate). But it equally collapsed the
cost of the compensating machinery: the errata register, drift
audits, blind verification, and above all **just-in-time
micro-registration** — the family-FDR registration was authored,
PI-ruled, and computed within days, with CMT-0106 run outcome-blind
under it. The forward-looking recipe the project backed into in its
second half: a leaner upfront registration (design + few
confirmatory hypotheses + procedural rules) combined with
LLM-supported micro-registrations at each analysis boundary —
shrinking the unit of preregistration from *the project* to *the
analysis*. The retrospective can present this as the resolution of
its own first-half over-bake, evidenced from the paper's own record.

## Changelog

### 2026-08-17 — Seed 7 augmented with the PI's fuller articulation

Session-close addendum: first-comprehensive-because-AI-assisted; the
process-vs-artefact distinction (planning clarified thinking; the
waterfall artefact did not survive contact with reality, with
omissions/contradictions/errors receipted in the D17 inventory);
the waterfall → agile arc naming the micro-registration recipe.

### 2026-08-16 — Seed 7 added (S133 D16-settlement addendum)

Seed 7 drafts the preregistration retrospective planned under the
D16 rider: the PI's over-registration thesis with receipts, the two
counterweights (amendment count as biased measure; the confirmatory
payoff delivered), the grain-not-volume diagnosis, and the
micro-registration recipe as the both-ways LLM-support claim.

### 2026-08-16 — Seed 6 added (S133 D13-settlement addendum)

Seed 6 externalises the threshold-transfer explanation from the
Session-133 D13 dialogue: the plateau rule, the standardised-reference
decomposition (gap ≈ pure threshold axis; temperature +0.0006), and
the four-step decision tree with the PI's tie-breakers (cheaper /
more permissive), the cheap-re-tune cost argument (recalculation +
one verifier run), and the GT-free protocol as a preliminary branch.

### 2026-08-03 — Seed 5 added (S125 E72-remediation addendum)

Seed 5 drafted from the PI's 2026-08-03 direction during the E72
matched-temperature follow-ups: tile-MCC as the semi-automated
extraction metric (with the app-repurposing idea) and the
cost-equivalence framing for the Pareto discussion. Cross-cell paired
tests in flight at drafting; the seed cites where they land.

### 2026-06-13 (later) — Seed 4 statistical upgrade

**Refresh trigger**: Shawn requested the alternate-metric permutation
with CIs. `scripts/mcc_tiering_55map.py` (zbook, $0; gate 8/8 exact)
tiers the 55-map board on the MCC statistic: 20/28 pairs significant,
five tiers, **IM-k3 sole Tier 1** (significant against every other
cell, incl. the F1 oracle at BH p = 0.0056). Seed 4's claim upgrades
from "best tile-MCC numerically" to "statistically clear sole leader
on the tile axis"; BCa MCC CIs (already on disk in the Track-2
summaries) now render on the metric board.

### 2026-06-13 — Original publication

Seeds 1–3 drafted from the Session-113 closing chain (Obs 366 § 2;
Obs 367; Obs 368 / `results/gtfree-selection/gtfree-selection-findings.md`
§ 6) per the S114 continuity plan, item 3. Seed 4 added from the
Session-114 metric-board refresh (commit `0a05a4ef9`), clearly marked
as outside the S113 plan.
