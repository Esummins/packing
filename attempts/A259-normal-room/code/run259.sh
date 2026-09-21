#!/bin/bash
# A259 detached lane (ONE python at a time, BelowNormal + affinity 0xFFFF set inside the scripts).  Resumable: every
# stage skips keyed rows already in results/*.jsonl;  touch ../logs/STOP stops between rows; delete it and rerun.
#   bash run259.sh adv | sample | cert | chain
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
case "$1" in
  adv)
    for side in shat 3.82 3.95 3.99; do for boxes in 1 0; do
      [ -f ../logs/STOP ] && exit 0
      python adv259.py --side $side --boxes $boxes --restarts 6 --iters 250 --seed 1 >> ../logs/adv259.log 2>&1
    done; done ;;
  sample)
    python sample259.py --n 30 --sides 3.82,shat,3.95,3.99 --seed 2 >> ../logs/sample259.log 2>&1 ;;
  cert)
    python cert259.py --mode run >> ../logs/cert259.log 2>&1 ;;
  chain)   # the certificate tree, then its verifier, then the remaining cross-check samples (one python at a time)
    python cert259.py --mode run >> ../logs/cert259.log 2>&1
    [ -f ../logs/STOP ] && exit 0
    python verify259.py --sample 1.0 > ../results/verify259.json 2>> ../logs/cert259.log
    python sample259.py --n 30 --sides 3.82,shat,3.95,3.99 --seed 2 >> ../logs/sample259.log 2>&1 ;;
esac
