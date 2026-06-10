#!/usr/bin/env python3
# ============================================================================
# characterise_gs_plateau.py
# ----------------------------------------------------------------------------
# Session 111 ($0): the wide-ranging F1-vs-buffer plateau characterisation
# Shawn requested for choosing the Gold-Standard "practical working
# precision" — where does the F1 gain from loosening spatial precision
# level off, and does the levelling point differ by architecture,
# aggregation, modality, thinking level, or temperature?
#
# DATA: results/conditions-manifest.json — 267/295 conditions carry the
# full canonical 14-buffer curve (5..150 m) with per-buffer F1/P/R + CIs.
# Pure tabulation: no re-scoring, no API.
#
# PLATEAU ONSET (stated criterion): the smallest canonical buffer b such
# that EVERY subsequent step gain is <= 0.005 F1 (the verifier-noise floor
# established in verifier-robustness §2). TAIL DRIFT = F1@last - F1@onset
# (re-rising tails past the onset indicate incidental matches, not
# localisation signal).
#
# SCOPE: GS conditions only (corpus 4-map-gs; the 55-map generalisation
# track uses the corrected/extended GT and gets its own analysis with a
# noise-floor check). Conditions with <10 buffer rows are skipped and
# counted.
#
# Usage:
#   .venv/bin/python scripts/characterise_gs_plateau.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-10 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONDITIONS = BASE_DIR / "results" / "conditions-manifest.json"
RUNS = BASE_DIR / "results" / "runs-manifest.json"
OUT_DIR = BASE_DIR / "results" / "working-precision"
STEP_NOISE = 0.005  # the verifier-robustness §2 noise floor


def derive_tags(cond: dict) -> dict:
    """Best-effort modality/thinking/temperature tags from label + pool names.

    The manifest does not carry these as first-class fields for every
    condition; the naming conventions are consistent enough for grouping.
    Ambiguous cases are tagged 'unknown' rather than guessed.
    """
    text = f"{cond['label']} {cond.get('proposer_pool', '')}".lower()
    modality = ("image" if "image" in text else
                "text" if "text" in text else "unknown")
    thinking = ("high" if "high" in text else
                "medium" if "medium" in text else
                "minimal" if ("min" in text or "minimal" in text) else "unknown")
    m = re.search(r"t-?0[-.]([037])\b|t0\.([037])\b", text)
    temp = f"0.{m.group(1) or m.group(2)}" if m else "unknown"
    return {"modality": modality, "thinking": thinking, "temperature": temp}


def plateau(curve: list[tuple[int, float]]) -> dict:
    """Compute plateau onset, F1 landmarks, and tail drift for one curve."""
    onset = curve[-1][0]
    for i in range(len(curve)):
        gains = [curve[j + 1][1] - curve[j][1] for j in range(i, len(curve) - 1)]
        if all(g <= STEP_NOISE for g in gains):
            onset = curve[i][0]
            break
    by_m = dict(curve)
    f1_onset = by_m[onset]
    return {"onset_m": onset, "f1_20": by_m.get(20), "f1_onset": round(f1_onset, 4),
            "f1_50": by_m.get(50), "f1_last": curve[-1][1],
            "tail_drift": round(curve[-1][1] - f1_onset, 4)}


