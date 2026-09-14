#!/usr/bin/env python3
"""Project one ``post_run_report.md`` per registered run from the manifests.

Batch 1 item 1 of ``planning/documentation-foundation-checklist-2026-09-13.md``:
every run directory the registry names should carry a post-run report, and the
PI asked on 2026-09-13 for the missing ones to be back-filled in bulk (that
request supersedes "back-fill on touch" for this item only).

**These are GENERATED PROJECTIONS, not hand-authored documents.** Under the PI
ruling of 2026-09-11 (``docs/methodology/output-directory-standard.md``
§ "Documents in Revision Policy Scope"), a Markdown file under an in-scope path
that a generator emits from registered inputs is OUT of the
banner-and-changelog requirement and IN a stricter one: a ``GENERATED FILE``
banner naming the generator, the source commit of the inputs it was projected
from, and a ``--check`` drift guard run by a tier-1 test. "Is this current?" is
answered by the drift test, not by a changelog. The before/after notes for a
regeneration go in the commit message.

Anti-confabulation contract
---------------------------
Every figure in a report is read from a committed file named in that report's
own § 10 provenance block. Where a figure is not on file the report writes
**not supplied** and says why — it never estimates, and it never infers a model
or a cost from a directory name. Two consequences worth stating up front:

* **Cost.** ``cost_usd`` in the passes manifest is each pass meta's OWN
  ``cost_estimate.total_cost_usd`` (``generate_post_run_report.py:568,672``), and
  the token-load audit of 2026-06-12 established that those self-reported
  figures price at STANDARD rates although every audited run executed at
  ``--service-tier flex`` (half price) and omit thinking tokens although Gemini
  bills thinking at the output rate (``reports/token-load-audit-2026-06-12.md``
  § 1). The reports therefore label the sum "as recorded in pass metadata", carry
  that caveat verbatim, and cite the audits that mention the run. They do NOT
  present the sum as the run's cost.
* **Audit citations.** A run is listed against an audit report when the run_id or
  its directory path appears in that report's text. That is a pointer to where
  the audited figures live, not a claim that the report audits the run in full —
  the wording says so.

The two hand-authored narrative reports (``55maps-image-generalisation``,
``55maps-text-min-generalisation``) are SKIPPED, not overwritten: they carry
Dawid-Skene corrections, paired comparisons, per-map extrema and recovery
narratives that no projection of the manifests can re-derive, and they are in
full Revision-Policy scope with their own changelogs. See :data:`HAND_AUTHORED`.

Usage::

    python3 scripts/generate_run_reports.py --run h13          # print to stdout
    python3 scripts/generate_run_reports.py --all              # summary only
    python3 scripts/generate_run_reports.py --all --write      # write the reports
    python3 scripts/generate_run_reports.py --check            # drift guard (exit 1)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[1]

#: Semantic version of this generator, written into every report. Bump on any
#: change to the rendered content.
#:
#: 1.1.0 (2026-09-13): § 4 gained the per-run token-load audit block
#: (:data:`TOKEN_AUDIT`). Added because 1.0.0 printed the manifest's token totals as
#: plain fact, and the audit had already established that the ``usage_stats`` block
#: those totals come from is 2× or 3× double-counted on three of the 55-map runs — a
#: figure wrong in a known direction is exactly what this generator's
#: anti-confabulation contract forbids.
GENERATOR_VERSION: str = "1.1.0"

#: The committed inputs every report is projected from. Listed in each report's
#: § 10 so a reader can re-derive it, and named here so the set is one thing.
INPUT_FILES: tuple[str, ...] = (
    "results/run-registry.json",
    "results/runs-manifest.json",
    "results/conditions-manifest.json",
    "results/passes-manifest.json",
    "results/analyses-manifest.json",
    "results/run-conditions.json",
    "results/run-analyses.json",
    "docs/methodology/preregistration/protocol-errata.md",
)

#: Cost/spend audits a report cites when it names the run. Each is cited as a
#: POINTER to audited figures, never as a per-run total.
AUDIT_REPORTS: tuple[str, ...] = (
    "reports/token-load-audit-2026-06-12.md",
    "reports/r7-gaps-deltas-2026-09-11.md",
    "reports/k-ladder-phase2-deltas-2026-09-12.md",
    "reports/billing-reconciliation-2026-09-11.md",
)

#: Per-run verdicts from ``reports/token-load-audit-2026-06-12.md``, transcribed
#: verbatim with the section each figure comes from.
#:
#: This table is load-bearing for honesty, not decoration. The passes manifest
#: takes a pass's ``tokens`` from the meta's ``usage_stats`` block
#: (``generate_post_run_report.py:567,671`` → ``_tokens_from_usage``), and the audit
#: established by per-item recomputation that ``usage_stats`` is DOUBLE-COUNTED on
#: three of these runs — a 2026-05-02/03 recovery merge summed the original run's
#: usage into the post-recovery cumulative total, and on the image run the manifest
#: generator then added the pre-recovery backups on top again. So for those runs the
#: token figures § 4 reports from the manifest are themselves inflated by the stated
#: factor, and a report that printed them without saying so would publish numbers
#: wrong by 2× or 3× in a known direction.
#:
#: Fields: ``(audit section, manifest-vs-clean, live-metas-vs-clean,
#: trustworthy source, clean per-pass figures)``. Deliberately NO derived run
#: total: the audit's pass count and the manifest's pass count need not agree (the
#: text-high run has 6 pass rows against the audit's 5), so multiplying here would
#: manufacture a figure no file carries.
TOKEN_AUDIT: dict[str, tuple[str, str, str, str, str]] = {
    "55maps-text-min-generalisation": (
        "§ 3.1", "2.0× inflated", "clean (factor 1.000 on all axes)",
        "live `*.meta.json`",
        "5 passes; clean flex cost US$4.67/pass (mean US$4.6723); per pass input "
        "12,828,582 (exactly 1,502/tile), output mean 976,791 (range "
        "972,669–980,412), thinking 0"),
    "55maps-text-high-generalisation": (
        "§ 3.2", "2.0× inflated", "2.0× inflated (factors 2.003–2.016 across axes)",
        "`per_item_metadata`",
        "5 passes; clean flex cost US$40.19/pass (range US$39.92–40.45), of which "
        "thinking is ~US$34.51; clean per pass input 12,828,582, output mean "
        "1,647,744, thinking mean 23,005,025 (2,693/tile)"),
    "55maps-text-high-t0-3-generalisation": (
        "§ 3.3", "clean (1.0×)", "clean (factors 1.0001–1.0012; no recovery merge)",
        "either",
        "5 passes; clean flex cost US$50.82/pass (range US$49.94–51.64); per pass "
        "input 12,828,582, output mean 1,461,601, thinking mean 30,283,306 "
        "(3,546/tile — T=0.3 thinks ~32 % more than T=0.7)"),
    "55maps-image-generalisation": (
        "§ 3.4", "3.0× inflated", "2.0× inflated (same recovery-merge mechanism)",
        "`per_item_metadata`",
        "5 passes; clean flex cost US$39.07/pass (range US$38.78–39.27); clean per "
        "pass input 133,743,514 of which cached 124,211,741 (the explicit PV-library "
        "context cache, 14,549 tokens, TTL 1 h), non-cached input 9,531,773, output "
        "mean 1,283,956, thinking mean 19,033,673 (2,228/tile); cache storage "
        "excluded as negligible (< US$0.15 across the run)"),
    "55maps-text-min-n10-uplift": (
        "§ 3.5", "not assessed", "clean (factors ≤ 1.0001)", "either",
        "proposer runs 6–10: clean flex cost US$4.65/pass (mean US$4.6531); per pass "
        "input 12,828,582 (1,502/tile), output mean 963,967, thinking 0. Verifier "
        "(`verified-3of10/run.meta.json`): 16,482 calls, input 29,535,744 (exactly "
        "1,792/call), output 2,588,179, flex US$11.27 (US$0.000684/call)"),
}

#: Runs whose ``post_run_report.md`` is HAND-AUTHORED and must not be replaced by
#: a projection. Mapped to the reason, which the summary prints.
HAND_AUTHORED: dict[str, str] = {
    "55maps-image-generalisation":
        "hand-authored narrative report (394/280-line class) carrying Dawid-Skene "
        "annotator-incompleteness correction, per-map cost extrema, timeline and "
        "recovery narrative — none of it re-derivable from the manifests. In full "
        "Revision-Policy scope with its own changelog; a projection would destroy it.",
    "55maps-text-min-generalisation":
        "hand-authored narrative report carrying the paired HIGH-vs-MIN comparison "
        "(the run's scientific question), Dawid-Skene correction, launcher-provenance "
        "caveat and limitations — not re-derivable from the manifests. In full "
        "Revision-Policy scope with its own changelog.",
    "gemini37-image-55map-2026-09-13":
        "hand-authored launch-state and campaign record carrying the two post-pass "
        "gates and why they are post-pass, the per-pass audited costs, the flex 503 "
        "storm and its 13-candidate gap, the dual-meta accounting a cleanup leaves "
        "behind, the verifier-leg audit method, the six mechanism gates and a resume "
        "path — none of it re-derivable from the manifests. In full Revision-Policy "
        "scope with its own changelog; a projection would destroy it.",
}

#: The buffers the reports surface from a condition's 14-buffer metric block.
#: 20 m is the preregistered localisation buffer; 50 m is the deployment working
#: buffer (``results/run-analyses.json``, the ``55map-leaderboard-50m`` ``_note``:
#: "the canonical 50 m working buffer (Obs 360 derivation)").
HEADLINE_BUFFERS: tuple[str, ...] = ("20", "50")

#: Filenames inside a run directory the report inventories, with a label each.
IN_DIR_DOCS: dict[str, str] = {
    "experiment_intent.md": "per-pass/per-run intent",
    "evaluation.md": "evaluation summary",
    "pre_launch_audit.md": "audit-config output",
    "post_run_report_retrospective.md": "retrospective post-run report",
}

NOT_SUPPLIED = "not supplied"


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #


def _load(rel: str) -> dict:
    """Read one committed JSON input."""
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def _git_head() -> str:
    """Short HEAD hash for the source-commit stamp, or ``unknown``."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True, timeout=10).stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return "unknown"


