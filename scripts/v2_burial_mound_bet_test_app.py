#!/usr/bin/env python3
"""Streamlit re-review app for the v2 burial-mound bet test.

Walks the reviewer through the 177 false-positive (FP) candidates that the
v2 closed-list FP-classifier reclassified into one of the four burial-mound
categories (``burial-mound``, ``settlement-mound``,
``triangulation-point-on-burial-mound``, ``benchmark-on-burial-mound``) so
that a per-candidate verdict can be recorded to settle the 2026-04-29 bet
over the true review-error rate.

Default crop view is the **exact 150 m window the v2 classifier
saw** (no rings) so that the reviewer adjudicates the same image the model
adjudicated. A sidebar toggle exposes the richer 400 m ringed view from
``scripts/review_candidates.py`` when extra spatial context aids a
borderline call.

Bet adjudication denominator: **1,675** — the ``not_mound`` corpus the user
actually reviewed and the v2 classifier inspected. The 2 % review-error
threshold equates to **34 ``real_mound_my_error`` verdicts among the 177
reclassifications (≈ 19 % of reclassifications)**.

Verdicts (keyboard ``1`` / ``2`` / ``3`` / ``4``):

1. ``real_mound_my_error`` — user's review-pass label was wrong; this is a
   real mound (any in-scope subtype, including settlement-mound).
2. ``v2_overclaim`` — v2 is wrong; user's ``not_mound`` stands.
3. ``edge_case_ambiguous`` — reasonable people could disagree.
4. ``skip`` — defer this candidate; re-queue once at end. A second skip
   persists as ``skip`` permanently with note ``"double-skip"``.

A blinded calibration sample (~20 ``v2-not_mound``-agreed rows) is mixed
into the queue by default, providing an inter-rater calibration noise
floor. Calibration rows are flagged via ``is_calibration = true`` in the
verdicts CSV and excluded from the headline 177-row count.

Verdicts persist to
``results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv``.
The resume key is ``(run, candidate_id)`` because ``candidate_id`` alone is
non-unique across runs.

Usage::

    bash scripts/launch_v2_burial_mound_bet_test.sh

Or directly::

    .venv/bin/streamlit run scripts/v2_burial_mound_bet_test_app.py

See ``planning/v2-burial-mound-bet-test-app-plan-2026-04-29.md`` (commit
``8d2f7f47``) for the binding design specification, and Obs 308 in
``docs/notes/reflections/working-notes.md`` for the bet's empirical
motivation.

Author: Shawn Ross, Claude Code (Opus 4.7)
Licence: Apache 2.0
"""

from __future__ import annotations

import csv
import json
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/ so we can reuse the 400 m ringed
# context-crop renderer from ``review_candidates.py`` without duplicating it.
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
sys.path.insert(0, str(_SCRIPT_DIR))

# 150 m exact-classifier-view renderer lives in the v2 FP-classifier driver,
# whose filename contains a hyphen — import via importlib rather than the
# normal ``import`` statement (Python identifiers cannot contain hyphens).
import importlib.util  # noqa: E402

_FP_CLASSIFY_PATH = _SCRIPT_DIR / "55maps-fp-classify.py"
_fp_spec = importlib.util.spec_from_file_location(
    "fp_classify_v2", _FP_CLASSIFY_PATH,
)
if _fp_spec is None or _fp_spec.loader is None:
    raise RuntimeError(
        f"Failed to load FP-classifier module from {_FP_CLASSIFY_PATH}",
    )
_fp_classify = importlib.util.module_from_spec(_fp_spec)
# Register the module in ``sys.modules`` BEFORE exec_module so that
# dataclasses defined inside the module (which call ``sys.modules.get(
# cls.__module__)`` to look up enclosing-namespace types) can resolve
# their own module. Without this registration the ``@dataclass`` decorator
# on ``FPRecord`` raises ``AttributeError`` on Python ≥ 3.13.
sys.modules["fp_classify_v2"] = _fp_classify
_fp_spec.loader.exec_module(_fp_classify)
render_classifier_crop = _fp_classify.render_crop

