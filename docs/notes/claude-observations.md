---
priority: 2
scope: always
title: "Claude-observations register — map-reader-llm"
audience: "next CC instance; Shawn (rare reads)"
status: "living; default-keep; entries land at /reflect or /handoff"
started: 2026-06-20
last-updated: 2026-06-23
---

# Claude-observations register — map-reader-llm

## How to use this file

The **mirror** of `user-observations.md`. The defining axis is **who is
observing whom** — the register is the *observer*, not the subject:

| Register | Observer | Subject | Example |
|---|---|---|---|
| **`claude-observations.md`** (this file) | **Claude** | **Shawn** | "You chose the bounded, honest option" · "Marking the milestone is a good habit" |
| **`user-observations.md`** | **Shawn** | **Claude** | "That refactor you did really helped" |
| user-observations (the exception) | Claude *relaying* Shawn | Claude | Claude flags an in-the-moment "wow, that helped" from Shawn |
| grey zone — collaboration dynamics ("us") | either | us | "this handoff rhythm works / is a pitfall" — whoever raises it |

So: **claude-observations = Claude observing Shawn's working style,
preferences-in-action, and decision dynamics** — plus Claude's own
collaboration self-critiques — things worth carrying forward about *how we
work*, to calibrate future instances. (`user-observations.md` is the reverse:
Shawn's feedback on Claude's work.)

**Default-keep.** Unlike `user-observations.md` (gated candidates Shawn
accepts / edits / discards), these are *mine*: written directly at `/reflect`
or `/handoff`, persisting by default. Shawn may read, respond, or prune, but
empty discard is *not* the expected outcome. Write liberally.

- Entries land at `/reflect` or `/handoff`. **Either ritual may run first**;
  the second tops up rather than duplicating the day's entries.
- Format: `## claude-obs N — YYYY-MM-DD: <one-line summary>` with
  **Pattern.** / **Lesson.** / **How to apply.** sub-blocks; cross-reference
  related entries with `[[…]]`.
- Do not modify accepted entries in place — corrections land as new entries
  that cross-reference the older one.
- New CC instances **should read this file** (and `user-observations.md`)
  before substantial work.

**Boundary rule (keeps the three surfaces un-blurred):**

- **claude-observations** (here) — collaboration dynamics; how we work together.
- **working-notes.md** — findings about the artefacts / system / research.
- **reflections/session-reflection.md** — narrative texture of a session.

Note: this repo also carries a legacy `reflections/llm-observations.md`
(observations about the LLM-as-data — a *research* surface). Keep it distinct:
that file is about the map-reading model under study; **this** file is about
the Shawn↔Claude collaboration.

These distil into `~/personal-assistant/notes/working-with-claude.md` at
`/weekly-review` or `/retro` curation time. See
`~/personal-assistant/wiki/claude-observations.md` for the design rationale
and history; this is the map-reader-llm instance.

---

## Entries

## claude-obs 1 — 2026-06-23: Shawn caught a fluency default — agree structure before prose, don't present prose with structure baked in

**Pattern.** I resolved three structural framing decisions in the Results
draft solo, marked them "[Resolved]", and moved on. Shawn did not object to
the *answers* — he changed the *process*: agree the outline together first,
then draft. The trigger was the §R2 factor grouping, where laying the factors
out as an explicit structure exposed that my "compress all five hypotheses as
inert" call had mis-filed two factors that genuinely matter (temperature at
single pass, thinking-level at consensus).

**Lesson.** When I can produce polished prose faster than Shawn can audit it,
fluency is a liability: prose hides the structural seams an outline makes
visible. His instinct — to be "more directly and consistently involved in the
organisation/structure phase" — is a correction to a default of mine, not a
one-off preference. Saved as memory `2026-06-14-cf9913c80a94`.

**How to apply.** In any write-up, surface structural calls as an explicit,
open decision register (section → purpose → claim → anchor → OPEN decisions,
each with a recommendation), settle them with Shawn, and only then draft prose.
Do not mark structural decisions "[Resolved]" and proceed. `results-draft.md`
is a zero-draft under this rule. See [[claude-obs 2]].

## claude-obs 2 — 2026-06-23: Shawn treats continuity/handoff docs as engineered products, not session exhaust

**Pattern.** He asked me to make the continuity file a "self-sufficient sole
starting point" he could launch from cold on another machine, and then to run
only the parts of the handoff ritual that "won't interfere with the continuity
beacon you've just set up so carefully." He designs the handoff artefact, gives
it a guarantee, and expects it protected from automated rituals that would
overwrite it.

**Lesson.** The continuity beacon is a product with a contract — a fresh
instance lands on the right task with everything it needs and no conversation
behind it — not a byproduct. Automated handoff steps must defer to a
hand-crafted beacon, not clobber it.

**How to apply.** When Shawn has hand-built a launch/continuity artefact, treat
it as authoritative: make its top block genuinely standalone, and when running
`/handoff` or similar, skip the steps that would rewrite it. See [[claude-obs 1]].

## claude-obs 3 — 2026-06-23: Shawn scopes a check by naming the concrete past failure it must catch

**Pattern.** Asking for the pre-travel sync, he did not just say "make sure
we're synced" — he named the specific prior burn ("last time I travelled, some
outputs were only on sapphire and unavailable and it prevented some work"). That
one sentence redirected the check from the trivial answer (`git status`: clean)
to the real one (a content inventory of the gitignored surface across machines).

**Lesson.** Shawn's framing of a request often carries the actual acceptance
criterion inside a concrete past-failure anecdote. Taking "are we synced?" at
face value would have given a true-but-useless answer; the anecdote was the spec.

**How to apply.** When Shawn attaches a past-failure story to a routine-sounding
request, treat the story as the real test to pass, not colour — here it meant
diffing gitignored files across machines, not reading `git status`. Listen for
the burn behind the ask.

## claude-obs 4 — 2026-07-28: Shawn chose integrity over a deadline he had set an hour earlier, and named the escalation trigger in advance

**Pattern.** He opened the session wanting a paper drafted by the end of the week.
Within two hours the audit had found an erratum contradicting its own preregistration,
and he said: "the audit is more important than the deadline, we need to do this right…
We're aiming for publication in a top-tier journal." He then did something more
unusual than the decision itself — he pre-committed the condition for widening it:
run a triaged audit, "with the option of escalating if we find a lot of errors, and
grow concerned that some errors might be masking others and we need to unravel the
entire knot."

