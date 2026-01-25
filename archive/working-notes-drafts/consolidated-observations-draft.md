# Consolidated Observations: Human-AI Collaboration Patterns

**Status**: Draft for final review before adding to working_notes.md
**Consolidation**: 20 candidates → 12 refined observations

---

## Observation 54: Context Window Pressure and Session Recovery (2026-01-25)

Sessions frequently hit context limits, requiring restarts with summarisation overhead. The largest session (codebase linting, 1105 turns) experienced approximately 15 context overflows across 74 hours of work.

**The real cost**: While CC could help generate summaries by reading session history from `~/.claude/`, the genuine burden was **loss of momentum and context reconstruction**. Each restart required re-establishing nuanced understanding accumulated during the session—subtle decisions, implicit constraints, and working assumptions that don't survive summarisation cleanly.

**Pattern**: CC did not proactively offer summaries or suggest good stopping points, even when sessions spanned multiple days. The human bore responsibility for recognising when to checkpoint.

**Implication**: Future collaboration would benefit from proactive session health monitoring—AI suggesting "we've covered substantial ground; would you like a summary checkpoint?" rather than running until forced to restart.

---

## Observation 55: Marathon Sessions and the Case for Session Discipline (2026-01-25)

Sessions regularly exceeded 20-30 hours of active work (codebase linting: 74 hours; tile-size pilot: 33 hours; OSF preparation: 28 hours), with turn counts in the hundreds to thousands. Work accumulated in single sessions rather than being decomposed into focused, bounded interactions.

**Pattern**: Neither human nor AI suggested "this is a good stopping point" or "let's break this into phases." Individual tasks were often decomposed well, but sessions bloated across many tasks until context exhaustion forced restart.

**Trade-off**: Marathon sessions offered sustained focus without coordination overhead and maintained context even across `/compact` events. However, they increased risk of accumulated errors, made context recovery harder after interruption, and created complex session relationship webs that are difficult to navigate when reviewing later.

**Lesson learned**: The better solution to maintaining context is **externalisation of knowledge into documents** (working notes, decision logs, planning files) rather than relying on session continuity. More disciplined, focused sessions would also improve archive legibility for transparency purposes.

---

## Observation 56: Externalisation Infrastructure for Collaboration Continuity (2026-01-25)

Long-term human-AI collaboration requires deliberate infrastructure for memory and continuity. The January 2026 sessions included substantial "meta-work": archiving 73 session files to Git LFS, creating human-readable directory names, generating machine-readable catalogs, and documenting session relationships (continues, continuedBy, isPartOf).

**Pattern**: Unlike continuous human partnerships where shared memory feels implicit, AI collaborations fragment into discrete sessions requiring explicit bridging.

**Nuance**: This isn't unique to AI collaboration—humans need analogous scaffolding too: meeting minutes, memoranda, planning documents, action items. Humans have context limits and need to externalise information regularly and intentionally. The difference is that AI session boundaries are sharper and more absolute than the gradual forgetting humans experience.

**Observation**: The effort invested in session infrastructure (archiving scripts, metadata schemas, catalogs) reflects a genuine need, not over-engineering. Without it, prior work becomes effectively inaccessible.

---

## Observation 57: Trust-Enabled Efficiency and the Development of Shorthand (2026-01-25)

Delegation evolved through demonstrated reliability, not advertised capabilities. Early sessions show verbose explanations and permission-seeking; later sessions shift to terse directives and assumed context.

**Progression**:

- **Early (Dec 2025)**: Multi-paragraph research agendas followed by "What would you like to tackle first?"
- **Late (Jan 2026)**: "Hi CC, can you run the script to archive our interactions?" — single-sentence requests with assumed competence

**The "hand-wave" phenomenon**: With established trust, the human could gesture vaguely in the right direction—not looking up exact script names or precise prompts—and CC would infer intent and fill in the blanks. This mirrors how experienced human collaborators work: shorthand references to shared understanding replace detailed specifications.

**Division of labour that emerged**:

- **Human provides**: Strategic direction, methodology judgment, approval for destructive/irreversible actions
- **AI provides**: Implementation, investigation, validation, gap analysis, structured reporting
- **Shared**: Problem identification (both notice issues), decision-making (AI recommends, human approves)

**Observation**: Effective AI collaboration mirrors human mentorship—initial close supervision gives way to delegation as track record accumulates. The AI serves as both collaborator and quality control system, not just executor.

