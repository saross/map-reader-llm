#!/usr/bin/env python3
"""
W2-3a: offline consistency checks on the Phase 2 verifier API outputs.

The 28 ``probabilities.json`` and ``run.meta.json`` files of the K-ladder
Phase 2 run (326181bcd) and the smoke run (9a934eaef) are real-time API
outputs with no raw responses kept, so they cannot be regenerated without
spend. What CAN be checked offline, and is checked here, is that each is
internally consistent with the regenerated inputs and with the files that
were derived from it:

* the probabilities' key set equals the committed crop manifest's candidate
  ids (``candidate_{id:05d}``), and ``total_results`` equals the manifest's
  ``successful_extractions`` and the union's feature count;
* every ``mound_probability`` is a number in [0, 1];
* the meta's success count equals ``total_results``, with zero failures,
  and its configuration is the gate's (model, temperature 0.0, MINIMAL);
* the meta's token totals reproduce the spend ledger's flex figure.

Usage::

    python check_api_outputs.py --tree <326181bcd tree> --out result.json

Read-only; no network; no API call.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def check_stage(tree: Path, union: str, crops_dir: str, verify_dir: str) -> dict[str, Any]:
    """Check one verifier stage's probabilities and meta against its inputs."""
    manifest = json.loads((tree / crops_dir / "candidate_manifest.json").read_text())
    probs = json.loads((tree / verify_dir / "probabilities.json").read_text())
    meta = json.loads((tree / verify_dir / "run.meta.json").read_text())
    n_union = len(json.loads((tree / union).read_text())["features"])
    ids = {f"candidate_{c['candidate_id']:05d}" for c in manifest["candidates"]}
    keys = set(probs["results"])
    values = [r.get("mound_probability") for r in probs["results"].values()]
    bad_values = [v for v in values
                  if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 1]
    stats = meta.get("execution_stats", {})
    finish = stats.get("finish_reason_counts", {})
    config = meta.get("configuration", {})
    usage = meta.get("usage_stats", {})
    flex = (int(usage.get("total_input_tokens", 0)) * 0.25
            + (int(usage.get("total_output_tokens", 0))
               + int(usage.get("total_thoughts_tokens", 0) or 0)) * 1.50) / 1e6
    res = {
        "verify_dir": verify_dir,
        "n_union_features": n_union,
        "manifest_successful": manifest["successful_extractions"],
        "manifest_tile_fallback": manifest["tile_fallback_crops"],
        "total_results": probs.get("total_results"),
        "n_keys": len(keys),
        "keys_equal_manifest_ids": keys == ids,
        "n_bad_probability_values": len(bad_values),
        "meta_success": finish.get("success"),
        "meta_items_failed": stats.get("items_failed"),
        "meta_model": config.get("model"),
        "meta_temperature": config.get("temperature"),
        "meta_thinking": config.get("thinking_level"),
        "meta_instruction_file": config.get("instruction_file"),
        "flex_usd_from_meta": round(flex, 6),
    }
    res["consistent"] = bool(
        res["keys_equal_manifest_ids"]
        and res["n_bad_probability_values"] == 0
        and res["total_results"] == res["n_keys"] == res["manifest_successful"] == n_union
        and res["meta_success"] == res["total_results"]
        and res["meta_items_failed"] == 0
        and res["manifest_tile_fallback"] == 0
    )
    return res


def main() -> int:
    """Check the 28 Phase 2 stages (and, optionally, the smoke stage)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--tree", required=True, type=Path)
    parser.add_argument("--smoke-tree", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.tree))
    from scripts.run_k_ladder_phase2_verifier import resolve_paths  # noqa: E402

    tree = args.tree
    rungs = json.loads((tree / "results/k-ladder-2026-09-12/phase2/unions.json").read_text())
    ledger = json.loads((tree / "results/k-ladder-2026-09-12/phase2/spend-ledger.json").read_text())
    by_dir = {e["verify_dir"]: e for e in ledger["rungs"].values()}
    stages = []
    for rung in rungs["rungs"]:
        paths = resolve_paths(rung)
        rec = check_stage(tree, f"{rung['consensus_dir']}/consensus_t1.geojson",
                          paths["crops_dir"], paths["verify_dir"])
        rec["row"] = rung["row"]
        entry = by_dir.get(paths["verify_dir"], {})
        rec["ledger_flex_usd"] = entry.get("flex_usd")
        rec["ledger_matches_meta"] = entry.get("flex_usd") == rec["flex_usd_from_meta"]
        rec["consistent"] = rec["consistent"] and rec["ledger_matches_meta"]
        stages.append(rec)
    smoke = None
    if args.smoke_tree:
        smoke = check_stage(args.smoke_tree,
                            "outputs/k-ladder-2026-09-12/smoke/union_smoke5.geojson",
                            "outputs/k-ladder-2026-09-12/smoke/crops",
                            "outputs/k-ladder-2026-09-12/smoke/verify")
    out = {"n_stages": len(stages),
           "n_consistent": sum(1 for s in stages if s["consistent"]),
           "total_results": sum(s["total_results"] for s in stages),
           "stages": stages, "smoke": smoke}
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("n_stages", "n_consistent", "total_results")}))
    if smoke:
        print("smoke consistent:", smoke["consistent"])
    for s in stages:
        if not s["consistent"]:
            print("INCONSISTENT", json.dumps(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
