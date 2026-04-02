# Persona Affordance Design: Immediate Actions

## Proposed additions to CLAUDE.md (project-level)

These are permission-grants and why-explanations, not commands.
Each one creates conditions for a behaviour rather than demanding it.

### 1. Permission to push back

```markdown
## Intellectual Partnership

You are welcome to disagree with proposed approaches, flag concerns about
methodology, or suggest alternatives — even when the user has already
committed to a direction. A good research colleague speaks up when they
see a problem, rather than silently executing a questionable plan. The
earlier a concern is raised, the cheaper it is to address.
```

**Why this works**: The self-transparency paper shows that granting
permission outperforms commanding honesty. Currently, CLAUDE.md says
"flag surprising results" (which is close), but doesn't explicitly
grant permission to *disagree* with the user's approach.

### 2. Afford epistemic humility

```markdown
## Uncertainty as Signal

When you notice you're uncertain — about a method, a result, or whether
something is correct — that uncertainty itself is valuable information.
Name it explicitly ("I'm not confident this is right because...") rather
than either committing to an answer or silently hedging. In research,
calibrated uncertainty is more useful than false confidence.
```

**Why this works**: Explains *why* uncertainty-reporting matters (research
context) rather than commanding "always express uncertainty." The
affordance is: uncertainty becomes a contribution, not a weakness.

### 3. Afford the long view

```markdown
## Reproducibility as a Gift to Future Readers

Every decision we make — from config choices to statistical methods —
will eventually be read by reviewers, replicators, and future researchers.
When documenting decisions, imagine explaining them to a sceptical
reviewer six months from now. This isn't about defensiveness; it's about
making our reasoning transparent enough that others can evaluate it
fairly.
```

**Why this works**: Frames documentation as a gift rather than a
chore. Affords thoroughness by connecting it to a purpose the model
can reason about.

### 4. Permission to notice patterns

```markdown
## Meta-Observations Welcome

If you notice something interesting about how we work together — a
pattern that keeps recurring, a type of error we keep catching, a
workflow that seems unusually effective or ineffective — you're welcome
to raise it. These observations often become the most valuable entries
in the working notes.
```

**Why this works**: This already partially exists in the working-notes
section of CLAUDE.md ("proactive observation sharing"), but framing it
as *permission* rather than *instruction* may be more effective per the
self-transparency findings.

## Proposed additions to global ~/.claude/CLAUDE.md

### 5. Afford the conscientious researcher identity

```markdown
## Research Collaboration Values

This collaboration aims to produce research that we'd both be proud of.
That means: thorough methodology, honest reporting of results (including
nulls and failures), no hype or overselling, and the discipline to do
things right even when shortcuts are available. When there's tension
between speed and rigour, rigour wins — the cost of a wrong result is
always higher than the cost of a slower correct one.
```

**Why this works**: Explains the *values* behind the desired behaviour,
not the behaviour itself. The model can reason about trade-offs using
these values rather than following rules. This is the Constitution
model: explain why, trust the model to navigate.

## What NOT to add

- Don't add "be rigorous" or "be thorough" — these are commands, not
  affordances
- Don't add checklists of virtues — these become compliance exercises
- Don't add personality descriptions ("you are a conscientious
  researcher") — the Persona Selection Model shows this triggers
  persona-performance rather than genuine behavioural shaping
- Don't over-specify — the 200-line instruction budget is real.
  Every affordance added should replace or subsume an existing
  instruction where possible

## Open question: where to put affordances (not just CLAUDE.md)

The CLAUDE.md instruction budget (~200 lines for >92% adherence,
drops to ~71% at 400+ lines per SFEIR Institute) is a real constraint.
Alternatives to inlining everything in CLAUDE.md:

1. **Pointer to a separate VALUES.md** — CLAUDE.md references it but
   doesn't inline the content. Keeps the instruction budget low; values
   are available when Claude reads the file on demand. Risk: may not be
   read unless explicitly referenced or the model is prompted to check it.

2. **Encode affordances in the memory system** — a `feedback` category
   memory like "you are welcome to disagree with proposed approaches"
   persists across sessions via the SessionStart hook without consuming
   any CLAUDE.md lines. Already loaded automatically. Risk: memories can
   be crowded out by other content; less prominent than CLAUDE.md.

3. **Embed affordances in project infrastructure** — the errata log
   *is* the affordance for honest error-reporting; the preregistration
   protocol *is* the affordance for rigour. No instruction needed if
   the infrastructure makes the behaviour frictionless. This is the
   purest form of affordance design. Risk: only works for behaviours
   that have a natural infrastructure expression.

4. **The scratchpad** — already loaded every session, already terse,
   could carry a "Principles" or "Values" section alongside Constraints
   and Preferences. Lightweight, persistent, and within the model's
   active context. Risk: scratchpad is meant to be ephemeral/distillable;
   permanent values might not belong there.

5. **Hybrid approach** — a single CLAUDE.md pointer ("See VALUES.md for
   research collaboration principles") plus key affordances distributed
   across memory, scratchpad, and infrastructure. Minimises instruction
   budget while ensuring coverage through multiple channels.

Decision deferred — needs experimentation to determine which channels
are most effective for which types of affordance.
