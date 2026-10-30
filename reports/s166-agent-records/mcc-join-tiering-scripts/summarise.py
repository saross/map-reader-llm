#!/usr/bin/env python3
"""
Gate, compare and summarise the Era-2 board's MCC family under three tile joins.

Part of the S166 MCC robustness job, part (b)
(``reports/s166-agent-records/mcc-join-tiering.md``). Reads the outputs of
``chain.sh`` and the committed board, and writes:

* ``summary.json`` — the reproduction gate (the default-join run against the
  committed ``tiering_20m.json`` and MCC MCB), the per-join table, the five
  claim checks, the independent cross-check against the 2026-09-12 tile-join
  audit, and the three withheld cells' MCC under each geometric join;
* ``mcc-family-<join>.json`` for each geometric join — the run's
  ``mcc_permutation`` block with its run metadata (the F1 side is not copied:
  it is checked identical to the default run's and recorded as such);
* ``mcb/`` — the geometric joins' MCC MCB artefacts, copied verbatim;
* ``README.md`` — the tables, rendered from ``summary.json`` only.

Nothing in the board or the register is written.

Usage: python summarise.py <clone_root> <chain_out_dir> <results_dir>

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import geopandas as gpd
from scipy.stats import spearmanr

BOARD_ID = "gs-era2-verified-board-2026-09-10"
BOARD = f"results/leaderboard/era2/{BOARD_ID}"
JOINS = ("id", "geometric-primary", "geometric-contains")
GEOMETRIC = JOINS[1:]
#: The register row's named MCC leader (results/run-analyses.json, row
#: gs-era2-verified-board-2026-09-10, `outcome`: "MCC Tier 1 = 34 cell(s)
#: (verified-adv-image-baseline-pro-vf-era2b MCC 0.8887; ...").
REGISTER_MCC_LEADER = "pv-diag-384::verified-adv-image-baseline-pro-vf-era2b"
#: The ten members the S164 restatement re-scored after the 2026-09-12 audit
#: (reports/s164-agent-records/restatement-pass-scripts/board_chain.sh, MOVED).
MOVED_SINCE_AUDIT = {
    "gemini37-image-gs-2026-09-01__g37-image-k5-verified-carried-p0_10-k5",
    "gemini37-image-gs-2026-09-01__g37-image-k5-verified-swap37-p0_90-k5",
    "gemini37-screen-2026-08-28__g37-text-k10-verified-carried-p0_10-k10",
    "gemini37-screen-2026-08-28__g37-text-k5-verified-carried-p0_10-k5",
    "gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5",
    "gemini37-screen-2026-08-28__g37-text-k5-verified-swap38-p0_88-k5",
    "grid-2026-08-18__g384-ov192-k10-verified37-p0_98-k10",
    "grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10",
    "image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8",
    "image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9",
}
#: Run metadata that legitimately differs between two runs of one board.
VOLATILE = {"generated_at_utc", "git_commit"}


def load(path: Path) -> Any:
    """Read one JSON file."""
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    """Hex digest of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tiering_path(out: Path, join: str) -> Path:
    """Where chain.sh's tiering run for ``join`` wrote its JSON."""
    stem = "tiering_20m" if join == "id" else f"tiering_20m_{join}"
    return out / "tiering" / join / f"{stem}.json"


def mcb_path(out: Path, metric: str, join: str = "id") -> Path:
    """Where chain.sh's MCB run wrote its JSON."""
    suffix = "" if metric == "f1" else "_mcc"
    if join != "id":
        suffix += f"_{join}"
    return out / "mcb" / f"{BOARD_ID}{suffix}_b20_m1.json"


def admissible(mcb: dict) -> list[str]:
    """The Hsu (constrained one-sided) MCB admissible refs, in candidate order."""
    kept = mcb["kept_indices"]
    return [mcb["candidates"][kept[i]]["ref"] for i in mcb["hsu_not_ruled_out"]]


