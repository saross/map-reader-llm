#!/usr/bin/env python3
"""
55-map FP-Class Classification Driver (Obs 296 Diagnostic Test #2)
==================================================================

Description
-----------
Classifies false-positive (FP) detections from the four corrected 55-map
generalisation runs (T=0.3 text-HIGH, T=0.7 text-HIGH, image, text-MIN)
by the cartographic feature most likely responsible for the detector's
mistake. Tests Shawn's hypothesis (Obs 296) that 55-map FPs concentrate
on numbers / benchmarks (distractor-pull failure mode), while the GS
calibration corpus surfaces a different mode (spot-heights / water).

The audit agent's original FP-class diagnostic could not run on the
existing review CSV's ``symbol_type`` column (it collapses to
``not_mound`` for every FP — see Obs 300 "Test #2 blocked"). This driver
substitutes a Vision Language Model (VLM) classification pass on
on-the-fly rendered 150 m crops, asking Gemini 3 Flash to apply its
Soviet-1980s-topographic-symbol vocabulary directly.

Methodology — cartographic-naming approach
------------------------------------------
Per Shawn's design decision (2026-04-28), this prompt deliberately names
cartographic-vocabulary categories. The detection prompts elsewhere in
this project describe visual features without naming conventions; for
*classification* we WANT the model to apply its cartographic knowledge
— categories are conventional and the question is "what type of feature
is this?". A Soviet-1980s vocabulary anchor in the prompt protects
against generic-vs-Soviet category mismatch.

v2 (2026-04-29) — burial-mound categories added
-----------------------------------------------
The v1 closed list (``number, benchmark, water-feature, contour-ring,
vegetation, settlement, road-or-track, scale-bar-or-grid, none, other``)
was scoped for FP-only classification on the 55-map corpus, where every
input row carries ``human_label == "not_mound"`` (i.e., human-confirmed
non-mound). v2 appends four burial-mound categories (``burial-mound``,
``benchmark-on-burial-mound``, ``triangulation-point-on-burial-mound``,
``settlement-mound``) to mirror the parallel gold-standard (GS) re-run
of the same date — the GS driver classifies both true positives (TPs)
and FPs, and needs the burial-mound symbols on its TP side. Cross-corpus
chi-square comparisons in the paper draw on identical category sets, so
the 55-map list must mirror it.

Strictly, the 55-map analysis remains FP-only by design. Any FP that
v2 reclassifies as a burial-mound category indicates a review-pass
false-FP label (a real mound accidentally clicked "not_mound") and is
itself a finding — flagged in the v1-vs-v2 comparison section of the
v2 report. See ``archive/55maps-fp-classification-v1-pre-burial-mound-list/ARCHIVE-NOTE.md``.

Pipeline
--------
1. Enumerate FPs across all four corrected 55-map run review CSVs
   (``human_label == "not_mound"``).
2. Render 150x150 m crops in-memory from source GeoTIFFs (mirrors the
   live-raster crop logic in ``scripts/review_candidates.py``).
3. Classify each crop via Gemini 3 Flash (``service_tier="flex"``,
   parallel ThreadPoolExecutor workers).
4. Tabulate per-corpus and aggregate distributions; chi-square test
   compares image vs text-track for the asymmetric-failure-mode
   hypothesis. Confidence-weighted analysis is reported alongside.
5. Write JSON results, Markdown report, and a stacked-bar figure.

Robust JSON parsing: handles dict-shaped payloads, list-of-dict
wrapping (mirrors ``_unwrap_verdict_payload`` from
``scripts/lib_verifier.py``, commit ``acba8999``), and retries on
transient errors.

Cost
----
~1,119 calls expected (per audit). At Stage A verifier-T pilot baseline
(~$0.0014 per call), without flex discount, expect ~$1.57; with flex
50 % off, ~$0.78. Hard-cap at $5.00 (driver halts and reports actuals).

Outputs
-------
``results/55maps-fp-classification/``:

- ``fp_classifications.json`` — per-FP record (run, candidate_id, x, y,
  category, confidence, rationale).
- ``category_distribution.json`` — per-corpus + aggregate counts and
  percentages, chi-square test result.
- ``report.md`` — synthesis with table, statistical test, headline
  finding, and methodological caveats.
- ``figures/category_distribution.png`` — stacked-bar chart per corpus.
- ``cost_summary.json`` — actual API spend per run + total.

Usage
-----
.. code-block:: bash

    python scripts/55maps_fp_classify.py \\
        --workers 20 \\
        --output-dir results/55maps-fp-classification

Created
-------
2026-04-28 — Claude Code (Opus 4.7) for Shawn Ross.

Licence
-------
Apache 2.0
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import csv
import io
import json
import logging
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from PIL import Image
from rasterio.windows import Window
from scipy import stats

# Project-root imports — config + lib_verifier patterns.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import config  # noqa: E402  — must follow sys.path mutation


# =========================================================================
# Constants and configuration
# =========================================================================

# Four corrected 55-map run review CSVs — keyed by short corpus label.
# The labels match the column headers in the per-corpus distribution
# table in the report.
RUN_CSV_PATHS: dict[str, Path] = {
    "T0.3": REPO_ROOT / (
        "results/55maps-text-high-t0.3-generalisation/"
        "human-review-multi-buffer.csv"
    ),
    "T0.7": REPO_ROOT / (
        "results/55maps-text-high-generalisation/"
        "human-review-multi-buffer.csv"
    ),
    "image": REPO_ROOT / (
        "results/55maps-image-generalisation/"
        "human-review-multi-buffer.csv"
    ),
    "text-MIN": REPO_ROOT / (
        "results/55maps-text-min-generalisation/"
        "human-review-multi-buffer.csv"
    ),
}

# Source rasters live here. EPSG:32635 (UTM zone 35 N).
RASTERS_DIR = REPO_ROOT / "inputs/rasters/Russian1981_32635"

# Crop size in metres (matches the Obs 296 / Test #2 spec).
CROP_SIZE_M: float = 150.0

# Display upscale: render the metric-window then upscale to this px size
# so symbol detail is legible to the VLM at ~5 m/px native resolution.
# Match the value used by review_candidates.py for visual parity.
DISPLAY_PX: int = 768

# Closed category list — matches the prompt below verbatim. The order
# here drives the order in the report tables and the figure legend.
#
# v2 (2026-04-29): four burial-mound categories appended for cross-corpus
# consistency with the parallel gold-standard (GS) re-run, which needs
# the burial-mound symbols on its true-positive (TP) side. The 55-map
# corpus is FP-only by design (input is rows with human_label ==
# "not_mound"), so burial-mound categories should rarely be chosen here;
# any FP reclassified as burial-mound v2 indicates a review-pass
# false-FP label (a real mound accidentally clicked "not_mound") and is
# itself a finding. See `archive/55maps-fp-classification-v1-pre-burial-mound-list/ARCHIVE-NOTE.md`.
CATEGORIES: list[str] = [
    "number",
    "benchmark",
    "water-feature",
    "contour-ring",
    "vegetation",
    "settlement",
    "road-or-track",
    "scale-bar-or-grid",
    "burial-mound",
    "benchmark-on-burial-mound",
    "triangulation-point-on-burial-mound",
    "settlement-mound",
    "none",
    "other",
]

# Categories considered the "55-map distractor-pull" failure mode (Obs 296
# hypothesis): numbers + benchmarks. Any FP in either is contributing to
# what Shawn predicted dominates the 55-map FP profile.
DISTRACTOR_PULL_CATEGORIES: set[str] = {"number", "benchmark"}

# Categories considered the "GS / spot-height / water-feature" failure
# mode. We do not have a separate "spot-height" category in the closed
# list because spot-heights on Soviet maps are rendered as the "number"
# category (the elevation digits) plus an optional benchmark; the
# water-feature category captures the second arm of Shawn's hypothesis.
# Reported alongside DISTRACTOR_PULL for transparency.
GS_FAILURE_MODE_CATEGORIES: set[str] = {"water-feature"}

# Hard cap on cumulative API spend (USD). The driver halts and reports
# actuals if exceeded mid-run.
COST_HARD_CAP_USD: float = 5.00

# Gemini 3 Flash pricing (USD per 1 M tokens). Verified against
# ``scripts/lib_llm_metadata.py`` (PRICING table, 2026-03-27).
PRICE_INPUT_PER_MTOK: float = 0.50
PRICE_OUTPUT_PER_MTOK: float = 3.00
# Flex tier discount factor — server-side, but applied here for the
# in-driver cost monitor. Documented as "50% off" in the project's
# proposer driver (``scripts/4_detect_mounds_batch.py:1663``).
FLEX_DISCOUNT: float = 0.50

# Retry config for individual API calls.
MAX_RETRIES: int = 3
RETRY_BACKOFF_SECONDS: list[int] = [2, 4, 8]


# =========================================================================
# Prompt — verbatim from the spec
# =========================================================================

CLASSIFICATION_PROMPT: str = """\
You are an expert in Soviet 1980s topographic map symbology. Below is a 150x150 \
metre crop from a Soviet 1980s 1:50,000 topographic map. The centre of this \
crop was identified by an automated detector as a possible burial mound \
symbol, but human review rejected it as a false positive.

