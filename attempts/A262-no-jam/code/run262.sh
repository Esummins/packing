#!/bin/bash
# A262 driver.  Resume block: every stage is resumable (rows already in results/ are skipped); `touch logs/STOP` stops
# after the current job.  ONE heavy python at a time: the stages run in sequence.
#   bash run262.sh ring      JAM rings at s-hat and 3.82 (ring262: structured starts, room of each ring)   ~ 20 min
#   bash run262.sh adv       adversary on the room of the JAM-ring family (adv262)                         ~ 1 h
#   bash run262.sh search    11-square search with a JAM corner on (s-hat, 4) and at the window (search262)
#   bash run262.sh span      second toucher above X under the ceiling (span262)                            ~ 40 min
#   bash run262.sh float2    FLOAT2 corner local search (float262)                                       ~ 30 min
#   bash run262.sh pair3     certificate tree, 3-square corner PAIR (the TL corner of a JAM ring)          ~ 3 CPU-h
#   bash run262.sh jam [sec] certificate tree, the JAM corner, centre root cell, 64 sub-jobs, budget       (8 h default)
#   bash run262.sh verify    own verifier of both trees
#   bash run262.sh chain     ring -> adv -> span -> search   (chain2: adv -> span -> search;  chain3: float2 -> pair3 -> verify -> jam -> verify -> held -> sector)
#   bash run262.sh pages     SVG pages (geometry-checked)
cd "$(dirname "$0")" || exit 1
export PYTHONDONTWRITEBYTECODE=1 JAM_COARSE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY=python
stage() {
  case "$1" in
    ring)   $PY ring262.py --s 3.877083590022814 --grid 2 && $PY ring262.py --s 3.82 --grid 2 ;;
    adv)    $PY adv262.py ;;
    search) $PY search262.py ;;
    span)   $PY span262.py ;;
    float2) $PY float262.py ;;
    pair3)  $PY tree262.py --fam pair3 ;;
    jam)    $PY tree262.py --fam jam --only 3,4 --sub 6 --budget ${2:-28800} ;;
    verify) $PY verify262.py ;;
    held)   $PY held262.py ;;
    sector) $PY sector262.py ;;
    pages)  $PY pages262.py ;;
    *) echo "unknown stage $1"; exit 2 ;;
  esac
}
if [ "$1" = "chain" ] || [ "$1" = "chain2" ] || [ "$1" = "chain3" ]; then
  L="ring adv span search"; [ "$1" = "chain2" ] && L="adv span search"; [ "$1" = "chain3" ] && L="float2 pair3 verify jam verify held sector"
  for st in $L; do
    [ -e ../logs/STOP ] && exit 0
    stage $st
  done
  echo "$(echo $1 | tr a-z A-Z) END $(date)"
else
  stage "$1"
fi
