# Pro thinking probe, v1: stopped during its first arm

- **Launched**: 2026-10-12T12:32:50Z (`scripts/run_pro_thinking_probe.sh`, commit `c4e6305d9`).
- **Stopped**: 2026-10-12T12:53Z by the main session (Claude, Session 163), during arm
  `text-t0.0` (Gemini 3.1 Pro, thinking HIGH, T = 0.0, flex tier, 50 tiles).
- **Why**: the rate governor had counted 273 request attempts for 50 tiles (35 completed,
  3 failed), with a mean latency of about 299 seconds per request and no 429 or 503 errors.
  The runner retries a response whose finish reason is MAX_TOKENS, or that has no content
  parts, up to `--max-retries` (default 15) times (`scripts/4_detect_mounds_batch.py`, the
  finish-reason and content checks after `generate_content`). Both triggers mean the model's
  thinking used up the 8,192-token output budget. Each retry is a billed call, so the arm was
  heading past the approved call count and budget.
- **Spend**: unknown exactly; upper bound about US$13.84 (273 attempts × (1,502 input tokens
  × US$1 per million + 8,192 output tokens × US$6 per million), Pro's flex rates). The
  October invoice will give the billed figure.
- **What survives**: `text-t0.0/detections-detect_brief-text-3.1-pro-2026-10-12.geojson`
  (detections written so far) and `_run_log.txt`. The per-request token records were held in
  memory and were lost when the process was stopped; the runner has no interrupt handler.
- **Reading, not yet measured**: in June the same request (`n1-pro-rerun-384`, the same 50
  tiles) took a median 3.7 seconds with zero thought tokens on every request; tonight requests
  took about five minutes and most exhausted the output budget, which points to heavy thinking
  at T = 0.0 today. Version 2 (`scripts/run_pro_thinking_probe_v2.sh`) measures it, one
  attempt per tile, so every request's tokens are recorded.

## Correction (2026-10-12T13:10Z): the cause was 503s, not thinking

Version 2's first arm (`v2-text-t0.0/`, one attempt per tile, flex tier) recorded every
request: 17 of 20 returned `503 UNAVAILABLE` ("This model is currently experiencing high
demand"), and the 3 that succeeded finished with `STOP`, 10 output tokens, and **zero thought
tokens**, as in June. So the v1 attempts above were 503 retries with backoff, not responses that
exhausted the output budget, and the "reading" above (heavy thinking at T = 0.0 today) is wrong.
503s are not billed: v1's spend is roughly its successful requests at about US$0.0016 each
(under US$0.10), not the upper bound given above. Version 3
(`scripts/run_pro_thinking_probe_v3.sh`) moves to the standard tier.
