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

**The verifier is the methodology-audit instrument**, not just a gate on authoring:
the manifest build doubles as a methodology audit, so most checks **WARN** — they
surface a result for human adjudication (re-score to standardise, or accept) —
rather than hard-failing. **ERROR** is reserved for the unambiguous wrong-source
cases (a named eval that scored a *different* file; a real scope leak where both
bounds are known). A feature-count divergence, a bounds-less eval, or an
unclaimed eval are WARNs: each is a signal that a result may be stale,
non-standard, or missing — the re-scoring worklist, not a failure.

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


def _geojson_coord_frame(rel_path: str) -> str | None:
    """Classify a geojson's coordinate frame for the CRS sanity check.

    Returns ``"utm-no-crs"`` — projected metres (first |x| > 180°) with NO declared
    ``crs`` member, the silent-misread hazard behind the 2026-05-31 F1=0 bug: the
    scorer trusts a missing ``crs`` as WGS84 and mis-reprojects the points off the
    tile grid. Returns ``"ok"`` for WGS84 degrees, or projected coords that DO carry
    an explicit ``crs`` (the scorer reprojects those correctly). ``None`` if
    unreadable.
    """
    path = g.REPO_ROOT / rel_path
    if not path.exists():
        return None
    try:
        doc = g._load_json(path)
    except (json.JSONDecodeError, OSError):
        return None
    feats = doc.get("features")
    if not isinstance(feats, list) or not feats:
        return None
    coord = feats[0].get("geometry", {}).get("coordinates")
    while isinstance(coord, list) and coord and isinstance(coord[0], list):
        coord = coord[0]
    if not (isinstance(coord, list) and coord and isinstance(coord[0], (int, float))):
        return None
    return "utm-no-crs" if abs(coord[0]) > 180 and "crs" not in doc else "ok"


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

    # CRS sanity: projected metres with no declared crs are silently misread as WGS84
    # by the scorer and mis-reprojected off the tile grid (the 2026-05-31 F1=0 bug).
    if detections and _geojson_coord_frame(detections) == "utm-no-crs":
        discs.append(_disc(WARN, "crs-missing-utm",
                           f"{label}: detections look like projected metres (|x|>180) with no "
                           f"crs member — silent-misread hazard; declare the CRS or reproject"))

    # scope_override may be mis-authored as a bare string instead of a scope dict;
    # resolve it defensively so a typo surfaces as a discrepancy, not a crash.
    so = spec.get("scope_override")
    if so is not None and not isinstance(so, dict):
        discs.append(_disc(WARN, "scope-override-malformed",
                           f"{label}: scope_override is not a scope object ({so!r})"))
    override_bounds = so.get("bounds_path") if isinstance(so, dict) else None
    effective_scope = override_bounds or scope_bounds

    # eval ↔ detections, scope, and feature-count checks (need both the eval and the geojson)
    if eval_doc is not None and detections:
        eval_dets, eval_bounds = _eval_inputs(eval_doc)
        det_norm = g._normalise_detections_path(detections)
        if det_norm not in eval_dets:
            # the eval scored a different named file — unambiguous wrong-source
            discs.append(_disc(ERROR, "eval-detections-mismatch",
                               f"{label}: eval scored {eval_dets}, not {det_norm}"))
        if eval_bounds and effective_scope and eval_bounds != effective_scope:
            # a real scope leak, both bounds known — hard error
            discs.append(_disc(ERROR, "scope-mismatch",
                               f"{label}: eval bounds {eval_bounds} != scope {effective_scope}"))
        elif effective_scope and not eval_bounds:
            # cannot confirm scope (bounds-less eval) — surface, don't skip silently
            discs.append(_disc(WARN, "scope-uncheckable",
                               f"{label}: eval records no bounds; scope unconfirmed "
                               f"({effective_scope})"))
        n_det = (eval_doc.get("summary") or {}).get("n_detections")
        fc = _geojson_feature_count(detections)
        if fc is None:
            discs.append(_disc(WARN, "geojson-missing",
                               f"{label}: detections missing/unreadable — feature check skipped "
                               f"({detections})"))
        elif n_det is not None and n_det != fc:
            # divergence is a SIGNAL for adjudication (stale eval vs benign drift),
            # NOT a hard error — the verifier surfaces; the human decides re-run vs accept
            discs.append(_disc(WARN, "feature-count-drift",
                               f"{label}: geojson has {fc} features but eval n_detections={n_det} "
                               f"(possible stale eval — re-score or accept)"))
        # all-zero F1 across every buffer is a scoring red flag (a CRS misread can make
        # detections match nothing at any radius while tile-MCC still shows faint signal)
        f1s = [b.get("f1") for b in ((eval_doc.get("summary") or {}).get("buffers") or [])]
        if f1s and all(v in (0, 0.0, None) for v in f1s):
            discs.append(_disc(WARN, "f1-all-zero",
                               f"{label}: F1 is 0 at every buffer — a scoring red flag "
                               f"(e.g. a CRS misread), likely not a real result"))

    # pool resolves + n_passes sane
    pool = spec.get("proposer_pool")
    if pool and pool not in proposer_pools and not spec.get("source_run"):
        discs.append(_disc(WARN, "pool-unresolved",
                           f"{label}: proposer_pool '{pool}' is not one of this run's pools "
                           f"(cross-run? add a source_run note)"))
    elif pool in proposer_pools:
        spec_pool = proposer_pools[pool]
        path = spec_pool.get("path") if isinstance(spec_pool, dict) else None
        rel = path or f"proposer/{pool}"
        pool_dir = g.REPO_ROOT / run_dir_rel / rel
        if not pool_dir.is_dir():
            # a string-form pool with no explicit path can resolve to a non-existent
            # proposer/<pool> dir — surface it rather than silently skipping n_passes
            discs.append(_disc(WARN, "pool-dir-not-found",
                               f"{label}: pool path '{rel}' not found under {run_dir_rel} "
                               f"— n_passes uncheckable"))
        else:
            n_on_disk = len(list(pool_dir.glob("run_*")))
            n_passes = spec.get("n_passes")
            if isinstance(n_passes, int) and n_passes > n_on_disk:
                discs.append(_disc(WARN, "n-passes-over",
                                   f"{label}: n_passes={n_passes} exceeds {n_on_disk} run_* dirs"))
    return discs


