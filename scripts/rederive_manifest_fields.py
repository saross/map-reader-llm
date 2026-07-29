#!/usr/bin/env python3
"""Phase 2 (C3) — independent field-level re-derivation of the manifests.

For every row of the five verifiable manifests, re-derive each field
from the row's own cited raw sources (``provenance.source_files``,
``results/run-conditions.json``, ``results/run-facts.json``, the
filesystem) using FRESH extraction code — nothing is imported from
``generate_post_run_report.py``, whose extraction logic is the thing
under test (audit-charter § 7 Phase 2; § 5 rule 1: verify against the
least-writable artefact).

Per-field verdicts:

- ``MATCH``          — independently re-derived value equals the manifest value.
- ``MISMATCH``       — values differ (goes to LLM triage).
- ``SOURCE_SILENT``  — the cited source carries no value for this field
                       (e.g. the retest-era empty ``usage_stats`` wall).
- ``STRUCTURAL``     — identifier/derived fields not independently
                       re-derivable from raw sources (ids, pool slugs).
- ``MISSING_SOURCE`` — a cited provenance file does not exist.

Output: ``reports/verification/c3-rederivation/rederivation-report.json``
with per-row detail and a summary block. Deterministic; run on sapphire
for the official enumeration (charter § 8).

Usage::

    python3 scripts/rederive_manifest_fields.py [--limit N] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = (
    REPO_ROOT / "reports" / "verification" / "c3-rederivation"
    / "rederivation-report.json"
)


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def dig(obj: Any, *paths: str) -> Any:
    """Return the first non-None value at any dotted path in obj."""
    for path in paths:
        cur = obj
        ok = True
        for key in path.split("."):
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return None


def close(a: Any, b: Any, tol: float = 1e-6) -> bool:
    """Equality with float tolerance (costs, seconds, metric values)."""
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a) - float(b)) <= tol
        except (TypeError, ValueError):
            return False
    return a == b


def verdict_row(field: str, manifest_val: Any, derived: Any,
                silent_ok: bool = False) -> dict:
    """Build one field-verdict record."""
    if derived is None:
        if manifest_val is None:
            return {"field": field, "verdict": "MATCH", "manifest": None,
                    "derived": None, "note": "null == null"}
        return {"field": field, "verdict": "SOURCE_SILENT",
                "manifest": manifest_val, "derived": None}
    v = "MATCH" if close(manifest_val, derived) else "MISMATCH"
    return {"field": field, "verdict": v, "manifest": manifest_val,
            "derived": derived}


# --------------------------------------------------------------------------- #
# Passes
# --------------------------------------------------------------------------- #

#: manifest token field -> candidate meta usage_stats keys
TOKEN_MAP = {
    "input_billed": ("usage_stats.total_input_tokens",),
    "input_cached": ("usage_stats.total_cached_tokens",),
    "output": ("usage_stats.total_output_tokens",),
    "thinking": ("usage_stats.total_thoughts_tokens",
                 "usage_stats.total_reasoning_tokens"),
    "total": ("usage_stats.total_tokens",),
}

STRUCTURAL_PASS_FIELDS = ("pass_id", "run_id", "proposer_pool", "pass_n",
                          "modality")


def rederive_pass(row: dict) -> dict:
    """Re-derive one passes-manifest row from its cited meta file(s)."""
    fields: list[dict] = []
    sources = row.get("provenance", {}).get("source_files", [])
    metas = []
    for s in sources:
        p = REPO_ROOT / s
        if not p.exists():
            return {"pass_id": row["pass_id"], "error": "MISSING_SOURCE",
                    "missing": s, "fields": []}
        metas.append(load(p))
    meta = metas[0] if metas else {}

    for f in STRUCTURAL_PASS_FIELDS:
        fields.append({"field": f, "verdict": "STRUCTURAL",
                       "manifest": row.get(f), "derived": None})

    fields.append(verdict_row(
        "model_requested", row.get("model_requested"),
        dig(meta, "configuration.model", "model_requested")))
    fields.append(verdict_row(
        "model_used", row.get("model_used"),
        dig(meta, "model_used", "api_metadata.model_version")))
    fields.append(verdict_row(
        "model_version", row.get("model_version"),
        dig(meta, "model_version", "api_metadata.model_version")))
    fields.append(verdict_row(
        "thinking_level", row.get("thinking_level"),
        dig(meta, "configuration.thinking_level", "thinking_level")))
    fields.append(verdict_row(
        "temperature", row.get("temperature"),
        # temperature_effective carries the E55-corrected value where a
        # serialisation bug left configuration.temperature stale (triage
        # ruling T1, 2026-07-30); prefer it when present.
        dig(meta, "configuration.temperature_effective",
            "configuration.temperature", "temperature")))
    fields.append(verdict_row(
        "instruction_hash", row.get("instruction_hash"),
        dig(meta, "configuration.system_instruction_hash",
            "configuration.instruction_hash", "instruction_hash")))
    fields.append(verdict_row(
        "library_hash", row.get("library_hash"),
        dig(meta, "configuration.library_hash", "library_hash",
            "hashes.library")))
    # Aggregate execution stats across ALL cited metas — a pass row may
    # cite several source files (checkpoint segments); the manifest value
    # is the aggregate, so the re-derivation must aggregate too.
    # Aggregate semantics: checkpoint-segment metas can overlap, so the
    # correct processed count is the UNION of completed_items where the
    # lists exist; sums are the fallback. An execution_stats block that is
    # entirely zero with empty item lists is a recorder gap (same class as
    # the empty usage_stats wall) -> SOURCE_SILENT, not a false mismatch.
    completed: set[str] = set()
    failed_items: set[str] = set()
    all_have_lists = bool(metas)
    agg_processed = agg_failed = agg_retries = 0
    have_ex = ex_all_zero = False
    for mm in metas:
        exs = mm.get("execution_stats") or {}
        if not exs:
            all_have_lists = False
            continue
        have_ex = True
        agg_processed += exs.get("items_processed") or 0
        agg_failed += exs.get("items_failed") or 0
        agg_retries += exs.get("retries_total") or 0
        ci, fi = exs.get("completed_items"), exs.get("failed_items")
        if isinstance(ci, list):
            completed.update(ci)
        else:
            all_have_lists = False
        if isinstance(fi, list):
            for item in fi:
                if isinstance(item, dict):
                    # failed_items entries may be {item/filename: ..., error: ...}
                    name = (item.get("item") or item.get("filename")
                            or item.get("tile") or json.dumps(item, sort_keys=True))
                    failed_items.add(str(name))
                else:
                    failed_items.add(str(item))
    ex_all_zero = (have_ex and agg_processed == 0 and agg_failed == 0
                   and not completed and not failed_items)
    if have_ex and not ex_all_zero:
        n_proc = len(completed) if all_have_lists and completed else agg_processed
        n_fail = (len(failed_items - completed)
                  if all_have_lists and (completed or failed_items)
                  else agg_failed)
        if n_proc > 0 and n_fail == 0:
            derived_status = "ok"
        elif n_proc > 0:
            derived_status = "partial"
        else:
            derived_status = "failed"
        fields.append(verdict_row("status", row.get("status"), derived_status))
        fields.append(verdict_row("n_tiles_processed",
                                  row.get("n_tiles_processed"), n_proc))
    elif ex_all_zero:
        for f in ("status", "n_tiles_processed"):
            fields.append({"field": f, "verdict": "SOURCE_SILENT",
                           "manifest": row.get(f), "derived": None,
                           "note": "recorder gap: execution_stats all-zero"})
    else:
        fields.append(verdict_row("status", row.get("status"),
                                  dig(meta, "status", "run_status")))
        fields.append(verdict_row(
            "n_tiles_processed", row.get("n_tiles_processed"),
            dig(meta, "n_tiles_processed", "tiles_processed")))

    # tokens: the retest-era wall — usage blocks present but all-zero are
    # treated as SILENT when the manifest also records zeros/nulls, and as
    # a MISMATCH source otherwise (a zero source against a non-zero claim
    # is a real discrepancy, not silence).
    usage = meta.get("usage_stats") or {}
    usage_empty = all(
        not any(v > 0 for v in (mm.get("usage_stats") or {}).values()
                if isinstance(v, (int, float)))
        for mm in metas) and bool(usage)
    man_tokens = row.get("tokens") or {}
    for mf, cands in TOKEN_MAP.items():
        vals = [dig(mm, *cands) for mm in metas]
        vals = [v for v in vals if v is not None]
        derived = sum(vals) if vals else None
        man_val = man_tokens.get(mf)
        if usage_empty:
            if not man_val:
                fields.append({"field": f"tokens.{mf}", "verdict": "SOURCE_SILENT",
                               "manifest": man_val, "derived": None,
                               "note": "era-wall: usage_stats unpopulated"})
            else:
                fields.append({"field": f"tokens.{mf}", "verdict": "MISMATCH",
                               "manifest": man_val, "derived": 0,
                               "note": "manifest non-zero over empty usage block"})
        else:
            fields.append(verdict_row(f"tokens.{mf}", man_val, derived))

    costs = [dig(mm, "cost_estimate.total_cost_usd",
                 "cost_estimate.total_usd", "cost_usd") for mm in metas]
    costs = [c for c in costs if c is not None]
    fields.append(verdict_row(
        "cost_usd", row.get("cost_usd"),
        round(sum(costs), 6) if costs else None))
    durs = [dig(mm, "timestamp.duration_seconds", "wall_clock_s")
            for mm in metas]
    durs = [x for x in durs if x is not None]
    fields.append(verdict_row(
        "wall_clock_s", row.get("wall_clock_s"),
        sum(durs) if durs else None))
    man_ts = row.get("timestamps") or {}
    starts = [dig(mm, "timestamp.start", "start_time") for mm in metas]
    ends = [dig(mm, "timestamp.end", "end_time") for mm in metas]
    starts = [s for s in starts if s]
    ends = [e for e in ends if e]
    fields.append(verdict_row("timestamps.start", man_ts.get("start"),
                              min(starts) if starts else None))
    fields.append(verdict_row("timestamps.end", man_ts.get("end"),
                              max(ends) if ends else None))
    fields.append(verdict_row(
        "retries", row.get("retries"),
        agg_retries if have_ex else dig(meta, "retries")))

    return {"pass_id": row["pass_id"], "fields": fields}


# --------------------------------------------------------------------------- #
# Conditions
# --------------------------------------------------------------------------- #

FACTOR_FIELDS = ("architecture", "aggregation", "proposer_pool", "n_passes",
                 "vote_threshold", "prob_threshold", "verifier_config",
                 "scope_override")


def rederive_condition(row: dict, decomposition: dict) -> dict:
    """Re-derive one conditions row from its eval JSON + the decomposition."""
    fields: list[dict] = []
    for f in ("condition_id", "run_id", "label"):
        fields.append({"field": f, "verdict": "STRUCTURAL",
                       "manifest": row.get(f), "derived": None})

    # factor fields against the decomposition sidecar (independent load)
    fam = decomposition.get(row["run_id"], {})
    cond = next((c for c in fam.get("conditions", [])
                 if c.get("label") == row.get("label")), None)
    for f in FACTOR_FIELDS:
        if cond is None:
            fields.append({"field": f, "verdict": "SOURCE_SILENT",
                           "manifest": row.get(f), "derived": None,
                           "note": "no matching decomposition condition"})
        elif f == "scope_override":
            fields.append(verdict_row(f, row.get(f), cond.get(f),
                                      silent_ok=True))
        else:
            fields.append(verdict_row(f, row.get(f), cond.get(f)))

    # metrics against the cited eval JSON
    sources = row.get("provenance", {}).get("source_files", [])
    eval_path = next((s for s in sources if s.endswith(".json")), None)
    if eval_path is None or not (REPO_ROOT / eval_path).exists():
        fields.append({"field": "metrics", "verdict": "MISSING_SOURCE",
                       "manifest": "(block)", "derived": None,
                       "missing": eval_path})
        return {"condition_id": row["condition_id"], "fields": fields}
    ev = load(REPO_ROOT / eval_path)

    fields.append(verdict_row(
        "n_detections", row.get("n_detections"),
        dig(ev, "summary.n_detections", "n_detections")))

    man_pb = (row.get("metrics") or {}).get("per_buffer") or {}
    raw_buffers = dig(ev, "summary.buffers", "per_buffer", "buffers") or []
    if isinstance(raw_buffers, list):
        ev_pb = {}
        for b in raw_buffers:
            key = str(b.get("buffer_metres"))
            ev_pb[key] = {
                "f1": b.get("f1"), "precision": b.get("precision"),
                "recall": b.get("recall"),
                "ci": {"low": b.get("f1_ci_lower"),
                       "high": b.get("f1_ci_upper")},
            }
    else:
        ev_pb = raw_buffers
    n_match = n_mismatch = n_silent = 0
    mismatches: list[str] = []
    for buf, man_m in man_pb.items():
        ev_m = ev_pb.get(buf) or ev_pb.get(str(buf)) or {}
        for metric in ("f1", "precision", "recall"):
            mv, dv = man_m.get(metric), ev_m.get(metric)
            if dv is None:
                n_silent += 1
            elif close(mv, dv, tol=5e-5):
                n_match += 1
            else:
                n_mismatch += 1
                mismatches.append(f"{buf}m/{metric}: {mv} vs {dv}")
        man_ci, ev_ci = man_m.get("ci") or {}, ev_m.get("ci") or {}
        for cf in ("low", "high"):
            mv, dv = man_ci.get(cf), ev_ci.get(cf)
            if dv is None:
                n_silent += 1
            elif close(mv, dv, tol=5e-5):
                n_match += 1
            else:
                n_mismatch += 1
                mismatches.append(f"{buf}m/ci.{cf}: {mv} vs {dv}")
    fields.append({
        "field": "metrics.per_buffer",
        "verdict": "MISMATCH" if n_mismatch else
                   ("MATCH" if n_match else "SOURCE_SILENT"),
        "n_values_match": n_match, "n_values_mismatch": n_mismatch,
        "n_values_silent": n_silent,
        "mismatches": mismatches[:20],
    })

    man_tc = (row.get("metrics") or {}).get("tile_classification")
    ev_tc = dig(ev, "summary.tile_classification", "tile_classification")
    if man_tc is not None:
        if ev_tc is None:
            fields.append({"field": "metrics.tile_classification",
                           "verdict": "SOURCE_SILENT",
                           "manifest": "(block)", "derived": None})
        else:
            def flat(tc: dict) -> dict:
                conf = tc.get("confusion") or {}
                def pt(v):
                    return v.get("point") if isinstance(v, dict) else v
                return {"tp": conf.get("tp", tc.get("tp")),
                        "tn": conf.get("tn", tc.get("tn")),
                        "fp": conf.get("fp", tc.get("fp")),
                        "fn": conf.get("fn", tc.get("fn")),
                        "mcc": pt(tc.get("mcc")),
                        "sensitivity": pt(tc.get("sensitivity")),
                        "specificity": pt(tc.get("specificity"))}
            man_flat, ev_flat = flat(man_tc), flat(ev_tc)
            same = all(close(man_flat.get(k), ev_flat.get(k), tol=5e-5)
                       for k in man_flat if man_flat.get(k) is not None)
            fields.append({"field": "metrics.tile_classification",
                           "verdict": "MATCH" if same else "MISMATCH",
                           "manifest": man_tc if not same else "(block)",
                           "derived": ev_tc if not same else "(block)"})
    return {"condition_id": row["condition_id"], "fields": fields}


# --------------------------------------------------------------------------- #
# Runs, analyses, registry (the +890 GATE 0 extension)
# --------------------------------------------------------------------------- #

def rederive_simple() -> list[dict]:
    """Existence/consistency checks for runs, analyses, and the registry."""
    out: list[dict] = []
    registry = load(REPO_ROOT / "results/run-registry.json")["registry"]
    for e in registry:
        exists = (REPO_ROOT / e["directory_path"]).exists()
        planned = e.get("status") == "planned"
        out.append({"row": f"registry::{e['run_id']}",
                    "verdict": "MATCH" if (exists or planned) else "MISMATCH",
                    "detail": f"directory_path exists={exists}, "
                              f"status={e.get('status')}"})
    runs = load(REPO_ROOT / "results/runs-manifest.json")["runs"]
    for r in runs:
        exists = (REPO_ROOT / r["directory_path"]).exists()
        prr = r.get("post_run_report_path")
        prr_ok = prr is None or (REPO_ROOT / prr).exists()
        v = "MATCH" if exists and prr_ok else "MISMATCH"
        out.append({"row": f"runs::{r['run_id']}", "verdict": v,
                    "detail": f"dir={exists}, post_run_report={prr_ok}"})
    analyses = load(REPO_ROOT / "results/analyses-manifest.json")["analyses"]
    cond_ids = {c["condition_id"] for c in
                load(REPO_ROOT / "results/conditions-manifest.json")["conditions"]}
    for a in analyses:
        op = a.get("output_path")
        op_ok = op is None or (REPO_ROOT / op).exists()
        fks = [c for c in (a.get("conditions_compared") or [])
               if c not in cond_ids]
        v = "MATCH" if op_ok and not fks else "MISMATCH"
        out.append({"row": f"analyses::{a['analysis_id']}", "verdict": v,
                    "detail": f"output_path={op_ok}, unresolved FKs={fks}"})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 2 C3 manifest field re-derivation.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Restrict passes/conditions to the first N rows "
                             "(local smoke testing).")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    passes = load(REPO_ROOT / "results/passes-manifest.json")["passes"]
    conditions = load(REPO_ROOT / "results/conditions-manifest.json")["conditions"]
    decomposition = load(
        REPO_ROOT / "results/run-conditions.json")["decomposition"]
    if args.limit:
        passes, conditions = passes[:args.limit], conditions[:args.limit]

    pass_results = [rederive_pass(r) for r in passes]
    cond_results = [rederive_condition(r, decomposition) for r in conditions]
    simple_results = rederive_simple()

    def tally(results: list[dict]) -> dict[str, int]:
        t: dict[str, int] = {}
        for r in results:
            if r.get("error"):
                t["MISSING_SOURCE"] = t.get("MISSING_SOURCE", 0) + 1
                continue
            for f in r["fields"]:
                t[f["verdict"]] = t.get(f["verdict"], 0) + 1
        return t

    report = {
        "_README": "Phase 2 C3 field-level re-derivation (audit-charter § 7). "
                   "Fresh extraction code, no imports from the generator. "
                   "Verdict vocabulary in scripts/rederive_manifest_fields.py.",
        "summary": {
            "n_passes": len(pass_results),
            "n_conditions": len(cond_results),
            "n_simple_rows": len(simple_results),
            "passes_verdicts": tally(pass_results),
            "conditions_verdicts": tally(cond_results),
            "simple_verdicts": {
                v: sum(1 for r in simple_results if r["verdict"] == v)
                for v in ("MATCH", "MISMATCH")},
        },
        "passes": pass_results,
        "conditions": cond_results,
        "simple": simple_results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
