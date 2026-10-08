# Stale register notes resolved, 2026-10-07

> **Last revised**: 2026-10-08 (§ 10 added: the PI's ruling registered
> pv-diag-256's archived pool in place, and the union checker now reproduces
> its union; § 0, § 1c and § 9 item 2 point to it. Before that: 2026-10-07,
> original publication, Session 162). See [§ Changelog](#changelog) for
> revision history.

The record of the stale-register-notes pass (PI request, 2026-10-07),
merged as branch `stale-notes-2026-10-07` (`6da52378c`..`84c75f184`). Written
by the agent that did the work; added here unchanged below this header.

Branch `stale-notes-2026-10-07`, cut from `origin/main` at `5fac69fc5`, pushed
to `origin` (head `84c75f184`). Not merged; nothing pushed to `main`; no pull
request opened. PI approval for the work: 2026-10-07.

All quoted before/after strings below were extracted programmatically from the
pre-change register (`git show 5fac69fc5:results/run-conditions.json`), the
branch's register, the scripts and the regeneration diffs, not retyped.

## 0. Summary

| # | item | status | files | commits |
|---|---|---|---|---|
| 1 | pv-diag-256 passes "not materialised" | **fixed** (append-only) | `results/run-conditions.json` (`_note`, two `_source_run_basis`); `scripts/check_union_provenance.py`; `reports/union-staleness-retrospective-2026-09-12.md`; `reports/register-repair-2026-10-05-investigations/README.md` | `6da52378c`, `262f392ae`, `162af73c5` |
| 2 | verifier-t-pilot T0.0 called an image verifier | **fixed** (append-only) | `results/run-conditions.json` | `719f42c88` |
| 3 | stride ladder rungs "over the full K=10 union" | **fixed** (append-only) | `results/run-conditions.json` (3 conditions in `stride-phaseb-2026-08-25`) | `5546f9740` |
| 4 | K-ladder `operating-points.json` 3.7 K = 3 cell | **STOPPED, not edited** | none | none |
| 5 | pv-diag-384 "No condition cites either" | **fixed** (append-only) | `results/run-conditions.json` | `e8d7d0f27` |
| 6 | session-78 `*-text` `instruction_file` | **fixed** (field in place, note appended; builder fixed) | `scripts/build_gs_era2_board_opmax.py`, `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/membership.json`, `results/run-conditions.json` | `fe874fd41`, `369b767d3` |
| - | propagation through generators | done | `results/conditions-manifest.json` + 5 renderings; 4 `post_run_report.md` | `3b537582b`, `84c75f184` |
| 10 | pv-diag-256's archived pool registered in place (PI ruling, 2026-10-08) | **done** (added; nothing moved) | see § 10 | `20e0be0d3` … `8e343e6e7` |

**Is `results/run-conditions.json` generated?** No. Its `_README` calls it "the
generator's third INPUT", "Authored in archetype batches". The scripts that
write it are one-shot authoring scripts that refuse or no-op on re-run
(`register_pass1_author.py` refuses existing keys; `register_verifier_stage_refresh.py`
and `annotate_partial_run_warns.py` key idempotence on their original sentence
being present; `build_gs_era2_board_opmax.py register` never rewrites an existing
row's `verifier_config`). So the register was edited directly, and every note
correction is **appended** (`" | Corrected 2026-10-07 …"` on run notes, `" Corrected …"`
on condition notes) so the original sentences stay and those scripts still read
as applied. The file round-trips byte for byte with `json.dumps(indent=1)`; each
register commit's diff touches only the edited strings (item 1: 3 lines, item 2:
1, item 3: 3, item 5: 1, item 6: 12). The derived artefacts were then
regenerated through their generators (§ 7).

## 1. pv-diag-256: the passes exist

**Verified at source.** `git ls-files archive/outputs-non-production-tile-sizes/`
lists `text-baseline/text-t0.0/run_1/` and `text-n5/text-t0.7/run_1..5/`, each
with `detections_*.geojson`, `.meta.json` and `.tiles.json`. Metas: baseline
T 0.0, five passes T 0.7, all `detect_brief-text`, `gemini-3-flash`, minimal,
1,032 items. Pass sizes 1,843 / 1,859 / 1,829 / 1,838 / 1,856. sha256 of
`outputs/h11/pv-diag-256/consensus/text-baseline.geojson` equals that of the
archived baseline pass's detections (`bf44bc7b11e3b3f3…`, re-checked locally).
Union feature counts `text-1of5..5of5` = 2,558 / 1,909 / 1,645 / 1,423 / 1,165,
matching PR #25's reproduction in binding `pv-diag-256-text-5of5-union`.
Commits `3d22184d6` (tracked at the live path), `276e4ca80` (archived;
`git show --name-status` shows the archive pass files as added there),
`bd24293d4` (re-added at the live path) confirmed.

### 1a. `results/run-conditions.json`, `decomposition.pv-diag-256._note` (`6da52378c`)

Stale sentence (kept):

> Proposer passes were NOT materialised as run_* dirs (only consensus + crops), so proposer_pools is empty and conditions reference the pool by string (benign pool-unresolved; pv-384/512 precedent).

Appended:

> | Corrected 2026-10-07 (stale register notes, PI-approved; reviewed bindings pv-diag-256-text-baseline and pv-diag-256-text-5of5-union in results/manipulation-gate-bindings.json): 'Proposer passes were NOT materialised as run_* dirs' above is wrong. They were materialised, and they are tracked with their metas under archive/outputs-non-production-tile-sizes/, where 276e4ca80 (2026-04-16) archived them from outputs/h11/pv-diag-256/: the N=1 T=0.0 baseline pass at text-baseline/text-t0.0/run_1 and the five N=5 T=0.7 passes at text-n5/text-t0.7/run_1..run_5 (detect_brief-text, gemini-3-flash, MINIMAL, 1,032 tiles each). consensus/text-baseline.geojson is byte-identical to the baseline pass's detections (sha256 bf44bc7b11e3...), and a read-only reproduction from the five T=0.7 passes gives the feature counts of text-1of5..text-5of5 and the coordinates of text-5of5 exactly. proposer_pools stays empty only because no registered pool spec reaches archive/; registering one is a separate decision. No metric, eval or detection changed.

### 1b. Same file, both conditions' `_source_run_basis` (`text-baseline`, `text-consensus-5of5`; same commit)

Not in the brief's list, but the same false claim in the same run entry.

Before:

> proposer passes not materialised as run_* dirs; only outputs/h11/pv-diag-256/consensus/ exists — stated in the run's `_note`

Appended:

> . Corrected 2026-10-07: the passes were materialised as run_* dirs; they are tracked, with their metas, under archive/outputs-non-production-tile-sizes/ (text-baseline/text-t0.0/run_1; text-n5/text-t0.7/run_1..run_5), archived there by 276e4ca80. source_run pv-diag-256 is unchanged; see the run's `_note`.

### 1c. `scripts/check_union_provenance.py` lines 169-177 → 169-186 (`262f392ae`)

Before:

```python
#: union directory -> why its parameters are not recoverable.
UNRESOLVABLE: dict[str, str] = {
    # Anchor: results/run-conditions.json, decomposition.pv-diag-256.`_note` —
    # "Proposer passes were NOT materialised as run_* dirs (only consensus +
    # crops), so proposer_pools is empty".
    "outputs/h11/pv-diag-256/consensus":
        "proposer passes were never materialised as run_*/pass_* directories "
        "(results/run-conditions.json, decomposition.pv-diag-256.`_note`)",
}
```

After:

```python
#: union directory -> why this checker does not re-derive it.
UNRESOLVABLE: dict[str, str] = {
    # Anchor: results/manipulation-gate-bindings.json, binding
    # pv-diag-256-text-5of5-union (PR #25), and the correction appended to
    # results/run-conditions.json, decomposition.pv-diag-256.`_note`, on
    # 2026-10-07. Until then this entry said the proposer passes were never
    # materialised. They were: 276e4ca80 archived the five N = 5, T = 0.7
    # passes, tracked with their metas, at
    # archive/outputs-non-production-tile-sizes/text-n5/text-t0.7/run_1..5.
    # The entry stays because no registered pool reaches archive/ and
    # POOL_OVERRIDES maps only registered pools. The binding records a
    # read-only reproduction from those passes that matches the union exactly.
    "outputs/h11/pv-diag-256/consensus":
        "pool not registered: its five passes sit outside the union's run, at "
        "archive/outputs-non-production-tile-sizes/text-n5/text-t0.7/run_1..5 "
        "(archived by 276e4ca80); provenance settled by binding "
        "pv-diag-256-text-5of5-union (results/manipulation-gate-bindings.json)",
}
```

Behaviour deliberately unchanged (classification stays UNRESOLVED). Moving the
entry to `POOL_OVERRIDES` would let the checker reproduce the union, but it
empties `UNRESOLVABLE`, which `tests/test_check_union_provenance.py::test_documented_unresolvable_dirs_are_declared_not_guessed`
forbids ("the table should not be silently emptied"), and it is the same
"register the archived pool" decision the note leaves to the PI. 11/11 tests in
that file pass.

Superseded 2026-10-08: the PI ruled to register the pool in place, and the
entry moved to `POOL_OVERRIDES`, with the test changed deliberately (§ 10).

### 1d. `reports/union-staleness-retrospective-2026-09-12.md` (`162af73c5`)

Body edited in place, banner and changelog per the revision policy.

| where | before | after |
|---|---|---|
| banner | `Last revised: 2026-09-12 (later — …)` | `Last revised: 2026-10-07 (§ 5 corrected: the pv-diag-256 pool this report called non-existent is archived and tracked, and a read-only reproduction from it matches the UNRESOLVED union exactly. …)` |
| verdict | ends "… with `n_passes: 30`." | adds "The UNRESOLVED union's pool has since been found under `archive/`, and a read-only reproduction from it matches the union exactly (§ 5, corrected 2026-10-07); the sweep's own classification is unchanged." |
| § 5 | "It cannot be re-derived because **the pool does not exist**." … "and they may not exist anywhere." | pool outside the union's run and unregistered; passes archived and tracked (paths, counts); PR #25's exact reproduction (2,558 / 1,909 / 1,645 / 1,423 / 1,165); classification stays UNRESOLVED and why |
| § 5 | "(E62)" flag attributed to "the register note" | attributed to `results/run-facts.json`, `pv-diag-256.purpose` (re-verified: the phrase is there, not in the `_note`) |
| § 6 row | `UNRESOLVED` | `UNRESOLVED (pool since found; § 5)` |
| changelog | — | new `2026-10-07` entry with a before→after table and "what did NOT change" |

`results/union-staleness-retrospective-2026-09-12.json` is the 2026-09-12 sweep's
verbatim output and keeps its old `detail` string (stated in the changelog).

### 1e. `reports/register-repair-2026-10-05-investigations/README.md` (`162af73c5`)

PR #25's binding caveat also names `d31-other-legs.md:152-153` ("`pv-diag-256` has
no proposer meta"). That folder's README declares the four files "working records,
not findings of record" and lists known supersessions, so the record itself was
left untouched and the README's "One known case" became "Two known cases", adding:

> `d31-other-legs.md` § 4 says "`pv-diag-256` has no proposer meta". That holds only for `outputs/` and `results/`, the trees the survey's `cost_audit.json` sidecars cover (its item 5). The run's six proposer passes, with their metas, are tracked under `archive/outputs-non-production-tile-sizes/` (`text-baseline/text-t0.0/run_1`, `text-n5/text-t0.7/run_1..5`), archived there by `276e4ca80`. Pull request #25's reviewed bindings `pv-diag-256-text-baseline` and `pv-diag-256-text-5of5-union` (`results/manipulation-gate-bindings.json`) are the verified account.

Banner and changelog (with an "Original publication" stub) added.

## 2. verifier-t-pilot: the T0.0 baseline ran text (`719f42c88`)

**Verified at source.** The T0.0 arm has no stage of its own;
`outputs/verifier-t-pilot/T0.0/` holds only `materialised/`. Binding
`vtpilot-t0-0` and `scripts/run_verifier_t_stage_b.py` route it to
`outputs/gs/gold-standard-v2/verified-v1/probabilities.json`. That stage's
`run.meta.json` today (cleanup leg, 2026-05-03) and as committed at `a01858e53`
(request leg, started 2026-04-10T04:21Z) both record `version
verify_adversarial-text`, `instruction_file verify_adversarial.md`,
`example_count 0`; the request leg used 1,069,824 input tokens = 597 × 1,792.
T0.5 and T1.0 metas record the same version, file and example_count,
1,087,744 tokens = 607 × 1,792 each. Probabilities: T0.5 and T1.0 607; the gs-v2
file 608 today (597 at the product commit, per the binding). `results/run-facts.json`
does not repeat the confound claim.

Stale clause (kept):

> the T0.0 baseline is gs-v2's IMAGE verifier whereas T0.5/T1.0 use the text verifier (verify_adversarial-text) -> temperature/modality partly confounded

Appended to `decomposition.verifier-t-pilot._note`:

> | Corrected 2026-10-07 (stale register notes, PI-approved; reviewed binding vtpilot-t0-0 in results/manipulation-gate-bindings.json): the CAVEATS clause above is wrong on modality. The T0.0 baseline, gold-standard-v2's verified-v1, ran the TEXT verifier: its run.meta.json records configuration.version verify_adversarial-text, instruction_file verify_adversarial.md and example_count 0, in both the request leg (started 2026-04-10, as committed at a01858e53; 1,069,824 input tokens = 597 x 1,792) and the 2026-05-03 cleanup leg. T0.5 and T1.0 record the same version, instruction file and example_count (1,087,744 input tokens = 607 x 1,792 each). The three arms share one verifier configuration except temperature, so temperature is NOT confounded with modality. (They do differ in coverage: T0.0's probabilities held 597 results when its product was materialised, T0.5 and T1.0 hold 607.) The self-eval-bias caveat stands. gold-standard-v2's own `_note` (AMENDED 2026-10-05, tracker C-18) relabels verified-v1 text.

