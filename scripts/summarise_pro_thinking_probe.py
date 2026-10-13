#!/usr/bin/env python3
"""Summarise delivered thinking per arm of the Pro thinking probe.

The probe (``scripts/run_pro_thinking_probe.sh``, 2026-10-12) asks
Gemini 3.1 Pro for thinking level HIGH on 50 gold-standard tiles per arm,
varying only temperature, to test whether temperature switches Pro's
thinking on or off (ruling D61 (4) in ``planning/pi-decisions-2026-09-20.md``).
This script reads each arm's ``*.meta.json`` (written by
``scripts/4_detect_mounds_batch.py`` with ``per_item_metadata``) and reports,
per arm, the distribution of thought tokens per request, output tokens,
latency, the model version that answered, and finish reasons. For the June
comparison it reads the same fields from the genuine-Pro HIGH passes of
2026-06-03 (``outputs/h11/n1-pro-rerun-384/pro-{text,image}-high-t0``),
restricted to the probe's 50 tiles.

Usage::

    python scripts/summarise_pro_thinking_probe.py \\
        --probe-dir outputs/pro-thinking-probe-2026-10-12 \\
        --out outputs/pro-thinking-probe-2026-10-12/summary.json

Example output (one line per arm, then the June baselines)::

    text-t0.0   n=50  thoughts median=0 ... zero=50/50  model=gemini-3.1-pro-preview
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

JUNE_DIR = Path("outputs/h11/n1-pro-rerun-384")
JUNE_ARMS = {"june-text-high-t0": "pro-text-high-t0", "june-image-high-t0": "pro-image-high-t0"}


def _items(meta_path: Path) -> list[dict]:
    """Return the per-request records of one meta file (empty if absent)."""
    meta = json.loads(meta_path.read_text())
    return meta.get("per_item_metadata") or []


def _summarise(items: list[dict]) -> dict:
    """Distribution of thought tokens and related fields over requests.

    Args:
        items: Per-request records as written by ``lib_llm_metadata``.

    Returns:
        A dict of counts, quantiles, and the set of model versions seen.
    """
    thoughts = [int((r.get("tokens") or {}).get("thoughts_tokens") or 0) for r in items]
    output = [int((r.get("tokens") or {}).get("output_tokens") or 0) for r in items]
    latency = [int(r.get("latency_ms") or 0) for r in items]
    if not items:
        return {"n": 0}
    q = statistics.quantiles(thoughts, n=4) if len(thoughts) > 1 else [thoughts[0]] * 3
    return {
        "n": len(items),
        "thoughts_min": min(thoughts),
        "thoughts_q1": q[0],
        "thoughts_median": statistics.median(thoughts),
        "thoughts_q3": q[2],
        "thoughts_max": max(thoughts),
        "thoughts_mean": round(statistics.fmean(thoughts), 1),
        "n_zero_thoughts": sum(t == 0 for t in thoughts),
        "thoughts_total": sum(thoughts),
        "output_median": statistics.median(output),
        "output_total": sum(output),
        "latency_ms_median": statistics.median(latency),
        "model_versions": sorted({str(r.get("model_version")) for r in items}),
        "finish_reasons": sorted({str(r.get("finish_reason")) for r in items}),
        "n_parse_fail": sum(not r.get("parse_success", True) for r in items),
    }


def main() -> None:
    """Summarise every probe arm and the June baselines on the same tiles."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--probe-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    tiles = set(json.loads((args.probe_dir / "tiles-50-seed42.json").read_text()))
    result: dict[str, dict] = {}
    for arm_dir in sorted(p for p in args.probe_dir.iterdir() if p.is_dir()):
        metas = sorted(arm_dir.glob("*.meta.json"))
        items = [r for m in metas for r in _items(m)]
        result[arm_dir.name] = _summarise(items)
    for label, pool in JUNE_ARMS.items():
        items = [r for m in sorted((JUNE_DIR / pool).glob("run_*/*.meta.json"))
                 for r in _items(m) if r.get("item_id") in tiles]
        result[label] = _summarise(items)

    for arm, s in result.items():
        if not s.get("n"):
            print(f"{arm:20s} n=0")
            continue
        print(f"{arm:20s} n={s['n']:3d} thoughts median={s['thoughts_median']:>7} "
              f"IQR=[{s['thoughts_q1']}, {s['thoughts_q3']}] max={s['thoughts_max']:>6} "
              f"zero={s['n_zero_thoughts']}/{s['n']} output median={s['output_median']} "
              f"latency median={s['latency_ms_median'] / 1000:.1f}s "
              f"model={','.join(s['model_versions'])}")
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")


if __name__ == "__main__":
    main()
