#!/usr/bin/env python3
"""Generate the hypothesis-outcome table from the analyses manifest.

The table is a PURE PROJECTION of ``results/analyses-manifest.json`` — the
D17 ruling (outline decision D17 = A + schema amendment, Session 133;
executed in the S134 reconciliation block): the manifest is the single
source of truth for hypothesis disposition, and no cell of this table is
hand-maintained. Re-run after any manifest regeneration.

Two classes of content appear:

* **Registration constants** (hypothesis titles and registered tiers) are
  immutable facts of the lodged preregistration, carried as script
  constants with per-line anchors into ``osf/preregistration.md``. They
  cannot drift because the lodged text cannot change.
* **Everything else** — disposition, preregistration labels, deviations,
  the family BH-FDR verdict, where each hypothesis is reported — is
  projected from manifest rows at generation time.

Disposition rules (vocabulary v2, ``analyses-manifest.schema.json``):

* A hypothesis is **executed** when a ``confirmatory``/
  ``confirmatory-with-deviation`` or ``registered-exploratory`` row
  references it — those labels assert execution of a registered analysis.
* ``post-hoc`` rows never count as execution of the registered obligation
  (they are listed as related characterisation).
* A ``not-executed`` disposition row marks the obligation unexecuted; if
  executed rows coexist with one (H2's case), the hypothesis is
  **partially executed**.

The family BH-FDR verdict for H1–H8 is parsed mechanically from the
``family-bh-fdr-confirmatory`` row's outcome ("Rejection set {…}"); the
script fails loudly if that row or any hypothesis disappears.

Usage:
    python3 scripts/generate_hypothesis_outcome_table.py [--check]

``--check`` regenerates in memory and exits non-zero if the committed
outputs differ (drift guard); the default writes
``results/hypothesis-outcome-table/hypothesis-outcome-table.{md,json}``.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "results" / "analyses-manifest.json"
OUT_DIR = REPO_ROOT / "results" / "hypothesis-outcome-table"
OUT_MD = OUT_DIR / "hypothesis-outcome-table.md"
OUT_JSON = OUT_DIR / "hypothesis-outcome-table.json"

FAMILY_ROW_ID = "family-bh-fdr-confirmatory"

#: Registration constants — immutable facts of the lodged preregistration
#: (docs/methodology/preregistration/osf/preregistration.md). Line anchors
#: given per entry; tiers per §5 (:398), §6 (:833-1092).
HYPOTHESES: dict[str, tuple[str, str]] = {
    "H1": ("Modality and elaboration level (osf:400)", "confirmatory"),
    "H2": ("Two-stage pipelines do not improve detection (osf:451)", "confirmatory"),
    "H3": ("Consensus voting improves F1 (osf:497)", "confirmatory"),
    "H4": ("Example ordering / canonical placement (osf:534)", "confirmatory"),
    "H5": ("Negative text treatment (osf:578)", "confirmatory"),
    "H6": ("Flash-to-Pro transfer (osf:651)", "confirmatory"),
    "H7": ("Temperature affects detection (osf:705)", "confirmatory"),
    "H8": ("Library composition and scaling (osf:737)", "confirmatory"),
    "H9": ("Diversity mechanisms in consensus voting (osf:841)", "exploratory (Tier A)"),
    "H10": ("Training-pool size effects (osf:904)", "exploratory (Tier B)"),
    "H11": ("Tile size effects (osf:944)", "exploratory (Tier B)"),
    "H12": ("Hard-positive to hard-negative ratio (osf:980)", "exploratory (Tier B)"),
    "H13": ("Overlap/stride effects (osf:1014)", "exploratory (Tier B)"),
    "H14": ("Cross-model consistency (osf:1056)", "exploratory (Tier C, deferred)"),
    "H15": ("Cross-model consensus voting (osf:1074)", "exploratory (Tier C, deferred)"),
}

EXECUTED_LABELS = {"confirmatory", "confirmatory-with-deviation", "registered-exploratory"}
CONFIRMATORY_SET = {f"H{i}" for i in range(1, 9)}


def load_analyses(path: Path = MANIFEST) -> list[dict]:
    """Load analysis rows from the generated manifest."""
    return json.loads(path.read_text())["analyses"]


def parse_rejection_set(analyses: list[dict]) -> tuple[set[str], set[str]]:
    """Derive the family BH-FDR rejection set and exclusion set.

    Returns ``(rejected, excluded)``. ``rejected`` is parsed from the one
    "Rejection set {…}" clause in the family row's outcome (loud failure
    on zero or multiple clauses). ``excluded`` is derived STRUCTURALLY:
    a confirmatory hypothesis absent from the family row's own
    ``hypothesis_refs`` never entered the family — the prose ("H6
    excluded") is used only as a cross-check, so a rewording can never
    silently convert "never run" into "not rejected" (S134 audit
    finding H-1).
    """
    row = next((a for a in analyses if a["analysis_id"] == FAMILY_ROW_ID), None)
    if row is None:
        raise ValueError(f"family row '{FAMILY_ROW_ID}' missing from manifest")
    outcome = row.get("outcome") or ""
    clauses = re.findall(r"[Rr]ejection set \{([^}]*)\}", outcome)
    if len(clauses) != 1:
        raise ValueError(
            f"family outcome must carry exactly one 'Rejection set {{…}}' "
            f"clause; found {len(clauses)}")
    rejected = {h.strip() for h in clauses[0].split(",") if h.strip()}
    if not rejected <= CONFIRMATORY_SET:
        raise ValueError(
            f"rejection set names non-confirmatory hypotheses: "
            f"{sorted(rejected - CONFIRMATORY_SET)}")
    excluded = CONFIRMATORY_SET - set(row.get("hypothesis_refs") or [])
    prose_excluded = set(re.findall(r"(H\d+)\s+(?:was\s+)?excluded", outcome))
    if prose_excluded and prose_excluded != excluded:
        raise ValueError(
            f"family outcome prose declares excluded={sorted(prose_excluded)} "
            f"but hypothesis_refs imply excluded={sorted(excluded)}")
    if rejected & excluded:
        raise ValueError(
            f"hypotheses both rejected and excluded: {sorted(rejected & excluded)}")
    return rejected, excluded


def project(analyses: list[dict]) -> list[dict]:
    """Project the manifest into one record per hypothesis H1–H15."""
    rejected, excluded = parse_rejection_set(analyses)
    records: list[dict] = []
    for hyp, (title, tier) in HYPOTHESES.items():
        refs = [a for a in analyses if hyp in (a.get("hypothesis_refs") or [])]
        executed = [a for a in refs if a.get("preregistered") in EXECUTED_LABELS]
        posthoc = [a for a in refs if a.get("preregistered") == "post-hoc"]
        dispo_rows = [a for a in refs if a.get("preregistered") == "not-executed"]
        unadjudicated = [a for a in refs if a.get("preregistered") is None]

        if unadjudicated:
            raise ValueError(
                f"{hyp}: unadjudicated rows (preregistered null) reference "
                f"it: {sorted(a['analysis_id'] for a in unadjudicated)} — "
                f"adjudicate before generating the table")

        if executed and dispo_rows:
            disposition = "partially executed"
        elif executed:
            disposition = "executed"
        elif dispo_rows:
            disposition = "not executed"
        else:
            raise ValueError(
                f"{hyp}: only post-hoc rows (or none at all) reference it — "
                f"the register carries no registered-execution or "
                f"not-executed disposition row for this obligation")

        if hyp not in CONFIRMATORY_SET:
            family = "— (exploratory: not in family)"
        elif hyp in excluded:
            if disposition == "executed":
                raise ValueError(
                    f"{hyp}: excluded from the family but the register "
                    f"shows it executed — verdict/disposition inconsistency")
            family = "— (excluded: never run)"
        elif hyp in rejected:
            family = "rejected (q=0.05)"
        else:
            family = "not rejected"

        # E-numbers are extracted from WITHIN each deviations entry, so a
        # prose entry like "E49/E51 (carry-forward)" still contributes
        # both disclosures (S134 audit finding H-2). Entries carrying no
        # E-number (e.g. an argued no-deviation note) contribute nothing,
        # by design — the rationale lives on the row itself.
        deviations = sorted(
            {e for a in executed + dispo_rows
             for d in (a.get("deviations") or [])
             for e in re.findall(r"\bE\d+\b", d)},
            key=lambda e: int(e[1:]))

        def _ids(rows: list[dict]) -> list[str]:
            return sorted(f"{a['analysis_id']} [{a['preregistered']}]" for a in rows)

        records.append({
            "hypothesis": hyp,
            "title": title,
            "registered_as": tier,
            "disposition": disposition,
            "family_fdr": family,
            "analyses": _ids(executed + dispo_rows),
            "related_post_hoc": _ids(posthoc),
            "deviations": deviations,
        })
    return records


def _git_head() -> str:
    """Return the short HEAD hash for the generation stamp (or 'unknown')."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True,
            timeout=10).stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return "unknown"


