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

    **The carried convention, settled by the PI on 2026-09-13.** Of the two
    readings, **the stride ladder's own vote shell** (k = 1 / 3 / 4 / 8 at
    K = 1 / 3 / 5 / 10, the four ``stride-phaseb-2026-08-25`` rungs' own ``k``
    column) is **the carried point**; the literal ``k = K`` reading of ruling
    R2's text stays as a **disclosed column** beside it, because it is what
    several committed cells were built at and dropping it would hide a
    transfer tax of up to −0.2566 F1@20 that a reader may want to see. So the
    table's ``carried F1@20`` column is the shell reading and ``carried F1@20,
    k = K`` is the disclosure; the compatibility inventory tiers on the shell
    reading too. The two coincide at K ≤ 3, so no Phase 2 rung's number moves —
    only K = 5 and K = 10 of the thirteen ``pv-diag-384`` families are affected,
    and for them both readings were already computed and committed
    (``phase2/committed-carried/scores.json``).

    **Cost.** Every cost is at the uniform discounted tier (PI ruling D19,
    amended 2026-10-04) and traces to the passes register through
    ``scripts/lib_frontier_cost.py`` (WP4b,
    ``planning/wp4b-frontier-cost-design-2026-10-04.md``). Every rung's
    verifier leg is measured from this run's own metas at K = 1 and K = 3, and
    priced at ``VF_CALL_USD`` (the Gemini 3 Flash verifier per candidate,
    pooled over the 55-map generalisation campaign's four complete legs) for
    the committed rungs. The proposer leg prices each family at its OWN
    measured GS passes where the register records them (PI ruling
    2026-10-04), which replaced units borrowed across families:

    =====================================  ==========================================
    family                                 pass unit (anchor)
    =====================================  ==========================================
    ten families with recorded GS passes   their own ten passes (``own-gs-measured``)
    the four T 0.7 families (text, image)  the mean of the family's own T0.3 and
                                           T1.0 GS passes (``t07-neighbour-mean``)
    =====================================  ==========================================

    The T0.7 GS pools recorded no tokens (empty batch records). Before
    2026-10-04 the MINIMAL image families borrowed the MINIMAL text unit
    (0.266) and were priced at less than half their measured pass (0.573),
    and (briefly) the T0.7 text families took the 55-map T0.7 measurement,
    about 7 % below their GS neighbours; the pass rate is still constant
    within a family, so each ladder's cost RATIO between rungs is exact.

    **Same assessed area (PI ruling D51, 2026-10-07).** A ladder compares
    rungs meant to differ in K alone, so before anything is written every
    ladder's rungs must be shown to have searched the same area: each rung's
    candidate pool has its assessed area determined from provenance
    (``scripts/lib_assessed_area.py``) and compared on the ladder's frame.
    The build REFUSES (exit 3) when they differ, and refuses (exit 4) when a
    pool's area cannot be determined — unless ``--clip-to-common-area``
    (every reported point is re-scored with its detections clipped to the
    common area, named in the output) or ``--allow-undetermined-area`` is
    given. With both, a ladder whose determined rungs differ has EVERY rung,
    the undetermined ones included, re-scored on the determined rungs'
    common area, and its status says so
    (``clipped-to-common-area-with-undetermined``). The 3.7 GS ladder's
    committed K = 5 and K = 10 unions were clipped to the grid-common
    footprint upstream and its K = 1 and K = 3 unions were not (37.94 km² of
    the board frame between them), which is the case the gate exists for.

    **What a clip publishes (v1.4.0, Astra's review of 2026-10-09,
    finding 1).** Before v1.4.0 a clip attached a nested
    ``clipped_to_common_area`` block to each point and every product still
    published the unclipped scores. Now, when ``--clip-to-common-area`` is
    given, each ladder names its **score basis** in every product (the
    tables, the summary gains, the Pareto rows, the figure's legend, the
    compatibility inventory and ``ladders.json``): a ladder the gate clips
    REPORTS the clipped re-scores in the fields every consumer reads
    (``f1_20``, ``precision_20``, ``recall_20``, ``n_detections``) and
    keeps its original values whole under ``historical_as_evaluated``. The
    fields the clip did not regenerate — the bootstrap interval, tile-MCC
    and its interval, and the evaluation, detection and board-cell paths —
    are WITHHELD on a clipped point (set to ``null`` and listed with the
    reason under ``withheld``), never paired with the clipped estimate. A
    clipped ladder is WITHHELD from the compatibility inventory, because the
    instruments that read it resolve each rung through the register to the
    unclipped evaluation; the inventory says what is missing. A requested
    clip REFUSES (exit 5) when a reported point cannot be re-scored. Without
    the flag nothing here changes: the products are byte-identical to
    v1.3.0's.

Usage::

    python scripts/build_k_ladder_phase2_tables.py [--clip-to-common-area]

Outputs:
    results/k-ladder-2026-09-12/phase2/ladders.json
    results/k-ladder-2026-09-12/phase2/ladder-tables.md
    results/k-ladder-2026-09-12/phase2/ladders-compat.json
    results/k-ladder-2026-09-12/figures/k-ladder-pareto-phase2.png

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_assessed_area import (  # noqa: E402
    COMMON_AREA_CLIP_NAME,
    DEFAULT_TOLERANCE_KM2,
    EXIT_AREA_MISMATCH,
    EXIT_AREA_UNDETERMINED,
    METHOD_UNDETERMINED,
    AssessedArea,
    AssessedAreaMismatchError,
    AssessedAreaUndeterminedError,
    add_area_gate_arguments,
    compare_assessed_areas,
    determine_assessed_area,
    rescore_clipped_evaluation,
)
from scripts.lib_frontier_cost import gs_units, phase2_pass_units  # noqa: E402

logger = logging.getLogger(__name__)

#: 1.4.0 (2026-10-10): a clip is the reported basis in every product, the
#: unregenerated fields are withheld, and a point the clip cannot re-score
#: refuses (Astra's review of 2026-10-09, finding 1); 1.3.0 (2026-10-07): the
#: D51 assessed-area gate; 1.2.1: shares rounded once (D27); 1.2.0: costs from
#: the register.
__version__ = "1.4.0"

#: The score basis of a ladder the D51 gate clipped: every reported point is
#: re-scored with its detections clipped to the area common to all rungs.
BASIS_CLIPPED = COMMON_AREA_CLIP_NAME

#: The score basis of a ladder reported as its cells were evaluated. Under a
#: clip it is also the name of the HISTORICAL basis a clipped point keeps.
BASIS_AS_EVALUATED = "as-evaluated"

#: Where a clipped point keeps its original (as-evaluated, unclipped) values.
HISTORICAL_KEY = "historical_as_evaluated"

#: The fields of a point that describe its as-evaluated cell and that a clip
#: does not regenerate, each with the reason it is withheld on a clipped point.
#: Pairing any of them with a clipped estimate would present an old interval,
#: tile metric or evaluation as though it belonged to the clipped score.
NOT_REGENERATED_BY_CLIP: dict[str, str] = {
    "f1_20_ci": "the bootstrap interval of the unclipped cell; not regenerated on "
                "the clipped detections",
    "tile_mcc": "tile-MCC of the unclipped cell's tile table; not regenerated on "
                "the clipped detections",
    "tile_mcc_ci": "the interval of the unclipped tile-MCC; not regenerated",
    "tile_mcc_raw": "the unclipped cell's raw tile-MCC; not regenerated",
    "eval_path": "the unclipped cell's evaluation; no evaluation of the clipped "
                 "detections exists (the re-score read its inputs: "
                 "rescored_from_eval_path)",
    "detections": "the unclipped cell's materialised detections; the clipped "
                  "detections were scored in memory and not written",
    "cell": "the signed board's unclipped cell directory",
}

#: Vocabulary-withholding notes that describe the unclipped tile-MCC; on a
#: clipped point they move to the historical record with the value they explain.
_HISTORICAL_ONLY = ("tile_mcc_withheld", "tile_mcc_withheld_why")

#: Exit code when a requested clip cannot re-score a reported point.
EXIT_CLIP_RESCORE_FAILED = 5

#: The marker every clip re-score refusal carries (``main`` exits 5 on it).
CLIP_RESCORE_FAILED = "CLIP RE-SCORE FAILED"

#: Which of the two readings of "the carried point" the tables REPORT, settled
#: by the PI on 2026-09-13: the gold-standard stride ladder's own vote shell
#: (k = 1 / 3 / 4 / 8 at K = 1 / 3 / 5 / 10). The other reading, ruling R2's
#: literal ``k = K``, stays in the tables as a disclosed column and in
#: ``phase2/committed-carried/scores.json`` in full. They coincide at K <= 3.
CARRIED_READING = "stride-shell"

#: The reading disclosed beside it, never as the headline.
CARRIED_READING_DISCLOSED = "k-equals-K"

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

# The GS-scale units at the uniform discounted tier (PI ruling D19, amended
# 2026-10-04), from the passes register (scripts/lib_frontier_cost.gs_units),
# shared with scripts/build_pareto_v2.py. They replaced 0.266 / 2.29 / 1.714 /
# 0.000693, which they reproduce within 0.4 % (WP4b).
_GS_UNITS = gs_units()
MIN_PASS_USD = _GS_UNITS["min_pass"].usd
HIGH_PASS_USD = _GS_UNITS["high_pass"].usd
G37_PASS_USD = _GS_UNITS["g37_pass"].usd
VF_CALL_USD = _GS_UNITS["vf_call"].usd
HEADLINE_BUFFER = 20

#: Per family: display label, thinking level, modality, the per-pass proposer
#: cost and how well anchored it is.
FAMILIES: dict[str, dict[str, Any]] = {
    "flash-minimal-text-n30-t07-text-t0.3": {
        "label": "Gemini 3 MINIMAL text 384 px, T 0.3",
        "thinking": "minimal", "modality": "text", "temperature": 0.3,
    },
    "flash-minimal-text-n30-t07-text-t0.7": {
        "label": "Gemini 3 MINIMAL text 384 px, T 0.7",
        "thinking": "minimal", "modality": "text", "temperature": 0.7,
    },
    "flash-minimal-text-n30-t07-text-t1.0": {
        "label": "Gemini 3 MINIMAL text 384 px, T 1.0",
        "thinking": "minimal", "modality": "text", "temperature": 1.0,
    },
    "flash-high-text-n5-text-t0.3": {
        "label": "Gemini 3 HIGH text 384 px, T 0.3",
        "thinking": "high", "modality": "text", "temperature": 0.3,
    },
    "flash-high-text-n5-text-t0.7": {
        "label": "Gemini 3 HIGH text 384 px, T 0.7",
        "thinking": "high", "modality": "text", "temperature": 0.7,
    },
    "flash-high-text-n5-text-t1.0": {
        "label": "Gemini 3 HIGH text 384 px, T 1.0",
        "thinking": "high", "modality": "text", "temperature": 1.0,
    },
    "image-n5-image-t0.3": {
        "label": "Gemini 3 MINIMAL image 384 px, T 0.3",
        "thinking": "minimal", "modality": "image", "temperature": 0.3,
    },
    "image-n5-image-t0.7": {
        "label": "Gemini 3 MINIMAL image 384 px, T 0.7",
        "thinking": "minimal", "modality": "image", "temperature": 0.7,
    },
    "image-n5-image-t1.0": {
        "label": "Gemini 3 MINIMAL image 384 px, T 1.0",
        "thinking": "minimal", "modality": "image", "temperature": 1.0,
    },
    "flash-high-image-n5-image-t0.3": {
        "label": "Gemini 3 HIGH image 384 px, T 0.3",
        "thinking": "high", "modality": "image", "temperature": 0.3,
    },
    "flash-high-image-n5-image-t0.7": {
        "label": "Gemini 3 HIGH image 384 px, T 0.7",
        "thinking": "high", "modality": "image", "temperature": 0.7,
    },
    "flash-high-image-n5-image-t1.0": {
        "label": "Gemini 3 HIGH image 384 px, T 1.0",
        "thinking": "high", "modality": "image", "temperature": 1.0,
    },
    "scale-4-optimal-487": {
        "label": "Gemini 3 scale-4-optimal 487",
        "thinking": "high", "modality": "text+image", "temperature": 0.7,
    },
    "g384_ov192_g37": {
        "label": "Gemini 3.7 text, GS B geometry",
        "thinking": "low (3.7)", "modality": "text", "temperature": 0.7,
    },
}

# Each family's pass unit is set from the passes register (PI ruling
# 2026-10-04, WP4b): its own measured GS passes where recorded, otherwise the
# anchors below. ``data/pricing/frontier-configurations.json``
# ``k_ladder_phase2_pass_units``; ``scripts/lib_frontier_cost.phase2_pass_units``.
_PASS_UNITS = phase2_pass_units()
for _family, _meta in FAMILIES.items():
    _unit, _anchor = _PASS_UNITS[_family]
    _meta["pass_usd"], _meta["pass_anchor"] = _unit.usd, _anchor

PASS_ANCHORS: dict[str, str] = {
    "own-gs-measured": (
        "the family's own ten GS passes from the passes register, re-priced at "
        "the uniform discounted tier (PI ruling D19, amended 2026-10-04)"
    ),
    "t07-neighbour-mean": (
        "ESTIMATED as the plain mean of the same family's own T0.3 and T1.0 GS "
        "passes (not a linear interpolation at T 0.7), because its T0.7 GS "
        "passes recorded no tokens (PI ruling 2026-10-04: text and image alike, "
        "so every Phase 2 family rests on GS measurements). The two neighbours "
        "differ by 1.7 % (MINIMAL text), 23 % (HIGH text), 0.3 % (MINIMAL "
        "image) and 18 % (HIGH image)"
    ),
}


#: Cells whose ``source_tile`` vocabulary does not match the scoring frame's
#: tile names have a MEANINGLESS tile-MCC, because
#: ``lib_advanced_metrics.calculate_tile_classification`` matches detections to
#: tiles by that string rather than geometrically. Their F1 is unaffected BY THE
#: VOCABULARY (point matching is geometric) — though until ruling D50 it was
#: affected by the separate per-sheet detection SCOPE, which kept out-of-frame
#: detections as false positives (``reports/frames-blast-radius-2026-10-07.md``
#: § 5.1). This file records the per-cell verdict; any cell that is not
#: ``MATCH`` has its tile-MCC withheld rather than printed.
TILE_VOCAB_JSON = PHASE2 / "tile-vocabulary-match.json"


def load(path: Path) -> Any:
    """Read a JSON file."""
    with open(path) as handle:
        return json.load(handle)


def tile_mcc_verdicts() -> dict[str, str]:
    """Map each materialised cell's filename to its tile-vocabulary verdict."""
    if not TILE_VOCAB_JSON.exists():
        logger.warning(
            "%s absent — tile-MCC is reported unconditionally. Run "
            "scripts/check_tile_vocabulary_match.py so a vocabulary mismatch "
            "cannot pass as a measurement",
            TILE_VOCAB_JSON.relative_to(BASE_DIR),
        )
        return {}
    return {
        Path(cell["detections"]).name: cell["verdict"]
        for cell in load(TILE_VOCAB_JSON)["cells"]
    }


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


#: Where the 3.7 GS family's committed K = 5 and K = 10 unions sit.
G37_UNION = (
    "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/union_k{k}.geojson"
)


def _r1_board_members() -> dict[tuple[str, int], dict[str, Any]]:
    """The signed board's R1 (v1, adversarial) members, keyed by (pool, K)."""
    membership = load(BOARD / "opmax" / "membership.json")
    return {
        (member["proposer_pool"], member["k"]): member
        for member in membership["members"]
        if (member.get("verifier_config") or {}).get("variant") == "v1"
        and (member.get("verifier_config") or {}).get("instruction_file")
        == "verify_adversarial.md"
    }


def committed_sibling_pools(pool: str) -> dict[int, str]:
    """The candidate pools of a family's committed K = 5 and K = 10 rungs.

    Used by the D51 assessed-area gate here and by the sweeps that buy the
    K = 1 and K = 3 rungs (``score_k_ladder_phase2_rungs.py``), so both
    compare against the same siblings.

    Args:
        pool: The family's proposer pool slug (a key of :data:`FAMILIES`).

    Returns:
        ``{K: union path}`` for whichever committed rungs record a union.
    """
    if pool == "g384_ov192_g37":
        return {k: G37_UNION.format(k=k) for k in (5, 10)}
    members = _r1_board_members()
    out: dict[int, str] = {}
    for k in (5, 10):
        union = ((members.get((pool, k)) or {}).get("vintage") or {}).get("union")
        if union:
            out[k] = union
    return out


def new_rung_pools(pool: str) -> dict[int, str]:
    """The candidate pools of a family's Phase 2 K = 1 and K = 3 rungs.

    Args:
        pool: The family's proposer pool slug.

    Returns:
        ``{K: union path}`` from ``phase2/operating-points.json`` (empty when
        the rungs have not been prepared).
    """
    points_path = PHASE2 / "operating-points.json"
    if not points_path.exists():
        return {}
    return {
        entry["n_passes"]: entry["union"]
        for entry in load(points_path)["rungs"]
        if entry["pool_slug"] == pool and entry.get("union")
    }


def build() -> dict[str, Any]:
    """Assemble the fourteen ladders from every committed and new source."""
    new_scores = load(PHASE2 / "scores.json")
    committed_carried = load(PHASE2 / "committed-carried" / "scores.json")
    membership = load(BOARD / "opmax" / "membership.json")
    conditions = load(BASE_DIR / "results" / "run-conditions.json")

    verdicts = tile_mcc_verdicts()

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
                # The candidate pool, for the D51 assessed-area gate in main().
                "pool": new_rung_pools(pool).get(record["n_passes"]),
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
                union = BASE_DIR / G37_UNION.format(k=k)
                if candidates is None:
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
                        "verifier_usd_basis": (
                            f"priced at VF_CALL_USD {VF_CALL_USD:.7f} "
                            "(register, D19)"
                        ),
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
                        "pool": str(union.relative_to(BASE_DIR)),
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
                    "verifier_usd_basis": (
                        f"priced at VF_CALL_USD {VF_CALL_USD:.7f} "
                        "(register, D19)"
                    ),
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
                    "pool": committed_sibling_pools(pool).get(k),
                }
            )

        rungs.sort(key=lambda rung: rung["K"])

        # Withhold tile-MCC wherever the cell's source_tile vocabulary is not
        # the frame's. Printing 0.13 beside a sibling's 0.77 would invite a
        # reading of "K destroys tile discrimination" from an instrument
        # artefact.
        for rung in rungs:
            for point_name in ("opmax", "carried"):
                points = []
                if point_name == "opmax" and rung.get("opmax"):
                    points = [rung["opmax"]]
                elif point_name == "carried":
                    points = [
                        values
                        for values in (rung.get("carried") or {}).values()
                        if values
                    ]
                for values in points:
                    detections = values.get("detections")
                    if not detections:
                        continue
                    verdict = verdicts.get(Path(detections).name)
                    if verdict and verdict != "MATCH":
                        values["tile_mcc_withheld"] = verdict
                        values["tile_mcc_withheld_why"] = (
                            "the cell's source_tile vocabulary is not this "
                            "frame's tile_name vocabulary, and "
                            "calculate_tile_classification matches on that "
                            "string rather than geometrically, so tile-MCC is "
                            "not interpretable here; F1 is unaffected"
                        )
                        values["tile_mcc_raw"] = values.get("tile_mcc")
                        values["tile_mcc"] = None

        for rung in rungs:
            proposer = round(rung["K"] * meta["pass_usd"], 4)
            rung["proposer_flex_usd"] = proposer
            if rung["verifier_flex_usd"] is None:
                # An em dash in the table is honest but quiet, and the usual
                # cause is a ledger that has not caught up with a rung that
                # finished after the last recompute. Say so, so a missing
                # figure cannot be mistaken for a rung that has no cost.
                logger.warning(
                    "%s K=%d: no verifier cost — the spend ledger has no entry "
                    "for this rung (run --recompute-ledger), so its all-in cost "
                    "is left unset rather than guessed",
                    meta["label"],
                    rung["K"],
                )
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
        "carried_convention": {
            "reported": CARRIED_READING,
            "disclosed": CARRIED_READING_DISCLOSED,
            "ruling": "PI, 2026-09-13",
            "note": (
                "The stride ladder's own vote shell (k = 1/3/4/8 at "
                "K = 1/3/5/10) is THE carried point; ruling R2's literal "
                "k = K stays as a disclosed column. The two coincide at "
                "K <= 3, so no Phase 2 rung's number moved — only the "
                "committed K = 5 and K = 10 rungs are affected, and both "
                "readings were already computed in "
                "phase2/committed-carried/scores.json"
            ),
        },
        "cost_model": {
            "min_pass_usd": MIN_PASS_USD,
            "high_pass_usd": HIGH_PASS_USD,
            "g37_pass_usd": G37_PASS_USD,
            "vf_call_usd": VF_CALL_USD,
            "basis": ("the passes register at the uniform discounted tier (PI ruling D19, "
                      "amended 2026-10-04), through scripts/lib_frontier_cost.py; each "
                      "family's pass unit and its anchor are on its ladder (pass_usd, "
                      "pass_usd_anchor)"),
        },
        "n_ladders": len(ladders),
        "ladders": ladders,
    }


