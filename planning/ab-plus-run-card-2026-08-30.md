# AB+ corpus for the ISPRS paper bibliography — run card

> **Last revised**: 2026-08-30 (original publication; AWAITING PI GO
> — no agents launch before it). See [§ Changelog](#changelog).

**Purpose**: per-source Annotated Bibliography Plus (AB+) entries for
every work the paper may cite — attested quotes with page anchors,
deterministically verified against extracted text, plus a
fresh-context verifier pass against inflated interpretation (the
paper-b two-mechanism design: code catches fabrication, an
independent LLM catches overreach). Downstream: Related-work drafting
pulls from entries, and the paper-review lens checks every cited
claim against its citekey's attested quotes.

## Scope

| Collection | Items | PDFs |
|---|---:|---:|
| `vlm-burial-mound-detection` (BTKV5ZIF) | 103 (post-dedupe 2026-08-30) | 103 |
| `vlm-adjacent-reference` (7GCK5VQ8) — all 8 per the PI's inclusion ruling | 8 | 8 |
| **Total** | **111** | **111/111** |

## Tooling (vendored, not shared)

The paper-b `ab_plus` package (Apache-2.0) is vendored into this
repo's `scripts/ab_plus/` with config repointed here — paper-b is a
collaborative repo and its config hard-codes its own collection and
output homes. Carried conventions: **`_work/` page text is
copyrighted and NEVER committed** (gitignored); deliverables +
index are committed. Setup deltas: `pymupdf` added to
`requirements.txt` (the extractor imports it); extractor via
`AB_PLUS_EXTRACTOR_DIR` (verified present at
`~/Code/llm-reproducibility/extraction-system/scripts/pdf_processing/`);
Zotero DB read-only as ever. Outputs: `outputs/ab-plus/` +
`results/ab-plus-index.md`.

**Citekeys**: BibTeX exported from the two collections via the API
into `paper/references.bib` (dual purpose — it also wires the Quarto
manuscript). Items carrying pinned Better BibTeX `citationKey`
fields keep them; divergence between export keys and pinned keys is
resolved at export time and recorded in the index.

## Stages and agent plan

| Stage | Mechanism | Cost |
|---|---|---|
| 1. Resolve + extract | CLI (`resolve`, `extract`) — deterministic PDF→text, cached | $0, local |
| 2. Entry drafting | one background agent per source, **Opus-tier** (subagent model policy), batched ~8 concurrent; reads extracted text only, writes entry JSON to schema | Claude usage, no external API |
| 3. Quote check | deterministic (`check`) — every attested quote byte-verified against page text | $0 |
| 4. Interpretation verification | fresh-context **Opus** verifier agent per entry (sees entry + source, not the drafter's reasoning) | Claude usage |
| 5. Render + index | CLI (`render`) → per-source markdown + coverage index | $0 |

**Aggregate (stated per standing rule)**: ~111 drafting agents +
~111 verifier agents ≈ **222 Opus agent runs**, batched across
sessions as background work — no Gemini/external API spend, but a
material draw on Claude usage; the batching keeps any single session
light. Priority order: the eight adjacent items (three Related-work
framing clusters) + the Seed-8 sources first, then the long tail.

**Failed-check loop**: entries failing stage 3 or 4 go back to their
drafter with the verdict (the established proposer/verifier
iterate pattern); two consecutive failures escalate to the PI.

## Sign-off

- [ ] PI go (scope, agent counts, vendoring approach)

## Changelog

### 2026-08-30 — Original publication

Drafted after the Zotero repairs completed PDF coverage (dedupe +
two API-side attachments; the client-side attach bug is with the PI
— plugin-exception hypothesis, debug log read pending). Adjacent
collection ruled IN (all 8, PI same day).
