# Open questions and decisions — the PI's list

> **Last revised**: 2026-10-06 (A.3 ruled and measured; B.8 opened; S162). See
> [§ Changelog](#changelog) for revision history.

Every open question and decision outside the items already handled in
Session 161, grouped as the PI asked: **needs your words now**, **has a
default** (Claude proceeds on the default unless told otherwise), and **can
wait**. Sources: the tracker `planning/text-track-transmission-2026-10-05.md`
(claims C-xx, workstreams Wx), the S160 close block in
`planning/paper-writeup-continuity.md`, and this session's work.

## A. Needs your words now

1. **B-17** (Obs 187, E69, ruling 1a): re-test as-is, re-sweep first, or
   both. Recommended: as-is for the D42 record, re-sweep as a labelled
   sensitivity, annotate the stale summary row and Obs 187, and move "the
   configurations differed" to W2.7.
2. **I4** (`fair-384-vs-512.json`): March sweep or the E39 sweep.
   Recommended: both; March is the D42 record, E39 the figure to cite.
3. **W2.7, configuration-level tests**: option and floor statistic
   (`planning/w27-configuration-level-testing-2026-10-05.md`). Recommended:
   a replicate floor (95th percentile of replicate |ΔF1|) plus rewording,
   a two-level test only where the paper's argument rests on a claim.
   RULED 2026-10-06 (D45-D47); the floors measured and the claims screened
   the same day (`reports/w27-replicate-floors-2026-10-06.md`).
4. **W7.5 / S-9** — see that item's result when it lands (this session).

## B. Has a default (proceeding unless you say otherwise)

1. **W1, the documentation pass**, in the tracker's order (metadata →
   low-level records → intermediate → paper): withdraw or correct C-01,
   C-02, C-03, C-04, C-06, C-07, C-08, C-11 to C-13, C-15, C-16, C-20 to
   C-26; apply D42's re-test to its inventoried sites (C-25); check prose
   that called S-12's four February contrasts null. Paper text is drafted
   for your review, not finalised.
2. **C-05 / "D11"**: the two signed Era-1 boards rank five Phase 2c text
   cells that are one configuration. Default: a D9 signature note on each
   saying so (no tier is driven by a replicate difference), drafted for
   your approval.
3. **"D12" / C-07, C-09**: Experiment E's void claims; C-09's notes are in,
   C-07's withdrawal goes with W1.
4. **H1's permutation caveat**: keep 0.0715 with the caveat in
   `results/family-fdr/family_fdr.md` § 1 (the verdict is null either way).
   The alternative, a test of H1's own null (permuting only within matched
   elaboration pairs), is not planned unless you want it.
5. **C-14a**: correct the null-exemplar script's "sent the labels only" note
   at the script's next run.
6. **W4.3 to W4.5**: Obs 280's label by a new Obs (with W1.4); the
   modality checker resolves its 17 blind verifier stages from the register;
   the register regenerated for C-18's label with the next batch.
7. **W6 prevention**, as engineering tasks: the manipulation check as a
   tested guard (W6.1, design shared with map-reader-bench); an inert
   configuration field as an error (W6.2); a currency guard for generated
   outputs (W6.3, which also covers `grid_analysis.json`'s stale cost block
   from D42's regeneration); the in-batch retries' tier and usage (W6.5).
8. **The register-repair PR**: the branch now carries the register repair
   (D30-D41), D42 and E91. Default: open it as one pull request with a
   section per piece, run a code review, merge on your word. OPENED
   2026-10-06 (S162), with the W2.7 report and the W1 and W4/W6 passes on
   the same branch; merge on the PI's word.

## C. Can wait (your call, not urgent)

1. **W5 follow-up runs** (each needs its own API approval): the list of
   questions believed answered and not (null examples in a text prompt;
   Experiment E's steps at adequate n; a text-with-examples arm; Pro
   thinking), the optional H4 fingerprint replay (about US$0.67), and
   replicate runs W2.7 may call for.
2. **W6.4**: the text prompt's fixed sentence asking the model to match "the
   above Reference Examples": keep for comparability or fix, before any W5
   run.
3. **W7.1** Pro thinking (Pro HIGH metas record 0 thought tokens), **W7.2**
   the image-token budget behind 384 and 512 px costing the same, **W7.3**
   saying where temperature and ordering are evidenced by code only: all
   offline checks.
4. **W8.1 / W8.2**: what left the repository with a wrong description (the
   June colleague summary, any talk or slide, the participatory-GIS article
   if it cites this work; OSF is done, map-reader-bench informed). Claude
   drafts each correction; you send.
5. **C7**: whether the pv-384/512 conditions cite the original legs or the
   `-v2` legs (the `-v2` legs are still upper bounds in the register).
6. **W2.5**: widen the replicate calibration to every significance test the
   paper relies on (bootstrap CIs, the H-family, the K-ladder tests).
7. **Rate-card entries** for 20 archive metas (3 Pro preview, 3.1
   Flash-Lite, Flash-latest, 2.5 Flash): accepted, low priority.
8. **The rest of `~/cc-scratch/bootstrap-cis/`** on sapphire (PV crops,
   results and sweeps, scripts): inventoried in
   `archive/pre-patch-retest-detections-2026-03-21/scratch-inventory.md5`;
   archive more of it only if a re-test needs it.
9. **Reviews never silently discarded**: user observations S150-S160
   (`docs/notes/user-observations.md`); working-notes candidates (a)-(f)
   from S157-S159; the `scripts/bulk-archive.py` infrastructure gate in
   personal-assistant (carried since S158).

## Changelog

### 2026-10-06 — A.3 ruled and measured; B.8 opened (Session 162)

D45-D47 recorded against A.3; the floors are in
`reports/w27-replicate-floors-2026-10-06.md`. The register-repair PR of B.8
was opened the same day.

### 2026-10-05 — Original publication (Session 161)

Compiled for item 5 of the Session 161 brief, after X1, the OSF work, D42 and
the W2.7 note.
