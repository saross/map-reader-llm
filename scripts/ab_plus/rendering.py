"""Render a verified AB+ entry to its markdown deliverable.

Turns the structured entry (proposer output), the deterministic check report,
and the optional verifier verdict into the per-source ``.md`` file, matching the
format of the hand-drafted ``huang2023large.md`` locked during co-design.

Two anti-confabulation choices:

* the **full citation is read from the .bib**, not from the LLM — the proposer
  never reproduces bibliographic metadata it could get subtly wrong;
* the **verified locator wins** — if the deterministic checker found a quote on a
  different page than the proposer claimed, the renderer prints the verified
  page and flags the correction.

Printed page numbers are rendered as ``page_index + 1`` (best-effort: correct for
this corpus, where the PDF front matter aligns; labelled as such).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .checking import CheckReport, QuoteStatus
from .config import AB_PLUS_DIR, BIB_PATH
from .zotero import _extract_braced_field


def _display_quote(quote: str) -> str:
    """Collapse intra-quote whitespace for readable display.

    The verbatim quote stored in the entry preserves the source's mid-sentence
    newlines (from two-column PDF extraction) so it matches the deterministic
    checker exactly. For the rendered deliverable those newlines read as ragged
    line breaks, so we collapse all whitespace runs to single spaces. This is
    the agreed cleanup-on-display step; it does NOT repair de-hyphenation
    artefacts (e.g. 'selfcorrect'), whose proper fix is logged in
    llm-reproducibility (task C).
    """
    return re.sub(r"\s+", " ", quote).strip()


def _bib_fields(citekey: str, bib_path: Path | None = None) -> dict[str, str]:
    """Pull author/year/title/journal/doi for a citekey from the .bib.

    Best-effort and tolerant: any field that is absent is simply omitted.
    """
    import re

    bib_path = bib_path or BIB_PATH
    text = bib_path.read_text(encoding="utf-8")
    for chunk in re.split(r"\n(?=@)", text):
        m = re.match(r"@\w+\s*\{\s*([^,\s]+)\s*,", chunk.lstrip())
        if not m or m.group(1) != citekey:
            continue
        fields: dict[str, str] = {}
        for name in ("author", "title", "year", "journal", "booktitle", "doi", "eprint"):
            raw = _extract_braced_field(chunk, name)
            if raw is not None:
                fields[name] = re.sub(r"<[^>]+>", "", raw).replace("{", "").replace("}", "").strip()
        return fields
    return {}


def _format_authors(author_field: str) -> str:
    """Format a BibTeX ``and``-separated author list for display."""
    authors = [a.strip() for a in author_field.split(" and ") if a.strip()]
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) <= 3:
        return ", ".join(authors[:-1]) + " & " + authors[-1]
    return authors[0] + " et al."


def _format_cite(citekey: str) -> str:
    """Build a plain-text citation for a citekey from the .bib (best-effort)."""
    f = _bib_fields(citekey)
    if not f:
        return f"(citation unavailable for {citekey})"
    parts: list[str] = []
    if "author" in f:
        parts.append(_format_authors(f["author"]))
    if "year" in f:
        parts.append(f"({f['year']})")
    if "title" in f:
        parts.append(f"*{f['title']}.*")
    venue = f.get("journal") or f.get("booktitle")
    if venue:
        parts.append(f"{venue}.")
    if "doi" in f:
        parts.append(f"DOI: {f['doi']}")
    elif "eprint" in f:
        parts.append(f"arXiv:{f['eprint']}")
    return " ".join(parts)


def _printed(page_index: int) -> str:
    """Best-effort printed-page label for a 0-based page index."""
    return f"p.{page_index + 1}"


def _verified_page(report: CheckReport, role: str, index: int) -> tuple[int | None, str]:
    """Return ``(authoritative_page, note)`` for one quote from the check report.

    The authoritative page is the verified one when the checker found the quote;
    the note flags a locator correction or a failure.
    """
    for r in report.results:
        if r.role == role and r.index == index:
            if r.status is QuoteStatus.PASS:
                return r.claimed_page, ""
            if r.status is QuoteStatus.LOCATOR_MISMATCH:
                pg = r.verified_pages[0] if r.verified_pages else r.claimed_page
                return pg, f" *(locator corrected from claimed p{r.claimed_page})*"
            return r.claimed_page, " *(⚠ NOT FOUND in source — quote suspect)*"
    return None, ""


def render_entry(
    entry: dict[str, Any],
    report: CheckReport,
    verdict: dict[str, Any] | None = None,
    provenance: dict[str, str] | None = None,
) -> str:
    """Render an AB+ entry to markdown.

    Args:
        entry: The structured AB+ entry (proposer output).
        report: The deterministic quote-check report for this entry.
        verdict: Optional independent-verifier output (advisory flags).
        provenance: Optional generation provenance stamped into the
            auto-generated block. Recognised keys: ``model`` (the model ID
            requested for the proposer + verifier agents), ``run_date``,
            ``workflow_run`` (the ``wf_`` run ID), ``pipeline_rev`` (git
            short hash of the pipeline at render time). Added 2026-07-24:
            session metadata and commit trailers both proved unreliable for
            model attribution, so the artefact must carry its own stamp.

    Returns:
        The markdown document as a string.
    """
    citekey = entry.get("citekey", "<unknown>")
    title = _bib_fields(citekey).get("title", citekey)
    lines: list[str] = []

    lines.append(f"# AB+ — {title}")
    lines.append("")
    lines.append("| field | value |")
    lines.append("|---|---|")
    lines.append(f"| **citekey** | `{citekey}` |")
    lines.append(f"| **full cite** | {_format_cite(citekey)} |")
    if entry.get("register"):
        lines.append(f"| **register** | {entry['register']} |")
    if entry.get("primary_gap"):
        lines.append(f"| **primary gap** | {entry['primary_gap']} |")
    if entry.get("also_touches"):
        lines.append(f"| **also touches** | {'; '.join(entry['also_touches'])} |")
    lines.append(
        "| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |"
    )
    lines.append("")

    lines.append("## Summary (Claude's synthesis — advisory, unverified)")
    lines.append("")
    lines.append(entry.get("summary", "").strip())
    lines.append("")

    lines.append("## Positioning annotation (interpretive)")
    lines.append("")
    lines.append(entry.get("positioning", "").strip())
    lines.append("")

    lines.append("## Key points (salience-ranked to the citing paper)")
    lines.append("")
    for i, kp in enumerate(entry.get("key_points", [])):
        page, note = _verified_page(report, "key_point", i)
        loc_bits = [f"page_index {page}", _printed(page) if page is not None else ""]
        if kp.get("section"):
            loc_bits.append(kp["section"])
        locator = " · ".join(b for b in loc_bits if b) + note
        stance = kp.get("relevance_stance", "")
        rel = " · ".join(
            b for b in [kp.get("relevance_section"), kp.get("relevance_gap"),
                        f"**{stance}**" if stance else ""] if b
        )
        lines.append(f"### KP{i + 1}")
        lines.append(f'- **Quote (verbatim):** "{_display_quote(kp.get("quote", ""))}"')
        lines.append(f"- **Locator:** {locator}")
        lines.append(f"- **Paraphrase:** {kp.get('paraphrase', '').strip()}")
        lines.append(f"- **Relevance:** {rel}")
        lines.append("")

    hook = entry.get("framing_hook")
    if hook:
        page, note = _verified_page(report, "framing_hook", 0)
        loc = f"page_index {page} · {_printed(page)}" if page is not None else ""
        lines.append("## Optional framing hook (not counted in the salience cap)")
        lines.append("")
        lines.append(f'- **Quote (verbatim):** "{_display_quote(hook.get("quote", ""))}"')
        lines.append(f"- **Locator:** {loc}{note}")
        if hook.get("note"):
            lines.append(f"- **Why:** {hook['note'].strip()}")
        lines.append("")

    # --- Auto-generated provenance block ---
    lines.append("## Extraction / fidelity notes (auto-generated)")
    lines.append("")
    lines.append(
        f"- Deterministic quote check: **{report.n_passed}/{report.n_quotes} passed**"
        + ("  — ⚠ FABRICATION DETECTED" if report.has_fabrication else ".")
    )
    for r in report.failures:
        lines.append(
            f"  - `{r.status.value}` {r.role}[{r.index}]: claimed p{r.claimed_page}, "
            f"found {r.verified_pages or 'nowhere'} — “{r.quote_preview}”"
        )
    if provenance:
        # Sanitise: a backtick or newline in a value would break the code
        # span / list structure. Values are operator-supplied CLI flags, so
        # this guards against accidents, not adversaries.
        def _prov(key: str) -> str:
            value = provenance.get(key) or ""
            return value.replace("`", "'").replace("\n", " ").replace("\r", " ")

        bits: list[str] = []
        if _prov("model"):
            # "requested": the stamp records what the workflow asked for; the
            # archived per-message transcript fields remain ground truth for
            # the resolved model (verified equal for claude-opus-4-8 by the
            # 2026-07-24 dispatch probe).
            bits.append(f"model `{_prov('model')}` requested (proposer + verifier)")
        if _prov("run_date"):
            bits.append(f"run {_prov('run_date')}")
        if _prov("workflow_run"):
            bits.append(f"workflow `{_prov('workflow_run')}`")
        if _prov("pipeline_rev"):
            bits.append(f"pipeline rev `{_prov('pipeline_rev')}`")
        if bits:
            lines.append(f"- Generated by: {'; '.join(bits)}.")
    if verdict:
        lines.append("")
        lines.append("## Independent verifier (advisory — flags only)")
        lines.append("")
        if "per_point" in verdict:
            # Per-point shape (map-reader-llm pilot, 2026-08-30): one verdict
            # per key point plus the edit list the post-verdict edit pass
            # applies before render. Rendered since 2026-09-02 — the pilot's
            # first render used only the flag-list branch below, which
            # printed "none" for entries carrying OVERREACH verdicts.
            for pp in verdict.get("per_point") or []:
                idx = pp.get("index")
                label = f"KP{idx + 1}" if isinstance(idx, int) else "KP?"
                note = str(pp.get("note", "")).strip()
                lines.append(f"- **{label}: {pp.get('verdict', '?')}** — {note}")
            edits = verdict.get("edits") or []
            if edits:
                lines.append(
                    "- **requested edits** (applied to the entry by the edit pass "
                    "before render; kept quotes byte-identical):"
                )
                for ed in edits:
                    lines.append(f"  - {ed}")
            else:
                lines.append("- **requested edits:** none")
        else:
            for key in ("paraphrase_flags", "summary_flags", "relevance_flags"):
                flags = verdict.get(key) or []
                label = key.replace("_", " ")
                if flags:
                    lines.append(f"- **{label}:**")
                    for fl in flags:
                        lines.append(f"  - {fl}")
                else:
                    lines.append(f"- **{label}:** none")
        if verdict.get("overall"):
            lines.append(f"- **overall:** {verdict['overall']}")
    lines.append("")
    return "\n".join(lines)


def write_entry(
    entry: dict[str, Any],
    report: CheckReport,
    verdict: dict[str, Any] | None = None,
    out_dir: Path | None = None,
    provenance: dict[str, str] | None = None,
) -> Path:
    """Render an entry and write it to ``<out_dir>/<citekey-lower>.md``.

    Args:
        entry: The structured AB+ entry.
        report: The deterministic quote-check report.
        verdict: Optional verifier output.
        out_dir: Output directory (defaults to the ab-plus deliverables dir).
        provenance: Optional generation provenance (see ``render_entry``).

    Returns:
        The path written.
    """
    out_dir = out_dir or AB_PLUS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{entry.get('citekey', 'entry').lower()}.md"
    path.write_text(
        render_entry(entry, report, verdict, provenance=provenance),
        encoding="utf-8",
    )
    return path
