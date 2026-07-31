#!/usr/bin/env python3
"""Heuristic consistency sweep: generated markdown vs sibling JSON.

Phase 3 generated-stratum coverage for families that have a resolved
sibling-JSON source but no exact comparer yet (``planning/audit-charter.md``
§ 7; registry ``sources``). For every registry entry whose ``sources``
resolve to JSON artefact(s), extract each numeric token from the
markdown and test whether SOME number in the sibling JSON reproduces it
at quoted precision (``scripts/lib_c4_compare.py``).

This is deliberately a set-membership heuristic, not a cell-exact
check: it cannot prove a file correct, but a markdown quoting numbers
its own source no longer contains is exactly the stale-desync failure
class the sweep exists to catch. Verdicts:

- ``CONSISTENT`` — every checked markdown number is reproducible from
  the sibling JSON's number pool.
- ``SUSPECT`` — one or more numbers have no source counterpart (listed;
  triage decides — renderer-computed values like percentages produce
  benign flags).

Families already covered by exact probes (evaluation.md,
threshold_sweep_summary, manifest companions, 55map leaderboard) are
skipped. Deterministic; run on sapphire.

Usage::

    python3 scripts/sweep_sibling_json_consistency.py \
        [--out reports/verification/c4-regen/sibling-consistency-report.json]
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
DEFAULT_OUT = (REPO_ROOT / "reports" / "verification" / "c4-regen"
               / "sibling-consistency-report.json")

ALREADY_COVERED = {
    "gen-evaluation-md", "gen-threshold-sweep", "gen-manifest-companions",
    "gen-55map-leaderboard",
}
# Numeric tokens worth checking: decimals, or integers of >= 2 digits
# (single digits are overwhelmingly list markers and tier numbers).
NUM_RE = re.compile(r"(?<![\w./-])[-+−]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\w./-])[-+−]?\d+\.\d+|(?<![\w./-])\d{2,}")


def collect_numbers(obj, pool: set[float]) -> None:
    """Recursively collect every number in a JSON structure."""
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        pool.add(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            collect_numbers(v, pool)
    elif isinstance(obj, list):
        for v in obj:
            collect_numbers(v, pool)
    elif isinstance(obj, str):
        # Numbers embedded in strings (dates excluded by the md-side regex
        # anyway) still count as source support.
        for tok in re.findall(r"-?\d+(?:\.\d+)?", obj):
            try:
                pool.add(float(tok))
            except ValueError:
                pass


def strip_noise(text: str) -> str:
    """Remove markdown constructs that are numeric but not claims."""
    text = re.sub(r"`[^`\n]*`", " ", text)          # inline code (paths, ids)
    text = re.sub(r"\]\([^)\n]*\)", "]", text)      # link targets
    text = re.sub(r"\b\d{4}-\d{2}-\d{2}[T ]?[\d:.+Z]*\b", " ", text)  # dates/stamps
    text = re.sub(r"\b[0-9a-f]{7,40}\b", " ", text)  # git hashes
    return text


def sweep_file(md_path: Path, sources: list[str]) -> dict:
    """Check one markdown file against its sibling JSON number pool."""
    pool: set[float] = set()
    for src in sources:
        try:
            collect_numbers(json.loads((REPO_ROOT / src).read_text(encoding="utf-8")), pool)
        except (OSError, json.JSONDecodeError) as exc:
            return {"file": str(md_path.relative_to(REPO_ROOT)), "verdict": "NO-SOURCE",
                    "problems": [f"{src}: {exc}"]}
    # Derived support: percentages of any pooled value, and pairwise
    # deltas are NOT synthesised — only direct and ×100 forms.
    scaled = {v * 100.0 for v in pool if abs(v) <= 1.0}

    text = strip_noise((md_path.read_text(encoding="utf-8", errors="replace")))
    problems: list[str] = []
    checked = 0
    for token in NUM_RE.findall(text):
        parsed = parse_value(token.replace("−", "-"))
        if parsed is None:
            continue
        checked += 1
        supported = any(
            match_at_quoted_precision(parsed, candidate)["match"]
            for candidate in pool | scaled
        )
        if not supported:
            problems.append(token)
    dedup = sorted(set(problems))
    verdict = "CONSISTENT" if not dedup else "SUSPECT"
    return {"file": str(md_path.relative_to(REPO_ROOT)), "verdict": verdict,
            "numbers_checked": checked, "unsupported": dedup[:25]}


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    results = []
    for entry in registry["files"]:
        if entry["stratum"] != "generated" or entry["rule_id"] in ALREADY_COVERED:
            continue
        sources = [s for s in entry.get("sources", []) if s.endswith((".json", ".geojson"))]
        if not sources:
            continue
        results.append(dict(sweep_file(REPO_ROOT / entry["path"], sources),
                            rule_id=entry["rule_id"],
                            hand_edited=entry.get("hand_edited", False)))

    counts: dict[str, int] = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    report = {"_meta": {"generator": "scripts/sweep_sibling_json_consistency.py",
                        "heuristic": "set-membership at quoted precision; SUSPECT feeds triage, not verdicts",
                        "counts": counts},
              "results": results}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("counts:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    for r in [x for x in results if x["verdict"] == "SUSPECT"][:15]:
        print(f"  SUSPECT {r['file']} ({r['rule_id']}): {r['unsupported'][:6]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
