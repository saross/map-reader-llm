#!/usr/bin/env python3
"""
Render the K-ladder tile-join job's ``summary.json`` as its ``summary.md`` tables.

Part of the S166 K-ladder tile-join job
(``reports/s166-agent-records/k-ladder-mcc-join.md``). Every number in the
Markdown is read from ``summary.json`` (written by ``summarise.py``), so
nothing is retyped. The prose around the tables is fixed text; the record
carries the reading.

Usage: python render.py <summary_json> <summary_md> <date> <commit>

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

JOINS = ("id", "geometric-primary", "geometric-contains")
SHORT = {"id": "`id`", "geometric-primary": "primary", "geometric-contains": "contains"}

NAMES = {
    "gs-stride-a": "GS stride A (board frame)",
    "55map-stride-a-r2": "55-map stride A, r2",
    "55map-stride-a-standardised": "55-map stride A, standardised",
    "55map-stride-b-r2": "55-map stride B, r2",
    "55map-stride-b-standardised": "55-map stride B, standardised",
    "55map-stride-b-g37vf-r2": "55-map stride B, 3.7 verifier",
    "37arm1-r2": "3.7 arm 1",
    "37arm2-r2": "3.7 arm 2",
    "tier-e": "tier E (as evaluated)",
    "phase2-flash-minimal-text-n30-t07-text-t0-3": "MINIMAL text T 0.3",
    "phase2-flash-minimal-text-n30-t07-text-t0-7": "MINIMAL text T 0.7",
    "phase2-flash-minimal-text-n30-t07-text-t1-0": "MINIMAL text T 1.0",
    "phase2-flash-high-text-n5-text-t0-3": "HIGH text T 0.3",
    "phase2-flash-high-text-n5-text-t0-7": "HIGH text T 0.7",
    "phase2-flash-high-text-n5-text-t1-0": "HIGH text T 1.0",
    "phase2-image-n5-image-t0-3": "MINIMAL image T 0.3",
    "phase2-image-n5-image-t0-7": "MINIMAL image T 0.7",
    "phase2-image-n5-image-t1-0": "MINIMAL image T 1.0",
    "phase2-flash-high-image-n5-image-t0-3": "HIGH image T 0.3",
    "phase2-flash-high-image-n5-image-t0-7": "HIGH image T 0.7",
    "phase2-flash-high-image-n5-image-t1-0": "HIGH image T 1.0",
    "phase2-scale-4-optimal-487": "scale-4-optimal 487",
}


def name(slug: str) -> str:
    """A ladder's display name; clipped ladders carry a marker."""
    if slug.startswith("d51clip-"):
        base = slug.removeprefix("d51clip-")
        return f"{NAMES.get(base, base).replace(' (as evaluated)', '')}, D51 clipped"
    return NAMES.get(slug, slug)


def p_text(p: float) -> str:
    """A BH p-value at four decimals, with the permutation floor shown."""
    return "<0.0001" if p < 0.0001 else f"{p:.4f}"


def cell(delta: float, p: float, sig: bool) -> str:
    """One ΔMCC (BH p) table cell, bold when BH-significant."""
    text = f"{delta:+.4f} ({p_text(p)})"
    return f"**{text}**" if sig else text


def ks(values: list[int]) -> str:
    """A set of pass counts as text."""
    return "{" + ", ".join(str(v) for v in values) + "}" if values else "none"


