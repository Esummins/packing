#!/bin/bash
# A265 detached lane: ONE python at a time (BelowNormal + affinity inside the scripts).  Resumable: cert265 skips cells
# in the index; strip265 is one run (skipped if its result exists).  touch ../logs/STOP stops between steps / cells.
#     bash run265.sh chain
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOG=../logs/chain265.log
stop() { [ -f ../logs/STOP ] && { echo "STOP seen $(date)" >> $LOG; exit 0; }; }
case "$1" in
  chain)
    echo "chain start $(date)" >> $LOG
    stop; python cert265.py --maxdepth 26 >> $LOG 2>&1
    stop; python verify265.py --sample 1.0 >> $LOG 2>&1
    stop; [ -f ../results/strip265.json ] || python strip265.py --step 1 >> ../logs/strip265.log 2>&1
    stop; python miss265.py >> ../logs/miss265.log 2>&1
    echo "chain end $(date)" >> $LOG ;;
esac