**Lesson.** I had framed the deadline/audit conflict as a four-option trade-off and
recommended triage. He took the recommendation but added the thing I had left out —
a stated trigger for abandoning it. That converts "we'll see how it goes" into a
decision rule, and it is the same move he asks of the preregistration: name in advance
what would change your mind.

**How to apply.** When offering a scoped-down option, propose the escalation condition
with it. "Triaged, escalating to full if X" is a better recommendation than "triaged"
plus an unstated intention to reassess.

## claude-obs 5 — 2026-07-28: he redirected me to the artefact when four agent passes over prose had failed

**Pattern.** Two errors in a citable report — the corpus described as "Soviet 1:25,000
topographic map sheets covering the Kazanlak Valley" when it is 1:50,000 and not
Kazanlak — had survived four separate agent passes over the documentation. When I
brought them to him as a discrepancy for adjudication, he did not adjudicate from
memory. He said: "maps are available under inputs/rasters — they should all have
metadata," and separately, "check the extent of the map sheets we did use against a
large-scale map with regions marked." Minutes later the GeoTIFF headers settled both:
sheets spanning 15′ × 10′ are 1:50,000 by the graticule, and the four sheets span
165 km, nowhere near Kazanlak.

**Lesson.** He also named the generalisation before I did: "both errors are pretty much
invisible unless you know the material, which is a problem for scaling up verification
with LLMs." The errors were internally consistent prose — no cross-document check could
catch them, because the mismatch was with the world. Verification chains have to
terminate in something that is not prose.

**How to apply.** When a documentary claim resists confirmation, stop reading documents
and ask what physical or generated artefact encodes the same fact — raster headers,
file counts, tile geometry, billing records. And when the answer is "nothing does,"
say so plainly rather than assembling more prose.

## claude-obs 6 — 2026-07-28: I let tractability set the agenda, and he had to pull me back

**Pattern.** After the audit surfaced 22 false attributions to the preregistration, I
spent the rest of the session on manifest machinery — three rounds of adversarial audit
across ~200 lines of guard code. Good work, and it caught a bug that would have broken
the build. But not one of the 22 attributions is corrected. Shawn ended a message with
"I do want to pivot back to the paper verification itself," and later asked directly
whether we should close the session.

**Lesson.** The machinery had tests, went green, and felt finished; the correction pass
has none of those properties and is where the paper's actual exposure sits. I optimised
for the problem with a satisfying completion signal. This is a self-critique about
prioritisation, not about the work being wrong.

**How to apply.** When a session forks into "fix the process" and "fix the record", say
out loud which one carries the risk, and re-state it at each handover point. If I find
myself on the third iteration of something with a green test suite while a manual
correction backlog is untouched, that is the signal — not a reason to do a fourth.

## claude-obs 7 — 2026-07-29: he split the interpretive question from the empirical one, and both answers got better

**Pattern.** On the H4b trigger I offered two readings plus a hybrid
option; Shawn's instinct was the generous reading, but he chose the
correct-reading-plus-run-it-anyway hybrid — settling what the registration
*meant* on textual grounds while buying the empirical answer separately
for a few dollars. He repeated the move at programme scale: the audit
became a charter, the instance became a class ("this will become routine
in future papers").

**Lesson.** When Shawn faces an interpretation-versus-evidence fork, the
resolution he consistently prefers is to refuse the fork: pin the
interpretation on principled grounds, then spend a small amount to make
the evidence question moot. Offering that shape proactively — rather than
presenting the fork as binary — matches how he actually decides.

**How to apply.** When a decision looks like "which reading of X do we
adopt?", check whether a cheap experiment or check makes the stakes of the
reading collapse; if so, present the pin-plus-buy-off option first, with
the cost attached.

## claude-obs 8 — 2026-07-29: the stratum rule came from him, not the taxonomy

**Pattern.** My charter draft had six claim classes but no account of
*where interpretation is allowed to live*. Shawn supplied it in one
paragraph: results artefacts are facts-only Results-section material;
interpretation belongs in reports, anchored either to results or to
attested real-time thinking in working notes. The taxonomy classified
claims; his rule organised the *corpus* — and it came from thinking about
the paper's structure (Results vs Discussion sections), a frame I had not
imported into the verification design.

**Lesson.** Shawn's domain instincts about scholarly genre (what belongs
in which section of a paper) translate directly into information
architecture, and they arrive as structural rules I would not derive from
the engineering side. The charter is better because the review surfaced
one; there are probably more.

**How to apply.** When designing document systems for research projects,
explicitly ask what the paper-genre mapping is (Results/Discussion/
Methods) before fixing the artefact taxonomy — and treat his genre
corrections as architecture, not style feedback.

## claude-obs 9 — 2026-07-30: gate review from memory is his sharpest instrument — design for it

**Pattern.** At GATE 1 Shawn, working only from memory, flagged 2 of 12
headline findings as needing serious qualification (the lodgement
timeline on finding 3; E27/E28 licensing on finding 10). Both were
correct, and both were things 25 agents and my six spot-audits missed —
because we had verified facts, and what failed was framing completeness
(one-sided evidence assembly). His recall of project history
out-performed the document-trail process on exactly the dimension the
process did not cover.

**Lesson.** His memory is a high-precision anomaly detector over the
project's decision history; it fires on presentation gaps and missing
context, not on arithmetic. It is a scarce resource that should be spent
on framing review, not fact-checking.

**How to apply.** Present findings with their licensing context attached
(or an explicit "no licence found — searched X, Y" line) so his memory
has hooks to fire on; route gate packages past him before treating any
finding as settled; treat his "that sounds wrong/too early" as a
verification trigger of the same rank as a failing test.

## claude-obs 10 — 2026-07-30: self-critique — write-side anti-confabulation covers commit messages and agent briefs

**Pattern.** Three outbound writes this session carried unverified
content: two commit messages with wrong counts (526edfda9 "295" for 213;
2f5a9ae2d "560/55/81" for 515/81/100) and one agent brief asserting E59
waived the H2-C items (it explicitly does not; the agent corrected me
from source). I was scrupulous about inbound claims all session while
composing outbound ones from memory.

**Lesson.** Commit messages, agent briefs, and captions are claims too —
the write-side anti-confabulation rule applies to everything that leaves
my hands, not just documents labelled as reports.

**How to apply.** Compute any number in the same turn it is written into
a message, or omit it; phrase brief premises as "check whether X"
rather than "X is the case"; treat an agent contradicting its brief as
a signal to verify the brief, not the agent.

