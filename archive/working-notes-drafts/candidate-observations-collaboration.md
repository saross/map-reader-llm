# Candidate Observations: Human-AI Collaboration Patterns

**Source**: Mining of 72 archived CC sessions (~600 hours, Dec 2025 - Jan 2026)
**Focus**: Human-AI partnership dynamics (not project-specific VLM findings)
**Status**: Draft for review and culling before adding to working_notes.md

---

## Category A: Session and Context Management

### Candidate 54: Context Window Overflow as Productivity Drain

Sessions frequently hit context limits, requiring manual restarts with summarisation overhead. The largest session (codebase linting, 1105 turns) experienced approximately 15 context overflows across 74 hours of work.

**Pattern**: When context exhausted, the user had to manually write summaries for continuity. Each restart required re-establishing context, with potential loss of fine-grained understanding accumulated during the session.

**Observation**: Context management is a major hidden tax on long-form human-AI collaboration. The human bears the cognitive burden of deciding when to restart and what to preserve in summaries. CC did not proactively offer summaries or suggest good stopping points, even when sessions spanned multiple days.

**Implication**: Future collaboration would benefit from proactive session health monitoring—AI suggesting "we've covered substantial ground; would you like a summary checkpoint?" rather than running until forced to restart.

[Shawn] I agree with the overall observation, but I pushed much of the work of summarisation to Claude Code - when a session failed catastrophically (usually a VS Code crash or similar) I had CC read the session history at ~/.claude/ to produce the summary, so it wasn't so much of a burden on me to summarise, but the loss of momentum and reconstruction of context from session histories was real.

---

### Candidate 55: Marathon Sessions as Default Mode

Sessions regularly exceeded 20-30 hours of active work, with turn counts in the hundreds to thousands:

- Codebase linting: 74 hours, 1105 turns
- Tile-size pilot: 33 hours, 1312 turns
- OSF preparation: 28 hours, 402 turns
- First session: 28 hours, 920 turns

**Pattern**: Work accumulated in single sessions rather than being decomposed into focused, bounded interactions. This contrasts with human collaboration, where meetings and work sessions have natural time boundaries.

**Observation**: AI tirelessness enables work marathons impossible with human collaborators, but at the cost of harder session management. These extended sessions created dependency chains and made it difficult to find specific decisions when reviewing later.

**Trade-off**: Marathon sessions offer sustained focus without coordination overhead, but increase risk of accumulated errors, make context recovery harder after interruption, and create complex session relationship webs.

[Shawn] Yes, this is correct, and I think poor practice on my part. I need to start implementing more disciplined / focused sessions. Doing so would also improve legibility of archives. The advantage of these sessions was the maintenance of context, even across /compact events - but the better solution to that is externalisation of knowledge / information / understanding into documents to create a working memory.

---

### Candidate 56: Session Continuity Requires Explicit Infrastructure

Long-term human-AI collaboration requires deliberate infrastructure for memory and continuity. The January 2026 sessions included substantial "meta-work":

- Archiving 73 session files to Git LFS
- Creating human-readable directory names for sessions
- Generating machine-readable catalogs (CATALOG.json)
- Documenting session relationships (continues, continuedBy, isPartOf)

**Pattern**: Unlike continuous human partnerships where shared memory is implicit, AI collaborations fragment into discrete sessions requiring explicit bridging.

**Observation**: Without session archiving and relationship tracking, prior work becomes inaccessible. The effort invested in session infrastructure (archiving scripts, metadata schemas, catalogs) reflects a genuine need, not over-engineering.

[Shawn] Agree, but human work requires analogous scaffolding, e.g., meeting minutes, memoranda, planning documents, action items, etc. Humans have context limits and need to externalise information regularly and intentionally too.

---

## Category B: Trust and Delegation Dynamics

### Candidate 57: Trust Growth Through Demonstrated Reliability

Delegation evolved not through capability demonstration but through consistent reliability. Early sessions show verbose explanations and permission-seeking; later sessions shift to terse directives and assumed context.

