#!/usr/bin/env python3
"""
Assemble the fourteen new four-rung K ladders Phase 2 bought
============================================================

Description:
    Phase 1 found eight fixed-parameter K ladders and reported them
    (`results/k-ladder-2026-09-12/findings.md`), and recorded in § 6.3 that the
    thirteen Gemini 3 ``pv-diag-384`` families and the 3.7 gold-standard screen
    each held only two rungs — K = 5 and K = 10 — so none reached the
    three-rung bar. Phase 2 bought their K = 1 and K = 3 rungs. This script
    assembles the result: **fourteen four-rung ladders** at K = 1, 3, 5, 10, all
    on one frame (`era2-b-487`), one reference (the Gold Standard curator
    reference), one verifier (R1), and one evaluation recipe.

    Each rung is reported at two operating points, per ruling R2:

    * ``opmax`` — the F1@20 argmax of that rung's own sweep on the board frame.
      Measured here for K = 1 and K = 3; read from the signed board's committed
      cells for K = 5 and K = 10 (and derived at US$0 for the 3.7 family, whose
      committed rungs are registered at their carried point only).
    * ``carried`` — a point fixed before evaluation. Two readings are carried
      because the corpus holds two and they diverge sharply above K = 3; see
      ``scripts/derive_k_ladder_committed_carried.py``.

    **Cost.** Every rung's verifier leg is audited flex: measured from this
    run's own metas at K = 1 and K = 3, and priced at the audit's
    ``VF_CALL_USD`` for the committed rungs. The proposer leg uses the cost
    model ``scripts/build_pareto_v2.py`` already adopts, plus one figure audited
    from the 3.7 screen's own metas:

    ========================  ==========  =====================================
    pass type                 US$ / pass  anchor
    ========================  ==========  =====================================
    Gemini 3 MINIMAL (GS 487)      0.266  `token-load-audit-2026-06-12.md` § 5
    Gemini 3 HIGH (GS 487)          2.29  same
    Gemini 3.7 low (GS screen)     1.714  `billing-reconciliation-2026-09-11.md`
                                          line 102 (ten passes, 20.9 M input /
                                          1.07 M output / 3.89 M thinking →
                                          US$17.1 flex) at the 3.7 flex rates
                                          0.375 / 1.875 (line 41: list
                                          0.75 / 3.75, flex 0.5 ×)
    ========================  ==========  =====================================

    The two Gemini 3 constants were measured on TEXT passes and scaled by
    487 / 8,541. The audit's measured HIGH **image** pass scales to US$2.23,
    within 3 % of ``HIGH_PASS_USD``, so carrying 2.29 across to the image pools
    is sound; no MINIMAL image pass was ever measured, and that is flagged per
    family rather than hidden. Crucially the pass rate is **constant within a
    family**, so each ladder's cost RATIO between rungs is exact even where the
    absolute level inherits the constant's uncertainty — and the ratio is what a
    Pareto reading of K turns on.

Usage::

    python scripts/build_k_ladder_phase2_tables.py

Outputs:
    results/k-ladder-2026-09-12/phase2/ladders.json
    results/k-ladder-2026-09-12/phase2/ladder-tables.md
    results/k-ladder-2026-09-12/figures/k-ladder-pareto-phase2.png

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

PHASE2 = BASE_DIR / "results" / "k-ladder-2026-09-12" / "phase2"
BOARD = (
    BASE_DIR
    / "results"
    / "leaderboard"
    / "era2"
    / "gs-era2-verified-board-2026-09-10"
)
FIGURE = (
    BASE_DIR
    / "results"
    / "k-ladder-2026-09-12"
    / "figures"
    / "k-ladder-pareto-phase2.png"
)

MIN_PASS_USD = 0.266
HIGH_PASS_USD = 2.29
G37_PASS_USD = 1.714
VF_CALL_USD = 0.000693
HEADLINE_BUFFER = 20

#: Per family: display label, thinking level, modality, the per-pass proposer
#: cost and how well anchored it is.
FAMILIES: dict[str, dict[str, Any]] = {
    "flash-minimal-text-n30-t07-text-t0.3": {
        "label": "Gemini 3 MINIMAL text 384 px, T 0.3",
        "thinking": "minimal", "modality": "text", "temperature": 0.3,
        "pass_usd": MIN_PASS_USD, "pass_anchor": "min-text-scaled",
    },
    "flash-minimal-text-n30-t07-text-t0.7": {
        "label": "Gemini 3 MINIMAL text 384 px, T 0.7",
        "thinking": "minimal", "modality": "text", "temperature": 0.7,
        "pass_usd": MIN_PASS_USD, "pass_anchor": "min-text-measured",
    },
    "flash-minimal-text-n30-t07-text-t1.0": {
        "label": "Gemini 3 MINIMAL text 384 px, T 1.0",
        "thinking": "minimal", "modality": "text", "temperature": 1.0,
        "pass_usd": MIN_PASS_USD, "pass_anchor": "min-text-scaled",
    },
    "flash-high-text-n5-text-t0.3": {
        "label": "Gemini 3 HIGH text 384 px, T 0.3",
        "thinking": "high", "modality": "text", "temperature": 0.3,
        "pass_usd": HIGH_PASS_USD, "pass_anchor": "high-text-t03-measured",
    },
    "flash-high-text-n5-text-t0.7": {
        "label": "Gemini 3 HIGH text 384 px, T 0.7",
        "thinking": "high", "modality": "text", "temperature": 0.7,
        "pass_usd": HIGH_PASS_USD, "pass_anchor": "high-text-measured",
    },
    "flash-high-text-n5-text-t1.0": {
        "label": "Gemini 3 HIGH text 384 px, T 1.0",
        "thinking": "high", "modality": "text", "temperature": 1.0,
        "pass_usd": HIGH_PASS_USD, "pass_anchor": "high-text-scaled",
    },
    "image-n5-image-t0.3": {
        "label": "Gemini 3 MINIMAL image 384 px, T 0.3",
        "thinking": "minimal", "modality": "image", "temperature": 0.3,
        "pass_usd": MIN_PASS_USD, "pass_anchor": "min-image-unmeasured",
    },
    "image-n5-image-t0.7": {
        "label": "Gemini 3 MINIMAL image 384 px, T 0.7",
        "thinking": "minimal", "modality": "image", "temperature": 0.7,
        "pass_usd": MIN_PASS_USD, "pass_anchor": "min-image-unmeasured",
    },
    "image-n5-image-t1.0": {
        "label": "Gemini 3 MINIMAL image 384 px, T 1.0",
        "thinking": "minimal", "modality": "image", "temperature": 1.0,
        "pass_usd": MIN_PASS_USD, "pass_anchor": "min-image-unmeasured",
    },
    "flash-high-image-n5-image-t0.3": {
        "label": "Gemini 3 HIGH image 384 px, T 0.3",
        "thinking": "high", "modality": "image", "temperature": 0.3,
        "pass_usd": HIGH_PASS_USD, "pass_anchor": "high-image-measured",
    },
    "flash-high-image-n5-image-t0.7": {
        "label": "Gemini 3 HIGH image 384 px, T 0.7",
        "thinking": "high", "modality": "image", "temperature": 0.7,
        "pass_usd": HIGH_PASS_USD, "pass_anchor": "high-image-measured",
    },
    "flash-high-image-n5-image-t1.0": {
        "label": "Gemini 3 HIGH image 384 px, T 1.0",
        "thinking": "high", "modality": "image", "temperature": 1.0,
        "pass_usd": HIGH_PASS_USD, "pass_anchor": "high-image-measured",
    },
    "scale-4-optimal-487": {
        "label": "Gemini 3 scale-4-optimal 487",
        "thinking": "high", "modality": "text+image", "temperature": 0.7,
        "pass_usd": HIGH_PASS_USD, "pass_anchor": "high-text-scaled",
    },
    "g384_ov192_g37": {
        "label": "Gemini 3.7 text, GS B geometry",
        "thinking": "low (3.7)", "modality": "text", "temperature": 0.7,
        "pass_usd": G37_PASS_USD, "pass_anchor": "g37-gs-measured",
    },
}

PASS_ANCHORS: dict[str, str] = {
    "min-text-measured": (
        "MIN_PASS_USD 0.266 — ten measured 55-map MINIMAL text T0.7 passes "
        "scaled by 487/8,541 (token-load-audit § 5). This family IS that "
        "family's temperature"
    ),
    "min-text-scaled": (
        "MIN_PASS_USD 0.266, measured at T 0.7 and carried to this "
        "temperature. The HIGH track's T0.3 pass measures 26 % above its T0.7 "
        "pass, so the absolute level is approximate; the ladder's cost RATIO "
        "in K is exact"
    ),
    "high-text-measured": (
        "HIGH_PASS_USD 2.29 — five measured 55-map HIGH text T0.7 passes "
        "scaled by 487/8,541; GS bracket [2.15, 2.64] (token-load-audit § 5)"
    ),
    "high-text-t03-measured": (
        "HIGH_PASS_USD 2.29 is used for comparability, though this family's "
        "own T0.3 HIGH pass measures US$50.82 at deployment = US$2.90 scaled "
        "(token-load-audit § 5 deployment table), 27 % higher"
    ),
    "high-text-scaled": (
        "HIGH_PASS_USD 2.29, measured at T 0.7 text and carried here; "
        "approximate in level, exact in the ladder's K ratio"
    ),
    "high-image-measured": (
        "HIGH_PASS_USD 2.29; the audit's measured HIGH image pass "
        "(US$39.07 at deployment, cached) scales to US$2.23, within 3 %"
    ),
    "min-image-unmeasured": (
        "MIN_PASS_USD 0.266 carried from MINIMAL text. **No MINIMAL image "
        "pass has ever been measured**, and an image prompt is roughly ten "
        "times larger, so this level is the weakest in the table. The "
        "ladder's K ratio is still exact"
    ),
    "g37-gs-measured": (
        "US$1.714/pass — audited from this pool's OWN metas: ten passes at "
        "20.9 M input / 1.07 M output / 3.89 M thinking = US$17.1 flex "
        "(billing-reconciliation-2026-09-11.md line 102) at the 3.7 flex "
        "rates 0.375 / 1.875 (line 41)"
    ),
}


def load(path: Path) -> Any:
    """Read a JSON file."""
    with open(path) as handle:
        return json.load(handle)


def git_head() -> str:
    """Return the repository's short HEAD, or ``"unknown"``."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def headline(eval_path: Path) -> dict[str, Any] | None:
    """Read F1@20, its CI, and tile-MCC from one evaluation."""
    if not eval_path.exists():
        return None
    evaluation = load(eval_path)
    summary = evaluation["summary"]
    row = next(
        entry
        for entry in summary["buffers"]
        if int(entry["buffer_metres"]) == HEADLINE_BUFFER
    )
    mcc = (summary.get("tile_classification") or {}).get("mcc") or {}
    return {
        "f1_20": row.get("f1"),
        "f1_20_ci": row.get("f1_ci"),
        "precision_20": row.get("precision"),
        "recall_20": row.get("recall"),
        "tile_mcc": mcc.get("point"),
    }