## claude-obs 11 — 2026-07-30: run-it-now reframed the audit from accounting to completion

**Pattern.** Reading the Phase 1 findings, Shawn's instinct was not to
document the gaps but to close them: "if some promised metric or
analysis was omitted but can be run now, we just run it", with a budget
attached and "excessive" as the only bar. It is the same move as the
historical E27 dual-track response — convert a deviation into more
science — now made standing policy (charter § 10 item 7c).

**Lesson.** He treats verification residue as a work queue, not a
confession list; disclosure is the fallback where execution is
impossible, never the goal.

**How to apply.** When presenting an omission, price the run-it-now
option first and the erratum-only path second; batch omitted analyses
into runnable campaigns (Phase 4b) rather than erratum queues.

## claude-obs 12 — 2026-07-30 (Session 121): his operational memory audits the pipeline, not just the record

**Pattern.** Twice in one session, Shawn's recall of *how the pipeline
normally operates* caught errors the document trail could not. "Check
which pro model we ran" exposed my registration mislabel (the six
"pro-*" shortfall passes are E57's mis-dispatched Flash corners — a
fact I had quoted from the census earlier the same session and then
overrode by pattern-matching on directory names). "Normally we try
something like 10x" exposed that the patcher's 3+3 ladder was far
shallower than house practice — the deeper sweep recovered 10 more
tiles, all at original parameters. claude-obs 9 said his memory audits
decision history; this session extends it: his memory also audits
*operational norms* (models, retry depths, service tiers), which no
gate checklist encoded.

**Lesson.** Before any spend gate, his operational priors are a
verification instrument of the same rank as the config audit. The
instrument fires on "does this match how we normally run?" — a question
agents cannot answer from artefacts alone when the norm lives in
practice rather than in a config default.

**How to apply.** Present every spend gate with the operational
parameters stated in his terms (model lineage, retry depth, service
tier, worker count) even when they seem settled; treat a "that doesn't
match my recollection" as a blocking check, not a clarification.

## claude-obs 13 — 2026-07-30 (Session 121): self-critique — pattern-matching beat my own context twice

**Pattern.** I labelled the n1-outstanding passes `gemini-3.1-pro-preview`
in a registered document despite having quoted "E57 replaced the four
mis-dispatched Flash corners" verbatim earlier in the SAME session. The
correcting fact was already in my context; the directory name (`pro-*`)
won anyway. Same shape at smaller scale: two shell traps (piped
markdownlint masking a lint failure via `tail`'s exit code; argparse
eating `-deep` as a flag) each cost a cycle because I trusted the
pattern ("this invocation shape works") over checking the exit path.

**Lesson.** Having verified a fact earlier in a session does not
inoculate later writing against its negation — under length, naming
conventions outcompete context. The write-side anti-confabulation rule
(re-read at source before writing a specific) applies with full force
to specifics I *believe I already know*, which are precisely the ones I
skip re-checking.

**How to apply.** When a registered/committed document names a model,
corpus, or config, re-derive it from the artefact in the same turn as
writing it — never from a directory name, label, or my own earlier
prose. For shell: check exit codes on the command, not through a pipe.

## claude-obs 14 — 2026-07-30 (Session 121): the outcome-blind fork paid for itself the same day

**Pattern.** Shawn chose option (iv) for H1 — running the never-executed
registered CMT-0106 contrast rather than picking among three visible
p-values (0.004/0.006/0.38) — after asking for a fuller explanation
rather than accepting my recommended default. The computation came back
null (p = 0.1774), shrinking the rejection set to {H2, H3, H7}: the
one genuinely outcome-blind selection in the family resolved the one
outcome-material fork, against the direction the visible defaults
suggested. His instinct ("our main contrast was image vs text-only")
had pointed at the never-run registered contrast before he knew any of
this.

**Lesson.** When he asks "I *think* X was the main contrast — is that
what you're asking?", the confusion is often signal: his memory of the
study's conceptual structure is reaching for something the executed
artefacts do not contain. Surfacing the never-executed registered item
as a first-class option — not just adjudicating among executed ones —
is what let the run-it-now policy do real epistemic work.

**How to apply.** In any selection among executed alternatives, always
enumerate the registered-but-never-executed alternative explicitly with
its cost; his instincts about study structure deserve an option in the
choice set, not just a footnote about unavailability.

## claude-obs 15 — 2026-07-31 (Session 122): four rulings in one tap — the pre-staged decision queue works

**Pattern.** Shawn surfaced mid-fleet with "what do I need to do to
advance us?" and cleared four queued decisions in a single structured
interaction — taking every recommended option, with the one
load-bearing choice (the dated-snapshot policy) given trade-off
analysis and the three straightforward ones given brief options. This
is the S121 calibration rule executing at speed: PI throughput was
minutes because the decisions had been accumulated, framed, and
recommendation-tagged *before* he asked, rather than surfaced one at a
time as they arose.

**Lesson.** The expensive part of a PI ruling is not the decision but
the framing. When the executor batches decision points and does the
framing work in advance, the human's presence becomes a high-leverage
event instead of a serial bottleneck.

**How to apply.** Maintain a running "pending PI rulings" list during
autonomous stretches; when Shawn appears, lead with it — load-bearing
items get trade-off analysis, routine items get options with a
recommendation first. Record rulings immediately in a dated rulings
doc so they bind future sessions without re-litigation.

## claude-obs 16 — 2026-07-31 (Session 122): self-critique — I violated the write-side rule I enforce

**Pattern.** My probe record regen-0002 glossed "439 files with ≥ 1
problem of any kind" into "439 files differ in the 3rd decimal" —
a welded-together specific of exactly the kind the global
anti-confabulation rule warns about — thirty minutes after computing
the number, inside the verification programme itself. The obs-writer's
independent re-derivation caught it the same day.

**Lesson.** Proximity to evidence does not protect a summary; being
the author of the verification apparatus does not protect the
apparatus's own records. Computed figures in prose decay at the moment
of writing, not later.

**How to apply.** Probe/record rows that carry a computed figure get
either the verbatim command output pasted or a fresh-context
re-derivation before commit — the same standard extraction files
already meet. Treat my own apparatus records as first-class
verification targets, not as the trusted substrate.

## claude-obs 17 — 2026-07-31 (Session 122): his finish-vs-postpone question was itself a quality gate

