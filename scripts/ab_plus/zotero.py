"""Resolve BibTeX citekeys to their downloaded PDF files via Zotero.

There is no Better BibTeX database on this machine, so Zotero does not store the
BibTeX citekeys we use in the paper. We therefore *join on title*: the .bib
gives ``citekey -> title``; Zotero's SQLite gives ``title -> PDF attachment``.
Normalising both titles (lowercase, alphanumerics only) makes the join robust to
punctuation, case, and whitespace differences.

The Zotero database is opened **read-only** through an immutable URI, so this
never interferes with a running Zotero and never mutates the library.

Any citekey that fails to resolve is reported rather than silently dropped — a
missing PDF (e.g. Liang 2025) or a group-library item (e.g. Hersh) should be
visible, not swallowed.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .config import COLLECTION_KEY, ZOTERO_DB


@dataclass(frozen=True)
class PdfRef:
    """A resolved source: its citekey, title, Zotero attachment key, and PDF path."""

    citekey: str
    title: str
    attachment_key: str
    pdf_path: Path

    @property
    def exists(self) -> bool:
        """True if the PDF file is actually present on disk."""
        return self.pdf_path.is_file()


def _norm_title(title: str) -> str:
    """Reduce a title to a join key: lowercase, alphanumerics only.

    Drops punctuation, braces, and whitespace so 'LM vs LM: Detecting...' and
    'LM vs LM Detecting...' collide. Markup tags are stripped FIRST: some
    Zotero titles embed literal HTML (e.g. ``<scp>AI</scp>`` from publisher
    metadata), and the alphanumeric reduction alone would leak the tag names
    into the key (``scpaiscp``), silently breaking the join — this defeated
    the Marchionini_2024 resolution (found 2026-07-24). Deliberately
    aggressive — title collisions within a curated bibliography are
    vanishingly unlikely.
    """
    return re.sub(r"[^a-z0-9]+", "", re.sub(r"<[^>]+>", "", title).lower())


def _extract_braced_field(chunk: str, field: str) -> str | None:
    """Extract a brace-delimited BibTeX field value with balanced-brace matching.

    Walks from the field's opening ``{`` to its *matching* close brace, tracking
    nesting depth, so it stops at the right place regardless of what follows
    (a newline in multi-line entries, ``, `` in single-line Crossref entries) and
    correctly handles protective inner braces such as ``{LLMs}``.

    Args:
        chunk: The text of one BibTeX entry.
        field: Field name to extract (case-insensitive), e.g. ``"title"``.

    Returns:
        The raw field value (between the outer braces), or None if absent.
    """
    m = re.search(rf"\b{field}\s*=\s*\{{", chunk, re.IGNORECASE)
    if not m:
        # Quoted-string form (``title = "..."``), used throughout
        # assembly/paper-b.bib. Added 2026-07-24: the brace-only parser
        # silently dropped 22/25 of that file's entries, which crippled any
        # citekey↔title join built on it (first caught in the AB+ audit's
        # reconciliation pass). BibTeX protects literal quotes and accents
        # inside quoted values as brace groups that may CONTAIN a quote
        # (``{\"u}``, ``{"}``), so the scan accepts either a non-quote,
        # non-brace character or a whole single-level brace group. Doubly
        # nested braces inside quoted values are not handled (none occur in
        # the paper's bibs; the braced form covers them).
        q = re.search(
            rf"\b{field}\s*=\s*\"((?:[^\"{{}}]|\{{[^{{}}]*\}})*)\"",
            chunk,
            re.IGNORECASE,
        )
        return q.group(1) if q else None
    depth = 1
    out: list[str] = []
    for ch in chunk[m.end():]:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        out.append(ch)
    return "".join(out)


def _clean_title(raw: str) -> str:
    """Normalise a raw BibTeX title to plain text for joining and display.

    Strips HTML/XML markup (Crossref ships ``<i>``, ``<scp>``, ``<sub>`` …),
    removes protective braces, and collapses whitespace.
    """
    text = re.sub(r"<[^>]+>", "", raw)            # drop markup tags
    text = text.replace("{", "").replace("}", "")  # drop protective braces
    return re.sub(r"\s+", " ", text).strip()


def parse_bib_titles(bib_path: Path) -> dict[str, str]:
    """Extract ``citekey -> title`` from a BibTeX file.

    Handles both entry styles in this .bib: multi-line arXiv ``@misc`` entries
    and single-line Crossref ``@article``/``@inproceedings`` entries. Titles are
    extracted by balanced-brace matching and cleaned of markup.

    Args:
        bib_path: Path to the .bib file.

    Returns:
        Mapping of citekey to its cleaned title.

    Raises:
        FileNotFoundError: If ``bib_path`` does not exist.
    """
    text = bib_path.read_text(encoding="utf-8")
    titles: dict[str, str] = {}
    # Split into entries on '@' at the start of a line; comment lines (% ...)
    # between entries simply do not match the citekey pattern and are skipped.
    for chunk in re.split(r"\n(?=@)", text):
        key_match = re.match(r"@\w+\s*\{\s*([^,\s]+)\s*,", chunk.lstrip())
        if not key_match:
            continue
        raw_title = _extract_braced_field(chunk, "title")
        if raw_title is None:
            continue
        titles[key_match.group(1)] = _clean_title(raw_title)
    return titles


def _query_zotero_pdfs(collection_key: str, db_path: Path) -> list[tuple[str, str, str]]:
    """Return ``(title, attachment_key, storage_path)`` for sources in a collection.

    Walks collections -> collectionItems -> items -> itemAttachments, accepting
    ``application/pdf`` and — since 2026-07-24 — ``text/html`` webpage
    snapshots (some sources, e.g. web-published essays, have only a snapshot;
    an HTML-only item previously surfaced as a false "no PDF attachment"
    miss). Where an item has both, the PDF is preferred. ``storage_path`` is
    the raw ``path`` field (``storage:filename.ext``); the caller turns it
    into an absolute path. Items without any usable attachment are returned
    with empty attachment fields so they remain visible.
    """
    uri = f"file:{db_path}?immutable=1"
    con = sqlite3.connect(uri, uri=True)
    try:
        rows = con.execute(
            """
            SELECT idv.value AS title,
                   COALESCE(att.key, '')        AS att_key,
                   COALESCE(ia.path, '')        AS path,
                   COALESCE(ia.contentType, '') AS ctype,
                   it.itemID                    AS item_id
            FROM collections c
            JOIN collectionItems ci ON ci.collectionID = c.collectionID
            JOIN items it           ON it.itemID = ci.itemID
            JOIN itemData idat       ON idat.itemID = it.itemID
            JOIN fields f            ON f.fieldID = idat.fieldID AND f.fieldName = 'title'
            JOIN itemDataValues idv  ON idv.valueID = idat.valueID
            LEFT JOIN itemAttachments ia
                   ON ia.parentItemID = it.itemID
                  AND ia.contentType IN ('application/pdf', 'text/html')
                  AND ia.itemID NOT IN (SELECT itemID FROM deletedItems)
            LEFT JOIN items att      ON att.itemID = ia.itemID
            WHERE c.key = ?
              AND it.itemID NOT IN (SELECT itemID FROM deletedItems)
            ORDER BY title
            """,
            (collection_key,),
        ).fetchall()
    finally:
        con.close()

    # One row per item: PDF beats HTML snapshot beats no attachment; within a
    # content type, an attachment with a usable stored file beats one without
    # (a linked-URL text/html attachment has contentType set but an empty
    # path — it must not shadow a real snapshot; /audit, 2026-07-24); the
    # attachment key breaks remaining ties so multi-attachment items resolve
    # deterministically.
    ctype_rank = {"application/pdf": 0, "text/html": 1, "": 2}
    best: dict[int, tuple[tuple[int, int, str], tuple[str, str, str]]] = {}
    for title, att_key, path, ctype, item_id in rows:
        usable = 0 if path.startswith("storage:") else 1
        rank = (ctype_rank.get(ctype, 2), usable, att_key)
        if item_id not in best or rank < best[item_id][0]:
            best[item_id] = (rank, (title, att_key, path))
    return sorted((rec for _, rec in best.values()), key=lambda r: r[0])


def _storage_path_to_file(attachment_key: str, stored_path: str) -> Path | None:
    """Turn a Zotero ``storage:`` path into an absolute file path.

    Zotero stores attachment files at ``~/Zotero/storage/<attachment_key>/<file>``
    where ``<file>`` is the part after the ``storage:`` prefix.
    """
    if not stored_path.startswith("storage:") or not attachment_key:
        return None
    filename = stored_path[len("storage:"):]
    return ZOTERO_DB.parent / "storage" / attachment_key / filename


# Minimum normalised-title length for the containment fallback to fire, so a
# very short title cannot spuriously match a longer unrelated one.
_CONTAINMENT_MIN_LEN: int = 12


def _join_titles(
    bib_titles: dict[str, str],
    zotero_rows: list[tuple[str, str, str]],
) -> dict[str, tuple[str, str, str]]:
    """Match each bib citekey to a Zotero row by title, in two passes.

    Pass 1 is exact normalised-title equality. Pass 2 is a containment fallback
    for the remaining citekeys: it accepts a Zotero row whose normalised title
    is a substring of the bib's (or vice versa) — this bridges cases where
    Zotero stores an abbreviated title (e.g. 'To Trust or to Think' for an entry
    whose full title carries a subtitle). The fallback fires only when the
    shorter title is at least :data:`_CONTAINMENT_MIN_LEN` characters and the
    match is *unique* among unconsumed rows, so it stays safe on a curated set.

    Each Zotero row is consumed by at most one citekey.

    Args:
        bib_titles: citekey -> cleaned title.
        zotero_rows: ``(title, attachment_key, path)`` tuples from the collection.

    Returns:
        Mapping of citekey -> matched Zotero row.
    """
    rows_norm = [(_norm_title(t), (t, a, p)) for t, a, p in zotero_rows]
    consumed: set[int] = set()
    matches: dict[str, tuple[str, str, str]] = {}

    # Pass 1: exact normalised-title equality.
    for citekey, bib_title in bib_titles.items():
        nb = _norm_title(bib_title)
        for i, (nz, row) in enumerate(rows_norm):
            if i in consumed:
                continue
            if nz == nb:
                matches[citekey] = row
                consumed.add(i)
                break

    # Pass 2: containment fallback for still-unmatched citekeys.
    for citekey, bib_title in bib_titles.items():
        if citekey in matches:
            continue
        nb = _norm_title(bib_title)
        candidates = [
            i
            for i, (nz, _row) in enumerate(rows_norm)
            if i not in consumed
            and min(len(nz), len(nb)) >= _CONTAINMENT_MIN_LEN
            and (nz in nb or nb in nz)
        ]
        if len(candidates) == 1:
            i = candidates[0]
            matches[citekey] = rows_norm[i][1]
            consumed.add(i)

    return matches


def resolve_collection(
    collection_key: str = COLLECTION_KEY,
    bib_path: Path | None = None,
    db_path: Path | None = None,
) -> tuple[dict[str, PdfRef], list[str]]:
    """Resolve every citekey in the .bib to its PDF in the Zotero collection.

    Args:
        collection_key: Zotero collection key to look in.
        bib_path: BibTeX file (defaults to :data:`config.BIB_PATH`).
        db_path: Zotero SQLite path (defaults to :data:`config.ZOTERO_DB`).

    Returns:
        A pair ``(resolved, unresolved)`` where ``resolved`` maps citekey ->
        :class:`PdfRef` (only entries with a PDF present on disk) and
        ``unresolved`` is a sorted list of citekeys that could not be matched to
        a present PDF, each annotated with the reason.
    """
    from .config import BIB_PATH

    bib_path = bib_path or BIB_PATH
    db_path = db_path or ZOTERO_DB

    bib_titles = parse_bib_titles(bib_path)
    zotero_rows = _query_zotero_pdfs(collection_key, db_path)
    matches = _join_titles(bib_titles, zotero_rows)

    resolved: dict[str, PdfRef] = {}
    unresolved: list[str] = []
    for citekey, bib_title in bib_titles.items():
        match = matches.get(citekey)
        if match is None:
            unresolved.append(f"{citekey} (no Zotero item in collection — title join failed)")
            continue
        z_title, att_key, stored_path = match
        pdf_path = _storage_path_to_file(att_key, stored_path)
        if pdf_path is None:
            unresolved.append(
                f"{citekey} (Zotero item has no PDF or HTML-snapshot attachment)"
            )
            continue
        ref = PdfRef(citekey=citekey, title=z_title, attachment_key=att_key, pdf_path=pdf_path)
        if not ref.exists:
            unresolved.append(f"{citekey} (PDF path recorded but file absent: {pdf_path})")
            continue
        resolved[citekey] = ref

    return resolved, sorted(unresolved)
