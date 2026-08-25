# Project: map-reader-llm

Claude Code entry point. It carries only Claude-specific mechanisms.

This project's shared policy — context, directory map, conventions,
research-finding calibration, document revision policy, compute location,
quota notes — lives in a harness-neutral file that every agent working here
follows, and is imported here so it loads at session start:

@docs/agent-guidance.md

Project policy changes go in that file, not in this one. Global instructions
from `~/.claude/CLAUDE.md` also apply.

## Claude-specific mechanisms

- **Running experiments**: invoke the `map-reader` skill for experiment
  execution guidance.
- **Phase-boundary check**: invoke the `/phase-gate` skill before committing
  API spend or compute to a new experimental phase (rationale and the list
  of what counts as a phase boundary: `docs/agent-guidance.md`).
- **End-of-session reflection**: invoke the `/reflect` skill. The user will
  prompt with "let's reflect", `/reflect`, or similar. Reflections are most
  valuable when written by the instance that did the work — trigger before
  compacting rather than after.

## Session Archiving

This project uses structured CC session archiving for research transparency.
**Amended 2026-08-22** — the in-repo `archive/cc-sessions/` location this
section previously documented no longer exists (contents resolved into the
consolidated store, SHA-256 parity verified 2026-05-21; the migration was
minuted only in a `.gitignore` comment, which is why stale pointers
survived here):

- Sessions are archived automatically (SessionEnd/PreCompact hooks) to the
  machine-local mirror `~/cc-archives/`, converged daily with the canonical
  union on rpi-server and an offsite R2 backup. Store roles:
  `~/personal-assistant/data/global-claude-md/network-resources.md`.
- ⚠ This project's sessions live under TWO archive names: `map-reader-llm`
  (canonical — Shawn's ruling 2026-08-22) and `vlm-burial-mound-detection`
  (alias; this file's former `# Project:` line forked the archive).
  **Completeness questions must read both** — the alias map is
  `~/personal-assistant/data/config/project-identities.json`.
- For provenance or audit work, read the ARCHIVE, never the live
  `~/.claude/projects/` store (machine-partial by construction).
- See `docs/methodology/transparency/` for the archiving specification
  (amendment note at the top of the specification records this change).
