#!/usr/bin/env python3
"""Harvest the transmitted signature of every *.meta.json (read-only).

Usage: python harvest.py <repo_root> <out_jsonl>

Walks outputs/ and archive/ under the repository root, parses every
meta, and writes one JSON line per meta with the fields that determine
what reached the model (model, temperature, thinking, system-instruction
hash, include_example_images, example list when images were sent) and the
recorded per-request input-token distribution. Writes nothing in the repo.
"""
from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
from multiprocessing import Pool
from pathlib import Path


def _dig(d, *keys):
    """Return the first non-None value found at any of the dotted keys."""
    for k in keys:
        cur = d
        ok = True
        for part in k.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return None


def _stats(vals):
    vals = [v for v in vals if isinstance(v, (int, float))]
    if not vals:
        return None
    return {
        "n": len(vals),
        "min": min(vals),
        "median": statistics.median(vals),
        "max": max(vals),
        "n_distinct": len(set(vals)),
    }


def harvest(path: str) -> dict:
    """Extract the signature fields of one meta file."""
    rec: dict = {"path": path}
    try:
        with open(path) as f:
            m = json.load(f)
    except Exception as exc:  # noqa: BLE001 - record and move on
        rec["error"] = repr(exc)[:200]
        return rec
    if not isinstance(m, dict):
        rec["error"] = "not a dict"
        return rec
    cfg = m.get("configuration") or {}
    snap = cfg.get("full_config_snapshot") or {}
    env = m.get("environment") or {}
    rec["script"] = env.get("script")
    rec["git_commit"] = env.get("git_commit")
    rec["start"] = _dig(m, "timestamp.start")
    rec["version"] = cfg.get("version") or snap.get("version")
    rec["model"] = cfg.get("model")
    rec["snap_model"] = snap.get("model")
    rec["instruction_file"] = cfg.get("instruction_file") or snap.get("instruction_file")
    rec["sys_hash"] = cfg.get("system_instruction_hash")
    rec["library_hash"] = cfg.get("library_hash")
    rec["temperature"] = cfg.get("temperature")
    rec["temperature_effective"] = cfg.get("temperature_effective")
    rec["snap_temperature"] = snap.get("temperature")
    rec["thinking_level"] = cfg.get("thinking_level")
    rec["snap_thinking_level"] = snap.get("thinking_level")
    rec["tile_size"] = cfg.get("tile_size")
    rec["cfg_include_example_images"] = cfg.get("include_example_images")
    # Raw snapshot value: absent means the runner default (True)
    rec["snap_include_example_images"] = snap.get(
        "include_example_images", "ABSENT"
    ) if snap else "NO_SNAPSHOT"
    rec["example_count"] = cfg.get("example_count")
    rec["ordering_override"] = cfg.get("ordering_override") or snap.get("ordering_override")
    rec["ordering_seed"] = cfg.get("ordering_seed") if cfg.get("ordering_seed") is not None \
        else snap.get("ordering_seed")
    exs = snap.get("examples")
    if exs is None:
        exs = cfg.get("library_manifest")
    if isinstance(exs, list):
        rec["examples"] = [
            (e.get("path"), e.get("label"), e.get("category"))
            if isinstance(e, dict) else (str(e), None, None)
            for e in exs
        ]
    else:
        rec["examples"] = None
    rec["text_only_labels"] = snap.get("text_only_labels")
    rec["crop_label"] = snap.get("crop_label")
    # Other snapshot keys that might carry a manipulation
    rec["snap_keys"] = sorted(k for k in snap.keys() if k != "examples")
    for k in ("calibration_set_id", "pool_source", "library", "library_id",
              "pool", "crop_size", "hypothesis", "description"):
        if k in snap:
            rec["snap_" + k] = snap[k] if not isinstance(snap[k], (dict, list)) \
                else json.dumps(snap[k])[:300]
    # Usage
    us = m.get("usage_stats") or {}
    rec["total_input_tokens"] = us.get("total_input_tokens")
    rec["total_cached_tokens"] = us.get("total_cached_tokens")
    rec["n_responses_with_usage"] = us.get("n_responses_with_usage")
    rec["request_count"] = _dig(us, "by_provider.google_gemini.request_count")
    rec["usage_source"] = us.get("usage_source")
    rec["batch_mode"] = _dig(m, "batch_api.execution_mode")
    rec["chunked"] = bool(m.get("chunked_run"))
    pim = m.get("per_item_metadata") or []
    if isinstance(pim, list) and pim:
        ins, cached, models = [], [], set()
        for it in pim:
            if not isinstance(it, dict):
                continue
            tok = it.get("tokens") or {}
            ins.append(tok.get("input_tokens"))
            c = tok.get("cached_tokens")
            if c is None:
                c = tok.get("cached_content_tokens")
            cached.append(c)
            mu = it.get("model_used") or it.get("model_version")
            if mu:
                models.add(mu)
        rec["pim_n"] = len(pim)
        rec["pim_input"] = _stats(ins)
        rec["pim_cached"] = _stats(cached)
        rec["pim_models"] = sorted(models)
    else:
        rec["pim_n"] = 0
    ex = m.get("execution_stats") or {}
    rec["items_processed"] = ex.get("items_processed")
    rec["pricing_model"] = _dig(m, "cost_estimate.pricing_used.model")
    rec["manifest_path"] = snap.get("manifest_path") or cfg.get("manifest_path")
    rec["n_completed_items"] = len(ex.get("completed_items") or [])
    # A transmitted-library fingerprint: only meaningful when images sent
    inc = rec["snap_include_example_images"]
    sent_images = (inc is True or inc == "ABSENT")
    rec["images_sent_by_config"] = sent_images
    if sent_images and rec["examples"]:
        lib = json.dumps([(p, lab) for p, lab, _ in rec["examples"]])
        rec["sent_library_fp"] = hashlib.sha256(lib.encode()).hexdigest()[:12]
        rec["sent_example_n"] = len(rec["examples"])
    else:
        rec["sent_library_fp"] = "NONE"
        rec["sent_example_n"] = 0
    if rec["examples"]:
        lib = json.dumps([(p, lab) for p, lab, _ in rec["examples"]])
        rec["listed_library_fp"] = hashlib.sha256(lib.encode()).hexdigest()[:12]
        rec["listed_example_n"] = len(rec["examples"])
    else:
        rec["listed_library_fp"] = "NONE"
        rec["listed_example_n"] = 0
    try:
        rec["bytes"] = os.path.getsize(path)
    except OSError:
        pass
    return rec


def main() -> None:
    root = Path(sys.argv[1])
    out = Path(sys.argv[2])
    paths = []
    for top in ("outputs", "archive"):
        for dp, _dn, fn in os.walk(root / top):
            for f in fn:
                if f.endswith(".meta.json"):
                    paths.append(os.path.join(dp, f))
    paths.sort()
    with Pool(min(16, os.cpu_count() or 4)) as pool:
        recs = pool.map(harvest, paths, chunksize=4)
    with open(out, "w") as fo:
        for r in recs:
            r["path"] = os.path.relpath(r["path"], root)
            fo.write(json.dumps(r) + "\n")
    print(len(recs), "metas harvested")


if __name__ == "__main__":
    main()
