#!/usr/bin/env python3
"""Verify the ``evaluation.md`` generated family against sibling JSONs.

Phase 3 generated-stratum re-derivation (``planning/audit-charter.md``
§ 7; GATE 0 decision 2). ``scripts/evaluate_detections.py`` has no
render-only mode, so instead of byte-regeneration this comparer parses
every committed ``evaluation.md`` table and checks each cell against the
same-directory ``evaluation.json`` at quoted precision
(``scripts/lib_c4_compare.py``): the markdown asserts nothing the JSON
does not support.

Checked per file: the ``**Detections**`` count; per buffer row — F1 /
P / R points and confidence intervals (CIs), and, where the MCC-widened
header is present, MCC + MCC CI + sensitivity + specificity (constant
across buffers, from ``summary.tile_classification``). ``N/A *`` CI
cells (bootstrap unreliable) are checked for consistency with the
JSON's ``ci_unreliable`` flags, and ``undefined`` tile-metric cells
(erratum E81 — degenerate 2 x 2 tile confusion matrix) are checked for
definedness agreement with the JSON's ``null``.

Verdicts per file: VERIFIED / MISMATCH (cells listed) / PARSE-FAIL /
NO-SOURCE. Deterministic; run on sapphire per project compute policy.

Usage::

    python3 scripts/verify_evaluation_md_family.py \
        [--registry reports/verification/generated-file-registry.json] \
        [--out reports/verification/c4-regen/evaluation-md-report.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_c4_compare import match_at_quoted_precision, parse_value  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = REPO_ROOT / "reports" / "verification" / "generated-file-registry.json"
DEFAULT_OUT = REPO_ROOT / "reports" / "verification" / "c4-regen" / "evaluation-md-report.json"

DETECTIONS_RE = re.compile(r"^\*\*Detections\*\*:\s*([\d,]+)")
ROW_RE = re.compile(r"^\|\s*(\d+)m\s*\|")
CI_RE = re.compile(r"^\[\s*([-\d.]+),\s*([-\d.]+)\s*\]$")

#: The literal string ``evaluate_detections.py`` writes into a
#: tile-metric cell whose value is not computable — its
#: ``UNDEFINED_DISPLAY`` constant. Erratum E81 (2026-08-18): when the
#: 2 x 2 tile confusion matrix is degenerate the Matthews Correlation
#: Coefficient (MCC) has no value, and the JSON now carries ``null``
#: where it used to carry a coerced ``0.0``. A markdown cell reading
#: this word against a ``null`` source is a PASS — the two agree that
#: no measurement exists. A number against ``null`` (or this word
#: against a number) is a MISMATCH.
UNDEFINED_DISPLAY = "undefined"


def check_cell(quoted: str, actual, cell: str, problems: list[str]) -> None:
    """Compare one quoted markdown cell against a source value."""
    parsed = parse_value(quoted)
    if parsed is None:
        if quoted.startswith("N/A"):
            return  # point-value N/A markers mirror absent source values
        problems.append(f"{cell}: unparseable quote {quoted!r}")
        return
    if actual is None:
        problems.append(f"{cell}: quoted {quoted} but source value absent")
        return
    result = match_at_quoted_precision(parsed, float(actual))
    if not result["match"]:
        problems.append(f"{cell}: quoted {quoted} vs source {actual}")


def check_cell_either(quoted: str, record: dict, cell: str,
                      problems: list[str]) -> None:
    """Compare a cell the renderer fills from the bootstrap mean.

    Accepts a match against ``mean`` (the renderer's key) or ``point``
    (the JSON headline); reports a problem only when neither matches.
    """
    trial: list[str] = []
    check_cell(quoted, record.get("mean"), cell, trial)
    if not trial:
        return
    trial2: list[str] = []
    check_cell(quoted, record.get("point"), cell, trial2)
    if not trial2:
        return
    problems.append(f"{cell}: quoted {quoted} matches neither mean "
                    f"{record.get('mean')} nor point {record.get('point')}")


def check_tile_metric(quoted: str, record: dict, cell: str,
                      problems: list[str]) -> None:
    """Compare a tile-metric cell, allowing an explicitly undefined value.

    Wraps :func:`check_cell_either` with the erratum-E81 branch: a tile
    metric is *undefined* when its JSON block carries ``null`` in both
    ``mean`` and ``point`` (a degenerate 2 x 2 tile confusion matrix
    leaves the coefficient with no value), and the renderer writes the
    word :data:`UNDEFINED_DISPLAY` for it. Definedness must agree on
    both sides:

    * word vs ``null`` — PASS (both say "no measurement");
    * number vs ``null`` — MISMATCH (the markdown asserts a
      measurement the JSON does not support, which is the defect E81
      exists to catch);
    * word vs number — MISMATCH (the markdown hides a measurement);
    * number vs number — falls through to the normal comparison, so a
      genuine 0.000 is still checked as a number.

    Args:
        quoted: The markdown cell text, stripped.
        record: The metric's JSON block (``mean`` / ``point`` / CI).
        cell: Cell identifier for the problem message.
        problems: Accumulator the caller renders into the verdict.
    """
    defined = (
        record.get("mean") is not None or record.get("point") is not None
    )
    if quoted == UNDEFINED_DISPLAY:
        if defined:
            problems.append(
                f"{cell}: quoted {UNDEFINED_DISPLAY!r} but JSON records "
                f"mean {record.get('mean')} / point {record.get('point')}",
            )
        return
    if not defined:
        problems.append(
            f"{cell}: quoted {quoted} but the JSON metric is undefined "
            f"(mean and point are both null) — it should read "
            f"{UNDEFINED_DISPLAY!r}",
        )
        return
    check_cell_either(quoted, record, cell, problems)


def check_ci(quoted: str, lo, hi, unreliable: bool, cell: str,
             problems: list[str]) -> None:
    """Compare a CI cell — ``[a, b]``, ``N/A *``, or ``undefined``.

    Erratum E81: an MCC CI whose bounds are ``null`` is rendered as the
    whole-cell word :data:`UNDEFINED_DISPLAY` rather than as an
    interval. That must PASS against ``null`` bounds and FAIL against
    present ones.
    """
    if quoted == UNDEFINED_DISPLAY:
        if lo is not None or hi is not None:
            problems.append(
                f"{cell}: quoted {UNDEFINED_DISPLAY!r} but JSON CI is "
                f"present ([{lo}, {hi}])",
            )
        return
    if quoted.startswith("N/A"):
        if not unreliable and lo is not None:
            problems.append(f"{cell}: N/A quoted but JSON CI present and reliable")
        return
    match = CI_RE.match(quoted)
    if not match:
        problems.append(f"{cell}: unparseable CI {quoted!r}")
        return
    if lo is None or hi is None:
        problems.append(f"{cell}: CI quoted but JSON CI absent")
        return
    check_cell(match.group(1), lo, f"{cell}.lo", problems)
    check_cell(match.group(2), hi, f"{cell}.hi", problems)


def verify_file(md_path: Path, json_path: Path) -> dict:
    """Verify one evaluation.md against its sibling evaluation.json."""
    problems: list[str] = []
    try:
        source = json.loads(json_path.read_text(encoding="utf-8"))
        lines = md_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, json.JSONDecodeError) as exc:
        return {"file": str(md_path.relative_to(REPO_ROOT)),
                "verdict": "PARSE-FAIL", "problems": [str(exc)]}

    summary = source.get("summary", source)
    by_buffer = {b["buffer_metres"]: b for b in summary.get("buffers", [])}
    tc = summary.get("tile_classification") or {}

    rows_checked = 0
    for line in lines:
        det = DETECTIONS_RE.match(line)
        if det:
            check_cell(det.group(1), summary.get("n_detections"), "detections", problems)
            continue
        row = ROW_RE.match(line)
        if not row:
            continue
        buffer_m = int(row.group(1))
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        buf = by_buffer.get(buffer_m)
        if buf is None:
            problems.append(f"{buffer_m}m: row has no JSON buffer record")
            continue
        rows_checked += 1
        unreliable = bool(buf.get("ci_unreliable"))
        # cells: Buffer, F1, F1 CI, P, P CI, R, R CI [, MCC, MCC CI, Sens, Spec]
        if len(cells) < 7:
            problems.append(f"{buffer_m}m: short row ({len(cells)} cells)")
            continue
        check_cell(cells[1], buf.get("f1"), f"{buffer_m}m.f1", problems)
        check_ci(cells[2], buf.get("f1_ci_lower"), buf.get("f1_ci_upper"),
                 unreliable, f"{buffer_m}m.f1_ci", problems)
        check_cell(cells[3], buf.get("precision"), f"{buffer_m}m.p", problems)
        check_ci(cells[4], buf.get("p_ci_lower"), buf.get("p_ci_upper"),
                 unreliable, f"{buffer_m}m.p_ci", problems)
        check_cell(cells[5], buf.get("recall"), f"{buffer_m}m.r", problems)
        check_ci(cells[6], buf.get("r_ci_lower"), buf.get("r_ci_upper"),
                 unreliable, f"{buffer_m}m.r_ci", problems)
        if len(cells) >= 11 and tc:
            # The renderer prints the bootstrap MEAN for these columns
            # (evaluate_detections.py:834,837), not the point estimate;
            # accept mean first, point as fallback, and record which.
            # E81: any of the three tile metrics may be undefined, so
            # these go through check_tile_metric rather than
            # check_cell_either — a rendered "undefined" against a
            # null JSON value is a PASS, not an unparseable quote.
            mcc, sens, spec = tc.get("mcc", {}), tc.get("sensitivity", {}), tc.get("specificity", {})
            check_tile_metric(cells[7], mcc, f"{buffer_m}m.mcc", problems)
            check_ci(cells[8], mcc.get("ci_lower"), mcc.get("ci_upper"),
                     unreliable, f"{buffer_m}m.mcc_ci", problems)
            check_tile_metric(cells[9], sens, f"{buffer_m}m.sens", problems)
            check_tile_metric(cells[10], spec, f"{buffer_m}m.spec", problems)

    if rows_checked == 0:
        return {"file": str(md_path.relative_to(REPO_ROOT)),
                "verdict": "PARSE-FAIL", "problems": ["no buffer rows parsed"] + problems}
    verdict = "VERIFIED" if not problems else "MISMATCH"
    return {"file": str(md_path.relative_to(REPO_ROOT)), "verdict": verdict,
            "rows_checked": rows_checked, "problems": problems}


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    targets = [e for e in registry["files"] if e.get("rule_id") == "gen-evaluation-md"]
    results = []
    for entry in targets:
        md_path = REPO_ROOT / entry["path"]
        json_path = md_path.parent / "evaluation.json"
        if not json_path.exists():
            results.append({"file": entry["path"], "verdict": "NO-SOURCE",
                            "problems": ["sibling evaluation.json missing"]})
            continue
        results.append(verify_file(md_path, json_path))

    counts: dict[str, int] = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    report = {"_meta": {"generator": "scripts/verify_evaluation_md_family.py",
                        "family": "gen-evaluation-md", "counts": counts},
              "results": results}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("counts:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    bad = [r for r in results if r["verdict"] not in ("VERIFIED",)]
    for r in bad[:20]:
        print(f"  {r['verdict']}: {r['file']}: {r['problems'][:3]}")
    if len(bad) > 20:
        print(f"  ... and {len(bad) - 20} more (see report)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
