# AB+ agent briefs

Shared briefs for the three Large Language Model (LLM) roles in the
Annotated Bibliography Plus (AB+) pipeline (`scripts/ab_plus/`;
run card `planning/ab-plus-run-card-2026-08-30.md`). The
deterministic stages (resolve, extract, gate, quote check, render) are
CLI subcommands; these briefs drive the three agent stages, one fresh
agent per source per stage:

| Stage | Brief | Reads | Writes |
|---|---|---|---|
| draft | `drafter-brief.md` | schema, one exemplar, own page cache | `_work/<citekey>.entry.json` |
| verify | `verifier-brief.md` | entry + page cache (never the drafter's reasoning) | `_work/<citekey>.verdict.json` |
| edit | `editor-brief.md` | drafter brief, entry, verdict, page cache | `_work/<citekey>.entry.json` (in place) |

Dispatch messages are one or two lines: "Follow the brief at
`prompts/ab-plus/<role>-brief.md` exactly. Your citekey: X. Cluster:
Y. Scratch dir: Z." plus any per-source caution (a cache provenance
note, a known pagination quirk). Agents run at the Opus tier per the
subagent model policy; the render step stamps the requested model.

The pilot (25 sources, 2026-08-30) ran these briefs from a session
scratchpad; they were promoted here on 2026-09-02, extended with the
tail's positioning clusters, the per-citekey scratch rule, and the
overflow-notes convention, before the remaining 88 sources ran.
