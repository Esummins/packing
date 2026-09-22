#!/bin/bash
# A266 detached chain (ONE python at a time, BelowNormal inside each script; resumable: strip266 skips cells in its
# index, probe / cap skip when their result exists; touch ../logs/STOP stops between stages / cells):
#   chain:  cap266 (CAPACITY-2 measured, ~15 min) -> probe266 jam 3000 in-domain samples (~1 h: the box test at
#           shrinking radii + the exact pocket where it fails) -> probe266 mir 1500 -> strip266 lane jam on the six
#           ring-relevant root cells (theta_C < 15 deg, y_X >= 1.63, phi_X <= 45 deg) with 150 000 boxes per cell
#           (~40 min each; the rest of each cell is OPEN 'budget', the index records the certified volume) ->
#           verify266 jam (10 % sample) -> pages266 -> commit (explicit pathspecs)
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
    stop; python pages266.py >> $LOG 2>&1
    commit "cap266 (CAPACITY-2 measured), miss_region page"
    stop; [ -f ../results/probe266_jam_big.done ] || { python probe266.py --lane jam --n 3000 --seed 11 >> ../logs/probe266_jam.log 2>&1 && touch ../results/probe266_jam_big.done; }
    stop; [ -f ../results/probe266_mir.json ] || python probe266.py --lane mir --n 1500 --seed 12 >> ../logs/probe266_mir.log 2>&1
    commit "probe266 jam 3000 / mir 1500"
    stop; python strip266.py --mode run --lane jam --maxdepth 30 --budget 150000 --only "0,1,0;0,1,1;0,1,2;0,2,0;0,2,1;0,2,2" >> ../logs/strip266_jam.log 2>&1
    commit "strip266 lane jam, six ring cells, budget 150000"
    stop; python verify266.py --lane jam --sample 0.1 >> ../logs/verify266_jam.log 2>&1
    stop; python pages266.py >> $LOG 2>&1
    commit "verify266 jam (10 % sample), pages"
    echo "chain end $(date)" >> $LOG ;;
esac
