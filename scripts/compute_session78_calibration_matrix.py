#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# compute_session78_calibration_matrix.py
# ---------------------------------------------------------------------------
# Purpose
# -------
# Compute per-cell calibration metrics (AUC, Brier, ECE, per-bin empirical
# P(mound), low-tail miscalibration) for the Session 78 verifier
# calibration matrix. Fourteen cells = {6 novel variants + canonical
# adversarial-text} x {image pool, text pool}.
#
# This is the Observation 269-equivalent analysis: it answers whether any
# prompt variant changes the image-track miscalibration first observed on
# the 55-map canonical verifier.
#
# Ground truth
# ------------
# Spatial matching at 20 m buffer against curator-labelled reference mounds
# (inputs/vectors/references/mounds-reference.geojson, 569 features,
# EPSG:32635). Candidate centroids are already in EPSG:32635 (confirmed by
# inspection of candidate_manifest.json), so no reprojection needed.
#
# Scope filter
# ------------
# Candidates restricted to those whose source_tile is in the 487-tile
# Era 2 evaluation scope (inputs/vectors/bounds/384/
# full_evaluation_bounds.geojson).
#
# Outputs
# -------
# - results/verifier-calibration-matrix/<pool>-<variant>/calibration.json
#   (14 files, one per cell)
# - planning/session-78-matrix-calibration-summary.md
#
# Usage
# -----
#   .venv/bin/python scripts/compute_session78_calibration_matrix.py
#
# Run on sapphire per project convention.
# Language: UK/Australian English throughout.
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from sklearn.metrics import brier_score_loss, roc_auc_score

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

REFERENCE_PATH = REPO_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS_PATH = REPO_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

BUFFER_METRES = 20.0
N_BOOTSTRAP = 10_000
BOOTSTRAP_SEED = 42

POOLS = {
    "image": REPO_ROOT / "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
    "text": REPO_ROOT / "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
}

NOVEL_VARIANTS = [
    "adversarial",
    "brief",
    "brief-text",
    "checklist",
    "checklist-text",
    "comparative",
]
CANONICAL_VARIANT = "adversarial-text"

OUT_ROOT = REPO_ROOT / "results/verifier-calibration-matrix"
SUMMARY_PATH = REPO_ROOT / "planning/session-78-matrix-calibration-summary.md"

# ECE bin edges: 10 equal-width bins on [0, 1].
ECE_BIN_EDGES = np.linspace(0.0, 1.0, 11)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


@dataclass
class PoolData:
    """Shared per-pool data (candidates + GT labels)."""

    pool: str
    candidate_ids: np.ndarray  # shape (n,), dtype=object (strings)
    y_true: np.ndarray  # shape (n,), 0/1 ground truth
    in_scope: np.ndarray  # shape (n,), boolean — within 487-tile allowlist


def load_pool_data(pool_name: str, pool_dir: Path) -> PoolData:
    """Load candidate manifest, assign ground-truth labels, filter scope."""
    manifest_path = (
        pool_dir / "session-78-matrix" / "shared-crops" / "candidate_manifest.json"
    )
    with open(manifest_path) as f:
        manifest = json.load(f)
    cands = manifest["candidates"]

    # Build candidate arrays. Centroids are already in EPSG:32635.
    ids, xs, ys, tiles = [], [], [], []
    for c in cands:
        ids.append(f"candidate_{c['candidate_id']:05d}")
        xs.append(c["centroid_x"])
        ys.append(c["centroid_y"])
        tiles.append(c["source_tile"])

    # Reference mounds (already in EPSG:32635).
    ref = gpd.read_file(REFERENCE_PATH).to_crs("EPSG:32635")
    # Explode MultiPoints to individual points so sjoin_nearest works cleanly.
    ref_points = ref.explode(index_parts=False).reset_index(drop=True)

    cand_gdf = gpd.GeoDataFrame(
        {"candidate_id": ids, "source_tile": tiles},
        geometry=[Point(x, y) for x, y in zip(xs, ys)],
        crs="EPSG:32635",
    )

    # Ground truth via nearest-neighbour distance <= 20 m.
    joined = gpd.sjoin_nearest(
        cand_gdf,
        ref_points[["geometry"]],
        how="left",
        distance_col="dist_m",
    )
    # If a candidate matched multiple ref points (rare with sjoin_nearest),
    # keep the minimum distance.
    joined = joined.loc[joined.groupby("candidate_id")["dist_m"].idxmin()]
    joined = joined.set_index("candidate_id").loc[ids]  # restore order
    y_true = (joined["dist_m"].to_numpy() <= BUFFER_METRES).astype(int)

    # Scope filter: source_tile must be in the 487-tile allowlist.
    bounds = gpd.read_file(BOUNDS_PATH)
    allowlist = set(bounds["tile_name"].tolist())
    in_scope = np.array([t in allowlist for t in tiles], dtype=bool)

    return PoolData(
        pool=pool_name,
        candidate_ids=np.array(ids, dtype=object),
        y_true=y_true,
        in_scope=in_scope,
    )


