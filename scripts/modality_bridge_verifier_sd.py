#!/usr/bin/env python3
"""
Run C: the verifier's re-invocation SD on Run B's cells, and § 7's floors with it.

Why this exists
---------------
Run B's floors (``results/modality-bridge-2026-10-07/findings.md`` § 7,
``scripts/modality_bridge_floors.py``) hold the verifier fixed and add a
borrowed verifier band of 0.001 per contrast. An independent audit
(``reports/s163-agent-records/run-b-floors-audit.md``, finding 1) judged that
band too small for the 487-tile frame. Run C
(``planning/run-c-verifier-reinvocation-2026-10-08.md``) verified each of Run
B's ten Stage 2 legs twice more, with byte-identical requests, so each
committed cell now has three verifier replicates: replicate 1 (the committed
legs, 2026-10-07) and replicates 2 and 3 (2026-10-08). This script measures
the verifier's re-invocation standard deviation (SD) per cell and recomputes
§ 7's gap and gap-change floors with it, as the card's § 7 fixed before any
replicate result existed:

1. **Cells.** Every committed verified set (``best``, ``op``, ``ladder5``) at
   its own committed point (prob_t, k), scored at 20 m on the 487-tile frame
   for each replicate. ``best`` and ``op`` apply the point to the union joined
   to the replicate's probabilities (``image_b_analysis.load_image_union``,
   join-gated); ``ladder5`` rebuilds the first-five rung and re-inherits each
   replicate's probabilities within 10 m (the floors' subset machinery).
2. **Flips.** Candidate accept/reject decisions at each set's point, among
   the candidates its vote gate admits: pairwise flip rates, and the share
   split across the three replicates.
3. **Verifier SD.** The sample SD of the three F1s (two degrees of freedom),
   its 95 % chi-square interval and the range. Sensitivity: a pooled SD per
   verifier family over one set per leg (``best``).
4. **Floors.** 1.96 · √(Σ proposer SD² + Σ verifier SD²) for every gap (two
   cells) and gap change (four cells), the measured verifier variance in
   place of the 0.001-per-contrast band. The proposer SDs are the committed
   ones (``floors/floors.json``), read, not recomputed. Readings: point,
   upper (proposer upper SDs), direct and § 3 (as § 7), and two verifier
   sensitivities (each cell's verifier SD at its chi-square upper bound; the
   pooled family SD). Per contrast, the break-even verifier SD: the SD that,
   on every cell alike, brings the ratio to 1.

Gates (nothing is written unless every one passes)
--------------------------------------------------
1. Replicate 1 reproduces every committed set exactly: per-tile TP, FP and FN
   equal to the committed verified set's (so the same F1), and the F1 within
   1e-3 of ``analysis.json`` (floors gate 2).
2. The deduplicated passes the ``ladder5`` rungs are built from are the ones
   the floors used (SHA-256 against ``floors/gates.json``).
3. The committed floors re-derive from the committed cell SDs (every gap and
   gap-change floor, to 1e-12), so the cells read are the cells § 7 used.
4. Every replicate covers every union candidate (the join gate), and its
   probabilities come from the repaired copy (``_repaired``), as Stage 2
   scored replicate 1.

Usage::

    python scripts/modality_bridge_verifier_sd.py \\
        --out-dir results/modality-bridge-2026-10-07/verifier-sd

Zero API. Run on sapphire (the ``ladder5`` rungs need the arm's deduplicated
passes, under ``<arm>/scoring/`` there; ``--scoring-root`` points elsewhere).

Created: 2026-10-08
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import logging
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import modality_bridge_floors as fl  # noqa: E402

logger = logging.getLogger(__name__)

#: Replicates: 1 is the committed Stage 2 leg, 2 and 3 are Run C's.
REPS: tuple[int, ...] = (1, 2, 3)
#: Two-sided level of the chi-square interval for an SD.
CI_LEVEL = 0.95
#: Leg label (floors) -> the verifier family it names.
FAMILY = {"g3v": "Gemini 3", "g37v": "Gemini 3.7"}
#: Verifier SDs measured in June on the same frame (single-run F1 SD, five
#: iterations, T 0.0; ``results/verifier-robustness/verifier-robustness-findings.md`` § 2).
JUNE_G3_RANGE = (0.0025, 0.0072)


# --------------------------------------------------------------------------- #
# Pure functions (tier-1 tested in tests/test_modality_bridge_verifier_sd.py).
# --------------------------------------------------------------------------- #


def rep_dir(base: str, rep: int) -> str:
    """The verify directory a replicate is scored from.

    Replicate 1 is read where the floors read it (``verify_g3`` for the three
    legs whose repaired copies were never committed and changed no row;
    ``verify_<v>_repaired`` otherwise). Replicates 2 and 3 are read from
    their repaired copies.

    Args:
        base: The floors' replicate-1 directory (``fl.ARMS[...].legs``).
        rep: Replicate number.

    Returns:
        The directory name under ``verifier/<cell>/``.

    Examples:
        >>> rep_dir("verify_g3", 1), rep_dir("verify_g3", 2)
        ('verify_g3', 'verify_g3_rep2_repaired')
        >>> rep_dir("verify_g37_repaired", 3)
        'verify_g37_rep3_repaired'
    """
    if rep == 1:
        return base
    v = base.removeprefix("verify_").removesuffix("_repaired")
    return f"verify_{v}_rep{rep}_repaired"


def chi2_sd_interval(sd: float, df: int, level: float = CI_LEVEL) -> tuple[float, float]:
    """Chi-square confidence interval for a normal SD estimated with ``df`` degrees of freedom.

    ``[s · √(df / χ²_{1−α/2, df}), s · √(df / χ²_{α/2, df})]``.

    Args:
        sd: The sample SD.
        df: Its degrees of freedom (n − 1 for one sample).
        level: Two-sided confidence level.

    Returns:
        ``(lower, upper)``.

    Examples:
        >>> lo, hi = chi2_sd_interval(1.0, 2)
        >>> round(lo, 4), round(hi, 4)
        (0.5207, 6.2847)
    """
    from scipy.stats import chi2

    a = 1.0 - level
    return (float(sd * np.sqrt(df / chi2.ppf(1 - a / 2, df))),
            float(sd * np.sqrt(df / chi2.ppf(a / 2, df))))


def sd_summary(values: Sequence[float]) -> dict[str, Any]:
    """Mean, sample SD, its chi-square interval and the range of replicate values.

    Args:
        values: One value per replicate (at least two).

    Returns:
        ``n``, ``mean``, ``sd`` (divisor n − 1), ``df``, ``sd_ci95``,
        ``range`` (max − min), ``min`` and ``max``.

    Examples:
        >>> s = sd_summary([0.90, 0.91, 0.92])
        >>> round(s["sd"], 6), round(s["range"], 6), s["df"]
        (0.01, 0.02, 2)
    """
    v = np.asarray(values, dtype=float)
    sd = float(np.std(v, ddof=1))
    return {"n": int(len(v)), "mean": float(v.mean()), "sd": sd, "df": int(len(v) - 1),
            "sd_ci95": list(chi2_sd_interval(sd, len(v) - 1)),
            "range": float(v.max() - v.min()), "min": float(v.min()), "max": float(v.max())}


def pooled_sd(sds: Sequence[float], dfs: Sequence[int]) -> dict[str, Any]:
    """Pooled SD of independent samples: √(Σ dfᵢ sᵢ² / Σ dfᵢ), with its interval.

    Args:
        sds: Each sample's SD.
        dfs: Each sample's degrees of freedom.

    Returns:
        ``sd``, ``df`` and ``sd_ci95``.

    Examples:
        >>> round(pooled_sd([0.003, 0.004], [2, 2])["sd"], 6)
        0.003536
    """
    s = np.asarray(sds, dtype=float)
    d = np.asarray(dfs, dtype=float)
    sd = float(np.sqrt(np.sum(d * s ** 2) / d.sum()))
    return {"sd": sd, "df": int(d.sum()), "sd_ci95": list(chi2_sd_interval(sd, int(d.sum())))}


def floor_with_verifier(proposer_sds: Sequence[float], verifier_sds: Sequence[float]) -> float:
    """Floor of a signed sum of independent cells, both variance sources in quadrature.

    ``1.96 · √(Σ proposer SD² + Σ verifier SD²)``: the measured verifier
    variance replaces § 7's linear band of 0.001 per contrast.

    Args:
        proposer_sds: Each cell's run-to-run (proposer) SD.
        verifier_sds: Each cell's verifier re-invocation SD, in the same order.

    Returns:
        The floor.

    Raises:
        ValueError: If the two lists differ in length.

    Examples:
        >>> round(floor_with_verifier([0.003], [0.004]), 6)
        0.0098
    """
    if len(proposer_sds) != len(verifier_sds):
        raise ValueError("one verifier SD per cell")
    p = np.asarray(proposer_sds, dtype=float)
    v = np.asarray(verifier_sds, dtype=float)
    return float(fl.Z * np.sqrt(np.sum(p ** 2) + np.sum(v ** 2)))


def break_even_sd(estimate: float, proposer_sds: Sequence[float]) -> float:
    """The verifier SD, equal on every cell, at which |estimate| equals its floor.

    Solves ``|estimate| = 1.96 · √(Σ p² + m s²)`` for s, with m cells. Zero
    when the proposer SDs alone already reach the estimate.

    Args:
        estimate: The contrast (a gap or a gap change).
        proposer_sds: Its cells' proposer SDs.

    Returns:
        The break-even per-cell verifier SD.

    Examples:
        >>> s = break_even_sd(0.05, [0.01, 0.01])
        >>> round(floor_with_verifier([0.01, 0.01], [s, s]), 6)
        0.05
        >>> break_even_sd(0.01, [0.01, 0.01])
        0.0
    """
    p2 = float(np.sum(np.square(np.asarray(proposer_sds, dtype=float))))
    room = (abs(estimate) / fl.Z) ** 2 - p2
    return float(np.sqrt(room / len(proposer_sds))) if room > 0 else 0.0


def flip_rates(accepts: Sequence[np.ndarray]) -> dict[str, Any]:
    """Accept/reject flips between replicates over the same candidates.

    Args:
        accepts: One boolean array per replicate, aligned candidate for
            candidate.

    Returns:
        ``n`` candidates, ``pairwise`` (``"1-2"`` -> rate and count), the
        mean pairwise rate, and ``split`` (rate and count of candidates whose
        decision is not unanimous across all replicates).

    Examples:
        >>> r = flip_rates([np.array([1, 1, 0, 0], bool), np.array([1, 0, 0, 0], bool),
        ...                 np.array([1, 1, 0, 1], bool)])
        >>> r["pairwise"]["1-2"]["count"], r["split"]["count"], r["n"]
        (1, 2, 4)
    """
    a = [np.asarray(x, dtype=bool) for x in accepts]
    n = int(len(a[0]))
    pairs = {}
    for i, j in itertools.combinations(range(len(a)), 2):
        c = int((a[i] != a[j]).sum())
        pairs[f"{i + 1}-{j + 1}"] = {"count": c, "rate": c / n if n else float("nan")}
    stack = np.vstack(a) if n else np.zeros((len(a), 0), bool)
    split = int((stack.any(axis=0) & ~stack.all(axis=0)).sum())
    return {"n": n, "pairwise": pairs,
            "pairwise_mean_rate": float(np.mean([p["rate"] for p in pairs.values()])),
            "split": {"count": split, "rate": split / n if n else float("nan")}}


# --------------------------------------------------------------------------- #
# Loading and scoring (sapphire).
# --------------------------------------------------------------------------- #


def sha256(path: Path) -> str:
    """Hex SHA-256 of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_replicates(reps: Sequence[int] = REPS
                    ) -> tuple[dict[tuple[str, str, int], Any], dict[str, Any], list[str]]:
    """Every leg's gated union joined to each replicate's probabilities.

    Args:
        reps: The replicates to load (``--gate-only`` loads replicate 1).

    Returns:
        ``(unions, provenance, failures)``: per (arm, leg, rep) the gated union;
        per leg and replicate the directory, the probabilities file's SHA-256
        and its repair record; gate 4's failures (a replicate that does not
        cover its union).
    """
    from scripts import image_b_analysis as iba
    from scripts.grid_verifier_analysis import JoinGateError
    from scripts.stride_verifier_analysis import reassign_gate

    unions: dict[tuple[str, str, int], Any] = {}
    prov: dict[str, Any] = {}
    failures: list[str] = []
    for name, arm in fl.ARMS.items():
        vroot = fl.OUTPUTS / name / "verifier" / arm.cell
        for leg, base in arm.legs:
            for rep in reps:
                vdir = rep_dir(base, rep)
                key = f"{name}/{leg}/rep{rep}"
                try:
                    u = reassign_gate(iba.load_image_union(vroot, arm.union_name, vdir),
                                      fl._G["bounds"], key)
                except (JoinGateError, FileNotFoundError) as exc:
                    failures.append(f"{key}: {exc}")
                    continue
                unions[(name, leg, rep)] = u
                rec = vroot / vdir / "parse_repair.json"
                repair = json.loads(rec.read_text()) if rec.exists() else None
                prov[key] = {
                    "dir": str((vroot / vdir).relative_to(PROJECT_ROOT)),
                    "probabilities_sha256": sha256(vroot / vdir / "probabilities.json"),
                    "n": int(len(u)),
                    "parse_error_rows": None if repair is None else repair["n_parse_error_rows"],
                    "repaired": None if repair is None else len(repair["changed"]),
                    "unrecovered": None if repair is None else len(repair["unrecovered"]),
                }
    return unions, prov, failures


