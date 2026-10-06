#!/usr/bin/env python3
"""Price the archive's billed executions into a ledger for the project total.

Purpose
-------
The passes register (``results/passes-manifest.json``) prices every pass of
every registered run, and two hand ledgers carry spend the register cannot:
``data/pricing/superseded-executions.json`` (D22) and
``data/pricing/unmetered-executions.json`` (D35). Neither ever reached
``archive/``: 734 git-tracked metas there record token usage, outside the
register and outside the WP4 ``cost_audit.json`` sidecars, whose scan covered
``outputs/`` and ``results/`` only (PI ruling D38, 2026-10-05).

This script reads the hand-reviewed classification of those metas
(``data/pricing/archive-classification.json``) and writes
``data/pricing/archive-executions.json``:

- **SUPERSEDED**, **UNREGISTERED** (a cited execution no registered run
  carries, by ruling: D40's Experiment E) and **UNSURE** (pending a ruling):
  priced the way the WP4
  sidecars price a meta outside the register
  (:func:`scripts.backfill_cost_audit_sidecars.outside_entry`, which calls
  ``PassCoster.cost_fragment``: the meta's own usage at the tier the committed
  evidence resolves). A meta marked ``partial`` (its last resume overwrote part
  of its pass) is a floor, ``audited-lower-bound``.
- **DUPLICATE** and **SNAPSHOT**: no separate spend; the twin is checked to
  exist and to be tracked.
- **REAL**: carried by a register row, which is checked to cite the meta; its
  cost is the register's and is not added here.

It also counts, by subtree, the tracked archive metas that record NO usage
(Batch API metas, mostly): D39 leaves their spend to WP6's invoice residual,
with no per-item figure.

Usage
-----
::

    python scripts/build_archive_ledger.py            # dry run: report only
    python scripts/build_archive_ledger.py --write    # write the ledger
    python scripts/build_archive_ledger.py --check    # exit 1 if it would change

A classification that misses a usage-bearing archive meta, or names a meta
that is not one, stops the build: a new archive meta is classified by hand
first. Zero API; a few seconds of compute (run it on sapphire with the rest of
the register pipeline).

Created: 2026-10-05 (Session 160, the register repair, rulings D38-D39)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.backfill_cost_audit_sidecars import (  # noqa: E402
    outside_entry,
    read_json,
    register_stamp,
)
from scripts.lib_pass_cost import PassCoster  # noqa: E402

CLASSIFICATION = PROJECT_ROOT / "data" / "pricing" / "archive-classification.json"
LEDGER = PROJECT_ROOT / "data" / "pricing" / "archive-executions.json"
REGISTER = PROJECT_ROOT / "results" / "passes-manifest.json"
RUN_REGISTRY = PROJECT_ROOT / "results" / "run-registry.json"

#: This writer's identity, stamped into the ledger.
GENERATOR = "scripts/build_archive_ledger.py"
GENERATOR_VERSION = "1.0.0"

#: The classes the classification may use (its _README defines them).
PRICED = ("SUPERSEDED", "UNREGISTERED", "UNSURE")
TWINNED = ("DUPLICATE", "SNAPSHOT")
CLASSES = PRICED + TWINNED + ("REAL",)


class LedgerError(ValueError):
    """The classification and the archive disagree; nothing is written."""


def tracked_archive_metas(repo_root: Path) -> list[str]:
    """Every git-tracked ``*.meta.json`` under ``archive/``, repository-relative, sorted.

    Raises:
        LedgerError: Outside a git checkout: the scope is the committed metas
            only, so it cannot be built from whatever is on disk.
    """
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--", "archive/"], cwd=repo_root,
                             check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LedgerError(f"git unavailable in {repo_root}: the ledger reads committed "
                          "metas only") from exc
    return sorted(n for n in out.decode("utf-8").split("\0") if n.endswith(".meta.json"))


def records_usage(meta: dict[str, Any]) -> bool:
    """D38's filter: usage-bearing when input tokens or a runner cost estimate are recorded.

    Examples:
        >>> records_usage({"usage_stats": {"total_input_tokens": 12}})
        True
        >>> records_usage({"usage_stats": {"total_input_tokens": 0},
        ...                "cost_estimate": {"total_cost_usd": 0.0}})
        False
    """
    usage = meta.get("usage_stats") or {}
    return bool(usage.get("total_input_tokens")
                or (meta.get("cost_estimate") or {}).get("total_cost_usd"))


def subtree(meta_rel: str) -> str:
    """The archive subtree a meta sits in (its first two path components)."""
    return "/".join(meta_rel.split("/")[:2])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def price_entry(entry: dict[str, Any], meta: dict[str, Any], repo_root: Path,
                runs: list[dict[str, Any]], coster: PassCoster) -> dict[str, Any]:
    """Price one SUPERSEDED or UNSURE meta; a ``partial`` one becomes a floor.

    Args:
        entry: Its classification entry.
        meta: The parsed meta.
        repo_root: The repository root.
        runs: The run registry's entries (for the tier walk's context).
        coster: The register's coster.

    Returns:
        ``cost_usd``, ``cost_basis``, the priced fragment and its context.
    """
    rel = entry["meta"]
    priced = outside_entry(meta, repo_root / rel, rel, runs, coster, repo_root)
    out = {k: priced[k] for k in ("cost_usd", "cost_basis", "fragment") if k in priced}
    out["resolution_context"] = priced.get("resolution_context")
    if entry.get("partial") and out["cost_basis"] in ("audited", "audited-upper-bound"):
        # The meta holds only part of its pass (a later resume overwrote the
        # rest): a floor at its lowest candidate tier, as the register floors
        # a cleanup-overwritten leg. The rest is D39's invoice residual.
        low = (out["fragment"].get("bounds_usd") or {}).get("low", out["cost_usd"])
        out["cost_basis"], out["cost_usd"] = "audited-lower-bound", low
    return out


def build(repo_root: Path = PROJECT_ROOT, classification_path: Path | None = None,
          register_path: Path | None = None, run_registry_path: Path | None = None,
          coster: PassCoster | None = None) -> dict[str, Any]:
    """The ledger document, from the classification and the committed archive.

    Raises:
        LedgerError: A usage-bearing meta is unclassified, a classified meta is
            not one, a class is unknown, a twin is missing or untracked, or a
            REAL meta's register row does not cite it.
    """
    classification_path = classification_path or repo_root / CLASSIFICATION.relative_to(
        PROJECT_ROOT)
    register_path = register_path or repo_root / REGISTER.relative_to(PROJECT_ROOT)
    run_registry_path = run_registry_path or repo_root / RUN_REGISTRY.relative_to(PROJECT_ROOT)
    classification = read_json(classification_path)
    register = read_json(register_path)
    runs = read_json(run_registry_path).get("registry") or [] \
        if run_registry_path.exists() else []
    coster = coster or PassCoster()
    tracked = tracked_archive_metas(repo_root)
    tracked_set = set(tracked)
    metas = {rel: read_json(repo_root / rel) for rel in tracked}
    bearing = {rel for rel, m in metas.items() if records_usage(m)}
    entries = classification["entries"]
    named = [e["meta"] for e in entries]
    if len(named) != len(set(named)):
        raise LedgerError("the classification names a meta twice")
    missing = sorted(bearing - set(named))
    extra = sorted(set(named) - bearing)
    if missing or extra:
        raise LedgerError(f"classification out of step with the archive: {len(missing)} "
                          f"usage-bearing meta(s) unclassified {missing[:3]}, {len(extra)} "
                          f"classified meta(s) not usage-bearing {extra[:3]}")
    cited = {src: row for row in register["passes"]
             for src in (row.get("provenance") or {}).get("source_files") or []}
    rows = {row["pass_id"]: row for row in register["passes"]}
    out_entries = []
    for entry in entries:
        rel, cls = entry["meta"], entry["class"]
        if cls not in CLASSES:
            raise LedgerError(f"{rel}: unknown class {cls!r}")
        record = {k: v for k, v in entry.items()}
        if cls in TWINNED:
            twin = entry.get("twin")
            if not twin or twin not in tracked_set and not _git_tracked(repo_root, twin):
                raise LedgerError(f"{rel}: its twin {twin!r} is not a tracked file")
            record.update(cost_usd=None, cost_basis="not-separate-spend",
                          twin_in_register=twin in cited)
        elif cls == "REAL":
            row = rows.get(entry.get("register_pass_id") or "")
            if row is None or rel not in (row.get("provenance") or {}).get("source_files", []):
                raise LedgerError(f"{rel}: REAL, but register row "
                                  f"{entry.get('register_pass_id')!r} does not cite it")
            record.update(cost_usd=None, cost_basis="in-register",
                          register_cost_usd=row.get("cost_usd"),
                          register_cost_basis=row.get("cost_basis"))
        else:
            record.update(price_entry(entry, metas[rel], repo_root, runs, coster))
        out_entries.append(record)
    return assemble(out_entries, metas, bearing, classification_path, register,
                    register_path.relative_to(repo_root).as_posix(), coster, repo_root)


def _git_tracked(repo_root: Path, rel: str) -> bool:
    """Whether a repository-relative path is tracked by git."""
    return subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=repo_root,
                          capture_output=True).returncode == 0


def assemble(entries: list[dict[str, Any]], metas: dict[str, dict], bearing: set[str],
             classification_path: Path, register: dict[str, Any], register_rel: str,
             coster: PassCoster, repo_root: Path) -> dict[str, Any]:
    """The ledger: totals by class and basis, the entries, and the unmetered counts."""
    totals: dict[str, Any] = {}
    for cls in CLASSES:
        members = [e for e in entries if e["class"] == cls]
        block: dict[str, Any] = {"metas": len(members)}
        if cls in PRICED:
            by_basis: dict[str, float] = defaultdict(float)
            for e in members:
                if e.get("cost_usd") is not None:
                    by_basis[e["cost_basis"]] += e["cost_usd"]
            block["priced_usd"] = round(sum(by_basis.values()), 6)
            block["by_basis_usd"] = {k: round(v, 6) for k, v in sorted(by_basis.items())}
            block["unpriced"] = sum(1 for e in members if e.get("cost_usd") is None)
            block["partial"] = sum(1 for e in members if e.get("partial"))
        totals[cls] = block
    zero = Counter(subtree(rel) for rel in metas if rel not in bearing)
    return {
        "_README": (
            "The archive's billed executions, priced for WP6's project total (PI rulings D38 "
            "and D39, 2026-10-05). GENERATED by scripts/build_archive_ledger.py from "
            "data/pricing/archive-classification.json (hand-reviewed); never edit by hand. "
            "SUPERSEDED, UNREGISTERED (cited but unregistered, by ruling: D40) and UNSURE "
            "(pending a ruling) metas are priced like a WP4 sidecar's "
            "meta outside the register (PassCoster.cost_fragment at the tier the committed "
            "evidence resolves; several candidate tiers publish the highest, with bounds); a "
            "partial meta is a floor. DUPLICATE and SNAPSHOT metas are not separate spend; "
            "REAL metas are register rows, priced there. totals.SUPERSEDED.priced_usd and "
            "totals.UNREGISTERED.priced_usd are what the project total adds; "
            "zero_usage_metas_by_subtree lists the metas that record "
            "no usage, whose spend is WP6's invoice residual (D39)."),
        "schema": "archive-executions/1",
        "generator": GENERATOR,
        "generator_version": GENERATOR_VERSION,
        "classification": {"path": classification_path.relative_to(repo_root).as_posix(),
                           "sha256": _sha256(classification_path)},
        "register": register_stamp(register, register_rel),
        "rate_card": coster.card_identity,
        "totals": totals,
        "zero_usage_metas_by_subtree": dict(sorted(zero.items())),
        "zero_usage_metas": sum(zero.values()),
        "entries": entries,
    }


def render(doc: dict[str, Any]) -> str:
    """The ledger's committed text (stable key order, one trailing newline)."""
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n"