def build() -> dict[str, Any]:
    """Assemble the fourteen ladders from every committed and new source."""
    new_scores = load(PHASE2 / "scores.json")
    committed_carried = load(PHASE2 / "committed-carried" / "scores.json")
    membership = load(BOARD / "opmax" / "membership.json")
    conditions = load(BASE_DIR / "results" / "run-conditions.json")

    g37_opmax_path = PHASE2 / "g37-opmax" / "scores.json"
    g37_opmax = load(g37_opmax_path) if g37_opmax_path.exists() else None

    board_by_pool_k = {
        (member["proposer_pool"], member["k"]): member
        for member in membership["members"]
        if (member.get("verifier_config") or {}).get("variant") == "v1"
        and (member.get("verifier_config") or {}).get("instruction_file")
        == "verify_adversarial.md"
    }
    carried_by_pool_k = {
        (cell["proposer_pool"], cell["k"]): cell
        for cell in committed_carried["cells"]
    }

    # The 3.7 family's committed rungs are carried cells; their board-frame
    # evaluations are the `-era2b` register rows.
    g37_carried_eval: dict[int, str] = {}
    g37_carried_n: dict[int, int] = {}
    for condition in conditions["decomposition"][
        "gemini37-screen-2026-08-28"
    ]["conditions"]:
        label = condition.get("label", "")
        if label.endswith("-era2b") and "verified-carried-p0.10" in label:
            g37_carried_eval[int(condition["n_passes"])] = condition["eval_path"]
            if condition.get("n_candidates"):
                g37_carried_n[int(condition["n_passes"])] = condition[
                    "n_candidates"
                ]

    ladders: list[dict[str, Any]] = []
    for pool, meta in FAMILIES.items():
        rungs: list[dict[str, Any]] = []

        # --- K = 1 and K = 3: this run's new rungs -----------------------
        for record in new_scores["rungs"]:
            if record["pool_slug"] != pool:
                continue
            rung: dict[str, Any] = {
                "K": record["n_passes"],
                "source": "phase-2 (new, this run)",
                "candidates": record["candidates"],
                "verifier_flex_usd": record["verifier_flex_usd"],
                "verifier_usd_basis": "measured from this run's meta",
                "verifier_stage": record["verifier_stage"],
                "carried_identical_to_opmax": record.get(
                    "carried_identical_to_opmax"
                ),
                "frames_agree_on_argmax": record.get("frames_agree_on_argmax"),
                "opmax": record.get("opmax"),
                "carried": {
                    "k-equals-K": record.get("carried"),
                    "stride-shell": record.get("carried"),
                },
                "carried_readings_coincide": True,
                "labels": record["labels"],
            }
            rungs.append(rung)

        # --- K = 5 and K = 10: committed rungs ---------------------------
        for k in (5, 10):
            if pool == "g384_ov192_g37":
                carried_eval = g37_carried_eval.get(k)
                carried_metrics = (
                    headline(BASE_DIR / carried_eval) if carried_eval else None
                )
                opmax_metrics = None
                opmax_point = None
                candidates = g37_carried_n.get(k)
                if g37_opmax:
                    stage = next(
                        (
                            entry
                            for entry in g37_opmax["stages"]
                            if entry["k"] == k
                        ),
                        None,
                    )
                    if stage:
                        opmax_metrics = headline(BASE_DIR / stage["eval_path"])
                        opmax_point = {
                            "vote_t": stage["opmax"]["vote_t"],
                            "prob_t": stage["opmax"]["prob_t"],
                            "n_detections": stage["n_detections"],
                            "eval_path": stage["eval_path"],
                            **(opmax_metrics or {}),
                        }
                if candidates is None:
                    union = BASE_DIR / (
                        "outputs/gemini37-screen-2026-08-28/verifier/"
                        f"g384_ov192_g37/union_k{k}.geojson"
                    )
                    candidates = (
                        len(load(union).get("features", []))
                        if union.exists()
                        else None
                    )
                carried_point = (
                    {
                        "vote_t": k,
                        "prob_t": 0.10,
                        "eval_path": carried_eval,
                        **(carried_metrics or {}),
                    }
                    if carried_metrics
                    else None
                )
                rungs.append(
                    {
                        "K": k,
                        "source": "committed (register); opmax derived at US$0",
                        "candidates": candidates,
                        "verifier_flex_usd": (
                            round(candidates * VF_CALL_USD, 4)
                            if candidates
                            else None
                        ),
                        "verifier_usd_basis": "priced at VF_CALL_USD 0.000693",
                        "opmax": opmax_point,
                        "carried": {
                            "k-equals-K": carried_point,
                            "stride-shell": carried_point,
                        },
                        "carried_readings_coincide": True,
                        "carried_note": (
                            "this family's committed carried point is "
                            "(prob_t 0.10, k = K), its own convention"
                        ),
                    }
                )
                continue

            member = board_by_pool_k.get((pool, k))
            carried = carried_by_pool_k.get((pool, k))
            if member is None:
                logger.warning("%s K=%d: no committed board member", pool, k)
                continue
            # The board's cell directory is
            # <run_id>__<label with dots as underscores>, and the label of an
            # on-board opmax cell is <membership label>-opmax.
            cell = (
                f"{member['run_id']}__"
                f"{(member['label'] + '-opmax').replace('.', '_')}"
            )
            opmax_eval = BOARD / "cells" / cell / "evaluation.json"
            opmax_metrics = headline(opmax_eval)
            if opmax_metrics is None:
                logger.warning(
                    "%s K=%d: no board-frame evaluation at %s",
                    pool,
                    k,
                    opmax_eval.relative_to(BASE_DIR),
                )
            carried_readings: dict[str, Any] = {}
            if carried:
                for reading, values in carried["readings"].items():
                    carried_readings[reading] = {
                        "vote_t": values["vote_t"],
                        "prob_t": values["prob_t"],
                        "n_detections": values["n_detections"],
                        "f1_20": values.get("f1_20"),
                        "tile_mcc": values.get("tile_mcc"),
                        "eval_path": values["eval_path"],
                    }
            candidates = (member.get("vintage") or {}).get("n_union")
            rungs.append(
                {
                    "K": k,
                    "source": "committed (signed board); carried derived at US$0",
                    "candidates": candidates,
                    "verifier_flex_usd": (
                        round(candidates * VF_CALL_USD, 4)
                        if candidates
                        else None
                    ),
                    "verifier_usd_basis": "priced at VF_CALL_USD 0.000693",
                    "verifier_stage": member["stage_id"],
                    "condition_id": member["condition_id"],
                    "opmax": (
                        {
                            "vote_t": member["vote_threshold"],
                            "prob_t": member["prob_threshold"],
                            "n_detections": member.get("registry_n"),
                            "eval_path": str(
                                opmax_eval.relative_to(BASE_DIR)
                            ),
                            "cell": cell,
                            **(opmax_metrics or {}),
                        }
                        if opmax_metrics
                        else None
                    ),
                    "carried": carried_readings,
                    "carried_readings_coincide": False,
                }
            )

        rungs.sort(key=lambda rung: rung["K"])
        for rung in rungs:
            proposer = round(rung["K"] * meta["pass_usd"], 4)
            rung["proposer_flex_usd"] = proposer
            rung["all_in_flex_usd"] = (
                round(proposer + rung["verifier_flex_usd"], 4)
                if rung["verifier_flex_usd"] is not None
                else None
            )

        ladders.append(
            {
                "family": meta["label"],
                "proposer_pool": pool,
                "run_id": (
                    "gemini37-screen-2026-08-28"
                    if pool == "g384_ov192_g37"
                    else "pv-diag-384"
                ),
                "thinking_level": meta["thinking"],
                "modality": meta["modality"],
                "temperature": meta["temperature"],
                "pass_usd": meta["pass_usd"],
                "pass_usd_anchor": PASS_ANCHORS[meta["pass_anchor"]],
                "corpus": "4-map-gs",
                "frame": "era2-b-487",
                "frame_file": (
                    "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
                ),
                "reference_file": (
                    "inputs/vectors/references/mounds-reference.geojson"
                ),
                "headline_buffer_m": HEADLINE_BUFFER,
                "r1_verifier": True,
                "n_rungs": len(rungs),
                "rungs": rungs,
            }
        )

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "script": "scripts/build_k_ladder_phase2_tables.py",
        "script_version": __version__,
        "card": "planning/k-ladder-review-2026-09-11.md",
        "costing": "reports/k-ladder-phase2-costing-2026-09-12.md",
        "cost_model": {
            "min_pass_usd": MIN_PASS_USD,
            "high_pass_usd": HIGH_PASS_USD,
            "g37_pass_usd": G37_PASS_USD,
            "vf_call_usd": VF_CALL_USD,
            "basis": "flex (0.5 x list); input 0.25, output+thinking 1.50 per M",
        },
        "n_ladders": len(ladders),
        "ladders": ladders,
    }


