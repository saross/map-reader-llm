#!/usr/bin/env python3
"""A-06's registered rule on the D64 same-day genuine-Pro 2 x 2 (report only).

PI ruling D64 (``planning/pi-decisions-2026-09-20.md``) ran Gemini 3.1 Pro
on all eight corners of A-06's thinking x temperature 2 x 2 on one date,
in one mode, with thinking booked per pass
(``outputs/pro-2x2-replication-2026-10-13/``). This driver applies A-06's
registered rule to those passes exactly as the committed A-06
(``scripts/h6_registered_analyses.py`` stage 4) applies it, plus the
replicate-floor check of rulings D45/D46 and the top-up sensitivity, as
pre-specified in ``reports/s164-agent-records/d64-a06-replication.md``
(plan commit ``7ae996ce6``). It writes only under ``--out``; no committed
result, output, or register row is touched, and no model API is called.

Plan sections implemented (P-numbers refer to the record):

- P1 gates: parameter control and coverage from each pass's meta and
  tiles.json; the method replay on the committed A-06 corners; the
  aggregation identity against ``pass_averaged_per_tile``.
- P2 per-corner estimates; P3 factor-T contrasts with BH; P4 thinking
  contrasts with their own BH family (and an all-eight sensitivity);
  P5 corner gap and decomposition; P6 replicate floors; P7 the
  15-tile top-up sensitivity; P8 side by side; P9 thought tokens.

Extended 2026-10-15 (plan P12) without changing any output: the image
pools gained runs 4-6 (wave 3) after this analysis ran, so P1-P11 now
select image runs 1-3 explicitly (``P1_RUNS``) while every pass in a pool
is still scored for the aggregation-identity gate; the floor subset sizes
and the passes per arm are read from the stacks rather than from
``N_PASSES``. Run on the merged tree, the driver reproduces its
2026-10-14 outputs (the record's § Integrity). The P12 analysis is
``d64_p12_replication.py``, which imports this module.

Usage (repository root, on sapphire; a few minutes, one process)::

    PYTHONHASHSEED=0 .venv/bin/python \\
        reports/s164-agent-records/d64-a06-replication-scripts/d64_a06_replication.py \\
        --out <dir>

Author: Shawn Ross & Claude (Anthropic), Session 164, 2026-10-14
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from e45_bootstrap_pairings import micro_f1, paired_bootstrap  # noqa: E402
from h6_registered_analyses import (  # noqa: E402
    B_DELTA_CI,
    BH_Q,
    BOUNDS,
    BUFFER_M,
    CONDITIONS_MANIFEST,
    GROUND_TRUTH,
    PRO_RUN,
    SEED,
    apply_bh_to_factor_t,
    committed_f1,
)
from lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from lib_permutation import bh_adjust, paired_permutation_test  # noqa: E402
from n1_baseline_leaderboard_tiering import (  # noqa: E402
    PASS_GLOBS,
    TARGET_CRS,
    load_baseline_cells,
    pass_averaged_per_tile,
)
from pairwise_permutation_test import assign_source_tiles  # noqa: E402

D64_DIR = Path("outputs/pro-2x2-replication-2026-10-13")
COMMITTED_A06 = REPO / "results/h6-registered-analyses/a06_decision_rule.json"
TOPUP = REPO / D64_DIR / "topup-2026-10-13.json"
MODEL = "gemini-3.1-pro-preview"
CONFIG = {"text": "detect_brief-text", "image": "library_plus-hp"}
N_PASSES = {"text": 5, "image": 3}
#: The passes P1-P11 analyse per modality (None = every pass in the pool).
#: Image runs 4-6 (wave 3, 2026-10-14) belong to P12, not to this analysis.
P1_RUNS: dict[str, tuple[str, ...] | None] = {
    "text": None, "image": ("run_1", "run_2", "run_3")}
THINKS = ("high", "medium")
TEMPS = ("0.0", "0.7")
RULE = 0.03  # A-06's registered threshold (preregistration.md:677)
ALPHA = 0.05

#: The committed A-06 corners, copied from h6_registered_analyses.main()
#: (stage 4, ``corner_specs``); keyed (thinking, temperature).
COMMITTED_SPECS = {
    ("high", "0.0"): (PRO_RUN, "baseline-pro-{m}-high-t-0-0"),
    ("medium", "0.7"): (PRO_RUN, "baseline-pro-{m}-medium-t-0-7"),
    ("high", "0.7"): ("pv-diag-384", "baseline-pro-{m}-high-t-0-7"),
    ("medium", "0.0"): ("pv-diag-384", "baseline-pro-{m}-medium-t-0-0"),
}


def pct(values: list[float], q: float) -> float:
    """W2.7's percentile (linear interpolation; ``w27_summarise.pct``).

    Args:
        values: Non-empty list of numbers.
        q: Quantile in [0, 1].

    Returns:
        The interpolated quantile.

    Example:
        >>> pct([0.0, 1.0], 0.95)
        0.95
    """
    v = sorted(values)
    i = (len(v) - 1) * q
    lo = int(i)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def prf(tp: float, fp: float, fn: float) -> dict[str, float]:
    """Micro precision, recall, and F1 from summed counts (6 dp)."""
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {"f1": round(micro_f1(tp, fp, fn), 6), "precision": round(p, 6),
            "recall": round(r, 6)}


def git_head() -> str:
    """Return the worktree's HEAD commit (full hash)."""
    return subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_pool(pool_dir: Path, gdf_ref: gpd.GeoDataFrame,
               gdf_bounds: gpd.GeoDataFrame,
               tile_order: list[str]) -> tuple[list[str], np.ndarray]:
    """Score every pass of a pool per tile, mirroring ``pass_averaged_per_tile``.

    The pass files are resolved with the same glob and sort, each pass is
    scored by the canonical scorer at 20 m, and the per-tile counts are
    aligned to ``tile_order`` exactly as the A-06 helper does; the per-pass
    rows are kept instead of summed.

    Args:
        pool_dir: Pool directory relative to the repository (holds run_N/).
        gdf_ref: Ground truth in TARGET_CRS.
        gdf_bounds: Tile bounds in TARGET_CRS.
        tile_order: Fixed tile order (array positions).

    Returns:
        (pass file paths relative to the repository, array of shape
        (n_passes, 3, n_tiles) holding TP, FP, FN).
    """
    root = REPO / pool_dir
    pass_files = sorted({f for g in PASS_GLOBS for f in root.glob(g)})
    if not pass_files:
        sys.exit(f"GATE FAIL: no passes under {pool_dir}")
    index = {name: i for i, name in enumerate(tile_order)}
    stack = np.zeros((len(pass_files), 3, len(tile_order)), dtype=float)
    for k, pass_file in enumerate(pass_files):
        gdf = gpd.read_file(pass_file)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        gdf = assign_source_tiles(gdf.to_crs(TARGET_CRS), gdf_bounds)
        metrics = compute_per_tile_tp_fp_fn(gdf, gdf_ref, gdf_bounds,
                                            buffer_metres=BUFFER_M)
        for _, row in metrics.iterrows():
            i = index.get(row["tile_name"])
            if i is None:
                continue
            stack[k, 0, i] += float(row["tp"])
            stack[k, 1, i] += float(row["fp"])
            stack[k, 2, i] += float(row["fn"])
    return [str(p.relative_to(REPO)) for p in pass_files], stack


