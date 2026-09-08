#!/usr/bin/env python3
"""Survey verifier-stage directories for sweep/probabilities staleness.

Purpose
-------
A "verifier stage" is any directory under ``outputs/`` holding a
``probabilities.json`` whose ``results`` carry ``mound_probability`` values.
Some stages were verified in two events: an initial run, then a later
"cleanup" pass that filled in missing probabilities.  A threshold sweep
(``sweep_2d.json``) computed BEFORE that cleanup describes only a partial
verification and is therefore STALE.

This script enumerates every stage, reads the sweep (if present), pulls the
last git commit touching each artefact, and classifies the stage.  It also
cross-references the run register (``results/run-conditions.json``,
``results/run-analyses.json``) and greps the Markdown corpus for citations of
flagged stages.

Read-only: it never writes inside the repository.

Usage
-----
    # on sapphire (compute-location rule), from the synced repo root
    python scripts/survey_sweep_staleness.py --repo . --out /tmp/survey-out
    # then copy survey.json to reports/sweep-staleness-survey-<date>.json and
    # render with scripts/render_sweep_staleness_report.py

Outputs ``survey.json`` (raw per-stage records) into the ``--out`` directory.
First run: 2026-09-08 (Session 151), preserved as
``reports/sweep-staleness-survey-2026-09-08.json``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------
# git helpers
# --------------------------------------------------------------------------


def build_last_commit_map(repo: Path, pathspecs: list[str]) -> dict[str, dict[str, Any]]:
    """Return {relative path: {commit, date, subject}} for the LAST commit
    touching each path.

    One ``git log --name-only`` traversal is used instead of N per-file
    invocations; the first time a path appears (log order is newest first) is
    its most recent commit.
    """
    cmd = [
        "git",
        "-C",
        str(repo),
        "log",
        "--pretty=format:\x01%H\x02%ad\x02%s",
        "--date=short",
        "--name-only",
        "--",
        *pathspecs,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    last: dict[str, dict[str, Any]] = {}
    commit = date = subject = ""
    for line in proc.stdout.splitlines():
        if line.startswith("\x01"):
            commit, date, subject = line[1:].split("\x02", 2)
            continue
        path = line.strip()
        if not path:
            continue
        if path not in last:
            last[path] = {"commit": commit[:9], "full_commit": commit, "date": date,
                          "subject": subject}
    return last


def commit_history(repo: Path, rel_path: str, limit: int = 5) -> list[dict[str, str]]:
    """Return up to ``limit`` recent commits touching one path (newest first)."""
    cmd = [
        "git", "-C", str(repo), "log", f"-{limit}",
        "--pretty=format:%H\x02%ad\x02%s", "--date=short", "--", rel_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    out = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        h, d, s = line.split("\x02", 2)
        out.append({"commit": h[:9], "date": d, "subject": s})
    return out


# --------------------------------------------------------------------------
# probabilities.json parsing
# --------------------------------------------------------------------------


def parse_probabilities(path: Path) -> dict[str, Any] | None:
    """Read one probabilities.json.

    Returns None when the file is not a verifier-stage probabilities file
    (no ``results`` container carrying ``mound_probability``).
    """
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:  # noqa: BLE001 - want the reason recorded
        return {"parse_error": f"{type(exc).__name__}: {exc}"}

    if not isinstance(data, dict):
        return None
    results = data.get("results")
    if results is None:
        return None

    n_results = 0
    n_with_prob = 0
    null_ids: list[str] = []
    has_mp_key = False

    if isinstance(results, dict):
        items = results.items()
    elif isinstance(results, list):
        items = [
            (str(entry.get("candidate_id", idx)) if isinstance(entry, dict) else str(idx), entry)
            for idx, entry in enumerate(results)
        ]
    else:
        return None

    for key, entry in items:
        n_results += 1
        if not isinstance(entry, dict):
            continue
        if "mound_probability" in entry:
            has_mp_key = True
            if entry["mound_probability"] is not None:
                n_with_prob += 1
            else:
                null_ids.append(key)
        else:
            null_ids.append(key)

    if not has_mp_key:
        return None

    cleanup = data.get("cleanup_history")
    cleanup_recovered = None
    cleanup_events = None
    if cleanup:
        if isinstance(cleanup, list):
            cleanup_events = len(cleanup)
            cleanup_recovered = [
                {
                    "timestamp": ev.get("timestamp"),
                    "initial_missing": ev.get("initial_missing"),
                    "recovered": ev.get("recovered"),
                    "still_missing": ev.get("still_missing"),
                }
                for ev in cleanup
                if isinstance(ev, dict)
            ]
        else:
            cleanup_events = 1
            cleanup_recovered = [cleanup]

    return {
        "n_results": n_results,
        "n_with_probability": n_with_prob,
        "n_null_probability": n_results - n_with_prob,
        "null_ids_sample": null_ids[:10],
        "total_results_field": data.get("total_results"),
        "cleanup_history_present": bool(cleanup),
        "cleanup_events": cleanup_events,
        "cleanup_recovered": cleanup_recovered,
        "mode": data.get("mode"),
        "iterations": data.get("iterations"),
        "version": data.get("version"),
    }


def find_manifest(stage_dir: Path) -> dict[str, Any] | None:
    """Locate the crop manifest that defines the candidate pool for a stage.

    Placement varies across vintages.  ``candidate_manifest.json`` sits either
    directly in the stage directory, inside ``<stage>/crops/``, or (older runs
    with shared crops) in a ``crops/`` directory beside the stage.  Only the
    first two are authoritative for that stage; a sibling ``crops/`` may be
    shared between stages, so it is recorded as advisory only.
    """
    candidates = [
        (stage_dir / "candidate_manifest.json", "in-stage"),
        (stage_dir / "crops" / "candidate_manifest.json", "in-crops"),
        (stage_dir.parent / "crops" / "candidate_manifest.json", "sibling-crops"),
    ]
    for path, scope in candidates:
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            return {"scope": scope, "error": f"{type(exc).__name__}: {exc}"}
        n_cands = len(data.get("candidates") or [])
        return {
            "scope": scope,
            "authoritative": scope in {"in-stage", "in-crops"},
            "n_candidates": n_cands,
            "total_detections": data.get("total_detections"),
            "successful_extractions": data.get("successful_extractions"),
            "failed_extractions": data.get("failed_extractions"),
        }
    return None


# --------------------------------------------------------------------------
# sweep parsing
# --------------------------------------------------------------------------


def parse_sweep(path: Path) -> dict[str, Any]:
    """Read one sweep file and extract the 'no filter' candidate count.

    The canonical schema is a top-level LIST of rows with keys
    ``config, vote_t, prob_t, n, p, r, f1, buffer_m``.  The "all candidates"
    row is the one with the LOWEST vote threshold and ``prob_t == 0.0``; the
    max ``n`` over buffers/configs at that point is the candidate pool size.
    """
    record: dict[str, Any] = {"file": path.name, "schema": None, "all_cand_n": None,
                              "unparsed_reason": None}
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:  # noqa: BLE001
        record["unparsed_reason"] = f"JSON load failed: {type(exc).__name__}: {exc}"
        return record

    rows: list[dict[str, Any]] | None = None
    if isinstance(data, list):
        rows = [r for r in data if isinstance(r, dict)]
        record["schema"] = "list-of-rows"
    elif isinstance(data, dict):
        # Try common wrapper keys.
        for key in ("rows", "sweep", "results", "grid", "sweep_rows", "data"):
            value = data.get(key)
            if isinstance(value, list) and value and isinstance(value[0], dict):
                rows = value
                record["schema"] = f"dict-wrapped:{key}"
                break
        if rows is None:
            record["unparsed_reason"] = (
                "top-level dict with no recognised row list; keys="
                + ",".join(sorted(data.keys())[:15])
            )
            return record

    if not rows:
        record["unparsed_reason"] = "empty row list"
        return record

    record["n_rows"] = len(rows)
    sample_keys = sorted(rows[0].keys())
    record["row_keys"] = sample_keys

    vote_key = next((k for k in ("vote_t", "vote_threshold", "vt") if k in rows[0]), None)
    prob_key = next((k for k in ("prob_t", "prob_threshold", "pt") if k in rows[0]), None)
    n_key = next((k for k in ("n", "n_detections", "count") if k in rows[0]), None)
    if n_key is None:
        record["unparsed_reason"] = f"no candidate-count key in rows; keys={sample_keys}"
        return record

    record["configs"] = sorted({str(r.get("config")) for r in rows if "config" in r})[:12]
    record["buffers"] = sorted({r.get("buffer_m") for r in rows if r.get("buffer_m") is not None})

    if vote_key is None and prob_key is None:
        record["unparsed_reason"] = f"no vote/prob threshold keys; keys={sample_keys}"
        return record

    candidates = rows
    if vote_key is not None:
        votes = [r[vote_key] for r in rows if r.get(vote_key) is not None]
        if votes:
            min_vote = min(votes)
            record["min_vote_t"] = min_vote
            candidates = [r for r in candidates if r.get(vote_key) == min_vote]
    if prob_key is not None:
        probs = [r[prob_key] for r in candidates if r.get(prob_key) is not None]
        if probs:
            min_prob = min(probs)
            record["min_prob_t"] = min_prob
            candidates = [r for r in candidates if r.get(prob_key) == min_prob]

    ns = [r[n_key] for r in candidates if isinstance(r.get(n_key), (int, float))]
    if not ns:
        record["unparsed_reason"] = "no numeric n at the minimum-threshold rows"
        return record
    record["all_cand_n"] = int(max(ns))
    record["all_cand_n_min"] = int(min(ns))
    record["max_n_any_row"] = int(
        max(r[n_key] for r in rows if isinstance(r.get(n_key), (int, float)))
    )
    return record


# --------------------------------------------------------------------------
# main survey
# --------------------------------------------------------------------------


def classify(stage: dict[str, Any]) -> str:
    """Assign a verdict to one stage record."""
    sweeps = stage["sweeps"]
    if not sweeps:
        return "NO SWEEP"
    parsed = [s for s in sweeps if s.get("all_cand_n") is not None]
    if not parsed:
        return "UNPARSED"

    n_with = stage["n_with_probability"]
    best_n = max(s["all_cand_n"] for s in parsed)

    if best_n == n_with:
        return "CONSISTENT"
    if best_n < n_with:
        return "STALE"
    # best_n > n_with: sweep covers more candidates than currently hold a
    # probability -- not the staleness class under survey.
    return "SWEEP_EXCEEDS_PROBS"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="repository root")
    ap.add_argument("--out", required=True, help="output directory for survey.json")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = repo / "outputs"
    prob_files = sorted(outputs.rglob("probabilities.json"))
    print(f"found {len(prob_files)} probabilities.json under outputs/", file=sys.stderr)

    print("building git last-commit map ...", file=sys.stderr)
    commit_map = build_last_commit_map(repo, ["outputs", "results"])
    print(f"  {len(commit_map)} paths in map", file=sys.stderr)

    stages: list[dict[str, Any]] = []
    skipped: list[str] = []

    for idx, prob_path in enumerate(prob_files, 1):
        rel_dir = prob_path.parent.relative_to(repo).as_posix()
        if idx % 25 == 0:
            print(f"  [{idx}/{len(prob_files)}] {rel_dir}", file=sys.stderr)
        info = parse_probabilities(prob_path)
        if info is None:
            skipped.append(rel_dir)
            continue
        if "parse_error" in info:
            stages.append({
                "stage_dir": rel_dir,
                "verdict": "UNPARSED",
                "prob_parse_error": info["parse_error"],
                "sweeps": [],
            })
            continue

        rel_prob = prob_path.relative_to(repo).as_posix()
        prob_commit = commit_map.get(rel_prob)

        sweep_paths = sorted(
            p for p in prob_path.parent.iterdir()
            if p.is_file() and p.name.startswith("sweep")
        )
        sweeps = []
        for sweep_path in sweep_paths:
            srec = parse_sweep(sweep_path)
            rel_sweep = sweep_path.relative_to(repo).as_posix()
            srec["path"] = rel_sweep
            srec["git"] = commit_map.get(rel_sweep)
            sweeps.append(srec)

        manifest = find_manifest(prob_path.parent)
        # Incompleteness has two forms.  (a) Entries present but null-valued.
        # (b) Entries ABSENT altogether -- the form the known cleanup case took
        # (342 -> 802 results), only visible against the crop manifest.
        incomplete_null = info["n_with_probability"] < info["n_results"]
        incomplete_missing = False
        manifest_shortfall = None
        if manifest and manifest.get("authoritative") and manifest.get("n_candidates"):
            manifest_shortfall = manifest["n_candidates"] - info["n_with_probability"]
            incomplete_missing = manifest_shortfall > 0
        still_missing = 0
        for ev in (info.get("cleanup_recovered") or []):
            still_missing += ev.get("still_missing") or 0

        stage = {
            "stage_dir": rel_dir,
            **{k: v for k, v in info.items() if k != "null_ids_sample"},
            "null_ids_sample": info["null_ids_sample"],
            "prob_git_last": prob_commit,
            "sweeps": sweeps,
            "manifest": manifest,
            "manifest_shortfall": manifest_shortfall,
            "cleanup_still_missing": still_missing,
            "incomplete": incomplete_null or incomplete_missing or still_missing > 0,
            "incomplete_reasons": [
                r for r, flag in (
                    ("null-valued entries", incomplete_null),
                    ("entries absent vs crop manifest", incomplete_missing),
                    ("cleanup_history still_missing > 0", still_missing > 0),
                ) if flag
            ],
        }
        stage["verdict"] = classify(stage)

        # Secondary staleness signal: sweep predates probabilities AND counts differ.
        for srec in sweeps:
            sg, pg = srec.get("git"), prob_commit
            srec["sweep_predates_probs"] = bool(
                sg and pg and sg["date"] < pg["date"]
            )
        if stage["verdict"] in {"CONSISTENT", "SWEEP_EXCEEDS_PROBS"}:
            for srec in sweeps:
                if (
                    srec.get("sweep_predates_probs")
                    and srec.get("all_cand_n") is not None
                    and srec["all_cand_n"] != stage["n_with_probability"]
                    and stage["verdict"] != "CONSISTENT"
                ):
                    stage["verdict"] = "STALE"
        stages.append(stage)

    print(f"parsed {len(stages)} stages; skipped {len(skipped)} non-verifier files",
          file=sys.stderr)

    # ---------------------------------------------------------------- register
    conditions_path = repo / "results" / "run-conditions.json"
    analyses_path = repo / "results" / "run-analyses.json"
    cond_index: list[dict[str, Any]] = []
    pass_index: list[dict[str, Any]] = []
    unresolved_passes: list[dict[str, Any]] = []
    stage_dir_set = {s["stage_dir"] for s in stages}
    if conditions_path.exists():
        decomposition = json.loads(conditions_path.read_text())["decomposition"]
        for run_id, run in decomposition.items():
            for cond in run.get("conditions", []):
                cond_index.append({
                    "run_id": run_id,
                    "label": cond.get("label"),
                    "detections": cond.get("detections"),
                    "eval_path": cond.get("eval_path"),
                })

        # The register also enumerates verifier stages in a per-run
        # ``verifier_passes`` block whose ``path`` is RELATIVE to the run's
        # output root.  Two shapes exist: {pass_id: {"path": ..., ...}} and
        # {pass_id: modality} where the pass_id itself is the relative path.
        # The run root is recovered from any condition path containing the
        # run_id as a path segment.
        for run_id, run in decomposition.items():
            passes = run.get("verifier_passes") or {}
            if not passes:
                continue
            roots: set[str] = set()
            for cond in run.get("conditions", []):
                for field in ("detections", "eval_path"):
                    value = cond.get(field)
                    if isinstance(value, str) and value.startswith("outputs/"):
                        segs = value.split("/")
                        if run_id in segs:
                            roots.add("/".join(segs[: segs.index(run_id) + 1]))
            for pass_id, entry in passes.items():
                rel = entry.get("path") if isinstance(entry, dict) else pass_id
                if not isinstance(rel, str):
                    continue
                matched: list[str] = []
                for root in roots:
                    cand = f"{root}/{rel}"
                    matched.extend(
                        s for s in stage_dir_set
                        if s == cand or s.startswith(cand + "/")
                    )
                if not matched:
                    # Fall back to suffix matching, but only accept it when it
                    # is unambiguous: a bare rel_path like "verified" otherwise
                    # matches scores of unrelated stages.  Path segments are
                    # normalised ('.' -> '-') because run_ids spell "t0.3" as
                    # "t0-3".
                    norm = run_id.replace(".", "-")
                    suffix = [s for s in stage_dir_set
                              if s == rel or s.endswith("/" + rel)]
                    if len(suffix) > 1:
                        suffix = [s for s in suffix
                                  if norm in [seg.replace(".", "-")
                                              for seg in s.split("/")]]
                    matched = suffix if len(suffix) == 1 else []
                if matched:
                    for stage_dir in sorted(set(matched)):
                        pass_index.append({
                            "run_id": run_id, "pass_id": pass_id,
                            "rel_path": rel, "stage_dir": stage_dir,
                            "modality": (entry.get("modality")
                                         if isinstance(entry, dict) else entry),
                        })
                else:
                    unresolved_passes.append(
                        {"run_id": run_id, "pass_id": pass_id, "rel_path": rel})
    analyses_index: list[dict[str, Any]] = []
    if analyses_path.exists():
        for an in json.loads(analyses_path.read_text())["analyses"]:
            analyses_index.append({
                "analysis_id": an.get("analysis_id"),
                "output_path": an.get("output_path"),
                "conditions_compared": an.get("conditions_compared"),
            })

    def refs_for(stage_dir: str) -> dict[str, Any]:
        prefix = stage_dir + "/"
        hits_cond = [
            {
                "run_id": c["run_id"], "label": c["label"], "field": field,
                "value": c[field],
            }
            for c in cond_index
            for field in ("detections", "eval_path")
            if isinstance(c.get(field), str)
            and (c[field] == stage_dir or c[field].startswith(prefix))
        ]
        hits_an = [
            {"analysis_id": a["analysis_id"], "output_path": a["output_path"]}
            for a in analyses_index
            if isinstance(a.get("output_path"), str)
            and (a["output_path"] == stage_dir or a["output_path"].startswith(prefix))
        ]
        hits_pass = [
            {k: p[k] for k in ("run_id", "pass_id", "rel_path", "modality")}
            for p in pass_index if p["stage_dir"] == stage_dir
        ]
        return {"conditions": hits_cond, "analyses": hits_an,
                "verifier_passes": hits_pass}

    # ------------------------------------------------------------- doc corpus
    md_files: list[Path] = []
    for sub in ("results", "reports", "docs"):
        base = repo / sub
        if base.exists():
            md_files.extend(base.rglob("*.md"))
    corpus: list[tuple[str, int, str]] = []
    for md in md_files:
        try:
            for lineno, line in enumerate(md.read_text(errors="replace").splitlines(), 1):
                corpus.append((md.relative_to(repo).as_posix(), lineno, line))
        except Exception:  # noqa: BLE001
            continue
    print(f"doc corpus: {len(md_files)} markdown files, {len(corpus)} lines",
          file=sys.stderr)

    def doc_hits(stage_dir: str, limit: int = 3) -> dict[str, Any]:
        """Cite hits on the full stage path; fall back to the last two segments."""
        needles = [stage_dir]
        segs = stage_dir.split("/")
        if len(segs) >= 2:
            needles.append("/".join(segs[-2:]))
        for needle in needles:
            hits = []
            for fname, lineno, line in corpus:
                if needle in line:
                    hits.append({"file": fname, "line": lineno,
                                 "text": line.strip()[:200]})
                    if len(hits) >= limit:
                        break
            if hits:
                return {"needle": needle, "hits": hits}
        return {"needle": needles[0], "hits": []}

    def path_last_commit(rel: str) -> dict[str, Any] | None:
        """Last commit for a file, or the newest commit under a directory."""
        direct = commit_map.get(rel)
        if direct:
            return direct
        prefix = rel.rstrip("/") + "/"
        under = [v for k, v in commit_map.items() if k.startswith(prefix)]
        if not under:
            return None
        return max(under, key=lambda v: v["date"])

    # External-evaluation staleness: for every stage whose probabilities were
    # amended by a cleanup pass, check whether the register's evaluation
    # artefacts for conditions drawing on that stage predate the amendment.
    for stage in stages:
        if not stage.get("cleanup_history_present"):
            continue
        prob_date = (stage.get("prob_git_last") or {}).get("date")
        checks = []
        for cond in cond_index:
            det = cond.get("detections")
            if not isinstance(det, str):
                continue
            if not (det == stage["stage_dir"] or det.startswith(stage["stage_dir"] + "/")):
                continue
            ev = cond.get("eval_path")
            ev_commit = path_last_commit(ev) if isinstance(ev, str) else None
            checks.append({
                "run_id": cond["run_id"],
                "label": cond["label"],
                "detections": det,
                "eval_path": ev,
                "eval_last_commit": ev_commit,
                "eval_predates_cleanup": bool(
                    ev_commit and prob_date and ev_commit["date"] < prob_date),
            })
        stage["external_eval_checks"] = checks

    flagged = [s for s in stages
               if s["verdict"] in {"STALE", "UNPARSED", "SWEEP_EXCEEDS_PROBS"}
               or s.get("incomplete")]
    print(f"cross-referencing {len(flagged)} flagged stages ...", file=sys.stderr)
    for stage in stages:
        stage["register"] = refs_for(stage["stage_dir"])
    for stage in flagged:
        stage["doc_citations"] = doc_hits(stage["stage_dir"])
        # Extra history for the flagged ones.
        stage["prob_git_history"] = commit_history(
            repo, stage["stage_dir"] + "/probabilities.json", limit=6
        )

    summary = {
        "total_stages": len(stages),
        "consistent": sum(1 for s in stages if s["verdict"] == "CONSISTENT"),
        "stale": sum(1 for s in stages if s["verdict"] == "STALE"),
        "no_sweep": sum(1 for s in stages if s["verdict"] == "NO SWEEP"),
        "unparsed": sum(1 for s in stages if s["verdict"] == "UNPARSED"),
        "sweep_exceeds_probs": sum(
            1 for s in stages if s["verdict"] == "SWEEP_EXCEEDS_PROBS"),
        "incomplete": sum(1 for s in stages if s.get("incomplete")),
        "cleanup_touched": sum(1 for s in stages if s.get("cleanup_history_present")),
        "cleanup_touched_no_sweep": sum(
            1 for s in stages
            if s.get("cleanup_history_present") and s["verdict"] == "NO SWEEP"),
        "manifest_authoritative": sum(
            1 for s in stages
            if (s.get("manifest") or {}).get("authoritative")),
        "manifest_absent_or_sibling": sum(
            1 for s in stages
            if not (s.get("manifest") or {}).get("authoritative")),
        "skipped_non_verifier": len(skipped),
        "skipped_paths": skipped,
        "register_passes_resolved": len(pass_index),
        "register_passes_unresolved": len(unresolved_passes),
        "register_passes_unresolved_detail": unresolved_passes,
        "stages_linked_to_register": sum(
            1 for s in stages
            if s["register"]["conditions"] or s["register"]["verifier_passes"]),
        "head_commit": subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip(),
    }

    payload = {"summary": summary, "stages": stages}
    (out_dir / "survey.json").write_text(json.dumps(payload, indent=1))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
