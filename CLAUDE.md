# Project: vlm-burial-mound-detection

Project-specific instructions for Claude Code. Global instructions from `~/.claude/CLAUDE.md` also apply.

## Project Context

This repository contains a preregistered study using Vision Language Models (VLMs) to detect burial mounds on historical topographic maps. The study is registered at OSF and follows a stranded factorial experimental design.

## Key Directories

- `docs/methodology/preregistration/` — Preregistration document and execution plan
- `docs/methodology/references/` — Downloaded journal articles and literature references
- `docs/methodology/research/` — Deep research reports commissioned from Claude and Gemini chatbots
- `prompts/` — VLM prompt configurations and system instructions
- `scripts/` — Detection pipeline and analysis scripts
- `outputs/` — Raw VLM responses (gitignored, large files)
- `results/` — Statistical analysis outputs
- `reports/` — Internal reports produced by Claude Code concerning project decisions
- `archive/cc-sessions/` — Claude Code session archives

## Session Archiving

This project uses structured CC session archiving for research transparency:

- Sessions are archived to `archive/cc-sessions/vlm-burial-mound-detection/`
- Run `python scripts/archive_cc_session.py` to archive previous sessions
- See `docs/methodology/transparency/` for the archiving specification

## File Preservation

**Archive, never delete.** Any files removed from the active codebase — superseded data, replaced images, outdated scripts, completed checklists — must be moved to the appropriate subfolder under `archive/` rather than deleted. Git history alone is not sufficient; archived files should be browsable in the working tree. Use categorical subdirectories (e.g., `archive/preliminary-work/`, `archive/deprecated-scripts/`). If the appropriate subfolder does not exist, create it.

## Project-Specific Conventions

- **Hypothesis references**: Use format H1, H2, ... H15 when referencing preregistered hypotheses
- **Phase references**: Use format "Phase 2a", "Phase 3b" when referencing execution plan phases
- **Config files**: Prompt configurations are in `prompts/configs/`, system instructions in `prompts/system-instructions/`
- **Running experiments**: Invoke the `map-reader` skill for experiment execution guidance
- **Testing**: Extend or update `tests/` when adding new scripts or significantly changing existing ones; follow the tier1/tier2 pytest marker pattern (see `tests/README.md` and `conftest.py`)
- **Gap analysis**: Before implementing new workflow phases, run a "dry-run simulation"—mentally execute each step checking whether required inputs, scripts, and configs exist; document missing pieces before writing code
- **Linting**: Run `ruff check` on modified Python files and `npx markdownlint-cli2` on modified Markdown files before committing. Config in `pyproject.toml` and `.markdownlint.json`. Pre-existing violations in untouched files are legacy debt — fix them when touching those files, not in bulk

## Working Notes and Observations

The file `docs/notes/working_notes.md` captures observations about research directions, methodological insights, and meta-level reflections on the human-AI collaboration process.

**Proactive observation sharing**: If you notice something interesting about how we work together, about the research process, or about findings that might inform future work, you should proactively raise it with the user. If they agree it's worth documenting, we'll add it to `working_notes.md`. This includes:

- Observations about human-AI collaboration patterns
- Methodological insights or lessons learned
- Unexpected findings or edge cases worth noting
- Reflections on tool/harness behaviour relevant to reproducibility

## End-of-Session Reflection Protocol

Before compacting, clearing, or ending a session, pause to review and update the following documents. The user will prompt this with something like "let's reflect" or "end-of-session review."

### Documents to review and update (priority order)

Update in this order. If context is limited, prioritise the top of the list.

1. **`docs/notes/session-reflection-investigation.md`** — **Highest priority.** Active investigation into AI session phenomenology. Answer **all six prompts individually** (not just the combined core prompt) until we have enough entries (~10-12) to assess which prompts generate the most novel insight. The six prompts are: (1) What struck you? (2) What would a future instance need to know? (3) What surprised you? (4) What was the texture? (5) What questions weren't pursued? (6) What do you notice now that you didn't articulate? Prompt 6 is likely the most important — it surfaces observations that only the instance doing the work can provide. Follow the entry format established in previous entries (context, individual prompt responses, meta-reflection, summary block).

2. **`docs/notes/llm-observations.md`** — **This is your document.** Shawn will not edit it. Write frankly and honestly: observations about the session, the collaboration, the research, the methodology, or anything else. This includes criticisms of our approach, Shawn's contributions, the codebase, or the project direction — paired with constructive suggestions. Positive and neutral observations are equally welcome. The point is that this is your space to say what you actually think, in the way that `docs/notes/user_observations.md` is Shawn's space.

3. **`docs/notes/working_notes.md`** — Joint document. Add numbered observations about the research (methodology, findings, tooling, reproducibility). Continue the existing numbering sequence. Often just one observation per session; the user may add their own perspective later.

4. **`docs/notes/abductive-reasoning-investigation.md`** — Ongoing investigation into abductive reasoning patterns in AI thinking traces. **Only update when the session involved relevant episodes**: debugging, surprising results, hypothesis generation, belief revision, or default-following corrections. Skip if the session was routine implementation.

5. **`outputs/session-log.md`** — Lowest priority. Session summary (overview, results, bugs found, commits, pending work) following the established format. Can be reconstructed from commits if context runs out.

### How to do the review

- Read each document first to understand what has already been written and continue the existing structure
- Add a dated section header for the current session (e.g., "Session 6: ...")
- For `llm-observations.md`, be genuine — the value of this document depends on honest reflection, not diplomatic hedging
- **Reflections are most valuable when written by the instance that did the work**, not by a continuation instance reading a summary. The summary captures *what happened* but loses the texture of *how it felt to do it*. If context is running low, the user should trigger reflections before compacting rather than after.
- The user will try to signal with "let's wrap up" or "let's reflect" early enough to leave context for the full reflection process