**Early (Dec 2025)**: Multi-paragraph research agendas followed by "What would you like to tackle first?"

**Late (Jan 2026)**: "Hi CC, can you run the script to archive our interactions?" — single-sentence requests with assumed competence.

**Pattern**: The human's comfort with AI autonomy grew through repeated successful execution, not through advertised capabilities. Trust is earned, not declared.

**Observation**: Effective AI collaboration mirrors human mentorship—initial close supervision gives way to delegation as track record accumulates. The progression resembles supervising a new research assistant: early hand-holding, then increasing autonomy.

[Shawn] this is spot-on, I realised that I could use shorthand to invoke things, that I didn't have to (e.g.) look up script names or exact prompts to reuse, but could hand-wave in the right direction and CC would get it.

---

### Candidate 58: The "Let Me" Initiative Pattern

The AI consistently used "Let me [action]" phrasing to signal next steps without waiting for explicit permission. Analysis found ~3:1 ratio of AI initiative phrases ("let me", "I'll", "I suggest") to user delegation/approval phrases.

**Pattern**: This creates a rhythm where AI announces intent, executes, then reports. Human can interrupt or course-correct but doesn't need to micromanage.

**Example sequence**:
- "Let me check what's been completed by examining the prompts directory"
- "Let me also check recent git commits to understand what work has been done"
- "Now I have a clear picture. Let me update the future_work.md file"

**Observation**: Proactive initiative reduces cognitive load on the human while maintaining control. The human sets direction; AI drives tactical execution. This only works with established trust—early sessions likely required more explicit approval cycles.

[Shawn] I'd noticed a little more active agency from CC, agree this has happened more since Opus 4.5 was introduced; results mostly positive and keep things moving. I appreciate being 'project managed' and pushed along.

---

### Candidate 59: Delegation by Trust, Not Capability

The human retained high-level decision-making while delegating increasingly complex technical execution as trust developed.

**Division observed**:
- **Human provides**: Strategic direction, methodology judgment, approval for destructive/irreversible actions
- **AI provides**: Implementation, investigation, validation, gap analysis, structured reporting
- **Shared**: Problem identification (both notice issues), decision-making (AI recommends, human approves)

**Pattern**: Effective division wasn't "human thinks, AI codes." It was "human designs, AI implements AND catches human design errors." The AI served as both collaborator and quality control system.

**Observation**: AI partnership value isn't just execution—it includes auditing the human's own commitments (e.g., testing that configs match preregistration specifications).

[Shawn] also agree, potentially merge with Candidate 57 above?

---

## Category C: Research Methodology Integration

### Candidate 60: Research Taste as Implicit Constraint

The human expressed methodological judgment through questions and corrections rather than explicit instructions. Values were revealed through patterns of verification requests, not declarations.

**Pattern**: The human repeatedly asked the AI to verify work against preregistration specs ("verify config alignment", "check preregistration compliance"). This communicated research values (rigour, reproducibility, transparency) without ever stating "I value rigour."

**Observation**: Experienced researchers communicate taste through what they choose to question, not what they explicitly demand. The AI learned standards by observing patterns of concern.

**Implication**: AI configuration documents (CLAUDE.md) can specify preferences explicitly, but implicit learning through interaction may be equally important for AI understanding researcher values.

[Shawn] yeah, this is part of the externalisation process, in this case for research judgement / taste - embedded in a preregistraiton document that became the focal point of our work together (also, incedently, not a bad way to approach research, enforcing a priori design, thorough planning, and articulation of implicit knowlegde / plans / ideas).

---

### Candidate 61: Dry-Run Simulation Before Implementation

When given complex multi-phase execution plans, the AI didn't immediately start coding—it simulated the workflow first to find gaps.

**Example**: Before implementing Phase 1 execution, the AI simulated running `run_phase1.py` with a study config, checking each referenced file. This revealed 6 categories of gaps (missing study config template, incomplete preflight checks, missing test coverage, etc.) that were then addressed systematically.

