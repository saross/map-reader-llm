# Project: vlm-burial-mound-detection

Project-specific instructions for Claude Code. Global instructions from `~/.claude/CLAUDE.md` also apply.

## Project Context

This repository contains a preregistered study using Vision Language Models (VLMs) to detect burial mounds on historical topographic maps. The study is registered at OSF and follows a stranded factorial experimental design.

## Key Directories

- `docs/methodology/preregistration/` — Preregistration document and execution plan
- `prompts/` — VLM prompt configurations and system instructions
- `scripts/` — Detection pipeline and analysis scripts
- `outputs/` — Raw VLM responses (gitignored, large files)
- `results/` — Statistical analysis outputs
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