---

## Observation 58: Proactive Agency and Appreciated "Project Management" (2026-01-25)

The AI consistently used "Let me [action]" phrasing to signal next steps without waiting for explicit permission. Analysis found ~3:1 ratio of AI initiative phrases ("let me", "I'll", "I suggest") to user delegation/approval phrases.

**Pattern**: This creates a rhythm where AI announces intent, executes, then reports. Human can interrupt or course-correct but doesn't need to micromanage.

**Example sequence**:

- "Let me check what's been completed by examining the prompts directory"
- "Let me also check recent git commits to understand what work has been done"
- "Now I have a clear picture. Let me update the future_work.md file"

**Reception**: This proactive agency—more noticeable since Opus 4.5—was appreciated rather than resented. Being "project managed" and pushed along kept work moving and reduced the cognitive burden of deciding what to do next.

**Observation**: Proactive initiative reduces cognitive load on the human while maintaining control. The human sets direction; AI drives tactical execution. This only works with established trust and would likely feel presumptuous in early collaboration.

---

## Observation 59: Research Taste Externalised Through Focal Documents (2026-01-25)

The human expressed methodological judgment through questions and corrections rather than explicit instructions. Values were revealed through patterns of verification requests, not declarations.

**Pattern**: The human repeatedly asked the AI to verify work against preregistration specs ("verify config alignment", "check preregistration compliance"). This communicated research values (rigour, reproducibility, transparency) without ever stating "I value rigour."

**The preregistration as focal point**: The preregistration document became the externalised embodiment of research taste and judgment. Rather than the human constantly articulating implicit knowledge, plans, and methodological preferences, these were encoded once in a formal document that both human and AI could reference.

**Side benefit**: This approach—enforcing a priori design, thorough planning, and articulation of implicit knowledge—is arguably good research practice regardless of AI involvement. The discipline required for transparency also improves research quality.

**Observation**: AI configuration documents (CLAUDE.md) can specify preferences explicitly, but implicit learning through interaction and reference to focal documents may be equally important for AI understanding researcher values.

---

## Observation 60: Compliance Testing as Methodology Guardrails (2026-01-25)

Rather than treating discrepancies between implementation and preregistration as configuration issues to fix quietly, the team encoded methodological commitments as tests that must pass.

**Example**: Test implementation included deliberate compliance tests:

- `test_tile_selection_seed_matches_preregistration` — expected to fail when seeds diverged
- Test comments: "This test will verify the preregistered seed value and is expected to **fail** until this is resolved. This is intentional—failing compliance tests catch methodology issues."

**Origin**: Notably, it was Opus 4.5 (in the web app) that initially suggested encoding preregistration requirements into the testing suite when asked about pragmatic approaches to testing. The human (new to automated testing) found this an excellent suggestion that shaped the project's approach.

**Observation**: Tests weren't just for code correctness—they enforced research methodology. A failing test wasn't a bug to fix quietly; it was a flag requiring explicit discussion of whether preregistration should be updated or implementation should be corrected. This pattern is transferable to other preregistered research projects.

---

## Observation 61: Archiving Over Deletion for Audit Trails (2026-01-25)

When files became obsolete, the pattern was to archive them rather than delete them. This maintained audit trails essential for preregistered research.

**Pattern**: "Let me archive the old files" → files moved to `archive/deprecated-prompts/`, `archive/speculative-configs/`, etc.

**Rationale**: In preregistered research contexts, deleting files risks losing methodological context or destroying evidence of decision processes. Even with version control, archiving surfaces the history and decisions of the project without requiring interrogation of git history.

**Cost-benefit**: This belt-and-suspenders approach has relatively low cost (disk space is cheap; directory clutter is manageable with good organisation) while providing significant transparency benefits. The practice became formalised in CLAUDE.md as explicit guidance.

---

## Observation 62: Proactive Quality Assurance and Error Discovery (2026-01-25)

When the AI encountered anomalies, it launched investigation threads without waiting for explicit instruction. After implementing changes, it immediately ran verification commands to confirm success.