class Corpus:
    """Every committed input, indexed by run.

    Loading once and indexing is what keeps the whole-corpus build cheap: the
    conditions manifest alone is ~146k lines, and re-scanning it per run would
    turn a seconds-long build into a minutes-long one.
    """

    def __init__(self) -> None:
        self.registry = {e["run_id"]: e for e in _load(INPUT_FILES[0])["registry"]}
        self.runs = {r["run_id"]: r for r in _load(INPUT_FILES[1])["runs"]}
        self.conditions: dict[str, list[dict]] = {}
        for c in _load(INPUT_FILES[2])["conditions"]:
            self.conditions.setdefault(c["run_id"], []).append(c)
        self.passes: dict[str, list[dict]] = {}
        for p in _load(INPUT_FILES[3])["passes"]:
            self.passes.setdefault(p["run_id"], []).append(p)
        self.analyses = _load(INPUT_FILES[4])["analyses"]
        self.decomposition = _load(INPUT_FILES[5])["decomposition"]
        self.run_analyses = {a["analysis_id"]: a
                             for a in _load(INPUT_FILES[6])["analyses"]}
        self.errata = _parse_errata()
        self.audit_text = {rel: (REPO_ROOT / rel).read_text(encoding="utf-8")
                           for rel in AUDIT_REPORTS}

    def analyses_for(self, run_id: str) -> list[dict]:
        """Analyses whose ``conditions_compared`` include a condition of this run."""
        prefix = f"{run_id}::"
        return [a for a in self.analyses
                if any(cid.startswith(prefix)
                       for cid in (a.get("conditions_compared") or []))]


def _parse_errata() -> list[tuple[str, str, str]]:
    """Split the errata register into ``(id, title, body)`` triples.

    Blocks are ``### E<n>: <title>`` and run to the next ``###``/``##`` heading.
    Returned in register order so a report's errata list is stable.
    """
    text = (REPO_ROOT / INPUT_FILES[7]).read_text(encoding="utf-8")
    blocks: list[tuple[str, str, str]] = []
    heads = list(re.finditer(r"^### (E\d+): (.*)$", text, flags=re.MULTILINE))
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        blocks.append((m.group(1), m.group(2).strip(), text[m.end():end]))
    return blocks


# --------------------------------------------------------------------------- #
# Small formatting helpers
# --------------------------------------------------------------------------- #


def _cell(value: object) -> str:
    """Render one table cell, never inventing a value for a missing one."""
    if value is None or value == "":
        return NOT_SUPPLIED
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ", ".join(f"`{v}`" for v in value) if value else "—"
    return str(value)


