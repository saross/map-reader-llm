#!/usr/bin/env python3
"""
kl_splice.py -- splice re-run ladders into the K-ladder roll-ups, others kept.

Purpose:
    S164 restatement pass, K-ladder lane, part 2. ``k_ladder_mcc_test.py`` and
    ``k_ladder_mcb.py`` write their roll-up (``summary.json``, and for the MCB
    ``table.md``) from the ladders of ONE run, so ``--only`` would shrink the
    committed roll-up to the ladders re-run. Each ladder is tested on its own
    cells with its own seed and its own Benjamini-Hochberg family (the MCC test)
    or its own bootstrap (the MCB), so a ladder's record does not depend on
    which other ladders ran with it. This helper therefore keeps every other
    ladder's committed record byte for byte and replaces only the re-run ones,
    in place, then recomputes the roll-up fields exactly as the scripts do:

    * ``mcc``: ``n_ladders``, ``gate_all_passed`` and ``generated_at_utc`` (the
      re-run's); the other top-level keys must equal the committed ones.
    * ``mcb``: ``n_ladders``, ``gate_all_passed``, ``roll_up`` (the script's own
      five list comprehensions, ``scripts/k_ladder_mcb.py`` ``main``) and
      ``generated_at_utc``; ``table.md`` re-rendered with the script's own
      ``markdown_table``.

    ``--identity`` splices the committed records into the committed roll-up,
    which must reproduce it byte for byte apart from ``generated_at_utc``: the
    proof that the splice itself changes nothing else.

Usage:
    python kl_splice.py mcc <code_root> <committed_summary> <rerun_summary> <out_summary>
    python kl_splice.py mcb <code_root> <committed_summary> <rerun_summary> <out_dir>
    (add --identity to splice the committed records into themselves)

Author: Claude (Opus 5.5) for Shawn Ross, S164 restatement pass, 2026-10-15.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def splice_mcc(committed: dict, rerun: dict) -> dict:
    """Replace the re-run ladders' entries in the MCC-test summary."""
    for key in ("source_inventory", "n_permutations", "seed"):
        if committed[key] != rerun[key]:
            raise SystemExit(f"mcc: {key} differs: {committed[key]!r} vs {rerun[key]!r}")
    new = {e["ladder"]: e for e in rerun["ladders"]}
    ladders = [new.get(e["ladder"], e) for e in committed["ladders"]]
    if set(new) - {e["ladder"] for e in committed["ladders"]}:
        raise SystemExit("mcc: a re-run ladder is not in the committed summary")
    out = dict(committed)
    out["generated_at_utc"] = rerun["generated_at_utc"]
    out["n_ladders"] = len(ladders)
    out["gate_all_passed"] = all(s["gate_passed"] for s in ladders)
    out["ladders"] = ladders
    return out


def splice_mcb(committed: dict, rerun: dict) -> dict:
    """Replace the re-run ladders' records in the MCB summary; recompute the roll-up."""
    for key in ("script", "instrument", "withheld"):
        if committed[key] != rerun[key]:
            raise SystemExit(f"mcb: {key} differs between the runs")
    new = {e["slug"]: e for e in rerun["ladders"]}
    if set(new) - {e["slug"] for e in committed["ladders"]}:
        raise SystemExit("mcb: a re-run ladder is not in the committed summary")
    collated = [new.get(e["slug"], e) for e in committed["ladders"]]
    out = dict(committed)
    out["generated_at_utc"] = rerun["generated_at_utc"]
    out["n_ladders"] = len(collated)
    out["gate_all_passed"] = all(g["passed"] for lad in collated for g in lad["gates"])
    # The roll-up exactly as scripts/k_ladder_mcb.py main() builds it.
    out["roll_up"] = {
        "ladders_whose_F1_admissible_set_contains_K3": [
            lad["slug"] for lad in collated if (lad.get("f1") or {}).get("contains_K3")],
        "ladders_whose_F1_admissible_set_excludes_K10": [
            lad["slug"] for lad in collated if (lad.get("f1") or {}).get("excludes_K10")],
        "ladders_whose_F1_admissible_set_is_the_whole_ladder": [
            lad["slug"] for lad in collated if (lad.get("f1") or {}).get("whole_ladder")],
        "ladders_whose_MCC_admissible_set_is_the_whole_ladder": [
            lad["slug"] for lad in collated if (lad.get("mcc") or {}).get("whole_ladder")],
        "ladders_whose_MCC_admissible_set_contains_K1": [
            lad["slug"] for lad in collated
            if 1 in ((lad.get("mcc") or {}).get("hsu_admissible_K") or [])],
    }
    out["ladders"] = collated
    return out


def main() -> int:
    """Splice and write."""
    args = [a for a in sys.argv[1:] if a != "--identity"]
    identity = "--identity" in sys.argv
    mode, code, committed_p, rerun_p, out_p = args
    committed = json.loads(Path(committed_p).read_text(encoding="utf-8"))
    rerun = committed if identity else json.loads(Path(rerun_p).read_text(encoding="utf-8"))
    if mode == "mcc":
        out = splice_mcc(committed, rerun)
        Path(out_p).write_text(json.dumps(out, indent=2) + "\n")
    elif mode == "mcb":
        sys.path.insert(0, str(Path(code).resolve()))
        from scripts.k_ladder_mcb import markdown_table  # noqa: PLC0415
        out = splice_mcb(committed, rerun)
        out_dir = Path(out_p)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "summary.json").write_text(json.dumps(out, indent=2) + "\n",
                                              encoding="utf-8")
        (out_dir / "table.md").write_text(markdown_table(out["ladders"]) + "\n",
                                          encoding="utf-8")
    else:
        raise SystemExit(f"unknown mode {mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
