"""Command-line interface for the deterministic AB+ steps.

Wraps the non-LLM parts of the pipeline so they can be driven from the shell (or
from a workflow agent via Bash): resolve citekeys to PDFs, extract page text,
run the deterministic quote check, render an entry to markdown, and dump the
proposer schema.

Must be run with a Python that has PyMuPDF — the repo-local venv
(``python3 -m venv .venv && .venv/bin/pip install -r requirements.txt``),
e.g.::

    PY=.venv/bin/python
    $PY scripts/ab_plus/cli.py resolve
    $PY scripts/ab_plus/cli.py extract --citekey Huang2023large
    $PY scripts/ab_plus/cli.py check  --entry _work/Huang2023large.entry.json
    $PY scripts/ab_plus/cli.py render --entry _work/Huang2023large.entry.json

The LLM steps (proposer, verifier) live in the workflow, not here.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Allow running as a plain script (python scripts/ab_plus/cli.py ...).
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ab_plus.checking import check_entry, check_overflow, format_report
from ab_plus.config import REPO_ROOT, WORK_DIR
from ab_plus.extraction import extract_source, load_cached_pages
from ab_plus.gate import assess_cache, format_table
from ab_plus.ocr_repair import ocr_repair
from ab_plus.rendering import _bib_fields, write_entry
from ab_plus.schema import (
    ENTRY_SCHEMA,
    OVERFLOW_SCHEMA,
    entry_warnings,
    validate_entry,
    validate_overflow,
    validate_verdict,
)
from ab_plus.zotero import resolve_collection


def _pipeline_rev() -> str:
    """Return the repo's git revision (``--dirty``-aware), or '' if unavailable.

    Best-effort provenance: the revision identifies the pipeline code that
    rendered the entry, complementing the model/run stamps passed by the
    caller. ``--dirty`` is honest about uncommitted pipeline changes.
    """
    try:
        return subprocess.run(
            ["git", "-C", str(REPO_ROOT), "describe", "--always", "--dirty"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout.strip()
    except Exception:
        return ""


def _resolve_kwargs(args: argparse.Namespace) -> dict:
    """Build resolve_collection() overrides from the optional CLI flags.

    Returns only the overrides actually supplied, so defaults in config.py
    (tranche-1: COLLECTION_KEY/BIB_PATH) continue to apply when flags are
    omitted. Added 2026-06-12 for tranche-2 (different Zotero subcollection
    and bib slice per tranche).
    """
    kwargs: dict = {}
    if getattr(args, "collection_key", None):
        kwargs["collection_key"] = args.collection_key
    if getattr(args, "bib", None):
        kwargs["bib_path"] = Path(args.bib)
    return kwargs


def _cmd_resolve(args: argparse.Namespace) -> int:
    """Resolve citekeys to PDFs and write the map to _work/."""
    resolved, unresolved = resolve_collection(**_resolve_kwargs(args))
    print(f"Resolved {len(resolved)} citekeys; {len(unresolved)} unresolved.")
    for u in unresolved:
        print(f"  unresolved: {u}")
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    out = WORK_DIR / "citekey-pdf-map.json"
    out.write_text(
        json.dumps(
            {ck: str(ref.pdf_path) for ck, ref in sorted(resolved.items())},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {out}")
    return 0


def _cmd_extract(args: argparse.Namespace) -> int:
    """Extract page text for one citekey (or all resolved) into the cache."""
    resolved, _ = resolve_collection(**_resolve_kwargs(args))
    if args.citekey:
        targets = {args.citekey: resolved.get(args.citekey)}
    else:
        targets = resolved
    rc = 0
    for ck, ref in targets.items():
        if ref is None:
            print(f"  {ck}: NOT RESOLVED (no PDF)")
            rc = 1
            continue
        pages = extract_source(ck, ref.pdf_path, force=args.force)
        print(f"  {ck}: {len(pages)} pages cached")
    return rc


def _cmd_gate(args: argparse.Namespace) -> int:
    """Classify page caches as PASS/WARN/FAIL before any drafter launches.

    Added 2026-09-02 (pilot amendment 1): a watermark-only text layer evaded
    the pilot's zero-length check. Exit 2 if any cache FAILs.
    """
    if args.citekey:
        citekeys = [args.citekey]
    else:
        citekeys = sorted(
            p.name[: -len(".pages.json")] for p in WORK_DIR.glob("*.pages.json")
        )
    # Content heuristics (2026-09-03) use the source's DOI, when the .bib has
    # one, to tell a sibling article's DOI from the source's own.
    results = [
        assess_cache(
            ck,
            load_cached_pages(ck),
            min_chars_per_page=args.min_chars_per_page,
            source_doi=_bib_fields(ck).get("doi"),
        )
        for ck in citekeys
    ]
    print(format_table(results))
    return 2 if any(r.verdict == "FAIL" for r in results) else 0


def _cmd_ocr_repair(args: argparse.Namespace) -> int:
    """Rebuild one FAILed page cache by OCR and write its provenance note."""
    resolved, _ = resolve_collection(**_resolve_kwargs(args))
    ref = resolved.get(args.citekey)
    if ref is None:
        print(f"  {args.citekey}: NOT RESOLVED (no PDF)")
        return 1
    rotate: dict[int, int] = {}
    for spec in args.rotate or []:
        idx, deg = spec.split(":")
        rotate[int(idx)] = int(deg)
    note = ocr_repair(
        args.citekey, ref.pdf_path, dpi=args.dpi, rotate=rotate, force=args.force
    )
    pages = load_cached_pages(args.citekey)
    result = assess_cache(args.citekey, pages)
    print(f"  {args.citekey}: {len(pages)} pages OCR'd, {result.n_chars} chars; "
          f"gate now {result.verdict} {result.reason}")
    print(f"  provenance note: {note}")
    return 0


def _overflow_path(citekey: str) -> Path:
    """Where the overflow sidecar for a citekey lives (may not exist)."""
    return WORK_DIR / f"{citekey}.overflow.json"


def _load_overflow(citekey: str, explicit: str | None) -> dict | None:
    """Load the overflow sidecar named on the CLI or auto-detected in _work/."""
    path = Path(explicit) if explicit else _overflow_path(citekey)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _cmd_check(args: argparse.Namespace) -> int:
    """Run the deterministic quote check on an entry JSON file.

    Since 2026-09-03 also prints advisory band warnings (never failing) and,
    when an overflow sidecar exists for the citekey, checks its spans too —
    a failed overflow span fails the check, because the appendix would
    otherwise publish a paraphrase whose anchor cannot be verified.
    """
    entry = json.loads(Path(args.entry).read_text(encoding="utf-8"))
    problems = validate_entry(entry)
    if problems:
        print("Structural problems:")
        for p in problems:
            print(f"  - {p}")
    for w in entry_warnings(entry):
        print(f"Advisory: {w}")
    pages = load_cached_pages(entry["citekey"])
    report = check_entry(entry, pages)
    print(format_report(report))
    rc = 0 if report.all_passed else 2
    overflow = _load_overflow(entry["citekey"], getattr(args, "overflow", None))
    if overflow is not None:
        for p in validate_overflow(overflow):
            print(f"Overflow structural problem: {p}")
            rc = 2
        oreport = check_overflow(overflow, pages)
        print(format_report(oreport).replace("Quote check", "Overflow span check", 1))
        if not oreport.all_passed:
            rc = 2
    return rc


def _cmd_render(args: argparse.Namespace) -> int:
    """Render an entry JSON (with its check report, optional verdict) to markdown."""
    entry = json.loads(Path(args.entry).read_text(encoding="utf-8"))
    pages = load_cached_pages(entry["citekey"])
    report = check_entry(entry, pages)
    verdict = json.loads(Path(args.verdict).read_text(encoding="utf-8")) if args.verdict else None
    if verdict is not None:
        # Enforced since 2026-09-03: a verdict outside the vocabulary must
        # not reach the deliverable silently (the tail rendered one).
        problems = validate_verdict(verdict)
        if problems:
            print("Verdict problems (not rendered):", file=sys.stderr)
            for p in problems:
                print(f"  - {p}", file=sys.stderr)
            return 2
    for w in entry_warnings(entry):
        print(f"Advisory: {w}", file=sys.stderr)
    overflow = _load_overflow(entry["citekey"], args.overflow)
    overflow_report = None
    if overflow is not None:
        problems = validate_overflow(overflow)
        if problems:
            print("Overflow problems (not rendered):", file=sys.stderr)
            for p in problems:
                print(f"  - {p}", file=sys.stderr)
            return 2
        overflow_report = check_overflow(overflow, pages)
    out_dir = Path(args.out_dir) if args.out_dir else None
    # Generation provenance (2026-07-24): the caller passes the model/run
    # identity the workflow pinned; the git revision is derived here. Only an
    # artefact-local stamp survives session-metadata and commit-trailer drift.
    # Gated on caller-supplied fields: a bare `render` must reproduce the
    # committed corpus byte-for-byte (a rev-only stamp broke re-render
    # idempotency and implied provenance where the model was unknown —
    # /audit finding, 2026-07-24).
    supplied = {
        "model": args.model or "",
        "run_date": args.run_date or "",
        "workflow_run": args.workflow_run or "",
    }
    supplied = {k: v for k, v in supplied.items() if v}
    provenance = {**supplied, "pipeline_rev": _pipeline_rev()} if supplied else None
    if not args.model:
        print(
            "NOTE: no --model supplied; entry rendered without generation "
            "provenance (pass --model/--run-date/--workflow-run on real runs).",
            file=sys.stderr,
        )
    path = write_entry(
        entry, report, verdict, out_dir=out_dir, provenance=provenance,
        overflow=overflow, overflow_report=overflow_report,
    )
    extra = (
        f"; overflow {overflow_report.n_passed}/{overflow_report.n_quotes}"
        if overflow_report is not None else ""
    )
    print(f"Wrote {path}  ({report.n_passed}/{report.n_quotes} quotes verified{extra})")
    return 0


def _cmd_schema(args: argparse.Namespace) -> int:
    """Print the AB+ entry JSON schema (or, with --overflow, the sidecar schema)."""
    print(json.dumps(OVERFLOW_SCHEMA if args.overflow else ENTRY_SCHEMA, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(prog="ab_plus", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_resolve = sub.add_parser("resolve", help="resolve citekeys to PDFs; write the map")
    p_resolve.add_argument("--collection-key", help="Zotero collection key (default: config)")
    p_resolve.add_argument("--bib", help="BibTeX file for citekeys (default: config)")
    p_resolve.set_defaults(func=_cmd_resolve)

    p_extract = sub.add_parser("extract", help="extract + cache page text")
    p_extract.add_argument("--citekey", help="single citekey; omit for all resolved")
    p_extract.add_argument("--force", action="store_true", help="re-extract even if cached")
    p_extract.add_argument("--collection-key", help="Zotero collection key (default: config)")
    p_extract.add_argument("--bib", help="BibTeX file for citekeys (default: config)")
    p_extract.set_defaults(func=_cmd_extract)

    p_gate = sub.add_parser("gate", help="pre-flight cache-quality gate (PASS/WARN/FAIL)")
    p_gate.add_argument("--citekey", help="single citekey; omit for every cached source")
    p_gate.add_argument(
        "--min-chars-per-page", type=int, default=1000, dest="min_chars_per_page",
        help="thin-cache threshold (default 1000)",
    )
    p_gate.set_defaults(func=_cmd_gate)

    p_ocr = sub.add_parser("ocr-repair", help="rebuild a FAILed page cache by OCR")
    p_ocr.add_argument("--citekey", required=True, help="citekey whose cache to rebuild")
    p_ocr.add_argument("--dpi", type=int, default=300, help="render dpi (default 300)")
    p_ocr.add_argument(
        "--rotate", action="append", metavar="PAGE:DEG",
        help="rotate a page before OCR, e.g. --rotate 12:90 (repeatable)",
    )
    p_ocr.add_argument("--force", action="store_true", help="OCR even if the gate passes")
    p_ocr.add_argument("--collection-key", help="Zotero collection key (default: config)")
    p_ocr.add_argument("--bib", help="BibTeX file for citekeys (default: config)")
    p_ocr.set_defaults(func=_cmd_ocr_repair)

    p_check = sub.add_parser("check", help="deterministic quote check of an entry JSON")
    p_check.add_argument("--entry", required=True, help="path to entry JSON")
    p_check.add_argument(
        "--overflow", help="overflow sidecar JSON (default: _work/<citekey>.overflow.json if present)"
    )
    p_check.set_defaults(func=_cmd_check)

    p_render = sub.add_parser("render", help="render an entry JSON to markdown")
    p_render.add_argument("--entry", required=True, help="path to entry JSON")
    p_render.add_argument("--verdict", help="optional verifier verdict JSON")
    p_render.add_argument(
        "--overflow", help="overflow sidecar JSON (default: _work/<citekey>.overflow.json if present)"
    )
    p_render.add_argument("--out-dir", help="output dir (default: ab-plus deliverables)")
    p_render.add_argument(
        "--model", help="model ID the workflow pinned for proposer + verifier"
    )
    p_render.add_argument("--run-date", dest="run_date", help="generation run date")
    p_render.add_argument(
        "--workflow-run", dest="workflow_run", help="workflow run ID (wf_...)"
    )
    p_render.set_defaults(func=_cmd_render)

    p_schema = sub.add_parser("schema", help="print the AB+ entry JSON schema")
    p_schema.add_argument(
        "--overflow", action="store_true", help="print the overflow sidecar schema instead"
    )
    p_schema.set_defaults(func=_cmd_schema)
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
