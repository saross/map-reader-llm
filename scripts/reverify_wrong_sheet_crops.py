#!/usr/bin/env python3
"""
Re-verify wrong-sheet verifier candidates on crops cut from their own sheet.

Why this exists
---------------
Draft PR #42 (``origin-gap-grid-plateau``) found that a cluster centroid with
no recorded sheet sent the crop extractor to the neighbouring sheet's raster:
an Elenovo (``K-35-053-3``) point, keyed to a tile of ``K-35-052-4``, was cut
from ``K-35-052-4``'s raster, where it lies outside the map, so the verifier
saw a crop that was 59 to 100 % no-data and scored it near 0. The read-only
sweep of every verifier leg (``reports/s163-agent-records/
wrong-sheet-crops-sweep-2026-10-13.md``) found 1,515 such rows in 95 legs
under ``outputs/``. PI decision D62 (1), step 2
(``planning/pi-decisions-2026-09-20.md``), approved re-verifying every
affected leg's wrong-sheet candidates on crops cut from the right sheet: five
Batch API jobs, one per verifier configuration (model, prompt configuration,
temperature, and thinking level, each exactly as the leg ran), 1,029 calls,
about US$0.78.

This script carries that out and follows the D55 Q4 precedent
(``scripts/reverify_unparseable_rows.py``): the committed legs are never
written; each leg's answers are booked into its ``<leg>_repaired/`` copy, the
directory ``scripts/lib_verify_dirs.py`` reads, with a per-leg
``reverify-wrong-sheet-<date>.json`` record whose ``rows`` carry each call's
cost (the field ``verify_dir_provenance`` sums).

**Which rows.** The sweep's ``wrong_sheet.csv`` (its two runs are
byte-identical) names every (leg, candidate). A ``<leg>_repaired`` leg in it
is a re-parse of its sibling's calls, so it is sent once, under the sibling,
and booked into that same repaired copy. Rows outside ``outputs/`` (archive
legs and a human-review kit with no model) are out of scope.

**Which crop.** The corrected crop is cut by the project's own extractor,
``extract_candidates.crop_region``, at the manifest's recorded centroid and
padding, from the raster ``extract_candidates.resolve_raster_path`` finds for
the sheet the sweep names (every row: Elenovo). The old crop is re-cut the
same way from the raster its ``source_tile`` names, and must equal the PNG
the leg was shown pixel for pixel, so the extractor and the pairing of leg
and manifest are both confirmed before anything is sent.

**Which request.** Each request is built by ``lib_verifier.build_verifier_jsonl``
(the batch verifier path's builder) from the leg's recorded
``full_config_snapshot``, with the leg's recorded thinking level and
temperature, and audited against the leg's ``run.meta.json`` (temperature,
output ceiling, thinking level, system-instruction hash). Where the leg's own
request file survives (the batch legs that kept ``verifier_requests*.jsonl``),
the builder must also reproduce the leg's original line for the original crop
byte for byte. The key is prefixed with a leg tag (``L07__candidate_00185``)
because one job holds the same candidate for several legs.

Subcommands
-----------
``build``     Select the rows, cut and check the crops, build and audit the
              requests, group them into one job per configuration, estimate
              the cost on the rate card. Refuses unless the call count is
              within ``--tolerance`` of ``--expect-calls`` and the estimate
              is within ``--max-cost-usd``. Zero API.
``lodge``     Upload every job's requests and submit every job, then poll
              each to a terminal state and keep its ``batch_results.jsonl``.
              Refuses if any job is already recorded: a second batch is a new
              approval. Prints ``REVERIFY LODGE COMPLETE`` or
              ``REVERIFY LODGE PARTIAL`` at the start of a line. Nothing is
              ever re-sent.
``book``      Parse each answer (the batch parser, then the real-time path's
              repair), price its usage at the batch tier, and merge it into
              ``<leg>_repaired/``. Zero API.
``release``   After the outputs are committed: delete each job's input and
              output files from the Files API, only for a terminal job.
``summarise`` Per leg, how many re-verified candidates clear the leg's
              operating thresholds before and after; the gold-standard
              places; the audited cost by job. Zero API.

Usage (on sapphire, in a scratch clone; the crops, rasters and surviving
request files are the shared checkout's untracked files)::

    RUN=outputs/wrong-sheet-reverify-2026-10-13
    SW=~/scratch/wrong-sheet-crops-2026-10-13/out
    python scripts/reverify_wrong_sheet_crops.py build --out $RUN \\
        --selection $SW/runA/wrong_sheet.csv --pairing $SW/runA/legs.json \\
        --data-root ~/Code/map-reader-llm --sample-root $SW/runA/corrected-sample \\
        --expect-calls 1029 --tolerance 0.02 --max-cost-usd 1.50
    python scripts/reverify_wrong_sheet_crops.py lodge --run-dir $RUN --max-cost-usd 1.50
    python scripts/reverify_wrong_sheet_crops.py book --run-dir $RUN
    python scripts/reverify_wrong_sheet_crops.py summarise --run-dir $RUN
    # commit the run directory and the repaired copies, then:
    python scripts/reverify_wrong_sheet_crops.py release --run-dir $RUN

Created: 2026-10-13
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import logging
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.modality_bridge_stage2_checks import _response_text  # noqa: E402
from scripts.reverify_unparseable_rows import (  # noqa: E402
    Refused,
    audit_line,
    find_request_lines,
    parse_new_response,
    request_files,
    sha256_bytes,
    sha256_file,
)

logger = logging.getLogger(__name__)

#: The ruling this script carries out.
DECISION = "D62 (1) step 2, planning/pi-decisions-2026-09-20.md"

#: Markers printed at the start of a line for ``wait_for_run.py --marker``.
MARKER_COMPLETE = "REVERIFY LODGE COMPLETE"
MARKER_PARTIAL = "REVERIFY LODGE PARTIAL"

#: The tier every job is lodged at; the rate card prices it.
TIER = "batch"

#: The block a repaired copy's ``probabilities.json`` gains.
BLOCK_KEY = "reverify_wrong_sheet"

#: A crop pixel is "dark" when every band is 0 (the extractor's boundless
#: fill and the rasters' no-data), as the sweep measured it.
CENTRE_HALF = 10

#: The sheets the sweep found on every row: the crop sheet the extractor
#: used, and the sheet the point lies on.
EXPECTED_CROP_SHEET = "K-35-052-4_32635"
EXPECTED_FIX_SHEET = "K-35-053-3_Elenovo"

#: Gold-standard reference mounds, for the near-mound summary.
GS_REFERENCE = "inputs/vectors/references/mounds-reference.geojson"

#: Distance (m) for "near a gold-standard mound", as the sweep used.
NEAR_M = 20.0


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def rel(path: Path, root: Path = PROJECT_ROOT) -> str:
    """*path* relative to *root* when it lies inside it."""
    try:
        return str(Path(path).resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def map_name(tile: str) -> str:
    """The sheet name of a tile id, as ``extract_candidates`` derives it."""
    from scripts.extract_candidates import tile_id_to_map_name

    return tile_id_to_map_name(tile)


def dark_shares(img: np.ndarray) -> tuple[float, float]:
    """(whole-crop, central 21 x 21 window) share of pure-black pixels.

    Args:
        img: An H x W x 3 uint8 array.

    Returns:
        Two shares in [0, 1], rounded to six places as the sweep wrote them.
    """
    blk = img.max(axis=2) == 0
    h, w = blk.shape
    c = blk[h // 2 - CENTRE_HALF:h // 2 + CENTRE_HALF + 1,
            w // 2 - CENTRE_HALF:w // 2 + CENTRE_HALF + 1]
    return round(float(blk.mean()), 6), round(float(c.mean()), 6)


def pixels(path: Path) -> np.ndarray:
    """A PNG's pixels as an RGB uint8 array."""
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"))