def tracks(clone: Path, refs: list[str]) -> tuple[dict[str, str], dict[str, Any]]:
    """Each cell's proposer track (image or text), and how it was derived.

    The board membership records ``track`` from the transmitted proposer
    configuration (erratum E88, ``membership.json``) for its 110 members. The
    -opmax rows of the archived Era-2 PV board are not in that file, so they
    take the track of a member sharing their ``proposer_pool`` (every pool
    present in the membership maps to exactly one track — checked here), and a
    pool absent from the membership is read from its name. The rule and its
    counts are returned so the record can state them.
    """
    rc = load(clone / "results/run-conditions.json")["decomposition"]
    members = {m["condition_id"]: m for m in load(clone / BOARD / "membership.json")["members"]}

    def base(ref: str) -> str:
        return ref[:-len("-era2b")] if ref.endswith("-era2b") else ref

    pool_of: dict[str, str] = {}
    for ref in refs:
        run, label = ref.split("::", 1)
        cond = next(c for c in rc[run]["conditions"] if c["label"] == label)
        pool_of[ref] = cond["proposer_pool"]
    pool_track: dict[str, set[str]] = {}
    for ref in refs:
        member = members.get(base(ref))
        if member and member.get("track"):
            pool_track.setdefault(pool_of[ref], set()).add(member["track"])
    conflicts = {p: sorted(t) for p, t in pool_track.items() if len(t) > 1}
    if conflicts:
        raise ValueError(f"proposer pools with two tracks: {conflicts}")
    out: dict[str, str] = {}
    basis = {"membership": 0, "pool-sibling": 0, "pool-name": 0}
    by_name: dict[str, str] = {}
    for ref in refs:
        member = members.get(base(ref))
        if member and member.get("track"):
            out[ref] = member["track"]
            basis["membership"] += 1
        elif pool_of[ref] in pool_track:
            out[ref] = next(iter(pool_track[pool_of[ref]]))
            basis["pool-sibling"] += 1
        else:
            pool = pool_of[ref]
            out[ref] = "image" if ("image" in pool or "scale-4" in pool) else "text"
            basis["pool-name"] += 1
            by_name[ref] = f"{pool} -> {out[ref]}"
    return out, {"basis_counts": basis, "by_pool_name": by_name}


def spearman(a: dict[str, float], b: dict[str, float], refs: list[str]) -> float:
    """Spearman's rho between two MCC readings over ``refs`` (ties averaged)."""
    rho = spearmanr([a[r] for r in refs], [b[r] for r in refs]).statistic
    return round(float(rho), 4)


def audit_crosscheck(clone: Path, runs: dict[str, dict]) -> dict[str, Any]:
    """Compare the rebuilt confusions with the 2026-09-12 tile-join audit.

    The audit (``scripts/audit_tile_join_variants.py``) computed every board
    cell's confusion under all three joins on 2026-09-12, independently of the
    tiering harness. Cells whose inputs have not changed since must agree
    exactly under every join; the S164 restatement re-scored ten board cells and
    the K-ladder cells afterwards, so those may differ and are reported apart.
    """
    rc = load(clone / "results/run-conditions.json")["decomposition"]
    eval_to_ref: dict[str, str] = {}
    for ref in runs["id"]["mcc_permutation"]["gates"]:
        run, label = ref.split("::", 1)
        cond = next(c for c in rc[run]["conditions"] if c["label"] == label)
        eval_to_ref[cond["eval_path"]] = ref
    result: dict[str, Any] = {}
    for name in ("board-era2-2026-09-12.json", "k-ladder-phase2-cells-2026-09-12.json"):
        audit = load(clone / "results/tile-join-audit" / name)
        per_join = {j: {"equal": 0, "differ": [], "refused_in_audit": 0} for j in JOINS}
        n_matched = 0
        for cell in audit["cells"]:
            ref = eval_to_ref.get(cell["evaluation"])
            if ref is None:
                continue
            n_matched += 1
            for join in JOINS:
                audited = cell["joins"][join]
                if audited.get("refused"):
                    per_join[join]["refused_in_audit"] += 1
                    continue
                rebuilt = runs[join]["mcc_permutation"]["gates"][ref]["confusion"]
                if rebuilt == audited["confusion"]:
                    per_join[join]["equal"] += 1
                else:
                    per_join[join]["differ"].append({
                        "ref": ref, "audit_label": cell["label"],
                        "moved_since_audit": cell["label"] in MOVED_SINCE_AUDIT,
                        "audit": audited["confusion"], "rebuilt": rebuilt,
                    })
        result[name] = {"n_audit_cells": audit["n_cells"],
                        "n_matched_to_board_cells": n_matched, "joins": per_join}
    return result


