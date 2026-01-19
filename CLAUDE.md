# Project: vlm-burial-mound-detection

Project-specific instructions for Claude Code. Global instructions from `~/.claude/CLAUDE.md` also apply.

## Project Context

This repository contains a preregistered study using Vision Language Models (VLMs) to detect burial mounds on historical topographic maps. The study is registered at OSF and follows a stranded factorial experimental design.

## Key Directories

- `docs/methodology/preregistration/` — Preregistration document and execution plan
- `docs/methodology/articles/` — Downloaded journal articles and literature references
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

## Project-Specific Conventions

- **Hypothesis references**: Use format H1, H2, ... H15 when referencing preregistered hypotheses
- **Phase references**: Use format "Phase 2a", "Phase 3b" when referencing execution plan phases
- **Config files**: Prompt configurations are in `prompts/configs/`, system instructions in `prompts/system-instructions/`

## Working Notes and Observations

The file `docs/working_notes.md` captures observations about research directions, methodological insights, and meta-level reflections on the human-AI collaboration process.

**Proactive observation sharing**: If you notice something interesting about how we work together, about the research process, or about findings that might inform future work, you should proactively raise it with the user. If they agree it's worth documenting, we'll add it to `working_notes.md`. This includes:

- Observations about human-AI collaboration patterns
- Methodological insights or lessons learned
- Unexpected findings or edge cases worth noting
- Reflections on tool/harness behaviour relevant to reproducibility