def pixel_sha256(arr: np.ndarray) -> str:
    """SHA-256 of an array's shape and bytes, so equal pixels hash equal."""
    return sha256_bytes(repr(arr.shape).encode() + arr.tobytes())


def job_slug(model: str, temperature: float, thinking: str) -> str:
    """A job directory name, e.g. ``gemini-3.7-flash_t0.0_low``."""
    return f"{model}_t{float(temperature):.1f}_{str(thinking).lower()}"


def crop_set_slug(manifest_rel: str) -> str:
    """The sweep's slug for a manifest: its directory with ``/`` as ``__``."""
    return manifest_rel.removesuffix("/candidate_manifest.json").replace("/", "__")


def usage_per_call(meta: dict[str, Any], n_results: int) -> dict[str, float]:
    """A leg's mean billed tokens per request, from its ``run.meta.json``.

    The divisor is the number of requests the usage covers: the batch path's
    ``n_responses_with_usage``, else the real-time path's request count,
    else the items processed, else the number of results.

    Args:
        meta: The leg's run meta.
        n_results: The leg's number of results.

    Returns:
        ``{"input", "cached", "output", "thoughts", "divisor"}``.
    """
    u = meta.get("usage_stats") or {}
    bu = (meta.get("results_summary") or {}).get("batch_usage") or {}
    prov = (u.get("by_provider") or {}).get("google_gemini") or {}
    items = (meta.get("execution_stats") or {}).get("items_processed")
    div = (bu.get("n_responses_with_usage") or prov.get("request_count") or items
           or n_results or 1)
    return {"input": (u.get("total_input_tokens") or 0) / div,
            "cached": (u.get("total_cached_tokens") or 0) / div,
            "output": (u.get("total_output_tokens") or 0) / div,
            "thoughts": (u.get("total_thoughts_tokens") or 0) / div,
            "divisor": div}


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def load_selection(path: Path) -> list[dict[str, str]]:
    """The sweep's wrong-sheet rows under ``outputs/``."""
    with open(path, newline="") as fh:
        return [r for r in csv.DictReader(fh) if r["leg"].startswith("outputs/")]


def select_legs(rows: list[dict[str, str]]) -> tuple[dict[str, list[int]], dict[str, str]]:
    """The legs to send for, and which repaired legs ride on a sibling.

    Args:
        rows: The selection's rows.

    Returns:
        ``(sent, riders)``: ``leg -> sorted candidate ids`` for every leg
        whose calls are sent, and ``repaired leg -> sibling`` for each
        ``_repaired`` leg whose sibling is sent.

    Raises:
        Refused: When a repaired leg's candidates differ from its sibling's.
    """
    by_leg: dict[str, set[int]] = defaultdict(set)
    for r in rows:
        by_leg[r["leg"]].add(int(r["candidate_id"]))
    sent: dict[str, list[int]] = {}
    riders: dict[str, str] = {}
    for leg in sorted(by_leg):
        sib = leg.removesuffix("_repaired")
        if leg != sib and sib in by_leg:
            if by_leg[leg] != by_leg[sib]:
                raise Refused(f"{leg} names candidates {sorted(by_leg[leg] ^ by_leg[sib])} "
                              f"that its sibling {sib} does not, or the reverse")
            riders[leg] = sib
            continue
        sent[leg] = sorted(by_leg[leg])
    return sent, riders


def leg_setting(repo: Path, leg: str) -> dict[str, Any]:
    """A leg's verifier configuration as it ran, from its committed files.

    Args:
        repo: The repository (clone) root.
        leg: The leg directory, relative to *repo*.

    Returns:
        ``{"model", "verifier_config", "temperature", "thinking_level",
        "configuration", "meta", "probs"}``.

    Raises:
        Refused: When the leg is not a single-pass leg or its files disagree.
    """
    d = repo / leg
    probs = json.loads((d / "probabilities.json").read_text())
    meta = json.loads((d / "run.meta.json").read_text())
    conf = meta["configuration"]
    if int(probs.get("iterations") or 1) != 1:
        raise Refused(f"{leg}: iterations {probs.get('iterations')}; single-pass legs only")
    if probs.get("verifier_config") != conf.get("version"):
        raise Refused(f"{leg}: probabilities.json verifier_config "
                      f"{probs.get('verifier_config')!r} != run.meta.json version "
                      f"{conf.get('version')!r}")
    snap = conf.get("full_config_snapshot") or {}
    if not snap:
        raise Refused(f"{leg}: run.meta.json has no full_config_snapshot")
    return {"model": conf["model"], "verifier_config": probs["verifier_config"],
            "temperature": float(conf["temperature"]),
            "thinking_level": str(conf["thinking_level"]).lower(),
            "configuration": conf, "meta": meta, "probs": probs}


def cut_crop(raster: Path, x: float, y: float, padding: int, out: Path) -> None:
    """Cut one crop with the project's extractor, or refuse."""
    from scripts.extract_candidates import crop_region

    if not crop_region(raster, (x, y), padding, out):
        raise Refused(f"crop_region failed for ({x}, {y}) on {raster}")


def resolve_sheet_raster(sheet_or_tile: str, rasters_dir: Path) -> Path:
    """The raster the extractor resolves for a tile id or a bare sheet name."""
    from scripts.extract_candidates import resolve_raster_path

    tile = sheet_or_tile if "_x" in sheet_or_tile else f"{sheet_or_tile}_x0_y0.png"
    found = resolve_raster_path(tile, rasters_dir)
    if found is None:
        raise Refused(f"no raster for {sheet_or_tile} under {rasters_dir}")
    return found