def first_five_rung(name: str, scoring_root: Path) -> tuple[Any, np.ndarray, np.ndarray]:
    """The first-five rung of a ten-pass arm and its inheritance into the union.

    Returns:
        ``(rung, idx, matched)`` as ``modality_bridge_floors.subset_job`` builds
        them for the subset (0, 1, 2, 3, 4).
    """
    arm = fl.ARMS[name]
    passes = fl.load_passes(scoring_root / name / "scoring", arm.cell, arm.n_passes)
    rung = fl.build_rung(passes[:5])
    xy = np.c_[rung.geometry.x.to_numpy(), rung.geometry.y.to_numpy()]
    union_xy = fl._G["union_xy"][name]
    _dist, idx, matched = fl.inherit_index(xy, union_xy)
    return rung, idx, matched


def replicate_set(union: Any, kind: str, point: tuple[float, int],
                  rung: tuple[Any, np.ndarray, np.ndarray] | None) -> tuple[Any, np.ndarray]:
    """One replicate's verified set at a committed point, and its accept mask.

    Args:
        union: The gated union joined to the replicate's probabilities.
        kind: ``best``, ``op`` or ``ladder5``.
        point: ``(prob_t, k)``.
        rung: For ``ladder5``, the first-five rung, its inheritance index and
            match mask (:func:`first_five_rung`).

    Returns:
        ``(verified set, accept mask over the vote-admitted candidates)``.
    """
    from scripts.grid_verifier_analysis import verified_subset

    prob_t, k = point
    if kind == "ladder5":
        r, idx, matched = rung
        cell = r.copy()
        cell["mound_probability"] = union["mound_probability"].to_numpy()[idx]
        cell = cell[matched].copy()
    else:
        cell = union
    admitted = cell["vote_count"].to_numpy() >= k
    accept = cell["mound_probability"].to_numpy()[admitted] >= prob_t
    return verified_subset(cell, prob_t, k), accept