def no_hypothesis_rows(analyses: list[dict]) -> list[str]:
    """Register rows carrying no hypothesis_refs (outside the H frame)."""
    return sorted(a["analysis_id"] for a in analyses
                  if not (a.get("hypothesis_refs") or []))


def render_md(records: list[dict], no_hyp: list[str]) -> str:
    """Render the Markdown view of the table."""
    head = _git_head()
    lines = [
        "# Hypothesis-outcome table",
        "",
        "> **GENERATED FILE — do not hand-edit.** Produced by",
        "> `scripts/generate_hypothesis_outcome_table.py` from",
        f"> `results/analyses-manifest.json` at commit `{head}`; re-run the",
        "> script after any manifest regeneration. Pure projection per the",
        "> D17 ruling (`docs/paper/results-outline.md` § D17): no cell is",
        "> hand-maintained.",
        "",
        "Labels: vocabulary v2 (`docs/manifest-schemas/"
        "analyses-manifest.schema.json`).",
        "`post-hoc` rows never count as execution of a registered",
        "obligation; they are listed as related characterisation. The",
        "family BH-FDR verdict is parsed from the",
        f"`{FAMILY_ROW_ID}` row (rejection = the registered H0 rejected at",
        "q = 0.05; for H2 that falsifies the registered no-improvement",
        "prediction — see the row's outcome for interpretation). The",
        "deviations column is the union over the hypothesis's",
        "registered-analysis rows; a family-level row contributes its full",
        "array, so per-hypothesis attribution lives in the errata entries",
        "themselves.",
        "",
        "| Hyp | Registered hypothesis | Registered as | Disposition | Family BH-FDR | Registered-analysis rows | Deviations |",
        "|-----|----------------------|---------------|-------------|---------------|--------------------------|------------|",
    ]
    for r in records:
        rows = "; ".join(r["analyses"]) or "—"
        devs = ", ".join(r["deviations"]) or "—"
        lines.append(
            f"| {r['hypothesis']} | {r['title']} | {r['registered_as']} | "
            f"{r['disposition']} | {r['family_fdr']} | {rows} | {devs} |")
    lines += ["", "## Related post-hoc characterisation", ""]
    lines.append("| Hyp | Post-hoc rows referencing the hypothesis |")
    lines.append("|-----|------------------------------------------|")
    for r in records:
        ph = "; ".join(r["related_post_hoc"]) or "—"
        lines.append(f"| {r['hypothesis']} | {ph} |")
    lines += ["", "## Register rows outside the hypothesis frame", ""]
    lines.append("Rows with no `hypothesis_refs` (deployment boards and")
    lines.append("methodological re-measurements) — part of the register but")
    lines.append("outside the H1–H15 reconciliation:")
    lines.append("")
    for aid in no_hyp:
        lines.append(f"- `{aid}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="verify committed outputs match a regeneration")
    args = ap.parse_args()

    analyses = load_analyses()
    records = project(analyses)
    md = render_md(records, no_hypothesis_rows(analyses))
    js = json.dumps({"hypotheses": records}, indent=1, ensure_ascii=False) + "\n"

    if args.check:
        stale = []
        if not OUT_JSON.exists() or OUT_JSON.read_text() != js:
            stale.append(str(OUT_JSON))
        # The MD embeds the HEAD hash, so compare it with the hash line
        # neutralised on both sides (regeneration at a new commit must not
        # count as drift when the projection is unchanged).
        def strip(text: str) -> str:
            return re.sub(r"commit `[^`]+`", "commit `X`", text)

        if not OUT_MD.exists() or strip(OUT_MD.read_text()) != strip(md):
            stale.append(str(OUT_MD))
        if stale:
            print("STALE:", ", ".join(stale))
            return 1
        print(f"hypothesis-outcome table up to date ({len(records)} hypotheses)")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md)
    OUT_JSON.write_text(js)
    print(f"wrote {OUT_MD.relative_to(REPO_ROOT)} and "
          f"{OUT_JSON.relative_to(REPO_ROOT)} ({len(records)} hypotheses)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
