#!/usr/bin/env python3
# ============================================================================
# build_pareto_leaderboard.py
# ----------------------------------------------------------------------------
# Session 111 ($0): the passes-vs-F1 Pareto leaderboard for the Gold-Standard
# 384 px proposer-verifier architecture (487 tiles, curator GT, F1@20 m), with
# targeted pairwise tile-swap permutation tests between ADJACENT pass-budget
# rungs of the Flash ladder.
#
# The Flash ladder (total passes = proposer passes + verifier passes):
#    6: 5-prop + n=1 carry-forward verifier (cheap end — scored HERE, new)
#   10: 5-prop + N=5 minimal T=0.3 verifier (matrix leader 0.8739)
#   11: 10-prop + n=1 verifier (0.8769, nof10_comparison.log)
#   31: 30-prop (16of30) + n=1 verifier (0.8902 — the registered headline)
#   35: 30-prop (16of30) + N=5 minimal T=0.3 verifier (opmax 0.8951)
#
# Context rows (table + figure only, no ladder test): high-thinking 10-pass
# (matrix; statistically tied with minimal), and the Pro-proposer 6-pass cells
# (pro_pv.log; different model, already compared in S110).
#
# Method (project-canonical, reused verbatim): materialise each rung's
# best-operating-point detection set, verify it reproduces its recorded
# F1@20 m (gate), compute per-tile TP/FP/FN (Hungarian per map, 20 m), then
# the FULL C(5,2)=10 round-robin permutation_test_float (10k, seed 42,
# two-sided), BH-FDR at q=0.05, and greedy-clique tiers — the same board
# machinery as the matrix and Era-1 leaderboards. Adjacent pairs answer the
# continuity's rung-step questions; the span pairs guard against the
# "no single step significant, but the cumulative climb is" trap.
#
# COST: $0 (on-disk re-score). Single process; the cheap-end sweep is ~40
# Hungarian scorings — run on zbook per the project compute rule.
#
# Usage:
#   .venv/bin/python scripts/build_pareto_leaderboard.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-10 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))  # consensus_vs_baseline uses bare imports
from scripts.analyse_verifier_robustness import (  # noqa: E402
    EVAL_CRS,
    GROUND_TRUTH,
    accepted_cids,
    load_candidate_table,
)
from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.consensus_vs_baseline_tiering import consensus_per_tile  # noqa: E402
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    greedy_clique_tiers,
    permutation_test_float,
)

VERIFIED = BASE_DIR / "outputs" / "h11" / "pv-diag-384" / "verified"
MATRIX_SETS = BASE_DIR / "results" / "verifier-robustness" / "matrix-sets"
OPMAX_SETS = BASE_DIR / "results" / "verifier-robustness" / "opmax-sets"
BOUNDS = BASE_DIR / "inputs" / "vectors" / "bounds" / "384" / "full_evaluation_bounds.geojson"
OUT_DIR = BASE_DIR / "results" / "verifier-robustness" / "pareto"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
N_PERMUTATIONS = 10000
SEED = 42

# Ladder rungs with a pre-materialised geojson carry an expected F1@20 m gate
# (4 d.p., from the committed logs/manifest). The cheap end has no prior
# record — it is scored fresh here and its op is discovered by the sweep.
LADDER_GEOJSON = [
    # (label, passes, proposer/verifier split, geojson, expected F1, op, source)
    ("min10", 10, (5, 5), MATRIX_SETS / "min-T0.3.geojson", 0.8739,
     "4of5 / mean / pt0.15 (N=5 min T0.3 verifier)", "matrix_tiering.json"),
    ("nof10", 11, (10, 1), None, 0.8769,
     "6of10 / n=1 / pt0.2", "nof10_comparison.log"),
    ("headline31", 31, (30, 1),
     BASE_DIR / "outputs/era1-pv-stage-d/384-consensus-text-high/pass_1/accepted_t0.2.geojson",
     0.8902, "16of30 / n=1 / pt0.2 (registered headline)",
     "pv-diag-384::verified-adv-text-consensus-16of30"),
    ("opmax35", 35, (30, 5),
     OPMAX_SETS / "opmax-16of30-N5minT0.3-vt3-pt0.15.geojson", 0.8951,
     "16of30 / consensus_vt3 / pt0.15 (N=5 min T0.3 verifier)",
     "robustness_summary_T0.3.json"),
]

