#!/usr/bin/env python3
"""
Run B Stage 2's arm table and the checks the launcher runs around it.

Why this exists
---------------
The pre-launch audit of Stage 2 (``reports/s163-agent-records/run-b-stage2-audit.md``)
asked for four checks the launcher did not make. They share one table of
what each arm was supposed to send and how big its union was expected to
be, so they live here, beside that table, and the launcher
(``scripts/modality-bridge-2026-10-07-stage2.sh``) calls them:

``metas ARM`` (audit A5)
    Every pass file of the arm (main and recovery fragments) has a sibling
    ``.meta.json``; its ``configuration`` must record the arm's model,
    temperature (1.0 on the two ``temp1`` arms, 0.7 otherwise) and thinking
    level. On the three explicit-cache arms every file's cached share must
    lie in 0.92–0.97, "about 0.94" (the measured profile is 18,909 cached of
    about 20,020 input tokens per call, 0.9445 on all ten landed ``g3-image``
    passes: a share outside means the cache did not engage, or held something
    else, and the request shape differs). On ``g37-image``, whose cache is
    implicit and affects cost only, the pass's token-weighted share must be
    at least 0.5 (Stage 1 card § 4.4's gate) unless the operator allows it.
``band LEG`` / ``estimate`` (audit A6; re-check R1)
    A union outside ±15 % of its guide size is refused until the operator
    names that leg in ``BAND_OK=<leg>[,<leg>]`` (Stage 2 card § 3); a blanket
    value is refused. The two ``temp1`` arms' guides are their T 0.7 twins'
    times 1.2 (:data:`T10_FACTOR`), the measured effect of T 1.0 on a
    five-pass Gemini 3 text union.
``repair LEG_DIR`` (audit A2)
    The batch path books a verifier response that does not parse with plain
    ``json.loads`` as ``mound_probability`` 0.0 with reasoning
    ``PARSE_ERROR: …`` (``lib_verifier.parse_verifier_results``), where every
    original leg's real-time path repaired it with
    ``lib_batch_api.parse_response_with_repair``. This re-parses those rows
    from the leg's ``batch_results.jsonl`` with the real-time path's own
    steps (fence stripping, ``parse_response_with_repair``,
    ``_unwrap_verdict_payload``) and writes the result to a SIBLING
    directory, ``<leg>_repaired/``: ``probabilities.json`` (the leg's, with
    the recovered rows replaced and every row that cannot be recovered
    REMOVED), ``run.meta.json`` (a byte copy of the leg's, so a clean-up
    there keeps its configuration gate) and ``parse_repair.json`` (which
    rows changed, from what to what, which could not be recovered, and the
    digest of each file written: a later ``repair`` refuses to overwrite a
    copy something else has changed, such as a clean-up's merge). A
    "recovered" row must carry ``mound_probability`` as a number in [0, 1].
    The leg directory is never written. Scoring reads ``--verify-dir
    <leg>_repaired``. A removed row is a missing candidate there, on
    purpose: the real-time path would have retried such a response, so
    scoring refuses (its join gate) until the
    row is re-verified (``run_pv.py cleanup --verified-dir <leg>_repaired``,
    a real-time call that needs the PI's go; Stage 2 card § 7), rather than
    silently scoring a 0.0. Of the nine PARSE_ERROR rows in the twenty
    committed batch legs, two repair (an extra closing brace) and seven do
    not (an unescaped quote inside a string).

Usage::

    python scripts/modality_bridge_stage2_checks.py metas g3-image --out OUT
    python scripts/modality_bridge_stage2_checks.py band g37-text:g3 --out OUT
    python scripts/modality_bridge_stage2_checks.py estimate --out OUT
    python scripts/modality_bridge_stage2_checks.py repair \\
        OUT/g37-text/verifier/detect_brief-text/verify_g3

Zero API.

Created: 2026-10-08
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

#: Model names the two verifier legs pin, and the Stage 1 arms' proposers.
G3_MODEL = "gemini-3-flash-preview"
G37_MODEL = "gemini-3.7-flash"

#: The review band around a union's guide size (Stage 2 card § 3).
BAND = 0.15

#: An explicit-cache pass sends 18,909 of about 20,020 input tokens from the
#: cache (0.9445 measured on all ten landed g3-image passes, 2026-10-07); the
#: window is "about 0.94".
EXPLICIT_SHARE_RANGE = (0.92, 0.97)

#: The implicit-cache gate of the Stage 1 card (§ 4.4): cost only.
IMPLICIT_MIN_SHARE = 0.50


@dataclass(frozen=True)
class ArmSpec:
    """What one Stage 1 arm sent, and how big its union was expected to be."""

    k: int
    version: str
    model: str
    temperature: float
    thinking: str
    cache: str  # "explicit", "implicit" or "none"
    guide: int
    guide_source: str


#: The seven arms (Stage 1 card §§ 4.2, 4.8; Stage 2 card § 3 for guides).
ARMS: dict[str, ArmSpec] = {
    "g3-text": ArmSpec(10, "detect_brief-text", G3_MODEL, 0.7, "minimal", "none",
                       3319, "original union_k10"),
    "g3-image": ArmSpec(10, "detect_brief-text-image", G3_MODEL, 0.7, "minimal",
                        "explicit", 4065, "original union_k10"),
    "g37-text": ArmSpec(5, "detect_brief-text", G37_MODEL, 0.7, "low", "none",
                        791, "original union_k5"),
    "g37-image": ArmSpec(5, "detect_brief-text-image", G37_MODEL, 0.7, "low",
                         "implicit", 674, "original union_k5"),
    "g37-image-cache": ArmSpec(5, "detect_brief-text-image", G37_MODEL, 0.7, "low",
                               "explicit", 674, "twin g37-image"),
    "g3-text-temp1": ArmSpec(5, "detect_brief-text", G3_MODEL, 1.0, "minimal", "none",
                             3257, "T 0.7 guide 2,714 x 1.2 (T 1.0)"),
    "g3-image-temp1": ArmSpec(5, "detect_brief-text-image", G3_MODEL, 1.0, "minimal",
                              "explicit", 3346, "T 0.7 guide 2,788 x 1.2 (T 1.0)"),
}

#: The T 1.0 factor on the temp1 guides (Stage 2 audit re-check, R1). The
#: committed h11 Gemini 3 text arms (outputs/h11/pv-diag-384/
#: flash-minimal-text-n30-t07/text-t0.7 and text-t1.0; 487 tiles, minimal
#: thinking) give five-pass unions, through this chain's 20 m dedup and c = 1
#: clustering, of 1,593 -> 1,926 (passes 1-5, x1.209) and 1,569 -> 1,865
#: (passes 6-10, x1.189): the passes agree less at T 1.0, raw detections per
#: pass barely move. The image factor is assumed equal; none is measured.
T10_FACTOR = 1.2

#: The ten verifier legs, ARM:V.
LEGS: tuple[str, ...] = (
    "g3-text:g3", "g3-image:g3", "g37-text:g3", "g37-text:g37", "g37-image:g3",
    "g37-image:g37", "g37-image-cache:g3", "g37-image-cache:g37",
    "g3-text-temp1:g3", "g3-image-temp1:g3",
)

#: Audited cost per candidate of the original legs (cost_audit.json), as a
#: (low, high) range per verifier; the 3.7 text swap leg's register row is a
#: lower bound, so its card token basis (US$0.87 / 791) is used.
RATES: dict[str, tuple[float, float]] = {
    "g3": (2.271158 / 3319, 0.478101 / 674),
    "g37": (0.737004 / 674, 0.87 / 791),
}


# ---------------------------------------------------------------------------
# A5: the pass metas
# ---------------------------------------------------------------------------


def meta_path(pass_file: Path) -> Path:
    """Return the ``.meta.json`` sibling of a detections GeoJSON."""
    return pass_file.with_name(pass_file.name.removesuffix(".geojson") + ".meta.json")


def _share(usage: dict) -> tuple[float | None, int, int]:
    """Cached share and the two token totals of a meta's usage block."""
    inp = int(usage.get("total_input_tokens") or 0)
    cached = int(usage.get("total_cached_tokens") or 0)
    share = usage.get("cached_share")
    if share is None and inp:
        share = cached / inp
    return (None if share is None else float(share)), inp, cached


