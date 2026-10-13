# Pro thinking probe: Gemini 3.1 Pro at thinking HIGH delivers no thinking at any temperature tested

> **Last revised**: 2026-10-13 (original publication). See [§ Changelog](#changelog) for
> revision history.

- **Run by**: the main session of Session 163 (Claude, Anthropic; Claude Code, model lane
  Opus 5.5), 2026-10-12, under the PI's approval of the model check and the 250-call text
  and image probe with all extras (about US$17), and later up to a 25 % overrun.
- **Ruling**: `planning/pi-decisions-2026-09-20.md` D61 (4).
- **Model**: `gemini-3.1-pro-preview`, served as version `3.1-pro-preview-01-2026` (model
  check, 2026-10-12).
- **Scripts**: `scripts/run_pro_thinking_probe.sh` (v1), `scripts/run_pro_thinking_probe_v2.sh`,
  `scripts/run_pro_thinking_probe_v3.sh`; summary by `scripts/summarise_pro_thinking_probe.py`
  (`summary.json` in this directory).

## 1. Question

The genuine-Pro HIGH passes of 2026-06-03 (`n1-pro-rerun-384`, T = 0.0) recorded zero thought
tokens, and the June 2026 invoice confirmed it (`reports/manipulation-check-2026-10-05.md` § D;
Obs 509). h6 A-06 reads "temperature is the driver" from a contrast of those passes with March
T = 0.7 Pro HIGH passes whose thinking was never recorded. If temperature switched Pro's
thinking on, A-06's temperature effect would partly be a thinking effect. This probe asks
whether Pro, asked for thinking HIGH, delivers thinking at T = 0.0, 0.7, or 1.0.

## 2. Design, and what happened to it

Every flag matches the June run (`scripts/run_n1_pro_rerun.sh`): the same configs
(`detect_brief-text.json`, `library_plus-hp.json`), the model override, thinking HIGH, 384 px
tiles, context caching. Only temperature varies within a modality. Tiles are a seeded sample
of the 487 gold-standard tiles (seed 42): 50 for v1, a seeded 20 of those 50 for v2 and v3.

| Version | Tier, attempts | What happened |
|---|---|---|
| v1 (12:32Z) | flex, up to 15 | Stopped at 12:53Z in its first arm: 273 attempts for 50 tiles. First read as thinking exhausting the output budget; v2 showed the attempts were 503 retries. Per-request records lost (the runner has no interrupt handler). `v1-stopped.md`. |
| v2 (12:56Z) | flex, 1 | First arm: 17 of 20 requests returned 503 UNAVAILABLE ("This model is currently experiencing high demand"); stopped at 13:09Z. |
| v3 (13:10Z) | standard, up to 3 | All five arms ran (to 14:14Z); 503s still dominated, so each arm has few successes. |

The 503s fell on different tiles in v2 and v3 (the three successful tiles of each text T = 0.0
arm do not overlap), so they reflect demand, not the tiles.

## 3. Result

Thought tokens per successful request (finish reason `STOP`); the June rows are the same 50 tiles
from the 2026-06-03 run.

| Arm | Successful requests | Thought tokens | Output tokens |
|---|---:|---|---|
| text, T = 0.0 (v2 and v3) | 6 | 0 in all 6 | 10 in all 6 |
| text, T = 0.7 (v3) | 4 | 0 in all 4 | 6, 10, 49, 136 |
| text, T = 1.0 (v3) | 4 | 0 in all 4 | 10, 10, 46, 321 |
| image, T = 0.0 (v3) | 1 | 0 | 10 |
| image, T = 0.7 (v3) | 5 | 0 in all 5 | 1, 6, 10, 136, 137 |
| June text, T = 0.0 | 150 | 0 in all 150 | median 10 |
| June image, T = 0.0 | 150 | 0 in all 150 | median 16 |

**All 20 successful requests tonight recorded zero thought tokens, at every temperature and in
both modalities**, as all 300 June requests did at T = 0.0. Asked for thinking HIGH on this task,
Gemini 3.1 Pro delivers none, and raising the temperature to 0.7 or 1.0 does not switch it on.

## 4. What it means, and what it does not

- **For A-06.** On today's service the HIGH contrast would compare two temperatures with no
  thinking on either side, so "temperature is the driver" is not confounded by thinking here.
  That is evidence about today's service, consistent with June at T = 0.0; it cannot prove what
  the March T = 0.7 passes did, because their usage was never recorded and same-model drift is a
  standing condition (Obs 508).
- **For H6 and the leaderboard.** The Pro HIGH cells were Pro without thinking; the probe adds
  that higher temperatures do not change that.
- **Odd but recorded.** In June the Pro MEDIUM passes did record a little thinking (per-pass
  means 6 to 43 thought tokens per request), more than HIGH's zero.
- **Limits.** Small samples (1 to 6 successes per arm) because about 80 % of requests failed with
  503s; T = 1.0 and image were tested on the standard tier only.

## 5. Cost

503 responses are not billed. The runner's own estimates: v2's first arm US$0.0047 and v3's five
arms US$0.0461 (per-arm figures in the metas). v1's per-request records were lost; its billed
requests are its successes, at about US$0.0016 each (under US$0.10). The October invoice will
give the billed total. Approved: about US$17 plus up to 25 %.

## 6. Process notes

- The image dry run before v1 created a 14,549-token Pro context cache that a dry run never
  deleted; it was deleted by hand about two minutes later, and the runner is fixed on draft
  PR #34.
- v1's stop note first misread the retries as budget-exhausting thinking; it is corrected in
  place (`v1-stopped.md`, § Correction).

## Changelog

### 2026-10-13 — Original publication

First report of the probe (v1 stopped, v2 stopped, v3 complete), written after v3 finished at
2026-10-12T14:14Z.
