# Sonnet gate verdict — protocol-errata genre: FAIL (2026-08-02, Session 125)

**Ruling under test**: `phase3-rulings-2026-07-31.md` § 5 — Sonnet runs
the mechanical tail free after the b014 PASS, but "new task kinds or
radically different target sources get a fresh Opus-duplicate
comparison before Sonnet scales there, and doubt escalates to Opus".

## Design

- **Sonnet batch**: b015 (`docs/methodology/preregistration/protocol-errata.md`
  lines 1–393, Sonnet, this session; archived to
  `015-sonnet-gate-evidence-2026-08-02.json` in this directory).
- **Opus reference**: `calib-b.json` (protocol-errata lines 1–248,
  Opus, Session 122 calibration) — the overlap range 1–248 is the
  comparison window. The Sonnet agent was told not to read calib-b.
- Comparison run by the session main loop: value-verbatim multisets
  and claim-line coverage over the window, span-convention differences
  (Obs 378 class: `128×128` vs `128`+`128`, `~$286` vs `$286`,
  bracketed lists vs elements) paired off before judging.

## Result — Sonnet coverage is a strict subset

| measure (lines 1–248) | Sonnet b015 | Opus calib-b |
| :--- | ---: | ---: |
| claims | 27 | 45 |
| value spans | 55 | 70 |
| lines covered only by this model | 0 | 13 |

The 13 Opus-only lines carry ~14 genuine checkable claims Sonnet
missed entirely — not span conventions. Registration-critical members:

- L59: preregistered temperature **1.0** and counterfactual **0.1**
  (the would-have-run value without the fix)
- L95/140/169: the **20 m** spatial matching tolerance (three claims)
- L163: **7** integration tests added by the E7 fix; L157: **Three**
  union_all() call sites replaced
- L30: **three** OSF companion documents realigned; L57: **five**
  execution fields added
- L187: **Three** crop-extraction options; L190: `fill_value=0`;
  L222: **50 m** recognition-failure threshold; L235: hard positive
  pool size **4**; L70: counterfactual **100 %** API failure rate

## Verdict

**FAIL for the protocol-errata genre.** Contrast with b014
(hypothesis-tracking: line-identical coverage, zero missed claims
either way). Dense, correction-block-heavy registration errata are not
a ruling-4 Sonnet class.

**Caveats recorded honestly**: (1) the gate design told the Sonnet
agent its 1–248 range would be superseded at assembly, which may have
depressed effort on the comparison window — a design flaw; future
gates must not mark the comparison range superseded. (2) The b014 PASS
was on the same directory but a different genre (tracking table vs
errata prose); the genre boundary, not the directory, is the operative
variable. Neither caveat rescues the batch: the misses are real and
the residual range (249–393) has no Opus cover either.

## Actions taken (this session)

1. Sonnet 015.json archived here (never deleted); **b015 re-extracted
   by Opus** into `c4-extraction/015.json`.
2. **b016–b023 (protocol-errata continuation) reassigned to Opus.**
3. **Decisions-log/execution-plan genre check**: the same wave ran
   b007–b013 on Sonnet under the b014 precedent; an independent Opus
   duplicate of b007 (`007-opus-duplicate-2026-08-02.json`, this
   directory) gates acceptance of those batches before they enter the
   corpus. Verdict appended below when compared.

## b007 gate (decisions-log genre) — PASS (appended 2026-08-02)

Opus duplicate `007-opus-duplicate-2026-08-02.json` (72 claims / 144
values) vs Sonnet `c4-extraction/007.json` (67 claims / 144 values),
decisions-log.md lines 1–308:

- Value differences are overwhelmingly span conventions (unit affixes
  `1047.1m` vs `1047.1`, `128×128` vs `128`+`128`, `>50m` vs `50`,
  `2×` vs `2` — the Obs 378 class; the harness parses both).
- Sonnet-side residue: TWO missed value instances, both restatements
  of values it captured elsewhere — line 60's table-header "(20
  tiles)" (pilot size captured at line 58) and line 217's vendor-
  recommendation "T=1.0" (captured at lines 205/215/221).
- Opus-side residue: THREE number-word claims Sonnet caught and Opus
  missed — line 3 "exactly three documents" (a genuine lodgement-
  scope count), line 117 "two-dimensional ranking", line 186 "one per
  sheet".

Near-symmetric small tails, no one-direction recall gap — the b014
profile, not the b015 profile. **Sonnet batches b007–b013
(decisions-log, execution-checklist, execution-plan) are ACCEPTED.**
The genre boundary this pair of gates draws: tracking/decision-log
prose passes on Sonnet; dense correction-block errata do not.
