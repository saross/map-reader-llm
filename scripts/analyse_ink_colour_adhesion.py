#!/usr/bin/env python3
"""
Obs 407 ink-colour adhesion test — does displacement sort by attractor ink colour?

Background
----------
During the ruling-21 marking walk the PI observed that displaced marks
appear to "adhere" to nearby printed features (attractors), and on walk
item #4635 noted the binding followed ink colour: a displaced detection
bound to the *black* trig-on-mound symbol rather than the nearer
orange-brown mound symbol ("if it adhered to this one it would be
orange-brown"). Obs 407 records the testable form: if adhesion is
colour-matched, displacement behaviour should sort by attractor ink
colour, testable from the marking data alone.

Operationalisation (PI-approved, Session 133 pre-run review;
``planning/s133-analysis-block-2026-08-15.md`` hardening 1)
-----------------------------------------------------------
A symbol-class contrast on displacement magnitude, not a full
vector-field attribution. On the map sheets, symbol types map onto ink
colour classes:

- **black-element**: ``bench_mark_on_mound``, ``trig_point_on_mound`` —
  the mound carries a black geodetic overprint (and its printed
  elevation numeral), so a black-ink attractor coincides with the true
  centre;
- **plain**: ``burial_mound``, ``settlement_mound`` — orange-brown
  relief ink only; the nearest black ink is off-mound.

Colour-matched adhesion for model detections predicts *smaller*
displacements on black-element mounds (the black attractor sits on the
target) than on plain mounds. The student cohorts act as the internal
control for the "geodetic mounds are larger / better mapped" confound
(block plan hardening 2): a mapping-quality effect should compress
student displacements on black-element mounds too; colour adhesion
specific to the model pipeline should not.

Cohorts (block plan hardening 3; exclusions fixed a priori)
-----------------------------------------------------------
- ``model``: ``source_layer == promoted_phantom`` — VLM detections
  promoted to the reference; displacement = detection position → the
  PI's marked true centre.
- ``student_random``: ``item_type == jitter_sample`` — the 100-record
  random, conflation-free student sample drawn to measure placement
  error (``planning/point-marking-app-spec.md``); the unbiased student
  displacement cohort.
- ``student_hard``: remaining ``corrected_student`` records —
  condition-selected (conflations, pairs, merge sites), reported as a
  biased-but-larger student cohort.

Excluded a priori: ``not_a_mound`` records, ``extra_point``, skipped
records, and records with no displacement.

Statistics
----------
Per cohort: black − plain difference in mean and in median displacement,
two-sided label-permutation tests (default 10,000 permutations, seed
42), plus per-class descriptives (n, mean, median, quartiles, P90).

Usage
-----
    python scripts/analyse_ink_colour_adhesion.py            # writes JSON
    python scripts/analyse_ink_colour_adhesion.py --dry-run  # print, no write

Output: ``results/obs407-ink-colour-adhesion/adhesion-results.json``.
Compute: trivial (<1 min); run on sapphire per the standing compute rule.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_INPUT = (
    REPO_ROOT / "results" / "deployment-oracle-2026-06-06" / "canonical-gt"
    / "marked-centres.csv"
)
DEFAULT_OUTPUT = (
    REPO_ROOT / "results" / "obs407-ink-colour-adhesion" / "adhesion-results.json"
)

BLACK_ELEMENT = {"bench_mark_on_mound", "trig_point_on_mound"}
PLAIN = {"burial_mound", "settlement_mound"}
SEED = 42
N_PERMUTATIONS = 10_000


def load_records(path: Path) -> list[dict]:
    """
    Load marked-centres rows that pass the a-priori inclusion filters.

    Excludes ``not_a_mound`` symbol types, the single ``extra_point``
    layer row, skipped records, and records without a displacement
    (the filters fixed in the block plan before any contrast ran).

    Args:
        path: the marked-centres.csv produced by the ruling-21 marking app.

    Returns:
        One dict per retained row with keys ``source_layer``,
        ``item_type``, ``symbol_type``, ``colour_class`` ("black" or
        "plain"), and ``displacement_m`` (float).
    """
    kept: list[dict] = []
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            if row["symbol_type"] == "not_a_mound":
                continue
            if row["source_layer"] == "extra_point":
                continue
            if row["skipped"] == "True":
                continue
            if not row["displacement_m"]:
                continue
            symbol = row["symbol_type"]
            if symbol in BLACK_ELEMENT:
                colour = "black"
            elif symbol in PLAIN:
                colour = "plain"
            else:  # an unexpected symbol type is a stop state, not a guess
                raise ValueError(f"unmapped symbol_type {symbol!r}")
            kept.append(
                {
                    "source_layer": row["source_layer"],
                    "item_type": row["item_type"],
                    "symbol_type": symbol,
                    "colour_class": colour,
                    "displacement_m": float(row["displacement_m"]),
                }
            )
    return kept


def assign_cohort(record: dict) -> str | None:
    """
    Map a record to its analysis cohort, or None if it belongs to none.

    Cohort definitions are fixed in the block plan (hardening 3):
    ``model`` = promoted phantoms; ``student_random`` = the seeded
    jitter sample; ``student_hard`` = every other corrected-student row.
    """
    if record["source_layer"] == "promoted_phantom":
        return "model"
    if record["source_layer"] == "corrected_student":
        if record["item_type"] == "jitter_sample":
            return "student_random"
        return "student_hard"
    return None


def descriptives(values: list[float]) -> dict:
    """Return n, mean, median, quartiles, and P90 for one class sample."""
    arr = np.asarray(values, dtype=float)
    return {
        "n": int(arr.size),
        "mean_m": round(float(arr.mean()), 2),
        "median_m": round(float(np.median(arr)), 2),
        "q1_m": round(float(np.percentile(arr, 25)), 2),
        "q3_m": round(float(np.percentile(arr, 75)), 2),
        "p90_m": round(float(np.percentile(arr, 90)), 2),
    }


def permutation_test(
    black: list[float],
    plain: list[float],
    statistic: str,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict:
    """
    Two-sided label-permutation test on the black − plain difference.

    The observed statistic is the difference (black − plain) in the
    chosen summary (``"mean"`` or ``"median"``) of displacement
    magnitude. Under the null the colour labels are exchangeable, so
    the labels are shuffled ``n_permutations`` times and the two-sided
    p-value is the add-one-corrected share of permuted |differences|
    at least as large as the observed |difference|.

    Args:
        black: displacement magnitudes (m), black-element class.
        plain: displacement magnitudes (m), plain class.
        statistic: "mean" or "median".
        n_permutations: number of label shuffles.
        seed: RNG seed (fixed so reruns are byte-stable).

    Returns:
        Dict with the observed difference, p-value, and test metadata.
    """
    summarise = np.mean if statistic == "mean" else np.median
    pooled = np.asarray(black + plain, dtype=float)
    n_black = len(black)
    observed = float(summarise(pooled[:n_black]) - summarise(pooled[n_black:]))

    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(n_permutations):
        perm = rng.permutation(pooled)
        delta = float(summarise(perm[:n_black]) - summarise(perm[n_black:]))
        if abs(delta) >= abs(observed):
            exceed += 1
    p_value = (1 + exceed) / (1 + n_permutations)
    return {
        "statistic": statistic,
        "observed_black_minus_plain_m": round(observed, 3),
        "p_two_sided": round(p_value, 5),
        "n_permutations": n_permutations,
        "seed": seed,
    }


def analyse(records: list[dict], n_permutations: int = N_PERMUTATIONS) -> dict:
    """
    Run the full cohort × class analysis on the retained records.

    Returns the results dict that becomes the output JSON: per-cohort
    class descriptives and both permutation tests, plus the census
    the findings document anchors to.
    """
    cohorts: dict[str, dict[str, list[float]]] = {}
    for rec in records:
        cohort = assign_cohort(rec)
        if cohort is None:
            continue
        cohorts.setdefault(cohort, {"black": [], "plain": []})
        cohorts[cohort][rec["colour_class"]].append(rec["displacement_m"])

    results: dict = {"cohorts": {}}
    for name, classes in sorted(cohorts.items()):
        black, plain = classes["black"], classes["plain"]
        results["cohorts"][name] = {
            "black": descriptives(black),
            "plain": descriptives(plain),
            "tests": [
                permutation_test(black, plain, "mean", n_permutations),
                permutation_test(black, plain, "median", n_permutations),
            ],
        }
    results["census"] = {
        "records_retained": len(records),
        "records_in_cohorts": sum(
            len(c["black"]) + len(c["plain"]) for c in cohorts.values()
        ),
    }
    return results


def main(argv: list[str] | None = None) -> int:
    """CLI entry point; see the module docstring for the analysis design."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                        help="marked-centres.csv path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="results JSON path")
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS,
                        help="label shuffles per test (default 10,000)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print results JSON to stdout, write nothing")
    args = parser.parse_args(argv)

    records = load_records(args.input)
    results = analyse(records, n_permutations=args.permutations)
    results["inputs"] = {
        "marked_centres_csv": str(args.input.relative_to(REPO_ROOT)
                                  if args.input.is_relative_to(REPO_ROOT) else args.input),
        "colour_classes": {
            "black": sorted(BLACK_ELEMENT),
            "plain": sorted(PLAIN),
        },
    }

    payload = json.dumps(results, indent=1, ensure_ascii=False) + "\n"
    if args.dry_run:
        print(payload)
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload)
    print(f"wrote {args.output}")
    # A compact console summary so the operator sees the headline without
    # opening the JSON (medians are the skew-robust reading).
    for name, cohort in results["cohorts"].items():
        med_b = cohort["black"]["median_m"]
        med_p = cohort["plain"]["median_m"]
        p_med = cohort["tests"][1]["p_two_sided"]
        print(f"  {name}: median black {med_b} m vs plain {med_p} m (p={p_med})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
