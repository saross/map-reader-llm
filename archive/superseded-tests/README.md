# Archived superseded tests

One-off prompt/proposer test runs, superseded by later production runs and
preserved here per the project's "archive, never delete" policy.

| Dir | What it was | Superseded by | Archived |
|-----|-------------|---------------|----------|
| `propose-brief-v1-test/` | First test of the `propose_brief` prompt (v1) | `propose_brief_v2` → `e47-propose-brief` | 2026-04-21 (Session 92) |
| `v2-proposer-test/` | Single-pass test of `propose_brief_v2.md` (487 items, 2026-04-08, gemini-3-flash) | the production `outputs/h11/e47-propose-brief` run | 2026-05-30 |

`v2-proposer-test/` was moved out of `outputs/h11/` in Session 92 (commit
`43895be1`) and archived here on 2026-05-30 during the run-registry fan-out
review, once confirmed it is a superseded one-off with no live (non-doc)
references. Both are exploratory prompt tests, not registry runs.
