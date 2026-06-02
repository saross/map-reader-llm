# Sub-step 3b — conditions + passes decomposition plan

**Created**: 2026-05-30 (Session 94, after the 3b dry-run gap simulation).
**Status**: scope LOCKED with the user; extractor-first build not yet started.
**Predecessors**: `planning/run-registry-draft-review.md` (the 7 issues, the
facts-phase carry-ins, GAP-1…10), `planning/manifest-schema-design.md` (the
four-entity model), `planning/paper-writeup-continuity.md` (Session 93 beacon).

**Purpose**: record the locked scope, the verified gap simulation, the extractor
work items, and the archetype-batch sequencing for fanning the manifest generator
out from the gold-standard-v2 vertical slice to the other 26 runs.

---

## 1. Locked decisions (Session 94)

| # | Decision | Resolution |
|---|---|---|
| Q1 | Sequencing | **Archetype batches (I-draft-you-verify)**: build the generalised extractor + an auto-discovery drafter first, then verify/author the 26 specs in 5 batches grouped by run shape. |
| Q2 | Threshold-sweep grain | **Vote-threshold = conditions; probability-threshold = operating point.** Consensus VOTE sweeps stay separate conditions (gs-v2 precedent: 3of5/4of5/5of5). Greedy/verifier PROBABILITY sweeps (`t1…t5`) collapse to ONE condition at a chosen operating point; the sweep is recorded later as an analysis. |
| Q3 | Spec home | **New sidecar `results/run-conditions.json`** (principled, not expedient): preserves entity-level separation, isolates the high-churn decomposition from the locked `run-facts.json`, gives input↔output symmetry, and extends the B1 drift-check to a 3-input guard. `GS_V2_FACTS` migrates into it as the first entry. |

---

## 2. The headline finding

The bottleneck is **human decomposition, not extractor code.** Evals are NOT 1:1
with conditions (verified 2026-05-30):

- **562** `evaluation.json` under `results/` (plus inline `outputs/**/evaluation/`
  the index does not yet scan).
- h8-v2 alone has **50** eval files but its registry-declared conditions are
  composition × aggregation ≈ **14**. The collapse (`greedy/canonical/{t1…t5}` →
  one greedy-canonical condition at a chosen operating point; `with-mcc/canonical`
  → the *same* condition re-scored for MCC) is irreducibly human.
- **~982** proposer `run_*` dirs + **110** verifier `run.meta.json` (excl. gs) ≈
  **~1,100 passes** to extract — mechanical but voluminous.

So 3b = authoring 26 more `GS_V2_FACTS`-equivalents (the I-draft-you-verify half),
on top of a bounded set of extractor-code fixes.

---

## 3. Gap simulation — verdicts (verified 2026-05-30)

