#!/usr/bin/env python3
"""
Gate the K-ladder tile-join job's id runs against the committed artefacts, and tabulate the joins.

Part of the S166 K-ladder tile-join job
(``reports/s166-agent-records/k-ladder-mcc-join.md``). Reads the chain's
outputs under ``results/k-ladder-2026-09-12/mcc-join-2026-10-30/<join>/`` and
writes that directory's ``summary.json``.

**The gate (the published join, run with the committed commands).** Every
``id`` artefact is compared with its committed counterpart key by key, in key
order, value for value. The only keys set aside are those that cannot match
by construction, each listed in the output: run timestamps
(``generated_at_utc``), commit stamps (``git_commit``), the paths of this
run's own outputs (``tiering_artefact``, ``artefact``), and three provenance
fields of the summaries (``source_inventory``, which names this job's copy of
the Phase 2 inventory; ``conditions``, a key the driver gained on 2026-10-30
after the Phase 1 and Phase 2 summaries were committed; and absolute
``*_override`` paths, compared after their machine-specific root is removed).

**The tables**, per join, beside ``id``:

1. per ladder, tile-MCC from K = 1 to the best F1 rung (delta, BH p,
   direction), the counts behind "falls on 16 of 21; no significant rise;
   four significant falls", and every other significant MCC pair;
2. the MCC MCB admissible sets, K = 1's admissibility and the highest-MCC
   rung;
3. § 8.6: the consensus-only and the verified K = 1 -> 10 tile-MCC changes,
   as evaluated and on D51's clipped basis;
4. the id-join mechanism diagnostic, per rung.

Usage: python summarise.py <clone_root>

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

K = "results/k-ladder-2026-09-12"
CLIP = f"{K}/clipped-mcc-2026-10-30"
R = f"{K}/mcc-join-2026-10-30"
JOINS = ("id", "geometric-primary", "geometric-contains")
GEOMETRIC = JOINS[1:]
Q = 0.05
ROOT_RE = re.compile(r"^/.*?/(results|inputs|outputs)/")

#: The keys the tiering harness gained after the committed 55-map and Phase 2
#: MCC tests were written (2026-09-12, 06:11 to 08:52 UTC, at 156bddf36): the
#: gate record's geometry arm (24e6ae696, 2026-09-12 13:00 UTC), the withheld
#: cells (670f6ee76, 2026-09-13) and the MCC family's tiers and ranking
#: (30a27f361, 2026-09-13). A committed file written before the first of them
#: may lack exactly these keys and nothing else; any other difference fails.
SCHEMA_CUTOFF_UTC = "2026-09-12T13:00:34"
EXPECTED_ADDITIONS = frozenset({
    "/gate/cell_gates/<ref>/geometry", "/mcc_permutation/gates/<ref>/geometry",
    "/mcc_permutation/n_cells_with_mcc", "/mcc_permutation/n_cells_withheld",
    "/mcc_permutation/n_pairs", "/mcc_permutation/n_tiers",
    "/mcc_permutation/ranking", "/mcc_permutation/reported_not_tiering",
    "/mcc_permutation/tie_set", "/mcc_permutation/tiers",
    "/mcc_permutation/withheld", "/n_cells", "/n_cells_withheld", "/withheld_cells",
})

#: Phase 1 display names (k_ladder_mcb.DISPLAY_NAMES, copied so this reads
#: without importing the instruments).
P1_NAMES = {
    "gs-stride-a": "GS stride A (board frame)",
    "55map-stride-a-r2": "55-map stride A, r2",
    "55map-stride-a-standardised": "55-map stride A, standardised",
    "55map-stride-b-r2": "55-map stride B, r2",
    "55map-stride-b-standardised": "55-map stride B, standardised",
    "55map-stride-b-g37vf-r2": "55-map stride B, 3.7 verifier",
    "37arm1-r2": "3.7 arm 1",
    "37arm2-r2": "3.7 arm 2",
    "tier-e": "tier E (grid 384 px / 50 %, verified)",
}


def load(path: Path) -> dict:
    """Read one JSON file."""
    return json.loads(path.read_text())


def norm(value: object) -> object:
    """Strip a machine-specific root from an absolute repository path."""
    if isinstance(value, str):
        return ROOT_RE.sub(r"<ROOT>/\1/", value)
    return value


def diff(a: object, b: object, ignore: set[str], path: str = "") -> dict[str, list[str]]:
    """Every difference between two JSON values, by kind.

    Args:
        a: The committed value.
        b: This run's value.
        ignore: Key names set aside at any depth.
        path: Where in the document this is (for the report).

    Returns:
        ``{"value", "missing", "added", "order"}``, each a list of paths:
        a value that differs (or a list of another length); a committed key
        this run lacks; a key this run writes that the committed artefact
        lacks; and a dict whose shared keys come in another order.
    """
    out: dict[str, list[str]] = {"value": [], "missing": [], "added": [], "order": []}

    def walk(x: object, y: object, where: str) -> None:
        if isinstance(x, dict) and isinstance(y, dict):
            kx = [k for k in x if k not in ignore]
            ky = [k for k in y if k not in ignore]
            out["missing"] += [f"{where}/{k}" for k in kx if k not in y]
            out["added"] += [f"{where}/{k}" for k in ky if k not in x]
            if [k for k in kx if k in y] != [k for k in ky if k in x]:
                out["order"].append(where)
            for k in kx:
                if k not in y:
                    continue
                if k.endswith("_override"):
                    if norm(x[k]) != norm(y[k]):
                        out["value"].append(f"{where}/{k}: {x[k]!r} != {y[k]!r}")
                else:
                    walk(x[k], y[k], f"{where}/{k}")
        elif isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y):
                out["value"].append(f"{where}: length {len(x)} != {len(y)}")
            for i, (u, v) in enumerate(zip(x, y)):
                walk(u, v, f"{where}[{i}]")
        elif x != y or type(x) is not type(y):
            out["value"].append(f"{where}: {x!r} != {y!r}")

    walk(a, b, path)
    return out


def fold(path: str) -> str:
    """A key path with list indices and cell refs folded, for comparison."""
    path = re.sub(r"\[\d+\]", "[]", path)
    return re.sub(r"/[^/]*::[^/]*", "/<ref>", path)


def verdict(d: dict[str, list[str]], allow_added: bool) -> bool:
    """Whether one comparison reproduces the committed artefact.

    Args:
        d: A :func:`diff` result.
        allow_added: Whether this run may add keys: only where the committed
            file predates :data:`SCHEMA_CUTOFF_UTC`, and then only the keys in
            :data:`EXPECTED_ADDITIONS`.

    Returns:
        True when no committed value or key is lost or changed, nothing is
        reordered, and nothing is added beyond what is tolerated.
    """
    if d["value"] or d["missing"] or d["order"]:
        return False
    if not d["added"]:
        return True
    return allow_added and {fold(p) for p in d["added"]} <= EXPECTED_ADDITIONS


def predates_schema(doc: dict) -> bool:
    """Whether a committed artefact was written before the harness's additions."""
    return str(doc.get("generated_at_utc", "9999")) < SCHEMA_CUTOFF_UTC


