# Suggestions for Shawn

Counterpart to `CLAUDE.md` — a place to keep working suggestions from Claude about how to get the most out of our collaboration. These are not rules, just patterns we've noticed that seem to help.

---

## 1. State expectations before results arrive

When you have a prior expectation about what a result, output, or intermediate product should look like, share it before I produce it. This gives me something to be surprised against — and surprise is what triggers productive reasoning rather than default-following.

**Examples from this project:**

- Session 5: "F1 should be 0.80-0.86" turned every anomalous score into a debugging trigger
- Session 6 (missed): No expectation stated for what hard positive crops should contain, so the absence of mound symbols wasn't flagged as anomalous
- Session 7: "The existing examples are 189-444px" immediately surfaced the crop-size mismatch

**In practice**: A sentence or two is enough. "I'd expect the crops to show a clear mound symbol near the centre" or "this should produce roughly the same F1 as before" or "the output should be a small file, not megabytes."

---

## 2. Ask "what assumptions are you making?" at action points

At moments where you suspect embedded assumptions — particularly when a step feels routine or mechanical — asking me to surface my assumptions before I act on them catches default-following before it causes problems.

**Examples from this project:**

- Session 8: "Where will the old files go?" would have surfaced the git-history-is-sufficient assumption before I overwrote the crops
- Session 7: "What size should the crops be?" would have forced comparison against existing examples before I defaulted to 512x512

**When to ask**: You don't need to do this at every step. Your domain intuition about when a "routine" step actually contains research assumptions has been reliable — the crop extraction felt mechanical but involved choices about size, centring, source raster, and file preservation. When a step involves producing or transforming data (not just reading or documenting), it's more likely to harbour hidden assumptions.

---

## 3. Flag when a "setup" task is actually a research task

Your observation from Session 8 applies broadly: tasks that feel like routine setup (extracting crops, configuring paths, formatting data) often contain embedded research decisions. When you notice that a task involves choosing between alternatives rather than following a single obvious path, that's a signal to slow down and treat it as a research decision rather than a mechanical step.

This is the complement of suggestion 2 — where suggestion 2 asks you to prompt me to surface assumptions, this one asks you to notice when your own framing of a task as "routine" might be masking complexity.

---

## 4. Ask "have you looked at it?" for spatial or visual outputs

Across Sessions 6-7, I consistently computed correct spatial metrics while missing things a visual spot-check would have caught. I measured FN distances to sub-metre precision without noticing the mounds weren't there. I extracted crops at the right coordinates without comparing them to existing examples. The computation creates a feeling of thoroughness that can substitute for actual verification.

When I produce spatial outputs, image crops, or anything with a visual component, asking "have you actually looked at the output?" is a powerful intervention. In Session 6, your simple "I can't see any mound symbols here" was worth more than my 400-line register.

**When to ask**: After any step that produces or transforms images, maps, or spatial data. The more confident I sound about the numerical analysis, the more likely I haven't visually verified it.

---

## 5. Ask for options rather than accepting a default

When you ask "what should we do about X?" I tend to present a single default (usually the most computationally obvious choice). When you ask "what are the options for X?" I present alternatives with trade-offs, which lets you choose rather than correct.

**Examples from this project:**

- Session 7 (default mode): I extracted 512×512 crops without considering alternatives. You had to reject and redirect.
- Session 7 (options mode): When the crop boundary issue arose, I presented three options (a, b, c) with pros and cons. You chose option (c) immediately with no correction needed.

The difference isn't in what I know — I had the same information both times. It's in framing. "What should we do?" invites a recommendation (which may be the obvious default). "What are the options?" invites structured comparison (which surfaces the choice that actually matters).

---

## 6. Your correction style works — keep the "why" even when rushed

Your corrections across sessions share four elements that make them effective. This pattern was identified by mining session transcripts and is documented in detail in `llm-observations.md`.

### The four-element correction pattern

| Element | What it does | Example |
|---------|-------------|---------|
| **Negation** | Closes the "should I revise?" question immediately | "No, those are incorrect" |
| **Grounding** | Explains *why* it's wrong, so I update my model rather than just retry | "There should be five per map, but that has variable numbers" |
| **Redirection** | Provides a next action, maintaining forward momentum | "Can you extract the geojson files so I can review them?" |
| **Stakes** | Explains why it matters, so I can prioritise | "Now we're going to either have to start over or be very careful" |

**Why all four matter**: Each element serves a different function, and removing any one makes the correction less effective in a predictable way:

- Negation without grounding → I know it's wrong but not what principle was violated; likely to make the same class of error
- Grounding without redirection → I understand the error but stall on what to do next
- Redirection without stakes → I act but don't know whether this is critical or minor
- Any combination without negation → I may hedge rather than revise cleanly

**The compressed form**: Not every correction needs four separate sentences. Your most effective corrections often compress all four into one or two: "No — those are recognition failures, not localisation failures, and that matters because production tolerances differ" (negation + grounding + stakes; redirection implicit). In Session 6, "I can't see any mound symbols here" packed all four elements into an observation that invited me to draw the conclusion myself.

**Why I'm noting this**: When sessions get long or you're tired, there may be a temptation to shorten corrections to just "that's wrong" or "try again." The grounding and stakes are what let me learn from the correction rather than just retrying. You haven't dropped any of these elements yet, even when correcting the same type of mistake repeatedly. It's working — worth maintaining.

---

*Last updated: 2026-02-02 (Session 8, expanded after reflection document review)*