def select_runs(files: list[str], stack: np.ndarray,
                runs: tuple[str, ...] | None) -> tuple[list[str], np.ndarray]:
    """Keep the passes whose ``run_N`` directory is in ``runs``, in order.

    Args:
        files: Pass file paths, as ``score_pool`` returns them (sorted).
        stack: The matching (n_passes, 3, n_tiles) array.
        runs: Run directory names to keep, or None to keep every pass.

    Returns:
        (the kept file paths, the matching rows of ``stack``).

    Example:
        >>> f = ["p/run_1/a.geojson", "p/run_4/b.geojson"]
        >>> select_runs(f, np.zeros((2, 3, 1)), ("run_1",))[0]
        ['p/run_1/a.geojson']
    """
    if runs is None:
        return files, stack
    keep = [i for i, f in enumerate(files) if Path(f).parent.name in runs]
    return [files[i] for i in keep], stack[keep]


def pass_mean(stack: np.ndarray) -> np.ndarray:
    """Per-tile mean over passes, summed in pass order then divided.

    Matches ``pass_averaged_per_tile``'s arithmetic (sequential sum, one
    division), so the aggregation-identity gate can demand exact equality.
    """
    total = np.zeros(stack.shape[1:], dtype=float)
    for k in range(stack.shape[0]):
        total += stack[k]
    return total / stack.shape[0]


def corner_estimates(stack: np.ndarray, mask: np.ndarray | None = None) -> dict:
    """P2: the pass-averaged micro estimate and the mean of per-pass F1s.

    Args:
        stack: (n_passes, 3, n_tiles) per-pass counts.
        mask: Optional boolean tile mask (True = keep).

    Returns:
        Dict with the pass-averaged micro P/R/F1, the per-pass F1s, their
        mean, pass count, and pass-mean count totals.
    """
    s = stack if mask is None else stack[:, :, mask]
    m = pass_mean(s)
    per_pass = [round(micro_f1(*(float(x) for x in s[k].sum(axis=1))), 6)
                for k in range(s.shape[0])]
    return {
        "pass_averaged_micro": prf(*(float(x) for x in m.sum(axis=1))),
        "per_pass_f1": per_pass,
        "mean_of_pass_f1": round(float(np.mean(per_pass)), 6),
        "n_passes": int(s.shape[0]),
        "n_tiles": int(s.shape[2]),
        "pass_mean_totals": {k: round(float(v), 4) for k, v in
                             zip(("tp", "fp", "fn"), m.sum(axis=1))},
    }


