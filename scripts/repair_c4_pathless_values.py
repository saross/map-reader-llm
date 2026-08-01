#!/usr/bin/env python3
"""Repair pathless ``read`` values in C4 extraction files (ruling 8).

Session-124 file-level repair pass (`phase3-rulings-2026-07-31.md` § 8;
Obs 379): gives pathless ``read`` values an explicit, quantity-driven
locator so the recompute harness never needs the (now refused)
anchor-path fallback. Two row populations are targeted:

- **File-only rows**: value pathless, claim anchor has a file but no
  path — currently honest ``UNRESOLVED`` at recompute.
- **Fallback rows**: value pathless, claim anchor carries a path — the
  Obs 379 trap configuration, silently compared against whatever the
  anchor locates until the Session-124 harness fix refused it.

Repairs are driven by a **shared quantity→anchor mapping** — each rule
keys on the value's ``quantity`` semantics (never on whether a
candidate path happens to reproduce the quoted number, which would
launder coincidences into MATCHes). Every applied locator is verified
to *resolve* at apply time; the resolved value is logged but never
gates the repair — a genuine document error must still surface as a
MISMATCH downstream.

Rows no rule covers are emitted as the LLM-tail worklist (ruling 8's
"LLM tail for the remainder"). Non-JSON-anchored pathless rows without
a rule are out of scope: the instrument treats non-JSON anchors as
legitimate triage scope (registered values anchor to the lodged prose
document, path null).

Outputs (with ``--apply``): edited extraction files in place, plus an
audit log at
``reports/verification/c4-triage/pathless-repair-<date>.json`` carrying
one row per repair (rule, old/new path, resolved value, prior recompute
status) and the unmapped tail worklist. Dry-run (default) writes the
log with ``applied: false`` and touches nothing.

Usage::

    python3 scripts/repair_c4_pathless_values.py            # dry-run
    python3 scripts/repair_c4_pathless_values.py --apply    # write
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recompute_c4_claims import resolve_anchor_value  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTRACTION_DIR = REPO_ROOT / "reports" / "verification" / "c4-extraction"
REPORT_PATH = REPO_ROOT / "reports" / "verification" / "c4-recompute-report.json"
LOG_PATH = (REPO_ROOT / "reports" / "verification" / "c4-triage"
            / f"pathless-repair-{date.today().isoformat()}.json")

# Canonical corpus artefacts for recurring quantities. Each maps a
# quantity PREFIX to (file, path). Cross-file locators are emitted when
# the claim's anchor file differs from the canonical file.
CANONICAL_QUANTITIES: list[tuple[str, str, str]] = [
    ("tile count, Phase 1 holdout",
     "inputs/tiles/validation_manifest.json", "len:$"),
    ("tile count, Era 1 evaluation corpus",
     "inputs/vectors/bounds/full_evaluation_bounds.geojson", "len:$.features"),
    ("tile count, Era 2 evaluation corpus",
     "inputs/tiles_384/full_evaluation_manifest.json", "len:$"),
]

# Feature-count quantities readable from the claim's own GeoJSON anchor.
SELF_FEATURE_COUNT_PREFIXES = (
    "candidates at the ",
    "candidate count, ",
    "count of curator-verified ground-truth mound symbols",
    "count of reviewed student-digitised mounds",
)

# Tile-count-bearing list manifests (counted whole: ``len:$``).
TILE_LIST_MANIFESTS = {
    "inputs/tiles/validation_manifest.json",
    "inputs/tiles_384/full_evaluation_manifest.json",
}


def canonicalise_len(path: str) -> str:
    """Rewrite ``len(...)``/``count(...)`` wrappers onto the ``len:``
    prefix (instrument v1.2 amendment 4's canonical spelling)."""
    stripped = path.strip()
    for wrapper in ("len(", "count("):
        if stripped.startswith(wrapper) and stripped.endswith(")"):
            return "len:" + stripped[len(wrapper):-1].strip()
    return stripped


def rule_expected_verifier_input(value: dict, claim: dict) -> str | None:
    """Batch-044 family: 'expected verifier input count (n_consensus)…'.

    The claim's own arithmetic anchor (gap = a − b) already names the
    correct source for the expected-input count: operand ``a``, the
    cell's candidate manifest. The anchor *path* (``len($.results)``,
    operand ``b``) is the RECORDED-output count — a different quantity,
    which is exactly what the silent fallback used to compare.
    """
    if not value["quantity"].startswith(
            "expected verifier input count (n_consensus) for cell "):
        return None
    anchor = claim.get("anchor") or {}
    operands = {op["name"]: op for op in anchor.get("operands") or []}
    if anchor.get("expression", "").replace(" ", "") != "a-b" or "a" not in operands:
        return None
    op_a = operands["a"]
    return f"{op_a['file']}#{canonicalise_len(op_a['path'])}"


def rule_canonical_quantity(value: dict, claim: dict) -> str | None:
    """Recurring corpus-level counts with one canonical source each."""
    for prefix, file, path in CANONICAL_QUANTITIES:
        if value["quantity"].startswith(prefix):
            anchor = claim.get("anchor") or {}
            if anchor.get("file") == file and not anchor.get("path"):
                return path
            return f"{file}#{path}"
    return None


def rule_self_feature_count(value: dict, claim: dict) -> str | None:
    """Candidate/mound counts anchored to their own GeoJSON."""
    anchor = claim.get("anchor") or {}
    file = anchor.get("file") or ""
    if not file.endswith(".geojson"):
        return None
    if value["quantity"].startswith(SELF_FEATURE_COUNT_PREFIXES):
        return "len:$.features"
    return None


def rule_tile_count_local(value: dict, claim: dict) -> str | None:
    """Phase-labelled tile counts whose anchor is already a counting
    artefact (a tile-list manifest or a bounds GeoJSON) — the extractor
    chose the right file and omitted only the count spelling."""
    if "tile count" not in value["quantity"]:
        return None
    anchor = claim.get("anchor") or {}
    file = anchor.get("file") or ""
    if file in TILE_LIST_MANIFESTS:
        return "len:$"
    if file.endswith("bounds.geojson"):
        return "len:$.features"
    return None


RULES = [
    ("expected-verifier-input-operand-a", rule_expected_verifier_input),
    ("canonical-quantity", rule_canonical_quantity),
    ("self-geojson-feature-count", rule_self_feature_count),
    ("tile-count-local-artefact", rule_tile_count_local),
]


def prior_statuses() -> dict[tuple[str, int, int], str]:
    """Index the committed recompute report by (batch, claim, value)."""
    if not REPORT_PATH.exists():
        return {}
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    return {(r["batch"], r["claim_index"], r["value_index"]): r["status"]
            for r in report["rows"]}


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true",
                        help="write repairs into the extraction files")
    args = parser.parse_args(argv)

    prior = prior_statuses()
    repairs: list[dict] = []
    tail: list[dict] = []
    edited: dict[Path, dict] = {}

    for path in sorted(EXTRACTION_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        batch = path.stem
        touched = False
        for ci, claim in enumerate(data["claims"]):
            anchor = claim.get("anchor") or {}
            for vi, value in enumerate(claim["values"]):
                method = value.get("method") or claim["method"]
                if method != "read" or value.get("path"):
                    continue
                row = {
                    "batch": batch, "claim_index": ci, "value_index": vi,
                    "quantity": value["quantity"],
                    "value_verbatim": value["value_verbatim"],
                    "anchor_file": anchor.get("file"),
                    "anchor_path": anchor.get("path"),
                    "n_values": len(claim["values"]),
                    "prior_status": prior.get((batch, ci, vi)),
                }
                for rule_name, rule in RULES:
                    new_path = rule(value, claim)
                    if new_path is None:
                        continue
                    # The locator must resolve — a rule pointing at a
                    # path that fails to resolve is a rule defect, not
                    # a repair. The resolved value is provenance only.
                    try:
                        resolved = resolve_anchor_value(
                            anchor.get("file") or "", new_path)
                    except KeyError as exc:
                        row.update(rule=rule_name, candidate_path=new_path,
                                   resolution_error=str(exc))
                        tail.append(row)
                        break
                    row.update(rule=rule_name, new_path=new_path,
                               resolved=resolved)
                    repairs.append(row)
                    if args.apply:
                        value["path"] = new_path
                        touched = True
                    break
                else:
                    # No rule fired. JSON-anchored rows (and non-JSON
                    # rows in the amendment-3 trap form) go to the LLM
                    # tail; other non-JSON rows are legitimate triage
                    # scope and stay as they are.
                    jsonish = (anchor.get("file") or "").endswith(
                        (".json", ".geojson"))
                    trap_form = bool(anchor.get("path")) and len(claim["values"]) > 1
                    if jsonish or trap_form:
                        tail.append(row)
        if touched:
            edited[path] = data

    if args.apply:
        for path, data in edited.items():
            path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n",
                            encoding="utf-8")

    log = {
        "_meta": {
            "generator": "scripts/repair_c4_pathless_values.py",
            "date": date.today().isoformat(),
            "ruling": "phase3-rulings-2026-07-31.md § 8 (Session 124)",
            "applied": bool(args.apply),
            "counts": {
                "repaired": len(repairs),
                "tail": len(tail),
                "files_edited": len(edited),
            },
            "rules": [name for name, _ in RULES],
        },
        "repairs": repairs,
        "tail_worklist": tail,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(log, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    mode = "APPLIED" if args.apply else "dry-run"
    print(f"{mode}: {len(repairs)} repaired ({len(edited)} files), "
          f"{len(tail)} to the LLM tail; log: {LOG_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
