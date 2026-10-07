"""Group the input-drift rows by cause and render the report's per-row tables.

Input-drift provenance trace, 2026-10-07. Read-only: reads ``out/trace.json`` (from
``trace_input_drift.py``), ``out/scored_vintage.json`` (from ``rescore_scored_vintage.py``)
and ``results/run-conditions.json``, and prints Markdown to stdout. No number in the
report's per-row tables is transcribed by hand.

For each row it derives:

- the **scored commit** of each detection file (the vintage ``rescore_scored_vintage.py``
  reproduced against) and the **rewrite commits**: every later commit in the file's
  ``git log --follow`` history, which is what changed the file under the evaluation;
- the **group**, from the rewrite commits (see :data:`GROUPS`);
- the **register status**: a registered condition's source, a waived evaluation
  (``_ignored_evals``), a pre-recovery record (``_pre_recovery_eval_path``), archived, or
  none of these;
- committed and today's feature counts, F1 at 20 m (or the cell's only committed buffer)
  committed and on today's file, and whether the scored vintage reproduces.

Usage::

    python3 summarise_drift.py --repo ~/Code/map-reader-llm --trace out/trace.json \\
        --vintage out/scored_vintage.json > out/tables.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

#: Group label keyed by the first rewrite commit of the row's (first) detection file.
GROUPS = {
    "99ae28ec4": "A. E71 dead-tile rerun rewrote single passes (2026-07-30)",
    "d01ea4412": "A. E71 dead-tile rerun rewrote single passes (2026-07-30)",
    "f6116cba0": "B. E71 downstream consensus rebuilds (2026-07-30 and 2026-09-08)",
    "185681674": "B. E71 downstream consensus rebuilds (2026-07-30 and 2026-09-08)",
    "e01b8617a": "B. E71 downstream consensus rebuilds (2026-07-30 and 2026-09-08)",
    "e7ebc1695": "B. E71 downstream consensus rebuilds (2026-07-30 and 2026-09-08)",
    "c07c57766": "C. E57/Obs 338 Pro-medium run_1 recovery (2026-06-03)",
    "8965d2365": "D. 55-map verified-set recovery rebuilds and reference edits (2026-05)",
    "d7f85978d": "D. 55-map verified-set recovery rebuilds and reference edits (2026-05)",
    "c1ea6df3c": "D. 55-map verified-set recovery rebuilds and reference edits (2026-05)",
    "987534c03": "E. Recovery-fragment-drop fix re-materialised the 3.7 K = 3 set (2026-09-13)",
}

#: Group for rows whose detection file did not change (the reference did).
REFERENCE_ONLY = "D. 55-map verified-set recovery rebuilds and reference edits (2026-05)"


def register_status(row: dict[str, Any], pre_recovery: set[str]) -> str:
    """Describe how the register treats one evaluation path."""
    reg = row["register"]
    if reg["conditions"]:
        ids = ", ".join(f"`{c['condition_id']}`" for c in reg["conditions"])
        return f"registered: {ids}"
    if row["eval"] in pre_recovery:
        return "pre-recovery record (`_pre_recovery_eval_path`)"
    if reg["ignored_in"]:
        return "waived (`_ignored_evals`, " + ", ".join(reg["ignored_in"]) + ")"
    if row["eval"].startswith("archive/"):
        return "archived"
    return "none (not registered, waived or pointed to)"


def headline(metrics: dict[str, Any]) -> tuple[str, Any, Any]:
    """Return (buffer, committed F1, today's F1) at 20 m, else the first scored buffer."""
    pb = metrics["per_buffer"]
    b = "20" if "20" in pb else sorted(pb, key=int)[0]
    c = (pb[b]["committed"] or {}).get("f1")
    return b, c, pb[b]["off"]["f1"]


def main() -> int:
    """Print the grouped per-row tables and a per-group count."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--vintage", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    trace = json.loads(args.trace.read_text())
    vint = {r["eval"]: r for r in json.loads(args.vintage.read_text())["rows"]}
    rc_text = (repo / "results/run-conditions.json").read_text()
    rc = json.loads(rc_text)
    pre_recovery = set()
    for run in rc["decomposition"].values():
        for cond in run.get("conditions") or []:
            if cond.get("_pre_recovery_eval_path"):
                pre_recovery.add(cond["_pre_recovery_eval_path"])

    grouped: dict[str, list[str]] = {}
    for row in trace["rows"]:
        v = vint[row["eval"]]
        f0 = row["files"][0]
        scored = v["inputs"]["detections"][0]["commit"]
        hist = [h["hash"] for h in f0["history"]]
        # A directory pin names a commit that need not touch this file; the file's content
        # at that pin is then its newest earlier version, which carries the committed count.
        content = scored if scored in hist else (f0["matching_commits"] or [None])[0]
        later = hist[: hist.index(content)] if content in hist else hist
        rewrite = list(reversed(later))  # oldest first
        group = GROUPS.get(rewrite[0], "?") if rewrite else REFERENCE_ONLY
        committed = "/".join(str(f["committed_n"]) for f in row["files"])
        today = "/".join(str(f["n_features_disk"]) for f in row["files"])
        b, c_f1, t_f1 = headline(row["metrics"])
        gt = v["inputs"]["ground_truth"]
        ref_note = "" if gt["commit"] == gt["head_commit"] else f"; reference `{gt['commit']}`"
        repro = "yes" if v.get("reproduced") else "F1/P/R yes; MCC no (" + \
            "; ".join(v.get("misses") or []) + ")"
        line = (f"| `{row['eval']}` | {register_status(row, pre_recovery)} | {committed} → "
                f"{today} | `{scored}`{ref_note} | "
                + (", ".join(f"`{h}`" for h in rewrite) or "none (only the reference changed)")
                + f" | {b} m: {c_f1} → {t_f1:.4f} | "
                f"{repro} | {v.get('n_out_of_frame_total')} |")
        grouped.setdefault(group, []).append(line)

    header = ("| Evaluation | Register | Features committed → today | Scored vintage | "
              "Rewritten by | F1 committed → today | Reproduces on scored vintage | "
              "Out of frame (scored vintage) |\n|---|---|---|---|---|---|---|---:|")
    for group in sorted(grouped):
        n = len(grouped[group])
        print(f"\n### {group}: {n} row{'s' if n != 1 else ''}\n")
        print(header)
        for line in sorted(grouped[group]):
            print(line)
    print("\nCounts: " + "; ".join(f"{g[:1]} {len(v)}" for g, v in sorted(grouped.items())))
    print_registered(repo, trace["rows"])
    print_repointed(repo, trace["rows"])
    return 0


def print_repointed(repo: Path, rows: list[dict[str, Any]]) -> None:
    """Check registered rows re-pointed to a recovery re-score against today's file.

    A row of ``results/run-conditions.json`` whose ``eval_path`` lies under
    ``results/recovery-reeval-2026-*`` and whose ``detections`` is a single-file drift
    input is compared with the frames OFF re-score of that file at F1@20, F1@50 and MCC.
    """
    manifest = json.loads((repo / "results/conditions-manifest.json").read_text())
    by_id = {c["condition_id"]: c for c in manifest["conditions"]}
    today: dict[str, tuple[Any, Any, Any]] = {}
    for row in rows:
        if len(row["files"]) == 1 and "20" in row["metrics"]["per_buffer"]:
            pb = row["metrics"]["per_buffer"]
            today.setdefault(row["files"][0]["path"], (
                pb["20"]["off"]["f1"], pb["50"]["off"]["f1"], row["metrics"]["off_mcc"]))
    rc = json.loads((repo / "results/run-conditions.json").read_text())
    print("\n| Re-pointed registered condition | F1@20 registered / today | "
          "F1@50 registered / today | MCC registered / today | Equal (±1e-4) |\n"
          "|---|---|---|---|---|")
    n_checked = n_equal = 0
    for run_id, run in rc["decomposition"].items():
        for cond in run.get("conditions") or []:
            det = cond.get("detections")
            if "recovery-reeval-2026" not in (cond.get("eval_path") or "") or det not in today:
                continue
            reg = by_id[f"{run_id}::{cond['label']}"]["metrics"]
            r20 = reg["per_buffer"]["20"]["f1"]
            r50 = reg["per_buffer"]["50"]["f1"]
            rmcc = (reg.get("tile_classification") or {}).get("mcc")
            t20, t50, tmcc = today[det]
            pairs = [(r20, t20), (r50, t50)] + ([(rmcc, tmcc)] if rmcc is not None else [])
            equal = all(t is not None and abs(r - t) <= 1e-4 + 1e-9 for r, t in pairs)
            n_checked += 1
            n_equal += equal
            print(f"| `{run_id}::{cond['label']}` | {r20:.4f} / {t20:.4f} | {r50:.4f} / "
                  f"{t50:.4f} | {rmcc} / {tmcc if tmcc is None else round(tmcc, 4)} | "
                  f"{'yes' if equal else 'NO'} |")
    print(f"\nRe-pointed rows checked: {n_checked}; equal to today's file: {n_equal}")


def print_registered(repo: Path, rows: list[dict[str, Any]]) -> None:
    """Print, per registered drift row, its value, today's file value and its twin's value.

    The twin is the ``<condition>-post-e71`` row of ``results/conditions-manifest.json``
    (PI ruling 3a). "Today" is the frames OFF re-score of the current file. Δ is today
    minus the registered (pinned) value.
    """
    manifest = json.loads((repo / "results/conditions-manifest.json").read_text())
    by_id = {c["condition_id"]: c for c in manifest["conditions"]}
    print("\n| Registered condition | Metric | Registered (pinned) | Today's file (OFF) | "
          "Δ | `-post-e71` twin | Twin equals today (±1e-4) |\n|---|---|---:|---:|---:|---:|---|")
    for row in rows:
        for cond in row["register"]["conditions"]:
            twin = by_id.get(cond["condition_id"] + "-post-e71")
            pb = row["metrics"]["per_buffer"]
            cells = [("F1@20", cond["f1_20"], pb["20"]["off"]["f1"],
                      twin and twin["metrics"]["per_buffer"]["20"]["f1"]),
                     ("F1@50", cond["f1_50"], pb["50"]["off"]["f1"],
                      twin and twin["metrics"]["per_buffer"]["50"]["f1"]),
                     ("MCC", cond["mcc"], row["metrics"]["off_mcc"],
                      twin and twin["metrics"]["tile_classification"]["mcc"])]
            for name, reg, today, tw in cells:
                same = "yes" if tw is not None and abs(tw - today) <= 1e-4 + 1e-9 else "NO"
                print(f"| `{cond['condition_id']}` | {name} | {reg:.4f} | {today:.4f} | "
                      f"{today - reg:+.4f} | {tw:.4f} | {same} |")


if __name__ == "__main__":
    raise SystemExit(main())
