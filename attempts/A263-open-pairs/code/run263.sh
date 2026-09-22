#!/bin/bash
# A263 detached lane: ONE python at a time (BelowNormal + affinity inside the scripts).  Resumable: cert263 skips cells
# in the index, slabjobs263 resumes A261-style state files, fact263 / slab263 skip keyed rows.  touch ../logs/STOP
# stops between cells / boxes; delete it and rerun to resume.      bash run263.sh chain [hours]
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOG=../logs/chain263.log
stop() { [ -f ../logs/STOP ] && { echo "STOP seen $(date)" >> $LOG; exit 0; }; }
slab_jobs() {   # SM first (M2 cheap, M3, M1), then every SR; the all-slab cubes of M1 / M3 LAST (analytic obligation)
  python slabjobs263.py list | awk '{print $1}' | grep -v jobs | grep -v -E '^SM[13]_0123$'
  echo SM3_0123; echo SM1_0123
}
case "$1" in
  chain)
    HOURS=${2:-40}
    echo "chain start $(date) budget ${HOURS}h" >> $LOG
    for fam in P2 WS WE; do stop; python cert263.py --mode run --fam $fam --maxdepth 26 >> $LOG 2>&1; done
    stop; python verify263.py --sample 0.3 --tags P2,WE,WS > ../results/verify263_adj.json 2>> $LOG
    for job in $(slab_jobs); do
      stop
      [ -f ../certs/$job.state.json ] && grep -q '"done": true' ../certs/$job.state.json && continue
      python slabjobs263.py run $job 5400 >> $LOG 2>&1
      if grep -q '"done": true' ../certs/$job.state.json 2>/dev/null; then
        python slabjobs263.py verify $job >> ../results/slabverify263.log 2>&1
      fi
    done
    for fam in P2 WS WE; do stop; python cert263.py --mode run --fam $fam --adj 0 --maxdepth 22 >> $LOG 2>&1; done
    stop; python verify263.py --sample 0.3 --tags P2n,WEn,WSn > ../results/verify263_nonadj.json 2>> $LOG
    stop; python slab263.py --quick >> ../logs/slab263.log 2>&1
    for fam in WE WS P2; do stop; python fact263.py --mode adv --fam $fam --restarts 6 --iters 150 >> ../logs/adv263.log 2>&1; done
    for fam in WE WS; do stop; python fact263.py --mode adv --fam $fam --adj 0 --restarts 6 --iters 150 >> ../logs/adv263.log 2>&1; done
    echo "chain end $(date)" >> $LOG ;;
  verify) python verify263.py --sample 1.0 --tags P2,WE,WS ;;
esac