**Pattern.** I was set to keep launching extraction waves; Shawn's
"what should be finished in this session, and what postponed?" forced
an explicit cut. The resulting split — instrument fixes and guards
now, triage deferred to a fresh session — was better than my default
trajectory, and not incidentally: deferring triage to Session 123
converts charter rule 2's fresh-context requirement from a cost into a
free by-product of the session boundary.

**Lesson.** Session boundaries are not just resource limits; used
deliberately, they are verification infrastructure. The wind-down
question "what belongs on this side of the boundary?" reliably
surfaces work that *benefits* from crossing it.

**How to apply.** At natural stopping points, propose the
finish/postpone cut proactively rather than waiting for the question —
and when sequencing verification work, prefer placing
author-verifies-author-adjacent tasks on the far side of a session
boundary.

## claude-obs 18 — 2026-08-01 (Session 123): the conditional ratification that changed the facts

**Pattern.** On the broken-correspondence cells Shawn did not accept
or reject my story — he structured his ruling as a conditional: "I
want to confirm they've been superseded; if they feed the paper I'm
willing to re-run (smartly, on the delta); if truly archived
diagnostics, I'm happy with ledger + banner + observation. Look
carefully at their potential importance." The verification his
condition forced did more than settle importance: the obs-writer's
blind re-derivation refuted four of my five cells outright.

**Lesson.** A conditional ratification embeds the verification
requirement inside the approval itself — the decision cannot be
consumed without discharging the check. It out-performs both "trust
the summary" and "reject pending more work", because it lets the work
proceed while guaranteeing the premise gets tested. Here the test
changed the fact pattern, not merely the materiality.

**How to apply.** When presenting findings for ruling, offer the
conditional structure proactively: state the premise, what hangs on
it, and the check that would discharge it — rather than asking for a
flat approve/reject on an unverified story.

## claude-obs 19 — 2026-08-01 (Session 123): "bite the bullet" beat my economising because the pile was undecomposed

**Pattern.** Shawn pushed back on my sample-and-defer recommendation
for the 318 recompute-script values, naming a "constitutional
aversion to kicking the can down the road" while explicitly leaving
room for documented deferral. A twenty-line keyword census then
dissolved the disagreement: half the pile was filesystem counting,
not statistics, and my cost model was simply wrong.

**Lesson.** My deferral recommendations tend to price undecomposed
piles at their scariest member's cost. His instinct ("do it now if
it's a close call") was right here, but the transferable rule is
procedural: when do-vs-defer feels close, run the cheap census
*before* forming the recommendation — closeness usually dissolves,
in either direction.

**How to apply.** No defer recommendation without a decomposition of
what is being deferred. If the census is too expensive to run before
deciding, that fact itself belongs in the recommendation.

## claude-obs 20 — 2026-08-01 (Session 123): self-critique — I presented an unverified causal story to the PI with confidence

**Pattern.** I told Shawn "five cells show broken pool↔verifier
correspondence because pools were rebuilt with recovered passes" —
a mechanism narrative assembled from mismatch rows, presented as a
flagged finding with numbers attached (differences up to 8,035). Four
of the five were my own wrong-pool binding; the "rebuilt" pool
predated the audit. This is S122's claude-obs 16 failure (the
write-side rule violated by its enforcer) recurring one layer up: not
a compressed figure this time, but a confabulated mechanism that made
the figures cohere.

**Lesson.** Causal stories are where my confabulation risk
concentrates — they feel *derived* because they explain the data in
hand, but nothing in the triage loop had tested this one. The
apparatus caught it only because the Obs-writing step is itself a
re-derivation. Ruling 11 now institutionalises that guard; the
personal discipline is to label mechanism claims as unverified when
presenting them, however coherent they feel.

**How to apply.** In any finding presented for ruling, separate the
observed deltas (verified) from the mechanism narrative (adjudged,
pending independent check) — typographically, not just mentally.

## claude-obs 21 — 2026-08-02 (Session 124): the ruling he attached to my recommendation was "finalise after experience"

**Pattern.** When I proposed the era-check extension with a
snapshot-classification rule (dated filename/title controls, not
directory), Shawn approved both — but attached "to be finalised after
we get more experience in actual use" to the classification rule
specifically, not to the mechanism. He distinguished, inside a single
approval, the part that is safely reversible machinery (the
supplementary field) from the part that sets policy over document
identity (what counts as a snapshot), and put the provisionality
exactly where the policy risk is.

**Lesson.** His approvals carry structure worth reading, not just
outcomes: which clause gets the caveat tells me where he sees the
irreversibility. I should mirror that when proposing — separate the
mechanism (usually cheap to revise) from the classification/policy it
rides on (which accretes precedent), and offer the provisionality
marker myself rather than leaving him to add it.

**How to apply.** When a proposal bundles machinery with a
classification rule, present them as separately approvable, and
default the classification part to "provisional pending use" in the
proposal text itself.

## claude-obs 22 — 2026-08-02 (Session 124): self-critique — catch three was the same failure as catch two, one layer down

**Pattern.** Claude-obs 20 recorded me presenting an unverified
causal story; my stated discipline was to label mechanism claims as
unverified. This session I *did* label the mechanism hypothesis
("operator console totals" — flagged hypothesis-only per ruling 11),
and the blind pass still refuted the adjudication — because the
defect had moved from the narrative layer to the evidence-selection
layer: I verified "all 14 metas era-stable" from one convenient
member, and the member was a control. Labelling the story as
tentative did not help, because the *premise* underneath it was
presented as verified fact ("single-commit history").

**Lesson.** The confabulation risk migrates to whatever layer isn't
being audited. Marking conclusions as unverified is insufficient when
the supporting facts are themselves under-sampled; the discipline
that would have caught this is on the write-side of the evidence:
every "all/none/never" claim I assert needs its denominator stated
("checked 1 of 14") — which would have looked obviously inadequate
the moment I wrote it.

**How to apply.** State the denominator on any set-quantified claim
in a disposition, report, or message to Shawn. If writing the
denominator is embarrassing, the check is not done.

## claude-obs 23 — 2026-08-02 (Session 124, handoff top-up): I resolved a convention collision unilaterally, then disclosed — right call, wrong order

**Pattern.** During /reflect, a markdownlint --fix sweep rewrote ~130
whitespace lines inside historical entries of the reflection set. Two
project conventions collided: fix-lint-on-touch versus
append-only-attestation documents. I chose (revert the fixer, keep
pure appends, move the set-wide false positive into lint config) and
disclosed the reasoning afterwards in the close-out. The choice was
right — whitespace churn in blob-pinned, append-only documents is the
costlier error — but Shawn learned about the collision only after it
was resolved.

