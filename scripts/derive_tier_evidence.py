#!/usr/bin/env python3
"""
Derive the committed service-tier evidence the passes register prices from.

Why this script exists
----------------------
A pass's cost depends on the service tier it ran at (standard, flex or the
Batch API), and before 2026-09-21 no run meta recorded its tier. The
register therefore needs evidence from outside the meta, and that evidence
must be COMMITTED so that the register regenerates identically on any clone
(``planning/cost-accounting-fix-plan-2026-09-21.md`` § 4.3; PI rulings
D11 to D18 in ``planning/pi-decisions-2026-09-20.md``). Two sources exist:

1. **Billing exports** (``billing``). The Google Cloud billing console's
   monthly Cost table and single-day Reports exports, downloaded by the PI
   into ``docs/costs/`` (gitignored: the files carry billing-account and
   project identifiers). Each SKU names its model and, for discounted
   traffic, its tier (``... flex``, ``... batch``). This subcommand reduces
   them to which tiers billed which model on which **Pacific-time** billing
   day (Cloud Billing dates usage in US Pacific time; established in
   ``reports/billing-reconciliation-2026-09-11.md`` § 3.1) and writes
   ``data/pricing/billing-day-tiers.json`` with no identifiers in it.
2. **Run logs** (``logs``). From 2026-04-09 (commit ``2a2cd81c7``) the
   detection runner prints ``Service tier: <tier>`` at launch. This
   subcommand sweeps every ``*.log`` under ``outputs/`` and writes
   ``data/pricing/run-log-tiers.json``: per directory, the tiers its logs
   name, each log cited by path, SHA-256 and whether git tracks it. Run it
   on sapphire, which holds logs the workstation clone does not.

Interpretation rules (encoded once, here)
-----------------------------------------
- **SKU to model** is an explicit table (:data:`SKU_MODELS`), never a
  substring guess: ``gemini 3 flash`` must not swallow ``gemini 3.1 flash
  lite preview``, and ``Gemini 3 Pro Image`` is an image-GENERATION model,
  not the 3.1 Pro the project ran.
- **SKU to tier**: a SKU naming ``batch`` is batch; one naming ``flex`` is
  flex; a cache-read or cache-storage SKU naming neither carries no tier
  signal (Gemini 3 Flash bills its cache read under one SKU at every tier);
  anything else is standard.
- **Project filter.** Cost tables carry a project column and are filtered
  to ``map-reader-llm`` here. Reports exports do not, so each is classed:
  ``documented`` (the five 28 Aug - 1 Sep exports the 2026-09-11
  reconciliation states were project-filtered, pinned by SHA-256),
  ``contaminated`` (it carries a SKU ``map-reader-llm`` was never invoiced
  for that month, so it cannot have been filtered), or ``unverified``.
  An unfiltered export can only ADD tiers to a day, never remove one, so a
  day it shows as single-tier is still valid evidence; a day it shows as
  mixed may be mixed only because of another project's traffic.

Usage::

    # On the workstation (where docs/costs/ lives):
    python3 scripts/derive_tier_evidence.py billing

    # On sapphire (where every run log lives):
    python3 scripts/derive_tier_evidence.py logs

    # Either, without writing: print what would change.
    python3 scripts/derive_tier_evidence.py billing --check

Created: 2026-10-03 (WP3 of the cost accounting plan)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COSTS_DIR = PROJECT_ROOT / "docs" / "costs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
BILLING_OUT = PROJECT_ROOT / "data" / "pricing" / "billing-day-tiers.json"
LOGS_OUT = PROJECT_ROOT / "data" / "pricing" / "run-log-tiers.json"

#: The project whose spend the register accounts for.
PROJECT = "map-reader-llm"

#: Cloud Billing reports date usage in US Pacific time.
BILLING_TIMEZONE = "America/Los_Angeles"

#: SKU description (normalised: lower case, underscores as spaces) to the
#: model it bills. Order matters: the first pattern that matches wins, so
#: the specific ``3.1 flash lite`` and ``3 pro image`` rows precede the
#: general ``3 flash`` and ``3 pro`` rows. Canonical ids follow the rate
#: card (``data/pricing/gemini-rate-card.json``) where the card prices the
#: model; models the project never registered a pass for keep a plain id so
#: their spend is still visible.
SKU_MODELS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bgemini 3\.1 flash lite\b"), "gemini-3.1-flash-lite-preview"),
    (re.compile(r"\bgemini 3 pro image\b"), "gemini-3-pro-image"),
    (re.compile(r"\bgemini 3\.8 flash\b"), "gemini-3.8-flash"),
    (re.compile(r"\bgemini 3\.7 flash\b"), "gemini-3.7-flash"),
    (re.compile(r"\bgemini 3\.6 flash\b"), "gemini-3.6-flash"),
    (re.compile(r"\bgemini 3\.5 flash\b"), "gemini-3.5-flash"),
    (re.compile(r"\bgemini 3 pro\b"), "gemini-3.1-pro-preview"),
    (re.compile(r"\bgemini 3 flash\b"), "gemini-3-flash-preview"),
    (re.compile(r"\bgemini 2\.5 flash\b"), "gemini-2.5-flash"),
    (re.compile(r"\bgemini 2\.0 flash\b"), "gemini-2.0-flash"),
]

#: Reports exports the 2026-09-11 billing reconciliation records as
#: project-filtered (``reports/billing-reconciliation-2026-09-11.md`` § 3.1,
#: "five project-filtered daily exports, 28 Aug - 1 Sep"), pinned by the
#: SHA-256 of the file as downloaded so a later re-export cannot inherit the
#: status by name.
DOCUMENTED_FILTERED: dict[str, str] = {
    "956fc8c40108076d496a6aef7b022f93676776dcc324c1d83235032d8e4f5b29": "2026-08-28",
    "098d6351158f651d8dadab8c529b07c477e8c4aae1d8fda265b17c4f0515cbcc": "2026-08-29",
    "91def07b83981442e24a2ae115942967ef0602d3aa87fcd2fe412ca1b644bc13": "2026-08-30",
    "02bf738ef58161018b702680d1e7057e8ca836e98423cd5bbacc207ff0f0c2e8": "2026-08-31",
    "3968d1e5a92a38ecf0ca540cc785885e1b8d1027dd53218439cf35be76e0d623": "2026-09-01",
}

#: Preference when a day has more than one export.
FILTER_RANK = {"documented": 0, "unverified": 1, "contaminated": 2}

#: The runner's launch line (``scripts/4_detect_mounds_batch.py`` since
#: ``2a2cd81c7``): ``Service tier: flex``.
TIER_LINE = re.compile(r"service tier:\s*([a-z]+)", re.IGNORECASE)

#: The runner's line when it creates an EXPLICIT context cache
#: (``--use-cache``). It matters for the tier: the cached call path builds
#: its own request config without ``service_tier`` (see lib_pass_cost).
CACHE_LINE = re.compile(r"^Context cache created: ", re.MULTILINE)

#: A verifier COMMAND (``run_pv.py verify|cleanup`` or ``5_verify_crops``):
#: the line where a verifier stage starts, and whose own ``--service-tier``
#: switch is that stage's requested tier. Only a command marks the stage: a
#: looser pattern ("verif") is tripped by an output path such as
#: ``outputs/verifier-t-pilot/`` or by the word "unverified" (re-audit round 2).
VERIFIER_CMD = re.compile(r"run_pv\.py\s+(?:verify|cleanup)\b|5_verify_crops")
SWITCH = re.compile(r"--service-tier[= ]([a-z]+)")

#: Where one command ends on a combined command line.
COMMAND_END = re.compile(r"&&|\|\||;|\||&")

#: The service tiers a tier line may name; anything else is recorded as unknown
#: rather than passed on as a tier.
KNOWN_TIERS = ("standard", "flex", "batch")

REPORTS_NAME = re.compile(
    r"Reports, (\d{4}-\d{2}-\d{2}) [—-] (\d{4}-\d{2}-\d{2})(?: \((\d+)\))?\.csv$")
COST_TABLE_NAME = re.compile(r"Cost table, (\d{4}-\d{2})-\d{2} [—-] ")


# ---------------------------------------------------------------------------
# SKU interpretation.
# ---------------------------------------------------------------------------


def normalise_sku(sku: str) -> str:
    """Lower-case a SKU description and read underscores as spaces.

    Examples:
        >>> normalise_sku("Generate_content_cached_input_token_count_gemini_3_pro_short_image")
        'generate content cached input token count gemini 3 pro short image'
    """
    return re.sub(r"\s+", " ", sku.replace("_", " ").lower()).strip()


def sku_model(sku: str) -> str | None:
    """The model a SKU bills, by the explicit table, or None if no row matches.

    Examples:
        >>> sku_model("Generate content input token count gemini 3 flash text flex")
        'gemini-3-flash-preview'
        >>> sku_model("Generate content input token count gemini 3.1 flash lite preview text")
        'gemini-3.1-flash-lite-preview'
        >>> sku_model("Generate_content image output token count for Gemini 3 Pro Image")
        'gemini-3-pro-image'
    """
    s = normalise_sku(sku)
    for pattern, model in SKU_MODELS:
        if pattern.search(s):
            return model
    return None


def sku_tier(sku: str) -> str | None:
    """The tier a SKU names, or None for a tier-silent cache SKU.

    Examples:
        >>> sku_tier("Generate content output token count gemini 3 flash text flex")
        'flex'
        >>> sku_tier("Generate_content text output token count for gemini 3 flash batch")
        'batch'
        >>> sku_tier("Generate_content text output token count for gemini 3 flash")
        'standard'
        >>> sku_tier("Generate_content cached image input token count for gemini 3 flash") is None
        True
        >>> sku_tier("Generate content input token count gemini 3.7 flash image flex caching")
        'flex'
    """
    s = normalise_sku(sku)
    if "batch" in s:
        return "batch"
    if "flex" in s:
        return "flex"
    if "cached" in s or "storage" in s:
        return None
    return "standard"


def sku_class(sku: str) -> str:
    """Which billed token class a SKU counts: ``input``, ``output`` or ``other``.

    ``other`` is cache storage (token-hours), which is not a token count.

    Examples:
        >>> sku_class("Generate content output token count gemini 3 flash text flex")
        'output'
        >>> sku_class("Generate_content cached image input token count for gemini 3 flash")
        'input'
        >>> sku_class("Generate_content cached text storage token hours for gemini 3 flash")
        'other'
    """
    s = normalise_sku(sku)
    if "storage" in s:
        return "other"
    if "output" in s:
        return "output"
    if "input" in s:
        return "input"
    return "other"


def _amount(text: str) -> float:
    """Parse a console number such as ``"1,234,567"`` or ``"274,027.054"``."""
    return float(text.replace(",", "").strip() or 0)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Billing exports.
# ---------------------------------------------------------------------------


def read_cost_tables(costs_dir: Path) -> tuple[list[dict[str, Any]], dict[str, set[str]]]:
    """Every Gemini usage line billed to the project, from the monthly Cost tables.

    Args:
        costs_dir: Directory holding the console exports.

    Returns:
        ``(lines, skus_by_month)``: one dict per usage line (model, tier,
        start, end, tokens, AUD, month), and per month the SKU descriptions
        the project was invoiced for (the contamination test for Reports
        exports, which carry no project column).
    """
    lines: list[dict[str, Any]] = []
    skus_by_month: dict[str, set[str]] = defaultdict(set)
    for path in sorted(costs_dir.glob("*Cost table, *.csv")):
        m = COST_TABLE_NAME.search(path.name)
        if not m:
            continue
        month = m.group(1)
        header: list[str] | None = None
        with path.open(newline="", encoding="utf-8") as fh:
            for rec in csv.reader(fh):
                if header is None:
                    if "SKU description" in rec:
                        header = rec
                    continue
                if len(rec) < len(header):
                    continue
                row = dict(zip(header, rec))
                if (row["Project name"] != PROJECT or row["Service description"] != "Gemini API"
                        or row["Cost type"] != "Usage"):
                    continue
                sku = row["SKU description"].strip()
                skus_by_month[month].add(sku)
                lines.append({
                    "month": month,
                    "sku": sku,
                    "model": sku_model(sku),
                    "tier": sku_tier(sku),
                    "start": row["Usage start date"],
                    "end": row["Usage end date"],
                    "unit": row["Usage unit"],
                    "amount": _amount(row["Usage amount"]),
                    "aud": float(row["Unrounded cost ($)"] or 0),
                })
    return lines, skus_by_month


def read_day_exports(costs_dir: Path, skus_by_month: dict[str, set[str]]
                     ) -> dict[str, dict[str, Any]]:
    """The best single-day Reports export for each Pacific billing day.

    Args:
        costs_dir: Directory holding the console exports.
        skus_by_month: From :func:`read_cost_tables`.

    Returns:
        ``{day: {"project_filter", "sha256", "lines": [...], "alternatives": n}}``,
        choosing per day the export with the strongest filter status.
    """
    best: dict[str, dict[str, Any]] = {}
    seen: dict[str, int] = defaultdict(int)
    for path in sorted(costs_dir.glob("*Reports, *.csv")):
        m = REPORTS_NAME.search(path.name)
        if not m or m.group(1) != m.group(2):
            continue  # a range export, not a day
        day = m.group(1)
        digest = _sha256(path)
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        header = rows[0]
        lines = []
        for rec in rows[1:]:
            if len(rec) < len(header):
                continue
            row = dict(zip(header, rec))
            if row.get("Service description") != "Gemini API":
                continue
            sku = row["SKU description"].strip()
            lines.append({"sku": sku, "model": sku_model(sku), "tier": sku_tier(sku),
                          "amount": _amount(row["Usage amount"]),
                          "aud": float(row.get("Unrounded subtotal ($)") or 0)})
        month_skus = skus_by_month.get(day[:7])
        if digest in DOCUMENTED_FILTERED:
            status = "documented"
        elif month_skus is not None and any(
                ln["sku"] not in month_skus and ln["amount"] > 0 for ln in lines):
            status = "contaminated"
        else:
            status = "unverified"
        seen[day] += 1
        candidate = {"project_filter": status, "sha256": digest, "lines": lines}
        held = best.get(day)
        if held is None or FILTER_RANK[status] < FILTER_RANK[held["project_filter"]]:
            best[day] = candidate
    for day, entry in best.items():
        entry["alternatives"] = seen[day] - 1
    return best


def merge_intervals(spans: list[tuple[str, str]]) -> list[list[str]]:
    """Merge overlapping or adjacent ``(start, end)`` ISO-date spans.

    Examples:
        >>> merge_intervals([("2026-04-08", "2026-04-17"), ("2026-04-10", "2026-04-30"),
        ...                  ("2026-05-02", "2026-05-06")])
        [['2026-04-08', '2026-04-30'], ['2026-05-02', '2026-05-06']]
    """
    out: list[list[str]] = []
    for start, end in sorted(spans):
        if out and date.fromisoformat(start) <= date.fromisoformat(out[-1][1]) + timedelta(days=1):
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return out


def build_billing_evidence(costs_dir: Path) -> dict[str, Any]:
    """Reduce the console exports to the committed billing-day evidence.

    Args:
        costs_dir: Directory holding the console exports.

    Returns:
        The document written to ``data/pricing/billing-day-tiers.json``.
    """
    lines, skus_by_month = read_cost_tables(costs_dir)
    if not lines:
        raise SystemExit(f"derive_tier_evidence: no Cost table lines for {PROJECT} under "
                         f"{costs_dir}; download the monthly Cost tables first")
    # Intervals: the union of each line's own usage window, per model and tier.
    spans: dict[str, dict[str, list[tuple[str, str]]]] = defaultdict(lambda: defaultdict(list))
    months: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    for ln in lines:
        if ln["model"] is None or ln["amount"] <= 0:
            continue
        tier = ln["tier"] or "tier-silent"
        if ln["tier"] is not None:
            spans[ln["model"]][ln["tier"]].append((ln["start"], ln["end"]))
        cell = months[ln["month"]][ln["model"]]
        cell[tier] = round(cell.get(tier, 0.0) + ln["aud"], 6)
    intervals = {model: {tier: merge_intervals(s) for tier, s in sorted(by_tier.items())}
                 for model, by_tier in sorted(spans.items())}

    exports = read_day_exports(costs_dir, skus_by_month)
    days: dict[str, dict[str, Any]] = {}
    for day in sorted(exports):
        entry = exports[day]
        by_model: dict[str, dict[str, Any]] = {}
        for ln in entry["lines"]:
            if ln["model"] is None or ln["amount"] <= 0:
                continue
            cell = by_model.setdefault(ln["model"], {"tiers": {}, "tier_silent": {}})
            cls = sku_class(ln["sku"])
            bucket = (cell["tier_silent"] if ln["tier"] is None
                      else cell["tiers"].setdefault(ln["tier"], {}))
            bucket[cls] = bucket.get(cls, 0) + int(ln["amount"])
        days[day] = {"project_filter": entry["project_filter"],
                     "export_sha256": entry["sha256"],
                     "other_exports_for_day": entry["alternatives"],
                     "models": dict(sorted(by_model.items()))}
    return {
        "_README": (
            "Which service tiers billed which Gemini model on which Pacific-time billing day, "
            f"for project {PROJECT}, reduced from the Google Cloud billing console exports in "
            "docs/costs/ (gitignored; they carry account identifiers) by "
            "scripts/derive_tier_evidence.py billing. 'intervals' is the union of each "
            "monthly Cost-table line's own usage window per model and tier (a superset of the "
            "days the tier actually billed); 'days' is exact per-day evidence from single-day "
            "Reports exports, each classed by project filter (documented / unverified / "
            "contaminated; an unfiltered export can only add tiers, never remove one), "
            "with the tokens billed per tier and token class (input, output, other = cache "
            "storage token-hours), so a pass whose output exceeds a tier's whole day can be "
            "ruled out of that tier. Tier-silent cache SKUs carry no tier signal and are "
            "counted apart. Read by "
            "scripts/lib_pass_cost.py; never edit by hand."),
        "schema": "billing-day-tiers/2",
        "project": PROJECT,
        "timezone": BILLING_TIMEZONE,
        "months_covered": sorted(skus_by_month),
        "intervals": intervals,
        "days": days,
        "monthly_aud_by_model_and_tier": {m: dict(sorted(v.items()))
                                          for m, v in sorted(months.items())},
    }


# ---------------------------------------------------------------------------
# Run logs.
# ---------------------------------------------------------------------------


def _git_tracked(paths: list[Path]) -> set[str]:
    """Repository-relative paths among *paths* that git tracks."""
    if not paths:
        return set()
    rel = [p.relative_to(PROJECT_ROOT).as_posix() for p in paths]
    out = subprocess.run(["git", "ls-files", "-z", "--", *rel], cwd=PROJECT_ROOT,
                         capture_output=True, check=True)
    return {s for s in out.stdout.decode().split("\0") if s}


def parse_log(text: str) -> dict[str, Any]:
    r"""Read one log's tier evidence: the launch tiers, and the verifier stage's own.

    ``verifier_tiers`` are the tiers a log records FOR a verifier stage: a
    ``Service tier:`` line after the log's first verifier command, or the
    ``--service-tier`` switch within a verifier command itself (only its own
    segment of a combined command line, so a proposer's switch on the same
    line is not read as the verifier's). A log that only mentions a verifier
    records none.

    Args:
        text: The log's text.

    Returns:
        ``tiers`` (known tier words on ``Service tier:`` lines), ``unknown``,
        ``tier_lines``, ``explicit_cache_lines`` and ``verifier_tiers``.

    Examples:
        >>> log = "Service tier: flex\nrun_pv.py verify --x y\nService tier: standard\n"
        >>> parse_log(log)["verifier_tiers"]
        ['standard']
        >>> parse_log("Service tier: flex\noutputs/verifier-t-pilot\nService tier: flex\n")[
        ...     "verifier_tiers"]
        []
        >>> combined = "4_detect --service-tier standard && run_pv.py verify --service-tier flex"
        >>> parse_log(combined)["verifier_tiers"]
        ['flex']
        >>> parse_log("python3 scripts/run_pv.py verify --x y --service-tier flex\n")["verifier_tiers"]
        ['flex']
    """
    lines = text.splitlines()
    first_verifier = next((i for i, ln in enumerate(lines) if VERIFIER_CMD.search(ln)), None)
    words: list[str] = []
    verifier: set[str] = set()
    for i, ln in enumerate(lines):
        for m in TIER_LINE.finditer(ln):
            word = m.group(1).lower()
            words.append(word)
            if first_verifier is not None and i > first_verifier and word in KNOWN_TIERS:
                verifier.add(word)
        for cmd in VERIFIER_CMD.finditer(ln):
            segment = COMMAND_END.split(ln[cmd.start():], maxsplit=1)[0]
            verifier.update(w for w in SWITCH.findall(segment) if w in KNOWN_TIERS)
    return {"tiers": sorted({w for w in words if w in KNOWN_TIERS}),
            "unknown": sorted({w for w in words if w not in KNOWN_TIERS}),
            "tier_lines": len(words),
            "explicit_cache_lines": len(CACHE_LINE.findall(text)),
            "verifier_tiers": sorted(verifier)}


def build_log_evidence(outputs_dir: Path) -> dict[str, Any]:
    """Sweep run logs for the runner's ``Service tier:`` launch line.

    Args:
        outputs_dir: The ``outputs/`` tree.

    Returns:
        The document written to ``data/pricing/run-log-tiers.json``: per
        directory (repository-relative), the tiers its own logs name and the
        logs cited.
    """
    logs = sorted(outputs_dir.rglob("*.log"))
    hits: list[tuple[Path, dict[str, Any]]] = []
    for path in logs:
        try:
            parsed = parse_log(path.read_text(errors="ignore"))
        except OSError:
            continue
        if parsed["tier_lines"] or parsed["verifier_tiers"]:
            hits.append((path, parsed))
    tracked = _git_tracked([p for p, _ in hits])
    dirs: dict[str, dict[str, Any]] = {}
    for path, parsed in hits:
        rel_dir = path.parent.relative_to(PROJECT_ROOT).as_posix()
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        entry = dirs.setdefault(rel_dir, {"tiers": [], "verifier_tiers": [],
                                          "explicit_cache": False, "logs": []})
        record = {"path": rel, "sha256": _sha256(path), "tracked": rel in tracked,
                  "tiers": parsed["tiers"], "tier_lines": parsed["tier_lines"],
                  "explicit_cache_lines": parsed["explicit_cache_lines"],
                  "verifier_tiers": parsed["verifier_tiers"]}
        if parsed["unknown"]:
            record["unknown_tier_words"] = parsed["unknown"]
        entry["logs"].append(record)
        entry["tiers"] = sorted(set(entry["tiers"]) | set(parsed["tiers"]))
        # Per log, never OR-ed across logs: a proposer log's launch tier does
        # not become verifier evidence because a neighbouring log mentions a
        # verifier (re-audit, 2026-10-03).
        entry["verifier_tiers"] = sorted(set(entry["verifier_tiers"])
                                         | set(parsed["verifier_tiers"]))
        entry["explicit_cache"] = entry["explicit_cache"] or parsed["explicit_cache_lines"] > 0
    # A directory with no known tier for either stage carries no evidence.
    dirs = {d: e for d, e in dirs.items() if e["tiers"] or e["verifier_tiers"]}
    return {
        "_README": (
            "Service tiers named by run logs, per directory. The detection runner prints "
            "'Service tier: <tier>' at launch from 2026-04-09 (commit 2a2cd81c7); this file "
            "is the sweep of every *.log under outputs/ by scripts/derive_tier_evidence.py "
            "logs, run on sapphire (which holds logs the workstation clone does not). A "
            "directory whose logs name more than one tier is a conflict the reader must not "
            "resolve by walking further up. explicit_cache records that the run created an "
            "explicit context cache (--use-cache): the runner's cached call path omits "
            "service_tier (scripts/4_detect_mounds_batch.py, since 76a2cc719), so a "
            "real-time request on it is billed at standard whatever the launch line says. "
            "verifier_tiers are the tiers a log records FOR a verifier stage: a Service tier "
            "line after the log's first verifier command, or --service-tier on a run_pv.py "
            "verify or cleanup command; only these pin a verifier leg beneath a run-level "
            "log. Tier words other than standard, flex and batch are kept as "
            "unknown_tier_words, never as tiers. Read by scripts/lib_pass_cost.py; never "
            "edit by hand."),
        "schema": "run-log-tiers/4",
        "logs_scanned": len(logs),
        "logs_with_tier_lines": len(hits),
        "directories": dict(sorted(dirs.items())),
    }


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _write(doc: dict[str, Any], out: Path, check: bool) -> int:
    """Write *doc* to *out* (or, with ``check``, report whether it would change)."""
    text = json.dumps(doc, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    current = out.read_text(encoding="utf-8") if out.exists() else None
    if check:
        if current == text:
            print(f"{out.relative_to(PROJECT_ROOT)}: up to date")
            return 0
        print(f"{out.relative_to(PROJECT_ROOT)}: WOULD CHANGE", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out.relative_to(PROJECT_ROOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("source", choices=("billing", "logs"))
    parser.add_argument("--check", action="store_true",
                        help="write nothing; exit 1 if the committed file would change")
    args = parser.parse_args(argv)
    if args.source == "billing":
        doc = build_billing_evidence(COSTS_DIR)
        days = doc["days"]
        print(f"months covered: {', '.join(doc['months_covered'])}")
        print(f"single-day exports: {len(days)} "
              f"({sum(d['project_filter'] == 'documented' for d in days.values())} documented, "
              f"{sum(d['project_filter'] == 'unverified' for d in days.values())} unverified, "
              f"{sum(d['project_filter'] == 'contaminated' for d in days.values())} contaminated)")
        return _write(doc, BILLING_OUT, args.check)
    doc = build_log_evidence(OUTPUTS_DIR)
    print(f"logs scanned: {doc['logs_scanned']}; with a tier line: {doc['logs_with_tier_lines']}")
    return _write(doc, LOGS_OUT, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
