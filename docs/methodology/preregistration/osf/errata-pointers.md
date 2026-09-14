# Erratum pointers into the lodged registration

> **Last revised**: 2026-09-14 (three § H1 / § H4 / factorial-table rows added
> under erratum E88). See [§ Changelog](#changelog) for revision history.

## What this document is, and why it exists separately

`preregistration.md` in this directory is the in-repository copy of the
registration lodged with the Open Science Framework (OSF). The lodged
registration is **immutable**, and so, in practice, is this copy: the
commitment ledger `results/commitments.json` pins all three lodged documents by
git blob (`preregistration.md` at `fa221b30f395`) and anchors **702 extracted
commitments** to verbatim statements at specific line ranges inside them.
Inserting so much as a blockquote shifts those line numbers and breaks the
anchors — attempted on 2026-09-13, it produced 520 verbatim-locator failures in
`scripts/validate_commitments.py` and two tier-1 test failures. That tripwire is
the system working as designed.

So the corrections cannot be written **into** the lodged text, and this document
is where they live instead: a section-by-section index from a passage of the
registration to the erratum that corrects it. It is a navigation aid, not an
authority — the authoritative record of every deviation, correction and
clarification is [`../protocol-errata.md`](../protocol-errata.md).

**Coverage**: this index is **not** a complete map of the 88-entry errata
register onto the registration. It was created to discharge E87's remediation 1
and covers the passages E86 and E87 correct, plus the adjudications a reader of
those passages needs (E64, E73), and was extended on 2026-09-14 with the
modality passages **E88** corrects. Entries are added on touch, as later errata
land on identified passages.

Line numbers refer to `preregistration.md` at blob `fa221b30f395`, which is the
blob the commitment ledger pins; they are stable for as long as that pin holds.

## Index

| § | Passage | Line | Erratum | What is wrong |
|---|---------|-----:|---------|---------------|
| 2.1 | "**Total**: 361 tiles from 4 annotated Soviet topographic map sheets" | 78 | **E64 (ii)**; noted by **E87** | Corpus size is specified as 361 here and as "~360" in § 8.6. Operative reading: **the 360 physical tiles** (90 per sheet). The Era-1 evaluation frame is those 360 minus the 20 calibration tiles — **340**. E87 records that the paper draft had carried 361 forward without this adjudication. |
| 2.3 | Per-sheet training-tile tables, **Mound Count** and **Density** columns | 106–145 | **E87** | Counts came from a bounding-box approximation of each sheet's georeferencing that never read the raster affine. The **tile filenames are correct** and match `inputs/tiles/calibration_manifest.json` exactly; only the counts are wrong. |
| 2.3 | "**Training set summary**: 20 tiles, 36 mounds total" | 146 | **E87** | **36 is an undercount. The affine-correct figure is 50** distinct reference symbols over the 20 512 px windows (39 over their 448 px cores). |
| 2.4 | Per-sheet holdout tables, same two columns | 154–233 | **E87** | As § 2.3. |
| 2.4 | "**Holdout set summary**: 60 tiles, 79 mounds total" | 234 | **E87** | **79 is an undercount. The affine-correct figure is 97** distinct symbols over the 60 512 px windows (82 over their cores). § 3.2's power discussion quotes this "60 tiles (79 mound symbols)". |
| 2.5 | Density Distribution table (8/7/5 training, 30/18/12 holdout) | 238–246 | **E87** | Derived from the §§ 2.3–2.4 counts, so it inherits their error: under the corrected counts **10 of 20 training and 27 of 60 holdout tiles change stratum**, and **3 training and 12 holdout tiles listed as `empty` are not empty**. The stratified sample is unchanged — these are the strata the registered seeds drew from — so § 2.5 records **how the selection was made**, not the tiles' true mound content. |
| H1 | "**Test**: Compare detection performance across 5 modality/elaboration levels" and the five-level table beneath it | 410–420 | **E88** | The five levels are correctly defined, and H1's own confirmatory contrast groups the five phase-2a conditions correctly. What **E88** corrects is how the factor's value was RECORDED downstream: four analysis scripts assigned it by testing a condition label for the substring `image` rather than reading `include_example_images` over a non-empty exemplar list in the transmitted configuration. Eight conditions and one proposer pool carried a wrong label. No hypothesis-outcome row changes. |
| H1 | "**Text-modality consistency**: Identical text is used across modalities…" | 432 | **E88** | The clause is the reason modality is a property of the *exemplar library* and not of the prompt text or of the map tile (which is always transmitted as an image — it is a vision task). It is therefore the passage that licenses **E88**'s derivation rule, and the passage a reader needs before accepting that a `*-text` label over an image-bearing configuration is mislabelled rather than a different condition. |
| H4 | "`*_canonical-last.json`, `*_random-order.json` … Same instruction file per modality" | 2017 | **E88** | The operative reading of "same instruction file per modality" is that H4's four exemplar-ORDERING variants inherit their arm's configuration, so all four are **image-bearing** (instruction `detect_brief-text-image.md`, `include_example_images` true, `example_count` 13 — read from `outputs/retest/phase2e/canonical-last/run_1/detections_canonical-last_run01.meta.json`). Their labels name neither modality, so the retired substring test fell through to `text` on some artefacts and left them in *neither* group on others — the four `retest-phase2e::` cells are exactly the cells E88's recomputation moves into the image group (17 computable cells → 21). |
| H8 | "**Availability constraint**: The training set contains 36 mounds across 20 tiles. Hard examples are drawn from failures across K=10 baseline runs…" | 815 | **E87** and **E64 (i)** | E87: the 36 is an undercount (50), so the availability constraint this paragraph reasons from — and which it says "motivates H10 (training pool size)" — was looser than stated. The H10 motivation is not reversed, because the binding constraint was the mining campaign's *yield*, but the arithmetic is wrong. E64 (i): "K=10 baseline runs" and the any-run candidacy rule contradict § 8.4.1; operative reading is K=5 passes, any-run hard positives, ≥3-of-5 hard negatives. |
| H10 | "**Constraints**: Total tiles available: 361 … Maximum training pool: ~301 tiles (361 − 60 holdout)" | 936–938 | **E64 (ii)** | The same already-adjudicated corpus figure as § 2.1. Not re-opened by E87. |
| 8.4.2 | Library-composition table, **Null tile** row, "Source: Training set" | 1512 | **E86** | True of the **2025-12-23** training set, false of the committed calibration set. The set was re-selected on 2026-01-04 (`4d011a839`) and none of the three null tiles survived, but `inputs/examples/null-tiles/null_tiles_manifest.json` was never regenerated. The four hard-example categories in the same table are unaffected (all 20 crops' source tiles are committed calibration tiles). |
| 8.4.3 | "**Null tiles** (3 tiles selected via stratified sampling)" — the pool, seed and the three named tiles | 1533–1541 | **E86** | The pool ("Training tiles with density=empty") and seed 20251223 describe the superseded set. Because the evaluation exclusion geometry was built from the *committed* calibration set, these three tiles were never excluded: all three are themselves tiles of the 340-tile Era-1 evaluation frame. The pool criterion also reads the mound counts **E87** corrects, though all three tiles are empty under the corrected geometry too (0 references in each window, both at 512 px and over the 448 px core). |
| 8.6 | "**Reproducibility**: Re-running with same seeds produces identical selection" | 1946 | **E87** | Holds, and is the reason `scripts/select_tiles_phase2.py` is **frozen rather than corrected**: fixing its georeferencing would change the density strata and so change which tiles the registered seeds select. |
| 8.6 | Output Artefacts list | 1948–1953 | **E20 / E73**, **E87** | E20/E73: `holdout_manifest.json` was renamed `validation_manifest.json`, and the script was realigned to write the new name in E73 (2026-08-02), so the path listed is stale but the regeneration command now produces the file the pipeline reads. E87: the listed `tile_selection_metadata.json` carries the superseded per-tile counts and density strata, and labels the 448 px **stride** as `parameters.tile_size`; both are annotated in that file. |

## The null-exemplar exposure, in one place

E86's measured exposure, because a reader arriving from §§ 8.4.2–8.4.3 will want
it without opening the register. Recomputed from the manifests by
`scripts/audit_null_exemplar_overlap.py`; the overlapping tile ids are in
`inputs/examples/null-tiles/null_overlap_by_frame.json`.

| Frame | Tile size | Tiles | Overlapping null-exemplar pixels |
|-------|----------:|------:|---------------------------------:|
| Era-1 `tiles/full_evaluation` | 512 px | 340 | **25** (including all three exemplars themselves) |
| Era-1 `tiles/validation` (the registered holdout) | 512 px | 60 | 3 |
| Era-1 `tiles/verification` | 512 px | 5 | 0 |
| Era-2 `tiles_384/full_evaluation` | 384 px | 487 | 20 |
| Era-2 `tiles_384/validation` | 384 px | 240 | 6 |
| Era-3 `calibration/h10-384/test` | 384 px | 327 | 13 |

No reference symbol lies inside a null window, so no precision, recall, F1 or
Matthews correlation coefficient (MCC) value changes. The exposure is confined
to the image modality: of the 41 configurations that transmit example images,
37 include the three null exemplars and the only four that do not are the
`verify_*.json` verifier configurations; the 22 text-modality configurations
carry the nulls as labels only (`include_example_images: false`), and the 55-map
deployment corpus shares no sheet with the three tiles.

## Corrected counts

The affine-correct per-tile counts for both registered sets are published beside
the lodged tables, clearly labelled as a post-hoc correction, in
[`tile-mound-counts-recomputed-2026-09-13.md`](tile-mound-counts-recomputed-2026-09-13.md)
(with a machine-readable `.json` sibling). Both are generated by
`scripts/recount_prereg_tile_mounds.py` and drift-guarded by its `--check` mode
and a tier-1 test.

## Changelog

### 2026-09-14 — Three modality rows added under erratum E88

**Trigger**: the corpus-wide modality-track audit
([`reports/modality-track-audit-2026-09-14.md`](../../../../reports/modality-track-audit-2026-09-14.md))
and the PI's four rulings of 2026-09-14, ruling 1 of which inserts **E88** and
indexes it here.

| | before | after |
|---|---|---|
| Index rows | 12 | **15** |
| Errata indexed | E20, E64, E73, E86, E87 | **+ E88** |
| Registration passages indexed | §§ 2.1, 2.3, 2.4, 2.5, H8, H10, 8.4.2, 8.4.3, 8.6 | **+ § H1 (`:410–420`, `:432`), § H4 (`:2017`)** |

**What did NOT change**: every pre-existing row is verbatim; no line number was
restated; `preregistration.md` is untouched and still at blob `fa221b30f395`
(the blob `results/commitments.json` pins), so the 702 commitment anchors are
undisturbed. E88 corrects no lodged *text* — the registration's definition of
the modality factor is correct, and what moved is how four analysis scripts
recorded the factor's value.

Commit: this entry's commit.

### 2026-09-13 — Original publication

Created to discharge **E87** remediation 1 after the intended approach —
annotating `preregistration.md` inline with blockquote erratum pointers — was
found to be architecturally forbidden. `results/commitments.json` pins that file
by git blob and anchors 702 commitments to verbatim line ranges inside it; the
inline annotation shifted the line numbers and produced **520**
verbatim-locator failures plus two tier-1 failures in
`tests/test_validate_commitments.py`. The annotations were reverted (the file is
back at blob `fa221b30f395`) and became this companion index instead, which
delivers the same reader-facing guarantee without touching the pinned text.

Initial coverage: the passages E86 and E87 correct (§§ 2.1, 2.3, 2.4, 2.5, H8,
H10, 8.4.2, 8.4.3, 8.6) plus the E64, E20 and E73 adjudications a reader of
those passages needs. Twelve index rows.
