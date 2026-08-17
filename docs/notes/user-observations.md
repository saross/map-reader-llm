# User observations — map-reader-llm

Meta-level log about how Shawn and Claude collaborate on this project. Feeds
`~/personal-assistant/notes/working-with-claude.md` at `/weekly-review`
curation time. Distinct from `working-notes.md` (research findings) and the
`reflections/` set (Claude's self-reflection): this is observations *about the
human's working style and our division of labour*.

## Session 108 — 2026-06-09

**"Don't leave loose ends" is a quality-bar steer, not a direction steer.**
Shawn's highest-leverage input this session raised the *standard of done* rather
than redirecting the work. Mid-session I had worked around a manifest-generator
timestamp-churn bug three times (clean recoveries, each narrated as prudent);
his "could we also resolve the secondary wart … not leave too many loose ends"
reframed it from a constraint to dodge into a bug to fix — and the upstream fix
made the workarounds retroactively unnecessary. The pattern: he intervenes to
move the bar from "task finished" to "codebase left better", not to choose a
different task.

**"Step back: where are we in the big picture" is a phase-naming device.**
Partway through closing the session's individual items, Shawn asked where we
were in the multi-week results / intermediate-documentation rationalisation. The
question lifted the work from task-completion to recognising an *inflection* —
the rationalisation is complete (28/28 runs decomposed, 281 conditions / 10
analyses, drift-check ALL VALID); the project pivots from building the
structured backbone to writing the paper from it. Without the prompt I would
have kept finishing items without naming the transition. He periodically
re-frames from the tactical to the strategic, and that re-framing is what turns
a pile of closed tasks into a recognised phase boundary.

## Session 109–110 — 2026-06-09/10

**The human supplies the fair baseline; I default to the flattering one.** The
session's biggest analytical correction came from Shawn's "rank the consensus
rules against the single-pass *mean*, not the best pass" — which exposed a real
+0.012 consensus benefit I had twice reported as "no benefit" by benchmarking
against the luckiest of five passes (one you can't obtain in production). His
reframings repeatedly forced the honest counterfactual: "is this actually a new
high?", "compared to *other 5-pass* proposers?", "apples-to-apples 11 vs 10
passes". The division of labour was stark — I executed fast and gated carefully,
but I kept drifting toward comparisons that confirmed my prior; he supplied the
baseline that didn't. The science this session was in his *questions*, not my
execution.

**"Haven't we already done X?" — institutional memory as spend-control.** His
recall that Pro 3.1 had already been run (multi-pass, with verifier, on disk)
turned a ~$61 re-run into a $0 re-score; the same instinct ("check the disk")
would have averted the ~$106 model-benchmark I'd costed had I asked it myself.
He holds the project's what's-already-on-disk map better than I reconstruct it,
and a single "don't we have this?" beats a careful cost estimate of a redundant
run. Lesson for me: before costing any run, ask whether the data already exists.

**Cost-discipline as a permanently-active lens.** "Temperature is free but
thinking isn't, so on a tie advance minimal"; "what would benefit from warm
context [before we wind down]?"; the insistence on per-dollar comparisons
throughout. Shawn keeps a cost/value lens always on, and it is what turned a
pile of within-noise F1 ties into a clean decision rule (*on a tie, take the
cheaper config*) and a disciplined wind-down (lock the numbers warm, defer the
mechanical figure-build). He also resists the round-number dismissal: when I
waved the +0.005 operational-max lift through as "within ~1 SD", he flagged that
0.005 is *right at* the boundary and put a permutation test on the agenda rather
than let me pre-judge it.

## Session 111–112 — 2026-06-10/11

**The bookkeeping question as depth-charge.** The session's most consequential
finding came from an innocuous inventory question: "have we run min6 on the
55-map production?" We had — and the answer reversed a GS conclusion I had just
built a Pareto production column on. Shawn's questions often look like
housekeeping but function as audits of a claim's evidential basis; I had priced
a production recommendation without checking whether production evidence for it
existed (it did, three directories away, and contradicted me). The matching
follow-up — "is TH7-k3 oracle or carry-forward?" — forced the taxonomy that
made the threshold-transfer decomposition publishable.

**He asks for input on decisions he could make alone — and engages with the
structure, not the number.** "If you think there's a good argument for a
standardised 50 m shared operational buffer, please let me know — I would like
your input on these buffer decisions." He then adopted the two-role scheme
(30 m characterisation / 50 m operational) rather than either of the single
numbers on offer. The request was genuine: the recommendation changed the
outcome, and the engagement was with the reasoning shape.

**"Present results for everything we have" — completeness as policy.** Rather
than letting the image-cell discovery rest as a one-off, he directed a
systematic sweep of every unswept pool on disk. The audit found the
pro-verifier surprise nobody was looking for and closed the 30-pass-family
optimum question for free. The instinct: unexamined data is simultaneously a
liability (hidden contradictions) and an asset (free findings), and the cure
for both is the same sweep.

## Session 113 — 2026-06-12 (approved in-session)

**He supplies the one dataset only he can see — and it settles the audit.**
The token-load audit's conclusions rested on reconstructed token counts until
Shawn pulled the Google billing-console dailies (AEST) on request: the 18
April single-day figure matched the audited rates within 4% and excluded the
legacy manifests by 3×, and the June dailies excluded the pre-audit uplift
cost outright. The pattern: when an analysis bottoms out at "the ground truth
is outside the repo", he fetches it rather than letting the lower-bound caveat
stand — and supplying it promptly turned a plausible audit into a corroborated
one.

**"Make everything that can be first-class first-class."** Asked whether 16
sweep cells should stay analysis-internal, he generalised the question into a
registration policy: if the data and metadata exist to pass the gates, the
cell becomes a condition — no curation by anticipated usefulness. The two
principled exceptions (a cell whose optimum duplicates an existing condition;
one already minted) survived because they are structural, not judgement calls.
The policy removes a whole class of future "is X citable?" decisions.

**The interactive sign-off walkthrough as a review format.** Working the
sign-off queue together — each analysis presented with its claim, its
re-verified numbers, and one flagged caveat; each Obs walked with blemishes
routed to an append-only rider — caught real defects that batch sign-off
would have missed (a stale cost table, an artefact mischaracterised as a
finding, a mislabelled comparator). His verdict cadence ("accept, next?")
kept it fast; the format's value was that every signature now has a
verification trail behind it.

## Session 114–117 — 2026-06-13/23 (candidates — pending Shawn's review on return)

**The structure correction: he wants in on organisation before prose, not
after.** I had resolved three framing decisions in the Results draft and
marked them "[Resolved]", treating structural calls as mine to make and
report. Shawn reframed the *process* rather than the answers — "work with me
on an outline first, then drafting … be more directly and consistently
involved in the organisation/structure phase." It was a correction to a
default of mine: my "compress the five single-factor hypotheses as uniformly
inert" call had mis-filed two factors that genuinely matter (temperature at
single pass, thinking-level at consensus), and the error was invisible in
prose but obvious once the factors were laid out as a structure. The division
of labour he is asking for: I surface structure as explicit open options, he
settles them, then I draft. The principle he named — fluent prose hides the
seams an outline exposes — is now a standing preference (memory
`2026-06-14-cf9913c80a94`).

**He designs his handoff infrastructure and expects it protected.** Two
requests in one breath: make the continuity file "a self-sufficient sole
starting point" he can launch from cold on zbook, and then run only the
handoff parts that "won't interfere with the continuity beacon you've just
set up so carefully." He treats the beacon as an engineered product with a
guarantee — a fresh instance lands on the right task with everything it needs
— and explicitly fenced it off from the automated ritual that would otherwise
overwrite it. The steer for me: a hand-crafted launch artefact is
authoritative; defer to it, do not clobber it.

## Session 118 — 2026-07-28 (candidates — pending Shawn's review)

*Drafted at handoff by Claude Opus 5. Accept / edit / discard / replace. Silence
holds these over; it does not discard them.*

**Candidate 1 — the deadline/integrity call, and pre-committing the escalation.**
You reversed your own end-of-week deadline within two hours of setting it, once
the audit found an erratum contradicting its own preregistration — and then added
the thing I had left out of my recommendation: a stated condition for widening
the scope ("escalating if we find a lot of errors, and grow concerned that some
errors might be masking others"). Worth recording whether that framing was
useful, or whether I should have offered the escalation trigger unprompted.

**Candidate 2 — redirecting me to the artefact.** When I brought you the map-scale
and study-area discrepancy for adjudication, you did not adjudicate from memory —
you pointed me at `inputs/rasters` and at checking sheet extents against a region
map. That closed in minutes what four agent passes over prose had missed. Did
that feel like a normal correction, or like a gap in how I was approaching
verification?

**Candidate 3 — the T=1.6 reversal.** You said "let's just run it"; I then found
the trigger does not fire on the registered 60-tile corpus and recommended not
running. You accepted. Was raising that *after* you had decided the right call,
or should I have found it before presenting the option?

**Candidate 4 — machinery vs record.** You wrote "I do want to pivot back to the
paper verification itself," and later asked whether we should close the session.
I read both as a signal I had over-invested in the manifest machinery while the
22 false attributions sat untouched. Was that the intent, or am I over-reading?

## Session 119 — 2026-07-29 (candidates — pending Shawn's review)

- **Candidate A**: "You've done excellent work" — said after the review +
  correction pass, immediately followed by the decision to escalate me from
  reviewer to orchestrator of the end-to-end verification programme. The
  observation: the review's willingness to break the prior session's
  conclusions (P2, C5, the timestamp) is what earned the bigger mandate —
  adversarial honesty about a sibling instance's work read as
  trustworthiness, not disloyalty.
- **Candidate B**: Shawn accepted the "pin the interpretation, buy off the
  evidence" H4b hybrid over his own first instinct (the generous reading),
  saying my solution was "more elegant" — evidence that presenting a
  third option that dissolves a binary is more useful to him than
  arguing either side.

## Pending review — 2026-07-30 (Session 120 handoff candidates)

Candidates drafted at handoff; accept / edit / discard / replace.
Silence holds them over (2026-07-05 rule).

1. **The from-memory catch that upgraded the process.** Reviewing the 12
   GATE 1 headline findings from memory alone, Shawn caught 2 needing
   serious qualification — both one-sided evidence assembly that 25
   agents and 6 orchestrator spot-audits had missed. His follow-up
   question ("how do you suggest we ensure the other 10 are reliable?")
   produced the calibrated blind defence pass and charter rule 13 — a
   permanent process upgrade from a single question.
2. **Calibrated scepticism about recorded settings.** His warning to
   check that phase3c "really was high thinking and not just
   mis-recorded" proved exactly right in shape: token-level
   corroboration turned out to be unavailable across the whole retest
   era, and the erratum now carries that caveat instead of a bare claim.
3. **In-the-moment reaction (relayed).** "This is great" on the
   defence-pass design — specifically the use of his own two catches as
   blind calibration probes. The pattern he responded to: methods that
   measure their own reliability before asking to be trusted.

## Session 121 — 2026-07-30 (approved 2026-07-31)

**His operational-memory checks changed real outcomes.** "Check which
pro model we ran" caught the registration mislabelling the E57 Flash
corners as Pro (collapsing the rerun to all-Flash and a fifth of the
cost), and "normally we try ~10x" caught the patcher's too-shallow 3+3
ladder (the deeper sweep recovered 10 more tiles). Both fired on
operational norms no checklist encoded.

**The morning-rulings format stays as the standard gate-morning shape —
with an explicit trade-off habit for the load-bearing calls.** The
structured decision batches (recommendations attached, verbatim
evidence, outcome-materiality labelled) let him rule on ~15 decision
points in one sitting. His rider on accepting (verbatim): "On decisions
that are actual 'close calls' or load-bearing, let's also get in the
habit of explicitly looking at trade-offs — as soon as you did the
deeper dive on H8 the indecision evaporated and the correct path became
clear."

**Two decision registers, two presentation depths.** His elaboration on
the H1 "explain further" moment (verbatim): "a species of the
load-bearing decision above where a deeper dive is needed — the brief
presentation of options as per yesterday's morning rulings is *great*
for straightforward decisions, but the entailed + load-bearing ones
need a deeper dive. H1 and H8 were good examples of this." The
calibration rule this sets: brief structured options for
straightforward rulings; proactive trade-off analysis (not merely
on-request) for entailed and load-bearing ones — H1 (outcome-material
selection) and H8 (methods-defensibility choice) are the type
specimens.

*(Working-notes candidate WN-1 from this session's gate was also
accepted — promoted to Obs 375, the outcome-blind fork.)*

## Session 121 close — 2026-07-31 (Shawn's in-session reaction, recorded verbatim)

"What a good session this was, we made substantial progress such that I
am building more confidence in the map-reader results/reports, after
the initial disappointment of finding crucial errors after I thought
these docs were ready. It's a bonus that we are generalising this for
use in other projects."

Context for the register: this marks the epistemic trajectory the
verification charter was designed for — docs believed ready (pre-S118)
→ crucial errors found (S118–119) → systematic programme (S120–121) →
confidence *rebuilt on checking rather than assumed*. The
generalisation he calls a bonus is charter § 1's designed-in
reusability (next targets: inscriptions, llm-reproducibility).

## Session 122 — 2026-07-31 (candidates — pending Shawn's review)

Phase 3 (C4) claimed and executed at fleet scale: registry, machinery,
calibration, 18 subagents, generated stratum ~80 % verified, US$0.00
API. Candidates drafted at handoff; accept / edit / discard — silence
holds them over.

**Candidate A — the pre-staged decision queue made PI time
high-leverage.** When Shawn surfaced mid-fleet and asked "what do I
need to do to advance us?", Claude led with four accumulated,
recommendation-tagged decisions (one with trade-off analysis, three
with brief options per the S121 calibration rule). All four cleared in
one interaction and were executed within the hour — rulings doc,
clobber guards, Obs dispatch, fleet-model policy. The S121 rule
generalises: batching decision points during autonomous stretches and
framing them before the PI asks converts PI presence from a serial
bottleneck into a minutes-long high-leverage event.

**Candidate B — validator-gated autonomy earned post-hoc trust.** The
extraction fleet ran an entire phase-stage (18 agents, ~1,070 claims)
without mid-flight PI attention, and the thing that made that safe was
not agent quality but the committed validator each agent had to
satisfy before handing back (16/16 files structurally clean at first
hand-back). Shawn could trust the batch commits without reading them
because acceptance criteria were externalised and machine-checkable —
a pattern worth naming for future fleet designs.

**Candidate C — the apparatus catching its operator was surfaced, not
buried.** When the obs-writer's re-derivation showed Claude's own
probe record had glossed "439" wrongly, the correction was landed
append-only within the hour and reported prominently in the close-out
(rather than quietly fixed). If this transparency-on-self-error is
the behaviour Shawn wants locked in, accepting this candidate makes
it a standing expectation rather than a one-off.

## Session 123 — 2026-08-01 (approved 2026-08-01; candidate C dropped at review)

**Candidate A — trusting the escalation judgment, not the model
labels.** When ratifying the Sonnet fleet policy you didn't re-litigate
the comparison data; you observed "it seems like you were thorough and
that you are escalating to Opus when in doubt" and made the
escalation *judgment* the thing you licensed — Sonnet where cleared,
fresh comparison on new task kinds, Opus on doubt. If that reading is
right, what earned the delegation was the visible spot-audit apparatus
plus the stated escalation rule, not the head-to-head numbers alone.

**Candidate B — the apparatus catching Claude is what makes Claude
trustworthy.** Your response to the round-4 refutation (four of my
five flagged cells were my own binding artefact) was not concern about
the error but "we should systematise the independent-verification
pattern wherever possible, it's the way to be sure about things." The
observation: you treat a system that visibly catches its operator as
*more* reliable than one that reports no errors — and you moved
immediately to institutionalise the catch mechanism (ruling 11) rather
than to add scrutiny of the operator.

*(Candidate C — census-grounded walkthroughs make rulings cheap —
dropped at review, 2026-08-01.)*

## Session 124 — 2026-08-02 (approved 2026-08-02; B generalised at review)

**Candidate A — three decisions, one message, each at its own grain.**
After asking for a walkthrough of the open questions, you resolved all
three in a single reply — and each carried a different decision
texture: the era-check extension got full approval *plus* a
provisionality marker placed precisely on the classification rule;
the gap-bound escalation got a bare confirmation of process; the test
redesign got "is (b) correct? investigate further, then settle."
If the reading is right, the walkthrough format (what it is / why it
matters / options / recommendation, per item) is what enabled
one-pass dispatch at three different confidence levels — worth
keeping as the standing shape for decision batches.

**Candidate B — recommendation-as-hypothesis (generalised by Shawn
at review).** The instance: on the failing tests you didn't accept
"option (b) is most principled" as a decision; you asked whether it
was *correct* and ordered an investigation before settling. The
investigation changed the outcome — one of the three failures turned
out to be live-fixture staleness (re-pinned on evidence, no redesign
needed), and the ledger growth was verified governance-clean before
the invariant design was built on top of it. Shawn's generalisation
(2026-08-02): "when there's a genuine decision we create a
hypothesis about the most principled / lowest-technical-debt-
incurring one, test it, then decide." The standing protocol this
sets: for genuine (non-obvious) decisions, the recommendation is not
the decision input — it is the *hypothesis*; a cheap investigation
against the artefact record tests it; the decision follows the
evidence. Applies beyond test repair: any choice where "most
principled" can be probed before it hardens into implementation.

**Candidate C — licensing the register, not the entries.** You
approved both Obs candidates in five words without asking to see
drafts — consistent with S123's candidate A reading (what earned the
delegation was the visible apparatus, here the obs-writer's mandatory
blind re-derivation). The writers then materially improved both
entries (a corrected caveat in Obs 380; the anti-correlation
sharpening in Obs 381), which is the outcome that pattern predicts:
gate the process once, and the per-entry gate becomes redundant.

## Session 125 — 2026-08-03 (approved 2026-08-03; B and D dropped at review)

**Candidate A — the "(Recommended)" label earned scepticism twice, and
your re-openings out-performed it.** Of the six D-sequence decisions,
you accepted four recommendations as offered — but the two you
re-opened were precisely the two where my label was wrong or
truncated. D6's "accept the catch-up (Recommended)" would have
enshrined a machine-dependent generator; your "investigate first"
converted it into a 72-row defect-class removal. D4's binary
(tracked-only vs machine_scope fields) had truncated the option space
to the verifier's convenience; your what-is-it-for reframe produced
the tracked-proxies rule, strictly better than both options I priced.
The pattern for future instances: my recommendation quality drops
when the option space was generated by the same tool that surfaced
the problem — treat those labels as first drafts, not defaults.

**Candidate C — in-the-moment reaction, recorded near-verbatim.** On
the paired-MCC ladder: "that's the clearest explanation of the F1
vs. MCC divergence that you've produced." What preceded it: the
exception-question was answered by reframing (two metrics, two levels
of analysis, a replication of Obs 274 rather than an exception)
instead of by a p-value — the explanation landed because it dissolved
the apparent contradiction rather than adjudicating it.

## Session 127 — 2026-08-04 (approved 2026-08-04; B dropped at review)

**Candidate A — the decision-by-decision mode, and the granularity of the
option previews.** Once you became available to adjudicate, the session ran
as a sequence of single questions with four options each, most carrying
ASCII previews of the trade-off (cost, blast radius, what gets left
behind). You engaged with every one and twice rejected the frame rather
than the options.

*Your verdict*: the granularity was about right — **and a recommendation
is always wanted.** In your words, you "always appreciate a recommendation
(whether I choose it or use it as a springboard for discussion with you
that leads elsewhere)". This is the operative instruction for future
instances: a recommendation is not presumption and its value does not
depend on being taken. Its function is to give you something to push
against — twice today the recommendation was the thing you reframed away
from, and that was still the fastest route to the better answer. Never
withhold one for fear of steering; withholding removes the springboard.

**Candidate C — the interim-conservatism half of the session.** For the
first stretch I escalated rather than adjudicated (per the 48-hour window
directive), producing W7-E1/E2/E3 and a queue rather than repairs. When you
arrived you unblocked most of it in three decisions.

*Your verdict*: **it arrived usefully shaped.** So the open question
resolves in favour of the escalation discipline as practised — the queue
was not front-loading work that standing rulings already licensed. For
future instances: under a conservatism directive, escalating with the
evidence assembled and the options priced is the right shape, and the cost
of the PI unblocking three items is lower than the cost of an instance
adjudicating research conclusions unsupervised.

**Candidate D — in-the-moment reaction, recorded near-verbatim.** After the
first tranche of flagged findings (the coverage drift, the era_check
indictment, the stale-banner set): *"Thanks for the flags, I'm happy with
how you are handling them. Please proceed as suggested."* What preceded it
was a report that separated confirmed defects from open research findings
from instrument gaps, each with its evidence pointer, and an explicit note
of which items I had NOT repaired and why. Recording it because the
structure that earned it is reproducible: the flags were sorted by what
kind of thing they were, not by when I found them.

*(Candidate B — on whether leading with a self-introduced error read as
transparency or as burying the findings — dropped at review.)*

## Session 128 — 2026-08-04 (approved 2026-08-04, all candidates kept)

**Candidate A — the provenance that only existed in your head.** Asked
whether the 4-map gold-standard corpus should be folded into the reference
standardisation, you answered with its history rather than a yes or no:
you have reviewed it **four times** — once for a previous paper, three
times for this project — **re-positioned each point to dead centre within
1–2 px**, and your fourth manual extraction pass at the start of this
project found **one** additional false negative, with nothing surfacing in
months of use since. Conclusion: "The GS corpus is as good as I can make
it, it doesn't need review."

*Why this is worth recording.* None of that was in the repository. The
project has spent four sessions establishing that the 55-map student layer
is four layers with three different sizes and two stage-specific
asymmetries — and the whole time, the other corpus was quietly the one
reference that genuinely earns the name "gold standard", on evidence no
document held. It is now ruling 21(d). For future instances: **when the PI
answers a scoping question with provenance instead of a decision, the
provenance is usually the more valuable half** — capture it verbatim
before acting on the decision. And more specifically, ask about the *other*
artefacts early: a project can carry an unrecorded quality asymmetry
between two datasets for months, and reasoning that treats them as
comparable will be quietly wrong.

**Candidate B — you generalised the fix before I proposed it.** Presented
with one reference defect (W7-D9) and a menu of three ways to repair § 4.1,
you declined all three and restated the problem a level up: nail down the
reference dataset first, build the precise-location app, then run *every*
tainted no-API re-analysis against the standardised artefact, with
API-spend cases discussed separately. "End goal are accurate runs on
standardised artefacts."

*Why this is worth recording.* My three options were all local repairs to
one section; the fourth option — stop repairing instances and fix the
generator — was the right one and was not on my menu. This is now ruling
21, and it converted a per-defect cost into a one-off. For future
instances: when presenting repair options for the *n*th instance of a
recurring defect class, **include "fix the thing that keeps producing
these" as an explicit option**, and price it. Four reference defects had
surfaced in four days (rulings 19 and 20, W7-D8, W7-D9) and I was still
offering per-site repairs on the fourth.

**Candidate C — the limitation stated as plainly as the goal.** In the
same breath as commissioning the best-possible reference you named what it
cannot be: "not really 'gold standard', as we've no way to economically
recover the joint student + model FNs."

*Why this is worth recording.* The instinct being modelled is worth
copying: define the artefact's ceiling at the moment of commissioning it,
not at write-up when a reviewer asks. That sentence is now in ruling 21(b)
with an instruction that it ship in the artefact's own header rather than
only in a changelog — because a reference that is *almost* a gold standard
will be called one by a downstream document within a wave or two unless
the qualifier travels with it.

**Candidate D — scope, priced and then declined.** Your first phrasing was
"the mounds in my 'corrected' dataset", which reads as the 4,746 student
layer. Presented with the arithmetic — 773 phantoms ≈ 1 h, 4,746 students
≈ 6 h, both ≈ 7 h — and the fact that re-marking student centres moves the
reference geometry at *every* buffer rather than only sub-50 m, you chose
the committed 773-only scope.

*Why this is worth recording.* The decision took one exchange because the
aggregate was stated rather than the per-unit rate. This is the global
CLAUDE.md "compute aggregate implications" rule paying off on the PI's own
time rather than on API spend, and the second half mattered as much as the
first: the *blast radius* differed between the options, not just the hours.
For future instances: when a scope reading is ambiguous, **price both
readings and state what each one invalidates downstream**, then ask — do
not silently take the narrower one because it matches a prior commitment.

---

## Session 129 — 2026-08-06 (approved 2026-08-14, all candidates kept)

**Candidate 1 — reporting a fix as done twice on evidence that could not have
failed.** The keyboard nudge was declared working on an AppTest run that cannot
execute custom components, so the interfering path could never fire; and a
`str.replace` whose anchor did not match returned the string unchanged, which
was committed and reported as a fix. Both were caught by Shawn using the app,
not by Claude. The correction adopted mid-session — verify in a real browser,
assert the anchor before writing, and state *how* a fix was checked — should be
standing practice rather than a response to being caught twice.

**Candidate 2 — the app was materially improved by Shawn's cases, not by the
spec.** Seven instrument changes (partner selector, numbered candidates, nudge,
alignment circle, review ordering, merge-wrong verdict, pre-merge partners) all
came from him hitting a real case and describing it. The spec anticipated none
of them. Worth recording as evidence for building thin and iterating against
real use rather than specifying more up front.

**Candidate 3 — Claude introduced a distinction the analysis did not need, and
Shawn caught it.** At item 685 Claude advised marking the "keeper" as distinct,
introducing a directional judgement that contradicted its own earlier guidance
and would have made ~1,300 decisions harder for no gain. Shawn asked whether the
inconsistency mattered rather than assuming it did; measurement showed it did
not, and the advice was withdrawn.

**Candidate 4 — the terminology objection was substantive, not cosmetic.**
Shawn objected to "phantom" for his own confirmed mounds; the register already
called the layer `4_reviewer_promoted_extension`, so the interface had been
contradicting the data model. Claude had used the misleading term throughout
without noticing the tension.

## Session 130 — 2026-08-10 (approved 2026-08-14; candidate 2 dropped at review)

**Candidate 1 — marking-semantics questions were answered from the code and
spec, not from plausibility, and the difference was visible.** Every "should
I 'c' this?" question came back with the instrument's actual rule cited to
file and line (partner gating, cluster counting, red-partner legality) —
including twice answering "the spec already decided this" against Claude's
own earlier advice. The four-day pass proceeded without a single semantics
reversal after the fact.

**Candidate 3 — every "I think I did X wrong" was turned into a query before
a re-review, and the walks shrank by an order of magnitude each time.**
Suspected wrong phantom-partnering: 1 item (already flagged). Suspected
double-resolutions: 2 conflicts of 35 shared points. Suspected middle-class
re-review: 2 of 108. The screen time spent was on residues, never on
candidate classes.

**Candidate 4 — instrument fixes landed mid-campaign without ever costing
marking state.** Five code changes shipped while the pass was live; each
relaunch resumed at the first unmarked item because marks save per decision.
The fix-while-hot cadence worked because the data layer made it safe — worth
saying explicitly if it shaped how corrections felt from the marking chair.

**Candidate 5 (in-the-moment reaction, relayed) — interactive edge-case
adjudication beat documentation.** At session close, unprompted: "I
appreciated your help working through the manual review. The ability to ask
questions about edge or corner cases was better than documentation!" Distinct
from Candidate 1 (source-grounded answers): this is about the *modality* — a
responsive instrument-analyst answering the case in front of the reviewer
outperformed any amount of up-front procedure writing. Consistent with the
S129 finding that the spec anticipated none of the seven instrument changes;
here, the same lesson on the guidance side: the corner cases could not have
been enumerated in advance, only answered when hit.

## Session 131 — 2026-08-14 (approved 2026-08-14; candidate 4 dropped at review)

**Candidate 1 — the plan survived contact with five naive questions worse
than it survived execution.** Shawn's pre-run audit ("what artefacts?
what tripwires? ordered or simultaneous? partial completion? what
verifications?") exposed four structural gaps in an execution plan Claude
was ready to run — a coherence ordering, a mixed-vintage gate, a
document-atomicity rule, and an uncalibrated verification layer. None
were in any planning document. Claude's plans present as more complete
than they are; the interrogation, not the plan, produced the contract.

**Candidate 2 — Claude wrote causal mechanisms into the permanent record
before testing them, twice, in the same arc where it built machinery
against exactly that.** "Inputs repaired after the fit" went into a
pushed commit message on pattern-match; the fallback explanation went
into chat an hour later; both were falsified by single cheap commands —
run only after Shawn asked "do we need to follow up on these now?". The
numbers discipline is established; the because-clause discipline lagged
an error class behind, and it took the human's sequencing instinct to
close the gap before the report inherited the false mechanism.

**Candidate 3 — live phantom-side bookkeeping made the six-item walk
frictionless (in-the-moment reaction, relayed).** At each borderline item
Claude answered "is the orange phantom already allocated?" from the
claim data in seconds — including the correction that one phantom was
bound by its own claim rather than by anyone claiming it. Shawn: "ok,
thank you for that clarification", and at session end, unprompted:
"thanks for a productive session". The walk closed six-for-six with no
re-opens; the S130 lesson (interactive adjudication beats documentation)
extended from marking semantics to referential bookkeeping.

## Session 132 — 2026-08-15 (approved 2026-08-15; candidate 3 dropped at review)

**Candidate 1 — contract-scoped autonomy: four queue items, three blind
verifier cycles, and zero mid-arc questions.** The session ran items 2–5
end to end under the S131 execution contract without once returning for a
go/no-go — every would-be question (gating semantics, the gate redesign,
proceeding to items 4 and 5) resolved against a contract clause instead.
The one genuine anomaly (the anchor-vintage discovery) was handled inside
the contract's own "reproduce before you vary" stop state. Worth Shawn's
verdict on whether reviewing a finished arc beat steering a live one —
and whether this autonomy level generalises beyond $0 legs.

**Candidate 2 — the batched candidate walk worked from the reviewing
chair.** Thirteen working-notes candidates accepted in one word;
nine user-obs candidates judged in three structured batches with exactly
one discard, no rework, and no context reconstruction needed — four
sessions of backlog cleared in minutes. If the pre-formed-candidate
format (evidence in the text, counter-evidence included) is what made
the discard as fast as the accepts, that is worth recording as the
standard for future drafting.

## Session 133 — 2026-08-16 (approved 2026-08-17; all three kept)

**Candidate 1 — the deep-dive explanations converted straight into
paper prose, and Shawn said so in the moment.** Two explanation
requests ("explain D-S to a non-statistician archaeologist"; "explain
the threshold-transfer failure") drew explicit in-the-moment
reactions — "This is an excellent explanation, can you externalise
it?" and "you have articulated the granularity problem with the
preregistration well" — and both externalised into discussion-seeds
Seeds 6–7 within minutes of landing. The register that worked:
load-bearing structure first, jargon shed, the honest caveat kept
(the optimism's boundary; the counterweights to the over-bake
thesis). If the pattern holds, "explain it to me" requests are the
cheapest route to Discussion-quality prose and should be treated as
drafting opportunities, not detours.

**Candidate 2 — currency notes on every decision meant no ruling
landed on stale premises.** The D5–D17 review settled thirteen
decisions in one sitting, and part of what made each ruling safe was
that every presentation carried a what-changed-since-drafting audit:
E60 had already resolved the "no erratum covers it" line; D17's
heavy lifts (family FDR, CMT-0106, E45) had already landed and been
signed; D13's block figures were stale-vintage and were refreshed at
settlement. The same verify-before-presenting move opened the
session (the handoff prompt's "three pending user-obs" had already
been resolved in `eb6efa621`). Worth recording if Shawn agrees the
currency audits were load-bearing for the review's speed — the
alternative (ruling on July-vintage premises) would have produced
rulings needing re-litigation.

**Candidate 3 — the verification loop ran end-to-end twice with no
PI arbitration needed.** Both blind verifiers returned
pass-with-corrections; all seven corrections were wording-level; the
disagreement rule (conflict → third derivation) never fired; and the
corrections were applied autonomously with changelog trails, Shawn
seeing only the summaries. On $0 documentation work the full stack —
pre-run review, execution, blind verify, corrections, registry — now
runs without a human in the loop between go and report. Worth
Shawn's verdict on whether that autonomy envelope is right, and
whether it extends to the D17 reconciliation block (which touches
the manifest and schema — higher stakes than prose).

## Session 134 — 2026-08-17 (approved 2026-08-17; candidates 1, 3, and 4 discarded at review)

**Candidate 2 — the outline-first correction arrived with the
compliment attached.** "I'm happy you've drafted methods, but I'd be
more comfortable reviewing an outline with you first before we start
drafting too much text" — a process correction delivered mid-approval.
Claude had extended prose into a section whose structure Shawn had
not settled, on momentum from the licensed Results work. The remedy
cost two question rounds (MD1–MD6) and licensed five further
subsections, so the correction was cheap to honour — but it was
Shawn who had to make it; Claude should have proposed the outline
walk before drafting M.x, not after.

## S135 candidates (2026-08-18, pending review)

Drafted at handoff; accept / edit / discard / replace. Unanswered
candidates hold over — silence never discards.

- **Candidate 1 — the rationale-before-ruling exchange.** On the H6
  classification you declined to rule on a recommendation label and
  asked for the full argument; the written rationale (four arguments
  plus the counter-case) got "agree, in full". Was the initial
  compressed presentation an under-serve for a call of that weight,
  or is recommendation-first-then-expand the right default with
  expansion on demand?
- **Candidate 2 — the AFK block's decision-deferral.** You returned
  from AFK to a completed, blind-verified five-analysis batch with
  every PI-facing call queued as PROPOSED rather than made (classes,
  counting rule, sign-offs). Did that division — full execution
  autonomy, zero decision autonomy — land where you want it, or was
  anything queued that Claude should have just decided (or vice
  versa)?
- **Candidate 3 — the cost-overrun flagging.** The H13 run came in
  31 % over the gated figure and Claude led with that fact in the
  report and commit rather than absorbing a ~$1.40 difference.
  Useful calibration, or noise at this dollar scale? (The underlying
  process error is logged as claude-obs 58 either way.)