def compat_inventory(payload: dict[str, Any]) -> dict[str, Any]:
    """Re-shape the Phase 2 ladders into the Phase-1 inventory schema.

    ``scripts/k_ladder_mcc_test.py`` — the gated instrument that carries
    tile-MCC through the same permutation swap masks as F1 — reads the Phase-1
    ``ladders.json`` schema: one rung per K, each with ``K``, ``condition_id``,
    ``eval_path``, ``f1_headline`` and ``tile_mcc``. This emits that shape so
    the Phase 2 ladders go through the existing instrument rather than a second
    implementation of it.

    **Basis, chosen per family rather than globally.** A ladder must compare
    four rungs at ONE operating point, and only register-resolvable cells can be
    tiered (the instrument resolves ``conditions_compared`` through the
    register):

    * the thirteen ``pv-diag-384`` families use the **opmax** basis at all four
      rungs — K = 1 and K = 3 are this run's registered rows, K = 5 and K = 10
      the signed board's committed ``-opmax`` cells;
    * the 3.7 gold-standard family uses the **carried** basis, because its
      committed K = 5 and K = 10 rungs are registered at their carried point
      and their opmax cells were derived at US$0 without being registered. For
      that family the two points coincide at K = 5 and K = 10 anyway, so the
      basis choice costs nothing.

    A family with fewer than three register-resolvable rungs on one basis is
    omitted, with the reason recorded.

    Args:
        payload: The output of :func:`build`.

    Returns:
        An inventory dict in the Phase-1 schema, plus a ``skipped`` list.
    """
    ladders: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for ladder in payload["ladders"]:
        basis = (
            "carried"
            if ladder["proposer_pool"] == "g384_ov192_g37"
            else "opmax"
        )
        rungs: list[dict[str, Any]] = []
        for rung in ladder["rungs"]:
            point = rung.get(basis)
            if basis == "carried":
                point = (rung.get("carried") or {}).get("k-equals-K")
            if not point or point.get("f1_20") is None:
                continue
            condition_id = rung.get("condition_id")
            if condition_id is None and rung["source"].startswith("phase-2"):
                labels = rung.get("labels") or {}
                label = labels.get(basis)
                # A rung whose two points coincide registers once, under the
                # opmax label; the carried basis must then cite that row.
                if basis == "carried" and rung.get(
                    "carried_identical_to_opmax"
                ):
                    label = labels.get("opmax")
                if label:
                    condition_id = f"{ladder['run_id']}::{label}"
            if basis == "carried" and condition_id is None:
                # The 3.7 family's committed carried rows are the -era2b ones.
                condition_id = (
                    f"{ladder['run_id']}::g37-text-k{rung['K']}"
                    f"-verified-carried-p0.10-k{rung['K']}-era2b"
                )
            if condition_id is None:
                continue
            rungs.append(
                {
                    "K": rung["K"],
                    "condition_id": condition_id,
                    "eval_path": point["eval_path"],
                    "f1_headline": point["f1_20"],
                    "f1_20": point["f1_20"],
                    "tile_mcc": point.get("tile_mcc"),
                    "n_detections": point.get("n_detections"),
                    "vote_threshold": point.get("vote_t"),
                    "prob_threshold": point.get("prob_t"),
                    "cost": {
                        "usd": rung.get("all_in_flex_usd"),
                        "basis": "audited (flex)",
                    },
                }
            )
        if len(rungs) < 3:
            skipped.append(
                {
                    "family": ladder["family"],
                    "basis": basis,
                    "n_resolvable_rungs": len(rungs),
                    "why": (
                        "fewer than three register-resolvable rungs on one "
                        "operating-point basis"
                    ),
                }
            )
            continue
        ladders.append(
            {
                "slug": f"phase2-{ladder['proposer_pool'].replace('.', '-').replace('_', '-').lower()}",
                "family": f"{ladder['family']} [{basis}]",
                "family_base": ladder["family"],
                "operating_point_basis": basis,
                "run_id": ladder["run_id"],
                "proposer_pool": ladder["proposer_pool"],
                "corpus": ladder["corpus"],
                "frame_file": ladder["frame_file"],
                "reference_file": ladder["reference_file"],
                "headline_buffer_m": ladder["headline_buffer_m"],
                "r1_verifier": ladder["r1_verifier"],
                "rungs": rungs,
            }
        )

    return {
        "generated_at_utc": payload["generated_at_utc"],
        "script": "scripts/build_k_ladder_phase2_tables.py",
        "schema_note": (
            "Phase-1 ladders.json schema, emitted so "
            "scripts/k_ladder_mcc_test.py can test these ladders with the "
            "gated board instrument rather than a second implementation of it"
        ),
        "n_ladders": len(ladders),
        "n_skipped": len(skipped),
        "skipped": skipped,
        "ladders": ladders,
    }


