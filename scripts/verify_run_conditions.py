#!/usr/bin/env python3
"""Deterministic verifier for the run-conditions decomposition (sub-step 3b, Tier 1).

Re-derives each decomposed run's cross-checkable invariants FROM SOURCE and reports
the discrepancies JSON-Schema validation cannot catch — content errors that are
schema-valid but wrong:

* **eval ↔ detections** — the evaluation a condition points at actually scored the
  condition's detection geojson (not a different file);
* **scope** — the evaluation's bounds match the run's nominal scope, or the
  condition's ``scope_override`` (the 327-vs-487 leakage trap);
* **feature count** — the detection geojson's feature count equals the eval's
  ``n_detections`` (a wrong-source signal that has caught real errors before —
  ``feedback_feature_count_crosscheck``);
* **pool resolves** — the condition's ``proposer_pool`` is one of the run's pools
  (or a flagged cross-run reference), and ``n_passes`` does not exceed the passes
  on disk;
* **completeness** — every scored evaluation under the run is either claimed by a
  condition or explicitly waived in ``_ignored_evals`` (catches silent omissions).

This is Tier 1 of the Batch verification loop (the deterministic backbone). A
fresh-context LLM adversarial pass (Tier 2) handles the judgment calls. The
verifier writes nothing — it re-computes from source and emits a verdict per run.

Usage:
    python scripts/verify_run_conditions.py            # all decomposed runs
    python scripts/verify_run_conditions.py --run h8-v2
    python scripts/verify_run_conditions.py --json     # machine-readable report
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# Reuse the generator's loaders + path helpers. The import path differs between
# `python scripts/verify_run_conditions.py` (scripts/ on sys.path) and a pytest
# import (repo root on sys.path via pythonpath=.), so try both.
try:  # pragma: no cover - exercised by the two run contexts, not a branch to test
    from scripts import generate_post_run_report as g
except ModuleNotFoundError:  # pragma: no cover
    import generate_post_run_report as g

ERROR = "ERROR"
WARN = "WARN"


def _disc(severity: str, code: str, message: str) -> dict[str, str]:
    """Build one discrepancy record."""
    return {"severity": severity, "code": code, "message": message}


def _eval_inputs(eval_doc: dict) -> tuple[list[str], str | None]:
    """Return ``(normalised detections list, bounds)`` from an eval's ``_metadata``."""
    meta = eval_doc.get("_metadata", {})
    inf = meta.get("input_files", {}) or {}
    dets = inf.get("detections") or []
    if isinstance(dets, str):
        dets = [dets]
    bounds = inf.get("bounds") or (meta.get("cli_args") or {}).get("bounds")
    return [g._normalise_detections_path(d) for d in dets], bounds


def _geojson_feature_count(rel_path: str) -> int | None:
    """Number of features in a geojson, or ``None`` if it cannot be read/parsed."""
    path = g.REPO_ROOT / rel_path
    if not path.exists():
        return None
    try:
        doc = g._load_json(path)
    except (json.JSONDecodeError, OSError):
        return None
    feats = doc.get("features")
    return len(feats) if isinstance(feats, list) else None


def _auto_match_eval(detections: str, scope_bounds: str | None,
                     index: dict) -> str | None:
    """Resolve the eval for a no-``eval_path`` condition, mirroring the extractor.

    Returns the repo-relative eval path the extractor would select (scope-preferring,
    then most-complete), or ``None`` if nothing matches.
    """
    cands = index.get(g._normalise_detections_path(detections), [])
    scope_match = [c for c in cands if c[2] == scope_bounds]
    chosen = scope_match or cands
    if not chosen:
        return None
    return max(chosen, key=lambda c: len(c[1].get("buffers", [])))[0]


def verify_condition(spec: dict, scope_bounds: str | None,
                     proposer_pools: dict, run_dir_rel: str, index: dict) -> list[dict]:
    """Re-derive and check one condition's invariants from source."""
    discs: list[dict] = []
    label = spec.get("label", "?")
    eval_path = spec.get("eval_path")
    detections = spec.get("detections")

    # resolve the scoring eval (explicit eval_path, else the extractor's auto-match)
    eval_doc: dict | None = None
    if eval_path:
        ep = g.REPO_ROOT / eval_path
        if not ep.exists():
            discs.append(_disc(ERROR, "eval-missing",
                               f"{label}: eval_path {eval_path} does not exist"))
        else:
            eval_doc = g._load_json(ep)
    elif detections:
        resolved = _auto_match_eval(detections, scope_bounds, index)
        if resolved is None:
            discs.append(_disc(ERROR, "eval-unresolved",
                               f"{label}: no eval auto-matches detections {detections}"))
        else:
            eval_doc = g._load_json(g.REPO_ROOT / resolved)

    if eval_path and not detections:
        discs.append(_disc(WARN, "no-detections",
                           f"{label}: eval_path given without detections — cannot cross-check "
                           f"eval↔detections or feature count"))

    # eval ↔ detections, scope, and feature-count checks (need both the eval and the geojson)
    if eval_doc is not None and detections:
        eval_dets, eval_bounds = _eval_inputs(eval_doc)
        det_norm = g._normalise_detections_path(detections)
        if det_norm not in eval_dets:
            discs.append(_disc(ERROR, "eval-detections-mismatch",
                               f"{label}: eval scored {eval_dets}, not {det_norm}"))
        effective_scope = (spec.get("scope_override") or {}).get("bounds_path") or scope_bounds
        if eval_bounds and effective_scope and eval_bounds != effective_scope:
            discs.append(_disc(ERROR, "scope-mismatch",
                               f"{label}: eval bounds {eval_bounds} != scope {effective_scope}"))
        n_det = (eval_doc.get("summary") or {}).get("n_detections")
        fc = _geojson_feature_count(detections)
        if n_det is not None and fc is not None and n_det != fc:
            discs.append(_disc(ERROR, "feature-count-mismatch",
                               f"{label}: geojson has {fc} features but eval n_detections={n_det}"))

    # pool resolves + n_passes sane
    pool = spec.get("proposer_pool")
    if pool and pool not in proposer_pools and not spec.get("source_run"):
        discs.append(_disc(WARN, "pool-unresolved",
                           f"{label}: proposer_pool '{pool}' is not one of this run's pools "
                           f"(cross-run? add a source_run note)"))
    elif pool in proposer_pools:
        spec_pool = proposer_pools[pool]
        path = spec_pool.get("path") if isinstance(spec_pool, dict) else None
        pool_dir = g.REPO_ROOT / run_dir_rel / (path or f"proposer/{pool}")
        n_on_disk = len(list(pool_dir.glob("run_*")))
        n_passes = spec.get("n_passes")
        if isinstance(n_passes, int) and n_on_disk and n_passes > n_on_disk:
            discs.append(_disc(WARN, "n-passes-over",
                               f"{label}: n_passes={n_passes} exceeds {n_on_disk} run_* dirs"))
    return discs


