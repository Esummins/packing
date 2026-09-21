#!/bin/bash
# A262 driver.  Resume block: every stage is resumable (rows already in results/ are skipped); `touch logs/STOP` stops
# after the current job.  ONE heavy python at a time: the stages run in sequence.
#   bash run262.sh ring      JAM rings at s-hat and 3.82 (ring262: structured starts, room of each ring)   ~ 20 min
#   bash run262.sh adv       adversary on the room of the JAM-ring family (adv262)                         ~ 1 h
#   bash run262.sh search    11-square search with a JAM corner on (s-hat, 4) and at the window (search262)
#   bash run262.sh span      second toucher above X under the ceiling (span262)                            ~ 40 min
#   bash run262.sh chain     ring -> adv -> span -> search   (chain2: adv -> span -> search)
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
    pages)  $PY pages262.py ;;
    *) echo "unknown stage $1"; exit 2 ;;
  esac
}
if [ "$1" = "chain" ] || [ "$1" = "chain2" ]; then
  L="ring adv span search"; [ "$1" = "chain2" ] && L="adv span search"
  for st in $L; do
    [ -e ../logs/STOP ] && exit 0
    stage $st
  done
else
  stage "$1"
fi