def report(doc: dict[str, Any]) -> list[str]:
    """Human-readable totals for the dry run."""
    lines = []
    for cls, block in doc["totals"].items():
        line = f"{cls:10s} {block['metas']:4d} metas"
        if "priced_usd" in block:
            line += (f", US${block['priced_usd']:,.6f} ({block['by_basis_usd']}); "
                     f"unpriced {block['unpriced']}, partial {block['partial']}")
        lines.append(line)
    lines.append(f"zero-usage archive metas (D39 residual): {doc['zero_usage_metas']}")
    return lines


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the ledger")
    mode.add_argument("--check", action="store_true",
                      help="exit 1 if the committed ledger would change")
    args = parser.parse_args(argv)
    try:
        doc = build()
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    text = render(doc)
    current = LEDGER.read_text(encoding="utf-8") if LEDGER.exists() else None
    for line in report(doc):
        print(line)
    if args.check:
        if current == text:
            print(f"{LEDGER.relative_to(PROJECT_ROOT)}: up to date")
            return 0
        print(f"{LEDGER.relative_to(PROJECT_ROOT)}: WOULD CHANGE", file=sys.stderr)
        return 1
    if args.write:
        LEDGER.write_text(text, encoding="utf-8")
        print(f"wrote {LEDGER.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