CONTEXT_ROWS = [
    # Recorded values from committed S110 artefacts; no re-materialisation.
    {"label": "high10", "passes": 10, "split": [5, 5], "f1": 0.8764, "mcc": None,
     "op": "4of5 / consensus_vt5 / pt0.3 (N=5 HIGH T0.3 verifier, ~3x cost)",
     "source": "matrix_tiering.json", "note": "statistically tied with min10 (matrix tier 1)"},
    {"label": "pro6-flashvf", "passes": 6, "split": [5, 1], "f1": 0.8491, "mcc": 0.730,
     "op": "3of5 / n=1 / pt0.15 (Pro 3.1 proposer + Flash verifier)",
     "source": "pro_pv.log", "note": "different proposer model; S110 model comparison"},
    {"label": "pro6-provf", "passes": 6, "split": [5, 1], "f1": 0.8506, "mcc": 0.730,
     "op": "3of5 / n=1 / pt0.15 (Pro 3.1 proposer + Pro verifier)",
     "source": "pro_pv.log", "note": "different proposer + verifier model"},
]


def sweep_cheap6(gdf_ref: gpd.GeoDataFrame, gdf_bounds: gpd.GeoDataFrame) -> dict:
    """Score the cheap end: 5-pass proposer union + n=1 carry-forward verifier.

    Sweeps proposer k-of-5 x prob_t over the flash-high-text-1of5 pool (3,736
    candidates, n=1 minimal T=0.0 verifier probabilities) with the "mean" rule
    (one iteration -> that iteration's probability), exactly mirroring
    score_nof10_comparison.py at the 5-pass grain.

    Args:
        gdf_ref: Ground-truth references (EPSG:32635).
        gdf_bounds: 384 px evaluation tile boundaries (EPSG:32635).

    Returns:
        Best-op dict: ``{f1, mcc, pk, pt, cids, by_cid}``.
    """
    pool = VERIFIED / "flash-high-text-1of5"
    table = load_candidate_table(pool / "candidate_manifest.json",
                                 pool / "probabilities.json")
    by_cid = {r["cid"]: r for r in table}
    n_iters = {len(r["iter_probs"]) for r in table}
    if n_iters != {1}:
        sys.exit(f"GATE FAIL (cheap6): expected n=1 verifier probs, got iters {n_iters}")
    max_pk = max(r["vote_count"] for r in table)
    print(f"  cheap6 pool: {len(table)} candidates, proposer votes 1..{max_pk}", flush=True)

    best = {"f1": -1.0}
    for pk in range(1, max_pk + 1):
        for pt in PROB_TS:
            cids = accepted_cids(table, pk, "mean", pt)
            if not cids:
                continue
            res = _score_cids(cids, by_cid, gdf_ref, gdf_bounds)
            if res["f1"] > best["f1"]:
                best = {"f1": res["f1"], "mcc": res["mcc"], "pk": pk, "pt": pt,
                        "cids": cids, "by_cid": by_cid}
    print(f"  cheap6 best: F1@20m={best['f1']:.4f} MCC={best['mcc']:.3f} "
          f"at {best['pk']}of5, pt{best['pt']} (n={len(best['cids'])})", flush=True)
    return best


