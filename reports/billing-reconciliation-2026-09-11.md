# Billing reconciliation: Google Cloud invoices against the audited token basis

> **Last revised**: 2026-09-11 (original publication, Session 153). See
> [§ Changelog](#changelog).

**Purpose**: reconcile what Google actually charged for this project
against the token-basis cost audits the paper cites
(`reports/token-load-audit-2026-06-12.md` for the Gemini 3 campaigns;
`reports/r7-gaps-deltas-2026-09-11.md` § 2 for the Gemini 3.7 leg), and
settle the "3.7 bills at roughly 0.6 × the token basis" expectation that
§ R7.3 of the Results draft carried as a flagged note.

**Sources**: nine monthly Cost-table exports (invoice months December
2025 to August 2026), one account-wide Reports export (SKU totals,
1 January to 30 September 2026), and one Cost-breakdown export (grand
total, 1 December 2025 to 11 September 2026), all downloaded by the PI
from the Google Cloud billing console on 2026-09-11. The files sit in
`docs/costs/`, which is **gitignored** because the repository is public
and the exports carry the billing-account and invoice identifiers. Every
figure below is re-read from those files; none is quoted from memory.

## 1. Three facts about the invoices

1. **Currency is AUD.** Every Cost-table export states `Currency,AUD` and
   a monthly exchange rate (1.5398 in December 2025 down to 1.3949 in
   May 2026; 1.4389 in August 2026). The audits are in USD at Google's
   list prices. Any comparison must convert.
2. **Every invoiced row belongs to the one project.** The Project-name
   column holds a single value, `map-reader-llm`, in all nine months.
   There is no other project on any invoice.
3. **The billed rates reproduce the USD list rates exactly.** August
   2026, Gemini 3.7 Flash flex tier: text output 62,430,515 tokens for
   A$168.44 is A$2.698 per million, which is US$1.875 (flex output) ×
   1.4389. Image input 235,690,988 tokens for A$127.18 is US$0.375 ×
   1.4389. Text input 109,017,948 tokens for A$58.83, the same. Image
   caching input 20,122,880 tokens for A$1.09 is US$0.0375, one tenth of
   the input rate. The rates on file in `scripts/lib_llm_metadata.py`
   (0.75 / 3.75 list, flex 0.5 ×) are therefore the rates Google billed.

## 2. Where the account-wide total and the project total diverge

| Figure | Value (AUD) | Source |
|---|---:|---|
| Sum of invoiced usage, Dec 2025 – Aug 2026 | 6,709.88 | nine Cost tables, `Cost type = Usage` |
| Sum of invoiced tax, same months | 670.99 | nine Cost tables, `Cost type = Tax` |
| Cost breakdown, 1 Dec 2025 – 11 Sep 2026, usage before tax | 6,740.47 | Cost-breakdown export |
| Implied September 1–11 project usage | 30.59 | 6,740.47 − 6,709.88 |
| Reports export, 1 Jan – 30 Sep 2026, SKU subtotals | 7,152.38 | Reports export |

The Reports export exceeds the invoices by A$442.51 net after allowing
for December 2025 (which the Reports range excludes). A per-SKU
comparison locates the excess almost entirely in one line:

| SKU | Invoiced (AUD) | Reports (AUD) | Difference | Tokens invoiced → reported |
|---|---:|---:|---:|---|
| Gemini 3.5 Flash text input, flex | 4.61 (June) | 431.43 | +426.82 | 4.4 M → 409.7 M |
| Gemini 3.5 Flash text output, flex | 6.85 (June) | 25.07 | +18.22 | 1.1 M → 4.0 M |
| Gemini 3.5 Flash flex caching storage and cached input | 0.00 | 15.34 | +15.34 | 0 → 20.0 M |
| Gemini 3.6 Flash text input, flex | 0.00 | 2.31 | +2.31 | 0 → 2.1 M |
| Gemini 3.7 Flash image input, flex (+ caching) | 128.27 | 145.27 | +17.00 | September image-GS run |
| Gemini 3.7 Flash text output and input, flex | 227.27 | 232.07 | +4.80 | September verifier legs |

About A$463 of the difference is Gemini 3.5 Flash and 3.6 Flash usage
in September that no map-reader-llm invoice or cost breakdown contains.
The Reports export was account-wide (it has no project column), so the
most economical reading is that another project on the same billing
account used Gemini 3.5 Flash heavily in September. The map-reader-llm
Flash 3.5 work (the 2×2 role permutation, Session 111) is the June
invoice's A$11.46 and nothing else. **To confirm**: a Reports export
grouped by project over the same range (requested from the PI). Until
then the project total stands at A$6,740.47 before tax, which agrees
with the invoices.

## 3. The Gemini 3.7 leg, August 2026

All 3.7 usage on the August invoice is dated 28–31 August. Billed, in
AUD and converted at the invoice's 1.4389:

| SKU (3.7 Flash) | Tokens | AUD | USD |
|---|---:|---:|---:|
| text output, flex | 62,430,515 | 168.44 | 117.06 |
| image input, flex | 235,690,988 | 127.18 | 88.39 |
| text input, flex | 109,017,948 | 58.83 | 40.89 |
| image input caching, flex | 20,122,880 | 1.09 | 0.76 |
| text input caching, flex | 441,136 | 0.02 | 0.01 |
| standard-tier probes (30 Aug: text out, image in, text in) | 215,219 | 0.43 | 0.30 |
| **total** | | **355.99** | **247.41** |

Audited or reconstructed token-basis spend in the same window (USD, flex):

| Run | Basis | USD |
|---|---|---:|
| 55-map proposer, five passes (`gemini37-55map-2026-08-29`) | audited, per-item metadata (`r7-gaps-deltas` § 2.2) | 144.27 |
| 55-map arm 2 verifier, 3.7 (`verify_arm2`) | audited (`r7-gaps-deltas` § 2.3) | 14.31 |
| GS screen, ten 3.7 passes (`gemini37-screen-2026-08-28`, runs 1–10 + recoveries) | `usage_stats` totals read this session: 20.9 M input, 1.07 M output, 3.89 M thinking | 17.1 |
| Fourth cell verifier over 57,482 candidates (`stride-55map … verify_37`) | **simulated** at arm 2's per-candidate rate (its meta was overwritten by a 29-item cleanup pass) | 64.7 |
| GS swap-37 verifier (791 candidates) and the grid `verify_37` (913) | metas overwritten by cleanup passes; simulated at the same rate | 1.9 |
| Two aborted partial 55-map passes (30 Aug) | no meta on file | unknown |
| **total known** | | **242.3** |

The billed US$247.41 exceeds the known token basis by about US$5, or
2 %, which is the size the two unrecorded aborted passes would plausibly
have. On the output side the match is close to exact: billed 62.43 M
output tokens against 40.05 M (proposer, thinking included) + 3.07 M
(arm 2) + 13.9 M (fourth cell, simulated) + 4.96 M (GS screen) + 0.3 M
(small verifiers) = 62.3 M. On the input side the billed 365.3 M
exceeds the known 334.5 M by 30.8 M, consistent with roughly one
aborted 24,561-tile pass (36.9 M input per complete pass).

**Conclusion for § R7.3**: the "billed at roughly 0.6 × the token basis"
expectation is **refuted**. Billed spend slightly exceeds the audited
token basis, as it should when aborted runs are unrecorded. The 0.6 ×
figure has two candidate origins, both artefacts: the 3.7 metas' own
`cost_estimate`, which priced 3.7 at Gemini 3 rates (0.5 / 3.0 against
0.75 / 3.75, a 0.67 × ratio); or a USD-against-AUD reading (1 / 1.4389
= 0.695). Neither is a property of the SKU. The § R7.3 paragraph should
say the leg's billed cost reconciles to the audited basis within 2 %, in
USD, with the fourth cell's verifier simulated.

## 4. Open questions

1. **The June audit's corroboration currency.** § 10 of
   `reports/token-load-audit-2026-06-12.md` compares "billed $402.08" on
   18 April with an audited US$419.64 and calls it a −4 % match, but
   names no currency. If that dashboard figure was AUD, the USD billed
   was about US$277 (at April's 1.4508) and the match is not a match.
   The PI is asked which console page supplied the 18 April daily.
2. **September SKU rows for the project.** The 3.7 image GS run
   (1–2 September), the fourth cell's cleanup, the 3.8 screen
   (4 September) and the 8 September verifier-stage refresh are not yet
   invoiced. A Reports export filtered to the project for 1–11
   September would close them now; otherwise the September invoice will.
3. **The fourth cell's true verifier load** is unrecoverable from the
   repository (meta overwritten). The billing residual above bounds it
   only jointly with the aborted passes.

## Changelog

### 2026-09-11 — Original publication (Session 153)

Built from the PI's billing-console exports of the same day. No API
spend. Findings: invoices are AUD and single-project; billed rates equal
USD list × exchange rate; the account-wide Reports total exceeds the
project total by September Gemini 3.5 Flash usage attributable to
another project (confirmation pending); the August 3.7 leg reconciles to
the audited token basis within 2 %, refuting the 0.6 × expectation.