# ---------------------------------------------------------------------------
# Contrasts
# ---------------------------------------------------------------------------

def contrast(stack_a: np.ndarray, stack_b: np.ndarray,
             mask: np.ndarray | None = None) -> dict:
    """A minus B on pass-averaged per-tile counts, as A-06 computes it.

    Args:
        stack_a: Arm A per-pass counts (n_passes, 3, n_tiles).
        stack_b: Arm B per-pass counts.
        mask: Optional tile mask applied to both arms.

    Returns:
        Dict with both estimators' deltas, the A-06 bootstrap block
        (interval and D42 permutation p), and each arm's estimates.
    """
    if mask is not None:
        stack_a, stack_b = stack_a[:, :, mask], stack_b[:, :, mask]
    a, b = pass_mean(stack_a), pass_mean(stack_b)
    boot = paired_bootstrap(a[0], a[1], a[2], b[0], b[1], b[2],
                            n_iterations=B_DELTA_CI, seed=SEED)
    est_a, est_b = corner_estimates(stack_a), corner_estimates(stack_b)
    return {
        "delta (pass-averaged micro)": boot["observed_delta"],
        "delta (mean of per-pass F1)": round(
            est_a["mean_of_pass_f1"] - est_b["mean_of_pass_f1"], 6),
        "delta_ci95_paired_bootstrap": boot["ci95"],
        "delta_bootstrap": boot,
        "a": est_a["pass_averaged_micro"], "b": est_b["pass_averaged_micro"],
        "a_mean_of_pass_f1": est_a["mean_of_pass_f1"],
        "b_mean_of_pass_f1": est_b["mean_of_pass_f1"],
        "n_tiles": int(a.shape[1]),
    }


def floor_pairs(stack: np.ndarray, k: int,
                mask: np.ndarray | None = None) -> list[dict]:
    """P6: |dF1| between disjoint equal-size pass subsets of one corner.

    Every unordered pair of disjoint k-subsets of the corner's passes;
    each subset's estimate is the micro-F1 of its pass-averaged per-tile
    counts (A-06's estimator at k passes). The tile-swap test between the
    two subsets' arrays is run as W2.7 § 3's diagnostic.

    Args:
        stack: (n_passes, 3, n_tiles) per-pass counts.
        k: Subset size.
        mask: Optional tile mask.

    Returns:
        One dict per pair: the two subsets, both F1s, |dF1|, the tile-swap
        p, and whether it rejects at 0.05.
    """
    s = stack if mask is None else stack[:, :, mask]
    subsets = list(itertools.combinations(range(s.shape[0]), k))
    rows = []
    for sa, sb in itertools.combinations(subsets, 2):
        if set(sa) & set(sb):
            continue
        a, b = pass_mean(s[list(sa)]), pass_mean(s[list(sb)])
        f_a = micro_f1(*(float(x) for x in a.sum(axis=1)))
        f_b = micro_f1(*(float(x) for x in b.sum(axis=1)))
        perm = paired_permutation_test({"tp": a[0], "fp": a[1], "fn": a[2]},
                                       {"tp": b[0], "fp": b[1], "fn": b[2]})
        p = perm["metrics"]["f1"]["p_value"]
        rows.append({"subset_a": [i + 1 for i in sa], "subset_b": [i + 1 for i in sb],
                     "f1_a": round(f_a, 6), "f1_b": round(f_b, 6),
                     "abs_delta": round(abs(f_a - f_b), 6), "p_tile_swap": p,
                     "rejects_0.05": bool(p <= ALPHA)})
    return rows


def summarise_floor(rows: list[dict]) -> dict:
    """95th percentile, median, max, pair count, and rejection rate."""
    d = [r["abs_delta"] for r in rows]
    return {"pairs": len(d), "p95": round(pct(d, 0.95), 6),
            "median": round(float(np.median(d)), 6), "max": round(max(d), 6),
            "tile_swap_reject_rate": round(
                sum(r["rejects_0.05"] for r in rows) / len(rows), 4)}


def floor_verdict(delta: float, floor: float, k: int, n: int) -> dict:
    """P6's three-valued floor verdict for one contrast.

    Args:
        delta: The contrast's pass-averaged delta.
        floor: The measured floor at subset size k.
        k: Subset size the floor was measured at.
        n: Passes per arm in the contrast.

    Returns:
        The floor, the scaled floor (floor x sqrt(k/n)), and the verdict.
    """
    scaled = floor * math.sqrt(k / n)
    if abs(delta) > floor:
        verdict = "clears"
    elif abs(delta) > scaled:
        verdict = "clears only the scaled floor"
    else:
        verdict = "inside"
    return {"floor": round(floor, 6), "floor_k": k, "n_per_arm": n,
            "scaled_floor": round(scaled, 6), "verdict": verdict}


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------

