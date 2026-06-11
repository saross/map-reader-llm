#!/usr/bin/env python3
# ============================================================================
# measure_miss_correlation_gs.py
# ----------------------------------------------------------------------------
# Session 112 ($0): measure the STUDENT x SYSTEM miss correlation on the
# 4 GS sheets — the empirical upgrade to the GT-epistemics bound (Shawn,
# 2026-06-11). The 55-map canonical GT cannot contain mounds missed by BOTH
# students and the machine (the "double-miss" blind spot), so reported
# recall is an upper bound. The GS sheets hold an adjudicated curator GT
# plus the student data plus production system detections — so the
# double-miss rate and its deviation from independence are directly
# measurable there, and transfer to the 55-map bound as a correlation
# factor.
#
# METHOD: restrict curator mounds (truth) to the Era-2 487-tile evaluation
# bounds (the system only saw those tiles). Label each mound:
#   student-found  — Hungarian match to student-mounds-gs-4maps-reviewed
#                    at 50 m (the project-canonical student-jitter radius,
#                    cf. analyse_student_gt_fn_rate_gs4.py)
#   system-found   — Hungarian match to the production headline detection
#                    set (pv-diag-384 verified-adv-text-consensus-16of30,
#                    412 detections) at 20 m canonical (+ 30/50 m
#                    sensitivity)
# Then the 2x2 found/miss table, Fisher exact, odds ratio, observed
# double-miss vs the independence expectation, and the implied 55-map
# recall-inflation bound: P(neither finds) = c x ms x mm where c is the
# measured correlation ratio; recall inflation factor = 1/(1 - P(neither)).
#
# Usage (zbook):  .venv/bin/python scripts/measure_miss_correlation_gs.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
from scipy.stats import fisher_exact

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.lib_advanced_metrics import match_detections_to_references  # noqa: E402

CURATOR = BASE_DIR / "inputs/vectors/references/mounds-reference.geojson"
STUDENTS = BASE_DIR / "inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson"
SYSTEM = (BASE_DIR / "outputs/era1-pv-stage-d/384-consensus-text-high"
          / "pass_1/accepted_t0.2.geojson")
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUT = BASE_DIR / "results/working-precision/gs-miss-correlation.json"
STUDENT_RADIUS = 50.0
SYSTEM_RADII = [20.0, 30.0, 50.0]

# 55-map transfer inputs (anchored): student FN rate from the GS-4
# confusion analysis (9.1 % cumulative; convergent 9-11 % with the 55-map
# estimate) and the oracle's recall@50 vs the canonical GT.
MS_55 = 0.091
ORACLE_EVAL = BASE_DIR / "results/55maps-extended-gt-2026-06-07/T03-k3/evaluation.json"


def to_32635(path: Path) -> gpd.GeoDataFrame:
    """Read a geojson, magnitude-detect undeclared CRS, return EPSG:32635."""
    g = gpd.read_file(path)
    if g.crs is None:
        g = g.set_crs("EPSG:32635" if abs(g.geometry.x.iloc[0]) > 180 else "EPSG:4326")
    return g.to_crs("EPSG:32635")


def matched_flags(gdf_ref: gpd.GeoDataFrame, gdf_det: gpd.GeoDataFrame,
                  radius: float) -> list[bool]:
    """Per-reference matched/unmatched flags via the canonical Hungarian matcher."""
    _, matched_ref, _, _ = match_detections_to_references(
        list(gdf_det.geometry), list(gdf_ref.geometry), max_distance=radius)
    hit = set(matched_ref)
    return [i in hit for i in range(len(gdf_ref))]


def main() -> int:
    """Compute the 2x2 miss table at each system radius and the 55-map bound."""
    bounds = to_32635(BOUNDS)
    area = bounds.union_all()
    curator = to_32635(CURATOR)
    curator = curator[curator.geometry.within(area)].reset_index(drop=True)
    students = to_32635(STUDENTS)
    system = to_32635(SYSTEM)
    print(f"curator mounds in eval bounds: {len(curator)} | students {len(students)} "
          f"| system detections {len(system)}", flush=True)

    s_found = matched_flags(curator, students, STUDENT_RADIUS)
    ms = 1 - sum(s_found) / len(curator)
    print(f"student miss rate @ {STUDENT_RADIUS:.0f} m: {ms:.3f} "
          f"(prior whole-sheet derivation: 0.091)", flush=True)

    out = {"n_curator_in_bounds": len(curator), "student_radius_m": STUDENT_RADIUS,
           "student_miss_rate": round(ms, 4), "system": str(SYSTEM.relative_to(BASE_DIR)),
           "by_system_radius": []}
    o_rec = json.loads(ORACLE_EVAL.read_text())["summary"]
    mm55 = 1 - next(b for b in o_rec["buffers"] if b["buffer_metres"] == 50)["recall"]

    for r in SYSTEM_RADII:
        sys_found = matched_flags(curator, system, r)
        a = sum(s and y for s, y in zip(s_found, sys_found))   # both found
        b = sum(s and not y for s, y in zip(s_found, sys_found))  # students only
        c = sum((not s) and y for s, y in zip(s_found, sys_found))  # system only
        d = sum((not s) and (not y) for s, y in zip(s_found, sys_found))  # both miss
        n = len(curator)
        mm = (b + d) / n
        dm_obs = d / n
        dm_ind = ms * mm
        ratio = dm_obs / dm_ind if dm_ind else float("inf")
        odds, p = fisher_exact([[a, b], [c, d]])
        # transfer: P(neither) on the 55 maps with the measured ratio
        p_neither_55 = min(ratio * MS_55 * mm55, 0.5)
        inflation = 1 / (1 - p_neither_55)
        row = {"system_radius_m": r, "both_found": a, "students_only": b,
               "system_only": c, "both_miss": d,
               "system_miss_rate": round(mm, 4),
               "double_miss_observed": round(dm_obs, 4),
               "double_miss_independence": round(dm_ind, 4),
               "correlation_ratio": round(ratio, 2),
               "fisher_odds": round(float(odds), 2), "fisher_p": float(f"{p:.2e}"),
               "implied_55map_p_neither": round(p_neither_55, 4),
               "implied_55map_recall_inflation_factor": round(inflation, 4)}
        out["by_system_radius"].append(row)
        print(f"\nsystem radius {r:.0f} m: both {a} | students-only {b} | "
              f"system-only {c} | both-miss {d}", flush=True)
        print(f"  system miss {mm:.3f}; double-miss obs {dm_obs:.4f} vs "
              f"independence {dm_ind:.4f} -> ratio {ratio:.2f} "
              f"(Fisher OR {odds:.2f}, p={p:.2e})", flush=True)
        print(f"  implied 55-map P(neither) = {p_neither_55:.4f} -> reported "
              f"recall inflated by ~{(inflation - 1) * 100:.1f}%", flush=True)

    out["transfer_inputs"] = {"ms_55": MS_55, "mm_55_oracle_at_50m": round(mm55, 4)}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nWrote {OUT.relative_to(BASE_DIR)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
