#!/usr/bin/env python3
"""
The tile-presence presentation: every configuration's tile-MCC optimum, costed.

PI ruling 2026-09-21 (superseding ruling 6c of 2026-09-20) dropped the "MCC
oracle" from the main boards under BOTH definitions. Tile-MCC stays reported
beside micro-F1 @ 50 m at the carried and F1-oracle points, the F1 oracle
stays free over both dimensions, and the tile-MCC optimum moves HERE, into a
separate presentation for the reader who cares about tile presence rather
than detection counts.

Why it is separate
------------------
A tile-MCC optimum is not a companion to an F1 oracle. Tile-MCC asks only
whether a tile was hit at all, so a second or third detection inside an
already-positive tile is free in that currency and costly in F1; lowering the
vote threshold adds exactly that kind of detection. Every one of the r2
board's 23 families therefore puts its UNCONSTRAINED tile-MCC optimum at the
lowest vote count its sweep offers (PI decision log D6a, 2026-09-20; Obs 492),
and eighteen of the eighteen whose sweeps reach a single vote sit at k = 1.
Presented beside an F1 oracle that number reads as a rival configuration.
Presented here, with its vote count in a column of its own and the verifier
pool it would need priced beside it, it reads as what it is: the best a
metric indifferent to over-generation can do, if you are willing to buy the
pool.

What this builds (all of it from COMMITTED sweep records; zero API)
------------------------------------------------------------------
``leaderboard.json`` / ``leaderboard.md``
    One row per configuration — the r2 board's 23 families and the two image
    campaigns' twelve rung x arm cells — at its unconstrained tile-MCC
    optimum: vote count, probability threshold, detections, the full tile
    confusion, tile-MCC, the micro-F1 @ 50 m it costs there, the family's
    CARRIED point's tile-MCC for reference, and the verifier cost of the pool
    the point needs. Sorted by tile-MCC. Every row is an ORACLE: no
    configuration on this table has a calibrated carried point at its tile-MCC
    optimum.

``frontier/frontier.json`` / ``frontier.md`` / ``frontier-<track>.png``
    Per configuration, the ``(micro_f1_50, tile_mcc)`` Pareto-non-dominated
    sweep points — the honest statement of the trade, rather than one end of
    it — with one figure per campaign, all families overlaid, the carried
    point and the F1 oracle marked.

``findings.md``
    What the table is for, the vote-count finding, the cost dimension and the
    E89 caveat.

The cost dimension
------------------
A tile-MCC optimum at k = 1 needs a verifier probability for every candidate
in the union at one vote, not just for the unanimous ones. The pool is read
from the committed sweep CSV — the row at ``prob_t`` 0.0 for that vote count
is exactly "how many candidates have at least k votes" — and priced at the
AUDITED per-candidate rate of that configuration's own verifier leg, via
``scripts/audit_verifier_cost.py`` over the leg's committed metas (the same
auditor the campaigns' post-run reports cite). Where the pool is smaller than
the leg, the configuration INHERITS its probabilities from a larger
verification and the row says so; where it is larger, the point asks for
candidates that were never verified, and the row says that instead.

The drift check
---------------
``--check`` regenerates the selected stage's files in memory from the
committed sweep records (and, for ``costs``, from a fresh run of the cost
auditor), compares them byte for byte with what is committed, and writes
nothing: exit 0 when every file matches, exit 1 with each stale path
logged. It is the guard the register's other generators carry, so a
sweep re-run, a relabel, or a hand edit that leaves ``leaderboard.md``
saying something its inputs no longer say is caught at test time rather
than by a reader. The frontier PNGs are not compared (a rasteriser's
bytes are not a claim); ``frontier.json`` and ``frontier.md`` are.

Usage::

    python scripts/build_tile_presence_board.py --stage costs
    python scripts/build_tile_presence_board.py --stage leaderboard
    python scripts/build_tile_presence_board.py --stage frontier
    python scripts/build_tile_presence_board.py --stage all
    python scripts/build_tile_presence_board.py --stage all --check

Zero API. Run on sapphire.

Created: 2026-09-21 (Session 158)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.final_board_sweeps import (  # noqa: E402
    carried_k_by_family,
    read_sweep_csv,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OUT = PROJECT_ROOT / "results/tile-presence-2026-09-21"
BOARD_HOME = PROJECT_ROOT / "results/55map-final-board-r2-2026-09-06"
G37_HOME = PROJECT_ROOT / "results/gemini37-image-55map-2026-09-13"
G3_HOME = PROJECT_ROOT / "results/gemini3-image-55map-2026-09-16"
COSTS = "verifier-costs.json"
BUFFER_M = 50

#: The verifier leg each configuration's probabilities come from, keyed by the
#: configuration-name prefix and resolved longest-prefix-first. Every path is a
#: verifier STAGE directory holding a ``run.meta.json``; a tuple of two is a
#: leg run in two passes, which ``audit_verifier_cost.py`` sums.
#:
#: Provenance: the text incumbents' two-pass union is
#: ``final_board_sweeps.build_families`` (the original vote >= 4 verification
#: merged with the S104 vote-3 increment under ``DEPLOY``); the stride and 3.7
#: roots are ``stride55_sweep_oracle.RUNS`` and
#: ``gemini37_sweep_oracle.CELLS``; the image legs are the campaign roots of
#: ``gemini37_image_55map_r2.Campaign``.
VOTE3 = "results/deployment-oracle-2026-06-06/vote3-verify"
STRIDE_V = "outputs/stride-55map-2026-08-25/verifier"
LEGS: dict[str, tuple[str, ...]] = {
    "TH7": ("outputs/55maps-text-high-generalisation/verified",
            f"{VOTE3}/55maps-text-high-generalisation/verified"),
    "T03": ("outputs/55maps-text-high-t0.3-generalisation/verified",
            f"{VOTE3}/55maps-text-high-t0.3-generalisation/verified"),
    "TM": ("outputs/55maps-text-min-generalisation/verified",
           f"{VOTE3}/55maps-text-min-generalisation/verified"),
    "IM": ("outputs/55maps-image-generalisation/verified",),
    "UPL": ("outputs/55maps-text-min-n10-uplift/verified-3of10",),
    "A-": (f"{STRIDE_V}/g384_ov128_55map/verify",),
    "B-": (f"{STRIDE_V}/g384_ov192_55map/verify",),
    "ARM1-": ("outputs/gemini37-55map-2026-08-29/verifier/"
              "g384_ov192_55map_g37/verify_arm1",),
    "ARM2-": ("outputs/gemini37-55map-2026-08-29/verifier/"
              "g384_ov192_55map_g37/verify_arm2",),
    "FOURTH-": (f"{STRIDE_V}/g384_ov192_55map/verify_37",),
}
for _k in (1, 3, 5):
    for _a in (1, 2):
        LEGS[f"IMG-ARM{_a}-K{_k}"] = (
            f"outputs/gemini37-image-55map-2026-09-13/verifier/"
            f"g384_ov192_55map_g37img/verify_k{_k}_arm{_a}",)
        LEGS[f"G3IMG-ARM{_a}-K{_k}"] = (
            f"outputs/gemini3-image-55map-2026-09-16/verifier/"
            f"g384_ov192_55map_g3img/verify_k{_k}_arm{_a}",)

#: A leg whose meta records no model of its own needs a rate card named. Only
#: the legs that actually need one are listed, and each says why.
LEG_MODEL: dict[str, str] = {}

#: Audited verifier-leg costs as the campaigns' own post-run reports PUBLISH
#: them, transcribed with their source. These exist because
#: ``scripts/audit_verifier_cost.py`` cannot always reach the truth from the
#: working tree: ``run_pv.py cleanup`` before 2026-09-14 rewrote
#: ``run.meta.json`` with the retry pass's usage only, so a stage whose main
#: pass survives nowhere on disc audits to a LOWER BOUND. The auditor says so
#: rather than guessing, and its own docstring names this campaign's K = 1
#: arm 2 as the worked example (US$0.0153 read against US$7.7028 audited).
#:
#: Where the auditor IS complete it is cross-checked against these figures and
#: must agree to the cent, so neither source can drift from the other
#: unnoticed.
PUBLISHED_USD = "outputs/gemini37-image-55map-2026-09-13/post_run_report.md"
PUBLISHED_USD_G3 = "outputs/gemini3-image-55map-2026-09-16/post_run_report.md"
PUBLISHED_LEG_COST: dict[str, dict[str, Any]] = {
    # gemini37-image-55map-2026-09-13, post_run_report.md section 2 stage
    # table ("K = 1 arm 1", "K = 1 arm 2", "K = 3 arm 1", "K = 3 arm 2",
    # "K = 5 arm 1", "K = 5 arm 2"), read 2026-09-21.
    "IMG-ARM1-K1": {"usd": 4.9626, "candidates": 6985, "source": PUBLISHED_USD},
    "IMG-ARM2-K1": {"usd": 7.7028, "candidates": 6985, "source": PUBLISHED_USD},
    "IMG-ARM1-K3": {"usd": 5.9058, "candidates": 8337, "source": PUBLISHED_USD},
    "IMG-ARM2-K3": {"usd": 9.2650, "candidates": 8337, "source": PUBLISHED_USD},
    "IMG-ARM1-K5": {"usd": 6.4896, "candidates": 9173, "source": PUBLISHED_USD},
    "IMG-ARM2-K5": {"usd": 10.1788, "candidates": 9173,
                    "source": PUBLISHED_USD},
    # gemini3-image-55map-2026-09-16, post_run_report.md section 2 stage
    # table, read 2026-09-21. Its "Six verifier legs" row totals US$189.4717
    # over 209,920 verifications, which these six reproduce.
    "G3IMG-ARM1-K1": {"usd": 15.7559, "candidates": 22785,
                      "source": PUBLISHED_USD_G3},
    "G3IMG-ARM2-K1": {"usd": 25.3978, "candidates": 22785,
                      "source": PUBLISHED_USD_G3},
    "G3IMG-ARM1-K3": {"usd": 25.1020, "candidates": 36389,
                      "source": PUBLISHED_USD_G3},
    "G3IMG-ARM2-K3": {"usd": 40.5813, "candidates": 36389,
                      "source": PUBLISHED_USD_G3},
    "G3IMG-ARM1-K5": {"usd": 31.5422, "candidates": 45786,
                      "source": PUBLISHED_USD_G3},
    "G3IMG-ARM2-K5": {"usd": 51.0925, "candidates": 45786,
                      "source": PUBLISHED_USD_G3},
}

#: How close an auditor run and a published figure must be to be called the
#: same number. One cent: both are quoted to four decimal places.
COST_AGREEMENT_USD = 0.01

#: Cost bases that may be used to price a pool. ``unaudited`` may not: a
#: cleanup-overwritten stage yields a lower bound, and multiplying a lower
#: bound by a pool size produces a number that looks like a cost and is not.
PRICEABLE = ("audited", "published")


@dataclass(frozen=True)
class Track:
    """One source of sweep records.

    Attributes:
        key: Short name used in filenames and the ``track`` column.
        title: Human name for the documents.
        home: Results home holding ``sweeps.json`` and ``sweep_<name>.csv``.
        record_key: ``families`` (the board) or ``rungs`` (a campaign).
        optimum_key: The record field holding the UNCONSTRAINED tile-MCC
            optimum. The board writes ``mcc_argmax``; the campaigns write
            ``mcc_argmax_unconstrained`` beside their carried-k selection.
    """

    key: str
    title: str
    home: Path
    record_key: str
    optimum_key: str
    extra: dict = field(default_factory=dict)


TRACKS = (
    Track("board", "r2 55-map board", BOARD_HOME, "families", "mcc_argmax"),
    Track("g37-image", "Gemini 3.7 image campaign", G37_HOME, "rungs",
          "mcc_argmax_unconstrained"),
    Track("g3-image", "Gemini 3 image campaign", G3_HOME, "rungs",
          "mcc_argmax_unconstrained"),
)


# ---------------------------------------------------------------------------
# Pure helpers (these are what tests/test_tile_presence_board.py pins).
# ---------------------------------------------------------------------------


def leg_for(config: str) -> tuple[str, ...] | None:
    """The verifier stage directories one configuration's pool was verified in.

    Longest prefix wins, so ``IMG-ARM2-K3`` takes its own leg rather than a
    shorter family prefix that happens to match.

    Args:
        config: Configuration name, e.g. ``B-N10`` or ``G3IMG-ARM1-K5``.

    Returns:
        The stage directories, or ``None`` when no prefix matches.
    """
    matches = [p for p in LEGS if config.startswith(p)]
    if not matches:
        return None
    return LEGS[max(matches, key=len)]


def pool_at_vote(rows: list[dict], min_votes: int) -> int | None:
    """How many candidates carry at least ``min_votes`` votes.

    Read off the sweep itself rather than recounted: the row at ``prob_t``
    0.0 keeps every candidate whose vote count clears the threshold, so its
    ``n_detections`` IS the pool a point at that vote count draws on. Using
    the committed CSV keeps the pool on the same evidence as the optimum.

    Args:
        rows: One configuration's sweep rows.
        min_votes: The vote count to size the pool at.

    Returns:
        The pool size, or ``None`` if the sweep has no zero-threshold row at
        that vote count (a grid built only from observed probabilities).
    """
    for row in rows:
        if int(row["min_votes"]) == int(min_votes) \
                and float(row["prob_t"]) == 0.0:
            return int(row["n_detections"])
    return None


def sweep_row_at(rows: list[dict], prob_t: float,
                 min_votes: int) -> dict | None:
    """The sweep row at one operating point, or ``None``."""
    for row in rows:
        if (abs(float(row["prob_t"]) - float(prob_t)) < 1e-9
                and int(row["min_votes"]) == int(min_votes)):
            return row
    return None


def pareto_front(rows: list[dict]) -> list[dict]:
    """The ``(micro_f1_50, tile_mcc)`` non-dominated points, F1-descending.

    A point is dominated when another point is at least as good on BOTH
    metrics and strictly better on one. Duplicated coordinates are collapsed
    to their first occurrence in ``(prob_t, min_votes)`` order, so the front
    is a set of trade-offs rather than a set of ties.

    Args:
        rows: One configuration's sweep rows; rows missing either metric are
            ignored rather than treated as zero.

    Returns:
        The non-dominated rows, sorted by ``micro_f1_50`` descending.
    """
    scored = [r for r in rows
              if r.get("micro_f1_50") is not None
              and r.get("tile_mcc") is not None]
    scored.sort(key=lambda r: (float(r["prob_t"]), int(r["min_votes"])))
    seen: set[tuple[float, float]] = set()
    unique: list[dict] = []
    for row in scored:
        coord = (float(row["micro_f1_50"]), float(row["tile_mcc"]))
        if coord in seen:
            continue
        seen.add(coord)
        unique.append(row)
    front = [
        row for row in unique
        if not any(
            float(other["micro_f1_50"]) >= float(row["micro_f1_50"])
            and float(other["tile_mcc"]) >= float(row["tile_mcc"])
            and (float(other["micro_f1_50"]) > float(row["micro_f1_50"])
                 or float(other["tile_mcc"]) > float(row["tile_mcc"]))
            for other in unique)
    ]
    front.sort(key=lambda r: -float(r["micro_f1_50"]))
    return front


def cost_block(pool_n: int | None, leg: dict | None) -> dict:
    """Price one configuration's pool at its leg's per-candidate rate.

    A leg is priceable only when its cost is ``audited`` (the auditor read
    every pass) or ``published`` (a post-run report states it). An
    ``unaudited`` leg — one whose main pass was cleanup-overwritten — yields
    a LOWER BOUND, and a lower bound multiplied by a pool size is a number
    that looks like a cost and is not, so the row is left null with its
    reason instead.

    Args:
        pool_n: Candidates the operating point's vote count admits.
        leg: The leg record from ``verifier-costs.json``, or ``None`` when no
            leg is mapped to this configuration.

    Returns:
        The cost columns, with ``pool_exceeds_verified`` set when the point
        asks for candidates the leg never verified and ``inherits_larger_leg``
        set when the pool is a subset of a bigger verification.
    """
    if leg is None:
        return {"verifier_cost_basis": "unmapped",
                "verifier_leg_items": None, "verifier_leg_usd": None,
                "verifier_usd_per_candidate": None, "pool_verifier_usd": None,
                "pool_exceeds_verified": None, "inherits_larger_leg": None,
                "verifier_leg_paths": None, "verifier_cost_note": None}
    basis = leg.get("basis", "unaudited")
    items = leg.get("candidates")
    usd = leg.get("usd")
    block = {
        "verifier_cost_basis": basis,
        "verifier_leg_items": items,
        "verifier_leg_usd": round(usd, 4) if usd is not None else None,
        "verifier_usd_per_candidate": None,
        "pool_verifier_usd": None,
        "pool_exceeds_verified": None,
        "inherits_larger_leg": None,
        "verifier_leg_paths": leg.get("stages"),
        "verifier_cost_note": leg.get("note"),
    }
    if items:
        block["pool_exceeds_verified"] = (pool_n > items
                                          if pool_n is not None else None)
        block["inherits_larger_leg"] = (pool_n < items
                                        if pool_n is not None else None)
    if basis not in PRICEABLE or not items or usd is None:
        return block
    rate = usd / items
    block["verifier_usd_per_candidate"] = rate
    if pool_n is not None:
        block["pool_verifier_usd"] = round(pool_n * rate, 4)
    return block


def rank_by_tile_mcc(rows: list[dict]) -> list[dict]:
    """Sort by tile-MCC descending and stamp a 1-based ``rank``."""
    out = sorted(rows, key=lambda r: -float(r["tile_mcc"]))
    for i, row in enumerate(out, 1):
        row["rank"] = i
    return out


# ---------------------------------------------------------------------------
# Reading the committed records.
# ---------------------------------------------------------------------------


def carried_point(track: Track, name: str, record: dict,
                  board_carried: dict) -> tuple[float, int] | None:
    """The configuration's CARRIED operating point, or ``None``.

    The board reads it from its own ``cells_manifest.json`` (via
    ``final_board_sweeps.carried_k_by_family``, the same reader the sweep
    record uses), so a family with no carried cell — ``UPL``, ``A-N1``,
    ``B-N1`` — honestly has none. A campaign rung carries it in its own
    record.

    Args:
        track: The track this configuration belongs to.
        name: Configuration name.
        record: Its entry in ``sweeps.json``.
        board_carried: ``carried_k_by_family`` output for the board.

    Returns:
        ``(prob_t, min_votes)`` or ``None``.
    """
    if track.record_key == "families":
        entry = board_carried.get(name)
        return (entry["prob_t"], entry["k"]) if entry else None
    point = record.get("carried_point")
    return (float(point[0]), int(point[1])) if point else None


def build_rows(costs: dict[str, dict]) -> list[dict]:
    """One leaderboard row per configuration across every track."""
    board_carried = carried_k_by_family(BOARD_HOME / "cells_manifest.json")
    rows: list[dict] = []
    for track in TRACKS:
        sweeps = json.loads((track.home / "sweeps.json").read_text())
        for name, record in sweeps[track.record_key].items():
            best = record.get(track.optimum_key)
            if best is None:
                logger.warning("%s: no %s in the sweep record — skipped",
                               name, track.optimum_key)
                continue
            csv_rows = read_sweep_csv(track.home / f"sweep_{name}.csv")
            k = int(best["min_votes"])
            carried = carried_point(track, name, record, board_carried)
            carried_row = (sweep_row_at(csv_rows, *carried) if carried
                           else None)
            rows.append({
                "config": name,
                "track": track.key,
                "basis": "ORACLE",
                "min_votes": k,
                "prob_t": float(best["prob_t"]),
                "n_detections": int(best["n_detections"]),
                "tile_tp": best.get("tile_tp"), "tile_tn": best.get("tile_tn"),
                "tile_fp": best.get("tile_fp"), "tile_fn": best.get("tile_fn"),
                "tile_mcc": float(best["tile_mcc"]),
                "micro_f1_50": float(best["micro_f1_50"]),
                "carried_point": list(carried) if carried else None,
                "carried_tile_mcc": (float(carried_row["tile_mcc"])
                                     if carried_row else None),
                "carried_micro_f1_50": (float(carried_row["micro_f1_50"])
                                        if carried_row else None),
                "tile_mcc_over_carried": (
                    float(best["tile_mcc"]) - float(carried_row["tile_mcc"])
                    if carried_row else None),
                "micro_f1_50_vs_carried": (
                    float(best["micro_f1_50"])
                    - float(carried_row["micro_f1_50"])
                    if carried_row else None),
                "pool_n_at_vote": pool_at_vote(csv_rows, k),
                **cost_block(pool_at_vote(csv_rows, k), costs.get(name)),
                "sweep_csv": str(
                    (track.home / f"sweep_{name}.csv").relative_to(
                        PROJECT_ROOT)),
            })
    return rank_by_tile_mcc(rows)


# ---------------------------------------------------------------------------
# Writing, or checking instead of writing.
# ---------------------------------------------------------------------------


def report_drift(expected: dict[Path, str]) -> list[str]:
    """Compare regenerated payloads with the committed files; write nothing.

    Args:
        expected: Destination path -> the text a regeneration would write.

    Returns:
        One line per file that is missing or differs, repository-relative
        where the path is under the repository. Empty means the committed
        presentation is exactly what its committed inputs regenerate.
    """
    stale: list[str] = []
    for path, text in expected.items():
        rel = (str(path.relative_to(PROJECT_ROOT))
               if path.is_relative_to(PROJECT_ROOT) else str(path))
        if not path.is_file():
            stale.append(f"{rel} (missing)")
        elif path.read_text() != text:
            stale.append(rel)
    return stale


def emit(expected: dict[Path, str], check: bool) -> int:
    """Write the payloads, or under ``check`` compare them and write nothing.

    Args:
        expected: Destination path -> text.
        check: True to compare instead of write.

    Returns:
        0 when written, or when every file matches; 1 when any is stale.
    """
    if check:
        stale = report_drift(expected)
        for line in stale:
            logger.error("STALE: %s", line)
        if stale:
            return 1
        logger.info("check: %d file(s) match a regeneration", len(expected))
        return 0
    for path, text in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return 0


# ---------------------------------------------------------------------------
# Stage: audit the verifier legs.
# ---------------------------------------------------------------------------


def audit_legs(check: bool = False) -> int:
    """Price every mapped verifier leg and write ``verifier-costs.json``.

    Calls ``scripts/audit_verifier_cost.py`` — the auditor both campaigns'
    post-run reports cite — rather than re-deriving a rate here, so this
    table cannot drift from the audited figures those reports publish.

    Args:
        check: Compare with the committed ``verifier-costs.json`` instead of
            writing it (the auditor still runs).

    Returns:
        Process exit code.
    """
    configs = sorted({
        name
        for track in TRACKS
        for name in json.loads(
            (track.home / "sweeps.json").read_text())[track.record_key]
    })
    by_leg: dict[tuple[str, ...], list[str]] = {}
    for config in configs:
        leg = leg_for(config)
        if leg is None:
            logger.warning("%s: no verifier leg mapped", config)
            continue
        by_leg.setdefault(leg, []).append(config)

    costs: dict[str, dict] = {}
    disagreements: list[str] = []
    for leg, members in sorted(by_leg.items()):
        cmd = [".venv/bin/python", "scripts/audit_verifier_cost.py",
               *leg, "--json"]
        model = next((LEG_MODEL[m] for m in members if m in LEG_MODEL), None)
        if model:
            cmd += ["--model", model]
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                              text=True, check=False)
        start = proc.stdout.find("[")
        if start < 0:
            logger.error("auditor produced no JSON for %s: %s", leg,
                         proc.stderr[-600:])
            return 1
        stages = json.loads(proc.stdout[start:])
        audited = {
            "usd": sum(s["audited_usd"] for s in stages),
            "candidates": sum(s["items_covered"] for s in stages),
            "complete": all(s["complete"] for s in stages),
            "notes": [n for s in stages for n in s.get("notes", [])],
        }
        # One published figure per leg at most; every member of a shared leg
        # is the same leg, so the first that has one speaks for all of them.
        published = next((PUBLISHED_LEG_COST[m] for m in members
                          if m in PUBLISHED_LEG_COST), None)
        record = reconcile(leg, members, audited, published)
        if record.get("disagreement"):
            disagreements.append(record["disagreement"])
        for config in members:
            costs[config] = record
        logger.info("%-44s %-9s US$%9.4f over %7d candidates  (%s)",
                    Path(leg[0]).name + (f" +{len(leg) - 1}"
                                         if len(leg) > 1 else ""),
                    record["basis"], record["usd"] or 0.0,
                    record["candidates"] or 0,
                    ", ".join(members[:3])
                    + ("…" if len(members) > 3 else ""))
        if record["basis"] == "unaudited":
            logger.warning("  %s", record["note"])
    if disagreements:
        for line in disagreements:
            logger.error("COST DISAGREEMENT %s", line)
        return 1
    payload = json.dumps({
        "_README": (
            "Verifier-leg cost per configuration. basis 'audited' = "
            "scripts/audit_verifier_cost.py read every pass of the leg; "
            "'published' = the auditor could not (a pre-2026-09-14 cleanup "
            "overwrote the main pass's meta, so it yields a LOWER BOUND) and "
            "the figure is the campaign post-run report's, cited in 'source'; "
            "'unaudited' = neither, so the leg has no usable cost and nothing "
            "derived from it is priced. Where both exist they are required to "
            f"agree to US${COST_AGREEMENT_USD:.2f}."),
        "agreement_tolerance_usd": COST_AGREEMENT_USD,
        "generated_by": "scripts/build_tile_presence_board.py --stage costs",
        "legs": costs,
    }, indent=2) + "\n"
    rc = emit({OUT / COSTS: payload}, check)
    if check or rc:
        return rc
    by_basis: dict[str, int] = {}
    for record in costs.values():
        by_basis[record["basis"]] = by_basis.get(record["basis"], 0) + 1
    logger.info("wrote %s (%d configurations, %d legs; %s)",
                (OUT / COSTS).relative_to(PROJECT_ROOT), len(costs),
                len(by_leg),
                ", ".join(f"{n} {b}" for b, n in sorted(by_basis.items())))
    return 0


def reconcile(leg: tuple[str, ...], members: list[str], audited: dict,
              published: dict | None) -> dict:
    """Settle one leg's cost between the auditor and the published figure.

    Args:
        leg: The stage directories audited.
        members: Configurations drawing on this leg.
        audited: The auditor's summed result for the leg.
        published: The post-run report's figure, or ``None``.

    Returns:
        The leg record written into ``verifier-costs.json``, carrying the
        basis the cost may be used under and, on a mismatch, a
        ``disagreement`` the caller turns into a failure.
    """
    base = {"stages": list(leg), "configs": members,
            "auditor_usd": round(audited["usd"], 6),
            "auditor_candidates": audited["candidates"],
            "auditor_complete": audited["complete"],
            "auditor_notes": audited["notes"]}
    if audited["complete"] and audited["candidates"]:
        record = {**base, "basis": "audited", "usd": audited["usd"],
                  "candidates": audited["candidates"],
                  "source": "scripts/audit_verifier_cost.py over the leg's "
                            "committed metas",
                  "note": None}
        if published and abs(published["usd"] - audited["usd"]) \
                > COST_AGREEMENT_USD:
            record["disagreement"] = (
                f"{members[0]}: auditor US${audited['usd']:.4f} vs published "
                f"US${published['usd']:.4f} ({published['source']})")
        elif published:
            record["cross_checked_against"] = published["source"]
        return record
    if published:
        return {**base, "basis": "published", "usd": published["usd"],
                "candidates": published["candidates"],
                "source": published["source"],
                "note": ("the auditor reads a LOWER BOUND here — a "
                         "pre-2026-09-14 cleanup overwrote the main pass's "
                         "meta — so the published audited figure is used; "
                         "see auditor_notes")}
    return {**base, "basis": "unaudited", "usd": None, "candidates": None,
            "source": None,
            "note": ("no usable verifier-leg cost: the auditor reads only a "
                     "lower bound (cleanup-overwrite) and no post-run report "
                     f"publishes this leg. Audit target: {', '.join(leg)}")}


# ---------------------------------------------------------------------------
# Stage: the leaderboard.
# ---------------------------------------------------------------------------

HEADER = ("| rank | configuration | track | basis | votes | prob | n | "
          "tile-MCC | F1@50 | carried point | carried tile-MCC | "
          "ΔMCC | pool @ votes | verified | US$/cand | pool US$ |")
RULE = ("|---:|---|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|"
        "---:|---:|")


def render_row(row: dict) -> str:
    """One markdown row of the leaderboard."""
    def num(value: Any, fmt: str) -> str:
        return "—" if value is None else format(value, fmt)

    carried = ("—" if not row["carried_point"]
               else f"({row['carried_point'][0]:.2f}, k{row['carried_point'][1]})")
    flag = ""
    if row.get("pool_exceeds_verified"):
        flag = " ⚠"
    return (
        f"| {row['rank']} | {row['config']} | {row['track']} | "
        f"{row['basis']} | **k{row['min_votes']}** | {row['prob_t']:.2f} | "
        f"{row['n_detections']} | {row['tile_mcc']:.4f} | "
        f"{row['micro_f1_50']:.4f} | {carried} | "
        f"{num(row['carried_tile_mcc'], '.4f')} | "
        f"{num(row['tile_mcc_over_carried'], '+.4f')} | "
        f"{num(row['pool_n_at_vote'], 'd')}{flag} | "
        f"{num(row['verifier_leg_items'], 'd')} | "
        f"{num(row['verifier_usd_per_candidate'], '.6f')} | "
        f"{num(row['pool_verifier_usd'], '.2f')} |")


def leaderboard_markdown(rows: list[dict]) -> str:
    """The whole ``leaderboard.md``."""
    n_exceed = sum(1 for r in rows if r.get("pool_exceeds_verified"))
    n_inherit = sum(1 for r in rows if r.get("inherits_larger_leg"))
    at_one = sum(1 for r in rows if r["min_votes"] == 1)
    body = "\n".join(render_row(r) for r in rows)
    return f"""# Tile-presence leaderboard — every configuration at its tile-MCC optimum

