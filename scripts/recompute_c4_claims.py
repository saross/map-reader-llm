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
from lib_c4_compare import match_at_quoted_precision, parse_value, resolve_path  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = REPO_ROOT / "reports" / "verification" / "c4-extraction"
DEFAULT_OUT = REPO_ROOT / "reports" / "verification" / "c4-recompute-report.json"

MECHANICAL = {"read", "arithmetic"}
_ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name,
                  ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd,
                  ast.Pow)

_json_cache: dict[str, object] = {}


def load_json(relpath: str):
    """Load (and cache) a committed JSON artefact by repo-relative path."""
    if relpath not in _json_cache:
        _json_cache[relpath] = json.loads(
            (REPO_ROOT / relpath).read_text(encoding="utf-8")
        )
    return _json_cache[relpath]


def resolve_anchor_value(file: str, path: str):
    """Resolve a value from an anchor file, honouring the ``len:`` prefix.

    Raises:
        KeyError: On any resolution failure (message says why).
    """
    take_len = path.startswith("len:")
    if take_len:
        path = path[4:]
    obj = load_json(file)
    value = resolve_path(obj, path)
    if take_len:
        try:
            return len(value)
        except TypeError as exc:
            raise KeyError(f"len: target not sized ({exc})") from exc
    return value


def safe_eval(expression: str, names: dict[str, float]) -> float:
    """Evaluate an arithmetic expression over named operands.

    Only literals, single-letter names, + - * / ** and unary signs are
    permitted (schema-constrained upstream).

    Raises:
        ValueError: On disallowed syntax or unknown names.
    """
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"disallowed syntax {type(node).__name__} in {expression!r}")
        if isinstance(node, ast.Name) and node.id not in names:
            raise ValueError(f"unknown operand {node.id!r} in {expression!r}")
    return float(eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, names))


def compare(quoted_verbatim: str, actual) -> dict:
    """Compare a source value against a verbatim quote at quoted precision."""
    quoted = parse_value(quoted_verbatim)
    if quoted is None:
        return {"status": "UNRESOLVED", "reason": f"unparseable quote {quoted_verbatim!r}"}
    try:
        actual_f = float(actual)
    except (TypeError, ValueError):
        return {"status": "UNRESOLVED", "reason": f"non-numeric source value {actual!r}"}
    result = match_at_quoted_precision(quoted, actual_f)
    # Percentage scale bridge: quoted "92.0 %" vs source fraction 0.9203.
    if not result["match"] and quoted.is_percentage and abs(actual_f) <= 1.0 < abs(quoted.value):
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
                    row.update(compare(value["value_verbatim"], actual))
            else:  # arithmetic
                operands = (anchor.get("operands") if anchor else None) or []
                expr = (anchor.get("expression") if anchor else None) or ""
                names = {op["name"]: float(resolve_anchor_value(op["file"], op["path"]))
                         for op in operands}
                row.update(compare(value["value_verbatim"], safe_eval(expr, names)))
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