def verify_completeness(directory_path: str, conditions: list[dict],
                        ignored_evals: set[str], index: dict) -> list[dict]:
    """Flag scored evals under the run that no condition claims and that aren't waived.

    Limitation: only evals whose detections live under the run's own directory are
    considered, so a CROSS-RUN condition (whose eval/detections sit under another
    run, e.g. h12-v2's r2-balanced reusing an h10 pool) is not completeness-checked
    here — it must be accounted for under the run that physically owns its eval.
    """
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


def _eval_completeness(summary: dict) -> tuple[bool, bool]:
    """``(has_full_buffers, has_mcc)`` for an evaluation.json ``summary``.

    Full buffers = the canonical 20/30/40/50 m set is present; MCC = a
    ``tile_classification`` block exists.
    """
    buffers = {b.get("buffer_metres") for b in (summary.get("buffers") or [])}
    return {20, 30, 40, 50} <= buffers, bool(summary.get("tile_classification"))


def classify_run(run_id: str, registry_obj: dict, index: dict) -> dict:
    """Classify a run's scored evals for the re-scoring worklist (the audit pass).

    For each ``evaluation.json`` that scored a detection under the run, decides
    ``standard-current`` (full buffers + MCC + n_detections present and matching the
    geojson) vs ``needs-rescore`` (with reasons: partial-buffers / no-mcc / stale /
    no-n_detections). A run with materialised detection outputs but ZERO standard
    evals is flagged ``no_standard_scoring`` — its results were scored by a
    non-standard pipeline (leaderboard / sweep) or not at all, so they need
    re-scoring to standardise. The worklist's purpose: prefer re-scoring to
    standardise over building adapters for legacy eval shapes.
    """
    entry = next((e for e in registry_obj.get("registry", []) if e["run_id"] == run_id), None)
    if entry is None:
        return {"run_id": run_id, "error": "not in registry"}
    dpath = entry["directory_path"]
    dir_prefix = g._normalise_detections_path(dpath.rstrip("/") + "/")

    evals: list[dict] = []
    for det_path, evs in sorted(index.items()):
        if not det_path.startswith(dir_prefix):
            continue
        fc = _geojson_feature_count(det_path)
        for eval_rel, summary, _bounds in evs:
            has_full, has_mcc = _eval_completeness(summary)
            n_det = summary.get("n_detections")
            reasons: list[str] = []
            if not has_full:
                reasons.append("partial-buffers")
            if not has_mcc:
                reasons.append("no-mcc")
            if n_det is None:
                reasons.append("no-n_detections")
            elif fc is not None and n_det != fc:
                reasons.append(f"stale:{fc}vs{n_det}")
            evals.append({"eval": eval_rel,
                          "status": "standard-current" if not reasons else "needs-rescore",
                          "reasons": reasons})

    run_dir = g.REPO_ROOT / dpath
    materialised = 0
    if run_dir.is_dir():
        for p in run_dir.rglob("*.geojson"):
            parts = p.relative_to(run_dir).parts
            # count aggregation/verified outputs, not raw proposer passes or crops
            if any(part == "crops" or (part.startswith("run_") and part[4:].isdigit())
                   for part in parts):
                continue
            materialised += 1

    n_std = sum(1 for e in evals if e["status"] == "standard-current")
    return {
        "run_id": run_id,
        "directory_path": dpath,
        "n_evals": len(evals),
        "n_standard_current": n_std,
        "n_needs_rescore": len(evals) - n_std,
        "n_materialised_geojson": materialised,
        "no_standard_scoring": len(evals) == 0 and materialised > 0,
        "evals": evals,
    }


def classify_all() -> list[dict]:
    """Classify every EXECUTED registered run for the re-scoring worklist.

    ``status: planned`` runs are skipped. They have no directory and no
    evaluations by design, so classifying one yields a row of zeros that is
    indistinguishable from an executed run whose evaluations are missing — and
    ``no_standard_scoring`` evaluates to False on it (``0 == 0 and 0 > 0``), so it
    would not even be flagged. A silently mis-classified planned run is worse than
    a crash, because it enters the worklist looking like real but unscored work.
    """
    registry_obj = g.load_run_registry()
    index = g._build_eval_index()
    return [classify_run(e["run_id"], registry_obj, index)
            for e in registry_obj.get("registry", [])
            if isinstance(e, dict) and e.get("status") != "planned"]


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
    parser.add_argument("--classify", action="store_true",
                        help="Audit pass: classify every run's evals (standard-current vs "
                             "needs-rescore) for the re-scoring worklist; emits JSON.")
    args = parser.parse_args(argv)

    if args.classify:
        print(json.dumps(classify_all(), indent=2))
        return 0

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
