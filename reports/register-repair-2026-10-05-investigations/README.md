# Register repair: the investigation records

> **Last revised**: 2026-10-07 (a second known case: `d31-other-legs.md`'s
> "`pv-diag-256` has no proposer meta"). See [§ Changelog](#changelog) for
> revision history.

Four read-only investigations that a subagent wrote during Session 160
(2026-10-04/05) for the register repair
(`reports/register-repair-2026-10-05.md`). They were kept in the session's
scratchpad and are preserved here at session close because the rulings cite
their substance.

| File | Question | Informed |
|---|---|---|
| `d30-grid-2026-08-18.md` | How to add grid-2026-08-18's proposer passes | D30 |
| `d31-other-legs.md` | Which real legs sit outside the register | D31 |
| `archaeology-section-4.md` | The launch archaeology's § 4 findings A to E | D34-D37 |
| `d40-archive-groups.md` | How to register the archive survey's unsure groups | D40 |

**Read them as working records, not as findings of record.** Each states the
commit it read. Where a ruling (`planning/pi-decisions-2026-09-20.md`), the
repair report or a later report differs, the later document holds. Two known
cases:

- `d40-archive-groups.md` is where the text track's missing examples first
  surfaced. The verified account is `reports/manipulation-check-2026-10-05.md`
  and `planning/text-track-transmission-2026-10-05.md`.
- `d31-other-legs.md` § 4 says "`pv-diag-256` has no proposer meta". That holds
  only for `outputs/` and `results/`, the trees the survey's `cost_audit.json`
  sidecars cover (its item 5). The run's six proposer passes, with their metas,
  are tracked under `archive/outputs-non-production-tile-sizes/`
  (`text-baseline/text-t0.0/run_1`, `text-n5/text-t0.7/run_1..5`), archived there
  by `276e4ca80`. Pull request #25's reviewed bindings `pv-diag-256-text-baseline`
  and `pv-diag-256-text-5of5-union` (`results/manipulation-gate-bindings.json`)
  are the verified account.

## Changelog

### 2026-10-07 — a second known case (d31, pv-diag-256)

**Trigger**: pull request #25 (merged `439ffd7ac`) found the pv-diag-256
proposer passes, with metas, under `archive/`; the PI approved resolving the
stale records on 2026-10-07. The README now lists `d31-other-legs.md`'s
"`pv-diag-256` has no proposer meta" as a second known case beside d40's, as a
bulleted list. The four working records themselves are unchanged: the README is
where their known supersessions are recorded.

**What did NOT change**: every investigation file; the table.

**Landed in**: the commit that adds this entry, on branch
`stale-notes-2026-10-07`.

### 2026-10-05 — Original publication

The README for the four Session 160 investigation records (D30, D31, D34-D37,
D40), preserved from the session scratchpad at `dc156f4e9`, with one known case
(d40's text-track finding).
