#!/usr/bin/env python3
"""Runner registry primitives for the C4 ``recompute-script`` class.

Ruling 7 (``reports/verification/phase3-rulings-2026-07-31.md`` § 7):
the recompute-script method class is executed comprehensively via a
runner registry rather than deferred. This module provides the
**census/count primitives** — the first registry tranche, covering the
counting quantities that JSONPath filters cannot express (regex-matched
inventory subsets, script-constant occurrences, directory censuses,
aggregate derivations). Cost/token and statistical runners follow as
separate tranches.

Specs live in
``reports/verification/apparatus/recompute-script-registry.json``::

    {"specs": [{"batch": "038-h11", "claim_index": 9, "value_index": 0,
                "runner": "json-subset-count",
                "params": {"file": "planning/condition-inventory.json",
                           "list_path": "$",
                           "where": [{"key": "path", "op": "regex",
                                      "value": "gold-standard-v2"}]},
                "note": "…"}]}

Each runner takes ``params`` and returns a number. The recompute
harness consults the registry for ``method: "recompute-script"``
values: with a spec, the value is compared like a read; without one,
it stays SKIPPED and the missing family is a NAMED line in the GATE 3
package (ruling 7: no silent deferrals).

All paths are repo-relative so specs execute identically on any
machine (local or sapphire).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = (REPO_ROOT / "reports" / "verification" / "apparatus"
                 / "recompute-script-registry.json")


def _resolve_list(file: str, list_path: str):
    """Load a JSON artefact and resolve ``list_path`` to a list."""
    from lib_c4_compare import resolve_path
    obj = json.loads((REPO_ROOT / file).read_text(encoding="utf-8"))
    value = obj if list_path in ("$", "") else resolve_path(obj, list_path)
    if not isinstance(value, list):
        raise ValueError(f"{list_path!r} in {file} is not a list")
    return value


def _match(element, where: list[dict]) -> bool:
    """Evaluate predicate conjunction over one list element."""
    for cond in where:
        raw = element.get(cond["key"]) if isinstance(element, dict) else None
        op = cond["op"]
        if op == "eq":
            ok = raw == cond["value"]
        elif op == "ne":
            ok = raw != cond["value"]
        elif op == "regex":
            ok = raw is not None and re.search(cond["value"], str(raw)) is not None
        elif op == "contains":
            ok = raw is not None and cond["value"] in str(raw)
        else:
            raise ValueError(f"unknown predicate op {op!r}")
        if not ok:
            return False
    return True


def run_glob_count(params: dict) -> int:
    """Count filesystem entries matching a glob under a root.

    Params: ``root`` (repo-relative dir), ``glob`` (pattern, may
    contain ``**``), optional ``kind`` (``file``/``dir``/``any``,
    default ``file``).
    """
    root = REPO_ROOT / params["root"]
    kind = params.get("kind", "file")
    hits = root.glob(params["glob"])
    if kind == "file":
        return sum(1 for h in hits if h.is_file())
    if kind == "dir":
        return sum(1 for h in hits if h.is_dir())
    return sum(1 for _ in hits)


def run_regex_count(params: dict) -> int:
    """Count regex hits in a text file.

    Params: ``file`` (repo-relative), ``pattern`` (Python regex),
    optional ``scope`` (``lines`` counts matching lines — the default —
    while ``occurrences`` counts every match).
    """
    text = (REPO_ROOT / params["file"]).read_text(encoding="utf-8",
                                                  errors="replace")
    pattern = re.compile(params["pattern"])
    if params.get("scope", "lines") == "occurrences":
        return sum(1 for _ in pattern.finditer(text))
    return sum(1 for line in text.splitlines() if pattern.search(line))


def run_json_subset_count(params: dict) -> int:
    """Count list elements satisfying predicates JSONPath filters
    cannot express (regex, multi-key conjunctions).

    Params: ``file``, ``list_path`` (``$`` for a root-level list),
    ``where`` (list of ``{key, op, value}``; op ∈ eq/ne/regex/contains).
    """
    elements = _resolve_list(params["file"], params["list_path"])
    return sum(1 for el in elements if _match(el, params["where"]))


def run_json_aggregate(params: dict) -> float:
    """Aggregate a key over (optionally filtered) list elements.

    Params: ``file``, ``list_path``, ``key``, ``agg`` (``min``/``max``/
    ``sum``/``count-distinct``), optional ``where`` as in subset-count.
    Covers derivations like a consensus pool's effective vote threshold
    (min over feature vote counts).
    """
    elements = _resolve_list(params["file"], params["list_path"])
    if params.get("where"):
        elements = [el for el in elements if _match(el, params["where"])]
    values = []
    for el in elements:
        raw = el
        for step in params["key"].split("."):
            raw = raw[step]
        values.append(raw)
    agg = params["agg"]
    if agg == "min":
        return min(values)
    if agg == "max":
        return max(values)
    if agg == "sum":
        return sum(values)
    if agg == "count-distinct":
        return len(set(values))
    raise ValueError(f"unknown agg {agg!r}")


RUNNERS = {
    "glob-count": run_glob_count,
    "regex-count": run_regex_count,
    "json-subset-count": run_json_subset_count,
    "json-aggregate": run_json_aggregate,
}


def load_registry() -> dict[tuple[str, int, int], dict]:
    """Index registered specs by (batch, claim_index, value_index).

    Returns an empty index when the registry file does not exist yet —
    the harness then leaves every recompute-script value SKIPPED, which
    is the pre-registry behaviour.
    """
    if not REGISTRY_PATH.exists():
        return {}
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {(s["batch"], s["claim_index"], s["value_index"]): s
            for s in registry.get("specs", [])}


def execute_spec(spec: dict) -> float:
    """Execute one registered spec and return its number.

    Raises:
        KeyError: Unknown runner name.
        ValueError: Malformed params (message says why).
    """
    runner = RUNNERS[spec["runner"]]
    return runner(spec["params"])
