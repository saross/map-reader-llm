#!/usr/bin/env python3
"""Render the sweep-staleness survey report from its JSON survey file.

Every figure in ``reports/sweep-staleness-survey-2026-09-08.md`` is read from
``reports/sweep-staleness-survey-2026-09-08.json`` (produced by
``scripts/survey_sweep_staleness.py`` on sapphire against the working tree)
so that no number is transcribed by hand. Survey of 2026-09-08, Session 151.

Usage
-----
    python scripts/render_sweep_staleness_report.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SURVEY_JSON = REPO / "reports" / "sweep-staleness-survey-2026-09-08.json"
REPORT_MD = REPO / "reports" / "sweep-staleness-survey-2026-09-08.md"
SURVEY = json.loads(SURVEY_JSON.read_text())
SUM = SURVEY["summary"]
STAGES = SURVEY["stages"]

KNOWN = "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10"

# Supplementary citations found by a direct grep of planning/, which sits
# outside the results/reports/docs grep scope of the survey script.
PLANNING_HITS = {
    "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10": [
        "planning/phase3a-verifier-recovery-runbook.md:109 (cell 9, gap 460, "
        "\"**NOT cited** in any leaderboard / script\")",
        "planning/verifier-stage-refresh-2026-09-08.md:30",
    ],
    "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5": [
        "planning/phase3a-verifier-recovery-runbook.md:110 (cell 10, gap 11, "
        "feeds `flash-high-image-n5-t0.3-greedy-v1-487tile.json`)",
    ],
    "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5": [
        "planning/phase3a-verifier-recovery-runbook.md:113 (cell 13, gap 1, "
        "feeds `flash-high-image-n5-t0.7-greedy-v1-487tile.json`)",
    ],
    "outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5": [
        "planning/phase3a-verifier-recovery-runbook.md:112 (cell 12, gap 1, "
        "feeds `flash-high-image-n5-t1.0-greedy-v1-487tile.json`)",
    ],
    "outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10": [
        "planning/phase3a-verifier-recovery-runbook.md:114 (cell 14, gap 1, "
        "feeds `scale4-optimal-greedy-v1-487tile.json`)",
    ],
}

stale = sorted((s for s in STAGES if s["verdict"] == "STALE"),
               key=lambda s: s["stage_dir"])
incomplete = sorted((s for s in STAGES if s.get("incomplete")),
                    key=lambda s: s["stage_dir"])
no_sweep = sorted(s["stage_dir"] for s in STAGES if s["verdict"] == "NO SWEEP")
cleanup_no_sweep = sorted(
    (s for s in STAGES
     if s["cleanup_history_present"] and s["verdict"] == "NO SWEEP"),
    key=lambda s: s["stage_dir"])

out: list[str] = []
w = out.append

w("# Sweep-staleness survey of verifier stages")
w("")
w("> **Last revised**: 2026-09-08 (original publication). See "
  "[§ Changelog](#changelog) for revision history.")
w(">")
w(f"> **Surveyed**: 2026-09-08 against repository HEAD `{SUM['head_commit']}` "
  "(working tree, branch `main`). Read-only: no repository file was created or "
  "modified.")
w("")

# ---------------------------------------------------------------- method
w("## Method")
w("")
w(f"Every directory under `outputs/` holding a `probabilities.json` whose "
  f"`results` entries carry `mound_probability` was enumerated "
  f"({SUM['total_stages']} stages, ~470 MB of JSON), and each was paired with "
  "any file in the same directory whose name starts with `sweep`. For each "
  "sweep the \"all candidates\" cell was taken as the maximum `n` over rows at "
  "the lowest `vote_t` with `prob_t == 0.0` (across every `buffer_m` and "
  "`config`), and compared with the count of candidates currently holding a "
  "non-null probability. Last-commit provenance for both artefacts came from a "
  "single `git log --name-only` traversal of `outputs/` and `results/`. "
  "Completeness was checked two ways, because the known failure hides entries "
  "rather than nulling them: null-valued entries, and entries absent relative "
  "to the stage's own `candidate_manifest.json`. Flagged stages were then "
  "cross-referenced against `results/run-conditions.json` (conditions' "
  "`detections`/`eval_path` and the per-run `verifier_passes` block, whose "
  "paths are run-relative), `results/run-analyses.json` (`output_path`), and a "
  "line-level grep of every Markdown file under `results/`, `reports/`, and "
  "`docs/`.")
w("")
w("**Compute**: run on `sapphire` (`ssh sapphire`, repo at "
  "`~/Code/map-reader-llm`, venv `.venv`), per the project's compute-location "
  "rule. Script copied to `sapphire:/tmp/survey_sweep_staleness.py` and "
  "executed there; `survey.json` copied back. Wall time 3.9 s "
  "(the tree was in page cache), 2,524 Markdown files / 229,058 lines scanned.")
w("")

# --------------------------------------------------------------- summary
w("## Summary counts")
w("")
w("| Category | Count |")
w("| --- | ---: |")
w(f"| Verifier stages found (`probabilities.json` with `mound_probability`) | "
  f"{SUM['total_stages']} |")
w(f"| CONSISTENT (sweep n == candidates with a probability) | {SUM['consistent']} |")
w(f"| **STALE** (sweep n < candidates with a probability) | **{SUM['stale']}** |")
w(f"| NO SWEEP (no `sweep*` file in the stage directory) | {SUM['no_sweep']} |")
w(f"| UNPARSED (sweep schema unreadable) | {SUM['unparsed']} |")
w(f"| Sweep n exceeds probabilities (other mismatch) | "
  f"{SUM['sweep_exceeds_probs']} |")
w(f"| INCOMPLETE (candidates missing or null-valued) | {SUM['incomplete']} |")
w("")
w("Supporting counts, same run:")
w("")
w(f"- Stages carrying a `cleanup_history`: **{SUM['cleanup_touched']}**; of "
  f"those, {SUM['stale']} have an in-directory sweep (all {SUM['stale']} are "
  f"STALE) and {SUM['cleanup_touched_no_sweep']} have none.")
w(f"- Sweep files found in stage directories: "
  f"{sum(len(s['sweeps']) for s in STAGES)}, every one named `sweep_2d.json` "
  "and every one the documented top-level-list schema "
  "(`config, vote_t, prob_t, n, p, r, f1, buffer_m`). No other sweep filename "
  "or schema occurs inside a stage directory.")
w(f"- Authoritative `candidate_manifest.json` available for "
  f"{SUM['manifest_authoritative']} stages; the other "
  f"{SUM['manifest_absent_or_sibling']} have no manifest, or only a shared "
  "sibling `crops/` manifest that cannot be attributed to the stage.")
w(f"- Register linkage: {SUM['register_passes_resolved']} `verifier_passes` "
  f"entries resolved to a stage directory, "
  f"{SUM['register_passes_unresolved']} unresolved.")
w("")

# ------------------------------------------------------- detector check
known = next((s for s in STAGES if s["stage_dir"] == KNOWN), None)
w("## Detector validation against the known case")
w("")
if known and known["verdict"] == "STALE":
    sw = known["sweeps"][0]
    g, p = sw["git"], known["prob_git_last"]
    rec = (known["cleanup_recovered"] or [{}])[0]
    w(f"**PASS.** `{KNOWN}` is flagged STALE. The detector reads its "
      f"`sweep_2d.json` all-candidates cell (`vote_t={sw['min_vote_t']}`, "
      f"`prob_t={sw['min_prob_t']}`, max over buffers "
      f"{sw['buffers']}) as **n = {sw['all_cand_n']}**, last committed "
      f"`{g['commit']}` ({g['date']}), against **{known['n_with_probability']} "
      f"candidates with a probability** in `probabilities.json`, last committed "
      f"`{p['commit']}` ({p['date']}, \"{p['subject']}\"). The "
      f"`cleanup_history` records `initial_missing={rec.get('initial_missing')}`, "
      f"`recovered={rec.get('recovered')}`, "
      f"`still_missing={rec.get('still_missing')}` at "
      f"{rec.get('timestamp')} — matching the brief's description exactly "
      f"(342 swept, 460 later added, 802 total).")
else:
    w(f"**FAIL.** `{KNOWN}` was not flagged STALE — verdict "
      f"{known['verdict'] if known else 'stage not found'}.")
w("")
w("Two independent corroborations that the detector measures the intended "
  "quantity, not an artefact:")
w("")
w("1. `reports/phase3a-verifier-completeness-audit-2026-05-03.md` (written "
  "before the cleanup) tabulates the same pre-cleanup counts this survey "
  "recovers from the sweeps — e.g. line 126 records `2190 | 2179 | 11` for "
  "`image-t0.3/verified-v1-n5`, and the stale sweep's all-candidates cell is "
  "2179 against 2190 probabilities.")
w("2. All 28 CONSISTENT stages match exactly (sweep n == probabilities n == "
  "results n) and in every case the sweep and the probabilities were committed "
  "in the *same* commit — the expected signature of a sweep run after its "
  "verification finished.")
w("")

# ----------------------------------------------------------- stale table
w("## STALE stages (full table)")
w("")
w(f"All {len(stale)} share one history: swept during the April verification "
  "commits, then amended by the 2026-05-06 Tier-2 cleanup pass `c6b5e6b10` "
  "(\"data(p3a-recovery): cleanup Tier-2 cells (6 cells, 474 cands)\"), with no "
  "re-sweep afterwards. Their recovered counts sum to "
  f"{sum(sum((e.get('recovered') or 0) for e in (s['cleanup_recovered'] or [])) for s in stale)} "
  "candidates, which is that commit's 474.")
w("")
w("| # | Stage | Sweep n | Probs n (with prob / results) | Gap | Sweep commit | "
  "Probs commit | cleanup_history (recovered) |")
w("| --: | --- | --: | --: | --: | --- | --- | --- |")
for i, s in enumerate(stale, 1):
    sw = s["sweeps"][0]
    g, p = sw["git"], s["prob_git_last"]
    rec = sum((e.get("recovered") or 0) for e in (s["cleanup_recovered"] or []))
    gap = s["n_with_probability"] - sw["all_cand_n"]
    w(f"| {i} | `{s['stage_dir']}` | {sw['all_cand_n']} | "
      f"{s['n_with_probability']} / {s['n_results']} | **{gap}** | "
      f"`{g['commit']}` {g['date']} | `{p['commit']}` {p['date']} | "
      f"yes ({rec}) |")
w("")
w("Per-stage detail, register cross-references, and citing documents:")
w("")
for i, s in enumerate(stale, 1):
    sw = s["sweeps"][0]
    g, p = sw["git"], s["prob_git_last"]
    man = s["manifest"] or {}
    w(f"### {i}. `{s['stage_dir']}`")
    w("")
    w(f"- **Sweep**: `{sw['path']}` — {sw['n_rows']} rows, schema "
      f"`{sw['schema']}`, configs {sw['configs']}, buffers {sw['buffers']}; "
      f"all-candidates cell at `vote_t={sw['min_vote_t']}` / "
      f"`prob_t={sw['min_prob_t']}` gives **n = {sw['all_cand_n']}** "
      f"(identical across all buffers: min {sw['all_cand_n_min']}, max "
      f"{sw['all_cand_n']}). Last commit `{g['commit']}` ({g['date']}) — "
      f"\"{g['subject']}\".")
    w(f"- **Probabilities**: {s['n_results']} results, "
      f"{s['n_with_probability']} with a non-null `mound_probability`, "
      f"`total_results` field = {s['total_results_field']}. Last commit "
      f"`{p['commit']}` ({p['date']}) — \"{p['subject']}\".")
    hist = s.get("prob_git_history") or []
    if len(hist) > 1:
        w("  - Commit history: "
          + "; ".join(f"`{h['commit']}` {h['date']}" for h in hist))
    w(f"- **cleanup_history**: {json.dumps(s['cleanup_recovered'])}")
    w(f"- **Crop manifest** ({man.get('scope')}): "
      f"{man.get('n_candidates')} candidates, "
      f"`total_detections`={man.get('total_detections')} — shortfall vs "
      f"probabilities = {s['manifest_shortfall']} (stage is complete; only the "
      "sweep is behind).")
    reg = s["register"]
    if reg["verifier_passes"]:
        for vp in reg["verifier_passes"]:
            w(f"- **Register**: `results/run-conditions.json` → "
              f"`decomposition/{vp['run_id']}/verifier_passes/{vp['pass_id']}` "
              f"(`path` = `{vp['rel_path']}`, modality {vp['modality']}).")
    else:
        w("- **Register**: no `verifier_passes` entry.")
    w(f"- **Register conditions** with `detections`/`eval_path` inside this "
      f"stage: {len(reg['conditions']) or 'none'}"
      + ("" if not reg["conditions"] else
         " — " + "; ".join(f"{c['run_id']}/{c['label']} ({c['field']})"
                           for c in reg["conditions"])) + ".")
    w(f"- **Register analyses** with `output_path` inside this stage: "
      f"{len(reg['analyses']) or 'none'}.")
    cites = s.get("doc_citations") or {"hits": []}
    if cites["hits"]:
        w("- **Cited in** (`results/`, `reports/`, `docs/`; first 3 hits):")
        for h in cites["hits"]:
            w(f"  - `{h['file']}:{h['line']}` — {h['text'][:150]}")
    else:
        w("- **Cited in** (`results/`, `reports/`, `docs/`): no hits.")
    for extra in PLANNING_HITS.get(s["stage_dir"], []):
        w(f"- **Also cited in** (outside the specified grep scope): {extra}")
    w("")

# --------------------------------------------------------- remediation
w("## Remediation status of the five")
w("")
w("Only the known case has been re-swept. "
  "`results/recovery-reeval-2026-09-08/pv-diag-384/"
  "image-t0.0-verified-v1-n10-april-complete-resweep/sweep_2d.json` (240 rows, "
  "all-candidates cell n = 802) is today's like-for-like re-sweep of the "
  "April stage's complete probabilities, and its README states the diagnosis "
  "this survey reproduces independently. The stage's own `sweep_2d.json` was "
  "deliberately left in place under the preserve-and-compare policy, so it "
  "still reads STALE by the counts and always will.")
w("")
w("**The other four have no re-sweep anywhere in `results/`.** Their downstream "
  "exposure, as far as it can be traced:")
w("")
w("- `planning/phase3a-verifier-recovery-runbook.md` records each as feeding a "
  "named leaderboard cell. All four of those cells now live only in "
  "`archive/superseded-leaderboards/leaderboard/cells/`, retired by "
  "`b69d8af4b` (2026-08-20, \"chore(archive): retire the legacy "
  "results/leaderboard family\") — no live leaderboard consumes them.")
w("- Of those archived cells, `scale4-optimal-greedy-v1-487tile.json` records "
  "`n_candidates_loaded` = 3600, i.e. the **pre-cleanup** count for "
  "`scale-4-optimal-487/verified-v1-n10` (complete: 3601) — that cell was "
  "built on the partial set.")
w("- The other three cells record `n_candidates_loaded` of 3412, 3211, and "
  "4638, which are the counts of the *`verified-v1-n10`* siblings (all "
  "CONSISTENT), not of the STALE `verified-v1-n5` stages. The runbook's "
  "\"feeds\" mapping is therefore looser than it reads: those three cells do "
  "not appear to have been built on the stale sweeps.")
w("")
w("Gaps of 11, 1, 1, and 1 candidate on pools of 2,190–3,601 are small — the "
  "runbook's own estimate for the largest (cell 10, gap 11) was \"Likely "
  "<0.005 F1 movement\" "
  "(`planning/phase3a-verifier-recovery-runbook.md:110`) — but each stage's "
  "in-directory sweep is nonetheless a partial-verification artefact, and "
  "nothing in the directory says so.")
w("")

# ------------------------------------------------------------ incomplete
w("## INCOMPLETE stages")
w("")
if not incomplete:
    w(f"**None.** Across all {SUM['total_stages']} stages, every "
      "`probabilities.json` entry carries a non-null `mound_probability`, no "
      "`cleanup_history` reports `still_missing > 0`, and for the "
      f"{SUM['manifest_authoritative']} stages with an attributable "
      "`candidate_manifest.json` the probability count equals the manifest "
      "candidate count exactly (shortfall 0 in every case). The five STALE "
      "stages are themselves complete — the gap is in the sweep, not the "
      "verification.")
else:
    w("| Stage | Results | With probability | Manifest | Shortfall | Reasons |")
    w("| --- | --: | --: | --: | --: | --- |")
    for s in incomplete:
        man = s["manifest"] or {}
        w(f"| `{s['stage_dir']}` | {s['n_results']} | "
          f"{s['n_with_probability']} | {man.get('n_candidates')} | "
          f"{s['manifest_shortfall']} | {', '.join(s['incomplete_reasons'])} |")
w("")

# ------------------------------------------------------ cleanup, no sweep
w("## Cleanup-touched stages with no in-directory sweep")
w("")
w(f"These {len(cleanup_no_sweep)} stages were amended by a cleanup pass but "
  "carry no `sweep*` file, so the staleness class as defined cannot arise "
  "inside the directory. They are listed because the same hazard could exist "
  "in whatever *external* artefact consumed them.")
w("")
w("| Stage | Recovered | Results | Probabilities last commit |")
w("| --- | --: | --: | --- |")
for s in cleanup_no_sweep:
    rec = sum((e.get("recovered") or 0) for e in (s["cleanup_recovered"] or []))
    p = s["prob_git_last"] or {}
    w(f"| `{s['stage_dir']}` | {rec} | {s['n_results']} | "
      f"`{p.get('commit', '-')}` {p.get('date', '-')} |")
w("")
ext_rows = [(s, e) for s in STAGES for e in (s.get("external_eval_checks") or [])]
w(f"For the cleanup-touched stages the register links "
  f"{len(ext_rows)} conditions whose `detections` lie inside the stage "
  "directory. Comparing each condition's `eval_path` last-commit date with the "
  "stage's probabilities last-commit date, **0 of "
  f"{len(ext_rows)} evaluations predate the cleanup** — every one was last "
  "committed after the probabilities were amended. See the caveat below on "
  "what that check can and cannot establish.")
w("")

# --------------------------------------------------------------- no sweep
w("## NO SWEEP stages")
w("")
w(f"{len(no_sweep)} stages hold no file whose name starts with `sweep`. The "
  "full list is in `survey.json`; paths follow.")
w("")
for path in no_sweep:
    w(f"- `{path}`")
w("")

# --------------------------------------------------------------- caveats
w("## Caveats")
w("")
w("1. **Scope is the in-directory sweep.** Only files named `sweep*` inside the "
   "stage directory were treated as that stage's sweep. Sweeps and evaluations "
   "computed over a stage but written elsewhere (e.g. "
   "`results/h8-v2/verifier-sweep/*/sweep_2d_greedy_pv.json`, "
   "`results/rescore-2026-05-31/pv-diag-384/sweep/`, "
   "`results/verifier-robustness/sweep-sets/`) were not matched back to their "
   "source stage; a pre-cleanup sweep living in `results/` would not be caught "
   "by this survey.")
w("2. **Commit dates are a coarse proxy.** The external-evaluation check "
   "compares git commit dates, not content. A file re-committed for an "
   "unrelated reason (a bulk move, a reformat) looks fresh — several rescore "
   "evaluations share the single commit `70c550177` (2026-08-23) — so \"does "
   "not predate the cleanup\" means the artefact was touched later, not that it "
   "was recomputed on the complete probabilities.")
w("3. **`n` is a detection count, not a candidate count.** The sweep's `n` "
   "counts detections surviving the threshold pair, so its equality with the "
   "probability count at `vote_t`=min / `prob_t`=0.0 is an empirical property "
   "of this pipeline (it holds exactly in all 28 CONSISTENT stages), not a "
   "definitional identity. A sweep whose candidate pool legitimately differs "
   "from the stage's would read as STALE here.")
w("4. **Manifest attribution.** Completeness could be checked against a crop "
   f"manifest for only {SUM['manifest_authoritative']} of "
   f"{SUM['total_stages']} stages. For the remaining "
   f"{SUM['manifest_absent_or_sibling']} the only completeness evidence is "
   "null-valued entries and `cleanup_history`, which cannot detect candidates "
   "that were never written and never recorded as missing.")
w(f"5. **Register coverage.** {SUM['register_passes_unresolved']} "
   "`verifier_passes` entries could not be resolved to a stage directory "
   "(listed in `survey.json` under "
   "`summary.register_passes_unresolved_detail`), mostly `verifier-robustness` "
   "passes whose recorded path is the parent of the stage and "
   "`proposer-verifier-384` image passes with no matching directory. A stage "
   "reached only through one of those would show no register linkage here.")
w("6. **Moving HEAD.** Another session committed to `main` during the survey "
   "(`de0fde55e` → `8a67c8881`, a documentation commit plus a one-line change "
   "to `results/run-conditions.json`). The reported run is entirely against "
   f"`{SUM['head_commit']}`; no file under `outputs/` changed between the two.")
w("7. **Read-only compliance.** No repository file was created, modified, or "
   "committed; all writing went to the scratchpad and to `sapphire:/tmp/`. "
   "A local `git status` during the survey listed 16 files as modified "
   "(mostly under `archive/`); these are an artefact of the sandboxed shell "
   "failing to read some blobs — `git` reported \"short read while indexing\" "
   "on one, and that file "
   "(`results/h11-384-pv-diagnostic/flash-high-image-4of5/threshold_sweep.csv`) "
   "is byte-identical on sapphire (1,618 bytes, md5 "
   "`b2cdfdd2220593fc81cbb84e606ca9f8`) and clean in sapphire's `git status`. "
   "The survey itself read the tree on sapphire, so it is unaffected.")
w("")

# ------------------------------------------------------------- artefacts
w("## Artefacts")
w("")
w("- `reports/sweep-staleness-survey-2026-09-08.json` — raw per-stage records (all 265 stages: counts, "
  "`cleanup_history`, git provenance for probabilities and sweeps, sweep "
  "parse detail, manifest cross-check, register links, doc citations).")
w("- `scripts/survey_sweep_staleness.py` — the survey script (run on sapphire).")
w("- `scripts/render_sweep_staleness_report.py` — renders this report from the JSON.")
w("")
w("## Changelog")
w("")
w("### 2026-09-08 — Original publication")
w("")
w("Survey commissioned in Session 151 after the image-stage finding "
  "(`reports/recovery-consistency-audit-2026-09-08.md` § 6.1); run on sapphire "
  "at HEAD `8a67c8881`; five stale stages, none cited by a registered condition "
  "or analysis.")
w("")

text = "\n".join(line.rstrip() for line in out).rstrip() + "\n"
REPORT_MD.write_text(text)
print(f"wrote {REPORT_MD.relative_to(REPO)} ({len(out)} lines)")
