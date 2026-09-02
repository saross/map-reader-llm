# AB+ corpus for the ISPRS paper bibliography — run card

> **Last revised**: 2026-09-02 (tail run PAUSED at the usage limit with
> 45/88 rendered; resume protocol in the continuity file).
> See [§ Changelog](#changelog).

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

- [x] PI go — 2026-08-30, **PILOT FIRST**: 25 sources (the 8 adjacent
  + 17 core named in the seeds/skeleton), then a Claude-usage
  checkpoint against the PI's weekly meter (baseline **26 % used** at
  approval) before the remaining ~88 are authorised. Vendoring and
  scope otherwise as proposed.

## Tail run (2026-09-02)

Manifest: `outputs/ab-plus/manifests/tail-2026-09-02.json` (88
sources; cluster, wave, gate result, status). Briefs:
`prompts/ab-plus/` (drafter, verifier, editor). Waves of ~15
concurrent drafters at the Opus tier, verifiers dispatched as drafts
land, editors on every PASS-WITH-EDITS; deterministic check + render
per wave, stamped `--model claude-opus-5 --run-date 2026-09-02`.

## Changelog

### 2026-09-02 (later) — Tail run PAUSED at the usage limit

Interim state (manifest is authoritative): **45/88 rendered**,
7 editing, 2 verifying,
2 drafted, 7 drafting,
25 queued. All verdicts PASS-WITH-EDITS (0 FAIL,
0 clean); two carried an UNSUPPORTED key point corrected at edit.
Ran at the harness cap of 20 concurrent Opus-tier agents with rolling
refill; ~0.35–0.5M reported tokens per source across the three agent
stages (drafters ~120–170k, verifiers ~85–125k, editors ~90–150k).
New cache-defect class: IEEE Access PDFs extract table captions
without bodies (2 sources; verifiers rendered pages). Resume protocol
in `planning/paper-writeup-continuity.md` § STATE AFTER S146; drivers
in `scripts/ab_plus/tail/`.

### 2026-09-02 — Tail run LAUNCHED; amendments applied

PI-directed resumption on ~24 h of extra Claude usage credit. Before
launch: (1) the pilot report's amendment 1 became a CLI step
(`gate`: chars/page, empty pages, byte-identical-page watermark
signature) — tail result 85 PASS, 1 WARN (davis_comparison_2019, an
accepted-manuscript bundle with image-only figure pages), 2 FAIL
(trier_using_2019, gerasimova_argumentbased_2024 — Wiley watermark-only
rasterised downloads); (2) the pilot's hand OCR repair became
`ocr-repair` (preserve original, 300 dpi + tesseract, provenance note)
and was applied to the two FAILs; (3) amendment 2 (per-citekey scratch
dirs) and amendment 3 (overflow-notes file) went into the briefs, which
were promoted from a session scratchpad into `prompts/ab-plus/`;
(4) the renderer learned the pilot's per-point verdict shape (the
pilot deliverables had printed "flags: none" beside OVERREACH
verdicts) and the pilot 25 were re-rendered with a model stamp
(`claude-opus-5`, verified from the archived S144 subagent
transcripts). Commits `4f3c0924f`, `fbbfb0a4e`, and the re-render
commit that follows it. Outcome numbers land in the next entry.

### 2026-08-30 (later still) — Usage checkpoint MEASURED

PI meter: the 25-source pilot cost **~10 % of the weekly Claude
quota** (26 % → ~35 %). Implication: the remaining ~88 sources ≈
35 % of a week in one push — too much beside drafting. Plan: batch
the tail at ~25–30 sources per quota week (~10–12 %/week), scheduled
early in fresh weeks, prioritised by citation likelihood; the core
Related-work slate is already covered by the pilot, so nothing in
the tail blocks drafting. Economy option for the least-cited tail,
PI's call: Sonnet-tier drafters with Opus verifiers (the
deterministic checker is model-independent and the verifier layer is
what catches interpretive defects) — estimated ~40–50 % cheaper per
source, at the cost of heavier verifier passes.

### 2026-08-30 (later) — Pilot COMPLETE, corpus build PAUSED

All 25 pilot sources rendered and committed (0/25 passed fresh-context
verification without edits — the two-mechanism design caught
interpretive defects everywhere; nothing fabricated). Full findings,
catch taxonomy, pipeline amendments, and the usage arithmetic:
`reports/ab-plus-pilot-report-2026-08-30.md`. PAUSED per the PI's
quota ruling; the remaining ~88 sources run on PI go with the
amendments applied (cache pre-flight gate, per-citekey workdirs).

### 2026-08-30 — Original publication

Drafted after the Zotero repairs completed PDF coverage (dedupe +
two API-side attachments; the client-side attach bug is with the PI
— plugin-exception hypothesis, debug log read pending). Adjacent
collection ruled IN (all 8, PI same day).