def _named_rung_points(rung: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Every operating point a rung reports, each with a name for messages.

    A point shared by two readings (a Phase 2 rung's carried dict maps both
    readings to one object) is listed once, under its first name.

    Args:
        rung: One rung of a ladder.

    Returns:
        ``[(name, point), ...]``: ``opmax`` first, then each carried reading.
    """
    named: list[tuple[str, dict[str, Any]]] = (
        [("opmax", rung["opmax"])] if rung.get("opmax") else []
    )
    seen: set[int] = {id(point) for _, point in named}
    for reading, values in (rung.get("carried") or {}).items():
        if values and id(values) not in seen:
            named.append((f"carried {reading}", values))
            seen.add(id(values))
    return named


def _rung_points(rung: dict[str, Any]) -> list[dict[str, Any]]:
    """Every operating point a rung reports (opmax and each carried reading)."""
    return [point for _, point in _named_rung_points(rung)]


def is_clipped(ladder: dict[str, Any]) -> bool:
    """Whether a ladder's scores are reported on the clipped basis."""
    return (ladder.get("score_basis") or {}).get("reported") == BASIS_CLIPPED


def historical(point: dict[str, Any] | None) -> dict[str, Any]:
    """A point's as-evaluated values: its historical record when clipped, else itself.

    Args:
        point: An operating point, or ``None``.

    Returns:
        The values the cell was evaluated with (empty for ``None``).
    """
    if not point:
        return {}
    return point.get(HISTORICAL_KEY) or point


def report_clipped_point(point: dict[str, Any], clipped: dict[str, Any]) -> None:
    """Make a point's clipped re-score its reported values (D51, in place).

    The point keeps its operating point (``vote_t``, ``prob_t``) and the
    fields every consumer reads now carry the clipped re-score: ``f1_20``,
    ``precision_20``, ``recall_20`` and ``n_detections``. Every field the
    clip did not regenerate (:data:`NOT_REGENERATED_BY_CLIP`) is set to
    ``None`` and listed with its reason under ``withheld``, so no consumer
    pairs the clipped estimate with the unclipped cell's interval, tile
    metric or evaluation. The point's original values are kept whole under
    :data:`HISTORICAL_KEY`, named :data:`BASIS_AS_EVALUATED`.

    Args:
        point: A reported operating point (mutated).
        clipped: Its :func:`rescore_clipped_evaluation` result, named.
    """
    record = copy.deepcopy(point)
    record["score_basis"] = BASIS_AS_EVALUATED
    withheld = {
        key: why for key, why in NOT_REGENERATED_BY_CLIP.items() if key in point
    }
    for key in withheld:
        point[key] = None
    for key in _HISTORICAL_ONLY:
        point.pop(key, None)
    point.update(
        {
            "score_basis": BASIS_CLIPPED,
            "f1_20": clipped["f1"],
            "precision_20": clipped["precision"],
            "recall_20": clipped["recall"],
            "n_detections": clipped["n_detections"],
            "n_removed_by_clip": clipped["n_removed"],
            "rescored_from_eval_path": record.get("eval_path"),
            "withheld": withheld,
            "clipped_to_common_area": clipped,
            HISTORICAL_KEY: record,
        }
    )


def _ladder_basis(comparison_record: dict[str, Any], clipped: bool) -> dict[str, Any]:
    """The ``score_basis`` record a ladder carries when a clip was requested.

    Args:
        comparison_record: The ladder's ``assessed_area`` record.
        clipped: Whether the gate clipped this ladder.

    Returns:
        A JSON-serialisable record naming the reported basis.
    """
    if not clipped:
        return {
            "reported": BASIS_AS_EVALUATED,
            "why": (
                f"a clip was requested and the gate's status is "
                f"{comparison_record.get('status')!r}, so nothing was clipped: "
                "the scores are the cells as evaluated"
            ),
        }
    return {
        "reported": BASIS_CLIPPED,
        "historical": BASIS_AS_EVALUATED,
        "historical_key": HISTORICAL_KEY,
        "status": comparison_record.get("status"),
        "common_area_km2": comparison_record.get("common_area_km2"),
        "frame_area_km2": comparison_record.get("frame_area_km2"),
        "what": (
            "every reported point's F1@20, precision, recall and detection count "
            "are re-scored with its detections clipped to the area every rung "
            "searched and the frame's reference set kept whole (D51 option 1), "
            "at the rung's own unclipped operating point"
        ),
        "withheld": (
            "on every clipped point the fields the clip did not regenerate (the "
            "bootstrap interval, tile-MCC and its interval, and the evaluation, "
            "detection and board-cell paths) are null and listed under "
            f"'withheld'; the as-evaluated values are under '{HISTORICAL_KEY}'"
        ),
        "unchanged": (
            "candidates and the proposer, verifier and all-in costs are each "
            "rung's as-run pool and spend: the clip changes what is scored, not "
            "what was paid"
        ),
        "register": (
            "a rung's condition_id and labels name its registered as-evaluated "
            "cells; no clipped cell is registered"
        ),
    }


def apply_area_gate(
    payload: dict[str, Any],
    *,
    tolerance_km2: float = DEFAULT_TOLERANCE_KM2,
    clip_to_common: bool = False,
    allow_undetermined: bool = False,
) -> list[str]:
    """Confirm each ladder's rungs searched the same area (PI ruling D51).

    For every ladder, each rung's candidate pool (``rung["pool"]``) has its
    assessed area determined from provenance and compared, within the
    ladder's scoring frame, against its siblings'. The ladder gains an
    ``assessed_area`` record either way.

    Where the areas differ and ``clip_to_common`` is set (with
    ``allow_undetermined``, also when some rungs are undetermined: the clip
    is then to the determined rungs' common area), EVERY reported operating
    point is re-scored with the detections outside the common area removed
    and the frame's reference set kept (option 1 of the ruling), at the
    rung's own operating point, and the re-score becomes the point's
    reported value (:func:`report_clipped_point`; the original values are
    kept as the historical basis). A point that cannot be re-scored — it
    names no evaluation, its evaluation names no inputs, or the inputs
    cannot be read — refuses the ladder (:data:`CLIP_RESCORE_FAILED`)
    rather than being skipped, and the ladder's points are left untouched.

    With ``clip_to_common`` the payload and every ladder that passes gain a
    ``score_basis`` record naming the basis the products report. Without it
    neither is added, so the products of an unclipped build are unchanged.

    Args:
        payload: The output of :func:`build` (mutated).
        tolerance_km2: The gate's tolerance.
        clip_to_common: Clip instead of refusing a mismatch.
        allow_undetermined: Record an undetermined pool instead of refusing.

    Returns:
        One refusal message per refused ladder (empty when none refused).
        The caller must not publish a payload with refusals.
    """
    refusals: list[str] = []
    if clip_to_common:
        payload["score_basis"] = {
            "clip_requested": True,
            "clip": COMMON_AREA_CLIP_NAME,
            "ruling": "PI ruling D51 (2026-10-07), option 1",
            "per_ladder": (
                "each ladder's score_basis names its reported basis: "
                f"{BASIS_CLIPPED!r} where the gate clipped it, "
                f"{BASIS_AS_EVALUATED!r} where it found nothing to clip"
            ),
        }
    for ladder in payload["ladders"]:
        areas = []
        for rung in ladder["rungs"]:
            label = f"K = {rung['K']}"
            if rung.get("pool"):
                areas.append(determine_assessed_area(rung["pool"], label=label))
            else:
                areas.append(AssessedArea(
                    label, "", None, None, METHOD_UNDETERMINED,
                    reason="the ladder records no candidate pool for this rung"))
        try:
            comparison = compare_assessed_areas(
                areas, frame=ladder["frame_file"], tolerance_km2=tolerance_km2,
                clip_to_common=clip_to_common, allow_undetermined=allow_undetermined,
            )
        except AssessedAreaMismatchError as exc:
            ladder["assessed_area"] = exc.comparison
            refusals.append(f"{ladder['family']}: {exc}")
            continue
        except AssessedAreaUndeterminedError as exc:
            refusals.append(f"{ladder['family']}: {exc}")
            continue
        ladder["assessed_area"] = comparison.record
        # A clip with undetermined rungs is a clip too: every rung, the
        # undetermined ones included, is re-scored on the determined rungs'
        # common area (finding 1 of the PR #26 review).
        if not comparison.clips:
            if clip_to_common:
                ladder["score_basis"] = _ladder_basis(comparison.record, clipped=False)
            continue
        # Re-score every reported point before changing any, so a refusal
        # leaves the ladder as it was. A point that cannot be re-scored is a
        # refusal, never a silent skip: publishing it unclipped beside its
        # clipped siblings would compare two areas under one basis.
        failures: list[str] = []
        rescored: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for rung in ladder["rungs"]:
            for name, point in _named_rung_points(rung):
                where = f"K = {rung['K']} {name}"
                eval_path = point.get("eval_path")
                if not eval_path:
                    failures.append(f"{where} names no evaluation to re-score")
                    continue
                try:
                    clipped = rescore_clipped_evaluation(
                        eval_path, comparison.common, buffer_m=HEADLINE_BUFFER,
                    )
                except (OSError, ValueError, KeyError) as exc:
                    failures.append(
                        f"{where}: {eval_path} could not be re-scored "
                        f"({type(exc).__name__}: {exc})"
                    )
                    continue
                if clipped is None:
                    failures.append(
                        f"{where}: {eval_path} records no detections, bounds and "
                        "reference to re-score"
                    )
                    continue
                clipped["clip"] = COMMON_AREA_CLIP_NAME
                clipped["at"] = "the rung's own (unclipped) operating point"
                rescored.append((point, clipped))
        if failures:
            refusals.append(
                f"{ladder['family']}: {CLIP_RESCORE_FAILED} — a clip to the common "
                f"area was requested and {len(failures)} reported point(s) cannot "
                f"be re-scored on it: {'; '.join(failures)}"
            )
            continue
        for point, clipped in rescored:
            report_clipped_point(point, clipped)
        ladder["score_basis"] = _ladder_basis(comparison.record, clipped=True)
    return refusals


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
      basis choice costs nothing. The carried basis reads the
      ``stride-shell`` reading, per the PI's ruling of 2026-09-13; for this
      family the two readings coincide at every rung, so the re-sourcing moves
      no number and only makes the basis say which reading it means.

    A family with fewer than three register-resolvable rungs on one basis is
    omitted, with the reason recorded.

    **A clipped ladder is withheld** (D51; Astra's review of 2026-10-09,
    finding 1). The instruments resolve each rung's ``condition_id`` through
    the register to its evaluation and recompute from it, and the register
    holds only the as-evaluated (unclipped) cells. Exporting a clipped
    ladder would have them test the unclipped comparison under the clipped
    ladder's name, so it is listed under ``skipped`` with what is missing
    instead. When a clip was requested, every exported ladder names its
    ``score_basis`` (as evaluated) and the inventory names the request.

    Args:
        payload: The output of :func:`build`.

    Returns:
        An inventory dict in the Phase-1 schema, plus a ``skipped`` list.
    """
    ladders: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    clip_requested = bool(payload.get("score_basis"))

    for ladder in payload["ladders"]:
        basis = (
            "carried"
            if ladder["proposer_pool"] == "g384_ov192_g37"
            else "opmax"
        )
        if is_clipped(ladder):
            skipped.append(_withheld_clipped_ladder(ladder, basis))
            continue
        rungs: list[dict[str, Any]] = []
        for rung in ladder["rungs"]:
            point = rung.get(basis)
            if basis == "carried":
                # The carried point is the stride shell (PI ruling 2026-09-13).
                # For the one family that tiers on the carried basis the two
                # readings coincide at every rung, so this re-sourcing moves no
                # number — it makes the basis say which reading it means.
                point = (rung.get("carried") or {}).get(CARRIED_READING)
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
                        "basis": "uniform discounted tier (D19); see the ladder's "
                                 "pass_usd_anchor",
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
        withheld = [
            rung["K"]
            for rung in ladder["rungs"]
            if (rung.get(basis) or {}).get("tile_mcc_withheld")
            or any(
                (values or {}).get("tile_mcc_withheld")
                for values in (rung.get("carried") or {}).values()
            )
        ]
        if withheld:
            skipped.append(
                {
                    "family": ladder["family"],
                    "basis": basis,
                    "n_resolvable_rungs": len(rungs),
                    "rungs_with_withheld_tile_mcc": sorted(set(withheld)),
                    "why": (
                        "tile-MCC is withheld on some rungs (source_tile "
                        "vocabulary is not the frame's), and the instrument "
                        "runs the F1 and MCC permutations together — tiering "
                        "this ladder would compare a meaningless MCC against a "
                        "sound one and manufacture a large spurious drop. The "
                        "F1 ladder is still reported in full in the tables"
                    ),
                }
            )
            continue
        entry: dict[str, Any] = {
            "slug": "phase2-" + (
                ladder["proposer_pool"].replace(".", "-").replace("_", "-").lower()
            ),
            "family": f"{ladder['family']} [{basis}]",
            "family_base": ladder["family"],
            "operating_point_basis": basis,
            "carried_reading": CARRIED_READING if basis == "carried" else None,
            "run_id": ladder["run_id"],
            "proposer_pool": ladder["proposer_pool"],
            "corpus": ladder["corpus"],
            "frame_file": ladder["frame_file"],
            "reference_file": ladder["reference_file"],
            "headline_buffer_m": ladder["headline_buffer_m"],
            "r1_verifier": ladder["r1_verifier"],
            "rungs": rungs,
        }
        if clip_requested:
            # Named only under a clip request, so an unclipped build's
            # inventory is byte-identical to v1.3.0's.
            entry["score_basis"] = BASIS_AS_EVALUATED
        ladders.append(entry)

    inventory: dict[str, Any] = {
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
    if clip_requested:
        inventory["score_basis"] = {
            "clip_requested": True,
            "exported": BASIS_AS_EVALUATED,
            "note": (
                "a clip to the common assessed area was requested (D51). Every "
                "exported ladder is on the as-evaluated basis, because the "
                "instruments resolve its registered cells; every ladder the gate "
                f"clipped is under 'skipped' with score_basis {BASIS_CLIPPED!r} "
                "and what its export is missing"
            ),
        }
    return inventory


#: What a clipped ladder's export lacks, so the instruments could test it.
CLIPPED_EXPORT_MISSING = (
    "per rung, the reported point's detections materialised as a GeoJSON "
    "clipped to the common assessed area (clip-to-common-assessed-area)",
    "per rung, an evaluation.json of those clipped detections, with its "
    "bootstrap interval and per-tile table regenerated",
    "per rung, a register row (results/run-conditions.json) naming that "
    "evaluation, so that scripts/k_ladder_mcc_test.py and "
    "scripts/k_ladder_mcb.py resolve the clipped cell and not the "
    "as-evaluated one",
)


def _withheld_clipped_ladder(ladder: dict[str, Any], basis: str) -> dict[str, Any]:
    """The ``skipped`` entry of a ladder the D51 gate clipped.

    Args:
        ladder: A ladder whose score basis is :data:`BASIS_CLIPPED`.
        basis: Its operating-point basis (``opmax`` or ``carried``).

    Returns:
        The entry, naming both bases' F1@20 per rung and what is missing.
    """
    rungs = []
    for rung in ladder["rungs"]:
        point = rung.get(basis)
        if basis == "carried":
            point = (rung.get("carried") or {}).get(CARRIED_READING)
        if not point or point.get("f1_20") is None:
            continue
        rungs.append(
            {
                "K": rung["K"],
                "f1_20": point["f1_20"],
                "f1_20_basis": point.get("score_basis", BASIS_AS_EVALUATED),
                "f1_20_as_evaluated_historical": historical(point).get("f1_20"),
            }
        )
    return {
        "family": ladder["family"],
        "basis": basis,
        "score_basis": BASIS_CLIPPED,
        "n_resolvable_rungs": len(rungs),
        "why": (
            "the ladder is reported on the clipped basis (D51), and the "
            "instruments resolve each rung's condition_id through the register "
            "to its as-evaluated (unclipped) evaluation, so an export would test "
            "the unclipped comparison under this ladder's name. Withheld until "
            "the clipped cells exist"
        ),
        "missing": list(CLIPPED_EXPORT_MISSING),
        "rungs": rungs,
    }


def fmt(value: Any, places: int = 4) -> str:
    """Format a number for a Markdown cell, or an em dash for ``None``."""
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{places}f}"
    return str(value)


def pct(ratio: float | None) -> str:
    """Format a ratio as a whole percentage, rounding once, or an em dash.

    The ratio must be the raw quotient, never a value already rounded:
    v1.2.0 rounded the shares to three decimals and then to a whole
    percentage, which turned 0.31491 into 0.315 and then "32 %" (PI
    ruling D27, 2026-10-04).

    Args:
        ratio: A share in [0, 1], or ``None`` when it is undefined.

    Returns:
        ``"31 %"``-style text, or ``"—"`` for ``None``.

    Example:
        >>> pct(7.2405 / 22.9921)
        '31 %'
    """
    if ratio is None:
        return "—"
    return f"{ratio * 100:.0f} %"


def _basis_paragraph() -> str:
    """The paragraph a clip-requested build's tables open with."""
    return (
        "**Score basis.** This build was asked to clip to the common assessed "
        "area (`--clip-to-common-area`, PI ruling D51). Each ladder names its "
        "basis below: a ladder the gate clipped REPORTS clipped re-scores and "
        "keeps its original scores beside them as a historical basis, never as "
        "the reported one; a ladder in which the gate found nothing to clip is "
        "reported as evaluated. The summary and Pareto tables carry each "
        "ladder's basis, and so does the figure's legend. Clipped ladders are "
        "withheld from `ladders-compat.json`, which lists what their export "
        "lacks."
    )


def _ladder_basis_line(ladder: dict[str, Any]) -> str:
    """The line naming one ladder's score basis (clip-requested builds only)."""
    basis = ladder.get("score_basis") or {}
    if not is_clipped(ladder):
        return f"Score basis: **as evaluated** — {basis.get('why', 'not clipped')}."
    return (
        "Score basis: **clipped to the common assessed area** "
        f"(`{BASIS_CLIPPED}`, {fmt(basis.get('common_area_km2'))} km² of the "
        f"frame's {fmt(basis.get('frame_area_km2'))} km²; gate status "
        f"`{basis.get('status')}`). Each F1@20 marked *clipped* is re-scored "
        "with the rung's detections clipped to that area and the frame's "
        "reference set kept whole (D51 option 1), at the rung's own unclipped "
        "operating point; *n* is the clipped detection count. The *as evaluated "
        "(historical)* columns are the original unclipped scores, kept for "
        "comparison, not reported. Tile-MCC, the bootstrap intervals and the "
        "evaluation paths are withheld: they belong to the unclipped cells and "
        "were not regenerated. Candidates and costs are each rung's as-run pool "
        "and spend."
    )


def _clipped_ladder_rows(ladder: dict[str, Any]) -> list[str]:
    """One clipped ladder's table: clipped and historical F1@20 side by side."""
    rows = [
        "| K | source | candidates | opmax (k, p) | opmax F1@20, clipped | "
        "opmax F1@20, as evaluated (historical) | opmax tile-MCC | n, clipped | "
        "carried F1@20, clipped | carried F1@20, as evaluated (historical) | "
        "carried F1@20, k = K (disclosed), clipped | carried F1@20, k = K "
        "(disclosed), as evaluated (historical) | proposer US$ | verifier US$ | "
        "all-in US$ |",
        "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rung in ladder["rungs"]:
        opmax = rung.get("opmax") or {}
        carried = rung.get("carried") or {}
        kk = carried.get(CARRIED_READING_DISCLOSED) or {}
        shell = carried.get(CARRIED_READING) or {}
        point = (
            f"({opmax.get('vote_t')}, {opmax.get('prob_t')})" if opmax else "—"
        )
        rows.append(
            f"| {rung['K']} | {rung['source']} | "
            f"{fmt(rung.get('candidates'), 0)} | {point} | "
            f"{fmt(opmax.get('f1_20'))} | {fmt(historical(opmax).get('f1_20'))} | "
            f"{'withheld' if opmax else '—'} | "
            f"{fmt(opmax.get('n_detections'), 0)} | "
            f"{fmt(shell.get('f1_20'))} | {fmt(historical(shell).get('f1_20'))} | "
            f"{fmt(kk.get('f1_20'))} | {fmt(historical(kk).get('f1_20'))} | "
            f"{fmt(rung.get('proposer_flex_usd'), 2)} | "
            f"{fmt(rung.get('verifier_flex_usd'), 2)} | "
            f"**{fmt(rung.get('all_in_flex_usd'), 2)}** |"
        )
    return rows


def _gain(by_k: dict[int, dict[str, Any]], *, as_evaluated: bool = False,
          ) -> tuple[float, float, int, float]:
    """K = 1's F1@20, the best rung's F1@20 and K, and the gain between them.

    Args:
        by_k: ``{K: rung}`` for the rungs with an opmax F1@20, K = 1 among them.
        as_evaluated: Read each point's historical (as-evaluated) F1@20
            instead of its reported one.

    Returns:
        ``(base, best, best_k, gain)``, the gain rounded to four decimals.
    """
    def f1(k: int) -> float:
        point = by_k[k]["opmax"]
        return (historical(point) if as_evaluated else point)["f1_20"]

    base = f1(1)
    best_k = max(by_k, key=f1)
    best = f1(best_k)
    return base, best, best_k, round(best - base, 4)


def tables(payload: dict[str, Any]) -> str:
    """Render the per-family ladder tables and the two summary tables.

    When the payload records a clip request (``payload["score_basis"]``),
    every table names each ladder's score basis and a clipped ladder's
    F1@20 is its clipped re-score, with the as-evaluated value beside it as
    the historical basis. Without one the text is exactly v1.3.0's.
    """
    clip_requested = bool(payload.get("score_basis"))
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
    if clip_requested:
        lines.append(_basis_paragraph())
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
        if clip_requested:
            lines.append(_ladder_basis_line(ladder))
            lines.append("")
        if is_clipped(ladder):
            lines.extend(_clipped_ladder_rows(ladder))
            lines.append("")
            continue
        lines.append(
            "| K | source | candidates | opmax (k, p) | opmax F1@20 | "
            "opmax tile-MCC | n | carried F1@20 | carried F1@20, k = K "
            "(disclosed) | proposer US$ | verifier US$ | all-in US$ |"
        )
        lines.append(
            "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|"
        )
        for rung in ladder["rungs"]:
            opmax = rung.get("opmax") or {}
            carried = rung.get("carried") or {}
            kk = carried.get(CARRIED_READING_DISCLOSED) or {}
            shell = carried.get(CARRIED_READING) or {}
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
                # The stride shell IS the carried point (PI ruling 2026-09-13);
                # k = K follows it as the disclosed column.
                f"{fmt(shell.get('f1_20'))} | {fmt(kk.get('f1_20'))} | "
                f"{fmt(rung.get('proposer_flex_usd'), 2)} | "
                f"{fmt(rung.get('verifier_flex_usd'), 2)} | "
                f"**{fmt(rung.get('all_in_flex_usd'), 2)}** |"
            )
        lines.append("")

    # --- Summary 1: F1 gain and MCC direction -------------------------------
    lines.append("## Summary: what K buys, per family")
    lines.append("")
    if clip_requested:
        lines.append(
            "| family | score basis | K=1 F1@20 | best rung F1@20 (K) | total F1 "
            "gain | K=3 share of the gain | K=1 MCC | best-rung MCC | MCC verdict | "
            "K=3 cost / top-rung cost | total F1 gain, as evaluated (historical) |"
        )
        lines.append("|---|---|---:|---|---:|---:|---:|---:|:---:|---:|---|")
    else:
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
        clipped = is_clipped(ladder)
        base, best, best_k, gain = _gain(by_k)
        at3 = by_k.get(3, {}).get("opmax", {}).get("f1_20")
        # Each share is rendered from its raw quotient and stored to four
        # decimals; rounding before rendering double-rounds (D27).
        share_raw = (
            (at3 - base) / gain
            if at3 is not None and gain not in (0, None) and gain != 0
            else None
        )
        share = None if share_raw is None else round(share_raw, 4)
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
        cost_share_raw = cost3 / top_cost if cost3 and top_cost else None
        cost_share = (
            None if cost_share_raw is None else round(cost_share_raw, 4)
        )
        row: dict[str, Any] = {
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
        if not clip_requested:
            lines.append(
                f"| {ladder['family']} | {fmt(base)} | {fmt(best)} (K={best_k}) | "
                f"**{gain:+.4f}** | "
                f"{pct(share_raw)} | "
                f"{fmt(mcc1)} | {fmt(mccbest)} | {verdict} | "
                f"{pct(cost_share_raw)} |"
            )
            summary_rows.append(row)
            continue
        # A clip-requested build names each row's basis; a clipped ladder's
        # tile-MCC was not regenerated, so its MCC cells say so.
        row["score_basis"] = BASIS_CLIPPED if clipped else BASIS_AS_EVALUATED
        historical_cell = "— (not clipped)"
        mcc_cells = f"{fmt(mcc1)} | {fmt(mccbest)} | {verdict}"
        if clipped:
            row["mcc_verdict"] = "withheld"
            mcc_cells = "withheld | withheld | withheld"
            h_base, h_best, h_best_k, h_gain = _gain(by_k, as_evaluated=True)
            row[HISTORICAL_KEY] = {
                "f1_k1": h_base, "f1_best": h_best, "best_k": h_best_k,
                "gain": h_gain,
            }
            historical_cell = f"{h_gain:+.4f} (K=1 {fmt(h_base)}, K={h_best_k} {fmt(h_best)})"
        lines.append(
            f"| {ladder['family']} | {row['score_basis']} | {fmt(base)} | "
            f"{fmt(best)} (K={best_k}) | **{gain:+.4f}** | {pct(share_raw)} | "
            f"{mcc_cells} | {pct(cost_share_raw)} | {historical_cell} |"
        )
        summary_rows.append(row)
    lines.append("")

    # --- Summary 2: efficient rungs -----------------------------------------
    lines.append("## Pareto: the efficient rungs of each new ladder")
    lines.append("")
    lines.append(
        "A rung is efficient when no cheaper rung of the same ladder scores as "
        "well at the sweep-optimal point."
    )
    lines.append("")
    if clip_requested:
        lines.append(
            "Each row is on its ladder's score basis: a clipped ladder's F1@20 "
            "is its clipped re-score."
        )
        lines.append("")
        lines.append("| family | score basis | efficient rungs (K @ US$ → F1@20) |")
        lines.append("|---|---|---|")
    else:
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
        basis_cell = (
            f"{BASIS_CLIPPED if is_clipped(ladder) else BASIS_AS_EVALUATED} | "
            if clip_requested else ""
        )
        lines.append(
            f"| {ladder['family']} | {basis_cell}"
            f"{'; '.join(efficient) if efficient else '—'} |"
        )
    payload["summary"] = summary_rows
    # A trailing "" plus the joiner's own newline emitted two blank lines at the
    # end of the file, which markdownlint refuses (MD012). One trailing newline.
    return "\n".join(lines) + "\n"


def figure_series(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """The data the figure plots: one line per ladder with two or more points.

    Each line's points are ``(K, all-in US$, F1@20)`` on the ladder's
    reported basis, so a clipped ladder plots its clipped re-scores; its
    legend label says so. ``index`` is the ladder's position in the payload,
    which picks its marker.

    Args:
        payload: The gated payload.

    Returns:
        ``[{"index", "family", "label", "modality", "score_basis",
        "points"}, ...]``.
    """
    series: list[dict[str, Any]] = []
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
        label = ladder["family"].replace("Gemini 3 ", "").replace(
            "Gemini 3.7 ", "3.7 "
        )
        if is_clipped(ladder):
            label += " [clipped]"
        series.append(
            {
                "index": index,
                "family": ladder["family"],
                "label": label,
                "modality": ladder["modality"],
                "score_basis": (
                    BASIS_CLIPPED if is_clipped(ladder) else BASIS_AS_EVALUATED
                ),
                "points": points,
            }
        )
    return series


def figure(payload: dict[str, Any], out: Path) -> None:
    """Cost against F1@20 at the sweep-optimal point, one line per family."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.0, 6.0))
    markers = ["o", "s", "^", "v", "D", "P", "X", "*", "<", ">", "h", "p", "8", "d"]
    for entry in figure_series(payload):
        points = entry["points"]
        xs = [point[1] for point in points]
        ys = [point[2] for point in points]
        style = "--" if entry["modality"] == "image" else "-"
        ax.plot(
            xs,
            ys,
            style,
            marker=markers[entry["index"] % len(markers)],
            linewidth=1.3,
            markersize=5.5,
            label=entry["label"],
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
    ylabel = "F1@20 on the board frame, sweep-optimal point"
    if payload.get("score_basis"):
        ylabel += "\n[clipped]: re-scored on the common assessed area (D51)"
    ax.set_ylabel(ylabel)
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


def _display(path: Path) -> Path:
    """A path relative to the repository when it is inside it, for log lines."""
    try:
        return path.relative_to(BASE_DIR)
    except ValueError:
        return path


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Assemble the fourteen new four-rung K ladders"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--no-figure", action="store_true")
    add_area_gate_arguments(parser)
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    payload = build()
    # PI ruling D51: a ladder compares rungs meant to differ in K alone, so
    # its rungs must have searched the same area. Refuse before anything is
    # written unless the caller asked to clip (or to record undetermined
    # pools as such).
    refusals = apply_area_gate(
        payload,
        tolerance_km2=args.area_tolerance_km2,
        clip_to_common=args.clip_to_common_area,
        allow_undetermined=args.allow_undetermined_area,
    )
    if refusals:
        for message in refusals:
            logger.error("D51 gate REFUSED %s", message)
        if any(CLIP_RESCORE_FAILED in m for m in refusals):
            # A requested clip that cannot re-score every reported point
            # must not publish: exit 5, nothing written.
            raise SystemExit(EXIT_CLIP_RESCORE_FAILED)
        undetermined_only = all("UNDETERMINED" in m for m in refusals)
        raise SystemExit(
            EXIT_AREA_UNDETERMINED if undetermined_only else EXIT_AREA_MISMATCH
        )
    if args.clip_to_common_area:
        clipped = [ladder["family"] for ladder in payload["ladders"] if is_clipped(ladder)]
        logger.warning(
            "score basis: %d ladder(s) REPORTED clipped to the common area (%s), "
            "%d as evaluated; clipped ladders are withheld from the compat "
            "inventory", len(clipped), "; ".join(clipped) or "none",
            len(payload["ladders"]) - len(clipped),
        )
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
        _display(PHASE2 / "ladders-compat.json"),
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
