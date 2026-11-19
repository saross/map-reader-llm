"""Measure own-sheet raster padding without scoring or changing references.

The pilot estimates aggregate local CPU time before a wider read-only audit.
Each source scan is opened once. Outside-scan pixels are excluded, and window
coverage is reported separately. Near-black fractions do not identify symbols.
Input bytes, scan bytes, and this script are hashed in the output provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import resource
import time
from collections import Counter
from pathlib import Path

# This hard ceiling protects the local workstation if the pilot underestimates.
resource.setrlimit(resource.RLIMIT_CPU, (25, 25))

import numpy as np  # noqa: E402
import rasterio  # noqa: E402

ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    """Hash unchanged input bytes in bounded memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect(values: np.ndarray, row: int, col: int) -> dict:
    """Measure actual scan pixels and separately report missing window coverage."""
    height, width = values.shape[1:]
    inside = 0 <= row < height and 0 <= col < width
    result = {"row": row, "column": col, "inside_scan": inside,
              "centre_rgb": values[:, row, col].tolist() if inside else None}
    for size in (1, 9, 31):
        radius = size // 2
        top, bottom = max(0, row - radius), min(height, row + radius + 1)
        left, right = max(0, col - radius), min(width, col + radius + 1)
        count = max(0, bottom - top) * max(0, right - left)
        fraction = None
        if count:
            fraction = float(np.all(values[:, top:bottom, left:right] <= 8, axis=0).mean())
        result[f"scan_coverage_{size}px"] = count / (size * size)
        result[f"near_black_fraction_{size}px"] = fraction
    return result


def inspect_sheet(scan: dict, features: list[dict]) -> dict:
    """Read a scan once, check its grid, and measure its assigned references."""
    started = time.process_time()
    path = Path(scan["path"])
    scan_hash = sha256(path)
    hashed = time.process_time()
    with rasterio.open(path) as src:
        if src.crs.to_epsg() != 32635 or src.transform.b or src.transform.d:
            raise ValueError(f"Unexpected scan coordinate system or rotation: {path.name}")
        if src.transform.a <= 0 or src.transform.e >= 0 or src.count < 3:
            raise ValueError(f"Unexpected scan orientation or bands: {path.name}")
        values = src.read([1, 2, 3])
        loaded = time.process_time()
        rows = []
        for feature in features:
            coordinate = feature["geometry"]["coordinates"]
            if feature["geometry"]["type"] != "Point":
                raise ValueError("Reference geometry is not a point")
            row, col = src.index(*coordinate)
            rows.append({"properties": feature["properties"], "coordinate": coordinate,
                         "measurement": inspect(values, row, col)})
        measured = time.process_time()
        return {"sheet": scan["sheet"], "path": str(path), "sha256": scan_hash,
                "bytes": path.stat().st_size, "width": src.width, "height": src.height,
                "crs": str(src.crs), "transform": list(src.transform),
                "cpu_seconds": {"hash": hashed - started, "read": loaded - hashed,
                                "measure": measured - loaded, "total": measured - started},
                "rows": rows}


def main() -> None:
    """Run a pilot or an explicitly selected bounded whole-file diagnostic."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    wall_started = time.monotonic()
    manifest = json.loads((ROOT / "input-manifest.json").read_text())
    reference = json.loads((ROOT / "reference-r2.json").read_text())
    if sha256(ROOT / "reference-r2.json") != manifest["reference_sha256"]:
        raise ValueError("Reference bytes differ from the anchored manifest")
    if reference["crs"]["properties"]["name"] != "urn:ogc:def:crs:EPSG::32635":
        raise ValueError("Unexpected reference coordinate system")
    grouped = {}
    for feature in reference["features"]:
        grouped.setdefault(feature["properties"]["source_map"], []).append(feature)
    scans = manifest["scans"][:1] if args.pilot else manifest["scans"]
    sheets = [inspect_sheet(scan, grouped[scan["sheet"]]) for scan in scans]
    counts = Counter()
    for sheet in sheets:
        for row in sheet["rows"]:
            measurement = row["measurement"]
            status = "outside_scan" if not measurement["inside_scan"] else "inside_scan"
            if (measurement["scan_coverage_9px"] == 1
                    and measurement["near_black_fraction_9px"] == 1):
                status = "entire_9px_window_near_black"
            counts[(row["properties"]["confidence_grade"], status)] += 1
    output = {"purpose": manifest["purpose"], "pilot": args.pilot,
              "method": "Containing raster pixel; RGB <= 8. Fractions use only actual scan "
                        "pixels; coverage distinguishes clipped windows. No symbol adjudication.",
              "anchors": {"script_sha256": sha256(Path(__file__)),
                          "manifest_sha256": sha256(ROOT / "input-manifest.json"),
                          "reference_commit": manifest["reference_commit"],
                          "reference_path": manifest["reference_path"],
                          "reference_sha256": manifest["reference_sha256"]},
              "sheets": sheets,
              "summary": [{"confidence_grade": key[0], "status": key[1], "count": count}
                          for key, count in sorted(counts.items())],
              "cpu_seconds": time.process_time(),
              "wall_seconds": time.monotonic() - wall_started}
    if args.pilot:
        sample = sheets[0]
        byte_ratio = sum(scan["bytes"] for scan in manifest["scans"]) / sample["bytes"]
        point_ratio = len(reference["features"]) / len(sample["rows"])
        timing = sample["cpu_seconds"]
        # Apply a safety factor: compression, grid sizes, and cache behaviour vary.
        estimate = ((timing["hash"] + timing["read"]) * byte_ratio
                    + timing["measure"] * point_ratio) * 1.5 + 2
        output["full_audit_cpu_estimate_seconds"] = estimate
        output["pilot_plus_full_cpu_estimate_seconds"] = estimate + time.process_time()
    name = "pilot-result.json" if args.pilot else "padding-diagnostic.json"
    with (ROOT / name).open("x") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")
    print(json.dumps({key: value for key, value in output.items() if key != "sheets"}))


if __name__ == "__main__":
    main()
