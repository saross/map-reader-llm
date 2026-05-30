# Run-registry draft — review sheet (I-draft-you-verify)

**Created**: 2026-05-30 (Session 92+ fan-out, sub-step 1).
**Status**: DRAFT for human verification. The machine artefact is
`planning/run-registry-draft.json` (28 entries, schema-valid against
`docs/manifest-schemas/run-registry.schema.json`). Nothing under `results/` was
touched — the generator's gold-standard-v2 stub at `results/run-registry.json`
is left in place until this draft is verified and promoted.

**Purpose**: enumerate *what is a run* across the live `outputs/` tree so the
manifest generator can fan out beyond the gold-standard-v2 vertical slice. Per
the agreed posture: I draft and flag the ambiguous run-vs-condition groupings;
you verify, split, or merge; the verified result is promoted to
`results/run-registry.json`.

---

## How this was enumerated

- **Primary source: the live `outputs/` tree**, not `planning/condition-inventory.json`.
  The inventory is both stale (it omits the `55maps-*`, `wbf`, `verifier-t-pilot`,
  and `gold-standard-v2` runs and still references dead `results/leaderboard` and
  old `retest/` paths) and the wrong grain (its entries are condition- *or
  pass*-level — e.g. `retest/phase3c/track1-image/h9-A-p1…p4` are four passes).
  It is used here only for `primary_hypothesis` / `historical_aliases` hints.
- **Grain default (your decision): umbrella = one run.** Where a directory holds
  subdirs that are scale, threshold, or temperature variants sharing a proposer
  pool, the umbrella is one run and the subdirs become *conditions*. Every such
  case is tagged `FLAG-GRAIN` in the draft's `notes` so you can split it.
- **Non-runs omitted (your decision):** `outputs/{figures,results}`,
  `outputs/qgis-{dedup,sanity,wbf}-check`, `outputs/test-phase2b`,
  `outputs/v2-proposer-test`. None appear in the draft.

**Result: 28 runs.** 23 are settled; 5 carry a `FLAG-GRAIN` for your call.

---

## The 28 runs at a glance

| # | run_id | directory_path | hypothesis (inventory) | flag |
|---|---|---|---|---|
| 1 | `55maps-generalisation` | `outputs/55maps-generalisation` | — (absent) | carry-fwd #10 |
| 2 | `55maps-image-generalisation` | `outputs/55maps-image-generalisation` | — | — |
| 3 | `55maps-text-high-generalisation` | `outputs/55maps-text-high-generalisation` | — | — |
| 4 | `55maps-text-high-t0-3-generalisation` | `outputs/55maps-text-high-t0.3-generalisation` | — | **FLAG-SLUG** |
| 5 | `55maps-text-min-generalisation` | `outputs/55maps-text-min-generalisation` | — | — |
| 6 | `gold-standard-v2` | `outputs/gs/gold-standard-v2` | — | populated |
| 7 | `h10` | `outputs/h10` | H10v2 | **FLAG-GRAIN** |
| 8 | `consensus-384-t1-0` | `outputs/h11/consensus-384-UNINTENDED-T1.0` | — | **FLAG-SLUG**, E43 |
| 9 | `e47-propose-brief` | `outputs/h11/e47-propose-brief` | H11 | — |
| 10 | `n1-outstanding-384` | `outputs/h11/n1-outstanding-384` | H11 | — |
| 11 | `proposer-verifier-384` | `outputs/h11/proposer-verifier-384` | H11 | — |
| 12 | `proposer-verifier-512` | `outputs/h11/proposer-verifier-512` | — | — |
| 13 | `pv-diag-256` | `outputs/h11/pv-diag-256` | — | — |
| 14 | `pv-diag-384` | `outputs/h11/pv-diag-384` | H11/H3/H8 | GAP-7 |
| 15 | `h12-v2` | `outputs/h12-v2` | H12v2 | **FLAG-GRAIN** |
| 16 | `h8-v2` | `outputs/h8-v2` | H8v2 | **FLAG-GRAIN** |
| 17 | `retest-phase2a` | `outputs/retest/phase2a` | H1 | — |
| 18 | `retest-phase2b` | `outputs/retest/phase2b` | H7 | — |
| 19 | `retest-phase2c` | `outputs/retest/phase2c` | H8 | — |
| 20 | `retest-phase2d` | `outputs/retest/phase2d` | H5 | — |
| 21 | `retest-phase2e` | `outputs/retest/phase2e` | H4 | — |
| 22 | `retest-phase3a` | `outputs/retest/phase3a` | H3 | — |
| 23 | `retest-phase3a-high` | `outputs/retest/phase3a-high` | H3 | — |
| 24 | `retest-phase3a-replication` | `outputs/retest/phase3a-replication` | H3 | — |
| 25 | `retest-phase3c` | `outputs/retest/phase3c` | H9 | GAP-6 |
| 26 | `retest-h11-single-pass-384-t0` | `outputs/retest/h11-single-pass-384-t0` | H11 | — |
| 27 | `verifier-t-pilot` | `outputs/verifier-t-pilot` | — | **FLAG-GRAIN** |
| 28 | `wbf` | `outputs/wbf` | — | **FLAG-GRAIN** |