def main() -> int:
    """Tabulate plateau onsets across the GS condition set."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conds = json.loads(CONDITIONS.read_text())["conditions"]
    runs = {r["run_id"]: r for r in json.loads(RUNS.read_text())["runs"]}

    rows, skipped = [], defaultdict(int)
    for c in conds:
        run = runs.get(c["run_id"], {})
        if run.get("corpus") != "4-map-gs":
            skipped["non-gs-corpus"] += 1
            continue
        pb = c["metrics"].get("per_buffer") or {}
        if len(pb) < 10:
            skipped["lt10-buffers"] += 1
            continue
        curve = sorted(((int(k), v["f1"]) for k, v in pb.items()
                        if v.get("f1") is not None), key=lambda t: t[0])
        if len(curve) < 10:
            skipped["lt10-f1-values"] += 1
            continue
        scope = (c.get("scope_override") or run.get("scope") or {})
        rows.append({
            "condition_id": c["condition_id"],
            "architecture": c.get("architecture"),
            "aggregation": c.get("aggregation"),
            "tile_size": run.get("tile_size_px"),
            "test_set": scope.get("test_set_id"),
            **derive_tags(c),
            **plateau(curve),
        })

    # ---- summary tables ----------------------------------------------------
    def summarise(group_key) -> list[dict]:
        groups = defaultdict(list)
        for r in rows:
            groups[group_key(r)].append(r)
        out = []
        for key, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            onsets = [m["onset_m"] for m in members]
            drifts = [m["tail_drift"] for m in members]
            out.append({"group": key, "n": len(members),
                        "onset_median": statistics.median(onsets),
                        "onset_p90": round(
                            sorted(onsets)[max(0, int(0.9 * len(onsets)) - 1)], 1),
                        "onset_max": max(onsets),
                        "tail_drift_median": round(statistics.median(drifts), 4)})
        return out

    overall = summarise(lambda r: "ALL-GS")
    by_arch = summarise(lambda r: f"{r['architecture']}/{r['aggregation']}")
    by_size = summarise(lambda r: f"{r['tile_size']}px")
    by_mod = summarise(lambda r: r["modality"])
    by_think = summarise(lambda r: r["thinking"])
    by_temp = summarise(lambda r: f"T{r['temperature']}")
    outliers = sorted([r for r in rows if r["onset_m"] >= 50],
                      key=lambda r: -r["onset_m"])

    def table(title, summ):
        lines = [f"\n### {title}\n",
                 "| group | n | onset median | p90 | max | tail drift (med) |",
                 "|---|---:|---:|---:|---:|---:|"]
        lines += [f"| {s['group']} | {s['n']} | {s['onset_median']:g} m "
                  f"| {s['onset_p90']:g} | {s['onset_max']} | {s['tail_drift_median']:+.4f} |"
                  for s in summ]
        return "\n".join(lines)

    md = ["# GS plateau characterisation — F1 vs buffer (working precision)",
          "",
          f"> Generated by `scripts/characterise_gs_plateau.py` from "
          f"`results/conditions-manifest.json`. Plateau onset = smallest "
          f"canonical buffer where every subsequent step gain <= {STEP_NOISE} "
          f"F1; tail drift = F1@last - F1@onset.",
          "",
          f"Conditions analysed: **{len(rows)}** (skipped: {dict(skipped)})",
          table("Overall", overall),
          table("By architecture/aggregation", by_arch),
          table("By tile size", by_size),
          table("By modality", by_mod),
          table("By thinking level", by_think),
          table("By temperature", by_temp),
          "\n### Late-plateau conditions (onset >= 50 m)\n"]
    if outliers:
        md += ["| condition | onset | F1@20 | F1@onset | tail drift |",
               "|---|---:|---:|---:|---:|"]
        md += [f"| {o['condition_id']} | {o['onset_m']} m | {o['f1_20']} "
               f"| {o['f1_onset']} | {o['tail_drift']:+.4f} |" for o in outliers]
    else:
        md.append("None.")

    (OUT_DIR / "gs-plateau-characterisation.json").write_text(json.dumps({
        "criterion": {"step_noise": STEP_NOISE,
                      "definition": "smallest buffer with all later step gains <= noise"},
        "n_analysed": len(rows), "skipped": dict(skipped),
        "summary": {"overall": overall, "by_architecture": by_arch,
                    "by_tile_size": by_size, "by_modality": by_mod,
                    "by_thinking": by_think, "by_temperature": by_temp},
        "conditions": rows}, indent=2) + "\n")
    (OUT_DIR / "gs-plateau-characterisation.md").write_text("\n".join(md) + "\n")

    print(f"analysed {len(rows)} GS conditions (skipped {dict(skipped)})")
    for s in overall + by_arch[:6]:
        print(f"  {s['group']:<28} n={s['n']:<4} onset median {s['onset_median']:g} m "
              f"(p90 {s['onset_p90']:g}, max {s['onset_max']}), "
              f"tail drift {s['tail_drift_median']:+.4f}")
    print(f"late-plateau (>=50 m): {len(outliers)} conditions")
    print(f"Wrote {OUT_DIR.relative_to(BASE_DIR)}/gs-plateau-characterisation.{{json,md}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
