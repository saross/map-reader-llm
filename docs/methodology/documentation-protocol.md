# Documentation Protocol

**Purpose**: Define when and how each documentation source gets updated,
to prevent the drift discovered in Session 51 (decisions log 1 month
stale, session log 6 weeks stale, while working notes stayed current).

**Last updated**: 2026-03-15

---

## Principles

1. **Single source of truth per information type.** Don't duplicate
   information across documents — cross-reference instead.
2. **Document decisions when made, not retroactively.** The rationale
   is freshest at the point of decision.
3. **Working notes are the backbone.** Observations capture findings
   as they happen. Other documents reference them.
4. **Formal documents serve formal purposes.** The decisions log and
   errata exist for preregistration compliance and auditability.
   They don't need to be exhaustive narratives — they need to be
   accurate, numbered, and cross-referenced.

---

## Document Responsibilities

### Working notes (`working-notes.md`) — Observations

**When to write**: During or immediately after discovering a finding,
mechanism, or pattern. This is the primary real-time capture document.

**Trigger**: Any of:

- A surprising result
- A methodological insight
- An infrastructure lesson
- A pattern across experiments

**Format**: `## Observation N: [title] (YYYY-MM-DD)`

**Cadence**: Continuous — write as discoveries happen.

### Decisions log (`decisions-log.md`) — Decisions

**When to write**: When making a design choice that affects methodology,
closes a pathway, or changes the experimental plan.

**Trigger**: Any of:

- Choosing between alternatives (configs, approaches, thresholds)
- Closing a pathway (abandoning Flash-Lite, closing 384 tiles)
- Deviating from the preregistration
- Carrying forward a parameter to the next phase

**Format**: `## Decision N: [title]` with Date, Decision, Rationale,
Alternatives, Evidence fields.

**Cadence**: Per-decision. Typically 1-3 per session when running
experiments; 0 for analysis-only sessions.

**Rule**: If you find yourself writing "we decided to..." in working
notes, that's a decision log entry.

### Protocol errata (`protocol-errata.md`) — Errata

**When to write**: When implementation deviates from the preregistration,
or when a bug affects results.

**Trigger**: Any of:

- A parameter differs from what the preregistration specifies
- A bug affects experimental outputs
- A clarification is needed for ambiguous preregistration language

**Format**: `### EN: [title]` with Date, Type, Files, Impact table
followed by Description, Fix, Affected results.

**Cadence**: As discovered. Often batched at phase boundaries.

### Results files (`results/`) — Per-phase outputs

**When to write**: After completing a phase's analysis.

**Trigger**: Phase completion.

**Format**: Phase-specific. Must include a status line
(`**Status**: Complete / In Progress / Draft`).

**Cadence**: Once per phase, updated if results are revised (e.g., v2).

### Session log (`session-log.md`) — Session summaries

**When to write**: At session end, as part of `/reflect`.

**Trigger**: End of session.

**Format**: Session number, date, focus, what was done, key findings,
commits.

**Cadence**: Every session. Can be brief for short sessions.

**Note**: The session log is a timeline index, not a duplicate of
working notes. Keep entries concise — link to observations and results
rather than repeating findings.

---

## End-of-Session Checklist

Before ending a session that involved experiments or decisions:

- [ ] **Observations**: Any new findings written to working notes?
- [ ] **Decisions**: Any design choices made? → decisions log
- [ ] **Errata**: Any deviations from preregistration? → errata
- [ ] **Results**: Phase completed? → results file with status
- [ ] **Session log**: Session summary written?
- [ ] **Cross-references**: New entries reference related documents?

This checklist should be incorporated into the `/reflect` skill.

---

## What Goes Where (Decision Tree)

```text
"I discovered something interesting"
  → Observation in working-notes.md

"We chose X over Y"
  → Decision in decisions-log.md (+ Observation if the finding
    that prompted the decision is itself interesting)

"This doesn't match the preregistration"
  → Erratum in protocol-errata.md

"The phase is done, here are the numbers"
  → Results file in results/

"Here's what happened this session"
  → Session entry in session-log.md (brief, with cross-refs)
```

---

## Anti-Patterns to Avoid

1. **Don't write decisions in working notes only.** Working notes
   capture *findings*; decisions log captures *choices*. A finding
   ("HIGH thinking helps consensus") is not a decision ("use HIGH
   thinking for consensus runs").

2. **Don't backfill session logs from commit messages.** If you
   missed writing a session entry, add a brief stub rather than
   reconstructing a detailed narrative. The information exists in
   other documents.

3. **Don't duplicate errata descriptions in decisions.** Reference
   the erratum number — `See E33` — rather than re-describing the
   bug.

4. **Don't let the decisions log go stale.** If a session involves
   a decision and you don't log it, the next session will inherit
   the debt. Log decisions when made, even as one-liners that you
   flesh out later.
