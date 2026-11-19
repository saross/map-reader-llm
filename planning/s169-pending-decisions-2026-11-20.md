# S169: decisions pending for the PI, and actions to take on zbook

> **Last revised**: 2026-11-20 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, Opus lane (`claude-opus-5-5`),
  session S169 on amd-tower, at the session's close. amd-tower is going into
  storage (about 18–24 months), and work resumes on **zbook**.
- **Why**: the S169 overnight run (Wave 1 of the tile-join resolution, with
  Astra's cross-model reviews) ended with a set of decisions only the PI can
  make. This is the durable list, in the order that unblocks work, with the
  main session's recommendation for each. It replaces the walkthrough given
  in conversation on 2026-11-19.
- **Where the work is**:
  - Wave 1 code, tests, reports: branch `tile-join-wave-1` (not merged; the PR
    waits for M1). Records under `reports/tile-join-wave-1/`.
  - Specifications on `main`: `planning/tile-join-wave-1-spec-2026-11-01.md`,
    `planning/tile-join-wave-2-spec-2026-11-19.md`,
    `planning/tile-join-wave-s-spec-2026-11-18.md`.
  - The seam stop: `reports/tile-join-wave-1/stop-2026-11-18-55map-seams.md`
    (§ 5 is current), `reports/tile-join-wave-1/dry-run.md` §§ 2–2.4.
  - The overnight log: `reports/tile-join-wave-1/overnight-log-2026-11-18.md`.
  - The code audit record: `reports/tile-join-wave-1/g1-audit.md`.

## State in one paragraph

Wave 1 stopped at its specification's § 5 on 2026-11-18, on the 55-map sheet
check, and remains stopped. Everything independent of the PI's seam ruling is
done and reviewed. The code passes tier 1 at `d812e1472` (4,779 passed, 0
failed); 99 + 3 mutants are killed; two fresh-context Claude audits and Astra's
reviews are closed (Astra closed R3 at `d812e1472`). E93 and the OSF draft are
accepted as drafts (nothing posted). The Wave 2 and wave S specifications'
technical reviews are closed (design only). Gate G1: items 8 (tests, lint) and 9
(audit) are met; items 1–7 need the W1.5 smoke run, which the stop has paused.
**None of Astra's acceptances is a ruling, a merge, or a launch.**

## 1. The seam ruling (the central decision; it shapes the rest)

**What is established** (stop record § 5; `dry-run.md` §§ 2.2–2.4; the
whole-file padding audit in `reports/tile-join-wave-1/padding-audit/`):

- On the 55-map r2 reference, 34 point–tile contacts from 27 references lie on
  a neighbouring sheet's map content, plus 16 ambiguous contacts. Of the 27,
  25 sit in black padding on their **own labelled sheet**, one is ambiguous
  there, and one (`student:04282`; r50 `student:04296`) has weak map-content
  verdicts on both sheets.
- So these are not established double printings. Each is (2) a wrong sheet
  label, (3) a mound printed on both sheets at different positions (needing a
  centre on its own sheet), or unclear. Pixels at the point cannot separate (2)
  from (3).
- The labels trace to the original 55-map import (`301b51128`), before centre
  marking.
- The whole-file audit of all 5,018 r2 references found 33 in padding on their
  own sheet: 27 are the seam set; **6 are new**, all graded `out_of_scope`
  (`student:02861`/`02862` Radetski, `01823`/`01824` Asenovgrad, `02684`/`02685`
  Radnevo). Whether they enter scoring is not checked.
- Possible pre-existing effect: D50 already matches symbols per sheet, so these
  references may already affect published 55-map symbol-level scores (26
  references exposed on r2). **Not measured**; exposure is not an F1 change.

**Recommendation**:

- Keep the sheet-specific join as ruled (D73 (2)). No seam exception and no
  frame-wide join (option (c) would add 316 padding tiles as positives on r2).
- Treat the seam cases as a **reference correction**: adjudicate the
  references (the 27, the 16 ambiguous contacts, and the 6 new ones if they
  are in scope) using Astra's paired-image index, classify each (label error /
  displaced counterpart needing a centre / genuine second copy / unclear), and
  publish a versioned reference.
- Disclose it **separately** from the join change, with its own timing; it
  will move 55-map F1, precision, and recall by an amount not yet measured
  (E93 states the F1 invariant only for fixed references).
- Rule **before** any 55-map score is computed (Wave 2 spec P3); otherwise the
  ruling is results-informed and E93 must say so.
- Linked: which reference the paper's 55-map claims cite, r2 or canonical r50
  (Wave 2 spec P15).

**Adjudication material**: Astra's index of 40 paired panels with notes,
`~/agent-mail/codex/reviews/seam-paired-views-2026-11-18/visual-review-index.html`.
**This lives in agent mail on amd-tower**; it is preserved in the agent-mail
tarball (see § 9). The panel titles carry the pre-fix classifier labels; the
notes say so. Leads Astra flagged: `student:01876` and `02686` (possible
displaced counterparts), `02069` and `04282`, `01575`, `01822`, `01447`/`01561`.

## 2. Split M1? (Wave 2 spec P2)

