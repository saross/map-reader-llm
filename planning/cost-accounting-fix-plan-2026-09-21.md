# Cost accounting: diagnosis and fix plan

**Status**: RULED 2026-09-21 (S157): D11–D18 all as recommended, D17 to
be verified, D18 amended (published-rate check with a flag to the PI);
see `planning/pi-decisions-2026-09-20.md`. Work packages proceed in order.
**Update 2026-10-03 (Session 158)**: WP3 built on branch `wp3-cost-basis`
(register regenerated, overrides seeded, C3 re-run); the frontier cost axis
PROMOTED out of WP5 to a new WP4b on the PI's instruction. What building WP3
found is in § 8; it changes three of this plan's premises.
**Trigger**: the S157 coverage check found the passes register booking the
3.7 image campaign at US$1,061 against an audited US$415, and the PI asked
why the live feedback during runs is accurate to cents while the recorded
figures keep going wrong, given the billing reconciliations of August and
September.
**Method**: four fresh-context investigation lenses (live messages; meta
writers; artefact and consumer inventory; capability scan of Google's
billing and pricing surfaces), each read-only, each anchored to file and
line; the `/review-implementation` protocol applied to the design. Every
figure below was re-read at source this session.

---

## 1. The four questions, answered

### 1.1 What are the "estimated" and "actual" costs shown live?

Two different families of message reach the PI during a run.

**The K-ladder drivers** (`scripts/run_k_ladder_tier_e.py`,
`scripts/run_k_ladder_phase2_verifier.py`) print a rung header with an
estimate and a completion line with the flex cost. The estimate is
`candidates × US$0.000693`, a per-candidate rate calibrated by the June
token-load audit (`run_k_ladder_tier_e.py:170,289`). The "actual" is
recomputed from the leg's own token counts at the flex rate card,
`(input × 0.25 + (output + thinking) × 1.50) / 1e6`
(`run_k_ladder_phase2_verifier.py:167-195`); it never reads the meta's
`cost_estimate`, and its docstring says why: the meta prices at list with
`discount: 1.0` whatever tier ran. For the 31 K-ladder rungs on disk the
estimate and the actual agree to between US$0.0001 and US$0.0244 per
rung, and the actual agrees with `scripts/audit_verifier_cost.py` to six
decimal places.

**The September image rows** (both campaigns) had no driver print. After
each leg drained, the session agent ran `scripts/audit_verifier_cost.py`
or `scripts/audit_proposer_cost.py` over the leg's metas and compared the
result with the card's projection; the post-run reports label those
figures "Audited" (`outputs/gemini3-image-55map-2026-09-16/post_run_report.md`
§ 2, e.g. K = 3 arm 2 US$40.5813 against a US$40 projection).

So in both cases the live "actual" IS the audited basis: fresh input,
cache-read input and output-plus-thinking priced separately at the tier
that ran, from the run's own token counts.

One qualification, found by the capability scan and confirmed against
the invoice CSV this session: the auditors price the 3.7 and 3.8 cache
read at the standard rate, US$0.075 per million, on the stated ground
that cache reads are the same at every tier
(`scripts/audit_proposer_cost.py:101-106`). That is true of Gemini 3
Flash (invoiced at US$0.0500 per million, no tier suffix) and false of
3.7 Flash, which the August and September invoices bill at US$0.0378
and US$0.0362 per million on flex, half the standard rate. On the 3.7
image campaign's 2,123 million cached proposer tokens that is a
US$79.61 overstatement of the audited proposer total (US$369.44 cited;
US$289.83 on the rate card of record, re-audited on sapphire 2026-09-21
under WP1). The September verifier legs and
every Gemini 3 leg are unaffected (no cached tokens, or a tier-invariant
cache rate). The 2 percent reconciliation of 2026-09-11 predates the
cache-heavy 3.7 legs.

### 1.2 Why are the live figures accurate?

Because the auditors implement the rule the September billing
reconciliation validated against Google's invoices: audited token basis
and invoiced spend agree within 2 percent
(`reports/billing-reconciliation-2026-09-11.md` § 3). The K-ladder
agreement to cents is narrower than that and is a self-consistency check
on the token model (estimate and actual share one rate card and one
tier), not a check against a bill; the reconciliation is the check
against the bill.

### 1.3 Why are the recorded figures wrong?

The register (`results/passes-manifest.json`) does not read the auditors.
It copies each meta's `cost_estimate.total_cost_usd` verbatim
(`scripts/generate_post_run_report.py:570` proposer, `:674` verifier),
and that block is written by `lib_llm_metadata.estimate_cost`
(`scripts/lib_llm_metadata.py:1262-1352`), which is wrong in ways that
depend on when and where the pass ran:

