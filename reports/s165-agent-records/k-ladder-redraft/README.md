# K-ladder outcome redraft (PR #52, row `k-ladder-2026-09-12`)

> **Last revised**: 2026-10-18 (version 3 added after Astra's review).
> Earlier the same day: original publication. See
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
| `k-ladder-redraft-v3.md` | Version 3, after Astra's review of version 2 (PASS WITH FIXES): the admissibility, resolution, and clipped tile-MCC readings corrected, the mechanism wording qualified, and a plain-language lead added; same sections as version 2, with § 8 mapping each review item to its fix |
| `k-ladder-redraft-v2.md` | The redraft under review: the outcome text (§ 1), a word diff against the signed text (§ 2), every change with its source (§ 3), recounts (§ 4), decisions for the PI (§ 5), attestation corrections (§ 6), companion edits to `results/k-ladder-2026-09-12/findings.md` and `reports/k-ladder-mcb-deltas-2026-09-13.md` (§ 7), and a change log against version 1 (§ 8) |
| `verify-v1.md` | The independent verification of version 1 (PASS WITH FIXES), whose findings version 2 addresses |
| `restatement-drafts-verify.md` | The independent verification of all fifteen restatement drafts; § 4.12 is the brief the redraft started from |
| `scripts/recount.py` | Recounts the SHAPE clause on the restated tables: `python scripts/recount.py <repository root>` |
| `scripts/build2.py` | Builds the version 2 outcome (§ 1) from the signed text by 25 exact replacements, each required to match once: `python scripts/build2.py <repository root> <output directory>` |
| `scripts/build2_opt2.py` | Builds decision A's Option 2 text (tier E unclipped leads) from `build2.py`'s edits: same arguments |
| `scripts/companion.py` | Builds the § 7 companion edits for both options and their edit list: same arguments |
| `scripts/build3.py`, `scripts/build3_opt2.py`, `scripts/companion3.py` | The version 3 builders, same arguments as their version 2 counterparts; `build3.py` reproduces version 3's § 1 exactly |
| `scripts/data/companion-edits-v3.json` | The version 3 companion edit list (`companion3.py` reproduces it byte for byte) |
| `scripts/data/companion-edits.json` | The companion edit list as the redraft agent produced it (`companion.py` reproduces it byte for byte) |

The scripts read committed files only (the restated tables under `results/`,
the register, and the two companion documents) and write only to the output
directory given.

## Changelog

### 2026-10-18 (later) — Version 3

Astra reviewed version 2 (PASS WITH FIXES: every number reproduced; three
interpretation fixes and two editorial points). Version 3 and its builders
are added; version 2 is kept as reviewed.

### 2026-10-18 — Original publication

The redraft's version 2 and its two verification reports, committed for
a cross-model review (Astra) before the PI walks the text.
