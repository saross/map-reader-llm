# AB+ edit brief (apply a verifier's verdict to an entry)

Repo: `/home/shawn/Code/map-reader-llm`. Apply the fresh-context
verifier's edit verdict to one Annotated Bibliography Plus (AB+)
entry, named in your dispatch message. You are a fresh agent: the
drafter's context is gone, and you work from the on-disk artefacts.
Written 2026-09-02 from the pilot's per-entry edit dispatches (S144,
2026-08-30).

## Steps — read, in order

1. `prompts/ab-plus/drafter-brief.md` — the binding rules (quotes
   byte-verbatim with page anchors, 300–500-word summary, UK English,
   salience to the citing paper).
2. `outputs/ab-plus/_work/<citekey>.pages-provenance.md` if it
   exists — OCR or cache caveats; any NEW quote or table number from
   a flagged page must be confirmed against a rendered page image
   (PyMuPDF `get_pixmap` at 200–300 dpi) per that note.
3. The entry: `outputs/ab-plus/_work/<citekey>.entry.json`.
4. The verdict: `outputs/ab-plus/_work/<citekey>.verdict.json`.
5. The source text: `outputs/ab-plus/_work/<citekey>.pages.json` —
   at least every page an edit touches, in context.

## Rules

- Apply EVERY edit in the verdict's `edits` list unless the source
  text contradicts the verifier. The layers check each other: if you
  decline an edit, quote the page span that justifies declining and
  say so in your report (two verifier-side errors were caught this
  way in the pilot). Optional edits are your judgement call.
- Kept quotes stay BYTE-IDENTICAL. If an edit requires a new or
  re-cut quote, it must pass the deterministic checker.
- Edit only interpretive fields (summary, positioning, paraphrases,
  gap labels, framing_hook.note) unless the verdict names a quote.
- Keep the summary inside the 300–500-word band; move a verified
  secondary caveat that will not fit to
  `outputs/ab-plus/_work/<citekey>.overflow-notes.md` rather than
  dropping it.
- Write back with the same JSON formatting (`indent=1`,
  `ensure_ascii=False`). Temporary files only in the per-citekey
  scratch directory named in the dispatch message.
- Re-run
  `PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli check --entry outputs/ab-plus/_work/<citekey>.entry.json`
  — it must PASS.

## Report (returned to the orchestrator)

Per-edit: applied / declined (with the justifying page span) /
adapted (how). Final check verdict (N/N). Summary word count. UK
English.