| Defect in `estimate_cost` or its callers | Effect | Status |
|---|---|---|
| No cache-read rate in the table; `total_input_tokens` (which includes cached tokens) priced whole at the input rate (`:1327`) | Cache-heavy legs 2.5 to 3.3 times too high (3.7 image proposer pass 1: 80.8 % cached, meta US$201.05 vs audited US$81.92) | **open** |
| Verifier call site passes no tier discount (`scripts/run_pv.py:2290`), realtime flex and Batch API alike | Every verifier leg exactly 2 times too high (`verify_k5_arm2_replicate`: meta US$20.41 vs audited US$10.20) | **open** |
| Proposer realtime applies the flex discount unconditionally (`4_detect_mounds_batch.py:1354`), ignoring `--service-tier standard` | A standard-tier run would record half its bill | **open** |
| Unknown model falls through to a silent `default` of 0.50 / 3.00 (`:1313-1322`) | 3.7 priced as Gemini 3 (1.5 times too low) on 55 metas, 2026-08-28 to 09-01 | fixed for 3.7/3.8 keys 2026-09-04 (`73658c579`); the silent fallthrough remains |
| Thinking tokens omitted | Understated on high-thinking runs (thinking was 86 % of one pass's output bill in June) | fixed 2026-09-04 |
| Batch chunk merge writes only `total_cost_usd` from the chunk sum; every other cost field stays chunk 0's (`lib_batch_api.py:1876-1910`) | Four metas whose `input + output ≠ total` | **open** |
| Recovery and cleanup merges add dollars rather than re-pricing tokens, drop `cost_basis` and `list_*`, keep the original's `pricing_used` (`lib_llm_metadata.py:1603-1620`) | Merged metas cannot say which basis their dollars are on; the June 2 to 3 times double counts came through this path | partially mitigated (overlap warning; per-pass split since 2026-09-14) |
| Early runners wrote zero `usage_stats` | 817 of 1,538 metas (the retest and h11 families, 2026-03 to 04) carry `total_cost_usd: 0.0` with no tokens behind it | unrecoverable from metadata |
| **The auditors** price the 3.7/3.8 cache read undiscounted (`audit_proposer_cost.py:101-106,118-121`) | 3.7 cache-heavy legs overstated: US$79.61 on the 3.7 image proposer pool (§ 1.1) | **open** |

The register therefore carries at least four cost conventions keyed to
the pass's date, none labelled: registered totals are 2.5 times audited
on the image rows and about 0.5 times on the August 3.7 text leg. The
project's own notation key (§ 8) names the audited basis as the citable
one and calls the runner's estimator an over-recorder, but never binds
`passes-manifest.cost_usd` to any term.

### 1.4 Why did the reconciliations not fix it?

Every fix since June landed one layer downstream of the register:

| Fix | Layer touched | Register touched? |
|---|---|---|
| June token-load audit (2026-06-12) | cost-manifest generator (`run_generalisation.py --pricing-tier`, opt-in; default still `recorded`), Pareto v2, four `cost_manifest.json` | no; the file is not named |
| Billing reconciliations (08-29, 09-11) | reports and paper prose; the invoice CSV | no |
| r7-gaps-deltas § 2 (09-11) | Results draft cells | no |
| PI decision D5 (09-20) | the two auditors (model read from the meta) | no |

Across all eight history documents the passes register is named zero
times. Worse, the verification apparatus certifies it: the C3
re-derivation ledger reports `cost_usd` MATCH on 1,132 of 1,132 rows,
because it defines correctness as agreement with the meta
(`scripts/rederive_manifest_fields.py:347-352`). A wrong basis is
structurally invisible to every check the project runs.

---

## 2. Consumers, mislabels, and the one signed row at risk

**Consumers of the register's `cost_usd`.** The uplift supplement labels
it correctly ("runner-estimator; NOT the § 8 audited basis", 346 rows).
The run reports inject a caveat. The H6 registered analyses call it
"audited per-pass cost_usd" (`scripts/h6_registered_analyses.py:49,712`)
and gate on it: analysis row `h6-a09-cost-gate`, **signed 2026-09-17**,
quotes cost ratios built from the register column against audited
Pareto dollars. That is the one signed claim resting on the mislabel.
`pass-budget-pareto-v2` (signed) is on the audited basis and is not
affected.

**Mislabelled "audited" figures** (runner estimate or list-halved, called
audited): `h6_registered_analyses.py:49,712` and its `a09_cost_gate.json`
and findings; `h13_overlap_analysis.py:223,245`; `verify_h13_overlap.py:282`;
`grid_analysis.py:474,498` and `grid_verifier_analysis.py:400-410`;
`results/stride-2026-08-25/findings.md:22`; `results/analyses-manifest.md`
h13 row; `final_board_build.py:153-190` (`FAMILY_COST`: two families
all-in, two proposer-only, unmarked; TM understated about 23 percent),
inherited by `build_k_ladder_tables.py`. The uplift supplement's build
report points readers at two of these as the places where "genuine
audited cost" exists.

**Unlabelled projections presented as costs**: `results/paper-tables/cost_retrospective.json`
(no basis field; runner estimate plus simulated batch), the hand-written
`outputs/55maps-image-generalisation/post_run_report.md` ("Total:
$364.70"), and the § R6 table of the Results draft (projected 55-map
dollars beside measured GS dollars, flagged R6-14 in the claims
inventory).

**Live hazards**: `run_generalisation.py cmd_all` regenerates
`cost_manifest.json` on the `recorded` basis, so a re-run silently
overwrites the June audited manifests; the K-ladder drivers hard-code
Gemini 3 flex rates and would understate a 3.7 leg by 28 percent with
no warning.

---

## 3. Review of the implementation space

### 3.1 Capability scan (what else exists)

Retrieved 2026-09-21 from Google's documentation (the pricing page
self-reports "Last updated 2026-09-16 UTC") and from the project's own
invoice CSV.

