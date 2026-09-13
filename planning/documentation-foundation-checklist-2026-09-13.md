# Documentation foundation checklist — the preregistration → outcome chain

> **Last revised**: 2026-09-13 (Batch 1 items 1 and 2 closed; prior
> 2026-09-13: original publication, Session 153, the PI asked for the
> chain's remaining documentation to be externalised as a checklist to
> work through before the paper's outline pass). See
> [§ Changelog](#changelog).

**Purpose**: make sure every primary and intermediate document on the
chain preregistration → experiment → result → analysis → outcome is
complete and current, so the paper is written from a closed foundation.
Items are ticked with a date and the commit that closed them; nothing is
deleted. Agent tier per item follows the subagent policy: Opus for all
agent work; Fable only for the PI-facing orchestration turns.

## 1. The chain, link by link (state on 2026-09-13)

| Link | Artefact | State | Gap |
|---|---|---|---|
| Preregistration → hypotheses | `results/hypothesis-outcome-table/` (generated, drift-guarded) | complete: 15 hypotheses, every row with analyses, status, errata | none (paper sentence on H6 not-executed rests on E40/E41/E74) |
| Experiments → runs and conditions | `results/runs-manifest.json`, `results/conditions-manifest.json`, `scripts/verify_run_conditions.py` | 41 runs, 593 conditions all with metrics; verifier ~~22 pass / 19 partial~~ → **38 pass / 3 partial / 0 fail** (2026-09-13, `f4fd90c71` + `e88fd5bfa`) | closed to the annotation limit (§ 2 item 2); the 3 remaining partials are by-design disclosures, and reaching 41 needs a PI verdict-model call |
| Runs → post-run reports | `outputs/**/post_run_report.md` | ~~2 of 36 run directories~~ → **41 of 41** (2026-09-13, `c4edf1328`): 39 generated projections + 2 hand-authored | closed (§ 2 item 1) |
| Results → analyses → signatures | `results/run-analyses.json`; findings documents | 67 rows, 66 signed, 1 unsigned by design; every findings doc bannered | boards pending one rebuild each (§ 2 items 4–5); the image run's row (§ 2 item 6) |
| Deviations → errata | `docs/methodology/preregistration/protocol-errata.md` (E1–E85) | complete register | Methods amendments section currency to E85 (§ 2 item 7) |
| Working notes | `docs/notes/working-notes.md` (Obs 1–476) | current | four or five Obs from 2026-09-12/13 (§ 2 item 3) |
| Paper-facing | `docs/paper/results-draft.md`, `results-outline.md`, `results-claims-inventory-2026-09-12.md`, `methods-draft.md`, `discussion-outline.md`, `discussion-seeds.md`, `manuscript-skeleton-isprs.md` | outline decisions D1–D22 settled; inventory built for R0–R2, R4–R5, R7–R9; Methods zero-draft; Discussion outline current to August | § 2 items 8–10; D-1..D-5 and D.9 stay DEFERRED |
| The project's own documentation audit | `planning/interim-docs-review.md` (2026-04-22), `docs/methodology/output-directory-standard.md` compliance table (2026-05-26) | stale | § 2 item 11 |

## 2. Items (tick with date + commit; never delete)

**Batch 1 — $0, Opus agents, can run now**

- [x] **1. Post-run reports for every run directory** — done 2026-09-13,
  commit `c4edf1328`. The gap was **39 of 41**, not 34 of 36: the registry
  holds 41 runs at 41 distinct directory paths, all present and tracked,
  and 2 carried a report. Taken via the GENERATED-PROJECTION route the
  2026-09-11 ruling opened — 39 reports emitted by the new
  `scripts/generate_run_reports.py` with a GENERATED banner, a
  source-commit stamp and a `--check` drift guard run by a tier-1 test,
  rather than 39 hand changelogs that would each go stale at the next
  manifest rebuild. The 2 hand-authored narrative reports were NOT
  overwritten (their Dawid-Skene corrections and paired comparisons are
  not re-derivable from the manifests) and took the banner + Changelog
  instead — which corrected the standard's "2 compliant" cell, since
  neither had carried either. Deltas:
  `reports/documentation-batch1-deltas-2026-09-13.md` § 2.
  Anchor: `docs/methodology/output-directory-standard.md`
  § "Documents in Revision Policy Scope" (scope table and changelog
  updated in the same commit).
- [x] **2. Resolve the 19 partial runs** — done 2026-09-13, commits
  `f4fd90c71` (verifier) and `e88fd5bfa` (annotations). Verifier
  **22 pass / 19 partial → 38 pass / 3 partial / 0 fail**; 221 open WARNs
  → 12. Cleared: 115 `pool-unresolved` by `source_run` annotation across
  seven runs (each with its filesystem or authoring-script anchor), 13
  `unclaimed-eval` by `_ignored_evals` waivers with reasons, and 81
  instrument false positives by two verifier corrections — 79
  `geojson-missing` that were directory-valued detections (aggregated
  multi-pass cells, all present) and 2 `pool-dir-not-found` that were
  materialised pool files. No metric, evaluation, detection or threshold
  changed; every runs/conditions/passes manifest row is identical modulo
  extraction timestamps.
  **Target was 41 pass; 38 is the honest maximum by annotation.** The
  remaining 3 runs hold 12 WARNs that are by-design disclosures the
  project has already settled — `n-passes-over` on
  `55maps-text-min-n10-uplift` (the mixed-provenance pool's "honest
  by-design signal", S106) and `pinned-vintage` on `e47-propose-brief`
  and `n1-outstanding-384` (ruling 3a, raised only when the pin CHECKS
  OUT). Clearing either would delete a disclosure. **Open for the PI**: a
  verdict-model change — a third `disclosures` list beside
  `discrepancies`, with PASS defined over `discrepancies` alone — would
  reach 41 pass without losing the disclosures, but it changes what a
  signature attests, so it was flagged rather than done
  (`reports/documentation-batch1-deltas-2026-09-13.md` § 3.4).
- [ ] **3. Obs for the 2026-09-12/13 findings**: the tile-join class (a
  metric keyed by a name beside one keyed by geometry; overlapping frames);
  the recovery-fragment class (a count can hold while the set changes; a
  fragment can lower the count); the verifier-stage reversal of tile-MCC's
  response to K; the MCB-versus-greedy disagreement in both directions;
  the AUD-against-USD corroboration. Owner: obs-writer (Opus).
- [ ] **4. Methods amendments section currency** (`docs/paper/methods-draft.md`
  § M.x) to E85 and the S153 rulings (generated projections; the
  name-based tile join as published convention; the carried-point
  convention). Owner: Opus agent.
- [ ] **5. Refresh the project's documentation audit**: re-run the
  interim-docs scorecard against today's inventory and update the
  output-directory standard's compliance table with current counts.
  Owner: Opus agent.

**Batch 2 — after the image run lands ($0 except as noted)**

- [ ] **6. Era-2 board rebuild and re-signature**: the four re-scored
  cells (recovery-fragment fix, landed `eda4ab70e`: three unchanged, k3
  0.8870 → 0.8860), the tile-MCC permutation family (ruling 7), one
  rebuild, one signature (PI: "I'll wait"). Owner: Opus agent; PI signs.
  - [ ] **6a. Prerequisite**: the tile-join invariant currently raises
    inside `bootstrap_ci` and aborts the WHOLE evaluation of a refused
    cell, so the k3 cell's moved F1 cannot be written to its evaluation
    or register row. Under ruling 6 (name-based join published; refused
    cells' F1 reported in full, per-tile table withheld) the invariant
    must withhold the per-tile table and let F1 and its bootstrap proceed.
    Code fix + test, then write the k3 evaluation. Also promote
    `carry_probabilities.py` (integer-crop-window coverage test) to
    `scripts/`. Owner: Opus agent.
  - [ ] **6b. PI decision**: one verifier call (≈ US$0.0007) to make
    tier E's K = 5 zero-delta unconditional (candidate_01335 carried 0.10
    across a 1 px crop shift against a 0.15 gate) — or accept as
    conditional and disclosed.
- [ ] **7. 55-map board r2 rebuild**: the K = 5 rung of stride B under the
  3.7 verifier, the image run's cells (K = 1, K = 3, both arms), the MCC
  tiering; signatures. Owner: Opus agent; PI signs.
- [ ] **8. The image run's analysis row** `gemini37-image-55map-2026-09-13`
  and findings; P1–P5 verdicts; the deployment-scale modality result into
  the Results inventory. PI signs.
- [ ] **9. Results draft housekeeping**: clear the four `[DRAFT, S153 —
  pending PI ruling]` markers now ruled; extend the claims inventory to
  R3, R6 and R1b against the ladder findings; regenerate the cross-section
  summary. Owner: Opus agent.
- [ ] **10. Uplift supplement currency**: re-pair if any new verified cell
  gains a twin by construction; amend and re-sign the pairing row only if
  counts move.
- [ ] **11. Second documentation audit pass** after items 6–10, so the
  scorecard describes the foundation the outline pass starts from.

**Then**: the Results outline pass proper, section by section, with the
PI ruling per section (the standing "outline first" rule); the
literature-review walk-through alongside; D-1..D-5 and D.9 re-opened only
after that.

## 3. Standing rules that apply

- Signatures mean something: every re-signature is presented with what
  it attests, what changed, what did not.
- Keep history, present the best available; ladder, then board.
- Generated projections carry provenance, not a hand changelog.
- Compute on sapphire; at most three live worktrees on the local disk.

## Changelog

### 2026-09-13 — Batch 1 items 1 and 2 closed (Session 153)

| Claim | Before | After |
|---|---|---|
| Run directories with a post-run report | 2 of 36 (card's figure) | 41 of 41 — the registry holds 41 runs at 41 distinct paths, so the gap was 39 |
| Verifier verdicts | 22 pass / 19 partial / 0 fail | 38 pass / 3 partial / 0 fail |
| Open verifier WARNs | 221 | 12, all by-design disclosures |

**What did NOT change**: no metric, evaluation, detection, threshold or
signature; 41 runs and 593 conditions before and after. Deltas with anchors:
`reports/documentation-batch1-deltas-2026-09-13.md`.

**Raised for the PI** (not actioned): reaching 41 pass needs a verifier
verdict-model change — a `disclosures` list beside `discrepancies`, with PASS
defined over `discrepancies` alone — because the remaining 12 WARNs are
satisfied checks the model has nowhere to put. That changes what a signature
attests, so it is a PI call, not an agent's.

### 2026-09-13 — Original publication (Session 153)

Externalised from the chain assessment given in session. Batch 1
launched the same day on Opus agents at the PI's request.