---

## The five FLAG-GRAIN groupings — your call

Each is drafted as **one run** (your default). Listed strongest-to-weakest split
candidate:

1. **`wbf` (28) — strongest split candidate.** Its four subdirs
   (`e47-propose-brief-n5`, `fh-text-n30`, `fh-text-n5`, `gold-standard-v2-detect`)
   are WBF *fusion* outputs that consume *other runs'* proposer pools. They read
   more like cross-run *conditions* than an internally-coherent run. Carry-forward
   #11 (`gold-standard-v2-detect`) is one of them. Two coherent options: (a) keep
   `wbf` as a thin umbrella run holding four fusion conditions; (b) attach each
   fusion output as a condition of its *source* run (gs-v2, e47, fh-text). Option
   (b) is cleaner conceptually but needs cross-run condition references the
   extractor does not yet do (GAP-6).
2. **`h8-v2` (16).** Subdirs `canonical / plus-hp / pure-positive-canon / greedy /
   wbf / scale-{4,8,16,32}` — `scale-N` are verifier-scale variants over one
   proposer pool, i.e. conditions. One run is defensible; the 327-vs-487 scope
   trap (Session 92 beacon) means some conditions need `scope_override`.
3. **`verifier-t-pilot` (27).** `T0.0 / T0.5 / T1.0` — verifier-temperature
   conditions over a shared pool. Clean "one run, three conditions".
4. **`h12-v2` (15).** `greedy / r1-hn-heavy / r3-hp-heavy / wbf` — aggregation
   variants. One run.
5. **`h10` (7).** `evaluation-v2 / example-pools-v2 / hard-cases-v2` — these look
   like sub-analyses/diagnostics rather than scored conditions; may not yield
   conditions at all. One run.

---

## Two design contradictions the fan-out surfaced (both RESOLVED 2026-05-30)

### A. Slug pattern forbids dots — but §1A and a live dir contain them

The `run_id` pattern in **both** the run-registry and runs schemas is
`^[a-z0-9]+(-[a-z0-9]+)*$` — **no dots allowed**. Two collisions:

- **§1A's worked example `consensus-384-t1.0` is itself invalid** against the
  schema it was written for. The draft uses `consensus-384-t1-0` (dot→hyphen).
- `outputs/55maps-text-high-t0.3-generalisation` can't seed a dotted slug; the
  draft uses `55maps-text-high-t0-3-generalisation`.

**Options**: (a) **dot→hyphen** in slugs + a one-line correction to §1A's example
(my default, applied in the draft); (b) relax the schema pattern to allow dots
(uglier slugs, but §1A stays as written and slugs mirror dirs exactly).

> **✅ Resolved — option A1 (dot→hyphen).** §1A and its 2026-05-29 changelog
> corrected; the no-dots constraint documented inline; draft notes updated. The
> physical dir rename is a deferred follow-up (see below).

### B. The registry is *input* at fan-out, but the generator currently *writes* it

The design (§1, §2.5) treats the run registry as the **generator's input** — the
hand-verified list of what to extract. But the current generator *synthesises*
`results/run-registry.json` from `GS_V2_FACTS` via `extract_registry_entry()`
(an output). That was fine for a one-run slice; at fan-out the verified registry
must be the **source-of-truth the generator reads** to know which runs exist.

**Proposed resolution** (flagged, not yet applied): on approval, promote this
draft to `results/run-registry.json`; retire `extract_registry_entry()` as a
synthesiser and have the generator *read + validate + render* the registry
instead, using it as the run list. No schema change needed.

