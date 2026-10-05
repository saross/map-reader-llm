# OSF registration update 2 — draft for the PI

> **Last revised**: 2026-10-05 (original publication, Session 161). See
> [§ Changelog](#changelog) for revision history.

**Status: DRAFT, not submitted.** The second update to registration
`osf.io/tybgq` that the PI agreed to in Session 161 (tracker W8.3, erratum
E91). It is public under the PI's name once submitted, so it waits for his
approval of the text. The block below is the proposed "justification" field;
the registration's summary field is left as it is.

---

## Update 2 (2026-10-05): errata E17–E91 and the late deposit of the pre-holdout materials

**Preregistration**: v4.7 (2026-01-31), unchanged. Corrections are recorded
in the errata register, never in the lodged documents.
**Repository**: <https://github.com/saross/map-reader-llm> (public); state at
this update: commit `5a3fb86d8`. This project was made public on 2026-10-05.

### 1. A registered deposit that was not made (erratum E91)

The registration commits to uploading to this project, before any holdout
evaluation, the library manifest, the brief and verbose texts, a mapping
table from hard-example image to text guidance, the final hard-example image
filenames, the selection rationale, the H9 prompt variants V1–V5, the exact
ordering for each condition, and the random seeds (preregistration § 8.4.1,
Step 6; appendix, "Finalisation Documentation"). It was not done. An upload
of five supporting files was attempted on 2026-02-04, alongside the first
update, but the files did not attach: none of them is on OSF.

The materials are now deposited, late, in this project's folder
`late-deposit-2026-10-05/`, each from the git commit that holds it. Holdout
evaluation began on 2026-02-05 at 02:03 UTC. Five of the nine items (library
manifest, brief text, verbose text, hard-example images and filenames,
selection rationale) were public in the repository before then,
byte-identical at commit `5d8c251`, which the first update of this
registration cites by hash, and are unchanged since. The other four were not
fixed before holdout: the mapping table never existed as a file; the H9
variants were finalised on 2026-03-07; the example orderings used in the H4
experiment were settled in code on 2026-02-12, a week after holdout
evaluation began, and no run's output records the order in which examples
were actually sent (the orders are reconstructed from the code at each run's
recorded commit); and of the random seeds, the one for H4's random ordering
took effect only on 2026-02-12, while H9 used a fixed rotation instead of a
seeded draw. `deposit-index.md` in that folder gives each item's status, its
commit, and a permanent GitHub link.

### 2. Errata since the first update

The first update recorded errata E1–E16. The register now holds 75 further
entries (E17–E91): deviations, corrections and clarifications found during
execution and later audits, each with its date, evidence and impact.

- The register:
  <https://github.com/saross/map-reader-llm/blob/main/docs/methodology/preregistration/protocol-errata.md>
- An index from passages of the lodged preregistration to the errata that
  correct them: `preregistration-files/errata-pointers.md` in this project.
- Corrected per-tile mound counts for §§ 2.3–2.5 (erratum E87):
  `preregistration-files/tile-mound-counts-recomputed-2026-09-13.md` and
  `.json` in this project.

### 3. Files

The first update left this registration's list of attached files empty;
this update re-attaches the three lodged documents. They remain in the
registration's archive and in this project's
`preregistration-files/` folder, byte-identical to the repository copies
(SHA-256 checked 2026-10-05).

---

## Points for the PI

1. **Approve or edit the text above.** Your reply is the approval.
2. **Re-attach the lodged documents to the update's file field?** The first
   update left it empty; attaching the three `preregistration-files/`
   documents would restore what the original response listed. Recommended.
3. **Who submits.** Claude can create and submit the update through the OSF
   API after approval, or you paste the text into the OSF interface.

## Changelog

### 2026-10-05 — Original publication (Session 161)

Drafted after the late deposit was uploaded and verified on OSF.