- **What the API returns.** Every response, realtime and Batch, carries
  `usageMetadata` with `promptTokenCount` (which "includes the number of
  tokens in the cached content"), `cachedContentTokenCount`,
  `candidatesTokenCount`, `thoughtsTokenCount`, and per-modality
  details. **No price field.** A `serviceTier` field exists in the wire
  format but reads `SERVICE_TIER_STANDARD` on all 128,521 Batch
  responses on disk, so it does not identify the billing tier; the
  `x-gemini-service-tier` response header is documented for the
  priority-inference path and is capturable through the installed SDK's
  `sdk_http_response.headers`, but whether the plain `generateContent`
  endpoint emits it is unverified (no API call was made).
- **Actual billed cost, programmatically.** The Cloud Billing API and
  the Budgets API expose no spend. The only path is the **BigQuery
  billing export**: hourly rows per SKU per project, cost in the
  account currency with a per-row `currency_conversion_rate`,
  typically available within a day, append-only. It is **not
  retroactive**: enabling it today recovers nothing before today. The
  Gemini API on the AI Studio path attributes to the Cloud project and
  no finer (labels unsupported), so per-run attribution is by hour
  window; this project's legs are sequential, which makes that
  workable.
- **Rate card, programmatically.** The Catalog API lists SKUs with
  prices in a chosen currency, and the `cloud_pricing_export` table
  lands a daily list-and-account price per SKU in the same dataset as
  the cost rows, so reconciliation becomes a join on SKU id. The SKU
  grammar on this account separates flex, batch and caching (for
  example `Generate content input token count gemini 3.7 flash image
  flex caching`), confirmed from 128 invoice rows. Thinking has no
  separate 3.x SKU; it is inside output.
- **Pricing today, per million tokens, USD.** 3.7 and 3.8 Flash:
  standard 0.75 in / 3.75 out (thinking included) / 0.075 cache read;
  batch and flex halve all three, cache read included. Gemini 3 Flash
  Preview: 0.50 / 3.00 / 0.05, batch and flex halve input and output
  but the cache read is "Same as Standard". Cache storage is
  tier-invariant. **Every headline rate doubles on 2027-01-01**, so any
  hand-maintained table without validity dates mis-costs every run
  after New Year.
- **The SDK** has no pricing helper; `count_tokens` is a pre-flight
  estimate that is itself an API call.
- **Open-source practice.** LiteLLM's cost map is the only one carrying
  3.7/3.8 batch, flex and reasoning rates, but it fetches over the
  network at import unless pinned, carries no validity dates, and has
  no batch or flex *cache* rate (the exact field this project gets
  wrong). Pydantic's `genai-prices` is dated and pinned in the wheel but
  has no batch tier for Gemini. Langfuse keys prices on
  `(model, tier, usage type, start date)`, which is the shape that makes
  both defects above unrepresentable. No open-source project reconciles
  reconstructed cost against a cloud invoice; that join is bespoke.

**What this changes.** The audited basis is the right idea and the wrong
authority: it is a hand-typed card that has now been wrong twice (3.7
rates; 3.7 cache tier). The invoice, or its BigQuery export, is the only
authority, and the rate card must be validated against it.

### 3.2 Exploitation review (are we using what we have?)

- The per-response `usage_metadata` already carries every token class
  the audited formula needs, and the register rows already carry
  `tokens: {input_billed, input_cached, output, thinking, total}`
  (`generate_post_run_report.py`). The register prices none of it; it
  copies a dollar figure computed elsewhere from the same numbers.
- Two correct pricing implementations exist (`audit_proposer_cost.py`,
  `audit_verifier_cost.py`: three token classes, per-model card with a
  cache rate, tier discount on input and output only, raise on an
  unknown model). They are not the function the runners call.
- The tile-presence builder's `verifier-costs.json` is the exemplar of
  labelled cost: a `basis` per leg (`audited`, `published`, `unaudited`),
  a `_README`, an agreement tolerance, null rather than a fallback.
  Nothing else in the register does this.
- The invoice CSV the PI exports (`reports/billing/gemini-spend-by-sku.csv`)
  is read by hand once per reconciliation; no script compares a month's
  audited sum with its invoiced sum.

### 3.3 Quantitative audit

| Dimension | Current | After the plan |
|---|---|---|
| Register cost basis | runner estimate, four conventions, unlabelled | audited from tokens, one function, labelled per row |
| Register error, 3.7 image row | US$1,061 recorded vs US$415 audited (2.56 times) | 0 by construction (the register IS the audit) |
| Passes priceable from tokens | 529 of 1,339 carry tokens; all 1,339 carry a dollar figure | 529 audited; 810 null with `cost_basis: unrecorded`; the four 55-map generalisation runs from the June per-item audit |
| Checks that would catch a wrong basis | none (C3 ledger checks fidelity to the meta) | register-vs-auditor agreement test; monthly invoice reconciliation gate |
| API spend to fix | US$0 | US$0 (every figure re-derives from committed metas) |
| Compute | — | one register regeneration on sapphire (minutes); auditor runs over 43 runs (minutes) |

### 3.4 Recommendation

Significant redesign warranted, but small in code: one cost function,
one writer, one labelled register field, one reconciliation gate. The
alternative of labelling only (leave the numbers, add `cost_basis:
runner-estimate`) is honest but leaves a factor-of-two error published
in the register and does not stop the next consumer calling it audited.

---

## 4. Design

### 4.1 One cost function

A single `price_usage()` in `scripts/lib_llm_metadata.py` (or a new
`scripts/lib_cost.py` that both the runners and the auditors import),
with this contract:

1. **Three token classes**: fresh input = `prompt − cached`, cache-read
   input, output + thinking. Gemini's `prompt_token_count` includes the
   cached tokens; subtract before pricing.
2. **One rate card**, keyed `(model, tier, usage type, valid from)`
   with usage type in {input, cached input, output, cache storage},
   pinned in the repository as data (not code), each entry carrying its
   source (the pricing page and, where one exists, the invoice SKU and
   month that confirmed it) and its validity window, so the 2027-01-01
   step is a second row rather than a silent break. Seeded from
   LiteLLM's map with its revision and etag recorded as provenance,
   then validated entry by entry against the invoice CSV before use.
   Stamped into every `pricing_used` block so a figure re-derives later
   without the code.
3. **Raise on an unknown model.** No `default`. An alias table maps
   `gemini-3-flash` and `gemini-3-flash-preview` to one card explicitly.
4. **Tier from the run's recorded configuration** (`service_tier` or the
   batch marker), never from a constant at the call site. Discount
   applies to fresh input and output; the cache-read rate is
   tier-invariant.
5. **Stamp everything**: model, card version, tier, the three token
   counts billed, the three rates, the basis (`audited`), so that
   `input + cache + output = total` is checkable from the block itself.
6. **Null, not zero**, when a meta reports no usage: `cost_usd: null`
   with `cost_basis: unrecorded` and `n_responses_with_usage: 0`.

The auditors become thin wrappers over the same function (they keep
their leg-summing and recovery-register logic, which is about *which
metas*, not *what rate*).

### 4.2 One writer, merges re-price

Every call site that writes `cost_estimate` (the two proposer paths, the
verifier path, the legacy verifier, the chunk merge, the recovery and
cleanup merges, the generalisation cost manifest) calls the one function
on **summed tokens**, deduplicated by item id. No path adds dollars. The
merged block therefore always satisfies its own arithmetic and carries
the basis. The old block key stays `cost_estimate` for compatibility,
with `schema: cost/2` inside it.