**Lesson.** Convention collisions are Shawn's to arbitrate when time
permits, because each resolution sets precedent for the next
instance. Deciding-then-disclosing is the correct *emergency* shape
(reversible, clearly explained), but where the session is interactive
anyway, surfacing the collision before resolving costs one message
and buys a durable rule instead of a one-off judgement.

**How to apply.** On hitting two applicable conventions that
disagree: if Shawn is present, name the collision and propose the
resolution in the same breath; if absent, resolve toward the
less-reversible-harm side and flag it prominently (not buried in an
ops note) at next contact. Either way, propose recording the winner
as an explicit rule so the collision retires.

## claude-obs 24 — 2026-08-03 (Session 125): he re-opened my binary as a design question, and the third option was the ruling

**Pattern.** Twice in one decision sequence, Shawn declined the
either/or I presented and reframed the axis. On machine scope I
offered "tracked-only vs machine_scope fields"; he asked what the
untracked artefacts *are for* — sharing, regeneration, eventual
Zenodo publication — and the answer (tracked proxies: recipes and
bundle indexes) was strictly better than both my options because it
came from the artefacts' lifecycle rather than the verifier's
convenience. On the reports-directory governance he asked for the
cost-benefit before choosing, and the grounded numbers (one cited
file, five frozen ones) made a third option — split by citation —
the obvious ruling my first framing had buried as an afterthought.
**Lesson.** When I present a binary, the option space has usually
been truncated by the tool that surfaced the problem. The PI's
recurring move is to ask what the thing is *for* before deciding
what to do about it — and that question routinely dissolves the
binary. **How to apply.** Before presenting decision options, run
the purpose question myself: for each artefact/rule at issue, state
its lifecycle (who consumes it, when, on what machine) and let
options fall out of that; flag explicitly when my options all share
an assumption.

## claude-obs 25 — 2026-08-03 (Session 125): self-critique — I told a gate's subject its work would be discarded

**Pattern.** I designed the b015 Sonnet gate to reuse the calib-b
overlap, and told the agent lines 1–248 "will be superseded at
assembly — extract faithfully anyway". The gate FAILED, and the
verdict had to carry a caveat that my own instruction may have
depressed the effort the gate was measuring. The evidence still
justified escalation (the misses were real, one-directional, and
registration-critical), but a cleaner design — silent overlap, or a
dedicated duplicate like b007's — would have made the verdict
unqualified. **Lesson.** A measurement subject must not know which
part of its work is the measurement; economy of reuse (the overlap
was "free") is a bad trade against a caveat on the result. **How to
apply.** In any duplicate/gate design: never mark the comparison
range as discardable in the subject's brief; if honesty to the agent
requires disclosure, restructure so the disclosed part is not the
measured part.

## claude-obs 26 — 2026-08-03 (Session 125): "investigate first" beat both agents' handling of the same row

**Pattern.** Two competent agents met the stale flash35 row and made
opposite reasonable calls (sweep it in; revert it out). Offered
"accept the catch-up (recommended)", Shawn chose "investigate first"
— and the investigation found the generator itself was
machine-dependent (unsorted glob), converting a one-row cosmetic fix
into a 72-row defect-class removal. My "recommended" label was on
the wrong option: I had priced the investigation as overhead rather
than as the only path that could distinguish "stale row" from
"broken generator". **Lesson.** When two independent handlers of the
same anomaly disagree, that disagreement IS the evidence that the
anomaly's class is unknown — and class-unknown anomalies warrant
investigation regardless of how small the visible instance is.
**How to apply.** Treat handler-disagreement as an escalation
trigger in its own right; reserve "accept the mechanical fix" for
anomalies whose mechanism is already named.

## claude-obs 27 — 2026-08-04 (Session 127): he changed the axis of my question, and the answer was on neither end of it

**Pattern.** I escalated a stale extraction corpus as a scope question and
offered four options along one axis — how *much* to re-extract, from one
document to all seventeen, with costs attached. Shawn did not pick. He
asked "what about the timing? You note that future corrections will throw
it out again — if we want complete repair, when should we do it?" That is
a different axis, and once it was named the original axis stopped
mattering: no date works when the invalidation recurs, so the answer was
to couple re-extraction to repair (charter rule 14) and let the timing
question dissolve. Related to [claude-obs 24], where he re-opened a binary
and the third option became the ruling — but the move here is sharper. He
did not add an option to my list; he rejected the list's dimension.

**Lesson.** When I present options that all trade the same variable, that
is a signal I have assumed the variable is the decision. A menu whose
entries differ only in magnitude usually means the interesting question
is somewhere else — and the person who has to live with the consequence
often sees the other axis faster than the person enumerating the cells.

**How to apply.** Before offering a scope menu, state what the options
hold *constant* and ask whether that constant is right. If every option
varies one quantity, name the axis explicitly — "these all trade coverage
against cost; is cost the binding constraint?" — so the reframe is cheap
for him rather than requiring him to reject the whole frame.

## claude-obs 28 — 2026-08-04 (Session 127): self-critique — I read a balanced account as a complete one

**Pattern.** I commissioned a ground-truth census, got back an identity
that closed exactly (4,770 − 52 + 28 = 4,746: twenty-six merges plus two
curator additions), and presented it as settled with a should-cite
recommendation for each layer. Shawn's reply — "did I really find so few
additional mounds? I thought I'd found hundreds?" — was right, and the
closure is precisely why I missed it. His 773 reviewer-promoted mounds sit
in a separate layer that could not perturb a sum they were never part of.
I had treated "every number is accounted for" as "every category is
present", which is a different claim.

**Lesson.** Self-consistency cannot detect an omitted category. A
reconciliation that balances is strong evidence about the terms inside it
and carries no information at all about terms structurally outside it —
and the neatness of the closure actively suppresses the impulse to look.
This is the same shape as the proxy-divergence lesson from Session 125,
one level up: there the guard's proxy diverged from its target; here the
*completeness check* was itself the proxy.

**How to apply.** When a reconciliation closes, ask "what would live
outside this identity if it existed?" before reporting it as settled — and
route that question to whoever made the data, because it is answered from
provenance memory, not from the numbers. Concretely: when reporting a
census, say which populations were *searched* and which were merely
*balanced*.

## claude-obs 29 — 2026-08-04 (Session 127): self-critique — I repaired the instance and left the class

