#!/usr/bin/env python3
"""
Gold-standard FP-Class Classification Driver (Obs 302 follow-up).
=================================================================

Description
-----------
Classifies all 371 detections in the gold-standard (GS) verified-v1
full-scope set (``outputs/h11/gold-standard-v2/verified-v1/``) by the
cartographic feature most likely responsible for the detection — the
GS-side comparator that the original Obs 302 diagnostic flagged as
missing. The 55-map sibling driver
(``scripts/55maps-fp-classify.py``, commit ``5040f5b4``) tests Shawn's
hypothesis that 55-map FPs concentrate on numbers / benchmarks
(distractor-pull); this script closes the loop by tabulating the same
closed-list category distribution on the GS corpus.

Framing — different mechanisms, comparable rigour
-------------------------------------------------
The 55-map driver derives its FP set from human reviewer overrides
(``human_label == "not_mound"`` on noisy student GT). The GS pipeline
has no equivalent per-detection review step — but the GS curator GT
(``inputs/vectors/references/mounds-reference.geojson``, 569 mounds)
was triple-checked and manually re-centred to within ~1 px of each
mound's true centre during Sobotkova 2022 + this project's reverify
pass — sub-metre positional precision. Distance-from-curator-GT is
therefore not a proxy on the GS corpus; it is a high-precision
geometric filter equivalent in rigour to the 55-map's per-detection
human review. See ``planning/gs-fp-classification-plan-2026-04-29.md``
§2 for the full framing.

Methodology — cartographic-naming approach
------------------------------------------
This driver reuses the 55-map prompt and closed-list categories
verbatim — symmetric methodology is required for cross-corpus
comparability. Categories: number, benchmark, water-feature,
contour-ring, vegetation, settlement, road-or-track,
scale-bar-or-grid, none, other.

Pipeline
--------
1. Read the verified-v1 GeoJSON (371 detections) and curator GT (569
   mounds, exploded MultiPoint -> Point).
2. Compute Euclidean planar distance from each detection to its
   nearest curator GT mound via ``scipy.spatial.cKDTree``
   (EPSG:32635 native CRS for both files, no reprojection).
3. Render 150x150 m crops in-memory from the four GS GeoTIFFs at
   ``inputs/rasters/`` (top level — distinct from the 55-map driver's
   ``inputs/rasters/Russian1981_32635/`` directory).
4. Classify each crop via Gemini 3 Flash (``service_tier="flex"``,
   parallel ThreadPoolExecutor workers).
5. Partition results post-hoc into TP-side (<= threshold) and FP-side
   (> threshold) buckets at five thresholds {25, 50, 75, 100, 125} m;
   tabulate distributions per bucket. Sensitivity sweep is a
   post-classification aggregation (a single API pass classifies
   every detection regardless of distance — see plan §6 for the
   "sanity check on classifier reliability" rationale for classifying
   TP-side detections as well).
6. Cross-corpus chi-square test against the 55-map text-track
   aggregate distribution (the comparator that closes the Obs 302
   gap).
7. Write JSON results, Markdown report, and stacked-bar figures.

Robust JSON parsing: handles dict-shaped payloads, list-of-dict
wrapping (mirrors ``_unwrap_verdict_payload`` from
``scripts/lib_verifier.py``, commit ``acba8999``), and retries on
transient errors.

Cost
----
371 calls expected. At ~$0.00045 per call (per the 55-map driver's
realised per-call cost: $0.5071 / 1119 calls), expect ~$0.17 USD with
flex tier. Hard-cap at $5.00 (driver halts and reports actuals);
user-approved API ceiling for this run is also $5.00.

Outputs
-------
``results/gs-fp-classification/``:

- ``fp_classifications.json`` — per-detection record (candidate_id,
  x, y, source_tile, map_name, dist_to_nearest_curator_GT, category,
  confidence, rationale, token usage).
- ``category_distribution.json`` — TP-side and per-threshold FP-side
  distributions; cross-corpus chi-square test versus 55-map
  text-track aggregate.
- ``report.md`` — synthesis with TP-side reliability check, FP-side
  per-threshold tables, cross-corpus comparison, and Obs 302
  follow-up framing.
- ``figures/category_distribution.png`` — stacked-bar chart with
  TP-side and per-threshold FP-side columns.
- ``figures/cross_corpus_comparison.png`` — side-by-side bars
  comparing the GS-FP aggregate (50 m primary) with the 55-map
  text-track aggregate.
- ``cost_summary.json`` — actual API spend.

Usage
-----
.. code-block:: bash

    python scripts/gs-fp-classify.py \\
        --workers 4 \\
        --thresholds 25,50,75,100,125 \\
        --output-dir results/gs-fp-classification

Created
-------
2026-04-29 — Claude Code (Opus 4.7) for Shawn Ross. Sibling to
``scripts/55maps-fp-classify.py`` (do not modify; the two drivers
share helper signatures by copy, not by import — see plan §9).

Licence
-------
Apache 2.0
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import io
import json
import logging
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from PIL import Image
from rasterio.windows import Window
from scipy import stats
from scipy.spatial import cKDTree

# Project-root imports — config + lib_verifier patterns.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import config  # noqa: E402  — must follow sys.path mutation


# =========================================================================
# Constants and configuration
# =========================================================================

# Verified-v1 detections (371 features, EPSG:32635). Path is the canonical
# operating-point output described in
# ``planning/gs-fp-classification-plan-2026-04-29.md`` §1.
DETECTIONS_PATH: Path = REPO_ROOT / (
    "outputs/h11/gold-standard-v2/verified-v1/"
    "verified_detections_full-scope.geojson"
)

# Curator-corrected GT (569 mounds, MultiPoint, EPSG:32635). Triple-checked
# sub-metre positional precision — see plan §2.2.
REFERENCE_PATH: Path = REPO_ROOT / (
    "inputs/vectors/references/mounds-reference.geojson"
)

# Source rasters live at the TOP LEVEL of the rasters directory on the
# GS corpus (the four GS map sheets), distinct from the 55-map driver's
# ``inputs/rasters/Russian1981_32635/`` (where the 55 sheets live).
RASTERS_DIR = REPO_ROOT / "inputs/rasters"

# 55-map result file used as the cross-corpus comparator in the
# headline chi-square test (cf. plan §11.1).
COMPARATOR_55MAP_DISTRIBUTION_PATH: Path = REPO_ROOT / (
    "results/55maps-fp-classification/category_distribution.json"
)

# Run label — the GS pipeline has only one operating point, so we use a
# single label per record (the 55-map driver labels by run T0.3 / T0.7 /
# image / text-MIN). See plan §9.1 item 4.
RUN_LABEL: str = "GS_full"

# Distance thresholds (metres) for the post-classification sensitivity
# sweep. 50 m is the primary; the others form the sensitivity envelope
# documented in plan §5.1 / §5.3.
DEFAULT_THRESHOLDS_M: tuple[int, ...] = (25, 50, 75, 100, 125)

# Primary threshold: the headline FP partition (plan §5.2). Used for
# the cross-corpus chi-square comparator and the headline
# distractor-pull / GS-failure-mode tables.
PRIMARY_THRESHOLD_M: int = 50

# Crop size in metres (matches the Obs 296 / Test #2 spec).
CROP_SIZE_M: float = 150.0

# Display upscale: render the metric-window then upscale to this px size
# so symbol detail is legible to the VLM at ~5 m/px native resolution.
# Match the value used by review_candidates.py for visual parity.
DISPLAY_PX: int = 768

# Closed category list — matches the prompt below verbatim. The order
# here drives the order in the report tables and the figure legend.
CATEGORIES: list[str] = [
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
centre of the crop could have triggered the detector?

Choose ONE category from this closed list (Soviet 1980s topographic \
conventions). When in doubt, prefer the more specific category over "other".

- number — spot-elevation numeric label, often small italic digits, sometimes \
with a dot below
- benchmark — bench-mark or triangulation marker (cross, triangle, "БМ" or "Δ")
- water-feature — blue river, stream, lake, pond, swamp, drainage symbol, or \
well marker
- contour-ring — closed contour line(s) forming a ring or oval (brown), often \
around a small hill or depression
- vegetation — green-shaded area, tree or shrub symbol, or forest-edge marking
- settlement — house symbol(s), village or hamlet outline, or other \
built-feature cluster
- road-or-track — line symbol for transport (single line, double line, dashed)
- scale-bar-or-grid — printed scale bar, grid intersection, or coordinate label
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
# Detection enumeration (GS-side: verified-v1 GeoJSON + cKDTree distance)
# =========================================================================


@dataclass(frozen=True, slots=True)
class FPRecord:
    """A single GS detection record fed to the classifier.

    The class name is preserved from the 55-map driver (``FPRecord``)
    for code symmetry, but on the GS side every detection — both
    TP-side (<= primary threshold from a curator GT mound) and
    FP-side (> primary threshold) — is processed in a single pass.
    The ``dist_m`` field carries the nearest-curator-GT distance used
    for post-classification bucketing.

    Frozen + slotted so records can be used as worker arguments across
    threads safely.
    """

    run: str
    candidate_id: str
    map_name: str
    x: float
    y: float
    source_tile: str
    dist_m: float


def _map_name_from_source_tile(source_tile: str) -> str:
    """Derive a human-readable map name from a tiled source-tile filename.

    Source tiles look like ``K-35-052-4_32635_x3024_y2016.png``. The
    map name is the prefix before the first ``_x`` token. If the
    pattern doesn't match we fall back to the raw value.
    """
    if not source_tile:
        return ""
    # Conventional split on ``_x`` (the x-pixel-offset marker).
    for marker in ("_x", "_X"):
        idx = source_tile.find(marker)
        if idx > 0:
            return source_tile[:idx]
    # Fall back to stem.
    return Path(source_tile).stem


def load_gs_detections(
    detection_path: Path = DETECTIONS_PATH,
    reference_path: Path = REFERENCE_PATH,
) -> list[FPRecord]:
    """Load GS detections + nearest-curator-GT distance per detection.

    Reads the verified-v1 detections GeoJSON (371 features) and the
    curator-corrected reference GeoJSON (569 MultiPoint mounds), then
    computes the Euclidean planar distance from each detection to its
    nearest reference Point via ``scipy.spatial.cKDTree``. Both files
    are EPSG:32635 (verified at session start), so no reprojection is
    needed.

    Args:
        detection_path: Path to the verified-v1 detections GeoJSON.
        reference_path: Path to the curator GT (``mounds-reference``).

    Returns:
        List of ``FPRecord`` for every detection. Every detection is
        included regardless of distance — bucketing into TP-side /
        FP-side happens at aggregation time (see plan §6 / §8).
    """
    if not detection_path.is_file():
        raise FileNotFoundError(f"Detections file missing: {detection_path}")
    if not reference_path.is_file():
        raise FileNotFoundError(f"Reference file missing: {reference_path}")

    # Load + verify CRS.
    det = gpd.read_file(detection_path)
    if det.crs is None or str(det.crs).upper() != "EPSG:32635":
        raise ValueError(
            f"Detections CRS expected EPSG:32635; got {det.crs}"
        )
    ref = gpd.read_file(reference_path)
    if ref.crs is None or str(ref.crs).upper() != "EPSG:32635":
        raise ValueError(f"Reference CRS expected EPSG:32635; got {ref.crs}")

    # Explode MultiPoint -> Point so cKDTree sees a 2D coords array.
    ref_pts = ref.explode(index_parts=False).reset_index(drop=True)
    ref_coords = np.column_stack(
        [ref_pts.geometry.x.values, ref_pts.geometry.y.values],
    )
    det_coords = np.column_stack(
        [det.geometry.x.values, det.geometry.y.values],
    )

    tree = cKDTree(ref_coords)
    distances, _ = tree.query(det_coords, k=1)

    records: list[FPRecord] = []
    for (_, row), d in zip(det.iterrows(), distances):
        # ``candidate_id`` may be int or str in the GeoJSON; coerce to str
        # for downstream JSON serialisation symmetry with the 55-map driver.
        cand_id = row.get("candidate_id")
        cand_id_str = str(cand_id) if cand_id is not None else ""
        source_tile = str(row.get("source_tile", ""))
        records.append(FPRecord(
            run=RUN_LABEL,
            candidate_id=cand_id_str,
            map_name=_map_name_from_source_tile(source_tile),
            x=float(row.geometry.x),
            y=float(row.geometry.y),
            source_tile=source_tile,
            dist_m=float(d),
        ))
    logger.info(
        "Loaded %d detections; distance distribution: "
        "min=%.2f median=%.2f max=%.2f m",
        len(records), distances.min(),
        float(np.median(distances)), distances.max(),
    )
    return records


def bucket_records(
    records: list[FPRecord], threshold_m: float,
) -> tuple[list[FPRecord], list[FPRecord]]:
    """Split records into TP-side (<= threshold) and FP-side (> threshold).

    Uses the ``dist_m`` (nearest-curator-GT distance) field that
    ``load_gs_detections`` attaches to each record.

    Args:
        records: All loaded detections (no pre-filtering).
        threshold_m: Distance threshold in metres.

    Returns:
        ``(tp_records, fp_records)`` lists.
    """
    tp = [r for r in records if r.dist_m <= threshold_m]
    fp = [r for r in records if r.dist_m > threshold_m]
    return tp, fp


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


def counts_for_records(
    results: list[ClassificationResult],
    record_subset: list[FPRecord],
    categories: list[str],
    confidence_floor: float = 0.0,
) -> dict[str, int]:
    """Category counts restricted to a record subset (e.g. TP-side bucket).

    The subset is identified by the ``(run, candidate_id)`` tuple of
    each ``FPRecord``. Successful classifications from records not in
    the subset are ignored — this lets a single classification pass
    drive multiple post-hoc partitions (TP-side, FP-side at any
    threshold).

    Args:
        results: All ``ClassificationResult`` from the API run.
        record_subset: Records to include in the count.
        categories: Closed list of category labels (column order).
        confidence_floor: Drop classifications with confidence below
            this threshold (0.0 = include all).

    Returns:
        ``dict[category -> count]`` over the subset.
    """
    keys = {(r.run, r.candidate_id) for r in record_subset}
    out: dict[str, int] = {c: 0 for c in categories}
    for r in results:
        if not r.success:
            continue
        if r.confidence < confidence_floor:
            continue
        if (r.fp.run, r.fp.candidate_id) not in keys:
            continue
        if r.category in out:
            out[r.category] += 1
    return out


def confidence_weighted_for_records(
    results: list[ClassificationResult],
    record_subset: list[FPRecord],
    categories: list[str],
) -> dict[str, float]:
    """Per-record-subset distribution weighted by per-call confidence.

    Records with low confidence contribute fractionally to their
    category mass; the column sum equals the sum of confidences for
    that subset, not its n.
    """
    keys = {(r.run, r.candidate_id) for r in record_subset}
    out: dict[str, float] = {c: 0.0 for c in categories}
    for r in results:
        if not r.success:
            continue
        if (r.fp.run, r.fp.candidate_id) not in keys:
            continue
        if r.category in out:
            out[r.category] += float(r.confidence)
    return out


def load_55map_text_track_aggregate(
    path: Path = COMPARATOR_55MAP_DISTRIBUTION_PATH,
) -> dict[str, int] | None:
    """Reconstruct the 55-map text-track aggregate counts.

    The 55-map ``category_distribution.json`` writes per-run counts
    keyed by ``T0.3``, ``T0.7``, ``image``, ``text-MIN``. The
    text-track aggregate is the sum across the three text runs (i.e.
    everything except ``image``). This is the comparator used in the
    cross-corpus chi-square test (plan §11.1, plan §9.1 item 5).

    Args:
        path: Path to the 55-map ``category_distribution.json``.

    Returns:
        ``dict[category -> count]`` for the text-track aggregate, or
        ``None`` if the file does not exist or has unexpected shape.
    """
    if not path.is_file():
        logger.warning(
            "55-map comparator file missing: %s", path,
        )
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        counts = doc.get("counts", {})
        runs = doc.get("runs", [])
        categories = doc.get("categories", [])
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning(
            "Could not parse 55-map comparator %s: %s", path, exc,
        )
        return None
    text_runs = [r for r in runs if r != "image"]
    if not text_runs:
        return None
    agg: dict[str, int] = {c: 0 for c in categories}
    for run in text_runs:
        for cat in categories:
            agg[cat] += int(counts.get(run, {}).get(cat, 0))
    return agg


def chi_square_two_distributions(
    distribution_a: dict[str, int],
    distribution_b: dict[str, int],
    categories: list[str],
    label_a: str,
    label_b: str,
) -> dict[str, Any]:
    """Two-distribution chi-square test (with Pearson residuals).

    Generic helper used here for the cross-corpus comparison
    (GS-FP aggregate vs 55-map text-track aggregate at the primary
    threshold). Returns the chi-square statistic, degrees of freedom,
    p-value, expected counts, and per-category Pearson residuals.

    Falls through with ``insufficient_data=True`` if either row is
    empty or fewer than two non-zero categories remain after dropping
    all-zero columns. When >20 % of cells have expected counts < 5,
    also computes Fisher's exact / Monte Carlo p-value as a small-N
    fallback (plan §13.3).
    """
    if not distribution_a or not distribution_b:
        return {"insufficient_data": True, "reason": "missing track(s)"}

    a_row = [distribution_a.get(c, 0) for c in categories]
    b_row = [distribution_b.get(c, 0) for c in categories]
    table = np.array([a_row, b_row], dtype=float)

    # Both rows must carry mass for chi-square to be defined.
    if table[0].sum() == 0 or table[1].sum() == 0:
        return {
            "insufficient_data": True,
            "reason": "one track has zero classified records",
            "n_a": int(table[0].sum()),
            "n_b": int(table[1].sum()),
        }

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

    # Per plan §13.3: if >20 % of cells have expected counts < 5,
    # also report a Monte Carlo p-value (simulated null) as a small-N
    # robustness check. Two scipy quirks to handle:
    # 1. ``correction=True`` (the default) is incompatible with the
    #    resampling method, so we disable Yates's correction for the
    #    MC run only — the asymptotic p-value above keeps default.
    # 2. ``PermutationMethod`` internally rebuilds the contingency
    #    table from per-record samples (``[i] * table[i, j]``) which
    #    fails on a float-typed observed array. Cast to int before
    #    handing the table to the resampling routine.
    expected_arr = np.asarray(expected, dtype=float)
    low_exp_frac = float((expected_arr < 5).mean())
    monte_carlo_p: float | None = None
    if low_exp_frac > 0.20:
        try:
            mc_result = stats.chi2_contingency(
                table_kept.astype(int),
                correction=False,
                method=stats.PermutationMethod(n_resamples=10000),
            )
            monte_carlo_p = float(mc_result.pvalue)
        except (TypeError, ValueError):
            # Older scipy may not accept PermutationMethod here; leave
            # the asymptotic p-value as the only reported value.
            monte_carlo_p = None

    # Pearson residuals — (observed - expected) / sqrt(expected).
    # Reported per-category with sign so we can read the direction.
    residuals = (table_kept - expected) / np.sqrt(expected)
    per_category_res = []
    for j, cat in enumerate(cats_kept):
        per_category_res.append({
            "category": cat,
            f"{label_a}_observed": int(table_kept[0, j]),
            f"{label_b}_observed": int(table_kept[1, j]),
            f"{label_a}_expected": float(round(expected[0, j], 3)),
            f"{label_b}_expected": float(round(expected[1, j], 3)),
            f"{label_a}_residual": float(round(residuals[0, j], 3)),
            f"{label_b}_residual": float(round(residuals[1, j], 3)),
        })

    out = {
        "insufficient_data": False,
        "label_a": label_a,
        "label_b": label_b,
        "chi2": float(chi2),
        "p_value": float(p_value),
        "dof": int(dof),
        f"n_{label_a}": int(table[0].sum()),
        f"n_{label_b}": int(table[1].sum()),
        "categories_used": cats_kept,
        "low_expected_count_fraction": round(low_exp_frac, 3),
        "per_category": per_category_res,
    }
    if monte_carlo_p is not None:
        out["monte_carlo_p_value"] = monte_carlo_p
        out["monte_carlo_resamples"] = 10000
    return out


# =========================================================================
# Output writers
# =========================================================================


def write_classifications_json(
    results: list[ClassificationResult],
    records: list[FPRecord],
    primary_threshold_m: int,
    path: Path,
) -> None:
    """Write per-detection classification records to JSON.

    Each row carries the GS-specific fields ``dist_to_nearest_curator_GT_m``
    (Euclidean planar distance, EPSG:32635) and ``bucket_primary``
    (TP-side / FP-side at the primary 50 m threshold), so downstream
    consumers can re-bucket without recomputing distances.

    Args:
        results: Classification results from the API run.
        records: Original ``FPRecord`` list (carries the
            ``dist_m`` distance field).
        primary_threshold_m: Distance threshold (m) at which the
            ``bucket_primary`` column is computed.
        path: Output JSON path.
    """
    # Build a lookup from (run, candidate_id) -> dist_m so we can
    # decorate each row with its distance even if the result didn't
    # capture it directly.
    dist_lookup = {
        (r.run, r.candidate_id): r.dist_m for r in records
    }
    rows = []
    for r in results:
        dist = dist_lookup.get(
            (r.fp.run, r.fp.candidate_id), float(r.fp.dist_m),
        )
        bucket = "tp_side" if dist <= primary_threshold_m else "fp_side"
        rows.append({
            "run": r.fp.run,
            "candidate_id": r.fp.candidate_id,
            "map_name": r.fp.map_name,
            "x": r.fp.x,
            "y": r.fp.y,
            "source_tile": r.fp.source_tile,
            "dist_to_nearest_curator_GT_m": round(float(dist), 3),
            "bucket_primary": bucket,
            "primary_threshold_m": primary_threshold_m,
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


def _percent_dict(
    counts: dict[str, int], categories: list[str],
) -> dict[str, float]:
    """Return ``{category: percent}`` rounded to two decimal places."""
    total = sum(counts.values())
    if total == 0:
        return {c: 0.0 for c in categories}
    return {c: round(100.0 * counts.get(c, 0) / total, 2) for c in categories}


def write_distribution_json(
    tp_counts: dict[str, int],
    tp_weighted: dict[str, float],
    fp_counts_by_threshold: dict[int, dict[str, int]],
    cross_corpus_chi2: dict[str, Any],
    cross_corpus_chi2_by_threshold: dict[int, dict[str, Any]],
    fifty_five_text_aggregate: dict[str, int] | None,
    categories: list[str],
    n_total: int,
    primary_threshold_m: int,
    thresholds_m: list[int],
    path: Path,
) -> None:
    """Write the TP-side + per-threshold FP-side distributions + chi-square.

    Args:
        tp_counts: TP-side category counts at the primary threshold.
        tp_weighted: TP-side confidence-weighted category counts.
        fp_counts_by_threshold: ``{threshold_m -> {category -> count}}``
            for each threshold in the sensitivity sweep.
        cross_corpus_chi2: Result from
            ``chi_square_two_distributions`` against the 55-map
            text-track aggregate at the primary threshold.
        fifty_five_text_aggregate: Reconstructed 55-map text-track
            aggregate counts (or ``None`` if comparator unavailable).
        categories: Closed-list category labels (column order).
        n_total: Total successfully classified detections.
        primary_threshold_m: Primary threshold (m) used for the headline
            partition and the cross-corpus chi-square.
        thresholds_m: Full list of thresholds in the sweep.
        path: Output JSON path.
    """
    fp_pct = {
        thr: _percent_dict(fp_counts_by_threshold[thr], categories)
        for thr in thresholds_m
    }
    tp_pct = _percent_dict(tp_counts, categories)
    doc = {
        "version": "1.0",
        "n_total_classified": n_total,
        "categories": categories,
        "primary_threshold_m": primary_threshold_m,
        "thresholds_m": thresholds_m,
        "tp_side_at_primary": {
            "counts": tp_counts,
            "percentages": tp_pct,
            "weighted_by_confidence": tp_weighted,
            "n": sum(tp_counts.values()),
        },
        "fp_side_by_threshold": {
            str(thr): {
                "counts": fp_counts_by_threshold[thr],
                "percentages": fp_pct[thr],
                "n": sum(fp_counts_by_threshold[thr].values()),
            }
            for thr in thresholds_m
        },
        "cross_corpus_chi_square_primary": cross_corpus_chi2,
        "cross_corpus_chi_square_by_threshold": {
            str(thr): cross_corpus_chi2_by_threshold[thr]
            for thr in thresholds_m
        },
        "comparator_55map_text_track_aggregate": fifty_five_text_aggregate,
    }
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")


def write_cost_summary(
    n_calls: int,
    input_tokens: int,
    output_tokens: int,
    flex: bool,
    wall_clock_seconds: float,
    path: Path,
) -> None:
    """Write total token counts and estimated cost for the single GS run.

    Args:
        n_calls: Total successful + failed API calls.
        input_tokens: Aggregate input tokens.
        output_tokens: Aggregate output tokens.
        flex: Whether flex-tier discount was assumed.
        wall_clock_seconds: Total wall-clock time of the API loop.
        path: Output JSON path.
    """
    cost = compute_cost(input_tokens, output_tokens, flex=flex)
    doc = {
        "version": "1.0",
        "flex_tier_assumed": flex,
        "pricing": {
            "model": "gemini-3-flash",
            "input_per_1m_usd": PRICE_INPUT_PER_MTOK,
            "output_per_1m_usd": PRICE_OUTPUT_PER_MTOK,
            "flex_discount_factor": FLEX_DISCOUNT if flex else 1.0,
        },
        "per_run": {
            RUN_LABEL: {
                "n_calls": n_calls,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": round(cost, 4),
            },
        },
        "totals": {
            "n_calls": n_calls,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 4),
        },
        "wall_clock_seconds": round(wall_clock_seconds, 1),
        "wall_clock_pretty": (
            f"{wall_clock_seconds // 60:.0f}m {wall_clock_seconds % 60:.0f}s"
        ),
    }
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")


def write_distribution_figure(
    tp_counts: dict[str, int],
    fp_counts_by_threshold: dict[int, dict[str, int]],
    categories: list[str],
    thresholds_m: list[int],
    path: Path,
) -> None:
    """Plot a stacked bar chart: TP-side + per-threshold FP-side columns.

    Args:
        tp_counts: TP-side counts at the primary threshold.
        fp_counts_by_threshold: Per-threshold FP-side counts.
        categories: Category order (legend / stacking order).
        thresholds_m: Thresholds in the sweep (column order after TP).
        path: Output PNG path.
    """
    column_labels = ["TP-side\n(<=50 m)"] + [
        f"FP\n>{thr} m" for thr in thresholds_m
    ]
    columns = [tp_counts] + [
        fp_counts_by_threshold[thr] for thr in thresholds_m
    ]
    n_cols = len(column_labels)
    pct_matrix = np.zeros((len(categories), n_cols), dtype=float)
    n_per_col = []
    for j, col in enumerate(columns):
        col_total = sum(col.values())
        n_per_col.append(col_total)
        if col_total <= 0:
            continue
        for i, cat in enumerate(categories):
            pct_matrix[i, j] = 100.0 * col.get(cat, 0) / col_total

    palette = plt.get_cmap("tab10").colors
    fig, ax = plt.subplots(figsize=(9.0, 5.5), dpi=140)
    bottoms = np.zeros(n_cols, dtype=float)
    for i, cat in enumerate(categories):
        ax.bar(
            column_labels, pct_matrix[i],
            bottom=bottoms,
            label=cat,
            color=palette[i % len(palette)],
            edgecolor="white",
            linewidth=0.4,
        )
        bottoms += pct_matrix[i]
    # Annotate bar tops with N for transparency at low FP counts.
    for j, n in enumerate(n_per_col):
        ax.text(
            j, 102.0, f"n={n}",
            ha="center", va="bottom", fontsize=8,
        )
    ax.set_ylabel("Percentage of detections (%)")
    ax.set_xlabel("Bucket")
    ax.set_title(
        "GS FP-class distribution: TP-side + FP-side per threshold "
        "(Obs 302 follow-up)\n"
        "Cartographic categories from Gemini 3 Flash classification",
        fontsize=10,
    )
    ax.set_ylim(0, 110)
    ax.legend(
        bbox_to_anchor=(1.02, 1.0), loc="upper left",
        frameon=False, fontsize=8, title="category",
    )
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_cross_corpus_figure(
    gs_fp_primary_counts: dict[str, int],
    fifty_five_text_aggregate: dict[str, int] | None,
    categories: list[str],
    primary_threshold_m: int,
    path: Path,
) -> None:
    """Plot side-by-side stacked bars: GS-FP primary vs 55-map text-track.

    The headline cross-corpus visualisation referenced in plan §11.1 /
    §7.2. Columns: ``GS FP (>50 m)`` and ``55-map text-track aggregate``.

    Args:
        gs_fp_primary_counts: GS FP-side counts at the primary threshold.
        fifty_five_text_aggregate: Reconstructed 55-map text-track
            aggregate counts; ``None`` -> figure not written.
        categories: Category order (legend / stacking order).
        primary_threshold_m: Primary threshold (m), used in the title.
        path: Output PNG path.
    """
    if fifty_five_text_aggregate is None:
        logger.warning(
            "55-map text-track aggregate unavailable; skipping cross-corpus "
            "figure at %s", path,
        )
        return
    columns = [gs_fp_primary_counts, fifty_five_text_aggregate]
    column_labels = [
        f"GS FP\n(>{primary_threshold_m} m)",
        "55-map\ntext-track aggregate",
    ]
    n_cols = len(columns)
    pct_matrix = np.zeros((len(categories), n_cols), dtype=float)
    n_per_col = []
    for j, col in enumerate(columns):
        col_total = sum(col.values())
        n_per_col.append(col_total)
        if col_total <= 0:
            continue
        for i, cat in enumerate(categories):
            pct_matrix[i, j] = 100.0 * col.get(cat, 0) / col_total
    palette = plt.get_cmap("tab10").colors
    fig, ax = plt.subplots(figsize=(7.5, 5.5), dpi=140)
    bottoms = np.zeros(n_cols, dtype=float)
    for i, cat in enumerate(categories):
        ax.bar(
            column_labels, pct_matrix[i],
            bottom=bottoms,
            label=cat,
            color=palette[i % len(palette)],
            edgecolor="white",
            linewidth=0.4,
        )
        bottoms += pct_matrix[i]
    for j, n in enumerate(n_per_col):
        ax.text(
            j, 102.0, f"n={n}",
            ha="center", va="bottom", fontsize=8,
        )
    ax.set_ylabel("Percentage of FPs (%)")
    ax.set_title(
        "Cross-corpus FP-class comparison (Obs 302 follow-up)\n"
        "GS at the primary threshold vs 55-map text-track aggregate",
        fontsize=10,
    )
    ax.set_ylim(0, 110)
    ax.legend(
        bbox_to_anchor=(1.02, 1.0), loc="upper left",
        frameon=False, fontsize=8, title="category",
    )
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _format_chi2_block(chi2: dict[str, Any], label_a: str, label_b: str) -> list[str]:
    """Render a chi-square test result as Markdown lines for the report."""
    lines: list[str] = []
    if chi2.get("insufficient_data"):
        lines.append(
            f"Insufficient data for chi-square test "
            f"({chi2.get('reason', 'unknown')})."
        )
        lines.append("")
        return lines
    lines.append(f"- chi-squared statistic: {chi2['chi2']:.3f}")
    lines.append(f"- degrees of freedom: {chi2['dof']}")
    lines.append(f"- p-value: {chi2['p_value']:.4g}")
    lines.append(f"- n ({label_a}): {chi2[f'n_{label_a}']}")
    lines.append(f"- n ({label_b}): {chi2[f'n_{label_b}']}")
    lines.append(
        f"- categories retained (non-zero across both rows): "
        f"{', '.join(chi2['categories_used'])}"
    )
    lines.append(
        f"- low-expected-count fraction (< 5): "
        f"{chi2.get('low_expected_count_fraction', 0.0):.2f}"
    )
    if "monte_carlo_p_value" in chi2:
        lines.append(
            f"- Monte Carlo p-value "
            f"({chi2.get('monte_carlo_resamples', 'n/a')} resamples): "
            f"{chi2['monte_carlo_p_value']:.4g} "
            "(small-N robustness check; per plan §13.3 the asymptotic "
            "p-value is unreliable when many cells have expected counts < 5)"
        )
    lines.append("")
    lines.append("### Per-category Pearson residuals")
    lines.append("")
    lines.append(
        "Pearson residuals (observed - expected) / sqrt(expected) indicate "
        "which categories drive the difference. |residual| > 2 is the "
        "conventional threshold for a meaningful per-cell effect."
    )
    lines.append("")
    lines.append(
        f"| Category | {label_a} obs | {label_a} exp | {label_a} residual | "
        f"{label_b} obs | {label_b} exp | {label_b} residual |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for r in chi2["per_category"]:
        lines.append(
            f"| {r['category']} | {r[f'{label_a}_observed']} | "
            f"{r[f'{label_a}_expected']:.1f} | "
            f"{r[f'{label_a}_residual']:+.2f} | "
            f"{r[f'{label_b}_observed']} | "
            f"{r[f'{label_b}_expected']:.1f} | "
            f"{r[f'{label_b}_residual']:+.2f} |"
        )
    lines.append("")
    return lines


def _format_distribution_table(
    columns: list[tuple[str, dict[str, int]]],
    categories: list[str],
) -> list[str]:
    """Render a category-vs-column counts/percent table."""
    lines: list[str] = []
    col_labels = [label for label, _ in columns]
    col_totals = [sum(counts.values()) for _, counts in columns]
    header = "| Category | " + " | ".join(col_labels) + " |"
    sep = "|---|" + "".join("---:|" for _ in columns)
    lines.append(header)
    lines.append(sep)
    for cat in categories:
        cells = []
        for (_, counts), total in zip(columns, col_totals):
            n = counts.get(cat, 0)
            denom = total if total > 0 else 1
            cells.append(f"{n} ({100 * n / denom:.1f} %)")
        lines.append(f"| {cat} | " + " | ".join(cells) + " |")
    lines.append(
        "| **N** | "
        + " | ".join(f"**{t}**" for t in col_totals)
        + " |"
    )
    return lines


def write_report_md(
    tp_counts: dict[str, int],
    tp_weighted: dict[str, float],
    fp_counts_by_threshold: dict[int, dict[str, int]],
    cross_corpus_chi2: dict[str, Any],
    cross_corpus_chi2_by_threshold: dict[int, dict[str, Any]],
    fifty_five_text_aggregate: dict[str, int] | None,
    categories: list[str],
    n_total: int,
    n_failed: int,
    n_records_total: int,
    cost_total: float,
    wall_clock_seconds: float,
    primary_threshold_m: int,
    thresholds_m: list[int],
    path: Path,
) -> None:
    """Write the GS-side synthesis report.

    Mirrors the structure of ``results/55maps-fp-classification/report.md``:
    Method -> per-bucket distribution -> distractor-pull share ->
    GS-failure-mode share -> chi-square -> verdict -> caveats.

    Args:
        tp_counts: TP-side category counts at the primary threshold.
        tp_weighted: Confidence-weighted TP-side counts.
        fp_counts_by_threshold: ``{threshold_m -> {category -> count}}``
            for the post-classification sensitivity sweep.
        cross_corpus_chi2: Result of the chi-square test against the
            55-map text-track aggregate at the primary threshold.
        fifty_five_text_aggregate: Reconstructed 55-map text-track
            aggregate counts (used for direct row-by-row comparison).
        categories: Closed list (row order in tables).
        n_total: Total successfully classified detections.
        n_failed: Failed / skipped detections.
        n_records_total: Count of input records before classification.
        cost_total: Estimated USD spend (flex-tier discount applied).
        wall_clock_seconds: API loop wall-clock time.
        primary_threshold_m: Primary threshold (m) for the headline.
        thresholds_m: Full sensitivity-sweep thresholds.
        path: Output report path.
    """
    fp_primary = fp_counts_by_threshold.get(primary_threshold_m, {})
    n_tp = sum(tp_counts.values())
    n_fp_primary = sum(fp_primary.values())

    lines: list[str] = []
    lines.append(
        "# GS FP-class classification (Obs 302 follow-up)"
    )
    lines.append("")
    lines.append(
        f"_Generated "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_"
    )
    lines.append("")
    lines.append(
        "Closes the comparator gap flagged in `results/"
        "55maps-fp-classification/report.md` Caveats - the 55-map driver "
        "tested Shawn's hypothesis (Obs 296) on one corpus but lacked the "
        "GS-side measurement to make a clean cross-corpus claim. This run "
        "applies the same Soviet-1980s closed-list classifier to all 371 "
        "detections in the GS verified-v1 full-scope set "
        "(`outputs/h11/gold-standard-v2/verified-v1/"
        "verified_detections_full-scope.geojson`), partitioning into "
        "TP-side (<= 50 m from a curator GT mound) and FP-side (> 50 m) "
        "post-classification. Plan reference: "
        "`planning/gs-fp-classification-plan-2026-04-29.md` "
        "(commit `edd2ecce`)."
    )
    lines.append("")

    lines.append("## Methodology - different mechanisms, comparable rigour")
    lines.append("")
    lines.append(
        "The 55-map sibling driver derives its FP set from human reviewer "
        "overrides (`human_label == \"not_mound\"`) on noisy student GT "
        "(`student-mounds-55maps-reviewed.geojson`, ~25 m positional "
        "jitter). The GS pipeline has no equivalent per-detection review "
        "step, but the GS curator GT "
        "(`inputs/vectors/references/mounds-reference.geojson`, 569 "
        "mounds) was triple-checked and manually re-centred to within "
        "~1 px of each mound's true centre during Sobotkova 2022 + this "
        "project's reverify pass - sub-metre positional precision. "
        "Distance-from-curator-GT is therefore not a proxy on the GS "
        "corpus; it is a high-precision geometric filter. See plan "
        "section 2 for the full framing."
    )
    lines.append("")

    lines.append("## Method")
    lines.append("")
    lines.append(
        "1. Loaded all 371 detections from the verified-v1 GeoJSON and "
        "569 curator GT mounds (MultiPoint -> Point exploded). Both "
        "files are EPSG:32635, no reprojection."
    )
    lines.append(
        "2. Computed Euclidean planar distance from each detection to "
        "its nearest reference Point via `scipy.spatial.cKDTree` "
        "(precedent: `scripts/analyse_attractor_pull_gs.py`)."
    )
    lines.append(
        "3. Rendered 150 x 150 m crops on-the-fly from the four GS "
        "GeoTIFFs at `inputs/rasters/` "
        "(K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1) using the "
        "live-raster pipeline mirrored from "
        "`scripts/review_candidates.py`."
    )
    lines.append(
        "4. Classified each crop via Gemini 3 Flash (flex tier, "
        "thinking_level=minimal, temperature=0.0). Closed-list "
        f"categories (verbatim from the 55-map driver): "
        f"{', '.join(categories)}."
    )
    lines.append(
        "5. Partitioned results post-hoc into TP-side "
        f"(<= {primary_threshold_m} m) and FP-side (> threshold) "
        f"buckets at thresholds {thresholds_m} m. The classification "
        "pass is a single census; the threshold sweep is a "
        "post-classification aggregation. See plan section 6 for the "
        "rationale for classifying TP-side detections as well "
        "(reliability sanity check)."
    )
    lines.append(
        "6. Cross-corpus chi-square test against the 55-map text-track "
        "aggregate "
        "(`results/55maps-fp-classification/category_distribution.json`)."
    )
    lines.append("")
    lines.append(
        f"Total classified: {n_total} / {n_records_total} "
        f"(failed/skipped: {n_failed}). "
        f"Wall-clock: {wall_clock_seconds:.1f} s "
        f"({wall_clock_seconds / 60:.1f} m). "
        f"Estimated API cost: ${cost_total:.4f} USD (flex tier)."
    )
    lines.append("")

    # Distance distribution by stratum (the user-required headline view).
    lines.append("## Distribution by distance-from-curator-GT stratum")
    lines.append("")
    lines.append(
        "The TP-side and FP-side rows below are partitioned at each "
        "sensitivity-sweep threshold so the user can see how the FP-class "
        "distribution shifts as the threshold tightens or relaxes. The "
        f"primary threshold is {primary_threshold_m} m (plan section 5.2)."
    )
    lines.append("")
    columns = [(f"TP (<={primary_threshold_m} m)", tp_counts)]
    for thr in thresholds_m:
        columns.append((f"FP (>{thr} m)", fp_counts_by_threshold[thr]))
    lines.extend(_format_distribution_table(columns, categories))
    lines.append("")

    # TP-side reliability sanity check.
    lines.append("## TP-side reliability check (plan section 6.5)")
    lines.append("")
    lines.append(
        "A well-calibrated classifier should assign mostly `none` / "
        "`other` to TP-side detections - the Soviet 1980s topographic "
        "vocabulary has no \"burial mound\" category, so a real mound "
        "centred under the crop has nothing in the closed list to map "
        "onto. A TP bucket dominated by a vocabulary category (e.g. "
        "`contour-ring` > 10 %) would indicate the classifier is "
        "hallucinating Soviet-vocabulary categories onto correct "
        "detections, which would change how the FP-side categories are "
        "interpreted."
    )
    lines.append("")
    none_tp = tp_counts.get("none", 0)
    other_tp = tp_counts.get("other", 0)
    none_other_share = (
        100.0 * (none_tp + other_tp) / n_tp if n_tp else 0.0
    )
    lines.append(
        f"- TP-side n: {n_tp}"
    )
    lines.append(
        f"- `none` + `other` share on TP-side: "
        f"{none_other_share:.1f} % "
        f"({none_tp} + {other_tp} / {n_tp})"
    )
    # Vocabulary-category leakage check: any category > 10 % of TP?
    leak_categories: list[str] = []
    for cat in categories:
        if cat in {"none", "other"}:
            continue
        if n_tp == 0:
            break
        share = 100.0 * tp_counts.get(cat, 0) / n_tp
        if share > 10.0:
            leak_categories.append(f"{cat} ({share:.1f} %)")
    if leak_categories:
        lines.append(
            "- WARNING: vocabulary-category leakage on TP-side > 10 %: "
            f"{'; '.join(leak_categories)}. The FP-side categorical "
            "interpretation should be tempered accordingly (plan "
            "section 13.7)."
        )
    else:
        lines.append(
            "- No vocabulary category exceeds 10 % share on the TP-side; "
            "the classifier appears well-calibrated against the closed "
            "list (plan section 13.7 is satisfied)."
        )
    lines.append("")

    # Distractor-pull (number + benchmark) summary.
    lines.append("## Distractor-pull share (number + benchmark)")
    lines.append("")
    lines.append(
        "Shawn's 55-map hypothesis predicted high `number + benchmark` "
        "share (Soviet 1980s spot-elevation labels and survey markers); "
        "the 55-map result was instead `contour-ring`-dominant (Obs 302). "
        "On the GS side, Shawn's intuition was that water-features and "
        "spot-heights (= `number` in this vocabulary) would dominate. "
        "The table below tests both arms by threshold."
    )
    lines.append("")
    lines.append(
        "| Bucket | number + benchmark | share | water-feature | share | n |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|")
    rows = [(f"TP (<={primary_threshold_m} m)", tp_counts)]
    for thr in thresholds_m:
        rows.append((f"FP (>{thr} m)", fp_counts_by_threshold[thr]))
    for label, counts in rows:
        n = sum(counts.values())
        nb = counts.get("number", 0) + counts.get("benchmark", 0)
        wf = counts.get("water-feature", 0)
        denom = n if n else 1
        lines.append(
            f"| {label} | {nb} | {100 * nb / denom:.1f} % | "
            f"{wf} | {100 * wf / denom:.1f} % | {n} |"
        )
    lines.append("")

    # Cross-corpus comparison.
    lines.append("## Cross-corpus comparison vs 55-map text-track aggregate")
    lines.append("")
    lines.append(
        f"Headline cross-corpus contrast: GS FP at the primary "
        f"threshold (> {primary_threshold_m} m, n={n_fp_primary}) "
        "versus the 55-map text-track aggregate (sum of T0.3, T0.7, "
        "text-MIN runs from "
        "`results/55maps-fp-classification/category_distribution.json`)."
    )
    lines.append("")
    if fifty_five_text_aggregate is not None:
        lines.append(
            "| Category | GS FP (>{primary} m) | GS share | "
            "55-map text-track | 55-map share |".format(
                primary=primary_threshold_m,
            )
        )
        lines.append("|---|---:|---:|---:|---:|")
        n_gs = n_fp_primary if n_fp_primary else 1
        n_55 = (
            sum(fifty_five_text_aggregate.values())
            if fifty_five_text_aggregate else 1
        )
        for cat in categories:
            gs_n = fp_primary.get(cat, 0)
            tt_n = fifty_five_text_aggregate.get(cat, 0)
            lines.append(
                f"| {cat} | {gs_n} | {100 * gs_n / n_gs:.1f} % | "
                f"{tt_n} | {100 * tt_n / n_55:.1f} % |"
            )
        lines.append(
            f"| **N** | **{n_fp_primary}** | | "
            f"**{sum(fifty_five_text_aggregate.values())}** | |"
        )
        lines.append("")
    else:
        lines.append(
            "55-map comparator file unavailable - cross-corpus row table "
            "skipped."
        )
        lines.append("")

    lines.append(
        "### Chi-square test - GS FP at primary threshold vs 55-map "
        "text-track"
    )
    lines.append("")
    lines.extend(_format_chi2_block(cross_corpus_chi2, "gs", "fifty_five"))

    # Per-threshold chi-square summary so the deepest filter (>125 m,
    # the apples-to-apples comparator alongside the 50 m primary) is
    # visible at a glance.
    lines.append("### Cross-corpus chi-square at every sweep threshold")
    lines.append("")
    lines.append(
        "Re-running the same chi-square contingency at each threshold "
        "in the sensitivity sweep. The >125 m row is the strictest "
        "FP filter (no detection within 125 m of any curator GT mound) "
        "and serves as the apples-to-apples comparator alongside the "
        "50 m primary."
    )
    lines.append("")
    lines.append(
        "| Threshold (m) | n_gs | chi2 | dof | asymp p | "
        "Monte Carlo p | low_exp_frac |"
    )
    lines.append("|---:|---:|---:|---:|---:|---:|---:|")
    for thr in thresholds_m:
        block = cross_corpus_chi2_by_threshold[thr]
        if block.get("insufficient_data"):
            lines.append(
                f"| {thr} | n/a | n/a | n/a | n/a | n/a | n/a |"
            )
            continue
        n_gs_thr = block.get("n_gs", 0)
        chi2_v = block.get("chi2", float("nan"))
        dof_v = block.get("dof", 0)
        asymp_p = block.get("p_value", float("nan"))
        mc_p = block.get("monte_carlo_p_value")
        mc_str = f"{mc_p:.4g}" if mc_p is not None else "n/a"
        low_exp_v = block.get("low_expected_count_fraction", 0.0)
        lines.append(
            f"| {thr} | {n_gs_thr} | {chi2_v:.3f} | {dof_v} | "
            f"{asymp_p:.4g} | {mc_str} | {low_exp_v:.2f} |"
        )
    lines.append("")

    # Verdict.
    lines.append("## Verdict on Shawn's GS-side hypothesis")
    lines.append("")
    p_value = cross_corpus_chi2.get("p_value")
    mc_p = cross_corpus_chi2.get("monte_carlo_p_value")
    chosen_p = mc_p if mc_p is not None else p_value
    p_label = (
        "Monte Carlo" if mc_p is not None else "asymptotic"
    )
    if n_fp_primary == 0:
        lines.append(
            "**INSUFFICIENT DATA** - the FP-side bucket at the primary "
            "threshold is empty; no headline can be drawn."
        )
        lines.append("")
    else:
        # Compute headline shares for the verdict text.
        wf_share = (
            100.0 * fp_primary.get("water-feature", 0) / n_fp_primary
        )
        nb_share = (
            100.0 * (fp_primary.get("number", 0)
                     + fp_primary.get("benchmark", 0)) / n_fp_primary
        )
        # Identify the dominant FP-side category.
        sorted_cats = sorted(
            ((cat, fp_primary.get(cat, 0)) for cat in categories),
            key=lambda kv: kv[1], reverse=True,
        )
        dominant_cat, dominant_n = sorted_cats[0]
        dominant_share = (
            100.0 * dominant_n / n_fp_primary if n_fp_primary else 0.0
        )
        lines.append(
            f"- Dominant GS FP-side category at >{primary_threshold_m} m: "
            f"`{dominant_cat}` "
            f"({dominant_n} / {n_fp_primary} = {dominant_share:.1f} %)"
        )
        lines.append(
            f"- water-feature share on GS FP-side at "
            f">{primary_threshold_m} m: {wf_share:.1f} %"
        )
        lines.append(
            f"- number + benchmark (spot-height proxy) share on GS "
            f"FP-side at >{primary_threshold_m} m: {nb_share:.1f} %"
        )
        if chosen_p is not None:
            lines.append(
                f"- Cross-corpus chi-square ({p_label}) p-value: "
                f"{chosen_p:.4g}"
            )
        lines.append("")
        # Compose a narrative verdict.
        if chosen_p is not None and chosen_p < 0.05:
            lines.append(
                "The GS FP-side distribution differs significantly from "
                "the 55-map text-track aggregate at the primary threshold. "
                "Inspect the per-category Pearson residuals above to see "
                "which categories drive the divergence."
            )
        elif chosen_p is not None:
            lines.append(
                "The GS FP-side distribution is not statistically "
                "distinguishable from the 55-map text-track aggregate at "
                "the primary threshold (p >= 0.05). Caveat: with n="
                f"{n_fp_primary} on the GS side, statistical power is "
                "limited; absence of a significant difference does not "
                "demonstrate equivalence."
            )
        lines.append("")

    # Threshold-sensitivity flag.
    lines.append("## Threshold sensitivity")
    lines.append("")
    # Compare dominant share across thresholds.
    dominant_by_threshold: dict[int, tuple[str, float]] = {}
    for thr in thresholds_m:
        col = fp_counts_by_threshold[thr]
        n = sum(col.values())
        if n == 0:
            dominant_by_threshold[thr] = ("(none)", 0.0)
            continue
        sorted_cats = sorted(
            ((cat, col.get(cat, 0)) for cat in categories),
            key=lambda kv: kv[1], reverse=True,
        )
        dom_cat, dom_n = sorted_cats[0]
        dominant_by_threshold[thr] = (dom_cat, 100.0 * dom_n / n)
    lines.append(
        "| Threshold (m) | n_fp | dominant category | dominant share |"
    )
    lines.append("|---:|---:|---|---:|")
    for thr in thresholds_m:
        n_fp = sum(fp_counts_by_threshold[thr].values())
        dom_cat, dom_share = dominant_by_threshold[thr]
        lines.append(
            f"| {thr} | {n_fp} | `{dom_cat}` | {dom_share:.1f} % |"
        )
    lines.append("")
    # Fragility flag (plan §13.2).
    shares_only = [v[1] for v in dominant_by_threshold.values()]
    if shares_only and (max(shares_only) - min(shares_only) > 15.0):
        lines.append(
            "**Threshold-fragile**: the dominant category's share spans "
            f"more than 15 percentage points "
            f"({min(shares_only):.1f} - {max(shares_only):.1f} %) across "
            "the sweep. The paper Discussion should cite the primary "
            "threshold alongside a sensitivity-range footnote (plan "
            "section 13.2)."
        )
    else:
        lines.append(
            "Dominant-category share is threshold-stable across the "
            "sweep (range < 15 percentage points)."
        )
    lines.append("")

    # Caveats.
    lines.append("## Caveats and methodological notes")
    lines.append("")
    lines.append(
        "- **Single-pass classification, no consensus.** Each detection "
        "is classified once at temperature 0.0, thinking_level=minimal. "
        "Gemini 3 Flash class assignment may be noisy in ambiguous "
        "centres. The confidence-weighted distribution in "
        "`category_distribution.json` provides a sensitivity check; "
        "results should be read as a coarse first-pass profile, not a "
        "precise per-class accounting."
    )
    lines.append(
        "- **Different mechanisms, comparable rigour.** The 55-map FP set "
        "comes from human reviewers overriding noisy student-GT geometric "
        "labels at the per-detection step. The GS FP set comes from "
        "geometric filtering against a triple-checked sub-metre curator "
        "GT, with the human work done upstream during GT centring. Both "
        "sides defensibly produce a curator-grade FP set; framing the GS "
        "filter as a \"shortcut\" or \"proxy\" misreads the upstream "
        "investment in GT precision (plan section 2)."
    )
    lines.append(
        "- **Number = spot-height confound.** Soviet 1:50,000 maps "
        "render spot-heights as numeric elevation labels - the same "
        "`number` category that captures the distractor-pull arm of "
        "Shawn's 55-map hypothesis. Cross-corpus, identical `number` "
        "share on GS vs 55-map text-track does not by itself "
        "discriminate label distractor-pull from spot-height ambiguity; "
        "rationale-string review is required for that disambiguation."
    )
    lines.append(
        "- **Crop-centre ambiguity.** Some detections sit in dense map "
        "regions where multiple categories are plausible near the 150 m "
        "crop centre. The model is asked to pick the strongest "
        "burial-mound-confusable feature; the resulting category may "
        "differ from a strict \"closest-to-centre\" reading."
    )
    lines.append(
        "- **Per-map analysis is not powered.** The Lesovo sheet "
        "(K-35-078-1) carries only ~11 detections in the verified-v1 "
        "set, leaving < 2 FPs at any threshold. Per-corpus reporting is "
        "the only meaningful unit; per-map breakdowns are not reported "
        "(plan section 6.4)."
    )
    lines.append(
        "- **Small N on GS FP-side.** At the primary threshold the "
        f"GS FP bucket has n={n_fp_primary}. Chi-square expected counts "
        "fall below 5 in some cells; the report uses a Monte Carlo "
        "p-value as a robustness check when this happens (plan section "
        "13.3). Per-category Pearson residuals should be interpreted "
        "with the small-N caveat in mind."
    )
    lines.append("")

    # Findable later.
    lines.append("## Findable later")
    lines.append("")
    lines.append(
        "Search terms: GS FP-class classification, Obs 302 follow-up, "
        "cross-corpus comparator, distance-from-curator-GT primary 50 m, "
        "sensitivity sweep 25 50 75 100 125 m, Soviet 1980s topographic "
        "categories closed list, Gemini 3 Flash 150 m crop "
        "classification, TP-side reliability check, water-feature "
        "spot-height GS failure mode, sub-metre curator GT precision."
    )

    # Single trailing newline at EOF (markdownlint MD012 / MD047).
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# =========================================================================
# Driver
# =========================================================================


def _parse_thresholds(raw: str) -> list[int]:
    """Parse a comma-separated list of integer thresholds from CLI."""
    thresholds: list[int] = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            thresholds.append(int(token))
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"invalid threshold value '{token}': {exc}"
            ) from exc
    if not thresholds:
        raise argparse.ArgumentTypeError("--thresholds list is empty")
    return sorted(set(thresholds))


def run(
    output_dir: Path,
    workers: int,
    flex: bool,
    thresholds_m: list[int],
    primary_threshold_m: int,
    limit: int | None = None,
    dry_run: bool = False,
) -> int:
    """Top-level driver: load detections, classify, aggregate, write outputs.

    Args:
        output_dir: Root directory for all output artefacts.
        workers: ThreadPoolExecutor concurrency.
        flex: Use flex service tier (50 % discount).
        thresholds_m: Distance thresholds (m) for the post-classification
            sensitivity sweep.
        primary_threshold_m: Primary threshold (m) - the headline FP
            partition; must appear in ``thresholds_m``.
        limit: Optional cap on the number of detections processed
            (smoke test).
        dry_run: Skip the API loop and write aggregation outputs only -
            used for pipeline plumbing tests with a stub results list.
            (Currently always False from CLI; kept as a hook.)

    Returns:
        Exit code: 0 success, 2 hard-cap exceeded, 3 input missing.
    """
    setup_logging()
    if primary_threshold_m not in thresholds_m:
        raise ValueError(
            f"primary_threshold_m ({primary_threshold_m}) must be in "
            f"thresholds_m ({thresholds_m})"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    # 1. Load detections + curator GT distance.
    logger.info(
        "Loading detections from %s and reference from %s",
        DETECTIONS_PATH, REFERENCE_PATH,
    )
    try:
        records = load_gs_detections()
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s", exc)
        return 3
    if limit:
        logger.info("Smoke test: limiting to first %d records", limit)
        records = records[:limit]
    n_records = len(records)
    logger.info("Total detections to classify: %d", n_records)

    # Pre-classification distance histogram (the pre-launch validation
    # output, surfaced in the run log so anomalies appear before any API
    # calls happen). Plan section 10.1.
    for thr in thresholds_m:
        tp_n = sum(1 for r in records if r.dist_m <= thr)
        fp_n = n_records - tp_n
        logger.info(
            "  threshold=%3d m: TP-side=%3d  FP-side=%3d", thr, tp_n, fp_n,
        )

    if dry_run:
        logger.info("Dry-run mode: skipping API loop.")
        return 0

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
                    "Model '%s' not available; using '%s'",
                    model_cfg, preview,
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
        "Model: %s | flex tier: %s | workers: %d",
        model_cfg, flex, workers,
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
                render_and_classify, rec, client, model_cfg, gen_config,
            ): rec
            for rec in records
        }
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            results.append(res)
            completed += 1
            cumulative_in_tok += res.input_tokens
            cumulative_out_tok += res.output_tokens
            if not res.success:
                failed += 1
            if completed % 50 == 0 or completed == n_records:
                elapsed = time.time() - t_start
                rate = completed / elapsed if elapsed > 0 else 0
                cost_so_far = compute_cost(
                    cumulative_in_tok, cumulative_out_tok, flex=flex,
                )
                logger.info(
                    "Progress %d/%d (%.1f calls/s) | failed %d | "
                    "tokens in/out %d/%d | est cost $%.4f",
                    completed, n_records, rate, failed,
                    cumulative_in_tok, cumulative_out_tok, cost_so_far,
                )
                # Hard-cap guard.
                if cost_so_far > COST_HARD_CAP_USD:
                    logger.error(
                        "Hard-cap exceeded ($%.4f > $%.2f) — halting.",
                        cost_so_far, COST_HARD_CAP_USD,
                    )
                    for f in futures:
                        f.cancel()
                    halted_at_cap = True
                    break

    wall_clock = time.time() - t_start
    n_classified = sum(1 for r in results if r.success)

    # 4. Aggregate: TP-side at primary, FP-side per threshold.
    tp_records, _ = bucket_records(records, primary_threshold_m)
    tp_counts = counts_for_records(results, tp_records, CATEGORIES)
    tp_weighted = confidence_weighted_for_records(
        results, tp_records, CATEGORIES,
    )
    fp_counts_by_threshold: dict[int, dict[str, int]] = {}
    for thr in thresholds_m:
        _, fp_records = bucket_records(records, thr)
        fp_counts_by_threshold[thr] = counts_for_records(
            results, fp_records, CATEGORIES,
        )

    # 5. Cross-corpus chi-square (GS FP vs 55-map text-track) at the
    # primary threshold + at every other threshold in the sweep so the
    # report can show how the cross-corpus comparison shifts as the
    # FP-filter tightens (the >125 m stratum is the deepest filter — no
    # detection with any plausible reference within 125 m contaminates
    # the FP bucket — and is reported as the apples-to-apples
    # comparator alongside the 50 m primary).
    fifty_five_text_aggregate = load_55map_text_track_aggregate()
    cross_corpus_chi2_by_threshold: dict[int, dict[str, Any]] = {}
    for thr in thresholds_m:
        if fifty_five_text_aggregate is None:
            cross_corpus_chi2_by_threshold[thr] = {
                "insufficient_data": True,
                "reason": "55-map comparator unavailable",
            }
        else:
            cross_corpus_chi2_by_threshold[thr] = chi_square_two_distributions(
                fp_counts_by_threshold[thr],
                fifty_five_text_aggregate,
                CATEGORIES,
                label_a="gs",
                label_b="fifty_five",
            )
    cross_corpus_chi2 = cross_corpus_chi2_by_threshold[primary_threshold_m]

    # 6. Write outputs.
    write_classifications_json(
        results, records, primary_threshold_m,
        output_dir / "fp_classifications.json",
    )
    write_distribution_json(
        tp_counts=tp_counts,
        tp_weighted=tp_weighted,
        fp_counts_by_threshold=fp_counts_by_threshold,
        cross_corpus_chi2=cross_corpus_chi2,
        cross_corpus_chi2_by_threshold=cross_corpus_chi2_by_threshold,
        fifty_five_text_aggregate=fifty_five_text_aggregate,
        categories=CATEGORIES,
        n_total=n_classified,
        primary_threshold_m=primary_threshold_m,
        thresholds_m=thresholds_m,
        path=output_dir / "category_distribution.json",
    )
    write_distribution_figure(
        tp_counts=tp_counts,
        fp_counts_by_threshold=fp_counts_by_threshold,
        categories=CATEGORIES,
        thresholds_m=thresholds_m,
        path=figures_dir / "category_distribution.png",
    )
    write_cross_corpus_figure(
        gs_fp_primary_counts=fp_counts_by_threshold[primary_threshold_m],
        fifty_five_text_aggregate=fifty_five_text_aggregate,
        categories=CATEGORIES,
        primary_threshold_m=primary_threshold_m,
        path=figures_dir / "cross_corpus_comparison.png",
    )
    cost_total = compute_cost(
        cumulative_in_tok, cumulative_out_tok, flex=flex,
    )
    write_cost_summary(
        n_calls=len(results),
        input_tokens=cumulative_in_tok,
        output_tokens=cumulative_out_tok,
        flex=flex,
        wall_clock_seconds=wall_clock,
        path=output_dir / "cost_summary.json",
    )
    write_report_md(
        tp_counts=tp_counts,
        tp_weighted=tp_weighted,
        fp_counts_by_threshold=fp_counts_by_threshold,
        cross_corpus_chi2=cross_corpus_chi2,
        cross_corpus_chi2_by_threshold=cross_corpus_chi2_by_threshold,
        fifty_five_text_aggregate=fifty_five_text_aggregate,
        categories=CATEGORIES,
        n_total=n_classified,
        n_failed=failed,
        n_records_total=n_records,
        cost_total=cost_total,
        wall_clock_seconds=wall_clock,
        primary_threshold_m=primary_threshold_m,
        thresholds_m=thresholds_m,
        path=output_dir / "report.md",
    )

    logger.info(
        "Done. Classified %d / %d (failed %d). Wall %0.1fs. Cost ~$%.4f. "
        "Outputs in %s",
        n_classified, n_records, failed, wall_clock, cost_total, output_dir,
    )
    return 2 if halted_at_cap else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output-dir", type=Path,
        default=REPO_ROOT / "results/gs-fp-classification",
        help="Output directory for results (default: %(default)s)",
    )
    p.add_argument(
        "--workers", type=int, default=4,
        help="Parallel workers for the API loop (default: 4)",
    )
    p.add_argument(
        "--thresholds", type=_parse_thresholds,
        default=list(DEFAULT_THRESHOLDS_M),
        help=(
            "Comma-separated FP-filter thresholds in metres "
            "(default: 25,50,75,100,125)"
        ),
    )
    p.add_argument(
        "--primary-threshold", type=int,
        default=PRIMARY_THRESHOLD_M,
        help=(
            "Primary threshold (m) - must be present in --thresholds "
            "(default: 50)"
        ),
    )
    p.add_argument(
        "--no-flex", action="store_true",
        help="Disable flex tier (uses standard pricing; default off).",
    )
    p.add_argument(
        "--limit", type=int, default=None,
        help="Smoke test: cap N detections (default: no cap).",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help=(
            "Skip the API loop entirely; load detections + log distance "
            "histogram only. Used for pre-launch sanity checks."
        ),
    )
    args = p.parse_args()
    return run(
        output_dir=args.output_dir,
        workers=args.workers,
        flex=not args.no_flex,
        thresholds_m=args.thresholds,
        primary_threshold_m=args.primary_threshold,
        limit=args.limit,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
