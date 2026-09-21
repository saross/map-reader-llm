# Cost accounting: diagnosis and fix plan

**Status**: RULED 2026-09-21 (S157): D11–D18 all as recommended, D17 to
be verified, D18 amended (published-rate check with a flag to the PI);
see `planning/pi-decisions-2026-09-20.md`. Work packages proceed in order.
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
about US$290 on the invoice basis). The September verifier legs and
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
| 3 | Passes schema `cost_basis`, `cost_source`; generator prices from tokens; `_README`; markdown column; C3 ledger semantics | schema round-trip; register-vs-auditor test; C3 claim test | local | branch + PR (schema change) |
| 4 | Back-fill: `cost_audit.json` sidecars for every meta with usage; register regenerated on sapphire; `published` set for the twelve legs; hypothesis table and run reports re-projected | drift checks green; ALL VALID | sapphire | PR from WP3 |
| 5 | Mislabels corrected (ten sites in § 2); `FAMILY_COST` re-derived from the manifests with per-figure provenance; `cost_retrospective.json` gains a basis; the hand-written post-run report gains the caveat; K-ladder drivers take the model from the config | one test per script that its "audited" function calls WP1 | local | small PRs, one per artefact family |
| 6 | `reconcile_invoice.py` and the August/September fixtures; a `docs/methodology` note on how to run it each month | fixture test at the 2 percent gap the reconciliation found | local | main |
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

## Changelog

### 2026-09-21 — Original draft (Session 157)

Written from four read-only investigation lenses and the
`/review-implementation` protocol; no code changed, no API spend.
