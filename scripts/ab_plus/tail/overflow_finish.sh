#!/usr/bin/env bash
# Render entries whose overflow sidecar exists and checks clean; stamps as the tail did.
# Promoted 2026-09-03 from the S147 scratch driver. Usage: overflow_finish.sh <citekey>...
# Clears a stale .git/index.lock first if no git process holds it (concurrent agents'
# `git status` calls left two behind during the batch).
cd /home/shawn/Code/map-reader-llm || exit 1
[ -f .git/index.lock ] && ! pgrep -x git >/dev/null && rm -f .git/index.lock
for k in "$@"; do
  e="outputs/ab-plus/_work/$k.entry.json"; v="outputs/ab-plus/_work/$k.verdict.json"; o="outputs/ab-plus/_work/$k.overflow.json"
  [ -f "$o" ] || { echo "$k: NO SIDECAR"; continue; }
  varg=""; [ -f "$v" ] && varg="--verdict $v"
  if PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli check --entry "$e" >/dev/null 2>&1; then
    out=$(PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli render --entry "$e" $varg --model claude-opus-5 --run-date 2026-09-02 2>/dev/null | tail -1)
    echo "$k: RENDERED ${out##*(}"
  else
    echo "$k: CHECK FAILED"; PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli check --entry "$e" 2>/dev/null | grep -v PASS | head -5
  fi
done
