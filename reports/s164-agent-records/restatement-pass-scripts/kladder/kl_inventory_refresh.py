#!/usr/bin/env python3
"""
kl_inventory_refresh.py -- refresh the K-ladder inventory's values, membership fixed.

Purpose:
    S164 restatement pass, K-ladder lane (``reports/s164-agent-records/
    restatement-pass.md`` § 1.4, step 6). ``results/k-ladder-2026-09-12/
    inventory.json`` is the Phase 1 inventory of 2026-09-12; the Phase 1 table
    builder (``scripts/build_k_ladder_tables.py``) reads every rung's metrics
    from it. Re-running ``scripts/build_k_ladder_inventory.py`` now would also
    add every ladder registered since (a structural change the pass does not
    make), so this driver keeps the committed membership exactly and refreshes
    only each listed cell's values, with the builder's own per-entry reader
    (``build_k_ladder_inventory.eval_recipe``) and its own renderer
    (``render_markdown``) and output format.

    For every cell entry of every family it re-reads the entry's own
    ``eval_path`` and replaces ``f1_20``, ``f1_50``, ``mcc`` and
    ``n_detections`` (the stored count is the fallback, as the builder's is
    the manifest's). It REFUSES (exit 3) if a cell's ``eval_path``, ``bounds``
    or ``ground_truth`` would change, since those define the family a cell
    belongs to. Nothing else in the payload is touched.

    ``--prove`` keeps every byte the builder would have written, so a run on
    the data as of the inventory's own commit must reproduce the committed
    ``inventory.json`` and ``inventory-tables.md`` exactly. Without it, the
    refreshed JSON gains one top-level ``values_refreshed`` record (when,
    by what, and how many values moved); ``generated_at_utc`` keeps naming
    the build of the membership.

Usage:
    python kl_inventory_refresh.py --code <repo with scripts/> --data <data root> \
        --inventory <inventory.json> --out-dir <dir> [--prove]

Author: Claude (Opus 5.5) for Shawn Ross, S164 restatement pass, 2026-10-15.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VALUE_KEYS = ("f1_20", "f1_50", "mcc", "n_detections")
IDENTITY_KEYS = ("eval_path", "bounds", "ground_truth")


def main() -> int:
    """Refresh the values of a committed inventory and write both products."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--prove", action="store_true")
    args = ap.parse_args()

    sys.path.insert(0, str(args.code.resolve()))
    import scripts.build_k_ladder_inventory as bki  # noqa: PLC0415

    # The builder reads each evaluation relative to its REPO_ROOT.
    bki.REPO_ROOT = args.data.resolve()
    payload = json.loads(args.inventory.read_text(encoding="utf-8"))
    moved: list[dict] = []
    refusals: list[str] = []
    for fam in payload["families"]:
        # JSON turned the builder's integer rung keys into strings; restore
        # them, in order, so the renderer sorts 1, 3, 5, 10 as the builder did.
        fam["cells"] = {int(k): v for k, v in fam["cells"].items()}
        for k, entries in fam["cells"].items():
            for entry in entries:
                rec = bki.eval_recipe({"eval_path": entry["eval_path"],
                                       "n_detections": entry["n_detections"]})
                for key in IDENTITY_KEYS:
                    if rec[key] != entry[key] and entry["eval_path"]:
                        refusals.append(f"{entry['condition_id']}: {key} "
                                        f"{entry[key]!r} -> {rec[key]!r}")
                for key in VALUE_KEYS:
                    if rec[key] != entry[key]:
                        moved.append({"family": fam["family"], "K": k,
                                      "condition_id": entry["condition_id"], "key": key,
                                      "old": entry[key], "new": rec[key]})
                        entry[key] = rec[key]
    if refusals:
        for line in refusals:
            print("REFUSED (membership would change):", line, file=sys.stderr)
        return 3
    if not args.prove:
        payload["values_refreshed"] = {
            "at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "by": ("kl_inventory_refresh.py (S164 restatement pass, K-ladder lane): "
                   "each listed cell's f1_20, f1_50, mcc and n_detections re-read from "
                   "its eval_path with build_k_ladder_inventory.eval_recipe; membership, "
                   "frames, references and gaps are the committed build's"),
            "n_values_moved": len(moved),
        }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "inventory.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "inventory-tables.md").write_text(
        bki.render_markdown(payload), encoding="utf-8")
    (args.out_dir / "moved.json").write_text(json.dumps(moved, indent=1) + "\n")
    print(f"{len(moved)} value(s) moved; wrote {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