def main() -> int:
    """Write the Markdown."""
    src, dst, date, commit = (Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3],
                              sys.argv[4])
    s = json.loads(src.read_text())
    lines: list[str] = []
    add = lines.append

    add("# K-ladder tile-MCC under the three tile joins")
    add("")
    add(f"> **Last revised**: {date} (original publication). See "
        "[§ Changelog](#changelog) for revision history.")
    add("")
    add("Rendered by `reports/s166-agent-records/k-ladder-mcc-join-scripts/render.py` "
        "from `summary.json` in this directory; the record, with the reading, is "
        "`reports/s166-agent-records/k-ladder-mcc-join.md`. Computed at "
        f"`{commit}` on sapphire. Joins: `id` is the published name join; "
        "\"primary\" and \"contains\" are `geometric-primary` and "
        "`geometric-contains` (`lib_advanced_metrics.TILE_JOINS`). Every delta "
        "is (higher K) − (lower K); BH p is adjusted within each ladder's own "
        "round-robin; bold marks BH q = 0.05 significance.")
    add("")

    # Gate
    add("## 1. Gate: the `id` runs against the committed artefacts")
    add("")
    add("| artefact set | files compared | passed | keys this run adds |")
    add("|---|---:|---|---:|")
    for key, g in s["gate"]["gates"].items():
        n = g.get("n_files_compared", g.get("n_rows_replayed"))
        add(f"| `{key}` | {n} | {'yes' if g['passed'] else '**NO**'} | "
            f"{len(g.get('schema_additions', []))} |")
    add("")
    add(f"All passed: **{'yes' if s['gate']['all_passed'] else 'NO'}**.")
    add("")

    # Q1
    add("## 2. Tile-MCC from K = 1 to the best F1 rung")
    add("")
    add("| ladder | pair | `id` | primary | contains |")
    add("|---|---|---:|---:|---:|")
    by_join = {j: {r["ladder"]: r for r in s["q1_k1_to_best"][j]["rows"]}
               for j in JOINS}
    for slug, row in by_join["id"].items():
        cells = [cell(by_join[j][slug]["mcc_delta"], by_join[j][slug]["mcc_p_bh"],
                      by_join[j][slug]["mcc_significant"]) for j in JOINS]
        add(f"| {name(slug)} | {row['pair']} | " + " | ".join(cells) + " |")
    add("")
    for basis, label in (("the_21_as_evaluated", "as evaluated"),
                         ("the_21_on_d51_clipped_basis", "six Phase 2 ladders on D51's "
                                                         "clipped basis")):
        add(f"The 21 verified ladders ({label}):")
        add("")
        add("| join | falls | rises | significant falls | significant rises |")
        add("|---|---:|---:|---|---|")
        for j in JOINS:
            t = s["q1_k1_to_best"][j][basis]
            add(f"| {SHORT[j]} | {t['falls']} of {t['n']} | {t['rises']} of {t['n']} | "
                f"{len(t['significant_falls'])}: "
                f"{'; '.join(name(x) for x in t['significant_falls']) or '—'} | "
                f"{len(t['significant_rises'])}: "
                f"{'; '.join(name(x) for x in t['significant_rises']) or '—'} |")
        add("")
    add("Every other BH-significant tile-MCC pair (adjacent rungs, not the "
        "K = 1 → best pair):")
    add("")
    add("| join | ladder | pair | ΔMCC (BH p) |")
    add("|---|---|---|---:|")
    for j in JOINS:
        rows = (s["q1_k1_to_best"][j]["other_significant_mcc_pairs_the_21"]
                + s["q1_k1_to_best"][j]["other_significant_mcc_pairs_clipped"])
        if not rows:
            add(f"| {SHORT[j]} | — | — | — |")
        for r in rows:
            add(f"| {SHORT[j]} | {name(r['ladder'])} | {r['pair']} | "
                f"{r['delta']:+.4f} ({p_text(r['p_bh'])}) |")
    add("")

    # Q2
    add("## 3. Tile-MCC Hsu MCB admissible sets and the highest-MCC rung")
    add("")
    add("| ladder | `id` set (top) | primary set (top) | contains set (top) |")
    add("|---|---|---|---|")
    for part in ("main", "clipped"):
        lads = {j: {x["slug"]: x for x in s["q2_mcb"][j][part]["ladders"]}
                for j in JOINS}
        for slug in lads["id"]:
            cells = [f"{ks(lads[j][slug]['mcc_admissible_K'])} "
                     f"(K = {lads[j][slug]['mcc_best_K']})" for j in JOINS]
            add(f"| {name(slug)} | " + " | ".join(cells) + " |")
    add("")
    add("| join | ladders | K = 1 admissible | K = 1 highest | highest at K = 1 / 3 / 5 "
        "/ 10 | whole ladder admissible | K = 10 excluded |")
    add("|---|---:|---:|---:|---|---:|---:|")
    for part, label in (("main", "22"), ("clipped", "7 clipped")):
        for j in JOINS:
            m = s["q2_mcb"][j][part]
            h = m["highest_K_counts"]
            add(f"| {SHORT[j]} ({label}) | {m['n_ladders']} | {m['k1_admissible']} | "
                f"{m['k1_highest']} | {h['1']} / {h['3']} / {h['5']} / {h['10']} | "
                f"{m['whole_ladder']} | {len(m['excludes_K10'])} |")
    add("")

    # Q3
    add("## 4. § 8.6: K = 1 → 10 tile-MCC, consensus-only against verified")
    add("")
    add("| join | consensus only (K1 → K10) | verified, as evaluated (BH p) | "
        "verified, D51 clipped (BH p) | swing, as evaluated / clipped | "
        "sign reversal, as evaluated / clipped |")
    add("|---|---:|---:|---:|---:|---|")
    for j in JOINS:
        q = s["q3_section_8_6"][j]
        c = q["consensus_only"]
        a, k = q["verified_as_evaluated"], q["verified_d51_clipped"]
        add(f"| {SHORT[j]} | {c['mcc_k1']:.4f} → {c['mcc_k10']:.4f} "
            f"({c['delta']:+.4f}) | {a['low']:.4f} → {a['high']:.4f} "
            f"({a['delta']:+.4f}, {p_text(a['p_bh'])}) | {k['low']:.4f} → "
            f"{k['high']:.4f} ({k['delta']:+.4f}, {p_text(k['p_bh'])}) | "
            f"{q['swing_as_evaluated']:.4f} / {q['swing_clipped']:.4f} | "
            f"{'yes' if q['sign_reversal_as_evaluated'] else 'no'} / "
            f"{'yes' if q['sign_reversal_clipped'] else 'no'} |")
    add("")

    # Q4
    m = s["q4_mechanism"]
    add("## 5. Diagnostic: `id`-join FN tiles that hold the rung's own detections")
    add("")
    pooled = m["pooled_22_ladders_as_evaluated"]
    add(f"Pooled over the 22 as-evaluated ladders' rungs: {pooled['with_detection_inside']:,} "
        f"of {pooled['fn_tiles']:,} false-negative tiles ({100 * pooled['share']:.1f} %). "
        f"Cross-check of each rung's `id` MCC against its tiering: "
        f"{m['crosscheck_against_id_tierings']['n_mismatches']} mismatches.")
    add("")
    add("From K = 1 to each ladder's top rung, the number of ladders whose count "
        "rises / falls / stays the same:")
    add("")
    add("| ladders | detections | FN tiles | FN tiles holding a detection | share | "
        "geometric − `id` MCC gain larger at the top rung (primary / contains) |")
    add("|---|---|---|---|---|---|")
    for key, label in (("gold_standard_frame_ladders", "gold-standard frame"),
                       ("deployment_55map_ladders", "55-map deployment"),
                       ("all_22", "all 22")):
        t = m["k1_to_top_k"][key]

        def rfs(block: dict) -> str:
            return f"{block['rise']} / {block['fall']} / {block['same']}"

        add(f"| {label} ({t['n']}) | {rfs(t['n_detections'])} | {rfs(t['fn_tiles'])} | "
            f"{rfs(t['fn_tiles_holding_a_detection'])} | {rfs(t['share'])} | "
            f"{t['join_gain_larger_at_top_k_geometric-primary']} / "
            f"{t['join_gain_larger_at_top_k_geometric-contains']} of {t['n']} |")
    add("")
    add("| ladder | FN tiles holding a detection / FN tiles, by K | share, K = 1 → "
        "top K | geometric − `id` MCC gain, K = 1 → top K (primary; contains) |")
    add("|---|---|---:|---|")
    for lad in m["ladders"]:
        parts = [f"K{r['K']} {r['fn_with_detection_inside']}/{r['fn']}"
                 for r in lad["rungs"] if "fn" in r]
        change = lad["share_change_k1_to_top"]
        g1, gt = lad["join_gain_k1"], lad["join_gain_top_k"]
        add(f"| {name(lad['slug'])} | {'; '.join(parts)} | "
            f"{lad['share_k1']:.3f} → {lad['share_top_k']:.3f} "
            f"({change:+.3f}) | {g1['geometric-primary']:+.4f} → "
            f"{gt['geometric-primary']:+.4f}; {g1['geometric-contains']:+.4f} → "
            f"{gt['geometric-contains']:+.4f} |")
    add("")
    add("## Changelog")
    add("")
    add(f"### {date} — Original publication")
    add("")
    add("Written by the S166 K-ladder tile-join job from `summary.json`.")
    dst.write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