def check_crop(entry: dict[str, Any], csv_row: dict[str, str], *, crops_base: Path,
               rasters_dir: Path, out_png: Path, sample: Path | None) -> dict[str, Any]:
    """Re-cut the old crop, cut the corrected one, and measure both.

    Args:
        entry: The candidate's manifest entry.
        csv_row: One of the selection's rows for this candidate.
        crops_base: The manifest's directory in the data root.
        rasters_dir: The data root's rasters directory.
        out_png: Where the corrected crop is written.
        sample: The sweep's corrected sample for this candidate, if kept.

    Returns:
        The crop provenance block.

    Raises:
        Refused: On any disagreement.
    """
    cid = int(entry["candidate_id"])
    x, y = float(entry["centroid_x"]), float(entry["centroid_y"])
    if abs(x - float(csv_row["x"])) > 1e-5 or abs(y - float(csv_row["y"])) > 1e-5:
        raise Refused(f"candidate {cid}: manifest centroid ({x}, {y}) differs from the "
                      f"selection's ({csv_row['x']}, {csv_row['y']})")
    sheet = map_name(entry["source_tile"])
    if sheet != csv_row["crop_sheet"] or sheet != EXPECTED_CROP_SHEET:
        raise Refused(f"candidate {cid}: source tile sheet {sheet} is not the selection's "
                      f"{csv_row['crop_sheet']}")
    fix_sheet = csv_row["fix_sheet"]
    if fix_sheet != EXPECTED_FIX_SHEET:
        raise Refused(f"candidate {cid}: fix sheet {fix_sheet}, expected {EXPECTED_FIX_SHEET}")
    padding = int(entry.get("_padding") or 75)
    old_raster = resolve_sheet_raster(entry["source_tile"], rasters_dir)
    fix_raster = resolve_sheet_raster(fix_sheet, rasters_dir)
    old_png = crops_base / entry["crop_file"]
    with tempfile.TemporaryDirectory() as tmp:
        recut = Path(tmp) / "recut.png"
        cut_crop(old_raster, x, y, padding, recut)
        recut_px = pixels(recut)
        recut_bytes_sha = sha256_file(recut)
    # One crop set (the Gemini 3.7 image GS K3 crops) kept no PNGs; there the
    # crop the leg was shown is the re-cut, as the sweep measured it.
    retained = old_png.is_file()
    old_px = pixels(old_png) if retained else recut_px
    if retained and (old_px.shape != recut_px.shape or not np.array_equal(old_px, recut_px)):
        raise Refused(f"candidate {cid}: the extractor's re-cut of {old_png} from "
                      f"{old_raster.name} differs from it")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cut_crop(fix_raster, x, y, padding, out_png)
    new_px = pixels(out_png)
    old_dark, old_cdark = dark_shares(old_px)
    new_dark, new_cdark = dark_shares(new_px)
    if abs(old_dark - float(csv_row["dark_as_verified"])) > 1e-6:
        raise Refused(f"candidate {cid}: dark share {old_dark} differs from the sweep's "
                      f"{csv_row['dark_as_verified']}")
    if abs(new_dark - float(csv_row["fix_dark"])) > 1e-6:
        raise Refused(f"candidate {cid}: corrected dark share {new_dark} differs from the "
                      f"sweep's {csv_row['fix_dark']}")
    sample_check = None
    if sample is not None and sample.is_file():
        sp = pixels(sample)
        sample_check = bool(sp.shape == new_px.shape and np.array_equal(sp, new_px))
        if not sample_check:
            raise Refused(f"candidate {cid}: corrected crop differs from the sweep's "
                          f"independent cut {sample}")
    return {
        "centroid": [x, y], "padding": padding,
        "old": {"png": entry["crop_file"], "png_retained": retained,
                "sha256": sha256_file(old_png) if retained else None,
                "recut_sha256": recut_bytes_sha,
                "pixels_sha256": pixel_sha256(old_px), "raster": old_raster.name,
                "sheet": sheet, "dark_share": old_dark, "centre_dark_share": old_cdark,
                "recut_equal_pixels": True if retained else None,
                "recut_equal_bytes": (recut_bytes_sha == sha256_file(old_png)
                                      if retained else None)},
        "new": {"sha256": sha256_file(out_png), "pixels_sha256": pixel_sha256(new_px),
                "raster": fix_raster.name, "sheet": fix_sheet, "dark_share": new_dark,
                "centre_dark_share": new_cdark,
                "equals_sweep_sample": sample_check},
    }


def build_request(entry: dict[str, Any], crop_rel: str, crops_root: Path,
                  setting: dict[str, Any]) -> dict[str, Any]:
    """One request line from the batch builder, with the leg's configuration.

    Args:
        entry: The candidate's manifest entry.
        crop_rel: The crop's path under *crops_root*.
        crops_root: Base directory for ``crop_file``.
        setting: The leg's :func:`leg_setting`.

    Returns:
        The parsed line ``lib_verifier.build_verifier_jsonl`` writes.
    """
    from scripts.lib_verifier import build_verifier_jsonl

    conf = setting["configuration"]
    config = dict(conf["full_config_snapshot"])
    config["thinking_level"] = conf.get("thinking_level")
    cand = {k: v for k, v in entry.items() if not k.startswith("_")}
    cand["crop_file"] = crop_rel
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "line.jsonl"
        n = build_verifier_jsonl(manifest={"candidates": [cand]}, config=config,
                                 output_path=out, crops_base_dir=crops_root,
                                 temperature_override=conf.get("temperature"))
        if n != 1:
            raise Refused(f"builder wrote {n} lines for candidate {entry['candidate_id']}")
        return json.loads(out.read_text().splitlines()[0])


def line_image_b64(line: dict[str, Any]) -> list[str]:
    """The base64 image payloads of a request line, in order."""
    parts = line["request"]["contents"][0]["parts"]
    return [p["inline_data"]["data"] for p in parts if "inline_data" in p]


def estimate_job(legs: list[tuple[dict[str, float], int]], model: str, at: str) -> dict:
    """Price a job at each leg's own mean usage per call, batch tier."""
    from scripts.lib_cost import price_usage

    tot = {"total_input_tokens": 0.0, "total_cached_tokens": 0.0,
           "total_output_tokens": 0.0, "total_thoughts_tokens": 0.0}
    n = 0
    for per, k in legs:
        n += k
        tot["total_input_tokens"] += per["input"] * k
        tot["total_cached_tokens"] += per["cached"] * k
        tot["total_output_tokens"] += per["output"] * k
        tot["total_thoughts_tokens"] += per["thoughts"] * k
    usage = {f: int(round(v)) for f, v in tot.items()}
    usage["n_responses_with_usage"] = n
    return price_usage(usage, model=model, tier=TIER, at=at,
                       tier_source="estimate: each leg's mean usage per call")