def schema_additions(files: dict[str, dict[str, list[str]]]) -> list[str]:
    """The distinct added key paths, with list indices and cell refs folded."""
    return sorted({fold(p) for d in files.values() for p in d["added"]})


def gate_dir(root: Path, committed: str, mine: str, ignore_ladder: set[str],
             ignore_summary: set[str], tiering_glob: str) -> dict:
    """Compare a whole committed instrument directory with this run's.

    Args:
        root: Clone root.
        committed: Repo-relative committed directory.
        mine: Repo-relative directory this run wrote.
        ignore_ladder: Keys set aside in per-ladder JSONs.
        ignore_summary: Keys set aside in ``summary.json``.
        tiering_glob: Glob of the tiering JSONs under ``tiering/``.

    Returns:
        A gate record with every difference listed.
    """
    rec: dict = {"committed": committed, "run": mine, "files": {}, "passed": True}
    c_dir, m_dir = root / committed, root / mine
    names = sorted(p.name for p in c_dir.glob("*.json"))
    mine_names = sorted(p.name for p in m_dir.glob("*.json"))
    if names != mine_names:
        rec["passed"] = False
        rec["file_set"] = {"committed": names, "run": mine_names}
    for name in names:
        ignore = ignore_summary if name == "summary.json" else ignore_ladder
        doc = load(c_dir / name)
        d = diff(doc, load(m_dir / name), ignore) \
            if (m_dir / name).exists() else {"value": ["file missing"],
                                             "missing": [], "added": [], "order": []}
        d["committed_predates_schema"] = [str(predates_schema(doc))]
        rec["files"][name] = d
        rec["passed"] &= verdict(d, predates_schema(doc))
    tierings = sorted((c_dir / "tiering").glob(tiering_glob))
    for path in tierings:
        rel = path.relative_to(c_dir)
        other = m_dir / rel
        doc = load(path)
        d = diff(doc, load(other), {"generated_at_utc", "git_commit"}) \
            if other.exists() else {"value": ["file missing"], "missing": [],
                                    "added": [], "order": []}
        d["committed_predates_schema"] = [str(predates_schema(doc))]
        rec["files"][str(rel)] = d
        rec["passed"] &= verdict(d, predates_schema(doc))
    rec["n_files_compared"] = len(rec["files"])
    rec["n_files_with_tolerated_additions"] = sum(
        1 for d in rec["files"].values() if d["added"])
    rec["schema_additions"] = schema_additions(rec["files"])
    return rec


