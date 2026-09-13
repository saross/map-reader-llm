#!/usr/bin/env python3
"""Annotate ``results/run-conditions.json`` to clear the verifier's clearable WARNs.

One-shot authoring script for Batch 1 item 2 of
``planning/documentation-foundation-checklist-2026-09-13.md``: resolve the partial
runs reported by ``scripts/verify_run_conditions.py`` **by annotation only**. No
metric, evaluation, detection or threshold is touched — the script adds exactly two
kinds of field:

1. ``source_run`` on a condition whose ``proposer_pool`` is not a key of its run's
   ``proposer_pools`` map. The verifier asks for this note explicitly
   (``pool-unresolved``: "cross-run? add a source_run note") and suppresses the WARN
   when it is present. Every value below is the run that PHYSICALLY OWNS the
   proposer passes, established from the filesystem and from the authoring scripts,
   and each carries its anchor in :data:`POOL_SOURCE_RUNS`. Most are the condition's
   own run: the pool name is a *logical* name — a prompt, a selection band, a
   diversity grouping, or a pool whose passes were never materialised as ``run_*``
   directories — rather than a registered pool key. That is the established
   convention in this file, not an invention: ``pv-diag-384``'s
   ``verified-adv-text-consensus-16of30`` already carries
   ``source_run: "pv-diag-384"`` for exactly this reason, and three run ``_note``s
   (``pv-diag-256``, ``pv-diag-384``, ``retest-phase3c``) already adjudicate the
   class as "benign pool-unresolved" in prose. This script moves that adjudication
   from prose the verifier cannot read into a field it can.

2. dict-form ``_ignored_evals`` waivers (``{"eval_path", "reason"}``) for scored
   evaluations under a run that no condition claims. The reasons below were each
   read out of the evaluation's own ``_metadata.input_files`` and compared against
   the claiming condition's ``eval_path``; none is inferred from a filename.

Deliberately NOT cleared (see § "Left standing" in
``reports/documentation-batch1-deltas-2026-09-13.md``): the ``n-passes-over`` WARNs
on ``55maps-text-min-n10-uplift`` and the ``pinned-vintage`` WARNs on
``e47-propose-brief`` / ``n1-outstanding-384``. Both are **by-design disclosures**
the project has already settled — clearing them would delete an honest signal, not
resolve a defect.

Usage:
    python scripts/annotate_partial_run_warns.py --dry-run   # report, write nothing
    python scripts/annotate_partial_run_warns.py --write     # apply the annotations

    # then, as with every edit to this input:
    python scripts/verify_run_conditions.py
    python scripts/generate_post_run_report.py --all --write
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[1]
RUN_CONDITIONS: Path = REPO_ROOT / "results" / "run-conditions.json"

#: ``run_id -> {pool_name: (source_run, anchor)}``.
#:
#: ``source_run`` is the run whose directory physically holds the proposer passes.
#: ``anchor`` is the re-verifiable evidence for that claim: a path under the run, or
#: the authoring script and line that named the pool. Nothing here is inferred from a
#: pool name alone.
POOL_SOURCE_RUNS: dict[str, dict[str, tuple[str, str]]] = {
    # The prompt name in the pool slot. The physical passes are keyed by grid
    # geometry (four pools), so no single registered pool key exists; the four
    # geometry pools were never decomposed into ``proposer_pools``.
    "grid-2026-08-18": {
        "brief-text": (
            "grid-2026-08-18",
            "prompt-level pool name spanning the run's four geometry pools; passes at "
            "outputs/grid-2026-08-18/g{384_ov048,384_ov192,512_ov064,512_ov256}/run_*",
        ),
    },
    # Same shape: ``brief-text`` is the prompt; the per-arm passes live under
    # scoring/, and only the two top-level armB/armC dirs are registered pools.
    "h13": {
        "brief-text": (
            "h13",
            "prompt-level pool name; per-arm passes at "
            "outputs/h13/scoring/{common,native}/arm{A,B,C}/run_{1..3}",
        ),
    },
    # A single proposer pass written straight into proposer/ with no run_N dir, so
    # ``proposer_pools`` is empty and the condition names the pool by prompt string.
    "proposer-verifier-384": {
        "detect_brief-text": (
            "proposer-verifier-384",
            "single un-numbered proposer pass at outputs/h11/proposer-verifier-384/"
            "proposer/detections-detect_brief-text-3-flash-2026-03-15.geojson",
        ),
    },
    "proposer-verifier-512": {
        "detect_brief-text": (
            "proposer-verifier-512",
            "single un-numbered proposer pass at outputs/h11/proposer-verifier-512/"
            "proposer/detections.geojson",
        ),
    },
    # Proposer passes were never materialised as run_* dirs (only consensus/ and
    # crops/), which the run's own _note already records as benign.
    "pv-diag-256": {
        "text": (
            "pv-diag-256",
            "proposer passes not materialised as run_* dirs; only "
            "outputs/h11/pv-diag-256/consensus/ exists — stated in the run's _note",
        ),
    },
    # Five diversity groupings per track, each a logical union over the run's own
    # registered physical pass-variant pools (GAP-6, stated in the run's _note).
    "retest-phase3c": {
        f"track{t}-h9-{letter}-diversity": (
            "retest-phase3c",
            f"diversity grouping over the run's own h9-{letter.upper()} pass-variant "
            f"pools; consensus output at outputs/retest/phase3c/diversity-consensus/"
            f"track{t}/{letter.upper()}",
        )
        for t, letters in (("1-image", "abcde"), ("2-text", "abde"))
        for letter in letters
    },
    # Two shapes, both this run's own pools:
    #  * ten N1 baseline conditions naming their pool by relative path-string
    #    ("pool/temp") instead of the registered "pool-temp" key — the run's _note
    #    already calls these "benign pool-unresolved";
    #  * the verifier-stage selection bands, each a real directory under verified/.
    #    scripts/author_verifier_robustness_registration.py registers the SAME pool
    #    names with source_run "pv-diag-384" from the verifier-robustness run, which
    #    settles the ownership question independently of this script.
    "pv-diag-384": {
        **{
            name: (
                "pv-diag-384",
                f"N1 baseline condition naming its own pool by relative path-string; "
                f"pool directory outputs/h11/pv-diag-384/{name}",
            )
            for name in (
                "flash-high-image-n5/image-t0.7",
                "flash-high-text-n5/text-t0.7",
                "flash-minimal-text-n30-t07/text-t0.7",
                "image-baseline/image-t0.0",
                "image-n5/image-t0.7",
                "pro-high-image-n5/image-t0.7",
                "pro-high-text-n5/text-t0.7",
                "pro-medium-image-baseline/image-t0.0",
                "pro-medium-text-baseline/text-t0.0",
                "text-baseline/text-t0.0",
            )
        },
        **{
            name: (
                "pv-diag-384",
                f"verifier-stage selection band over this run's own proposer pool; "
                f"band directory outputs/h11/pv-diag-384/verified/{name}",
            )
            for name in (
                "flash-high-image-1of5",
                "flash-high-text-1of10",
                "flash-high-text-1of5",
                "flash-high-text-t03-1of5",
                "flash-minimal-text-t07-1of5",
                "image-1of10",
                "image-1of5",
                "image-baseline",
                "pro-high-text-1of5",
                "text-1of10",
                "text-baseline",
                "text-min-t07-true-1of5",
            )
        },
        "pro-high-image-1of5": (
            "pv-diag-384",
            "verifier-stage selection band over this run's own Pro image pool; the "
            "sweep records its probabilities under the -pro-verifier spelling "
            "(scripts/sweep_unswept_pools.py, manifest 'pro-high-image-1of5' / probs "
            "'pro-high-image-1of5-pro-verifier'), directory outputs/h11/pv-diag-384/"
            "verified/pro-high-image-1of5-pro-verifier",
        ),
        "pro-medium-image-baseline": (
            "pv-diag-384",
            "single-pass Pro image baseline pool of this run; directory "
            "outputs/h11/pv-diag-384/pro-medium-image-baseline",
        ),
        "pro-medium-text-baseline": (
            "pv-diag-384",
            "single-pass Pro text baseline pool of this run; directory "
            "outputs/h11/pv-diag-384/pro-medium-text-baseline",
        ),
    },
}

#: ``run_id -> [(eval_path, reason)]`` waivers appended to ``_ignored_evals``.
#:
#: Every reason was written after opening the evaluation and reading its
#: ``_metadata.input_files.detections``, then comparing it with the ``eval_path`` of
#: the condition that scores the same detections today.
IGNORED_EVAL_WAIVERS: dict[str, list[tuple[str, str]]] = {
    "e47-propose-brief": [
        (
            f"results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/"
            f"propose_brief-text/consensus/consensus_t{k}/evaluation.json",
            f"Superseded pre-recovery scoring. This 2026-05-31 rescore scored "
            f"outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/"
            f"consensus/consensus_t{k}.geojson — the same detections the registered "
            f"condition consensus-{k}of5 now scores at "
            f"results/recovery-reeval-2026-09-08/e47-propose-brief/consensus-{k}of5/"
            f"evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote "
            f"the file. Kept as the pre-recovery record per ruling 3a (PI, "
            f"2026-09-07); not a second condition.",
        )
        for k in range(1, 6)
    ],
    "n1-outstanding-384": [
        (
            f"results/rescore-2026-05-31/n1-outstanding-384/{pool}/consensus/"
            f"consensus_t{k}/evaluation.json",
            f"Superseded pre-recovery scoring. This 2026-05-31 rescore scored "
            f"outputs/h11/n1-outstanding-384/{pool}/consensus/consensus_t{k}.geojson "
            f"— the same detections the registered condition "
            f"{pool}-consensus-{k}of3 now scores at "
            f"results/recovery-reeval-2026-09-08/n1-outstanding-384/"
            f"{pool}-consensus-{k}of3/evaluation.json after the E71 dead-tile "
            f"recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record "
            f"per ruling 3a (PI, 2026-09-07); not a second condition.",
        )
        for pool in ("pro-image-high-t0", "pro-text-high-t0")
        for k in range(1, 4)
    ],
    "pv-diag-256": [
        (
            f"results/uplift-supplement/verifier-pairing/"
            f"verifier-robustness__{label}/evaluation.json",
            f"Uplift-supplement verifier-pairing input for the CROSS-RUN condition "
            f"verifier-robustness::{label}, which draws its proposer pool from this "
            f"run (source_run 'pv-diag-256' in "
            f"scripts/author_verifier_robustness_registration.py) and so scores "
            f"outputs/h11/pv-diag-256/consensus/text-5of5.geojson. It surfaces under "
            f"pv-diag-256 only because the detections live here; it is an input to "
            f"the supplement's pairing tables "
            f"(planning/uplift-supplement-2026-08-28.md), not a pv-diag-256 "
            f"condition. Same waiver class as the 55maps-text-min-n10-uplift "
            f"pairing entries (PI ruling 2026-09-07, "
            f"planning/reference-revision-2026-09-06.md).",
        )
        for label in ("verified-256-union-t0-0-n5", "verified-256-ge3of5-t0-3-n5")
    ],
}

#: ``run_id -> sentence appended to the run's ``_note``.`` Records WHY the
#: annotations landed, so the decomposition explains itself without this script.
NOTE_APPENDS: dict[str, str] = {
    "grid-2026-08-18":
        "Pool annotation (2026-09-13, S153 Batch 1 item 2): the conditions name their "
        "proposer pool by PROMPT ('brief-text'); the physical passes are keyed by grid "
        "geometry (g384_ov048 / g384_ov192 / g512_ov064 / g512_ov256, each with "
        "run_*), which was never decomposed into proposer_pools. source_run records "
        "this run as the pool's home so the benign pool-unresolved WARN is machine-"
        "readable. No metric, eval or detection changed.",
    "h13":
        "Pool annotation (2026-09-13, S153 Batch 1 item 2): the conditions name their "
        "proposer pool by PROMPT ('brief-text'); the per-arm passes live under "
        "scoring/{common,native}/arm{A,B,C}/run_{1..3} while proposer_pools registers "
        "only the two top-level armB/armC dirs. source_run records this run as the "
        "pool's home. No metric, eval or detection changed.",
    "proposer-verifier-384":
        "Pool annotation (2026-09-13, S153 Batch 1 item 2): the run's single proposer "
        "pass was written straight into proposer/ with no run_N directory, so "
        "proposer_pools is empty and the conditions name the pool by prompt string. "
        "source_run records this run as the pool's home (pv-512 / pv-256 precedent). "
        "No metric, eval or detection changed.",
    "proposer-verifier-512":
        "Pool annotation (2026-09-13, S153 Batch 1 item 2): as for "
        "proposer-verifier-384 — one un-numbered proposer pass at "
        "proposer/detections.geojson, empty proposer_pools, pool named by prompt "
        "string; source_run records this run as the pool's home. No metric, eval or "
        "detection changed.",
    "pv-diag-256":
        "Pool annotation (2026-09-13, S153 Batch 1 item 2): the 'benign "
        "pool-unresolved' adjudication stated above is now machine-readable — "
        "source_run 'pv-diag-256' on both conditions. Two uplift-supplement "
        "verifier-pairing evaluations of this run's text-5of5 detections, which "
        "belong to the cross-run verifier-robustness 256 conditions, are waived into "
        "_ignored_evals with reasons. No metric, eval or detection changed.",
    "pv-diag-384":
        "Pool annotation (2026-09-13, S153 Batch 1 item 2): the 'benign "
        "pool-unresolved' adjudication stated above is now machine-readable. The ten "
        "N1 baseline conditions that name their pool by relative path-string, and the "
        "verifier-stage selection bands (each a real directory under verified/), all "
        "carry source_run 'pv-diag-384'. The same band names are registered with "
        "source_run 'pv-diag-384' from the verifier-robustness run, which settles pool "
        "ownership independently. No metric, eval or detection changed.",
    "retest-phase3c":
        "Pool annotation (2026-09-13, S153 Batch 1 item 2): the GAP-6 'benign "
        "pool-unresolved' adjudication stated above is now machine-readable — "
        "source_run 'retest-phase3c' on the nine diversity-grouping conditions, each "
        "a logical union over this run's own registered pass-variant pools. No "
        "metric, eval or detection changed.",
    "e47-propose-brief":
        "Completeness waivers (2026-09-13, S153 Batch 1 item 2): the five "
        "rescore-2026-05-31 consensus_t{1..5} evaluations are the PRE-RECOVERY "
        "scoring of the same consensus geojsons the registered consensus-{1..5}of5 "
        "conditions now score at recovery-reeval-2026-09-08; waived with reasons. The "
        "pinned-vintage WARN on single-pass-run_4 is left standing: it is the ruling-"
        "3a disclosure working as designed, not a defect. No metric changed.",
    "n1-outstanding-384":
        "Completeness waivers (2026-09-13, S153 Batch 1 item 2): the six "
        "rescore-2026-05-31 consensus_t{1..3} evaluations of the two pro-*-high-t0 "
        "pools are the PRE-RECOVERY scoring of the same consensus geojsons the "
        "registered *-consensus-{1..3}of3 conditions now score at "
        "recovery-reeval-2026-09-08; waived with reasons. The eight pinned-vintage "
        "WARNs are left standing as ruling-3a disclosures. No metric changed.",
}


def load() -> dict:
    """Read the decomposition input."""
    return json.loads(RUN_CONDITIONS.read_text(encoding="utf-8"))


def apply_annotations(doc: dict) -> list[str]:
    """Mutate ``doc`` in place; return a human-readable change log.

    Raises:
        KeyError: if a run, pool or eval path named in the tables above is absent
            from the decomposition — a silent no-op would let a stale table look
            like a successful run.
    """
    changes: list[str] = []
    decomp = doc["decomposition"]

    for run_id, pools in POOL_SOURCE_RUNS.items():
        if run_id not in decomp:
            raise KeyError(f"{run_id} is not in the decomposition")
        n = 0
        for spec in decomp[run_id].get("conditions", []):
            pool = spec.get("proposer_pool")
            if pool in pools and not spec.get("source_run"):
                source_run, anchor = pools[pool]
                spec["source_run"] = source_run
                spec["_source_run_basis"] = anchor
                n += 1
        if n == 0:
            raise KeyError(f"{run_id}: no condition matched the pool table — stale entry?")
        changes.append(f"{run_id}: source_run on {n} condition(s) "
                       f"({len(pools)} distinct pool name(s))")

    for run_id, waivers in IGNORED_EVAL_WAIVERS.items():
        if run_id not in decomp:
            raise KeyError(f"{run_id} is not in the decomposition")
        entry = decomp[run_id]
        existing = entry.setdefault("_ignored_evals", [])
        have = {e["eval_path"] if isinstance(e, dict) else e for e in existing}
        added = 0
        for eval_path, reason in waivers:
            if not (REPO_ROOT / eval_path).exists():
                raise KeyError(f"{run_id}: waived eval {eval_path} does not exist")
            if eval_path in have:
                continue
            existing.append({"eval_path": eval_path, "reason": reason})
            added += 1
        changes.append(f"{run_id}: {added} _ignored_evals waiver(s) added")

    for run_id, sentence in NOTE_APPENDS.items():
        if run_id not in decomp:
            raise KeyError(f"{run_id} is not in the decomposition")
        entry = decomp[run_id]
        note = entry.get("_note") or ""
        if sentence in note:
            continue
        entry["_note"] = f"{note} | {sentence}" if note.strip() else sentence
        changes.append(f"{run_id}: _note appended")

    return changes


def main(argv: list[str] | None = None) -> int:
    """Entry point. Exit 0 on success, 2 on a bad CLI argument."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Report the annotations and write nothing.")
    parser.add_argument("--write", action="store_true",
                        help="Apply the annotations to results/run-conditions.json.")
    args = parser.parse_args(argv)
    if not (args.dry_run or args.write):
        parser.print_help()
        return 2

    doc = load()
    changes = apply_annotations(doc)
    for line in changes:
        print(f"  {line}")

    if args.write:
        RUN_CONDITIONS.write_text(
            json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nwrote {RUN_CONDITIONS.relative_to(REPO_ROOT)}")
    else:
        print("\ndry run — nothing written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
