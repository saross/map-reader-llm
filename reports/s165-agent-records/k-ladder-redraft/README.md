# K-ladder outcome redraft (PR #52, row `k-ladder-2026-09-12`)

> **Last revised**: 2026-10-18 (original publication). See
> [§ Changelog](#changelog) for revision history.

Review packet for the redrafted register outcome of `k-ladder-2026-09-12`
(the K-ladder review), the one row of the S164 restatement pass whose
drafted text the Principal Investigator (PI) sent back for a redraft in
Session 165. The other fourteen drafted outcomes were approved and applied
in `c24d5a04f`.

- Executed by: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`): the main Session 165 session and three Opus
  sub-agents (a verifier of all fifteen drafts, a redraft agent, and a
  verifier of the redraft's first version). All read-only on the
  repository; no model Application Programming Interface (API) call.
- Date: 2026-10-18 (UTC).

## Files

| File | What it is |
|---|---|
| `k-ladder-redraft-v2.md` | The redraft under review: the outcome text (§ 1), a word diff against the signed text (§ 2), every change with its source (§ 3), recounts (§ 4), decisions for the PI (§ 5), attestation corrections (§ 6), companion edits to `results/k-ladder-2026-09-12/findings.md` and `reports/k-ladder-mcb-deltas-2026-09-13.md` (§ 7), and a change log against version 1 (§ 8) |
| `verify-v1.md` | The independent verification of version 1 (PASS WITH FIXES), whose findings version 2 addresses |
| `restatement-drafts-verify.md` | The independent verification of all fifteen restatement drafts; § 4.12 is the brief the redraft started from |
| `scripts/recount.py` | Recounts the SHAPE clause on the restated tables: `python scripts/recount.py <repository root>` |
| `scripts/build.py` | Builds the outcome from the signed text by exact replacements, each required to match once: `python scripts/build.py <repository root> <output directory>` |

Both scripts read only committed files under `results/`.

## Changelog

### 2026-10-18 — Original publication

The redraft's version 2 and its two verification reports, committed for
a cross-model review (Astra) before the PI walks the text.
