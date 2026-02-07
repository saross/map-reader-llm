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

## Research Finding Calibration

**Flag surprising results.** When analysis produces results that contradict expectations, hypotheses, or prior experience, proactively raise this with the user rather than accepting the output at face value. Surprising research findings are as important to flag as implementation bugs — both require human judgement to interpret.

Examples of findings worth flagging:

- Results that contradict preregistered hypotheses (e.g., H1 predicts X > Y but data shows Y > X)
- Metrics that diverge from prior experience (e.g., "this F1 seems lower/higher than expected")
- Patterns that violate domain expectations (e.g., "all conditions clustering when they should diverge")
- Effect sizes or directions that seem implausible given the experimental design

The appropriate response to a surprising finding is not to explain it away or accept it uncritically, but to:

1. Flag the surprise explicitly ("This result contradicts H1 / prior experience / expectations")
2. Verify the data pipeline is correct (are we analysing what we think we're analysing?)
3. If the pipeline is correct, document the finding as a genuine scientific result worth explaining

This project has repeatedly benefited from human domain calibration catching anomalies that automated checks missed. The same calibration applies to research findings, not just implementation correctness.

## Working Notes and Observations

The file `docs/notes/working_notes.md` captures observations about research directions, methodological insights, and meta-level reflections on the human-AI collaboration process.

**Proactive observation sharing**: If you notice something interesting about how we work together, about the research process, or about findings that might inform future work, you should proactively raise it with the user. If they agree it's worth documenting, we'll add it to `working_notes.md`. This includes:

- Observations about human-AI collaboration patterns
- Methodological insights or lessons learned
- Unexpected findings or edge cases worth noting
- Reflections on tool/harness behaviour relevant to reproducibility

## Experiment Execution

- **Never hard-code worker counts in study YAML files.** Parallelisation is the job of the TPM governor in `4_detect_mounds_batch.py`, not the study definition. When running experiments, pass `--workers N` via the CLI to set concurrency; the governor will dynamically manage throughput within API limits. Study YAML files should set `workers: 1` as the safe default and let the operator choose the appropriate parallelism at runtime.

## Google API Quota Notes

- **Gemini API daily quotas reset at midnight US Pacific Time** (midnight PT = 7:00 PM AEDT / 6:00 PM AEST next day)
- The user is in Sydney, Australia — plan experiment runs around the local evening reset window
- Free-tier and pay-as-you-go rate limits (Tokens Per Minute (TPM), Requests Per Minute (RPM)) are rolling and do not have a fixed reset time, but daily quotas do

## End-of-Session Reflection

Invoke the `/reflect` skill to run the end-of-session reflection protocol. The user will prompt with "let's reflect", `/reflect`, or similar. Reflections are most valuable when written by the instance that did the work — trigger before compacting rather than after.