# --------------------------------------------------------------------------- #
# Analysis.
# --------------------------------------------------------------------------- #


def score_cells(sets: Mapping[tuple[str, str], Any], unions: Mapping[tuple, Any],
                rungs: Mapping[str, Any], reps: Sequence[int] = REPS
                ) -> tuple[dict[str, Any], list[str]]:
    """Every committed set under each replicate, gated on replicate 1.

    Args:
        sets: The committed sets (``modality_bridge_floors.load_committed_sets``).
        unions: Per (arm, leg, rep) the gated union (:func:`load_replicates`).
        rungs: Per ten-pass arm its first-five rung (:func:`first_five_rung`).
        reps: The replicates to score; replicate 1 must come first. With
            replicate 1 alone (``--gate-only``) only the gate is computed.

    Returns:
        ``(cells, failures)``: per ``cell/kind`` the point, the F1 and counts
        per replicate, the SD summary, the replicate-1 minus mean-of-others
        difference and the flips; gate 1's failures.
    """
    out: dict[str, Any] = {}
    failures: list[str] = []
    for (cell, kind), s in sets.items():
        arm, leg = fl.CELLS[cell]
        f1s, accepts, totals = [], [], []
        for rep in reps:
            vset, accept = replicate_set(unions[(arm, leg, rep)], kind, s["point"],
                                         rungs.get(arm))
            c = fl.counts_of(vset)
            f1s.append(fl.micro(c))
            accepts.append(accept)
            totals.append({k: int(c[k].sum()) for k in ("tp", "fp", "fn")}
                          | {"n_det": int(len(vset))})
            if rep == 1:
                equal = all(np.array_equal(c[k], s["counts"][k]) for k in ("tp", "fp", "fn"))
                if not equal or f1s[0] != s["f1"] or not s["ok"]:
                    failures.append(f"{cell}/{kind}: replicate 1 {f1s[0]:.6f} does not "
                                    f"reproduce the committed set ({s['f1']:.6f})")
        label = f"{cell}/{kind}"
        out[label] = {"cell": cell, "kind": kind, "arm": arm, "leg": leg,
                      "verifier": FAMILY[leg], "point": list(s["point"]),
                      "committed_f1": s["committed_f1"], "f1": dict(zip(map(str, reps), f1s)),
                      "totals": dict(zip(map(str, reps), totals))}
        if len(reps) > 1:
            out[label].update({**sd_summary(f1s),
                               "rep1_minus_mean_later": f1s[0] - float(np.mean(f1s[1:])),
                               "flips": flip_rates(accepts)})
        logger.info("%-30s %s F1 %s", label, s["point"], " ".join(f"{x:.4f}" for x in f1s))
    return out, failures


