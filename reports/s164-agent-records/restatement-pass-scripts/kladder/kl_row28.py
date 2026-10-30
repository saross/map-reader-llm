#!/usr/bin/env python3
"""
kl_row28.py -- S164 restatement pass, K-ladder lane: the dated fix of
``results/k-ladder-2026-09-12/phase2/operating-points.json`` row 28.

Purpose:
    Row 28 (Gemini 3.7 text, GS B geometry, K = 3) still names the verifier
    stage and union count from before the recovery-fragment fix
    (``75d7c8d4c``), as the findings' changelog of 2026-10-07 recorded. The
    live cell (``phase2/cells/gemini37-screen-2026-08-28__g37-text-k3-verified-
    opmax``) scores the 495-feature set that ``verify_k3_recovery-fixed`` over
    the rebuilt 759-candidate ``consensus-n3`` gives at (3, 0.10). This writes
    the row with the live cell's facts and a dated ``_note``; every other byte
    of the file is unchanged (``json.dumps(indent=2)`` + newline reproduces the
    committed file exactly, checked first).

Usage:
    python kl_row28.py <committed operating-points.json> <candidate output>

Author: Claude (Opus 5.5) for Shawn Ross, S164 restatement pass, 2026-10-15.
"""
import json
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text()
doc = json.loads(text)
assert json.dumps(doc, indent=2) + "\n" == text, "formatting would not round-trip"
row = next(r for r in doc["rungs"] if r["row"] == 28)
assert (row["pool_slug"], row["n_passes"], row["candidates"]) == ("g384_ov192_g37", 3, 757)
assert row["opmax"]["n_detections"] == 494 and row["carried"]["n_detections"] == 494
VR = "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37"
row["verifier_stage"] = "g384_ov192_g37-union-k3-verify-recovery-fixed"
row["verify_dir"] = f"{VR}/verify_k3_recovery-fixed"
row["candidates"] = 759
for point in (row["opmax"], row["carried"]):
    point["n_detections"] = 495
row["sweep_board_frame"] = f"{VR}/verify_k3_recovery-fixed/sweep_2d_era2b.json"
row["sweep_era2_frame"] = f"{VR}/verify_k3_recovery-fixed/sweep_2d.json"
# The committed sweeps of the recovery-fixed stage (f8e0eb600, 2026-09-13) give
# (3, 0.10) as the argmax on both frames: F1@20 0.886, n 495 (pre-D50 scorer).
for key in ("opmax", "opmax_on_era2_frame"):
    row[key]["sweep_f1_20"] = 0.886
    row[key]["sweep_n"] = 495
row["_note"] = (
    "DATED FIX 2026-10-15 (S164 restatement pass, reports/s164-agent-records/"
    "restatement-pass.md § 1.4; recorded as stale in results/k-ladder-2026-09-12/"
    "findings.md, changelog 2026-10-07): the live cell scores the recovery-fixed "
    "stage (manipulation-gate binding g37-kladder-k3-verify-k3-recovery-fixed: "
    "verify_k3_recovery-fixed over the rebuilt 759-candidate consensus-n3, fix "
    "75d7c8d4c), whose (3, 0.10) set holds 495 features. verifier_stage, verify_dir, "
    "the two sweep paths, candidates (757 -> 759), sweep_f1_20 (0.887 -> 0.886) and "
    "sweep_n and n_detections (494 -> 495) now name it; the sweep figures are that "
    "stage's committed sweeps (f8e0eb600, 2026-09-13, pre-D50 scorer), whose argmax "
    "on both frames is the same point (3, 0.10). Today's board-frame sweep of the "
    "stage (D50 scorer) gives F1@20 0.9135 at (3, 0.10), n 495, still the argmax, "
    "unclipped and clipped to the D51 common area (0.9073). The spend "
    "ledger keys this row by row number (row28-g384_ov192_g37-union-k3-verify), so "
    "its verifier cost is unchanged.")
dst.write_text(json.dumps(doc, indent=2) + "\n")
print("written", dst)
