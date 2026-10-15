#!/usr/bin/env bash
# Full tier-1 suite at the branch head (single process); pid and rc files.
cd $HOME/scratch/s164-merges-2026-10-13/wt || exit 9
echo $$ > $HOME/scratch/s164-rescore-2026-10-13/logs/tier1/tier1.pid
git log --oneline -1 > $HOME/scratch/s164-rescore-2026-10-13/logs/tier1/tier1.log
OMP_NUM_THREADS=1 $HOME/Code/map-reader-llm/.venv/bin/python -m pytest -m tier1 -q -p no:cacheprovider >> $HOME/scratch/s164-rescore-2026-10-13/logs/tier1/tier1.log 2>&1
echo $? > $HOME/scratch/s164-rescore-2026-10-13/logs/tier1/tier1.rc
