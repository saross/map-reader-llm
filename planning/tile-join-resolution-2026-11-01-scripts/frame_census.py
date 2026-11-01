"""Frame census for the tile-join review: overlap, frames per signed row, coverage.

Evidence for ``planning/tile-join-resolution-2026-11-01.md`` (S167,
2026-11-01). For the 21 signed register rows that quote tile-MCC (the list in
the S166 CLOSE block of ``planning/paper-writeup-continuity.md``), this
reports:

1. every frame (bounds file) their cells' evaluations were scored on, read
   from each evaluation's ``_metadata.cli_args.bounds``;
2. each frame's overlap: summed tile area over the area of the tiles' union
   (1.0 is a partition);
3. per row, how many of its conditions have a committed geometric-join
   reading. This is a TEXT match of ``run::label`` ids and labels against the
   committed tile-join outputs, so it is indicative, not exact;
4. in the Era-2 board's cells whose detection files record ``source_tiles``,
   the share of detections seen on two or more tiles.

Run from the repository root with the project venv. Output:
``frame_census.txt`` beside this file. Zero API calls.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import geopandas as gpd

REPO = Path(__file__).resolve().parents[2]

ROWS = [
    # 11 of the 15 rows re-signed 2026-10-30 that quote MCC
    "k-ladder-2026-09-12", "gs-era2-verified-board-2026-09-10", "verifier-uplift-pairing",
    "null-exemplar-sensitivity-2026-09-13", "grid-postverifier-2026-08-18",
    "grid-tilesize-overlap-2026-08-18", "gemini37-screen-2026-08-28",
    "gemini38-screen-armv-2026-09-04", "gemini37-fourth-cell-gs-leg-2026-08-31",
    "image-b-modality-2026-08-28", "image-b-thinking-pair-2026-08-28",
    # ten other signed rows that quote MCC
    "pass-budget-pareto-v2", "tile-level-f1", "tile-level-f1-r2",
    "gemini3-image-55map-2026-09-16", "gemini37-image-55map-2026-09-13",
    "gemini37-image-55map-k5-replicate-2x2-2026-09-20", "gemini37-55map-grid-2026-08-31",
    "55map-r2-leaderboard-mcc-50m", "h13-overlap-2026-08-18", "obs280-shared-reference-r2",
]
GEOMETRIC_OUTPUTS = [
    REPO / "results/tile-join-audit",
    REPO / "results/k-ladder-2026-09-12/mcc-join-2026-10-30/geometric-primary",
    REPO / "results/k-ladder-2026-09-12/mcc-join-2026-10-30/geometric-contains",
]


def frame_of(eval_path: Path) -> str:
    """Return the repo-relative bounds file an evaluation was scored on."""
    meta = json.loads(eval_path.read_text()).get("_metadata", {})
    bounds = (meta.get("cli_args") or {}).get("bounds") or \
        (meta.get("input_files") or {}).get("bounds") or "<none recorded>"
    bounds = str(bounds)
    for anchor in ("inputs/", "outputs/"):
        if anchor in bounds:
            return bounds[bounds.index(anchor):]
    return bounds


def overlap_ratio(bounds_rel: str) -> tuple[int, float]:
    """Tile count and summed-area / union-area ratio of one frame."""
    gdf = gpd.read_file(REPO / bounds_rel)
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    if gdf.crs.is_geographic:
        gdf = gdf.to_crs(32635)
    return len(gdf), float(gdf.geometry.area.sum() / gdf.geometry.union_all().area)


def main() -> int:
    """Write the census to ``frame_census.txt`` and echo it."""
    analyses = {a["analysis_id"]: a for a in
                json.loads((REPO / "results/run-analyses.json").read_text())["analyses"]}
    decomp = json.loads((REPO / "results/run-conditions.json").read_text())["decomposition"]

    covered: set[str] = set()
    for root in GEOMETRIC_OUTPUTS:
        for path in root.rglob("*.json"):
            text = path.read_text()
            covered |= set(re.findall(r'"([A-Za-z0-9_.\-]+::[A-Za-z0-9_.\-]+)"', text))
            covered |= set(re.findall(r'"label":\s*"([^"]+)"', text))

    lines: list[str] = []
    frames_seen: Counter[str] = Counter()
    lines.append("## Frames per signed row, and geometric-join coverage (text match)")
    for rid in ROWS:
        row = analyses[rid]
        frames: Counter[str] = Counter()
        n_cov = 0
        for ref in row["conditions_compared"]:
            run, label = ref.split("::", 1)
            if ref in covered or label in covered:
                n_cov += 1
            cond = next((c for c in decomp.get(run, {}).get("conditions", [])
                         if c["label"] == label), None)
            eval_path = (cond or {}).get("eval_path")
            if eval_path and (REPO / eval_path).exists():
                frames[frame_of(REPO / eval_path)] += 1
        frames_seen.update(frames)
        frame_text = "; ".join(f"{f} x{n}" for f, n in sorted(frames.items()))
        lines.append(f"{rid}: {n_cov}/{len(row['conditions_compared'])} covered | {frame_text}")

    lines.append("")
    lines.append("## Frame overlap (summed tile area / union area; 1.0 = partition)")
    for frame in sorted(frames_seen):
        if frame.startswith("<"):
            continue
        n_tiles, ratio = overlap_ratio(frame)
        lines.append(f"{frame}: {n_tiles} tiles, {ratio:.4f}")

    lines.append("")
    lines.append("## Era-2 board: detections seen on 2+ tiles (cells recording source_tiles)")
    shares: Counter[str] = Counter()
    n_with, n_without = 0, 0
    for ref in analyses["gs-era2-verified-board-2026-09-10"]["conditions_compared"]:
        run, label = ref.split("::", 1)
        cond = next(c for c in decomp[run]["conditions"] if c["label"] == label)
        feats = json.loads((REPO / cond["detections"]).read_text())["features"]
        lens = [len(f["properties"].get("source_tiles") or []) for f in feats]
        if not any(lens):
            n_without += 1
            continue
        n_with += 1
        for n in lens:
            shares["2+" if n > 1 else str(n)] += 1
    total = sum(shares.values())
    lines.append(f"cells with the list: {n_with}; without: {n_without}")
    lines.append(", ".join(f"{k} tiles: {v} ({v / total:.1%})" for k, v in sorted(shares.items())))

    out = "\n".join(lines) + "\n"
    (Path(__file__).parent / "frame_census.txt").write_text(out)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
