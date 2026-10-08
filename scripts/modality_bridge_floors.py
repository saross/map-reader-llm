#!/usr/bin/env python3
"""
Run B, scoring plan items 4, 6 and 7: the gap change, the date component, the floors.

Why this exists
---------------
Run B (``planning/modality-bridge-2026-10-07.md``) re-ran the modality claim's
proposer arms on one day, 2026-10-07, on the Batch API, and verified them.
Its first scoring (``scripts/modality-bridge-2026-10-07-score.sh``, results in
``results/modality-bridge-2026-10-07/``) gave the cells and the text − image
gaps with their tile-swap p-values. Three items of the card's § 9 remained:

* **Item 4, the gap change.** A 3.7 gap minus a Gemini 3 gap,
  ``(T37 − I37) − (T3 − I3)``, tested with the grid's interaction instrument,
  ``grid_analysis.paired_interaction``: a paired tile bootstrap interval
  (B = 1,000, seed 42) and the permutation p of
  ``lib_permutation.paired_interaction_permutation`` (10,000, seed 42). The
  four per-tile count arrays are passed as a = T37, b = T3, c = I37, d = I3,
  so each tile swaps its text and image labels within both families
  together, as the card prescribes. A sensitivity passes a = T37, b = I37,
  c = T3, d = I3 (the same statistic, the family labels swapped instead);
  to first order both are the sign-flip test of each tile's contribution to
  the statistic, and they differ only through micro-F1's denominators.
* **Item 6, the date component.** Bridge minus original for each of the six
  D49 cells, at the original operating point and at each side's oracle (its
  own sweep best), with the tile-swap p and same-tile flip rates. It is date
  PLUS serving mode (batch against the originals' real-time tiers), never
  date alone.
* **Item 7, the floors** (PI rulings D45 and D46, method of
  ``reports/w27-replicate-floors-2026-10-06.md`` § 6b and its
  ``floors-v2/`` scripts). Each arm's rung is rebuilt from EVERY subset of
  its passes with the K = 5 ladder's own mechanism (``image_b_analysis``:
  re-cluster the subset, inherit each candidate's verifier probability from
  the arm's union verification within 10 m, so the verifier is held fixed),
  and scored at 20 m on the 487-tile frame along the cell's vote path
  ``k' = round(k / K · K')``. The run-to-run standard deviation (SD) at K'
  passes is ``sqrt(V_sub · N / (N − K'))`` over all C(N, K') subsets, carried
  to K = N by § 6b's rules (ten passes: the larger of a power-law fit, a
  hyperbola fit and the flat K' = 5 value; five passes: the larger of the
  fits and the direct K' = 3 and K' = 4 values). Floors, as § 6b's
  re-screen: two independent cells ``1.96 · sqrt(SD_x² + SD_y²) + 0.001``;
  a gap change of four independent cells ``1.96 · sqrt(ΣSD²) + 0.002`` (the
  verifier re-invocation band of W2.7 § 6, 0.001, once per contrast, added
  linearly). The committed § 3 floors (proposer-only consensus on the
  487-tile corpus) are reported beside them, translated to per-cell SDs
  (SD = floor / (1.96 · √2)) where a contrast has more than two cells.
  Sensitivity (``floor_direct``): the ten-pass arms are subsampled up to
  K' = 9, so their K = 10 SD is also read as the largest DIRECT estimate
  from K' = 5 to 9, which shows how far § 6b's fitted carry moves a floor.

Gates (nothing is written unless every one passes)
--------------------------------------------------
1. The six original cells and three original gaps reproduce
   (``modality_bridge_anchors.run_six_cell_gate``).
2. Every committed Run B verified set re-scores, per tile, to its
   ``analysis.json`` F1 within 1e-3 (the project's mechanism bound).
3. Every committed Run B gap test (``gap_test.json``, ``k5/``,
   ``additions/``) reproduces exactly: both F1s, the difference and the p.
4. The subset machinery: for every arm the all-pass rung reproduces the arm's
   union (count and vote counts; every candidate inherits at distance under
   0.01 m) and every committed cell set exactly (per-tile counts equal); for
   the ten-pass arms the first-five rung reproduces the committed K = 5
   ladder set exactly.

Inputs: committed Run B outputs only, except the deduplicated passes. Stage 2
wrote them under ``<arm>/scoring/`` on sapphire and did not commit them; they
are rebuilt from the committed pass GeoJSONs by
``scripts/modality_bridge_union.py --write --compare-to <committed union>``
into ``--scoring-root`` (the rebuilt unions equal the committed ones). The
first scoring read three Gemini 3 legs' ``verify_g3_repaired/`` copies,
which were not committed either; their ``parse_repair.json`` records no
parse-error row and no change, so this script reads the committed
``verify_g3/`` (gate 2 confirms every F1).

Usage::

    python scripts/modality_bridge_floors.py --scoring-root /tmp/runb-floors \\
        --workers 20 --out-dir results/modality-bridge-2026-10-07/floors

Zero API. Run on sapphire (about ten minutes on 20 workers).

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
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

OUTPUTS = PROJECT_ROOT / "outputs/modality-bridge-2026-10-07"
RESULTS = PROJECT_ROOT / "results/modality-bridge-2026-10-07"
W27_PAIRS = (PROJECT_ROOT
             / "reports/w27-replicate-floors-2026-10-06-scripts/gs_consensus_pairs.csv")

#: Normal quantile for a two-sided 95 % band (D46's 95th percentile of |ΔF1|).
Z = 1.96
#: Verifier re-invocation band per contrast (W2.7 § 6; § 6b adds it to every floor).
VERIFIER_BAND = 0.001
#: Candidate inheritance tolerance (``image_b_analysis.INHERIT_TOL_M``).
INHERIT_TOL_M = 10.0
#: § 6b fits the ten-pass families on K' = 1..5.
FIT_KMAX = 5
#: Tolerance of gate 2 (``gemini37_image_gap_test``'s mechanism bound).
F1_TOL = 1e-3
#: § 3's printed 384-px (487-tile) floors at the (K, t) the Run B cells use
#: (``reports/w27-replicate-floors-2026-10-06.md`` § 3 table); the CSV
#: re-derivation must match them to four places.
S3_PRINTED: dict[tuple[int, int], float] = {
    (10, 10): 0.0253, (10, 9): 0.0191, (5, 5): 0.0295, (5, 4): 0.0211}


@dataclass(frozen=True)
class Arm:
    """One Run B proposer arm: its config version, pass count and verifier legs.

    Attributes:
        name: Arm directory under ``outputs/modality-bridge-2026-10-07``.
        cell: Config version (the pass and union subdirectory).
        n_passes: Passes in the arm's union (K).
        legs: ``(leg, verify directory)`` pairs under ``verifier/<cell>/``.
    """

    name: str
    cell: str
    n_passes: int
    legs: tuple[tuple[str, str], ...]

    @property
    def union_name(self) -> str:
        """The union file the arm's legs verified."""
        return f"union_k{self.n_passes}.geojson"


#: The seven arms. ``g3-text``, ``g3-image`` and ``g3-text-temp1`` read the
#: committed ``verify_g3``: their uncommitted ``_repaired`` copies changed no
#: row (module docstring).
ARMS: dict[str, Arm] = {a.name: a for a in (
    Arm("g3-text", "detect_brief-text", 10, (("g3v", "verify_g3"),)),
    Arm("g3-image", "detect_brief-text-image", 10, (("g3v", "verify_g3"),)),
    Arm("g37-text", "detect_brief-text", 5,
        (("g3v", "verify_g3_repaired"), ("g37v", "verify_g37_repaired"))),
    Arm("g37-image", "detect_brief-text-image", 5,
        (("g3v", "verify_g3_repaired"), ("g37v", "verify_g37_repaired"))),
    Arm("g37-image-cache", "detect_brief-text-image", 5,
        (("g3v", "verify_g3_repaired"), ("g37v", "verify_g37_repaired"))),
    Arm("g3-text-temp1", "detect_brief-text", 5, (("g3v", "verify_g3"),)),
    Arm("g3-image-temp1", "detect_brief-text-image", 5, (("g3v", "verify_g3_repaired"),)),
)}

