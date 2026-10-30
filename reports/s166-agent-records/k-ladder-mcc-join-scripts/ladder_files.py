#!/usr/bin/env python3
"""
The K ladders this job tests, and every file their instruments read.

Part of the S166 K-ladder tile-join job
(``reports/s166-agent-records/k-ladder-mcc-join.md``). The instruments
(``scripts/k_ladder_mcc_test.py``, ``scripts/k_ladder_mcb.py`` and the tier E
tiering) resolve each rung through a conditions file to its evaluation, and
read the detections, ground truth and bounds that evaluation's ``cli_args``
(or ``input_files``) name, unless the ladder overrides the bounds. A partial
copy that lacks one of those files has corrupted results here before, so this
module lists every ladder (with its rungs, as ``(K, condition id)`` pairs) and
every path a whole-tree copy must hold, and checks each one exists.

The ladders, 29 in all:

* Phase 1 (8): ``ladders.json``, oracle basis, as ``k_ladder_mcc_test`` selects;
* Phase 2 (13): the compatibility inventory the committed Phase 2 test read
  (``phase2/ladders-compat.json`` at ``326181bcd``; the file at today's head
  holds only the 7 unclipped ladders);
* tier E as evaluated (1): ``tier-e/tiering-input``;
* the D51-clipped ladders (7): ``clipped-mcc-2026-10-30/ladders-clipped.json``.

Usage: python ladder_files.py <repo_root> <phase2_compat_json> [--missing]

Prints one JSON document: ``ladders`` (slug, group, n_rungs, conditions file,
bounds override) and ``files`` (path, exists). With ``--missing`` it prints
only the paths that do not exist, one per line.

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

K = "results/k-ladder-2026-09-12"
CLIP = f"{K}/clipped-mcc-2026-10-30"
BOARD_BOUNDS = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"


def resolve(root: Path, conditions: str, ref: str) -> dict:
    """Resolve one condition id through a conditions file.

    Args:
        root: Repository root.
        conditions: Repo-relative conditions file (register or sidecar).
        ref: ``run::label`` condition id.

    Returns:
        The condition record.
    """
    data = json.loads((root / conditions).read_text())["decomposition"]
    run, label = ref.split("::", 1)
    return next(c for c in data[run]["conditions"] if c["label"] == label)


def cli_of(root: Path, eval_path: str) -> dict:
    """An evaluation's inputs, filled as ``era1_leaderboard_tiering.load_cells`` fills them.

    Args:
        root: Repository root.
        eval_path: Repo-relative ``evaluation.json``.

    Returns:
        The ``cli_args`` dict with ``bounds``, ``ground_truth`` and the
        detection inputs defaulted from ``input_files``.
    """
    meta = json.loads((root / eval_path).read_text())["_metadata"]
    cli = dict(meta.get("cli_args") or {})
    inf = meta.get("input_files") or {}
    cli.setdefault("bounds", inf.get("bounds"))
    cli.setdefault("ground_truth", inf.get("ground_truth"))
    if not (cli.get("detections") or cli.get("detections_dir")):
        fallback = inf.get("detections")
        if isinstance(fallback, str):
            cli["detections_dir"] = fallback
        elif isinstance(fallback, list) and fallback:
            cli["detections"] = fallback
    return cli


def eval_inputs(root: Path, eval_path: str) -> list[str]:
    """Every input an evaluation names, as the tiering harness resolves them.

    Args:
        root: Repository root.
        eval_path: Repo-relative ``evaluation.json``.

    Returns:
        The evaluation itself plus its detections, ground truth and bounds.
    """
    cli = cli_of(root, eval_path)
    out = [eval_path]
    det = cli.get("detections")
    if isinstance(det, str):
        det = [det]
    out += list(det or [])
    if cli.get("detections_dir"):
        out.append(cli["detections_dir"])
    out += [p for p in (cli.get("bounds"), cli.get("ground_truth")) if p]
    return out


def ladder_specs(root: Path, compat: Path) -> list[dict]:
    """Every ladder the job tests, with its rungs and how it is resolved.

    Args:
        root: Repository root (the scripts are imported from it).
        compat: The 13-ladder Phase 2 compatibility inventory.

    Returns:
        One dict per ladder: ``slug``, ``group``, ``conditions`` (repo-relative),
        ``bounds_override`` (repo-relative or None), ``rungs`` (a list of
        ``{"K", "ref"}`` in ascending K).
    """
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from scripts.k_ladder_mcc_test import select_rungs, slug_for  # noqa: PLC0415

    specs: list[dict] = []

    def add(slug: str, group: str, conditions: str, rungs: list[tuple[int, str]],
            bounds: str | None) -> None:
        specs.append({"slug": slug, "group": group, "conditions": conditions,
                      "bounds_override": bounds,
                      "rungs": [{"K": k, "ref": r} for k, r in sorted(rungs)]})

    for lad in json.loads((root / K / "ladders.json").read_text())["ladders"]:
        slug = slug_for(lad)
        rungs = [(int(r["K"]), r["condition_id"]) for r in select_rungs(lad)]
        if slug == "gs-stride-a":
            add(slug, "phase 1", f"{K}/tiering-input/gs-stride-a/run-conditions.json",
                rungs, BOARD_BOUNDS)
        else:
            add(slug, "phase 1", "results/run-conditions.json", rungs, None)
    for lad in json.loads(compat.read_text())["ladders"]:
        rungs = [(int(r["K"]), r["condition_id"]) for r in select_rungs(lad)]
        add(lad["slug"], "phase 2", "results/run-conditions.json", rungs, BOARD_BOUNDS)
    tier_e = json.loads((root / K / "tier-e/ladder.json").read_text())
    k_of = {r["label"]: int(r["n_passes"]) for r in tier_e["rungs"]}
    ana = json.loads((root / K / "tier-e/tiering-input/run-analyses.json").read_text())
    refs = ana["analyses"][0]["conditions_compared"]
    add("tier-e", "tier E", f"{K}/tier-e/tiering-input/run-conditions.json",
        [(k_of[r.split("::", 1)[1]], r) for r in refs], BOARD_BOUNDS)
    for lad in json.loads((root / CLIP / "ladders-clipped.json").read_text())["ladders"]:
        rungs = [(int(r["K"]), r["condition_id"]) for r in select_rungs(lad)]
        add(lad["slug"], "clipped", f"{CLIP}/tiering-input/run-conditions.json",
            rungs, BOARD_BOUNDS)
    return specs


def main() -> int:
    """List the ladders' inputs and check they exist under the root."""
    root = Path(sys.argv[1]).resolve()
    compat = Path(sys.argv[2])
    specs = ladder_specs(root, compat)
    files: set[str] = set()
    for spec in specs:
        files.add(spec["conditions"])
        if spec["bounds_override"]:
            files.add(spec["bounds_override"])
        for rung in spec["rungs"]:
            cond = resolve(root, spec["conditions"], rung["ref"])
            files.update(eval_inputs(root, cond["eval_path"]))

    rows = [{"path": p, "exists": (root / p).exists()} for p in sorted(files)]
    if "--missing" in sys.argv:
        for row in rows:
            if not row["exists"]:
                print(row["path"])
        return 0
    print(json.dumps({
        "ladders": [{k: s[k] for k in ("slug", "group", "conditions",
                                       "bounds_override")}
                    | {"n_rungs": len(s["rungs"]),
                       "K": [r["K"] for r in s["rungs"]]} for s in specs],
        "n_files": len(rows),
        "n_missing": sum(not r["exists"] for r in rows),
        "files": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