def check_metas(arm: str, out: Path, allow_low_implicit: bool = False,
                ) -> dict[str, Any]:
    """Check every pass file's meta of an arm against what the arm sends.

    Args:
        arm: Arm name (a key of :data:`ARMS`).
        out: The campaign output root (``outputs/modality-bridge-2026-10-07``).
        allow_low_implicit: Accept a ``g37-image`` pass whose implicit cached
            share is under :data:`IMPLICIT_MIN_SHARE` (cost only).

    Returns:
        ``{"arm", "ok", "problems", "passes": [...]}`` with, per pass, each
        file's model, temperature, thinking level and cached share.
    """
    from scripts.modality_bridge_union import resolve_batch_pass_paths

    spec = ARMS[arm]
    cell = out / arm / spec.version
    problems: list[str] = []
    passes: list[dict[str, Any]] = []
    for i in range(1, spec.k + 1):
        run = f"run_{i}"
        try:
            files = resolve_batch_pass_paths(cell, run)
        except FileNotFoundError as exc:
            problems.append(f"{run}: {exc}")
            continue
        rows = []
        tin = tcached = 0
        for f in files:
            mp = meta_path(f)
            if not mp.exists():
                problems.append(f"{run}: no meta beside {f.name}")
                continue
            meta = json.loads(mp.read_text())
            cfg = meta.get("configuration") or {}
            share, inp, cached = _share(meta.get("usage_stats") or {})
            tin += inp
            tcached += cached
            row = {"file": str(mp), "model": cfg.get("model"),
                   "temperature": cfg.get("temperature"),
                   "thinking_level": cfg.get("thinking_level"), "cached_share": share}
            rows.append(row)
            label = f"{run} {mp.name}"
            if cfg.get("model") != spec.model:
                problems.append(f"{label}: model {cfg.get('model')!r}, want {spec.model!r}")
            temp = cfg.get("temperature")
            if temp is None or abs(float(temp) - spec.temperature) > 1e-9:
                problems.append(f"{label}: temperature {temp!r}, want {spec.temperature}")
            if str(cfg.get("thinking_level") or "").lower() != spec.thinking:
                problems.append(f"{label}: thinking level {cfg.get('thinking_level')!r}, "
                                f"want {spec.thinking!r}")
            lo, hi = EXPLICIT_SHARE_RANGE
            if spec.cache == "explicit" and (share is None or not lo <= share <= hi):
                problems.append(f"{label}: cached share {share}, want {lo}-{hi} (the "
                                "explicit cache did not engage as designed: a different "
                                "request shape; discard the pass and re-lodge it)")
        pass_share = tcached / tin if tin else None
        if (spec.cache == "implicit" and not allow_low_implicit
                and (pass_share is None or pass_share < IMPLICIT_MIN_SHARE)):
            problems.append(f"{run}: implicit cached share {pass_share}, want >= "
                            f"{IMPLICIT_MIN_SHARE} (cost only; IMPLICIT_SHARE_OK=1 accepts it)")
        passes.append({"run": run, "files": rows, "pass_cached_share": pass_share})
    return {"arm": arm, "ok": not problems, "problems": problems, "passes": passes}