def load_probabilities(prob_path: Path, candidate_ids: np.ndarray) -> np.ndarray:
    """Load mound_probability aligned to candidate_ids (NaN if missing)."""
    with open(prob_path) as f:
        data = json.load(f)
    results = data["results"]
    out = np.full(len(candidate_ids), np.nan, dtype=float)
    for i, cid in enumerate(candidate_ids):
        if cid in results:
            out[i] = float(results[cid]["mound_probability"])
    return out


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def compute_ece(y_true: np.ndarray, y_score: np.ndarray) -> tuple[float, list[dict]]:
    """Expected Calibration Error and per-bin diagnostics.

    Uses 10 equal-width bins on [0, 1]. Bin i covers [edge_i, edge_{i+1}],
    with the last bin right-inclusive so p == 1.0 is counted.
    """
    n = len(y_true)
    ece = 0.0
    bins: list[dict] = []
    for i in range(len(ECE_BIN_EDGES) - 1):
        lo = float(ECE_BIN_EDGES[i])
        hi = float(ECE_BIN_EDGES[i + 1])
        if i == len(ECE_BIN_EDGES) - 2:
            mask = (y_score >= lo) & (y_score <= hi)
        else:
            mask = (y_score >= lo) & (y_score < hi)
        count = int(mask.sum())
        if count > 0:
            mean_pred = float(y_score[mask].mean())
            emp = float(y_true[mask].mean())
            ece += (count / n) * abs(mean_pred - emp)
        else:
            mean_pred = None
            emp = None
        bins.append(
            {
                "lo": lo,
                "hi": hi,
                "count": count,
                "mean_predicted": mean_pred,
                "empirical_p_mound": emp,
            }
        )
    return float(ece), bins


def compute_low_tail_p_mound(
    y_true: np.ndarray, y_score: np.ndarray, threshold: float = 0.25
) -> float | None:
    """Empirical P(mound) for candidates with p <= threshold (Obs 269 metric)."""
    mask = y_score <= threshold
    if mask.sum() == 0:
        return None
    return float(y_true[mask].mean())


