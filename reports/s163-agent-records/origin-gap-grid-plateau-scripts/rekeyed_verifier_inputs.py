"""Which verifier inputs did the legacy re-key send to the wrong sheet's raster?

For every committed verified union in the grid, stride, winner-ladder, and
Image-B chains: rebuild the members (``lib_cluster_origins``), find the rows
whose stored ``source_tile`` lies on a sheet the cluster was never seen on,
and report their verifier probabilities, vote counts, distance to the nearest
curator mound, and (where the crop PNGs exist in the read-only shared
checkout) the share of black no-data pixels in their crops, against the same
statistics for every other row. Then an OPTIMISTIC bound: the cell's best
point re-scored as if every re-keyed candidate had been verified a mound
(probability 1.0). Read-only; no model call.

Usage: python rekeyed_verifier_inputs.py <copy_root> <crops_root> <out_json>
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from PIL import Image

root = Path(sys.argv[1]).resolve()
crops_root = Path(sys.argv[2]).resolve()
out_path = Path(sys.argv[3])
sys.path[:0] = [str(root), str(root / "scripts")]

from scripts import stride_verifier_analysis as svs  # noqa: E402
from scripts.grid_analysis import CRS, load_cell_passes, score  # noqa: E402
from scripts.grid_verifier_analysis import verified_subset  # noqa: E402
from scripts.image_b_analysis import load_image_union  # noqa: E402
from scripts.lib_cluster_origins import attach_union_origins, rekey_on_origin  # noqa: E402

bounds = gpd.read_file(svs.COMMON_BOUNDS)
ref = gpd.read_file(svs.GROUND_TRUTH).to_crs(CRS)

#: (label, outputs root, cell, union file, verify dir, crops dir, passes)
GRID = "outputs/grid-2026-08-18"
PB = "outputs/stride-phaseb-2026-08-25"
PC = "outputs/stride-phasec-2026-08-25"
IB = "outputs/image-b-gs-2026-08-28"
K10 = "union_k10.geojson"
UNIONS = [
    ("grid/g512_ov064", GRID, "g512_ov064", K10, "verify", "crops", 10),
    ("grid/g512_ov256", GRID, "g512_ov256", K10, "verify", "crops", 10),
    ("grid/g384_ov048", GRID, "g384_ov048", K10, "verify", "crops", 10),
    ("grid/g384_ov192", GRID, "g384_ov192", K10, "verify", "crops", 10),
    ("stride/g512_ov176", PB, "g512_ov176", K10, "verify", "crops", 10),
    ("stride/g384_ov128", PB, "g384_ov128", K10, "verify", "crops", 10),
    ("stride/g256_ov064", PB, "g256_ov064", K10, "verify", "crops", 10),
    ("stride/g512_ov320", PB, "g512_ov320", K10, "verify", "crops", 10),
    ("stride/g384_ov240", PC, "g384_ov240", K10, "verify", "crops", 10),
    ("winner/N1", PB, "g384_ov128", "union_k1.geojson", "verify_k1", "crops_k1", 1),
    ("winner/N3", PB, "g384_ov128", "union_k3.geojson", "verify_k3", "crops_k3", 3),
    ("winner/N5", PB, "g384_ov128", "union_k5.geojson", "verify_k5", "crops_k5", 5),
    ("imageb/min", IB, "g384_ov192_image", K10, "verify", "crops", 10),
    ("imageb/high", IB, "g384_ov192_image_high", K10, "verify", "crops", 10),
]


def dark_share(png: Path) -> float | None:
    """Share of pure-black pixels (the rasters' no-data) in one crop."""
    if not png.exists():
        return None
    arr = np.asarray(Image.open(png).convert("RGB"))
    return float((arr.max(axis=2) == 0).mean())


def best_point(label: str) -> tuple[float, int] | None:
    """The committed best (prob_t, min_votes) for the cell, where one exists."""
    kind, cell = label.split("/")
    if kind == "grid":
        b = json.loads((root / "results/grid-2026-08-18/verifier_analysis.json").read_text())
        b = b["board_best"][cell]
    elif kind == "stride":
        b = json.loads(
            (root / "results/stride-2026-08-25/stride_verifier_analysis.json").read_text()
        )["boards"][cell]
    elif kind == "winner":
        n = cell[1:]
        b = json.loads((root / "results/stride-2026-08-25/plateau_analyses.json").read_text())
        b = b["winner_ladder_exact"]["N"][n]["best"]
    else:
        rel = (
            "results/image-b-gs-2026-08-28/analysis.json"
            if cell == "min"
            else "results/image-b-gs-2026-08-28/high/analysis.json"
        )
        b = json.loads((root / rel).read_text())["image_best"]
    return float(b["prob_t"]), int(b["min_votes"])


result = {}
for label, base, cell, union_name, verify_dir, crops_dir, n in UNIONS:
    vroot = root / base / "verifier" / cell
    union = load_image_union(vroot, union_name, verify_dir)
    union = svs.reassign_gate(union, bounds, cell)
    passes = load_cell_passes(root / base / "scoring", cell, n_passes=n)
    att = attach_union_origins(union, passes, bounds, label=label)
    fixed, _ = rekey_on_origin(att, bounds)
    moved = fixed.index[
        fixed["source_tile"].to_numpy() != att.loc[fixed.index, "source_tile"].to_numpy()
    ]
    others = att.index.difference(moved)
    manifest = json.loads((vroot / crops_dir / "candidate_manifest.json").read_text())
    cands = manifest["candidates"]
    assert all(cands[i]["candidate_id"] == i for i in range(len(cands)))
    assert all(cands[i]["source_tile"] == att.loc[i, "source_tile"] for i in moved)
    crop_dir = crops_root / base / "verifier" / cell / crops_dir
    dark_moved = [dark_share(crop_dir / cands[i]["crop_file"]) for i in moved]
    rng = np.random.default_rng(42)
    sample = rng.choice(np.asarray(others), size=min(200, len(others)), replace=False)
    dark_other = [dark_share(crop_dir / cands[int(i)]["crop_file"]) for i in sample]
    dist = [float(ref.distance(g).min()) for g in att.loc[moved].geometry]
    entry = {
        "n_rows": int(len(att)),
        "n_rekeyed": int(len(moved)),
        "rekeyed_ids": [int(i) for i in moved],
        "rekeyed_max_prob": float(att.loc[moved, "mound_probability"].max())
        if len(moved)
        else None,
        "rekeyed_n_prob_ge_0p15": int((att.loc[moved, "mound_probability"] >= 0.15).sum()),
        "rekeyed_votes": sorted(int(v) for v in att.loc[moved, "vote_count"]),
        "rekeyed_n_within_20m_of_a_mound": int(sum(d <= 20 for d in dist)),
        "others_share_prob_ge_0p15": float((att.loc[others, "mound_probability"] >= 0.15).mean()),
        "crop_dark_share_rekeyed_median": (
            float(np.median([d for d in dark_moved if d is not None]))
            if any(d is not None for d in dark_moved)
            else None
        ),
        "crop_dark_share_rekeyed_min": (
            float(min(d for d in dark_moved if d is not None))
            if any(d is not None for d in dark_moved)
            else None
        ),
        "crop_dark_share_others_sample_median": (
            float(np.median([d for d in dark_other if d is not None]))
            if any(d is not None for d in dark_other)
            else None
        ),
        "crops_found": int(sum(d is not None for d in dark_moved)),
    }
    point = best_point(label)
    if point is not None and len(moved):
        prob_t, k = point
        now = score(verified_subset(fixed, prob_t, k), ref, bounds)
        bound = fixed.copy()
        bound.loc[bound.index.isin(moved), "mound_probability"] = 1.0
        hi = score(verified_subset(bound, prob_t, k), ref, bounds)
        entry["optimistic_bound_at_best_point"] = {
            "prob_t": prob_t,
            "min_votes": k,
            "f1_fixed": now["f1"],
            "f1_if_rekeyed_verified_mounds": hi["f1"],
            "delta": hi["f1"] - now["f1"],
            "n_added": int(hi["n_detections"] - now["n_detections"]),
        }
    result[label] = entry
    print(label, {k: v for k, v in entry.items() if k != "rekeyed_ids"})

out_path.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
