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

**Approval-with-envelope lets the work run overnight.** "I approve up to $5",
"ca. $34 unless the smoke test throws up a serious issue", "go to both!" — he
delegates execution inside an explicit cost envelope plus a smoke gate, stated
up front. That structure is what allowed two API campaigns and a model tranche
to run unattended (relaunches, cleanups and all) without a single re-approval
round-trip, while keeping every dollar pre-authorised. The pattern to preserve:
the envelope and the abort condition are named *before* launch, so autonomy has
edges.

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
