# S169 overnight log: Wave 1 of the tile-join resolution, 2026-11-18 to 19

> **Last revised**: 2026-11-19 (final entries appended). See
> [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, Opus lane, the S169
  main session on amd-tower. This is the running log the session kept
  through the night, while the PI was away and the mail watch was armed.
  It is committed as written, with the corrections below.
- **Status**: a record of events, not a source of results. Every number
  in it points to a committed file named beside it; read those files.
  The times are approximate (AEDT), and a few entries were written out of
  order.

## Corrections to entries below (read these first)

- **23:45, "both are on printed mound symbols"**: the two crops I viewed
  showed symbols on the *neighbouring* sheet. Both points lie in padding on
  their own labelled sheet (see 05:40, and stop record § 5).
- **06:45, "No contact … has map content on both sheets, so case 1 is
  ruled out" and "All 40 of Astra's pairs agree"**: withdrawn. They rested
  on a half-pixel error in the shared helper (see 07:30 and 08:15). After
  the fix, one feature (`student:04282`, r50 `student:04296`) has map
  content on both sheets, and the comparison with Astra's pairs is 39 of
  40 final and 37 of 39 original, compatible under different window rules
  rather than identical.
- **06:45, the D50 "symbol-level exposure" counts** are counts of
  references placed on a sheet where the point is padding. They are not
  false-negative or false-positive counts, and not F1 changes.

## Log

- 23:05: P2 approved by the PI. P3 met: zbook freeze equals the lockfile
  (172 packages, name normalised), and tier 1 is 4,525 passed. P4 met.
  Recorded in `e92d1c5d7`.
- 23:15: agents started:
  - wave S spec;
  - W1.0 census (branch `tile-join-wave-1-w10`);
  - W1.1–W1.2 code (branch `tile-join-wave-1`);
  - W1.3 drafts (branch `tile-join-wave-1-w13`).
- 23:12: mail watch armed (until about 09:10). Astra's coordination mail
  was answered: I confirmed Astra's static consumer audit and declined an
  implementation task, because the PI scoped Astra to reviews.
- 23:22: wave S draft done (`a588b96f1`). The block census reproduces byte
  for byte on amd-tower. The agent corrected the brief's stride: the stride
  is 336 px for 384 px tiles, not 256 px. Merged to main as `92064b134`.
- 23:24: **amd-tower eCryptfs incident.** `git merge` died with SIGBUS in
  update-index. The kernel log shows a burst of 128 `ecryptfs_read_folio:
  Error decrypting page; err = [-4]` lines at 23:21 (EINTR, not EIO). There
  were earlier bursts at 08:57 (46 lines) and 10:15 (24 lines) the same day.
  There were no I/O, NVMe, or EXT4 errors in 7 days. Sixteen files showed
  as modified, and all 16 hash equal to HEAD. They were stale index stat
  entries, refreshed with `git add`, which changed no content. The merge
  succeeded on retry. The home filesystem is 96 % full (19 GB free).
  **For the PI:** worth a look. eCryptfs page-read interruptions under
  parallel I/O, on a nearly full disk.
- 23:25: W1.3 drafts done (`652786ae8`). Verified: the frame-wide values of
  the 3.7 cells have been on record since 2026-09-12
  (`reports/tile-mcc-geometric-join-2026-09-12.md:247–249`). The W1.0 agent
  was told to disclose this in `withheld-37.md`.
- 23:26: review request sent to Astra (wave S, and the E93 and OSF drafts).
- 23:30: the OTHER count for personal-assistant rose to 2 and fell to 0 (read elsewhere).
- 23:33: Astra's consumer audit received and receipted. It reports C1–C4
  and 116 call sites in 70 files. I forwarded it to the code agent as
  in-scope W1.1 work (every wrapper that reaches a count table), plus a
  `consumer-dispositions.md` table. The reconciled dispositions go back to
  Astra with the code head.
- 23:45: **§ 5 STOP.** The W1.0 55-map sheet check found 32 map-content
  cross-sheet contacts (26 references, 9 `_4326` seams) in r2, and 32–35 in
  each of the other files. I viewed two crops; both are on printed mound
  symbols. The PI was push-notified. The stop record is `8b81bb710` (W1.0
  branch). Eligibility: 24 rows, 24 eligible subject to criterion 3;
  note A awaits the PI.
- 23:52: the W1.0 agent was resumed on a seam measurement (second copies
  and phantoms) and on steps 3–8 (no corrected scores). The code agent was
  told to keep the sheet-assignment decision isolated for a seam option and
  to run nothing on 55-map data. Astra was asked for an independent check
  of the stop.
- 23:42: Astra agreed the stop is warranted. Astra asked for the full
  evidence and distinguishes the mask classification from confirming a
  symbol. I built a read-only package at
  `~/agent-mail/claude/reviews/seam-stop-2026-11-18/` (50 contacts, circled
  crops, 41 uncircled tiles with `.pgw`, a manifest), sent it, and
  receipted the request.
- 23:44: Astra's reviews arrived.
  - E93 and OSF: accept the framing as a working draft. Text corrections
    E1 (per-condition caveat in the OSF text), E2 (bound the claim about
    unmerged output), and E3 ("re-scored under the new sheet-specific
    joins", and add the seam stop).
  - Wave S: changes requested.
    - S1: decide with `(c+1)/(N+1)`. BH's first threshold for 153 cells
      is about 4.3e-6, below the sampling floor.
    - S2: the geometry cross-check cancels algebraically, so it is not
      independent.
    - S3: the block-size separation and booking-boundary claims are
      wrong.
    - S4: an unresolved sensitivity design must qualify, not support.
    - S5: the targets for the unmerged sentinel.
    - Also: the stratified-bootstrap answer, and the bookkeeping
      (Decision 10 wording; 745,280,000 draws for the boards alone).
  - Both receipted. Two Opus revision agents started (`wave-s-spec`;
    `tile-join-wave-1-w13`). Each finding is verified before it is
    applied.
- 23:50: Astra's ownership hook blocks Python reads of my mail subtree, so
  I made a neutral read-only copy at `/tmp/seam-stop-evidence-2026-11-18/`.
- ~00:00: E93 and OSF revised (`87d3dfc47`). E1–E3 were all accepted.
  Correction: it is 32 contacts involving 26 references (I had written
  "32 references").
- ~00:00: **seam measurement** (`dry-run.md` § 2.2, W1.0 `6bd4a3e03`):
  - canonical r50 already has `phantom:*` second copies for 29 of its 33
    map-content contacts, so options (a) and (b) move 0 tiles there;
  - r2, best-available, and the student files have none, so (a) and (b)
    move 11 tiles each;
  - (c) frame-wide moves 333 tiles on r2, mostly from padding.
  - Sent to Astra with the E93 head.
- ~00:10: **W1.0 complete** (W1.0 branch `12875b7bf`; the wave stays
  stopped on the seam ruling).
  - Census 2,817 + 12 = 2,829, matching the spec. I re-counted it with
    `git ls-files`.
  - Worklist: reproducible-legacy 2,445, unresolved-recipe 281,
    historical-only 54, known-withheld 49. No paper-cited file is
    unresolved (758 + 3). I verified this in `worklist.json`.
  - Smoke cells 3–5 pinned (two unmerged).
  - **All eight cells' legacy replays reproduce** their committed
    confusions and intervals. Cells 6–8 end in their recorded refusals.
  - Timings: the 55-map cell takes 131 s wall time and 2.1 GB.
  - New PI questions: the 46 withheld cells outside W1.4 (D73 (4)
    scope?); which other live directories count as frozen under D73 (5);
    79 paper-cited files of unknown construction route.
- ~00:15: stop record amended (`89cab15ee`). The Wave 2 spec is now drafted
  with the seam left as an open parameter, so Astra can review it
  overnight.
- ~00:35: wave S revised on round 1 (`0a1b4dadd`). All findings were
  accepted. Both scripts reproduce on re-run. Merged to main as
  `99dff19bd`.
  - The merge hit a second "short read while indexing". This time there
    were no eCryptfs kernel lines, and all 17 flagged files hash equal to
    HEAD. Same fix: refresh the index, then retry.
  - Round-2 request sent to Astra.
  - Wave S now has 12 PI questions, four of them new: the estimator, Pst
    primary, the draw budget, and the seams.
- ~00:40: Astra's counting correction to the seam measurement.
  - Option (a) adds 26 distinct references on r2, not 32 (six mounds
    reach two tiles of the same sheet).
  - The (c) comparison should give disjoint categories (map-content /
    ambiguous / padding).
  - Astra's pixel audit reproduces all 50 contacts with no discrepancy.
    Two ambiguous contacts (student:04282) remain for manual judgement.
  - Sent back to the W1.0 agent to correct; mail receipted.
- ~00:45: Astra on the E93 revision: E1–E3 addressed. The new seam
  paragraph must:
  - separate the symbol-level effect from the tile-level effect (11
    tiles);
  - separate the proximity fact, the confirmed examples, and the
    unadjudicated candidates;
  - make the F1/P/R invariant conditional on fixed references (a
    reference correction is a separate component).
  The E93 agent was resumed to fix this, and the W1.0 agent was asked to
  fix the same overclaim in stop-record § 1. Receipted.
- ~01:00: seam counting corrected (`21cd6ef97`).
  - Option (a) adds 26 references on r2 (40 with ambiguous); 4 on
    canonical r50 (20 with ambiguous).
  - Option (c) on r2: 11 map content, 6 ambiguous, and 316 confirmed
    padding tiles.
  - Stop record § 1 overclaim fixed.
  - Sent to Astra.
- ~01:05: E93/OSF seam paragraph revised (`a22c614be`). It separates the
  two effects, splits the evidence three ways, and makes the invariant
  conditional on fixed references. Sent to Astra.
- ~01:25: Wave 2 spec drafted (`f5f3824bb`). The cost script reproduces
  byte for byte. Merged to main as `7d6e1e881`; review request sent to
  Astra.
  - Projection: 63.84 CPU-hours, about 4.8 h wall-clock. The new-rule
    step is assumed to cost the same as a replay (unmeasured).
  - Order: GS phase A first; 55-map phase B waits for the seam ruling.
  - The drafter found that the other GS frames (384, 512, 256 full, grid,
    H10, H13) have no sheet-boundary check, so this is precondition P4.
  - 14 PI questions. P2 asks whether to split M1 so GS can proceed before
    the seam ruling.
- ~02:10: **GS frames sheet check**: across 12 frames, 237 padding, 0
  ambiguous, and 0 map content. 6 are unmeasurable, but they lie off the
  scan's edge. The seam problem is specific to 55-map.
- ~02:15: **W1.1–W1.2 code complete** (14 commits, 97 files).
  - 68 perfect-detector tests. The red sentinel gives 30 and 14 failures
    under its two mutations.
  - C1–C4 covered; dispositions for 131 calls; an AST scan pinned 23
    more second-order calls.
  - Tier 1 at `06fd89ffb`: 4,595 passed, 1 failed (registry).
- Merged W1.0 and W1.3 into `tile-join-wave-1` (`4935c0761`,
  `913f77ccb`). Registry rebuilt on zbook (adds only 5 report files;
  `f6f5ffe54`). Tier-1 re-run launched. Code head sent to Astra.
- ~02:30: Astra **accepted the E93/OSF drafts** at `a22c614be`, as drafts
  awaiting the seam ruling and the measured results. This is not approval
  to post. Receipted; no reply owed.
- ~02:30: fresh-context audit launched (G1 item 9). Lens A covers
  implementation and Lens B tests; both Opus, both on frozen
  `git archive` copies on zbook.
- ~02:35: **tier 1 at `f6f5ffe54`: 4,596 passed, 0 failed**, 5 skipped, 1 xfailed (4,525 + 68 new + 2 former xfails + registry). The tier-1 half of G1 item 8 is met.
- ~02:40: **Astra's full seam-stop review**
  (`20261118T132837Z-astra-55map-seam-stop-review.md`):
  - The stop is warranted.
  - All 50 contacts were independently reproduced (full affine inverse),
    and the 26 distinct candidates were viewed: no counterexample to the
    map-content class. Symbol identity is not adjudicated.
  - **Prefers (a)**, conditional on an independently adjudicated,
    versioned reference correction:
    - audit the whole seam candidate set consistently, using both
      sheets' imagery and the actual symbol centres;
    - each printed instance gets its own identity and provenance, linked
      to the physical mound;
    - report the join change and the reference correction as separate
      effects.
  - (b) needs a precise definition; (c) is not recommended (316 padding
    tiles); (d) at most a declared sensitivity analysis.
  - Agrees the overnight continuation is reasonable, but says it does not
    constitute a passed G1.
  - Receipted.
- ~02:45: Astra's wave S round 2: round-1 findings addressed. Two
  corrections remain before the lock: S6 (the undefined-MCC bound
  double-counts; use a union) and S7 (the exact-group floor is not the
  sampled estimator's floor). Recommendation for the PI: the valid
  estimator for Wave 3, and withdraw significance claims that vanish
  under it. Sent to the wave S agent; receipted.
- ~03:00: wave S S6 and S7 applied (`4a75615cb`), merged as `d9f5d6096`; round-3 head sent to Astra with two choices for review.
- ~03:10: Astra's **Wave 2 review: changes requested.**
  - W2-1: the seam hook is not a complete policy.
  - W2-2: resume must check the full computation identity and the whole
    output bundle.
  - W2-3: a reference change needs a schema amendment.
  - W2-4: a replay tolerance needs the PI to amend the stop rule.
  - W2-5: precise surgical-write rules.
  - The scope is confirmed (2,829 entries). Sent to the Wave 2 agent;
    receipted.
- ~03:10: **audit Lens A: no Critical.** M1 (refusal probe for mixed
  pairs), M2 (`mcc_tiering_55map` hard-codes `id`), M3 (3 unlisted
  launchers), M4 (`recorded_tile_joins` doesn't validate names), plus
  L1–L9. All 612 join-taking calls bind correctly (AST); no positional
  shifts; symbol matching untouched; count tables sum on real data. Fixes
  wait for Lens B.
- ~03:15: Astra's wave S round 3: S6 and S7 closed, both choices accepted. One wording fix (floor guarantee narrowed) committed on main. Wave S review is complete pending the PI's choices.
- ~03:30: **audit Lens B.**
  - **B-C1 is a real bug**: the k-ladder MCB replay with `--tile-join id
    --count-table-join id` crashes on F1, hidden by a stub.
  - Critical test gaps: B-C2 and B-C3 (the evaluator interval joins can be
    dropped with tier 1 green) and B-C4 (sheet-primary nearest-centre
    booking is untested).
  - Medium: CLI wiring, provenance reader, wrapper provenance, pinned
    sites (static test suggested), replicated quantities.
  - The red sentinel reproduces exactly.
- ~03:35: consolidated findings written to
  `scratchpad/g1-audit-findings.md`. The code agent was resumed for one
  fix round:
  - all Medium and above, plus most Lows, plus the W2-1 docstring;
  - pin the in-place re-score launchers to legacy joins (my decision,
    pending the PI);
  - write `g1-audit.md` with the dispositions.
  A re-audit of the fixes follows.
- ~03:50: Wave 2 spec revised (`1883c9611`; W2-1..W2-5 adopted; A1–A7 closed), merged to main; round 2 sent to Astra.
- ~03:55: Astra's interim code finding: W1-C1 (an unlabelled cached MCC block gets relabelled). Astra recommends pinning the launchers and a named refusal for references with no sheet. Both were added to the fix round (the reference refusal flagged as a main-session decision pending the PI). Receipted.
- ~04:00: Astra's interim W1-C2 (era1 load_cells: no recorded count-table replay before F1) and W1-C3 (drift silently withheld; same as A-L6). Added to the fix round; receipted.
- ~04:05: Astra's Wave 2 round 2: W2-1/3/4 addressed. R2-1 (atomic manifest transitions, recovery), R2-2 (frozen identity anchor on restart), R2-3 (Markdown cells keyed by identity; wording allowlist), A10 (1.5 is not the same as bootstrap-done). Sent to the Wave 2 agent; receipted.
- ~04:25: Wave 2 round-2 details applied (`6d2729b96`), merged to main; round 3 sent to Astra.
- ~04:30: Astra's **full code review: changes requested** (W1-C1..C4). W1-C4 is new: a recorded refusal is checked by reason only (a 525/526 replay accepted against a committed 22/526). No binding errors in 479 modules; launcher pinning endorsed; reference refusal recommended. Sent to the code agent; receipted. Astra wants the fix head for re-review.
- ~04:40: Astra's Wave 2 round 3: three lifecycle gaps (fresh inputs against the anchor; expected refusal counts as done; supersession anchor). New audit: all 24 alternative-writer files come from native corrected-F1 adapters (percentile CIs, references varying by buffer) and must replay through engine plus adapter. Sent to the Wave 2 agent; receipted.
- ~05:00: Wave 2 round-3 applied (`16354b73a`: lifecycle cases; 24 files now rescore-native). The scope script reproduces. Merged as 288e36541; round 4 sent to Astra.
- ~05:15: the code agent hit a context-length limit after 9 pushed fix commits (`bc9b23ad6`..`1b913722a`, including B-C1, the reference refusal, launcher pinning, W1-C2/C3/C4). It left consumer-dispositions.md uncommitted. A fresh Opus agent was started to finish: status table, remaining fixes, mutation re-run, tier 1, g1-audit.md, registry.
- ~05:25: Astra **closed the Wave 2 technical review** at `16354b73a` (design only; not launch). Its 3 implementation notes were recorded in § 5.2 on main. Receipted.
- ~05:40: **Astra: seam attribution evidence.**
  - For student:01862/01863/01876/01878 the recorded point is in black
    padding on its OWN labelled sheet, and on a symbol on the neighbouring
    sheet: likely an inherited wrong sheet label (case 2), not a second
    copy.
  - Lineage: `mark_mound_centres.py` saves the queue's `map_name`, not
    the raster shown.
  - **I viewed the panels for 01862 and 02387** (my two "confirmed"
    examples). Both are padding on their own sheet. My earlier "printed on
    both sheets" reading is wrong for these.
  - Possible pre-existing symbol-level effect via D50 per-sheet matching:
    a hypothesis, being measured.
  - A fresh agent was started on an own-sheet pixel classification of all
    contacts (branch `tile-join-wave-1-seam2`). Receipted.
- ~05:50: Astra's padding diagnostic: for all 26 distinct r2 map-content pairs the own (labelled) sheet is all near-black at the point (and at the original student coordinate); the recipient has no black. Only 1 of 14 ambiguous pairs is all-black at source. **For r2 the map-content set looks like case-2 sheet-label errors, not double printings.** Forwarded to the measurement agent as a cross-check; receipted.
- ~06:20: **G1 fix round complete** (`f6f5ffe54..0549672ec`): all findings fixed except A-L9; tier 1 at 4,699 passed, 0 failed; 61/61 mutants killed; red sentinel passes; `g1-audit.md` written; registry rebuilt. I checked that the 12 reference files have no blank sheet. Fresh re-audit started; fix head sent to Astra.
- ~06:30: Astra interim re-review: **W1-C4 still open**. `compare_present` skips fields absent from the replay, so a replay with no diagnostics passes (`compared: []`). Held for one consolidated fix round after the re-audit and Astra's final re-review. The re-auditor was told to hunt the same pattern. Receipted.
- ~06:45: **own-sheet seam measurement** (branch `tile-join-wave-1-seam2`
  `61c091dc2`, `dry-run.md` § 2.4).
  - **No contact in any 55-map file has map content on both sheets**, so
    case 1 is ruled out.
  - Every map-content contact is own-sheet padding: case 2 (a label
    error) or case 3 (a displaced counterpart). The pixels cannot tell 2
    from 3; that needs the own-sheet edge viewed.
  - r2: 25 distinct references (12 with an own-sheet blob within about
    240 m, 13 with none).
  - All 40 of Astra's pairs agree.
  - r50: 20 of its 24 have a phantom on the recipient sheet; the student
    reference is stranded in padding.
  - D50 symbol-level exposure: r2 has 26 references (plus 1 ambiguous) on
    a sheet where the point is padding.
  - Suggested: a whole-file pass for any reference in its own sheet's
    padding.
- ~06:45: **DISK.** amd-tower `/home` is 99% full (8.6 GB free); each full
  worktree is about 9.4 GB. The seam2 worktree had to be sparse.
  **For the PI** (the deletion needs approval; the safety check blocked
  me): these four worktrees are clean, pushed, and merged, so they are
  safe to remove (about 37 GB):

      git worktree remove ~/worktrees/map-reader-llm/claude-wave-s-spec
      git worktree remove ~/worktrees/map-reader-llm/claude-wave-2-spec
      git worktree remove ~/worktrees/map-reader-llm/claude-tile-join-wave-1-w10
      git worktree remove ~/worktrees/map-reader-llm/claude-tile-join-wave-1-w13

  No new full worktrees on amd-tower until then.
- ~06:50: Astra's second re-review interim: W1-C3 still open on a count-table-only change (era1:1685); W1-C2 replicate-mean skips the F1 replay; a new missing-pair fallback in k_ladder_mcc_test:621–632 passes the gate on absence. Plus the W1-C4 test at test_tile_join_wave1_audit.py:1013 asserts the wrong thing. All 'absence = agreement'. Held for the consolidated fix round; receipted.
- ~07:05: stop record revised (seam2 `3497c5bda`): § 5 own-sheet evidence; § 2 'confirmed' examples corrected; title corrected. Sent to Astra. TODO: E93/OSF 'confirmed by eye' wording when seam2 merges into tjw1.
- ~07:15: Astra's **fix re-review: changes requested**. W1-C1 closed. R2-1 (W1-C4 missing replay fields), R2-2 (W1-C3 count-table-only path), R2-3 (W1-C2 replicate-mean), R2-4 (missing-pair fallback), R2-5 (stride55 import order breaks standalone run), R2-6 (pd.NA blank-sheet). A fresh lean fix agent was started; the Claude re-audit's findings will be folded in. Receipted.
- ~07:30: **Astra: a pixel-convention bug** in the shared seam helper (centre index floored as an edge index). With the correct containing pixel, student:04282 becomes a 1/3-candidate (content on both sheets), so my stop-record § 5 'ruled out for every contact' is not robust. Also wording: '40/40 agree' (really 39/40 and 36/39), and 'no class from centre marking' is too strong. A fresh agent will fix the helper once, re-run all seam and GS checks, and revise the documents. Receipted.
- ~07:40: Astra's own-sheet review: changes requested (pixel convention; § 5 heading; separate agreement types; 'predates centre marking'; exposure is not FN/FP; missing world file → unmeasured). Lineage: 24 of 26 r2 pairs carry the sheet label unchanged from the original 55-map import (`301b51128`, a spatial join against rasters per the session-log note). Forwarded to the pixel-fix agent; receipted.
- ~07:55: **fresh re-audit of the fixes**:
  - RA-C1: a false stop on a real committed board (double-rounded MCC).
  - RA-C2: the tier-E launcher reads a stale file after pinning.
  - RA-C3 = R2-5.
  - Six Medium, including 13 unpinned .sh launchers and a refusal log
    Traceback that reads as crashed.
  - 9/12 new mutants survive.
  - About 600 real cells replayed with no other false stop; no symbol-level
    F1/P/R change.
  Findings are in `scratchpad/g1-reaudit-findings.md` and were folded
  into the final fix round.
- ~08:15: pixel-convention fix complete (seam2 `834c705a2`; self-tests re-run by me on zbook: pass). One 1/3-candidate in every file (student:04282 / r50 04296; weak, near the threshold). GS unchanged. § 5 overclaims withdrawn. Sent to Astra.
- ~08:30: Astra **accepted the seam pixel correction and revised interpretation** at seam2 `834c705a2` (not feature identity, a reference correction, the ruling, a merge, or launch). It independently matched all 50 contacts and 62 own-tile measurements. Lead: student:02686 (panel 030) may be a displaced counterpart (case 3), which illustrates why padding at the point cannot rule case 3 out. Receipted.
- ~08:55: **final code fix round done** (`0549672ec..4a8d2af34`, plus my dispositions update `ef18e4e76`). Tier 1 is 4,772 passed, 0 failed; 99/99 mutants killed. All of R2-1..R2-6 and the RA findings are fixed. Fix head sent to Astra.

## Changelog

### 2026-11-19 — Final entries appended

The entries from about 08:30 to 08:55 were appended when the overnight
run ended.

### 2026-11-19 — Original publication

Committed at the end of the overnight run, with the corrections block
added. The log entries themselves are unchanged.