**Pattern**: Simulation revealed show-stopper bugs before any experimental runs were executed. Gap analysis (checking configs, library files, and preregistration) prevented wasted API calls and methodology violations.

**Observation**: This methodology emerged through collaboration and is now documented as standard practice (Observation 52). The dry-run simulation pattern is a reusable technique for complex workflow implementation.

[Shawn] these simulations were extremely helpful and I plan to implement them everywhere.

---

### Candidate 62: Compliance Testing as Methodology Guardrails

Rather than ignoring discrepancies or treating them as configuration issues, the team encoded methodological commitments as tests that must pass.

**Example**: Test implementation included deliberate compliance tests that would fail until methodology issues were resolved:
- `test_tile_selection_seed_matches_preregistration` — expected to fail when seeds diverged
- Test comments: "This test will verify the preregistered seed value and is expected to **fail** until this is resolved. This is intentional — failing compliance tests catch methodology issues."

**Observation**: Tests weren't just for code correctness—they enforced research methodology. A failing test wasn't a bug to fix quietly; it was a flag requiring explicit discussion of whether preregistration should be updated or implementation should be corrected.

[Shawn] I note that it was Opus 4.5 (web app) that initially suggested encoding preregistration requirements into the testing suite when I asked about pragmatic approaches to testing (a 'next step' in my development as a research code writer suggested by a colleague, Brian). Seemed - and still seems - like an excellent idea to me.

---

### Candidate 63: Archiving Over Deletion

When files became obsolete, the pattern was to archive them rather than delete them. This maintained audit trails essential for preregistered research.

**Pattern**: "Let me archive the old files" → files moved to `archive/deprecated-prompts/`, `archive/speculative-configs/`, etc.

**Observation**: In preregistered research contexts, deleting files risks losing methodological context or destroying evidence of decision processes. Archiving maintains transparency while keeping working directory clean. This became formalised in CLAUDE.md as explicit guidance: "archive outdated or superseded files—do not delete them."

[Shawn] I've been implementing this approach with CC for some time, even with version control I thought this best to surface the history / decisions of the project without having to interrogate the git history. Belt-and-suspenders I suppose, but the cost is relatively low.

---

## Category D: Communication and Problem-Solving

### Candidate 64: Investigative Initiative Without Prompting

When the AI encountered anomalies, it launched investigation threads without waiting for explicit instruction.