def fmt(value: Any, places: int = 4) -> str:
    """Format a number for a Markdown cell, or an em dash for ``None``."""
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{places}f}"
    return str(value)


def tables(payload: dict[str, Any]) -> str:
    """Render the per-family ladder tables and the two summary tables."""
    lines: list[str] = []
    lines.append("# Phase 2: the fourteen new four-rung K ladders")
    lines.append("")
    lines.append(
        "> **GENERATED — do not edit by hand.** Written by "
        "`scripts/build_k_ladder_phase2_tables.py` "
        f"v{__version__}; regenerate rather than correct. Source commit "
        f"`{git_head()}`, generated "
        f"{payload['generated_at_utc']}. Per "
        "`docs/methodology/output-directory-standard.md` § \"Documents in "
        "Revision Policy Scope\" (2026-08-14 ruling), a generated projection "
        "carries a GENERATED banner and a source-commit stamp instead of a "
        "hand changelog. The machine-readable form is `ladders.json`."
    )
    lines.append("")
    lines.append(
        "Assembled from "
        "`phase2/scores.json`, `phase2/committed-carried/scores.json`, "
        "`phase2/g37-opmax/scores.json`, the signed board's `opmax/"
        "membership.json` and its `cells/`, and `phase2/spend-ledger.json`. "
        "Every rung is on the board frame `era2-b-487`, the Gold Standard "
        "curator reference, 14 buffers, 10,000 BCa draws, seed 42, MCC."
    )
    lines.append("")

    for ladder in payload["ladders"]:
        lines.append(f"## {ladder['family']}")
        lines.append("")
        lines.append(
            f"Pool `{ladder['proposer_pool']}`, thinking "
            f"{ladder['thinking_level']}, {ladder['modality']}, "
            f"T {ladder['temperature']}. Proposer pass "
            f"US${ladder['pass_usd']:.3f} — {ladder['pass_usd_anchor']}."
        )
        lines.append("")
        lines.append(
            "| K | source | candidates | opmax (k, p) | opmax F1@20 | "
            "opmax tile-MCC | n | carried k=K F1@20 | carried shell F1@20 | "
            "proposer US$ | verifier US$ | all-in US$ |"
        )
        lines.append(
            "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|"
        )
        for rung in ladder["rungs"]:
            opmax = rung.get("opmax") or {}
            kk = (rung.get("carried") or {}).get("k-equals-K") or {}
            shell = (rung.get("carried") or {}).get("stride-shell") or {}
            point = (
                f"({opmax.get('vote_t')}, {opmax.get('prob_t')})"
                if opmax
                else "—"
            )
            lines.append(
                f"| {rung['K']} | {rung['source']} | "
                f"{fmt(rung.get('candidates'), 0)} | {point} | "
                f"{fmt(opmax.get('f1_20'))} | {fmt(opmax.get('tile_mcc'))} | "
                f"{fmt(opmax.get('n_detections'), 0)} | "
                f"{fmt(kk.get('f1_20'))} | {fmt(shell.get('f1_20'))} | "
                f"{fmt(rung.get('proposer_flex_usd'), 2)} | "
                f"{fmt(rung.get('verifier_flex_usd'), 2)} | "
                f"**{fmt(rung.get('all_in_flex_usd'), 2)}** |"
            )
        lines.append("")

    # --- Summary 1: F1 gain and MCC direction -------------------------------
    lines.append("## Summary: what K buys, per family")
    lines.append("")
    lines.append(
        "| family | K=1 F1@20 | best rung F1@20 (K) | total F1 gain | "
        "K=3 share of the gain | K=1 MCC | best-rung MCC | MCC verdict | "
        "K=3 cost / top-rung cost |"
    )
    lines.append("|---|---:|---|---:|---:|---:|---:|:---:|---:|")
    summary_rows: list[dict[str, Any]] = []
    for ladder in payload["ladders"]:
        by_k = {
            rung["K"]: rung
            for rung in ladder["rungs"]
            if (rung.get("opmax") or {}).get("f1_20") is not None
        }
        if 1 not in by_k or len(by_k) < 2:
            continue
        base = by_k[1]["opmax"]["f1_20"]
        best_k = max(by_k, key=lambda k: by_k[k]["opmax"]["f1_20"])
        best = by_k[best_k]["opmax"]["f1_20"]
        gain = round(best - base, 4)
        at3 = by_k.get(3, {}).get("opmax", {}).get("f1_20")
        share = (
            round((at3 - base) / gain, 3)
            if at3 is not None and gain not in (0, None) and gain != 0
            else None
        )
        mcc1 = by_k[1]["opmax"].get("tile_mcc")
        mccbest = by_k[best_k]["opmax"].get("tile_mcc")
        verdict = "—"
        if mcc1 is not None and mccbest is not None:
            delta = mccbest - mcc1
            verdict = (
                "**down**" if delta < -0.003
                else ("up" if delta > 0.003 else "flat")
            )
        top_cost = by_k[max(by_k)].get("all_in_flex_usd")
        cost3 = by_k.get(3, {}).get("all_in_flex_usd")
        cost_share = (
            round(cost3 / top_cost, 3)
            if cost3 and top_cost
            else None
        )
        lines.append(
            f"| {ladder['family']} | {fmt(base)} | {fmt(best)} (K={best_k}) | "
            f"**{gain:+.4f}** | "
            f"{'—' if share is None else f'{share * 100:.0f} %'} | "
            f"{fmt(mcc1)} | {fmt(mccbest)} | {verdict} | "
            f"{'—' if cost_share is None else f'{cost_share * 100:.0f} %'} |"
        )
        summary_rows.append(
            {
                "family": ladder["family"],
                "f1_k1": base,
                "f1_best": best,
                "best_k": best_k,
                "gain": gain,
                "share_at_k3": share,
                "mcc_k1": mcc1,
                "mcc_best": mccbest,
                "mcc_verdict": verdict.replace("*", ""),
                "cost_share_at_k3": cost_share,
            }
        )
    lines.append("")

    # --- Summary 2: efficient rungs -----------------------------------------
    lines.append("## Pareto: the efficient rungs of each new ladder")
    lines.append("")
    lines.append(
        "A rung is efficient when no cheaper rung of the same ladder scores as "
        "well at the sweep-optimal point."
    )
    lines.append("")
    lines.append("| family | efficient rungs (K @ US$ → F1@20) |")
    lines.append("|---|---|")
    for ladder in payload["ladders"]:
        points = sorted(
            (
                (rung["K"], rung["all_in_flex_usd"], rung["opmax"]["f1_20"])
                for rung in ladder["rungs"]
                if rung.get("all_in_flex_usd") is not None
                and (rung.get("opmax") or {}).get("f1_20") is not None
            ),
            key=lambda triple: triple[1],
        )
        efficient = []
        best_so_far = float("-inf")
        for k, usd, f1 in points:
            if f1 > best_so_far:
                efficient.append(f"{k} @ ${usd:.2f} → {f1:.4f}")
                best_so_far = f1
        lines.append(
            f"| {ladder['family']} | "
            f"{'; '.join(efficient) if efficient else '—'} |"
        )
    lines.append("")
    payload["summary"] = summary_rows
    return "\n".join(lines) + "\n"