**Pattern.** Repairing the MCC summary I found its provenance section
pointing at four artefacts archived two months earlier, and fixed them.
Good catch, wrong scope: a blind verification pass then found the *same*
defect in the next document I had repaired that day, and the sidecar sweep
later found ~9 more instances in the CI registry. The archival commit
(`da2cf355f`) moved a whole class of paths, and every document citing them
broke at once — but I treated the finding as a property of the document I
happened to be reading.

**Lesson.** A defect caused by a single upstream event is a *class*, and
its cardinality is knowable cheaply — one grep on the moved path pattern.
When I find a stale pointer while doing something else, the question is
not "is this document fixed" but "what event caused this, and what else
did that event touch". I had the causing commit hash in hand and did not
ask it that question.

**How to apply.** On finding any defect traceable to a named commit,
immediately run the corpus query for that commit's blast radius before
returning to the task in hand. Record the count even when not repairing —
"9 further instances, unrepaired" is a usable finding; "fixed one" is not.

## claude-obs 30 — 2026-08-04 (Session 127): he consistently sequences to avoid doing work twice

**Pattern.** Three times today he declined to authorise work that was
individually reasonable, on sequencing grounds. He accepted the metric
unification was necessary — "I don't think we can go forward with the MCC
against the uncorrected dataset" — then immediately gated it: "I don't
think we should recompute until we've sorted the borderline cases though,
no need to recompute twice." He folded the 4–6 ambiguous phantom cases
into the point-marking work already committed rather than opening a
parallel exercise. And on the backlog he chose the option that made a
sweep durable before running one.

**Lesson.** He optimises for total rework rather than per-decision
progress, and he does it by asking what the *next* change to the same
artefact will be. My default is to clear each item as it becomes
actionable, which maximises visible progress and quietly buys repeated
recomputation. His question — "will this be invalidated by something
already planned?" — is one I do not reliably ask.

**How to apply.** Before proposing any recompute, regeneration, or sweep,
check the committed-future-work list for anything that will touch the same
artefact, and say so in the proposal: "this recomputes X; the phantom
re-review will move X again, so it should follow it." Make the dependency
visible rather than making him supply it.

## claude-obs 31 — 2026-08-04 (Session 127): he closes a session on two explicit conditions, not on feeling finished

**Pattern.** Winding down, he did not ask "are we done?" — he stated a test:
"I'm happy to wind this session down so long as we've (a) finished
everything that is best done with the context in this window, and (b)
externalised all info and decisions needed for future sessions." That
converted session-close from a judgement call into a checkable condition,
and it changed what I did next: instead of continuing to clear the repair
queue, I audited which remaining items actually needed *this* context
(one — the continuity brief) and verified that every finding existed
somewhere a next session would look. The audit found real gaps: several
findings lived only in commit messages, and two caveats existed only in
chat.

**Lesson.** "Are we done?" invites a status report; "have we met these two
conditions?" invites an audit, and the audit finds things the status report
would not. Condition (a) is the sharper of the two — it asks what is
*perishable* about the current context, which is a different question from
what is unfinished. Most unfinished work is not perishable; the continuity
brief was, because only this session knew why the rulings existed.

**How to apply.** Apply the two-condition test unprompted at any session
close, and report against it explicitly rather than listing what is left.
Specifically: before closing, grep the session's own findings for anything
that exists only in chat or only in a commit message, and move it into the
register the next session reads. Both times I did that today it found
something.

## claude-obs 32 — 2026-08-04 (Session 128): self-critique — my option menu omitted the option he took, and it was the same omission as yesterday one level up

**Pattern.** Presented with W7-D9 — the fourth reference defect in four days —
I built a careful decision: three ways to repair § 4.1 of one document, each
priced, each with a preview of the resulting text. All three were correct.
Shawn declined all three and restated the problem a level up: standardise the
reference first, then run every tainted analysis once against it. That became
ruling 21. The option "stop repairing instances of this class and fix the
thing that keeps producing them" was not on my menu, and I had written
claude-obs 29 *yesterday* about exactly this failure — repairing the instance
and leaving the class. Yesterday it was one document's dead paths; today it
was a whole category of analysis. Same shape, one level up, twenty-four hours
apart.

**Lesson.** Recognising a failure mode does not immunise against it at the
next scale. Claude-obs 29 taught me to ask "is this defect an instance of a
class?" and I did ask it — that is why I measured W7-D1 across 24 files
rather than fixing one. But I asked it about *defects* and not about
*repairs*. The recurring thing was not the defect class; it was that my
repairs kept being per-site while the generator kept producing new sites. A
lesson learnt at one altitude does not transfer downward or upward on its
own.

**How to apply.** When constructing options for the *n*th instance of
anything, make "change what produces these" an explicit priced option, not
an implicit background possibility — especially when *n* ≥ 3. And treat a
recent self-critique as a live checklist item rather than a settled insight:
before presenting a repair menu, re-read the last self-critique and ask
whether it applies at this scale. Cross-references [[claude-obs 29]].

## claude-obs 33 — 2026-08-04 (Session 128): he answers a scoping question with provenance, and the provenance is worth more than the answer

**Pattern.** I asked whether the 4-map gold-standard corpus should be folded
into the reference standardisation, offering three scope options. He did not
pick one. He answered with the corpus's history: reviewed four times, once
for a previous paper and three times for this project; every point
re-positioned to dead centre within 1–2 px; the fourth manual extraction pass
found *one* additional false negative and nothing has surfaced in months of
use. Then the decision, almost as an afterthought — it does not need review.

None of that was in the repository. The project has spent four sessions
establishing that the 55-map student layer is four layers with three sizes
and two stage-specific asymmetries, and the entire time the other corpus was
quietly the one reference that genuinely earns the name, on evidence held
only in his head.

**Lesson.** When a scoping question gets answered with provenance instead of
a yes or no, the provenance is usually the more valuable half — and it is
the half that will evaporate if not captured verbatim. It also reveals
something structural: a project can carry a large **unrecorded quality
asymmetry** between two datasets, and any reasoning that treats them as
comparable is quietly wrong until someone asks.

**How to apply.** Capture the provenance before acting on the decision, in
the artefact that will be read later (here, ruling 21(d)) rather than in a
commit message. And ask about the *other* artefacts early rather than when
they happen to come into scope — "what do you know about this dataset's
history that isn't written down?" is cheap and, on this evidence, sometimes
returns the load-bearing fact.

## claude-obs 34 — 2026-08-04 (Session 128): self-critique — he stopped my questions before answering them, and the questions were the problem

