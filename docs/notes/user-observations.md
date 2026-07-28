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
