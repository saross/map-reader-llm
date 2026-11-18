#!/usr/bin/env python3
"""
Build the tile-join Wave 1 worklist (W1.0, step 4) from the census facts.

Inputs are the two read-only extractions (``census_extract.py`` and
``census_detections.py``), the analyses and conditions registers, and
``docs/paper/``. Output is ``reports/tile-join-wave-1/worklist.json``: one
entry per tracked evaluation file with its frame, construction route,
single or replicated, recorded classification join, paper citation, and a
status with a reason. Standard library only; nothing is scored.

Classification rules (stated here so the worklist can be audited):

* **Construction route**, from how the detection input was built, never
  from ``source_tiles`` alone:

  - ``merged`` if the input's features carry a field only a merging step
    writes (``vote_count``, ``cluster_size``, ``source_tiles``,
    ``origin_tiles``: the consensus, union, and verifier materialisers);
  - ``unmerged`` if the input is raw single-pass detector output (exactly
    the detector's schema: ``confidence``, ``label``, ``method``,
    ``model``, ``source_tile``, ``subtype``), or an Era-1 proposer-verifier
    stage-D ``-single-`` pass's accepted candidates;
  - ``merged`` by name if the input carries none of those fields but its
    path names a merging product (``consensus``, ``union``, ``opmax``,
    ``carried``, ``<k>of<n>``, ``vote``/``vt`` thresholds, ``k<n>_verified``,
    ``wbf``, ``twin``, ``uplift``); the basis says so;
  - ``unknown`` otherwise, including every input that could not be opened.

  For the null-exemplar sensitivity cells, whose detection files are
  gitignored derivatives, the route is read from their recorded sources in
  ``results/null-exemplar-sensitivity-2026-09-13/detections_manifest.json``.
* **Paper-cited** if (1) the file is the ``eval_path`` of a condition in
  the ``conditions_compared`` of a signed row of ``results/run-analyses.json``
  (``signature.status == "signed"``), resolved through
  ``results/run-conditions.json``; or (2) it lies under a directory that
  ``docs/paper/*.md`` names and that exists.
* **Status**, first match wins:

  1. ``historical-only``: under ``archive/`` (D73 (5));
  2. ``known-withheld``: a recorded tile-join refusal
     (``summary.tile_join_withheld`` or a withheld tile block);
  3. ``already-migrated``: records a sheet-specific join (none expected);
  4. ``reproducible-legacy``: the D22 recipe names references and bounds
     that exist, and its detection input opens;
  5. ``unresolved-recipe``: anything else, with the missing piece named.

Usage (zbook, from the branch worktree; the data root is read-only)::

    python3 reports/tile-join-wave-1/scripts/build_worklist.py \\
        --census ~/scratch/wave1/w10/census/census.jsonl \\
        --detections ~/scratch/wave1/w10/census/detections.jsonl \\
        --data-root ~/Code/map-reader-llm \\
        --out reports/tile-join-wave-1/worklist.json

Created: 2026-11-18 (tile-join Wave 1, W1.0)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
MERGE_MARKERS = {"vote_count", "cluster_size", "source_tiles", "origin_tiles"}
RAW_DETECTOR_KEYS = {"confidence", "label", "method", "model", "source_tile", "subtype"}
MERGED_NAME_RE = re.compile(
    r"consensus|union|opmax|carried|\d+of\d+|vote\d|_vt\d|vt\d+_|k\d+_verified|"
    r"wbf|twin|uplift|verified37|best-op|postverif", re.IGNORECASE)
NULL_MANIFEST = ROOT / "results/null-exemplar-sensitivity-2026-09-13/detections_manifest.json"


def signed_eval_paths() -> dict[str, list[str]]:
    """Map each evaluation path to the signed register rows citing it.

    Returns:
        ``{eval_path: [analysis_id, ...]}``.
    """
    analyses = json.loads((ROOT / "results/run-analyses.json").read_text())["analyses"]
    decomposition = json.loads((ROOT / "results/run-conditions.json").read_text())[
        "decomposition"]
    cond = {}
    for run, value in decomposition.items():
        if isinstance(value, dict):
            for c in value.get("conditions", []):
                cond[f"{run}::{c['label']}"] = c.get("eval_path")
    out: dict[str, list[str]] = {}
    for row in analyses:
        if (row.get("signature") or {}).get("status") != "signed":
            continue
        for ref in row.get("conditions_compared") or []:
            path = cond.get(ref)
            if path:
                out.setdefault(path, []).append(row["analysis_id"])
    return out


def paper_dirs() -> list[str]:
    """Existing directories that ``docs/paper/*.md`` names.

    Returns:
        Repository-relative directory paths.
    """
    tokens: set[str] = set()
    for md in (ROOT / "docs/paper").glob("*.md"):
        for m in re.findall(r"(?:results|outputs|archive)/[A-Za-z0-9_./\-]+", md.read_text()):
            tokens.add(m.rstrip(".,);:`").rstrip("/"))
    return sorted(t for t in tokens if (ROOT / t).is_dir())


def file_route(facts: dict[str, Any]) -> tuple[str, str]:
    """Route of one detection file from its recorded facts.

    Args:
        facts: One ``files[]`` entry of ``census_detections.py``.

    Returns:
        ``(route, basis)``.
    """
    if "error" in facts:
        return "unknown", "detection file unreadable"
    keys = set(facts.get("keys") or [])
    name = facts["file"]
    if keys & MERGE_MARKERS:
        return "merged", f"merge field(s) {sorted(keys & MERGE_MARKERS)}"
    if keys == RAW_DETECTOR_KEYS:
        return "unmerged", "raw single-pass detector schema"
    if "era1-pv-stage-d" in name and "-single-" in name:
        return "unmerged", "Era-1 PV stage-D single-pass accepted candidates"
    if MERGED_NAME_RE.search(name):
        return "merged", "no merge field; path names a merging product"
    return "unknown", f"no merge field; keys {sorted(keys)[:8]}"


def combine(routes: list[tuple[str, str]]) -> tuple[str, str]:
    """Combine per-file routes into one evaluation's route.

    Args:
        routes: ``(route, basis)`` for each input file.

    Returns:
        One route; ``mixed`` routes are reported as ``unknown``.
    """
    if not routes:
        return "unknown", "no detection input could be opened"
    kinds = {r for r, _ in routes}
    if len(kinds) == 1:
        return routes[0]
    return "unknown", f"inputs disagree: {sorted(kinds)}"


def main() -> None:
    """Write the worklist and print the tallies."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--detections", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    census = [json.loads(x) for x in args.census.read_text().splitlines()]
    dets = {d["path"]: d for d in
            (json.loads(x) for x in args.detections.read_text().splitlines())}
    file_facts = {f["file"]: f for d in dets.values() for f in d["files"]}
    signed = signed_eval_paths()
    pdirs = paper_dirs()
    manifest = json.loads(NULL_MANIFEST.read_text())["cells"]
    null_sources = {}
    for cell in manifest:
        null_sources[cell["detections_root"]] = [f["source"] for f in cell.get("files", [])]

    entries = []
    for rec in census:
        path = rec["path"]
        data = json.loads((ROOT / path).read_text())
        summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
        buffers = summary.get("buffers") if isinstance(summary.get("buffers"), list) else []
        has_ci = any(isinstance(b, dict) and b.get("f1_ci_lower") is not None for b in buffers)

        # Construction route.
        routes = [file_route(f) for f in dets[path]["files"]]
        if not routes and path.startswith("results/null-exemplar-sensitivity-2026-09-13/"):
            det = rec.get("detections")
            listed = det if isinstance(det, list) else [det] if det else []
            for p in listed:
                root = str(Path(p).parent)
                for src in null_sources.get(root, []):
                    full = str((args.data_root / src))
                    if full in file_facts:
                        r, b = file_route(file_facts[full])
                        routes.append((r, f"via null-exemplar manifest source {src}: {b}"))
                    else:
                        r = "merged" if MERGED_NAME_RE.search(src) else "unknown"
                        routes.append((r, f"via null-exemplar manifest source {src} "
                                          "(name only; source not opened)"))
        route, route_basis = combine(routes)

        n_per_run = rec.get("n_per_run")
        replicated = bool(n_per_run and n_per_run > 1)
        join = rec.get("tile_join_summary") or rec.get("tile_join_cli")

        cited_by = signed.get(path, [])
        cited_dirs = [d for d in pdirs if path.startswith(d + "/")]
        paper_cited = bool(cited_by or cited_dirs)

        gt = rec.get("ground_truth")
        bounds = rec.get("bounds")
        missing = []
        if not rec.get("has_metadata"):
            missing.append("no _metadata")
        if not gt or not (args.data_root / gt).exists():
            missing.append("references not recorded or absent")
        if not bounds or not (args.data_root / bounds).exists():
            missing.append("bounds not recorded or absent")
        if not dets[path]["files"]:
            missing.append("detection input not recorded or absent")

        if path.startswith("archive/"):
            status = "historical-only"
            reason = "under archive/ (D73 (5)): labelled counterpart, never overwritten"
        elif rec.get("has_tile_join_withheld") or rec.get("tile_withheld"):
            status, reason = "known-withheld", "records a tile-join refusal under its recorded join"
        elif join and str(join).startswith("sheet-"):
            status, reason = "already-migrated", f"records join {join}"
        elif not missing:
            status = "reproducible-legacy"
            reason = "D22 recipe complete; inputs present on the data root"
        else:
            status, reason = "unresolved-recipe", "; ".join(missing)

        entries.append({
            "path": path,
            "frame": bounds or None,
            "reference": gt or None,
            "construction_route": route,
            "route_basis": route_basis,
            "replication": "replicated" if replicated else "single",
            "n_per_run": n_per_run,
            "recorded_classification_join": join,
            "recorded_count_table_join": rec.get("count_table_join"),
            "has_tile_classification": rec.get("has_tile_classification"),
            "has_bootstrap_intervals": has_ci,
            "paper_cited": paper_cited,
            "cited_by_signed_rows": cited_by,
            "cited_by_docs_paper_dirs": cited_dirs,
            "status": status,
            "reason": reason,
            "boot_seed": rec.get("boot_seed"),
            "boot_n": rec.get("boot_n"),
            "script_commit": rec.get("script_commit"),
        })

    tallies = {
        "n_files": len(entries),
        "status": Counter(e["status"] for e in entries),
        "status_paper_cited": Counter(e["status"] for e in entries if e["paper_cited"]),
        "route": Counter(e["construction_route"] for e in entries),
        "replication": Counter(e["replication"] for e in entries),
        "join": Counter(str(e["recorded_classification_join"]) for e in entries),
        "paper_cited": sum(e["paper_cited"] for e in entries),
        "paper_cited_by_signed_rows": sum(bool(e["cited_by_signed_rows"]) for e in entries),
        "paper_cited_by_docs_paper": sum(bool(e["cited_by_docs_paper_dirs"]) for e in entries),
        "frame": Counter(str(e["frame"]) for e in entries),
    }
    out = {
        "generated_by": "reports/tile-join-wave-1/scripts/build_worklist.py",
        "rules": __doc__.split("Usage")[0].strip(),
        "paper_dirs": pdirs,
        "tallies": {k: dict(v) if isinstance(v, Counter) else v for k, v in tallies.items()},
        "entries": entries,
    }
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["tallies"], indent=1))


if __name__ == "__main__":
    main()