# ---------------------------------------------------------------------------
# A6: the review band, and the estimate
# ---------------------------------------------------------------------------


def union_size(arm: str, out: Path) -> int | None:
    """The built union's feature count from its build record, or None."""
    spec = ARMS[arm]
    build = out / arm / "verifier" / spec.version / f"union_k{spec.k}.build.json"
    if not build.exists():
        return None
    return int(json.loads(build.read_text())["union_features"])


def band_for(arm: str) -> tuple[int, int]:
    """The review band (inclusive, rounded) around an arm's guide size."""
    g = ARMS[arm].guide
    return round(g * (1 - BAND)), round(g * (1 + BAND))


def in_band(arm: str, n: int) -> bool:
    """True when a union of n candidates lies inside the arm's band."""
    lo, hi = band_for(arm)
    return lo <= n <= hi


def parse_band_ok(value: str | None) -> set[str]:
    """Parse ``BAND_OK``: the legs, by name, the operator lets past the band.

    The override is per leg (Stage 2 audit re-check, R1): a blanket value
    such as ``1`` or ``all`` would also waive the band for every D49 leg of a
    ``verify all``, so it is refused.

    Args:
        value: ``"g3-text-temp1:g3,g3-image-temp1:g3"`` (commas or spaces),
            or empty.

    Returns:
        The named legs.

    Raises:
        ValueError: If a name is not one of :data:`LEGS`.

    Examples:
        >>> sorted(parse_band_ok("g37-text:g3, g37-text:g37"))
        ['g37-text:g3', 'g37-text:g37']
    """
    legs = {x for x in (value or "").replace(",", " ").split() if x}
    unknown = sorted(legs - set(LEGS))
    if unknown:
        raise ValueError(f"BAND_OK names legs, e.g. BAND_OK=g3-text-temp1:g3; not "
                         f"{unknown} (a blanket waiver is not accepted)")
    return legs


