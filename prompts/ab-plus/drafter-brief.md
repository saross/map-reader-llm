# AB+ drafting brief (shared by every drafter agent)

Repo: `/home/shawn/Code/map-reader-llm`. Produce ONE Annotated
Bibliography Plus (AB+) entry for the citekey named in your dispatch
message. Promoted into the repository on 2026-09-02 from the pilot
brief (S144, 2026-08-30), which lived only in a session scratchpad;
the pilot's 25 entries under `outputs/ab-plus/` were drafted to the
same rules.

## Steps

1. Read `scripts/ab_plus/schema.py` — `ENTRY_SCHEMA` and
   `validate_entry` are the binding contract (required fields:
   citekey, summary, positioning, key_points; each key point is
   {quote, page_index, section, paraphrase, relevance_gap,
   relevance_section, relevance_stance}; optional framing_hook).
2. Read ONE rendered exemplar for voice and format, chosen by your
   cluster: `outputs/ab-plus/caspari_convolutional_2019.md` for
   empirical/technical sources, `outputs/ab-plus/gould_but_2026.md`
   for methodology/preregistration sources. Read NO other entry or
   `_work/` file except your own — independence between sources is
   part of the design.
3. If `outputs/ab-plus/_work/<citekey>.pages-provenance.md` exists,
   read it FIRST: it records an OCR rebuild or other cache caveat and
   tells you which pages must be confirmed against rendered images.
4. Read your source's full text:
   `outputs/ab-plus/_work/<citekey>.pages.json` — the ENTIRE cache,
   every page, before selecting quotes (page through with offset if
   it is long).
5. Write the entry to `outputs/ab-plus/_work/<citekey>.entry.json`
   (pure JSON, UTF-8, `indent=1`, `ensure_ascii=False`).
6. Verify:
   `PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli check --entry outputs/ab-plus/_work/<citekey>.entry.json`
   — every quote is byte-checked against the page text. Iterate
   until it passes clean (re-select a verbatim span or fix the
   page_index; never edit a quote to read better).
7. Temporary files, if any, go ONLY in your per-citekey scratch
   directory named in the dispatch message — never in `_work/`
   beside another source's files (a shared-filename collision
   occurred in the pilot).

## Binding rules

- Quotes VERBATIM from the page text with the correct page_index —
  the checker is deterministic and unforgiving. Keep each quote the
  shortest span that carries the point.
- key_points: 3–7, capped by SALIENCE TO THE CITING PAPER, not by the
  source's own coverage. Most salient first.
- summary: 300–500 words, advisory register, no padding; weave in the
  intersections with the citing paper; every factual claim ABOUT THE
  SOURCE must be true of the source.
- positioning: 2–3 sentences on where this source sits relative to
  the citing paper's claims, naming ONE primary cluster from the list
  below (others may be mentioned as secondary). The sentence target
  and the summary band are targets, not gates (PI ruling 2026-09-03,
  after the tail): exceed them only when a verified nuance would
  otherwise be lost, and say so in your report.
- Numbers quoted or restated from the source must match the page
  text exactly; denominators, baselines, and conditions travel with
  every comparative number. Anti-confabulation is the point of this
  artefact.
- Hedged findings stay hedged; condition-specific results stay
  scoped; the source's own caveats travel with the point they weaken.
- If a secondary, verified caveat will not fit the summary band,
  write it to the overflow sidecar
  `outputs/ab-plus/_work/<citekey>.overflow.json` rather than dropping
  it: one item per caveat with `paraphrase` (our words), `quote` (the
  VERBATIM span it rests on — byte-checked by `cli.py check`),
  `page_index`, and optional `topic`/`section`. The renderer publishes
  the paraphrase and page anchor only; the sidecar is the complete
  copy. Schema: `python -m ab_plus.cli schema --overflow`. A free-form
  `<citekey>.overflow-notes.md` may accompany it for cache-defect
  registers and working notes, but anything a reader should see goes
  in the sidecar.
- UK/Australian English in all free text.

## The citing paper (what "salience" is measured against)

A preregistered study using vision-language models (VLMs, the Gemini
family) to detect burial-mound symbols — one symbol family among
dozens — on scanned Soviet-era topographic maps of Bulgaria. Its
architecture is consensus-over-passes (repeated sampling of a
proposer, greedy consensus aggregation) followed by an adversarial
verifier pass; it measures a cost/accuracy trade-space (F1 and MCC,
tile-level and object-level at 20 m / 50 m match radii); it
transfers calibration from a small gold standard to a 55-map
deployment (carried vs oracle operating points, transfer taxes);
it reports annotation budgets, ground-truth epistemics (curator vs
adjudicated reference data), a novice-human (student) baseline, a
text-vs-image modality comparison, and an area-segmentation to
point-symbol difficulty ladder. It is positioned against CNN
prospection, open-vocabulary detection, and historical-map
extraction prior art. Its preregistration apparatus includes
registered hypotheses, an analyses register, an errata log,
recorded deviations, and an adaptive/phased design (the
"adaptive preregistration" thread: Gould et al. 2026, Srivastava
2018). Reasoning-mode ("thinking") settings, verbalised confidence,
and self-consistency-style aggregation are live design questions.

## Positioning clusters (pick the primary)

- archaeological prospection prior art (automated site or mound
  detection in remote-sensing data);
- historical-map extraction lineage (symbols, roads, settlements,
  legends from scanned or historical maps);
- symbol-on-technical-drawing analogue (blueprints, floor plans,
  engineering symbols);
- open-vocabulary / VLM detection alternative (zero-shot grounding,
  VLM benchmarks, retrieval over visual documents, reasoning-vs-
  perception trade-offs);
- few-shot / in-context learning / annotation budget (many-shot ICL,
  prompt-order sensitivity, calibration-before-use, bias in ICL);
- consensus / test-time-compute antecedent (self-consistency,
  repeated sampling, multi-agent or multi-model agreement,
  self-correction limits, diversity metrics);
- calibration / verbalised confidence (eliciting and evaluating
  stated confidence in LLMs and VLMs);
- preregistration and open-science methodology (preregistration
  templates, deviations, pre-analysis plans, blind analysis,
  adaptive designs, registered reports, reusable holdouts,
  preregistration for AI/LLM research);
- methods/metrics (evaluation protocol, metric hygiene, statistical
  design).

## Final report (returned to the orchestrator)

citekey; check verdict (must be PASS, with N/N quotes); page count
read; 3–5 lines of content signal (what in this source matters most
to the citing paper); any metric-hygiene traps noticed (for example
class-relative vs aggregate F1 — the O'Hara lesson); any cache
defect you found (empty pages, truncated tables, OCR slips) with page
indices; whether you wrote an overflow-notes file.
