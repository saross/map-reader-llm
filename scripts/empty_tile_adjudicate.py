#!/usr/bin/env python3
"""
Empty-tile audit: adjudicate the reviewer's marks and estimate the double-miss floor.

Implements the mark adjudication protocol of
`planning/student-baseline-2026-08-31.md` § 5b. Every mark the reviewer
placed in the empty-tile audit (`results/empty-tile-audit/verdicts.csv`,
latest pass per tile) is classified corpus-wide by nearest neighbour at
50 m — across ALL tiles, not just the tile it was marked on — against:

(a) the canonical ground truth (GT),
(b) the deployed detection sets (the 3.7 arm-2 carried set and the
    Gemini 3 B-geometry primary set),
(c) the raw candidate unions with their verifier probabilities (the
    3.7 K=5 union under the 3.7 verifier; the Gemini 3 K=10 union under
    both the Gemini 3 and the 3.7 verifier).

Classes (first match wins, in this order):

- ``known-in-GT``          — a GT point within 50 m (the edge artefact of
                             tile-based emptiness; also detected or not).
- ``detected``             — no GT point, but a deployed detection within
                             50 m (a model find the GT lacks).
- ``proposed-but-filtered``— no GT or deployed point, but a union candidate
                             within 50 m (proposed, then killed by the
                             verifier or the operating point).
- ``true-double-miss``     — nothing within 50 m in any set.

Only ``true-double-miss`` counts toward the FN floor. The floor is
estimated on the sampled empty tiles: the 10 % tier is a complete simple
random sample (seed 42) of the 4,676 empty evaluation tiles, and the
20 % tier extends it; tiles reviewed so far are treated as the sample.
The rate carries a Clopper–Pearson 95 % interval and is scaled to the
frame; the implied count is expressed against the GT size.

Outputs (``--out-dir``, default ``results/empty-tile-audit``):

- ``adjudication.json`` — per-mark rows with the nearest point in every
  set, the class, and the floor estimate with its inputs.
- ``adjudication.md``   — the same as a report under the revision
  policy (banner + changelog).

Usage::

    python scripts/empty_tile_adjudicate.py [--out-dir DIR] [--radius-m 50]

Zero API, seconds (a few hundred marks against ~80k points).

Created: 2026-09-05 (Session 148)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import beta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

CRS = "EPSG:32635"

#: Ground-truth references. The Ruling-21 STANDARDISED reference is the
#: default from 2026-09-06 (PI, Session 148): Ruling 21 requires it for any
#: reference-tainted analysis, and the canonical r50 file carries ~150
#: phantoms Ruling 21 removed as duplicates. ``--gt canonical`` reproduces
#: the first (2026-09-05) run.
GT_FILES = {
    "standardised": "inputs/vectors/references/best-available-gt-55maps.geojson",
    "canonical": "inputs/vectors/references/canonical-gt-55maps-r50.geojson",
}

#: The reviewer's symbol for "this known (overlay) mound is a GT error".
#: Such a mark is a flag on the reference, not a mound sighting: it gets
#: its own class and never counts toward the FN floor.
GT_ERROR_SYMBOL = "Known (yellow) mound is NOT a mound — GT error"

#: Reference sets, in the protocol's order. ``kind`` drives the class. The
#: GT entry's path is filled from GT_FILES at run time.
REFERENCE_SETS = [
    ("ground-truth", "gt", None),
    ("arm2-carried-3.7", "deployed",
     "results/gemini37-55map-2026-08-31/arm2/g384_ov192_55map_g37/primary/"
     "verified_detections.geojson"),
    ("B-N5-carried-G3", "deployed",
     "results/55map-final-board-2026-08-27/cells/B-N5-carried/detections.geojson"),
    ("union-3.7-K5", "union",
     "outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/union_k5.geojson"),
    ("union-G3-K10", "union",
     "outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/union_k10.geojson"),
]

#: Verifier probability files joined to the unions by candidate index
#: (the stride chain's row-order join: candidate_NNNNN is row NNNNN).
UNION_PROBABILITIES = {
    "union-3.7-K5": {
        "3.7-vf": "outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/"
                  "verify_arm2/probabilities.json",
        "G3-vf": "outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/"
                 "verify_arm1/probabilities.json",
    },
    "union-G3-K10": {
        "G3-vf": "outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/"
                 "verify/probabilities.json",
        "3.7-vf": "outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/"
                  "verify_37/probabilities.json",
    },
}

#: Sampling frame, from results/empty-tile-audit/sample_summary.json.
SAMPLE_SUMMARY = "results/empty-tile-audit/sample_summary.json"
GT_SIZE_NOTE = "canonical GT point count read from the GT file at run time"


def latest_pass(verdicts: pd.DataFrame) -> pd.DataFrame:
    """Keep only each tile's most recent pass (re-saving supersedes)."""
    keep = verdicts.groupby("tile_name")["pass_id"].transform("max")
    return verdicts[verdicts["pass_id"] == keep].copy()