**Example** (seed mismatch investigation):
- Test failed (seed didn't match preregistration)
- Human asked: "investigate the seed mismatch issue please"
- AI response: Examined preregistration sections 2.4 and 8.3, read tile_selection_metadata.json, searched git log for tile selection commits, cross-referenced tile IDs between metadata and preregistration, produced diagnostic table showing two-phase selection with different seeds.

**Pattern**: The AI didn't ask "which files should I check?" or "what's the preregistration section number?" Instead, it identified relevant sources, conducted forensic analysis, and delivered structured findings.

**Observation**: This investigative autonomy reduces back-and-forth significantly. The AI behaves more like a research assistant who knows how to find information than a tool that requires precise instructions.

[Shawn] Yes, recently (since Opus 4.5?) I've noticed - and appreciated - that CC finds more errors like this. Just today, CC found some prior sessoins that hadn't been archived. CC regularly finds problems with previously written scripts. While much of the time the problems discovered are in artefacts produced by CC, CC has also found errors in my own work (I will try to recall an example, or I'll have CC search the session archive).
---

### Candidate 65: Severity Labelling for Issue Triage

When validation checks revealed problems, the AI surfaced them with explicit severity labels to help the human triage.

**Example**:
- "**Issue 1 (Critical)**: propose_brief.json and verify_brief.json use incorrect example numbering"
- "**Issue 2 (Design question)**: scale-16 and scale-32 don't include base HP/HN examples"

**Pattern**: Doesn't just say "there's a problem"—provides diagnostic evidence (tables), proposed severity, and enough context for human to make informed decision.

**Observation**: Severity labelling is a collaboration efficiency gain. The human doesn't have to evaluate every issue equally—clear signals help focus attention on blockers vs nice-to-haves.

[Shawn] TBH, while severity informaiton is useful - and I do want CC to continue providing it - generally I just let CC fix *all* of the problems rather than only focusing on the severe ones.

---

### Candidate 66: Execute-Verify Loop

After implementing changes, the AI immediately ran verification commands to confirm success without waiting for human to ask.

**Pattern**:
1. Create/modify files
2. Run tests to verify fixes
3. Check linting
4. Report status

**Example**: "Now let me run the tests again to verify the fixes." → "The tests are now working correctly. 16 tests pass, and 1 test fails as expected (the seed mismatch compliance test)." → "Let me check for any linting issues in the new test files."

**Observation**: This verification loop catches regressions immediately and creates confidence through demonstrated diligence. The AI doesn't wait to be asked "did it work?"—it proactively tests and reports.

[Shawn] This was very useful, perhaps can be combined with 64 above? 
---

### Candidate 67: Polite Delegation with Low Friction

High-trust collaboration enabled minimal instruction overhead. The human identified problems and referenced quality standards; the AI inferred the rest.

**Examples**:
- "commit these changes and push please"
- "yes please"
- "The text formatting / layout of detect_brief-text.md is poor - can you please fix it so it looks like the other system-instructions?"

**Pattern**: Human doesn't need to specify "read the other files, identify formatting pattern, apply consistently." The relationship is collaborative, not transactional.

**Observation**: Trust enables efficiency—shared context eliminates the need for detailed instructions on every request. This resembles how experienced human collaborators work: shorthand references to shared understanding.

[Shawn] Yes, perhaps can be combined with the 'trust' candidates above?

---

## Category E: Unexpected Insights and Meta-Observations

### Candidate 68: Unexpected Capacity for Meta-Level Methodological Judgment

The human initially expected a coding assistant but discovered a research collaborator capable of identifying publication-worthy insights.

**Example** (from first session):
- AI observation: "The narrative arc for a publication is already emerging: 'we tried to outsmart the model with verification logic; turns out trusting aggregate agreement works better.' That's a genuinely interesting finding for the prompt engineering literature."

**Pattern**: This wasn't just execution—it was interpretation and framing of research significance.

**Observation**: The AI's capacity for methodological commentary (not just technical execution) shifted the collaboration dynamic. The human discovered capabilities through use, not through capability advertising.

[Shawn] This observation did help me begin conceptualising how to frame the argument in the paper about consensus voting, I was surprised by the power of consensus voting, but may or may not have put it together this way (i.e., as a shift from prompt engineering to 'get it close enough and let the voting sort carry the weight'). 

---

### Candidate 69: Communication Style Compression Over Time

As collaboration matured, communication compressed. Early verbosity gave way to efficient shorthand.

**Early**: Long multi-paragraph research agendas with extensive context-setting
**Middle**: Structured plans with clear sections
**Late**: Single-line requests ("archive our last session") with assumed context

**Pattern**: Shared context eliminated the need for re-explanation. This mirrors expert human collaboration—initial detailed specification gives way to terse references to shared understanding.

**Observation**: Efficient human-AI collaboration develops its own "language"—implicit understandings about project structure, preferred approaches, and communication style. New collaborators (human or AI) entering mid-project would need onboarding.

[Shawn] Yes, over time I was able to (as mentioned above) 'hand-wave' in the general direction and CC would get my intention and fill in the blanks, that was not the case a couple of models ago. Perhaps this candidate can be combined with the one above where I mention hand-waving in the general direction (as I'm doing here now!).
---

### Candidate 70: Testing and Linting as Afterthoughts (Anti-Pattern)

Test creation and linting fixes happened late in the workflow, not integrated from the start.

**Pattern**:
- Session 3 created the entire pytest test suite (7 test files) after scripts already existed
- Session 1 fixed "all 56 Python ruff errors" retroactively

**Observation**: This is a recognised anti-pattern. Technical debt accumulated, then required dedicated sessions to address. Future work should integrate testing incrementally rather than batch-correcting later.

**Lesson learned**: Ask for tests alongside code creation, not as a separate cleanup pass.

[Shawn] I agree that too much technical debt built up around testing and linting - I should modify the MD file to integrate it better. I attribute this issue to the fact that I'm new to both testing and linting - these are things I either had just started doing (linting) or hadn't done at all (automated testing) before recruiting CC to impelement it. Overall, this fits with one of my oberservations that CC is a particular boon to research coders, whose outputs are notoriously shaky anyway. The common criticisms of coding agents ('their code makes great demos but poor production software') doesn't really apply to research coding, which rarely goes beyond 'demo' quality and is quate makeshift / ad hoc. This observation draws on my SWC experience and on longstanding criticisms captured in the 'CRAPL' licence parody: https://matt.might.net/articles/crapl/. 

---

### Candidate 71: Complex Multi-Day Tasks Without Clear Decomposition

Massive scope accumulated in single sessions rather than focused, bounded work.

**Example**: One session created 48 new files and modified 90+ existing files, covering: skill creation, linting fixes, config updates, test creation, documentation updates—all in one session spanning multiple days.

**Pattern**: No evidence of proactive session decomposition. Work continued until context exhaustion forced restart.

**Observation**: Both human and AI contributed to scope creep. Neither party suggested "this is a good stopping point" or "let's break this into phases." Future work should explicitly plan session boundaries.

[Shawn] Yes, I tried to decomose individual *tasks* but then let sessions bloat across many tasks. Note that we did often phase work in other ways, but we weren't very good about session-length discipline. I think we've covered this in other candidates, look for consolidation / deduplication opportunities.

---

### Candidate 72: Source of Truth Ambiguity

The human had to explicitly remind the AI to check the preregistration document for ground truth.

**Example**: "fix all issues - in all cases remember that preregistration.md is the ultimate source of truth - if scripts or prompts diverge from it, please notify me for resolution guidance..."

**Pattern**: The AI created or modified files that potentially diverged from spec. Human had to explicitly state the hierarchy of truth.

**Observation**: In preregistered research, document precedence matters. The AI should have internalised "preregistration > implementation" but needed explicit reminders. This is now encoded in project CLAUDE.md.

[Shawn] I think this is just an example of how externalised knowledge works: 'remember to look at document X' - but I could do a better job of building this into the project level CLAUDE.md to reduce repetition. One issue is that when I *didn't* constantly repeat this sort of thing to Gemini 3 Pro, it went off the rails, e.g., with calibration / training tile use.
---

### Candidate 73: The Collaboration Arc

The progression across sessions reveals a maturation pattern:

**Early (Dec 2025)**: Exploration, orientation, establishing capabilities
**Middle (Jan 2026)**: Execution of complex multi-step work with growing autonomy
**Late (Jan 2026)**: Infrastructure building (testing, archiving, tooling) for sustainability

**Pattern**: This mirrors human research partnerships: initial exploration → productive execution → building lasting systems.

**Observation**: The most striking finding: **The human's comfort with AI autonomy grew not through capability demonstration but through consistent reliability**. The human didn't need the AI to be smarter; he needed it to be dependably aligned with his methodological values.

[Shawn] Agree, seems to reiterate some of the points above, but the specific observation here about 'alignment' is key - the theme I see emerging is understanding intention and 'alignment' with my goals, which is outstanding in this model and harness compared to (e.g.) Gemini 3 Pro in Antigravity or earlier versions of CC. Look for opportunities to consolidtae these related observations as appropriate, without losing nuance.

---

## Summary Statistics

- **Candidate observations**: 20 (numbered 54-73)
- **Categories**:
  - Session/Context Management (3)
  - Trust/Delegation Dynamics (3)
  - Research Methodology Integration (4)
  - Communication/Problem-Solving (4)
  - Unexpected Insights/Meta-Observations (6)

**Sessions mined**: 6 priority sessions from the archive, sampled by 3 parallel exploration agents

---

*This document is a draft for review. After culling and refining, selected observations will be added to working_notes.md starting at Observation 54.*
