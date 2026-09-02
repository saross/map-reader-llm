# AB+ verification brief (fresh-context, per entry)

Repo: `/home/shawn/Code/map-reader-llm`. You are the INDEPENDENT
verifier for one Annotated Bibliography Plus (AB+) entry, named in
your dispatch message. You have not seen the drafter's reasoning;
your job is to catch INFLATED INTERPRETATION — the deterministic
checker has already verified quotes byte-for-byte, so fabrication is
not your target; overreach is. Promoted into the repository on
2026-09-02 from the pilot brief (S144, 2026-08-30).

## Steps

1. If `outputs/ab-plus/_work/<citekey>.pages-provenance.md` exists,
   read it FIRST — it tells you which pages are OCR-rebuilt or
   truncated and must be confirmed against rendered page images
   rather than the cache.
2. Read the entry: `outputs/ab-plus/_work/<citekey>.entry.json`.
3. Read the source text: `outputs/ab-plus/_work/<citekey>.pages.json`
   — the whole thing; your value is the context the entry may have
   dropped. Read NO other `_work/` file or rendered entry.
4. For EVERY key point, the summary, and the positioning claim, ask:
   does the source, read in context, actually support this reading?
   Hunt specifically for: (a) hedged findings reported as firm;
   (b) subset- or condition-specific results generalised; (c) a
   baseline or denominator dropped from a comparative number; (d) the
   source's own caveats omitted where they would weaken the point;
   (e) salience drift — a point true of the source but framed to
   overstate its relevance to the citing paper (a preregistered VLM
   study of burial-mound symbol detection on historical maps:
   transfer/calibration economics, annotation budgets, F1 and MCC
   reporting, consensus-over-passes plus adversarial verifier,
   difficulty ladder, preregistration apparatus); (f) a garbled
   source sentence "repaired" in the wrong direction; (g) claims
   about the source that rest on external knowledge rather than its
   text (flag as NOT CHECKABLE, not as wrong).
5. Verdict per key point: SUPPORTED / OVERREACH (with the corrective
   reading) / UNSUPPORTED. A claim resting on external knowledge gets
   its own `per_point` item with `"index": "not_checkable"` (or the
   field name) and `"verdict": "NOT CHECKABLE"` plus a note — these
   four values are the whole vocabulary and the renderer rejects any
   other (enforced 2026-09-03). Overall: PASS, PASS-WITH-EDITS (list the
   exact edits, field by field, as replace-X-with-Y instructions), or
   FAIL (a load-bearing claim is contradicted by the source).
6. Write your verdict JSON to
   `outputs/ab-plus/_work/<citekey>.verdict.json` as
   `{"citekey": ..., "overall": ..., "per_point": [{"index": ..,
   "verdict": .., "note": ..}], "edits": [..]}` — and do NOT edit
   the entry yourself. Temporary files, if any, go only in the
   per-citekey scratch directory named in the dispatch message.

## Report (returned to the orchestrator)

Overall verdict; count of per-point verdicts by class; the single
most consequential correction, if any; anything in the verdict that
is a judgement call the editor may reasonably decline. UK English.
