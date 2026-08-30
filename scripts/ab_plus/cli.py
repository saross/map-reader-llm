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

from ab_plus.checking import check_entry, format_report
from ab_plus.config import REPO_ROOT, WORK_DIR
from ab_plus.extraction import extract_source, load_cached_pages
from ab_plus.rendering import write_entry
from ab_plus.schema import ENTRY_SCHEMA, validate_entry
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


def _cmd_check(args: argparse.Namespace) -> int:
    """Run the deterministic quote check on an entry JSON file."""
    entry = json.loads(Path(args.entry).read_text(encoding="utf-8"))
    problems = validate_entry(entry)
    if problems:
        print("Structural problems:")
        for p in problems:
            print(f"  - {p}")
    pages = load_cached_pages(entry["citekey"])
    report = check_entry(entry, pages)
    print(format_report(report))
    return 0 if report.all_passed else 2


def _cmd_render(args: argparse.Namespace) -> int:
    """Render an entry JSON (with its check report, optional verdict) to markdown."""
    entry = json.loads(Path(args.entry).read_text(encoding="utf-8"))
    pages = load_cached_pages(entry["citekey"])
    report = check_entry(entry, pages)
    verdict = json.loads(Path(args.verdict).read_text(encoding="utf-8")) if args.verdict else None
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
    path = write_entry(entry, report, verdict, out_dir=out_dir, provenance=provenance)
    print(f"Wrote {path}  ({report.n_passed}/{report.n_quotes} quotes verified)")
    return 0


def _cmd_schema(args: argparse.Namespace) -> int:
    """Print the AB+ entry JSON schema (for the proposer agent)."""
    print(json.dumps(ENTRY_SCHEMA, indent=2))
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

    p_check = sub.add_parser("check", help="deterministic quote check of an entry JSON")
    p_check.add_argument("--entry", required=True, help="path to entry JSON")
    p_check.set_defaults(func=_cmd_check)

    p_render = sub.add_parser("render", help="render an entry JSON to markdown")
    p_render.add_argument("--entry", required=True, help="path to entry JSON")
    p_render.add_argument("--verdict", help="optional verifier verdict JSON")
    p_render.add_argument("--out-dir", help="output dir (default: ab-plus deliverables)")
    p_render.add_argument(
        "--model", help="model ID the workflow pinned for proposer + verifier"
    )
    p_render.add_argument("--run-date", dest="run_date", help="generation run date")
    p_render.add_argument(
        "--workflow-run", dest="workflow_run", help="workflow run ID (wf_...)"
    )
    p_render.set_defaults(func=_cmd_render)

    sub.add_parser("schema", help="print the AB+ entry JSON schema").set_defaults(
        func=_cmd_schema
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