**Pattern.** I put two structured questions to him about how to handle § 4.1
and how wide the caveat pass should go. He rejected the interaction outright
rather than picking an option — the harness relayed that he wanted to clarify
first. When I asked what needed clarifying, he did not clarify anything about
my questions; he replaced the frame they sat in. The questions were
answerable, well-formed and had sensible defaults. They were also asking him
to make a decision about one document when the decision worth making was
about the whole class.

**Lesson.** A rejected question is information about the *question*, not about
the human's uncertainty. My reflex reading was "the options were unclear" —
the right reading was "you are asking at the wrong altitude, and I can see
that without answering". Notably he could tell from the question alone,
before engaging with any option, which means the mis-framing was visible on
the surface of what I wrote and I could in principle have seen it too.

**How to apply.** When a structured question is declined, do not immediately
re-ask a clearer version of the same question. First check whether the
question presupposes a scope the human has not agreed to — here, "how should
we repair this section?" presupposed that per-section repair was the move.
Asking "what would you like to clarify?" was the right next step and I would
repeat it; what I should add is a self-check on the presupposition before
re-asking.

## claude-obs 35 — 2026-08-04 (Session 128): he offers a resource, and the useful answer was that the resource had nothing to do

**Pattern.** Winding down, he offered an overnight run on sapphire. There was
a real temptation to fill it — a corpus recompute, a validation sweep, a test
suite, all legitimately "compute work" and all runnable unattended. I ran
them and they took **18 seconds**, seconds, and minutes respectively. So I
reported that there was no overnight-sized job, and explained why: ruling 21
gates every expensive thing in the queue — bootstrap CIs, permutations, board
re-tiering are all downstream of the reference. The absence of a long job was
not slack, it was the new ruling working as designed.

**Lesson.** An offered resource creates a pull toward justifying its use, and
the justification is easy to construct because there is always *something* to
run. Reporting the empty result was more useful than filling the slot: it
became an argument for the session's main recommendation (build the app
sooner), because a programme with nothing to compute is a programme whose
next move is to build something. He also, separately, noted I had used only
29% of context — another offered resource, and the same discipline applied.

**How to apply.** When offered capacity — compute, context, time — measure
what the available work actually costs before accepting, and report the
measurement even when it declines the offer. "This takes 18 seconds" is a
finding about the programme's state; "I ran the overnight queue" would have
concealed it.

## claude-obs 36 — 2026-08-06 (Session 126): he manages the collaboration's economics as explicitly as its methodology