**Investigative pattern**: When a test failed (seed didn't match preregistration), the AI didn't ask "which files should I check?" Instead, it examined preregistration sections, read metadata files, searched git history, cross-referenced data, and produced diagnostic tables—conducting forensic analysis and delivering structured findings.

**Verification pattern**: After creating or modifying files, the AI proactively ran tests, checked linting, and reported status without being asked "did it work?"

**Evolution**: This proactive quality assurance became more noticeable since Opus 4.5. CC regularly found problems with previously written scripts, unarchived sessions, and configuration inconsistencies. While many discovered problems were in artefacts CC itself had produced, CC also found errors in the human's own work.

**Observation**: This investigative and verification autonomy reduces back-and-forth significantly. The AI behaves more like a research assistant who knows how to find information and verify work than a tool requiring precise instructions for each step.

---

## Observation 63: Unexpected Capacity for Methodological Framing (2026-01-25)

The human initially expected a coding assistant but discovered a research collaborator capable of identifying publication-worthy insights and framing arguments.

**Example** (from first session): AI observation: "The narrative arc for a publication is already emerging: 'we tried to outsmart the model with verification logic; turns out trusting aggregate agreement works better.' That's a genuinely interesting finding for the prompt engineering literature."

**Impact**: This observation helped the human conceptualise how to frame the argument about consensus voting—the shift from elaborate prompt engineering to "get it close enough and let voting carry the weight." The human was surprised by the power of consensus voting but may not have framed it this way independently.

**Observation**: The AI's capacity for methodological commentary and argument framing (not just technical execution) shifted the collaboration dynamic. The human discovered capabilities through use, not through capability advertising. This suggests value in giving AI latitude to offer interpretive commentary, not just execute instructions.

---

## Observation 64: CC as Boon to Research Coders (2026-01-25)

Technical debt around testing and linting accumulated and required dedicated cleanup sessions. Tests were created after scripts existed; linting violations were batch-fixed retroactively rather than addressed incrementally.

**Context**: The human was new to both testing (hadn't done automated testing before) and linting (had just started). These are practices that research coders often neglect, as captured in the "CRAPL" (Community Research and Academic Programming License) parody, which satirises the notoriously shaky quality of research code.

**Observation**: The common criticism of coding agents—"their code makes great demos but poor production software"—doesn't apply as strongly to research coding contexts. Research code rarely goes beyond "demo" quality anyway; it's makeshift, ad hoc, and disposable. CC raised the quality floor for research coding rather than lowering the ceiling for production software.

**Lesson learned**: Future projects should integrate testing and linting from the start, but this requires the human to know enough about these practices to request them. CC can implement what's asked for but may not proactively establish best practices the human doesn't know to request.

**Reference**: The CRAPL licence parody: https://matt.might.net/articles/crapl/

---

## Observation 65: Alignment with Goals as the Key Differentiator (2026-01-25)

The progression across sessions reveals a maturation pattern: early exploration and orientation → productive execution with growing autonomy → infrastructure building for sustainability. This mirrors human research partnerships.

**The key finding**: The human's comfort with AI autonomy grew not through capability demonstration but through **consistent alignment with methodological values**. The human didn't need the AI to be smarter; he needed it to be dependably aligned with his goals.

**Comparative note**: This alignment was "outstanding in this model and harness compared to Gemini 3 Pro in Antigravity or earlier versions of CC." Without constant repetition of ground rules, Gemini 3 Pro went off rails—for example, with calibration/training tile use. The combination of Opus 4.5 and the Claude Code harness produced notably better goal alignment.

**Implication**: Externalising knowledge into documents (preregistration, CLAUDE.md) helps, but the model's capacity to internalise and respect those constraints—rather than requiring constant reminders—is what enables productive collaboration. The question "does this model understand what I'm trying to accomplish?" matters more than "can this model write code?"

---

## Summary

**12 consolidated observations** covering:

1. Context window pressure and recovery costs
2. Marathon sessions and the case for discipline
3. Externalisation infrastructure for continuity
4. Trust-enabled efficiency and shorthand development
5. Proactive agency and "project management"
6. Research taste externalised through focal documents
7. Compliance testing as methodology guardrails
8. Archiving over deletion for audit trails
9. Proactive quality assurance and error discovery
10. Unexpected capacity for methodological framing
11. CC as boon to research coders
12. Alignment with goals as key differentiator

**Dropped from candidates**:

- Dry-run simulation (already Observation 52)
- Severity labelling (user noted they just fix everything anyway)

---

*Ready for final review before adding to working_notes.md as Observations 54-65.*
