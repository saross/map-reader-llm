# Provenance audit — `pv-diag-384::pro-high-text-n5-text-t0.7`

> **Verdict**: **Genuinely Pro throughout (all 10 runs).** Not mixed. The `config.model`
> split is a metadata-serialisation artefact whose cause is datable to the hour.
> **Severity: documentation-only — no reported number changes.** One real
> defect found: `results/passes-manifest.json` mislabels 10 passes.

Audit date: 2026-07-28. Read-only; nothing in the repo was modified.

---

## 0. Correction to the brief's premise (load-bearing)

The task brief states that E57 prescribes the eval `_metadata.input_files.detections`
path plus `study_manifest.json` as ground truth. **That is E57's original
(2026-06-02) resolution, which E57's own 2026-06-03 Update explicitly supersedes.**

`docs/methodology/preregistration/protocol-errata.md:1826` (Update section):

> **The authoritative field for *what ran* is `per_item_metadata.model_version` /
> `pricing_used.model` — NEVER `config.model`** (a Flash template-default on BOTH
> groups) **and never the directory slug or the study YAML** (which record *intent*,
> not dispatch).

So the prior pass applied the **retired** hierarchy. Under the *current* hierarchy the
resolution path is not merely available — it is present in every file:

| Field | Present for this pool? | Anchor |
|---|---|---|
| `cost_estimate.pricing_used.model` | **YES — all 10 runs** | `run_1/detections_text-t0.7_run01.meta.json:648-653` |
| `study_manifest.json` | **YES** (but describes only runs 6–10) | `outputs/h11/pv-diag-384/pro-high-text-n5/study_manifest.json` |
| `per_item_metadata` | No (batch mode; structural) | `scripts/lib_batch_api.py:1397` `finalise(include_per_item=False)` |

The prior pass's claim that *both* authoritative fields are absent is therefore
**wrong on both counts**. Only `per_item_metadata` is genuinely absent.

> **Live demonstration of the failure mode.** A sub-agent I dispatched during this
> audit independently reported "`pricing_used` and `per_item_metadata` — the two
> fields E57 declares authoritative — are **absent from all ten files**." I had
> already read `pricing_used` directly. A first raw `grep -o '"pricing_used"[^}]*}'`
> also returned nothing — because the JSON is pretty-printed and line-based grep
> cannot cross newlines. A one-line tooling artefact produced a confident,
> false absence claim from two independent agents. **"Field absent" assertions in
> this codebase should never be trusted without a `grep -A5` or a JSON parse.**

---

## 1. What is actually on disk

Pool root: `outputs/h11/pv-diag-384/pro-high-text-n5/` — `study_manifest.json`,
`checkpoint.json`, and `text-t0.7/` (742 MB) containing `run_1` … `run_10` plus
`consensus/`.

Full model-bearing field inventory, read from each
`text-t0.7/run_N/detections_text-t0.7_runNN.meta.json`:

| Run | `configuration.model` | `…full_config_snapshot.model` | `cost_estimate.pricing_used.model` | rates in/out | `environment.git_commit` | `timestamp.start` (UTC) |
|---:|---|---|---|---|---|---|
| 1 | `gemini-3-flash` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `765cb232a` | 2026-03-24T04:00:25 |
| 2 | `gemini-3-flash` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `765cb232a` | 2026-03-24T04:00:20 |
| 3 | `gemini-3-flash` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `765cb232a` | 2026-03-24T04:00:30 |
| 4 | `gemini-3-flash` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `765cb232a` | 2026-03-24T03:49:23 |
| 5 | `gemini-3-flash` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `765cb232a` | 2026-03-24T03:49:19 |
| 6 | `gemini-3.1-pro-preview` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `33db78e4a` | 2026-03-29T04:09:22 |
| 7 | `gemini-3.1-pro-preview` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `33db78e4a` | 2026-03-29T04:10:59 |
| 8 | `gemini-3.1-pro-preview` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `33db78e4a` | 2026-03-29T04:11:04 |
| 9 | `gemini-3.1-pro-preview` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `33db78e4a` | 2026-03-29T04:11:08 |
| 10 | `gemini-3.1-pro-preview` | `gemini-3-flash` | **`gemini-3.1-pro-preview`** | 2.0/12.0 | `33db78e4a` | 2026-03-29T04:14:45 |