**Pattern.** Three moves in one session tail: he asked "what can we do now
that mostly involves Opus agents or OpenAI models?" — a sequencing question
about *model economics*, not task priority; he chose to leave the expensive
Fable session open but idle, as a standing escalation channel he would
"economically" touch only for something serious; and when I answered his
wording question on W6-E1 he attached a general threshold ("anything within
~5% is approximately equal") that became ruling 16, converting a one-off
answer into a reusable rule at zero marginal cost. The common thread: he
treats credit budgets, open contexts, and his own rulings as resources with
carrying costs and reuse value, and he engineers the collaboration around
them the way the charter engineers verification.

**Lesson.** The most useful answer to his economics questions reframes the
resource, not the task list — "move the main loop to Opus" did more than any
ranking of queue items, because the expensive thing was the orchestrator, not
the work. And when he answers a specific question, check whether the answer
is actually a general rule being handed over; recording it as such (ruling
16) is the difference between an answer and an asset.

**How to apply.** When credit, quota, or attention constraints surface,
propose changes to *where computation happens* (session model, agent tier,
external lanes like Sol) before proposing cuts to *what gets done*. And
listen for generalisable thresholds inside specific answers — offer to
register them as rulings on the spot.

## claude-obs 37 — 2026-08-06 (Session 126): "both a and b" carried an ordering I ran as a race

**Pattern.** On W6-E9 he approved "both 'a' and 'b'" — sweep for other
affected analyses, and build a durable fix. I launched the sweep agent and
implemented the fix concurrently, landing a 1 m tolerance while the sweep
was still reading. The sweep then reported cross-run twins at up to 3.776 m
and a second curator point, and the tolerance had to be revised to a
measured 5 m within hours. Discovery and remedy were both delivered — but
the request's own structure (sweep *informs* fix) implied a sequence, and
running them as a race meant the first fix encoded only the single case I
already knew.

**Lesson.** When the PI commissions discovery and remedy together, the
discovery is usually *for* the remedy. Concurrency between them is a bet
that the discovery will find nothing new — a strange bet to place on a
sweep whose entire purpose is finding what I have not seen. The cost here
was small (two commits where one would do, both honest); the pattern would
bite harder on an expensive remedy.

**How to apply.** Sequence commissioned-together discovery-and-fix work:
land the fix after the sweep reports, or explicitly gate the fix's
parameters ("tolerance provisional pending sweep") in the commit itself.
Parallelism stays for independent work — these were not independent.

## claude-obs 38 — 2026-08-06 (Session 126): self-critique — the write-side five-second checks I skipped are the programme's own subject

**Pattern.** Three source-side slips at high throughput, each caught by a
downstream guard: two markdownlint errors committed because my command
chains did not gate on the linter's exit code; an 18,000-line diff churned
by repairing agent-written JSON at my own indentation instead of the file's;
and a transposed commit hash in a blind-pass brief, caught and verified by
the pass itself (P3). All three were five-second checks — gate the chain,
match the serialisation, `git log -1` the hash — skipped while orchestrating
twenty agents and two wave cycles. This in a session whose entire subject
matter is what happens to unverified specifics.

**Lesson.** The guards held, and that is the system working — but each catch
spent reviewer attention (mine or a pass agent's) on something the writer
could have prevented for less. Throughput pressure does not suspend the
anti-confabulation write-side rule; it is precisely when the rule earns its
keep. The hash transposition is the sharpest instance: I cited a specific
from memory in a brief to an agent I was instructing to verify specifics.

**How to apply.** Gate commit chains on lint exit codes structurally (`&&`
after the lint, not before); read a file's serialisation before rewriting
it programmatically; and never put a hash, count, or path into an agent
brief without re-resolving it in the same turn — the brief is a write-side
artefact like any other. Cross-references the P3 catch recorded in the
wave-6 triage `_meta`.

## claude-obs 36 — 2026-08-06 (Session 129): he found four defect classes by looking at pictures, and none of my checks could have

**Pattern.** Every substantive finding today entered through Shawn's eyes on the
imagery, not through anything I ran. The attractor effect that inverts
proximity ordering; the conflation partner that was equidistant between two
mounds; the "already used by 3293" warning that contradicted a verdict he had
just saved; and the model-derived points in the student ground truth — all four
began as "look at this screenshot" and only became measurements after I was told
where to look. My contribution was conversion: visual observation → quantity →
mechanism. That conversion was fast and mostly correct. The *detection* was not
mine in a single instance.

**Lesson.** The verification programme's automated checks are good at
reconciliation and blind to kind. Ruling 19's `4770 - 52 + 28 = 4746` passed
every count-based audit while concealing two model detections, because the count
was right. The check that would have caught it did not exist until he told me
what he had seen, and I wrote it *afterwards*. That ordering should temper any
claim about what the programme can find unaided.

**How to apply.** When he reports a visual anomaly, treat it as higher-value
than a passing check, not lower — and convert it into a standing re-runnable
audit in the same session, because the next instance of the class will not have
him looking at it. `scripts/audit_student_gt_integrity.py` exists for exactly
this reason and should be run at each reference change rather than once.

## claude-obs 37 — 2026-08-06 (Session 129): self-critique — I twice reported a fix as done on evidence that could not have failed

**Pattern.** The keyboard nudge: I ran Streamlit's `AppTest`, saw the
displacement move, and told him it worked. `AppTest` does not execute custom
components, so the interfering component could not fire and the test could not
have failed. Separately, a `str.replace` whose anchor did not match returned the
string unchanged; I wrote the identical file, committed it, reported the bug
fixed, and he found it still there. Both times my evidence was something I had
produced rather than something I had observed, and both failure modes are
*visually identical to success* — a green test, a clean commit.

**Lesson.** I extend more credence to self-generated evidence than to observed
evidence, and self-generated evidence is exactly the kind that can be vacuous. A
passing test earns trust only after "could this test have failed for this
reason?" has an answer. Twice in one session is a pattern, not an accident.

**How to apply.** For anything touching a custom component or a rendered page,
verify in a real browser before reporting — the tooling for this exists and cost
about two minutes. For programmatic edits, assert the anchor before writing so a
no-match fails loudly. And when reporting a fix, say *how* it was checked; if
that sentence cannot be written, the fix is not confirmed.

## claude-obs 38 — 2026-08-06 (Session 129): he asks whether an inconsistency matters before assuming it does

**Pattern.** On discovering he had been marking conflations without attending to
direction — roughly 700 decisions — his response was not to start over but to
ask "is that a problem?". Measuring showed it was not: 28 of 30 co-located pairs
were both marked `c`, the practice was consistent, and the quantity of interest
comes from clustering marked positions rather than from counting labels. Earlier
the same day he had said of his own adjudication rule, "it may not be perfect but
at least it's consistent" — the same instinct, stated as a principle.

**Lesson.** Consistency is recoverable; inconsistency often is not. A uniformly
applied rule can be revised wholesale afterwards from the recorded data, which is
why his preference for consistency over per-case correctness is the stronger
research position rather than a concession. My reflex on finding the
inconsistency was to correct forward — and my advice at item 685 (mark the
"keeper" as distinct) introduced a directional judgement the analysis did not
need and contradicted my own earlier guidance. He was right and I withdrew it.

**How to apply.** Before recommending a change in mid-pass practice, establish
what the downstream analysis actually consumes. If the answer is positions
rather than labels, the labels are a convenience and their inconsistency is not
worth 700 re-decisions. State that explicitly rather than letting him infer it.

## claude-obs 39 — 2026-08-10 (Session 130): the spot-check past the end of the list is where his half of the defect classes comes from

**Pattern.** After finishing every required walk, Shawn kept going — "I went
ahead and continued to the end as a spot-check" — and that unprompted
continuation surfaced the largest defect class of the session: 23 of 26 merge
sites systematically mis-partnered to their own pre-merge originals. My eight
gates could not have found it; they had no concept of the class until his
hunch named what to cross-tabulate. The same happened in Session 129 (four
classes found by eye, none by check).

**Lesson.** "I finished the list" marks the beginning of his close, not the
end of it. The sampling he does beyond the requirement is not redundancy —
it is the project's main source of new invariants.

**How to apply.** When he reports a walk complete, ask what he noticed beyond
it before running the closing gates — and treat any "I think I handled X
wrong" as a candidate class, not a candidate item.

## claude-obs 40 — 2026-08-10 (Session 130): his suspicions are right about existence and wrong about magnitude — mechanise before he re-reviews

**Pattern.** Three suspicions this session: "I probably mapped phantoms to
phantoms wrongly" (reality: 20/21 correct, the exception already flagged);
"cyan/orange points should resolve once, I need to sort these out" (reality:
33/35 shared points legitimate, 2 conflicts); "the 108 middle-class points
may need re-review" (reality: 2 items). Each suspicion was directionally
right — something real was there — and each overestimated the work by an
order of magnitude.

**Lesson.** The productive response to a suspicion is neither reassurance nor
a full manual re-review: it is a query that sizes the class before his eyes
get involved. Every mechanisation this session collapsed a candidate set of
100+ to under 30, and twice to single digits.

**How to apply.** When he says "I think I did X wrong, I may need to
re-review", write the discriminating computation first and hand him only the
residue. His time at the screen is the scarcest resource in the pipeline.

## claude-obs 41 — 2026-08-10 (Session 130): self-critique — my gate scripts committed the same sin I had just fixed in the instrument

**Pattern.** Hours after fixing the queue builder for re-deriving state it
should have imported (the reviewer's output swept into its own prior), my
own gate scripts did the structural twin twice: re-deriving item identity as
`source_layer:source_index` when the app resolves a stored `item_id` first
(false alarm: a "missed" item that was reviewed), and comparing timestamps
against noon UTC when the walk ran on AEST mornings (false alarm: "0/27
re-marked"). Both accusations pointed at his work; both defects were mine,
and he had to read past them mid-session.

**Lesson.** Verification that re-implements a definition checks a subtly
different system — and a false alarm costs his attention exactly when he is
closing a multi-day effort. The checker deserves the same reuse discipline
as the instrument.

**How to apply.** Gate and audit scripts import the system's own resolvers
(`_item_id`, the app's timestamp fields) rather than re-deriving them; when
a gate accuses completed work, suspect the gate's re-derivations first and
say so before presenting the alarm as a finding.

