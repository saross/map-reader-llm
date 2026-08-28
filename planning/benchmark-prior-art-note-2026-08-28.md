# Benchmark prior-art note — symbol-extraction benchmark position

> **Last revised**: 2026-08-28 (original publication). Recorded at PI
> request during S143 ("make a note of this for future benchmark
> construction planning"). See [§ Changelog](#changelog).

**Question answered**: does any existing VLM map benchmark preempt
turning this project's corpus + machinery into a symbol-extraction
benchmark (the successor-paper spine, Obs 436)? **No — verified
against the collection 2026-08-28.**

## The three nearest benchmarks (all in the Zotero TRAP library)

| Benchmark | Task type | Material | Why it does not preempt |
|---|---|---|---|
| CartoMapQA (Ung et al., ACM SIGSPATIAL 2025) | question-answering: map understanding/reasoning, OCR, semantics | modern cartographic maps | no detection/localisation task |
| GeoMap-Bench / PEACE (Huang et al., CVPR 2025) | QA: extraction, referring, grounding, reasoning, analysis | geological maps | verified lit-scout caveat (docs/methodology/research/lit-scout-oldreport-resolve-2026-08-21.md, Row 6): "not bounding-box detection — cite as evidence of general-VLM weakness on cartographic material, never as a detection baseline" |
| BlueprintSymVL (Shteriyanov et al., 2025) | discriminative symbol RECOGNITION (one-shot visual examples) | engineering blueprints | recognition of symbols, not dense in-scene extraction; not maps; found VLM degradation in clutter + hallucination |

Nearest detection-adjacent published result: Kirsanova et al.
(GeoSearch 2025), GPT-4o legend detection F1 0.88 on **legend items**
with 15 visual exemplars — legend entries, not in-map symbol
extraction (docs/methodology/research/
claude-comparison-with-other-research.md).

## The open position our benchmark would occupy

**Dense, georeferenced symbol detection/extraction on degraded
historical scanned cartography**: find every member of one symbol
family across full sheets, scored spatially against adjudicated
ground truth. Differentiators, all already built:

1. **Task type**: detection with spatial scoring (buffer-resolved
   corrected-F1, tile-MCC) — vs QA and crop-level recognition.
2. **Material**: 1:50k scanned historical topographic sheets with
   dense competing symbology and scan degradation.
3. **Ground truth**: 55 sheets / 8,541 tiles; canonical AND
   standardised references (~5,010 adjudicated points, marked-centre
   extension layer); a field-validated subset (Sobotková et al. 2023,
   2024); the two-reference protocol.
4. **Instrument calibration**: the sensitivity/MDE appendix
   (results/sensitivity-mde-2026-08-28/) quantifies what the
   benchmark's own instruments can resolve — rare for any benchmark.
5. **Cost-awareness**: $/mound and Pareto-frontier reporting as a
   first-class benchmark dimension (results/55map-final-board-
   2026-08-27/) — novel in this space.
6. The trio above actively HELPS the case: they document VLM weakness
   on cartographic material and stop short of detection.

## Before a benchmark paper commits (required checks)

1. `/read` CartoMapQA's full PDF — confirm no detection sub-task
   (this note rests on verified lit-scout rows + research notes, not
   a cover-to-cover read).
2. `prior-art-scout` sweep for post-2025-11 entrants; check the
   map-text-spotting ecosystem (e.g. ICDAR historical-map
   competitions — TEXT-focused; verify no symbol track has appeared).
3. ⚠ Provenance trap on record: an older internal report spliced
   PEACE's GPT-4o 0.369 onto CartoMapQA; corrected by the 2026-08-21
   lit-scout resolve. Do not cite that pairing from pre-resolve notes.

## Changelog

### 2026-08-28 — Original publication

Drafted in-session (S143) from the Zotero search + the verified
lit-scout rows, at PI request.
