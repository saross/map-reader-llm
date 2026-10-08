# Discovered, then lost: the no-mound signal in the parent's text arm

> **Last revised**: 2026-10-08 (moved here as the master copy). See [§ Changelog](#changelog) for revision history.

**Provenance.** Written in the map-reader-bench repository (private) as
`reports/2026-10-08-no-mound-signal-history.md`, commit `4d0191c` on branch
`claude/no-mound-history-2026-10-08` (bench pull request #45), and copied here
unchanged apart from this note, the banner and the first changelog entry
(SHA-256 of the source `52210fa7…`). This repository
holds the **master copy**, by the PI's ruling of 2026-10-08: its subject and its
evidence are this project's history, and this repository is public; the bench
links here. **Reading the paths:** "the parent" is this repository, so paths
such as `working-notes.md`, `decisions-log.md` and `prompts/…` are this
repository's; `reports/2026-10-05-d8-*.md` in "Why this exists" and § 6 are the
bench's. Transcript names refer to the session archive (`~/cc-archives/`).

Author: Claude (Opus 5.5), 2026-10-08, at Shawn's request. Research by three Opus agents on
2026-10-06, one per period. Each read keyword windows of annotation-selected session
transcripts in `~/cc-archives/map-reader-llm/` and was free to follow leads. Opus
re-verified the load-bearing anchors against the parent repository and the transcripts
(§ 4). Read-only; zero model calls.

**Why this exists.** Preview provider defaults failed the bench's development gate on false
alarms in cores without mound-family symbols (`reports/2026-10-05-d8-results.md`). Shawn
asked whether a missing "no mounds is fine" signal in text prompts was an error the project
missed, or something it knew about and lived with. He did not want to rely on memory. The
answer matters as a case study: knowledge that was discovered, recorded, and then lost.
**This report informs a later decision about the bench prompt. It decides nothing.**

## 1. The short answer

**Both, in sequence:**

- **The need was found first, on Lesovo,** and solved for images with null tiles and an
  explicit "output nothing" instruction.
- **The text arm never received an equivalent.**
- **That text runs sent no examples at all was known and written down in February 2026.**
  Its implication for false positives on no-mound tiles was never drawn.
- **The knowledge was then lost.** A false conclusion was drawn from an inert manipulation
  in March. The mechanism was partly rediscovered in April, misremembered in September, and
  fully re-established in October.

No transcript shows a deliberate decision to live with text-arm false positives because
consensus voting or the proposer-verifier stage would remove them.

## 2. Timeline

**Anchor marks:** ✓ means Opus re-verified the anchor (§ 4); † means the session was found
outside the annotation triage (§ 3). The other entries rest on the agents' reading.

1. **2025-12-17: the need appears, on Lesovo ✓.**
   - Working note Obs 14 in commit `ae93fc8d5` reads: "To address the False Positive Rate on
     'Sparse' maps (e.g., Lesovo), we identified that the model needs explicit instruction on
     what 'Nothing' looks like."
   - The same commit adds three null tiles with the prompt line "The following images
     confirm what 'NO MOUNDS' looks like. If a tile looks like these, output nothing."
   - Obs 13, in the same notes, records a separate runaway-output problem on blank edge
     tiles, fixed by an information-density check.
2. **2025-12-22 to 23: null tiles kept and rebuilt** (`2025-12-22T03-05_6c7214f9` †).
   - Shawn: "agree that v4.2 SHOULD have null tiles to avoid hallucinations" ✓.
   - The library was rebuilt as a seeded, documented set (commit `a2ad75c98`), with Lesovo
     required.
3. **2025-12-23: text gets look-alike text, not null text** (`2025-12-23T07-25_76a6bf00`).
   - Shawn asked for text-only prompts "with and without negatives".
   - The assistant noted that text-only "has no images, so the *only* way to convey hard
     negative information is through the instruction text itself".
   - The text "hardneg" prompts that followed described look-alike symbols, but no text
     equivalent of the null tiles was written (the agent's reading).
4. **2026-01-07: the text-only negative condition is dropped** (`2026-01-06T22-04_f4cb3541`).
   It was removed from the preregistration during a simplification. Preregistration v4.2
   then tests text-only only at "H5=None".
5. **The parent's text prompt never said an empty answer was acceptable ✓.** Its only
   relevant line refers to examples it never received: "If reference examples are provided,
   compare uncertain cases against them" (`prompts/system-instructions/detect_brief-text.md:22`
   at `2d4631171`).
6. **2026-02-06: a reverse bug, then the fix** (`2026-02-05T08-26_60a2ebc3`).
   - Shawn was surprised that the F1 scores were "so closely clustered".
   - The assistant found that "All 5 conditions are sending the same 17 example images":
     before the fix, text-only runs had sent every listed image. This rests on code reading;
     token counts were not checked.
   - The E25 fix (`4ecaf06d4`, 2026-02-06 ✓) then made text-only send nothing beyond the
     instruction and the tile.
7. **2026-02-10 to 11: known, and written down ✓.**
   - Shawn recalled that the null tiles came in because "without them the model kept looking
     for symbols until its output tokens filled up - we *had to* include some null tiles"
     (`2026-02-10T04-17_c97d0881`). The agent notes this may merge Obs 13 with Obs 14.
   - The Phase 2d text-only configurations record "Text-only modality — examples are
     metadata only, images never sent" (`b0d7dd080`, 2026-02-11 ✓).
   - Decision 17's table reads "(17 ex., none sent)" (`decisions-log.md:873` at
     `4bb549fb` ✓).
   - The assistant said "The examples array in the config is just metadata — nothing from it
     reaches the model", and Shawn replied "Agree" (`2026-02-11T11-55_8572e864` ✓).
   - Phase 2d did test exclusion text in the text-only arm: F1 was 0.660 with minimal text,
     0.602 terse, and 0.548 verbose (`cf59a834` †).
   - **The implication was not drawn:** the text arm had no "no mounds is fine" signal of
     any kind.
8. **2026-03-10: forgotten, and a false finding.**
   - Planning Experiment E, the assistant dropped the null tiles for recall bias: "Null
     tiles teach the model that 'no detections' is acceptable" (`2026-03-10T07-43_2236eeb5` †).
   - Shawn objected: "In the past we've found that removal of nulls … causes serious
     problems… putting the nulls back in to let the model know that 'no mounds is OK'"
     (`2026-03-10T10-51_8b1f6404` ✓).
   - The configuration was text-only, so restoring the nulls changed nothing that was sent.
     The single-run change from F1 0.640 to 0.690 became Obs 156, "Null examples as
     structural constraints" (`working-notes.md:2839` at `4bb549fb` ✓). It is now known to
     be replicate noise (Obs 496).
   - The run metadata read in that session showed `include_example_images: false` beside
     an example count. Nobody remarked on it.
9. **2026-03-14: fixed for the verifier, not the proposer** (`2026-03-14T21-50` †).
   - The same gap was found on the verifier side and fixed by adding text labels.
   - A subagent audit rated the proposer configuration "CORRECT".
   - A run log said "Text-only modality: skipping example images".
10. **2026-04-14: partly rediscovered ✓.**
    - Shawn asked: "if H10 was text-only, what were the 'hard examples'?"
      (`2026-04-13T08-46`).
    - Obs 235 records the answer: the claimed mechanism "was impossible because neither
      library reached the API" (`working-notes.md:9422` and `:9512` at `4bb549fb` ✓).
    - H10 and H12 were retracted, and launch checks were added. The finding was **not**
      carried back to Obs 156, Experiment E, or the text headline.
    - A day later the assistant was still comparing example counts as if the text runs had
      carried 17.
11. **2026-09-14 to 16: misremembered.**
    - Assistants said text cells "transmitted the labels but never the pixels" ✓ (the phrase
      is in `2026-09-14T03-38`).
    - The same was written into a script comment (`48dec436c`).
    - Both are wrong.
12. **2026-10-05: fully established.**
    - In Session 160, a subagent reported that Experiment E's four passes sent exactly 1,672
      input tokens per tile.
    - A manipulation check found that every text-only request sent the instruction and the
      tile only.
    - Obs 496 (`ac42e456a`, `working-notes.md:36873` ✓) and ruling D40 followed. Shawn: "ok,
      this is a major issue, I'm happy you uncovered it now."

## 3. Did the annotations help? (a case study)

The triage selected sessions whose annotations matched keywords (`auto_generated` title,
purpose, and tags, and `three_ps`). Of the sessions that turned out to matter:

| | Sessions |
|---|---|
| **Surfaced by the triage (about 11)** | The Phase 2a modality discovery; Phase 2d setup and its text-arm exchanges; Experiment E; the H10/H12 retraction; the cold-start library; the September null-exemplar sensitivity session; and the October discovery session, which was selected by accident |
| **Missed (7)** | Where the null tiles came from (2025-12-22); both Phase 2d results sessions; the Experiment E plan that dropped the nulls; the March configuration audit; a March track comparison; and the September misdescription |

**Three ways the triage failed:**

1. **"null" is noise.** It matches JSON `null` in every metadata file, and the project also
   uses "null" for null results.
2. **Annotations describe a session's main task, not its side threads.** The null-tile
   origin sat inside a session titled for prompt architecture.
3. **The single most important session had no annotation** ("Auto-metadata unavailable").

**Verdict:** annotations are good pointers to a topic's main episodes, and weak at origins
and turning points. Following leads from annotated sessions recovered the rest.

## 4. What was re-verified, and how

Opus checked these directly on 2026-10-08:

| Claim | Where it was checked |
|---|---|
| Obs 14 text and the null-tile prompt line | `git show ae93fc8d5` |
| The "metadata only, images never sent" notes | `git grep` at `b0d7dd080` (dated 2026-02-11) |
| Decision 17's "(17 ex., none sent)" | `decisions-log.md:873` at `4bb549fb` |
| The headings and lines of Obs 156, Obs 235, and Obs 496 | `4bb549fb` and `ac42e456a` |
| The E25 commit and its date | `4ecaf06d4` |
| The parent text prompt's line 22 | `2d4631171` |
| Four quoted phrases | Present in the named transcripts |

Everything else in § 2 is the agents' reading of transcript windows, reported with
timestamps in their returns. It was not re-read.

## 5. What it bears on, without deciding it

- **The same sheet, the same behaviour.** The bench's preview false alarms (158 of 166 on
  Lesovo) are the problem first named in December 2025.
