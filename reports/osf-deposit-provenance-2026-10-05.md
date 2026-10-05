# Pre-holdout deposit: provenance in the public repository

> **Last revised**: 2026-10-05 (original publication, Session 161). See
> [§ Changelog](#changelog) for revision history.

Prepared 2026-10-05 for the PI's erratum and late deposit. This was read-only research
on `/home/shawn/Code/map-reader-llm`, using git, grep, and file reads; no API (OSF,
Gemini, GitHub) was called. Every hash, date, path, and line number below comes from a
command in § 4. Dates are given as git records them (author date, local offset) with
UTC where it matters. "Holdout" here means the Era-1 60-tile set named `validation` in
the codebase (erratum E20 renamed "holdout" to "validation").

## Summary

The registration commits to depositing nine items on the Open Science Framework (OSF)
before any holdout evaluation: four at `osf/preregistration.md:1498-1500` and five at
`osf/preregistration-appendix-prompts.md:159-167`. The task brief counts eight. None was
deposited. The first holdout API call was at **2026-02-05 02:03:57 UTC**, about 20 seconds
after commit `c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3` (02:03:37 UTC).

**Five items existed in executed form before that call and are unchanged since:**

- the library images, with their filenames;
- the library manifest (functional equivalent);
- the brief text;
- the verbose text;
- the selection rationale with frequency counts.

They are also byte-identical in commit `5d8c251b9824ae9b3f3f3cf3d90496978578a085`
(2026-02-04 09:58 AEDT). That commit is cited by hash in the OSF registration update
submitted 2026-02-04 10:50 UTC, so it is the one externally timestamped anchor (§ 3.1).
The run metadata's prompt hashes equal the SHA-256 of the committed texts.

**Four items fall short:**

- **Mapping table.** It never existed as a file. A partial pre-holdout mapping exists
  (seven of eight hard examples).
- **H9 variants V1-V5.** They did not exist until 2026-03-07, 30 days after holdout
  began. The lodged design builds them from the winning holdout configuration, so they
  could not have preceded holdout evaluation.
- **Exact ordering.** At holdout start it existed only as config-file order plus code
  whose "canonical-first" did nothing. The executed H4 definitions date from 2026-02-12.
  No run records the order actually sent.
- **Random seeds.** They are mixed:
  - The tile-selection, null-tile, and execution-order seeds were fixed before holdout.
  - The H4 random-order seed base (42) was in the study YAML but was not wired to the
    detector until 2026-02-12.
  - H9 used no seed at all: a hand-written rotation replaced the registered seeded
    sampling.

---

## 1. Holdout start(s), with evidence

### 1.1 First holdout evaluation: Phase 2a, 2026-02-05

| Evidence | Value |
|---|---|
| Commit in force | `c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3`, 2026-02-05T13:03:37+11:00 (02:03:37 UTC), "feat(scripts): Add run_phase2.py OFAT runner, archive run_study.py (D15)" |
| First holdout API call (session archive, private) | 2026-02-05T02:03:57.063Z: `run_phase2.py studies/phase2a-h1-modality.yaml --condition image-only --runs 1 --limit 1`, which returned "Status: OK". Then 02:05:05.090Z: `--runs 1 --limit 3`, 5 units, "$0.0327". Both outputs were overwritten by later runs at the same paths. Source: `~/cc-archives/map-reader-llm/2026-02-05T01-47_3b5c4531/session.jsonl.gz` |
| First full 60-tile run (tool call) | 2026-02-05T02:07:04.520Z: `--condition image-only --runs 1` |
| First surviving run meta (public) | `archive/outputs-pre-retest-60-tile/phase2a/image-only/run_1/detections_image-only_run01.meta.json`: `timestamp.start` 2026-02-05T02:07:06.586542+00:00, `git_commit` `c64a7dce…`, manifest `inputs/tiles/validation_manifest.json`, 60 items |
| The tiles were holdout tiles | The `studies/phase2a-h1-modality.yaml:52` manifest at `c64a7dce` is `inputs/tiles/validation_manifest.json` (60 entries). Its selection seed 1767425239 (`tile_selection_metadata.json:168` at `c64a7dce`) is the "holdout selection seed" of lodged `preregistration.md:1944`. E20 records the holdout-to-validation renaming |
| Corroboration | Erratum E24: "a `--dry-run` … corrupted the checkpoint from 3 completed units to 50", matching the three image-only metas at `c64a7dce` (02:07-02:19 UTC). `execution-checklist.md:109`: Phase 2a began 2026-02-05. `session-log.md` Session 17 still lists "Upload Phase 1 materials to OSF" as pending |
| No earlier holdout call | (a) All 2,864 tracked `*.meta.json` files were scanned; none uses the validation manifest before 02:07:06 UTC. Phase 1 used `calibration_manifest.json`, 20 tiles, 2026-02-01. (b) No untracked or ignored meta files exist. (c) The session archives from 2026-01-28 to the 2026-02-05T01-47 session hold no non-dry-run detection command; both archive names were checked |

**Recommended wording for the erratum.** "Holdout evaluation began on 2026-02-05 at
02:03 UTC (13:03 AEDT). The repository state at that moment is commit `c64a7dce`." Note
that `c64a7dce` is the commit the first runs executed from. Its tree is the pre-holdout
state.

**Later holdout evaluations on the same 60 tiles**, relevant to the post-holdout items:

- Phase 2e (H4) ran from 2026-02-11T13:56:48Z to 2026-02-12T00:08:03Z. The run commits were:
  - `8118eb5e762e5254c0159bb6fdb03be8b8435427`;
  - `fa3043f8e9e62bbc0959c26790cb544b6bb0aca3`;
  - `8c292af65fcd6de503a9b8fa4f9044b092bad8c5`.
- Phase 3c (H9) ran from 2026-03-07T19:24:17Z to 2026-03-08T05:50:52Z, all 225 metas at
  `ec00c2ae031865f14bbc0014a4f8c37680057e2a`.

### 1.2 Second holdout evaluation: Era-1 retest, 2026-03-15 (340 tiles)

The retest used `inputs/tiles/full_evaluation_manifest.json`: 340 tiles, the 360-tile
corpus less the 20 calibration tiles. That set includes the original 60.

| Evidence | Value |
|---|---|
| First retest API work (session archive, private) | 2026-03-15T10:03:32.595Z (tool call), a pilot: `run_phase2.py studies/retest/phase2c-h8-library-text-only.yaml --mode batch --condition plus-hp --runs 1`. Batch job `batches/6n7kdicate0p5wzmy1yn250djgqwgfegvr6a`, completed by 10:08:55Z. Source: `~/cc-archives/map-reader-llm/2026-03-15T05-54_transition-map-reader-llm-study-to-340-tile/session.jsonl.gz`. An attempt at 09:57:38Z failed for lack of `GOOGLE_API_KEY` and made no calls |
| Code at the pilot | Local commit `72d585b`, which is **not in the repository** (`git cat-file` fails). It was rebased into `f06afb7acb45f01d56d6cbaf7d9e5304b93a6a98` (author date 2026-03-15T18:38:02+11:00; committer date 2026-03-15T21:06:11+11:00, i.e. the rebase at 10:06:11 UTC). The pilot's outputs were later overwritten: the surviving plus-hp text meta is 10:56:52Z at `5a57f586e` |
| Full launch | 2026-03-15T10:26:09.611Z to 10:26:19.429Z (tool calls): nine retest study YAMLs (Phases 2a-2e) |
| Commit in force at full launch | `5a57f586eebe936cff3638a542cf0ea92d1107a1`, 2026-03-15T21:21:42+11:00 (10:21:42 UTC) |
| First surviving retest meta (public) | `outputs/retest/phase2c/track2-text/canonical/run_1/detections_canonical_run01.meta.json`: 2026-03-15T10:39:15.436499+00:00, `5a57f586e…`, 340 items. A batch meta records the write time, not the submission time |

Aside: 384 px H11 verifier runs (`outputs/h11/proposer-verifier-384/`) wrote metas on
2026-03-14, before the retest. They are a different tile frame and are outside this
question.

---

## 2. Per-item provenance

The pre-holdout reference commit is `H` = `c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3`. Its
tree is byte-identical, for every library, text, config, and register path, to the
OSF-cited `5d8c251b9824ae9b3f3f3cf3d90496978578a085`, except `studies/phase2e-h4-ordering.yaml`
(§ 3.1). "Unchanged to HEAD" means the blob hash or the scripted comparison is equal at
HEAD (`72366e2a4`, branch `register-repair`). All cited commits are contained in
`origin/main`, per the local remote-tracking ref; GitHub was not queried.

| # | Item | Path(s) | Executed-form commit | Last pre-holdout commit touching it | Changed after holdout start? | Permalink (pre-holdout tree) | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Library manifest | `inputs/examples/neutral-naming/MANIFEST.md`; `prompts/configs/library_*.json` (7); `prompts/configs/detect_*.json` (11); `inputs/examples/null-tiles/null_tiles_manifest.json` | MANIFEST: `6e772b55ac806a7e9d010d1cece500c37ee7abf0` (2026-02-02T21:18:46+11:00). Config example lists: `e41d80de8528937fbbd6b205c9463999f53e7733` (2026-01-21T23:23:42+11:00); `library_pure-positive-canon.json`: `d06eacd0ec9ccf20473c3565e93145410b833e33` (2026-02-01T12:51:24+11:00) | Same as executed-form | MANIFEST and null manifest: `bcf936ad2d214836be62e941d76122672b6e41c9` (2026-09-13; E86 annotation of null-exemplar provenance, no change to the listed files). Library configs: `953e2d26ddde67657d54e67bf3ae188523e205d1` (2026-02-08; adds model, instruction, T and thinking fields) and `b84925d294abbe13d00d6d95a27c2c7b4273279a` (2026-04-18; plus-hp `include_example_images` made explicit). Original 11 detect configs: `4ecaf06d49011a08537f37951823a58d07975465` (2026-02-06; E25 text-only flag) and `c9f178bf7e92ff75e6cc1a5b5db6ce14c900182b` (2026-08-28). Other post-holdout commits only add new `detect_*.json` files. **The example lists (paths and order) are identical at H and HEAD for all 18 detect and library configs** | <https://github.com/saross/map-reader-llm/blob/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/inputs/examples/neutral-naming/MANIFEST.md> · <https://github.com/saross/map-reader-llm/tree/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/prompts/configs> | The planned `inputs/few-shot-library/library-manifest.json` (`execution-plan.md:237`) **never existed in any commit**. MANIFEST.md is the de facto manifest: it gives neutral name, source file, category, source tile, fid, and distance for each example |
| 2 | Brief text | `prompts/system-instructions/detect_brief-text.md` ≡ `detect_brief-text-image.md` (same blob `274c48f47010a87a73ff205554a1b9adf22305b6`) | `2d46311714e5dc2459f117f0bc90be15e6d669aa` (2026-02-03T23:19:33+11:00) | `2d46311…` | **No** (blob equal at HEAD) | <https://github.com/saross/map-reader-llm/blob/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/prompts/system-instructions/detect_brief-text.md> | SHA-256 `e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12` equals `prompt_hash` in the Phase 2a metas and `system_instruction_hash` in the retest metas. Caveat (E25): the February text-only runs at H also received images. Those runs were re-done after `4ecaf06d` and the invalid ones archived in `archive/phase2a-invalid-text-only-runs/`. The text itself did not change |
| 3 | Verbose text | `detect_verbose-text.md` ≡ `detect_verbose-text-image.md` (blob `2ecd222963e9e35a6bd3ae332271eccbf9648094`) | `52d54e981c0b3233944036f65e5c71ef290a6b0b` (2026-02-04T09:46:04+11:00) | `52d54e98…` | **No** | <https://github.com/saross/map-reader-llm/blob/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/prompts/system-instructions/detect_verbose-text.md> | SHA-256 `522f54e0c4fee5cba379abb4d088603a690ef1645a0a3988e27f0057ff9ed367` equals `prompt_hash` in the verbose metas. Separate from H1 brief and verbose: the H5 exclusion variants (`*_terse.md`, `*_verbose.md`) were edited after holdout by `b0d7dd0802bed68eb9eada9e918823c02b297379` (2026-02-11; E28) |
| 4 | Mapping table (hard example ↔ text guidance) | None as such. Partial: `archive/planning/hard-example-review/prompt-text-review-synopsis.md` | Created as `planning/prompt-text-review-synopsis.md` by `f3e33b7fb785011e949b1462cd83ee541f2040ae` (2026-02-03T22:00:05+11:00) | Moved to the archive path by `b7d7238f159802eadcfe2f5f810879e5eb66abba` (2026-02-03T23:27:33+11:00) | **No** (blob `b929ff98…` equal at H and HEAD) | <https://github.com/saross/map-reader-llm/blob/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/archive/planning/hard-example-review/prompt-text-review-synopsis.md> | **No dedicated table ever existed.** The planned `prompts/text-image-alignment.md` is in no commit. The synopsis maps text Changes 1-4 to HP 07; HN 13; HN 11 and 14; HP 05, 06 and 08. **HN 12 is unmapped**, and the synopsis itself says the full "Cross-reference table" was "In CC Session 11 conversation (prompt text ↔ image path)". Context: `combined-prompt-review-feedback.md` (same folder); Decisions 13-14; E16 |
| 5 | Final image filenames for all hard examples (and images) | `inputs/examples/hard-positive/example_05..08_*.png` (4); `inputs/examples/hard-negative/example_11..14_*.png` (core 4) and `example_18..29_*.png` (H9 pool, 12); symlinks `inputs/examples/neutral-naming/example_NN.png` | 05-08 and 11-14 (re-extracted as 128×128 crops): `f793ca7cb8c9b539e4503448b81286e4d98ab94e` (2026-02-02T21:18:32+11:00). 18-29: `6e772b55…` (2026-02-02T21:18:46+11:00) | `6e772b55…`; `git diff` from there to H over `inputs/examples` is empty | **No** (`git diff --stat H HEAD` shows no PNG or symlink change) | <https://github.com/saross/map-reader-llm/tree/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/inputs/examples> | The first crops (`12898e9478e596fa807d15ad509adc85721f8d80`, 2026-02-01) were superseded before holdout. Sizes: HP 135,382 B; HN 558,073 B. Caveat E86: the three null exemplars overlap 3 of the 60 holdout tiles (`bcf936ad` message) |
| 6 | Selection rationale (frequency counts) | `outputs/phase1-library/fp-fn-register.md`, now `archive/outputs-pre-retest-60-tile/phase1-library/fp-fn-register.md` (R100 move by `276e4ca80e2e664e896db4c540731e919f9a58a5`, 2026-04-16). Also `decisions-log.md` Decision 4 and raw Phase 1 outputs in the same folder | Register: `3c835863d88080f8745307426c8f78d4e15f7950` (2026-02-02T21:19:24+11:00; created `bc7ace196986c7611afc5f9d8cd37d43760d2bd6`, 2026-02-01). Decision 4 final wording: `2b473d74c4b4135ce71a6c4ec52b8a685177d664` (2026-02-04T21:16:56+11:00) | Register: `3c835863…`. Decisions log: H (adds D15 only) | Register: **no** (blob `b5d42f45…` equal at H and HEAD; path moved only). Decision 4 section: **no** (identical text at H and HEAD) | <https://github.com/saross/map-reader-llm/blob/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/outputs/phase1-library/fp-fn-register.md> | A prose summary of Decision 4, with aggregate counts (24 FNs 0/5; 9 recognition and 15 localisation failures; 4 HN from vote-5/5), reached OSF before holdout in the 2026-02-04 registration update (repository copy `osf/phase1-errata-and-decisions.md:176-198`). That update was **embargoed until 2026-06-30**. Decision 4 at `5d8c251` still carried the stale K=10 wording; `2b473d74` corrected it the same day |
| 7 | Complete H9 prompt variants V1-V5 | `prompts/system-instructions/detect_brief-text-image_v1..v5.md`; `prompts/configs/phase3c-t{1,2}-h9*.json` (22); `scripts/generate_phase3c_configs.py`; `studies/phase3c-h9-diversity-track{1,2}.yaml` | `ec00c2ae031865f14bbc0014a4f8c37680057e2a` (2026-03-07T23:03:26+11:00 = 12:03:26 UTC), the only commit for each file | **None: did not exist before holdout.** At H, `prompts/README.md:291-298` lists only the five illustrative framing lines, with "Status: Methodology specified; final instruction files to be created before holdout evaluation" | **No** commits after `ec00c2ae` on any of these paths | <https://github.com/saross/map-reader-llm/blob/ec00c2ae031865f14bbc0014a4f8c37680057e2a/prompts/system-instructions/detect_brief-text-image_v1.md> (v2-v5 alongside) | Finalised **30 days after** holdout began, and after holdout Phases 2a-2e and 3a. They ran in the 60-tile Phase 3c (2026-03-07T19:24Z to 2026-03-08T05:50Z) and the retest Phase 3c (metas 2026-03-18T12:08Z to 2026-03-25T06:38Z). By design they could not precede holdout: lodged `preregistration.md:1411` and appendix `:140-147` build V1-V5 from the winning holdout configuration. They vary the H1 title line, whereas lodged `:1397-1399` holds "Section headers and order" constant. E63: the retest Phase 3c ran at HIGH thinking |
| 8 | Exact ordering for each condition | Config `examples` arrays; `scripts/4_detect_mounds_batch.py` `reorder_examples`; `scripts/run_phase2.py`; `studies/phase2e-h4-ordering.yaml`; `studies/retest/*.yaml` | Config order: as item 1 (H). **H4 executed definitions:** `ea5f153322121a6fd7b2842aae2f76820a905e78` (2026-02-12T00:44:26+11:00; E29, true canonical-first, config-default added, seed passthrough) and `8118eb5e762e5254c0159bb6fdb03be8b8435427` (2026-02-12T00:44:41+11:00; four-arm YAML). Retest batch mirror: `ead94aa81d686f41fbef0627d1e7575e4ef8930a` (2026-03-15T13:33:11+11:00) | At H: `4_detect_mounds_batch.py:108-150` (`reorder_examples`; canonical-first is a **no-op** at `:127-130`; canonical-last `:132-136`; random `:138-144`). `run_phase2.py:169-170` and `:371-373` pass `--ordering` but **not** `--ordering-seed`. Phase 2e YAML: three levels, placeholder carry-forward | **Yes**: `ea5f1533`, `8118eb5e`, `ead94aa81`, and retest YAMLs `f06afb7a…` (2026-03-15) | <https://github.com/saross/map-reader-llm/blob/8118eb5e762e5254c0159bb6fdb03be8b8435427/scripts/4_detect_mounds_batch.py#L158-L236> · <https://github.com/saross/map-reader-llm/blob/5a57f586eebe936cff3638a542cf0ea92d1107a1/scripts/run_phase2.py#L74-L115> | **No run records the order sent.** The February real-time metas record `ordering_override` and seed but the unreordered list; the retest batch metas record neither (W3 report). Order is code-inferred (§ 2.8). February 2a-2d ran in config order (`ordering_override` is None in all 290 metas). Retest 2b-2d fixed `canonical-first` (YAMLs `:48-49`, `:89-90`, `:51-52`) |
| 9 | Random seeds used | `inputs/tiles/tile_selection_metadata.json`; `inputs/examples/null-tiles/null_tiles_manifest.json`; `scripts/run_phase2.py`; `studies/phase2e-h4-ordering.yaml`; `studies/retest/phase2e-h4-ordering.yaml`; Phase 2e metas | Tile seeds 2025-12-23 and 2026-01-03; null-tile seed 2025-12-23; unit-order seed `20260205` at H; H4 seed base 42 present at H but only **wired** at `ea5f1533` (2026-02-12) | H for all present seeds | H4 seeding changed post-holdout (`ea5f1533`). The H9 seed **never existed** | <https://github.com/saross/map-reader-llm/blob/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/inputs/tiles/tile_selection_metadata.json> · <https://github.com/saross/map-reader-llm/blob/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/scripts/run_phase2.py#L183-L225> | Itemised in § 2.9 |

### 2.1 Notes on item 1 (library manifest)

- The executed library is the 17-example Scale-8 set (`library_scale-8.json` at H) and its
  sub-libraries (`library_canonical.json`, `library_plus-hp.json`,
  `library_pure-positive-canon.json`, `library_scale-4.json`).
- `library_scale-16.json` and `library_scale-32.json` were empty at H (deferred, E11).
- The neutral-name files are git symlinks (mode `120000`) into `legend-positive/`,
  `hard-positive/`, `legend-negative/`, `hard-negative/` and `null-tiles/`. Their link
  targets are identical at H and HEAD.

### 2.4 Notes on item 4 (mapping table)

The PI could reconstruct a table now from the synopsis, the brief and verbose texts at
`2d46311`/`52d54e98`, and Decisions 13-14. It should be labelled as a 2026-10
reconstruction, not a pre-holdout record. The Session 11 transcript, if archived, may
hold the original table (not searched here).

### 2.8 Ordering as executed (code-inferred, not recorded)

February Phase 2e used `library_plus-hp.json` (13 examples) through the real-time path at
`8118eb5e`. The table was computed offline in this session by executing
`reorder_examples` from `git show 8118eb5e:scripts/4_detect_mounds_batch.py` lines
158-236. The input was `library_plus-hp.json` at `8118eb5e`. Python 3.13.3 was used here;
the run-time Python version was not verified.

| Arm | Example order (neutral-name numbers) |
|---|---|
| config-default (Phase 2c baseline, symlinked) | 01 02 03 04 05 06 07 08 09 10 15 16 17 |
| canonical-first | 01 02 03 04 09 10 05 06 07 08 15 16 17 |
| canonical-last (real-time path: non-canonical + canonical) | 05 06 07 08 15 16 17 01 02 03 04 09 10 |
| random, run 1, seed 42 | 08 07 03 10 17 06 16 09 04 05 01 02 15 |
| random, seed 43 | 09 10 15 17 07 16 04 02 06 08 03 05 01 |
| random, seed 44 | 04 06 05 08 01 15 10 17 03 02 16 09 07 |
| random, seed 45 | 09 16 15 04 06 01 03 10 02 17 08 07 05 |
| random, seed 46 | 08 17 09 06 15 16 05 03 04 10 01 07 02 |
| random, seed 47 | 16 01 15 10 04 05 03 17 08 09 07 02 06 |
| random, seed 48 | 16 15 01 04 02 08 07 05 10 17 03 06 09 |
| random, seed 49 | 05 15 04 10 03 08 09 01 16 17 07 06 02 |
| random, seed 50 | 10 07 09 02 03 16 01 15 17 04 06 05 08 |
| random, seed 51 | 01 02 06 08 10 05 07 15 17 03 16 09 04 |

- **Seeds and metas.** The seeds 42-51 per run are recorded in the February metas
  (`ordering_seed`). The order itself is not.
- **Cross-check.** The seed-42 order matches the independent retest replay in
  `reports/phase2e-ordering-check-2026-10-05.md` (W3.2).
- **Retest canonical-last.** The batch mirror at `5a57f586e:scripts/run_phase2.py:103`
  sent `null + hard + canonical`: 15 16 17 05 06 07 08 01 02 03 04 09 10 (W3). This
  differs from the February real-time arm (05-08 before 15-17). The canonical placement
  is the same.
- **Phases 2a-2d.** Config order throughout, for example `detect_*.json`: Canon+ 01-04,
  HP 05-08, Canon− 09-10, HN 11-14, null 15-17 (`ordering_note` in each config at H).
- **Registered "HP/HN interleaved randomly (documented seed)".** No interleaving or seed
  appears in any config (lodged `preregistration.md:564`).

### 2.9 Seeds as executed

| Seed | Value | Where (file:line at commit) | Pre-holdout? |
|---|---|---|---|
| Calibration (training) tile selection | 1766464625 | `inputs/tiles/tile_selection_metadata.json:11` at H; lodged `preregistration.md:91`, `:1944` | Yes (already registered) |
| Holdout (validation) tile selection | 1767425239 | same file `:168` at H | Yes (already registered) |
| Null-tile selection | 20251223 | `null_tiles_manifest.json` `selection_methodology.random_seed` at H; lodged `:1538` | Yes |
| Execution-unit shuffle | 20260205 (default argument) | `run_phase2.py:186` (call `:501`) at H; same default at `8118eb5e:192`, `ec00c2ae:210`, `5a57f586e:268`. The realised order is in each phase's `study_manifest.json` `execution_order` | Yes |
| H4 random ordering (February) | base 42, so seeds 42-51 for runs 1-10 | `studies/phase2e-h4-ordering.yaml:63` at H (declared). Wired by `ea5f1533`: `run_phase2.py:229` and `:448-449` at `8118eb5e`. Recorded per run in the Phase 2e metas | Declared yes; **effective only from 2026-02-12** |
| H4 random ordering (retest) | 42 (run 1) | `studies/retest/phase2e-h4-ordering.yaml` (`random_seed_base: 42`); `run_phase2.py:875` and `:305` at `5a57f586e`. **Not recorded in the retest meta** | No (2026-03-15) |
| H9 HN rotation (C/E) | **none**: a fixed hand-written schedule | `scripts/generate_phase3c_configs.py:101-107` (`HN_ROTATION`) at `ec00c2ae` | No, and it departs from lodged §8.4.4 seeded sampling (`:1605`, `:1664`) |
| API generation seed | none set | At H, `4_detect_mounds_batch.py` uses `seed` only in ordering (`:140-141`) | n/a |

---

## 3. Proposed deposit bundle

### 3.1 Anchoring

- **Recommended source commit for Part A: `5d8c251b9824ae9b3f3f3cf3d90496978578a085`.**
  - The repository copy of the OSF update (`osf/phase1-errata-and-decisions.md:5`) reads
    "at commit `5d8c251`". The OSF state check
    (`reports/osf-state-check-2026-10-05.md` § 1.3) reports that update as submitted
    2026-02-04 10:50 UTC. This was not re-verified against OSF in this session.
  - `git diff --stat 5d8c251 c64a7dce` over the library, text, config, register, and
    synopsis paths changes only `studies/phase2e-h4-ordering.yaml`. That change is E17
    housekeeping (`passes: 5` removed; costs).
  - So OSF's own timestamp fixes the git object hash of a tree containing items 1, 2, 3,
    5 and 6 and the partial item 4. This is the best mitigation available.
  - Caveat: git commit dates are self-reported. The OSF hash citation is the only
    external timestamp found, and push dates to GitHub were not checked.
- **Discrepancy to resolve.** `session-log.md` Session 15 (2026-02-04) says the "user
  uploaded 5 files to OSF": protocol-errata, decisions-log, fp-fn-register,
  hypothesis-tracking, and prompt-text-review-synopsis. The OSF state check found no
  upload after 2026-01-31 and no files on the update. If those files were ever attached,
  item 6 and the partial item 4 were deposited on time. Worth checking the update's
  version history on OSF.
- **Tying OSF bytes to git.** With each file, upload a listing of
  `git ls-tree -r <commit> -- <paths>` (blob hashes), so anyone can confirm the
  deposited bytes equal the committed blobs.

### 3.2 Part A: pre-holdout materials

Rows are at `5d8c251` and identical at `c64a7dce`, unless marked "at `c64a7dce`". The
decisions log and the Phase 2e YAML differ between the two commits.

| File (path at commit) | Size (bytes) | Item |
|---|---:|---|
| `inputs/examples/neutral-naming/MANIFEST.md` | 12,020 | 1, 5 |
| `prompts/configs/library_*.json` (7 files) | 10,302 | 1 |
| `prompts/configs/detect_*.json` (11 files) | 27,898 | 1, 8 (config order) |
| `inputs/examples/hard-positive/*.png` (4) | 135,382 | 5 |
| `inputs/examples/hard-negative/*.png` (16) | 558,073 | 5 |
| `inputs/examples/legend-positive/*.png` (4) and `legend-negative/*.png` (2) | 35,410 + 6,502 | 1 (canonical examples) |
| `prompts/system-instructions/detect_brief-text.md` (identical to `-image`) | 1,567 | 2 |
| `prompts/system-instructions/detect_verbose-text.md` (identical to `-image`) | 5,305 | 3 |
| `outputs/phase1-library/fp-fn-register.md` | 20,837 | 6 |
| `archive/planning/hard-example-review/prompt-text-review-synopsis.md` | 5,949 | 4 (partial) |
| `inputs/examples/null-tiles/null_tiles_manifest.json` | 934 | 9 |
| `inputs/tiles/tile_selection_metadata.json` (at `c64a7dce`; pre-E87-note version) | 17,490 | 9 |
| `docs/methodology/preregistration/decisions-log.md` (at `c64a7dce`; Decision 4 final) | 35,004 | 6 |
| `studies/phase2e-h4-ordering.yaml` (at `c64a7dce`) | 4,678 | 8, 9 (seed base 42 declared) |
| **Subtotal** | **≈ 893 KB** | |
| Optional: `inputs/examples/null-tiles/null_*.png` (3) | 1,451,046 | 1 (null exemplars; E86 caveat) |

### 3.3 Part B: post-holdout materials, labelled as finalised after holdout began

| File (path at commit) | Size (bytes) | Item |
|---|---:|---|
| `prompts/system-instructions/detect_brief-text-image_v1..v5.md` at `ec00c2ae` | 9,067 | 7 |
| `scripts/generate_phase3c_configs.py` at `ec00c2ae` (HN rotation; no seed) | 13,571 | 7, 9 |
| `studies/phase3c-h9-diversity-track1.yaml` and `track2.yaml` at `ec00c2ae` | 10,413 + 9,067 | 7 |
| Optional: `prompts/configs/phase3c-*.json` (22) at `ec00c2ae` | 69,117 | 7 |
| `studies/phase2e-h4-ordering.yaml` at `8118eb5e` | 5,169 | 8, 9 |
| `studies/retest/phase2e-h4-ordering.yaml` at `f06afb7a` | 3,722 | 8, 9 |
| `reports/phase2e-ordering-check-2026-10-05.md` (`ccf9c613d4517b94015c1921de6ae54e689b051f`) | 24,743 | 8 |
| **Subtotal** | **≈ 145 KB** (with optional configs) | |

- **The W3 report's commit is not yet on `origin/main`.** It is on `origin/register-repair`
  only, so its permalink would break if that branch were deleted.
- **To be written by the PI:**
  - a short `deposit-index.md` giving, for each registered item, its file, commit, and
    permalink, with "pre-holdout" or "late" stated;
  - an ordering-and-seeds table (§§ 2.8-2.9) labelled "code-inferred";
  - a reconstructed mapping table labelled as a 2026-10 reconstruction.

---

## 4. Verification log

All commands were run in `/home/shawn/Code/map-reader-llm` on 2026-10-05.
`H=c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3`.

```bash
# Registered passages
grep -n "Step 6: Document and Upload\|upload to OSF: library manifest" docs/methodology/preregistration/osf/preregistration.md
grep -n "Finalisation Documentation\|Final image filenames for all hard\|Random seeds used" docs/methodology/preregistration/osf/preregistration-appendix-prompts.md

# Holdout start
# meta scan (scratchpad scan_meta.py): every tracked *.meta.json -> start, git_commit, manifest, items
git ls-files --others --ignored --exclude-standard | grep -c meta.json      # 0
git show -s --format='%H %ad %s' --date=iso-strict c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3
TZ=UTC git show -s --format='UTC: %ad' --date=iso-local c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3
git show $H:studies/phase2a-h1-modality.yaml | grep -n manifest           # :52
git show $H:inputs/tiles/tile_selection_metadata.json | grep -n "random_seed\|selection_date"
sed -n 464,480p docs/methodology/preregistration/protocol-errata.md        # E20
awk '/^### E2[1-4]/{p=1} /^### E25/{p=0} p' docs/methodology/preregistration/protocol-errata.md   # E24
zcat ~/cc-archives/map-reader-llm/2026-02-05T01-47_3b5c4531/session.jsonl.gz | <python: Bash tool_use + tool_result for run_phase2>
# (scan of ~/cc-archives/map-reader-llm sessions 2026-01-28 .. 2026-02-05T01-47 for non-dry-run detection)

# Retest start
git show -s --format='%H %ad %s' --date=iso-strict 5a57f586eebe936cff3638a542cf0ea92d1107a1
git show -s --format='%H author=%ad committer=%cd %s' --date=iso-strict f06afb7acb45f01d56d6cbaf7d9e5304b93a6a98
git cat-file -t 72d585b                                                    # fatal: not a valid object
zcat ~/cc-archives/map-reader-llm/2026-03-15T05-54_transition-map-reader-llm-study-to-340-tile/session.jsonl.gz | <python: run_phase2 retest commands and results>
# (python over outputs/retest/**/*.meta.json: earliest per phase)

# Items 1 and 5: library
git log --follow --format='%H %ad %s' --date=iso-strict -- inputs/examples/neutral-naming/MANIFEST.md
for d in hard-positive hard-negative legend-positive legend-negative null-tiles neutral-naming; do git log --format='%H %ad %s' --date=iso-strict $H -- inputs/examples/$d; done
git diff --stat 6e772b55ac806a7e9d010d1cece500c37ee7abf0 $H -- inputs/examples      # empty
git diff --stat $H HEAD -- inputs/examples/{hard-positive,hard-negative,legend-positive,legend-negative,null-tiles,neutral-naming}   # MANIFEST, null JSONs only
git ls-tree $H inputs/examples/neutral-naming/ ; git ls-tree HEAD inputs/examples/neutral-naming/   # symlink blobs equal
git show bcf936ad2d214836be62e941d76122672b6e41c9 -- inputs/examples/neutral-naming/MANIFEST.md
python3 scratchpad/cmp_examples.py $H HEAD                                 # 18 detect/library configs identical
for f in ...; do git log -2 $H -- prompts/configs/$f; git log $H..HEAD -- prompts/configs/$f; done
git show 953e2d26ddde67657d54e67bf3ae188523e205d1 --stat ; git show b84925d294abbe13d00d6d95a27c2c7b4273279a -- prompts/configs/library_plus-hp.json
git log --all --name-only -- 'inputs/few-shot-library' '**/library-manifest*' '**/text-image-alignment*' 'prompts/brief-text.md' 'prompts/verbose-text.md'   # nothing

# Items 2 and 3: texts
for f in detect_brief-text.md detect_brief-text-image.md detect_verbose-text.md detect_verbose-text-image.md; do git log -3 $H -- prompts/system-instructions/$f; git log $H..HEAD -- prompts/system-instructions/$f; git rev-parse $H:prompts/system-instructions/$f HEAD:prompts/system-instructions/$f; done
git show $H:prompts/system-instructions/detect_brief-text.md | sha256sum   # e169b723...
git show $H:prompts/system-instructions/detect_verbose-text.md | sha256sum # 522f54e0...
# python: prompt_hash in archive/outputs-pre-retest-60-tile/phase2a/*/run_1/*.meta.json

# Item 4: mapping
git ls-files | grep -i "synopsis\|alignment\|mapping"
git show --stat f3e33b7fb785011e949b1462cd83ee541f2040ae ; git show --stat b7d7238f159802eadcfe2f5f810879e5eb66abba
git rev-parse $H:archive/planning/hard-example-review/prompt-text-review-synopsis.md HEAD:archive/planning/hard-example-review/prompt-text-review-synopsis.md
sed -n 30,128p archive/planning/hard-example-review/prompt-text-review-synopsis.md

# Item 6: rationale
git log --follow --name-status -- archive/outputs-pre-retest-60-tile/phase1-library/fp-fn-register.md
git rev-parse $H:outputs/phase1-library/fp-fn-register.md HEAD:archive/outputs-pre-retest-60-tile/phase1-library/fp-fn-register.md   # b5d42f45 both
git log -4 $H -- docs/methodology/preregistration/decisions-log.md
# awk-extract "## Decision 4" at $H, HEAD, 5d8c251 and diff (H == HEAD; 5d8c251 differs: K=10 wording)

# Item 7: H9
git log --follow -- prompts/system-instructions/detect_brief-text-image_v{1..5}.md     # ec00c2ae only
git log ec00c2ae031865f14bbc0014a4f8c37680057e2a..HEAD -- 'prompts/configs/phase3c-*' studies/phase3c-h9-diversity-track{1,2}.yaml scripts/generate_phase3c_configs.py prompts/system-instructions/detect_brief-text-image_v{1..5}.md   # nothing
git grep -l -i "tumuli markers\|kurgan indicators" $H -- .
git show $H:prompts/README.md | grep -n -B2 -A12 "tumuli markers"
grep -n "Identify winning configuration\|Document all 5 variants" docs/methodology/preregistration/osf/preregistration-appendix-prompts.md
grep -n "Identify optimal base configuration\|Section headers and order" docs/methodology/preregistration/osf/preregistration.md
# python over archive/outputs-pre-retest-60-tile/phase3c and outputs/retest/phase3c metas: first/last start, commits

# Items 8 and 9: ordering and seeds
git show $H:scripts/4_detect_mounds_batch.py | sed -n 100,152p ; git show $H:studies/phase2e-h4-ordering.yaml
git show $H:scripts/run_phase2.py | sed -n 183,225p ; git show $H:scripts/run_phase2.py | grep -n generate_execution_units
git show ea5f153322121a6fd7b2842aae2f76820a905e78 --stat
git log --follow -- studies/phase2e-h4-ordering.yaml ; git log --follow -- studies/retest/phase2e-h4-ordering.yaml
git show 8118eb5e762e5254c0159bb6fdb03be8b8435427:scripts/4_detect_mounds_batch.py | sed -n 181,232p
git show 8118eb5e762e5254c0159bb6fdb03be8b8435427:scripts/run_phase2.py | grep -n 'random_seed_base\|ordering_seed'
git show 5a57f586eebe936cff3638a542cf0ea92d1107a1:scripts/run_phase2.py | grep -n 'if ordering == "\|random_seed_base'
git show -s ead94aa81d686f41fbef0627d1e7575e4ef8930a fa3043f8e9e6 8c292af65fcd
# python over archive/outputs-pre-retest-60-tile/phase2e metas: ordering_override, ordering_seed, examples
# python over phase2a-2d metas: ordering_override all None
grep -n -A1 "^fixed:" studies/retest/phase2{a,b,c,d}-*.yaml
git show ec00c2ae031865f14bbc0014a4f8c37680057e2a:scripts/generate_phase3c_configs.py | sed -n 99,117p
git show $H:inputs/examples/null-tiles/null_tiles_manifest.json | head -20
# offline: exec reorder_examples (8118eb5e lines 158-236) on library_plus-hp.json @8118eb5e, seeds 42-51

# Anchors, sizes, remotes
git show -s --format='%H author=%ad committer=%cd %s' --date=iso-strict 5d8c251
git diff --stat 5d8c251b9824ae9b3f3f3cf3d90496978578a085 $H -- inputs/examples prompts/configs prompts/system-instructions outputs/phase1-library/fp-fn-register.md archive/planning/hard-example-review studies/phase2e-h4-ordering.yaml inputs/tiles/tile_selection_metadata.json
git merge-base --is-ancestor 5d8c251b9824ae9b3f3f3cf3d90496978578a085 $H
git cat-file -s <commit>:<path>   ;  git ls-tree -r -l <commit> <dir>
git branch -r --contains <hash>    # all cited hashes in origin/main; W3 report only origin/register-repair
```

## Changelog

### 2026-10-05 — Original publication (Session 161)

Written by a read-only research agent for W8.3/W8.4 (S-11), Session 161; its key commits, blob hashes, dates and the session-log record were spot-checked against git at source before use.