### 4.3 The register prices its own tokens

`generate_post_run_report.py` stops copying the meta's dollar figure.
For each pass it prices the `tokens` block it already extracts, through
the one function, at the tier the meta records, and writes:

- `cost_usd` on the audited basis;
- `cost_basis`: `audited` | `published` | `unrecorded`;
- `cost_source`: the card version and tier used, or the report cited.

The passes schema gains the two fields (schema change, branch and PR).
The `_README` of the manifest states the basis in one sentence. The
rendered markdown gains a basis column.

**Published basis** covers the twelve legs the S156 close block listed
as un-auditable (cleanup overwrote the main meta): they take the
post-run report's figure, as the tile-presence builder already does, with
the report cited in `cost_source`.

### 4.4 Checks that see the basis

- **C3 re-derivation**: the ledger's `cost_usd` claim becomes "equals the
  one function applied to the row's tokens at the row's tier", not
  "equals the meta". A meta whose own block disagrees with the register
  by more than US$0.01 is reported, not certified.
- **Register-vs-auditor test** (tier 1): for a fixed set of committed
  legs, the register row equals the auditor's leg total.
- **Mutation sentinel**: a test that flips the cache rate to the input
  rate must go red.
- **Monthly invoice gate** (new script, `scripts/reconcile_invoice.py`):
  reads the invoice rows (the PI's SKU export under `docs/costs/`,
  gitignored, until the BigQuery export has accrued; the export's rows
  thereafter) and the register, sums both per billing month and per SKU
  family in USD at the invoice's own conversion rate, and reports the
  gap per SKU; a gap over 5 percent on any SKU family fails. The gate
  is what catches a wrong rate on one component, which a total-only
  comparison hides (the 2 percent agreement of September was a total).
  The August and September months are the first fixtures.
- **Applied-tier capture**: the runners record the tier the request
  asked for; WP2 also records the `x-gemini-service-tier` response
  header when present, so a downgraded request is booked at the rate it
  was billed at. Verified on the first live leg after WP2 lands, under
  the API call review gate.
- **Vocabulary binding**: `docs/methodology/notation-key.md` § 8 binds
  `passes-manifest.cost_usd` to "audited"; `signature-policy.md` gains
  one sentence: a signature covers the basis of any cost the row quotes.

### 4.5 What is not changed

- No historical meta is rewritten in place. Re-priced blocks are written
  as a sidecar `cost_audit.json` beside each meta by a one-off
  back-fill (archive-never-delete), and the register reads tokens, not
  the block, so the old blocks can stay as the historical record.
- No API spend. No re-run of any leg.
- The 817 zero-usage metas stay zero-usage; their passes become `null`
  with `cost_basis: unrecorded`, and the four 55-map generalisation runs
  keep their June per-item audited totals as `published` at run level.

---

## 5. Work packages

| WP | Deliverable | Tests | Where | Branch |
|---|---|---|---|---|
| 0 | This plan ruled; decisions D11–D18 below recorded in `planning/pi-decisions-2026-09-20.md`; **the BigQuery billing export enabled by the PI in the billing console the same day** (it is not retroactive; every day unenabled is a day lost to hand exports) | — | console | — |
| 1 | `price_usage()` with the rate card as dated data (`data/pricing/gemini-rate-card.json`), alias table, tier handling, null-vs-zero; auditors refactored to call it; the S156 figures that carry no cached tokens reproduce byte for byte (US$10.2033, US$6.4909, US$189.47, US$233.63) and the cache-heavy 3.7 figures move by the documented amount (§ 1.1), recorded in the affected post-run reports' changelogs | tier-1 unit tests; a red sentinel per defect class (cache rate by tier, unknown model, thinking, merge, validity date) | local | branch + PR (touches `lib_llm_metadata.py`, ~200 lines) |
| 2 | All writers call WP1 on summed tokens; merges re-price; `cmd_all` uses the audited basis or refuses | tests per writer; a merge-consistency test (`input + cache + output = total`) | local | same PR as WP1 |
| 3 | Passes schema `cost_basis`, `cost_source`; generator prices from tokens; `_README`; markdown column; C3 ledger semantics. **Built 2026-10-03** (§ 8): tier evidence ladder (`scripts/lib_pass_cost.py`) over committed evidence (`data/pricing/billing-day-tiers.json`, `run-log-tiers.json`, `tier-attestations.json`, `cost-overrides.json`, derived by `scripts/derive_tier_evidence.py`); recovery fragments summed; recovery-merged metas read per-item sums; register regenerated; C3 re-run | schema round-trip; register-vs-auditor test; C3 claim test — **39 tests, three mutations red** | local + sapphire | branch `wp3-cost-basis` + PR |
| 4 | Back-fill: `cost_audit.json` sidecars for every meta with usage; hypothesis table re-projected; the tile-presence `verifier-costs.json` re-run; the September row of `reports/billing/gemini-spend-by-sku.csv` re-derived from the invoice (FX 1.3904, not the August 1.4389 placeholder). The register regeneration, the run-report projection and the `published` legs moved INTO WP3's PR (the drift tests needed them) | drift checks green; ALL VALID | sapphire | PR from WP3 |
| 4b | **BUILT 2026-10-04 on branch `wp4b-frontier-cost` (design `planning/wp4b-frontier-cost-design-2026-10-04.md`; walkthrough for the PI `reports/wp4b-frontier-repricing-2026-10-04.md`). D19 amended the same day: one UNIFORM discounted tier for every configuration; scope widened to all three frontiers (board, GS Pareto v2, both K-ladder phases); Phase 2 families at their own measured passes. `scripts/lib_frontier_cost.py` + `data/pricing/frontier-configurations.json`; the board's efficiency frontier gains the 3.7 runs; a Phase 1 defect (the fourth cell priced as stride B) corrected; the three signed rows await the PI's signature notes.** **Frontier cost axis — PROMOTED 2026-10-03; basis ruled D19: each configuration priced at the tier it was MEANT to run at, never penalised for an API usage error; superseded executions excluded (D22); floors completed from comparable legs. (PI: costs are how the Pareto frontier is computed, and the frontier is a paper result).** Replace `FAMILY_COST` (`scripts/final_board_build.py:153`: 13 hand-entered figures on a stated mixed basis, nine 3.7-campaign families `None` and dropped from the efficiency table) with figures derived from the register per family — proposer passes x N/K plus the verifier legs the family's cells use — each carrying its basis, so the frontier plots an interval where a tier or a leg is unresolved. Settle the six lower-bound verifier legs (IM, TH7, T03, TM, stride A, FOURTH) from the June backup metas or carry them as bounds. Known movement: **IM proposer US$195.40 -> US$359.65** (its explicit-cache passes billed standard, § 8.3); TH7, T03, TM and the uplift reproduce the June audit within cents per pass | a builder test that every family figure traces to register rows; the frontier membership before and after, reported to the PI | sapphire | branch + PR |
| 5 | Mislabels corrected (ten sites in § 2; `FAMILY_COST` moved to WP4b); `cost_retrospective.json` gains a basis; the hand-written post-run report gains the caveat; K-ladder drivers take the model from the config | one test per script that its "audited" function calls WP1 | local | small PRs, one per artefact family |
| 6 | `reconcile_invoice.py` reading the console exports in `docs/costs/` (D17 revised: no BigQuery), the August/September fixtures, and a `docs/methodology` note giving the monthly export routine — which console page, which filters, where the file goes — so it takes minutes | fixture test at the 2 percent gap the reconciliation found | local | main |
| 7 | Signed rows re-read: `h6-a09-cost-gate` re-derived on the audited basis with a dated signature note (D9 pattern) if the ratios move; every analysis outcome quoting dollars checked against the new register | — | — | main, with the PI |

