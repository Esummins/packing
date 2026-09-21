#!/usr/bin/env bash
# A255 driver.  bash run255.sh corpus|local|blocked|ring|pages|test
#   corpus  = sense255 + slide255 (15 s);  local = local255 (5 min);  blocked = blocked255 (minutes)
#   ring    = ringsense255, the DETACHED run (43 sense-pattern orbits x 2 sides; resumable: rows already in
#             results/ringsense255.jsonl are skipped; touch attempts/A255-common-sense/logs/STOP to stop between
#             restarts; rerun the same command to resume); commits + pushes its rows when it ends.
# At most 2 python processes of A255 at a time.  Never touches other attempts' processes.
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
A=attempts/A255-common-sense
mkdir -p $A/logs $A/results
commit_rows() {
  git add "$@"
  git commit -q -m "A255: $1 rows (detached run)" -- "$@"
  git fetch -q && git merge -q --no-edit origin/master && git push -q
}
case "$1" in
  corpus) python $A/code/sense255.py && python $A/code/slide255.py ;;
  local) python $A/code/local255.py --restarts 60 ;;
  blocked)
    python $A/code/blocked255.py --restarts 80 >> $A/logs/blocked255.log 2>&1
    commit_rows $A/results/blocked255.jsonl ;;
  ring)
    python $A/code/ringsense255.py --sides 3.99,3.877084 --restarts 8 >> $A/logs/ringsense255.log 2>&1
    python $A/code/summarise255.py >> $A/logs/ringsense255.log 2>&1
    commit_rows $A/results/ringsense255.jsonl $A/results/sense255.md ;;
  pages) python $A/code/pages255.py ;;
  test) python $A/code/test255.py ;;
  *) echo "usage: run255.sh corpus|local|blocked|ring|pages|test" ;;
esac