def _f4(value: object) -> str:
    """Four-decimal float, or the not-supplied marker."""
    return f"{value:.4f}" if isinstance(value, (int, float)) else NOT_SUPPLIED


#: Rendered where a tile-level metric was refused rather than merely
#: absent. ``NOT_SUPPLIED`` says "this evaluation does not carry the
#: metric", which is true of a withheld cell but far too weak: the metric
#: was refused, by a named invariant, on a stated frame, and the reader
#: needs to know that the condition's whole-frame F1 beside it is
#: nonetheless sound. The word points at the condition row's
#: ``tile_withheld_reason``.
WITHHELD = "withheld"


def _mcc_cell(tile: dict) -> str:
    """Render the tile-MCC column, distinguishing withheld from absent.

    Args:
        tile: A condition row's ``metrics.tile_classification`` block.

    Returns:
        The four-decimal MCC; ``"withheld"`` when the block records a
        tile-join refusal (PI ruling 2026-09-13, Session 153 ruling 6);
        otherwise :data:`NOT_SUPPLIED`.

    Examples:
        >>> _mcc_cell({"mcc": 0.8139})
        '0.8139'
        >>> _mcc_cell({"mcc": None})
        'not supplied'
        >>> _mcc_cell({"mcc": None, "tile_withheld_reason": "x"})
        'withheld'
    """
    if tile.get("mcc") is None and tile.get("tile_withheld_reason"):
        return WITHHELD
    return _f4(tile.get("mcc"))


def _pipe(text: str) -> str:
    """Escape pipes so a value cannot break a Markdown table row."""
    return str(text).replace("|", "\\|")


def _prose(text: object) -> str:
    """Neutralise Markdown-significant characters in VERBATIM reproduced prose.

    The registers' prose is full of literal underscores, asterisks and angle
    brackets that are identifiers and placeholders, never markup —
    ``_ignored_evals``, ``run_generalisation.py``, ``detect_brief-text``,
    ``'-recovery-<date>'``. Reproduced raw they trip markdownlint (MD033 inline
    HTML, MD037 spaces in emphasis, MD049 emphasis style) and, worse, a renderer
    may swallow them: ``<date>`` disappears as an unknown tag, and a pair of
    underscores italicises the text between them.

    Backslash escapes and the ``&lt;`` entity both render as the literal
    character, so the rendered report says exactly what the register says. Applied
    only to prose — paths and identifiers the report wraps in backticks are inline
    code, which these rules already exempt, and escaping inside backticks would
    show the backslashes.
    """
    if text is None or text == "":
        return NOT_SUPPLIED
    out = str(text).replace("<", "&lt;").replace(">", "&gt;")
    return out.replace("_", "\\_").replace("*", "\\*")


def _kv_table(rows: list[tuple[str, str]]) -> list[str]:
    """A two-column field/value table."""
    out = ["| Field | Value |", "|---|---|"]
    out += [f"| {k} | {_pipe(v)} |" for k, v in rows]
    return out


#: How many eval paths a single waiver reason names inline before the report
#: defers to ``results/run-conditions.json`` for the rest. pv-diag-384 waives 663
#: evaluations under a handful of reasons; reproducing every path inline made its
#: report 409 KB, four fifths of it duplicated text.
_WAIVER_PATH_CAP: int = 12


def _group_by_text(conditions: list[dict], extract) -> list[tuple[str, list[str]]]:
    """Group conditions by an identical extracted string.

    A qualification written once for a family of sibling cells (h13's three
    native-tiling arms share one caveat verbatim; pv-diag-384 has 138 caveats over
    far fewer distinct texts) should be reproduced once with every cell it covers
    named. Returns ``[(text, [labels])]`` ordered by descending group size then
    text, so the ordering is deterministic and the drift guard is stable.

    Args:
        conditions: the run's condition rows.
        extract: maps a row to its text, or to ``None``/empty to skip it.
    """
    groups: dict[str, list[str]] = {}
    for c in conditions:
        text = extract(c)
        if text:
            groups.setdefault(str(text), []).append(c["label"])
    return sorted(((t, sorted(labels)) for t, labels in groups.items()),
                  key=lambda kv: (-len(kv[1]), kv[0]))


def _labels(labels: list[str]) -> str:
    """Render a group's condition labels as inline code, all of them."""
    return ", ".join(f"`{_pipe(lab)}`" for lab in labels)


# --------------------------------------------------------------------------- #
# Section renderers
# --------------------------------------------------------------------------- #


def _section_identity(run_id: str, corpus: Corpus) -> list[str]:
    """§ 1 — what the run is, as the registry and runs manifest record it."""
    entry = corpus.registry[run_id]
    row = corpus.runs.get(run_id, {})
    return ["## 1. Identity and registration", ""] + _kv_table([
        ("Run id", f"`{run_id}`"),
        ("Directory", f"`{entry['directory_path']}`"),
        ("Registry status", _cell(entry.get("status"))),
        ("Purpose", _prose(row.get("purpose"))),
        ("Run type (derived)", _cell(row.get("run_type"))),
        ("Primary hypothesis", _cell(row.get("primary_hypothesis"))),
        ("Also informs", _cell(row.get("also_informs"))),
        ("Headline condition", _cell(row.get("headline_condition_id"))),
        ("Headline rationale", _prose(row.get("headline_rationale"))),
        ("Historical aliases", _cell(row.get("historical_aliases"))),
        ("Working-notes Obs", _cell(row.get("working_notes_obs"))),
        ("Registry notes", _prose(entry.get("notes"))),
    ]) + [""]


def _section_scope(run_id: str, corpus: Corpus) -> list[str]:
    """§ 2 — corpus, tiling and the evaluation frame."""
    row = corpus.runs.get(run_id, {})
    scope = row.get("scope") or {}
    return ["## 2. Scope and evaluation frame", ""] + _kv_table([
        ("Tile size (px)", _cell(row.get("tile_size_px"))),
        ("Corpus", _cell(row.get("corpus"))),
        ("Ground-truth reference", _cell(row.get("gt_reference"))),
        ("Test set id", _cell(scope.get("test_set_id"))),
        ("Test tiles", _cell(scope.get("n_test_tiles"))),
        ("Bounds", f"`{scope['bounds_path']}`" if scope.get("bounds_path")
         else NOT_SUPPLIED),
        ("Calibration set id", _cell(scope.get("calibration_set_id"))),
        ("Calibration tiles", _cell(scope.get("n_calibration_tiles"))),
    ]) + [""]


