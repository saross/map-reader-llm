"""Probe: pass dates from metas, and the CRS of each family's pass files (read-only)."""
import glob
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sets = json.load(open(REPO / "reports/retest-bootstrap-check-2026-10-05-scripts/replicate_sets.json"))


def meta_dates(run_dir):
    ds = {}
    for m in glob.glob(str(REPO / run_dir / "*.meta.json")) + glob.glob(str(REPO / run_dir / "run.meta.json")):
        try:
            j = json.load(open(m))
        except Exception:
            continue
        s = json.dumps(j)[:40000]
        for d in re.findall(r"(2026-\d{2}-\d{2})T\d{2}", s)[:4]:
            ds[d] = ds.get(d, 0) + 1
    return ds


for g, members in sets.items():
    for m in members:
        agg = {}
        for p in m["passes"]:
            for d, n in meta_dates(p["run_dir"]).items():
                agg[d] = agg.get(d, 0) + n
        print(f"g{g:>2} {m['run_id']}::{m['arm']:42s} {dict(sorted(agg.items()))}")

print("--- first coordinate of one pass file per family ---")
for p in ["outputs/stride-55map-2026-08-25/g384_ov192_55map/run_1/",
          "outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/run_1/",
          "outputs/gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img/run_1/",
          "outputs/gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img/run_1/",
          "outputs/55maps-text-min-n10-uplift/proposer/run_6/",
          "outputs/55maps-text-high-generalisation/proposer/detect_brief-text/run_1/",
          "outputs/h11/pv-diag-384/text-n10/text-t0.7/run_1/"]:
    fs = sorted(glob.glob(str(REPO / p / "detections-*.geojson")))
    if not fs:
        print(p, "NO FILE", sorted(glob.glob(str(REPO / p / "*")))[:5])
        continue
    d = json.load(open(fs[0]))
    f = d["features"][0]
    print(p, "crs:", (d.get("crs") or {}).get("properties"), "coord:",
          f["geometry"]["coordinates"] if f["geometry"]["type"] == "Point" else str(f["geometry"]["coordinates"])[:60],
          "| props:", list(f["properties"].keys())[:8])