def union_flips(unions: Mapping[tuple, Any], reps: Sequence[int] = REPS) -> dict[str, Any]:
    """Per leg: the share of union candidates whose probability changes, and flips at 0.5.

    Returns:
        Per ``arm/leg``: candidates, pairwise share with any probability
        change, and the accept flips over the whole union at prob_t 0.5 (a
        common reference point; the cells' own points are in ``cells``).
    """
    out = {}
    for name, arm in fl.ARMS.items():
        for leg, _base in arm.legs:
            probs = [unions[(name, leg, r)]["mound_probability"].to_numpy() for r in reps]
            changed = {f"{i + 1}-{j + 1}": float(np.mean(probs[i] != probs[j]))
                       for i, j in itertools.combinations(range(len(reps)), 2)}
            out[f"{name}/{leg}"] = {"n": int(len(probs[0])), "prob_changed_share": changed,
                                    "flips_at_0.5": flip_rates([p >= 0.5 for p in probs])}
    return out


def committed_floor_gate(floors: Mapping[str, Any], gap_change: Mapping[str, Any]
                         ) -> tuple[dict[str, Any], list[str]]:
    """Gate 3: the committed floors re-derive from the committed cell SDs.

    Returns:
        ``(contrasts, failures)``: per gap and gap change its cells
        (``cell/kind`` in contrast order) and the committed record.
    """
    contrasts: dict[str, Any] = {}
    failures: list[str] = []
    cells = floors["cells"]
    for gap, (text, image, kind, _f, _l) in fl.GAPS.items():
        members = [f"{text}/{kind}", f"{image}/{kind}"]
        contrasts[gap] = {"type": "gap", "cells": members, "committed": floors["gaps"][gap]}
    for label, _g37, _g3, tier in fl.GAP_CHANGES:
        rec = gap_change[label]["cells"]
        members = [f"{rec[r][0]}/{rec[r][1]}" for r in ("T37", "I37", "T3", "I3")]
        contrasts[label] = {"type": "gap change", "tier": tier, "cells": members,
                            "committed": floors["gap_changes"][label]}
    for label, c in contrasts.items():
        n = 1 if c["type"] == "gap" else 2
        sds = [cells[m]["sd"] for m in c["cells"]]
        ups = [cells[m]["sd_upper"] for m in c["cells"]]
        for key, vals in (("floor", sds), ("floor_upper", ups)):
            again = fl.contrast_floor(vals, n)
            if abs(again - c["committed"][key]) > 1e-12:
                failures.append(f"{label}: {key} {again} does not re-derive "
                                f"{c['committed'][key]}")
    return contrasts, failures