def build(*, repo: Path, data_root: Path, selection: Path, pairing: Path, out_dir: Path,
          expect_calls: int, tolerance: float, max_cost_usd: float,
          sample_root: Path | None = None, at: str | None = None) -> dict[str, Any]:
    """Cut the corrected crops and build one request file per configuration.

    Args:
        repo: The repository (clone) root: committed legs and manifests.
        data_root: The checkout holding the untracked crops, rasters and
            surviving request files (may equal *repo*).
        selection: The sweep's ``wrong_sheet.csv``.
        pairing: The sweep's ``legs.json`` (leg -> manifest).
        out_dir: The run directory; must be absent or hold only ``inputs/``.
        expect_calls: The approved number of calls.
        tolerance: The relative difference allowed from *expect_calls*.
        max_cost_usd: The estimate's ceiling.
        sample_root: The sweep's ``corrected-sample`` directory, for an
            independent check of the corrected crops (optional).
        at: Pricing date (default: today, UTC).

    Returns:
        The build record (also written as ``build.json``).

    Raises:
        Refused: On any failed gate. Files written before a refusal stay in
        *out_dir* for inspection; nothing is sent.
    """
    at = at or datetime.now(timezone.utc).date().isoformat()
    # Only an ``inputs/`` directory (the selection and pairing copied in for
    # provenance) may be there already.
    if out_dir.exists() and any(p.name != "inputs" for p in out_dir.iterdir()):
        raise Refused(f"{out_dir} is not empty; a build is never overwritten")
    rows = load_selection(selection)
    pair = json.loads(pairing.read_text())
    sent, riders = select_legs(rows)
    by_key = {(r["leg"], int(r["candidate_id"])): r for r in rows}
    out_dir.mkdir(parents=True, exist_ok=True)
    crops_root = out_dir / "crops"
    crop_cache: dict[tuple[str, int], dict[str, Any]] = {}
    jobs: dict[str, dict[str, Any]] = {}
    leg_records: list[dict[str, Any]] = []
    out_rows: list[dict[str, Any]] = []
    for idx, leg in enumerate(sorted(sent)):
        tag = f"L{idx:02d}"
        setting = leg_setting(repo, leg)
        man_rel = (pair.get(leg) or {}).get("manifest")
        if not man_rel:
            raise Refused(f"{leg}: the pairing names no manifest")
        manifest = json.loads((repo / man_rel).read_text())
        data_man = data_root / man_rel
        if data_man.resolve() != (repo / man_rel).resolve() and \
                sha256_file(data_man) != sha256_file(repo / man_rel):
            raise Refused(f"{man_rel}: the data root's copy differs from the repository's")
        man_ids = {int(c["candidate_id"]) for c in manifest["candidates"]}
        prob_ids = {int(k.rsplit("_", 1)[1]) for k in setting["probs"]["results"]}
        if man_ids != prob_ids:
            raise Refused(f"{leg}: its {len(prob_ids)} result ids are not the "
                          f"{len(man_ids)} candidate ids of {man_rel}")
        entries = {int(c["candidate_id"]): c for c in manifest["candidates"]}
        # The canonical rasters, whatever directory the manifest recorded (one
        # names a worktree long gone); the old crop's pixel-for-pixel re-cut
        # in check_crop is what proves the raster is the one the leg used.
        rasters_dir = data_root / "inputs" / "rasters"
        slug = crop_set_slug(man_rel)
        per = usage_per_call(setting["meta"], len(setting["probs"]["results"]))
        req_files = request_files(data_root / leg)
        originals = (find_request_lines(req_files, {f"candidate_{c:05d}" for c in sent[leg]})
                     if req_files else {})
        jkey = job_slug(setting["model"], setting["temperature"], setting["thinking_level"])
        job = jobs.setdefault(jkey, {
            "model": setting["model"], "temperature": setting["temperature"],
            "thinking_level": setting["thinking_level"],
            "verifier_config": setting["verifier_config"], "lines": [], "legs": [],
            "usage": []})
        if job["verifier_config"] != setting["verifier_config"]:
            raise Refused(f"{leg}: prompt configuration {setting['verifier_config']} in a job "
                          f"for {job['verifier_config']}")
        for cid in sent[leg]:
            key = f"candidate_{cid:05d}"
            if key not in setting["probs"]["results"]:
                raise Refused(f"{leg}: {key} is not in its probabilities.json")
            entry = dict(entries[cid])
            entry["_padding"] = manifest.get("padding") or 75
            ck = (man_rel, cid)
            if ck not in crop_cache:
                sample = (sample_root / slug / f"candidate_{cid:05d}_fixed.png"
                          if sample_root else None)
                crop_cache[ck] = check_crop(
                    entry, by_key[(leg, cid)], crops_base=data_man.parent,
                    rasters_dir=rasters_dir, out_png=crops_root / slug / f"{key}.png",
                    sample=sample)
            prov = crop_cache[ck]
            line = build_request(entry, f"{slug}/{key}.png", crops_root, setting)
            if line["key"] != key:
                raise Refused(f"{leg}: builder key {line['key']} != {key}")
            problems = audit_line(line, setting["configuration"])
            if problems:
                raise Refused(f"{leg} {key}: request disagrees with run.meta.json: {problems}")
            imgs = line_image_b64(line)
            new_bytes = (crops_root / slug / f"{key}.png").read_bytes()
            if imgs != [base64.b64encode(new_bytes).decode("ascii")]:
                raise Refused(f"{leg} {key}: the request does not carry the corrected crop")
            fidelity: dict[str, Any] = {"checked": False}
            hits = originals.get(key) or []
            if hits:
                bodies = {b for _, b in hits}
                if len(bodies) != 1:
                    raise Refused(f"{leg} {key}: {len(bodies)} distinct original lines")
                orig = build_request(entry, entry["crop_file"], data_man.parent, setting)
                same = json.dumps(orig).encode() == hits[0][1]
                fidelity = {"checked": True, "request_file": rel(hits[0][0], data_root),
                            "original_line_sha256": sha256_bytes(hits[0][1]),
                            "rebuilt_identical_bytes": same}
                if not same:
                    raise Refused(f"{leg} {key}: today's builder does not reproduce the "
                                  "leg's original request line for the original crop")
            line["key"] = f"{tag}__{key}"
            body = json.dumps(line).encode()
            job["lines"].append(body)
            out_rows.append({
                "leg": leg, "leg_tag": tag, "key": key, "request_key": line["key"],
                "candidate_id": cid, "job": jkey, "manifest": man_rel,
                "crop_rel": f"crops/{slug}/{key}.png", "old_probability":
                    setting["probs"]["results"][key].get("mound_probability"),
                "votes": entry.get("properties", {}).get("vote_count"),
                "request_line_sha256": sha256_bytes(body), "original_request": fidelity,
                "crop": prov})
        job["legs"].append(leg)
        job["usage"].append((per, len(sent[leg])))
        leg_records.append({
            "leg": leg, "tag": tag, "manifest": man_rel, "job": jkey,
            "model": setting["model"], "temperature": setting["temperature"],
            "thinking_level": setting["thinking_level"],
            "verifier_config": setting["verifier_config"],
            "mode_as_run": setting["probs"].get("mode"),
            "system_instruction_hash": setting["configuration"].get("system_instruction_hash"),
            "n_results": len(setting["probs"]["results"]), "n_rows": len(sent[leg]),
            "candidate_ids": sent[leg], "usage_per_call": per,
            "riders": sorted(r for r, s in riders.items() if s == leg),
            "request_files_found": [rel(p, data_root) for p in req_files]})
    n_calls = sum(len(j["lines"]) for j in jobs.values())
    if abs(n_calls - expect_calls) > tolerance * expect_calls:
        raise Refused(f"{n_calls} calls built; approved {expect_calls} within "
                      f"{tolerance:.0%}")
    job_records: dict[str, Any] = {}
    total = 0.0
    for jkey, job in sorted(jobs.items()):
        jdir = out_dir / "jobs" / jkey
        jdir.mkdir(parents=True, exist_ok=True)
        req = jdir / "verifier_requests.jsonl"
        req.write_bytes(b"".join(b + b"\n" for b in job["lines"]))
        est = estimate_job(job["usage"], job["model"], at)
        total += est["total_cost_usd"] or 0.0
        job_records[jkey] = {
            "model": job["model"], "temperature": job["temperature"],
            "thinking_level": job["thinking_level"], "verifier_config": job["verifier_config"],
            "n_requests": len(job["lines"]), "n_legs": len(job["legs"]), "legs": job["legs"],
            "requests": {"path": rel(req, out_dir), "sha256": sha256_file(req),
                         "bytes": req.stat().st_size},
            "estimate": est}
    if total > max_cost_usd:
        raise Refused(f"estimate US${total:.4f} exceeds the US${max_cost_usd} ceiling")
    record = {
        "script": "scripts/reverify_wrong_sheet_crops.py build",
        "script_sha256": sha256_file(Path(__file__)),
        "decision": DECISION, "built_at": datetime.now(timezone.utc).isoformat(),
        "tier": TIER, "priced_at": at,
        "inputs": {"selection": str(selection), "selection_sha256": sha256_file(selection),
                   "pairing": str(pairing), "pairing_sha256": sha256_file(pairing),
                   "repo": str(repo), "data_root": str(data_root),
                   "sample_root": str(sample_root) if sample_root else None},
        "n_selection_rows": len(rows), "n_legs_sent": len(sent),
        "riders": riders, "n_calls": n_calls, "expect_calls": expect_calls,
        "n_distinct_crops": len(crop_cache),
        "estimate_usd": round(total, 6), "max_cost_usd": max_cost_usd,
        "jobs": job_records, "legs": leg_records, "rows": out_rows,
    }
    (out_dir / "build.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


# ---------------------------------------------------------------------------
# lodge
# ---------------------------------------------------------------------------


def lodge(run_dir: Path, client: Any, max_cost_usd: float, *,
          resolve_model: Callable[[Any, str], str | None],
          preflight: Callable[..., Any], upload: Callable[..., str],
          submit: Callable[..., Any], poll: Callable[..., Any],
          retrieve: Callable[[Any, Any], list[dict]],
          state_name: Callable[[Any], str]) -> int:
    """Lodge every job, then poll each to a terminal state.

    All jobs are lodged before the first is polled, so the run waits once
    for the slowest. The lifecycle functions are injected so the gates are
    testable without an API; :func:`main` passes ``lib_batch_api``'s.

    Returns:
        0 when every job SUCCEEDED and every key came back, 2 otherwise.

    Raises:
        Refused: Before any upload, when a gate fails.
    """
    build_rec = json.loads((run_dir / "build.json").read_text())
    if build_rec["estimate_usd"] > max_cost_usd:
        raise Refused(f"estimate US${build_rec['estimate_usd']} exceeds the "
                      f"US${max_cost_usd} ceiling")
    paths: dict[str, Path] = {}
    keys: dict[str, list[str]] = {}
    for jkey, job in sorted(build_rec["jobs"].items()):
        jdir = run_dir / "jobs" / jkey
        if (jdir / "batch_jobs.json").exists():
            raise Refused(f"{jdir / 'batch_jobs.json'} exists: this run has lodged "
                          "already, and a second batch is a new approval")
        req = run_dir / job["requests"]["path"]
        if sha256_file(req) != job["requests"]["sha256"]:
            raise Refused(f"{req} has changed since build")
        ks = [json.loads(line)["key"] for line in req.read_text().splitlines()]
        if len(ks) != job["n_requests"] or len(set(ks)) != len(ks):
            raise Refused(f"{req}: {len(ks)} lines ({len(set(ks))} keys); build recorded "
                          f"{job['n_requests']}")
        resolved = resolve_model(client, job["model"])
        if resolved != job["model"]:
            raise Refused(f"model {job['model']!r} resolves to {resolved!r}")
        paths[jkey], keys[jkey] = req, ks
    total = sum(len(v) for v in keys.values())
    if total != build_rec["n_calls"]:
        raise Refused(f"{total} requests on disk; build recorded {build_rec['n_calls']}")
    # No sweep: this run may delete only its own files.
    try:
        preflight(client, list(paths.values()), log=logger, sweep=None)
    except Exception as exc:  # noqa: BLE001 - any preflight failure stops the lodge
        raise Refused(f"File API storage preflight: {exc}") from exc

    stamp = datetime.now(timezone.utc)
    records: dict[str, dict[str, Any]] = {}
    jobs_live: dict[str, Any] = {}

    def save(jkey: str) -> None:
        (run_dir / "jobs" / jkey / "batch_jobs.json").write_text(
            json.dumps(records[jkey], indent=1) + "\n")

    for i, jkey in enumerate(sorted(paths)):
        job = build_rec["jobs"][jkey]
        records[jkey] = {
            "display_name": f"pv-verifier-wrongsheet-{stamp:%Y%m%d-%H%M}-j{i}",
            "model": job["model"], "tier": TIER, "requests": job["requests"]["path"],
            "requests_sha256": job["requests"]["sha256"], "n_requests": len(keys[jkey]),
            "file": None, "job": None, "state": "not lodged"}
        save(jkey)
        try:
            records[jkey]["file"] = upload(client, paths[jkey], records[jkey]["display_name"])
            records[jkey]["state"] = "uploaded"
            save(jkey)
            live = submit(client, job["model"], records[jkey]["file"],
                          records[jkey]["display_name"])
        except Exception as exc:  # noqa: BLE001 - one job must not lose the others
            records[jkey]["state"] = f"lodging failed: {exc}"
            save(jkey)
            print(f"ERROR lodging {jkey}: {exc}", flush=True)
            continue
        records[jkey]["job"] = getattr(live, "name", str(live))
        records[jkey]["state"] = "lodged"
        records[jkey]["lodged_at"] = datetime.now(timezone.utc).isoformat()
        save(jkey)
        jobs_live[jkey] = live
        print(f"Lodged {records[jkey]['job']} ({len(keys[jkey])} requests, "
              f"model {job['model']}, {jkey})", flush=True)

    ok = True
    for jkey in sorted(paths):
        if jkey not in jobs_live:
            ok = False
            continue
        try:
            done = poll(client, records[jkey]["job"])
        except Exception as exc:  # noqa: BLE001 - record and keep the others
            records[jkey]["state"] = f"lost while polling: {exc}"
            save(jkey)
            print(f"ERROR polling {jkey}: {exc}", flush=True)
            ok = False
            continue
        state = state_name(getattr(done, "state", ""))
        records[jkey]["state"] = state
        records[jkey]["terminal_at"] = datetime.now(timezone.utc).isoformat()
        dest = getattr(done, "dest", None)
        records[jkey]["output_file"] = getattr(dest, "file_name", None) if dest else None
        save(jkey)
        rows: list[dict] = []
        if records[jkey]["output_file"]:
            rows = retrieve(client, done)
            with open(run_dir / "jobs" / jkey / "batch_results.jsonl", "w") as fh:
                for row in rows:
                    fh.write(json.dumps(row) + "\n")
        returned = {r.get("key") for r in rows if "error" not in r}
        missing = sorted(set(keys[jkey]) - returned)
        records[jkey]["n_results"] = len(rows)
        records[jkey]["missing_or_errored"] = missing
        save(jkey)
        print(f"{jkey}: {state}, {len(rows)}/{len(keys[jkey])} rows, "
              f"{len(missing)} missing or errored", flush=True)
        if state != "JOB_STATE_SUCCEEDED" or missing:
            ok = False
    if ok:
        print(f"{MARKER_COMPLETE}: {total}/{total} rows in {len(paths)} jobs", flush=True)
        return 0
    print(f"{MARKER_PARTIAL}: see jobs/*/batch_jobs.json. Nothing was re-sent: a resend "
          "needs a new approval.", flush=True)
    return 2


# ---------------------------------------------------------------------------
# book
# ---------------------------------------------------------------------------


def book(run_dir: Path, repo: Path = PROJECT_ROOT, date_tag: str | None = None) -> int:
    """Merge every answer into its leg's repaired copy, and its riders' record.

    The base of each repaired copy is the committed ``<leg>_repaired/``
    when one exists (its parse repairs stay), else the leg itself, copied:
    ``probabilities.json`` re-written with the answers merged and
    ``run.meta.json`` as a byte copy. Only the re-verified rows change.

    Args:
        run_dir: The run directory.
        repo: The repository root the legs are under.
        date_tag: Suffix of the per-leg record name (default: the last job's
            terminal date).

    Returns:
        0 when every answer was booked; 1 when any is unparseable (that row is
        REMOVED from the repaired copy, so scoring refuses until it is
        re-verified, and it is not re-sent).

    Raises:
        Refused: When a job is not complete or a repaired copy already holds
        this record.
    """
    from scripts.lib_batch_api import aggregate_batch_usage
    from scripts.lib_cost import price_usage

    build_rec = json.loads((run_dir / "build.json").read_text())
    raw: dict[str, dict] = {}
    terminal: list[str] = []
    jobs_meta: dict[str, dict] = {}
    for jkey in sorted(build_rec["jobs"]):
        jdir = run_dir / "jobs" / jkey
        jm = json.loads((jdir / "batch_jobs.json").read_text())
        jobs_meta[jkey] = jm
        terminal.append((jm.get("terminal_at") or "")[:10])
        path = jdir / "batch_results.jsonl"
        if not path.is_file():
            raise Refused(f"{jkey}: no batch_results.jsonl")
        for line in path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                raw[row["key"]] = row
    priced_at = max(t for t in terminal if t) if any(terminal) else \
        datetime.now(timezone.utc).date().isoformat()
    tag = date_tag or priced_at
    rec_name = f"reverify-wrong-sheet-{tag}.json"
    rows_out: list[dict[str, Any]] = []
    for r in build_rec["rows"]:
        job = build_rec["jobs"][r["job"]]
        result = raw.get(r["request_key"])
        text = _response_text(result or {})
        usage = aggregate_batch_usage([result] if result else [])
        cost = price_usage(usage, model=job["model"], tier=TIER, at=priced_at,
                           tier_source="batch-api (reverify_wrong_sheet_crops.py lodge)")
        out = {k: r[k] for k in ("leg", "leg_tag", "key", "request_key", "candidate_id",
                                 "job", "manifest", "crop_rel", "old_probability", "votes")}
        out.update(batch_job=jobs_meta[r["job"]].get("job"), new_response_text=text,
                   new_finish_reason=(((result or {}).get("response") or {})
                                      .get("candidates") or [{}])[0].get("finishReason"),
                   usage_metadata=((result or {}).get("response") or {}).get("usageMetadata"),
                   cost_usd=cost["total_cost_usd"],
                   tokens_billed=cost.get("tokens_billed"), crop=r["crop"])
        try:
            verdict, method = parse_new_response(text)
        except (ValueError, TypeError) as exc:
            out.update(new_probability=None, booked=False, parse_error=str(exc))
        else:
            out.update(new_probability=verdict["mound_probability"], parse_method=method,
                       booked=True, verdict=verdict)
        rows_out.append(out)

    by_leg: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for o in rows_out:
        by_leg[o["leg"]].append(o)
    for leg_rec in build_rec["legs"]:
        done = (repo / (leg_rec["leg"] + "_repaired")) / rec_name
        if done.exists():
            raise Refused(f"{done} exists: already booked; nothing written")
    leg_records: list[dict[str, Any]] = []
    for leg_rec in build_rec["legs"]:
        leg = leg_rec["leg"]
        leg_dir = repo / leg
        rep_dir = leg_dir.with_name(leg_dir.name + "_repaired")
        if (rep_dir / "probabilities.json").is_file():
            base = "repaired copy"
        else:
            base = "leg"
            rep_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(leg_dir / "run.meta.json", rep_dir / "run.meta.json")
            shutil.copyfile(leg_dir / "probabilities.json", rep_dir / "probabilities.json")
        probs_path = rep_dir / "probabilities.json"
        before = sha256_file(probs_path)
        probs = json.loads(probs_path.read_text())
        merged, removed, absent_before = [], [], []
        for o in by_leg[leg]:
            if o["key"] not in probs["results"]:
                absent_before.append(o["key"])
            if o["booked"]:
                probs["results"][o["key"]] = dict(o["verdict"])
                merged.append(o)
            else:
                probs["results"].pop(o["key"], None)
                removed.append(o["key"])
        if "total_results" in probs:
            probs["total_results"] = len(probs["results"])
        probs[BLOCK_KEY] = {"record": rec_name, "n_merged": len(merged),
                            "keys": [o["key"] for o in merged], "removed_unparseable": removed,
                            "source": rel(run_dir, repo), "decision": DECISION,
                            "base": base}
        probs_path.write_text(json.dumps(probs, indent=2) + "\n")
        per_leg = {
            "script": "scripts/reverify_wrong_sheet_crops.py book", "decision": DECISION,
            "leg_dir": leg, "run_dir": rel(run_dir, repo), "base": base,
            "riders": leg_rec["riders"],
            "batch_job": jobs_meta[leg_rec["job"]].get("job"), "job": leg_rec["job"],
            "model": leg_rec["model"], "temperature": leg_rec["temperature"],
            "thinking_level": leg_rec["thinking_level"], "tier": TIER,
            "probabilities_sha256_before": before,
            "probabilities_sha256_after": sha256_file(probs_path),
            "rows": [{"key": o["key"], "old_probability": o["old_probability"],
                      "new_probability": o["new_probability"],
                      "parse_method": o.get("parse_method"), "cost_usd": o["cost_usd"],
                      "old_crop_dark_share": o["crop"]["old"]["dark_share"],
                      "old_crop_raster": o["crop"]["old"]["raster"],
                      "new_crop_dark_share": o["crop"]["new"]["dark_share"],
                      "new_crop_raster": o["crop"]["new"]["raster"],
                      "new_crop": o["crop_rel"], "new_crop_sha256": o["crop"]["new"]["sha256"]}
                     for o in merged],
            "removed_unparseable": removed, "absent_from_base": absent_before,
            "note": "run.meta.json here is the leg's byte copy (or the committed repaired "
                    "copy's); the calls' usage and cost are in the run directory's record.json",
        }
        (rep_dir / rec_name).write_text(json.dumps(per_leg, indent=1) + "\n")
        leg_records.append({k: per_leg[k] for k in (
            "leg_dir", "base", "riders", "job", "probabilities_sha256_before",
            "probabilities_sha256_after", "removed_unparseable", "absent_from_base")}
            | {"n_merged": len(merged)})

    by_job: dict[str, dict[str, Any]] = {}
    for jkey, job in sorted(build_rec["jobs"].items()):
        mine = [o for o in rows_out if o["job"] == jkey]
        usage = aggregate_batch_usage([raw[o["request_key"]] for o in mine
                                       if o["request_key"] in raw])
        by_job[jkey] = {
            "batch_job": jobs_meta[jkey].get("job"), "state": jobs_meta[jkey].get("state"),
            "model": job["model"], "temperature": job["temperature"],
            "thinking_level": job["thinking_level"], "n_requests": job["n_requests"],
            "n_results": jobs_meta[jkey].get("n_results"),
            "n_booked": sum(o["booked"] for o in mine),
            "tokens": {k: usage[k] for k in ("total_input_tokens", "total_cached_tokens",
                                             "total_output_tokens", "total_thoughts_tokens")},
            "audited_cost_usd": round(sum(o["cost_usd"] or 0.0 for o in mine), 6),
            "priced_on_job_totals": price_usage(
                usage, model=job["model"], tier=TIER, at=priced_at,
                tier_source="batch-api (reverify_wrong_sheet_crops.py lodge)"),
            "estimate_usd": job["estimate"]["total_cost_usd"]}
    unparseable = [o for o in rows_out if not o["booked"]]
    record = {
        "script": "scripts/reverify_wrong_sheet_crops.py book", "decision": DECISION,
        "booked_at": datetime.now(timezone.utc).isoformat(), "tier": TIER,
        "priced_at": priced_at,
        "batch_results_sha256": {j: sha256_file(run_dir / "jobs" / j / "batch_results.jsonl")
                                 for j in sorted(build_rec["jobs"])},
        "n_rows": len(rows_out), "n_booked": len(rows_out) - len(unparseable),
        "n_unparseable": len(unparseable),
        "total_cost_usd": round(sum(o["cost_usd"] or 0.0 for o in rows_out), 6),
        "estimate_usd": build_rec["estimate_usd"], "jobs": by_job, "legs": leg_records,
        "rows": rows_out,
    }
    (run_dir / "record.json").write_text(json.dumps(record, indent=1) + "\n")
    for jkey, j in by_job.items():
        print(f"  {jkey}: {j['n_booked']}/{j['n_requests']} booked, "
              f"US${j['audited_cost_usd']} (estimate US${j['estimate_usd']})")
    print(f"Total US${record['total_cost_usd']} (estimate US${record['estimate_usd']}); "
          f"{len(unparseable)} unparseable")
    return 1 if unparseable else 0


# ---------------------------------------------------------------------------
# release
# ---------------------------------------------------------------------------


def release(run_dir: Path, client: Any, *, state_name: Callable[[Any], str],
            terminal: frozenset[str], delete: Callable[..., tuple[int, int]]) -> int:
    """Delete each terminal job's own input and output files from the Files API.

    Returns:
        0 when every delete went through, 1 otherwise.

    Raises:
        Refused: When any job is not terminal (nothing is deleted then).
    """
    recs: dict[Path, dict] = {}
    for path in sorted((run_dir / "jobs").glob("*/batch_jobs.json")):
        rec = json.loads(path.read_text())
        if rec.get("job"):
            live = client.batches.get(name=rec["job"])
            state = state_name(getattr(live, "state", ""))
            if state not in terminal:
                raise Refused(f"job {rec['job']} is {state}; nothing is released")
        recs[path] = rec
    bad = 0
    for path, rec in recs.items():
        names = [n for n in (rec.get("file"), rec.get("output_file")) if n]
        deleted, errors = delete(client, names, "reverify-wrong-sheet")
        rec["released"] = {"at": datetime.now(timezone.utc).isoformat(), "files": names,
                           "deleted": deleted, "errors": errors}
        path.write_text(json.dumps(rec, indent=1) + "\n")
        print(f"{path.parent.name}: released {deleted} of {len(names)} file(s) "
              f"({errors} error(s))")
        bad += errors + (len(names) - deleted - errors)
    return 0 if bad == 0 else 1


# ---------------------------------------------------------------------------
# summarise
# ---------------------------------------------------------------------------


def operating_points(repo: Path, leg: str, model: str, union_k: int | None) -> list[dict]:
    """The operating points a leg's answers are scored at.

    Registered conditions (``results/run-conditions.json``) on the leg's
    cell with the leg's verifier model and union size; for a modality-bridge
    leg, its cell's ``analysis.json`` operating point.

    Args:
        repo: The repository root.
        leg: The leg directory.
        model: The leg's verifier model.
        union_k: The passes in the leg's union (from its manifest), if known.

    Returns:
        ``[{"source", "label", "prob_t", "min_votes"}]``, possibly empty.
    """
    parts = leg.split("/")
    run = parts[1]
    if run.startswith("modality-bridge"):
        arm, leaf = parts[2], parts[-1]
        v = re.match(r"verify_(g37|g3)", leaf)
        if not v:
            return []
        cell = repo / "results" / run / f"{arm}-{v.group(1)}v" / "analysis.json"
        if not cell.is_file():
            return []
        op = json.loads(cell.read_text()).get("operating_point") or {}
        if op.get("prob_t") is None:
            return []  # the T 1.0 cells record no operating point
        return [{"source": rel(cell, repo), "label": cell.parent.name,
                 "prob_t": op.get("prob_t"), "min_votes": op.get("min_votes")}]
    if len(parts) < 4 or parts[2] != "verifier":
        return []
    cell = parts[3]
    rc = json.loads((repo / "results/run-conditions.json").read_text())["decomposition"]
    runrec = rc.get(run, {})
    # The run's verifier cells: a condition whose proposer pool names one of
    # them belongs to that cell only (``g384_ov192_image_high``'s labels
    # begin with ``g384-ov192-image-``); otherwise its label names the cell.
    cells = {str(v.get("path", "")).split("/")[1]
             for v in (runrec.get("verifier_passes") or {}).values()
             if isinstance(v, dict) and str(v.get("path", "")).startswith("verifier/")}
    out = []
    for c in runrec.get("conditions", []):
        if c.get("architecture") != "proposer-verifier":
            continue
        pool = c.get("proposer_pool")
        if pool in cells:
            if pool != cell:
                continue
        elif not c["label"].startswith(cell.replace("_", "-") + "-"):
            continue
        if (c.get("verifier_config") or {}).get("model") != model:
            continue
        if union_k is not None and c.get("n_passes") not in (None, union_k):
            continue
        out.append({"source": f"results/run-conditions.json::{run}::{c['label']}",
                    "label": c["label"], "prob_t": c.get("prob_threshold"),
                    "min_votes": c.get("vote_threshold")})
    return out


def summarise(run_dir: Path, repo: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Per-leg threshold crossings, gold-standard places, and cost by job.

    Returns:
        The summary (also written as ``summary.json``).
    """
    import geopandas as gpd
    from scipy.spatial import cKDTree

    rec = json.loads((run_dir / "record.json").read_text())
    build_rec = json.loads((run_dir / "build.json").read_text())
    g = gpd.read_file(repo / GS_REFERENCE).to_crs("EPSG:32635")
    ref = np.array([[p.centroid.x, p.centroid.y] for p in g.geometry])
    tree = cKDTree(ref)
    legs_out = []
    for leg_rec in build_rec["legs"]:
        leg = leg_rec["leg"]
        rows = [o for o in rec["rows"] if o["leg"] == leg]
        man = json.loads((repo / leg_rec["manifest"]).read_text())
        mk = re.search(r"union_k(\d+)", str(man.get("source_geojson") or ""))
        ops = operating_points(repo, leg, leg_rec["model"], int(mk.group(1)) if mk else None)
        thresholds = sorted({o["prob_t"] for o in ops if o["prob_t"] is not None})
        if not thresholds:
            thresholds = [0.5]
        crossings = {}
        for t in thresholds:
            old = sum((o["old_probability"] or 0) >= t for o in rows)
            new = sum(o["booked"] and o["new_probability"] >= t for o in rows)
            crossings[f"{t:g}"] = {"old_ge": old, "new_ge": new}
        # At each registered operating point (probability AND vote
        # threshold): the rows that enter its scored set before and after.
        at_ops = {}
        for t, v in sorted({(o["prob_t"], o["min_votes"]) for o in ops}):
            def enters(o: dict, p: float | None) -> bool:
                return bool(p is not None and p >= t and (v is None or (o["votes"] or 0) >= v))
            at_ops[f"p{t:g}_k{v}"] = {
                "old": sum(enters(o, o["old_probability"]) for o in rows),
                "new": sum(enters(o, o["new_probability"] if o["booked"] else None)
                           for o in rows)}
        legs_out.append({
            "leg": leg, "job": leg_rec["job"], "n": len(rows),
            "operating_points": ops, "at_operating_points": at_ops,
            "thresholds_used": thresholds if ops else "none registered; 0.5 shown",
            "crossings": crossings,
            "old_max": max((o["old_probability"] or 0) for o in rows),
            "new_max": max((o["new_probability"] or 0) for o in rows if o["booked"]),
            "new_mean": round(float(np.mean([o["new_probability"] for o in rows
                                             if o["booked"]])), 6),
            "changes_nothing": all(c["new_ge"] == c["old_ge"] for c in crossings.values()),
        })
    # Gold-standard places: each row's distance to the nearest reference mound.
    near_rows = []
    for o in rec["rows"]:
        x, y = o["crop"]["centroid"]
        d, i = tree.query([x, y])
        if d <= NEAR_M:
            near_rows.append((int(i), o, round(float(d), 3)))
    by_mound: dict[int, list] = defaultdict(list)
    for i, o, d in near_rows:
        by_mound[i].append((o, d))
    leg_t = {lo["leg"]: lo["thresholds_used"] for lo in legs_out}

    def clears(o: dict) -> bool:
        """Whether a row's answer clears its leg's lowest operating threshold."""
        ts = leg_t[o["leg"]]
        t = ts[0] if isinstance(ts, list) else 0.5
        return bool(o["booked"] and o["new_probability"] >= t)

    mounds = []
    for i, items in sorted(by_mound.items()):
        mounds.append({
            "reference_index": i, "x": round(float(ref[i][0]), 3),
            "y": round(float(ref[i][1]), 3), "n_rows": len(items),
            "n_legs": len({o["leg"] for o, _ in items}),
            "distance_m": [min(d for _, d in items), max(d for _, d in items)],
            "old_max": max((o["old_probability"] or 0) for o, _ in items),
            "new_min": min(o["new_probability"] for o, _ in items if o["booked"]),
            "new_max": max(o["new_probability"] for o, _ in items if o["booked"]),
            "n_rows_clear_leg_threshold": sum(clears(o) for o, _ in items),
            "n_rows_new_ge_0.5": sum(o["booked"] and o["new_probability"] >= 0.5
                                     for o, _ in items)})
    pts: dict[tuple[float, float], list] = {}
    for _, o, _ in near_rows:
        pts.setdefault((round(o["crop"]["centroid"][0], 6),
                        round(o["crop"]["centroid"][1], 6)), []).append(o)
    # "Places": the sweep record counts 275 places and 43 near a mound but
    # keeps no definition; a 10 m grid (coordinates rounded to the nearest
    # 10 m) is the closest reconstruction found, and is labelled as such.
    places: dict[tuple[float, float], list] = defaultdict(list)
    for o in rec["rows"]:
        x, y = o["crop"]["centroid"]
        places[(round(x, -1), round(y, -1))].append(o)
    near_places = {k: v for k, v in places.items()
                   if min(float(tree.query(o["crop"]["centroid"])[0]) for o in v) <= NEAR_M}
    shares = [sum(clears(o) for o in v) / len(v) for v in near_places.values()]
    summary = {
        "script": "scripts/reverify_wrong_sheet_crops.py summarise",
        "record_sha256": sha256_file(run_dir / "record.json"),
        "jobs": rec["jobs"], "total_cost_usd": rec["total_cost_usd"],
        "estimate_usd": rec["estimate_usd"], "legs": legs_out,
        "legs_where_nothing_changes": [lo["leg"] for lo in legs_out if lo["changes_nothing"]],
        "near_gs": {"radius_m": NEAR_M, "reference": GS_REFERENCE,
                    "n_rows": len(near_rows), "n_distinct_points": len(pts),
                    "n_distinct_crops": len({(o["manifest"], o["candidate_id"])
                                             for _, o, _ in near_rows}),
                    "n_reference_mounds": len(by_mound), "mounds": mounds,
                    "places_10m_grid": {
                        "definition": "rows grouped by centroid rounded to the nearest 10 m; "
                                      "a reconstruction, as the sweep kept no definition",
                        "n_places": len(places), "n_near": len(near_places),
                        "n_near_all_rows_clear": sum(x == 1.0 for x in shares),
                        "n_near_most_rows_clear": sum(x > 0.5 for x in shares),
                        "n_near_some_rows_clear": sum(x > 0.0 for x in shares),
                        "n_near_no_row_clears": sum(x == 0.0 for x in shares)}},
        "all_rows": {"n": len(rec["rows"]),
                     "new_ge_0.5": sum(o["booked"] and o["new_probability"] >= 0.5
                                       for o in rec["rows"]),
                     "old_ge_0.5": sum((o["old_probability"] or 0) >= 0.5 for o in rec["rows"])},
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _client() -> Any:
    """The API client, configured as ``run_pv.py``'s batch path configures it."""
    from google import genai

    from scripts.run_pv import _get_api_key

    return genai.Client(api_key=_get_api_key(), http_options={"api_version": "v1alpha"})


def main(argv: list[str] | None = None) -> int:
    """Run one subcommand.

    Returns:
        0 on success; 1 on a refusal or (``book``) an unparseable answer;
        2 when (``lodge``) a job did not fully succeed.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--selection", type=Path, required=True)
    b.add_argument("--pairing", type=Path, required=True)
    b.add_argument("--data-root", type=Path, default=PROJECT_ROOT)
    b.add_argument("--sample-root", type=Path, default=None)
    b.add_argument("--expect-calls", type=int, required=True)
    b.add_argument("--tolerance", type=float, default=0.02)
    b.add_argument("--max-cost-usd", type=float, required=True)
    b.add_argument("--at", default=None, help="pricing date (ISO); default today")
    lo = sub.add_parser("lodge")
    lo.add_argument("--run-dir", type=Path, required=True)
    lo.add_argument("--max-cost-usd", type=float, required=True)
    for name in ("book", "release", "summarise"):
        sp = sub.add_parser(name)
        sp.add_argument("--run-dir", type=Path, required=True)
        if name != "release":
            sp.add_argument("--repo", type=Path, default=PROJECT_ROOT,
                            help="root the legs are under (default: this checkout); a "
                                 "scratch mirror lets the step be run twice and compared")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "build":
            rec = build(repo=PROJECT_ROOT, data_root=args.data_root, selection=args.selection,
                        pairing=args.pairing, out_dir=args.out,
                        expect_calls=args.expect_calls, tolerance=args.tolerance,
                        max_cost_usd=args.max_cost_usd, sample_root=args.sample_root,
                        at=args.at)
            for jkey, j in rec["jobs"].items():
                print(f"  {jkey}: {j['n_requests']} requests, {j['n_legs']} legs, "
                      f"estimate US${j['estimate']['total_cost_usd']}")
            fid = [r for r in rec["rows"] if r["original_request"]["checked"]]
            print(f"BUILD OK: {rec['n_calls']} calls in {len(rec['jobs'])} jobs, "
                  f"{rec['n_distinct_crops']} distinct corrected crops, "
                  f"{len(fid)} original lines reproduced, estimate US${rec['estimate_usd']}")
            return 0
        if args.cmd == "lodge":
            from scripts import lib_batch_api as lba
            from scripts.run_pv import _resolve_model_name

            return lodge(args.run_dir, _client(), args.max_cost_usd,
                         resolve_model=_resolve_model_name,
                         preflight=lba.preflight_file_storage, upload=lba.upload_jsonl,
                         submit=lba.submit_batch_job, poll=lba.poll_batch_job,
                         retrieve=lba.retrieve_batch_results,
                         state_name=lba._get_state_name)
        if args.cmd == "book":
            return book(args.run_dir, repo=args.repo)
        if args.cmd == "summarise":
            s = summarise(args.run_dir, repo=args.repo)
            print(json.dumps({k: s[k] for k in ("total_cost_usd", "all_rows",
                                                "legs_where_nothing_changes")}, indent=1))
            return 0
        from scripts import lib_batch_api as lba

        return release(args.run_dir, _client(), state_name=lba._get_state_name,
                       terminal=lba._TERMINAL_STATES, delete=lba.cleanup_batch_files)
    except Refused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