def _pass_kind(p: dict) -> str:
    """``verifier`` or ``proposer``, decided on the manifest's own marker.

    A verifier row is the one whose ``n_tiles_processed`` is null WITH a stated
    reason (E72/GAP-8): its meta records candidate crops, not tiles. Deciding on
    that field rather than on a directory name is the point — a pool name is not
    evidence of what a pass did.
    """
    return "verifier" if p.get("n_tiles_null_reason") else "proposer"


def _section_execution(run_id: str, corpus: Corpus) -> list[str]:
    """§ 3 — the passes actually on file: model, tier, thinking, temperature."""
    passes = corpus.passes.get(run_id, [])
    out = ["## 3. Execution — passes on file", ""]
    if not passes:
        out += [
            "No pass rows in `results/passes-manifest.json` for this run. A run is "
            "decomposed into passes only where its proposer/verifier metas were "
            "materialised as resolvable pass files; where they were not, the "
            "decomposition records pools and conditions without passes. See § 5 for "
            "the registered conditions and § 1 for the registry note.", ""]
        return out

    for kind in ("proposer", "verifier"):
        rows = [p for p in passes if _pass_kind(p) == kind]
        if not rows:
            continue
        out += [f"### 3.{1 if kind == 'proposer' else 2} {kind.capitalize()} passes "
                f"({len(rows)})", ""]
        if kind == "proposer":
            out += [
                "| Pool | Pass | Model used | Model requested | Modality | Thinking "
                "| Temp | Status | Tiles done | Dispatched | Retries |",
                "|---|---:|---|---|---|---|---:|---|---:|---:|---:|"]
            for p in sorted(rows, key=lambda r: (r["proposer_pool"], r["pass_n"])):
                out.append(
                    f"| `{_pipe(p['proposer_pool'])}` | {p['pass_n']} "
                    f"| {_cell(p.get('model_used'))} "
                    f"| {_cell(p.get('model_requested'))} "
                    f"| {_cell(p.get('modality'))} | {_cell(p.get('thinking_level'))} "
                    f"| {_cell(p.get('temperature'))} | {_cell(p.get('status'))} "
                    f"| {_cell(p.get('n_tiles_processed'))} "
                    f"| {_cell(p.get('n_tiles_dispatched'))} "
                    f"| {_cell(p.get('retries'))} |")
        else:
            out += [
                "| Pool | Pass | Model used | Modality | Thinking | Temp | Status "
                "| Candidates verified | Retries |",
                "|---|---:|---|---|---|---:|---|---:|---:|"]
            for p in sorted(rows, key=lambda r: (r["proposer_pool"], r["pass_n"])):
                out.append(
                    f"| `{_pipe(p['proposer_pool'])}` | {p['pass_n']} "
                    f"| {_cell(p.get('model_used'))} | {_cell(p.get('modality'))} "
                    f"| {_cell(p.get('thinking_level'))} "
                    f"| {_cell(p.get('temperature'))} | {_cell(p.get('status'))} "
                    f"| {_cell(p.get('n_candidates_verified'))} "
                    f"| {_cell(p.get('retries'))} |")
            reasons = {p["n_tiles_null_reason"] for p in rows
                       if p.get("n_tiles_null_reason")}
            out += ["", "Verifier rows report no tile count by design: " +
                    " ".join(_prose(r) for r in sorted(reasons)), ""]
        out.append("")

    mismatched = [p for p in passes
                  if p.get("model_requested") and p.get("model_used")
                  and p["model_requested"] != p["model_used"]]
    if mismatched:
        out += [
            f"**Model dispatch mismatch on {len(mismatched)} pass(es)**: the model "
            f"the meta records as USED differs from the one requested. The manifest "
            f"reads `model_used` from `per_item_metadata.model_used` and never infers "
            f"it from a directory name, which is why the divergence is visible here "
            f"at all (erratum-backed gotcha: a `pro-`named condition ran Flash).", ""]
        out += ["| Pool | Pass | Requested | Used |", "|---|---:|---|---|"]
        out += [f"| `{_pipe(p['proposer_pool'])}` | {p['pass_n']} "
                f"| {p['model_requested']} | {p['model_used']} |"
                for p in sorted(mismatched, key=lambda r: (r["proposer_pool"],
                                                           r["pass_n"]))]
        out.append("")
    return out


