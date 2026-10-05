# Late deposit of the registered pre-holdout materials — index

> **Last revised**: 2026-10-05 (later: items 8 and 9 worded more fully).
> See [§ Changelog](#changelog) for revision history.

**This is a late deposit.** The registration committed these materials to
the Open Science Framework (OSF) project "before any holdout evaluation"
(`preregistration.md:1498-1500`; `preregistration-appendix-prompts.md:159-167`).
They were not deposited then. Erratum **E91**
(`../../protocol-errata.md`) records the deviation. This index deposits them
on 2026-10-05, each from the git commit that holds it, and states for every
item whether it was public before holdout evaluation began.

**Holdout evaluation began** on 2026-02-05 at 02:03:57 UTC (the first
Phase 2a run on the 60 validation tiles), at commit
[`c64a7dce`](https://github.com/saross/map-reader-llm/tree/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3).
The repository <https://github.com/saross/map-reader-llm> is public.

**The external anchor.** The registration's first update on OSF
(submitted 2026-02-04 10:50 UTC) cites commit `5d8c251` by hash. Every
pre-holdout file in part A below is byte-identical at `5d8c251` and at
`c64a7dce`. Commit dates are self-reported; that OSF citation is the one
timestamp outside this repository that fixes a git tree to a date.

## The nine registered items

| # | Registered item | Status at holdout start | Deposited as (commit / path) | Permalink |
|---|---|---|---|---|
| 1 | Library manifest | **Public before holdout; unchanged since.** No `library-manifest.json` was ever made; the manifest that ran is `MANIFEST.md` plus the library and detection configurations | A / `5d8c251b9/inputs/examples/neutral-naming/MANIFEST.md`; `5d8c251b9/prompts/configs/library_*.json`, `detect_*.json` | [MANIFEST.md](https://github.com/saross/map-reader-llm/blob/5d8c251b9824ae9b3f3f3cf3d90496978578a085/inputs/examples/neutral-naming/MANIFEST.md) · [configs](https://github.com/saross/map-reader-llm/tree/5d8c251b9824ae9b3f3f3cf3d90496978578a085/prompts/configs) |
| 2 | Brief text | **Public before holdout; unchanged since** (its SHA-256 equals the run metadata's `prompt_hash`) | A / `5d8c251b9/prompts/system-instructions/detect_brief-text.md` (identical to `-image`) | [brief text](https://github.com/saross/map-reader-llm/blob/5d8c251b9824ae9b3f3f3cf3d90496978578a085/prompts/system-instructions/detect_brief-text.md) |
| 3 | Verbose text | **Public before holdout; unchanged since** | A / `5d8c251b9/prompts/system-instructions/detect_verbose-text.md` (identical to `-image`) | [verbose text](https://github.com/saross/map-reader-llm/blob/5d8c251b9824ae9b3f3f3cf3d90496978578a085/prompts/system-instructions/detect_verbose-text.md) |
| 4 | Mapping table (hard-example image ↔ text guidance) | **Never existed as a file.** A partial mapping (seven of eight hard examples) was public before holdout | A / `5d8c251b9/archive/planning/hard-example-review/prompt-text-review-synopsis.md` | [synopsis](https://github.com/saross/map-reader-llm/blob/5d8c251b9824ae9b3f3f3cf3d90496978578a085/archive/planning/hard-example-review/prompt-text-review-synopsis.md) |
| 5 | Final image filenames for all hard examples | **Public before holdout; unchanged since** (images and names) | A / `5d8c251b9/inputs/examples/{hard-positive,hard-negative,legend-positive,legend-negative,null-tiles}/` | [examples](https://github.com/saross/map-reader-llm/tree/5d8c251b9824ae9b3f3f3cf3d90496978578a085/inputs/examples) |
| 6 | Selection rationale (frequency counts) | **Public before holdout; unchanged since** | A / `5d8c251b9/outputs/phase1-library/fp-fn-register.md`; `c64a7dceb/docs/methodology/preregistration/decisions-log.md` (Decision 4) | [register](https://github.com/saross/map-reader-llm/blob/5d8c251b9824ae9b3f3f3cf3d90496978578a085/outputs/phase1-library/fp-fn-register.md) |
| 7 | Complete H9 prompt variants V1-V5 | **Finalised 2026-03-07, after holdout began.** The registered design builds them from the winning holdout configuration | B / `ec00c2ae0/prompts/system-instructions/detect_brief-text-image_v1..v5.md`, their configs, study files and generator | [H9 variants](https://github.com/saross/map-reader-llm/tree/ec00c2ae031865f14bbc0014a4f8c37680057e2a/prompts/system-instructions) |
| 8 | Exact ordering for each condition | **Not fixed before holdout.** The example orderings used in the H4 experiment were settled in code on 2026-02-12, a week after holdout evaluation began (before then the code's canonical-first was a no-op, E29). No run's output records the order in which examples were actually sent; the orders are reconstructed from the code at each run's recorded commit | A / `c64a7dceb/scripts/4_detect_mounds_batch.py`, `studies/phase2e-h4-ordering.yaml` (as at holdout start); B / `8118eb5e7/` (February H4), `f06afb7ac/` and `5a57f586e/` (March retest), `ccf9c613d/reports/phase2e-ordering-check-2026-10-05.md` (the orders, inferred from code and outputs) | [W3 report](https://github.com/saross/map-reader-llm/blob/ccf9c613d4517b94015c1921de6ae54e689b051f/reports/phase2e-ordering-check-2026-10-05.md) |
| 9 | Random seeds used | **Partly before holdout.** Tile-selection, null-tile and execution-order seeds were fixed before; the seed base 42 for H4's random ordering was declared but passed to the code only on 2026-02-12; H9 used a fixed hand-written rotation instead of a seeded draw | A / `c64a7dceb/inputs/tiles/tile_selection_metadata.json`, `5d8c251b9/inputs/examples/null-tiles/null_tiles_manifest.json`, `c64a7dceb/scripts/run_phase2.py`; B / `ec00c2ae0/scripts/generate_phase3c_configs.py` | [tile seeds](https://github.com/saross/map-reader-llm/blob/c64a7dcebcd2fc4a55fafbc296b4c2f6ef1155b3/inputs/tiles/tile_selection_metadata.json) |

Nothing is reconstructed: items 4, 8 and 9 are deposited as what existed,
and labelled. The detailed provenance (every hash and date, with the
commands that support them) is `reports/osf-deposit-provenance-2026-10-05.md`
in the repository.

## What was uploaded to OSF

Folder `late-deposit-2026-10-05/` of project `osf.io/h9x4g`:

- `deposit-index.md` — this file.
- `A-public-before-holdout.zip` — 60 files, from commits `5d8c251b9` and
  `c64a7dceb`, laid out as `<commit>/<repository path>`.
- `B-finalised-after-holdout.zip` — 35 files, from commits `ec00c2ae0`,
  `8118eb5e7`, `f06afb7ac`, `5a57f586e` and `ccf9c613d`, same layout.
- `A-ls-tree.txt`, `B-ls-tree.txt` — `git ls-tree -r` of every deposited
  path at its commit (mode, type, blob hash, path).

**To check a deposited file against the repository**: run
`git hash-object <file>` and compare with its line in the `ls-tree`
listing, or `git ls-tree -r <commit> -- <path>` in a clone. All 95 files
matched when the bundle was built.

## Changelog

### 2026-10-05 (later) — Items 8 and 9 worded more fully

The ordering and seed rows now say what "not fixed before holdout" and "not
recorded" mean, in the wording the PI approved for registration update 2. No
status changed.

### 2026-10-05 — Original publication (Session 161)

Written for erratum E91's late deposit, from the provenance record
`reports/osf-deposit-provenance-2026-10-05.md` (spot-checked against git).
