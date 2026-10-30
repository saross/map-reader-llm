#!/usr/bin/env bash
S=$HOME/scratch/kladder-mcc-join-2026-10-30; L=$S/logs
echo $$ > $L/suite2.pid; echo RUNNING > $L/suite2.state
cd $S/suite2 || { echo "FAILED cd" > $L/suite2.state; exit 9; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 MPLBACKEND=Agg
$HOME/Code/map-reader-llm/.venv/bin/python -m pytest -m tier1 -q -p no:cacheprovider
rc=$?; echo $rc > $L/suite2.rc
[ $rc -eq 0 ] && echo DONE > $L/suite2.state || echo "FAILED $rc" > $L/suite2.state
