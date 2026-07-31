# Sonnet spot-audit verdict — C4 extraction fleet (2026-07-31, Session 123)

**Ruling under test**: `phase3-rulings-2026-07-31.md` § 4 — Sonnet
permitted for the fleet's mechanical tail, gated on a spot-audit of the
first Sonnet batches against an Opus duplicate.

## Design

- **Sonnet batches**: b003 (documentation-index, documentation-protocol,
  mcc-permutation-validation; → `003-doc-index/003-doc-protocol/003-mcc-perm.json`)
  and b014 (hypothesis-tracking.md, whole document; → `014.json`).
- **Opus reference**: an independent duplicate of b014
  (`014-opus-reference.json`, this directory), same instrument (v1.2),
  no visibility of the Sonnet output.
- All outputs validator-clean on first submission (after each agent's
  own self-check loop).

## b014 head-to-head (the recall test)

| measure | Sonnet | Opus reference |
| :--- | :--- | :--- |
| claims | 49 | 46 |
| values | 127 | 114 |
| claim-line coverage | 54 lines | 54 lines |

- Coverage is line-identical except one wrapped-span boundary on each
  side (Sonnet 214, Opus 223); the underlying values (`6/10`, `4/10`,
  `T=0.0`; `F1=0.609`) were captured by BOTH — verified token-by-token.
- **Zero missed claims in either direction.** The value-set differences
  are span conventions: Opus keeps affixes in the verbatim (`2×`,
  `+0.09`, `~23:1`), Sonnet splits them (`2`, `0.09`, `23`); the
  harness parses both forms. Sonnet enumerated small counts more
  richly (hence 127 vs 114 values).
- Sonnet independently applied the v1.1 registered-value rule
  (lodged-doc anchors for design claims), used schema-1.1 per-value
  arithmetic once, and surfaced a genuine stale-reference finding (the
  document names `results/phase3a-consensus/`, which does not exist in
  the working tree).

## b003 quality notes

Claim-sparse documents handled with correct rule-5 scope decisions
(identifier cross-references excluded, decision logged); the
claim-dense mcc-permutation doc anchored to real committed caches with
canonical `len:` counts, and refused to force mismatched anchors onto
differently-scoped leaderboard values (left `anchor-unknown` with a
search trail).

## Verdict

**PASS — the Sonnet tail runs free** on ruling 4's document classes
(tracking docs, checklists, low-span-density methodology files). Opus
remains the default for dense results prose. `extractor.model` records
the model per file; the validator, recompute harness, and triage gate
every output regardless of extraction model.