Effort: WP1–3 about two sessions of agent work plus audit; WP4 one
sapphire regeneration; WP5–7 one session. Every PR gets the two-lens
audit and a re-audit, as today's work did.

---

## 6. Decisions required

- **D11 — Basis of record.** The register's `cost_usd` is the audited
  basis (recommended), or the runner estimate labelled as such.
- **D12 — Null versus zero.** Passes with no recorded usage publish
  `null` with `cost_basis: unrecorded` (recommended), or keep `0.0`.
- **D13 — Published fallback.** The twelve overwritten legs carry the
  post-run report's figure as `published` (recommended), or `null`.
- **D14 — Historical metas.** Left as written, with audited sidecars
  (recommended, archive-never-delete), or rewritten in place.
- **D15 — Invoice gate tolerance.** 5 percent per month (recommended;
  the reconciliation found 2 percent with aborted runs unrecorded).
- **D16 — The signed H6 cost gate.** Re-derive and annotate under the
  D9 pattern (recommended), or leave with a dated note that its basis
  was the runner estimate.
- **D17 — Enable the BigQuery billing export now** (recommended; PI
  action in the billing console; standard export to a dataset in the
  map-reader-llm project; the console CSV workflow continues until it
  has accrued a month).
  *Revised 2026-09-21 (evening)*: ABANDONED after two attempts; the
  console exports the reconciliations already used are the source of
  record for the invoice gate. See `planning/pi-decisions-2026-09-20.md`.
- **D18 — Rate authority.** The pinned dated card validated against
  invoices is the authority (recommended); LiteLLM and the pricing page
  are sources it cites, never the figure of record.
  *Amended at ruling*: WP1 also ships `scripts/check_published_rates.py`,
  which reads the model rows of Google's pricing page and compares them
  with the card; any difference is a flagged report for the PI to confirm
  in AI Studio or the Cloud Console before the card is edited. It never
  edits the card itself.

---

## 7. Risks

- **The rate card is still hand-maintained.** The scan (§ 3.1) says
  whether Google exposes it programmatically; if not, the pinned card
  with a `verified_on` date and the monthly invoice gate are the
  controls.
- **A schema change touches every register consumer.** WP3's tests
  enumerate them (§ 2 list); the C3 ledger change is the one with
  semantics, not just a field.
- **Re-pricing may move numbers a signed row quotes.** WP7 reads every
  dollar in a signed outcome against the new register before anything
  is republished; the D9 signature-note pattern records what moved. The
  known movement is the 3.7 cache correction (§ 1.1): the 3.7 image
  campaign's audited proposer total falls by about US$80, and its
  post-run report, card stop-rule minutes and the Results draft's § R7
  cells that cite it are refreshed under the revision policy.
- **The 2027-01-01 rate doubling.** Handled by the dated card; a test
  asserts that a run dated 2027-01-02 prices at the new row.

---

## 8. What building WP3 found (2026-10-03, Session 158)

Every figure below was re-read at source in the session; the console
exports in `docs/costs/` (gitignored) are reduced to committed evidence by
`scripts/derive_tier_evidence.py`.

1. **No meta records its tier, and the one label that looks like a record is
   a constant.** From 2026-08-18 (`d0a709059`) the real-time writer stamped
   `discount_reason: "Gemini real-time flex (50 % of list, as per Batch API)"`
   whatever tier ran. The register's tier is therefore inferred from
   evidence (batch markers, run logs, launch manifests, `cost/2` records, PI
   attestations, and the invoice's Pacific-time billing days, which are
   US Pacific per `reports/billing-reconciliation-2026-09-11.md` § 3.1), each
   item cited in `cost_source`.
2. **"All campaign spend is flex" (S157 carry-forward, notation key § 8) was
   false.** The pipeline gained `--service-tier` on 2026-04-09 (`2a2cd81c7`);
   no flex SKU was billed before 2026-04-08. Gemini standard-tier spend over
   December to September: **USD 1,582.72**, so **USD 791.36** of discount
   forgone, USD 341.53 of it before flex existed in the pipeline and
   **USD 449.83 after** (per-month invoice FX; Obs 495).