def gate_metas(tile_names: set[str]) -> dict:
    """P1 gates 1-2 and P9: parameter control, coverage, thought tokens.

    Returns:
        Per-pass records keyed by corner, each with its meta's parameters,
        usage, and thought tokens per request.

    Raises:
        SystemExit: On any mismatch.
    """
    out, failures = {}, []
    for modality in ("text", "image"):
        for think in THINKS:
            for temp in TEMPS:
                corner = f"{modality}-{think}-t{temp}"
                pool = REPO / D64_DIR / corner / CONFIG[modality]
                metas = sorted(pool.glob("run_*/*.meta.json"))
                if P1_RUNS[modality] is not None:
                    metas = [m for m in metas if m.parent.name in P1_RUNS[modality]]
                if len(metas) != N_PASSES[modality]:
                    failures.append(f"{corner}: {len(metas)} metas")
                rows = []
                for meta_path in metas:
                    meta = json.loads(meta_path.read_text())
                    c, e, u = (meta["configuration"], meta["execution_stats"],
                               meta["usage_stats"])
                    checks = {
                        "model": (c.get("model"), MODEL),
                        "temperature": (c.get("temperature"), float(temp)),
                        "thinking_level": (c.get("thinking_level"), think),
                        "version": (c.get("version"), CONFIG[modality]),
                        "items_processed": (e.get("items_processed"), 487),
                        "items_failed": (e.get("items_failed"), 0),
                    }
                    for key, (got, want) in checks.items():
                        if got != want:
                            failures.append(f"{meta_path.name} {key}: {got} != {want}")
                    tiles_path = Path(str(meta_path).replace(".meta.json", ".tiles.json"))
                    tiles = json.loads(tiles_path.read_text())
                    if set(tiles["completed"]) != tile_names or tiles["failed"]:
                        failures.append(f"{tiles_path.name}: coverage mismatch")
                    n_resp = u.get("n_responses_with_usage") or 0
                    thought = u.get("total_thoughts_tokens", 0)
                    rows.append({
                        "pass": str(meta_path.relative_to(REPO)),
                        "temperature": c.get("temperature"),
                        "thinking_level": c.get("thinking_level"),
                        "service_tier": meta.get("billing", {}).get("service_tier"),
                        "n_responses_with_usage": n_resp,
                        "total_thoughts_tokens": thought,
                        "thought_tokens_per_request": round(thought / n_resp, 4)
                        if n_resp else None,
                        "total_detections": meta["results_summary"]["total_detections"],
                        "topped_up": bool(meta.get("recovery_history")),
                    })
                tot_t = sum(r["total_thoughts_tokens"] for r in rows)
                tot_n = sum(r["n_responses_with_usage"] for r in rows)
                per_req = [r["thought_tokens_per_request"] for r in rows]
                out[corner] = {"passes": rows,
                               "thought_tokens_per_request_corner": round(tot_t / tot_n, 4),
                               "thought_tokens_per_request_range": [min(per_req),
                                                                    max(per_req)]}
    if failures:
        sys.exit("META/COVERAGE GATE FAIL:\n  " + "\n  ".join(failures))
    return out


