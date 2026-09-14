#!/usr/bin/env python3
"""Before → after for every modality-GROUPED statistic the 2026-09-14 audit moved.

The audit (`scripts/derive_condition_modality.py`,
`reports/modality-track-audit-2026-09-14.md`) found eight registered
conditions and one proposer pool whose recorded modality disagreed with the
configuration their proposer transmitted. Modality is a preregistered factor
(H1), so a wrong label can reach a modality-grouped statistic. This script
recomputes every such statistic with corrected labels and tabulates the
movement, so that "nothing registered changed" is a measurement rather than an
assertion.

US$0 — pure tabulation from committed evaluations. No cell is re-scored: the
cells' metrics are right, only their group membership moves.

Three statistics are in scope:

1. **``results/working-precision/gs-plateau-characterisation.json``**
   ``summary.by_modality`` — plateau onset medians, p90, max and tail drift per
   modality over the Gold-Standard condition set. Three conditions move from
   the image group to the text group. The recomputed tabulation is produced by
   ``scripts/characterise_gs_plateau.py --out-dir <recomputed>``.
2. **``results/tile-size-sweep/tile_size_sweep.json``**
   ``best_per_size.by_arch_modality`` — the best FLASH cell per
   (tile size × architecture × modality). ``retest-phase2e::canonical-last``
   moves from the text leg to the image leg at 512 px, so BOTH legs can change
   (the text leg loses its winner; the image leg gains a candidate). The
   recomputed sweep is produced by
   ``scripts/tile_size_sweep.py --output-dir <recomputed>``.
3. **The paper's § R2 metric-trade-off claim** — "text-only cells reach
   F1 ≈ 0.60 with essentially no tile-level discrimination while image-bearing
   cells trade F1 for markedly better discrimination (MCC 0.094-0.291 across
   the 17 computable image-bearing cells)", with the changelog's "undefined on
   8 of the 14 phase-2 text-only cells; 0.0665 on the other 6". This script
   recomputes both groups' membership and MCC ranges from the committed
   per-cell evaluations under ``results/paper-eval/phase2/512px-14buf-mcc/``
   using DERIVED modality, so the paper's counts can be checked rather than
   trusted.

Usage
-----
    # After running the two upstream recomputations into <audit>/recomputed/
    python3 scripts/compare_modality_recomputation.py \
        --audit-dir results/modality-track-audit-2026-09-14

Writes ``<audit-dir>/recomputation.json`` and ``recomputation.md``.
"""

from __future__ import annotations

import argparse
import glob
import json
import statistics
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.derive_condition_modality import condition_modality  # noqa: E402

PLATEAU_PUBLISHED = "results/working-precision/gs-plateau-characterisation.json"
SWEEP_PUBLISHED = "results/tile-size-sweep/tile_size_sweep.json"
PHASE2_MCC_DIR = "results/paper-eval/phase2/512px-14buf-mcc"
PHASE2_RUNS = ("retest-phase2a", "retest-phase2b", "retest-phase2c",
               "retest-phase2d", "retest-phase2e")


# ── 1. the plateau tabulation ────────────────────────────────────────────

