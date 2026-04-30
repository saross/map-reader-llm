#!/usr/bin/env python3
"""Streamlit re-inspection app — confirm Mode 2 of the v2-FP failure taxonomy.

Walks the reviewer through the 117 false-positive (FP) candidates that the
v2 closed-list FP-classifier reclassified as ``settlement-mound`` so that a
per-candidate verdict can be recorded against the **Mode 2** confound
hypothesis (Obs 312, commit ``c4585f60``):

> *Many ``settlement-mound`` calls are actually closed topographic
> contour lines (orange-brown, like settlement-mound ovals, but without
> the diagnostic hachures that distinguish a mound from a contour ring.)*

The unfortunate aliasing is colour-only: at Soviet 1:50,000 scan quality
and the v2 classifier's 150 m / 768 px crop resolution, topo contour ink
and mound-symbol ink share the same orange-brown hue. The sole intended
discriminator — rays / hachures around the mound oval — is intermittently
below the visual-resolution threshold.

This app focuses on the ``settlement-mound`` sub-class (the largest of
the four burial-mound subtypes within the 177-row bet-test set, per
Obs 308). It uses the **same 150 m / 768 px crop the v2 classifier saw**
(displayed at 300 px to mirror ``CLASSIFIER_VIEW_PX`` from the bet-test
app) so the reviewer adjudicates on the model's own visual evidence.

Verdicts (keyboard ``1`` / ``2`` / ``3`` / ``4``):

1. ``closed_topo_line_no_hachures`` — Mode 2 confirmed: an orange-brown
   closed contour ring with no rays / hachures.
2. ``closed_topo_line_with_hachures`` — closed contour but DOES have
   hachures. A different cartographic feature (potentially the Mode 3
   "many hachures" symbol). Flag for further classification.
3. ``other_orange_brown_feature`` — a different orange-brown feature
   class (open contour, road segment, etc.). Free-text note encouraged.
4. ``not_orange_brown`` — not the colour-aliasing mechanism at all; a
   different failure mode entirely.

Verdicts persist to
``results/55maps-fp-classification/v2-burial-mound-bet-test/``
``settlement-mound-mode2-verdicts.csv``. The resume key is
``(run, candidate_id)`` because ``candidate_id`` alone is non-unique
across runs (matching the bet-test app's resume convention).

Headline interpretation on completion (all 117 reviewed):

* ``closed_topo_line_no_hachures`` ≥ 60 % → **Mode 2 SUPPORTED**
* 30 % ≤ share < 60 %                  → **Mode 2 PARTIAL**
* share < 30 %                          → **Mode 2 REJECTED**

Usage::

    bash scripts/launch_v2_settlement_mound_mode2.sh

Or directly::

    .venv/bin/streamlit run scripts/v2_settlement_mound_mode2_app.py \\
        --server.port 8502

References:

* Bet-test app (sibling, mirrored patterns):
  ``scripts/v2_burial_mound_bet_test_app.py`` (commits ``3107d476`` /
  ``d318c50c``).
* Obs 312 — bet-test resolved 0/177 review errors (commit
  ``c4585f60``); failure taxonomy Modes 1, 2, 3 documented in
  ``docs/notes/reflections/working-notes.md``.

Author: Shawn Ross, Claude Code (Opus 4.7)
Licence: Apache 2.0
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# Path setup — allow imports from the FP-classifier driver script (whose
# filename contains a hyphen, so we have to load it via importlib).
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
sys.path.insert(0, str(_SCRIPT_DIR))

_FP_CLASSIFY_PATH = _SCRIPT_DIR / "55maps-fp-classify.py"
_fp_spec = importlib.util.spec_from_file_location(
    "fp_classify_v2_mode2", _FP_CLASSIFY_PATH,
)
if _fp_spec is None or _fp_spec.loader is None:
    raise RuntimeError(
        f"Failed to load FP-classifier module from {_FP_CLASSIFY_PATH}",
    )
_fp_classify = importlib.util.module_from_spec(_fp_spec)
# Register the module in ``sys.modules`` BEFORE exec_module so that
# dataclasses defined inside the module (which call ``sys.modules.get(
# cls.__module__)`` to look up enclosing-namespace types) can resolve
# their own module. Without this registration the ``@dataclass``
# decorator on ``FPRecord`` raises ``AttributeError`` on Python ≥ 3.13.
# Mirrors the pattern in ``v2_burial_mound_bet_test_app.py``.
sys.modules["fp_classify_v2_mode2"] = _fp_classify
_fp_spec.loader.exec_module(_fp_classify)
render_classifier_crop = _fp_classify.render_crop


# =========================================================================
# Constants
# =========================================================================

# Source data — v2 classifications JSON (1,119 rows; 117 are
# ``settlement-mound``). The count is verified via
# ``Counter(r['category'] for r in rows)['settlement-mound']`` at app
# start; mismatches are surfaced in a sidebar warning.
FP_CLASSIFICATIONS_PATH = (
    _REPO_ROOT
    / "results/55maps-fp-classification/fp_classifications.json"
)

# Output directory + verdicts CSV path. Re-uses the bet-test directory
# so all post-hoc inspections of the v2 reclassifications co-locate.
OUTPUT_DIR = (
    _REPO_ROOT
    / "results/55maps-fp-classification/v2-burial-mound-bet-test"
)
VERDICTS_CSV_PATH = OUTPUT_DIR / "settlement-mound-mode2-verdicts.csv"

# Crop-view default — capped at 300 px to match ``CLASSIFIER_VIEW_PX``
# in the bet-test app (Soviet 1:50,000 raster source resolution is only
# ~70-150 px per 150 m crop; doubling to 300 px stays close to native
# while remaining inspectable, and avoids the upscale pixelation
# artefacts the user observed at 768 px).
CLASSIFIER_VIEW_PX: int = 300

# The sub-class under inspection. Set in ``planning/...`` and Obs 312.
TARGET_CATEGORY: str = "settlement-mound"

# Headline-interpretation thresholds (per spec §7).
MODE2_SUPPORTED_THRESHOLD: float = 0.60
MODE2_PARTIAL_THRESHOLD: float = 0.30

# Verdict labels — order drives the on-screen button order and the
# keyboard-shortcut digit (``1`` → first, ``2`` → second, etc.).
VERDICTS: list[tuple[str, str, str]] = [
    (
        "closed_topo_line_no_hachures",
        "1",
        "Closed topo line — no hachures (Mode 2 confirmed)",
    ),
    (
        "closed_topo_line_with_hachures",
        "2",
        "Closed topo line — WITH hachures (different feature)",
    ),
    (
        "other_orange_brown_feature",
        "3",
        "Other orange-brown feature (note recommended)",
    ),
    (
        "not_orange_brown",
        "4",
        "Not orange-brown — different failure mode",
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
        List of v2-classification dicts with keys: ``run``,
        ``candidate_id``, ``map_name``, ``x``, ``y``, ``source_tile``,
        ``category``, ``raw_category``, ``confidence``, ``rationale``,
        ``success``, ``error``, ``input_tokens``, ``output_tokens``.
    """
    with open(FP_CLASSIFICATIONS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def build_queue(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Construct the deterministic review queue.

    Filters the 1,119 v2 classifications to just the
    ``settlement-mound`` sub-class (117 rows for the published
    classification at commit ``ec21c8ef``) and orders them by
    ``(run, descending confidence, candidate_id)`` for a stable
    resume order — matching the bet-test app's queue-ordering
    convention.

    Args:
        rows: Full FP-classifications list (1,119 rows for the v2 run).

    Returns:
        Ordered list of candidate dicts where every row has
        ``category == "settlement-mound"``.
    """
    target_rows = [
        dict(r) for r in rows
        if r.get("category") == TARGET_CATEGORY
    ]
    target_rows.sort(
        key=lambda r: (
            str(r.get("run", "")),
            -float(r.get("confidence", 0.0)),
            str(r.get("candidate_id", "")),
        ),
    )
    return target_rows


# =========================================================================
# CSV persistence — settlement-mound-mode2-verdicts.csv
# =========================================================================


VERDICTS_CSV_HEADER: list[str] = [
    "run",
    "candidate_id",
    "mode2_verdict",
    "note",
    "timestamp",
]


def load_existing_verdicts() -> dict[tuple[str, str], dict[str, Any]]:
    """Load existing verdicts for resume support.

    Returns:
        Dict keyed on ``(run, candidate_id)`` mapping to the full row
        dict (mode2_verdict, note, timestamp). Empty dict if the file
        does not yet exist or is malformed.
    """
    if not VERDICTS_CSV_PATH.is_file():
        return {}
    out: dict[tuple[str, str], dict[str, Any]] = {}
    try:
        with open(VERDICTS_CSV_PATH, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                key = (
                    str(row.get("run", "")),
                    str(row.get("candidate_id", "")),
                )
                out[key] = {
                    "mode2_verdict": row.get("mode2_verdict", ""),
                    "note": row.get("note", ""),
                    "timestamp": row.get("timestamp", ""),
                }
    except Exception:  # noqa: BLE001 — corrupt file → start fresh
        return {}
    return out


def append_verdict_row(
    run: str,
    candidate_id: str,
    mode2_verdict: str,
    note: str,
) -> None:
    """Append a verdict row to the on-disk CSV (atomic-ish via flush+fsync).

    Creates the parent directory and writes the header on first save.
    Uses ``fsync`` after each row so a crash mid-session loses at most
    the in-flight row (mirrors the bet-test app's persistence pattern).

    Args:
        run: The candidate's source run (T0.3 / T0.7 / image / text-MIN).
        candidate_id: Per-run candidate identifier (string-typed because
            historical CSVs sometimes left-pad with zeros).
        mode2_verdict: One of ``closed_topo_line_no_hachures``,
            ``closed_topo_line_with_hachures``,
            ``other_orange_brown_feature``, ``not_orange_brown``.
        note: Optional free-text note from the reviewer.
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
            "mode2_verdict": mode2_verdict,
            "note": note,
            "timestamp": timestamp,
        })
        fh.flush()
        # fsync for crash-resistance — kernel buffer to disk.
        try:
            import os
            os.fsync(fh.fileno())
        except OSError:
            # Some filesystems (e.g., overlayfs in containers) reject
            # fsync; the flush above is sufficient for normal process
            # exit, so degrade gracefully.
            pass


def pop_last_verdict_row() -> dict[str, str] | None:
    """Remove the last verdict row from the on-disk CSV and return it.

    Used by the "Undo last verdict" button to back the queue up by one
    step. Re-writes the CSV without the popped row + fsyncs so the
    in-memory session state can be reloaded from disk and the queue
    position re-derived.

    Returns:
        Dict of the popped row's columns (run, candidate_id,
        mode2_verdict, note, timestamp), or ``None`` if the CSV is
        absent or empty.
    """
    if not VERDICTS_CSV_PATH.is_file():
        return None
    rows: list[dict[str, str]] = []
    with open(VERDICTS_CSV_PATH, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    if not rows:
        return None
    last_row = rows[-1]
    remaining = rows[:-1]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(VERDICTS_CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=VERDICTS_CSV_HEADER)
        writer.writeheader()
        for row in remaining:
            writer.writerow(row)
        fh.flush()
        try:
            import os
            os.fsync(fh.fileno())
        except OSError:
            pass
    return last_row


# =========================================================================
# Crop rendering
# =========================================================================


@st.cache_data(show_spinner=False)
def render_classifier_crop_cached(x: float, y: float) -> Image.Image | None:
    """Cache wrapper around the v2 FP-classifier's exact crop.

    The underlying crop is the 150 m / 768 px window the v2 classifier
    actually saw — no rings, no centre cross. Streamlit displays it at
    ``CLASSIFIER_VIEW_PX`` (300 px) to avoid upscale-pixelation
    artefacts. Mirrors the bet-test app's headline view so the Mode 2
    inspection adjudicates on the same visual evidence the model used.
    """
    return render_classifier_crop(centroid_x=x, centroid_y=y)


# =========================================================================
# Streamlit UI
# =========================================================================


def _select_current_index(
    queue: list[dict[str, Any]],
    verdicts: dict[tuple[str, str], dict[str, Any]],
) -> int:
    """Return the index of the next candidate to review.

    Walks the queue and returns the index of the first row not yet
    judged. Returns ``len(queue)`` once all rows are resolved (no more
    work — fall through to the summary panel).
    """
    for i, c in enumerate(queue):
        key = (str(c["run"]), str(c["candidate_id"]))
        if key not in verdicts:
            return i
    return len(queue)


def _render_summary_panel(
    queue: list[dict[str, Any]],
    verdicts: dict[tuple[str, str], dict[str, Any]],
) -> None:
    """Render the end-of-queue summary table + Mode 2 interpretation.

    The headline interpretation thresholds are documented in the spec
    (commit context — Obs 312, plan §7) and at the module-level
    constants ``MODE2_SUPPORTED_THRESHOLD`` / ``MODE2_PARTIAL_THRESHOLD``.
    """
    st.success(
        "All settlement-mound candidates judged. "
        "Mode 2 interpretation below.",
    )

    # Restrict to the queue's keys so a stale CSV from a different run
    # cannot pollute the headline.
    queue_keys = {
        (str(c["run"]), str(c["candidate_id"])) for c in queue
    }
    queue_verdicts = [
        v["mode2_verdict"] for k, v in verdicts.items() if k in queue_keys
    ]
    counter = Counter(queue_verdicts)

    n_total = len(queue)

    # ---- Verdict breakdown table ----
    st.markdown(
        f"### Verdict breakdown — {n_total} settlement-mound calls",
    )
    if n_total > 0:
        table_rows = []
        for verdict_name, _key, _label in VERDICTS:
            count = counter.get(verdict_name, 0)
            share = 100.0 * count / n_total
            table_rows.append({
                "Verdict": verdict_name,
                "Count": count,
                f"Share of {n_total}": f"{share:.1f} %",
            })
        st.table(table_rows)

    # ---- Headline Mode 2 interpretation ----
    confirmed = counter.get("closed_topo_line_no_hachures", 0)
    confirmed_share = confirmed / n_total if n_total > 0 else 0.0

    st.markdown("### Mode 2 interpretation")
    st.markdown(
        f"- ``closed_topo_line_no_hachures`` count: "
        f"**{confirmed} / {n_total}** "
        f"(**{confirmed_share * 100:.1f} %**)\n"
        f"- ``≥ {MODE2_SUPPORTED_THRESHOLD * 100:.0f} %`` → "
        "**Mode 2 SUPPORTED**\n"
        f"- ``{MODE2_PARTIAL_THRESHOLD * 100:.0f}-"
        f"{MODE2_SUPPORTED_THRESHOLD * 100:.0f} %`` → "
        "**Mode 2 PARTIAL**\n"
        f"- ``< {MODE2_PARTIAL_THRESHOLD * 100:.0f} %`` → "
        "**Mode 2 REJECTED**",
    )
    if confirmed_share >= MODE2_SUPPORTED_THRESHOLD:
        st.success(
            f"**Mode 2 SUPPORTED** — {confirmed_share * 100:.1f} % of "
            "settlement-mound calls are closed topographic contours "
            "without hachures, confirming the colour-aliasing "
            "hypothesis as the dominant confound for this sub-class.",
        )
    elif confirmed_share >= MODE2_PARTIAL_THRESHOLD:
        st.warning(
            f"**Mode 2 PARTIAL** — {confirmed_share * 100:.1f} % of "
            "settlement-mound calls match the closed-topo-line "
            "pattern. The colour-aliasing story holds for a "
            "substantive minority but does not dominate; review the "
            "remaining verdict classes to characterise the additional "
            "failure modes.",
        )
    else:
        st.error(
            f"**Mode 2 REJECTED** — only {confirmed_share * 100:.1f} % "
            "of settlement-mound calls match the closed-topo-line "
            "pattern. The Mode 2 colour-aliasing hypothesis does not "
            "hold for this sub-class; the Discussion text in "
            "working-notes.md (Obs 312) needs softening.",
        )


def main() -> None:
    """Streamlit app entry point.

    Renders the Mode 2 confirmation UI: progress, current crop,
    candidate metadata, v2 verdict + rationale, four verdict buttons,
    optional notes textarea, and a sidebar with running tally.
    Persists each verdict to disk on submit and resumes from the
    on-disk verdicts CSV on next launch.
    """
    st.set_page_config(
        page_title="v2 settlement-mound — Mode 2 confirmation",
        layout="centered",
    )

    # ---- Load and queue ----
    rows = load_classifications()
    queue = build_queue(rows)
    n_queue = len(queue)

    # ---- Session state ----
    if "verdicts" not in st.session_state:
        st.session_state.verdicts = load_existing_verdicts()
    verdicts: dict[tuple[str, str], dict[str, Any]] = (
        st.session_state.verdicts
    )

    # ---- Sidebar ----
    with st.sidebar:
        st.markdown("### Scope")
        st.markdown(
            f"- Sub-class: ``{TARGET_CATEGORY}``\n"
            f"- Calls in queue: **{n_queue}**\n"
            f"- Source: ``fp_classifications.json`` "
            "(55-map FP-classifier v2)\n"
            "- Crop: 150 m / 768 px (displayed at 300 px) — "
            "exactly what the model saw",
        )
        if n_queue != 117:
            # Defensive: the spec quotes 117 from Obs 308. If the source
            # JSON has been re-run since then, surface the divergence so
            # the operator can decide whether the inspection still
            # makes sense.
            st.warning(
                f"Expected 117 ``{TARGET_CATEGORY}`` rows (per "
                f"Obs 308); found {n_queue}. The source JSON may "
                "have been regenerated. Review the working notes "
                "before recording verdicts.",
            )

        st.markdown("---")
        st.markdown("### Running tally")
        # Restrict tally to keys actually in the current queue so a
        # stale CSV from a re-run does not skew the live counts.
        queue_keys = {
            (str(c["run"]), str(c["candidate_id"])) for c in queue
        }
        counter = Counter(
            v["mode2_verdict"]
            for k, v in verdicts.items()
            if k in queue_keys
        )
        for verdict_name, _key, _label in VERDICTS:
            st.write(
                f"- ``{verdict_name}``: "
                f"{counter.get(verdict_name, 0)}",
            )

    # ---- Header + progress ----
    st.title("v2 settlement-mound — Mode 2 confirmation")
    st.caption(
        "Re-inspection of the 117 v2 ``settlement-mound`` "
        "reclassifications. Mode 2 hypothesis (Obs 312, commit "
        "``c4585f60``): the dominant confound is closed topographic "
        "contour lines (orange-brown, no hachures). See "
        "``docs/notes/reflections/working-notes.md`` for the failure "
        "taxonomy.",
    )

    judged_keys = {
        k for k, v in verdicts.items()
        if v.get("mode2_verdict") and k in {
            (str(c["run"]), str(c["candidate_id"])) for c in queue
        }
    }
    n_judged = len(judged_keys)
    st.progress(
        n_judged / n_queue if n_queue > 0 else 1.0,
        text=(
            f"Progress: {n_judged} / {n_queue} verdicts "
            f"({100 * n_judged / n_queue:.1f} %)"
            if n_queue > 0
            else "No candidates to review."
        ),
    )

    # ---- Identify the current candidate ----
    current_idx = _select_current_index(queue, verdicts)
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

    st.markdown(
        f"**Candidate {current_idx + 1} of {n_queue}** "
        f"&nbsp;|&nbsp; run = ``{run}`` "
        f"&nbsp;|&nbsp; candidate_id = ``{candidate_id}``  \n"
        f"map = ``{map_name}`` &nbsp;|&nbsp; "
        f"source_tile = ``{source_tile}``  \n"
        f"centroid = ({x:.1f}, {y:.1f}) [EPSG:32635]",
    )

    # ---- Crop rendering ----
    try:
        img = render_classifier_crop_cached(x, y)
        if img is None:
            st.error(
                f"No raster covers point ({x:.1f}, {y:.1f}); skip "
                "this candidate by recording the most-applicable "
                "verdict (likely ``not_orange_brown`` if the crop "
                "cannot be assessed) with a free-text note.",
            )
        else:
            st.image(img, width=CLASSIFIER_VIEW_PX)
            st.caption(
                "Exact 150 m crop the v2 classifier saw — no rings, "
                "no centre cross. Displayed at 300 px to avoid "
                "upscale-pixelation artefacts (underlying classifier "
                "crop is 768 px).",
            )
    except Exception as exc:  # noqa: BLE001
        st.error(
            f"Failed to render candidate ({run}, {candidate_id}): "
            f"{exc}",
        )

    # ---- v2 model verdict + reviewer's original label ----
    st.markdown(
        f"**v2 verdict:** ``{v2_category}`` "
        f"(confidence {v2_confidence:.2f})  \n"
        f"**v2 rationale:** {v2_rationale or '_(empty)_'}  \n"
        "**Bet-test verdict:** ``v2_overclaim`` (Obs 312 — all 177 "
        "reclassifications confirmed as classifier overclaims)",
    )

    st.divider()

    # ---- Verdict input ----
    note_key = f"note_{run}_{candidate_id}"
    note = st.text_input(
        "Optional note",
        key=note_key,
        placeholder=(
            "Free-text — e.g. ``contour ring at hilltop, no rays`` "
            "or ``open contour, NOT closed``"
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

    # ---- Undo last verdict ----
    n_csv_rows = (
        sum(1 for _ in open(VERDICTS_CSV_PATH, encoding="utf-8")) - 1
        if VERDICTS_CSV_PATH.is_file()
        else 0
    )
    n_csv_rows = max(n_csv_rows, 0)
    undo_col, info_col = st.columns([2, 5])
    with undo_col:
        if st.button(
            "↶ Undo last verdict",
            key="btn_undo_last",
            disabled=(n_csv_rows == 0),
            help=(
                "Remove the most recent verdict from the CSV and step "
                "the queue back by one. Click again to undo further. "
                "Disabled when there are no verdicts to undo."
            ),
            use_container_width=True,
        ):
            popped = pop_last_verdict_row()
            if popped is None:
                st.warning("No verdicts to undo.")
            else:
                st.session_state.verdicts = load_existing_verdicts()
                st.toast(
                    f"Undid {popped.get('mode2_verdict', '?')} "
                    f"verdict for run="
                    f"{popped.get('run', '?')}, candidate_id="
                    f"{popped.get('candidate_id', '?')}.",
                )
                st.rerun()
    with info_col:
        st.caption(
            f"Verdicts on disk: {n_csv_rows}. "
            "Undo pops the latest row each click; multi-undo by "
            "repeating.",
        )

    # ---- Keyboard-shortcut listener ----
    # Mirrors the bet-test app's handler — attached in capture phase to
    # the parent document(s) so keystrokes are intercepted regardless
    # of iframe focus. Buttons whose label starts with "<digit>:" are
    # the verdict-button targets.
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
            if (d.__mode2KeyHandler) {
                d.removeEventListener(
                    'keydown', d.__mode2KeyHandler, true,
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
            if (e.__mode2Seen) return;
            e.__mode2Seen = true;
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
            d.__mode2KeyHandler = handler;
        }
    })();
    </script>
    """
    st.components.v1.html(shortcut_js, height=0)

    # ---- Verdict handling ----
    if button_pressed is not None:
        verdicts[key] = {
            "mode2_verdict": button_pressed,
            "note": note,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        append_verdict_row(run, candidate_id, button_pressed, note)
        st.rerun()


if __name__ == "__main__":
    main()
