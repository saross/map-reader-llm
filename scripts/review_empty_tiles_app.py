#!/usr/bin/env python3
"""Streamlit app for the empty-tile audit (double-miss floor).

Card § 5 of `planning/student-baseline-2026-08-31.md`: the reviewer
walks the nested sample built by `empty_tile_audit_sample.py` — all
10 %-tier tiles first, then the 20 % escalation — and for each tile
either dismisses it (``n``: no mounds) or clicks each mound's
location and picks its map symbol. Click coordinates convert to
EPSG:32635 through the tile's world bounds carried in the manifest,
so no rasters are needed on the review machine.

Interaction (keyboard shortcuts via the battle-tested handler from
`review_candidates.py` / `mark_mound_centres.py`):

- ``n`` — no mounds on this tile; record and advance.
- click — stage a mark at the click point; pick the symbol (radio)
  and press ``a`` (or the button) to add it. Multiple marks per tile.
- ``m`` — save this tile's marks and advance (needs ≥ 1 mark).
- ``u`` — undo the last staged mark.
- ``s`` — skip (decide later; skipped tiles resurface at the end).
- ``b`` — back one tile (re-opens it for editing).

Output (``--output``, default
``results/empty-tile-audit/verdicts.csv``): one row per no-mounds
tile, one row per mark otherwise. Append-only with resume — re-runs
pick up at the first unreviewed tile. Going back and re-saving a tile
supersedes its earlier rows (the loader keeps the last pass).

Usage::

    streamlit run scripts/review_empty_tiles_app.py -- \
        --manifest results/empty-tile-audit/audit_manifest.csv \
        --tiles-dir inputs/empty-tile-audit-tiles \
        --output results/empty-tile-audit/verdicts.csv

Created: 2026-08-31 (Session 145)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DISPLAY_SCALE = 2  # 384 px tile shown at 768 px
TILE_PX = 384

#: Canonical mound symbols (student-layer MapSymbol vocabulary; the four
#: burial-mound subtypes confirmed against TM 30-548 items 81-84, Obs 306)
#: plus the escape hatch.
SYMBOLS = (
    "Hairy brown circle",
    "Hairy black diamond with a dot inside",
    "Hairy black triangle with a dot inside",
    "Hairy black square with a dot inside",
    "Other / unsure (note below)",
)

VERDICT_FIELDS = [
    "order_index", "tile_name", "map_name", "tier", "verdict",
    "mark_index", "x_px", "y_px", "x_world", "y_world", "symbol",
    "note", "reviewed_at", "pass_id",
]

# Same handler as mark_mound_centres.py, with the log prefix, document
# property, and timer renamed so concurrently open review apps do not
# fight over one document property.
_SHORTCUT_JS = """
<script>
(function() {
    // Binds a single keypress to any button whose label starts "<key>:".
    // Attach to every same-origin document reachable (main, top, own,
    // sibling component iframes) and re-attach on an interval, because
    // Streamlit recreates component iframes on every rerun and clicking
    // the tile image moves keyboard focus into its iframe.
    const LOG = function() {
        console.log.apply(console, ['[empty-tiles]'].concat(
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
        setTimeout(function() {
            const opts = {bubbles: true, cancelable: true, view: window};
            try {
                btn.dispatchEvent(new MouseEvent('mousedown', opts));
                btn.dispatchEvent(new MouseEvent('mouseup', opts));
                btn.dispatchEvent(new MouseEvent('click', opts));
            } catch (err) { LOG('dispatch failed', err); }
        }, 0);
    };

    const handler = function(ev) {
        if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
        const tag = (ev.target && ev.target.tagName || '').toLowerCase();
        if (tag === 'input' || tag === 'textarea') return;
        const key = ev.key.toLowerCase();
        let buttons;
        try { buttons = mainDoc.querySelectorAll('button'); }
        catch (e) { return; }
        for (let i = 0; i < buttons.length; i++) {
            const label = (buttons[i].innerText || '').trim().toLowerCase();
            if (label.startsWith(key + ':')) {
                ev.preventDefault();
                ev.stopPropagation();
                simulateClick(buttons[i], label);
                return;
            }
        }
    };

    const attach = function() {
        const docs = collectDocs();
        let added = 0;
        for (let i = 0; i < docs.length; i++) {
            if (docs[i].__emptyTilesKeyHandler) {
                try {
                    docs[i].removeEventListener(
                        'keydown', docs[i].__emptyTilesKeyHandler, true,
                    );
                } catch (err) {}
            }
            try {
                docs[i].addEventListener('keydown', handler, true);
                docs[i].__emptyTilesKeyHandler = handler;
                added += 1;
            } catch (err) {}
        }
        if (added) LOG('handler attached to', added, 'new document(s)');
    };

    attach();
    if (window.__emptyTilesTimer) clearInterval(window.__emptyTilesTimer);
    window.__emptyTilesTimer = setInterval(attach, 700);
})();
</script>
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse arguments passed after Streamlit's ``--``."""
    parser = argparse.ArgumentParser(description="Empty-tile audit review.")
    parser.add_argument(
        "--manifest",
        default="results/empty-tile-audit/audit_manifest.csv")
    parser.add_argument(
        "--tiles-dir", default="inputs/empty-tile-audit-tiles",
        help="Directory holding <map_name>/<tile_name> PNGs.")
    parser.add_argument(
        "--output", default="results/empty-tile-audit/verdicts.csv")
    return parser.parse_args(argv if argv is not None else sys.argv[1:])


@st.cache_data(show_spinner=False)
def load_manifest(path: str) -> pd.DataFrame:
    """The audit manifest, ordered by ``order_index``."""
    df = pd.read_csv(path)
    return df.sort_values("order_index").reset_index(drop=True)


def load_verdicts(path: Path) -> pd.DataFrame:
    """Existing verdicts; empty frame when starting fresh."""
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=VERDICT_FIELDS)


def latest_pass(verdicts: pd.DataFrame) -> pd.DataFrame:
    """Keep only each tile's most recent pass (re-saves supersede)."""
    if verdicts.empty:
        return verdicts
    keep = verdicts.groupby("tile_name")["pass_id"].transform("max")
    return verdicts[verdicts["pass_id"] == keep]


def append_rows(path: Path, rows: list[dict]) -> None:
    """Append verdict rows, writing the header on first use."""
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=VERDICT_FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def to_world(row: pd.Series, x_px: float, y_px: float) -> tuple[float, float]:
    """Tile-pixel click -> EPSG:32635, via the manifest's tile bounds."""
    return (row.minx + x_px * row.px_m, row.maxy - y_px * row.px_m)


def annotated_image(img: Image.Image, marks: list[dict]) -> Image.Image:
    """The display image with staged marks drawn as crosses."""
    out = img.resize((TILE_PX * DISPLAY_SCALE,) * 2, Image.LANCZOS)
    draw = ImageDraw.Draw(out)
    for i, m in enumerate(marks):
        x, y = m["x_px"] * DISPLAY_SCALE, m["y_px"] * DISPLAY_SCALE
        r = 12
        draw.line([(x - r, y), (x + r, y)], fill="red", width=3)
        draw.line([(x, y - r), (x, y + r)], fill="red", width=3)
        draw.text((x + 6, y + 6), str(i + 1), fill="red")
    return out


def main() -> None:
    args = parse_args()
    st.set_page_config(page_title="Empty-tile audit", layout="wide")
    manifest = load_manifest(args.manifest)
    out_path = PROJECT_ROOT / args.output
    tiles_dir = PROJECT_ROOT / args.tiles_dir

    verdicts = latest_pass(load_verdicts(out_path))
    done = set(verdicts["tile_name"])
    skipped: set[str] = set(st.session_state.get("skipped", set()))

    if "cursor" not in st.session_state:
        remaining = manifest[~manifest["tile_name"].isin(done)]
        st.session_state.cursor = (int(remaining.index[0])
                                   if len(remaining) else len(manifest))
    cursor = st.session_state.cursor
    st.session_state.setdefault("marks", [])
    st.session_state.setdefault("last_click", None)

    # End state: everything reviewed (skips resurface first).
    if cursor >= len(manifest):
        pending = [t for t in manifest["tile_name"]
                   if t in skipped and t not in done]
        if pending:
            st.session_state.cursor = int(
                manifest[manifest["tile_name"] == pending[0]].index[0])
            st.rerun()
        n10 = int((manifest["tier"] == "10pct").sum())
        st.success(f"All {len(manifest)} tiles reviewed "
                   f"({n10} in the 10 % tier). Thank you!")
        st.iframe(_SHORTCUT_JS, height=1)
        return

    row = manifest.iloc[cursor]
    n10 = int((manifest["tier"] == "10pct").sum())
    n_done = len(done)
    tier_note = ("10 % tier" if row.tier == "10pct"
                 else "20 % ESCALATION tier — stopping here is fine")
    st.markdown(
        f"**Tile {cursor + 1} / {len(manifest)}** ({n_done} saved) · "
        f"`{row.tile_name}` · {tier_note} · 10 % boundary at {n10}")

    img_path = tiles_dir / row.map_name / row.tile_name
    if not img_path.exists():
        st.error(f"Tile image missing: {img_path} — rsync the file list "
                 "from sapphire (see the sampler's tile_filelist.txt).")
        st.iframe(_SHORTCUT_JS, height=1)
        return
    img = Image.open(img_path)

    col_img, col_ctl = st.columns([3, 1])
    with col_img:
        click = streamlit_image_coordinates(
            annotated_image(img, st.session_state.marks),
            key=f"tile_{cursor}",
        )
        # The component re-reports its last click every rerun; only a NEW
        # raw position counts (same guard as mark_mound_centres.py).
        if click is not None:
            raw = (click["x"], click["y"])
            if raw != st.session_state.last_click:
                st.session_state.last_click = raw
                st.session_state.pending_click = {
                    "x_px": click["x"] / DISPLAY_SCALE,
                    "y_px": click["y"] / DISPLAY_SCALE,
                }
                st.rerun()

    with col_ctl:
        pending = st.session_state.get("pending_click")
        if pending:
            st.markdown(f"Staged click at ({pending['x_px']:.0f}, "
                        f"{pending['y_px']:.0f}) px")
        symbol = st.radio("Symbol", SYMBOLS, key=f"sym_{cursor}")
        note = st.text_input("Note (for other/unsure)", key=f"note_{cursor}")
        if st.button("a: add mark at click", disabled=pending is None):
            m = dict(st.session_state.pending_click)
            m["symbol"], m["note"] = symbol, note
            st.session_state.marks.append(m)
            st.session_state.pending_click = None
            st.rerun()
        if st.button("u: undo last mark",
                     disabled=not st.session_state.marks):
            st.session_state.marks.pop()
            st.rerun()
        for i, m in enumerate(st.session_state.marks):
            st.caption(f"{i + 1}. {m['symbol']} @ "
                       f"({m['x_px']:.0f}, {m['y_px']:.0f})")

    def advance() -> None:
        st.session_state.cursor = cursor + 1
        st.session_state.marks = []
        st.session_state.pending_click = None
        st.session_state.last_click = None
        st.rerun()

    def base_row(verdict: str, idx: int = 0) -> dict:
        return {"order_index": int(row.order_index),
                "tile_name": row.tile_name, "map_name": row.map_name,
                "tier": row.tier, "verdict": verdict, "mark_index": idx,
                "x_px": "", "y_px": "", "x_world": "", "y_world": "",
                "symbol": "", "note": "",
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "pass_id": datetime.now(timezone.utc).strftime(
                    "%Y%m%dT%H%M%S%f")}

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("n: NO mounds — next"):
            append_rows(out_path, [base_row("no_mounds")])
            advance()
    with c2:
        if st.button("m: save marks — next",
                     disabled=not st.session_state.marks):
            rows = []
            for i, m in enumerate(st.session_state.marks):
                r = base_row("mound", i)
                wx, wy = to_world(row, m["x_px"], m["y_px"])
                r.update({"x_px": round(m["x_px"], 1),
                          "y_px": round(m["y_px"], 1),
                          "x_world": round(wx, 2), "y_world": round(wy, 2),
                          "symbol": m["symbol"], "note": m["note"]})
                rows.append(r)
            append_rows(out_path, rows)
            advance()
    with c3:
        if st.button("s: skip — decide later"):
            skipped.add(row.tile_name)
            st.session_state.skipped = skipped
            advance()
    with c4:
        if st.button("b: back one tile", disabled=cursor == 0):
            st.session_state.cursor = cursor - 1
            st.session_state.marks = []
            st.session_state.pending_click = None
            st.session_state.last_click = None
            st.rerun()

    st.iframe(_SHORTCUT_JS, height=1)


if __name__ == "__main__":
    main()
