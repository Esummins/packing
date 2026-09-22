#!/bin/bash
# A266 detached chain (ONE python at a time, BelowNormal inside each script; resumable: strip266 skips cells in its
# index; touch ../logs/STOP stops between stages / cells):
#   chain:  cap266 (CAPACITY-2 measured, ~15 min) -> strip266 lane jam (27 root cells) -> verify266 jam ->
#           strip266 lane mir -> verify266 mir -> pages266 -> commit (explicit pathspecs)
#   bash run266.sh chain
cd "$(dirname "$0")" || exit 1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOG=../logs/chain266.log
stop() { [ -f ../logs/STOP ] && { echo "STOP seen $(date)" >> $LOG; exit 0; }; }
commit() {
  cd ../../.. || exit 1
  git add attempts/A266-last-two/certs attempts/A266-last-two/results docs/residue_map/campaigns/A266-last-two > /dev/null 2>&1
  git commit -q -m "A266 chain: $1 (detached commit)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- attempts/A266-last-two/certs attempts/A266-last-two/results docs/residue_map/campaigns/A266-last-two >> attempts/A266-last-two/logs/chain266.log 2>&1
  cd attempts/A266-last-two/code || exit 1
}
case "$1" in
  chain)
    echo "chain start $(date)" >> $LOG
    stop; [ -f ../results/cap266.json ] || python cap266.py --n 40 --iters 40 --step 1.0 >> ../logs/cap266.log 2>&1
    commit "cap266 (CAPACITY-2 measured)"
    stop; python strip266.py --mode run --lane jam --maxdepth 30 >> ../logs/strip266_jam.log 2>&1
    commit "strip266 lane jam"
    stop; python verify266.py --lane jam --sample 1.0 >> ../logs/verify266_jam.log 2>&1
    commit "verify266 jam"
    stop; python strip266.py --mode run --lane mir --maxdepth 30 >> ../logs/strip266_mir.log 2>&1
    commit "strip266 lane mir"
    stop; python verify266.py --lane mir --sample 1.0 >> ../logs/verify266_mir.log 2>&1
    stop; python pages266.py >> $LOG 2>&1
    commit "verify266 mir, pages266"
    echo "chain end $(date)" >> $LOG ;;
esac