def _section_cost(run_id: str, corpus: Corpus) -> list[str]:
    """§ 4 — the recorded token load and cost, with the audit caveat."""
    passes = corpus.passes.get(run_id, [])
    out = ["## 4. Token load and recorded cost", ""]
    if not passes:
        out += [f"No pass rows, so no recorded token load. {NOT_SUPPLIED}: this run's "
                f"spend is not reconstructable from the passes manifest.", ""]
    else:
        axes = ("input_billed", "input_cached", "output", "thinking", "total")
        totals = {a: 0 for a in axes}
        missing_tokens = 0
        for p in passes:
            tok = p.get("tokens") or {}
            if not tok:
                missing_tokens += 1
                continue
            for a in axes:
                if isinstance(tok.get(a), (int, float)):
                    totals[a] += tok[a]
        costs = [p["cost_usd"] for p in passes
                 if isinstance(p.get("cost_usd"), (int, float))]
        walls = [p["wall_clock_s"] for p in passes
                 if isinstance(p.get("wall_clock_s"), (int, float))]
        out += _kv_table([
            ("Passes on file", str(len(passes))),
            ("Input tokens (billed)", f"{totals['input_billed']:,}"),
            ("Input tokens (cached)", f"{totals['input_cached']:,}"),
            ("Output tokens", f"{totals['output']:,}"),
            ("Thinking tokens", f"{totals['thinking']:,}"),
            ("Total tokens", f"{totals['total']:,}"),
            ("Passes with no token record", str(missing_tokens)),
            ("Sum of recorded `cost_usd`",
             f"US${sum(costs):,.4f} over {len(costs)} of {len(passes)} pass(es)"
             if costs else NOT_SUPPLIED),
            ("Passes with no `cost_usd`", str(len(passes) - len(costs))),
            ("Summed wall clock",
             f"{sum(walls) / 3600:,.2f} h over {len(walls)} pass(es)"
             if walls else NOT_SUPPLIED),
        ])
        audit = TOKEN_AUDIT.get(run_id)
        if audit:
            section, manifest_v, metas_v, source, clean = audit
            out += [
                "",
                f"> **Audited: the token figures above are inflated by a measured "
                f"factor.** `reports/token-load-audit-2026-06-12.md` {section} "
                f"recomputed this run's load from `per_item_metadata` and found its "
                f"`usage_stats` block — which is exactly where the manifest takes a "
                f"pass's `tokens` from (`_tokens_from_usage`) — **{metas_v}**; its "
                f"`cost_manifest.json` is **{manifest_v}**. The trustworthy source is "
                f"{source}. Audited clean figures, quoted from {section}: {clean}. No "
                f"run total is derived here: the audit's pass count and this "
                f"manifest's need not agree, so multiplying would manufacture a "
                f"figure no file carries.",
            ]
        # A bare blank line between two blockquotes splits them and trips MD028; a
        # ">" line keeps the audit verdict and the pricing caveat as two paragraphs
        # of ONE quote, which is also how they should read.
        out += [
            ">" if audit else "",
            "> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is "
            "the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by "
            "`scripts/generate_post_run_report.py`. The token-load audit of "
            "2026-06-12 established that those self-reported estimates price at "
            "STANDARD rates although the audited runs executed at "
            "`--service-tier flex` (half price) and omit thinking tokens although "
            "Gemini bills thinking at the output rate "
            "(`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is "
            "reproduced here as the recorded figure and as an input to a "
            "reconciliation, not as a total to cite.", ""]

    cited = [rel for rel, text in corpus.audit_text.items()
             if run_id in text or corpus.registry[run_id]["directory_path"] in text]
    if cited:
        out += ["Audit and reconciliation reports whose text names this run or its "
                "directory — consult these for audited figures; a mention is a "
                "pointer, not a claim that the report audits this run in full:", ""]
        out += [f"- `{rel}`" for rel in cited]
    else:
        out += ["No cost audit on file names this run or its directory: an "
                f"independently audited cost for this run is **{NOT_SUPPLIED}**. The "
                "four audits checked are "
                + ", ".join(f"`{r}`" for r in AUDIT_REPORTS) + "."]
    out.append("")
    return out


def _condition_metric_row(c: dict) -> str:
    """One row of the § 5 conditions table."""
    metrics = c.get("metrics") or {}
    per_buffer = metrics.get("per_buffer") or {}
    cells = []
    for b in HEADLINE_BUFFERS:
        block = per_buffer.get(b) or {}
        f1 = _f4(block.get("f1"))
        ci = block.get("ci") or {}
        if isinstance(ci.get("low"), (int, float)) and isinstance(ci.get("high"),
                                                                 (int, float)):
            f1 = f"{f1} [{ci['low']:.4f}, {ci['high']:.4f}]"
        cells.append(f1)
    tile = metrics.get("tile_classification") or {}
    vt = c.get("vote_threshold")
    pt = c.get("prob_threshold")
    op = "/".join(x for x in (f"k={vt}" if vt is not None else "",
                              f"pt={pt}" if pt is not None else "") if x) or "—"
    return (f"| `{_pipe(c['label'])}` | {_cell(c.get('architecture'))} "
            f"| {_cell(c.get('aggregation'))} | {_cell(c.get('n_passes'))} | {op} "
            f"| {_cell(c.get('n_detections'))} | {cells[0]} | {cells[1]} "
            f"| {_mcc_cell(tile)} |")


