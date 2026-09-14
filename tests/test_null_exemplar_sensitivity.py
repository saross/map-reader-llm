"""Tier-1 tests for the null-exemplar leak sensitivity instruments.

Covers the properties the 2026-09-13 sensitivity analysis rests on:

1. **The overlap geometry.** A tile is exposed when its WINDOW overlaps a null
   exemplar window with strictly positive area — touching edges do not count,
   and the pixel-space test must agree with the ground-space one under the
   per-sheet affine the script derives rather than assumes.
2. **The affine derivation fails loudly.** A frame whose tiles do not share one
   resolution and one origin per sheet invalidates the pixel-space test, so
   ``derive_sheet_affines`` must raise rather than return a fitted average.
3. **The exposure rule.** ``include_example_images`` defaults to TRUE in the
   pipeline, and a config that sends images but carries no null-category
   example is NOT exposed.
4. **The filter keeps the file and drops the right features.** Filtering must
   remove exactly the features booked to an exposed tile and leave every other
   property and the CRS declaration untouched.
5. **Cell shape is preserved (regression).** ``cell_per_tile`` reads a
   ``detections`` LIST as one unioned set but a ``detections_dir`` as the
   per-tile MEAN over pass files, so ``reduced_cli`` must hand a
   replicate-mean cell a DIRECTORY, never a list. Collapsing the mean into a
   union produced apparent between-frame deltas of up to 0.33 F1 before this
   was fixed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
for candidate in (REPO, REPO / "scripts"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import compute_null_exemplar_overlap as overlap  # noqa: E402

pytestmark = pytest.mark.tier1


# ── 1. the overlap geometry ──────────────────────────────────────────────

def test_parse_tile_name_reads_the_pixel_window():
    """A tile name yields its sheet and its top-left pixel offset."""
    assert overlap.parse_tile_name("K-35-052-4_32635_x896_y1792.png") == (
        "K-35-052-4_32635", 896, 1792)


def test_parse_tile_name_rejects_a_name_with_no_window():
    """A name that encodes no window is an error, not a silent skip."""
    with pytest.raises(ValueError, match="does not encode a pixel window"):
        overlap.parse_tile_name("some-other-file.png")


@pytest.mark.parametrize(
    ("a_x", "a_y", "expected", "why"),
    [
        (0, 0, True, "a 384 window at the null window's own origin overlaps"),
        (511, 0, True, "one pixel of column overlap still overlaps"),
        (512, 0, False, "abutting on the right edge shares no area"),
        (-384, 0, False, "abutting on the left edge shares no area"),
        (0, 512, False, "abutting below shares no area"),
        (-383, -383, True, "a single corner pixel of overlap counts"),
        (-384, -384, False, "a shared corner point shares no area"),
    ],
)
def test_windows_overlap_requires_positive_area(a_x, a_y, expected, why):
    """Only a strictly positive intersection counts as an overlap."""
    assert overlap.windows_overlap(a_x, a_y, 384, 0, 0, 512) is expected, why


def test_envelopes_overlap_ignores_a_shared_edge():
    """Two envelopes meeting on an edge do not overlap."""
    assert not overlap.envelopes_overlap((0, 0, 10, 10), (10, 0, 20, 10))
    assert overlap.envelopes_overlap((0, 0, 10, 10), (9, 0, 20, 10))


# ── 2. the affine derivation ─────────────────────────────────────────────

def _square(minx: float, miny: float, side: float) -> dict:
    """Build a rectangular bounds feature."""
    return {
        "type": "Feature",
        "properties": {},
        "geometry": {"type": "Polygon", "coordinates": [[
            [minx, miny], [minx + side, miny],
            [minx + side, miny + side], [minx, miny + side], [minx, miny],
        ]]},
    }


def _frame(entries: list[tuple[str, float, float, float]]) -> dict:
    """Build a tile-name -> envelope mapping from (name, minx, miny, side)."""
    out = {}
    for name, minx, miny, side in entries:
        ring = _square(minx, miny, side)["geometry"]["coordinates"][0]
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        out[name] = (min(xs), min(ys), max(xs), max(ys))
    return out


def test_derive_sheet_affines_recovers_the_grid():
    """One resolution and one top-left origin are recovered per sheet."""
    # Two tiles of a 10-px sheet at 5 m/px: pixel x grows east, pixel y south.
    frame = _frame([
        ("S_x0_y0.png", 1000.0, 1950.0, 50.0),
        ("S_x10_y0.png", 1050.0, 1950.0, 50.0),
        ("S_x0_y10.png", 1000.0, 1900.0, 50.0),
    ])
    affines = overlap.derive_sheet_affines(frame, tile_px=10)
    res, origin_x, origin_y_top = affines["S"]
    assert res == pytest.approx(5.0)
    assert origin_x == pytest.approx(1000.0)
    assert origin_y_top == pytest.approx(2000.0)


def test_derive_sheet_affines_raises_on_a_mixed_resolution():
    """A sheet whose tiles disagree on resolution invalidates the test."""
    frame = _frame([
        ("S_x0_y0.png", 0.0, 0.0, 50.0),
        ("S_x10_y0.png", 50.0, 0.0, 60.0),
    ])
    with pytest.raises(AssertionError, match="disagree on resolution"):
        overlap.derive_sheet_affines(frame, tile_px=10)


def test_derive_sheet_affines_raises_on_a_shifted_origin():
    """A sheet whose tiles do not share one origin invalidates the test."""
    frame = _frame([
        ("S_x0_y0.png", 0.0, 0.0, 50.0),
        ("S_x10_y0.png", 55.0, 0.0, 50.0),
    ])
    with pytest.raises(AssertionError, match="disagree on the sheet origin"):
        overlap.derive_sheet_affines(frame, tile_px=10)


def test_nominal_window_projects_pixel_y_downwards():
    """Pixel y grows south while northing grows north."""
    affines = {"S": (5.0, 1000.0, 2000.0)}
    minx, miny, maxx, maxy = overlap.nominal_window(affines, "S", 10, 10, 10)
    assert (minx, maxy) == pytest.approx((1050.0, 1950.0))
    assert (maxx, miny) == pytest.approx((1100.0, 1900.0))


# ── 3. the exposure rule ─────────────────────────────────────────────────

def _write_meta(path: Path, include: bool | None, categories: list[str],
                version: str = "detect_test") -> None:
    """Write a minimal run.meta.json."""
    config: dict = {"version": version, "full_config_snapshot": {
        "version": version,
        "examples": [{"path": f"e{i}.png", "category": c}
                     for i, c in enumerate(categories)],
    }}
    if include is not None:
        config["include_example_images"] = include
    path.write_text(json.dumps({"configuration": config}))


def test_include_example_images_defaults_to_true(tmp_path):
    """A config with no key sent the images — the pipeline default is TRUE."""
    import analyse_null_exemplar_sensitivity as sens

    meta = tmp_path / "run.meta.json"
    _write_meta(meta, None, ["canonical_positive", "null"])
    read = sens.read_run_meta(meta)
    assert read["include_example_images"] is True
    assert read["n_null_examples"] == 1


def test_images_without_a_null_example_are_not_exposure(tmp_path):
    """Sending images is not enough: a null-category exemplar must be present."""
    import analyse_null_exemplar_sensitivity as sens

    meta = tmp_path / "run.meta.json"
    _write_meta(meta, True, ["canonical_positive", "hard_negative"])
    read = sens.read_run_meta(meta)
    assert read["include_example_images"] is True
    assert read["n_null_examples"] == 0


def test_text_only_config_is_not_exposure(tmp_path):
    """A text-only config sent the labels, not the pixels."""
    import analyse_null_exemplar_sensitivity as sens

    meta = tmp_path / "run.meta.json"
    _write_meta(meta, False, ["null", "null", "null"])
    read = sens.read_run_meta(meta)
    assert read["include_example_images"] is False
    assert read["n_null_examples"] == 3


@pytest.mark.parametrize(
    ("text", "expected"),
    [("flash-high-image-n5", "image"), ("brief-text", "text"),
     ("detect_brief-text-image", "both"), ("scale-4-optimal-487", None)],
)
def test_name_modality_tokens(text, expected):
    """The pool-name fallback reads image/text tokens, and flags both."""
    import analyse_null_exemplar_sensitivity as sens

    assert sens.name_modality(text) == expected


# ── 4. the filter ────────────────────────────────────────────────────────

def test_filter_one_drops_only_the_exposed_features(tmp_path, monkeypatch):
    """Features booked to an exposed tile go; everything else is untouched."""
    import analyse_null_exemplar_sensitivity as sens

    # filter_one resolves its source and destination against the repository
    # root; the test re-roots that at tmp_path so the real path handling runs.
    monkeypatch.setattr(sens, "BASE_DIR", tmp_path)
    src = tmp_path / "detections.geojson"
    payload = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
        "features": [
            {"type": "Feature",
             "properties": {"source_tile": "A_x0_y0.png", "confidence": 0.9},
             "geometry": {"type": "Point", "coordinates": [1.0, 2.0]}},
            {"type": "Feature",
             "properties": {"source_tile": "A_x336_y0.png", "confidence": 0.1},
             "geometry": {"type": "Point", "coordinates": [3.0, 4.0]}},
        ],
    }
    src.write_text(json.dumps(payload))
    dest = tmp_path / "out" / "detections.geojson"
    entry = sens.filter_one("detections.geojson", dest, {"A_x336_y0.png"}, None)
    assert entry == {
        "source": "detections.geojson", "filtered": "out/detections.geojson",
        "n_features": 2, "n_dropped": 1, "n_kept": 1,
        "source_tile_backfilled": False,
    }
    written = json.loads(dest.read_text())
    assert written["crs"] == payload["crs"], "the CRS declaration must survive"
    assert [f["properties"] for f in written["features"]] == [
        {"source_tile": "A_x0_y0.png", "confidence": 0.9}]


# ── 5. cell shape is preserved (regression) ──────────────────────────────

def test_reduced_cli_keeps_a_replicate_mean_cell_a_directory():
    """A pass-directory cell must stay a directory, not become a file list.

    ``cell_per_tile`` reads a ``detections`` list as ONE unioned set and a
    ``detections_dir`` as the per-tile MEAN over the matched pass files, so
    handing a replicate-mean cell a list silently changes its statistic.
    """
    import analyse_null_exemplar_sensitivity as sens

    cli = {"detections": None, "detections_dir": "outputs/run/pool",
           "glob": "*/detections_*.geojson", "bounds": "b.geojson"}
    entry = {"source_detections_dir": "outputs/run/pool",
             "source_glob": "*/detections_*.geojson",
             "detections_root": "results/sens/detections/frame/cell",
             "files": [{"filtered": "results/sens/detections/frame/cell/a.geojson"},
                       {"filtered": "results/sens/detections/frame/cell/b.geojson"}]}
    out = sens.reduced_cli(cli, entry)
    assert out["detections_dir"] == "results/sens/detections/frame/cell"
    assert out["glob"] == "*/detections_*.geojson"
    assert out["detections"] is None
    assert out["bounds"] == "b.geojson", "unrelated keys are carried through"


def test_reduced_cli_keeps_a_single_set_cell_a_list():
    """A cell scored from an explicit file list stays a list."""
    import analyse_null_exemplar_sensitivity as sens

    cli = {"detections": ["results/x.geojson"], "detections_dir": None,
           "glob": None}
    entry = {"source_detections_dir": None, "source_glob": None,
             "detections_root": "results/sens/detections/frame/cell",
             "files": [{"filtered": "results/sens/detections/frame/cell/x.geojson"}]}
    out = sens.reduced_cli(cli, entry)
    assert out["detections"] == ["results/sens/detections/frame/cell/x.geojson"]
    assert out["detections_dir"] is None
    assert out["glob"] is None


def test_committed_findings_matches_a_rerender():
    """The committed findings.md must match a regeneration from its artefacts.

    The document's numbers are substituted from `analysis.json`,
    `leak_signature.json` and `paired_tile_swap.json`, so this is the drift
    guard the project's generated documents carry: a re-computation that was
    not followed by a re-render fails here rather than leaving stale numbers
    in a cited document.
    """
    import render_null_exemplar_findings as render

    needed = [render.OUT_DIR / name for name in
              ("analysis.json", "leak_signature.json", "paired_tile_swap.json",
               "overlap_tiles.json", "cell_inventory.json", "findings.md")]
    missing = [p.name for p in needed if not p.exists()]
    if missing:
        pytest.skip(f"sensitivity artefacts absent: {', '.join(missing)}")
    assert render.main(["--check"]) == 0, (
        "results/null-exemplar-sensitivity-2026-09-13/findings.md is stale — "
        "re-run scripts/render_null_exemplar_findings.py")


def test_mcc_from_confusion_matches_the_definition():
    """The MCC helper agrees with the closed form and guards a zero margin."""
    import analyse_null_exemplar_sensitivity as sens

    assert sens.mcc_from_confusion(10, 10, 0, 0) == pytest.approx(1.0)
    assert sens.mcc_from_confusion(0, 0, 10, 10) == pytest.approx(-1.0)
    assert sens.mcc_from_confusion(5, 5, 5, 5) == pytest.approx(0.0)
    assert sens.mcc_from_confusion(10, 0, 0, 0) is None, "a zero margin is None"
