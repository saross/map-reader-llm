#!/usr/bin/env python3
"""
Inventory the fixed-parameter pass-count (K) ladders that exist in the register.

The K-ladder review (``planning/k-ladder-review-2026-09-11.md`` § 3 step 1,
under ruling R1) asks a narrow question: for each proposer family, which
K rungs exist as COMMITTED VERIFIED cells whose non-K parameters are
identical, and where are the gaps?

Ruling R1 fixes the verifier at every rung — the carried Gemini 3 verifier,
recorded in the register as instruction file ``verify_adversarial.md``,
model ``gemini-3-flash-preview``, thinking level ``minimal``, temperature
0.0, one iteration. The project's own shorthand for that configuration is
"verify_adversarial-text, T=0.0, MINIMAL, n=1" (the ``_note`` of every
``stride-phaseb-2026-08-25`` ladder row); there is no file called
``verify_adversarial-text.md`` in ``prompts/system-instructions/``, so the
inventory matches on the recorded fields, not on the shorthand.

A LADDER FAMILY is a maximal set of verified conditions sharing:

* ``run_id`` (so one campaign, one corpus, one tiling);
* ``proposer_pool`` (which in this project encodes the proposer model,
  its thinking level, the input modality and the sampling temperature);
* the full ``verifier_config`` signature (variant, instruction file,
  model, thinking level, temperature, iterations);
* the evaluation frame and reference of the cells' committed evaluations.

Rungs are the distinct ``n_passes`` values in that set. A family whose
rungs differ in anything besides K is reported as ``not-a-ladder`` with the
differing field named (stop state 1 of
``planning/k-ladder-phase1-run-2026-09-12.md``).

GAP CLASSIFICATION. For every K in {1, 3, 5, 10} absent from a family, the
gap is classed:

``committed``
    not a gap — a verified cell exists at this K.
``zero-usd-exact``
    a first-N sub-pool consensus can be built from the family's committed
    passes AND an existing verifier ``probabilities.json`` covers that
    sub-pool's candidates. Coverage means the sub-pool's candidates are a
    POSITION-MATCHED subset of the universe the verifier saw; it is proved
    per gap, never inferred from a count.
``zero-usd-inherited``
    the rung can be built by the preregistered first-N rule with verifier
    probabilities INHERITED from a longer pass ladder by nearest neighbour
    within 10 m — the mechanism ``scripts/stride55_ladder.py`` and
    ``scripts/gemini37_arm_ladder.py`` already use and the register already
    carries (validated at +/-0.008 on the gold standard, 2026-08-25). Costs
    US$0 but is an approximation, not an exact re-verification.
``needs-verifier-pass``
    no existing verifier output covers the sub-pool's candidate universe, so
    the rung needs a verifier call. Phase 2; costed, not run.
``no-passes``
    the family's run does not hold enough proposer passes to build the rung
    at all (e.g. a three-pass run has no K = 5 rung).

Usage::

    python scripts/build_k_ladder_inventory.py \\
        --out-dir results/k-ladder-2026-09-12

Zero API, zero bootstrap; pure register and filesystem reads.

Created: 2026-09-12 (Session 154, K-ladder Phase 1 step 1)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CONDITIONS_MANIFEST = REPO_ROOT / "results/conditions-manifest.json"
COVERAGE_PROBE = REPO_ROOT / "results/k-ladder-2026-09-12/subpool-coverage-probe.json"
RUN_CONDITIONS = REPO_ROOT / "results/run-conditions.json"
RUN_FACTS = REPO_ROOT / "results/run-facts.json"

#: The rungs the review asks about (`planning/k-ladder-review-2026-09-11.md` § 1).
LADDER_RUNGS = (1, 3, 5, 10)

#: Ruling R1's verifier: the carried Gemini 3 verifier, no swaps.
R1_VERIFIER = {
    "instruction_file": "verify_adversarial.md",
    "model": "gemini-3-flash-preview",
    "thinking_level": "minimal",
    "temperature": 0.0,
}

#: Where a pool's proposer passes live, per run. Used only to count the
#: passes available for a first-N rung; absent runs are reported as unknown.
PASS_ROOTS = {
    "pv-diag-384": "outputs/h11/pv-diag-384",
    "stride-55map-2026-08-25": "outputs/stride-55map-2026-08-25",
    "gemini37-55map-2026-08-29": "outputs/gemini37-55map-2026-08-29",
    "grid-2026-08-18": "outputs/grid-2026-08-18",
    "gemini37-screen-2026-08-28": "outputs/gemini37-screen-2026-08-28",
    "gemini37-image-gs-2026-09-01": "outputs/gemini37-image-gs-2026-09-01",
    "image-b-gs-2026-08-28": "outputs/image-b-gs-2026-08-28",
    "stride-phaseb-2026-08-25": "outputs/stride-phaseb-2026-08-25",
    "stride-phasec-2026-08-25": "outputs/stride-phasec-2026-08-25",
}

#: A proposer pass directory is ``run_<digits>`` exactly. ``run_3_recovery``
#: is a completion of pass 3, not a fourth pass, so counting it would
#: overstate the ladder's reach (the mistake this pattern exists to avoid).
PASS_DIR_RE = re.compile(r"^run_\d+$")

#: Human family names, keyed by (run_id, proposer_pool). Anything not named
#: here is reported under its raw (run, pool) key, so nothing is dropped.
FAMILY_NAMES = {
    ("pv-diag-384", "flash-minimal-text-n30-t07-text-t0.0"): "Gemini 3 MINIMAL text 384 px, T 0.0",
    ("pv-diag-384", "flash-minimal-text-n30-t07-text-t0.3"): "Gemini 3 MINIMAL text 384 px, T 0.3",
    ("pv-diag-384", "flash-minimal-text-n30-t07-text-t0.7"): "Gemini 3 MINIMAL text 384 px, T 0.7",
    ("pv-diag-384", "flash-minimal-text-n30-t07-text-t1.0"): "Gemini 3 MINIMAL text 384 px, T 1.0",
    ("pv-diag-384", "flash-high-text-n5-text-t0.0"): "Gemini 3 HIGH text 384 px, T 0.0",
    ("pv-diag-384", "flash-high-text-n5-text-t0.3"): "Gemini 3 HIGH text 384 px, T 0.3",
    ("pv-diag-384", "flash-high-text-n5-text-t0.7"): "Gemini 3 HIGH text 384 px, T 0.7",
    ("pv-diag-384", "flash-high-text-n5-text-t1.0"): "Gemini 3 HIGH text 384 px, T 1.0",
    ("pv-diag-384", "image-n5-image-t0.3"): "Gemini 3 MINIMAL image 384 px, T 0.3",
    ("pv-diag-384", "image-n5-image-t0.7"): "Gemini 3 MINIMAL image 384 px, T 0.7",
    ("pv-diag-384", "image-n5-image-t1.0"): "Gemini 3 MINIMAL image 384 px, T 1.0",
    ("pv-diag-384", "flash-high-image-n5-image-t0.3"): "Gemini 3 HIGH image 384 px, T 0.3",
    ("pv-diag-384", "flash-high-image-n5-image-t0.7"): "Gemini 3 HIGH image 384 px, T 0.7",
    ("pv-diag-384", "flash-high-image-n5-image-t1.0"): "Gemini 3 HIGH image 384 px, T 1.0",
    ("gemini37-screen-2026-08-28", "g384_ov192_g37"): "Gemini 3.7 text, GS B geometry",
    ("gemini37-image-gs-2026-09-01", "g384_ov192_g37img"): "Gemini 3.7 image, GS B geometry",
    ("image-b-gs-2026-08-28", "g384_ov192_image"): "Gemini 3 MINIMAL image, GS B geometry",
    ("image-b-gs-2026-08-28", "g384_ov192_image_high"): "Gemini 3 HIGH image, GS B geometry",
    ("grid-2026-08-18", "brief-text"): "Grid campaign text (geometry in the label)",
    ("stride-phaseb-2026-08-25", "g384_ov128"): "Stride A (g384 ov128), GS, exact re-verification",
    ("stride-55map-2026-08-25", "g384_ov128_55map"): "Stride A (g384 ov128), 55-map",
    ("stride-55map-2026-08-25", "g384_ov192_55map"): "Stride B (g384 ov192), 55-map",
    ("gemini37-55map-2026-08-29", "g384_ov192_55map_g37"): "Gemini 3.7 arm, 55-map",
}


def verifier_signature(cond: dict[str, Any]) -> tuple:
    """The full verifier signature of a condition, as a hashable tuple."""
    vc = cond.get("verifier_config") or {}
    return (
        vc.get("variant"),
        vc.get("instruction_file"),
        vc.get("model"),
        vc.get("thinking_level"),
        vc.get("temperature"),
        vc.get("iterations"),
    )


def is_r1_verifier(cond: dict[str, Any]) -> bool:
    """True when the condition carries ruling R1's carried Gemini 3 verifier."""
    vc = cond.get("verifier_config") or {}
    return all(vc.get(k) == v for k, v in R1_VERIFIER.items())


