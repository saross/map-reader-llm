#!/usr/bin/env python3
"""D64 plan P12: the confirmatory replication on image passes 4-6 (report only).

After the first D64 results (image passes 1-3, 2026-10-13), the PI approved
three more passes per image corner (runs 4-6, 2026-10-14; ruling D66 (4)).
Plan items P12 and P12.1 of ``reports/s164-agent-records/d64-a06-replication.md``
(commits ``e783ed3ac``, ``751525d7e``, ``2d5cb991c``, all before any pass 4-6
F1 was computed) fix a confirmatory test of the two borderline image
contrasts on passes 4-6 ALONE, its four-part criterion, its wording, and
the A-06 headline each verdict selects. This driver applies them exactly,
with the record's own driver (``d64_a06_replication.py``, imported as a
library) for scoring, contrasts, floors, and BH:

- Confirmatory (P12): C1 = image HIGH - MEDIUM at T 0.0 and C2 = image
  T 0.0 - T 0.7 at MEDIUM, on passes 4-6; D42 paired tile-swap
  permutation p (tiles in the bounds file's order, which is sorted, D63);
  BH across C1 and C2 only; criteria (a) sign as in passes 1-3,
  (b) BH-adjusted p < 0.05, (c) |delta| >= 0.03, (d) |delta| above the
  image replicate floor of passes 4-6 alone (K = 1, 12 pairs); the
  verdict, its approved wording, and the headline mapping.
- Secondary (P12, labelled as such): the pooled six-pass estimates of all
  eight contrasts (text keeps its five passes); the other image contrasts
  on passes 4-6; a day-effect check per image corner (passes 1-3 against
  4-6 as a K = 3 disjoint-subset difference, against the within-day K = 1
  floor); sensitivities dropping (i) the 15 real-time top-up tiles of
  2026-10-13 (as P7) and (ii) the wave-3 batch top-up tiles of 2026-10-15
  (they ran a day after their passes) from both arms of every affected
  contrast; thought tokens per image pass and corner from the merged metas.

Gates, before anything is reported: parameter control, coverage, and run
dates for all 24 image passes (and the original driver's gate for the text
passes); the 2026-10-15 top-up record agrees with every pass's
``recovery_history``; the aggregation identity against the A-06 helper on
every pool; and a replay showing that passes 1-3 reproduce the committed
2026-10-14 results (``out/d64_a06_results.json``) exactly.

It writes only under ``--out``; no model API is called.

Usage (repository root, on sapphire; one process, about ten minutes)::

    PYTHONHASHSEED=0 .venv/bin/python \\
        reports/s164-agent-records/d64-a06-replication-scripts/d64_p12_replication.py \\
        --out <dir>

Author: Shawn Ross & Claude (Anthropic), Session 164, 2026-10-15
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d64_a06_replication as drv  # noqa: E402  (also puts scripts/ on sys.path)
from lib_permutation import bh_adjust, paired_permutation_test  # noqa: E402
from n1_baseline_leaderboard_tiering import (  # noqa: E402
    TARGET_CRS,
    pass_averaged_per_tile,
)

REPO = drv.REPO
COMMITTED_OUT = HERE / "out" / "d64_a06_results.json"
TOPUP_1013 = REPO / drv.D64_DIR / "topup-2026-10-13.json"
TOPUP_1015 = REPO / drv.D64_DIR / "topup-2026-10-15.json"
THINKS, TEMPS, RULE = drv.THINKS, drv.TEMPS, drv.RULE

#: The two image waves and the UTC date each pass must have started on.
WAVES = {"passes 1-3": ("run_1", "run_2", "run_3"),
         "passes 4-6": ("run_4", "run_5", "run_6")}
WAVE_DATE = {"passes 1-3": "2026-10-13", "passes 4-6": "2026-10-14"}
P12_ALPHA = 0.05  # criterion (b): BH-adjusted p < 0.05 (strict, as P12 words it)
IMAGE_KEYS = [("image", t, tp) for t in THINKS for tp in TEMPS]

#: The confirmatory contrasts (P12): arms A and B, and where their passes 1-3
#: value sits in the committed results (section, row label).
CONFIRMATORY = {
    "C1": {"contrast": "image HIGH minus MEDIUM at T 0.0",
           "a": ("image", "high", "0.0"), "b": ("image", "medium", "0.0"),
           "passes_1_3": ("thinking", "image thinking at T 0.0")},
    "C2": {"contrast": "image T 0.0 minus T 0.7 at MEDIUM",
           "a": ("image", "medium", "0.0"), "b": ("image", "medium", "0.7"),
           "passes_1_3": ("factor_T", "image MEDIUM")},
}
#: The other image contrasts on passes 4-6 (secondary), with the corner gap.
OTHER_46 = {
    "image T 0.0 minus T 0.7 at HIGH": (("image", "high", "0.0"), ("image", "high", "0.7")),
    "image HIGH minus MEDIUM at T 0.7": (("image", "high", "0.7"), ("image", "medium", "0.7")),
    "image corner gap (HIGH T 0.0 minus MEDIUM T 0.7)": (("image", "high", "0.0"),
                                                        ("image", "medium", "0.7")),
}

#: P12.1's approved wording and headline mapping, verbatim.
WORDING = {
    "REPLICATES": "confirmed on three independent passes run the next day",
    "PARTLY": ("same direction on three further passes but not confirmed; the check "
               "had roughly even odds of passing even if the effect were as large as "
               "first seen"),
    "FAILS": "not replicated: the direction reversed on three further passes",
}
HEADLINE_A = "TEMPERATURE IS THE DRIVER"
HEADLINE_B = ("TEMPERATURE IS THE DRIVER IN TEXT; IN IMAGE THE MAIN DRIVER, WITH THE "
              "REQUESTED THINKING LEVEL ALSO MATTERING AT T=0.0 (D64 same-day replication)")
C2_FAILS_SUFFIX = "; IN IMAGE AT MEDIUM THINKING, NOT REPLICATED"


def corner_name(key: tuple[str, str, str]) -> str:
    """``("image", "high", "0.0")`` -> ``"image-high-t0.0"``."""
    return f"{key[0]}-{key[1]}-t{key[2]}"


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------

def gate_image_metas(tile_names: set[str]) -> dict:
    """Parameter control, coverage, run date, and thought tokens, 24 passes.

    Args:
        tile_names: The 487 bounds tiles.

    Returns:
        Per corner: one row per pass (wave, start time, thought tokens per
        request, top-up flag) and the corner's thought tokens per request
        for passes 1-3, 4-6, and 1-6.

    Raises:
        SystemExit: On any mismatch.
    """
    out, failures = {}, []
    for key in IMAGE_KEYS:
        corner = corner_name(key)
        pool = REPO / drv.D64_DIR / corner / drv.CONFIG["image"]
        metas = sorted(pool.glob("run_*/*.meta.json"))
        runs = [m.parent.name for m in metas]
        if runs != [f"run_{i}" for i in range(1, 7)]:
            failures.append(f"{corner}: runs {runs}")
        rows = []
        for meta_path in metas:
            meta = json.loads(meta_path.read_text())
            c, e, u = meta["configuration"], meta["execution_stats"], meta["usage_stats"]
            wave = next(w for w, r in WAVES.items() if meta_path.parent.name in r)
            checks = {
                "model": (c.get("model"), drv.MODEL),
                "temperature": (c.get("temperature"), float(key[2])),
                "thinking_level": (c.get("thinking_level"), key[1]),
                "version": (c.get("version"), drv.CONFIG["image"]),
                "items_processed": (e.get("items_processed"), 487),
                "items_failed": (e.get("items_failed"), 0),
                "service_tier": (meta.get("billing", {}).get("service_tier"), "batch"),
                "start date": (meta["timestamp"]["start"][:10], WAVE_DATE[wave]),
            }
            for name, (got, want) in checks.items():
                if got != want:
                    failures.append(f"{corner}/{meta_path.parent.name} {name}: {got} != {want}")
            tiles = json.loads(Path(str(meta_path).replace(".meta.json", ".tiles.json"))
                               .read_text())
            if set(tiles["completed"]) != tile_names or tiles["failed"]:
                failures.append(f"{corner}/{meta_path.parent.name}: coverage mismatch")
            n_resp = u.get("n_responses_with_usage") or 0
            if n_resp != 487:
                failures.append(f"{corner}/{meta_path.parent.name}: {n_resp} responses")
            thought = u.get("total_thoughts_tokens", 0)
            rows.append({
                "pass": str(meta_path.relative_to(REPO)), "wave": wave,
                "start_utc": meta["timestamp"]["start"],
                "n_responses_with_usage": n_resp, "total_thoughts_tokens": thought,
                "thought_tokens_per_request": round(thought / n_resp, 4) if n_resp else None,
                "total_detections": meta["results_summary"]["total_detections"],
                "topped_up": bool(meta.get("recovery_history")),
            })

        def per_request(sel: list[dict]) -> float:
            return round(sum(r["total_thoughts_tokens"] for r in sel)
                         / sum(r["n_responses_with_usage"] for r in sel), 4)

        out[corner] = {
            "passes": rows,
            "thought_tokens_per_request": {
                "passes 1-3": per_request([r for r in rows if r["wave"] == "passes 1-3"]),
                "passes 4-6": per_request([r for r in rows if r["wave"] == "passes 4-6"]),
                "passes 1-6": per_request(rows)},
            "thought_tokens_per_request_range": [
                min(r["thought_tokens_per_request"] for r in rows),
                max(r["thought_tokens_per_request"] for r in rows)],
        }
    if failures:
        sys.exit("IMAGE META GATE FAIL:\n  " + "\n  ".join(failures))
    return out


def gate_topup(metas: dict, tile_names: set[str]) -> dict:
    """The 2026-10-15 top-up record agrees with every pass's meta.

    Every topped-up pass recovered exactly its failed tiles; its meta's
    last ``recovery_history`` entry names the same tiles; the record's
    passes and untouched passes are the 12 wave-3 passes; no pass of
    runs 1-3 carries a recovery history.

    Returns:
        Per topped-up pass, its tiles and the top-up's own thought tokens;
        the distinct tile set; the counts.

    Raises:
        SystemExit: On any disagreement.
    """
    rec = json.loads(TOPUP_1015.read_text())
    failures, passes = [], {}
    wave3 = {f"{corner_name(k)}/{r}" for k in IMAGE_KEYS for r in WAVES["passes 4-6"]}
    if set(rec["passes"]) | set(rec["untouched"]) != wave3 or (
            set(rec["passes"]) & set(rec["untouched"])):
        failures.append("record's passes and untouched passes are not the 12 wave-3 passes")
    for name, p in sorted(rec["passes"].items()):
        corner, run = name.split("/")
        meta_path = next((REPO / drv.D64_DIR / corner / drv.CONFIG["image"] / run)
                         .glob("*.meta.json"))
        hist = json.loads(meta_path.read_text()).get("recovery_history") or []
        if (sorted(p["recovered"]) != sorted(p["failed_before"]) or p["still_failing"]
                or not p.get("merged")):
            failures.append(f"{name}: record not fully recovered and merged")
        if not hist or sorted(hist[-1]["recovered_ids"]) != sorted(p["failed_before"]):
            failures.append(f"{name}: meta recovery_history disagrees with the record")
        if not set(p["failed_before"]) <= tile_names:
            failures.append(f"{name}: tiles outside the bounds")
        usage = p.get("usage") or {}
        passes[name] = {"tiles": sorted(p["failed_before"]),
                        "n_tiles": len(p["failed_before"]),
                        "topup_thoughts_tokens": usage.get("total_thoughts_tokens"),
                        "topup_responses": usage.get("n_responses_with_usage")}
    for corner, block in metas.items():
        for row in block["passes"]:
            if row["wave"] == "passes 1-3" and row["topped_up"]:
                failures.append(f"{row['pass']}: a pass 1-3 carries a recovery history")
            run = Path(row["pass"]).parent.name
            if row["wave"] == "passes 4-6" and row["topped_up"] != (
                    f"{corner}/{run}" in rec["passes"]):
                failures.append(f"{row['pass']}: top-up flag disagrees with the record")
    n_instances = sum(v["n_tiles"] for v in passes.values())
    if n_instances != rec["totals"]["failed_before"]:
        failures.append(f"{n_instances} tile-pass instances against the record's "
                        f"{rec['totals']['failed_before']}")
    if failures:
        sys.exit("TOP-UP GATE FAIL:\n  " + "\n  ".join(failures))
    distinct = sorted({t for v in passes.values() for t in v["tiles"]})
    return {"passes": passes, "untouched": sorted(rec["untouched"]),
            "tile_pass_instances": n_instances, "distinct_tiles": distinct,
            "n_distinct_tiles": len(distinct)}


def canonical(obj: object) -> object:
    """Round-trip through JSON as the original driver writes it."""
    return json.loads(json.dumps(obj, default=str))


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def relabel(rows: list[dict], offset: int) -> list[dict]:
    """Shift ``floor_pairs`` subset labels from slice positions to pass numbers."""
    return [{**r, "subset_a": [i + offset for i in r["subset_a"]],
             "subset_b": [i + offset for i in r["subset_b"]]} for r in rows]


def wave_floor(stacks: dict, wave: str, mask: np.ndarray | None) -> dict:
    """The image K = 1 floor of one wave (4 corners x 3 pairs = 12 pairs).

    Args:
        stacks: Six-pass image stacks keyed (modality, think, temp).
        wave: ``"passes 1-3"`` or ``"passes 4-6"``.
        mask: Tile mask or None.

    Returns:
        The pooled summary (``p95`` is the floor), per-corner summaries, and
        the pair rows labelled with true pass numbers.
    """
    lo = 0 if wave == "passes 1-3" else 3
    per_corner, flat = {}, []
    for key in IMAGE_KEYS:
        rows = relabel(drv.floor_pairs(stacks[key][lo:lo + 3], 1, mask), lo)
        per_corner[corner_name(key)] = drv.summarise_floor(rows)
        flat += [{"corner": corner_name(key), "k": 1, **r} for r in rows]
    return {"pooled": drv.summarise_floor(flat), "per_corner": per_corner, "rows": flat}


def criteria(row: dict, sign_1_3: float, p_bh: float, floor: float) -> dict:
    """P12's four criteria and the verdict for one confirmatory contrast.

    Args:
        row: The contrast row (``drv.contrast``) on passes 4-6.
        sign_1_3: The contrast's passes 1-3 delta (its sign is the target).
        p_bh: The BH-adjusted p across C1 and C2.
        floor: The image K = 1 floor of passes 4-6.

    Returns:
        Each criterion's value and pass/fail, the verdict, and its wording.
    """
    d = row["delta (pass-averaged micro)"]
    c = {
        "a_sign_matches_passes_1_3": {"delta_4_6": d, "delta_1_3": sign_1_3,
                                      "met": bool(np.sign(d) == np.sign(sign_1_3) and d != 0)},
        "b_bh_adjusted_p_below_0.05": {"p_bh_adjusted": p_bh, "met": bool(p_bh < P12_ALPHA)},
        "c_abs_delta_at_least_0.03": {"abs_delta": round(abs(d), 6),
                                      "met": bool(abs(d) >= RULE)},
        "d_abs_delta_above_floor_4_6": {"abs_delta": round(abs(d), 6), "floor": floor,
                                        "met": bool(abs(d) > floor)},
    }
    met = [v["met"] for v in c.values()]
    if not c["a_sign_matches_passes_1_3"]["met"]:
        verdict = "FAILS"
    elif all(met):
        verdict = "REPLICATES"
    else:
        verdict = "PARTLY"
    failed = [k for k, v in c.items() if not v["met"]]
    return {"criteria": c, "criteria_failed": failed, "verdict": verdict,
            "wording": WORDING[verdict]}


def confirmatory(stacks: dict, ref_1_3: dict, mask: np.ndarray | None) -> dict:
    """C1 and C2 on passes 4-6, BH across the two, criteria, verdicts.

    Args:
        stacks: Six-pass image stacks.
        ref_1_3: Passes 1-3 deltas keyed "C1", "C2".
        mask: Tile mask or None (all 487 tiles).

    Returns:
        The floor of passes 4-6, both contrast rows with their criteria,
        the BH family, and the headline the P12.1 mapping selects.
    """
    floor = wave_floor(stacks, "passes 4-6", mask)
    f = floor["pooled"]["p95"]
    rows = {}
    for cid, spec in CONFIRMATORY.items():
        row = drv.contrast(stacks[spec["a"]][3:6], stacks[spec["b"]][3:6], mask)
        row["contrast"] = spec["contrast"]
        row["per_pass_f1_a"] = drv.corner_estimates(stacks[spec["a"]][3:6], mask)["per_pass_f1"]
        row["per_pass_f1_b"] = drv.corner_estimates(stacks[spec["b"]][3:6], mask)["per_pass_f1"]
        row["floor_verdict (P6 three-valued, K = 1, n = 3)"] = drv.floor_verdict(
            row["delta (pass-averaged micro)"], f, 1, 3)
        rows[cid] = row
    raw = [float(rows[c]["delta_bootstrap"]["p_value"]) for c in CONFIRMATORY]
    adj = [round(p, 6) for p in bh_adjust(raw)]
    for cid, p in zip(CONFIRMATORY, adj):
        rows[cid]["p_bh_adjusted (C1 and C2)"] = p
        rows[cid].update(criteria(rows[cid], ref_1_3[cid], p, f))
        # The second estimator, as P3 reports it; criteria use pass-averaged.
        d2 = rows[cid]["delta (mean of per-pass F1)"]
        rows[cid]["mean_of_per_pass_reading"] = {
            "sign": bool(np.sign(d2) == np.sign(ref_1_3[cid])),
            "abs_at_least_0.03": bool(abs(d2) >= RULE), "above_floor": bool(abs(d2) > f)}
    headline = HEADLINE_B if rows["C1"]["verdict"] == "REPLICATES" else HEADLINE_A
    if rows["C2"]["verdict"] == "FAILS":
        headline += C2_FAILS_SUFFIX
    return {"floor_passes_4_6": {k: v for k, v in floor.items() if k != "rows"},
            "floor_rows": floor["rows"], "C1": rows["C1"], "C2": rows["C2"],
            "bh": {"family": list(CONFIRMATORY), "p_permutation": dict(zip(CONFIRMATORY, raw)),
                   "p_bh_adjusted": dict(zip(CONFIRMATORY, adj))},
            "headline_selected": headline,
            "headline_rule": "P12.1: C1 REPLICATES -> (b); PARTLY or FAILS -> (a); "
                             "C2 FAILS adds the suffix"}


def other_46(stacks: dict, mask: np.ndarray | None, floor: float) -> dict:
    """The other image contrasts and the corner gap on passes 4-6 (no family)."""
    out = {}
    for label, (ka, kb) in OTHER_46.items():
        row = drv.contrast(stacks[ka][3:6], stacks[kb][3:6], mask)
        row["contrast"] = label
        row["floor_verdict (K = 1, n = 3, floor of passes 4-6)"] = drv.floor_verdict(
            row["delta (pass-averaged micro)"], floor, 1, 3)
        row["_note"] = "secondary; raw permutation p, in no BH family"
        out[label] = row
    return out


def day_effect(stacks: dict, mask: np.ndarray | None) -> dict:
    """Per image corner, passes 4-6 minus passes 1-3 (a K = 3 split).

    The difference is set against the within-day K = 1 floor (the 24
    replicate pairs inside the two days) with P6's three-valued verdict
    (``floor_verdict`` with k = 1, n = 3), and each single day's floor is
    shown beside it. The day split's rank among the corner's ten disjoint
    3-vs-3 splits is reported: with no day effect the day split is one of
    ten exchangeable splits.
    """
    f13, f46 = wave_floor(stacks, "passes 1-3", mask), wave_floor(stacks, "passes 4-6", mask)
    within = drv.summarise_floor(f13["rows"] + f46["rows"])
    corners, k3_rows = {}, []
    for key in IMAGE_KEYS:
        s = stacks[key] if mask is None else stacks[key][:, :, mask]
        a, b = drv.pass_mean(s[0:3]), drv.pass_mean(s[3:6])
        f_a = drv.micro_f1(*(float(x) for x in a.sum(axis=1)))
        f_b = drv.micro_f1(*(float(x) for x in b.sum(axis=1)))
        perm = paired_permutation_test({"tp": b[0], "fp": b[1], "fn": b[2]},
                                       {"tp": a[0], "fp": a[1], "fn": a[2]})
        splits = drv.floor_pairs(stacks[key], 3, mask)
        k3_rows += [{"corner": corner_name(key), "k": 3, **r} for r in splits]
        day = next(r for r in splits if r["subset_a"] == [1, 2, 3])
        rank = 1 + sum(r["abs_delta"] > day["abs_delta"] for r in splits)
        delta = round(f_b - f_a, 6)
        corners[corner_name(key)] = {
            "f1_passes_1_3": round(f_a, 6), "f1_passes_4_6": round(f_b, 6),
            "delta (4-6 minus 1-3)": delta, "abs_delta": round(abs(delta), 6),
            "p_tile_swap": perm["metrics"]["f1"]["p_value"],
            "n_discordant_tiles": perm["n_discordant_tiles"],
            "verdict_vs_within_day_floor": drv.floor_verdict(delta, within["p95"], 1, 3),
            "exceeds_floor_1_3": bool(abs(delta) > f13["pooled"]["p95"]),
            "exceeds_floor_4_6": bool(abs(delta) > f46["pooled"]["p95"]),
            "day_split_rank_of_10": rank,
        }
    return {"within_day_floor_k1": within, "floor_passes_1_3": f13["pooled"],
            "floor_passes_4_6": f46["pooled"], "corners": corners,
            "k3_split_rows": k3_rows}


def strip_rows(floors: dict) -> dict:
    """Drop the per-pair rows (they go to the CSV) from a build_floors block."""
    return {m: {k: v for k, v in f.items() if k != "corner_rows"} for m, f in floors.items()}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Run the gates, the confirmatory test, and the secondary analyses."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    gdf_ref = gpd.read_file(drv.GROUND_TRUTH).to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file(drv.BOUNDS).to_crs(TARGET_CRS)
    tile_order = list(gdf_bounds["tile_name"].unique())
    if len(tile_order) != 487 or tile_order != sorted(tile_order):
        sys.exit("GATE FAIL: the bounds tiles are not 487 in sorted order (D63)")
    tile_names = set(tile_order)

    print("Gate: text passes and image runs 1-3 (the original driver's gate) ...", flush=True)
    drv.gate_metas(tile_names)
    print("Gate: all 24 image passes ...", flush=True)
    metas = gate_image_metas(tile_names)
    print("Gate: the 2026-10-15 top-up record ...", flush=True)
    topup = gate_topup(metas, tile_names)

    print("Scoring every pass ...", flush=True)
    stacks, files, identity = {}, {}, {}
    for modality in ("text", "image"):
        for think in THINKS:
            for temp in TEMPS:
                key = (modality, think, temp)
                pool = drv.D64_DIR / corner_name(key) / drv.CONFIG[modality]
                files[corner_name(key)], stack = drv.score_pool(
                    pool, gdf_ref, gdf_bounds, tile_order)
                want = 5 if modality == "text" else 6
                runs = [Path(f).parent.name for f in files[corner_name(key)]]
                if runs != [f"run_{i}" for i in range(1, want + 1)]:
                    sys.exit(f"GATE FAIL: {corner_name(key)} passes {runs}")
                tp, fp, fn, n = pass_averaged_per_tile(pool, gdf_ref, gdf_bounds, tile_order)
                ours = drv.pass_mean(stack)
                identity[corner_name(key)] = bool(
                    n == stack.shape[0] and np.array_equal(ours[0], tp)
                    and np.array_equal(ours[1], fp) and np.array_equal(ours[2], fn))
                if not identity[corner_name(key)]:
                    sys.exit(f"AGGREGATION-IDENTITY GATE FAIL: {corner_name(key)}")
                stacks[key] = stack

    print("Gate: passes 1-3 reproduce the committed 2026-10-14 results ...", flush=True)
    s13 = {k: (v if k[0] == "text" else v[0:3]) for k, v in stacks.items()}
    floors13, _ = drv.build_floors(s13, None)
    main13 = drv.analyse(s13, floors13, None, None)
    committed = json.loads(COMMITTED_OUT.read_text())
    replay = {
        "main": canonical(main13) == committed["main"],
        "floors": canonical(strip_rows(floors13)) == committed["floors"],
        "corners": all(canonical(drv.corner_estimates(s13[k])) == committed["corners"][
            corner_name(k)] for k in s13),
    }
    if not all(replay.values()):
        sys.exit(f"PASSES 1-3 REPLAY GATE FAIL: {replay}")
    ref_1_3 = {cid: main13[spec["passes_1_3"][0]][spec["passes_1_3"][1]][
        "delta (pass-averaged micro)"] for cid, spec in CONFIRMATORY.items()}

    corners = {}
    for key, stack in stacks.items():
        if key[0] == "text":
            corners[corner_name(key)] = {"passes 1-5": drv.corner_estimates(stack)}
        else:
            corners[corner_name(key)] = {
                "passes 1-3": drv.corner_estimates(stack[0:3]),
                "passes 4-6": drv.corner_estimates(stack[3:6]),
                "passes 1-6": drv.corner_estimates(stack)}

    print("Confirmatory: C1 and C2 on passes 4-6 ...", flush=True)
    conf = confirmatory(stacks, ref_1_3, None)
    floor46 = conf["floor_passes_4_6"]["pooled"]["p95"]
    others = other_46(stacks, None, floor46)

    print("Secondary: pooled six-pass estimates ...", flush=True)
    floors6, flat6 = drv.build_floors(stacks, None)
    pooled = drv.analyse(stacks, floors6, None, None)

    print("Secondary: day effect ...", flush=True)
    day = day_effect(stacks, None)

    print("Secondary: sensitivity (i), the 15 real-time tiles of 2026-10-13 ...", flush=True)
    rt = json.loads(TOPUP_1013.read_text())
    drop_rt = sorted({t for u in rt["units"] for t in u["failed_before"]})
    mask_rt = np.array([t not in set(drop_rt) for t in tile_order])
    affected_text = {"text HIGH", "text thinking at T 0.0", "text thinking at T 0.7",
                     "text corner gap"}
    floors_rt, flat_rt = drv.build_floors(stacks, mask_rt, ("text",))
    pooled_rt = drv.analyse(stacks, floors6, mask_rt, affected_text, floors_rt)

    print("Secondary: sensitivity (ii), the wave-3 batch top-up tiles ...", flush=True)
    drop_w3 = topup["distinct_tiles"]
    mask_w3 = np.array([t not in set(drop_w3) for t in tile_order])
    conf_w3 = confirmatory(stacks, ref_1_3, mask_w3)
    others_w3 = other_46(stacks, mask_w3, conf_w3["floor_passes_4_6"]["pooled"]["p95"])
    affected_image = {"image HIGH", "image MEDIUM", "image thinking at T 0.0",
                      "image thinking at T 0.7", "image corner gap"}
    floors_w3, flat_w3 = drv.build_floors(stacks, mask_w3, ("image",))
    pooled_w3 = drv.analyse(stacks, floors6, mask_w3, affected_image, floors_w3)
    day_w3 = day_effect(stacks, mask_w3)

    def pair_rows(label: str, n_tiles: int, rows: list[dict]) -> list[dict]:
        return [{"set": label, "tiles": n_tiles, **r} for r in rows]

    n_w3 = int(mask_w3.sum())
    csv_rows = (pair_rows("image passes 4-6 (confirmatory floor)", 487, conf["floor_rows"])
                + pair_rows("image passes 4-6 (confirmatory floor)", n_w3,
                            conf_w3["floor_rows"])
                + pair_rows("pooled (text 1-5, image 1-6)", 487, flat6)
                + pair_rows("pooled, text without the 15 real-time tiles",
                            int(mask_rt.sum()), flat_rt)
                + pair_rows("pooled, image without the wave-3 top-up tiles", n_w3, flat_w3)
                + pair_rows("day effect: image 3-vs-3 splits", 487, day["k3_split_rows"])
                + pair_rows("day effect: image 3-vs-3 splits", n_w3, day_w3["k3_split_rows"]))
    for d in (day, day_w3):
        d.pop("k3_split_rows")
    for c in (conf, conf_w3):
        c.pop("floor_rows")

    doc = {
        "_README": ("D64 plan P12: the confirmatory replication of the two borderline "
                    "image contrasts on passes 4-6, with the secondary analyses (report "
                    "only; plan reports/s164-agent-records/d64-a06-replication.md P12 and "
                    "P12.1, commits e783ed3ac, 751525d7e, 2d5cb991c)."),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": drv.git_head(),
        "settings": {"buffer_m": drv.BUFFER_M, "bootstrap_B": drv.B_DELTA_CI,
                     "seed": drv.SEED, "permutations": 10_000, "rule": RULE,
                     "criterion_b": "BH-adjusted p < 0.05 across C1 and C2 only",
                     "tiles": len(tile_order), "tile_order": "bounds file order (sorted)",
                     "scorer": "lib_advanced_metrics.compute_per_tile_tp_fp_fn (D50, main)"},
        "gates": {"text_and_image_runs_1_3_metas": "pass (original driver's gate)",
                  "image_metas_24_passes": "pass (model, temperature, thinking level, "
                  "configuration, 487 processed, 0 failed, batch tier, start date, "
                  "coverage, 487 responses with usage)",
                  "topup_2026_10_15_record": "pass", "aggregation_identity": identity,
                  "passes_1_3_replay_against_committed": replay},
        "pass_files": files,
        "thought_tokens_image": metas,
        "topup_2026_10_15": {k: v for k, v in topup.items() if k != "distinct_tiles"},
        "corners": corners,
        "confirmatory": {"passes_1_3_deltas": ref_1_3, **conf},
        "secondary": {
            "_note": ("Secondary, labelled as such (P12). The pooled six-pass extension "
                      "was data-dependent (passes 4-6 were added partly because C1 and C2 "
                      "looked borderline), so the pooled p values are not used for C1 or "
                      "C2."),
            "other_image_contrasts_passes_4_6": others,
            "pooled_six_pass": {"floors": strip_rows(floors6), **pooled},
            "day_effect": day,
            "sensitivity_realtime_15": {
                "dropped_tiles": drop_rt, "n_dropped": len(drop_rt),
                "applies_to": sorted(affected_text),
                "confirmatory": "unchanged by construction (no text corner in C1 or C2)",
                "pooled_six_pass": {"floors_text": strip_rows(floors_rt)["text"],
                                    **pooled_rt}},
            "sensitivity_wave3_topup": {
                "dropped_tiles": drop_w3, "n_dropped": len(drop_w3), "n_tiles_left": n_w3,
                "confirmatory": conf_w3, "other_image_contrasts_passes_4_6": others_w3,
                "pooled_six_pass": {"applies_to": sorted(affected_image),
                                    "floors_image": strip_rows(floors_w3)["image"],
                                    **pooled_w3},
                "day_effect": day_w3},
        },
    }
    (args.out / "d64_p12_results.json").write_text(
        json.dumps(doc, indent=1, sort_keys=False, default=str) + "\n")
    with open(args.out / "p12_floor_pairs.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0]))
        w.writeheader()
        for r in csv_rows:
            w.writerow({k: json.dumps(v) if isinstance(v, list) else v for k, v in r.items()})
    np.savez_compressed(args.out / "d64_p12_per_pass_counts.npz",
                        tile_order=np.array(tile_order),
                        **{corner_name(k): v for k, v in stacks.items()})
    print(f"C1 {conf['C1']['verdict']}, C2 {conf['C2']['verdict']}; "
          f"headline: {conf['headline_selected']}", flush=True)
    print(f"Wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