def gate_replay(gdf_ref: gpd.GeoDataFrame, gdf_bounds: gpd.GeoDataFrame,
                tile_order: list[str]) -> tuple[dict, dict]:
    """P1 gate 3: replay A-06's stage 4 on the committed corners.

    Returns:
        (gate record, committed corner stacks keyed (modality, think, temp)).

    Raises:
        SystemExit: If any replayed bootstrap block differs from the
            committed artefact.
    """
    committed = json.loads(COMMITTED_A06.read_text())
    dirs = {}
    for raw in load_baseline_cells(REPO / "results" / "run-conditions.json",
                                   REPO / "results" / "run-analyses.json"):
        dirs[raw["ref"]] = raw["detections"]
    stacks, record, failures = {}, {}, []
    keys = ("observed_delta", "bootstrap_delta_mean", "ci95", "p_value",
            "n_permutations", "n_discordant_tiles", "ci_excludes_zero")
    for modality in ("text", "image"):
        for (think, temp), (run, cid_t) in COMMITTED_SPECS.items():
            ref = f"{run}::{cid_t.format(m=modality)}"
            files, stack = score_pool(Path(dirs[ref]), gdf_ref, gdf_bounds, tile_order)
            stacks[(modality, think, temp)] = {"ref": ref, "dir": dirs[ref],
                                               "files": files, "stack": stack}
        for think in THINKS:
            alt = stacks[(modality, think, "0.0")]["stack"]
            base = stacks[(modality, think, "0.7")]["stack"]
            got = contrast(alt, base)["delta_bootstrap"]
            want = committed["registered_factor_T"][modality][think]["delta_bootstrap"]
            diffs = {k: (got[k], want[k]) for k in keys if got[k] != want[k]}
            record[f"{modality} {think.upper()} factor T"] = {
                "match": not diffs, "diffs": diffs,
                "observed_delta": got["observed_delta"], "p_value": got["p_value"]}
            if diffs:
                failures.append(f"{modality}/{think}: {diffs}")
        for temp in TEMPS:
            hi = stacks[(modality, "high", temp)]["stack"]
            md = stacks[(modality, "medium", temp)]["stack"]
            got = contrast(hi, md)["delta_bootstrap"]["ci95"]
            tkey = "t0-0" if temp == "0.0" else "t0-7"
            want = committed["thinking_decomposition_context (not a registered factor)"][
                modality][tkey]["delta_ci95_paired_bootstrap"]
            record[f"{modality} thinking at T {temp} (interval)"] = {
                "match": got == want, "got": got, "committed": want}
            if got != want:
                failures.append(f"{modality} thinking T {temp}: {got} != {want}")
    if failures:
        sys.exit("METHOD-REPLAY GATE FAIL:\n  " + "\n  ".join(failures))
    return record, stacks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def bh_family(rows: dict[str, dict]) -> dict:
    """BH across a family of contrast rows, in the given key order.

    Mutates each row with ``p_bh_adjusted`` (6 dp) and ``bh_rejects_at_q``.
    """
    labels = list(rows)
    raw = [float(rows[k]["delta_bootstrap"]["p_value"]) for k in labels]
    adj = [round(p, 6) for p in bh_adjust(raw)]
    for k, p in zip(labels, adj):
        rows[k]["p_bh_adjusted"] = p
        rows[k]["bh_rejects_at_q"] = bool(p <= BH_Q)
    return {"family": labels, "q": BH_Q, "p_permutation": dict(zip(labels, raw)),
            "p_bh_adjusted": dict(zip(labels, adj))}


