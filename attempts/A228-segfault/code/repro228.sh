#!/bin/bash
# A228 -- reproduce the pass-5 segfault of k5_16_interior_Y0402 (the crash is in the *g1* pad, t ~ 977 s,
# at the no-room leaf of R.3.4.p1) in an ISOLATED cert dir, under faulthandler, with the SAME flags the
# running pass-5 workers use.  Detached: `bash repro228.sh [wall] [pads] [tag]`; the traceback lands in
# logs/repro228_<tag>.log.
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A228-segfault
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONFAULTHANDLER=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export A220_NOROOM_INHERIT=1 A221_LANE=1
WALL=${1:-1200}; PADS=${2:-g1}; TAG=${3:-g1}; NID=${4:-k5_16_interior_Y0402}
LOG=$ATT/logs/repro228_${TAG}.log
echo "$(date '+%H:%M:%S') start $NID pads=$PADS wall=$WALL A220_NOROOM_INHERIT=1 A221_LANE=1" | tee -a $LOG
python -X faulthandler attempts/A211-coarse-tree/code/run211.py page "$NID" --pads "$PADS" --wall "$WALL" \
    --cert-dir $ATT/certs --results $ATT/results/repro228.jsonl --no-fig >> $LOG 2>&1
echo "$(date '+%H:%M:%S') rc=$? $NID pads=$PADS" | tee -a $LOG
