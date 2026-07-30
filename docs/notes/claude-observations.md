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
