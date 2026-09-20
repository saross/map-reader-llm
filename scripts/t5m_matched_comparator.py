#!/usr/bin/env python3
"""
T5m: the protocol-matched confound check of the image 2x2, as an addition.

Why this script exists
----------------------
The image 2x2's declared T5 (``reports/image-2x2-tests-declaration-2026-09-19.md``
section 3) asks whether, with five confounds removed, the earlier Gemini 3
image cell is reproduced, and answers it by testing ``G3IMG-ARM1-K3-carried``
— **3-of-3 unanimity on a three-pass pool**, n = 5,538 — against ``IM-k3`` —
**3-of-5 majority on a five-pass pool**, n = 4,680. Matching the absolute vote
count across pools of different depth does not remove the passes confound; it
converts it into a vote-*fraction* confound of 1.0 against 0.6
(``results/im-june-pool-grid-2026-09-20/findings.md`` section 6). The grid in
that note shows the protocol-matched comparator is the September pool at
K = 5 read at ``min_votes`` 3, and that the sign of the comparison depends on
which axis the matching holds fixed.

The PI ruled on 2026-09-20: keep T5 exactly as declared — it is committed in
three citable JSONs and in the declaration's changelog — and **add** a matched
test, T5m, at the K = 3 rung only, because ``IM-k3`` is a three-vote cell.
This script is that addition. It touches neither ``tests_2x2_K3.json`` nor
``scripts/gemini37_image_55map_r2.py``.

What it builds
--------------
Two cells on the already-swept ``G3IMG-ARM1-K5`` candidate frame, both at
three votes, both under the same arm-1 verifier (``gemini-3-flash-preview``,
``minimal``, T = 0) that IM-k3's June leg ran in configuration:

- ``G3IMG-ARM1-K5-votes3-carried`` at (0.15, k3) — IM-k3's own operating
  point, so the two cells differ in pool and not in threshold;
- ``G3IMG-ARM1-K5-votes3-f1-oracle`` at the best micro-F1 row with
  ``min_votes`` 3 in ``sweep_G3IMG-ARM1-K5.csv``, so the carried-versus-oracle
  tax on the September side is visible rather than implied.

Every primitive is **imported** from ``scripts/gemini37_image_55map_r2.py`` —
the candidate frame with its ``assign_eval_frame_tiles`` re-stamp, the
operating-point predicate, the achievable grid, the per-tile arrays, the tile
vectors, the engine recipe and both permutation tests. Nothing about the
measurement is re-implemented, so a difference here cannot be an artefact of a
second scorer.

The gates
---------
1. **Sweep identity** (``--stage materialise``). Each materialised cell must
   reproduce its own row of ``sweep_G3IMG-ARM1-K5.csv`` exactly: detection
   count, aggregate TP/FP/FN, the tile confusion, micro-F1 @ 50 m and
   tile-MCC. A cell that does not is not the point the grid reported, and
   nothing is written.
2. **Declared-T5 reproduction** (``--stage tests``). Test (c) re-runs the
   declared T5 pair through this script's own code path and must reproduce
   ``results/image-2x2-2026-09-19/tests_2x2_K3.json`` ``f1_tests[4]`` /
   ``mcc_tests[4]`` exactly — +0.001604 at p = 0.7604 on micro-F1 and
   +0.013698 at p = 0.0578 on tile-MCC. If it does not, the pipeline is not
   the pipeline that produced the declared result and the run stops.
3. **Shared truth**. Every pair asserts equal per-tile truth vectors before a
   paired test is run, so a frame mismatch cannot masquerade as an effect.

Usage::

    python scripts/t5m_matched_comparator.py --stage materialise
    # commit the two detections files and the manifest, then:
    python scripts/t5m_matched_comparator.py --stage score --workers 5 --jobs 2
    python scripts/t5m_matched_comparator.py --stage tests

Zero API. Run on sapphire: the scoring stage is a 10,000-draw BCa bootstrap
per cell and each test is 10,000 permutations over 8,541 tiles.

Created: 2026-09-20
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts import gemini37_image_55map_r2 as r2  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The Gemini 3 image campaign's results home, where the new cells land beside
#: the 2x2's own. The campaign is selected in :func:`_select`, which rebinds
#: the r2 module's campaign globals.
CAMPAIGN_KEY = "g3"
RESULTS_HOME = PROJECT_ROOT / "results/gemini3-image-55map-2026-09-16"
SWEEP_CSV = RESULTS_HOME / "sweep_G3IMG-ARM1-K5.csv"
MANIFEST = RESULTS_HOME / "cells_manifest.json"

#: The rung the matched comparator is read off: arm 1, K = 5, three votes.
RUNG_LABEL = "G3IMG-ARM1-K5"
ARM = "arm1"
K = 5
MIN_VOTES = 3

#: IM-k3's own probability threshold, so the matched-carried cell differs from
#: it in the pool and not in the operating point
#: (``outputs/55maps-image-generalisation`` ``resolved_config.yaml``; the June
#: grid's carried row, ``results/im-june-pool-grid-2026-09-20/findings.md``).
MATCHED_PROB = 0.15

#: Where the 2x2's test files live, and the declared file test (c) reproduces.
TESTS_HOME = PROJECT_ROOT / "results/image-2x2-2026-09-19"
DECLARED_TESTS = TESTS_HOME / "tests_2x2_K3.json"
DECLARED_T5_CELL = "G3IMG-ARM1-K3-carried"
DECLARATION = "reports/image-2x2-tests-declaration-2026-09-19.md"

#: Row index of T5 in the declared file's ``f1_tests`` / ``mcc_tests`` arrays.
T5_ROW = 4

CARRIED_LABEL = f"{RUNG_LABEL}-votes3-carried"
ORACLE_LABEL = f"{RUNG_LABEL}-votes3-f1-oracle"

#: The manifest ``basis`` strings. They say in the artefact itself that these
#: cells are post-hoc additions serving T5m, so a later reader of the manifest
#: cannot mistake them for members of the campaign's declared cell set.
CARRIED_BASIS = "protocol-matched comparator for T5m (post-hoc, 2026-09-20)"
ORACLE_BASIS = (
    "protocol-matched comparator for T5m, F1 oracle at 3 votes "
    "(post-hoc, 2026-09-20)"
)


def _select() -> None:
    """Bind the r2 module to the Gemini 3 image campaign."""
    r2.select_campaign(CAMPAIGN_KEY)


# ---------------------------------------------------------------------------
# The sweep rows the cells are gated against.
# ---------------------------------------------------------------------------


def sweep_rows() -> list[dict[str, Any]]:
    """Every row of the K = 5 arm-1 sweep, typed.

    Returns:
        The sweep's rows with numeric fields converted: ``prob_t`` and the two
        metrics to float, the counts to int (``tp``/``fp``/``fn`` are written
        as floats by the sweep and are integral).

    Raises:
        FileNotFoundError: If the sweep has not been run.
    """
    with SWEEP_CSV.open(newline="") as fh:
        rows = list(csvmod.DictReader(fh))
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append({
            "rung": row["rung"],
            "prob_t": float(row["prob_t"]),
            "min_votes": int(row["min_votes"]),
            "n_detections": int(row["n_detections"]),
            "tp": float(row["tp"]),
            "fp": float(row["fp"]),
            "fn": float(row["fn"]),
            "micro_f1_50": float(row["micro_f1_50"]),
            "tile_mcc": float(row["tile_mcc"]),
            "tile_tp": int(row["tile_tp"]),
            "tile_tn": int(row["tile_tn"]),
            "tile_fp": int(row["tile_fp"]),
            "tile_fn": int(row["tile_fn"]),
        })
    return out


def cell_specs() -> list[dict[str, Any]]:
    """The two cells to build, each with the sweep row it must reproduce.

    The carried cell is pinned to IM-k3's own threshold; the oracle cell is
    read off the sweep as the best micro-F1 row at three votes rather than
    retyped from prose, so a changed sweep moves the cell rather than
    silently disagreeing with it.

    Returns:
        Two specs, each ``{label, basis, prob_t, min_votes, row}``.

    Raises:
        SystemExit: If the matched carried point is not in the sweep.
    """
    rows = [r for r in sweep_rows() if r["min_votes"] == MIN_VOTES]
    if not rows:
        raise SystemExit(f"{SWEEP_CSV}: no rows at min_votes {MIN_VOTES}")
    carried = next((r for r in rows if abs(r["prob_t"] - MATCHED_PROB) < 1e-9), None)
    if carried is None:
        raise SystemExit(
            f"{SWEEP_CSV}: no row at ({MATCHED_PROB}, k{MIN_VOTES}) — the "
            "matched carried point is not in the swept grid")
    oracle = max(rows, key=lambda r: r["micro_f1_50"])
    return [
        {"label": CARRIED_LABEL, "basis": CARRIED_BASIS, "prob_t": carried["prob_t"],
         "min_votes": MIN_VOTES, "row": carried},
        {"label": ORACLE_LABEL, "basis": ORACLE_BASIS, "prob_t": oracle["prob_t"],
         "min_votes": MIN_VOTES, "row": oracle},
    ]


# ---------------------------------------------------------------------------
# Materialisation, gated against the sweep.
# ---------------------------------------------------------------------------


def _gate_against_sweep(
    sub: gpd.GeoDataFrame,
    row: dict[str, Any],
    ref: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
    tile_index: dict[str, int],
) -> list[str]:
    """Check a materialised cell against its swept row.

    Args:
        sub: The materialised subset.
        row: The sweep row for the same operating point.
        ref: The r2 reference in EPSG:32635.
        bounds: The evaluation frame in EPSG:32635.
        tile_index: ``tile_name -> row`` index.

    Returns:
        A list of failure descriptions, empty when the cell reproduces the row.
    """
    failures: list[str] = []
    if len(sub) != row["n_detections"]:
        failures.append(f"n {len(sub)} != swept {row['n_detections']}")
    tp, fp, fn = r2.per_tile_arrays(sub, ref, bounds, tile_index)
    for name, got, want in (("tp", tp.sum(), row["tp"]), ("fp", fp.sum(), row["fp"]),
                            ("fn", fn.sum(), row["fn"])):
        if float(got) != float(want):
            failures.append(f"{name} {got} != swept {want}")
    got_f1 = r2.micro_f1(tp.sum(), fp.sum(), fn.sum())
    if abs(got_f1 - row["micro_f1_50"]) > 1e-9:
        failures.append(f"micro_f1_50 {got_f1!r} != swept {row['micro_f1_50']!r}")
    truth, pred, _conf = r2.tile_vectors(sub, ref, bounds)
    tile = {
        "tile_tp": int((pred & truth).sum()),
        "tile_fp": int((pred & ~truth).sum()),
        "tile_fn": int((~pred & truth).sum()),
        "tile_tn": int((~pred & ~truth).sum()),
    }
    for key, got_i in tile.items():
        if got_i != row[key]:
            failures.append(f"{key} {got_i} != swept {row[key]}")
    got_mcc = float(r2.mcc_from_confusion(
        tile["tile_tp"], tile["tile_tn"], tile["tile_fp"], tile["tile_fn"]))
    if abs(got_mcc - row["tile_mcc"]) > 1e-9:
        failures.append(f"tile_mcc {got_mcc!r} != swept {row['tile_mcc']!r}")
    return failures


def stage_materialise() -> int:
    """Build both cells, gate them against the sweep, and record them.

    Returns:
        A process exit status: 0 on success, 1 if any cell fails its gate.
    """
    _select()
    specs = cell_specs()
    frame = r2.rung_frame(ARM, K)
    logger.info("%s: %d candidates", RUNG_LABEL, len(frame))

    points = set(r2.with_carried(r2.achievable_points(frame, K), ARM, K))
    for spec in specs:
        point = (spec["prob_t"], spec["min_votes"])
        if point not in points:
            logger.error("point %s is not on the rung's achievable grid", point)
            return 1

    ref, bounds, tile_index = r2.load_frames()
    built: list[dict[str, Any]] = []
    failures: list[str] = []
    for spec in specs:
        sub = r2.materialise(frame, float(spec["prob_t"]), int(spec["min_votes"]))
        bad = _gate_against_sweep(sub, spec["row"], ref, bounds, tile_index)
        logger.info("gate sweep-identity %-34s n=%5d — %s", spec["label"], len(sub),
                    "OK" if not bad else "FAIL")
        for item in bad:
            logger.error("GATE FAIL %s: %s", spec["label"], item)
        failures.extend(f"{spec['label']}: {item}" for item in bad)
        built.append({"spec": spec, "sub": sub})
    if failures:
        logger.error("nothing written: %d gate failure(s)", len(failures))
        return 1

    cells: list[dict[str, Any]] = []
    for item in built:
        spec, sub = item["spec"], item["sub"]
        dest = RESULTS_HOME / "cells" / spec["label"] / "detections.geojson"
        dest.parent.mkdir(parents=True, exist_ok=True)
        sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
        cells.append({
            "label": spec["label"],
            "rung": RUNG_LABEL,
            "arm": ARM,
            "verifier_model": r2.ARM_MODEL[ARM][0],
            "verifier_thinking": r2.ARM_MODEL[ARM][1],
            "k": K,
            "basis": spec["basis"],
            "point": f"({float(spec['prob_t']):.2f}, k{int(spec['min_votes'])})",
            "n_detections": int(len(sub)),
            "det": str(dest.relative_to(PROJECT_ROOT)),
        })
        logger.info("%-34s n=%5d -> %s", spec["label"], len(sub),
                    dest.relative_to(PROJECT_ROOT))

    manifest = json.loads(MANIFEST.read_text())
    manifest["cells"] = r2.merge_cells(manifest["cells"], cells)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    logger.info("wrote %s (%d cells, %d new or replaced)",
                MANIFEST.relative_to(PROJECT_ROOT), len(manifest["cells"]), len(cells))
    return 0


# ---------------------------------------------------------------------------
# Scoring, on the r2 board's recipe.
# ---------------------------------------------------------------------------


def stage_score(workers: int, jobs: int) -> int:
    """Score both cells with the engine, on the same recipe as the 2x2's cells.

    Args:
        workers: Engine parallelism per cell.
        jobs: Cells scored concurrently.

    Returns:
        A process exit status.
    """
    manifest = json.loads(MANIFEST.read_text())
    cells = [c for c in manifest["cells"] if c["label"] in (CARRIED_LABEL, ORACLE_LABEL)]
    if len(cells) != 2:
        logger.error("expected both T5m cells in the manifest, found %d", len(cells))
        return 2
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", *[c["det"] for c in cells]],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip()
    if dirty:
        logger.error(
            "detections not committed — the engine's --require-clean-inputs "
            "would refuse them. Commit these first:\n%s", dirty)
        return 4

    def run_one(cell: dict[str, Any]) -> tuple[str, int]:
        out_dir = str((RESULTS_HOME / "cells" / cell["label"]).relative_to(PROJECT_ROOT))
        cmd = r2.engine_command(cell["det"], out_dir, cell["label"], workers)
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                              text=True, check=False)
        (RESULTS_HOME / "cells" / cell["label"] / "score.log").write_text(
            proc.stdout + proc.stderr)
        return cell["label"], proc.returncode

    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for label, rc in pool.map(run_one, cells):
            logger.info("scored %-34s rc=%d", label, rc)
            if rc != 0:
                failed.append(label)
    if failed:
        logger.error("scoring FAILED for %s — see each cell's score.log", failed)
        return 1
    logger.info("scored %d cells", len(cells))
    return 0


# ---------------------------------------------------------------------------
# The three paired tests.
# ---------------------------------------------------------------------------


def _declared_t5() -> dict[str, dict[str, Any]]:
    """The declared T5 rows the reproduction gate compares against.

    Returns:
        ``{"f1": row, "mcc": row}`` from ``tests_2x2_K3.json``.

    Raises:
        SystemExit: If either row is not the T5 row it is expected to be.
    """
    declared = json.loads(DECLARED_TESTS.read_text())
    rows = {"f1": declared["f1_tests"][T5_ROW], "mcc": declared["mcc_tests"][T5_ROW]}
    for metric, row in rows.items():
        if row.get("test") != "T5" or row.get("a") != DECLARED_T5_CELL:
            raise SystemExit(
                f"{DECLARED_TESTS}: {metric}_tests[{T5_ROW}] is not the declared "
                f"T5 row (test={row.get('test')!r}, a={row.get('a')!r})")
    return rows


def _check_reproduction(metric: str, got: dict[str, Any],
                        want: dict[str, Any]) -> list[str]:
    """Compare a reproduced declared-T5 row with the committed one.

    Both are produced by the same rounding in ``permutation_test_float`` /
    ``permutation_test_mcc`` (six places on the statistics, four on the
    p-value), so equality is exact rather than tolerant: a difference of one
    unit in the last place means a different input, not a different adder.

    Args:
        metric: ``"f1"`` or ``"mcc"``.
        got: The row this run produced.
        want: The committed row.

    Returns:
        Failure descriptions, empty on an exact reproduction.
    """
    keys = ["observed_diff", "p_value", "null_mean", "null_std", "n_tiles",
            f"{metric}_a", f"{metric}_b"]
    return [f"{metric} {k}: {got[k]!r} != committed {want[k]!r}"
            for k in keys if got[k] != want[k]]


def cell_records(by_label: dict[str, dict[str, Any]], cells: dict[str, dict[str, Any]],
                 im_k3: Any) -> dict[str, dict[str, Any]]:
    """The ``cells`` block of the output file: what each cell is and where.

    Args:
        by_label: The campaign manifest's cells, keyed by label.
        cells: The per-cell vectors computed for the tests, keyed by label.
        im_k3: The ``IM-k3`` comparator record from the r2 module.

    Returns:
        One record per cell, keyed by label.
    """
    out: dict[str, dict[str, Any]] = {}
    for label in (CARRIED_LABEL, ORACLE_LABEL, DECLARED_T5_CELL, "IM-k3"):
        if label in by_label:
            det = by_label[label]["det"]
            point = by_label[label]["point"]
        else:
            det, point = im_k3.detections, f"({MATCHED_PROB:.2f}, k{MIN_VOTES})"
        out[label] = {
            "label": label,
            "det": det,
            "point": point,
            "n": cells[label]["n"],
            "confusion": cells[label]["confusion"],
        }
    return out


def stage_tests() -> int:
    """Run T5m and its oracle twin, plus the declared T5 for the record.

    Returns:
        A process exit status: 0 on success, 3 on a truth-vector mismatch,
        5 if the declared T5 pair is not reproduced.
    """
    _select()
    manifest = json.loads(MANIFEST.read_text())
    by_label = {c["label"]: c for c in manifest["cells"]}
    for label in (CARRIED_LABEL, ORACLE_LABEL, DECLARED_T5_CELL):
        if label not in by_label:
            logger.error("cell %s is not in %s", label, MANIFEST)
            return 2

    im_k3 = next(c for c in r2.COMPARATORS if c.label == "IM-k3")
    ref, bounds, tile_index = r2.load_frames()

    def vectors(det_path: Path) -> dict[str, Any]:
        """Per-tile counts, per-tile vectors and the confusion for one cell."""
        det = r2.read_detections(det_path)
        tp, fp, fn = r2.per_tile_arrays(det, ref, bounds, tile_index)
        truth, pred, conf = r2.tile_vectors(det, ref, bounds)
        return {"tp": tp, "fp": fp, "fn": fn, "truth": truth, "pred": pred,
                "confusion": conf, "n": int(len(det))}

    cells = {
        "IM-k3": vectors(PROJECT_ROOT / im_k3.detections),
        CARRIED_LABEL: vectors(PROJECT_ROOT / by_label[CARRIED_LABEL]["det"]),
        ORACLE_LABEL: vectors(PROJECT_ROOT / by_label[ORACLE_LABEL]["det"]),
        DECLARED_T5_CELL: vectors(PROJECT_ROOT / by_label[DECLARED_T5_CELL]["det"]),
    }
    truth = cells["IM-k3"]["truth"]
    for label, cell in cells.items():
        if not np.array_equal(truth, cell["truth"]):
            logger.error("truth vectors differ for %s — different frames", label)
            return 3
    logger.info("gate shared-truth: %d tiles, %d positive — OK",
                len(truth), int(truth.sum()))

    pairs = [
        ("T5m", "protocol-matched confound check vs IM-k3", CARRIED_LABEL,
         "the matched comparator: same pool depth (5 passes), same vote count "
         "(3), same probability threshold (0.15), same verifier arm"),
        ("T5m-oracle", "protocol-matched confound check at the F1 oracle",
         ORACLE_LABEL,
         "the same matched comparator read at its own best micro-F1 row with "
         "min_votes 3, so the carried-versus-oracle tax is visible"),
        ("T5-declared", "the declared T5, reproduced for the record",
         DECLARED_T5_CELL,
         "3-of-3 unanimity on a three-pass pool against IM-k3's 3-of-5 "
         "majority on a five-pass pool; reproduced here as a pipeline gate, "
         "with its verdict unchanged in tests_2x2_K3.json"),
    ]
    b = cells["IM-k3"]
    f1_rows, mcc_rows = [], []
    for tid, name, label, contrast in pairs:
        a = cells[label]
        f1_rows.append({
            "test": tid, "name": name, "a": label, "b": "IM-k3",
            "contrast": contrast,
            **r2.permutation_test_float(a["tp"], a["fp"], a["fn"],
                                        b["tp"], b["fp"], b["fn"],
                                        n_permutations=r2.N_PERMS, seed=r2.SEED)})
        mcc_rows.append({
            "test": tid, "name": name, "a": label, "b": "IM-k3",
            "contrast": contrast,
            **r2.permutation_test_mcc(a["pred"], b["pred"], truth,
                                      n_permutations=r2.N_PERMS, seed=r2.SEED)})

    declared = _declared_t5()
    reproduction: list[str] = []
    for metric, rows in (("f1", f1_rows), ("mcc", mcc_rows)):
        got = next(r for r in rows if r["test"] == "T5-declared")
        bad = _check_reproduction(metric, got, declared[metric])
        logger.info("gate declared-T5 %-4s d=%+.6f p=%.4f vs committed "
                    "d=%+.6f p=%.4f — %s", metric.upper(), got["observed_diff"],
                    got["p_value"], declared[metric]["observed_diff"],
                    declared[metric]["p_value"], "OK" if not bad else "FAIL")
        for item in bad:
            logger.error("GATE FAIL %s", item)
        reproduction.extend(bad)
    if reproduction:
        logger.error("the declared T5 pair is NOT reproduced — stopping without "
                     "writing. This pipeline is not the pipeline that produced "
                     "%s.", DECLARED_TESTS.relative_to(PROJECT_ROOT))
        return 5

    out = {
        "declaration": DECLARATION,
        "declaration_section": "3a — T5m, protocol-matched confound check",
        "rung": 3,
        "status": "additional (post-hoc, PI ruling 2026-09-20)",
        "why": (
            "The declared T5 matches the absolute vote count across pools of "
            "different depth, which converts the passes confound into a "
            "vote-fraction confound of 1.0 against 0.6. The protocol-matched "
            "comparator is the September Gemini 3 pool at K = 5 read at "
            "min_votes 3 (results/im-june-pool-grid-2026-09-20/findings.md "
            "section 6). T5m adds that comparison; it does not replace T5, "
            "whose verdict stands as committed in "
            "results/image-2x2-2026-09-19/tests_2x2_K3.json."
        ),
        "cells": cell_records(by_label, cells, im_k3),
        "buffer_m": r2.BUFFER_M,
        "reference": r2.REFERENCE,
        "n_permutations": r2.N_PERMS,
        "seed": r2.SEED,
        "multiplicity": (
            "No Benjamini-Hochberg adjustment. T5m is one declared contrast "
            "reported with its own F1-oracle twin, plus the declared T5 pair "
            "re-run as a pipeline gate — not a new declared family. Raw "
            "p-values are reported. The declared family's correction is "
            "unchanged: it remains the five tests of tests_2x2_K3.json, and "
            "nothing here enters it."
        ),
        "f1_tests": f1_rows,
        "mcc_tests": mcc_rows,
    }
    TESTS_HOME.mkdir(parents=True, exist_ok=True)
    dest = TESTS_HOME / "tests_t5m_K3.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    for metric, rows in (("f1", f1_rows), ("mcc", mcc_rows)):
        for row in rows:
            logger.info("%-3s %-12s %-34s %.4f vs %.4f  d=%+.4f p=%.4f",
                        metric.upper(), row["test"], row["a"],
                        row[f"{metric}_a"], row[f"{metric}_b"],
                        row["observed_diff"], row["p_value"])
    logger.info("wrote %s", dest.relative_to(PROJECT_ROOT))
    return 0


def main() -> int:
    """Entry point. Returns a process exit status."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True,
                    choices=["materialise", "score", "tests"])
    ap.add_argument("--workers", type=int, default=5,
                    help="Engine parallelism per cell in --stage score (default 5)")
    ap.add_argument("--jobs", type=int, default=2,
                    help="Cells scored concurrently in --stage score (default 2)")
    args = ap.parse_args()
    if args.stage == "materialise":
        return stage_materialise()
    if args.stage == "score":
        return stage_score(args.workers, args.jobs)
    return stage_tests()


if __name__ == "__main__":
    sys.exit(main())
