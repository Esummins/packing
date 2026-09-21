#!/bin/bash
# A260 detached lane (ONE python at a time; BelowNormal + affinity 0xFFFF are set inside the scripts).  Resumable: every
# stage skips keyed rows already in results/*.jsonl / certs index;  touch ../logs/STOP stops between rows; delete + rerun.
#   bash run260.sh corpus | adv | cert | chain        (chain = cert -> verify260 -> adv; rerun to resume)
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
adv() {
  for side in shat 3.82; do for adj in 1 0; do for emin in 0 0.05; do
    [ -f ../logs/STOP ] && exit 0
    python adv260.py --side $side --adj $adj --emin $emin --restarts 8 --iters 400 --seed 1 >> ../logs/adv260.log 2>&1
  done; done; done
}
case "$1" in
  corpus) python corpus260.py > ../logs/corpus260.log 2>&1 ;;
  adv) adv ;;
  cert)
    for fam in layer hybA hybB hybAB; do
      [ -f ../logs/STOP ] && exit 0
      python cert260.py --mode run --fam $fam >> ../logs/cert260.log 2>&1
    done ;;
  chain)   # certificates (layer ~1 min, hybA / hybB ~1 CPU-h each, hybAB ~4 CPU-h), their verifier, then the adversary
    for fam in layer hybA hybB hybAB; do
      [ -f ../logs/STOP ] && exit 0
      python cert260.py --mode run --fam $fam >> ../logs/cert260.log 2>&1
    done
    [ -f ../logs/STOP ] && exit 0
    python verify260.py --sample 1.0 > ../results/verify260.json 2>> ../logs/cert260.log
    [ -f ../logs/STOP ] && exit 0
    adv ;;
esac