All ten: `total_tiles=487, completed=487, failed=0` (`*.tiles.json`);
`batch_api.execution_mode = "batch"`; `usage_stats` all-zero and
`cost_estimate.*_cost_usd = 0.0` (batch job returned no token counts —
this is why cost is $0, not evidence about the model).

Note `full_config_snapshot.model` is `gemini-3-flash` on **all ten**, including the
runs whose `configuration.model` correctly reads Pro. It is the raw base-config dict
and is never override-merged — it is the single least reliable field in the file.

**Two dispatch events.** `study_manifest.json` describes only the N=10 extension:
`"H11: 384px Pro HIGH — Text N=10"`, `"total_units": 5`, `execution_order` =
`run_10, run_7, run_8, run_9, run_6`, `"Uses --resume to skip runs 1-5."` The
manifest for the original N=5 study was **overwritten in place**. This is itself a
provenance-erasing pattern (§6).

---

## 2. Is the pool genuinely mixed? — No. Four independent lines converge on Pro

### Line 1 — `pricing_used.model` is Pro on all ten, and the rates prove it is derived

`pricing_used.model = gemini-3.1-pro-preview` with `input_per_1m: 2.0,
output_per_1m: 12.0` on every run. Verified by raw `grep -A5 '"pricing_used"'`:
line 648–653 in `run_1`/`run_5`, line 649–654 in `run_6`/`run_10`.

Critically, the `google_gemini` **`default`** rate is `{"input": 0.50, "output": 3.00}`
(`scripts/lib_llm_metadata.py:1017`) — i.e. Flash rates. The $2/$12 pair only arises
from a successful longest-prefix match against the `gemini-3.1-pro-preview` key
(`scripts/lib_llm_metadata.py:1009`, match logic at `:1057-1064`). **The rates
could not have been produced by a fallback.**

### Line 2 — code trace: `pricing_used` and the actual dispatch share one variable

At the exact commit runs 1–5 executed (`765cb232a`, extracted via `git show`):

- `submit_batch_job(client, ctx.model_name, uploaded_name, display_name)` — line 1492 → **this is the real dispatch**
- `write_batch_outputs(..., model_name=ctx.model_name, ...)` — line 1718
- inside `write_batch_outputs`: `estimate_cost(usage=usage, provider=…, model=model_name)` — line 1288 → **writes `pricing_used.model`**

Same `ctx.model_name` object on both branches. Meanwhile `configuration.model` came
from a *different* source — the `config` dict (`ctx.prompt_config`) via
`LLMMetadataTracker`, which at that commit was constructed **without**
`model_override` (line 1257–1262), so `configuration.model` fell through to
`self.config.get("model")` = the base-config template default
(`scripts/lib_llm_metadata.py:515-519`).

**Therefore `pricing_used.model` is a faithful record of the model string used to
create the batch job; `configuration.model` is not.**

### Line 3 — the split is exactly the commit boundary of a known metadata fix

`model_override` was introduced in **`260f039f3`, 2026-03-26**, "fix(scripts):
session 57 code audit — bug fixes across 15 files" (touches both
`lib_batch_api.py` and `lib_llm_metadata.py`).

```
git merge-base --is-ancestor 260f039f3 765cb232a  → NO  (runs 1–5,  2026-03-24)
git merge-base --is-ancestor 260f039f3 33db78e4a  → YES (runs 6–10, 2026-03-29)
```

The `config.model` flip occurs precisely at the fix boundary. Nothing about the
dispatched model changed — only whether the runner *serialised* the override.

### Line 4 — empirical: no model-scale discontinuity in the scores

Per-run F1@20 m from `results/paper-eval/n1/384px-14buf-mcc/pro-text-high-t-0-7/evaluation.json`:

| Run | n_det | F1@20 m | | Run | n_det | F1@20 m |
|---|---:|---:|---|---|---:|---:|
| 01 | 440 | 0.7383 | | 06 | 442 | 0.7434 |
| 02 | 442 | 0.7503 | | 07 | 433 | 0.7258 |
| 03 | 429 | 0.7546 | | 08 | 435 | 0.7540 |
| 04 | 430 | 0.7514 | | 09 | 439 | 0.7346 |
| 05 | 439 | 0.7460 | | 10 | 448 | 0.7520 |

