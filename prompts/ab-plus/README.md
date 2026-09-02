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

## Dispatch discipline (2026-09-03, from claude-obs 86)

- The orchestrator's dispatch line carries the citekey, the cluster,
  and the cache notes — nothing that characterises the source. The one
  time it did ("a COS working paper" for pu_designing_2019) the error
  reached three agents before a drafter caught it.
- Paste the gate's content notes (`cli.py gate --citekey X`) into the
  drafter and verifier dispatches verbatim: cover-sheet and
  author-manuscript (page mapping), neighbour-contamination and
  trailing-text (attribute by reading), caption-only-table (render
  before citing), sections-empty (reconstruct locators).
- When an author of the source is an author of the citing paper, say
  so in the verifier dispatch: the self-flattering drift was strongest
  there.
- Length limits are targets, not gates (PI ruling 2026-09-03).
