# Project: map-reader-llm

Codex entry point. It carries only Codex-specific mechanisms.

At the start of a substantive session, read `docs/agent-guidance.md`. It holds
this project's shared policy: context, directory map, conventions,
research-finding calibration, document revision policy, compute location, and
quota notes. It applies to every agent working here. Global instructions from
`~/.codex/AGENTS.md` also apply.

Project policy changes go in `docs/agent-guidance.md`, not in this file.

## Codex-specific mechanisms

- **Running experiments:** no Codex-native `map-reader` skill is installed.
  Re-read the relevant preregistration execution plan and current pipeline or
  runbook documentation, then perform the shared dry-run simulation before
  editing or launching a new phase.
- **Phase-boundary check:** no Codex-native `/phase-gate` skill is installed.
  Before committing Application Programming Interface (API) spend or compute,
  manually re-check inputs, scripts, configuration, carry-forward assumptions,
  aggregate cost and call count, concurrency, and capacity. Surface gaps and
  obtain the global API-call approval before launch.
- **Ownership:** `CLAUDE.md` and `.claude/` are Claude-owned and read-only to
  Sol. `docs/agent-guidance.md` is shared project policy.