def _section_conditions(run_id: str, corpus: Corpus) -> list[str]:
    """§ 5 — the registered conditions and their headline metrics."""
    conds = corpus.conditions.get(run_id, [])
    out = [f"## 5. Registered conditions ({len(conds)})", ""]
    if not conds:
        out += ["This run registers no conditions in `results/conditions-manifest.json`.",
                ""]
        return out
    out += [
        "F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment "
        "working buffer. Confidence intervals are those the evaluation recorded "
        "(method, iterations and seed per condition in the manifest). `mcc` is "
        "tile-level. A cell reading "
        f"*{NOT_SUPPLIED}* means the metric is absent from the condition's "
        "evaluation, not that it is zero; a tile-MCC reading "
        f"*{WITHHELD}* means the tile-join invariant REFUSED that "
        "condition's per-tile table on this frame, so the tile metrics and "
        "the bootstrap intervals were not computed — the condition's "
        "whole-frame F1 is unaffected and is reported in full (PI ruling "
        "2026-09-13; the named reason is in the condition's manifest row).",
        "",
        "| Condition | Architecture | Aggregation | Passes | Operating point "
        "| Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |",
        "|---|---|---|---:|---|---:|---|---|---:|"]
    out += [_condition_metric_row(c) for c in sorted(conds, key=lambda r: r["label"])]
    out.append("")

    # Which buffers were actually scored. Without this a reader meeting
    # "not supplied" in the F1@50 m column cannot tell a missing metric from a
    # missing buffer, and h13 is the live case: every one of its conditions was
    # scored at 20 m alone.
    buffer_sets: dict[tuple[str, ...], int] = {}
    for c in conds:
        keys = tuple(sorted(((c.get("metrics") or {}).get("per_buffer") or {}),
                            key=float))
        buffer_sets[keys] = buffer_sets.get(keys, 0) + 1
    out += ["Buffers on file (metres), by how many conditions carry that set:", ""]
    for keys, n in sorted(buffer_sets.items(), key=lambda kv: (-kv[1], kv[0])):
        listed = ", ".join(keys) if keys else "none"
        out.append(f"- {n} condition(s): {listed}")
    n_mcc = sum(1 for c in conds
                if ((c.get("metrics") or {}).get("tile_classification") or {})
                .get("mcc") is not None)
    # A condition missing a tile-MCC because the invariant refused its join is
    # a different fact from one whose evaluation simply never computed the
    # metric, so the count of refusals is stated rather than folded into the
    # shortfall.
    withheld_reasons = sorted({
        reason for c in conds
        if (reason := (
            (c.get("metrics") or {}).get("tile_classification") or {}
        ).get("tile_withheld_reason"))
    })
    n_withheld = sum(1 for c in conds
                     if ((c.get("metrics") or {}).get("tile_classification")
                         or {}).get("tile_withheld_reason"))
    mcc_line = f"Tile-level MCC is on file for {n_mcc} of {len(conds)} condition(s)."
    if n_withheld:
        mcc_line += (
            f" Of the {len(conds) - n_mcc} without one, {n_withheld} "
            f"{'is' if n_withheld == 1 else 'are'} WITHHELD by the "
            f"tile-join invariant ({', '.join(withheld_reasons)}); "
            f"{'its' if n_withheld == 1 else 'their'} whole-frame F1 is "
            "unaffected."
        )
    out += ["", mcc_line, ""]

    caveats = _group_by_text(conds, lambda c: c.get("caveat"))
    if caveats:
        n_cond = sum(len(labels) for _, labels in caveats)
        out += [f"### 5.1 Condition caveats ({n_cond} condition(s), "
                f"{len(caveats)} distinct caveat(s))", "",
                "Grouped by identical text: a caveat written once for a family of "
                "sibling cells is reproduced once, with every cell it applies to "
                "named. Nothing is elided.", ""]
        for text, labels in caveats:
            out += [f"- {_labels(labels)}", f"  {_prose(text)}"]
        out.append("")

    overrides = _group_by_text(
        conds, lambda c: ", ".join(f"{k} = {v}" for k, v in
                                   sorted((c.get("scope_override") or {}).items()))
        or None)
    if overrides:
        n_cond = sum(len(labels) for _, labels in overrides)
        out += [f"### 5.2 Scope overrides ({n_cond} condition(s), "
                f"{len(overrides)} distinct frame(s))", "",
                "These conditions are scored on a frame other than the run's nominal "
                "scope in § 2 — the 327-vs-487 leakage trap the verifier exists to "
                "catch, disclosed per condition:", ""]
        for text, labels in overrides:
            out += [f"- {_labels(labels)}", f"  {_prose(text)}"]
        out.append("")

    decomp = corpus.decomposition.get(run_id, {})
    note = decomp.get("_note")
    if note:
        out += ["### 5.3 Decomposition note", "",
                "Verbatim from `results/run-conditions.json` — the hand-authored "
                "record of how this run was decomposed and what was adjudicated:", "",
                f"> {_prose(note)}", ""]
    ignored = decomp.get("_ignored_evals") or []
    if ignored:
        by_reason: dict[str, list[str]] = {}
        for item in ignored:
            if isinstance(item, dict):
                reason = item.get("reason") or (
                    f"{NOT_SUPPLIED} — waived without a recorded reason")
                path = item["eval_path"]
            else:
                reason = (f"{NOT_SUPPLIED} — a bare-string entry, written before the "
                          f"waiver register carried reasons")
                path = item
            by_reason.setdefault(reason, []).append(path)
        out += [f"### 5.4 Waived evaluations ({len(ignored)}, "
                f"{len(by_reason)} distinct reason(s))", "",
                "Scored evaluations under this run that no condition claims, each "
                "waived in `results/run-conditions.json` rather than left silent. "
                "Grouped by identical reason; where a reason covers more than "
                f"{_WAIVER_PATH_CAP} paths the first {_WAIVER_PATH_CAP} are named and "
                "the decomposition carries the rest.", ""]
        for reason, paths in sorted(by_reason.items(), key=lambda kv: -len(kv[1])):
            shown = sorted(paths)[:_WAIVER_PATH_CAP]
            out += [f"- **{len(paths)} evaluation(s)** — {_prose(reason)}"]
            out += [f"  - `{p}`" for p in shown]
            if len(paths) > _WAIVER_PATH_CAP:
                out.append(f"  - … and {len(paths) - _WAIVER_PATH_CAP} more under the "
                           f"same waiver (full list in "
                           f"`results/run-conditions.json`, this run's "
                           f"`_ignored_evals`)")
        out.append("")
    return out


def _section_analyses(run_id: str, corpus: Corpus) -> list[str]:
    """§ 6 — which registered analyses read this run."""
    rows = corpus.analyses_for(run_id)
    out = [f"## 6. Analyses that read this run ({len(rows)})", ""]
    if not rows:
        out += ["No registered analysis in `results/analyses-manifest.json` compares a "
                "condition of this run. That is a statement about the register, not "
                "about the run's usefulness: a run can inform the paper through a "
                "findings document without a register row.", ""]
        return out
    out += ["A run is linked to an analysis when the analysis's "
            "`conditions_compared` names one of this run's conditions. *Cells* is how "
            "many of the analysis's compared conditions come from this run, out of its "
            "total. *Signed* is the register's `manually_verified_at` stamp.", "",
            "| Analysis | Cells | Type | Hypotheses | Registration | Paper section "
            "| Deviations | Signed | Output |",
            "|---|---|---|---|---|---|---|---|---|"]
    for a in sorted(rows, key=lambda r: r["analysis_id"]):
        n_here = sum(1 for cid in (a.get("conditions_compared") or [])
                     if cid.startswith(f"{run_id}::"))
        total = len(a.get("conditions_compared") or [])
        out.append(
            f"| `{a['analysis_id']}` | {n_here} of {total} "
            f"| {_cell(a.get('type'))} | {_cell(a.get('hypothesis_refs'))} "
            f"| {_cell(a.get('preregistered'))} | {_cell(a.get('paper_section'))} "
            f"| {_cell(a.get('deviations'))} "
            f"| {_cell(a.get('manually_verified_at'))} "
            f"| `{_pipe(a.get('output_path') or NOT_SUPPLIED)}` |")
    out.append("")
    return out


_FINDINGS_RE = re.compile(r"(results/[\w./\-]*findings[\w./\-]*\.md)")


def _section_findings(run_id: str, corpus: Corpus) -> list[str]:
    """§ 7 — the findings documents that write this run up.

    Collected two ways, both deterministic: an analysis ``output_path`` that is a
    Markdown file, and any ``results/**findings*.md`` path mentioned in the
    analysis register's ``_note`` / ``outcome`` prose. Only paths that EXIST on
    disk are listed, so a stale mention cannot become a false citation.
    """
    rows = corpus.analyses_for(run_id)
    found: dict[str, set[str]] = {}
    for a in rows:
        aid = a["analysis_id"]
        out_path = a.get("output_path") or ""
        if out_path.endswith(".md") and (REPO_ROOT / out_path).is_file():
            found.setdefault(out_path, set()).add(aid)
        prose = " ".join(str(x) for x in (
            a.get("outcome") or "", a.get("predicted_outcome") or "",
            (corpus.run_analyses.get(aid) or {}).get("_note") or ""))
        for m in _FINDINGS_RE.findall(prose):
            if (REPO_ROOT / m).is_file():
                found.setdefault(m, set()).add(aid)
    out = [f"## 7. Findings documents ({len(found)})", ""]
    if not found:
        out += ["No findings document on disk is named by an analysis that reads this "
                f"run: a findings write-up for this run is **{NOT_SUPPLIED}** from "
                "the register. § 6's `output_path` column gives each analysis's "
                "artefact directory.", ""]
        return out
    out += ["| Document | Named by |", "|---|---|"]
    out += [f"| `{path}` | {', '.join(f'`{a}`' for a in sorted(aids))} |"
            for path, aids in sorted(found.items())]
    out.append("")
    return out