Identify the cartographic feature most likely responsible for the detector's \
mistake — i.e., what visually plausible burial-mound-like feature near the \
centre of the crop could have triggered the detector? In the rare case that \
the centre actually does carry a burial-mound symbol (i.e., the human review \
mislabelled a real mound as "not_mound"), choose the appropriate \
burial-mound category instead.

Choose ONE category from this closed list (Soviet 1980s topographic \
conventions). When in doubt, prefer the more specific category over "other".

- number — spot-elevation numeric label, often small italic digits, sometimes \
with a dot below
- benchmark — bench-mark or triangulation marker NOT on a burial mound \
(cross, triangle, "БМ" or "Δ" standing alone on the ground surface)
- water-feature — blue river, stream, lake, pond, swamp, drainage symbol, or \
well marker
- contour-ring — closed contour line(s) forming a ring or oval (brown), often \
around a small hill or depression, with NO mound symbol inside
- vegetation — green-shaded area, tree or shrub symbol, or forest-edge marking
- settlement — house symbol(s), village or hamlet outline, or other \
built-feature cluster, NOT a settlement-mound (tell)
- road-or-track — line symbol for transport (single line, double line, dashed)
- scale-bar-or-grid — printed scale bar, grid intersection, or coordinate label
- burial-mound — Soviet 1980s burial-mound symbol: a small brown ring with \
short outward radial hachures (a "sunburst" / "hairy circle"), no overlaid \
benchmark or triangulation mark
- benchmark-on-burial-mound — a burial-mound sunburst with a bench-mark \
overlay (cross, "БМ"-style mark) at its centre
- triangulation-point-on-burial-mound — a burial-mound sunburst with a \
filled-triangle (Δ) triangulation marker at its centre
- settlement-mound — a tell / settlement-mound symbol: a black hairy/ringed \
square or rectangle, sometimes with a central dot, larger and more angular \
than the (round) burial-mound symbol
- none — no obvious feature near centre; appears to be blank or empty terrain
- other — clearly a feature is present but doesn't match the categories above

Respond ONLY with valid JSON in this exact shape, no other text:

