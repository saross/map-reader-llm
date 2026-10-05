#!/usr/bin/env python3
"""Build the per-arm transmitted-signature table (read-only on the repo).

Joins results/run-conditions.json (arms) and results/passes-manifest.json
(source metas per pass) with the harvested meta records (metas.jsonl), and
writes arms.json beside this script.
"""
from __future__ import annotations

import collections
import json
import os
import sys
from pathlib import Path

ROOT = Path("/home/shawn/Code/map-reader-llm")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
import derive_condition_modality as dcm  # noqa: E402  (path helpers only)

META = {}
for line in open(HERE / "metas.jsonl"):
    r = json.loads(line)
    META[r["path"]] = r

reg = json.load(open(ROOT / "results/run-registry.json"))["registry"]
RUN_DIR = {x["run_id"]: x["directory_path"] for x in reg}
dec = json.load(open(ROOT / "results/run-conditions.json"))["decomposition"]
passes = json.load(open(ROOT / "results/passes-manifest.json"))["passes"]
PIDX = collections.defaultdict(list)
for p in passes:
    PIDX[(p["run_id"], p["proposer_pool"])].append(p)


def metas_under(d: str) -> list[str]:
    """Meta paths at or under a directory, or a file-prefix form."""
    d = os.path.normpath(d)
    out = [p for p in META if p.startswith(d + "/") or p == d + ".meta.json"]
    return sorted(out)


def is_chunk(p: str) -> bool:
    return "_chunk" in os.path.basename(p)


def eff_temp(r: dict):
    t = r.get("temperature_effective")
    return t if t is not None else r.get("temperature")


def signature(r: dict) -> dict:
    """Transmitted-signature fields of one meta record."""
    is_ver = str(r.get("version") or "").startswith("verify_") or \
        r.get("script") in ("run_pv.py", "5_verify_crops.py")
    if is_ver:
        # lib_verifier.build_reference_items: text_only_labels win; else
        # every listed example is sent as an image (no include flag read).
        tl = r.get("text_only_labels") or []
        if tl:
            sent = "text-labels:" + str(len(tl))
        elif r.get("listed_example_n"):
            sent = "images:" + r["listed_library_fp"] + f"/{r['listed_example_n']}"
        else:
            sent = "none"
    else:
        if r.get("images_sent_by_config") and r.get("listed_example_n"):
            sent = "images:" + r["listed_library_fp"] + f"/{r['listed_example_n']}"
        else:
            sent = "none"
    return {
        "stage": "verifier" if is_ver else "proposer",
        "model": _model_of_record(r),
        "temperature_eff": eff_temp(r),
        "thinking": r.get("thinking_level"),
        "sys_hash": (r.get("sys_hash") or "")[:12] or None,
        "examples_sent": sent,
        "tile_size": r.get("tile_size"),
    }


def _model_of_record(r: dict):
    """What ran: per-item model_version, else pricing model, else config (E57)."""
    pm = r.get("pim_models") or []
    if len(pm) == 1:
        return pm[0]
    if r.get("pricing_model"):
        return r["pricing_model"]
    return r.get("model")


def per_request(r: dict):
    n = r.get("n_responses_with_usage") or r.get("request_count")
    ti = r.get("total_input_tokens")
    if n and ti is not None:
        return round(ti / n, 1)
    return None