# 400 m ringed view (sidebar toggle).
from review_candidates import render_candidate_context_crop  # noqa: E402

# =========================================================================
# Constants
# =========================================================================

# Mound-category set — the bet test's 177 reclassifications are exactly the
# rows where ``category`` is one of these.
MOUND_CATEGORIES: set[str] = {
    "burial-mound",
    "benchmark-on-burial-mound",
    "triangulation-point-on-burial-mound",
    "settlement-mound",
}

# Source data — v2 classifications JSON committed at ec21c8ef (verified
# during plan-writing; 1,119 rows total, of which 177 are mound-category).
FP_CLASSIFICATIONS_PATH = (
    _REPO_ROOT
    / "results/55maps-fp-classification/fp_classifications.json"
)

# Output directory + verdicts CSV path. Created on first save.
OUTPUT_DIR = (
    _REPO_ROOT
    / "results/55maps-fp-classification/v2-burial-mound-bet-test"
)
VERDICTS_CSV_PATH = OUTPUT_DIR / "verdicts.csv"

# Source rasters used for live crop rendering. Mirrors the v2
# FP-classifier's rasters directory.
RASTERS_DIR = _REPO_ROOT / "inputs/rasters/Russian1981_32635"

# Bet adjudication constants — denominator and threshold (see plan §7.2).
BET_DENOMINATOR: int = 1675
BET_THRESHOLD_PCT: float = 0.02
# 1,675 × 0.02 = 33.5 → rounded up to 34. Inline so the threshold is
# self-documenting in the summary panel.
BET_THRESHOLD_COUNT: int = 34

# Calibration-sample size. The plan says ~20 v2-``not_mound``-agreed rows.
CALIBRATION_SAMPLE_SIZE: int = 20
# Random-seed for calibration-sample reproducibility — fixed so the same
# calibration crops appear across resume sessions.
CALIBRATION_SEED: int = 20260429

# Crop-view defaults.
# CLASSIFIER_VIEW_PX is capped at 300 to avoid the heavy upscaling artefacts
# the user observed at 768 px (Soviet 1:50,000 raster source resolution is
# only ~70-150 px per 150 m crop; doubling to 300 px stays close to native
# while remaining inspectable).
CLASSIFIER_VIEW_PX: int = 300
RINGED_VIEW_PX: int = 600
RINGED_VIEW_CONTEXT_M: float = 400.0

# Verdict labels — order drives the on-screen button order and the
# keyboard-shortcut digit (``1`` → first, ``2`` → second, etc.).
VERDICTS: list[tuple[str, str, str]] = [
    (
        "real_mound_my_error",
        "1",
        "Real mound — my not_mound was the error",
    ),
    (
        "v2_overclaim",
        "2",
        "v2 overclaim — my not_mound stands",
    ),
    (
        "edge_case_ambiguous",
        "3",
        "Edge case — reasonable people could disagree",
    ),
    (
        "skip",
        "4",
        "Skip — re-queue once at end",
    ),
]
VERDICT_KEYS: dict[str, str] = {key: name for name, key, _ in VERDICTS}


# =========================================================================
# Data loading
# =========================================================================


