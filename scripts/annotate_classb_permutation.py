#!/usr/bin/env python3
"""
Annotate D42's class B artefacts with their permutation re-test (D43, D44).

Why this script exists
----------------------
PI ruling D42 retired every bootstrap p-value. Class B is the set of March
pairwise artefacts W2 could not re-test because their inputs had moved
(`reports/d42-implementation-2026-10-05.md` § 6). Their inputs were found
(`reports/d42-implementation-2026-10-05-scripts/moved-inputs.md`) and the
producers were re-run on sapphire with the D42 code, into scratch; the
re-run outputs are kept under `results/d42-retest-2026-10-05/class-b/`.

Re-running moves the confidence intervals as well as the p-values (the CI
method became BCa in April, and the March tile order followed the hash
seed), so, as with the retest files, the committed artefacts are ANNOTATED,
not replaced: each comparison gains a `permutation_retest` block, and the
bootstrap fields stay as published. Two PI rulings shape the special cases:

* **D43 (B-17)**: the record re-tests the March pairing as it ran (today's
  minimal-verifier file at threshold 0.20); a re-sweep of that file is
  added beside it as a labelled sensitivity, and the stale variant summary
  (F1 0.774, n 397, from an overwritten file) is flagged.
* **D44 (I4)**: the record uses the March 512 px sweep (threshold 0.20); the
  E39 sweep (threshold 0.15, the figure to cite) is added beside it.

`pairwise-384px.json` (B-16) cannot be re-tested: the current per-tile
scorer refuses its 512 px detections on the 384 px frame (their tile names
are the other frame's), which is the defect its March tables carried
silently. It gets a note instead.

Before writing, every annotated row's point estimates are checked against
the re-run (detections and F1 must match), so a row is never annotated with
a test of different data.

Usage::

    python scripts/annotate_classb_permutation.py          # dry run
    python scripts/annotate_classb_permutation.py --write

Created: 2026-10-06 (Session 161, D43/D44)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RE = ROOT / "results/d42-retest-2026-10-05/class-b"
PW = ROOT / "results/h11-384-pv-diagnostic/pairwise"
METHOD = "paired tile-swap permutation, 10,000, seed 42 (D42); re-run 2026-10-06"
NOTE = ("PI ruling D42: the p_value fields inside f1/precision/recall_difference "
        "are the RETIRED bootstrap values (2 x minority tail, floor 1/B), kept as "
        "published; the authoritative test is each comparison's permutation_retest "
        "block. Bootstrap CIs stay as published (a re-run would move them: BCa "
        "since April). Re-run outputs: results/d42-retest-2026-10-05/class-b/; "
        "report: reports/d42-implementation-2026-10-05.md.")


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def block(result: dict, source: str) -> dict:
    """The permutation_retest block from a re-run result dict."""
    out = {"f1_p": result["f1_difference"]["p_value"],
           "precision_p": result["precision_difference"]["p_value"],
           "recall_p": result["recall_difference"]["p_value"],
           "method": METHOD, "source": source}
    perm = result.get("permutation") or {}
    if "n_discordant_tiles" in perm:
        out["n_discordant_tiles"] = perm["n_discordant_tiles"]
    return out


def check(label: str, a: dict, b: dict, keys: tuple[str, ...]) -> None:
    for k in keys:
        if a.get(k) != b.get(k):
            raise SystemExit(f"{label}: {k} differs (committed {a.get(k)} vs re-run {b.get(k)}); "
                             "not annotating a test of different data")


def fair_384(data: dict) -> list[str]:
    march = load(RE / "fair-384-vs-512-march-sweep.json")
    e39 = load(RE / "fair-384-vs-512-e39-sweep.json")
    log = []
    for key, row in data.items():
        m = march[key]
        check(f"fair {key}", row, m, ("f1_384", "f1_512", "det_384", "det_512_raw", "det_512_clipped"))
        row["result"]["permutation_retest"] = block(
            m["result"], "results/d42-retest-2026-10-05/class-b/fair-384-vs-512-march-sweep.json")
        log.append(f"{key}: F1 p {row['result']['f1_difference']['p_value']} -> "
                   f"{m['result']['f1_difference']['p_value']}")
    e = e39["I4:deterministic"]
    data["I4:deterministic"]["current_e39_sweep"] = {
        "_note": ("D44: the figure to cite. The March 512 px sweep (step 0.1) had no 0.15 row and "
                  "pinned the 512 px threshold at 0.20; E39 (01c84b841) re-swept on the common "
                  "0.05 grid, whose optimum is 0.15."),
        "f1_512": e["f1_512"], "det_512_raw": e["det_512_raw"],
        "det_512_clipped": e["det_512_clipped"],
        "f1_difference_bootstrap_mean": e["result"]["f1_difference"]["mean"],
        "f1_ci": [e["result"]["f1_difference"]["ci_lower"], e["result"]["f1_difference"]["ci_upper"]],
        "permutation_retest": block(e["result"],
                                    "results/d42-retest-2026-10-05/class-b/fair-384-vs-512-e39-sweep.json"),
    }
    log.append(f"I4 (E39 sweep): f1_512 {e['f1_512']}, F1 p {e['result']['f1_difference']['p_value']}")
    return log


def pes(data: dict, rerun: str, twins: dict[str, str]) -> list[str]:
    r = load(RE / rerun)["comparisons"]
    log, flips = [], 0
    for key, row in data["comparisons"].items():
        src = twins.get(key, key)
        rr = r[src]
        row["permutation_retest"] = block(rr, f"results/d42-retest-2026-10-05/class-b/{rerun}")
        if src != key:
            row["permutation_retest"]["_note"] = f"duplicate of {src} (same arms); its re-test"
        old, new = row["f1_difference"]["p_value"], rr["f1_difference"]["p_value"]
        if (old < 0.05) != (new < 0.05):
            flips += 1
            log.append(f"  raw-alpha flip: {key} F1 p {old} -> {new}")
    log.insert(0, f"{len(data['comparisons'])} rows annotated; raw-alpha F1 flips: {flips}")
    return log


def p3a(data: dict) -> list[str]:
    r = {c["comparison"]: c for c in load(RE / "phase3a-high-text-pairwise.json")["comparisons"]}
    log = []
    for row in data["comparisons"]:
        rr = r[row["comparison"]]
        check(f"p3a {row['comparison']}", row["point_estimates_a"], rr["point_estimates_a"],
              ("f1", "n_detections"))
        check(f"p3a {row['comparison']}", row["point_estimates_b"], rr["point_estimates_b"],
              ("f1", "n_detections"))
        row["permutation_retest"] = block(
            rr["effect_size"], "results/d42-retest-2026-10-05/class-b/phase3a-high-text-pairwise.json")
        log.append(f"{row['comparison']}: F1 p {row['effect_size']['f1_difference']['p_value']} -> "
                   f"{rr['effect_size']['f1_difference']['p_value']}")
    return log


def verifier_thinking(data: dict, rerun: str, resweep: str | None) -> list[str]:
    rr = load(RE / rerun)["pairwise"][0]
    row = data["pairwise"][0]
    row["permutation_retest"] = block(rr, f"results/d42-retest-2026-10-05/class-b/{rerun}")
    log = [f"F1 p {row['f1_difference']['p_value']} -> {rr['f1_difference']['p_value']}"]
    if resweep:
        rs = load(RE / resweep)
        sw = load(RE / "b17-minimal-resweep-threshold-sweep.json")["optimal"]
        rsp = rs["pairwise"][0]
        row["resweep_sensitivity"] = {
            "_note": ("D43: labelled sensitivity. The minimal-verifier probabilities were rewritten "
                      "33 s after the March sweep read them (inferred from timestamps; "
                      "moved-inputs.md § 3), so the 0.20 threshold was chosen on a file that no "
                      "longer exists. Re-swept on today's file, the optimum is "
                      f"{sw['threshold']}; this is the pairwise at that threshold."),
            "minimal_threshold": sw["threshold"], "minimal_f1": sw["f1"],
            "minimal_n_accepted": sw.get("n_accepted"),
            "f1_difference_bootstrap_mean": rsp["f1_difference"]["mean"],
            "f1_ci": [rsp["f1_difference"]["ci_lower"], rsp["f1_difference"]["ci_upper"]],
            "permutation_retest": block(rsp, f"results/d42-retest-2026-10-05/class-b/{resweep}"),
        }
        data["d42_variant_note"] = (
            "The minimal (\"flash\") variant's summary (threshold 0.20, F1 0.774, n 397) comes "
            "from the first submission of that verifier leg, whose probabilities.json was "
            "overwritten 33 s after the sweep read it; today's file gives F1 0.7666, n 392 at "
            "0.20, and the pairwise above was computed on today's file. Two runs of the same "
            "minimal verifier therefore differ by about 0.007 F1, against the 0.018 "
            "minimal-vs-medium difference (W2.7, D43).")
        log.append(f"re-sweep: minimal threshold {sw['threshold']}, F1 {sw['f1']}; F1 p "
                   f"{rsp['f1_difference']['p_value']}")
    return log


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    jobs = [
        (PW / "fair-384-vs-512.json", fair_384, 2),
        (ROOT / "results/pv/pairwise-effects/pairwise-effect-sizes.json",
         lambda d: pes(d, "pairwise-effect-sizes-v1-inputs.json",
                       {"H:pv-08-text-3of10_vs_consensus-high-25of30":
                        "D:pv-08-text-3of10_vs_consensus-high-25of30",
                        "H:pv-09-text-5of10_vs_consensus-high-25of30":
                        "B:pv-09-text-5of10_vs_consensus-high-25of30"}), 2),
        (ROOT / "results/pv/pairwise-effects/pairwise-effect-sizes-v2.json",
         lambda d: pes(d, "pairwise-effect-sizes-v2.json", {}), 2),
        (ROOT / "results/retest/phase3a-high-text/phase3a-high-text-pairwise.json", p3a, 2),
        (PW / "pro-proposer-verifier-thinking-text/comparison.json",
         lambda d: verifier_thinking(d, "b17-text-as-is-comparison.json",
                                     "b17-text-resweep-comparison.json"), 2),
        (PW / "pro-proposer-verifier-thinking-image/comparison.json",
         lambda d: verifier_thinking(d, "b18-image-as-is-comparison.json", None), 2),
    ]
    for path, fn, _ in jobs:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        print(f"== {path.relative_to(ROOT)}")
        for line in fn(data):
            print("   " + line)
        if isinstance(data, dict):
            data["d42_annotation"] = NOTE
        if args.write:
            indent = 2 if raw.startswith('{\n  "') else (1 if raw.startswith('{\n "') else None)
            path.write_text(json.dumps(data, indent=indent) + ("\n" if raw.endswith("\n") else ""),
                            encoding="utf-8")

    b16 = PW / "pairwise-384px.json"
    raw = b16.read_text(encoding="utf-8")
    data = json.loads(raw)
    data["d42_annotation"] = (
        "NOT RE-TESTABLE under D42 (2026-10-06). The current per-tile scorer refuses this "
        "file's 512 px detections on the 384 px frame: only 72 of 558 in-frame detections "
        "carry a 384 px tile name (TileJoinRefusalError). In March the same mismatch was "
        "silent: the per-tile tables behind these CIs and p-values dropped the TP and FP of "
        "most 512 px detections, so they should not be cited. The contrasts are superseded "
        "by fair-384-vs-512.json, which reassigns 512 px detections to 384 px tiles.")
    print(f"== {b16.relative_to(ROOT)}: note added (not re-testable)")
    if args.write:
        indent = 2 if raw.startswith('{\n  "') else (1 if raw.startswith('{\n "') else None)
        b16.write_text(json.dumps(data, indent=indent) + ("\n" if raw.endswith("\n") else ""),
                       encoding="utf-8")
    if not args.write:
        print("(dry run: nothing written; --write applies it)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