- runs 1–5: mean **0.7481**, sd 0.0056, mean n_det 436.0
- runs 6–10: mean **0.7420**, sd 0.0106, mean n_det 439.4
- **Δ = −0.0062** — smaller than the within-half spread, and *negative* (the
  putatively-Flash half scores **higher**).

For scale, E57's documented genuine Flash-vs-Pro gap at the adjacent corner
(`protocol-errata.md:1838-1843`) is **0.494 → 0.804**, i.e. **Δ ≈ 0.31 — roughly
50× larger**. A genuine Flash/Pro boundary at run 5/6 is not compatible with
this data.

### Line 5 (control) — a same-signature pool where per-item ground truth *does* exist

`outputs/h11/pv-diag-384/pro-medium-text-baseline/text-t0.0/run_1/detections_text-t0.0_run01.meta.json`
carries the **identical signature** (`configuration.model = gemini-3-flash`,
`pricing_used.model = gemini-3.1-pro-preview`) — but, because the E57 n=3 addendum
recovery merged resume records into it, it also has **26 `per_item_metadata`
records**. All 26 agree unanimously:

```
model_used      : {'gemini-3.1-pro-preview': 26}
model_version   : {'gemini-3.1-pro-preview': 26}
model_requested : {'gemini-3.1-pro-preview': 26}
```

This is E57's own top-of-hierarchy field, applied to the same failure signature,
**confirming `pricing_used` and contradicting `config.model`.** It is as close to a
controlled validation of the inference as the corpus permits.

### Where the evidence runs out

`per_item_metadata` is absent for this pool and cannot be recovered: batch mode calls
`tracker.finalise(include_per_item=False)` (`scripts/lib_batch_api.py:1397`), and the
retained `batch_working/*.jsonl` files (runs 6–10 only; 487 lines each) contain only
`{key, request}` — **request payloads, no responses, no model string anywhere**.
Runs 1–5 have no `batch_working/` at all. So the single highest-authority field is
permanently unavailable for runs 1–5. Everything above is the next tier down —
but it is four mutually independent tiers, one of them externally validated.

---

## 3. The exposure

**Because all ten runs are Pro, the run-span question is moot for model identity.**
Whether a condition draws runs 1–5, 6–10, or all 10, it draws Gemini 3.1 Pro.

The three `verified-adv-pro-text-*-3of5` conditions do consume **runs 1–5** (via the
504-feature union `outputs/h11/pv-diag-384/consensus/pro-high-text-1of5.geojson`,
materialised 2026-03-24, five days before runs 6–10 existed;
`scripts/materialise_vr_condition_sets.py:53`). Their registrations:

| Condition | `results/run-conditions.json` | F1 (`results/conditions-manifest.md`) |
|---|---|---|
| `pv-diag-384::verified-adv-pro-text-flash-vf-3of5` | `:2429-2447` | 0.8491 (`:177`) |
| `pv-diag-384::verified-adv-pro-text-pro-vf-3of5` | `:2448-2466` | 0.8506 (`:178`) |
| `pv-diag-384::verified-adv-pro-text-medium-vf-3of5` | `:2747-2766` | 0.8495 (`:193`) |

**These conditions are correctly labelled Pro.** The hypothesis that they "rest on
Flash proposals while being labelled Pro" is **not supported** — it is exactly the
red herring the brief warned might be there, and it is.

I separately confirmed the *verifier* side is sound: every `-pro-verifier` directory
under `outputs/h11/pv-diag-384/verified/` records
`gemini-3.1-pro-preview` at $2/$12 in both `configuration.model` and
`pricing_used.model` — including `pro-high-text-1of5-pro-verifier/run.meta.json`
(2026-03-25T23:35:52). So the paper's Pro-verifier-vs-Flash-verifier comparison
uses a genuine Pro verifier.

