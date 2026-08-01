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
  Includes the instrument v1.2 amendment 3 refusal: a pathless value in
  a multi-value claim never inherits the claim anchor's path (Obs 379 —
  the silent fallback compared pass counts against temperatures); the
  fallback survives only for single-value claims, where the anchor path
  is by definition the claim's locator. Non-JSON anchors get a distinct
  ``triage scope`` reason whether or not a path is present.
- ``SKIPPED`` — method out of mechanical scope (regen-diff,
  historical, unverifiable-era, external, anchor-unknown; and
  ``recompute-script`` values with no registered runner — those
  reasons name the gap so unspecced families surface as NAMED lines
  in gate packages, per ruling 7). A ``recompute-script`` value WITH
  a registered runner spec (``lib_c4_runners``,
  ``apparatus/recompute-script-registry.json``) is executed and
  compared exactly like a read.

Path extension over the lib resolver: a ``len:`` prefix counts the
resolved collection (GeoJSON feature counts etc.).

Git-era resolution (ruling 9): a ``read`` anchor missing from the
working tree is retried against the repository tree at the source
document's era commit (the newest commit still holding the
extraction's recorded ``git_blob``), with unique-suffix
disambiguation for era-relative locators. Era-resolved rows are
marked ``resolution: "git-era"`` — they attest the document against
its era, not the current artefact.

Era check for moved anchors (ruling 12): on dated-snapshot documents
(dated filename/title — detected from the filename stem for now,
provisional per the ruling), a MISMATCH on a mechanical
(``read``/``arithmetic``) row gains a supplementary ``era_check``
field: the locator (or every operand) is re-resolved at the era
commit and compared again, recording whether the document was
faithful to its era. Never a status change — the primary verdict
stays the current-artefact comparison; triage uses the field to
separate SNAPSHOT-DIVERGENCE from SNAPSHOT-DEFECT mechanically.

Usage::

    python3 scripts/recompute_c4_claims.py [paths...] [--out reports/verification/c4-recompute-report.json]
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_c4_compare import (  # noqa: E402
    match_at_quoted_precision,
    normalise_path,
    parse_value,
    resolve_path,
)
from lib_c4_runners import execute_spec, load_registry  # noqa: E402

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
    file, path = split_locator(file, path)
    return resolve_in_obj(load_json(file), path)


def split_locator(file: str, path: str) -> tuple[str, str]:
    """Split a ``<file>#<jsonpath>`` cross-file locator; pass through
    plain paths unchanged."""
    path = path.strip()
    if "#" in path and not path.startswith(("$", "len:")):
        override, _, subpath = path.partition("#")
        if not subpath:
            raise KeyError(f"file#path locator missing path part: {path!r}")
        return override.strip(), subpath.strip()
    return file, path


def resolve_in_obj(obj, path: str):
    """Resolve a locator path against already-loaded JSON (shared by
    working-tree and git-era resolution)."""
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


