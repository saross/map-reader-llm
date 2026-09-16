# Signature policy — what a PI signature means and how it is recorded

> **Last revised**: 2026-09-16 (original publication — the policy, the status
> vocabulary, and the migration of 69 register rows onto it). See
> [§ Changelog](#changelog) for revision history.

This project records which of its findings a human has actually reviewed. That
record is only worth having if "signed" means one thing. Until 2026-09-16 it
did not, and this document fixes the meaning.

## What a signature means

A signature means **all** of the following happened:

1. The Principal Investigator (PI) was shown a **written walkthrough** of the
   row — what it claims, what changed since any prior signature, what was
   independently verified and how, and what the signature does **not** cover.
2. He read it seriously and asked whatever questions he had. (He does push
   back; a walkthrough that produces questions is the system working.)
3. He gave an **explicit affirmative**.

Nothing else is a signature. In particular:

- An **authoring stamp is not a signature.** An agent finishing a row and
  recording that fact is not oversight.
- **Silence is not a signature**, and neither is "carry on", "looks fine", or
  an instruction to proceed with other work.
- **Approval of one row never carries to another**, and approval of a row at
  one revision never carries to a later one.
- **An agent never signs.** The agent prepares the walkthrough and writes the
  record after the PI's affirmative — it does not decide that a row is signed.

## What the agent owes the walkthrough

A walkthrough is not a summary of the row. It must give the PI what he needs
to disagree:

- **The claim**, in the terms of the finding rather than the pipeline.
- **What changed** since the last signature, if there was one.
- **Independent verification.** The agent re-checks the load-bearing numbers
  **from the artefacts**, not from the report of the job that produced them. A
  job asserting its own correctness is not evidence. Say which numbers were
  re-derived and which were taken on trust.
- **Scope limits** — what the signature will not reach.
- **Anything the agent thinks is wrong, weak, or over-stated.** Surfacing a
  concern the PI then over-rules is a good outcome; suppressing it is not.

## How it is recorded

Each row of `results/run-analyses.json` carries a `signature` object, which the
generator copies into the published `results/analyses-manifest.json`. Its
predecessor — a free-text `_signature_note` — never reached the manifest at
all, because every underscore-prefixed key is dropped there, so the only
signature evidence downstream was an ambiguous timestamp.

```json
"signature": {
  "status": "signed",
  "signed_at": "2026-09-16T02:58:00Z",
  "attests": "what was approved, INCLUDING what it does not cover",
  "presentation": "where the walkthrough can be found",
  "history": []
}
```

`manually_verified_at` survives beside it with its original and **only** job:
an authoring stamp that tells the generator not to overwrite hand-authored
fields. It is never a signature and must never be counted as one.

### Status vocabulary

| status | meaning |
|---|---|
| `signed` | The PI approved a walkthrough of the row **as it stands**. |
| `unsigned` | Authored, awaiting that walkthrough. |
| `unsigned-by-design` | Deliberately never signed — calibration material whose claim is carried by a signed sibling. |
| `re-sign-pending` | A prior signature the row has since outgrown. |
| `legacy-signed` | Stamped before 2026-09-16, under the convention where the timestamp *was* the signature, with the row's substance unchanged since. The review happened; its scope was never written down. |

Counting signed rows means counting `status == "signed"`. It never means
counting timestamps, and it never means counting the presence of a note — the
old note field contained the word "UNSIGNED" on three rows, so presence and
meaning pointed opposite ways.

### When a signature lapses

`status` moves to `re-sign-pending` on any change to the row's numbers,
membership, tiering, gates, disclosures, or to what its `attests` asserts. It
does **not** lapse on regeneration stamps, formatting, or changes to files the
`attests` text explicitly excludes. The prior signature is preserved in
`history`; it is never deleted.

### Enforcement

`scripts/generate_post_run_report.py` runs `check_signature_integrity` beside
schema validation, and its errors block the write exactly as a schema
violation does:

- `signed` must carry a `signed_at` **and** a non-empty `attests`.
- `legacy-signed` must carry a `signed_at`, and must **not** carry an
  `attests` — its scope was never recorded, and writing one now would be
  fabrication.
- `unsigned`, `unsigned-by-design` and `re-sign-pending` must not carry a
  `signed_at`.

Every run prints a status tally (`INFO: signature status: ...`) so the count
is never taken by hand. Tier-1 tests in
`tests/test_generate_post_run_report.py` cover each rule.

## The 2026-09-16 migration

69 rows were migrated. 19 carried a signature note (17 real signatures, 2
explicitly unsigned); the other 50 carried a bare timestamp.

Those 50 were split by the question that actually matters — **has the row
moved since it was stamped?** A row untouched since its stamp still has a
signature vouching for exactly the text standing there; what is missing is
only the record of scope. A row whose substance changed afterwards has a
signature vouching for text nobody read.

The split was computed by walking all 103 commits of the register, hashing each
row's substantive fields (signature fields excluded) and comparing **commit
positions**, not dates, so a row whose outcome and stamp were written in one
commit does not read as drift. Result: **25 clean → `legacy-signed`**, **23
drifted → `re-sign-pending`**, and 2 rows to `unsigned` (see below).

Two methodological traps in that walk, recorded because both produced
confident wrong answers first:

- Commit `b64ceae00` published a register carrying conflict markers that does
  not parse. Reading that as "every row absent" stops the walk and reports the
  entire register as having changed at the repair that followed. Unreadable
  snapshots must be **skipped**, never read as absence.
- Comparing a content commit's date against the timestamp *inside* the row
  marks every row whose outcome and stamp were written together as drifted.
  Compare positions in history instead.

`era1-single-pass-baseline-matrix` and `tile-size-sweep` went to `unsigned`
rather than `legacy-signed`: the E88 work of 2026-09-14 amended both in place
precisely because the project judged them never PI-signed, and calling them
legacy-signed would contradict a decision already acted on.

The `re-sign-pending` rows are queued in
`planning/legacy-signature-queue-2026-09-16.md`, grouped by the systematic
pass that moved them — nine conversations, not 23.

## Changelog

### 2026-09-16 — Original publication

Written after the PI asked for signatures to be made unambiguous, following
the discovery that "66 signed" had been arrived at by counting authoring
timestamps. Establishes the meaning above, the `signature` object and its
status vocabulary, the enforcement in the generator, and the migration of all
69 rows. No finding, number or outcome changed: this is a record of oversight,
not of results.