3. **A live defect: the explicit-cache path drops the tier.**
   `scripts/4_detect_mounds_batch.py` builds a fresh `GenerateContentConfig`
   for a request with a context cache (`--use-cache`) and omits
   `service_tier` (block from `76a2cc719`, 2026-03-28; flex reached only the
   main path). Such a run logs `Service tier: flex` and bills standard. Found
   by the volume rule: `h8-v2`'s 37 passes produced 23.25 M output tokens on
   2026-04-15 Pacific, when the invoice billed **0.60 M** flex output all
   day. The two runs whose logs record an explicit cache (`h8-v2`,
   `55maps-image-generalisation`) are the two in April's standard window.
   **Not fixed**: the fix (copy `service_tier` into the cached config) needs
   a one-request probe that the API accepts flex with an explicit cache,
   which is an API call for the PI to approve; meanwhile a guard refusing
   `--use-cache` with `--service-tier flex` would prevent a recurrence.
4. **The register's `tokens` column double-counted 14 passes.** The
   2026-05-02 recovery merge summed the original run's usage into the
   cumulative usage (`IM` x5, `TH7` x5, `gold-standard-v2` x4); the June
   token-load audit found it (§§ 3.2, 3.4), the register never took it up.
   Fixed: such metas read their per-item sums.
5. **Recovery fragments were missing from the cost**: 118 M tokens on 57
   passes. Each fragment is now priced at its own tier and date.
6. **Thirty verifier legs cannot be fully priced from their metas** (a
   cleanup overwrote the main meta). Two carry their post-run report's figure
   (`published`, `data/pricing/cost-overrides.json`). One (`gemini37-screen`
   swap38) kept its main leg as a tracked `run.meta.main-*.json` and is priced
   from both. The other **28 are floors** (`audited-lower-bound`, US$1.01 in
   all): five listed in the overrides file, the rest detected because the
   meta accounts for under 90 % of its leg's `probabilities.json` results.
   Their real spend is NOT in the register's total. Four sit under frontier
   incumbents (IM, TH7, TM; T03's was wrongly listed and is audited: its meta
   records the whole 9,910-call leg).
7. **C3 had not completed since 2026-07-29**: it parsed every cited source
   as JSON and crashed on a cited `run.log` and a gzipped meta. Rebuilt and
   re-run: every cost field certifies (`cost_usd` 1,339 MATCH; fragments,
   stamps and basis label 527; bounds 211 + 211). Reading run_pv's `item_id`
   cleared 126 `status` false alarms (540 to 414 between committed C3
   reports); the **414** non-cost MISMATCH verdicts
   that remain (wall clock and end time on recovery passes, tile counts,
   `model_requested`, retries) predate this work and are queued for a look,
   since some may be the same kind of parsing gap.
8. **The register on the audited basis**: **US$3,088.53** published (288
   audited, 211 upper bound, 28 lower bound, 2 published, 810 unrecorded),
   with the tier uncertainty bracketing it down to **US$2,828.71**; it was
   US$4,674.00 on the runner estimate. The invoices total **USD 5,554.83**
   over December to September; the difference is the 810 unrecorded passes,
   the 28 floors' missing spend, superseded executions, and unregistered
   traffic (layer 3: top-down, by work units). (Corrected 2026-10-03 before
   merge: this item first counted the Gemini 3 row's two `pre-rerun`
   verifier legs, about 62 M input tokens, as superseded spend. They are
   snapshots of the same Batch API jobs their legs' live metas price; see
   item 15.)
