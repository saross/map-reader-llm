# Discussion — seed paragraphs

> **Last revised**: 2026-06-13 (original publication, Session 114). See
> [§ Changelog](#changelog) for revision history.

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

---

## Changelog

### 2026-06-13 — Original publication

Seeds 1–3 drafted from the Session-113 closing chain (Obs 366 § 2;
Obs 367; Obs 368 / `results/gtfree-selection/gtfree-selection-findings.md`
§ 6) per the S114 continuity plan, item 3. Seed 4 added from the
Session-114 metric-board refresh (commit `0a05a4ef9`), clearly marked
as outside the S113 plan.