#: Results cell directory -> (arm, verifier leg).
CELLS: dict[str, tuple[str, str]] = {
    "g3-text-g3v": ("g3-text", "g3v"),
    "g3-image-g3v": ("g3-image", "g3v"),
    "g37-text-g3v": ("g37-text", "g3v"),
    "g37-text-g37v": ("g37-text", "g37v"),
    "g37-image-g3v": ("g37-image", "g3v"),
    "g37-image-g37v": ("g37-image", "g37v"),
    "g37-image-cache-g3v": ("g37-image-cache", "g3v"),
    "g37-image-cache-g37v": ("g37-image-cache", "g37v"),
    "g3-text-temp1-g3v": ("g3-text-temp1", "g3v"),
    "g3-image-temp1-g3v": ("g3-image-temp1", "g3v"),
}

#: Verified-set kinds: (GeoJSON written by image_b_analysis, key path of its
#: point in analysis.json).
SET_KINDS: dict[str, tuple[str, tuple[str, ...]]] = {
    "best": ("verified_best_20m.geojson", ("image_best",)),
    "op": ("verified_op_20m.geojson", ("operating_point",)),
    "ladder5": ("verified_ladder_n5_20m.geojson", ("ladder", "5", "best")),
}

#: Gap label -> (text cell, image cell, set kind, committed file, committed label).
GAPS: dict[str, tuple[str, str, str, str, str]] = {
    "g3": ("g3-text-g3v", "g3-image-g3v", "best", "gap_test.json", "g3"),
    "carried-verifier": ("g37-text-g3v", "g37-image-g3v", "best", "gap_test.json",
                         "carried-verifier"),
    "all-3.7": ("g37-text-g37v", "g37-image-g37v", "best", "gap_test.json", "all-3.7"),
    "g3-k5": ("g3-text-g3v", "g3-image-g3v", "ladder5", "k5/gap_test.json", "g3-k5"),
    "g3-t1-k5": ("g3-text-temp1-g3v", "g3-image-temp1-g3v", "best",
                 "additions/gap_test.json", "g3-t1-k5"),
    "fifth-leg-g3v": ("g37-text-g3v", "g37-image-cache-g3v", "best",
                      "additions/gap_test.json", "fifth-leg-g3v"),
    "fifth-leg-g37v": ("g37-text-g37v", "g37-image-cache-g37v", "best",
                       "additions/gap_test.json", "fifth-leg-g37v"),
}

#: Committed duplicates of the D49 pairs (additions/ re-ran them for comparison).
GAP_ALIASES: dict[tuple[str, str], str] = {
    ("additions/gap_test.json", "g3-best"): "g3",
    ("additions/gap_test.json", "carried-verifier-best"): "carried-verifier",
    ("additions/gap_test.json", "all-3.7-best"): "all-3.7",
}

#: Gap changes: (label, 3.7-side gap, Gemini 3-side gap, tier). Primary: § 9
#: item 4's two; the rest are the secondaries the brief names.
GAP_CHANGES: tuple[tuple[str, str, str, str], ...] = (
    ("carried-verifier minus g3", "carried-verifier", "g3", "primary"),
    ("all-3.7 minus g3", "all-3.7", "g3", "primary"),
    ("carried-verifier minus g3-k5", "carried-verifier", "g3-k5", "secondary: K-matched"),
    ("all-3.7 minus g3-k5", "all-3.7", "g3-k5", "secondary: K-matched"),
    ("carried-verifier minus g3-t1-k5", "carried-verifier", "g3-t1-k5",
     "secondary: Gemini 3 at T 1.0"),
    ("all-3.7 minus g3-t1-k5", "all-3.7", "g3-t1-k5", "secondary: Gemini 3 at T 1.0"),
    ("fifth-leg-g3v minus g3", "fifth-leg-g3v", "g3", "secondary: fifth leg"),
    ("fifth-leg-g37v minus g3", "fifth-leg-g37v", "g3", "secondary: fifth leg"),
    ("fifth-leg-g3v minus g3-t1-k5", "fifth-leg-g3v", "g3-t1-k5",
     "secondary: fifth leg, fully matched"),
    ("fifth-leg-g37v minus g3-t1-k5", "fifth-leg-g37v", "g3-t1-k5",
     "secondary: fifth leg, fully matched"),
)

#: The six D49 cells -> their original's label in ``modality_bridge_anchors``.
DATE_CELLS: dict[str, str] = {
    "g3-text-g3v": "g3-text",
    "g3-image-g3v": "g3-image",
    "g37-text-g3v": "g37-text-g3v",
    "g37-text-g37v": "g37-text-g37v",
    "g37-image-g3v": "g37-image-g3v",
    "g37-image-g37v": "g37-image-g37v",
}

#: Worker state (set in the parent before the pool forks).
_G: dict[str, Any] = {}


# --------------------------------------------------------------------------- #
# Pure functions (tier-1 tested in tests/test_modality_bridge_floors.py).
# --------------------------------------------------------------------------- #


def k_path(frac: float, n_passes: int) -> int:
    """Vote threshold at ``n_passes`` on a relative-threshold path.

    Rounds half up and never falls below 1, as ``floors2_analyse.k_path``.

    Args:
        frac: The cell's vote fraction ``k / K`` (e.g. 0.9 for k9 of 10).
        n_passes: Passes in the rung.

    Returns:
        The vote threshold for a rung of ``n_passes``.

    Examples:
        >>> [k_path(0.9, n) for n in (1, 5, 6, 10)]
        [1, 5, 5, 9]
    """
    return max(1, int(np.floor(frac * n_passes + 0.5)))


def fpc_sd(values: Sequence[float], n: int, k: int) -> float:
    """Run-to-run SD of a K-pass statistic from its values over ALL K-subsets.

    ``sqrt(V_sub · N / (N − K))`` with ``V_sub`` the variance (divisor C(N, K))
    of the subset values: unbiased for a mean over passes, conservative in
    expectation for consensus F1 (``floors2_analyse.sd_run``).

    Args:
        values: The statistic on every K-subset of the N passes.
        n: Passes in the pool (N).
        k: Passes per subset (K, below N).

    Returns:
        The estimated run-to-run SD.

    Raises:
        ValueError: If ``k`` is not below ``n``.

    Examples:
        >>> round(fpc_sd([0.0, 1.0], 2, 1), 6)
        0.707107
    """
    if not 0 < k < n:
        raise ValueError(f"need 0 < k < n, got k={k}, n={n}")
    return float(np.sqrt(np.var(np.asarray(values, dtype=float)) * n / (n - k)))


def jackknife_se(subsets: Sequence[tuple[int, ...]], values: Sequence[float],
                 n: int, k: int) -> float:
    """Leave-one-pass-out jackknife standard error of :func:`fpc_sd`.

    Replicate j uses only the subsets that avoid pass j (N − 1 passes), as
    ``floors2_analyse.jack_sd``.

    Args:
        subsets: The K-subsets (tuples of pass indices) in ``values`` order.
        values: The statistic on each subset.
        n: Passes in the pool.
        k: Passes per subset.

    Returns:
        The jackknife SE, or NaN when ``n − 1 <= k`` (no replicate is defined).
    """
    if n - 1 <= k:
        return float("nan")
    vals = np.asarray(values, dtype=float)
    reps = []
    for j in range(n):
        keep = np.array([j not in s for s in subsets])
        reps.append(fpc_sd(vals[keep], n - 1, k))
    r = np.asarray(reps)
    return float(np.sqrt((n - 1) / n * ((r - r.mean()) ** 2).sum()))