- **The bench prompt is already ahead of the parent.** It says "If there are no targets,
  return an empty detections array", which the parent's text prompt never said.
- **What the bench text task lacks is the look-alike side,** the role the null and
  hard-negative tiles played for images.
- **Whether a text equivalent helps was never tested.** The parent's own open-items list
  says so: "null examples in a text prompt (never tested)".

## 6. The general lesson

Each loss happened where a fact was recorded at the wrong grain:

- **February:** a configuration note and a decisions-log table recorded the fact, but no
  observation stated its consequence for false positives.
- **April:** a retraction stated the mechanism generally, but applied it to only the two
  hypotheses in front of it.
- **September:** a plausible summary replaced the record.

The countermeasures the bench has since adopted check what is transmitted, not what is
configured: the payload manipulation check and the configuration-field audit
(`reports/2026-10-05-d8-preflight.md` § 3).

## Changelog

### 2026-10-08 — Moved here as the master copy

Copied unchanged from map-reader-bench commit `4d0191c` (bench pull request #45),
with the provenance note above added. The PI ruled the same day that the master
copy sits in this repository and the bench links to it, settling the question
the entry below left open. No figure or claim changed.

### 2026-10-08 — Written

Written from three agent reports of 2026-10-06, with load-bearing anchors re-verified, at
Shawn's request. Shared with the map-reader-llm session as a case study. Where the master
copy sits is to be decided with that session.