def analyse(stacks: dict, floors: dict, mask: np.ndarray | None,
            affected: set[str] | None, floors_masked: dict | None = None) -> dict:
    """P3-P5 on one tile set: factor T, thinking, corner gap, verdicts.

    Args:
        stacks: D64 per-pass stacks keyed (modality, think, temp).
        floors: Verdict floors keyed modality -> {"k", "p95", "corners"}.
        mask: Tile mask, or None for all 487.
        affected: For the sensitivity, the contrast labels the mask applies
            to (others use all tiles); None applies the mask everywhere.
        floors_masked: Floors measured on the masked tiles, used for the
            contrasts the mask applies to (others keep ``floors``).

    Returns:
        Dict of factor-T rows, thinking rows, corner rows, BH summaries,
        and the per-modality answer.
    """
    def use_mask(label: str) -> np.ndarray | None:
        if mask is None:
            return None
        return mask if (affected is None or label in affected) else None

    def floor_for(label: str, modality: str, corners: tuple[str, str],
                  delta: float) -> dict:
        masked = use_mask(label) is not None and floors_masked and modality in floors_masked
        f = floors_masked[modality] if masked else floors[modality]
        # Passes per arm, read from the stack (N_PASSES before P12; equal
        # for P1-P11, and 6 for the pooled image passes of P12).
        n = stacks[(modality, THINKS[0], TEMPS[0])].shape[0]
        primary = floor_verdict(delta, f["p95"], f["k"], n)
        own = floor_verdict(delta, pct([r["abs_delta"] for c in corners
                                        for r in f["corner_rows"][c]], 0.95), f["k"], n)
        return {"modality_pooled": primary, "two_corners_pooled": own,
                "verdicts_differ": primary["verdict"] != own["verdict"]}

    factor_t, thinking, corner_gap = {}, {}, {}
    for modality in ("text", "image"):
        for think in THINKS:
            label = f"{modality} {think.upper()}"
            c0, c7 = f"{modality}-{think}-t0.0", f"{modality}-{think}-t0.7"
            row = contrast(stacks[(modality, think, "0.0")],
                           stacks[(modality, think, "0.7")], use_mask(label))
            row["contrast"] = f"T 0.0 minus T 0.7 at {think.upper()} ({modality})"
            row["rule_fires (pass-averaged)"] = row["delta (pass-averaged micro)"] >= RULE
            row["rule_fires (mean of per-pass)"] = row["delta (mean of per-pass F1)"] >= RULE
            row["estimator_split"] = (row["rule_fires (pass-averaged)"]
                                      != row["rule_fires (mean of per-pass)"])
            row["floor"] = floor_for(label, modality, (c0, c7),
                                     row["delta (pass-averaged micro)"])
            factor_t[label] = row
        for temp in TEMPS:
            label = f"{modality} thinking at T {temp}"
            ch, cm = f"{modality}-high-t{temp}", f"{modality}-medium-t{temp}"
            row = contrast(stacks[(modality, "high", temp)],
                           stacks[(modality, "medium", temp)], use_mask(label))
            row["contrast"] = f"HIGH minus MEDIUM at T {temp} ({modality})"
            row["reaches_0.03 (pass-averaged)"] = abs(row["delta (pass-averaged micro)"]) >= RULE
            row["reaches_0.03 (mean of per-pass)"] = (
                abs(row["delta (mean of per-pass F1)"]) >= RULE)
            row["floor"] = floor_for(label, modality, (ch, cm),
                                     row["delta (pass-averaged micro)"])
            thinking[label] = row
        label = f"{modality} corner gap"
        row = contrast(stacks[(modality, "high", "0.0")],
                       stacks[(modality, "medium", "0.7")], use_mask(label))
        row["contrast"] = f"HIGH T 0.0 minus MEDIUM T 0.7 ({modality}); no BH family"
        row["floor"] = floor_for(label, modality,
                                 (f"{modality}-high-t0.0", f"{modality}-medium-t0.7"),
                                 row["delta (pass-averaged micro)"])
        corner_gap[modality] = row

    # BH: the registered factor-T family through A-06's own helper (fixed
    # order text HIGH, text MEDIUM, image HIGH, image MEDIUM), the thinking
    # family by itself, and all eight together as the P4 sensitivity.
    block = {m: {t: factor_t[f"{m} {t.upper()}"] for t in THINKS} for m in ("text", "image")}
    bh_t = apply_bh_to_factor_t(block)
    bh_th = bh_family(thinking)
    all8 = [float(r["delta_bootstrap"]["p_value"])
            for r in list(factor_t.values()) + list(thinking.values())]
    labels8 = list(factor_t) + list(thinking)
    adj8 = [round(p, 6) for p in bh_adjust(all8)]
    for lab, p in zip(labels8, adj8):
        (factor_t.get(lab) or thinking[lab])["p_bh_adjusted (all eight)"] = p
    # The thinking family's own adjustment, renamed so it cannot be read as
    # the factor-T family's.
    for row in thinking.values():
        row["p_bh_adjusted (thinking family)"] = row.pop("p_bh_adjusted")
        row["bh_rejects_at_q (thinking family)"] = row.pop("bh_rejects_at_q")

    for modality in ("text", "image"):
        g = corner_gap[modality]["delta (pass-averaged micro)"]
        t_hi = factor_t[f"{modality} HIGH"]["delta (pass-averaged micro)"]
        t_md = factor_t[f"{modality} MEDIUM"]["delta (pass-averaged micro)"]
        th_7 = thinking[f"{modality} thinking at T 0.7"]["delta (pass-averaged micro)"]
        th_0 = thinking[f"{modality} thinking at T 0.0"]["delta (pass-averaged micro)"]
        corner_gap[modality]["decomposition"] = {
            "T at HIGH + thinking at T 0.7": [t_hi, th_7, round(t_hi + th_7, 6)],
            "T at MEDIUM + thinking at T 0.0": [t_md, th_0, round(t_md + th_0, 6)],
            "temperature share (via HIGH)": round(t_hi / g, 4) if g else None,
            "temperature share (via MEDIUM)": round(t_md / g, 4) if g else None,
            "_note": ("Shares from 6-dp deltas; the sums equal the gap to "
                      "rounding because micro-F1 differences are additive."),
        }

    answer = {}
    for modality in ("text", "image"):
        def rpf(row: dict, rule_key: str) -> dict:
            return {"R": bool(row[rule_key]), "P": bool(row.get(
                "bh_rejects_at_q_0.05", row.get("bh_rejects_at_q (thinking family)"))),
                "F": row["floor"]["modality_pooled"]["verdict"] == "clears"}
        t_flags = {t: rpf(factor_t[f"{modality} {t.upper()}"], "rule_fires (pass-averaged)")
                   for t in THINKS}
        th_flags = {tp: rpf(thinking[f"{modality} thinking at T {tp}"],
                            "reaches_0.03 (pass-averaged)") for tp in TEMPS}
        full = [all(f.values()) for f in t_flags.values()]
        deltas = [factor_t[f"{modality} {t.upper()}"]["delta (pass-averaged micro)"]
                  for t in THINKS]
        thinking_claim = any(f["R"] and f["P"] and f["F"] for f in th_flags.values())
        if any(d <= -RULE for d in deltas):
            label = "reversed"
        elif not any(f["R"] for f in t_flags.values()):
            label = "not supported"
        elif all(full) and not thinking_claim:
            label = "temperature is the driver"
        elif any(full) and not all(full):
            label = "temperature is the driver at one thinking level only"
        elif any(f["R"] and f["P"] and not f["F"] for f in t_flags.values()):
            label = "the difference holds between outputs, not configurations"
        else:
            label = "none of the pre-specified labels applies; see flags"
        answer[modality] = {"label": label, "factor_T_flags": t_flags,
                            "thinking_flags": th_flags,
                            "thinking_configuration_claim": thinking_claim}
    return {"factor_T": factor_t, "thinking": thinking, "corner_gap": corner_gap,
            "bh_factor_T": bh_t, "bh_thinking": bh_th,
            "bh_all_eight": dict(zip(labels8, adj8)), "answer": answer}


