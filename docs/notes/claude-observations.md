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
