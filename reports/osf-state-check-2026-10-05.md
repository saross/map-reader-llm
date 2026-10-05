# OSF state check: project h9x4g and registration tybgq

> **Last revised**: 2026-10-05 (original publication, Session 161). See
> [§ Changelog](#changelog) for revision history.

**Status: for the PI's check.** W8.3 of
`planning/text-track-transmission-2026-10-05.md`: investigate the Open
Science Framework (OSF) project before any upload. Read-only: GET requests
to the OSF Application Programming Interface (API) v2 with the project
token, no write. Raw responses are not committed (they are a session
scratch dump); every claim below can be re-checked with the requests named.

## 1. What is on OSF

### 1.1 The project, `osf.io/h9x4g` ("VLM Map Reader")

- **Private** (`public: false`). Created 2025-12-23. No components
  (`/nodes/h9x4g/children/` is empty), no wiki, one storage provider
  (OSF Storage).
- **Storage holds four files**, in `/preregistration-files/`, all uploaded
  2026-01-31 12:50 UTC: `README.md` (1,686 bytes), `preregistration.md`,
  `preregistration-appendix-prompts.md`, `preregistration-coverage.md`.
- The project's description is an older text than the repository's
  `docs/methodology/preregistration/osf/description.md` (it names "Gemini,
  Claude, GPT-4") and ends: "All materials—preregistration, prompts, tile
  selection manifests, analysis code, and results—will be deposited here".

The activity log is complete and short (`/nodes/h9x4g/logs/`, 19 entries).
Every file and registration event:

| UTC | Event |
|---|---|
| 2026-01-31 12:29-12:33 | First upload: the three documents and a README at the root |
| 2026-01-31 12:50 | Folder `updated/` created; the v4.7 set uploaded into it |
| 2026-01-31 12:54 | Registration initiated (embargo) |
| 2026-02-01 09:57 | Embargo approved |
| 2026-02-01 11:01 | The four root files removed; `updated/` renamed `preregistration-files/` |
| 2026-06-30 05:41 | Embargo completed (the registration became public) |

**Nothing has been uploaded to the project since 2026-01-31, and nothing
other than the first-upload set was ever removed.** The files the PI
expected were never uploaded; they were not lost.

### 1.2 The registration, `osf.io/tybgq`

- The project's only registration (`/nodes/h9x4g/registrations/`): an
  Open-Ended Registration, registered 2026-01-31 12:54 UTC, **public**
  since the embargo ended on 2026-06-30. Its description matches
  `description.md`; its summary matches `narrative-summary.md`.
- **Its frozen archive holds both upload sets**: the first upload at the
  root (`preregistration.md` as at commit `97cacba9c`, before the
  2026-01-31 date bump; `preregistration-coverage.md` v2.5, 12,749 bytes;
  a 1,685-byte README) and the v4.7 set under `updated/`.
- **SHA-256 comparison**: the repository's three lodged documents in
  `docs/methodology/preregistration/osf/` are byte-identical to the
  `updated/` set and to the project's `preregistration-files/`. The
  repository `README.md` differs (it gained the corrections section on
  2026-09-13). This agrees with the 2026-07-28 check recorded in
  `protocol-errata.md:1031`.

### 1.3 Updates: exactly one

`/registrations/tybgq/schema_responses/` returns two responses: the
original (2026-01-31) and **one update, submitted 2026-02-04 10:50 UTC and
approved**. Its justification is the Phase 1 errata and decisions document
(E1-E16; Decisions 4, 11-14; the repository copy is
`osf/phase1-errata-and-decisions.md`, identical but for HTML-escaped `>`
signs and one stripped link: the published update reads "**Repository**:
at commit `5d8c251`" with no repository URL).

The update also changed the form's file field (`updated_response_keys:
["uploader"]`): the original response attached five files (the three
documents, the README, and the appendix a second time); **the update's
response attaches none**. The current version of the registration's form
therefore lists no files. The files themselves remain in the frozen
archive. The likeliest cause: the original attachments pointed at project
files that were moved or removed on 2026-02-01, three days before the
update. Worth a look on the registration's page (version history).

No later update exists: errata E17-E90 have never reached OSF.

## 2. What is not on OSF

| Item | Repository | On OSF |
|---|---|---|
| The current README (corrections section) | `osf/README.md` | No (January README only) |
| The errata reverse index | `osf/errata-pointers.md` | No |
| E87 per-tile mound counts | `osf/tile-mound-counts-recomputed-2026-09-13.{md,json}` | No |
| Errata E17-E90 | `protocol-errata.md` | No (E1-E16 only, in the update) |
| The pre-holdout deposit (§ 3) | see § 3 | **No** |

## 3. A registered commitment that was not met (surprise)

The lodged registration commits to an upload before any holdout
evaluation:

- `osf/preregistration.md:1498-1500`: "Before any holdout evaluation,
  upload to OSF: library manifest, brief text, verbose text, mapping table
  (hard example image ↔ corresponding text guidance)."
- `osf/preregistration-appendix-prompts.md:161-167`: "Before any holdout
  evaluation, the following will be uploaded to the connected Open Science
  Framework (OSF) project: final image filenames for all hard examples;
  selection rationale (frequency counts from training evaluation); complete
  H9 prompt variants (V1-V5); exact ordering for each condition; random
  seeds used."

The project log shows no upload after 2026-01-31, so none of this was
deposited before Phase 2 or since. The 2026-02-04 update's justification
covers the selection rationale in prose (Decision 4) but none of the rest.
No erratum records the omission (`protocol-errata.md` has no entry on it;
`execution-plan.md:233-240` and `:802` still list the items unticked).

This bears on the transmission work. The "exact ordering for each
condition" is what W3 had to reconstruct from code at the recorded commit
(S-3: Phase 2e's orderings were in no artefact). A timely deposit would
have fixed the orderings, and the libraries each condition sent, in a
public, dated record.

## 4. The newest preregistration in the repository

`docs/methodology/preregistration/osf/preregistration.md` is the lodged
v4.7 text, byte-identical to OSF; no later version exists in the
repository or its archive. One cosmetic inconsistency in the lodged text:
its "Document version" field reads 4.6 (`:9` and `:2388`) while its own
changelog lists v4.7 (`:2394`) and the README says all documents are at
v4.7. The commit `f037a9d8d` bumped the date but not that field.

## 5. Options for the PI (nothing done yet)

1. **Where corrections go.** The project is private, so a file uploaded to
   its storage is invisible to readers of the public registration. The
   registration's archive is frozen. Two channels reach readers:
   (a) a second registration update (public, dated, versioned; the channel
   the February update used), whose justification can carry the errata
   since E16 or point to them, with files attached; (b) making the project
   public and depositing there (mutable; what the project description
   promises). They are not exclusive.
2. **The § 3 omission** needs an erratum (and a decision whether to
   deposit the registered materials now, late, with the erratum saying so).
3. **The superseded file**: the January `README.md` in
   `preregistration-files/` is the only file the current README
   supersedes; the three lodged documents stay.
4. **The empty form field** (§ 1.3): whether a new update should re-attach
   the lodged documents.

## Changelog

### 2026-10-05 — Original publication (Session 161)

Written for W8.3 before any upload, from read-only OSF API v2 requests:
`/nodes/h9x4g/` (with `children`, `files`, `logs`, `wikis`,
`registrations`) and `/registrations/tybgq/` (with `files`, `logs`,
`schema_responses`), and SHA-256 hashes against the repository.
