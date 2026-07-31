# C4 extraction instructions — quantitative claims in hand-written mine documents

**Version**: 1.0 (2026-07-31). **Controller**: `planning/audit-charter.md`
§ 7 Phase 3. **Schema**: `docs/manifest-schemas/c4-claims.schema.json`.
**Consumers**: extraction agents (one per document or document batch); the
assembly step assigns `claim_id`s and validates against the schema; the
recompute harness resolves anchors and diffs; triage adjudicates
mismatches.

## Task

Read ONLY your assigned mine document(s) and enumerate EVERY checkable
quantitative claim — full enumeration, no sampling (charter § 5 rule 3).
When in doubt whether a number is a checkable claim, include it and flag
the doubt in `notes`. Missing a real quantitative claim is the failure
mode this programme exists to catch; over-inclusion is cheap to prune.

A **quantitative claim** is any number the document asserts as a fact
about the study: metrics (F1, MCC, precision, recall, confidence
intervals), test statistics (p, Δ, ρ, effect sizes, permutation/bootstrap
counts), counts (tiles, passes, conditions, mounds, candidates, clusters,
tests, files), costs (US$, token counts), rates and percentages,
parameters asserted as what-was-run (temperatures, thresholds, seeds,
worker counts, N iterations), and physical quantities (buffer metres,
pixel sizes, distances).

## Output

Write a JSON object conforming to the schema to your assigned output file
under `reports/verification/c4-extraction/`. Set every `claim_id` to
`null` (assigned at assembly). Fill `source_document.git_blob` with the
output of `git rev-parse HEAD:<file>` (abbreviated to ≥ 7 chars). Return
a one-line count summary as your final message, not the JSON.

## Hard rules

1. **`claim_text` is a VERBATIM contiguous span** copied
   character-for-character from the source — never paraphrase, never
   stitch non-contiguous text. Use the minimal span (sentence, list item,
   or table row) that carries the value(s) plus enough context to
   identify what they measure; `source.lines` (1-indexed, inclusive) must
   bound the span. One claim row per span; put every checkable value in
   the span into `values[]` in order of appearance.
2. **Anchor to the least-writable artefact** (charter § 5 rule 1, § 4
   hierarchy). If the document names its source (a path, a manifest, an
   eval JSON), anchor there. If the value plainly lives in a standard
   artefact (sibling `evaluation.json`, `results/conditions-manifest.json`,
   a `threshold_sweep.json`), anchor there. Never anchor prose to prose:
   if the only visible source is another markdown document, set method
   `anchor-unknown` and name that document in `notes` — triage will chase
   the chain to an artefact.
3. **Method assignment**:
   - `read` — the value should sit at `anchor.path` in the anchor file.
   - `arithmetic` — derivable from committed values (`anchor.expression`,
     operands named in `notes`): deltas, ratios, sums, percentages.
   - `recompute-script` — needs scripted recomputation (bootstrap CIs,
     permutation p-values, tiering). Record the claim; do NOT attempt the
     computation yourself.
   - `historical` — the quoted-old-value side of correction blocks and
     changelogs ("was X, now Y": X is `historical`; Y is a live claim).
     Superseded-and-marked values in changelog before→after tables are
     `historical` too.
   - `unverifiable-era` — token/usage claims about the retest era
     (phase2a–3c; `reports/verification/phase2-gate-package.md` § 4):
     `usage_stats` is wholesale unpopulated there. Flag, don't fight.
   - `external` — vendor pricing, billing-console figures, quota values:
     no repo artefact can decide them. Attestation material only.
   - `anchor-unknown` — you cannot locate an anchor. Say what you looked
     for in `notes`.
4. **Do not verify while extracting.** You may open an anchor file ONLY
   to confirm it exists and locate `anchor.path`; never adjudicate
   match/mismatch — that is the harness's job (charter § 5 rule 2:
   fresh-context verification).
5. **Out of C4 scope — do not extract** (logged as an explicit scope
   decision, not silent): dates and timestamps, git hashes and blob ids,
   session numbers, Obs/erratum/claim/commitment identifiers, version
   strings, line-number citations, and numbers inside file paths or
   condition names (`min6`, `t0.3`, `384` in `pv-diag-384` are names, not
   claims). A number used BOTH as a name and as an asserted fact ("the
   487-tile Era 2 corpus") IS a claim (count, Era 2 tile corpus).
6. **Tables**: one claim row per table row; `values[]` covers the
   numeric cells; `quantity` carries the row+column meaning. Wholly
   generated tables pasted into hand-written documents are still claims
   made by the document — extract them.
7. Attribute nothing from outside your assigned document; if it
   references another section or file, note the reference, do not chase
   it beyond anchor identification (rule 2 above).
8. UK English in free-text fields you author (`quantity`, `notes`);
   verbatim fields follow the source exactly.

## Known traps (from Phases 1–2)

- Changelog before→after tables are dense with `historical` values —
  misclassifying them as live claims will flood triage with false
  mismatches.
- The same quantity appears at different precisions across documents
  (0.890 vs 0.8902): record `value_verbatim` exactly; the harness owns
  rounding tolerance (match at quoted precision).
- Costs appear as estimates ("~$60"), audited figures ("$34.5"), and
  billed figures ("$402.08") — put which-kind in `quantity`; audited and
  billed figures anchor differently (manifests vs `external`).
- Retest-era (phase2a–3c) tile counts ARE verifiable (scalar
  `items_processed`); token counts are NOT (`unverifiable-era`).