def verify_completeness(directory_path: str, conditions: list[dict],
                        ignored_evals: set[str], index: dict) -> list[dict]:
    """Flag scored evals under the run that no condition claims and that aren't waived."""
    dir_prefix = g._normalise_detections_path(directory_path.rstrip("/") + "/")
    claimed = {s["eval_path"] for s in conditions if s.get("eval_path")}
    auto_dets = {g._normalise_detections_path(s["detections"])
                 for s in conditions if not s.get("eval_path") and s.get("detections")}
    discs: list[dict] = []
    for det_path, evals in sorted(index.items()):
        if not det_path.startswith(dir_prefix):
            continue
        for eval_rel, summary, _bounds in evals:
            if eval_rel in claimed or eval_rel in ignored_evals or det_path in auto_dets:
                continue
            discs.append(_disc(WARN, "unclaimed-eval",
                               f"scored eval {eval_rel} (n_det={summary.get('n_detections')}) "
                               f"is neither a condition nor in _ignored_evals"))
    return discs


def verify_run(run_id: str, registry_obj: dict, facts: dict, decomposition: dict,
               index: dict) -> dict[str, Any]:
    """Verify one decomposed run; return ``{run_id, verdict, discrepancies}``."""
    entry = next((e for e in registry_obj.get("registry", []) if e["run_id"] == run_id), None)
    if entry is None:
        return {"run_id": run_id, "verdict": "FAIL",
                "discrepancies": [_disc(ERROR, "no-registry", f"{run_id} not in the registry")]}
    decomp = decomposition[run_id]
    run_facts = facts.get(run_id, {})
    scope_bounds = (run_facts.get("scope") or {}).get("bounds_path")
    proposer_pools = decomp.get("proposer_pools", {})
    directory_path = entry["directory_path"]

    discs: list[dict] = []
    for spec in decomp.get("conditions", []):
        discs += verify_condition(spec, scope_bounds, proposer_pools, directory_path, index)
    ignored = {e["eval_path"] if isinstance(e, dict) else e
               for e in decomp.get("_ignored_evals", [])}
    discs += verify_completeness(directory_path, decomp.get("conditions", []), ignored, index)

    has_error = any(d["severity"] == ERROR for d in discs)
    verdict = "FAIL" if has_error else ("PARTIAL" if discs else "PASS")
    return {"run_id": run_id, "verdict": verdict, "discrepancies": discs}


def verify_all(only: str | None = None) -> list[dict]:
    """Verify every decomposed run (or just ``only``)."""
    registry_obj = g.load_run_registry()
    facts = g.load_run_facts()
    decomposition = g.load_run_conditions()
    index = g._build_eval_index()
    run_ids = [r for r in decomposition if (only is None or r == only)]
    return [verify_run(r, registry_obj, facts, decomposition, index) for r in sorted(run_ids)]


def _print_report(reports: list[dict]) -> None:
    """Human-readable verdict + discrepancy listing."""
    icon = {"PASS": "✓", "PARTIAL": "~", "FAIL": "✗"}
    for rep in reports:
        print(f"{icon.get(rep['verdict'], '?')} {rep['verdict']:7s} {rep['run_id']}")
        for d in rep["discrepancies"]:
            print(f"      [{d['severity']}] {d['code']}: {d['message']}")
    n_fail = sum(r["verdict"] == "FAIL" for r in reports)
    n_partial = sum(r["verdict"] == "PARTIAL" for r in reports)
    print(f"\n{len(reports)} run(s): {len(reports) - n_fail - n_partial} pass, "
          f"{n_partial} partial, {n_fail} fail")


def main(argv: list[str] | None = None) -> int:
    """Entry point. Exit 1 if any run FAILs (ERROR-level discrepancy)."""
    parser = argparse.ArgumentParser(description="Tier 1 run-conditions verifier.")
    parser.add_argument("--run", metavar="RUN_ID", help="Verify only this run.")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    args = parser.parse_args(argv)

    reports = verify_all(only=args.run)
    if not reports:
        target = f" {args.run!r}" if args.run else "s"
        print(f"No decomposed run{target} to verify.", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        _print_report(reports)
    return 1 if any(r["verdict"] == "FAIL" for r in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