def plateau_delta(published: Path, recomputed: Path) -> dict[str, Any]:
    """Diff the plateau tabulation's per-modality summary and its siblings.

    Args:
        published: The committed ``gs-plateau-characterisation.json``.
        recomputed: The same file rebuilt with derived modality.

    Returns:
        ``{"by_modality": [...], "unchanged_summaries": [...],
        "changed_summaries": [...], "n_analysed": {...},
        "conditions_that_moved": [...]}``.
    """
    old = json.loads(published.read_text(encoding="utf-8"))
    new = json.loads(recomputed.read_text(encoding="utf-8"))

    def index(doc: dict, name: str) -> dict[str, dict]:
        return {r["group"]: r for r in doc["summary"][name]}

    rows = []
    o, n = index(old, "by_modality"), index(new, "by_modality")
    for group in sorted(set(o) | set(n)):
        before, after = o.get(group), n.get(group)
        rows.append({
            "group": group,
            "before": None if before is None else {
                k: before[k] for k in ("n", "onset_median", "onset_p90",
                                       "onset_max", "tail_drift_median")},
            "after": None if after is None else {
                k: after[k] for k in ("n", "onset_median", "onset_p90",
                                      "onset_max", "tail_drift_median")},
            "changed": before != after,
        })

    unchanged, changed = [], []
    for name in ("overall", "by_architecture", "by_tile_size", "by_thinking",
                 "by_temperature"):
        same = (json.dumps(old["summary"][name], sort_keys=True)
                == json.dumps(new["summary"][name], sort_keys=True))
        (unchanged if same else changed).append(name)

    old_mod = {c["condition_id"]: c.get("modality") for c in old["conditions"]}
    moved = [{"condition_id": c["condition_id"],
              "before": old_mod.get(c["condition_id"]),
              "after": c.get("modality"),
              "basis": c.get("modality_basis")}
             for c in new["conditions"]
             if old_mod.get(c["condition_id"]) != c.get("modality")]

    return {"by_modality": rows, "unchanged_summaries": unchanged,
            "changed_summaries": changed,
            "n_analysed": {"before": old["n_analysed"], "after": new["n_analysed"]},
            "conditions_that_moved": moved}


# ── 2. the tile-size sweep's modality grid ───────────────────────────────

def sweep_delta(published: Path, recomputed: Path) -> dict[str, Any]:
    """Diff the tile-size sweep's ``by_arch_modality`` grid and isolation views.

    Args:
        published: The committed ``tile_size_sweep.json``.
        recomputed: The same file rebuilt with derived modality.

    Returns:
        ``{"by_arch_modality": [...], "isolation_views": {...}}``.
    """
    old = json.loads(published.read_text(encoding="utf-8"))
    new = json.loads(recomputed.read_text(encoding="utf-8"))

    def flat(doc: dict) -> dict[tuple[str, str], dict]:
        out = {}
        for size, legs in doc["best_per_size"]["by_arch_modality"].items():
            for leg, cell in legs.items():
                out[(size, leg)] = cell
        return out

    o, n = flat(old), flat(new)
    rows = []
    for key in sorted(set(o) | set(n)):
        before, after = o.get(key), n.get(key)

        def summarise(cell: dict | None) -> dict | None:
            if cell is None:
                return None
            return {"ref": cell["ref"], "f1": cell["f1"], "mcc": cell["mcc"]}

        rows.append({"size": key[0], "leg": key[1],
                     "before": summarise(before), "after": summarise(after),
                     "changed": summarise(before) != summarise(after)})

    views = {}
    for name in ("single_pass_isolation", "consensus_isolation", "pv_matched"):
        views[name] = ("IDENTICAL"
                       if json.dumps(old[name], sort_keys=True)
                       == json.dumps(new[name], sort_keys=True) else "CHANGED")
    return {"by_arch_modality": rows, "isolation_views": views}


# ── 3. the paper's § R2 phase-2 MCC groups ───────────────────────────────