def figure(payload: dict[str, Any], out: Path) -> None:
    """Cost against F1@20 at the sweep-optimal point, one line per family."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.0, 6.0))
    markers = ["o", "s", "^", "v", "D", "P", "X", "*", "<", ">", "h", "p", "8", "d"]
    for index, ladder in enumerate(payload["ladders"]):
        points = sorted(
            (
                (rung["K"], rung["all_in_flex_usd"], rung["opmax"]["f1_20"])
                for rung in ladder["rungs"]
                if rung.get("all_in_flex_usd") is not None
                and (rung.get("opmax") or {}).get("f1_20") is not None
            )
        )
        if len(points) < 2:
            continue
        xs = [point[1] for point in points]
        ys = [point[2] for point in points]
        style = "--" if ladder["modality"] == "image" else "-"
        ax.plot(
            xs,
            ys,
            style,
            marker=markers[index % len(markers)],
            linewidth=1.3,
            markersize=5.5,
            label=ladder["family"].replace("Gemini 3 ", "").replace(
                "Gemini 3.7 ", "3.7 "
            ),
        )
        for k, x, y in points:
            ax.annotate(
                f"{k}",
                (x, y),
                textcoords="offset points",
                xytext=(4, -8),
                fontsize=7,
            )
    ax.set_xscale("log")
    ax.set_xlabel(
        "Audited all-in cost per rung, US$ (flex, gold standard), log scale"
    )
    ax.set_ylabel("F1@20 on the board frame, sweep-optimal point")
    ax.set_title(
        "Pass count against cost: the fourteen four-rung ladders Phase 2 "
        "completed"
    )
    ax.grid(True, which="both", alpha=0.25, linewidth=0.6)
    ax.legend(fontsize=7, loc="lower right", ncol=2, framealpha=0.9)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Assemble the fourteen new four-rung K ladders"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--no-figure", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    payload = build()
    markdown = tables(payload)
    PHASE2.mkdir(parents=True, exist_ok=True)
    with open(PHASE2 / "ladders.json", "w") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    with open(PHASE2 / "ladder-tables.md", "w") as handle:
        handle.write(markdown)

    compat = compat_inventory(payload)
    with open(PHASE2 / "ladders-compat.json", "w") as handle:
        json.dump(compat, handle, indent=2)
        handle.write("\n")
    logger.info(
        "compat inventory: %d ladder(s) testable, %d skipped -> %s",
        compat["n_ladders"],
        compat["n_skipped"],
        (PHASE2 / "ladders-compat.json").relative_to(BASE_DIR),
    )
    for entry in compat["skipped"]:
        logger.warning(
            "  skipped %s (%s basis, %d rung(s)): %s",
            entry["family"],
            entry["basis"],
            entry["n_resolvable_rungs"],
            entry["why"],
        )

    if not args.no_figure:
        figure(payload, FIGURE)

    logger.info("%d ladder(s)", payload["n_ladders"])
    for ladder in payload["ladders"]:
        scored = sum(
            1
            for rung in ladder["rungs"]
            if (rung.get("opmax") or {}).get("f1_20") is not None
        )
        logger.info(
            "  %-40s rungs=%d opmax-scored=%d",
            ladder["family"],
            ladder["n_rungs"],
            scored,
        )


if __name__ == "__main__":
    main()