def gate_mcb(root: Path, committed: str, mine: str) -> dict:
    """Compare a committed MCB directory (summary and per-ladder artefacts)."""
    rec: dict = {"committed": committed, "run": mine, "files": {}, "passed": True}
    c_dir, m_dir = root / committed, root / mine
    d = diff(load(c_dir / "summary.json"), load(m_dir / "summary.json"),
             {"generated_at_utc", "artefact"})
    rec["files"]["summary.json"] = d
    rec["passed"] &= verdict(d, False)
    for path in sorted(c_dir.glob("*/*.json")):
        rel = path.relative_to(c_dir)
        other = m_dir / rel
        d = diff(load(path), load(other), set()) if other.exists() else {
            "value": ["file missing"], "missing": [], "added": [], "order": []}
        rec["files"][str(rel)] = d
        rec["passed"] &= verdict(d, False)
    rec["n_files_compared"] = len(rec["files"])
    rec["schema_additions"] = schema_additions(rec["files"])
    return rec


def tiering_of(root: Path, join: str, group_dir: str, slug: str | None,
               buffer_m: int) -> dict:
    """This run's tiering JSON for one ladder under one join."""
    name = f"tiering_{buffer_m}m" + ("" if join == "id" else f"_{join}") + ".json"
    base = root / R / join / group_dir
    return load(base / name) if slug is None else load(base / "tiering" / slug / name)


def oriented_pair(tiering: dict, ref_lo: str, ref_hi: str) -> dict:
    """The MCC pair (higher K) - (lower K) from a tiering's round-robin."""
    block = tiering["mcc_permutation"]
    for e in block["pairwise"]:
        if {e["ref_a"], e["ref_b"]} == {ref_lo, ref_hi}:
            sign = 1.0 if e["ref_a"] == ref_hi else -1.0
            mcc = {row["ref"]: row["mcc"] for row in block["ranking"]}
            return {"low": mcc[ref_lo], "high": mcc[ref_hi],
                    "delta": round(sign * e["observed_mcc_diff"], 6),
                    "p_bh": e["bh_adjusted_p"], "significant": e["significant"]}
    raise KeyError((ref_lo, ref_hi))


def direction(delta: float, significant: bool) -> str:
    """A pair's direction word, significance marked."""
    word = "falls" if delta < 0 else "rises" if delta > 0 else "flat"
    return word + (" (sig)" if significant else "")