The GS frames are clean: all 12 frames, 237 contacts, all on padding
(`dry-run.md` § 2.3). Splitting M1 lets W1.5 smoke the GS cells (1 and 3–8) now,
close G1 for the gold standard, and launch Wave 2's GS phase (about 41 CPU-hours,
about 2.9 h wall-clock at 14 workers or 1.4 h at 30, on zbook); the 55-map cell
2 waits for the seam ruling. **Recommend yes.**

## 3. Confirm three overnight main-session decisions

1. Every in-place re-scoring launcher (`.py` and `.sh`) is pinned to the legacy
   rules (`id`/`id`), so only Wave 2's driver can re-score under the new rules
   (`reports/tile-join-wave-1/consumer-dispositions.md`; Astra agreed).
2. A reference with a missing or blank sheet label is refused by name
   (`tile_join_unattributed_reference`), not silently dropped. No committed
   reference file has one (checked).
3. Branch-only work continued while the wave was stopped, including drafting
   the Wave 2 specification with the seam left open (stop record § 3).

**Recommend confirming all three.**

## 4. Note A (`reports/tile-join-wave-1/withheld-37.md`)

D51's searched-area difference was not treated as an exclusion of the three
withheld Gemini 3.7 cells from the as-evaluated K-ladder families; tier E has
the same difference and stays in. **Recommend confirming.** (Overruling makes
rows 13–18 not eligible.)

## 5. Before Wave 2 launches (`tile-join-wave-2-spec-2026-11-19.md` § 12.1, P1–P15)

Most have sensible defaults. The ones needing judgement, with recommendations:

- **P9**: keep the stop rule strict (first interval or replay-guard failure
  stops; no tolerance). Yes.
- **P12**: apply the D73 (4) eligibility rule to the 46 other withheld files.
  Yes.
- **P10**: 30 workers rather than 14 (memory allows). Yes.
- **P13**: trace the builders of the 79 paper-cited files of unknown
  construction route before Wave 4 interprets the deltas (not needed before
  M2).
- **P1** (unattended mode) and **P4** (merge with Wave 3, after M3): yes.
- **P3** and **P15**: see § 1.

## 6. Before wave S locks its design (`tile-join-wave-s-spec-2026-11-18.md` § 11, Q1–Q12)

- **Q9 (estimator)**: Astra recommends the valid permutation p-value
  `(c+1)/(N+1)` for Wave 3's decisions, withdrawing a significance claim that
  disappears under it. **Recommend accepting.**
- **Q6**: does a primary block of about 6.7 km plausibly match how barrow
  groups cluster in these landscapes? Only the PI can judge.
- **Q7 (timeline)**: the 2026-11-29 target is tight but plausible only if the
  seam ruling and adjudication happen promptly; the remaining compute is Wave 2
  (about 64 CPU-hours projected), Wave 3, and wave S.
- **Q1** (lock before Wave 2 produces any corrected result), **Q10**
  (unstratified bootstrap primary; the sheet-stratified one a sensitivity
  design), **Q11** (10,000 draws): yes.

## 7. Later, not urgent

- The OSF disclosure text: approve the exact text after the final numbers;
  posting needs the PI's approval of that text.
- Whether to fix symbol matching's silent drop of a blank-sheet reference
  (perfect detector with one null `Map` gives F1 0.8889; no committed file has
  one; `g1-audit.md` § 8.3).
- Obs 516 needs rewriting: its "printed on both sides" premise no longer holds.
  Obs 517 and the four how-we-work questions from the S168 handoff still await
  a verdict.

## 8. On zbook, first session (Sunday)

1. `git fetch && git status -sb` in `~/Code/map-reader-llm`; fast-forward
   `main` (the final sync at S169 close should leave it 0 behind).
2. Wave 1 work is on branch `tile-join-wave-1`; zbook has a worktree at
   `~/worktrees/map-reader-llm/claude-tile-join-wave-1` (fast-forward it).
3. Agent mail lives on amd-tower. On zbook there is no `~/agent-mail`; the
   preserved copy is a tarball (§ 9). Decide with the move-infra work where the
   live mailbox goes next.
4. Then take § 1 first; §§ 2–4 are quick confirmations.

## 9. Preservation of amd-tower-only material

- **The repository**: every branch S169 used is pushed to GitHub. A full git
  bundle (all refs, including old local-only agent branches and stashes) is at
  `rpi-server:/mnt/qnap/shawn/Backups/amd-tower-git-bundles-2026-11/Code_map-reader-llm.bundle`,
  refreshed at S169 close. A file-level comparison found no gitignored data
  file that exists only on amd-tower.
- **Agent mail** (`~/agent-mail`, 81 MB, not under version control; Astra's
  review evidence cited by committed documents is under `codex/reviews/`):
  preserved as a read-only tarball at S169 close (location recorded in the
  continuity start-here block).
- **amd-tower disk**: 99 % full. Four finished worktrees are clean, pushed, and
  merged, and could be removed (about 37 GB), which the safety check left to the
  PI; with the machine going into storage this no longer matters for the work.

## Changelog

### 2026-11-20 — Original publication

Written at S169's close from the 2026-11-19 walkthrough, with the whole-file
padding audit result added, before amd-tower goes into storage.
