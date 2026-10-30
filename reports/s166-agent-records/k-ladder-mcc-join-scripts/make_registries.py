#!/usr/bin/env python3
"""
Write the MCB registries the K-ladder tile-join job runs ``k_ladder_mcb.py`` with.

Part of the S166 K-ladder tile-join job
(``reports/s166-agent-records/k-ladder-mcc-join.md``).

**Why a registry for the ``id`` run too.** At today's head the default
``k_ladder_mcb.py`` registry cannot run: ``label_to_k`` and
``display_names`` read ``phase2/ladders-compat.json``, which the clipped
rebuild of 2026-10-15 (``0fc2d6389``, written after the committed
``mcb/summary.json``) cut to the 7 unclipped ladders, so the 24 rung labels of
the other 6 Phase 2 ladders have no K. The ``id`` registry written here is
the committed registry (``ladder_registry()``: the same analyses, conditions,
bounds, buffers and committed tierings) plus each label's K and each ladder's
family name, read by the module's own ``label_to_k`` and ``display_names``
pointed at the 13-ladder compatibility inventory the committed run read. It
passes through ``--registry``, an option that already exists for this.

**The geometric registries** are the same entries with each ``tiering`` path
moved to the tiering this job wrote under that join
(``tiering_<buffer>m_<join>.json``), so the MCB gate compares each rung's
statistic with the join's own MCC. The clipped registries start from the
committed ``clipped-mcc-2026-10-30/mcb-registry.json`` and are remapped the
same way; the ``id`` run uses that committed file unchanged.

Usage: python make_registries.py <clone_root> <phase2_compat_json> <out_rel> <registry_dir>

``out_rel`` is the job's results directory relative to the clone root.

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

K = "results/k-ladder-2026-09-12"
CLIP = f"{K}/clipped-mcc-2026-10-30"
GEOMETRIC = ("geometric-primary", "geometric-contains")

#: Committed tiering directory prefix -> this job's per-join directory.
REMAP = (
    (f"{CLIP}/mcc-test/tiering/", "clipped-mcc-test/tiering/"),
    (f"{K}/phase2/mcc-test/tiering/", "phase2-mcc-test/tiering/"),
    (f"{K}/mcc-test/tiering/", "mcc-test/tiering/"),
    (f"{K}/tier-e/tiering/", "tier-e/"),
)


def remap(tiering: str, out_rel: str, join: str) -> str:
    """Move a committed tiering path to this job's tiering under a join.

    Args:
        tiering: Repo-relative committed ``tiering_<buffer>m.json``.
        out_rel: The job's results directory, repo-relative.
        join: The geometric join.

    Returns:
        The repo-relative ``tiering_<buffer>m_<join>.json`` this job wrote.

    Raises:
        ValueError: if the path is under no known committed directory.
    """
    for prefix, target in REMAP:
        if tiering.startswith(prefix):
            rest = tiering[len(prefix):]
            stem = rest[: -len(".json")]
            return f"{out_rel}/{join}/{target}{stem}_{join}.json"
    raise ValueError(f"no remap for {tiering}")


def main() -> int:
    """Write the id, geometric and clipped-geometric registries."""
    root, compat, out_rel, reg_dir = (sys.argv[1], sys.argv[2], sys.argv[3],
                                      Path(sys.argv[4]))
    sys.path.insert(0, root)
    import scripts.k_ladder_mcb as mcb  # noqa: PLC0415

    # The committed run's own inventory, so every label has its K and every
    # ladder its family name (see the module docstring).
    mcb.PHASE2_INVENTORY = Path(compat).resolve()
    k_of = mcb.label_to_k()
    names = mcb.display_names()

    base = []
    for entry in mcb.ladder_registry():
        committed = mcb.committed_ranking(entry["tiering"])
        base.append({
            "slug": entry["slug"],
            "analysis_id": entry["analysis_id"],
            "analyses": str(entry["analyses"]),
            "conditions": str(entry["conditions"]) if entry["conditions"] else None,
            "bounds": entry["bounds"],
            "buffer_m": entry["buffer_m"],
            "tiering": str(entry["tiering"]),
            "group": entry["group"],
            "family": names.get(entry["slug"], entry["slug"]),
            "k_by_label": {label: k_of[label] for label in committed},
        })
    clipped = json.loads((Path(root) / CLIP / "mcb-registry.json").read_text())

    reg_dir.mkdir(parents=True, exist_ok=True)
    (reg_dir / "id-registry.json").write_text(json.dumps(base, indent=2) + "\n")
    for join in GEOMETRIC:
        for name, entries in (("registry", base), ("clipped-registry", clipped)):
            moved = [{**e, "tiering": remap(e["tiering"], out_rel, join)}
                     for e in entries]
            (reg_dir / f"{join}-{name}.json").write_text(
                json.dumps(moved, indent=2) + "\n")
    print(f"wrote {len(base)} ladder(s) x id + {len(GEOMETRIC)} joins, "
          f"{len(clipped)} clipped ladder(s) x {len(GEOMETRIC)} joins, to {reg_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
