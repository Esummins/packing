#!/bin/bash
# A265 second lane (after run265.sh chain has ended): the two remaining P2 cells, then the verifier over all five.
# Resumable (cert265 skips cells in the index); touch ../logs/STOP stops between cells.   bash run265b.sh cells
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOG=../logs/chain265.log
stop() { [ -f ../logs/STOP ] && { echo "STOP seen $(date)" >> $LOG; exit 0; }; }
case "$1" in
  cells)
    echo "cells start $(date)" >> $LOG
    stop; python cert265.py --cells "3,5;3,6" --maxdepth 26 >> $LOG 2>&1
    stop; python verify265.py --sample 1.0 >> $LOG 2>&1
    stop; python pages265.py >> $LOG 2>&1
    echo "cells end $(date)" >> $LOG ;;
esac