#: The headline matching buffer per corpus. 20 m on the gold standard, 50 m on
#: the 55-map corpus — the ``is_primary_buffer`` rule of
#: ``docs/methodology/notation-key.md`` § 7.1.
HEADLINE_BUFFER_M = {"4-map-gs": 20, "55-map": 50}
DEFAULT_HEADLINE_BUFFER_M = 20


def eval_recipe(cond: dict[str, Any]) -> dict[str, Any]:
    """The frame, reference and metrics of the condition's committed evaluation.

    Records F1 at BOTH 20 m and 50 m, because the corpora have different
    headline buffers and a ladder must be read at its own.

    Args:
        cond: A condition row joined with its register-side fields.

    Returns:
        The evaluation path, its bounds and ground truth, F1 at 20 m and 50 m,
        the tile MCC point estimate, and the detection count.
    """
    path = cond.get("eval_path") or ""
    out = {"eval_path": path, "bounds": None, "ground_truth": None,
           "f1_20": None, "f1_50": None, "mcc": None,
           "n_detections": cond.get("n_detections")}
    full = REPO_ROOT / path
    if not path or not full.exists():
        return out
    try:
        doc = json.loads(full.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return out
    cli = (doc.get("_metadata") or {}).get("cli_args") or {}
    out["bounds"] = cli.get("bounds")
    out["ground_truth"] = cli.get("ground_truth")
    summary = doc.get("summary") or {}
    for band in summary.get("buffers", []):
        metres = band.get("buffer_metres", band.get("buffer_m"))
        if metres == 20:
            out["f1_20"] = band.get("f1")
        elif metres == 50:
            out["f1_50"] = band.get("f1")
    tile = (summary.get("tile_classification") or {}).get("mcc")
    out["mcc"] = tile.get("point") if isinstance(tile, dict) else tile
    if summary.get("n_detections") is not None:
        out["n_detections"] = summary.get("n_detections")
    return out


def count_passes(run_id: str, pool: str) -> int | None:
    """How many proposer passes the run holds for this pool, if discoverable."""
    root = PASS_ROOTS.get(run_id)
    if not root:
        return None
    base = REPO_ROOT / root
    if not base.exists():
        return None
    # pv-diag-384 pools are recorded as "<pool-dir>-<temperature-dir>"; the
    # register's pool name joins the two directory levels with a hyphen.
    candidates = []
    for depth in (1, 2, 3):
        candidates += [p for p in base.glob("/".join(["*"] * depth)) if p.is_dir()]
    best = None
    for path in candidates:
        rel = path.relative_to(base)
        joined = "-".join(rel.parts)
        if joined == pool or rel.parts[-1] == pool:
            runs = [p for p in path.glob("run_*")
                    if p.is_dir() and PASS_DIR_RE.match(p.name)]
            if runs:
                best = max(best or 0, len(runs))
    return best


#: Families whose committed rungs were themselves built by the first-N
#: inheritance mechanism (``cluster_first_n`` plus nearest-neighbour
#: probability inheritance within 10 m). A missing rung in one of these can be
#: added the same way at US$0, as an approximation rather than an exact
#: re-verification.
INHERITANCE_FAMILIES = {
    ("stride-55map-2026-08-25", "g384_ov128_55map"),
    ("stride-55map-2026-08-25", "g384_ov192_55map"),
    ("gemini37-55map-2026-08-29", "g384_ov192_55map_g37"),
}


def load_coverage_probe() -> dict[str, Any] | None:
    """The candidate-position coverage probe's findings, if it has been run.

    ``scripts/probe_subpool_verifier_coverage.py`` answers the one question the
    gap classification turns on: can a shorter first-N sub-pool union reuse a
    longer union's verifier probabilities? The probe's verdict is cited per gap
    so the classification is evidence-backed rather than asserted.
    """
    if not COVERAGE_PROBE.exists():
        return None
    try:
        return json.loads(COVERAGE_PROBE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def classify_gaps(fam: dict[str, Any], probe: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Class every absent rung of one family, with the evidence for the class.

    Args:
        fam: A family record from :func:`build`.
        probe: The coverage probe's payload, or ``None`` if it has not run.

    Returns:
        One record per K in :data:`LADDER_RUNGS`, in ascending order.
    """
    available = fam["n_proposer_passes_on_disk"]
    key = (fam["run_id"], fam["proposer_pool"])
    probe_summary = None
    if probe:
        not_covered = [pr for pr in probe["probes"] if not pr["covered_by_position_match"]]
        probe_summary = (
            f"{len(not_covered)} of {probe['n_probes']} probed sub-pool / longer-union "
            f"pairs are NOT positional prefixes at {probe['tolerance_m']} m "
            f"(`results/k-ladder-2026-09-12/subpool-coverage-probe.json`)")
    out = []
    for k in LADDER_RUNGS:
        if k in fam["cells"]:
            out.append({"K": k, "class": "committed",
                        "evidence": [c["condition_id"] for c in fam["cells"][k]]})
            continue
        if available is not None and k > available:
            out.append({
                "K": k, "class": "no-passes",
                "evidence": (f"the run holds {available} proposer pass(es) for this "
                             f"pool, fewer than the {k} the rung needs")})
            continue
        if key in INHERITANCE_FAMILIES:
            out.append({
                "K": k, "class": "zero-usd-inherited",
                "evidence": ("this family's committed rungs were built by "
                             "cluster_first_n plus nearest-neighbour probability "
                             "inheritance within 10 m (scripts/stride55_ladder.py, "
                             "scripts/gemini37_arm_ladder.py), so the same "
                             "mechanism reaches this rung at US$0 — as an "
                             "approximation, not an exact re-verification")})
            continue
        out.append({
            "K": k, "class": "needs-verifier-pass",
            "evidence": (
                "a first-N sub-pool consensus is buildable at US$0 "
                "(scripts/merge_passes.py --passes 1,..,N, the preregistered "
                "first-N rule), but no committed verifier output covers its "
                "candidates: clustering over N passes recomputes every cluster's "
                "mean centroid, so the sub-pool union is neither a positional "
                "prefix of a longer union nor a coordinate subset of it. "
                + (probe_summary or "The coverage probe has not been run."))})
    return out


def register_side_fields() -> dict[str, dict[str, Any]]:
    """``eval_path`` / ``detections`` / ``_note`` per condition id.

    ``results/conditions-manifest.json`` is the projected register and does
    not carry these three fields; ``results/run-conditions.json`` does. The
    inventory needs the evaluation path to read each cell's frame and
    reference, so the two are joined on ``<run_id>::<label>``.
    """
    dec = json.loads(RUN_CONDITIONS.read_text(encoding="utf-8"))["decomposition"]
    out: dict[str, dict[str, Any]] = {}
    for run_id, entry in dec.items():
        for cond in entry.get("conditions", []):
            out[f"{run_id}::{cond['label']}"] = {
                "eval_path": cond.get("eval_path"),
                "detections": cond.get("detections"),
                "_note": cond.get("_note"),
            }
    return out


def build() -> dict[str, Any]:
    """Group every verified condition into ladder families and classify gaps."""
    manifest = json.loads(CONDITIONS_MANIFEST.read_text(encoding="utf-8"))
    facts = json.loads(RUN_FACTS.read_text(encoding="utf-8"))["facts"]
    side = register_side_fields()
    probe = load_coverage_probe()

    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for cond in manifest["conditions"]:
        if cond.get("aggregation") != "verified":
            continue
        cond = dict(cond)
        cond.update(side.get(cond["condition_id"]) or {})
        # The recipe is part of the family key, not a property of it: a
        # 55-map pool scored against r2, canonical and standardised
        # references is three ladders, not one ladder with three recipes,
        # and mixing them would compare cells across strata.
        cond["_recipe"] = eval_recipe(cond)
        key = (cond["run_id"], cond.get("proposer_pool"), verifier_signature(cond),
               cond["_recipe"]["bounds"], cond["_recipe"]["ground_truth"])
        groups[key].append(cond)

    families = []
    for (run_id, pool, vsig, bounds, ground_truth), conds in groups.items():
        rungs: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for cond in conds:
            k = cond.get("n_passes")
            if k is None:
                continue
            rungs[int(k)].append(cond)
        recipes = set()
        cells = {}
        for k in sorted(rungs):
            entries = []
            for cond in sorted(rungs[k], key=lambda c: c["condition_id"]):
                rec = cond["_recipe"]
                recipes.add((rec["bounds"], rec["ground_truth"]))
                entries.append({
                    "condition_id": cond["condition_id"],
                    "vote_threshold": cond.get("vote_threshold"),
                    "prob_threshold": cond.get("prob_threshold"),
                    "scope_override": (cond.get("scope_override") or {}).get("test_set_id"),
                    **rec,
                })
            cells[k] = entries
        n_passes_available = count_passes(run_id, pool)
        base_name = FAMILY_NAMES.get((run_id, pool), f"{run_id} / {pool}")
        frame_tag = (bounds or "no-committed-evaluation").split("/")[-1]
        ref_tag = (ground_truth or "no-reference").split("/")[-1]
        fam = {
            "family": f"{base_name} [{frame_tag} / {ref_tag}]",
            "family_base": base_name,
            "frame_file": bounds,
            "reference_file": ground_truth,
            "run_id": run_id,
            "proposer_pool": pool,
            "corpus": (facts.get(run_id) or {}).get("corpus"),
            "verifier": {
                "variant": vsig[0], "instruction_file": vsig[1], "model": vsig[2],
                "thinking_level": vsig[3], "temperature": vsig[4], "iterations": vsig[5],
            },
            "r1_verifier": all(
                vsig[i] == R1_VERIFIER[k]
                for i, k in ((1, "instruction_file"), (2, "model"),
                             (3, "thinking_level"), (4, "temperature"))
            ),
            "n_proposer_passes_on_disk": n_passes_available,
            "rungs_present": sorted(cells),
            "n_distinct_eval_recipes": len(recipes),
            "eval_recipes": sorted(
                [{"bounds": b, "ground_truth": g} for b, g in recipes],
                key=lambda r: str(r["bounds"])),
            "cells": cells,
        }
        fam["headline_buffer_m"] = HEADLINE_BUFFER_M.get(
            fam["corpus"], DEFAULT_HEADLINE_BUFFER_M)
        fam["gaps"] = classify_gaps(fam, probe)
        fam["ladder_status"] = (
            "not-a-ladder: rungs do not share one evaluation recipe"
            if len(recipes) > 1 else
            ("ladder" if len([k for k in cells if k in LADDER_RUNGS]) >= 2
             else "single-rung")
        )
        families.append(fam)

    families.sort(key=lambda f: (f["family"], str(f["verifier"]["model"])))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "card": "planning/k-ladder-review-2026-09-11.md",
        "run_card": "planning/k-ladder-phase1-run-2026-09-12.md",
        "ruling": "R1 — the carried Gemini 3 verifier at every rung, no swapping",
        "r1_verifier": R1_VERIFIER,
        "ladder_rungs_asked": list(LADDER_RUNGS),
        "source": {
            "conditions_manifest": "results/conditions-manifest.json",
            "run_facts": "results/run-facts.json",
        },
        "coverage_probe": {
            "path": "results/k-ladder-2026-09-12/subpool-coverage-probe.json",
            "ran": probe is not None,
            "n_probes": (probe or {}).get("n_probes"),
            "tolerance_m": (probe or {}).get("tolerance_m"),
            "n_covered": sum(
                1 for pr in (probe or {}).get("probes", [])
                if pr["covered_by_position_match"]),
        },
        "n_families": len(families),
        "families": families,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    """One table per family, gaps marked; the narrative is added by hand."""
    lines = [
        "<!-- GENERATED by scripts/build_k_ladder_inventory.py — "
        "the narrative sections are hand-written and preserved on regeneration. -->",
        "",
        "## Families, one table each",
        "",
        f"Generated {payload['generated_at_utc']} from "
        "`results/conditions-manifest.json`. "
        f"{payload['n_families']} (run, pool, verifier) groups hold at least one "
        "verified condition.",
        "",
    ]
    for fam in payload["families"]:
        if len(fam["rungs_present"]) < 2:
            continue
        lines += [
            f"### {fam['family']}",
            "",
            f"- run `{fam['run_id']}`, pool `{fam['proposer_pool']}`, "
            f"corpus {fam['corpus']}",
            f"- verifier: `{fam['verifier']['instruction_file']}` / "
            f"`{fam['verifier']['model']}` / {fam['verifier']['thinking_level']} / "
            f"T {fam['verifier']['temperature']} / n {fam['verifier']['iterations']} "
            f"— R1 compliant: **{'yes' if fam['r1_verifier'] else 'no'}**",
            f"- proposer passes on disk: {fam['n_proposer_passes_on_disk']}",
            f"- ladder status: {fam['ladder_status']}",
            f"- headline buffer: {fam['headline_buffer_m']} m "
            f"(the {fam['corpus']} corpus's, per the notation key's "
            "`is_primary_buffer` rule)",
            "",
            "| K | condition | k | prob_t | F1@20 | F1@50 | tile-MCC | n | frame |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
        headline = fam["headline_buffer_m"]
        for k in sorted(fam["cells"]):
            for cell in fam["cells"][k]:
                frame = (cell["bounds"] or "").split("/")[-1] or "—"
                f20 = cell["f1_20"]
                f50 = cell["f1_50"]
                f20 = f"**{f20}**" if headline == 20 and f20 is not None else f20
                f50 = f"**{f50}**" if headline == 50 and f50 is not None else f50
                lines.append(
                    f"| {k} | `{cell['condition_id']}` | {cell['vote_threshold']} | "
                    f"{cell['prob_threshold']} | {f20} | {f50} | {cell['mcc']} | "
                    f"{cell['n_detections']} | {frame} |")
        missing = [k for k in payload["ladder_rungs_asked"] if k not in fam["cells"]]
        lines += ["", f"Rungs absent of {payload['ladder_rungs_asked']}: "
                      f"{missing or 'none'}", ""]
        gaps = [g for g in fam["gaps"] if g["class"] != "committed"]
        if gaps:
            lines += ["| absent K | class | why |", "|---:|---|---|"]
            for gap in gaps:
                why = gap["evidence"]
                if isinstance(why, list):
                    why = ", ".join(why)
                lines.append(f"| {gap['K']} | `{gap['class']}` | {why} |")
            lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Write the inventory JSON and the generated half of the Markdown."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--out-dir", type=Path,
                        default=REPO_ROOT / "results/k-ladder-2026-09-12",
                        help="Directory for inventory.json and inventory-tables.md.")
    args = parser.parse_args(argv)
    payload = build()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "inventory.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "inventory-tables.md").write_text(
        render_markdown(payload), encoding="utf-8")
    multi = [f for f in payload["families"] if len(f["rungs_present"]) >= 2]
    print(f"{payload['n_families']} groups; {len(multi)} with >= 2 rungs")
    for fam in multi:
        print(f"  {fam['family']:<52s} K={fam['rungs_present']} "
              f"R1={fam['r1_verifier']} recipes={fam['n_distinct_eval_recipes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
