"""Regenerate fair-384-vs-512.json and pairwise-384px.json into a scratch
directory under PI ruling D42 (permutation p from the shared library).

Run on sapphire from the repository root (reads only; writes only to OUT):
    cd ~/Code/map-reader-llm && PYTHONHASHSEED=0 .venv/bin/python regen_384.py /tmp/regen-b/384
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import geopandas as gpd

REPO = Path.cwd()
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO))
spec = importlib.util.spec_from_file_location("cmp384", REPO / "scripts/compare-384-vs-512.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
from scripts.lib_consensus import load_shared_data  # noqa: E402

ARCH = REPO / "archive/outputs-experimental-pilot/pv"  # was outputs/pv (276e4ca80, all R100)
I4_SWEEP = "results/pv/phase1/adversarial-text-150/text-n1-t0.0-minimal/threshold_sweep.json"


def sweep512(name):
    """512 px sweep as of March; only I4's was later regenerated (01c84b841, E39)."""
    if name == "text-n1-t0.0-minimal":
        return json.loads(subprocess.check_output(["git", "-C", str(REPO), "show", f"e686e695e:{I4_SWEEP}"]))
    return json.loads((REPO / "results/pv/phase2" / name / "threshold_sweep.json").read_text())


def gdf512(name):
    """512 px PV detections at the March optimal threshold (raw, 512 tile names)."""
    sweep = sweep512(name)
    sub = "adversarial-text-150" if name == "text-n1-t0.0-minimal" else "phase2"
    probs = m.load_probs(ARCH / "results" / sub / name / "probabilities.json")
    manifest = json.loads((ARCH / "crops-150" / name / "candidate_manifest.json").read_text())
    return m.build_pv_gdf(probs, manifest, sweep["optimal"]["threshold"]), sweep["optimal"]["f1"]


gdf_ref, _ = load_shared_data(REPO / "inputs/vectors")  # March: outputs/references symlink
b384 = gpd.read_file(REPO / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson").to_crs(m.TARGET_CRS)


def effect(gdf_a, gdf_b):
    """Same call as both March producers; p now comes from the permutation test."""
    return m.bootstrap_effect_size_ci(
        gdf_det_a=gdf_a, gdf_bounds_a=b384, gdf_det_b=gdf_b, gdf_bounds_b=b384,
        gdf_ref=gdf_ref, n_iterations=1000, random_seed=42, return_p_values=True,
    )


# fair-384-vs-512.json, committed key order (I4 was appended by the one-off run-i4.py)
FAIR = [
    ("I1:loose_consensus", "text-1of10", "06-text-1of10", "Loose consensus (1-of-10): 384px vs 512px"),
    ("I2:goldilocks", "text-5of10", "09-text-5of10", "Goldilocks zone (5-of-10): 384px vs 512px"),
    ("I3:best_vs_best", "text-6of10", "09-text-5of10", "384px best (6-of-10) vs 512px best (5-of-10)"),
    ("I5:image_moderate", "image-3of5", "12-image-3of10", "Image moderate consensus: 384px vs 512px"),
    ("I6:image_baseline", "image-baseline", "17-image-t0.0", "Image baseline (N=1 T=0.0): 384px vs 512px"),
    ("I4:deterministic", "text-baseline", "text-n1-t0.0-minimal", "Deterministic baseline (N=1 T=0.0): 384px vs 512px"),
]
fair = {}
for key, c384, c512, desc in FAIR:
    g384, f1_384 = m.load_384_pv(c384)
    raw, f1_512 = gdf512(c512)
    clip = m.reassign_to_384_tiles(raw, b384)
    fair[key] = {"description": desc, "config_384": c384, "config_512": c512, "f1_384": f1_384,
                 "f1_512": f1_512, "det_384": len(g384), "det_512_raw": len(raw),
                 "det_512_clipped": len(clip), "result": effect(g384, clip)}
(OUT / "fair-384-vs-512.json").write_text(json.dumps(m.make_serialisable(fair), indent=2))

# pairwise-384px.json (inline run-fixed-analyses.py, Task 4). I1/I2 reproduce the
# March construction: raw 512 px GDF, NOT re-tiled (superseded by fair-384-vs-512).
PW = [
    ("J:J1", "text-5of10", "image-3of5", "Text vs image moderate consensus"),
    ("J:J2", "text-1of10", "image-1of5", "Text vs image loose consensus"),
    ("J:J3", "text-baseline", "image-baseline", "Text vs image single-pass"),
    ("J:J4", "text-10of10", "image-5of5", "Text vs image strict consensus"),
    ("K:K1", "text-1of10", "text-5of10", "Loose vs moderate"),
    ("K:K2", "text-5of10", "text-10of10", "Moderate vs strict"),
    ("K:K3", "text-baseline", "text-5of10", "Single-pass vs moderate consensus"),
    ("K:K4", "text-baseline", "text-1of10", "T=0.0 single vs T=0.7 single"),
    ("I:I1", "text-1of10", "512:06-text-1of10", "384px vs 512px: Single diverse pass"),
    ("I:I2", "text-5of10", "512:09-text-5of10", "384px vs 512px: Goldilocks zone"),
]
pw = {}
for key, a, b, desc in PW:
    gdf_a = m.load_384_pv(a)[0]
    gdf_b = gdf512(b[4:])[0] if b.startswith("512:") else m.load_384_pv(b)[0]
    pw[key] = {"description": desc, "result": effect(gdf_a, gdf_b), "det_a": len(gdf_a), "det_b": len(gdf_b)}
(OUT / "pairwise-384px.json").write_text(json.dumps(m.make_serialisable(pw), indent=2))