**Paper exposure**: `grep` for `pro-high-text`, `pro-text-high`, `3of5`,
`verified-adv-pro` across `docs/paper/` (`results-draft.md`, `results-outline.md`,
`discussion-seeds.md`) returns **zero hits**. The pool is never named. It backs
unnamed prose claims at `docs/paper/results-draft.md:190-197` ("A Pro-class verifier
ties the Flash verifier…"; "Pro is a genuinely better *bare* proposer but a worse PV
partner — its near-deterministic sampling caps pool recall"). **Those claims are
unaffected**, because they compare Pro against Flash and the Pro side is genuinely Pro.

---

## 4. Blast radius

### 4a. What is actually wrong — `results/passes-manifest.json` (10 passes)

The manifest records `model_used` / `model_requested` = **`gemini-3-flash`** for:

- `pv-diag-384::pro-high-text-n5-text-t0.7::run1` … `run5` (manifest lines 11386, 11460, 11497, 11534, 11571)
- `pv-diag-384::pro-high-image-n5-image-t0.7::run1` … `run5`

`model_version` is `null` for all 10 (and for runs 6–10 too). Runs 6–10 of the text
pool are correctly `gemini-3.1-pro-preview`. **10 mislabelled pass rows.**

**Root cause** — `scripts/generate_post_run_report.py:373-382`, in the branch taken
when no per-item records exist:

```python
# Era-1 batch-API shape (GAP-9): no per-item record. configuration.model
# is the best available authoritative value (the verifier path uses the
# same fallback); the tile count is in execution_stats.
n_proc = es.get("items_processed") or 0
model_used = cfg.get("model", "")
model_requested = cfg.get("model")
model_version = None
```

The comment's premise is false: `configuration.model` is *not* the best available
value, because `cost_estimate.pricing_used.model` is also present — **in
1,187 of 1,187 metas corpus-wide (100 % coverage; zero metas lack it)** — and is
strictly more authoritative. The generator never consults it.

The generator does have a `model_of_record` sidecar override
(`generate_post_run_report.py:346`, `:386-391`), but it is authored for only **8
pools**, all outside this one: the four `n1-outstanding-384` pro-* pools and the four
`n1-pro-rerun-384` pools (`results/run-conditions.json:229, 235, 241, …`). The block
for this pool, `run-conditions.json:1482`, is bare:
`{"modality": "text", "path": "pro-high-text-n5/text-t0.7"}` — no `model_of_record`.

### 4b. Downstream propagation of the wrong label

- `results/passes-manifest.md:318-327` — the rendered table, column header `model`.
- `planning/condition-inventory.json` entry `h11-pvd-pro-high-text-n5` records
  `"model": "gemini-3-flash"` (verified by direct parse), `"K": 10`.

Both are documentation surfaces. Neither feeds a computed metric.

### 4c. Scored artefacts consuming the pool — all numerically unaffected

Leaderboards (`results/leaderboard/era2/leaderboard_tiers_20m.json:25-40`,
F1@20 m 0.8359 at K=10/t=6), per-architecture consensus rank 1
(`results/leaderboard/per-architecture/era2/consensus/leaderboard_tiers_20m.md:12`),
the transfer row `consensus -> pv` in
`results/leaderboard/per-architecture/cross-architecture-paired-era2_f1.md:19`,
the Pareto rows `pro6-flashvf` / `pro6-provf` in
`results/verifier-robustness/pareto/pareto_leaderboard.json`, and the N=1 cell
`baseline-pro-text-high-t-0-7` (F1 0.745, `summary.n_runs = 10`) all consume
detection **geometry**, which no one disputes. **No metric moves.**

`results/analyses-manifest.json:18` (analysis `n1-baseline-matrix-384`) asserts
*"(All eight Pro cells are genuine Gemini 3 Pro at n>=3; see deviations E57 …)"*.
**This audit confirms that statement rather than undermining it.**

### 4d. One unrelated wrinkle found in passing (not provenance)

`results/verifier-robustness/pool_recall_ceilings.json` row `pro-high-t07-5pass`
reports `union_per_pass: 1.15` = `n_union 504 / per_pass_mean 437.7`. The union
(504) is the **5-run** consensus, but `per_pass_mean` is globbed over
`run_*/detections_*.meta.json` (`scripts/compute_pool_recall_ceilings.py:48`),
i.e. **all 10 runs**. Runs 1–5 alone mean 436.0. Corrected ratio 504/436.0 = 1.156
vs reported 1.152 — **both round to 1.15, so the reported figure stands.**
Mixed-denominator hygiene issue only; flagged for completeness, not a correction.

---

## 5. What would settle it definitively

**A purely on-disk resolution exists and is presented above (§2, five lines,
one externally validated). I do not think a billing lookup is needed.**

If the PI wants belt-and-braces confirmation anyway, the lookup is small and precise.
All twelve affected passes are batch-mode, and Pro/Flash SKUs are separately itemised.

**Google Cloud billing console → filter by SKU, group by day:**

| | |
|---|---|
| **Date (UTC)** | **2026-03-24** — the text pool's 5 passes were submitted 03:49:19–04:00:30 UTC (batch jobs complete later the same day). The sibling `pro-high-image-n5` runs 1–5 were submitted the same UTC day, 03:59:26–07:09:43. |
| **Expected model / SKU** | `gemini-3.1-pro-preview` (Pro-tier SKU, batch), **not** a Flash SKU |
| **Expected call volume** | text pool 5 × 487 = **2,435** batch requests; plus image pool 5 × 487 = **2,435**; **≈ 4,870 Pro batch requests on 2026-03-24** |
| **Expected rate** | $2.00 / $12.00 per 1M tokens with the 50 % batch discount → **$1.00 / $6.00 effective** |
| **Also worth a glance — 2026-03-23** | `pro-medium-text-baseline` run_1 (14:21:48 UTC) and `pro-medium-image-baseline` run_1 (15:11:34 UTC), 487 tiles each — but these two are already independently confirmed Pro by 26 per-item records (§2 Line 5) |
| **What would falsify the verdict** | A Pro-tier SKU **absent** on 2026-03-24 while a Flash SKU shows ~4,870 unexplained extra batch requests |

Sydney note: 2026-03-24 UTC ≈ 2026-03-24 11:00 – 2026-03-25 11:00 AEDT.

---

## 6. Characterising the failure mode

### 6a. Mechanism — same *bug family* as E57, but a different and milder instance

E57 names one root cause but the corpus actually contains **two distinct failure
modes that E57's prose blurs together**:

| | **Mode A — serialisation artefact** | **Mode B — true mis-dispatch** |
|---|---|---|
| What happened | Override reached the API; only the metadata writer missed it | Override never reached the API; the wrong model ran |
| Signature | `config.model` = flash, `pricing_used` = **pro** (fields **disagree**) | `config.model` = flash, `pricing_used` = flash, per-item = flash (fields **all agree**) |
| Instance | **This pool** (+3 siblings) | E57's four `n1-outstanding-384` pro-* cells |
| Cost consequence | None — billed as Pro | Billed as Flash |
| Finding consequence | **None** | **Changed the N=1 leaderboard, tie_set, and H6 narrative** |
| Fixed by | `260f039f3` (2026-03-26) adding `model_override` to the tracker | Re-dispatch as `n1-pro-rerun-384` |

E57's root-cause sentence — *"the proposer runner serialised the base-config `model`
without merging the per-study Pro override"* — describes **Mode A precisely**. Its
Update then describes Mode B. **This instance is Mode A: benign, and already fixed
upstream.** The dangerous mode is B, and it is not present here.

### 6b. Size of the affected class — bounded exhaustively at 12 metas

I parsed **all 1,187 `*.meta.json` under `outputs/`** and compared
`configuration.model` against `cost_estimate.pricing_used.model`:

- 774 disagree in total
- **762 are benign same-family**: `gemini-3-flash` → `gemini-3-flash-preview`, the
  `-preview` suffix resolution at `scripts/lib_batch_api.py:2101-2109`
- **12 are cross-family** (`gemini-3-flash` → `gemini-3.1-pro-preview`) — the
  complete Mode-A class:

| Pool | Passes | Manifest label today |
|---|---|---|
| `pv-diag-384/pro-high-text-n5/text-t0.7` | run_1–5 | **wrong** (`gemini-3-flash`) |
| `pv-diag-384/pro-high-image-n5/image-t0.7` | run_1–5 | **wrong** (`gemini-3-flash`) |
| `pv-diag-384/pro-medium-text-baseline/text-t0.0` | run_1 | correct (rescued by per-item records) |
| `pv-diag-384/pro-medium-image-baseline/image-t0.0` | run_1 | correct (rescued by per-item records) |

**This is exactly the set of four `pv-diag-384` Pro pools that E57's Update already
affirms are genuinely Pro** — an independent, mechanical rediscovery of E57's own
conclusion. All 12 ran at pre-`260f039f3` commits (`765cb232a`, `2126c3efa`,
`2f425fc8a`). **The class is closed: no pool dispatched after 2026-03-26 can exhibit
Mode A.** `pro-high-text-n5` is not unique; it is 1 of 4, and the least surprising
member.

### 6c. Are the manifests able to detect this class? — Partly, and blind where it matters

**Mode A is detectable** and the current manifests miss it purely by choice of field:
`generate_post_run_report.py` reads `configuration.model` and ignores
`pricing_used.model`, which is present everywhere. Cheap to fix.

**Mode B is structurally invisible to any internal-consistency check.** I verified
this directly on the known-bad pools: every `n1-outstanding-384` pro-* meta reads
`config.model = gemini-3-flash-preview`, `pricing_used = gemini-3-flash-preview`,
rates 0.5/3.0, `per_item_metadata.model_version = gemini-3-flash-preview`. **Every
field agrees.** Nothing inside the file is wrong; only the *name* — the directory
slug `pro-text-high-t0` and the study YAML's `--model gemini-3.1-pro` — records an
intent the dispatch never honoured. No self-consistency check can catch that. Only
an **intent-versus-dispatch** comparison can, which is why E57 needed the billing
console.

I ran that intent-versus-dispatch check corpus-wide (slug/path claims Pro vs
`pricing_used` family). It returned **14 suspects**:

- **8** = the four `n1-outstanding-384` pro-* pools — i.e. it **re-detects E57's
  mis-dispatch from disk alone, no billing console required**
- **6** = benign false positives under `outputs/h11/pv-diag-384/verified/`, where
  "pro" names the *proposer* pool and the verifier is legitimately Flash
  (e.g. `pro-text-medium-verifier`, `pro-high-text-1of5-flash-minimal-verifier`)
- **0 new mis-dispatches anywhere in the corpus**

That last point is the most reassuring result of this audit: **the wider problem the
PI is probing for does not appear to exist beyond what E57 already documents.**

### 6d. Cheapest checks that would catch this class

**Check 1 (three lines, catches Mode A).** In
`scripts/generate_post_run_report.py:373-382`, prefer `pricing_used.model` in the
no-per-item fallback and warn on cross-family disagreement:

```python
pu = (meta.get("cost_estimate") or {}).get("pricing_used", {}).get("model")
cm = cfg.get("model")
if pu and cm and _family(pu) != _family(cm):
    print(f"WARNING: model disagreement in {meta_path}: config={cm} pricing={pu}",
          file=sys.stderr)
model_used = pu or cm or ""
```

Zero new I/O — the dict is already loaded. Rerunning the generator would correct all
10 mislabelled rows automatically, with no sidecar authoring.

**Check 2 (the important one — catches Mode B, the finding-affecting mode).** A
CI/test assertion that **declared intent matches recorded dispatch**: for every pool,
compare the study YAML's `--model` (and/or the `pro`/`flash` token in the directory
slug) against `pricing_used.model`. Mode B produces an internally consistent file, so
this is the *only* on-disk check that can catch it. Demonstrated working above: it
recovers all 8 known-bad `n1-outstanding-384` passes with 6 easily-suppressed false
positives (whitelist `*/verified/*`, where the slug names the proposer).