def estimate(out: Path) -> dict[str, Any]:
    """Per leg: candidates (built union, else guide), band, flag and cost."""
    rows = []
    lo_t = hi_t = 0.0
    for leg in LEGS:
        arm, v = leg.split(":")
        built = union_size(arm, out)
        n = built if built is not None else ARMS[arm].guide
        lo, hi = sorted(n * r for r in RATES[v])
        lo_t += lo
        hi_t += hi
        rows.append({"leg": leg, "n": n, "source": "union" if built is not None else "guide",
                     "band": band_for(arm),
                     "out_of_band": built is not None and not in_band(arm, built),
                     "cost": (lo, hi)})
    return {"rows": rows, "total": (lo_t, hi_t)}


# ---------------------------------------------------------------------------
# A2: re-parse PARSE_ERROR rows with the real-time path's repair
# ---------------------------------------------------------------------------


def repair_text(text: str) -> dict:
    """Parse one verifier response as the real-time path does.

    Mirrors ``lib_verifier._call_verifier_api``: strip Markdown fences, parse
    with ``parse_response_with_repair``, unwrap a list-shaped payload.

    Args:
        text: The response text (``parts[0].text``).

    Returns:
        The verdict fields the batch parser books.

    Raises:
        ValueError: If the text cannot be repaired.
    """
    import math

    from scripts.lib_batch_api import parse_response_with_repair
    from scripts.lib_verifier import _unwrap_verdict_payload

    txt = text.replace("```json", "").replace("```", "").strip()
    verdict = _unwrap_verdict_payload(parse_response_with_repair(txt))
    # A payload without a usable probability is not a recovery: the
    # real-time path would book 0.0 by default, which is exactly the silent
    # 0.0 this step exists to avoid (Stage 2 audit re-check, R2).
    prob = verdict.get("mound_probability")
    if (isinstance(prob, bool) or not isinstance(prob, (int, float))
            or not math.isfinite(prob) or not 0.0 <= prob <= 1.0):
        raise ValueError(f"repaired payload has no mound_probability in [0, 1] "
                         f"(got {prob!r})")
    return {
        "mound_probability": float(prob),
        "reasoning": verdict.get("reasoning", ""),
        "best_alternative": verdict.get("best_alternative", ""),
        "alternative_evidence": verdict.get("alternative_evidence", ""),
    }


