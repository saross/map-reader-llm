#!/usr/bin/env python3
"""Streamlit app for precise centre-marking of the 773 promoted phantoms.

Ruling 21 makes a fixed ground-truth reference the gate for every
reference-tainted re-analysis, and ruling 20(d) makes this app step 1 of
that sequence. Five queued analyses wait on its output — see
``reports/verification/reference-standardisation-queue.md``.

**Scope**: ruling 21c set this at the 773 promoted phantoms only. The PI
widened it on 2026-08-05 to sweep up every possible conflation in the same
pass, at a **50 m** cut. The queue is built by
``scripts/build_marking_queue.py`` and comes to **1,006 items** — the 773
phantoms, plus 133 corrected-student points that either conflate with a
phantom, sit close to another student point, or are one of the 26 merged
centroids and 2 curator additions that distinguish layer 2 from layer 1,
plus a random 100-point sample for the placement-jitter estimate.

The remaining ~4,600 student mounds are still *not* re-marked: the proximity
audit found layer 2 essentially clean at this range, so there is nothing
there to adjudicate. The resulting reference is mixed-provenance by design
and is explicitly NOT a gold standard.

For each phantom the app shows a georeferenced window of the source
topographic sheet centred on the recorded position, overlays any nearby
student ground-truth points, and asks the reviewer to click the mound's
true centre. Three things resolve at once (ruling 20d step 2):

1. **Obs 371** — match distances were recorded as 25 m rings anchored at
   50 m rather than measured from marked centres, so sub-50 m Track-2
   figures penalise correct detections of student-missed mounds.
2. **The conflations** — any two mounds within 50 m, whether phantom to
   student, phantom to phantom, or student to student. They cannot be
   settled from coordinates; they have to be seen. The ``c`` verdict
   ("same mound as a neighbouring point") is what settles them. Four
   phantom-student pairs sit *inside* the 5 m de-duplication tolerance
   (0.98 m at the tightest) and are near-certain double-counts.
3. **The merge sites** — the 26 positions where two student points were
   replaced by a merged centroid. The app overlays the two superseded
   layer-1 positions so the merge can be checked, not just inherited.
4. **Row sorting** — handled downstream, not here.

Why this does not simply reuse ``review_candidates.render_candidate_context_crop``:
that renderer returns an image and nothing else, and it centres the crop
on the raster pixel *containing* the recorded point. At these sheets'
5.012 m/px resolution the pixel centre sits up to a half-diagonal
(3.54 m) from the recorded position. That is invisible when judging 50 m
tolerance rings, but it is a systematic error of the same order as the
7.3-15 m borderlines this review exists to adjudicate. This module
therefore carries a :class:`CropGeometry` alongside every crop and
converts clicks through the raster's own affine transform, so a marked
position is exact regardless of how the window was framed.

Usage — normally just::

    scripts/launch_point_marking.sh

which rebuilds the queue and supplies every path. The underlying call is
``streamlit run scripts/mark_mound_centres.py --`` with ``--queue-csv``,
``--phantom-csv``, ``--superseded-csv``, ``--rasters-dir``,
``--student-gt`` and ``--output``; see :func:`parse_args`.

Keys: ``d`` distinct · ``c`` same as a neighbour · ``u`` uncertain ·
``s`` skip · ``n``/``b`` navigate. ``d`` and ``c`` require a click first;
pressing them early is refused with an on-screen explanation rather than
silently ignored. (The buttons are deliberately never *disabled*: a
disabled button swallows the dispatched keyboard click, so the shortcut
would appear to do nothing at all.)

Output is written to a **new** file; no source layer is ever mutated in
place. The file is rewritten atomically after every mark, so an
interrupted session resumes exactly where it stopped.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import streamlit as st
from affine import Affine
from PIL import Image, ImageDraw
from rasterio.windows import Window
from streamlit_image_coordinates import streamlit_image_coordinates

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from review_candidates import _best_raster_for_point  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# The projected CRS every input shares (verified: the 55 Russian1981
# sheets, canonical-review.csv's x/y, and the student GeoJSON are all
# EPSG:32635).
_TARGET_CRS = "EPSG:32635"

# Window width in metres. 200 m gives roughly 40 native pixels across at
# 5.012 m/px — enough context to identify the mound symbol and see any
# neighbouring student point, without shrinking the target to a speck.
_DEFAULT_CONTEXT_M = 200.0

# On-screen size. Upscaling ~40 native px to 700 display px puts one
# native pixel at ~17 display px, so a click resolves to well under a
# metre of positional quantisation.
_DEFAULT_DISPLAY_PX = 700

# Reference rings, in metres from the recorded position. These are the
# distances that matter for the conflation judgement: 5 m is the
# de-duplication tolerance already applied, 15 m the "genuinely distinct
# mounds" floor. A point between them is a borderline case.
_DEDUP_TOLERANCE_M = 5.0
_DISTINCT_FLOOR_M = 15.0
# How far out a neighbour is FLAGGED for a conflation judgement. This is
# deliberately wider than the queue's own cut
# (build_marking_queue._DEFAULT_THRESHOLD_M, 75 m) because the two radii
# answer different questions and cost differently.
#
# The queue cut decides which STUDENT points get their own review item --
# expensive, since each is a separate decision. The flag radius decides
# which neighbours get explained on screen -- free, since they are drawn
# anyway.
#
# 110 m is set by the number-attractor effect (PI, 2026-08-05): a label or
# numeral near a mound can pull a detection well off the mound it belongs
# to, so a phantom and the student point for the SAME mound can sit 100 m
# apart (candidate 33: 102.9 m). Those need judging, but the student point
# itself is correctly placed and needs no re-marking -- only the displaced
# phantom does, via "c". Flagging to 110 m covers 399 of 773 phantoms;
# queueing to 110 m would have added ~470 items to re-mark points that are
# already right.
_FLAG_RADIUS_M = 110.0
# The queue's own cut, mirrored here only so the wording can distinguish
# "queued as its own item" from "flagged for your judgement".
_CONFLATION_CUT_M = 75.0
_CONTEXT_RINGS_M = (_DEDUP_TOLERANCE_M, _DISTINCT_FLOOR_M,
                    _CONFLATION_CUT_M, _FLAG_RADIUS_M)

# Radius within which student ground-truth points are drawn. Slightly
# larger than the window half-width so a point just off-screen still
# registers in the "nearest student point" readout.
_STUDENT_SEARCH_M = 250.0

# Radius of the alignment circle drawn at the marked point, in ground
# metres. Sized to the inner edge of a mound symbol's ring so the reviewer
# aligns a shape against a shape rather than judging a centre by eye on a
# blurred, distorted blob. ~8 native px at ~5 m/px is a ~40 m diameter, so
# 20 m radius is the starting estimate; it is adjustable because symbol
# size varies and the right value wants trial and error.
_DEFAULT_ALIGN_RADIUS_M = 20.0

# Keyboard nudge for the marked point. Clicking to within a pixel of a
# blurred symbol takes four or five attempts; nudging by a fixed step
# converges in a few keypresses and needs no aiming at all, which is the
# useful half of the drag-the-map-under-a-fixed-crosshair pattern.
# Default 2.5 m is half a native pixel at ~5 m/px — one step below the
# imagery's own quantisation floor, so it cannot be the limiting factor.
_DEFAULT_NUDGE_M = 2.5
_NUDGE_KEYS = {
    "i": ("north", 0.0, 1.0),
    "k": ("south", 0.0, -1.0),
    "j": ("west", -1.0, 0.0),
    "l": ("east", 1.0, 0.0),
}

_MAGENTA = (255, 0, 255)
_CYAN = (0, 255, 255)
_YELLOW = (255, 255, 0)
_ORANGE = (255, 140, 0)
_RED = (255, 40, 40)

# Reviewer verdicts. Keys double as the keyboard shortcut; button labels
# are rendered "<key>: <label>" so review_candidates.py's key-binding JS
# (reused verbatim below) can find them.
_VERDICTS = {
    "d": ("distinct", "Distinct mound"),
    "c": ("same_as_neighbour", "Same as a neighbour"),
    "x": ("not_a_mound", "Not a mound (FP)"),
    "u": ("uncertain", "Uncertain"),
    "s": ("skipped", "Skip"),
}

# Verdicts that require a marked centre first. "not_a_mound" does not:
# there is nothing to mark, and forcing a click would either fabricate a
# position or push a definite judgement into "uncertain", making the
# false-positive count unrecoverable afterwards.
_VERDICTS_NEEDING_A_CLICK = {"distinct", "same_as_neighbour"}

_OUTPUT_COLUMNS = [
    "queue_index",
    "item_id",
    "item_type",
    "source_layer",
    "source_index",
    "candidate_id",
    "map_name",
    "buffer_metres",
    "x",
    "y",
    "x_marked",
    "y_marked",
    "displacement_m",
    "nearest_neighbour_m",
    "verdict",
    # Which neighbour the reviewer's click actually resolved to. With 116
    # phantoms carrying more than one neighbour inside the flag radius, a
    # bare "same_as_neighbour" does not say WHICH -- and inferring it
    # downstream would re-do, less well, a judgement already made here.
    "resolved_partner_layer",
    "resolved_partner_m",
    # The partner's own position. Layer and distance alone cannot identify
    # WHICH neighbour was claimed, so without these a point can be used as
    # the conflation partner of two different items with nothing to catch
    # it.
    "resolved_partner_x",
    "resolved_partner_y",
    "symbol_type_prior",
    "symbol_type",
    "symbol_type_changed",
    "uncertain",
    "skipped",
    "marked_by",
    "marked_at",
]

# Curator vocabulary for symbol type, matching review_candidates.py's
# _MOUND_TYPES plus the two non-mound outcomes. Offered on student items so
# the reviewer can confirm or correct what the student recorded — which
# makes student symbol-classification error measurable rather than assumed.
_SYMBOL_TYPES = [
    "burial_mound",
    "settlement_mound",
    "bench_mark_on_mound",
    "trig_point_on_mound",
    "not_a_mound",
    "unsure",
]

# Human-readable forms, so the reviewer reads "Benchmark on burial mound"
# rather than parsing a snake_case identifier at speed. The stored value is
# always the identifier; only the display changes.
_SYMBOL_LABELS = {
    "burial_mound": "Burial mound",
    "settlement_mound": "Settlement mound",
    "bench_mark_on_mound": "Benchmark on burial mound",
    "trig_point_on_mound": "Trig point on burial mound",
    "not_a_mound": "Not a mound",
    "unsure": "Unsure",
}

# Overlay layers drawn as context around the subject point. Each entry is
# (colour, radius_px, stroke_px); the subject itself is drawn separately as
# a cross so it is never confused with its neighbours.
# Display names for the layers. "Phantom" is SCORING jargon -- a detection
# with no student-GT match is scored a false positive, a "phantom" -- but
# the 773 in layer 4 are the ones the reviewer then CONFIRMED as real
# mounds the students missed. Calling them phantoms in the UI says the
# opposite of what they are. The register keys the layer
# "4_reviewer_promoted_extension", which is accurate.
#
# The internal value stays "promoted_phantom": it is half of every mark's
# item_id, so renaming it would strand every mark recorded so far. Display
# and identity are deliberately separated here.
_LAYER_DISPLAY = {
    "promoted_phantom": "promoted mound",
    "corrected_student": "student GT",
    "extra_point": "extra point",
}


def _layer_name(layer: str) -> str:
    """Human-readable name for a layer key."""
    return _LAYER_DISPLAY.get(layer, layer.replace("_", " "))


_CONTEXT_STYLES = {
    "student": (_CYAN, 7, 3),
    "phantom": (_ORANGE, 9, 3),
    "superseded": (_RED, 5, 2),
}


# ---------------------------------------------------------------------------
# Crop geometry — the exact pixel/world correspondence
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CropGeometry:
    """Exact mapping between display pixels and projected world metres.

    A crop is an integer-pixel window of a raster, upscaled to a square
    display image. Converting a click back to world coordinates needs
    three things: where the window starts in the raster's pixel grid,
    how many raster pixels one display pixel spans, and the raster's own
    affine transform.

    Fractional pixel coordinates here are **corner-referenced**, which is
    the convention of :class:`affine.Affine`: integer ``(col, row)`` lands
    on a pixel's top-left corner, and ``(col + 0.5, row + 0.5)`` is its
    centre. Mixing this up with rasterio's centre-referenced
    :meth:`rasterio.DatasetReader.xy` is a half-pixel — 2.5 m at these
    sheets — so the two frames are never mixed in this module.

    Attributes:
        transform_coeffs: The raster's affine transform as the 6-tuple
            ``(a, b, c, d, e, f)``. Stored as a plain tuple rather than
            an :class:`~affine.Affine` so the containing object survives
            Streamlit's pickle-based caching unchanged.
        col_origin: Window's left edge, in corner-referenced fractional
            columns of the source raster.
        row_origin: Window's top edge, in corner-referenced fractional
            rows.
        window_px: Window width and height in raster pixels (square).
        display_px: Rendered image width and height in display pixels
            (square).

    Example:
        >>> from affine import Affine
        >>> geom = CropGeometry(
        ...     transform_coeffs=tuple(Affine(5.0, 0, 300000, 0, -5.0, 4700000)),
        ...     col_origin=100, row_origin=200, window_px=40, display_px=400,
        ... )
        >>> geom.display_to_world(200, 200)  # centre of the image
        (300300.0, 4698900.0)
    """

    transform_coeffs: tuple[float, float, float, float, float, float]
    col_origin: int
    row_origin: int
    window_px: int
    display_px: int

    @property
    def transform(self) -> Affine:
        """Rebuild the affine transform from its stored coefficients."""
        return Affine(*self.transform_coeffs)

    @property
    def metres_per_display_px(self) -> float:
        """Ground distance spanned by one display pixel."""
        return abs(self.transform.a) * self.window_px / self.display_px

    def display_to_world(
        self, px: float, py: float,
    ) -> tuple[float, float]:
        """Convert a display-pixel position to projected world metres.

        Args:
            px: Horizontal display-pixel coordinate, 0 at the left edge.
            py: Vertical display-pixel coordinate, 0 at the top edge.

        Returns:
            The ``(x, y)`` world coordinate in the raster's CRS.
        """
        scale = self.window_px / self.display_px
        col_frac = self.col_origin + px * scale
        row_frac = self.row_origin + py * scale
        world_x, world_y = self.transform * (col_frac, row_frac)
        return float(world_x), float(world_y)

    def world_to_display(
        self, world_x: float, world_y: float,
    ) -> tuple[float, float]:
        """Convert projected world metres to a display-pixel position.

        The exact inverse of :meth:`display_to_world`; used to draw the
        recorded position, nearby student points and the reviewer's own
        mark onto the crop.

        Args:
            world_x: Easting in the raster's CRS.
            world_y: Northing in the raster's CRS.

        Returns:
            The ``(px, py)`` display-pixel position. May fall outside
            ``[0, display_px]`` for points beyond the window.
        """
        col_frac, row_frac = ~self.transform * (world_x, world_y)
        scale = self.display_px / self.window_px
        px = (col_frac - self.col_origin) * scale
        py = (row_frac - self.row_origin) * scale
        return float(px), float(py)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _placeholder(display_px: int, message: str) -> Image.Image:
    """Grey fallback image carrying an explanatory message."""
    img = Image.new("RGB", (display_px, display_px), (200, 200, 200))
    ImageDraw.Draw(img).text((10, 10), message, fill=(40, 40, 40))
    return img


@st.cache_data(show_spinner=False)
def render_base_crop(
    x: float,
    y: float,
    rasters_dir: str,
    context_m: float = _DEFAULT_CONTEXT_M,
    display_px: int = _DEFAULT_DISPLAY_PX,
    resampling: str = "lanczos",
) -> tuple[Image.Image, CropGeometry | None]:
    """Render the bare map window around ``(x, y)``, plus its geometry.

    Overlays are deliberately *not* drawn here: this function does the
    expensive raster read and is cached on its arguments, while the
    overlays change on every click and are composited separately by
    :func:`draw_overlays`. Pre-rendering the whole set up front (see
    ``--prerender``) is what keeps the review itself instant.

    The window is an integer-pixel box centred on the pixel containing
    ``(x, y)``, read with ``boundless=True`` so a phantom near a sheet
    edge still yields a correctly-sized image. The returned
    :class:`CropGeometry` describes exactly where that box sits, so the
    up-to-3.54 m framing offset never propagates into a marked position.

    Args:
        x: Easting of the recorded position, in the raster CRS.
        y: Northing of the recorded position, in the raster CRS.
        rasters_dir: Directory of georeferenced sheets to search.
        context_m: Window width in ground metres.
        display_px: Output image width and height in pixels.
        resampling: ``"lanczos"`` or ``"nearest"``; see
            :func:`parse_args`. Note that no filter adds information —
            the sheets are ~5 m/px, so a marked centre carries roughly
            half a pixel (±2.5 m) of irreducible quantisation.

    Returns:
        A ``(image, geometry)`` pair. ``geometry`` is ``None`` when no
        raster covers the point, in which case ``image`` is a grey
        placeholder and the candidate cannot be marked.
    """
    raster_path = _best_raster_for_point(Path(rasters_dir), x, y)
    if raster_path is None:
        return _placeholder(
            display_px, f"[no raster covers]\n{x:.1f}, {y:.1f}",
        ), None

    with rasterio.open(raster_path) as src:
        row_c, col_c = src.index(x, y)
        res_m_per_px = abs(src.transform.a)
        half_px = max(1, int(round(context_m / 2 / res_m_per_px)))
        window = Window(
            col_c - half_px, row_c - half_px, half_px * 2, half_px * 2,
        )
        arr = src.read(window=window, boundless=True, fill_value=0)
        transform_coeffs = tuple(src.transform)[:6]

    n_bands = arr.shape[0]
    if n_bands >= 3:
        img_data = arr[:3].transpose(1, 2, 0)
    elif n_bands in (1, 2):
        grey = arr[0]
        img_data = np.stack([grey, grey, grey], axis=-1)
    else:
        return _placeholder(display_px, "[unreadable raster bands]"), None

    # LANCZOS preserves the thin line-art of topographic symbols better
    # than bicubic at these upscaling factors (~17x). NEAREST is offered
    # because at 5 m/px the smooth version can imply a precision the
    # source does not have.
    filt = Image.LANCZOS if resampling == "lanczos" else Image.NEAREST
    img = (
        Image.fromarray(img_data.astype(np.uint8))
        .convert("RGB")
        .resize((display_px, display_px), filt)
    )
    geometry = CropGeometry(
        transform_coeffs=transform_coeffs,  # type: ignore[arg-type]
        col_origin=col_c - half_px,
        row_origin=row_c - half_px,
        window_px=half_px * 2,
        display_px=display_px,
    )
    return img, geometry


def _draw_scale_bar(
    draw: ImageDraw.ImageDraw, geom: CropGeometry, length_m: float = 50.0,
) -> None:
    """Draw a labelled scale bar in the lower-left of the crop."""
    bar_px = length_m / geom.metres_per_display_px
    x0 = 16
    y0 = geom.display_px - 24
    draw.rectangle(
        [(x0 - 6, y0 - 16), (x0 + bar_px + 6, y0 + 8)],
        fill=(0, 0, 0, 170),
    )
    draw.line([(x0, y0), (x0 + bar_px, y0)], fill=(255, 255, 255), width=3)
    for end_x in (x0, x0 + bar_px):
        draw.line(
            [(end_x, y0 - 5), (end_x, y0 + 5)], fill=(255, 255, 255), width=3,
        )
    draw.text((x0, y0 - 14), f"{length_m:.0f} m", fill=(255, 255, 255))


def _draw_ring_label_text(
    draw: ImageDraw.ImageDraw, text: str, x: int, y: int,
    colour: tuple[int, int, int],
) -> None:
    """Draw a small boxed label beside a context marker."""
    pad = 3
    try:
        bbox = draw.textbbox((0, 0), text)
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except (AttributeError, TypeError):
        width, height = 6 * len(text), 11
    draw.rectangle(
        [(x - pad, y - height // 2 - pad),
         (x + width + pad, y + height // 2 + pad)],
        fill=(0, 0, 0, 200),
    )
    draw.text((x, y - height // 2), text, fill=(*colour, 255))


def draw_overlays(
    base: Image.Image,
    geom: CropGeometry,
    recorded: tuple[float, float],
    context: dict[str, list[tuple[float, float]]],
    marked: tuple[float, float] | None,
    rings_m: tuple[float, ...] = _CONTEXT_RINGS_M,
    numbering: dict[tuple[float, float], str] | None = None,
    align_radius_m: float = 0.0,
) -> Image.Image:
    """Composite the review overlays onto a base crop.

    Draws, in back-to-front order: reference rings around the recorded
    position, neighbouring points from each context layer, the recorded
    position itself (magenta cross), the reviewer's mark (yellow cross
    with a connecting line), and a scale bar.

    Colours are chosen for contrast against Soviet 1:50k topographic
    sheets, where magenta, cyan and orange are essentially absent from the
    map content.

    Args:
        base: The unannotated crop from :func:`render_base_crop`.
        geom: That crop's geometry, used for every world-to-pixel step.
        recorded: The ``(x, y)`` position of the item under review.
        context: Neighbouring positions by layer name — ``"student"``
            (cyan), ``"phantom"`` (orange) and ``"superseded"`` (red, the
            layer-1 points a merged centroid replaced). Unknown names are
            ignored rather than raising, so a caller can pass a layer the
            styles do not yet cover.
        marked: The reviewer's clicked ``(x, y)``, or ``None`` if unmarked.
        rings_m: Reference-ring radii in ground metres.
        align_radius_m: Radius in ground metres of an alignment circle
            drawn at the marked point. Zero disables it.
        numbering: Optional ``(x, y) -> label`` map, drawn beside the
            matching marker. Two neighbours of the same layer at similar
            distances are otherwise indistinguishable between the map and
            the partner dropdown, which is what this exists to fix.

    Returns:
        A new RGB image; ``base`` is not modified.
    """
    img = base.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    rec_px, rec_py = geom.world_to_display(*recorded)

    # Reference rings, outermost first so the tightest sits on top.
    for radius_m in sorted(rings_m, reverse=True):
        r_px = radius_m / geom.metres_per_display_px
        alpha = 110 if radius_m >= _DISTINCT_FLOOR_M else 200
        draw.ellipse(
            [(rec_px - r_px, rec_py - r_px), (rec_px + r_px, rec_py + r_px)],
            outline=(*_MAGENTA, alpha),
            width=1 if radius_m >= _DISTINCT_FLOOR_M else 2,
        )

    # Neighbouring points — the conflation judgement is exactly "is that
    # the same mound as this one?", so every candidate partner must be
    # visible and distinguishable by layer.
    for layer_name, points in context.items():
        style = _CONTEXT_STYLES.get(layer_name)
        if style is None:
            continue
        colour, radius, stroke = style
        for point_x, point_y in points:
            point_px, point_py = geom.world_to_display(point_x, point_y)
            draw.ellipse(
                [(point_px - radius, point_py - radius),
                 (point_px + radius, point_py + radius)],
                outline=(*colour, 255), width=stroke,
            )
            tag = (numbering or {}).get((point_x, point_y))
            if tag:
                _draw_ring_label_text(
                    draw, tag, int(point_px + radius + 9), int(point_py),
                    colour,
                )

    # Recorded position.
    half = 9
    draw.line(
        [(rec_px - half, rec_py), (rec_px + half, rec_py)],
        fill=(*_MAGENTA, 255), width=2,
    )
    draw.line(
        [(rec_px, rec_py - half), (rec_px, rec_py + half)],
        fill=(*_MAGENTA, 255), width=2,
    )

    # The reviewer's mark, joined to the recorded position so the
    # displacement is visible as well as numeric.
    if marked is not None:
        mpx, mpy = geom.world_to_display(*marked)
        # Alignment circle first, so the crosshair sits on top of it.
        if align_radius_m > 0:
            r_px = align_radius_m / geom.metres_per_display_px
            draw.ellipse(
                [(mpx - r_px, mpy - r_px), (mpx + r_px, mpy + r_px)],
                outline=(*_YELLOW, 220), width=2,
            )
        draw.line(
            [(rec_px, rec_py), (mpx, mpy)], fill=(*_YELLOW, 190), width=1,
        )
        half = 11
        draw.line(
            [(mpx - half, mpy), (mpx + half, mpy)],
            fill=(*_YELLOW, 255), width=3,
        )
        draw.line(
            [(mpx, mpy - half), (mpx, mpy + half)],
            fill=(*_YELLOW, 255), width=3,
        )

    _draw_scale_bar(draw, geom)
    return Image.alpha_composite(img, overlay).convert("RGB")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_queue(queue_csv: Path) -> pd.DataFrame:
    """Load the review queue built by ``build_marking_queue.py``.

    ``buffer_metres`` is cast to float explicitly. In the upstream
    ``canonical-review.csv`` that column is stored in **two string
    formats** — 410 rows carry ``'50'`` and 5 carry ``'50.0'``, and
    similarly at the other bands — so any consumer bucketing on the raw
    text reports 410 at R = 50 m instead of the true 415. The queue
    builder already normalises it; the cast here keeps the guarantee if
    a queue is ever produced by another route. Student rows carry no
    buffer, so the column is nullable.

    ``queue_index`` is the stable key. ``candidate_id`` is **not** unique
    across runs and must not be used as an identifier; it is carried
    through as metadata only, and is empty for student rows.

    Args:
        queue_csv: Path to ``marking-queue.csv``.

    Returns:
        The queue with ``buffer_metres`` coerced to float.

    Raises:
        ValueError: If a required column is missing.
    """
    df = pd.read_csv(queue_csv)
    required = {"queue_index", "item_type", "source_layer", "source_index",
                "x", "y"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"{queue_csv} is missing required column(s): "
            f"{', '.join(sorted(missing))}",
        )
    df = df.copy()
    if "buffer_metres" in df.columns:
        df["buffer_metres"] = pd.to_numeric(
            df["buffer_metres"], errors="coerce",
        )
    return df


@st.cache_data(show_spinner=False)
def load_superseded_points(superseded_csv: str) -> np.ndarray:
    """Load the layer-1 positions that merged centroids replaced.

    Overlaid in red at merge sites so the reviewer can check the merge
    rather than inherit it. Returns an empty array when the file is
    absent, since the overlay is context rather than a requirement.

    Args:
        superseded_csv: Path to the superseded-positions CSV.

    Returns:
        An ``(n, 2)`` array of projected coordinates.
    """
    path = Path(superseded_csv)
    if not path.exists():
        return np.zeros((0, 2))
    frame = pd.read_csv(path)
    return np.column_stack([
        frame["x"].to_numpy(dtype=float), frame["y"].to_numpy(dtype=float),
    ])


@st.cache_data(show_spinner=False)
def load_student_points(student_gt: str) -> np.ndarray:
    """Load student ground-truth positions as an ``(n, 2)`` array.

    Args:
        student_gt: Path to the reviewed student-mound GeoJSON.

    Returns:
        Projected ``(x, y)`` coordinates in :data:`_TARGET_CRS`.

    Raises:
        ValueError: If the layer has no CRS, since silently assuming one
            would put every overlay in the wrong place.
    """
    gdf = gpd.read_file(student_gt)
    if gdf.crs is None:
        raise ValueError(
            f"{student_gt} has no CRS; cannot align it with the rasters.",
        )
    if gdf.crs.to_string() != _TARGET_CRS:
        gdf = gdf.to_crs(_TARGET_CRS)
    centroids = gdf.geometry.centroid
    return np.column_stack([centroids.x.to_numpy(), centroids.y.to_numpy()])


@st.cache_data(show_spinner=False)
def load_phantom_points(phantom_csv: str) -> np.ndarray:
    """Load the promoted-phantom positions as an ``(n, 2)`` array.

    Overlaid in orange so a phantom-to-phantom pair is visible as such.
    The queue already contains every phantom as an item; this layer is
    what lets the reviewer see the *partner* while judging one of them.

    Args:
        phantom_csv: Path to ``canonical-review.csv``.

    Returns:
        Projected ``(x, y)`` coordinates.
    """
    frame = pd.read_csv(phantom_csv)
    return np.column_stack([
        frame["x"].to_numpy(dtype=float), frame["y"].to_numpy(dtype=float),
    ])


def _item_id(row: "pd.Series") -> str:
    """Stable identity for a queue item, independent of its position.

    Marks are keyed on this rather than ``queue_index`` so the queue can be
    re-sorted without stranding completed work. Derived from the source
    layer and index, which are recorded on every mark, so a marks file
    written before ``item_id`` existed still resolves.

    Args:
        row: A queue row or a previously saved mark.

    Returns:
        An identifier of the form ``"<source_layer>:<source_index>"``.
    """
    stored = row.get("item_id")
    if stored is not None and not pd.isna(stored) and str(stored).strip():
        return str(stored)
    return f"{row['source_layer']}:{int(row['source_index'])}"


def _text(value: object) -> str:
    """Coerce a possibly-missing CSV cell to a clean string.

    A blank cell round-trips through pandas as ``float('nan')``, which is
    **truthy** — so ``value or ""`` does not catch it and ``str(value)``
    yields the literal text "nan". That string then appears as a
    selectable symbol type in the UI. Guard with an explicit null check.

    Args:
        value: The raw cell value.

    Returns:
        The value as a string, or ``""`` if missing.
    """
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def _nearest_distance(
    points: list[tuple[float, float]], x: float, y: float,
) -> float | None:
    """Distance to the closest of ``points``, or ``None`` if empty."""
    if not points:
        return None
    return min(math.hypot(px - x, py - y) for px, py in points)


def nearby_student_points(
    points: np.ndarray, x: float, y: float,
    radius_m: float = _STUDENT_SEARCH_M,
) -> tuple[list[tuple[float, float]], float | None]:
    """Find student points near ``(x, y)`` and the distance to the closest.

    A brute-force scan is used deliberately: 4,746 points is a trivial
    vectorised distance computation (well under a millisecond), and it
    avoids a spatial-index dependency in a function that tests must be
    able to call directly.

    Args:
        points: ``(n, 2)`` array of student positions.
        x: Easting of the phantom.
        y: Northing of the phantom.
        radius_m: Search radius in ground metres.

    Returns:
        A ``(nearby, nearest_distance_m)`` pair. ``nearest_distance_m``
        is ``None`` when no student point falls within ``radius_m``.
    """
    if len(points) == 0:
        return [], None
    deltas = points - np.array([x, y])
    distances = np.hypot(deltas[:, 0], deltas[:, 1])
    within = distances <= radius_m
    if not within.any():
        return [], None
    nearby = [tuple(map(float, p)) for p in points[within]]
    return nearby, float(distances[within].min())


def load_existing_marks(output_csv: Path) -> dict[int, dict]:
    """Load previously saved marks so a session resumes where it stopped.

    Args:
        output_csv: Path to this app's own output file.

    Returns:
        Mapping of ``item_id`` to the saved record. Empty when the file
        does not yet exist. Keyed on identity rather than position so a
        re-sorted queue does not strand completed work.
    """
    if not output_csv.exists():
        return {}
    df = pd.read_csv(output_csv)
    if not {"source_layer", "source_index"} <= set(df.columns):
        return {}
    marks: dict[str, dict] = {}
    for record in df.to_dict("records"):
        marks[_item_id(pd.Series(record))] = record
    return marks


def save_marks(marks: dict[int, dict], output_csv: Path) -> None:
    """Write all marks to CSV via an atomic temp-then-rename.

    Called after every single mark, so an hour of clicking survives a
    crash or an accidental browser refresh. The atomic rename guards
    against a truncated file if the write is interrupted mid-flight.

    Args:
        marks: Mapping of ``item_id`` to record.
        output_csv: Destination path. Parent directories are created.
    """
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(marks.values(), key=lambda r: int(r["queue_index"]))
    frame = pd.DataFrame(rows, columns=_OUTPUT_COLUMNS)
    tmp = output_csv.with_suffix(output_csv.suffix + ".tmp")
    frame.to_csv(tmp, index=False)
    tmp.replace(output_csv)


def build_record(
    row: pd.Series,
    marked: tuple[float, float] | None,
    verdict: str,
    nearest_neighbour_m: float | None,
    marked_by: str,
    symbol_type: str = "",
    resolved_partner: tuple[str, float, float, float] | None = None,
) -> dict:
    """Assemble one output row.

    ``displacement_m`` — the headline diagnostic for Obs 371 — is derived
    here rather than downstream so the saved file is self-contained.

    Args:
        row: The item's row from :func:`load_queue`.
        marked: Clicked ``(x, y)``, or ``None`` for skipped/uncertain
            rows with no click.
        verdict: One of the values in :data:`_VERDICTS`.
        nearest_neighbour_m: Distance to the closest point in any other
            layer, if one falls within the search radius.
        marked_by: Reviewer name recorded in the output.
        resolved_partner: ``(layer, distance_m, x, y)`` of the chosen
            neighbour, or ``None``. The coordinates are what make a
            double-claim detectable afterwards.
        symbol_type: The reviewer's symbol-type call. Recorded alongside
            ``symbol_type_prior`` (what the student layer already held) and
            a derived ``symbol_type_changed`` flag, so student
            classification error is countable directly from this file.

    Returns:
        A dict keyed by :data:`_OUTPUT_COLUMNS`.
    """
    if marked is not None:
        displacement = math.hypot(
            marked[0] - float(row["x"]), marked[1] - float(row["y"]),
        )
    else:
        displacement = None
    buffer_value = row.get("buffer_metres")
    prior_symbol = _text(row.get("prior_symbol_type"))
    return {
        "queue_index": int(row["queue_index"]),
        "item_id": _item_id(row),
        "item_type": row["item_type"],
        "source_layer": row["source_layer"],
        "source_index": int(row["source_index"]),
        "candidate_id": row.get("candidate_id", ""),
        "map_name": row.get("map_name", ""),
        "buffer_metres": (
            None if buffer_value is None or pd.isna(buffer_value)
            else float(buffer_value)
        ),
        "x": float(row["x"]),
        "y": float(row["y"]),
        "x_marked": marked[0] if marked else None,
        "y_marked": marked[1] if marked else None,
        "displacement_m": displacement,
        "nearest_neighbour_m": nearest_neighbour_m,
        "verdict": verdict,
        "resolved_partner_layer": (
            resolved_partner[0] if resolved_partner else ""
        ),
        "resolved_partner_m": (
            resolved_partner[1] if resolved_partner else None
        ),
        "resolved_partner_x": (
            resolved_partner[2] if resolved_partner else None
        ),
        "resolved_partner_y": (
            resolved_partner[3] if resolved_partner else None
        ),
        "symbol_type_prior": prior_symbol,
        "symbol_type": symbol_type,
        # Only meaningful when the reviewer actually made a call and a
        # prior existed; otherwise False rather than a spurious "changed".
        "symbol_type_changed": bool(
            symbol_type and prior_symbol and symbol_type != prior_symbol,
        ),
        "uncertain": verdict == "uncertain",
        "skipped": verdict == "skipped",
        "marked_by": marked_by,
        "marked_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Keyboard shortcuts
# ---------------------------------------------------------------------------

# Binds a single keypress to any button whose label starts "<key>:".
# Lifted from scripts/review_candidates.py, which has been driven through
# several thousand review decisions with this handler; the only changes
# are the log prefix and the handler property name, so the two apps do
# not fight over the same document property when both are open.
_SHORTCUT_JS = """
<script>
(function() {
    // Binds a single keypress to any button whose label starts "<key>:".
    //
    // The hard part is not matching the key, it is RECEIVING it. Streamlit
    // renders custom components -- including the click-to-mark image -- in
    // their own iframes. Clicking the image moves keyboard focus into that
    // iframe, so a handler attached only to the main document never sees
    // the subsequent keypress. Since every item starts with a click on the
    // image, a main-document-only handler works exactly once: before the
    // first click, and never again.
    //
    // So: attach to every same-origin document we can reach (parent, top,
    // our own, and each sibling component iframe), and re-attach on an
    // interval because Streamlit destroys and recreates those iframes on
    // every rerun. Streamlit's iframe sandbox includes allow-same-origin,
    // which is what makes reaching into siblings possible at all.
    const LOG = function() {
        console.log.apply(console, ['[mark-centres]'].concat(
            Array.prototype.slice.call(arguments)
        ));
    };

    let mainDoc = document;
    try { if (window.parent) mainDoc = window.parent.document; } catch (e) {}

    const collectDocs = function() {
        const docs = [];
        const push = function(d) {
            if (d && docs.indexOf(d) === -1) docs.push(d);
        };
        try { push(window.parent.document); } catch (e) {}
        try { push(window.top.document); } catch (e) {}
        push(document);
        const roots = docs.slice();
        for (let i = 0; i < roots.length; i++) {
            let frames;
            try { frames = roots[i].querySelectorAll('iframe'); }
            catch (e) { continue; }
            for (let j = 0; j < frames.length; j++) {
                try { push(frames[j].contentDocument); } catch (e) {}
            }
        }
        return docs;
    };

    const simulateClick = function(btn, label) {
        if (!btn) return;
        if (btn.disabled) { LOG('button is disabled:', label); return; }
        // Deliberately NOT scrollIntoView: dispatching works on an
        // off-screen button, and scrolling made the page jump on every
        // nudge keypress.
        setTimeout(function() {
            const opts = {bubbles: true, cancelable: true, view: window};
            try {
                btn.dispatchEvent(new MouseEvent('mousedown', opts));
                btn.dispatchEvent(new MouseEvent('mouseup', opts));
                btn.dispatchEvent(new MouseEvent('click', opts));
                if (typeof btn.click === 'function') btn.click();
                LOG('clicked', label);
            } catch (err) {
                LOG('click failed', err);
            }
        }, 0);
    };

    const handler = function(e) {
        if (e.ctrlKey || e.altKey || e.metaKey) return;
        if (e.__markCentresSeen) return;
        e.__markCentresSeen = true;

        const target = e.target;
        if (target && (target.tagName === 'INPUT' ||
                       target.tagName === 'TEXTAREA' ||
                       target.isContentEditable)) return;
        const key = (e.key || '').toLowerCase();
        if (!key) return;

        // Buttons always live in the MAIN document, whichever frame the
        // keypress happened to arrive in.
        let buttons;
        try { buttons = mainDoc.querySelectorAll('button'); }
        catch (err) { LOG('cannot reach main document', err); return; }
        const matches = [];
        for (let i = 0; i < buttons.length; i++) {
            const text = (buttons[i].textContent || '').trim().toLowerCase();
            if (text.indexOf(key + ':') === 0) matches.push(buttons[i]);
        }
        if (matches.length === 0) return;
        const btn = matches[matches.length - 1];
        try {
            const focused = mainDoc.activeElement;
            if (focused && focused.blur) focused.blur();
        } catch (err) {}
        simulateClick(btn, (btn.textContent || '').trim());
        e.preventDefault();
        e.stopPropagation();
    };

    const attach = function() {
        const docs = collectDocs();
        let added = 0;
        for (let i = 0; i < docs.length; i++) {
            if (docs[i].__markCentresKeyHandler === handler) continue;
            if (docs[i].__markCentresKeyHandler) {
                try {
                    docs[i].removeEventListener(
                        'keydown', docs[i].__markCentresKeyHandler, true,
                    );
                } catch (err) {}
            }
            try {
                docs[i].addEventListener('keydown', handler, true);
                docs[i].__markCentresKeyHandler = handler;
                added += 1;
            } catch (err) {}
        }
        if (added) LOG('handler attached to', added, 'new document(s)');
    };

    attach();
    // Streamlit recreates component iframes on every rerun, so a one-off
    // attachment goes stale as soon as the reviewer marks anything.
    if (window.__markCentresTimer) clearInterval(window.__markCentresTimer);
    window.__markCentresTimer = setInterval(attach, 700);
})();
</script>
"""


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments passed after Streamlit's ``--``.

    Args:
        argv: Argument list; defaults to ``sys.argv[1:]``.

    Returns:
        The parsed namespace.
    """
    parser = argparse.ArgumentParser(
        description="Mark true centres for the 773 promoted phantoms.",
    )
    parser.add_argument(
        "--queue-csv", required=True, type=Path,
        help="marking-queue.csv from scripts/build_marking_queue.py.",
    )
    parser.add_argument(
        "--rasters-dir", required=True, type=Path,
        help="Directory of georeferenced sheets covering the 55-map corpus.",
    )
    parser.add_argument(
        "--student-gt", required=True, type=Path,
        help="Reviewed student-mound GeoJSON, overlaid for conflation calls.",
    )
    parser.add_argument(
        "--phantom-csv", required=True, type=Path,
        help="canonical-review.csv, overlaid so phantom pairs are visible.",
    )
    parser.add_argument(
        "--re-review-csv", type=Path, default=None,
        help=(
            "CSV from build_re_review_list.py naming marks that need a "
            "second look, with reasons. Enables the 'Re-review list' "
            "navigation mode."
        ),
    )
    parser.add_argument(
        "--superseded-csv", type=Path, default=None,
        help=(
            "Superseded layer-1 positions from build_marking_queue.py, "
            "overlaid in red at merge sites. Optional context."
        ),
    )
    parser.add_argument(
        "--output", required=True, type=Path,
        help="Destination CSV. Never the input; written atomically.",
    )
    parser.add_argument(
        "--marked-by", default="", help="Reviewer name recorded per row.",
    )
    parser.add_argument(
        "--context-m", type=float, default=_DEFAULT_CONTEXT_M,
        help=f"Window width in metres (default {_DEFAULT_CONTEXT_M:.0f}).",
    )
    parser.add_argument(
        "--display-px", type=int, default=_DEFAULT_DISPLAY_PX,
        help=f"Display size in pixels (default {_DEFAULT_DISPLAY_PX}).",
    )
    parser.add_argument(
        "--resampling", choices=("lanczos", "nearest"), default="lanczos",
        help=(
            "Upscaling filter. 'lanczos' (default) matches "
            "review_candidates.py and reads more naturally; 'nearest' shows "
            "true pixel edges, making the ~5 m native quantisation visible "
            "rather than smoothed away."
        ),
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="Mark mound centres", layout="wide")
    args = parse_args()

    for reserved in (args.queue_csv, args.phantom_csv, args.student_gt):
        if args.output.resolve() == reserved.resolve():
            st.error(
                f"--output must not be {reserved}: source layers are never "
                "mutated in place.",
            )
            return

    queue = load_queue(args.queue_csv)
    re_review = (
        pd.read_csv(args.re_review_csv)
        if args.re_review_csv and args.re_review_csv.exists()
        else pd.DataFrame(columns=["item_id", "reasons"])
    )
    re_review_reasons = dict(
        zip(re_review["item_id"], re_review["reasons"], strict=False),
    )
    students = load_student_points(str(args.student_gt))
    phantoms = load_phantom_points(str(args.phantom_csv))
    superseded = (
        load_superseded_points(str(args.superseded_csv))
        if args.superseded_csv else np.zeros((0, 2))
    )

    if "marks" not in st.session_state:
        st.session_state.marks = load_existing_marks(args.output)
    if "cursor" not in st.session_state:
        # Resume at the first unmarked row rather than at zero. Membership
        # is tested by identity, so a re-sorted queue resumes correctly.
        done = set(st.session_state.marks)
        remaining = [
            i for i in range(len(queue))
            if _item_id(queue.iloc[i]) not in done
        ]
        st.session_state.cursor = remaining[0] if remaining else 0
    if "pending" not in st.session_state:
        st.session_state.pending = {}

    marks: dict[str, dict] = st.session_state.marks
    cursor: int = st.session_state.cursor
    row = queue.iloc[cursor]
    n_total = len(queue)
    is_phantom = row["source_layer"] == "promoted_phantom"

    # --- sidebar: progress and navigation ------------------------------
    with st.sidebar:
        st.metric("Marked", f"{len(marks)} / {n_total}")
        st.progress(len(marks) / n_total if n_total else 0.0)
        st.caption(
            "Click the true centre, then press a verdict key.\n\n"
            "**d** distinct · **c** same as a neighbour · "
            "**u** uncertain · **s** skip\n\n"
            "**n** next · **b** back",
        )
        st.caption(
            "Overlays: :violet[magenta] this point · :blue[cyan] student GT "
            "· :orange[orange] promoted mounds (your bullseye confirmations) "
            "· :red[red] superseded (pre-merge) positions",
        )
        st.caption(f"Output: `{args.output}`")

        # Zoom has to be adjustable per item, not fixed at launch. The 26
        # merged pairs are separated by between 1.7 m and 49.2 m, so no
        # single window shows them all: at 200 m a 1.7 m separation is
        # about six display pixels.
        zoom_options = sorted({50.0, 100.0, 200.0, 400.0, args.context_m})
        context_m = st.select_slider(
            "Window width (m)", options=zoom_options,
            value=st.session_state.get("context_m", args.context_m),
            format_func=lambda v: f"{v:.0f} m",
        )
        st.session_state.context_m = context_m

        # Navigation scope. "Revisit earliest" exists because an
        # adjudication rule refined mid-pass has to be applied backwards to
        # the marks made before it, or the reference is internally
        # inconsistent -- and those marks are scattered through the queue,
        # not contiguous, so they cannot be reached by stepping.
        nav_mode = st.selectbox(
            "Navigate",
            ["Unmarked only", "All items", "Re-review list",
             "Revisit earliest marks"],
            index=0,
        )
        revisit_n = 0
        if nav_mode == "Revisit earliest marks":
            revisit_n = int(st.number_input(
                "How many of the earliest marks",
                min_value=1, max_value=max(1, len(marks)),
                value=min(130, max(1, len(marks))), step=10,
            ))
        st.session_state.nav_mode = nav_mode
        st.session_state.revisit_n = revisit_n

        align_radius = st.slider(
            "Alignment circle radius (m)", min_value=0.0, max_value=40.0,
            value=st.session_state.get(
                "align_radius", _DEFAULT_ALIGN_RADIUS_M,
            ),
            step=1.0,
            help=(
                "Drawn at your marked point, sized to a mound symbol's "
                "ring. Click roughly, then nudge until the circle sits on "
                "the symbol. 0 hides it."
            ),
        )
        st.session_state.align_radius = align_radius
        show_rings = st.checkbox(
            "Show reference rings", value=st.session_state.get(
                "show_rings", True,
            ),
            help="The 5 / 15 / 75 / 110 m rings around the recorded point.",
        )
        st.session_state.show_rings = show_rings
        st.session_state.nudge_step = st.select_slider(
            "Nudge step (m)", options=[0.5, 1.0, 2.5, 5.0, 10.0],
            value=st.session_state.get("nudge_step", _DEFAULT_NUDGE_M),
            help="Step size for the i/j/k/l nudge keys.",
        )

        jump = st.number_input(
            "Jump to item", min_value=0, max_value=max(0, n_total - 1),
            value=cursor, step=1,
        )
        if jump != cursor:
            st.session_state.cursor = int(jump)
            st.session_state.pop("refusal", None)
            st.rerun()

    # --- the crop -------------------------------------------------------
    base, geom = render_base_crop(
        float(row["x"]), float(row["y"]), str(args.rasters_dir),
        context_m, args.display_px, args.resampling,
    )
    point_x, point_y = float(row["x"]), float(row["y"])
    nearby_students, nearest_student_m = nearby_student_points(
        students, point_x, point_y,
    )
    nearby_phantoms, nearest_phantom_m = nearby_student_points(
        phantoms, point_x, point_y,
    )
    nearby_superseded, _ = nearby_student_points(
        superseded, point_x, point_y,
    )
    # The subject itself lives in one of these layers, so drop the
    # coincident copy — otherwise every point appears to have a neighbour
    # at 0 m and the readout is meaningless.
    own_layer = nearby_phantoms if is_phantom else nearby_students
    own_layer[:] = [
        p for p in own_layer
        if math.hypot(p[0] - point_x, p[1] - point_y) > 1e-6
    ]
    if is_phantom:
        nearest_phantom_m = _nearest_distance(nearby_phantoms, point_x, point_y)
    else:
        nearest_student_m = _nearest_distance(
            nearby_students, point_x, point_y,
        )
    candidates = [d for d in (nearest_student_m, nearest_phantom_m)
                  if d is not None]
    nearest_m = min(candidates) if candidates else None
    # Which layer that nearest neighbour is in, named with its overlay
    # colour: "a neighbour at 53.8 m" sends the reviewer hunting for the
    # wrong marker when the neighbour is orange and they expect cyan.
    if nearest_m is None:
        nearest_label = ""
    elif nearest_phantom_m is not None and nearest_m == nearest_phantom_m:
        nearest_label = "another promoted mound (orange)"
    else:
        nearest_label = "a student GT point (cyan)"
    context = {
        "student": nearby_students,
        "phantom": nearby_phantoms,
        "superseded": nearby_superseded,
    }

    existing = marks.get(_item_id(row))
    # A key present with value None means the reviewer explicitly cleared
    # the mark. That has to outrank a previously saved position, or
    # clearing would silently undo itself on the next rerun.
    if cursor in st.session_state.pending:
        marked = st.session_state.pending[cursor]
    elif existing is not None and pd.notna(existing.get("x_marked")):
        marked = (float(existing["x_marked"]), float(existing["y_marked"]))
    else:
        marked = None

    # Which items navigation may land on, given the sidebar scope.
    if nav_mode == "All items":
        allowed = set(range(n_total))
    elif nav_mode == "Re-review list":
        allowed = {
            i for i in range(n_total)
            if _item_id(queue.iloc[i]) in re_review_reasons
        }
    elif nav_mode == "Revisit earliest marks":
        # Earliest BY MARKING TIME, which is the order the rule changed in
        # -- not queue order, which the re-sort scrambled relative to it.
        timed = [
            (m.get("marked_at", ""), key) for key, m in marks.items()
        ]
        earliest = {key for _, key in sorted(timed)[:revisit_n]}
        allowed = {
            i for i in range(n_total)
            if _item_id(queue.iloc[i]) in earliest
        }
    else:
        allowed = {
            i for i in range(n_total)
            if _item_id(queue.iloc[i]) not in marks
        }
    if not allowed:
        allowed = {cursor}
    # Switching scope should land on something in scope. Without this the
    # reviewer selects "Re-review list" and sits on whatever unrelated item
    # was already on screen until they press next.
    if cursor not in allowed and st.session_state.get("nav_scope") != nav_mode:
        st.session_state.nav_scope = nav_mode
        st.session_state.cursor = min(allowed)
        st.rerun()
    st.session_state.nav_scope = nav_mode

    # Candidates are numbered before the crop is drawn so the markers on
    # the map and the entries in the partner dropdown carry the SAME label.
    # Distance alone does not disambiguate two neighbours of one layer that
    # sit 64.7 m and 65.5 m away.
    anchor = marked if marked is not None else (point_x, point_y)

    def _bearing(from_xy, to_xy) -> str:
        """Eight-point compass bearing, for a human-readable label."""
        east, north = to_xy[0] - from_xy[0], to_xy[1] - from_xy[1]
        points = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]
        idx = int(((math.degrees(math.atan2(north, east)) % 360) + 22.5)
                  // 45) % 8
        return points[idx]

    candidates = []
    for layer_name, colour, points in (
        ("corrected_student", "cyan", nearby_students),
        ("promoted_phantom", "orange", nearby_phantoms),
    ):
        for cx, cy in points:
            dist = math.hypot(cx - anchor[0], cy - anchor[1])
            if dist <= _FLAG_RADIUS_M:
                candidates.append((dist, layer_name, colour, (cx, cy)))
    candidates.sort()
    numbering = {
        pos: str(i + 1) for i, (_, _, _, pos) in enumerate(candidates)
    }
    # Which candidate positions another item has already claimed as its
    # conflation partner. Two items claiming one point means one of them is
    # wrong, and without this the reviewer would have to remember every
    # earlier decision to notice.
    claimed: dict[tuple[float, float], str] = {}
    for key, record in marks.items():
        px, py = record.get("resolved_partner_x"), record.get(
            "resolved_partner_y",
        )
        if px is None or py is None or pd.isna(px) or pd.isna(py):
            continue
        claimed[(round(float(px), 2), round(float(py), 2))] = str(key)

    def _claim(pos) -> str:
        owner = claimed.get((round(pos[0], 2), round(pos[1], 2)))
        if owner and owner != _item_id(row):
            return f"  ⚠ already used by {owner}"
        return ""

    candidate_labels = [
        f"{i + 1} · {colour} {_layer_name(layer)} — {dist:.1f} m "
        f"{_bearing(anchor, pos)}{_claim(pos)}"
        for i, (dist, layer, colour, pos) in enumerate(candidates)
    ]

    left, right = st.columns([3, 1])

    with left:
        label = (
            f"candidate {row['candidate_id']} · {row['map_name']}"
            if is_phantom
            else f"student point #{int(row['source_index'])}"
        )
        st.subheader(f"Item {cursor} of {n_total - 1} · {label}")
        st.caption(f"`{row['item_type']}` from `{row['source_layer']}`")

        # Symbol type up front, not buried beside the verdict buttons: the
        # reviewer confirms it at a glance on every student item, so it has
        # to be readable without hunting. MapSymbol is the student's own
        # description and is always populated; _reviewed_subtype is a
        # curator re-review present on only 26 of 4,746 features, so it is
        # shown as an addition when it exists rather than as the headline.
        prior_subtype = _text(row.get("prior_symbol_type"))
        student_symbol = _text(row.get("student_map_symbol"))
        student_feature = _text(row.get("student_feature_type"))
        # Headline whatever classification exists for this mound. The
        # curator vocabulary wins where present; failing that, a student
        # item still carries its own MapSymbol description, which is the
        # assertion actually being confirmed on the 4,720 features with no
        # curator subtype.
        if prior_subtype:
            st.markdown(
                "### " + _SYMBOL_LABELS.get(prior_subtype, prior_subtype),
            )
            if student_symbol:
                st.caption(
                    f"student drew: {student_symbol}"
                    + (f" · {student_feature}" if student_feature else ""),
                )
        elif student_symbol:
            st.markdown(f"### {student_symbol}")
            st.caption(
                "student's own description — no curator subtype on record"
                + (f" · {student_feature}" if student_feature else ""),
            )
        else:
            st.markdown("### _no symbol type on record_")

        # A recovery conflict is the one case where the blank is not
        # ignorance but disagreement between passes. Say which values
        # competed, so this is adjudicated rather than skipped past.
        conflict = _text(row.get("prior_symbol_conflict"))
        if conflict:
            competing = " vs ".join(
                _SYMBOL_LABELS.get(v.strip(), v.strip())
                for v in conflict.split(" vs ")
            )
            st.error(
                f"**Symbol type needs adjudicating** — earlier passes "
                f"disagree: {competing}. Pick one below.",
            )
        if geom is None:
            st.image(base)
            st.error(
                "No raster covers this position — record it as uncertain.",
            )
        else:
            annotated = draw_overlays(
                base, geom, (point_x, point_y), context, marked,
                rings_m=_CONTEXT_RINGS_M if show_rings else (),
                numbering=numbering, align_radius_m=align_radius,
            )
            # The zoom level is part of the widget key: a click captured
            # at one window width must not be re-applied after the reviewer
            # zooms, since the pixel means a different distance.
            # The epoch is part of the key so that clearing a mark
            # produces a FRESH component. Without it the widget keeps
            # returning its last click, which would re-place the point on
            # the very next rerun and make "clear" look broken.
            epoch = st.session_state.get("click_epoch", 0)
            click = streamlit_image_coordinates(
                annotated, key=f"crop_{cursor}_{context_m:.0f}_{epoch}",
            )
            # Only act on a NEW click. The component re-reports its last
            # click on every rerun, so comparing against the stored world
            # position would treat a stale re-report as a fresh click and
            # overwrite any keyboard nudge the moment it was made --
            # silently undoing it. Track the raw pixel click instead and
            # ignore repeats.
            if click is not None:
                raw = (click["x"], click["y"])
                consumed = st.session_state.setdefault("last_click", {})
                if consumed.get(cursor) != raw:
                    consumed[cursor] = raw
                    st.session_state.pending[cursor] = geom.display_to_world(
                        *raw,
                    )
                    st.session_state.pop("refusal", None)
                    st.rerun()

    with right:
        st.markdown("**Recorded**")
        st.caption(f"{point_x:.2f}, {point_y:.2f}")
        if is_phantom and pd.notna(row.get("buffer_metres")):
            st.caption(f"buffer {float(row['buffer_metres']):.0f} m")

        st.markdown("**Nearest neighbours**")
        for layer_label, distance in (
            ("student GT", nearest_student_m),
            ("promoted mound", nearest_phantom_m),
        ):
            st.caption(
                f"{layer_label}: "
                + (f"{distance:.1f} m" if distance is not None
                   else f"none within {_STUDENT_SEARCH_M:.0f} m"),
            )

        if nearest_m is not None and nearest_m <= _DEDUP_TOLERANCE_M:
            st.error(
                f"**{nearest_label} at {nearest_m:.1f} m** — inside the "
                f"{_DEDUP_TOLERANCE_M:.0f} m de-duplication tolerance. "
                "This should not have survived de-duplication and is very "
                "likely the same mound counted twice.",
            )
        elif nearest_m is not None and nearest_m < _DISTINCT_FLOOR_M:
            st.warning(
                f"Borderline: {nearest_label} at {nearest_m:.1f} m, between the "
                f"{_DEDUP_TOLERANCE_M:.0f} m de-duplication tolerance "
                f"and the {_DISTINCT_FLOOR_M:.0f} m distinct-mound "
                "floor. Decide whether this is the same mound.",
            )
        elif nearest_m is not None and nearest_m <= _FLAG_RADIUS_M:
            # Why a neighbour is on screen at all. Without this the cyan or
            # orange marker looks like an error rather than the reason the
            # item is in the queue.
            st.info(
                f"**Conflation candidate** — {nearest_label} lies "
                f"{nearest_m:.1f} m away. Beyond the "
                f"{_DISTINCT_FLOOR_M:.0f} m distinct-mound floor, so two "
                "separate mounds is the usual reading — but a nearby "
                "numeral or label can pull a detection this far off the "
                "mound it belongs to, so mark **c** if the imagery shows "
                "one mound recorded twice.",
            )
        elif nearest_m is not None:
            # Beyond the cut, so not queued as a conflation -- but it is
            # still drawn, and an unexplained marker reads as a bug. Every
            # visible neighbour gets an explanation, whatever its distance.
            st.caption(
                f"Nearest neighbour is {nearest_label}, {nearest_m:.1f} m "
                f"away — beyond the {_FLAG_RADIUS_M:.0f} m flag radius, "
                "shown for context only.",
            )

        if "merge_site" in str(row["item_type"]):
            st.info(
                f"Merge site: {len(nearby_superseded)} superseded position(s) "
                "shown in red. Check that the merged centre is right.",
            )

        reasons = re_review_reasons.get(_item_id(row))
        if reasons:
            explain = {
                "rule_consistency":
                    "marked before the adjudication rule was settled — "
                    "re-check it against the current rule",
                "partner_ambiguity":
                    "more than one neighbour was in range and the partner "
                    "was auto-picked as the nearest — confirm it is the "
                    "right one",
            }
            st.warning(
                "**Flagged for re-review**: "
                + "; ".join(explain.get(r, r) for r in str(reasons).split("+")),
            )

        if "curator_addition" in str(row["item_type"]):
            st.error(
                "**W7-R2 — provenance breach.** This point was added to the "
                "student GT from a MODEL DETECTION, which the student layer "
                "must never contain. Check the map: is there actually a "
                "mound here? #4744's 'second of two-touching-mounds' claim "
                "was already found contradicted by the imagery. Mark **x** "
                "if nothing is there; if it IS a real mound it still does "
                "not belong in this layer, and the record needs relocating "
                "to the promoted-mound layer rather than deleting.",
            )

        if "strange_symbol" in str(row["item_type"]):
            st.error(
                "**Unrecognised symbol** — this feature's MapSymbol is not "
                "one of the four mapped forms, so nothing is pre-selected. "
                "Suspected classification error rather than a mound; "
                "confirm from the imagery.",
            )

        if "jitter_sample" in str(row["item_type"]):
            st.info(
                "Jitter sample — no conflation here by construction. Just "
                "mark the true centre and press **d**; the displacement "
                "from the student position is the measurement.",
            )

        if marked is not None:
            displacement = math.hypot(
                marked[0] - point_x, marked[1] - point_y,
            )
            st.markdown("**Marked**")
            st.caption(f"displacement {displacement:.1f} m")

        # Which neighbour a "same as neighbour" verdict means. Nearest-to-
        # the-mark is the right default but is WRONG whenever a nearer
        # neighbour is a genuinely separate mound -- the case that prompted
        # this: a phantom pulled off THIS mound by a number attractor sits
        # further away than a correct, distinct student mound. Auto-
        # resolution would have recorded the wrong association silently.
        def _as_partner(entry):
            dist, layer, _colour, pos = entry
            return (layer, dist, pos[0], pos[1])

        partner_choice = _as_partner(candidates[0]) if candidates else None
        if len(candidates) > 1:
            chosen = st.selectbox(
                "If 'same as a neighbour', which one?",
                options=list(range(len(candidates))),
                format_func=lambda i: candidate_labels[i],
                key=f"partner_{cursor}",
            )
            partner_choice = _as_partner(candidates[chosen])
        elif candidates:
            # Exactly one candidate: no dropdown, so the claim warning has
            # nowhere to appear unless it is stated here. This is the case
            # where the reviewer can least cross-check it themselves.
            st.caption(f"Partner: {candidate_labels[0]}")

        if marked is None:
            st.info("Click the mound centre.")

        # A refused verdict — pressing "d" before placing a centre — is
        # reported here rather than swallowed. Cleared as soon as a mark
        # lands or the reviewer navigates away.
        if st.session_state.get("refusal"):
            st.warning(st.session_state["refusal"])

        # The source sheets are ~5 m/px, so a click cannot resolve better
        # than about half a pixel however far the crop is magnified. Say
        # so on screen: the output's float columns would otherwise imply
        # a precision the imagery does not carry.
        if geom is not None:
            native_m = abs(geom.transform.a)
            st.caption(
                f"Source {native_m:.2f} m/px — marking precision floor "
                f"±{native_m / 2:.1f} m",
            )

        if existing is not None:
            st.success(f"Saved: {existing['verdict']}")

        # Symbol type — offered on every item. Phantoms carry one too: the
        # reviews that promoted them recorded a symbol_type, which
        # build_marking_queue.py joins back by coordinate (770 of 773
        # recovered) since canonical-review.csv dropped the column.
        prior = _text(row.get("prior_symbol_type"))
        recorded = _text(row.get("student_map_symbol"))
        feature = _text(row.get("student_feature_type"))

        st.divider()
        st.markdown("**Symbol type**")
        if recorded:
            st.caption(
                f"student: {recorded}" + (f" · {feature}" if feature else ""),
            )
        options = list(_SYMBOL_TYPES)
        if prior and prior not in options:
            options.insert(0, prior)
        default = options.index(prior) if prior in options else 0
        symbol_type = st.radio(
            "Confirm or correct",
            options=options,
            index=default,
            key=f"symbol_{cursor}",
            format_func=lambda v: _SYMBOL_LABELS.get(v, v),
            label_visibility="collapsed",
        )
        if prior:
            prior_label = _SYMBOL_LABELS.get(prior, prior)
            if symbol_type != prior:
                st.warning(f"changed from **{prior_label}**")
            else:
                st.caption(f"confirms {prior_label}")
        else:
            st.caption("nothing on record — your call sets it")

        st.divider()
        for key, (verdict, label) in _VERDICTS.items():
            needs_click = verdict in _VERDICTS_NEEDING_A_CLICK
            # Deliberately NOT disabled when a click is still required.
            # A disabled button silently swallows the keyboard shortcut --
            # the browser ignores dispatched clicks on it -- so the
            # reviewer presses "d", nothing happens, and there is no
            # feedback explaining why. Keep the button live and refuse
            # the action explicitly below instead.
            if st.button(
                f"{key}: {label}", key=f"v_{key}_{cursor}",
                use_container_width=True,
            ):
                # Never st.stop() here: the shortcut JS is injected at the
                # end of the script, so halting early would tear down the
                # key handler and break the NEXT keypress as well.
                if needs_click and marked is None:
                    st.session_state.refusal = (
                        f"**{label}** needs a centre first — click the mound "
                        f"on the image, then press **{key}**. Use **s** to "
                        "skip or **u** for uncertain if you cannot place it."
                    )
                else:
                    # A click is recorded whenever one was made, including
                    # for uncertain rows — a marked-but-uncertain centre is
                    # more informative than a bare flag.
                    # Resolve against the MARKED point, not the recorded
                    # one: the reviewer's click is what says which mound
                    # this actually is.
                    resolved = partner_choice
                    marks[_item_id(row)] = build_record(
                        row, marked, verdict, nearest_m, args.marked_by,
                        symbol_type, resolved,
                    )
                    save_marks(marks, args.output)
                    st.session_state.pending.pop(cursor, None)
                    st.session_state.pop("refusal", None)
                    # Advance to the next UNMARKED item, not simply the
                    # next index. Re-sorting the queue scatters previously
                    # completed work through it, so a naive +1 would walk
                    # the reviewer back through decisions already made.
                    nxt = next(
                        (i for i in range(cursor + 1, n_total)
                         if i in allowed
                         and (nav_mode != "Unmarked only"
                              or _item_id(queue.iloc[i]) not in marks)),
                        None,
                    )
                    if nxt is not None:
                        st.session_state.cursor = nxt
                    elif cursor + 1 < n_total:
                        st.session_state.cursor = cursor + 1
                st.rerun()

        if marked is not None:
            st.caption("Nudge the mark")
            nudge_step = st.session_state.get("nudge_step", _DEFAULT_NUDGE_M)
            up_col = st.columns(3)
            with up_col[1]:
                nudged = st.button("i: ↑", key=f"n_i_{cursor}",
                                   use_container_width=True)
            mid = st.columns(3)
            with mid[0]:
                nudged_w = st.button("j: ←", key=f"n_j_{cursor}",
                                     use_container_width=True)
            with mid[1]:
                nudged_d = st.button("k: ↓", key=f"n_k_{cursor}",
                                     use_container_width=True)
            with mid[2]:
                nudged_e = st.button("l: →", key=f"n_l_{cursor}",
                                     use_container_width=True)
            pressed = {
                "i": nudged, "k": nudged_d, "j": nudged_w, "l": nudged_e,
            }
            for key, was_pressed in pressed.items():
                if was_pressed:
                    _, dx, dy = _NUDGE_KEYS[key]
                    st.session_state.pending[cursor] = (
                        marked[0] + dx * nudge_step,
                        marked[1] + dy * nudge_step,
                    )
                    st.rerun()

            if st.button(
                "r: Clear mark", key=f"clear_{cursor}",
                use_container_width=True,
            ):
                st.session_state.pending[cursor] = None
                st.session_state.setdefault("last_click", {}).pop(cursor, None)
                st.session_state["click_epoch"] = (
                    st.session_state.get("click_epoch", 0) + 1
                )
                st.session_state.pop("refusal", None)
                st.rerun()

        st.divider()
        nav_back, nav_next = st.columns(2)
        with nav_back:
            if st.button(
                "b: Back", disabled=cursor == 0, use_container_width=True,
            ):
                prev = [i for i in sorted(allowed) if i < cursor]
                st.session_state.cursor = prev[-1] if prev else max(0, cursor - 1)
                st.session_state.pending.pop(cursor, None)
                st.session_state.pop("refusal", None)
                st.rerun()
        with nav_next:
            if st.button(
                "n: Next", disabled=cursor + 1 >= n_total,
                use_container_width=True,
            ):
                fwd = [i for i in sorted(allowed) if i > cursor]
                st.session_state.cursor = (
                    fwd[0] if fwd else min(n_total - 1, cursor + 1))
                st.session_state.pending.pop(cursor, None)
                st.session_state.pop("refusal", None)
                st.rerun()

    # st.iframe, not st.components.v1.html: the latter was scheduled for
    # removal after 2026-06-01 and now emits a deprecation warning.
    # review_candidates.py still uses the old call — that is legacy debt
    # to fix when next touching that file, not in bulk here.
    # height=1 rather than 0: st.iframe rejects a zero height, and the
    # shortcut iframe only needs to exist, not to be seen.
    st.iframe(_SHORTCUT_JS, height=1)


if __name__ == "__main__":
    main()