def disjoint_pairs(subsets: Sequence[tuple[int, ...]]) -> list[tuple[int, int]]:
    """Index pairs of subsets that share no pass.

    Args:
        subsets: Tuples of pass indices.

    Returns:
        ``(i, j)`` with ``i < j`` for every disjoint pair.

    Examples:
        >>> disjoint_pairs([(0,), (1,), (0, 1)])
        [(0, 1)]
    """
    return [(i, j) for i, j in itertools.combinations(range(len(subsets)), 2)
            if not set(subsets[i]) & set(subsets[j])]


def fit_extrapolate(ks: Sequence[int], sds: Sequence[float], k_target: int) -> dict[str, float]:
    """Power-law (log-log least squares) and hyperbola (SD = a + b/K) fits, read at a target.

    As ``floors2_analyse.fit_extrapolate``; the power fit is NaN when any SD is
    not positive (its logarithm is undefined).

    Args:
        ks: Rung sizes fitted.
        sds: The SD at each.
        k_target: The rung size to read the fits at.

    Returns:
        ``power``, ``power_exp``, ``hyper``, ``hyper_a`` and ``hyper_b``.
    """
    kk = np.asarray(ks, dtype=float)
    ss = np.asarray(sds, dtype=float)
    if np.all(ss > 0):
        b, a = np.polyfit(np.log(kk), np.log(ss), 1)
        power, power_exp = float(np.exp(a + b * np.log(k_target))), float(b)
    else:
        power, power_exp = float("nan"), float("nan")
    hb, ha = np.polyfit(1 / kk, ss, 1)
    return {"power": power, "power_exp": power_exp, "hyper": float(ha + hb / k_target),
            "hyper_a": float(ha), "hyper_b": float(hb)}


def full_rung_sd(n: int, sd_by_k: Mapping[int, float], se_by_k: Mapping[int, float],
                 fit: Mapping[str, float], fit_se: Mapping[str, float]) -> dict[str, Any]:
    """The run-to-run SD of an N-pass cell at K = N, by § 6b's rules.

    At K = N there is no subset spread, so the SD is carried from smaller
    rungs (``floors-v2/floors2_rescreen.py``):

    * ``N > FIT_KMAX`` (the ten-pass arms): point = max(power fit, hyperbola
      fit, SD at K' = FIT_KMAX); upper = max(point, power + 1.96 · its
      jackknife SE, hyperbola + 1.96 · its jackknife SE);
    * ``N <= FIT_KMAX`` (the five-pass arms): point = max(power fit,
      hyperbola fit, SD at K' = N − 1, SD at K' = N − 2); upper = point +
      1.96 · the jackknife SE at K' = N − 2.

    Args:
        n: Passes (the target K).
        sd_by_k: Direct FPC SD at each K' < N.
        se_by_k: Jackknife SE at each K' (NaN where undefined).
        fit: :func:`fit_extrapolate` read at K = N.
        fit_se: Jackknife SEs of the fits (``power``, ``hyper``; NaN allowed).

    Returns:
        ``sd`` (point), ``sd_upper`` and ``rule`` (a sentence).
    """
    if n > FIT_KMAX:
        point = float(np.nanmax([fit["power"], fit["hyper"], sd_by_k[FIT_KMAX]]))
        upper = float(np.nanmax([point, fit["power"] + Z * fit_se.get("power", np.nan),
                                 fit["hyper"] + Z * fit_se.get("hyper", np.nan)]))
        rule = (f"K = {n} of {n} passes: max(power fit, hyperbola fit on K' = 1..{FIT_KMAX}, "
                f"flat K' = {FIT_KMAX}); upper adds 1.96 jackknife SE of the fits")
    else:
        point = float(np.nanmax([fit["power"], fit["hyper"], sd_by_k[n - 1], sd_by_k[n - 2]]))
        se = se_by_k.get(n - 2, np.nan)
        upper = point + Z * se if np.isfinite(se) else float("nan")
        rule = (f"K = {n} of {n} passes: max(fits on K' = 1..{n - 1}, direct K' = {n - 2}, "
                f"K' = {n - 1}); upper adds 1.96 jackknife SE at K' = {n - 2}")
    return {"sd": point, "sd_upper": upper, "rule": rule}


def direct_max_sd(sd_by_k: Mapping[int, float], n: int) -> float:
    """Sensitivity SD at K = N: the largest direct FPC SD from K' = FIT_KMAX to N − 1.

    § 6b carries the SD to K = N by fits on K' <= 5 because its ten-pass
    families were not subsampled above K' = 5. Where the direct estimates
    exist, they show whether the carry over- or under-shoots (a fit to an
    SD that rises with K extrapolates upward).

    Args:
        sd_by_k: Direct FPC SD at each K' < N.
        n: Passes.

    Returns:
        ``max(sd_by_k[k] for FIT_KMAX <= k < n)``.

    Examples:
        >>> direct_max_sd({5: 0.012, 6: 0.013, 9: 0.011}, 10)
        0.013
    """
    return float(max(v for k, v in sd_by_k.items() if FIT_KMAX <= k < n))


def contrast_floor(sds: Sequence[float], n_contrasts: int,
                   band: float = VERIFIER_BAND) -> float:
    """D46 floor of a signed sum of independent cells.

    ``1.96 · sqrt(ΣSD²) + band · n_contrasts``: one cell pair (a gap, a date
    component) is ``n_contrasts = 1``; a gap change of four cells is 2.

    Args:
        sds: Run-to-run SD of each cell in the contrast.
        n_contrasts: Pairwise contrasts the statistic contains.
        band: Verifier re-invocation band per contrast.

    Returns:
        The floor (95th percentile of |statistic| under the null).

    Examples:
        >>> round(contrast_floor([0.003, 0.004], 1), 6)
        0.0108
    """
    return float(Z * np.sqrt(np.sum(np.square(np.asarray(sds, dtype=float))))
                 + band * n_contrasts)


def s3_floor_as_sd(floor: float) -> float:
    """A § 3 pairwise floor (95th percentile of |ΔF1|) as a per-cell SD.

    Args:
        floor: The committed floor between two replicate cells.

    Returns:
        ``floor / (1.96 · √2)``.
    """
    return float(floor / (Z * np.sqrt(2.0)))


def tile_flips(a: Mapping[str, np.ndarray], b: Mapping[str, np.ndarray]) -> dict[str, Any]:
    """Same-tile changes between two outputs on one tile frame.

    A tile is **discordant** when any of its TP, FP or FN counts differ. It is
    **in error** when FP + FN > 0; it is **fixed** when in error in ``a`` and
    clean in ``b``, **broken** when clean in ``a`` and in error in ``b``.

    Args:
        a: Per-tile ``tp``/``fp``/``fn`` arrays of the reference output.
        b: The same of the other output, aligned tile for tile.

    Returns:
        ``n_tiles``, ``discordant``, ``discordant_rate``, ``fixed``, ``broken``,
        ``error_flip_rate`` and the summed count changes ``d_tp``, ``d_fp``,
        ``d_fn`` (b minus a).

    Examples:
        >>> z = np.zeros(2)
        >>> r = tile_flips({"tp": z, "fp": np.array([1., 0.]), "fn": z},
        ...                {"tp": z, "fp": z, "fn": np.array([0., 1.])})
        >>> (r["discordant"], r["fixed"], r["broken"])
        (2, 1, 1)
    """
    n = len(a["tp"])
    differs = np.zeros(n, dtype=bool)
    for key in ("tp", "fp", "fn"):
        differs |= np.asarray(a[key]) != np.asarray(b[key])
    err_a = (np.asarray(a["fp"]) + np.asarray(a["fn"])) > 0
    err_b = (np.asarray(b["fp"]) + np.asarray(b["fn"])) > 0
    fixed = int((err_a & ~err_b).sum())
    broken = int((~err_a & err_b).sum())
    return {
        "n_tiles": int(n), "discordant": int(differs.sum()),
        "discordant_rate": float(differs.sum() / n), "fixed": fixed, "broken": broken,
        "error_flip_rate": float((fixed + broken) / n),
        "d_tp": float(np.sum(b["tp"]) - np.sum(a["tp"])),
        "d_fp": float(np.sum(b["fp"]) - np.sum(a["fp"])),
        "d_fn": float(np.sum(b["fn"]) - np.sum(a["fn"])),
    }