{"category": "<one-of-the-list>", "confidence": <0.0-1.0>, "rationale": \
"<one-sentence-description-of-the-feature>"}
"""


# =========================================================================
# Logging
# =========================================================================

logger = logging.getLogger("fp_classify")


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a concise, time-stamped formatter."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


# =========================================================================
# Raster lookup + crop rendering (mirrors review_candidates.py)
# =========================================================================

# Cached raster bounds — populated on first call to
# ``best_raster_for_point`` to avoid rescanning the rasters dir.
_RASTER_BOUNDS_CACHE: list[tuple[Path, tuple[float, float, float, float]]] = []


def _collect_raster_bounds() -> list[
    tuple[Path, tuple[float, float, float, float]]
]:
    """Gather (path, (left, bottom, right, top)) for every TIF in dir.

    Cached on first call. Mirrors the helper in
    ``scripts/review_candidates.py:_collect_raster_bounds``.
    """
    global _RASTER_BOUNDS_CACHE
    if _RASTER_BOUNDS_CACHE:
        return _RASTER_BOUNDS_CACHE
    out: list[tuple[Path, tuple[float, float, float, float]]] = []
    for p in sorted(RASTERS_DIR.glob("*.tif")):
        try:
            with rasterio.open(p) as src:
                b = src.bounds
                out.append((p, (
                    float(b.left), float(b.bottom),
                    float(b.right), float(b.top),
                )))
        except Exception:  # noqa: BLE001 — corrupt TIFs skipped silently
            continue
    _RASTER_BOUNDS_CACHE = out
    return out


def best_raster_for_point(
    x: float, y: float, sample_px: int = 40,
) -> Path | None:
    """Return the raster whose pixels at (x, y) have most real content.

    Trapezoidal sheets inside rectangular rasters leave black-fill
    outside the mapped area, so bounds filtering alone picks the wrong
    neighbouring sheet for points near the edge. Sample a small window
    at (x, y) and prefer the raster with the most non-black pixels.
    Mirrors ``scripts/review_candidates.py:_best_raster_for_point``.
    """
    bounds_list = _collect_raster_bounds()
    best: tuple[Path, float, float] | None = None
    for path, (left, bottom, right, top) in bounds_list:
        if not (left <= x <= right and bottom <= y <= top):
            continue
        try:
            with rasterio.open(path) as src:
                row_f, col_f = src.index(x, y)
                row = int(round(float(row_f)))
                col = int(round(float(col_f)))
                window = Window(
                    col - sample_px // 2, row - sample_px // 2,
                    sample_px, sample_px,
                )
                arr = src.read(
                    window=window, boundless=True, fill_value=0,
                )
                if arr.shape[0] == 0:
                    continue
                bands = arr[:3] if arr.shape[0] >= 3 else arr[:1]
                near_black = np.all(bands <= 8, axis=0)
                real_frac = 1.0 - float(near_black.mean())
        except Exception:  # noqa: BLE001
            continue
        min_edge = min(x - left, right - x, y - bottom, top - y)
        candidate = (path, real_frac, min_edge)
        if best is None:
            best = candidate
            continue
        if real_frac - best[1] > 0.01:
            best = candidate
        elif abs(real_frac - best[1]) <= 0.01 and min_edge > best[2]:
            best = candidate
    return best[0] if best else None


def render_crop(
    centroid_x: float,
    centroid_y: float,
    context_m: float = CROP_SIZE_M,
    display_px: int = DISPLAY_PX,
) -> Image.Image | None:
    """Render a ``context_m``-wide crop centred on (x, y) as a PIL image.

    Reads the source raster on demand (via ``rasterio`` with
    ``boundless=True`` so edge-of-sheet candidates still produce a
    correctly-sized image) and upscales to ``display_px`` via LANCZOS
    for legible map symbols at the ~5 m/px native resolution.

    Returns ``None`` if no raster covers the point — these are skipped
    by the classification driver.
    """
    raster_path = best_raster_for_point(centroid_x, centroid_y)
    if raster_path is None:
        logger.warning(
            "No raster covers point (%.1f, %.1f); skipping",
            centroid_x, centroid_y,
        )
        return None

    with rasterio.open(raster_path) as src:
        row_f, col_f = src.index(centroid_x, centroid_y)
        row_c = int(round(float(row_f)))
        col_c = int(round(float(col_f)))
        res_m_per_px = abs(src.transform.a)
        half_px = max(1, int(round(context_m / 2 / res_m_per_px)))
        window = Window(
            col_c - half_px, row_c - half_px,
            half_px * 2, half_px * 2,
        )
        arr = src.read(window=window, boundless=True, fill_value=0)
        n_bands = arr.shape[0]
        if n_bands >= 3:
            img_data = arr[:3].transpose(1, 2, 0)
        elif n_bands in (1, 2):
            g = arr[0]
            img_data = np.stack([g, g, g], axis=-1)
        else:
            return None
        raw_img = Image.fromarray(
            img_data.astype(np.uint8),
        ).convert("RGB")

    # Upscale to display size so map symbols remain sharp under VLM
    # tokenisation. LANCZOS preserves edges better than bicubic for
    # line-art topographic content.
    return raw_img.resize((display_px, display_px), Image.LANCZOS)


# =========================================================================
# FP enumeration
# =========================================================================


@dataclass(frozen=True, slots=True)
class FPRecord:
    """A single false positive enumerated from a review CSV.

    Frozen and slotted so we can use the records as worker arguments
    safely across threads.
    """

    run: str
    candidate_id: str
    map_name: str
    x: float
    y: float
    source_tile: str


def load_fps_for_run(run_label: str, csv_path: Path) -> list[FPRecord]:
    """Read a review CSV, return rows where ``human_label == "not_mound"``.

    The review CSV header is documented in
    ``scripts/review_candidates.py``: candidate_id, verifier_probability,
    human_label, symbol_type, source_tile, map_name, x, y, buffer_metres,
    timestamp.

    Args:
        run_label: Short corpus label (e.g. ``"T0.3"``).
        csv_path: Path to the review CSV.

    Returns:
        List of ``FPRecord`` for each row with ``human_label`` == "not_mound".
    """
    fps: list[FPRecord] = []
    if not csv_path.is_file():
        raise FileNotFoundError(f"Review CSV missing: {csv_path}")
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if row.get("human_label", "").strip() != "not_mound":
                continue
            try:
                x = float(row["x"])
                y = float(row["y"])
            except (KeyError, ValueError) as exc:
                logger.warning(
                    "Skipping row (run=%s cand=%s): bad coords (%s)",
                    run_label, row.get("candidate_id"), exc,
                )
                continue
            fps.append(FPRecord(
                run=run_label,
                candidate_id=row.get("candidate_id", ""),
                map_name=row.get("map_name", ""),
                x=x, y=y,
                source_tile=row.get("source_tile", ""),
            ))
    return fps


def enumerate_all_fps() -> list[FPRecord]:
    """Concatenate FPs across all four corrected runs.

    Returns:
        Flat list of ``FPRecord`` for every (run, candidate_id) FP across
        the four corrected 55-map generalisation runs.
    """
    all_fps: list[FPRecord] = []
    for run_label, csv_path in RUN_CSV_PATHS.items():
        run_fps = load_fps_for_run(run_label, csv_path)
        logger.info("Loaded %d FPs for run %s", len(run_fps), run_label)
        all_fps.extend(run_fps)
    return all_fps


# =========================================================================
# JSON parsing — mirrors lib_verifier._unwrap_verdict_payload
# =========================================================================


def unwrap_payload(data: Any) -> dict[str, Any]:
    """Normalise a parsed Gemini JSON payload to a dict.

    The classification prompt asks for a single JSON object, but
    Gemini occasionally wraps the response in a single-element list
    (the ``cand_01563`` parser-bug pattern documented in
    ``scripts/lib_verifier.py:_unwrap_verdict_payload``). This helper
    accepts both shapes and rejects anything else.

    Args:
        data: Object returned by ``json.loads`` on the model's text.

    Returns:
        A dict suitable for ``.get("category", ...)`` field lookups.

    Raises:
        ValueError: If ``data`` is neither a dict nor a non-empty list
            whose first element is a dict.
    """
    if isinstance(data, dict):
        return data
    if isinstance(data, list) and data and isinstance(data[0], dict):
        logger.debug(
            "Response was a list of length %d; unwrapping first element",
            len(data),
        )
        return data[0]
    raise ValueError(
        f"Response is not a JSON object or non-empty list of objects "
        f"(got {type(data).__name__})"
    )


def normalise_category(raw: str) -> str:
    """Map a model-returned category string to the closed-list canonical form.

    Gemini occasionally returns slight variants ("numbers", "benchmark.",
    leading whitespace). This helper strips, lowercases, and matches
    against the closed list; unrecognised values fall through to "other".
    """
    if not raw:
        return "other"
    cleaned = raw.strip().lower().rstrip(".,;")
    # Direct match first.
    if cleaned in CATEGORIES:
        return cleaned
    # Common typo fixes.
    #
    # Note (v2): the standalone aliases ``triangulation`` and
    # ``triangulation-point`` map to ``benchmark`` (matching v1's
    # behaviour for survey markers on bare ground), NOT to the new
    # ``triangulation-point-on-burial-mound`` category — that latter
    # requires the model to identify a triangulation marker explicitly
    # superimposed on a burial-mound symbol. The four-token alias keys
    # for that category are listed lower.
    aliases = {
        "numbers": "number",
        "spot-elevation": "number",
        "spot-height": "number",
        "spot height": "number",
        "elevation": "number",
        "benchmarks": "benchmark",
        "triangulation": "benchmark",
        "triangulation-point": "benchmark",
        "water": "water-feature",
        "water feature": "water-feature",
        "river": "water-feature",
        "stream": "water-feature",
        "lake": "water-feature",
        "contour": "contour-ring",
        "contour ring": "contour-ring",
        "veg": "vegetation",
        "tree": "vegetation",
        "trees": "vegetation",
        "forest": "vegetation",
        "village": "settlement",
        "house": "settlement",
        "building": "settlement",
        "road": "road-or-track",
        "track": "road-or-track",
        "trail": "road-or-track",
        "path": "road-or-track",
        "scale-bar": "scale-bar-or-grid",
        "grid": "scale-bar-or-grid",
        "scale bar": "scale-bar-or-grid",
        "blank": "none",
        "empty": "none",
        # v2 burial-mound categories — alias common variants the model
        # might emit (snake_case from elsewhere in the project, plain
        # English variants, plurals).
        "burial mound": "burial-mound",
        "burial_mound": "burial-mound",
        "mound": "burial-mound",
        "tumulus": "burial-mound",
        "kurgan": "burial-mound",
        "benchmark on burial mound": "benchmark-on-burial-mound",
        "benchmark on mound": "benchmark-on-burial-mound",
        "benchmark_on_mound": "benchmark-on-burial-mound",
        "benchmark-on-mound": "benchmark-on-burial-mound",
        "bench-mark-on-burial-mound": "benchmark-on-burial-mound",
        "bench mark on burial mound": "benchmark-on-burial-mound",
        "triangulation point on burial mound":
            "triangulation-point-on-burial-mound",
        "triangulation on burial mound":
            "triangulation-point-on-burial-mound",
        "triangulation-on-mound": "triangulation-point-on-burial-mound",
        "triangulation_on_mound": "triangulation-point-on-burial-mound",
        "trig-on-mound": "triangulation-point-on-burial-mound",
        "trig point on burial mound":
            "triangulation-point-on-burial-mound",
        "settlement mound": "settlement-mound",
        "settlement_mound": "settlement-mound",
        "tell": "settlement-mound",
    }
    if cleaned in aliases:
        return aliases[cleaned]
    return "other"


# =========================================================================
# Gemini API call
# =========================================================================


@dataclass
class ClassificationResult:
    """Per-FP classification record + token usage for cost accounting."""

    fp: FPRecord
    category: str
    raw_category: str
    confidence: float
    rationale: str
    success: bool
    error: str
    input_tokens: int
    output_tokens: int


def call_gemini_classify(
    fp: FPRecord,
    crop_b64_png: str,
    client: Any,
    model_name: str,
    gen_config: Any,
) -> ClassificationResult:
    """Single-FP classification call with retry/backoff.

    Returns a ``ClassificationResult`` whether or not the call succeeded;
    failures carry empty category and ``success=False``.
    """
    from google.genai import types  # deferred import

    # Build content: prompt text + inline crop PNG.
    content_parts = [
        types.Part.from_text(text=CLASSIFICATION_PROMPT),
        types.Part.from_bytes(
            data=base64.b64decode(crop_b64_png),
            mime_type="image/png",
        ),
    ]
    content = types.Content(parts=content_parts)

    last_err = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=content,
                config=gen_config,
            )

            # Token usage — extract before parsing because parsing
            # might raise. ``usage_metadata`` is the standard SDK field.
            usage = getattr(response, "usage_metadata", None)
            in_tok = (
                int(getattr(usage, "prompt_token_count", 0) or 0)
                if usage else 0
            )
            out_tok = (
                int(getattr(usage, "candidates_token_count", 0) or 0)
                if usage else 0
            )

            try:
                txt = response.text
            except (ValueError, AttributeError) as exc:
                # Safety-blocked or empty response — deterministic, no retry.
                return ClassificationResult(
                    fp=fp, category="", raw_category="",
                    confidence=0.0, rationale="",
                    success=False, error=f"BLOCKED_OR_EMPTY: {exc}",
                    input_tokens=in_tok, output_tokens=out_tok,
                )
            if txt is None:
                return ClassificationResult(
                    fp=fp, category="", raw_category="",
                    confidence=0.0, rationale="",
                    success=False, error="NULL_TEXT",
                    input_tokens=in_tok, output_tokens=out_tok,
                )

            # Strip markdown fences if present.
            txt = txt.replace("```json", "").replace("```", "").strip()

            try:
                data = json.loads(txt)
                payload = unwrap_payload(data)
            except (json.JSONDecodeError, ValueError, AttributeError) as exc:
                # Retry once on transient parse error; fall through after.
                last_err = f"PARSE_ERROR: {exc} | raw={txt[:200]!r}"
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS[attempt - 1])
                    continue
                return ClassificationResult(
                    fp=fp, category="", raw_category="",
                    confidence=0.0, rationale="",
                    success=False, error=last_err,
                    input_tokens=in_tok, output_tokens=out_tok,
                )

            raw_cat = str(payload.get("category", ""))
            cat = normalise_category(raw_cat)
            try:
                conf = float(payload.get("confidence", 0.0))
            except (TypeError, ValueError):
                conf = 0.0
            rationale = str(payload.get("rationale", ""))

            return ClassificationResult(
                fp=fp, category=cat, raw_category=raw_cat,
                confidence=conf, rationale=rationale,
                success=True, error="",
                input_tokens=in_tok, output_tokens=out_tok,
            )

        except Exception as exc:  # noqa: BLE001 — retry on any API-side error
            last_err = f"{type(exc).__name__}: {exc}"
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS[attempt - 1])
                continue
            return ClassificationResult(
                fp=fp, category="", raw_category="",
                confidence=0.0, rationale="",
                success=False, error=last_err,
                input_tokens=0, output_tokens=0,
            )
    # Should never reach here.
    return ClassificationResult(
        fp=fp, category="", raw_category="",
        confidence=0.0, rationale="",
        success=False, error=f"UNEXPECTED_RETRY_FALLTHROUGH: {last_err}",
        input_tokens=0, output_tokens=0,
    )


def render_and_classify(
    fp: FPRecord,
    client: Any,
    model_name: str,
    gen_config: Any,
) -> ClassificationResult:
    """Render the FP crop in-memory and classify it via Gemini.

    Worker function for ``ThreadPoolExecutor``. Skips FPs whose centroid
    has no covering raster.
    """
    crop = render_crop(fp.x, fp.y)
    if crop is None:
        return ClassificationResult(
            fp=fp, category="", raw_category="",
            confidence=0.0, rationale="",
            success=False, error="NO_RASTER_COVERAGE",
            input_tokens=0, output_tokens=0,
        )

    # Encode PNG to base64 bytes for inline part assembly. The
    # ``call_gemini_classify`` helper will decode on the way in to
    # ``types.Part.from_bytes`` — this round-trip avoids passing live
    # ``Image`` objects across threads (PIL Image is technically thread
    # safe for read-only ops but we follow the project's convention of
    # serialising to bytes at the worker boundary).
    buf = io.BytesIO()
    crop.save(buf, format="PNG")
    crop_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return call_gemini_classify(
        fp=fp,
        crop_b64_png=crop_b64,
        client=client,
        model_name=model_name,
        gen_config=gen_config,
    )


# =========================================================================
# Cost accounting
# =========================================================================


def compute_cost(
    input_tokens: int, output_tokens: int, flex: bool = True,
) -> float:
    """Estimate USD cost from token counts, applying flex-tier discount.

    Args:
        input_tokens: Aggregate input tokens (across all calls).
        output_tokens: Aggregate output tokens.
        flex: Apply the 50 % flex-tier multiplier.

    Returns:
        Estimated cost in USD.
    """
    raw = (
        (input_tokens / 1_000_000) * PRICE_INPUT_PER_MTOK
        + (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_MTOK
    )
    return raw * (FLEX_DISCOUNT if flex else 1.0)


# =========================================================================
# Aggregation + statistics
# =========================================================================


def per_run_distribution(
    results: list[ClassificationResult],
    runs: list[str],
    categories: list[str],
    confidence_floor: float = 0.0,
) -> dict[str, dict[str, int]]:
    """Per-run category counts.

    Args:
        results: All successful classifications.
        runs: Ordered list of run labels (column order).
        categories: Ordered list of category labels (row order).
        confidence_floor: Drop classifications with confidence below
            this threshold. ``0.0`` = include all (default).

    Returns:
        ``dict[run -> dict[category -> count]]``.
    """
    out: dict[str, dict[str, int]] = {
        r: {c: 0 for c in categories} for r in runs
    }
    for r in results:
        if not r.success:
            continue
        if r.confidence < confidence_floor:
            continue
        if r.fp.run in out and r.category in out[r.fp.run]:
            out[r.fp.run][r.category] += 1
    return out


def confidence_weighted_distribution(
    results: list[ClassificationResult],
    runs: list[str],
    categories: list[str],
) -> dict[str, dict[str, float]]:
    """Per-run distribution with per-record weight = confidence.

    Records with low confidence contribute fractionally to their
    category's mass; the column sum equals the sum of confidences for
    that run, not the n_FPs. Reported alongside the unweighted counts as
    a sensitivity check (low-confidence picks may signal noisy
    classification).
    """
    out: dict[str, dict[str, float]] = {
        r: {c: 0.0 for c in categories} for r in runs
    }
    for r in results:
        if not r.success:
            continue
        if r.fp.run in out and r.category in out[r.fp.run]:
            out[r.fp.run][r.category] += float(r.confidence)
    return out


def chi_square_image_vs_text(
    counts: dict[str, dict[str, int]],
    categories: list[str],
) -> dict[str, Any]:
    """Chi-square test: image vs text-track aggregate distribution.

    Pools the three text runs into a single text-track total, places it
    against the image run, and tests whether the per-category
    distribution differs between tracks. Returns the chi-square
    statistic, degrees of freedom, p-value, expected counts, and a
    per-category Pearson residual breakdown for diagnostic reading.

    Returns an empty dict (with ``insufficient_data=True``) if either
    track is empty or the contingency table has all-zero columns.
    """
    text_runs = [r for r in counts if r != "image"]
    image_run = "image"
    if image_run not in counts or not text_runs:
        return {"insufficient_data": True, "reason": "missing track(s)"}

    image_row = [counts[image_run][c] for c in categories]
    text_row = [
        sum(counts[r][c] for r in text_runs) for c in categories
    ]
    table = np.array([image_row, text_row], dtype=float)

    # Both rows (tracks) must carry mass for chi-square to be defined.
    if table[0].sum() == 0 or table[1].sum() == 0:
        return {
            "insufficient_data": True,
            "reason": "one track has zero classified FPs",
            "n_image": int(table[0].sum()),
            "n_text": int(table[1].sum()),
        }

    # Drop columns that are all-zero across both tracks — chi-square
    # would otherwise return nan.
    keep = (table.sum(axis=0) > 0)
    if keep.sum() < 2:
        return {"insufficient_data": True, "reason": "<2 non-zero categories"}
    table_kept = table[:, keep]
    cats_kept = [c for c, k in zip(categories, keep) if k]

    chi2, p_value, dof, expected = stats.chi2_contingency(table_kept)

    # Pearson residuals — (observed - expected) / sqrt(expected).
    # Reported per-category with sign so we can read the direction.
    residuals = (table_kept - expected) / np.sqrt(expected)
    per_category_res = []
    for j, cat in enumerate(cats_kept):
        per_category_res.append({
            "category": cat,
            "image_observed": int(table_kept[0, j]),
            "text_observed": int(table_kept[1, j]),
            "image_expected": float(round(expected[0, j], 3)),
            "text_expected": float(round(expected[1, j], 3)),
            "image_residual": float(round(residuals[0, j], 3)),
            "text_residual": float(round(residuals[1, j], 3)),
        })

    return {
        "insufficient_data": False,
        "chi2": float(chi2),
        "p_value": float(p_value),
        "dof": int(dof),
        "n_image": int(table[0].sum()),
        "n_text": int(table[1].sum()),
        "categories_used": cats_kept,
        "per_category": per_category_res,
        "image_runs": [image_run],
        "text_runs": text_runs,
    }


# =========================================================================
# Output writers
# =========================================================================


def write_classifications_json(
    results: list[ClassificationResult], path: Path,
) -> None:
    """Write per-FP classification records to JSON."""
    rows = []
    for r in results:
        rows.append({
            "run": r.fp.run,
            "candidate_id": r.fp.candidate_id,
            "map_name": r.fp.map_name,
            "x": r.fp.x,
            "y": r.fp.y,
            "source_tile": r.fp.source_tile,
            "category": r.category,
            "raw_category": r.raw_category,
            "confidence": r.confidence,
            "rationale": r.rationale,
            "success": r.success,
            "error": r.error,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
        })
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def write_distribution_json(
    counts: dict[str, dict[str, int]],
    weighted: dict[str, dict[str, float]],
    chi2: dict[str, Any],
    runs: list[str],
    categories: list[str],
    n_total: int,
    path: Path,
) -> None:
    """Write the per-corpus distribution + chi-square test to JSON."""
    pct: dict[str, dict[str, float]] = {}
    for run in runs:
        col_total = sum(counts[run].values())
        pct[run] = {
            c: (
                round(100.0 * counts[run][c] / col_total, 2)
                if col_total > 0 else 0.0
            )
            for c in categories
        }
    aggregate = {c: sum(counts[r][c] for r in runs) for c in categories}
    grand_total = sum(aggregate.values())
    aggregate_pct = {
        c: (
            round(100.0 * aggregate[c] / grand_total, 2)
            if grand_total > 0 else 0.0
        )
        for c in categories
    }
    doc = {
        "version": "1.0",
        "n_total_classified": n_total,
        "categories": categories,
        "runs": runs,
        "counts": counts,
        "percentages": pct,
        "weighted_by_confidence": weighted,
        "aggregate_counts": aggregate,
        "aggregate_percentages": aggregate_pct,
        "chi_square_image_vs_text": chi2,
    }
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")


def write_cost_summary(
    per_run_tokens: dict[str, tuple[int, int, int]],
    flex: bool,
    wall_clock_seconds: float,
    path: Path,
) -> None:
    """Write per-run + total token counts and estimated cost.

    Args:
        per_run_tokens: ``dict[run -> (n_calls, in_tok, out_tok)]``.
        flex: Whether flex-tier discount was assumed.
    """
    rows = {}
    total_in = total_out = total_calls = 0
    for run, (n_calls, in_tok, out_tok) in per_run_tokens.items():
        cost = compute_cost(in_tok, out_tok, flex=flex)
        rows[run] = {
            "n_calls": n_calls,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "cost_usd": round(cost, 4),
        }
        total_in += in_tok
        total_out += out_tok
        total_calls += n_calls
    grand_cost = compute_cost(total_in, total_out, flex=flex)
    doc = {
        "version": "1.0",
        "flex_tier_assumed": flex,
        "pricing": {
            "model": "gemini-3-flash",
            "input_per_1m_usd": PRICE_INPUT_PER_MTOK,
            "output_per_1m_usd": PRICE_OUTPUT_PER_MTOK,
            "flex_discount_factor": FLEX_DISCOUNT if flex else 1.0,
        },
        "per_run": rows,
        "totals": {
            "n_calls": total_calls,
            "input_tokens": total_in,
            "output_tokens": total_out,
            "cost_usd": round(grand_cost, 4),
        },
        "wall_clock_seconds": round(wall_clock_seconds, 1),
        "wall_clock_pretty": (
            f"{wall_clock_seconds // 60:.0f}m {wall_clock_seconds % 60:.0f}s"
        ),
    }
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")


def write_distribution_figure(
    counts: dict[str, dict[str, int]],
    runs: list[str],
    categories: list[str],
    path: Path,
) -> None:
    """Plot a stacked bar chart of per-corpus category percentages."""
    n_runs = len(runs)
    pct_matrix = np.zeros((len(categories), n_runs), dtype=float)
    for j, run in enumerate(runs):
        col_total = sum(counts[run].values())
        if col_total <= 0:
            continue
        for i, cat in enumerate(categories):
            pct_matrix[i, j] = 100.0 * counts[run][cat] / col_total

    # Use tab20 — 20 distinguishable colours, big enough for v2's
    # 14-category list (10 cartographic + 4 burial-mound).
    palette = plt.get_cmap("tab20").colors  # 20 distinguishable colours
    fig, ax = plt.subplots(figsize=(8.5, 5.0), dpi=140)
    bottoms = np.zeros(n_runs, dtype=float)
    for i, cat in enumerate(categories):
        ax.bar(
            runs, pct_matrix[i],
            bottom=bottoms,
            label=cat,
            color=palette[i % len(palette)],
            edgecolor="white",
            linewidth=0.4,
        )
        bottoms += pct_matrix[i]
    ax.set_ylabel("Percentage of FPs (%)")
    ax.set_xlabel("Corpus / run")
    ax.set_title(
        "55-map FP-class distribution by run (Obs 296 Test #2 — v2)\n"
        "Cartographic + burial-mound categories from Gemini 3 Flash",
        fontsize=10,
    )
    ax.set_ylim(0, 100)
    ax.legend(
        bbox_to_anchor=(1.02, 1.0), loc="upper left",
        frameon=False, fontsize=8, title="category",
    )
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


#: v1 categories — frozen here so the v2 driver can show v1-vs-v2
#: comparisons in the report without re-reading the archived v1 outputs.
#: The v1 list was 10 categories (no burial-mound entries).
V1_CATEGORIES: tuple[str, ...] = (
    "number",
    "benchmark",
    "water-feature",
    "contour-ring",
    "vegetation",
    "settlement",
    "road-or-track",
    "scale-bar-or-grid",
    "none",
    "other",
)

#: v1 aggregate counts (n = 1,119), copied from the archived v1
#: ``category_distribution.json`` file. Used for v1-vs-v2 comparison.
V1_AGGREGATE_COUNTS: dict[str, int] = {
    "number": 214,
    "benchmark": 54,
    "water-feature": 136,
    "contour-ring": 458,
    "vegetation": 64,
    "settlement": 157,
    "road-or-track": 13,
    "scale-bar-or-grid": 2,
    "none": 7,
    "other": 14,
}

#: v1 distractor-pull (number + benchmark) shares from the archived v1
#: report. Used for the v1-vs-v2 comparison row in the verdict.
V1_DISTRACTOR_SHARE_TEXT_PCT: float = 22.7
V1_DISTRACTOR_SHARE_IMAGE_PCT: float = 27.6
V1_CHI2_P_VALUE: float = 0.1474
V1_VERDICT: str = (
    "NOT SUPPORTED — text-track distractor-pull share is below 30 %, "
    "and image-vs-text-track chi-square is non-significant."
)


def write_report_md(
    counts: dict[str, dict[str, int]],
    weighted: dict[str, dict[str, float]],
    chi2: dict[str, Any],
    runs: list[str],
    categories: list[str],
    n_total: int,
    n_failed: int,
    cost_total: float,
    wall_clock_seconds: float,
    path: Path,
) -> None:
    """Write a synthesis report covering the methodology, headline,
    chi-square test, methodology change vs v1, and caveats.

    The v2 report mirrors the v1 structure but adds two new sections:
    a "Methodology change" block explaining the closed-list expansion
    and a v1-vs-v2 comparison table focused on whether any FPs
    reclassify into the new burial-mound categories.
    """
    lines: list[str] = []
    lines.append(
        "# 55-map FP-class classification — Obs 296 Diagnostic Test #2 (v2)\n"
    )
    lines.append(
        f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_\n"
    )
    lines.append(
        "Tests Shawn's hypothesis (Obs 296) that 55-map false positives "
        "concentrate on numbers / benchmarks (distractor-pull failure mode), "
        "while the gold-standard (GS) calibration corpus surfaces a "
        "different mode (spot-heights / water features). The original "
        "Test #2 was blocked by the review CSV's collapsed `symbol_type` "
        "column (Obs 300); this run substitutes a Vision Language Model "
        "(VLM) classification pass on rendered 150 m crops, asking "
        "Gemini 3 Flash to apply Soviet-1980s topographic-symbol "
        "categories directly.\n"
    )

    # Methodology change — v2-specific.
    lines.append("## Methodology change (v2 vs v1)\n")
    lines.append(
        "v1 (archived at "
        "`archive/55maps-fp-classification-v1-pre-burial-mound-list/`) "
        "used a 10-category FP-only closed list: `number, benchmark, "
        "water-feature, contour-ring, vegetation, settlement, "
        "road-or-track, scale-bar-or-grid, none, other`. There was no "
        "`burial-mound` category. The 55-map analysis is FP-only by "
        "design — every input row carries `human_label == \"not_mound\"`, "
        "i.e., human-confirmed non-mound — so the v1 list was "
        "defensible for this corpus alone.\n"
    )
    lines.append(
        "v2 mirrors the parallel gold-standard (GS) re-run of the same "
        "date by appending four Soviet 1980s burial-mound symbols: "
        "`burial-mound`, `benchmark-on-burial-mound`, "
        "`triangulation-point-on-burial-mound`, `settlement-mound`. "
        "Cross-corpus chi-square comparisons in the paper draw on "
        "identical category sets, so the 55-map list must mirror the GS "
        "list. Any 55-map FP that v2 reclassifies as a burial-mound "
        "category indicates a review-pass false-FP label (a real mound "
        "accidentally clicked \"not_mound\") and is itself a finding — "
        "see the v1-vs-v2 comparison section below.\n"
    )

    lines.append("## Method\n")
    lines.append(
        "1. Enumerated FPs from the four corrected 55-map review CSVs "
        "(`human_label == \"not_mound\"`).\n"
        "2. Rendered 150x150 m crops on-the-fly from the source GeoTIFFs "
        "(`inputs/rasters/Russian1981_32635/`) using the live-raster "
        "pipeline mirrored from `scripts/review_candidates.py`.\n"
        "3. Classified each crop via Gemini 3 Flash (flex tier, "
        "thinking_level=minimal, temperature=0.0). Closed-list categories "
        f"(v2, 14 entries): {', '.join(categories)}.\n"
        "4. Tabulated per-corpus distributions; ran a chi-square test "
        "on image vs text-track aggregate distribution.\n"
    )
    lines.append(
        f"Total classified: {n_total} (failed/skipped: {n_failed}). "
        f"Wall-clock: {wall_clock_seconds:.1f} s "
        f"({wall_clock_seconds / 60:.1f} m). "
        f"Estimated API cost: ${cost_total:.4f} USD (flex tier).\n"
    )

    # Per-corpus table.
    lines.append("## Per-corpus distribution\n")
    header = (
        "| Category | "
        + " | ".join(f"{r}" for r in runs)
        + " | aggregate |"
    )
    sep = (
        "|---|"
        + "".join("---:|" for _ in runs)
        + "---:|"
    )
    lines.append(header)
    lines.append(sep)
    aggregate = {c: sum(counts[r][c] for r in runs) for c in categories}
    grand_total = sum(aggregate.values())
    col_totals = {r: sum(counts[r].values()) for r in runs}
    for cat in categories:
        cells = []
        for run in runs:
            n = counts[run][cat]
            denom = col_totals[run] if col_totals[run] > 0 else 1
            cells.append(f"{n} ({100 * n / denom:.1f} %)")
        agg_n = aggregate[cat]
        agg_denom = grand_total if grand_total > 0 else 1
        lines.append(
            f"| {cat} | "
            + " | ".join(cells)
            + f" | {agg_n} ({100 * agg_n / agg_denom:.1f} %) |"
        )
    lines.append(
        "| **N (FPs)** | "
        + " | ".join(f"**{col_totals[r]}**" for r in runs)
        + f" | **{grand_total}** |\n"
    )

    # v1-vs-v2 aggregate comparison.
    lines.append("## v1-vs-v2 aggregate comparison\n")
    lines.append(
        "How did the four added burial-mound categories shift the "
        "55-map FP profile? Each row shows the v1 aggregate count and "
        "share alongside the v2 aggregate. Burial-mound categories "
        "were not in v1 — any v2 mass on those rows reflects FPs that "
        "v1 had to assign to the closest non-burial-mound category "
        "(typically `contour-ring` for the round mound symbol or "
        "`settlement` for the angular tell symbol).\n"
    )
    v1_total = sum(V1_AGGREGATE_COUNTS.values())
    v2_total = grand_total
    lines.append(
        "| Category | v1 n | v1 % | v2 n | v2 % | Δ (v2 − v1) pp |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|")
    burial_mound_categories: tuple[str, ...] = (
        "burial-mound",
        "benchmark-on-burial-mound",
        "triangulation-point-on-burial-mound",
        "settlement-mound",
    )
    for cat in categories:
        v1_n = V1_AGGREGATE_COUNTS.get(cat, 0)
        v1_pct = (100.0 * v1_n / v1_total) if v1_total > 0 else 0.0
        v2_n = aggregate[cat]
        v2_pct = (100.0 * v2_n / v2_total) if v2_total > 0 else 0.0
        # Mark burial-mound rows for visibility.
        cat_label = (
            f"**{cat}**" if cat in burial_mound_categories else cat
        )
        if cat in V1_AGGREGATE_COUNTS:
            v1_n_cell = f"{v1_n}"
            v1_pct_cell = f"{v1_pct:.1f} %"
            delta_cell = f"{v2_pct - v1_pct:+.1f}"
        else:
            v1_n_cell = "—"
            v1_pct_cell = "—"
            delta_cell = f"+{v2_pct:.1f} (new)"
        lines.append(
            f"| {cat_label} | {v1_n_cell} | {v1_pct_cell} | "
            f"{v2_n} | {v2_pct:.1f} % | {delta_cell} |"
        )
    lines.append(
        f"| **N (FPs)** | **{v1_total}** | — | **{v2_total}** | — | — |\n"
    )
    burial_mound_v2_total = sum(
        aggregate[c] for c in burial_mound_categories
    )
    burial_mound_v2_pct = (
        100.0 * burial_mound_v2_total / v2_total if v2_total > 0 else 0.0
    )
    lines.append(
        f"**Total v2 mass on the four burial-mound categories: "
        f"{burial_mound_v2_total} / {v2_total} FPs "
        f"({burial_mound_v2_pct:.1f} %).**\n"
    )
    if burial_mound_v2_total == 0:
        lines.append(
            "Zero burial-mound assignments confirms the FP-only design "
            "of the 55-map analysis was sound — no FPs in the four "
            "corrected runs are real mounds that the human reviewer "
            "missed. The v1 distribution is materially preserved under "
            "v2, with shifts confined to the non-burial-mound rows "
            "(re-balancing within the unchanged 10 categories due to "
            "single-pass classification noise).\n"
        )
    elif burial_mound_v2_pct < 1.0:
        lines.append(
            "A small number (< 1 %) of FPs were reclassified as "
            "burial-mound symbols under v2. These are candidate "
            "review-pass false-FP labels (real mounds accidentally "
            "clicked \"not_mound\"); they should be inspected manually "
            "before drawing conclusions, but the headline FP-only "
            "design of the 55-map analysis is materially sound. See "
            "`fp_classifications.json` for per-FP records "
            "(`category` field on rows in burial-mound categories).\n"
        )
    else:
        lines.append(
            f"**FINDING:** {burial_mound_v2_total} FPs "
            f"({burial_mound_v2_pct:.1f} %) reclassify as burial-mound "
            "categories under v2. This exceeds the < 1 % "
            "calibration-noise threshold and indicates a non-trivial "
            "rate of review-pass false-FP labels (real mounds "
            "accidentally clicked \"not_mound\" by the reviewer). "
            "Per-FP records are in `fp_classifications.json` "
            "(filter on `category in {burial-mound, "
            "benchmark-on-burial-mound, "
            "triangulation-point-on-burial-mound, settlement-mound}`); "
            "manual review of these crops is the natural follow-up.\n"
        )

    # Distractor-pull (number + benchmark) summary.
    lines.append("## Distractor-pull share (number + benchmark)\n")
    lines.append(
        "Shawn's hypothesis predicts 55-map FPs concentrate on "
        "**number + benchmark** (Soviet 1980s spot-elevation labels and "
        "survey markers).\n"
    )
    lines.append("| Run | number + benchmark | share | n_FPs |")
    lines.append("|---|---:|---:|---:|")
    for run in runs:
        nb = counts[run].get("number", 0) + counts[run].get("benchmark", 0)
        denom = col_totals[run] if col_totals[run] > 0 else 1
        lines.append(
            f"| {run} | {nb} | {100 * nb / denom:.1f} % | "
            f"{col_totals[run]} |"
        )
    text_total = sum(
        counts[r].get("number", 0) + counts[r].get("benchmark", 0)
        for r in runs if r != "image"
    )
    text_denom = sum(col_totals[r] for r in runs if r != "image") or 1
    image_nb = counts.get("image", {}).get("number", 0) + counts.get(
        "image", {},
    ).get("benchmark", 0)
    image_denom = col_totals.get("image", 0) or 1
    lines.append(
        f"| **text-track aggregate** | **{text_total}** | "
        f"**{100 * text_total / text_denom:.1f} %** | "
        f"**{text_denom if text_denom != 1 else 0}** |"
    )
    lines.append(
        f"| **image** | **{image_nb}** | "
        f"**{100 * image_nb / image_denom:.1f} %** | "
        f"**{image_denom if image_denom != 1 else 0}** |\n"
    )

    # Spot-height / water-feature share — GS-failure-mode predictor.
    lines.append("## GS-failure-mode share (water-feature)\n")
    lines.append(
        "Shawn's hypothesis predicts the GS calibration corpus would "
        "have produced FPs on **spot-heights and water features**. "
        "Note that on Soviet maps a spot-height usually presents as a "
        "numeric label (sometimes plus a benchmark) — the closed list "
        "categorises elevation digits as `number` rather than as a "
        "separate spot-height bucket. This row therefore reports only "
        "the second arm of the GS prediction (water-feature). The "
        "first arm (numbers as spot-heights) is folded into the "
        "distractor-pull row above; under Shawn's hypothesis, "
        "55-map number-prevalence reflects label distractor-pull, "
        "while GS would-be number-prevalence reflects spot-height "
        "ambiguity. The diagnostic alone cannot tell those apart "
        "without GS data — flagged as a methodological caveat.\n"
    )
    lines.append("| Run | water-feature | share |")
    lines.append("|---|---:|---:|")
    for run in runs:
        wf = counts[run].get("water-feature", 0)
        denom = col_totals[run] if col_totals[run] > 0 else 1
        lines.append(f"| {run} | {wf} | {100 * wf / denom:.1f} % |")
    lines.append("")

    # Chi-square test.
    lines.append("## Chi-square test — image vs text-track\n")
    if chi2.get("insufficient_data"):
        lines.append(
            f"Insufficient data for chi-square test "
            f"({chi2.get('reason', 'unknown')}).\n"
        )
    else:
        lines.append(
            f"- chi-squared statistic: {chi2['chi2']:.3f}\n"
            f"- degrees of freedom: {chi2['dof']}\n"
            f"- p-value: {chi2['p_value']:.4g}\n"
            f"- n (image): {chi2['n_image']}\n"
            f"- n (text-track aggregate): {chi2['n_text']}\n"
            f"- categories used: {', '.join(chi2['categories_used'])}\n"
        )
        lines.append("")
        lines.append(
            "### Per-category Pearson residuals\n\n"
            "Pearson residuals (observed − expected) / √expected indicate "
            "which categories drive the difference. |residual| > 2 is the "
            "conventional threshold for a meaningful per-cell effect.\n"
        )
        lines.append(
            "| Category | image obs | image exp | image residual | "
            "text obs | text exp | text residual |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for r in chi2["per_category"]:
            lines.append(
                f"| {r['category']} | {r['image_observed']} | "
                f"{r['image_expected']:.1f} | {r['image_residual']:+.2f} | "
                f"{r['text_observed']} | {r['text_expected']:.1f} | "
                f"{r['text_residual']:+.2f} |"
            )
        lines.append("")

    # Verdict.
    lines.append("## Verdict on Shawn's hypothesis\n")
    nb_share_text = 100 * text_total / text_denom if text_denom else 0.0
    nb_share_image = 100 * image_nb / image_denom if image_denom else 0.0
    # Threshold for "high distractor-pull share" — picked as roughly
    # twice the baseline rate Shawn cited (~15 % image, ~5 % text-track
    # mid-distance pull rate per Obs 296). 30 % means the
    # number+benchmark categories together account for at least 30 % of
    # the FPs on the track in question.
    DISTRACTOR_SHARE_THRESHOLD_PCT = 30.0
    p_value = chi2.get("p_value")
    if p_value is None:
        verdict = "INSUFFICIENT DATA"
    elif p_value < 0.05 and nb_share_text > DISTRACTOR_SHARE_THRESHOLD_PCT:
        verdict = (
            "**SUPPORTED** — text-track distractor-pull (number + "
            "benchmark) share exceeds 30 %, and image-vs-text-track "
            "distributions differ significantly (chi-square p < 0.05)."
        )
    elif nb_share_text > DISTRACTOR_SHARE_THRESHOLD_PCT:
        verdict = (
            "**PARTIALLY SUPPORTED** — text-track distractor-pull share "
            "is high (> 30 %), but image-vs-text-track chi-square is "
            "non-significant. The dominant 55-map text-track FP class is "
            "distractor-pull as predicted, but the image vs text "
            "asymmetric-failure-mode framing is not statistically sharp."
        )
    elif p_value < 0.05:
        verdict = (
            "**MIXED** — image-vs-text distributions differ significantly, "
            "but text-track distractor-pull share does not exceed 30 %; "
            "the dominant 55-map FP class on text-track is something "
            "other than number/benchmark."
        )
    else:
        verdict = (
            "**NOT SUPPORTED** — text-track distractor-pull share is "
            "below 30 %, and image-vs-text-track chi-square is "
            "non-significant. Shawn's predicted asymmetric-failure-mode "
            "pattern is not visible in this classification pass."
        )
    lines.append(verdict)
    lines.append("")
    if p_value is not None:
        lines.append(
            f"- Text-track aggregate (number + benchmark) share: "
            f"{nb_share_text:.1f} %\n"
            f"- Image-track (number + benchmark) share: "
            f"{nb_share_image:.1f} %\n"
            f"- Chi-square p-value (image vs text-track): "
            f"{p_value:.4g}\n"
        )
    else:
        lines.append("- Chi-square p-value: insufficient data\n")

    # v1 verdict comparison.
    lines.append("### Comparison with v1 verdict\n")
    lines.append(
        f"v1 verdict: **{V1_VERDICT}**\n\n"
        f"- v1 text-track distractor-pull share: "
        f"{V1_DISTRACTOR_SHARE_TEXT_PCT:.1f} % "
        f"(v2: {nb_share_text:.1f} %)\n"
        f"- v1 image-track distractor-pull share: "
        f"{V1_DISTRACTOR_SHARE_IMAGE_PCT:.1f} % "
        f"(v2: {nb_share_image:.1f} %)\n"
        f"- v1 chi-square p-value: {V1_CHI2_P_VALUE:.4f}"
        + (
            f" (v2: {p_value:.4g})\n"
            if p_value is not None
            else " (v2: insufficient data)\n"
        )
    )
    if p_value is not None:
        v1_supported = (
            V1_DISTRACTOR_SHARE_TEXT_PCT > DISTRACTOR_SHARE_THRESHOLD_PCT
            and V1_CHI2_P_VALUE < 0.05
        )
        v2_supported = (
            nb_share_text > DISTRACTOR_SHARE_THRESHOLD_PCT
            and p_value < 0.05
        )
        if v1_supported == v2_supported:
            lines.append(
                "v1 and v2 verdicts agree on the headline question: "
                "Shawn's distractor-pull-on-text-track hypothesis is "
                f"{'supported' if v2_supported else 'not supported'} "
                "under both closed lists. The closed-list expansion "
                "did not change the hypothesis-testing outcome.\n"
            )
        else:
            lines.append(
                "**v1 and v2 verdicts diverge** on the headline "
                "question. The closed-list expansion materially "
                "changed the hypothesis-testing outcome — likely "
                "because vocabulary leakage from FPs that were really "
                "mound-like signs has shifted between the v1 and v2 "
                "category sets. Inspect the v1-vs-v2 comparison "
                "table above to see which categories drove the "
                "change.\n"
            )

    # Caveats.
    lines.append("## Caveats and methodological notes\n")
    lines.append(
        "- **Single-pass classification, no consensus.** Each FP is "
        "classified once at temperature 0.0, thinking_level=minimal. "
        "Gemini 3 Flash class assignment may be noisy in ambiguous "
        "centres (e.g. crops with multiple plausible features near "
        "centre). The confidence-weighted distribution in "
        "`category_distribution.json` provides a sensitivity check; "
        "results should be read as a coarse first-pass profile, not a "
        "precise per-class accounting.\n"
        "- **No GS comparator.** The diagnostic compares the four 55-map "
        "runs against each other, not against the GS corpus. The "
        "headline hypothesis (55-map vs GS asymmetric failure modes) is "
        "tested only on the 55-map side; the GS half is inferred from "
        "Shawn's prior manual review (Obs 296). A direct GS-side "
        "classification is the natural follow-up.\n"
        "- **Number = spot-height confound.** Soviet 1:50,000 maps "
        "render spot-heights as numeric elevation labels — the same "
        "`number` category that captures the distractor-pull arm of "
        "Shawn's 55-map hypothesis. The two arms are not separable by "
        "this classification alone; the cross-corpus picture (55-map "
        "number-prevalence as label distractor-pull vs GS "
        "number-prevalence as spot-height ambiguity) is a paper "
        "interpretation, not a measurement.\n"
        "- **Crop-centre ambiguity.** Some FPs sit in dense map regions "
        "where multiple categories are plausible near the 150 m crop "
        "centre. The model is asked to pick the strongest "
        "burial-mound-confusable feature; the resulting category may "
        "differ from a strict \"closest-to-centre\" reading.\n"
        "- **Prompt vocabulary anchor.** The prompt names Soviet 1980s "
        "topographic categories explicitly. This is a deliberate "
        "departure from the detection-prompt convention (visual-feature "
        "naming without cartographic vocabulary); for FP "
        "classification we WANT the model to apply its cartographic "
        "knowledge. Generic vs Soviet category mismatch was guarded "
        "against by including a Cyrillic example (\"БМ\") in the prompt.\n"
    )

    # Findable later (mirrors obs format for grep-discoverability).
    lines.append("## Findable later\n")
    lines.append(
        "Search terms: 55-map FP-class classification, Obs 296 Test #2, "
        "cartographic-naming approach, Gemini 3 Flash 150 m crop "
        "classification, distractor-pull text-track number benchmark, "
        "chi-square image vs text-track, water-feature spot-height GS "
        "failure mode, Soviet 1980s topographic categories closed list, "
        "rendered crop in-memory base64, flex tier classification "
        "single-pass, confidence-weighted distribution sensitivity, "
        "55-map FP v2 burial-mound closed list, cross-corpus consistency "
        "with parallel GS re-run, review-pass false-FP labels.\n"
    )

    # Join + collapse any double blank lines that might creep in
    # (markdownlint MD012). Trailing single newline at EOF is canonical.
    raw = "\n".join(lines) + "\n"
    while "\n\n\n" in raw:
        raw = raw.replace("\n\n\n", "\n\n")
    path.write_text(raw, encoding="utf-8")


# =========================================================================
# Driver
# =========================================================================


def run(
    output_dir: Path,
    workers: int,
    flex: bool,
    limit: int | None = None,
) -> int:
    """Top-level driver: enumerate, classify, aggregate, write outputs.

    Args:
        output_dir: Root directory for all output artefacts.
        workers: ThreadPoolExecutor concurrency.
        flex: Use flex service tier (50 % discount).
        limit: Optional cap on the number of FPs processed (smoke test).

    Returns:
        Exit code: 0 success, 2 hard-cap exceeded, 3 input missing.
    """
    setup_logging()
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    # 1. Enumerate FPs across all four runs.
    logger.info("Enumerating FPs across %d runs", len(RUN_CSV_PATHS))
    try:
        fps = enumerate_all_fps()
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 3
    if limit:
        logger.info("Smoke test: limiting to first %d FPs", limit)
        fps = fps[:limit]
    n_fps = len(fps)
    logger.info("Total FPs to classify: %d", n_fps)

    # 2. Initialise Gemini client.
    if not config.GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY not found in environment.")
        return 3

    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=config.GOOGLE_API_KEY,
        http_options={"api_version": "v1alpha"},
    )

    # Resolve model name (preview-suffix fallback if needed).
    model_cfg = "gemini-3-flash"
    try:
        available = {
            m.name.removeprefix("models/") for m in client.models.list()
        }
        if model_cfg not in available:
            preview = f"{model_cfg}-preview"
            if preview in available:
                logger.info(
                    "Model '%s' not available; using '%s'", model_cfg, preview,
                )
                model_cfg = preview
            else:
                logger.error(
                    "Model '%s' not available (preview also missing).",
                    model_cfg,
                )
                return 3
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Could not list models (%s); proceeding with '%s'",
            exc, model_cfg,
        )

    # Build generation config — minimal thinking, T=0, JSON response,
    # safety off (this is archaeological / neutral content). Flex
    # service tier applied here.
    gen_kwargs: dict[str, Any] = {
        "temperature": 0.0,
        "max_output_tokens": 1024,
        "response_mime_type": "application/json",
        "thinking_config": types.ThinkingConfig(thinking_level="MINIMAL"),
        "safety_settings": [
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT", threshold="OFF",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF",
            ),
        ],
    }
    if flex:
        gen_kwargs["service_tier"] = "flex"
    gen_config = types.GenerateContentConfig(**gen_kwargs)

    logger.info(
        "Model: %s | flex tier: %s | workers: %d", model_cfg, flex, workers,
    )

    # 3. Classify in parallel.
    results: list[ClassificationResult] = []
    completed = 0
    failed = 0
    cumulative_in_tok = 0
    cumulative_out_tok = 0
    halted_at_cap = False
    t_start = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                render_and_classify, fp, client, model_cfg, gen_config,
            ): fp
            for fp in fps
        }
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            results.append(res)
            completed += 1
            cumulative_in_tok += res.input_tokens
            cumulative_out_tok += res.output_tokens
            if not res.success:
                failed += 1
            if completed % 50 == 0 or completed == n_fps:
                elapsed = time.time() - t_start
                rate = completed / elapsed if elapsed > 0 else 0
                cost_so_far = compute_cost(
                    cumulative_in_tok, cumulative_out_tok, flex=flex,
                )
                logger.info(
                    "Progress %d/%d (%.1f calls/s) | failed %d | "
                    "tokens in/out %d/%d | est cost $%.4f",
                    completed, n_fps, rate, failed,
                    cumulative_in_tok, cumulative_out_tok, cost_so_far,
                )
                # Hard-cap guard.
                if cost_so_far > COST_HARD_CAP_USD:
                    logger.error(
                        "Hard-cap exceeded ($%.4f > $%.2f) — halting.",
                        cost_so_far, COST_HARD_CAP_USD,
                    )
                    # Cancel pending futures.
                    for f in futures:
                        f.cancel()
                    halted_at_cap = True
                    break

    wall_clock = time.time() - t_start

    # 4. Aggregate per-run distributions.
    runs = list(RUN_CSV_PATHS.keys())
    counts = per_run_distribution(results, runs, CATEGORIES)
    weighted = confidence_weighted_distribution(results, runs, CATEGORIES)
    chi2 = chi_square_image_vs_text(counts, CATEGORIES)
    n_classified = sum(1 for r in results if r.success)

    # 5. Per-run cost breakdown.
    per_run_tokens: dict[str, tuple[int, int, int]] = {}
    for run_label in runs:
        run_results = [r for r in results if r.fp.run == run_label]
        n_calls = len(run_results)
        in_tok = sum(r.input_tokens for r in run_results)
        out_tok = sum(r.output_tokens for r in run_results)
        per_run_tokens[run_label] = (n_calls, in_tok, out_tok)

    # 6. Write outputs.
    write_classifications_json(results, output_dir / "fp_classifications.json")
    write_distribution_json(
        counts, weighted, chi2, runs, CATEGORIES, n_classified,
        output_dir / "category_distribution.json",
    )
    write_distribution_figure(
        counts, runs, CATEGORIES,
        figures_dir / "category_distribution.png",
    )
    cost_total = compute_cost(
        cumulative_in_tok, cumulative_out_tok, flex=flex,
    )
    write_cost_summary(
        per_run_tokens, flex=flex, wall_clock_seconds=wall_clock,
        path=output_dir / "cost_summary.json",
    )
    write_report_md(
        counts=counts,
        weighted=weighted,
        chi2=chi2,
        runs=runs,
        categories=CATEGORIES,
        n_total=n_classified,
        n_failed=failed,
        cost_total=cost_total,
        wall_clock_seconds=wall_clock,
        path=output_dir / "report.md",
    )

    logger.info(
        "Done. Classified %d / %d (failed %d). Wall %0.1fs. Cost ~$%.4f. "
        "Outputs in %s",
        n_classified, n_fps, failed, wall_clock, cost_total, output_dir,
    )
    return 2 if halted_at_cap else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output-dir", type=Path,
        default=REPO_ROOT / "results/55maps-fp-classification",
        help="Output directory for results (default: %(default)s)",
    )
    p.add_argument(
        "--workers", type=int, default=20,
        help="Parallel workers for the API loop (default: 20)",
    )
    p.add_argument(
        "--no-flex", action="store_true",
        help="Disable flex tier (uses standard pricing; default off).",
    )
    p.add_argument(
        "--limit", type=int, default=None,
        help="Smoke test: cap N FPs (default: no cap).",
    )
    args = p.parse_args()
    return run(
        output_dir=args.output_dir,
        workers=args.workers,
        flex=not args.no_flex,
        limit=args.limit,
    )


if __name__ == "__main__":
    sys.exit(main())