def _git(*args: str) -> str:
    """Run a git command in the repo root and return stdout.

    Raises:
        KeyError: On git failure — the era-resolution layer treats any
            git error as an unresolvable anchor, never a crash.
    """
    result = subprocess.run(["git", *args], cwd=REPO_ROOT,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise KeyError(f"git {' '.join(args[:2])} failed: "
                       f"{result.stderr.strip()[:120]}")
    return result.stdout


_era_commit_cache: dict[tuple[str, str], str | None] = {}
_era_tree_cache: dict[str, list[str]] = {}
_tracked_files_cache: list[str] | None = None


def _tracked_files() -> list[str]:
    """Tracked working-tree paths (cached), for suffix disambiguation."""
    global _tracked_files_cache
    if _tracked_files_cache is None:
        _tracked_files_cache = _git("ls-files").splitlines()
    return _tracked_files_cache


def find_era_commit(doc_path: str, doc_blob: str) -> str | None:
    """Newest commit whose tree holds the extraction's recorded blob of
    the source document — the document's era (ruling 9 / ruling 1)."""
    key = (doc_path, doc_blob)
    if key not in _era_commit_cache:
        _era_commit_cache[key] = None
        try:
            for commit in _git("log", "--format=%H", "--", doc_path).split():
                try:
                    blob = _git("rev-parse", f"{commit}:{doc_path}").strip()
                except KeyError:
                    continue
                if blob.startswith(doc_blob):
                    _era_commit_cache[key] = commit
                    break
        except KeyError:
            pass
    return _era_commit_cache[key]


def era_resolve(era_commit: str, file: str, path: str):
    """Resolve a locator against the repository tree at the document's
    era commit (ruling 9: anchors deleted after extraction).

    A file absent from the era tree at its exact path is retried as a
    unique SUFFIX match — session-era documents quote cell-relative
    locators (``<cell>/threshold_sweep.json``) whose parent directory
    the era tree disambiguates. Ambiguity fails loudly.

    Returns:
        ``(value, resolved_file)`` — the resolved value and the
        era-tree path it came from.

    Raises:
        KeyError: On any failure (message says why).
    """
    file, path = split_locator(file, path)
    if not file.endswith((".json", ".geojson")):
        raise KeyError(f"non-JSON anchor {file} (triage scope)")
    if era_commit not in _era_tree_cache:
        _era_tree_cache[era_commit] = _git(
            "ls-tree", "-r", "--name-only", era_commit).splitlines()
    tree = _era_tree_cache[era_commit]
    resolved_file = file
    if file not in tree:
        hits = [t for t in tree if t.endswith("/" + file)]
        if len(hits) != 1:
            raise KeyError(
                f"era-resolution: {len(hits)} candidates for {file!r} "
                f"at {era_commit[:9]}")
        resolved_file = hits[0]
    obj = json.loads(_git("show", f"{era_commit}:{resolved_file}"))
    return resolve_in_obj(obj, path), resolved_file


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


# Dated filename stems mark snapshot documents (ruling 12's provisional
# classification rule: dated filename or dated title controls, not the
# directory; title detection awaits experience in use).
SNAPSHOT_STEM_RE = re.compile(r"\d{4}-\d{2}-\d{2}|session-\d+", re.IGNORECASE)


def is_snapshot_doc(doc_path: str) -> bool:
    """Ruling-12 snapshot classification from the filename stem."""
    return bool(SNAPSHOT_STEM_RE.search(Path(doc_path).stem))


def _era_check(row: dict, claim: dict, value: dict, era: dict) -> None:
    """Attach the ruling-12 ``era_check`` field to a MISMATCH row.

    Re-resolves the row's locator (read) or every operand (arithmetic)
    at the source document's era commit and records whether the quote
    was faithful to its era. Failures land as ``era_check.error`` —
    never an exception, never a status change.
    """
    commit = find_era_commit(era["doc"], era["blob"])
    if commit is None:
        row["era_check"] = {"error": "no era commit found for source blob"}
        return
    try:
        anchor = claim.get("anchor") or {}
        if row["method"] == "read":
            path = value.get("path") or anchor.get("path")
            actual, _ = era_resolve(commit, anchor.get("file") or "", path)
        else:  # arithmetic
            source = value if value.get("expression") else anchor
            names = {op["name"]: float(era_resolve(commit, op["file"],
                                                   op["path"])[0])
                     for op in source.get("operands") or []}
            actual = safe_eval(source.get("expression") or "", names)
        verdict = compare(value["value_verbatim"], actual,
                          unit=value.get("unit"))
        row["era_check"] = {"faithful": verdict["status"] == "MATCH",
                            "status": verdict["status"],
                            "actual_era": verdict.get("actual", actual),
                            "commit": commit[:12]}
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
        row["era_check"] = {"error": str(exc)}


def process_claim(batch: str, index: int, claim: dict,
                  registry: dict | None = None,
                  era: dict | None = None) -> list[dict]:
    """Produce one report row per value in a claim.

    Args:
        batch: Extraction-file stem (report row key).
        index: Claim index within the file.
        claim: The claim object.
        registry: Runner-spec index from
            :func:`lib_c4_runners.load_registry` (``None`` → no specs,
            every ``recompute-script`` value stays SKIPPED).
        era: Source-document era context ``{"doc": path, "blob": hash}``
            for ruling-9 git-era resolution of ``read`` anchors missing
            from the working tree (``None`` → missing anchors stay
            UNRESOLVED). Era-resolved rows carry ``resolution:
            "git-era"`` plus the commit and era-tree path — a MATCH
            there attests the document against its ERA, not against
            the current artefact.
    """
    rows: list[dict] = []
    anchor = claim["anchor"]
    for vi, value in enumerate(claim["values"]):
        method = value.get("method") or claim["method"]
        row = {
            "batch": batch, "claim_index": index, "value_index": vi,
            "method": method, "quantity": value["quantity"],
            "value_verbatim": value["value_verbatim"],
        }
        if method == "recompute-script":
            spec = (registry or {}).get((batch, index, vi))
            if spec is None:
                row.update(status="SKIPPED",
                           reason="recompute-script without registered runner")
            else:
                try:
                    result = execute_spec(spec)
                    row.update(compare(value["value_verbatim"], result,
                                       unit=value.get("unit")))
                    row["runner"] = spec["runner"]
                except (KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
                    row.update(status="UNRESOLVED",
                               reason=f"runner {spec.get('runner')} failed: {exc}")
            rows.append(row)
            continue
        if method not in MECHANICAL:
            row.update(status="SKIPPED", reason=f"method {method} is triage/deferred scope")
            rows.append(row)
            continue
        try:
            if method == "read":
                own_path = value.get("path")
                anchor_path = anchor.get("path") if anchor else None
                anchor_file = anchor.get("file") if anchor else None
                effective = own_path or anchor_path
                # A cross-file locator names its own source, so a
                # non-JSON claim anchor does not block resolution.
                crosses = bool(effective) and "#" in effective \
                    and not effective.startswith(("$", "len:"))
                if anchor_file and not crosses \
                        and not anchor_file.endswith((".json", ".geojson")):
                    row.update(status="UNRESOLVED",
                               reason=f"non-JSON anchor {anchor_file} (triage scope)")
                elif not own_path and anchor_path and len(claim["values"]) > 1:
                    # Obs 379: the silent anchor-path fallback compared
                    # pass counts against temperatures. Instrument v1.2
                    # amendment 3 forbids this configuration — refuse it
                    # loudly rather than compare the wrong quantity.
                    row.update(status="UNRESOLVED",
                               reason="pathless value in multi-value claim "
                                      "(v1.2 amendment 3) — anchor-path "
                                      "fallback refused")
                elif not anchor or not effective:
                    row.update(status="UNRESOLVED", reason="read claim without anchor path")
                else:
                    try:
                        actual = resolve_anchor_value(anchor_file, effective)
                    except FileNotFoundError as missing:
                        # Ruling 9: anchor deleted (or era-relative)
                        # after extraction — resolve at the source
                        # document's era commit.
                        commit = (find_era_commit(era["doc"], era["blob"])
                                  if era else None)
                        if commit is None:
                            raise KeyError(
                                f"anchor missing from working tree "
                                f"({missing}); no era context") from missing
                        try:
                            actual, era_file = era_resolve(
                                commit, anchor_file, effective)
                            row.update(resolution="git-era",
                                       era_commit=commit[:12],
                                       era_file=era_file)
                        except KeyError as era_fail:
                            # Artefact absent at era too (e.g. a
                            # later-materialised regen copy): bind an
                            # era-relative locator to a UNIQUE tracked
                            # working-tree suffix match; ambiguity
                            # stays a loud failure.
                            file, sub = split_locator(anchor_file,
                                                      effective)
                            hits = [t for t in _tracked_files()
                                    if t.endswith("/" + file)]
                            if len(hits) != 1:
                                raise KeyError(
                                    f"{era_fail}; working-tree suffix: "
                                    f"{len(hits)} candidates") from era_fail
                            actual = resolve_in_obj(load_json(hits[0]), sub)
                            row.update(resolution="suffix-current",
                                       resolved_file=hits[0])
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
        if (row.get("status") == "MISMATCH" and era and era.get("snapshot")
                and method in MECHANICAL):
            _era_check(row, claim, value, era)
        rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    paths = args.paths or sorted(DEFAULT_DIR.glob("*.json"))
    registry = load_registry()
    rows: list[dict] = []
    for path in paths:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        batch = Path(path).stem
        era = {"doc": data["source_document"]["file"],
               "blob": data["source_document"]["git_blob"],
               "snapshot": is_snapshot_doc(data["source_document"]["file"])}
        for i, claim in enumerate(data["claims"]):
            for row in process_claim(batch, i, claim, registry, era):
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