def interaction_arms(text37: Any, text3: Any, image37: Any, image3: Any,
                     swap: str = "modality") -> tuple[Any, Any, Any, Any]:
    """Order four cells for ``paired_interaction(a, b, c, d)``.

    The statistic is ``(a − b) − (c − d)``, and the permutation swaps a with
    c and b with d in a tile. ``modality`` gives a = T37, b = T3, c = I37,
    d = I3: the statistic is ``(T37 − I37) − (T3 − I3)`` and each tile swaps
    text with image in both families together (the card's instrument).
    ``family`` gives a = T37, b = I37, c = T3, d = I3: the same statistic,
    with each tile swapping the families instead.

    Args:
        text37: Counts of the 3.7-side text cell.
        text3: Counts of the Gemini 3-side text cell.
        image37: Counts of the 3.7-side image cell.
        image3: Counts of the Gemini 3-side image cell.
        swap: ``modality`` or ``family``.

    Returns:
        ``(a, b, c, d)``.

    Raises:
        ValueError: On an unknown ``swap``.

    Examples:
        >>> interaction_arms("T37", "T3", "I37", "I3")
        ('T37', 'T3', 'I37', 'I3')
        >>> interaction_arms("T37", "T3", "I37", "I3", swap="family")
        ('T37', 'I37', 'T3', 'I3')
    """
    if swap == "modality":
        return text37, text3, image37, image3
    if swap == "family":
        return text37, image37, text3, image3
    raise ValueError(f"swap must be 'modality' or 'family', got {swap!r}")


