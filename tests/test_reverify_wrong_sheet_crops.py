"""
Tests for ``scripts/reverify_wrong_sheet_crops.py`` (PI decision D62 (1), step 2).

The script re-verifies wrong-sheet verifier candidates on crops cut from
their own sheet, as one Batch API job per verifier configuration, and books
the answers into each leg's ``<leg>_repaired/`` copy. These tests build a
tiny synthetic repository on disk (two rasters, a crop manifest, three legs)
and fake the API lifecycle, so they make no call:

- **build** cuts the corrected crop with the project's extractor from the
  right sheet, groups the requests by configuration with leg-tagged keys,
  sends a ``_repaired`` leg once (under its sibling), and refuses on a wrong
  call count, an estimate over the ceiling, an old crop the extractor does
  not reproduce, and an unexpected sheet.
- **lodge** refuses a second batch and a model that resolves to another
  name, prints the ``wait_for_run.py`` markers, and never re-sends.
- **book** creates a repaired copy from the leg (or merges into the
  committed one), changes only the re-verified rows, removes a row whose
  answer is unparseable, and refuses to book twice.
- **release** deletes nothing while a job is not terminal.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import reverify_wrong_sheet_crops as ws  # noqa: E402
from scripts.extract_candidates import crop_region  # noqa: E402

pytestmark = pytest.mark.tier1

rasterio = pytest.importorskip("rasterio")

#: The verifier configuration every synthetic leg ran (the real prompt file,
#: so the system-instruction hash audit runs against real bytes).
SNAPSHOT = {
    "version": "verify_adversarial-text", "model": "gemini-3-flash",
    "instruction_file": "verify_adversarial.md", "temperature": 0.0,
    "max_output_tokens": 8192, "thinking_level": "minimal", "examples": [],
    "text_only_labels": ["Positive: Burial Mound (Kurgan)", "Negative: Benchmark ALONE"],
    "crop_label": "Now classify the candidate symbol at the centre of this crop:",
}
CROP_SHEET, FIX_SHEET = ws.EXPECTED_CROP_SHEET, ws.EXPECTED_FIX_SHEET
X0, Y0, RES = 400_000.0, 4_700_000.0, 5.0
POINTS = [(X0 + 500.0, Y0 - 500.0), (X0 + 900.0, Y0 - 900.0)]
GOOD = ('{"best_alternative": "a", "alternative_evidence": "e", "reasoning": "r", '
        '"mound_probability": 0.9}')
#: An unescaped double quote inside a string, which no repair tier parses
#: (``tests/test_reverify_unparseable_rows.py``'s verbatim 55-map row, shortened).
UNPARSEABLE = (
    '{\n    "best_alternative": "Natural shoreline",\n    "alternative_evidence": "small '
    "vegetation marks ('\"'), but no central mound symbol.\",\n    \"reasoning\": \"None.\","
    '\n    "mound_probability": 0.0\n}')


def _instruction_hash() -> str:
    text = (PROJECT_ROOT / "prompts/system-instructions/verify_adversarial.md").read_text()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _raster(path: Path, value: int, mark: bool = True) -> None:
    """A 3-band 400 x 400 GeoTIFF in EPSG:32635, filled with *value*."""
    from rasterio.transform import from_origin

    path.parent.mkdir(parents=True, exist_ok=True)
    arr = np.full((3, 400, 400), value, dtype=np.uint8)
    if mark:
        arr[:, 95:105, 95:105] = 30  # a mark at the first point
    with rasterio.open(path, "w", driver="GTiff", height=400, width=400, count=3,
                       dtype="uint8", crs="EPSG:32635",
                       transform=from_origin(X0, Y0, RES, RES)) as dst:
        dst.write(arr)


def _leg(root: Path, leg: str, model: str, thinking: str, probs: dict[str, float]) -> None:
    d = root / leg
    d.mkdir(parents=True, exist_ok=True)
    snap = dict(SNAPSHOT, thinking_level=thinking)
    results = {k: {"mound_probability": p, "reasoning": "old", "best_alternative": "b",
                   "alternative_evidence": "e"} for k, p in probs.items()}
    (d / "probabilities.json").write_text(json.dumps({
        "version": "1.0", "mode": "realtime", "verifier_config": "verify_adversarial-text",
        "iterations": 1, "total_results": len(results), "results": results}, indent=2))
    (d / "run.meta.json").write_text(json.dumps({"configuration": {
        "version": "verify_adversarial-text", "model": model,
        "instruction_file": "verify_adversarial.md",
        "system_instruction_hash": _instruction_hash(), "temperature": 0.0,
        "max_output_tokens": 8192, "thinking_level": thinking,
        "full_config_snapshot": snap},
        "usage_stats": {"total_input_tokens": 1792 * 2, "total_output_tokens": 150 * 2,
                        "total_cached_tokens": 0, "total_thoughts_tokens": 0},
        "results_summary": {"batch_usage": {"n_responses_with_usage": 2}}}))


@pytest.fixture()
def repo(tmp_path: Path) -> dict:
    """A synthetic repository: rasters, one crop manifest, three legs."""
    root = tmp_path / "repo"
    _raster(root / "inputs/rasters" / f"{CROP_SHEET}.tif", 0, mark=False)  # off-map
    _raster(root / "inputs/rasters" / f"{FIX_SHEET}.tif", 200)   # on-map
    cell = "outputs/run/verifier/cell"
    crops = root / cell / "crops"
    cands = []
    for i, (x, y) in enumerate(POINTS):
        crop_region(root / "inputs/rasters" / f"{CROP_SHEET}.tif", (x, y), 75,
                    crops / "crops" / f"candidate_{i:05d}.png")
        cands.append({"candidate_id": i, "crop_file": f"crops/candidate_{i:05d}.png",
                      "source_tile": f"{CROP_SHEET}_x0_y0.png", "centroid_x": x,
                      "centroid_y": y, "properties": {"vote_count": 7}})
    manifest = {"rasters_dir": "/gone/inputs/rasters", "padding": 75, "candidates": cands}
    (crops / "candidate_manifest.json").write_text(json.dumps(manifest))
    probs = {"candidate_00000": 0.05, "candidate_00001": 0.8}
    _leg(root, f"{cell}/verify", "gemini-3-flash-preview", "minimal", probs)
    _leg(root, f"{cell}/verify_37", "gemini-3.7-flash", "low", probs)
    _leg(root, f"{cell}/verify_37_repaired", "gemini-3.7-flash", "low", probs)
    old_dark = ws.dark_shares(ws.pixels(crops / "crops/candidate_00000.png"))[0]
    rows = []
    for leg in ("verify", "verify_37", "verify_37_repaired"):
        rows.append({"leg": f"{cell}/{leg}", "candidate_id": "0", "crop_sheet": CROP_SHEET,
                     "fix_sheet": FIX_SHEET, "x": f"{POINTS[0][0]:.6f}",
                     "y": f"{POINTS[0][1]:.6f}", "dark_as_verified": f"{old_dark}",
                     "fix_dark": "0.0"})
    rows.append(dict(rows[0], leg="archive/old/verify"))  # out of scope
    sel = tmp_path / "wrong_sheet.csv"
    with open(sel, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    pairing = tmp_path / "pairing.json"
    pairing.write_text(json.dumps({f"{cell}/{leg}": {"manifest": f"{cell}/crops/"
                                                     "candidate_manifest.json"}
                                   for leg in ("verify", "verify_37",
                                               "verify_37_repaired")}))
    return {"root": root, "cell": cell, "selection": sel, "pairing": pairing,
            "run": root / "outputs/reverify-run"}


def _build(r: dict, **kw) -> dict:
    args = {"repo": r["root"], "data_root": r["root"], "selection": r["selection"],
            "pairing": r["pairing"], "out_dir": r["run"], "expect_calls": 2,
            "tolerance": 0.0, "max_cost_usd": 0.05, "at": "2026-10-13"}
    args.update(kw)
    return ws.build(**args)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def test_build_groups_by_configuration_and_cuts_from_the_right_sheet(repo: dict) -> None:
    rec = _build(repo)
    assert rec["n_calls"] == 2
    assert sorted(rec["jobs"]) == ["gemini-3-flash-preview_t0.0_minimal",
                                   "gemini-3.7-flash_t0.0_low"]
    # The _repaired leg rides on its sibling: sent once, booked there.
    assert rec["riders"] == {f"{repo['cell']}/verify_37_repaired": f"{repo['cell']}/verify_37"}
    keys = sorted(r["request_key"] for r in rec["rows"])
    assert keys == ["L00__candidate_00000", "L01__candidate_00000"]
    crop = rec["rows"][0]["crop"]
    assert crop["old"]["dark_share"] == 1.0 and crop["old"]["recut_equal_pixels"]
    assert crop["new"]["dark_share"] == 0.0 and crop["new"]["raster"] == f"{FIX_SHEET}.tif"
    line = json.loads((repo["run"] / rec["jobs"]["gemini-3.7-flash_t0.0_low"]["requests"]
                       ["path"]).read_text().splitlines()[0])
    gen = line["request"]["generation_config"]
    assert gen["thinking_config"]["thinking_level"] == "LOW" and gen["temperature"] == 0.0
    assert (repo["run"] / "build.json").is_file()


def test_build_is_deterministic(repo: dict, tmp_path: Path) -> None:
    a = _build(repo)
    b = _build(repo, out_dir=tmp_path / "second")
    for job in a["jobs"]:
        assert a["jobs"][job]["requests"]["sha256"] == b["jobs"][job]["requests"]["sha256"]


def test_build_refuses_a_call_count_outside_the_tolerance(repo: dict) -> None:
    with pytest.raises(ws.Refused, match="approved 3"):
        _build(repo, expect_calls=3)


def test_build_refuses_an_estimate_over_the_ceiling(repo: dict) -> None:
    with pytest.raises(ws.Refused, match="ceiling"):
        _build(repo, max_cost_usd=1e-7)


def test_build_refuses_an_old_crop_the_extractor_does_not_reproduce(repo: dict) -> None:
    from PIL import Image

    png = repo["root"] / repo["cell"] / "crops/crops/candidate_00000.png"
    Image.fromarray(np.full((150, 150, 3), 9, dtype=np.uint8)).save(png)
    with pytest.raises(ws.Refused, match="re-cut"):
        _build(repo)


def test_build_refuses_an_unexpected_fix_sheet(repo: dict) -> None:
    rows = list(csv.DictReader(open(repo["selection"])))
    for r in rows:
        r["fix_sheet"] = "K-35-062-2_Rakovski"
    with open(repo["selection"], "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with pytest.raises(ws.Refused, match="fix sheet"):
        _build(repo)


def test_build_never_overwrites(repo: dict) -> None:
    _build(repo)
    with pytest.raises(ws.Refused, match="not empty"):
        _build(repo)


# ---------------------------------------------------------------------------
# lodge (fake lifecycle)
# ---------------------------------------------------------------------------


def _fakes(answer: dict[str, str] | None = None, state: str = "JOB_STATE_SUCCEEDED",
           resolve=lambda c, m: m) -> dict:
    sent: list[str] = []

    def upload(client, path, name):
        sent.append(path.read_text())
        return f"files/{len(sent)}"

    def retrieve(client, done):
        lines = [json.loads(x) for x in sent[int(done.src.split('/')[1]) - 1].splitlines()]
        return [{"key": ln["key"], "response": {
            "candidates": [{"content": {"parts": [{"text": (answer or {}).get(ln["key"], GOOD)}]},
                            "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 1792, "candidatesTokenCount": 140,
                              "thoughtsTokenCount": 20, "totalTokenCount": 1952}}}
            for ln in lines]

    return {"resolve_model": resolve, "preflight": lambda *a, **k: None, "upload": upload,
            "submit": lambda c, m, f, n: SimpleNamespace(name=f"batches/{f}"),
            "poll": lambda c, name: SimpleNamespace(
                state=state, src=name.removeprefix("batches/"),
                dest=SimpleNamespace(file_name=f"out-{name}")),
            "retrieve": retrieve, "state_name": lambda s: s, "_sent": sent}


def _lodge(run: Path, fk: dict) -> int:
    return ws.lodge(run, None, 1.0, **{k: v for k, v in fk.items() if not k.startswith("_")})


def test_lodge_completes_and_refuses_a_second_batch(repo: dict, capsys) -> None:
    _build(repo)
    fk = _fakes()
    assert _lodge(repo["run"], fk) == 0
    assert ws.MARKER_COMPLETE in capsys.readouterr().out
    assert len(fk["_sent"]) == 2
    with pytest.raises(ws.Refused, match="second batch"):
        _lodge(repo["run"], _fakes())


def test_lodge_refuses_a_model_that_resolves_elsewhere(repo: dict) -> None:
    _build(repo)
    with pytest.raises(ws.Refused, match="resolves"):
        _lodge(repo["run"], _fakes(resolve=lambda c, m: m + "-x"))


def test_lodge_reports_partial_and_does_not_resend(repo: dict, capsys) -> None:
    _build(repo)
    fk = _fakes(state="JOB_STATE_FAILED")
    assert _lodge(repo["run"], fk) == 2
    assert ws.MARKER_PARTIAL in capsys.readouterr().out
    assert len(fk["_sent"]) == 2  # one upload per job, none repeated


# ---------------------------------------------------------------------------
# book
# ---------------------------------------------------------------------------


def test_book_merges_only_the_reverified_rows(repo: dict) -> None:
    _build(repo)
    _lodge(repo["run"], _fakes())
    root, cell = repo["root"], repo["cell"]
    leg_before = (root / cell / "verify/probabilities.json").read_bytes()
    rep_before = json.loads((root / cell / "verify_37_repaired/probabilities.json").read_text())
    assert ws.book(repo["run"], repo=root) == 0
    # The committed leg is never written; its new repaired copy is.
    assert (root / cell / "verify/probabilities.json").read_bytes() == leg_before
    new = json.loads((root / cell / "verify_repaired/probabilities.json").read_text())
    assert new["results"]["candidate_00000"]["mound_probability"] == 0.9
    assert new["results"]["candidate_00001"]["mound_probability"] == 0.8
    assert new[ws.BLOCK_KEY]["base"] == "leg"
    assert (root / cell / "verify_repaired/run.meta.json").read_bytes() == \
        (root / cell / "verify/run.meta.json").read_bytes()
    # The 3.7 leg's committed repaired copy is the base, and only one row moves.
    rep = json.loads((root / cell / "verify_37_repaired/probabilities.json").read_text())
    assert rep[ws.BLOCK_KEY]["base"] == "repaired copy"
    assert rep["results"]["candidate_00001"] == rep_before["results"]["candidate_00001"]
    recs = list((root / cell / "verify_37_repaired").glob("reverify-wrong-sheet-*.json"))
    assert len(recs) == 1
    row = json.loads(recs[0].read_text())["rows"][0]
    assert row["old_probability"] == 0.05 and row["new_probability"] == 0.9
    assert row["cost_usd"] > 0 and row["new_crop_dark_share"] == 0.0
    record = json.loads((repo["run"] / "record.json").read_text())
    assert record["n_booked"] == 2 and record["total_cost_usd"] > 0
    with pytest.raises(ws.Refused, match="already booked"):
        ws.book(repo["run"], repo=root)


def test_book_removes_an_unparseable_answer(repo: dict) -> None:
    _build(repo)
    _lodge(repo["run"], _fakes(answer={"L00__candidate_00000": UNPARSEABLE}))
    assert ws.book(repo["run"], repo=repo["root"]) == 1
    new = json.loads((repo["root"] / repo["cell"] /
                      "verify_repaired/probabilities.json").read_text())
    assert "candidate_00000" not in new["results"]
    assert new[ws.BLOCK_KEY]["removed_unparseable"] == ["candidate_00000"]


# ---------------------------------------------------------------------------
# release and helpers
# ---------------------------------------------------------------------------


def test_release_deletes_nothing_while_a_job_runs(repo: dict) -> None:
    _build(repo)
    _lodge(repo["run"], _fakes())
    deleted: list = []
    client = SimpleNamespace(batches=SimpleNamespace(
        get=lambda name: SimpleNamespace(state="JOB_STATE_RUNNING")))
    with pytest.raises(ws.Refused, match="nothing is released"):
        ws.release(repo["run"], client, state_name=lambda s: s,
                   terminal=frozenset({"JOB_STATE_SUCCEEDED"}),
                   delete=lambda c, names, label: deleted.append(names) or (len(names), 0))
    assert deleted == []


def test_dark_shares_counts_pure_black_only() -> None:
    img = np.full((21, 21, 3), 255, dtype=np.uint8)
    img[:, :7] = 0
    img[0, 10] = (0, 0, 1)  # not pure black
    whole, centre = ws.dark_shares(img)
    assert whole == round(7 * 21 / 441, 6) and centre == whole


def test_select_legs_refuses_a_repaired_leg_that_disagrees() -> None:
    rows = [{"leg": "outputs/a/verify", "candidate_id": "1"},
            {"leg": "outputs/a/verify_repaired", "candidate_id": "2"}]
    with pytest.raises(ws.Refused, match="sibling"):
        ws.select_legs(rows)


def test_operating_points_keep_a_named_pool_to_its_own_cell(tmp_path: Path) -> None:
    """``g384_ov192_image_high``'s labels begin with ``g384-ov192-image-``; its
    conditions must not be read as the ``g384_ov192_image`` cell's."""
    run = "image-b-gs-2026-08-28"
    conds = [
        {"label": "g384-ov192-image-min-k10-verified-p0.15-k9", "architecture":
         "proposer-verifier", "proposer_pool": "g384_ov192_image", "n_passes": 10,
         "prob_threshold": 0.15, "vote_threshold": 9,
         "verifier_config": {"model": "gemini-3-flash-preview"}},
        {"label": "g384-ov192-image-high-k10-verified-p0.20-k8", "architecture":
         "proposer-verifier", "proposer_pool": "g384_ov192_image_high", "n_passes": 10,
         "prob_threshold": 0.2, "vote_threshold": 8,
         "verifier_config": {"model": "gemini-3-flash-preview"}},
        {"label": "g384-ov192-k10-verified-p0.15-k10", "architecture": "proposer-verifier",
         "proposer_pool": "brief-text", "n_passes": 10, "prob_threshold": 0.15,
         "vote_threshold": 10, "verifier_config": {"model": "gemini-3-flash-preview"}},
    ]
    passes = {"a": {"path": "verifier/g384_ov192_image/verify"},
              "b": {"path": "verifier/g384_ov192_image_high/verify"}}
    (tmp_path / "results").mkdir()
    (tmp_path / "results/run-conditions.json").write_text(json.dumps(
        {"decomposition": {run: {"conditions": conds, "verifier_passes": passes}}}))
    ops = ws.operating_points(tmp_path, f"outputs/{run}/verifier/g384_ov192_image/verify",
                              "gemini-3-flash-preview", 10)
    assert [(o["prob_t"], o["min_votes"]) for o in ops] == [(0.15, 9)]
    # A bridge cell with no operating point registers none.
    cell = tmp_path / "results/modality-bridge-x/g3-text-temp1-g3v"
    cell.mkdir(parents=True)
    (cell / "analysis.json").write_text(json.dumps({"operating_point": None}))
    assert ws.operating_points(
        tmp_path, "outputs/modality-bridge-x/g3-text-temp1/verifier/d/verify_g3_rep2",
        "gemini-3-flash-preview", 10) == []