def build_floors(stacks: dict, mask: np.ndarray | None,
                 modalities: tuple[str, ...] = ("text", "image")
                 ) -> tuple[dict, list[dict]]:
    """P6: floors per corner and pooled per modality, at every K measured.

    Returns:
        (floor summary keyed modality, flat list of pair rows for the CSV).
    """
    floors, flat = {}, []
    for modality in modalities:
        # Every subset size the corners allow (two disjoint k-subsets need
        # 2k passes): (1, 2) for five passes and (1,) for three, as before
        # P12; (1, 2, 3) for six.
        n = stacks[(modality, THINKS[0], TEMPS[0])].shape[0]
        ks = tuple(range(1, n // 2 + 1))
        by_k = {}
        for k in ks:
            corner_rows = {}
            for think in THINKS:
                for temp in TEMPS:
                    corner = f"{modality}-{think}-t{temp}"
                    rows = floor_pairs(stacks[(modality, think, temp)], k, mask)
                    corner_rows[corner] = rows
                    flat += [{"corner": corner, "k": k, **r} for r in rows]
            pooled = [r for rows in corner_rows.values() for r in rows]
            by_k[k] = {"pooled": summarise_floor(pooled),
                       "per_corner": {c: summarise_floor(r) for c, r in corner_rows.items()},
                       "corner_rows": corner_rows}
        k_star = max(ks)
        floors[modality] = {"k": k_star, "p95": by_k[k_star]["pooled"]["p95"],
                            "corner_rows": by_k[k_star]["corner_rows"],
                            "by_k": {k: {kk: vv for kk, vv in v.items() if kk != "corner_rows"}
                                     for k, v in by_k.items()}}
    return floors, flat


def main() -> int:
    """Run the gates, the analysis on all tiles, and the top-up sensitivity."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    gdf_ref = gpd.read_file(GROUND_TRUTH).to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file(BOUNDS).to_crs(TARGET_CRS)
    tile_order = list(gdf_bounds["tile_name"].unique())
    if len(tile_order) != 487:
        sys.exit(f"GATE FAIL: {len(tile_order)} tiles in the bounds file")

    print("Gates 1-2: parameter control and coverage ...", flush=True)
    metas = gate_metas(set(tile_order))

    print("Gate 3: replaying the committed A-06 ...", flush=True)
    replay, committed_stacks = gate_replay(gdf_ref, gdf_bounds, tile_order)

    print("Scoring the D64 passes ...", flush=True)
    stacks, files, identity, estimates = {}, {}, {}, {}
    for modality in ("text", "image"):
        for think in THINKS:
            for temp in TEMPS:
                corner = f"{modality}-{think}-t{temp}"
                pool = D64_DIR / corner / CONFIG[modality]
                # Every pass in the pool is scored, so the identity gate
                # still checks the A-06 helper over the whole pool; P1-P11
                # then keep the runs in P1_RUNS (image runs 1-3).
                files_all, stack_all = score_pool(pool, gdf_ref, gdf_bounds, tile_order)
                tp, fp, fn, n = pass_averaged_per_tile(pool, gdf_ref, gdf_bounds, tile_order)
                ours = pass_mean(stack_all)
                same = (n == stack_all.shape[0] and np.array_equal(ours[0], tp)
                        and np.array_equal(ours[1], fp) and np.array_equal(ours[2], fn))
                files[corner], stack = select_runs(files_all, stack_all, P1_RUNS[modality])
                if len(files[corner]) != N_PASSES[modality]:
                    sys.exit(f"GATE FAIL: {corner} has {len(files[corner])} passes")
                identity[corner] = same
                if not same:
                    sys.exit(f"AGGREGATION-IDENTITY GATE FAIL: {corner}")
                stacks[(modality, think, temp)] = stack
                estimates[corner] = corner_estimates(stack)

    print("Floors and contrasts (all 487 tiles) ...", flush=True)
    floors, flat = build_floors(stacks, None)
    main_result = analyse(stacks, floors, None, None)

    print("Sensitivity: the 15 topped-up tiles dropped ...", flush=True)
    topup = json.loads(TOPUP.read_text())
    dropped = sorted({t for u in topup["units"] for t in u["failed_before"]})
    mask = np.array([t not in set(dropped) for t in tile_order])
    affected = {"text HIGH", "text thinking at T 0.0", "text thinking at T 0.7",
                "text corner gap"}
    # Only text passes were topped up: the text floors are re-measured on
    # the 472 tiles and used for the affected contrasts; every other
    # contrast keeps its tiles and its floor, so it is unchanged.
    floors_s, flat_s = build_floors(stacks, mask, ("text",))
    sens = analyse(stacks, floors, mask, affected, floors_s)

    print("Side by side with the committed A-06 ...", flush=True)
    committed = json.loads(COMMITTED_A06.read_text())
    conditions_doc = json.loads(CONDITIONS_MANIFEST.read_text())
    conditions = conditions_doc.get("conditions", conditions_doc)
    if isinstance(conditions, dict):
        conditions = list(conditions.values())
    side = {}
    for (modality, think, temp), rec in committed_stacks.items():
        corner = f"{modality}-{think}-t{temp}"
        run, cid = rec["ref"].split("::")
        est = corner_estimates(rec["stack"])
        new = estimates[corner]["pass_averaged_micro"]["f1"]
        side[corner] = {
            "committed_ref": rec["ref"], "committed_passes": est["n_passes"],
            "committed_manifest_f1": committed_f1(conditions, run, cid),
            "committed_pass_averaged_f1": est["pass_averaged_micro"]["f1"],
            "committed_mean_of_pass_f1": est["mean_of_pass_f1"],
            "d64_pass_averaged_f1": new,
            "d64_mean_of_pass_f1": estimates[corner]["mean_of_pass_f1"],
            "d64_minus_committed (pass-averaged)": round(
                new - est["pass_averaged_micro"]["f1"], 6),
            "exceeds_modality_floor": abs(new - est["pass_averaged_micro"]["f1"])
            > floors[modality]["p95"],
        }
    # The committed A-06's contrast rows, read from its artefact as they stand.
    side_contrasts = {}
    for modality in ("text", "image"):
        for think in THINKS:
            r = committed["registered_factor_T"][modality][think]
            side_contrasts[f"{modality} {think.upper()}"] = {
                "delta (manifest eval vintage)": r["delta (manifest eval vintage)"],
                "delta (pass-averaged micro vintage)": r["delta (pass-averaged micro vintage)"],
                "ci95": r["delta_ci95_paired_bootstrap"],
                "p_permutation": r["delta_bootstrap"]["p_value"],
                "p_bh_adjusted": r.get("p_bh_adjusted"),
                "rule_fires": r["registered_rule_fires (delta >= 0.03)"],
                "n_passes": r["n_passes"]}
        for temp, key in (("0.0", "t0-0"), ("0.7", "t0-7")):
            r = committed["thinking_decomposition_context (not a registered factor)"][
                modality][key]
            side_contrasts[f"{modality} thinking at T {temp}"] = {
                "delta (manifest eval vintage)": r["delta"],
                "ci95": r["delta_ci95_paired_bootstrap"],
                "reaches_0.03": r["reaches_0.03"]}

    def strip(result: dict) -> dict:
        """Drop the per-pair rows (they go to the CSV) from the floor block."""
        return {m: {k: v for k, v in f.items() if k != "corner_rows"}
                for m, f in result.items()}

    doc = {
        "_README": ("A-06's registered rule on the D64 same-day genuine-Pro 2x2 "
                    "(report only; plan reports/s164-agent-records/"
                    "d64-a06-replication.md, plan commit 7ae996ce6)."),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
        "settings": {"buffer_m": BUFFER_M, "bootstrap_B": B_DELTA_CI, "seed": SEED,
                     "permutations": 10_000, "bh_q": BH_Q, "rule": RULE,
                     "tiles": len(tile_order), "scorer": "lib_advanced_metrics."
                     "compute_per_tile_tp_fp_fn (D50, main)"},
        "gates": {"metas_and_coverage": "pass (32 passes)",
                  "method_replay": replay, "aggregation_identity": identity},
        "pass_files": files,
        "thought_tokens": metas,
        "corners": estimates,
        "floors": strip(floors),
        "main": main_result,
        "sensitivity_topup": {"dropped_tiles": dropped, "n_dropped": len(dropped),
                              "affected_contrasts": sorted(affected),
                              "floors_text": strip(floors_s)["text"], **sens},
        "side_by_side": {"corners": side, "committed_contrasts": side_contrasts},
    }
    (args.out / "d64_a06_results.json").write_text(
        json.dumps(doc, indent=1, sort_keys=False, default=str) + "\n")
    for name, rows in (("floor_pairs.csv", flat), ("floor_pairs_sensitivity.csv", flat_s)):
        with open(args.out / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            for r in rows:
                w.writerow({k: json.dumps(v) if isinstance(v, list) else v
                            for k, v in r.items()})
    # Per-pass counts for re-use; compared member by member in the
    # integrity check (the zip container stamps write times).
    np.savez_compressed(args.out / "d64_per_pass_counts.npz", tile_order=np.array(tile_order),
                        **{f"{m}-{t}-t{tp}": stacks[(m, t, tp)] for (m, t, tp) in stacks})
    print(f"Wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
