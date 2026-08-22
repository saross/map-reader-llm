# Test suite conventions

This directory holds the project's pytest suite. The project
`CLAUDE.md` points here for the tier-marker pattern; the markers
themselves are declared in `pytest.ini` at the repository root.

## Tier markers

Every test must carry exactly one tier marker. As of 2026-08-23 the
suite holds ~1,922 tests (1,895 tier1, 27 tier2) and zero unmarked
tests — a state restored by the Session 137 audit follow-up after 103
tests were found carrying no marker.

- **`tier1` — critical path.** Fast, hermetic tests: unit tests over
  synthetic fixtures, monkeypatched I/O, no network, no API spend,
  no dependence on large committed data files. The full tier-1 suite
  runs in ~3 minutes and is the gate for every commit that touches
  scripts (project `CLAUDE.md` § Testing).
- **`tier2` — high-value, heavier.** Integration tests and tests that
  read larger committed artefacts (e.g. leaderboard tiering,
  standardised-reference scoring, phase-4 integration). Run before
  campaign launches and at session close, not necessarily on every
  commit.

## The pattern

Mark at module level, immediately after the imports:

```python
import pytest

pytestmark = pytest.mark.tier1
```

A module mixing tiers marks individual tests or classes with
`@pytest.mark.tier1` / `@pytest.mark.tier2` instead. When adding a
new test module, choose tier1 unless the tests are slow (> ~1 s
each), read bulk committed data, or exercise multi-script
integration paths.

## Running

```bash
# The per-commit gate
python -m pytest -m tier1 -q

# The heavier set
python -m pytest -m tier2 -q

# Guard against unmarked tests creeping back in (expect 0 collected)
python -m pytest --collect-only -q -m "not tier1 and not tier2"
```

New scripts require accompanying tests, and significantly changed
scripts require extended ones (project `CLAUDE.md` § Testing).