def main() -> int:
    """Gate, tabulate, write ``summary.json``."""
    root = Path(sys.argv[1]).resolve()
    out: dict = {"job": "S166 K-ladder tile-join", "joins": list(JOINS)}

    # ---------------- the gate ----------------
    lad_ignore = {"generated_at_utc", "tiering_artefact"}
    sum_ignore = {"generated_at_utc", "source_inventory", "conditions"}
    gates = {
        "phase1_mcc_test": gate_dir(root, f"{K}/mcc-test", f"{R}/id/mcc-test",
                                    lad_ignore, sum_ignore, "*/tiering_*m.json"),
        "phase2_mcc_test": gate_dir(root, f"{K}/phase2/mcc-test",
                                    f"{R}/id/phase2-mcc-test", lad_ignore,
                                    sum_ignore, "*/tiering_*m.json"),
        "clipped_mcc_test": gate_dir(root, f"{CLIP}/mcc-test",
                                     f"{R}/id/clipped-mcc-test", lad_ignore,
                                     sum_ignore, "*/tiering_*m.json"),
        "phase1_2_tier_e_mcb": gate_mcb(root, f"{K}/mcb", f"{R}/id/mcb"),
        "clipped_mcb": gate_mcb(root, f"{CLIP}/mcb", f"{R}/id/clipped-mcb"),
    }
    te = diff(load(root / K / "tier-e/tiering/tiering_20m.json"),
              load(root / R / "id/tier-e/tiering_20m.json"),
              {"generated_at_utc", "git_commit"})
    gates["tier_e_tiering"] = {"committed": f"{K}/tier-e/tiering/tiering_20m.json",
                               "run": f"{R}/id/tier-e/tiering_20m.json",
                               "files": {"tiering_20m.json": te},
                               "passed": verdict(te, False),
                               "n_files_compared": 1,
                               "schema_additions": schema_additions(
                                   {"tiering_20m.json": te})}
    consensus = load(root / R / "consensus/grid-overlap-joins.json")
    gates["consensus_grid_sweep"] = {
        k: consensus["gate"][k] for k in
        ("passed", "n_rows_replayed", "n_rows_committed", "row_mismatches",
         "rung_mismatches", "f1_and_count_join_invariant", "reference")}
    out["gate"] = {
        "all_passed": all(g["passed"] for g in gates.values()),
        "schema_cutoff_utc": SCHEMA_CUTOFF_UTC,
        "expected_additions": sorted(EXPECTED_ADDITIONS),
        "keys_set_aside": {
            "per_ladder": sorted(lad_ignore), "summaries": sorted(sum_ignore),
            "tierings": ["generated_at_utc", "git_commit"],
            "mcb_summary": ["generated_at_utc", "artefact"],
            "mcb_artefacts": ["*_override compared after removing the root"]},
        "gates": gates,
    }

    # ---------------- census: every tiering, cells, withholding, clip --------
    census = []
    for join in JOINS:
        sfx = "" if join == "id" else f"_{join}"
        paths = sorted((root / R / join).glob(f"*/tiering/*/tiering_*m{sfx}.json"))
        paths.append(root / R / join / "tier-e" / f"tiering_20m{sfx}.json")
        for path in paths:
            doc = load(path)
            block = doc["mcc_permutation"]
            refs = [row["ref"] for row in doc["ranking"]]
            n_clip = sum(r.endswith("-d51clip") for r in refs)
            census.append({
                "join": join,
                "ladder": path.parent.name if "tiering" in path.parent.parent.name
                else "tier-e",
                "n_cells": doc["n_cells"], "n_tiles": doc["n_tiles"],
                "n_withheld_f1_arm": doc["n_cells_withheld"],
                "n_cells_with_mcc": block["n_cells_with_mcc"],
                "n_withheld_mcc_arm": block["n_cells_withheld"],
                "clip_status": ("D51 clipped" if n_clip == len(refs)
                                else "as evaluated" if n_clip == 0 else "MIXED"),
                "tile_join_recorded": block.get("tile_join") or "id"})
    out["tiering_census"] = {
        "n_tierings": len(census),
        "n_cells_per_join": {j: sum(c["n_cells"] for c in census if c["join"] == j)
                             for j in JOINS},
        "n_withheld_any_arm": sum(c["n_withheld_f1_arm"] + c["n_withheld_mcc_arm"]
                                  for c in census),
        "n_mixed_clip_status": sum(c["clip_status"] == "MIXED" for c in census),
        "join_recorded_matches": all(c["tile_join_recorded"] == c["join"]
                                     for c in census),
        "tierings": census,
    }

    # ---------------- Q1: K = 1 -> best rung, every ladder ----------------
    groups = (("phase 1", "mcc-test"), ("phase 2", "phase2-mcc-test"),
              ("clipped", "clipped-mcc-test"))
    q1: dict = {}
    for join in JOINS:
        rows = []
        for group, gdir in groups:
            summ = load(root / R / join / gdir / "summary.json")
            for lad in summ["ladders"]:
                doc = load(root / R / join / gdir / f"{lad['ladder']}.json")
                head = next(p for p in doc["pairs"] if "k1-vs-best" in p["kind"])
                others = [{"pair": p["pair"], "kind": p["kind"],
                           "delta": p["mcc"]["delta"], "p_bh": p["mcc"]["p_bh"]}
                          for p in doc["pairs"]
                          if p["kind"] == "adjacent" and p["mcc"]["significant"]]
                rows.append({
                    "ladder": lad["ladder"], "group": group,
                    "pair": head["pair"],
                    "f1_delta": head["f1"]["delta"], "f1_p_bh": head["f1"]["p_bh"],
                    "mcc_low": head["mcc"]["low"], "mcc_high": head["mcc"]["high"],
                    "mcc_delta": head["mcc"]["delta"], "mcc_p_bh": head["mcc"]["p_bh"],
                    "mcc_significant": head["mcc"]["significant"],
                    "direction": direction(head["mcc"]["delta"],
                                           head["mcc"]["significant"]),
                    "other_significant_mcc_pairs": others,
                    "n_cells_withheld_mcc_arm":
                        (doc.get("tile_join") or {}).get("n_cells_withheld_mcc_arm", 0),
                    "gate_passed": doc["gate"]["passed"],
                })
        # Tier E as evaluated, K = 1 -> best F1 rung (K = 5), from its tiering.
        tier = tiering_of(root, join, "tier-e", None, 20)
        f1 = {r["ref"]: r["eval_f1"] for r in tier["ranking"]}
        refs = sorted(f1, key=lambda r: int(re.search(r"-k(\d+)-", r).group(1)))
        best = max(refs, key=lambda r: f1[r])
        pair = oriented_pair(tier, refs[0], best)
        rows.append({"ladder": "tier-e", "group": "tier E",
                     "pair": f"K1-vs-K{re.search(r'-k(\d+)-', best).group(1)}",
                     "mcc_low": pair["low"], "mcc_high": pair["high"],
                     "mcc_delta": pair["delta"], "mcc_p_bh": pair["p_bh"],
                     "mcc_significant": pair["significant"],
                     "direction": direction(pair["delta"], pair["significant"]),
                     "n_cells_withheld_mcc_arm":
                         tier["mcc_permutation"]["n_cells_withheld"]})

        def tally(sel: list[dict]) -> dict:
            return {"n": len(sel),
                    "falls": sum(r["mcc_delta"] < 0 for r in sel),
                    "rises": sum(r["mcc_delta"] > 0 for r in sel),
                    "significant_falls": [r["ladder"] for r in sel
                                          if r["mcc_delta"] < 0 and r["mcc_p_bh"] < Q],
                    "significant_rises": [r["ladder"] for r in sel
                                          if r["mcc_delta"] > 0 and r["mcc_p_bh"] < Q],
                    "non_falls": [r["ladder"] for r in sel if r["mcc_delta"] >= 0]}

        as_eval = [r for r in rows if r["group"] in ("phase 1", "phase 2")]
        clipped = {r["ladder"].removeprefix("d51clip-"): r for r in rows
                   if r["group"] == "clipped"}
        on_clip = [clipped.get(r["ladder"], r) for r in as_eval]
        q1[join] = {
            "rows": rows,
            "the_21_as_evaluated": tally(as_eval),
            "the_21_on_d51_clipped_basis": tally(on_clip),
            "other_significant_mcc_pairs_the_21": [
                {"ladder": r["ladder"], **p} for r in as_eval
                for p in r["other_significant_mcc_pairs"]],
            "other_significant_mcc_pairs_clipped": [
                {"ladder": r["ladder"], **p} for r in rows if r["group"] == "clipped"
                for p in r["other_significant_mcc_pairs"]],
        }
    out["q1_k1_to_best"] = q1

    # ---------------- Q2: the MCC MCB sets ----------------
    q2: dict = {}
    for join in JOINS:
        res = {}
        for name, sub in (("main", "mcb"), ("clipped", "clipped-mcb")):
            summ = load(root / R / join / sub / "summary.json")
            lads = []
            for lad in summ["ladders"]:
                m = lad["mcc"]
                lads.append({"slug": lad["slug"], "family": lad["family"],
                             "rungs": lad["rungs"],
                             "mcc_admissible_K": m["hsu_admissible_K"],
                             "mcc_best_K": m["best_K"],
                             "mcc_by_K": m["statistic_by_K"],
                             "w_upper": round(m["hsu_w_upper"], 4),
                             "f1_admissible_K": (lad.get("f1") or {}).get(
                                 "hsu_admissible_K")})
            res[name] = {
                "gate_all_passed": summ["gate_all_passed"],
                "n_ladders": len(lads),
                "k1_admissible": sum(1 in x["mcc_admissible_K"] for x in lads),
                "k1_not_admissible": [x["slug"] for x in lads
                                      if 1 not in x["mcc_admissible_K"]],
                "k1_highest": sum(x["mcc_best_K"] == 1 for x in lads),
                "highest_K_counts": {str(k): sum(x["mcc_best_K"] == k for x in lads)
                                     for k in (1, 3, 5, 10)},
                "whole_ladder": sum(len(x["mcc_admissible_K"]) == len(x["rungs"])
                                    for x in lads),
                "excludes_K10": [x["slug"] for x in lads
                                 if 10 in x["rungs"] and 10 not in x["mcc_admissible_K"]],
                "ladders": lads,
            }
        q2[join] = res
    out["q2_mcb"] = q2

    # ---------------- Q3: § 8.6 ----------------
    q3: dict = {}
    for join in JOINS:
        cons = consensus["per_join"][join]
        tier = tiering_of(root, join, "tier-e", None, 20)
        refs = {int(re.search(r"-k(\d+)-", r["ref"]).group(1)): r["ref"]
                for r in tier["ranking"]}
        as_eval = oriented_pair(tier, refs[1], refs[10])
        clip_t = tiering_of(root, join, "clipped-mcc-test", "d51clip-tier-e", 20)
        crefs = {int(re.search(r"-k(\d+)-", r["ref"]).group(1)): r["ref"]
                 for r in clip_t["ranking"]}
        clip = oriented_pair(clip_t, crefs[1], crefs[10])
        c_delta = cons["delta_mcc_k1_to_k10"]
        q3[join] = {
            "consensus_only": {"mcc_k1": cons["rungs"]["1"]["mcc"],
                               "mcc_k10": cons["rungs"]["10"]["mcc"],
                               "delta": c_delta},
            "verified_as_evaluated": as_eval,
            "verified_d51_clipped": clip,
            "swing_as_evaluated": round(c_delta - as_eval["delta"], 6),
            "swing_clipped": round(c_delta - clip["delta"], 6),
            "sign_reversal_as_evaluated": c_delta > 0 > as_eval["delta"],
            "sign_reversal_clipped": c_delta > 0 > clip["delta"],
        }
    out["q3_section_8_6"] = q3

    # ---------------- Q4: the mechanism diagnostic ----------------
    mech = load(root / R / "mechanism/id-join-mechanism.json")
    id_mcc: dict[str, float] = {}
    join_mcc: dict[str, dict[str, float]] = {j: {} for j in JOINS}
    for join in JOINS:
        for _, gdir in groups:
            for path in (root / R / join / gdir / "tiering").glob("*/tiering_*.json"):
                for row in load(path)["mcc_permutation"]["ranking"]:
                    join_mcc[join][f"{path.parent.name}|{row['ref']}"] = row["mcc"]
        for row in tiering_of(root, join, "tier-e", None, 20)["mcc_permutation"]["ranking"]:
            join_mcc[join][f"tier-e|{row['ref']}"] = row["mcc"]
    id_mcc = join_mcc["id"]
    q4_lads = []
    crosscheck_bad = []
    pooled = {"fn": 0, "inside": 0}
    for lad in mech["ladders"]:
        rungs = []
        for r in lad["rungs"]:
            key = f"{lad['slug']}|{r['ref']}"
            if "withheld" in r:
                rungs.append(r)
                continue
            if key in id_mcc and round(r["mcc_id"], 4) != round(id_mcc[key], 4):
                crosscheck_bad.append({"key": key, "mechanism": r["mcc_id"],
                                       "tiering": id_mcc[key]})
            pooled["fn"] += r["fn"]
            pooled["inside"] += r["fn_with_detection_inside"]
            rungs.append({"K": r["K"], "fn": r["fn"],
                          "fn_with_detection_inside": r["fn_with_detection_inside"],
                          "share": r["share"], "n_detections": r["n_detections"],
                          "mcc": {j: join_mcc[j].get(key) for j in JOINS}})
        shares = [x["share"] for x in rungs if x.get("share") is not None]
        scored = [x for x in rungs if "fn" in x]
        first, top = scored[0], scored[-1]

        def gain(rung: dict, join: str) -> float | None:
            """The rung's MCC under a geometric join minus its id MCC."""
            a, b = rung["mcc"].get(join), rung["mcc"].get("id")
            return None if a is None or b is None else round(a - b, 6)

        q4_lads.append({
            "slug": lad["slug"], "group": lad["group"], "n_tiles": lad["n_tiles"],
            "rungs": rungs,
            "share_k1": shares[0] if shares else None,
            "share_top_k": shares[-1] if shares else None,
            "share_change_k1_to_top": (round(shares[-1] - shares[0], 6)
                                       if len(shares) > 1 else None),
            "monotone_rising": all(b >= a for a, b in zip(shares, shares[1:])),
            "monotone_falling": all(b <= a for a, b in zip(shares, shares[1:])),
            "fn_k1": first["fn"], "fn_top_k": top["fn"],
            "n_detections_k1": first["n_detections"],
            "n_detections_top_k": top["n_detections"],
            "inside_k1": first["fn_with_detection_inside"],
            "inside_top_k": top["fn_with_detection_inside"],
            "join_gain_k1": {j: gain(first, j) for j in GEOMETRIC},
            "join_gain_top_k": {j: gain(top, j) for j in GEOMETRIC},
        })
    main_lads = [x for x in q4_lads if x["group"] != "clipped"]
    out["q4_mechanism"] = {
        "crosscheck_against_id_tierings": {"n_mismatches": len(crosscheck_bad),
                                           "mismatches": crosscheck_bad},
        "pooled_22_ladders_as_evaluated": {
            "fn_tiles": sum(r["fn"] for x in main_lads for r in x["rungs"] if "fn" in r),
            "with_detection_inside": sum(r["fn_with_detection_inside"]
                                         for x in main_lads for r in x["rungs"]
                                         if "fn" in r)},
        "ladders_share_higher_at_top_K_than_K1": [
            x["slug"] for x in main_lads
            if (x["share_change_k1_to_top"] or 0) > 0],
        "ladders_share_lower_at_top_K_than_K1": [
            x["slug"] for x in main_lads
            if (x["share_change_k1_to_top"] or 0) < 0],
        "ladders": q4_lads,
    }
    p = out["q4_mechanism"]["pooled_22_ladders_as_evaluated"]
    p["share"] = round(p["with_detection_inside"] / p["fn_tiles"], 6)

    def k_tallies(sel: list[dict]) -> dict:
        """From K = 1 to the top rung: how many ladders' counts rise or fall."""
        def ups(key_lo: str, key_hi: str) -> dict:
            return {"rise": sum(x[key_hi] > x[key_lo] for x in sel),
                    "fall": sum(x[key_hi] < x[key_lo] for x in sel),
                    "same": sum(x[key_hi] == x[key_lo] for x in sel)}
        out_t = {"n": len(sel),
                 "n_detections": ups("n_detections_k1", "n_detections_top_k"),
                 "fn_tiles": ups("fn_k1", "fn_top_k"),
                 "fn_tiles_holding_a_detection": ups("inside_k1", "inside_top_k"),
                 "share": ups("share_k1", "share_top_k")}
        for j in GEOMETRIC:
            out_t[f"join_gain_larger_at_top_k_{j}"] = sum(
                x["join_gain_top_k"][j] > x["join_gain_k1"][j] for x in sel)
        return out_t

    gs = [x for x in main_lads if x["n_tiles"] < 1000]
    dep = [x for x in main_lads if x["n_tiles"] >= 1000]
    out["q4_mechanism"]["k1_to_top_k"] = {
        "gold_standard_frame_ladders": k_tallies(gs),
        "deployment_55map_ladders": k_tallies(dep),
        "all_22": k_tallies(main_lads),
    }

    (root / R / "summary.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"gate all passed: {out['gate']['all_passed']}")
    for name, g in gates.items():
        bad = {k: {kind: v[kind][:3] for kind in ("value", "missing", "order")
                   if v[kind]}
               for k, v in g.get("files", {}).items()
               if v["value"] or v["missing"] or v["order"]}
        print(f"  {name}: {'PASS' if g['passed'] else 'FAIL'} "
              f"({g.get('n_files_compared', g.get('n_rows_replayed'))} compared; "
              f"added keys: {len(g.get('schema_additions', []))}) {bad or ''}")
    return 0 if out["gate"]["all_passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