def phase2_mcc_groups() -> dict[str, Any]:
    """Recompute the § R2 metric-trade-off groups from the committed evaluations.

    Reads every cell under ``results/paper-eval/phase2/512px-14buf-mcc/``, maps
    it back to its registered condition, derives its modality, and reports each
    group's size, how many cells have a defined tile MCC, and the MCC range —
    the quantities § R2 and its 2026-08-17 changelog entry quote.

    Returns:
        ``{"cells": [...], "groups": {...}}``.
    """
    decomposition = json.loads(
        (BASE_DIR / "results/run-conditions.json").read_text(
            encoding="utf-8"))["decomposition"]
    # Map a cell directory name (p2a-brief-text, p2b-image-t-0-0) back to its
    # condition. The directory slug drops "." and inserts "-" inconsistently
    # ("image-t0.0" -> "image-t-0-0"), so both sides are compared with every
    # non-alphanumeric character removed.
    def key(text: str) -> str:
        return "".join(ch for ch in text.lower() if ch.isalnum())

    by_label: dict[str, tuple[str, str]] = {}
    for run in PHASE2_RUNS:
        stem = "p2" + run[len("retest-phase2"):]
        for cond in (decomposition.get(run) or {}).get("conditions", []):
            by_label[key(f"{stem}-{cond['label']}")] = (run, cond["label"])

    cells = []
    for path in sorted(glob.glob(str(BASE_DIR / PHASE2_MCC_DIR / "*/evaluation.json"))):
        name = Path(path).parent.name
        run_label = by_label.get(key(name))
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
        mcc = tile_mcc_of(doc)
        f1 = f1_at_20m_of(doc)
        if run_label is None:
            cells.append({"cell": name, "condition_id": None, "modality": None,
                          "basis": "unmapped", "tile_mcc": mcc, "f1_20": f1})
            continue
        run, label = run_label
        pool = next((c.get("proposer_pool") for c in decomposition[run]["conditions"]
                     if c["label"] == label), "") or ""
        modality, basis = condition_modality(run, pool)
        cells.append({"cell": name, "condition_id": f"{run}::{label}",
                      "modality": modality, "basis": basis,
                      "tile_mcc": mcc, "f1_20": f1})

    groups: dict[str, Any] = {}
    for modality in ("text", "image", None):
        members = [c for c in cells if c["modality"] == modality]
        defined = [c for c in members if c["tile_mcc"] is not None]
        f1s = [c["f1_20"] for c in members if c["f1_20"] is not None]
        groups[str(modality)] = {
            "n_cells": len(members),
            "n_with_a_defined_tile_mcc": len(defined),
            "n_undefined": len(members) - len(defined),
            "tile_mcc_min": round(min((c["tile_mcc"] for c in defined), default=0.0), 4)
            if defined else None,
            "tile_mcc_max": round(max((c["tile_mcc"] for c in defined), default=0.0), 4)
            if defined else None,
            "tile_mcc_median": round(statistics.median(c["tile_mcc"] for c in defined), 4)
            if defined else None,
            "f1_20_median": round(statistics.median(f1s), 4) if f1s else None,
            "cells": sorted(c["cell"] for c in members),
        }
    return {"cells": cells, "groups": groups}


def tile_mcc_of(doc: dict) -> float | None:
    """Read a cell evaluation's tile-level MCC point estimate.

    ``evaluate_detections.py`` writes it at
    ``summary.tile_classification.mcc.point``, and leaves it null with
    ``method: "undefined"`` when the tile confusion matrix has an empty row or
    column (a cell that flags every tile positive has no true negatives, so MCC
    is undefined rather than zero — the distinction § R2 of the paper draft
    turns on).

    Args:
        doc: A parsed ``evaluation.json``.

    Returns:
        The tile MCC point estimate, or None when it is undefined or absent.
    """
    mcc = ((doc.get("summary") or {}).get("tile_classification") or {}).get("mcc") or {}
    point = mcc.get("point")
    return None if not isinstance(point, (int, float)) else float(point)


def f1_at_20m_of(doc: dict) -> float | None:
    """Read a cell evaluation's F1 at the 20 m headline buffer.

    Args:
        doc: A parsed ``evaluation.json``.

    Returns:
        F1@20 m, or None when absent.
    """
    for buf in (doc.get("summary") or {}).get("buffers") or []:
        if buf.get("buffer_metres") == 20 or buf.get("buffer_m") == 20:
            value = buf.get("f1")
            return None if value is None else float(value)
    return None


# ── rendering ────────────────────────────────────────────────────────────

