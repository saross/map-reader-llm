#!/usr/bin/env python3
"""
Final 55-map board addendum: the post-hoc 3.7-family cells.

Materialises cells that the stage-1 sweep swept but never built, at
points the board itself already holds a sweep row for. Two sets, chosen
with ``--set``:

``carried-analogue`` (PI ruling 2026-09-20, item 1)
    The seven missing **carried-analogue** rungs of the 3.7 families.
    Each family's top rung carries a GS-selected operating point
    (ARM1 (0.10, k5); ARM2 (0.80, k5); FOURTH (0.98, k10) — read from
    ``final_board_sweeps.G37_IDENTITY``, so the threshold cannot drift
    from the one the identity gate enforces). A *carried analogue* is
    that same probability threshold applied DOWNWARD to a lower rung,
    with ``k`` set to the rung's own N. The canonical grid board already
    publishes exactly this construction for the two arms
    (``results/gemini37-55map-2026-08-31/grid-board/grid_board.json``,
    ``basis: "carried-analogue"``); it was never carried onto the r2
    board, which is why image-vs-text at K/N = 1 and 3 could only be
    read carried-against-oracle
    (``reports/comparability-inventory-37-runs-2026-09-20.md`` § 3.2).

``mcc-oracle`` (PI ruling 2026-09-20, item 2) — SUPERSEDED
    The ten **unconstrained tile-MCC argmax** cells of the same ten
    families, read from ``sweeps.json``'s ``mcc_argmax``. The image
    campaigns publish an ``mcc_oracle`` per rung; the text track and the
    fourth cell had none, so any MCC comparison across the two tracks was
    one-sided. These cells were built on 2026-09-20 and are kept on disk
    and in the manifest, relabelled
    ``mcc-oracle, unconstrained k (post-hoc, superseded 2026-09-20)``,
    because every one of them sits at the LOWEST vote count its family's
    sweep offers — a recorded property of the metric, not a defect to be
    edited out.

``mcc-oracle-at-carried-k`` (PI ruling 2026-09-20, the redefinition)
    The ten **carried-k tile-MCC oracle** cells: the same families, at
    ``sweeps.json``'s ``mcc_argmax_at_carried_k`` — the tile-MCC optimum
    over ``prob_t`` with ``min_votes`` pinned to the family's carried
    vote count. Labelled ``<family>-mcc-oracle-k<carried>``. This is the
    board's published MCC oracle from 2026-09-20, and unlike the
    unconstrained optimum it is a like-for-like companion of the F1
    oracle: both are read at the family's own vote structure. Running
    this set also relabels the superseded ``-mcc-oracle`` cells above, so
    the two can never be confused in the manifest.

Every set is **post-hoc**: they are not registered claims, and they are
labelled ``basis: "... (post-hoc)"`` wherever they appear — the same
discipline as ``final_board_n3_carried.py``'s emergent N = 3 cells, and
the same label prefix that makes ``final_board_sweeps.py`` carry them
forward across a regeneration.

GATES (nothing is written unless all pass, per set):

1. **Count**: each materialised cell's detection count equals the
   committed sweep CSV row for its point EXACTLY, proving the same
   derivation chain produced it.
2. **Confusion**: re-scoring the materialised subset through the sweep's
   own scorer reproduces the CSV row's ``tp``/``fp``/``fn`` and tile
   confusion EXACTLY, and its micro-F1 @ 50 m and tile-MCC to within the
   board's documented mechanism bound (0.003). The count gate alone
   cannot see a cell that holds the right NUMBER of the wrong
   detections.
3. **Published F1** (``carried-analogue`` only): the row's micro-F1 also
   matches the inventory's published figure to 4 d.p.

``--verify-scored`` re-reads the same comparison AFTER the engine has
run: each cell's committed ``evaluation.json`` must reproduce its sweep
row's F1 @ 50 m and tile-MCC to within 0.003, end to end.

This script does NOT re-tier the board: ``final_board_50m.json``, its
tiers and its BH family are not touched, and ``final_board_build.py`` is
not run (PI ruling 2026-09-13, carried forward 2026-09-20). Scoring is
``r2_score_cells.py --stage board``, which picks the new cells up from
the manifest.

Usage::

    python scripts/final_board_posthoc_cells.py --set carried-analogue
    python scripts/final_board_posthoc_cells.py --set mcc-oracle-at-carried-k
    python scripts/r2_score_cells.py --stage board --jobs 4 --workers 2
    python scripts/final_board_posthoc_cells.py \
        --set mcc-oracle-at-carried-k --verify-scored

Zero API. Run on sapphire.

Created: 2026-09-20 (Session 157)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.build_55map_leaderboard import (  # noqa: E402
    BOUNDS,
    board_home,
    reference_gt,
)
from scripts.final_board_sweeps import (  # noqa: E402
    BUFFER_M,
    G37_IDENTITY,
    MECHANISM_BOUND,
    build_g37_families,
    tile_confusion,
)
from scripts.lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
)
from scripts.n1_baseline_leaderboard_tiering import micro_f1  # noqa: E402
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402
from scripts.stride55_score import build_map_constrained_index  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: Cross-check for the ``carried-analogue`` set: the micro-F1 @ 50 m the
#: inventory published for each point (§ 3.2, read from the committed sweep
#: CSVs on 2026-09-20). The gate compares the CSV row this run reads against
#: this table to 4 d.p., so a regenerated CSV that moved cannot pass silently.
CARRIED_ANALOGUE_F1 = {
    "ARM2-N1-carried": 0.8459,
    "ARM2-N3-carried": 0.8802,
    "ARM1-N1-carried": 0.7859,
    "ARM1-N3-carried": 0.8469,
    "FOURTH-N1-carried": 0.8348,
    "FOURTH-N3-carried": 0.8744,
    "FOURTH-N5-carried": 0.8754,
}

#: Basis labels. All contain "post-hoc", which is what
#: ``final_board_sweeps.py``'s carry-forward matches on.
BASIS = {
    "carried-analogue": "carried-analogue (post-hoc)",
    "mcc-oracle": "mcc-oracle (post-hoc)",
    "mcc-oracle-at-carried-k": "mcc-oracle at carried k (post-hoc, 2026-09-20)",
}

#: What the ten unconstrained MCC-oracle cells are relabelled to when the
#: carried-k set lands. They stay on disk and in the manifest — the collapse
#: to the lowest vote count is the finding, so the evidence for it is kept
#: (archive, never delete) — but no consumer may read them as the board's
#: MCC oracle any more.
SUPERSEDED_MCC_BASIS = (
    "mcc-oracle, unconstrained k (post-hoc, superseded 2026-09-20)")

F1_TOLERANCE = 5e-5  # half a 4-d.p. ulp: identity at published precision


def carried_analogue_points() -> list[tuple[str, str, float, int, str]]:
    """The seven carried-analogue cells: family, label, threshold, k, note.

    Derived rather than listed: each 3.7 family's top rung carries a
    GS-selected ``(prob_t, k_max)`` in
    ``final_board_sweeps.G37_IDENTITY`` — the same table the stage-1
    identity gate enforces — and the analogue applies that ``prob_t``
    downward at every rung ``n < k_max`` with ``k = n``. The rung set
    therefore follows ``k_max`` (5 for the arms, 10 for the fourth cell)
    and cannot drift away from the families the sweep actually builds.

    Returns:
        One tuple per cell: ``(family, label, prob_t, min_votes, note)``,
        in the inventory's order.
    """
    out: list[tuple[str, str, float, int, str]] = []
    for top_family, ((prob_t, k_max), _n) in G37_IDENTITY.items():
        stem = top_family.rsplit("-N", 1)[0]
        for n in (n for n in (1, 3, 5) if n < k_max):
            note = (
                f"carried analogue: ({prob_t:.2f}, k{k_max}) is {stem}'s "
                f"GS-carried operating point at its top rung; the same "
                f"probability threshold is applied downward here with k set "
                f"to this rung's own N. Added 2026-09-20 per "
                f"reports/comparability-inventory-37-runs-2026-09-20.md "
                f"§ 3.2. Post-hoc, not a registered claim."
            )
            out.append((f"{stem}-N{n}", f"{stem}-N{n}-carried", prob_t, n,
                        note))
    return out


def mcc_families(families: dict) -> list[str]:
    """The ten 3.7-campaign families the MCC addendum covers.

    Args:
        families: The ``families`` block of ``sweeps.json``.

    Returns:
        Their names, sorted.
    """
    stems = [f.rsplit("-N", 1)[0] for f in G37_IDENTITY]
    return sorted(name for name in families
                  if name.rsplit("-N", 1)[0] in stems)


def mcc_oracle_at_carried_k_points(
        out_dir: Path) -> list[tuple[str, str, float, int, str]]:
    """The ten carried-k tile-MCC oracle cells, from ``sweeps.json``.

    The board's MCC oracle from the PI ruling of 2026-09-20: the tile-MCC
    optimum over ``prob_t`` at the family's CARRIED vote count, so that it
    answers the same question of the same configuration as the F1 oracle
    beside it. The point is read from the record rather than recomputed,
    for the same reason ``mcc_oracle_points`` reads ``mcc_argmax``: one
    selector, in ``final_board_sweeps.py``, gated by its own tests.

    Args:
        out_dir: The board home holding ``sweeps.json``.

    Returns:
        One tuple per cell: ``(family, label, prob_t, min_votes, note)``.
        The label carries the carried k explicitly —
        ``<family>-mcc-oracle-k<carried>`` — so it can never be read as
        the superseded unconstrained cell of the same family.

    Raises:
        SystemExit: If a family's record carries no
            ``mcc_argmax_at_carried_k`` (``final_board_sweeps.py
            --record-carried-k`` has not run), or carries it as null
            because the family has no carried cell.
    """
    sweeps = json.loads((out_dir / "sweeps.json").read_text())
    families = sweeps.get("families", {})
    wanted = mcc_families(families)
    missing = [name for name in wanted
               if "mcc_argmax_at_carried_k" not in families[name]]
    if missing:
        raise SystemExit(
            "sweeps.json carries no mcc_argmax_at_carried_k for "
            f"{', '.join(missing)} — run scripts/final_board_sweeps.py "
            "--reference r2 --record-carried-k first (PI ruling "
            "2026-09-20, the MCC-oracle redefinition).")
    null = [name for name in wanted
            if families[name]["mcc_argmax_at_carried_k"] is None]
    if null:
        raise SystemExit(
            f"{', '.join(null)} have no carried k on this board, so no "
            "carried-k MCC oracle can be materialised for them; add their "
            "carried cells first.")
    out: list[tuple[str, str, float, int, str]] = []
    for name in wanted:
        record = families[name]
        best = record["mcc_argmax_at_carried_k"]
        unconstrained = record.get("mcc_argmax") or {}
        note = (
            f"tile-MCC oracle at this family's CARRIED vote count "
            f"(k{record['carried_k']}, from {record['carried_k_source']}): "
            f"the tile-MCC optimum over prob_t with min_votes pinned, so it "
            f"is the like-for-like companion of the F1 oracle "
            f"(tile-MCC {best['tile_mcc']:.4f}, micro-F1@50 "
            f"{best['micro_f1_50']:.4f}, against the F1 argmax's "
            f"{record['argmax']['micro_f1_50']:.4f}). Supersedes the "
            f"UNCONSTRAINED optimum at "
            f"({unconstrained.get('prob_t')}, k{unconstrained.get('min_votes')}), "
            f"which is kept as {name}-mcc-oracle with a superseded basis: "
            f"all 23 board families put that optimum at the lowest vote "
            f"count their sweep offers. PI ruling 2026-09-20. Post-hoc, "
            f"not a registered claim."
        )
        out.append((name, f"{name}-mcc-oracle-k{record['carried_k']}",
                    float(best["prob_t"]), int(best["min_votes"]), note))
    return out


def relabel_superseded_mcc_cells(manifest: dict) -> list[str]:
    """Relabel the unconstrained MCC-oracle cells' basis, in place.

    Archive, never delete: the cells stay on disk and in the manifest, so
    the collapse they record stays browsable, but their basis says plainly
    that they are no longer the board's MCC oracle.

    Args:
        manifest: The parsed ``cells_manifest.json``.

    Returns:
        The labels relabelled by this call.
    """
    touched: list[str] = []
    for cell in manifest["cells"]:
        if cell.get("basis") == BASIS["mcc-oracle"]:
            cell["basis"] = SUPERSEDED_MCC_BASIS
            touched.append(cell["label"])
    return touched


def mcc_oracle_points(out_dir: Path) -> list[tuple[str, str, float, int, str]]:
    """The ten UNCONSTRAINED tile-MCC argmax cells, from ``sweeps.json``.

    Superseded 2026-09-20 by :func:`mcc_oracle_at_carried_k_points`;
    retained so the cells this set built remain reproducible.

    Args:
        out_dir: The board home holding ``sweeps.json``.

    Returns:
        One tuple per cell: ``(family, label, prob_t, min_votes, note)``.

    Raises:
        SystemExit: If a family's sweep record carries no ``mcc_argmax``
            (i.e. ``final_board_sweeps.py`` has not been re-run with the
            extended sweep record for that family).
    """
    sweeps = json.loads((out_dir / "sweeps.json").read_text())
    families = sweeps.get("families", {})
    stems = [f.rsplit("-N", 1)[0] for f in G37_IDENTITY]
    wanted = [name for name in families
              if name.rsplit("-N", 1)[0] in stems]
    missing = [name for name in wanted if "mcc_argmax" not in families[name]]
    if missing:
        raise SystemExit(
            "sweeps.json carries no mcc_argmax for "
            f"{', '.join(sorted(missing))} — re-run "
            "scripts/final_board_sweeps.py --reference r2 --families "
            "<families> first (PI ruling 2026-09-20, item 2).")
    out: list[tuple[str, str, float, int, str]] = []
    for name in sorted(wanted):
        best = families[name]["mcc_argmax"]
        note = (
            f"tile-MCC argmax of this family's committed sweep space "
            f"(tile-MCC {best['tile_mcc']:.4f} against the F1 argmax's "
            f"{families[name]['argmax']['micro_f1_50']:.4f} micro-F1@50). "
            f"Added 2026-09-20 per "
            f"reports/comparability-inventory-37-runs-2026-09-20.md § 3.7, "
            f"so the text track and the fourth cell carry the MCC oracle "
            f"the image rows already publish. Post-hoc, not a registered "
            f"claim."
        )
        out.append((name, f"{name}-mcc-oracle", float(best["prob_t"]),
                    int(best["min_votes"]), note))
    return out


def sweep_row(out_dir: Path, family: str, prob_t: float,
              min_votes: int) -> dict:
    """The committed sweep CSV row for one point.

    Args:
        out_dir: The board home holding ``sweep_<family>.csv``.
        family: Family name (CSV stem).
        prob_t: Probability threshold.
        min_votes: Minimum vote count.

    Returns:
        The matching row as a dict of strings.

    Raises:
        SystemExit: If the CSV has no row at that point.
    """
    path = out_dir / f"sweep_{family}.csv"
    with path.open(newline="") as fh:
        for row in csvmod.DictReader(fh):
            if (abs(float(row["prob_t"]) - prob_t) < 1e-9
                    and int(row["min_votes"]) == min_votes):
                return row
    raise SystemExit(f"{path.name}: no sweep row at ({prob_t}, k{min_votes})")


def set_points(which: str,
               out: Path) -> list[tuple[str, str, float, int, str]]:
    """The cells of one ``--set``.

    Args:
        which: A key of :data:`BASIS`.
        out: The board home.

    Returns:
        One tuple per cell: ``(family, label, prob_t, min_votes, note)``.
    """
    if which == "carried-analogue":
        return carried_analogue_points()
    if which == "mcc-oracle-at-carried-k":
        return mcc_oracle_at_carried_k_points(out)
    return mcc_oracle_points(out)


def confusion_gate(label: str, sub: gpd.GeoDataFrame, row: dict,
                   ref: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame) -> None:
    """Re-score a materialised cell against its committed sweep row.

    The count gate cannot see a cell holding the right NUMBER of the wrong
    detections. This runs the sweep's own scorer over the materialised
    subset and demands the integer counts back EXACTLY and the two
    statistics within the board's documented mechanism bound.

    Args:
        label: Cell label, for the message.
        sub: The materialised subset, EPSG:32635, with ``source_tile``.
        row: The committed sweep CSV row (strings).
        ref: The reference points for this board vintage.
        bounds: The evaluation bounds.

    Raises:
        RuntimeError: On any mismatch.
    """
    tiles = compute_per_tile_tp_fp_fn(sub, ref, bounds,
                                      buffer_metres=BUFFER_M)
    got = {"tp": int(tiles["tp"].sum()), "fp": int(tiles["fp"].sum()),
           "fn": int(tiles["fn"].sum())}
    got.update({k.removeprefix("tile_"): v
                for k, v in tile_confusion(sub, ref, bounds).items()
                if k != "tile_mcc"})
    want = {k: int(row[k]) for k in ("tp", "fp", "fn")}
    want.update({k.removeprefix("tile_"): int(row[k])
                 for k in ("tile_tp", "tile_tn", "tile_fp", "tile_fn")
                 if row.get(k) not in (None, "")})
    bad = {k: (got[k], want[k]) for k in want if got.get(k) != want[k]}
    if bad:
        raise RuntimeError(
            f"{label}: confusion gate FAILED — {bad} (got, committed)")
    f1 = micro_f1(got["tp"], got["fp"], got["fn"])
    mcc = tile_confusion(sub, ref, bounds)["tile_mcc"]
    for name, value, committed in (
            ("micro-F1@50", f1, float(row["micro_f1_50"])),
            ("tile-MCC", mcc, float(row["tile_mcc"]))):
        if abs(value - committed) > MECHANISM_BOUND:
            raise RuntimeError(
                f"{label}: {name} gate FAILED — {value:.6f} vs committed "
                f"{committed:.6f} (bound {MECHANISM_BOUND})")
    logger.info("%-26s confusion gate OK (tp/fp/fn %d/%d/%d exact; "
                "micro-F1 %.4f, tile-MCC %.4f)", label, got["tp"], got["fp"],
                got["fn"], f1, mcc)


def verify_scored(which: str, out: Path) -> int:
    """Check each cell's committed evaluation against its sweep row.

    The end-to-end confirmation: the engine's own F1 @ 50 m and tile-MCC,
    computed through a different code path from the sweep's, must land
    within the board's mechanism bound of the row the cell was selected
    on.

    Args:
        which: The set to verify.
        out: The board home.

    Returns:
        Process exit code (non-zero on any failure).
    """
    failures: list[str] = []
    for family, label, prob_t, min_votes, _note in set_points(which, out):
        evaluation = out / "cells" / label / "evaluation.json"
        if not evaluation.is_file():
            failures.append(f"{label}: no evaluation.json")
            continue
        summary = json.loads(evaluation.read_text())["summary"]
        buffers = [b for b in summary["buffers"]
                   if b["buffer_metres"] == BUFFER_M]
        if not buffers:
            failures.append(f"{label}: evaluation has no {BUFFER_M} m row")
            continue
        row = sweep_row(out, family, prob_t, min_votes)
        checks = (("F1@50", buffers[0]["f1"], float(row["micro_f1_50"])),
                  ("tile-MCC", summary["tile_classification"]["mcc"]["point"],
                   float(row["tile_mcc"])))
        n_ok = int(summary["n_detections"]) == int(row["n_detections"])
        ok = n_ok and all(abs(a - b) <= MECHANISM_BOUND
                          for _n, a, b in checks)
        logger.info("%-26s n %d vs %s | %s — %s", label,
                    int(summary["n_detections"]), row["n_detections"],
                    ", ".join(f"{n} {a:.4f} vs sweep {b:.4f}"
                              for n, a, b in checks),
                    "OK" if ok else "FAIL")
        if not ok:
            failures.append(label)
    if failures:
        for f in failures:
            logger.error("VERIFY FAIL %s", f)
        return 1
    logger.info("%s: every scored cell reproduces its sweep row within %s",
                which, MECHANISM_BOUND)
    return 0


def main(which: str, reference: str = "r2", force_r1: bool = False,
         verify: bool = False) -> int:
    """Materialise one post-hoc set and append it to the board's manifest.

    Args:
        which: A key of :data:`BASIS`.
        reference: Board vintage — only ``r2`` carries the 3.7 families.
        force_r1: Permit writing into the committed r1 board home
            (read-only by policy, H2/H15).
        verify: Verify the set's committed evaluations instead of
            materialising anything.

    Returns:
        Process exit code.

    Raises:
        RuntimeError: If a cell's count or confusion does not reproduce
            its committed sweep row, or (carried-analogue) if that row's
            micro-F1 has moved off the inventory's published figure.
    """
    out = board_home(reference)
    if reference == "standardised" and not force_r1:
        raise SystemExit(
            f"{out.relative_to(PROJECT_ROOT)} is the committed r1 board home "
            "and is read-only (H2/H15); the 3.7 families are an r2-only "
            "membership in any case. Use --reference r2.")
    if verify:
        return verify_scored(which, out)

    points = set_points(which, out)
    logger.info("%s: %d cells to materialise", which, len(points))

    bounds = gpd.read_file(BOUNDS)
    if bounds.crs is None:
        bounds = bounds.set_crs("EPSG:4326")
    bounds = bounds.to_crs("EPSG:32635")
    ref = reference_gt(reference)
    index = build_map_constrained_index()
    families = build_g37_families(index)
    for spec in families.values():
        spec["gdf"] = assign_source_tiles(spec["gdf"], bounds)

    manifest_path = out / "cells_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    have = {c["label"] for c in manifest["cells"]}

    for family, label, prob_t, min_votes, note in points:
        row = sweep_row(out, family, prob_t, min_votes)
        expected = int(row["n_detections"])
        if which == "carried-analogue":
            published = CARRIED_ANALOGUE_F1[label]
            got = float(row["micro_f1_50"])
            if abs(got - published) > F1_TOLERANCE:
                raise RuntimeError(
                    f"{label}: sweep row micro-F1 {got:.6f} has moved off "
                    f"the inventory's published {published:.4f}")
        g = families[family]["gdf"]
        sub = g[(g["mound_probability"] >= prob_t)
                & (g["vote_count"] >= min_votes)]
        if len(sub) != expected:
            raise RuntimeError(
                f"{label}: gate FAILED — {len(sub)} at ({prob_t}, "
                f"k{min_votes}) vs committed sweep {expected}")
        logger.info("%-26s count gate OK (%d at (%.2f, k%d), sweep "
                    "micro-F1 %.4f)", label, len(sub), prob_t, min_votes,
                    float(row["micro_f1_50"]))
        confusion_gate(label, sub, row, ref, bounds)
        dest = out / "cells" / label / "detections.geojson"
        dest.parent.mkdir(parents=True, exist_ok=True)
        sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
        if label not in have:
            manifest["cells"].append({
                "label": label,
                "det": str(dest.relative_to(PROJECT_ROOT)),
                "basis": BASIS[which],
                "point": f"({prob_t:.2f}, k{min_votes})",
                "committed_eval": False,
                "note": note})
            logger.info("%s: appended to cells_manifest", label)

    if which == "mcc-oracle-at-carried-k":
        touched = relabel_superseded_mcc_cells(manifest)
        logger.info("relabelled %d unconstrained MCC-oracle cell(s) to %r: %s",
                    len(touched), SUPERSEDED_MCC_BASIS, ", ".join(touched))

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    logger.info("%s ADDENDUM COMPLETE (%d cells in manifest)", which.upper(),
                len(manifest["cells"]))
    return 0


if __name__ == "__main__":
    _ap = argparse.ArgumentParser(description=__doc__)
    _ap.add_argument("--set", dest="which", required=True,
                     choices=sorted(BASIS),
                     help="Which post-hoc set to materialise.")
    _ap.add_argument(
        "--reference", choices=["standardised", "r2"], default="r2",
        help="Board vintage to append to (default: r2, the only vintage "
             "whose membership includes the 3.7 families).")
    _ap.add_argument("--force-r1", action="store_true",
                     help="Permit writing into the committed r1 board home.")
    _ap.add_argument(
        "--verify-scored", action="store_true",
        help="Materialise nothing: check that each of the set's cells has a "
             "committed evaluation.json reproducing its sweep row's n, "
             "F1 @ 50 m and tile-MCC within the board's mechanism bound.")
    _a = _ap.parse_args()
    sys.exit(main(_a.which, _a.reference, force_r1=_a.force_r1,
                  verify=_a.verify_scored))
