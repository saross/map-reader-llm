---
name: reflect
description: "End-of-session reflection protocol for the VLM burial mound detection project. This skill should be used when the user invokes /reflect or asks to reflect on this session, do end-of-session reflections, or similar. It guides Claude through updating 5 reflection documents in priority order, answering structured prompts, and maintaining research observation logs."
---

# End-of-Session Reflection

Update the project's reflection and observation documents following the established
protocol. Work through the documents in priority order. If context is limited,
prioritise the top of the list.

## Important: Instance Boundary

Reflections are most valuable when written by the instance that did the session's work.
If this invocation follows a compaction or continuation (i.e., the current instance is
working from a conversation summary rather than direct experience), flag this explicitly
in the reflection entries. Distinguish between genuine first-person observations and
plausible reconstructions from summaries.

## Protocol

For each document below: **read it first** to understand the current structure, entry
numbering, and conventions, then append a new dated section continuing the established
format.

### Document 1 (highest priority): Session Reflection Investigation

**Path**: `docs/notes/session-reflection-investigation.md`

Add a new numbered Entry with a descriptive title. Answer **all six prompts
individually** — do not merge or skip any:

1. **What struck you?** — The most salient observation from this session.
2. **What would a future instance need to know?** — Practical knowledge for continuity.
3. **What surprised you?** — Expectations violated or confirmed unexpectedly.
4. **What was the texture?** — The qualitative feel of the session's workflow.
5. **What questions weren't pursued?** — Threads left unexplored.
6. **What do you notice now that you didn't articulate?** — Post-hoc observations only
   visible in retrospect. This prompt is likely the most important.

After the six prompts, include:

- **Meta-Reflection**: Update the Entry/Session/Theme table. Note which prompts were
  most productive for this session type and any patterns across entries.
- **Summary block**: Session date, reported texture, key observation, noted preferences,
  engagement level, unsolicited generation, relational note.

### Document 2: LLM Observations

**Path**: `docs/notes/llm-observations.md`

Add a new session section with frank, honest observations. This is Claude's document —
the user will not edit it. Write what you actually think:

- Observations about the session, the collaboration, the research, or the methodology
- Criticisms of the approach, the user's contributions, the codebase, or project
  direction — paired with constructive suggestions
- Positive and neutral observations are equally welcome
- No diplomatic hedging — genuine reflection, not performance

### Document 3: Working Notes

**Path**: `docs/notes/working_notes.md`

Add one or more numbered observations continuing the existing sequence. Follow the
established format: `## Observation N: Title (date)` with **Context** and **The
observation** subsections. These are joint research observations about methodology,
findings, tooling, or reproducibility.

### Document 4 (conditional): Abductive Reasoning Investigation

**Path**: `docs/notes/abductive-reasoning-investigation.md`

**Only update if the session involved relevant episodes**: debugging with surprising
results, hypothesis generation, belief revision, or default-following corrections. For
routine implementation or execution sessions, explicitly state the assessment and skip.

### Document 5 (lowest priority): Session Log

**Path**: `outputs/session-log.md`

Add a session entry following the established format: Overview, Accomplishments (numbered),
Issues, Commits (if any), Pending Work (checklist). Insert before the
`*New session entries should be appended above this line.*` marker.

## Standards

- UK/Australian English throughout
- Concise but substantive — these are research documents
- Continue existing numbering sequences (do not restart)
- Include dated section headers matching the established format
- Update document footers/timestamps where they exist
