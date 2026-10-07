# API gate, 2026-10-07: T03 same-date re-verification and the modality bridging pair

> **Last revised**: 2026-10-07 (original publication, Session 162). See
> [§ Changelog](#changelog) for revision history.

**Status: AWAITING THE PI's APPROVAL, stage by stage.** Nothing has been
submitted. Costs use the passes register's uniform discounted tier (flex
equals batch; PI ruling D19), per candidate or per tile from the original
legs (`results/passes-manifest.json`, read 2026-10-07). Context:
`reports/w27-replicate-floors-2026-10-06.md` § 6a (the verifier-date check
on text MIN) and § 7 (the modality claim R7.3-22/23).

## 1. Run A: T03 same-date re-verification (55-map, verifier only)

**Why.** The board's T03 3-of-5 cell adds a vote-3 shell verified on
2026-06-06 to a 4-of-5 set verified on 2026-04-26/27. Re-verifying both
sets on one day reads T03's k3 − k4 contrast (+0.009 on the board) under
one verifier date, and gives a three-date drift series for one family
(April, June, October). The PI chose T03 alone (2026-10-07) for its drift
value at low cost.

| item | value |
|---|---|
| Model | `gemini-3-flash-preview`, thinking minimal, T = 0.0, pinned with `--model` so no alias can resolve to a newer release |
| Verifier configuration | `prompts/configs/verify_adversarial-text.json` (as both original legs) |
| Mode | **Batch API** (the original legs ran real time; batch and flex re-invocations of this verifier agree to about 0.001 F1, D4/D8) |
| Inputs | 9,910 4-of-5 crops (`outputs/55maps-text-high-t0.3-generalisation/crops`) and 4,035 vote-3 crops (`results/deployment-oracle-2026-06-06/vote3-verify/55maps-text-high-t0.3-generalisation/crops`), unchanged |
| Calls | **13,945** (3 + 2 batch jobs) |
| Estimated cost | **about US$9.64** (US$6.90 for 9,910 and US$2.74 for 4,035 on the original legs) |
| File API | about 0.8 GB of request files (cap 20 GiB; `preflight_file_storage` runs before lodging; delete after the leg is committed) |
| Output | `outputs/verifier-date-2026-10-07/55maps-text-high-t0.3-generalisation/{verified-k4set,verified-increment}/` (new; nothing original is touched) |
| Dry run | both sets built (9,910 and 4,035 lines; every line T = 0, MINIMAL), no API call |
| Guard override | the 4-of-5 manifest disagrees with its union on 15 `vote_count`s, all 4 → 5: the documented April extractor defect (`results/im-june-pool-grid-2026-09-20/findings.md` § 7, table row `55maps-text-high-t0.3-generalisation`). It changes no crop, no candidate id and no 3-of-5 or 4-of-5 cell, so the launch passes `--allow-stale-manifest`, which logs the reason. **Approval of this run includes this override.** |

**Optional add-on, text MIN (same settings): 12,390 calls (10,170 + 2,220),
about US$8.55.** It would give text MIN four verification dates (April 18,
June 6, June 11, October), the longest drift series the project could have
for one family, and a second family for the same-date contrast. Its 4-of-5
manifest carries the same documented defect (88 candidates, all 4 → 5).

**After the run (offline):** score T03 k3 and k4 under October
probabilities with the § 6a scripts; report k3 − k4 under one date, the
April → October and June → October shifts on identical candidates, and the
flip rates; add to the W2.7 report.

## 2. Run B: the modality bridging pair (gold standard, 487-tile frame)

**Why.** R7.3-22/23 says "text beats image" is a Gemini 3 property: the
within-family text − image gap moved from +0.0549 (Gemini 3) to −0.0115 and
−0.0043 (Gemini 3.7). Its four arms ran on four dates (2026-08-18 to
2026-09-01), and on this corpus same-request runs 20 days apart differed by
0.04–0.06 F1 (S-9). Re-running the arms on one day removes the date
component from both gaps and from the comparison between them.

**Recommended approach: all four arms submitted together, not the two
Gemini 3 arms first.** Running the Gemini 3 pair alone (about US$39) would
settle the Gemini 3 gap on one date, but the comparison the claim rests on
(the gap CHANGE between families) would again span dates, now October
against September. All four together cost about US$30 more and settle the
claim itself. Each arm is re-run exactly as it was (same model, thinking,
temperature, configuration, tiling and K), so the bridge measures the
date, not a design change. The K mismatch inside the original claim
(Gemini 3 at K = 10, Gemini 3.7 at K = 5) is addressed for free: the
Gemini 3 arms' first five passes give a K = 5 rung (two extra verifier legs,
about US$1.50).

| arm (original date) | proposer | passes × tiles = calls | proposer cost | verifier leg(s) | verifier calls | verifier cost |
|---|---|---|---:|---|---:|---:|
| Gemini 3 text (2026-08-18) | `gemini-3-flash-preview`, minimal, T 0.7, text | 10 × 1,398 = 13,980 | US$8.38 | Gemini 3, K = 10 union | about 3,300 | US$2.27 |
| Gemini 3 image (2026-08-28) | `gemini-3-flash-preview`, minimal, T 0.7, image | 10 × 1,398 = 13,980 | US$25.96 | Gemini 3, K = 10 union | about 4,100 | US$2.80 |
| Gemini 3.7 text (2026-08-28) | `gemini-3.7-flash`, low, T 0.7, text | 5 × 1,398 = 6,990 | about US$8.60 | Gemini 3 and Gemini 3.7, K = 5 | about 1,600 | about US$1.43 |
| Gemini 3.7 image (2026-09-01) | `gemini-3.7-flash`, low, T 0.7, image | 5 × 1,398 = 6,990 | US$18.33 | Gemini 3 and Gemini 3.7, K = 5 | about 1,350 | US$1.22 |
| **Total** | | **41,940** | **about US$61** | | **about 10,350** | **about US$8** |

Plus the optional Gemini 3 K = 5 rung legs (about US$1.50). **Grand total
about US$69–71.** All legs on the Batch API (PI ruling 2026-09-18 for 3.7;
the same route for Gemini 3). The swap37 leg's cost is estimated at the
3.7 verifier's per-candidate rate, because its register row records only a
2-candidate cleanup.

**Stages (each its own approval, per the global API gate rule):**

- **Stage 0 (free, one API call):** list the served models, to confirm
  `gemini-3-flash-preview` and `gemini-3.7-flash` are still available. If
  either is gone the bridge cannot be run for that family, and Run A's
  model check is the same call.
- **Stage 1:** the four proposer runs, submitted together (about US$61).
  Configurations are built to mirror each original leg's meta, then
  audited with the pre-launch configuration audit before submission.
- **Stage 2:** union building and extraction (offline, with the union
  provenance guard), then the six verifier legs (about US$8) and the two
  optional K = 5 rung legs.

## 3. What approval covers

1. Run A (T03): Stage 0 and the submission, including the
   `--allow-stale-manifest` override above. Optional: the text-MIN add-on.
2. Run B: approval of the design and Stage 0 now; Stages 1 and 2 come back
   to the PI with their final configurations and the audit verdict.

## Changelog

### 2026-10-07 — Original publication (Session 162)

Written at the PI's request after the verifier-date check (§ 6a of the
W2.7 report). Dry runs for Run A were made on sapphire with no API call.