def _section_errata(run_id: str, corpus: Corpus) -> list[str]:
    """§ 8 — protocol errata bearing on this run.

    Two disjoint sources, labelled so neither borrows the other's authority:
    *registered* errata are those an analysis of this run lists in its
    ``deviations`` field; *textual* errata are those whose register entry mentions
    the run_id or its directory path. A textual mention is a pointer to read the
    entry, not a claim that the erratum is about this run.
    """
    directory = corpus.registry[run_id]["directory_path"]
    registered: set[str] = set()
    for a in corpus.analyses_for(run_id):
        registered.update(a.get("deviations") or [])
    titles = {eid: title for eid, title, _ in corpus.errata}
    textual = {eid for eid, _title, body in corpus.errata
               if run_id in body or directory in body}

    out = ["## 8. Protocol errata", ""]
    if not registered and not textual:
        out += ["No erratum in `docs/methodology/preregistration/protocol-errata.md` "
                "is registered against an analysis of this run, and none mentions the "
                "run or its directory.", ""]
        return out
    if registered:
        out += [f"### 8.1 Registered as deviations ({len(registered)})", "",
                "Listed in the `deviations` field of an analysis that reads this run:",
                ""]
        out += [f"- **{eid}** — {_prose(titles.get(eid))}"
                for eid in sorted(registered, key=_erratum_sort)]
        out.append("")
    other = sorted(textual - registered, key=_erratum_sort)
    if other:
        out += [f"### 8.2 Mentioning this run ({len(other)})", "",
                "The entry's text names this run id or its directory path. A mention "
                "is a pointer to read the entry, not a claim that the erratum is "
                "about this run:", ""]
        out += [f"- **{eid}** — {_prose(titles.get(eid))}" for eid in other]
        out.append("")
    return out


def _erratum_sort(eid: str) -> tuple[int, str]:
    """Sort E-numbers numerically (E9 before E71), unknown labels last."""
    m = re.fullmatch(r"E(\d+)", eid)
    return (int(m.group(1)), "") if m else (10**6, eid)


def _section_artefacts(run_id: str, corpus: Corpus) -> list[str]:
    """§ 9 — the documents and pool structure inside the run directory."""
    directory = REPO_ROOT / corpus.registry[run_id]["directory_path"]
    rel_base = corpus.registry[run_id]["directory_path"]
    out = ["## 9. Documents and structure in the run directory", ""]
    if not directory.is_dir():
        out += [f"`{rel_base}` does not exist in this checkout. If the run's outputs "
                f"live only on sapphire (untracked there), they are outside every "
                f"committed source this report is projected from and their contents "
                f"are **{NOT_SUPPLIED}** here.", ""]
        return out

    rows: list[tuple[str, str, int]] = []
    for name, label in IN_DIR_DOCS.items():
        hits = sorted(p.relative_to(directory).as_posix()
                      for p in directory.rglob(name))
        if hits:
            rows.append((label, name, len(hits)))
    if rows:
        out += ["| Document class | Filename | Count |", "|---|---|---:|"]
        out += [f"| {label} | `{name}` | {n} |" for label, name, n in rows]
        out += ["", "These classes are in Revision-Policy scope going forward "
                "(`docs/methodology/output-directory-standard.md` § \"Documents in "
                "Revision Policy Scope\").", ""]
    else:
        out += ["No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or "
                "retrospective report under this directory.", ""]

    decomp = corpus.decomposition.get(run_id, {})
    pools = decomp.get("proposer_pools") or {}
    vpasses = decomp.get("verifier_passes") or {}
    if pools or vpasses:
        out += ["### 9.1 Registered pools", ""]
        if pools:
            out += ["| Proposer pool | Modality | Path within the run directory |",
                    "|---|---|---|"]
            for name, spec in sorted(pools.items()):
                mod = spec.get("modality") if isinstance(spec, dict) else spec
                path = spec.get("path") if isinstance(spec, dict) else None
                path_cell = f"`{_pipe(path)}`" if path else (
                    f"{NOT_SUPPLIED} (string-form pool; resolved as "
                    f"`proposer/{_pipe(name)}`)")
                out.append(f"| `{_pipe(name)}` | {_cell(mod)} | {path_cell} |")
            out.append("")
        if vpasses:
            out += [f"{len(vpasses)} registered verifier-pass directory/directories; "
                    "see `results/run-conditions.json` for the full list.", ""]
    return out


def _section_provenance(run_id: str, corpus: Corpus, head: str) -> list[str]:
    """§ 10 — what this report was projected from."""
    row = corpus.runs.get(run_id, {})
    prov = row.get("provenance") or {}
    out = ["## 10. Provenance of this report", "",
           "This report is a projection. Every figure above is read from one of the "
           "committed inputs below; nothing is estimated, and a figure that is not on "
           f"file is written **{NOT_SUPPLIED}** with its reason.", "",
           "| Field | Value |", "|---|---|",
           f"| Generator | `scripts/generate_run_reports.py` v{GENERATOR_VERSION} |",
           f"| Source commit | `{head}` |",
           f"| Manifest extractor | `{_cell(prov.get('extractor_version'))}` |",
           f"| Run row last extracted | `{_cell(prov.get('last_extracted_at'))}` |",
           ""]
    out += ["Inputs:", ""]
    out += [f"- `{rel}`" for rel in INPUT_FILES]
    out += ["", "The run row's own upstream sources, as the manifest records them:", ""]
    src = prov.get("source_files") or []
    out += ([f"- `{s}`" for s in src] if src else [f"- {NOT_SUPPLIED}"])
    out += ["", "Regenerate and drift-check with:", "",
            "```bash", "python3 scripts/generate_run_reports.py --all --write",
            "python3 scripts/generate_run_reports.py --check", "```", ""]
    return out


# --------------------------------------------------------------------------- #
# Report assembly
# --------------------------------------------------------------------------- #