> **✅ Resolved — B1 + drift-check.** The verified registry becomes the
> hand-authored source-of-truth at `results/run-registry.json`. The generator
> reads + validates it, uses `registry[]` as the authoritative run list, renders
> `results/run-registry.md` from it, and retires `extract_registry_entry()` as a
> synthesiser. Added guard: the generator WARNs if a run with facts has no
> registry row, or a registry row has no facts (registry↔facts drift). §1 item 5's
> "generator-as-only-writer" scopes to runs/conditions/passes, not the registry,
> so this is consistent with the design. **Implementation lands in sub-step 3**
> (extractor generalisation), after the registry and per-run facts are settled.

---

## Carried-forward gap simulation (full record)

Verdicts: present / ambiguous / missing. Sub-step 1 (registry) is addressed by
this draft; sub-steps 2–3 are recorded so nothing is lost.

| Gap | Sub-step | Finding |
|---|---|---|
| GAP-1 | 1 | `condition-inventory.json` is stale + wrong-grain → not the registry source. **Resolved** (enumerated from live tree). |
| GAP-2 | 1 | Run-vs-condition grain varies by subtree → 5 FLAG-GRAIN umbrellas above. **Resolved pending your verify.** |
| GAP-3 | 1 | Non-runs identified and omitted. **Resolved.** |
| GAP-4 | 2 | No per-run facts store exists; `gt_reference` is not uniformly `curator` (55maps runs use a cleaned/student GT — see `results/55maps-cleaned-gt-evaluation/`). Bulk human work; authored after registry lock. |
| GAP-5 | 2 | Scope is per-run (327 vs 487) and sometimes per-condition (`scope_override`); canonical source `results/evaluation-scopes.md`. |
| GAP-6 | 3 | `extract_passes()` assumes `proposer/<pool>/run_N/`; only 8 run roots have a `proposer/` dir. Fusion/aggregation-only runs (`wbf/*`, `h8-v2` scales) consume *other* runs' pools → needs cross-run pass references. |
| GAP-7 | 3 | Verifier-pass extractor handles one `run.meta.json` per dir, but `pv-diag-384` has 88 (per-condition passes). Many-pass shape unhandled. |
| GAP-8 | 3 | (carry-forward) Verifier `n_tiles_processed = request_count` is wrong semantics (per-candidate-crop, not tiles). Decide: keep + document, derive true tile count, or null. |
| GAP-9 | 3 | Possible third `*.meta.json` shape in older Era-1 `retest/*` (batch-API meta without `per_item_metadata`). Verify when generalising the extractor. |

---

## Deferred follow-ups

- **Contradiction A — RESOLVED (2026-05-30): dot→hyphen (option A1).** §1A's
  worked example and its changelog were corrected (`consensus-384-t1.0` →
  `consensus-384-t1-0`) and the no-dots constraint documented inline.
- **Deferred (user request): rename dotted *directories* to match their slugs.**
  Two cases, of unequal cost:
  - `outputs/55maps-text-high-t0.3-generalisation` →
    `outputs/55maps-text-high-t0-3-generalisation` — cheap and clean (few
    references); safe to do in the rename follow-up.
  - `outputs/h11/consensus-384-UNINTENDED-T1.0` (the `T1.0` carries a dot) —
    **caveat**: §1A *explicitly decided not to rename this directory* (~150
    references; identity already decoupled via the neutral `run_id`). A rename
    here reopens that decision and is not "cheap". Recommend leaving the dir
    as-is and relying on `directory_path` + `historical_aliases`; revisit only
    if the dotted dir actually breaks tooling.
  - (The `verifier-t-pilot/T0.0|T0.5|T1.0` dirs also carry dots but are
    *condition*-level, not runs.)

## What I need from you to proceed

1. **Verify the 28-run enumeration** — split/merge any of the five FLAG-GRAIN
   umbrellas; confirm the omitted non-runs; correct any hypothesis tag.
2. **Rule on contradiction A** (dot→hyphen vs relax the pattern).
3. **Rule on contradiction B** (promote draft to `results/` + flip the generator
   to read the registry).

On your verified edits I promote the registry to `results/run-registry.json`,
then move to sub-step 2 (per-run facts), starting with the runs whose facts are
most machine-supported (the `55maps-*` runs with `post_run_report.md`, and the
already-extracted `gold-standard-v2`).