## 3. Stride ladder rungs read their own `verify_kN` (`5546f9740`)

**Where the notes are.** Not in `stride-55map-2026-08-25`: that run's four
"over the full K=10 union" notes sit on `n_passes: 10` conditions and are
correct, and its N < 10 rungs already say "probabilities inherited from K=10".
The stale notes are the three winner-ladder rungs of `stride-phaseb-2026-08-25`
(the rows PR #25's bindings `stride-g384ov128-ladder-n{1,3,5}` flag). The other
"full K=10 union" notes in that run and in `stride-phasec-2026-08-25` sit on
K = 10 cells and are correct. `results/stride-2026-08-25/findings.md` does not
repeat the claim.

**Verified at source.** `scripts/register_pass1_materialise.py:75-88` (`rung(n)`)
joins `outputs/stride-phaseb-2026-08-25/verifier/g384_ov128/union_k{n}.geojson` to
`verify_k{n}/probabilities.json`. Unions 1,290 / 1,700 / 1,968 features; each
`verify_k{n}` holds the same number of results and its meta records the same
number of items processed; K = 10 `verify` processed 2,387. All four metas record
`verify_adversarial-text`, `verify_adversarial.md`, T 0.0, minimal,
example_count 0. Register stages `g384_ov128-union-k{1,3,5}-verify` exist with
those paths.

Before (rung n1; n3 and n5 differ only in "first-3 … 0.8911, union 1700" and
"first-5 … 0.8856, union 1968"):

> Winner-ladder exact rung (first-1 passes, exact re-verification; F1@20 0.8677, union 1290). Carry-forward verifier (verify_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.

Appended (n1; n3 and n5 substitute `k3`/`k5`, `union_k3`/`union_k5` and the
binding id):

> Corrected 2026-10-07 (stale register notes, PI-approved; reviewed binding stride-g384ov128-ladder-n1): 'over the full K=10 union' is wrong for this rung. It read its own exact re-verification, verifier/g384_ov128/verify_k1/probabilities.json over union_k1.geojson (register stage g384_ov128-union-k1-verify; scripts/register_pass1_materialise.py rung()), not the K=10 union's verify stage. The verifier configuration is the same carry-forward one.

Generator source not changed: `scripts/register_pass1_author.py:54-55`
(`CARRY_NOTE`) wrote the sentence, but that one-shot script refuses to run once
its keys exist, so it cannot overwrite the register; editing it would rewrite
its historical record for no effect.

## 4. K-ladder `operating-points.json`, 3.7 K = 3 cell: STOPPED

**Verified stale.** `results/k-ladder-2026-09-12/phase2/operating-points.json`
row 28 records `verifier_stage g384_ov192_g37-union-k3-verify`, `verify_dir …/verify_k3`,
`candidates 757`, opmax `sweep_f1_20 0.887`, `sweep_n 494`, `n_detections 494`.
The live product `materialised/g37-text-k3-verified-opmax.geojson` has 495
features (installed by `987534c03`) and binding
`g37-kladder-k3-verify-k3-recovery-fixed` resolves it to `verify_k3_recovery-fixed`
(756 carried + 3 fresh results) over the rebuilt 759-feature `consensus-n3`.

**Generated?** Yes, by `scripts/score_k_ladder_phase2_rungs.py prepare`
(`script` field; the generated-file registry covers Markdown only, so it is not
listed there). Row 27 (K = 1) is NOT stale: binding `g37-kladder-k1-verify-k1`
says both live K = 1 products still read `verify_k1`.

**Regeneration, run on sapphire in two disposable copies** (`prepare --row 28
--sweep-workers 2`, sapphire's `.venv` Python; copies deleted afterwards;
sapphire's checkout untouched, still at `439ffd7ac`):

(a) Builder as committed: the row stays on `verify_k3` and becomes internally
inconsistent: the sweep (over `crops_k3`, the pre-fix 757 candidates) still
says 494 / 0.887, while materialisation (verify_k3's probabilities joined by
index to the rebuilt 759-feature union) gives 495. It does not fix the cell.

```diff
2c2
<   "generated_at_utc": "2026-09-12T08:39:20+00:00",
---
>   "generated_at_utc": "2026-10-07T01:54:04+00:00",
1268c1268
<       "candidates": 757,
---
>       "candidates": 759,
1282c1282
<         "n_detections": 494,
---
>         "n_detections": 495,
1297c1297
<         "n_detections": 494,
---
>         "n_detections": 495,
```

(b) Builder with `STAGE_OVERRIDES[…g384_ov192_g37][3]` in
`scripts/run_k_ladder_phase2_verifier.py:130-141` pointed at
`verify_k3_recovery-fixed` / `crops_k3_recovery-fixed` /
`g384_ov192_g37-union-k3-verify-recovery-fixed` (scratch copy only). This
yields the correct cell; within `operating-points.json` only row 28 and the
timestamp change:

```diff
2c2
<   "generated_at_utc": "2026-09-12T08:39:20+00:00",
---
>   "generated_at_utc": "2026-10-07T01:55:40+00:00",
1268,1270c1268,1270
<       "candidates": 757,
<       "verifier_stage": "g384_ov192_g37-union-k3-verify",
<       "verify_dir": "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k3",
---
>       "candidates": 759,
>       "verifier_stage": "g384_ov192_g37-union-k3-verify-recovery-fixed",
>       "verify_dir": "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k3_recovery-fixed",
1272,1273c1272,1273
<       "sweep_board_frame": "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k3/sweep_2d_era2b.json",
<       "sweep_era2_frame": "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k3/sweep_2d.json",
---
>       "sweep_board_frame": "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k3_recovery-fixed/sweep_2d_era2b.json",
>       "sweep_era2_frame": "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k3_recovery-fixed/sweep_2d.json",
1278,1279c1278,1279
<         "sweep_f1_20": 0.887,
<         "sweep_n": 494,
---
>         "sweep_f1_20": 0.886,
>         "sweep_n": 495,
1282c1282
<         "n_detections": 494,
---
>         "n_detections": 495,
1289,1290c1289,1290
<         "sweep_f1_20": 0.887,
<         "sweep_n": 494
---
>         "sweep_f1_20": 0.886,
>         "sweep_n": 495
1297c1297
<         "n_detections": 494,
---
>         "n_detections": 495,
```

In both runs the materialised geojson and the stage sweep files came out
byte-identical to the committed ones.

**Why I stopped.** Neither path regenerates only the stale cell.

- Path (a) does not fix the cell (it keeps `verify_k3`) and makes the row
  internally inconsistent.
- Path (b) needs a builder source change, and `STAGE_OVERRIDES` is shared:
  - the verifier launcher (`verify_rung`) uses it as the directory the
    2026-09-12 run wrote, and `--skip-done` uses it as the ledger key;
  - `--recompute-ledger` would re-book row 28 from the 3-call recovery leg's
    meta and drop the 757-call leg's cost;
  - `register_k_ladder_phase2_conditions.py` uses it as the stage it registers;
  - `tests/test_k_ladder_phase2.py::test_g37_rungs_use_the_screens_own_verifier_tree`
    pins `verify_k3` for K = 3.
- Both paths rewrite `phase2/score-jobs.txt` wholesale: 46 lines become 1.

A clean fix needs a separate override for the scoring step only (a
"live-product stage" map read by `score_k_ladder_phase2_rungs.py` and
nothing else). That is a design decision, so I left it. The file is unedited.

## 5. pv-diag-384: a recovery stage is now cited (`e8d7d0f27`)

**Verified at source.** `pv-high-text-t0.0-n3-recovery-2026-09-08-opmax` was
registered at `5d860ede3` (2026-09-12) and its board cell `…-opmax-era2b` at
`7ea38de6e` (2026-09-12). Binding `current-vintage-pv-high-text-t0.0-n3-recovery`
resolves both to stage `flash-high-text-n5-text-t0.0-verified-v1-n3-recovery-2026-09-08`.
The image stage `flash-high-image-n5-image-t0.0-verified-v1-n10-recovery-2026-09-08`
appears in no condition, binding or analysis (it appears only in `verifier_passes`
and `passes-manifest.json`). The parallel `e47-propose-brief` "No condition cites
either" was checked and is still true, so it was left.

Stale sentence (kept, because `register_verifier_stage_refresh.py`'s idempotence
checks `note in current`): "… into the '-recovery-2026-09-08' directories
registered here as inventory rows beside the originals, which stay as the
pre-recovery record. No condition cites either. …"

Appended to `decomposition.pv-diag-384._note`:

> | Corrected 2026-10-07 (stale register notes, PI-approved): 'No condition cites either' in the verifier-stage refresh entry above is out of date for the text stage. Since 2026-09-12, flash-high-text-n5-text-t0.0-verified-v1-n3-recovery-2026-09-08 is read by two conditions of this run: pv-high-text-t0.0-n3-recovery-2026-09-08-opmax (registered at 5d860ede3; PI rulings B2 and R4, planning/k-ladder-review-2026-09-11.md section 4) and its board cell pv-high-text-t0.0-n3-recovery-2026-09-08-opmax-era2b (added at 7ea38de6e); reviewed binding current-vintage-pv-high-text-t0.0-n3-recovery in results/manipulation-gate-bindings.json. The image stage flash-high-image-n5-image-t0.0-verified-v1-n10-recovery-2026-09-08 is still cited by no condition.

## 6. session-78 `*-text` instruction files (`fe874fd41`, `369b767d3`)

**Verified at source.** `prompts/system-instructions/` holds
`verify_adversarial.md`, `verify_adversarial_v2.md`, `verify_brief.md`,
`verify_checklist.md` and `verify_comparative.md`, and no `*-text.md`. For all
six stages (`outputs/h11/pv-diag-384/flash-high-{text,image}-n5/{text,image}-t0.7/session-78-matrix/verified-{checklist,adversarial,brief}-text/`)
both legs' metas were read: the current `run.meta.json` (last leg `414ee8a4b`)
and the earlier leg via `git show` (`5cee158bc`, `96a6ac235`, `bd0a4d091`,
`f36e7bef9`, `35b380a6d` and `e85c62902`). Every one records
`instruction_file verify_<x>.md`, `version verify_<x>-text` and
`example_count 0`.

**Generator.** The rows were minted by `scripts/build_gs_era2_board_opmax.py
register` from `membership.json`. The wrong strings came from that script's
`S78_VARIANT_FILES` (lines 159-162). That map is fixed, with a comment, in
`fe874fd41`. `membership.json` was regenerated through the builder's
`membership` subcommand: an unmodified rerun changes only `derived_at_utc`, and
the fixed rerun changes exactly the six `instruction_file` strings plus
`derived_at_utc`. `register` does not rewrite existing rows' `verifier_config`,
so the six register rows were edited in `369b767d3`.

| condition (`pv-diag-384::`) | `instruction_file` before | after |
|---|---|---|
| `session-78-text-checklist-text-opmax` | `verify_checklist-text.md` | `verify_checklist.md` |
| `session-78-text-adversarial-text-opmax` | `verify_adversarial-text.md` | `verify_adversarial.md` |
| `session-78-text-brief-text-opmax` | `verify_brief-text.md` | `verify_brief.md` |
| `session-78-image-checklist-text-opmax` | `verify_checklist-text.md` | `verify_checklist.md` |
| `session-78-image-adversarial-text-opmax` | `verify_adversarial-text.md` | `verify_adversarial.md` |
| `session-78-image-brief-text-opmax` | `verify_brief-text.md` | `verify_brief.md` |

Each row's `_note` gains a dated record of the change (example, the first row):

> Corrected 2026-10-07 (stale register notes, PI-approved; reviewed binding s78-text-checklist-text): verifier_config.instruction_file read 'verify_checklist-text.md', a file that does not exist in prompts/system-instructions/. Both legs' run.meta.json for the stage record instruction_file 'verify_checklist.md' with configuration.version 'verify_checklist-text' and example_count 0, so the field now reads 'verify_checklist.md'; verifier_config.variant keeps the text-only configuration distinct from the image one.

## 7. Propagation through generators

- **Manifests (`3b537582b`).** I ran `generate_post_run_report.py --all --write`
  on sapphire in a disposable clone of the branch at `369b767d3` and copied the
  outputs back. `conditions-manifest.json` changes in exactly the rows whose
  input changed: nine `caveat` strings (3 ladder rungs, 6 session-78 rows) with
  their `last_extracted_at`, the six `instruction_file` strings, and
  `generated_at`. The other manifests' JSON is unchanged; their five `.md`
  renderings change only in the source-commit stamp. `--check-renderings`:
  "5 register rendering(s) current".
- **Run reports (`84c75f184`).** `generate_run_reports.py --check` flagged four
  reports as stale: `outputs/h11/pv-diag-256/`, `outputs/h11/pv-diag-384/`,
  `outputs/stride-phaseb-2026-08-25/` and `outputs/verifier-t-pilot/`
  `post_run_report.md`. I regenerated them on sapphire and committed only those
  four. The other 36 differed by their stamp alone, which `--check`
  neutralises. Their diffs carry the appended corrections and the new stamp.
  After the commit `--check` reads "all 40 generated post-run report(s) up to
  date".
- **`scripts/verify_run_conditions.py`** gives byte-identical output before
  (register at `5fac69fc5`) and after: "44 run(s): 41 pass, 3 partial, 0 fail".

## 8. Tests and lint

- **Pinned tests, tier 1.** These are the tests that reference the touched
  files (`test_lib_manipulation_signature`, `test_selection_aware_intervals`,
  `test_uplift_supplement_builders`, `test_evaluate_detections_metadata`,
  `test_check_union_provenance`, `test_author_e43_matched_temperature`,
  `test_era1_leaderboard_tiering`, `test_r2_chain_hardenings`, `test_lib_pass_cost`,
  `test_generate_post_run_report`, `test_manifest_vote_gate`,
  `test_k_ladder_closeout` and `test_k_ladder_board_admission`). I ran them
  locally after the first register edit:
  `587 passed, 3 deselected in 114.30s (0:01:54)`. The final full suite
  includes them.
- **Full tier-1 suite.** Run on sapphire against the final head `84c75f184`
  (`python -m pytest -m tier1 -q -p no:cacheprovider`):
  `= 1 failed, 3875 passed, 5 skipped, 53 deselected, 3 xfailed, 4 warnings in 250.97s (0:04:10) =`.
  - The failure, `tests/test_build_generated_file_registry.py::test_committed_registry_matches_a_rebuild`,
    **predates this branch**. At base `5fac69fc5` that file gives
    `1 failed, 19 passed, 2 deselected`.
  - Its whole drift is one new file,
    `reports/w27-replicate-floors-2026-10-06-scripts/verifier-date-tm-check.md`.
    It was added at `3a1ce64eb` (2026-10-06 23:03), after the registry's last
    rebuild at `3d8018315` (19:37). I did not rebuild the registry because the
    document belongs to another workstream.
  - Before the run-report commit, the suite had a second failure
    (`test_generate_run_reports.py::test_no_drift_in_committed_reports`). That
    was my own drift, and `84c75f184` fixed it.
- **Lint.**
  - Ruff, under the branch's config: `ruff check` passes on
    `scripts/check_union_provenance.py` and `scripts/build_gs_era2_board_opmax.py`.
  - Ruff, under the new `ruff.toml` that landed on `main` after this branch's
    base (`79dac1f34`, E501 enforced): `check_union_provenance.py` is clean, but
    `build_gs_era2_board_opmax.py` has **71 pre-existing E501 lines**. None is
    mine (my lines are at most 81 characters). Fixing them would be an
    unrelated mechanical diff of 71 lines, so I left them. Under the new "fix on
    touch" rule they are due when this PR lands.
  - `npx markdownlint-cli2`: 0 errors on the retrospective, the README and the
    four run reports.

## 9. Left undone, and why

1. **Item 4** (§ 4): stopped by the brief's rule. It needs a scoring-only
   stage override; that is a design decision.
2. **Registering the archived pv-diag-256 pool** (so that
   `check_union_provenance.py` reproduces the union itself): a PI decision. It
   changes checker behaviour, and a tier-1 test. Decided 2026-10-08 (register
   in place) and done: § 10.
3. **Other copies of stale claims, outside PR #25's list.** I left these
   unedited:
   - `reports/documentation-batch1-deltas-2026-09-13.md:205` and
     `reports/w27-replicate-floors-2026-10-06-scripts/claims-inventory-2026-10-06.md:244`
     repeat "passes not materialised". The second belongs to an active
     workstream.
   - Downstream derived snapshots still carry the old strings:
     - `results/uplift-supplement/conditions.csv` and
       `conditions-by-buffer.csv`: the three ladder caveats;
     - `results/k-ladder-2026-09-12/inventory.json`: six `instruction_file`
       strings (built from the manifest by `build_k_ladder_inventory.py`);
     - the frozen `tiering-input/run-conditions.json` copies under
       `results/null-exemplar-sensitivity-2026-09-13/` and
       `results/k-ladder-2026-09-12/tiering-input/gs-stride-a/`;
     - `reports/verification/c3-rederivation/rederivation-report.json`.

     These are dated analysis inputs or outputs. No drift test covers them.
4. **One-shot authoring scripts' source strings** were left unchanged:
   - `register_pass1_author.py` `CARRY_NOTE`;
   - `register_verifier_stage_refresh.py` `NOTES`;
   - `annotate_partial_run_warns.py`, the pv-diag-256 anchor.

   Appending kept their idempotence, and editing them would make a rerun
   append duplicates.
5. **A surprise to flag (not investigated).** In
   `results/k-ladder-2026-09-12/phase2/operating-points.json`, all 28 rungs'
   board-frame sweep (`sweep_2d_era2b.json`) and Era-2-frame sweep
   (`sweep_2d.json`) are byte-identical, so `frames_agree_on_argmax: true`
   holds trivially. The two bounds files differ: 487 tiles each, but the
   symmetric difference of their footprints is about 13.4 km², roughly 1 % of
   the area. It may be benign, if no detection or reference mound falls in
   the sliver, but someone should check before a claim leans on "the frames
   agree".
6. **Scratch.** I deleted all sapphire scratch copies
   (`/tmp/w27-oprepro-20261007`, `~/cc-scratch/w27-stale-notes-20261007`).
   The regeneration diffs are kept beside this report (`op-asis.diff`,
   `op-patched.diff`).

## 10. pv-diag-256 registered in place (PI ruling, 2026-10-08)

Added 2026-10-08 by the agent that did the work, on branch
`worktree-agent-a462722af99b42e8c`, cut from `16d41b494`. It settles § 9 item 2.

**The ruling.** The Session 162 close recommended "register pv-diag-256 in
place" (`planning/paper-writeup-continuity.md`, S162 block, item 5, "Decisions
waiting"). The PI approved it on 2026-10-08.

**What "in place" meant at source.** The register already had the mechanism.
A pool spec may name `repo_path`, a repository-relative root that stands in for
the run directory: ruling D32 for verifier legs, D41 for proposer pools
(`scripts/generate_post_run_report.py`, `_leg_root`). h10's
`coldstart-pool_160` uses it for passes archived under
`archive/intermediate-calibration/`. Registering in place therefore meant
adding pool specs whose root is `archive/outputs-non-production-tile-sizes`.
Nothing about that was ambiguous. No file moved, and no committed condition,
evaluation, detection or figure changed.

**Verified at source before acting.**

- `git ls-files` lists the six pass directories, each with its detections,
  `.meta.json` and `.tiles.json`. The metas record `detect_brief-text`,
  `gemini-3-flash`, thinking `minimal`, 1,032 items, T 0.0 for the baseline
  and T 0.7 for the five passes, and `include_example_images: false`. Pass
  sizes: 1,828 (baseline); 1,843 / 1,859 / 1,829 / 1,838 / 1,856.
- `3d22184d6` (2026-04-15), `276e4ca80` (2026-04-16) and `bd24293d4`
  (2026-04-19) are the commits § 1 describes.
- The baseline pass's detections and `consensus/text-baseline.geojson` share
  sha256 `bf44bc7b11e3b3f3…`. The archived and live copies of
  `text-{1..5}of5.geojson` are byte-identical.
- Re-derived with the checker's own functions from the five T = 0.7 passes:
  2,558 / 1,909 / 1,645 / 1,423 / 1,165 features at ≥ 1 … 5 votes, the
  committed counts, with no unmatched feature at 1 m either way. The in-memory
  EPSG:32635 vote-5 centroids equal `text-5of5.geojson`'s coordinates exactly.

**Two choices, each with its precedent.**

1. *Two pools, not one.* The keys follow pv-diag-384, which registers the same
   layout as `text-baseline-text-t0.0` and `text-n10-text-t0.7`. The union's
   pool alone would have satisfied the checker, but
   `scripts/check_manipulation.py` (`proposer_metas_for_condition`) falls back
   to a run's sole pool when nothing else binds a condition. With one pool it
   would have bound the T = 0.0 baseline condition to the T = 0.7 passes.
2. *Conditions unchanged.* Both still name `proposer_pool: "text"` with
   `source_run: pv-diag-256`. pv-diag-384's baseline conditions do the same,
   naming `text-baseline` beside the registered `text-baseline-text-t0.0`.
   Re-pointing them would rewrite committed condition fields (left undone,
   below).

**What changed.**

| file | change | commit |
|---|---|---|
| `results/run-conditions.json` | `pv-diag-256.proposer_pools`: `{}` → two specs at `repo_path` `archive/outputs-non-production-tile-sizes`; dated append to the run's `_note` | `20e0be0d3` |
| `results/manipulation-gate-bindings.json` | dated append to the caveats of `pv-diag-256-text-baseline` and `pv-diag-256-text-5of5-union` | `20e0be0d3` |
| `scripts/check_union_provenance.py` | union moved from `UNRESOLVABLE` (now empty) to `POOL_OVERRIDES`; comparison reads EPSG:32635 as well as WGS84; a union in any other declared CRS is UNRESOLVED; v1.1.0 | `303fbd3d2` |
| `tests/test_check_union_provenance.py`; new `tests/test_check_union_provenance_committed.py` (tier 2) | guard test changed deliberately; registration, frame and CRS tests; the five committed unions re-derived | `303fbd3d2` |
| `scripts/generate_run_reports.py`, `tests/test_generate_run_reports.py` | § 9.1 of a run report no longer places a `repo_path` pool inside the run directory | `a710152d1` |
| `results/passes-manifest.json` and the five register renderings; `outputs/h10/post_run_report.md`, `outputs/h11/pv-diag-256/post_run_report.md` | regenerated | `e5f702d2c` |
| 729 `cost_audit.json` sidecars, `data/pricing/archive-executions.json` | register stamp only | `8e343e6e7` |
| this report, `reports/union-staleness-retrospective-2026-09-12.md`, and the re-run's output beside this report | record | the commit that adds this section |

The `_note` append, verbatim:

> Registered in place 2026-10-08 (PI ruling 2026-10-08, approving the Session 162 close's recommendation 'register pv-diag-256 in place', planning/paper-writeup-continuity.md; record: reports/stale-register-notes-2026-10-07.md section 10): 'proposer_pools stays empty' in the 2026-10-07 correction above is superseded. The six archived passes are registered where they lie, and no file moved: proposer_pools text-baseline-text-t0.0 (the N=1 T=0.0 baseline pass) and text-n5-text-t0.7 (the five N=5 T=0.7 passes) name repo_path archive/outputs-non-production-tile-sizes, the mechanism h10's coldstart-pool_160 uses (ruling D41); the keys follow pv-diag-384's names for the same layout. Their metas record no token usage (Batch API), so their passes-manifest rows carry cost_usd null with basis unrecorded (ruling D12). The conditions are unchanged: both still name proposer_pool 'text' with source_run pv-diag-256, as pv-diag-384's baseline conditions name theirs beside registered pools. scripts/check_union_provenance.py now re-derives consensus/ from text-n5-text-t0.7 (POOL_OVERRIDES) and reproduces text-1of5..text-5of5 exactly (2,558 / 1,909 / 1,645 / 1,423 / 1,165 features). No metric, eval or detection changed.

The binding caveats gain a shorter dated note to the same effect. Each adds
that the condition still names pool `text`, so the binding still supplies the
proposer route. The gate confirms it: the routes now read
`binding:pv-diag-256-text-baseline:passes-manifest:pv-diag-256/text-baseline-text-t0.0`
and the five-source equivalent for the union.

**Two defects found on the way, both fixed.**

1. *The checker could not compare these unions at all.* The 256 plan's own
   builder wrote them in EPSG:32635, with a `crs` member. Every union the
   2026-09-12 sweep compared was a WGS84 `merge_passes.py` output, and
   `_utm_points` projected every point as degrees. Moving the table entry alone
   would have crashed on this union with
   `ValueError: cannot convert float NaN to integer`. Projected points now pass
   through (`merge_passes.coords_are_geographic` decides). The largest matched
   offset, 0.068 m, comes from the `geojson` library's six-decimal precision on
   `apply_threshold`'s WGS84 output; the pyproj round trip alone is
   nanometres. That is what the 1 m tolerance is for.
2. *Generated run reports placed `repo_path` pools inside the run directory.*
   § 9.1's column header reads "Path within the run directory", and the cell
   printed the bare `path`. h10's report has said `pool_160` lies inside
   `outputs/h10` since D41, and pv-diag-256's would have done the same. The
   cell now gives the repository path. The header is unchanged, so only those
   two reports re-render.

Every new test was confirmed red without its fix. The cases: override removed,
table refilled, frame handling removed, CRS guard removed, and the committed
renderer.

**Regeneration and checks.** All of them ran on sapphire, in a disposable clone
of the branch, with sapphire's `.venv`.

- `generate_post_run_report.py --all --write`: `ALL VALID (44 runs + 658
  conditions + 1455 passes + 71 analyses vs schemas)`. The passes register
  gains exactly the six rows (1,449 → 1,455), each `cost_usd` null, basis
  `unrecorded`, and a new `generated_at`. The runs, conditions and analyses
  JSONs are unchanged. `run_type` stays `mixed`. `--check-renderings`: 5
  current.
- `generate_run_reports.py --check`: all 40 up to date after re-rendering
  pv-diag-256 and h10. pv-diag-256's report now lists the six passes and gives
  its total as "at least US$0.7990; no ceiling (6 unrecorded pass(es))".
- `verify_run_conditions.py`: `44 run(s): 41 pass, 3 partial, 0 fail`, as in
  § 7.
- `derive_condition_modality.py --check`: exit 0.
- `backfill_cost_audit_sidecars.py` and `build_archive_ledger.py`: each sidecar
  and the ledger records the register's `generated_at`, so all 729 sidecars and
  the ledger went stale on the stamp alone. Their content otherwise equals a
  rebuild, checked file by file with the stamp removed. Both were rewritten.
  The 98 sidecars `--write` also created are not committed. They are for new
  metas of three 2026-10-07 workstreams (`modality-bridge` 86,
  `temperature-probe` 8, `verifier-date` 4), were already missing at the base
  commit, and belong to those workstreams.
- Full tier 1, at head `8e343e6e7`:
  `= 1 failed, 4038 passed, 5 skipped, 59 deselected, 3 xfailed, 4 warnings in 269.36s (0:04:29) =`.
  The failure,
  `test_build_generated_file_registry.py::test_committed_registry_matches_a_rebuild`,
  predates the branch. The base commit `16d41b494` both rebuilt the registry
  and added `reports/s163-agent-records/run-b-floors-audit.md` without
  registering it, and a rebuild differs by that file alone. It is left for the
  run-b workstream.
- Tier 2: `4 failed, 51 passed, 2 skipped`. The new module passes at all five
  thresholds. All four failures predate the branch. Three fail identically with
  the base commit's register files swapped in
  (`test_tile_presence_board_committed.py::test_a_two_stage_leg_sums_both_stages`
  and two in `test_integration_intent_check.py`). The fourth, the sidecar test,
  now reports only the 98 missing (0 differing), the same 98 as at base.
- Ruff passes on the two scripts and three test modules touched.
  `npx markdownlint-cli2` reports 0 errors on this report and the
  retrospective.

**A surprise: the union sweep now depends on the merger's pass order.** The
checker's comparison changed, so I re-ran its full `--all` sweep to confirm the
other 105 unions were unaffected. The output is
`reports/stale-register-notes-2026-10-07-union-sweep-2026-10-08.json`. pv-diag-256 now
REPRODUCES. But 24 unions that the 2026-09-12 sweep called REPRODUCES (15) or
SUBPOOL-CONSISTENT (9) now read STALE, by 0 to 4 features. All 24 are in 10-
or 30-pass pools: pv-diag-384, phase3a, phase3a-high and phase3a-replication.
The re-derived counts of the five known-STALE unions moved too (for example
`consensus_t2`: 1,186 → 1,176).

The cause is `75d7c8d4c` (2026-09-13, "fold run_N_recovery fragments into their
pass"). It changed `merge_passes.resolve_pass_files` from sorted directory-name
order (`run_1`, `run_10`, `run_2`, …) to numeric order. `cluster_across_passes`
is greedy, so the clusters depend on that order, and the order changes only
when a pool has 10 or more passes. With the pre-`75d7c8d4c` merger, four of the
24 return their 2026-09-12 class: a 10-pass whole pool, a 30-pass whole pool, a
30-pass pv-diag-384 pool, and a declared 10-pass sub-pool. The known-STALE
`consensus_t2` stays STALE. The pass files are byte-identical in sapphire's
own checkout and the clone, and the checker in sapphire's checkout gives the
same verdict. These are therefore not new staleness: the unions were built in
the old order and are re-derived in the new one. Nothing on this branch causes
them. The base (v1.0.0) checker's own full sweep, in the same clone, gives
the same classes, feature counts and unmatched counts on all 105 other unions.
The only difference between the two sweeps is pv-diag-256: UNRESOLVED under
v1.0.0, REPRODUCES under v1.1.0.

This bears on the S162 open item "pinning union pass order". Until the build
order is pinned or recorded, a re-run of `check_union_provenance.py --all`
calls these 24 STALE. Neither `run_pv.py verify`'s manifest check nor a union
built since `75d7c8d4c` is affected. I did not investigate further or change
anything for it.

**Left undone.**

1. *The conditions still name pool `text`.* Re-pointing `text-baseline` to
   `text-baseline-text-t0.0` and `text-consensus-5of5` to `text-n5-text-t0.7`,
   and dropping `source_run`, would let the register's own routes find their
   passes instead of the bindings. Two code paths ignore `repo_path` for a
   pool that a condition cites, and would need the same fix first:
   `scripts/verify_run_conditions.py`, whose pool-directory check would warn
   `pool-dir-not-found`, and `generate_post_run_report._pool_union_coverage`.
   No condition cites a `repo_path` pool today, h10's included, so neither
   path is reached.
2. *Merge hazard.* `8e343e6e7` changes one line in each of 730 files. If
   another branch regenerates the passes register before this one merges,
   every one of them conflicts. To resolve, take either side, then rerun
   `backfill_cost_audit_sidecars.py --write` and `build_archive_ledger.py
   --write` against the merged register, without committing the other
   workstreams' missing sidecars.
3. *Zero-usage accounting.* The six archived metas now count twice: among the
   ledger's 585 zero-usage archive metas (D39's invoice residual), and as
   register rows with no figure. Neither carries money, so no figure is
   double-counted. But someone counting unrecorded executions from both would
   count these six twice.
4. *The 2026-10-07 diffs.* § 9 item 6 says `op-asis.diff` and
   `op-patched.diff` are kept beside this report. Neither is tracked, and
   neither is in the main checkout's `reports/`.

## Changelog

### 2026-10-08 — § 10: pv-diag-256 registered in place

**Trigger**: the PI's ruling of 2026-10-08 on § 9 item 2, "register
pv-diag-256 in place", which the Session 162 close recommended.

| claim | before | after |
|---|---|---|
| `pv-diag-256.proposer_pools` | `{}` | two pools at `repo_path` `archive/outputs-non-production-tile-sizes` |
| the checker on `outputs/h11/pv-diag-256/consensus` | UNRESOLVED (`UNRESOLVABLE`) | REPRODUCES (`POOL_OVERRIDES`), at all five thresholds |
| `UNRESOLVABLE` entries | 1 | 0 |
| passes register rows | 1,449 | 1,455 |
| pv-diag-256's report, passes on file | 1 | 7 |
| pv-diag-256's report, run total | US$0.7990 | at least US$0.7990; no ceiling (6 unrecorded) |

**What did NOT change**: §§ 1–9's account of 2026-10-07, apart from the
pointers added to § 0, § 1c and § 9 item 2; any condition, evaluation,
detection or cost figure; the runs, conditions and analyses manifests' JSON.

**Landed in**: `20e0be0d3` … `8e343e6e7` and the commit that adds this entry,
on branch `worktree-agent-a462722af99b42e8c`.

### 2026-10-07 — Original publication (Session 162)

The agent record, with this header added.
