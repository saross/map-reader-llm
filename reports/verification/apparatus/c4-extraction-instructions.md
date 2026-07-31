# C4 extraction instructions — quantitative claims in hand-written mine documents

**Version**: 1.2 (2026-07-31, S123 triage lessons; v1.1/v1.0 same
day). **Controller**:
`planning/audit-charter.md`
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
   - `arithmetic` — derivable from committed values: deltas, ratios,
     sums, percentages. Fill `anchor.expression` (e.g. `a - b`) AND
     `anchor.operands[]` — one `{name, file, path}` per operand, so the
     harness can evaluate mechanically. Single-letter operand names.
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
   numeric cells; `quantity` carries the row+column meaning. Use
   per-value `path` when one anchor file holds the row's cells at
   different locators, and per-value `method` for mixed spans (a delta
   beside a permutation p-value). Wholly generated tables pasted into
   hand-written documents are still claims made by the document —
   extract them.
7. Attribute nothing from outside your assigned document; if it
   references another section or file, note the reference, do not chase
   it beyond anchor identification (rule 2 above).
8. UK English in free-text fields you author (`quantity`, `notes`);
   verbatim fields follow the source exactly.

**v1.1 calibration rule** (calib-b lesson): a numeric claim about what
the REGISTRATION specifies ("the preregistered temperature was 1.0",
"registered as 10,000 permutations") anchors to the lodged document
(`docs/methodology/preregistration/osf/…`, `path` null), NEVER to the
config/script that executed — the executed artefact records the
deviation, not the promise, and anchoring there manufactures a false
mismatch. Claims about what was RUN anchor to configs/metas as before.
Non-JSON anchors (`config.py` constants, test counts in `tests/*.py`,
crop-size PNGs) are legitimate and expected — the harness routes them
to triage rather than resolving mechanically.

**v1.2 amendments** (Session-123 triage of the first recompute —
every item below is a defect class that reached the harness):

1. **One derivation per expression.** The harness compares EVERY
   effective-`arithmetic` value against an expression result. A span
   carrying several derived values gives each its own value-level
   `expression` + `operands` (schema 1.1); `anchor.expression` covers
   at most one. NEVER let the operand values themselves (the numbers a
   derivation consumes) inherit an `arithmetic` claim method — give
   each `method: "read"` with its own path, or they are compared
   against their own difference (the 487−160=327 trap: 487 and 160
   both "mismatched" 327).
2. **Cross-file locators.** A value `path` may name another file:
   `<repo-relative-file>#<jsonpath>` (e.g. a range minimum living in a
   sibling run's meta). Operands name their file in their own `file`
   field as before.
3. **No pathless values in multi-value claims.** A value with
   `path: null` falls back to `anchor.path`; when the value's quantity
   is not what `anchor.path` locates, the fallback silently compares
   the wrong quantity (the pass-count-vs-temperature trap: "5 passes"
   compared against `$.configuration.temperature` = 0.7). In any claim
   with more than one value, every `read` value carries its own
   `path`; a value with no locatable path takes an explicit
   non-read method (`recompute-script` / `anchor-unknown`) instead.
4. **Counts.** Canonical spelling is the `len:` prefix
   (`len:$.features`, `len:$.results`). The harness also accepts
   `len(...)`/`count(...)`, a `.length` suffix, and
   `(array length)`/`(distinct count)` annotations, but emit `len:`.
   Derived-probabilities files (keys `derived_from`/`source`/
   `vote_threshold`) carry no `total_results` scalar — count them via
   `len:$.results`.
5. **Approx markers are verbatim.** `~`/`≈` on a quoted value belongs
   in `value_verbatim`; dropping it promotes an approximate quote to a
   hard comparison (the ≈$1.11 flex-pricing row surfaced as MISMATCH
   instead of APPROX).
6. **Shared units and signs in ranges.** In spans like "2.4–2.7 %"
   only one value carries the sign/unit; set the other values' `unit`
   field (`%`, `m`, …) so the harness can bridge scales.
7. **Filters are legal paths.** `$.cells[?(@.name=='TH7-k3')].f1_50`
   (single-match equality) and `[*]` (constant-collapse across a
   collection) resolve mechanically; prefer them over pathless
   approximations like `len($.cells)` for a factor-level count.

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
