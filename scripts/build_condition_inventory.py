#!/usr/bin/env python3
"""Build a structured condition inventory across all production eras.

Crawls outputs/retest/ (Era 1), outputs/h11/ (Era 2), outputs/h8-v2/,
outputs/h10/, outputs/h12-v2/ (Era 3) and extracts per-condition metadata
from .meta.json files. Outputs a JSON inventory at
planning/condition-inventory.json and a human-readable markdown summary
at planning/condition-inventory.md.

Reproducing this inventory: ``python scripts/build_condition_inventory.py``
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# v2 verifier configs — quarantined (data leakage from test pool)
V2_VERIFIER_QUARANTINE = {
    "adversarial-text-v2", "adversarial-image-v2",
    "brief-text-v2", "brief-image-v2",
    "checklist-text-v2", "checklist-image-v2",
}


def find_runs(condition_dir: Path) -> list[Path]:
    """Find run_N directories under a condition path."""
    runs = sorted(
        [d for d in condition_dir.iterdir()
         if d.is_dir() and d.name.startswith("run_")],
        key=lambda d: int(d.name.split("_")[1]),
    )
    return runs


def read_first_meta(condition_dir: Path) -> dict | None:
    """Read the first available .meta.json from run_1 (or any run)."""
    for run_dir in find_runs(condition_dir):
        metas = sorted(run_dir.glob("*.meta.json"))
        if metas:
            return json.loads(metas[0].read_text())
    return None


def has_consensus(condition_dir: Path) -> bool:
    """Check if consensus outputs exist in any naming convention.

    Recognises:
    - merge_passes convention: consensus_t1..t5.geojson
    - H11-era convention: *-NofM.geojson (e.g., flash-high-text-1of5.geojson)
    - Older convention: merged_*.geojson
    """
    for subdir_name in ("", "consensus", "greedy", "voting"):
        check_dir = condition_dir / subdir_name if subdir_name else condition_dir
        if not check_dir.exists():
            continue
        # merge_passes convention
        if (check_dir / "consensus_t4.geojson").exists():
            return True
        # H11-era convention (NofM pattern)
        if list(check_dir.glob("*-[0-9]*of[0-9]*.geojson")):
            return True
        # Older merged convention
        if list(check_dir.glob("merged_*.geojson")):
            return True
    return False


def find_consensus_files(condition_dir: Path) -> list[str]:
    """Return list of consensus file names found."""
    found = []
    for subdir_name in ("", "consensus", "greedy", "voting"):
        check_dir = condition_dir / subdir_name if subdir_name else condition_dir
        if not check_dir.exists():
            continue
        for pattern in ("consensus_t*.geojson", "*-[0-9]*of[0-9]*.geojson",
                        "merged_*.geojson", "voting_summary.json"):
            found.extend(f.name for f in check_dir.glob(pattern))
    return sorted(set(found))


def has_verifier(condition_dir: Path) -> bool:
    """Check if verifier probabilities.json exists."""
    for p in [
        condition_dir / "verified" / "probabilities.json",
        condition_dir / "probabilities.json",
    ]:
        if p.exists():
            return True
    return False


def extract_condition(
    condition_dir: Path,
    era: int,
    hypothesis: str,
    notes: str = "",
) -> dict | None:
    """Extract metadata for a single condition directory."""
    runs = find_runs(condition_dir)
    if not runs:
        return None

    meta = read_first_meta(condition_dir)
    cfg = meta.get("configuration", {}) if meta else {}
    fcs = cfg.get("full_config_snapshot", {})

    version = cfg.get("version") or fcs.get("version") or "unknown"
    temperature = cfg.get("temperature") or fcs.get("temperature")
    thinking = cfg.get("thinking_level") or fcs.get("thinking_level") or "unknown"
    include_imgs = cfg.get("include_example_images")
    if include_imgs is None:
        include_imgs = fcs.get("include_example_images")
    model = cfg.get("model") or fcs.get("model") or "unknown"
    instruction = cfg.get("instruction_file") or fcs.get("instruction_file") or ""

    track = "image" if include_imgs else "text"
    k = len(runs)
    arch = "single-pass" if k == 1 else "consensus"

    consensus_files = find_consensus_files(condition_dir)
    has_cons = bool(consensus_files)
    status = "READY" if has_cons else (
        "SINGLE_PASS_ONLY" if k == 1 else "NEEDS_CONSENSUS"
    )

    return {
        "id": condition_dir.name,
        "path": str(condition_dir.relative_to(BASE)),
        "era": era,
        "hypothesis": hypothesis,
        "track": track,
        "architecture": arch,
        "K": k,
        "T": temperature,
        "thinking": thinking,
        "model": model,
        "config_version": version,
        "instruction_file": instruction,
        "consensus_built": has_cons,
        "consensus_files": consensus_files,
        "verifier_data": has_verifier(condition_dir),
        "status": status,
        "notes": notes,
    }


def crawl_era1() -> list[dict]:
    """Crawl outputs/retest/ for Era 1 conditions."""
    retest = BASE / "outputs" / "retest"
    conditions = []

    # Phase 2a — H1 modality (5 conditions)
    for d in sorted((retest / "phase2a").iterdir()):
        if d.is_dir() and d.name != "checkpoint.json":
            c = extract_condition(d, 1, "H1", "T=1.0 (not production carry-forward)")
            if c:
                c["id"] = f"h1-{d.name}"
                conditions.append(c)

    # Phase 2b — H7 temperature (2 tracks × 5 temps)
    for track_dir in sorted((retest / "phase2b").iterdir()):
        if not track_dir.is_dir():
            continue
        for temp_dir in sorted(track_dir.iterdir()):
            if temp_dir.is_dir():
                c = extract_condition(temp_dir, 1, "H7")
                if c:
                    c["id"] = f"h7-{track_dir.name}-{temp_dir.name}"
                    conditions.append(c)

    # Phase 2c — H8 library (2 tracks + exploratory)
    for track_dir in sorted((retest / "phase2c").iterdir()):
        if not track_dir.is_dir():
            continue
        for lib_dir in sorted(track_dir.iterdir()):
            if lib_dir.is_dir():
                c = extract_condition(lib_dir, 1, "H8")
                if c:
                    c["id"] = f"h8-{track_dir.name}-{lib_dir.name}"
                    conditions.append(c)

    # Phase 2d — H5 neg text (2 tracks × 2 treatments)
    for track_dir in sorted((retest / "phase2d").iterdir()):
        if not track_dir.is_dir():
            continue
        for txt_dir in sorted(track_dir.iterdir()):
            if txt_dir.is_dir():
                c = extract_condition(txt_dir, 1, "H5")
                if c:
                    c["id"] = f"h5-{track_dir.name}-{txt_dir.name}"
                    conditions.append(c)

    # Phase 2e — H4 ordering (4 conditions)
    for d in sorted((retest / "phase2e").iterdir()):
        if d.is_dir() and d.name not in ("checkpoint.json", "study_manifest.json"):
            c = extract_condition(d, 1, "H4")
            if c:
                c["id"] = f"h4-{d.name}"
                conditions.append(c)

    # Phase 3a — H3 consensus (2 tracks × 3 temps, K=30)
    for track_dir in sorted((retest / "phase3a").iterdir()):
        if not track_dir.is_dir():
            continue
        for temp_dir in sorted(track_dir.iterdir()):
            if temp_dir.is_dir():
                c = extract_condition(temp_dir, 1, "H3")
                if c:
                    c["id"] = f"h3-{track_dir.name}-{temp_dir.name}"
                    conditions.append(c)

    # Phase 3a-high — H3 HIGH thinking (text track only, K=30)
    p3ah = retest / "phase3a-high"
    if p3ah.exists():
        for track_dir in sorted(p3ah.iterdir()):
            if not track_dir.is_dir():
                continue
            for temp_dir in sorted(track_dir.iterdir()):
                if temp_dir.is_dir():
                    runs = find_runs(temp_dir)
                    if runs:
                        c = extract_condition(temp_dir, 1, "H3", "HIGH thinking")
                        if c:
                            c["id"] = f"h3-high-{track_dir.name}-{temp_dir.name}"
                            conditions.append(c)
                    else:
                        conditions.append({
                            "id": f"h3-high-{track_dir.name}-{temp_dir.name}",
                            "path": str(temp_dir.relative_to(BASE)),
                            "era": 1, "hypothesis": "H3",
                            "status": "EMPTY",
                            "notes": "Planned but not executed",
                            "K": 0, "track": "image" if "image" in track_dir.name else "text",
                            "architecture": "consensus",
                        })

    # Phase 3a-replication — H3 replication (2 conditions, K=30)
    p3ar = retest / "phase3a-replication"
    if p3ar.exists():
        for d in sorted(p3ar.iterdir()):
            if d.is_dir():
                c = extract_condition(d, 1, "H3", "replication")
                if c:
                    c["id"] = f"h3-rep-{d.name}"
                    conditions.append(c)

    # Phase 3c — H9 diversity (45 conditions, K=5)
    p3c = retest / "phase3c"
    if p3c.exists():
        for track_dir in sorted(p3c.iterdir()):
            if not track_dir.is_dir():
                continue
            for div_dir in sorted(track_dir.iterdir()):
                if div_dir.is_dir():
                    c = extract_condition(div_dir, 1, "H9")
                    if c:
                        c["id"] = f"h9-{track_dir.name}-{div_dir.name}"
                        conditions.append(c)

    # H11 bridge — single-pass 384 at T=0
    h11_bridge = retest / "h11-single-pass-384-t0"
    if h11_bridge.exists():
        for d in sorted(h11_bridge.iterdir()):
            if d.is_dir():
                c = extract_condition(d, 1, "H11", "384px bridge condition")
                if c:
                    c["id"] = f"h11-bridge-{d.name}"
                    conditions.append(c)

    return conditions


def crawl_era2() -> list[dict]:
    """Crawl outputs/h11/ for Era 2 conditions."""
    h11 = BASE / "outputs" / "h11"
    conditions = []

    # pv-diag-384 — main H11 conditions
    pvd = h11 / "pv-diag-384"
    shared_consensus = pvd / "consensus" if pvd.exists() else None

    # Map shared consensus files to condition prefixes
    shared_consensus_map: dict[str, list[str]] = {}
    if shared_consensus and shared_consensus.exists():
        for f in shared_consensus.glob("*.geojson"):
            name = f.stem
            parts = name.rsplit("-", 1)
            if "of" in parts[-1]:
                config_prefix = parts[0]
                threshold = parts[-1]
            else:
                config_prefix = name
                threshold = "baseline"
            shared_consensus_map.setdefault(config_prefix, []).append(threshold)

    if pvd and pvd.exists():
        for study_dir in sorted(pvd.iterdir()):
            if not study_dir.is_dir():
                continue
            if study_dir.name in ("consensus", "crops", "final-pv-jobs.log",
                                   "flash-final-jobs.log", "checkpoint.json"):
                continue
            if study_dir.name.endswith(".log"):
                continue
            for config_dir in sorted(study_dir.iterdir()):
                if config_dir.is_dir():
                    note = ""
                    if "611tiles" in study_dir.name:
                        note = "EXCLUDED: ran on 611 tiles (not production scope)"
                    c = extract_condition(config_dir, 2, "H11", note)
                    if c:
                        c["id"] = f"h11-pvd-{study_dir.name}"
                        if note:
                            c["status"] = "EXCLUDED"
                        # Check shared consensus directory for this condition
                        # Map study_dir names to consensus prefixes
                        prefix_map = {
                            "flash-high-text-n5": "flash-high-text",
                            "flash-high-image-n5": "flash-high-image",
                            "flash-minimal-text-n30-t07": "flash-minimal-text-t07",
                            "pro-high-text-n5": "pro-high-text",
                            "pro-high-image-n5": "pro-high-image",
                            "text-n10": "text",
                            "image-n5": "image",
                            "text-baseline": "text-baseline",
                            "image-baseline": "image-baseline",
                            "pro-medium-text-baseline": None,
                            "pro-medium-image-baseline": None,
                            "text-baseline-611tiles": None,
                        }
                        cons_prefix = prefix_map.get(study_dir.name, study_dir.name)
                        if cons_prefix and cons_prefix in shared_consensus_map:
                            thresholds = shared_consensus_map[cons_prefix]
                            c["consensus_built"] = True
                            c["consensus_files"] = [
                                f"{cons_prefix}-{t}.geojson" for t in thresholds
                            ]
                            if c["status"] == "NEEDS_CONSENSUS":
                                c["status"] = "READY"
                            c["notes"] = (c.get("notes", "") +
                                f" Shared consensus: {len(thresholds)} threshold(s)").strip()
                        conditions.append(c)
                        break
            else:
                c = extract_condition(study_dir, 2, "H11")
                if c:
                    c["id"] = f"h11-pvd-{study_dir.name}"
                    conditions.append(c)

    # n1-outstanding-384 — single-pass + small-K
    n1 = h11 / "n1-outstanding-384"
    if n1.exists():
        for d in sorted(n1.iterdir()):
            if d.is_dir() and d.name not in ("checkpoint.json", "study_manifest.json"):
                c = extract_condition(d, 2, "H11", "n1-outstanding")
                if c:
                    c["id"] = f"h11-n1-{d.name}"
                    conditions.append(c)

    # proposer-verifier-384 — PV comparison (v1 and v2)
    pv384 = h11 / "proposer-verifier-384"
    if pv384.exists():
        for f in sorted(pv384.glob("verified-*.geojson")):
            name = f.stem.replace("verified-", "")
            is_v2 = name in V2_VERIFIER_QUARANTINE or name.endswith("-v2")
            conditions.append({
                "id": f"pv-{name}",
                "path": str(f.relative_to(BASE)),
                "era": 2,
                "hypothesis": "H11",
                "track": "image" if "image" in name else "text",
                "architecture": "single-pass+PV",
                "K": 1,
                "T": None,
                "thinking": None,
                "model": "gemini-3-flash",
                "config_version": f"verified-{name}",
                "instruction_file": "",
                "consensus_built": False,
                "verifier_data": True,
                "status": "QUARANTINED" if is_v2 else "PV_READY",
                "notes": "v2 verifier — data leakage from test pool" if is_v2
                         else "v1 verifier — PV leaderboard entry",
            })

    # e47-propose-brief
    e47 = h11 / "e47-propose-brief"
    if e47.exists():
        for study_dir in sorted(e47.iterdir()):
            if study_dir.is_dir() and study_dir.name not in ("checkpoint.json",):
                for config_dir in sorted(study_dir.iterdir()):
                    if config_dir.is_dir():
                        c = extract_condition(config_dir, 2, "H11", "e47 propose-brief")
                        if c:
                            c["id"] = "h11-e47-propose-brief"
                            conditions.append(c)
                        break

    # gold-standard-v2
    gs = h11 / "gold-standard-v2" / "proposer"
    if gs.exists():
        for d in sorted(gs.iterdir()):
            if d.is_dir() and d.name.startswith("run_"):
                pass
        c = extract_condition(gs, 2, "H11", "gold-standard-v2 proposer")
        if c:
            c["id"] = "h11-gold-standard-v2"
            conditions.append(c)

    return conditions


def crawl_era3() -> list[dict]:
    """Crawl outputs/h8-v2/, h10/evaluation-v2/, h12-v2/ for Era 3."""
    conditions = []

    # H8 v2
    h8 = BASE / "outputs" / "h8-v2"
    for cond_name in [
        "pure-positive-canon", "canonical", "plus-hp",
        "scale-4", "scale-8", "scale-16", "scale-32",
    ]:
        d = h8 / cond_name
        if d.exists():
            c = extract_condition(d, 3, "H8v2")
            if c:
                c["id"] = f"h8v2-{cond_name}"
                # Check for greedy consensus
                greedy_dir = h8 / "greedy" / cond_name
                if greedy_dir.exists() and (greedy_dir / "consensus_t4.geojson").exists():
                    c["consensus_built"] = True
                    c["status"] = "READY"
                conditions.append(c)

    # H10 v2
    h10_eval = BASE / "outputs" / "h10" / "evaluation-v2"
    if h10_eval.exists():
        for d in sorted(h10_eval.iterdir()):
            if d.is_dir() and d.name.startswith("pool_"):
                c = extract_condition(d, 3, "H10v2")
                if c:
                    c["id"] = f"h10v2-{d.name}"
                    cons_dir = d / "consensus"
                    if cons_dir.exists() and (cons_dir / "consensus_t4.geojson").exists():
                        c["consensus_built"] = True
                        c["status"] = "READY"
                    conditions.append(c)

    # H12 v2
    h12 = BASE / "outputs" / "h12-v2"
    for cond_name in ["r1-hn-heavy", "r3-hp-heavy"]:
        d = h12 / cond_name
        if d.exists():
            c = extract_condition(d, 3, "H12v2")
            if c:
                c["id"] = f"h12v2-{cond_name}"
                greedy_dir = h12 / "greedy" / cond_name
                if greedy_dir.exists() and (greedy_dir / "consensus_t4.geojson").exists():
                    c["consensus_built"] = True
                    c["status"] = "READY"
                conditions.append(c)

    # R2 (reused from H10 v2 pool_160_hp4hn4)
    conditions.append({
        "id": "h12v2-r2-balanced",
        "path": "outputs/h10/evaluation-v2/pool_160_hp4hn4",
        "era": 3, "hypothesis": "H12v2",
        "track": "image", "architecture": "consensus",
        "K": 5, "T": 0.7, "thinking": "high",
        "model": "gemini-3-flash", "config_version": "detect_pool_160_hp4hn4_v2",
        "instruction_file": "detect_brief-text-image.md",
        "consensus_built": True, "verifier_data": True,
        "status": "READY",
        "notes": "Reused from H10 v2 pool_160_hp4hn4 (byte-identical to H8 v2 Scale-8)",
    })

    return conditions


def load_existing_evaluations() -> dict[str, dict]:
    """Load pre-computed F1/P/R from aggregate files and per-condition results.

    Returns a dict mapping condition label → {f1, precision, recall, source}.
    """
    evals: dict[str, dict] = {}

    # 1. all-bootstrap-cis.json (Era 1, 496 entries)
    abc_path = BASE / "results" / "all-bootstrap-cis.json"
    if abc_path.exists():
        d = json.loads(abc_path.read_text())
        for key, val in d.get("results", {}).items():
            f1_data = val.get("f1", {})
            evals[key] = {
                "f1": f1_data.get("mean"),
                "f1_ci_lower": f1_data.get("ci_lower"),
                "f1_ci_upper": f1_data.get("ci_upper"),
                "source": "all-bootstrap-cis.json",
            }

    # 2. bootstrap-cis-384px.json (Era 2, 81 entries)
    bc384_path = BASE / "results" / "h11-384-pv-diagnostic" / "bootstrap-cis-384px.json"
    if bc384_path.exists():
        d = json.loads(bc384_path.read_text())
        for key, val in d.get("results", {}).items():
            best = val.get("best_f1") or val.get("f1", {})
            if isinstance(best, dict):
                evals[f"384px:{key}"] = {
                    "f1": best.get("mean"),
                    "source": "bootstrap-cis-384px.json",
                }

    # 3. Per-condition threshold_sweep.json in results/h11-384-pv-diagnostic/
    for sweep in (BASE / "results" / "h11-384-pv-diagnostic").glob("*/threshold_sweep.json"):
        cond_name = sweep.parent.name
        if f"384px:{cond_name}" not in evals:
            try:
                sd = json.loads(sweep.read_text())
                if isinstance(sd, dict) and "optimal" in sd:
                    opt = sd["optimal"]
                    evals[f"384px-sweep:{cond_name}"] = {
                        "f1": opt.get("f1"),
                        "source": f"h11-384-pv-diagnostic/{cond_name}/threshold_sweep.json",
                    }
            except (json.JSONDecodeError, KeyError):
                pass

    return evals


def write_inventory(conditions: list[dict]) -> None:
    """Write JSON and markdown inventory."""
    # Cross-reference with existing evaluations
    existing_evals = load_existing_evaluations()
    n_with_eval = 0
    for c in conditions:
        c["existing_evaluation"] = False
        c["existing_f1"] = None
        # Try various label formats
        for label_fn in [
            lambda c: f"single:{c['path'].replace('outputs/retest/','')}",
            lambda c: f"384px:{c['id'].replace('h11-pvd-','')}",
            lambda c: c["id"],
        ]:
            try:
                label = label_fn(c)
            except (KeyError, TypeError):
                continue
            # Check partial matches in existing_evals
            for ekey, edata in existing_evals.items():
                if label in ekey or ekey.endswith(label):
                    c["existing_evaluation"] = True
                    c["existing_f1"] = edata.get("f1")
                    c["eval_source"] = edata.get("source", "")
                    n_with_eval += 1
                    break
            if c["existing_evaluation"]:
                break

    print(f"Conditions with existing evaluation data: {n_with_eval}/{len(conditions)}")

    out_json = BASE / "planning" / "condition-inventory.json"
    out_json.write_text(json.dumps(conditions, indent=2))
    print(f"Wrote {len(conditions)} conditions to {out_json}")

    # Summary stats
    by_era = {}
    by_status = {}
    for c in conditions:
        era = c.get("era", "?")
        by_era[era] = by_era.get(era, 0) + 1
        st = c.get("status", "?")
        by_status[st] = by_status.get(st, 0) + 1

    print(f"\nBy era: {dict(sorted(by_era.items()))}")
    print(f"By status: {dict(sorted(by_status.items()))}")

    needs_consensus = [c for c in conditions if c.get("status") == "NEEDS_CONSENSUS"]
    print(f"\nConditions needing merge_passes: {len(needs_consensus)}")
    for c in needs_consensus[:10]:
        print(f"  {c['id']} (K={c.get('K')}, era={c.get('era')})")
    if len(needs_consensus) > 10:
        print(f"  ... and {len(needs_consensus)-10} more")


if __name__ == "__main__":
    all_conditions = []
    all_conditions.extend(crawl_era1())
    all_conditions.extend(crawl_era2())
    all_conditions.extend(crawl_era3())
    write_inventory(all_conditions)