def floors_with_verifier(contrasts: Mapping[str, Any], floors: Mapping[str, Any],
                         cells: Mapping[str, Any], pooled: Mapping[str, Any]
                         ) -> dict[str, Any]:
    """Every gap and gap change against its floor with the measured verifier SD.

    Returns:
        Per contrast: the estimate, the committed floors and ratios, and the
        new floors and ratios (point, upper, direct, § 3; verifier at its
        chi-square upper bound; pooled family SD), the cells' verifier SDs and
        the break-even verifier SD.
    """
    fc = floors["cells"]
    out = {}
    for label, c in contrasts.items():
        com = c["committed"]
        est = com["estimate"]
        m = c["cells"]
        p_sd = [fc[x]["sd"] for x in m]
        p_up = [fc[x]["sd_upper"] for x in m]
        p_dir = [fc[x]["sd_direct"] for x in m]
        p_s3 = [fl.s3_floor_as_sd(fc[x]["s3_floor"]) for x in m]
        v_sd = [cells[x]["sd"] for x in m]
        v_up = [cells[x]["sd_ci95"][1] for x in m]
        v_pool = [pooled[cells[x]["verifier"]]["sd"] for x in m]
        # Added after the results (not in the card's § 7 plan): each cell at
        # its family's pooled 95 % upper bound, a tighter upper reading than
        # a single cell's two-degree-of-freedom interval.
        v_pool_up = [pooled[cells[x]["verifier"]]["sd_ci95"][1] for x in m]
        new = {
            "floor": floor_with_verifier(p_sd, v_sd),
            "floor_upper": floor_with_verifier(p_up, v_sd),
            "floor_direct": floor_with_verifier(p_dir, v_sd),
            "s3_floor": floor_with_verifier(p_s3, v_sd),
            "floor_verifier_upper": floor_with_verifier(p_sd, v_up),
            "floor_verifier_pooled": floor_with_verifier(p_sd, v_pool),
            "floor_verifier_pooled_upper": floor_with_verifier(p_sd, v_pool_up),
        }
        ratios = {k.replace("floor", "ratio") if k != "s3_floor" else "s3_ratio":
                  abs(est) / v for k, v in new.items()}
        out[label] = {
            "type": c["type"], "tier": c.get("tier"), "cells": m, "estimate": est,
            "p": com.get("p_modality_swap"),
            "committed": {k: com[k] for k in ("floor", "floor_upper", "floor_direct",
                                              "s3_floor", "ratio", "ratio_upper",
                                              "ratio_direct", "s3_ratio")},
            "with_verifier": {**new, **ratios},
            "verifier_sds": v_sd, "proposer_sds": p_sd,
            "break_even_verifier_sd": break_even_sd(est, p_sd),
            "break_even_verifier_sd_upper": break_even_sd(est, p_up),
        }
        logger.info("%-34s %+.4f ratio %.2f -> %.2f (break-even verifier SD %.4f)", label,
                    est, com["ratio"], ratios["ratio"], out[label]["break_even_verifier_sd"])
    return out


