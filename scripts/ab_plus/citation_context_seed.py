"""Generate a deterministic relevance seed from a citekey's usage in the paper.

The AB+ proposer prompt requires a per-citekey relevance seed. Tranches 1-7
used the §2-grounding synthesis, which only covers the §2 sources; the
2026-07 gap run covers citekeys cited across the whole paper, for which no
synthesis entry exists — and pointing the proposer at a seed that lacks its
citekey invites confabulated relevance, the exact failure the pipeline
exists to prevent.

This script builds the seed deterministically instead: for each citekey it
extracts the paragraph(s) of the paper's own prose surrounding every
``\\cite``-family command that references it. Where a source sits for Paper B
is thereby grounded in how the paper actually uses it — no LLM call, fully
re-runnable, and the output header records the git revision of the prose it
was derived from.

Usage (from the repo root)::

    .venv/bin/python scripts/ab_plus/citation_context_seed.py \
        --citekeys flyvbjerg_five_2006,Asch_1956 \
        --out outputs/section2-grounding/gap-seed-2026-07.md

The output is committed alongside the tranche it seeds, so entry provenance
can point at the exact seed text the proposer read.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ab_plus.config import REPO_ROOT

# Any command whose name contains "cite" — the same full-family discipline
# the 2026-07-24 audit forced on the cited-key census (a `\citealp`-shaped
# gap there produced a false "uncited" finding).
_CITE_RE = re.compile(
    r"\\[A-Za-z]*[Cc]ite[A-Za-z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}"
)


def _tex_files() -> list[Path]:
    """The paper's live prose: assembly/**/*.tex, excluding archive/."""
    return sorted(
        p for p in (REPO_ROOT / "assembly").rglob("*.tex")
        if "archive" not in p.parts
    )


def _paragraphs(text: str) -> list[str]:
    """Split TeX source into paragraphs on blank lines."""
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def contexts_for(citekey: str) -> list[tuple[str, str]]:
    """Return ``(location, paragraph)`` for every paragraph citing the key.

    Matching is exact on the citekey within the cite command's key list
    (commands may carry several comma-separated keys).
    """
    hits: list[tuple[str, str]] = []
    for tex in _tex_files():
        text = tex.read_text(encoding="utf-8")
        for para in _paragraphs(text):
            for m in _CITE_RE.finditer(para):
                keys = [k.strip() for k in m.group(1).split(",")]
                if citekey in keys:
                    rel = tex.relative_to(REPO_ROOT)
                    hits.append((str(rel), para))
                    break  # one hit per paragraph is enough
    return hits


def build_seed(citekeys: list[str]) -> str:
    """Render the seed document for the given citekeys."""
    rev = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "describe", "--always", "--dirty"],
        capture_output=True, text=True, timeout=10,
    ).stdout.strip() or "unknown"
    lines = [
        "# Citation-context relevance seed (deterministic)",
        "",
        f"Generated {date.today().isoformat()} from `assembly/**/*.tex` at "
        f"revision `{rev}` by `scripts/ab_plus/citation_context_seed.py`.",
        "Each section reproduces the paper's own paragraphs that cite the",
        "source — the proposer reads relevance from actual usage, not from a",
        "synthesis that may not cover the key.",
        "",
    ]
    for ck in citekeys:
        hits = contexts_for(ck)
        lines.append(f"## {ck}")
        lines.append("")
        if not hits:
            lines.append(
                "NO CITATION CONTEXTS FOUND in assembly/ — do not invent "
                "relevance; flag this entry for author attention."
            )
            lines.append("")
            continue
        for location, para in hits:
            lines.append(f"### Cited in `{location}`")
            lines.append("")
            lines.append("```tex")
            lines.append(para)
            lines.append("```")
            lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ab_plus.citation_context_seed", description=__doc__
    )
    parser.add_argument(
        "--citekeys", required=True,
        help="comma-separated citekeys to build seed sections for",
    )
    parser.add_argument("--out", required=True, help="output markdown path")
    args = parser.parse_args(argv)
    citekeys = [c.strip() for c in args.citekeys.split(",") if c.strip()]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_seed(citekeys), encoding="utf-8")
    empty = [ck for ck in citekeys if f"## {ck}\n\nNO CITATION" in out.read_text(
        encoding="utf-8")]
    print(f"Wrote {out} ({len(citekeys)} citekeys; {len(empty)} without contexts"
          f"{': ' + ', '.join(empty) if empty else ''})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
