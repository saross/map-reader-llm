# r2 disclosure drafts — step 8 of the recompute chain (for PI review)

> **Last revised**: 2026-09-07 (original publication; drafts, nothing landed).
> Card: `planning/reference-revision-2026-09-06.md` § 4 step 8. Each block
> below is a PROPOSAL for one document the one-commit rule governs; the PI
> edits or approves the text, then it lands in its home with the erratum id
> in the commit message. Numbers are read from the committed artefacts named
> beside them.

## 1. Erratum entry — `docs/methodology/preregistration/protocol-errata.md`

### E84: The 55-map deployment reference changed after the registered analyses ran — revision r2 (−6 / +14 records) re-measures every 55-map figure; no tier moves, no claim reverses

| Field | Value |
|-------|-------|
| Date | 2026-09-07 |
| Type | Correction of the instrument (reference revision); disclosure of re-measurement |
| Commit | `4d92997bd` (step 3), `7894b5b5a` / `cd4905ec3` (step 4), `22353e660` (boards), this entry's commit |
| Files | `inputs/vectors/references/best-available-gt-55maps-r2.geojson` (5,018 records: 4,726 student + 278 extension + 14 audit-reviewed); `results/55maps-r2-ref-2026-09-06/`; `results/55map-final-board-r2-2026-09-06/`; `results/55map-leaderboard/55map_leaderboard_50m_r2.json`; `results/metric-leaderboards/55map-mcc-tiering-r2.json`; the register's `-r2-gt` rows |
| Impact | Low on every number, nil on every claim: max \|ΔF1@50\| over the 23 r1 board cells 0.0009 (band 0.005); the 8-cell leaderboard's five tiers are member-for-member identical; the 23 r1 cells' tier structure is preserved on the 35-cell r2 board. What changes is the reference the paper cites and the board's membership (the 3.7 campaign's cells join). |

**Description**: the standardised reference (ruling 21, E83) was frozen before the
registered 55-map analyses re-ran. Two PI audits then examined it directly: an
empty-tile audit (500 tiles; 5 true double-misses in 470 empty tiles, 1.06 %,
CI 0.35–2.47 %) and a complete census of the 719 clustered mounds (13
edge-safety marks confirmed, 6 GT-error points, 6 model-found omissions, 2
double-misses, 1 vote-gate kill). Their adjudications, applied as a single
deterministic instruction set (`results/reference-revision-r2/audit-revision-instructions.csv`:
6 removals, 14 additions), produce revision r2. One removal overrides a
Ruling-21 "distinct" adjudication on the PI's inspection of the symbol
(`extension:40` and its 10.3 m student neighbour are one mound; r2 keeps the
student record).

**Protocol impact**: every 55-map figure cited by the paper was re-measured
on r2 through the unbroken chain (the IM-k4 scoring template for every
evaluation; the GS tile-swap permutation + BH + greedy-clique tiering for
every board), with the r1 regression gates pinned to r1 and live during the
r2 build (G3: the committed 8-cell board reproduced exactly; G4 and the
family identity, mechanism and geometry gates: all exact). Recall falls by
0.0006–0.0014 on every cell and precision is flat — the signature of a
reference that gained 14 mounds no channel had detected — so no tier moves
among r1 cells and no ranking claim reverses. The r2 board additionally
carries the 3.7 campaign's cells (membership ruling 2026-09-06): its top
tier is `ARM2-N5-oracle` 0.8871 and `ARM2-N3-oracle` 0.8848, above the r1
leader `B-N10-oracle` (0.8560, now T4).

**What the revision does not fix**: the estimated-correction column
(`results/55map-final-board-r2-2026-09-06/estimated-correction.json`)
carries the error the audits did NOT see — expected unseen double-misses
M ≈ 50, GT errors E_err ≈ 36 and model-found omissions E_om ≈ 36 outside the
audited clusters — as P̂ / R̂ / F1̂ with Monte Carlo intervals beside every r2
point estimate (F1̂ 0.0005–0.0007 below the point, ±0.005), never as a
re-tiering.

