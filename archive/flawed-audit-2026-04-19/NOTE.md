# Archived: flawed documentation audit (2026-04-19)

This directory contains the four files of the original documentation
audit committed on 2026-04-19 in commit `8747d726`. They were
superseded on 2026-04-21 by the verified re-run whose artefacts now
sit at `results/documentation-audit/`.

## Why archived

Three known classes of error in the original audit:

1. **Hallucinated cost figures** — e.g. claimed text-MIN cost
   $165.74 with 90.2 % cache hit; actual is $60.79 with 0.0 % cache
   hit (per `outputs/55maps-text-min-generalisation/cost_manifest.json::totals.cost_usd`).
2. **Conflated runs with similar names** — merged the 2026-04-10
   retrospective text-HIGH run at `outputs/55maps-generalisation/`
   with the 2026-04-19 re-run at `outputs/55maps-text-high-generalisation/`,
   reporting a fictional "$359.53" cost that neither run produced.
3. **Wrong Observation number attributions** — blanket Obs 255 across
   all three 55-map runs; actual attributions span Obs 256 (image),
   258-260 (text), 261 (bimodal).

Pattern: fluent prose with plausible-but-wrong numbers. Structural
framework was sound.

## What replaced them

Files under `results/documentation-audit/` (at the time of this note):

- `README.md`, `audit-summary.md`, `priority-backfill.md` — direct
  replacements with cited figures throughout.
- `results-audit-2026-04-21.md` — full run-by-run table; 85 numeric
  claims with explicit file + key-path citations.
- `verification-2026-04-21.md` — adversarial fact-check report from a
  fresh-context verifier agent; 82/85 claims PASS, 0 DEAD citations,
  no silently-wrong uncited figures.

## Why not delete

Per the project's archive-never-delete policy
(`CLAUDE.md`): "archived files should be browsable in the working
tree." Git history alone is not sufficient; this directory keeps the
superseded content accessible for methodology transparency and for
any future audit of the audit process itself.

## Retained for historical reference only

Do NOT cite numbers from these files in the paper or downstream
work. The 2026-04-21 audit is authoritative.

Planning document that drove the re-run workflow:
`planning/doc-audit-rerun-plan.md`.

## Provenance

- Generated: 2026-04-19 (commit `8747d726`)
- Superseded: 2026-04-21 (replacement commit — see git log
  `archive/flawed-audit-2026-04-19/`)