def _score_cids(cids, by_cid, gdf_ref, gdf_bounds) -> dict:
    sel = [by_cid[c] for c in sorted(cids)]
    gdf = gpd.GeoDataFrame(
        {"geometry": [Point(r["x"], r["y"]) for r in sel],
         "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
    return score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20, compute_mcc=True)


def _write_gdf(cids, by_cid, path: Path) -> None:
    sel = [by_cid[c] for c in sorted(cids)]
    gpd.GeoDataFrame(
        {"geometry": [Point(r["x"], r["y"]) for r in sel],
         "source_tile": [r["source_tile"] for r in sel]},
        crs=EVAL_CRS).to_crs("EPSG:4326").to_file(path, driver="GeoJSON")


def materialise_nof10(gdf_ref, gdf_bounds) -> tuple[Path, dict]:
    """Materialise the 10-prop + n=1 verifier best-op set (6of10, pt0.2)."""
    pool = VERIFIED / "flash-high-text-1of10"
    table = load_candidate_table(pool / "candidate_manifest.json",
                                 pool / "probabilities.json")
    by_cid = {r["cid"]: r for r in table}
    cids = accepted_cids(table, 6, "mean", 0.2)
    res = _score_cids(cids, by_cid, gdf_ref, gdf_bounds)
    gj = OUT_DIR / "nof10-6of10-n1-pt0.2.geojson"
    _write_gdf(cids, by_cid, gj)
    return gj, res


def plot_figure(ladder: list[dict], context: list[dict], pairs: list[dict]) -> Path:
    """Render the passes-vs-F1 Pareto figure with pairwise p-values."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5.5))
    xs = [c["passes"] for c in ladder]
    ys = [c["f1"] for c in ladder]
    ax.plot(xs, ys, "o-", color="#1f77b4", lw=1.5, ms=7, zorder=3,
            label="Flash ladder (gemini-3-flash proposer + verifier)")
    # Per-label annotation offsets chosen to avoid collisions (opmax sits at
    # the axes corner; min10/high10 coincide at x=10; the two Pro cells stack).
    offsets = {"opmax35": (-8, 4, "right"), "high10": (-42, -16, "center"),
               "pro6-provf": (0, 8, "center"), "pro6-flashvf": (0, -20, "center")}
    for c in ladder:
        tier = f" (T{c['tier']})" if "tier" in c else ""
        dx, dy, ha = offsets.get(c["label"], (0, 9, "center"))
        ax.annotate(f"{c['label']}{tier}\n{c['f1']:.4f}", (c["passes"], c["f1"]),
                    textcoords="offset points", xytext=(dx, dy), ha=ha, fontsize=8)
    for c in context:
        marker, colour = ("s", "#ff7f0e") if c["label"].startswith("pro") else ("o", "#888888")
        ax.scatter([c["passes"]], [c["f1"]], marker=marker, facecolors="none",
                   edgecolors=colour, s=55, zorder=3)
        dx, dy, ha = offsets.get(c["label"], (0, -20, "center"))
        ax.annotate(f"{c['label']}\n{c['f1']:.4f}", (c["passes"], c["f1"]),
                    textcoords="offset points", xytext=(dx, dy), ha=ha,
                    fontsize=7, color=colour)
    # P-value labels at the midpoint of each adjacent ladder segment.
    for p in pairs:
        a = next(c for c in ladder if c["label"] == p["a"])
        b = next(c for c in ladder if c["label"] == p["b"])
        ax.annotate(f"p={p['p_value']:.2f}",
                    ((a["passes"] + b["passes"]) / 2, (a["f1"] + b["f1"]) / 2),
                    textcoords="offset points", xytext=(4, -11), fontsize=7,
                    color="#555555", style="italic")
    ax.scatter([], [], marker="s", facecolors="none", edgecolors="#ff7f0e",
               label="Pro 3.1 proposer (context)")
    ax.scatter([], [], marker="o", facecolors="none", edgecolors="#888888",
               label="HIGH-thinking verifier (context)")
    all_f1 = [c["f1"] for c in ladder] + [c["f1"] for c in context]
    ax.set_ylim(min(all_f1) - 0.004, max(all_f1) + 0.004)
    ax.set_xlim(3.5, 38)
    ax.set_xlabel("total passes (proposer + verifier)")
    ax.set_ylabel("F1@20 m (best operating point)")
    ax.set_title("Pass budget vs F1@20 m — GS 384 px proposer-verifier "
                 "(487 tiles, curator GT)")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    out = OUT_DIR / "pareto_leaderboard.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def main() -> int:
    """Build the Pareto leaderboard: materialise, gate, test, plot, report."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)
    tile_order = sorted(gdf_bounds["tile_name"].tolist())

    print("=== cheap end (5-prop + n=1 verifier, 6 passes) ===", flush=True)
    cheap = sweep_cheap6(gdf_ref, gdf_bounds)
    cheap_gj = OUT_DIR / f"cheap6-{cheap['pk']}of5-n1-pt{cheap['pt']}.geojson"
    _write_gdf(cheap["cids"], cheap["by_cid"], cheap_gj)

    ladder = [{"label": "cheap6", "passes": 6, "split": [5, 1], "f1": cheap["f1"],
               "mcc": cheap["mcc"], "op": f"{cheap['pk']}of5 / n=1 / pt{cheap['pt']}",
               "source": "this script (new)", "geojson": str(cheap_gj.relative_to(BASE_DIR))}]

    print("\n=== ladder rungs (verification gates) ===", flush=True)
    for label, passes, split, gj, expect, op, source in LADDER_GEOJSON:
        if gj is None:
            gj, res = materialise_nof10(gdf_ref, gdf_bounds)
        else:
            gdf = gpd.read_file(gj)
            if gdf.crs is None:
                gdf = gdf.set_crs("EPSG:4326")
            res = score_detection_set(gdf.to_crs(EVAL_CRS), gdf_ref, gdf_bounds,
                                      buffer_metres=20, compute_mcc=True)
        if round(res["f1"], 4) != expect:
            sys.exit(f"GATE FAIL ({label}): F1@20m={res['f1']:.4f}, expected {expect}")
        print(f"  gate ok: {label} F1@20m={res['f1']:.4f} MCC={res['mcc']:.3f}", flush=True)
        ladder.append({"label": label, "passes": passes, "split": list(split),
                       "f1": res["f1"], "mcc": res["mcc"], "op": op, "source": source,
                       "geojson": str(Path(gj).relative_to(BASE_DIR))})

    print("\n=== round-robin tile-swap permutations (10 pairs, 10k, seed 42) ===",
          flush=True)
    per_tile = {c["label"]: consensus_per_tile(Path(c["geojson"]), gdf_ref, gdf_bounds,
                                               tile_order) for c in ladder}
    labels = [c["label"] for c in ladder]
    adjacent = set(zip(labels, labels[1:]))
    pairs = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            res = permutation_test_float(*per_tile[a], *per_tile[b],
                                         n_permutations=N_PERMUTATIONS, seed=SEED)
            pairs.append({"a": a, "b": b, "adjacent": (a, b) in adjacent, **res})
    adjusted = apply_bh_correction([p["p_value"] for p in pairs], q=0.05)
    significant = {}
    for p, adj in zip(pairs, adjusted):
        p["bh_adjusted_p"] = round(adj, 6)
        p["significant"] = bool(adj < 0.05)
        significant[frozenset({p["a"], p["b"]})] = p["significant"]
        flag = "SIG" if p["significant"] else "ns"
        kind = "adjacent" if p["adjacent"] else "span"
        print(f"  {p['a']:<11} vs {p['b']:<11} diff={p['observed_diff']:+.4f} "
              f"p={p['p_value']:.4f} bh={p['bh_adjusted_p']:.4f} [{flag}] ({kind})",
              flush=True)

    ordered = sorted(ladder, key=lambda c: c["f1"], reverse=True)
    tiers = greedy_clique_tiers([c["label"] for c in ordered], significant)
    tier_of = {ref: t for t, members in enumerate(tiers, 1) for ref in members}
    for c in ladder:
        c["tier"] = tier_of[c["label"]]
    print(f"\n  tiers: {tiers}", flush=True)

    fig_path = plot_figure(ladder, CONTEXT_ROWS, [p for p in pairs if p["adjacent"]])

    out = {"scope": "GS 384px / 487 tiles / curator GT / F1@20m, best op per rung",
           "ladder": ladder, "context": CONTEXT_ROWS, "tiers": tiers, "pairwise": pairs,
           "method": "consensus_per_tile + permutation_test_float, C(5,2)=10 round-robin, "
                     "10k tile-swap, seed 42, two-sided; BH-FDR q=0.05; greedy-clique "
                     "tiers (matrix/Era-1 board machinery)",
           "figure": str(fig_path.relative_to(BASE_DIR))}
    out_json = OUT_DIR / "pareto_leaderboard.json"
    out_json.write_text(json.dumps(out, indent=2) + "\n")

    n_sig = sum(1 for p in pairs if p["significant"])
    print(f"\n{n_sig}/10 pairs significant after BH-FDR -> {len(tiers)} tier(s).",
          flush=True)
    print(f"Wrote {out_json.relative_to(BASE_DIR)} + {fig_path.relative_to(BASE_DIR)}",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