| Gap | Verdict | Evidence | Extractor work |
|---|---|---|---|
| GAP-6 cross-run conditions | confirmed | `outputs/h12-v2/` has `r1-hn-heavy`,`r3-hp-heavy` (own `run_1-5`) but **no `r2-balanced`** dir (→ h10 `pool_160`); verifier-t-pilot `T0.0` → gs-v2 `verified-v1`; 3 wbf fusions → source runs | spec names a *foreign* `proposer_pool`; condition emits with no own passes |
| GAP-7 many-verifier-pass | confirmed | `pv-diag-384` has **88** `run.meta.json` across ~15 pools + `verified/` | generalise verifier-pass walk beyond one-per-dir |
| GAP-9 Era-1 meta shape | confirmed (sharper) | `retest/phase2a/.../run_1` meta has **no `per_item_metadata`**; model in `configuration.model`. Current code → `model_used=""`. Newer runs (gs-v2, h8-v2) carry it | proposer fallback to `configuration.model`, weaker provenance (as the verifier path already does) |
| GAP-10 override temp | confirmed | verifier-t-pilot `T0.5/T1.0`: `configuration.temperature=0.0` but `temperature_effective=0.5/1.0` (E55). `T0.0` has no meta (→ gs-v2 cross-ref) | prefer `temperature_effective` → `run.log` over `configuration.temperature` |
| G-E eval-index coverage (new) | gap | index globs `results/**/evaluation.json` only — misses inline `outputs/55maps-*/evaluation/evaluation.json` and pv-diag-256's archived `threshold_sweep.json`/`summary.json` | extend index to those locations/shapes; allow a per-condition `eval_path` override + shape adapter |
| G-G split MCC eval (new) | gap | h8-v2/h10/h12-v2/55maps store F1 in `greedy/<x>/<t>/` but MCC in a *separate* `with-mcc/`/`mcc/` eval; `_metrics_from_eval` reads one summary | merge tile-classification from a sibling MCC eval (or spec names `mcc_eval`) |
| G-H wbf eval provenance (new) | ambiguous | of 4 wbf carry-ins only `wbf-gs-v2-detect-vote2plus` has an indexed `results/` eval; `fh-text-n30`/`fh-text-n5` (leaderboard #1/#2, F1≈0.890/0.864) have geojsons but no `evaluation.json` by path | resolve each wbf condition's eval source during decomposition |

---

## 4. Extractor-first build — work items (do BEFORE batch authoring)

1. **Sidecar input** `results/run-conditions.json`, keyed by `run_id`; each entry
   carries `proposer_pools`, `verifier_passes`, `conditions`. Generator reads it;
   `GS_V2_FACTS` migrates in as the first entry (behaviour-preserving — the 4
   gs-v2 conditions + 6 passes must reproduce byte-identically). Add the 3-input
   drift-check (registry ↔ facts ↔ conditions).
2. **GAP-9** proposer-meta fallback: no `per_item_metadata` → `configuration.model`,
   provenance notes the weaker source.
3. **GAP-7** generalise the verifier-pass walk to per-pool/per-condition metas.
4. **GAP-10** prefer `configuration.temperature_effective` (then `run.log`) over
   `configuration.temperature`.
5. **GAP-6** formalise cross-run conditions (foreign `proposer_pool`, optional
   `source_run`/`source_pass_ids`; condition emits without own passes).
6. **G-E** extend `_build_eval_index` to inline `outputs/**/evaluation/` evals and a
   per-condition `eval_path` override + a `threshold_sweep.json`/`summary.json`
   shape adapter (pv-diag-256).
7. **G-G** metric-merge from a sibling MCC eval where the primary eval lacks MCC.
8. **Auto-drafter** (`--draft-run <id>`): walks a run's tree and proposes a
   condition/pass spec skeleton into the sidecar for human verification.
9. **Tests** extended per batch (tier-1, deterministic, no API/bootstrap).

### 4a. Audit carry-forwards (from the increment-1 `/audit`, 2026-05-30)

Increment 1's audit surfaced extractor-robustness items in code paths no current
input exercises but the batches will. Fold these into increment 2 (the GAP fixes
touch the same extractors). The increment-1 *consequences* — a stale coverage
note, the run-registry `status` crash-path, and two weak tests — were fixed in
the increment-1 follow-up commit.

The increment-2 audit (after 2a/2b) fixed four real defects in the new code:
two `.get(k, fallback)` null-handling bugs (`_effective_temperature`,
Era-1 `items_processed`) that drop a valid value on an explicit JSON `null`; the
two `cost_estimate` null-guards; and a descriptive `eval_path`-missing error
(was a bare `FileNotFoundError` aborting `--all`). It also strengthened the
`eval_path` test to truly isolate explicit selection from the auto-matcher.
The remaining Low items (a pool spec with no `modality`, a slash in a verifier
label, a bare-string `scope_override`) are left to schema validation, which
catches them loudly at emit time — acceptable for a hand-authored input.

- **Malformed-spec hardening** — `extract_conditions`/`extract_passes` read
  `spec[...]` with bare subscripts; a hand-authored sidecar typo aborts the whole
  `--all` with a bare `KeyError`. Give a descriptive per-spec error (or warn+skip),
  consistent with the missing-eval warning path.
- **Brittle `run_*` parse** — `int(run_n_dir.name.split("_")[1])` crashes on a
  non-numeric `run_*` dir; guard before the Era-1 / many-pass batches.
- **Empty-pass status** — `items_failed == 0 and n_proc == 0` is mislabelled `ok`;
  fix when reworking status for GAP-9.
- **Falsy `model_used`** — the `next(…, "")` fallback records `""` for a non-empty
  pass whose per-item model is blank; tighten alongside the GAP-9 model fallback.
- **No-MCC conditions (sharpened by the increment-2 audit)** — `_metrics_from_eval`
  emits `None` tp/tn/fp/fn when an eval lacks a `confusion` block, but the conditions
  schema REQUIRES tp/tn/fp/fn as non-null integers (and `mcc` present). So a
  genuinely MCC-less result (pv-diag-256, batch E) CANNOT be emitted as a valid
  condition as-is — batch E must compute its tile-classification, point at an
  MCC-bearing eval, or the schema must be relaxed for that one diagnostic run.
- **Provenance path normalisation** — conditions record the raw `spec["detections"]`
  while the eval match used the normalised path; align when batch E (wbf) uses
  pre-reorg paths.

---

## 5. Archetype batches (26 runs; gs-v2 already done)

| Batch | Runs | Gaps exercised |
|---|---|---|
| **A — simple proposer/consensus/verifier** | `e47-propose-brief`, `n1-outstanding-384`, `proposer-verifier-384`, `proposer-verifier-512`, `retest-h11-single-pass-384-t0`, `consensus-384-t1-0` | base extractor + GAP-9 (pv-512 is Era-1) |
| **B — 55maps generalisation** | `55maps-generalisation`, `55maps-image-generalisation`, `55maps-text-high-generalisation`, `55maps-text-high-t0-3-generalisation`, `55maps-text-min-generalisation` | G-E (inline evals), student GT, carry-forward #10 (`verified_detections_paired`) |
| **C — library studies** | `h8-v2`, `h10`, `h12-v2` | Q2 sweep-grain, G-G (split MCC), GAP-6 (h12 r2→h10 pool), scope_override (487 siblings vs 327 nominal) |
| **D — Era-1 retest** | `retest-phase2a/2b/2c/2d/2e`, `retest-phase3a`, `retest-phase3a-high`, `retest-phase3a-replication`, `retest-phase3c` | GAP-9 at scale, deep nesting (phase3c `h9-X-pN` = passes) |
| **E — gap-heavy diagnostics** | `pv-diag-384`, `pv-diag-256`, `verifier-t-pilot` (+ the 4 wbf cross-run conditions attaching to gs-v2/e47/pv-diag-384) | GAP-7, G-E (archived eval), GAP-10, GAP-6/G-H (wbf) |

Run tally: A 6 + B 5 + C 3 + D 9 + E 3 = 26. ✓

---

## 6. Carry-ins to honour (from the facts-phase review)

- **wbf condition reassignments** (`scripts/fuse_detections_wbf.py` `SPECIAL_CONFIGS`):
  `gold-standard-v2-detect`→gs-v2 (`detect_brief-text`, n5, vote2plus geojson);
  `e47-propose-brief-n5`→e47 (`flash-high-text-n5`, n5); `fh-text-n5`→pv-diag-384
  (`text-t0.7`, n5); `fh-text-n30`→pv-diag-384 (`text-t0.7`, n30; needs pv-diag-384
  passes extended to 30).
- **scope_overrides**: h8-v2 / h12-v2 verifier-stage conditions evaluated on the
  327 pool (not 487); 487 evals are comparability siblings → condition-level
  `scope_override`. Same pattern for `retest-phase2b` (5 cross-scope evals on 487).
- **pv-diag-256 archived eval**: `archive/results-non-production-tile-sizes/h11-256-pv-diagnostic/`
  (`threshold_sweep.json`/`summary.json` shapes; commit 276e4ca8). No MCC; 431 ref
  mounds; bespoke 256 scope.
- **55-map base run = superseded original** (carry-forward #10): `55maps-generalisation`
  (`verified_paired`) is the pre-recovery original of `55maps-text-high-generalisation`
  (same T=0.7 text experiment, same reconstruction config). When authoring Batch B,
  confirm the inferred scope and decide **fold the base into text-high as a
  `historical_alias` vs keep it as a cited original**. Full identity/coverage map:
  `docs/methodology/55maps-generalisation-runs.md`.

---

## 7. Out of scope for 3b

- Sub-step 3c (analyses manifest) — hybrid human-authored, follows 3b.
- Headline-condition designation (`headline_condition_id`) — human, deferred.
- Model-provenance reconciliation against billing (Session 91 carry-forward).
- Physical directory renames (dotted dirs) — deferred follow-up.