def withheld_geometric(clone: Path, run_id: dict) -> list[dict[str, Any]]:
    """The three withheld cells' tile confusion and MCC under each geometric join.

    They are withheld on the F1 arm (the per-tile F1 table refuses their
    vocabulary under the published join) and so are outside every family here.
    Their geometric MCC is computed for disclosure only — where they would
    stand if the PI admitted them — and is not entered into any family.
    """
    sys.path.insert(0, str(clone / "scripts"))
    import era1_leaderboard_tiering as t  # noqa: PLC0415
    from lib_advanced_metrics import calculate_tile_classification  # noqa: PLC0415

    rc = load(clone / "results/run-conditions.json")["decomposition"]
    bounds = gpd.read_file(clone / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson")
    bounds = bounds.to_crs(t.TARGET_CRS)
    refs = gpd.read_file(
        clone / "inputs/vectors/references/mounds-reference.geojson").to_crs(t.TARGET_CRS)
    out = []
    for w in run_id["withheld_cells"]:
        run, label = w["ref"].split("::", 1)
        cond = next(c for c in rc[run]["conditions"] if c["label"] == label)
        meta = load(clone / cond["eval_path"])["_metadata"]
        cli = dict(meta.get("cli_args") or {})
        det = t.cell_detections(cli, bounds)
        row: dict[str, Any] = {"ref": w["ref"], "eval_f1": w["eval_f1"],
                               "eval_path": cond["eval_path"]}
        for join in JOINS:
            res = calculate_tile_classification(det, refs, bounds, tile_join=join)
            if "error" in res:
                row[join] = {"refused": True, "reason": res.get("reason")}
            else:
                row[join] = {"confusion": {k: int(res[k]) for k in ("tp", "tn", "fp", "fn")},
                             "mcc": round(float(res["mcc"]), 4)}
        out.append(row)
    return out


def short(ref: str) -> str:
    """A board ref without its run prefix, for tables."""
    return ref.split("::", 1)[1]


def render_readme(s: dict[str, Any]) -> str:
    """Render the results directory's README from ``summary.json`` alone.

    Every figure in the document comes from ``s``; the prose around the tables
    is fixed. Interpretation is left to the agent record that cites this
    directory (``reports/s166-agent-records/mcc-join-tiering.md``).
    """
    g, pj, cl = s["gate"], s["per_join"], s["claims"]
    cols = " | ".join(f"`{j}`" for j in JOINS)
    rule = "|---|" + "---:|" * len(JOINS)

    def row(label: str, values: list[Any]) -> str:
        return f"| {label} | " + " | ".join(str(v) for v in values) + " |"

    def yn(flag: bool) -> str:
        return "yes" if flag else "no"

    lines = [
        "# Era-2 board: tile-MCC tiering under three tile joins",
        "",
        "> **Last revised**: 2026-10-30 (original publication). See "
        "[§ Changelog](#changelog) for revision history.",
        "",
        "A **sensitivity reading** of the gold-standard (GS) Era-2 verified board's "
        "tile-level Matthews Correlation Coefficient (MCC) family "
        f"(`{BOARD}/`). The board publishes its MCC permutation family and its MCC "
        "Multiple Comparisons with the Best (MCB) admissible set under the name-based "
        "`id` tile join, the published convention (S153 ruling 6). Here both are "
        "rebuilt under that join (the reproduction gate) and under the two geometric "
        "joins of `reports/tile-mcc-geometric-join-2026-09-12.md` § 2. Only the MCC "
        "arm changes: the F1 tiering, its tiers and its three withheld cells are the "
        "board's own in all three runs. Nothing in the board, the register or any "
        "findings document was written.",
        "",
        f"Instruments: `{s['instrument']['tiering']}` "
        f"({s['instrument']['tiering_settings']}) and `{s['instrument']['mcb']}` "
        f"({s['instrument']['mcb_settings']}). "
        f"Membership: `{s['instrument']['analyses']}` (150 tiered cells, 487 tiles). "
        f"Computed at commit `{s['computed_at_commit']['id']}` on sapphire. "
        "Machine-readable record: `summary.json`; each geometric join's MCC family: "
        "`mcc-family-<join>.json`; its MCC MCB: `mcb/`.",
        "",
        "## 1. Reproduction gate (`id` join)",
        "",
        "| Quantity | Committed | This run | Equal |",
        "|---|---:|---:|:---:|",
        f"| F1 pairs significant | 8075 of 11175 | {g['f1']['n_significant']} of "
        f"{g['f1']['n_pairs']} | {yn(g['f1']['n_significant'] == 8075)} |",
        f"| F1 tiers | 14 | {g['f1']['n_tiers']} | {yn(g['f1']['n_tiers'] == 14)} |",
        f"| F1 Tier 1 (the same five cells, same order) | 5 | {len(g['f1']['tie_set'])} | "
        f"{yn(g['f1']['tie_set_equals_committed'])} |",
        f"| MCC pairs significant | 3001 of 11175 | {g['mcc']['n_significant']} of "
        f"{g['mcc']['n_pairs']} | {yn(g['mcc']['n_significant'] == 3001)} |",
        f"| MCC tiers | 6 | {g['mcc']['n_tiers']} | {yn(g['mcc']['n_tiers'] == 6)} |",
        f"| MCC Tier 1 | 34 | {g['mcc']['tie_set_size']} | "
        f"{yn(g['mcc']['tie_set_equals_committed'])} |",
        f"| whole `mcc_permutation` block | — | — | {yn(g['mcc']['block_equals_committed'])} |",
        f"| tiering JSON keys differing beyond `generated_at_utc`, `git_commit` | — | "
        f"{len(g['tiering_keys_differing_beyond_run_metadata'])} | "
        f"{yn(not g['tiering_keys_differing_beyond_run_metadata'])} |",
        f"| F1 MCB admissible set | 52 | {g['mcb']['f1']['admissible_size']} | "
        f"{yn(g['mcb']['f1']['admissible_equals_committed'])} |",
        f"| MCC MCB admissible set | 60 | {g['mcb']['mcc']['admissible_size']} | "
        f"{yn(g['mcb']['mcc']['admissible_equals_committed'])} |",
        f"| F1 MCB artefact byte-identical | — | — | {yn(g['mcb']['f1']['byte_identical'])} |",
        f"| MCC MCB artefact byte-identical | — | — | {yn(g['mcb']['mcc']['byte_identical'])} |",
        f"| join-aware MCB builder under `id` = default derivation | — | — | "
        f"{yn(g['builder_id_check']['passed'])} |",
        "",
        f"**Gate: {'PASSED' if g['passed'] else 'FAILED'}.**",
        "",
        "## 2. Per-join MCC family",
        "",
        f"| | {cols} |",
        rule,
        row("MCC pairs significant (BH q 0.05, of 11,175)",
            [pj[j]["n_significant"] for j in JOINS]),
        row("MCC tiers", [pj[j]["n_tiers"] for j in JOINS]),
        row("MCC Tier 1 (tie set) size", [pj[j]["tier1_size"] for j in JOINS]),
        row("MCC MCB admissible (Hsu), of 150",
            [pj[j]["mcb_admissible_size"] for j in JOINS]),
        row("top MCC cell", [f"`{short(pj[j]['top_cell']['ref'])}`" for j in JOINS]),
        row("— its tile-MCC", [f"{pj[j]['top_cell']['mcc']:.4f}" for j in JOINS]),
        row("— its track; F1 tier",
            [f"{pj[j]['top_cell']['track']}; {pj[j]['top_cell']['f1_tier']}" for j in JOINS]),
        row("Spearman of MCC vs `id`, 150 cells",
            [f"{pj[j]['spearman_vs_id_150']:.4f}" for j in JOINS]),
        row(f"Spearman of MCC vs `id`, the {pj['id']['n_cells_dir']} `cells/` cells",
            [f"{pj[j]['spearman_vs_id_cells_dir']:.4f}" for j in JOINS]),
        row("mean ΔMCC vs `id` (min … max)",
            [f"{pj[j]['delta_mcc_vs_id']['mean']:+.4f} ({pj[j]['delta_mcc_vs_id']['min']:+.4f}"
             f" … {pj[j]['delta_mcc_vs_id']['max']:+.4f})" for j in JOINS]),
        row("cells higher / lower than under `id`",
            [f"{pj[j]['delta_mcc_vs_id']['n_higher']} / {pj[j]['delta_mcc_vs_id']['n_lower']}"
             for j in JOINS]),
        row("MCC MCB argmax stability (distinct winners)",
            [f"{pj[j]['argmax_stability']:.4f} ({pj[j]['n_distinct_argmax']})" for j in JOINS]),
        "",
        "The 2026-09-12 audit's own Spearman figures, recomputed from "
        "`results/tile-join-audit/board-era2-2026-09-12.json` (103 cells, before the "
        "S164 restatement): "
        + ", ".join(f"`{j}` {v:.4f}" for j, v in
                    s["s165_spearman_recomputed_from_2026_09_12_audit"].items())
        + ".",
        "",
        "## 3. Claim checks",
        "",
        f"| Claim | {cols} |",
        rule,
        row("(i) top F1 cell in MCC Tier 1",
            [yn(cl["i"][j]["in_mcc_tier1"]) for j in JOINS]),
        row("— its MCC rank / MCC tier",
            [f"{cl['i'][j]['mcc_rank']} / {cl['i'][j]['mcc_tier']}" for j in JOINS]),
        row("— MCC-admissible", [yn(cl["i"][j]["mcc_admissible"]) for j in JOINS]),
        row("(ii) F1 Tier-1 cells in MCC Tier 1, of 5",
            [cl["ii"][j]["n_in_mcc_tier1"] for j in JOINS]),
        row("— their MCC ranks",
            [", ".join(str(r) for r in cl["ii"][j]["mcc_ranks"]) for j in JOINS]),
        row("(iii) F1-admissible ∩ MCC-admissible",
            [f"{cl['iii'][j]['both']} of {cl['iii'][j]['f1_admissible']} and "
             f"{cl['iii'][j]['mcc_admissible']}" for j in JOINS]),
        row("— union / F1-only / MCC-only",
            [f"{cl['iii'][j]['union']} / {cl['iii'][j]['f1_only']} / "
             f"{cl['iii'][j]['mcc_only']}" for j in JOINS]),
        row("— top MCC cell F1-admissible",
            [yn(cl["iii"][j]["top_mcc_cell_f1_admissible"]) for j in JOINS]),
        row("(iv) top MCC cell's track", [cl["iv"][j]["top_cell_track"] for j in JOINS]),
        row("— image cells in the MCC top 10",
            [cl["iv"][j]["n_image_in_top10"] for j in JOINS]),
        row("— MCC Tier 1 image / text",
            [f"{cl['iv'][j]['tier1_by_track']['image']} / "
             f"{cl['iv'][j]['tier1_by_track']['text']}" for j in JOINS]),
        row("— MCC-admissible image / text",
            [f"{cl['iv'][j]['mcb_admissible_by_track']['image']} / "
             f"{cl['iv'][j]['mcb_admissible_by_track']['text']}" for j in JOINS]),
        row("— median MCC rank, image / text",
            [f"{cl['iv'][j]['median_mcc_rank']['image']:g} / "
             f"{cl['iv'][j]['median_mcc_rank']['text']:g}" for j in JOINS]),
        row("(v) register's MCC leader is the top MCC cell",
            [yn(cl["v"][j]["is_top"]) for j in JOINS]),
        row("— its MCC, rank, MCC tier",
            [f"{cl['v'][j]['mcc']:.4f}, {cl['v'][j]['mcc_rank']}, {cl['v'][j]['mcc_tier']}"
             for j in JOINS]),
        row("— in MCC Tier 1 / MCC-admissible",
            [f"{yn(cl['v'][j]['in_mcc_tier1'])} / {yn(cl['v'][j]['mcc_admissible'])}"
             for j in JOINS]),
        "",
        f"The top F1 cell is `{short(cl['i']['id']['top_f1_cell'])}`; the register's MCC "
        f"leader (row `{BOARD_ID}`, `outcome`) is `{short(REGISTER_MCC_LEADER)}`. "
        f"Board composition by proposer track: {cl['iv']['id']['board_by_track']['image']} "
        f"image, {cl['iv']['id']['board_by_track']['text']} text (derivation in "
        "`summary.json` → `track_derivation`).",
        "",
        "## 4. MCC Tier 1 under each join",
        "",
    ]
    for join in JOINS:
        members = pj[join]["tier1"]
        lines += [f"**`{join}`** ({len(members)} cells): "
                  + ", ".join(f"`{short(r)}`" for r in members) + ".", ""]
    lines += [
        "## 5. Cross-checks",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    for join in GEOMETRIC:
        gc = s["geometric_run_checks"][join]
        lines.append(
            f"| `{join}`: F1 side identical to the `id` run; MCC gates passed; "
            f"MCC withheld; MCB candidate set equal | {yn(gc['f1_side_equals_default_run'])}; "
            f"{gc['n_gates_passed']} of {gc['n_cells_with_mcc']}; {gc['n_mcc_withheld']}; "
            f"{yn(gc['mcb_candidates_equal_default'])} |")
    for name, ac in s["audit_crosscheck"].items():
        cells = "; ".join(
            f"`{j}` {ac['joins'][j]['equal']} equal, {len(ac['joins'][j]['differ'])} differ"
            + (f" ({sum(1 for d in ac['joins'][j]['differ'] if d['moved_since_audit'])}"
               " re-scored since)" if ac["joins"][j]["differ"] else "")
            + (f", {ac['joins'][j]['refused_in_audit']} refused in the audit"
               if ac["joins"][j]["refused_in_audit"] else "")
            for j in JOINS)
        lines.append(f"| confusions against `results/tile-join-audit/{name}` "
                     f"({ac['n_matched_to_board_cells']} board cells matched) | {cells} |")
    rt = s["reference_positive_tiles_per_join"]
    lines.append("| reference-positive tiles (TP + FN), one value per join across "
                 "all cells | " + "; ".join(f"`{j}` {rt[j]}" for j in JOINS) + " |")
    lines += [
        "",
        "**The three withheld cells** stay withheld in every run: the per-tile F1 "
        "table refuses their vocabulary under the published join, which the F1 arm "
        "keeps. Their MCC under each join, computed for disclosure only and entered "
        "into no family:",
        "",
        f"| cell | F1@20 | {cols} |",
        "|---|---:|" + "---:|" * len(JOINS),
    ]
    for w in s["withheld_cells_geometric"]:
        vals = ["refused" if w[j].get("refused") else f"{w[j]['mcc']:.4f}" for j in JOINS]
        lines.append(f"| `{short(w['ref'])}` | {w['eval_f1']:.4f} | " + " | ".join(vals) + " |")
    tb = s["track_derivation"]["basis_counts"]
    lines += [
        "",
        "**Track (claim iv).** A cell's track is its proposer's transmitted modality: "
        f"the board membership's `track` field (E88) for {tb['membership']} cells; the "
        f"track of a member sharing the same `proposer_pool` for {tb['pool-sibling']} "
        "-opmax rows (every pool in the membership maps to one track, checked); the "
        f"pool's name for {tb['pool-name']}.",
        "",
        "**Diagnostic files** (used by no table above; written by "
        "`id_join_mechanism.py` and `mechanism_summary.py` in "
        "`reports/s166-agent-records/mcc-join-tiering-scripts/`): "
        "`id-join-mechanism.json` counts, per cell, the false-negative tiles under "
        "`id` that geometrically contain one of the cell's detections, and "
        "`id-join-mechanism-summary.json` aggregates them.",
        "",
        "## Changelog",
        "",
        "### 2026-10-30 — Original publication",
        "",
        "First publication, by the S166 MCC robustness job, part (b), on branch "
        "`mcc-join-tiering-2026-10-30`. The record, with the reading of these tables, "
        "is `reports/s166-agent-records/mcc-join-tiering.md`.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    """Run every comparison and write the results directory."""
    clone, out, results = (Path(p) for p in sys.argv[1:4])
    results.mkdir(parents=True, exist_ok=True)
    committed = load(clone / BOARD / "tiering_20m.json")
    runs = {j: load(tiering_path(out, j)) for j in JOINS}
    mcb_committed = {
        "f1": clone / BOARD / "mcb" / f"{BOARD_ID}_b20_m1.json",
        "mcc": clone / BOARD / "mcb" / f"{BOARD_ID}_mcc_b20_m1.json",
    }
    mcb_runs = {"f1": mcb_path(out, "f1"), **{j: mcb_path(out, "mcc", j) for j in JOINS}}
    mcb = {k: load(p) for k, p in mcb_runs.items()}

    # --- 1. The reproduction gate (default join) ----------------------------
    run_id = runs["id"]
    differing = sorted(k for k in set(committed) | set(run_id)
                       if k not in VOLATILE and committed.get(k) != run_id.get(k))
    mcc_c, mcc_r = committed["mcc_permutation"], run_id["mcc_permutation"]
    gate = {
        "tiering_keys_differing_beyond_run_metadata": differing,
        "f1": {
            "n_significant": sum(r["significant"] for r in run_id["pairwise"]),
            "n_pairs": len(run_id["pairwise"]),
            "n_tiers": len(run_id["tiers"]),
            "tie_set": run_id["tie_set"],
            "tie_set_equals_committed": run_id["tie_set"] == committed["tie_set"],
            "expected": {"n_significant": 8075, "n_pairs": 11175, "n_tiers": 14},
        },
        "mcc": {
            "n_significant": mcc_r["n_significant"], "n_pairs": mcc_r["n_pairs"],
            "n_tiers": mcc_r["n_tiers"], "tie_set_size": len(mcc_r["tie_set"]),
            "tie_set_equals_committed": mcc_r["tie_set"] == mcc_c["tie_set"],
            "block_equals_committed": mcc_r == mcc_c,
            "expected": {"n_significant": 3001, "n_pairs": 11175, "n_tiers": 6,
                         "tie_set_size": 34},
        },
        "mcb": {
            metric: {
                "sha256_run": sha256(mcb_runs[metric if metric == "f1" else "id"]),
                "sha256_committed": sha256(mcb_committed[metric]),
                "admissible_size": len(admissible(mcb[metric if metric == "f1" else "id"])),
                "admissible_equals_committed": admissible(
                    mcb[metric if metric == "f1" else "id"]
                ) == admissible(load(mcb_committed[metric])),
            }
            for metric in ("f1", "mcc")
        },
        "builder_id_check": load(out / "builder-id-check.json"),
        "withheld_refs": [w["ref"] for w in run_id["withheld_cells"]],
    }
    for metric in ("f1", "mcc"):
        g = gate["mcb"][metric]
        g["byte_identical"] = g["sha256_run"] == g["sha256_committed"]
    gate["mcb"]["expected"] = {"f1": 52, "mcc": 60}
    gate["passed"] = (
        not differing
        and gate["f1"]["n_significant"] == 8075 and gate["f1"]["n_tiers"] == 14
        and gate["f1"]["tie_set_equals_committed"]
        and mcc_r["n_significant"] == 3001 and mcc_r["n_tiers"] == 6
        and len(mcc_r["tie_set"]) == 34 and gate["mcc"]["block_equals_committed"]
        and gate["mcb"]["f1"]["admissible_size"] == 52
        and gate["mcb"]["mcc"]["admissible_size"] == 60
        and gate["mcb"]["f1"]["admissible_equals_committed"]
        and gate["mcb"]["mcc"]["admissible_equals_committed"]
        and gate["builder_id_check"]["passed"]
    )

    # --- 2. The geometric runs keep the F1 side and gate every MCC cell -----
    f1_keys = ("ranking", "tiers", "tie_set", "pairwise", "withheld_cells", "n_cells",
               "n_cells_withheld", "n_tiles")
    geometric_checks = {}
    for join in GEOMETRIC:
        block = runs[join]["mcc_permutation"]
        geometric_checks[join] = {
            "f1_side_equals_default_run": all(runs[join][k] == run_id[k] for k in f1_keys),
            "tile_join_recorded": block.get("tile_join"),
            "n_cells_with_mcc": block["n_cells_with_mcc"],
            "n_mcc_withheld": block["n_cells_withheld"],
            "n_gates_passed": sum(1 for g in block["gates"].values() if g and g.get("passed")),
            "mcb_candidates_equal_default": [c["ref"] for c in mcb[join]["candidates"]]
            == [c["ref"] for c in mcb["id"]["candidates"]],
        }

    # --- 3. Per-join table ---------------------------------------------------
    refs = [row["ref"] for row in run_id["mcc_permutation"]["ranking"]]
    track, track_basis = tracks(clone, refs)
    mcc = {j: {row["ref"]: row["mcc"] for row in runs[j]["mcc_permutation"]["ranking"]}
           for j in JOINS}
    rank = {j: {row["ref"]: row["rank"] for row in runs[j]["mcc_permutation"]["ranking"]}
            for j in JOINS}
    tier = {j: {row["ref"]: row["mcc_tier"] for row in runs[j]["mcc_permutation"]["ranking"]}
            for j in JOINS}
    # The 103 cells the board re-scored into its own cells/ directory — the set
    # the 2026-09-12 audit and the S165 Spearman figures cover.
    rc = load(clone / "results/run-conditions.json")["decomposition"]
    cells_dir_refs = []
    for r in refs:
        run, label = r.split("::", 1)
        cond = next(c for c in rc[run]["conditions"] if c["label"] == label)
        if cond["eval_path"].startswith(f"{BOARD}/cells/"):
            cells_dir_refs.append(r)
    f1_tier1 = committed["tie_set"]
    top_f1 = committed["ranking"][0]["ref"]
    f1_adm = set(admissible(mcb["f1"]))
    per_join = {}
    for join in JOINS:
        block = runs[join]["mcc_permutation"]
        tie = block["tie_set"]
        adm = admissible(mcb[join])
        top = block["ranking"][0]
        delta = [mcc[join][r] - mcc["id"][r] for r in refs]
        per_join[join] = {
            "n_pairs": block["n_pairs"],
            "n_significant": block["n_significant"],
            "n_tiers": block["n_tiers"],
            "tier_sizes": [len(t["members"]) for t in block["tiers"]],
            "tier1": tie,
            "tier1_size": len(tie),
            "mcb_admissible": adm,
            "mcb_admissible_size": len(adm),
            "mcb_two_sided_band_size": len(mcb[join]["mcb_not_ruled_out"]),
            "mcb_selected": mcb[join]["candidates"][
                mcb[join]["kept_indices"][mcb[join]["selected_index"]]]["ref"],
            "mcb_apparent": round(mcb[join]["apparent_f1"], 4),
            "argmax_stability": mcb[join]["argmax_stability"],
            "n_distinct_argmax": mcb[join]["n_distinct_argmax"],
            "top_cell": {"ref": top["ref"], "mcc": top["mcc"], "track": track[top["ref"]],
                         "f1_tier": top.get("f1_tier"), "eval_f1": top["eval_f1"]},
            "top10": [{"ref": r["ref"], "mcc": r["mcc"], "track": track[r["ref"]],
                       "f1_tier": r.get("f1_tier")} for r in block["ranking"][:10]],
            "spearman_vs_id_150": spearman(mcc[join], mcc["id"], refs),
            "spearman_vs_id_cells_dir": spearman(mcc[join], mcc["id"], cells_dir_refs),
            "n_cells_dir": len(cells_dir_refs),
            "delta_mcc_vs_id": {
                "mean": round(sum(delta) / len(delta), 4),
                "min": round(min(delta), 4), "max": round(max(delta), 4),
                "n_higher": sum(1 for d in delta if d > 0),
                "n_lower": sum(1 for d in delta if d < 0),
            },
        }

    # The S165 figures (Spearman 0.85 / 0.77 over 103 cells) were read from the
    # 2026-09-12 audit; recompute them there so the brief's anchor is checked.
    audit = load(clone / "results/tile-join-audit/board-era2-2026-09-12.json")
    a_mcc = {j: {c["label"]: c["joins"][j]["mcc"] for c in audit["cells"]} for j in JOINS}
    a_labels = [c["label"] for c in audit["cells"]]
    s165_check = {j: spearman(a_mcc[j], a_mcc["id"], a_labels) for j in GEOMETRIC}

    # --- 4. Claim checks -----------------------------------------------------
    n_track = {k: sum(1 for r in refs if track[r] == k) for k in ("image", "text")}
    claims: dict[str, Any] = {"i": {}, "ii": {}, "iii": {}, "iv": {}, "v": {}}
    for join in JOINS:
        pj = per_join[join]
        tie = set(pj["tier1"])
        adm = set(pj["mcb_admissible"])
        claims["i"][join] = {"top_f1_cell": top_f1, "in_mcc_tier1": top_f1 in tie,
                             "mcc_rank": rank[join][top_f1], "mcc_tier": tier[join][top_f1],
                             "mcc": mcc[join][top_f1], "mcc_admissible": top_f1 in adm}
        claims["ii"][join] = {"n_in_mcc_tier1": sum(1 for r in f1_tier1 if r in tie),
                              "of": len(f1_tier1),
                              "mcc_ranks": [rank[join][r] for r in f1_tier1],
                              "mcc_tiers": [tier[join][r] for r in f1_tier1]}
        claims["iii"][join] = {"f1_admissible": len(f1_adm), "mcc_admissible": len(adm),
                               "both": len(f1_adm & adm), "union": len(f1_adm | adm),
                               "f1_only": len(f1_adm - adm), "mcc_only": len(adm - f1_adm),
                               "both_members": sorted(f1_adm & adm),
                               "top_mcc_cell_f1_admissible": pj["top_cell"]["ref"] in f1_adm}
        tier1_tracks = {k: sum(1 for r in tie if track[r] == k) for k in ("image", "text")}
        adm_tracks = {k: sum(1 for r in adm if track[r] == k) for k in ("image", "text")}
        ranks_by_track = {k: sorted(rank[join][r] for r in refs if track[r] == k)
                          for k in ("image", "text")}
        claims["iv"][join] = {
            "top_cell_track": pj["top_cell"]["track"],
            "top5_tracks": [r["track"] for r in pj["top10"][:5]],
            "top10_tracks": [r["track"] for r in pj["top10"]],
            "n_image_in_top10": sum(1 for r in pj["top10"] if r["track"] == "image"),
            "tier1_by_track": tier1_tracks,
            "mcb_admissible_by_track": adm_tracks,
            "median_mcc_rank": {k: v[len(v) // 2] if len(v) % 2 else
                                (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2
                                for k, v in ranks_by_track.items()},
            "board_by_track": n_track,
        }
        claims["v"][join] = {"register_leader": REGISTER_MCC_LEADER,
                             "mcc": mcc[join][REGISTER_MCC_LEADER],
                             "mcc_rank": rank[join][REGISTER_MCC_LEADER],
                             "mcc_tier": tier[join][REGISTER_MCC_LEADER],
                             "is_top": pj["top_cell"]["ref"] == REGISTER_MCC_LEADER,
                             "in_mcc_tier1": REGISTER_MCC_LEADER in tie,
                             "mcc_admissible": REGISTER_MCC_LEADER in adm}

    # --- 5. Reference-axis sanity: reference-positive tiles per join --------
    ref_tiles = {}
    for join in JOINS:
        counts = {(g["confusion"]["tp"] + g["confusion"]["fn"])
                  for g in runs[join]["mcc_permutation"]["gates"].values()}
        ref_tiles[join] = sorted(counts)

    summary = {
        "board": BOARD_ID,
        "computed_at_commit": {j: runs[j]["git_commit"] for j in JOINS},
        "generated_at_utc": {j: runs[j]["generated_at_utc"] for j in JOINS},
        "instrument": {
            "tiering": "scripts/era1_leaderboard_tiering.py --permute-mcc "
                       "[--tile-join JOIN]",
            "tiering_settings": "10,000 tile-swap draws, seed 42, BH q = 0.05 per "
                                "family, greedy clique",
            "mcb": "scripts/selection_aware_intervals.py --board --metric mcc "
                   "[--tile-join JOIN] --bootstrap 10000 --m-frac 1.0",
            "mcb_settings": "admissible set: hsu_not_ruled_out, Hsu's constrained "
                            "one-sided form",
            "analyses": f"{BOARD}/tiering-input/run-analyses.json",
        },
        "gate": gate,
        "geometric_run_checks": geometric_checks,
        "per_join": per_join,
        "s165_spearman_recomputed_from_2026_09_12_audit": s165_check,
        "claims": claims,
        "reference_positive_tiles_per_join": ref_tiles,
        "audit_crosscheck": audit_crosscheck(clone, runs),
        "withheld_cells_geometric": withheld_geometric(clone, run_id),
        "track_derivation": track_basis,
        "tracks": track,
    }
    (results / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for join in GEOMETRIC:
        run = runs[join]
        (results / f"mcc-family-{join}.json").write_text(json.dumps({
            "analysis_id": run["analysis_id"], "tile_join": join,
            "git_commit": run["git_commit"], "generated_at_utc": run["generated_at_utc"],
            "n_permutations": run["n_permutations"], "seed": run["seed"],
            "fdr_q": run["fdr_q"], "n_tiles": run["n_tiles"], "n_cells": run["n_cells"],
            "f1_side": "identical to the default-join run and the committed board "
                       "(summary.json -> geometric_run_checks); not copied",
            "mcc_permutation": run["mcc_permutation"],
        }, indent=2) + "\n")
    (results / "mcb").mkdir(exist_ok=True)
    for join in GEOMETRIC:
        shutil.copy2(mcb_runs[join], results / "mcb" / mcb_runs[join].name)
    (results / "README.md").write_text(render_readme(summary))
    print(json.dumps({"gate_passed": gate["passed"],
                      "geometric_run_checks": geometric_checks}, indent=2))
    return 0 if gate["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