**Correction**: the paper's 55-map figures cite the `-r2-gt` conditions and
the r2 boards; the `-standardised-gt` rows and r1 boards remain in the
register as the record of what the registered analyses measured.

## 2. Methods — `docs/paper/methods-draft.md` § M.3, an added paragraph

After the ruling-21 paragraph:

> Two targeted audits then examined the standardised reference directly. A
> 500-tile empty-tile audit (tiles no channel had marked) found five mounds
> missed by both students and every model — 1.06 % of the 470 empty tiles
> reviewed (95 % CI 0.35–2.47 %), extrapolating to ≈ 50 unseen mounds across
> the 4,676-tile empty frame — and a complete census of the 719 mounds in
> clusters found six reference points that are not mounds, six model-found
> mounds the reference lacked, and two further double-misses. Applied as a
> single deterministic instruction set, the adjudications remove six records
> and add fourteen, giving revision r2 (5,018 records: 4,726 student, 278
> extension, 14 audit-reviewed, all at marked centres). Every 55-map figure in
> this paper is measured against r2; re-measurement moved no cell's F1 by
> more than 0.0009 and changed no tier among the previously reported cells.
> Because the audits sample the reference rather than exhaust it, we also
> report an estimated correction for the error they did not see (§ R7),
> propagated from the audit rates by Monte Carlo and shown beside — never in
> place of — each point estimate.

## 3. Discussion — `docs/paper/discussion-outline.md` D.8, one bullet

> - **Reference error that no audit saw.** r2 removes the error two PI
>   audits found; the estimated-correction column carries what they did not
>   (≈ 50 unseen double-misses in the empty frame, ≈ 36 GT errors and ≈ 36
>   model-found omissions outside the audited clusters, each with a
>   Clopper–Pearson interval). Two assumptions are stated with it: the
>   cluster census's error rates are extrapolated to the 4,291 non-clustered,
>   non-audited points, where errors may be rarer (reviewed less hard) or
>   commoner (duplicates concentrate in clusters, Obs 396); and the correction
>   is corpus-level and uniform, so it widens every interval by ≈ ±0.005 and
>   cannot re-order a board — which is why it is a column, not a re-tiering.

## 4. Working-notes observation (for `/observe`, obs-writer)

**Obs 45x — Reference revision r2: a −6 / +14 change set moved no tier and
every recall.** Re-measuring all 55-map figures on r2 (two audits' adjudications
applied deterministically) moved F1@50 by at most 0.0009 on 23 board cells,
always through recall (−0.0006 to −0.0014) with precision flat — the
signature of adding mounds no channel had detected — and preserved every tier
structure. The reference's *residual* error is the larger uncertainty: the
estimated-correction column (M ≈ 50, E_err ≈ E_om ≈ 36) widens every interval
by ≈ ±0.005, wider than the tier gaps. Two findings the board now carries
that are not confirmations: the all-3.7 stack's N = 3 oracle sits in T1 with
its N = 5 oracle (the Obs 438 "saturates at N = 3" pattern repeats for the
3.7 proposer at 60 % of the pass spend), and the fourth cell's N = 3 oracle
(0.8747) is level with its own N = 10 carried point (0.8728). Both are oracle
claims. Method notes for the record: the sweep's oracle argmax landed on the
same operating point on r2 for all 13 r1 families; the companion B N = 5 set,
re-materialised from pass-pinned inputs, reproduced the ladder's canonical
F1 to the last digit; the whole chain ran on one engine at $0.

## 5. The § R7 table — `docs/paper/results-draft.md`

Not drafted here: the table rewrite is the one-commit rule's own item (results
`.md` + changelog entry together, erratum id in the message) and depends on
the PI's presentation ruling on the older 55-map strata. The numbers it needs
are in `results/55map-final-board-r2-2026-09-06/final-board-50m.md` (the
35-cell board with cost, group letters and the runs table) and
`estimated-correction.md` (the column).