def write_summary(path: Path, cells: Mapping[str, Any], floors: Mapping[str, Any]) -> None:
    """Two-part CSV: one row per cell, then one per contrast."""
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["kind", "label", "point", "f1_rep1", "f1_rep2", "f1_rep3", "sd",
                    "sd_ci95_lo", "sd_ci95_hi", "range", "rep1_minus_mean_later",
                    "flip_split_rate", "flip_pairwise_mean_rate"])
        for label, c in cells.items():
            w.writerow(["cell", label, f"{c['point'][0]},{c['point'][1]}",
                        *(round(c["f1"][str(r)], 6) for r in REPS), round(c["sd"], 6),
                        round(c["sd_ci95"][0], 6), round(c["sd_ci95"][1], 6),
                        round(c["range"], 6), round(c["rep1_minus_mean_later"], 6),
                        round(c["flips"]["split"]["rate"], 6),
                        round(c["flips"]["pairwise_mean_rate"], 6)])
        w.writerow([])
        w.writerow(["kind", "label", "estimate", "committed_ratio", "ratio", "ratio_upper",
                    "ratio_direct", "s3_ratio", "ratio_verifier_upper", "ratio_verifier_pooled",
                    "ratio_verifier_pooled_upper", "break_even_verifier_sd"])
        for label, g in floors.items():
            nv = g["with_verifier"]
            w.writerow([g["type"], label, round(g["estimate"], 6),
                        round(g["committed"]["ratio"], 4), round(nv["ratio"], 4),
                        round(nv["ratio_upper"], 4), round(nv["ratio_direct"], 4),
                        round(nv["s3_ratio"], 4), round(nv["ratio_verifier_upper"], 4),
                        round(nv["ratio_verifier_pooled"], 4),
                        round(nv["ratio_verifier_pooled_upper"], 4),
                        round(g["break_even_verifier_sd"], 6)])


