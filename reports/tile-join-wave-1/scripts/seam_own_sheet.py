#!/usr/bin/env python3
"""
Own-sheet check of every non-padding seam contact (tile-join Wave 1, § 2.4).

The Wave 1 sheet check (``sheet_check_55map.py``; ``dry-run.md`` §§ 2–2.2)
measured each cross-sheet contact on the **other** sheet's tile only: a
reference recorded on sheet A (``source_map``) lies inside a tile of sheet
B, on B's map content (or ambiguously so). Astra's paired views showed, for
five r2 references, that the point lies in black padding on its **own**
sheet A. The PI must tell three cases apart:

1. separate printed instances on both sheets;
2. a sheet label inconsistent with the image (own sheet = padding there);
3. displaced counterparts needing sheet-specific centres (own sheet has
   the symbol nearby, but not at the point).

For every map-content and ambiguous contact in all five tracked 55-map
reference files, this script measures the point on its own sheet: every
own-sheet tile whose footprint contains the point, with that tile's own PNG
and ``.pgw``, using the sheet check's pixel functions and thresholds
unchanged. It then keeps three **distinct** fields per contact:

- ``own_verdict``: padding, ambiguous, map-content, or ``outside`` (no
  own-sheet tile contains the point);
- ``recipient_verdict``: the sheet check's verdict on the other sheet's
  tile, re-measured here and checked against the committed summary;
- ``*_hint``: a symbol-proximity hint on both sheets (distance to the
  nearest dark compact blob). It is a **hint**, not an adjudication: the
  pixel test finds dark compact marks, not mound symbols.

and a derived ``candidate_class``:

- ``2-candidate``: own = padding or outside, recipient = map-content;
- ``1/3-candidate``: own = map-content and recipient = map-content;
- ``other``: anything else, with a reason (ambiguous is never merged into
  map-content).

Where the lineage can be read cheaply from tracked files, the point's
**original** coordinate (before standardisation or centre marking) is also
measured on its own sheet: r2 and the best-available file via the
standardised student file's ``std_source_index`` into the reviewed student
file; canonical r50 via its ``student:<n>`` number into the reviewed file,
accepted only where the reviewed feature's ``uuid`` equals r50's
``source_id_lossy`` and the sheets agree. The two student files are the
inputs themselves (original = final). Optionally (``--astra``), Astra's
independent diagnostic on the full-sheet scans is compared per pair.

Nothing is imported from the scorer; no model output is read.

Usage (zbook, reference environment, from a checkout of the branch; tiles
are gitignored and read from the main checkout)::

    ~/Code/map-reader-llm/.venv/bin/python \\
        reports/tile-join-wave-1/scripts/seam_own_sheet.py \\
        --tile-dir ~/Code/map-reader-llm/inputs/tiles_384_55maps \\
        --astra ~/scratch/wave1/seam2/astra/source-padding-diagnostic.json \\
        --json-out reports/tile-join-wave-1/scripts/out/seam_own_sheet.json \\
        > reports/tile-join-wave-1/scripts/out/seam_own_sheet.txt

Created: 2026-11-19 (tile-join Wave 1, seam follow-up, amd-tower / zbook)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from seam_second_copy import SUMMARY, TileIndex, load_refs_full  # noqa: E402
from sheet_check_55map import (  # noqa: E402
    BOUNDS,
    NEAR_BLACK_MAX,
    PROJECT_ROOT,
    REFERENCE_FILES,
    classify,
    load_tiles,
    measure_pixels,
    pixel_position,
)

STANDARDISED = (PROJECT_ROOT / "results/deployment-oracle-2026-06-06/canonical-gt"
                "/standardised/student-mounds-55maps-standardised.geojson")
REVIEWED = PROJECT_ROOT / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
R2 = "inputs/vectors/references/best-available-gt-55maps-r2.geojson"
R50 = "inputs/vectors/references/canonical-gt-55maps-r50.geojson"
#: Lineage route per reference file (see the module docstring).
LINEAGE = {
    R2: "standardised",
    "inputs/vectors/references/best-available-gt-55maps.geojson": "standardised",
    R50: "reviewed-by-number",
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson": "self",
    "inputs/vectors/references/student-mounds-55maps.geojson": "self",
}
#: Hint: a pixel is "dark ink" if its luminance is at or below this value
#: and it is not near-black padding (which is excluded by component size).
INK_LUMA_MAX = 110.0
#: Hint: a dark connected component counts as a "compact blob" if its area
#: and bounding box fall within these limits (in pixels).
BLOB_AREA = (6, 600)
BLOB_SIDE_MAX = 40
#: Hint: search radius around the point, in pixels.
HINT_RADIUS_PX = 48
#: Hint: radius of the "near-symbol fraction" disc, in pixels.
NEAR_RADIUS_PX = 8
#: Verdict priority when one point is measured in several tiles.
PRIORITY = ("map-content", "ambiguous", "padding")
COORD_TOL_M = 0.01


def combine(verdicts: list[str]) -> str:
    """Combine per-tile verdicts for one point into one verdict.

    Args:
        verdicts: Verdicts from :func:`sheet_check_55map.classify`, one per
            own-sheet tile containing the point.

    Returns:
        ``outside`` if the list is empty; else the highest-priority verdict
        (map-content, then ambiguous, then padding).
    """
    if not verdicts:
        return "outside"
    return next(v for v in PRIORITY if v in verdicts)


def symbol_hint(png: Path, col: float, row: float, metres_per_px: float
                ) -> dict[str, Any]:
    """Distance from a point to the nearest dark compact blob in a tile.

    A cheap hint, not an adjudication. Dark ink is luminance at or below
    ``INK_LUMA_MAX``; connected components (8-connectivity) of dark ink
    whose area and bounding box are small count as compact blobs, so large
    padding areas and long lines are excluded.

    Args:
        png: Tile image.
        col: Point's column.
        row: Point's row.
        metres_per_px: Ground size of one pixel (from the world file).

    Returns:
        The distance in pixels and metres to the nearest blob pixel within
        ``HINT_RADIUS_PX`` (None if none), that blob's area and mean RGB,
        and the fraction of blob pixels within ``NEAR_RADIUS_PX``.
    """
    import numpy as np  # noqa: PLC0415
    from PIL import Image  # noqa: PLC0415
    from scipy import ndimage  # noqa: PLC0415

    with Image.open(png) as image:
        rgb = np.asarray(image.convert("RGB")).astype(float)
    luma = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    labels, n = ndimage.label(luma <= INK_LUMA_MAX, structure=np.ones((3, 3)))
    if n == 0:
        return {"nearest_blob_px": None, "nearest_blob_m": None,
                "near_symbol_fraction": 0.0}
    areas = ndimage.sum_labels(np.ones_like(luma), labels, range(1, n + 1))
    slices = ndimage.find_objects(labels)
    compact = np.zeros(n + 1, dtype=bool)
    for k, (area, sl) in enumerate(zip(areas, slices), start=1):
        side = max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start)
        compact[k] = BLOB_AREA[0] <= area <= BLOB_AREA[1] and side <= BLOB_SIDE_MAX
    blob = compact[labels]
    rows, cols = np.indices(luma.shape)
    dist = np.hypot(cols + 0.5 - col, rows + 0.5 - row)
    near = dist <= NEAR_RADIUS_PX
    frac = float(blob[near].mean()) if near.any() else 0.0
    cand = blob & (dist <= HINT_RADIUS_PX)
    if not cand.any():
        return {"nearest_blob_px": None, "nearest_blob_m": None,
                "near_symbol_fraction": round(frac, 4)}
    flat = np.where(cand, dist, np.inf)
    r, c = np.unravel_index(int(np.argmin(flat)), flat.shape)
    k = labels[r, c]
    member = labels == k
    return {
        "nearest_blob_px": round(float(dist[r, c]), 1),
        "nearest_blob_m": round(float(dist[r, c]) * metres_per_px, 1),
        "nearest_blob_area_px": int(member.sum()),
        "nearest_blob_mean_rgb": [int(v) for v in rgb[member].mean(axis=0)],
        "near_symbol_fraction": round(frac, 4),
    }


def metres_per_pixel(tile_dir: Path, tile: dict[str, Any]) -> float:
    """Pixel size in metres, from the tile's world file (``a`` term).

    Args:
        tile_dir: Directory holding ``<sheet>/<stem>.pgw``.
        tile: Tile record.

    Returns:
        Absolute x pixel size.
    """
    stem = tile["name"].removesuffix(".png")
    return abs(float((tile_dir / tile["sheet"] / f"{stem}.pgw").read_text().split()[0]))


def measure_on_sheet(index: TileIndex, tile_dir: Path, sheet: str, x: float,
                     y: float, hint: bool) -> dict[str, Any]:
    """Measure a point on every tile of one sheet whose footprint holds it.

    Args:
        index: Tile index of the frame.
        tile_dir: Root of the tile images.
        sheet: The sheet whose tiles are measured.
        x: Easting.
        y: Northing.
        hint: Whether to compute the symbol-proximity hint.

    Returns:
        The combined verdict, whether the tiles disagree, the per-tile
        measurements, and (if asked) the hint from the tile where the
        nearest blob is closest.
    """
    per_tile = []
    for i in index.containing(x, y):
        tile = index.tiles[i]
        if tile["sheet"] != sheet:
            continue
        pos = pixel_position(tile_dir, tile, x, y)
        if pos is None:
            per_tile.append({"tile": tile["name"], "verdict": None,
                             "note": "world file missing"})
            continue
        stem = tile["name"].removesuffix(".png")
        png = tile_dir / tile["sheet"] / f"{stem}.png"
        m = measure_pixels(png, pos[0], pos[1], None)
        rec: dict[str, Any] = {
            "tile": tile["name"], "col": round(pos[0], 1), "row": round(pos[1], 1),
            "verdict": classify(m),
            "window_near_black_fraction": m["window_near_black_fraction"],
            "rgb_at_point": m["rgb_at_point"],
        }
        if hint:
            rec["hint"] = symbol_hint(png, pos[0], pos[1],
                                      metres_per_pixel(tile_dir, tile))
        per_tile.append(rec)
    verdicts = [t["verdict"] for t in per_tile if t["verdict"]]
    out: dict[str, Any] = {
        "verdict": combine(verdicts),
        "tiles_disagree": len(set(verdicts)) > 1,
        "n_tiles": len(per_tile),
        "tiles": per_tile,
    }
    hints = [t["hint"] for t in per_tile if t.get("hint")]
    if hints:
        with_blob = [h for h in hints if h["nearest_blob_px"] is not None]
        out["hint"] = (min(with_blob, key=lambda h: h["nearest_blob_px"])
                       if with_blob else hints[0])
    return out


def candidate_class(own: str, recipient: str) -> tuple[str, str]:
    """Classify one contact (or pair) from its own and recipient verdicts.

    Args:
        own: Own-sheet verdict (including ``outside``).
        recipient: Recipient-sheet verdict.

    Returns:
        (class, reason).
    """
    if recipient == "map-content" and own in ("padding", "outside"):
        return "2-candidate", f"own {own}, recipient map-content"
    if recipient == "map-content" and own == "map-content":
        return "1/3-candidate", "map content on both sheets"
    return "other", f"own {own}, recipient {recipient}"


def load_original_coordinates(ref_name: str, refs: list[dict[str, Any]]
                              ) -> dict[str, dict[str, Any]]:
    """The pre-standardisation coordinate of each traceable reference.

    Args:
        ref_name: Reference file (repository-relative).
        refs: Records from :func:`seam_second_copy.load_refs_full`, with
            the file's raw properties under ``props``.

    Returns:
        Feature key -> {status, x, y, sheet, ...}. ``status`` is
        ``traced``, ``self`` (the file is the input), ``not-student``, or
        ``mismatch`` (the lineage check failed; no coordinate given).
    """
    route = LINEAGE[ref_name]
    reviewed = json.loads(REVIEWED.read_text())["features"]
    standardised = (json.loads(STANDARDISED.read_text())["features"]
                    if route == "standardised" else [])
    out: dict[str, dict[str, Any]] = {}
    for ref in refs:
        if route == "self":
            out[ref["key"]] = {"status": "self", "x": ref["x"], "y": ref["y"],
                               "sheet": ref["sheet"]}
            continue
        if not ref["id"].startswith("student:"):
            out[ref["key"]] = {"status": "not-student"}
            continue
        n = int(ref["id"].split(":")[1])
        if route == "standardised":
            if n >= len(standardised):
                out[ref["key"]] = {"status": "mismatch", "why": "index out of range"}
                continue
            std = standardised[n]
            sx, sy = std["geometry"]["coordinates"][:2]
            ok = (math.hypot(sx - ref["x"], sy - ref["y"]) <= COORD_TOL_M
                  and std["properties"]["source_map"] == ref["sheet"]
                  and std["properties"]["uuid"] == ref["props"].get("source_id_lossy"))
            src_i = std["properties"].get("std_source_index")
            if not ok or src_i is None:
                out[ref["key"]] = {"status": "mismatch",
                                   "why": "standardised feature does not match"}
                continue
            src = reviewed[src_i]
            ok = src["properties"]["uuid"] == std["properties"]["uuid"]
            position_source = std["properties"].get("std_position_source")
        else:
            if n >= len(reviewed):
                out[ref["key"]] = {"status": "mismatch", "why": "index out of range"}
                continue
            src_i, src = n, reviewed[n]
            ok = (src["properties"]["uuid"] == ref["props"].get("source_id_lossy")
                  and src["properties"]["source_map"] == ref["sheet"])
            position_source = ref["props"].get("position_source")
        if not ok:
            out[ref["key"]] = {"status": "mismatch",
                               "why": "reviewed feature does not match"}
            continue
        ox, oy = src["geometry"]["coordinates"][:2]
        out[ref["key"]] = {
            "status": "traced", "x": float(ox), "y": float(oy),
            "sheet": src["properties"]["source_map"], "reviewed_index": src_i,
            "position_source": position_source,
            "moved_m": round(math.hypot(ox - ref["x"], oy - ref["y"]), 1),
        }
    return out


def sha256(path: Path) -> str:
    """Hex SHA-256 of a file.

    Args:
        path: File to hash.

    Returns:
        The digest.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    """Measure, classify, summarise, and print every in-scope contact."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tile-dir", type=Path,
                        default=PROJECT_ROOT / "inputs/tiles_384_55maps")
    parser.add_argument("--astra", type=Path, default=None,
                        help="Astra's source-padding-diagnostic.json, for comparison")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    tiles = load_tiles(BOUNDS)
    index = TileIndex(tiles)
    tile_by_name = {t["name"]: t for t in tiles}
    summary = json.loads(SUMMARY.read_text())
    report: dict[str, Any] = {
        "frame": str(BOUNDS.relative_to(PROJECT_ROOT)),
        "summary_input": str(SUMMARY.relative_to(PROJECT_ROOT)),
        "summary_sha256": sha256(SUMMARY),
        "thresholds": {"near_black_max": NEAR_BLACK_MAX,
                       "verdict_rule": "sheet_check_55map.classify, unchanged",
                       "hint_ink_luma_max": INK_LUMA_MAX, "hint_blob_area": BLOB_AREA,
                       "hint_blob_side_max": BLOB_SIDE_MAX,
                       "hint_radius_px": HINT_RADIUS_PX,
                       "near_radius_px": NEAR_RADIUS_PX},
        "references": {},
    }
    print(f"frame {report['frame']}; contacts from {report['summary_input']} "
          f"(sha256 {report['summary_sha256'][:12]})")

    for ref_name in REFERENCE_FILES:
        raw = json.loads((PROJECT_ROOT / ref_name).read_text())["features"]
        refs = load_refs_full(PROJECT_ROOT / ref_name)
        for ref in refs:
            ref["props"] = raw[int(ref["key"].split(".")[0])]["properties"]
        by_pos = {(r["sheet"], r["x"], r["y"]): r for r in refs}
        originals = load_original_coordinates(ref_name, refs)
        contacts = summary["references"][ref_name]["non_padding_contacts"]
        print(f"\n=== {ref_name}: {len(contacts)} non-padding contacts")
        records = []
        for c in contacts:
            ref = by_pos.get((c["ref_sheet"], c["x"], c["y"]))
            if ref is None:  # Fall back to the nearest same-sheet point.
                ref = min((r for r in refs if r["sheet"] == c["ref_sheet"]),
                          key=lambda r: math.hypot(r["x"] - c["x"], r["y"] - c["y"]))
                if math.hypot(ref["x"] - c["x"], ref["y"] - c["y"]) > COORD_TOL_M:
                    raise SystemExit(f"cannot key contact {c['ref_id']} in {ref_name}")
            own = measure_on_sheet(index, args.tile_dir, c["ref_sheet"], ref["x"],
                                   ref["y"], hint=True)
            # Recipient: re-measure on the contact's tile and check the summary.
            rtile = tile_by_name[c["tile"]]
            pos = pixel_position(args.tile_dir, rtile, ref["x"], ref["y"])
            rstem = rtile["name"].removesuffix(".png")
            rpng = args.tile_dir / rtile["sheet"] / f"{rstem}.png"
            rmeasure = measure_pixels(rpng, pos[0], pos[1], None)
            rverdict = classify(rmeasure)
            if rverdict != c["verdict"]:
                raise SystemExit(f"recipient verdict differs from the summary: "
                                 f"{c['ref_id']} {c['tile']}")
            rhint = symbol_hint(rpng, pos[0], pos[1],
                                metres_per_pixel(args.tile_dir, rtile))
            cls, reason = candidate_class(own["verdict"], rverdict)
            orig = originals[ref["key"]]
            orig_own = None
            if orig["status"] == "traced":
                orig_own = measure_on_sheet(index, args.tile_dir, c["ref_sheet"],
                                            orig["x"], orig["y"], hint=False)["verdict"]
            rec = {
                "ref_id": c["ref_id"], "feature_key": ref["key"],
                "ref_sheet": c["ref_sheet"], "recipient_sheet": c["tile_sheet"],
                "recipient_tile": c["tile"], "layer": ref["layer"],
                "position_source": ref["props"].get("position_source"),
                "own_verdict": own["verdict"], "own_tiles_disagree": own["tiles_disagree"],
                "own_n_tiles": own["n_tiles"], "own_tiles": own["tiles"],
                "own_hint": own.get("hint"),
                "recipient_verdict": rverdict,
                "recipient_window_near_black_fraction":
                    rmeasure["window_near_black_fraction"],
                "recipient_hint": rhint,
                "candidate_class": cls, "class_reason": reason,
                "original": orig, "original_own_verdict": orig_own,
            }
            records.append(rec)
            oh, rh = rec["own_hint"] or {}, rhint
            print(f"  {c['ref_sheet']} {c['ref_id']} (feature {ref['key']}) -> "
                  f"{c['tile']}: own {own['verdict']} ({own['n_tiles']} tile(s)"
                  f"{', DISAGREE' if own['tiles_disagree'] else ''}); recipient "
                  f"{rverdict}; class {cls}; hint own "
                  f"{oh.get('nearest_blob_px')} px / recipient "
                  f"{rh.get('nearest_blob_px')} px; original "
                  f"{orig['status']} {orig_own or ''}")

        # Distinct references: one per (feature, recipient sheet) pair. The
        # point is the same for every contact of a pair, so the own verdict
        # is too; the recipient verdict combines by priority.
        pairs: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for rec in records:
            pairs[(rec["feature_key"], rec["recipient_sheet"])].append(rec)
        pair_rows = []
        for (key, rsheet), recs in sorted(pairs.items()):
            rv = combine([r["recipient_verdict"] for r in recs])
            cls, reason = candidate_class(recs[0]["own_verdict"], rv)
            pair_rows.append({
                "feature_key": key, "ref_id": recs[0]["ref_id"],
                "ref_sheet": recs[0]["ref_sheet"], "recipient_sheet": rsheet,
                "own_verdict": recs[0]["own_verdict"], "recipient_verdict": rv,
                "candidate_class": cls, "class_reason": reason,
                "n_contacts": len(recs),
                "original_status": recs[0]["original"]["status"],
                "original_own_verdict": recs[0]["original_own_verdict"],
                "original_moved_m": recs[0]["original"].get("moved_m"),
                "own_hint_px": (recs[0]["own_hint"] or {}).get("nearest_blob_px"),
                "recipient_hint_px": min(
                    (r["recipient_hint"]["nearest_blob_px"] for r in recs
                     if r["recipient_hint"]["nearest_blob_px"] is not None),
                    default=None),
            })

        def tally(rows: list[dict]) -> dict[str, Any]:
            """Count rows by class, by own × recipient verdict, and by seam."""
            by_seam: dict[str, Counter] = defaultdict(Counter)
            for r in rows:
                by_seam[f"{r['ref_sheet']} -> {r['recipient_sheet']}"][
                    r["candidate_class"]] += 1
            return {
                "by_class": dict(Counter(r["candidate_class"] for r in rows)),
                "by_own_x_recipient": dict(Counter(
                    f"own {r['own_verdict']} / recipient {r['recipient_verdict']}"
                    for r in rows)),
                "by_seam": {k: dict(v) for k, v in sorted(by_seam.items())},
            }

        # Symbol-level consequence: distinct references (by feature) that
        # D50's per-sheet matching places on a sheet (their source_map)
        # where the point is padding or outside that sheet's tiles.
        features: dict[str, dict[str, Any]] = {}
        for rec in records:
            f = features.setdefault(rec["feature_key"], {
                "ref_id": rec["ref_id"], "own_verdict": rec["own_verdict"],
                "recipient_verdicts": set()})
            f["recipient_verdicts"].add(rec["recipient_verdict"])
        consequence = Counter()
        for f in features.values():
            rv = "map-content" if "map-content" in f["recipient_verdicts"] else "ambiguous"
            consequence[f"own {f['own_verdict']} / recipient {rv}"] += 1
        entry = {
            "n_contacts": len(records), "n_pairs": len(pair_rows),
            "n_features": len(features),
            "contacts": tally(records), "pairs": tally(pair_rows),
            "features_by_own_and_recipient": dict(consequence),
            "original_status": dict(Counter(r["original_status"] for r in pair_rows)),
            "original_own_by_final_own": dict(Counter(
                f"final {r['own_verdict']} / original {r['original_own_verdict']}"
                for r in pair_rows if r["original_status"] == "traced")),
            "pair_rows": pair_rows, "contact_records": records,
        }
        print(f"  contacts: {entry['contacts']['by_class']}; "
              f"{entry['contacts']['by_own_x_recipient']}")
        print(f"  pairs ({len(pair_rows)}): {entry['pairs']['by_class']}; "
              f"{entry['pairs']['by_own_x_recipient']}")
        print(f"  features ({len(features)}): {dict(consequence)}")
        print(f"  original coordinates: {entry['original_status']}; "
              f"{entry['original_own_by_final_own']}")
        for seam, counts in entry["pairs"]["by_seam"].items():
            print(f"    pairs at {seam}: {counts}")
        report["references"][ref_name] = entry

    if args.astra is not None:
        report["astra"] = compare_astra(args.astra, report["references"][R2])

    if args.json_out is not None:
        args.json_out.write_text(json.dumps(report, indent=1, default=list) + "\n")


def compare_astra(path: Path, r2: dict[str, Any]) -> dict[str, Any]:
    """Compare r2's own-sheet verdicts with Astra's full-scan diagnostic.

    Astra measured the labelled source scan (whole sheet), near-black being
    all bands at most 8, in 9 × 9 and 31 × 31 windows; this script measures
    the own-sheet tiles, near-black being all bands at most 20, with the
    sheet check's verdict rule. Agreement is read as: Astra all-black at
    9 × 9 if and only if this script's own verdict is padding or outside.

    Args:
        path: Astra's ``source-padding-diagnostic.json``.
        r2: This script's r2 entry.

    Returns:
        The input hash, one row per Astra pair, and the disagreements.
    """
    astra = json.loads(path.read_text())
    mine = {(p["ref_id"], p["recipient_sheet"]): p for p in r2["pair_rows"]}
    rows, disagree = [], []
    print(f"\n=== Astra comparison ({path.name}, sha256 {sha256(path)[:12]})")
    for a in astra["rows"]:
        k = (a["reference_id"], a["recipient_sheet"])
        p = mine.get(k)
        fin = a["reference_at_final_coordinate"]
        inp = a.get("reference_at_input_coordinate") or {}
        row = {
            "ref_id": k[0], "recipient_sheet": k[1],
            "astra_candidate_verdict": a["candidate_verdict"],
            "astra_final_9px": fin["near_black_fraction_9px"],
            "astra_final_31px": fin["near_black_fraction_31px"],
            "astra_final_inside_scan": fin["inside_scan"],
            "astra_input_9px": inp.get("near_black_fraction_9px"),
            "astra_position_source": a.get("position_source"),
            "mine_found": p is not None,
            "mine_recipient": p and p["recipient_verdict"],
            "mine_own": p and p["own_verdict"],
            "mine_original_own": p and p["original_own_verdict"],
            "mine_class": p and p["candidate_class"],
        }
        astra_black = fin["near_black_fraction_9px"] == 1.0
        mine_black = p is not None and p["own_verdict"] in ("padding", "outside")
        row["agree"] = p is not None and astra_black == mine_black
        if p is not None and inp:
            row["agree_original"] = ((inp.get("near_black_fraction_9px") == 1.0)
                                     == (p["original_own_verdict"]
                                         in ("padding", "outside")))
        rows.append(row)
        if not row["agree"] or row.get("agree_original") is False:
            disagree.append(row)
        print(f"  {k[0]} -> {k[1]}: Astra {a['candidate_verdict']}, own 9px "
              f"{fin['near_black_fraction_9px']:.3f} / 31px "
              f"{fin['near_black_fraction_31px']:.3f}; mine own {row['mine_own']}, "
              f"original {row['mine_original_own']}, class {row['mine_class']}"
              f"{'' if row['agree'] else '  <-- DISAGREE'}")
    unmatched = sorted(set(mine) - {(r["ref_id"], r["recipient_sheet"]) for r in rows})
    print(f"  rows {len(rows)}; disagreements {len(disagree)}; "
          f"my pairs not in Astra's file {len(unmatched)}")
    return {"input": str(path), "sha256": sha256(path), "rows": rows,
            "disagreements": disagree, "mine_not_in_astra": unmatched}


if __name__ == "__main__":
    main()