9. **Two downloads were missing** because billing days are Pacific:
   2026-04-14 (`h10`, 14.3 M output) and 2026-06-02 (`n1-pro-rerun-384`). The
   2026-08-28 and 08-31 re-exports of 2026-10-03 lack the project filter
   (they carry another project's Gemini 3.5 traffic); the documented
   filtered exports of 2026-09-11 are used instead.
10. **For WP6**: per-day volumes bound the residue jointly where single
    passes cannot be pinned (2026-04-16: unresolved register output 36.45 M
    against 21.09 M flex billed, so at least 15.4 M was standard); September
    bills Gemini 3.6 Flash with no registered pass; the 3.7 cache read on the
    September batch legs bills at the standard cache rate (AUD 0.10428/M =
    USD 0.075/M at FX 1.3904); the card's `gemini-3-flash-preview` note
    "billed US$402.08 against US$419.64" repeats the AUD-for-USD comparison
    corrected on 2026-09-11.
11. **Five audit rounds** (`/audit`: two fresh-context lenses, then four
    re-audits of the fixes, each on the Opus tier). Each round found real
    defects in the previous round's fixes, none critical after round 1:
    a CLI `cost/2` tier outranking the cached path; a resumed fragment
    narrowing on one informative end day; run-level proposer logs pinning
    verifier legs (and then a looser "mentions a verifier" test doing the
    same); C3 certifying by default in four places; the run reports adding
    ceilings and floors into one sum; a cleanup-overwritten verifier class
    the overrides file missed. 142 test cases (99 functions) now pin the rules; each round's
    fresh mutations turned the suite red. Full tier-1 on sapphire: 3,424
    passed.
12. **Decisions for the PI** — RULED 2026-10-03 as D19-D23
    (`planning/pi-decisions-2026-09-20.md`); the list below is kept as asked:
    - The TH7 verifier's main leg survives only as a gitignored
      `run.meta.json.pre-recovery-*.backup` (9,131 calls; with the live 74,
      the June audit's whole leg at US$6.42). Force-adding that one 6 KB
      file would let the register price a frontier incumbent's verifier
      instead of a US$0.05 floor.
    - swap38's main leg is recorded under `--service-tier flex` in
      `planning/gemini38-screen-2026-09-04.md`; a tier attestation would
      take it from an upper bound (US$1.69) to audited (US$0.85).
    - Superseded executions (`pre-rerun` metas) are excluded from the pass
      cost; confirm they belong only in the honest total.
    - The `pv-diag-384` Pro baseline legs carry batch markers, yet no Gemini
      3 Pro batch SKU was ever invoiced (US$0.96; a probable mislabel).
    - The live cached-path defect (§ 8.3): approve a one-request probe
      before the runner fix, or a guard refusing `--use-cache` with flex.
13. **Queued, not fixed in WP3** (the fifth audit round, 2026-10-03, found no
    critical or medium defect in WP3's code; these predate it or are latent):
    - `n_candidates_verified` falls back to request counts on 85 verifier rows
      (`generate_post_run_report._verifier_candidates`): 37 record nothing
      and should be null, not 0; 20 count errored requests as completions
      (2,657 over); 4 read a cleanup-overwritten meta. Count
      `finish_reason_counts["success"]` and return null when nothing is
      recorded. The coverage detector shares the request fallback, so the
      same fix tightens it: an errored request can make a partial leg look
      whole. A non-cost field on 85 rows: its own small PR and audit.
    - The 414 non-cost C3 MISMATCH verdicts (§ 8.7).
    - Latent, no committed case: the command splitter is not quote-aware
      (`'a;b'` cuts a following switch) and does not split `N&cmd`; the
      instant comparisons raise on a naive timestamp (every cited stamp is
      offset-aware UTC).
14. **Settled after the PI's rulings of 2026-10-03** (D19-D23):
    - **The runner defect is fixed and tested live.** `cached_call_config`
      copies the full request config (`2df65047e`). The live probe
      (`outputs/tier-cache-probe-2026-10-03/direct.json`) reproduced the
      defect (the pre-fix cached config on a flex launch was served
      `standard`) and the fix (served `flex`); four adjacent runs of the fixed
      runner served every request at its requested tier, flex or standard,
      cached or not. The tracker now records the served tier per request
      from the `x-gemini-service-tier` header, and the coster believes it
      above everything else (`applied-header`).
    - **Cleanups no longer overwrite main records**: the verifier cleanup
      merges since `94bc5c7d9` (2026-09-14, tested); proposer resumes merge
      since `1ce1a982d` (2026-04-27); `merge_recovery_meta.py`, the tool that
      double-counted TH7 and IM, now refuses a cumulative input.
    - TH7's verifier is audited from its force-added backup (D20); swap38 is
      attested per its notes (D21); superseded executions have a ledger
      (D22); the frontier will rank configurations at their intended tier
      (D19, WP4b).
    - **Pinning the unresolved tiers (follow-up, not frontier-critical):
      launch-command archaeology.** The session transcripts in
      `~/cc-archives/` hold the executed launch commands with their flags;
      `h10`, `h12-v2` and the 2026-04-16 `library_plus-hp` launches show
      `--use-cache` with `--service-tier flex`, so they ran on the cached
      path and billed standard. A script that matches each executed launch
      to its run directory by output path and records `--use-cache` and
      `--service-tier` per run, as committed and cited evidence, would pin
      most of the April residue. A cached-token fingerprint does NOT
      separate explicit from implicit caching (the adjacent runs without
      an explicit cache got constant implicit hits of 12,187 tokens).
      The 2026-04-14 export pins `h10` at standard already.
15. **Audit rounds 7 to 9 (2026-10-03)** refined item 14. Final state:
    - **The served tier survives every runner.** `run_pv.py verify`
      finalises without per-item records, so the tracker also counts
      responses per served tier at run level
      (`usage_stats.served_tier_counts`, `"unreported"` for none), and
      `merge_meta` sums the counts with the tokens they describe.
    - **The header is believed only where it covers every response.**
      - One tier across all of them pins, above everything; a request
        record it overrules is a note.
      - Several tiers price the fragment across exactly those tiers.
      - Where only some responses reported one, the reported tiers WIDEN
        the candidates the other evidence gives, because the rest may have
        run elsewhere and narrowing would understate. The invoice's day
        set (without the whole-fragment volume rule) and the PI's
        attestation of the meta are set against them as conflicts; a batch
        marker beside them is a note (a real-time cleanup or retry ran
        too).
      - A response served at a tier the rate card does not price makes the
        fragment unpriceable; C3 re-derives that reason independently.
    - **The cached-path rule follows the code a run executed, not the
      clock.** It is lifted only when every commit the meta records
      (`environment.git_commit`, or a merge's `git_commits`, where a part
      with no commit counts as `"unknown"`) is a plain hash descending from
      `2df65047e`, or the header covers every response. The fix reaches
      `main` only when this branch merges, and a run launched from `main`
      meanwhile still drops its tier. The tracker now reads the commit
      once per process, at import, in its own directory: before, it read
      `HEAD` at finalise time in the working directory, so a pull during a
      long run could have named a commit with the fix for code without it.
    - Also: `merge_recovery_meta.py` refuses a shared `run_id` and a
      verifier meta (by script or item prefix); named and globbed preserved
      main legs are deduplicated together, and a named one that would not
      be priced, or does not sit beside its primary, is an error; an
      attestation glob that could never apply says why; the runner refuses
      `tools` beside a cache instead of dropping them.
    - **Corrected before merge**:
      - The superseded ledger's fd-storm entry read "no meta", but the four
        attempts have metas: US$0.11 over the three with usage.
      - **The ledger's two `pre-rerun` entries (US$27.85) were a double
        count**, found by the round-7 re-audit. Batch mode keeps a leg's
        predecessor meta as `run.meta.pre-rerun-N.json` when it rebuilds the
        meta. After a `batch-recover` its results are inside the live meta:
        the Gemini 3 row's K = 1 and K = 5 arm 2 sidecars hold 18,785 of
        22,785 and 16,000 of 45,786 results of the SAME jobs, and no request
        was billed twice. They are withdrawn (kept, with the reason); the
        ledger's priced total is US$0.11. The entries had also named the
        wrong model (`gemini-3-flash-preview`; the metas say
        `gemini-3.7-flash`). D22 was put to the PI with those two entries
        as its example; its principle stands.
      - A1 and D21 cited a later documentation commit (`69a081b2c`) for the
        code live at swap38's launch: `scripts/run_pv.py` was last changed
        by `2ce4536ea` and `scripts/lib_verifier.py` by `4bb33b7e2`, both
        unchanged at `21a34339f`.
    - **Verification.** Each round ran two fresh-context lenses
      (implementation, test adequacy); rounds 8 and 9 found no critical
      defect. Every fix carries a mutation that turns a test red (round 7:
      28; lens-B survivors: 13; lens-A fixes: 8; round 8: 10; round 9: 13, one
      of which survived until its test moved to a fresh interpreter).
      **The round-9 fixes were mutation-tested but not re-audited by fresh
      lenses**: they change conflict labels and when the commit is read,
      never a price, and the rounds had converged. No register figure
      moved in rounds 7 to 9: US$3,094.05 on the audited basis, US$2,859.81
      at the tier lower bound; every C3 cost verdict MATCH.

---

## Changelog

### 2026-10-04 — WP4b built: the frontier cost axis from the register (Session 158)

D19 amended (uniform discount tier) and WP4b widened to all three
frontiers on the PI's rulings of 2026-10-04. Built on branch
`wp4b-frontier-cost`: the library and mapping, the board refreshed in
place (its tiering untouched), Pareto v2 and both K-ladder phases
regenerated on sapphire, drift guards for every output, two audit lenses
and a re-audit. What moved: the board's efficiency frontier (3.7 runs
priced for the first time); the K-ladder Phase 1 fourth-cell ladder
(defect corrected) and the arms' N < 5 rungs; Phase 2's dollar levels
(MINIMAL image 1.4x to 1.9x). What did NOT move: any F1, MCC, tier,
group or pairwise result; Pareto v2's efficient sets; any K-ladder's
efficient rungs. Details: `reports/wp4b-frontier-repricing-2026-10-04.md`.

### 2026-10-03 (rounds 7 to 9) — the served tier; ledger corrected (Session 158)

§ 8.15 added; § 8.8 corrected. What changed: the tracker's run-level
served-tier count and its commit read at import; the coverage rule for the
header; the cached-path rule decided by the run's recorded commits; and
three corrections made before merge (the fd-storm ledger entry; the two
`pre-rerun` entries withdrawn as a US$27.85 double count, so the ledger is
now US$0.11; the swap38 citation). What did NOT change: every register
figure (US$3,094.05; tier lower bound US$2,859.81; 312 audited, 188 upper
bound, 27 lower bound, 2 published, 810 unrecorded) and every C3 cost
verdict (MATCH). Commits `429dfac1f` to `fb3767404`.

### 2026-10-03 (later) — four audit rounds; § 8 figures refreshed (Session 158)

| | WP3 build | after four audit rounds |
|---|---|---|
| register total | US$3,086.02 | US$3,088.53 (swap38's main leg priced) |
| tier lower bound | US$2,827.06 | US$2,828.71 |
| lower-bound legs | 6 (overrides) | 28 (5 overrides + detected by coverage) |
| C3 non-cost MISMATCH | 538 | 414 (126 `status` false alarms cleared; the round-4 commit message's "545 to 414, 131" counted an uncommitted build) |
| tests in `tests/test_lib_pass_cost.py` | 39 cases | 142 cases (99 functions) |

What did NOT change: no proposer pass's cost moved in rounds 2 to 4; the
frontier incumbents' figures are as in WP4b; the register-equals-auditor
figure (US$233.6295) holds. § 8.11 records the rounds, § 8.12 the five
decisions they surfaced for the PI.

### 2026-10-03 — WP3 built; § 8 findings; frontier cost axis promoted to WP4b (Session 158)

WP3 on branch `wp3-cost-basis`. Three premises of this plan moved:

| | before | after |
|---|---|---|
| campaign tier | "all campaign spend is flex" | flex only from 2026-04-08, and not on the explicit-cache path (§ 8.2, 8.3) |
| the register's tokens | the primary meta's `usage_stats` | primary plus recovery fragments; per-item sums where the recovery merge doubled the count (§ 8.4, 8.5) |
| the twelve overwritten legs | `published` from their reports | eight register passes: two `published`, six `audited-lower-bound` (no report publishes them) |
| register total | US$4,674.00 (runner estimate) | US$3,086.02 audited (US$2,827.06 at the tier lower bound) |

The PI's instruction of 2026-10-03 (items 1–4 approved) on the unresolved tier: price at the highest
candidate as a labelled upper bound, with a dated attestation file to pin
tiers as evidence arrives. `FAMILY_COST` moved from WP5 to a new WP4b,
promoted. WP4 narrowed: the register regeneration, the run-report
projection and the overridden legs went into WP3's PR.

### 2026-09-21 (evening) — PR #20 ready for merge after three audit rounds

Branch `cost-accounting-wp1` at d28af1f9a. Two-lens audit, fix, re-audit,
fix, narrow re-audit, fix: no critical remains. Defects closed on the way
that the plan had not named: the merge did not know the unpriceable block
it introduced (a pass half priced would have read as audited); the chunk
merge's fold inflated a mixed pass by a third; a cleanup across the
2027-01-01 step would have been priced at the 2026 row; the batch
patcher's zero stub dragged an audited block to the legacy path; nulls
crashed five consumers and collapsed to zero in a sixth. The card gains
`gemini-3.5-flash` (fourteen June metas; three June invoice SKUs confirm
its flex rates). Full tier-1 on sapphire 3,285 passed. The rate check
reads the live page exactly on today's date and on 2027-01-01. Awaiting
the PI's merge; D17 (BigQuery export) still to be verified in the console.

### 2026-09-21 (later) — WP1 and WP2 on a branch, PR #20

WP1 and WP2 delivered on `cost-accounting-wp1` (PR #20, five commits
through ca39d3f7a): the rate card as data, `scripts/lib_cost.py`, the
writers and merges re-wired, the auditors delegating, the D18 published-rate
check (36 of 36 rates equal the live page of 2026-09-21). Acceptance
re-audited on sapphire: US$6.4909, US$10.2033, US$189.4718 and US$233.6295
reproduce; the 3.7 image proposer pool re-audits at US$289.8262 against the
US$369.4409 cited (the cache correction of § 1.1, to the cent). Two-lens
audit and full tier-1 run in progress before merge.

### 2026-09-21 — Original draft (Session 157)

Written from four read-only investigation lenses and the
`/review-implementation` protocol; no code changed, no API spend.