def bootstrap_metrics(
    y_true: np.ndarray,
    y_score: np.ndarray,
    n_boot: int = N_BOOTSTRAP,
    seed: int = BOOTSTRAP_SEED,
) -> dict:
    """Bootstrap CIs for AUC, Brier, ECE, low-tail P(mound)."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    aucs = np.empty(n_boot)
    briers = np.empty(n_boot)
    eces = np.empty(n_boot)
    low_tails = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yt = y_true[idx]
        ys = y_score[idx]
        # AUC requires both classes; skip with NaN otherwise.
        if yt.sum() == 0 or yt.sum() == n:
            aucs[b] = np.nan
        else:
            aucs[b] = roc_auc_score(yt, ys)
        briers[b] = brier_score_loss(yt, ys)
        eces[b], _ = compute_ece(yt, ys)
        lt = compute_low_tail_p_mound(yt, ys)
        low_tails[b] = lt if lt is not None else np.nan
    return {
        "auc": (float(np.nanpercentile(aucs, 2.5)), float(np.nanpercentile(aucs, 97.5))),
        "brier": (float(np.percentile(briers, 2.5)), float(np.percentile(briers, 97.5))),
        "ece": (float(np.percentile(eces, 2.5)), float(np.percentile(eces, 97.5))),
        "low_tail": (
            float(np.nanpercentile(low_tails, 2.5)),
            float(np.nanpercentile(low_tails, 97.5)),
        ),
    }


# ---------------------------------------------------------------------------
# Per-cell calibration
# ---------------------------------------------------------------------------


def resolve_prob_path(pool_dir: Path, variant: str) -> Path:
    """Return path to probabilities.json for a given variant on a pool.

    After the 2026-04-25 re-run, canonical (adversarial-text) lives in
    session-78-matrix alongside the novel variants — all share the same
    shared-crops candidate set. The legacy verified-v1-n5 path is
    no longer canonical for this matrix.
    """
    return (
        pool_dir
        / "session-78-matrix"
        / f"verified-{variant}"
        / "probabilities.json"
    )


def compute_cell(
    pool: str,
    variant: str,
    pool_data: PoolData,
    pool_dir: Path,
) -> dict:
    """Compute calibration metrics for a single (pool, variant) cell."""
    prob_path = resolve_prob_path(pool_dir, variant)
    y_score_all = load_probabilities(prob_path, pool_data.candidate_ids)

    # Require: candidate in scope AND has a probability.
    mask = pool_data.in_scope & ~np.isnan(y_score_all)
    y_true = pool_data.y_true[mask]
    y_score = y_score_all[mask]

    n_total = int(mask.sum())
    n_mound = int(y_true.sum())
    n_not = n_total - n_mound
    prevalence = n_mound / n_total if n_total > 0 else None

    auc_point = roc_auc_score(y_true, y_score) if 0 < n_mound < n_total else None
    brier_point = brier_score_loss(y_true, y_score) if n_total > 0 else None
    ece_point, bins = compute_ece(y_true, y_score)
    low_tail_point = compute_low_tail_p_mound(y_true, y_score)

    ci = bootstrap_metrics(y_true, y_score)

    return {
        "pool": pool,
        "variant": variant,
        "prob_path": str(prob_path.relative_to(REPO_ROOT)),
        "buffer_metres": BUFFER_METRES,
        "scope_tiles": 487,
        "n_total": n_total,
        "n_mound": n_mound,
        "n_not_mound": n_not,
        "prevalence": prevalence,
        "auc": {
            "point": auc_point,
            "ci_lower": ci["auc"][0],
            "ci_upper": ci["auc"][1],
        },
        "brier": {
            "point": brier_point,
            "ci_lower": ci["brier"][0],
            "ci_upper": ci["brier"][1],
        },
        "ece": {
            "point": ece_point,
            "ci_lower": ci["ece"][0],
            "ci_upper": ci["ece"][1],
        },
        "p_mound_low_tail": {
            "threshold": 0.25,
            "mean": low_tail_point,
            "ci_lower": ci["low_tail"][0],
            "ci_upper": ci["low_tail"][1],
        },
        "calibration_bins": bins,
        "bootstrap": {
            "n_iterations": N_BOOTSTRAP,
            "seed": BOOTSTRAP_SEED,
        },
    }


# ---------------------------------------------------------------------------
# Summary markdown
# ---------------------------------------------------------------------------


def write_summary(cells: list[dict]) -> None:
    """Author the summary markdown (pool x variant x AUC/Brier/ECE table)."""
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    variants_order = NOVEL_VARIANTS + [CANONICAL_VARIANT]
    by_cell = {(c["pool"], c["variant"]): c for c in cells}

    def fmt(x):
        return "—" if x is None else f"{x:.3f}"

    lines: list[str] = []
    lines.append("# Session 78 Verifier Calibration Matrix — Summary")
    lines.append("")
    lines.append(
        "Per-cell calibration metrics (AUC, Brier, ECE) for the Session 78 "
        "verifier prompt variant matrix. Fourteen cells = seven verifier "
        "variants (six novel alternatives + the canonical "
        "`adversarial-text`) across two candidate pools (image track, text "
        "track). Ground truth: spatial matching at 20 m buffer vs. curator "
        "reference mounds (`inputs/vectors/references/mounds-reference.geojson`, "
        "569 features). Candidates filtered to the 487-tile Era 2 "
        "evaluation scope."
    )
    lines.append("")
    lines.append("## Main table")
    lines.append("")
    lines.append(
        "| pool | variant | n_total | prevalence | AUC | Brier | ECE | "
        "P(mound\\|p<=0.25) |"
    )
    lines.append("|------|---------|---------|-----------|-----|-------|-----|---------------------|")
    for pool in ("image", "text"):
        for v in variants_order:
            c = by_cell.get((pool, v))
            if c is None:
                continue
            lines.append(
                "| {pool} | {variant} | {n} | {prev} | {auc} ({alo}–{ahi}) | "
                "{br} ({blo}–{bhi}) | {ece} ({elo}–{ehi}) | {lt} |".format(
                    pool=pool,
                    variant=v,
                    n=c["n_total"],
                    prev=fmt(c["prevalence"]),
                    auc=fmt(c["auc"]["point"]),
                    alo=fmt(c["auc"]["ci_lower"]),
                    ahi=fmt(c["auc"]["ci_upper"]),
                    br=fmt(c["brier"]["point"]),
                    blo=fmt(c["brier"]["ci_lower"]),
                    bhi=fmt(c["brier"]["ci_upper"]),
                    ece=fmt(c["ece"]["point"]),
                    elo=fmt(c["ece"]["ci_lower"]),
                    ehi=fmt(c["ece"]["ci_upper"]),
                    lt=fmt(c["p_mound_low_tail"]["mean"]),
                )
            )
    lines.append("")

    # Obs 269 comparison
    img_canon = by_cell.get(("image", CANONICAL_VARIANT))
    lines.append("## Comparison to Observation 269")
    lines.append("")
    lines.append(
        "Observation 269 (55-map image-track canonical, earlier session "
        "work) reported **AUC = 0.655, ECE = 0.269** — a strongly "
        "miscalibrated low-tail where candidates with low verifier "
        "probability still carried high empirical mound rates."
    )
    lines.append("")
    if img_canon is not None:
        lines.append(
            "Current run, image track, canonical `adversarial-text` "
            "(Era 2 scope, 4-map gold-standard corpus):"
        )
        lines.append("")
        lines.append(
            f"- AUC = {fmt(img_canon['auc']['point'])} "
            f"(95% CI: {fmt(img_canon['auc']['ci_lower'])}–"
            f"{fmt(img_canon['auc']['ci_upper'])})"
        )
        lines.append(
            f"- ECE = {fmt(img_canon['ece']['point'])} "
            f"(95% CI: {fmt(img_canon['ece']['ci_lower'])}–"
            f"{fmt(img_canon['ece']['ci_upper'])})"
        )
        lines.append(
            f"- P(mound | p<=0.25) = {fmt(img_canon['p_mound_low_tail']['mean'])}"
        )
        lines.append("")
        lines.append(
            "Note: Obs 269 scope is 55 maps; this run's scope is the "
            "four-map gold-standard corpus (487-tile Era 2). Differences "
            "in corpus composition confound a direct numerical comparison, "
            "but the qualitative pattern (low-tail P(mound) vs AUC vs ECE) "
            "is what the matrix is designed to probe."
        )
    lines.append("")

    # Per-track top/bottom
    lines.append("## Top and bottom per track")
    lines.append("")
    for pool in ("image", "text"):
        pool_cells = [c for c in cells if c["pool"] == pool]
        if not pool_cells:
            continue
        # Rank by ECE (lower = better calibrated)
        by_ece = sorted(pool_cells, key=lambda c: c["ece"]["point"])
        by_auc = sorted(
            pool_cells,
            key=lambda c: (c["auc"]["point"] if c["auc"]["point"] is not None else -1),
            reverse=True,
        )
        lines.append(f"**{pool} track**")
        lines.append("")
        lines.append(
            f"- Best ECE: `{by_ece[0]['variant']}` "
            f"(ECE = {fmt(by_ece[0]['ece']['point'])}, "
            f"AUC = {fmt(by_ece[0]['auc']['point'])})"
        )
        lines.append(
            f"- Worst ECE: `{by_ece[-1]['variant']}` "
            f"(ECE = {fmt(by_ece[-1]['ece']['point'])}, "
            f"AUC = {fmt(by_ece[-1]['auc']['point'])})"
        )
        lines.append(
            f"- Best AUC: `{by_auc[0]['variant']}` "
            f"(AUC = {fmt(by_auc[0]['auc']['point'])}, "
            f"ECE = {fmt(by_auc[0]['ece']['point'])})"
        )
        lines.append("")

    # Interpretation
    lines.append("## Interpretation")
    lines.append("")
    img_cells = [c for c in cells if c["pool"] == "image"]
    if img_canon is not None and img_cells:
        canon_ece = img_canon["ece"]["point"]
        canon_auc = img_canon["auc"]["point"]
        improvers = [
            c
            for c in img_cells
            if c["variant"] != CANONICAL_VARIANT
            and c["ece"]["point"] < canon_ece
            and (c["auc"]["point"] or 0) >= (canon_auc or 0)
        ]
        lines.append(
            "Variants on the image track that improve both ECE and AUC "
            "versus the canonical `adversarial-text`:"
        )
        lines.append("")
        if improvers:
            for c in improvers:
                lines.append(
                    f"- `{c['variant']}`: ECE "
                    f"{fmt(c['ece']['point'])} vs canonical "
                    f"{fmt(canon_ece)}; AUC {fmt(c['auc']['point'])} vs "
                    f"canonical {fmt(canon_auc)}"
                )
        else:
            lines.append(
                "- None — no matrix variant dominates the canonical "
                "`adversarial-text` on both ECE and AUC simultaneously."
            )
        lines.append("")
        # Does any variant clear the Obs 269 image miscalibration (ECE ~ 0.27)?
        cleared = [c for c in img_cells if c["ece"]["point"] < 0.10]
        lines.append(
            "Obs 269 image-track miscalibration pattern = ECE ~ 0.27. "
            "Variants on this run that sit well below that threshold "
            "(ECE < 0.10):"
        )
        lines.append("")
        if cleared:
            for c in sorted(cleared, key=lambda x: x["ece"]["point"]):
                lines.append(
                    f"- `{c['variant']}`: ECE = {fmt(c['ece']['point'])}"
                )
        else:
            lines.append(
                "- None — no image-track variant clears ECE < 0.10; all "
                "sit in the miscalibrated regime."
            )
        lines.append("")

    # Anomalies
    lines.append("## Anomaly flags")
    lines.append("")
    anoms: list[str] = []
    # Very low n — suggests scope / manifest mismatch.
    for c in cells:
        if c["n_total"] < 100:
            anoms.append(
                f"- `{c['pool']}-{c['variant']}`: only {c['n_total']} "
                "in-scope candidates with probabilities — check manifest / "
                "probabilities alignment."
            )
        if c["prevalence"] is not None and (
            c["prevalence"] < 0.05 or c["prevalence"] > 0.98
        ):
            anoms.append(
                f"- `{c['pool']}-{c['variant']}`: extreme prevalence "
                f"{c['prevalence']:.3f} — AUC may be unstable."
            )
    # Image-pool GT coverage caveat
    anoms.append(
        "- Image-track reference-GT coverage: `mounds-reference.geojson` "
        "is the curator ground truth for the four-map gold-standard "
        "corpus. If any image-pool candidates fall on tiles outside the "
        "corpus reference coverage, their zero-label assignments may "
        "under-count true mounds. The 487-tile scope filter mitigates "
        "this, but the caveat persists for any corpus expansion."
    )
    for a in anoms:
        lines.append(a)
    lines.append("")

    lines.append("## Method")
    lines.append("")
    lines.append(
        "- Ground truth: candidate centroid within 20 m of any reference "
        "mound centroid (EPSG:32635, `gpd.sjoin_nearest`)."
    )
    lines.append(
        "- ECE: 10 equal-width probability bins on `[0, 1]`; weighted "
        "mean `|mean_predicted - empirical_P(mound)|`."
    )
    lines.append(
        f"- Bootstrap: {N_BOOTSTRAP:,} resamples with replacement, "
        f"seed={BOOTSTRAP_SEED}; 95% percentile CIs."
    )
    lines.append(
        "- Scope filter: `inputs/vectors/bounds/384/"
        "full_evaluation_bounds.geojson` (487 tiles, Era 2)."
    )
    lines.append("")
    lines.append(
        "Per-cell machine-readable results at "
        "`results/verifier-calibration-matrix/<pool>-<variant>/calibration.json`."
    )
    lines.append("")

    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    all_variants = NOVEL_VARIANTS + [CANONICAL_VARIANT]

    # Load per-pool data once (shared across variants on the same pool).
    print("Loading pool data ...")
    pool_data: dict[str, PoolData] = {}
    for pool_name, pool_dir in POOLS.items():
        pd_obj = load_pool_data(pool_name, pool_dir)
        pool_data[pool_name] = pd_obj
        n_scope = int(pd_obj.in_scope.sum())
        n_mound = int(pd_obj.y_true[pd_obj.in_scope].sum())
        print(
            f"  [{pool_name}] total={len(pd_obj.candidate_ids)} "
            f"in_scope={n_scope} in_scope_mound={n_mound}"
        )

    # Build cell task list.
    tasks = [
        (pool, variant, pool_data[pool], POOLS[pool])
        for pool in POOLS
        for variant in all_variants
    ]

    def _run(args):
        pool, variant, pd_obj, pool_dir = args
        print(f"  computing {pool}-{variant} ...")
        return compute_cell(pool, variant, pd_obj, pool_dir)

    print(f"Computing {len(tasks)} cells ...")
    with ThreadPoolExecutor(max_workers=4) as ex:
        cells = list(ex.map(_run, tasks))

    # Write per-cell JSON.
    for c in cells:
        cell_dir = OUT_ROOT / f"{c['pool']}-{c['variant']}"
        cell_dir.mkdir(parents=True, exist_ok=True)
        out_path = cell_dir / "calibration.json"
        with open(out_path, "w") as f:
            json.dump(c, f, indent=2)
        print(f"  wrote {out_path.relative_to(REPO_ROOT)}")

    # Write summary markdown.
    write_summary(cells)
    print(f"  wrote {SUMMARY_PATH.relative_to(REPO_ROOT)}")

    # Print compact table to stdout for the report.
    print()
    print("=" * 80)
    print(f"{'pool':6s} {'variant':18s} {'n':>5s} {'prev':>6s} "
          f"{'AUC':>6s} {'Brier':>6s} {'ECE':>6s} {'p<=.25':>7s}")
    print("-" * 80)
    for c in cells:
        print(
            f"{c['pool']:6s} {c['variant']:18s} "
            f"{c['n_total']:>5d} "
            f"{(c['prevalence'] or 0):>6.3f} "
            f"{(c['auc']['point'] or 0):>6.3f} "
            f"{(c['brier']['point'] or 0):>6.3f} "
            f"{(c['ece']['point'] or 0):>6.3f} "
            f"{(c['p_mound_low_tail']['mean'] or 0):>7.3f}"
        )
    print("=" * 80)


if __name__ == "__main__":
    main()
