# Billing reconciliation, 2026-08-29: the Gemini 3 Flash ×1.6 gap

> **Last revised**: 2026-08-29 (SKU check attempted — detailed
> reports lag ~48 h, determination DEFERRED to ~2026-09-02; see the
> changelog). See [§ Changelog](#changelog) for revision history.

**Classification**: post-hoc cost audit, $0 API spend. Read-only analysis of
committed run metadata. No Application Programming Interface (API) call was
made in producing this report.

## 1. The question

The Principal Investigator's (PI) Google Cloud billing console, read
2026-08-29, showed for the trailing seven days:

| Stock Keeping Unit (SKU) | Billed |
|---|---|
| Gemini 3 Flash | $700.01 |
| Gemini 3.7 Flash | $5.28 |
| **Total** | **$705.29** |

The project expectation was roughly $437 (Session 142 ≈ $338, Session 143
≈ $92, plus the Gemini 3.7 screen ≈ $7.4; recorded in
`planning/gemini37-55map-2026-08-29.md` lines 81 and 121–122). The Gemini 3
Flash line is therefore about ×1.6 the expectation.

## 2. Headline

**The gap is a rate gap, not a volume gap.** Every run that could have
produced the billed spend is present and correctly counted in the
repository's committed metadata; the token volumes reconcile against the
documented per-call profiles to the token. What does not reconcile is the
price applied to them.

The decisive arithmetic:

- Recomputed from raw token counts at **flex** rates, the whole in-window
  Gemini 3 Flash corpus costs **$400.63**.
- Even at the **absolute flex ceiling** — charging every one of the
  529,031,196 cached tokens at the full non-cached input rate — it costs
  **$506.43**.
- The billed figure, **$700.01**, exceeds that flex ceiling by **$193.58**.
  No flex-basis accounting of the committed runs can reach it.
- Recomputed at **list** (standard) rates, the same corpus costs
  **$801.26**, and $700.01 sits comfortably inside the list-basis
  uncertainty bracket **[$670.09, $801.26]** spanned by plausible
  treatments of the two sub-rates the repository cannot pin down
  (cached-read pricing and thinking-token pricing).

The best-fitting single explanation, which also accounts for the otherwise
puzzling Gemini 3.7 line, is that **the flex discount is honoured for
`gemini-3.7-flash` but not for `gemini-3-flash-preview`**. All 148 in-window
Gemini 3 runs used the preview model identifier; all 16 Gemini 3.7 runs used
the general-availability identifier. Preview SKUs commonly lack the
discounted service tiers. This is a hypothesis consistent with every number
below, not a confirmed fact — see [§ 9](#9-what-would-settle-it).

## 3. Method and sources

1. **Enumeration.** Every `*.meta.json` under `outputs/**` was parsed
   (1,397 files) and bucketed on the `timestamp.start` field — not file
   modification time. 164 runs fall in 2026-08-22 → 2026-08-29. Both
   proposer metas (`detections-*.meta.json`) and verifier metas
   (`run.meta.json`) were included.
2. **Completeness checks.** `archive/**` was swept separately (1,314
   further metas): **zero** carry an August 2026 start date, so nothing
   in-window has been archived out of `outputs/`. The only other metas on
   disk are under `.claude/worktrees/`, which are duplicate checkouts of the
   same runs, not additional spend.
3. **Costing.** Recomputed from `usage_stats.total_input_tokens`,
   `total_cached_tokens`, `total_output_tokens` and
   `total_thoughts_tokens`. The metas' own `cost_estimate` fields were
   **not** trusted (see [§ 6](#6-why-the-metas-own-estimates-disagree)).
4. **Rates.** Gemini 3 Flash from `reports/token-load-audit-2026-06-12.md`
   lines 30–34: flex $0.25 per 1M input, $0.05 per 1M cached, $1.50 per 1M
   output with thinking included in the output price; standard exactly ×2
   ($0.50 / $0.10 / $3.00). Gemini 3.7 Flash from
   `planning/gemini37-screen-2026-08-28.md` line 52: flex $0.375 per 1M
   input, $1.875 per 1M output including thinking; list taken as ×2.
5. **In-flight runs.** The task anticipated a separate bucket for runs
   stamped 2026-08-29 (the Gemini 3.7 escalation passes 6–10 and the 55-map
   Gemini 3.7 K = 5 run). **No meta on disk carries a 2026-08-29 start**:
   those runs had not written metadata when this analysis ran, so the bucket
   is empty and nothing needed excluding. The latest committed run ends
   2026-08-28T23:23:40 UTC.

### Verification that the token counts are sound

Mean input tokens per call, by campaign, match the documented profiles
exactly: **1,502 per tile** for the 384-pixel text proposers (the value
`reports/token-load-audit-2026-06-12.md` line 52 records), **≈1,780** for
verifier calls, and **20,019** for the image proposer of which **18,907** is
cached prefix. Per-item metadata confirms that `input_tokens` is inclusive
of `cached_input_tokens` (sample item: 20,019 total, 18,909 cached, 1,110
fresh), so the cached tokens are discounted rather than double-counted.
There is no token undercount.

## 4. Per-campaign reconciliation

All figures recomputed from raw token counts. "Out+think" is output plus
thinking tokens, which share the output rate.

| SKU | Campaign | Role | Runs | Calls | Input (M) | Cached (M) | Out+think (M) | Flex $ | List $ |
|---|---|---|---|---|---|---|---|---|---|
| Gemini 3 | `stride-55map-2026-08-25` | proposer | 38 | 387,322 | 581.7 | 0.0 | 43.41 | 210.53 | 421.07 |
| Gemini 3 | `stride-55map-2026-08-25` | verifier | 2 | 57,990 | 103.0 | 0.0 | 8.95 | 39.18 | 78.36 |
| Gemini 3 | `image-b-gs-2026-08-28` | proposer | 32 | 27,981 | 560.2 | 529.0 | 29.61 | 78.65 | 157.29 |
| Gemini 3 | `image-b-gs-2026-08-28` | verifier | 2 | 13,304 | 23.8 | 0.0 | 2.12 | 9.11 | 18.22 |
| Gemini 3 | `stride-phaseb-2026-08-25` | proposer | 43 | 41,253 | 62.0 | 0.0 | 6.37 | 25.05 | 50.10 |
| Gemini 3 | `stride-phaseb-2026-08-25` | verifier | 7 | 17,007 | 29.9 | 0.0 | 2.64 | 11.44 | 22.87 |
| Gemini 3 | `stride-phasec-2026-08-25` | proposer | 11 | 24,831 | 37.3 | 0.0 | 3.71 | 14.89 | 29.78 |
| Gemini 3 | `stride-phasec-2026-08-25` | verifier | 1 | 5,267 | 9.4 | 0.0 | 0.81 | 3.57 | 7.14 |
| Gemini 3 | `grid-2026-08-18` | verifier | 4 | 9,254 | 16.4 | 0.0 | 1.45 | 6.27 | 12.54 |
| Gemini 3 | `h7-escalation-2026-08-28` | proposer | 6 | 2,040 | 3.1 | 0.0 | 0.40 | 1.37 | 2.74 |
| Gemini 3 | `gemini37-screen-2026-08-28` | verifier | 1 | 791 | 1.4 | 0.0 | 0.13 | 0.56 | 1.11 |
| Gemini 3 | `h2c-probe-2026-08-24` | verifier | 1 | 10 | 0.0 | 0.0 | 0.00 | 0.01 | 0.01 |
| **Gemini 3 total** | | | **148** | **587,050** | **1,428.0** | **529.0** | **99.62** | **400.63** | **801.26** |
| Gemini 3.7 | `gemini37-screen-2026-08-28` | proposer | 16 | 7,054 | 10.5 | 0.0 | 2.46 | 8.56 | 17.12 |
| **Gemini 3.7 total** | | | **16** | **7,054** | **10.5** | **0.0** | **2.46** | **8.56** | **17.12** |

Note that the Gemini 3.7 screen's *verifier* ran on Gemini 3 Flash, so it
bills to the Gemini 3 SKU — that row is listed under Gemini 3 above.

**Cross-check against the project's own expectations.** Grouping the
Gemini 3 flex figures by session gives $310.94 for the Session 142
campaigns (stride, grid, `h2c-probe`) against the ≈$338 recorded
expectation, and $89.69 for the Session 143 campaigns (`image-b-gs`,
`h7-escalation`, the Gemini 3.7 screen's verifier) against ≈$92. The flex
recomputation reproduces the project's own accounting closely, which
confirms the enumeration is complete and that the ~$437 expectation was a
flex-basis expectation.

## 5. Candidate explanations, quantified

Each candidate is priced against the Gemini 3 Flash billed figure of
$700.01. "Contribution" is the dollar movement the mechanism produces from
the flex baseline of $400.63.

| # | Candidate | Contribution | Resulting total | Residual vs $700.01 | Verdict |
|---|---|---|---|---|---|
| i | **List rather than flex rates on all Gemini 3 runs** | +$400.63 | $801.26 | +$101.25 | **Necessary.** The only mechanism that can bridge a ~$300 gap. Over-shoots on its own. |
| i-a | List rates, cached reads at the flex cache rate ($0.05/M) | +$374.17 | $774.80 | +$74.79 | Variant of (i); brackets the answer. |
| i-b | List rates, cached reads unbilled | +$347.72 | $748.35 | +$48.34 | Variant of (i); brackets the answer. |
| i-c | List rates, thinking tokens unbilled | +$322.36 | $722.99 | +$22.98 | Closest single-mechanism fit. |
| i-d | List rates, cached reads unbilled **and** thinking unbilled | +$269.46 | $670.09 | −$29.92 | Lower edge of the list bracket. |
| ii | **503-storm retries billed as fresh input** | +$6.04 flex / +$12.08 list | — | — | **Ruled out as a driver.** 12,134 retries against 587,050 successful calls (2.07%); at each campaign's own mean input per call that is 24,162,947 extra tokens, worth $6.04 at flex or $12.08 at list — at most 4% of the gap. |
| iii | **Token undercount in the metas** | $0 | — | — | **Ruled out.** Per-call profiles match the documented values exactly (1,502 text, ≈1,780 verifier, 20,019 image of which 18,907 cached). Nothing is missing. |
| iv | **Spend from other work sharing the billing account** | Unbounded above; bounded at **≤ $29.92** if (i-d) is the true rate structure, and **$0** is fully consistent with the evidence | — | — | **Not required.** The list-basis bracket already contains $700.01. Cannot be excluded — see the visibility limits below. |
| v | **Thinking tokens billed at a rate other than the output rate** | −$78.26 (list basis) if unbilled | see i-c / i-d | — | Plausible contributor. Thinking is only 26,087,219 of the 99,624,631 output-plus-thinking tokens, so it can move the total by at most $78.26 at list rates. |

### Why a reporting-lag explanation does not work on its own

Google Cloud cost data lags. The console was read at approximately
2026-08-29T02:34 UTC (the timestamp on commit `f0531ca8b`, which recorded
the console glance, is 2026-08-29 12:34 +1000), which is 2026-08-28T19:34
Pacific Daylight Time — so the trailing-seven-day window spans roughly
2026-08-22 to 2026-08-28 Pacific and **excludes none of the runs above**;
the latest ends 2026-08-28T16:23 Pacific.

If a uniform reporting lag were trimming the tail, one cut-off time would
have to satisfy both SKU lines. It does not. Under the list basis, the
Gemini 3 cumulative total reaches $700.01 only at about 2026-08-28T05:06
UTC, implying a lag of roughly **21.5 hours**; the Gemini 3.7 line reaches
$5.28 at about 2026-08-28T20:05 UTC, implying roughly **6.5 hours**. The two
are irreconcilable, so lag alone is not the answer — though a few hours of
lag on the Gemini 3.7 line specifically remains very likely, since that
campaign finished barely three hours before the read.

### The Gemini 3.7 line points the same way

The Gemini 3.7 SKU billed **$5.28**, which is *below* its flex
recomputation of **$8.56** and far below its list recomputation of $17.12.
Billing below the flex price means the flex discount was applied to that
model (with a few hours of the last passes not yet posted). The Gemini 3
line simultaneously requires list rates. The two facts are consistent only
if the discount is model-dependent — which is exactly what the preview
versus general-availability split predicts.

## 6. Why the metas' own estimates disagree

The live estimator was not used, and inspection shows why it could not be.

- For cached runs it charges **every** input token at the full non-cached
  rate. On `image-b-gs-2026-08-28/g384_ov192_image/run_1`, `cost_estimate`
  records `input_cost_usd` 6.99664 — that is all 27,986,562 input tokens at
  $0.25 per 1M, ignoring the 26,434,782 cached tokens that attract $0.05.
- It **omits thinking tokens entirely**. The same file's
  `output_cost_usd` prices only `total_output_tokens`.
- For Gemini 3.7 it uses **Gemini 3 rates**: the run_1 meta's
  `cost_estimate.pricing_used` reads `input_per_1m: 0.5`, `output_per_1m:
  3.0` under `model: gemini-3.7-flash`, understating the true input rate by
  ×1.5 and the output rate by ×1.25.

Summed across the in-window corpus the estimator reports $537.44 for
Gemini 3 and $3.43 for Gemini 3.7 — wrong in both directions and matching
neither basis.

## 7. Residual

Against the best-supported model — **list rates on the Gemini 3 Flash
preview SKU** — the repository over-predicts the billed figure by **$101.25
(12.6%)**: $801.26 recomputed against $700.01 billed.

That residual is *fully absorbed* by uncertainty in two sub-rates the
repository cannot resolve, both of which move in the required direction:

- Cached-read pricing on 529,031,196 tokens: worth up to **$52.90** at list
  rates if reads are free rather than charged at $0.10 per 1M.
- Thinking-token pricing on 26,087,219 tokens: worth up to **$78.26** at
  list rates if thinking is not billed at the output rate.

Since $700.01 lies inside the resulting bracket **[$670.09, $801.26]**, no
external or unaccounted spend needs to be invoked. **Whether any part of
the $101.25 is instead reporting lag, a genuine rate difference, or spend
from work outside this repository cannot be determined from repository
evidence.**

### What the repository cannot see

Stated explicitly, so the residual is not over-claimed:

- The billing account's other projects, other API keys, and any non-repository
  script that used the same credentials. The repository has no visibility
  into these at all.
- The service tier actually *requested* at launch. The argparse default in
  `scripts/4_detect_mounds_batch.py` line 1787 is `flex`, and
  `scripts/run_recovery_rerun.py` line 63 sets `SERVICE_TIER = "flex"`, but
  `scripts/lib_verifier.py` line 235 defaults `service_tier` to `None`, and
  **no run log survives for any in-window campaign** — the script prints
  `Service tier: …` at launch, but zero `.log` files exist under the seven
  campaign directories, and none of them wrote a `launch_manifest.json`
  recording the tier the way the legacy `55maps-*` campaigns did.
- The service tier actually *honoured* by the API, which is the crux and is
  only visible in the billing export's SKU description.
- Cache-creation and cache-storage charges. Per-item metadata shows
  `cache_creation_tokens: 0` on sampled items, but storage at $1.00 per 1M
  tokens per hour is not recorded anywhere in the metas.

## 8. Implication for the historical cost record

If flex is not honoured for `gemini-3-flash-preview`, the consequence
reaches backwards. The legacy generalisation campaigns audited in
`reports/token-load-audit-2026-06-12.md` ran on **the same
`gemini-3-flash-preview` identifier** (verified across the 37
`outputs/55maps-*` metas), and their `launch_manifest.json` files record
`"service_tier": "flex"` — that is, they *requested* flex, which is what the
audit priced them at. That audit's headline of **~$722 flex** for the
generalisation set would then be understated by close to ×2.

This should be treated as a flagged consequence requiring confirmation, not
a correction to make now. It does not affect any scientific result — only
the cost-per-deployment figures quoted in planning and paper text, including
the "$97 per 55 sheets" and "$0.000687 per verifier call" style anchors.

## 9. What would settle it

Repository evidence has been taken as far as it goes. Three console or
export views would disambiguate immediately:

1. **Cloud Billing detailed export / "Cost table" report, grouped by SKU,
   for 2026-08-22 → 2026-08-28.** Google names the tier in the SKU
   description itself. Seeing `Gemini 3 Flash Preview Input (Standard)`
   rather than `… (Flex)` — or the absence of any flex SKU line for the
   preview model while one exists for `gemini-3.7-flash` — confirms or kills
   the central hypothesis outright. This is the single most decisive view.
2. **Cost table grouped by SKU *and* day, same range.** Per-day totals let
   the reconstruction in [§ 4](#4-per-campaign-reconciliation) be checked
   campaign by campaign — the stride campaigns land on 08-23 to 08-26
   Pacific, `image-b-gs` and `h7` on 08-27, the Gemini 3.7 screen on 08-28 —
   and separate genuine rate effects from reporting lag. It also shows
   whether the input, output, and cached-read SKUs are billed as separate
   lines, which resolves the cached-read and thinking-token sub-rates.
3. **Cost table grouped by project (and by billing account, if more than one
   project bills to it).** This is the only way to bound candidate (iv):
   spend from work outside this repository sharing the credentials. If a
   single project accounts for the whole $700.01, external spend is zero and
   the residual is entirely a rate and lag question.

A fourth, cheap and forward-looking: **restore launch-time tier
provenance.** Have the campaign drivers write a `launch_manifest.json`
recording `service_tier` (as the legacy `55maps-*` runs did) and retain the
`run.log` that already prints the tier. Both were absent for all seven
in-window campaigns, and their absence is why this reconciliation has to
argue from prices rather than simply read what was requested.

## Changelog

### 2026-08-29 (later) — SKU check: partial post, ALL Flex; hypothesis re-ranked

The PI attempted the § 9 decisive check the same day. Two findings:

1. **The detailed (SKU-grouped) reports lag ~48 hours**: the
   model-level view reads ~$800 total, but only ~$250 has posted to
   the detailed reports. Full determination deferred — **re-check on
   or after ~2026-09-02**.
2. **Every charge posted so far is on "Gemini 3 Flash Flex" SKUs.**

Finding 2 re-ranks the hypotheses. The posted ~$250 covers roughly
the window's first days, whose flex-basis recomputation is of the
same order — consistent with the flex discount being HONOURED. If
the remaining days also post as Flex, the detailed total should land
near the § 5 flex basis ($400.63–$506.43), NOT at $700 — implying
the model-level "$700.01" is a **display-basis artefact**: a
usage-page rendering priced at list rates (the § 5 list bracket
[$670.09, $801.26] contains it) while actual billing applies the
flex SKUs. Under that reading there is no billing anomaly, true
window spend is ≈ $400–500, and the token-load-audit flex anchors
stand. The alternative (later days post at Standard SKUs) remains
open until the reports catch up. Until settled, cost planning keeps
the conservative list basis for `gemini-3-flash-preview` ceilings;
paper cost figures remain untouched either way pending the
~2026-09-02 re-check.

### 2026-08-29 — Original publication

Written in response to the PI's console glance of 2026-08-29 showing
Gemini 3 Flash $700.01 and Gemini 3.7 Flash $5.28 for the trailing seven
days, against a project expectation of roughly $437. Enumerated 164
in-window runs across 1,397 `outputs/**` metas plus a 1,314-meta
`archive/**` sweep (no in-window hits), recomputed all costs from raw token
counts under flex and list bases, and tested five candidate explanations.
Conclusion: the flex-basis ceiling of $506.43 cannot reach the billed
$700.01, so the discrepancy is a rate gap; the list basis brackets the
billed figure at [$670.09, $801.26]; the preview-versus-general-availability
service-tier split is the best-fitting mechanism, and the billing export's
SKU descriptions would settle it. Residual against the plain list basis:
$101.25 (12.6%), absorbed by cached-read and thinking-token sub-rate
uncertainty.
