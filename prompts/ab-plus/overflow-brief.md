# AB+ overflow structuring brief (fresh-context, per source)

Repo: `/home/shawn/Code/map-reader-llm`. You are the STRUCTURER for
one Annotated Bibliography Plus (AB+) source, named in your dispatch
message. Its drafter and editor left verified secondary material in a
free-form note, `outputs/ab-plus/_work/<citekey>.overflow-notes.md`,
that the 300–500-word summary could not hold. Your job is to turn that
material into the overflow sidecar the pipeline can check and publish:
`outputs/ab-plus/_work/<citekey>.overflow.json`. Written 2026-09-03
after the PI's decision on the tail report: the sidecar is the
COMPLETE copy (paraphrase beside the verbatim span it rests on, so
accuracy can be checked against the text at any time); the rendered
entry publishes the paraphrase and page anchor only.

## Steps

1. If `outputs/ab-plus/_work/<citekey>.pages-provenance.md` exists,
   read it FIRST: the cache is OCR-rebuilt and every quote you write
   must be confirmed character-for-character on the rendered page
   image (PyMuPDF `get_pixmap` at 250 dpi from the copy-of-record path
   it names; use `.venv/bin/python`). Record the page indices you
   checked in the note's designated section.
2. Read the entry (`_work/<citekey>.entry.json`), the overflow notes,
   and the whole page cache (`_work/<citekey>.pages.json`). Read the
   sidecar schema: `PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli schema --overflow`.
3. For each substantive, source-grounded point in the notes, write one
   item:
   - `paraphrase`: our words, UK/Australian English, one to three
     sentences, self-contained (a reader of the public entry sees only
     this and the anchor). Denominators, conditions, hedges, and
     attributions travel with it. It must be checkable against the
     quote: a reader comparing the two should agree the paraphrase is
     what the span says.
   - `quote`: the VERBATIM span the paraphrase rests on, copied from
     the page cache (not from memory, not from the notes — notes may
     have normalised it). The shortest span that carries the point;
     it must pass the deterministic checker byte-for-byte after
     whitespace normalisation. Never a span from a page the gate
     flagged as a neighbouring article, and never one that straddles a
     page break.
   - `page_index` (0-based, the page the span is on); optional
     `section` (advisory locator) and `topic` (a two- to five-word
     heading).
4. What does NOT become an item: the drafter's or editor's inferences
   about the citing paper; cache-defect registers, OCR-slip lists,
   page-mapping caveats, and working notes (these stay in the `.md`
   note, which you do not modify); anything the entry's key points or
   summary already state in the same detail (an item may sharpen a
   key point with a specific — a number, a denominator, a named
   condition — but not repeat it). Cap at twelve items, ordered by
   salience to the citing paper (a preregistered VLM study of
   burial-mound symbol detection on historical maps: transfer and
   calibration economics, annotation budgets, F1 and MCC reporting,
   consensus-over-passes plus adversarial verifier, difficulty
   ladder, preregistration apparatus).
5. Write the sidecar with `indent=1`, `ensure_ascii=False`, a
   trailing newline, and these top-level fields: `citekey`,
   `generated` (today's ISO date), `model` (`claude-opus-5`),
   `source_notes` (the notes path), `items`.
6. Run
   `PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli check --entry outputs/ab-plus/_work/<citekey>.entry.json`
   — it now checks the sidecar too and must PASS on every overflow
   span. A span that will not verify is re-cut from the cache or the
   item is dropped; never "repaired" from memory.
7. Do not modify `entry.json`, `verdict.json`, the `.md` note, or any
   rendered file under `outputs/ab-plus/`. Temporary files only in the
   per-citekey scratch directory named in the dispatch. Do not commit.

## Report (final message)

Item count; which note sections were structured and which were left
as working notes and why; any span you could not verify and what you
did; for OCR-rebuilt caches, the page indices visually attested; the
check verdict (must be PASS with the overflow span count).