def _response_text(row: dict) -> str | None:
    """``response.candidates[0].content.parts[0].text`` of a batch row, or None."""
    try:
        return row["response"]["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return None


class RepairRefused(RuntimeError):
    """The repaired copy holds files ``repair`` did not write (R3)."""


#: The files ``repair`` writes into the repaired copy and records digests of.
REPAIR_OUTPUTS = ("probabilities.json", "run.meta.json")


def _digest(path: Path) -> str | None:
    """SHA-256 of a file, or None when it does not exist."""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def check_repaired_copy_untouched(out_dir: Path) -> None:
    """Refuse to overwrite a repaired copy that something else has written to.

    The repaired copy is where ``run_pv.py cleanup`` merges re-verified
    candidates (Stage 2 card § 7). A second ``repair`` that rewrote it would
    discard those paid results (Stage 2 audit re-check, R3). ``repair``
    records the digest of every file it writes (``parse_repair.json``,
    ``written``); a copy whose ``probabilities.json`` or ``run.meta.json``
    is missing from that record or no longer matches it is refused.

    Args:
        out_dir: The repaired copy.

    Raises:
        RepairRefused: If a file was written or changed by something else.
    """
    if not out_dir.exists():
        return
    record_path = out_dir / "parse_repair.json"
    written = (json.loads(record_path.read_text()).get("written") or {}
               if record_path.exists() else {})
    for name in REPAIR_OUTPUTS:
        now = _digest(out_dir / name)
        if now is not None and now != written.get(name):
            raise RepairRefused(
                f"{out_dir / name} was not written by repair, or has changed since "
                "(a clean-up merged into it?); re-running repair would discard it. "
                "Move the repaired copy to archive/ first if that is intended.")


def repair_leg(leg_dir: Path, out_dir: Path | None = None) -> dict[str, Any]:
    """Re-parse a leg's PARSE_ERROR rows; write the repaired leg beside it.

    Writes ``probabilities.json`` (repaired), ``run.meta.json`` (a byte copy
    of the leg's, so that ``run_pv.py cleanup --verified-dir <leg>_repaired``
    keeps its configuration gate; Stage 2 audit re-check, R4) and
    ``parse_repair.json`` (what changed, and the digest of each file it
    wrote, which a later run checks before overwriting; R3).

    Args:
        leg_dir: The verifier leg directory (``probabilities.json``,
            ``batch_results.jsonl`` and ``run.meta.json``). Never written.
        out_dir: Destination (default ``<leg_dir>_repaired``).

    Returns:
        The repair record (also written as ``parse_repair.json``).

    Raises:
        FileNotFoundError: If an input file is missing.
        RepairRefused: If the repaired copy holds files repair did not write.
    """
    out_dir = out_dir or leg_dir.with_name(leg_dir.name + "_repaired")
    check_repaired_copy_untouched(out_dir)
    probs_path = leg_dir / "probabilities.json"
    raw_path = leg_dir / "batch_results.jsonl"
    probs = json.loads(probs_path.read_text())
    results = probs["results"]
    targets = {k for k, v in results.items()
               if str(v.get("reasoning", "")).startswith("PARSE_ERROR")}
    raw: dict[str, dict] = {}
    with open(raw_path) as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("key") in targets:
                raw[row["key"]] = row
    changed, unrecovered = [], []
    for key in sorted(targets):
        text = _response_text(raw.get(key, {}))
        before = results[key]
        if text is None:
            unrecovered.append({"key": key, "why": "no response text in batch_results.jsonl",
                                "reasoning": before.get("reasoning")})
            del results[key]
            continue
        try:
            after = repair_text(text)
        except (ValueError, TypeError) as exc:
            unrecovered.append({"key": key, "why": f"repair failed: {exc}",
                                "reasoning": before.get("reasoning"),
                                "text_sha256": hashlib.sha256(text.encode()).hexdigest()})
            del results[key]
            continue
        changed.append({"key": key, "before": before.get("mound_probability"),
                        "after": after["mound_probability"],
                        "before_reasoning": before.get("reasoning"),
                        "text_sha256": hashlib.sha256(text.encode()).hexdigest()})
        results[key] = dict(before, **after)
    record = {
        "script": "scripts/modality_bridge_stage2_checks.py repair",
        "method": "lib_batch_api.parse_response_with_repair after Markdown-fence "
                  "stripping, then lib_verifier._unwrap_verdict_payload: the real-time "
                  "path's parse (lib_verifier._call_verifier_api)",
        "leg_dir": str(leg_dir),
        "source_probabilities_sha256": hashlib.sha256(probs_path.read_bytes()).hexdigest(),
        "source_batch_results_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "n_results": len(probs["results"]) + len(unrecovered),
        "n_results_written": len(results),
        "n_parse_error_rows": len(targets),
        "changed": changed,
        "unrecovered": unrecovered,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    if "total_results" in probs:
        probs["total_results"] = len(results)
    probs["parse_repair"] = {"record": "parse_repair.json", "n_changed": len(changed),
                             "n_unrecovered_removed": len(unrecovered),
                             "removed_keys": [u["key"] for u in unrecovered]}
    (out_dir / "probabilities.json").write_text(json.dumps(probs, indent=2) + "\n")
    meta_src = leg_dir / "run.meta.json"
    if meta_src.exists():
        # A byte copy: the clean-up's configuration gate compares against
        # the leg's own main-pass configuration. It is the same leg, not a
        # second spend (Stage 2 card § 8).
        shutil.copyfile(meta_src, out_dir / "run.meta.json")
    record["run_meta_copied_from"] = str(meta_src) if meta_src.exists() else None
    record["source_run_meta_sha256"] = _digest(meta_src)
    record["written"] = {name: _digest(out_dir / name) for name in REPAIR_OUTPUTS
                         if (out_dir / name).exists()}
    (out_dir / "parse_repair.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Run one check.

    Returns:
        0 when the check passed (``repair``: when no PARSE_ERROR row remains
        unrecovered), 1 when it refused, 2 on a bad ``BAND_OK``, 3 when there
        is nothing to check yet (``band``: no union) or ``repair`` refuses to
        overwrite a repaired copy.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("metas")
    m.add_argument("arm", choices=sorted(ARMS))
    m.add_argument("--out", type=Path, required=True)
    m.add_argument("--allow-low-implicit-share", action="store_true")
    m.add_argument("--json-out", type=Path, default=None)
    b = sub.add_parser("band")
    b.add_argument("leg", choices=LEGS)
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--band-ok", default="", help="BAND_OK: legs let past the band")
    e = sub.add_parser("estimate")
    e.add_argument("--out", type=Path, required=True)
    e.add_argument("--band-ok", default="", help="BAND_OK: legs let past the band")
    r = sub.add_parser("repair")
    r.add_argument("leg_dir", type=Path)
    r.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args(argv)

    if args.cmd == "metas":
        res = check_metas(args.arm, args.out, args.allow_low_implicit_share)
        if args.json_out is not None:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(json.dumps(res, indent=1) + "\n")
        for p in res["problems"]:
            print(f"{args.arm}: META MISMATCH — {p}")
        if res["ok"]:
            shares = [p["pass_cached_share"] for p in res["passes"]]
            print(f"{args.arm}: metas OK — {ARMS[args.arm].model}, T "
                  f"{ARMS[args.arm].temperature}, thinking {ARMS[args.arm].thinking}, "
                  f"cache {ARMS[args.arm].cache}; pass cached shares "
                  f"{[None if s is None else round(s, 4) for s in shares]}")
        return 0 if res["ok"] else 1
    if args.cmd in ("band", "estimate"):
        try:
            waived = parse_band_ok(args.band_ok)
        except ValueError as exc:
            print(f"REFUSED: {exc}")
            return 2
    if args.cmd == "band":
        arm = args.leg.split(":")[0]
        n = union_size(arm, args.out)
        lo, hi = band_for(arm)
        if n is None:
            print(f"{args.leg}: no union built yet — run `prepare {arm}` first")
            return 3
        if in_band(arm, n):
            print(f"{args.leg}: union {n} inside the band {lo}-{hi} (guide "
                  f"{ARMS[arm].guide}, {ARMS[arm].guide_source})")
            return 0
        print(f"{args.leg}: OUT OF BAND — union {n} outside {lo}-{hi} (guide "
              f"{ARMS[arm].guide}, {ARMS[arm].guide_source}). A surprising finding: "
              f"raise it with the PI; BAND_OK={args.leg} lets this leg proceed.")
        if args.leg in waived:
            print(f"{args.leg}: BAND_OK names this leg — proceeding, as the operator "
                  "decided")
            return 0
        return 1
    if args.cmd == "estimate":
        est = estimate(args.out)
        refused = []
        for row in est["rows"]:
            lo, hi = row["cost"]
            flag = ""
            if row["out_of_band"]:
                flag = ("OUT OF BAND (BAND_OK)" if row["leg"] in waived else "OUT OF BAND")
                if row["leg"] not in waived:
                    refused.append(row["leg"])
            print(f"{row['leg']:22s} {row['n']:6d} ({row['source']:5s})  band "
                  f"{row['band'][0]:5d}-{row['band'][1]:<5d}  US${lo:6.2f} - {hi:6.2f}  {flag}")
        lo, hi = est["total"]
        print(f"{'total':22s} {'':34s}  US${lo:6.2f} - {hi:6.2f}")
        if refused:
            print(f"REFUSED: outside the review band (Stage 2 card § 3): {refused}; raise "
                  f"it with the PI, then BAND_OK={','.join(refused)}")
            return 1
        return 0
    try:
        rec = repair_leg(args.leg_dir, args.out_dir)
    except RepairRefused as exc:
        print(f"{args.leg_dir}: REFUSED — {exc}")
        return 3
    print(f"{args.leg_dir}: {rec['n_parse_error_rows']} PARSE_ERROR row(s); "
          f"{len(rec['changed'])} recovered, {len(rec['unrecovered'])} not")
    for c in rec["changed"]:
        print(f"    {c['key']}: {c['before']} -> {c['after']}")
    for u in rec["unrecovered"]:
        print(f"    {u['key']}: UNRECOVERED, removed from the repaired copy ({u['why'][:80]})")
    if rec["unrecovered"]:
        print("  Removed rows are missing candidates in the repaired leg: scoring refuses "
              "until they are re-verified (run_pv.py cleanup, real time; the PI's go; card § 7)")
    return 0 if not rec["unrecovered"] else 1


if __name__ == "__main__":
    sys.exit(main())