def inherit_index(rung_xy: np.ndarray, union_xy: np.ndarray,
                  tol: float = INHERIT_TOL_M) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Nearest union candidate for each rung cluster, as the K = 5 ladder inherits.

    Args:
        rung_xy: Rung cluster centroids, shape (m, 2), project CRS.
        union_xy: Union candidate points, shape (u, 2), project CRS.
        tol: Largest distance at which a probability is inherited (metres).

    Returns:
        ``(distance, index, matched)``: the nearest union candidate's distance
        and index per cluster, and ``distance <= tol``.
    """
    from scipy.spatial import cKDTree

    if len(rung_xy) == 0:
        return np.zeros(0), np.zeros(0, dtype=int), np.zeros(0, dtype=bool)
    d, idx = cKDTree(union_xy).query(rung_xy, k=1)
    return d, idx, d <= tol


# --------------------------------------------------------------------------- #
# Loading and scoring (sapphire).
# --------------------------------------------------------------------------- #


def read_point(analysis: Mapping[str, Any], kind: str) -> tuple[float, int]:
    """The (prob_t, min_votes) point of a set kind in an ``analysis.json``.

    Args:
        analysis: A parsed ``analysis.json``.
        kind: A key of :data:`SET_KINDS`.

    Returns:
        ``(prob_t, min_votes)``.
    """
    node: Any = analysis
    for key in SET_KINDS[kind][1]:
        node = node[key]
    return float(node["prob_t"]), int(node["min_votes"])


def read_f1(analysis: Mapping[str, Any], kind: str) -> float:
    """The committed F1 of a set kind in an ``analysis.json``."""
    node: Any = analysis
    for key in SET_KINDS[kind][1]:
        node = node[key]
    return float(node["f1"])


def load_passes(scoring_dir: Path, cell: str, n: int) -> list[list[dict]]:
    """Load an arm's deduplicated passes in numeric run order.

    ``grid_analysis.load_cell_passes`` with the pass count as a parameter (it
    is fixed at ten there).

    Args:
        scoring_dir: The arm's ``scoring`` directory.
        cell: Config version.
        n: Passes.

    Returns:
        One detection list per pass, as ``load_cell_passes`` returns them.
    """
    passes = []
    for i in range(1, n + 1):
        path = scoring_dir / "common" / cell / f"run_{i}" / "detections_dedup.geojson"
        data = json.loads(path.read_text())
        passes.append([
            {"centroid": tuple(f["geometry"]["coordinates"]),
             "label": f["properties"].get("label", "mound"),
             "source_tiles": (f["properties"].get("origin_tiles") or "").split(";"),
             "cluster_size": int(f["properties"].get("cluster_size", 1))}
            for f in data["features"]])
    return passes


def counts_of(gdf: Any) -> dict[str, np.ndarray]:
    """Per-tile counts of a verified set on the 487-tile frame (the gap tests' path)."""
    from scripts.grid_verifier_analysis import per_tile_counts

    return per_tile_counts(gdf, _G["bounds"], _G["ref"])


def micro(counts: Mapping[str, np.ndarray]) -> float:
    """Micro-F1 of per-tile counts (``n1_baseline_leaderboard_tiering.micro_f1``)."""
    from scripts.n1_baseline_leaderboard_tiering import micro_f1

    return float(micro_f1(counts["tp"].sum(), counts["fp"].sum(), counts["fn"].sum()))


def build_rung(passes: list[list[dict]]) -> Any:
    """Cluster a pass subset exactly as ``image_b_analysis``'s ladder does.

    Args:
        passes: The subset's passes, in ascending run order.

    Returns:
        GeoDataFrame (project CRS) with ``vote_count`` and ``source_tile``;
        no row is dropped here (the ladder drops only unmatched clusters).
    """
    import geopandas as gpd

    from scripts.grid_analysis import CRS
    from scripts.h13_k_sensitivity import cluster_votes
    from scripts.prepare_h13_scoring import assign_primary_tiles

    centroids, votes = cluster_votes(passes, 1)
    gdf = gpd.GeoDataFrame(
        {"vote_count": np.asarray(votes)},
        geometry=gpd.points_from_xy([c[0] for c in centroids], [c[1] for c in centroids]),
        crs=CRS)
    gdf["source_tile"] = assign_primary_tiles(gdf, _G["bounds"])
    return gdf


def subset_job(job: tuple[str, tuple[int, ...]]) -> dict[str, Any]:
    """Build one subset rung of one arm and score it at every point of every leg.

    Args:
        job: ``(arm name, subset of pass indices)``.

    Returns:
        ``rows`` (one per leg and point: n_det, tp, fp, fn, f1), ``counts``
        (per-tile arrays, kept only for the flip yardstick's K' and the all-pass
        rung), and ``top`` (the all-pass rung's union-reproduction record).
    """
    from scripts.grid_verifier_analysis import verified_subset

    name, subset = job
    arm = ARMS[name]
    st = _G["arms"][name]
    rung = build_rung([st["passes"][i] for i in subset])
    xy = np.c_[rung.geometry.x.to_numpy(), rung.geometry.y.to_numpy()]
    dist, idx, matched = inherit_index(xy, st["union_xy"])
    n_k = len(subset)
    keep_counts = n_k in (arm.n_passes // 2, arm.n_passes) or subset == tuple(range(5))
    out: dict[str, Any] = {"arm": name, "subset": subset, "rows": [], "counts": {}}
    if n_k == arm.n_passes:
        # The union is this rung less its off-carrier clusters (union_with_votes),
        # so every on-carrier cluster must sit on its own union candidate.
        on = rung["source_tile"].notna().to_numpy()
        out["top"] = {
            "n_rung": int(len(rung)), "n_on_carrier": int(on.sum()),
            "n_matched": int(matched.sum()),
            "max_distance_on_carrier_m": float(dist[on].max()) if on.any() else 0.0,
            "union_indices_unique": bool(len(set(idx[on].tolist())) == int(on.sum())),
            "votes_equal_on_carrier": bool(np.array_equal(
                rung["vote_count"].to_numpy()[on], st["union_votes"][idx[on]])),
        }
    for leg, probs in st["probs"].items():
        cell = rung.copy()
        cell["mound_probability"] = probs[idx] if len(idx) else np.zeros(0)
        cell = cell[matched].copy()
        for prob_t, frac in st["points"][leg]:
            k = k_path(frac, n_k)
            sub = verified_subset(cell, prob_t, k)
            c = counts_of(sub)
            out["rows"].append({
                "arm": name, "leg": leg, "prob_t": prob_t, "frac": frac, "K": n_k, "k": k,
                "subset": "-".join(map(str, subset)), "n_det": int(len(sub)),
                "tp": int(c["tp"].sum()), "fp": int(c["fp"].sum()), "fn": int(c["fn"].sum()),
                "f1": micro(c)})
            if keep_counts:
                out["counts"][(leg, prob_t, frac)] = {key: v.copy() for key, v in c.items()}
    return out


def sha256(path: Path) -> str:
    """Hex SHA-256 of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------- #
# Analysis steps.
# --------------------------------------------------------------------------- #


def load_committed_sets() -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    """Read every committed Run B verified set and gate it against analysis.json.

    Returns:
        ``(analyses, sets, failures)``: per cell its parsed ``analysis.json``;
        per (cell, kind) the set's counts, F1 and point; gate 2's failures.
    """
    import geopandas as gpd

    from scripts.grid_analysis import CRS

    analyses: dict[str, Any] = {}
    sets: dict[tuple[str, str], Any] = {}
    failures: list[str] = []
    for cell in CELLS:
        analysis = json.loads((RESULTS / cell / "analysis.json").read_text())
        analyses[cell] = analysis
        for kind, (fname, _keys) in SET_KINDS.items():
            path = RESULTS / cell / fname
            if not path.exists():
                continue
            gdf = gpd.read_file(path).to_crs(CRS)
            counts = counts_of(gdf)
            f1 = micro(counts)
            committed = read_f1(analysis, kind)
            ok = abs(f1 - committed) <= F1_TOL
            if not ok:
                failures.append(f"{cell}/{kind}: per-tile {f1:.6f} vs committed {committed:.6f}")
            sets[(cell, kind)] = {"counts": counts, "f1": f1, "committed_f1": committed,
                                  "point": read_point(analysis, kind), "n": int(len(gdf)),
                                  "ok": ok}
    return analyses, sets, failures


def reproduce_gaps(sets: Mapping[tuple[str, str], Any]) -> tuple[dict[str, Any], list[str]]:
    """Gate 3: re-run every committed gap test and require exact agreement.

    Returns:
        ``(record, failures)``; the record holds each pair's reproduced result.
    """
    from scripts.image_b_analysis import N_PERMS, SEED
    from scripts.n1_baseline_leaderboard_tiering import permutation_test_float

    record: dict[str, Any] = {}
    failures: list[str] = []
    checks = [(f, lab, gap) for gap, (_t, _i, _k, f, lab) in GAPS.items()]
    checks += [(f, lab, gap) for (f, lab), gap in GAP_ALIASES.items()]
    for fname, lab, gap in checks:
        text, image, kind, _f, _l = GAPS[gap]
        t, i = sets[(text, kind)]["counts"], sets[(image, kind)]["counts"]
        res = permutation_test_float(t["tp"], t["fp"], t["fn"], i["tp"], i["fp"], i["fn"],
                                     n_permutations=N_PERMS, seed=SEED)
        committed = json.loads((RESULTS / fname).read_text())["pairs"][lab]
        ok = (abs(res["f1_a"] - committed["f1_a"]) < 1e-9
              and abs(res["f1_b"] - committed["f1_b"]) < 1e-9
              and abs(res["observed_diff"] - committed["observed_diff"]) < 1e-9
              and res["p_value"] == committed["p_value"])
        record[f"{fname}::{lab}"] = {
            "gap": gap, "reproduced_diff": res["observed_diff"], "reproduced_p": res["p_value"],
            "committed_diff": committed["observed_diff"], "committed_p": committed["p_value"],
            "ok": ok}
        if not ok:
            failures.append(f"{fname}::{lab}: {res['observed_diff']:+.6f} p {res['p_value']} vs "
                            f"{committed['observed_diff']:+.6f} p {committed['p_value']}")
        logger.info("gap %-34s %+.6f p=%.4f (committed %+.6f p=%.4f) %s", f"{fname}::{lab}",
                    res["observed_diff"], res["p_value"], committed["observed_diff"],
                    committed["p_value"], "OK" if ok else "FAILED")
    return record, failures


def gap_change_tests(sets: Mapping[tuple[str, str], Any]) -> dict[str, Any]:
    """Item 4: every gap change with the grid's interaction instrument.

    Returns:
        Per gap change: the observed statistic, the bootstrap CI95, the
        modality-swap permutation p (primary), the family-swap p (sensitivity),
        and the four cells; BH-adjusted primary p over all ten.
    """
    from scripts.grid_analysis import paired_interaction
    from scripts.lib_permutation import bh_adjust, paired_interaction_permutation

    out: dict[str, Any] = {}
    for label, g37, g3, tier in GAP_CHANGES:
        t37, i37, k37 = GAPS[g37][0], GAPS[g37][1], GAPS[g37][2]
        t3, i3, k3 = GAPS[g3][0], GAPS[g3][1], GAPS[g3][2]
        c = {"T37": sets[(t37, k37)]["counts"], "I37": sets[(i37, k37)]["counts"],
             "T3": sets[(t3, k3)]["counts"], "I3": sets[(i3, k3)]["counts"]}
        res = paired_interaction(*interaction_arms(c["T37"], c["T3"], c["I37"], c["I3"]))
        fam = paired_interaction_permutation(
            *interaction_arms(c["T37"], c["T3"], c["I37"], c["I3"], swap="family"),
            metric="f1")
        gap37 = micro(c["T37"]) - micro(c["I37"])
        gap3 = micro(c["T3"]) - micro(c["I3"])
        out[label] = {
            "tier": tier, "gap_37": g37, "gap_3": g3,
            "cells": {"T37": [t37, k37], "I37": [i37, k37], "T3": [t3, k3], "I3": [i3, k3]},
            "gap_37_value": gap37, "gap_3_value": gap3,
            "gap_change": res["difference_of_differences"],
            "ci95": [res["ci_lower"], res["ci_upper"]], "excludes_zero": res["excludes_zero"],
            "bootstrap_mean": res["bootstrap_mean"], "n_bootstrap": res["n_iterations"],
            "p_modality_swap": res["p_two_sided"], "p_method": res["p_method"],
            "p_family_swap": fam["p_value"], "n_permutations": res["n_permutations"],
            "seed": res["seed"],
        }
        logger.info("gap change %-32s %+.4f CI95 [%+.4f, %+.4f] p=%.4f (family-swap p=%.4f)",
                    label, res["difference_of_differences"], res["ci_lower"], res["ci_upper"],
                    res["p_two_sided"], fam["p_value"])
    adjusted = bh_adjust([v["p_modality_swap"] for v in out.values()])
    for v, q in zip(out.values(), adjusted):
        v["p_bh_all_ten"] = q
    return out


def original_sets() -> dict[str, Any]:
    """Each original cell's set at its registered point (= its sweep best, gate 1).

    Returns:
        Per original label: counts, micro-F1, point and set size.
    """
    from scripts import image_b_analysis as iba
    from scripts.grid_verifier_analysis import verified_subset
    from scripts.modality_bridge_anchors import ORIGINAL_CELLS
    from scripts.stride_verifier_analysis import reassign_gate

    out = {}
    for c in ORIGINAL_CELLS:
        vroot = PROJECT_ROOT / c.outputs_root / "verifier" / c.cell
        union = reassign_gate(iba.load_image_union(vroot, c.union_name, c.verify_dir),
                              _G["bounds"], c.label)
        sub = verified_subset(union, c.prob_t, c.min_votes)
        counts = counts_of(sub)
        out[c.label] = {"counts": counts, "f1": micro(counts), "registered_f1": c.f1,
                        "point": [c.prob_t, c.min_votes], "n": int(len(sub))}
    return out


def date_components(sets: Mapping[tuple[str, str], Any],
                    originals: Mapping[str, Any]) -> dict[str, Any]:
    """Item 6: bridge minus original per D49 cell at the original point and the oracle.

    The original's operating point is its sweep best (gate 1), so its set
    serves both rows; the bridge contributes its set at the original's point
    (``op``) and at its own best (``best``).

    Returns:
        Per cell and point: both F1s, the difference, the tile-swap p and the
        same-tile flips (original as the reference output).
    """
    from scripts.image_b_analysis import N_PERMS, SEED
    from scripts.n1_baseline_leaderboard_tiering import permutation_test_float

    out: dict[str, Any] = {}
    for cell, orig_label in DATE_CELLS.items():
        orig = originals[orig_label]
        out[cell] = {"original": orig_label, "original_point": orig["point"],
                     "original_f1": orig["f1"], "label": "date plus serving mode"}
        for kind, name in (("op", "at_original_point"), ("best", "at_oracle")):
            b = sets[(cell, kind)]
            o = orig["counts"]
            res = permutation_test_float(b["counts"]["tp"], b["counts"]["fp"],
                                         b["counts"]["fn"], o["tp"], o["fp"], o["fn"],
                                         n_permutations=N_PERMS, seed=SEED)
            out[cell][name] = {
                "bridge_point": list(b["point"]), "bridge_f1": b["f1"],
                "difference": b["f1"] - orig["f1"], "p_tile_swap": res["p_value"],
                "flips": tile_flips(o, b["counts"]),
            }
            logger.info("date %-16s %-18s bridge %.4f - original %.4f = %+.4f p=%.4f "
                        "discordant %d", cell, name, b["f1"], orig["f1"], b["f1"] - orig["f1"],
                        res["p_value"], out[cell][name]["flips"]["discordant"])
    return out


def section3_floors() -> dict[tuple[int, int], float]:
    """§ 3's committed 487-tile floors: 95th percentile of within-execution |ΔF1|.

    Read from W2.7's ``gs_consensus_pairs.csv`` (``px384``, 20 m, within), with
    the report's linear-interpolation percentile.

    Returns:
        ``(K, t) -> floor``.
    """
    agg: dict[tuple[int, int], list[float]] = {}
    with W27_PAIRS.open() as fh:
        for r in csv.DictReader(fh):
            if r["kind"] == "within" and r["scope"] == "px384" and r["buffer"] == "20":
                agg.setdefault((int(r["K"]), int(r["t"])), []).append(float(r["abs_dF1"]))
    return {key: float(np.percentile(v, 95)) for key, v in agg.items()}


def run_subsets(workers: int) -> tuple[list[dict], dict, dict]:
    """Item 7's heavy step: every subset rung of every arm, in parallel.

    Returns:
        ``(rows, counts, tops)``: every scored row; per (arm, subset, leg,
        prob_t, frac) the per-tile counts kept; per arm the all-pass record.
    """
    jobs = [(name, s) for name, arm in ARMS.items()
            for kk in range(1, arm.n_passes + 1)
            for s in itertools.combinations(range(arm.n_passes), kk)]
    jobs.sort(key=lambda j: -len(j[1]))
    logger.info("%d subset rungs over %d arms on %d workers", len(jobs), len(ARMS), workers)
    with Pool(workers) as pool:
        results = pool.map(subset_job, jobs, chunksize=4)
    rows, counts, tops = [], {}, {}
    for r in results:
        rows.extend(r["rows"])
        for key, c in r["counts"].items():
            counts[(r["arm"], r["subset"], *key)] = c
        if "top" in r:
            tops[r["arm"]] = r["top"]
    return rows, counts, tops


def cell_sds(rows: list[dict]) -> dict[tuple[str, str, float, float], dict[str, Any]]:
    """Per (arm, leg, prob_t, frac) path: SD at every K', fits, and the K = N value.

    Returns:
        Keyed by the path: ``sd_by_k``, ``se_by_k``, ``sd_dp_by_k`` (disjoint
        pairs), ``fit``, ``fit_se``, ``full`` (:func:`full_rung_sd`) and
        ``direct5`` (K' = 5, for the ten-pass arms' K = 5 rung).
    """
    paths: dict[tuple, dict[int, list[tuple[tuple[int, ...], float]]]] = {}
    for r in rows:
        key = (r["arm"], r["leg"], r["prob_t"], r["frac"])
        sub = tuple(int(x) for x in r["subset"].split("-"))
        paths.setdefault(key, {}).setdefault(r["K"], []).append((sub, r["f1"]))
    out = {}
    for key, by_k in paths.items():
        n = ARMS[key[0]].n_passes
        sd_by_k, se_by_k, dp_by_k = {}, {}, {}
        for kk, items in sorted(by_k.items()):
            if kk >= n:
                continue
            subs = [s for s, _ in items]
            vals = np.asarray([v for _, v in items])
            sd_by_k[kk] = fpc_sd(vals, n, kk)
            se_by_k[kk] = jackknife_se(subs, vals, n, kk)
            pairs = disjoint_pairs(subs)
            dp_by_k[kk] = (float(np.sqrt(np.mean([(vals[i] - vals[j]) ** 2
                                                  for i, j in pairs]) / 2))
                           if pairs else float("nan"))
        kfit = [kk for kk in range(1, min(FIT_KMAX, n - 1) + 1)]
        fit = fit_extrapolate(kfit, [sd_by_k[kk] for kk in kfit], n)
        # Jackknife of the fits: refit on the subsets avoiding pass j (N − 1 passes).
        reps = []
        if all(n - 1 > kk for kk in kfit):
            for j in range(n):
                sds_j = []
                for kk in kfit:
                    vals = [v for s, v in by_k[kk] if j not in s]
                    sds_j.append(fpc_sd(vals, n - 1, kk))
                fj = fit_extrapolate(kfit, sds_j, n)
                reps.append((fj["power"], fj["hyper"]))
        fit_se: dict[str, float] = {}
        if reps:
            r_arr = np.asarray(reps)
            for col, name in ((0, "power"), (1, "hyper")):
                fit_se[name] = float(np.sqrt((n - 1) / n * ((r_arr[:, col]
                                                             - r_arr[:, col].mean()) ** 2).sum()))
        out[key] = {"n": n, "sd_by_k": sd_by_k, "se_by_k": se_by_k, "sd_dp_by_k": dp_by_k,
                    "fit": fit, "fit_se": fit_se,
                    "full": full_rung_sd(n, sd_by_k, se_by_k, fit, fit_se)}
        if n > FIT_KMAX:
            out[key]["direct5"] = {"sd": sd_by_k[FIT_KMAX],
                                   "sd_upper": sd_by_k[FIT_KMAX] + Z * se_by_k[FIT_KMAX]}
            # Sensitivity: the ten-pass arms also have DIRECT estimates at
            # K' = 6..9, which § 6b's 55-map families did not compute; the
            # largest direct value from K' = 5 up stands in for the carry.
            out[key]["direct_max"] = direct_max_sd(sd_by_k, n)
    return out


def cell_path(cell: str, kind: str, sets: Mapping[tuple[str, str], Any]
              ) -> tuple[tuple[str, str, float, float], int]:
    """The subset path of a committed set and the rung size its SD is read at.

    Returns:
        ``((arm, leg, prob_t, frac), K)``; K is 5 for ``ladder5`` sets.
    """
    arm, leg = CELLS[cell]
    prob_t, k = sets[(cell, kind)]["point"]
    big_k = 5 if kind == "ladder5" else ARMS[arm].n_passes
    return (arm, leg, prob_t, k / big_k), big_k


def sd_of(cell: str, kind: str, sets: Mapping[tuple[str, str], Any],
          sds: Mapping[tuple, Any]) -> dict[str, Any]:
    """Run-to-run SD (point, upper) of a committed set, with its provenance."""
    path, big_k = cell_path(cell, kind, sets)
    rec = sds[path]
    if big_k == rec["n"]:
        sd = rec["full"]
        return {"sd": sd["sd"], "sd_upper": sd["sd_upper"], "rule": sd["rule"],
                "sd_direct": rec.get("direct_max", sd["sd"]), "path": list(path), "K": big_k}
    return {"sd": rec["direct5"]["sd"], "sd_upper": rec["direct5"]["sd_upper"],
            "rule": f"direct, all C({rec['n']}, 5) subsets; upper adds 1.96 jackknife SE",
            "sd_direct": rec["direct5"]["sd"], "path": list(path), "K": big_k}


def flip_yardstick(counts: Mapping[tuple, Any], arm: str, leg: str, prob_t: float,
                   frac: float) -> dict[str, Any]:
    """Within-execution same-tile flips between disjoint subset rungs at K' = N // 2.

    Returns:
        ``K``, ``pairs``, median and 95th percentile of the discordant-tile and
        error-flip rates.
    """
    n = ARMS[arm].n_passes
    kk = n // 2
    subs = [s for (a, s, lg, p, f) in counts
            if a == arm and lg == leg and p == prob_t and f == frac and len(s) == kk]
    subs = sorted(set(subs))
    disc, err = [], []
    for i, j in disjoint_pairs(subs):
        fl = tile_flips(counts[(arm, subs[i], leg, prob_t, frac)],
                        counts[(arm, subs[j], leg, prob_t, frac)])
        disc.append(fl["discordant_rate"])
        err.append(fl["error_flip_rate"])
    return {"K": kk, "pairs": len(disc),
            "discordant_rate_median": float(np.median(disc)) if disc else float("nan"),
            "discordant_rate_p95": float(np.percentile(disc, 95)) if disc else float("nan"),
            "error_flip_rate_median": float(np.median(err)) if err else float("nan"),
            "error_flip_rate_p95": float(np.percentile(err, 95)) if err else float("nan")}


def subset_gates(sets: Mapping[tuple[str, str], Any], counts: Mapping[tuple, Any],
                 tops: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Gate 4: the all-pass rungs reproduce the unions and every committed set.

    Returns:
        ``(record, failures)``.
    """
    record: dict[str, Any] = {"unions": dict(tops), "sets": {}}
    failures: list[str] = []
    for name, top in tops.items():
        if not (top["n_on_carrier"] == len(_G["arms"][name]["union_votes"])
                and top["max_distance_on_carrier_m"] < 0.01
                and top["union_indices_unique"] and top["votes_equal_on_carrier"]):
            failures.append(f"{name}: all-pass rung does not reproduce the union {top}")
    for (cell, kind), s in sets.items():
        path, big_k = cell_path(cell, kind, sets)
        arm, leg, prob_t, frac = path
        subset = tuple(range(big_k))
        c = counts.get((arm, subset, leg, prob_t, frac))
        ok = c is not None and all(np.array_equal(c[k], s["counts"][k])
                                   for k in ("tp", "fp", "fn"))
        record["sets"][f"{cell}/{kind}"] = {"subset": list(subset), "equal": ok,
                                           "f1": micro(c) if c is not None else None,
                                           "committed": s["f1"]}
        if not ok:
            failures.append(f"{cell}/{kind}: subset rung {subset} does not reproduce the set")
    return record, failures


def floors_report(sets: Mapping[tuple[str, str], Any], sds: Mapping[tuple, Any],
                  gap_changes: Mapping[str, Any], dates: Mapping[str, Any],
                  s3: Mapping[tuple[int, int], float], counts: Mapping[tuple, Any]
                  ) -> dict[str, Any]:
    """Item 7: every gap, gap change and date component against its floor.

    Returns:
        ``cells`` (SD per committed set), ``gaps``, ``gap_changes`` and
        ``date_components``, each with the estimate, its floor (point and
        upper), the ratio |estimate| / floor, and the § 3 reference.
    """
    def s3_of(cell: str, kind: str) -> float:
        """The § 3 floor at the set's (K, t)."""
        _path, big_k = cell_path(cell, kind, sets)
        return s3[(big_k, sets[(cell, kind)]["point"][1])]

    cells = {f"{c}/{k}": {**sd_of(c, k, sets, sds), "f1": sets[(c, k)]["f1"],
                          "point": list(sets[(c, k)]["point"]), "s3_floor": s3_of(c, k)}
             for (c, k) in sets}
    gaps = {}
    for gap, (text, image, kind, _f, _l) in GAPS.items():
        st, si = sd_of(text, kind, sets, sds), sd_of(image, kind, sets, sds)
        est = sets[(text, kind)]["f1"] - sets[(image, kind)]["f1"]
        fl = contrast_floor([st["sd"], si["sd"]], 1)
        fu = contrast_floor([st["sd_upper"], si["sd_upper"]], 1)
        fd = contrast_floor([st["sd_direct"], si["sd_direct"]], 1)
        s3f = Z * np.sqrt(s3_floor_as_sd(s3_of(text, kind)) ** 2
                          + s3_floor_as_sd(s3_of(image, kind)) ** 2)
        gaps[gap] = {"estimate": est, "floor": fl, "floor_upper": fu,
                     "ratio": abs(est) / fl, "ratio_upper": abs(est) / fu,
                     "floor_direct": fd, "ratio_direct": abs(est) / fd,
                     "s3_floor": float(s3f), "s3_ratio": abs(est) / float(s3f),
                     "sds": [st["sd"], si["sd"]]}
    gcs = {}
    for label, g37, g3, tier in GAP_CHANGES:
        rec = gap_changes[label]
        sd_list, up_list, dir_list, s3_list = [], [], [], []
        for role in ("T37", "I37", "T3", "I3"):
            cell, kind = rec["cells"][role]
            s = sd_of(cell, kind, sets, sds)
            sd_list.append(s["sd"])
            up_list.append(s["sd_upper"])
            dir_list.append(s["sd_direct"])
            s3_list.append(s3_floor_as_sd(s3_of(cell, kind)))
        fl = contrast_floor(sd_list, 2)
        fu = contrast_floor(up_list, 2)
        fd = contrast_floor(dir_list, 2)
        s3f = float(Z * np.sqrt(np.sum(np.square(s3_list))))
        est = rec["gap_change"]
        gcs[label] = {"tier": tier, "estimate": est, "p_modality_swap": rec["p_modality_swap"],
                      "floor": fl, "floor_upper": fu, "ratio": abs(est) / fl,
                      "ratio_upper": abs(est) / fu, "floor_direct": fd,
                      "ratio_direct": abs(est) / fd, "s3_floor": s3f,
                      "s3_ratio": abs(est) / s3f, "sds": sd_list}
    dcs = {}
    for cell, rec in dates.items():
        dcs[cell] = {}
        for kind, name in (("op", "at_original_point"), ("best", "at_oracle")):
            s = sd_of(cell, kind, sets, sds)
            est = rec[name]["difference"]
            # The original's run-to-run SD is taken equal to the bridge's (same
            # configuration); the § 3 floor is a pairwise floor already.
            fl = contrast_floor([s["sd"], s["sd"]], 1)
            fu = contrast_floor([s["sd_upper"], s["sd_upper"]], 1)
            fd = contrast_floor([s["sd_direct"], s["sd_direct"]], 1)
            arm, leg, prob_t, frac = cell_path(cell, kind, sets)[0]
            dcs[cell][name] = {
                "estimate": est, "p_tile_swap": rec[name]["p_tile_swap"], "floor": fl,
                "floor_upper": fu, "ratio": abs(est) / fl, "ratio_upper": abs(est) / fu,
                "floor_direct": fd, "ratio_direct": abs(est) / fd,
                "s3_floor": s3_of(cell, kind), "s3_ratio": abs(est) / s3_of(cell, kind),
                "flips": rec[name]["flips"],
                "within_execution_flips": flip_yardstick(counts, arm, leg, prob_t, frac)}
    return {"cells": cells, "gaps": gaps, "gap_changes": gcs, "date_components": dcs}


def write_summary(path: Path, report: Mapping[str, Any], gap_changes: Mapping[str, Any],
                  committed_p: Mapping[str, float]) -> None:
    """The short CSV: one row per gap, gap change and date component."""
    fields = ["kind", "label", "estimate", "p", "floor", "floor_upper", "ratio",
              "ratio_upper", "floor_direct", "ratio_direct", "s3_floor", "s3_ratio"]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for gap, g in report["gaps"].items():
            w.writerow({"kind": "gap", "label": gap, "estimate": round(g["estimate"], 6),
                        "p": committed_p[gap], **{k: round(g[k], 6) for k in fields[4:]}})
        for label, g in report["gap_changes"].items():
            w.writerow({"kind": f"gap change ({g['tier']})", "label": label,
                        "estimate": round(g["estimate"], 6), "p": g["p_modality_swap"],
                        **{k: round(g[k], 6) for k in fields[4:]}})
        for cell, rec in report["date_components"].items():
            for name, g in rec.items():
                w.writerow({"kind": "date plus serving mode", "label": f"{cell} {name}",
                            "estimate": round(g["estimate"], 6), "p": g["p_tile_swap"],
                            **{k: round(g[k], 6) for k in fields[4:]}})


def main(argv: list[str] | None = None) -> int:
    """Run the gates, then items 4, 6 and 7, and write the results.

    Args:
        argv: Command-line arguments (default ``sys.argv[1:]``).

    Returns:
        0 on success, 1 when a gate failed (nothing written).
    """
    import geopandas as gpd

    from scripts.grid_analysis import CRS
    from scripts.modality_bridge_anchors import AnchorGateError, run_six_cell_gate
    from scripts.stride_verifier_analysis import COMMON_BOUNDS, GROUND_TRUTH

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scoring-root", type=Path, default=OUTPUTS,
                    help="Root holding <arm>/scoring/common/<cell>/run_<N>/ (default: the "
                         "Stage 2 location, uncommitted).")
    ap.add_argument("--out-dir", type=Path, default=RESULTS / "floors")
    ap.add_argument("--workers", type=int, default=20)
    args = ap.parse_args(argv)
    t0 = time.time()

    _G["bounds"] = gpd.read_file(COMMON_BOUNDS)
    _G["ref"] = gpd.read_file(GROUND_TRUTH).to_crs(CRS)
    gates: dict[str, Any] = {}
    failures: list[str] = []

    # Gate 1: the six original cells and three original gaps.
    try:
        gates["six_cell"] = run_six_cell_gate()
    except AnchorGateError as exc:
        logger.error("%s", exc)
        return 1
    logger.info("gate 1 passed (%.0f s)", time.time() - t0)

    # Gate 2: every committed bridge set re-scores to its analysis.json F1.
    analyses, sets, fail2 = load_committed_sets()
    gates["committed_sets"] = {f"{c}/{k}": {kk: v[kk] for kk in
                                            ("f1", "committed_f1", "point", "n", "ok")}
                               for (c, k), v in sets.items()}
    failures += fail2

    # Gate 3: every committed gap test reproduces exactly.
    gates["committed_gaps"], fail3 = reproduce_gaps(sets)
    failures += fail3
    if failures:
        logger.error("gates 2-3 FAILED: %s", failures)
        return 1
    logger.info("gates 2-3 passed (%.0f s)", time.time() - t0)

    # Item 4 and item 6 (the gates above cover their inputs).
    gap_changes = gap_change_tests(sets)
    originals = original_sets()
    dates = date_components(sets, originals)

    # Item 7: subset rungs (worker state first, so the pool's fork inherits it).
    from scripts import image_b_analysis as iba
    from scripts.stride_verifier_analysis import reassign_gate

    _G["arms"] = {}
    provenance: dict[str, Any] = {}
    for name, arm in ARMS.items():
        vroot = OUTPUTS / name / "verifier" / arm.cell
        probs, union_ref = {}, None
        for leg, vdir in arm.legs:
            u = reassign_gate(iba.load_image_union(vroot, arm.union_name, vdir),
                              _G["bounds"], f"{name}/{leg}")
            probs[leg] = u["mound_probability"].to_numpy()
            union_ref = u
        points: dict[str, list[tuple[float, float]]] = {}
        for cell, (a, leg) in CELLS.items():
            if a != name:
                continue
            for kind in SET_KINDS:
                if (cell, kind) in sets:
                    p, k = sets[(cell, kind)]["point"]
                    big_k = 5 if kind == "ladder5" else arm.n_passes
                    pt = (p, k / big_k)
                    if pt not in points.setdefault(leg, []):
                        points[leg].append(pt)
        sdir = args.scoring_root / name / "scoring"
        _G["arms"][name] = {
            "passes": load_passes(sdir, arm.cell, arm.n_passes),
            "union_xy": np.c_[union_ref.geometry.x.to_numpy(), union_ref.geometry.y.to_numpy()],
            "union_votes": union_ref["vote_count"].to_numpy(),
            "probs": probs, "points": points}
        provenance[name] = {
            f"run_{i}": sha256(sdir / "common" / arm.cell / f"run_{i}" / "detections_dedup.geojson")
            for i in range(1, arm.n_passes + 1)}
    gates["scoring_passes_sha256"] = provenance
    rows, counts, tops = run_subsets(args.workers)
    logger.info("subset rungs done: %d rows (%.0f s)", len(rows), time.time() - t0)

    # Gate 4: the subset machinery reproduces the unions and committed sets.
    gates["subset_machinery"], fail4 = subset_gates(sets, counts, tops)
    if fail4:
        logger.error("gate 4 FAILED: %s", fail4)
        return 1
    logger.info("gate 4 passed")

    sds = cell_sds(rows)
    s3 = section3_floors()
    gates["section3_printed"] = {f"K{k}_t{t}": {"printed": v, "derived": s3[(k, t)],
                                                "ok": round(s3[(k, t)], 4) == v}
                                 for (k, t), v in S3_PRINTED.items()}
    if not all(g["ok"] for g in gates["section3_printed"].values()):
        logger.error("§ 3 floors do not re-derive: %s", gates["section3_printed"])
        return 1
    report = floors_report(sets, sds, gap_changes, dates, s3, counts)
    committed_p = {gap: gates["committed_gaps"][f"{f}::{lab}"]["reproduced_p"]
                   for gap, (_t, _i, _k, f, lab) in GAPS.items()}

    # Everything gated: write.
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    meta = {"script": "scripts/modality_bridge_floors.py",
            "scoring_root": str(args.scoring_root), "z": Z, "verifier_band": VERIFIER_BAND,
            "inherit_tol_m": INHERIT_TOL_M, "wall_seconds": round(time.time() - t0, 1)}
    (out / "gates.json").write_text(json.dumps({"meta": meta, **gates}, indent=1,
                                               default=float) + "\n")
    (out / "gap_change.json").write_text(json.dumps(gap_changes, indent=1, default=float) + "\n")
    (out / "date_component.json").write_text(json.dumps(
        {"label": "date plus serving mode (batch against the originals' real-time tiers), "
                  "never date alone", "cells": dates}, indent=1, default=float) + "\n")
    sd_out = {f"{a}|{lg}|{p}|{fr}": {**v, "sd_by_k": {str(k): x for k, x in v["sd_by_k"].items()},
                                     "se_by_k": {str(k): x for k, x in v["se_by_k"].items()},
                                     "sd_dp_by_k": {str(k): x
                                                    for k, x in v["sd_dp_by_k"].items()}}
              for (a, lg, p, fr), v in sds.items()}
    (out / "floors.json").write_text(json.dumps(
        {"meta": meta, "section3_floors": {f"K{k}_t{t}": v for (k, t), v in sorted(s3.items())},
         "paths": sd_out, **report}, indent=1, default=float) + "\n")
    with (out / "subset_cells.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["arm"], r["leg"], r["prob_t"], r["frac"],
                                                 r["K"], r["subset"])))
    write_summary(out / "summary.csv", report, gap_changes, committed_p)
    logger.info("FLOORS COMPLETE -> %s (%.0f s)", out, time.time() - t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