def main(argv: list[str] | None = None) -> int:
    """Run the gates, measure the verifier SDs, recompute the floors, and write.

    Args:
        argv: Command-line arguments (default ``sys.argv[1:]``).

    Returns:
        0 on success, 1 when a gate failed (nothing written).
    """
    import geopandas as gpd

    from scripts.grid_analysis import CRS
    from scripts.stride_verifier_analysis import COMMON_BOUNDS, GROUND_TRUTH

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scoring-root", type=Path, default=fl.OUTPUTS,
                    help="Root holding <arm>/scoring/common/<cell>/run_<N>/ (default: the "
                         "Stage 2 location on sapphire).")
    ap.add_argument("--out-dir", type=Path, default=fl.RESULTS / "verifier-sd")
    ap.add_argument("--gate-only", action="store_true",
                    help="Load replicate 1 only, run every gate, write nothing (a check "
                         "before the replicates land).")
    args = ap.parse_args(argv)
    reps = (1,) if args.gate_only else REPS
    t0 = time.time()

    fl._G["bounds"] = gpd.read_file(COMMON_BOUNDS)
    fl._G["ref"] = gpd.read_file(GROUND_TRUTH).to_crs(CRS)
    floors = json.loads((fl.RESULTS / "floors" / "floors.json").read_text())
    floors_gates = json.loads((fl.RESULTS / "floors" / "gates.json").read_text())
    gap_change = json.loads((fl.RESULTS / "floors" / "gap_change.json").read_text())
    gates: dict[str, Any] = {}
    failures: list[str] = []

    # Gate 4 first: every replicate covers its union (join gate).
    unions, prov, fail4 = load_replicates(reps)
    gates["replicates"] = prov
    failures += fail4
    # Gate 3: the committed floors re-derive from the committed cell SDs.
    contrasts, fail3 = committed_floor_gate(floors, gap_change)
    failures += fail3
    # Gate 2: the passes the ladder5 rungs are built from are the floors'.
    passes_sha = {}
    for name in ("g3-text", "g3-image"):
        arm = fl.ARMS[name]
        base = args.scoring_root / name / "scoring" / "common" / arm.cell
        passes_sha[name] = {f"run_{i}": sha256(base / f"run_{i}" / "detections_dedup.geojson")
                            for i in range(1, arm.n_passes + 1)}
        if passes_sha[name] != floors_gates["scoring_passes_sha256"][name]:
            failures.append(f"{name}: deduplicated passes differ from the floors'")
    gates["scoring_passes_sha256"] = passes_sha
    if failures:
        logger.error("gates FAILED: %s", failures)
        return 1

    # Gate 1 inside the scoring: replicate 1 reproduces every committed set.
    _analyses, sets, fail_sets = fl.load_committed_sets()
    if fail_sets:
        logger.error("committed sets do not re-score: %s", fail_sets)
        return 1
    fl._G["union_xy"] = {}
    for name in ("g3-text", "g3-image"):
        u = unions[(name, "g3v", 1)]
        fl._G["union_xy"][name] = np.c_[u.geometry.x.to_numpy(), u.geometry.y.to_numpy()]
    rungs = {name: first_five_rung(name, args.scoring_root) for name in ("g3-text", "g3-image")}
    cells, fail1 = score_cells(sets, unions, rungs, reps)
    gates["replicate_1_reproduces"] = {lab: {"f1_rep1": c["f1"]["1"],
                                             "committed_f1": c["committed_f1"]}
                                       for lab, c in cells.items()}
    if fail1:
        logger.error("gate 1 FAILED: %s", fail1)
        return 1
    logger.info("gates passed: %d committed sets reproduced by replicate 1 (%.0f s)",
                len(cells), time.time() - t0)
    if args.gate_only:
        return 0

    # Pooled SD per family over one set per leg (best).
    pooled = {}
    for fam in FAMILY.values():
        best = [c for c in cells.values() if c["kind"] == "best" and c["verifier"] == fam]
        pooled[fam] = {**pooled_sd([c["sd"] for c in best], [c["df"] for c in best]),
                       "cells": [f"{c['cell']}/best" for c in best]}
    report = floors_with_verifier(contrasts, floors, cells, pooled)

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    meta = {"script": "scripts/modality_bridge_verifier_sd.py", "replicates": list(REPS),
            "replicate_dates": {"1": "2026-10-07", "2": "2026-10-08", "3": "2026-10-08"},
            "z": fl.Z, "ci_level": CI_LEVEL, "june_g3_single_run_sd_range": JUNE_G3_RANGE,
            "scoring_root": str(args.scoring_root), "wall_seconds": round(time.time() - t0, 1)}
    (out / "gates.json").write_text(json.dumps({"meta": meta, **gates}, indent=1,
                                               default=float) + "\n")
    (out / "verifier_sd.json").write_text(json.dumps(
        {"meta": meta, "cells": cells, "pooled": pooled, "unions": union_flips(unions)},
        indent=1, default=float) + "\n")
    (out / "floors_with_verifier.json").write_text(json.dumps(
        {"meta": meta, "contrasts": report}, indent=1, default=float) + "\n")
    write_summary(out / "summary.csv", cells, report)
    logger.info("VERIFIER SD COMPLETE -> %s (%.0f s)", out, time.time() - t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
