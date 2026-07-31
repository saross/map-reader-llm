#!/usr/bin/env python3
"""Recompute and diff C4 quantitative claims against their anchors.

Phase 3 harness (``planning/audit-charter.md`` § 7): consumes validated
extraction files from ``reports/verification/c4-extraction/``, resolves
each claim's anchor, and compares every quoted value against the source
at quoted precision (``scripts/lib_c4_compare.py``). Purely mechanical —
no LLM judgement; anything unresolvable is bucketed for triage, never
guessed.

Per-value statuses:

- ``MATCH`` — source reproduces the quoted value (mode records
  exact/round/truncate/percent-rescaled).
- ``MISMATCH`` — source value found but does not reproduce the quote.
- ``APPROX`` — approx-marked quote (``~``); computed error recorded,
  triage decides.
- ``UNRESOLVED`` — anchor/path/operand failed to resolve (reason given).
- ``SKIPPED`` — method out of mechanical scope (recompute-script,
  regen-diff, historical, unverifiable-era, external, anchor-unknown).

Path extension over the lib resolver: a ``len:`` prefix counts the
resolved collection (GeoJSON feature counts etc.).

Usage::

    python3 scripts/recompute_c4_claims.py [paths...] [--out reports/verification/c4-recompute-report.json]
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_c4_compare import (  # noqa: E402
    match_at_quoted_precision,
    normalise_path,
    parse_value,
    resolve_path,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = REPO_ROOT / "reports" / "verification" / "c4-extraction"
DEFAULT_OUT = REPO_ROOT / "reports" / "verification" / "c4-recompute-report.json"

MECHANICAL = {"read", "arithmetic"}
_ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name,
                  ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd,
                  ast.Pow)

_json_cache: dict[str, object] = {}


def load_json(relpath: str):
    """Load (and cache) a committed JSON artefact by repo-relative path.

    Raises:
        KeyError: For non-JSON anchors (``.py``, ``.md``, images…) — a
            clean triage reason instead of a parser stack trace.
    """
    if not relpath.endswith((".json", ".geojson")):
        raise KeyError(f"non-JSON anchor {relpath} (triage scope)")
    if relpath not in _json_cache:
        _json_cache[relpath] = json.loads(
            (REPO_ROOT / relpath).read_text(encoding="utf-8")
        )
    return _json_cache[relpath]


def resolve_anchor_value(file: str, path: str):
    """Resolve a value from an anchor file.

    Handles, beyond a plain JSONPath: the cross-file ``<file>#<path>``
    locator form (the named file overrides ``file``); the ``len:``
    prefix and its corpus spellings (``len($.x)``, ``$.x.length``,
    ``(array length)`` / ``(distinct count)`` annotations — via
    :func:`normalise_path`); and ``[*]`` wildcard results, which
    collapse to a scalar only when every element agrees (a constant
    asserted across a collection), else fail loudly.

    Raises:
        KeyError: On any resolution failure (message says why).
    """
    path = path.strip()
    if "#" in path and not path.startswith(("$", "len:")):
        override, _, subpath = path.partition("#")
        if not subpath:
            raise KeyError(f"file#path locator missing path part: {path!r}")
        file, path = override.strip(), subpath.strip()
    obj = load_json(file)
    # Plain resolution first so a genuine key named ``length`` wins;
    # the length/count spellings are retried only when it fails.
    collection_op = None
    try:
        value = resolve_path(obj, path)
    except KeyError:
        stripped, collection_op = normalise_path(path)
        if collection_op is None:
            raise
        value = resolve_path(obj, stripped)
    if collection_op == "len":
        try:
            return len(value)
        except TypeError as exc:
            raise KeyError(f"len: target not sized ({exc})") from exc
    if collection_op == "distinct":
        try:
            return len(set(value))
        except TypeError as exc:
            raise KeyError(f"distinct-count target not hashable ({exc})") from exc
    if isinstance(value, list):
        unique = {repr(element) for element in value}
        if len(unique) == 1:
            return value[0]
        raise KeyError(
            f"[*] resolved {len(value)} elements with {len(unique)} distinct "
            f"values (a scalar quote needs a constant collection): {path!r}")
    return value


def safe_eval(expression: str, names: dict[str, float]) -> float:
    """Evaluate an arithmetic expression over named operands.

    Only literals, single-letter names, + - * / ** and unary signs are
    permitted (schema-constrained upstream).

    Raises:
        ValueError: On disallowed syntax or unknown names.
    """
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"unparseable expression {expression!r}: {exc}") from exc
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"disallowed syntax {type(node).__name__} in {expression!r}")
        if isinstance(node, ast.Name) and node.id not in names:
            raise ValueError(f"unknown operand {node.id!r} in {expression!r}")
    return float(eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, names))


def compare(quoted_verbatim: str, actual, unit: str | None = None) -> dict:
    """Compare a source value against a verbatim quote at quoted precision.

    Args:
        quoted_verbatim: The value span exactly as quoted.
        actual: The recomputed/read source value.
        unit: The extraction's ``unit`` field — consulted for the
            percentage bridge when the verbatim itself lost the sign
            (a shared ``%`` across a quoted range).
    """
    quoted = parse_value(quoted_verbatim)
    if quoted is None:
        return {"status": "UNRESOLVED", "reason": f"unparseable quote {quoted_verbatim!r}"}
    try:
        actual_f = float(actual)
    except (TypeError, ValueError):
        return {"status": "UNRESOLVED", "reason": f"non-numeric source value {actual!r}"}
    result = match_at_quoted_precision(quoted, actual_f)
    # Percentage scale bridge: quoted "92.0 %" vs source fraction 0.9203.
    percentish = quoted.is_percentage or (unit or "").strip() == "%"
    if not result["match"] and percentish and abs(actual_f) <= 1.0 < abs(quoted.value):
        rescaled = match_at_quoted_precision(quoted, actual_f * 100.0)
        if rescaled["match"]:
            return {"status": "MATCH", "mode": "percent-rescaled",
                    "actual": actual_f * 100.0, "abs_error": rescaled["abs_error"]}
    if result["match"]:
        return {"status": "MATCH", "mode": result["mode"],
                "actual": result["actual"], "abs_error": result["abs_error"]}
    status = "APPROX" if result["mode"] == "approx" else "MISMATCH"
    return {"status": status, "mode": result["mode"],
            "actual": result["actual"], "abs_error": result["abs_error"]}


def process_claim(batch: str, index: int, claim: dict) -> list[dict]:
    """Produce one report row per value in a claim."""
    rows: list[dict] = []
    anchor = claim["anchor"]
    for vi, value in enumerate(claim["values"]):
        method = value.get("method") or claim["method"]
        row = {
            "batch": batch, "claim_index": index, "value_index": vi,
            "method": method, "quantity": value["quantity"],
            "value_verbatim": value["value_verbatim"],
        }
        if method not in MECHANICAL:
            row.update(status="SKIPPED", reason=f"method {method} is triage/deferred scope")
            rows.append(row)
            continue
        try:
            if method == "read":
                path = value.get("path") or (anchor.get("path") if anchor else None)
                if not anchor or not path:
                    row.update(status="UNRESOLVED", reason="read claim without anchor path")
                else:
                    actual = resolve_anchor_value(anchor["file"], path)
                    row.update(compare(value["value_verbatim"], actual,
                                       unit=value.get("unit")))
            else:  # arithmetic — value-level expression (schema 1.1) wins
                source = value if value.get("expression") else (anchor or {})
                operands = source.get("operands") or []
                expr = source.get("expression") or ""
                names = {op["name"]: float(resolve_anchor_value(op["file"], op["path"]))
                         for op in operands}
                row.update(compare(value["value_verbatim"], safe_eval(expr, names),
                                   unit=value.get("unit")))
        except (KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
            row.update(status="UNRESOLVED", reason=str(exc))
        rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    paths = args.paths or sorted(DEFAULT_DIR.glob("*.json"))
    rows: list[dict] = []
    for path in paths:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        batch = Path(path).stem
        for i, claim in enumerate(data["claims"]):
            for row in process_claim(batch, i, claim):
                row["source_file"] = data["source_document"]["file"]
                row["source_lines"] = claim["source"]["lines"]
                rows.append(row)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    report = {"_meta": {"generator": "scripts/recompute_c4_claims.py",
                        "inputs": [str(p) for p in paths], "counts": counts},
              "rows": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out}: "
          + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