Had Check 2 existed in March 2026, E57's finding-changing mis-dispatch would have
been caught **before** the four Flash cells reached the N=1 leaderboard — without a
billing reconciliation.

**Check 3 (prevention, cheap).** Stop overwriting `study_manifest.json` on
`--resume`; write `study_manifest.run6-10.json` or append to a list. The
original N=5 manifest for this pool is unrecoverable, which is what made the pool
look ambiguous in the first place.

---

## 7. Bottom line

| Question | Answer |
|---|---|
| Mixed? | **No — genuinely Pro, all 10 runs.** Four independent lines, one externally validated by 26 per-item records on a same-signature control pool. |
| Does a number change? | **No.** No F1, MCC, tier, leaderboard, transfer, or Pareto value moves. |
| Is anything wrong? | **Yes, documentation only**: 10 mislabelled `model_used` rows in `results/passes-manifest.json` (+ mirrors in `passes-manifest.md`, `planning/condition-inventory.json`). |
| Class size | **12 metas / 4 pools**, exhaustively bounded over 1,187 files; class closed after 2026-03-26. |
| New mis-dispatches found | **Zero**, corpus-wide. |
| Billing lookup needed? | **Not required.** Specified in §5 if wanted. |

The `config.model` reading that triggered this audit was a **red herring — but a
productive one**: chasing it surfaced a genuine 10-row manifest defect, a code-level
root cause with a three-line fix, a structural blind spot for the *dangerous* failure
mode, and an on-disk check that reproduces E57's billing finding for free.