arms = []
for run, v in dec.items():
    for kind in ("proposer_pools", "verifier_passes"):
        for key, spec in (v.get(kind) or {}).items():
            src = "passes-manifest"
            paths = []
            for p in PIDX.get((run, key), []):
                paths += (p.get("provenance") or {}).get("source_files") or []
            paths = [p for p in paths if p in META]
            if not paths:
                src = "directory"
                cand_dirs = []
                if kind == "proposer_pools":
                    pp = spec.get("path") if isinstance(spec, dict) else None
                    rp = spec.get("repo_path") if isinstance(spec, dict) else None
                    if rp and pp:
                        cand_dirs.append(f"{rp}/{pp}")
                    base = RUN_DIR.get(run, "")
                    if pp == ".":
                        cand_dirs.append(base)
                    d, _ = dcm.pool_output_dir(run, key, pp)
                    if d and pp != ".":
                        cand_dirs.append(d)
                    for name in ([pp] if pp else []) + [key]:
                        cand_dirs += [f"{base}/{name}", f"{base}/proposer/{name}"]
                else:
                    cand_dirs = dcm.verify_stage_dirs(run, key, spec)
                    pp = spec.get("path") if isinstance(spec, dict) else None
                    rp = spec.get("repo_path") if isinstance(spec, dict) else None
                    base = rp or RUN_DIR.get(run, "")
                    cand_dirs += [f"{base}/{pp or key}"]
                for d in cand_dirs:
                    got = metas_under(d)
                    if kind == "proposer_pools":
                        got = [g for g in got if "/verified" not in g[len(d):]
                               and "/crops" not in g[len(d):]]
                    if got:
                        paths = got
                        src = "directory:" + d
                        break
            recs = [META[p] for p in sorted(set(paths))]
            # prefer non-chunk metas for statistics
            main = [r for r in recs if not is_chunk(r["path"])] or recs
            sigs = collections.Counter(json.dumps(signature(r), sort_keys=True) for r in main)
            versions = sorted({str(r.get("version")) for r in main})
            listed = sorted({f"{r['listed_library_fp']}/{r['listed_example_n']}" for r in main})
            orders = sorted({f"{r.get('ordering_override')}|{r.get('ordering_seed')}" for r in main})
            inc_raw = sorted({str(r.get("snap_include_example_images")) for r in main})
            pim_meds = [r["pim_input"]["median"] for r in main if r.get("pim_input")]
            pim_min = [r["pim_input"]["min"] for r in main if r.get("pim_input")]
            pim_max = [r["pim_input"]["max"] for r in main if r.get("pim_input")]
            pim_cached = [r["pim_cached"]["median"] for r in main if r.get("pim_cached")]
            prq = [per_request(r) for r in main if per_request(r) is not None]
            cached_tot = [r.get("total_cached_tokens") for r in main
                          if r.get("total_cached_tokens")]
            models_used = sorted({m for r in main for m in (r.get("pim_models") or [])})
            arm = {
                "run_id": run,
                "kind": "pool" if kind == "proposer_pools" else "verifier",
                "arm": key,
                "registered_modality": spec if isinstance(spec, str) else spec.get("modality"),
                "meta_source": src,
                "n_metas": len(main),
                "meta_paths": [r["path"] for r in main][:12],
                "config_versions": versions,
                "listed_examples": listed,
                "ordering": orders,
                "snap_include_example_images": inc_raw,
                "signatures": {k: c for k, c in sigs.items()},
                "n_signatures": len(sigs),
                "evidence": ("per-request tokens" if pim_meds else
                             ("aggregate tokens" if prq else "config fields only")),
                "pim_input_median_range": [min(pim_meds), max(pim_meds)] if pim_meds else None,
                "pim_input_min": min(pim_min) if pim_min else None,
                "pim_input_max": max(pim_max) if pim_max else None,
                "pim_cached_median_range": [min(pim_cached), max(pim_cached)]
                if pim_cached else None,
                "mean_input_per_request_range": [min(prq), max(prq)] if prq else None,
                "any_cached_tokens": bool(cached_tot),
                "models_used": models_used,
                "config_models": sorted({str(r.get("model")) for r in main}),
                "manifest_paths": sorted({str(r.get("manifest_path")) for r in main}),
                "items_processed": sorted({r.get("n_completed_items") or r.get("items_processed") or 0 for r in main})[:6],
                "batch": sorted({str(r.get("batch_mode")) for r in main}),
                "git_commits": sorted({(r.get("git_commit") or "")[:9] for r in main}),
                "starts": sorted({(r.get("start") or "")[:10] for r in main}),
            }
            arms.append(arm)

json.dump(arms, open(HERE / "arms.json", "w"), indent=1)
print(len(arms), "arms")
print(collections.Counter(a["evidence"] for a in arms))
print("no metas:", [(a["run_id"], a["arm"]) for a in arms if a["n_metas"] == 0])