def render(result: dict[str, Any]) -> str:
    """Render the before → after tables as Markdown.

    Args:
        result: The assembled recomputation record.

    Returns:
        The Markdown body.
    """
    out = ["# Modality-track audit — recomputation, before → after", "",
           "> **Last revised**: 2026-09-14 (original publication). "
           "See [§ Changelog](#changelog) for revision history.", "",
           "Every modality-GROUPED statistic the 2026-09-14 audit could move, "
           "recomputed with derived labels. US$0: no cell is re-scored, only "
           "its group membership moves. Generated by "
           "`scripts/compare_modality_recomputation.py`.", ""]

    plateau = result.get("plateau")
    out += ["## 1. `results/working-precision/gs-plateau-characterisation.json` "
            "— `summary.by_modality`", ""]
    if plateau is None:
        out += ["Not recomputed in this run.", ""]
    else:
        out += [f"Comparison basis: {plateau.get('comparison_basis', '—')}.", "",
                f"Conditions analysed: {plateau['n_analysed']['before']} → "
                f"{plateau['n_analysed']['after']}.", "",
                "| group | n | onset median | p90 | max | tail drift (median) |",
                "|---|---:|---:|---:|---:|---:|"]
        for row in plateau["by_modality"]:
            for state in ("before", "after"):
                r = row[state]
                if r is None:
                    out.append(f"| {row['group']} ({state}) | — | — | — | — | — |")
                else:
                    out.append(
                        f"| {row['group']} ({state}) | {r['n']} | "
                        f"{r['onset_median']:g} m | {r['onset_p90']:g} | "
                        f"{r['onset_max']} | {r['tail_drift_median']:+.4f} |")
        out += ["", f"Sibling summaries unchanged: "
                    f"{', '.join(f'`{s}`' for s in plateau['unchanged_summaries']) or 'none'}. "
                    f"Changed: "
                    f"{', '.join(f'`{s}`' for s in plateau['changed_summaries']) or 'none'}.", "",
                "Conditions that moved group:", ""]
        if plateau["conditions_that_moved"]:
            out += ["| condition | before | after | derivation basis |", "|---|---|---|---|"]
            out += [f"| `{m['condition_id']}` | {m['before']} | {m['after']} | "
                    f"{m['basis']} |" for m in plateau["conditions_that_moved"]]
        else:
            out.append("None.")
        out.append("")

    sweep = result.get("sweep")
    out += ["## 2. `results/tile-size-sweep/tile_size_sweep.json` "
            "— `best_per_size.by_arch_modality`", ""]
    if sweep is None:
        out += ["Not recomputed in this run.", ""]
    else:
        out += [f"Comparison basis: {sweep.get('comparison_basis', '—')}.", "",
                "| size | leg | before (ref, F1, MCC) | after (ref, F1, MCC) |",
                "|---|---|---|---|"]
        for row in sweep["by_arch_modality"]:
            def cell(value: dict | None) -> str:
                if value is None:
                    return "— (leg absent)"
                return (f"`{value['ref']}` {value['f1']} / "
                        f"{'—' if value['mcc'] is None else value['mcc']}")
            mark = " **← changed**" if row["changed"] else ""
            out.append(f"| {row['size']} | `{row['leg']}` | {cell(row['before'])} | "
                       f"{cell(row['after'])}{mark} |")
        out += ["", "Isolation views (View 1 / View 3, which hold modality fixed "
                    "rather than grouping by it): "
                    + ", ".join(f"`{k}` {v}" for k, v in sweep["isolation_views"].items()),
                ""]

    phase2 = result.get("phase2_mcc")
    out += ["## 3. The paper's § R2 metric-trade-off groups "
            "(`results/paper-eval/phase2/512px-14buf-mcc/`)", ""]
    if phase2 is None:
        out += ["Not recomputed in this run.", ""]
    else:
        out += ["| derived modality | cells | defined tile MCC | undefined | "
                "MCC min | MCC max | MCC median | F1@20 median |",
                "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for key in ("text", "image", "None"):
            g = phase2["groups"].get(key)
            if g is None or g["n_cells"] == 0:
                continue
            out.append(
                f"| {key} | {g['n_cells']} | {g['n_with_a_defined_tile_mcc']} | "
                f"{g['n_undefined']} | {g['tile_mcc_min']} | {g['tile_mcc_max']} | "
                f"{g['tile_mcc_median']} | {g['f1_20_median']} |")
        out.append("")

    out += ["## Changelog", "",
            "### 2026-09-14 — Original publication", "",
            "First recomputation of the modality-grouped statistics after the "
            "corpus-wide modality-track audit of 2026-09-14. No prior revision "
            "to diff against."]
    # Collapse any consecutive blanks the section builders left behind, so the
    # rendered document passes markdownlint MD012.
    lines: list[str] = []
    for line in out:
        if line == "" and lines and lines[-1] == "":
            continue
        lines.append(line)
    return "\n".join(lines)


def main() -> int:
    """Command-line entry point.

    Returns:
        0 on success.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--audit-dir", default="results/modality-track-audit-2026-09-14",
                    help="The audit directory; recomputed inputs are read from "
                         "its `recomputed/` subdirectory and the report is "
                         "written into it.")
    args = ap.parse_args()
    audit = BASE_DIR / args.audit_dir
    recomputed = audit / "recomputed"

    result: dict[str, Any] = {
        "_README": ("Before → after for every modality-GROUPED statistic the "
                    "2026-09-14 audit could move. No cell re-scored; only "
                    "group membership moves."),
        "generated_by": "scripts/compare_modality_recomputation.py",
    }

    # BEFORE is the legacy labelling rule re-run on TODAY'S register, not the
    # published artefact: both published tabulations predate register growth
    # (the plateau one covers 306 conditions against today's 459), so diffing
    # against them would conflate that growth with the modality correction.
    # The A/B below changes exactly one thing.
    plateau_before = recomputed / "working-precision-legacy/gs-plateau-characterisation.json"
    plateau_after = recomputed / "working-precision/gs-plateau-characterisation.json"
    if plateau_before.exists() and plateau_after.exists():
        result["plateau"] = plateau_delta(plateau_before, plateau_after)
        result["plateau"]["comparison_basis"] = (
            "legacy name-substring rule vs derived modality, both on the "
            f"register at this commit; the published {PLATEAU_PUBLISHED} is "
            "older and is not the baseline")
    else:
        print(f"skipping plateau: need both {plateau_before} and {plateau_after}")

    sweep_before = recomputed / "tile-size-sweep-legacy/tile_size_sweep.json"
    sweep_after = recomputed / "tile-size-sweep/tile_size_sweep.json"
    if sweep_before.exists() and sweep_after.exists():
        result["sweep"] = sweep_delta(sweep_before, sweep_after)
        result["sweep"]["comparison_basis"] = (
            "legacy name-substring rule vs derived modality, both on the "
            f"register at this commit; the published {SWEEP_PUBLISHED} is "
            "compared separately below")
        result["sweep"]["vs_published"] = sweep_delta(
            BASE_DIR / SWEEP_PUBLISHED, sweep_after)
    else:
        print(f"skipping sweep: need both {sweep_before} and {sweep_after}")

    if (BASE_DIR / PHASE2_MCC_DIR).is_dir():
        result["phase2_mcc"] = phase2_mcc_groups()
    else:
        print(f"skipping phase-2 MCC groups: {PHASE2_MCC_DIR} not found")

    audit.mkdir(parents=True, exist_ok=True)
    (audit / "recomputation.json").write_text(
        json.dumps(result, indent=1) + "\n", encoding="utf-8")
    (audit / "recomputation.md").write_text(render(result) + "\n", encoding="utf-8")
    print(f"wrote {audit}/recomputation.{{json,md}}")

    if "plateau" in result:
        moved = result["plateau"]["conditions_that_moved"]
        print(f"plateau: {len(moved)} condition(s) moved group; "
              f"changed summaries {result['plateau']['changed_summaries']}")
    if "sweep" in result:
        changed = [r for r in result["sweep"]["by_arch_modality"] if r["changed"]]
        print(f"sweep: {len(changed)} of "
              f"{len(result['sweep']['by_arch_modality'])} grid legs changed; "
              f"isolation views {result['sweep']['isolation_views']}")
    if "phase2_mcc" in result:
        for key, g in result["phase2_mcc"]["groups"].items():
            if g["n_cells"]:
                print(f"phase-2 {key}: {g['n_cells']} cells, "
                      f"{g['n_with_a_defined_tile_mcc']} with a defined MCC, "
                      f"range {g['tile_mcc_min']}–{g['tile_mcc_max']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
