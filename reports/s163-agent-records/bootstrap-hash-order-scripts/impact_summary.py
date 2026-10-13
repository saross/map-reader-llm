#!/usr/bin/env python3
"""
Summarise the D63 impact replays: committed -> fixed, with the hash-seed spread.

Reads the replay outputs written by ``script_replay.py`` under ``--work`` and
the committed files in ``--repo``, and writes a JSON record and a Markdown
summary. For every paired-difference interval it reports:

* the committed value ("before");
* today's ``main`` under ``PYTHONHASHSEED`` 0-3 (the spread that the hash
  order alone produces on today's code and inputs);
* the fixed branch (identical under every hash seed; checked);

and flags verdict crossings: an interval that starts or stops excluding zero
(committed -> fixed, and within the ``main`` spread), a p value crossing
0.05, a changed BH (Benjamini-Hochberg) decision, an interaction flag, or an
SD-slope flag.

Integrity: every replay ran twice (``run1``/``run2``); the summary refuses to
use a value unless both runs' digests agree (volatile keys dropped, listed in
each ``digests.json``), and requires the fixed branch's seeds to agree.

Usage::

    python impact_summary.py --repo <clone> --work /tmp/d63-runs --out <dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Callable

MAIN_SEEDS = (0, 1, 2, 3)
FIX_SEEDS = (1, 2)
METRICS = ("f1", "precision", "recall")


# ---------------------------------------------------------------------------
# Replay bookkeeping
# ---------------------------------------------------------------------------

VOLATILE_KEY = re.compile(
    r"(generated|timestamp|run_at|created|_at$|^date$|git_head|git_commit|"
    r"source_commit|commit$|elapsed|duration|runtime|wall|hostname|python_executable)",
    re.IGNORECASE,
)


def _strip(obj: Any) -> Any:
    """Drop volatile keys (when or where a run happened) from a JSON value."""
    if isinstance(obj, dict):
        return {k: _strip(v) for k, v in obj.items() if not VOLATILE_KEY.search(str(k))}
    if isinstance(obj, list):
        return [_strip(v) for v in obj]
    return obj


def norm_digest(seed_dir: Path, rel: str) -> str:
    """SHA-256 of an output with run-specific paths and volatile keys removed.

    Each replay ran in its own copy (``<work>/<name>/<ref>-<tag>/tree``), and
    some outputs record absolute input paths, so the copy's path is replaced
    by ``<tree>`` before hashing; JSON outputs also lose their timestamp keys.
    """
    path = seed_dir / rel
    if not path.exists():
        return "MISSING"
    text = path.read_text().replace(str(seed_dir.parent / "tree"), "<tree>")
    if path.suffix == ".json":
        text = json.dumps(_strip(json.loads(text)))
    return hashlib.sha256(text.encode()).hexdigest()


def _runs(work: Path, name: str, ref: str, seeds_by_tag: dict[str, tuple[int, ...]],
          rel: str) -> dict:
    """Locate each seed's output folder and check run1 == run2 per seed.

    Args:
        work: Replay work directory.
        name: Replay family name.
        ref: ``origin-main`` or ``bootstrap-hash-order``.
        seeds_by_tag: Tag stem (without ``-run1``/``-run2``) -> seeds.

    Returns:
        ``{seed: folder}`` for run1, after checking integrity.

    Raises:
        SystemExit: if a run is missing or the two runs disagree.
    """
    out: dict[int, Path] = {}
    for stem, seeds in seeds_by_tag.items():
        folders = {run: work / name / (f"{ref}-{stem}-{run}" if stem else f"{ref}-{run}")
                   for run in ("run1", "run2")}
        for seed in seeds:
            d1 = norm_digest(folders["run1"] / f"seed-{seed}", rel)
            d2 = norm_digest(folders["run2"] / f"seed-{seed}", rel)
            if d1 != d2 or d1 == "MISSING":
                raise SystemExit(f"INTEGRITY FAIL {name} {ref} seed {seed} {rel}: {d1} vs {d2}")
            out[seed] = folders["run1"] / f"seed-{seed}"
            DIGESTS[(name, ref, seed, rel)] = d1
    return out


DIGESTS: dict[tuple, str] = {}


def _load(folder: Path, rel: str) -> Any:
    """Load one replay output JSON."""
    return json.loads((folder / rel).read_text())


def _excl0(lo: float | None, hi: float | None) -> bool | None:
    """Whether an interval excludes zero (None if undefined)."""
    if lo is None or hi is None or (isinstance(lo, float) and math.isnan(lo)):
        return None
    return bool(lo > 0 or hi < 0)


# ---------------------------------------------------------------------------
# Family extractors: each returns {row_id: {metric: {lo, hi, mean, p}}}
# ---------------------------------------------------------------------------

def _diff_block(block: dict, p: float | None = None) -> dict:
    return {"lo": block.get("ci_lower"), "hi": block.get("ci_upper"),
            "mean": block.get("mean"),
            "p": p if p is not None else block.get("p_value")}


def ex_retest(doc: dict, committed: bool) -> dict:
    """Retest phase evaluation: one row per condition pair."""
    phase = next(iter(k for k in doc if not k.startswith("_")))
    rows = {}
    for r in doc[phase]["pairwise"]:
        rid = f"{phase}: {r['condition_a']} vs {r['condition_b']}"
        perm = r.get("permutation_retest", {}) if committed else {}
        rows[rid] = {m: _diff_block(r[f"{m}_difference"],
                                    perm.get(f"{m}_p") if committed else None)
                     for m in METRICS}
        rows[rid]["_bh"] = (perm.get("significant_bh_within_phase") if committed
                            else r.get("significant"))
    return rows


def ex_keyed(doc: dict, committed: bool) -> dict:
    """fair-384-vs-512 / pairwise-384px: entries keyed by comparison id."""
    rows = {}
    for key, entry in doc.items():
        if not isinstance(entry, dict) or "result" not in entry:
            continue
        res = entry["result"]
        if "refused" in res:
            # Today's scorer refuses this comparison (tile-join shortfall).
            rows[key] = {"_refused": res["refused"][:160]}
            continue
        perm = res.get("permutation_retest", {}) if committed else {}
        rows[key] = {m: _diff_block(res[f"{m}_difference"],
                                    perm.get(f"{m}_p") if committed else None)
                     for m in METRICS}
    return rows


def ex_pv(doc: dict, committed: bool) -> dict:
    """evaluate_pv_results compare --pairwise: the ``pairwise`` list."""
    rows = {}
    for r in doc["pairwise"]:
        rid = f"{r['variant_a'].split('/')[-1]} vs {r['variant_b'].split('/')[-1]}"
        perm = r.get("permutation_retest", {}) if committed else {}
        rows[rid] = {m: _diff_block(r[f"{m}_difference"],
                                    perm.get(f"{m}_p") if committed else None)
                     for m in METRICS}
    return rows


def ex_interaction(doc: dict, committed: bool) -> dict:
    """Thinking x temperature interaction: contrasts and simple effects."""
    if committed:
        doc = doc["thinking_temp_interaction"]
    rows = {}
    for m, test in doc["interaction_tests"].items():
        for c in test["interaction_contrasts"]:
            rid = f"{m}: difference of differences"
            rows[rid] = {"dod": _diff_block(c["difference_of_differences"])}
        for level, se in test["simple_effects"].items():
            rows[f"{m}: simple effect at {level}"] = {"se": _diff_block(se)}
        rows[f"{m}: interaction_detected"] = {"_flag": test["interaction_detected"]}
    return rows


def ex_sd(doc: dict, committed: bool) -> dict:
    """SD shrinkage v1: per-stratum slopes (the flag) and per-cell SD CIs."""
    rows = {}
    for r in doc["per_stratum_slopes"]:
        rid = f"slope {r['track']} {r['thinking']} T{r['T']}"
        rows[rid] = {"beta_1": {"lo": r["beta_1_ci_lower"], "hi": r["beta_1_ci_upper"],
                                "mean": r["beta_1"], "p": None},
                     "_flag": r["slower_than_iid"]}
    for r in doc["sd_per_cell_per_k"]:
        rid = f"sd {r['track']} {r['thinking']} T{r['T']} K{r['K_used']}"
        rows[rid] = {"sd": {"lo": r["sd_ci_lower"], "hi": r["sd_ci_upper"],
                            "mean": r["sd_f1"], "p": None}}
    return rows


FAMILIES: list[dict[str, Any]] = [
    *({"family": "retest", "name": "retest", "out": f"out/{p}-evaluation.json",
       "committed": [f"results/retest/{p}-evaluation.json"], "ex": ex_retest,
       "main_tags": {"s01": (0, 1), "s23": (2, 3)}, "fix_tags": {"s12": (1, 2)}}
      for p in ("phase2a", "phase2b-track1", "phase2b-track2", "phase2c-exploratory",
                "phase2c-track1", "phase2c-track2", "phase2d-track1", "phase2d-track2",
                "phase2e")),
    {"family": "interaction", "name": "interaction", "out": "out/image.json",
     "committed": ["results/secondary-effects/secondary_effects.json"], "ex": ex_interaction,
     "main_tags": {"": MAIN_SEEDS}, "fix_tags": {"": FIX_SEEDS}},
    {"family": "interaction", "name": "interaction", "out": "out/text.json",
     "committed": ["results/phase3a-text-matrix/secondary_effects.json"],
     "ex": ex_interaction, "main_tags": {"": MAIN_SEEDS}, "fix_tags": {"": FIX_SEEDS}},
    {"family": "sd-v1", "name": "sd-v1",
     "out": "results/secondary-effects-consensus-sd/sd_shrinkage.json",
     "committed": ["results/secondary-effects-consensus-sd/sd_shrinkage.json"], "ex": ex_sd,
     "main_tags": {"": MAIN_SEEDS}, "fix_tags": {"": FIX_SEEDS}},
    {"family": "fair384", "name": "fair384", "out": "out/fair-384-vs-512.json",
     "committed": ["results/h11-384-pv-diagnostic/pairwise/fair-384-vs-512.json",
                   "results/d42-retest-2026-10-05/class-b/fair-384-vs-512-march-sweep.json"],
     "ex": ex_keyed, "main_tags": {"s01": (0, 1), "s23": (2, 3)}, "fix_tags": {"s12": (1, 2)}},
    {"family": "fair384", "name": "fair384", "out": "out/pairwise-384px.json",
     "committed": ["results/h11-384-pv-diagnostic/pairwise/pairwise-384px.json"],
     "ex": ex_keyed, "main_tags": {"s01": (0, 1), "s23": (2, 3)}, "fix_tags": {"s12": (1, 2)}},
    {"family": "pvpair", "name": "pvpair", "out": "out/text-asis/comparison.json",
     "committed": [
         "results/h11-384-pv-diagnostic/pairwise/pro-proposer-verifier-thinking-text/"
         "comparison.json",
         "results/d42-retest-2026-10-05/class-b/b17-text-as-is-comparison.json"],
     "ex": ex_pv, "main_tags": {"": MAIN_SEEDS}, "fix_tags": {"": FIX_SEEDS}},
    {"family": "pvpair", "name": "pvpair", "out": "out/image-asis/comparison.json",
     "committed": [
         "results/h11-384-pv-diagnostic/pairwise/pro-proposer-verifier-thinking-image/"
         "comparison.json",
         "results/d42-retest-2026-10-05/class-b/b18-image-as-is-comparison.json"],
     "ex": ex_pv, "main_tags": {"": MAIN_SEEDS}, "fix_tags": {"": FIX_SEEDS}},
]


def summarise(repo: Path, work: Path, fam: dict) -> list[dict]:
    """Build one row per (comparison, metric) for one output file."""
    ex: Callable[[dict, bool], dict] = fam["ex"]
    main = _runs(work, fam["name"], "origin-main", fam["main_tags"], fam["out"])
    fix = _runs(work, fam["name"], fam.get("fix_ref", "bootstrap-hash-order"),
                fam["fix_tags"], fam["out"])
    # The fixed branch must give one output under every hash seed.
    fix_digests = {norm_digest(fix[s], fam["out"]) for s in fix}
    if len(fix_digests) != 1:
        raise SystemExit(f"FIX VARIES {fam['out']}: {fix_digests}")
    fixed = ex(_load(fix[min(fix)], fam["out"]), False)
    commits = {
        "main": sorted({json.loads((f.parent / "digests.json").read_text())["commit"][:9]
                        for f in main.values()}),
        "fixed": sorted({json.loads((f.parent / "digests.json").read_text())["commit"][:9]
                         for f in fix.values()}),
    }
    mains = {s: ex(_load(main[s], fam["out"]), False) for s in sorted(main)}
    committed = []
    for rel in fam["committed"]:
        path = repo / rel
        committed.append((rel, ex(json.loads(path.read_text()), True) if path.exists() else {}))
    rows = []
    for rid, metrics in fixed.items():
        for m, val in metrics.items():
            if m.startswith("_"):
                continue
            row = {"output": fam["out"], "family": fam["family"], "id": rid, "metric": m,
                   "commits": commits,
                   "fixed": val, "fixed_excl0": _excl0(val["lo"], val["hi"]),
                   "main": {s: mains[s].get(rid, {}).get(m) for s in mains},
                   "committed": {rel: c.get(rid, {}).get(m) for rel, c in committed}}
            row["main_excl0"] = sorted({_excl0(v["lo"], v["hi"]) for v in row["main"].values()
                                        if v}, key=str)
            row["committed_excl0"] = {rel: (_excl0(v["lo"], v["hi"]) if v else None)
                                      for rel, v in row["committed"].items()}
            row["main_p"] = sorted({v["p"] for v in row["main"].values() if v}, key=str)
            rows.append(row)
        for flag in ("_flag", "_bh", "_refused"):
            if flag in metrics:
                rows.append({"output": fam["out"], "family": fam["family"], "id": rid,
                             "metric": flag, "fixed": metrics[flag],
                             "main": {s: mains[s].get(rid, {}).get(flag) for s in mains},
                             "committed": {rel: c.get(rid, {}).get(flag)
                                           for rel, c in committed}})
    return rows


def main() -> int:
    """Summarise every family that has finished replays."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--families", nargs="*")
    args = ap.parse_args()
    all_rows: list[dict] = []
    skipped = []
    for fam in FAMILIES:
        if args.families and fam["family"] not in args.families:
            continue
        try:
            all_rows.extend(summarise(args.repo, args.work, fam))
        except FileNotFoundError as exc:
            skipped.append(f"{fam['out']}: {exc}")
    args.out.mkdir(parents=True, exist_ok=True)
    digests = [{"name": k[0], "ref": k[1], "seed": k[2], "output": k[3], "sha256": v}
               for k, v in sorted(DIGESTS.items(), key=str)]
    (args.out / "impact-rows.json").write_text(json.dumps(
        {"rows": all_rows, "skipped": skipped, "run1_equals_run2_digests": digests},
        indent=1, default=str) + "\n")
    print(f"{len(all_rows)} rows; skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