def load_points(path: Path) -> gpd.GeoDataFrame:
    """Load a point set into the working CRS, keeping its row order."""
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        raise RuntimeError(f"{path}: no CRS")
    gdf = gdf.to_crs(CRS).reset_index(drop=True)
    gdf["_row"] = np.arange(len(gdf))
    return gdf


def load_probabilities(path: Path, expected_n: int) -> dict[int, float]:
    """Verifier probabilities keyed by candidate row; gate on count and contiguity."""
    data = json.loads(path.read_text())
    results = data["results"]
    rows = sorted(int(k.split("_")[1]) for k in results)
    if len(rows) != expected_n or rows != list(range(expected_n)):
        raise RuntimeError(
            f"{path}: join gate FAILED — {len(rows)} results for a {expected_n}-row union, "
            f"contiguous={rows == list(range(len(rows)))}")
    return {int(k.split("_")[1]): float(v["mound_probability"]) for k, v in results.items()}


def nearest(tree: cKDTree, xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Nearest-neighbour distance and index for each query point."""
    dist, idx = tree.query(xy, k=1)
    return dist, idx


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact binomial interval for k successes in n trials."""
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def classify(hits: dict[str, tuple[float, str]], radius_m: float,
             symbol: str | None = None) -> str:
    """Apply the § 5b class order to a mark's nearest hits.

    Args:
        hits: set name -> (distance in metres, kind).
        radius_m: the adjudication radius.
        symbol: the reviewer's symbol; the GT-error flag short-circuits to
            its own class regardless of neighbours.

    Returns:
        One of the four protocol classes, or ``gt-error-flag``.
    """
    if symbol == GT_ERROR_SYMBOL:
        return "gt-error-flag"
    kinds_within = {kind for dist, kind in hits.values() if dist <= radius_m}
    if "gt" in kinds_within:
        return "known-in-GT"
    if "deployed" in kinds_within:
        return "detected"
    if "union" in kinds_within:
        return "proposed-but-filtered"
    return "true-double-miss"


def main() -> int:
    """Adjudicate every mark and write the report."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verdicts", default="results/empty-tile-audit/verdicts.csv")
    ap.add_argument("--manifest", default="results/empty-tile-audit/audit_manifest.csv")
    ap.add_argument("--out-dir", default="results/empty-tile-audit")
    ap.add_argument("--radius-m", type=float, default=50.0)
    ap.add_argument("--gt", choices=sorted(GT_FILES), default="standardised",
                    help="Ground-truth reference (default: standardised).")
    args = ap.parse_args()
    REFERENCE_SETS[0] = ("ground-truth", "gt", GT_FILES[args.gt])

    out_dir = PROJECT_ROOT / args.out_dir
    verdicts = latest_pass(pd.read_csv(PROJECT_ROOT / args.verdicts))
    manifest = pd.read_csv(PROJECT_ROOT / args.manifest)
    reviewed = verdicts.drop_duplicates("tile_name")
    marks = verdicts.dropna(subset=["x_world", "y_world"]).copy()
    logger.info("reviewed tiles %d (of %d in manifest); marks %d",
                len(reviewed), len(manifest), len(marks))

    # ---- Reference sets and their trees ----
    sets: dict[str, dict] = {}
    for name, kind, rel in REFERENCE_SETS:
        gdf = load_points(PROJECT_ROOT / rel)
        xy = np.column_stack([gdf.geometry.x.values, gdf.geometry.y.values])
        sets[name] = {"kind": kind, "gdf": gdf, "tree": cKDTree(xy), "path": rel}
        logger.info("%s: %d points", name, len(gdf))
    probs: dict[str, dict[str, dict[int, float]]] = {}
    for uname, files in UNION_PROBABILITIES.items():
        probs[uname] = {}
        for vf, rel in files.items():
            probs[uname][vf] = load_probabilities(PROJECT_ROOT / rel, len(sets[uname]["gdf"]))
            logger.info("%s / %s: join gate OK", uname, vf)

    # ---- Per-mark adjudication ----
    mxy = np.column_stack([marks["x_world"].values, marks["y_world"].values])
    rows = []
    for i, (_, m) in enumerate(marks.iterrows()):
        hits: dict[str, tuple[float, str]] = {}
        detail: dict[str, dict] = {}
        for name, s in sets.items():
            dist, idx = s["tree"].query(mxy[i], k=1)
            hits[name] = (float(dist), s["kind"])
            entry: dict = {"distance_m": round(float(dist), 1)}
            g = s["gdf"].iloc[int(idx)]
            if "vote_count" in g:
                entry["vote_count"] = int(g["vote_count"])
            if name in probs:
                for vf, table in probs[name].items():
                    entry[f"prob_{vf}"] = round(table[int(idx)], 3)
            if "gt_id" in g:
                entry["gt_id"] = str(g["gt_id"])
            detail[name] = entry
        cls = classify(hits, args.radius_m, m.get("symbol"))
        rows.append({
            "order_index": int(m["order_index"]), "tile_name": m["tile_name"],
            "map_name": m["map_name"], "tier": m["tier"], "symbol": m.get("symbol"),
            "x_world": round(float(m["x_world"]), 1), "y_world": round(float(m["y_world"]), 1),
            "class": cls, "nearest": detail,
            "nearest_anything_m": round(min(d for d, _ in hits.values()), 1),
        })
        logger.info("mark %s (%s): %s — nearest %s m", m["tile_name"], m["tier"], cls,
                    rows[-1]["nearest_anything_m"])

    # ---- Floor estimate ----
    summary = json.loads((PROJECT_ROOT / SAMPLE_SUMMARY).read_text())
    n_frame = int(summary["n_empty"])
    n_gt = len(sets["ground-truth"]["gdf"])
    classes = pd.Series([r["class"] for r in rows]).value_counts().to_dict()

    def floor(tiles: pd.DataFrame, label: str) -> dict:
        names = set(tiles["tile_name"])
        k = sum(1 for r in rows if r["class"] == "true-double-miss" and r["tile_name"] in names)
        n = len(names)
        lo, hi = clopper_pearson(k, n)
        rate = k / n if n else float("nan")
        return {
            "stratum": label, "tiles_reviewed": n, "true_double_misses": k,
            "rate_per_tile": rate, "ci95": [lo, hi],
            "implied_missed_in_frame": rate * n_frame,
            "implied_missed_ci95": [lo * n_frame, hi * n_frame],
            "implied_share_of_gt": rate * n_frame / n_gt,
            "implied_share_of_gt_ci95": [lo * n_frame / n_gt, hi * n_frame / n_gt],
        }

    estimates = [floor(reviewed, "all reviewed tiles"),
                 floor(reviewed[reviewed["tier"] == "10pct"], "10 % tier only (complete SRS)")]

    # Revision trail: carry forward the previous run's changelog so the
    # regenerated report keeps its history (results revision policy).
    prior_path = out_dir / "adjudication.json"
    history: list[dict] = []
    if prior_path.exists():
        prior = json.loads(prior_path.read_text())
        history = list(prior.get("history", []))
        history.append({"generated": prior.get("generated"),
                        "reference": prior.get("reference", "canonical"),
                        "reviewed_tiles": prior.get("reviewed_tiles"),
                        "classes": prior.get("classes")})

    payload = {
        "generated": date.today().isoformat(),
        "reference": args.gt,
        "reference_path": GT_FILES[args.gt],
        "history": history,
        "protocol": "planning/student-baseline-2026-08-31.md § 5b",
        "radius_m": args.radius_m,
        "reviewed_tiles": int(len(reviewed)),
        "reviewed_by_tier": reviewed["tier"].value_counts().to_dict(),
        "marks": int(len(marks)),
        "classes": classes,
        "frame_empty_tiles": n_frame,
        "gt_points": n_gt,
        "reference_sets": {n: {"kind": s["kind"], "n": int(len(s["gdf"])), "path": s["path"]}
                           for n, s in sets.items()},
        "estimates": estimates,
        "per_mark": rows,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "adjudication.json").write_text(json.dumps(payload, indent=2, default=float) + "\n")
    (out_dir / "adjudication.md").write_text(render_md(payload))
    logger.info("ADJUDICATION COMPLETE -> %s", (out_dir / "adjudication.md").relative_to(PROJECT_ROOT))
    return 0


def render_md(p: dict) -> str:
    """Render the report under the results revision policy."""
    today = p["generated"]
    lines = [
        "# Empty-tile audit — mark adjudication and double-miss floor",
        "",
        f"> **Last revised**: {today} (generated by `scripts/empty_tile_adjudicate.py`; "
        "regenerate rather than edit). See [§ Changelog](#changelog) for revision history.",
        "",
        f"Protocol: `{p['protocol']}` — nearest neighbour at {p['radius_m']:.0f} m, "
        f"corpus-wide, against the **{p['reference']}** ground truth "
        f"(`{p['reference_path']}`), the deployed sets, and the raw unions.",
        "",
        "## Coverage",
        "",
        f"- Tiles reviewed: **{p['reviewed_tiles']}** of a {p['frame_empty_tiles']}-tile empty "
        f"frame (by tier: {p['reviewed_by_tier']}).",
        f"- Marks placed: **{p['marks']}**. Classes: {p['classes']}.",
        f"- GT points: {p['gt_points']}.",
        "",
        "## Double-miss floor",
        "",
        "| Stratum | Tiles | True double-misses | Rate / tile (95 % CI) | Implied missed mounds "
        "in frame (95 % CI) | Share of GT (95 % CI) |",
        "|---|---:|---:|---|---|---|",
    ]
    for e in p["estimates"]:
        lo, hi = e["ci95"]
        mlo, mhi = e["implied_missed_ci95"]
        slo, shi = e["implied_share_of_gt_ci95"]
        lines.append(
            f"| {e['stratum']} | {e['tiles_reviewed']} | {e['true_double_misses']} | "
            f"{e['rate_per_tile']:.4f} ({lo:.4f}–{hi:.4f}) | "
            f"{e['implied_missed_in_frame']:.1f} ({mlo:.1f}–{mhi:.1f}) | "
            f"{100 * e['implied_share_of_gt']:.2f} % ({100 * slo:.2f}–{100 * shi:.2f} %) |")
    lines += ["", "## Per-mark adjudication", "",
              "| Tile | Tier | Class | Nearest anything (m) | GT (m) | arm-2 3.7 (m) | "
              "B-primary G3 (m) | 3.7 K=5 union (m; votes; p3.7/pG3) | "
              "G3 K=10 union (m; votes; pG3/p3.7) |",
              "|---|---|---|---:|---:|---:|---:|---|---|"]
    for r in p["per_mark"]:
        n = r["nearest"]
        u5, u10 = n["union-3.7-K5"], n["union-G3-K10"]
        lines.append(
            f"| `{r['tile_name']}` | {r['tier']} | **{r['class']}** | {r['nearest_anything_m']} | "
            f"{n['ground-truth']['distance_m']} | {n['arm2-carried-3.7']['distance_m']} | "
            f"{n['B-N5-carried-G3']['distance_m']} | "
            f"{u5['distance_m']}; {u5.get('vote_count', '—')}; "
            f"{u5.get('prob_3.7-vf', '—')}/{u5.get('prob_G3-vf', '—')} | "
            f"{u10['distance_m']}; {u10.get('vote_count', '—')}; "
            f"{u10.get('prob_G3-vf', '—')}/{u10.get('prob_3.7-vf', '—')} |")
    lines += ["", "## Reference sets", ""]
    for name, s in p["reference_sets"].items():
        lines.append(f"- `{name}` ({s['kind']}, {s['n']} points): `{s['path']}`")
    lines += ["", "## Changelog", ""]
    if p["history"]:
        lines += [f"### {today} — Regenerated against the {p['reference']} reference", "",
                  f"Classes now {p['classes']} over {p['reviewed_tiles']} tiles. Previous runs, "
                  "newest first:", ""]
        for h in reversed(p["history"]):
            lines.append(f"- {h['generated']}: reference `{h['reference']}`, "
                         f"{h['reviewed_tiles']} tiles, classes {h['classes']}.")
        lines.append("")
    first = p["history"][0]["generated"] if p["history"] else today
    lines += [f"### {first} — Original publication", "",
              "Generated at the close of the PI's manual review pass (the full 10 % tier plus "
              "the first tiles of the 20 % tier) against the canonical r50 reference. The "
              "union-to-probability joins passed the count-and-contiguity gate.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