@st.cache_data
def load_classifications() -> list[dict[str, Any]]:
    """Load the v2 FP-classifications JSON.

    Cached so that re-runs of the Streamlit script do not re-read the
    ~600 KB JSON each time.

    Returns:
        List of v2-classification dicts with the keys documented in
        ``planning/...md`` §3.1: ``run``, ``candidate_id``, ``map_name``,
        ``x``, ``y``, ``source_tile``, ``category``, ``raw_category``,
        ``confidence``, ``rationale``, ``success``, ``error``,
        ``input_tokens``, ``output_tokens``.
    """
    with open(FP_CLASSIFICATIONS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def build_queue(
    rows: list[dict[str, Any]],
    include_calibration: bool,
    seed: int = CALIBRATION_SEED,
) -> list[dict[str, Any]]:
    """Construct the deterministic review queue.

    The queue is built from:

    1. The 177 mound-category reclassifications (each tagged
       ``is_calibration=False``), sorted by ``(run, descending confidence,
       candidate_id)`` for a stable order across resume sessions.
    2. If ``include_calibration``: a random sample of
       ``CALIBRATION_SAMPLE_SIZE`` v2-``not_mound``-agreed rows
       (i.e., rows the v2 classifier called a non-mound category) tagged
       ``is_calibration=True`` and shuffled into a stable position
       interleaved with the substantive rows.

    Args:
        rows: Full FP-classifications list (1,119 rows for the v2 run).
        include_calibration: Whether to mix in the calibration sample.
        seed: Random seed for the calibration draw + interleave order.

    Returns:
        Ordered list of candidate dicts with an extra ``is_calibration``
        key. The reviewer cannot tell calibration rows apart from
        substantive rows during review (blinded).
    """
    # Substantive rows — the 177 reclassifications.
    mound_rows = [
        dict(r, is_calibration=False)
        for r in rows
        if r.get("category") in MOUND_CATEGORIES
    ]
    # Stable order: by run alphabetically, then descending confidence,
    # then candidate_id. Matches plan §6.2 step 2.
    mound_rows.sort(
        key=lambda r: (
            str(r.get("run", "")),
            -float(r.get("confidence", 0.0)),
            str(r.get("candidate_id", "")),
        ),
    )

    if not include_calibration:
        return mound_rows

    # Calibration pool — v2 successfully classified into a non-mound
    # category. Excludes failed calls (success=False) so the pool only
    # contains agreed-non-mound rows.
    calibration_pool = [
        r for r in rows
        if r.get("success") is True
        and r.get("category") not in MOUND_CATEGORIES
    ]
    rng = random.Random(seed)
    # Sample without replacement; cap at pool size in case the pool is
    # smaller than the requested sample.
    sample_n = min(CALIBRATION_SAMPLE_SIZE, len(calibration_pool))
    calibration_rows = [
        dict(r, is_calibration=True)
        for r in rng.sample(calibration_pool, sample_n)
    ]

    # Interleave: combine then shuffle a copy with the same seed so the
    # reviewer cannot tell calibration rows from substantive rows by
    # position. We use a separate RNG instance so the calibration draw
    # above is decoupled from the interleave order.
    combined = mound_rows + calibration_rows
    interleave_rng = random.Random(seed + 1)
    interleave_rng.shuffle(combined)
    return combined


# =========================================================================
# CSV persistence — verdicts.csv
# =========================================================================


VERDICTS_CSV_HEADER: list[str] = [
    "run",
    "candidate_id",
    "verdict",
    "note",
    "timestamp",
    "is_calibration",
]


def load_existing_verdicts() -> dict[tuple[str, str], dict[str, Any]]:
    """Load existing verdicts for resume support.

    Returns:
        Dict keyed on ``(run, candidate_id)`` mapping to the full row
        dict (verdict, note, timestamp, is_calibration). Empty dict if
        the file does not yet exist or is malformed.
    """
    if not VERDICTS_CSV_PATH.is_file():
        return {}
    out: dict[tuple[str, str], dict[str, Any]] = {}
    try:
        with open(VERDICTS_CSV_PATH, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                key = (str(row.get("run", "")),
                       str(row.get("candidate_id", "")))
                out[key] = {
                    "verdict": row.get("verdict", ""),
                    "note": row.get("note", ""),
                    "timestamp": row.get("timestamp", ""),
                    "is_calibration": (
                        str(row.get("is_calibration", "")).lower()
                        == "true"
                    ),
                }
    except Exception:  # noqa: BLE001 — corrupt file → start fresh
        return {}
    return out


def append_verdict_row(
    run: str,
    candidate_id: str,
    verdict: str,
    note: str,
    is_calibration: bool,
) -> None:
    """Append a verdict row to the on-disk CSV (atomic-ish via flush+fsync).

    Creates the parent directory and writes the header on first save.
    Uses ``fsync`` after each row so a crash mid-session loses at most
    the in-flight row (per plan §6.2 step 5).

    Args:
        run: The candidate's source run (T0.3 / T0.7 / image / text-MIN).
        candidate_id: Per-run candidate identifier (string-typed because
            historical CSVs sometimes left-pad with zeros).
        verdict: One of ``real_mound_my_error``, ``v2_overclaim``,
            ``edge_case_ambiguous``, ``skip``.
        note: Optional free-text note from the reviewer.
        is_calibration: True for calibration-sample rows; excluded from
            the headline 177-row count in the summary.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_header = not VERDICTS_CSV_PATH.is_file()
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(VERDICTS_CSV_PATH, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=VERDICTS_CSV_HEADER)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "run": run,
            "candidate_id": candidate_id,
            "verdict": verdict,
            "note": note,
            "timestamp": timestamp,
            "is_calibration": "true" if is_calibration else "false",
        })
        fh.flush()
        # fsync for crash-resistance — kernel buffer to disk.
        try:
            import os
            os.fsync(fh.fileno())
        except OSError:
            # Some filesystems (e.g., overlayfs in containers) reject
            # fsync; the flush above is still sufficient for normal
            # process exit, so degrade gracefully.
            pass


# =========================================================================
# Crop rendering
# =========================================================================


@st.cache_data(show_spinner=False)
def render_classifier_crop_cached(x: float, y: float) -> Image.Image | None:
    """Cache wrapper around the v2 FP-classifier's exact crop.

    The underlying crop is the 150 m / 768 px window the v2 classifier
    actually saw — no rings, no centre cross. Streamlit displays it at
    `CLASSIFIER_VIEW_PX` (300 px) to avoid upscale-pixelation artefacts.
    This is the headline view per plan §3.3.
    """
    return render_classifier_crop(centroid_x=x, centroid_y=y)


@st.cache_data(show_spinner=False)
def render_ringed_crop_cached(x: float, y: float) -> Image.Image:
    """Cache wrapper around the 400 m ringed context view.

    Mirrors the rendering used in ``review_candidates.py``: a 400 m
    crop with magenta concentric rings at 50/75/100/125/150 m. Used as
    the sidebar-toggle alternative when extra spatial context helps.
    """
    return render_candidate_context_crop(
        centroid_x=x,
        centroid_y=y,
        rasters_dir=str(RASTERS_DIR),
        context_m=RINGED_VIEW_CONTEXT_M,
        display_px=RINGED_VIEW_PX,
    )


# =========================================================================
# Streamlit UI
# =========================================================================


def _select_current_index(
    queue: list[dict[str, Any]],
    verdicts: dict[tuple[str, str], dict[str, Any]],
    skipped_once: set[tuple[str, str]],
) -> int:
    """Return the index of the next candidate to review.

    First pass: walk the queue; the first row not yet judged is current.
    Second pass: once everyone has been judged (substantively or
    skipped-once), revisit the once-skipped rows.
    Returns ``len(queue)`` if all rows are resolved (no more work).
    """
    # First pass — un-judged rows.
    for i, c in enumerate(queue):
        key = (str(c["run"]), str(c["candidate_id"]))
        if key not in verdicts:
            return i
    # All rows have an entry; revisit any one-time skips that haven't yet
    # been resolved into a substantive verdict.
    for i, c in enumerate(queue):
        key = (str(c["run"]), str(c["candidate_id"]))
        if key in skipped_once and verdicts.get(key, {}).get(
            "verdict",
        ) == "skip":
            return i
    return len(queue)


def _render_summary_panel(
    queue: list[dict[str, Any]],
    verdicts: dict[tuple[str, str], dict[str, Any]],
) -> None:
    """Render the end-of-queue summary table + bet adjudication.

    Excludes calibration-sample rows from the headline 177-row count
    (per plan §7.1) and computes the review-error rate against the
    1,675 ``not_mound`` corpus denominator (plan §7.2). Reports the
    bet outcome inline.
    """
    st.success("All candidates judged. Bet-test results below.")

    # Substantive (non-calibration) rows only — the bet is settled on these.
    substantive = [
        c for c in queue if not c.get("is_calibration", False)
    ]
    sub_keys = {
        (str(c["run"]), str(c["candidate_id"])) for c in substantive
    }
    sub_verdicts = [
        v["verdict"] for k, v in verdicts.items() if k in sub_keys
    ]
    sub_counter = Counter(sub_verdicts)

    # Calibration rows — reported separately as a noise-floor estimate.
    cal_keys = {
        (str(c["run"]), str(c["candidate_id"]))
        for c in queue if c.get("is_calibration", False)
    }
    cal_verdicts = [
        v["verdict"] for k, v in verdicts.items() if k in cal_keys
    ]
    cal_counter = Counter(cal_verdicts)

    # ---- Substantive verdict breakdown ----
    st.markdown("### Verdict breakdown — 177 reclassifications")
    n_sub = len(substantive)
    if n_sub > 0:
        rows = []
        for verdict_name, _key, _label in VERDICTS:
            count = sub_counter.get(verdict_name, 0)
            share = 100.0 * count / n_sub
            rows.append({
                "Verdict": verdict_name,
                "Count": count,
                "Share of 177": f"{share:.1f} %",
            })
        st.table(rows)

    # ---- Bet adjudication ----
    real_mound = sub_counter.get("real_mound_my_error", 0)
    edge = sub_counter.get("edge_case_ambiguous", 0)
    rate = real_mound / BET_DENOMINATOR if BET_DENOMINATOR > 0 else 0.0
    rate_inclusive = (
        (real_mound + edge) / BET_DENOMINATOR
        if BET_DENOMINATOR > 0 else 0.0
    )
    st.markdown("### Bet adjudication")
    st.markdown(
        f"- Denominator: **{BET_DENOMINATOR}** "
        f"(`not_mound` corpus reviewed and v2-inspected)\n"
        f"- Threshold: **{BET_THRESHOLD_COUNT} `real_mound_my_error` "
        f"verdicts** (`{BET_DENOMINATOR} × "
        f"{BET_THRESHOLD_PCT:.0%}` rounded up)\n"
        f"- Review-error rate: "
        f"**{real_mound} / {BET_DENOMINATOR} = "
        f"{rate * 100:.2f} %**\n"
        f"- Inclusive bound (incl. edge-case): "
        f"**{(real_mound + edge)} / {BET_DENOMINATOR} = "
        f"{rate_inclusive * 100:.2f} %**\n"
    )
    if real_mound < BET_THRESHOLD_COUNT:
        st.success(
            f"**PASS** ({real_mound} < {BET_THRESHOLD_COUNT}): Shawn wins "
            "the bet — review-error rate is below 2 %."
        )
    else:
        st.error(
            f"**FAIL** ({real_mound} ≥ {BET_THRESHOLD_COUNT}): the agent "
            "wins the bet — review-error rate is at or above 2 %."
        )

    # ---- Calibration sample ----
    if cal_keys:
        st.markdown("### Calibration sample (blinded)")
        st.markdown(
            f"{len(cal_keys)} v2-``not_mound``-agreed rows were "
            "interleaved into the queue as a fresh-eyes noise-floor "
            "estimate. These are excluded from the headline 177-row "
            "count above."
        )
        cal_rows = []
        for verdict_name, _key, _label in VERDICTS:
            count = cal_counter.get(verdict_name, 0)
            cal_rows.append({"Verdict": verdict_name, "Count": count})
        st.table(cal_rows)


def main() -> None:
    """Streamlit app entry point.

    Renders the bet-test review UI: progress, current crop, candidate
    metadata, v2 verdict + rationale, four verdict buttons, optional
    notes textarea, and a sidebar with view toggles + calibration
    toggle. Persists each verdict to disk on submit and resumes from
    the on-disk verdicts CSV on next launch.
    """
    st.set_page_config(
        page_title="v2 Burial-Mound Bet Test",
        layout="centered",
    )

    # ---- Sidebar controls (declared before main pane so toggles are
    # available when the queue is constructed) ----
    with st.sidebar:
        st.markdown("### View")
        ringed_view = st.toggle(
            "400 m ringed context view",
            value=False,
            help=(
                "OFF (default): show the exact 150 m crop the v2 "
                "classifier saw (displayed at 300 px), no rings. "
                "ON: switch to the 400 m context view with magenta "
                "concentric rings at 50/75/100/125/150 m used in the "
                "regular review UI."
            ),
        )
        st.markdown("---")
        st.markdown("### Queue")
        include_calibration = st.toggle(
            "Include calibration sample (~20 agreed-non-mound rows)",
            value=True,
            help=(
                "ON (default): mix ~20 v2-`not_mound`-agreed rows into "
                "the queue, blinded. Provides a fresh-eyes noise-floor "
                "estimate; excluded from the headline 177-row count."
            ),
        )

    # ---- Load and queue ----
    rows = load_classifications()
    queue = build_queue(rows, include_calibration=include_calibration)

    # ---- Session state — persist resume info across Streamlit re-runs ----
    if "verdicts" not in st.session_state:
        st.session_state.verdicts = load_existing_verdicts()
    verdicts: dict[tuple[str, str], dict[str, Any]] = (
        st.session_state.verdicts
    )

    # Track which rows have been skipped exactly once this session.
    # Used to enforce the "second skip persists permanently" rule (plan
    # §5 + §6.2). Seeded from on-disk verdicts so a resume picks up
    # one-time skips from a prior session.
    if "skipped_once" not in st.session_state:
        st.session_state.skipped_once = {
            k for k, v in verdicts.items() if v.get("verdict") == "skip"
        }
    skipped_once: set[tuple[str, str]] = st.session_state.skipped_once

    # ---- Header + progress ----
    st.title("v2 Burial-Mound Bet Test")
    st.caption(
        "Re-review of the 177 v2 burial-mound reclassifications from the "
        "55-map FP-classification. See "
        "`planning/v2-burial-mound-bet-test-app-plan-2026-04-29.md` "
        "(commit 8d2f7f47) for the binding spec."
    )

    n_queue = len(queue)
    judged_keys = {
        k for k, v in verdicts.items()
        if v.get("verdict") in {
            "real_mound_my_error",
            "v2_overclaim",
            "edge_case_ambiguous",
        } and k in {
            (str(c["run"]), str(c["candidate_id"])) for c in queue
        }
    }
    n_judged = len(judged_keys)
    st.progress(
        n_judged / n_queue if n_queue > 0 else 1.0,
        text=(
            f"Progress: {n_judged} / {n_queue} substantive verdicts "
            f"({100 * n_judged / n_queue:.1f} %)"
        ),
    )

    # Sidebar tally — useful at a glance during review.
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Running tally")
        sub_keys = {
            (str(c["run"]), str(c["candidate_id"])) for c in queue
            if not c.get("is_calibration", False)
        }
        sub_counter = Counter(
            v["verdict"] for k, v in verdicts.items() if k in sub_keys
        )
        for verdict_name, _key, _label in VERDICTS:
            st.write(
                f"- `{verdict_name}`: "
                f"{sub_counter.get(verdict_name, 0)}"
            )

    # ---- Identify the current candidate ----
    current_idx = _select_current_index(queue, verdicts, skipped_once)
    if current_idx >= n_queue:
        _render_summary_panel(queue, verdicts)
        return

    candidate = queue[current_idx]
    run = str(candidate["run"])
    candidate_id = str(candidate["candidate_id"])
    key = (run, candidate_id)

    # ---- Candidate metadata header ----
    map_name = candidate.get("map_name", "?")
    source_tile = candidate.get("source_tile", "?")
    x = float(candidate.get("x", 0.0))
    y = float(candidate.get("y", 0.0))
    v2_category = candidate.get("category", "?")
    v2_confidence = float(candidate.get("confidence", 0.0))
    v2_rationale = candidate.get("rationale", "")
    is_cal = candidate.get("is_calibration", False)

    st.markdown(
        f"**Candidate {current_idx + 1} of {n_queue}** "
        f"&nbsp;|&nbsp; run = `{run}` "
        f"&nbsp;|&nbsp; candidate_id = `{candidate_id}`  \n"
        f"map = `{map_name}` &nbsp;|&nbsp; "
        f"source_tile = `{source_tile}`  \n"
        f"centroid = ({x:.1f}, {y:.1f}) [EPSG:32635]"
    )

    # ---- Crop rendering ----
    # Default: exact classifier view (150 m, displayed at 300 px, no rings). Sidebar
    # toggle flips to the 400 m ringed view used in the regular review
    # UI. Per plan §3.3, the default pins the review to "what could the
    # model see?" — keep this as the headline view.
    try:
        if ringed_view:
            img = render_ringed_crop_cached(x, y)
            st.image(img, width=RINGED_VIEW_PX)
            st.caption(
                "400 m context crop with magenta concentric rings at "
                "50/75/100/125/150 m. Centre cross marks the proposer "
                "centroid."
            )
        else:
            img = render_classifier_crop_cached(x, y)
            if img is None:
                st.error(
                    f"No raster covers point ({x:.1f}, {y:.1f}); "
                    "use the sidebar toggle to flip to the 400 m view "
                    "for context, or skip this candidate."
                )
            else:
                st.image(img, width=CLASSIFIER_VIEW_PX)
                st.caption(
                    "Exact 150 m crop the v2 classifier saw — "
                    "no rings, no centre cross. Displayed at 300 px to "
                    "avoid upscale-pixelation artefacts (underlying "
                    "classifier crop is 768 px)."
                )
    except Exception as exc:  # noqa: BLE001
        st.error(
            f"Failed to render candidate ({run}, {candidate_id}): {exc}",
        )

    # ---- v2 model verdict + reviewer's original label ----
    # Both surfaced so the contradiction is explicit. The original
    # review label is implicitly ``not_mound`` for every row in the
    # FP-classifier's input — surfacing it here saves a CSV round-trip
    # and makes the disputed-call structure visible.
    st.markdown(
        f"**v2 verdict:** `{v2_category}` "
        f"(confidence {v2_confidence:.2f})  \n"
        f"**v2 rationale:** {v2_rationale or '_(empty)_'}  \n"
        f"**Original review label:** `not_mound` "
        "(the v2 model disputes this)"
    )

    st.divider()

    # ---- Verdict input ----
    # Optional notes textarea — keyed on the candidate so the field
    # clears between candidates. Persisted with the verdict on submit.
    note_key = f"note_{run}_{candidate_id}"
    note = st.text_input(
        "Optional note",
        key=note_key,
        placeholder=(
            "Free-text — e.g. 'tell-shaped feature, in scope' or "
            "'reads as a building cluster'"
        ),
    )

    st.markdown("**Your verdict (press 1 / 2 / 3 / 4):**")
    button_pressed: str | None = None
    cols = st.columns(len(VERDICTS))
    for i, (verdict_name, key_char, label) in enumerate(VERDICTS):
        with cols[i]:
            if st.button(
                f"{key_char}: {label}",
                key=f"btn_{key_char}_{run}_{candidate_id}",
                use_container_width=True,
            ):
                button_pressed = verdict_name

    # Keyboard-shortcut listener — adapted from review_candidates.py.
    # The handler is attached in the capture phase to the parent
    # document(s) so that keystrokes are intercepted regardless of
    # iframe focus.
    shortcut_js = """
    <script>
    (function() {
        const docs = [];
        try { docs.push(window.parent.document); } catch (e) {}
        try {
            if (window.top && window.top.document !== window.parent.document) {
                docs.push(window.top.document);
            }
        } catch (e) {}
        docs.push(document);
        const streamlitDoc = docs[0] || document;
        for (const d of docs) {
            if (d.__bettestKeyHandler) {
                d.removeEventListener(
                    'keydown', d.__bettestKeyHandler, true,
                );
            }
        }
        const simulateClick = function(btn) {
            if (!btn) return;
            btn.scrollIntoView({block: 'nearest', behavior: 'instant'});
            setTimeout(function() {
                const opts = {bubbles: true, cancelable: true, view: window};
                try {
                    btn.dispatchEvent(new MouseEvent('mousedown', opts));
                    btn.dispatchEvent(new MouseEvent('mouseup', opts));
                    btn.dispatchEvent(new MouseEvent('click', opts));
                    if (typeof btn.click === 'function') btn.click();
                } catch (err) {}
            }, 0);
        };
        const handler = function(e) {
            if (e.ctrlKey || e.altKey || e.metaKey) return;
            if (e.__bettestSeen) return;
            e.__bettestSeen = true;
            const active = (streamlitDoc.activeElement || null);
            if (active && (active.tagName === 'INPUT' ||
                           active.tagName === 'TEXTAREA' ||
                           active.isContentEditable)) return;
            const key = (e.key || '').toLowerCase();
            if (!key) return;
            const buttons = streamlitDoc.querySelectorAll('button');
            const matches = [];
            for (const btn of buttons) {
                const text = (btn.textContent || '').trim().toLowerCase();
                if (text.startsWith(key + ':')) matches.push(btn);
            }
            if (matches.length === 0) return;
            // Prefer the verdict buttons (last-rendered match).
            const btn = matches[matches.length - 1];
            const focused = streamlitDoc.activeElement;
            if (focused && focused.blur) focused.blur();
            simulateClick(btn);
            e.preventDefault();
            e.stopPropagation();
        };
        for (const d of docs) {
            d.addEventListener('keydown', handler, true);
            d.__bettestKeyHandler = handler;
        }
    })();
    </script>
    """
    st.components.v1.html(shortcut_js, height=0)

    # ---- Verdict handling ----
    if button_pressed is not None:
        # Skip semantics: first skip → record as ``skip`` and add to
        # ``skipped_once`` (the row will resurface at end of queue).
        # Second skip on the same row → persist permanently with note
        # ``"double-skip"``; subsequent passes will not re-queue it.
        if button_pressed == "skip":
            if key in skipped_once:
                # Second skip — finalise.
                final_note = (note + " ; " if note else "") + "double-skip"
                verdicts[key] = {
                    "verdict": "skip",
                    "note": final_note,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_calibration": is_cal,
                }
                append_verdict_row(
                    run, candidate_id, "skip", final_note, is_cal,
                )
                # Remove from one-time skip set so it does not loop again.
                skipped_once.discard(key)
            else:
                verdicts[key] = {
                    "verdict": "skip",
                    "note": note,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_calibration": is_cal,
                }
                append_verdict_row(
                    run, candidate_id, "skip", note, is_cal,
                )
                skipped_once.add(key)
        else:
            # Substantive verdict — overrides any prior skip on this row.
            verdicts[key] = {
                "verdict": button_pressed,
                "note": note,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "is_calibration": is_cal,
            }
            append_verdict_row(
                run, candidate_id, button_pressed, note, is_cal,
            )
            skipped_once.discard(key)
        st.rerun()


if __name__ == "__main__":
    main()