> **Last revised**: 2026-09-21 (first publication; PI ruling 2026-09-21).
> See [§ Changelog](#changelog) for revision history.
> Generated by `scripts/build_tile_presence_board.py --stage leaderboard`
> from the committed sweep records alone. Zero API.

**Every row on this table is an ORACLE.** The operating point is the
tile-MCC argmax over the configuration's whole achievable grid, chosen on
the evaluation reference itself. **No configuration here has a calibrated
carried point at its tile-MCC optimum** — not one of the {len(rows)} rows
was nominated in advance, and the `carried point` column shows what each
configuration actually deployed. Read these as an upper bound on what
tile-presence discrimination the pool can support, never as a result.

**The vote count is a column, not an assumption.** {at_one} of {len(rows)}
configurations put their tile-MCC optimum at a **single vote**, abandoning
the unanimity their carried point relies on. That is the whole reason this
table is separate from the boards (PI ruling 2026-09-21): a metric that
asks only whether a tile was hit at all is indifferent to over-generation
inside a tile, so it will always prefer the setting that over-generates.
Read `votes` before reading `tile-MCC`.

**The cost column prices the pool, not the run.** A point at k votes needs a
verifier probability for every candidate with at least k votes — `pool @
votes`, read off the sweep's own zero-threshold row — at the audited
per-candidate rate of that configuration's verifier leg
(`scripts/audit_verifier_cost.py` over the leg's committed metas, the
auditor the campaigns' post-run reports cite; `verifier-costs.json` records
the leg paths). {n_inherit} rows draw on a pool SMALLER than their leg:
they inherit probabilities from a larger verification and their `pool US$`
is what the point alone would cost, not what was spent. {n_exceed} rows
ask for more candidates than their leg verified (marked ⚠) — for those the
point is not reachable without further verifier spend.

| column | meaning |
|---|---|
| `votes` / `prob` | the optimum's operating point; `votes` is `min_votes`, never assumed |
| `n` | detections retained at that point |
| `tile-MCC` / `F1@50` | the two metrics AT the optimum, from the committed sweep row |
| `carried point` | what the configuration actually deployed; `—` where it has no carried cell |
| `carried tile-MCC` / `ΔMCC` | tile-MCC at the carried point, and what the oracle adds |
| `pool @ votes` | candidates with at least `votes` votes — the verifier pool the point needs |
| `verified` | candidates the configuration's verifier leg actually priced |
| `US$/cand` / `pool US$` | audited rate, and the pool at that rate |

{HEADER}
{RULE}
{body}

## What is not on this table

The per-point tile confusion (`tile_tp`, `tile_tn`, `tile_fp`, `tile_fn`)
is carried in `leaderboard.json` for every row; it is left out of the
markdown to keep the table readable. The Pareto trade between micro-F1 and
tile-MCC — which is what a reader choosing an operating point actually
needs — is in [`frontier/`](frontier/frontier.md).

## Changelog

### 2026-09-21 — Original publication

**Refresh trigger**: PI ruling 2026-09-21, superseding ruling 6c of
2026-09-20. The "MCC oracle" is dropped from the main boards under both
definitions — unconstrained and at-the-carried-k — tile-MCC stays reported
beside micro-F1 at the carried and F1-oracle points, and the tile-MCC
optimum moves to this separate tile-presence presentation.

**What this is**: {len(rows)} configurations — the r2 board's 23 families
and the two image campaigns' twelve rung x arm cells — each at its
unconstrained tile-MCC optimum, costed. Built from the committed sweep
records with no re-sweep and no API.

**Numbers that moved**: none. Every figure is read from a committed sweep
CSV or from `scripts/audit_verifier_cost.py` over committed metas.
"""


def leaderboard_payload(rows: list[dict]) -> dict[Path, str]:
    """The two leaderboard files as text, from ranked rows. Pure.

    Args:
        rows: The output of :func:`build_rows`.

    Returns:
        Destination path -> text, for :func:`emit`.
    """
    return {
        OUT / "leaderboard.json": json.dumps({
            "_README": (
                "Every configuration's UNCONSTRAINED tile-MCC optimum, costed. "
                "PI ruling 2026-09-21: the MCC oracle is dropped from the main "
                "boards and presented here instead. EVERY ROW IS AN ORACLE — "
                "the point is chosen on the evaluation reference and no "
                "configuration has a calibrated carried point at it. min_votes "
                "is a column, never an assumption."),
            "buffer_m": BUFFER_M,
            "reference": "r2",
            "generated_by": "scripts/build_tile_presence_board.py",
            "n_configurations": len(rows),
            "rows": rows,
        }, indent=2) + "\n",
        OUT / "leaderboard.md": leaderboard_markdown(rows),
    }


def stage_leaderboard(check: bool = False) -> int:
    """Write ``leaderboard.json`` and ``leaderboard.md``, or check them.

    Args:
        check: Compare with the committed files instead of writing.

    Returns:
        Process exit code.
    """
    costs_path = OUT / COSTS
    if not costs_path.is_file():
        raise SystemExit(
            f"{costs_path.relative_to(PROJECT_ROOT)} is missing — run "
            "--stage costs first (it audits the verifier legs).")
    costs = json.loads(costs_path.read_text())["legs"]
    rows = build_rows(costs)
    rc = emit(leaderboard_payload(rows), check)
    if check or rc:
        return rc
    logger.info("wrote leaderboard: %d configurations, %d at a single vote",
                len(rows), sum(1 for r in rows if r["min_votes"] == 1))
    return 0


# ---------------------------------------------------------------------------
# Stage: the frontier.
# ---------------------------------------------------------------------------


def compute_fronts() -> tuple[dict[str, dict], list[tuple[str, int]],
                              dict[str, dict]]:
    """Per configuration, the Pareto front and its marked points. Reads only.

    Returns:
        ``(fronts, counts, marks)``: the ``frontier.json`` records keyed by
        configuration; ``(name, non-dominated count)`` pairs in table order;
        and per configuration the carried row and the F1-oracle row the
        figures mark, which the JSON does not carry.
    """
    board_carried = carried_k_by_family(BOARD_HOME / "cells_manifest.json")
    fronts: dict[str, dict] = {}
    counts: list[tuple[str, int]] = []
    marks: dict[str, dict] = {}
    for track in TRACKS:
        sweeps = json.loads((track.home / "sweeps.json").read_text())
        for name, record in sweeps[track.record_key].items():
            rows = read_sweep_csv(track.home / f"sweep_{name}.csv")
            front = pareto_front(rows)
            counts.append((name, len(front)))
            carried = carried_point(track, name, record, board_carried)
            carried_row = (sweep_row_at(rows, *carried) if carried else None)
            f1_best = record.get("argmax") or record.get("f1_oracle")
            fronts[name] = {
                "track": track.key,
                "n_sweep_points": len(rows),
                "n_non_dominated": len(front),
                "carried_point": list(carried) if carried else None,
                "f1_oracle_point": ([f1_best["prob_t"], f1_best["min_votes"]]
                                    if f1_best else None),
                "mcc_optimum_point": [record[track.optimum_key]["prob_t"],
                                      record[track.optimum_key]["min_votes"]],
                "front": [{k: r[k] for k in
                           ("prob_t", "min_votes", "n_detections",
                            "micro_f1_50", "tile_mcc")} for r in front],
            }
            marks[name] = {"carried_row": carried_row, "f1_best": f1_best}
    return fronts, counts, marks


def frontier_payload(fronts: dict[str, dict],
                     counts: list[tuple[str, int]]) -> dict[Path, str]:
    """``frontier.json`` and ``frontier.md`` as text. Pure.

    Args:
        fronts: From :func:`compute_fronts`.
        counts: From :func:`compute_fronts`.

    Returns:
        Destination path -> text, for :func:`emit`.
    """
    home = OUT / "frontier"
    multi = [n for n, c in counts if c > 2]
    table = "\n".join(
        f"| {n} | {f['n_sweep_points']} | {f['n_non_dominated']} | "
        + (f"({f['carried_point'][0]:.2f}, k{f['carried_point'][1]})"
           if f["carried_point"] else "—") + " | "
        + (f"({f['f1_oracle_point'][0]:.2f}, k{f['f1_oracle_point'][1]})"
           if f["f1_oracle_point"] else "—") + " | "
        + f"({f['mcc_optimum_point'][0]:.2f}, "
          f"k{f['mcc_optimum_point'][1]}) |"
        for n, f in fronts.items())
    return {
        home / "frontier.json": json.dumps({
            "_README": (
                "Per configuration, the (micro_f1_50, tile_mcc) "
                "Pareto-non-dominated points of its committed sweep. A point is "
                "dominated when another is at least as good on both metrics and "
                "strictly better on one. This is the honest statement of the "
                "trade the tile-presence leaderboard shows one end of."),
            "buffer_m": BUFFER_M, "reference": "r2",
            "generated_by": "scripts/build_tile_presence_board.py",
            "configurations": fronts,
        }, indent=2) + "\n",
        home / "frontier.md": f"""# The micro-F1 / tile-MCC frontier

> **Last revised**: 2026-09-21 (first publication; PI ruling 2026-09-21).
> Generated by `scripts/build_tile_presence_board.py --stage frontier`.

The [tile-presence leaderboard](../leaderboard.md) shows one end of a
trade. This is the trade. For each of the {len(counts)} configurations, the
sweep points that are **Pareto-non-dominated** on `(micro-F1 @ 50 m,
tile-MCC)`: no other point in that configuration's achievable grid is at
least as good on both and better on one.

**{len(multi)} of {len(counts)} configurations have more than two
non-dominated points**, i.e. a genuine interior choice rather than a
straight swap between the F1 end and the tile-MCC end. The rest offer the
two ends and nothing between them — for those, a tile-presence deployment
is a decision about which metric to serve, not a tuning exercise.

| configuration | sweep points | non-dominated | carried | F1 oracle | tile-MCC optimum |
|---|---:|---:|---|---|---|
""" + table + """

## Figures

One per campaign, all that campaign's configurations overlaid, the carried
point drawn as an open square and the F1 oracle as a star:

- `frontier-board.png` — the r2 55-map board's 23 families
- `frontier-g37-image.png` — the Gemini 3.7 image campaign's six rungs
- `frontier-g3-image.png` — the Gemini 3 image campaign's six rungs

## Reading them

A front that runs steeply up-and-left is a configuration where tile-MCC can
only be bought with large amounts of F1 — the vote-count collapse of
Obs 492 seen as a curve. A front that is nearly flat is one where the two
metrics agree, and the carried point is close to both ends.
""",
    }


def draw_frontier_figures(fronts: dict[str, dict], marks: dict[str, dict]) -> None:
    """One PNG per track, every configuration overlaid. Never checked.

    Args:
        fronts: From :func:`compute_fronts`.
        marks: From :func:`compute_fronts`.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    home = OUT / "frontier"
    home.mkdir(parents=True, exist_ok=True)
    for track in TRACKS:
        fig, ax = plt.subplots(figsize=(9, 6.5))
        cmap = plt.get_cmap("tab20")
        names = [n for n, f in fronts.items() if f["track"] == track.key]
        for i, name in enumerate(names):
            front = fronts[name]["front"]
            carried_row = marks[name]["carried_row"]
            f1_best = marks[name]["f1_best"]
            colour = cmap(i % 20)
            ax.plot([r["micro_f1_50"] for r in front],
                    [r["tile_mcc"] for r in front],
                    marker="o", markersize=3, linewidth=1.1, color=colour,
                    label=name, alpha=0.85)
            if carried_row:
                ax.scatter([carried_row["micro_f1_50"]],
                           [carried_row["tile_mcc"]], marker="s", s=55,
                           facecolors="none", edgecolors=colour, linewidths=1.6)
            if f1_best:
                ax.scatter([f1_best["micro_f1_50"]], [f1_best["tile_mcc"]],
                           marker="*", s=110, color=colour, zorder=5)
        ax.set_xlabel("micro-F1 @ 50 m")
        ax.set_ylabel("tile-MCC")
        ax.set_title(f"{track.title}: micro-F1 / tile-MCC Pareto fronts\n"
                     "square = carried point, star = F1 oracle, "
                     "line = non-dominated set")
        ax.grid(alpha=0.25, linewidth=0.5)
        ax.legend(fontsize=6, ncol=2, loc="lower left", framealpha=0.85)
        fig.tight_layout()
        dest = home / f"frontier-{track.key}.png"
        fig.savefig(dest, dpi=160)
        plt.close(fig)
        logger.info("wrote %s", dest.relative_to(PROJECT_ROOT))


def stage_frontier(check: bool = False) -> int:
    """Write the Pareto fronts, the figures and ``frontier.md``, or check.

    Under ``check`` the JSON and the markdown are compared and the figures
    are neither drawn nor compared.

    Args:
        check: Compare with the committed files instead of writing.

    Returns:
        Process exit code.
    """
    fronts, counts, marks = compute_fronts()
    rc = emit(frontier_payload(fronts, counts), check)
    if check or rc:
        return rc
    draw_frontier_figures(fronts, marks)
    logger.info("frontier: %d configurations, %d with >2 non-dominated points",
                len(counts), sum(1 for _, c in counts if c > 2))
    return 0


# ---------------------------------------------------------------------------
# Stage: take the MCC oracle off the boards' manifests.
# ---------------------------------------------------------------------------

#: What the two families of MCC-oracle cell are called after the ruling of
#: 2026-09-21. Neither is deleted: the cells stay on disk, and the first is
#: what the tile-presence leaderboard presents.
TILE_PRESENCE_BASIS = (
    "tile-presence oracle (unconstrained tile-MCC optimum; presented in "
    "results/tile-presence-2026-09-21/)")
RETAINED_BASIS = (
    "mcc-oracle at carried k — retained, not presented (PI ruling 2026-09-21)")

#: Old basis -> new basis, per manifest. The board spells its bases out; the
#: campaigns use the short forms their materialiser writes.
RELABEL = {
    "mcc-oracle, unconstrained k (post-hoc, superseded 2026-09-20)":
        TILE_PRESENCE_BASIS,
    "mcc-oracle-unconstrained": TILE_PRESENCE_BASIS,
    "mcc-oracle at carried k (post-hoc, 2026-09-20)": RETAINED_BASIS,
    "mcc-oracle": RETAINED_BASIS,
}

#: The pointer every re-labelled cell gains, so a reader who finds the cell
#: can find the table that presents it (or the ruling that stopped presenting
#: it) without reading a changelog.
PRESENTATION = {
    TILE_PRESENCE_BASIS: (
        "PI ruling 2026-09-21: the tile-MCC optimum is no longer an oracle "
        "column on any board. This cell is the UNCONSTRAINED optimum and is "
        "presented in results/tile-presence-2026-09-21/leaderboard.md, with "
        "its vote count as a column and its verifier pool priced. Retained "
        "on disk with its committed evaluation."),
    RETAINED_BASIS: (
        "PI ruling 2026-09-21: the tile-MCC optimum is no longer an oracle "
        "column on any board, under either definition. This cell is the "
        "optimum at the family's CARRIED vote count, the definition ruling "
        "6c of 2026-09-20 introduced and this ruling superseded. It is "
        "retained on disk with its committed evaluation and is NOT "
        "presented; the tile-presence table presents the unconstrained "
        "optimum instead (results/tile-presence-2026-09-21/)."),
}

#: Sweep-record key rename: the campaigns called their carried-k selection
#: ``mcc_oracle``, which is the word the ruling drops. The board already
#: spells the same thing ``mcc_argmax_at_carried_k``, so the two tracks are
#: brought onto one vocabulary. Both argmaxes stay in the record as DATA —
#: only the name changes.
SWEEP_KEY_RENAME = {"mcc_oracle": "mcc_argmax_at_carried_k"}

MANIFESTS = (BOARD_HOME / "cells_manifest.json",
             G37_HOME / "cells_manifest.json",
             G3_HOME / "cells_manifest.json")
CAMPAIGN_SWEEPS = (G37_HOME / "sweeps.json", G3_HOME / "sweeps.json")


def relabel_manifest(manifest: dict) -> list[tuple[str, str, str]]:
    """Re-label every MCC-oracle cell of one manifest, in place.

    Args:
        manifest: The parsed ``cells_manifest.json``.

    Returns:
        ``(label, old basis, new basis)`` for each cell touched.
    """
    touched: list[tuple[str, str, str]] = []
    for cell in manifest["cells"]:
        old = cell.get("basis")
        new = RELABEL.get(old)
        if new is None:
            continue
        cell["basis"] = new
        cell["presentation"] = PRESENTATION[new]
        touched.append((cell["label"], old, new))
    return touched


def rename_sweep_keys(sweeps: dict, record_key: str) -> list[str]:
    """Apply :data:`SWEEP_KEY_RENAME` to every record, in place.

    Args:
        sweeps: The parsed ``sweeps.json``.
        record_key: ``rungs`` or ``families``.

    Returns:
        The records renamed.
    """
    touched: list[str] = []
    for name, record in sweeps.get(record_key, {}).items():
        for old, new in SWEEP_KEY_RENAME.items():
            if old in record:
                record[new] = record.pop(old)
                touched.append(name)
    return touched


def stage_relabel() -> int:
    """Re-label the manifests and bring the sweep records onto one vocabulary.

    Idempotent: a manifest already re-labelled has no old basis left to
    match, and a record already renamed has no old key.

    Returns:
        Process exit code.
    """
    for path in MANIFESTS:
        manifest = json.loads(path.read_text())
        touched = relabel_manifest(manifest)
        path.write_text(json.dumps(manifest, indent=2) + "\n")
        logger.info("%s: re-labelled %d cell(s)",
                    path.relative_to(PROJECT_ROOT), len(touched))
        for label, old, new in touched:
            logger.info("    %-34s %r -> %r", label, old[:38], new[:38])
    for path in CAMPAIGN_SWEEPS:
        sweeps = json.loads(path.read_text())
        touched = rename_sweep_keys(sweeps, "rungs")
        path.write_text(json.dumps(sweeps, indent=2) + "\n")
        logger.info("%s: renamed the carried-k key on %d rung(s)",
                    path.relative_to(PROJECT_ROOT), len(touched))
    return 0


STAGES = (("costs", audit_legs), ("leaderboard", stage_leaderboard),
          ("frontier", stage_frontier))


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Command-line arguments; ``None`` reads ``sys.argv``.

    Returns:
        A process exit status. Under ``--check`` every selected stage is
        compared before the status is decided, so one run names every
        stale file rather than the first.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True,
                    choices=["costs", "leaderboard", "frontier",
                             "relabel", "all"])
    ap.add_argument("--check", action="store_true",
                    help="regenerate the selected stage(s) in memory, compare "
                         "with the committed files, write nothing; exit 1 on "
                         "drift (the frontier PNGs are not compared)")
    args = ap.parse_args(argv)
    if args.stage == "relabel":
        if args.check:
            ap.error("--check does not apply to --stage relabel")
        return stage_relabel()
    status = 0
    for name, stage in STAGES:
        if args.stage not in (name, "all"):
            continue
        rc = stage(check=args.check)
        if rc and not args.check:
            return rc
        status = max(status, rc)
    return status


if __name__ == "__main__":
    sys.exit(main())
