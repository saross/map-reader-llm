#!/usr/bin/env bash
# Full tier-1 suite in the second clone, so no test can touch the run tree.
S=$HOME/scratch/kladder-mcc-join-2026-10-30
echo $$ > $S/logs/suite.pid; echo RUNNING > $S/logs/suite.state
cd $S/suite || { echo "FAILED cd" > $S/logs/suite.state; exit 9; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 MPLBACKEND=Agg
$HOME/Code/map-reader-llm/.venv/bin/python -m pytest -m tier1 -q -p no:cacheprovider
rc=$?; echo $rc > $S/logs/suite.rc
if [ $rc -eq 0 ]; then echo DONE > $S/logs/suite.state; else echo "FAILED $rc" > $S/logs/suite.state; fi
