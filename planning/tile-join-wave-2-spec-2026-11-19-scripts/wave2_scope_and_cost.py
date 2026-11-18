#!/usr/bin/env python3
"""
Scope and cost projection for the tile-join Wave 2 specification.

Reads the Wave 1 W1.0 worklist and smoke-replay timings from a pinned git
revision, opens every listed ``evaluation.json`` in the working tree (to
count its passes and buffers), and prints:

1. the proposed Wave 2 disposition of every worklist entry, cross-tabulated
   by corpus (gold standard or 55-map), paper citation, and writer;
2. the frames and reference files each corpus uses, with tile counts read
   from the frame files themselves;
3. a cost projection in CPU-hours and wall-clock, per class of file and in
   aggregate, built only from the measured legacy-replay timings.

Nothing is scored, imported from the project, or written except the text
report on standard output. Standard library only, so it may run on
amd-tower (whose virtual environment is not the reference environment).

Usage (from the repository root)::

    python3 planning/tile-join-wave-2-spec-2026-11-19-scripts/wave2_scope_and_cost.py \\
        --rev 89cab15ee > \\
        planning/tile-join-wave-2-spec-2026-11-19-scripts/wave2_scope_and_cost.txt

Created: 2026-11-19 (tile-join Wave 2 specification draft, S169)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import subprocess
from pathlib import Path
from typing import Any

#: Where W1.0 committed its worklist and replay record, on its own branch.
WORKLIST_PATH = "reports/tile-join-wave-1/worklist.json"
SMOKE_PATH = "reports/tile-join-wave-1/scripts/out/smoke_replay.json"

#: The repository prefix one recorded frame carries as an absolute path
#: (W1.0 open question 7); stripped so the frame file can be opened.
ABSOLUTE_PREFIX = "/home/shawn/Code/map-reader-llm/"

#: zbook's resources (operating brief): 32 cores with 2 kept free, 31 GB.
ZBOOK_CORES_USABLE = 30
ZBOOK_RAM_GB = 31.0
#: Memory left free for the operating system, the driver itself, and the
#: new joins' unmeasured extra memory (W1.5 re-measures peak RSS).
RAM_HEADROOM_GB = 6.0
#: The heavy-job worker cap of the Wave 1 operating brief.
WORKER_CAP_BRIEF = 14

def git_show_json(rev: str, path: str) -> Any:
    """Return the parsed JSON of ``path`` at git revision ``rev``.

    Args:
        rev: Any git revision (commit hash or remote branch).
        path: Repository-relative path.

    Returns:
        The parsed JSON value.
    """
    blob = subprocess.run(
        ["git", "show", f"{rev}:{path}"],
        check=True, capture_output=True,
    ).stdout
    return json.loads(blob)


def frame_tiles(frame: str | None, cache: dict[str, int | None]) -> int | None:
    """Count the tiles (features) of a frame file, or ``None`` if absent.

    Args:
        frame: The recorded frame path (may be absolute; see
            ``ABSOLUTE_PREFIX``), or ``None`` when no frame is recorded.
        cache: Memo of earlier counts, keyed by the recorded path.

    Returns:
        The feature count, or ``None`` when no frame is recorded or the
        file is not in the working tree.
    """
    if frame is None:
        return None
    if frame not in cache:
        path = Path(frame.removeprefix(ABSOLUTE_PREFIX))
        if path.is_file():
            cache[frame] = len(json.loads(path.read_text())["features"])
        else:
            cache[frame] = None
    return cache[frame]


def shape_of(path: str) -> tuple[int, int, str | None]:
    """Return (passes, buffers, writer) of one committed evaluation file.

    Args:
        path: Repository-relative path of the evaluation file.

    Returns:
        The number of passes (``len(per_run)``, or 1 for a single-run
        file), the number of buffer rows in ``summary.buffers`` (0 when
        absent), and ``_metadata.script_path`` (``None`` when absent).
    """
    doc = json.loads(Path(path).read_text())
    summary = doc.get("summary") or {}
    passes = len(doc.get("per_run") or []) or 1
    buffers = len(summary.get("buffers") or []) if isinstance(summary, dict) else 0
    writer = (doc.get("_metadata") or {}).get("script_path")
    return passes, buffers, writer


def disposition(entry: dict[str, Any]) -> str:
    """Map one W1.0 worklist entry to its proposed Wave 2 disposition.

    The rules are the specification's § 3.1 ("Disposition of every worklist
    entry"), restated here so the counts can be audited against them.

    Args:
        entry: One ``entries[]`` item of the W1.0 worklist.

    Returns:
        A short disposition label.
    """
    status = entry["status"]
    path = entry["path"]
    # A recorded refusal withheld the intervals (and the tile block), so a
    # known-withheld file is tile-bearing even when it carries neither.
    bearing = (entry["has_tile_classification"] or entry["has_bootstrap_intervals"]
               or status == "known-withheld")
    if status == "historical-only":
        return "counterpart" if bearing else "skip:not-tile-bearing"
    if status == "unresolved-recipe":
        if path.startswith("results/null-exemplar-sensitivity-2026-09-13/"):
            return "regenerate-then-rescore"
        if path.startswith(("results/verifier-t-pilot/", "results/retest/")):
            return "skip:no-recipe"
        return "hold:input-absent"
    if status == "known-withheld":
        return "rescore-in-place"
    if status == "reproducible-legacy":
        return "rescore-in-place" if bearing else "skip:not-tile-bearing"
    return f"unexpected:{status}"


def per_file_legacy_cpu(passes: int, buffers: int, corpus: str, tiles: int | None,
                        withheld: bool, rates: dict[str, float]) -> tuple[float, float]:
    """Project one file's legacy-replay CPU seconds and its compute leg.

    Args:
        passes: Passes in the file.
        buffers: Buffer rows in the file.
        corpus: ``"gs"`` or ``"55map"``.
        tiles: Frame tile count, for the unmeasured 256 px frame.
        withheld: Whether the file records a tile-join refusal (its legacy
            replay stops at the refusal, so it costs the measured refusal
            time rather than a full replay).
        rates: Measured rates from :func:`measured_rates`.

    Returns:
        (legacy-replay CPU seconds, new-rules compute CPU seconds), the
        second under the stated assumption that it equals a full replay.
    """
    nb = max(buffers, 1)
    if corpus == "55map" or (tiles is not None and tiles > 1000):
        # 55-map rate, and (conservatively) the unmeasured 1,032-tile 256 px
        # frame. Files with fewer than 14 buffers are charged the full
        # 14-buffer measurement: no 55-map single-buffer floor was measured.
        full = passes * max(nb, 14) * rates["r55_per_pass_buffer"]
    else:
        full = passes * max(nb * rates["rgs_per_pass_buffer"], rates["gs_floor_per_pass"])
    replay = passes * rates["refusal_per_pass"] if withheld else full
    return replay, full


def round_trip(path: str) -> str:
    """Classify whether a file is the scorer's own serialisation of itself.

    ``write_outputs`` writes ``json.dump(output, f, indent=2)`` with no
    trailing newline, so a re-emission that re-serialises the parsed
    document reproduces the committed bytes only if the file was written
    that way.

    Args:
        path: Repository-relative path of the evaluation file.

    Returns:
        ``"exact"``, ``"exact+newline"`` (identical apart from one trailing
        newline), or ``"differs"``.
    """
    text = Path(path).read_text(encoding="utf-8")
    again = json.dumps(json.loads(text), indent=2)
    if text == again:
        return "exact"
    if text == again + "\n":
        return "exact+newline"
    return "differs"


def measured_rates(smoke: dict[str, Any]) -> dict[str, float]:
    """Derive the cost rates from the W1.0 smoke replays.

    Args:
        smoke: The parsed ``smoke_replay.json``.

    Returns:
        The rates (CPU seconds), each documented in the report.
    """
    cells = {c["cell"]: c for c in smoke["cells"]}

    def per_pb(cell: str, passes: int) -> float:
        c = cells[cell]
        return c["cpu_s"] / (passes * len(c["recipe"]["buffers"]))

    return {
        # Gold-standard frames: the largest per-(pass x buffer) cost among
        # the full-recipe GS cells 1, 3, and 5 (cell 3, the 512 px frame).
        "rgs_per_pass_buffer": max(per_pb("1", 1), per_pb("3", 1), per_pb("5", 3)),
        # One-buffer floor per pass: cell 4 (grid, 20 m only).
        "gs_floor_per_pass": cells["4"]["cpu_s"],
        # 55-map: cell 2, 8,541 tiles, 14 buffers.
        "r55_per_pass_buffer": per_pb("2", 1),
        # A legacy replay that ends in its recorded refusal: the slowest of
        # the three withheld cells 6-8.
        "refusal_per_pass": max(cells[k]["cpu_s"] for k in ("6", "7", "8")),
        "rss_gs_mb": max(cells[k]["max_rss_mb"] for k in ("1", "3", "4", "5", "6", "7", "8")),
        "rss_55_mb": cells["2"]["max_rss_mb"],
    }


def main() -> int:
    """Print the scope tables and the cost projection.

    Returns:
        Process exit code (0).
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--rev", required=True,
                        help="Git revision holding the W1.0 worklist (e.g. 89cab15ee).")
    args = parser.parse_args()

    worklist = git_show_json(args.rev, WORKLIST_PATH)
    smoke = git_show_json(args.rev, SMOKE_PATH)
    rates = measured_rates(smoke)
    entries = worklist["entries"]
    tiles_cache: dict[str, int | None] = {}

    rows = []
    for e in entries:
        passes, buffers, writer = shape_of(e["path"])
        frame = e["frame"]
        corpus = "none" if frame is None else ("55map" if "55maps" in frame else "gs")
        tiles = frame_tiles(frame, tiles_cache)
        disp = disposition(e)
        replay, full = per_file_legacy_cpu(
            passes, buffers, corpus, tiles, e["status"] == "known-withheld", rates,
        )
        rows.append({**e, "passes": passes, "buffers": buffers, "writer": writer,
                     "corpus": corpus, "tiles": tiles, "disp": disp,
                     "replay_s": replay, "full_s": full})

    print(f"W1.0 worklist at {args.rev}: {len(entries)} entries")
    print()
    print("== 1. Proposed disposition x corpus x paper-cited ==")
    tab = collections.Counter((r["disp"], r["corpus"], r["paper_cited"]) for r in rows)
    for key in sorted(tab, key=str):
        print(f"  {tab[key]:5d}  {key}")
    print("  totals by disposition:",
          dict(collections.Counter(r["disp"] for r in rows)))
    print("  totals by corpus:", dict(collections.Counter(r["corpus"] for r in rows)))
    print()
    print("== 1b. Tile block / intervals, by disposition ==")
    tab = collections.Counter(
        (r["disp"], r["has_tile_classification"], r["has_bootstrap_intervals"]) for r in rows)
    for key in sorted(tab, key=str):
        print(f"  {tab[key]:5d}  {key}  (disp, tile block, intervals)")
    print()
    print("== 1c. Writer (_metadata.script_path), by disposition ==")
    tab = collections.Counter((r["writer"], r["disp"]) for r in rows)
    for key in sorted(tab, key=str):
        print(f"  {tab[key]:5d}  {key}")
    print("  files not written by scripts/evaluate_detections.py, by directory:")
    tab = collections.Counter(
        ("/".join(r["path"].split("/")[:2]), r["writer"], r["disp"]) for r in rows
        if r["writer"] != "scripts/evaluate_detections.py")
    for key in sorted(tab, key=str):
        print(f"    {tab[key]:4d}  {key}")
    print()
    print("== 1d. hold:input-absent and skip:no-recipe, by directory ==")
    tab = collections.Counter(
        ("/".join(r["path"].split("/")[:2]), r["disp"]) for r in rows
        if r["disp"] in ("hold:input-absent", "skip:no-recipe"))
    for key in sorted(tab, key=str):
        print(f"  {tab[key]:5d}  {key}")
    print()
    print("== 2. Frames (tiles) and references, rescored or counterparted files ==")
    active = [r for r in rows if r["disp"] in
              ("rescore-in-place", "counterpart", "regenerate-then-rescore")]
    tab = collections.Counter((r["corpus"], r["frame"], r["tiles"]) for r in active)
    for key in sorted(tab, key=str):
        print(f"  {tab[key]:5d}  {key}")
    print("  references:")
    tab = collections.Counter((r["corpus"], r["reference"], r["paper_cited"]) for r in active)
    for key in sorted(tab, key=str):
        print(f"    {tab[key]:5d}  {key}  (corpus, reference, paper-cited)")
    print("  absolute frame or reference paths:")
    for r in rows:
        if (r["frame"] or "").startswith("/") or (r["reference"] or "").startswith("/"):
            print(f"    {r['path']} [{r['disp']}] frame={r['frame']} ref={r['reference']}")
    print()
    print("== 3. Cost projection (CPU seconds are legacy-replay measurements) ==")
    for k, v in rates.items():
        print(f"  {k} = {v:.4f}")
    print()
    header = (f"  {'class (corpus, tiles, passes, buffers)':44s} {'files':>5s} "
              f"{'replay CPU-h':>12s} {'compute CPU-h':>13s} {'x2 CPU-h':>9s}")
    print(header)
    classes: dict[tuple, list[dict]] = collections.defaultdict(list)
    for r in active:
        classes[(r["corpus"], r["tiles"], r["passes"], r["buffers"])].append(r)
    agg = collections.defaultdict(float)
    for key in sorted(classes, key=str):
        group = classes[key]
        rep = sum(r["replay_s"] for r in group) / 3600
        comp = sum(r["full_s"] for r in group) / 3600
        agg[(key[0], "replay")] += rep
        agg[(key[0], "compute")] += comp
        print(f"  {str(key):44s} {len(group):5d} {rep:12.3f} {comp:13.3f} {rep + comp:9.3f}")
    print()
    rss_gs, rss_55 = rates["rss_gs_mb"] / 1024, rates["rss_55_mb"] / 1024
    w55 = min(WORKER_CAP_BRIEF, math.floor((ZBOOK_RAM_GB - RAM_HEADROOM_GB) / rss_55))
    wgs_brief = WORKER_CAP_BRIEF
    wgs_cores = min(ZBOOK_CORES_USABLE, math.floor((ZBOOK_RAM_GB - RAM_HEADROOM_GB) / rss_gs))
    print("  by corpus and paper citation (replay + compute, CPU-h):")
    for corpus in ("gs", "55map"):
        for cited in (True, False):
            group = [r for r in active if r["corpus"] == corpus and r["paper_cited"] == cited]
            total = sum(r["replay_s"] + r["full_s"] for r in group) / 3600
            print(f"    {corpus:6s} paper-cited={cited!s:5s} {len(group):5d} files {total:8.2f}")
    print("  non-scorer writers among active files (corpus, writer, paper-cited):")
    tab = collections.Counter((r["corpus"], r["writer"], r["paper_cited"]) for r in active
                              if r["writer"] != "scripts/evaluate_detections.py")
    for key in sorted(tab, key=str):
        print(f"    {tab[key]:4d}  {key}")
    print(f"  workers: 55-map {w55} (memory: ({ZBOOK_RAM_GB} - {RAM_HEADROOM_GB}) GB / "
          f"{rss_55:.3f} GB, capped at {WORKER_CAP_BRIEF}); GS {wgs_brief} (brief cap), "
          f"or {wgs_cores} (cores, memory {wgs_cores * rss_gs:.1f} GB)")
    for corpus, workers in (("gs", wgs_brief), ("gs", wgs_cores), ("55map", w55)):
        rep, comp = agg[(corpus, "replay")], agg[(corpus, "compute")]
        for mult_name, total in (("replay+compute", rep + comp),
                                 ("+ full idempotence rerun", rep + 2 * comp)):
            print(f"  {corpus:6s} {mult_name:26s} {total:8.2f} CPU-h; "
                  f"{workers:2d} workers -> {total / workers:6.2f} h wall")
    print()
    print("== 4. Re-serialisation: committed bytes == json.dumps(parsed, indent=2)? ==")
    rt = {r["path"]: round_trip(r["path"]) for r in rows}
    print("  ", dict(collections.Counter(rt.values())))
    for r in rows:
        if rt[r["path"]] == "differs":
            print(f"    differs: {r['path']} [{r['disp']}] writer={r['writer']}")
    tab = collections.Counter((rt[r["path"]], r["disp"]) for r in rows
                              if rt[r["path"]] == "exact+newline")
    for key in sorted(tab, key=str):
        print(f"    {tab[key]:4d}  {key}")
    print()
    print("== 5. Schema strata (replay risk): metadata_version, interval method, coverage ==")
    smoke_paths = {c["committed"] for c in smoke["cells"]}
    strata: collections.Counter = collections.Counter()
    for r in rows:
        doc = json.loads(Path(r["path"]).read_text())
        meta = doc.get("_metadata") or {}
        buffers = (doc.get("summary") or {}).get("buffers") or []
        r["mv"] = meta.get("metadata_version")
        r["method"] = (meta.get("bootstrap") or {}).get("method")
        r["has_cov"] = bool(buffers) and "coverage" in buffers[0]
        strata[(r["disp"], r["mv"], r["method"], r["has_cov"])] += 1
    for key in sorted(strata, key=str):
        print(f"  {strata[key]:5d}  {key}  (disp, metadata_version, method, coverage block)")
    print("  smoke cells (the strata W1.0's determinism replays exercised):")
    for r in rows:
        if r["path"] in smoke_paths:
            print(f"    {r['mv']} {r['method']} cov={r['has_cov']} {r['path']}")
    tab = collections.Counter((r["mv"], r["paper_cited"]) for r in active)
    print("  active files by metadata_version and paper citation:")
    for key in sorted(tab, key=str):
        print(f"    {tab[key]:5d}  {key}")
    longest = max(active, key=lambda r: r["replay_s"] + r["full_s"])
    print(f"  longest single file (replay + compute): {longest['path']} "
          f"{(longest['replay_s'] + longest['full_s']) / 60:.1f} min CPU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