def render_report(run_id: str, corpus: Corpus, head: str) -> str:
    """Render one run's complete post-run report."""
    entry = corpus.registry[run_id]
    lines = [
        f"<!-- GENERATED FILE — do not hand-edit. Projected from the registered "
        f"manifests by scripts/generate_run_reports.py v{GENERATOR_VERSION}. "
        f"Hand edits are destroyed on the next regeneration and fail the --check "
        f"drift guard. -->",
        f"# Post-run report — {run_id}",
        "",
        "> **GENERATED FILE — do not hand-edit.** Projected from the registered "
        f"manifests by `scripts/generate_run_reports.py` v{GENERATOR_VERSION} at "
        f"source commit `{head}`. This file carries provenance instead of a hand "
        "changelog, per the PI ruling of 2026-09-11 recorded in "
        "`docs/methodology/output-directory-standard.md` § \"Documents in Revision "
        "Policy Scope\": a generated document's history is its inputs' and its "
        "generator's git history, so \"is this current?\" is answered by the "
        "`--check` drift guard and its tier-1 test, not by a changelog. Regenerate "
        "after any manifest rebuild; put before/after notes in the commit message.",
        "",
        f"**Directory**: `{entry['directory_path']}` · **Registry status**: "
        f"{_cell(entry.get('status'))} · **Purpose**: "
        f"{_prose((corpus.runs.get(run_id) or {}).get('purpose'))}",
        "",
    ]
    lines += _section_identity(run_id, corpus)
    lines += _section_scope(run_id, corpus)
    lines += _section_execution(run_id, corpus)
    lines += _section_cost(run_id, corpus)
    lines += _section_conditions(run_id, corpus)
    lines += _section_analyses(run_id, corpus)
    lines += _section_findings(run_id, corpus)
    lines += _section_errata(run_id, corpus)
    lines += _section_artefacts(run_id, corpus)
    lines += _section_provenance(run_id, corpus, head)
    text = "\n".join(lines).rstrip() + "\n"
    # collapse any accidental triple blank line so markdownlint MD012 holds
    return re.sub(r"\n{3,}", "\n\n", text)


def target_path(run_id: str, corpus: Corpus) -> Path:
    """Where this run's report is written."""
    return REPO_ROOT / corpus.registry[run_id]["directory_path"] / "post_run_report.md"


def runs_to_project(corpus: Corpus) -> list[str]:
    """Registered runs that get a generated report, in registry order."""
    return [rid for rid in corpus.registry if rid not in HAND_AUTHORED]


#: Every place a report writes the source-commit stamp. ``--check`` blanks all of
#: them before comparing, because regenerating at a new HEAD must not read as drift
#: when the projection itself is unchanged — the same neutralisation the
#: hypothesis-outcome table's ``--check`` uses.
#:
#: There are TWO sites, and missing one is not a cosmetic slip. The stamp is written
#: by the commit that lands the reports, so from the moment that commit exists HEAD
#: has moved past it and an un-neutralised site NEVER matches again: the guard fires
#: on every run, for every report, for ever, reporting drift that does not exist and
#: hiding drift that does. The first version of this function neutralised only
#: ``source commit `…` `` in the banner and missed the § 10 table cell, where the
#: pipe and spaces break the contiguous ``commit `` match — caught by the full
#: tier-1 suite the first time it ran after the landing commit, which is the guard
#: working on itself.
_STAMP_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"source commit `[^`]+`", "source commit `X`"),          # the banner
    (r"\| Source commit \| `[^`]+` \|", "| Source commit | `X` |"),  # § 10's table
)


def _neutralise(text: str) -> str:
    """Blank every source-commit stamp so only real content differences remain."""
    for pattern, replacement in _STAMP_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


def main(argv: list[str] | None = None) -> int:
    """Entry point. 0 success; 1 drift found; 2 a bad CLI argument."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true", help="Project every registered run.")
    ap.add_argument("--run", metavar="RUN_ID",
                    help="Project one run; prints the report unless --write.")
    ap.add_argument("--write", action="store_true",
                    help="Write the reports into their run directories.")
    ap.add_argument("--check", action="store_true",
                    help="Regenerate in memory and exit 1 if any committed report "
                         "differs (the drift guard; ignores the commit stamp).")
    args = ap.parse_args(argv)
    if not (args.all or args.run or args.check):
        ap.print_help()
        return 2

    corpus = Corpus()
    head = _git_head()

    if args.run:
        if args.run not in corpus.registry:
            print(f"No run '{args.run}' in results/run-registry.json.", file=sys.stderr)
            return 2
        if args.run in HAND_AUTHORED:
            print(f"'{args.run}' has a hand-authored post-run report — not projected.\n"
                  f"  reason: {HAND_AUTHORED[args.run]}", file=sys.stderr)
            return 2
        text = render_report(args.run, corpus, head)
        if args.write:
            path = target_path(args.run, corpus)
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO_ROOT)} ({len(text):,} bytes)")
        else:
            print(text)
        return 0

    targets = runs_to_project(corpus)

    if args.check:
        stale, missing = [], []
        for rid in targets:
            path = target_path(rid, corpus)
            if not path.exists():
                missing.append(path.relative_to(REPO_ROOT).as_posix())
            elif _neutralise(path.read_text(encoding="utf-8")) != _neutralise(
                    render_report(rid, corpus, head)):
                stale.append(path.relative_to(REPO_ROOT).as_posix())
        for label, group in (("MISSING", missing), ("STALE", stale)):
            for rel in group:
                print(f"{label}: {rel}")
        if missing or stale:
            print(f"\n{len(missing)} missing, {len(stale)} stale of {len(targets)} "
                  f"generated report(s) — re-run with --all --write")
            return 1
        print(f"all {len(targets)} generated post-run report(s) up to date "
              f"({len(HAND_AUTHORED)} hand-authored report(s) skipped by design)")
        return 0

    written = 0
    for rid in targets:
        text = render_report(rid, corpus, head)
        path = target_path(rid, corpus)
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1
        print(f"  {'wrote' if args.write else 'would write'} "
              f"{path.relative_to(REPO_ROOT).as_posix():62s} {len(text):>7,} bytes")
    print(f"\n{written if args.write else len(targets)} report(s) "
          f"{'written' if args.write else 'projected'} at source commit {head}")
    for rid, reason in HAND_AUTHORED.items():
        print(f"  skipped {rid}: {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
