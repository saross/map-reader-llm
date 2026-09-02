#!/usr/bin/env bash
# Deterministic tail of the per-source pipeline: quote check (must PASS),
# then render with verdict + provenance stamps. Usage: finish.sh <citekey>...
cd /home/shawn/Code/map-reader-llm || exit 1
for k in "$@"; do
  e="outputs/ab-plus/_work/$k.entry.json"; v="outputs/ab-plus/_work/$k.verdict.json"
  if [ ! -f "$e" ]; then echo "$k: NO ENTRY"; continue; fi
  chk=$(PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli check --entry "$e" 2>/dev/null | tail -1)
  rc=$?
  varg=""; [ -f "$v" ] && varg="--verdict $v"
  if PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli check --entry "$e" >/dev/null 2>&1; then
    out=$(PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli render --entry "$e" $varg --model claude-opus-5 --run-date 2026-09-02 2>/dev/null | tail -1)
    ov=$(python3 -c "import json,sys; print(json.load(open('$v')).get('overall','-'))" 2>/dev/null || echo "-")
    echo "$k: RENDERED ${out##*(} verdict=$ov"
  else
    echo "$k: CHECK FAILED -> $chk"
  fi
done
